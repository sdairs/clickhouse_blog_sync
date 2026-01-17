---
title: "February 2025 Newsletter"
date: "2025-02-20T04:54:13.924Z"
author: "Mark Needham"
category: "Community"
excerpt: "Welcome to the February ClickHouse newsletter, which will round up what’s happened in real-time data warehouses over the last month."
---

# February 2025 Newsletter

Well, January went by quickly, didn’t it?! That means it must be time for our second newsletter of 2025.

This month's big news is the launch of JSONBench, a benchmark suite for JSON analytics. Ryadh Dahimene tells us about agent-facing analytics, Shahar Gvirtz explains why he likes ClickHouse, Tom Schreiber dives into the join improvements in 25.1, and more.

## Featured community member: Chris Lawrence

This month's featured community member is Chris Lawrence, Dev Lead and Senior Software Engineer at <a href="https://www.linkedin.com/company/use-amp/" target="_blank">AMP</a>.

![1_newsletter202502.png](https://clickhouse.com/uploads/1_newsletter202502_4f144a0657.png)

Chris previously co-founded ReSync Digital, successfully launching over 30 products for early-stage startups, and has experience in machine vision and IoT solutions through his work with Skip-Line, LLC.

Chris Lawrence <a href="https://clickhouse.com/videos/amp-from-batch-processing-to-streaming" target="_blank">spoke at the ClickHouse meetup in Melbourne in August 2024</a>. He shared how AMP’s implementation of ClickHouse Cloud has helped them transform their data pipeline from batch processing to real-time streaming, improving their analytics platform's speed and reliability. Chris also elaborated on his talk in <a href="https://clickhouse.com/blog/amp-clickhouse-oss-to-clickhouse-cloud" target="_blank">a recent blog post</a>.

➡️ <a href="https://www.linkedin.com/in/chrislawrence121/" target="_blank">Follow Chris on LinkedIn</a>

## Upcoming events

### Global events

* <a href="https://clickhouse.com/company/events/v25-2-community-release-call" target="_blank">v25.2 Community Call</a> - Feb 27

### Free training

* <a href="https://clickhouse.com/company/events/clickhouse-fundamentals" target="_blank">ClickHouse Fundamentals</a> - Feb 26 and Mar 19
* <a href="https://clickhouse.com/company/events/202503-emea-paris-inperson-clickhousetraining" target="_blank">Formation ClickHouse en présentiel</a>, Paris - Mar 4
* <a href="https://clickhouse.com/company/events/202503-amer-seattle-inperson-developer-fast-track" target="_blank">In-Person ClickHouse Developer Fast Track - Seattle</a> - Mar 5
* <a href="https://clickhouse.com/company/events/202503-emea-query-optimization" target="_blank">ClickHouse Query Optimization Workshop</a> - Mar 12
* <a href="https://clickhouse.com/company/events/202503-amer-clickhouse-admin-workshop" target="_blank">ClickHouse Admin Workshop</a> - Mar 12
* <a href="https://clickhouse.com/company/events/202503-apj-sydney-inperson-clickhouse-developer" target="_blank">In-Person ClickHouse Developer - Sydney</a> - Mar 24-25
* <a href="https://clickhouse.com/company/events/202503-apj-melbourne-inperson-clickhouse-developer" target="_blank">In-Person ClickHouse Developer - Melbourne</a> - Mar 27-28
* <a href="https://clickhouse.com/company/events/202504-apj-bangalore-inperson-developer-fast-track" target="_blank">In-Person ClickHouse Developer Fast Track - Bangalore</a> - Apr 1

### Events in AMER

* <a href="https://www.meetup.com/clickhouse-los-angeles-user-group/events/305952193/?slug=clickhouse-los-angeles-user-group&isFirstPublish=true" target="_blank">Clickhouse Meetup with LA DevOps</a> - Feb 20
* <a href="https://www.meetup.com/clickhouse-seattle-user-group/events/305916325/?eventOrigin=your_events" target="_blank">ClickHouse Meetup in Seattle</a> - Mar 5
* <a href="https://clickhouse.com/company/events/2025-03-scale-22" target="_blank">Scale 22x</a>, Pasadena - Mar 6 - Mar 9
* <a href="https://clickhouse.com/company/events/03-2025-san-francisco" target="_blank">Game Developers Conference</a>, San Francisco - Mar 17
* <a href="https://www.meetup.com/clickhouse-silicon-valley-meetup-group/events/306046697/?eventOrigin=group_events_list" target="_blank">ClickHouse Meetup @ Cloudflare</a>, San Francisco - Mar 19
* <a href="https://www.meetup.com/clickhouse-boston-user-group/events/305882607/?slug=clickhouse-boston-user-group&eventId=300907870&isFirstPublish=true" target="_blank">ClickHouse Meetup @ Klaviyo</a>, Boston - Mar 25
* <a href="https://www.meetup.com/clickhouse-new-york-user-group/events/305916369/?eventOrigin=group_upcoming_events" target="_blank">ClickHouse Meetup @ Braze</a>, New York - Mar 26
* <a href="https://clickhouse.com/company/events/2025-04-google-next" target="_blank">Google Next</a>, Las Vegas - Apr 9
* <a href="https://clickhouse.com/openhouse" target="_blank">Open House User Conference</a>, San Francisco - May 28

### Events in EMEA

* <a href="https://www.meetup.com/clickhouse-france-user-group/events/305792997/" target="_blank">ClickHouse Meetup @ Nexton</a>, Paris - Mar 4
* <a href="https://clickhouse.com/company/events/04-2025-kubecon-london" target="_blank">KubeCon 2025</a>, London - April 1-4
* <a href="https://clickhouse.com/company/events/04-2025-aws-paris" target="_blank">AWS Summit 2025</a>, Paris - April 9
* <a href="https://clickhouse.com/company/events/2025-04-aws-summit-amsterdam" target="_blank">AWS Summit 2025</a>, Amsterdam - April 16
* <a href="https://clickhouse.com/company/events/04-2025-aws-london" target="_blank">AWS Summit, 2025</a>, London - April 30

### Events in APAC

* <a href="https://www.meetup.com/clickhouse-singapore-meetup-group/events/305917892/" target="_blank">ClickHouse Singapore Meetup</a> - Feb 25
* <a href="https://www.huodongxing.com/event/3794544969111?td=3894807410019" target="_blank">ClickHouse Shanghai Meetup</a>, China- Mar 1
* <a href="https://forefrontevents.co/event/data-ai-summit-nsw-2025/" target="_blank">Data & AI Summit NSW</a>, Australia - Mar 18
* <a href="https://current.confluent.io/bengaluru" target="_blank">Current Bengaluru</a>, India - Mar 19
* <a href="https://www.meetup.com/clickhouse-delhi-user-group/events/306253492/" target="_blank">ClickHouse Delhi Meetup</a>, India - Mar 22
* <a href="https://latencyconf.io/" target="_blank">Latency Conference</a>, Australia - Apr 3-4
* <a href="https://web3.teamz.co.jp/en" target="_blank">TEAMZ Web3/AI Summit</a>, Japan - Apr 16-17

## Introducing JSONBench: The billion docs JSON Challenge vs MongoDB, Elasticsearch, and more

![2_newsletter202502.png](https://clickhouse.com/uploads/2_newsletter202502_fd28c5c96d.png)

The <a href="https://clickhouse.com/blog/202411-newsletter#how-we-built-a-new-powerful-json-data-type-for-clickhouse" target="_blank">November newsletter</a> mentioned the new JSON data type and explained its performance benefits. To test these claims, we developed <a href="https://jsonbench.com/" target="_blank">JSONBench</a>, a benchmark suite for JSON analytics.

Tom Schreiber has published a comprehensive blog post comparing how different databases handle JSON data. The analysis covers performance benchmarks and storage approaches across multiple systems, including ClickHouse, MongoDB, and Elasticsearch.

His findings detail how each database performs with analytical queries on JSON data and explore their underlying JSON storage mechanisms.

➡️ <a href="https://clickhouse.com/blog/json-bench-clickhouse-vs-mongodb-elasticsearch-duckdb-postgresql" target="_blank">Read the blog post</a>

## Shahar Gvirtz: 7 Reasons why I like ClickHouse

It’s always fun to come across a blog post by a community member enjoying their time with ClickHouse!

I won’t go through all of Shahar’s reasons for liking ClickHouse, but I did want to highlight one of the things that he likes, which is an underrated feature of ClickHouse - its ability to compress data. In Shahar’s words:

> Logs stored in ClickHouse take up only 28% of the space they occupy in Elasticsearch.

If you ever need to tell a friend or colleague why you like ClickHouse, you could do worse than point them to this blog post!

➡️ <a href="https://shahargv.medium.com/7-reasons-why-i-like-clickhouse-9cbb11b142d5" target="_blank">Read the blog post</a>

## Agent-Facing Analytics

![3_newsletter202502.png](https://clickhouse.com/uploads/3_newsletter202502_1727daa7b3.png)

Ryadh Dahimene has written a (IMHO) brilliant blog post explaining a new user persona for <a href="https://clickhouse.com/engineering-resources/what-is-real-time-analytics" target="_blank">real-time analytics</a> databases - AI agents!

Ryadh first takes us on a brief tour of AI developments since the launch of ChatGPT in 2022, including the "sense-think-act" loop, the introduction of support for tools by LLMs, and the recent evolution of reasoning models like OpenAI o1 and DeepSeek-R1.

He then explores the role of real-time analytics databases in agentic workflows and introduces the <a href="https://github.com/ClickHouse/mcp-clickhouse/tree/f8cc7e09d71b624691702520a4741e1849b4b4be" target="_blank">ClickHouse MCP Server</a>. This is our implementation of the server side of Anthropic’s Model Context Protocol, which means you can easily converse with a ClickHouse database from the Claude Desktop.

➡️ <a href="https://clickhouse.com/blog/agent-facing-analytics" target="_blank">Read the blog post</a>

## ClickHouse and Cribl: A Powerful Data Ingestion and Analysis Duo

![4_newsletter202502.png](https://clickhouse.com/uploads/4_newsletter202502_08ff7adaee.png)

Cribl Stream is a data processing platform that works with various data sources, including <a href="https://clickhouse.com/engineering-resources/telemetry-data" target="_blank">telemetry data</a>, like logs, metrics, and trace data. It can preprocess, filter, and transform events before forwarding them to destinations, helping optimize storage utilization and query efficiency. Support for ClickHouse was recently added to its list of supported outputs.

David Maislin has written a detailed guide showing how to set up and use this integration. The guide includes step-by-step instructions for creating ClickHouse tables, configuring Cribl Stream destinations, and using Cribl Search to query the data. It also demonstrates how to use ClickHouse alongside Cribl's data processing features, complete with examples using Cribl's Datagen feature to generate test data.

➡️ <a href="https://cribl.io/blog/clickhouse-and-cribl-a-powerful-data-ingestion-and-analysis-duo/" target="_blank">Read the blog post</a>

## ClickHouse Cloud evolution: compute-compute separation, improved autoscaling, and more!

![5_newsletter202502.png](https://clickhouse.com/uploads/5_newsletter202502_24dd703b23.png)

ClickHouse Cloud was built in record time and brought to market in December 2022. Since then, over a thousand companies have onboarded their workloads into our managed service, and every day, they now collectively run 5.5 billion queries, scanning 3.5 quadrillion records on top of 100PB of data!

Over the past two years, we've gained valuable insights from working closely with our users and have significantly evolved our cloud architecture. This blog describes the latest improvements, including <a href="https://clickhouse.com/blog/introducing-warehouses-compute-compute-separation-in-clickhouse-cloud" target="_blank">compute-compute separation</a>, high-performance machine types (<a href="https://clickhouse.com/blog/graviton-boosts-clickhouse-cloud-performance" target="_blank">moving to Graviton in AWS</a>), single-replica services, and more reactive and seamless automatic scaling.

➡️ <a href="https://clickhouse.com/blog/evolution-of-clickhouse-cloud-new-features-superior-performance-tailored-offerings" target="_blank">Read the blog post</a>

## 25.1 release

In the 25.1 release blog post, Tom Schreiber did a deep dive into the improvements made to the parallel hash join algorithm probe phase. If you’re interested in database internals, that’s worth a read.

This release also introduced MinMax indices at the table level, improved the Merge table engine and table function, added auto-increment functionality, and some nice CLI usability improvements.

➡️ <a href="https://clickhouse.com/blog/clickhouse-release-25-01" target="_blank">Read the release post</a>

## Interesting projects

While compiling the newsletter each month, I come across many ClickHouse-based projects, so I thought I’d share some of them this month.

* <a href="https://apitally.io/" target="_blank">apitally.io</a> - An API monitoring and analytics tool for Python / Node.js apps. It helps users understand API usage and performance, spot issues early, and troubleshoot effectively when something goes wrong. The founder mentioned that it uses ClickHouse to store data on a <a href="https://news.ycombinator.com/item?id=42915435" target="_blank">Hacker News thread</a>.
* <a href="https://github.com/Openpanel-dev/openpanel" target="_blank">Openpanel</a> - An open-source alternative to Mixpanel for capturing user behavior across web, mobile apps, and backend services. It uses ClickHouse to store events.
* <a href="https://www.vigilant.run/home" target="_blank">Vigilant</a> - A lightweight tool for managing structured logs. It lets you centralize your logs, search them, and create alerts. It <a href="https://news.ycombinator.com/item?id=42814930" target="_blank">uses ClickHouse under the hood</a>.
* <a href="https://github.com/caioricciuti/ch-ui" target="_blank">CH-UI</a> - A user interface for interacting with the ClickHouse Server. It has syntax highlighting for queries and lets you see visual metrics about your instance.

## Video Corner

* As Benjamin Wootton <a href="https://clickhouse.com/videos/replicating-data-postgres-clickhouse-cloud" target="_blank">demonstrates in this hands-on video</a>, splitting workloads between PostgreSQL for transactions and ClickHouse for analytics is becoming increasingly popular. He walks us through two ways to keep these databases in sync—using the open-source <a href="https://github.com/PeerDB-io/peerdb" target="_blank">PeerDB</a> tool or <a href="https://clickhouse.com/docs/en/integrations/clickpipes/postgres" target="_blank">ClickHouse Cloud's built-in solution</a>.
* I created a video showing <a href="https://clickhouse.com/videos/clickhouse-mcp-server" target="_blank">how to use the recently released ClickHouse MCP server</a>.
* I also created a video showing <a href="https://clickhouse.com/videos/clickhouse-monitoring-dashboard" target="_blank">how to use the built-in monitoring dashboard</a> to debug some common problems.
* Leon Kozlowski from Flock Safety explains how they <a href="https://clickhouse.com/videos/real-time-traffic-analytics-flock-safety" target="_blank">transformed their traffic analytics system from a slow, daily-batch Redshift setup to a real-time solution using ClickHouse</a>. The system handles over a billion ML predictions per day from its network of surveillance cameras.
* Derek Chia and Karthikayan Muthuramalingam <a href="https://clickhouse.com/videos/maximising-analytics-clickhouse-kafka" target="_blank">present a technical overview of integrating ClickHouse with Kafka</a>, showing how these technologies can work together effectively for real-time data processing and analytics. Derek explains ClickHouse's capabilities as an open-source columnar database optimized for analytics, while Karthikayan details Kafka's role as a distributed event streaming platform.

## Post of the month

My favorite post this month was by <a href="https://x.com/JacobWolf" target="_blank">Jacob Wolf</a>, who’s ingesting lots of data into ClickHouse.

![6_newsletter202502.png](https://clickhouse.com/uploads/6_newsletter202502_1b466bad33.png)

➡️ <a href="https://x.com/JacobWolf/status/1884316267093582231" target="_blank">Read the post</a>
