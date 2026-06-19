---
title: "What a difference 10 years of open source makes"
date: "2026-06-17T11:32:16.602Z"
author: "Al Brown"
category: "Engineering"
excerpt: "On June 15, 2016, ClickHouse went open source under the Apache 2.0 license. Ten years later, it's one of the most widely deployed analytical databases in the world. "
---

# What a difference 10 years of open source makes

On June 15, 2016, ClickHouse went open source under the Apache 2.0 license. Ten years later, it's one of the most widely deployed analytical databases in the world. And that's because of you. The 2,600+ people who have built, broken, debated, and contributed your way through a decade of monthly releases.

Alexey Milovidov, ClickHouse's creator and CTO, has [written his own reflections on the decade](https://clickhouse.com/blog/open-source-10).

## A decade in the open

[In 2025 alone](https://clickhouse.com/blog/alexey-favorite-features-2025), ClickHouse gained **277 new features, 319 performance optimizations, and 1,051 bug fixes** across twelve releases.

In 10 years that looks like:

- **2,600+ contributors**  
- **~48,000 GitHub stars**  
- **~239,000 commits**  
- **~800 releases**  
- **Hundreds of millions of downloads**  
- **200+ integrations**

But what have those ~240k commits been building towards?

![feature_timeline.png](https://clickhouse.com/uploads/feature_timeline_de8c8a9ef1.png)

## Joining the dots on JOINs

Asked on a release call when ClickHouse would stop optimizing join performance, Alexey's answer was: "We will never stop!"

He means it. Over [two years of focused join engineering](https://clickhouse.com/blog/clickhouse-fast-joins), ClickHouse became **26× faster** on the join-heavy TPC-H SF100 workload, comparing version 22.4 to 26.4, with the last year alone contributing roughly 6×:

- **Correlated subquery decorrelation:** queries that previously couldn't run at all now execute as ordinary joins.  
- **Lazy column replication:** 1.9× faster by avoiding physical row duplication when joins fan out.  
- **Runtime filters:** build-side join keys filter the probe side during execution, making queries 2.1× faster and dropping peak memory on one query from 1.24 GiB to 185 MiB.  
- **Statistics-based join reordering:** the optimizer reorders joins automatically. One six-table query went from 3,903.7 seconds to 2.7 seconds (1,450× faster) and from 99.1 GiB of memory to 3.9 GiB.

![fastjoinsprogress.png](https://clickhouse.com/uploads/fastjoinsprogress_c5df6c9dae.png)

## Updates, deletes, JSON, search, and vectors

Joins weren't the only thing moving. In about eighteen months, ClickHouse picked up real SQL updates, a true JSON type, full-text search, and production-grade vector search, all in the open.

### Real UPDATEs and DELETEs (25.7)

Column stores aren't supposed to be good at updates, but rules are meant to be broken. ClickHouse 25.7 (July 2025) shipped standard SQL UPDATE, built on [patch parts](https://clickhouse.com/blog/updates-in-clickhouse-2-sql-style-updates): tiny delta parts written alongside your data instead of rewriting whole columns. On a [600-million-row benchmark](https://clickhouse.com/blog/updates-in-clickhouse-3-benchmarks), that works out to **1,700× faster than classic mutations** for bulk updates and up to 2,400× for single-row updates.

### A true JSON type (25.3)

ClickHouse 25.3 (March 2025) shipped a [production-ready JSON type](https://clickhouse.com/blog/clickhouse-release-25-03): real columnar JSON, built on the Variant and Dynamic types and plugged into all the usual query acceleration. And 25.8 made complex JSON [58× faster with 3,300× less memory](https://clickhouse.com/blog/json-data-type-gets-even-better). On the [billion-document JSON benchmark](https://clickhouse.com/blog/json-bench-clickhouse-vs-mongodb-elasticsearch-duckdb-postgresql), one billion Bluesky events, ClickHouse ran aggregations 2,500× faster than MongoDB with 40% less storage, and fit in 99 GB what took PostgreSQL 622 GB.

### Full-text search (26.2)

As of 26.2 (March 2026), ClickHouse has native full-text search. Columnar [inverted indexes](https://clickhouse.com/blog/clickhouse-full-text-search) that went experimental in 25.9, beta in 25.12, and [production-ready in 26.2](https://clickhouse.com/blog/full-text-search-ga-release). Cold text queries run 7–10× faster with the index, and one GitHub-events example dropped from a 193-second scan to 0.422 seconds.

Getting full-text search right was a [multi-year journey](https://clickhouse.com/blog/clickhouse-search-with-inverted-indices) with many contributions. Three iterations later, it's [one of the most powerful full-text search implementations you can run anywhere](https://clickhouse.com/blog/elasticsearch-log-analytics-clickhouse).

### Vector search grew up (25.8 and beyond)

Vector similarity indexes (HNSW) [hit GA in 25.8](https://clickhouse.com/blog/clickhouse-2025-roundup). Then came [QBit](https://clickhouse.com/blog/qbit-vector-search) (October 2025), a data type you won't find anywhere else: it lets you pick your vector precision at query time instead of locking it in when you design the table. That buys roughly 2× faster searches at the same recall, brute-force memory down from 6.05 GiB to 740 MiB, and 4.3× higher throughput.

## Faster by default

Every release has engine work under the hood, as we always want each new version to be faster than the last without you changing a thing. And when you want to push further, we want you to have the right tools for that too:

- [**Lazy materialization**](https://clickhouse.com/blog/clickhouse-gets-lazier-and-faster-introducing-lazy-materialization) (25.4, on by default): defer reading large columns until they're actually needed. A Top-N query went from 219 seconds to 139 milliseconds (1,576× faster) with 40× less I/O and 300× lower peak memory. "You get the speed without lifting a finger."  
- [**Query condition cache**](https://clickhouse.com/blog/introducing-the-clickhouse-query-condition-cache) (25.3, now on by default): one bit per filter condition per granule, so repeated dashboard-style queries skip data the primary index can't, a 13× speedup in the demo workload.  
- [**Projections as secondary indexes**](https://clickhouse.com/blog/projections-secondary-indices) (25.6, polished through 26.1): _part_offset-based projections behave like secondary indexes without duplicating the data. One example cut rows scanned from 30.73 million to 16,384, a 1,876× reduction.  
- [**CoalescingMergeTree**](https://clickhouse.com/blog/clickhouse-25-6-coalescingmergetree) (25.6): a table engine that keeps the latest non-null value per column, turning partial updates into plain appends. Contributed by community member Konstantin Vedernikov.  
- [**Parallel replicas**](https://clickhouse.com/blog/clickhouse-parallel-replicas) (beta): spread a single query across every replica in the cluster, so adding replicas makes the same query faster. A raw GROUP BY over 100 billion rows ran in 414 milliseconds, peaking at 241.83 billion rows per second.

## Open benchmarks, open methodology

Database benchmarketing has a deservedly bad reputation with cherry-picked workloads, hidden configs, numbers nobody can reproduce. 

Just like the engine itself, ClickHouse benchmarks are open-source, with all the data, schemas, queries, scripts, and results, so anyone can run and validate. Over the years that's grown into a whole family:

- [**ClickBench**](https://benchmark.clickhouse.com/): the analytical database benchmark, now covering 50+ systems, with every script and result [on GitHub](https://github.com/ClickHouse/ClickBench). Anyone can submit a system, and many vendors have.  
- [**JSONBench**](https://github.com/ClickHouse/JSONBench): a billion Bluesky events testing how databases really handle semi-structured data, the benchmark behind the JSON numbers above.  
- [**TPC-H**](https://github.com/ClickHouse/tpc-h-openhouse): the classic warehouse benchmark, where ClickHouse [runs all 22 SF100 queries in around 20 seconds](https://clickhouse.com/blog/tpc-h-clickhouse-cloud-vs-snowflake-databricks-bigquery-redshift) on a single node. At SF10, running the entire suite costs $0.009.  
- [**CostBench**](https://github.com/ClickHouse/CostBench): an open cost-performance benchmark [introduced in May 2026](https://clickhouse.com/blog/costbench-data-warehouse-cost-performance), publishing workloads, pricing assumptions, and raw results, on the principle that "cost-performance should not be a black box."  
- [**PostgresBench**](https://github.com/ClickHouse/PostgresBench): the [same open treatment](https://clickhouse.com/blog/postgresbench) applied to managed Postgres services, built on the standard pgbench tool.

Ten years in, the open ethos extends from code to methodology. Don't trust our numbers; run them.

## Meeting you where you are

ClickHouse has always been easy to pick up, being one binary that runs happily on a laptop. But how you can use it has been evolving, from agents running ClickHouse for you, to running custom code inside UDFs, to querying ClickHouse with Postgres:

- [**clickhousectl**](https://clickhouse.com/blog/introducing-clickhousectl-official-cli-for-clickhouse-local-and-cloud): the official CLI, itself an [Apache 2.0 project](https://github.com/ClickHouse/clickhousectl) written in Rust. One line `curl https://clickhouse.com/cli | sh` gets you installed, giving you local version management, project scaffolding, local server management and ClickHouse Cloud control.  
- [**AI functions**](https://clickhouse.com/docs/sql-reference/functions/ai-functions) (26.4): call an LLM straight from SQL. aiGenerate, aiClassify, aiExtract, and aiTranslate work against OpenAI, Anthropic, or any OpenAI-compatible endpoint, so you can classify or enrich rows mid-query.  
- [**31 SQL dialects**](https://presentations.clickhouse.com/2026-release-26.3/) (26.3): SET dialect = 'polyglot' and ClickHouse accepts queries written in other dialects, from Postgres to Snowflake to Spark, via a library seeded from sqlglot.  
- [**WebAssembly UDFs**](https://clickhouse.com/blog/clickhouse-release-26-03) (26.3, experimental): write user-defined functions in any language that compiles to Wasm, sandboxed in Wasmtime.  
- [**PromQL**](https://clickhouse.com/blog/open-house-2026-day-1) (experimental): query ClickHouse in Prometheus's query language, with integration in open-source ClickStack.  
- [**pg_clickhouse**](https://clickhouse.com/blog/introducing-pg_clickhouse): an open-source Postgres extension that lets standard Postgres query ClickHouse with transparent pushdown.

## A community of builders

As we say in every release post: "A special welcome to all the new contributors!"

With every release, new contributors are joining the ClickHouse community to help build the world's fastest analytical database. Every contribution, big or small, is what makes ClickHouse, ClickHouse.

If you've been part of the ClickHouse journey for a while, you might recognize some frequent flyers:

- **Amos Bird**, a legendary long-time contributor, built the projections indexing syntax that shipped in 26.1.  
- **Michael Jarrett** contributed automatic minmax indices in 26.2, after validating sub-0.2-second Top-N queries on a 50-billion-row table as a user in 25.12.  
- **Jiebin Sun** made uniqExact 3–15× faster on high-core-count machines in 26.4.  
- **Yarik Briukhovetskyi** sped up RIGHT and FULL JOIN in 26.2.  
- **Nihal Z. Miaji** shipped dictGetKeys in 25.12, faster DISTINCT on LowCardinality columns in 26.1, and the primes table function in 26.2.  
- **Konstantin Vedernikov** contributed an entire table engine, the CoalescingMergeTree covered above.

At Open House 2026, we launched the [Community Champions Program](https://clickhouse.com/blog/open-house-2026-day-2) to recognize the people who answer the questions, write the integrations, and file the bug reports that keep the project honest.

## To the next ten years

To everyone who has used and contributed to ClickHouse: [thank you!](https://clickhouse.com/blog/thank-you-for-building-with-us)

> "This momentum and achievement is thanks to the community that has built, broken, debated, contributed to, and pushed ClickHouse forward long before there was a company to put a logo on it. Thank you." - Aaron Katz, CEO, ClickHouse Inc.

If you want to be part of the next ten: [star or contribute on GitHub](https://github.com/ClickHouse/ClickHouse), join a monthly release call, or raise your hand for the Community Champions Program.

The ClickHouse journey has only just begun.