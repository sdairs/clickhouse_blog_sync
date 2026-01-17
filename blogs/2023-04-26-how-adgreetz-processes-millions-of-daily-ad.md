---
title: "How AdGreetz Processes Millions of Daily Ad Impressions with ClickHouse Cloud"
date: "2023-04-26T07:47:13.634Z"
author: "Elissa Weve"
category: "User stories"
excerpt: "AdGreetz chose ClickHouse Cloud for its data storage and analytics needs, benefiting from faster query speeds, excellent customer support, and cost-effective integration with their high-volume ad impressions tech stack."
---

# How AdGreetz Processes Millions of Daily Ad Impressions with ClickHouse Cloud

[AdGreetz](https://www.adgreetz.com/) is the industry’s leading AdTech and MarTech personalization platform, specializing in the creation and distribution of millions of intelligent, data-driven, hyper-personalized ads and messages. With a reach spanning 26 diverse channels including email, app, Meta, Google/YouTube, TikTok, CTV/OTT and programmatic platforms - AdGreetz processes millions of ad impressions daily. When AdGreetz needed a high-performance, cost-effective solution for their data storage and analytics needs, ClickHouse Cloud emerged as the ideal choice, offering impressive query speed, excellent customer support, and affordability.

## AdGreetz's Data Processing Journey: From AWS Athena to Snowflake and Finally ClickHouse

Initially, AdGreetz was using AWS Athena for their data processing needs, but it struggled to meet their increasing performance and data demands. They then turned to Snowflake and experimented with it for about a month, but the cost proved to be prohibitive for their data volume and query performance. Noor Thabit, a Senior Software Engineer at AdGreetz, explained, “Naturally as an AdTech company, data is the heart of our business, and we have a lot of it. For a small startup budget, the value that we got from Snowflake wasn't great. It's expensive for the performance and features we get. So we went looking for alternatives.”

This search led them to ClickHouse, which delivered high-performance analytics at a substantially lower cost. AdGreetz was particularly impressed with the query speed, rich features, and the exceptional value they experienced using ClickHouse Cloud. Noor highlighted, "With Snowflake, we were using the standard plan, small compute, which cost nearly six times more than ClickHouse Cloud. We got several seconds query time and no materialized views. With ClickHouse Cloud’s production instance, we are getting sub-second query time along with materialized views. The decision to switch was a no-brainer for us.”

Noor also praised the customer support, stating, "What really impressed us, in addition to the great performance, is the customer support. They're fantastic. Every time we had a small issue or a general question, the support team response would be very quick and actually helpful. If it's an incident or a major issue, the support team would take their time to try to replicate the issue and come up with the fix. If necessary, they would schedule a 1:1 meeting with us. It’s been amazing, and it's been consistently like this so far."

## Seamless Integration of ClickHouse into AdGreetz's High-Volume Ad Impressions Tech Stack

AdGreetz handles 5-6 million ad impression events daily, with numbers peaking at 20-30 million during busy periods. These impression events come from ad serving clients around the world, making low latency architecture essential. To manage these events they utilize Cloudflare workers which process the events individually and asynchronously. Each worker handles one event at a time, sending a success response to the client, while simultaneously processing and enriching the event in the background. Once complete, the worker asynchronously inserts data into ClickHouse. Currently, Cloudflare workers only support HTTP connections, not TCP. However, ClickHouse is well-suited for this, as it accepts HTTP requests and enables the direct insertion of JSON payloads without requiring SQL format conversion. This streamlined compatibility simplifies the architecture and eliminates the need for an aggregating component like Kafka. In addition, the ability to query the database over HTTP using TypeScript reduces adoption time and maintains a simplified architecture. With approximately 1.25 billion rows of data stored, ClickHouse's data compression feature efficiently manages storage requirements.

![AdGreetz image1v3.png](https://clickhouse.com/uploads/Ad_Greetz_image1v3_b5523899d3.png)

**Overview of AdGreetz's Ad Processing Architecture**
- AdGreetz receives millions of events daily from vast tag serving servers.
- These events are sent to Cloudflare workers, which handle the processing.
- Cloudflare workers parse the event data and enrich it before sending it to ClickHouse.
- ClickHouse uses the [HTTP/REST interface](https://clickhouse.com/docs/en/interfaces/http) and [async inserts](https://clickhouse.com/docs/en/optimize/asynchronous-inserts) to handle the data insertion. 

To optimize cost and performance, AdGreetz uses a main table along with [materialized views](https://clickhouse.com/docs/en/guides/developer/cascading-materialized-views) for aggregates in ClickHouse. They partition data by time and use Metabase for dashboards and reports, which they then provide externally to their partners who act as intermediaries for end clients. They use views to filter data by customer, ensuring secure separation between different customers' data. Noor emphasizes the importance of this security layer, stating, "we have a view that filters data by customer, providing a layer of security between different customers, without the need to separate the data into different tables."

![Metabase-ss-1.png](https://clickhouse.com/uploads/Metabase_ss_1_8dea9d2a84.png)
![metabase-ss-2.png](https://clickhouse.com/uploads/metabase_ss_2_724f50c6fb.png)
![Screenshot 2023-03-21 at 2.49.55 PM.png](https://clickhouse.com/uploads/Screenshot_2023_03_21_at_2_49_55_PM_397baefd7e.png)
_User-facing, real-time ad performance dashboards for AdGreetz's partners showcasing aggregated impression data_

As a high-performance, cost-effective, and scalable analytics solution, ClickHouse has proven to be an essential component of AdGreetz's tech stack. It enables the efficient processing of millions of ad impressions daily, while its scalable architecture can adapt to AdGreetz's future growth and increasing data volumes.The integration of ClickHouse and its features has helped AdGreetz deliver personalized, data-driven advertising experiences.

Visit: [https://www.adgreetz.com/](https://www.adgreetz.com/)

