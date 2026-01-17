---
title: "ClickHouse Release 25.12"
date: "2026-01-12T13:23:50.724Z"
author: "The ClickHouse Team"
category: "Engineering"
excerpt: "ClickHouse 25.12 is here! In this post, you will learn about faster top-n queries with data skipping indexes, faster lazy reading with join-style execution model, and more!"
---

# ClickHouse Release 25.12

Another month goes by, which means it’s time for another release! 

<p>ClickHouse version 25.12 contains 26 new features &#127876; 31 performance optimizations `&#9976;` 129 bug fixes &#x2603;</p>

This release we have faster top-n queries with data skipping indexes, faster lazy reading with join-style execution model, and more!

## New contributors

A special welcome to all the new contributors in 25.12! The growth of ClickHouse's community is humbling, and we are always grateful for the contributions that have made ClickHouse so popular.

Below are the names of the new contributors:

*Alex Soffronow Pagonidis, Alexey Bakharew, Govind R Nair, Jeremy Aguilon, Kirill Kopnev, LeeChaeRok, MakarDev, Paresh Joshi, Revertionist, Sam Kaessner, Seva Potapov, Shaurya Mohan, Sümer Cip, Yonatan-Dolan, alsugiliazova, htuall, ita004, jetsetbrand, mostafa, punithns97, rainac1*

Hint: if you’re curious how we generate this list… [here](https://gist.github.com/gingerwizard/5a9a87a39ba93b422d8640d811e269e9).

<iframe width="768" height="432" src="https://www.youtube.com/embed/UdxLygnjsRY?si=i29B3Q7eTEC6hkSv" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

You can also [view the slides from the presentation](https://presentations.clickhouse.com/2025-release-25.12/).

## Faster Top-N queries with data skipping indexes

### Contributed by Shankar Iyer

> **Why this matters**  
ClickHouse is the fastest production-grade analytical DBMS on [ClickBench](https://benchmark.clickhouse.com/), a benchmark based on [real-world web analytics traffic](https://github.com/ClickHouse/ClickBench/?tab=readme-ov-file#overview) with results published for more than 70 database systems. It is also the fastest production-grade analytical system on [JSONBench](https://jsonbench.com/) among all major engines with first-class JSON support.<br/><br/>ClickHouse’s performance leadership comes from **many** [engine-level optimizations](https://clickhouse.com/docs/concepts/why-clickhouse-is-so-fast#meticulous-attention-to-detail) for common analytical query patterns. **Top-N queries** are one of these patterns. They appear frequently in real workloads. [More than half](https://github.com/ClickHouse/ClickBench/blob/main/clickhouse/queries.sql) of the queries in ClickBench and a [significant fraction](https://github.com/ClickHouse/JSONBench/blob/main/clickhouse/queries.sql) of those in JSONBench follow a Top-N pattern. This section focuses on the specific optimizations ClickHouse applies to make Top-N queries faster.

Top-N queries are ubiquitous in data analytics. Some typical examples include retrieving the most recent events, the highest-scoring users, the most expensive transactions, or the top orders:

<pre><code type='click-ui' language='sql'>
SELECT *
FROM orders
ORDER BY total_amount DESC
LIMIT 3;
</code></pre>

   
ClickHouse already applies several optimizations to run Top-N queries efficiently and fast:

1. [Streaming](https://clickhouse.com/docs/sql-reference/statements/select#implementation-details) Top-N (bounded memory):   
   ClickHouse doesn’t sort all rows at once. Instead, it streams data and keeps only the current Top-N candidates, so memory usage stays proportional to N rather than to the table size.

2. [Read in order](https://clickhouse.com/blog/clickhouse-faster-queries-with-projections-and-primary-indexes#utilize-indexes-for-preventing-resorting-and-enabling-short-circuiting) (avoid sorting completely):  
   If the data on disk is already ordered by the ORDER BY column(s), or can be read in that order via a [projection](https://clickhouse.com/docs/sql-reference/statements/alter/projection), ClickHouse can avoid sorting and simply read the first rows in order.

3. [Lazy reading](https://clickhouse.com/blog/clickhouse-gets-lazier-and-faster-introducing-lazy-materialization) (defer reading non-order columns):  
   Even when the query selects many columns, ClickHouse can first determine the Top-N rows using only the columns needed for ordering, and only then read the remaining columns for those rows. This reduces I/O dramatically.

These optimizations are **orthogonal** to each other: they address different aspects of Top-N query execution and can be applied independently or in combination within a single query.

This release introduces additional, orthogonal optimizations for Top-N queries: using [data skipping indexes](https://clickhouse.com/docs/optimize/skipping-indexes/examples) for static or dynamic top-n filtering to **significantly reduce the number of rows that need to be processed**.

### Static Top-N filtering (no predicates) 

Let’s start with the simplest case: a Top-N query without any predicates or filters.

<pre><code type='click-ui' language='sql'>
SELECT * FROM T ORDER BY c ASC LIMIT 3;
</code></pre>

   
Even without a WHERE clause, ClickHouse can reduce the amount of data read if a [minmax data skipping index](https://clickhouse.com/docs/optimize/skipping-indexes/examples) exists on the ORDER BY column `c`. 

To illustrate this, assume table T consists of five [granules](https://clickhouse.com/docs/guides/best-practices/sparse-primary-indexes#data-is-organized-into-granules-for-parallel-data-processing) (the smallest processing units in ClickHouse, each covering 8,192 rows by default). For each granule, the min and max values of column `c` are stored in a minmax data skipping index, as shown below:

| Granule | min(c) | max(c) |
|---------|--------|--------|
| 1       | 40     | 90     |
| 2       | 10     | 30     |
| 3       | 5      | 25     |
| 4       | 60     | 110    |
| 5       | 1      | 15     |

This is what ClickHouse does for `ORDER BY c LIMIT 3`:

* Look only at min(c) values from the minmax index.  
  Smallest mins are:  
  * Granule 5 → min = 1  
  * Granule 3 → min = 5  
  * Granule 2 → min = 10

* Read only granules 5, 3, and 2 from disk  
* Merge their rows → return top 3 values

All remaining granules are skipped entirely.

*(Note that in practice, more than three granules may be read because data is processed in blocks, which can span multiple adjacent granules, and [multiple threads process data in parallel](https://clickhouse.com/docs/optimize/query-parallelism#distributing-work-across-processing-lanes).)*

To illustrate the effect, we use the [anonymized web analytics example data](https://clickhouse.com/docs/getting-started/example-datasets/metrica). We [created the table and loaded the data](https://pastila.nl/?000d9e4d/048b6bdf283322bef6dc9bba561215c6#VWIpCGN9UO1RrWi2ilL5eA==GCM) on an AWS m6i.8xlarge EC2 instance (32 cores, 128 GB RAM) with a gp3 EBS volume (16k IOPS, 1000 MiB/s max throughput).

This is our example Top-N query without any predicates:

<pre><code type='click-ui' language='sql'>
SELECT URL, EventTime 
FROM hits 
ORDER BY EventTime
LIMIT 10;
</code></pre>

On 25.12, *without* the new data-skipping-index-based optimization, the fastest of three runs finished in 0.044 seconds:

```shell
10 rows in set. Elapsed: 0.044 sec. Processed 100.08 million rows, 1.20 GB (2.27 billion rows/s., 27.26 GB/s.)
Peak memory usage: 2.23 MiB.

10 rows in set. Elapsed: 0.044 sec. Processed 100.08 million rows, 1.20 GB (2.29 billion rows/s., 27.56 GB/s.)
Peak memory usage: 2.25 MiB.

10 rows in set. Elapsed: 0.044 sec. Processed 100.08 million rows, 1.20 GB (2.27 billion rows/s., 27.33 GB/s.)
Peak memory usage: 2.24 MiB.

```

Note that all ~100 million rows of the hits table got processed.

Now we run the same query *with* the new data skipping-indexes-based optimization by enabling the new [use_skip_indexes_for_top_k](https://clickhouse.com/docs/operations/settings/settings#use_skip_indexes_for_top_k) setting. Note that the table has a [minmax data skipping index on the `EventTime` column](https://pastila.nl/?000d9e4d/048b6bdf283322bef6dc9bba561215c6#VWIpCGN9UO1RrWi2ilL5eA==GCM).

<pre><code type='click-ui' language='sql'>
SELECT URL, EventTime 
FROM hits 
ORDER BY EventTime
LIMIT 10
SETTINGS use_skip_indexes_for_top_k = 1;
</code></pre>

Now the fastest of three runs finished in 0.009 seconds:

```shell
10 rows in set. Elapsed: 0.009 sec. Processed 163.84 thousand rows, 4.95 MB (17.48 million rows/s., 528.35 MB/s.)
Peak memory usage: 917.51 KiB.

10 rows in set. Elapsed: 0.009 sec. Processed 163.84 thousand rows, 4.95 MB (18.03 million rows/s., 544.98 MB/s.)
Peak memory usage: 198.47 KiB.

10 rows in set. Elapsed: 0.009 sec. Processed 163.84 thousand rows, 4.95 MB (18.19 million rows/s., 549.68 MB/s.)
Peak memory usage: 198.47 KiB.
```

This is roughly **5 times faster than before**. Instead of processing the table’s full **~100 million rows**, ClickHouse processed only about **163 thousand rows**, which reduced the amount of data read from roughly **1.2 GB** to just **4.95 MB**.

This I/O benefit will grow with table size: when tables run into billions or trillions of rows, and especially when the cache is cold, avoiding unnecessary reads at the granule level becomes increasingly impactful.

> Importantly, this reduction happens **before** any rows are read, purely based on granule-level metadata.

###  Dynamic Top-N threshold filtering (with predicates)

So far, we’ve looked at Top-N queries without predicates, where granules can be preselected using static min/max metadata on the ORDER BY column.

When a Top-N query also includes predicates, the data skipping becomes *dynamic*.

As the query executes, ClickHouse continuously maintains the current Top-N result set. **The current N-th value effectively acts as a dynamic threshold.**

This mechanism builds on [streaming for secondary indices](https://clickhouse.com/blog/clickhouse-release-25-09#streaming-for-secondary-indices), introduced in ClickHouse 25.9: Instead of evaluating data skipping indexes upfront, ClickHouse interleaves data skipping index checks with data reads. As soon as a granule becomes eligible for reading (after [primary index analysis](https://clickhouse.com/docs/primary-indexes) for the predicate evaluation), its corresponding minmax data skipping index entry is consulted.

At that point, the current Top-N threshold is compared against the granule’s min/max metadata. If the granule cannot possibly contain values that would improve the Top-N result set, it is skipped immediately and never read.

As execution progresses and better Top-N candidates are found, the threshold tightens further, allowing ClickHouse to prune an increasing number of granules dynamically during query execution. Because the query stops once the Top-N result is complete, tighter thresholds allow ClickHouse to stop reading and skipping granules earlier.

We demonstrate the effectiveness of these mechanics with another example Top-N query, this time with a predicate:

<pre><code type='click-ui' language='sql'>
SELECT URL,EventTime 
FROM hits 
WHERE URL LIKE '%google%'
ORDER BY EventTime
LIMIT 10;
</code></pre>

On 25.12, *without* the new data-skipping-index-based dynamic top-N threshold filtering, the fastest of three runs finished in 0.325 seconds. We disabled the [query condition cache](https://clickhouse.com/blog/introducing-the-clickhouse-query-condition-cache) for all runs to get the raw data processing behavior each time.

```shell
10 rows in set. Elapsed: 0.333 sec. Processed 100.00 million rows, 9.42 GB (299.96 million rows/s., 28.26 GB/s.)
Peak memory usage: 143.92 MiB.

10 rows in set. Elapsed: 0.325 sec. Processed 100.00 million rows, 9.42 GB (307.37 million rows/s., 28.95 GB/s.)
Peak memory usage: 138.46 MiB.

10 rows in set. Elapsed: 0.334 sec. Processed 100.00 million rows, 9.42 GB (299.55 million rows/s., 28.22 GB/s.)
Peak memory usage: 147.47 MiB.
```

Note that all 100 million rows of the hits table got processed.

Now we run the same query *with* the new data-skipping-index-based dynamic top-N threshold filtering by enabling [streaming for secondary indices](https://clickhouse.com/blog/clickhouse-release-25-09#streaming-for-secondary-indices) and by enabling the new [use_top_k_dynamic_filtering](https://clickhouse.com/docs/operations/settings/settings#use_top_k_dynamic_filtering) setting. Note that the table has a [minmax data skipping index on the `EventTime` column](https://pastila.nl/?000d9e4d/048b6bdf283322bef6dc9bba561215c6#VWIpCGN9UO1RrWi2ilL5eA==GCM) and we disabled the [query condition cache](https://clickhouse.com/blog/introducing-the-clickhouse-query-condition-cache) for all runs to fully isolate the dynamic top-N threshold filtering.  

<pre><code type='click-ui' language='sql'>
SELECT URL,EventTime 
FROM hits 
WHERE URL LIKE '%google%'
ORDER BY EventTime
LIMIT 10
SETTINGS
  use_query_condition_cache = 0,
  use_skip_indexes_on_data_read = 1,
  use_skip_indexes_for_top_k = 1,
  use_top_k_dynamic_filtering = 1;
</code></pre>

Now the fastest of three runs finished in 0.033 seconds:

```shell
10 rows in set. Elapsed: 0.034 sec. Processed 7.66 million rows, 515.98 MB (227.36 million rows/s., 15.32 GB/s.)
Peak memory usage: 51.30 MiB.

10 rows in set. Elapsed: 0.034 sec. Processed 7.59 million rows, 509.67 MB (224.45 million rows/s., 15.08 GB/s.)
Peak memory usage: 51.29 MiB.

10 rows in set. Elapsed: 0.033 sec. Processed 7.67 million rows, 520.58 MB (234.95 million rows/s., 15.96 GB/s.)
Peak memory usage: 47.28 MiB.
```

This is roughly **10× faster than before**. Instead of processing the table’s full **~100 million rows**, ClickHouse processed only about **7 million rows**, which reduced the amount of data read from roughly **9.42 GB** to about **520.58 MB**.

As in the previous example, this I/O benefit grows with table size: when tables run into billions or trillions of rows (and especially when the cache is cold), dynamically skipping granules that cannot improve the current Top-N result becomes increasingly impactful.

As explained above, ClickHouse achieves this by continuously maintaining the current Top-N threshold *during* query execution and using the minmax data skipping index to dynamically skip granules whose values cannot improve the Top-10 result.

> **Community feedback**  
We have received [initial feedback](https://github.com/ClickHouse/ClickHouse/pull/89835#issuecomment-3566807610) from a community member, Michael Jarrett ([@EmeraldShift](https://github.com/EmeraldShift)), who has contributed across several recent issues and pull requests and tested these optimizations on very large production tables.<br/><br/>He observed that the skip index optimization is **remarkably fast, under 0.2 seconds on a table with 50 billion rows**, validating both the performance characteristics and the overall design in real-world settings. Further improvements are expected to make this even faster.

## Faster lazy reading with join-style execution model

### Contributed by Nikolai Kochetov

In the previous section, we introduced [**lazy reading**](https://clickhouse.com/blog/clickhouse-gets-lazier-and-faster-introducing-lazy-materialization) as one of the low-level optimizations that helps accelerate Top-N queries by deferring reads of non-ordering columns until the final result set is known.

In ClickHouse 25.12, lazy reading itself became significantly faster. The underlying execution model was redesigned, allowing lazy reading to scale efficiently to **much larger LIMIT values** and unlock additional performance gains.

###  Lazy reading before 25.12

When lazy reading was first introduced, it intentionally shipped with a conservative default.

The execution model worked as follows:

1. ClickHouse first read only the columns needed for sorting.

2. After the Top-N rows were identified, it fetched the remaining selected columns **row by row**.

This meant that if a query returned **N rows** and selected **M non-ordering columns**, ClickHouse performed roughly **N × M individual column reads**.

While this avoided reading unnecessary data, it also resulted in many small, scattered reads. For larger LIMIT values, the overhead of these per-row lookups could outweigh the benefits of deferred I/O.

For that reason, the [original lazy materialization blog post](https://clickhouse.com/blog/clickhouse-gets-lazier-and-faster-introducing-lazy-materialization) noted:

> Note: Lazy materialization is applied automatically for LIMIT N queries, but only up to a N threshold. This is controlled by the query_plan_max_limit_for_lazy_materialization setting (**default: 10**).

### What changed in 25.12

In ClickHouse 25.12, lazy reading switches to a **join-style execution model**, benefiting from the same vectorized, parallel execution model as ”normal” joins, making it efficient even for large LIMIT values.

Conceptually, the pipeline now looks like this:

1. Read the ORDER BY columns and determine the Top-N rows (unchanged).

2. Materialize a compact set of row identifiers.

3. Perform **a single batched lookup that joins those row identifiers back to the base table**.

The default value of [query_plan_max_limit_for_lazy_materialization](https://clickhouse.com/docs/operations/settings/settings#query_plan_max_limit_for_lazy_materialization) is now **10,000**. This limit exists because lazy reading still requires a sort of the lazily materialized columns, which can become noticeable at very large LIMIT values.

Lazy reading continues to work well with [read-in-order execution](https://clickhouse.com/blog/clickhouse-faster-queries-with-projections-and-primary-indexes#utilize-indexes-for-preventing-resorting-and-enabling-short-circuiting), which typically uses less memory than full sorting.

### Demonstration

We illustrate the effect using the same [anonymized web analytics dataset](https://clickhouse.com/docs/getting-started/example-datasets/metrica) as in the previous section. The data was [loaded](https://pastila.nl/?00239aa4/4acd8d1e7c548d73fb3681859739d0f4#Ho1IpeLvb21ELTi9hfr8rw==GCM) on an AWS m6i.8xlarge instance (32 cores, 128 GB RAM) backed by a gp3 EBS volume.

To stress lazy reading, we use a Top-N query with a **large LIMIT of 100,000 rows**.

For this experiment, we explicitly disable the lazy-materialization limit by setting [query_plan_max_limit_for_lazy_materialization](https://clickhouse.com/docs/operations/settings/settings#query_plan_max_limit_for_lazy_materialization) to `0`, allowing lazy reading to apply without restriction.

<pre><code type='click-ui' language='sql'>
SELECT * 
FROM hits 
ORDER BY EventTime 
LIMIT 100000
FORMAT Hash
SETTINGS query_plan_max_limit_for_lazy_materialization = 0;
</code></pre>

#### Lazy reading before 25.12

In ClickHouse 25.11, lazy reading still materialized remaining columns row by row.

For this query, that meant fetching **104 non-order columns** for each of the **100,000 Top-N rows** –> around **10 million individual column lookups**.

The fastest of three runs completed in **38.7 seconds**:

```shell
100000 rows in set. Elapsed: 38.702 sec. Processed 100.00 million rows, 1.20 GB (2.58 million rows/s., 31.01 MB/s.)
Peak memory usage: 981.92 MiB.

100000 rows in set. Elapsed: 34.193 sec. Processed 100.00 million rows, 1.20 GB (2.92 million rows/s., 35.09 MB/s.)
Peak memory usage: 977.59 MiB.

100000 rows in set. Elapsed: 34.152 sec. Processed 100.00 million rows, 1.20 GB (2.93 million rows/s., 35.14 MB/s.)
Peak memory usage: 953.25 MiB.
```

As discussed earlier, for large Top-N limits (such as the LIMIT 100,000 in this example), the overhead of per-row lazy materialization can outweigh the benefits of deferred I/O.

We can illustrate this by disabling lazy reading entirely. By setting `query_plan_optimize_lazy_materialization = false`, ClickHouse falls back to eagerly reading all selected columns up front, avoiding the row-by-row lookup overhead.

With lazy reading disabled, the fastest of three runs completed in **7.014 seconds**:

```shell
100000 rows in set. Elapsed: 7.910 sec. Processed 100.00 million rows, 56.83 GB (12.64 million rows/s., 7.18 GB/s.)
Peak memory usage: 73.75 GiB.

100000 rows in set. Elapsed: 7.847 sec. Processed 100.00 million rows, 56.83 GB (12.74 million rows/s., 7.24 GB/s.)
Peak memory usage: 76.67 GiB.

100000 rows in set. Elapsed: 7.014 sec. Processed 100.00 million rows, 56.83 GB (14.26 million rows/s., 8.10 GB/s.)
Peak memory usage: 77.58 GiB.

```

This confirms why lazy reading originally shipped with a conservative default. For large LIMIT values, eager sequential reads can outperform row-by-row lazy materialization, even though they require reading significantly more data and consume substantially more memory.

#### Lazy reading in 25.12

Rather than fetching 104 columns for each row individually, ClickHouse now performs a single join-like pass to materialize all remaining columns for the Top-100,000 rows at once.

The fastest of three runs completed in **0.513 seconds**:

```shell
100000 rows in set. Elapsed: 0.513 sec. Processed 104.87 million rows, 3.56 GB (204.62 million rows/s., 6.94 GB/s.)
Peak memory usage: 967.19 MiB.

100000 rows in set. Elapsed: 0.524 sec. Processed 104.87 million rows, 3.56 GB (200.13 million rows/s., 6.79 GB/s.)
Peak memory usage: 951.09 MiB.

100000 rows in set. Elapsed: 0.520 sec. Processed 104.87 million rows, 3.56 GB (201.77 million rows/s., 6.85 GB/s.)
Peak memory usage: 953.08 MiB.
```

This is roughly **75 times faster than with the previous lazy reading mechanics** (and 14 times faster than without lazy reading).

#### Looking under the hood

We can confirm the change in lazy reading mechanics by inspecting the logical query plans for the same query using EXPLAIN PLAN:

<pre><code type='click-ui' language='sql'>
EXPLAIN PLAN
SELECT * 
FROM hits 
ORDER BY EventTime 
Limit 100000
SETTINGS query_plan_max_limit_for_lazy_materialization = 0;
</code></pre>

On 25.11, with the old mechanics for lazy reading the plan shows (read it from bottom to top) how ClickHouse plans to

1. Read data from the table ( only the ORDER BY column).  
2. Sort the data  
3. Apply the LIMIT  
4. **Then lazily fetch the remaining non-order columns row by row**.

```shell
LazilyRead
...
Limit
...
Sorting
...
ReadFromMergeTree (default.hits) 
```

On 25.12, the plan changes in a fundamental way.

The engine still:

1. Reads only the ORDER BY column.  
2. Sorts the data  
3. Applies the LIMIT

But instead of row-by-row materialization, it now introduces a **dedicated join step** to fetch the remaining columns in bulk from the base table:

```shell
JoinLazyColumnsStep
    ...
    Limit
    ...
    Sorting
    ...
    ReadFromMergeTree (default.hits) 
LazilyReadFromMergeTree
```

## Faster Joins with a more powerful join reordering algorithm


### Contributed by Alexander Gololobov

Top-N queries got faster. Lazy reading got faster. And, unsurprisingly for a ClickHouse release, joins got faster as well. ClickHouse 25.12 ships with a simple  (for now) but more powerful join reordering algorithm for INNER JOINs - DPsize - that explores more join orders than the existing greedy approach, often producing more efficient execution plans with less intermediate data.


### Join reordering primer

As a quick [reminder](https://clickhouse.com/blog/clickhouse-release-25-09#join-reordering), when multiple tables are joined, the join order does not affect correctness, but it can dramatically affect performance. Different join orders can produce vastly different amounts of intermediate data. Since ClickHouse’s default hash-based join algorithms build in-memory structures from one side of each join, choosing a join order that keeps build inputs small is critical for fast and efficient execution.


### DPsize join reordering algorithm

[DPsize](https://www.vldb.org/conf/2006/p930-moerkotte.pdf) is one of the classic join reordering algorithms and is used, often with variations, in many database systems, including PostgreSQL and IBM DB2.

It can be considered the classical [dynamic programming](https://en.wikipedia.org/wiki/Dynamic_programming) approach (hence the name DPsize) that constructs the optimal join order based on a given cost model in a bottom-up fashion:



* It starts with the simplest plans: single tables.
* It then builds optimal plans for pairs of tables.
* Then for three tables, four tables, and so on.
* At each step, it constructs larger join plans by combining two already-optimal smaller subplans.

You can think of it as gradually assembling the final join tree, increasing its size step by step while always reusing the cheapest plans found so far.

The trade-off is optimize-cost:



* DPsize explores many more possible join orders than greedy algorithms.
* In practice, this means DPsize is more powerful, but also more optimizer-time expensive, than greedy reordering.

This is why many systems historically default to greedy join ordering and only use DP-based approaches selectively.


### DPsize in ClickHouse 25.12

In ClickHouse 25.12, DPsize is introduced as an additional option for INNER JOIN reordering: a simple but more expressive algorithm that explores a richer set of join orders and can produce better execution plans for more complex join graphs.

A new experimental setting controls what algorithms are used in which order, e.g. [query_plan_optimize_join_order_algorithm](https://clickhouse.com/docs/operations/settings/settings#query_plan_optimize_join_order_algorithm)='dpsize,greedy' means that DPsize is tried first with fallback to greedy.


### Demonstration

Let’s see DPsize in action using the classic [TPC-H join benchmark](https://clickhouse.com/docs/getting-started/example-datasets/tpch).

We reuse the same [eight TPC-H tables (extended with column statistics)](https://pastila.nl/?01031010/7475d7ba575a41d9fd86eaaff97cb201#SGYcmaof4DoQzewNH3tBKA==) from an [earlier release post](https://clickhouse.com/blog/clickhouse-release-25-09#join-reordering) that introduced global join reordering. The data is [loaded](https://pastila.nl/?003e78ba/abfe6ec788901e3755ade78c516878c5#/d8OIS+RA2PIkS+N9Sw9bQ==) with a scale factor of 100, and the benchmark is run on an AWS EC2 m6i.8xlarge instance (32 vCPUs, 128 GiB RAM).

Note that we run all join queries with these settings, to ensure that join reordering and statistics-based optimization are fully enabled: 

<pre><code type='click-ui' language='sql'>
SET allow_experimental_analyzer = 1;
SET query_plan_optimize_join_order_limit = 10;
SET allow_statistic_optimize = 1;
SET query_plan_join_swap_table='auto';
SET enable_parallel_replicas = 0;
</code></pre>



We use the same eight-table TPC-H join query that we previously used to introduce global join reordering. The query itself is unchanged; the only difference is the join reordering strategy used by the optimizer. We run it once with the existing greedy join reordering algorithm, and once with DPsize, by setting:



* query_plan_optimize_join_order_algorithm = 'greedy'
* query_plan_optimize_join_order_algorithm = 'dpsize'

This allows us to directly compare the execution plans produced by the two algorithms on an identical workload.

<pre><code type='click-ui' language='sql'>
SELECT
  n_name,
  sum(l_extendedprice * (1 - l_discount)) AS revenue
FROM
  customer,
  orders,
  lineitem,
  supplier,
  nation,
  region
WHERE
  c_custkey = o_custkey
AND l_orderkey = o_orderkey
AND l_suppkey = s_suppkey
AND c_nationkey = s_nationkey
AND s_nationkey = n_nationkey
AND n_regionkey = r_regionkey
AND r_name = 'ASIA'
AND o_orderdate >= DATE '1994-01-01'
AND o_orderdate < DATE '1994-01-01' + INTERVAL '1' year
GROUP BY
  n_name
ORDER BY
  revenue DESC
SETTINGS
    query_plan_optimize_join_order_algorithm = 'greedy';
    -- query_plan_optimize_join_order_algorithm = 'dpsize';
</code></pre>


When we first run the query with both algorithms using EXPLAIN, we can see the join order chosen by each optimizer.

[Greedy join order](https://pastila.nl/?0082792b/6bbdf64225cd3dc79264714c7f155848#yeZ5T0t2zOb59pds62abfg==GCM):
```shell
(((lineitem ⋈ (orders ⋈ customer)) ⋈ (supplier ⋈ (nation ⋈ region))))
```

The greedy algorithm proceeds as follows:



* orders is joined with customer
* nation is joined with region, and the result is joined with supplier
* The result of orders ⋈ customer is joined with lineitem
* Finally, the two larger intermediate results are joined together

This plan is built incrementally by repeatedly extending the current plan with what looks like the cheapest next join at each step.


[DPsize join order](https://pastila.nl/?0075036f/88a89e565f83c1e1bfb972b2707db9a4#2Aev6EGEicUs2lm231DcNw==GCM):
```shell
((lineitem ⋈ orders) ⋈ (supplier ⋈ (nation ⋈ region))) ⋈ customer
```




With DPsize, the join order is different:



* lineitem is joined with orders.
* nation is joined with region, and the result is joined with supplier
* These two intermediate results are then joined together
* customer is joined last 


By considering larger combinations of tables, DPsize is able to delay joining customer until the end, resulting in a different, and, as we will see below,  in this case more efficient execution plan.

When we execute the query with both join reordering algorithms and measure three consecutive runs for each, the difference becomes visible in actual runtime. With identical data, the plan produced by DPsize consistently runs faster than the greedy plan. Across the three runs, the DPsize plan is about 4.7% faster than the greedy one.

Three consecutive Greedy runs:
```shell
5 rows in set. Elapsed: 2.975 sec. Processed 638.85 million rows, 14.76 GB (214.76 million rows/s., 4.96 GB/s.)
Peak memory usage: 3.65 GiB.

5 rows in set. Elapsed: 2.718 sec. Processed 638.85 million rows, 14.76 GB (235.06 million rows/s., 5.43 GB/s.)
Peak memory usage: 3.64 GiB.

5 rows in set. Elapsed: 2.702 sec. Processed 638.85 million rows, 14.76 GB (236.44 million rows/s., 5.46 GB/s.)
Peak memory usage: 3.65 GiB.
```

Three consecutive DPsize runs:
```shell
5 rows in set. Elapsed: 2.667 sec. Processed 638.85 million rows, 14.76 GB (239.53 million rows/s., 5.53 GB/s.)
Peak memory usage: 3.83 GiB.

5 rows in set. Elapsed: 2.658 sec. Processed 638.85 million rows, 14.76 GB (240.37 million rows/s., 5.55 GB/s.)
Peak memory usage: 3.84 GiB.

5 rows in set. Elapsed: 2.672 sec. Processed 638.85 million rows, 14.76 GB (239.08 million rows/s., 5.52 GB/s.)
Peak memory usage: 3.83 GiB.
```

While this is a modest improvement for this particular eight-table query, the impact of join reordering grows with **query complexity**. For queries that join **more tables**, involve **larger size differences between relations**, or have **less obvious join orders**, exploring a richer set of join orders can lead to significantly larger performance gains.





## Text index is beta

### Contributed by Anton Popov, Elmi Ahmadov, Jimmy Aguilar Mena

Three months after [version 3 of the text index was introduced in ClickHouse 25.9](https://clickhouse.com/blog/clickhouse-release-25-09#a-new-text-index), in ClickHouse 25.12, it has moved to beta status.

Let’s remind ourselves how it works with help from the [Hacker News example dataset](https://clickhouse.com/docs/getting-started/example-datasets/hacker-news). We’ll first create a table, and one change since 25.9 is that [we need to specify a `tokenizer`](https://clickhouse.com/docs/engines/table-engines/mergetree-family/textindexes#creating-a-text-index) - we can’t use the value `default` anymore.

<pre><code type='click-ui' language='sql'>
SET enable_full_text_index=1;

CREATE TABLE hackernews
(
    `id` Int64,
    `deleted` Int64,
    `type` String,
    `by` String,
    `time` DateTime64(9),
    `text` String,
    `dead` Int64,
    `parent` Int64,
    `poll` Int64,
    `kids` Array(Int64),
    `url` String,
    `score` Int64,
    `title` String,
    `parts` Array(Int64),
    `descendants` Int64,
    INDEX inv_idx(text)
    TYPE text(tokenizer = 'splitByNonAlpha')
    GRANULARITY 128
)
ORDER BY time;
</code></pre>

Valid values for the tokenizer, which you can also find in the docs, are as follows:

```shell
tokenizer = splitByNonAlpha
                                           | splitByString[(S)]
                                           | ngrams[(N)]
                                           | sparseGrams[(min_length[, max_length[, min_cutoff_length]])]
                                           | array
```

We can write queries against the `text` field to find specific terms using the `hasToken`, `hasAllTokens`, and `hasAnyTokens` functions.

The following query finds the users posting about OpenAI:

<pre><code type='click-ui' language='sql'>
SELECT by, count()
FROM hackernews
WHERE hasToken(text, 'OpenAI')
GROUP BY ALL
ORDER BY count() DESC
LIMIT 10;
</code></pre>

```shell
┌─by──────────────┬─count()─┐
│ minimaxir       │      48 │
│ sillysaurusx    │      43 │
│ gdb             │      40 │
│ thejash         │      24 │
│ YeGoblynQueenne │      23 │
│ nl              │      20 │
│ Voloskaya       │      19 │
│ p1esk           │      18 │
│ rvz             │      17 │
│ visarga         │      16 │
└─────────────────┴─────────┘
```

Our next query finds users posting about OpenAI and Google in the same post:

<pre><code type='click-ui' language='sql'>
SELECT by, count()
FROM hackernews
WHERE hasAllTokens(text, ['OpenAI', 'Google'])
GROUP BY ALL
ORDER BY count() DESC
LIMIT 10;
</code></pre>

```shell
┌─by──────────────┬─count()─┐
│ thejash         │      17 │
│ boulos          │       8 │
│ p1esk           │       6 │
│ nl              │       5 │
│ colah3          │       5 │
│ sillysaurusx    │       5 │
│ Voloskaya       │       4 │
│ YeGoblynQueenne │       4 │
│ visarga         │       4 │
│ rvz             │       4 │
└─────────────────┴─────────┘
```

And our final query finds the users who posted about OpenAI or Google:

<pre><code type='click-ui' language='sql'>
SELECT by, count()
FROM hackernews
WHERE hasAnyTokens(text, ['OpenAI', 'Google'])
GROUP BY ALL
ORDER BY count() DESC
LIMIT 10;
</code></pre>

```shell
┌─by───────────┬─count()─┐
│ ocdtrekkie   │    2506 │
│ nostrademons │    2317 │
│ pjmlp        │    1948 │
│ tptacek      │    1626 │
│ ChuckMcM     │    1523 │
│ dragonwriter │    1417 │
│ mtgx         │    1189 │
│ dredmorbius  │    1142 │
│ jrockway     │    1121 │
│ Animats      │    1103 │
└──────────────┴─────────┘
```

We can also use other clauses and functions to search text, but the text index will only be used if complete tokens can be extracted from the search term.

For example, the following query won’t use the full-text search index:

<pre><code type='click-ui' language='sql'>
SELECT by, count()
FROM hackernews
WHERE text LIKE '%OpenAI%'
GROUP BY ALL
ORDER BY count() DESC
LIMIT 10;
</code></pre>

```shell
┌─by──────────────┬─count()─┐
│ minimaxir       │      49 │
│ sillysaurusx    │      45 │
│ gdb             │      40 │
│ thejash         │      24 │
│ YeGoblynQueenne │      23 │
│ nl              │      20 │
│ Voloskaya       │      19 │
│ p1esk           │      18 │
│ rvz             │      17 │
│ visarga         │      16 │
└─────────────────┴─────────┘

10 rows in set. Elapsed: 2.161 sec. Processed 28.03 million rows, 9.42 GB (12.97 million rows/s., 4.36 GB/s.)
Peak memory usage: 171.12 MiB.
```

If we want this query to use the full-text index, we need to add spaces around `OpenAI` so that the query engine can extract complete tokens from the search term.

<pre><code type='click-ui' language='sql'>
SELECT by, count()
FROM hackernews
WHERE text LIKE '% OpenAI %'
GROUP BY ALL
ORDER BY count() DESC
LIMIT 10;
</code></pre>

```shell
┌─by──────────────┬─count()─┐
│ minimaxir       │      33 │
│ sillysaurusx    │      31 │
│ gdb             │      19 │
│ thejash         │      17 │
│ YeGoblynQueenne │      16 │
│ rvz             │      13 │
│ visarga         │      13 │
│ Voloskaya       │      13 │
│ ryanmercer      │      11 │
│ backpropaganda  │      11 │
└─────────────────┴─────────┘

10 rows in set. Elapsed: 0.529 sec. Processed 7.39 million rows, 2.61 GB (13.95 million rows/s., 4.92 GB/s.)
Peak memory usage: 171.45 MiB.
```

## dictGetKeys

### Contributed by Nihal Z. Miaji

ClickHouse supports various dictionaries, a special type of in-memory table that utilizes specialized data structures for fast key-value lookups.

The following dictionary allows us to look up the borough or zone for a given Location ID. It is populated from a CSV file of taxi zones in New York.

<pre><code type='click-ui' language='sql'>
CREATE DICTIONARY taxi_zone_dictionary
(
  LocationID UInt16 DEFAULT 0, -- key
  Borough String,              -- attributes
  Zone String,
  service_zone String
)
PRIMARY KEY LocationID
SOURCE(HTTP(URL 'https://datasets-documentation.s3.eu-west-3.amazonaws.com/nyc-taxi/taxi_zone_lookup.csv' FORMAT 'CSVWithNames'))
LIFETIME(MIN 0 MAX 0) 
LAYOUT(HASHED_ARRAY());
</code></pre>

We can use the `dictGet` function to find the borough and zone where `LocationId=240`:

<pre><code type='click-ui' language='sql'>
SELECT dictGet('taxi_zone_dictionary', ('Borough', 'Zone'), 240);
</code></pre>


```shell
┌─dictGet('taxi_z⋯Zone'), '240')─┐
│ {                             ↴│
│↳  "Borough": "Bronx",         ↴│
│↳  "Zone": "Van Cortlandt Park"↴│
│↳}                              │
└────────────────────────────────┘
```

As of ClickHouse 25.12, we can retrieve the keys for a given attribute using the `dictGetKeys` function. The following query returns the `LocationID`s for the Bronx:

<pre><code type='click-ui' language='sql'>
SELECT dictGetKeys('taxi_zone_dictionary', 'Borough', 'Bronx')
</code></pre>

```shell
Row 1:
──────
dictGetKeys(⋯', 'Bronx'): [81,46,18,254,183,185,147,58,31,167,119,3,51,59,259,212,47,174,199,60,213,200,169,248,184,235,242,126,241,168,136,208,78,20,94,250,32,182,220,247,159,69,240]
```

This function automatically creates a per-query cache, allowing bulk lookups to be fast. The size of the cache is controlled by the [`max_reverse_dictionary_lookup_cache_size_bytes`](https://clickhouse.com/docs/operations/settings/settings#max_reverse_dictionary_lookup_cache_size_bytes) setting.

## Non-constant IN

### Contributed by Yarik Briukhovetskyi

As of ClickHouse 25.12, we can now use non-constant lists as part of the `IN` clause of a query. Let’s have a look at how this works with help from the [New York taxis dataset](https://clickhouse.com/docs/tutorial).

The following query returns the drop-offs to LaGuardia when the payment type was cash and to JFK for other payment types.

<pre><code type='click-ui' language='sql'>
SELECT dropoff_nyct2010_gid, payment_type, count()
FROM trips
WHERE dropoff_nyct2010_gid IN (payment_type = 'CSH' ? [138] : [132])
GROUP BY ALL;
</code></pre>

If we run this query before 25.12, we’ll get the following error:

```shell
Received exception:
Code: 1. DB::Exception: Function 'in' is supported only if second argument is constant or table expression. (UNSUPPORTED_METHOD)
```

If we run it with 25.12, we’ll see the following output:

```shell
┌─dropoff_nyct2010_gid─┬─payment_type─┬─count()─┐
│                  138 │ CSH          │   10356 │
│                  132 │ CRE          │   10824 │
│                  132 │ NOC          │      80 │
│                  132 │ DIS          │      39 │
└──────────────────────┴──────────────┴─────────┘
```

## HMAC 

### Contributed by Mikhail F. Shiryaev.

The 25.12 also sees the introduction of an HMAC function for message authentication using a (shared) secret key. This makes it possible to use the ClickHouse server as a webhook and validate message authenticity on `INSERT`.

To use ClickHouse like this, we need to allow reading of HTTP headers from incoming requests by configuring the following setting:

<pre><code type='click-ui' language='yaml'>
profiles:
  default:
    allow_get_client_http_header: 1
</code></pre>

We’ll then create two tables:

* `webhook_staging,` which will store all incoming payloads  
* `webhook_prod,` which will only store payloads where the signature is valid.

The staging table looks like this:

<pre><code type='click-ui' language='sql'>
CREATE TABLE webhook_staging (
    received_at DateTime DEFAULT now(),
    raw_payload String,
    signature String DEFAULT getClientHTTPHeader('X-Hub-Signature-256')
) ENGINE = MergeTree()
ORDER BY received_at;
</code></pre>

The production table is like this:

<pre><code type='click-ui' language='sql'>
CREATE TABLE webhook_prod (
    received_at DateTime,
    event_type String,
    payload String
) ENGINE = MergeTree()
ORDER BY received_at;
</code></pre>

And then we’ll have a materialized view that reads incoming rows to the staging table and forwards them to the production table if the signature is valid:

<pre><code type='click-ui' language='sql'>
CREATE MATERIALIZED VIEW webhook_validator TO webhook_prod AS
SELECT 
    received_at,
    raw_payload::JSON.event as event_type,
    raw_payload as payload
FROM webhook_staging
WHERE signature = 'sha256=' || lower(hex(HMAC('SHA256', raw_payload, 'my_secret_key')));
</code></pre>

We can simulate a webhook request to ClickHouse using the wrong key:

<pre><code type='click-ui' language='shell'>
PAYLOAD='{"event":"user_signup","user_id":789}'
SIGNATURE=$(echo -n "$PAYLOAD" | openssl dgst -sha256 -hmac "my_secret_key2" | cut -d' ' -f2)

curl -X POST "http://localhost:8123/?query=INSERT%20INTO%20webhook_staging%20(raw_payload)%20FORMAT%20RawBLOB" 
  -H "X-Hub-Signature-256: sha256=$SIGNATURE" 
  -d "$PAYLOAD"
</code></pre>

If we query the `webhook_staging` table, we’ll see the following entry:

```shell
Row 1:
──────
received_at: 2026-01-06 13:51:53
raw_payload: {"event":"user_signup","user_id":789}
signature:   sha256=8184a43ddb115fba57877a6e3f85b48ae60d678dbcf44407130e467b4106cd3b
```

But `webhook_logs` is empty! We can run a variation of the materialized view’s query to show that the signature was invalid:

<pre><code type='click-ui' language='sql'>
SELECT
    received_at,
    raw_payload::JSON.event as event_type,
    raw_payload as payload,
    signature,
    'sha256=' || lower(hex(HMAC('SHA256', raw_payload, 'my_secret_key')))
FROM webhook_staging
</code></pre>

```shell
Row 1:
──────
received_at:              2026-01-06 13:51:53
event_type:               user_signup
payload:                  {"event":"user_signup","user_id":789}
signature:                sha256=8184a43ddb115fba57877a6e3f85b48ae60d678dbcf44407130e467b4106cd3b
concat('sha2⋯et_key')))): sha256=1f0480fde689cf4080e3b621f6c127df41506efabbf71767539f68b809a90203
```

We can see that the two signatures don’t match. If we submit a request using the correct key, the record will be inserted into the `webhook_logs` table.
