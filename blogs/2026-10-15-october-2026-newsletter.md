---
title: "October 2026 newsletter"
date: "2026-10-15T10:07:35.737Z"
author: "Mark Needham"
category: "Community"
excerpt: "Welcome to the October 2026 ClickHouse newsletter, featuring CostBench results against BigQuery and Databricks, ClickHouse 26.9, executable UDFs on ClickHouse Cloud, and the latest community news and events."
---

# October 2026 newsletter

Hello and welcome to another ClickHouse newsletter!

This month brings two more installments in the CostBench series, with Tom Schreiber and Lionel Palacin putting BigQuery and Databricks through their paces on a real-time analytics workload.

The 26.9 release adds new boundary conditions to the LIMIT clause that make log analysis easier, and a CREATE TOKEN statement for time-limited credentials.

Elsewhere, executable user-defined functions are now generally available on ClickHouse Cloud, and we have Postgres deep dives on memory safety and running on local NVMe storage.

## Featured community member: Hoang Minh V {#featured-community-member}

This month's featured community member is Hoang Minh V, Senior Software Developer at shyftplan.

![](https://clickhouse.com/uploads/oct2026_nl_image1_126e4b6e6d.png)

Hoang is a TU Munich alumnus and has had more than 100 pull requests merged into ClickHouse since May, 48 of which are in the 26.9 release.

Much of his 26.9 work went into <a href="https://clickhouse.com/blog/introducing-promql?utm_source=clickhouse&utm_medium=email&utm_campaign=202610-newsletter&ref=newsletter" target="_blank">PromQL and the `TimeSeries` engine</a>. He added a fast path for PromQL aggregations with an empty `by()` modifier, such as `sum by() (m)`, which skips a tag transformation over every input series. He also sped up `TimeSeries` reads and the `timeSeries*ToGrid` aggregate functions, stopped PromQL counting consecutive `NaN` samples as changes, and added support for quoted label names in grouping modifiers.

Outside PromQL, he made `LIMIT BY` stop reading input once a constant grouping key reaches its limit, and fixed more than a dozen edge cases in array, string, and URL functions.

➡️ <a href="https://www.linkedin.com/in/hmv-io/" target="_blank">Connect with Hoang on LinkedIn</a>

## 26.9 release {#release}

![](https://clickhouse.com/uploads/oct2026_nl_image2_22fff01e9d.png)

The ClickHouse 26.9 release extends the `LIMIT` clause with `AFTER` and `UNTIL` boundary conditions, which start and stop output based on values in the ordered result.

This functionality makes log analysis much easier, as we can now retrieve every server error, along with the requests that followed it, in a single query.

This release also adds incremental refresh for append-only materialized views, `CREATE TOKEN` for time-limited credentials, `DISTINCT` that can spill to disk, and much more!

➡️ <a href="https://clickhouse.com/blog/clickhouse-release-26-09?utm_source=clickhouse&utm_medium=email&utm_campaign=202610-newsletter&ref=newsletter" target="_blank">Read the release post</a>

## Why I use ClickHouse for my web analytics tool {#web_analytics_lienks}

![](https://clickhouse.com/uploads/oct2026_nl_image3_5408048ab7.png)

Philip explains why he chose ClickHouse for Lienks, his privacy-friendly web analytics tool. PostgreSQL stores application data, such as users, workspaces, and billing, while pageviews and custom events are stored in ClickHouse.

Philip points out that PostgreSQL would handle Lienks' current size, but chose ClickHouse up front because he hopes to scale to billions of events and wouldn’t want to migrate if that happens.

➡️ <a href="https://dev.to/philipkpz/why-i-use-clickhouse-for-my-web-analytics-tool-1ig0" target="_blank">Read the blog post</a>

## Why Databricks can't match ClickHouse Cloud for real-time analytics {#costbench_databricks}

![](https://clickhouse.com/uploads/oct2026_nl_image4_fc87049c80.jpg)

Last month, Tom Schreiber and Lionel Palacin introduced <a href="https://clickhouse.com/blog/costbench-real-time-performance-per-dollar?utm_source=clickhouse&utm_medium=email&utm_campaign=202610-newsletter&ref=newsletter" target="_blank">CostBench</a>, a benchmark that measures the end-to-end performance and cost of real-time analytics across cloud data warehouses. They went on to show that <a href="https://clickhouse.com/blog/clickhouse-vs-snowflake-real-time-performance-per-dollar?utm_source=clickhouse&utm_medium=email&utm_campaign=202610-newsletter&ref=newsletter" target="_blank">Snowflake can’t match ClickHouse Cloud for real-time analytics</a>.

This month, they put Databricks through its paces, ingesting 113.2 billion stock-market quotes while queries run. ClickHouse Cloud delivered 752× better end-to-end performance per dollar.

ClickHouse uses incremental materialized views to keep its pre-aggregations current at insert time, whereas Databricks splits that work across ingestion, asynchronous clustering, and materialized view refreshes. As a result, Databricks' preparation cost came to \$695.60, compared to \$28.69 for ClickHouse.

➡️ <a href="https://clickhouse.com/blog/clickhouse-vs-databricks-real-time-performance-per-dollar?utm_source=clickhouse&utm_medium=email&utm_campaign=202610-newsletter&ref=newsletter" target="_blank">Read the blog post</a>

## Why BigQuery can't match ClickHouse Cloud for real-time analytics {#costbench_bigquery}

![](https://clickhouse.com/uploads/oct2026_nl_image5_cfbec2e833.jpg)

Tom and Lionel also ran CostBench against BigQuery, ingesting 113.2 billion quotes while queries ran.

ClickHouse Cloud performs 438× better per dollar under BigQuery's Capacity pricing and 512× better under On-demand pricing.

ClickHouse sorts and pre-aggregates data on insert, while BigQuery leaves catch-up work for query time. The total query runtime was 58.29 seconds for ClickHouse and 49.36 minutes for BigQuery.

➡️ <a href="https://clickhouse.com/blog/clickhouse-vs-bigquery-real-time-performance-per-dollar?utm_source=clickhouse&utm_medium=email&utm_campaign=202610-newsletter&ref=newsletter" target="_blank">Read the blog post</a>


---

## Run the numbers yourself

CostBench found ClickHouse Cloud 752× better per dollar than Databricks for real-time analytics. Try it on your own data with $300 in free credits.

[Start free](https://console.clickhouse.cloud/signUp?loc=202610-newsletter&utm_source=clickhouse&utm_medium=email&utm_campaign=202610-newsletter&ref=newsletter&utm_blogctaid=2646)

---

## Executable UDFs are now generally available on ClickHouse Cloud {#executable_udfs_ga}

![](https://clickhouse.com/uploads/oct2026_nl_image6_9d8e41db12.png)

Executable UDFs, which let you upload your own functions and call them from SQL, are now generally available on ClickHouse Cloud on AWS, GCP, and Azure.

Since the beta, they've added a native runtime for precompiled Rust, Go, C++, and JavaScript binaries, outbound network access, and a `deterministic` flag that lets the query cache serve queries that call a UDF.

The blog post shows a Rust UDF that counts LLM tokens at insert time and a Python UDF that calls Claude to grade a sample of completions.

➡️ <a href="https://clickhouse.com/blog/executable-udfs-generally-available-on-clickhouse-cloud?utm_source=clickhouse&utm_medium=email&utm_campaign=202610-newsletter&ref=newsletter" target="_blank">Read the blog post</a>

## Postgres Round-up {#postgres_round_up}

![](https://clickhouse.com/uploads/oct2026_nl_image7_5ea62fbef0.jpg)

The Postgres Round-up is back for a second month. This time we've got recaps from Postgres Summit US, PGDay Lowlands, and Percona Live Amsterdam, as well as deep dives into memory safety and running Postgres on local NVMe storage.

* David Wheeler <a href="https://clickhouse.com/blog/postgres-summit-us-2026?utm_source=clickhouse&utm_medium=email&utm_campaign=202610-newsletter&ref=newsletter" target="_blank">looks back on Postgres Summit US 2026</a> in New York, where he demoed four tools that connect Postgres and ClickHouse, including `pg_clickhouse` and `pg_stat_ch`.
* Gülçin Yıldırım Jelínek <a href="https://clickhouse.com/blog/postgres-week-in-the-netherlands-pgday-lowlands-percona-live-2026?utm_source=clickhouse&utm_medium=email&utm_campaign=202610-newsletter&ref=newsletter" target="_blank">shares notes from PGDay Lowlands and Percona Live Amsterdam</a>, where she spoke about `pg_clickhouse`, `pg_stat_ch` and PostgreSQL 19 monitoring.
* Philip Dubé <a href="https://clickhouse.com/blog/memory-safety-postgres-extensions-c-cpp?utm_source=clickhouse&utm_medium=email&utm_campaign=202610-newsletter&ref=newsletter" target="_blank">explains how ClickHouse's Postgres extensions safely combine C and C++</a>, with each taking a different approach, from removing C++ entirely to running it in a separate helper process.
* David Wheeler <a href="https://clickhouse.com/blog/pg_clickhouse-chdb?utm_source=clickhouse&utm_medium=email&utm_campaign=202610-newsletter&ref=newsletter" target="_blank">walks through the latest `pg_clickhouse` and chdb extension releases</a>, which add character-encoding checks and improve support for nested data, JSON, and type mappings.
* Kevin Biju Kizhake Kanichery <a href="https://clickhouse.com/blog/can-your-postgres-survive-a-bad-query?utm_source=clickhouse&utm_medium=email&utm_campaign=202610-newsletter&ref=newsletter" target="_blank">tests how Postgres providers handle a query that exhausts memory</a>, and explains why ClickHouse Managed Postgres fails a query rather than letting the whole database go down.
* Kaushik Iska <a href="https://clickhouse.com/blog/postgres-on-nvme?utm_source=clickhouse&utm_medium=email&utm_campaign=202610-newsletter&ref=newsletter" target="_blank">argues that slow Postgres is often slow storage</a>, showing how local NVMe helps once the working set outgrows memory, and where analytics still needs ClickHouse.

## The official ClickHouse provider for Apache Airflow is now available {#airflow_provider}

![](https://clickhouse.com/uploads/oct2026_nl_image8_20a1fc97e4.jpg)

Aditya Chidurala, Bentsi Leviav, and Alex Francoeur introduce `apache-airflow-providers-clickhousedb`, the official ClickHouse provider for Apache Airflow.

Built on ClickHouse Connect, it lets you run DDL, DML, and analytical queries with Airflow's standard `SQLExecuteQueryOperator`. When you need more control, the provider's `ClickHouseHook` gives you direct access to the ClickHouse client, including a `bulk_insert_rows` method for fast columnar inserts. ClickHouse's internal data warehouse uses the provider to move about 6 billion rows a day.

➡️ <a href="https://clickhouse.com/blog/clickhouse-airflow-provider?utm_source=clickhouse&utm_medium=email&utm_campaign=202610-newsletter&ref=newsletter" target="_blank">Read the blog post</a>

## chDB Durable Layer for agent memory {#chdb_durable_layer}

![](https://clickhouse.com/uploads/oct2026_nl_image9_89084720cd.jpg)

Changshuo Chen introduces the chDB Durable Layer, which allows agent memory to survive the machine on which it was created.

You keep querying a fast local copy as usual, while the source of truth lives in an object storage bucket you own, whether that's S3, GCS, or Azure Blob. That means a new laptop, CI job, or throwaway sandbox can pick up where the last one left off.

➡️ <a href="https://clickhouse.com/blog/chdb-durable-layer-for-agent-memory?utm_source=clickhouse&utm_medium=email&utm_campaign=202610-newsletter&ref=newsletter" target="_blank">Read the blog post</a>

## Open House videos {#open_house_videos}

The Open House Roadshow has now wrapped up, and the talks are on our website. Here are a few highlights from New York and Sydney.

* Matt Scanlin, Senior Data Engineer at Polymarket, <a href="https://clickhouse.com/videos/openhouse-nyc-polymarket?utm_source=clickhouse&utm_medium=email&utm_campaign=202610-newsletter&ref=newsletter" target="_blank">explains how replacing MongoDB with ClickHouse Cloud</a> took their liquidity incentive calculations from days to minutes.
* Sho, a data engineer at OpenRouter, <a href="https://clickhouse.com/videos/openhouse-nyc-openrouter?utm_source=clickhouse&utm_medium=email&utm_campaign=202610-newsletter&ref=newsletter" target="_blank">shows how ClickHouse powers everything from user dashboards and public model rankings to internal Slack agents</a>, with OpenRouter now serving over 110 trillion tokens a week.
* Paul, a principal engineer at Buildkite, <a href="https://clickhouse.com/videos/open-house-sydney-buildkite-real-time-analytics?utm_source=clickhouse&utm_medium=email&utm_campaign=202610-newsletter&ref=newsletter" target="_blank">explains how Test Engine uses ClickHouse Cloud for flaky test detection and test splitting</a>, following the ingestion of 100 billion test executions in July alone.
* Sergey Iakovlev and Sahil Bahl <a href="https://clickhouse.com/videos/open-house-sydney-canva-langfuse?utm_source=clickhouse&utm_medium=email&utm_campaign=202610-newsletter&ref=newsletter" target="_blank">share how Canva's AI support agents resolve tickets in about two minutes</a>, using Langfuse, built on ClickHouse, for tracing, prompt management, and evaluations.
* Trevor Preston, Senior Principal Engineer at Xero, <a href="https://clickhouse.com/videos/open-house-sydney-xero-observability?utm_source=clickhouse&utm_medium=email&utm_campaign=202610-newsletter&ref=newsletter" target="_blank">explains how Xero made its network observable</a> by loading VPC flow logs and CDN logs into ClickStack, where the flow logs compress 22×.

➡️ <a href="https://clickhouse.com/videos?utm_source=clickhouse&utm_medium=email&utm_campaign=202610-newsletter&ref=newsletter&category=open-house" target="_blank">Watch all the Open House videos</a>

## Upcoming events {#upcoming-events}

### Global virtual events

* Webinar <a href="https://clickhouse.com/pt-BR/company/events/Intro-CH-PT?utm_source=clickhouse&utm_medium=email&utm_campaign=202610-newsletter&ref=newsletter" target="_blank">Introdução a ClickHouse: analytics, observabilidade e IA em um só lugar</a> - Oct 20, 2026
* Webinar <a href="https://clickhouse.com/es/company/events/AI-Agents-Langfuse-ES?utm_source=clickhouse&utm_medium=email&utm_campaign=202610-newsletter&ref=newsletter" target="_blank">El loop de los agentes de IA: de trazas a evaluaciones con Langfuse</a> - Oct 21, 2026

### Virtual training

* <a href="https://clickhouse.com/company/events/202610-APJ-Real-time-Analytics-ClickHouse-Level3?utm_source=clickhouse&utm_medium=email&utm_campaign=202610-newsletter&ref=newsletter" target="_blank">Real-time Analytics with ClickHouse: Level 3</a> - Oct 16, 2026
* <a href="https://clickhouse.com/company/events/202611-AMER-ClickHouse-Fundamentals?utm_source=clickhouse&utm_medium=email&utm_campaign=202610-newsletter&ref=newsletter" target="_blank">ClickHouse Fundamentals</a> - Nov 4, 2026
* <a href="https://clickhouse.com/company/events/202611-AMER-EMEA-Observability-with-ClickStack?utm_source=clickhouse&utm_medium=email&utm_campaign=202610-newsletter&ref=newsletter" target="_blank">Observability with ClickStack Fundamentals</a> - Nov 11, 2026

### Events in AMER

* <a href="https://devopsdays.org/events/2026-bogota/welcome/" target="_blank">DevOpsDays Bogotá</a> - Bogotá, Colombia, Oct, 23, 2026
* <a href="https://clickhouse.com/company/events/202611nycmodal?utm_source=clickhouse&utm_medium=email&utm_campaign=202610-newsletter&ref=newsletter" target="_blank">AI Builders Night New York @ Modal</a> - New York - Nov 3, 2026
* <a href="https://clickhouse.com/company/events/202611librechatnyc?utm_source=clickhouse&utm_medium=email&utm_campaign=202610-newsletter&ref=newsletter" target="_blank">LibreChat Meetup New York</a> - Brooklyn - Nov 5, 2026
* <a href="https://clickhouse.com/company/events/202611slckubecon?utm_source=clickhouse&utm_medium=email&utm_campaign=202610-newsletter&ref=newsletter" target="_blank">Observability with ClickStack Fundamentals Kubecon Training</a> - Salt Lake City - Nov 9, 2026
* <a href="https://clickhouse.com/company/events/20261109SF?utm_source=clickhouse&utm_medium=email&utm_campaign=202610-newsletter&ref=newsletter" target="_blank">AI Builders Night</a> - San Francisco - Nov 9, 2026
* <a href="https://events.linuxfoundation.org/kubecon-cloudnativecon-north-america/" target="_blank">KubeCon + CloudNativeCon North America</a> - Salt Lake City - Nov 10, 2026
* <a href="https://sc26.supercomputing.org/" target="_blank">SuperComputing 2026</a> - Nov 15, 2026
* <a href="https://clickhouse.com/company/events/202611sfdemeetup?utm_source=clickhouse&utm_medium=email&utm_campaign=202610-newsletter&ref=newsletter" target="_blank">San Francisco Data Engineering Meetup</a> - San Francisco - Nov 17, 2026
* <a href="https://clickhouse.com/company/events/202611toronoto?utm_source=clickhouse&utm_medium=email&utm_campaign=202610-newsletter&ref=newsletter" target="_blank">Toronto Data Engineering Meetup</a> - Toronto - Nov 18, 2026
* <a href="https://reinvent.awsevents.com/" target="_blank">AWS re:Invent</a> - Las Vegas - Nov 30, 2026

### Events in EMEA

* <a href="https://www.google.com/search?q=hayadata+tel+aviv&oq=hayadata+tel+aviv&gs_lcrp=EgZjaHJvbWUqBggAEEUYOzIGCAAQRRg7MgcIARAhGKAB0gEIMTYyNGowajeoAgCwAgA&sourceid=chrome&source=chrome.ob&ie=UTF-8" target="_blank">Hayadata Israel</a>, Oct 20, 2026
* <a href="https://www.postgresql.org/about/event/pgconfeu-2026-2587/" target="_blank">PostgreSQL Conference Europe - Oct 20-23, 2026</a>
* <a href="https://aws.amazon.com/events/cloud-days/riyadh/" target="_blank">AWS Cloud Days Riyadh</a> - Oct 21, 2026
* <a href="https://vds.tech/" target="_blank">VDS Startup Valencia</a> - Oct 21,22, 2026
* <a href="https://clickhouse.com/company/events/202610-EMEA-London-Real-time-Analytics-w-ClickHouse?utm_source=clickhouse&utm_medium=email&utm_campaign=202610-newsletter&ref=newsletter" target="_blank">London In-Person Training: Real-time Analytics with ClickHouse</a> - Oct 21, 2026
* <a href="https://clickhouse.com/company/events/ai-builders-and-analytics-oct-london-2026?utm_source=clickhouse&utm_medium=email&utm_campaign=202610-newsletter&ref=newsletter" target="_blank">AI Builders and Analytics London</a> - Oct 21, 2026
* <a href="https://luma.com/clickh-vtzf" target="_blank">AI Builders and Databases Dubai</a> - Oct 22, 2026
* <a href="https://battleofthequants.com/london-2026/" target="_blank">Battle of the Quants London - Oct 22, 2026</a>
* <a href="https://clickhouse.com/company/events/202610-EMEA-Dublin-Real-time-Analytics-w-ClickHouse?utm_source=clickhouse&utm_medium=email&utm_campaign=202610-newsletter&ref=newsletter" target="_blank">Dublin In-Person Training: Real-time Analytics with ClickHouse</a> - Oct 23, 2026
* <a href="https://thenetwork-group.com/dach-chief-data-officer-network/" target="_blank">CDO Frankfurt</a> - Nov 2,3 2026
* <a href="https://luma.com/clickh-1qqg" target="_blank">AI Builders and Databases Madrid</a> - Nov 3, 2026
* <a href="https://clickhouse.com/company/events/202611-EMEA-Krakow-Real-time-Analytics-w-ClickHouse?utm_source=clickhouse&utm_medium=email&utm_campaign=202610-newsletter&ref=newsletter" target="_blank">Krakow 2-day In-Person Training: Real-time Analytics with ClickHouse</a> - Krakow - Nov 3, 2026
* <a href="https://luma.com/clickh-az0n" target="_blank">AI Builders and Databases Krakow</a> - Krakow - Nov 4, 2026
* <a href="https://forward-data-conference.com/en/" target="_blank">Forward Data Paris</a> - Nov 16, 2026
* <a href="https://clickhouse.com/company/events/202611-EMEA-Paris-Real-time-Analytics-w-ClickHouse?utm_source=clickhouse&utm_medium=email&utm_campaign=202610-newsletter&ref=newsletter" target="_blank">Paris 2-day In-Person Training: Real-time Analytics with ClickHouse</a> - Paris - Nov 25, 2026
* <a href="https://clickhouse.com/company/events/ai-builders-and-databases-nov-cyprus-2026?utm_source=clickhouse&utm_medium=email&utm_campaign=202610-newsletter&ref=newsletter" target="_blank">AI Builders and Databases Cyprus</a> - Limassol - Nov 26, 2026
* <a href="https://datatlv.com/Home.html" target="_blank">Data TLV Israel,</a> Nov 26, 2026

### Events in APAC and Japan

* <a href="https://clickhouse.com/company/events/202610-APJ-Webinar-Build-a-unified-data-stack-Postgres-and-ClickHouse?utm_source=clickhouse&utm_medium=email&utm_campaign=202610-newsletter&ref=newsletter" target="_blank">Build a unified data stack for real-time AI with Postgres and ClickHouse</a> - Webinar - Oct 22, 2026
* <a href="https://clickhouse.com/company/events/202611-APJ-Melbourne-The-Agentic-Data-Stack?utm_source=clickhouse&utm_medium=email&utm_campaign=202610-newsletter&ref=newsletter" target="_blank">The Agentic Data Stack - Melbourne</a> - Melbourne - Nov 5, 2026
* <a href="https://clickhouse.com/company/events/202611-APJ-Sydney-The-Agentic-Data-Stack?utm_source=clickhouse&utm_medium=email&utm_campaign=202610-newsletter&ref=newsletter" target="_blank">The Agentic Data Stack - Sydney</a> - Sydney - Nov 10, 2026
* <a href="https://clickhouse.com/company/events/202611-APJ-Brisbane-The-Agentic-Data-Stack?utm_source=clickhouse&utm_medium=email&utm_campaign=202610-newsletter&ref=newsletter" target="_blank">The Agentic Data Stack - Brisbane</a> - Brisbane - Nov 11, 2026
* <a href="https://clickhouse.com/company/events/202611-APJ-Bengaluru-The-Agentic-Data-Stack?utm_source=clickhouse&utm_medium=email&utm_campaign=202610-newsletter&ref=newsletter" target="_blank">The Agentic Data Stack - Bengaluru</a> - Bengaluru - Nov 12, 2026
* <a href="https://clickhouse.com/company/events/202611-APJ-Auckland-The-Agentic-Data-Stack?utm_source=clickhouse&utm_medium=email&utm_campaign=202610-newsletter&ref=newsletter" target="_blank">The Agentic Data Stack - Auckland</a> - Auckland - Nov 17, 2026
* <a href="https://clickhouse.com/company/events/202611-APJ-Wellington-The-Agentic-Data-Stack?utm_source=clickhouse&utm_medium=email&utm_campaign=202610-newsletter&ref=newsletter" target="_blank">The Agentic Data Stack - Wellington</a> - Wellington - Nov 18, 2026
