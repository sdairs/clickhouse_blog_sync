---
title: "How Spyne simplified their CDC pipeline with ClickPipes and ClickHouse Cloud"
date: "2026-06-22T11:37:29.230Z"
author: "ClickHouse"
category: "User stories"
excerpt: "Spyne cut table onboarding from 1.5+ hours to minutes and eliminated schema drift by migrating their CDC pipeline from a self-managed Debezium/Kafka stack to ClickPipes and ClickHouse Cloud."
---

# How Spyne simplified their CDC pipeline with ClickPipes and ClickHouse Cloud

## Summary

* Spyne uses ClickPipes to power its real-time CDC pipeline, streaming changes from MySQL and MongoDB sources directly into ClickHouse Cloud.  
* They migrated from a self-managed Debezium/Kafka stack to ClickPipes, eliminating 1.5+ hours of manual work per table onboarding and resolving schema drift issues.  
* Automated schema evolution in ClickPipes replaced a slow, error-prone manual process, drastically improving developer velocity and data consistency.

[Spyne](https://www.spyne.ai/) is an AI-native automotive retail tech company that helps dealerships sell faster and engage smarter. Its two flagship products handle opposite ends of the dealership workflow: [Studio AI](https://www.spyne.ai/virtual-car-photography-studio) transforms raw vehicle photos into studio-quality images, spins, and videos for digital storefronts, while [Vini AI](https://www.vini.mx/) acts as an always-on AI sales assistant, answering calls and chats, qualifying leads, and booking appointments.

Both products depend on data being accurate and up-to-date. But as the company grew and added new features, the team responsible for keeping that data flowing was spending more time maintaining the pipeline than analyzing what flowed through it.

At a [January 2026 ClickHouse meetup in Gurgaon](https://clickhouse.com/videos/202601-gurgaon-meetup-spyneai), DevOps engineer Abhash Solanki shared how Spyne simplified their CDC pipeline, migrating from a self-managed setup built on Debezium and Kafka to serverless [ClickPipes](https://clickhouse.com/cloud/clickpipes) and [ClickHouse Cloud](https://console.clickhouse.cloud/).

<iframe width="768" height="432" src="https://www.youtube.com/embed/gNJENprGhm0" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

## Infrastructure toil and schema drift

Spyne's old CDC pipeline was, in Abhash's words, a "complex beast, an intricate web of open-source tools and custom configurations."

Source databases in MySQL and MongoDB fed into Debezium connectors, which read changes from binary and operation logs in real time and published them as messages to a Kafka cluster. The Kafka cluster then fed those into a self-hosted ClickHouse instance, with a [Kafka engine table](https://clickhouse.com/docs/engines/table-engines/integrations/kafka) consuming the stream and flattening each message into a single JSON payload. From there, [materialized views](https://clickhouse.com/docs/materialized-views) (specific to the schema) transformed the flattened JSONs into final [ReplacingMergeTree tables](https://clickhouse.com/docs/engines/table-engines/mergetree-family/replacingmergetree), ClickHouse's mechanism for handling updates efficiently.

![Spyne AI Diagrams MDSN-54.png](https://clickhouse.com/uploads/Spyne_AI_Diagrams_MDSN_54_af64f3e4a7.png)

*Spyne's old CDC pipeline: MySQL/MongoDB sources flowing through Debezium connectors, a Kafka cluster, and ClickHouse's Kafka engine table and materialized views into ReplacingMergeTree tables.*

The architecture, while functional, created what Abhash calls significant "operational toil," demanding constant attention and consuming valuable engineering hours.

The first major bottleneck was onboarding new tables. Every new table triggered a manual process: raise a DevOps ticket, map data types from MySQL or MongoDB to ClickHouse-compatible DDL (a manual, error-prone process Abhash calls the "type mismatch nightmare"), write the Kafka engine table, create the materialized view, update the Debezium connector config, and restart the pipeline, risking downtime.

"Adding a new table would take at least 1 to 1.5 hours of manual intervention and manual workload," Abhash says. "Whenever a new product release or a new analytical table has to be added, this whole cycle has to be performed."

That wasn't even the biggest pain point. The main problem, as Abhash describes it, was "schema drift nightmares." In a dynamic dev environment like Spyne's, source tables change frequently; new columns get added, data types get altered. When that happened, Debezium would faithfully capture the change and Kafka would deliver it, but the downstream materialized view, locked to its original DDL, would "silently ignore" the new data, leading to data inconsistencies and a lack of visibility into critical new features.

Identifying the gap could take days, after which the fix required stopping the pipeline, altering the materialized view and final table, restarting everything, and often resyncing the whole table from scratch. This manual intervention created major delays and increased the risk of errors, making every release, as Abhash puts it, a "high-stakes operation."

## Embracing simplicity with ClickPipes

When Abhash went looking for a more robust and manageable solution, he didn't have to look far. Spyne was already self-hosting ClickHouse, and he saw that the database's managed service, [ClickHouse Cloud](https://console.clickhouse.cloud/), offered a native ingestion engine, [ClickPipes](https://clickhouse.com/cloud/clickpipes). "The promise of a fully managed service, designed for seamless CDC, was compelling," he says.

With ClickHouse Cloud's efficient and easy-to-use UI, setting up a new data pipeline now takes "mere minutes," a welcome change from the meticulous Debezium configuration and schema mapping of the old system. "For a person who was manually adding each table and generating schemas for it, it felt like magic," Abhash says.

![Spyne AI Diagrams.png](https://clickhouse.com/uploads/Spyne_AI_Diagrams_0f719848ca.png)

*Spyne's new CDC pipeline, with sources flowing directly into ClickHouse Cloud via ClickPipes.*

The biggest win, as he puts it, is "automated schema evolution." ClickPipes automatically detects upstream changes in sources like MongoDB and MySQL, then applies them to the corresponding ClickHouse tables instantly, with no manual intervention or pipeline restarts. This "zero-touch maintenance" has drastically improved developer velocity, allowing features to be deployed and data to be analyzed with "unprecedented speed and reliability."

## Solving challenges along the way

While ClickPipes immediately solved the team's main challenges, Abhash is quick to point out that "managed services aren't always magic… they also have some toils of their own." He notes that even with advanced platforms like ClickHouse Cloud, you still need to understand how things work under the hood and be willing to adapt how you operate.

As the team got to know the platform, they encountered specific architectural nuances and behaviors that required them to evolve their SQL patterns and operational awareness to fully leverage its benefits. "This was less about fixing flaws," Abhash says, "and more about optimizing our approach for the new paradigm."

---

## Get started today

Interested in seeing how ClickHouse works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-982-get-started-today-sign-up&utm_blogctaid=982)

---


## Challenge #1: The "snapshot" block

[Adding a new table](https://clickhouse.com/docs/integrations/clickpipes/postgres/add_table) to an active ClickPipe causes the entire pipe to pause its CDC streaming while it snapshots the new table. For Spyne, where new tables are added regularly, this created lag in analytics dashboards and interrupted real-time data flow.

The solution was careful ClickPipes planning. Abhash and the team isolated the 10 or so most critical large historical tables (i.e. those requiring real-time analytics at all times) into dedicated ClickPipes. New and lower-priority tables were grouped separately, so that when a snapshot pause occurs, production analytics remain unaffected.

## Challenge #2: The "consistency trap" with ReplacingMergeTree

ClickPipes uses ClickHouse's ReplacingMergeTree engine for efficient data ingestion and deduplication. While powerful, this introduces the concept of [eventual consistency](https://en.wikipedia.org/wiki/Eventual_consistency), which Abhash acknowledges caught the team off guard initially.

What it means is that when a row is updated, two versions briefly coexist (the old and the new) until a background merge resolves them. In Spyne's self-hosted setup, they had tuned this process to complete in less than a minute. But that level of control wasn't available in a managed environment like ClickHouse Cloud.

The team's solution was to add [`FINAL`](https://clickhouse.com/docs/sql-reference/statements/select/from#final-modifier) to their downstream queries, forcing deduplication at query time rather than waiting for the background merge. The trade-off, as Abhash notes, is increased CPU usage on the ClickHouse cluster due to the on-demand deduplication, but it guarantees accurate results in the dashboards that matter most.

## Challenge #3: The "all-or-nothing" recovery risk

When a source database outage (e.g. an AWS RDS failover) causes binary log loss, it creates what Abhash calls the "nightmare scenario": a binlog gap that breaks the CDC chain, invalidating the replication slot and halting data flow.

With self-managed Debezium, the team could perform a targeted partial resync, reingesting only the data from the window around the outage. But with ClickPipes, that granular recovery control isn't available. Recovery often requires a full table resync, which for Spyne can mean reingesting terabytes of data, driving up both ingress costs and latency.

For planned downtime, they can prevent the binlog gap from occurring by pausing the ClickPipe before the maintenance window begins. But for unplanned outages (which he notes are rare in managed services) there's no clean fix. "We have to adapt to it," he says.

## Less engineering toil, more time analyzing data

Throughout the migration, Abhash was clear about the tradeoffs. "Managing a self-managed pipeline gave us intricate control, but it had a very manual way of ingesting data into ClickHouse," he says. "Moving to ClickPipes has eliminated our operational toil."

With [ClickHouse Cloud](https://console.clickhouse.cloud/), Spyne has successfully removed the engineering toil of managing Debezium configurations, Kafka, and complex schema mappings. They've automated schema evolution with ClickPipes, dramatically improving velocity and data consistency. And they've learned to optimize queries for ReplacingMergeTree and strategically manage costs under ClickHouse Cloud's consumption-based pricing model.

As Abhash puts it, "The trade-offs were undeniably worth it for the enhanced stability and significant speed gains we achieved in our data pipelines at Spyne."

---

## Get started today

Interested in seeing how ClickHouse works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-983-get-started-today-sign-up&utm_blogctaid=983)

---