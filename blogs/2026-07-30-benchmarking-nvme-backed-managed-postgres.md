---
title: "Benchmarking NVMe-backed Managed Postgres: PlanetScale and ClickHouse"
date: "2026-07-30T14:30:07.727Z"
author: "Sai Srirampur"
category: "Engineering"
excerpt: "We ran ClickHouse Managed Postgres and PlanetScale on the same hardware. ClickHouse delivered up to 54% higher throughput with lower latency."
---

# Benchmarking NVMe-backed Managed Postgres: PlanetScale and ClickHouse

We launched [PostgresBench](https://clickhouse.com/blog/postgresbench), a fully reproducible, open-source benchmark for managed PostgreSQL services, a few months ago. It was well received, and we received valuable [feedback](https://clickhouse.com/blog/postgresbench-ha) from the community on how to evolve it. 

One of the most common requests was to include locally NVMe-backed PostgreSQL services such as PlanetScale Postgres alongside ClickHouse Managed Postgres. Based on that feedback, we recently added PlanetScale Postgres (their Metal offering) to PostgresBench.

This blog presents the benchmark results and analyzes why the two services performed differently, even though both ClickHouse Managed Postgres and PlanetScale Postgres are built on similar NVMe-backed infrastructure.

![blog-screenshot.png](https://clickhouse.com/uploads/blog_screenshot_fb1e854de4.png)

## **Benchmark**

PostgresBench uses **pgbench**, PostgreSQL's standard benchmarking tool, with a TPC-B-like workload consisting of short, highly concurrent transactions with frequent inserts, updates, and deletes. To ensure the benchmark is not network-bound, we use PostgreSQL databases with **100 GB** and **500 GB** of data. Below is the `pgbench` command used for the benchmark.

The benchmark uses the following command:

```bash
pgbench -c 256 -j 16 -T 600 -M prepared -P 30 \
  -s $SCALE_FACTOR \
  -h $PGHOST -p $PGPORT -U $PGUSER -d $PGDATABASE
```

## **Hardware**

To ensure a fair comparison, both services were benchmarked using **identical hardware**.


* **AWS r8gd.xlarge** and **r8gd.4xlarge** instances
* Local **NVMe** storage
* One primary with **two synchronous standbys** using quorum replication for high availability
* **us-west-2** AWS region

The benchmark client ran on a dedicated **16 vCPU, 64 GB** instance in the same region, ensuring the client was never the bottleneck.

**In short, both services were tested on the same VM family, instance sizes, region, and benchmark configuration.**

## Results


### ~100 GB dataset (scale 6849)

| System                      | Machine           | TPS       | Avg latency (ms) | P95 (ms) | P99 (ms) |
|-----------------------------|-------------------|----------:|-----------------:|---------:|---------:|
| PlanetScale Metal           | 16vCPU, 128GB RAM | 16,887.23 |           15.144 |   25.729 |   32.894 |
| ClickHouse Managed Postgres | 16vCPU, 128GB RAM | 25,429.48 |           10.073 |   20.228 |   29.146 |
| PlanetScale Metal           | 4vCPU, 32GB RAM   |  4,675.85 |           54.714 |   81.073 |  103.579 |
| ClickHouse Managed Postgres | 4vCPU, 32GB RAM   |  6,242.29 |           41.050 |   80.137 |  115.215 |

The results show that ClickHouse Managed Postgres consistently outperformed PlanetScale Metal across both instance sizes. On the **16 vCPU / 128 GB** configuration, ClickHouse delivered **25,429 TPS**, about **51% higher throughput** than PlanetScale's **16,887 TPS**, while reducing average latency from **15.1 ms** to **10.1 ms**, **~33% lower**.

On the **4 vCPU / 32 GB** configuration, ClickHouse achieved **6,242 TPS** vs **4,676 TPS**, a ~34% higher throughput and reduced average latency from **54.7 ms** to **41.1 ms** (~25% lower).

Tail latencies (P95/P99) were comparable on the smaller instance and consistently lower on the larger instance.


### ~500 GB dataset (scale 34247)

| System                      | Machine           | TPS       | Avg latency (ms) | P95 (ms) | P99 (ms) |
|-----------------------------|-------------------|----------:|-----------------:|---------:|---------:|
| PlanetScale Metal           | 16vCPU, 128GB RAM | 14,046.42 |           18.239 |   30.756 |   38.608 |
| ClickHouse Managed Postgres | 16vCPU, 128GB RAM | 21,693.71 |           11.809 |   23.859 |   31.369 |

The same trend continued with the larger **500 GB** dataset. On the **16 vCPU / 128 GB** configuration, ClickHouse Managed Postgres delivered **21,694 TPS**, compared to **14,046 TPS** for PlanetScale Metal, a **54% improvement in throughput**. At the same time, average latency dropped from **18.2 ms** to **11.8 ms**, with P95 and P99 latencies also consistently lower. 


## Why is ClickHouse Managed Postgres faster than PlanetScale Postgres?

The difference isn't the hardware. Both services were benchmarked on identical AWS r8gd instances with local NVMe storage, configured with one primary and two synchronous standbys using quorum replication. Both also acknowledge commits after one standby confirms the write (`ANY 1`), with `synchronous_commit` enabled. 
 
The performance difference comes from how the services are engineered around PostgreSQL. 
 
ClickHouse Managed Postgres applies several system-level optimizations that reduce CPU, memory, and I/O overhead. For example, it reserves memory using 2 MB huge pages, which reduces page-table overhead under highly concurrent workloads. On identical hardware, we [measured](https://clickhouse.com/blog/huge-pages-clickhouse-managed-postgres) this optimization alone improving throughput by about 12%. 
 
The write path is also optimized. We enable `wal_compression = lz4` and configure `max_wal_size` based on the instance size (up to 256 GB), reducing WAL volume and checkpoint frequency. This lowers the amount of data written to local NVMe and synchronously replicated to standbys. 
 
Based on the PostgreSQL settings exposed by PlanetScale Metal, we observed that `huge_pages` and `wal_compression` are disabled, and `max_wal_size` is set to 8 GB. There may be additional implementation differences that are not externally visible through `pg_settings`. 
 
Every subsystem gets the same treatment: wal-g is configured per machine, with upload concurrency and S3 part sizes computed from the vCPUs, memory, and NVMe layout it lands on; backups read the disk with direct I/O so the page cache stays with Postgres; writes are throttled when WAL archiving falls behind so the disk never fills. We have written up some of this so far: [huge pages](https://clickhouse.com/blog/huge-pages-clickhouse-managed-postgres), [strict memory overcommit](https://clickhouse.com/blog/strict-memory-overcommit-for-postgres), [the PgBouncer fleet](https://clickhouse.com/blog/pgbouncer-clickhouse-managed-postgres), [WAL-RUS](https://clickhouse.com/blog/walrus-postgres-backups-in-rust). There is more coming. Keep an eye on the [ClickHouse blog](https://clickhouse.com/blog). 
 
These results are based on the PostgresBench workload. While we expect the same engineering optimizations to benefit many real-world OLTP workloads, every application is different. We recommend validating performance with your own workload as part of a proof of concept.




---

## Get started with ClickHouse Managed Postgres today

Interested in seeing how ClickHouse Managed Postgres works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?intent=pg&loc=blog-cta-1458-get-started-with-clickhouse-managed-postgres-today-sign-up&utm_blogctaid=1458)

---