---
title: "Shopify powers observability for global-scale commerce with ClickHouse"
date: "2026-08-20T10:17:25.319Z"
author: "ClickHouse"
category: "User stories"
excerpt: "Shopify unified global-scale observability on ClickHouse, achieving up to 30x faster queries while ingesting 100 million events per second at peak."
---

# Shopify powers observability for global-scale commerce with ClickHouse

## Summary

- Shopify replaced fragmented observability vendors with Observe, its own unified platform for metrics, logs, traces, and exceptions, built on ClickHouse.
- Moving to ClickHouse delivered a 16x query improvement out of the box, spiking past 30x, while bringing previously unpredictable vendor costs under control.
- At Black Friday–Cyber Monday peak, the platform ingests around 100 million events per second (roughly 110 GB/s of telemetry) and keeps it queryable in under a minute.


[Shopify](https://www.shopify.com/ca) is one of the largest commerce platforms on Earth, operating on five continents with around 500 Kubernetes clusters and 1.5 million pods running at any moment. Traffic flows constantly from Ruby, Go, and TypeScript services, mobile apps, edge logs, databases, and other sources. As engineering director Elijah McPherson puts it, “Commerce never sleeps, and neither does Shopify.”

That demand peaks every year around Black Friday, Cyber Monday (BFCM). “This is our Super Bowl,” Elijah says. Last year during BFCM, Shopify stored 90 PB of data across its fleet, served 2.2 trillion requests at the edge, and ran 14.8 trillion queries against its databases. At peak load, the platform processes up to $5.1 million in transactions per minute.

CALL OUT QUOTE: "During this past Black Friday and Cyber Monday, a minute of downtime can cost our merchants $5.1 million. That's why observability is critical, we need to detect issues and prevent any downtime." — Elijah McPherson, Engineering Director, Shopify

At [Open House SF 2026](https://clickhouse.com/openhouse/san-francisco), Elijah shared how Shopify built its own observability platform for global-scale commerce: why they chose self-hosted ClickHouse; how unifying logs, traces, and exceptions on one engine helped cut cost and complexity; and why, if they were doing it all over again, he’d likely reach for [ClickHouse Cloud](https://clickhouse.com/cloud) instead.

## A disjointed, unpredictable setup

Elijah joined Shopify in 2021 to rebuild its observability infrastructure. At the time, the setup was siloed across vendors: one for metrics, another for logs, another for traces. Bills were scaling faster than the fleet itself, and the team couldn’t forecast them.

“I came in specifically because our observability platform was disjointed across multiple vendors,” Elijah says. “The cost was growing astronomically high, and we couldn't predict it.”

That fragmentation impacted the team’s roadmap. Tooling that had become core production infrastructure was locked into external roadmaps Shopify didn’t control, which meant signals that belonged together lived in systems that didn’t talk to each other. Asking a single question across metrics, logs, and traces meant manually stitching answers across vendors.

Taking stock of the situation, what the team needed was clear: Build something that’s cohesive, make it affordable, make it specific for Shopify, and make it scale.

## Observability built by Shopify, for Shopify

The answer was an internal platform the team calls Observe. The idea is a single place to look across every signal and answer developers’ questions: What’s happening in production *right now*? Is checkout healthy? Did a deploy change behavior? What happened during an incident? How are we performing during BFCM? Can I deploy with confidence?

It didn't happen all at once. The Shopify team started with metrics, where the pain was sharpest and they could have the largest impact. After moving metrics off a costly observability vendor and onto ClickHouse, they consolidated logs, traces, profiles, and exceptions onto the same engine. Recognizing that all of these signals were the same primitive (structured, time-ordered, high-dimensional events), they built one platform for search and analytics across all of them. Today Shopify runs metrics, logs, traces, exceptions, and profiles on ClickHouse.

The requirements were demanding. Ingest runs at around 50 million events per second at steady state and 100 million at BFCM peak, roughly 110 GB/s of uncompressed telemetry at peak, from hundreds of teams and constantly evolving schemas. “Our engineers really depend on this data being available, and they also want to query this data in under a minute,” Elijah says. Those queries arrive in every shape, from broad analytics to needle-in-a-haystack lookups across 30 days.

## Choosing ClickHouse as the engine

The team tried several solutions, and ClickHouse came out on top. “ClickHouse was what won for us, primarily due to it being fast, being able to handle our load, and being open-source, which meant we can contribute and understand the source code,” Elijah says.

He calls ClickHouse “very unique in that it’s an open-source project that scales.” It gave Shopify control over its costs and roadmap, with no per-byte pricing model to outgrow. On top of that, the database keeps improving as the ClickHouse team and wider community invest in it. “A rising tide lifts all boats,” Elijah says.

While no product is perfectly turnkey at Shopify’s scale, Elijah says ClickHouse got them “pretty far down that road” and is “performant out of the box.” It was built for high-volume columnar inserts and interactive analytics over petabytes rather than batch jobs, and its flexible schema model gave the team room to build on.

CALL OUT QUOTE: “We saw around a 16x improvement out of the box with ClickHouse once we had it deployed, and at peak performance over 30x. And for us, less compute is money.”
— Elijah McPherson, Engineering Director, Shopify

## Lessons from running ClickHouse at scale

Picking ClickHouse was just the start. After running ClickHouse as the backbone of Shopify’s observability platform for a few years, Elijah had a few lessons to share at Open House about improving performance, cost efficiency, and reliability.

The first was about durability. ClickHouse prefers large batches over many small inserts, but as Elijah says, “wait for a big batch” means high latency, and Shopify can’t afford to lose data in the meantime. The solution was a pipeline that buffers telemetry in Kafka, then commits large synchronous writes, acknowledging a batch only after ClickHouse has durably stored it.

Next was flexible schemas. Hundreds of teams at Shopify emit hundreds of event shapes that change daily, so the schema can’t be fixed in advance. To keep queries fast anyway, Elijah and the team use [materialized views](https://clickhouse.com/docs/materialized-views). A metadata view tracks which fields exist and what values they hold, making autocomplete queries return in 50-100 milliseconds. The team also promotes hot keys out of [`Map(String, String)`](https://clickhouse.com/docs/sql-reference/data-types/map) into typed columns, so queries stop converting types at read time. This runs roughly 30% faster than the all-string baseline and compresses better.

And materialized views solve a second problem: correlation. When something breaks, an engineer needs every event tied to a single request, scattered across logs, traces, queries, and profiles. Shopify maintains a materialized view that records which datasets each high-value identifier touched and when, so hitting that lookup first turns a fleet-wide search into a few targeted scans, amounting to a 10x speedup. “If someone wants to say ‘show me all logs, all events, all traces for this job,’ we can do that,” Elijah says.

## Operating it day to day in production

Today, Shopify’s observability platform with ClickHouse runs across roughly 20 tenants, each with its own ingest sources, schema, and query mix. Something is migrating every week (schema changes, ClickHouse updates, Kubernetes upgrades, incompatible node types), and ingestion can’t pause.

To manage that, the team wrote an in-house Kubernetes operator, giving them a declarative schema manager that turns migrations and topology changes across all the tenants into reviewable diffs instead of one-off manual work.

Running open-source ClickHouse also means owning every performance and cost trade-off directly. “Everything is a knob for us,” Elijah says. At scale, things like disk bandwidth, IOPS, CPU, part-merge throughput, and object-storage bills add up to a constant balancing act.

[Compression](https://clickhouse.com/docs/data-compression/compression-in-clickhouse) is a recurring win, since every byte saved means less bandwidth, fewer IOPS, and a smaller bill. One meaningful change was sorting map keys at write time, which gave the team 20-40% disk savings.

## What’s next for Shopify and ClickHouse

For Elijah and the team, the work is never done. They’re currently shifting toward tiered storage with NVMe for the hot path, SSD for the warm window, and object storage for cold history, paired with ARM-based compute. On the schema side, they’re moving past `Map(String, String)` and promoted columns to bucketed maps or [ClickHouse’s native JSON type](https://clickhouse.com/docs/sql-reference/data-types/newjson) for better compression and query plans with less migration work. They’re also rebuilding the ingestion pipeline in Rust, with a per-message acknowledgment model and event-loop scheduling. As Elijah notes, ingest volume tends to double from one BFCM to the next, making the collection pipeline “the hottest of the hot paths.” The rewrite is meant to stay ahead of that.

The same engine that powers internal observability is now expanding into adjacent domains. Shopify runs profiling continuously across its fleet and writes it to ClickHouse alongside logs, traces, and exceptions, which lets the team query CPU flamegraphs over billions of samples. Because all of that data sits in one place, it can also feed an “AI agent layer that anyone at Shopify can talk to, and that’s all backed and queried through ClickHouse,” Elijah says.

The next step is merchant-facing analytics, things like checkout funnels, product views, and conversion insights. “ClickHouse seemed like a natural fit,” Elijah says. “If we can ingest all of the telemetry data and query it for ourselves, this in practice would work really well for our merchants as well.”

## DIY ClickHouse vs. ClickHouse Cloud

Elijah acknowledges that Shopify built their observability platform on self-hosted ClickHouse because, at the time, [ClickHouse Cloud](https://clickhouse.com/cloud) didn’t exist. That means taking on the operational burden themselves. “If I were to go back and ask, ‘Do I really need to do this myself?’ the answer is probably not,” he says. “I think we would choose something like ClickHouse Cloud.”

He notes that while self-hosting offers certain advantages like full control over your roadmap, SLAs, and cost curve, ClickHouse’s managed service delivers faster time-to-value, with [separated storage and compute](https://clickhouse.com/docs/guides/separation-storage-compute), upgrades, and scaling out of the box. “They handle a lot of this for you,” he says. “You can separate ingest from query compute, and it actually turns out you don’t need as many replicas of the data, and that saves money.”

What’s more, Shopify independently arrived at many of the same optimizations the [ClickStack](https://clickhouse.com/clickstack) team has implemented. As the two teams continue to learn from each other’s work, improvements driven by users like Shopify are folded back into ClickStack, allowing the wider open-source community to benefit from the same attention to detail in performance and usability.


---

## Get started today

Interested in seeing how ClickHouse works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-1603-get-started-today-sign-up&utm_blogctaid=1603)

---