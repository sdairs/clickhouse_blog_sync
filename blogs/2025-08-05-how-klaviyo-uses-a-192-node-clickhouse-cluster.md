---
title: "How Klaviyo uses a 192-node ClickHouse cluster for real-time segmentation and personalization"
date: "2025-08-05T16:55:05.252Z"
author: "ClickHouse Team"
category: "User stories"
excerpt: "“Our customers want to identify trends in their customer base and interact meaningfully with their customers. ClickHouse powers the engine for that.”  Patrick McGrath, Lead Software Engineer"
---

# How Klaviyo uses a 192-node ClickHouse cluster for real-time segmentation and personalization

If you’ve ever gotten a perfectly timed text or email about a product you’ve been eyeing, you know how much timing and personalization matter. For consumer brands, it can be the difference between a missed opportunity and making the sale.

[Klaviyo](https://www.klaviyo.com/) was created to help brands get more from their customer data. Today, companies like Glossier, Vans, Dollar Shave Club, and nearly 170,000 others use it to deliver personalized messages across email, SMS, mobile push, and more. Its B2C CRM brings marketing, service, and analytics into one platform, helping brands drive revenue and build stronger customer relationships.

Segmentation is one of Klaviyo’s most powerful features, and one of its biggest technical challenges. Every day, the platform ingests billions of events and profile updates, computes tens of billions of segment memberships, and keeps everything fresh as new data streams in. That requires queries to run fast, reliably, and at massive scale.

As a lead software engineer in Klaviyo’s data platform group, Patrick McGrath’s team builds the backend services and query infrastructure that turn raw data into real-time insight. Their mission: unify data across the stack and make it actionable, so brands can engage the right customers at the right time. “ClickHouse powers the engine for that,” he says.

At Open House, [Patrick sat down with ClickHouse solutions architect Jake Vernon](https://clickhouse.com/openhouse#video-klaviyo) to talk about the value of segmentation, how Klaviyo rebuilt its system with ClickHouse, and which new ClickHouse features he’s most excited to bring back to the team.

<iframe width="560" height="315" src="https://www.youtube.com/embed/3K8Cz5dWwl0?si=9zN7LzGzRY4VePPH" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

## From hours to seconds with ClickHouse

Real-time segmentation is one of Klaviyo’s superpowers. It’s how brands discover patterns in customer behavior, target high-value users, and trigger timely, relevant campaigns. Whether someone browsed a product, signed up recently, or hasn’t opened an email in a while, personalization is all about seeing the right data and acting on it quickly.

“Our customers want to be able to identify trends in their customer base and interact meaningfully with their customers,” Patrick says. “A lot of that is about targeted marketing, creating a segment of users that qualify for certain criteria, and then targeting them.”

Klaviyo’s original segmentation engine was orchestrated in Python, with logic scattered across multiple systems, including MySQL databases and a massive Cassandra cluster storing pre-aggregated event counters. But this architecture had major limitations. For large customers, segment evaluation could take over an hour. Pre-aggregating data meant computing metrics in advance, even if they were never used. Making changes, like adding a new condition, could require replaying more than a trillion events.

To make matters worse, Patrick adds, “The solution we had was also really expensive.”

 :::global-blog-cta::: 

By 2022, the team was ready for a change. They began exploring alternatives and landed on ClickHouse. Its [columnar design](https://clickhouse.com/docs/faq/general/columnar-database), speed, scalability, and rich SQL capabilities gave them the flexibility they needed. Their engineers already had experience using it, which made adoption easier. “We knew it was fast, and that it could satisfy our use case,” Patrick says.

What followed was a [full system rebuild](https://clickhouse.com/videos/rebuilding-segmentation-with-clickhouse)—30 epics, 117 features, and 821 user stories over the course of a year. Now, instead of spreading logic across systems, Klaviyo replicates all segment-relevant data into ClickHouse and computes memberships with a single query. “We just execute the query,” Patrick says, “and we can compute a segment in one second.”


## Optimizing for real-time performance

Today, Klaviyo runs ClickHouse at massive scale. Their main segmentation cluster spans 192 nodes and uses [bi-level sharding](https://clickhouse.com/docs/engines/table-engines/special/distributed)—first by company ID, then by profile ID. Every day, it handles billions of updates and tens of billions of segment membership changes across millions of segments. With ClickHouse, the company is saving “a significant amount of money on infrastructure,” Patrick said when describing the system rebuild in 2023.

But their work didn’t stop there. With the new system in place, the team quickly shifted gears to tuning performance and making sure it’s optimized to scale as the company grows.

As Patrick described at a [ClickHouse meetup in Boston in January 2025](https://clickhouse.com/videos/klaviyo-boston-meetup), many of Klaviyo’s segments rely on time-based filters, such as “opened an email 3-5 days ago.” Not only are these filters common—roughly 60% of segments use them—they’re also computationally expensive, since they require constant reevaluation over time. 

Initially, Klaviyo reprocessed segments on a fixed schedule, whether anything had changed or not. That led to a ton of wasted work. The same profile might be added to the same segment three days in a row, burning compute for no real reason.

To solve this, the team rethought how trait data was stored and queried. They built an entity-attribute-value (EAV) table using a [materialized view](https://clickhouse.com/docs/materialized-views), and included the property name in the sort key. That made it easy to zero in on just the data relevant to a specific condition (e.g. birthday or event timestamp) rather than scanning the whole dataset.

“The key lesson was pushing down as many conditions as possible when reading data,” Patrick says. This allowed them to scope updates to only the affected profiles.

The system now works in two phases. A lightweight query identifies which profile-segment pairs need updating. Those results get chunked, pushed to a message queue, and then picked up by parallel workers that handle the updates. This separation lets Klaviyo scale the heavy-lifting phase independently, keeping things snappy even as data volumes grow.


## What’s next for Klaviyo and ClickHouse

While Klaviyo runs ClickHouse on-prem today, Patrick sees plenty of value in [ClickHouse Cloud](https://clickhouse.com/cloud)’s architecture. “There’s a lot of benefits to being able to leverage object storage,” he says. “The separation of compute and storage allows you to scale compute elastically. You don’t have to manage EBS and virtual machines yourself. That’s really neat.”

At Open House, he shared his thoughts on a few new ClickHouse features, including [native support for updates](https://clickhouse.com/blog/highlights-from-open-house-our-first-user-conference#lightweight-updates), a long-requested addition that simplifies workloads where data needs to be modified after insert. He also highlighted the [Postgres CDC Connector for ClickPipes](https://clickhouse.com/cloud/clickpipes/postgres-cdc-connector), which allows real-time replication from Postgres into ClickHouse. “It opens up a world of query possibilities,” Patrick says. “You can run transactional queries in Postgres and then execute really quick analytical queries in ClickHouse, which solves so many needs.”

But perhaps the feature that resonated most—and that feels closest to Patrick and his team’s work at Klaviyo—was ClickHouse’s new [Model Context Protocol (MCP)](https://clickhouse.com/blog/integrating-clickhouse-mcp). Built to support AI agent workflows, it helps LLMs retrieve and make sense of ClickHouse data in natural language, so agents can query and reason over it on the fly.

“That’s something Klaviyo is interested in as well—making our customers’ data useful to them, so they can understand who their customers are,” he says. “It’s neat to see parallels there.”

With ClickHouse, Patrick and his team at Klaviyo are reimagining what’s possible with real-time segmentation. As the platform grows to support even more great products, features, and brands, they have the foundation they need to keep innovating at scale.

To learn more about ClickHouse’s new features and improve the speed and scalability of your team’s data operations, [try ClickHouse Cloud free for 30 days](https://clickhouse.com/cloud).