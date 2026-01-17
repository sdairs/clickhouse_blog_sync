---
title: "ClickHouse projections now behave like true secondary indexes"
date: "2026-01-09T10:18:46.824Z"
author: "Tom Schreiber"
category: "Engineering"
excerpt: "ClickHouse now supports granule-level pruning for lightweight projections, enabling them to act as true secondary indexes that work together to dramatically speed up multi-filter queries without duplicating full table data."
---

# ClickHouse projections now behave like true secondary indexes


> **TL;DR**<br/><br/>ClickHouse tables once had only *one* primary index.<br/>Now they can have **many**, implemented as lightweight projections that behave like primary indexes, without duplicating data.

**Prefer a quick walkthrough?**<br/>
Watch Mark explain how projections act as secondary indexes in ClickHouse:

<iframe width="768" height="432" src="https://www.youtube.com/embed/Fe6DqnWBs1I?si=DSwxb9BlvSwHjibA" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

<br/>

## Why projections matter

[Primary indexes](https://clickhouse.com/docs/primary-indexes) are the most important mechanism ClickHouse uses to speed up filtered queries. By storing rows on disk in the order of the table’s sorting key, the engine maintains a sparse index that can quickly locate the relevant ranges of data. But because this index depends on the physical sort order of the table, **each table can have only one primary index**.

To accelerate queries whose filters do not align with that single index, ClickHouse offers [**projections**](https://clickhouse.com/docs/sql-reference/statements/alter/projection) - automatically maintained, hidden table copies stored in a different sort order, and therefore with a different primary index. These alternative layouts can speed up queries that benefit from those orderings. The downside, historically, was storage cost: **projections duplicated the base table’s data on disk**.

## Lightweight projections as secondary indexes

Since release **25.6**, however, ClickHouse can create much more lightweight [projections that behave like a **secondary index**](https://clickhouse.com/blog/clickhouse-release-25-06#filtering-by-multiple-projections) without duplicating full rows. Instead of storing complete data copies, they store only their sorting key plus a [_part_offset](https://clickhouse.com/docs/data-modeling/projections#smarter_storage_with_part_offset) pointer back into the base table, greatly reducing storage overhead.

When applicable, [ClickHouse uses such a projection’s primary index like a secondary index to locate matching rows](https://clickhouse.com/blog/clickhouse-release-25-06#smarter-storage-with-_part_offset), while still reading the actual row data from the base table. Multiple lightweight projections can work together, so a query with several filters can take advantage of every applicable projection, and if one of the filters also matches the base table’s primary index, **that index participates as well**.


## From part-level to granule-level pruning

Until now, this mechanism could only prune entire parts; **granule-level pruning** was not supported.

With this release, _part_offset-based projections now behave like true secondary indexes with **granule-level pruning**, enabling much finer filtering and dramatically faster queries.


## Example: combining multiple projection indexes

To demonstrate this, we’ll again use [the UK price paid dataset](https://clickhouse.com/docs/getting-started/example-datasets/uk-price-paid), this time defining the table with two lightweight _part_offset-based projections: by_time and by_town:

<pre><code type='click-ui' language='sql'>
CREATE OR REPLACE TABLE uk.uk_price_paid_with_proj
(
    price UInt32,
    date Date,
    postcode1 LowCardinality(String),
    postcode2 LowCardinality(String),
    type Enum8(
      'terraced' = 1, 'semi-detached' = 2, 'detached' = 3, 'flat' = 4, 'other' = 0),
    is_new UInt8,
    duration Enum8('freehold' = 1, 'leasehold' = 2, 'unknown' = 0),
    addr1 String,
    addr2 String,
    street LowCardinality(String),
    locality LowCardinality(String),
    town LowCardinality(String),
    district LowCardinality(String),
    county LowCardinality(String),
    PROJECTION by_time (
        SELECT _part_offset ORDER BY date
    ),
    PROJECTION by_town (
        SELECT _part_offset ORDER BY town
    )
)
ENGINE = MergeTree
ORDER BY (postcode1, postcode2, addr1, addr2);
</code></pre>

Then we load the data using the instructions [here](https://clickhouse.com/docs/getting-started/example-datasets/uk-price-paid).

The diagram below sketches the base table and its two lightweight _part_offset-based projections:

![image6.png](https://clickhouse.com/uploads/image6_c12f1d6103.png)

① The base table is sorted by (postcode1, postcode2, addr1, addr2). This defines its primary index, making queries that filter by those columns fast and efficient.

② The by_time and ③ by_town projections store only their sorting key plus _part_offset, pointing back into the base table and greatly reducing data duplication. Their primary indexes act as secondary indexes for the base table, speeding up queries that filter on date and/or town.

*We benchmarked this on an AWS m6i.8xlarge EC2 instance (32 cores, 128 GB RAM) with a gp3 EBS volume (16k IOPS, 1000 MiB/s max throughput).*

We will run a query filtering on the date and town columns. Note that these columns are not part of the base table’s primary key. 

First, we run the query with projection support disabled to get a baseline performance. Note that we disabled the [query condition cache](https://clickhouse.com/blog/introducing-the-clickhouse-query-condition-cache) and [PREWHERE](https://clickhouse.com/docs/optimize/prewhere) to fully isolate index-based data pruning:

<pre><code type='click-ui' language='sql'>
SELECT *
FROM uk.uk_price_paid_with_proj
WHERE (date = '2008-09-26') AND (town = 'BARNARD CASTLE')
FORMAT Null
SETTINGS
    use_query_condition_cache = 0,
    optimize_move_to_prewhere = 0,
    optimize_use_projections= 0;
</code></pre>

The fastest of three runs finished in **0.077 seconds**:

```shell 
0 rows in set. Elapsed: 0.084 sec. Processed 30.73 million rows, 1.29 GB (363.92 million rows/s., 15.26 GB/s.)
Peak memory usage: 129.07 MiB.

0 rows in set. Elapsed: 0.076 sec. Processed 30.73 million rows, 1.29 GB (406.96 million rows/s., 17.07 GB/s.)
Peak memory usage: 129.29 MiB.

0 rows in set. Elapsed: 0.077 sec. Processed 30.73 million rows, 1.29 GB (398.51 million rows/s., 16.71 GB/s.)
Peak memory usage: 129.27 MiB.
```

Note that it was a full table scan, reading the whole table (~30 million rows)

Now we run the query with enabled projection support:

<pre><code type='click-ui' language='sql'>
SELECT *
FROM uk.uk_price_paid_with_proj
WHERE (date = '2008-09-26') AND (town = 'BARNARD CASTLE')
FORMAT Null
SETTINGS
    use_query_condition_cache = 0,
    optimize_move_to_prewhere = 0,
    optimize_use_projections= 1; -- default value
</code></pre>

The fastest of three runs finished in **0.010 seconds**:

```shell 
0 rows in set. Elapsed: 0.010 sec. Processed 16.38 thousand rows, 644.86 KB (1.60 million rows/s., 63.06 MB/s.)
Peak memory usage: 4.89 MiB.

0 rows in set. Elapsed: 0.010 sec. Processed 16.38 thousand rows, 644.86 KB (1.69 million rows/s., 66.36 MB/s.)
Peak memory usage: 4.88 MiB.

0 rows in set. Elapsed: 0.011 sec. Processed 16.38 thousand rows, 644.86 KB (1.54 million rows/s., 60.57 MB/s.)
Peak memory usage: 4.89 MiB.
```

The result: **0.077 s vs. 0.010 s — roughly a 90% speedup.**

Also note that this time only ~16k rows instead of all ~30 million rows got scanned.

Via EXPLAIN we can see that ClickHouse is using the primary indexes of *both* projections as secondary indexes to prune base table granules:

<pre><code type='click-ui' language='sql'>
EXPLAIN projections = 1
SELECT *
FROM uk.uk_price_paid_with_proj
WHERE (date = '2008-09-26') AND (town = 'BARNARD CASTLE')
SETTINGS
    use_query_condition_cache = 0,
    optimize_move_to_prewhere = 0,
    optimize_use_projections= 1; -- default value
</code></pre>   

```shell
    ┌─explain────────────────────────────────────────────────────────────┐
 1. │ Expression ((Project names + Projection))                          │
 2. │   Filter ((WHERE + Change column names to column identifiers))     │
 3. │     ReadFromMergeTree (uk.uk_price_paid_with_proj)                 │
 4. │     Projections:                                                   │
 5. │       Name: by_time                                                │
 6. │         Description: Projection has been analyzed...               │
 7. │         Condition: (date in [14148, 14148])                        │
 8. │         Search Algorithm: binary search                            │
 9. │         Parts: 5                                                   │
10. │         Marks: 7                                                   │
11. │         Ranges: 5                                                  │
12. │         Rows: 57344                                                │
13. │         Filtered Parts: 0                                          │
14. │       Name: by_town                                                │
15. │         Description: Projection has been analyzed...               │
16. │         Condition: (town in ['BARNARD CASTLE', 'BARNARD CASTLE'])  │
17. │         Search Algorithm: binary search                            │
18. │         Parts: 5                                                   │
19. │         Marks: 5                                                   │
20. │         Ranges: 5                                                  │
21. │         Rows: 40960                                                │
22. │         Filtered Parts: 0                                          │
    └────────────────────────────────────────────────────────────────────┘                     
```


Row 10 of the EXPLAIN output shows that the **by_time** projection (specifically its primary index) first narrows the search to **7 granules** (“Marks”). Since each granule contains 8,192 rows, this corresponds to **7 × 8192 = 57,344 rows** to scan (as shown in row 12). Those 7 granules lie across **5 data parts** (row 9), so the engine would need to read **5 corresponding data ranges (row 11)**.

Then, starting at row 14, the **by_town** projection’s primary index is applied. It filters out 2 of the 7 granules previously selected by the by_time projection. The final result: the engine needs to scan **5 granules**, located in **5 data ranges** across **5 parts** of the base table, because those granules may contain rows matching the query’s time and town predicate.

Two new settings are introduced to control this optimization:

* max_projection_rows_to_use_projection_index: If the estimated number of rows to read from the projection is <= this value, projection index can be applied.

* min_table_rows_to_use_projection_index: If the estimated number of rows to read from the table is >= this value, projection index will be considered.

## Key takeaway

ClickHouse tables once had only *one* primary index.

Now they can have **many**, each behaving like a primary index, and ClickHouse will use *all of them* when your query has multiple filters.