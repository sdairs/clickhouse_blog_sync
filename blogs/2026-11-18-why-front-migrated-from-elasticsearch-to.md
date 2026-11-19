---
title: "Why Front migrated from Elasticsearch to ClickHouse for “pixel-perfect” analytics at scale"
date: "2026-11-19T07:05:41.137Z"
author: "ClickHouse"
category: "User stories"
excerpt: "Front powers customer-facing analytics for 9,000+ B2B companies with ClickHouse Cloud, cutting metric development from three weeks to three days and querying 4x more historical data."
---

# Why Front migrated from Elasticsearch to ClickHouse for “pixel-perfect” analytics at scale

## Summary

- Front uses ClickHouse Cloud to power customer-facing analytics across tens of millions of messages per day for over 9,000 B2B companies.
- With Elasticsearch, developing a new metric used to take a senior engineer three weeks; with ClickHouse, a junior engineer can do it in three days.
- For one enterprise customer, a 30-second query that returned 11 days of data in Elasticsearch now returns 1.5 months of data in ClickHouse (a 4x increase)

[Front](https://front.com/) is a customer service platform built for the complexities of B2B. Trusted by over 9,000 companies ranging from small teams to large organizations like Stripe, Zoom, and BCG, it brings teams, conversations, and AI together into one coordinated system, so customer operations stay fast, accurate, and in control.

A big part of Front’s value proposition is analytics. Support leaders and operations managers use conversation data to make business decisions, from scheduling shifts around busy periods, to identifying which product issues are driving the most tickets, to proving whether AI features are actually saving time. With tens of millions of messages flowing through the platform every day, accuracy is as important as speed.

“Our goal is pixel-perfect analytics,” says Louis Cherel, Front’s analytics engineering lead. “We want every single value to exactly match the conversation that happened.”

For years, Elasticsearch handled the job well enough. But as Front’s data expanded and its ambitions grew, the engineering cost became unsustainable. We caught up with Louis and the team to learn how migrating to [ClickHouse Cloud](https://clickhouse.com/cloud) on AWS made queries more powerful, developers more productive, and Front’s analytics roadmap even more expansive.

## Facing engineering bottlenecks

By late 2025, Front was running 25 TB of analytics data across 200 Elasticsearch nodes. The system had served them well over the years, but as Louis says, it required “a strong team that really knows it, knows the quirks of it, and knows how to make it fast.”

The main challenge was Elastic’s query language, Painless. “To make it really fast, you have to write very specific code that’s very tied to Elasticsearch,” Louis says. For Front’s engineers, that meant writing highly specialized scripts for every metric they wanted to expose. Every metric needed its own implementation for each visualization type: a scalar summary card, a data table, a time-series graph, a grouped breakdown by inbox or teammate. “It was complex and required very thorough work to ensure every implementation was correct,” he adds.

The consequences rippled across the business. Adding a single new metric, “even a very obvious one, like number of active accounts,” would take a senior engineer several weeks, Louis says. “We couldn’t let anyone outside of the analytics team create any metric without massive guardrails and very scrutinized review cycles.”

“We didn’t want the analytics team to be the bottleneck for creating new metrics,” adds engineering manager Shelton Wilson. “What we wanted was for every developer within the company to be enabled to create metrics related to the product they were building.”

With a growing product roadmap and a shift upmarket bringing larger and more demanding customers, the analytics team knew they needed a new solution that could scale with their data and engineering resources. 

## Why they chose ClickHouse Cloud

Deciding on a new database didn’t take long. Front needed something built for [aggregating columnar data at scale](https://clickhouse.com/docs/faq/general/columnar-database), and ClickHouse Cloud was the obvious fit. “We decided on ClickHouse because it was literally the tool we needed,” Louis says.

[SQL compatibility](https://clickhouse.com/docs/sql-reference) was a big part of the draw. After years of wrestling with Painless, they loved the prospect of a query language that any developer could read and write. “I’m personally a fan of SQL,” Louis says. “It’s easy to read, easy to learn, and leads to very good performance.”

Another factor was the open-source nature of ClickHouse. “The first thing I did was clone the repository on my computer,” Louis says. “When I have questions, I just go to the repository. I can’t say that about all solutions. ClickHouse is outstanding in that realm of analytics tools.”

## A slow, steady, and seamless migration

Rather than cutting over all at once, Front’s migration strategy was to run ClickHouse in parallel with Elasticsearch, inserting every new event into both systems simultaneously and comparing outputs metric by metric. “We don’t want any discrepancies,” Louis says. “Zero is our target.”

The primary architectural shift was in how Front builds metrics. In ClickHouse each of the roughly 70 metrics exposed to customers is defined once via a single framework that specifies what it measures, which events it counts, and what filters apply. A layer of generators then handles every visualization automatically. “Everything is self-contained,” Louis says. “You specify the filters you want and the framework does the rest.”

Underpinning this is a custom-built ClickHouse query builder, which Louis describes as essentially an abstract syntax tree that assembles optimized SQL from modular components. “You can just create your own filter and push it to the [WHERE clause](https://clickhouse.com/docs/sql-reference/statements/select/where), and it will automatically make the query performant across various visualizations,” he says. “With Elasticsearch, we couldn’t do something like that. With ClickHouse, it’s kind of a given.”

The word Louis uses is “composability,” or the ability to snap components together without duplicating logic or introducing inconsistencies. It’s what the team always wanted, but what Painless made structurally impossible.

The trickiest element was maintaining pixel-perfect accuracy with mutable data. Conversations in Front aren’t static; a customer might delete a message containing PII months after the fact, or merge two threads that turned out to be duplicates. The team solved this using ClickHouse’s [VersionedCollapsingMergeTree engine](https://clickhouse.com/docs/engines/table-engines/mergetree-family/versionedcollapsingmergetree), which tracks and reconciles data changes over time to ensure every number a customer sees is exact.

## Performance boost for customers

With ClickHouse, query performance at scale is no longer a limiting factor. One of Front’s largest customers, a company with around ten thousand users, with millions of reads for a daily aggregation, relies heavily on tags to categorize conversations. Their tag detail report requires computing across 60 GB of row data. With Elasticsearch, Louis could squeeze just 11 days of history into a 30-second query window. “And even that was a stretch,” he says. “I had to fix a bunch of bugs and go deep into Painless.”

The same query in ClickHouse returns a month and a half of data in the same window. “With half the number of machines of equal performance,” Louis says. Shelton adds, “Computing large volumes of data has become a lot easier, which opens up more possibilities for offering customers a better experience when they’re looking at their analytics.”

Those gains cascade down to customers, who now have more flexibility in how they interact with their data. “It’s unlocked so many cases for custom dashboards,” Louis says. “Before, each metric had to go through a whole process. Now the metric is there, every visualization is available, and the customer just clicks and does whatever they want.”

## Internal productivity boosts 

Developer productivity has also seen a big boost. The first metric built entirely within the new ClickHouse framework took a junior engineer just three days to implement, compared to the several weeks it would have taken a senior engineer in Elasticsearch. “That's a very, very big improvement,” Shelton says. “Where Louis and the senior team’s expertise should be is making sure the technical infrastructure is 100% sound, not implementing metrics that anyone can implement now that we have ClickHouse.”

A quieter win came from infrastructure operations. If a customer requested to move from one cloud region to another (e.g. AWS East to AWS West), it used to take days with Elasticsearch. “With ClickHouse, that process takes minutes,” says senior infrastructure engineer Teodor Paius. 

## What’s next for Front and ClickHouse

Shelton says Front has “very big aspirations” for analytics on the platform. “Our ambition is that ClickHouse will enable us to move a lot faster introducing new ways of reporting,” he says.

One near-term project is backlog metrics, measurements like the total number of open conversations that span arbitrary time windows rather than fixed periods. ClickHouse’s ability to materialize computed views makes this feasible for the first time. 

Another is AI-assisted metric creation, where product managers define metrics in plain language and AI translates them into ClickHouse queries. “You’ve removed all the technical complexity from the metric definition,” Louis says. “If you know the business and how it works, you can describe the metric.”

As Front continues its move upmarket, analytics remains a big part of the pitch. “We can already see that the ability to compute this amount of data will be an enabler for that type of client,” Shelton says.

Louis sums up the migration simply: “This whole project has been about stopping being a bottleneck.” By that measure, it’s already working. With ClickHouse, the team that once gatekept every metric is now building the infrastructure that lets anyone at Front create one.

---

## Get started today

Interested in seeing how ClickHouse works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-3083-get-started-today-sign-up&utm_blogctaid=3083)

---