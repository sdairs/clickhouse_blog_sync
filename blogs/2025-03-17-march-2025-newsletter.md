---
title: "March 2025 Newsletter"
date: "2025-03-17T09:57:39.076Z"
author: "Mark Needham"
category: "Community"
excerpt: "Welcome to the March ClickHouse newsletter, which will round up what’s happened in real-time data warehouses over the last month."
---

# March 2025 Newsletter

While the weather in the Northern Hemisphere seems undecided about Spring, there's no confusion about it being time for the March ClickHouse newsletter.

This month, the Postgres CDC connector for ClickPipes went into Public Beta, and we announced general availability for Bring Your Own Cloud on AWS. We’ve got the latest on ClickHouse support for Apache Iceberg, how to build a ClickHouse-based data warehouse for contact center analytics, visitor segmentation with Theta Sketches, and more!


## Featured community member: Matteo Pelati

This month's featured community member is Matteo Pelati, Co-Founder at <a href="https://langdb.ai/" target="_blank">LangDB</a>.

![0_march2025.png](https://clickhouse.com/uploads/0_march2025_dea5945f2b.png)

Before founding LangDB, Matteo held senior leadership positions at Goldman Sachs as Global Head of Product Data Engineering and at DBS Bank as Executive Director of Data Platform Technology, where he led a team of over 130 engineers building bank-wide data platforms.

LangDB is a full-featured and managed AI gateway that provides instant access to 250+ LLMs with enterprise-ready features. It uses ClickHouse as its foundational data store, where all AI gateway data, traces, and analytics are stored. It also leverages ClickHouse's custom UDF functionality to enable direct AI model calls from SQL queries, seamlessly integrating structured data analytics and AI capabilities.

Mateo recently <a href="https://clickhouse.com/videos/singapore-meetup-langdb-building-intelligent-applications-with-clickhouse" target="_blank">presented on LangDB at the ClickHouse Singapore meetup</a>, where he demonstrated how organizations can leverage this integration to build sophisticated AI applications while maintaining complete control over their data infrastructure and analytics pipeline.

➡️ <a href="https://www.linkedin.com/in/matteopelati/" target="_blank">Follow Mateo on LinkedIn</a>

## Upcoming events

It’s just over two months until our biggest event of the year - <a href="https://clickhouse.com/openhouse?utm_source=marketo&utm_medium=email&utm_campaign=newsletter" target="_blank">Open House, The ClickHouse User Conference</a> in San Francisco on May 28-29.

Join us for a full day of technical deep dives, use case presentations from top ClickHouse users, founder updates, and conversations with fellow ClickHouse users. Whether you're new to ClickHouse or an experienced user, there's something for everyone.

➡️ <a href="https://clickhouse.com/openhouse?utm_source=marketo&utm_medium=email&utm_campaign=newsletter" target="_blank">Register for Open House</a>

### Global events

* <a href="https://clickhouse.com/company/events/v25-3-community-release-call" target="_blank">v25.3 Community Call</a> - Mar 20

### Free training

* <a href="https://clickhouse.com/company/events/202503-apj-sydney-inperson-clickhouse-developer" target="_blank">In-Person ClickHouse Developer - Sydney</a> - March 24-25
* <a href="https://clickhouse.com/company/events/202503-latam-sao-paulo-inperson-clickhouse-developer" target="_blank">Treinamento Presencial ClickHouse Developer - São Paulo, Brasil</a>, March 25-26
* <a href="https://clickhouse.com/company/events/202503-apj-melbourne-inperson-clickhouse-developer" target="_blank">In-Person ClickHouse Developer - Melbourne</a> - March 27-28
* <a href="https://clickhouse.com/company/events/202504-apj-bangalore-inperson-developer-fast-track" target="_blank">In-Person ClickHouse Developer Fast Track - Bangalore</a> - April 1
* <a href="https://clickhouse.com/company/events/202504-emea-clickhouse-bigquery-workshop" target="_blank">BigQuery to ClickHouse Workshop - Virtual</a> - April 1
* <a href="https://clickhouse.com/company/events/202504-emea-vienna-inperson-clickhouse-developer" target="_blank">ClickHouse Developer In-Person Training - Vienna, Austria</a> - April 7-8
* <a href="https://clickhouse.com/company/events/202504-apj-clickhouse-observability" target="_blank">Using ClickHouse for Observability - Virtual</a> - April 15
* <a href="https://clickhouse.com/company/events/202504-emea-clickhouse-fundamentals" target="_blank">ClickHouse Fundamentals - Virtual</a> - April 22

### Events in AMER

* <a href="https://www.meetup.com/clickhouse-boston-user-group/events/305882607/?slug=clickhouse-boston-user-group&eventId=300907870&isFirstPublish=true" target="_blank">ClickHouse Meetup @ Klaviyo</a>, Boston - March 25
* <a href="https://www.meetup.com/clickhouse-brasil-user-group/events/306385974/" target="_blank">ClickHouse Meetup in São Paulo</a> - March 25
* <a href="https://www.meetup.com/clickhouse-new-york-user-group/events/305916369/?eventOrigin=group_upcoming_events" target="_blank">ClickHouse Meetup @ Braze</a>, New York - March 26
* <a href="https://www.meetup.com/clickhouse-dc-user-group/events/306439995/" target="_blank">ClickHouse Launching Meetup in DC</a> - March 27
* <a href="https://clickhouse.com/company/events/2025-04-google-next" target="_blank">Google Next</a>, Las Vegas - April 9
* <a href="https://clickhouse.com/openhouse?utm_source=marketo&utm_medium=email&utm_campaign=newsletter" target="_blank">Open House User Conference</a>, San Francisco - May 28-29

### Events in EMEA

* <a href="https://www.meetup.com/clickhouse-switzerland-meetup-group/events/306435122/" target="_blank">ClickHouse Meetup in Zurich</a> - March 24
* <a href="https://www.meetup.com/clickhouse-hungary-user-group/events/306435234/" target="_blank">ClickHouse Meetup in Budapest</a> - March 25
* <a href="https://clickhouse.com/company/events/04-2025-kubecon-london" target="_blank">KubeCon 2025</a>, London - April 1-4
* <a href="https://clickhouse.com/company/events/202504-emea-oslo-meetup" target="_blank">ClickHouse Meetup in Oslo</a> - April 8
* <a href="https://clickhouse.com/company/events/04-2025-aws-paris" target="_blank">AWS Summit 2025</a>, Paris - April 9
* <a href="https://clickhouse.com/company/events/2025-04-aws-summit-amsterdam" target="_blank">AWS Summit 2025</a>, Amsterdam - April 16
* <a href="https://clickhouse.com/company/events/04-2025-aws-london" target="_blank">AWS Summit 2025</a>, London - April 30

### Events in APAC

* <a href="https://www.meetup.com/clickhouse-delhi-user-group/events/306253492/" target="_blank">ClickHouse Delhi Meetup</a>, India - Mar 22
* <a href="https://www.meetup.com/clickhouse-australia-user-group/events/306549810/" target="_blank">ClickHouse Sydney Meetup</a> - April 1
* <a href="https://latencyconf.io/" target="_blank">Latency Conference</a>, Australia - Apr 3-4
* <a href="https://web3.teamz.co.jp/en" target="_blank">TEAMZ Web3/AI Summit</a>, Japan - Apr 16-17

## 25.2 release

![1_march2025.png](https://clickhouse.com/uploads/1_march2025_efc9bd623e.png)

ClickHouse 25.2 delivers more performance gains for joins. The parallel hash join system has been further optimized to ensure 100% CPU core utilization. Tom Schreiber explains how this was achieved.

The release also introduces Parquet Bloom filters, a new backup database engine, integration with the Delta Rust Kernel, enhanced HTTP streaming capabilities for real-time data consumption, and more!

➡️ <a href="https://clickhouse.com/blog/clickhouse-release-25-02" target="_blank">Read the release post</a>

## Postgres CDC connector for ClickPipes is now in Public Beta

![2_march2025.png](https://clickhouse.com/uploads/2_march2025_5d2086949f.png)

The Postgres CDC connector for ClickPipes is now in public beta, enabling seamless replication of PostgreSQL databases to ClickHouse Cloud with just a few clicks.

The connector features high-performance capabilities, including parallel snapshotting for 10x faster initial loads and near real-time data freshness.

Successful implementations are already running at organizations like Syntage and Neon, handling terabyte-scale migrations. During the public beta period, this powerful integration tool is available free of charge to all users.

➡️ <a href="https://clickhouse.com/blog/postgres-cdc-connector-clickpipes-public-beta" target="_blank">Read the blog post</a>

## ClickHouse & Grafana for High Cardinality Metrics

Tomer Ben David explores how ClickHouse and Grafana can effectively handle high cardinality metrics \- a common challenge when tracking data across numerous unique dimensions like individual user sessions, container IDs, or geographical locations.

The article details how ClickHouse's columnar storage, vectorized query execution, and efficient compression capabilities make it ideal for processing large volumes of granular data. Grafana provides powerful visualization, templating features, and alerting to make this data actionable.

Tomer also offers practical strategies for managing high cardinality, including data aggregation techniques, dimensionality reduction, and pre-aggregation at the source.

➡️ <a href="https://medium.com/@Tom1212121/clickhouse-grafana-for-high-cardinality-metrics-4fc3708ba617" target="_blank">Read the blog post</a>

## Climbing the Iceberg with ClickHouse

![3_march2025.png](https://clickhouse.com/uploads/3_march2025_9f42276fd5.png)


Melvyn Peignon explores ClickHouse's evolving role in the data lake and lakehouse ecosystem, highlighting three key integration patterns: data loading from data lakes, ad-hoc querying, and frequent querying of lake data.

He also outlines ClickHouse's 2025 roadmap for lakehouse integration, focusing on three main areas: enhancing user experience for data lake queries through expanded catalog integrations, improving capabilities for working with data lakes, including write support for Iceberg and Delta formats, and developing an Iceberg CDC Connector in ClickPipes.

➡️ <a href="https://clickhouse.com/blog/climbing-the-iceberg-with-clickhouse" target="_blank">Read the blog post</a>

## How Cresta Scales Real-Time Insights with ClickHouse

![4_march2025.png](https://clickhouse.com/uploads/4_march2025_1bf99b75a7.png)

Xiaoyi Ge, Daniel Hoske, and Florin Szilagyi wrote a blog post describing Cresta’s implementation of ClickHouse as its primary data warehouse solution for processing contact center analytics. After migrating from PostgreSQL, it achieved a 50% reduction in storage costs while handling tens of millions of daily records across three dedicated clusters for real-time aggregation, raw event storage, and observability.

The platform now powers Cresta's Director UI, enabling enterprise customers to query billions of records with flexible time ranges while maintaining responsive performance for real-time contact center insights.

They also shared key optimization strategies, including careful schema design to align with query patterns, leveraging materialized views for frequent queries, and utilizing ClickHouse's sparse indexes and bloom filters to accelerate specific queries.

➡️ <a href="https://cresta.com/blog/how-cresta-scales-real-time-insights-with-clickhouse/" target="_blank">Read the blog post</a>

## Announcing General Availability of ClickHouse BYOC (Bring Your Own Cloud) on AWS

![5_march2025.png](https://clickhouse.com/uploads/5_march2025_cd7c95fba4.png)

BYOC (Bring Your Own Cloud) on AWS is generally available, allowing enterprises to run ClickHouse Cloud while keeping all their data within their own AWS VPC environment.

This deployment model, part of a five-year strategic collaboration with AWS, enables organizations to maintain complete data control and security compliance while benefiting from ClickHouse's managed service capabilities.

➡️ <a href="https://clickhouse.com/blog/announcing-general-availability-of-clickhouse-bring-your-own-cloud-on-aws" target="_blank">Read the blog post</a>

## Postgres to ClickHouse: Data Modeling Tips V2

![6_march2025.png](https://clickhouse.com/uploads/6_march2025_461dacaee6.png)

Lionel Palacin and Sai Srirampur provide a comprehensive guide on migrating data from PostgreSQL to ClickHouse using Change Data Capture (CDC). The article explains how ClickPipes and PeerDB enable continuous tracking of inserts, updates, and deletes in Postgres, replicating them to ClickHouse for real-time analytics while maintaining data consistency through ClickHouse's ReplacingMergeTree engine.  

The authors detail several strategies for optimizing performance, including deduplication approaches using the FINAL keyword, views, and materialized views. They also explore advanced topics like custom ordering keys, JOIN optimizations, and denormalization techniques using refreshable and incremental materialized views.

➡️ <a href="https://clickhouse.com/blog/postgres-to-clickhouse-data-modeling-tips-v2" target="_blank">Read the blog post</a>

## Quick reads

* Coroot has <a href="https://coroot.com/blog/engineering/coroot-v1-7-monitoring-clickhouse-and-zookeeper-with-ebpf/" target="_blank">added support for the ClickHouse native and ZooKeeper protocols</a>, making it much easier to observe these distributed systems.
* Keshav Agrawal demonstrates <a href="https://www.akitmcs.com/post/building-a-real-time-data-pipeline-with-go-kafka-clickhouse-and-apache-superset" target="_blank">how to build a scalable real-time data pipeline</a> combining Go for data generation, Kafka for message queuing, ClickHouse for high-performance storage, and Apache Superset for visualization, providing a complete solution for processing both streaming and batch data.
* After finding Grafana's Loki inadequate for web log analysis, Scott Laird documents <a href="https://scottstuff.net/posts/2025/02/27/caddy-logs-in-clickhouse-via-vector/" target="_blank">his migration to ClickHouse</a>. His guide provides step-by-step instructions for setting up ClickHouse with proper authentication, creating an appropriate schema for Caddy's JSON logs, and configuring Vector as the data pipeline middleware to transform and stream logs into ClickHouse.
* <a href="https://sateeshpy.medium.com/building-a-scalable-etl-pipeline-data-warehouse-with-apache-spark-minio-and-clickhouse-0154342872e9" target="_blank">A tutorial by sateesh.py</a> demonstrates how to build a modern ETL pipeline combining Apache Spark for data processing, MinIO for S3-compatible storage, Delta Lake for data storage, and ClickHouse for fast analytical querying, complete with code examples.
* Hellmar Becker demonstrates <a href="https://blog.hellmar-becker.de/2025/03/09/clickhouse-data-cookbook-visitor-segmentation-with-theta-sketches/%20" target="_blank">how to use ClickHouse's theta sketches for visitor segmentation and set operations</a>, efficiently counting unique visitors across different content segments while also performing more complex operations like intersections and unions.

## Post of the month

My favorite post this month was by <a href="https://x.com/chriselgee" target="_blank">Chris Elgee</a>, who likes ClickHouse’s compression functionality.

![7_march2025.png](https://clickhouse.com/uploads/7_march2025_5110d40afa.png)

➡️ <a href="https://x.com/chriselgee/status/1894760925527245261" target="_blank">Read the post</a>
