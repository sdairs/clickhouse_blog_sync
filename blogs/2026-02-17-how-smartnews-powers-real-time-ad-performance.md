---
title: "How SmartNews powers real-time ad performance dashboards with ClickHouse"
date: "2026-02-17T08:35:59.304Z"
author: "ClickHouse"
category: "User stories"
excerpt: "“With our old setup, we kept hearing complaints from customers that it was way too slow. But with ClickHouse, we can now display real-time aggregation results to advertisers.” - Ryu Kiyose, Engineering Manager"
---

# How SmartNews powers real-time ad performance dashboards with ClickHouse

## Summary

<style>
div.w-full + p, 
pre + p,
span.relative + p {
  text-align: center;
  font-style: italic;
}
</style>

SmartNews uses ClickHouse to power real-time ad performance dashboards for thousands of advertisers on Japan’s \#1 news app. Since migrating from Redshift to ClickHouse, user-facing queries that used to take several hours in their old setup now return in just a few seconds. They now handle around 3 million queries and 60,000 inserts per hour, with most reads completing in under 100 milliseconds.

Founded in 2012, [SmartNews](https://www.smartnews.com/) has grown into the \#1 news app in Japan, with more than 50 million downloads. Its business model relies heavily on advertising: users interact with the app, advertisers deliver their campaigns, and SmartNews shares a portion of that revenue with its 4,500+ media partners. As engineering manager Ryu Kiyose puts it, “This motivates them to provide even more high-quality content, which we then deliver to our users.”

But to keep that cycle running, advertisers need timely feedback. When Ryu joined the company in 2020, ad performance data often took hours to reach them. One of his first projects was to fix that. Today, the same data typically arrives in just a few seconds.

At our [April 2025 meetup in Tokyo](https://clickhouse.com/videos/tokyo-meetup-smartnews-15apr25), Ryu shared how SmartNews rebuilt its analytics pipeline with ClickHouse, replacing a slow, batch-driven system with a fast, streaming engine that now powers millions of queries per hour.

## From batch to real-time visibility

Prior to ClickHouse, SmartNews’s pipeline involved multiple steps. Ad delivery logs were written to Amazon S3 every 15 minutes, then processed in hourly batches and loaded into Amazon Redshift for aggregation. From there, the results were exported to Amazon RDS, where they could be queried by SmartNews’s Ads Manager dashboard. 

“This entire end-to-end process took about two to three hours,” Ryu says. “We kept hearing complaints that it was way too slow.”

![SmartNews User Story Issue 1232 (4).jpg](https://clickhouse.com/uploads/Smart_News_User_Story_Issue_1232_4_d53ff5c28b.jpg)

SmartNews's pre-ClickHouse pipeline circa 2021: batchy, delayed, fragile.

In 2021, they overhauled the system. Now, ad delivery data is streamed through Kafka before being inserted into ClickHouse. Flink is used, too, though Ryu notes that it’s “not doing anything special”—just copying data due to some internal technical requirements. “All of our business logic and aggregation logic is handled within ClickHouse,” he says.

![SmartNews User Story Issue 1232 (3).jpg](https://clickhouse.com/uploads/Smart_News_User_Story_Issue_1232_3_37c469ffcc.jpg)

SmartNews's current ClickHouse-based pipeline: streaming, real-time, scalable.

The new architecture is simpler, and the performance gains have been passed on to end users. “End to end, the fastest processing time is about 2 to 3 seconds,” Ryu says. “By connecting to Ads Manager, we can display real-time aggregation results to advertisers.”

## Serving millions of queries per hour

For each campaign, SmartNews’s Ads Manager dashboard lets advertisers see metrics like budget spend, impressions, click counts, click-through rates, and more. “We’re sending data here in real time, and the latest data is always available in ClickHouse,” Ryu says. 

The system runs around 60,000 insert queries per hour, or roughly 1,000 per minute, representing about 20 GB of data. These continuous inserts ensure that advertisers can view the latest results with minimal lag.

On the read side, the platform handles approximately 3 million SELECT queries per hour, or around 100 per second, across several thousand advertiser accounts. Most queries complete in under 100 milliseconds. “That’s quite fast,” Ryu adds.

## Scaling from EC2 to Kubernetes

When the team first rolled out ClickHouse, they deployed it on AWS EC2 using a basic four-node cluster with two shards and two replicas per shard. Each node had its own local table, with [distributed tables](https://clickhouse.com/docs/engines/table-engines/special/distributed) layered on top and [materialized views](https://clickhouse.com/docs/materialized-views) used for aggregation.

![SmartNews User Story Issue 1232 (1).jpg](https://clickhouse.com/uploads/Smart_News_User_Story_Issue_1232_1_96884692ff.jpg)

ClickHouse on EC2: 2 shards with 2 replicas each—simple and reliable.

It was a straightforward, reliable setup. But as data volume grew, so did the need for something more flexible. “Recently,” Ryu says, “our infrastructure has been evolving rapidly.”

To ensure what he calls “future scalability and flexibility,” the team migrated everything to Kubernetes. They’re still running with four nodes, but now use three shards with two replicas per shard, allowing for greater parallelism and better workload distribution.

![SmartNews User Story Issue 1232.jpg](https://clickhouse.com/uploads/Smart_News_User_Story_Issue_1232_e8f91b21c4.jpg)

ClickHouse on Kubernetes: 3 shards with 2 replicas each—more flexible and scalable.

ClickHouse’s architecture made this kind of scaling simple. Each node still has its own local table, while distributed tables span the entire cluster. On top of that, the team performs aggregations and writes to separate summary tables to keep queries fast and efficient.

## A clean, efficient pipeline

When Ryu was a university student, he and his peers had a saying: “Talk is cheap, show me the code.” What that means, he says, is “rather than just talking about something, people want to see the actual code.” True to his word, he delivered at the Tokyo meetup, walking through the structure behind SmartNews’s real-time reporting pipeline.

The architecture is intentionally simple. After Flink receives ad events (e.g. clicks, impressions), it writes them to ClickHouse in mini-batches, inserting “hundreds or even thousands of rows at a time.” These records land in a raw “ads action” table, with each row containing the log type (click or impression), campaign ID, timestamp, and other metadata.

![SmartNews User Story Issue 1232 (2).jpg](https://clickhouse.com/uploads/Smart_News_User_Story_Issue_1232_2_d10d073dec.jpg)

SmartNews’s ad event pipeline: Flink to ClickHouse with materialized views.

From there, [materialized views](https://clickhouse.com/docs/materialized-views) take over. These views aggregate the raw rows into an “ads report” table that groups impressions and clicks by campaign and time window. The logic is simple: if the log type is “impression,” it increments the impression count; if it’s “click,” it increments the click count. The team uses ClickHouse’s [ReplicatedSummingMergeTree engine](https://clickhouse.com/docs/engines/table-engines/mergetree-family/replication) to sum up values efficiently during ingestion.

By pre-aggregating data on the way in, the system avoids scanning massive volumes of raw events at query time. “This significantly reduces the amount of data,” Ryu explains. “That way, queries are much lighter when displaying on the dashboard.”

It’s a clean, efficient pipeline. Raw events go in, real-time summaries come out. For most reporting needs, that simplicity is exactly the point.

## Calculating ad reach in real time

While the data pipeline is simple by nature, one of the most technically challenging parts is calculating ad reach—specifically, the number of unique users who’ve seen an ad.

Unlike impressions or clicks, which can be summed in real time with straightforward logic, reach requires counting unique users across large datasets, often over dynamic and unpredictable time windows. “This is actually pretty challenging,” Ryu says, “because the time period isn’t fixed. If you want to calculate the distinct count for a specific period, it’s hard to pre-aggregate or compress the data in advance.”

To solve this, SmartNews uses ClickHouse’s [uniqCombined function](https://clickhouse.com/docs/sql-reference/aggregate-functions/reference/uniqcombined), which implements a variant of the [HyperLogLog algorithm](https://en.wikipedia.org/wiki/HyperLogLog)—something Ryu describes as “almost like magic.” Instead of tracking every unique user ID, the system stores a compressed intermediate “reach state.” This state doesn’t carry much meaning on its own, but it enables fast, memory-efficient estimation of distinct counts when queried.

The logic fits neatly into the broader architecture. As new ad events flow into the raw action table, materialized views use ClickHouse’s aggregate functions to update the reach state. When queried, the reporting tables return approximate distinct counts grouped by campaign and time window. This approach lets SmartNews balance performance and accuracy using tunable parameters built into the function.

To test how well it worked, the team ran a series of accuracy experiments. For campaigns with up to 500 unique users, the counts were 100% accurate. At 40,000 users, the margin of error rose slightly to around 2%, and remained in that range even as counts scaled into the millions. The algorithm is designed to keep the error rate stable regardless of the total number of records, making it well-suited for estimating high-cardinality metrics like ad reach.

Query performance also held up under scale. For a week’s worth of data, the team measured a P95 latency of 1.2 seconds. A full month of data returned in about 3 seconds, while three months took roughly 5 seconds. “This is fast enough,” Ryu says—especially for a real-time dashboard querying compressed estimates at scale.

## Speed, scale, and simplicity

SmartNews’s investment in ClickHouse has brought newfound speed, scale, and simplicity. Instead of a slow, batch-based reporting system, they’ve built a real-time analytics platform that delivers valuable performance insights to advertisers within seconds. 

Core logic that once spanned multiple tools now runs entirely inside ClickHouse. Materialized views, efficient table engines, and approximate aggregates now power everything from high-volume dashboards to deeper campaign analytics.

For Ryu and the team, the impact goes beyond faster queries. It’s about having a foundation flexible enough to grow with the business. ClickHouse gives them the confidence to keep innovating, expanding the platform, and supporting advertisers across Japan.

---

## Looking to scale your team’s data operations?

Interested in seeing how ClickHouse works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-64-looking-to-scale-your-team-s-data-operations-sign-up&utm_blogctaid=64)

---