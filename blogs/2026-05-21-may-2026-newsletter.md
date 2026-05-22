---
title: "May 2026 newsletter"
date: "2026-05-21T10:02:42.633Z"
author: "Mark Needham"
category: "Community"
excerpt: "Welcome to the May 2026 ClickHouse newsletter, which will round up what’s happened in real-time data warehouses over the last month."
---

# May 2026 newsletter

Hello, and welcome to the May 2026 ClickHouse newsletter!

This month's issue is heavy on observability, with Javier Ortiz on how Qonto replaced Grafana Tempo with ClickHouse Cloud, and LINE MAN Wongnai's walkthrough of rebuilding their stack to handle 60 billion records a day at 10x better storage efficiency.

There's also an AI thread running through: Qonto's MCP-powered incident companion, Mastra's new ClickHouse adapter for agent telemetry, and Benjamin Wootton on agentic analytics in financial services.

And rounding things out, Mark Needham covers index-based pruning, and Tom Schreiber and Lionel Palacin make the case against Elasticsearch for log analytics.

## Featured community member: Javier Ortiz {#featured-community-member}

This month's featured community member is Javier Ortiz, Tech Lead for SRE Observability at Qonto, a digital banking platform serving over 600,000 small businesses and freelancers across Europe.

![](https://clickhouse.com/uploads/newsletter_may2026_image1_b67d7bae92.png)

Javier built their observability function from the ground up, growing the team from zero to four engineers while staying hands-on across architecture, tooling, and incident response.

When Qonto's Grafana Tempo-based tracing setup started hitting its limits, Javier led the migration to ClickHouse Cloud for unified observability across traces, logs, and events. <a href="https://clickhouse.com/resources/engineering/database-compression" target="_blank">ClickHouse's compression</a> reduced their high-cardinality trace metadata from 231 TB uncompressed to 376 GB on disk, making it feasible to store everything without sampling, and query windows expanded from a few hours to two weeks. He also built an AI-powered incident companion on top of the <a href="https://clickhouse.com/blog/integrating-clickhouse-mcp" target="_blank">ClickHouse MCP server</a>, enabling engineers to quickly investigate production issues in natural language.

In February 2026, Javier presented this work at the ClickHouse Meetup in Paris in a talk titled "<a href="https://clickhouse.com/videos/qonto-supercharging-observability" target="_blank">Supercharging Observability with ClickHouse and AI</a>", which was also written up as a <a href="https://clickhouse.com/blog/qonto" target="_blank">blog post</a>.

➡️ <a href="https://www.linkedin.com/in/ortizjaviere/" target="_blank">Connect with Javier on LinkedIn</a>

## Open House 2026 {#open-house}

It's now only one week until Open House, a free three-day ClickHouse user conference running May 26-28 at Convene, San Francisco.

Kick things off on May 26 with hands-on workshops on real-time analytics, observability, AI agents, and database administration, then head into two days of keynotes, technical sessions, and networking.

Hear from ClickHouse's CEO Aaron Katz and CTO Alexey Milovidov, plus Bret Taylor (Sierra), Guillermo Rauch (Vercel), Charity Majors (Honeycomb.io), Tristan Handy (dbt Labs), and practitioners from Visa, Cisco, Shopify, and Zoox. Admission is free!

➡️ <a href="https://clickhouse.com/openhouse/san-francisco" target="_blank">Register now</a>

## 26.4 release {#26-4-release}

![](https://clickhouse.com/uploads/newsletter_may2026_image2_6e5c11640f.png)

The 26.4 release had a big focus on SQL compatibility features, including VALUES as a table expression, natural join, and compound INTERVAL literals.

There's also a new function, `JSONAllValues`, for adding a text index on all JSON sub-columns, `COUNT(DISTINCT)` got faster on machines with many cores, and the web UI was polished.

➡️ <a href="https://clickhouse.com/blog/clickhouse-release-26-04" target="_blank">Read the release post</a>

## How LINE MAN Wongnai handles 60 billion records a day at 10x better storage efficiency {#how-line-man-wongnai-handles-60-billion-records-a-day}

![](https://clickhouse.com/uploads/newsletter_may2026_image3_a6b59dcfbb.png)

Tanawit Aeabsakul walks through how the Platform & SRE team at LINE MAN Wongnai rebuilt their observability stack on self-hosted ClickHouse to serve three independent business clusters (LINE MAN, Wongnai, and FoodStory) that previously had no shared query surface.

The result is 1.5 million rows per second at peak ingest, 10x compression with 143 TB of raw data stored in just 14 TB on disk, a 53% reduction in observability costs, and 100% trace retention after years of sampling.

➡️ <a href="https://life.wongnai.com/how-we-reduced-storage-10x-while-handling-60-billion-records-a-day-0ed9b9783362" target="_blank">Read the blog post</a>

## Do you still need Elasticsearch for log analytics? ClickHouse says no. {#do-you-still-need-elasticsearch-for-log-analytics}

![](https://clickhouse.com/uploads/newsletter_may2026_image4_28bb62ef54.png)

Tom Schreiber and Lionel Palacin benchmarked ClickHouse against Elasticsearch for log analytics on datasets up to 50 billion rows.

ClickHouse uses 5x less disk space and runs queries 4-6x faster on cold runs, and Tom and Lio argue that logs are fundamentally analytical data that happen to contain text, making a dedicated search engine the wrong tool for the job.

➡️ <a href="https://clickhouse.com/blog/elasticsearch-log-analytics-clickhouse" target="_blank">Read the blog post</a>

## Deploying agentic analytics in financial services {#deploying-agentic-analytics-in-financial-services}

![](https://clickhouse.com/uploads/newsletter_may2026_image5_8be65be4ff.png)

Benjamin Wootton explores why financial services has emerged as an early adopter of agentic analytics, with use cases spanning trade surveillance, complaint analysis, and KYC/AML automation.

He argues that the convergence of better LLMs, MCP servers, and observability tooling has made the approach production-ready, and that ClickHouse's ability to handle tens of concurrent queries makes it a natural fit for the workload.

➡️ <a href="https://benjaminwootton.com/insights/agentic-analytics-financial-services" target="_blank">Read the blog post</a>

## ClickStack SQL Charting and Alerting {#clickstack-sql-charting-and-alerting}

![](https://clickhouse.com/uploads/newsletter_may2026_image6_2d0db8b946.png)

Drew Davis and Dale McDiarmid introduce SQL-based charting and alerting in ClickStack, letting you build dashboards and alerts from arbitrary ClickHouse SQL rather than a fixed query builder.

Queries adapt automatically to dashboard time ranges and filters via macros, and alerting supports analytical patterns, such as error spikes relative to rolling baselines rather than static thresholds.

➡️ <a href="https://clickhouse.com/blog/clickstack-sql-charting-and-alerting" target="_blank">Read the blog post</a>

## Index-based pruning in ClickHouse {#index-based-pruning-in-clickhouse}

![](https://clickhouse.com/uploads/newsletter_may2026_image7_0e9d16c884.png)

Mark Needham walks through three index-based pruning strategies in ClickHouse: the primary index, lightweight projections, and minmax skip indexes.

Using a UK property sales dataset, he builds intuition for which technique to reach for and why the choice depends on how your data is ordered on disk.

➡️ <a href="https://clickhouse.com/blog/index-based-pruning" target="_blank">Read the blog post</a>

## Quick reads {#quick-reads}

* The Mastra team <a href="https://mastra.ai/blog/introducing-clickhouse-support" target="_blank">announced native ClickHouse support in the Mastra AI agent framework</a> with a new storage adapter that persists agent telemetry, traces, and logs to ClickHouse Cloud or self-hosted ClickHouse for production observability.
* Mobin Shaterian <a href="https://medium.com/stackademic/connecting-kafka-to-clickhouse-with-ssl-a-complete-integration-guide-e5a0a5957de3" target="_blank">walks through connecting a SASL_SSL-secured Kafka cluster to ClickHouse</a>, covering SSL configuration, building the ingestion pipeline with a Kafka engine table and materialized view, and performance tuning tips.
* Denis Sazonov covers ClickHouse in <a href="https://medium.com/@sadensmol/learning-system-design-9-clickhouse-why-analytical-databases-are-absurdly-fast-9bc1dfef29f9" target="_blank">part nine of his Learning System Design series</a>, explaining why analytical databases are so fast through columnar storage, per-column compression codecs, vectorized SIMD execution, and the sparse primary index. He also provides practical guidance on MergeTree, LowCardinality, and correctly batching inserts.
* The ClickStack team introduces <a href="https://clickhouse.com/blog/otel-fyi" target="_blank">otel.fyi</a>, a search-first documentation site for the OpenTelemetry Collector that consolidates receiver, processor, exporter, and extension configuration into a single place.

---

## Get started today

Interested in seeing how ClickHouse works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-656-get-started-today-sign-up&utm_blogctaid=656)

---

## Upcoming events {#upcoming-events}

### Global virtual events

* <a href="https://clickhouse.com/company/events/202605-APJ-Webinar-Observing-and-Improving-AI-Agents-with-Langfuse" target="_blank">Observing and Improving AI Agents with Langfuse</a> - May 27, 2026
* <a href="https://clickhouse.com/company/events/202605-EMEA-DACH-Webinar-MaterializedViews-DE" target="_blank">Real-Time Analytics ohne ETL: Inkrementelle Materialized Views und Dictionaries in ClickHouse</a> - May 28, 2026
* <a href="https://clickhouse.com/company/events/202605-LATAM-Agentic-AI-Webinar" target="_blank">Maximizando a produtividade dos seus Agentes de IA com ClickHouse</a> - Jun 16, 2026

### Virtual training

* <a href="https://clickhouse.com/company/events/202606-AMER-Observability-with-ClickStack-Level1" target="_blank">Observability with ClickStack: Level 1</a> - Jun 3, 2026
* <a href="https://clickhouse.com/company/events/202606-APJ-ClickHouse-Fundamentals" target="_blank">ClickHouse Fundamentals</a> - Jun 10, 2026
* <a href="https://clickhouse.com/company/events/202606-AMER-EMEA-ClickHouse-Fundamentals" target="_blank">ClickHouse Fundamentals</a> - Jun 24, 2026
* <a href="https://clickhouse.com/company/events/202607-APJ-Observability-with-ClickStack-Level1" target="_blank">Observability with ClickStack: Level 1</a> - Jul 8, 2026
* <a href="https://clickhouse.com/company/events/202607-APJ-Observabiity-with-ClickStack-Level2" target="_blank">Observability with ClickStack: Level 2</a> - Jul 9, 2026
* <a href="https://clickhouse.com/company/events/202607-APJ-Observabiity-with-ClickStack-Level3" target="_blank">Observability with ClickStack: Level 3</a> - Jul 10, 2026
* <a href="https://clickhouse.com/company/events/202607-AMER-EMEA-query-optimization-workshop" target="_blank">Query Optimization with ClickHouse Workshop</a> - Jul 22, 2026

### Events in AMER

* <a href="https://clickhouse.com/company/events/202606torontomeetup" target="_blank">Toronto Meetup</a> - Toronto - Jun 2, 2026
* <a href="https://clickhouse.com/company/events/202606-LATAM-Bogota-Real-time-Analytics-with-ClickHouse" target="_blank">Capacitación presencial en Bogotá: Analytics en tiempo real con ClickHouse</a> - Bogotá - Jun 2, 2026
* <a href="https://luma.com/64ox1was" target="_blank">Bogotá Meetup</a> - Jun 2, 2026
* <a href="https://luma.com/clickh-0h6k" target="_blank">ClickHouse Café @ Snowflake Summit</a> - Jun 3, 2026
* <a href="https://luma.com/c7p3qazp" target="_blank">AWS Summit Toronto Happy Hour with rootly AI</a> - Toronto - Jun 3, 2026
* AWS Summit Toronto - Toronto - Jun 3, 2026
* <a href="https://clickhouse.com/company/events/202606-AMER-Toronto-Real-time-Analytics-w-ClickHouse" target="_blank">Toronto In-Person Training: Real-time Analytics with ClickHouse</a> - Toronto - Jun 5, 2026
* <a href="https://rio.websummit.com/" target="_blank">Web Summit Rio de Janeiro</a> - Jun 9-11, 2026
* AWS Summit Los Angeles - Los Angeles - Jun 10, 2026
* <a href="https://luma.com/clickh-2ujv" target="_blank">ClickHouse + Hex AI Hackathon</a> - Jun 11, 2026
* <a href="https://luma.com/clickh-87tk" target="_blank">Sao Paulo Meetup</a> - Jun 11, 2026
* <a href="https://luma.com/clickh-vrjd" target="_blank">ClickHouse Cafe @ Data & AI summit</a> - San Francisco - Jun 16, 2026
* AWS Summit NYC - NYC - Jun 17, 2026
* <a href="https://luma.com/odgqf98e" target="_blank">AWS Summit NYC Happy Hour with rootly AI</a> - New York - Jun 17, 2026
* <a href="https://luma.com/jr8tc94e" target="_blank">ClickHouse Vancouver Meetup</a> - Jun 23, 2026
* <a href="https://luma.com/vwt2i2rs" target="_blank">Apache Iceberg Seattle Meetup</a> - Jun 25, 2026
* <a href="https://luma.com/clickh-2crf" target="_blank">AI Demo Night SF</a> - Jul 1, 2026
* <a href="https://luma.com/clickh-o8up" target="_blank">Happy Hour Open Source de Montreal</a> - Jul 9, 2026

### Events in EMEA

* <a href="https://clickhouse.com/company/events/202605-EMEA-DACH-Germany-Hamburg-AWS-Summit-Hamburg" target="_blank">AWS Summit</a> - Hamburg - May 19, 2026
* <a href="https://clickhouse.com/company/events/202605-EMEA-London-Real-time-Analytics-w-ClickHouse" target="_blank">London In-Person Training: Real-time Analytics with ClickHouse</a> - London - May 19, 2026
* <a href="https://clickhouse.com/company/events/202605-EMEA-SPIGT-Spain-GoogleSummit-Madrid" target="_blank">Google Summit Madrid</a> - Madrid - May 28, 2026
* <a href="https://europe.money2020.com/" target="_blank">Money 2020</a> - Amsterdam - Jun 2, 2026
* <a href="https://clickhouse.com/company/events/202605-EMEA-SPIGT-Spain-AWSSummitMadrid" target="_blank">AWS Summit Madrid</a> - Madrid - Jun 4, 2026
* <a href="https://luma.com/0stvf1vi" target="_blank">Hands-on Workshop</a> - Tel Aviv - Jun 9, 2026
* <a href="https://cloudonair.withgoogle.com/events/cloud-ai-live-amsterdam-2026" target="_blank">Google Cloud AI Live</a> - Amsterdam - Jun 11, 2026
* <a href="https://thenetwork-group.com/benelux-chief-data-officer-network/" target="_blank">Benelux CDO Network</a> - Amsterdam - Jun 15, 2026
* <a href="https://vivatech.com/" target="_blank">Vivatech</a> - Paris - Jun 17, 2026
* <a href="https://clickhouse.com/company/events/202606-EMEA-Benelux-Amsterdam-The-Agentic-Data-Stack" target="_blank">The Agentic Data Stack</a> - Amsterdam - Jun 18, 2026
* <a href="https://www.tdwi-konferenz.de/" target="_blank">TDWI</a> - Munich - Jun 23, 2026

### Events in APAC

* <a href="https://clickhouse.com/company/events/202605-APJ-3P-Tokyo-FindyVPoESummit" target="_blank">Findy VPoE Summit</a> - Tokyo - May 22, 2026
* Bangkok OSS & Data Evening - Bangkok - May 27, 2026
* <a href="https://clickhouse.com/company/events/202605-APJ-3P-Mumbai-AWSSummit" target="_blank">AWS Summit Mumbai</a> - Mumbai - May 28, 2026
* <a href="https://clickhouse.com/company/events/202605-APJ-3P-Bangkok-AWSSummit" target="_blank">AWS Summit Bangkok</a> - Bangkok - May 28, 2026
* <a href="https://clickhouse.com/company/events/202606-APJ-3P-Tokyo-FindyAIEngineeringSummit" target="_blank">AI Engineering Summit</a> - Tokyo - Jun 8, 2026
* <a href="https://clickhouse.com/company/events/202606-APJ-3P-Singapore-SuperAI" target="_blank">SuperAI</a> - Singapore - Jun 10, 2026
* <a href="https://clickhouse.com/company/events/202606-APJ-3P-Sydney-GartnerData-and-Analytics" target="_blank">Gartner Data & Analytics Summit Sydney</a> - Sydney - Jun 16, 2026
* <a href="https://clickhouse.com/company/events/202606-APJ-3P-HongKong-AWSSummit" target="_blank">AWS Summit Hong Kong</a> - Hong Kong - Jun 17, 2026
* <a href="https://clickhouse.com/company/events/202606-APJ-3P-Mumbai-KubeCon" target="_blank">KubeCon + CloudNativeCon India</a> - Mumbai - Jun 18, 2026
* <a href="https://clickhouse.com/company/events/202606-APJ-3P-KualaLumpur-KCD" target="_blank">KCD Kuala Lumpur</a> - Kuala Lumpur - Jun 27, 2026
* <a href="https://clickhouse.com/company/events/202607-APJ-3P-Melbourne-DataEngBytes" target="_blank">DataEngBytes Melbourne</a> - Melbourne - Jul 23, 2026
* <a href="https://clickhouse.com/company/events/202607-APJ-3P-Sydney-DataEngBytes" target="_blank">DataEngBytes Sydney</a> - Sydney - Jul 28, 2026
* <a href="https://clickhouse.com/company/events/202607-APJ-3P-Tokyo-GoogleNext" target="_blank">Google Cloud Next Tokyo</a> - Tokyo - Jul 30, 2026
