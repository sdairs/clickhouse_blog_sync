---
title: "How Infinitas Learning uses ClickHouse Managed Postgres to process billions of events for 1.6M unique learners"
date: "2026-11-16T10:54:45.411Z"
author: "ClickHouse"
category: "User stories"
excerpt: "Infinitas Learning runs transactions for 1.6 million learners on ClickHouse Managed Postgres and serves real-time analytics to teachers from ClickHouse Cloud, where distributed cache cut P99 latency from about 13 seconds to 410 milliseconds."
---

# How Infinitas Learning uses ClickHouse Managed Postgres to process billions of events for 1.6M unique learners

## Summary

- Infinitas Learning, one of Europe’s largest educational publishers, uses ClickHouse to process results for 1.6 million learners and 324 million assignments a year.
- Transactional workloads run on ClickHouse Managed Postgres, where P50 latency dropped from milliseconds to double-digit microseconds after migrating from Neon.
- Customer-facing analytics run on ClickHouse Cloud, where support-led optimization and distributed cache cut P99 latency from ~13 seconds to 410 milliseconds.

How Infinitas Learning uses ClickHouse Managed Postgres to process billions of events for 1.6M unique learners

[Infinitas Learning](https://www.infinitaslearning.com/) is one of Europe’s largest educational publishers, with publishing companies in the Netherlands, Belgium, Portugal, Poland, and Sweden. In the 2025-2026 school year, the group sold more than 25 million books. As engineering manager Jerome van den Heuvel puts it, “If you live in the Netherlands and have children in secondary education, you’ll most likely find some books from our Dutch publisher, Noordhoff, at your home.”

Along with books, Infinitas Learning runs digital platforms where learners complete assignments and take tests online. Last school year, 1.6 million unique learners completed 324 million assignments on those platforms. Each assignment generates events that have to be recorded, turned into an updated picture of each learner’s progress, and served back in real time.

At our [Open House 2026 roadshow in Amsterdam](https://clickhouse.com/openhouse/amsterdam-2026), Jerome and data engineer Ana Lacruz described how the Results & Insights team at Infinitas Learning uses [ClickHouse Managed Postgres](https://clickhouse.com/cloud/postgres) to ingest and process billions of events and how the search for fast, stable analytics took them from [ClickHouse Cloud](https://clickhouse.com/cloud) to self-hosting and back again.

## The database becomes the API

Two years ago, Infinitas Learning’s primary and secondary education platforms were each managing assignment results and basic insights on their own, with important logic repeated in multiple places. “We set ourselves a mission to unify and collect those learner results into one solution that scales, with the domain knowledge concentrated in one team,” Jerome says.

They started with what he calls a “textbook implementation,” a resilient event-sourced system built on Apache Kafka. The platforms sent data through an API into multiple Kafka topics using Avro schemas, with Java and Apache Flink moving data between topics until it landed in a Postgres database the platform teams read from. “Technically this was pretty awesome,” Jerome says, “but it was complex and carried significant overhead.”

![](https://clickhouse.com/uploads/infinitas_oct2026_image1_b897968b7b.png)

Infinitas Learning’s educational platform teams, he recalls, had three requests for the system: “Can you make it transactional? Can you make it real-time? And can you make it easier to use?” The first two were especially hard in the eventually consistent system they had created.

So the team kept what was working and simplified where they could. “With that, we became proud members of the Postgres-for-everything movement,” Jerome says.

In the new setup, events enter the system through public functions defined in Postgres using PL/pgSQL, which the platform teams invoke directly. “There’s no REST API layer, just the database,” Jerome says. The underlying tables and views aren’t accessible to the platforms, which prevents “doom queries” that could bog down the database. On every event, the system computes the new state of an assignment as well as the learner’s overall progress, which the platforms use to decide the next assignment and populate progress dashboards.

While the setup proved ideal for recording what each learner did, it struggled to make sense of all of that data at once. “We learned very quickly that Postgres was not meeting our requirements for analytics,” Jerome says. “That’s why we also introduced ClickHouse to our stack.” (More on that in later sections.)

![](https://clickhouse.com/uploads/infinitas_oct2026_image2_50d94e6fa3.png)

## From Neon to ClickHouse Managed Postgres

With everything on Postgres, the team needed somewhere to run it. They started on Azure’s managed Postgres service, but it couldn’t meet their demands for performance and uptime. So in early 2025, they moved to Neon. “We liked Neon,” Jerome says, “but we ran into some functional problems.”

For one, major Postgres version upgrades were challenging. Cache size was coupled to unpredictable compute, which meant “data that could easily have been served from cache suddenly needed more CPU and memory resources.” Features the team wanted to try, like the [pg_clickhouse extension](https://clickhouse.com/blog/introducing-pg_clickhouse), weren’t available. In the end, the Azure region they were using was deprecated within Neon, giving them no choice but to find a new solution.

Around the same time, ClickHouse introduced [ClickHouse Managed Postgres](https://clickhouse.com/cloud/postgres), a unified data stack that combines Postgres for transactions and ClickHouse for analytics. The team evaluated it, liked what they saw, and decided to migrate.

From there, things were simple. They created the environment, built the schema manually, and set up [ClickPipes](https://clickhouse.com/cloud/clickpipes). All 750 GB of data was copied within 16 hours. The cutover, done together with Infinitas Learning’s primary and secondary education platform teams in a 20-minute timeframe, required no downtime, thanks to logical replication between the old and new servers.

> “It was as simple as switching endpoints. A migration that took us weeks in the past was now done in two days on ClickHouse Managed Postgres.”
>
> — Jerome van den Heuvel, Engineering Manager, Infinitas Learning

The first thing that impressed them was server performance. “Our P50 latency is now measured in double-digit microseconds instead of milliseconds, and P99 latency in double-digit milliseconds instead of seconds,” Jerome says. During a heavy load test, CPU remained “pretty much flatlined.” Beyond raw speed, he also highlights the benefit of having “ClickHouse and Postgres under the same roof,” the level of integration between them, and the tooling and detailed metrics that come with the service.

## ClickHouse Cloud for customer-facing analytics

While the team was sorting out where Postgres should live, the ClickHouse side of the Results & Insights team’s stack was also taking shape.

The analytics the team builds are real-time and customer-facing, served straight to teachers. “Nobody wants to wait seconds for a page to load, and teachers are no exception,” she says. “So our bar for response time is high, and that’s the main driver for us—latency.”

Infinitas Learning’s first experiments with customer-facing analytics began three years ago with what Ana says they “lovingly nicknamed the throwaway solution.” Built before the move to Postgres, it was always meant to be temporary. Data flowed from source systems through Airbyte to Snowflake, then through Azure Data Factory into Azure SQL Server, and finally into dashboards. With multiple tools chained together to copy, transform, and enrich the data, it was “nowhere near real time,” and the pipeline was built for one narrow use case that was both costly and difficult to extend.

![](https://clickhouse.com/uploads/infinitas_oct2026_image3_3b31f011f9.png)

Once Postgres became the system of record for learner results, they tried using it for analytics too. “We reached the same conclusion many teams have before us,” Ana says. “Postgres is great for transactions, but it doesn’t scale for the analytics we need.”

They went looking for an OLAP database to pair with Postgres and landed on [ClickHouse Cloud](https://clickhouse.com/cloud). “It promised the performance we needed,” Ana says. “The compression just by itself surprised us.” One table holds almost 2 billion rows, with 300 GB uncompressed reduced to just 27 GB in ClickHouse, an 11x reduction. “ClickHouse also comes with some great tools that are easy to work with,” she adds, highlighting features like [ClickPipes](https://clickhouse.com/cloud/clickpipes), ClickHouse Cloud’s native ingestion layer; [materialized views](https://clickhouse.com/docs/concepts/features/materialized-views), which precompute query results as data arrives; and [dictionaries](https://clickhouse.com/docs/concepts/features/dictionaries), which hold reference data in memory for fast lookups without joins.

But while the team thought they had done everything right—denormalizing everything from Postgres into one table, loading all contextual data into dictionaries, eliminating joins entirely—tail latency remained a problem. A query that usually took 200 milliseconds would sometimes jump to several seconds. With a P99 SLA of 500 milliseconds, spikes reached as high as 13 seconds. “Performance was great most of the time,” Ana says. “Most of the time was not good enough.”

## Taming tail latency with distributed cache

They discovered the culprit was cache misses, made worse by the table’s [primary key](https://clickhouse.com/docs/concepts/best-practices/choosing-a-primary-key), a high-cardinality UUID that comes from a different system and that the team can’t control. UUIDs index badly, Ana explains, and ClickHouse has to check every table part for a match because it has no good way of knowing where a given UUID lives, then load all of that data into cache. “All of this adds up,” she says. To make matters worse, continuous inserts kept invalidating the cache, and any new replica started with an empty one, so the team also had to disable autoscaling. “It worked, but performance was not stable,” Ana adds.

Since reading from cache was fast, the team wondered if the problem traced back to ClickHouse Cloud’s [separation of storage and compute](https://clickhouse.com/docs/products/cloud/reference/architecture). “Could we get the stability we needed by hosting ClickHouse ourselves?” Ana remembers asking. “The answer was yes.” With the move to self-hosting, P50 dropped to 80 milliseconds and P99 to 300 milliseconds.

Self-hosting, however, was difficult to manage. “We got everything we wanted—but at a price,” Ana says. “Now we were also *responsible* for everything. We ran a single replica, which was simple to manage but meant we had nothing to fall back on. Recovery from any failure would be slow. We were worried about something going wrong, and this made us avoid updates. We ran like this for months, still building dashboards, while we watched every ClickHouse release for a way we could go back to Cloud.”

Eventually, they did return. “This time, we were not alone,” Ana says. “The ClickHouse support team worked with us and took our optimizations to the next level.” Together, they reviewed the team’s data model, queries, compression, and table settings. They optimized for reads and cranked up merges, since fewer parts means less to scan. Queries that once peaked at 13 seconds now topped out around two seconds. “This was good enough for us to move back knowing we still had an ace up our sleeve,” she says.

That ace was [distributed cache](https://clickhouse.com/blog/building-a-distributed-cache-for-s3), a shared cache layer that keeps hot data available across all replicas. ClickHouse enrolled Infinitas Learning in the private preview just before the team went live for the new school year. “Instead of forcing merges to speed up reads, what we did is turn on every single setting that prewarms the cache,” Ana explains. “We now rely on distributed cache to fetch our data, so we barely have to read from disk anymore.”

In load tests, P99 came in at 410 milliseconds, under the team’s 500-millisecond target and close to what they had achieved self-hosting.

> “Coming back from open source to ClickHouse Cloud, we’re now very happy with the performance we’re getting. We also don’t manage upgrades, and all the features that come with a fully managed service, like autoscaling, make life much easier.”
>
> — Ana Lacruz, Data Engineer, Infinitas Learning

![](https://clickhouse.com/uploads/infinitas_oct2026_image4_373154c769.png)

*P50 and P99 latency across Cloud v1, self-hosted, optimized Cloud, and Cloud with distributed cache.*

## ClickHouse and Postgres, better together

Today, Infinitas Learning’s primary and secondary education platforms talk to two databases for learner results: Postgres for transactions, ClickHouse for analytics. “That’s two connections, two data models, two systems to keep in sync,” Ana says.

“Our vision is to collapse that into one,” she continues, explaining that the plan is to use the [pg_clickhouse](https://clickhouse.com/blog/introducing-pg_clickhouse) Postgres extension as the under-the-hood link between the two, pushing query execution down to ClickHouse so that transactions and analytics live behind a single service. “The same place a client records a test is the same place that it reads back a whole classroom’s progress over a year,” Ana says. “One connection, one source of truth, transactions and analytics, both powered by ClickHouse Cloud.”

The pairing has already changed how fast the team can ship. “At Infinitas Learning, we want to be bold and move fast without breaking things,” Ana says. “The ClickHouse ecosystem helps us do exactly that. We can now take a dashboard or a widget from proof of concept to production-ready with real data in a matter of hours.” She credits ClickHouse’s support team with “the best support and level of engagement we’ve had in many years working in IT.”

“The reason all this matters isn’t the technology,” she adds. “It’s that our team can now spend its time on actionable insights so we can help 1.6 million learners reach their full potential and support their teachers guiding them along the way. Everything we’ve built ties back to our purpose at Infinitas Learning: empowering teachers and learners to grow.”

---

## Get started with ClickHouse Managed Postgres today

Interested in seeing how ClickHouse Managed Postgres works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?intent=pg&loc=blog-cta-3034-get-started-with-clickhouse-managed-postgres-today-sign-up&utm_blogctaid=3034)

---