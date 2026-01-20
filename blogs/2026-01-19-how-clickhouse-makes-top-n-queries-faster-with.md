---
title: "How ClickHouse makes Top-N queries faster with granule-level data skipping"
date: "2026-01-19T10:29:01.538Z"
author: "Tom Schreiber"
category: "Engineering"
excerpt: "A deep dive into how ClickHouse uses data-skipping metadata to turn Top-N queries into a pruning problem, cutting I/O and speeding up queries at scale."
---

# How ClickHouse makes Top-N queries faster with granule-level data skipping


> **TL;DR**<br/><br/>ClickHouse treats Top-N as a first-class query pattern. By using min/max metadata from data-skipping indexes, it can skip entire granules before reading any data. In our examples this yields 5–10× faster Top-N queries and 10–100× less data read, especially effective on large tables and cold cache.

**Prefer a quick walkthrough?**<br/>
Watch Mark explain how ClickHouse optimizes Top-N queries:

<iframe width="768" height="432" src="https://www.youtube.com/embed/SyayPSrsAhI?si=6xrsWPFtFlOaz5q7" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

<br/>

## Optimizing common query patterns

ClickHouse’s performance [leadership](https://benchmark.clickhouse.com/) comes from systematically identifying **common analytical query patterns** and aggressively optimizing **each of them** at the engine level.

Top-N queries are one of the most important of these patterns.

They appear frequently in real analytical workloads, dashboards, monitoring queries, ranking reports, and exploratory analysis. 

“Show me the latest events.”

“Who are the top customers by revenue?”

“What are the most expensive orders today?”

<pre>
<code type='click-ui' language='sql' show_line_numbers='false'>
SELECT *
FROM orders
ORDER BY total_amount DESC
LIMIT 3;
</code>
</pre>
Over time, the engine has accumulated a large number of low-level optimizations specifically designed to make Top-N queries fast: streaming execution, read-in-order, lazy reading, and more.

This blog focuses on one additional optimization in that toolbox: a new way to **use data skipping indexes to eliminate work before any data is read**, further accelerating Top-N queries as data sizes grow.


## How ClickHouse already optimizes Top-N queries

ClickHouse already applies several optimizations to run Top-N queries efficiently and fast:

1. [Streaming](https://clickhouse.com/docs/sql-reference/statements/select#implementation-details) Top-N (bounded memory):   
   ClickHouse doesn’t sort all rows at once. Instead, it streams data and keeps only the current Top-N candidates, so memory usage stays proportional to N rather than to the table size.

2. [Read in order](https://clickhouse.com/blog/clickhouse-faster-queries-with-projections-and-primary-indexes#utilize-indexes-for-preventing-resorting-and-enabling-short-circuiting) (avoid sorting completely):  
   If the data on disk is already ordered by the ORDER BY column(s), or can be read in that order via a [projection](https://clickhouse.com/docs/sql-reference/statements/alter/projection), ClickHouse can avoid sorting and simply read the first rows in order.

3. [Lazy reading](https://clickhouse.com/blog/clickhouse-gets-lazier-and-faster-introducing-lazy-materialization) (defer reading non-order columns):  
   Even when the query selects many columns, ClickHouse can first determine the Top-N rows using only the columns needed for ordering, and only then read the remaining columns for those rows. This reduces I/O dramatically.

These optimizations are **orthogonal** to each other: they address different aspects of Top-N query execution and can be applied independently or in combination within a single query.

Despite these optimizations, Top-N queries still require scanning all relevant [granules](https://clickhouse.com/docs/guides/best-practices/sparse-primary-indexes#data-is-organized-into-granules-for-parallel-data-processing), even when only a handful of rows are ultimately returned.

## The missing piece: skipping data before it is ever read

ClickHouse applies additional, orthogonal optimizations for Top-N queries by using [data skipping indexes](https://clickhouse.com/docs/optimize/skipping-indexes/examples) for static or dynamic Top-N filtering, **significantly reducing the number of rows that need to be processed**.

The rest of this post shows how this works in practice, starting with the simplest case.


## Static Top-N filtering (no predicates) 

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

### Benchmark: static Top-N

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

## Dynamic Top-N threshold filtering (with predicates)

So far, we’ve looked at Top-N queries without predicates, where granules can be preselected using static min/max metadata on the ORDER BY column.

When a Top-N query also includes predicates, the data skipping becomes *dynamic*.

As the query executes, ClickHouse continuously maintains the current Top-N result set. **The current N-th value effectively acts as a dynamic threshold.**

This mechanism builds on [streaming for secondary indices](https://clickhouse.com/blog/clickhouse-release-25-09#streaming-for-secondary-indices), introduced in ClickHouse 25.9: Instead of evaluating data skipping indexes upfront, ClickHouse interleaves data skipping index checks with data reads. As soon as a granule becomes eligible for reading (after [primary index analysis](https://clickhouse.com/docs/primary-indexes) for the predicate evaluation), its corresponding minmax data skipping index entry is consulted.

At that point, the current Top-N threshold is compared against the granule’s min/max metadata. If the granule cannot possibly contain values that would improve the Top-N result set, it is skipped immediately and never read.

As execution progresses and better Top-N candidates are found, the threshold tightens further, allowing ClickHouse to prune an increasing number of granules dynamically during query execution. Because the query stops once the Top-N result is complete, tighter thresholds allow ClickHouse to stop reading and skipping granules earlier.

### Benchmark: dynamic Top-N

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

## Production-scale validation

These mechanics have also been validated on very large production tables.

In [early testing](https://github.com/ClickHouse/ClickHouse/pull/89835#issuecomment-3566807610) on a table with **50 billion rows**, Top-N queries using skip index filtering completed in under **0.2 seconds**, confirming that granule-level pruning remains effective even at extreme scale. Further improvements are expected to make this even faster.


## Turning Top-N into a metadata problem

With data skipping–based Top-N filtering, ClickHouse turns Top-N queries into a **metadata-driven pruning problem**.

By comparing the current Top-N threshold against granule-level min/max metadata, ClickHouse can skip large portions of a table without reading a single row. For simple Top-N queries, this pruning happens up front. For queries with predicates, it happens dynamically as execution progresses and the threshold tightens.

This kind of metadata-driven pruning is **especially powerful in modern architectures with object storage or disaggregated compute**, where avoiding unnecessary reads saves not just CPU, but also network I/O and latency.

In our examples, this approach sped up Top-N queries by **5× to 10×** and reduced the amount of data read by **one to two orders of magnitude**, purely by skipping granules that could not improve the result.

Crucially, this optimization composes with existing Top-N techniques like streaming execution, read-in-order, and lazy reading. Each optimization addresses a different bottleneck, and together they allow ClickHouse to scale Top-N queries from millions to billions of rows efficiently.

For users, this means a familiar query pattern `ORDER BY … LIMIT N` now benefits from increasingly aggressive pruning as data grows. By treating common query patterns as problems that can often be solved *before* touching the data at all.

