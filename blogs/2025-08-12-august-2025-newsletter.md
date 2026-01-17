---
title: "August 2025 newsletter"
date: "2025-08-12T16:13:31.679Z"
author: "Mark Needham"
category: "Community"
excerpt: "Welcome to the August 2025 ClickHouse newsletter, which will round up what’s happened in real-time data warehouses over the last month."
---

# August 2025 newsletter


Hello, and welcome to the August 2025 ClickHouse newsletter!

This month, we have lightweight updates introduced in ClickHouse 25.7, LLM observability for LibreChat with ClickStack, a Gemini vs Claude SQL bake-off, and more!

## Featured community member: Gene Makarov  {#featured-community-member}

This month's featured community member is Gene Makarov, CTO at SWOT Mobility.

![0_august.png](https://clickhouse.com/uploads/0_august_d79f4f633d.png)

As CTO of SWAT Mobility, he leads data science teams creating algorithms for demand-responsive public transit systems, dealing with real-time GPS data processing, traffic analysis, and logistics optimization for millions of commuters.

Gene is a long-time user of ClickHouse, picking it up for the first time almost a decade ago, just after it became open-source! Recently, he tackled an interesting challenge: <a href="https://www.linkedin.com/posts/gene-makarov-18aa9511_clickhouse-is-quite-powerful-database-which-activity-7334866878877548544-bANc?utm_source=share&utm_medium=member_desktop&rcm=ACoAAACI6V4B_x0ZnBa8U3AkVEmxmQ7-T2kWckI" target="_blank">rendering vector tiles directly from ClickHouse for mapping engines like MapboxGL and MapLibre</a>.

Building on Alexey Milovidov's bitmap tile example, Gene created an elegant solution using an intermediate Golang server to generate MVT format tiles. His weekend experiment demonstrates how ClickHouse can efficiently serve hundreds of millions of geospatial points for real-time mapping applications.

➡️ <a href="https://www.linkedin.com/in/gene-makarov-18aa9511/" target="_blank">Follow Gene on LinkedIn</a>

## Upcoming events {#upcoming-events}

### Global events

* <a href="https://clickhouse.com/company/events/v25-8-community-release-call" target="_blank">v25.8 Community Call</a> - August 28

### Virtual training

* <a href="https://clickhouse.com/company/events/202509-emea-clickstack-deep-dive-part1" target="_blank">Observability at Scale with ClickStack (Virtual)</a> - August 27
* <a href="https://clickhouse.com/company/events/202508-apj-query-optimization" target="_blank">ClickHouse Query Optimization (Virtual)</a> - August 27
* <a href="https://clickhouse.com/company/events/202509-amer-clickhouse-deep-dive-part1" target="_blank">ClickHouse Deep Dive Part 1</a> - September 3
* <a href="https://clickhouse.com/company/events/202509-emea-query-optimization" target="_blank">ClickHouse Query Optimization Workshop</a> - September 11
* <a href="https://clickhouse.com/company/events/202509-emea-clickhouse-deep-dive-part1" target="_blank">ClickHouse Deep Dive Part 1</a> - September 24

### Events in AMER

* <a href="https://clickhouse.com/company/events/202509-amer-SF-meetup" target="_blank">San Francisco ClickHouse Meetup</a> - August 26
* <a href="https://clickhouse.com/company/events/20250827-in-person-SanFrancisco-Observability-at-Scale-ClickStack" target="_blank">Menlo Park In-Person Training - Observability at Scale with ClickStack: Logs, Metrics, Traces and RUM on ClickHouse</a> - August 27
* <a href="https://clickhouse.com/company/events/20250828-in-person-SanFrancisco-Observability-at-Scale-ClickStack" target="_blank">San Francisco In-Person Training - Observability at Scale with ClickStack: Logs, Metrics, Traces and RUM on ClickHouse</a> - August 28
* <a href="https://clickhouse.com/company/events/202509-namer-tor-meetup" target="_blank">Toronto ClickHouse Meetup</a> - September 3
* <a href="https://clickhouse.com/company/events/202509-amer-ra-meetup" target="_blank">Raleigh ClickHouse Meetup</a> - September 4
* <a href="https://clickhouse.com/company/events/2025-09-Amer-AWSSummit-Toronto" target="_blank">AWS Summit Toronto</a> - September 4
* <a href="https://clickhouse.com/company/events/202509-in-person-clickhouse-deep-dive" target="_blank">ClickHouse Deep Dive Training - Toronto</a> - September 5
* <a href="https://clickhouse.com/company/events/202509-amer-NY-meetup" target="_blank">New York ClickHouse + Docker Meetup</a> - September 8
* <a href="https://clickhouse.com/company/events/2025-09-Amer-AWSSummit-LosAngeles" target="_blank">AWS Summit Los Angeles</a> - September 17
* <a href="https://clickhouse.com/company/events/202510-nyc-clickhouse-deep-dive-part1" target="_blank">ClickHouse Deep Dive Part 1 - In-Person Training (New York)</a> - 7 October

### Events in EMEA

* <a href="https://techbbq.dk/" target="_blank">Tech BBQ Copenhagen</a> - August 27-28
* <a href="https://clickhouse.com/company/events/202509-EMEA-TelAviv-meetup" target="_blank">ClickHouse Meetup in Tel Aviv</a> - September 9
* <a href="https://aws.amazon.com/events/summits/zurich/" target="_blank">AWS Summit Zurich</a> - September 11
* <a href="https://www.haya-data.com/" target="_blank">HayaData Tel Aviv</a>, September 16
* <a href="https://clickhouse.com/company/events/202509-EMEA-Dubai-meetup" target="_blank">ClickHouse Meetup in Dubai</a> - September 16
* <a href="https://clickhouse.com/company/events/202509-EMEA-Dubai-RoundTable" target="_blank">Roundtable: "Real-Time Data & AI: Best Practices with AWS & ClickHouse"</a> - September 17
* <a href="https://www.bigdataldn.com/" target="_blank">BigData London</a> - September 24-25
* <a href="https://amsterdam.pydata.org/" target="_blank">PyData Amsterdam</a> - September 24-25
* <a href="https://aws.amazon.com/events/cloud-days/" target="_blank">AWS Cloud Day Riyadh</a>, September 29
* <a href="https://clickhouse.com/company/events/202509-EMEA-Madrid-meetup" target="_blank">ClickHouse Meetup in Madrid</a> - September 30
* <a href="https://clickhouse.com/company/events/202510-EMEA-Barcelona-meetup" target="_blank">ClickHouse Meetup in Barcelona</a> - October 1
* <a href="https://clickhouse.com/company/events/AI-ClimateTechPanel-Amsterdam" target="_blank">AI in ClimateTech Panel - Amsterdam C-Level Meetup</a> - October 7
* <a href="https://clickhouse.com/company/events/202510-EMEA-Zurich-meetup" target="_blank">ClickHouse Meetup in Zürich</a> - October 9
* <a href="https://clickhouse.com/company/events/202510-EMEA-London-meetup" target="_blank">ClickHouse Meetup in London</a> - October 15
* <a href="https://clickhouse.com/company/events/202510-amsterdam-open-house" target="_blank">Amsterdam User Conference</a> - October 27
* <a href="https://clickhouse.com/company/events/202510-in-person-clickhouse-deep-dive-part-1" target="_blank">ClickHouse Deep Dive Part 1 In-Person Training</a> (Amsterdam) - October 28
* <a href="https://clickhouse.com/company/events/202511-EMEA-Cyprus-meetup" target="_blank">ClickHouse Meetup in Cyprus</a> - November 20

### Events in APAC

* <a href="https://dtcc.it168.com/" target="_blank">Database Technology Conference China</a> - August 21
* <a href="https://clickhouse.com/company/events/202508-APJ-Pune-AWSCommunityDayPune" target="_blank">AWS Community Day Pune</a> - August 23
* <a href="https://clickhouse.com/company/events/202509-apj-Gurgaon-inperson-migration-to-clickhouse" target="_blank">Delhi/Gurgaon Migration to ClickHouse Workshop (in-person)</a> - September 4
* <a href="https://clickhouse.com/company/events/202509-APJ-Sydney-CloudCon" target="_blank">CloudCon Sydney</a> - September 9-10
* <a href="https://vdac.vn/pages/vietnam-11-september-2025" target="_blank">Asia Data Analytics Conference Vietnam</a> - September 11
* <a href="https://communityday.awsugvad.in/" target="_blank">AWS Community Day Vadodara</a> - September 13
* <a href="https://aws.amazon.com/startups/events/aws-startup-dev-day-sydney-2025" target="_blank">AWS Startup Dev Day Sydney</a> - September 18
* <a href="https://forefrontevents.co/event/data-ai-summit-singapore-2025/" target="_blank">Data & AI Summit Singapore</a> - September 24
* <a href="https://clickhouse.com/openhouse/sydney" target="_blank">Sydney Open House User Conference</a> - October 2
* <a href="https://clickhouse.com/openhouse/bangalore" target="_blank">Bangalore Open House User Conference</a> - October 7

## 25.7 release  {#release}

![1_august.png](https://clickhouse.com/uploads/1_august_2dc99aa221.png)

In ClickHouse 25.7, we've delivered lightweight SQL UPDATE and DELETE operations that are up to 1,000× times faster thanks to Anton Popov's new patch-part mechanism.

We've also added <a href="https://clickhouse.com/docs/use-cases/AI/ai-powered-sql-generation" target="_blank">AI-powered SQL generatio</a>n from Kaushik Iska (just type `??` and ask your question in plain English!), Amos Bird's clever optimization that makes `count()` aggregations 20-30% faster by skipping memory allocation, and Nikita Taranov's continued JOIN improvements delivering up to 1.8× speedups.

➡️ <a href="https://clickhouse.com/blog/clickhouse-release-25-07" target="_blank">Read the release post</a>

## Using Gemini and Claude For SQL Analytics - A Bake Off {#using-gemini-and-claude-for-sql-analytics-a-bake-off}

![2_august.png](https://clickhouse.com/uploads/2_august_2088af27a6.png)

Benjamin Wootton benchmarked Claude Opus and Gemini 2.5 Pro for SQL analytics with ClickHouse, using Danny's Diner SQL. Both LLMs achieved near-perfect accuracy, generating complex SQL queries from plain English prompts via the <a href="https://clickhouse.com/docs/use-cases/AI/MCP" target="_blank">MCP (Model Context Protocol)</a> standard. You'll have to read the blog to find out which model solved the questions more quickly!

➡️ <a href="https://benjaminwootton.com/insights/clickhouse-gemini-claude" target="_blank">Read the blog post</a>

## How we built fast UPDATEs for the ClickHouse column store {#how-we-built-fast-updates-for-the-clickhouse-column-store}

![3_august.png](https://clickhouse.com/uploads/3_august_0e430e119d.png)


In the first part of Tom Schreiber’s deep dive into ClickHouse updates, he explains how ClickHouse solves the performance challenges of row-level updates by treating updates as inserts through purpose-built engines like ReplacingMergeTree, CoalescingMergeTree, and CollapsingMergeTree that leverage ClickHouse's insert throughput and background merge process.

➡️ <a href="https://clickhouse.com/blog/updates-in-clickhouse-1-purpose-built-engines" target="_blank">Read the blog post</a>

## Querying ~86 Million rows/s for high-performance dashboard analytics {#querying-86-million-rows-s-for-high-performance-dashboard-analytics}

![4_august.png](https://clickhouse.com/uploads/4_august_cf0cf3f366.png)

Edouard Kombo shares how he abandoned his initial Python + PostgreSQL stack when faced with 4-second query times on just 50 million rows, discovering that ClickHouse's columnar storage and vectorized execution could scan 400 million rows at ~86 million rows per second - making sub-second analytics on billions of rows achievable.

➡️ <a href="https://edouard-kombo.medium.com/querying-billions-of-data-in-seconds-with-go-clickhouse-svelte-5157e9cb5232" target="_blank">Read the blog post</a>

## LLM observability with ClickStack, OpenTelemetry, and MCP {#llm-observability-with-clickstack-opentelemetry-and-mcp}

![5_august.png](https://clickhouse.com/uploads/5_august_71915d3759.png)

Dale McDiarmid and Lionel Palacin demonstrate how to build comprehensive LLM observability using ClickStack, our open-source observability stack, to instrument LibreChat - an AI chat platform with MCP support.

➡️ <a href="https://clickhouse.com/blog/llm-observability-clickstack-mcp" target="_blank">Read the blog post</a>

## Quick reads {#quick-reads}

* Mohamed Hussain S explores <a href="https://dev.to/mohhddhassan/from-python-to-clickhouse-parquet-etl-with-go-lm1" target="_blank">generating a Parquet file using Python and loading it into ClickHouse using Go</a>.
* Mohamed Hussain S also <a href="https://medium.com/@mohhddhassan/my-first-clickhouse-query-mistakes-and-what-they-taught-me-acd7fbee4773" target="_blank">shares some lessons he learnt about writing better ClickHouse queries</a>.
* Divyanshu Raj <a href="https://www.glassflow.dev/blog/aggregatingmergetree-clickhouse" target="_blank">explores the AggregatingMergeTree table engine</a>, explains how it works, where it shines, and how it compares with other engines like ReplacingMergeTree.
* Bayu Setiawan builds a <a href="https://clickhouse.com/blog/building-a-medallion-architecture-with-clickhouse" target="_blank">medallion architecture</a> <a href="https://towardsdev.com/building-a-scalable-real-time-etl-pipeline-with-kafka-debezium-flink-airflow-minio-and-b5a85ae28a02" target="_blank">using Kafka, Debezium, Flink, Airflow, ClickHouse, and MinIO</a>.
* Alireza Mousavizade explains how to build a <a href="https://medium.com/@alireza.mousavizade/real-time-user-behavior-analytics-at-scale-with-kafka-and-clickhouse-cf3107a30728" target="_blank">real-time session analytics pipeline</a> designed for high-throughput, resilience, and superior query performance, capable of transforming raw event streams into interactive, live dashboards.
