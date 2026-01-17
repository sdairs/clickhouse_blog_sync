---
title: "July 2024 Newsletter"
date: "2024-07-16T14:07:44.603Z"
author: "ClickHouse Team"
category: "Community"
excerpt: "Welcome to the July ClickHouse newsletter, which will round up what’s happened in real-time data warehouses over the last month."
---

# July 2024 Newsletter

Welcome to the July ClickHouse newsletter, which will round up what’s happened in real-time data warehouses over the last month.

This month, we have optimal table sorting in the 24.6 release, tracking vessels with ClickHouse &amp; Grafana, and tactics for optimizing CPU usage when running ClickHouse.

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## Inside this issue

- [Featured community member](/blog/202407-newsletter#featured-community-member)
- [Upcoming events](/blog/202407-newsletter#upcoming-events)
- [24.6 release](/blog/202407-newsletter#246-release)
- [How to track vessels with Python, ClickHouse, and Grafana](/blog/202407-newsletter#how-to-track-vessels-with-python-clickhouse-and-grafana)
- [ClickHouse MergeTree Engine](/blog/202407-newsletter#clickhouse-mergetree-engine)
- [Optimizing ClickHouse: The Tactics that worked for highlight.io](/blog/202407-newsletter#optimizing-clickhouse-tactics-that-worked-for-highlightio)
- [ClickHouse Cloud updates: July 2024](/blog/202407-newsletter#clickhouse-cloud-updates-july-2024)
- [Video corner: Import patterns](/blog/202407-newsletter#video-corner-import-patterns)
- [Post of the month](/blog/202407-newsletter#post-of-the-month)

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## Featured community member

This month's featured community member is taiyang-li (李扬)

![202407-featuredmember.png](https://clickhouse.com/uploads/202407_featuredmember_dad0aa43b0.png)

taiyang-li is a frequent contributor to the ClickHouse database, regularly <a href="https://github.com/ClickHouse/ClickHouse/pulls?q=is:pr+author:taiyang-li+">contributing pull requests</a> that improve ClickHouse’s performance and string processing capabilities.
In just the last few months, he’s committed code that let the -<span style="font-family: 'courier new', courier; color: #41D76B">UTF8</span> functions handle strings containing only ASCII characters, fixed <span style="font-family: 'courier new', courier; color: #41D76B">concat</span> to accept empty arguments, and improved the compatibility of the <span style="font-family: 'courier new', courier; color: #41D76B">upper/lowerUTF8</span> functions.
And if you’ve noticed that the <span style="font-family: 'courier new', courier; color: #41D76B">splitByRegexp</span>, <span style="font-family: 'courier new', courier; color: #41D76B">coalesce</span>, or <span style="font-family: 'courier new', courier; color: #41D76B">ifNotNull</span> functions are quicker, you can also thank taiyang-li for that!

<a href="https://github.com/taiyang-li">Follow Taiyang-Li on GitHub</a>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## Upcoming events

- <a href="/company/events/clickhouse-fundamentals?utm_source=clickhouse&utm_medium=web&utm_campaign=202407-newsletter" target="_blank" id="">ClickHouse Fundamentals</a> - July 24th &amp; 25th
- <a href="/company/events/v24-7-community-release-call?utm_source=clickhouse&utm_medium=web&utm_campaign=202407-newsletter" target="_blank" id="">ClickHouse Community Call</a> - July 30th
- <a href="/company/events/202407-amer-postgres-to-clickhouse-migration?utm_source=clickhouse&utm_medium=web&utm_campaign=202407-newsletter" target="_blank" id="">Migrating from Postgres to ClickHouse Workshop</a> - July 31st
- <a href="/company/events/202408-clickhouse-bigquery-workshop?utm_source=clickhouse&utm_medium=web&utm_campaign=202407-newsletter" target="_blank" id="">BigQuery to ClickHouse Workshop</a> - August 7th
- <a href="/company/events/clickhouse-fundamentals?utm_source=clickhouse&utm_medium=web&utm_campaign=202407-newsletter" target="_blank" id="">ClickHouse Fundamentals</a> - August 13th & 14th
- <a href="/company/events/202408-clickhouse-admin-workshop?utm_source=clickhouse&utm_medium=web&utm_campaign=202407-newsletter" target="_blank" id="">ClickHouse Admin Workshop</a> - August 21st

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## 24.6 release

![24_06_cd46491ba9.png](https://clickhouse.com/uploads/24_06_cd46491ba9_13a3408f28.png)

The latest release of ClickHouse saw the introduction of optimal table sorting. We can use this setting on table creation, and when ingesting data, after sorting by <span style="font-family: 'courier new', courier; color: #41D76B">ORDER BY</span> key, ClickHouse will automatically sort data to achieve the best compression. We also had a beta release of chDB that lets you query Pandas DataFrames directly, and functions for Hilbert Curves were added.

<a href="/blog/clickhouse-release-24-06?utm_source=clickhouse&utm_medium=web&utm_campaign=202407-newsletter">Read the release post</a>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## How to track vessels with Python, ClickHouse, and Grafana

![vessel.jpg](https://clickhouse.com/uploads/vessel_0b068d3284.jpg)

Ignacio Van Droogenbroeck has written a cool blog post on tracking vessels in San Francisco and Buenos Aires. He shows how to get the data from AisStream’s WebSockets API into ClickHouse and then creates a series of visualizations using Grafana.

<a href="https://cduser.com/tracking-vessels-using-python-clickhouse-grafana?utm_source=clickhouse&utm_medium=web&utm_campaign=202407-newsletter">Read the blog post</a>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## ClickHouse MergeTree Engine

![mergetree.png](https://clickhouse.com/uploads/mergetree_67dfbe2252.png)

Tôi là Duyệt has started writing blog posts about using ClickHouse in Kubernetes. A recent post explores the default MergeTree table engine. Tôi explains what happens when data is ingested into a table using this engine. He then goes through how to use it, including inserting data, supported data types, and column modifiers.

<a href="https://blog.duyet.net/2024/05/clickhouse-mergetree.html?utm_source=clickhouse&utm_medium=web&utm_campaign=202407-newsletter">Read the blog post</a>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## Optimizing ClickHouse: Tactics that worked for highlight.io

![cpu-wait.png](https://clickhouse.com/uploads/cpu_wait_75875ad6b1.png)

highlight.io is an open-source, full-stack Monitoring Platform. It ingests 100 TB of observability per month, much of which goes into ClickHouse. CTO Vadim Korolik has written a blog post sharing their lessons on optimizing ClickHouse to reduce CPU load.&nbsp;

<a href="https://www.highlight.io/blog/lw5-clickhouse-performance-optimization?utm_source=clickhouse&utm_medium=web&utm_campaign=202407-newsletter">Read the blog post</a>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## ClickHouse Cloud updates: July 2024

![cloud-highlights.png](https://clickhouse.com/uploads/cloud_highlights_6d571c03a7.png)

Did you know that we publish a ClickHouse Cloud Changelog every fortnight? In the latest version, we announced the availability of ClickHouse Cloud on Microsoft Azure and a new Query Logs Insights UI to make it easier to debug your queries. The Prometheus endpoints for metrics is also in Private Preview.

<a href="/docs/en/whats-new/cloud?utm_source=clickhouse&utm_medium=web&utm_campaign=202407-newsletter" target="_blank">View the changelog</a>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## Video corner: Import patterns

Mark Needham has recorded several videos demonstrating import patterns with ClickHouse:

- <a href="/videos/derive-columns-other-columns?utm_source=clickhouse&utm_medium=web&utm_campaign=202407-newsletter">Deriving columns from other columns</a> shows how to use the DEFAULT, ALIAS, and MATERIALIZED column modifiers
- Next, we learn about the <a href="/videos/ephemeral-column-modifier?utm_source=clickhouse&utm_medium=web&utm_campaign=202407-newsletter">EPHEMERAL column modifier</a>, which is used when we don’t want to store a column but rather have that column referenced by the other column modifiers.
- Finally, we use the <a href="/videos/null-table-engine?utm_source=clickhouse&utm_medium=web&utm_campaign=202407-newsletter">Null Table Engine</a> to route incoming data to different destination tables based on filtering criteria.

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## Post of the month

Our favorite post this month was by <a href="https://x.com/byAnhtho/status/1807761150001688797" target="_blank">anhtho</a>, who’s using ClickHouse to analyze billing data.

<a href="https://x.com/byAnhtho/status/1807761150001688797" target="_blank">Read the post</a>

![tweet-1807761150001688797-july224.png](https://clickhouse.com/uploads/tweet_1807761150001688797_july224_a22d88887a.png)

