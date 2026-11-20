---
title: "November 2026 newsletter"
date: "2026-11-20T09:50:28.361Z"
author: "Mark Needham"
category: "Community"
excerpt: "The November ClickHouse newsletter brings four major platform launches, ClickHouse 26.10, JSONBench, GroeneAI, Loom, and our House Party at AWS re:Invent."
---

# November 2026 newsletter

Hello and welcome to the November ClickHouse newsletter!

This month, we did our biggest launch since ClickHouse Cloud, with Managed Postgres going GA, ClickHouse Observability and the Langfuse AI Gateway entering public beta, and ClickHouse Security launching in private preview.

GroeneAI gets stuck into bug fixes, Loom helps coding agents with those “didn’t we already work this out?” moments, and the billion-document JSON benchmark is back.

And AWS re:Invent is nearly here, which means it's time for us to throw another party with the Chainsmokers in Las Vegas!

## Featured community member: Ana Lacruz {#featured-community-member-ana-lacruz}

This month’s featured community member is Ana Lacruz, Data Engineer at Infinitas Learning.  
![](https://clickhouse.com/uploads/nov2026_nl_image2_774850b63c.png)

Ana works on the Results & Insights team, supporting educational platforms used by 1.6 million learners. The team uses ClickHouse Managed Postgres to record assignment results and learner progress, alongside ClickHouse Cloud for analytics.

At Open House Amsterdam, Ana [shared the team’s journey](https://clickhouse.com/blog/infinitas-learning-clickhouse-managed-postgres) from ClickHouse Cloud to self-hosting and back again. She explained how cache misses caused unpredictable query latency, and how self-hosting improved performance but brought maintenance and recovery responsibilities.

Working with ClickHouse’s support team, they optimized their queries and table settings before adopting distributed cache. In load tests, P99 query latency reached 410 milliseconds, meeting their 500-millisecond target. Ana also described how the team can now take a dashboard from proof of concept to production-ready, using real data, in hours.

➡️ [Connect with Ana on LinkedIn](https://www.linkedin.com/in/ana-lacruz-69140b53/)

## House Party with the Chainsmokers at AWS re:Invent {#house_party_with_the_chainsmokers_at_aws_reinvent}

![](https://clickhouse.com/uploads/nov2026_nl_image3_76202da2e6.png)  
The Chainsmokers are back for our third House Party at AWS re:Invent. 

Join us at Intrigue Nightclub in Las Vegas on Tuesday, December 1 for music and drinks after a day of conference sessions.

➡️ [Request a ticket](https://clickhouse.com/houseparty/reinvent?utm_source=clickhouse&utm_medium=email&utm_campaign=202611-newsletter&ref=newsletter)

## 26.10 release {#2610_release}

![ClickHouse 26.10 release](https://clickhouse.com/uploads/nov2026_nl_image4_50df69511a.png)

ClickHouse 26.10 introduces function composition for more readable SQL, JOINs with arbitrary conditions, and direct import and export of SQLite files.

Queries grouping by multiple `LowCardinality` columns get faster, while large `IN` subqueries can now spill to disk to reduce memory use. There’s also an experimental columns cache that reuses decoded column data across queries, avoiding repeated decompression and deserialization.

➡️ [Read the release post](https://clickhouse.com/blog/clickhouse-release-26-10?utm_source=clickhouse&utm_medium=email&utm_campaign=202611-newsletter&ref=newsletter)

## Our largest expansion yet {#our_largest_expansion_yet}

![The largest expansion of ClickHouse yet](https://clickhouse.com/uploads/nov2026_nl_image5_443c66acfc.jpg)

Our latest platform launch spanned transactions, observability, security, and AI engineering. 

Managed Postgres is now generally available on AWS, with Xata’s branching, cloning, and scale-to-zero capabilities planned for integration.

ClickHouse Observability enters public beta for investigating logs, metrics, traces, and session data.

And finally, ClickHouse Security launches in private preview with AI-assisted threat investigations, while the open-source Langfuse AI Gateway enters public beta to help teams track model usage and costs.

➡️ [Read the announcement](https://clickhouse.com/blog/announcing-clickhouse-platform-largest-expansion?utm_source=clickhouse&utm_medium=email&utm_campaign=202611-newsletter&ref=newsletter)

## Postgres round-up {#postgres_round_up}

![Postgres Round-up](https://clickhouse.com/uploads/nov2026_nl_image6_b7c14eabca.jpg)

This month brings Managed Postgres GA and the Xata acquisition, plus hands-on replication tests, failover engineering, query diagnostics, and lessons from customer migrations. 

➡️ [Register for the live webinar on November 23 to learn more!](https://clickhouse.com/company/events/202611-AMER-Webinar-Postgres-Vision-ClickHouse?utm_source=clickhouse&utm_medium=email&utm_campaign=202611-newsletter&ref=newsletter)

* Sai Srirampur [announces the general availability of Managed Postgres on AWS and the acquisition of Xata](https://clickhouse.com/blog/managed-postgres-ga-xata-acquisition?utm_source=clickhouse&utm_medium=email&utm_campaign=202611-newsletter&ref=newsletter), whose branching, cloning, and serverless capabilities are planned for integration into the service.  
* Hidehiko ASAHI [shares a month of WalShadow testing](https://clickhouse.com/blog/a-month-with-walshadow-clickhouse-managed-postgres?utm_source=clickhouse&utm_medium=email&utm_campaign=202611-newsletter&ref=newsletter), measuring a median replication latency of roughly 0.4 seconds in his private-preview workloads and verifying correctness, recovery, and materialized-view behavior.  
* Furkan Sahin [explains how fencing prevents two Postgres servers from acting as the primary during a failover](https://clickhouse.com/blog/fencing-a-postgres-primary-that-might-still-be-alive?utm_source=clickhouse&utm_medium=email&utm_campaign=202611-newsletter&ref=newsletter), and how the implementation differs across clouds.  
* Lionel Palacin and Gülçin Yıldırım Jelínek [make the case for testing faster Postgres before adding local data synchronization](https://clickhouse.com/blog/does-your-application-need-local-data-or-faster-postgres?utm_source=clickhouse&utm_medium=email&utm_campaign=202611-newsletter&ref=newsletter), especially when AI agents keep changing the data they need.  
* Al Brown [walks through clickhousectl v0.5.0](https://clickhouse.com/blog/clickhousectl-v0-5-0?utm_source=clickhouse&utm_medium=email&utm_campaign=202611-newsletter&ref=newsletter), which brings Managed Postgres metrics, logs, and read-only SQL into the terminal.  
* Amog Iska [previews more Managed Postgres notifications](https://clickhouse.com/blog/expanding-customer-notifications-managed-postgres?utm_source=clickhouse&utm_medium=email&utm_campaign=202611-newsletter&ref=newsletter) for inactive replication slots, switchovers, failovers, long-running transactions, and connection limits.  
* Sawyer Bateman [explains why Shipsidekick moved from Neon to ClickHouse Managed Postgres](https://clickhouse.com/blog/shipsidekick-neon-to-clickhouse-managed-postgres?utm_source=clickhouse&utm_medium=email&utm_campaign=202611-newsletter&ref=newsletter). His team replicated 500 GB in hours and reports roughly 10× faster queries.  
* Amog Iska also [introduces Postgres wait events in Query Insights](https://clickhouse.com/blog/postgres-wait-events-query-insights?utm_source=clickhouse&utm_medium=email&utm_campaign=202611-newsletter&ref=newsletter), with wait categories, blocked-session counts, and lock-wait durations to help explain slow queries.

## Why ClickHouse Cloud wins at real-time analytics {#why_clickhouse_cloud_wins_at_real_time_analytics}

![Why ClickHouse Cloud wins at real-time analytics](https://clickhouse.com/uploads/nov2026_nl_image7_0ed2f8431a.jpg)

Tom Schreiber and Lionel Palacin wrap up the CostBench series with an illustrated tour of the architecture behind ClickHouse Cloud.

They show how sorting and pre-aggregation during ingestion reduce query work, and how parallel execution spreads the remaining work across machines and CPU cores. The authors also explain how ClickHouse Cloud lets teams scale ingestion and queries separately, so each workload gets the resources it needs. 

And across the blog post, they also share customer examples of the architecture in practice: faster data preparation at Appcues, real-time decisions at Buildkite, and AI-powered security investigations at Artemis.

➡️ [Read the blog post](https://clickhouse.com/blog/why-clickhouse-cloud-wins-at-real-time-analytics?utm_source=clickhouse&utm_medium=email&utm_campaign=202611-newsletter&ref=newsletter)

## JSONBench is back, and ClickHouse still leads {#jsonbench_is_back_and_clickhouse_still_leads}

![JSONBench is back, and ClickHouse still leads](https://clickhouse.com/uploads/nov2026_nl_image8_7697190eb7.png)

[JSONBench](https://benchmark.clickhouse.com/json/) is an open-source benchmark that compares the query performance of different databases on large datasets of nested JSON documents. It now covers 27 database engines, up from five, with ClickHouse leading the published billion-document comparisons.

Tom Schreiber and Mark Needham walk through the results, including a cold-run aggregation over nested Bluesky events that took 661 milliseconds in ClickHouse and more than 32 minutes in MongoDB under the benchmark’s configurations. They also explain recent improvements to ClickHouse’s JSON type and how to reproduce the benchmark.

➡️ [Read the blog post](https://clickhouse.com/blog/jsonbench-is-back-clickhouse-still-leads?utm_source=clickhouse&utm_medium=email&utm_campaign=202611-newsletter&ref=newsletter)

## Meet GroeneAI: our autonomous contributor to ClickHouse {#meet_groeneai_our_autonomous_contributor_to_clickhouse}

![Meet GroeneAI: our autonomous contributor to ClickHouse](https://clickhouse.com/uploads/nov2026_nl_image9_483e68c9e2.jpg)

James Cunningham, Artem Brustovetskii and Alex Soffronow Pagonidis introduce GroeneAI, an autonomous contributor that investigates failures, writes and tests fixes, and follows pull requests through CI and human review.

Built on the open-source Nerve runtime, it uses persistent memory to carry work across sessions and learn from maintainer feedback. By October 25, it had contributed more than 3,100 merged pull requests, with ClickHouse maintainers deciding which changes to merge.

➡️ [Read the blog post](https://clickhouse.com/blog/meet-groeneai-our-autonomous-contributor-to-clickhouse?utm_source=clickhouse&utm_medium=email&utm_campaign=202611-newsletter&ref=newsletter)

## Introducing Loom: agent memory that keeps up with your code {#introducing_loom_agent_memory_that_keeps_up_with_your_code}

![Introducing Loom: agent memory that keeps up with your code](https://clickhouse.com/uploads/nov2026_nl_image10_9b31423edf.jpg)

James Cunningham and Lareb Zafar introduce Loom, an open-source memory and code-search system built on ClickHouse. It lets coding agents share findings across sessions and teams, so they can build on earlier investigations.

Loom records where memories came from, tracks code renames, and flags notes that may be stale when the underlying code changes. In the authors’ benchmark of questions about the ClickHouse codebase, Loom improved answer quality while lowering the average cost per question.

➡️ [Read the blog post](https://clickhouse.com/blog/introducing-loom-agent-memory-that-keeps-up-with-your-code?utm_source=clickhouse&utm_medium=email&utm_campaign=202611-newsletter&ref=newsletter)

## Quick reads {#quick-reads}

* Nicole Mitich explains [how to stream Oracle changes into ClickHouse with Striim](https://medium.com/striim/streaming-oracle-cdc-into-clickhouse-with-striim-c242f86fe052), covering MergeTree engine selection, recovery, and throughput tuning.  
* Patrick Salsbury shows [how ClickHouse’s LTTB function speeds up large time-series charts](https://medium.com/@p.r.salsbury/visualizing-large-scale-time-series-data-with-clickhouse-and-lttb-88635e100c05) by downsampling data, including the trade-off between faster charts and lost detail.  
* Innovafour explains [how it reduced storage from about 48 to 13 bytes per event](https://medium.com/@innovafoursas/from-48-to-13-bytes-per-event-shrinking-a-product-analytics-stack-to-fit-a-2-gb-server-cb579539a1f3), using schema, compression, and ingestion changes to fit its analytics stack on a 2 GB RAM server.  
* Frank Pacione shares lessons from [building a car search engine with ClickHouse and AI agents](https://medium.com/@fpacione/building-an-enthusiast-car-search-engine-with-provenance-using-ai-agents-227026b34e4d), including how fixing the agents’ JSON queries cut his daily ClickHouse costs by 30 to 50%.  
* Jitin Bahri describes [how Zoop moved API billing and analytics from BigQuery to ClickHouse](https://medium.com/zoop-engineering/clickhouse-at-zoop-billing-and-analytics-without-a-per-query-bill-9495b25a7f5c), using Postgres CDC and materialized views to keep usage totals up to date and costs more predictable.  
* Andrew Fleming and Abed Habli show [how they built Metabase data apps on ClickHouse for the AI Builders meetup in Stockholm](https://www.metabase.com/blog/data-apps-world-tour), including an F1 race replay that runs many queries per second over 60 million rows of telemetry.

## Events {#events}

### Global virtual events

* [Langfuse Workshop](https://luma.com/qi4abwvx) - Hybrid: Austin and Zoom - Nov 19, 2026  
* [ClickHouse Managed Postgres: The Vision Comes Together](https://clickhouse.com/company/events/202611-AMER-Webinar-Postgres-Vision-ClickHouse?utm_source=clickhouse&utm_medium=email&utm_campaign=202611-newsletter&ref=newsletter) - Nov 23, 2026  
* [v26.11 Community Call](https://clickhouse.com/company/events/v26-11-community-release-call?utm_source=clickhouse&utm_medium=email&utm_campaign=202611-newsletter&ref=newsletter) - Nov 24, 2026  
* [How ClickHouse's security team uses ClickHouse Security](https://clickhouse.com/company/events/202612-AMER-Webinar-ClickHouse-Security?utm_source=clickhouse&utm_medium=email&utm_campaign=202611-newsletter&ref=newsletter) - Dec 3, 2026  
* [ClickHouse for Starters「AI時代のデータプラットフォームとは」](https://clickhouse.com/ja/company/events/202612-APJ-Webinar-Japan-ClickHouseForStarters?utm_source=clickhouse&utm_medium=email&utm_campaign=202611-newsletter&ref=newsletter) - Japanese (Zoom) - Dec 9, 2026, 12:30–13:00 JST

### Virtual training

* [ClickHouse Observability Fundamentals (EMEA/APJ)](https://clickhouse.com/company/events/202612-EMEA-APJ-Observability-with-ClickStack?utm_source=clickhouse&utm_medium=email&utm_campaign=202611-newsletter&ref=newsletter) - Dec 2, 2026  
* [Fundamentos do ClickHouse](https://luma.com/clickh-7luq) - Portuguese - Dec 2, 2026  
* [ClickHouse Fundamentals (AMER)](https://clickhouse.com/company/events/202612-AMER-ClickHouse-Fundamentals?utm_source=clickhouse&utm_medium=email&utm_campaign=202611-newsletter&ref=newsletter) - Dec 2, 2026  
* [ClickHouse Observability Fundamentals (AMER)](https://clickhouse.com/company/events/202612-AMER-Observability-with-ClickStack?utm_source=clickhouse&utm_medium=email&utm_campaign=202611-newsletter&ref=newsletter) - Dec 9, 2026  
* [Observabilidad con ClickStack: Nivel 1 (LATAM)](https://luma.com/clickh-w10a) - Spanish - Dec 17, 2026  
* [ClickHouse Fundamentals (APJ/EMEA)](https://clickhouse.com/company/events/202612-APJ-EMEA-ClickHouse-Fundamentals?utm_source=clickhouse&utm_medium=email&utm_campaign=202611-newsletter&ref=newsletter) - Dec 22, 2026

### Events in AMER

* [ClickHouse Meetup — Seattle: Real-Time Analytics in Production](https://luma.com/clickh-0alm) - Seattle - Nov 19, 2026  
* [Treinamento presencial de 2 dias em São Paulo: Análise em tempo real com ClickHouse](https://clickhouse.com/company/events/202611-LATAM-Sao-Paulo-Real-time-Analytics-w-ClickHouse?utm_source=clickhouse&utm_medium=email&utm_campaign=202611-newsletter&ref=newsletter) - São Paulo - Nov 24–25, 2026  
* [Maxa x ClickHouse: Data Developer Meetup MTL](https://luma.com/4812th4n) - Montréal - Nov 26, 2026  
* [AWS re:Invent](https://clickhouse.com/campaigns/aws-reinvent-2026?utm_source=clickhouse&utm_medium=email&utm_campaign=202611-newsletter&ref=newsletter) - Las Vegas - Nov 30–Dec 4, 2026  
* [House Party with The Chainsmokers](https://clickhouse.com/company/events/20261201-houseparty?utm_source=clickhouse&utm_medium=email&utm_campaign=202611-newsletter&ref=newsletter) - Las Vegas - Dec 1, 2026  
* [45 RPM: Ramp x ClickHouse](https://luma.com/mqv2uyje) - Las Vegas - Dec 2, 2026  
* [Hell's Software Factory: The Challenges of the AI SDLC](https://luma.com/jbj2va14) - Las Vegas - Dec 2, 2026  
* [Holiday House](https://clickhouse.com/company/events/202612-AMER-Holiday-House-Dallas?utm_source=clickhouse&utm_medium=email&utm_campaign=202611-newsletter&ref=newsletter) - Grapevine, Texas - Dec 9, 2026  
* [Holiday House](https://clickhouse.com/company/events/2026-12-14-AMER-holiday-house-bayarea) - Bay Area - Dec 10, 2026  
* [Holiday House](https://clickhouse.com/company/events/202612-AMER-Holiday-House-NYC?utm_medium=email&utm_source=marketo&utm_content=202611-newsletter) - NYC - Dec 10, 2026  
* [Capacitación presencial en Bogotá: Observabilidad con ClickStack](https://clickhouse.com/company/events/202612-LATAM-Bogota-Observability-with-ClickStack?utm_source=clickhouse&utm_medium=email&utm_campaign=202611-newsletter&ref=newsletter) - Bogotá - Dec 15, 2026  
* [Holiday House](https://clickhouse.com/company/events/202612-AMER-Holiday-House-Salt-Lake-City?utm_source=clickhouse&utm_medium=email&utm_campaign=202611-newsletter&ref=newsletter) - Salt Lake City - Dec 17, 2026

### Events in EMEA

* [Search Week After Party: Pub Quiz by Qdrant with ClickHouse](https://luma.com/londonsearchweek_2026) - London - Nov 24, 2026  
* [Langfuse Hands-On Workshop: From AI Agent Observability to Evaluation & Continuous Improvement](https://clickhouse.com/company/events/202611-EMEA-AIAgent-Observability-Evaluation-Continuous-Improvement?utm_source=clickhouse&utm_medium=email&utm_campaign=202611-newsletter&ref=newsletter) - Dubai - Nov 25, 2026  
* [Datos rápidos, agentes inteligentes: desayuno con ClickHouse](https://clickhouse.com/company/events/202611-EMEA-SPIGT-Spain-Fast-Data-Smart-Agents-Breakfast-with-ClickHouse) - Madrid, Spain - Nov 25, 2026  
* [Data TLV](https://datatlv.com/Home.html) - Tel Aviv - Nov 26, 2026  
* [Daytona AI Builders](https://luma.com/ai-builders-paris-nov) - Paris, Nov 26, 2026  
* [Scaling Data Systems with ClickHouse Cyprus Meetup](https://luma.com/clickh-hs3o) - Limassol - Nov 26, 2026  
* [Data TLV](https://datatlv.com/Home.html) - Rishon LeZion, Israel - Nov 26, 2026  
* [ClickHouse Hands-on TLV](https://luma.com/xp2h8odw) - Tel Aviv, Israel - Nov 30, 2026  
* [AdoptAI](https://adoptai.artefact.com/) - Paris, France - Dec 3,4, 2026  
* [AI Builders and Databases Munich](https://luma.com/clickh-rsxf) - Munich - Dec 3, 2026  
* [Ahead of Time: A Hackathon by Mistral and ClickHouse](https://luma.com/clickh-mistral-hack-paris) - Paris - Dec 5, 2026  
* [GITEX](https://www.gitex.com/) - Dubai - Dec 8-11, 2026  
* [Microsoft Frontier Tour](https://frontiertour.microsoft.com/flow/microsoft/utrecht27/citylanding/page/cityhome) - Utrecht - Dec 10, 2026  
* [AI Tinkerers Milan - December 10 Demo Night](https://milan.aitinkerers.org/p/ai-tinkerers-milan-december-10-demo-night) - Milan - Dec 10, 2026  
* [kickoff(): hack, demo, play FC27 at Fulham’s Craven Cottage](https://luma.com/clickh-gqb5) - London - Dec 17, 2026

### Events in APAC and Japan

* [ClickHouse x OliveYoung x NxtCloud Seoul Meetup](https://luma.com/clickh-gb3i) - Seoul - Nov 25, 2026  
* [See What Your Agent Did: Trace it. Debug it. Ship it.](https://luma.com/clickh-k5ti) - Singapore - Nov 26, 2026  
* [The Agentic Data Stack](https://clickhouse.com/company/events/202611-APJ-Bengaluru-The-Agentic-Data-Stack?utm_source=clickhouse&utm_medium=email&utm_campaign=202611-newsletter&ref=newsletter) - Bengaluru - Nov 26, 2026  
* [Braze x ClickHouse: Real-Time Analytics and AI-Driven Customer Engagement](https://globalevents.braze.com/clickhouse-braze-261127/) - Tokyo - Nov 27, 2026  
* [Logs, metrics and traces at scale, without the bill shock](https://clickhouse.com/company/events/202612-APJ-Melbourne-Logs-Metrics-Traces-at-Scale?utm_source=clickhouse&utm_medium=email&utm_campaign=202611-newsletter&ref=newsletter) - Melbourne - Dec 8, 2026  
* [Logs, metrics and traces at scale, without the bill shock](https://clickhouse.com/company/events/202612-APJ-Sydney-Logs-Metrics-Traces-at-Scale?utm_source=clickhouse&utm_medium=email&utm_campaign=202611-newsletter&ref=newsletter) - Sydney - Dec 9, 2026  
* [Logs, metrics and traces at scale, without the bill shock](https://clickhouse.com/company/events/202612-APJ-Bengaluru-Logs-Metrics-Traces-at-Scale?utm_source=clickhouse&utm_medium=email&utm_campaign=202611-newsletter&ref=newsletter) - Bengaluru - Dec 10, 2026  
* [Melbourne Data Night with ClickHouse and ThoughtSpot](https://luma.com/clickh-x6bl) - Melbourne - Dec 15, 2026

➡️ [Browse all ClickHouse events](https://clickhouse.com/company/events?utm_source=clickhouse&utm_medium=email&utm_campaign=202611-newsletter&ref=newsletter) · [Follow the ClickHouse calendar on Luma](https://luma.com/clickhouse-events)


---

## Get started today

Interested in seeing how ClickHouse works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-3120-get-started-today-sign-up&utm_blogctaid=3120)

---