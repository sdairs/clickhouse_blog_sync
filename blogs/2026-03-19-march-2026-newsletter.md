---
title: "March 2026 newsletter"
date: "2026-03-19T11:15:47.686Z"
author: "Mark Needham"
category: "Community"
excerpt: "Welcome to the March 2026 ClickHouse newsletter, which will round up what’s happened in real-time data warehouses over the last month."
---

# March 2026 newsletter

Hello, and welcome to the March 2026 ClickHouse newsletter!

This month, we have an overview of Geospatial, the launch of chDB 4, how Hookdeck made payload search 60 times faster, The Agentic Data Stack, and more!

## Featured community member: Jamie Herre {#featured-community-member}

This month's featured community member is Jamie Herre, Sr. Director of Engineering at Cloudflare.

![](https://clickhouse.com/uploads/mar2026_nl_image4_2c5abe927e.png)

Jamie leads engineering on Cloudflare's analytics infrastructure - a system that processes over 1.61 quadrillion events every day across more than 300 global data centers, built on ClickHouse.

At the <a href="https://clickhouse.com/blog/cloudflare" target="_blank">ClickHouse meetup in August 2025</a>, Jamie shared how his team designed for both explosive growth and catastrophic failure simultaneously. In one live demonstration, a single query scanned 96 trillion events in under 2 seconds - while a simulated North American outage caused European clusters to silently absorb the load without missing a beat.

➡️ <a href="https://www.linkedin.com/in/jherre/" target="_blank">Connect with Jamie on LinkedIn</a>

## Upcoming events {#upcoming-events}

### Global virtual events {#global-virtual-events}

* <a href="https://clickhouse.com/company/events/v26-3-community-release-call" target="_blank">v26.3 Community Call</a> - Mar 26, 2026
* <a href="https://clickhouse.com/company/events/202604-APJ-Korea-Webinar-CDC-ClickPipes" target="_blank">CDC ClickPipes: 데이터베이스를 ClickHouse로 복제하는 가장 빠른 방법</a> - Apr 1, 2026
* <a href="https://clickhouse.com/company/events/202603-AMER-Webinar-MaterializedViews" target="_blank">Under-the-Hood: ClickHouse Incremental Materialized Views and Dictionaries</a> - Apr 9, 2026
* <a href="https://clickhouse.com/company/events/202604-APJ-Webinar-Unified-Data-Stack-ClickHouse-Postgres" target="_blank">Combining Postgres & ClickHouse to Build a Unified Data Stack</a> - Apr 22, 2026

### Virtual training {#virtual-training}

* <a href="https://clickhouse.com/company/events/202603-AMER-EMEA-Observabiity-with-ClickStackLevel3" target="_blank">Observability with ClickStack: Level 3</a> - Mar 25, 2026
* <a href="https://clickhouse.com/company/events/202604-AMER-EMEA-Observabiity-with-ClickStackLevel2" target="_blank">Observability with ClickStack: Level 2</a> - Apr 7, 2026
* <a href="https://clickhouse.com/company/events/202604-APJ-query-optimization" target="_blank">Query Optimization with ClickHouse Workshop</a> - Apr 7, 2026

### Events in AMER {#events-in-amer}

* <a href="https://clickhouse.com/company/events/20250325" target="_blank">SRECon</a> - Seattle - Mar 25, 2026
* <a href="https://clickhouse.com/company/events/20260324RSA" target="_blank">Bay Area Iceberg Meetup: RSA Edition</a> - San Francisco - Mar 24, 2026
* <a href="https://clickhouse.com/company/events/20260326OBS" target="_blank">Seattle Observability Meetup</a> - Seattle - Mar 26, 2026
* <a href="https://clickhouse.com/company/events/20260331SF" target="_blank">Fireside Chat in San Francisco: Column Stores & the Evolution of Observability</a> - San Francisco - Mar 31, 2026
* <a href="https://clickhouse.com/company/events/20260401Start" target="_blank">Seattle Startup Summit</a> - Seattle - Apr 1, 2026
* <a href="https://clickhouse.com/company/events/2026048ICEY" target="_blank">Iceberg Summit</a> - San Francisco - Apr 8, 2026
* <a href="https://clickhouse.com/company/events/20260409SF" target="_blank">AI Demo Night</a> - San Francisco - Apr 9, 2026
* <a href="https://clickhouse.com/company/events/google-cloud-next-2026" target="_blank">Google Cloud Next 2026</a> - Las Vegas - Apr 22, 2026
* <a href="https://clickhouse.com/company/events/2026-houseparty-google-next" target="_blank">House Party, Google Cloud Next</a> - Las Vegas - Apr 22, 2026
* <a href="https://clickhouse.com/company/events/202605-global-open-house" target="_blank">Open House</a> - San Francisco - May 26, 2026

### Events in EMEA {#events-in-emea}

* <a href="https://clickhouse.com/company/events/202603-EMEA-Munich-meetup" target="_blank">ClickHouse Meetup Munich</a> - Munich - Mar 19, 2026
* <a href="https://talk.clickhouse.com/MjM4LUZQQy0zMTcAAAGgUzZGmrCsh9LwlOhfQ5S4NuJ8xeCq3mUb8G5BcC77kIWCSLiIIgxcRMEPPICfZJY68i42uok=" target="_blank">KubeCon EU</a> - Amsterdam, 23-26 March - Hall 2 stand 261
* <a href="https://talk.clickhouse.com/MjM4LUZQQy0zMTcAAAGgUzZGmmaesRMWlmOCJFDfP-dRMIF62KX7wSNwW7XuKDPuAZhovJEFU7vmLZKWfQhES_NXQvg=" target="_blank">DW&BI</a> - Utrecht, 24 March
* <a href="https://clickhouse.com/company/events/202603-EMEA-Milan-meetup" target="_blank">ClickHouse x Apache Kafka x AWS</a> - Milan - Mar 26, 2026
* <a href="https://ti.to/maltaawsusergroup/gen-a-i-day-malta/with/lpqxlepi9ww" target="_blank">ClickHouse x AWS x DoiT - Gaming and Betting AI Workshop</a> - Malta - March 26, 2026
* <a href="https://clickhouse.com/company/events/202603-EMEA-Benelux-Amsterdam-LunchandLearn" target="_blank">Lunch & Learn with ClickHouse</a> - Amsterdam - Mar 31, 2026
* <a href="https://aws.amazon.com/events/summits/paris/" target="_blank">AWS Summit Paris</a> - Paris, 1 April - Level 1 (nr. G3)
* <a href="https://clickhouse.com/company/events/202604-EMEA-Observability-with-ClickStack" target="_blank">Amsterdam In-Person Training: Observability with ClickStack</a> - Amsterdam - Apr 8, 2026
* <a href="https://events.confluent.io/awsstartupexchangevienna2026" target="_blank">CTO Networking Event with ClickHouse, AWS, Confluent & DoiT</a> - Vienna - Apr 9, 2026
* <a href="https://luma.com/wjv3v1tn" target="_blank">Scaling the Enterprise AI Operating Model</a> - Berlin - Apr 14, 2026
* <a href="https://clickhouse.com/company/events/202604-EMEA-Paris-Real-time-Analytics-w-ClickHouse" target="_blank">Paris In-Person Training: Real-time Analytics with ClickHouse</a> - Paris - Apr 15, 2026
* <a href="https://www.meetup.com/clickhouse-ireland-user-group/events/313793261" target="_blank">ClickHouse Meetup in Dublin</a> - Dublin - Apr 16, 2026
* <a href="https://grafana.com/events/grafanacon/" target="_blank">GrafanaCON</a> - Barcelona - Apr 20-22, 2026
* <a href="https://clickhouse.com/company/events/202604-EMEA-Barcelona-Real-time-Analytics-w-ClickHouse" target="_blank">Barcelona In-Person Training: Real-time Analytics with ClickHouse</a> - Barcelona - Apr 20, 2026
* <a href="https://aws.amazon.com/events/summits/london/" target="_blank">AWS Summit London</a> - London - Apr 22 - Booth G18
* <a href="https://riseof.ai/conference-2026/" target="_blank">Rise of AI Berlin</a> - Berlin - May 5-6, 2026
* <a href="https://aws.amazon.com/events/summits/tel-aviv/" target="_blank">AWS Summit Tel Aviv</a> - Tel Aviv - May 6, 2026
* <a href="https://datainnovationsummit.com/" target="_blank">Data Innovation Summit</a> - Stockholm - May 6-8, 2026
* <a href="http://gartner.com/en/data-analytics" target="_blank">Gartner Data & Analytics</a> - London - May 11-13, 2026
* <a href="https://www.revolutionbanking.es/" target="_blank">Revolution Banking</a> - Madrid - May 12, 2026
* <a href="https://www.platfor-ma.com/" target="_blank">Platforma 2026</a> - Tel Aviv - May 20, 2026
* <a href="https://aws.amazon.com/events/summits/hamburg/" target="_blank">AWS Summit Hamburg</a> - Hamburg - May 20, 2026
* <a href="https://clickhouse.com/company/events/202605-EMEA-London-Real-time-Analytics-w-ClickHouse" target="_blank">London 2-day In-Person Training: Real-time Analytics with ClickHouse</a> - London - May 19, 2026
* <a href="https://www.meetup.com/clickhouse-london-user-group/events/313759007/" target="_blank">ClickHouse Meetup London</a> - London - May 19, 2026
* <a href="https://cloudonair.withgoogle.com/events/cloud-ai-live-madrid-2026" target="_blank">Google Summit Madrid</a> - Madrid - May 28, 2026

### Events in APAC {#events-in-apac}

* <a href="https://2026.pythonasia.org/" target="_blank">Python Asia 2026</a> - Manila - Mar 21-22, 2026
* <a href="https://clickhouse.com/company/events/meetup-nz-23mar2026" target="_blank">Postgres + ClickHouse: Building a Real-Time Open-Source Data Stack</a> - Auckland - Mar 23, 2026
* <a href="https://dataengbytes.com/2026/auckland" target="_blank">DataEngBytes Auckland</a> - Mar 24, 2026
* <a href="https://clickhouse.com/company/events/meetup-nz-25mar2026" target="_blank">Wellington Data Eng Meetup</a> - Wellington - Mar 25, 2026
* <a href="https://clickhouse.com/company/events/202603-apj-shenzhen-meetup" target="_blank">ClickHouse Shenzhen Meetup</a> - Shenzhen - Mar 28, 2026
* <a href="https://clickhouse.com/company/events/202604-APJ-Korea-Webinar-CDC-ClickPipes" target="_blank">Korean Webinar: CDC ClickPipes: 데이터베이스를 ClickHouse로 복제하는 가장 빠른 방법</a> - Apr 1, 2026
* <a href="https://events.confluent.io/dswt2026mumbai" target="_blank">Data Streaming World Mumbai</a> - Apr 13, 2026
* <a href="https://events.confluent.io/dswt2026bangalore" target="_blank">Data Streaming World Bangalore</a> - Apr 16, 2026
* <a href="https://clickhouse.com/company/events/taipei-open-source-meetup" target="_blank">Taipei Open Source Meetup</a> - Taipei - Apr 16, 2026
* <a href="https://www.meetup.com/clickhouse-bangalore-user-group/events/313739871/" target="_blank">Bangalore Meetup with Alexey Milovidov</a> - Apr 18, 2026
* <a href="https://events.confluent.io/dswt2026jakarta" target="_blank">Data Streaming World Jakarta</a> - Apr 21, 2026
* <a href="https://clickhouse.com/company/events/202604-APJ-Webinar-Unified-Data-Stack-ClickHouse-Postgres" target="_blank">APJ Webinar: Combining Postgres & ClickHouse to Build a Unified Data Stack</a> - Apr 22, 2026
* <a href="https://clickhouse.com/company/events/202604-APJ-HoChiMinh-Real-time-Analytics-with-ClickHouse" target="_blank">Ho Chi Minh In-Person Training: Real-time Analytics with ClickHouse</a> - Ho Chi Minh - Apr 22, 2026
* <a href="https://aws.amazon.com/events/summits/bengaluru/" target="_blank">AWS Summit Bengaluru</a> - Apr 22-23, 2026

## 26.2 release {#26-2-release}

![](https://clickhouse.com/uploads/mar2026_nl_image9_00d00cbf75.png)

My favorite feature in the recent ClickHouse 26.2 release is time-based block flushing for streaming data. This lets you batch inserts by time interval rather than row count, which is useful for low-throughput feeds like Wikimedia recent changes.

The release also brings production-ready text index and QBit data types, 3.2x faster RIGHT/FULL JOINs, and embedded ClickStack for in-product observability.

➡️ <a href="https://clickhouse.com/blog/clickhouse-release-26-02" target="_blank">Read the release post</a>

## Building towards an enterprise-grade Postgres service in ClickHouse Cloud {#building-towards-an-enterprise-grade-postgres-service}

![](https://clickhouse.com/uploads/mar2026_nl_image3_b4e4cebe10.jpg)

Sai Srirampur introduces the enterprise-grade Postgres service, coming soon to ClickHouse Cloud, bringing cross-AZ high availability, point-in-time recovery, automated backups, and failover-safe CDC slots for ClickHouse integration.

In other Postgres news, Kaushik Iska introduces <a href="https://clickhouse.com/blog/pg_stat_ch-postgres-extension-stats-to-clickhouse" target="_blank">pg_stat_ch</a>, an open-source Postgres extension that streams query metrics directly into ClickHouse for latency analysis and error tracking without impacting production performance.

➡️ <a href="https://clickhouse.com/blog/enterprise-postgres-service-in-clickhouse-cloud" target="_blank">Read the blog post</a>

## Announcing chDB 4: Write Pandas, Run ClickHouse, Now on Hex {#announcing-chdb-4}

![](https://clickhouse.com/uploads/mar2026_nl_image10_d4f00e1d08.png)

Ryadh Dahimene and Auxten Wang introduce chDB 4, which adds a Pandas-compatible DataStore API that executes on ClickHouse's engine under the hood.

Operations run lazily as an optimized pipeline, with automatic routing between ClickHouse and Pandas engines, and it's now available natively in Hex notebooks.

➡️ <a href="https://clickhouse.com/blog/chdb.4-0-pandas-hex" target="_blank">Read the release post</a>

## How Trigger.dev built a custom SQL language on top of ClickHouse {#how-trigger-dev-built-a-custom-sql-language}

![](https://clickhouse.com/uploads/mar2026_nl_image6_3d154dfd7b.png)

Matt Aitken, CEO of Trigger.dev, explains how they gave users SQL access to a shared multi-tenant ClickHouse cluster without risking data leaks.

Their solution is TRQL, a SQL-style DSL that compiles to tenant-isolated ClickHouse queries - dangerous operations are grammatically impossible, and tenant filters are injected at compile time.

➡️ <a href="https://trigger.dev/blog/how-trql-works" target="_blank">Read the blog post</a>

## Announcing General Availability of ClickHouse Full-text Search {#announcing-general-availability-of-full-text-search}

![](https://clickhouse.com/uploads/mar2026_nl_image7_a3a43dd469.png)

Melvyn Peignon announces the general availability of full-text search in ClickHouse, which uses native inverted indexes to enable fast token-based filtering at scale.

The implementation supersedes Bloom filters for string matching, delivering deterministic results without false positives and reducing the number of granules scanned by up to 96%.

To see it in action, Lionel Palacin built <a href="https://clickhouse.com/blog/gittrends" target="_blank">GitTrends</a>, an open-source demo that searches and aggregates nearly 10 billion GitHub events in real time, with a live comparison tool showing the performance differences between full-text search, Bloom filters, and a full table scan.

➡️ <a href="https://clickhouse.com/blog/full-text-search-ga-release" target="_blank">Read the blog post</a>

## How we made payload search 60x faster in ClickHouse {#how-we-made-payload-search-60x-faster}

![](https://clickhouse.com/uploads/mar2026_nl_image5_7eaefa6d9a.png)

Maurice Kherlakian at Hookdeck describes how webhook payload search across millions of semi-structured JSON records was timing out at 30+ seconds, making debugging nearly impossible.

The fix: hashing values into typed bucket columns so queries scan a single bucket instead of all, combined with iterative time-window scanning that stops once enough results are found, bringing latency down to under 400ms.

➡️ <a href="https://hookdeck.com/blog/how-we-made-payload-search-60x-faster-in-clickhouse" target="_blank">Read the blog post</a>

## The Agentic Data Stack {#the-agentic-data-stack}

![](https://clickhouse.com/uploads/mar2026_nl_image1_9d8086f2d3.png)

Dustin Healy outlines an open-source agentic data stack that lets AI agents query ClickHouse directly via natural language, replacing dashboards and data tickets with real-time conversational access.

The architecture combines ClickHouse's MCP server with an open-source LLM interface and Langfuse for observability, keeping data and infrastructure under the user's control.

➡️ <a href="https://clickhouse.com/blog/the-agentic-data-stack" target="_blank">Read the blog post</a>

## ClickHouse TTL in production: A safe strategy for data retention and disk optimization {#clickhouse-ttl-in-production}

![](https://clickhouse.com/uploads/mar2026_nl_image8_5f21853f75.png)

Aliakbar Hosseinzadeh shares a production runbook for implementing ClickHouse TTL policies after his cluster hit 97% disk utilization, covering the key mental model shift: TTL runs during background merges, not at insert time.

The winning combination is to align partitioning with your TTL time unit and `set ttl_only_drop_parts=1`, which lets ClickHouse drop whole parts cleanly rather than triggering expensive mutation-style rewrites.

➡️ <a href="https://medium.com/@aliakbarhosseinzadeh/clickhouse-ttl-in-production-a-safe-strategy-for-data-retention-and-disk-optimization-9f1546fe673f" target="_blank">Read the blog post</a>

## Quick reads {#quick-reads}

* Mark Needham <a href="https://clickhouse.com/blog/state-of-geospatial-march-2026" target="_blank">surveys everything ClickHouse can do with geospatial data in 2026</a> - from Geometry types and spatial operations to H3 grid-based analytics that run 12x faster than bounding-box queries on 10 million rows.
* Fiona J. Sylvester shows how to run <a href="https://medium.com/@fiona.j.sylvester/wait-you-can-do-anomaly-detection-directly-inside-a-database-ba6ec8dceb8c" target="_blank">STL-based anomaly detection directly in ClickHouse</a>, catching subtle deviations like a silent 4% transaction drop that would be missed by fixed thresholds.
* Parade suggests that <a href="https://medium.com/@parade4940/stop-calling-it-saas-why-you-should-dump-microsoft-fabric-and-use-clickhouse-for-data-analytics-62e73b3cffbe" target="_blank">Microsoft Fabric's shared capacity model creates unpredictable performance</a> and runaway costs, and that swapping in ClickHouse as the analytics engine keeps Power BI intact while cutting bills from tens to thousands of dollars a month.
* Tom Schreiber <a href="https://clickhouse.com/blog/table-cloning" target="_blank">explains how the CLONE AS command</a> creates instant copies of tables of any size by hard-linking immutable data parts rather than copying bytes, enabling safe experimentation on production-scale data with near-zero storage overhead.
* Shuva Jyoti Kar <a href="https://medium.com/google-cloud/agentic-threat-hunting-conversational-telemetry-with-clickhouse-the-new-mcp-java-sdk-and-google-bb3d98aff1f3" target="_blank">built a SecOps agent</a> that uses Google's MCP Toolbox and ClickHouse to let analysts query millions of rows of security telemetry in plain English, without exposing the schema or letting the LLM write raw SQL.
* Mohamed Hussain S explains how <a href="https://medium.com/@mohhddhassan/the-clickhouse-mental-model-most-engineers-miss-c1f39b18f46f" target="_blank">understanding two ClickHouse internals</a> - aggregation states and argMax - unlocks simpler, more powerful query design that would require subqueries and joins in traditional SQL databases.


---

## Get started today

Interested in seeing how ClickHouse works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-110-get-started-today-sign-up&utm_blogctaid=110)

---