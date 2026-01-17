---
title: "TimescaleDB to ClickHouse replication: Use cases, features, and how we built it"
date: "2025-09-06T12:44:38.816Z"
author: "ClickPipes team"
category: "Product"
excerpt: "The Postgres CDC connector in ClickPipes now supports one-time migrations and continuous replication from TimescaleDB."
---

# TimescaleDB to ClickHouse replication: Use cases, features, and how we built it

The [Postgres CDC connector in ClickPipes](https://clickhouse.com/cloud/clickpipes/postgres-cdc-connector) enables users to continuously replicate data from [Postgres](https://www.postgresql.org/) to [ClickHouse Cloud](https://clickhouse.com/cloud) for blazing-fast, real-time analytics. This connector supports both one-time migrations and continuous replication and is powered by [PeerDB](https://github.com/PeerDB-io/peerdb), an open-source Postgres CDC company [acquired](https://techcrunch.com/2024/07/30/real-time-database-startup-clickhouse-acquires-peerdb-to-expand-its-postgres-support/) by ClickHouse. Since its GA launch a few months ago, we’ve seen a surge in customer requests to extend these CDC capabilities to [TimescaleDB](https://github.com/timescale/timescaledb), the time-series Postgres extension maintained by TigerData.

## Use-cases

We see use cases that involve both one-time migrations and continuous replication. They primarily fall into three buckets:

1. **Online data migrations from TimescaleDB to ClickHouse:** In this use case, customers already run analytics on TimescaleDB. As their data or workloads (e.g., advanced analytics) scale, TimescaleDB no longer performs well without significant tuning and optimizations that require deep database/DBA expertise. These customers prefer a more turnkey solution that provides [significantly faster performance](https://benchmark.clickhouse.com/#system=+lik|saB&type=-&machine=-ca2|6t|gle|6ax|ae-|6ale|3al|gel&cluster_size=-&opensource=-&tuned=+n&metric=hot&queries=-). This is where ClickHouse has been compelling for them, as it is a purpose-built analytical database. To ensure a smooth migration, they seek a one-click online migration option from TimescaleDB to ClickHouse Cloud.

[![clickbench-cdc-blog-img.png](https://clickhouse.com/uploads/clickbench_timescale_ch_cdc_f00a9e26bc.png)](https://benchmark.clickhouse.com/#system=+lik|saB&type=-&machine=-ca2|6t|gle|6ax|ae-|6ale|3al|gel&cluster_size=-&opensource=-&tuned=+n&metric=hot&queries=-)

2. **Iterative migration from TimescaleDB to ClickHouse**: In this use case, similar to the one above, a customer wants to migrate from TimescaleDB to ClickHouse but prefers to do so iteratively. Because the application is complex, they choose to migrate in stages \- moving a few workloads at a time, offloading reads first, and then migrating the write pipeline. The Postgres CDC connector is particularly useful in such scenarios, as it keeps both TimescaleDB and ClickHouse in sync with lag as low as a few seconds, while gradually migrating all workloads to ClickHouse. Here is a testimonial from one of our customers, Kindly, who falls under this category of iterative migration from TimescaleDB to ClickHouse.

> “The Postgres CDC connector made it easy for us to transition to ClickHouse Cloud without redesigning our entire pipeline. It has significantly improved dashboard performance and enabled faster data exploration, making our analytics more efficient and scalable.” - Team @ Kindly.ai

3. **Co-existence use case** – In this scenario, customers use both TimescaleDB and ClickHouse to power their real-time applications. For example, they run transactional or time-series workloads on TimescaleDB while using ClickHouse for fast, advanced analytics. Postgres CDC makes sure to reliably replicate operational data from TimescaleDB to ClickHouse for lightning-fast real-time analytics.

## Features and demo

The Postgres CDC connector in ClickPipes (and PeerDB) supports both initial load/backfill (initial snapshot of data) and ongoing sync/CDC from TimescaleDB Hypertables to ClickHouse. This is possible thanks to the native logical replication support in TimescaleDB,  a benefit of it being a Postgres extension. The connector supports both compressed and uncompressed Hypertables. Here are its main features:

1. **Blazing fast initial loads** – One of the flagship features of ClickPipes is [**parallel snapshotting**](https://clickhouse.com/docs/integrations/clickpipes/postgres/parallel_initial_load), which migrates a single large table using parallel threads. This enables moving terabytes of data in just a few hours instead of days. It works for **TimescaleDB hypertables,** as well, although It does not extend to compressed hypertables, which don’t support CTID columns. In such cases, ClickPipes falls back to single-threaded execution — which remains fast thanks to a range of micro-optimizations, including cursors and efficient data movement via Avro \+ Zstd, among others.  
2. **Support for both uncompressed and compressed hypertables** – The ClickPipes Postgres CDC connector works with both uncompressed and compressed TimescaleDB hypertables, ensuring seamless replication into ClickHouse.  
3. **Support for schema changes** \- The ClickPipes Postgres CDC connector also supports automatic replication of [schema changes](https://clickhouse.com/docs/integrations/clickpipes/postgres/schema-changes) from TimescaleDB including adding and dropping columns.  
4. **Comprehensive alerts and metrics** – ClickPipes provides extensive metrics including throughput, inserts/updates/deletes per table, latency, and Postgres-native metrics such as replication slot size over time and wait events during replication. It also offers advanced [alerts](https://clickhouse.com/blog/postgres-cdc-connector-clickpipes-public-beta#user-facing-alerts) through Slack or email for issues like replication slot growth or replication failures etc. The goal is to deliver deep visibility into the replication process and ensure an enterprise-ready experience.

<iframe width="768" height="432" src="https://www.youtube.com/embed/FebWvSnW9Hk?si=-FxKbzH9BySESI-H" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

## How did we build it?

### Handling hypertables and chunks in logical replication

The TimescaleDB extension introduces **hypertables**—automatically partitioned tables designed to optimize query performance for time-series data. Like Postgres partitioned tables, hypertables don’t store data directly but do it in child tables called **chunks**. This design complicates logical replication, since changes must be tracked at the chunk level rather than the parent hypertable. It also requires handling scenarios where TimescaleDB automatically creates new chunks as data arrives.

For standard [Postgres partitioned tables](https://blog.peerdb.io/real-time-change-data-capture-for-postgres-partitioned-tables), logical replication relies on the [`publish_via_partition_root`](https://amitlan.com/writing/pg/partition-logical-replication/) option, which rewrites changes to appear as if they originated from the parent table. Hypertables, however, don’t support this option. ClickPipes (via PeerDB) therefore [performs the parent lookup explicitly](https://github.com/PeerDB-io/peerdb/blob/da537889fe9b9bbe84b85799385f3b576b5b34dd/flow/connectors/postgres/cdc.go#L1152) while processing changes. As long as the publication includes all child tables, this ensures that changes are routed correctly to the target ClickHouse table.

![timescalediagramfinal.png](https://clickhouse.com/uploads/timescalediagramfinal_cb752d0018.png)

To manage newly created chunks, TimescaleDB stores them under the `_timescaledb_internal` schema. By adding this schema to the Postgres publication, we capture all future chunks. It requires a bit of setup upfront but, once configured, results in a **hands-off replication experience** with ClickPipes.

### Supporting Compression

Another TimescaleDB feature beyond vanilla Postgres is **hypertable compression**, enabled via transparent compression or the newer Hypercore hybrid row-columnar engine. These configurations bring compression benefits similar to columnar and time-series databases like ClickHouse.

However, compressed storage introduces challenges. Our parallel initial-load strategy using `ctid` partitions doesn’t work here and fails with errors such as:

`ERROR: transparent decompression only supports tableoid system column`

We recently [shipped an improvement](https://github.com/search?q=repo%3APeerDB-io%2Fpeerdb+timescaledb&type=pullrequests) to detect this scenario and automatically fall back to a code path that avoids relying on the `ctid` column, ensuring replication remains reliable even with compressed hypertables.

## Conclusion

To get started with replicating or migrating your TimescaleDB workloads to ClickHouse, you can follow the resources below.

1. [Steps to setup logical replication on TimescaleDB](https://clickhouse.com/docs/integrations/clickpipes/postgres/source/timescale)  
2. [ClickPipes for replicating TimescaleDB to ClickHouse Cloud](https://clickhouse.com/docs/integrations/clickpipes/postgres)  
3. [PeerDB for replication TimescaleDB to ClickHouse Open Source](https://github.com/PeerDB-io/peerdb)

*\* Third-party logos and trademarks belong to their respective owners and are used here for identification purposes only. No endorsement is implied.*