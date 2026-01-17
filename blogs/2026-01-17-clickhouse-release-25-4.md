---
title: "ClickHouse Release 25.4"
date: "2025-05-06T12:22:45.552Z"
author: "The ClickHouse Team"
category: "Engineering"
excerpt: "ClickHouse 25.4 is out! In this post, we highlight lazy materialization, Apache Iceberg time travel, correlated subqueries for the `EXISTS` clause, and more!"
---

# ClickHouse Release 25.4

Another month goes by, which means it’s time for another release! 

<p>ClickHouse version 25.4 contains <b>25</b> new features &#127800; <b>23</b> performance optimizations &#129419; <b>58</b> bug fixes &#128029;</p>

This release brings lazy materialization, Apache Iceberg time travel, correlated subqueries for the `EXISTS` clause, and more!

## New Contributors

A special welcome to all the new contributors in 25.4! The growth of ClickHouse's community is humbling, and we are always grateful for the contributions that have made ClickHouse so popular.

Below are the names of the new contributors:

*Amol Saini, Drew Davis, Elmi Ahmadov, Fellipe Fernandes, Grigory Korolev, Jia Xu, John Doe, Luke Gannon, Muzammil Abdul Rehman, Nikolai Ryzhov, ParvezAhamad Kazi, Pavel Shutsin, Saif Ullah, Samay Sharma, Shahbaz Aamir, Sumit, Todd Yocum, Vladimir Baikov, Wudidapaopao, Xiaozhe Yu, arf42, cjw, felipeagfranceschini, krzaq, wujianchao5, zouyunhe*

Hint: if you’re curious how we generate this list… [here](https://gist.github.com/gingerwizard/5a9a87a39ba93b422d8640d811e269e9).

<iframe width="768" height="432" src="https://www.youtube.com/embed/7wbfKTlieOo?si=BshuBC5aa6YBApCA" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
<br />

You can also [view the slides from the presentation](https://presentations.clickhouse.com/2025-release-25.4/).

## Lazy materialization

### Contributed by Xiaozhe Yu

Lazy materialization is a new query optimization in ClickHouse that defers reading column data until it’s actually needed. In Top N queries with sorting and LIMIT, this means ClickHouse can often skip loading most of the data, cutting down I/O, memory usage, and runtime by orders of magnitude.

Here’s a real-world example: this query finds the [Amazon reviews](https://clickhouse.com/docs/getting-started/example-datasets/amazon-reviews) with the highest number of helpful votes, returning the top 3 along with their title, headline, and full text.

We first run it with lazy materialization disabled (and cold filesystem cache):

<pre><code type='click-ui' language='sql'>
SELECT helpful_votes, product_title, review_headline, review_body
FROM amazon.amazon_reviews
ORDER BY helpful_votes DESC
LIMIT 3
FORMAT Null
SETTINGS query_plan_optimize_lazy_materialization = false;
</code></pre>

```
0 rows in set. Elapsed: 219.071 sec. Processed 150.96 million rows, 71.38 GB (689.08 thousand rows/s., 325.81 MB/s.)
Peak memory usage: 1.11 GiB.
```

Then we rerun the exact same query, but this time with lazy materialization enabled (after clearing the filesystem cache again):

<pre><code type='click-ui' language='sql'>
SELECT helpful_votes, product_title, review_headline, review_body
FROM amazon.amazon_reviews
ORDER BY helpful_votes DESC
LIMIT 3
FORMAT Null
SETTINGS query_plan_optimize_lazy_materialization = true;
</code></pre>

```
0 rows in set. Elapsed: 0.139 sec. Processed 150.96 million rows, 1.81 GB (1.09 billion rows/s., 13.06 GB/s.)
Peak memory usage: 3.80 MiB.
```

Boom: a **1,576× speedup\!** With 40× less I/O and 300× lower memory.

Same query. Same table. Same machine.  
All we changed? When ClickHouse reads the data.


Tom Schreiber recently wrote a blog post, [ClickHouse gets lazier (and faster): Introducing lazy materialization](https://clickhouse.com/blog/clickhouse-gets-lazier-and-faster-introducing-lazy-materialization), in which he explains this feature in detail.

## Data Lakes from MergeTree tables

### Contributed by Alexey Milovidov

MergeTree tables on read-only disks can now refresh their state and load new data parts, if they appear in the background.

This lets you run an unlimited number of readers on top of externally hosted, continuously updating datasets, which is great for data sharing and publishing.

We can create at most one writer:

<pre><code type='click-ui' language='sql'>
CREATE TABLE writer (...) ORDER BY ()
SETTINGS 
  table_disk = true,
  disk = disk(
      type = object_storage,
      object_storage_type = s3,
      endpoint = 'https://mybucket.s3.us-east-1.amazonaws.com/data/',
      metadata_type = plain_rewritable);
</code></pre>

And an unlimited number of readers in any locations:

<pre><code type='click-ui' language='sql'>
CREATE TABLE reader (...) ORDER BY ()
SETTINGS 
  table_disk = true, 
  refresh_parts_interval = 1,
  disk = disk(
      readonly = true,
      type = object_storage,
      object_storage_type = s3,
      endpoint = 'https://mybucket.s3.us-east-1.amazonaws.com/data/',
      metadata_type = plain_rewritable);
</code></pre>

Let's have a look at one we created earlier, so to speak.
The following table dataset contains over 40 million posts from Hacker News:

<pre><code type='click-ui' language='sql'>
CREATE TABLE hackernews_history UUID '66491946-56e3-4790-a112-d2dc3963e68a'
(
    `update_time` DateTime DEFAULT now(),
    `id` UInt32,
    `deleted` UInt8,
    `type` Enum8(
        'story' = 1, 'comment' = 2, 'poll' = 3, 'pollopt' = 4, 'job' = 5
    ),
    `by` LowCardinality(String),
    `time` DateTime,
    `text` String,
    `dead` UInt8,
    `parent` UInt32,
    `poll` UInt32,
    `kids` Array(UInt32),
    `url` String,
    `score` Int32,
    `title` String,
    `parts` Array(UInt32),
    `descendants` Int32
)
ENGINE = ReplacingMergeTree(update_time)
ORDER BY id
SETTINGS 
  refresh_parts_interval = 60, 
  disk = disk(
    readonly = true, 
    type = 's3_plain_rewritable', 
    endpoint = 'https://clicklake-test-2.s3.eu-central-1.amazonaws.com/', 
    use_environment_credentials = false
  );
</code></pre>

We can write a query against it just like any other table:

<pre><code type='click-ui' language='sql'>
SELECT type, count()
FROM hackernews_history
GROUP BY ALL
ORDER BY count() DESC;
</code></pre>

```
┌─type────┬──count()─┐
│ comment │ 38549467 │
│ story   │  5777529 │
│ job     │    17677 │
│ pollopt │    15261 │
│ poll    │     2247 │
└─────────┴──────────┘
```

## CPU workload scheduler

### Contributed by Sergei Trifonov

This release adds [CPU slot scheduling](https://clickhouse.com/docs/operations/workload-scheduling#cpu_scheduling) for workloads, which lets you limit the number of concurrent threads for a specific workload.

This feature makes it possible to share ClickHouse clusters between different workloads and provide weighted fair allocation and priority-based allocation for CPU resources. 
This lets you, for example, run heavy ad-hoc queries without affecting high-priority real time reporting. 

Let's have a look at how to configure it.
We first need to define a CPU resource:

<pre><code type='click-ui' language='sql'>
CREATE RESOURCE cpu (MASTER THREAD, WORKER THREAD);
</code></pre>

> Once we define a CPU resource, the setting `max_concurrent_threads` is enabled for controlling CPU allocation. Without a CPU resource declaration, ClickHouse will use the server-level concurrency control settings (`concurrent_threads_soft_limit_num` and related settings) instead.

A quick explainer on the thread types from the docs: 

* Master thread — the first thread that starts working on a query or background activity like a merge or a mutation.
* Worker thread — the additional threads that master can spawn to work on CPU-intensive tasks.

To achieve better responsiveness, we might choose to use separate resources for master and worker threads:

<pre><code type='click-ui' language='sql'>
CREATE RESOURCE worker_cpu (WORKER THREAD);
CREATE RESOURCE master_cpu (MASTER THREAD);
</code></pre>

We can list the resources on our ClickHouse service by running the following query:

<pre><code type='click-ui' language='sql'>
SELECT *
FROM system.resources
FORMAT Vertical;
</code></pre>

We can then create workloads that use those resources.

<pre><code type='click-ui' language='sql'>
CREATE WORKLOAD all;

CREATE WORKLOAD admin IN all 
SETTINGS max_concurrent_threads = 10;

CREATE WORKLOAD production IN all 
SETTINGS max_concurrent_threads = 100;

CREATE WORKLOAD analytics IN production
SETTINGS max_concurrent_threads = 60, weight = 9;

CREATE WORKLOAD ingestion IN production;
</code></pre>

> We can only have one top level workload i.e. one that doesn't include the `IN <workload>` clause.

We can list the workloads on our ClickHouse service by running the following query:

<pre><code type='click-ui' language='sql'>
SELECT *
FROM system.workloads
FORMAT Vertical;
</code></pre>

We can then set the appropriate workload when querying:

<pre><code type='click-ui' language='sql'>
SET workload = 'analytics';
</code></pre>

## Correlated subqueries for EXISTS

### Contributed by Dmitry Novik

Our next feature is a fun one - the `EXISTS` clause now supports correlated subqueries! Let’s see how this works with help from the [UK property dataset](https://clickhouse.com/docs/getting-started/example-datasets/uk-price-paid).

Below is the schema for this dataset:

<pre><code type='click-ui' language='sql'>
CREATE TABLE uk.uk_price_paid
(
    price UInt32,
    date Date,
    postcode1 LowCardinality(String),
    postcode2 LowCardinality(String),
    type Enum8('terraced' = 1, 'semi-detached' = 2, 'detached' = 3, 'flat' = 4, 'other' = 0),
    is_new UInt8,
    duration Enum8('freehold' = 1, 'leasehold' = 2, 'unknown' = 0),
    addr1 String,
    addr2 String,
    street LowCardinality(String),
    locality LowCardinality(String),
    town LowCardinality(String),
    district LowCardinality(String),
    county LowCardinality(String)
)
ENGINE = MergeTree
ORDER BY (postcode1, postcode2, addr1, addr2);
</code></pre>

Let’s say we want to find districts/towns with the highest average property prices in 2009 where at least five properties were sold, but with one caveat: they must have sold at least one detached property for over £1 million in 2006!

We can now work this out with the following query:


<pre><code type='click-ui' language='sql'>
SELECT district, town,
       round(AVG(price), 2) AS avgPrice,
       COUNT(*) AS totalSales
FROM uk.uk_price_paid p1
WHERE date BETWEEN '2009-01-01' AND '2009-12-31'
AND EXISTS (
  SELECT 1
  FROM uk.uk_price_paid p2
  WHERE p2.district = p1.district
  AND p2.town = p1.town
  AND p2.type = 'detached'
  AND p2.price > 1000000
  AND p2.date BETWEEN '2006-01-01' AND '2006-12-31'
)
GROUP BY ALL
HAVING totalSales > 5
ORDER BY avgPrice DESC
LIMIT 10
SETTINGS allow_experimental_correlated_subqueries = 1;
</code></pre>


```
┌─district───────────────┬─town─────────────┬───avgPrice─┬─totalSales─┐
│ ELMBRIDGE              │ LEATHERHEAD      │  1118756.9 │         58 │
│ KENSINGTON AND CHELSEA │ LONDON           │ 1060251.76 │       1620 │
│ WOKING                 │ GUILDFORD        │     901000 │          9 │
│ CHILTERN               │ TRING            │  893333.33 │          6 │
│ ENFIELD                │ BARNET           │  891921.88 │         48 │
│ ELMBRIDGE              │ COBHAM           │   875841.6 │        202 │
│ WYCOMBE                │ HENLEY-ON-THAMES │     846300 │         10 │
│ GUILDFORD              │ GODALMING        │  831977.67 │          9 │
│ RUNNYMEDE              │ VIRGINIA WATER   │  802773.53 │         85 │
│ THREE RIVERS           │ NORTHWOOD        │  754197.22 │         36 │
└────────────────────────┴──────────────────┴────────────┴────────────┘
```

Notice that we must enable `allow_experimental_correlated_subqueries` as this is an experimental feature.

Lines 10 and 11 reference fields from the outer query (`p1`) within the subquery (`p2`). The condition `p2.district = p1.district AND p2.town = p1.town` creates a dynamic relationship between the two query levels, evaluating the subquery separately for each district/town combination.

## Persistent databases in clickhouse-local

### Contributed by Alexey Milovidov

The default database is now persistent when using [clickhouse-local](https://clickhouse.com/docs/operations/utilities/clickhouse-local). 

To see the difference that this makes, let's launch clickhouse-local in 25.3:

<pre><code type='click-ui' language='bash'>
clickhouse -m --path data
</code></pre>

We’ll create a table:

<pre><code type='click-ui' language='sql'>
CREATE TABLE foo (a UInt8) ORDER BY a;
</code></pre>

If we exit the CLI by typing `exit;` and relaunch it, the following query will return no rows:

<pre><code type='click-ui' language='sql'>
SHOW TABLES
</code></pre>

```
Ok.

0 rows in set. Elapsed: 0.008 sec.
```

Now let’s do the same with ClickHouse 25.4:

<pre><code type='click-ui' language='bash'>
clickhouse -m --path data2
</code></pre>

We’ll create a table:

<pre><code type='click-ui' language='sql'>
CREATE TABLE foo (a UInt8) ORDER BY a;
</code></pre>

And then if we exit before relaunching, we’ll see the following:

<pre><code type='click-ui' language='sql'>
SHOW TABLES
</code></pre>

```
   ┌─name─┐
1. │ foo  │
   └──────┘

1 row in set. Elapsed: 0.006 sec.
```

## Apache Iceberg time travel

### Contributed by Brett Hoerner, Dan Ivanik

Over the last few releases, we’ve been adding more support to ClickHouse for open table formats like Apache Iceberg/Delta Lake and catalogs like Unity/AWS Glue, and this release is no exception. 

It’s now possible to run Apache Iceberg queries based on previous snapshots, aka time travel. We’ve also recorded [a video showing how to use this functionality with the AWS Glue catalog](https://clickhouse.com/videos/iceberg-aws-glue-clickhouse).

<iframe width="768" height="432" src="https://www.youtube.com/embed/5fRcMByUrlY?si=1X9FrjyPGUjhkJD-" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

Below is an example showing the query syntax for this functionality: 

<pre><code type='click-ui' language='sql'>
CREATE DATABASE test
ENGINE = DataLakeCatalog
SETTINGS 
  catalog_type = 'glue', 
  region = '<region>', 
  aws_access_key_id = '<key>', 
  aws_secret_access_key = '<secret>';
</code></pre>

<pre><code type='click-ui' language='sql'>
SELECT count()
FROM test.`iceberg_benchmark.time_travel`
SETTINGS iceberg_timestamp_ms = 1742497721135;
</code></pre>

You can also see the [AWS Glue Catalog developer guide](https://clickhouse.com/docs/use-cases/data-lake/glue-catalog) for more examples.

## Default compression codec for tables

### Contributed by Gvoelfin

It’s now possible to set a default compression codec for every column in `MergeTree` tables. For example:

<pre><code type='click-ui' language='sql'>
CREATE TABLE t (
    time DateTime CODEC(ZSTD(3)), -- codec on a column level
    user_id UInt64, -- uses the default codec
    ...
) ORDER BY time
SETTINGS default_compression_codec = 'ZSTD(1)' -- codec on a table level
</code></pre>

As a reminder, ClickHouse applies `LZ4` compression in the self-managed version and `ZSTD` in ClickHouse Cloud by default.

As well as setting the default codec at a table level, we can also set it globally for all tables via a config file:

*config.d/compression.yaml*

<pre><code type='click-ui' language='sql'>
compression:
    case:
        min_part_size: 1000000000 # Optional condition
        method: 'zstd'
</code></pre>

## SSH Interface

### George Gamezardashvili, Nikita Mikhailov

ClickHouse 25.3 saw the ClickHouse Server add support for the SSH protocol, which means any SSH client can connect to it directly

We've now added support for this to [play.clickhouse.com](https://play.clickhouse.com).
You can connect to that service by running the following:

<pre><code type='click-ui' language='sql'>
ssh play@play.clickhouse.com
</code></pre>

There's no password, so you can just press enter when prompted for one.

There are a range of datasets to play with and below is an example of a query against a table containing stock prices:

<pre><code type='click-ui' language='sql'>
SELECT symbol, max(price), sum(volume)
FROM stock
GROUP BY ALL
ORDER BY max(price) DESC
LIMIT 10;
</code></pre>

```
    ┌─symbol─┬─max(price)─┬─sum(volume)─┐
 1. │ RBAK   │    9963.24 │ 11569148200 │
 2. │ SEB    │    1670.01 │     2382900 │
 3. │ WPO    │     996.74 │    30127600 │
 4. │ NVR    │        938 │   178289600 │
 5. │ GIW    │        767 │     1306400 │
 6. │ WTM    │      702.5 │    21839600 │
 7. │ INFY   │    670.062 │   670302700 │
 8. │ QCOM   │        659 │ 28698244000 │
 9. │ MCHXP  │        585 │       58200 │
10. │ MTB    │     575.25 │   507431900 │
    └────────┴────────────┴─────────────┘
```