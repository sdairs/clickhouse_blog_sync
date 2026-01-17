---
title: "April 2025 Newsletter"
date: "2025-04-16T08:29:42.278Z"
author: "Mark Needham"
category: "Community"
excerpt: "Welcome to the April ClickHouse newsletter, which will round up what’s happened in real-time data warehouses over the last month."
---

# April 2025 Newsletter

Hello, and welcome to the April 2025 ClickHouse newsletter!

This month, we bring you CloudQuery's compelling experience report after 6 months with ClickHouse, unveil the powerful new query condition cache in 25.3, reflect on our year of Rust development, announce our strategic acquisition of HyperDX, and more!

## Featured community member: Julian LaNeve {#featured-community-member}

This month's featured community member is Julian LaNeve, CTO at Astronomer.

![0_april.png](https://clickhouse.com/uploads/0_april_f7df5dfe00.png)


Before stepping into the CTO role in November 2023, Julian worked in the product team, focusing on developer experience, data observability, and open-source initiatives. Notably, he led the launch of Astronomer's Cloud IDE - a notebook tool designed for writing data pipelines.

Julian recently wrote a blog post describing why Astronomer chose ClickHouse Cloud to power its new data observability platform, Astro Observe. ClickHouse's ability to handle billions of Airflow workflow events with fast query performance and minimal maintenance requirements made it their database of choice. Julian also presented on the same topic at the <a href="https://clickhouse.com/blog/why-astronomer-chose-clickhouse-to-power-its-new-data-observability-platform-astro-observe" target="_blank">ClickHouse New York November 2024 meetup</a>.

➡️ <a href="https://www.linkedin.com/in/julianlaneve/" target="_blank">Follow Julian on LinkedIn</a>

## Upcoming events {#upcoming-events}

We've started announcing our first speakers with just over a month until <a href="https://clickhouse.com/openhouse?utm_source=marketo&utm_medium=email&utm_campaign=newsletter" target="_blank">Open House, The ClickHouse User Conference</a> in San Francisco on May 29.

Kevin Weil (CPO at OpenAI) and Martin Casado (Partner at Andreessen Horowitz) will join Aaron Katz (CEO at ClickHouse) for a fireside chat about the future of data infrastructure for AI at scale.

Lukas Biewald (Founder and CEO at Weights & Biases) will also join us to discuss the future of AI and the role high-performance databases like ClickHouse play in powering next-gen AI apps.

➡️ <a href="https://clickhouse.com/openhouse?utm_source=marketo&utm_medium=email&utm_campaign=newsletter" target="_blank">Register for Open House</a>

### Global events

* <a href="https://clickhouse.com/company/events/v25-4-community-release-call" target="_blank">v25.4 Community Call</a> - April 22

### Free training

* <a href="https://clickhouse.com/company/events/202504-emea-clickhouse-fundamentals" target="_blank">ClickHouse Fundamentals - Virtual</a> - April 22
* <a href="https://clickhouse.com/company/events/202504-apj-jakarta-inperson-bigquery-to-clickhouse" target="_blank">In-Person BigQuery to ClickHouse - Jakarta</a> - April 22
* <a href="https://clickhouse.com/company/events/202505-amer-clickhouse-observability" target="_blank">Using ClickHouse for Observability</a> - May 7
* <a href="https://clickhouse.com/company/events/clickhouse-fundamentals" target="_blank">ClickHouse Fundamentals - Virtual</a> - May 13
* <a href="https://clickhouse.com/company/events/202505-emea-munich-inperson-developer-fast-track" target="_blank">In-Person ClickHouse Developer Fast Track - Munich</a> - May 14
* <a href="https://clickhouse.com/company/events/202505-amer-clickhouse-developer" target="_blank">ClickHouse Developer Training - Virtual</a> - May 21

### Events in AMER

* <a href="https://www.meetup.com/clickhouse-denver-user-group/events/306934991/" target="_blank">ClickHouse Meetup in Denver</a> - April 23

### Events in EMEA

* <a href="https://clickhouse.com/company/events/04-2025-aws-london" target="_blank">AWS Summit 2025, London</a> - April 30
* <a href="https://clickhouse.com/company/events/202505-EMEA-Poland-AWS-Summit-MeetingRequests" target="_blank">AWS Summit 2025, Poland</a> - May 6
* <a href="https://www.meetup.com/clickhouse-london-user-group/events/306047172/" target="_blank">ClickHouse Meetup in London</a> - May 13
* <a href="https://clickhouse.com/company/events/202505-EMEA-Munich-HappyHour" target="_blank">ClickHouse Happy Hour Munich</a> - May 14
* <a href="https://www.meetup.com/clickhouse-turkiye-meetup-group/events/306978337/" target="_blank">ClickHouse Istanbul Meetup</a> - May 14

### Events in APAC

* <a href="https://www.meetup.com/clickhouse-indonesia-user-group/events/306973747/" target="_blank">ClickHouse Jakarta Meetup - AI Night!</a> - April 22
* <a href="https://aws.amazon.com/events/summits/bengaluru/" target="_blank">AWS Summit Bengaluru</a> - May 7-8
* <a href="https://aws.amazon.com/events/summits/hongkong/" target="_blank">AWS Summit Hong Kong</a> - May 8
* <a href="https://des.analyticsindiamag.com/" target="_blank">Data Engineering Summit</a>, Bengaluru - May 15-16

## 25.3 release {#release}

![1_april.png](https://clickhouse.com/uploads/1_april_706d25bab0.png)

My favorite feature in the 25.3 release is the <a href="https://clickhouse.com/blog/introducing-the-clickhouse-query-condition-cache" target="_blank">query condition cache</a>, which caches the ranges of data that match a `WHERE` clause. This is useful in dashboarding or observability use cases where multiple queries have a different overall shape but the same filtering condition.

This release adds read support for the AWS Glue and Unity catalogs, new array functions, and automatic parallelization for external data. Finally, the JSON data type is now production-ready!

➡️ <a href="https://clickhouse.com/blog/clickhouse-release-25-03" target="_blank">Read the release post</a>

## Six Months with ClickHouse at CloudQuery (The Good, The Bad, and the Unexpected) {#six-months-clickhouse}

![2_april.png](https://clickhouse.com/uploads/2_april_e9f4a4925d.png)

Herman Schaaf and Joe Karlsson shared their six-month experience using ClickHouse as their database backend for cloud asset inventory.

Their key insights include understanding when to use JOINs versus dictionaries for reference data, the critical importance of properly designing sorting keys for query performance, limitations of Materialized Views that led them to create custom snapshot tables, and ClickHouse's surprising versatility for logging and observability data.

Despite some challenges, CloudQuery found that ClickHouse delivered on its promises of speed and scalability for its cloud governance platform.

➡️ <a href="https://www.cloudquery.io/blog/six-months-with-clickhouse-at-cloudquery" target="_blank">Read the blog post</a>

## A Year of Rust in ClickHouse {#year-of-rust}

![3_april.png](https://clickhouse.com/uploads/3_april_b8aa814052.png)

Alexey Milovidov, ClickHouse's CTO, has written a blog about integrating Rust into their codebase.

The initiative began with small components like BLAKE3 and PRQL (with contributions from community members) before implementing more practical features such as Delta Lake support.

Throughout this journey, numerous technical challenges have been tackled, including build system integration, sanitizer compatibility, cross-compilation problems, and symbol size bloat.

➡️ <a href="https://clickhouse.com/blog/rust" target="_blank">Read the blog post</a>

## Scalable EDR Advanced Agent Analytics with ClickHouse {#scalable-edr-analytics}

![7_april.png](https://clickhouse.com/uploads/7_april_c5df7e0bec.png)

Huntress has implemented ClickHouse to enhance its EDR analytics capabilities. Using ClickHouse has allowed them to process billions of data points daily across millions of endpoints while maintaining rapid query performance.

The implementation leverages <a href="https://clickhouse.com/docs/engines/table-engines/mergetree-family/aggregatingmergetree" target="_blank">AggregatingMergeTree</a> and <a href="https://clickhouse.com/docs/materialized-view/incremental-materialized-view" target="_blank">Materialized Views</a> to monitor agent health and stability efficiently.

➡️ <a href="https://www.huntress.com/blog/scalable-edr-advanced-agent-analytics-with-clickhouse" target="_blank">Read the blog post</a>

## ClickHouse acquires HyperDX: The future of open-source observability {#clickhouse-hyperdx}

![4_april.png](https://clickhouse.com/uploads/4_april_f55fe2c585.png)

ClickHouse has acquired HyperDX, a fully open-source observability platform built on ClickHouse.

This acquisition strengthens our ability to provide developers and enterprises with efficient and scalable observability solutions. By combining HyperDX's UI and session replay capabilities with ClickHouse's database performance, we're enhancing our open-source observability offerings.

➡️ <a href="https://clickhouse.com/blog/clickhouse-acquires-hyperdx-the-future-of-open-source-observability" target="_blank">Read the blog post</a>

## Make Before Break - Faster Scaling Mechanics for ClickHouse Cloud {#make-before-break}

![5_april.png](https://clickhouse.com/uploads/5_april_bafbeed1b7.png)

Jayme Bird and Manish Gill wrote a blog post about the "Make Before Break" (MBB) scaling approach introduced in ClickHouse Cloud to address limitations in the previous scaling method.

Initially, ClickHouse Cloud used a single StatefulSet to manage all server replicas, requiring rolling restarts that could take hours during scaling. The MBB approach creates new pods with desired resources before removing old ones, eliminating downtime during scaling operations.

This required developing a MultiSTS architecture where each pod is managed by its own StatefulSet and custom Kubernetes controllers to orchestrate migrations. Despite technical challenges, the team successfully migrated their entire fleet to this new architecture, significantly improving scaling times and reducing customer disruptions.

➡️ <a href="https://clickhouse.com/blog/make-before-break-faster-scaling-mechanics-for-clickhouse-cloud" target="_blank">Read the blog post</a>

## Quick reads {#quick-reads}

* Hossein Kohzadi has written a blog post explaining <a href="https://itnext.io/integrating-clickhouse-with-net-a-comprehensive-guide-to-blazing-fast-analytics-3e178503d54e" target="_blank">how to use ClickHouse in .NET applications</a>.
* Roman Ianvarev <a href="https://medium.com/@rianvarev/introducing-querysight-a-query-driven-approach-to-data-warehouse-development-5f29b4bde4be" target="_blank">introduces QuerySight</a>, a command-line tool that analyzes ClickHouse query logs and provides intelligent optimization recommendations for your dbt project​.
* Raj Kantaria <a href="https://medium.com/@kantariyaraj/talk-to-your-database-with-mcp-88cf2468851d" target="_blank">briefly introduces Anthropic’s Model Context Protocol</a>, using the ClickHouse MCP Server as an example.
* Tom Schreiber walks us through <a href="https://clickhouse.com/blog/accelerating-clickhouse-json-queries-for-fast-bluesky-dashboards" target="_blank">accelerating ClickHouse queries on JSON data with the BlueSky dataset</a>.
* Keshav Agrawal builds a <a href="https://www.akitmcs.com/post/building-a-real-time-data-pipeline-with-go-kafka-clickhouse-and-apache-superset" target="_blank">Real-time data pipeline with Go, Kafka, ClickHouse, and Apache Superset</a>.

## Post of the month {#post-of-the-month}

My favorite post this month was by <a href="https://x.com/A_Pangeran" target="_blank">Andi Pangeran</a>, who’s been trying out Clickhouse’s support for reading from Delta Lake catalogs.

![6_april.png](https://clickhouse.com/uploads/6_april_c0fe0f49cb.png)


➡️ <a href="https://x.com/A_Pangeran/status/1904807887463211506" target="_blank">Read the post</a>
