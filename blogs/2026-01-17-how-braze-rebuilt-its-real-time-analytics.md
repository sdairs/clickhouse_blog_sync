---
title: "How Braze rebuilt its real-time analytics pipeline with ClickHouse Cloud"
date: "2025-06-26T15:51:54.052Z"
author: "ClickHouse Team"
category: "User stories"
excerpt: "“It’s a lot faster. The data is consistent. We have to do less work. It’s just way, way better for us.”  Caleb Severn, Senior Engineering Manager"
---

# How Braze rebuilt its real-time analytics pipeline with ClickHouse Cloud

[Braze](https://www.braze.com/) helps some of the world’s biggest brands stay connected with their customers. The multi-channel engagement platform powers everything from personalized emails to in-app messages, SMS campaigns, and push notifications. Every one of those touchpoints generates data—message sends and opens, custom events, profile updates—all of which need to be captured, processed, and made available for reporting in real time.

And we’re not talking small numbers. Braze processed over 3.9 trillion messages and other Canvas actions in 2024. On top of that, it ingests over a billion events per hour, including revenue-generating actions like purchases and signups.

For Braze’s customers—brands like PayPal, Gap, Canva, The Guardian, and Max—“real time” means actionable data without delay. Marketers need to know, often within seconds, whether messages were delivered, who clicked, and whether those clicks converted. As Caleb Severn, senior engineering manager at Braze, explains: “If a customer launches a campaign and refreshes the dashboard, they should see results immediately. If something breaks, they shouldn’t have to wait 30 minutes to figure it out.”

At a [March 2025 ClickHouse meetup in New York City](https://clickhouse.com/videos/meetupny_march_2025_01), Caleb walked through how Braze reimagined its real-time analytics pipeline, replacing a dual-system setup with a faster, more reliable approach powered by [ClickHouse Cloud](https://clickhouse.com/cloud).

## Lessons from running two pipelines

For years, Braze ran a dual-pipeline architecture. Events flowed into one of two systems depending on their intended use: MongoDB powered campaign analytics, while Snowflake handled raw event storage and complex, ad hoc reporting.

The setup evolved over time as Braze ran into scalability challenges performing one write to MongoDB for each new event that was received from a customer. 

To ease the load, the team introduced a Redis buffer to temporarily store events before flushing them to MongoDB in batches. This alleviated pressure, but it added latency, complexity, and potential points of failure. And there were delivery guarantees to think about—Kafka handled those natively, but Mongo didn’t. “With our bespoke MongoDB flusher class, we had to try to re-implement any sort of delivery semantics if we wanted them to match up with Kafka, which meant an extra system to maintain,” Caleb says.

![unnamed (17).png](https://clickhouse.com/uploads/unnamed_17_d0ef658f6e.png)

Braze’s legacy architecture, with events split between Snowflake and MongoDB pipelines.

Pulling data from MongoDB—especially for reports comparing multiple campaigns over long timeframes—often required custom aggregation logic to make it workable.

All of this added up to a growing operational burden. Engineers were juggling two pipelines, duplicating logic, and constantly troubleshooting mismatches. As Caleb puts it, “There’s a very real monetary and human cost of maintaining these two systems, especially when there are issues across them.”

:::global-blog-cta:::

## In search of a better architecture

Caleb and the team knew they needed a stronger foundation—something that could unify their reporting pipeline, scale with their data, and deliver fast, reliable analytics in real time. Their goal was to “simplify the pipeline to source from one single place”—one stream of data from Kafka, one system for querying, one source of truth for customers.

As they explored alternatives, the team laid out their requirements. First, they wanted a managed service. “We’ve done some self-hosted database work at Braze,” Caleb says. “It’s a lot of work and not something we want to support long-term.” 

Local dev tooling also mattered. Local development with existing cloud data warehouses had made iteration painful, and they wanted something easier to work with. Finally, they needed support for high-throughput ingestion from Kafka, fast aggregations, high read volume (10-50 qps), and a cost profile that wouldn’t blow up as usage grew.

[ClickHouse Cloud](https://clickhouse.com/cloud) checked every box. It could stream data straight from Kafka, aggregate on the fly using materialized views, scale horizontally with low ops overhead, and return results fast, even under heavy load. Most importantly, it let the team consolidate their analytics infrastructure without sacrificing speed, accuracy, or developer happiness.

## A simpler, faster system in production

In Braze’s new real-time analytics pipeline, built on ClickHouse Cloud, events stream in from Kafka via the [ClickHouse Kafka Connect Sink](https://clickhouse.com/docs/integrations/kafka/clickhouse-kafka-connect-sink) (“that made things easy,” Caleb says). The data lands in a raw events table, and from there, [materialized views](https://clickhouse.com/docs/materialized-views) roll up key metrics in real time, writing directly to aggregate tables ready for fast querying.

![braze2.png](https://clickhouse.com/uploads/braze2_c1b5073fb4.png)

Braze’s new architecture, with events flowing through Kafka into both Snowflake and ClickHouse.

This setup has eliminated much of the custom logic the team was using in their previous analytics pipeline. Time zone conversions, for example, now happen directly in ClickHouse. “It’s great that we can do these aggregations natively,” Caleb says. “Before, we had to export the data, cast the time zones, and send it back to the customer. That added a lot of overhead, especially on very large datasets.”

Query performance is also night and day. A campaign comparison report that once took more than 8 seconds—even after heavy optimization—now loads in under a second. “With ClickHouse, we do less work to get better results, and the data is consistent,” Caleb says.

That consistency has been a huge win. With all data flowing from Kafka into both ClickHouse and Snowflake, the team no longer worries about mismatches. “We can run reports without any discrepancies,” Caleb says. And even under heavy query loads, the system keeps up. “It’s a lot faster,” he adds. “It’s just way, way better for us.”


## Scaling analytics with ClickHouse

ClickHouse may have started as a solution for real-time campaign reporting, but with the new architecture proving its value in production, Braze has even bigger plans. “We want to continue expanding ClickHouse usage at Braze,” Caleb says. That includes fully migrating their legacy reporting pipelines (many of which still rely on previous database platforms or custom-built infrastructure) and exploring how ClickHouse can support more advanced analytics.

The team is also applying ClickHouse to observability. One live example: an API usage dashboard that gives customers real-time insight into how their systems interact with Braze. It used to run on Elasticsearch; now, it’s faster, cheaper, and more tightly integrated into the product experience.

Looking ahead, the team plans to offload more Snowflake workloads as well, especially those that are performance-sensitive or cost-intensive. “Anything we’re doing in Snowflake now that we can do cheaper or faster in ClickHouse, we want to do that,” Caleb says.

To learn more about ClickHouse and see how it can simplify [real-time analytics](https://clickhouse.com/resources/engineering/what-is-real-time-analytics) for your business, [try ClickHouse Cloud free for 30 days](https://clickhouse.com/cloud)