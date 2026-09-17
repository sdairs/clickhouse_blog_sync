---
title: "ClickHouse is now available on the dbt platform"
date: "2026-09-16T19:38:40.629Z"
author: "Aditya Chidurala, José Muñoz and Alex Francoeur"
category: "Product"
excerpt: "The ClickHouse adapter for dbt v2 is in public beta, powered by dbt’s Rust engine. ClickHouse also joins the dbt platform in private beta, supporting open-source ClickHouse and ClickHouse Cloud."
---

# ClickHouse is now available on the dbt platform

## Summary

* The latest ClickHouse adapter for dbt is built on dbt v2, the Rust rewrite of dbt. It is in public beta as of September 16, 2026, and ships with the open source dbt binary.
* ClickHouse, with support for both open-source ClickHouse and ClickHouse Cloud, is available on dbt platform for the first time, in private beta.


We're at [dbt Summit](https://www.getdbt.com/dbt-summit/) in Las Vegas this week (September 15 to 18, 2026) and are excited to share two announcements with our shared communities.

First, the ClickHouse adapter for dbt v2 is now available in public beta, and you can see the performance gains immediately from this Rust-based engine. Second, ClickHouse is now available as a natively supported data warehouse on dbt Platform. It is currently in private beta and is the first partner-built v2 adapter available on the platform. 

We are excited to see these two popular open-source projects come together. ClickHouse has been licensed under Apache 2.0 since 2016. The latest iteration of the dbt engine is also under Apache 2.0, with dbt Fusion built on top of it. The secret sauce behind our ClickHouse dbt v2 adapter is the [ADBC driver](https://clickhouse.com/blog/introducing-the-clickhouse-adbc-driver), allowing dbt to connect to ClickHouse using the Apache Arrow standard. Open source is in the DNA of both companies and ensures that our community can participate in the development, contributing both their ideas and code.

> *"The companies that win with AI will be the ones whose agents can be trusted with the numbers. That takes an analytics engine fast enough for agents to query at scale, which is what ClickHouse does, and a data foundation that makes every model tested, governed, and traceable, which is what dbt does. Bringing the two together on dbt v2 and in the dbt platform gives data teams both."*
>
> Shawn Toldo, VP, Worldwide Partner Ecosystem, dbt Labs

**The various ways you can use dbt with ClickHouse**

|  | dbt v1 adapter | dbt v2 adapter | ClickHouse in the dbt platform |
| :---- | :---- | :---- | :---- |
| Status | GA and maintained, since 2021  | Public beta, available September 16, 2026 | Private beta, available September 16, 2026 |
| What it is | The Python adapter, dbt-clickhouse, with thousands of teams running in production | The same adapter rebuilt for dbt's Rust engine, connecting with ADBC, shipped inside the dbt binary | ClickHouse as a connection in the dbt platform: Studio, environments, scheduled jobs, Catalog |
| Get it | pip install dbt-core dbt-clickhouse | python -m pip install --pre dbt | Request access via the [private beta form](https://docs.google.com/forms/d/1iffnA8pf_ETZnhcqjtda5v-RLIQCrNFKXaIL_7M5dOk/); dbt enables the connection per account |
| Docs | [Integrating dbt and ClickHouse](https://clickhouse.com/docs/integrations/dbt) | [dbt v2, dbt Fusion and the dbt platform](https://clickhouse.com/docs/integrations/connectors/data-ingestion/etl-tools/dbt/dbt-core-v2-fusion-and-platform)  | [dbt v2, dbt Fusion and the dbt platform](https://clickhouse.com/docs/integrations/connectors/data-ingestion/etl-tools/dbt/dbt-core-v2-fusion-and-platform) and [dbt docs](https://github.com/dbt-labs/docs.getdbt.com/pull/9975) |

## Five years of dbt + ClickHouse {#five_years_of_dbt__clickhouse}

In January 2021, [Dmitriy Sokolov](https://github.com/silentsokolov) built dbt-clickhouse to run his own dbt project on ClickHouse and published it under the Apache 2.0 license. Adoption grew, and in 2022 the project [moved to the ClickHouse GitHub organization](https://clickhouse.com/blog/clickhouse-dbt-project-introduction-and-webinar), where we maintain it as a ClickHouse-supported adapter and test it against ClickHouse Cloud on every release.   
dbt-clickhouse has stayed a community adapter as well as a vendor-supported one. More than 90 people have made contributions, and some of the adapter's most used features came from outside ClickHouse. As of the [latest release](https://github.com/ClickHouse/dbt-clickhouse/releases), dbt-clickhouse supports dbt 1.12 and includes features like table, view, incremental, and microbatch materializations, seeds, snapshots, contracts, and data and unit tests. Beyond dbt features, the adapter also supports ClickHouse-specific materializations for [materialized views](https://clickhouse.com/docs/integrations/connectors/data-ingestion/etl-tools/dbt/materialization-materialized-view), [dictionaries, and distributed tables](https://clickhouse.com/docs/integrations/connectors/data-ingestion/etl-tools/dbt/materializations), and [table settings](https://clickhouse.com/docs/integrations/connectors/data-ingestion/etl-tools/dbt/features-and-configurations) such as sorting keys, codecs, TTLs, skipping indexes, and projections as model config.   
Over 2,000 teams run dbt-clickhouse in production, from data teams using it for internal BI to product teams whose dbt models feed customer-facing analytics. 

![](https://clickhouse.com/uploads/dbt_platform_sep2026_image2_7ccd23d1d2.png)  
*Open source adoption of ClickHouse in the dbt ecosystem is accelerating* 

We plan to support the dbt 1.x adapter and 2.x in parallel, ensuring both are always up to date with the latest functionality.

## Why teams run dbt on ClickHouse {#why_teams_run_dbt_on_clickhouse}

dbt was born in the era of batch warehouses. Cloud data warehouses were designed for scheduled reporting, where a model that runs overnight for 10 minutes is fine. Since then, data needs have increasingly become more real-time. ClickHouse is built for workloads that require sub-second queries on data that landed seconds ago, many concurrent users and agents reading the same tables, and analytics served in real-time directly to consumers rather than a weekly dashboard. Bringing dbt to ClickHouse puts the same models, tests, and lineage in front of those operational, analytical workloads.

**Fresh data without a refresh cycle.** ClickHouse [materialized views](https://clickhouse.com/docs/concepts/features/materialized-views/incremental-materialized-view) are computed on the insert path, so a pre-aggregation is current the moment the raw rows land. The adapter's materialized_view materialization lets you define them as dbt models, with tests attached, on both the v1 and v2 adapters. Pair that with [ClickPipes](https://clickhouse.com/cloud/clickpipes) for Kafka and Postgres CDC and your dbt project runs over data that is seconds old.

**Concurrency for people and agents.** The same tables that serve a customer-facing dashboard can serve an AI agent issuing a steady stream of queries through the [ClickHouse MCP Server](https://clickhouse.com/docs/products/cloud/features/ai-ml/mcp/remote-mcp). dbt gives those agents curated, documented tables to query rather than raw events, and dbt's tests and contracts catch schema drift before it reaches them.

**Cost at that speed.** In [CostBench](https://clickhouse.com/blog/clickhouse-vs-snowflake-real-time-performance-per-dollar), published September 10, 2026, ClickHouse Cloud delivered 412x better end-to-end real-time performance per dollar than Snowflake while both ingested 113.2 billion rows and served the same continuous query workload, with 42 ms P99 latency on aggregate queries against 22.20 seconds. The [benchmark hub](https://clickhouse.com/benchmarks) has the full methodology.

**One engine, your choice of deployment.** The ClickHouse dbt v2 adapter targets the same engine whether you run open-source ClickHouse on your own hardware, ClickHouse Cloud, or [BYOC](https://clickhouse.com/cloud/bring-your-own-cloud) inside your own account. A model that runs in one place runs in the others.

## The dbt v2 adapter: public beta {#the_dbt_v2_adapter_public_beta}

dbt v2 is a ground-up rewrite of dbt in Rust, and adapters changed with it. A v1 adapter is a standalone Python package you install next to dbt-core. A v2 adapter lives inside dbt's codebase and talks to the database over ADBC. The ClickHouse adapter ships inside the dbt binary and there is no separate package to install. dbt Labs rebuilt the adapters it owns for v2.

### Why v2 is better

**Speed.** dbt Labs reports parse times up to 30x faster than dbt v1, so a project that took a minute to compile now compiles in seconds, and the feedback loop in your editor gets short enough to stay in flow.  
**One binary, native connectivity.** The adapter is built into dbt, and the connection runs over the [ClickHouse ADBC driver](https://clickhouse.com/blog/introducing-the-clickhouse-adbc-driver). dbt downloads the driver on first use.  
**The same project.** Models, tests, and profiles carry over; only the binary is different. Some features are still missing, and we’re nearly at feature parity with dbt-clickhouse.  Review the [v1 vs v2 parity table](https://clickhouse.com/docs/integrations/dbt/dbt-core-v2-fusion-and-platform#parity) before testing an existing project.  
**A path into the dbt platform.** The future of the dbt platform is built on v2 adapters. With the v2 adapter for ClickHouse available on dbt platform, we can build a foundation for both old and new dbt platform features. 

### Run your project on v2

Install dbt v2 with pip and check the version. The [dbt v2 upgrade guide](https://docs.getdbt.com/docs/dbt-versions/dbt-upgrade/upgrading-to-v2) covers the other install options.

<pre><code type='click-ui' language='bash'>
python -m pip install --pre dbt
dbt --version
</code></pre>

Review your existing profiles.yml against the v2 adapter’s supported connection settings before running your project. A minimal ClickHouse Cloud profile sets the type, host, credentials, and target database.

```yaml
clickhouse_cloud:
  target: prod
  outputs:
    prod:
      type: clickhouse
      host: <your-service>.clickhouse.cloud
      port: 8443
      user: default
      password: <password>
      schema: analytics
      secure: true
```

Then run your project as you did before.

<pre><code type='click-ui' language='bash'>
dbt debug
dbt build
</code></pre>

The first run pulls the ClickHouse ADBC driver automatically. If you want a sandbox instead of your own project, [jaffle-shop-clickhouse](https://github.com/ClickHouse/jaffle-shop-clickhouse) is our fork of dbt's example project and runs on the v1 adapter, the v2 adapter, and the dbt platform.   
![](https://clickhouse.com/uploads/dbt_platform_sep2026_image4_e7f7c4a6b9.png)  
*A ClickHouse dbt project running on dbt v2 in the VS Code extension.*  

Against the dbt v1 integration suite, the v2 adapter passes more than 81% of the full suite and 92% of the tests that apply to ClickHouse Cloud. These gaps will be filled shortly and you can view comparison table between the two adapters [here](https://clickhouse.com/docs/integrations/dbt/dbt-core-v2-fusion-and-platform#parity). If something on your project behaves differently, be sure to open up an issue in [our repository](https://github.com/ClickHouse/dbt-clickhouse).  The dbt v2 adapter is not ready for production workloads. Use the beta in development or staging on ClickHouse Cloud or a single-node self-managed instance.

## ClickHouse on the dbt platform: private beta {#clickhouse_on_the_dbt_platform_private_beta}

Today, we’re excited to announce that ClickHouse’s new v2 adapter is the first partner-built v2 adapter available on the dbt platform.  
Until now, using dbt with ClickHouse meant running dbt yourself. dbt on a laptop, in a CI runner, or from an orchestrator. With ClickHouse now available on the dbt platform, that’s no longer the case. In private beta, you can create a ClickHouse connection and develop models in Studio, the browser IDE, test them across development and staging environments, run them on scheduled jobs with logs and retries, and browse them in Catalog. The ClickHouse connection uses the dbt v2 adapter and has the same beta limitations as the local adapter.


![](https://clickhouse.com/uploads/dbt_platform_sep2026_image3_7254afc22d.png)  
*Connecting ClickHouse Cloud from the dbt platform.*  

To request early access, fill in the [private beta form](https://docs.google.com/forms/d/1iffnA8pf_ETZnhcqjtda5v-RLIQCrNFKXaIL_7M5dOk/)**.** By entering our private beta, you’ll be able to provide feedback at a critical stage in its development and help us design the best adapter possible for GA. The beta is hands-on. dbt enables the ClickHouse connection per account, you get a direct channel to both engineering teams, and what we hear during this phase influences the order in which the remaining pieces ship. What missing features matter most to you and what’s most critical to your workload? We’d love to learn more. Join the private beta today and help us build for your use case. 

![](https://clickhouse.com/uploads/dbt_platform_sep2026_image1_48f985b577.png)  
*A scheduled dbt job running against ClickHouse Cloud.*

## What comes next: the path to GA {#what_comes_next_the_path_to_ga}

We have a lot to do before we’re ready to GA the adapter, and it all starts with you. Your input and feedback will influence both the quality and direction we take it.

At a minimum, we know we want to have parity with the ClickHouse v1 adapter, dbt-clickhouse. This includes ON CLUSTER DDL and the distributed materializations, so Open Source clusters get the same coverage ClickHouse Cloud has today.

Beyond that, we plan to support Fusion capabilities such as dialect-aware validation, static analysis, the language server, column awareness in the VS Code extension, and engine-side column-level lineage. You can track our progress in [issue #736](https://github.com/ClickHouse/dbt-clickhouse/issues/736).

dbt Platform has many features such as the Semantic Layer and MetricFlow that our community and customers are interested in us supporting.

Try the ClickHouse dbt v2 adapter public beta, or request access to the ClickHouse private beta on the dbt platform. Share what works, report issues, and tell us which features you need next.

* Get started with dbt v2 adapter today: check out the [installation guide and ClickHouse connection guide](https://clickhouse.com/docs/integrations/connectors/data-ingestion/etl-tools/dbt)  
* Sign up for the private beta today with [this form](https://docs.google.com/forms/d/1iffnA8pf_ETZnhcqjtda5v-RLIQCrNFKXaIL_7M5dOk/)  
* Join our [slack community](https://clickhouse.com/slack), the [clickhouse channel on dbt slack](https://getdbt.slack.com/archives/C03KVDLMNV6) and [discuss what features](https://github.com/dbt-labs/dbt/discussions) you’d like to see next


---

## Get started today

Interested in seeing how ClickHouse works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-2054-get-started-today-sign-up&utm_blogctaid=2054)

---