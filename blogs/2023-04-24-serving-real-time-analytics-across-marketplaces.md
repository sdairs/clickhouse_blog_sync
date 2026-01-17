---
title: "Serving Real-Time Analytics Across Marketplaces at Adevinta with ClickHouse Cloud"
date: "2023-04-24T07:47:12.275Z"
author: "Elissa Weve"
category: "User stories"
excerpt: "Adevinta’s mission is to provide the best user experience for buying and selling goods and services online. To achieve this objective, Adevinta required a centralized analytics and dashboarding tool to monitor their seller's advertisements."
---

# Serving Real-Time Analytics Across Marketplaces at Adevinta with ClickHouse Cloud

[Adevinta](https://www.adevinta.com/), a leading online classifieds specialist, operates more than 25 platforms across 11 countries worldwide. Their household brands include Marktplaats in the Netherlands, Mobile.de in Germany, and Leboncoin in France, reaching hundreds of millions of people every month. These platforms are all about matchmaking, and help people find whatever they’re looking for in their local communities – whether it’s a car, an apartment, a sofa, or a new job. Every connection made or item found makes a difference by creating a world where people share more and waste less.

Adevinta’s mission is to provide the best user experience for buying and selling goods and services online. To achieve this objective, Adevinta required a centralized analytics and dashboarding tool to monitor their seller's advertisements, track interactions, and improve performance in real-time. After assessing various cloud-based database services like Google BigQuery, Cloud Spanner, and ClickHouse Cloud, they determined that ClickHouse Cloud was the most cost-effective option that could provide high performance and scalability across multiple marketplaces.

## User-Facing Real-Time Analytics and Dashboarding for Sellers

Adevinta’s Central Data Products team is tasked with building data and machine learning (ML) products to support their various marketplaces. To start with, they focus on specific marketplace problems, devise data solutions, and subsequently expand and scale to other marketplaces. This presents a complex challenge, as they need to constantly consider aspects such as reusability, uptime, and scalability.

To meet the needs of their sellers, Adevinta required a [user-facing real-time analytics](https://clickhouse.com/resources/engineering/what-is-real-time-analytics) and dashboarding solution that would allow the sellers to monitor their advertisements in real-time. This includes tracking views, favorites, and likes, capturing every interaction that occurs on their marketplaces. 

![Adevinta image1.png](https://clickhouse.com/uploads/Adevinta_image1_409e3b29ff.png)
_User-facing performance dashboards showing sellers their advertisement statistics in real-time_

Varun Krishnani, Engineering Manager for Apollo Ad-Growth, one of the Central Data Product teams, explained, "We needed a solution that could scale, but also provide end-user facing analytics capabilities with low latency and high throughput." A few years ago ClickHouse was selected for [real-time analytics](https://clickhouse.com/engineering-resources/what-is-real-time-analytics) and implemented as a self-managed environment. However, when Adevinta planned to migrate all its applications to the cloud, the team evaluated various solutions to determine the best fit for their needs.

![Adevinta image 2.jpg](https://clickhouse.com/uploads/Adevinta_image_2_8a1904294d.jpg)
_Adevinta's data pipeline utilizes Apache Beam Data Flow, running on Google DataFlow, in conjunction with Google Cloud Pub Sub event bus. The data is accessed through a Java client for querying._

## Moving to the Cloud
Adevinta evaluated several cloud-based database services, including ClickHouse Cloud, Google BigQuery, and Cloud Spanner. 

Their main requirements were:
- Fully fledged database service - performant, efficient, has capabilities like indexing, disaster recovery, backup and restore etc.
- Low operational complexity - no site reliability engineer (SRE) required, schema evolution
- Managed service and easily scalable
- Cloud agnostic - nice to have
- Easy to deploy and operate - admin user interface (UI), billing credits etc
- Rich query language
- Low latency, high throughput use case with <3 sec response time as the service level agreement (SLA)
- Current production workload - 80B rows (18TBs)
- Highly analytical queries with SQL interface

As part of the evaluation, they needed to consider their typical workload. Some workloads require the processing of small query volumes over vast amounts of data, and specialized products excel at that. At the other end of the spectrum, traditional database systems perform well for handling lots of queries over small amounts of data. However, Adevinta’s analytics workload was more analytical in nature, with dozens to hundreds of requests per second, and fell somewhere in between.

The team found that ClickHouse performed exceptionally well for their specific needs, as it was performant, cloud-agnostic, and more cost-effective than the other solutions. In comparison, BigQuery was 2x more expensive due to its pricing model that charges based on bytes scanned, and Cloud Spanner was 6x more expensive for the workload they tested. Adevinta chose ClickHouse Cloud as the winner, as it fit within their budget and offered the most value for their needs.

The solution was tested across multiple marketplaces with 22 queries per second, using a single table of 20 billion rows and 20 terabytes of data. They were confident ClickHouse was also future-proof as they anticipate raising query rates per second and volumes of data.

![Comparison - Cost excluded.png](https://clickhouse.com/uploads/Comparison_Cost_excluded_61be3e5bd5.png)

## Improving Analytics Performance and Scalability with ClickHouse Cloud

The main benefit of moving to ClickHouse Cloud for Adevinta was the elimination of the need for a self-managed environment. “One of the major requirements we had was to not have any dedicated site reliability support. You are not leveraging the potential of ClickHouse if you are not using not using ClickHouse Cloud”, remarked the Ad-Growth team.

The Ad-Growth team also mentioned how ClickHouse is well-suited for scaling analytics solutions to multiple marketplaces within Adevinta. “For instance, think of doing all the deep dive analytics, or AI and ML - you already have the data pre-prepared. ClickHouse helps us in terms of easy integration and onboarding more data into the database instance. It's extremely easy and super flexible. Marketplaces don't have to spend time figuring out a technology which can do this.”

Adevinta tested the system using approximately 5x their current workload. Their recommendations for others considering ClickHouse include matching the Order-By keys to the query access patterns and making sure both are tightly aligned. Additionally, they recommend running benchmarks on individual workloads to make data driven decisions based on real production data and query patterns. They also noted that ClickHouse is most effective when optimized and pre configured for known query access patterns.

According to Adevinta, working with the ClickHouse team has been a positive experience.
“Overall it has been a rewarding experience working with ClickHouse - from onboarding to execution. The Support teams have been excellent in helping with technology adoption in a complex setup,” said the Ad-Growth team.

Adevinta's journey to ClickHouse Cloud for real-time analytics has proven to be successful in meeting their needs for monitoring advertisements and tracking interactions in real-time. Overall, ClickHouse Cloud has provided Adevinta with a reliable, scalable and efficient real-time analytics solution for their online classifieds business.

Visit: [https://www.adevinta.com/](https://www.adevinta.com/)

## Further Reading
- [ClickHouse Benchmarks](https://clickhouse.com/blog/clickhouse-over-the-years-with-benchmarks)
