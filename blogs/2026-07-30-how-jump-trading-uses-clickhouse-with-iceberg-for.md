---
title: "How Jump Trading uses ClickHouse with Iceberg for analytics"
date: "2026-07-30T19:24:18.868Z"
category: "User stories"
excerpt: "Jump Trading captures petabyte-scale financial trading logs on a self-managed ClickHouse platform, where zero data loss and low latency are critical requirements."
---

# How Jump Trading uses ClickHouse with Iceberg for analytics

## Summary


* Jump Trading captures financial trading logs at the petabyte scale in a self-managed ClickHouse platform, where zero data loss and low latency are industry requirements. 
* ClickHouse cluster ingests hundreds of TB a day at a sub-20-second p99, serving real-time analytics across hundreds of billions of daily events
* Jump extended the platform with a parallel Iceberg pipeline to separate the batch analytics (reporting, research, etc…) from their real-time cluster for their business-critical use cases

“People think logs are only for observability,” says Arnaud Adant, database team lead at [Jump Trading](https://www.jumptrading.com/), a Chicago-based trading firm, “but in our case, it’s much more than that.”

Jump is a leading data and research-driven trading business based in Chicago, with offices all over the world. The company’s logging platform is less a debugging tool and acts more as the business system of record.

At [Open House SF 2026](https://clickhouse.com/openhouse/san-francisco), Arnaud shared how Jump built a self-managed ClickHouse platform, and how demand for full-scale batch exports pushed them to extend it with Apache Iceberg, without giving up the fast, familiar experience users had come to rely on.

[Watch on YouTube](https://youtube.com/watch?v=UqN1y_ZLMcI)

## Low Latency Lossless logging at petabyte scale

At Jump, retaining an enormous amount of logging is critical for many research and operational purposes, but scale can be a challenge. A single partition takes hundreds of TB a day uncompressed. The largest table alone stores the order of 100 billion events a day. Jump keeps a long history online for analytics, resulting in petabytes of compressed data.

The platform also has to be fast. Jump maintains a p99 of under 20 seconds, meaning 99% of events reach the database within that window. And because nothing can go missing, the logs are reconciled daily against their sources. 


## A successful 7+ years with ClickHouse

For over seven years, Jump has enjoyed the open-source benefits of ClickHouse. The steady drumbeat of performance improvements from ClickHouse, with the new data types like [DateTime64](https://clickhouse.com/docs/sql-reference/data-types/datetime64) and features like [Bloom filters](https://clickhouse.com/docs/optimize/skipping-indexes#bloom-filter-types) have been impactful at Jump. “ClickHouse is not only fast,” he says, “but its development is getting faster over time, and we see that with the advent of AI.”


>"ClickHouse is open-source and super-fast. When you get good performance out of technology, you save a lot of money, because you can do more with less hardware.” 
>— Arnaud Adant, Database Team Lead, JumpTrading

In addition to being ClickHouse users, the Jump team is an active contributor to the ClickHouse open-source project, having upstreamed quite a few improvements over the years. “We couldn’t do that with commercial alternatives,” Arnaud says, noting that they’ve tailored ClickHouse to their needs while giving back to the [ClickHouse community](https://clickhouse.com/community).


## A “textbook case for real-time analytics”

Jump runs an on-prem ClickHouse cluster with tens of large nodes, a textbook case for real-time analytics. The team gets low latency ingest by default while taking full advantage of their hardware, including fast NVMe storage, CPUs with SIMD instructions, and high-speed memory. “You don’t get that with other databases like Postgres or MySQL,” Arnaud says.

He highlights two ClickHouse features: [distributed tables](https://clickhouse.com/docs/engines/table-engines/special/distributed), which handle sharding for the high-volume fact tables; and [replicated tables](https://clickhouse.com/docs/engines/table-engines/mergetree-family/replication), which keep reference data available on each node in the cluster.

Raw data lands in a Redpanda cluster, fed by logs from thousands of nodes. A fleet of sharded, bare metal ingestors read from that stream and write into the corresponding ClickHouse shard. On the read side, users go through a load balancer that picks up a node at random and runs their queries against it. 

The diagram below sketches Jump’s ClickHouse implementation: Redpanda feeds sharded ingestors that write to ClickHouse, reads are routed through a load balancer, and Keeper handles replication and node registration.

![jump-clickhouse-implementation 1.jpg](https://clickhouse.com/uploads/jump_clickhouse_implementation_1_1c06fd00a1.jpg)

## Expanding data requirements across Jump

That architecture worked well for real-time analytics, but new export requirements pushed it beyond its original scope. Teams needed the data available to other readers in real time, including batch jobs and high-performance computing workloads running on Jump’s HPC infrastructure.

Serving those workloads from the same real-time cluster was not the right fit. To scale, Jump needed to separate compute from storage by moving to Parquet files on object storage, allowing each layer to scale independently.

The platform now supports two distinct workloads. Real-time analytics with fast readers and writers, ingestion peaks of 10 million rows per second, and a sub-20-second p99. And batch processing with slower, heavier readers pulling massive results set at high outgoing throughput, with greater tolerance for latency.


## Why Iceberg

The addition of that second workload led Jump to Iceberg. As an open table format built on Parquet, Iceberg offered scalable, long-term retention and made the data accessible to multiple readers, including Spark, Polars, and DuckDB.

Iceberg was particularly appealing for Jump’s use case because it behaves like a ClickHouse server. Tables live in a REST API catalog and feature familiar concepts like partitions, sort keys, statistics, deletes, and Bloom filters, with similar compression.

Jump’s team wanted to keep their new architecture simple. Taking inspiration from [Netflix’s double-write pipeline](https://clickhouse.com/blog/netflix-petabyte-scale-logging), it keeps Kafka as the single-entry point, branching into parallel paths with one set of consumers writing into the real-time ClickHouse cluster, and another writing Iceberg Parquet files out to object storage.

Much of that Iceberg-writing path is handled by ClickHouse itself. For example, [clickhouse-local](https://clickhouse.com/docs/operations/utilities/clickhouse-local) and ClickHouse Server can emit Parquet files directly to S3. And because [ClickHouse fully supports reading Iceberg](https://clickhouse.com/docs/engines/table-engines/integrations/iceberg), the same cluster that handles low latency ingest can also query the Iceberg tables, giving users a unified view of the data.

The next diagram shows Jump’s double-write pipeline: Kafka feeds parallel consumers writing to Iceberg and ClickHouse, with ClickHouse also reading Iceberg directly.

![jump-double-write-pipeline 1.jpg](https://clickhouse.com/uploads/jump_double_write_pipeline_1_35ef929405.jpg)

That unification was a hard requirement. Jump wanted teams to switch between Iceberg and ClickHouse seamlessly, running the same queries on both systems while having different latency and performance characteristics depending on the business requirements. 


>“With ClickHouse, all its best features carry over into Iceberg.” 
>— Arnaud Adant, Database Team Lead, JumpTrading

By integrating Iceberg with ClickHouse, Jump could still use core ClickHouse capabilities such as [Keeper](https://clickhouse.com/docs/guides/sre/keeper/clickhouse-keeper), [replication](https://clickhouse.com/docs/architecture/replication), [dictionaries](https://clickhouse.com/docs/dictionary), and [distributed tables](https://clickhouse.com/docs/engines/table-engines/special/distributed). Iceberg tables could be sharded and exposed through a single distributed view when needed. [Access control](https://clickhouse.com/docs/operations/access-rights) remained consistent across both systems with the same users, roles, and row policies. ClickHouse’s [system tables](https://clickhouse.com/docs/operations/system-tables) and [observability](https://clickhouse.com/docs/use-cases/observability) features carried over as well.



<video autoplay="1" muted="1" loop="1" controls="1">
  <source src="https://clickhouse.com/uploads/demo_openhouse_2026_2_8b20892ae0.mp4" type="video/mp4" />
</video>

The demo shows how Jump runs queries in both ClickHouse and ClickHouse reading Iceberg. At the top, it shows Jump running ClickHouse clusters with 18 trillion rows and 40 nodes. At the bottom, it shows ClickHouse running with the latest Iceberg version and 20 nodes.

## ClickHouse is fast, and its development is getting faster

In one experiment on a 20-node Iceberg setup, a `GROUP BY` query (deliberately not using metadata shortcuts) processed 376 billion rows, 109.5 TB of data, in 9.6 seconds, which is about 40 billion rows per second.

The benchmarks also confirmed Jump’s experience that  ClickHouse gets faster over time. Across cold and hot runs on a variety of queries, successive versions of ClickHouse trended steadily downward in elapsed time. On a quantile query, for example, performance improved from 13.5 seconds on [ClickHouse 25.12](https://clickhouse.com/blog/clickhouse-release-25-12) to 8.5 seconds on 26.2. That roadmap offers a glimpse of what’s possible by [combining ClickHouse and Iceberg](https://clickhouse.com/blog/climbing-the-iceberg-with-clickhouse), both now and in the future. 


>“Querying Iceberg from ClickHouse is very performant. What ClickHouse is doing in a single process today, we believe it can do in a distributed fashion over Iceberg. That’s going to be fantastic, because Iceberg is a standard that’s adopted everywhere.” 
— Arnaud Adant, Database Team Lead, JumpTrading

*See why data-driven teams like Jump Trading are pairing ClickHouse and Iceberg for real-time analytics and batch workloads. [Try ClickHouse Cloud free for 30 days](https://clickhouse.com/cloud).*


---

## Get started today

Interested in seeing how ClickHouse works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-1464-get-started-today-sign-up&utm_blogctaid=1464)

---