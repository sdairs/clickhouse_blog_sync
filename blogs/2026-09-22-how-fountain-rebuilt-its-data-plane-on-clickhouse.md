---
title: "How Fountain rebuilt its data plane on ClickHouse Cloud to power Cue, the Frontline Superintelligence"
date: "2026-09-22T14:52:36.789Z"
author: "ClickHouse"
category: "User stories"
excerpt: "Fountain cut analytics latency from three hours to under two minutes and costs by 66% by rebuilding Cue’s data plane on ClickPipes and ClickHouse Cloud."
---

# How Fountain rebuilt its data plane on ClickHouse Cloud to power Cue, the Frontline Superintelligence

## Summary

- Fountain runs Cue, its agentic AI platform for frontline hiring, on a real-time data plane built with ClickPipes and ClickHouse Cloud.
- Migrating off a multi-vendor BigQuery and S3/Iceberg batch stack to ClickHouse Cloud cut analytics latency from three hours to less than two minutes (with most queries returning in under a second) at roughly 66% lower cost.
- Postgres and MongoDB stream straight into ClickHouse via ClickPipes managed CDC (~8.5B rows and 2,000+ incremental materialized views across 15 deployments).

[Fountain](https://www.fountain.com/) builds solutions for the frontline workforce—the hourly workers in retail, logistics, food service, healthcare, and hospitality who make up the majority of the global workforce. Since 2014, Fountain’s platform has processed more than 91 million applicants and 14 million hires, with 10 products serving customers in over 75 countries.

As a global company powering the frontline hiring cycle from application to start date, Fountain operates around the clock, as do the companies (and their workers) who rely on it. “The frontline doesn’t sleep,” says Alex Norton, Fountain’s head of data platform. “Our customers are hiring, onboarding, and scheduling 24/7 across thousands of locations.”

In the past, Fountain relied on three-hour batch jobs. “This just didn’t serve our customers, who needed to make decisions *now*,” Alex says. So they built [Cue Frontline Superintelligence](https://www.fountain.com/news/fountain-launches-cue-to-run-frontline-hiring-and-workforce-operations), their agentic AI platform that powers frontline operations. With Cue, a frontline hiring manager can observe a signal at 9:02 a.m. and make a decision by 9:05.

> “The half-life of a frontline applicant is minutes, not hours. Moving from three-hour refreshes down to two minutes or less with ClickPipes was really transformational for our customer base.”
>
> — Alex Norton, Head of Data Platform, Fountain

At [Open House SF 2026](https://clickhouse.com/openhouse/san-francisco), Alex and senior analytics engineer Cecily Storey told the story of how they built Cue, from the multi-vendor batch architecture they left behind to the streamlined system they moved to with [ClickPipes](https://clickhouse.com/cloud/clickpipes) and [ClickHouse Cloud](https://clickhouse.com/cloud) on AWS, and how it helped them deliver sub-second queries at roughly two-thirds lower cost.

## Five reasons the old stack ran out of road

Fountain’s old analytics architecture used a traditional batch processing model. Data moved from source databases (13 Postgres production databases and four MongoDB databases) through a third-party replication vendor into S3, landing as Iceberg and Parquet, and then into BigQuery and ClickHouse (using the [s3 table function](https://clickhouse.com/docs/sql-reference/table-functions/s3)) for analytics.

![](https://clickhouse.com/uploads/fountain_sep2026_image3_aec6a983ad.png)

*Fountain’s old batch architecture: costly, brittle, too slow for frontline demands*

“This worked okay for our three-hour refresh pipeline,” Alex says, “but even then it became costly and brittle.” The team was managing a pipeline across multiple vendors and clouds; once MongoDB entered the picture, it became a pain for Fountain’s small data team. “It took a lot of time to maintain, and that’s time we could spend innovating,” he says.

Alex highlights five constraints that ultimately forced the rebuild. The first was freshness: a three-hour cadence was incompatible with agents that act in minutes. The second was cost: a single logical hop generated four separate bills: replication, S3 storage, warehouse ingest, and analytics compute. “Even at three-hour refreshes, the cost ran away from us,” he says.

The third was complexity: three vendors and two intermediate formats meant schema drift at every seam. The fourth was cardinality, as 10B+ row tables and transition windows exploded exponentially. And the fifth was concurrency: with thousands of users across a dozen tenants hitting the same data plane, Alex says, “getting our query latency below 10 seconds was a battle… getting it under a second was an impossibility.”

## Rebuilding with ClickPipes and ClickHouse Cloud

Alex describes the new architecture simply: “We lead with ClickPipes, and everything else sits on top.” Rather than stitch replication, object storage, and a warehouse into one long chain, Fountain uses ClickPipes managed CDC to stream both Postgres and MongoDB directly into ClickHouse Cloud. “One vendor, one connection per source database, zero glue code.”

![](https://clickhouse.com/uploads/fountain_sep2026_image2_a8a396c9e8.png)

*Fountain’s new ClickHouse-based architecture: one vendor, one hop, no scheduler*

[Native JSON](https://clickhouse.com/docs/sql-reference/data-types/newjson) lets Fountain handle MongoDB’s deeply nested documents without string parsing, which, in the old system, Alex says, “became very costly, especially in near real time.” [Incremental materialized views](https://clickhouse.com/docs/materialized-view/incremental-materialized-view) transform data the moment ClickPipes writes a batch, so there's no orchestrator on the data path. And row-level access control keeps each customer’s data isolated by construction, not by a query someone has to remember to write.

The result is two symmetrical pipelines—one for Postgres, one for MongoDB—that each run the same short path: source, ClickPipes, materialized views, Cue. Where the old architecture had two hops, four bills, and schema drift across the seam, the new one has one analytics platform, one hop, and no scheduler.

> “Instead of maintaining multiple analytical platforms, users can rely on ClickHouse as our real-time analytics platform. We’ve reduced costs by 66% and it’s much simpler to maintain.”
>
> — Alex Norton, Head of Data Platform, Fountain

## A deep dive into Fountain’s new architecture

Alex then handed the mic to Cecily Storey, the lead developer on Fountain’s real-time engine, who ran through the four ClickHouse capabilities the data plane rests on: ClickPipes, native JSON, incremental materialized views, and role-based access control.

## ClickPipes

“ClickPipes is the key,” Cecily says. “If you take one feature away from what Alex and I are talking about, it’s that ClickPipes made our real-time model simple and scalable.”

Today, Fountain runs more than 15 connectors feeding over 2,000 incremental materialized views. On the Postgres side, 11 production deployments replicate continuously into [SharedReplacingMergeTree](https://clickhouse.com/docs/cloud/reference/shared-merge-tree) tables, keyed on the Postgres primary key. Every row carries two columns stamped by ClickPipes itself, `_peerdb_synced_at` and `_peerdb_is_deleted`. “There’s nothing else to monitor or pay for,” Cecily says. “There’s no Iceberg layer, no S3 bucket.”

The MongoDB sources follow the same pattern across four databases powering Fountain’s workforce products. Each document lands in a single column of native JSON type. “The pairing of ClickPipes Mongo with the native JSON is what made it really possible for us to surface near real time for the Mongo sources,” Cecily says. All told, the CDC layer holds 8.48 billion rows across 1,550 tables in roughly 953 GiB compressed.

## Native JSON

On the old batch clusters, every MongoDB field had to be pulled out of a string column with a JSONExtract call. “It’s verbose,” Cecily says, “and it’s costly to parse for every field that you need for every single row of data that you’re parsing.”

ClickHouse’s native [JSON data type](https://clickhouse.com/docs/sql-reference/data-types/newjson) replaced all of that with simple dot notation. A field is just `doc.companyUuid::String` or `doc.homeAddress.city::String`, reaching as deep into the document as it needs to, without requiring an extraction function. “It’s fun to not have to put in JSONExtract and JSONValue every time,” Cecily says.

Because it’s schema-on-read, adding a new MongoDB field is a one-line SQL change to the downstream ReplacingMergeTree. “There’s no DDL, there’s no schema registry,” Cecily says. “We don’t have to backfill the ClickPipe itself, because all the data we need already exists in that single doc field.” Nested arrays arrive as arrays of dynamic values that play nicely with ClickHouse’s [array functions](https://clickhouse.com/docs/sql-reference/functions/array-functions) (`arrayMap`, `arrayJoin`, `arrayFirst`, `arrayLast`).

Most importantly, ClickHouse stores the JSON as a columnar substructure internally rather than reparsing a string on every read. “This is a significant win at scale,” Cecily says. “It saves us a huge amount in both CPU and memory consumption.”

## Incremental materialized views

The “heart of the architecture” is how transformation happens. Every materialized view downstream of a CDC source fires the moment ClickPipes writes a batch to the raw table. “It’s like a cascade,” Cecily says. “You make changes in one, it cascades to the next.”

Fountain runs more than 100 models across each of its 15 deployments this way, coding them in dbt and building them directly into ClickHouse. Most land in a [ReplacingMergeTree](https://clickhouse.com/docs/engines/table-engines/mergetree-family/replacingmergetree) (or a plain [MergeTree](https://clickhouse.com/docs/engines/table-engines/mergetree-family/mergetree) for immutable records like transition logs) with the transformation kept deliberately shallow so queries stay fast. “There’s no Dagster, there’s no Airflow, there’s no cron,” Cecily says. “Set it and forget it. The refresh is a property of the storage engine.”

![](https://clickhouse.com/uploads/fountain_sep2026_image4_b4ce2d6ae0.png)

*Transformation without orchestration: ClickPipes writes a batch to the raw CDC table, the materialized view fires, and deduplicated rows land in a ReplacingMergeTree, with no scheduler*

That insert-time model also unlocked the team’s “single biggest performance win.” To answer a common question (“How long did an applicant spend in a given stage?”) they needed each transition’s previous and next timestamps. Instead of running that window function across the whole table at query time, they moved the work into the materialized view, pairing ClickHouse’s [`lagInFrame` function](https://clickhouse.com/docs/sql-reference/window-functions/lagInFrame) with an [`ASOF JOIN`](https://clickhouse.com/docs/sql-reference/statements/select/join#asof-join-usage). `lagInFrame` handles records in the current batch, the `ASOF JOIN` reaches back to what’s already stored, and a [`coalesce`](https://clickhouse.com/docs/sql-reference/functions/functions-for-nulls#coalesce) takes the in-batch value when it exists, falling back to the stored one otherwise.

Computing it once at insert time on the 838-million-row transition table dropped per-query memory from 778 MiB to 153 MiB, an 80% reduction. Generalized across query shapes, the same pattern yields 60-98% memory savings. “Move the expensive shape to your incremental materialized view,” Cecily says, summing up the lesson, “and let your query stay cheap.”

## Security and governance

The final piece of the puzzle was perhaps the most novel: making sure Cue’s LLM can never see or influence the security model. “I had a lot of fun solving this one,” Cecily says.

As Cecily explains, every Cue analytics query runs as a per-deployment service user: “We’ve designed them as basically empty vessels, with absolutely no access on their own.” The access comes from a timestamp-versioned RBAC role that carries the `SELECT` grants and a set of session variables that are empty by default. Fountain’s backend MCP sets those variables at the start of each query, based on who’s asking and what they’re allowed to see, while a row policy on every table filters against the tenant key.

![](https://clickhouse.com/uploads/fountain_sep2026_image1_634502dda3.png)

*Tenant-safe analytics: Cue sets per-caller permission variables, the service user’s role routes the query, row policies filter on the tenant key, and the LLM never knows the security model.*

The security therefore lives entirely in the data plane, never in a `WHERE` clause the model constructs. “Our LLM has zero knowledge of the security model,” Cecily says. “Even if someone tried to prompt-inject our agent, they cannot leak cross-customer data, nor can they access data for products that they’re not allowed to see, because the variables that control for this are all at the database level and specified by our MCP completely outside of the agent LLM.”

And the design fails safely. If the permission variables are missing or invalid, if a role is not applied, or if a new table is not in the RBAC configuration, Cue simply sees no data rather than too much. As Cecily puts it, “This is inherently safe state behavior.”

## The results: faster, cheaper, built to scale

All of this exists to power Cue, Fountain’s agentic analytics and action layer. As Alex puts it, “We went from monitoring dashboards that were aggregating signals collected hours or days in advance, and then actively browsing those dashboards to identify those signals, to instead making this all real-time and allowing Cue to identify those insights and take action.”

Cecily adds numbers behind that transformation, noting, “We went from three hours to well under two minutes, and the reality is that for the vast majority of queries, it’s more like sub-second for our real time path.”

All told, the system now carries 8.48 billion CDC rows replicated continuously by ClickPipes, and 10.3 billion analytics rows across 15 deployments, served by more than 2,000 incremental materialized views. Window-function pre-materialization reduced memory by 60-98%. And compared with Fountain’s old batch-based process, the new platform, built on ClickHouse Cloud, costs around 66% less to run.

## Turning the engine inward

Having built Cue for customers, Alex says they now plan to “turn this engine inward and use it internally for our teams at Fountain.” Using [ClickHouse’s remote MCP,](https://clickhouse.com/docs/cloud/features/ai-ml/remote-mcp) the company will expose its real-time semantic model to internal stakeholders through Claude Desktop (packaged as a plugin with skills) so any Fountaineer can query the data model directly instead of filing a request with the data team. “This is going to be transformative for our product teams, connecting them closer to our data than they’ve ever been,” he says.

What began as a fix for a pipeline that couldn’t keep up has become a foundation the entire company is starting to build on. “Our near real-time pipelines built with ClickHouse are not only transforming the hourly workforce and how it’s managed,” Alex says, “but also how we’re building products to further serve frontline workers.”

---

## Get started today

Interested in seeing how ClickHouse works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-2251-get-started-today-sign-up&utm_blogctaid=2251)

---