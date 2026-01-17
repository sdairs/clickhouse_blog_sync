---
title: "ClickHouse replaces Postgres to power real-time analytics in Common Room customer portal"
date: "2024-06-20T15:53:11.055Z"
author: "ClickHouse Team"
category: "User stories"
excerpt: "Founded in 2020, Common Room is an AI-powered customer intelligence platform that helps organizations run go-to-market (GTM) intelligently from end to end."
---

# ClickHouse replaces Postgres to power real-time analytics in Common Room customer portal

_Integrating ClickHouse has been a significant step in Common Room’s data management evolution, empowering it to handle the growing complexity and volume of customer data that comes alongside its marketplace success._

Founded in 2020, <a href="https://www.commonroom.io/" target="_blank">Common Room</a> is an AI-powered customer intelligence platform that helps organizations run go-to-market (GTM) intelligently from end to end. Digital signal capture, unified identity and account intelligence, and AI and automations come together in one platform to help GTM teams reach the right person with the right context at the right time. One of the founding software engineers, Kirill Sapchuk, [spoke at a recent ClickHouse meetup](/videos/commonroom-clickhouse) to give us the rundown on Common Room and some insights around its data management journey.

![common-room-img1.png](https://clickhouse.com/uploads/common_room_img1_7927389f93.png)

Common Room aggregates data from many different sources—including products, websites, CRMs, LinkedIn, X, Slack, GitHub, Reddit, YouTube, and many more—and connects cross-channel activity to real people and real accounts. This provides GTM teams with  a unified view of customers across the entire digital ecosystem: _“Before Common Room, people would build a spreadsheet and then manually extract data from sources like Twitter or Slack, then struggle to combine and parse it all. It was, at best, a cumbersome process,”_ said Kirill. He and the rest of the Common Room team wanted to transform how organizations connect with people. 

## Challenges with Postgres powering real-time analytical workloads

Initially, the focus was on pulling in data from different sources to create a unified view of the customer: _“Each individual is represented by what’s called a ‘member object’, which gathers all their information from all the relevant data sources plus other important data. Who are they? What segment? Previous companies? Etc.,”_ Kirill explained. Then the team made it possible to search through contacts and their organizations using a rich set of multi-faceted filters and set up rules for proactive notifications and workflows based on these criteria.

This interactive, data-driven experience required a powerful analytical database to execute these operations quickly and efficiently. The original architecture relied on Postgres as the sole datastore for both transactional and analytical datasets, but the Common Room team found that as the datasets grew, PostgreSQL was no longer the right fit for the analytical queries powering its user interface. The company began to look for alternatives.

![common-room-img2.png](https://clickhouse.com/uploads/common_room_img2_762bea1427.png)

## Enter ClickHouse Cloud

Attracted by the active ClickHouse community and a turnkey cloud version ready for testing, Common Room explored using ClickHouse for its use case. Namely, supporting 10-million-member records with 100 fields each. _“We had a billion rows to store,”_ said Kirill.

Traditional analytical databases are optimized for immutable, append-only data, but Common Room’s top priority was a solution that could handle frequent updates—25% of records updated daily. ClickHouse provides purpose-built table engines that handle data with updates without sacrificing the performance of analytical queries. Common Room adopted the `ReplacingMergeTree` table engine to handle updates and noted considerable performance improvements in 23.12 with the &lt;FINAL> modifier. The team also adopted the `VersionCollapsingMergeTree` table engine for more complex scenarios like handling deletions without which the high volume of changes would lead to a 25% increase in the table size daily. Using +1/-1 signs allowed for marking old rows for deletion and replacement. 

Common Room also implemented refreshable materialized views to provide fast, queryable versions of data for scenarios where some delay was acceptable. To use these views effectively, the team also had to optimize the order of JOIN operations. While Common Room still uses PostgreSQL for point queries and Kafka for batch data transformation, ClickHouse now handles the majority of live, customer-initiated queries—serving as a fast search engine.

![common-room-img3.png](https://clickhouse.com/uploads/common_room_img3_23f04368d0.png)

ClickHouse has proven to be an invaluable addition to Common Room’s tech stack, allowing them to efficiently process complex analytical queries on top of recent and historical data without compromising performance. [Watch the video](/videos/commonroom-clickhouse) to find out more!