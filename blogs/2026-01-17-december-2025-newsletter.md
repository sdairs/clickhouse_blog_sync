---
title: "December 2025 newsletter"
date: "2025-12-18T09:31:00.768Z"
author: "Mark Needham"
category: "Community"
excerpt: "Welcome to the December 2025 ClickHouse newsletter, which will round up what’s happened in real-time data warehouses over the last month."
---

# December 2025 newsletter

Hello, and welcome to the December 2025 ClickHouse newsletter!

This month, we have a Postgres extension for querying ClickHouse, an analysis of how the five major cloud data warehouses compare in terms of cost-performance, a review of the year in Postgres CDC, and more!

## Featured community member: Zjan Carlo Turla {#featured-community-member}

This month's featured community member is Zjan Carlo Turla, Software Engineer at Canva.

![dec2025_image3.png](https://clickhouse.com/uploads/dec2025_image3_5c148fc70e.png)

Zjan works on Canva's Observability team, where he builds and maintains systems that monitor and ensure reliability across Canva's distributed infrastructure. Previously, he worked as a DevOps Consultant supporting large-scale platforms and spent several years at Kalibrr as an SRE, migrating monolithic applications to microservices on Kubernetes.

At the recent <a href="https://clickhouse.com/openhouse/sydney" target="_blank">Open House roadshow in Sydney</a>, he shared <a href="https://clickhouse.com/blog/canva-faster-search-lower-costs" target="_blank">how Canva migrated production observability workloads in ClickHouse</a>, processing 3 million spans and 3 million logs per second for 240 million monthly active users, achieving 10x faster search and 70% cost savings.

➡️ <a href="https://www.linkedin.com/in/zjan-carlo-turla-358b28164/" target="_blank">Connect with Zjan</a>

## Upcoming events {#upcoming-events}

### Global virtual events

* <a href="https://clickhouse.com/company/events/v25-12-community-release-call" target="_blank">v25.12 Community Call</a> - December 18

### Virtual training

* <a href="https://clickhouse.com/company/events/202512-amer-clickhouse-certified-developer-exam" target="_blank">Preparing for the ClickHouse Certified Developer Exam</a> - December 18

**Real-time Analytics**

* <a href="https://clickhouse.com/company/events/202601-EMEA-Real-time-Analytics-with-ClickHouse-Level1" target="_blank">Real-time Analytics with ClickHouse: Level 1</a> - January 14
* <a href="https://clickhouse.com/company/events/202601-EMEA-Real-time-Analytics-with-ClickHouse-Level2" target="_blank">Real-time Analytics with ClickHouse: Level 2</a> - January 21
* <a href="https://clickhouse.com/company/events/202601-EMEA-Real-time-Analytics-with-ClickHouse-Level3" target="_blank">Real-time Analytics with ClickHouse: Level 3</a> - January 28

**Observability**

* <a href="https://clickhouse.com/company/events/202512-AMER-Observability-with-ClickStack" target="_blank">Observability with ClickStack: Level 2</a> - December 17
* <a href="https://clickhouse.com/company/events/202602-AMER-Observability-with-ClickStack-Level1" target="_blank">Observability with ClickStack: Level 1</a> - February 4

### Events in AMER

* <a href="https://luma.com/abggijbh" target="_blank">Iceberg Meetup in Menlo Park</a> - January 21st
* <a href="https://luma.com/ifxnj82q" target="_blank">Iceberg Meetup in NYC</a> - January 23rd
* <a href="https://luma.com/iicnlq41" target="_blank">New York Meetup</a> - January 26th

### Events in EMEA

* <a href="https://clickhouse.com/company/events/202512-EMEA-TelAviv-meetup" target="_blank">ClickHouse Meetup in Tel Aviv</a> - December 29
* <a href="https://luma.com/3szhmv9h" target="_blank">Data & AI Paris Meetup</a> - January 22nd
* <a href="https://luma.com/yx3lhqu9" target="_blank">Apache Iceberg™ Meetup Belgium: FOSDEM Edition</a> - January 30th

### Events in APAC

* <a href="https://clickhouse.com/company/events/202601-APJ-Webinar-Materialized-Views" target="_blank">Under-the-Hood: Incremental Materialized Views & Dictionaries Webinar</a> - January 15

## Our gift to you: Free ClickHouse certification and new learning paths {#gift}

We've launched all-new self-paced learning paths designed to deliver the hands-on experience needed to build real-world skills and expertise to match your goals. Explore our new paths today:

* <a href="https://clickhouse.com/learn/real-time-analytics" target="_blank">Real-time Analytics with ClickHouse</a> - Learn how to power real-time dashboards, alerts, and event-driven apps with ClickHouse.
* <a href="https://clickhouse.com/learn/observability" target="_blank">Observability with ClickStack</a> - Ingest logs, metrics, and traces to monitor systems and power observability dashboards.
* <a href="https://learn.clickhouse.com/class_catalog/category/141050" target="_blank">Machine Learning and GenAI with ClickHouse</a> - Use ClickHouse to prepare data, feed models, and support GenAI workflows at scale.
* Data Warehousing with ClickHouse - Coming Soon! Design, build, and optimize modern data warehouses using ClickHouse.

As our holiday gift, get certified for free through the end of 2025. Use code **2025CERTFREE** at checkout to claim your certification at no cost.

➡️ <a href="https://clickhouse.com/learn" target="_blank">Start learning</a>

## 25.11 release {#release}

![dec2025_image9.png](https://clickhouse.com/uploads/dec2025_image9_d03fe17462.png)

My favourite feature in our penultimate release of the year, 25.11, is projections as secondary indices, which lets you create lightweight projections that behave like a secondary index without duplicating complete rows of data.

This release also features faster GROUP BY operations on 8-bit and 16-bit integer keys, as well as the argAndMin and argAndMax functions, fractional LIMIT and OFFSET, and more.

➡️ <a href="https://clickhouse.com/blog/clickhouse-release-25-11" target="_blank">Read the release post</a>

## Introducing pg_clickhouse: A Postgres extension for querying ClickHouse {#pg_clickhouse}

![dec2025_image8.png](https://clickhouse.com/uploads/dec2025_image8_030a51e094.png)

David Wheeler announced the release of pg_clickhouse, a PostgreSQL extension that brings ClickHouse's analytical power directly into your Postgres queries through foreign data wrappers.

Query ClickHouse tables from Postgres with intelligent pushdown optimization that executes aggregations and filters in ClickHouse for maximum performance, giving you access to massive analytical datasets without leaving your Postgres environment.

➡️ <a href="https://clickhouse.com/blog/introducing-pg_clickhouse" target="_blank">Read the announcement</a>

## Dlt+ClickHouse+Rill: Multi-Cloud Cost Analytics, Cloud-Ready {#dlt_clickhouse_rill}

![dec2025_image6.png](https://clickhouse.com/uploads/dec2025_image6_919ef77e95.png)

Simon Späti demonstrates how to build a real-time FinOps dashboard using dlt to ingest AWS cost and usage reports into ClickHouse, and then visualizes the data with Rill.

The setup provides a practical blueprint for instant cost analysis at scale, with ClickHouse serving as the analytical engine to handle millions of cost records.

➡️ <a href="https://www.ssp.sh/blog/finops-dlt-clickhouse-rill/" target="_blank">Read the blog post</a>

## Postgres CDC in ClickHouse, A year in review {#postgres_cdc_clickhouse}

![dec2025_image2.png](https://clickhouse.com/uploads/dec2025_image2_b6a73bb304.png)

Sai Srirampur reflects on a year of building Postgres CDC in ClickHouse Cloud, growing from a handful of PeerDB users to over 400 companies replicating more than 200 TB of data monthly.

The post highlights technical wins, such as eliminating expensive replication reconnects that caused hours of lag and reducing partition generation from over 7 hours to under a second, while outlining next steps to close data modeling gaps and further scale logical replication.

➡️ <a href="https://clickhouse.com/blog/postgres-cdc-year-in-review-2025" target="_blank">Read the blog post</a>

## ClickHouse as a security engine: Tempesta FW's approach to L7 DDoS and bot mitigation {#clickhouse_security_engine}

![dec2025_image4.jpg](https://clickhouse.com/uploads/dec2025_image4_f0455307df.jpg)

Tempesta Technologies developed WebShield, an open-source bot detection system that utilizes ClickHouse to analyze access logs in real-time and automatically block Layer 7 DDoS attacks and malicious bots.

➡️ <a href="https://tempesta-tech.com/blog/defending-against-l7-ddos-and-web-bots-with-tempesta-fw/" target="_blank">Read the blog post</a>

## How the five major cloud data warehouses compare on cost-performance {#cloud_data_warehouses_cost_performance}

![dec2025_image1.png](https://clickhouse.com/uploads/dec2025_image1_a877836355.png)

Did you know that public price lists of cloud data warehouses don't tell you real costs? Much more important is the amount of computing power the underlying engine consumes to run your queries.

Tom Schreiber & Lionel Palacin break down <a href="https://clickhouse.com/blog/how-cloud-data-warehouses-bill-you" target="_blank">how Snowflake, BigQuery, Databricks, and Redshift bill you</a>, then benchmark their actual cost-performance against ClickHouse.

➡️ <a href="https://clickhouse.com/blog/cloud-data-warehouses-cost-performance-comparison" target="_blank">Read the blog post</a>

## clickhouse.build: An agentic CLI to accelerate Postgres apps with ClickHouse {#clickhouse_build}

![dec2025_image7.png](https://clickhouse.com/uploads/dec2025_image7_7e52ce635d.png)

A Postgres + ClickHouse proof of concept in an hour? It sounds too good to be true, but clickhouse.build does precisely that.

Our new open-source CLI uses agents to scan your TypeScript code, identify analytical queries, configure ClickPipes CDC, and rewrite your app to use both databases - with a feature flag to toggle between backends and measure the impact.

➡️ <a href="https://clickhouse.com/blog/clickhouse-build-agentic-cli-accelerate-postgres-clickhouse-apps" target="_blank">Read the blog post</a>

## Quick reads {#quick-reads}

* Ahmet Kürşat Şerolar <a href="https://medium.com/logalarm-devs/clickhouse-fine-tuning-maximize-performance-for-time-series-and-logs-5b6f6943ca7c" target="_blank">shares a deep-dive on optimizing ClickHouse</a> for logs and time-series data, covering engine selection, partitioning, LowCardinality fields, codecs (DoubleDelta + ZSTD), materialized views, and TTL-based storage tiers.
* Vignesh T K <a href="https://www.mafiree.com/readBlog/speeding-up-clickhouse-queries-materialized-views-vs-refreshable-views-explained" target="_blank">explains the difference</a> between ClickHouse's Materialized Views (real-time updates on insert, best for streaming data) and Refreshable Materialized Views (scheduled periodic updates, better for complex joins and batch analytics).
* Georgii Baturin walks through <a href="https://medium.com/hands-on-dbt-with-clickhouse/hands-on-dbt-with-clickhouse-1-local-sandbox-and-safe-training-data-64f897be6843" target="_blank">setting up a local dbt analytics environment with ClickHouse</a>, covering Docker setup, creating separate training databases for raw data and dbt models, connecting dbt-core with the ClickHouse adapter, and configuring Git - providing a practical sandbox for learning dbt without touching production systems.
* Thinh Dang provides <a href="https://thinhdanggroup.github.io/tables-distributed-clickhouse-cluster/" target="_blank">a comprehensive guide to creating tables in distributed ClickHouse clusters</a>, covering local vs Distributed tables, ReplicatedMergeTree with Keeper coordination, ON CLUSTER DDL, sharding keys, internal_replication settings, and operational patterns like materialized views for aggregations - plus a practical checklist to avoid schema inconsistencies and replication headaches.
* Paul Bardea explains <a href="https://www.blacksmith.sh/blog/logging" target="_blank">how Blacksmith built a logging platform for GitHub Actions with ClickHouse</a>.

