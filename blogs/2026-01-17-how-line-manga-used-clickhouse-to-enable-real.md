---
title: "How LINE MANGA used ClickHouse to enable real-time analysis without moving a single row"
date: "2025-06-16T13:54:54.158Z"
author: "ClickHouse Team"
category: "User stories"
excerpt: "“We rely on numerous MySQL servers but faced challenges with real-time analysis. Before introducing ClickHouse, we relied on custom scripts for each analysis. This was difficult to develop and review, and execution was slow. ClickHouse’s integration engin"
---

# How LINE MANGA used ClickHouse to enable real-time analysis without moving a single row

"Japanese people read a *lot* of MANGA," says Kazuki Matsuda from [LINE Digital Frontier](https://ldfcorp.com/ja). And that’s no exaggeration. [LINE MANGA](https://manga.line.me/), their digital comic service, sometimes takes the \#1 spot on the Apple Store and Google Play rankings—even ahead of top mobile games.

LINE MANGA is operated by LINE Digital Frontier, a subsidiary of WEBTOON Entertainment, the world’s largest digital comics platform. As of the end of March 2025, the company has around 150 million monthly active users across its MANGA and novel offerings. They use data to analyze reader behavior, optimize recommendations, and track revenue in real time.

But for engineers like Kazuki, LINE MANGA’s growth also brought challenges. Over the years, the platform’s backend evolved into a sprawling network of MySQL databases that were fast and familiar, but increasingly difficult to analyze at scale.

At an [January 2025 ClickHouse meetup in Tokyo](https://clickhouse.com/videos/tokyo-meetup-line-from-stateles-servers-to-real-time-analytics), Kazuki shared how his team solved the problem by using ClickHouse to query MySQL directly, enabling real-time analysis without moving a single row.

<iframe width="768" height="432" src="https://www.youtube.com/embed/3vLpk0ZcMEE" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

<p><br /></p>

## More MySQL, more problems

LINE MANGA wasn’t built overnight. Over more than 10 years, the platform’s architecture evolved to meet the demands of a massive and growing user base. That meant MySQL—lots of it.

To keep things running smoothly, the team implemented both horizontal and vertical sharding. Product data lived in one set of databases, while user data was spread across many others, split by ID ranges. That setup worked well for the app itself, but not so much for analysis.

“With MySQL, things that should have been easy became difficult,” Kazuki says. Something as simple as joining book metadata with user purchase data meant writing custom scripts, figuring out which shard the user lived on, and manually reviewing each query. Even aggregating total sales across the platform was nearly impossible without bespoke code and long wait times.

They did have an internal analytics platform, but it came with its own limitations. Because it relied on ETL pipelines, the data wasn’t always fresh. And some datasets, like financial records or sensitive user data, couldn't be uploaded at all due to internal policies and audit restrictions. “Even if there’s an issue and you want to pull a list of affected users, the data might not be there yet,” Kazuki says. “Or it might be there, but you can’t touch it.”

All of this slowed the team down. Developers spent too much time wrestling with infrastructure instead of getting answers. They couldn’t run fast ad-hoc queries, couldn’t easily debug issues, and couldn’t build a clear picture of user behavior across the system.

At the same time, Kazuki says, rebuilding their stack or migrating away from MySQL would have been risky and expensive. What they really needed was a way to work with the data where it already lived. “That’s where ClickHouse came in,” he says.

## ClickHouse as a real-time query layer

Rather than overhauling their architecture or managing a new set of pipelines, the LINE MANGA team took a different path. ClickHouse offered a way to query MySQL directly, without ingesting or duplicating any data. “We don’t hold the data in ClickHouse,” Kazuki says. “Instead, we reference MySQL on the spot.”

They started by using ClickHouse’s [MySQL Table Engine](https://clickhouse.com/docs/engines/table-engines/integrations/mysql) and [MySQL Database Engine](https://clickhouse.com/docs/engines/database-engines/mysql) to create virtual tables that point to existing MySQL instances. These tables can be queried just like any other ClickHouse table, but under the hood, the queries are pushed down to MySQL, and the results are streamed back for processing. This lets the team join product data and user transactions—even when those records live on completely different servers—and get real-time answers using nothing but SQL.

![2_line_update.png](https://clickhouse.com/uploads/2_line_update_eadd55d64b.png)

ClickHouse joins product and user data by pushing query filters to MySQL shards.

To unify horizontally sharded data, they used the [MergeTree table engine](https://clickhouse.com/docs/engines/table-engines/mergetree-family/mergetree) to define virtual tables across shards. With this setup, the team can run one query to get total sales across all users, with ClickHouse handling the logic of querying each shard and stitching together the results.

![1_line_update.png](https://clickhouse.com/uploads/1_line_update_ad833f828f.png)

ClickHouse queries sharded MySQL data with a MergeTree table to aggregate sales in real time.

Condition pushdown makes the process even more efficient, filtering data at the source before it hits ClickHouse. “This is a key advantage,” Kazuki says. “The data is passed to MySQL, and only the results are sent back to ClickHouse for aggregation. This makes it possible to do horizontal sharding while doing the analysis vertically.”

## Local development, real-world results

At the [Tokyo ClickHouse meetup](https://clickhouse.com/videos/tokyo-meetup-line-from-stateles-servers-to-real-time-analytics), Kazuki gave a live demo of a ClickHouse instance running on his Mac, connected to three MySQL servers spun up with Docker Compose—one for master data, two for user shards. The schemas were identical, but the data was split by user ID range, just like in production. Using [clickhouse-local](https://clickhouse.com/docs/operations/utilities/clickhouse-local), he showed how a single SQL query could join purchase history across shards with book metadata, filter by date, and return accurate results—all without copying anything into ClickHouse.

The demo reflected how the team works in practice. In development, engineers spin up the same environment on their own machines, using IntelliJ to test queries and validate assumptions before anything hits production. It’s fast, easy to debug, and gives them a realistic view of what’s happening across shards, without having to worry about where the data lives.

![0_line_update.png](https://clickhouse.com/uploads/0_line_update_7846e53e84.png)

LINE MANGA uses ClickHouse with IntelliJ and Docker for local development, while production queries pass through an audit-compliant gateway.

In production, the system is more controlled. “We have a setup that includes an audit-compliant gateway,” Kazuki explains. All queries go through that gateway to meet compliance and monitoring requirements. Tasks that used to involve tracking down the right shard or writing custom scripts are now handled with simple SQL. Whether it’s debugging an issue or running a broader analysis, the team can move faster and ask better questions more easily.

## Real-time analytics at scale

For LINE MANGA, ClickHouse was never meant to replace MySQL. The team continues to rely on MySQL as their system of record, using ClickHouse as a way to make that data easier to explore, debug, and analyze in real time. Kazuki explained that while the team has considered other options, including NoSQL and distributed databases, they’ve built a strong engineering culture around MySQL and know how to get the most out of it. “We focus on the benefits, like sub-millisecond queries,” he adds.

Because ClickHouse doesn’t require data ingestion to be useful, it lowers the barrier to entry. Kazuki encouraged others at the Tokyo meetup to try it out, even just in development. Tools like [clickhouse-local](https://clickhouse.com/docs/operations/utilities/clickhouse-local) make it easy to spin up a local instance, connect to existing databases or flat files, and run real queries. “You can easily place a list of target users or IDs in a local file, refer to it as a table, and perform joins to output results,” he says.

Looking ahead, the LINE MANGA team sees their approach as not just a solution to their own challenges, but a model other developers can build on. “We believe this will serve as a helpful reference for improving the developer experience, as well as a good first step towards implementing ClickHouse,” Kazuki says. By keeping things simple, they’ve opened the door to real-time analytics, without adding unnecessary complexity.
