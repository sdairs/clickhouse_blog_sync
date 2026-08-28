---
title: "A universal interface: How QuintoAndar made ClickHouse plug-and-play with managed Postgres"
date: "2026-08-28T11:42:30.889Z"
author: "ClickHouse"
category: "User stories"
excerpt: "QuintoAndar unified ~900 million monthly events in ClickHouse Cloud and used ClickHouse Managed Postgres to make that data accessible to Hightouch and any Postgres-compatible tool."
---

# A universal interface: How QuintoAndar made ClickHouse plug-and-play with managed Postgres

## Summary

- QuintoAndar’s customer data platform runs on ClickHouse Cloud, unifying ~900 million monthly events from 14 million users and serving 300 million API requests.
- The team replaced a costly two-pipeline setup (one system for fast lookups, another for batch processing in Databricks) by writing events directly into ClickHouse.
- Hightouch’s Customer Studio feature doesn’t support ClickHouse, so they used ClickHouse Managed Postgres to bridge the gap, making ClickHouse reachable from any Postgres-compatible tool.

[QuintoAndar](https://www.quintoandar.com.br/), founded in 2013, replaced the guarantor with underwriting of its own. Today it’s the largest housing platform in Latin America, offering a direct, simple, and transparent experience for those looking to rent, buy, or sell a property. It closes more than 15,000 new rental contracts and 3,000 sale contracts every month, with over 650,000 visits scheduled monthly.

Bruno Brito is the tech lead manager on the customer data platform (CDP) team responsible for collecting, integrating, and unifying data about tenants, owners, and agents. “We’re collecting over 1 billion events per month from over 14 million users, with almost 900 million monthly raw events into ClickHouse,” he says. That data is then served back out to chatbots and internal services across roughly 300 million API requests a month.

Bruno joined us on a [recent webinar](https://www.youtube.com/watch?v=lw1wM5OlyW0), where he walked through how his team is rebuilding the CDP on [ClickHouse Cloud](https://clickhouse.com/cloud), from the consolidation to the roadblock that nearly stopped it, and how [ClickHouse Managed Postgres](https://clickhouse.com/cloud/postgres) turned out to be the missing piece.

## Problems with the old Lambda architecture

The CDP starts with mobile user tracking events and change data capture from transactional databases, streamed through Kafka. Both flow into an in-house event gateway, where the team applies governance, runs transformations, and enriches events on the way through. All of it is in service of what Bruno calls the team’s “360 vision around the customer.”

The previous architecture then split along classic Lambda lines. A hot layer (another in-house Postgres service, called Datazord) consumed the gateway’s output topics and served user information to chatbots and other internal consumers through its own Postgres database, chosen for low-latency reads. A cold layer used Kafka Connect to dump everything into a landing zone in the data lake, where 24/7 Databricks workflows processed it into a silver layer that analytical ETLs and Hightouch, their user activation tool, could draw from.

![](https://clickhouse.com/uploads/quintoandar_aug2026_image1_84033a1623.png)

*The previous CDP architecture: output topics from the event gateway split into a hot layer, where Datazord served chatbots from Postgres, and a cold layer running 24/7 Databricks workflows.*

As Bruno explains, there were a few problems. First, the team had to maintain two separate codebases, a familiar tax for anyone who has run a Lambda architecture. Second, in the cold path, enormous volumes of duplicate events meant constant `MERGE INTO` operations against Delta tables. “Duplicating all these millions of events every time was getting expensive not only in cost but in time,” Bruno says. And third, the Postgres instance holding the hot layer was starting to look like the wrong tool for the volume of events moving through it.

“As an architecture, it was kind of complicated,” Bruno says. “So we’re thinking, how can we simplify it, make it faster, and have this high-freshness, low-latency architecture that lets us provide all of this information? … And that’s when we found ClickHouse.”

## Consolidating on ClickHouse Cloud

The team’s answer was to stop treating Kafka topics as the output of the pipeline, and to have the event gateway write directly to ClickHouse instead. Walking through the old diagram, Bruno ticks off what changed: “We can get rid of this, get rid of this, get rid of that… and I can use ClickHouse to support all of our analytical queries.”

In the new architecture, Hightouch would query ClickHouse for user activation, and Datazord could serve its API requests from ClickHouse rather than its own Postgres, still returning results in under a second. That would remove the landing zone, the incessant `MERGE INTO` operations, and the need for a second codebase.

Bruno notes that QuintoAndar’s wider data organization runs Superset over Trino. His team wondered whether they were about to wall themselves off from everyone else. In practice, the answer was no. ClickHouse’s connectors meant Trino and Apache Spark could both reach the CDP’s tables, and ClickHouse could read Delta tables in the company’s data lake going the other way. “Integrating with this stack was not a huge problem for us,” he says.

![](https://clickhouse.com/uploads/quintoandar_aug2026_image3_678b99d857.png)

*The new stack the CDP team is implementing: the event gateway writes directly into ClickHouse, with Superset, Trino, and Spark all able to reach the CDP’s tables.*

## The roadblock: “Where’s ClickHouse?”

ClickHouse looked like the perfect fit. But then came the moment Bruno says all engineers have faced at some point: “You choose a new piece for your architecture, you start testing it, it works fantastic, and then you start integrating with all your other third-party tools…”

At QuintoAndar, Hightouch is central to how the marketing organization operates, syncing audience data out to the platforms that run its campaigns. The marketing team wanted to use its Customer Studio feature, which would let them build audiences, segment users, run A/B tests, and assemble multi-step journeys. However, when Bruno’s team went to the docs to check which sources Customer Studio supports—Snowflake, Databricks, BigQuery, Redshift, Athena, Synapse, MS SQL Server, PostgreSQL, Greenplum, Microsoft Fabric—there was one name conspicuously missing from the list.

“Where’s ClickHouse?” Bruno remembers asking. “It seemed like this awesome solution which would work perfectly for all of our use cases, until it didn’t.”

Databricks was the only qualifying engine already in QuintoAndar’s stack, but the central data team had decided to move away from Databricks SQL Warehouse due to its high cost, favoring open-source alternatives such as Trino, while the CDP team wanted to use ClickHouse. However, Trino wasn’t supported either.

That left one option: Postgres. As luck would have it, ClickHouse had just rolled out a [new offering](https://clickhouse.com/cloud/postgres) that lets teams run analytical and transactional workloads in one unified stack. As Bruno recalls, “That’s when we heard about ClickHouse’s managed Postgres service.”

## The missing piece: ClickHouse Managed Postgres

Connecting Hightouch to [ClickHouse Managed Postgres](https://clickhouse.com/cloud/postgres) lets Postgres reach ClickHouse on its behalf. 

> “All the great performance, low latency, everything great we saw in ClickHouse, we were able to make use of that in Hightouch through ClickHouse Managed Postgres. That was the missing piece of our architecture.” — Bruno Brito, Tech Lead Manager, QuintoAndar

The key mechanism is the [pg_clickhouse extension](https://clickhouse.com/blog/introducing-pg_clickhouse). Setup, he explains, was simple: create the extension, create a foreign server pointing at ClickHouse, create a schema, and import the foreign tables. After that, ClickHouse tables are queryable as ordinary Postgres tables, with joins and aggregations pushed down rather than dragged back into Postgres.

![](https://clickhouse.com/uploads/quintoandar_aug2026_image2_818ed9562a.png)

*Hightouch connects to Postgres managed by ClickHouse, which pushes those analytical queries down to ClickHouse, where the event gateway is already writing events directly.*

Asked what effect the round trip from Postgres to ClickHouse and back has on performance, Bruno says it’s negligible: “For the use case of Hightouch, it doesn’t affect it at all.”

And Postgres isn’t only forwarding queries. Hightouch’s Lightning Sync feature keeps state of its own (a planner table and an audit table) so that scheduled syncs push only what has changed rather than the entire audience every time. Those tables live in Postgres, on NVMe-backed storage. One connection ends up doing two jobs. 

> “It’s persisting data in Postgres just like an OLTP database, but it’s actually running the analytical queries in ClickHouse. So we’re making use of the best of both worlds.” — Bruno Brito, Tech Lead Manager, QuintoAndar

## Managed Postgres as a universal interface

For QuintoAndar, one of the biggest benefits of Postgres managed by ClickHouse is a much simpler architecture. “ClickHouse becomes this plug-and-play database where you can connect to any third-party tool that supports Postgres,” Bruno says. 

That simplicity, he adds, doesn’t come at the expense of governance: “It’s not like Postgres is going to be able to access everything you have in ClickHouse. You still have to create users, roles, and give access to what you want when you need it.”

The team also gets full value out of ClickHouse rather than paying for a second warehouse or query engine to satisfy a single integration. As Bruno says, “You can really leverage ClickHouse’s power and get the most out of it.”

Asked if replacing Hightouch was ever on the table, Bruno says the team never had to consider that option; they could stick with the solution they already had. Going forward, any tool that speaks Postgres can reach ClickHouse in the same way. “You can still make use of ClickHouse,” he says, “even if some of your partners don’t support it yet.”


---

## Get started today

Interested in seeing how ClickHouse works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-1683-get-started-today-sign-up&utm_blogctaid=1683)

---