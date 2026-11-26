---
title: "Hints and hazards: pg_plan_advice in PG19"
date: "2026-11-25T20:49:01.132Z"
author: "Colton Shepard"
category: "Engineering"
excerpt: "Explore PostgreSQL 19’s pg_plan_advice with examples on ClickHouse Managed Postgres, showing when query hints improve performance and when stale hints make it worse."
---

# Hints and hazards: pg_plan_advice in PG19

Over the past decade, one of the most contentious Postgres feature requests has been for query hints. The planner is remarkably effective at making good decisions, but it doesn’t always do so, and query hints have been proposed as a way to fill that gap. They’ve been a popular feature on other databases for years, and some would say that they are essential for production usage to ensure that indexes are used effectively and queries are planned sensibly. While [pg_hint_plan](https://www.postgresql.org/about/news/pg_hint_plan-v160-released-2712/) has existed for a while, the Postgres community has historically been divided on this topic, with the general consensus being that planner failures were bugs that should be fixed instead of being worked around.

Postgres 19 brings 2 new contrib modules that collectively provide the plan hint experience without affecting all queries or SQL syntax. [pg_plan_advice](https://www.postgresql.org/docs/19/pgplanadvice.html) works at the session level, allowing you to simply SET how the next queries will be planned. The technique supports a decent list of features, letting you specify scan method, join order, join method, parallelism, partitionwise joins, and semijoin uniqueness.

The companion extension provided is [pg_stash_advice](https://www.postgresql.org/docs/19/pgstashadvice.html). This is meant to apply to query identifiers instead of specific queries, so rather than using SET to hint, you instead find a specific query identifier and tell Postgres to always apply your hints only to that query. It supports the same capabilities for affecting query plans as pg_plan_advice, so most of this article applies to it as well.

Under the hood, these extensions work by telling the planner that it should not pick the options you didn’t select. This can’t actually force Postgres to pick the plan that you actually want, so if there’s no viable way to actually use the hint, the advice will be partially or fully ignored. In addition, there is no check that the advice is good- the planner will happily accept input that actively degrades query performance. In practice, this means that it can be similar to existing `enable_` knobs you may have already used to force certain plans on queries. For example, if you’re trying to convince the planner to use an index, here’s the old way and the new way you’d consider. They do similar things, but the advice extensions provide a lot more capability and granularity:

<pre><code type='click-ui' language='sql'>
SET enable_seqscan = off;
SELECT...;

SET pg_plan_advice.advice = 'INDEX_SCAN(my_table my_table_some_idx)';
SELECT...;
</code></pre>

## The scenarios {#the_scenarios}

I’ve put together a few examples of queries where you might want to consider using pg_plan_advice, and did some testing to see how well it works in practice. All of these tests ran on ClickHouse Managed Postgres, on a m6gd.xlarge machine with 4 vCPUs, 16GB RAM, and a 237GB local NVME drive. The tests are fairly artificial, as the planner is remarkably clever and it’s surprisingly difficult to construct scenarios that reliably give it trouble.

pg_plan_advice ships as a contrib module, so you’ll probably want to add it to your server’s `shared_preload_libraries` or take one of the following steps to get it working in a PG19 environment:

<pre><code type='click-ui' language='sql'>
-- session-level enablement
LOAD 'pg_plan_advice';

-- if updating PG configs is impractical, this may be a reasonable alternative.
-- keep in mind that this overwrites, so add your existing libraries too
ALTER ROLE &lt;test_role&gt; SET session_preload_libraries = 'pg_plan_advice';
</code></pre>

This post uses a lot of SET commands for demonstration purposes. If you are looking to use pg_plan_advice in a production system, please keep in mind that these should instead generally be `SET LOCAL` in a transaction to prevent unexpected effects on other queries.

## Scenario 1: `ORDER BY… LIMIT` {#scenario_1_order_by_limit}

The planner generally assumes that rows in a table are spread somewhat evenly. Unfortunately, the ISO Standard User does not actually exist, so a lot of database writes are clustered around bursts of correlated activity. This can lead to a scenario where the planner knows a few percent of rows match a given filter, starts walking through a primary key column to find them, and ends up scanning nearly the whole index before getting enough hits.

<pre><code type='click-ui' language='sql'>
CREATE TABLE events (
  id      bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  status  text NOT NULL,
  payload text
);
-- let's insert generic background rows here
INSERT INTO events (status, payload)
SELECT 'done', repeat('x', 100) FROM generate_series(1, 10_000_000);

-- now, let's insert the rare rows, all clustered at the end
INSERT INTO events (status, payload)
SELECT 'failed', repeat('x', 100) FROM generate_series(1, 50_000);
CREATE INDEX events_status_idx ON events (status);
VACUUM ANALYZE events;
</code></pre>

Here’s the query we’ll use for this:

<pre><code type='click-ui' language='sql'>
SELECT * FROM events WHERE status = 'failed' ORDER BY id LIMIT 10;
</code></pre>

Running it does, indeed, give us a terrible plan.

```shell
Limit  (cost=0.43..66.77 rows=10 width=114) (actual time=1461.915..1461.919 rows=10.00 loops=1)
  Buffers: shared hit=209144
  ->  Index Scan using events_pkey on events  (cost=0.43..388915.84 rows=58625 width=114) (actual time=1461.914..1461.916 rows=10.00 loops=1)
        Filter: (status = 'failed'::text)
        Rows Removed by Filter: 10000000
        Index Searches: 1
        Buffers: shared hit=209144
Planning Time: 0.091 ms
Generated Plan Advice:
  INDEX_SCAN(events public.events_pkey)
  NO_GATHER(events)
Execution Time: 1461.947 ms
```

Excellent, we’ve reproduced the failure! The index scan looks like it should be reasonable, and the cost of 66.77 is trivial: the planner clearly expected to find all 10 rows it needed immediately. Unfortunately, it had to gather and discard 10,000,000 rows before finding a useful result, which obviously took far longer than you’d expect. 

You’ve probably noticed the “Generated Plan Advice” section in this explain plan as well. This is another new feature; we’re using `EXPLAIN (ANALYZE, BUFFERS, PLAN_ADVICE)` here. Since we didn’t provide plan advice, this output just shows the plan it actually used.

We could definitely fix this with a new index, but that isn’t always a good option when you see this kind of thing in the wild, so let’s try a bitmap heap scan. It works by first constructing a bitmap of potential row locations using a bitmap index scan, and then decodes it to fetch the underlying data. It’s better suited to bulk operations, so it’s a good bet given how uncooperative the index scan is proving to be. Here’s all we need to do to actually use it:

<pre><code type='click-ui' language='sql'>
SET LOCAL pg_plan_advice.advice = 'BITMAP_HEAP_SCAN(events)';
</code></pre>

Here’s the new EXPLAIN.

```shell
Limit  (cost=89034.29..89035.45 rows=10 width=114) (actual time=7.285..9.655 rows=10.00 loops=1)
  Buffers: shared hit=1009
  ->  Gather Merge  (cost=89034.29..95705.84 rows=57283 width=114) (actual time=7.284..9.653 rows=10.00 loops=1)
        Workers Planned: 2
        Workers Launched: 2
        Buffers: shared hit=1009
        ->  Sort  (cost=88034.26..88093.93 rows=23868 width=114) (actual time=4.096..4.098 rows=10.00 loops=3)
              Sort Key: id
              Sort Method: top-N heapsort  Memory: 27kB
              Buffers: shared hit=1009
              Worker 0:  Sort Method: top-N heapsort  Memory: 27kB
              Worker 1:  Sort Method: top-N heapsort  Memory: 27kB
              ->  Parallel Bitmap Heap Scan on events  (cost=498.29..87518.48 rows=23868 width=114) (actual time=0.704..2.586 rows=16666.67 loops=3)
                    Recheck Cond: (status = 'failed'::text)
                    Heap Blocks: exact=464
                    Buffers: shared hit=995
                    Worker 0:  Heap Blocks: exact=224
                    Worker 1:  Heap Blocks: exact=222
                    ->  Bitmap Index Scan on events_status_idx  (cost=0.00..483.96 rows=57284 width=0) (actual time=1.743..1.743 rows=50000.00 loops=1)
                          Index Cond: (status = 'failed'::text)
                          Index Searches: 1
                          Buffers: shared hit=45
Planning Time: 0.104 ms
Supplied Plan Advice:
  BITMAP_HEAP_SCAN(events) /* matched */
Generated Plan Advice:
  BITMAP_HEAP_SCAN(events)
  GATHER_MERGE(events)
Execution Time: 9.687 ms
```

The parallelism makes it a bit tricky to read, but a few things stand out. First, we got <10ms execution time, so the bitmap heap scan actually did help. Second, we can now see the supplied plan advice at the bottom of the EXPLAIN output, and the matched feedback (without a failed flag) makes it clear that the planner actually used our advice. Please note that this does not necessarily mean that the planner benefited from the advice.

## Scenario 2: `JOIN` correlation {#scenario_2_join_correlation}

JOINs can be a source of planner complications, as statistics are resolutely single-table. The planner has a limited ability to predict how many rows will be pruned by filters on JOINed tables, so it can be way off base on selectivity. In general, it assumes that filters on different tables are independent of each other, which is a fairly easy assumption to violate with the following setup:

<pre><code type='click-ui' language='sql'>
CREATE TABLE accounts (id int PRIMARY KEY, plan text NOT NULL);
INSERT INTO accounts
SELECT g, CASE WHEN g % 100 = 0 THEN 'enterprise' ELSE 'standard' END
FROM generate_series(1, 1_000_000) g;
CREATE INDEX ON accounts (plan);

CREATE TABLE actions (id bigint PRIMARY KEY, account_id int NOT NULL, kind text NOT NULL, created_at timestamptz NOT NULL);
-- baseline rows
INSERT INTO actions
SELECT g, 1 + (random() * 999999)::int,
       (ARRAY['login','view','edit','sync'])[1 + (g % 4)],
       now() - random() * interval '90 days'
FROM generate_series(1, 10_000_000) g;
-- trial_start rows, randomly spread across non-enterprise accounts
INSERT INTO actions
SELECT 10_000_000 + g,
       (1 + (random() * 999998)::int) / 100 * 100 + 1 + (random() * 98)::int,  -- never a multiple of 100
       'trial_start',
       now() - random() * interval '90 days'
FROM generate_series(1, 500_000) g;
-- a handful of trial_start rows for enterprise accounts, also scattered randomly
INSERT INTO actions
SELECT 20_000_000 + g, 100 * (1 + (random() * 9999)::int), 'trial_start',
       now() - random() * interval '90 days'
FROM generate_series(1, 20) g;

CREATE INDEX actions_created_at_idx   ON actions (created_at);
CREATE INDEX actions_account_kind_idx ON actions (account_id, kind);
CREATE INDEX actions_kind_idx         ON actions (kind);
VACUUM ANALYZE accounts, actions;
</code></pre>

Here’s our baseline query. It’s just a simple join, filter, and limit:

<pre><code type='click-ui' language='sql'>
SELECT act.*
FROM actions act JOIN accounts a ON a.id = act.account_id
WHERE a.plan = 'enterprise' AND act.kind = 'trial_start'
ORDER BY act.created_at DESC
LIMIT 10;
</code></pre>

Here’s our first plan, with the planner doing the heavy lifting for us:

```shell
  Limit  (cost=0.86..1017.87 rows=10 width=25) (actual time=742.602..3836.972 rows=10.00 loops=1)
    Buffers: shared hit=4765176
    ->  Nested Loop  (cost=0.86..537793.14 rows=5288 width=25) (actual time=742.602..3836.963 rows=10.00 loops=1)
          Buffers: shared hit=4765176
          ->  Index Scan Backward using actions_created_at_idx on actions act  (cost=0.43..300345.83 rows=513441 width=25) (actual time=0.012..3153.670 rows=190851.00 loops=1)
                Filter: (kind = 'trial_start'::text)
                Rows Removed by Filter: 3800104
                Index Searches: 1
                Buffers: shared hit=4001812
          ->  Index Scan using accounts_pkey on accounts a  (cost=0.42..0.46 rows=1 width=4) (actual time=0.003..0.003 rows=0.00 loops=190851)
                Index Cond: (id = act.account_id)
                Filter: (plan = 'enterprise'::text)
                Rows Removed by Filter: 1
                Index Searches: 190851
                Buffers: shared hit=763364
  Planning:
    Buffers: shared hit=16
  Planning Time: 0.262 ms
  Generated Plan Advice:
    JOIN_ORDER(act a)
    NESTED_LOOP_PLAIN(a)
    INDEX_SCAN(act public.actions_created_at_idx a public.accounts_pkey)
    NO_GATHER(act a)
  Execution Time: 3837.021 ms
```

This plan is honestly pretty terrible. The planner correctly understands that there are 500K or so `trial_start` rows, and that 1% of customers are `enterprise` customers. It then multiplies these numbers by each other, which leads it to predict that 5000 rows will match, and it only needs 10. Unfortunately, the filters aren’t as independent as it’s estimating, so only 20 out of the 500K rows actually have the values it’s looking for. As such, it ends up scanning a lot more rows than it was counting on to get this result. You can see as much in the row estimates above: the planner predicts 5288 rows when we know there are only 20, which is right in line with the math.

To fix this, let’s try giving plan advice. We want the join order to prioritize accounts first, as that will give us a vastly more selective filter to cut down on row counts.

<pre><code type='click-ui' language='sql'>
SET LOCAL pg_plan_advice.advice = 'JOIN_ORDER(a act)';
</code></pre>

Here’s what it gives us:

```shell
  Limit  (cost=16804.99..16806.16 rows=10 width=25) (actual time=17.673..20.267 rows=10.00 loops=1)
    Buffers: shared hit=35486
    ->  Gather Merge  (cost=16804.99..17420.75 rows=5287 width=25) (actual time=17.672..20.264 rows=10.00 loops=1)
          Workers Planned: 2
          Workers Launched: 2
          Buffers: shared hit=35486
          ->  Sort  (cost=15804.97..15810.48 rows=2203 width=25) (actual time=14.854..14.856 rows=5.00 loops=3)
                Sort Key: act.created_at DESC
                Sort Method: quicksort  Memory: 25kB
                Buffers: shared hit=35486
                Worker 0:  Sort Method: quicksort  Memory: 25kB
                Worker 1:  Sort Method: quicksort  Memory: 25kB
                ->  Nested Loop  (cost=90.58..15757.36 rows=2203 width=25) (actual time=2.455..14.835 rows=6.67 loops=3)
                      Buffers: shared hit=35470
                      ->  Parallel Bitmap Heap Scan on accounts a  (cost=90.15..5425.23 rows=4292 width=4) (actual time=0.724..3.204 rows=3333.33 loops=3)
                            Recheck Cond: (plan = 'enterprise'::text)
                            Heap Blocks: exact=1986
                            Buffers: shared hit=5457
                            Worker 0:  Heap Blocks: exact=1713
                            Worker 1:  Heap Blocks: exact=1707
                            ->  Bitmap Index Scan on accounts_plan_idx  (cost=0.00..87.57 rows=10300 width=0) (actual time=1.202..1.202 rows=10000.00 loops=1)
                                  Index Cond: (plan = 'enterprise'::text)
                                  Index Searches: 1
                                  Buffers: shared hit=11
                      ->  Index Scan using actions_account_kind_idx on actions act  (cost=0.43..2.40 rows=1 width=25) (actual time=0.003..0.003 rows=0.00 loops=10000)
                            Index Cond: ((account_id = a.id) AND (kind = 'trial_start'::text))
                            Index Searches: 10000
                            Buffers: shared hit=30013
  Planning:
    Buffers: shared hit=16
  Planning Time: 0.269 ms
  Supplied Plan Advice:
    JOIN_ORDER(a act) /* matched */
  Generated Plan Advice:
    JOIN_ORDER(a act)
    NESTED_LOOP_PLAIN(act)
    BITMAP_HEAP_SCAN(a)
    INDEX_SCAN(act public.actions_account_kind_idx)
    GATHER_MERGE((act a))
  Execution Time: 20.309 ms
```

A nearly 200x improvement is absurdly better. By adjusting the join order, we’re able to take full advantage of the `accounts` table’s much lower number of rows matching the `enterprise` filter, which lets us dramatically cut down on the number of rows to scan. You probably won’t get quite as big a speedup in most cases in production, but this pattern comes up every now and then, and having a tool to address it is priceless.

This is probably the use case that fits the plan advice feature best. It’s rare, but there are not a lot of good alternatives for dealing with it. I’ve come across similar challenges perhaps a half dozen times, and while I was able to find workarounds, they got pretty hacky and difficult to reason around.

## Scenario 3: Handling stale hints {#scenario_3_handling_stale_hints}

We’ve got some promising results in scenario 1, but what happens if the data changes to be less lumpy while our hint is still in place? To test this, let’s set every third row to the failed state:

<pre><code type='click-ui' language='sql'>
UPDATE events SET status = 'failed' WHERE id % 3 = 0;
VACUUM ANALYZE events;
</code></pre>

This means we only need to walk a few rows to get what we’re looking for, so the planner estimate should be able to get us a good outcome. Sure enough, if we run without any hints, we get this:

```shell
Limit  (cost=0.43..1.86 rows=10 width=114) (actual time=0.021..0.031 rows=10.00 loops=1)
  Buffers: shared hit=23
  ->  Index Scan using events_pkey on events  (cost=0.43..497822.11 rows=3496879 width=114) (actual time=0.020..0.029 rows=10.00 loops=1)
        Filter: (status = 'failed'::text)
        Rows Removed by Filter: 20
        Index Searches: 1
        Buffers: shared hit=23
Planning Time: 0.091 ms
Generated Plan Advice:
  INDEX_SCAN(events public.events_pkey)
  NO_GATHER(events)
Execution Time: 0.052 ms
```

That’s the kind of result we wanted to see in the first place! Let’s see how we do with the earlier hint to use a bitmap heap scan in place:

```shell
Limit  (cost=357696.74..357697.90 rows=10 width=114) (actual time=365.137..368.829 rows=10.00 loops=1)
  Buffers: shared hit=64540
  ->  Gather Merge  (cost=357696.74..764965.92 rows=3496879 width=114) (actual time=365.136..368.826 rows=10.00 loops=1)
        Workers Planned: 2
        Workers Launched: 2
        Buffers: shared hit=64540
        ->  Sort  (cost=356696.71..360339.30 rows=1457033 width=114) (actual time=361.889..361.890 rows=7.00 loops=3)
              Sort Key: id
              Sort Method: top-N heapsort  Memory: 27kB
              Buffers: shared hit=64540
              Worker 0:  Sort Method: top-N heapsort  Memory: 27kB
              Worker 1:  Sort Method: top-N heapsort  Memory: 27kB
              ->  Parallel Bitmap Heap Scan on events  (cost=31349.45..325210.75 rows=1457033 width=114) (actual time=102.727..260.178 rows=1127777.67 loops=3)
                    Recheck Cond: (status = 'failed'::text)
                    Rows Removed by Index Recheck: 2
                    Heap Blocks: exact=9604 lossy=10957
                    Buffers: shared hit=64526
                    Worker 0:  Heap Blocks: exact=9577 lossy=11034
                    Worker 1:  Heap Blocks: exact=9675 lossy=10972
                    ->  Bitmap Index Scan on events_status_idx  (cost=0.00..30475.23 rows=3496879 width=0) (actual time=100.233..100.234 rows=3383333.00 loops=1)
                          Index Cond: (status = 'failed'::text)
                          Index Searches: 1
                          Buffers: shared hit=2667
Planning Time: 0.127 ms
Supplied Plan Advice:
  BITMAP_HEAP_SCAN(events) /* matched */
Generated Plan Advice:
  BITMAP_HEAP_SCAN(events)
  GATHER_MERGE(events)
Execution Time: 368.866 ms
```

That’s 7,000 times worse, and the feedback doesn’t show a problem because it’s still `matched`. Now that the artificial data condition tripping up the planner is gone, the planner has no problem doing a better job than our hinted alternate. This is a good reminder that all hints should be regularly checked for ongoing necessity — otherwise, your performance fixes can lead to performance issues.

## Conclusion {#conclusion}

We’ve gone through a few scenarios, and it’s clear that `pg_plan_advice` is a powerful but situational tool. It’s not easy to construct scenarios that reliably confuse the planner, but they show up in production often enough that it’s worth having a tool to address them. pg_plan_advice is new enough that it’s hard to say for sure, but I’d bet from what I’ve shown here that the following workflow will serve you well:

1. If you get a mysteriously slow query and tuning doesn’t get the results you wanted, then plan advice is a good thing to try.

2. If it works, then baking it into the transaction with `SET LOCAL`  is a good way to improve performance.

    1. You can also tie it to the query ID with `pg_stash_advice`. If you do so, note that this needs special handling for HA failover since it is not WAL-logged, and is not well explored.

3. If you do set advice, check on it in a few months, as shifting data and query patterns can make it counterproductive.

---

## Get started with ClickHouse Managed Postgres today

Interested in seeing how ClickHouse Managed Postgres works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?intent=pg&loc=blog-cta-3183-get-started-with-clickhouse-managed-postgres-today-sign-up&utm_blogctaid=3183)

---