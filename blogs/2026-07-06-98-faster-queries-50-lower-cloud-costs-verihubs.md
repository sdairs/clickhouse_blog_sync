---
title: "98% faster queries, 50% lower cloud costs: Verihubs’ journey from Postgres to ClickHouse"
date: "2026-07-06T13:20:29.307Z"
author: "ClickHouse"
category: "User stories"
excerpt: "Verihubs rebuilt its Postgres data warehouse on ClickHouse with real-time Kafka streaming, cutting query times by up to 98% and cloud costs by up to 50%."
---

# 98% faster queries, 50% lower cloud costs: Verihubs’ journey from Postgres to ClickHouse

## Summary

- Verihubs rebuilt its data warehouse on ClickHouse to power traffic analysis, reconciliation, performance reporting, and invoicing at scale.
- Streaming ingestion via Kafka/Connect + Debezium and MergeTree engines replaced daily Postgres pulls, improving freshness and reliability for stakeholders.
- ClickHouse delivered up to 98% faster queries and up to 50% lower cloud costs, turning dashboards into an interactive OLAP experience.

[Verihubs](https://verihubs.com/en/) is an AI company that builds identity infrastructure like face recognition, deepfake detection, liveness detection, eKYC flows, and WhatsApp OTP for some of Indonesia’s biggest banks, fintechs, and digital apps. 

“The data we manage is important and sensitive,” says software engineering lead Ray Antonius. The company also operates at significant scale: “We handle a huge number of transactions every day—around 50 million API calls per month across all our services.”

Behind those API calls is the data warehouse that helps Verihubs understand traffic, reconcile usage, measure client performance, and generate invoices. The warehouse doesn’t store sensitive data, but it still needs to be accurate, fast, and dependable, especially when finance and operations are trying to close the books or resolve discrepancies.

At our [December 2025 meetup in Jakarta](https://clickhouse.com/videos/jakarta-meetup-verihubs-09dec25), Ray shared how Verihubs rebuilt its warehousing stack around ClickHouse. In about six months, the team moved from a batch-heavy Postgres-based setup to a faster, cheaper, real-time OLAP architecture.

<iframe width="768" height="432" src="https://www.youtube.com/embed/Kl5mZASUzcQ" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

## The pains of Postgres

When Ray joined Verihubs in 2022, he inherited a data warehousing pipeline built around Postgres. A service running in Docker connected to the database, while Airflow pulled data in daily batches each morning. That data would be loaded into the warehouse, refined through additional Airflow jobs when needed, and then surfaced through Metabase.

![Verihub Diagram_2.png](https://clickhouse.com/uploads/Verihub_Diagram_2_881d1a0d7e.png)

*Verihubs’ old architecture, with daily batch pulls from Postgres into the data warehouse.*

“The main issue,” Ray says, “is that almost *everything* had problems.”

The first bottleneck was the choice to run analytics on Postgres, and to do it by repeatedly extracting from the OLTP system in batches. As Ray puts it, “Postgres was fast at first, but at some point it started to get really slow.” A single service could take two to six hours to process data. “Sometimes the process times out, fails, needs to be repeated, and the finance team keeps chasing us,” he adds.

Worse, the data didn’t always arrive within the window the pipeline assumed. Verihubs works with vendors that send callbacks indicating whether an SMS or WhatsApp message was delivered or failed. “Sometimes the data only arrives 20 days later, when it should be available within 24 hours,” Ray explains. “Other times, we’ve already pulled the data, generated the invoices, and processed the data, but it turns out to be wrong and needs to be replaced. That takes even more time.”

Backfills helped correct the record, but they also brought Postgres to its knees. “Because of how Postgres works during backfill, queries become extremely slow,” Ray says. As a result, the team kept getting the same stakeholder questions: *When can I get the latest data? Why does this number look different? Why does the query take so long?*

## A new ClickHouse-based architecture

Ray and the team had three main goals for their new architecture: speed, cost, and user experience. They rebuilt the warehouse around ClickHouse, splitting the design into two phases: ingestion and post-processing.

![](https://clickhouse.com/uploads/Verihub_Diagram_1_2b8f79e8b1.png)

*Verihubs’ new architecture, split into real-time data ingestion and post-processing in ClickHouse.*

## Data ingestion

On the ingestion side, the biggest shift was moving from daily pulls to streaming. “We now perform data ingestion in real time,” Ray says. Instead of extracting from OLTP each morning, Verihubs pushes data through Kafka, using Kafka Connect for streaming and Debezium for change data capture when rows need to be updated later.

Ray notes that ClickHouse offers simpler Kafka integration through [ClickPipes](https://clickhouse.com/cloud/clickpipes), but Verihubs hasn’t adopted it yet. Kafka also gave them something their old system didn’t: a built-in retry mechanism. Rather than writing directly to ClickHouse and dealing with timeouts and failed inserts, they buffer through Kafka so ingestion can recover gracefully.

From there, Verihubs routes data into ClickHouse based on its update pattern. Append-only transaction logs land in [MergeTree](https://clickhouse.com/docs/engines/table-engines/mergetree-family/mergetree) tables optimized for fast inserts and analytical scans. Updatable datasets captured via CDC flow into [ReplacingMergeTree](https://clickhouse.com/docs/guides/replacing-merge-tree) tables, allowing the warehouse to reconcile corrected rows over time without forcing the whole pipeline back into batch mode.

## Data post-processing

Once the data is in ClickHouse, post-processing becomes a mix of in-database refinement and external orchestration for the toughest logic. The team uses [materialized views](https://clickhouse.com/docs/materialized-views) to pre-aggregate high-volume tables into daily and monthly rollups, and [projections](https://clickhouse.com/docs/sql-reference/statements/alter/projection) to speed up stakeholder queries without changing the tables they already query. 

When transformations get too complex, or when the task starts to look like detection rather than aggregation, the team uses Dagster, with pipelines that flag suspicious behavior patterns (like sequential SMS spam across different phone numbers) and trigger notifications to Slack.

![](https://clickhouse.com/uploads/Verihub_Diagram_3_6e24e64085.png)

*Kafka streams events into ClickHouse, where MVs build daily/monthly transaction and COGS tables.*

In his presentation, Ray shared an example of Verihubs’ reconciliation path. ClickHouse ingests streaming transaction data, pulls in related reference data via CDC, and uses materialized views to produce downstream tables (e.g. daily COGS) that finance can use for reconciliation and invoicing.

## From 20-30 minutes to 2-3 seconds

For stakeholders used to waiting on slow, timeout-prone dashboards, Ray says, “the results are very significant.”

After migrating to ClickHouse, Verihubs saw query speed improve by as much as 98%. Queries that once took 20 to 30 minutes now finish in just two to three seconds, even when scanning datasets as large as 18 million rows.

The performance gains also changed how teams use the warehouse day to day. “We now have a real-time OLAP analytics database,” Ray says. This means stakeholders have faster access to up-to-date traffic and reconciliation data without waiting on daily batch processing.

And speed wasn’t the only win. With the new architecture, Ray says, Verihubs was able to reduce cloud spend, saving up to 50% in infrastructure costs.

## Four lessons from the migration

Ray shared a few lessons Verihubs learned while migrating from Postgres to ClickHouse.

“First,” he says, “database design is crucial.” In ClickHouse, the schema and table layout do a lot of the work. Verihubs focused on keeping schemas as normalized as possible, minimizing joins in downstream queries, and choosing [ordering keys](https://clickhouse.com/docs/integrations/clickpipes/postgres/ordering_keys) carefully. Get those decisions wrong early, Ray notes, and you may end up dropping and rebuilding tables to fix them. 

Table engine choice matters, too. Selecting the right [MergeTree family engine](https://clickhouse.com/docs/engines/table-engines/mergetree-family) is a commitment that shapes how you backfill, query, and insert data over time.

Next, Ray emphasized that ClickHouse’s performance profile isn’t symmetric across all write operations. Inserts are fast, but updates and deletes behave differently. ClickHouse applies mutations gradually, which may surprise teams coming from Postgres. Verihubs ran into moments where they’d applied an update, notified finance, and then had to explain why the numbers hadn’t changed yet, because the mutation hadn’t fully taken effect.

While ClickHouse SQL will feel familiar to Postgres users, it’s “not exactly the same as SQL in Postgres,” Ray says. There are differences in syntax and behavior, especially around [JOINs](https://clickhouse.com/docs/guides/joining-tables) and [ORDER BY](https://clickhouse.com/docs/sql-reference/statements/select/order-by). ClickHouse also comes with an array of built-in functions for time bucketing and transformations. “There are many functions you can use to speed up queries,” he adds.

Finally, Ray cautioned that backfills require planning, especially when materialized views depend on other tables. Unlike projections, materialized views don’t backfill automatically from their source tables. “Think carefully before creating cascading materialized views,” he says, “because you’ll have to backfill repeatedly.”

## Faster, more cost-effective analytics

Verihubs’ migration story underscores a lesson many teams learn the hard way: the database that feels “easy and cheap” at first can become a hidden tax once analytics becomes a core operational workflow. “Over time, it becomes anything but cheap,” Ray says. “Eventually, hosting costs, effort, and mental overhead all get more expensive.”

“ClickHouse lets you redesign for speed while still being cost-effective,” he adds. Streaming through Kafka replaced fragile daily pulls. Choosing the right MergeTree engines aligned the warehouse with how their data changes. Materialized views and projections turned raw, high-volume tables into fast, stakeholder-friendly datasets that support reconciliation and invoicing without bringing the system to a crawl.

With ClickHouse, the things that matter most to Verihubs—speed, cost, and user experience—reinforce each other instead of fighting for priority. Stakeholders get fresher data and faster answers, finance can reconcile and invoice with confidence, and Ray’s team can focus on building and shipping new capabilities.



---

## Get started today

Interested in seeing how ClickHouse works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-1212-get-started-today-sign-up&utm_blogctaid=1212)

---