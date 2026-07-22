---
title: "PostgresBench: Measuring the impact of High Availability on Managed Postgres performance"
date: "2026-07-21T16:13:25.605Z"
author: "Lionel Palacin, Sai Srirampur and Andrey Chudnovskiy"
category: "Engineering"
excerpt: "PostgresBench now includes HA benchmarks, comparing the performance of managed Postgres services under production-style HA configurations. This post explains the architectures behind each service and analyzes the trade-offs between availability guarantees"
---

# PostgresBench: Measuring the impact of High Availability on Managed Postgres performance

A few months ago, [we released PostgresBench](https://clickhouse.com/blog/postgresbench), an open source benchmark that compares managed Postgres performance across vendors with a [transparent, reproducible methodology](https://github.com/ClickHouse/PostgresBench/). It was well received by the [Postgres community](https://news.ycombinator.com/item?id=48611942), and the most common piece of feedback we heard was why we hadn't benchmarked any high availability configurations. Today, we've addressed that, and we're sharing results for HA configurations across those same vendors.

One important clarification: this isn't a complete high-availability comparison across vendors. It measures only the performance cost of achieving comparable levels of availability and data durability across various Postgres managed services.

![postgresbench-ha-screenshot.png](https://clickhouse.com/uploads/postgresbench_ha_screenshot_3bcf16f181.png)

---

## Get started with ClickHouse Managed Postgres today

Interested in seeing how ClickHouse Managed Postgres works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-1353-get-started-with-clickhouse-managed-postgres-today-sign-up&utm_blogctaid=1353)

---

## HA Setup across Postgres services

Managed Postgres services typically use two different architectures to provide high availability. 

**Shared-nothing** services (ClickHouse Managed Postgres, AWS RDS, and Crunchy Bridge) use isolated compute and single-tenant storage deployments for each customer instance, and rely on native PostgreSQL replication, with one or more physical streaming standbys and automatic failover if the primary becomes unavailable. 

**Shared-storage** services (AWS Aurora and Neon, both forks of Postgres) separate compute and storage, achieving durability by writing multiple copies of the WAL to a replicated storage layer on the commit path, and replacing failed compute nodes without relying on traditional streaming replicas.

For this comparison, we've defined high availability as the system's claim to recover after a primary failure within 2 minutes and zero data loss guarantees. We selected the closest comparable HA configuration offered by each managed service while keeping the comparison as fair as possible. The sections below describe the configuration we benchmarked for each vendor.

We matched the primary compute resources (CPU and RAM) as closely as possible across all vendors to ensure a fair comparison. For the shared-storage services this is not the full picture: hardware profiles and redundancy configuration on the storage backends are not publicly disclosed, though they contribute to system performance and reliability.

### ClickHouse Managed Postgres

**ClickHouse Managed Postgres** is a local NVMe-backed Postgres service optimized for high-performance OLTP workloads. Because local NVMe storage is ephemeral in the event of compute failures, the service offers [multiple high-availability (HA) configurations](https://clickhouse.com/docs/cloud/managed-postgres/high-availability) with different durability levels.

The single-standby configuration uses asynchronous replication and is ideal for workloads that can tolerate a small recovery point objective (RPO) i.e. accepting a few milli-seconds of lost transactions. The two-standby configuration uses synchronous quorum replication to provide zero data loss (RPO \= 0). Because all durability and high availability come from PostgreSQL replication and WAL upload rather than replicated disks, zero data loss with cross-AZ high availability today requires this quorum of 3 instances; we're working on a similar durability guarantee without the 3rd instance.

This was an intentional design choice to provide customers with the control and flexibility to choose their preferred HA configuration (0, 1, or 2 standbys) based on the mission-criticality of their workload. Both configurations are designed for fast failover, with hot standbys that minimize recovery time (RTO) when the primary becomes unavailable.

### Crunchy Bridge

Crunchy Bridge (Snowflake Postgres) provide [high availability](https://docs.crunchybridge.com/concepts/high-availability) using a single physical streaming standby replica. By default, replication is asynchronous. We were unable to configure synchronous replication (tweaking `synchronous_commit`) and did not find an option to guarantee a zero RPO. If we overlooked a supported configuration or setting, please let us know, we're happy to update this post accordingly.

### AWS RDS Postgres

AWS RDS (and Crunchy Bridge) rely on replicated managed disks for in-AZ durability, and hot standby PostgreSQL instances for high availability and cross-AZ durability. RDS supports one or two standbys, and both options always replicate synchronously, so there's no data loss on failover. We tested both: [Multi-AZ DB instance (one standby)](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.MultiAZSingleStandby.html) and [Multi-AZ DB cluster (two standbys, quorum)](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/multi-az-db-clusters-concepts.html).

### AWS Aurora Postgres

Aurora Postgres is an AWS-maintained fork of Postgres that provides high availability through a shared storage architecture rather than native Postgres streaming replication. Data is synchronously replicated across multiple storage nodes across multiple Availability Zones, and reader instances share the same storage volume as the writer. Hot standbys in shared-storage systems are not required for durability, while still beneficial for faster failovers or read traffic scale-out; AWS [recommends](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/Concepts.AuroraHighAvailability.html) deploying at least one Aurora Replica (reader) for High Availability. The replica enables automatic failover and fast recovery if the primary instance becomes unavailable. We benchmarked a cluster with one writer and one Aurora Replica.

### Neon

Neon is also a fork of Postgres that follows a separation of storage and compute architecture. Read throughput relies on a combination of local caches on the compute instances and remote reads from separate distributed systems usually referred to as "page servers". Neon goes further with multi-tenancy in the platform, with serverless compute clusters and connection gateways; those components introduce further trade-offs for business-critical workloads ([reference](https://clickhouse.com/blog/socialpruf#addressing-reliability-issues-and-network-costs-with-neon-postgres)), while adding flexibility and potential cost savings.

Neon positions its [high availability (HA)](https://neon.com/docs/introduction/high-availability) around eliminating the need for a standby node by bringing up a new compute node very quickly during a failover and attaching it to the existing storage. The company presents this as a cost advantage. The claim that a standby node is not required is questionable given Neon's track record of [availability and reliability issues](https://clickhouse.com/blog/socialpruf#addressing-reliability-issues-and-network-costs-with-neon-postgres) affecting many customers. However, for the purposes of this benchmark, we evaluate Neon's HA based on its documented architecture and positioning.



## Benchmark results

We benchmarked each configuration across a range of database instance sizes and dataset sizes, and every result is available on [PostgresBench](https://postgresbench.clickhouse.com/). Below, we present results for the largest instance size (16 vCPU, 64 GB RAM) and the largest dataset (500 GB), with each test running for 10 minutes. We report average transactions per second (TPS) and p99 transaction latency. 

The table below also includes a Single node row for each vendor, the single-node baseline already published in the first round of PostgresBench. Aurora and Neon results in this table are basically their single node deployment. 

| Vendor | Configuration | Avg TPS | TPS vs own Single node | Avg latency | Avg latency vs own Single node | p99 latency | p99 vs own Single node |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| ClickHouse Managed Postgres | Single node | 26,328 | 100% | 9.70 ms | 100% | 13.20 ms | 100% |
| ClickHouse Managed Postgres | 1 standby, async | 24,667 | 94% | 10.37 ms | 107% | 24.17 ms | 183% |
| ClickHouse Managed Postgres | 2 standbys, sync (quorum) | 20,720 | 79% | 12.34 ms | 127% | 33.49 ms | 254% |
| Crunchy Bridge | Single node | 11,113 | 100% | 23.00 ms | 100% | 41.68 ms | 100% |
| Crunchy Bridge | HA (1 standby, async) | 11,135 | 100% | 23.00 ms | 100% | 41.89 ms | 101% |
| RDS by AWS | Single node | 4,399 | 100% | 58.14 ms | 100% | 130.15 ms | 100% |
| RDS by AWS | Multi-AZ instance (1 sync) | 4,461 | 101% | 57.35 ms | 99% | 221.69 ms | 170% |
| RDS by AWS | Multi-AZ cluster (2 sync, quorum) | 4,659 | 106% | 54.92 ms | 94% | 816.63 ms | 627% |
| AWS Aurora  | Single node | 9,238 | 100% | 27.69 ms | 100% | 39.81 ms | 100% |
| AWS Aurora  | HA (1 standby, async) | 9,520 | 103% | 26.87 ms | 97% | 39.92 ms | 100% |
| Neon | Single node | 7,802 | 100% | 32.80 ms | 100% | 56.30 ms | 100% |

### Shared-nothing architecture

For the vendors that rely on standby replicas, comparing at matched compute and comparable durability levels:

1. **RDS Postgres:** For 0 RPO setup with fast failover (seconds-to-minutes RTO), ClickHouse Managed Postgres with 2 synchronous standbys (quorum) shows \~4× higher TPS, \~3× lower p50 latency, and \~7× lower p99 latency than Amazon RDS Multi-AZ with both single and two replicas.  
2. **Crunchy Bridge:** Against Crunchy Bridge's closest comparable HA configuration (1 asynchronous standby, fast failover with a small non-zero RPO), ClickHouse Managed Postgres (1 asynchronous standby) shows \~2.2× higher TPS, \~3.5× lower p50 latency, and \~1.75× lower p99 latency, while also providing stronger durability guarantees.

### Shared-storage architecture

For the shared-storage services, comparing at matched primary compute size:

3. **Aurora Postgres:** ClickHouse Postgres demonstrates a 2×+ throughput and latency advantage with a similarly configured PostgreSQL primary compute size with 1 standby.  
4. **Neon:** ClickHouse Postgres demonstrates a 3×+ throughput and latency advantage with a similarly configured PostgreSQL primary compute size.

## Conclusion

We’re happy to have added HA support. It better reflects a production-ready managed Postgres deployment and helps users understand the performance impact of different data durability implementations.

We’re not done yet, and we have plenty of ideas for where to take PostgresBench next. Areas we plan to invest in include adding more managed Postgres providers, making benchmark duration configurable, introducing additional workloads such as TPC-C and TPROC-C, and exposing more configuration options, including PostgreSQL configuration parameters. We also plan to analyze the cost-performance trade-offs across managed Postgres providers, similar to what we’ve been doing with [CostBench](https://clickhouse.com/blog/costbench-data-warehouse-cost-performance) for ClickHouse. Your feedback will help shape what comes next as we work toward making PostgresBench the default, fully reproducible benchmark for managed Postgres services.

[PostgresBench](https://github.com/ClickHouse/PostgresBench/) is open source and available on GitHub. Please review the methodology, reproduce the benchmarks, and contribute support for additional vendors.

---

## Get started with ClickHouse Managed Postgres today

Interested in seeing how ClickHouse Managed Postgres works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-1354-get-started-with-clickhouse-managed-postgres-today-sign-up&utm_blogctaid=1354)

---



