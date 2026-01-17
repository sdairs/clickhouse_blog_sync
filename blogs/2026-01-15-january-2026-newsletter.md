---
title: "January 2026 newsletter"
date: "2026-01-15T09:50:24.873Z"
author: "Mark Needham"
category: "Community"
excerpt: "Welcome to the January 2026 ClickHouse newsletter, which will round up what’s happened in real-time data warehouses over the last month."
---

# January 2026 newsletter

Hello, and welcome to the January 2026 ClickHouse newsletter!

This month, we learn how chDB achieved true zero-copy integration with Pandas DataFrames, how WKRP migrated their RuneScape tracking plugin from TimescaleDB to ClickHouse, replacing Apache Flink with ClickHouse's Kafka engine, and more!

## Featured community member: lgbo {#featured-community-member}

This month's featured community member is lgbo.

![jan20026_image5.png](https://clickhouse.com/uploads/jan20026_image5_7e4ba288f9.png)

lgbo works at BIGO, where they use ClickHouse in their real-time data pipeline that processes tens of billions of messages daily.

lgbo has submitted several pull requests to address performance issues, including reducing memory usage for window functions, reducing cache misses during hash table iteration, and optimizing CROSS JOINs.

lgbo also improved short-circuit execution performance by avoiding unnecessary operations on non-function columns, added a new stringCompare function for lexicographic comparison of substring portions, and fixed a bug where named tuple element names weren't preserved correctly during type derivation.

➡️ <a href="https://github.com/lgbo-ustc" target="_blank">Follow lgbo on GitHub</a>

## 25.12 release {#release}

![jan20026_image6.png](https://clickhouse.com/uploads/jan20026_image6_a0edc2e602.png)

ClickHouse 25.12 delivers significant improvements in query performance across the board. We have faster top-N queries through data skipping indexes, a reimagined lazy reading execution model that's 75 times faster, and a more powerful DPsize join reordering algorithm.

➡️ <a href="https://clickhouse.com/blog/clickhouse-release-25-12" target="_blank">Read the release post</a>

## The Journey to Zero-Copy: How chDB Became the Fastest SQL Engine on Pandas DataFrame {#chdb}

![jan20026_image7.png](https://clickhouse.com/uploads/jan20026_image7_1d3f81a67a.png)

chDB v4.0 achieves true zero-copy integration with Pandas DataFrames. By eliminating serialization steps and implementing direct memory sharing between ClickHouse and NumPy, queries that previously took 30 seconds now complete in under a second.

➡️ <a href="https://clickhouse.com/blog/chdb-journey-to-zero-copy" target="_blank">Read the blog post</a>

## A small-time review of ClickHouse {#clickhouse_review}

WKRP migrated their RuneScape tracking plugin from TimescaleDB to ClickHouse with impressive results. Storage usage improved dramatically: location data compressed from 4.28 GiB to 592 MiB (87% reduction), while XP tracking data went from 872 MiB to 168 MiB (81% reduction). Beyond storage, the migration simplified operations - upgrades now happen through the package manager without coordinated downtime.

The verdict: "Timescale worked well, but ClickHouse has provided better performance and made running the service easier."

➡️ <a href="https://www.wkrp.xyz/a-small-time-review-of-clickhouse/" target="_blank">Read the blog post</a>

## Solving the "Impossible" in ClickHouse: Advent of Code 2025 {#advent_of_code}

![jan20026_image1.png](https://clickhouse.com/uploads/jan20026_image1_245b4653d7.png)

Yes, we're still talking about Christmas in mid-January, but Zach Naimon's deep dive into solving Advent of Code 2025 entirely in ClickHouse SQL is worth the delayed celebration.

Following strict rules (pure SQL only, raw inputs, single queries), Zach tackled all 12 algorithmic puzzles that typically require Python, Rust, or C++. The solutions showcase ClickHouse's versatility through recursive CTEs for pathfinding, arrayFold for state machines, and specialized functions like intervalLengthSum for geometric problems.

Proof that with the right tools, "impossible" problems become just another data challenge.

➡️ <a href="https://clickhouse.com/blog/clickhouse-advent-of-code-2025" target="_blank">Read the blog post</a>

## Seven Companies, One Pattern: Why Every Scaled ClickHouse Deployment Looks the Same {#seven_companies}

Luke Reilly explains why Uber, Cloudflare, Instacart, GitLab, Lyft, Microsoft, and Contentsquare all build the same four-layer abstraction stack over ClickHouse: it changes cost curves.

Platform teams absorb schema optimization knowledge once through semantic layers and query translation engines, enabling sublinear scaling - headcount grows with data volume instead of user count.

Now AI is becoming the fifth layer, with tools like ClickHouse.ai and MCP servers adding natural language interfaces on top of these semantic definitions.

➡️ <a href="https://medium.com/@lureilly1/seven-companies-one-pattern-why-every-scaled-clickhouse-deployment-looks-the-same-d2ba68606ad6" target="_blank">Read the blog post</a>

## Your AI SRE needs better observability, not bigger models {#ai_sre}

![jan20026_image2.png](https://clickhouse.com/uploads/jan20026_image2_f3bbf2f869.png)

Drawing on his experience increasing Confluent's availability from 99.9% to 99.95%, Manveer Chawla explains why AI SRE copilots should prioritize investigation over auto-remediation. Most AI SRE tools fail because they're built on observability platforms with short retention, dropped high-cardinality dimensions, and slow queries.

The solution? Rethink the observability architecture. Manveer details a reference architecture using ClickHouse that demonstrates the effectiveness of AI copilots, which require better data foundations, rather than larger models.

➡️ <a href="https://clickhouse.com/blog/ai-sre-observability-architecture" target="_blank">Read the blog post</a>

## Simplifying real-time data pipelines: How ClickHouse replaced Flink for our Kafka Streams {#kafka_streams}

![jan20026_image4.png](https://clickhouse.com/uploads/jan20026_image4_df92d08407.png)

Ashkan Goleh Pour provides a detailed walkthrough of replacing Apache Flink with ClickHouse's native Kafka integration for real-time streaming.

The architecture uses ClickHouse's Kafka table engine to consume events directly, Materialized Views for continuous SQL transformations, and MergeTree tables for persistent state, thereby eliminating the need for external stream processors.

➡️ <a href="https://medium.com/towards-data-engineering/simplifying-real-time-data-pipelines-how-clickhouse-replaced-flink-for-our-kafka-streams-13f6f4e1e097" target="_blank">Read the blog post</a>

## Quick reads {#quick-reads}

* Georgii Baturin has written a multi-part series of posts showing <a href="https://medium.com/hands-on-dbt-with-clickhouse/hands-on-dbt-with-clickhouse-7-why-tests-matter-and-why-a-green-build-does-not-prove-anything-by-c15f1cb1264d" target="_blank">how to use dbt with ClickHouse</a>.
* Shuva Jyoti Kar demonstrates <a href="https://medium.com/@shuva.jyoti.kar.87/the-speed-of-thought-real-time-analytics-meets-agentic-ai-1864e1ed6165" target="_blank">how to build an autonomous AI agent system</a> by connecting ClickHouse with Google's Gemini CLI using the Model Context Protocol (MCP).
* Gulled Hayder shows <a href="https://medium.com/@aagulled/getting-clickhouse-ready-for-web-traffic-analysis-6bec9867e1ee" target="_blank">how to set up ClickHouse on a Linux system</a> with Python, install and configure the database with proper authentication, generate 1 million rows of synthetic web traffic data, and load it into a MergeTree table for analytics.
* ByteBoss [builds a real-time cryptocurrency market data pipeline](https://medium.com/@ByteBosss/building-a-real-time-cryptocurrency-market-data-pipeline-from-scratch-9c81acf3f75b) that connects to exchange WebSockets (Binance/Coinbase), normalizes their different data formats, streams through Kafka/Redpanda, automatically processes with ClickHouse materialized views, and visualizes live trading data in Grafana dashboards.

## Interesting projects {#interesting-projects}

* <a href="https://github.com/arniwesth/DoomHouse" target="_blank">DoomHouse</a> - An experimental "Doom-like" game engine that renders the 3D graphics entirely in ClickHouse SQL.
* <a href="https://hub.docker.com/r/genezhang/clickgraph" target="_blank">genezhang/clickgraph</a> - Stateless, read-only graph query engine for ClickHouse using Cypher.
* <a href="https://github.com/ppiankov/clickspectre" target="_blank">clickspectre</a> - A spectral ClickHouse analyzer that tracks which tables are actually used and by whom.

## Upcoming events {#upcoming-events}

### Virtual training

* <a href="https://clickhouse.com/company/events/202602-amer-clickhouse-admin-workshop" target="_blank">ClickHouse Admin Workshop</a> - 12th February
* <a href="https://clickhouse.com/company/events/202602-amer-emea-query-optimization" target="_blank">ClickHouse Query Optimization Workshop</a> - 19th February

**Real-time Analytics**

* <a href="https://clickhouse.com/company/events/202601-EMEA-Real-time-Analytics-with-ClickHouse-Level2" target="_blank">Real-time Analytics with ClickHouse: Level 2</a> - 21st January
* <a href="https://clickhouse.com/company/events/202601-EMEA-Real-time-Analytics-with-ClickHouse-Level3" target="_blank">Real-time Analytics with ClickHouse: Level 3</a> - 28th January

**Observability**

* <a href="https://clickhouse.com/company/events/202601-APJ-Observability-with-ClickStack-Level1" target="_blank">Observability with ClickStack: Level 1</a> (APJ time) - 27th January
* <a href="https://clickhouse.com/company/events/202601-APJ-Observability-with-ClickStack-Level2" target="_blank">Observability with ClickStack: Level 2</a> (APJ time) - 29th January
* <a href="https://clickhouse.com/company/events/202602-AMER-Observability-with-ClickStack-Level1" target="_blank">Observability with ClickStack: Level 1</a> - 4th February
* <a href="https://clickhouse.com/company/events/202602-AMER-Observabiity-with-ClickStackLevel2" target="_blank">Observability with ClickStack: Level 2</a> - 5th February

### Events in AMER

* <a href="https://luma.com/abggijbh" target="_blank">Iceberg Meetup in Menlo Park</a> - 21st January
* <a href="https://luma.com/ifxnj82q" target="_blank">Iceberg Meetup in NYC</a> - 23rd January
* <a href="https://luma.com/iicnlq41" target="_blank">New York Meetup</a> - 26th January
* <a href="https://clickhouse.com/company/events/webinar-true-cost-of-speed" target="_blank">The True Cost of Speed: What Query Performance Really Costs at Scale</a> - 3rd February
* <a href="https://luma.com/j2ck1sbz" target="_blank">AI Night SF</a> - 11th February
* <a href="https://www.meetup.com/clickhouse-toronto-user-group/events/312881151/?slug=clickhouse-toronto-user-group&eventId=310164482&isFirstPublish=true" target="_blank">Toronto Meetup</a> - 19th February
* <a href="https://luma.com/jsctpwoa" target="_blank">Seattle Meetup</a> - 26th February
* <a href="https://luma.com/wbkqmaqk" target="_blank">LA Meetup</a> - 6th March

### Events in EMEA

* <a href="https://luma.com/3szhmv9h" target="_blank">Data & AI Paris Meetup</a> - 22nd January
* <a href="https://clickhouse.com/company/events/agentic-data-stack-ams" target="_blank">The Agentic Data Stack: The Future is Conversational</a> (Amsterdam) - 27th January
* <a href="https://clickhouse.com/company/events/202601-EMEA-Paris-meetup" target="_blank">ClickHouse Meetup in Paris</a> - 28th January
* <a href="https://luma.com/yx3lhqu9" target="_blank">Apache Iceberg™ Meetup Belgium: FOSDEM Edition</a> - 30th January
* <a href="https://luma.com/czvs584m" target="_blank">FOSDEM Community Dinner Brussels</a> - 31st January
* <a href="https://clickhouse.com/company/events/202602-EMEA-Barcelona-meetup" target="_blank">ClickHouse Meetup in Barcelona</a> - 5th February
* <a href="https://clickhouse.com/company/events/202602-EMEA-London-meetup" target="_blank">ClickHouse Meetup in London</a> - 10th February
* <a href="https://www.meetup.com/clickhouse-georgia-meetup-group/events/312852206/" target="_blank">ClickHouse Meetup in Tbilisi Georgia</a> - 24th February

### Events in APAC

* <a href="https://clickhouse.com/company/events/202601-APJ-Singapore-Meetup" target="_blank">ClickHouse Singapore Meetup</a> - 27th January
* <a href="https://clickhouse.com/company/events/202601-APJ-Real-time-Analytics-w-ClickHouse" target="_blank">Boot Camp: Real-time Analytics with ClickHouse</a> - 27th January
* <a href="https://clickhouse.com/company/events/202601-apj-seoul-meetup" target="_blank">ClickHouse Seoul Meetup</a> - 29th January

### Speaking at ClickHouse meetups

Want to speak at a ClickHouse meetup? <a href="https://docs.google.com/forms/d/e/1FAIpQLSdpYbh0k3hmLOQ7JLXrubvEbiIul4TxJDp1AVewXHSdzHcmzA/viewform" target="_blank">Apply here!</a>

Below are some upcoming call for papers (CFPs):

* <a href="https://sessionize.com/iceberg-summit-2026/" target="_blank">Iceberg Summit SF</a> - April 6-8
* <a href="https://aicouncil.com/apply-to-speak" target="_blank">AI Council SF</a> - May 12-14
* <a href="https://sessionize.com/observability-summit-2026" target="_blank">Observability Summit Minneapolis</a>  - May 21-22
* <a href="https://events.linuxfoundation.org/kubecon-cloudnativecon-india/program/cfp/" target="_blank">Kubecon India Mumbai</a> - June 18-19
* <a href="https://pretalx.com/grafanacon-2026/cfp" target="_blank">GrafanaCon Barcelona</a> - April 20-22
* <a href="https://sessionize.com/wearedevelopers-world-congress-2026-europe" target="_blank">We Are Developers Berlin</a> - July 8-10
