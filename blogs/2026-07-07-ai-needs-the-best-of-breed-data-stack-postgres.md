---
title: "AI needs the best-of-breed data stack: Postgres and ClickHouse"
date: "2026-07-07T17:09:10.322Z"
author: "Sai Srirampur"
category: "Product"
excerpt: "AI applications are driving explosive data growth and collapsing the line between transactional and analytical workloads, making the best-of-breed combination of Postgres and ClickHouse — increasingly tied together through CDC, native querying, and observ"
---

# AI needs the best-of-breed data stack: Postgres and ClickHouse

Over the past few years working with thousands of companies on [Postgres](https://www.postgresql.org/) and [ClickHouse](https://clickhouse.com/), I've watched AI change what applications demand from their databases. Every AI application is a data application: agents generate huge volumes of operational data, and users expect real-time answers built on that data, often in the same request. That changes what applications demand from their databases. 

In this post, I want to explore what AI applications actually need from their data layer, why Postgres and ClickHouse are increasingly becoming the natural combination for those workloads and our investments in making this combination very accessible to developers. 

**TL;DR** AI is accelerating data growth at an unprecedented scale and is collapsing the traditional divide between transactional (OLTP) and analytical (OLAP) [workloads](https://clickhouse.com/resources/engineering/oltp-vs-olap). Meeting these demands requires best-of-breed databases, [Postgres](https://www.postgresql.org/) and ClickHouse, each excelling at what it was designed to do, while still working together seamlessly.

## What AI needs, and how it's changing the data landscape {#what-ai-needs-and-how-its-changing-the-data-landscape}

### AI is pushing the data layer to new limits {#ai_is_pushing_the_data_layer_to_new_limits}

AI-native applications generate far more data than traditional software. Every prompt, response, tool call, evaluation, and user interaction becomes data, driving explosive growth in both data volume and query concurrency.  

Here is a data-point showing the scale I am talking about. Across a sample of AI-native companies using Postgres and ClickHouse, we observed an average data increase of **more than 1,000% over six months**, adding **over 85 TB of data**.

<img src="/uploads/postgres_clickhouse_jul2026_image4_a4cd08fde5.png" style="width: 75%; display: block; margin: 24px auto;" alt="" />

Also, as AI moves beyond vibe-coded apps into production systems, the tradeoffs are changing. Applications are making mission-critical decisions and operating across a larger surface area and at greater scale, raising the bar for reliability and security at the data layer.

To keep up with these demands, AI needs a data layer that can ingest, process, and query massive volumes of data in real time, always available and secure. Fast provisioning and instant branching are nice, but they matter little if the underlying data stack isn’t fast, reliable or secure.

### AI needs OLTP and OLAP working together in real-time {#ai_needs_oltp_and_olap_working_together_in_real_time}

LLM-powered applications, AI-generated insights, anomaly detection, recommendation engines, and natural language interfaces all demand a much tighter feedback loop between transactional and analytical databases. Data written to a transactional database must become available for analytical queries almost immediately, whether to evaluate a potentially fraudulent transaction or diagnosing a production incident.

In these scenarios, the traditional pattern of moving data into a warehouse through hourly or minutely ETL is no longer sufficient. Transactional and analytical databases must operate in real time, with only seconds separating when data is written from when it is available for analysis.

### Open source foundations and costs matter {#open_source_foundations_and_costs_matter}

A similar shift is underway in AI infrastructure. As teams grow more wary of proprietary LLM lock-in and mounting token costs, they're also rethinking the flexibility and economics of their data stack. Open-source databases solve both: they offer self-hosted or managed deployment, the freedom to switch vendors as needs evolve, and often significantly lower costs.

## Why Postgres + ClickHouse is winning {#why-postgres-clickhouse-is-winning}

The above requirements are reshaping the data stacks AI-native companies choose. Postgres and ClickHouse are increasingly becoming the default choice, combining best-in-class real-time transactions and analytics on a strong open-source foundation. 

Let's understand on why this is happening.

### Postgres and ClickHouse are best-of-breed open source databases {#postgres_and_clickhouse_are_best_of_breed_open_source_databases}

**Postgres**, on the one hand, is the most popular open-source transactional database in the world. It offers rock-solid support for transactions,  including low-latency CRUD operations, ACID compliance, rich indexing, a full SQL interface that supports virtually any query, a robust extension framework, and a vast ORM and application ecosystem, making it the default backend for web and AI applications everywhere.

**ClickHouse**, on the other hand, is the fastest analytical database on the planet. It offers purpose-built capabilities including columnar storage, skip indexes, incremental materialized views, distributed cache, native JSON and full-text search, the recently introduced lazy materialization, and hundreds of optimizations, laser-focused on blazing-fast real-time analytics.

Both are enterprise-ready, offering proven capabilities for high availability, reliability, and security. 

Beyond that, they share the same open-source philosophy, backed by large and active communities. As a fun fact, Postgres recently celebrated its 30th anniversary as an Open Source database, while ClickHouse marked its 10th. 

<img src="/uploads/postgres_clickhouse_jul2026_image3_e41dbaac37.png" style="width: 75%; margin: 8px 0;" alt="" />

[Blog](https://about.gitlab.com/blog/two-sizes-fit-most-postgresql-and-clickhouse/) by cofounder of GitLab on how Postgres and ClickHouse complement each other and solve most data problems.

#### Developers love Postgres and ClickHouse {#developers_love_postgres_and_clickhouse}

Postgres offers one of the richest ecosystems of tools and integrations in the industry, while ClickHouse combines familiar SQL, effortless local development with a single binary, and analytical performance that rarely requires extensive tuning. Together, they deliver a dev experience that feels refreshingly simple: “it just works" This is reflected in their vast adoption, from tens of thousands of startups and AI-native companies to enterprises like [GitLab](https://about.gitlab.com/blog/two-sizes-fit-most-postgresql-and-clickhouse/), [Instacart](https://tech.instacart.com/real-time-fraud-detection-with-yoda-and-clickhouse-bd08e9dbe3f4), and [Cloudflare](https://blog.cloudflare.com/http-analytics-for-6m-requests-per-second-using-clickhouse/).

<img src="/uploads/postgres_clickhouse_jul2026_image1_44ca825776.png" style="width: 75%; display: block; margin: 24px auto;" alt="" />

[DB-Engines](https://db-engines.com/en/ranking) shows Postgres and ClickHouse as the most popular open source OLTP and OLAP databases, respectively, with both continuing to grow in popularity.

### Unifying OLTP and OLAP with Postgres and ClickHouse {#unifying_oltp_and_olap_with_postgres_and_clickhouse}

***Our approach here is simple: embrace Postgres and ClickHouse as the leading open source databases for OLTP and OLAP, and make the integration between them as seamless and native as possible for devs.***

We've been investing across the stack to make this happen. For data movement, we have [PeerDB](https://github.com/PeerDB-io/peerdb), which powers [ClickPipes](https://clickhouse.com/docs/integrations/clickpipes/postgres) for Postgres and provides Change Data Capture (CDC) with single-digit-second replication. It's battle-tested by more than 1,000 companies running multi-terabyte Postgres deployments. It implements purpose-built capabilities like [parallel snapshotting](https://clickhouse.com/docs/integrations/clickpipes/postgres/parallel_initial_load), automatic schema evolution, native Postgres and ClickHouse monitoring and resilient replication, making enterprise-scale CDC feel almost magical for customers.

For querying, we have the [`pg_clickhouse`](https://github.com/clickHouse/pg_clickhouse) extension that lets applications query ClickHouse directly from Postgres, making Postgres the single interface for both transactional and analytical workloads while transparently pushing analytical queries to ClickHouse.

For observability, [`pg_stat_ch`](https://github.com/ClickHouse/pg_stat_ch) complements the stack by streaming Postgres query telemetry into ClickHouse, enabling low-overhead, long-term observability and performance analysis. Because telemetry is stored in ClickHouse instead of Postgres itself, you can retain months of execution statistics and perform high-cardinality analysis without impacting OLTP performance.

We also launched [**Postgres managed by ClickHouse**](https://clickhouse.com/cloud/postgres), a fully managed Postgres service that combines Postgres with local NVMe storage for [industry-leading OLTP performance](https://clickhouse.com/blog/postgresbench) and native ClickHouse integration through CDC and pg_clickhouse. High availability, PITR, read replicas, forks, and end-to-end encryption come built in, giving developers a unified data stack that is [enterprise-ready](https://clickhouse.com/blog/enterprise-postgres-service-in-clickhouse-cloud).

There are multiple other initiatives that deepen the integration of Postgres and ClickHouse while continuing to let each do what it does best!

The diagram below depicts the Unified Data Stack, highlighting Postgres for OLTP, ClickHouse for OLAP, continuous replication between the two, and a unified query layer via the pg_clickhouse extension.

<img src="/uploads/postgres_clickhouse_jul2026_image2_9947261abd.png" style="width: 75%; display: block; margin: 24px auto;" alt="" />

#### Comparing best-of-breed and unified storage architectures {#comparing_best_of_breed_and_unified_storage_architectures}

The database industry has seen multiple attempts over the past decade to unify OLTP and OLAP into a single database engine. More recently, we've also seen architectures built around unified storage and data lakes. 

These approaches are technically interesting, but they also tie developers to proprietary platforms and ask a single system to optimize for workloads with fundamentally different requirements. OLTP and OLAP exist for a reason: row and column-oriented storage are each optimized for different access patterns and performance characteristics. 

Likewise, data lakes excel at data warehousing use-cases, and weren't designed for the low-latency, high-concurrency demands of real-time, customer and agent-facing applications. You can layer operational capabilities on top of these architectures, but they remain constrained by the need to support open table formats and a general-purpose storage layer. As a result, they inevitably involve tradeoffs that make it difficult to match the performance of storage engines like MergeTree, which are purpose-built for real-time analytics.

This distinction also reflects our strategy at ClickHouse: a best-of-breed approach. We focus on making MergeTree the best engine for real-time analytics while continuously innovating around open table formats for the data warehousing use-case.

## The future of AI is a best-of-breed data stack {#the-future-of-ai-is-a-best-of-breed-data-stack}

AI isn't making the distinction between OLTP and OLAP disappear, it's making it more important than ever. The applications defining this era need transactional databases that can reliably capture every interaction, analytical databases that can process that data in real time, and seamless integration between the two.

We believe the future isn't a single proprietary platform trying to optimize for fundamentally different workloads. It's an open, best-of-breed data stack built on Postgres and ClickHouse, where each database does what it does best while working together as one.

That's the vision we're building toward. From enterprise-grade CDC with PeerDB and ClickPipes, to `pg_clickhouse`, `pg_stat_ch`, and **Postgres managed by ClickHouse**, every investment is aimed at making Postgres and ClickHouse feel like a single, integrated stack for developers.


---

## Try Postgres managed by ClickHouse

ClickHouse + Postgres has become the unified data stack for applications that scale. With Managed Postgres now available in ClickHouse Cloud, this stack is a day-1 decision.

[Sign up](https://clickhouse.com/cloud/postgres?loc=blog-cta-1224-try-postgres-managed-by-clickhouse-sign-up&utm_blogctaid=1224)

---