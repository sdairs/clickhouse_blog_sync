---
title: "February 2024 Newsletter"
date: "2024-02-28T09:53:17.918Z"
author: "ClickHouse Team"
category: "Community"
excerpt: "Welcome to the February ClickHouse newsletter where we round up what’s been happening in the world of real-time data warehouses in the last month.  This month, we have a deep dive into ClickHouse’s internals, the Grafana v4.0 plugin, and the 24.1 release."
---

# February 2024 Newsletter

Welcome to the February ClickHouse newsletter where we round up what’s been happening in the world of real-time data warehouses in the last month.

This month, we have a deep dive into ClickHouse’s internals, the Grafana v4.0 plugin, and the 24.1 release with the experimental Variant type.

## Inside this issue

<ul>
<li><a href="/blog/newsletter-february-2024#featured-community-member">Featured community member</a></li>
<li><a href="/blog/newsletter-february-2024?utm_source=clickhouse&amp;utm_medium=email&amp;utm_campaign=202402-newsletter#clickhouse-grafana-plugin-40---leveling-up-sql-observability">ClickHouse Grafana plugin 4.0 - Leveling up SQL Observability</a></li>
<li><a href="/blog/newsletter-february-2024?utm_source=clickhouse&amp;utm_medium=email&amp;utm_campaign=202402-newsletter#clickhouse-cloud-live-february-2024">ClickHouse Cloud Live: February 2024</a></li>
<li><a href="/blog/newsletter-february-2024?utm_source=clickhouse&amp;utm_medium=email&amp;utm_campaign=202402-newsletter#241-release">24.1 release</a></li>
<li><a href="/blog/newsletter-february-2024?utm_source=clickhouse&amp;utm_medium=email&amp;utm_campaign=202402-newsletter#understanding-the-clickhouse-architecture">Understanding ClickHouse&rsquo;s Architecture</a></li>
<li><a href="/blog/newsletter-february-2024?utm_source=clickhouse&amp;utm_medium=email&amp;utm_campaign=202402-newsletter#post-of-the-month">Post&nbsp;of the month</a><br /></li>
<li><a href="/blog/newsletter-february-2024?utm_source=clickhouse&amp;utm_medium=email&amp;utm_campaign=202402-newsletter#upcoming-events">Upcoming events</a></li>
</ul>

## Featured community member

Our featured community member this month is <a href="https://www.linkedin.com/in/benjaminwootton?utm_source=clickhouse&utm_medium=web&utm_campaign=202402-newsletter" target="_blank" >Benjamin Wooton</a>, founder &amp; CTO of Ensemble, a company that helps businesses deploy real-time data, analytics, and AI platforms <a href="https://ensembleanalytics.io/why-clickhouse-cloud?utm_source=clickhouse&utm_medium=web&utm_campaign=202402-newsletter" target="_blank" >based on ClickHouse</a>.

![ben.png](https://clickhouse.com/uploads/ben_12da3f4537.png)

Benjamin is a passionate advocate of ClickHouse and you&rsquo;ll often see him engaging in discussions about real-time data warehouses and similar topics on LinkedIn and Twitter.

He&rsquo;s also written several blog posts over the last few weeks, covering various use cases. In the most recent one, Benjamin comes up with the optimal way of allocating consultants to projects based on their skills using Google&rsquo;s OR-Tools library mixed in with some ClickHouse queries. He also uses a similar toolkit to come up with <a href="https://ensembleanalytics.io/blog/clickhouse-vehicle-route-planning?utm_source=clickhouse&utm_medium=web&utm_campaign=202402-newsletter" target="_blank" >a solution to a traveling salesman type problem</a>.

And if that&rsquo;s not enough, Benjamin also presented Building Real-Time Analytics Systems with ClickHouse at the <a href="https://www.meetup.com/clickhouse-london-user-group/events/298891993/" target="_blank" >ClickHouse London meetup</a> this week.

<a href="https://www.linkedin.com/in/benjaminwootton/" target="_blank" >Follow Benjamin on LinkedIn</a>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## ClickHouse Grafana plugin 4.0 - leveling up SQL observability

![grafana2x.png](https://clickhouse.com/uploads/grafana2x_03066c6102.png)

We released the Grafana 4.0 plugin. With first-class support for logs and traces, it&rsquo;s now easier than ever to make sense of log data stored in ClickHouse.

<a href="https://clickhouse.com/blog/clickhouse-grafana-plugin-4-0?utm_source=clickhouse&utm_medium=web&utm_campaign=202402-newsletter" target="_blank" >Read the release post</a>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## ClickHouse Cloud Live: February 2024

![Cloudupdate.png](https://clickhouse.com/uploads/Cloudupdate_357d49888f.png)

The ClickHouse Cloud update call brought together a bunch of folks to talk about recent releases and the roadmap going forward. A unified console, new authentication options, and more.

<a href="https://clickhouse.com/videos/clickhouse-cloud-update-call-feb2024?utm_source=clickhouse&utm_medium=web&utm_campaign=202402-newsletter" target="_blank" >Watch the video</a>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## 24.1 Release

The 24.1 release introduces the Variant type, which is the first step on the way to semi structured column support in ClickHouse. We also have more string similarity functions, as well as performance improvements when using the FINAL keyword with the ReplacingMergeTree

<a href="https://clickhouse.com/blog/clickhouse-release-24-01?utm_source=clickhouse&utm_medium=web&utm_campaign=202402-newsletter" target="_blank">Read the release post</a>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## Understanding the ClickHouse architecture

<img src="https://discover.clickhouse.com/rs/238-FPC-317/images/CH architecture.png?version=0" alt="Understanding the ClickHouse architecture" width="100%" style="display: block;" /> 

Jack Vanlightly, Staff Technologist at Confluent, does a deep dive into the ClickHouse architecture, starting out with the way data is ingested. He explains the writing of parts, how they&rsquo;re merged, as well as data organization and indexes. He also covers the various table engines, compression techniques, data partitioning, and more.

<a href="https://jack-vanlightly.com/analyses/2024/1/23/serverless-clickhouse-cloud-asds-chapter-5-part-1?utm_source=clickhouse&utm_medium=web&utm_campaign=202402-newsletter" target="_blank" >Read the blog post</a>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## Post of the month

![Tweet.png](https://clickhouse.com/uploads/Tweet_14d584c769.png)

<a href="https://twitter.com/baptistejamin/status/1755599333452550224" target="_blank" >See the thread</a>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## Upcoming events

<ul>
<li><a href="https://clickhouse.com/company/events/v24-2-community-release-call?utm_source=clickhouse&utm_medium=web&utm_campaign=202402-newsletter" target="_blank" >v24.2 Community Call</a>&nbsp;- February 29th</li>
<li><a href="https://clickhouse.com/company/events/clickhouse-fundamentals?utm_source=clickhouse&utm_medium=web&utm_campaign=202402-newsletter" target="_blank" >FREE ClickHouse Training</a>&nbsp;- Various dates in March</li>
<li><a href="https://www.meetup.com/clickhouse-silicon-valley-meetup-group/events/299058486/" target="_blank" >San Francisco Meetup</a> - March 4th</li>
<li><a href="https://www.meetup.com/clickhouse-seattle-user-group/events/298650371/" target="_blank" >Seattle Meetup</a> - March 11th<br /></li>
<li><a href="https://www.meetup.com/clickhouse-new-york-user-group/events/298640542/" target="_blank" >New York Meetup</a> - March 19th</li><li><a href="https://www.meetup.com/clickhouse-australia-user-group/events/299479750/" target="_blank" >Melbourne Meetup</a> - March 20th</li>
<li><a href="https://www.meetup.com/clickhouse-france-user-group/events/298997115/" target="_blank" >Paris Meetup</a> - March 21st</li>
<li><a href="https://www.meetup.com/clickhouse-bangalore-user-group/events/299479850/" target="_blank" >Bangalore Meetup</a> - March 23rd</li>
</ul>