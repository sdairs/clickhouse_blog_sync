---
title: "October 2025 newsletter"
date: "2025-10-15T08:20:55.057Z"
author: "Mark Needham"
category: "Community"
excerpt: "Welcome to the October 2025 ClickHouse newsletter, which will round up what’s happened in real-time data warehouses over the last month."
---

# October 2025 newsletter

Hello, and welcome to the October 2025 ClickHouse newsletter!

This month, we have a new text index, scaling request logging from millions to billions, modeling messy data for OLAP, querying lakehouses from ClickHouse Cloud, and more!

## Featured community member: Mayank Joshi

This month's featured community member is Mayank Joshi, Co-Founder and CTO at Auditzy.

![image6.png](https://clickhouse.com/uploads/image6_15dde934cf.png)

Auditzy is a SaaS platform that provides comprehensive website auditing for performance, SEO, accessibility, and security analysis. Since 2022, they have been developing tools that provide technical insights to both technical and non-technical users, enabling teams to monitor website health and make data-driven improvements.

When scaling Auditzy's data processing capabilities, they migrated from PostgreSQL to ClickHouse, achieving a 33x performance improvement. Mayank shared this migration story at a ClickHouse meetup in Mumbai in July 2025, and it was <a href="https://clickhouse.com/blog/auditzy-33x-faster-clickhouse-vs-postgres" target="_blank">written up in blog post for the ClickHouse community</a>, highlighting the challenges with Postgres and the benefits of ClickHouse's ultra-fast, scalable architecture.

➡️ <a href="https://www.linkedin.com/in/themayankjoshi/" target="_blank">Follow Mayank on LinkedIn</a>

## Upcoming events

### Open House Roadshow

We have one more event left on the Open House Roadshow, and it’s in our home city of Amsterdam on 28th October!

The event will include keynotes, deep-dive talks, live demos, and AMAs with ClickHouse creators, builders, and users, as well as the opportunity to network with the ClickHouse community.

Alexey Milovidov (our CTO), Tyler Hannan (Senior Director of Developer Relations), and members of our engineering team will be there, so come say hi!

➡️ <a href="https://clickhouse.com/company/events/202510-amsterdam-open-house" target="_blank">Register for the Amsterdam User Conference on October 28</a>

### Global events

* <a href="https://clickhouse.com/company/events/v25-10-community-release-call" target="_blank">v25.10 Community Call</a> - October 30
* <a href="https://clickhouse.com/company/events/202510-EMEA-Webinar-ClickStack-French" target="_blank">Moderniser l’observabilité avec ClickStack : simplifier, accélérer, innover</a> - October 29
* <a href="https://clickhouse.com/company/events/202510-EMEA-Webinar-Iceberg-German" target="_blank">Next Gen Lakehouse Stack: ClickHouse Performance, Iceberg Catalog & Governance</a> - October 29
* <a href="https://clickhouse.com/company/events/202511-intro-clickstack-amer" target="_blank">Introducing ClickStack: The Future of Observability on ClickHouse</a> - November 4

### Virtual training

* <a href="https://clickhouse.com/company/events/202510-AMER-Real-time-Analytics-with-ClickHouse-Level1" target="_blank">Real-time Analytics with ClickHouse: Level 1</a> - October 28
* <a href="https://clickhouse.com/company/events/202510-AMER-Real-time-Analytics-with-ClickHouse-Level2" target="_blank">Real-time Analytics with ClickHouse: Level 2</a> - October 30
* <a href="https://clickhouse.com/company/events/202510-AMER-Real-time-Analytics-with-ClickHouse-Level3" target="_blank">Real-time Analytics with ClickHouse: Level 3</a> - October 31
* <a href="https://clickhouse.com/company/events/202511-amer-emea-query-optimization" target="_blank">ClickHouse Query Optimization Workshop</a> - November 5
* <a href="https://clickhouse.com/company/events/202511-AMER-chDB:Data-Analytics-with-ClickHouse-and-Python" target="_blank">chDB: Data Analytics with ClickHouse and Python</a> - November 12
* <a href="https://clickhouse.com/company/events/202511-AMER-Real-time-Analytics-with-ClickHouse-Level1" target="_blank">Real-time Analytics with ClickHouse: Level 1</a> - November 19
* <a href="https://clickhouse.com/company/events/202512-AMER-Real-time-Analytics-with-ClickHouse-Level1" target="_blank">Real-time Analytics with ClickHouse: Level 1</a> - December 2
* <a href="https://clickhouse.com/company/events/202512-AMER-Real-time-Analytics-with-ClickHouse-Level2" target="_blank">Real-time Analytics with ClickHouse: Level 2</a> - December 3
* <a href="https://clickhouse.com/company/events/202512-AMER-Real-time-Analytics-with-ClickHouse-Level3" target="_blank">Real-time Analytics with ClickHouse: Level 3</a> - December 4
* <a href="https://clickhouse.com/company/events/202512-AMER-Observability-at-Scale-with-ClickStack" target="_blank">Observability at Scale with ClickStack</a> - December 10

### Events in AMER

* <a href="https://clickhouse.com/company/events/202509-amer-bo-meetup" target="_blank">Boston ClickHouse Meetup</a> - September 19
* <a href="https://clickhouse.com/company/events/202511-LATAM-Real-time-Analytics-with-ClickHouse" target="_blank">In person training: Real-time Analytics with ClickHouse, Sao Paolo</a> - November 4
* <a href="https://clickhouse.com/company/events/202511-in-person-Atlanta-Observability-at-Scale-ClickStack" target="_blank">Atlanta In-Person Training - Observability at Scale with ClickStack</a> - November 10
* <a href="https://clickhouse.com/houseparty/the-sql" target="_blank">House Party, The SQL</a>, Las Vegas - December 2

### Events in EMEA

* <a href="https://clickhouse.com/company/events/202510-amsterdam-open-house" target="_blank">Amsterdam User Conference</a> - October 28
* <a href="https://clickhouse.com/company/events/202510-in-person-clickhouse-deep-dive-part-1" target="_blank">ClickHouse Deep Dive Part 1 In-Person Training</a> (Amsterdam) - October 28
* <a href="https://www.techshowmadrid.es/en/big-data-ai-world" target="_blank">BigData & AI World Madrid</a>  - October 29-30
* <a href="https://luma.com/event/manage/evt-iaVxW6AdEaFzKSD" target="_blank">AI Night Tallinn by ClickHouse</a> - October 30
* <a href="https://www.gartner.com/en/conferences/emea/symposium-spain" target="_blank">Gartner IT Barcelona</a> - November 10-13
* <a href="https://www.forward-data-conference.com/en" target="_blank">ForwardData Paris (Data&AI)</a> - November 24
* <a href="https://www.be4data.com/" target="_blank">Paris Monitoring Day</a> - November 25
* <a href="https://www.meetup.com/clickhouse-poland-user-group/events/311309076/?eventOrigin=network_page" target="_blank">ClickHouse Meetup Warsaw</a> - November 26

### Events in APAC

* <a href="https://vdac.vn/pages/indonesia-30-october-2025" target="_blank">Data & AI Summit Indonesia</a> - October 30
* <a href="https://www.getdbt.com/events/roadshow/coalesce-in-sydney" target="_blank">Coalesce Sydney</a> - November 6
* <a href="https://www.getdbt.com/events/roadshow/coalesce-in-melbourne" target="_blank">Coalesce Melbourne</a> - November 11
* <a href="https://laracon.au/" target="_blank">Laracon.au</a> - 13-14 November

## 25.9 release

![image7.png](https://clickhouse.com/uploads/image7_ec1f65c362.png)

My favorite feature in ClickHouse 25.9 is the completely redesigned text index. The new architecture diverges from the previous FST-based implementation to a streaming-friendly design structured around skip index granules, thereby enhancing query analysis efficiency and eliminating the need to load large chunks of data into memory.

The release also introduces automatic global join reordering, achieving 1,450x speedups in TPC-H benchmarks, as well as streaming secondary indices that eliminate startup delays and expanded data lake support, including enhancements to Apache Iceberg.

➡️ <a href="https://clickhouse.com/blog/clickhouse-release-25-09" target="_blank">Read the release post</a>

## Scaling request logging from millions to billions with ClickHouse, Kafka, and Vector

![image8.png](https://clickhouse.com/uploads/image8_22f491bb62.png)

Geocodio migrated from MariaDB to ClickHouse to handle billions of monthly geocoding requests after their deprecated TokuDB engine could no longer keep up with the scale, according to TJ Miller's detailed technical post. The initial approach encountered a common ClickHouse newcomer issue - direct row-level inserts resulted in a `TOO_MANY_PARTS` error, as the system couldn't merge parts quickly enough.

After consulting with the Honeybadger team (who had successfully implemented ClickHouse for their own analytics platform), Miller learned that ClickHouse's key requirement was the batch processing of records. The final architecture uses Kafka and Vector to aggregate data before inserting it into ClickHouse Cloud, with feature flags enabling a zero-downtime migration by running both systems in parallel for validation.

➡️ <a href="https://www.geocod.io/code-and-coordinates/2025-10-02-from-millions-to-billions/" target="_blank">Read the blog post</a>

## If it’s in your catalog, you can query it: The DataLakeCatalog engine in ClickHouse Cloud

![image5.png](https://clickhouse.com/uploads/image5_c5942ed537.png)

Tom Schreiber's guide highlights how ClickHouse Cloud now offers managed DataLakeCatalog functionality, bringing lakehouse capabilities to the cloud service with integrated AWS Glue and Databricks Unity Catalog support in beta.

The Cloud service eliminates the operational complexity of self-managing catalog integrations while leveraging the same high-performance execution path that handles MergeTree, Iceberg, and Delta Lake data uniformly. It also automatically discovers and queries Iceberg and Delta Lake tables from catalog metadata, supporting full Iceberg v2 features and complete Delta Lake compatibility.

Built on recent improvements, including rebuilt Parquet processing, enhanced caching, and optimized metadata layers, the managed DataLakeCatalog enables federated queries across multiple catalog types within a single query.

➡️ <a href="https://clickhouse.com/blog/query-your-catalog-clickhouse-cloud" target="_blank">Read the blog post</a>

## How Laravel Nightwatch handles billions of observability events in real time with Amazon MSK and ClickHouse Cloud

![image4.png](https://clickhouse.com/uploads/image4_60915058f7.png)

Laravel Nightwatch's observability platform launched with impressive results—5,300 users in the first 24 hours, processing 500 million events on day one, with an average dashboard latency of 97ms. The Laravel team achieved this scale using Amazon MSK and ClickHouse Cloud in a dual-database architecture that separates transactional workloads (Amazon RDS for PostgreSQL) from analytical workloads (ClickHouse Cloud).

The technical foundation includes Amazon MSK Express brokers, capable of handling over 1 million events per second during load testing, with ClickPipes integration eliminating the need for custom ETL pipelines. ClickHouse's columnar architecture delivers 100x faster query performance and 90% storage savings compared to traditional row-based databases, enabling sub-second queries across billions of observability events.

➡️ <a href="https://aws.amazon.com/blogs/big-data/how-laravel-nightwatch-handles-billions-of-observability-events-in-real-time-with-amazon-msk-and-clickhouse-cloud/" target="_blank">Read the blog post</a>

## OLAP On Tap: Untangle your bird's nest(edness) (or, modeling messy data for OLAP)

![image2.png](https://clickhouse.com/uploads/image2_f6f62102bb.png)

Johanan Ottensooser addresses the fundamental tension between efficient data collection (nested, variable JSON) and OLAP performance requirements (predictable, typed columns). Johanan demonstrates how rational upstream patterns, such as flexible transaction schemas with variable metadata, can become performance killers in columnar engines that rely on SIMD operations and low-cardinality filtering.

Three ClickHouse solutions emerge:

* Flattened line-item tables with materialized order views for stable analytics
* Nested() columns for consistent but variable-count arrays
* JSON columns with materialized hot paths for evolving schemas.

The key principle is modeling tables based on query grain and access patterns, rather than the source data structure, thereby moving parsing complexity from query time to ingest time for optimal analytical performance.

➡️ <a href="https://www.linkedin.com/pulse/olap-tap-untangle-your-birds-nestedness-modeling-data-ottensooser-axnhc/" target="_blank">Read the blog post</a>

## Build ClickHouse-powered APIs with React and MooseStack

![image9.png](https://clickhouse.com/uploads/image9_4026c615ca.png)

The 514 Labs team has developed a practical framework for building ClickHouse-powered analytics APIs that integrate seamlessly with existing React/TypeScript workflows. Using MooseStack OLAP, developers can introspect ClickHouse schemas to generate TypeScript types and OlapTable objects, then build fully type-safe analytical endpoints with runtime validation.

The architecture uses ClickPipes for real-time Postgres-to-ClickHouse synchronization, automatic OpenAPI specification generation for frontend SDK creation, and Boreal for production deployment with preview environments and schema migration validation.

➡️ <a href="https://clickhouse.com/blog/clickhouse-powered-apis-in-react-app-moosestack" target="_blank">Read the blog post</a>

## Quick reads

* <a href="https://medium.com/logalarm-devs/from-elasticsearch-to-clickhouse-why-we-migrated-logalarm-siem-c0a8373e1809" target="_blank">Logalarm SIEM migrated from Elasticsearch to ClickHouse</a> to overcome scaling limitations with billions of log events, achieving 70-85% storage reduction and sub-second query performance while solving data consistency issues.
* <a href="https://aws.amazon.com/blogs/big-data/seamlessly-integrate-data-on-google-bigquery-and-clickhouse-cloud-with-aws-glue/" target="_blank">This AWS blog post</a> demonstrates how to use AWS Glue ETL to migrate data from Google BigQuery to ClickHouse Cloud on AWS, leveraging the built-in ClickHouse marketplace connector to eliminate the need for custom integration scripts.
* <a href="http://Stromfee.AI" target="_blank">Stromfee.AI launched a platform</a> that combines ClickHouse database with MQTT IoT data analysis and Langchain MCP (Multimodal Conversation Protocol) to create interactive AI avatars as conversational interfaces for data analysis.
* Furkan Kahvec's research demonstrates <a href="https://medium.com/insiderengineering/clickhouse-query-optimization-argmax-vs-final-50c710a1a7f3" target="_blank">a dynamic approach for choosing between ClickHouse's argMax function and the FINAL modifier</a> based on filter selectivity, achieving up to 40% performance improvements and a 9x reduction in memory usage.
* <a href="https://medium.com/@parade4940/building-a-modern-analytics-extension-for-your-software-e6dbac8254be" target="_blank">Parade's guide</a> demonstrates how to build a modern analytics extension using open-source tools: ClickHouse for fast analytics, Apache Superset for visualization, and dlt for data pipelines, transforming transactional applications into analytically powerful platforms.
* <a href="https://medium.com/@dmitry.bogdanov/industrial-data-and-ai-crash-course-part-2-nano-data-platform-ade2bec8a738" target="_blank">Dmitry Bogdanov's hands-on tutorial</a> builds a containerized "Nano Data Platform" using Kafka for streaming, ClickHouse for time-series storage, and Metabase for visualization to handle industrial IoT data from simulated wind turbines.

## Video corner

* Aaron Katz, ClickHouse’s CEO, was <a href="https://clickhouse.com/videos/aaron-katz-thecube-siliconangle" target="_blank">interviewed as part of theCUBE + NYSE Wired’s Mixture of Experts series</a>.
* Yury Izrailevsky, President of Product & Technology at ClickHouse, <a href="https://creators.spotify.com/pod/profile/ossstartuppodcast/episodes/E182-The-Rise-of-ClickHouse-e3992rl?$web_only=true" target="_blank">joined the Open Source Startup Podcast</a>. In the interview, Yury explained how ClickHouse’s columnar architecture and performance optimizations enable petabyte-scale processing with millisecond query times.
* Mark Needham made videos about three prominent ClickHouse observability use cases: <a href="https://clickhouse.com/videos/petabyte-scale-observability-openai" target="_blank">OpenAI</a>, <a href="https://clickhouse.com/videos/tesla-observability" target="_blank">Tesla</a>, and <a href="https://clickhouse.com/videos/anthropic-observability-at-scale" target="_blank">Anthropic</a>.
* Mark also made a video showing how to <a href="https://clickhouse.com/videos/apache-iceberg-inserts" target="_blank">write to Apache Iceberg from ClickHouse</a>.
