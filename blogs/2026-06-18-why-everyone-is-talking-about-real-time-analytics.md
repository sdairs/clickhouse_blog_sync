---
title: "Why everyone is talking about real-time analytics (a note from “the yellow company”)"
date: "2026-06-18T18:57:19.831Z"
author: "ClickHouse"
category: "Product"
excerpt: "For years, real-time analytics was treated as a niche requirement. We believed otherwise. So why is everyone talking about it now?"
---

# Why everyone is talking about real-time analytics (a note from “the yellow company”)

There has been a lot of discussion recently around real-time analytics. For years, this was often dismissed as a small use case, relevant to a smaller set of operational or customer-facing workloads. We always believed otherwise. 

Customer-facing analytics, observability, fraud detection, operational applications, and AI agents all depend on fresh data and low-latency queries.

It seems others are now recognizing the category that ClickHouse and our customers have defined for years. It reflects the journey ClickHouse has been on, from an open-source project to serving more than 4,000 customers and over[ $250M in ARR](https://clickhouse.com/blog/thank-you-for-building-with-us). 

It feels like the right moment to revisit two principles we believe matter: openness and a clear definition of what a real-time analytics database actually is.

## Real-time claims deserve real benchmarks

The data industry has a long history of benefiting from open benchmarks. Whether it is [ClickBench](https://benchmark.clickhouse.com), [CostBench](https://clickhouse.com/benchmarks/costbench), [PostgresBench](https://postgresbench.clickhouse.com/), [TPC benchmarks](https://clickhouse.com/blog/tpc-h-clickhouse-cloud-vs-snowflake-databricks-bigquery-redshift), or community-led testing, customers are best served when performance claims can be independently verified.

A useful benchmark should be transparent about what is being measured, reproducible by anyone willing to run it, and clear about the conditions under which the results were achieved. Otherwise, it becomes difficult to distinguish between a meaningful measurement and a marketing claim.

![clickbench.png](https://clickhouse.com/uploads/Blog_Costs_014_291362ced8.png)

> We believe benchmarks should be open, transparent, and reproducible. All of ClickHouse’s benchmarks are publicly available and reproducible, including [ClickBench](https://benchmark.clickhouse.com), [PostgresBench](https://postgresbench.clickhouse.com/), [JSONBench](https://jsonbench.com) and our recently announced [CostBench](https://clickhouse.com/benchmarks/costbench). You can explore the methodology, datasets, queries, and results on our dedicated benchmarks page and reproduce the results yourself.

This is particularly important in real-time analytics, where benchmark results can vary dramatically depending on what is actually being tested. Two systems can produce similar latency numbers under controlled conditions while behaving very differently in production. 

A benchmark showing sub-second queries on a static dataset is useful, but it does not necessarily tell us how a system behaves when new data is continuously arriving, when working sets exceed memory, or when hundreds or thousands of concurrent queries are competing for resources.

As more attention is given to real-time analytics, we hope the industry continues moving toward benchmarks that are open, reproducible, and explicit about what they are measuring. 

## What actually makes a real-time analytics database?

Our experience building systems for this workload has taught us that many of the properties that determine success in production are also the easiest things to omit from a benchmark. Freshness, continuous ingestion, concurrency, transformation latency, and efficiency at scale rarely fit neatly into a single chart on stage, yet they often determine whether a system succeeds or fails once it reaches production.

For this reason, it is worth asking not only how real-time analytics should be benchmarked, but what a real-time analytics database should actually be expected to do. Coincidentally, we recently explored this [question in depth](https://clickhouse.com/blog/selecting-a-real-time-analytical-database). In summary, any platform claiming real-time analytics capabilities should be able to answer a few simple questions:

### Does ingestion scale without degrading queries? 

Continuous writes should not pull query latency along with them. In practice, that means an ingestion path that can run on isolated resources from the read path, and a concurrency model that holds tail latencies bounded as writers grow. ClickHouse, for example, uses consensus-based coordination through Keeper rather than optimistic concurrency. It pays a small coordination cost on every write, but keeps tail latencies predictable at the high insert concurrency seen in real-time workloads.

### Is data queryable within a second or two of being written? 

At real-world scale, the realistic target is a delay measured in milliseconds to a couple of seconds, with no catalog or manifest refresh sitting in the middle.

### Do transformations update incrementally, and not on a schedule? 

Materialized views, rollups, and pre-aggregations (done using AggregatingMergeTree in ClickHouse) should update with each insert, not on an interval. This ensures that they're immediately applied and enforce a delay on data availability. 

### Can you bias the system towards read-time or write-time work? 

Different workloads want different trade-offs. For some, you want indexes and aggregations built at write time so the freshest queries are immediately accelerated. For others, you want to keep the ingest throughput maximal and let the background work catch up. A real-time platform should expose that choice without forcing it. And index maintenance should never block ingestion. New data should be queryable as soon as it is committed, with or without its indexes fully built.

### Does a single engine serve all workloads? 

Text search, vector similarity, JSON, structured analytics. These should live in the same storage and query engine, not in four loosely coupled systems with their own freshness floors. 

### Is the performance shown on hot data, not just on cached benchmarks? 

The realistic question to ask of any platform is how fast its queries are on data that arrived a second ago, not how fast its repeated queries are on yesterday's table. The first number is what production looks like.

### Does resource efficiency hold up at scale? 

Real-time systems need to remain efficient as ingest volume, query concurrency, and retention grow. The important question is whether performance scales linearly with workload, or whether latency and compute costs begin to degrade disproportionately as traffic increases.

The common thread across these requirements is that real-time analytics is not a feature you switch on. It is a set of design decisions about ingest, storage, transformation, and query that have to be made consistently across the whole system. Either the platform was designed for this workload, or it is working hard to approximate it.

## Real-time analytics comes of age

One question worth asking is why real-time analytics has suddenly moved to the forefront. While several trends are contributing, we believe the rise of agentic workloads is [a major factor](https://clickhouse.com/blog/ai-redrawing-database-market). Agents consume data differently from humans. They issue more queries, operate continuously, and depend on fresh context to make decisions. As organizations deploy more of them, the combination of low latency, high concurrency, and fresh data is becoming a prerequisite rather than a luxury.

As the category continues to evolve, we hope two things become standard. First, open and reproducible benchmarks that allow customers to independently evaluate performance claims under realistic conditions. Second, a shared understanding of what real-time analytics actually requires beyond a single latency number. 

As the yellow company, we have been leading in real-time analytics for years, and believe it to be a foundational workload.

It’s nice to see the other colors finally recognizing it too.

