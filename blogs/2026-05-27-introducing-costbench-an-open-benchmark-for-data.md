---
title: "Introducing CostBench: an open benchmark for data warehouse cost-performance"
date: "2026-05-27T14:05:56.392Z"
author: "Tom Schreiber and Lionel Palacin"
category: "Engineering"
excerpt: "Introducing CostBench, an open benchmark that turns cloud data warehouse runtime and billing models into comparable performance-per-dollar results."
---

# Introducing CostBench: an open benchmark for data warehouse cost-performance

> **TL;DR**<br/>
CostBench is an open benchmark for cloud data warehouse cost-performance: performance-per-dollar, not just speed.<br/><br/>It helps teams choose the system that delivers the most performance per dollar for real-time analytical workloads.

<br/>

## Performance alone is only half the story

Most benchmarks tell you how fast a query runs. That is useful, but incomplete.

> In cloud data platforms, speed and cost are inseparable.  
 
If warehouse A is faster than warehouse B, A looks better on a performance chart. But if A costs three times more to run, the comparison changes. You might spend the same budget on a larger configuration of B, get more compute, and make B faster than A for less money overall.

That comparison is hard because every platform exposes cost differently: credits, DBUs, slot-seconds, compute units, RPUs.

![Blog-Bench2Cost.001.png](https://clickhouse.com/uploads/Blog_Bench2_Cost_001_341b09cafb.png)

The unit names differ, but the underlying question is the same: 

> How much compute did the system need to finish the workload, and what did that compute cost?

CostBench answers that question directly. It also exposes where cost-performance breaks: during ingest, while making data query-ready, or when serving reads.


## Why this matters in the AI era

Agentic analytics raises the pressure on every layer of the database.

New data never stops: events, transactions, logs, traces, user activity, fraud signals, operational state. At the same time, users and agents expect fast answers over fresh data.

> If the database is slow, the agent is slow. If the database is expensive, teams start rationing what agents can do: fewer retries, smaller datasets, less context, stale data.

In the AI era, fast and low-cost has to hold across the full analytics path: continuous ingest, query-ready preparation, and reads.

![Blog-Bench2Cost.002.png](https://clickhouse.com/uploads/Blog_Bench2_Cost_002_7f4af0a308.png)

**Read-side pressure** comes from query volume. A single user question can trigger many SQL queries: schema exploration, validation, retries, refinements, drilldowns, and follow-ups. Each extra query burns compute. At agentic scale, query volume turns directly into cost pressure.

**Write-side pressure** comes from real-time freshness: fresh data has to be continuously ingested, compressed, and organized so queries can skip more data. That work burns compute before the first query even runs, and determines how much compute those queries burn later.

## What CostBench measures

CostBench turns that pressure into a full-path cost-performance lens with two measurable dimensions:

* **Read-side cost-performance**: how much query performance you get per dollar.
* **Write-side cost-performance**: how efficiently each dollar turns fresh ingest into query-ready data. 


Together, they help answer the question that matters when choosing a platform: 
 
> Which system gives you the most performance per dollar for real-time analytical workloads?

![Blog-Bench2Cost.003.png](https://clickhouse.com/uploads/Blog_Bench2_Cost_003_c9407dbe1a.png)


The first release focuses on the read side: analytical queries over data that has already been loaded. We have also started measuring the write side, beginning with [Snowflake as a contrast point for ClickHouse](https://clickhouse.com/blog/write-side-cost-performance-snowflake-clickhouse). Broader write-side coverage will follow.

This gives CostBench a simple roadmap: expose whether real-time cost-performance holds across the full analytics pipeline, from making fresh data query-ready to querying it efficiently.


## The first results: read-side cost-performance

The first CostBench release turns read-side performance into a comparable performance-per-dollar result across major cloud data warehouses.

We compare ClickHouse Cloud, Snowflake, Databricks, BigQuery, and Redshift using 43 production-derived analytical queries on a real anonymized dataset, then apply [each vendor’s actual compute billing model](https://clickhouse.com/blog/how-cloud-data-warehouses-bill-you) to place every system on the same cost-performance plane: faster or slower, lower-cost or higher-cost.

![Blog-Bench2Cost.004.png](https://clickhouse.com/uploads/Blog_Bench2_Cost_004_66900fe22f.png)

ClickHouse Cloud is the only system that stays in the fast and low-cost zone as data scales. The nearest competitor is 23× worse in cost-performance.

That is the value of CostBench: it turns vendor-specific runtimes and billing models into a result teams can use when choosing a platform.


## Open and reproducible by design

CostBench is open because cost-performance claims should be inspectable.

The benchmark publishes the workload, scripts, configurations, pricing assumptions, raw JSON results, and methodology. If a result looks surprising, you can inspect the setup that produced it. If a configuration can be improved, it can be reviewed and corrected in the open.


## Try it yourself

Explore the results on the [ClickHouse benchmark hub](https://clickhouse.com/benchmarks), inspect the raw data, or clone the [CostBench repository](https://github.com/ClickHouse/CostBench) and run the benchmark yourself.

Cost-performance should not be a black box. CostBench makes it inspectable.

