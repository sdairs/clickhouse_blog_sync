---
title: "JSONBench is back, and ClickHouse still leads"
date: "2026-11-16T10:55:03.495Z"
author: "Tom Schreiber and Mark Needham"
category: "Engineering"
excerpt: "JSONBench now compares 27 database engines. ClickHouse still leads on a billion JSON documents. Explore the results and run the benchmark yourself."
---

# JSONBench is back, and ClickHouse still leads

## TL;DR

[JSONBench](https://benchmark.clickhouse.com/json/) has grown from five to 27 engines. Almost two years after its debut, ClickHouse still leads the billion-document comparison on identical hardware. You can run the open-source benchmark, reproduce the results, or add your system.

JSON is the lingua franca for handling semi-structured and unstructured data in modern systems, powering everything from logging and observability to real-time streaming, mobile app storage, and machine learning pipelines.

Document databases such as MongoDB make it easy to start working with JSON. Once the server is running, you can insert documents without declaring their fields or types upfront. The documents don’t have to share the same structure. Getting started feels refreshingly simple.

```text
# Connect to the local MongoDB server
mongosh

/* Create a collection */
db.createCollection("bluesky");

/* Insert JSON documents */
db.bluesky.insertMany([
  {"id":1,"author":"Tom","text":"I like pretzels 🥨"},
  {"id":2,"author":"Mark","text":"I like coffee ☕️"}
]);
```

ClickHouse can do this too. Create a table with a single JSON column, and you can start ingesting documents as they arrive, whatever their structure is, without defining the fields inside them upfront.

```text
# Connect to the local ClickHouse server
clickhouse client

/* Create a table with a JSON column */
CREATE TABLE bluesky (data JSON);

/* Insert JSON documents */
INSERT INTO bluesky FORMAT JSONAsObject
[
  {"id":1,"author":"Tom","text":"I like pretzels 🥨"},
  {"id":2,"author":"Mark","text":"I like coffee ☕️"}
];
```

The first documents are easy. Now let’s run an aggregation over a billion documents in MongoDB and ClickHouse.

## JSONBench: the billion-document test

The query below comes from [JSONBench](https://benchmark.clickhouse.com/json/), our open-source benchmark for analytics on JSON.

For this test, we use real [Bluesky](https://bsky.app/) events with their original nested JSON structure, rather than the simplified posts above. Each document represents an event such as a `post`, `like`, or `repost`. We’ll count which event types occur most often.

The corresponding MongoDB query:

```javascript
db.bluesky.aggregate([
  {$group: {_id: "$commit.collection", count: {$sum: 1}}},
  {$sort: {count: -1}}
]);
```

The ClickHouse query:

```sql
SELECT data.commit.collection AS event, count() AS count
FROM bluesky
GROUP BY event
ORDER BY count DESC;
```

The result is a list of event types and their counts, ordered from most common to least common.

```text
event                      count
app.bsky.feed.like          …
app.bsky.graph.follow       …
app.bsky.feed.post          …
…                           …
```

ClickHouse returns the result in **661 ms** on the cold run. MongoDB takes **32 minutes and 26 seconds**. Both run on the same machine type, using the [published benchmark configurations](https://github.com/ClickHouse/ClickBench/tree/main/json). The hot runs are shown alongside them.

<iframe src="/uploads/jsonbench_00_20261116_78e8fa845a.html" title="Aggregating one billion JSON documents" frameborder="0" style="display: block; width: 100%; height: 500px; max-height: 800px; border: 0;"></iframe>

ClickHouse [brings](https://clickhouse.com/blog/a-new-powerful-json-data-type-for-clickhouse) its native columnar storage, compression, and parallel query engine to JSON. Documents retain their flexibility, while queries benefit from [reading and processing the fields they need](https://clickhouse.com/blog/json-data-type-gets-even-better).

## JSONBench began with five systems

We [introduced](https://clickhouse.com/blog/json-bench-clickhouse-vs-mongodb-elasticsearch-duckdb-postgresql) JSONBench in January 2025 with five systems: **ClickHouse**, **MongoDB**, **Elasticsearch**, **DuckDB** and **PostgreSQL**. Each was tested on the same Bluesky data with five analytical queries.

In the original comparison, ClickHouse consistently outperformed all other tested JSON data stores in query performance and storage efficiency. Analytical query speedups reached thousands of times, while [the stored JSON was even smaller than the compressed source files](https://clickhouse.com/blog/json-bench-clickhouse-vs-mongodb-elasticsearch-duckdb-postgresql#storage-sizes-with-the-best-possible-compression).

The charts use JSONBench’s [combined score](https://github.com/ClickHouse/ClickBench/blob/main/README.md#results-usage-and-scoreboards), which brings together hot and cold query runtimes, loading time and storage size. Lower is better. The historical chart applies today’s calculation to the original measurements, omitting loading time because it was not recorded then.

<iframe src="/uploads/jsonbench_06_20261116_8985cea10b.html" title="JSONBench at one billion documents · January 2025" frameborder="0" style="display: block; width: 100%; height: 500px; max-height: 800px; border: 0;"></iframe>

## Almost two years later: 27 systems, ClickHouse still leads

The competition has had almost two years to catch up. Alexey Milovidov, the inventor of ClickHouse, has now revived JSONBench, merged community contributions and added more systems. The original five have been retested with newer versions and updated configurations. ClickHouse still leads their billion-document comparison.

<iframe src="/uploads/jsonbench_06a_20261116_a6ca595c3e.html" title="JSONBench at one billion documents · Almost two years later" frameborder="0" style="display: block; width: 100%; height: 500px; max-height: 800px; border: 0;"></iframe>

The field has grown from five to [27 database engines](https://github.com/ClickHouse/ClickBench/blob/main/json/data.generated.js), including **OpenSearch**, **Apache Doris**, **Databend**, **SingleStore**, **SQLite**, and **Umbra**. The next chart shows 14 selected entries with billion-document scores on the same machine type. ClickHouse leads this broader comparison too.

<iframe src="/uploads/jsonbench_07_20261116_8f69b24e0e.html" title="JSONBench at one billion documents" frameborder="0" style="display: block; width: 100%; height: 500px; max-height: 800px; border: 0;"></iframe>

The current charts show Combined scores relative to ClickHouse at 1.0. Lower is better. These are benchmark scores, not query time multipliers; unsuccessful queries and incomplete loads receive penalties.

## We haven’t stood still

Since the original JSONBench, we’ve shipped [178 changes](https://pastila.nl/?cafebabe/cdb762cca05d3a72cd2415eef55c9853.md#Rggd4nKl5Ipp61CruvsSqQ==GCM) to ClickHouse’s native JSON type, covering performance improvements, new features and fixes.

That includes faster reads and lower memory use, new indexes over [JSON field names](https://github.com/ClickHouse/ClickHouse/pull/98886) and [values](https://github.com/ClickHouse/ClickHouse/pull/100730), direct JSON support in [Parquet](https://github.com/ClickHouse/ClickHouse/pull/79649), and the option to [add type hints](https://github.com/ClickHouse/ClickHouse/pull/122711) without rewriting historical data.

The chart below shows JSON pull requests in yellow and work on the supporting [Dynamic](https://clickhouse.com/blog/a-new-powerful-json-data-type-for-clickhouse#building-block-2---dynamic-type) type in gray. Dynamic preserves the original types when a JSON field contains different kinds of values across documents.

<iframe src="/uploads/jsonbench_08_20261116_6428ce09dd.html" title="JSON development since JSONBench" frameborder="0" style="display: block; width: 100%; height: 500px; max-height: 800px; border: 0;"></iframe>

And we’re not done. The [JSON umbrella issue](https://github.com/ClickHouse/ClickHouse/issues/68428) tracks ongoing work and welcomes feature requests.

JSONBench is now also part of our [Versions Benchmark](https://benchmark.clickhouse.com/versions/#version=-&dataset=+jsonbench&metric=hot&queries=-), where you can follow JSON query performance across releases.

## Run JSONBench and add your system

JSONBench is an open-source benchmark with [public data, queries, configurations and results](https://github.com/ClickHouse/ClickBench/tree/main/json). You can reproduce the measurements, inspect how each system is tested, and contribute improvements.

If you know a system can do better, contribute an improved configuration or query. If your database is missing, add it. Vendors and community contributors are welcome.

## JSON flexibility at ClickHouse speed

JSON is the lingua franca for logs, events, applications, and machine learning pipelines. ClickHouse combines the flexibility to store those documents as they arrive with fast analytics and efficient storage at scale. That gives people and agents a common analytical engine for the applications they build, the systems they observe, and the security events they investigate.