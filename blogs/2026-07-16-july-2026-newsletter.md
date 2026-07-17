---
title: "July 2026 newsletter"
date: "2026-07-16T13:28:24.587Z"
author: "Mark Needham"
category: "Community"
excerpt: "Welcome to the July 2026 ClickHouse newsletter, which will round up what’s happened in real-time data warehouses over the last month."
---

# July 2026 newsletter

We're well into the summer in the Northern hemisphere, but the content keeps on coming!

Highlights from the 26.6 release include hypothetical skip indexes, AI embedding functions, and experimental support for continuous queries.

Charity Majors explains why ClickHouse is winning the observability wars, on the benchmarking front, Tom Schreiber puts Snowflake Interactive Tables head-to-head with ClickHouse Cloud, measuring cost and performance across the full pipeline, and if you're wrangling lots of small queries, Sanil Upadhyay has a guide to tuning ClickHouse for exactly that.

And don’t miss our first-ever virtual hackathon, from July 17-23.

## Featured community member: Rafeeq Abdul {#featured-community-member}

This month's featured community member is Rafeeq Abdul, Senior Director of Engineering for the Authorize.net payments solution at Visa.
![](https://clickhouse.com/uploads/jul2026_nl_image2_b0f39fe8fe.png)

Rafeeq's team manages $250 million in annual revenue across 2 million authorization events, but until recently, getting an answer out of that data meant waiting 2-3 days for a specialized SQL engineer to write a report.

He led the move to conversational analytics, pairing ClickHouse Cloud with the open-source LibreChat interface and the ClickHouse MCP server so non-technical staff can now ask questions like "show revenue risk by merchant segment" in natural language.

This solution helped surface millions in at-risk revenue and has reclaimed 8-10 hours per user each week. Rafeeq <a href="https://clickhouse.com/blog/visa-conversational-agents" target="_blank">shared the story</a> at ClickHouse's 2026 Open House user conference in San Francisco.

➡️ <a href="https://www.linkedin.com/in/rafeeqabdul/" target="_blank">Connect with Rafeeq on LinkedIn</a>

## Virtual Summer Hackathon: July 17-23 {#virtual-summer-hackathon}

![](https://clickhouse.com/uploads/jul2026_nl_image3_21f96b528b.png)

We're running our first-ever virtual hackathon, and you should apply!

The ClickHouse & Trigger.dev Virtual Summer Hackathon runs July 17 - 23. Build a production-quality AI agent chat experience using ClickHouse and Trigger.dev, compete for a share of EUR 10,000 in prizes, and get your work in front of a panel of 15+ judges, including ClickHouse founder Alexey Milovidov.

Open to professional developers across NAMER and EMEA. Solo or teams up to 5. Applications close July 16.

➡️ <a href="https://luma.com/clickh-uko4" target="_blank">Apply now</a>

## 26.6 release {#clickhouse-release-26-6}

![](https://clickhouse.com/uploads/jul2026_nl_image4_ef0ce18e4e.png)

My favorite feature from the 26.6 release is hypothetical skip indexes, which let you see whether adding a skip index to a table would improve query performance without actually building it.

This release also cleaned up how dependencies work for refreshable materialized views, so that we have proper cascading refreshable materialized views.

There’s also experimental support for continuous queries and AI embedding functions, a PNG output format, documentation built into the CLI, and Geospatial improvements.

➡️ <a href="https://clickhouse.com/blog/clickhouse-release-26-06" target="_blank">Read the release post</a>

## Have you heard? ClickHouse is winning the observability wars! {#clickhouse-winning-observability-wars}

![](https://clickhouse.com/uploads/jul2026_nl_image5_48359c12b1.png)

Charity Majors, Co-founder and CTO of observability company Honeycomb, argues that ClickHouse's columnar architecture, not lower price, is why post-2019 observability vendors can keep scaling past the point where three-pillar tools become "unmanageable."

She quotes <a href="https://matduggan.com/clickhouse-is-winning-the-observability-wars/" target="_blank">Mat Duggan</a> on the core idea: "ClickHouse at 10 TB a day looks like ClickHouse at 1 TB a day, just with more shards."

At 10 TB/day, Duggan's numbers show ClickHouse costing over 35x less than Datadog. He notes that most companies at this scale go hybrid: Datadog for APM and metrics, plus a self-hosted stack (often ClickHouse itself) for logs, plus a "pre-processing pipeline team" whose only job is trimming data to cut the Datadog bill.

What frustrates Charity is that vendors built on that same columnar core hide the architecture and market themselves as cheap Datadog clones instead of owning why they're actually better.

➡️ <a href="https://charity.wtf/p/have-you-heard-clickhouse-is-winning" target="_blank">Read the blog post</a>

## The end-to-end cost-performance of real-time analytics: Snowflake vs. ClickHouse Cloud {#snowflake-vs-clickhouse-cloud}

![](https://clickhouse.com/uploads/jul2026_nl_image6_c0a12569be.jpg)

Tom Schreiber, Mark Needham, and Lionel Palacin use CostBench to compare ClickHouse Cloud against Snowflake's Interactive Tables.

CostBench is an end-to-end benchmark that measures the true cost of real-time analytics across continuous ingestion, data maintenance, freshness, and query execution rather than query speed alone.

Running the full path over 28 hours, ClickHouse delivered better cost-performance, while Snowflake required a continuously running refresh warehouse to keep its pre-aggregated data up to date.

➡️ <a href="https://clickhouse.com/blog/real-time-analytics-cost-performance-snowflake-vs-clickhouse" target="_blank">Read the blog post</a>

## We don't copy our Postgres tables to ClickHouse. We replay them. {#postgres-cdc-replay}

![](https://clickhouse.com/uploads/jul2026_nl_image7_584dc3e019.png)

Sushant Yadav wires up Postgres→ClickHouse change-data-capture from off-the-shelf parts: Debezium decoding the WAL, Kafka carrying the row changes, and a ReplacingMergeTree sink keeping the latest version per key.

He then covers two challenges they encountered: silently-cached schemas on the sink and a replication slot that can fill the disk and freeze every database on the instance.

This blog gives a clear look at CDC on top of Postgres logical replication, which is the same foundation <a href="https://clickhouse.com/cloud/clickpipes/postgres-cdc" target="_blank">PeerDB / ClickPipes for Postgres CDC</a> builds on, minus the Debezium-and-Kafka assembly you'd otherwise manage yourself.

➡️ <a href="https://medium.com/@sushant8421/we-dont-copy-our-postgres-tables-to-clickhouse-we-replay-them-a12234b1927f" target="_blank">Read the blog post</a>

## chDB as the Agent's Local Data Engine {#chdb-agents-local-data-engine}

![](https://clickhouse.com/uploads/jul2026_nl_image8_2be844bca4.jpg)

An AI agent runs as a loop of 5–20 tool calls per turn, and a large share of those calls are data lookups. But when that data lives across a network, latency compounds and every flaky call has to be retried - and a retry means re-sending the entire context window, which isn’t cheap.

chDB fixes this by embedding a full ClickHouse query engine inside the agent's own process, so memory, session state, and hot lookups are now a local function call away.

➡️ <a href="https://clickhouse.com/blog/chdb-agents-local-data-engine" target="_blank">Read the blog post</a>

## Tuning ClickHouse for high concurrency {#tuning-clickhouse-high-concurrency}

![](https://clickhouse.com/uploads/jul2026_nl_image9_a3f9b3758a.png)

Sanil Upadhyay explains how to tweak ClickHouse settings to handle many concurrent small queries rather than a few large ones.

➡️ <a href="https://medium.com/@sanil.upadhyay12/tuning-clickhouse-for-high-concurrency-53-118-qps-1cebec6eb15b" target="_blank">Read the blog post</a>

## Announcing Silk: a silky smooth fiber runtime for ClickHouse {#announcing-silk}

![](https://clickhouse.com/uploads/jul2026_nl_image10_b20210aa0a.jpg)

James Cunningham and Vadim Skipin introduce Silk, an open-source C++ fiber runtime designed to reduce tail latency in I/O-bound work such as distributed cache lookups and object storage access.

Silk pairs a NUMA-aware work-stealing scheduler with io_uring and zero heap allocation on the hot path, yielding fibers in about 3.6 nanoseconds and hitting 5.9 million file IOPS. This is roughly 15x the throughput of boost::asio at one connection, and 65% better at the 99.9th-percentile latency than a thread-pool executor at 10,000 concurrent S3-style requests.

➡️ <a href="https://clickhouse.com/blog/silk" target="_blank">Read the blog post</a>

## Quick reads {#quick-reads}

* Zepto fixed a ClickHouse ingestion bottleneck under Confluent Cloud by patching the <a href="https://blog.zepto.com/clickhouse-ingestion-at-scale-an-open-source-zepto-engineering-story-7f57309e2175" target="_blank">open-source Kafka Connect connector</a> with cross-poll buffering and rewriting the serialization logic to use Jackson instead of Gson, boosting throughput 45%.
* Sergio De Simone explains how Momentic redesigned its AI-testing cache on ClickHouse after Postgres buckled under lock contention at ~1 billion entries, using `ReplacingMergeTree` and a composite primary key to scale to <a href="https://www.infoq.com/news/2026/07/momentic-postgres-clickhouse/" target="_blank">20 billion entries at 2M+ queries/day and ~250ms latency</a>.
* Muhammad Ali <a href="https://www.linkedin.com/pulse/i-gave-clickhouse-agents-my-telemetry-understand-traffic-muhammad-ali-y1hkc/" target="_blank">wired a Claude-powered SRE agent</a> to his OpenTelemetry data via ClickHouse Agents, and it dug through the logs, traces, and metrics to surface sqlmap SQL-injection probes, Nuclei vulnerability scans, and unauthenticated endpoints leaking credentials.
* Gaurav Pant <a href="https://medium.com/@gaurav.pant./why-clickhouse-is-so-fast-the-right-olap-1bdeb761de4e" target="_blank">explains why ClickHouse is so fast</a>, showing how columnar storage, a sparse primary index, SIMD vectorization, and immutable parts stack up, so that each layer multiplies the benefits of the others.
* Justin Torre <a href="https://www.justintorre.com/blogs/clickhouse-rls-query-parameters" target="_blank">shows how they safely let customers run arbitrary SQL against a shared, multi-tenant ClickHouse table by</a> enforcing tenancy in the database with a row policy and per-query settings.

---

## Get started today

Interested in seeing how ClickHouse works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-1335-get-started-today-sign-up&utm_blogctaid=1335)

---

## Upcoming events {#upcoming-events}

### Global virtual events

* <a href="https://clickhouse.com/company/events/202607-EMEA-Webinar-AskanExpert" target="_blank">Live Q&A: Ask a ClickHouse Expert</a> - Jul 21, 2026
* <a href="https://clickhouse.com/company/events/v26-7-community-release-call" target="_blank">v26.7 Community Call</a> - Jul 23, 2026
* <a href="https://clickhouse.com/company/events/202607-AMER-Webinar-Postgres-ClickHouse" target="_blank">How to build a unified data stack with Postgres and ClickHouse</a> - Jul 28, 2026
* <a href="https://clickhouse.com/company/events/202607_APJ_Event_Build-Better-LLM-Apps" target="_blank">Build Better LLM Apps</a> - Jul 30, 2026
* <a href="https://clickhouse.com/company/events/202608-APJ-Webinar-Open-Office-AMA" target="_blank">ClickHouse Open Office & Live AMA</a> - Aug 6, 2026
* <a href="https://clickhouse.com/company/events/202608-EMEA-Webinar-Costbench" target="_blank">Measuring the True Cost of Real-Time Analytics</a> - Aug 18, 2026

### Virtual training

* <a href="https://clickhouse.com/company/events/202607-AMER-EMEA-query-optimization-workshop" target="_blank">Query Optimization with ClickHouse Workshop</a> - Jul 22, 2026
* <a href="https://clickhouse.com/company/events/202607-APJ-ClickHouse-Fundamentals" target="_blank">ClickHouse Fundamentals</a> - Jul 28, 2026
* <a href="https://clickhouse.com/company/events/202607-AMER-Data-Warehousing-Level1" target="_blank">Data Warehousing with ClickHouse: Level 1</a> - Jul 28, 2026
* <a href="https://clickhouse.com/company/events/202607-AMER-data-warehousing-Level2" target="_blank">Data Warehousing with ClickHouse: Level 2</a> - Jul 29, 2026
* <a href="https://clickhouse.com/company/events/202607-AMER-data-warehousing-Level3" target="_blank">Data Warehousing with ClickHouse: Level 3</a> - Jul 30, 2026
* <a href="https://clickhouse.com/company/events/202608-EMEA-AMER-Real-time-Analytics-w-ClickHouse-Level1" target="_blank">Real-time Analytics with ClickHouse: Level 1</a> - Aug 4, 2026
* <a href="https://clickhouse.com/company/events/202608-EMEA-AMER-Real-time-Analytics-w-ClickHouse-Level2" target="_blank">Real-time Analytics with ClickHouse: Level 2</a> - Aug 5, 2026
* <a href="https://clickhouse.com/company/events/202608-EMEA-AMER-Real-time-Analytics-w-ClickHouse-Level3" target="_blank">Real-time Analytics with ClickHouse: Level 3</a> - Aug 6, 2026
* <a href="https://clickhouse.com/company/events/202608-AMER-EMEA-ClickHouse-Fundamentals" target="_blank">ClickHouse Fundamentals</a> - Aug 19, 2026

### Events in EMEA

* <a href="https://clickhouse.com/openhouse/amsterdam-2026" target="_blank">Open House AMS</a> - Sept 1
* <a href="https://luma.com/clickh-2ccj" target="_blank">The Agentic Data Stack: Berlin</a> - Sep 2
* <a href="https://techracesummit.com/" target="_blank">TechRace Summit: Poland</a> - Sep 10
* <a href="https://signalsconf.io/" target="_blank">Signals Berlin</a> (Langfuse) - Sept 10
* <a href="https://aws.amazon.com/events/summits/tel-aviv/" target="_blank">AWS Summit Tel Aviv</a> - Sept 10
* <a href="https://luma.com/clickh-vu1p" target="_blank">ClickHouse Amsterdam with Ayden</a> - Sep 15
* <a href="https://luma.com/clickh-dw1v" target="_blank">ClickHouse CapeTown Happy Hour</a> - Sep 15
* <a href="https://www.bigdataparis.com/en-gb.html" target="_blank">BigDataParis</a> - Sept 15-16
* <a href="https://events.linuxfoundation.org/agntcon-mcpcon-europe/" target="_blank">AgentCon + MCPCon</a> - Sept 17-18
* <a href="https://event.idc.com/event/ai-data-summit-spain/" target="_blank">IDC Madrid</a> - Sept 22
* <a href="https://luma.com/clickh-gsz1" target="_blank">ClickHouse Paris Meetup</a> - Sep 29
* <a href="https://clickhouse.com/openhouse/london-2026" target="_blank">Open House UK</a> - Sept 30
* <a href="https://www.agenticaiforum.net/" target="_blank">Agentic AI Forum Dubai</a> - Sept 30

### Events in AMER

* <a href="https://luma.com/clickh-9f9d" target="_blank">Hands-on training: Building agents with ClickHouse, Langfuse, and LibreChat</a> - San Francisco, CA - Jul 21, 2026
* <a href="https://luma.com/clickh-bkld" target="_blank">Happy Hour Warm-up AWS Summit Bogotá</a> - Jul 29, 2026
* <a href="https://clickhouse.com/company/events/202607-LATAM-AWS-Summit-Colombia" target="_blank">AWS Summit Bogotá</a> - Jul 30, 2026
* <a href="https://clickhouse.com/company/events/202608-LATAM-Buesno-Aires-Real-time-Analytics-with-ClickHouse" target="_blank">Capacitación presencial en Buenos Aires: Analytics en tiempo real con ClickHouse</a> - Buenos Aires - Aug 4, 2026
* <a href="https://clickhouse.com/company/events/202608-LATAM-Santiago-Real-time-Analytics-with-ClickHouse" target="_blank">Capacitación presencial en Santiago: Analytics en tiempo real con ClickHouse</a> - Santiago - Aug 6, 2026
* <a href="https://luma.com/qeg73alr" target="_blank">AI Demo Night</a> - Seattle, WA - Aug 6, 2026
* <a href="https://clickhouse.com/company/events/202607-LATAM-AWS-Summit-Mexico-City" target="_blank">AWS Summit Mexico City</a> - Aug 12, 2026
* <a href="https://luma.com/clickh-z578" target="_blank">Data Engineering Meetup</a> - San Francisco, CA - Aug 11, 2026
* <a href="https://luma.com/c4alsewg" target="_blank">AI Demo Night</a> - New York, NY - Aug 18, 2026
* <a href="https://luma.com/t3z5q5s8" target="_blank">NYC Iceberg™ Meetup</a> - New York, NY - Aug 20, 2026
* <a href="https://luma.com/jr8tc94e" target="_blank">Vancouver Meetup</a> - Vancouver, Canada - Aug 25, 2026
* <a href="https://luma.com/clickh-sie8" target="_blank">ClickHouse Hackathon</a> - San Francisco, CA - Aug 28, 2026
* <a href="https://luma.com/sl4dcdhx" target="_blank">Open House New York</a> 🏠 - New York, NY - Sep 10, 2026
* <a href="https://luma.com/clickh-wavw" target="_blank">Rows and Columns Summit</a> - San Francisco, CA - Sep 22, 2026

### Events in APAC

* <a href="https://clickhouse.com/company/events/ch-del-meetup-18jul26" target="_blank">ClickHouse in the Wild: Architecture Stories from Production</a> - Delhi - Jul 18, 2026
* <a href="https://clickhouse.com/company/events/202607-APJ-Training-Japan-RealTimeAnalytics-Level1" target="_blank">Training: Real-time Analytics with ClickHouse Level 1</a> - Tokyo - Jul 22, 2026
* <a href="https://clickhouse.com/company/events/202607-APJ-3P-Melbourne-DataEngBytes" target="_blank">DataEngBytes Melbourne</a> - Jul 23, 2026
* <a href="https://clickhouse.com/company/events/ch-bkk-meetup-23jul26" target="_blank">Bangkok OSS & Data Evening: Queries, Code & Community</a> - Jul 23, 2026
* <a href="https://clickhouse.com/company/events/ch-bom-meetup-25jul26" target="_blank">Lakes to Queries: Building High-Performance Data Platforms</a> - Mumbai - Jul 25, 2026
* <a href="https://clickhouse.com/company/events/2026-07-APJ-ASEAN-Singapore-BuildWorkshop" target="_blank">ClickHouse BUILD hands-on workshop - Singapore</a> - Jul 28, 2026
* <a href="https://clickhouse.com/company/events/202607-APJ-3P-Sydney-DataEngBytes" target="_blank">DataEngBytes Sydney</a> - Jul 28, 2026
* <a href="https://clickhouse.com/company/events/202607-APJ-3P-Tokyo-GoogleNext" target="_blank">Google Cloud Next Tokyo</a> - Jul 30, 2026
* <a href="https://clickhouse.com/clickathon/india2026" target="_blank">Click-a-Thon India</a> - Bangalore - August 1-2, 2026
* <a href="https://clickhouse.com/company/events/2026-08-APJ-ASEAN-Indonesia-Jakarta-BuildWorkshop" target="_blank">ClickHouse BUILD hands-on workshop - Jakarta</a> - Aug 5, 2026
* <a href="https://clickhouse.com/company/events/ch-jkt-meetup-05aug26" target="_blank">ClickHouse Jakarta Meetup - August 2026</a> - Aug 5, 2026
* <a href="https://clickhouse.com/company/events/202608-sydney-open-house" target="_blank">Open House Roadshow - Sydney</a> - Aug 11, 2026
* <a href="https://clickhouse.com/company/events/202608-APJ-Sydney-One-Database-Every-Workload" target="_blank">Sydney In-person training - One Database, Every Workload: A ClickHouse Workshop</a> - Aug 11, 2026
* <a href="https://clickhouse.com/company/events/202608-melbourne-open-house" target="_blank">Open House Roadshow - Melbourne</a> - Aug 13, 2026
* <a href="https://clickhouse.com/company/events/202608-APJ-Melbourne-One-Database-Every-Workload" target="_blank">Melbourne In-person training - One Database, Every Workload: A ClickHouse Workshop</a> - Aug 13, 2026
* <a href="https://clickhouse.com/company/events/ch-blr-meetup-22aug26" target="_blank">Bangalore Iceberg Community Meetup</a> - Aug 22, 2026
