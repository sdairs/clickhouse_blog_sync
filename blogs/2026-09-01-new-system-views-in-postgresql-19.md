---
title: "New system views in PostgreSQL 19"
date: "2026-09-02T08:10:15.712Z"
author: "Gülçin Yıldırım Jelínek"
category: "Engineering"
excerpt: "PostgreSQL 19 adds four system views that make lock contention, recovery state, autovacuum priorities, and dynamic shared memory allocations easier to inspect."
---

# New system views in PostgreSQL 19

  While writing about the [monitoring improvements in PostgreSQL 19](https://clickhouse.com/blog/postgres-19-monitoring-whats-new) and preparing my new talk on Postgres observability for [PostgreSQL Conference Europe](https://www.postgresql.eu/events/pgconfeu2026/schedule/session/8182-whats-new-with-monitoring-in-postgresql-19/) in October, I noticed the [system views](https://www.postgresql.org/docs/19/release-19.html#RELEASE-19-SYSTEM-VIEWS) got their own section in this release. The last time they were similarly highlighted was in PG13 and PG14. So I decided the system views need a blog of their own to go through what has changed. PostgreSQL 19 adds four new views, [pg_stat_lock](https://www.postgresql.org/docs/19/monitoring-stats.html#PG-STAT-LOCK-VIEW), [pg_stat_recovery](https://www.postgresql.org/docs/19/monitoring-stats.html#PG-STAT-RECOVERY-VIEW), [pg_stat_autovacuum_scores](https://www.postgresql.org/docs/19/monitoring-stats.html#PG-STAT-AUTOVACUUM-SCORES-VIEW), and [pg_dsm_registry_allocations](https://www.postgresql.org/docs/19/view-pg-dsm-registry-allocations.html), each deserving more than the one-line mention they got in my [monitoring blog](https://clickhouse.com/blog/postgres-19-monitoring-whats-new), so here is the tour.

  ***Disclaimer:** PostgreSQL 19 is still in beta as I write this and this area has already seen columns renamed mid-cycle; things can still change or get reverted before GA. The [release notes](https://www.postgresql.org/docs/19/release-19.html#RELEASE-19-SYSTEM-VIEWS) will be the final word.*

  ## pg_stat_lock {#pg_stat_lock}

  Locks are a special interest of mine 😀 Last year, I spoke at 16 conferences with a talk called "Anatomy of Table-Level Locks in PostgreSQL". If you're interested, some of those talks were recorded and are [available on YouTube](https://www.youtube.com/watch?v=DLwGuv1QVQU). So, you can imagine how excited I was to see a new locks view in PostgreSQL 19\.

  Until now your options for understanding lock contention were [`pg_locks`](https://www.postgresql.org/docs/19/view-pg-locks.html) (a snapshot of *right now*, no history) and `log_lock_waits` output (history, but you have to parse logs to aggregate the logs yourself, though PostgreSQL 19 now turns it on by default, a change I covered in my [monitoring post](https://clickhouse.com/blog/postgres-19-monitoring-whats-new)). 

  PostgreSQL 19 adds `pg_stat_lock` (a patch by Bertrand Drouvot [§](https://postgr.es/c/4019f725f)): cumulative, cluster-wide lock statistics with one row per lock type (`locktype`). The name `locktype` might be a little confusing. It is not the lock mode (such as ACCESS EXCLUSIVE or ROW SHARE) but the kind of lockable object (showing what was being locked) and there are 12 of them: `relation`, `transactionid`, `tuple`, `extend`, `page`, `object`, `advisory`, `virtualxid`, `spectoken`, `applytransaction`, `frozenid`, `userlock`.

  The view itself  is a thin wrapper around the new function `pg_stat_get_lock()`.

  > **Note**
>
> The newly introduced pg_stat_get_lock() function does not have a docs page, since like most of the `pg_stat_get_*` functions, it only exists to back the view, but it's there if you want to query it directly.

  ***Table 1:** [pg_stat_lock view](https://www.postgresql.org/docs/19/monitoring-stats.html#MONITORING-PG-STAT-LOCK-VIEW)*

  | Column | Type | Description |
  | :---- | :---- | :---- |
  | `locktype` | text | Type of the lockable object. See [`pg_locks`](https://www.postgresql.org/docs/19/view-pg-locks.html) for details. |
  | `waits` | bigint | Number of times a lock of this type had to wait because of a conflicting lock. Only incremented when the lock was successfully acquired after waiting longer than `deadlock_timeout`. |
  | `wait_time` | double precision | Total time spent waiting for locks of this type, in milliseconds. Only incremented when the lock was successfully acquired after waiting longer than `deadlock_timeout`. |
  | `fastpath_exceeded` | bigint | Number of times a lock of this type could not be acquired via fast path because the fast path slot limit was exceeded. Increasing `max_locks_per_transaction` can reduce this number. |
  | `stats_reset` | timestamp with time zone | Time at which these statistics were last reset.  |

  > **Note**
>
> One important detail: `waits` and `wait_time` only count locks that were successfully acquired after waiting longer than `deadlock_timeout` (1 second by default), so `pg_stat_lock` isn't a counter of every lock wait.

  Let's run some queries, I have two psql sessions to demo the lock contention. The first session takes a lock on the demo table and holds it by keeping the transaction open:

  <pre><code type='click-ui' language='sql'>
  -- session 1
  BEGIN;
  LOCK TABLE demo;
  SELECT pg_sleep(2.5);  -- hold the lock for 2.5 seconds
  COMMIT;
  </code></pre>

  The second session tries to lock the same table and cannot acquire the lock (until session 1 commits):

  <pre><code type='click-ui' language='sql'>
  -- session 2
  LOCK TABLE demo;   -- waits here until session 1 commits
  </code></pre>

  After the 2.5 seconds, session 1 commits and session 2 finally gets its lock. Since that wait lasted longer than the default `deadlock_timeout` of 1s and ended in a successful acquisition, it gets counted. To see that, let’s query the view:

  Before starting the demo, I reset the lock statistics with `pg_stat_reset_shared('lock')`, so the numbers below come from only this scenario. 

  > **Note**
>
> [`pg_stat_reset_shared()`](https://www.postgresql.org/docs/19/monitoring-stats.html#MONITORING-STATS-FUNCTIONS) resets cluster-wide statistics for a given target, such as `'wal'`, `'io'` or `'bgwriter'`. The `'lock'` target is new in PostgreSQL 19, added together with the pg_stat_lock view.

  <pre><code type='click-ui' language='sql'>
  SELECT waits, wait_time
  FROM pg_stat_lock
  WHERE locktype = 'relation';
  </code></pre>

  <pre><code type='click-ui' language='bash'>
  waits | wait_time
  -------+-----------
      1 |  2201.783
  (1 row)
  </code></pre>

  This result shows that session 2 had to wait 2.2 seconds (out of 2.5 second session 1 hoarded the table) to acquire the lock. The 0.3 second difference reflects session 2 asking for the lock, a moment after session 1 took it.

  On a real system, we won’t be chasing a single wait, so we’ll have to query lock types together with waits:

  <pre><code type='click-ui' language='sql'>
  SELECT locktype, waits, wait_time,
        round(wait_time::numeric / NULLIF(waits, 0), 1) AS avg_wait_ms
  FROM pg_stat_lock
  WHERE waits > 0
  ORDER BY wait_time DESC;
  </code></pre>

  <pre><code type='click-ui' language='bash'>
  locktype | waits | wait_time | avg_wait_ms
  ----------+-------+-----------+-------------
  relation |     1 |  2201.783 |      2201.8
  (1 row)
  </code></pre>

  > **Query insight**
>
> pg_stat_lock view always returns all 12 lock types, `WHERE waits > 0` filters out those without recorded contention. We then order by total wait time and calculate the average wait per lock type. A high total wait time can point to a frequently contended lock type, while a high average can reveal fewer but longer stalls.

  ### fastpath_exceeded

  I thought the `fastpath_exceeded` counter in the `pg_stat_lock` view was worth digging into, so I gave it its own section 🙂 For speed, each backend keeps a small set of fast-path slots for the most common locks that rarely conflict with anything. When a query needs more locks than the slot can hold, the extras fall back to the slower shared lock table and this counter ticks (every time,  no `deadlock_timeout` threshold here).  

  `fastpath_exceeded` can be particularly interesting for partition-heavy workloads, where a single query may need to lock many relations. 

  > **Note**
>
> If the `fastpath_exceeded` counter grows on your partition-heavy workload, that's a direct hint to raise `max_locks_per_transaction`. Starting from PostgreSQL 18, the fast-path slot count derives from it (before that it was fixed at 16; Christophe Pettus has [an excellent write-up of that era](https://thebuild.com/blog/sixteen-locks-ought-to-be-enough-for-anybody/)). PostgreSQL 19 doubled the default `max_locks_per_transaction` from 64 to 128 (Heikki Linnakangas [§](https://postgr.es/c/79534f906)).

  To make the demo easy, let's create a partitioned table with more partitions than the fast-path slots can cover. I chose 140 partitions, more than the new default 128\. (Postgres's own regression test uses the same trick, creating `max_locks_per_transaction` + 10 partitions.)

  <pre><code type='click-ui' language='sql'>
  CREATE TABLE part_demo (id int) PARTITION BY RANGE (id);

  DO $$
  BEGIN
    FOR i IN 1..140 LOOP
      EXECUTE format(
        'CREATE TABLE part_demo_%s PARTITION OF part_demo
        FOR VALUES FROM (%s) TO (%s)',
        i, (i-1)*1000, i*1000);
    END LOOP;
  END $$;
  </code></pre>

  Then reset the counters again for a clean read, and scan the table once; a plain `SELECT count(*)` has to lock the parent and every partition:

  <pre><code type='click-ui' language='sql'>
  SELECT pg_stat_reset_shared('lock');
  SELECT count(*) FROM part_demo;
  </code></pre>

  Now, let’s query our view:

  <pre><code type='click-ui' language='sql'>
  SELECT locktype, fastpath_exceeded
  FROM pg_stat_lock
  WHERE fastpath_exceeded > 0;
  </code></pre>

  <pre><code type='click-ui' language='bash'>
  locktype | fastpath_exceeded
  ----------+-------------------
  relation |               422
  (1 row)

  </code></pre>

  The count exceeds 140 because Postgres counts every over-limit lock acquisition attempt, and partitions can be locked during both planning and execution. The exact number may vary between runs; what matters is that it is non-zero, this workload spills out of the fast path.

  ## pg_stat_recovery {#pg_stat_recovery}

  If you have ever built a standby health check, you have probably used some or all of these functions to check the standby state: `pg_is_in_recovery()`, `pg_last_wal_replay_lsn()`, `pg_last_xact_replay_timestamp()`, `pg_get_wal_replay_pause_state()`. Each of these functions reads the shared recovery state under its own lock, at a slightly different moment. Even if you wrap them in a single view, which is what we DBAs used to do, the values are not guaranteed to be consistent with each other because replay keeps advancing between the calls.

  `pg_stat_recovery` (Xuneng Zhou [§](https://postgr.es/c/01d485b14), with a fix by Shinya Kato [§](https://postgr.es/c/2d4ead6f4)) assembles all this information in one row, read as a single atomic snapshot, so all fields are consistent with each other.

  ***Table 2:** [pg_stat_recovery view](https://www.postgresql.org/docs/19/monitoring-stats.html#MONITORING-PG-STAT-RECOVERY-VIEW)*

  | Column | Type | Description |
  | :---- | :---- | :---- |
  | `promote_triggered` | boolean | True if a promotion has been triggered. |
  | `last_replayed_read_lsn` | pg_lsn | Start write-ahead log location of the last successfully replayed WAL record. |
  | `last_replayed_end_lsn` | pg_lsn | End write-ahead log location, plus one, of the last successfully replayed WAL record. |
  | `last_replayed_tli` | integer | Timeline of the last successfully replayed WAL record. |
  | `replay_end_lsn` | pg_lsn | Write-ahead log location of the record currently being replayed (end position plus one). When no record is being actively replayed, equals `last_replayed_end_lsn`. |
  | `replay_end_tli` | integer | Timeline of the WAL record currently being replayed. When no record is being actively replayed, equals `last_replayed_tli`. |
  | `recovery_last_xact_time` | timestamptz | Timestamp of the last transaction commit or abort record replayed during recovery. This is the time at which the commit or abort WAL record for that transaction was generated on the primary. |
  | `current_chunk_start_time` | timestamptz | Time when the startup process observed that replay had caught up with the latest WAL chunk received from streaming replication. Used in recovery-conflict timing and replay/apply-lag diagnostics. NULL if streaming WAL has not yet been received or the time is not available. |
  | `pause_state` | text | Recovery pause state. Possible values: `not paused`, `pause requested`, `paused`. |

  <pre><code type='click-ui' language='sql'>
  SELECT last_replayed_end_lsn, last_replayed_tli,
        recovery_last_xact_time, pause_state, promote_triggered
  FROM pg_stat_recovery;
  </code></pre>

  <pre><code type='click-ui' language='bash'>
  last_replayed_end_lsn | last_replayed_tli |    recovery_last_xact_time    | pause_state | promote_triggered
  -----------------------+-------------------+-------------------------------+-------------+-------------------
  0/03001E20            |                 1 | 2026-08-31 15:43:27.762621+02 | not paused  | f
  (1 row)
  </code></pre>

  > **💡**
>
> The `pg_stat_recovery` view also exposes information that previously had no SQL interface: the start LSN of the last replayed record, the replay timelines, the end position of the record currently being replayed, and whether a promotion has been triggered. Previously, SQL could only tell you when a promotion had completed through `pg_is_in_recovery()` returning `false`, not that one was already underway.

  A few practical notes:

  * The view returns no rows on a primary, so you’ll need to query it on a standby.  
  * You need the `pg_read_all_stats` privilege to see the data.  
  *  The old functions are still there, this is purely additive. 

  If you maintain HA tooling, this is a good time to update it. If you run health checks every few seconds, getting a consistent view of the recovery state with one query instead of several is a small but nice win.

  ## pg_stat_autovacuum_scores {#pg_stat_autovacuum_scores}

  I will cover two changes in this section: a new autovacuum behaviour and a view (`pg_stat_autovacuum_scores`) to watch it.

  First, the behavior. PostgreSQL 19 changes ***how autovacuum decides what to work on first***. Before PostgreSQL 19, autovacuum processed tables in the order it found them in `pg_class`. Now, each worker calculates a score for every table based on how close it is to (or how far past) its autovacuum thresholds: XID age, multixact age, dead tuples, inserts and analyze staleness. The highest score wins, so tables needing attention most are processed first.

  Five new `autovacuum_*_score_weight` parameters (all defaulting to `1.0`) let you set weights for the components. Setting all of them to `0.0` restores the pre-19 ordering. Nathan Bossart’s commit calls this ["a baby step towards smarter autovacuum workers"](https://postgr.es/c/d7965d65f).

  The second change surfaces these stats: `pg_stat_autovacuum_scores` (Sami Imseih [§](https://postgr.es/c/87f61f0c8)) exposes these scores per table (including TOAST tables and system catalogs) in the current database, revealing what tables autovacuum prioritizes.

  ***Table 3:** [pg_stat_autovacuum_scores view](https://www.postgresql.org/docs/19/monitoring-stats.html#MONITORING-PG-STAT-AUTOVACUUM-SCORES-VIEW)*

  | Column | Type | Description |
  | :---- | :---- | :---- |
  | `relid` | oid | Oid of the table. |
  | `schemaname` | name | Name of the schema that the table is in. |
  | `relname` | name | Name of the table. |
  | `score` | double precision | Maximum value of all component scores. This is the value that autovacuum would use to sort the list of tables to process. |
  | `xid_score` | double precision | Transaction ID age component score. Scores greater than or equal to `autovacuum_freeze_score_weight` indicate that autovacuum would vacuum the table for transaction ID wraparound prevention. |
  | `mxid_score` | double precision | Multixact ID age component score. Scores greater than or equal to `autovacuum_multixact_freeze_score_weight` indicate that autovacuum would vacuum the table for multixact ID wraparound prevention. |
  | `vacuum_score` | double precision | Vacuum component score. Scores greater than or equal to `autovacuum_vacuum_score_weight` indicate that autovacuum would vacuum the table (unless autovacuum is disabled). |
  | `vacuum_insert_score` | double precision | Vacuum insert component score. Scores greater than or equal to `autovacuum_vacuum_insert_score_weight` indicate that autovacuum would vacuum the table (unless autovacuum is disabled). |
  | `analyze_score` | double precision | Analyze component score. Scores greater than or equal to `autovacuum_analyze_score_weight` indicate that autovacuum would analyze the table (unless autovacuum is disabled). |
  | `do_vacuum` | boolean | Whether autovacuum would vacuum the table. Note that even if the component scores indicate that autovacuum would vacuum the table, this may be false if autovacuum is disabled. |
  | `do_analyze` | boolean | Whether autovacuum would analyze the table. Note that even if the component scores indicate that autovacuum would analyze the table, this may be false if autovacuum is disabled. |
  | `for_wraparound` | boolean | Whether autovacuum would vacuum the table for wraparound prevention. |

  Let’s run a few queries to see it working. I created a 1000 row table, analyzed it and deleted 400 rows:

  <pre><code type='click-ui' language='sql'>
  CREATE TABLE av_demo AS
    SELECT g AS id, md5(g::text) AS payload FROM generate_series(1, 1000) g;
  ANALYZE av_demo;
  DELETE FROM av_demo WHERE id <= 400;

  </code></pre>

  Then asked the `pg_stat_autovacuum_scores` view what autovacuum thinks of my tables:

  <pre><code type='click-ui' language='sql'>
  SELECT relname, round(score::numeric,2) AS score,
        do_vacuum, do_analyze, for_wraparound
  FROM pg_stat_autovacuum_scores
  WHERE schemaname = 'public' AND (do_vacuum OR do_analyze)
  ORDER BY score DESC;
  </code></pre>

  <pre><code type='click-ui' language='bash'>
  relname | score | do_vacuum | do_analyze | for_wraparound
  ---------+-------+-----------+------------+----------------
  av_demo |  2.67 | t         | t          | f
  (1 row)

  </code></pre>

  Where does 2.67 come from? Autovacuum decides when to act using [thresholds](https://www.postgresql.org/docs/19/routine-vacuuming.html#AUTOVACUUM) computed from the table's row count. For analyze, the default is 50 + 0.1 × rows →  for our 1000 row table, that's 150\. We changed 400 rows, so the analyze score is  400 / 150 \= 2.67. 

  The deletes crossed the vacuum threshold too: 50 + 0.2 × 1000 \= 250, giving 400 / 250 \= 1.60. Since the overall score is the highest component, `av_demo` gets 2.67 and qualifies for both vacuum and analyze.

  `for_wraparound` derives from a different calculation entirely, not row changes, but age. As in, how far the table's oldest unfrozen transaction ID has drifted toward `autovacuum_freeze_max_age` (200 million transactions by default). Our freshly created table is nowhere near that threshold, so it is false.

  > **Note**
>
> `pg_stat_autovacuum_scores` computes scores from *current* statistics while autovacuum workers score the tables whenever they wake up. The two moments can differ, so treat the view as a strong hint of what autovacuum will prioritize, not a guarantee.

  ## pg_dsm_registry_allocations {#pg_dsm_registry_allocations}

  A smaller one: extensions increasingly allocate shared memory through the DSM registry, which spares them from needing `shared_preload_libraries` (and a restart) just to get shared memory. Until now that memory wasn't visible from SQL.

  > **What is the DSM registry?**
>
> DSM stands for dynamic shared memory: shared memory created at runtime, unlike the main shared memory area, which is allocated once at server start (which is why extensions needing shared state traditionally required `shared_preload_libraries` and a restart). The DSM registry, added in PostgreSQL 17 (Nathan Bossart [§](https://postgr.es/c/8b2bcf3f2)), lets backends create, find and attach to these shared memory segments by name. This means extensions get shared state with a plain `CREATE EXTENSION`, no restart. More in the docs: [Requesting Shared Memory After Startup](https://www.postgresql.org/docs/19/xfunc-c.html#XFUNC-SHARED-ADDIN-AFTER-STARTUP).

  This new `pg_dsm_registry_allocations` view (Florents Tselai [§](https://postgr.es/c/167ed8082), extended by Nathan Bossart [§](https://postgr.es/c/f894acb24)) lists each registry entry with its name, type (`segment`, `area` or `hash`) and size. A `NULL` size means the entry failed to initialize.

  ***Table 4:** [pg_dsm_registry_allocations view](https://www.postgresql.org/docs/19/view-pg-dsm-registry-allocations.html#VIEW-PG-DSM-REGISTRY-ALLOCATIONS)*

  | Column | Type | Description |
  | :---- | :---- | :---- |
  | `name` | text | The name of the allocation in the DSM registry. |
  | `type` | text | The type of allocation. Possible values are `segment`, `area`, and `hash`, which correspond to dynamic shared memory segments, areas, and hash tables, respectively. |
  | `size` | int8 | Size of the allocation in bytes. NULL for entries that failed initialization. |

  ## Outro {#outro}

  Thanks for reading this far! I hope the new system views excite you as much as they do me. We’re all counting down the days to PostgreSQL 19 and I’m already wishing everyone happy upgrades!

  I will be talking about PostgreSQL 19 observability at [PostgreSQL Conference Europe](https://2026.pgconf.eu/) in October, and several of the topics I covered here will make an appearance. Come say hi if you plan to be in Valencia! 👋


---

## Get started with ClickHouse Managed Postgres today

Interested in seeing how ClickHouse Managed Postgres works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?intent=pg&loc=blog-cta-1711-get-started-with-clickhouse-managed-postgres-today-sign-up&utm_blogctaid=1711)

---