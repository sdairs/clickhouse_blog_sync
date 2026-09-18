---
title: "Postgres week in the Netherlands: PGDay Lowlands & Percona Live 2026"
date: "2026-09-18T09:44:41.366Z"
author: "Gülçin Yıldırım Jelínek"
category: "Community"
excerpt: "Notes from three days in the Netherlands, featuring a lightning talk on pg_clickhouse and pg_stat_ch at PGDay Lowlands and a session on PostgreSQL 19 monitoring at Percona Live Amsterdam."
---

# Postgres week in the Netherlands: PGDay Lowlands & Percona Live 2026

Last week, I spent three days in the Netherlands and gave two talks at two conferences: a lightning talk at [PGDay Lowlands](https://2026.pgday.nl/) in Utrecht on Thursday, September 10, and a session at [Percona Live](https://perconalive.com/2026-amsterdam/) in Amsterdam on Friday, September 11\. In this blog post, I’m going to share my notes from both.

As often happens with conferences (or any big events, really), there was a minor hurdle to overcome before we could get there. On Wednesday, September 9, just one day before PGDay Lowlands, a nationwide 24-hour public transport strike stopped trains, buses, trams and metros across the whole country. Not the ideal warm-up for a conference that draws people from all over the world, but by Thursday morning everything was moving again and the day went ahead as planned. Yay!

## PGDay Lowlands, Utrecht {#pgday_lowlands_utrecht}

PGDay Lowlands is a one-day Dutch PostgreSQL conference (although all the talks are in English), organized by [PostgreSQL Europe](https://2026.pgday.nl/organisation/). This was its third edition, and the event moves around: last year, it was held at Blijdorp Zoo in Rotterdam; this year, it took place at TivoliVredenburg, a music venue in the center of Utrecht, with the main track in a hall called Cloud Nine.

Last year I gave a full 45-minute talk, my now famous [Anatomy of Table-Level Locks in PostgreSQL](https://www.postgresql.eu/events/pgdaynl2025/schedule/session/6730-anatomy-of-table-level-locks-in-postgresql/) (the recording is on [YouTube](https://youtu.be/2Zsjn47a7b8)). This year, I went for the other end of the spectrum: a five-minute lightning talk. It’s the format I struggle with the most, but I tried anyway.

## Analytics without leaving Postgres {#analytics_without_leaving_postgres}

Five minutes is not a lot of time, so I kept it to two open-source extensions ([pg_clickhouse](https://clickhouse.com/blog/introducing-pg_clickhouse) and [pg_stat_ch](https://clickhouse.com/blog/pg_stat_ch-postgres-extension-stats-to-clickhouse)) we maintain at ClickHouse, both Apache 2.0 licensed. The idea behind both is that you keep Postgres as your front door and your system of record, and let ClickHouse do the analytical heavy lifting behind it.

![](https://clickhouse.com/uploads/postgres_conferences_sep2026_image2_213d5d5fd7.jpg)  
*On a personal note, this was my first talk as a new ClickHouse employee 😀 [Photo credit: Tom](https://www.honkingelephant.com/)* 

[pg_clickhouse](https://github.com/ClickHouse/pg_clickhouse) is a foreign data wrapper. You `CREATE SERVER` pointing at ClickHouse, add a `USER MAPPING` with the credentials, and `IMPORT FOREIGN SCHEMA`: the ClickHouse tables show up as foreign tables in a Postgres schema of your choice, with the same column names and ClickHouse types mapped to Postgres types. Change `search_path` to that schema and existing read queries, ORMs and dashboards run unmodified. Where the query is pushable, the Postgres planner sends the whole thing to ClickHouse as ClickHouse SQL and gets back the aggregated result; otherwise it pushes down what it can and finishes the rest locally.

The point of `pg_clickhouse` is simple: moving data to ClickHouse is easy, but rewriting years’ worth of dashboard and ORM-generated SQL is hard. The extension lets existing PostgreSQL queries run against ClickHouse, so improving query pushdown is the top roadmap priority. Today, 15 of the 22 TPC-H queries at scale factor 1 are fully pushed down.

![](https://clickhouse.com/uploads/postgres_conferences_sep2026_image3_f67eafeb23.png)  
*The main slide from the lightning talk: Analytics Without Leaving Postgres*

[pg_stat_ch](https://github.com/ClickHouse/pg_stat_ch) goes in the opposite direction. Postgres hooks capture every query execution as a raw event (`timing, buffers, WAL, CPU, errors, application, client`), write it into a shared-memory ring buffer, and a background worker drains batches to ClickHouse over the native protocol, where the aggregation happens. It uses the same `query_id` as `pg_stat_statements`, so the two correlate, but you get per-query history you can slice by time and application, with real percentiles and error tracking. `pg_stat_statements` cannot give you that because it only keeps cumulative counters. There is no back-pressure by design: if ClickHouse is slow or unreachable, events are dropped and counted, and Postgres never waits.

### The rest of the lightning block

Lightning talks are so much fun to watch, so I stayed for the whole block.

![](https://clickhouse.com/uploads/postgres_conferences_sep2026_image5_0f6cdfdd15.jpg)  
*In the audience during the lightning talks. Look how happy I am 😀 [Photo credit: Tom](https://www.honkingelephant.com/)* 

[Cornelia Biacsics](https://www.postgresql.eu/events/pgdaynl2026/schedule/session/7779-my-lightning-talk-disaster/) opened with *My Lightning Talk Disaster*, looking back on her first speaking experience exactly one year later. It was also a reminder that the five-minute format is sold as the easy way in for new speakers, but is not risk-free, especially for introverts. Speaking as an extrovert, I can confirm that it is THE hardest format for me too, as I mentioned above. [Ellert van Koperen](https://www.postgresql.eu/events/pgdaynl2026/schedule/session/7881-when-partitioning-has-a-side-effect/) showed a real-life case where partitioning, the default answer to "the table keeps growing", had a knock-on effect with serious consequences, and the simple fix that resolved it. [Jan Wieremjewicz](https://www.postgresql.eu/events/pgdaynl2026/schedule/session/7795-tde-status-update/) gave a status update on [pg_tde](https://github.com/percona/pg_tde), what works today, what is still open, and how to get involved. And [Dave Pitts](https://www.postgresql.eu/events/pgdaynl2026/schedule/session/8512-behind-the-soundtrack-of-the-pgday-lowlands-trilogy/) closed the block with something completely different: the story behind the PGDay Lowlands conference songs, produced with digital instruments and an actual piano keyboard rather than generated by AI. Yes, this conference has its own soundtrack! 

The whole day was [live streamed](https://www.youtube.com/watch?v=mXndwAOrH7g) and recorded, and the individual talks will be available to watch later.

### Optimizer hints in PostgreSQL, by Michael Banck

Before lunch I attended [Michael Banck](https://www.postgresql.eu/events/pgdaynl2026/schedule/speaker/301-michael-banck/)'s talk, [Optimizer Hints in PostgreSQL](https://www.postgresql.eu/events/pgdaynl2026/schedule/session/7815-optimizer-hints-in-postgresql/), and I liked it a lot. Postgres has famously refused to add optimizer hints for decades, on the grounds that planner problems are bugs to fix. Michael walked through what you can do today: the `enable_*` parameters (reworked in PostgreSQL 18 so disabled node types are counted rather than penalized with a huge cost) and [pg_hint_plan](https://github.com/ossc-db/pg_hint_plan) with its `/*+ ... */` comments and hints table keyed by query ID.

The part I found most interesting was the two new PostgreSQL 19 contrib modules by Robert Haas, [pg_plan_advice](https://www.postgresql.org/docs/19/pgplanadvice.html) and [pg_stash_advice](https://www.postgresql.org/docs/19/pgstashadvice.html). They are aimed at plan stabilization rather than hints in the classic sense. 

`EXPLAIN (PLAN_ADVICE)` prints a compact "advice string" describing the plan you got (join order, join methods, scan methods, parallelism). You can feed that string back via `pg_plan_advice.advice` to pin the plan, and `pg_stash_advice` stores advice per query ID in shared memory, so it is applied automatically and survives reconnects and restarts. 

The implementation works by constraining the planner rather than replacing it, so you can only ever get a plan that the planner would have considered anyway. Michael's argument was that plan flips are the real problem, and stable plans are often worth a little lost performance. His [slides](https://www.postgresql.eu/events/pgdaynl2026/sessions/session/7815/slides/895/postgresql-optimizer-hints.pdf) are worth a read.

## Speaker dinner in Amsterdam {#speaker_dinner_in_amsterdam}

From Utrecht, I went straight to Amsterdam for the Percona Live speaker dinner on Thursday evening. It was a nice way to arrive at a conference (I was attending for the first time): meet the other speakers over dinner first, then show up the next morning already knowing a few faces.

![](https://clickhouse.com/uploads/cropped_dinner_4486c6c572.png)  
*Percona Live speaker dinner at De Bekeerde Suster—spot me listening carefully to Alastair Turner 🙂*

## Percona Live, Amsterdam {#percona_live_amsterdam}

[Percona Live 2026](https://perconalive.com/2026-amsterdam/) ran from September 9 to 11 at the Mövenpick Hotel Amsterdam City Centre. It is a multi-database conference, with MySQL, PostgreSQL, MongoDB, and Valkey tracks side by side, which makes for a broader audience than at a PGDay. I was only there for the final day.

The final morning opened with a fireside chat called [*The Columnstore Revolution*](https://perconalive.com/2026-amsterdam/talks/fireside-chat-the-columnstore-revolution/), moderated by Percona founder Peter Zaitsev, with Alexey Milovidov, CTO of ClickHouse, and Hannes Mühleisen, co-founder of DuckDB, discussing the resurgence of column-oriented databases and what it means for modern data workloads.

![](https://clickhouse.com/uploads/postgres_conferences_sep2026_image4_71742f0946.jpg)  
*I didn’t know that Alexey Milovidov, our CTO, would be there until Peter Zaitsev told me at the speaker dinner, so that was a nice surprise too.*

## What's new with monitoring in PostgreSQL 19 {#whats_new_with_monitoring_in_postgresql_19}

My [session](https://perconalive.com/2026-amsterdam/talks/whats-new-with-monitoring-in-postgresql-19/) was a 30-minute version of the [talk I'll give at PGConf.EU](https://www.postgresql.eu/events/pgconfeu2026/schedule/session/8182-whats-new-with-monitoring-in-postgresql-19/) in October.

I grouped the changes into five parts:

* **Logging:** `log_lock_waits` is now on by default, `log_min_messages` accepts different log levels for each process type, autoanalyze logging is split from autovacuum with `log_autoanalyze_min_duration`, and messages from remote servers, through replication, `postgres_fdw`, or `dblink` are now formatted like local ones.  
* **WAL and I/O:** the new `wal_fpi_bytes` counter appears in `pg_stat_wal`, per-backend statistics, `VACUUM` and `ANALYZE` log lines, and `EXPLAIN (ANALYZE, WAL)`. `COPY TO` / `FROM` files, pipes and programs now has its own wait events.  
* **`WAIT FOR`:** a new command for read-your-writes semantics on asynchronous standbys, with wait events for the written, flushed, and replayed stages of WAL.  
* **New system views:** `pg_stat_lock`, `pg_stat_recovery`, and `pg_stat_autovacuum_scores`.  
* **Multixacts and wraparound:** the new `pg_get_multixact_stats()`, and the XID wraparound warning threshold moving from 40 million to 100 million transactions.

I closed with what is already committed for PostgreSQL 20 (`pg_stat_get_backend_lock()`, which gives you `pg_stat_lock` per backend). I also covered wait-event statistics, where the discussion on the hackers list keeps moving towards sampling rather than counters.

If you want the long version, I have already written most of it in three posts: [What's New with Monitoring in PostgreSQL 19](https://clickhouse.com/blog/postgres-19-monitoring-whats-new), [Read your writes: WAIT FOR in PostgreSQL 19](https://clickhouse.com/blog/postgresql-19-wait-for-read-your-writes) and [New system views in PostgreSQL 19](https://clickhouse.com/blog/postgres-19-new-system-views).

## What's next {#whats_next}

Both events will be back in 2027 with dates and locations to follow.

Thanks to the people who made PGDay Lowlands happen: Floor Drees, Derk van Veen, Teresa Lopes, Boriss Mejías, Sarah Conway, Stacy Raspopina, Jos van Schouten, Chelsea Dole, Stefan Fercot and Ellert van Koperen. Thanks also to Peter Zaitsev, Alastair Turner, Jan Wieremjewicz and Kai Wagner from the Percona team for having me, and to everyone who came to my talks. See you in Valencia!


---

## Get started today

Interested in seeing how ClickHouse works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-2214-get-started-today-sign-up&utm_blogctaid=2214)

---