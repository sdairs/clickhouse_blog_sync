---
title: "June 2025 Newsletter"
date: "2025-06-17T15:02:22.192Z"
author: "Mark Needham"
category: "Community"
excerpt: "Welcome to the June 2025 ClickHouse newsletter, which will round up what’s happened in real-time data warehouses over the last month."
---

# June 2025 Newsletter

Hello, and welcome to the June 2025 ClickHouse newsletter!

This month, we’ve announced ClickStack, our new open-source observability solution. We also learn about the mark cache, how the CloudQuery team built a full-text search engine with ClickHouse, building agentic applications with the MCP Server, analyzing FIX data, and more!

## Featured community member: Joe Karlsson  {#featured-community-member}

This month's featured community member is Joe Karlsson, Senior Developer Advocate at CloudQuery.

![1_june.png](https://clickhouse.com/uploads/1_june_fea80c139d.png)

Joe is a seasoned developer advocate with over 5 years of experience building developer communities around cutting-edge data technologies, progressing through roles at MongoDB, SingleStore, Tinybird, and currently CloudQuery, where he specializes in creating technical content, proof-of-concepts, and educational resources that help developers effectively leverage modern data infrastructure tools.

Joe is a <a href="https://www.cloudquery.io/authors/joe-karlsson" target="_blank">prolific writer in the data engineering space</a>, covering everything from Kubernetes asset tracing to querying cloud infrastructure for expired dependencies.. He's also shared his hands-on ClickHouse experience in <a href="https://www.cloudquery.io/blog/how-we-handle-billion-row-clickhouse-inserts-with-uuid-range-bucketing" target="_blank">How We Handle Billion-Row ClickHouse Inserts With UUID Range Bucketing</a> and <a href="https://www.cloudquery.io/blog/six-months-with-clickhouse-at-cloudquery" target="_blank">Six Months with ClickHouse at CloudQuery (The Good, The Bad, and the Unexpected)</a>.

➡️ <a href="https://www.linkedin.com/in/joekarlsson/" target="_blank">Follow Joe on LinkedIn</a>

## Upcoming events {#upcoming-events}

### Global events

* <a href="https://clickhouse.com/company/events/v25-4-community-release-call" target="_blank">v25.6 Community Call</a> - June 26

### Free training

* <a href="https://clickhouse.com/company/events/202506-amer-clickhouse-admin-workshop" target="_blank">ClickHouse Admin Workshop (Virtual)</a> - June 25
* <a href="https://clickhouse.com/company/events/202506-apj-bangalore-inperson-query-optimization" target="_blank">In-Person ClickHouse Query Optimization Training - Bangalore</a> - June 26
* <a href="https://clickhouse.com/company/events/202507-emea-clickhouse-deeep-dive" target="_blank">ClickHouse Deep Dive Training (Virtual)</a> - July 2
* <a href="https://clickhouse.com/company/events/202507-apj-clickhouse-bigquery-workshop" target="_blank">BigQuery to ClickHouse Workshop (Virtual)</a> - July 9
* <a href="https://clickhouse.com/company/events/202507-in-person-clickhouse-deep-dive" target="_blank">ClickHouse Deep Dive Training - NYC</a> - July 15
* <a href="https://clickhouse.com/company/events/202507-emea-query-optimization" target="_blank">ClickHouse Query Optimization Workshop (Virtual)</a> - July 16
* <a href="https://clickhouse.com/company/events/202507-amer-clickhouse-fundamentals" target="_blank">ClickHouse Fundamentals (Virtual)</a> - July 30

### Events in AMER

* <a href="https://www.meetup.com/clickhouse-denver-user-group/events/308483614" target="_blank">ClickHouse @ RheinHaus Denver</a> - June 26th
* <a href="https://www.meetup.com/clickhouse-chicago-meetup-group/events/308463448https://www.meetup.com/clickhouse-chicago-meetup-group/events/308463448" target="_blank">ClickHouse + Docker AI Night Chicago</a> - July 1st
* <a href="https://clickhouse.com/company/events/202503-amer-atl-meetup" target="_blank">ClickHouse Meetup in Atlanta</a> - July 8
* <a href="https://clickhouse.com/company/events/202507-amer-PH-meetup" target="_blank">ClickHouse Social in Philly</a> - July 11
* <a href="https://clickhouse.com/company/events/202503-amer-NY-meetup" target="_blank">ClickHouse Meetup in New York</a> - July 15
* <a href="https://clickhouse.com/company/events/2025-07-Amer-AWSSummit-NewYork" target="_blank">AWS Summit New York</a> - July 16
* <a href="https://clickhouse.com/company/events/2025-09-Amer-AWSSummit-Toronto" target="_blank">AWS Summit Toronto</a> - September 4
* <a href="https://clickhouse.com/company/events/2025-09-Amer-AWSSummit-LosAngeles" target="_blank">AWS Summit Los Angeles</a> - September 17

### Events in EMEA

* <a href="https://clickhouse.com/company/events/202506-EMEA-Amsterdam-meetup" target="_blank">ClickHouse Meetup in Amsterdam</a> - June 25
* <a href="https://techbbq.dk/" target="_blank">Tech BBQ Copenhagen</a> - August 27-28
* <a href="https://aws.amazon.com/events/summits/zurich/" target="_blank">AWS Summit Zurich</a> - September 11
* <a href="https://www.bigdataldn.com/" target="_blank">BigData London</a> - September 24-25
* <a href="https://amsterdam.pydata.org/" target="_blank">PyData Amsterdam</a> - September 24-25

### Events in APAC

* <a href="https://clickhouse.com/company/events/2025-06-APJ-AWSSummit-Tokyo" target="_blank">AWS Summit Japan</a> - June 25-26
* <a href="https://clickhouse.com/company/events/202506-apj-bangalore-meetup" target="_blank">ClickHouse + Netskope + Confluent Bangalore Meetup</a> - June 27
* <a href="https://clickhouse.com/company/events/202507-apj-perth-meetup" target="_blank">ClickHouse Meetup in Perth</a> - July 2
* <a href="https://clickhouse.com/company/events/202507-APJ-Tokyo-DB-Tech-Showcase" target="_blank">DB Tech Showcase 2025 Tokyo</a> - July 10-11
* <a href="https://clickhouse.com/company/events/202507-APJ-Melbourne-DataEngBytes" target="_blank">DataEngBytes Melbourne</a>
* <a href="https://clickhouse.com/company/events/202507-APJ-Sydney-DataEngBytes" target="_blank">DataEngBytes Sydney</a>

## 25.5 release  {#release}

![2_june.png](https://clickhouse.com/uploads/2_june_e7ccb54577.png)

ClickHouse 25.5 is here, and the vector similarity index has moved from experimental to beta.

We’ve also added Hive metastore catalog support, made clickhouse-local a bit easier to use (you can skip FROM and SELECT with stdin now), and made the Parquet reader handle Geo types.

➡️ <a href="https://clickhouse.com/blog/clickhouse-release-25-05" target="_blank">Read the release post</a>

## ClickStack: A high-performance OSS observability stack on ClickHouse {#clickstack}

![3_june.png](https://clickhouse.com/uploads/3_june_0b1dc30c38.png)

At the recent OpenHouse conference, Mike Shi announced ClickStack, our new open-source observability solution that delivers a complete, out-of-the-box experience for logs, metrics, traces, and session replay powered by ClickHouse's high-performance database technology.

This product announcement represents our increased investment in the observability ecosystem. It combines the ClickHouse columnar storage engine with a purpose-built UI from HyperDX - a company we recently acquired - to create an accessible, unified observability platform.

The stack is completed with native OpenTelemetry integration, providing standardized data collection that simplifies the instrumentation and ingestion of telemetry data from all your applications and services.

➡️ <a href="https://clickhouse.com/blog/clickstack-a-high-performance-oss-observability-stack-on-clickhouse" target="_blank">Read the blog post</a>

## Why (and how) CloudQuery built a full-text search engine with ClickHouse {#cloudquery-fts}

![4_june.png](https://clickhouse.com/uploads/4_june_16f5ba31cb.png)

Our featured community member, Joe Karlsson, and his colleague James Riley have published an insightful blog post detailing their innovative approach to implementing full-text search capabilities.

Rather than adding external search infrastructure like Elasticsearch or MeiliSearch, they built their search index directly within ClickHouse using `ngrambf_v1` Bloom filter indices.

They also explain how they tuned performance, using multi-size ngram Bloom filters, weighted scoring, and thoughtful partitioning to support sub-400 ms search across more than 150 million rows. The post concludes with lessons learned, trade-offs around write performance, and a peek at upcoming features like LLM-based search and incremental indexing.

➡️ <a href="https://www.cloudquery.io/blog/why-and-how-we-built-our-own-full-text-search-engine-with-clickhouse" target="_blank">Read the blog post</a>

## Mark Cache: The ClickHouse speed hack you’re not using (yet) {#mark-cache}

![5_june.png](https://clickhouse.com/uploads/5_june_05a4ae52ad.png)

In his blog post on The New Stack, Anil Inamdar highlights the mark cache in ClickHouse.

This memory-resident mechanism stores metadata pointers that allow ClickHouse to quickly locate data without scanning or decompressing entire files, reducing query times and disk I/O for analytical workloads.

Anil explains how we can configure the size of this cache and then monitor performance using built-in metrics.

➡️ <a href="https://thenewstack.io/mark-cache-the-clickhouse-speed-hack-youre-not-using-yet/?taid=68474b88a2031300010b4f1a" target="_blank">Read the blog post</a>

## Building an agentic application with ClickHouse MCP Server {#agentic-app-clickhouse-mcp}

![10_june.png](https://clickhouse.com/uploads/10_june_3081f67e0c.png)

Lionel Palacin explores how agentic applications powered by LLMs can transform data interaction. Instead of clicking through filters and dropdowns, users can simply ask "Show me the price evolution in Manchester for the last 10 years" and get instant charts with explanations.

Lio takes us through the technical implementation using ClickHouse MCP Server and CopilotKit with React/Next.js, showing developers how to build their own conversational analytics experiences.

➡️ <a href="https://clickhouse.com/blog/building-an-agentic-application-with-clickhouse-mcp-server-and-copilotkit" target="_blank">Read the blog post</a>

## Analyzing FIX Data With ClickHouse {#analyzing-fix}

![7_june.png](https://clickhouse.com/uploads/7_june_5a6c35ed64.png)

Benjamin Wootton shows how we can use ClickHouse to analyze high-volume Financial Information eXchange (FIX) protocol data commonly used in capital markets trading.

Ben shows how to parse raw FIX messages using ClickHouse's built-in string and array functions, creating materialized views that incrementally process trade requests and confirmations. By joining this data with market prices and applying window functions, he calculates the financial impact of trade rejections on different banks' profit and loss positions.

➡️ <a href="https://benjaminwootton.com/insights/analysing-fix-data-with-clickhouse/" target="_blank">Read the blog post</a>

## Building a scalable user segmentation pipeline with ClickHouse and Airflow - Part 1: Model Training {#segmentation-pipeline}

![8_june.png](https://clickhouse.com/uploads/8_june_81f6938436.png)

A/B Tasty is building a scalable, automated user segmentation pipeline using ClickHouse and Apache Airflow. In the first article of a two-part blog series, Jhon Steven Neira covers the model training phase that periodically learns the clusters (centroids) from user behavior data.

ClickHouse handles aggregating user behavior features and performing K-Means clustering in SQL. Airflow ensures the training runs on schedule and that daily inference runs reliably each day using the latest available model.

Steven provides a detailed walkthrough of implementing K-Means clustering in ClickHouse, demonstrating how to use aggregation states and materialized views to build an efficient segmentation system.

➡️ <a href="https://medium.com/the-ab-tasty-tech-blog/building-a-scalable-user-segmentation-pipeline-with-clickhouse-and-airflow-part-1-model-training-75ab9fb59745" target="_blank">Read the blog post</a>

## ClickHouse in the wild: An odyssey through our data-driven marketing campaign in Q-Commerce {#data-driven-marketing}

![9_june.png](https://clickhouse.com/uploads/9_june_4ff47eee43.png)

Parham Abbasi shares how Snapp! Market used ClickHouse to drive a personalized marketing campaign at scale. Millions of users were profiled using <a href="https://en.wikipedia.org/wiki/Myers%E2%80%93Briggs_Type_Indicator#:~:text=In%20MBTI%20theory%2C%20the%20four,value%20of%20naturally%20occurring%20differences." target="_blank">MBTI-style</a> traits derived from real purchase behavior, like impulse levels, health focus, and price sensitivity.

The team used a multi-tiered data lake (<a href="https://clickhouse.com/blog/building-a-medallion-architecture-with-clickhouse" target="_blank">Bronze-Silver-Gold</a>) and ClickHouse’s ability to query Parquet directly to generate production-ready profiles. They also use the `partial_merge` join algorithm to keep memory use stable across multi-year datasets, enabling LLM-generated personas to be delivered at scale.

➡️ <a href="https://medium.com/@prmbas/clickhouse-in-the-wild-an-odyssey-through-our-data-driven-marketing-campaign-in-q-commerce-93c2a2404a39" target="_blank">Read the blog post</a>

## Quick reads {#quick-reads}

* Alexei shows us <a href="https://medium.com/@acosetov/building-udfs-in-clickhouse-with-go-a-step-by-step-guide-813076b167f4" target="_blank">how to write a user-defined function in Golang to check email validity</a>.
* Alasdair Brown and Mark Needham wrote a blog post about <a href="https://clickhouse.com/blog/integrating-clickhouse-mcp" target="_blank">creating "Hello World" examples for the ClickHouse MCP Server with different AI agent libraries</a>.
* We wrote <a href="https://clickhouse.com/blog/highlights-from-open-house-our-first-user-conference" target="_blank">a blog summarizing all the announcements at OpenHouse</a>, including the Postgres CDC connector in ClickPipes going GA, Lightweight Updates, performance improvements for joins, and more!
* Soumil Shah shows <a href="https://medium.com/@shahsoumil519/learn-how-to-query-s3-tables-with-clickhouse-e81a35f62c27" target="_blank">how to query Iceberg tables stored in S3 with ClickHouse</a>.
* Kevin Meneses González explains <a href="https://medium.com/data-science-collective/how-to-ingest-raw-kafka-data-into-clickhouse-without-wrecking-your-pipeline-731e58a76e7d%20" target="_blank">the advantages and disadvantages of each technique for loading data from Kafka into ClickHouse</a>.
* Lloyd Armstrong <a href="https://medium.com/@lloydarmstrong/terraforming-clickhouse-for-real-world-data-warehousing-f51bf2d8bdcc" target="_blank">developed a ClickHouse IAM module for Terraform that abstracts and simplifies the creation of roles and the granting of privileges</a>.
