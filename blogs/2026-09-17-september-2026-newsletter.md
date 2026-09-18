---
title: "September 2026 newsletter"
date: "2026-09-17T14:34:32.331Z"
author: "Mark Needham"
category: "Community"
excerpt: "Welcome to the September 2026 ClickHouse newsletter, featuring ClickHouse 26.8, PromQL, On-Demand Compute, CostBench results, and the latest community news and events."
---

# September 2026 newsletter

Hello and welcome to another ClickHouse newsletter!

We’ve got another feature-packed ClickHouse release, with custom HTTP handlers, pipelined SQL, and Japanese/Chinese tokenizers for the text-index.

Elsewhere, Mohamed Hussain S dives into the replication queue, Tom Schreiber and Lionel Palacin share the first end-to-end results from CostBench, and Himanshu Pandey walks us through reading ClickHouse query plans.

We also have preview releases of PromQL, On-Demand Compute, AI functions, and sub-second Postgres replication to ClickHouse

## Featured community member: Rory Shanks {#featured-community-member}

This month's featured community member is Rory Shanks, ClickHouse Engineer at PostHog.

![](https://clickhouse.com/uploads/sep2026_nl_image1_6de95ac8bc.png)

Rory’s background is in site reliability and cloud platform engineering, and he previously worked as a Staff DevOps Engineer at ENWAY and a Senior Site Reliability Engineer at Inkitt and powercloud.

Rory contributed several improvements to ClickHouse 26.8, released at the end of August.

First, he added an <a href="https://github.com/ClickHouse/ClickHouse/pull/113020" target="_blank">option for replicas to fetch already mutated data parts</a> from another replica, avoiding the need to repeat mutation work locally. Additionally, he added <a href="https://github.com/ClickHouse/ClickHouse/pull/112742" target="_blank">caching for tokens absent from the text index</a> and <a href="https://github.com/ClickHouse/ClickHouse/pull/113008" target="_blank">improved JSON subcolumn reads</a> by reusing column metadata during conversions.

➡️ <a href="https://www.linkedin.com/in/rorylshanks/" target="_blank">Connect with Rory on LinkedIn</a>

## Open House Roadshow {#open_house_roadshow}

We’re halfway through the <a href="https://clickhouse.com/company/events?category=Open+House&utm_source=clickhouse&utm_medium=email&utm_campaign=202609-newsletter&ref=newsletter" target="_blank">Open House Roadshow</a>, but there are still visits to come in <a href="https://clickhouse.com/company/events/202609-APJ-India-Bangalore-Open-House-Roadshow?utm_source=clickhouse&utm_medium=email&utm_campaign=202609-newsletter&ref=newsletter" target="_blank">Bangalore</a> (Sep 22), <a href="https://clickhouse.com/openhouse/london-2026?utm_source=clickhouse&utm_medium=email&utm_campaign=202609-newsletter&ref=newsletter" target="_blank">London</a> (Sep 30), and <a href="https://clickhouse.com/company/events/202610-munich-open-house?utm_source=clickhouse&utm_medium=email&utm_campaign=202609-newsletter&ref=newsletter" target="_blank">Munich</a> (Oct 6), so don’t forget to sign up!

➡️ <a href="https://clickhouse.com/company/events?category=Open+House&utm_source=clickhouse&utm_medium=email&utm_campaign=202609-newsletter&ref=newsletter" target="_blank">See all Open House locations</a>

## 26.8 release {#release}

![](https://clickhouse.com/uploads/sep2026_nl_image2_791480bdd7.png)

After last month’s mega 26.7 release blog post, we’ve decided to try something different this month: multiple smaller posts!

The 26.8 release includes a series of features, such as custom HTTP handlers and dynamic query filtering, that enable you to use <a href="https://clickhouse.com/blog/clickhouse-streaming-http-api?utm_source=clickhouse&utm_medium=email&utm_campaign=202609-newsletter&ref=newsletter" target="_blank">ClickHouse as a streaming HTTP API</a>. This release also adds a new `|>` operator that lets us write <a href="https://clickhouse.com/blog/pipelined-sql-26.8?utm_source=clickhouse&utm_medium=email&utm_campaign=202609-newsletter&ref=newsletter" target="_blank">queries as a sequence of transformations</a>.

The release also adds a `system.user_query_log` table that shows only the current user’s queries, a URL database engine, and Japanese and Chinese tokenizer support for the text index.

➡️ <a href="https://clickhouse.com/blog/clickhouse-release-26-08?utm_source=clickhouse&utm_medium=email&utm_campaign=202609-newsletter&ref=newsletter" target="_blank">Read the release post</a>

## Understanding the replication queue in ClickHouse {#replication_queue}

![](https://clickhouse.com/uploads/sep2026_nl_image3_3287f1a43b.png)

Mohamed Hussain S explores ClickHouse’s replication queue by stopping a replica and investigating the backlog.

He shows how to use the `system.replicas` and `system.replication_queue` system tables to diagnose issues, and explains why a non-empty queue doesn’t necessarily mean something is wrong.

➡️ <a href="https://dev.to/mohhddhassan/understanding-the-replication-queue-in-clickhouse-gl6" target="_blank">Read the blog post</a>

## Measuring real-time performance per dollar under continuous load: CostBench’s first end-to-end results {#costbench_results}

![](https://clickhouse.com/uploads/sep2026_nl_image4_91a192e230.jpg)

Tom Schreiber and Lionel Palacin share the first end-to-end results from <a href="https://clickhouse.com/blog/costbench-data-warehouse-cost-performance?utm_source=clickhouse&utm_medium=email&utm_campaign=202609-newsletter&ref=newsletter" target="_blank">CostBench</a>, an open benchmark for cloud data warehouse cost-performance: performance-per-dollar, rather than just speed.

They test ClickHouse Cloud, Snowflake, BigQuery, and Redshift Serverless under continuous ingestion, measuring the cost of keeping fresh data ready for queries alongside query performance.

In a follow-up post, they <a href="https://clickhouse.com/blog/clickhouse-vs-snowflake-real-time-performance-per-dollar?utm_source=clickhouse&utm_medium=email&utm_campaign=202609-newsletter&ref=newsletter" target="_blank">take a closer look at the ClickHouse Cloud and Snowflake results</a>, explaining how their architectures and billing models contribute to the performance-per-dollar gap.

➡️ <a href="https://clickhouse.com/blog/costbench-real-time-performance-per-dollar?utm_source=clickhouse&utm_medium=email&utm_campaign=202609-newsletter&ref=newsletter" target="_blank">Read the blog post</a>

## Announcing On-Demand Compute: Instant compute for your most intensive workloads {#on_demand_compute}

![](https://clickhouse.com/uploads/sep2026_nl_image5_6883c67807.jpg)

This is one of the biggest features we have been working on: On-Demand Compute is now in <a href="https://clickhouse.com/cloud/on-demand-compute-waitlist?utm_source=clickhouse&utm_medium=email&utm_campaign=202609-newsletter&ref=newsletter" target="_blank">private preview</a>.

You are now a step away from offloading intensive workloads to dedicated ClickHouse workers. And it doesn’t land alone! It comes with two friends:

• A new cost-based optimizer (CBO)  
• A new distributed query execution framework

The dream for anybody wanting to offload ad-hoc or data lake queries to dedicated workers!

Curious to learn more? Melvyn Peignon will present a <a href="https://clickhouse.com/company/events/202609-AMER-Webinar-On-Demand-Compute?utm_source=clickhouse&utm_medium=email&utm_campaign=202609-newsletter&ref=newsletter" target="_blank">live webinar on September 24th</a>, where he’ll explain how it works, give a live demo, and talk through the six-month roadmap.

➡️ <a href="https://clickhouse.com/blog/on-demand-compute?utm_source=clickhouse&utm_medium=email&utm_campaign=202609-newsletter&ref=newsletter" target="_blank">Read the announcement</a>

## ClickHouse 26.8 LTS: 57 Breaking Changes Since 26.3 {#clickhouse_26_8_lts}

![](https://clickhouse.com/uploads/sep2026_nl_image6_cc65b466a3.png)

Mohamed Hussain S has written an alternative blog post for the 26.8 release, exploring changes since the previous LTS release, 26.3.

He highlights breaking changes and new defaults across all five releases, with a checklist of what to audit before upgrading and monitor afterward.

➡️ <a href="https://dev.to/mohhddhassan/clickhouse-268-lts-57-breaking-changes-since-263-3ba9" target="_blank">Read the blog post</a>

## Postgres Round-up {#postgres_round_up}

![](https://clickhouse.com/uploads/sep2026_nl_image7_fc6aee448d.jpg)

We’ve been publishing more and more <a href="https://clickhouse.com/blog?search=postgres&utm_source=clickhouse&utm_medium=email&utm_campaign=202609-newsletter&ref=newsletter" target="_blank">Postgres content</a> as the weeks go by, so I thought it deserved its own section in the newsletter.

* Sai Srirampur announced <a href="https://clickhouse.com/blog/introducing-walshadow?utm_source=clickhouse&utm_medium=email&utm_campaign=202609-newsletter&ref=newsletter" target="_blank">WalShadow</a>, an open-source engine that replicates Postgres data to ClickHouse directly from the physical WAL. It’s available as an open-source project or in <a href="https://clickhouse.com/cloud/postgres/walshadow?utm_source=clickhouse&utm_medium=email&utm_campaign=202609-newsletter&ref=newsletter" target="_blank">private preview on ClickHouse Managed Postgres</a>.
* Kunal Gupta announced the availability of <a href="https://clickhouse.com/blog/postgres-managed-by-clickhouse-gcp-private-preview?utm_source=clickhouse&utm_medium=email&utm_campaign=202609-newsletter&ref=newsletter" target="_blank">ClickHouse Managed Postgres on Google Cloud</a>, also in <a href="https://clickhouse.com/cloud/postgres?utm_source=clickhouse&utm_medium=email&utm_campaign=202609-newsletter&ref=newsletter#gcp-waitlist" target="_blank">private preview</a> for the time being.
* David Wheeler announced the open-source <a href="https://clickhouse.com/blog/introducing-chdb-postgres?utm_source=clickhouse&utm_medium=email&utm_campaign=202609-newsletter&ref=newsletter" target="_blank">chdb Postgres extension</a>, which expands Postgres import and export features via the <a href="https://clickhouse.com/docs/chdb?utm_source=clickhouse&utm_medium=email&utm_campaign=202609-newsletter&ref=newsletter" target="_blank">chDB</a> library.
* Gülçin Yıldırım Jelínek has started writing a series of blog posts on Postgres 19\. So far, she’s covered <a href="https://clickhouse.com/blog/postgres-19-monitoring-whats-new?utm_source=clickhouse&utm_medium=email&utm_campaign=202609-newsletter&ref=newsletter" target="_blank">monitoring</a>, <a href="https://clickhouse.com/blog/postgres-19-new-system-views?utm_source=clickhouse&utm_medium=email&utm_campaign=202609-newsletter&ref=newsletter" target="_blank">new system views</a>, and <a href="https://clickhouse.com/blog/postgresql-19-wait-for-read-your-writes?utm_source=clickhouse&utm_medium=email&utm_campaign=202609-newsletter&ref=newsletter" target="_blank">read-your-writes</a>.
* Kaushik Iska explains how ClickHouse Managed Postgres <a href="https://clickhouse.com/blog/protect-postgres-from-supporting-processes?utm_source=clickhouse&utm_medium=email&utm_campaign=202609-newsletter&ref=newsletter" target="_blank">protects Postgres from resource-hungry supporting processes</a>.
* Sai Srirampur explores <a href="https://clickhouse.com/blog/posette-talk-recap-postgres-isnt-slow-your-storage-is?utm_source=clickhouse&utm_medium=email&utm_campaign=202609-newsletter&ref=newsletter" target="_blank">how storage choices affect Postgres performance</a>.
* Cristina Albu and Yashpreet Bathla walk through <a href="https://clickhouse.com/blog/clickhouse-managed-postgres-onboarding?utm_source=clickhouse&utm_medium=email&utm_campaign=202609-newsletter&ref=newsletter" target="_blank">a new onboarding flow for ClickHouse Managed Postgres</a>.

## Introducing ClickHouse's new TimeSeries Engine: Your drop-In Prometheus replacement {#promql_timeseries_engine}

![](https://clickhouse.com/uploads/sep2026_nl_image8_6086cc19f9.png)  
James Cunningham introduces PromQL and the TimeSeries table engine in ClickHouse Cloud, now in <a href="https://clickhouse.com/cloud/promql-support-waitlist?utm_source=clickhouse&utm_medium=email&utm_campaign=202609-newsletter&ref=newsletter" target="_blank">private preview</a>.

You can send metrics to ClickHouse through Prometheus remote write and query them with PromQL in Grafana, ClickHouse, or ClickStack, all while keeping your existing collection setup.

➡️ <a href="https://clickhouse.com/blog/introducing-promql?utm_source=clickhouse&utm_medium=email&utm_campaign=202609-newsletter&ref=newsletter" target="_blank">Read the blog post</a>

## Quick reads {#quick-reads}

* Saarth Soni <a href="https://medium.com/@saarthsoni/wikipulse-what-streaming-and-batch-actually-disagree-about-afbd88e1c267" target="_blank">compares streaming and batch counts of Wikipedia edits</a> using Quix Streams and ClickHouse, exploring why the same data can yield different results.
* Oleksandr Andrushchenko <a href="https://medium.com/@oleksandr.andrushchenko1988/clickhouse-vs-postgresql-what-happens-at-billion-row-scale-8506a11f2836" target="_blank">compares ClickHouse and PostgreSQL for SMS analytics</a>, reporting that ClickHouse processes 10 times more rows and exploring how query shape affects performance.
* Himanshu Pandey <a href="https://medium.com/@hp12/reading-a-clickhouse-explain-plan-ffb4e8353098" target="_blank">explains how to read ClickHouse query plans</a> to understand query execution and investigate performance.
* Andriy Yakovlev and George Larionov <a href="https://clickhouse.com/blog/ai-functions-in-clickhouse?utm_source=clickhouse&utm_medium=email&utm_campaign=202609-newsletter&ref=newsletter" target="_blank">introduce AI Functions in ClickHouse</a>, bringing AI models into SQL for tasks such as text generation, classification, and embeddings.
* Pete Hampton <a href="https://clickhouse.com/blog/mcp-toolbox-clickhouse-vectors?utm_source=clickhouse&utm_medium=email&utm_campaign=202609-newsletter&ref=newsletter" target="_blank">shows how to build semantic search with Google’s MCP Toolbox and ClickHouse</a>, automatically turning text into embeddings for storage and search.
* Lareb Zafar <a href="https://clickhouse.com/blog/clickgap-autonomous-qa-for-clickhouse?utm_source=clickhouse&utm_medium=email&utm_campaign=202609-newsletter&ref=newsletter" target="_blank">introduces ClickGap</a>, an autonomous QA agent that tests merged ClickHouse changes and traces regressions to the commits that introduced them.

## Upcoming events {#upcoming-events}

### Global virtual events

* Webinar: <a href="https://clickhouse.com/company/events/202609-AMER-Webinar-On-Demand-Compute?utm_source=clickhouse&utm_medium=email&utm_campaign=202609-newsletter&ref=newsletter" target="_blank">What if your most intensive queries could run on more compute? Introducing On-Demand Compute</a> - Sep 24, 2026 (AMER)
* Webinar: <a href="https://clickhouse.com/company/events/202610-EMEA-Webinar-On-Demand-Compute?utm_source=clickhouse&utm_medium=email&utm_campaign=202609-newsletter&ref=newsletter" target="_blank">What if your most intensive queries could run on more compute? Introducing On-Demand Compute</a> - Oct 7, 2026 (EMEA)

### Virtual training

* <a href="https://clickhouse.com/company/events/202609-APJ-query-optimization-workshop?utm_source=clickhouse&utm_medium=email&utm_campaign=202609-newsletter&ref=newsletter" target="_blank">Query Optimization with ClickHouse Workshop</a> - Sep 29, 2026
* <a href="https://clickhouse.com/company/events/202609-AMER-PostgreSQL-ClickHouse-Better-Together?utm_source=clickhouse&utm_medium=email&utm_campaign=202609-newsletter&ref=newsletter" target="_blank">PostgreSQL and ClickHouse, Better Together</a> -  - Oct 8, 2026
* <a href="https://clickhouse.com/company/events/202610-APJ-Real-time-Analytics-ClickHouse-Level1?utm_source=clickhouse&utm_medium=email&utm_campaign=202609-newsletter&ref=newsletter" target="_blank">Real-time Analytics with ClickHouse: Level 1</a> - Oct 20, 2026
* <a href="https://clickhouse.com/company/events/202610-APJ-Real-time-Analytics-ClickHouse-Level2?utm_source=clickhouse&utm_medium=email&utm_campaign=202609-newsletter&ref=newsletter" target="_blank">Real-time Analytics with ClickHouse: Level 2</a> - Oct 21, 2026
* <a href="https://clickhouse.com/company/events/202610-APJ-Real-time-Analytics-ClickHouse-Level3?utm_source=clickhouse&utm_medium=email&utm_campaign=202609-newsletter&ref=newsletter" target="_blank">Real-time Analytics with ClickHouse: Level 3</a> - Oct 22, 2026

### Events in AMER

* <a href="https://luma.com/clickh-wavw" target="_blank">Rows and Columns summit San Francisco</a> - Sep 22nd
* <a href="https://cloudonair.withgoogle.com/events/google-cloud-summit-brasil-2026-1" target="_blank">Google Cloud Summit Brasil</a> - Sep 23-24, 2026
* <a href="https://runway.runreveal.com/" target="_blank">Runway by RunReveal</a> - San Francisco - Sep 29, 2026
* <a href="https://coreweave.com/fully-connected-2026" target="_blank">CoreWeave Fully Connected</a> - San Francisco - Sep 29 - Oct 2, 2026
* <a href="https://clickhouse.com/company/events/202610-LATAM-SaoPaulo-Observability-with-ClickStack/?utm_source=clickhouse&utm_medium=email&utm_campaign=202609-newsletter&ref=newsletter" target="_blank">Sao Paulo In-person training</a> - Observabilidade com ClickStack - Sao Paulo - Oct 8, 2026
* Sao Paulo Meetup - Observabilidade de Agentes em Escala: o Case do iFood com Langfuse - Sao Paulo - Oct 8, 2026

### Events in EMEA

* <a href="https://ai.engineer/paris/2026" target="_blank">AI Engineer Paris (Langfuse) - Sept 22-24, 2026</a>
* <a href="https://clickhouse.com/company/events/202609-EMEA-Stockholm-Real-time-Analytics-w-ClickHouse?utm_source=clickhouse&utm_medium=email&utm_campaign=202609-newsletter&ref=newsletter" target="_blank">Stockholm In-Person Training: Real-time Analytics with ClickHouse</a> - Sep 23, 2026
* <a href="https://luma.com/p7td11mb" target="_blank">AI Builders and Databases Barcelona</a> - Sep 23, 2026
* <a href="https://www.bigdataldn.com/" target="_blank">BigDataLondon - Sept 23-24, 2026</a>
* <a href="https://clickhouse.com/company/events/202609-EMEA-Copenhagen-Real-time-Analytics-w-ClickHouse?utm_source=clickhouse&utm_medium=email&utm_campaign=202609-newsletter&ref=newsletter" target="_blank">Copenhagen In-person training - Sept 24, 2026</a>
* <a href="https://espc.tech/conference/fabcon-europe-2026/" target="_blank">FabCON - Sept 28 - Oct 1</a>
* <a href="https://go2.striim.com/2026-fabcon-ai-roundtable?tracker=clickhouse" target="_blank">FabCon Lunch and Learn - Sept 30, 2026</a>
* <a href="https://clickhouse.com/company/events/ai-builders-and-databases-sep-paris-2026?utm_source=clickhouse&utm_medium=email&utm_campaign=202609-newsletter&ref=newsletter" target="_blank">AI Builders and Databases Paris</a> - Sep 29, 2026
* <a href="https://www.agenticaiforum.net/" target="_blank">Agentic AI Forum Dubai</a> - Sept 30, 2026
* <a href="https://clickhouse.com/company/events/202609-EMEA-London-AI-Agents-w-Langfuse?utm_source=clickhouse&utm_medium=email&utm_campaign=202609-newsletter&ref=newsletter" target="_blank">London In-person training - From 0 to Production: Observing and Improving AI Agents with Langfuse</a> - Sep 30, 2026
* <a href="https://clickhouse.com/company/events/202609-EMEA-London-One-Database-Every-Workload?utm_source=clickhouse&utm_medium=email&utm_campaign=202609-newsletter&ref=newsletter" target="_blank">London In-person training - One Database, Every Workload: A ClickHouse Workshop</a> - Sep 30, 2026
* <a href="https://clickhouse.com/openhouse/london-2026?utm_source=clickhouse&utm_medium=email&utm_campaign=202609-newsletter&ref=newsletter" target="_blank">Open House Roadshow London</a> - Sep 30, 2026
* <a href="https://clickhouse.com/company/events/202610-EMEA-Munich-AI-Agents-w-Langfuse?utm_source=clickhouse&utm_medium=email&utm_campaign=202609-newsletter&ref=newsletter" target="_blank">Munich In-person training - From 0 to Production: Observing and Improving AI Agents with Langfuse</a> - Oct 6, 2026
* <a href="https://clickhouse.com/company/events/202610-EMEA-Munich-One-Database-Every-Workload?utm_source=clickhouse&utm_medium=email&utm_campaign=202609-newsletter&ref=newsletter" target="_blank">Munich In-person training - One Database, Every Workload: A ClickHouse Workshop</a> - Oct 6, 2026
* <a href="https://clickhouse.com/company/events/202610-munich-open-house?utm_source=clickhouse&utm_medium=email&utm_campaign=202609-newsletter&ref=newsletter" target="_blank">Open House Roadshow Munich</a> - Oct 6, 2026
* <a href="https://worldsummit.ai/" target="_blank">World Summit AI Amsterdam</a> - Oct 7-8, 2026
* <a href="https://clickhouse.com/company/events/ai-builders-and-databases-oct-stockholm-2026?utm_source=clickhouse&utm_medium=email&utm_campaign=202609-newsletter&ref=newsletter" target="_blank">AI Builders and Databases Stockholm</a> - Oct 8, 2026
* <a href="https://clickhouse.com/company/events/ai-builders-and-databases-oct-tel-aviv-2026?utm_source=clickhouse&utm_medium=email&utm_campaign=202609-newsletter&ref=newsletter" target="_blank">AI Builders and Databases Tel Aviv</a> - Oct 12, 2026
* <a href="https://luma.com/clickh-6n6u" target="_blank">SRECon Dublin Happy Hour by the Quay</a> - Oct 13, 2026
* <a href="https://www.usenix.org/conference/srecon25emea" target="_blank">SRECon Dublin</a> - Oct 13-15, 2026
* <a href="https://datainnovationsummit.com/region/mea/" target="_blank">Data Innovation Summit Dubai</a> Oct 14-15
* <a href="https://clickhouse.com/company/events/202610-EMEA-Oslo-Real-time-Analytics-w-ClickHouse?utm_source=clickhouse&utm_medium=email&utm_campaign=202609-newsletter&ref=newsletter" target="_blank">Oslo In-Person Training: Real-time Analytics with ClickHouse</a> - Oct 14, 2026
* <a href="https://www.postgresql.org/about/event/pgconfeu-2026-2587/" target="_blank">PostgreSQL Conference Europe - Oct 20-23, 2026</a>
* <a href="https://aws.amazon.com/events/cloud-days/riyadh/" target="_blank">AWS Cloud Days Riyadh</a> - Oct 21, 2026
* <a href="https://clickhouse.com/company/events/202610-EMEA-London-Real-time-Analytics-w-ClickHouse?utm_source=clickhouse&utm_medium=email&utm_campaign=202609-newsletter&ref=newsletter" target="_blank">London In-Person Training: Real-time Analytics with ClickHouse</a> - Oct 21, 2026
* <a href="https://clickhouse.com/company/events/ai-builders-and-analytics-oct-london-2026?utm_source=clickhouse&utm_medium=email&utm_campaign=202609-newsletter&ref=newsletter" target="_blank">AI Builders and Analytics London</a> - Oct 21, 2026
* <a href="https://luma.com/clickh-vtzf" target="_blank">AI Builders and Databases Dubai</a> - Oct 22, 2026
* <a href="https://battleofthequants.com/london-2026/" target="_blank">Battle of the Quants London - Oct 22, 2026</a>
* <a href="https://clickhouse.com/company/events/202610-EMEA-Dublin-Real-time-Analytics-w-ClickHouse?utm_source=clickhouse&utm_medium=email&utm_campaign=202609-newsletter&ref=newsletter" target="_blank">Dublin In-Person Training: Real-time Analytics with ClickHouse</a> - Oct 23, 2026
* <a href="https://luma.com/clickh-1qqg" target="_blank">AI Builders and Databases Madrid</a> - Nov 3, 2026
* <a href="https://clickhouse.com/company/events/ai-builders-and-databases-nov-cyprus-2026?utm_source=clickhouse&utm_medium=email&utm_campaign=202609-newsletter&ref=newsletter" target="_blank">AI Builders and Databases Cyprus</a> - Limassol - Nov 26, 2026

### Events in APAC

* <a href="https://clickhouse.com/company/events/202609-APJ-India-Bangalore-Open-House-Roadshow?utm_source=clickhouse&utm_medium=email&utm_campaign=202609-newsletter&ref=newsletter" target="_blank">Open House Roadshow Bangalore</a> - Sep 22, 2026
* Singapore - <a href="https://clickhouse.com/company/events/202609-APJ-Singapore-AI-Agents-w-Langfuse?utm_source=clickhouse&utm_medium=email&utm_campaign=202609-newsletter&ref=newsletter" target="_blank">From 0 to Production: Observing and Improving AI Agents with Langfuse</a> - Sep 24, 2026
* Singapore: <a href="https://clickhouse.com/company/events/202609-APJ-Singapore-One-Database-Every-Workload?utm_source=clickhouse&utm_medium=email&utm_campaign=202609-newsletter&ref=newsletter" target="_blank">One Database, Every Workload: A ClickHouse Workshop</a> - Sep 24, 2026
* Singapore: <a href="https://clickhouse.com/company/events/build-better-llm-apps-with-langfuse-singapore?utm_source=clickhouse&utm_medium=email&utm_campaign=202609-newsletter&ref=newsletter" target="_blank">Build Better LLM Apps</a> - Sep 29, 2026
* Auckland: <a href="https://clickhouse.com/company/events/one-database-every-workload-new-zealand?utm_source=clickhouse&utm_medium=email&utm_campaign=202609-newsletter&ref=newsletter" target="_blank">One Database, Every Workload: A ClickHouse Workshop</a> - Oct 6, 2026
* Auckland: <a href="https://clickhouse.com/company/events/nz-unified-data-stack-postgres-clickhouse?utm_source=clickhouse&utm_medium=email&utm_campaign=202609-newsletter&ref=newsletter" target="_blank">Build a unified data stack with Postgres and ClickHouse</a> - Oct 6, 2026
* Singapore: <a href="https://events.confluent.io/confluent-fsi-singapore-2026" target="_blank">Confluent Financial Services Leaders Summit</a> - Oct 9, 2026
* Sydney: <a href="https://clickhouse-workshop-syd.innovatusmediaevents.com/" target="_blank">Build a unified data stack for real-time AI with Postgres and ClickHouse</a> - Oct 13, 2026
* Melbourne: <a href="https://clickhouse.com/company/events/build-better-llm-apps-with-langfuse-melbourne?utm_source=clickhouse&utm_medium=email&utm_campaign=202609-newsletter&ref=newsletter" target="_blank">Build Better LLM Apps</a> - Oct 15, 2026
