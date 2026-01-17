---
title: "December 2024 newsletter"
date: "2024-12-18T17:36:14.990Z"
author: "ClickHouse Team"
category: "Community"
excerpt: "Welcome to the December ClickHouse newsletter, which will round up what’s happened in real-time data warehouses over the last month."
---

# December 2024 newsletter

Welcome to the December ClickHouse newsletter, our last one for 2024! This month we’ve got a guide to query optimization, a real-world example of SQL-based observability, product announcements around Amazon’s re-Invent conference, the Postgres CDC connector for ClickPipes moving into Private Preview, and more.

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>


## Inside this issue

<ul> 
<li><a href="https://clickhouse.com/blog/202412-newsletter#upcoming-events">Upcoming events</a></li>
<li><a href="https://clickhouse.com/blog/202412-newsletter#featured-community-member">Featured community member</a></li>
<li><a href="https://clickhouse.com/blog/202412-newsletter#2411-release">24.11 Release</a></li>
<li><a href="https://clickhouse.com/blog/202412-newsletter#a-simple-guide-to-clickhouse-query-optimization-part-1">A simple guide to ClickHouse query optimization: part 1</a></li>
<li><a href="https://clickhouse.com/blog/202412-newsletter#building-sql-based-observability-with-clickhouse-and-grafana">Building SQL-based Observability With ClickHouse and Grafana</a></li>
<li><a href="https://clickhouse.com/blog/202412-newsletter#postgres-cdc-connector-for-clickpipes-is-now-in-private-preview">
Postgres CDC connector for ClickPipes is now in Private Preview</a></li>
<li><a href="https://clickhouse.com/blog/202412-newsletter#clickhouse-decoded-making-sense-of-fast-data">ClickHouse Decoded: Making Sense of Fast Data</a></li>
<li><a href="https://clickhouse.com/blog/202412-newsletter#clickhouse-at-aws-reinvent-2024">
ClickHouse at AWS re:Invent 2024</a></li>
<li><a href="https://clickhouse.com/blog/202412-newsletter#video-corner">Video corner</a></li>
<li><a href="https://clickhouse.com/blog/202412-newsletter#quick-reads">Quick reads</a></li>
<li><a href="https://clickhouse.com/blog/202412-newsletter#clickhouse-user-conference">ClickHouse User Conference</a></li>
<li><a href="https://clickhouse.com/blog/202412-newsletter#post-of-the-month">Post of the month</a></li>
</ul>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## Upcoming events
 
<p><strong>Global events</strong></p> 
<ul> 
<li><a href="https://clickhouse.com/company/events/v24-12-community-release-call?utm_source=clickhouse&utm_medium=email&utm_campaign=202412-newsletter" target="_blank" id="">Release call 24.12</a> - Dec 19<br></li> 
<li><a href="https://clickhouse.com/company/events/v25-1-community-release-call?utm_source=clickhouse&utm_medium=email&utm_campaign=202412-newsletter" target="_blank" id="">Release call 25.1</a> - Jan 30<br></li> 

</ul> 
<p><strong>Free training</strong></p> 
<ul> 
<li><a href="https://clickhouse.com/company/events/clickhouse-fundamentals?utm_source=clickhouse&utm_medium=email&utm_campaign=202412-newsletter" target="_blank" id="">ClickHouse Fundamentals</a> - Virtual - Jan 8 and Jan 15<br></li> 
<li><a href="https://clickhouse.com/company/events/202501-emea-query-optimization?utm_source=clickhouse&utm_medium=email&utm_campaign=202412-newsletter" target="_blank" id="">ClickHouse Query Optimization Workshop</a> - Virtual - Jan 22</li> 
<li><a href="https://clickhouse.com/company/events/202501-amer-clickhouse-observability?utm_source=clickhouse&utm_medium=email&utm_campaign=202412-newsletter" target="_blank" id="">Using ClickHouse for Observability</a> - Virtual - Jan 29</li> 
</ul> 

<p><strong>Events in EMEA</strong></p> 
<ul> 
<li><a href="https://www.meetup.com/clickhouse-london-user-group/events/305146729/" target="_blank" id="">Meetup in London</a> - Feb 5<br></li> 
<li><a href="https://www.meetup.com/clickhouse-dubai-meetup-group/events/303096989/" target="_blank" id="">Meetup in Dubai</a> - Feb 10<br></li> 
</ul>

<p><strong>Events in APAC</strong></p> 
<ul> 
<li><a href="https://www.alibabacloud.com/en/events/alibabacloud-developer-summit-2025?_p_lc=1" target="_blank" id="">Alibaba Developer Summit Jakarta</a> - Jan 21<br></li> 
<li><a href="https://www.meetup.com/clickhouse-tokyo-user-group/events/305126993/" target="_blank" id="">Meetup in Tokyo</a> - Jan 23<br></li> 
</ul>

<br>

## Featured community member

This month's featured community member is Azat Khuzhin, Lead Engineer at Semrush.

![featured-202412.png](https://clickhouse.com/uploads/featured_202412_d0a6498ade.png)
<p>
Azat has been working at Semrush for over 13 years. His expertise lies in working with ClickHouse and other database management systems, handling large-scale distributed systems, and data processing. 
</p>
<p>He regularly contributes to ClickHouse, submitting over 60 pull requests this year, focused on performance optimization, system stability, and feature enhancements across various components. His work spans from improving distributed query processing and replication to enhancing security, configuration management, and user experience. 
</p>

<p><a href="https://www.linkedin.com/in/iamazat?utm_source=clickhouse&amp;utm_medium=email&amp;utm_campaign=202412-newsletter" target="_blank">Follow Azat on LinkedIn</a></p>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## 24.11 release

![release-24.11.png](https://clickhouse.com/uploads/release_24_11_7412f9e511.png)

<p>The standout feature in the 24.11 release was parallel hash join becoming the default join strategy. Other features include the ability to pre-warm the marks cache, the BFloat16 data type for vector search, and the <span style="font-family: terminal, monaco; color: #41d76b;">STALENESS</span> modifier for <span style="font-family: terminal, monaco; color: #41d76b;">WITH FILL</span>.</p>

<p>In the <a href="https://clickhouse.com/videos/202411-release-call">24.11 community call</a>, we also had a fun demo of <a href="https://www.hyperdx.io/">HyperDX</a>, an open-source observability platform that uses ClickHouse.</p>

<p><a href="https://clickhouse.com/blog/clickhouse-release-24-11">Read the release post</a></p>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## A simple guide to ClickHouse query optimization: part 1

![query-optimization.png](https://clickhouse.com/uploads/query_optimization_b787976d7b.png)

<p>Lionel Palacin recently joined the ClickHouse Product Marketing Engineering team and, while working on the <a href="https://sql.clickhouse.com/" target="_blank">new ClickHouse Playground</a>, became curious about how to improve the performance of sample queries used in the playground.
</p>
<p>In the first of a two-part blog series, he shares some things he’s learned. In the blog post, Lio explains what happens when a query runs, how to identify slow queries, and how to understand what happens during query execution using the EXPLAIN clause. He then shows how to apply various optimizations and see if they work.
</p>
<p><a href="https://clickhouse.com/blog/a-simple-guide-to-clickhouse-query-optimization-part-1" target="_blank">Read the blog post</a></p>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>


## Building SQL-based Observability With ClickHouse and Grafana

![observability-grafana.png](https://clickhouse.com/uploads/observability_grafana_f791b8b1f7.png)

<p><a href="https://www.linkedin.com/in/crt0r/">Timofey Chuchkanov</a>, DevOps Engineer at EVALAR JSC has written a blog post detailing his experience building an observability stack based on ClickHouse and Grafana.</p>

<p>After reviewing the criteria for the ideal stack, which included querying using SQL, the ability to query logs and metrics, and integrations with other software, Timofey went through the candidate stacks. These included Elasticserach, Loki, Timescale, and more, but they settled on ClickHouse.
</p>

<p>I enjoyed reading this one, and seeing more examples in the wild of <a href="https://clickhouse.com/blog/evolution-of-sql-based-observability-with-clickhouse">SQL-based observability</a> is cool.

</p>
<p><a href="https://cmtops.dev/posts/building-observability-with-clickhouse/">Read the blog post</a></p>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## Postgres CDC connector for ClickPipes is now in Private Preview

![postgres-connector.png](https://clickhouse.com/uploads/postgres_connector_3b1f2f93e3.png)

<p>We recently announced the private preview of the Postgres Change Data Capture (CDC) connector in ClickPipes.
</p>
<p>This enables customers to replicate their Postgres databases to ClickHouse Cloud in just a few clicks and leverage ClickHouse for blazing-fast analytics. You can use this connector for continuous replication and one-time migrations use cases from Postgres.
</p>
<p><a href="https://clickhouse.com/blog/postgres-cdc-connector-clickpipes-private-preview">Read the blog post</a></p>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## ClickHouse Decoded: Making Sense of Fast Data

![fast-data.png](https://clickhouse.com/uploads/fast_data_12c5108f28.png)

<p>Shubham Bhardwaj takes a detailed look into the way that ClickHouse works. He starts by exploring the way data is laid out on disk and describes each component. Next, we move onto materialized views, table engines, and, finally, how to scale ClickHouse.
</p>

<p><a href="https://towardsdev.com/clickhouse-decoded-making-sense-of-fast-data-41c5a020734d">Read the blog post</a></p>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## ClickHouse at AWS re:Invent 2024

![product-reinvent.png](https://clickhouse.com/uploads/product_reinvent_9dc038e9ff.png)

<p>A bunch of colleagues spent the first week of December at the AWS re-Invent conference in Las Vegas, and we had some product announcements simultaneously. 
</p>
<p>Some highlights: Bring Your Own Cloud, Dashboards, and Native JSON support are all in Beta, the Postgres CDC connector in ClickPipes is in private preview, and vector similarity indexes are in early access.
</p>

<p><a href="https://clickhouse.com/blog/reinvent-2024-product-announcements">Read the blog post</a></p>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## Video corner

<ul> 
<li>ClickHouse has no PIVOT operator, but you can still achieve similar functionality using aggregate function combinators. Mark shows us how in his latest video, ‘<a href="https://clickhouse.com/videos/pivot-clickhouse">Can you PIVOT in ClickHouse?</a>!</li> 
<li>Tony Burke works in the platform engineering team at SolarWinds, where they ingest three million messages per second into ClickHouse. Tony <a href="https://clickhouse.com/videos/solarwinds-observability-3-milion-records-per-second">explains how his team enhanced ClickHouse performance</a>, shedding light on real-time telemetry data management and query optimization.</li> 
<li> <a href="https://clickhouse.com/videos/intro-refreshable-materialized-views">Refreshable materialized views</a> were recently made production-ready, so Mark did another video introducing them and showing some use cases.</li>
</ul>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>


## Quick reads

<ul> 
<li>Niels Reijers wanted to do a <a href="https://medium.com/@nielsreijers/python-itertools-style-group-by-in-sql-with-some-help-from-ai-ab072018fea4">Python itertools-style GROUP BY in ClickHouse SQL</a>, and with help from the Brave Browser’s AI and some of his own refactoring, he got there!</li> 
<li>Zander Matheson <a href="https://bytewax.io/blog/building-a-click-house-sink-for-bytewax">discusses the latest connector module available for Bytewax, the ClickHouse Sink</a>. This sink enables users to seamlessly write data from Bytewax into ClickHouse.</li> 
<li>Wolfram Kriesing explains <a href="https://picostitch.hashnode.dev/clickhouse-aggregations-and-django">how to call ClickHouse’s aggregation functions from Django</a>.</li>
<li>Matt Blewitt shares his <a href="https://matt.blwt.io/post/7-databases-in-7-weeks-for-2025/">7 Databases to look at in 2025</a>, and includes this great quote: “If I had to only pick two databases to deal with, I’d be quite happy with just Postgres and ClickHouse - the former for OLTP, the latter for OLAP.”</li> 
</ul>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## ClickHouse User Conference

![user-conference.png](https://clickhouse.com/uploads/user_conference_a2b03043e6.png)

<p>Are you planning the conferences you'll attend in 2025? We suggest Open House—The ClickHouse User Conference, which will be held on May 28th and 29th in San Francisco.
</p>
<p>We'll have a day of free training on the 28th, followed by talks on the 29th. Tickets aren’t available yet but register below to be updated on all information.
</p>

<p><a href="https://clickhouse.com/company/events/202505-global-open-house">Register to be kept informed</a></p>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>


## Post of the month

<p>Our favorite post this month was by <a href="https://x.com/megulzar">Gulzar Ahmed</a>, who’s using ClickHouse to help build Hyperzod, online delivery software for local businesses in India:</p>

![twitter-202412.png](https://clickhouse.com/uploads/twitter_202412_72254b4837.png)

<p>
<a href="https://x.com/megulzar/status/1864880796143583399">Read the post</a>
</p>
