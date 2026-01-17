---
title: "100x Faster: GraphQL Hive migration from Elasticsearch to ClickHouse"
date: "2022-11-03T14:14:03.992Z"
author: "The Guild"
category: "User stories"
excerpt: "Learn how migrating from Elasticsearch to ClickHouse enabled GraphQL Hive to scale from millions to billions of requests monthly and make everything 100x faster. \"ClickHouse helped us to scale from millions to billions of rows monthly without headaches.\""
---

# 100x Faster: GraphQL Hive migration from Elasticsearch to ClickHouse

_We’d like to welcome The Guild as a guest to our blog. Read on to find out why they are using ClickHouse and their journey from Elasticsearch to ClickHouse._

## What is GraphQL Hive?
GraphQL Hive is a Schema Registry, Monitoring, and Analytics solution for GraphQL APIs.

As a fully open-source tool, GraphQL Hive helps you to track the history of changes,prevents breaking the API and analyzes the traffic of your API.

GraphQL Hive makes you aware of how your GraphQL API is used and what is the experience of its final users.

## What is GraphQL?
For those unfamiliar with GraphQL, it’s a communication protocol between the front and back end. We recommend reading “[Introduction to GraphQL](https://graphql.org/learn/)” written by the GraphQL Foundation, where we, as The Guild, are members.

![GraphQL.png](https://clickhouse.com/uploads/Graph_QL_1eb711ebe4.png)

As you can see, only a small part of data was fetched, leaving project’s name and contributors untouched. This is what GraphQL Hive is about, studying and analyzing the usage of GraphQL API.

## A database for GraphQL API monitoring

Let’s start by explaining the kinds of data GraphQL Hive operates on.

We could group them into three buckets:
- Schema Registry
- Monitoring
- Analytics

This article will mainly focus on monitoring and analytics features which ended up being the most challenging part to scale.

GraphQL Hive tries to answer the following questions:
- Who are the consumers of GraphQL API?
- What part of GraphQL API is consumed and by whom?
- What is the performance of GraphQL API?

To answer those questions, GraphQL Hive analyses every HTTP request and collects:
- name and version of an API consumer
- a list of requested types and fields (like User, Comment, User.id, User.name)
- an overall latency
- a body of the request

GraphQL Hive stores the details of every HTTP request.

## Previously, in GraphQL Hive…
This kind of data is not meant to be mutated, requires a Time to Live mechanism and a set of functions for analytics and data aggregation.

We decided to use Elasticsearch because it checked all the boxes and was flexible enough to evolve the product over time.

## Problems with Elasticsearch
My biggest concern with Elasticsearch was the query language. Everyone at The Guild (the company behind GraphQL Hive) is familiar with SQL, so the JSON-based language meant a steep learning curve.

At some point during the preview program, we reached the first scaling issues.

The average response time was getting slower as we stored more and more data.

The other problem was related to indexing. One big user affected the query performance of other smaller users.

We tried to improve it by creating an index per user, but because the overall speed of Elasticsearch was way below what we expected, we started looking for an alternative.

## Alternatives to Elasticsearch
When looking for an alternative, these were the requirements:
- Easy to learn and maintain
- Superb performance
- Good for analytics and aggregation of data
- Built-in TTL
- Type System
- No issue with high cardinality

We must say, there are more databases than people and even more benchmarks with different conclusions.

After researching, We decided to test **InfluxDB**, **TimescaleDB**, **Druid**, and **ClickHouse**.

We created a dataset of 20M rows in which one user owned half of them. To measure the performance, we tried to calculate a few high percentiles and see if one big user affects the query performance of the other, smaller users.

## The baseline was 10s with Elasticsearch.

We had big expectations for **InfluxDB**, it seemed like an extremely fast time-series database. Unfortunately, like many time-series databases, it struggles with the [high-cardinality data](https://clickhouse.com/resources/engineering/high-cardinality-slow-observability-challenge) common in modern observability platforms.. Every collected HTTP request in GraphQL Hive could be labeled with an infinite number of values across all users.

It was also really hard for us to get started.

**The query time was ~5s.**

Next was **TimescaleDB**. We liked the fact that it speaks SQL and supports relations between tables. The overall performance was much better than what we experienced with Elasticsearch.

**The response time was close to 3 seconds.**

At the time of our research (April 2021), **ClickHouse** felt very mysterious to us. We haven’t heard much about it, and we found only a few case studies. It seemed very similar to TimescaleDB but offered a much wider set of functions for data analytics, and the collection of table engines was perfect for our use case.

**The query time was… ~100ms.**

We haven’t tested Druid, it felt too complex. Even though it may be capable of handling an enormous amount of data, we wanted to find something simple yet powerful, and ClickHouse seemed like a perfect fit.

![average_read_time.png](https://clickhouse.com/uploads/average_read_time_1e59bdec8f.png)

## Migrating from Elasticsearch
The migration from Elasticsearch to ClickHouse was done gradually and wasn’t complex.

During the preview program, the Time to Live for collected data was only 30 days.

That’s why we decided to write data to both destinations at once, for a full month. This allowed us to seamlessly shift the read operations to ClickHouse, with zero downtime.

## GraphQL Hive and ClickHouse
After the switch, we saw a 100x improvement on average compared to the previous data pipeline.

>ClickHouse helped us to scale from millions to billions of rows monthly without headaches.

If you’re curious about our database structure and how we use ClickHouse, we recommend you to check out the source code [on GitHub](https://github.com/kamilkisiela/graphql-hive/blob/64e53f207b413f8bb222eabd6aeb437e3300dbfd/packages/services/storage/migrations/clickhouse.ts#L4-L189).

We also wrote a much more [in-depth article](https://the-guild.dev/blog/graphql-hive-and-clickhouse) explaining our ClickHouse setup and how we are able to process billions or GraphQL requests monthly.

## Taking it to the next level with ClickHouse Cloud
Our current data pipeline uses a single instance of ClickHouse. It works really well, and so far, we haven’t experienced any hiccups, but the need to scale it to more nodes will eventually arrive.

That’s why we started moving into **ClickHouse Cloud**.

Thanks to its out-of-the-box support for sharding and replication, we can focus on developing new features and let the ClickHouse Cloud take care of the rest.
