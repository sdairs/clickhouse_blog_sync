---
title: "Introducing WalShadow: Sub-second Postgres replication to ClickHouse from physical WAL"
date: "2026-09-10T15:53:42.134Z"
author: "Sai Srirampur"
category: "Product"
excerpt: "WalShadow replicates Postgres data directly from physical WAL into ClickHouse, delivering around 200 ms latency and 289,000 rows per second in benchmarks."
---

# Introducing WalShadow: Sub-second Postgres replication to ClickHouse from physical WAL

Today, we’re announcing [WalShadow](https://github.com/ClickHouse/walshadow), an open-source engine that replicates Postgres data to ClickHouse directly from physical WAL. 

In our benchmarks, transactions committed in Postgres became visible in ClickHouse in around 200 ms, while WalShadow sustained 289K rows/sec, effectively keeping pace with the source Postgres instance.

Unlike traditional CDC based systems, WalShadow doesn’t use Postgres logical replication. It consumes the same physical WAL stream used by Postgres replicas, decodes it outside the source database, and writes ClickHouse-native blocks directly into ClickHouse. The result is a replication architecture that gets close to the latency and throughput of a Postgres physical standby, while making the data immediately available for analytics in ClickHouse.

WalShadow supports the complete replication lifecycle, including initial load, continuous replication, schema evolution, restart recovery, and planned source switchovers.

By consuming physical WAL directly, WalShadow eliminates the need for logical replication slots, removes much of the operational overhead associated with logical replication, and significantly reduces resource consumption on the source Postgres instance. It also supports complex schema changes such as `ADD COLUMN`, `RENAME COLUMN`, `DROP COLUMN`, and `CREATE TABLE`.

WalShadow is fully open source and available today on [GitHub](https://github.com/ClickHouse/walshadow).

## Bringing WalShadow to ClickHouse Managed Postgres {#bringing_walshadow_to_clickhouse_managed_postgres}

For a fully managed experience, we’re also launching WalShadow in private preview for [ClickHouse Managed Postgres](https://clickhouse.com/cloud/postgres/walshadow). 


<iframe width="768" height="432" src="https://www.youtube.com/embed/RK0yBeK2OPw?si=GpnP-JZyUlqLmW1e" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>


Physical WAL is key to WalShadow’s architecture, but most managed Postgres services don’t expose it to customers, making it impossible to use WalShadow. ClickHouse Managed Postgres manages both sides of the stack, allowing us to integrate WalShadow directly into the Postgres replication layer and provide a native path from Postgres WAL to ClickHouse.

[Sign up for the private preview of WalShadow on ClickHouse Managed Postgres.](http://clickhouse.com/cloud/postgres/walshadow)

## Architecture: From physical WAL to ClickHouse-native blocks {#architecture_from_physical_wal_to_clickhousenative_blocks}

![WalShadow Schema Decoder Clickhouse.png](uploads/Wal_Shadow_Schema_Decoder_Clickhouse_70652d1a69.png)

> WalShadow takes a new approach to Postgres-to-ClickHouse replication, effectively turning ClickHouse into an analytical physical standby.

WalShadow consumes the same WAL stream Postgres generates for physical replication and recovery. Instead of asking the source database to decode changes into logical events, WalShadow processes the WAL outside the source through four stages:

1. **Track the live schema.** WalShadow filters catalog WAL records and replays them into a schema-only shadow Postgres instance. This maintains an up-to-date catalog of tables, columns, and Postgres types as the source schema evolves.  
2. **Decode data changes in parallel.** Heap records are distributed across a pool of Rust-based decoders without passing through the shadow Postgres instance.   
3. **Build ClickHouse-native blocks.** A batcher groups decoded rows by table into complete ClickHouse-native blocks, preserving data fidelity without intermediate format conversions.  
4. **Insert in parallel.** A separate pool of inserters writes multiple blocks to ClickHouse concurrently, allowing decoding and insertion to scale independently.

This creates a direct path from Postgres to ClickHouse: no logical decoding output plugin, no Kafka, and no JSON serialization or separate normalization step.

Because WalShadow processes blocks in parallel, they may arrive in ClickHouse out of order. WalShadow preserves correctness by attaching the source WAL position (`_lsn`) to every row, allowing ClickHouse to retain the latest version for each key. Operations that require strict ordering, such as schema changes and truncations, introduce barriers that wait for all preceding data to become durable before they are applied.

> **The source only needs to ship physical WAL, resulting in a load profile similar to a physical standby while allowing changes to reach ClickHouse within a second.**

For a detailed overview of architecture, see the [architecture documentation](https://github.com/ClickHouse/walshadow/tree/main/architecture). To understand various available tuning settings affecting performance and functionality, see the [configuration guide](https://github.com/ClickHouse/walshadow/blob/main/docs/configuration.md).

## Performance benchmarks {#performance_benchmarks}

We benchmarked WalShadow against [PeerDB](https://github.com/PeerDB-io/peerdb), our state-of-the-art Postgres-to-ClickHouse CDC tool powered by logical replication which powers ClickPipes.

For me, this comparison is bittersweet. We’re proud that PeerDB, which we created, serves thousands of customers. WalShadow carries that journey forward by reimagining replication directly from physical WAL and moving us closer to a unified Postgres and ClickHouse stack.

The benchmark replicated a continuous stream of changes from a single table, with Postgres, ClickHouse, and each replication tool running in the same region. We used modest `c8i.2xlarge` instances with 8 vCPUs each. Performance will vary by workload, but these results offer a useful indication of what WalShadow can offer.

### Around 200 ms commit-to-visible latency

![](https://clickhouse.com/uploads/walshadow_sep2026_image3_b60715f13f.png)

Commit-to-visible latency measures the time from a transaction committing in Postgres to its rows becoming visible in ClickHouse. A native Postgres physical replica established a practical baseline of around 50 ms. WalShadow achieved approximately 200 ms, compared with around 10 seconds for PeerDB, about 50x lower latency in this benchmark.

### 289,000 rows per second sustained throughput

![](https://clickhouse.com/uploads/walshadow_sep2026_image1_fbe85a67f2.png)

The source Postgres instance sustained approximately 290,000 inserted rows per second, establishing the maximum rate the replication pipeline could process. WalShadow replicated 289,000 rows per second, effectively matching the source without becoming the bottleneck. PeerDB sustained approximately 120,000 rows per second, or around 40% of the source rate.

These results show that low latency does not have to come at the cost of throughput: WalShadow keeps data real-time while operating at nearly the full speed of the source.

## Conclusion and vision {#conclusion_and_vision}

At ClickHouse, we have taken several major steps to bring Postgres and ClickHouse closer together: acquisition of [PeerDB](https://clickhouse.com/blog/clickhouse-welcomes-peerdb-adding-the-fastest-postgres-cdc-to-the-fastest-olap-database), launching [Postgres CDC in ClickPipes](https://clickhouse.com/blog/postgres-cdc-connector-clickpipes-ga), and introducing [ClickHouse Managed Postgres](https://clickhouse.com/blog/postgres-managed-by-clickhouse), an enterprise-grade Postgres service built on local NVMe storage for fast OLTP and natively integrated with ClickHouse for fast OLAP.

These efforts share one goal: to give developers a unified data stack that combines Postgres for transactions and ClickHouse for analytics, without added complexity.

WalShadow represents a major milestone toward that vision. By replicating directly from physical WAL into ClickHouse-native blocks, it delivers sub-second analytics, removes much of the operational overhead of logical replication, and supports advanced schema changes that are difficult to handle through conventional logical-decoding pipelines.

Over the coming months, we will work closely with customers to harden WalShadow across real-world workloads. We are already collaborating with an initial group of design partners and are now ready to expand access.

[**Sign up for the private preview**](http://clickhouse.com/cloud/postgres/walshadow)**, and we’ll get you access within a day or two.**



WalShadow is one of several initiatives underway to make Postgres and ClickHouse work seamlessly together. Stay tuned for more.

---

## Get started with ClickHouse Managed Postgres today

Interested in seeing how ClickHouse Managed Postgres works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?intent=pg&loc=blog-cta-1940-get-started-with-clickhouse-managed-postgres-today-sign-up&utm_blogctaid=1940)

---