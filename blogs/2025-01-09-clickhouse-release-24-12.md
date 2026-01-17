---
title: "ClickHouse Release 24.12"
date: "2025-01-09T10:41:04.878Z"
author: "The ClickHouse Team"
category: "Engineering"
excerpt: "ClickHouse 24.12 is available. In this post, you will learn about new features, including Iceberg REST catalog and schema evolution support, the ability to use JSON subcolumns as a primary key, and even more JOIN improvements."
---

# ClickHouse Release 24.12

Another month goes by, which means it’s time for another release! 

<p>ClickHouse version 24.12 contains <b>16</b> new features &#x1F983; <b>16</b> performance optimizations &#x26F8;&#xFE0F; <b>36</b> bug fixes &#x1F3D5;&#xFE0F;</p>

In this release, we have Enum usability improvements, Iceberg REST catalog and schema evolution support, reverse table ordering, the ability to use JSON subcolumns as a primary key, automatic JOIN reordering and more!

## New Contributors

As always, we send a special welcome to all the new contributors in 24.12! ClickHouse's popularity is, in large part, due to the efforts of the community that contributes. Seeing that community grow is always humbling.

Below are the names of the new contributors:

*Emmanuel Dias, Xavier Leune, Zawa\_ll, Zaynulla, erickurbanov, jotosoares, zhangwanyun1, zwy991114, “JiaQi*

Hint: if you’re curious how we generate this list… [here](https://gist.github.com/gingerwizard/5a9a87a39ba93b422d8640d811e269e9).

<iframe width="768" height="432" src="https://www.youtube.com/embed/bv-ut-Q6vnc?si=ArCQA08_5cNGdZjB" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

You can also [view the slides from the presentation](https://presentations.clickhouse.com/release_24.12/).

## Enum usability improvements

### Contributed by ZhangLiStar

This release also sees usability improvements when working with Enums. We’re going to explore them with help from the [Reddit comments dataset](https://clickhouse.com/docs/en/getting-started/example-datasets/reddit-comments). We’ll create a table with just a couple of the columns:

<pre>
    <code type='click-ui' language='sql'>
    CREATE TABLE reddit
    (
        subreddit LowCardinality(String),
        subreddit_type Enum(
            'public' = 1, 'restricted' = 2, 'user' = 3, 
            'archived' = 4, 'gold_restricted' = 5, 'private' = 6
        ),
    )
    ENGINE = MergeTree
    ORDER BY (subreddit);
    </code>
</pre>

We can insert the data like this:

<pre><code type='click-ui' language='sql'>
INSERT INTO reddit
SELECT subreddit, subreddit_type
FROM s3(        
  'https://clickhouse-public-datasets.s3.eu-central-1.amazonaws.com/reddit/original/RC_2017-12.xz',
  'JSONEachRow'
);
</code></pre>

Let’s say we want to count the number of posts by `subreddit_type` where the type contains the string `e`. We can write the following query using the `LIKE` operator:

<pre>
    <code type='click-ui' language='sql'>
SELECT
    subreddit_type,
    count() AS c
FROM reddit
WHERE subreddit_type LIKE '%restricted%'
GROUP BY ALL
ORDER BY c DESC;
</code></pre>


If we run this query before 24.12, we’ll see an error message like this:

```
Received exception:
Code: 43. DB::Exception: Illegal type Enum8('public' = 1, 'restricted' = 2, 'user' = 3, 'archived' = 4, 'gold_restricted' = 5, 'private' = 6) of argument of function like: In scope SELECT subreddit, count() AS c FROM reddit WHERE subreddit_type LIKE '%e%' GROUP BY subreddit ORDER BY c DESC LIMIT 20. (ILLEGAL_TYPE_OF_ARGUMENT)
```

If we run it in 24.12, we’ll get the following result:

```
   ┌─subreddit_type─┬──────c─┐
1. │ restricted     │ 698263 │
2. │ user           │  39640 │
   └────────────────┴────────┘
```

The equality and IN operators also now accept unknown values. For example, the following query returns any records that have a type of `Foo` or `public`:

```sql
SELECT count() AS c
FROM reddit
WHERE subreddit_type IN ('Foo', 'public')
GROUP BY ALL;
```

If we run this query before 24.12, we’ll see an error message like this:

```
Received exception:
Code: 691. DB::Exception: Unknown element 'Foo' for enum: while converting 'Foo' to Enum8('public' = 1, 'restricted' = 2, 'user' = 3, 'archived' = 4, 'gold_restricted' = 5, 'private' = 6). (UNKNOWN_ELEMENT_OF_ENUM)

```

If we run it in 24.12, we’ll get the following result:

```
   ┌────────c─┐
1. │ 85235907 │ -- 85.24 million
   └──────────┘
```

## Reverse table ordering

### Contributed by Amos Bird

This release added a new MergeTree setting, `allow_experimental_reverse_key,` which enables support for descending sort order in MergeTree sorting keys. You can see an example of usage below:

```sql
ENGINE = MergeTree 
ORDER BY (time DESC, key)
SETTINGS allow_experimental_reverse_key=1;
```

This table will sort the `time` field in descending order.

The ability to sort data like this is handy for [time series analysis](https://clickhouse.com/blog/working-with-time-series-data-and-functions-ClickHouse), especially Top N queries. 

## JSON subcolumns as table primary key

### Contributed by Pavel Kruglov

As a reminder, ClickHouse’s [new powerful JSON implementation](https://clickhouse.com/blog/a-new-powerful-json-data-type-for-clickhouse) stores the values of each unique JSON path in a true columnar fashion:

![0_release_24_12.png](https://clickhouse.com/uploads/0_release_24_12_10b4d050d4.png)

The diagram above sketches how ClickHouse stores (and reads) any inserted JSON key path as a native subcolumn, allowing high data compression and maintaining query performance seen on classic types.

This release now supports using JSON subcolumns as a table’s primary key columns:

```sql
CREATE TABLE T
(
    data JSON()
)
ORDER BY (data.a, data.b);
```

This means that ingested JSON documents are (per [table part](https://clickhouse.com/docs/en/parts)) stored on disk [ordered](https://clickhouse.com/docs/en/optimize/sparse-primary-indexes#data-is-stored-on-disk-ordered-by-primary-key-columns) by the JSON subcolumns that are used as primary key columns. Additionally, ClickHouse will create a [primary index](https://clickhouse.com/docs/en/optimize/sparse-primary-indexes) file for automatically [speeding up](https://clickhouse.com/docs/en/optimize/sparse-primary-indexes#the-primary-index-is-used-for-selecting-granules) queries that filter on primary key columns:

![1_release_24_12.png](https://clickhouse.com/uploads/1_release_24_12_64853e1e91.png)

Furthermore, using JSON subcolumns as primary key columns [enables](https://clickhouse.com/docs/en/optimize/sparse-primary-indexes#optimal-compression-ratio-of-data-files) optimal compression ratios for the subcolumns' `*.bin` data files, provided the primary key columns are arranged in ascending order of cardinality.

Let’s look at a more concrete example. 

We use an AWS EC2 `m6i.8xlarge` instance as a test machine with 32 vCPUs and 128 GiB of main memory and the [Bluesky dataset as a test dataset](https://clickhouse.com/blog/building-a-medallion-architecture-for-bluesky-json-data-with-clickhouse).

We loaded the 100 million Bluesky events (one JSON document per event) into two ClickHouse tables.

This is the first table that doesn’t use any JSON subcolumns as primary key columns:

```sql
CREATE TABLE bluesky_100m_raw
(
    data JSON()
)
ORDER BY ();
```

The second table uses some JSON subcolumns as primary key columns (plus optionally some [type hints](https://clickhouse.com/docs/en/sql-reference/data-types/newjson) for these columns to get rid of some type-casts in queries):

<pre><code type='click-ui' language='sql'>
CREATE TABLE bluesky_100m_primary_key
(
    data JSON(
        kind LowCardinality(String), 
        commit.operation LowCardinality(String), 
        commit.collection LowCardinality(String), 
        time_us UInt64
    )
)
ORDER BY (
    data.kind, 
    data.commit.operation, 
    data.commit.collection, 
    fromUnixTimestamp64Micro(data.time_us)
);
</code></pre>

Both tables contain the same 100 million JSON docs.

Now we run a query (“When do people block people on BlueSky” - adapted from the "When do people use BlueSky?” query that you can [run on the ClickHouse SQL playground](https://sql.clickhouse.com/?query_id=51KVUJ5FGJUQV9XU13JKL3&run_query=true&tab=charts)) on the table without a primary key:

<pre><code type='click-ui' language='sql'>
SELECT
    toHour(fromUnixTimestamp64Micro(data.time_us::UInt64)) AS hour_of_day,
    count() AS block_events
FROM bluesky_100m_raw
WHERE (data.kind = 'commit') 
AND (data.commit.operation = 'create') 
AND (data.commit.collection = 'app.bsky.graph.block')
GROUP BY hour_of_day
ORDER BY hour_of_day ASC;
</code></pre>

```text
    ┌─hour_of_day─┬─block_events─┐
 1. │           0 │        89395 │
 2. │           1 │       143542 │
 3. │           2 │       154424 │
 4. │           3 │       162894 │
 5. │           4 │        65893 │
 6. │           5 │        39556 │
 7. │           6 │        34359 │
 8. │           7 │        35230 │
 9. │           8 │        30812 │
10. │           9 │        35620 │
11. │          10 │        31094 │
12. │          16 │        33359 │
13. │          17 │        65555 │
14. │          18 │        65135 │
15. │          19 │        65775 │
16. │          20 │        70096 │
17. │          21 │        65640 │
18. │          22 │        75840 │
19. │          23 │       143024 │
    └─────────────┴──────────────┘

19 rows in set. Elapsed: 0.607 sec. Processed 100.00 million rows, 10.21 GB (164.83 million rows/s., 16.83 GB/s.)
Peak memory usage: 337.52 MiB.

```

Let’s run the same query on the table with a primary key (note that the query filters on a prefix of the primary key columns):

<pre><code type='click-ui' language='sql'>
SELECT
    toHour(fromUnixTimestamp64Micro(data.time_us)) AS hour_of_day,
    count() AS block_events
FROM bluesky_100m_primary_key
WHERE (data.kind = 'commit') 
AND (data.commit.operation = 'create') 
AND (data.commit.collection = 'app.bsky.graph.block')
GROUP BY hour_of_day
ORDER BY hour_of_day ASC;
</code></pre>

```text
    ┌─hour_of_day─┬─block_events─┐
 1. │           0 │        89395 │
 2. │           1 │       143542 │
 3. │           2 │       154424 │
 4. │           3 │       162894 │
 5. │           4 │        65893 │
 6. │           5 │        39556 │
 7. │           6 │        34359 │
 8. │           7 │        35230 │
 9. │           8 │        30812 │
10. │           9 │        35620 │
11. │          10 │        31094 │
12. │          16 │        33359 │
13. │          17 │        65555 │
14. │          18 │        65135 │
15. │          19 │        65775 │
16. │          20 │        70096 │
17. │          21 │        65640 │
18. │          22 │        75840 │
19. │          23 │       143024 │
    └─────────────┴──────────────┘

19 rows in set. Elapsed: 0.011 sec. Processed 1.47 million rows, 16.16 MB (129.69 million rows/s., 1.43 GB/s.)
Peak memory usage: 2.18 MiB.
```

Boom: The query runs 50 times faster and uses 150 times less memory.

## Iceberg REST catalog and schema evolution support

### Contributed by Daniil Ivanik and Kseniia Sumarokova

This release introduces support for querying [Apache Iceberg REST catalogs](https://iceberg.apache.org/concepts/catalog/). At the moment, the Unity and Polaris catalogs are supported. We first create a table using the [Iceberg table engine](https://clickhouse.com/docs/en/engines/table-engines/integrations/iceberg):

```
CREATE TABLE unity_demo
ENGINE = Iceberg('https://dbc-55555555-5555.cloud.databricks.com/api/2.1/unity-catalog/iceberg')
SETTINGS
  catalog_type = 'rest',
  catalog_credential = 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee:...',
  warehouse = 'unity',
  oauth_server_uri = 'https://dbc-55555555-5555.cloud.databricks.com/oidc/v1/token',
  auth_scope = 'all-apis,sql';
```

Then, we can query the data in the catalog’s underlying table:

```

SHOW TABLES FROM unity_demo;
SELECT * unity_demo."webinar.test";
```

The Iceberg table function supports schema evolution, including columns added or removed over time, renamed columns, and data types changed between primitive types.

## Parallel hash join by default in action

### Contributed by Nikita Taranov

[Every](https://clickhouse.com/blog/clickhouse-release-24-05#cross-join-improvements) ClickHouse release brings JOIN improvements, and since this is our special Christmas release, it’s loaded with a sleigh full of JOIN enhancements! ✨

In the [24.11 release post](https://clickhouse.com/blog/clickhouse-release-24-11#parallel-hash-join-is-the-default-join-strategy), we briefly mentioned that the [parallel hash join](https://clickhouse.com/blog/clickhouse-fully-supports-joins-hash-joins-part2#parallel-hash-join) is now ClickHouse's [default join strategy](https://clickhouse.com/docs/en/operations/settings/settings#join_algorithm). In this post, we will demonstrate the performance improvements of this change with a concrete example. 

We use an AWS EC2 m6i.8xlarge instance with 32 vCPUs and 128 GiB of main memory as a test machine. 

We use the [TPC-H dataset](https://clickhouse.com/docs/en/getting-started/example-datasets/tpch) with a scaling factor of 100 as a test dataset for table joins, which means that the overall amount of data stored in all tables is 100 GB.   
We created and loaded the 8 tables (modeling a wholesale supplier's data warehouse) by [following the instructions in the docs](https://clickhouse.com/docs/en/getting-started/example-datasets/tpch#data-generation-and-import).

Now we run query 3 from the [set of standard TPC-H benchmark queries](https://clickhouse.com/docs/en/getting-started/example-datasets/tpch#queries) with the previous default join strategy of ClickHouse - the [hash join](https://clickhouse.com/blog/clickhouse-fully-supports-joins-hash-joins-part2#hash-join):

<pre><code type='click-ui' language='sql'>
SELECT
    l_orderkey,
    sum(l_extendedprice * (1 - l_discount)) AS revenue,
    o_orderdate,
    o_shippriority
FROM
    customer,
    orders,
    lineitem
WHERE
    c_mktsegment = 'BUILDING'
    AND c_custkey = o_custkey
    AND l_orderkey = o_orderkey
    AND o_orderdate < DATE '1995-03-15'
    AND l_shipdate > DATE '1995-03-15'
GROUP BY
    l_orderkey,
    o_orderdate,
    o_shippriority
ORDER BY
    revenue DESC,
    o_orderdate
FORMAT Null
SETTINGS join_algorithm='hash';
</code></pre>

```
0 rows in set. Elapsed: 38.305 sec. Processed 765.04 million rows, 15.03 GB (19.97 million rows/s., 392.40 MB/s.)
Peak memory usage: 25.42 GiB.
```

Next, we run the same query with the new default join strategy of ClickHouse - the [parallel hash join](https://clickhouse.com/blog/clickhouse-fully-supports-joins-hash-joins-part2#parallel-hash-join):

<pre><code type='click-ui' language='sql'>
SELECT
    l_orderkey,
    sum(l_extendedprice * (1 - l_discount)) AS revenue,
    o_orderdate,
    o_shippriority
FROM
    customer,
    orders,
    lineitem
WHERE
    c_mktsegment = 'BUILDING'
    AND c_custkey = o_custkey
    AND l_orderkey = o_orderkey
    AND o_orderdate < DATE '1995-03-15'
    AND l_shipdate > DATE '1995-03-15'
GROUP BY
    l_orderkey,
    o_orderdate,
    o_shippriority
ORDER BY
    revenue DESC,
    o_orderdate
FORMAT Null
SETTINGS join_algorithm='default';
</code></pre>

```
0 rows in set. Elapsed: 5.099 sec. Processed 765.04 million rows, 15.03 GB (150.04 million rows/s., 2.95 GB/s.)
Peak memory usage: 29.65 GiB.
```

The query runs ~8 times faster with the parallel hash join.

## Automatic JOIN reordering

### Contributed by Vladimir Cherkasov

The next JOIN improvement of our Xmas release is automatic join reordering.

As a reminder, ClickHouse’s [fastest](https://clickhouse.com/blog/clickhouse-fully-supports-joins-how-to-choose-the-right-algorithm-part5#imdb-large-join-runs) join algorithms, like its new default algorithm, the [parallel hash join](https://clickhouse.com/blog/clickhouse-fully-supports-joins-hash-joins-part2#parallel-hash-join), are based on in-memory hash tables and work by ① first loading the data from the right-hand side table of the join query into a hash table (this is also called the build phase), and ② then the data from the left-hand side table is streamed and joined by doing lookups into the hash table (this is called the scan phase):

![2_release_24_12.png](https://clickhouse.com/uploads/2_release_24_12_a52f673ebf.png)

Note that because ClickHouse takes the right-hand side table and creates a hash table with its data in RAM, placing the smaller table on the right-hand side of the JOIN is more memory efficient and often much faster.

Similarly, ClickHouse’s additional non-memory bound [join algorithms](https://clickhouse.com/blog/clickhouse-fully-supports-joins-how-to-choose-the-right-algorithm-part5#overview-of-clickhouse-join-algorithms) based on external sorting, like the [partial merge join](https://clickhouse.com/blog/clickhouse-fully-supports-joins-full-sort-partial-merge-part3#partial-merge-join), have a a build and a scan phase. For example, the partial merge join first builds a sorted version of the right table and then scans the left table. Therefore, placing the smaller table on the right-hand side of the JOIN is often much faster.

Instead of always using the right table of a join for the build phase, ClickHouse now has a new setting - [query\_plan\_join\_swap\_table](https://clickhouse.com/docs/en/operations/settings/settings#query_plan_join_swap_table) - to determine which side of the join should be the build table. Possible values are:  

* `auto` (the default value): In this mode, ClickHouse will try to choose the table with the smallest number of rows for the build phase. This is beneficial for almost every join query.  
* `false`: Never swap tables (the right table is the build table).  
* `true`: Always swap tables (the left table is the build table).

We will demonstrate the `auto` mode of the new  `query_plan_join_swap_table` setting with another query over the TPC-H tables (see the previous section for instructions to create and load the tables, and info about the test hardware) where we join the `lineitem` and the `part` tables.

First, we check the size of these two tables:

```sql
SELECT
    table,
    formatReadableQuantity(sum(rows)) AS rows,
    formatReadableSize(sum(bytes_on_disk)) AS size_on_disk
FROM system.parts
WHERE active AND (table IN ['lineitem', 'part'])
GROUP BY table
ORDER BY table ASC;
```

```
   ┌─table────┬─rows───────────┬─size_on_disk─┐
1. │ lineitem │ 600.04 million │ 26.69 GiB    │
2. │ part     │ 20.00 million  │ 896.47 MiB   │
   └──────────┴────────────────┴──────────────┘
```

As you can see, the `lineitem` table is significantly larger than the `part` table.

The next query joins the `lineitem` and the `part` tables, and places the much larger `lineitem` table on the right side of the join:

<pre><code type='click-ui' language='sql'>
SELECT 100.00 * sum(
  CASE
  WHEN p_type LIKE 'PROMO%'
  THEN l_extendedprice * (1 - l_discount)
  ELSE 0 END) / sum(l_extendedprice * (1 - l_discount)) AS promo_revenue
FROM part, lineitem
WHERE l_partkey = p_partkey;
</code></pre>

We run this query with the new  `query_plan_join_swap_table` setting set to `false`, meaning that, as usual, the right table is the build table, and therefore ClickHouse first loads the data from the very large `lineitem` table into the main memory (in parallel into multiple hash tables as [the parallel hash join is the default join algoirthm](https://clickhouse.com/blog/clickhouse-release-24-11#parallel-hash-join-is-the-default-join-strategy)):

<pre><code type='click-ui' language='sql'>
SELECT 100.00 * sum(
  CASE
  WHEN p_type LIKE 'PROMO%'
  THEN l_extendedprice * (1 - l_discount)
  ELSE 0 END) / sum(l_extendedprice * (1 - l_discount)) AS promo_revenue
FROM part, lineitem
WHERE l_partkey = p_partkey
SETTINGS query_plan_join_swap_table='false';
</code></pre>


```
   ┌──────promo_revenue─┐
1. │ 16.650141208349083 │
   └────────────────────┘

1 row in set. Elapsed: 55.687 sec. Processed 620.04 million rows, 12.67 GB (11.13 million rows/s., 227.57 MB/s.)
Peak memory usage: 24.39 GiB.
```

Next, we run the same query with the new  `query_plan_join_swap_table` setting set to `auto` (the default value). Now ClickHouse will use estimations of the table sizes to determine which side of the join should be the build table. Therefore, ClickHouse first loads the data from the very much smaller `part` table into the main memory into hash tables before streaming and joining the data from the `lineitem` table:

<pre><code type='click-ui' language='sql'>
SELECT 100.00 * sum(
  CASE
  WHEN p_type LIKE 'PROMO%'
  THEN l_extendedprice * (1 - l_discount)
  ELSE 0 END) / sum(l_extendedprice * (1 - l_discount)) AS promo_revenue
FROM part, lineitem
WHERE l_partkey = p_partkey
SETTINGS query_plan_join_swap_table='auto';
</code></pre>

```
   ┌──────promo_revenue─┐
1. │ 16.650141208349083 │
   └────────────────────┘

1 row in set. Elapsed: 9.447 sec. Processed 620.04 million rows, 12.67 GB (65.63 million rows/s., 1.34 GB/s.)
Peak memory usage: 4.72 GiB.
```

As you can see, the query runs over 5 times faster and uses 5 times less memory.

## Optimization of JOIN expressions

### Contributed by János Benjamin Antal

For joins with a chain of conditions, separated by `OR`s, like shown in this abstract example… 

```sql
JOIN ... ON (a=b AND x) OR (a=b AND y) OR (a=b AND z)
```

… ClickHouse uses hash tables per condition (when one of the [hash table-based join algorithms](https://clickhouse.com/blog/clickhouse-fully-supports-joins-hash-joins-part2) is used).

One way to reduce the number of hash tables and to allow better predicate push downs is to extract common expressions from ON clause of the example JOIN above:

```sql
JOIN ...ON a=b AND (x OR y OR z)
```

This behavior can be enabled by setting the new `optimize_extract_common_expressions` setting to `1`. Because this setting is currently experimental, the default value is currently `0`.

We demonstrate this new setting with another query over the TPC-H tables (see the previous section for instructions on creating and loading the tables, plus infos about the used hardware). 

We run the following join query that has a chain of conditions, separated by `OR`s, with  `optimize_extract_common_expressions` set to `0` (which disables the setting):

<pre><code type='click-ui' language='sql'>
SELECT
  sum(l_extendedprice * (1 - l_discount)) AS revenue
FROM
  lineitem, part
WHERE
(
        p_partkey = l_partkey
    AND p_brand = 'Brand#12'
    AND p_container in ('SM CASE', 'SM BOX','SM PACK', 'SM PKG')
    AND l_quantity >= 1 AND l_quantity <= 1 + 10
    AND p_size BETWEEN 1 AND 5
    AND l_shipmode in ('AIR', 'AIR REG')
    AND l_shipinstruct = 'DELIVER IN PERSON'
)
OR
(
        p_partkey = l_partkey
    AND p_brand = 'Brand#23'
    AND p_container in ('MED BAG', 'MED BOX', 'MED PKG', 'MED PACK')
    AND l_quantity >= 10 AND l_quantity <= 10 + 10
    AND p_size BETWEEN 1 AND 10
    AND l_shipmode in ('AIR', 'AIR REG')
    AND l_shipinstruct = 'DELIVER IN PERSON'
)
OR
(
        p_partkey = l_partkey
    AND p_brand = 'Brand#34'
    AND p_container in ('LG CASE', 'LG BOX', 'LG PACK', 'LG PKG')
    AND l_quantity >= 20 AND l_quantity <= 20 + 10
    AND p_size BETWEEN 1 AND 15
    AND l_shipmode in ('AIR', 'AIR REG')
    AND l_shipinstruct = 'DELIVER IN PERSON'
)
SETTINGS optimize_extract_common_expressions = 0;
</code></pre>

On our test machine, this query had a progress of 3% after 30 minutes…so we aborted, and ran the same query with enabled  `optimize_extract_common_expressions` setting:

<pre><code type='click-ui' language='sql'>
SELECT
  sum(l_extendedprice * (1 - l_discount)) AS revenue
FROM
  lineitem, part
WHERE
(
        p_partkey = l_partkey
    AND p_brand = 'Brand#12'
    AND p_container in ('SM CASE', 'SM BOX','SM PACK', 'SM PKG')
    AND l_quantity >= 1 AND l_quantity <= 1 + 10
    AND p_size BETWEEN 1 AND 5
    AND l_shipmode in ('AIR', 'AIR REG')
    AND l_shipinstruct = 'DELIVER IN PERSON'
)
OR
(
        p_partkey = l_partkey
    AND p_brand = 'Brand#23'
    AND p_container in ('MED BAG', 'MED BOX', 'MED PKG', 'MED PACK')
    AND l_quantity >= 10 AND l_quantity <= 10 + 10
    AND p_size BETWEEN 1 AND 10
    AND l_shipmode in ('AIR', 'AIR REG')
    AND l_shipinstruct = 'DELIVER IN PERSON'
)
OR
(
        p_partkey = l_partkey
    AND p_brand = 'Brand#34'
    AND p_container in ('LG CASE', 'LG BOX', 'LG PACK', 'LG PKG')
    AND l_quantity >= 20 AND l_quantity <= 20 + 10
    AND p_size BETWEEN 1 AND 15
    AND l_shipmode in ('AIR', 'AIR REG')
    AND l_shipinstruct = 'DELIVER IN PERSON'
)
SETTINGS optimize_extract_common_expressions = 1;
</code></pre>


```
   ┌───────revenue─┐
1. │ 298937728.882 │ -- 298.94 million
   └───────────────┘

1 row in set. Elapsed: 3.021 sec. Processed 620.04 million rows, 38.21 GB (205.24 million rows/s., 12.65 GB/s.)
Peak memory usage: 2.79 GiB.
```

Now the query returned its result in 3 seconds.

## Non-equi JOINs supported by default

### Contributed by Vladimir Cherkasov

Since version 24.05, ClickHouse [had experimental support for non-equal conditions](https://clickhouse.com/blog/clickhouse-release-24-05#non-equal-join) in the ON clause of JOIN:

```sql
-- Equi join
SELECT t1.*, t2.* FROM t1 JOIN t2 ON t1.key = t2.key;

-- Non-equi joins
SELECT t1.*, t2.* FROM t1 JOIN t2 ON t1.key != t2.key;
SELECT t1.*, t2.* FROM t1 JOIN t2 ON t1.key > t2.key

```

With the current release, this support is no longer experimental and enabled by default.

Stay tuned for the next releases this year that will bring, [as promised](https://clickhouse.com/blog/clickhouse-release-24-05#cross-join-improvements), even more JOIN improvements!   
 