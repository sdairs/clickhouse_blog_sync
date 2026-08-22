---
title: "August 2026 newsletter"
date: "2026-08-21T09:12:10.505Z"
author: "Mark Needham"
category: "Community"
excerpt: "Welcome to the August 2026 ClickHouse newsletter, which will round up what’s happened in real-time data warehouses over the last month."
---

# August 2026 newsletter

A new database research lab, an interactive playground for over 100 databases, and our biggest release post ever - it’s just your average month in the world of ClickHouse!

In this issue, meet Andy Pavlo, the newest member of the ClickHouse team, learn about what’s new in 26.7, and catch up on the latest in ClickHouse Managed Postgres, observability, vector search, and more.

And don’t forget to register for the Open House Roadshow, which is visiting six cities over the next six weeks.

## Featured community member: Manuel Raimann {#featured-community-member}

This month's featured community member is Manuel Raimann, Head of Engineering at Redact.dev.

![](https://clickhouse.com/uploads/aug2026_nl_image2_da6d187c72.png)

Manuel contributed a series of performance improvements in the recent ClickHouse 26.7 release. His work sped up wide-integer comparisons by up to 7×, Delta decompression by up to 5×, and statistical and bitwise aggregates by up to 4×. He also made numeric array operations and primary-key index filtering faster.

Apart from contributing to ClickHouse, he also contributes to the open-source <a href="https://github.com/deadlock-api" target="_blank">Deadlock API</a>, which provides game data and analytics for Deadlock, Valve’s upcoming game combining third-person shooting with MOBA-style gameplay.

➡️ <a href="https://www.linkedin.com/in/manuel-raimann/" target="_blank">Connect with Manuel on LinkedIn</a>

## Open House Roadshow {#open-house-roadshow}

The <a href="https://clickhouse.com/company/events?category=Open+House" target="_blank">Open House Roadshow</a> continues, with visits to <a href="https://clickhouse.com/openhouse/amsterdam-2026" target="_blank">Amsterdam</a> (Sep 1), <a href="https://clickhouse.com/openhouse/singapore-2026" target="_blank">Singapore</a> (Sep 24), and <a href="https://clickhouse.com/openhouse/london-2026" target="_blank">London</a> (Sep 30).

Each stop will feature talks from both ClickHouse employees and customers, as well as optional training workshops.

We’ll also be visiting New York City, Bangalore, and Munich.

➡️ <a href="https://clickhouse.com/company/events?category=Open+House" target="_blank">See all Open House locations</a>

## 26.7 release {#clickhouse-release-26-7}

![](https://clickhouse.com/uploads/aug2026_nl_image3_8a04d0e120.png)

The 26.7 release blog post is our longest one yet. While there is certainly value in brevity, we’re going to let ourselves off this time because there were so many features that we needed to tell you about!

As always, we have join optimizations. The hash join algorithm has been made more efficient by reducing the probe-side input and shrinking build-side hash tables. ClickHouse will now also automatically choose how to arrange joins in a multi-table query.

Text indexes now store token positions, a feature that’s needed for efficient phrase search. We tested it on a Hacker News dataset, and a query for the phrase `"Google web search"` was 40 times faster.

The EXPLAIN clause has a new member: `EXPLAIN ANALYZE`, which runs every query-processing phase before discarding the result rows and annotating the logical execution-plan tree with measurements collected during actual execution.

That’s just a brief taster - we’ll let you read the blog post to find out the rest!

➡️ <a href="https://clickhouse.com/blog/clickhouse-release-26-07" target="_blank">Read the release post</a>

## Andy Pavlo joins ClickHouse to establish ClickHouse Labs {#andy-pavlo-clickhouse-labs}

![](https://clickhouse.com/uploads/aug2026_nl_image4_a677393785.png)

The news of the month (and maybe the year?!) is that Andy Pavlo is joining ClickHouse to establish ClickHouse Labs. Andy was previously a professor in the Computer Science Department at Carnegie Mellon University since 2013.

ClickHouse Labs is an applied research lab that will conduct scientifically valuable research and then help transform the best ideas into technology that matters to users.

In addition to developing ideas to improve ClickHouse, the lab will work with the ClickHouse PostgreSQL team to help establish its managed service as a market leader in performance and reliability.

➡️ <a href="https://clickhouse.com/blog/andy-pavlo-joins-clickhouse" target="_blank">Read the blog post</a>

## Your TTL is working. That might be the problem. {#ttl-working-problem}

![](https://clickhouse.com/uploads/aug2026_nl_image5_d9dfb8de97.png)

Amrelboridy’s disk kept filling up, but there wasn’t any indication why. There weren’t any orphaned or detached parts, and data retention was healthy.

In this blog post, Amrelboridy explains what happens in ClickHouse when a row’s Time To Live (TTL) expires and how configuring the partition key can save you a lot of headaches.

➡️ <a href="https://medium.com/@amrelboridy7/your-ttl-is-working-that-might-be-the-problem-3ed30cdb1492" target="_blank">Read the blog post</a>

## Alexey created a playground for 110 database systems {#clickbench-playground}

![](https://clickhouse.com/uploads/aug2026_nl_image6_9f76946ede.png)

Alexey has extended ClickBench, a benchmark for analytical databases, to include <a href="https://benchmark.clickhouse.com/playground" target="_blank">an interactive playground</a> where you can run ad hoc queries on the 100m-record ClickBench dataset against over 100 database systems.

The playground runs on Firecracker microVMs on an AWS EC2 instance, and in the blog post, Alexey explains why this was the only approach that provided strong isolation, reasonable cost, and fast startup.

➡️ <a href="https://clickhouse.com/blog/clickbench-playground" target="_blank">Read the blog post</a>

## Postgres vs ClickHouse is the wrong question. I use both. {#postgres-clickhouse-use-both}

![](https://clickhouse.com/uploads/aug2026_nl_image7_6b7745d2de.png)

Artem Senenko explains that “Postgres vs ClickHouse” is the wrong question because the databases solve different problems.

He uses Postgres for mutable data, such as monitors, incidents, teams, and configuration. But the continuously growing stream of immutable check results goes into ClickHouse for efficient storage and fast analytical queries.

The majority of the blog post focuses on ways to optimize ClickHouse, including compression codecs, tenant-aware sort keys, per-row retention periods, and materialized views that pre-aggregate data for dashboards.

➡️ <a href="https://dev.to/slima4/postgres-vs-clickhouse-i-use-both-4-tricks-from-the-split-4420" target="_blank">Read the blog post</a>

## What's new in ClickHouse Managed Postgres: Customer notifications, better observability, faster backups, extensions, and more {#managed-postgres-updates}

![](https://clickhouse.com/uploads/aug2026_nl_image8_83db185c09.jpg)

In the latest issue of What’s New in ClickHouse Managed Postgres, we introduce a smoother onboarding experience, proactive storage notifications, richer observability, and faster, more predictable backups for databases larger than 10 TB.

We’ve also expanded the extension ecosystem: pg_re2 makes regular-expression queries up to 9× faster, while improvements to pg_clickhouse and pg_stat_ch enable more efficient analytics and query monitoring across Postgres and ClickHouse.

➡️ <a href="https://clickhouse.com/blog/managed-postgres-notifications-observability-backups" target="_blank">Read the blog post</a>

## How we build and evaluate our MCP server for SRE agents {#clickstack-mcp-server-evals}

![](https://clickhouse.com/uploads/aug2026_nl_image9_ea46a1d641.jpg)

Brandon Pereira explains how the ClickStack team built hdx-evals, an open-source framework for measuring the reliability of AI agents' investigations into production incidents.

Across five reproducible scenarios containing millions of synthetic logs and spans, the purpose-built ClickStack MCP server scored 7–20 percentage points higher than giving agents direct SQL access through the ClickHouse MCP server.

Brandon also explores how tool schemas, response design, actionable errors, and query speed influence agent accuracy and consistency.

➡️ <a href="https://clickhouse.com/blog/benchmarking-the-clickstack-mcp-server-with-hdx-evals" target="_blank">Read the blog post</a>

## Quick reads {#quick-reads}

* Kaushik Iska explains <a href="https://clickhouse.com/blog/wal-backpressure-clickhouse-managed-postgres" target="_blank">how ClickHouse Managed Postgres uses tiered, WAL-aware write throttling</a> to slow clients before an archiving backlog fills the disk, giving the archiver time to recover before automatically restoring full throughput.
* Arsad Tanzim <a href="https://medium.com/@arsadtanzim/i-tried-replacing-my-logs-metrics-and-traces-stack-with-just-clickhouse-1dbbaa69d083" target="_blank">builds a ClickHouse, OpenTelemetry, and Grafana prototype</a> to unify logs, metrics, and traces in one SQL-queryable backend.
* Mohamed Hussain S <a href="https://medium.com/stackademic/can-clickhouse-replace-a-vector-database-i-actually-tested-it-9f0c54f2b036" target="_blank">tests ClickHouse vector search</a> and finds it can replace a dedicated vector database when embeddings sit alongside analytical data, while vector-only workloads with constant high-frequency writes favor a purpose-built system.
* Jordan Simonovski <a href="https://clickhouse.com/blog/espresso-machine-observability-with-otel" target="_blank">turns a Gaggia espresso machine into an OpenTelemetry-instrumented system</a>, streaming ESP32 and household sensor data into ClickStack and using an LLM agent to turn each shot into actionable brewing advice.

---

## Get started today

Interested in seeing how ClickHouse works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-1616-get-started-today-sign-up&utm_blogctaid=1616)

---

## Upcoming events {#upcoming-events}

### Global virtual events

* <a href="https://clickhouse.com/company/events/202608-APJ-PostgreSQL-ClickHouse-Better-Together" target="_blank">PostgreSQL and ClickHouse, Better Together</a> - Aug 25, 2026
* <a href="https://clickhouse.com/company/events/202608-AMER-Webinar-Data-Architecture-Zappi" target="_blank">Data Architecture Blueprints featuring Zappi</a> - Aug 26, 2026
* <a href="https://clickhouse.com/company/events/webinar-managed-postgres-korea-sept17" target="_blank">ClickHouse Managed Postgres 소개: pg_clickhouse로 구현하는 실시간 분석</a> - Sep 17, 2026

### Virtual training

* <a href="https://clickhouse.com/company/events/202609-APJ-query-optimization-workshop" target="_blank">Query Optimization with ClickHouse Workshop</a> - Sep 29, 2026
* <a href="https://clickhouse.com/company/events/202610-APJ-Real-time-Analytics-ClickHouse-Level1" target="_blank">Real-time Analytics with ClickHouse: Level 1</a> - Oct 20, 2026
* <a href="https://clickhouse.com/company/events/202610-APJ-Real-time-Analytics-ClickHouse-Level2" target="_blank">Real-time Analytics with ClickHouse: Level 2</a> - Oct 21, 2026
* <a href="https://clickhouse.com/company/events/202610-APJ-Real-time-Analytics-ClickHouse-Level3" target="_blank">Real-time Analytics with ClickHouse: Level 3</a> - Oct 22, 2026

### Events in AMER

* <a href="https://www.premierleague.com/en/coast-to-coast" target="_blank">Fulham Football Club Premier League Watch Party</a> - Atlanta - Aug 24, 2026
* <a href="https://clickhouse.com/company/events/vancouver202608" target="_blank">Vancouver Data Engineering Meetup</a> - Aug 25, 2026
* <a href="https://clickhouse.com/company/events/sfhackathon202608" target="_blank">Better Days: A Hackathon — San Francisco</a> - Aug 28, 2026
* <a href="https://clickhouse.com/company/events/boston202608" target="_blank">The Boston Data Party Trivia Night</a> - Aug 31, 2026
* <a href="https://aws.amazon.com/pt/events/summits/sao-paulo/" target="_blank">AWS Summit Sao Paulo</a> - Sep 3, 2026
* <a href="https://santiago.devopsdayschile.cl/" target="_blank">DevOpsDays Santiago</a> - Sep 8-9, 2026
* <a href="https://clickhouse.com/openhouse/nyc-2026" target="_blank">Open House Roadshow New York</a> - Sep 10
* <a href="https://luma.com/clickh-nw1d" target="_blank">Hands-on training: Building agents with ClickHouse and LibreChat — Boston</a> - Sep 14
* <a href="https://www.astronomer.io/events/orchestrate-everything" target="_blank">Astronomer Orchestrate Everything</a> - Sep 16, 2026
* <a href="https://www.getdbt.com/dbt-summit" target="_blank">dbt Summit</a> - Las Vegas - Sep 15-18, 2026
* <a href="https://allinevent.ai/?gad_source=1&gad_campaignid=24065615896&gbraid=0AAAAAp4XQCYgxFpav8IvuXLwsDHGQpEiq&gclid=Cj0KCQjw4orUBhCjARIsAIbF3qzRbNKwlsUJ6yDn3TyEUeV8urkw3OP-QTs3Ck4QITsdJM9ru-JrEk0aAoweEALw_wcB" target="_blank">All In Conference</a> - Montreal - Sep 16-17, 2026
* <a href="https://luma.com/clickh-wavw" target="_blank">Rows and Columns summit San Francisco</a> - Sep 22nd
* <a href="https://cloudonair.withgoogle.com/events/google-cloud-summit-brasil-2026-1" target="_blank">Google Cloud Summit Brasil</a> - Sep 23-24, 2026
* <a href="https://runway.runreveal.com/" target="_blank">Runway by RunReveal</a> - San Francisco - Sep 29, 2026
* <a href="https://coreweave.com/fully-connected-2026" target="_blank">CoreWeave Fully Connected</a> - San Francisco - Sep 29 - Oct 2, 2026

### Events in EMEA

* <a href="https://clickhouse.com/company/events/202609-EMEA-Amsterdam-AI-Agents-w-Langfuse" target="_blank">Amsterdam In-person training - From 0 to Production: Observing and Improving AI Agents with Langfuse</a> - Sep 1, 2026
* <a href="https://clickhouse.com/company/events/202609-EMEA-Amsterdam-One-Database-Every-Workload" target="_blank">Amsterdam In-person training - One Database, Every Workload: A ClickHouse Workshop</a> - Sep 1, 2026
* <a href="https://clickhouse.com/company/events/202609-amsterdam-open-house" target="_blank">Open House Roadshow Amsterdam</a> - Sep 1, 2026
* <a href="https://clickhouse.com/company/events/202609-EMEA-DACH-Germany-Berlin-The-Agentic-Data-Stack" target="_blank">The Agentic Data Stack, Berlin</a> - Sep 2, 2026
* <a href="https://aws.amazon.com/events/summits/tel-aviv/" target="_blank">AWS Summit Tel Aviv</a> - Sept 10, 2026
* <a href="https://techracesummit.com/" target="_blank">Tech Race Warsaw</a> - Sept 10, 2026
* <a href="https://clickhouse.com/company/events/202609-EMEA-UKI-Roundtable-AgenticLLMStack" target="_blank">The Agentic Data Stack</a> - London - Sep 11, 2026
* <a href="https://clickhouse.com/company/events/ai-builders-and-databases-sep-amsterdam-2026" target="_blank">ClickHouse Amsterdam Meetup @ Adyen</a> - Sep 15, 2026
* <a href="https://clickhouse.com/company/events/ai-builders-and-databases-sep-cape-town-2026" target="_blank">AI Builders and Databases Happy Hour Cape Town</a> - Sep 15, 2026
* BigData Paris
* <a href="https://clickhouse.com/company/events/202609-EMEA-France-Paris-The-Agentic-Data-Stack" target="_blank">The Agentic Data Stack - Paris</a> - Sep 17, 2026
* <a href="https://clickhouse.com/company/events/202609-EMEA-DACH-Zurich-The-Agentic-Data-Stack" target="_blank">The Agentic Data Stack - Zurich</a> - Sep 17, 2026
* IDC Madrid - Sept 22, 2026
* AI Engineer Paris (Langfuse) - Sept 22-24, 2026
* <a href="https://clickhouse.com/company/events/202609-EMEA-Stockholm-Real-time-Analytics-w-ClickHouse" target="_blank">Stockholm In-Person Training: Real-time Analytics with ClickHouse</a> - Sep 23, 2026
* <a href="https://luma.com/p7td11mb" target="_blank">AI Builders and Databases Barcelona</a> - Sep 23, 2026
* BigDataLondon - Sept 23-24, 2026
* FabCON - Sept 28 - Oct 1
* <a href="https://clickhouse.com/company/events/ai-builders-and-databases-sep-paris-2026" target="_blank">AI Builders and Databases Paris</a> - Sep 29, 2026
* <a href="https://www.agenticaiforum.net/" target="_blank">Agentic AI Forum Dubai</a> - Sept 30, 2026
* <a href="https://clickhouse.com/company/events/202609-EMEA-London-AI-Agents-w-Langfuse" target="_blank">London In-person training - From 0 to Production: Observing and Improving AI Agents with Langfuse</a> - Sep 30, 2026
* <a href="https://clickhouse.com/company/events/202609-EMEA-London-One-Database-Every-Workload" target="_blank">London In-person training - One Database, Every Workload: A ClickHouse Workshop</a> - Sep 30, 2026
* <a href="https://clickhouse.com/openhouse/london-2026" target="_blank">Open House Roadshow London</a> - Sep 30, 2026
* <a href="https://clickhouse.com/company/events/202610-EMEA-Munich-AI-Agents-w-Langfuse" target="_blank">Munich In-person training - From 0 to Production: Observing and Improving AI Agents with Langfuse</a> - Oct 6, 2026
* <a href="https://clickhouse.com/company/events/202610-EMEA-Munich-One-Database-Every-Workload" target="_blank">Munich In-person training - One Database, Every Workload: A ClickHouse Workshop</a> - Oct 6, 2026
* <a href="https://clickhouse.com/company/events/202610-munich-open-house" target="_blank">Open House Roadshow Munich</a> - Oct 6, 2026
* <a href="https://worldsummit.ai/" target="_blank">World Summit AI Amsterdam</a> - Oct 7-8, 2026
* <a href="https://clickhouse.com/company/events/ai-builders-and-databases-oct-stockholm-2026" target="_blank">AI Builders and Databases Stockholm</a> - Oct 8, 2026
* <a href="https://clickhouse.com/company/events/ai-builders-and-databases-oct-tel-aviv-2026" target="_blank">AI Builders and Databases Tel Aviv</a> - Oct 12, 2026
* <a href="https://luma.com/clickh-6n6u" target="_blank">SRECon Dublin Happy Hour by the Quay</a> - Oct 13, 2026
* <a href="https://www.usenix.org/conference/srecon25emea" target="_blank">SRECon Dublin</a> - Oct 13-15, 2026
* <a href="https://datainnovationsummit.com/region/mea/" target="_blank">Data Innovation Summit Dubai</a> Oct 14-15
* <a href="https://clickhouse.com/company/events/202610-EMEA-Oslo-Real-time-Analytics-w-ClickHouse" target="_blank">Oslo In-Person Training: Real-time Analytics with ClickHouse</a> - Oct 14, 2026
* PostgreSQL Conference Europe - Oct 20-23, 2026
* <a href="https://aws.amazon.com/events/cloud-days/riyadh/" target="_blank">AWS Cloud Days Riyadh</a> - Oct 21, 2026
* <a href="https://clickhouse.com/company/events/202610-EMEA-London-Real-time-Analytics-w-ClickHouse" target="_blank">London In-Person Training: Real-time Analytics with ClickHouse</a> - Oct 21, 2026
* <a href="https://clickhouse.com/company/events/ai-builders-and-analytics-oct-london-2026" target="_blank">AI Builders and Analytics London</a> - Oct 21, 2026
* <a href="https://luma.com/clickh-vtzf" target="_blank">AI Builders and Databases Dubai</a> - Oct 22, 2026
* Battle of the Quants London - Oct 22, 2026
* <a href="https://clickhouse.com/company/events/202610-EMEA-Dublin-Real-time-Analytics-w-ClickHouse" target="_blank">Dublin In-Person Training: Real-time Analytics with ClickHouse</a> - Oct 23, 2026
* <a href="https://luma.com/clickh-1qqg" target="_blank">AI Builders and Databases Madrid</a> - Nov 3, 2026
* <a href="https://clickhouse.com/company/events/ai-builders-and-databases-nov-cyprus-2026" target="_blank">AI Builders and Databases Cyprus</a> - Limassol - Nov 26, 2026

### Events in APAC

* <a href="https://clickhouse.com/company/events/ch-mel-meetup-26aug26" target="_blank">ClickHouse Melbourne Meetup - Aug 2026</a> - Aug 26, 2026
* <a href="https://clickhouse.com/company/events/ch-bkk-meetup-01sep26" target="_blank">NEOZO AI Meetup × ClickHouse: How Modern Data Platforms Power AI</a> - Bangkok - Sep 1, 2026
* <a href="https://clickhouse.com/company/events/202609-APJ-India-Bangalore-Open-House-Roadshow" target="_blank">Open House Roadshow Bangalore</a> - Sep 22, 2026
* <a href="https://clickhouse.com/company/events/202609-APJ-ASEAN-Singapore-Open-House-Roadshow" target="_blank">Open House Roadshow Singapore</a> - Sep 24, 2026
