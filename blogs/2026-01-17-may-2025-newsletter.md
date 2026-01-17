---
title: "May 2025 Newsletter"
date: "2025-05-12T09:01:00.359Z"
author: "Mark Needham"
category: "Community"
excerpt: "Welcome to the May ClickHouse newsletter, which will round up what’s happened in real-time data warehouses over the last month."
---

# May 2025 Newsletter

Hello, and welcome to the May 2025 ClickHouse newsletter!

This month, we have a deep dive into how ClickHouse has become "lazier", why the Microsoft Clarity analytics platform chose ClickHouse, an MCP/Real-Time Analytics panel, viewer retention metrics with ClickHouse, and more!

## Featured community member: Can Tian {#featured-community-member}

This month's featured community member is Can Tian, Senior Data Platform Engineer at DeepL.

![featured_may.png](https://clickhouse.com/uploads/featured_may_690bc9b49f.png)

Can Tian has a background in building scalable, cloud-native data systems using Python, C++, and modern infrastructure tools. With experience across DeepL, FactoryPal, and Springer Nature, he has worked on everything from data engineering to analytics and platform design.

Can has made <a href="https://github.com/ClickHouse/dbt-clickhouse/pulls?q=is:pr+author:canbekley" target="_blank">impactful contributions to dbt-clickhouse</a>, including adding support for incremental “microbatch” strategies, implementing schema change handling for distributed incremental models, and fixing critical issues related to `ON CLUSTER` statements in replicated databases.

➡️ <a href="https://www.linkedin.com/in/canbekleyici/" target="_blank">Follow Can on LinkedIn</a>

## Upcoming events {#upcoming-events}

It’s only two weeks until <a href="https://clickhouse.com/openhouse?utm_source=marketo&utm_medium=email&utm_campaign=newsletter" target="_blank">Open House, the ClickHouse User Conference</a> in San Francisco on May 29, and the impressive lineup of speakers continues to grow.

Lyft engineers Jeana Choi and Ritesh Varyani will explain how they use ClickHouse for near-real-time and sub-second analytics, enabling swift decision-making.

<a href="https://clickhouse.com/openhouse?utm_source=marketo&utm_medium=email&utm_campaign=newsletter" target="_blank">Register for Open House</a>

### Global events

* <a href="https://clickhouse.com/company/events/v25-5-community-release-call" target="_blank">v25.5 Community Call</a> - May 22

### Free training

* <a href="https://clickhouse.com/company/events/202505-emea-amsterdam-inperson-clickhouse-developer-fast-track" target="_blank">ClickHouse FastTrack Training</a> - Amsterdam - May 12
* <a href="https://clickhouse.com/company/events/202505-emea-amsterdam-inperson-clickhouse-for-observability" target="_blank">ClickHouse Observability Training</a> - Amsterdam - May 13
* <a href="https://clickhouse.com/company/news-events" target="_blank">ClickHouse Fundamentals Training</a> - Virtual - May 14
* <a href="https://clickhouse.com/company/events/202505-emea-munich-inperson-developer-fast-track" target="_blank">ClickHouse Developer FastTrack Training</a> - Munich - May 14
* <a href="https://clickhouse.com/company/events/202505-amer-clickhouse-developer" target="_blank">ClickHouse Developer Training - Virtual</a> - May 21
* <a href="https://clickhouse.com/company/events/clickhouse-fundamentals" target="_blank">ClickHouse Fundamentals - Virtual</a> - May 20, May 22, June 11
* <a href="https://clickhouse.com/company/events/202505-amer-clickhouse-developer" target="_blank">ClickHouse Developer Training  - Virtual</a> - May 21-22
* <a href="https://clickhouse.com/company/events/202505-open-house-query-optimization" target="_blank">In-Person ClickHouse Query Optimization Workshop - San Francisco</a> - May 28
* <a href="https://clickhouse.com/company/events/202505-open-house-clickhouse-developer" target="_blank">In-Person ClickHouse Developer Training Full Day San Francisco</a> - May 28
* <a href="https://clickhouse.com/company/events/202506-emea-clickhouse-datalake" target="_blank">Integrating your Data Lake with ClickHouse - Virtual</a> - June 5

### Events in AMER

* <a href="https://www.meetup.com/clickhouse-austin-user-group/events/307289908" target="_blank">ClickHouse Meetup in Austin -</a> May 13
* <a href="https://clickhouse.com/company/events/2025-05-Amer-Microsoft-Build" target="_blank">Microsoft Build - Seattle</a> - May 19-21
* <a href="https://www.meetup.com/clickhouse-seattle-user-group/events/307622716/" target="_blank">ClickHouse Meetup in Seattle</a> - May 20
* <a href="https://clickhouse.com/company/events/2025-07-Amer-AWSSummit-washingtondc" target="_blank">AWS Summit Washington D.C.</a> - June 10-11
* <a href="https://www.meetup.com/clickhouse-dc-user-group/events/307622954" target="_blank">ClickHouse Meetup in Washington D.C. -</a> June 12
* <a href="https://clickhouse.com/company/events/202507-Amer-confluent-financialserviceleaderssummit" target="_blank">Confluent’s Financial Services Leaders Summit, New York</a> - June 10
* <a href="https://clickhouse.com/company/events/202503-amer-atl-meetup" target="_blank">ClickHouse Meetup in Atlanta</a> - July 8
* <a href="https://clickhouse.com/company/events/202503-amer-NY-meetup" target="_blank">ClickHouse Meetup in New York</a> - July 15
* <a href="https://clickhouse.com/company/events/2025-09-Amer-AWSSummit-Toronto" target="_blank">AWS Summit Toronto</a> - September 4
* <a href="https://clickhouse.com/company/events/2025-09-Amer-AWSSummit-LosAngeles" target="_blank">AWS Summit Los Angeles</a> - September 17

### Events in EMEA

* <a href="https://clickhouse.com/company/events/202505-EMEA-Munich-HappyHour" target="_blank">Munich Happy Hour</a> - May 14
* <a href="https://clickhouse.com/company/events/202505-EMEA-Dubai-AWS-Summit" target="_blank">AWS Summit Dubai</a> - May 21
* <a href="https://clickhouse.com/company/events/202505-EMEA-TelAviv-AWS-Summit" target="_blank">AWS Summit Tel Aviv</a> - May 28
* <a href="https://aws.amazon.com/events/summits/stockholm/" target="_blank">AWS Summit Stockholm</a> - June 4
* <a href="https://aws.amazon.com/events/summits/hamburg/" target="_blank">AWS Summit Hamburg</a> - June 5
* <a href="https://aws.amazon.com/es/events/summits/madrid/" target="_blank">AWS Summit Madrid</a> - June 11
* <a href="https://techbbq.dk/" target="_blank">Tech BBQ Copenhagen</a> - August 27-28
* <a href="https://aws.amazon.com/events/summits/zurich/" target="_blank">AWS Summit Zurich</a> - September 11
* <a href="https://www.bigdataldn.com/" target="_blank">BigData London</a> - September 24-25
* <a href="https://amsterdam.pydata.org/" target="_blank">PyData Amsterdam</a> - September 24-25

### Events in APAC

* <a href="https://clickhouse.com/company/events/2025-05-APJ-Singapore-DevOpsDays" target="_blank">DevOpsDays Singapore</a> - May 15
* <a href="https://des.analyticsindiamag.com/" target="_blank">Data Engineering Summit</a>, Bengaluru - May 15-16
* <a href="https://www.huodongxing.com/event/7803892350511" target="_blank">ClickHouse Meetup in Shenzhen</a> - May 17
* <a href="https://clickhouse.com/company/events/2025-05-APJ-AWSSummit-Singapore" target="_blank">AWS Summit Singapore</a> - May 29
* <a href="https://clickhouse.com/company/events/2025-06-APJ-AWSSummit-Sydney" target="_blank">AWS Summit Sydney</a> - June 4-5
* <a href="https://www.meetup.com/clickhouse-tokyo-user-group/events/307689645/" target="_blank">Tokyo Meetup - AI Night!</a> - June 5
* <a href="https://clickhouse.com/company/events/2025-06-APJ-Tokyo-KubeCon-Japan" target="_blank">KubeCon + CloudNativeCon Japan</a> - June 16-17
* <a href="https://clickhouse.com/company/events/2025-06-APJ-AWSSummit-Tokyo" target="_blank">AWS Summit Japan</a> - June 25-26

## 25.4 release {#release}

![0_may.png](https://clickhouse.com/uploads/0_may_8f18386369.png)

It’s difficult to pick my favorite feature in the 25.4 release, but if I must, I’d go for lazy materialization. This optimization defers reading column data until needed, resulting in much faster queries. More on that in the next section!

MergeTree tables on read-only disks can now refresh their state and load new data parts, which effectively lets us create a ClickHouse-native data lake. Also included in this release is CPU slot scheduling, which lets you cap the number of threads running concurrently for a given workload.

Finally, there’s a nice quality-of-life update in <a href="https://clickhouse.com/docs/operations/utilities/clickhouse-local" target="_blank">clickhouse-local</a>: tables in the default database persist!

➡️ <a href="https://clickhouse.com/blog/clickhouse-release-25-04" target="_blank">Read the release post</a>

## ClickHouse gets lazier (and faster): Introducing lazy materialization {#clickhouse-lazier}

![1_may.png](https://clickhouse.com/uploads/1_may_2efada319d.png)

The lazy materialization functionality has been given the Tom Schreiber treatment, i.e., a super in-depth article breaking down how it works and the use cases it will help with.

Tom starts with ClickHouse’s existing building blocks of I/O efficiency and runs a real-world query through them, layer by layer, until lazy materialization kicks in and dramatically optimizes performance.

➡️ <a href="https://clickhouse.com/blog/clickhouse-gets-lazier-and-faster-introducing-lazy-materialization" target="_blank">Read the blog post</a>

## Why Microsoft Clarity chose ClickHouse {#microsoft-clarity}

![2_may.png](https://clickhouse.com/uploads/2_may_9e6f34ff9b.png)

Microsoft Clarity is a free analytics tool that helps website and app owners understand user interactions through visual snapshots and user interaction data. It provides heatmaps, session recordings, and insights.

When Microsoft decided to offer Clarity as a free public service, it needed to revamp its infrastructure. The original proof-of-concept using Elasticsearch and Spark couldn't handle the anticipated scale of millions of projects and hundreds of trillions of events. The system was slow, had low ingestion throughput, and would be prohibitively expensive at scale.

They turned to ClickHouse as a solution, and in the blog, they describe why they made that choice, what problems it has helped solve, and the challenges they encountered along the way.

➡️ <a href="https://clarity.microsoft.com/blog/why-microsoft-clarity-chose-clickhouse/" target="_blank">Read the blog post</a>

## Introducing AgentHouse {#agenthouse}

![3_may.png](https://clickhouse.com/uploads/3_may_0f0842e7a2.png)

Dmitry Pavlov announced AgentHouse, a chat-based demo environment where you can interact with ClickHouse datasets using the Claude Sonnet Large Language Model.

It uses <a href="https://www.librechat.ai/" target="_blank">LibreChat</a> under the covers, which means that you can get not only text answers to your questions, but also interactive charts.

➡️ <a href="https://clickhouse.com/blog/agenthouse-demo-clickhouse-llm-mcp" target="_blank">Read the blog post</a>

## How we handle billion-row ClickHouse inserts with UUID range bucketing {#billion-row-inserts}

![4_may.png](https://clickhouse.com/uploads/4_may_f3dcb03f83.png)

CloudQuery faced a challenge with ClickHouse when ingesting large batches of data, sometimes exceeding 25 million records per operation. These massive inserts caused out-of-memory errors because ClickHouse materializes the entire dataset in memory before spilling to disk.

To solve this problem, they developed an “Insert-Splitter” algorithm that breaks up large inserts into smaller, manageable chunks based on UUID ranges. This approach required careful implementation due to ClickHouse's UUID sorting behavior.

It worked well, though! Splitting a single 26-million-row insert into four balanced buckets reduced peak memory usage by 75% without sacrificing processing speed.

➡️ <a href="https://www.cloudquery.io/blog/how-we-handle-billion-row-clickhouse-inserts-with-uuid-range-bucketing" target="_blank">Read the blog post</a>

## MySQL CDC connector for ClickPipes is now in Private Preview {#mysql-cdc-connector}

![5_may.png](https://clickhouse.com/uploads/5_may_6a272d293f.png)

We recently announced the private preview of the MySQL Change Data Capture (CDC) connector in ClickPipes.

This lets customers replicate their MySQL databases to ClickHouse Cloud in just a few clicks and leverage ClickHouse for blazing-fast analytics. It works for continuous replication and one-time migration from MySQL, no matter where it's running.

➡️ <a href="https://clickhouse.com/blog/mysql-cdc-connector-clickpipes-private-preview" target="_blank">Read the blog post</a>

## Bootstrapping with ClickHouse {#bootstrapping-clickhouse}

![Bootstrapping with ClickHouse Apr 2025.webp](https://clickhouse.com/uploads/Bootstrapping_with_Click_House_Apr_2025_62bddc39a6.webp)

William Attache from AB Tasty wanted to speed up some statistical algorithms that use bootstrapping data by implementing them directly in ClickHouse SQL.

The blog walks us through his trial-and-error process with ClickHouse's native functions, explaining why initial random number strategies failed and how he eventually solved the problem using SQL-based workarounds and Python user-defined functions.

➡️ <a href="https://medium.com/the-ab-tasty-tech-blog/bootstrapping-with-clickhouse-c1750a9ec6d2" target="_blank">Read the blog post</a>

## Vimeo: behind viewer retention analytics at scale {#vimeo-viewer-retention-analysis}

![7_may.png](https://clickhouse.com/uploads/7_may_92519b28fd.png)

This article fascinated me as a video creator. While view counts provide basic feedback, understanding viewer retention - the percentage of viewers still watching each moment -offers deeper insights into content performance.

Vimeo's blog post reveals how they've built a sophisticated retention analytics system using ClickHouse. Rather than storing absolute view counts, they track viewing patterns by recording changes (+1 when a viewer starts watching a segment, -1 when they stop) and use window functions to calculate cumulative views at each second.

They have also built an AI-powered insights layer, pre-processing retention data through window averaging and run-length encoding to prevent overwhelming the AI's context window. Combined with carefully crafted prompt engineering, they can generate concise, actionable insights about viewer engagement patterns.

➡️ <a href="https://medium.com/vimeo-engineering-blog/behind-viewer-retention-analytics-at-scale-8dbbb5ae7ae2" target="_blank">Read the blog post</a>

## Video Corner {#video-corner}

* Gordon Chan, Staff Engineer at Buildkite (a scale-out delivery platform), <a href="https://www.youtube.com/watch?v=iw2kVH-vSH0" target="_blank">shared their journey adopting ClickHouse for test analytics</a>.
* Prathamesh Sonpatki, Developer Evangelist at Last9, <a href="https://www.youtube.com/watch?v=AYT0O3Al8-U" target="_blank">shared his insights on observability challenges and solutions</a> from building an observability platform that uses ClickHouse under the hood.
* Ryadh Dahimene hosted a panel discussion on <a href="https://clickhouse.com/videos/mcp-real-time-analytics-panel" target="_blank">Model Context Protocol (MCP) at the intersection of real-time analytics</a> with experts from various companies. The participants included representatives from Anthropic, ClickHouse, RunReveal, Five One, and A16Z.
* I created a video showing how to <a href="https://clickhouse.com/videos/backfill-materialized-view" target="_blank">backfill materialized views</a> on existing tables.
* I also showed how to <a href="https://clickhouse.com/videos/iceberg-aws-glue-clickhouse" target="_blank">querying Apache Iceberg tables via the AWS Glue catalog</a>.
* Finally, we have a short video explaining <a href="https://clickhouse.com/videos/json-data-type" target="_blank">ClickHouse’s JSON data type</a>.
