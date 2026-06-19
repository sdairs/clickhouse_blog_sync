---
title: "June 2026 newsletter"
date: "2026-06-18T09:23:47.185Z"
author: "Mark Needham"
category: "Community"
excerpt: "Welcome to the June 2026 ClickHouse newsletter, which will round up what’s happened in real-time data warehouses over the last month."
---

# June 2026 newsletter

Ten years ago this month, we released ClickHouse as an open-source project. What started as a prototype I built to solve a real data problem has grown into something I could not have imagined: 2,000 contributors, users on every continent, and a community that continues to push the project further than any single team could.

In this issue, you will find our own engineering updates alongside stories from community members building real systems with ClickHouse. Seeing people share what they have built is one of the best parts of having an open community.

Here's to the next ten years.

— Alexey Milovidov, inventor of ClickHouse

## Featured community member: Vasily Chekalkin {#featured-community-member}

This month's featured community member is Vasily Chekalkin, Staff Engineer at Neara in Sydney, Australia.

![](https://clickhouse.com/uploads/jun2026_nl_image1_96ed958d70.png)

Vasily contributed a series of improvements to ClickHouse's WebAssembly (WASM) user-defined functions in the 26.5 release.

He added a `DETERMINISTIC` keyword, which means WASM UDFs can be declared as pure functions, making them eligible for constant folding and widening coercions for arguments. He also made WASM UDFs visible in `system.functions` with their argument and return types. Together, these changes make WASM UDFs easier to introspect and better integrated with the query optimizer.

To see what's possible when you push WASM UDFs to their limits, check out his side project <a href="https://github.com/bacek/chgeos" target="_blank">chgeos</a> - PostGIS-compatible spatial functions for ClickHouse (`ST_Intersects`, `ST_Buffer`, `ST_Within`, and more) delivered as a WASM module powered by GEOS 3.12+.

Beyond WASM UDFs, Vasily is a regular contributor across ClickHouse's Geospatial and Iceberg functionality, from fixing WKT parsing to propagating table UUIDs from the Iceberg REST catalog.

➡️ <a href="https://www.linkedin.com/in/bacek/" target="_blank">Connect with Vasily on LinkedIn</a>

## Ten years of ClickHouse in open source {#ten-years-of-clickhouse-in-open-source}

![](https://clickhouse.com/uploads/jun2026_nl_image2_1e2d7960a0.png)

Alexey Milovidov kicked off the 10-year anniversary week with the full origin story.

It starts with a 2008 prototype built to keep up with web analytics data that was growing faster than any existing database could handle, runs through the open-source release on June 15, 2016, and reflects on what it means to build truly in the open, with 2,000+ contributors and counting.

➡️ <a href="https://clickhouse.com/blog/open-source-10" target="_blank">Read the blog post</a>

## 26.5 release {#265-release}

![](https://clickhouse.com/uploads/jun2026_nl_image3_0f8d84a5f8.png)

ClickHouse 26.5 sees some important performance optimizations, particularly around Top-N queries - those that sort or group a large dataset only to return a handful of rows.

Pushing `ORDER BY … LIMIT` through a JOIN (20.4× faster with 175× less memory on TPC-H SF100) and supporting `GROUP BY … LIMIT` without an `ORDER BY` (11.9× faster and 185× less peak memory) both let ClickHouse stop work early instead of processing rows it will only throw away later.

➡️ <a href="https://clickhouse.com/blog/clickhouse-release-26-05" target="_blank">Read the release post</a>

## Open House 2026 announcements {#open-house-2026-announcements}

![](https://clickhouse.com/uploads/jun2026_nl_image4_957b940dec.png)

We hosted our annual Open House conference a few weeks ago in San Francisco and detailed all the announcements in this blog post.

Highlights included **ClickHouse Postgres**, a managed Postgres service that achieved 5x+ more transactions/sec than AWS RDS, and **ClickHouse Agents**, a new agentic analytics service powered by Claude with a native chat interface and a no-code agent builder.

➡️ <a href="https://clickhouse.com/blog/open-house-2026-day-1" target="_blank">Read about the announcements</a>

## Introducing native ClickHouse support in Jaeger {#introducing-native-clickhouse-support-in-jaeger}

![](https://clickhouse.com/uploads/jun2026_nl_image5_42c462214c.png)

Mahad Zaryab walks through the design decisions behind native ClickHouse support in Jaeger v2.18.0, the most-requested storage backend from users running Jaeger at scale.

On a single-node benchmark, it achieved an ingestion rate of 50,000+ spans per second, with 8.6× compression, and sub-50ms search latency across 10 million spans.

➡️ <a href="https://medium.com/jaegertracing/introducing-native-clickhouse-support-in-jaeger-3341e8208720" target="_blank">Read the blog post</a>

## Building ClickCannon: a tool for benchmarking ClickHouse {#building-clickcannon-a-tool-for-benchmarking-clickhouse}

![](https://clickhouse.com/uploads/jun2026_nl_image6_f1677b8991.png)

Spencer Torres introduces ClickCannon, an open-source benchmarking tool for ClickHouse that grew out of internal work to build sizing recommendations for ClickStack.

It replays real production data at controlled throughput, simulates concurrent user query patterns, and decouples disk and insert workers, allowing each to be scaled independently, giving teams a flexible framework for testing any ClickHouse insert and query workload.

➡️ <a href="https://clickhouse.com/blog/building-clickcannon-a-tool-for-benchmark-clickhouse" target="_blank">Read the blog post</a>

## Building a high-throughput KPI pipeline on ClickHouse: partitioning, idempotent recalculation, and flat column storage {#building-a-high-throughput-kpi-pipeline-on-clickhouse-partitioning-idempotent-recalculation-and-flat-column-storage}

![](https://clickhouse.com/uploads/jun2026_nl_image7_fec53eddd2.png)

Mobin Shaterian details three ClickHouse-specific design decisions behind a telecom KPI pipeline processing 15 million rows per hour.

The pipeline uses `ALTER TABLE … DELETE` scoped to a time window for idempotent recalculation, stores hundreds of KPIs as flat columns for compression and query simplicity, and merges sparse KPI sources with CTEs and `FULL OUTER JOIN` so cells with missing data still land in the right row.

➡️ <a href="https://medium.com/stackademic/building-a-high-throughput-kpi-pipeline-on-clickhouse-partitioning-idempotent-recalculation-and-3302a12ddf83" target="_blank">Read the blog post</a>

## How ClickHouse became fast at joins {#how-clickhouse-became-fast-at-joins}

![](https://clickhouse.com/uploads/jun2026_nl_image8_baa16c3c5e.jpg)

Tom Schreiber charts two years of focused join engineering that made ClickHouse 26× faster on TPC-H SF100 join-heavy workloads.

Year one laid the foundation with parallel hash join as the default, smarter filter pushdown, and local join reordering.

In year two, we added correlated subquery support, lazy column replication, runtime filters, and statistics-based join reordering, the last of which dropped a six-table query from 3,903 seconds to 2.7 seconds.

➡️ <a href="https://clickhouse.com/blog/clickhouse-fast-joins" target="_blank">Read the blog post</a>

## Quick reads {#quick-reads}

* Mohamed Hussain S <a href="https://medium.com/stackademic/why-too-many-parts-destroy-clickhouse-performance-d143b75189e3" target="_blank">explains how to avoid ClickHouse's "too many parts" trap</a> by batching inserts into larger writes, using async inserts as a buffer, and avoiding overly granular partition keys, such as hourly timestamps.
* Mobin Shaterian <a href="https://medium.com/datadriveninvestor/how-we-rebuilt-a-telecom-kpi-platform-to-handle-billions-of-records-from-json-blobs-to-flat-1a4eb6b27574" target="_blank">explains how a telecom KPI platform was rebuilt to handle 10 billion records per month</a>, replacing JSON string columns with flat columnar storage, buffering inserts through Kafka, and pre-calculating KPIs with Airflow to cut query times from minutes to milliseconds.
* RaviKumar Vatthumalli explains how <a href="https://medium.com/@ravikumar.vattumalli.learning/3-reducing-browser-tab-memory-in-analytics-dashboards-with-clickhouse-arrowstream-24e3f01ce926" target="_blank">switching ClickHouse query results from JSON to ArrowStream</a> reduced memory usage in browser tabs for analytics dashboards.
* Caesario Kisty builds a <a href="https://blog.dataengineerthings.org/building-a-clickhouse-native-document-ingestion-pipeline-from-minio-to-vector-search-clickvector-448d6511f497" target="_blank">ClickHouse-native RAG ingestion pipeline</a> where ClickHouse handles state tracking, chunking, HNSW vector search, and scheduling via refreshable materialized views.
* Mark Needham wrote a blog post showing how to do [random native sampling in ClickHouse](https://clickhouse.com/blog/native-random-sampling)

---

## Get started today

Interested in seeing how ClickHouse works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-933-get-started-today-sign-up&utm_blogctaid=933)

---

## Events {#events}

### Global virtual events {#global-virtual-events}

* <a href="https://events.nikkeibp.co.jp/event/2026/nb26061819/" target="_blank">Nikkei AI Insight</a> - Jun 18, 2026
* <a href="https://clickhouse.com/company/events/202606-EMEA-Webinar-Unified-Data-Stack-ClickHouse-Postgres" target="_blank">Combining Postgres & ClickHouse to Build a Unified Data Stack</a> - Jun 23, 2026
* <a href="https://clickhouse.com/company/events/202606-AMER-CostBench" target="_blank">How to benchmark whether a system is truly real-time and cost-efficient</a> - Jun 24, 2026
* <a href="https://clickhouse.com/company/events/202606-EMEA-Webinar-FullTextSearch" target="_blank">Full Text Search at ClickHouse scale and speed</a> - Jun 30, 2026
* <a href="https://clickhouse.com/company/events/202607-APJ-Webinar-open-office-hour" target="_blank">ClickHouse Open Office & Live AMA</a> - Jul 2, 2026 (APJ-timing)
* <a href="https://clickhouse.com/company/events/202607-EMEA-Webinar-Langfuse" target="_blank">Observing and Improving AI Agents with Langfuse</a> - Jul 8, 2026

### Virtual training {#virtual-training}

* <a href="https://clickhouse.com/company/events/202606-AMER-EMEA-ClickHouse-Fundamentals" target="_blank">ClickHouse Fundamentals</a> - Jun 24, 2026
* <a href="https://clickhouse.com/company/events/202606-AMER-Integrating-ClickHouse-Data-Lake" target="_blank">Integrating ClickHouse with your Data Lake</a> - Jun 30, 2026
* <a href="https://clickhouse.com/company/events/202607-APJ-Observability-with-ClickStack-Level1" target="_blank">Observability with ClickStack: Level 1</a> - Jul 8, 2026 (APJ-timing)
* <a href="https://clickhouse.com/company/events/202607-APJ-Observabiity-with-ClickStack-Level2" target="_blank">Observability with ClickStack: Level 2</a> - Jul 9, 2026 (APJ-timing)
* <a href="https://clickhouse.com/company/events/202607-APJ-Observabiity-with-ClickStack-Level3" target="_blank">Observability with ClickStack: Level 3</a> - Jul 10, 2026 (APJ-timing)
* <a href="https://clickhouse.com/company/events/202607-AMER-EMEA-ClickHouse-Fundamentals" target="_blank">ClickHouse Fundamentals</a> - Jul 15, 2026

### Events in AMER {#events-in-amer}

* <a href="https://aws.amazon.com/events/summits/new-york/" target="_blank">AWS Summit New York</a> - New York - Jun 17, 2026
* <a href="https://clickhouse.com/company/events/seattleicejune26" target="_blank">Seattle Iceberg Meetup</a> - Seattle - Jun 25, 2026
* <a href="https://aws.amazon.com/es/events/summits/bogota/" target="_blank">AWS Summit Bogotá</a> - Bogotá - Jul 30, 2026

### Events in EMEA {#events-in-emea}

* <a href="https://cloudonair.withgoogle.com/events/london-summit-26-register-your-interest" target="_blank">Google Cloud Summit London</a> - London - Jun 17, 2026
* <a href="https://vivatech.com" target="_blank">VivaTech</a> - Paris - Jun 17, 2026
* <a href="https://clickhouse.com/company/events/202606-EMEA-Benelux-Amsterdam-The%20Agentic%20Data%20Stack" target="_blank">The Agentic Data Stack</a> - Amsterdam - Jun 18, 2026
* <a href="https://clickhouse.com/company/events/202606-EMEA-France-Paris-ClickHousePartner%20Meetup" target="_blank">Meetup Partenaires ClickHouse - Paris</a> - Jun 24, 2026
* <a href="https://clickhouse.com/company/events/AgenticAI-Energy-Amsterdam" target="_blank">Agentic AI in the Energy Industry - Panel Session</a> - Amsterdam - Jul 1, 2026
* <a href="https://luma.com/clickh-ha56" target="_blank">Data at Scale</a> - Amsterdam - Jul 7, 2026
* <a href="https://clickhouse.com/company/events/202607-EMEA-DACH-Germany-Berlin-WeAreDevelopers-MeetingRequest" target="_blank">WeAreDevelopers</a> - Berlin - Jul 8, 2026
* <a href="https://clickhouse.com/openhouse/amsterdam-2026?utm_source=marketo&utm_medium=email&utm_campaign=202609-EMEA-Benelux-Netherlands-Amsterdam-Open-House-Roadshow" target="_blank">Open House Roadshow</a> - Amsterdam - Sept 1, 2026
* <a href="https://clickhouse.com/openhouse/london-2026?utm_source=marketo&utm_medium=email&utm_campaign=202609-EMEA-UKI-London-Open-House-Roadshow" target="_blank">Open House Roadshow</a> - London - Sept 30, 2026

### Events in APAC {#events-in-apac}

* <a href="https://clickhouse.com/company/events/202606-APJ-3P-Mumbai-KubeCon" target="_blank">KubeCon + CloudNativeCon India</a> - Mumbai - Jun 18-19, 2026
* <a href="https://luma.com/clickhouse" target="_blank">ClaudSG x ClickHouse: How AI Queries & Answers From your Data - Singapore</a> - Singapore - June 19, 2026
* <a href="https://pycon.sg/" target="_blank">PyCon Singapore</a> - Singapore - June 19-20, 2026
* <a href="https://clickhouse.com/company/events/2026-06_APJ_China_Shanghai_AWS-Summit" target="_blank">AWS Summit Shanghai</a> - Shanghai - Jun 23, 2026
* <a href="https://clickhouse.com/company/events/ch-syd-meetup-24jun26" target="_blank">Agentic AI Unplugged: Running AI Agents at Scale</a> - Sydney - Jun 24, 2026
* <a href="https://aws.amazon.com/jp/events/summits/japan/" target="_blank">AWS Summit Japan</a> - Tokyo - Jun 25-26, 2026
* <a href="https://cloudonair.witney-2026" target="_blank">Google Cloud Summit Sydney</a> - Sydney - Jun 25, 2026
* <a href="https://clickhoueetup-26jun26" target="_blank">ClickHouse KL Meetup - June 2026</a> - Kuala Lumpur - Jun 26, 2026
* <a href="https://clickhouse.com/company/eur-KCD" target="_blank">KCD Kuala Lumpur</a> - Kuala Lumpur - Jun 27, 2026
* <a href="https://clickel-meetup-30jun26" target="_blank">ClickHouse + Confluent Seoul Meetup</a> - Seoul - Jun 30, 2026
* <a href="https://clickhouse.com/company/events/ch-bom-meetup-04jul26" target="_blank">Lakes to Queries: Building High-Performance Data Platforms</a> - Mumbai - Jul 4, 2026
* <a href="https://cloudonair.withgoogle.com/events/googlecloudday-taipei-2026" target="_blank">Google Cloud Day Taipei</a> - July 9, 2026
* <a href="https://clickhouse.com/company/events/ch-blr-meetup-11jul26" target="_blank">Pipes, Streams, and Queries: Engineering Fast Data at Scale</a> - Bangalore - Jul 11, 2026
* <a href="https://clickhouse.com/company/events/ch-mel-meetup-16jul26" target="_blank">ClickHouse Melbourne Meetup - July 2026</a> - Melbourne - Jul 16, 2026
* <a href="https://clickhouse.com/clickathon/india2026" target="_blank">Click-a-Thon India</a> - Bangalore - August 1-2, 2026
* <a href="https://clickhouse.com/openhouse/sydney-2026" target="_blank">Open House Roadshow - Sydney</a> - Aug 11, 2026
* <a href="https://clickhouse.com/openhouse/melbourne-2026" target="_blank">Open House Roadshow - Melbourne</a> - Aug 13, 2026
