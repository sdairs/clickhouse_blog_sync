---
title: "ClickHouse Release 25.8"
date: "2025-09-04T12:47:08.836Z"
author: "ClickHouse Team"
category: "Engineering"
excerpt: "ClickHouse 25.8 is available. In this post, you will learn about new features, including a new Parquet reader and Arrow Flight integration."
---

# ClickHouse Release 25.8

Another month goes by, which means it’s time for another release! 

<p>ClickHouse version 25.8 contains 45 new features &#127803; 47 performance optimizations &#127949; 119 bug fixes &#128029;</p>

This release brings a new, faster Parquet reader, Data Lake improvements, writes with Hive-style partitioning, initial PromQL support, and more!

## New contributors

A special welcome to all the new contributors in 25.8! The growth of ClickHouse's community is humbling, and we are always grateful for the contributions that have made ClickHouse so popular.

Below are the names of the new contributors:

*Alexei Fedotov, Bulat Sharipov, Casey Leask, Chris Crane, Dan Checkoway, Denny [DBA at Innervate], Evgenii Leko, Felix Mueller, Huanlin Xiao, Konstantin Dorichev, László Várady, Maruth Goyal, Nick, Rajakavitha Kodhandapani, Renat Bilalov, Rishabh Bhardwaj, RuS2m, Sahith Vibudhi, Sam Radovich, Shaohua Wang, Somrat Dutta, Stephen Chi, Tom Quist, Vladislav Gnezdilov, Vrishab V Srivatsa, Yunchi Pang, Zakhar Kravchuk, Zypperia, ackingliu, albertchae, alistairjevans, craigfinnelly, cuiyanxiang, demko, dorki, mlorek, rickykwokmeraki, romainsalles, saurabhojha, somratdutta, ssive7b, sunningli, xiaohuanlin, ylw510*

Hint: if you’re curious how we generate this list… [here](https://gist.github.com/gingerwizard/5a9a87a39ba93b422d8640d811e269e9).

<iframe width="768" height="432" src="https://www.youtube.com/embed/HB_-vji9RB0?si=3vmn1ore9-6l5GLA" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

You can also [view the slides from the presentation](https://presentations.clickhouse.com/2025-release-25.8/).

##  Parquet reader v3

### Contributed by Michael Kolupaev

ClickHouse is built for its native **MergeTree** tables, but it can also query over 70 external formats like **Parquet, JSON, CSV, and Arrow** directly, no ingestion required. Where most databases force you to load files into a native format first, ClickHouse skips that step and still gives you full SQL: joins, window functions, 170+ aggregate functions, and more.

Among these formats, **Parquet plays a special role** as the storage layer behind modern Lakehouse table formats like **Iceberg** and **Delta Lake**. That’s why in recent years we’ve heavily optimized for Parquet, as part of our mission to make ClickHouse the fastest engine in the world for querying it at scale.

This release introduces a new and faster **native Parquet reader** in ClickHouse (currently experimental). Until now, the previous non-native reader relied on the [Apache Arrow library](https://github.com/apache/arrow/tree/main/cpp): Parquet files were parsed into [Arrow](https://arrow.apache.org/) format, and [copied](https://github.com/ClickHouse/ClickHouse/blob/775b7d30c814bf9f28614b472d4ae8c10b39fa92/src/Processors/Formats/Impl/ArrowColumnToCHColumn.cpp) (in a streaming fashion) into ClickHouse’s native in-memory format for execution. The new native reader removes that extra layer, reading Parquet files **directly into ClickHouse’s in-memory format**, with better **parallelism** and **I/O efficiency**.

> Internally, we called it Yet Another Parquet Reader, because it really is the third. The first attempt (`input_format_parquet_use_native_reader`) was started but never finished. The second (v2) reached a pull request but stalled. Now, with v3, we finally have a fully integrated, native Parquet reader.

Now let’s look at what this new reader unlocks: improved parallelism and more efficient I/O.

### Improved parallelism

The diagram below (from our [earlier deep dive](https://clickhouse.com/blog/clickhouse-and-parquet-a-foundation-for-fast-lakehouse-analytics)) shows the physical on-disk structure of a Parquet file:

![Blog-release-25.8.001.png](https://clickhouse.com/uploads/Blog_release_25_8_001_4d2fc7259a.png)

We won't go into much detail here (you can read the deep dive for that), just briefly:

**Parquet files are hierarchical:**

**① Row groups** — horizontal partitions, typically ~1M rows / ~500 MB.  
**② Column chunks** — vertical slices, one per column in each row group.  
**③ Pages** — smallest unit, ~1 MB blocks of encoded values.

With this layout in mind, ClickHouse parallelizes Parquet queries across available CPU cores. 

The old reader already supported **scanning multiple row groups in parallel**, but the new reader goes further:  Instead of only processing entire row groups in parallel, **the new reader can read different columns from the same row group concurrently**, enabling better CPU utilization when fewer row groups are available.

And because the ClickHouse engine parallelizes almost every stage of query execution (filtering, aggregating, sorting), the new reader plugs seamlessly into an execution model that’s parallel from end to end:

![1_25.8-release.png](https://clickhouse.com/uploads/1_25_8_release_88a03c5498.png)

① Prefetch threads — fetch multiple columns in parallel.  
② Parsing threads — decode columns in parallel.  
③ File streams — process different Parquet files concurrently.  
④ Processing lanes — filter, aggregate, and sort across CPU cores in parallel.

**Note that with the new reader, ① prefetching is smarter:** it runs in a separate thread pool and only pulls what’s actually needed. For example, non-PREWHERE columns are prefetched only after [PREWHERE](https://clickhouse.com/docs/optimize/prewhere) is done, and we know which pages we'll need to read, eliminating wasted reads. *(We’ll talk more about PREWHERE in the next section.)*

Parallel processing of Parquet data boosts query performance, but the volume of data scanned also plays a huge role in speed. On that front, too, the new Parquet reader is more efficient!

### Improved I/O efficiency

While parallelism speeds up processing, smarter filtering reduces how much needs to be processed in the first place.

The diagram below shows the metadata Parquet stores for filtering:

![Blog-release-25.8.003.png](https://clickhouse.com/uploads/Blog_release_25_8_003_8c3178fd05.png)

① **Dictionaries** — map unique values for low-cardinality columns.  
② **Page stats** — min/max values per page.  
③ **Bloom filters** — per-column hints to skip irrelevant data.  
④ **Row group stats** — min/max values for entire row groups.

The previous ClickHouse Parquet reader already used **row-group-level** min/max and Bloom filters to avoid scanning irrelevant data.

The new native reader adds **page-level min/max filtering** and support for [**PREWHERE**](https://clickhouse.com/docs/optimize/prewhere), making it even more efficient. We’ll demo that next.

### Parquet reader performance

The new Parquet reader generally improved the performance of [ClickBench](https://benchmark.clickhouse.com/) queries by an average factor of **1.81×**, almost doubling speed when running the queries directly over Parquet files:

![3_25.8-release.png](https://clickhouse.com/uploads/3_25_8_release_ca1207554d.png)

### Demo

To demonstrate the parquet reader's improved performance, we will run a query over the dataset used by ClickBench.

Step 1: Create a directory to store the ClickBench [anonymised web analytics dataset](https://clickhouse.com/docs/getting-started/example-datasets/metrica) as a Parquet file

<pre><code type='click-ui' language='bash'>
mkdir ~/hits_parquet
cd ~/hits_parquet
</code></pre>

Step 2: Download the dataset in Parquet format:

<pre><code type='click-ui' language='bash'>
wget --continue --progress=dot:giga 'https://datasets.clickhouse.com/hits_compatible/hits.parquet'
</code></pre>

Step 3: Download the latest ClickHouse version:

<pre><code type='click-ui' language='bash'>
curl https://clickhouse.com/ | sh
</code></pre>

Step 4: Run clickhouse-local in interactive mode:

<pre><code type='click-ui' language='bash'>
./clickhouse local
</code></pre>

Now, we run a typical analytical query involving the URL and EventTime columns, with the previous parquet reader implementation:

<pre><code type='click-ui' language='sql'>
SELECT URL, EventTime 
FROM file('./hits_parquet/hits.parquet')
WHERE URL LIKE '%google%'
ORDER BY EventTime 
LIMIT 10
FORMAT Null;
</code></pre>

```
0 rows in set. Elapsed: 1.513 sec. Processed 99.57 million rows, 14.69 GB (65.82 million rows/s., 9.71 GB/s.)
Peak memory usage: 1.36 GiB.
```

Note that the query scanned and processed **99.57 million rows**, **14.69 GB** in **1.513 sec**.

Next, we run the same query again with the new parquet reader enabled:

<pre><code type='click-ui' language='sql'>
SELECT URL, EventTime 
FROM file('./hits_parquet/hits.parquet')
WHERE URL LIKE '%google%'
ORDER BY EventTime 
LIMIT 10
FORMAT Null
SETTINGS
    input_format_parquet_use_native_reader_v3 = 1
</code></pre>

```
0 rows in set. Elapsed: 0.703 sec. Processed 14.82 thousand rows, 6.67 MB (21.07 thousand rows/s., 9.48 MB/s.)
Peak memory usage: 1.91 GiB.
```

Now the query processed only **4.82K rows, 6.67 MB, in 0.703 sec**, about **2× faster**.

This speedup comes from a combination of **page-level min/max filtering** and **PREWHERE**.

* With page-level stats, ClickHouse prunes entire Parquet pages that can’t match the WHERE clause on the URL column.

* With [PREWHERE](https://clickhouse.com/docs/optimize/prewhere), ClickHouse scans only the EventTime values (at page granularity) for matching URLs.

### Why does it matter?

Fast Parquet processing is the foundation for ClickHouse as a Lakehouse engine. Open table formats like **Apache Iceberg** (and Delta Lake, Hudi, and others) all use Parquet as their storage layer:

![4_25.8-release.png](https://clickhouse.com/uploads/4_25_8_release_50c98f2d38.png)

That means every query over an Iceberg table ultimately comes down to how efficiently the engine can read and process Parquet files.

By making Parquet reading faster and smarter, we make ClickHouse a high-performance fit for data lakes: giving you the raw speed of our native engine, directly on open formats.

## Writes with Hive-style partitioning

### Contributed by Arthur Passos

ClickHouse now supports writing data with Hive-style partitioning. This means that data is split by directories, where the directory structure represents the values of the partition key. 

Let’s look at how it works with the [S3 table engine](https://clickhouse.com/docs/engines/table-engines/integrations/s3#partition-by). We’ll use MinIO so that we can test it locally, so let’s first install the MinIO client and server:

<pre><code type='click-ui' language='bash'>
brew install minio/stable/minio
brew install minio/stable/mc
</code></pre>

Next, let’s start the server:

<pre><code type='click-ui' language='bash'>
minio server hive-data
</code></pre>

And now let’s create a bucket:

<pre><code type='click-ui' language='bash'>
mc alias set minio http://127.0.0.1:9000 minioadmin minioadmin
mc mb minio/taxis
</code></pre>

```
Added `minio` successfully.
Bucket created successfully `minio/taxis`.
```

We’ll download some Parquet files from the New York taxis dataset:

<pre><code type='click-ui' language='bash'>
curl "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-06.parquet" -o yellow_tripdata_2023-06.parquet
</code></pre>

Now, it’s time to create a table. We’ll partition the data by `PULocationID` and `DOLocationID`, representing the pickup and drop-off locations.

<pre><code type='click-ui' language='sql'>
CREATE TABLE taxis
(
    VendorID              Int64,
    tpep_pickup_datetime  DateTime64(6),
    tpep_dropoff_datetime DateTime64(6),
    passenger_count       Float64,
    trip_distance         Float64,
    RatecodeID            Float64,
    store_and_fwd_flag    String,
    PULocationID          Int64,
    DOLocationID          Int64,
    payment_type          Int64,
    fare_amount           Float64,
    extra                 Float64,
    mta_tax               Float64,
    tip_amount            Float64,
    tolls_amount          Float64,
    improvement_surcharge Float64,
    total_amount          Float64,
    congestion_surcharge  Float64,
    airport_fee           Float64
)
ENGINE = S3(
    'http://127.0.0.1:9000/taxis',
    'minioadmin', 'minioadmin',
    format='Parquet', partition_strategy = 'hive'
)
PARTITION BY (PULocationID, DOLocationID);
</code></pre>

Next, let’s insert those Parquet files:

<pre><code type='click-ui' language='sql'>
INSERT INTO taxis
SELECT *
FROM file('*.parquet');
</code></pre>

We can then query the table as shown below:

<pre><code type='click-ui' language='sql'>
SELECT DOLocationID, _path, avg(fare_amount)
FROM taxis
WHERE PULocationID = 199
GROUP BY ALL;
</code></pre>

```
┌─DOLocationID─┬─_path───────────────────────────────────────────────────────────────┬─avg(fare_amount)─┐
│           79 │ taxis/PULocationID=199/DOLocationID=79/7368231474740330498.parquet  │             45.7 │
│          163 │ taxis/PULocationID=199/DOLocationID=163/7368231447649320960.parquet │               52 │
│          229 │ taxis/PULocationID=199/DOLocationID=229/7368231455001935873.parquet │             37.3 │
│          233 │ taxis/PULocationID=199/DOLocationID=233/7368231484399812609.parquet │             49.2 │
│           41 │ taxis/PULocationID=199/DOLocationID=41/7368231474941657088.parquet  │             31.7 │
│          129 │ taxis/PULocationID=199/DOLocationID=129/7368231437356498946.parquet │               10 │
│           70 │ taxis/PULocationID=199/DOLocationID=70/7368231504532471809.parquet  │                3 │
│          186 │ taxis/PULocationID=199/DOLocationID=186/7368231493912494080.parquet │             44.3 │
└──────────────┴─────────────────────────────────────────────────────────────────────┴──────────────────┘
```

## Data Lake improvements

### Contributed by Konstantin Vedernikov

ClickHouse’s Data Lake support also received improvements. Using the IcebergS3 table engine, you can now create an Apache Iceberg table, insert data, delete data, update data, and adjust the schema. 

Let’s start by creating a table using the  `IcebergLocal` table engine:

<pre><code type='click-ui' language='sql'>
CREATE TABLE demo (c1 Int32) 
ENGINE = IcebergLocal('/Users/markhneedham/Downloads/ice/');
</code></pre>

Support for writing to Iceberg is still experimental, so we’ll need to set the following config:

<pre><code type='click-ui' language='bash'>
SET allow_experimental_insert_into_iceberg=1;
</code></pre>

Insert some data:

<pre><code type='click-ui' language='sql'>
INSERT INTO demo VALUES (1), (2), (3);
</code></pre>

Query that table:

<pre><code type='click-ui' language='sql'>
SELECT * 
FROM demo;
</code></pre>

As expected, we have three rows:

```
┌─c1─┐
│  1 │
│  2 │
│  3 │
└────┘
```

Next, let’s delete the row where `c1=3`:

<pre><code type='click-ui' language='sql'>
DELETE FROM demo WHERE c1=3;
</code></pre>

And we’ll query the table again:

```
┌─c1─┐
│  1 │
│  2 │
└────┘
```

Great, one row down! Next, we’ll change the table DDL to have an extra column:

<pre><code type='click-ui' language='sql'>
ALTER TABLE demo 
ADD column c2 Nullable(String);
</code></pre>

Query the table again:

```
┌─c1─┬─c2───┐
│  1 │ ᴺᵁᴸᴸ │
│  2 │ ᴺᵁᴸᴸ │
└────┴──────┘
```

Perfect, we have our new column with all null values. Let’s add a new row:

<pre><code type='click-ui' language='sql'>
INSERT INTO demo VALUES (4, 'Delta Kernel');
</code></pre>

And then query the table a third time!

```
┌─c1─┬─c2───────────┐
│  4 │ Delta Kernel │
│  1 │ ᴺᵁᴸᴸ         │
│  2 │ ᴺᵁᴸᴸ         │
└────┴──────────────┘
```

Let’s now update `c2` for the row that has `c1=1`:

<pre><code type='click-ui' language='sql'>
ALTER TABLE demo
 (UPDATE c2 = 'Equality delete' WHERE c1 = 1);
</code></pre>

And let’s query the table one last time:

```
┌─c1─┬─c2──────────────┐
│  1 │ Equality delete │
│  4 │ Delta Kernel    │
│  2 │ ᴺᵁᴸᴸ            │
└────┴─────────────────┘
```

We can have a look at the underlying files that have been created in our bucket from doing all these operations by running the following command:

<pre><code type='click-ui' language='bash'>
$ tree ~/Downloads/ice
</code></pre>

```
/Users/markhneedham/Downloads/ice
├── data
│   ├── 8ef82353-d10c-489d-b1c4-63205e2491e4-deletes.parquet
│   ├── c5080e90-bbee-4406-9c3f-c36f0f47f89f-deletes.parquet
│   ├── data-369710b6-6b9c-4c68-bc76-c62c34749743.parquet
│   ├── data-4297610d-f152-4976-a8aa-885f0d29e172.parquet
│   └── data-b4a9533f-2c6d-4f5f-bff9-3a4b50d72233.parquet
└── metadata
    ├── 50bb92f9-1de1-4e27-98bc-1f5633b71025.avro
    ├── 842076c9-5c9a-476c-9083-b1289285518d.avro
    ├── 99ef0cd6-f702-4e5a-83e5-60bcc37a2dcf.avro
    ├── b52470e3-2c24-48c8-9ced-e5360555330a.avro
    ├── c4e99628-5eb8-43cc-a159-3ae7c3d18f48.avro
    ├── snap-1696903795-2-4ca0c4af-b3a8-4660-be25-c703d8aa88be.avro
    ├── snap-2044098852-2-e9602064-a769-475c-a1ae-ab129a954336.avro
    ├── snap-22502194-2-86c0c780-60a7-4896-9a29-a2317ad6c3f6.avro
    ├── snap-227376740-2-37010387-0c95-4355-abf7-1648282437cd.avro
    ├── snap-326377684-2-0d0d0b37-8aec-41c0-99ce-f772ab9e1f6b.avro
    ├── v1.metadata.json
    ├── v2.metadata.json
    ├── v3.metadata.json
    ├── v4.metadata.json
    ├── v5.metadata.json
    ├── v6.metadata.json
    └── v7.metadata.json
```

We can drop the table from ClickHouse by running `DROP TABLE demo`, but keep in mind that doing this won’t remove the underlying table from the storage bucket.

There are also other updates to Data Lake support, including:

* Writes into Iceberg are supported with the REST and Glue catalogs.  
* Support for `DROP TABLE` for Iceberg in REST and Glue catalogs.  
* Support for writes and time travel for Delta Lake tables.

The Unity, REST, Glue, and Hive Metastore catalogs have also been promoted from experimental to beta status.

## Virtual column _table everywhere

### Contributed by Xiaozhe Yu

The merge table function, which can query multiple tables concurrently, makes available the `_table` virtual column so that you can track the underlying table from which a result row came. This virtual column is now available for other queries as well.

For example, let’s say we had another table `foo`, defined as follows:

<pre><code type='click-ui' language='sql'>
CREATE TABLE foo
(
  c1 Int,
  c2 String,
  c3 String
)
ORDER BY c1;

INSERT INTO foo VALUES (7, 'ClickHouse', 'ClickStack');
</code></pre>

And we write a query against this table and the `icebergLocal` table function, as shown below:

<pre><code type='click-ui' language='sql'>
SELECT c1, c2, 
FROM icebergLocal('/Users/markhneedham/Downloads/ice')
UNION ALL
SELECT c1, c2
FROM foo;
</code></pre>

```
┌─c1─┬─c2──────────────┐
│  1 │ Equality delete │
│  7 │ ClickHouse      │
│  4 │ Delta Kernel    │
│  2 │ ᴺᵁᴸᴸ            │
└────┴─────────────────┘
```

We can now use the `_table` virtual column, so we’ll know which row came from each part of the `UNION ALL` query:

<pre><code type='click-ui' language='sql'>
SELECT c1, c2, _table
FROM icebergLocal('/Users/markhneedham/Downloads/ice')
UNION ALL
SELECT c1, c2, _table
FROM foo;
</code></pre>

```
┌─c1─┬─c2──────────────┬─_table───────┐
│  7 │ ClickHouse      │ foo          │
│  1 │ Equality delete │ icebergLocal │
│  4 │ Delta Kernel    │ icebergLocal │
│  2 │ ᴺᵁᴸᴸ            │ icebergLocal │
└────┴─────────────────┴──────────────┘
```

## S3 security features

### Contributed by Artem Brustovetski

This release added a couple more security features for working with data stored in S3.

You can now use custom IAM roles with the s3 table function:

<pre><code type='click-ui' language='sql'>
SELECT * 
FROM s3('s3://mybucket/path.csv', CSVWithNames,
    extra_credentials(role_arn =
'arn:aws:iam::111111111111:role/ClickHouseAccessRole-001'));
</code></pre>

It’s also now possible to define GRANTS for specific URLs in S3 rather than to all S3 buckets:

<pre><code type='click-ui' language='sql'>
GRANT READ ON S3('s3://foo/.*') 
TO user;
</code></pre>

## Arrow Flight integration

### Contributed by zakr600, Vitaly Baranov

[Arrow Flight](https://arrow.apache.org/docs/format/Flight.html) is a high-performance protocol for data exchange built on Apache Arrow's columnar memory format and gRPC for transport. Unlike traditional row-based protocols, Arrow Flight preserves data in its native columnar representation during transmission, eliminating costly serialization overhead and making it particularly well-suited for analytical workloads. Consider it a modern, efficient alternative to protocols like ODBC or JDBC, explicitly designed for the columnar data processing era.

ClickHouse now includes initial Arrow Flight support, allowing it to function as a client and server in the Arrow Flight ecosystem. ClickHouse can query remote Arrow Flight data sources using the `arrowflight` table function as a client. As a server, it can expose its data to Arrow Flight-compatible clients like PyArrow or other systems supporting the protocol.

This addition provides a new integration path, enabling it to work with the growing Arrow-native tools and applications ecosystem. While still an emerging capability, Arrow Flight support represents ClickHouse's first steps toward broader compatibility with columnar data processing workflows beyond its native protocol.

Let’s first look at how we can use ClickHouse as an Arrow Flight server. We’ll need to specify the port on which it should run. You might also need to specify the `listen_host`, otherwise, it might try to start listening on an IPv6 address, which isn’t supported on some systems. 

<pre><code type='click-ui' language='yaml'>
arrowflight_port: 6379
arrowflight:
  enable_ssl: false
listen_host: "127.0.0.1"
</code></pre>

Then, start the ClickHouse Server:

<pre><code type='click-ui' language='bash'>
./clickhouse server
</code></pre>

You should see a line like this:

```
Application: Listening for Arrow Flight compatibility protocol: 127.0.0.1:6379
```

Next, we’ll launch the ClickHouse Client:

<pre><code type='click-ui' language='bash'>
./clickhouse client
</code></pre>

And then create a table for ourselves based on the New York taxis dataset:

<pre><code type='click-ui' language='sql'>
CREATE TABLE taxis
ORDER BY VendorID
AS SELECT *
FROM url('https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-06.parquet')
SETTINGS schema_inference_make_columns_nullable = 0;
</code></pre>

Once that’s done, let’s launch the iPython REPL with pyarrow provided as a dependency:

<pre><code type='click-ui' language='bash'>
uv run --with pyarrow --with ipython ipython
</code></pre>

We can then run the following code to compute the average tip and passenger count:

<pre><code type='click-ui' language='python'>
import pyarrow.flight as fl

client = fl.FlightClient("grpc://localhost:6379")
token = client.authenticate_basic_token("default", "")

ticket = fl.Ticket(b"SELECT avg(tip_amount), avg(passenger_count) FROM taxis LIMIT 10")
call_options = fl.FlightCallOptions(headers=[token])

try:
    reader = client.do_get(ticket, call_options)

    table = reader.read_all()
    print("Table shape:", table.shape)
    print("Schema:", table.schema)
    print("nData:")
    print(table)
except Exception as e:
    print(f"Error: {e}")
</code></pre>

```
Table shape: (1, 2)
Schema: avg(tip_amount): double not null
avg(passenger_count): double not null

Data:
pyarrow.Table
avg(tip_amount): double not null
avg(passenger_count): double not null
----
avg(tip_amount): [[3.5949154187456926]]
avg(passenger_count): [[1.327664447087808]]
```

As mentioned earlier, ClickHouse can also act as an Arrow Flight client. This is done via the `arrowFlight` table function or `ArrowFlight` table engine.

We can then query Arrow Flight servers like this:

<pre><code type='click-ui' language='sql'>
SELECT * 
FROM arrowflight('localhost:6379', 'dataset');
</code></pre>


## Initial PromQL support

### Contributed by Vitaly Baranov

This release also adds initial support for PromQL (Prometheus Query Language). 
You can use it by setting `dialect='promql` in the ClickHouse client and point it at a time-series table using the setting `promql_table_name='X'`.
You'll then be able to run queries like this:

<pre><code type='click-ui' language='sql'>
rate(ClickHouseProfileEvents_ReadCompressedBytes[1m])[5m:1m]
</code></pre>


You can also wrap the PromQL query is a SQL statement: 

<pre><code type='click-ui' language='sql'>
SELECT * 
FROM prometheusQuery('up', ...)
</code></pre>

As of 25.8, only the rate, delta and increase functions are supported.

## Improved Azure Blob Storage Performance

### Contributed by Alexander Sapin

Object storages like AWS S3, GCP, and Azure Blob Storage are complex distributed systems with their own shenanigans. Especially latencies can become problematic: we observed rare, unexpected spikes of latencies up to 5 sec, 10 sec, 15 sec, …

We solved this problem for AWS and GCP a few years ago with our own HTTP client implementation:
- using multiple connections to multiple endpoints
- rotating endpoints for better distribution of the load
- running a second request as soon as there is a soft timeout
- doing many speculative retries aggressively

Now we have solved the latency issue also for Azure Blob Storage by replacing the HTTP client in Azure SDK with our implementation, reusing the same logic of aggressive retries as for AWS S3.

Results:

No more latency spikes!

This is enabled by default with the option to use the previous implementation via `azure_sdk_use_native_client=false`.