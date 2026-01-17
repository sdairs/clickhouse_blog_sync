---
title: "September 2025 newsletter"
date: "2025-09-17T13:44:56.683Z"
author: "Mark Needham"
category: "Community"
excerpt: "Welcome to the September 2025 ClickHouse newsletter, which will round up what’s happened in real-time data warehouses over the last month."
---

# September 2025 newsletter

Hello, and welcome to the September 2025 ClickHouse newsletter!

This month, Tom Schreiber explains how `GROUP BY` works at scale, we have a new Parquet reader, Airbyte has built a first-class ClickHouse connector, we learn about Laminar’s "flight recorder for AI", and more!

## Featured community member: Gaurav Sen  {#featured-community-member}

This month's featured community member is Gaurav Sen, Founder at InterviewReady.

![0_september_nl.png](https://clickhouse.com/uploads/0_september_nl_8aa81341a9.png)

Gaurav Sen is a software engineer and educator with over 650,000 YouTube subscribers, known for making complex system design concepts accessible to developers worldwide. With engineering experience at Uber, DirectI, and Morgan Stanley, he brings real-world expertise in building large-scale distributed systems and real-time analytics platforms.

Gaurav recently created popular videos walking through ClickHouse’s <a href="https://www.youtube.com/shorts/ErAqfaa9pgc" target="_blank">OpenAI</a> and <a href="https://www.youtube.com/shorts/zyYGhuYzbYY" target="_blank">Tesla</a> use cases. His videos help developers understand how ClickHouse can solve complex analytical problems, making advanced data engineering concepts approachable for his broad audience of software engineers and system designers.

➡️ <a href="https://www.linkedin.com/in/gkcs/" target="_blank">Follow Gaurav on LinkedIn</a>

## Upcoming events {#upcoming-events}

### Open House Roadshow

In case you missed the ClickHouse Open House conference back in May, we’re taking it on tour! We’ll visit four cities in October and hope to see some of you there.

Each event will include keynotes, deep-dive talks, live demos, and AMAs with ClickHouse creators, builders, and users, as well as the opportunity to network with the ClickHouse community.

* <a href="https://clickhouse.com/company/events/202510-sydney-open-house" target="_blank">Sydney User Conference</a> - October 2
* <a href="https://clickhouse.com/company/events/202510-nyc-open-house" target="_blank">NYC User Conference</a> - October 6
* <a href="https://clickhouse.com/company/events/202510-bangalore-open-house" target="_blank">Bangalore User Conference</a> - October 7
* <a href="https://clickhouse.com/company/events/202510-amsterdam-open-house" target="_blank">Amsterdam User Conference</a> - October 27

### Global events

* <a href="https://clickhouse.com/company/events/v25-9-community-release-call" target="_blank">v25.9 Community Call</a> - September 25
* <a href="https://clickhouse.com/company/events/introducing-clickstack-apj" target="_blank">Introducing ClickStack: The Future of Observability on ClickHouse</a> - September 23

### Virtual training

* <a href="https://clickhouse.com/company/events/202509-emea-clickhouse-deep-dive-part1" target="_blank">ClickHouse Deep Dive Part 1</a> - September 24
* <a href="https://clickhouse.com/company/events/202510-EMEA-Observability-at-Scale-with-ClickStack" target="_blank">Observability at Scale with ClickStack</a> - October 1
* <a href="https://clickhouse.com/company/events/202510-APJ-Observability-at-Scale-with-ClickStack" target="_blank">Observability at Scale with ClickStack</a> - October 14

### Events in AMER

* <a href="https://clickhouse.com/company/events/202509-amer-bo-meetup" target="_blank">Boston ClickHouse Meetup</a> - September 19
* <a href="https://clickhouse.com/company/events/denver56" target="_blank">Denver Meetup</a> - September 22
* <a href="https://lu.ma/hbt7ahud" target="_blank">Iceberg Bay Area Meetup</a> - October 1
* <a href="https://clickhouse.com/company/events/Aimeetupseattle" target="_blank">Seattle AI Meetup</a> - October 2
* <a href="https://clickhouse.com/company/events/202510-nyc-clickhouse-deep-dive-part1" target="_blank">ClickHouse Deep Dive Part 1 - In-Person Training (New York)</a> - October 7
* <a href="https://clickhouse.com/company/events/202511-in-person-Atlanta-Observability-at-Scale-ClickStack" target="_blank">Atlanta In-Person Training - Observability at Scale with ClickStack</a> - November 10

### Events in EMEA

* <a href="https://www.bigdataldn.com/" target="_blank">BigData London</a> - September 24-25
* <a href="https://amsterdam.pydata.org/" target="_blank">PyData Amsterdam</a> - September 24-25
* <a href="https://aws.amazon.com/events/cloud-days/" target="_blank">AWS Cloud Day Riyadh</a>, September 29
* <a href="https://clickhouse.com/company/events/202509-EMEA-Madrid-meetup" target="_blank">ClickHouse Meetup in Madrid</a> - September 30
* <a href="https://clickhouse.com/company/events/202509-EMEA-KSA-RoundTable" target="_blank">Meet The ClickHouse Team: "Real-Time Data & AI: Best Practices with AWS & ClickHouse"</a> (Riyadh, Kingdom of Saudi Arabia) - September 30
* <a href="https://clickhouse.com/company/events/202509-EMEA-Madrid-meetup" target="_blank">ClickHouse Meetup in Madrid</a> - September 30
* <a href="https://clickhouse.com/company/events/202510-EMEA-Barcelona-meetup" target="_blank">ClickHouse Meetup in Barcelona</a> - October 1
* <a href="https://www.bigdataparis.com/en-gb.html#/" target="_blank">BigData Paris</a> - October 1-2
* <a href="https://clickhouse.com/company/events/AI-ClimateTechPanel-Amsterdam" target="_blank">AI in ClimateTech Panel - Amsterdam C-Level Meetup</a> - October 7
* <a href="https://www.usenix.org/conference/srecon25emea" target="_blank">SRE Con Dublin</a> - October 7-9
* <a href="https://clickhouse.com/company/events/202510-EMEA-Zurich-meetup" target="_blank">ClickHouse Meetup in Zürich</a> - October 9
* <a href="https://www.gitex.com/" target="_blank">Gitex Dubai</a> - October 13-17
* <a href="https://clickhouse.com/company/events/202510-EMEA-London-meetup" target="_blank">ClickHouse Meetup in London</a> - October 15
* <a href="https://awscommunity.eu/" target="_blank">AWS Community Day Budapest</a> - October 16
* <a href="https://clickhouse.com/company/events/202510-amsterdam-open-house" target="_blank">Amsterdam User Conference</a> - October 28
* <a href="https://clickhouse.com/company/events/202510-in-person-clickhouse-deep-dive-part-1" target="_blank">ClickHouse Deep Dive Part 1 In-Person Training</a> (Amsterdam) - October 28
* <a href="https://www.techshowmadrid.es/en/big-data-ai-world" target="_blank">BigData & AI World Madrid</a>  - October 29-30
* <a href="https://www.gartner.com/en/conferences/emea/symposium-spain" target="_blank">Gartner IT Barcelona</a> - November 10-13
* <a href="https://clickhouse.com/company/events/202511-EMEA-Cyprus-meetup" target="_blank">ClickHouse Meetup in Cyprus</a> - November 20

### Events in APAC

* <a href="https://clickhouse.com/company/events/202509-apj-beijing-meetup" target="_blank">ClickHouse Beijing Meetup</a> - September 20
* <a href="https://clickhouse.com/company/events/202509-apj-pune-meetup" target="_blank">ClickHouse Pune Meetup</a> - September 20
* <a href="https://forefrontevents.co/event/data-ai-summit-singapore-2025/" target="_blank">Data & AI Summit Singapore</a> - September 24
* <a href="https://clickhouse.com/company/events/202509-apj-singapore-meetup" target="_blank">ClickHouse Singapore Meetup</a> - September 25
* <a href="https://clickhouse.com/company/events/202509-apj-melbourne-meetup" target="_blank">ClickHouse Melbourne Meetup</a> - September 30
* <a href="https://clickhouse.com/company/events/2025-09-APJ-tokyo-meetup" target="_blank">ClickHouse (クリックハウス) Tokyo Meetup</a> - September 30
* <a href="https://clickhouse.com/company/events/202509-apj-clickhouse-fundamentals" target="_blank">ClickHouse Fundamentals</a> (Tokyo, Japan) - September 30
* <a href="https://clickhouse.com/company/events/202510-sydney-clickhouse-deep-dive-part1" target="_blank">Sydney In-person Training - ClickHouse Deep Dive Part 1</a> - October 2
* <a href="https://clickhouse.com/company/events/202510-bangalore-clickhouse-deep-dive-part1" target="_blank">Bangalore In-person Training - ClickHouse Deep Dive Part 1</a> - October 7

## 25.8 release  {#release}

![6_september_nl.png](https://clickhouse.com/uploads/6_september_nl_d860f4e5b9.png)

The most exciting feature in the 25.8 release is the new native Parquet reader, which has page-level parallelism and `PREWHERE` pushdown. It delivers 1.8x faster performance while scanning 99.98% less data.

ClickHouse can also write data with Hive-style partitioning, has Arrow Flight integration, and even better Data Lake support.

➡️ <a href="https://clickhouse.com/blog/clickhouse-release-25-08" target="_blank">Read the release post</a>

## Clickhouse Spotlight: How Airbyte built a first-class destination connector  {#airbyte}

![2_september_nl.png](https://clickhouse.com/uploads/2_september_nl_715ef080a6.png)

Airbyte recently released a new first-class ClickHouse destination connector that delivers over 3× improved performance, supports single-sync loads of datasets larger than 1 TB, and preserves correct data types for a cleaner, more structured load.

➡️ <a href="https://airbyte.com/blog/clickhouse-destination-connector" target="_blank">Read the blog post</a>

## 4 common ClickHouse mistakes (and how to fix them)   {#4-clickhouse-mistakes}

![3_september_nl.png](https://clickhouse.com/uploads/3_september_nl_6e75f98dc0.png)

Nimrod Kir'on highlights four common mistakes that can trip up new ClickHouse users - from mis-tuned setups to schema design choices - and offers practical advice to get started on the right foot.

➡️ <a href="https://engineering.lsports.eu/getting-started-with-clickhouse-4-big-mistakes-any-novice-might-be-doing-when-they-start-working-d7f3b2fe1c59" target="_blank">Read the blog post</a>

## How Laminar is using ClickHouse to reimagine observability for AI browser agents   {#laminar}

![4_september_nl.png](https://clickhouse.com/uploads/4_september_nl_fb8d8a248c.png)

Laminar built a "flight recorder for AI" that captures what browser agents see and do - tackling <a href="https://clickhouse.com/engineering-resources/observability" target="_blank">observability</a> for one of the hottest areas in AI development today. It uses ClickHouse Cloud to transform billions of DOM events into instant video-like replays, making debugging AI agents as simple as watching YouTube.

➡️ <a href="https://clickhouse.com/blog/how-laminar-reimagined-observability-for-ai-browser-agents" target="_blank">Read the blog post</a>

## Scaling GROUP BY to 8,900+ cores: The engineering behind ultra-fast aggregations in ClickHouse   {#scaling-group-by}

![5_september_nl.png](https://clickhouse.com/uploads/5_september_nl_44176bc952.png)

It's time for another Tom Schreiber deep dive! This time, Tom explores ClickHouse's parallel replicas feature and how it scales GROUP BY operations across thousands of cores.

In his latest technical breakdown, Tom demonstrates how ClickHouse processes 100 billion rows in just 414 milliseconds—about the time it takes to snap your fingers, by leveraging mergeable partial aggregation states that enable elastic scaling across thousands of cores

➡️ <a href="https://clickhouse.com/blog/clickhouse-group-by-parallel-replicas-8900-cores" target="_blank">Read the blog post</a>

## Quick reads   {#quick-reads}

* Igor Gorbenko shows how you can combine CatBoost, open accident datasets, and ClickHouse <a href="https://python.plainenglish.io/how-we-built-a-route-safety-engine-using-catboost-open-data-and-clickhouse-5f39a046b222" target="_blank">to power a “route safety engine”</a> that evaluates risk across a journey and suggests safer paths, not just faster ones.
* Himnish Hunma <a href="https://klaviyo.tech/one-more-abstraction-ca8b1761cb6d" target="_blank">explores how Klaviyo uses ClickHouse under the hood</a>, and why adding “one more abstraction” unlocked the flexibility needed to scale their real-time analytics.
* Benjamin Wootton argues that <a href="https://benjaminwootton.com/insights/clickhouse-cloud-simplifies-data-stack" target="_blank">ClickHouse Cloud lets teams collapse entire modern data stacks into one powerful engine</a>, eliminating multiple systems, cutting down on ETL, reducing redundancy, and delivering fresh analytics from raw data without sacrificing performance.
* Our very own Mike Shi was <a href="https://horovits.medium.com/clickstack-clickhouses-new-observability-stack-unveiled-73f129a179a3" target="_blank">invited to the OpenObservability Talks podcast</a> to talk about ClickStack, the open-source observability stack we introduced just a few months ago that unifies logs, metrics, traces, and session replay.
* Liza Katz <a href="https://medium.com/@lizka.k/nuances-of-using-clickhouse-polygon-dictionaries-3beb561e8ba7" target="_blank">dives into the subtleties of using polygon dictionaries in ClickHouse</a>,  unpacking how overlapping shapes, key layouts, and lookup semantics can catch you off guard unless you're aware of the gotchas.
