---
title: "June 2024 Newsletter"
date: "2024-06-19T13:28:06.005Z"
author: "ClickHouse Team"
category: "Community"
excerpt: "Welcome to the June ClickHouse newsletter, which will round up what’s happened in real-time data warehouses over the last month."
---

# June 2024 Newsletter

Welcome to the June ClickHouse newsletter, which will round up what’s happened in real-time data warehouses over the last month.

This month, we have the dynamic data type in the 24.5 release, why HyperDX chose ClickHouse over Elasticsearch for observability data, and how to use ClickHouse to count unique users at scale.

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## In this issue

- [Featured Community Member](/blog/202406-newsletter#featured-community-member-michael-driscoll)
- [Upcoming events](/blog/202406-newsletter#upcoming-events)
- [24.5 release](/blog/202406-newsletter#245-release)
- [Why HyperDX Chose Clickhouse Over Elasticsearch for Storing Observability Data](https://clickhouse.com/blog/202406-newsletter#why-hyperdx-chose-clickhouse-over-elasticsearch-for-storing-observability-data)
- [Python User-Defined Functions in ClickHouse](/blog/202406-newsletter#python-user-defined-functions-in-clickhouse)
- [Tweeq Data Platform: Journey and Lessons Learned: Clickhouse, dbt, Dagster, and Superset](/blog/202406-newsletter#tweeq-data-platform-journey-and-lessons-learned-clickhouse-dbt-dagster-and-superset)
- [Using ClickHouse to count unique users at scale](/blog/202406-newsletter#using-clickhouse-to-count-unique-users-at-scale)
- [ClickHouse as part of the ETL/ELT process](/blog/202406-newsletter#clickhouse-as-part-of-the-etlelt-process)
- [Post of the month](/blog/202406-newsletter#post-of-the-month)


<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## Featured Community Member: Michael Driscoll

This month's featured community member is Michael Driscoll, Co-Founder and CEO at Rill Data.

![june-communitymember.png](https://clickhouse.com/uploads/june_communitymember_a3c139a247.png)

Michael has worked in the tech industry for two decades as a technologist, entrepreneur, and investor. Over the years, he has founded several companies, including Metamarkets, a real-time analytics platform for digital ad firms, which Snap, Inc. acquired in 2017. 

His latest company is Rill, a cloud service for operational intelligence. The Rill and ClickHouse worlds collided when Michael met Alexey, ClickHouse’s Co-Founder and CTO, at FOSDEM earlier this year.

Alexey suggested running Rill on top of a ClickHouse-powered data set of Wikipedia traffic. Michael and his team [got this working in a couple of days](https://www.rilldata.com/blog/operational-bi-embedded-dashboards-for-clickhouse), and Michael joined the [24.2 Community Call](https://clickhouse.com/blog/clickhouse-release-24-02) to share Rill’s connector for ClickHouse. Michael also [presented at the ClickHouse San Francisco meetup](https://clickhouse.com/videos/how-rill-powers-fast-exploratory-bi-with-clickhouse) two weeks ago.

[Follow Michael on LinkedIn](https://www.linkedin.com/in/medriscoll/)

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## Upcoming events

<ul> 
    <li><a href="https://clickhouse.com/company/events/clickhouse-fundamentals?utm_source=clickhouse&amp;utm_medium=web&amp;utm_campaign=202406-newsletter" target="_blank">ClickHouse Fundamentals</a> - June 26th &amp; 27th<br></li> 
    <li><a href="https://clickhouse.com/company/events/2024-06-aws-summit-dc?utm_source=clickhouse&amp;utm_medium=web&amp;utm_campaign=202406-newsletter" target="_blank">AWS Summit D.C.</a> - June 26th</li> 
    <li><a href="https://www.meetup.com/clickhouse-netherlands-user-group/events/300781068/" target="_blank" id="">Amsterdam Meetup</a> - June 27th</li> 
    <li><a href="https://clickhouse.com/company/events/v24-6-community-release-call?utm_source=clickhouse&amp;utm_medium=web&amp;utm_campaign=202406-newsletter" target="_blank" id="">ClickHouse 24.6 release call</a> - June 27th</li> 
    <li><a href="https://www.meetup.com/clickhouse-belgium-user-group/events/301220649/" target="_blank">Belgium Meetup</a> - July 4th</li>
    <li><a href="https://clickhouse.com/company/events/202407-cloud-update-live?utm_source=clickhouse&amp;utm_medium=web&amp;utm_campaign=202406-newsletter" target="_blank" id="">ClickHouse Cloud live update</a> - July 9th</li> 
    <li><a href="https://www.meetup.com/clickhouse-france-user-group/events/300783448/" target="_blank" id="">Paris Meetup</a> - July 9th</li> 
    <li><a href="https://www.meetup.com/clickhouse-new-york-user-group/events/300595845/" target="_blank" id="">New York Meetup</a> - July 9th</li> 
    <li><a href="https://docs.google.com/forms/d/e/1FAIpQLSdgfj0RqgUhyWuKWZoFJovMMGRdfm9mEpp4xWFK6nNcJSAklw/viewform" target="_blank" id="">AWS Summit New York Happy Hour</a> - July 10th</li> 
    <li><a href="https://www.meetup.com/clickhouse-boston-user-group/events/300907870/" target="_blank" id="">Boston Meetup</a> - July 11th</li> 
    <li><a href="https://www.meetup.com/clickhouse-singapore-meetup-group/events/301574841/" target="_blank" id="">Singapore Meetup</a> - July 11th</li> 
    </ul>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## 24.5 release

![release-245.png](https://clickhouse.com/uploads/release_245_f1959d6e45.png)

The journey to add a semi-structured data type to ClickHouse continues with the introduction of the Dynamic type. This release also saw performance improvements for CROSS JOINs and functionality to read into archive files on S3.

[Read the release post](https://clickhouse.com/blog/clickhouse-release-24-05)

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## Why HyperDX Chose Clickhouse Over Elasticsearch for Storing Observability Data

Michael Shi works on HyperDX, an open-source observability platform built on OpenTelemetry and Clickhouse. In this blog post, he explains why they use ClickHouse rather than Elasticsearch, pointing out that observability has become more of an analytics problem than a search problem. He identifies ClickHouse’s columnar data layout and sparse indexes as key differentiators. 

[Read the blog post](https://www.hyperdx.io/blog/why-clickhouse-over-elasticsearch-observability)

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## Python User-Defined Functions in ClickHouse

Tom Weisner has written a tutorial on using Python User-Defined functions in ClickHouse. He starts with a simple function that reverses a string before moving onto a multi-argument function that adds minutes or hours to a provided DateTime. He concludes with a function that detects elevated heart rate activity in time-series data with help from numpy and scipy.

[Read the blog post](https://towardsdev.com/user-defined-functions-in-clickhouse-with-python-c3f7724bd6de)

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## Tweeq Data Platform: Journey and Lessons Learned: Clickhouse, dbt, Dagster, and Superset

Tweeq is a fintech startup building a highly scalable and flexible payments platform from scratch. ClickHouse is the data warehouse, and Tweeq uses the Kafka table engine to ingest data. In this blog post, Atheer Alabdullatif explains how they chose ClickHouse and the other tools that form part of the data platform. 

[Read the blog post](https://engineering.tweeq.sa/tweeq-data-platform-journey-and-lessons-learned-clickhouse-dbt-dagster-and-superset-fa27a4a61904)

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## Using ClickHouse to count unique users at scale

![diagram-june2024-nl.png](https://clickhouse.com/uploads/diagram_june2024_nl_204fe63de8.png)

Twilio Engage is an Omnichannel Customer Engagement Tool that lets users define customers’ journeys. They wanted to show their users the overall stats per journey and provide more accurate step-level stats. This worked well for all users except those storing vast amounts of data. In the blog post, they explain how they solved this problem using semantic sharding and the `distributed_group_by_no_merge` setting, as well as reducing the size of grouping keys in the database.

[Read the blog post](https://segment.com/blog/using-clickhouse-to-count-unique-users-at-scale/)

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## ClickHouse as part of the ETL/ELT process

Nikolai Potapov discusses the different ways in which ClickHouse can transform data in a data pipeline. We learn about parameterized views, materialized views, and various table engines.

[Read the blog post](https://blog.devgenius.io/clickhouse-as-part-of-etl-elt-process-7ef1edf2ae7c)

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## Post of the month

Our favorite post this month was by [Pascal Senn](https://x.com/Pascal_Senn), who’s having a great time working with ClickHouse.

![tweet_1799506036828610991_20240619_135817_via_10015_io.png](https://clickhouse.com/uploads/tweet_1799506036828610991_20240619_135817_via_10015_io_f00c8b12eb.png)

<a href="https://x.com/Pascal_Senn/status/1799506036828610991" target="_blank">Read the post</a>