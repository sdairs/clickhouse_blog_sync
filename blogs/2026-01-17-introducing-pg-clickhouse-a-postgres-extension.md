---
title: "Introducing pg_clickhouse: A Postgres extension for querying ClickHouse"
date: "2025-12-10T14:27:48.868Z"
author: "David Wheeler "
category: "Product"
excerpt: "Today, we’re pleased to release pg_clickhouse, an Apache 2-licensed PostgreSQL extension to transparently execute analytics queries on ClickHouse directly from PostgreSQL."
---

# Introducing pg_clickhouse: A Postgres extension for querying ClickHouse

Over the last year, we’ve noticed a strong pattern in customers who’ve migrated their analytics workloads to ClickHouse Cloud: [After self-hosted ClickHouse, PostgreSQL](https://www.postgresql.org/) is the most common source of migrations. [ClickPipes](https://clickhouse.com/cloud/clickpipes) made data replication and migrations easy for these use-cases. However, we found that users still face significant challenges migrating queries and application code from PostgreSQL to ClickHouse. To address this, a few months ago we started looking into ways to simplify and reduce the time required to migrate analytical queries from PostgreSQL to ClickHouse.  

Today, we’re pleased to release [pg_clickhouse](https://github.com/ClickHouse/pg_clickhouse/) v0.1.0, an Apache 2-licensed PostgreSQL [extension](https://www.postgresql.org/docs/current/sql-createextension.html) to transparently execute analytics queries on ClickHouse directly from PostgreSQL.

Download pg_clickhouse from:

* [PGXN](https://pgxn.org/dist/pg_clickhouse)  
* [GitHub](https://github.com/ClickHouse/pg_clickhouse/releases)

Or kick the tires by spinning up a Docker instance:

<pre><code type='click-ui' language='bash'>
docker run --name pg_clickhouse -e POSTGRES_PASSWORD=my_pass 
       -d ghcr.io/clickhouse/pg_clickhouse:18
</code></pre>

Consider starting with the [tutorial](https://github.com/ClickHouse/pg_clickhouse/blob/main/doc/tutorial.md), or watch Sai run through the tutorial in the video below.

<iframe width="768" height="432" src="https://www.youtube.com/embed/zK9N5HZC2wA?si=HmYR6mdjLL3PiCeq" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

## **Goals**

Consider the common case where an organization builds an application backed by Postgres, including not only business data and transaction processing, but logging and metrics, as well. As the product grows, user traffic and data volume exponentially increase. As a result, the analytical queries powering both real-time customer-facing features and observability systems begin to slow down.   

Developers frequently mitigate these issues by using PostgreSQL read replicas, a provisional solution, at best. Eventually, they look to move the workload to a specialized analytics database such as ClickHouse. [ClickPipes](https://clickhouse.com/cloud/clickpipes) powers rapid data migration, but what to do with the existing PostgreSQL queries against that data, often created by SQL libraries or [ORM](https://en.wikipedia.org/wiki/Object%E2%80%93relational_mapping)s?

> The time-consuming part isn’t moving data; ClickPipes has that bit nailed. It’s rewriting months or years of analytics SQL baked into dashboards, ORMs, and cron jobs.

We imagined a PostgreSQL extension to reduce the need to migrate those queries at all, where one could follow the data migration with the workload migration simply by pointing those queries at a new Postgres database or schema.

Thus we set forth to build pg_clickhouse with a number of goals in mind:

1. Provide ClickHouse query execution from PostgreSQL  
2. Allow existing PostgreSQL queries to run unmodified  
3. Push down query execution to ClickHouse  
4. Create a foundation for continual query and [pushdown](https://www.postgresql.org/about/featurematrix/detail/postgres_fdw-pushdown/) evolution

What if ClickHouse tables looked just like regular PostgreSQL tables? Say they live in a separate schema from the existing Postgres analytics tables, but provide the identical structure? This pattern would allow existing queries to work as before, with just a change to [search_path](https://www.postgresql.org/docs/current/ddl-schemas.html#DDL-SCHEMAS-PATH).

## **History**

The [SQL/MED](https://en.wikipedia.org/wiki/SQL/MED) addresses exactly this use case by providing database extensions, called *foreign data wrappers,* to allow external data management via SQL. PostgreSQL has supported [foreign data wrappers](https://www.postgresql.org/docs/current/ddl-foreign-data.html) since version 9.3 back in 2011, and a [robust array of “FDW” extensions](https://wiki.postgresql.org/wiki/Foreign_data_wrappers), as they’re commonly  
called, has grown in the ensuing years.

We cast about for existing solutions, and quickly found and validated [clickhouse_fdw](https://github.com/ildus/clickhouse_fdw), developed by [Ildus Kurbangaliev](https://github.com/ildus) for [Adjust](https://www.adjust.com/) based on [initial work](https://github.com/Percona-Lab/clickhousedb_fdw) by [Ibrar Ahmed](https://github.com/ibrarahmad) at [Percona](https://www.percona.com). It supports not only raw data access, but query [pushdown](https://www.postgresql.org/about/featurematrix/detail/postgres_fdw-pushdown/), including for some `JOIN`s and aggregate functions.  

The project originated in 2019 from a fork of [postgres_fdw](https://www.postgresql.org/docs/current/postgres-fdw.html), the canonical reference implementation for PostgreSQL FDWs, as well as a fork of the [ClickHouse C++ library](https://github.com/clickHouse/clickhouse-cpp/). Sadly, it has seen only basic maintenance work since late 2020, mostly patches to ensure it works with newer versions of PostgreSQL. clickhouse_fdw was a great start, but hasn’t benefited from recent pushdown improvements in the PostgreSQL FDW API, including support for advanced aggregations, SEMI-JOINs, subqueries and more. It also lacked testing and support for platforms beyond Linux and lagged updates for new major PostgreSQL releases. After chatting about it with Ildus, we imported much of the functionality into a new project, [pg_clickhouse](https://github.com/ClickHouse/pg_clickhouse/), keeping the [Apache 2 license](https://github.com/clickHouse/pg_clickhouse?tab=Apache-2.0-1-ov-file#readme) for consistency of distribution.

## **Improvements**

While [clickhouse_fdw](https://github.com/ildus/clickhouse_fdw) and its predecessor, [postgres_fdw](https://www.postgresql.org/docs/current/postgres-fdw.html), provided the foundation for our FDW, we set out to modernize the code & build process, to fix bugs & address shortcomings, and to engineer into a complete product featuring near universal [pushdown](https://www.postgresql.org/about/featurematrix/detail/postgres_fdw-pushdown/) for analytics queries and aggregations.

Such advances include:

* Adopting standard [PGXS](https://www.postgresql.org/docs/current/extend-pgxs.html) build pipeline for PostgreSQL extensions  
* Adding prepared `INSERT` support to and adopting the latest supported  
  release of the [ClickHouse C++ library](https://github.com/clickHouse/clickhouse-cpp/)  
* Creating test cases and CI [workflows](https://github.com/ClickHouse/pg_clickhouse/actions) to ensure it works on PostgreSQL versions 13-18 and ClickHouse versions 22-25  
* Support for TLS-based connections for both the [binary protocol](https://clickhouse.com/docs/native-protocol/basics) and the [HTTP API](https://clickhouse.com/docs/interfaces/http), required for [ClickHouse Cloud](https://clickhouse.com/cloud)  
* Bool, Decimal, and JSON support  
* Transparent aggregate function pushdown, including for [ordered-set aggregates](https://www.postgresql.org/docs/current/functions-aggregate.html#FUNCTIONS-ORDEREDSET-TABLE): like `percentile_cont()`  
* [SEMI JOIN](https://clickhouse.com/blog/clickhouse-fully-supports-joins-part1#left--right-semi-join) pushdown

These last two features significantly advance the fitness of a foreign data wrapper for an analytics database. After all, the entire point is to benefit from the execution speed of running analytics workload on a specialized and efficient engine. It wouldn’t be much use if it just returned millions of rows for PostgreSQL to aggregate.

## **Aggregate Pushdown**

Ordered-set aggregates are some of the hardest functions to map between engines because the syntax does not translate directly. Ideally, an aggregate function fully pushes down to ClickHouse for efficient execution. Consider this query adapted from our [HouseClick](https://github.com/ClickHouse/HouseClick) project:

<pre><code type='click-ui' language='sql'>
SELECT
    type,
    round(min(price)) + 100 AS min,
    round(max(price)) AS max,
    round(percentile_cont(0.5) WITHIN GROUP (ORDER BY price)) AS median,
    round(percentile_cont(0.25) WITHIN GROUP (ORDER BY price)) AS "25th",
    round(percentile_cont(0.75) WITHIN GROUP (ORDER BY price)) AS "75th"
FROM
    uk.uk_price_paid
GROUP BY
    type
</code></pre>

This query uses 3 aggregate functions. `min()` and `max()` pushdown automatically, as they have the same names in both ClickHouse and PostgreSQL. But not `percentile_cont()`, which computes or averages the highest value within the percentage of all values. No such function exists in ClickHouse; nor does ClickHouse support the `WITHIN GROUP (ORDER BY x)` ordered set aggregate syntax.

It does, however, provide [parametric aggregate functions](https://clickhouse.com/docs/sql-reference/aggregate-functions/parametric-functions), including `quantile`, which implement a subset of the ordered set aggregate syntax. Thus, pg_clickhouse rewrites this query for ClickHouse as:

<pre><code type='click-ui' language='sql'>
SELECT
    type,
    (round(min(price)) + 100),
    round(max(price)),
    round(quantile(0.5)(price)),
    round(quantile(0.25)(price)),
    round(quantile(0.75)(price))
FROM
    uk.uk_price_paid
GROUP BY
    type
</code></pre>

Note the transparent conversion of `percentile_cont()`s *direct arguments* (`0.5`, `0.25`, `0.75`) to `quantile()`’s *parametric constants,* and then the `ORDER BY` arguments to *function arguments*:

```
percentile_cont(0.5) WITHIN GROUP (ORDER BY price) => quantile(0.5)(price)
```

More than that, pg_clickhouse, like clickhouse_fdw before it, translates [PostgreSQL aggregate](https://www.postgresql.org/docs/current/sql-expressions.html#SYNTAX-AGGREGATES) `FILTER (WHERE)` expressions to ClickHouse [-If combinators](https://clickhouse.com/docs/sql-reference/aggregate-functions/combinators#-if). Here’s the full PostgreSQL query from [HouseClick](https://github.com/ClickHouse/HouseClick):

<pre><code type='click-ui' language='sql'>
SELECT
    type,
    round(min(price)) + 100 AS min,
    round(min(price) FILTER (WHERE town='ILMINSTER' AND district='SOUTH SOMERSET' AND postcode1='TA19')) AS min_filtered,
    round(max(price)) AS max,
    round(max(price) FILTER (WHERE town='ILMINSTER' AND district='SOUTH SOMERSET' AND postcode1='TA19')) AS max_filtered,
    round(percentile_cont(0.5) WITHIN GROUP (ORDER BY price)) AS median,
    round(percentile_cont(0.5) WITHIN GROUP (ORDER BY price) FILTER (WHERE town='ILMINSTER' AND district='SOUTH SOMERSET' AND postcode1='TA19')) AS median_filtered,
    round(percentile_cont(0.25) WITHIN GROUP (ORDER BY price)) AS "25th",
    round(percentile_cont(0.25) WITHIN GROUP (ORDER BY price) FILTER (WHERE town='ILMINSTER' AND district='SOUTH SOMERSET' AND postcode1='TA19')) AS "25th_filtered",
    round(percentile_cont(0.75) WITHIN GROUP (ORDER BY price)) AS "75th",
    round(percentile_cont(0.75) WITHIN GROUP (ORDER BY price) FILTER (WHERE town='ILMINSTER' AND district='SOUTH SOMERSET' AND postcode1='TA19')) AS "75th_filtered"
FROM
    uk.uk_price_paid
GROUP BY
    type
</code></pre>

Run it with `EXPLAIN` to see the query plan:

```shell
                    QUERY PLAN                     
---------------------------------------------------
 Foreign Scan  (cost=1.00..-0.90 rows=1 width=112)
   Relations: Aggregate on (uk_price_paid)
```

Fully pushed down! This rewrite avoids shipping millions of rows back to PostgreSQL and keeps the heavy work inside ClickHouse. Use `EXPLAIN (VERBOSE)` to also output the query sent to ClickHouse (reformatted here):

<pre><code type='click-ui' language='sql'>
SELECT
    type,
    (round(min(price)) + 100),
    round(minIf(price,((((town = 'ILMINSTER') AND (district = 'SOUTH SOMERSET') AND (postcode1 = 'TA19'))) > 0))),
    round(max(price)),
    round(maxIf(price,((((town = 'ILMINSTER') AND (district = 'SOUTH SOMERSET') AND (postcode1 = 'TA19'))) > 0))),
    round(quantile(0.5)(price)),
    round(quantileIf(0.5)(price,((((town = 'ILMINSTER') AND (district = 'SOUTH SOMERSET') AND (postcode1 = 'TA19'))) > 0))),
    round(quantile(0.25)(price)),
    round(quantileIf(0.25)(price,((((town = 'ILMINSTER') AND (district = 'SOUTH SOMERSET') AND (postcode1 = 'TA19'))) > 0))),
    round(quantile(0.75)(price)),
    round(quantileIf(0.75)(price,((((town = 'ILMINSTER') AND (district = 'SOUTH SOMERSET') AND (postcode1 = 'TA19'))) > 0))) 
FROM
    uk.uk_price_paid
GROUP BY
    type
;
</code></pre>

Note that each `FILTER (WHERE)` expression has been converted to an `-If` suffixed ClickHouse function, which computes the equivalent filtering. In other words, this expression:

<pre><code type='click-ui' language='sql'>
min(price) FILTER (WHERE town='ILMINSTER' AND district='SOUTH SOMERSET' AND postcode1='TA19')
</code></pre>

Becomes:

<pre><code type='click-ui' language='sql'>
minIf(price,((((town = 'ILMINSTER') AND (district = 'SOUTH SOMERSET') AND (postcode1 = 'TA19'))) > 0))
</code></pre>

## **SEMI JOIN Pushdown**

As we nailed down the basics for pg_clickhouse, we began testing pushdown against [TPC-H](https://www.tpc.org/tpch/), the venerable “decision support workload” database benchmark, loaded into ClickHouse with scaling factor 1. At first, having added support for the Decimal type, 10 of the 22 queries ran quickly; of those, only 3 fully pushed down from pg_clickhouse foreign tables to ClickHouse sources. One was [query 3](https://github.com/Vonng/pgtpc/blob/master/tpch/queries/3.sql)'s joins:

```shell
EXPLAIN (ANALYZE, COSTS)
-- using default substitutions
select
    l_orderkey,
    sum(l_extendedprice * (1 - l_discount)) as revenue,
    o_orderdate,
    o_shippriority
from
    customer,
    orders,
    lineitem
where
    c_mktsegment = 'BUILDING'
    and c_custkey = o_custkey
    and l_orderkey = o_orderkey
    and o_orderdate < date '1995-03-15'
    and l_shipdate > date '1995-03-15'
group by
    l_orderkey,
    o_orderdate,
    o_shippriority
order by
    revenue desc,
    o_orderdate
LIMIT 10;
                                            QUERY PLAN                                             
---------------------------------------------------------------------------------------------------
 Foreign Scan  (cost=0.00..-10.00 rows=1 width=44) (actual time=60.146..60.162 rows=10.00 loops=1)
   Relations: Aggregate on (((customer) INNER JOIN (orders)) INNER JOIN (lineitem))
   FDW Time: 0.106 ms
 Planning:
   Buffers: shared hit=230
 Planning Time: 6.973 ms
 Execution Time: 61.567 ms
(7 rows)
```

Many of the rest that failed, however, use `JOIN`s to subqueries or `EXISTS` subqueries in `WHERE` clauses. [Query 4](https://github.com/Vonng/pgtpc/blob/master/tpch/queries/4.sql) offers a perfect example of the latter case (with `ANALYZE` disabled, because it took too long):

```shell
EXPLAIN (COSTS, VERBOSE, BUFFERS)
-- using default substitutions
select
    o_orderpriority,
    count(*) as order_count
from
    orders
where
    o_orderdate >= date '1993-07-01'and o_orderdate < date(date '1993-07-01' + interval '3month')
    and exists (select * from lineitem where l_orderkey = o_orderkey and l_commitdate < l_receiptdate)
group by
    o_orderpriority
order by
    o_orderpriority;
                                                                                                                                                                                          QUERY PLAN                                                                                                                                                                                          
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
 Sort  (cost=-80.86..-80.36 rows=200 width=40)
   Output: orders.o_orderpriority, (count(*))
   Sort Key: orders.o_orderpriority
   ->  HashAggregate  (cost=-90.50..-88.50 rows=200 width=40)
         Output: orders.o_orderpriority, count(*)
         Group Key: orders.o_orderpriority
         ->  Nested Loop  (cost=3.50..-93.00 rows=500 width=32)
               Output: orders.o_orderpriority
               Join Filter: (orders.o_orderkey = lineitem.l_orderkey)
               ->  HashAggregate  (cost=2.50..4.50 rows=200 width=4)
                     Output: lineitem.l_orderkey
                     Group Key: lineitem.l_orderkey
                     ->  Foreign Scan on tpch.lineitem  (cost=0.00..0.00 rows=0 width=4)
                           Output: lineitem.l_orderkey, lineitem.l_partkey, lineitem.l_suppkey, lineitem.l_linenumber, lineitem.l_quantity, lineitem.l_extendedprice, lineitem.l_discount, lineitem.l_tax, lineitem.l_returnflag, lineitem.l_linestatus, lineitem.l_shipdate, lineitem.l_commitdate, lineitem.l_receiptdate, lineitem.l_shipinstruct, lineitem.l_shipmode, lineitem.l_comment
                           Remote SQL: SELECT l_orderkey FROM tpch.lineitem WHERE ((l_commitdate < l_receiptdate))
               ->  Foreign Scan on tpch.orders  (cost=1.00..-0.50 rows=1 width=36)
                     Output: orders.o_orderkey, orders.o_custkey, orders.o_orderstatus, orders.o_totalprice, orders.o_orderdate, orders.o_orderpriority, orders.o_clerk, orders.o_shippriority, orders.o_comment
                     Remote SQL: SELECT o_orderkey, o_orderpriority FROM tpch.orders WHERE ((o_orderdate >= '1993-07-01')) AND ((o_orderdate < '1993-10-01')) ORDER BY o_orderpriority ASC NULLS LAST
 Planning:
   Buffers: shared hit=236
(20 rows)
```

Two foreign scans deep in the plan will never be efficient for such a simple query!

We’ve started to address these cases by two means:

1. Setting costs to encourage the PostgreSQL planner to push down queries, as befits analytics use cases  
2. More importantly, we added support for [SEMI JOIN](https://clickhouse.com/blog/clickhouse-fully-supports-joins-part1#left--right-semi-join) pushdown

These changes brought efficient execution (less than 1s) to 21 of the 22 queries, and full pushdown to 12, including [Query 4](https://github.com/Vonng/pgtpc/blob/master/tpch/queries/4.sql):

```shell
EXPLAIN (ANALYZE, COSTS, VERBOSE, BUFFERS)
-- using default substitutions
select
    o_orderpriority,
    count(*) as order_count
from
    orders
where
    o_orderdate >= date '1993-07-01'and o_orderdate < date(date '1993-07-01' + interval '3month')
    and exists (select * from lineitem where l_orderkey = o_orderkey and l_commitdate < l_receiptdate)
group by
    o_orderpriority
order by
    o_orderpriority;
                                                                                                                                                             QUERY PLAN                                                                                                                                                              
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
 Foreign Scan  (cost=1.00..5.10 rows=1000 width=40) (actual time=51.835..51.847 rows=5.00 loops=1)
   Output: orders.o_orderpriority, (count(*))
   Relations: Aggregate on ((orders) LEFT SEMI JOIN (lineitem))
   Remote SQL: SELECT r1.o_orderpriority, count(*) FROM  tpch.orders r1 LEFT SEMI JOIN tpch.lineitem r3 ON (((r3.l_commitdate < r3.l_receiptdate)) AND ((r1.o_orderkey = r3.l_orderkey))) WHERE ((r1.o_orderdate >= '1993-07-01')) AND ((r1.o_orderdate < '1993-10-01')) GROUP BY r1.o_orderpriority ORDER BY r1.o_orderpriority ASC
   FDW Time: 0.056 ms
 Planning:
   Buffers: shared hit=242
 Planning Time: 6.583 ms
 Execution Time: 54.937 ms
(9 rows)
```

This table compares query performance between regular PostgreSQL tables, pg_clickhouse prior to the introduction of SEMI-JOIN performance, and pg_clickhouse with SEMI-JOIN performance (as released today). The tests ran against PostgreSQL and ClickHouse tables loaded with TPC-H data at scaling factor 1; ✅ indicates full pushdown, while a dash indicates a query cancellation after 1m:

| Query | Postgres Runtime | Original Runtime | SEMI JOIN Runtime |
| ----- | ----- | ----- | ----- |
| [1](https://github.com/Vonng/pgtpc/blob/master/tpch/queries/1.sql) | 4478ms | ✅ 82ms | ✅ 73ms |
| [2](https://github.com/Vonng/pgtpc/blob/master/tpch/queries/2.sql) | 560ms | - | - |
| [3](https://github.com/Vonng/pgtpc/blob/master/tpch/queries/3.sql) | 1454ms | ✅ 74ms | ✅ 74ms  |
| [4](https://github.com/Vonng/pgtpc/blob/master/tpch/queries/4.sql) | 650ms | - | ✅ 67ms  |
| [5](https://github.com/Vonng/pgtpc/blob/master/tpch/queries/5.sql) | 452ms | - | ✅ 104ms  |
| [6](https://github.com/Vonng/pgtpc/blob/master/tpch/queries/6.sql) | 740ms | ✅ 33ms | ✅ 42ms  |
| [7](https://github.com/Vonng/pgtpc/blob/master/tpch/queries/7.sql) | 633ms | - | ✅ 83ms  |
| [8](https://github.com/Vonng/pgtpc/blob/master/tpch/queries/8.sql) | 320ms | - | ✅ 114ms  |
| [9](https://github.com/Vonng/pgtpc/blob/master/tpch/queries/9.sql) | 3028ms | - | ✅136ms  |
| [10](https://github.com/Vonng/pgtpc/blob/master/tpch/queries/10.sql) | 6ms | 10ms | ✅ 10ms  |
| [11](https://github.com/Vonng/pgtpc/blob/master/tpch/queries/11.sql) | 213ms | - | ✅ 78ms  |
| [12](https://github.com/Vonng/pgtpc/blob/master/tpch/queries/12.sql) | 1101ms | 99ms | ✅ 37ms  |
| [13](https://github.com/Vonng/pgtpc/blob/master/tpch/queries/13.sql) | 967ms | 1028ms | 1242ms |
| [14](https://github.com/Vonng/pgtpc/blob/master/tpch/queries/14.sql) | 193ms | 168ms | ✅ 51ms  |
| [15](https://github.com/Vonng/pgtpc/blob/master/tpch/queries/15.sql) | 1095ms | 101ms | 522 ms |
| [16](https://github.com/Vonng/pgtpc/blob/master/tpch/queries/16.sql) | 492ms | 1387ms | 1639ms |
| [17](https://github.com/Vonng/pgtpc/blob/master/tpch/queries/17.sql) | 1802ms | - | 9ms |
| [18](https://github.com/Vonng/pgtpc/blob/master/tpch/queries/18.sql) | 6185ms | - | 10ms |
| [19](https://github.com/Vonng/pgtpc/blob/master/tpch/queries/19.sql) | 64ms | 75m | 65ms |
| [20](https://github.com/Vonng/pgtpc/blob/master/tpch/queries/20.sql) | 473ms | - | 4595ms |
| [21](https://github.com/Vonng/pgtpc/blob/master/tpch/queries/21.sql) | 1334ms | - | 1702ms |
| [22](https://github.com/Vonng/pgtpc/blob/master/tpch/queries/22.sql) | 257ms | - | 268ms |

Note the overall performance improvement for nearly all queries against pg_clickhouse foreign tables with SEMI-JOIN support; In a couple of cases — queries 13, 15, and 16 — the query optimizer selects slower plans, and clearly we need to get to the bottom of Query 2’s performance. But the overall performance gain for the other queries is undeniable.

## **The Future**

We’re super happy with these improvements and pleased to bring them to you in this first release. But we’re far from done. Our top focus is finishing pushdown coverage for analytic workloads before adding DML features. Our road map:

1. Get the remaining 10 un-pushed-down [TPC-H](https://www.tpc.org/tpch/) queries optimally planned  
2. Test and fix pushdown for the [ClickBench](https://github.com/ClickHouse/ClickBench/) queries  
3. Support transparent pushdown of all PostgreSQL aggregate functions  
4. Support transparent pushdown of all PostgreSQL functions  
5. Implement comprehensive subquery pushdown  
6. Allow server-level and user-level [ClickHouse settings](https://clickhouse.com/docs/operations/settings) via `CREATE SERVER` and `CREATE USER`  
7. Support all ClickHouse data types  
8. Support lightweight [DELETE](https://clickhouse.com/docs/sql-reference/statements/delete)s and [UPDATE](https://clickhouse.com/docs/sql-reference/statements/update)s  
9. Support batch insertion via [COPY](https://www.postgresql.org/docs/current/sql-copy.html)  
10. Add a function to execute an arbitrary ClickHouse query and return its results as a tables  
11. Add support for pushdown of UNION queries when they all query the remote  
    database

And more; so much to do!  Install pg_clickhouse from [GitHub](https://github.com/ClickHouse/pg_clickhouse/releases) and [PGXN](https://pgxn.org/dist/pg_clickhouse) releases and try it on a real workload. Tell us via [project issues](https://github.com/ClickHouse/pg_clickhouse/issues) where pushdown breaks. We’ll fix it.



---

## Interested in trying out the new extension?

Try out the pg_clickhouse tutorial in the project's GitHub repository.

[Try out the tutorial](https://github.com/ClickHouse/pg_clickhouse/blob/main/doc/tutorial.md?loc=blog-cta-24-interested-in-trying-out-the-new-extension-try-out-the-tutorial&utm_blogctaid=24)

---