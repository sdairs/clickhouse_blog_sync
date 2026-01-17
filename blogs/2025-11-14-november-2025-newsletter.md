---
title: "November 2025 newsletter"
date: "2025-11-14T10:52:49.320Z"
author: "Mark Needham"
category: "Community"
excerpt: "Welcome to the November 2025 ClickHouse newsletter, which will round up what’s happened in real-time data warehouses over the last month."
---

# November 2025 newsletter

Hello, and welcome to the November 2025 ClickHouse newsletter!

This month, we have big news with our LibreChat acquisition, a data analyst's AI-powered warehouse build, 170x log compression techniques, and auto-exporting traces to OpenTelemetry.

## Featured community member: Kiyose Ryu  {#featured-community-member}

This month's featured community member is Kiyose Ryu, Engineering Manager at Smartnews, Inc.

![nov2025_image1.png](https://clickhouse.com/uploads/nov2025_image1_44b9d11f45.png)

Kiyose Ryu has worked at Smartnews for the past five years, where he's helped build a real-time aggregation system using ClickHouse.

Smartnews began introducing ClickHouse in 2020, and by 2021, had converted all advertiser reports to real-time. Advertisers need up-to-the-minute data to manage their campaigns effectively, which is why Smartnews prioritized delivering accurate, real-time reports. Kiyose Ryu <a href="https://clickhouse.com/videos/tokyo-meetup-smartnews-15apr25" target="_blank">shared the details of their implementation at the ClickHouse Tokyo meetup</a>.

➡️ <a href="https://about.smartnews.com/ja/" target="_blank">Learn more about Smartnews</a>

## Upcoming events {#upcoming-events}

### Global virtual events

* <a href="https://clickhouse.com/company/events/webinar-f45-fiveonefour-clickhouse" target="_blank">How F45 Turns 1B+ Data Points into 70% Higher Member Satisfaction</a> - November 20
* <a href="https://clickhouse.com/company/events/v25-11-community-release-call" target="_blank">v25.11 Community Call</a> - November 25

### Virtual training

**Real-time Analytics**

* <a href="https://clickhouse.com/company/events/202511-AMER-Real-time-Analytics-with-ClickHouse-Level1" target="_blank">Real-time Analytics with ClickHouse: Level 1</a> - November 19
* <a href="https://clickhouse.com/company/events/202511-APJ-Real-time-Analytics-with-ClickHouse-Level1" target="_blank">Real-time Analytics with ClickHouse: Level 1</a> (APJ-friendly) - November 25
* <a href="https://clickhouse.com/company/events/202511-APJ-Real-time-Analytics-with-ClickHouse-Level2" target="_blank">Real-time Analytics with ClickHouse: Level 2</a> (APJ-friendly) - November 26
* <a href="https://clickhouse.com/company/events/202511-APJ-Real-time-Analytics-with-ClickHouse-Level3" target="_blank">Real-time Analytics with ClickHouse: Level 3</a> (APJ-friendly) - November 27
* <a href="https://clickhouse.com/company/events/202512-AMER-Real-time-Analytics-with-ClickHouse-Level1" target="_blank">Real-time Analytics with ClickHouse: Level 1</a> - December 2
* <a href="https://clickhouse.com/company/events/202512-AMER-Real-time-Analytics-with-ClickHouse-Level2" target="_blank">Real-time Analytics with ClickHouse: Level 2</a> - December 3
* <a href="https://clickhouse.com/company/events/202512-AMER-Real-time-Analytics-with-ClickHouse-Level3" target="_blank">Real-time Analytics with ClickHouse: Level 3</a> - December 4
* <a href="https://clickhouse.com/company/events/202512-AMER-Real-time-Analytics-with-ClickHouse-Level1" target="_blank">Real-time Analytics with ClickHouse: Level 1</a> - December 9
* <a href="https://clickhouse.com/company/events/202512-AMER-Real-time-Analytics-with-ClickHouse-Level2" target="_blank">Real-time Analytics with ClickHouse: Level 2</a> - December 10
* <a href="https://clickhouse.com/company/events/202512-AMER-Real-time-Analytics-with-ClickHouse-Level3" target="_blank">Real-time Analytics with ClickHouse: Level 3</a> - December 11

**Observability**

* <a href="https://clickhouse.com/company/events/202511-EMEA-Observability-at-Scale-with-ClickStack" target="_blank">Observability at Scale with ClickStack</a> - November 26
* <a href="https://clickhouse.com/company/events/202512-AMER-Observability-at-Scale-with-ClickStack" target="_blank">Observability at Scale with ClickStack</a> - December 3
* <a href="https://clickhouse.com/company/events/202512-AMER-Observability-with-ClickStack" target="_blank">Observability with ClickStack: Level 2</a> - December 17

### Events in AMER

* <a href="https://clickhouse.com/houseparty/the-sql" target="_blank">House Party, The SQL</a>, Las Vegas - December 3

### Events in EMEA

* <a href="https://www.forward-data-conference.com/en" target="_blank">ForwardData Paris (Data&AI)</a> - November 24
* <a href="https://www.be4data.com/" target="_blank">Paris Monitoring Day</a> - November 25
* <a href="https://www.meetup.com/clickhouse-poland-user-group/events/311309076/?eventOrigin=network_page" target="_blank">ClickHouse Meetup Warsaw</a> - November 26
* <a href="https://clickhouse.com/company/events/202512-EMEA-TelAviv-meetup" target="_blank">ClickHouse Meetup in Tel Aviv</a> - December 29

### Events in APAC

* <a href="https://clickhouse.com/company/events/202511-in-person-Mumbai-Real-time-Analytics-with-ClickHouse-Level1" target="_blank">Mumbai In-Person Training - Real-time Analytics with ClickHouse: Level 1</a> - November 21
* <a href="https://www.meetup.com/clickhouse-thailand-meetup-group/events/311852739/" target="_blank">ClickHouse + AWS Bangkok Meetup</a> - November 25
* <a href="https://clickhouse.com/company/events/2025-12-APJ-Tokyo-OpenSourceSummitJapan" target="_blank">Open Source Summit Japan</a> - December 8
* <a href="https://clickhouse.com/company/events/202512-in-person-Jakarta-Real-time-Analytics-with-ClickHouse-Level1" target="_blank">Jakarta In-Person Training - Real-time Analytics with ClickHouse: Level 1</a> - December 9
* <a href="https://www.meetup.com/clickhouse-indonesia-user-group/events/311988089/" target="_blank">ClickHouse Jakarta Meetup</a> - December 9
* <a href="https://www.meetup.com/clickhouse-tokyo-user-group/events/311974739/" target="_blank">ClickHouse Tokyo Meetup & Year-End Party</a> - December 15
* <a href="https://clickhouse.com/company/events/2025-12-APJ-Tokyo-AIEngineeringSummitJapan" target="_blank">AI Engineering Summit Tokyo</a> - December 16

## 25.10 release {#release}

![nov2025_image2.png](https://clickhouse.com/uploads/nov2025_image2_d724343f36.png)

ClickHouse 25.10 sees a collection of JOIN performance optimizations. These include lazy column replication, bloom filter optimizations, and smarter push-down of complex conditions, delivering up to 24 times faster queries in some cases.

There are also several additions to the SQL syntax, including the `<=>` (IS NOT DISTINCT FROM) operator, negative limit and offset (perfect for getting the n most recent records but returning them in ascending order), and `LIMIT BY ALL`.

And finally, my personal favorite - as of ClickHouse 25.10, we can query the ClickHouse Arrow Flight server using the ClickHouse Arrow Flight client.

➡️ <a href="https://clickhouse.com/blog/clickhouse-release-25-10" target="_blank">Read the release post</a>

## ClickHouse welcomes LibreChat: Introducing the open-source Agentic Data Stack {#librechat}

![nov2025_image3.png](https://clickhouse.com/uploads/nov2025_image3_cdd181698e.png)

We acquired LibreChat, the leading open-source AI chat platform, to create the "Agentic Data Stack" - combining LibreChat's multi-LLM interface with ClickHouse's analytical speed so users can query data in plain English.

Companies like Shopify, Daimler Truck, and cBioPortal are already using this stack to democratize data access, and <a href="https://clickhouse.com/blog/ai-first-data-warehouse" target="_blank">our own AI-powered data warehouse</a> now handles 70% of queries for 200+ users.

LibreChat remains 100% open-source under its MIT license, and we plan to implement deeper native integrations while preserving the platform's flexibility.

➡️ <a href="https://clickhouse.com/blog/librechat-open-source-agentic-data-stack" target="_blank">Read the announcement</a>

## Streaming asynchronous inserts monitoring in ClickHouse {#streaming-asynchronous-inserts-monitoring-in-clickhouse}

![nov2025_image4.png](https://clickhouse.com/uploads/nov2025_image4_bcbf17b7d3.png)

AB Tasty's William Attache explains how his team built a comprehensive monitoring system to track ClickHouse asynchronous inserts end-to-end, from initial requests through flush queries to final part merges. The team created a custom view that joins data from multiple system tables to visualize the complete lifecycle of streaming inserts.

Along the way, they achieved significant cost savings by switching from JSON to RowBinary format and optimizing their batch sizes based on how ClickHouse actually creates and merges parts.

➡️ <a href="https://medium.com/the-ab-tasty-tech-blog/streaming-asynchronous-inserts-monitoring-in-clickhouse-c1378bd8b159" target="_blank">Read the blog post</a>

## We built a vector search engine that lets you choose precision at query time {#we-built-a-vector-search-engine-that-lets-you-choose-precision-at-query-time}

![nov2025_image5.png](https://clickhouse.com/uploads/nov2025_image5_178fcf89ba.png)

Raufs Dunamalijevs added QBit to ClickHouse, a column type that stores floats as bit planes. It allows you to choose how many bits to read during vector search, thereby tuning recall and performance without altering the data.

➡️ <a href="https://clickhouse.com/blog/qbit-vector-search" target="_blank">Read the blog post</a>

## From 0–1: Building our data warehouse with ClickHouse to enable self-serve analytics and observability at scale {#from-0-1-building-our-data-warehouse-with-clickhouse-to-enable-self-serve-analytics-and-observability-at-scale}

![nov2025_image6.png](https://clickhouse.com/uploads/nov2025_image6_ea0a2450fb.png)

Viralo hit 10M users, and their PostgreSQL analytics setup collapsed, with dashboards taking over 30 minutes to load, CPUs maxing out at over 80%, and queries failing. They migrated to ClickHouse Cloud and implemented a <a href="https://clickhouse.com/blog/building-a-medallion-architecture-with-clickhouse" target="_blank">medallion architecture</a>, using SQL for all data transformations instead of external ETL tools, which reduced query time to under 30 seconds.

Notably, Shubham Bhardwaj's team constructed the entire warehouse using a low-code approach, leveraging Claude Sonnet for code assistance, thereby eliminating orchestration tool costs and demonstrating that innovative architecture and AI tooling can effectively replace complex data stacks.

➡️ <a href="https://medium.com/@shubhamb957/from-0-1-building-our-data-warehouse-with-clickhouse-to-enable-self-serve-analytics-and-f5fbe2cd7e3a" target="_blank">Read the blog post</a>

## Tracing the invisible: Building end-to-end observability in a real-time streaming pipeline {#tracing-the-invisible-building-end-to-end-observability-in-a-real-time-streaming-pipeline}

![nov2025_image7.png](https://clickhouse.com/uploads/nov2025_image7_919adb86b2.png)

When building end-to-end observability for their real-time metrics pipeline, Pranav Mehta's team faced a unique challenge: ClickHouse stores query spans internally, but it cannot use an SDK to push those traces to an OpenTelemetry collector, as is done with application services.

They came up with a clever idea of using an incremental materialized view that writes to a table backed by the URL engine, which points at the OTel collector API.

Now they can trace a request all the way from the application, through NATS JetStream, into ClickHouse query execution - and see it all in one view.

➡️ <a href="https://medium.com/@pranavmehta94/tracing-the-invisible-building-end-to-end-observability-in-a-real-time-streaming-pipeline-eccc91524e24" target="_blank">Read the blog post</a>

## ClickHouse partners with Japan Cloud to establish ClickHouse K.K. and accelerate growth in Japan {#clickhouse-partners-with-japan-cloud-to-establish-clickhouse-k-k-and-accelerate-growth-in-japan}

![nov2025_image8.png](https://clickhouse.com/uploads/nov2025_image8_c644ce69a0.png)

Earlier this month, ClickHouse announced the establishment of ClickHouse K.K., its Japanese subsidiary, through a strategic partnership with Japan Cloud.

➡️ <a href="https://clickhouse.com/blog/japan-cloud" target="_blank">Read the blog post</a>

## Quick reads {#quick-reads}

* Alexey Milovidov <a href="https://clickhouse.com/blog/planes-weather" target="_blank">derives and visualizes real-time weather data</a> (wind direction, speed, and air pressure) from airplane telemetry stored in ClickHouse using trigonometry and color mapping.
* Nisarg Pipaliy has written <a href="https://medium.com/@nisargpipaliya2402/clickhouse-explained-simply-why-its-different-and-when-to-use-it-9b298406485d" target="_blank">a beginner-friendly explainer that breaks down ClickHouse's table engines</a>, showing how different engines, such as MergeTree, ReplacingMergeTree, and SummingMergeTree, give tables distinct "personalities" for handling deduplication, aggregation, and replication. This makes it clear why ClickHouse is fundamentally different from traditional row-based databases, such as PostgreSQL.
* Julian Virguez <a href="https://medium.com/@julianvirguez/real-time-product-sentiment-wiring-clickhouse-data-into-sf-ui-557812267d29" target="_blank">wired ClickHouse directly into Salesforce</a> using a Lightning Web Component that queries 150M rows of Amazon review data in under a second.
* Lionel Palacin demonstrated <a href="https://clickhouse.com/blog/log-compression-170x" target="_blank">how to achieve 170x+ compression on Nginx logs</a> by transforming raw text into structured columns with optimized data types and strategic ordering keys. He then followed this up with another post showing how to <a href="https://clickhouse.com/blog/improve-compression-log-clustering" target="_blank">automatically group similar log messages and extract variable fields into columns</a>, achieving nearly 50x compression while keeping logs fully queryable and reconstructable.
* Andrii K walks through <a href="https://medium.com/@andriikrymus/streaming-postgresql-data-changes-to-clickhouse-with-debezium-kafka-18dbebb8f29a" target="_blank">setting up a complete CDC pipeline</a> using Debezium to capture PostgreSQL changes, stream them through Kafka with Avro serialization, and sink into ClickHouse.

## Video corner {#video-corner}

* Mark Needham demonstrates the <a href="https://clickhouse.com/videos/mcp-server-chdb" target="_blank">ClickHouse MCP server's new chDB mode</a>, which enables in-process execution of ClickHouse queries without a server.
* At Web Summit 2025, <a href="https://clickhouse.com/videos/web-summit-2025-alexey-milovidov" target="_blank">Alexey Milovidov demonstrated loading massive public datasets into ClickHouse and then running real-time analytics</a>, such as comparing writing styles across domains, tracking trends on Reddit, and creating an interactive map that showed the "best photo" for every location on Earth.
* At <a href="https://clickhouse.com/openhouse/bangalore" target="_blank">OpenHouse Bangalore 2025</a>, Kiran Raparti and Pragnesh Bhavsar from HighLevel explained how they <a href="https://clickhouse.com/videos/open-house-bangalore-highlevel" target="_blank">migrated four critical use cases from MySQL, Elasticsearch, and MongoDB to ClickHouse</a>.
