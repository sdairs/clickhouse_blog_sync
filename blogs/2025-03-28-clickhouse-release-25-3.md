---
title: "ClickHouse Release 25.3"
date: "2025-03-28T09:26:02.733Z"
author: "The ClickHouse Team"
category: "Engineering"
excerpt: "ClickHouse 25.3 is out! In this post, we highlight expanded Lakehouse catalog support with AWS Glue and Unity, the new query condition cache, automatic parallelization for external data sources, two new handy functions—and the GA of our new JSON type. "
---

# ClickHouse Release 25.3

<style>
pre div.p-2 {
    margin-bottom: 2rem;
}
</style>

Another month goes by, which means it’s time for another release! 


<p>ClickHouse version 25.3 contains 18 new features &#x1F331; 13 performance optimizations &#x1F423; 48 bug fixes &#x1F326;&#xFE0F;</p>

This release brings query support for the AWS Glue and Unity catalogs, the new query condition cache, automatic parallelization when querying S3, and new array functions!

## New Contributors

A special welcome to all the new contributors in 25.3! The growth of ClickHouse's community is humbling, and we are always grateful for the contributions that have made ClickHouse so popular.

Below are the names of the new contributors:

*Andrey Nehaychik, Arnaud Briche, Cheryl Tuquib, Didier Franc, Filipp Abapolov, Ilya Kataev, Jason Wong, Jimmy Aguilar Mena, Mark Roberts, Onkar Deshpande, Shankar Iyer, Tariq Almawash, Vico.Wu, f.abapolov, flyaways, otlxm, pheepa, rienath, talmawash*

Hint: if you’re curious how we generate this list… [here](https://gist.github.com/gingerwizard/5a9a87a39ba93b422d8640d811e269e9).

<iframe width="768" height="432" src="https://www.youtube.com/embed/iCKEzp0_Z2Q?si=h8CXcsw862qctDc5" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

You can also [view the slides from the presentation](https://presentations.clickhouse.com/2025-release-25.3/).


## AWS Glue and Unity catalogs


### Contributed by Alexander Sapin

This release adds support for more Lakehouse catalogs - AWS Glue and Unity.

You can query Apache Iceberg tables via AWS Glue by first creating a database engine:
<pre><code type='click-ui' language='sql'>
CREATE DATABASE demo_catalog 
ENGINE = DataLakeCatalog
SETTINGS catalog_type = 'glue', region = 'us-west-2',
    aws_access_key_id = 'AKIA...', aws_secret_access_key = '...';
</code></pre>

And then querying the data:

<pre><code type='click-ui' language='sql'>
SHOW TABLES 
FROM demo_catalog;

SELECT * 
FROM "demo_catalog"."db.table";
</code></pre>

There’s support for Apache Iceberg and Delta Lake tables via the Unit catalog. Again, you’ll need to create a database engine:

<pre><code type='click-ui' language='sql'>
CREATE DATABASE unity_demo
ENGINE = DataLakeCatalog(
    'https://endpoint.cloud.databricks.com/api/2.1/unity-catalog')
SETTINGS catalog_type = 'unity',
    warehouse = 'workspace', catalog_credential = '...'
</code></pre>

And then you can query it like  a normal table:

<pre><code type='click-ui' language='sql'>
SHOW TABLES 
FROM unity_demo;

SELECT * 
FROM "unity_demo"."db.table";
</code>
</pre>

## JSON data type is production-ready


### Contributed by Pavel Kruglov

About 1.5 years ago, we weren’t happy with our JSON implementation, so we [returned to the drawing board](https://github.com/ClickHouse/ClickHouse/issues/54864). A [year later](https://clickhouse.com/blog/clickhouse-release-24-08#json-data-type), Pavel delivered a completely reimagined implementation for storing JSON on top of columnar storage. You can read about the journey in [How we built a new powerful JSON data type for ClickHouse](https://clickhouse.com/blog/a-new-powerful-json-data-type-for-clickhouse).

The result: unmatched performance, compression, and usability—far beyond anything offered by existing JSON data stores: [The billion docs JSON Challenge: ClickHouse vs. MongoDB, Elasticsearch, and more](https://clickhouse.com/blog/json-bench-clickhouse-vs-mongodb-elasticsearch-duckdb-postgresql).

**TL;DR:** As far as we know, this is the first time columnar storage has been implemented *right* for semi-structured data. ClickHouse’s new JSON storage is:



* More compact than compressed files on disk
* Thousands of times faster than traditional JSON stores like MongoDB and as easy to use
* The only JSON store that fully supports dynamic JSON paths *without* forcing them into a least common type

Our new [JSON type](https://clickhouse.com/docs/sql-reference/data-types/newjson) is now production-ready and fully integrated with ClickHouse’s query acceleration features. Read more in [Accelerating ClickHouse queries on JSON data for faster Bluesky insights](https://clickhouse.com/blog/accelerating-clickhouse-json-queries-for-fast-bluesky-dashboards).

We also created [JSONBench](https://jsonbench.com/), the first fair, vendor-neutral benchmark focused on analytics over JSON documents. Just try searching for anything comparable—there’s nothing else like it.

Finally, the core building blocks—[Variant](https://clickhouse.com/blog/clickhouse-release-24-01#variant-type) and [Dynamic](https://clickhouse.com/blog/clickhouse-release-24-05#dynamic-data-type) types—are now production-ready as standalone features. They power our JSON implementation and pave the way for future support of semi-structured formats like XML, YAML, and more.

We can’t wait to see what you build with it. Give it a try—and if you’re curious about what’s coming next for JSON in ClickHouse, [check out our roadmap](https://github.com/ClickHouse/ClickHouse/issues/68428).

## Query condition cache


### Contributed by ZhongYuanKai

This release adds the [query condition cache](https://clickhouse.com/docs/operations/query-condition-cache), which accelerates repeatedly run queries—such as in dashboarding or observability scenarios—with selective WHERE clauses that don’t benefit from the primary index. It’s especially effective when the same condition is reused across different queries.

For example, the following query counts all [Bluesky](https://bsky.social/about) posts that include the pretzel emoji:
<pre>
<code type='click-ui' language='sql'>
SELECT count()
FROM bluesky
WHERE (data.kind = 'commit')
  AND (data.commit.operation = 'create')
  AND (data.commit.collection = 'app.bsky.feed.post')
  AND (data.commit.record.text LIKE '%&#x1F968;%');
</code>
</pre>

This query returns the top languages for pretzel emoji posts:
<pre>
<code type='click-ui' language='sql'>
SELECT
    arrayJoin(CAST(data.commit.record.langs, 'Array(String)')) AS language,
    count() AS count
FROM bluesky
WHERE (data.kind = 'commit')
  AND (data.commit.operation = 'create')
  AND (data.commit.collection = 'app.bsky.feed.post')
  AND (data.commit.record.text LIKE '%&#x1F968;%')
GROUP BY language
ORDER BY count DESC;
</code>
</pre>

Both queries share the same predicate:
<pre>
<code type='click-ui' language='sql'>
WHERE (data.kind = 'commit')
  AND (data.commit.operation = 'create')
  AND (data.commit.collection = 'app.bsky.feed.post')
  AND (data.commit.record.text LIKE '%&#x1F968;%')
</code>
</pre>

With the query condition cache, the scan result from the first query is cached and reused by the second—resulting in a significant speedup.
You can find results for the queries above, performance metrics, and a deep dive into how the query condition cache works in our [dedicated blog post](https://clickhouse.com/blog/introducing-the-clickhouse-query-condition-cache).

## Automatic parallelization for external data


### Contributed by Konstantin Bogdanov

In the previous section, we saw how to count the number of pretzel emoji mentions when querying the BlueSky dataset loaded into a `MergeTree` table. Let’s now see how long it takes to query that data directly on S3:

<pre><code type='click-ui' language='sql'>
SELECT count()
FROM s3('https://clickhouse-public-datasets.s3.amazonaws.com/bluesky/file_{0001..0100}.json.gz', 'JSONAsObject')
WHERE (json.kind = 'commit') 
AND (json.commit.operation = 'create') 
AND (json.commit.collection = 'app.bsky.feed.post') 
AND (json.commit.record.text LIKE '%&#x1F968;%')
SETTINGS 
  input_format_allow_errors_num = 100, 
  input_format_allow_errors_ratio = 1;
</code></pre>

<pre><code type='click-ui' language='text' show_line_numbers='false'>
┌─count()─┐
│      69 │
└─────────┘

1 row in set. Elapsed: 64.902 sec. Processed 100.00 million rows, 13.35 GB (1.54 million rows/s., 205.75 MB/s.)
Peak memory usage: 2.68 GiB.
</code></pre>

Just over 1 minute! I have a ClickHouse Cloud cluster with 10 nodes, and I can spread the reading of the files across all the nodes by using the `s3Cluster` table function:

<pre><code type='click-ui' language='sql'>
SELECT count()
FROM s3Cluster(default, 'https://clickhouse-public-datasets.s3.amazonaws.com/bluesky/file_{0001..0100}.json.gz', 'JSONAsObject')
WHERE (json.kind = 'commit') 
AND (json.commit.operation = 'create') 
AND (json.commit.collection = 'app.bsky.feed.post') 
AND (json.commit.record.text LIKE '%&#x1F968;%')
SETTINGS 
  input_format_allow_errors_num = 100, 
  input_format_allow_errors_ratio = 1;
</code></pre>

Let’s see how long this takes!
<pre><code type='click-ui' language='text' show_line_numbers='false'>
┌─count()─┐
│      69 │
└─────────┘

1 row in set. Elapsed: 16.689 sec. Processed 100.00 million rows, 13.38 GB (5.99 million rows/s., 801.86 MB/s.)
Peak memory usage: 2.06 GiB.
</code></pre>

<!-----



Conversion time: 0.536 seconds.


Using this Markdown file:

1. Paste this output into your source file.
2. See the notes and action items below regarding this conversion run.
3. Check the rendered output (headings, lists, code blocks, tables) for proper
   formatting and use a linkchecker before you publish this page.

Conversion notes:

* Docs to Markdown version 1.0β44
* Fri Mar 28 2025 02:39:30 GMT-0700 (PDT)
* Source doc: 25.3 Release Blog Post
* This is a partial selection. Check to make sure intra-doc links work.
----->


That’s cut the time down by 4x - not quite linear, but not too bad!

`…Cluster` functions like [s3Cluster](https://clickhouse.com/docs/sql-reference/table-functions/s3Cluster), [azureBlobStorageCluster](https://clickhouse.com/docs/sql-reference/table-functions/azureBlobStorageCluster), [deltaLakeCluster](https://clickhouse.com/docs/sql-reference/table-functions/deltalakeCluster), [icebergCluster](https://clickhouse.com/docs/sql-reference/table-functions/icebergCluster), and [more](https://clickhouse.com/docs/sql-reference/table-functions) distribute work similarly to [parallel replicas](https://clickhouse.com/docs/deployment-guides/parallel-replicas)—but with a key difference: parallel replicas split work by [granule](https://clickhouse.com/docs/guides/best-practices/sparse-primary-indexes#data-is-organized-into-granules-for-parallel-data-processing) ranges, while `…Cluster` functions operate at the file level. We illustrate this below for our example query above with a diagram:

![Blog-release-25.3.001.png](https://clickhouse.com/uploads/Blog_release_25_3_001_e098f3d404.png)

The initiator server—the one receiving the query—resolves the file glob pattern, connects to all other servers, and dynamically dispatches files. The other servers request files from the initiator as they finish processing, repeating until all files are handled. Each server uses N parallel streams (based on its CPU cores) to read and process different ranges within each file. All partial results are then merged and streamed back to the initiator, which assembles the final result. Due to the overhead of coordination and merging partial results, the speedup isn’t always linear.

Starting from 25.3, you don’t need to call the `…Cluster` versions of remote data access functions to get distributed processing. Instead, ClickHouse will automatically distribute the work when called from a cluster if you have enabled parallel replicas. 

If you don’t want distributed processing, you can disable it by setting the following property:

<pre><code type='click-ui' language='sql'>
SET parallel_replicas_for_cluster_engines = 0;
</code></pre>

## arraySymmetricDifference


### Contributed by Filipp Abapolov

ClickHouse has an extensive collection of array functions that can solve various problems. One such problem is determining which elements in a pair of arrays exist in one array but not the other.

We can work this out by computing the union of the array and then removing any elements that are contained in the intersection of the arrays:

<pre><code type='click-ui' language='sql'>
WITH
    [1, 2, 3] AS a,
    [2, 3, 4] AS b
SELECT
    arrayUnion(a, b) AS union,
    arrayIntersect(a, b) AS intersect,
    arrayFilter(x -> (NOT has(intersect, x)), union) AS unionButNotIntersect;
</code></pre>

This works fine, but we thought it’d be cool if you could do this with a single function. Enter arraySymmetricDifference:

<pre><code type='click-ui' language='sql'>
WITH
    [1, 2, 3] AS a,
    [2, 3, 4] AS b
SELECT
    arrayUnion(a, b) AS union,
    arrayIntersect(a, b) AS intersect,
    arrayFilter(x -> (NOT has(intersect, x)), union) AS unionNotIntersect,
    arraySymmetricDifference(a, b) AS symmetricDifference;
</code></pre>

<pre><code type='click-ui' language='text' show_line_numbers='false'>
┌─union─────┬─intersect─┬─unionNotIntersect─┬─symmetricDifference─┐
│ [3,2,1,4] │ [2,3]     │ [1,4]             │ [1,4]               │
└───────────┴───────────┴───────────────────┴─────────────────────┘
</code></pre>

## estimateCompressionRatio


### Contributed by Tariq Almawash

Another function added in this release is `estimateCompressionRatio`, which can assess the potential impact of applying different compression algorithms to a column.

> Remember from the [data compression section of Why is ClickHouse fast?](https://clickhouse.com/docs/concepts/why-clickhouse-is-so-fast#storage-layer-data-compression) that ClickHouse compresses data at the column level.

We can see how it works by applying compression algorithms to the `CounterID` column in the `hits` table on [play.clickhouse.com](play.clickhouse.com):
<pre><code type='click-ui' language='sql'>
SELECT round(estimateCompressionRatio('NONE')(CounterID)) AS none,
       round(estimateCompressionRatio('LZ4')(CounterID)) AS lz4,
       round(estimateCompressionRatio('ZSTD')(CounterID)) AS zstd,
       round(estimateCompressionRatio('ZSTD(3)')(CounterID)) AS zstd3,
       round(estimateCompressionRatio('GCD')(CounterID)) AS gcd,
       round(estimateCompressionRatio('Gorilla')(CounterID)) AS gorilla,
       round(estimateCompressionRatio('Gorilla, ZSTD')(CounterID)) AS mix
FROM hits
FORMAT PrettyMonoBlock;
</code></pre>

We can see the output of the query below:
<pre><code type='click-ui' language='text' show_line_numbers='false'>
┏━━━━━━┳━━━━━┳━━━━━━┳━━━━━━━┳━━━━━┳━━━━━━━━━┳━━━━━━┓
┃ none ┃ lz4 ┃ zstd ┃ zstd3 ┃ gcd ┃ gorilla ┃  mix ┃
┡━━━━━━╇━━━━━╇━━━━━━╇━━━━━━━╇━━━━━╇━━━━━━━━━╇━━━━━━┩
│    1 │ 248 │ 4974 │  5110 │   1 │      32 │ 6682 │
└──────┴─────┴──────┴───────┴─────┴─────────┴──────┘
</code></pre>

The specialized codecs (`GCD` and `Gorilla`) have little impact. The more generic codecs, `LZ4` and, in particular, `ZSTD,` significantly reduce the space taken. We can also adjust the level of `ZSTD`, where a higher value means more compression. The higher the compression level, the longer it takes to compress a value, increasing the time for write operations.

We can also use this function on data that hasn’t been ingested into ClickHouse. The following query returns the schema of an Amazon Reviews Parquet file stored in an S3 bucket:

<pre><code type='click-ui' language='sql'>
DESCRIBE  s3(
  'https://datasets-documentation.s3.eu-west-3.amazonaws.com' ||
  '/amazon_reviews/amazon_reviews_2015.snappy.parquet'
)
SETTINGS describe_compact_output=1;
</code></pre>


<pre><code type='click-ui' language='text' show_line_numbers='false'>
┌─name──────────────┬─type─────────────┐
│ review_date       │ Nullable(UInt16) │
│ marketplace       │ Nullable(String) │
│ customer_id       │ Nullable(UInt64) │
│ review_id         │ Nullable(String) │
│ product_id        │ Nullable(String) │
│ product_parent    │ Nullable(UInt64) │
│ product_title     │ Nullable(String) │
│ product_category  │ Nullable(String) │
│ star_rating       │ Nullable(UInt8)  │
│ helpful_votes     │ Nullable(UInt32) │
│ total_votes       │ Nullable(UInt32) │
│ vine              │ Nullable(Bool)   │
│ verified_purchase │ Nullable(Bool)   │
│ review_headline   │ Nullable(String) │
│ review_body       │ Nullable(String) │
└───────────────────┴──────────────────┘
</code></pre>

The following query computes the compression ratio of the `product_category` column:

<pre><code type='click-ui' language='sql'>
SELECT round(estimateCompressionRatio(‘NONE’)(product_category)) AS none,
          round(estimateCompressionRatio(‘LZ4’)(product_category)) AS lz4,
          round(estimateCompressionRatio(‘ZSTD’)(product_category)) AS zstd
FROM
 s3(
  'https://datasets-documentation.s3.eu-west-3.amazonaws.com' ||
  '/amazon_reviews/amazon_reviews_2015.snappy.parquet'
);
</code></pre>


<pre><code type='click-ui' language='text' show_line_numbers='false'>
┌─none─┬─lz4─┬─zstd─┐
│    1 │ 227 │ 1750 │
└──────┴─────┴──────┘
</code></pre>

We can also see how well the data will be compressed if we import the data into a different column type:

<pre><code type='click-ui' language='sql'>
SELECT round(estimateCompressionRatio(‘NONE’)(product_category)) AS none,
          round(estimateCompressionRatio(‘LZ4’)(product_category)) AS lz4,
          round(estimateCompressionRatio(‘ZSTD’)(product_category)) AS zstd
FROM
 s3(
  'https://datasets-documentation.s3.eu-west-3.amazonaws.com' ||
  '/amazon_reviews/amazon_reviews_2015.snappy.parquet',
  ‘Parquet’,
  ‘product_category LowCardinality(String)’
);
</code></pre>

<pre><code type='click-ui' language='text' show_line_numbers='false'>
┌─none─┬─lz4─┬─zstd─┐
│    1 │ 226 │ 1691 │
└──────┴─────┴──────┘
</code></pre>

Or if we change the sort order of the data:

<pre><code type='click-ui' language='sql'>
SELECT round(estimateCompressionRatio(‘NONE’)(product_category)) AS none,
          round(estimateCompressionRatio(‘LZ4’)(product_category)) AS lz4,
          round(estimateCompressionRatio(‘ZSTD’)(product_category)) AS zstd
FROM (
  SELECT * 
  FROM
   s3(
    'https://datasets-documentation.s3.eu-west-3.amazonaws.com' ||
    '/amazon_reviews/amazon_reviews_2015.snappy.parquet',
    ‘Parquet’,
    ‘product_category LowCardinality(String)’
  )
  ORDER BY product_category
);
</code></pre>

<pre><code type='click-ui' language='text' show_line_numbers='false'>
┌─none─┬─lz4─┬─zstd─┐
│    1 │ 252 │ 7097 │
└──────┴─────┴──────┘
</code></pre>