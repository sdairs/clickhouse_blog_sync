---
title: "Read your writes: WAIT FOR in PostgreSQL 19"
date: "2026-08-25T12:36:23.272Z"
author: "Gülçin Yıldırım Jelínek"
category: "Engineering"
excerpt: "PostgreSQL 19's new `WAIT FOR` command enables read-your-writes consistency on asynchronous replicas by letting individual reads wait for a specific WAL position."
---

# Read your writes: WAIT FOR in PostgreSQL 19

PostgreSQL 19 introduces a new SQL command, [`WAIT FOR`](https://www.postgresql.org/docs/19/sql-wait-for.html), that lets a session block until WAL has reached a specific position. This gives us read-your-writes consistency on asynchronous replicas without paying the synchronous replication tax.

<pre><code type='click-ui' language='sql'>
WAIT FOR LSN 'lsn'
    [ WITH ( option [, ...] ) ];

where option can be:

    MODE 'mode'
    TIMEOUT 'timeout'
    NO_THROW

and mode can be:

    standby_replay | standby_write | standby_flush | primary_flush

</code></pre>

***Disclaimer:** PostgreSQL 19 is still in beta as I write this, so some of the details below may change before the final release. The [release notes](https://www.postgresql.org/docs/19/release-19.html) will be the final word once 19.0 goes GA.*

## The stale read problem

With asynchronous streaming replication, a commit on the primary is not immediately visible on a standby. There is always some replication lag, often just milliseconds, but enough to cause stale reads.

Let’s think of a simple example: an application creates an order on the primary and then immediately reads that order from a replica. If the replica has not replayed the relevant WAL yet, the `SELECT` query may return no rows. Nothing is actually broken here, the write has committed and replication is working. The replica simply hasn't caught up yet. What we need is a way to tell the replica: **wait until you've seen this write before running the read**.

Before `WAIT FOR`, we had a few options (that I can think of): 

* `synchronous_commit = remote_apply`: The primary blocks every commit until the standbys have replayed it. This guarantees the replica is up to date, but adds replication latency to every commit and makes writes depend on the standby.  
* Application-side polling: Record the LSN after the write, then repeatedly check `pg_last_wal_replay_lsn()` on the replica until it catches up. It works, but requires applications to implement their own polling and retry logic.  
* Just read from the primary: Well, it works, but it means giving up the benefit of replicas for scaling reads 😀

## What WAIT FOR does

I will try to explain how we can use `WAIT FOR`, using the example from [PG19 docs](https://www.postgresql.org/docs/19/sql-wait-for.html). The pattern is simple: after a write, get the current WAL position from the primary (using [`pg_current_wal_insert_lsn()`](https://www.postgresql.org/docs/19/functions-admin.html#FUNCTIONS-ADMIN-BACKUP)) and pass that LSN to the session that will read from the standby. There, `WAIT FOR` blocks until the standby has replayed WAL up to that position, then you run the read.

On the primary:

<pre><code type='click-ui' language='sql'>
UPDATE movie SET genre = 'Dramatic' WHERE genre = 'Drama';

SELECT pg_current_wal_insert_lsn();
 pg_current_wal_insert_lsn
---------------------------
 0/306EE20
</code></pre>

On the standby:

<pre><code type='click-ui' language='sql'>
WAIT FOR LSN '0/306EE20';
 status
---------
 success

SELECT * FROM movie WHERE genre = 'Drama';
 genre
-------
(0 rows)
</code></pre>

Once `WAIT FOR` returns `success`, everything up to that LSN is guaranteed to be applied, and the read reflects the primary's write. There is no application-side polling and no snapshot is held while waiting; the backend sleeps on a latch and the startup process wakes it as soon as replay reaches its LSN.

> **Note:** `WAIT FOR` compares LSN positions without understanding timelines, so after a promotion, a `success` may refer to WAL from a different timeline than the one your write went to. Treat it with appropriate suspicion.

There are a few insights here. The reason docs use the `pg_current_wal_insert_lsn()` function is because it is the most conservative choice, it covers even not-yet-flushed WAL of just-committed transactions when `synchronous_commit` is `off`.

Another advantage is that unlike `synchronous_commit = remote_apply`, the write stays asynchronous. Only a read that needs this guarantee waits for the standby, and it waits only until the replica catches up.

## WAIT FOR syntax

`WAIT FOR` supports different wait modes and a few configuration options. A runnable example of the command looks like below:

<pre><code type='click-ui' language='sql'>
WAIT FOR LSN '0/306EE20' WITH (MODE 'standby_flush', TIMEOUT '100ms', NO_THROW);
</code></pre>

Only the LSN is required. The mode picks which stage of WAL progress you are waiting on:

| Mode | Waits until the LSN is | Runs on |
| :---- | :---- | :---- |
| `standby_replay` (default) | **replayed**, so reads on the standby can see the changes | standby |
| `standby_flush` | **flushed to disk on the standby** (durable there, not yet visible) | standby |
| `standby_write` | **written on the standby** (may still sit in OS buffers) | standby |
| `primary_flush` | **flushed to disk on the primary** | primary |

On a standby, WAL moves through these stages: **written → flushed → replayed**. PostgreSQL 19 also exposes these stages through the `WaitForWalWrite`, `WaitForWalFlush`, and `WaitForWalReplay` wait events in `pg_stat_activity`, so you can see where sessions are waiting. (*You can read more about these changes in my previous blog post: [What's New with Monitoring in PostgreSQL 19](https://clickhouse.com/blog/postgres-19-monitoring-whats-new)*)

`TIMEOUT` limits how long to wait and if it is omitted or set to zero, `WAIT FOR` waits indefinitely. By default, a timeout raises an error. With `NO_THROW`, it returns a status instead:

<pre><code type='click-ui' language='sql'>
WAIT FOR LSN '0/306EE20' WITH (TIMEOUT '100ms', NO_THROW);
 status
---------
 timeout
</code></pre>

The possible statuses are `success`, `timeout`, and `not in recovery`. `not in recovery` can occur when using a standby mode on a primary, or when a standby is promoted while waiting. If the requested LSN had already been replayed before promotion, `WAIT FOR` still returns `success` on the promoted node.

## Why it must be a top-level command

This is my favorite part because it explains why earlier attempts at this feature ran into problems. If you’re interested in the history, it took about 10 years for `WAIT FOR` to make it into PostgreSQL. [The first proposal](https://www.postgresql.org/message-id/0240c26c-9f84-30ea-fca9-93ab2df5f305%40postgrespro.ru) was in 2016, and the feature was reverted three times along the way.

`WAIT FOR` cannot run inside a function, procedure, or `DO` block, or in transactions above `READ COMMITTED`. The reason is snapshots, as the [commit message](https://git.postgresql.org/gitweb/?p=postgresql.git;a=commitdiff;h=447aae13b) explains:

> WAIT FOR needs to wait without any snapshot held.  Otherwise, the snapshot could prevent the replay of WAL records, implying a kind of self-deadlock.

A session holding a snapshot can block WAL replay on a standby. For example, replaying a vacuum record may need to remove rows that an old snapshot can still see. Postgres resolves this conflict by pausing replay, and eventually by cancelling the session holding the snapshot.

Now imagine that same session is waiting for WAL replay to reach a specific LSN. Replay is stuck behind its snapshot, and the session will not release the snapshot until replay reaches its target. That’s the ***"self-deadlock"*** mentioned in the commit message.

To avoid this, `WAIT FOR` must run without holding a snapshot at all. A SQL function runs as part of a query and therefore always has a snapshot, so that path was never going to work. Instead, `WAIT FOR` is a utility command that runs snapshot-free at the top level, in the spirit of `VACUUM` or `CHECKPOINT`.

Ivan Kartyshov's [original 2016 proposal](https://www.postgresql.org/message-id/0240c26c-9f84-30ea-fca9-93ab2df5f305%40postgrespro.ru) already recognized this problem and the version landed in PostgreSQL 19 is built on that same insight:

> To avoid trouble with snapshots, WAITLSN was implemented as a utility statement, this allows us to circumvent the snapshot-taking mechanism.

## Conclusion

What I like about `WAIT FOR` is that it keeps asynchronous replication asynchronous. Instead of making every write wait for a replica, the cost is paid only when a read actually needs the read-your-writes guarantee.

Most applications will probably not call `WAIT FOR` directly and that’s fine. The docs say [*the LSN of the last modification should be stored on the client application side or the connection pooler side*](https://www.postgresql.org/docs/19/sql-wait-for.html) which makes poolers and protocol-aware proxies natural adopters. With a sticky session, a proxy could capture the LSN after a write and inject `WAIT FOR` before the next read it routes to a replica making read-your-writes transparent to the application.

Hope you enjoyed reading this blog post! If you’d like to hear more about PostgreSQL 19, I’ll be talking about its observability improvements, including the new wait events that ship alongside this feature at [PostgreSQL Conference Europe](https://www.postgresql.eu/events/pgconfeu2026/schedule/session/8182-whats-new-with-monitoring-in-postgresql-19/) in October.


---

## Get started with ClickHouse Managed Postgres today

Interested in seeing how ClickHouse Managed Postgres works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?intent=pg&loc=blog-cta-1640-get-started-with-clickhouse-managed-postgres-today-sign-up&utm_blogctaid=1640)

---