---
title: "What's New with Monitoring in PostgreSQL 19"
date: "2026-08-18T14:31:36.544Z"
author: "Gülçin Yıldırım Jelínek"
category: "Engineering"
excerpt: "What's New with Monitoring in PostgreSQL 19"
---

# What's New with Monitoring in PostgreSQL 19

PostgreSQL 19 is around the corner, and I will be talking about observability improvements at the upcoming [PostgreSQL Conference Europe](https://2026.pgconf.eu/). I am also co-organizing the PostgreSQL Observability Summit as part of [Community Events Day](https://2026.pgconf.eu/community-day/) on the last day of the conference, Friday, October 23. So, I thought this was a good time to organize my thoughts in a blog post.

***Disclaimer:** PostgreSQL 19 is still in beta as I write this, so some of the details below may change before the final release. The [release notes](https://www.postgresql.org/docs/19/release-19.html) will be the final word once 19.0 goes GA.*

With that out of the way, let's look at the PostgreSQL 19 monitoring and observability improvements that I find most useful and interesting.

## Lock contention is now visible by default {#lock_contention_is_now_visible_by_default}

`log_lock_waits` controls whether to log a message when a session waits longer than `deadlock_timeout` (1 second by default) to acquire a lock. Checking for deadlock is relatively expensive, so you’re advised to set an amount of time to wait before that check happens, ideally longer than your regular transaction time. This is the relationship between `deadlock_timeout` and `log_lock_waits` (Robert Haas even [suggested](https://postgr.es/m/CA+TgmobPaKeiXQ3q2Qb-ToLGPxy1kkOwi1AS16ZS0ryPKvPHTw@mail.gmail.com) separating the two). In short, enabling `log_lock_waits` provides a cheap lock contention detector for Postgres, yet it defaulted to off up until now.

PostgreSQL 19 flips the default to `on` (commit [`2aac62be8`](https://postgr.es/c/2aac62be8), Laurenz Albe). I love the reasoning in the commit message:

> If someone is stuck behind a lock for more than a second, that is almost always a problem that is worth a log entry.

## Different log verbosity per process type {#different_log_verbosity_per_process_type}

`log_min_messages` has always been a single global knob. If you wanted `DEBUG2` output from the checkpointer, you got `DEBUG2` from everything and good luck finding the line you care about.

Starting with PostgreSQL 19, `log_min_messages` accepts a comma-separated list of `process type:level` pairs, plus one mandatory level that applies to every process type not listed. A bare level is still valid, so the old syntax keeps working.

<pre><code type='click-ui' language='sql'>
-- DEBUG2 for the checkpointer, DEBUG1 for autovacuum, WARNING for everything else
ALTER SYSTEM SET log_min_messages = 'warning, checkpointer:debug2, autovacuum:debug1';
</code></pre>

The recognized process types are `archiver`, `autovacuum`, `backend`, `bgworker`, `bgwriter`, `checkpointer`, `checksums`, `ioworker`, `postmaster`, `slotsyncworker`, `startup`, `syslogger`, `walreceiver`, `walsender`, `walsummarizer` and `walwriter`. Note that `autovacuum` covers both the launcher and the workers.

## Separate logging for autoanalyze {#separate_logging_for_autoanalyze}

Until now, `log_autovacuum_min_duration` controlled log output for both VACUUM and ANALYZE runs by autovacuum. These are very different operations: autoanalyze runs are typically much shorter, so a threshold tuned to catch slow vacuums silently discards almost all ANALYZE activity.

PostgreSQL 19 adds `log_autoanalyze_min_duration`, which controls log output for ANALYZE. `log_autovacuum_min_duration` now only controls VACUUM logging. Both default to `10min`, accept `0` (log everything) and `-1` (disable). You can also set per-table overrides:

<pre><code type='click-ui' language='sql'>
-- For this table log every autoanalyze, regardless of the global setting
ALTER TABLE events SET (log_autoanalyze_min_duration = 0);
</code></pre>

**Upgrade notes:** If your tooling parses autovacuum logs, remember that after the upgrade `log_autovacuum_min_duration` alone no longer reports analyze runs. And if you’re displaying log parameters in a UI, consider making `log_autoanalyze_min_duration` visible as well.

## WAL full-page write bytes to VACUUM and ANALYZE logging {#wal_full_page_write_bytes_to_vacuum_and_analyze_logging}

Full-page images are often the dominant part of WAL volume and VACUUM generates plenty of them. If you’re not familiar with why, I’ll try to explain a bit. The first time a page is modified after a checkpoint, Postgres writes the entire 8kB page into the WAL instead of just the small change so crash recovery never has to trust a possibly torn page on disk. That means one tiny update of a 50-byte row can produce ~8kB of WAL if it happens to be the first touch of that page since the last checkpoint. VACUUM crawls through and dirties lots of cold pages, so it triggers plenty of these, which is why vacuuming a big, cold table can generate far more WAL than the amount of data it actually changed.

Postgres reported full-page image counts (`wal_fpi`) but not their size, so if you wanted the actual bytes, you had to dig through WAL with `pg_waldump` or `pg_walinspect`.

PostgreSQL 19 adds a new `wal_fpi_bytes` counter, added through a series of patches by Shinya Kato. You can see it cluster-wide in `pg_stat_wal` (what your metrics collector polls), per-session via `pg_stat_get_backend_wal()` (handy to join against `pg_stat_activity` when you're wondering which connection is producing all that WAL), per-query in `EXPLAIN (ANALYZE, WAL)`, and per-operation in VACUUM and ANALYZE log output, which now looks like this:

<pre><code type='click-ui' language='bash'>
WAL usage: 2841 records, 1904 full page images, 15735621 bytes,
           15242880 full page image bytes, 3 buffers full
</code></pre>

Comparing `wal_fpi_bytes` against `wal_bytes` tells you what fraction of your WAL is full-page images and whether `wal_compression`, checkpoint spacing or maintenance scheduling is where the win is.

## New wait events: WAL LSNs and COPY I/O {#new_wait_events_wal_lsns_and_copy_io}

Postgres 19 adds a few new wait events that make previously hard-to-see waits visible in `pg_stat_activity`.

As part of the infrastructure behind the new `WAIT FOR` command (which I plan to explain more in another blog post), PostgreSQL can now report when a session is waiting for WAL to reach a specific Log Sequence Number (LSN). A new `WaitForWalWrite` wait event covers waiting for WAL to be written and the existing `WaitForWalFlush` (previously primary-only) now also covers standbys. Together with `WaitForWalReplay` (as the name suggests, waiting for WAL to be replayed), they make it possible to tell which stage of WAL processing a session is waiting on (write → flush → replay).

Postgres 19 also closes a similar observability gap around `COPY`. Previously, `COPY FROM/TO` operations on a file, pipe or program used to do their reads and writes with no wait event at all, so we had no visibility when a backend got stuck. Now, the new `CopyFromRead` and `CopyToWrite` wait events make these paths observable. `COPY` over the wire protocol was already covered by `ClientRead`/`ClientWrite`, so this closes the file, pipe and program paths commonly used by bulk loads and ETL pipelines.

## Better logging for messages from remote Postgres servers {#better_logging_for_messages_from_remote_postgres_servers}

This one is subtle, but anyone running logical replication or FDW-heavy setups will appreciate it. NOTICE, WARNING and similar messages from a remote server (over replication, `postgres_fdw` or `dblink` connections) used to be printed directly to the local server's `stderr`. So, they did not get the usual log formatting, such as `log_line_prefix`, which made them harder to correlate with nearby log entries.

PostgreSQL 19 routes these messages through `ereport()` like local server messages. They get the normal log formatting and are prefixed with their origin: `received message via replication` or `received message via remote connection`. This makes cross-server log correlation significantly easier.

## Multixact activity with pg_get_multixact_stats() {#multixact_activity_with_pg_get_multixact_stats}

Multixacts, which Postgres creates when multiple transactions lock the same tuple (think foreign key checks and `SELECT ... FOR SHARE`), have long been an observability blind spot. When `pg_multixact/members/` started eating disk, your options were filesystem inspection and educated guessing.

PostgreSQL 19 adds `pg_get_multixact_stats()`:

<pre><code type='click-ui' language='sql'>
SELECT *, pg_size_pretty(members_size) AS members_size_pretty
FROM pg_get_multixact_stats();

 num_mxids | num_members | members_size | oldest_multixact | members_size_pretty
-----------+-------------+--------------+------------------+---------------------
 311740299 |  2785241176 |  13926205880 |                2 | 13 GB
</code></pre>

This gives us direct visibility into multixact activity: `num_mxids` shows how many multixact IDs are currently in use, `num_members` shows how many entries they contain and `members_size` shows how much disk space those members consume. `oldest_multixact` helps track how far back the oldest multixact still needed by the cluster goes.

A spike in `num_mxids` points at concurrent row-locking workloads; `oldest_multixact` holding still while `num_members` grows suggests a long-running transaction is blocking cleanup. The function requires `pg_read_all_stats`, so it slots straight into monitoring roles.

## More lead time before wraparound {#more_lead_time_before_wraparound}

Finally, the wraparound warning threshold for both transaction IDs and multixact IDs has been raised from 40 million to 100 million transactions before wraparound. The 40 million figure dated from an era of much lower transaction rates: a system burning 10,000 XIDs per second gets through it in about an hour, which is not much runway to notice, react and let an aggressive vacuum finish.

Importantly, this does not change when wraparound happens; it simply makes Postgres start warning you earlier. If your alerting on `age(datfrozenxid)` uses thresholds derived from the old warning point, revisit them.

## What this means for tooling: an upgrade checklist {#what_this_means_for_tooling_an_upgrade_checklist}

I know this is a lot of information to go through, so I decided to end this blog with a list of actionable items. So if you maintain observability tooling, check these before upgrading (or give this list to your agents 🙂):

***Disclaimer:** This checklist is not theoretical for me either: we maintain [pg_stat_ch](https://github.com/ClickHouse/pg_stat_ch), an open-source extension that streams query statistics from Postgres into ClickHouse, and supporting PostgreSQL 19 means walking through exactly this list: new WAL fields, new wait events and all.*

**Log parsers**

* Update patterns for the VACUUM/ANALYZE log line; it gained a field: `... bytes, N full page image bytes, N buffers full`.
* Add `log_autoanalyze_min_duration` to whatever reads autovacuum logs, `log_autovacuum_min_duration` alone no longer reports analyze runs.
* Expect new entry types:
  * `still waiting for lock` messages on clusters that never logged them
  * `received message via replication` / `received message via remote connection` entries (the latter always at local `LOG` severity, so severity-based filters won't catch a remote WARNING)

**Metric collectors**

* Start collecting `wal_fpi_bytes` from `pg_stat_wal` and track its ratio against `wal_bytes`.
* Add `pg_get_multixact_stats()` to your queries; the monitoring role needs `pg_read_all_stats`, and without it the function returns NULLs rather than an error, silently empty metrics.


**Wait event dictionaries**

* Add `CopyFromRead`, `CopyToWrite` and `WaitForWalWrite`; note `WaitForWalFlush` now also appears on standbys.


**Config validation and UIs**

* Accept the new `type:level` list syntax for `log_min_messages`, and surface `log_autoanalyze_min_duration` next to its autovacuum sibling.

**Alerts**

* Recalibrate `age(datfrozenxid)` alert thresholds against the new 100 million warning point, so your alerts still fire before the server starts complaining.

PostgreSQL 19 also introduces new system views (`pg_stat_lock`, `pg_stat_recovery`, `pg_stat_autovacuum_scores`) and improves several existing ones. I plan to cover these in a separate blog post, but it is not a bad idea to familiarize yourself with them already.

## Outro {#outro}

On a personal note, observability is where my Postgres world and my day job happen to meet. At [ClickHouse](https://clickhouse.com/), we are building a [managed Postgres service](https://clickhouse.com/cloud/postgres), while ClickHouse itself is what many engineering teams use to store and analyze the logs, metrics, and traces that systems like Postgres produce. So, I get to think about both sides of observability: the database emitting the signals and the database storing and analyzing them.

If you want to talk about any of this, come find me in Valencia at [PGConf.EU](http://PGConf.EU) on October 20-23!


---

## Get started with ClickHouse Managed Postgres today

Interested in seeing how ClickHouse Managed Postgres works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?intent=pg&loc=blog-cta-1565-get-started-with-clickhouse-managed-postgres-today-sign-up&utm_blogctaid=1565)

---