---
title: "ClickHouse Release 26.3"
date: "2026-04-07T16:13:19.556Z"
category: "Engineering"
excerpt: "ClickHouse 26.3 is here! In this release, async inserts are turned on by default, we've got more JOIN reordering, materialized CTES have arrived, and more!"
---

# ClickHouse Release 26.3

Another month goes by, which means it’s time for another release! 

<p>ClickHouse 26.3 contains 27 new features &#127799; 40 performance optimizations &#128007; 202 bug fixes &#128029;</p>

This release sees async inserts turned on by default, JOIN reordering for ANTI, SEMI, FULL, materialized CTES, and more!

## New contributors

A special welcome to all the new contributors in 26.3! The growth of ClickHouse's community is humbling, and we are always grateful for the contributions that have made ClickHouse so popular.

Below are the names of the new contributors:

*Alex Soffronow-Pagonidis, Alexey Smirnov, Amy Chen, Andrii Beskomornyi, Artem Brustovetskii, Artem Kytkin, Caio Ishizaka Costa, Cursor Agent, Daniel Q, Den Kalantaevskii, Desel72, Enric Calabuig, Finn, Fisnik Kastrati, François Martin, Herman Schaaf, JIaQi Tang, Maksim Kozlov, Nazarii Piontko, NeedmeFordev, Onyx2406, Riyane El Qoqui, Semen Checherinda, Vasily Chekalkin, Victor Zhou, Vikash, Yash, lioshik, martinfrancois, mcalfin, paf91, spider-yamet, tanner-bruce, vyalamar, wangzhibo*

Hint: if you’re curious how we generate this list… [here](https://gist.github.com/gingerwizard/5a9a87a39ba93b422d8640d811e269e9).

<iframe width="768" height="432" src="https://www.youtube.com/embed/\_bY0ucNB1lQ?si=m\_mhFlrMP1nhzHZQ" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen\></iframe\>

You can also [view the slides from the presentation](https://presentations.clickhouse.com/2026-release-26.3/).

## Materialized CTE

### Contributed by Dmitry Novik

The 26.3 release introduces the `MATERIALIZED` clause, which means that CTEs (subqueries in the WITH clause) will only be evaluated only once and stored in temporary tables.

Let’s have a look at how to use it with the [UK property prices dataset](https://clickhouse.com/docs/getting-started/example-datasets/uk-price-paid). The following query returns the most expensive properties alongside the average price of properties sold in that county that year and over all time.

<pre><code type='click-ui' language='sql'>
WITH county_year_avg AS MATERIALIZED
    (
        SELECT county, toYear(date) AS year, avg(price) AS avg_price
        FROM uk_price_paid3
        GROUP BY county,year
    )
SELECT p.price, p.addr1, p.town,
    p.county,
    toYear(p.date) AS year,
    round(cya.avg_price) AS countyYear,
    round(ca.avg_price) AS countyAllTime
FROM uk_price_paid3 AS p
INNER JOIN county_year_avg AS cya 
ON (p.county = cya.county) AND (toYear(p.date) = cya.year)
INNER JOIN
(
    SELECT county, avg(avg_price) AS avg_price
    FROM county_year_avg
    GROUP BY county
) AS ca ON p.county = ca.county
ORDER BY p.price DESC
LIMIT 10;
</code></pre>

The CTE will only be materialized if the following setting is configured:

<pre><code type='click-ui' language='sql'>
SET enable_materialized_cte=1;
</code></pre>

The results of running this query are shown below:

```shell
┌─────price─┬─street────────────┬─p.county───────┬─year─┬─ctyYear─┬─ctyAllTime─┐
│ 900000000 │ VICTORIA ROAD     │ KENT           │ 2021 │  457070 │     251980 │
│ 594300000 │ BAKER STREET      │ GREATER LONDON │ 2017 │  797029 │     466002 │
│ 569200000 │ STANHOPE ROW      │ GREATER LONDON │ 2018 │  821394 │     466002 │
│ 542540820 │ FORTESS ROAD      │ GREATER LONDON │ 2019 │  837867 │     466002 │
│ 523000000 │ NINE ELMS LANE    │ GREATER LONDON │ 2021 │  800579 │     466002 │
│ 494400000 │ NEWMARKET LANE    │ WEST YORKSHIRE │ 2019 │  244610 │     154516 │
│ 494400000 │ NEWMARKET LANE    │ WEST YORKSHIRE │ 2019 │  244610 │     154516 │
│ 480000000 │ SUTHERLAND AVENUE │ WEST MIDLANDS  │ 2022 │  343339 │     170087 │
│ 480000000 │ COOPER STREET     │ WEST MIDLANDS  │ 2022 │  343339 │     170087 │
│ 480000000 │ SUTHERLAND AVENUE │ WEST MIDLANDS  │ 2022 │  343339 │     170087 │
└───────────┴───────────────────┴────────────────┴──────┴─────────┴────────────┘
```

And the running time when the CTE is not materialized:

```shell
10 rows in set. Elapsed: 2.590 sec. Processed 91.36 million rows, 892.55 MB (35.27 million rows/s., 344.56 MB/s.)
Peak memory usage: 1.50 GiB.

10 rows in set. Elapsed: 2.707 sec. Processed 91.36 million rows, 892.55 MB (33.75 million rows/s., 329.71 MB/s.)
Peak memory usage: 1.50 GiB.

10 rows in set. Elapsed: 2.636 sec. Processed 91.36 million rows, 892.55 MB (34.66 million rows/s., 338.59 MB/s.)
Peak memory usage: 1.50 GiB.
```

And when it is materialized:

```shell
10 rows in set. Elapsed: 1.243 sec. Processed 60.91 million rows, 679.63 MB (49.02 million rows/s., 546.98 MB/s.)
Peak memory usage: 87.40 MiB.

10 rows in set. Elapsed: 1.219 sec. Processed 60.91 million rows, 679.63 MB (49.98 million rows/s., 557.68 MB/s.)
Peak memory usage: 88.97 MiB.

10 rows in set. Elapsed: 1.229 sec. Processed 60.91 million rows, 679.63 MB (49.58 million rows/s., 553.17 MB/s.)
Peak memory usage: 87.43 MiB.
```

The materialized version is a little over twice as fast. This dataset is reasonably small at 30 million records, so we’d see even more of an improvement at bigger scale.

## Pretty EXPLAIN

### Contributed by Kirill Kopnev

The 26.3 release also introduces new settings when using the `EXPLAIN` clause:

* `pretty=1` - tree-style indented output.  
* `compact=1` - collapses Expression steps.

If we prefix the query from the previous section with:

<pre><code type='click-ui' language='sql'>
EXPLAIN indexes=1, pretty=1, compact=1
</code></pre>

We see the following output for the not materialized CTE:

![2026-03-30_12-38-17.png](https://clickhouse.com/uploads/2026_03_30_12_38_17_9f6175afa7.png)


And the following output for the materialized one:

![2026-03-30_12-38-05.png](https://clickhouse.com/uploads/2026_03_30_12_38_05_15e7da3a8d.png)

## Natural sorting

### Contributed by Nazarii Piontko

The `naturalSortKey` function enables human-friendly sorting. 

For example, if we wanted to work out when Geospatial functions were added to ClickHouse, we could write the following query:

<pre><code type='click-ui' language='sql'>
SELECT introduced_in, count()
FROM system.functions
WHERE categories LIKE '%Geo%'
GROUP BY ALL
ORDER BY introduced_in;
</code></pre>

```shell
┌─introduced_in─┬─count()─┐
│ 1.1.0         │       5 │
│ 20.1.0        │      10 │
│ 20.3.0        │       6 │
│ 20.4.0        │       1 │
│ 21.11.0       │       4 │
│ 21.4.0        │      24 │
│ 21.9.0        │      11 │
│ 22.1.0        │       3 │
│ 22.2.0        │       5 │
│ 22.6.0        │      15 │
│ 25.10.0       │       4 │
│ 25.11.0       │       6 │
│ 25.12.0       │       1 │
│ 25.6.0        │       2 │
│ 25.7.0        │       2 │
└───────────────┴─────────┘
```

In the normal sort order, `21.11.0` comes before `21.4.0` and `21.9.0`, which isn’t what we’d expect. We can use the new function to sort this data in the expected order:

<pre><code type='click-ui' language='sql'>
SELECT introduced_in, count()
FROM system.functions
WHERE categories LIKE '%Geo%'
GROUP BY ALL
ORDER BY naturalSortKey(introduced_in);
</code></pre>

```shell
┌─introduced_in─┬─count()─┐
│ 1.1.0         │       5 │
│ 20.1.0        │      10 │
│ 20.3.0        │       6 │
│ 20.4.0        │       1 │
│ 21.4.0        │      24 │
│ 21.9.0        │      11 │
│ 21.11.0       │       4 │
│ 22.1.0        │       3 │
│ 22.2.0        │       5 │
│ 22.6.0        │      15 │
│ 25.6.0        │       2 │
│ 25.7.0        │       2 │
│ 25.10.0       │       4 │
│ 25.11.0       │       6 │
│ 25.12.0       │       1 │
└───────────────┴─────────┘
```

## JSONExtract works with JSON type

### Contributed by Fisnik Kastrati

Before ClickHouse 26.3, the [`JSONExtract` function](https://clickhouse.com/docs/sql-reference/functions/json-functions#JSONExtract) could only be used to extract fields from JSON strings, as shown in the example below:

<pre><code type='click-ui' language='sql'>
WITH '{"ClickHouse":{"version":"26.3"}}' AS s
SELECT s, toTypeName(s), JSONExtractString(s, 'ClickHouse', 'version');
</code></pre>

```shell
┌─s─────────────────────────────────┬─toTypeName(s)─┬─JSONExtractS⋯ 'version')─┐
│ {"ClickHouse":{"version":"26.3"}} │ String        │ 26.3                     │
└───────────────────────────────────┴───────────────┴──────────────────────────┘
```

If you tried to use this function to extract fields from a JSON type, you’d get the following exception:

<pre><code type='click-ui' language='sql'>
WITH '{"ClickHouse":{"version":"26.3"}}'::JSON AS s
SELECT s, toTypeName(s), JSONExtractString(s, 'ClickHouse', 'version');
</code></pre>

```shell
Received exception:
Code: 43. DB::Exception: The first argument of function JSONExtractString should be a string containing JSON, illegal type: JSON: In scope WITH CAST('{"ClickHouse":{"version":"26.3"}}', 'JSON') AS s SELECT JSONExtractString(s, 'ClickHouse', 'version'). (ILLEGAL_TYPE_OF_ARGUMENT)
```

If you run the same query in 26.3, it will return the following output:

```shell
┌─s─────────────────────────────────┬─toTypeName(s)─┬─JSONExtractS⋯ 'version')─┐
│ {"ClickHouse":{"version":"26.3"}} │ JSON          │ 26.3                     │
└───────────────────────────────────┴───────────────┴──────────────────────────┘
```

## Vertical merge for TTL DELETE

### Contributed by murphy-4o

In ClickHouse, every INSERT creates a new [data part](https://clickhouse.com/docs/parts) sorted by the table’s sorting key. To keep inserts [fast](https://clickhouse.com/docs/concepts/why-clickhouse-is-so-fast#storage-layer-concurrent-inserts-are-isolated-from-each-other), additional data processing is [deferred](https://clickhouse.com/docs/concepts/why-clickhouse-is-so-fast#storage-layer-merge-time-computation) to [background part merges](https://clickhouse.com/docs/merges).

These merges run continuously, combining smaller parts into larger ones. In the process, ClickHouse not only improves data layout for [data skipping](https://clickhouse.com/docs/primary-indexes), but also performs maintenance work such as [replacing rows](https://clickhouse.com/blog/updates-in-clickhouse-1-purpose-built-engines), [deleting rows](https://clickhouse.com/docs/guides/developer/ttl), [updating rows](https://clickhouse.com/blog/updates-in-clickhouse-2-sql-style-updates), or [pre-aggregating data](https://clickhouse.com/docs/materialized-view/incremental-materialized-view).

To perform merges efficiently, ClickHouse automatically selects one of two merge algorithms based on factors such as table width, number of rows, and data size:


### **1. Horizontal merge**



* Reads and merges **all columns together**, block by block 

* Writes the merged data back to disk


### **2. Vertical merge**



* Reads and merges **only the sorting key columns first**

* Temporarily records the final row order for the remaining columns

* Then processes and writes **remaining columns one by one**

To see the difference more clearly, let’s look at how each merge strategy works in practice.


### Horizontal merge: simple and CPU efficient

Horizontal merging is straightforward. Since all parts are already sorted by the same key, ClickHouse performs a single linear merge pass, similar to [merge sort](https://en.wikipedia.org/wiki/Merge_sort):

* Parts are read sequentially 

* Rows are compared on the fly 

* A new merged part is written 


The animation below illustrates this using example data parts from a table with a sorting key `(town, street)`:


<video autoplay="1" muted="1" loop="1" controls="1">
  <source src="https://clickhouse.com/uploads/Blog_release_26_03_animation_01_f97b6f50a5.mp4" type="video/mp4" />
</video>

The animation shows the horizontal merge process in three steps:

**① Merge blocks**  
 
Data from multiple parts is read in blocks and merged in memory based on the sorting key in a single linear merge pass. For simplicity, the animation shows full parts instead of block-by-block processing.

**② Write blocks into a new part** 

The merged data is written into a new data part. Again, the animation shows this as a single step for simplicity.

**③ Deactivate old parts** 

Once the merge is complete, the original parts are marked as inactive and eventually removed.

> For wide tables (e.g. 100+ columns), this approach can be memory-intensive.

Because merges operate on row blocks, ClickHouse must load entire blocks of wide rows into memory. The wider the table, the more expensive this becomes.

To address this, ClickHouse uses an alternative merge strategy.


### Vertical merge: memory-optimized for wide tables

Vertical merging reduces memory usage by processing columns separately.

The animation below shows this for a table with a sorting key `(town, street)`. For simplicity, only one additional column `price` is shown; other columns are processed the same way.


<video autoplay="1" muted="1" loop="1" controls="1">
  <source src="https://clickhouse.com/uploads/Blog_release_26_03_animation_02_bc2e57e442.mp4" type="video/mp4" />
</video>

The animation shows the vertical merge process in five steps:

**① Merge sorting key columns first**  

Data from multiple parts is read block by block and merged in memory using the sorting key in a single linear pass. For simplicity, the animation shows full columns instead of several column-blocks.

**② Record row order and write key columns**  

The resulting final row order is temporarily stored, and the merged sorting key columns are written to the new data part.

**③ Merge next column by recorded row order** 

The remaining columns are processed one by one. For each column, data is read block by block from all parts and merged according to the previously recorded final row order. The animation illustrates this as a single step and for one column only.

**This combination of column-by-column and block-by-block processing is what makes vertical merges memory efficient.**

**④ Add column data to the new part** 

The merged column data is appended to the new data part after each column is processed.

**⑤ Deactivate old parts** 

Once all columns are processed, the original parts are marked as inactive and eventually removed.

> This merge strategy is more efficient for wide tables, where loading all columns at once would be memory-expensive.

In practice, ClickHouse uses vertical merges only when it is expected to be beneficial.


### When does ClickHouse use vertical merge?

With default settings, vertical merge becomes eligible when the to be merged parts contain at least [131,072 rows](https://clickhouse.com/docs/operations/settings/merge-tree-settings#vertical_merge_algorithm_min_rows_to_activate) in total or at least [11 non-primary-key columns](https://clickhouse.com/docs/operations/settings/merge-tree-settings#vertical_merge_algorithm_min_columns_to_activate).

In other words, for merges where the memory savings are expected to outweigh the extra bookkeeping, ClickHouse automatically switches to the more memory-efficient vertical merge algorithm.

This is often the case in TTL-driven workloads, where large volumes of data accumulate over time and are often stored in wide tables.


### Efficient TTL DELETEs for wide tables

In ClickHouse, you can define [TTL rules](https://clickhouse.com/docs/guides/developer/ttl) to [automatically delete table data](https://clickhouse.com/docs/engines/table-engines/mergetree-family/mergetree#mergetree-removing-expired-data) after a certain period.

This is particularly useful for data that naturally ages out, such as logs, events, telemetry streams, or rolling analytics datasets.

These workloads typically accumulate large volumes of data over time, and in modern observability use cases, that data is often stored as [wide events](https://clickhouse.com/blog/breaking-free-from-rising-observability-costs-with-open-cost-efficient-architectures),  with [each row containing a large number of attributes](https://clickhouse.com/blog/scaling-observability-beyond-100pb-wide-events-replacing-otel).

As a result, TTL-based deletions frequently operate on large, wide tables, where merge operations become memory-intensive.

As mentioned earlier, [TTL DELETE is executed during background merges](https://clickhouse.com/docs/knowledgebase/when_is_ttl_applied), even though it doesn’t combine parts, instead reading individual parts, filtering them by TTL rules, and rewriting them.

> Starting with version 26.3, TTL DELETE operations can use vertical merges, reducing memory usage during these operations.

This behavior is controlled by the new [vertical_merge_optimize_ttl_delete](https://clickhouse.com/docs/operations/settings/merge-tree-settings#vertical_merge_optimize_ttl_delete) MergeTree setting (enabled by default).

## Async Insert by default


### Contributed by Sema Checherinda

As described in the “Vertical merge for TTL DELETE” section above, ClickHouse achieves [high insert throughput](https://clickhouse.com/docs/concepts/why-clickhouse-is-so-fast#storage-layer-concurrent-inserts-are-isolated-from-each-other) by writing independent [data parts](https://clickhouse.com/docs/parts) and [merging](https://clickhouse.com/docs/concepts/why-clickhouse-is-so-fast#storage-layer-merge-time-computation) them later in the background.

Creating and merging many small parts in a short time window is resource-intensive, so [inserts should be batched for optimal performance](https://clickhouse.com/blog/asynchronous-data-inserts-in-clickhouse#data-needs-to-be-batched-for-optimal-performance).

Either client-side, or you can use asynchronous inserts in ClickHouse. 

[Asynchronous inserts](https://clickhouse.com/docs/optimize/asynchronous-inserts) shift data batching from the client side to the server side: data from insert queries is inserted into a buffer first and then written to storage during the next buffer flush, triggered by a timeout, accumulated data size, or number of inserts.

![Screenshot 2026-04-06 at 15.02.48.png](https://clickhouse.com/uploads/Screenshot_2026_04_06_at_15_02_48_25984a0ae6.png)


Since we originally [blogged](https://clickhouse.com/blog/asynchronous-data-inserts-in-clickhouse) about asynchronous inserts, we refined and optimized them further. 

For example, since 24.2, asynchronous inserts use an [adaptive algorithm](https://clickhouse.com/blog/clickhouse-release-24-02#adaptive-asynchronous-inserts) to automatically adjust the buffer flush timeout based on the frequency of inserts. 

In version 26.1, we introduced a [consistent deduplication mechanism](https://clickhouse.com/blog/clickhouse-release-26-01#deduplication-of-asynchronous-inserts-with-materialized-views) for asynchronous inserts with materialized views.

**And now, starting with 26.3 LTS, asynchronous inserts are enabled by default.** 

ClickHouse automatically batches small inserts, reducing the number of parts created by frequent writes, without requiring configuration changes for most users.


## JOIN reordering for ANTI, SEMI, FULL


### Contributed by Hechem Selmi

> "When will you stop optimizing join performance?" We will never stop!

It’s not just asynchronous inserts that have come a long way. JOIN reordering has also seen significant improvements in recent months (and slightly related, just last month we [improved](https://clickhouse.com/blog/clickhouse-release-26-02#faster-right-and-full-join) the performance of RIGHT OUTER and FULL OUTER JOINs).


### Join reordering primer

As a quick reminder, when multiple tables are joined, the join order does not affect correctness, but it can dramatically affect performance. Because different join orders can produce vastly different amounts of intermediate data. Since ClickHouse’s default [hash-based join algorithms](https://clickhouse.com/blog/clickhouse-fully-supports-joins-hash-joins-part2) build in-memory structures from one side of each join, choosing a join order that keeps build inputs small is critical for fast and efficient execution.


### Evolution of JOIN reordering in ClickHouse

JOIN reordering in ClickHouse has evolved significantly over recent releases:



* **Local automatic join reordering** for two joined tables was introduced first, enabling the optimizer to move the smaller of both tables to the right (build) side and therefore reducing the effort needed to build the hash table. ([24.12](https://clickhouse.com/blog/clickhouse-release-24-12#automatic-join-reordering)) 

* This was followed by **global automatic join reordering**, allowing efficient optimization of complex join graphs across dozens of tables and **across the most common join types** (inner, outer, cross, semi, anti). ([25.09](https://clickhouse.com/blog/clickhouse-release-25-09#join-reordering)) 
 
> This resulted in significant improvements, for example, a [1,450× speedup and 25× reduction in memory usage](https://clickhouse.com/blog/clickhouse-release-25-09#benchmarks-tpc-h-results) on one TPC-H example query. 

* To further improve decision-making, ClickHouse introduced **automatic column statistics**, enabling better cost estimation for join ordering. ([25.10](https://clickhouse.com/blog/clickhouse-release-25-10#automatically-build-column-statistics-for-mergetree-tables)) 

* Finally, a more powerful join reordering algorithm (**DPsize**) was added for INNER JOINs, exploring a larger space of join orders and often producing more efficient execution plans. ([25.12](https://clickhouse.com/blog/clickhouse-release-25-12#faster-joins-with-a-more-powerful-join-reordering-algorithm)) 



### Now: JOIN reordering for all major join types supported in ClickHouse

ClickHouse can now reorder **all major [join types](https://clickhouse.com/blog/clickhouse-fully-supports-joins-part1)**, including **ANTI, SEMI, and FULL** joins.

Previously limited to INNER and LEFT/RIGHT joins, the optimizer now automatically selects the most efficient build side across all major join types, producing better plans and reducing memory usage.

This relies on [statistics being enabled](https://clickhouse.com/blog/clickhouse-release-25-10#automatically-build-column-statistics-for-mergetree-tables) for tables.


## Sharded Map


### Contributed by Pavel Kruglov

This release not only introduces “Vertical merges for TTL DELETE”, an optimization particularly useful for observability workloads, but also improves the internal storage of the ClickHouse Map data type, speeding up access patterns common in those workloads.


### Maps in observability workloads

Observability data, such as [OpenTelemetry (OTEL) events](https://clickhouse.com/blog/clickhouse-and-open-telemtry), often includes a large number of [tags](https://opentelemetry.io/docs/languages/dotnet/instrumentation/). These tags are simple key–value pairs that provide additional context for each recorded event.

Since tags are inherently flat, they don’t benefit from a datatype like [JSON](https://clickhouse.com/docs/sql-reference/data-types/newjson) supporting deeply nested structures.

Instead, the [Map](https://clickhouse.com/docs/sql-reference/data-types/map) data type, a collection of key–value pairs, maps naturally to the tags structure.


### How Map is stored today

Internally, Map is [Array](https://clickhouse.com/docs/sql-reference/data-types/array)([Tuple](https://clickhouse.com/docs/sql-reference/data-types/tuple)(Key, Value)) in ClickHouse. The diagram below shows how two rows inserted into a table with a tags column of type Map are stored on disk.

![Screenshot 2026-04-06 at 15.06.48.png](https://clickhouse.com/uploads/Screenshot_2026_04_06_at_15_06_48_a178079a8d.png)

As the diagram shows, a Map column is stored on disk as two separate arrays: one containing all keys and one containing the corresponding values. Each array is paired with an offsets file, which maps entries back to the table rows they belong to.


### The limitation

In practice, queries usually access only a small subset of keys within a map. Because keys and values are stored as plain arrays without indexing, every lookup requires scanning the arrays, leading to unnecessary data reads.


### The solution

To address this, the new storage format splits map data into multiple sub-arrays by grouping keys into hash-based buckets. As a result, accessing a single key, such as `tags['status']`, requires reading only the corresponding bucket instead of the entire column.

> This significantly reduces the amount of data processed for common lookup patterns.


### No insert penalty

Importantly, this optimization does not impact insert performance. New data is written using the existing format, and the bucketed layout is applied later during background merges.

The next diagram sketches this for two inserts into a table with a tags column of type Map.

![Screenshot 2026-04-06 at 15.07.07.png](https://clickhouse.com/uploads/Screenshot_2026_04_06_at_15_07_07_585aa5bdb3.png)

The diagram shows three steps:

**① Insert → Level 0 parts (default format)**

Each insert creates a new [data part](https://clickhouse.com/docs/parts) using the standard Map layout: keys and values are stored as two flat arrays, without any bucketing.

**② Another insert → another Level 0 part**

A second insert produces another part in the same format. At this stage, all map data is still stored as full key and value arrays. 

Accessing a single key would require scanning the entire arrays, but this is typically **not an issue since Level 0 parts are small**.

**③ Background merge → bucketed Map storage**

During the next [background merge](https://clickhouse.com/docs/merges), ClickHouse reorganizes the Map data by splitting keys into hash-based buckets. Each bucket stores a subset of keys and their corresponding values in smaller arrays.

When accessing a key such as `tags['status']`, ClickHouse uses the hash of the key to locate the corresponding bucket (e.g., `bucket 3`) and reads only those arrays, significantly reducing the amount of data that needs to be scanned.


### Performance impact

In practice, this results in 2–49x faster single-key lookups depending on map size.


### Configuration

This behavior is controlled by the new [map_serialization_version](https://clickhouse.com/docs/operations/settings/merge-tree-settings#map_serialization_version) MergeTree setting set to `with_buckets`, and [max_buckets_in_map](https://clickhouse.com/docs/operations/settings/merge-tree-settings#max_buckets_in_map) specifies into how many buckets the data is split at a maximim (`32` by default). 

Additional settings further control the exact layout. In the example shown in the diagram above, the bucketed structure results from the following configuration:

* map_serialization_version_for_zero_level_parts = 'basic'
* map_serialization_version = 'with_buckets'
* max_buckets_in_map = 3
* map_buckets_strategy = 'const'
* map_buckets_min_avg_size = 0.





---

## Get started today

Interested in seeing how ClickHouse works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-340-get-started-today-sign-up&utm_blogctaid=340)

---