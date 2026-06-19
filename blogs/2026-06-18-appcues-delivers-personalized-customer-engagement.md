---
title: "Appcues delivers personalized customer engagement with ClickHouse Cloud"
date: "2026-06-18T16:21:05.000Z"
author: "ClickHouse"
category: "User stories"
excerpt: "Appcues cut P95 query times 90%, ingestion latency 99%, and analytics spend 23% by migrating from Snowflake and Airflow to ClickHouse Cloud for real-time segmentation across 1.31 PB of data."
---

# Appcues delivers personalized customer engagement with ClickHouse Cloud

## Summary

- Appcues uses ClickHouse Cloud to support real-time analytics and segmentation across 1.31 PB of data and 410 billion events.
- While their previous technology stack, which included Airflow and Snowflake, worked well for batch reporting and dashboards, Appcues wanted to innovate and deliver real-time, customer-facing analytics.
- Now, Appcues cut P95 query times by 90% from 20+ seconds to <2 seconds, and reduced ingestion latency by 99% from 10+ minutes to 5 seconds.
- Even as workloads expanded to support new capabilities, Appcues reduced analytics spend by 23%.


[Appcues](https://www.appcues.com/), a platform that helps SaaS companies engage their customers to drive growth and lives inside its customers’ products, powering things like onboarding flows, tooltips, checklists, banners, emails, and push notifications. Customers send Appcues data from SDKs, Segment streams, CRMs, and public APIs so Appcues can help them, as Chris Brookins, VP of Engineering puts it, “deliver the right experience to the right customer at the right time.”

Today, Appcues manages 1.31 PB of data, has processed 410 billion events, and continuously updates over 1 billion user profiles. “We’re ingesting a ton of data from all these apps,” Chris says, “and there’s a lot of observability we need to provide.” Much of that data shows up in Appcues Studio, where customers track performance and outcomes. 

> “It’s very important that all this information is aggregated and delivered quickly for over a billion user profiles. Page load time has to be practically instant.”
>
> — Chris Brookins, VP of Engineering, Appcues

Appcues had spent years running its analytics platform on a stack that included Airflow and Snowflake. While Snowflake remains a strong solution for BI and reporting, delivering the real-time product analytics experience that customers increasingly expect requires a different approach. At our Boston meetup, Chris shared the journey that ultimately led them to [ClickHouse Cloud](https://clickhouse.com/cloud) on AWS.

## Challenges to delivering a delightful product experience

From the beginning, the platform ran on two main databases. DynamoDB handled the sub-second work of matching live visitors to segments, so Appcues could decide, before the next page load, which experiences to show. Snowflake powered analytics, including dashboards, performance graphs, NPS results, and the reporting customers rely on to tell whether their experiences are actually working. 

“Our aim is to create a delightful product experience for our customers,” Chris says. However, as Appcues scaled to ingest more and more data, query times went up to 20 seconds and costs became a challenge to manage as their previous stack wasn’t meant for low-latency analytics at scale. 

To increase query speeds, Appcues relied on Airflow. Every five to 10 minutes, jobs would roll up and pre-process data before writing it back. This delivered the product experience they were looking for, but it added costs and meant maintaining a growing web of jobs and servers. This setup also meant that customers were limited to looking at data in 10 minute windows.

When the team decided to introduce email, Chris' team knew they needed a new solution that was highly performant for real-time analytics and cost efficient. “That was a whole new channel with all sorts of new events and extra segmentation needs,” Chris says. Historically, Appcues was optimized to answer a direct, real-time question: *Which segments does this user belong to*? But with email, they needed to calculate, very quickly, *all the users in a segment*, across hundreds of segments per customer, with complex conditions based on historical behavior and even negative logic like “hasn’t been seen in 30 days.”

## Putting ClickHouse to the test

They started with a list of must-haves. As a small team, they wanted minimal operational overhead. They also wanted an open-source engine for transparency and optionality. After their experience with their previous cloud data warehouse, cost efficiency at scale was a huge priority. And any solution had to support HIPAA-compliant workloads and a future EU data center region. “It was a lot of requirements,” Chris admits. “We wanted to stress test everything possible.” He sent principal engineer Andy LeClair to a ClickHouse meetup to learn more, and those conversations became the start of an evaluation plan.

The first step was to export all Snowflake data to Parquet in S3 and load it into ClickHouse. Appcues also notified customers that ClickHouse would be used as a new sub-processor, since the platform stores a lot of personally identifiable information. 

The proof of concept focused on the email segmentation challenge. “A lot of these segments were very complicated,” Chris explains. “They had AND/OR conditions, nested conditions. They could refer to other segments of users or historical events, like, ‘Has this thing ever occurred in the last three months?’ It was a lot of work.”

In parallel, the team began laying the foundation for production. Events flowed through Kafka into a new “clickwriter” consumer for light deduplication and fast inserts. On the application side, the segment logic was formalized into a “clickclient” library, built on Elixir’s Ecto, giving the team a single, controlled way to generate complex ClickHouse queries.

Testing both their previous data warehouse and ClickHouse, they tuned each platform as far as they could. In ClickHouse’s case, features like [SharedReplacingMergeTree](https://clickhouse.com/docs/cloud/reference/shared-merge-tree) proved “huge in terms of improving performance,” Chris says.

By the end, the outcome was clear: ClickHouse ran the segment queries 73% faster. 

> “No matter how we tuned our previous cloud data warehouse, ClickHouse was faster. We were like, ‘Alright. This is a go.’”
>
> — Chris Brookins, VP of Engineering, Appcues

## Migrating to ClickHouse Cloud

From there, the project became a one-year, in-flight migration. “We were doing this while the plane was flying,” Chris says. “We had to ensure there was accuracy all through the project.”

With historical data already loaded into ClickHouse, the next phase was a steady loop of verification and iteration. The team refined their schema, learned how ClickHouse wanted data to be modeled, and worked closely with the ClickHouse team to choose the right [table engines](https://clickhouse.com/docs/engines/table-engines) and [materialized views](https://clickhouse.com/docs/materialized-views). Chris says. “The migration taught us a lot of positive practices. We developed a lot of discipline in terms of data management, moving to ClickHouse,” says Chris.

That discipline mattered, because Appcues’ data is hardly uniform. “Customers can send us anything,” Chris says. “It’s just key-value pairs.” Reports had to work across wildly different customer data shapes, from small startups to large enterprises. The team tested continuously across accounts, using edge cases to pressure-test the system before exposing it broadly.

As confidence grew, they began operationalizing ClickHouse Cloud in earnest. Different workloads were isolated into appropriately sized services, [autoscaling](https://clickhouse.com/docs/manage/scaling) rules were tuned, and the team “rinsed and repeated” until it was stable. Only then did they begin cutting customers over in waves. 

For those enterprise customers especially, the difference was night and day. “With our previous setup, there were queries that would take a week to complete, and other things they just couldn’t even do,” Chris says. “Our largest customers are thrilled.”


---

## Get started today

Interested in seeing how ClickHouse works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-962-get-started-today-sign-up&utm_blogctaid=962)

---

## Appcues’ new ClickHouse-based setup

By the time Chris took the stage in Boston, Appcues’ analytics system looked very different. At a high level, it now takes a noisy stream of key-value events and turns it into fast, queryable tables that match how the product actually needs to reason about users and experiences.

All events flow through Kafka into Appcues’ “clickwriter” consumer, which performs light deduplication before inserting data into ClickHouse. From there, data is split into two main families: experience analytics—impressions, completions, surveys, and outcomes tied to customer workflows—and user and group profiles, built from streams of property updates that must resolve into a clean, current-state view.

The deployment model reflects Appcues’ scale and compliance needs. Their primary ClickHouse warehouse runs five services with two to three replicas each, thirteen replicas total. Those services take advantage of what Chris calls “ClickHouse’s very fast upscaling and downscaling,” growing from modest instances with 16 GB of memory and 4 vCPUs to machines with over 1 TB of RAM and hundreds of cores during peak demand, then scaling back down to manage cost. A separate, fully isolated warehouse serves HIPAA customers.

[Materialized views](https://clickhouse.com/docs/materialized-views) are key to making this work at scale. Where Airflow once rolled up data every few minutes, ClickHouse now precomputes counts and sums at insert time. “That dramatically improved all our queries,” Chris says. “We were able to eliminate all of our Airflow infrastructure—all of that cost and, most importantly, all of that latency.”

For profile data, [SharedReplacingMergeTree](https://clickhouse.com/docs/cloud/reference/shared-merge-tree) sits at the heart of the design. Updates arrive as events, and ClickHouse resolves them into flattened profile tables. One important optimization was learning when *not* to use [FINAL](https://clickhouse.com/docs/sql-reference/statements/select/from#final-modifier). “We were trying to do all this in real time and not slow anything down,” Chris says. “We found that using [argMax](https://clickhouse.com/docs/sql-reference/aggregate-functions/reference/argmax) instead took stress off the system, while allowing us to get the latest user profile with minimal overhead.”

Late in the project, a final challenge emerged: deletes. Appcues provides self-serve APIs for GDPR and test-data deletions, and some customers generate a constant stream of them. Traditional deletes triggered expensive background merges, and as volume grew, they found themselves facing a growing backlog, with GDPR’s 30-day delete clock ticking.

The solution came with [ClickHouse 25.6](https://clickhouse.com/blog/clickhouse-release-25-06) and the introduction of [lightweight deletes](https://clickhouse.com/docs/guides/developer/lightweight-delete). “Its lightweight patch-part mechanism allowed us to blow through these deletes immediately,” Chris says. “All of a sudden, we were past our major challenge. That was awesome.”

## Faster queries, fresher data, lower cost

Previously, P95 query times hovered around 20 seconds. On ClickHouse, P95 is under two seconds—a 90% improvement—despite the fact that Appcues has added more workloads and features on top of the system. Even P99 and max latencies, Chris says, are “not that much higher… they’re very reasonable.”

The improvements in ingestion latency are even more impressive. Previously, thanks to those Airflow-based rollups, it could take 10 minutes or more for new events to show up in reports. But with ClickHouse, it’s closer to five seconds. “That’s 99% faster from the moment an event hits our servers to the moment you can query the results in ClickHouse,” Chris says.

Cost, meanwhile, has dropped significantly even as capabilities have expanded. Even with all the new segmentation and email workloads layered into ClickHouse, reducing the overall analytics stack by 23%, costs now scale more predictably as usage grows. 

Part of that comes down to the basic economics of [how cloud data warehouses bill for compute](https://clickhouse.com/blog/how-cloud-data-warehouses-bill-you) and [how different execution and scaling models translate performance into cost](https://clickhouse.com/blog/cloud-data-warehouses-cost-performance-comparison). In a provisioned “warehouse” model, scaling performance and concurrency often means scaling the meter right along with it. ClickHouse Cloud gives Appcues a more flexible way to size and autoscale compute to the workload they actually have.

For Chris and the Appcues team, this is only the beginning. “We didn’t stop there,” he says. “It wasn’t just a parity project.” The team has already started to push the platform further, rolling out new funnel reports that use ClickHouse [window functions](https://clickhouse.com/docs/sql-reference/window-functions) to show how users are progressing through workflow and messaging pipelines. They’ve also added AI-powered natural-language insights, with agents leveraging the “clickclient” query library to answer customer questions about product and user activity, benchmarks, and product adoption.

Now with ClickHouse Cloud, Appcues finally has an analytics platform that can keep up with real-time product decisions, support new channels and features, and scale efficiently without becoming a drag on the business. 

> “We’re thrilled with the results, and thrilled with the support we got from the ClickHouse team.”
>
> — Chris Brookins, VP of Engineering, Appcues
