---
title: "How Rokt Achieved Real-time Reporting with ClickHouse"
date: "2023-03-07T16:23:20.635Z"
author: "ClickHouse Editor"
category: "Community"
excerpt: "Vadim Semenov, Engineering Manager in charge of Reporting and Analytics at Rokt, presents his team's use case for ClickHouse."
---

# How Rokt Achieved Real-time Reporting with ClickHouse

<iframe width="764" height="430" src="https://www.youtube.com/embed/BEP07Edor-0" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>

<br/>

On December 6, 2022, Vadim Semenov, Engineering Manager in charge of Reporting and Analytics at Rokt, presented his team's use case for ClickHouse at the NYC meetup. Rokt is a global marketing technology company that specializes in developing e-commerce marketing tools to help companies personalize their customer experiences and drive revenue growth.

During the meetup, Semenov discussed the data Rokt collects, including views, clicks, purchases, and various events, and how they use this data to provide different types of reporting, including aggregated data sets, [real-time reporting](https://clickhouse.com/resources/engineering/what-is-real-time-analytics), and platform effectiveness measurement. Rokt also performs anomaly detection to determine if any issues arise on their end or the client's end.

![Rokt architecture.png](https://clickhouse.com/uploads/Rokt_architecture_fa449f41a4.png)

## Challenges with Reporting Systems
Rokt explained they have different types of users, including internal business analysts, client services or account managers, external users who access their data through their website or APIs, and other systems that use their datasets. The architecture of Rokt's reporting system was complicated, with external events going through Kafka and various Spark streaming and structure streaming applications that push data to a data lake backed by S3. Batch jobs produce data that was loaded to either Redshift or Elasticsearch.

However, Rokt faced several challenges with their architecture, such as limited customer data slicing and dicing capabilities, resulting in more requests for custom reports. This put pressure on the business analytics (BA) and reporting teams to provide custom reports instead of doing their primary work. 

To address these challenges, Rokt needed a new user interface (UI) that provided more group-by capabilities and filtering. “Our current setup with Elasticsearch wouldn't support it. So we decided to look into other databases on the market that would,” said Semenov. “The other parts about Elasticsearch that we didn't like, is it's not easy to ingest data because you have to basically do pushes, there's no load from S3, there are no joins, so labels must exist somewhere. If you change some label, you have to re-ingest all the data.” 

Semenov explained that there are several issues in querying the data with Elasticsearch. “It's difficult to query as you have to do JSON. You have to have some gateway that would translate your SQL to JSON or just fire JSON queries directly. And overall it leads to data duplications.”

## The Search for a Better Database
Rokt looked into other databases that could provide better support, since they faced difficulties with Elasticsearch. Semenov explained they evaluated several alternatives, including Apache Pinot, Druid, Citus Data, StarRocks, Snowflake and ClickHouse.

“Pinot and Druid are more real-time focussed. There were no joins. I was told that Druid supports it now in some limited capability, and obviously you cannot fire off all kinds of different SQL queries. Snowflake is more of a data warehouse and it's expensive,” said Semenov. “StarRocks claims to be a competitor to ClickHouse, but it's too fresh to use in production, and Citus Data is too Postgres oriented. Microsoft acquired them and they don't plan to support AWS obviously. So we decided to look closer at ClickHouse, and we really like it.”

This led them to benchmark ClickHouse against Redshift. They set up their own cluster with instance SSDs and EBS and found that ClickHouse was three times less expensive than Redshift without cache. 

“You can see that ClickHouse outperforms Redshift easily”, said Semenov. The performance of ClickHouse was consistent in returning results, with some spikes possibly related to the network storage. They also tested the performance of ClickHouse with different levels of concurrency, which showed predictable growth and a maximum query time of six seconds, and found that they could fire up to 200 queries per second. 

“‘We also looked at the size of the data that we load. On S3 we had different events stored. It was about 500 gigabytes in Parquet gzip, and once we loaded it into ClickHouse, we saw that it only takes about 500 (gigabytes) as well,” Semenov said. 

They compared this to the storage required for the same data in Elasticsearch. “For Elasticsearch we've made the same calculation and it turns out it's about six times more, so we can save some money on actual storage,” Semenov said. 

Semenov also provided an overview of their current setup, which included ClickHouse nodes in their own autoscaling group, ZooKeeper, and network load balancers and target groups spread across different nodes.

![Rokt overview.png](https://clickhouse.com/uploads/Rokt_overview_f08a1d62c3.png)

## Advantages of ClickHouse Cloud
Semenov discussed they soon plan to migrate to ClickHouse Cloud as it has several advantages for backups and data analytics, mentioning that using ClickHouse Cloud can solve many problems related to replication, sharding, and scalability. He explained that ClickHouse is particularly good at ingesting data from Kafka and using SQL to analyze real-time data. Additionally, ClickHouse has built-in dictionaries that make joins easier and reduce the need for API queries to different databases and services.

The NYC ClickHouse meetup was an excellent opportunity to learn about the challenges and solutions in data reporting for a leading e-commerce company. With ClickHouse, Rokt was able to achieve consistent and predictable results, reduce storage costs, and analyze real-time data more efficiently. 

## More Details
- This talk was given at the [ClickHouse Community Meetup](https://www.meetup.com/clickhouse-new-york-user-group/) in NYC on December 6, 2022
- The presentation materials are available on [GitHub](https://github.com/ClickHouse/clickhouse-presentations/blob/master/meetup67/Building%20the%20future%20of%20reporting%20at%20Rokt.pdf)