---
title: "ClickHouse Release 25.9"
date: "2025-10-01T09:15:05.163Z"
author: "The ClickHouse Team"
category: "Engineering"
excerpt: "ClickHouse 25.9 is available. In this post, you will learn about new features, including a new text index, join reordering, streaming for secondary indices, and more."
---

# ClickHouse Release 25.9

Another month goes by, which means it’s time for another release! 

<p>ClickHouse version 25.9 contains 25 new features &#127822; 22 performance optimizations &#127809; 83 bug fixes &#127807;</p>

This release brings automatic global join reordering, streaming for secondary indices, a new text index, and more!

## New contributors

A special welcome to all the new contributors in 25.9! The growth of ClickHouse's community is humbling, and we are always grateful for the contributions that have made ClickHouse so popular.

Below are the names of the new contributors:

*Aly Kafoury, Christian Endres, Dmitry Prokofyev, Kaviraj, Max Justus Spransy, Mikhail Kuzmin, Sergio de Cristofaro, Shruti Jain, c-end, dakang, jskong1124, polako, rajatmohan22, restrry, shruti-jain11, somrat.dutta, travis, yanglongwei*

Hint: if you’re curious how we generate this list… [here](https://gist.github.com/gingerwizard/5a9a87a39ba93b422d8640d811e269e9).

<iframe width="768" height="432" src="https://www.youtube.com/embed/LCHEPNXo8kQ?si=B7To0xp0HrUdRIwJ" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

You can also [view the slides from the presentation](https://presentations.clickhouse.com/2025-release-25.9/).

## Join reordering

### Contributed by Vladimir Cherkasov

A long-standing dream for many ClickHouse users has come true in this release: **automatic global join reordering**.

ClickHouse can now reorder complex join graphs spanning dozens of tables, across the most common join [types](https://clickhouse.com/blog/clickhouse-fully-supports-joins-part1) (inner, left/right outer, cross, semi, anti). Automatic global join reordering uses the fact that joins between more than two tables are [associative](https://en.wikipedia.org/wiki/Associative_property). 

### Why join order matters

For example, a database may choose to first join tables `A` and `B`, and then the result of that with table `C`: 


<img src="/uploads/0_25_9_8dc99321f7.png" style="width:40%">

Or it may first join `B` and `C`, and the result of that with table `A`:

<img src="/uploads/1_25_9_8d708bb7bd.png" style="width:40%">

Or it first joins `A` and `C`, and the result of that with `B`:

<img src="/uploads/2_25_9_192de5c4c1.png" style="width:40%">

The result will be the same in all three cases. 

The more tables are joined, the more important the global join order becomes. 

In some cases, **good and bad join orders can differ by many orders of magnitude in runtime**! 

To see why join order matters so much, let’s briefly recap how ClickHouse executes joins.

### How ClickHouse joins work

As a brief recap: ClickHouse’s [fastest](https://clickhouse.com/blog/clickhouse-fully-supports-joins-how-to-choose-the-right-algorithm-part5#imdb-large-join-runs) join algorithms, including the default [**parallel hash join**](https://clickhouse.com/blog/clickhouse-fully-supports-joins-hash-joins-part2#parallel-hash-join), have two phases:

1. **Build phase:** loading the right-hand side table into an in-memory hash table(s).

2. **Probe phase:** streaming the left-hand side table and performing lookups into the hash table(s).

![3_25.9.png](https://clickhouse.com/uploads/3_25_9_abe186190e.png)

> Because the build side is loaded into memory upfront, placing the smaller table on the right-hand side of the join is usually far more efficient.

Other [join algorithms](https://clickhouse.com/blog/clickhouse-fully-supports-joins-how-to-choose-the-right-algorithm-part5#overview-of-clickhouse-join-algorithms), such as the [**partial merge join**](https://clickhouse.com/blog/clickhouse-fully-supports-joins-full-sort-partial-merge-part3#partial-merge-join) (which uses external sorting rather than in-memory hash tables), also have build and probe phases. Here, too, placing the smaller table on the build side makes execution faster.

### Local join reordering

Automatic **local** join reordering for two joined tables was first [introduced](https://clickhouse.com/blog/clickhouse-release-24-12#automatic-join-reordering) in 24.12. This optimization moves the small of both tables to the right (**build**) side and therefore reduces the effort needed to build the hash table.

### Global join reordering

In 25.9, ClickHouse introduced **global** join reordering to determine the optimal join order (build vs probe) of more than two tables during query optimization. 

![4_25.9.png](https://clickhouse.com/uploads/4_25_9_a2eacad52f.png)

Global join order optimization is much more challenging than local optimization. As the number of possible join orders grows exponentially with the number of joined tables, ClickHouse cannot explore the search space exhaustively. The database instead runs a greedy optimization algorithm to converge to a “good enough” join order quickly.

The optimization algorithm also requires cardinality estimations of the join columns - i.e. how many rows are two joined tables expected to contain (considering additional WHERE filters on them). The cardinality estimations are provided using row count estimates from the storage engines or [column statistics](https://clickhouse.com/docs/engines/table-engines/mergetree-family/mergetree#available-types-of-column-statistics) (if available). 

As of today, column statistics must be created manually (see our example below). We plan to create column statistics for new tables automatically in future versions of ClickHouse.

### Controlling join reordering

Two new settings control the global join reordering:

* [query_plan_optimize_join_order_limit](https://clickhouse.com/docs/operations/settings/settings#query_plan_optimize_join_order_limit) - Value is the max number of tables to apply the reordering to.

* [allow_statistics_optimize](https://clickhouse.com/docs/operations/settings/settings#allow_statistics_optimize) - Allows using statistics to optimize join order

### Benchmarks: TPC-H results

Let’s see it in action on the classic [**TPC-H** join benchmark](https://clickhouse.com/docs/getting-started/example-datasets/tpch). 

To evaluate the impact of global join reordering with column statistics, we created two versions of the TPC-H schema (scale factor 100) on an AWS EC2 m6i.8xlarge instance (32 vCPUs, 128 GiB RAM):

1. **Without statistics:** the 8 TPC-H tables created with the [default DDL](https://clickhouse.com/docs/getting-started/example-datasets/tpch#data-generation-and-import).

2. **With statistics:** the same 8 tables [extended with column statistics](https://pastila.nl/?01031010/7475d7ba575a41d9fd86eaaff97cb201#SGYcmaof4DoQzewNH3tBKA==).

Once those tables are created, we can use the [commands in this script](https://pastila.nl/?003e78ba/abfe6ec788901e3755ade78c516878c5#/d8OIS+RA2PIkS+N9Sw9bQ==) to load the data.

> If you want to follow along, the commands to create and load the tables are included in the links above.

<pre><code type='click-ui' language='sql'>
CREATE DATABASE tpch_no_stats;
USE tpch_no_stats;
-- Create the 8 tables with the default DDL
-- Load data 
</code></pre>

<pre><code type='click-ui' language='sql'>
CREATE DATABASE tpch_stats;
USE tpch_stats;
-- Create the 8 tables with extended DDL (with column statistics)
-- Load data
</code></pre>

We then ran the following TPC-H query, which contains a join across six tables, as our test query:

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
  revenue DESC;
</code></pre>

First, we executed the query on the tables **without statistics**:

<pre><code type='click-ui' language='sql'>
USE tpch_no_stats;
SET query_plan_optimize_join_order_limit = 10;
SET allow_statistics_optimize = 1;

-- test_query
</code></pre>

```text
   ┌─n_name────┬─────────revenue─┐
1. │ VIETNAM   │  5310749966.867 │
2. │ INDIA     │ 5296094837.7503 │
3. │ JAPAN     │ 5282184528.8254 │
4. │ CHINA     │ 5270934901.5602 │
5. │ INDONESIA │ 5270340980.4608 │
   └───────────┴─────────────────┘

5 rows in set. Elapsed: 3903.678 sec. Processed 766.04 million rows, 16.03 GB (196.23 thousand rows/s., 4.11 MB/s.)
Peak memory usage: 99.12 GiB.
```

<p>
That took over one hour! &#x1F40C; And used 99 GiB of main memory.
</p>

Then we repeated the same query on the tables **with statistics**:

<pre><code type='click-ui' language='sql'>
USE tpch_stats;
SET query_plan_optimize_join_order_limit = 10;
SET allow_statistics_optimize = 1;

-- test_query
</code></pre>

```text
Query id: 5c1db564-86d0-46c6-9bbd-e5559ccb0355

   ┌─n_name────┬─────────revenue─┐
1. │ VIETNAM   │  5310749966.867 │
2. │ INDIA     │ 5296094837.7503 │
3. │ JAPAN     │ 5282184528.8254 │
4. │ CHINA     │ 5270934901.5602 │
5. │ INDONESIA │ 5270340980.4608 │
   └───────────┴─────────────────┘

5 rows in set. Elapsed: 2.702 sec. Processed 638.85 million rows, 14.76 GB (236.44 million rows/s., 5.46 GB/s.)
Peak memory usage: 3.94 GiB.
```

Now it took 2.7 seconds. **~1,450× faster than before.** With ~25x less memory usage.

### What’s next for join reordering

This is just the **first step** for global join reordering in ClickHouse. Today, it requires manually created statistics. The next steps will include:

* **Automatic statistics creation** — removing the need for manual setup.

* **Support more join types (like outer joins) and joins over subqueries**

* **More powerful join reordering algorithms** — handling larger join graphs and more complex scenarios.

Stay tuned.

## Streaming for secondary indices

### Contributed by Amos Bird

Before ClickHouse 25.9, **secondary indices** (e.g., minmax, set, bloom filter, vector, text) were evaluated *before* reading the underlying table data. This sequential process had several drawbacks:

* **Inefficient with LIMIT:** Even if a query stopped early, ClickHouse still had to scan the entire index upfront.
* **Startup delay:** Index analysis happened before query execution began.
* **Heavy index scans:** In some cases, scanning the index cost more than processing the actual data.

ClickHouse 25.9 eliminates these drawbacks by **interleaving data reads with index checks**. When ClickHouse is about to read a table data granule, it first checks the corresponding secondary index entry. If the index indicates the granule can be skipped, it's never read. Otherwise, the granule is read and processed while scanning continues on subsequent granules.

This concurrent execution eliminates startup delay and avoids wasted work. For queries with LIMIT, ClickHouse halts index checks and granule reads as soon as the result is complete.

**Results:** In testing with a 1 billion row table and a 2+ GiB bloom filter index, a simple LIMIT 1 query was **over 4× faster** (2.4s vs 10s) with streaming indices enabled.

This feature is controlled by the [use_skip_indexes_on_data_read](https://clickhouse.com/docs/operations/settings/settings#use_skip_indexes_on_data_read) setting.

**[Read the full deep-dive on streaming secondary indices →](https://clickhouse.com/blog/streaming-secondary-indices)**

##  A new text index

### Contributed by Anton Popov, Elmi Ahmadov, Jimmy Aguilar Mena

Since publishing [our blog on reworking full-text search in August 2025](https://clickhouse.com/blog/clickhouse-full-text-search), we’ve learned even more from extended testing. Some approaches we thought were ‘done’ turned out to be stepping stones toward an even better design. We view this as part of ClickHouse’s DNA: we share early, we test rigorously, and we continue to improve until we’re confident that we’ve delivered the fastest solution possible.

The previous FST-based implementation optimized space but was inefficient because it required loading large chunks of data into memory and wasn’t structured around skip index granules, making query analysis more difficult. 

The new design makes ClickHouse's text index streaming-friendly and structures data around skip index granules for more efficient queries. In ClickHouse 25.9, we're shipping this new experimental text index to provide more efficient and reliable full-text search.

To enable the text index, we need to set the following:

<pre><code type='click-ui' language='sql'>
SET allow_experimental_full_text_index;
</code></pre>

We’ll use the [Hacker News example dataset](https://clickhouse.com/docs/getting-started/example-datasets/hacker-news) to explore this feature. We can download the CSV file like this:

<pre><code type='click-ui' language='bash'>
wget https://datasets-documentation.s3.eu-west-3.amazonaws.com/hackernews/hacknernews.csv.gz
</code></pre>

Next, let’s create a table with a text index on the `text` column:

<pre><code type='click-ui' language='sql'>
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
    TYPE text(tokenizer = 'default')
    GRANULARITY 128
)
ENGINE = MergeTree
ORDER BY time;
</code></pre>

Now, we can ingest the data:

<pre><code type='click-ui' language='sql'>
INSERT INTO hackernews 
SELECT *
FROM file('hacknernews.csv.gz', CSVWithNames);
</code></pre>

Let’s check how many records the table contains:

<pre><code type='click-ui' language='sql'>
SELECT count()
FROM hackernews;
</code></pre>

```text
┌──count()─┐
│ 28737557 │ -- 28.74 million
└──────────┘
```

We’ve got just under 30 million records to work with.

Now let’s see how to query the `text` column. The [hasToken](https://clickhouse.com/docs/sql-reference/functions/string-search-functions#hastoken) function will use a text index if one exists. [searchAll](https://clickhouse.com/docs/sql-reference/functions/string-search-functions#searchall) and [searchAny](https://clickhouse.com/docs/sql-reference/functions/string-search-functions#searchany) will only work if the field has a text index.

To find the users who post the most about OpenAI, we could write the following query:

<pre><code type='click-ui' language='sql'>
select by, count()
FROM hackernews
WHERE hasToken(text, 'OpenAI')
GROUP BY ALL
ORDER BY count() DESC
LIMIT 10;
</code></pre>

```text
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

10 rows in set. Elapsed: 0.026 sec.
```

If we run that same query on a table without a text index, it takes about 10x longer:

```text
10 rows in set. Elapsed: 1.545 sec. Processed 27.81 million rows, 9.47 GB (17.99 million rows/s., 6.13 GB/s.)
Peak memory usage: 172.15 MiB.
```

We could also write the following query to find the users who posted the most messages that include both OpenAI and Google:

<pre><code type='click-ui' language='sql'>
select by, count()
FROM hackernews
WHERE searchAll(text, ['OpenAI', 'Google'])
GROUP BY ALL
ORDER BY count() DESC
LIMIT 10;
</code></pre>

```text
┌─by──────────────┬─count()─┐
│ thejash         │      17 │
│ boulos          │       8 │
│ p1esk           │       6 │
│ sillysaurusx    │       5 │
│ colah3          │       5 │
│ nl              │       5 │
│ rvz             │       4 │
│ Voloskaya       │       4 │
│ visarga         │       4 │
│ YeGoblynQueenne │       4 │
└─────────────────┴─────────┘

10 rows in set. Elapsed: 0.012 sec.
```

## Data lake improvements

### Contributed by Konstantin Vedernikov, Smita Kulkarni

ClickHouse 25.9 sees further support for data lakes, including:

* Support for the `ALTER UPDATE` and `DROP TABLE` clauses for Apache Iceberg  
* A new `iceberg_metadata_log` system table  
* ORC and Avro for Apache Iceberg data files  
* Unity catalog on Azure  
* Distributed `INSERT SELECT` for data lakes

## arrayExcept

### Contributed by Joanna Hulboj

ClickHouse 25.9 introduces the `arrayExcept` function, which enables you to determine the difference between two arrays. An example is shown below:

<pre><code type='click-ui' language='sql'>
SELECT arrayExcept([1, 2, 3, 4], [1, 3, 5]) AS res;
</code></pre>

```text
┌─res───┐
│ [2,4] │
└───────┘
```

##  Boolean settings

### Contributed by Thraeka

ClickHouse 25.9 also allows you to define boolean settings without specifying an argument. This means that we can make `DESCRIBE` output compact, like this:

<pre><code type='click-ui' language='sql'>
SET describe_compact_output;
</code></pre>

And no longer need to explicitly specify that it’s `true`, as we did before 25.9:

<pre><code type='click-ui' language='sql'>
SET describe_compact_output = true;
</code></pre>

To disable a setting, we still need to provide the argument as `false`.

## Storage Class specification for S3

### Contributed by Alexander Sapin

ClickHouse 25.9 allows you to specify the [AWS S3 storage class](https://docs.aws.amazon.com/AmazonS3/latest/userguide/storage-class-intro.html) when using the S3 table engine or table function.

For example, we could use [intelligent tiering](https://docs.aws.amazon.com/AmazonS3/latest/userguide/storage-class-intro.html) if we want AWS to optimize storage costs by automatically moving data to the most cost-effective access tier.

<pre><code type='click-ui' language='sql'>
CREATE TABLE test (s String)
ENGINE = S3('s3://mybucket/test.parquet',
            storage_class_name = 'INTELLIGENT_TIERING');

INSERT INTO test VALUES ('Hello');
</code></pre>

<pre><code type='click-ui' language='sql'>
INSERT INTO FUNCTION s3('s3://mybucket/test.parquet',
            storage_class_name = 'INTELLIGENT_TIERING') 
VALUES('test');
</code></pre>
