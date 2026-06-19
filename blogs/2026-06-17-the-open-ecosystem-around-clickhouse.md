---
title: "The open ecosystem around ClickHouse"
date: "2026-06-17T15:41:30.993Z"
author: "Al Brown"
category: "Company and culture"
excerpt: "Around any good database sits the clients you import, the dashboards your team shares, the pipelines that feed it, the projects that build on top of it, and now the agents that query it."
---

# The open ecosystem around ClickHouse

Around any good database sits the clients you import, the dashboards your team shares, the pipelines that feed it, the projects that build on top of it, and now the agents that query it. ClickHouse would not have [2,600+ contributors, 240k+ commits, and hundreds of millions of downloads](https://clickhouse.com/blog/what-a-difference-10-years-of-open-source-makes) without the ecosystem that has flourished around it.

## Building on open standards

ClickHouse is open source and built by a community of users. That shapes what the project reaches for when it connects to the rest of the world. ClickHouse gravitates to open standards that are themselves driven by their own communities, and over the years, it has adopted them across use cases: OpenTelemetry in observability, the Model Context Protocol in AI, Iceberg and Delta in the lakehouse. Much like ClickHouse is itself open, it integrates with an open ecosystem, where your data and your tooling stay yours, and you keep complete freedom over how you wire them together.

### Observability

OpenTelemetry is the open standard for instrumenting software, with one set of SDKs and one wire protocol for metrics, logs, and traces. You instrument once, and your telemetry can go anywhere, which means your instrumentation belongs to you.

With ClickHouse rapidly becoming the database of choice for observability, it needed first-class support for OTel. The ClickHouse exporter lives upstream in the OpenTelemetry Collector's contrib repository, and OpenTelemetry is the spine of [ClickStack](https://clickhouse.com/blog/clickstack-a-high-performance-oss-observability-stack-on-clickhouse), the open-source observability stack for ClickHouse.

ClickHouse is learning to speak Prometheus, too, with [PromQL support available experimentally](https://clickhouse.com/blog/open-house-2026-day-1#promql-support), so existing Prometheus queries and muscle memory carry over.

### AI

When agents arrived, they needed a standard way to reach tools and data, and the Model Context Protocol became it: an open protocol any model or framework can implement. The [ClickHouse MCP server](https://github.com/ClickHouse/mcp-clickhouse) is open source, and because MCP is an open protocol, it slots into whatever agent framework you already run. It's been shown [working with Agno, DSPy, LangChain, LlamaIndex, and PydanticAI](https://clickhouse.com/blog/integrating-clickhouse-mcp), and the list keeps growing. Any agent that speaks MCP can explore your tables, write queries, and read back results without anyone building a bespoke integration first.

### Open table formats & catalogs

Open table formats like Iceberg and Delta Lake let a dataset live in object storage, not tied to a single engine.

ClickHouse [reads Iceberg v2 in full](https://clickhouse.com/blog/climbing-the-iceberg-with-clickhouse), including schema evolution, time travel, with Iceberg writes landing in 25.8. Delta Lake support is [built on Delta Kernel](https://clickhouse.com/blog/clickhouse-is-data-lake-ready), and Apache Paimon arrived in [25.10](https://clickhouse.com/blog/clickhouse-2025-roundup).

A table format needs a catalog to track which files make up a table and hand that metadata to whatever engine asks. Here, too, ClickHouse leans on the open ones: it speaks the [Iceberg REST catalog](https://clickhouse.com/docs/use-cases/data-lake/rest-catalog) spec, [Apache Polaris](https://clickhouse.com/docs/use-cases/data-lake/polaris-catalog), and [Unity Catalog](https://clickhouse.com/docs/use-cases/data-lake/unity-catalog), each an open project with its own community. Because the catalog API is a standard rather than a product, you pick whichever one fits your stack, and swap later, without re-platforming your data.

## An open, unified data stack

Postgres is another great open-source database. It has a different job, but the same spirit. It sets the standard for transactional, OLTP workloads, and it does it in the open, guided by a community. ClickHouse does the same for analytics. Put them side by side, and you can't find a more obvious [pair](https://clickhouse.com/blog/postgres-managed-by-clickhouse-beta). GitLab [wrote about this setup](https://about.gitlab.com/blog/two-sizes-fit-most-postgresql-and-clickhouse/) a couple of years ago, and it has become common enough that the combination is turning into a standard in its own right.

There are now several open-source tools that bring the two databases closer together:

* [PeerDB](https://clickhouse.com/blog/postgres-cdc-year-in-review-2025) is the open-source Postgres CDC project that became the engine for moving transactional data into analytical tables.  
* [pg\_clickhouse](https://clickhouse.com/blog/introducing-pg_clickhouse) is an open-source Postgres extension that makes ClickHouse tables queryable from standard Postgres, with filters, projections, and aggregations pushed down transparently. If a tool speaks Postgres, it now speaks ClickHouse.  
* [pg\_stat\_ch](https://github.com/ClickHouse/pg_stat_ch) is an open-source Postgres extension that turns every query execution into a compact event and streams it into ClickHouse, where you can slice query latency, errors, and behavior over months of history like an APM.

## Built on ClickHouse

Some of the most interesting things in the ecosystem aren't just integrations. They're whole projects that chose ClickHouse as their engine and grew from there. A few have since become first-party, open-source projects alongside ClickHouse. Together, they mean ClickHouse can be more than a database: a full observability stack, or an LLM engineering platform, all without leaving open source.

[ClickStack](https://clickhouse.com/blog/clickstack-a-high-performance-oss-observability-stack-on-clickhouse) is a full open-source observability stack, ClickHouse for storage, the OpenTelemetry Collector for ingestion, and the HyperDX UI on top, launched in May 2025\. A [year in](https://clickhouse.com/blog/clickstack-a-year-in-review-2025), it's become one of the most active corners of the community.

[chDB](https://github.com/chdb-io/chdb) started as a community project, embedding ClickHouse in-process for Python, before [joining the family in 2024](https://clickhouse.com/blog/chdb-joins-clickhouse-family). It's still Apache 2.0 and, as of June 2026, sits at around 24 million PyPI downloads, running about 2.3 million a month. [chDB v4](https://clickhouse.com/blog/chdb.4-0-pandas-hex), released in March 2026, added the DataStore API, which lets you write pandas-compatible code that lazily compiles to optimized SQL on the ClickHouse engine, falling back to real pandas automatically for operations ClickHouse can't do. [Hex announced a partnership](https://hex.tech/blog/announcing-clickhouse-partnership/) that preinstalls chDB on every Hex notebook, with a one-click ClickHouse connection.

[Langfuse](https://clickhouse.com/blog/open-house-2026-day-1) is the open-source LLM observability and engineering platform, tracing, evals, and prompt management for teams building on top of models. Its team joined ClickHouse in January 2026, with Langfuse remaining open source, OpenTelemetry-native, and self-hostable.

[LibreChat](https://clickhouse.com/blog/open-house-2026-day-2) is the open-source agent and chat platform. It joined ClickHouse in October 2025 and continues as an active OSS project, shipping new releases every few weeks.

## Build with ClickHouse

Every official client is open source, and between them they cover the languages you're most likely to be writing:

- [Go](https://github.com/ClickHouse/clickhouse-go)  
- [Java](https://github.com/ClickHouse/clickhouse-java)  
- [JavaScript and Node.js](https://github.com/ClickHouse/clickhouse-js)  
- [Python](https://github.com/ClickHouse/clickhouse-connect)  
- [C++](https://github.com/ClickHouse/clickhouse-cpp)  
- [.NET](https://github.com/ClickHouse/clickhouse-cs)  
- [Rust](https://github.com/ClickHouse/clickhouse-rs)

The official Rust client, [clickhouse-rs](https://github.com/ClickHouse/clickhouse-rs), didn't start official at all. Paul Loyd built and maintained it as a community project for years before it became the official client. Someone built the thing because they needed it, the community gathered around it, and eventually it became part of the family.

The clients have had a busy year, and a lot of it shipped at [Open House](https://clickhouse.com/blog/open-house-2026-day-2). The Python client, clickhouse-connect, hit v1.0 GA with native async and full sync parity, 4x faster cold starts, and first-class numpy, pandas, pyarrow, and polars support, plus a SQLAlchemy dialect with Alembic migrations. The .NET client reached v1.2.0 with Entity Framework Core, a Serilog sink, and Aspire and Semantic Kernel packages on NuGet. There's a Laravel driver with Eloquent models and artisan migrations for the PHP side of the house.

And it's not just the clients. For teams running ClickHouse on Kubernetes, there's now an [official Apache 2.0 open-source Kubernetes operator](https://clickhouse.com/blog/clickhouse-kubernetes-operator), shipped in January 2026\. It automates the fiddly parts of running production clusters, sharding, replication, scaling, and safe rolling version upgrades, all driven through Kubernetes custom resources.

## Partners and integrations

[Apache Airflow](https://clickhouse.com/blog/open-house-2026-day-2#apache-airflow-native-provider) is the open-source standard for orchestrating data pipelines, the scheduler running the jobs that feed analytical tables, so a first-class ClickHouse provider reaches a lot of teams. ClickHouse is now getting an official hook and operator in [upstream Airflow](https://github.com/apache/airflow/pull/67080); going upstream, rather than living in a side plugin, means anyone who installs Airflow gets ClickHouse support in the box. But that official provider didn't appear out of nowhere. For years, community members Ivan Klimenko and Anton Bryzgalov built and maintained their own ClickHouse providers for Airflow racking up hundreds of thousands of downloads and keeping teams unblocked long before anything official existed.

[dbt](https://www.getdbt.com/) is the open-source tool analytics engineers use to transform data in the warehouse by writing plain SQL select statements, and the ClickHouse adapter itself [started as a gift from the community](https://clickhouse.com/blog/clickhouse-dbt-project-introduction-and-webinar). ClickHouse is now the first partner co-developing a [dbt Fusion engine adapter](https://clickhouse.com/blog/open-house-2026-day-2#dbt-clickhouse-fusion-adapter), now in alpha.

> "ClickHouse has become one of the fastest-growing databases in the dbt community" - Hope Watson, dbt Labs.

[Grafana](https://grafana.com/) is the open-source dashboarding tool that a huge share of engineering teams already keep open on a second monitor, which makes its plugin one of the most common ways people see ClickHouse data. It's also one of the longest-running integrations anywhere, and the teams have published [a shared vision for where it goes next](https://clickhouse.com/blog/grafana-plugin-vision).

[Fivetran's ClickHouse Cloud destination went GA](https://clickhouse.com/blog/open-house-2026-day-2#fivetran-generally-available), opening up more than 500 sources. [Sigma Computing's connector entered public beta](https://clickhouse.com/blog/open-house-2026-day-2#sigma-computing-connector-in-public-beta), Notion built a native ClickHouse MCP connector, and Google Cloud shipped a GA Dataflow template for Pub/Sub. Artie, Dreambase, Tavily, and Hightouch all shipped integrations of their own.

## Here's to the next 10 years

This open ecosystem has been building and flourishing for 10 years. 

ClickHouse is now becoming a default for AI-native companies, foundation labs, and the agents they build. You can see it threaded through this post: the MCP servers, agents querying ClickStack, chDB handing agents a pandas interface, and the [ClickHouse Agent Skills](https://clickhouse.com/blog/introducing-clickhouse-agent-skills). Given how fast that space is moving, this is surely only scratching the surface of what integrating with it will look like.

That's the thing about an open ecosystem: nobody gets to script it. The ClickHouse story has always been written by the people using it. 200+ integrations and hundreds of millions of downloads, built by maintainers, by partners, and by a community that just keeps shipping. If you've built something that talks to ClickHouse, you're part of this story.

We don't know what the next ten years of the ClickHouse ecosystem will look like. We can't wait to find out.  
