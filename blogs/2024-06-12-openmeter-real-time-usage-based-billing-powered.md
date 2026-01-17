---
title: "OpenMeter: Real-time usage-based billing powered by ClickHouse Cloud"
date: "2024-06-12T15:35:33.077Z"
author: "Peter Marton, CEO and Co-Founder of OpenMeter"
category: "User stories"
excerpt: "OpenMeter helps AI and cloud companies adopt usage-based pricing models."
---

# OpenMeter: Real-time usage-based billing powered by ClickHouse Cloud

We had the pleasure of hearing Peter Marton, CEO and Co-Founder of OpenMeter, share his company’s data ingestion approach, focusing on their Kafka + ClickHouse architecture at a [recent ClickHouse San Francisco meetup](/videos/kafka-and-clickhouse).

<a href="https://openmeter.io" target="_blank">OpenMeter</a> helps AI and cloud companies adopt usage-based pricing models. To meet the demands of AI businesses and enable real-time use cases such as usage limit enforcement, the OpenMeter team has developed a scalable, robust metering system capable of handling millions of billable events per second, built on top of ClickHouse Cloud. Today, usage-based pricing and billing are critical for many cloud infrastructures, developer tools, and AI SaaS services. However, many companies adopting this approach encounter challenges in ensuring precise metering for accurate billing and providing real-time usage feedback.

Peter credits his background in observability and infrastructure for sparking the idea of developing OpenMeter. During his tenure at Stripe, he recognized the difficulty in collecting usage data from infrastructure components due to the lack of standardized metering. High-quality data was essential, yet collecting, aggregating, and analyzing usage were time-consuming and labor-intensive. With the growing adoption of AI and usage-based pricing models, metering has become crucial for powering billing, cost, and revenue operations. This realization led to the development of OpenMeter, an open-source platform that delivers real-time metering and billing solutions.

![openmeter-1.png](https://clickhouse.com/uploads/openmeter_1_81d9284eab.png)

The presentation at the San Francisco meetup explored some of the challenges of metering. Data needs to be collected, cleansed, standardized to the same one-minute “tumbling windows”, deduplicated, and retained for long periods of time. Unlike observability metrics collected by DevOps, the data cannot be sampled at ingest time or rolled up after a while. 
 
Before ClickHouse, OpenMeter had architecture that was expensive and difficult to maintain, especially as the number of users on the platform grew. It was based on Kafka for event streaming, ksqlDB for aggregations into one-minute tumbling windows, and Postgres for storing pre-aggregated events. This approach had a number of challenges -  mainly resulting from the fact that ksqlDB does not support clusterization, so the team had to do manual sharding and run many separate instances of ksqlDB, which was resource-intensive and operationally complex. 

For the new architecture, robust and scalable collection of metering events was identified as a key requirement. And fast aggregation at search time on top of this data - crucial for customer-facing dashboards where users want real-time insights into the impact on usage on costs.
 
Technical architecture OpenMeter eventually settled on is based on Kafka for event buffering and managing back-pressure, modified [ClickHouse Kafka Connect Sink](https://github.com/ClickHouse/clickhouse-kafka-connect) to handle event deduplication, and ClickHouse [Materialized Views](https://clickhouse.com/docs/en/guides/developer/cascading-materialized-views) with [AggregatingMergeTree table engine](https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/aggregatingmergetree) for converting raw events into tumbling windows as well as long-term analytical data storage. Peter highlighted some of the intricacies of de-duplication and batch data processing, emphasizing the use of Kafka topics partitioned for each customer.  
 
![HIW_light_b.png](https://clickhouse.com/uploads/HIW_light_b_71514fc939.png)

All in all, this talk was a very useful glimpse into OpenMeter’s approach to some of the key challenges surrounding ingesting metering events at high scale, demonstrating how OpenMeter navigated challenges and optimized their architecture with Kafka and ClickHouse. They now have a robust database ingestion architecture suitable for their real-time analytics use cases and one that helps them meet the evolving demands of their customers.  
