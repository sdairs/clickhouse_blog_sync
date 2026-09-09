---
title: "Introducing chdb Postgres extension: High-performance imports from cloud storage"
date: "2026-09-08T15:42:52.505Z"
author: "David Wheeler"
category: "Product"
excerpt: "The chdb Postgres extension brings fast imports and exports across cloud storage platforms and data formats, powered by the embedded ClickHouse engine."
---

# Introducing chdb Postgres extension: High-performance imports from cloud storage

We're happy to announce a new Postgres extension: [chdb](https://pgxn.org/dist/chdb/). This extension
expands Postgres import and export features via the [chDB library](https://clickhouse.com/docs/chdb), an
in-process [ClickHouse](https://github.com/ClickHouse/ClickHouse) engine, providing efficient, flexible conversion to
and from a wide array of [data formats](https://clickhouse.com/docs/reference/formats/index) living on your favorite cloud
storage systems.

## Benchmark {#benchmark}

And *boy howdy* do we mean *efficient*! We compared [chdb](https://pgxn.org/dist/chdb/)'s performance
importing the [NYC Taxi dataset](https://clickhouse.com/docs/get-started/quickstarts/tutorial) (1m rows, wide table) in a number of data
formats to three other Postgres extensions, all reading from a
regionally-colocated [AWS S3](https://aws.amazon.com/s3/) bucket. To the chart!

![](https://clickhouse.com/uploads/pg_chdb_sep2026_image1_dark_f0b53a5236.png)

> In order to minimize differences and to optimize for measurement of
> extension performance rather than infrastructure, the [chdb](https://pgxn.org/dist/chdb/), [pg_lake](https://github.com/Snowflake-Labs/pg_lake), and
> [pg_duckdb](https://github.com/duckdb/pg_duckdb) benchmarks ran on `r8id.xlarge` [ClickHouse Managed Postgres](https://clickhouse.com/cloud/postgres)
> services with 4 vCPUs and 32 GB RAM; the [aws_s3](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_PostgreSQL.S3Import.html) benchmark ran on a
> `db.r8g.xlarge` [AWS RDS](https://aws.amazon.com/rds/postgresql/) host, also with 4 vCPUs and 32 GB RAM. Results
> average three runs for each import. See the [benchmark source code](https://github.com/ClickHouse/pg_chdb/blob/main/dev/benchmark/) for
> details.

Of the four extensions, [chdb](https://pgxn.org/dist/chdb/) exhibits the most consistent performance.
[pg_duckdb](https://github.com/duckdb/pg_duckdb) and [pg_lake](https://github.com/Snowflake-Labs/pg_lake), both backed by [DuckDB](https://duckdb.org), take around 2-3x as long
to import data from CSV, JSON, and Parquet. Only [aws_s3](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_PostgreSQL.S3Import.html) approaches [chdb](https://pgxn.org/dist/chdb/)'s
performance, but it supports a much more limited array of data formats.

## Data formats {#data_formats}

Did we mention data formats? The [chdb](https://pgxn.org/dist/chdb/) extension can read and write a slew of
data formats --- all those that [ClickHouse itself supports](https://clickhouse.com/docs/reference/formats/index). This
table summarizes the supported data formats and compression algorithms of the
extensions we compared; note that this [chdb](https://pgxn.org/dist/chdb/) list of formats is but a subset
of the [formats it supports](https://clickhouse.com/docs/reference/formats/index):

| Extension | Compression                          | Data Formats |
| --------- | ------------------------------------ | -------------------------------- |
| aws_s3    | none                                 | Text (TSV), CSV, Postgres Binary |
| pg_lake   | gzip, zstd, snappy (Parquet only)    | CSV, JSON, Parquet               |
| pg_duckdb | gzip, zstd, snappy (Parquet only)    | CSV, JSON, Parquet               |
| chdb      | gzip, zstd, lz4, bz2, snappy, brotli | TSV, CSV, JSON, BSON, Prometheus, Protobuf, Avro, Parquet, Arrow, XML, CapnProto, Markdown, MsgPack, ORC, and [more](https://clickhouse.com/docs/reference/formats/index)! |

As [ClickHouse](https://github.com/ClickHouse/ClickHouse) and the [chDB library](https://clickhouse.com/docs/chdb) add more, the [chdb](https://pgxn.org/dist/chdb/) extension will get
them for free!

We benchmarked [chdb](https://pgxn.org/dist/chdb/) performance loading the [NYC Taxi dataset](https://clickhouse.com/docs/get-started/quickstarts/tutorial) for a number
of these formats, where it demonstrated quite consistent performance:

![](https://clickhouse.com/uploads/pg_chdb_sep2026_image2_dark_be65cf7ea0.png)

We used the [JSONCompact](https://clickhouse.com/docs/reference/formats/JSON/JSONCompact) format for compatibility with the other extensions.
Other JSON formats, such as [JSONCompactEachRow](https://clickhouse.com/docs/reference/formats/JSON/JSONCompactEachRow), will more closely
approximate the performance of the other formats.

## Usage {#usage}

The [chdb](https://pgxn.org/dist/chdb/) package ships with two extensions: a [CREATE EXTENSION](https://www.postgresql.org/docs/current/sql-createextension.html) extension
named chdb and a [hook module](https://wiki.postgresql.org/wiki/PostgresServerExtensionPoints#Hooks) named chdb_hook.

### chdb extension

The chdb extension ([docs](https://pgxn.org/dist/chdb/doc/chdb.html)) provides the `chdb_query()` function,
which executes a single chDB query. For example, this query:

<pre><code type='click-ui' language='sql'>
SELECT * FROM chdb_query($$
  SELECT * FROM s3('s3://datasets-documentation/my-test-bucket-768/some_prefix/some_file_1.csv');
$$) AS (id int, months int, days int);
</code></pre>

Outputs:

```shell
 id | months | days
----+--------+------
  1 |      2 |    3
  3 |      2 |    1
  4 |      5 |    6
(3 rows)
```

### chdb_hook module

The `chdb_hook` module ([docs](https://pgxn.org/dist/chdb/doc/chdb_hook.html)) hooks into the [COPY](https://www.postgresql.org/docs/current/sql-copy.html) command to
copy data to or from an [AWS S3](https://aws.amazon.com/s3/), [Google Cloud Storage](https://cloud.google.com/storage), [Azure Blob Storage](https://azure.microsoft.com/en-us/products/storage/blobs/), file, or http URL. This example loads records from a CSV file on S3:

<pre><code type='click-ui' language='sql'>
CREATE TABLE times (
    id     INT NOT NULL,
    months INT NOT NULL,
    days   INT NOT NULL
);

LOAD 'chdb_hook';
COPY times FROM 's3://datasets-documentation/my-test-bucket-768/some_prefix/some_file_1.csv';
</code></pre>

After which the `times` table contains the records from the file:

```shell
# SELECT * FROM times;
 id | months | days
----+--------+------
  1 |      2 |    3
  3 |      2 |    1
  4 |      5 |    6
(3 rows)
```

A [CREATE TABLE](https://www.postgresql.org/docs/current/sql-createtable.html) command may also derive its columns, and load its rows, from
such a URL. Try this one (all the URLs in this piece point to legit data files):

<pre><code type='click-ui' language='sql'>
CREATE TABLE reviews () WITH (
    copy_from = 's3://datasets-documentation/amazon_reviews/amazon_reviews_2015.snappy.parquet'
);
</code></pre>

The resulting, fully-loaded table has this structure:

|      Column       |     Type      |
|------------------ | ------------- |
| review_date       | integer       |
| marketplace       | text          |
| customer_id       | numeric(20,0) |
| review_id         | text          |
| product_id        | text          |
| product_parent    | numeric(20,0) |
| product_title     | text          |
| product_category  | text          |
| star_rating       | smallint      |
| helpful_votes     | bigint        |
| total_votes       | bigint        |
| vine              | boolean       |
| verified_purchase | boolean       |
| review_headline   | text          |
| review_body       | text          |

## Data types {#data_types}

Like [pg_clickhouse](https://clickhouse.com/docs/products/managed-postgres/extensions/pg_clickhouse/), [chdb](https://pgxn.org/dist/chdb/) relies on the [pg-clickhouse-c](https://github.com/ClickHouse/pg-clickhouse-c/) headers-only
library to convert values from ClickHouse to Postgres, including its [type mapping](https://github.com/ClickHouse/pg-clickhouse-c/#type-mapping), as in the `CREATE TABLE` example above. The current release maps
nearly all of the ClickHouse types to Postgres types and vice versa. These
mappings work most of the time; when they don't, use the `structure` option to
tell [chdb](https://pgxn.org/dist/chdb/) what type to use.

For example, [pg-clickhouse-c](https://github.com/ClickHouse/pg-clickhouse-c/) maps a Postgres JSON value to ClickHouse
String, because [ClickHouse JSON](https://clickhouse.com/docs/reference/data-types/newjson) currently recognizes only JSON *objects*,
while Postgres JSON supports objects, arrays, and JSON scalar values. But
perhaps you're confident your JSON columns contain only objects, thanks to a
check constraint:

<pre><code type='click-ui' language='sql'>
CREATE TABLE projects (
    name   TEXT PRIMARY KEY,
    meta   JSON NOT NULL CHECK (json_typeof(meta) = 'object')
);

INSERT INTO projects
VALUES ( 'chdb',   '{"status": "release"}' ),
       ( 'walrus', '{"status": "revise"}'  );
</code></pre>

To benefit from the increased flexibility and storage for object-aware storage
formats such as [Parquet JSON](https://parquet.apache.org/docs/file-format/types/logicaltypes/#json), use the `structure` option to map it to
[ClickHouse JSON](https://clickhouse.com/docs/reference/data-types/newjson):

<pre><code type='click-ui' language='sql'>
COPY projects to 'file:///tmp/projects.parquet' (
    structure 'name String, meta JSON'
);
</code></pre>

## Cloud storage URLs {#cloud_storage_urls}

The [chdb_hook](https://pgxn.org/dist/chdb/doc/chdb_hook.html) extension reads and writes to all your favorite storage
platforms. It determines the appropriate protocol from the URL scheme.

| Schemes                        | Target                               |
| ------------------------------ | ------------------------------------ |
| `file`                         | Absolute path on the Postgres server |
| `http`, `https`                | HTTP URL                             |
| `s3`                           | [AWS S3](https://aws.amazon.com/s3/)                             |
| `gs`, `gcs`, `oss`             | [Google Cloud Storage](https://cloud.google.com/storage)               |
| `az`, `azure`, `abfss`, `abfs` | [Azure Blob Storage](https://azure.microsoft.com/en-us/products/storage/blobs/) or [Azure ABFS](https://learn.microsoft.com/en-us/azure/storage/blobs/data-lake-storage-introduction-abfs-uri) |
| `hdfs`                         | [Hadoop Distributed File System](https://en.wikipedia.org/wiki/Apache_Hadoop#Overview)     |

URLs may also use a number of [wildcards](https://pgxn.org/dist/chdb/doc/chdb_hook.html#Path.Wildcards) to concurrently fetch multiple files.
Revisiting the `CREATE TABLE` example above, this command finds and imports
six files from S3:

<pre><code type='click-ui' language='sql'>
CREATE TABLE times () WITH (
    copy_from = 's3://datasets-documentation/my-test-bucket-768/{some,another}_prefix/some_file_{1..3}.csv'
);
</code></pre>

After which the `times` table contains the records from each file it loaded:

```shell
SELECT * FROM times;
 c1 | c2 | c3 
----+----+----
  1 |  2 |  3
  3 |  2 |  1
  4 |  5 |  6
  1 |  2 |  3
  3 |  2 |  1
  4 |  5 |  6
  1 |  2 |  3
  3 |  2 |  1
  4 |  5 |  6
  1 |  2 |  3
  3 |  2 |  1
  4 |  5 |  6
  1 |  2 |  3
  3 |  2 |  1
  4 |  5 |  6
  1 |  2 |  3
  3 |  2 |  1
  4 |  5 |  6
 (18 rows)
```

## Architecture {#architecture}

Support for such a vast array of data formats and cloud platforms demands a
panoply of dependencies. We avoid managing those dependencies by delegating
the problem to the [chDB library](https://clickhouse.com/docs/chdb). But loading that library into a Postgres
backend would be excessive, especially for typically occasional or periodic
tasks such as loading from a data source once a day.

Data loading extensions thus take a variety of approaches to managing the size
and complexity of such a library by a variety of means:

*   [aws_s3](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_PostgreSQL.S3Import.html) simply downloads files to the local file system and passes
    control to [COPY](https://www.postgresql.org/docs/current/sql-copy.html); hence its limitation to [AWS S3](https://aws.amazon.com/s3/) sources and the
    formats that Postgres [COPY](https://www.postgresql.org/docs/current/sql-copy.html) supports
*   [pg_duckdb](https://github.com/duckdb/pg_duckdb) embeds the [DuckDB](https://duckdb.org) engine in the Postgres backend, overkill
    for occasional [COPY](https://www.postgresql.org/docs/current/sql-copy.html) needs
*   [pg_lake](https://github.com/Snowflake-Labs/pg_lake) runs a separate [DuckDB](https://duckdb.org)-powered service and communicates with
    it via the [libpq protocol](https://www.postgresql.org/docs/current/libpq.html), which permanently consumes resources on the
    Postgres host

The [chdb extension](https://pgxn.org/dist/chdb/) adopts its own distinctive architecture: It embeds
the [chDB library](https://clickhouse.com/docs/chdb) into a separate helper application. Neither the extension
nor [chdb_hook](https://pgxn.org/dist/chdb/doc/chdb_hook.html) link chDB. Instead, they start the helper app on demand and
communicate with it via an efficient, in-memory channel: file descriptors
(`STDIN`, `STDOUT`, and `STDERR`, plus another for configuration information).

This design prevents the [chDB library](https://clickhouse.com/docs/chdb) from consuming any more resources than
necessary to carry out a single command. It also isolates the PostgreSQL
cluster itself from [out of memory](https://en.wikipedia.org/wiki/Out_of_memory) issues that using shared memory with a
[background worker](https://www.postgresql.org/docs/current/bgworker.html) would suffer.

When the helper app finishes executing a command and has passed all its
results to the backend (in [ClickHouse Native](https://clickhouse.com/docs/reference/formats/Native) format, straight from the
source), it simply cleans up and exits, leaving the server resources to the
service that most matters: PostgreSQL.

```shell
                  +-------------+
                  |   helper    |
+----------+      |    app      |      +------+
| Postgres |      | +---------+ |      | chDB |
| Backend  |<---->| |  chDB   | |<---->| Data |
+----------+      | | Library | |      +------+
                  | +---------+ |
                  +-------------+
```

## What's next? {#whats_next}

We plan to continue making [chdb](https://pgxn.org/dist/chdb/) better. Potential roadmap items include:

*   Complete type mapping. We're gradually filling in the gap between
    Postgres and ClickHouse data types, to the benefit of both [chdb](https://pgxn.org/dist/chdb/) and
    [pg_clickhouse](https://clickhouse.com/docs/products/managed-postgres/extensions/pg_clickhouse/).
*   Access control to object storage via credential chain. Currently
    credentials required to read and write object stores must be passed
    explicitly in each [chdb](https://pgxn.org/dist/chdb/) call. We'd like to allow transparent,
    server-configured credentialing to work as well.
*   Support for `COPY (query) TO`
*   Support for a `WHERE` condition on [COPY](https://www.postgresql.org/docs/current/sql-copy.html)
*   Support for all of the existing [COPY](https://www.postgresql.org/docs/current/sql-copy.html) options
*   Support for the [Iceberg](https://iceberg.apache.org) format
*   Query files directly from storage

## Give it a try {#give_it_a_try}

Find the [chdb extension](https://pgxn.org/dist/chdb/) in all the usual places, including [GitHub](https://github.com/ClickHouse/pg_chdb)
and [PGXN](https://pgxn.org/dist/chdb/). We also provide it as part of the broader [pg_clickhouse](https://clickhouse.com/docs/products/managed-postgres/extensions/pg_clickhouse/)
package on [ClickHouse Managed Postgres](https://clickhouse.com/cloud/postgres); ask your support contact to add
`chdb_hook` to your default configuration, or just connect to a superuser
account via `psql` or your favorite client, run `CREATE EXTENSION chdb;` or
`LOAD 'chdb_hook';` and get started!

---

## Get started with ClickHouse Managed Postgres today

Interested in seeing how ClickHouse Managed Postgres works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?intent=pg&loc=blog-cta-1837-get-started-with-clickhouse-managed-postgres-today-sign-up&utm_blogctaid=1837)

---