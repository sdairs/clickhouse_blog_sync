---
title: "Why Astronomer chose ClickHouse to power its new data observability platform, Astro Observe"
date: "2025-03-10T15:41:46.125Z"
author: "Julian LaNeve"
category: "User stories"
excerpt: "Read how Astronomer chose ClickHouse Cloud to power Astro Observe, its new observability platform helping data teams proactively monitor and troubleshoot Apache Airflow workflows at scale with lightning-fast queries and minimal overhead."
---

# Why Astronomer chose ClickHouse to power its new data observability platform, Astro Observe

<iframe width="768" height="432" src="https://www.youtube.com/embed/Vkj3lPXc5Wk?si=o6uD7uukKtFWCqya" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
<p/>

Every modern data-driven company relies on workflows to move, transform, and process data. For many of them, [Apache Airflow](https://airflow.apache.org/) is the tool of choice. An open-source workflow management platform with over 30 million monthly downloads and a vibrant community of nearly 3,000 contributors, it powers everything from ETL jobs to machine learning pipelines to productionizing generative AI workloads.

But while Airflow is highly extensible, scalable, and easy to use, managing it at scale is another story entirely. As companies grow, so do their Airflow deployments, often evolving into sprawling networks of hundreds or even thousands of pipelines. Keeping them running smoothly and troubleshooting failures when they happen becomes increasingly complex.

That’s where [Astronomer](https://www.astronomer.io/) comes in. Similar to how Confluent and Databricks built managed platforms for Kafka and Spark, respectively, Astronomer created [Astro](https://www.astronomer.io/product/), a fully managed platform that helps organizations run, scale, and optimize Airflow without the operational burden. Today, hundreds of companies, from Fortune 10 enterprises to five-person startups, rely on Astro to bring mission-critical analytics, AI, and software to life. And Astronomer isn’t just a platform provider: its team contributes close to 60% of Airflow’s code, drives 100% of the project’s releases, and employs 19 of the community’s top committers.

"We’re fortunate to work with a very broad customer base," says Astronomer CTO Julian LaNeve. "Airflow is at the core of every customer’s data platform, whether they’re building analytics dashboards, operational reports, machine learning pipelines, or AI systems."

At a [December ClickHouse 2024 meetup in New York](https://www.youtube.com/watch?v=Vkj3lPXc5Wk), Julian and Astronomer software engineer Christine Shen shared the story behind their new observability product, [Astro Observe](https://www.astronomer.io/product/observe/) — including why they chose [ClickHouse Cloud](https://clickhouse.com/cloud) to handle billions of workflow events.

## The need for Astro Observe

Quickly identifying and fixing failures is a big part of maintaining reliable data pipelines. A single broken task can throw off entire workflows, delaying reports, disrupting AI models, or blocking downstream applications. But with thousands of scheduled jobs running in parallel, pinpointing where something went wrong is rarely straightforward and often requires digging through logs, tracing dependencies, and manually cross-referencing multiple systems.

As Julian and Christine explain, when a failure occurs, data teams must work through a series of troubleshooting steps, each of which takes time. "First, you have to figure out what failed," Julian says. "Then you have to figure out when it failed. Was it yesterday? A week ago? Then you have to figure out why it failed, which is the most ‘fun’, because the reason can be quite obscure. And most importantly, you have to understand the impact of the failure."

At Astronomer’s scale, even a small percentage of errors adds up fast. On one of its platforms, Astro users executed 18 million DAGs (Directed Acyclic Graphs) — Airflow’s fundamental unit of orchestration, which defines dependencies and execution order for tasks — and 100 million tasks in a single month. Of those tasks, 1.5% failed, with each failure taking an average of 1.24 hours to resolve before Observe.

"That’s a lot of hours per month just debugging failed pipelines, which isn’t fun for anyone," Julian says. "This is a problem we care a lot about solving, because all of our customers run into this. Observe takes the root-cause-analysis process from hours to seconds, which frees up hours per week of those data engineers’ time."

Launched in late 2024, Astro Observe was designed to eliminate the guesswork. Instead of relying on scattered logs and manual troubleshooting, it provides a single, centralized view of workflow health. Teams can instantly see what failed, when it happened, and what downstream jobs were affected, without piecing together data from multiple systems. It also helps track SLAs and data freshness, sending alerts before minor issues snowball into major problems and ensuring key processes stay on schedule.

![astronomer.png](https://clickhouse.com/uploads/astronomer_e9dc0a8229.png)

By turning Airflow monitoring into a proactive process, Astro Observe reduces downtime and frees engineers from endless troubleshooting cycles. But for Astronomer, making this vision a reality required a database capable of handling billions of real-time events with low query latency and minimal maintenance. That’s when they turned to [ClickHouse Cloud](https://clickhouse.com/cloud).

## Choosing the right database

Astronomer initially built a data lineage product on Amazon RDS for PostgreSQL, provisioning a separate database for each customer to keep workloads isolated. This setup worked fine at smaller stages, but as event volumes grew, it became harder to manage. Query performance degraded over time, particularly for analytical queries spanning large time ranges or requiring complex aggregations. The team also had to carefully limit the amount of stored data since retaining too much could negatively impact performance.

Around the same time, Julian met Ryan Delgado, Ramp’s Director of Engineering, at a ClickHouse event. They discussed Ramp’s recent adoption of ClickHouse for their real-time analytics use cases. "We were looking for something that solved similar problems," Julian says. Based on a strong endorsement from Ryan and ClickHouse’s reputation for lightning-fast query speeds, the Astronomer team decided to give it a try.

Their tests confirmed that ClickHouse could handle large-scale event ingestion while maintaining sub-second query performance, even across billions of records. Queries that had been computationally expensive in Postgres ran much faster, and the system supported high-throughput workloads without the need for extensive tuning.

Along with improving performance, ClickHouse Cloud simplified operations, providing a fully managed service and eliminating the need for infrastructure management. 

<blockquote>
<p>"ClickHouse Cloud has been great to work with. Managing it is super easy – we hardly have to think about it, and their team has been very helpful and responsive."</p>
<p>Julian LaNeve, Astronomer CTO</p>
</blockquote>

## Astro Observe’s data architecture

Astro Observe’s data pipeline starts with an Ingestion API, which collects event data from Airflow deployments and routes it for processing. These events include DAG and task run statuses, execution times, and error states.

Once ingested, events flow into Kafka, which acts as a buffer and event stream processor before writing to ClickHouse. Astronomer’s ingestion layer, built with Go-based microservices, enriches these events with organization metadata and pipeline dependencies, ensuring they’re structured correctly for downstream analysis. Kafka’s fault tolerance and replayability prevent data loss due to network disruptions or processing delays.

![astronomer_architecture.png](https://clickhouse.com/uploads/astronomer_architecture_b5f87a30f6.png)
_Astro Observe's data pipeline: Ingesting Airflow events into ClickHouse._

In addition to runtime events, Astro Observe also tracks configuration and code changes. Updates from the Deployments API and GitHub integrations are lower in volume and don’t require buffering, so they bypass Kafka and are written directly to ClickHouse.

Within ClickHouse, events are stored in a single table optimized for fast time-based lookups and efficient aggregations. A common schema structure links all tables via fields such as `org_id`, `run_id`, and `asset_id`, making it easy to track failures across different levels of the pipeline. 

At the same time, each event type retains unique attributes. For example, task execution events track fields like `duration`, `state`, and `type`, while deployment-related events capture configuration changes and metadata updates. This design allows Astro Observe to quickly retrieve event histories, identify failure patterns, and power its real-time observability dashboards.

![astronomer_schema.png](https://clickhouse.com/uploads/astronomer_schema_3b0ef14a03.png)
_ClickHouse schema: each event type has its own table, with common and event-specific fields._

## The benefits of ClickHouse

With the rollout of Astro Observe, ClickHouse has introduced several key advantages that simplify data management and improve query performance. At the meetup in New York City, Julian and Christine highlighted some of the ways ClickHouse Cloud has helped bring the observability platform’s capabilities to life.

### Scalability

Unlike traditional databases that require complex schema migrations, ClickHouse allows Astronomer to scale easily by adding new tables as needed. This flexibility is essential as the volume of Airflow event data continues to grow. "We’ve found it really easy to scale by adding new tables for new use cases," Christine says.

### Automated data retention

With billions of events flowing through Astro Observe, efficient data storage is a priority. Instead of relying on manual cleanup processes, ClickHouse’s [TTL (Time-to-live)](https://clickhouse.com/docs/en/guides/developer/ttl) feature automatically removes older records, so that only relevant data is retained. "We’re able to set specific TTLs on each of the tables, which helps automate data cleanup," Christine says.

### Data deduplication

Duplicate records can drive up storage costs and skew analytics, especially in a high-volume observability system. ClickHouse’s [MergeTree table engine](https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/mergetree) eliminates duplicate records, keeping event logs clean and making sure queries return accurate results. "ClickHouse takes care of deduplication for us, which is pretty neat," Christine says.

### Materialized views

Many observability queries require aggregating vast amounts of event data, which can be computationally expensive when performed on demand. 

<blockquote>
<p>"ClickHouse’s <a href="https://clickhouse.com/docs/en/materialized-view">materialized views</a> have been extremely helpful in allowing us to precompute all of those at insertion time instead of at read time, which allows us to query a lot faster."</p>
<p>Christine Shen, Software engineer</p>
</blockquote>

## Scaling Airflow observability

Astronomer's mission has always been to make Airflow easier to use, more scalable, and more reliable for data teams of all sizes. With Astro Observe, they’ve extended that mission into observability, allowing organizations to monitor and troubleshoot workflows proactively. By providing a clear picture of pipeline health, Astro Observe reduces time spent debugging and lets engineers focus on building new use cases rather than maintaining existing ones.

ClickHouse Cloud helps make all of this possible. Its ability to handle billions of workflow events in real time, while keeping query performance high and operational complexity low, means Astronomer can provide a top-notch observability experience without having to manage database infrastructure. As Astro Observe continues to evolve, ClickHouse’s speed, scalability, and flexibility will ensure that Astronomer’s customers can keep their Airflow environments running smoothly, no matter how complex their data pipelines become.

To learn more about ClickHouse and see how it can improve the speed and scalability of your team’s data operations, [try ClickHouse Cloud free for 30 days](https://clickhouse.com/cloud).

