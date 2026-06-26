---
title: "Why we rewrote WAL-G for Postgres backups in Rust: Meet WAL-RUS"
date: "2026-06-25T16:00:33.907Z"
author: "Sai Srirampur and Philip Dubé"
category: "Engineering"
excerpt: "How we built WAL-RUS, an open-source Rust-based Postgres backup tool that reduces virtual memory usage by over 70% compared to WAL-G while maintaining full compatibility."
---

# Why we rewrote WAL-G for Postgres backups in Rust: Meet WAL-RUS

![WAL-RUS Blog Banner.jpg](https://clickhouse.com/uploads/WAL_RUS_Blog_Banner_00f644032a.jpg)

Postgres backups are one of those pieces of infrastructure that should be boring. They sit in the background, continuously archiving WAL files, uploading backups, and making sure that when something goes wrong, recovery is possible.

At ClickHouse Cloud, this path is critical. WAL archival is what allows us to preserve durability and recoverability for our Postgres services. WAL-G has been a strong and reliable tool for this job. It is mature, battle-tested, and has served the Postgres community well.

But as we pushed Postgres into tighter and more resource-constrained environments, we started hitting a specific problem: memory predictability.

That led us to build [**WAL-RUS**](https://github.com/ClickHouse/wal-rus), an **open-source** Rust-based implementation of Postgres backup and WAL archival tooling, designed for predictable memory-efficiency and WAL-G compatibility.

## The problem {#the-problem}

WAL-G is written in Go, a garbage-collected language. While Go makes it easy to build reliable infrastructure software, garbage-collected runtimes make memory usage harder to predict, especially for long-running services like WAL archival.

The challenge isn't just **resident memory** (memory actively being used), but also **virtual memory** (memory reserved from the operating system). Go's runtime manages its own memory pools and can [reserve significantly more virtual memory](https://go.dev/doc/faq#Why_does_my_Go_process_use_so_much_virtual_memory) than the application is actively using. As workloads change, this footprint can fluctuate in ways that are difficult to reason about and tune. The [Go GC guide](https://go.dev/doc/gc-guide) describes this as a characteristic "sawtooth" pattern, where memory usage grows between garbage collection cycles and then falls after collection, making it difficult to predict peak memory consumption and provision resources efficiently.

For operators, that creates a simple but important problem: **how much memory should be reserved for backup infrastructure?**

The answer is usually "more than necessary" to avoid unexpected memory pressure. Memory budgeted for WAL archival is memory that cannot be confidently allocated to Postgres itself for queries, shared buffers, and page cache. [Postgres runs most reliably with overcommit disabled](https://www.postgresql.org/docs/current/kernel-resources.html#LINUX-MEMORY-OVERCOMMIT), making virtual memory a valuable resource modern software often leaves as an afterthought.

WAL-G remains a proven and reliable tool, but as we scaled Postgres into increasingly resource-constrained environments, we wanted a backup system with a more predictable memory profile, delivering the same functionality while consuming fewer resources and making capacity planning simpler.

## The solution: Introducing WAL-RUS {#the-solution-introducing-wal-rus}

We weren't looking for new functionality. WAL-G is a mature and reliable backup system we’re happy to contribute to. Our goal was to preserve core functionality and compatibility while providing a more predictable resource profile.

WAL-RUS is a Rust implementation of Postgres backup and WAL archival tooling built to address the operational challenges we encountered with memory predictability and resource usage.

**1\. Predictable Resource Usage:** Unlike garbage-collected runtimes, Rust gives us direct control over [memory allocation and concurrency](https://github.com/ClickHouse/wal-rus/blob/176a430d021bab6016c828bbd1dbe85ac1396cfc/src/main.rs#L22). WAL-RUS uses bounded worker pools and carefully controlled concurrency, making memory consumption easier to reason about and reducing the need to over-provision resources for backup infrastructure.

**2\. Built for Continuous WAL Archival:** WAL-RUS prioritizes WAL-G’s daemon architecture. Instead of spawning a new process and establishing new connections for every WAL file, it maintains persistent object storage connections that continuously process archival requests in the background.

**3\. Optimized for Streaming Workloads:** WAL archival is fundamentally a streaming problem: read WAL files, compress them, and upload to object storage. WAL-RUS minimizes unnecessary buffering and data copies throughout this pipeline, allowing it to perform the same archival work with a smaller and more predictable memory footprint.

**4\. WAL-G Compatibility:** WAL-RUS uses the same `WALG_` configuration variables as WAL-G and is continuously tested for interoperability. WAL-G can read archives generated by WAL-RUS, and WAL-RUS can read archives generated by WAL-G, making migration straightforward for existing deployments.

## Benchmarks {#benchmarks}

To evaluate WAL-RUS, we built a [reproducible benchmark](https://github.com/ClickHouse/wal-rus/tree/main/bench) that compares WAL-RUS, WAL-G, and pgBackRest under a sustained, WAL-heavy PostgreSQL workload. The benchmark continuously generates WAL, archives it to S3, and measures how efficiently each archiver uses memory while keeping up with WAL generation. To ensure a fair comparison, all three tools were configured with **four concurrent archival workers**.

### Memory usage {#memory-usage}

Memory efficiency was the primary motivation behind WAL-RUS, making memory consumption the first metric we examined.

![image (23).png](https://clickhouse.com/uploads/image_23_1483929622.png)

WAL-G reached nearly **2.8 GB** of peak virtual memory during the benchmark, while WAL-RUS remained below **1 GB**, a reduction of more than **70%**. WAL-RUS also maintained a stable memory profile throughout the run, making its resource requirements easier to reason about in production environments. pgBackRest deserves credit here as well. As a C-based implementation without a garbage-collected runtime, it has tight control over memory allocation.

### WAL archival throughput {#wal-archival-throughput}

![image (24).png](https://clickhouse.com/uploads/image_24_a91bdef1e0.png)

Both WAL-RUS and WAL-G consistently maintained minimal backlog throughout the benchmark, demonstrating they could keep up with the workload being generated. pgBackRest accumulated a larger backlog during periods of intense WAL activity, illustrating their architectural tradeoffs between daemon-based and process-based archival throughput.

### CPU utilization {#cpu-utilization}

![image (25).png](https://clickhouse.com/uploads/image_25_66b4c49349.png)

CPU utilization is less important, but good to keep an eye on. Usage is comparable between all three, primarily computing LZ4 compression.

## Summary and conclusion {#summary-and-conclusion}

WAL-RUS was built to solve a practical problem: delivering reliable PostgreSQL backups and WAL archival with a smaller, more predictable resource footprint. By combining Rust's explicit memory management with a daemonized streaming architecture, WAL-RUS achieves archival throughput comparable to WAL-G while significantly reducing memory consumption.

Importantly, WAL-RUS remains fully compatible with existing WAL-G archives and configuration, making adoption straightforward for existing deployments. WAL-RUS introduces support for using Postgres 17’s wal summaries for incremental backups, which we’re working to [upstream to WAL-G](https://github.com/wal-g/wal-g/pull/2293).

We didn't build WAL-RUS because WAL-G lacked functionality. WAL-G remains a mature and battle-tested project. We built WAL-RUS because we wanted tighter control over resource usage while preserving compatibility with the ecosystem that WAL-G helped establish.

As we continue to develop and harden the project, we plan to make WAL-RUS the default backup and WAL archival mechanism for our managed Postgres offering in ClickHouse Cloud.

The project is open source, and we welcome feedback, testing, and contributions!


---

## Try Postgres managed by ClickHouse

ClickHouse + Postgres has become the unified data stack for applications that scale. With Managed Postgres now available in ClickHouse Cloud, this stack is a day-1 decision.

[Sign up](https://clickhouse.com/cloud/postgres?loc=blog-cta-1090-try-postgres-managed-by-clickhouse-sign-up&utm_blogctaid=1090)

---