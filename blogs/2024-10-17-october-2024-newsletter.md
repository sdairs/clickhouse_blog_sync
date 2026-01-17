---
title: "October 2024 newsletter"
date: "2024-10-17T08:45:09.193Z"
author: "ClickHouse Team"
category: "Community"
excerpt: "Welcome to the October ClickHouse newsletter, which will round up what’s happened in real-time data warehouses over the last month."
---

# October 2024 newsletter

Welcome to the October ClickHouse newsletter, which will round up what’s happened in real-time data warehouses over the last month.

This month, we have the impressions and challenges of ClickHouse from a first-time user, the APPEND clause for Refreshable Materialized Views, the pancake SQL pattern, and more!

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>


## Inside this issue

<ul> 
<li><a href="https://clickhouse.com/blog/202410-newsletter#featured-community-member">Featured community member</a></li>
<li><a href="https://clickhouse.com/blog/202410-newsletter#upcoming-events">Upcoming events</a></li>
<li><a href="https://clickhouse.com/blog/202410-newsletter#clickhouse-for-embedded-analytics-first-impressions-and-unexpected-challenges">ClickHouse for Embedded Analytics: First Impressions and Unexpected Challenges</a></li>
<li><a href="https://clickhouse.com/blog/202410-newsletter#using-clickhouse-for-high-volume-data-pipeline-processing-and-asynchronous-updates">Using ClickHouse for High-Volume Data Pipeline Processing and Asynchronous Updates</a></li>
<li><a href="https://clickhouse.com/blog/202410-newsletter#249-release">24.9 release</a></li>
<li><a href="https://clickhouse.com/blog/202410-newsletter#the-pancake-sql-pattern">The pancake SQL pattern</a></li>
<li><a href="https://clickhouse.com/blog/202410-newsletter#clickhouse-cloud-live-update-september-2024">ClickHouse Cloud Live Update: September 2024</a></li>
<li><a href="https://clickhouse.com/blog/202410-newsletter#quick-reads">Quick reads</a></li>
<li><a href="https://clickhouse.com/blog/202410-newsletter#post-of-the-month">Post of the month</a></li>
</ul>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>


## Featured community member

This month's featured community member is Duc-Canh Le, a Software Engineer at Ahrefs.

![featured-member-202410.png](https://clickhouse.com/uploads/featured_member_202410_c1f100c1e1.png)

Duc-Canh works on data infrastructure at Ahrefs and is responsible for developing and operating ClickHouse on over 600 machines that hold 100 PB of compressed data. 

<p>He is a regular contributor to the ClickHouse code base and has made 28 contributions in the calendar year. These include supporting <span style="color: #41d76b; font-family: terminal, monaco;">OPTIMIZE</span> on join tables to reduce their memory footprint, fixing a bug when using an empty tuple on the left-hand side of the `IN` function, and a fix for the <span style="color: #41d76b; font-family: terminal, monaco;">FINAL</span> clause when run on tables that don’t use adaptive granularity.&nbsp;</p>

<p><a href="https://www.linkedin.com/in/canhld?utm_source=clickhouse&amp;utm_medium=email&amp;utm_campaign=202410-newsletter" target="_blank">Follow Duc-Canh on LinkedIn</a></p>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## Upcoming events
 
<p><strong>Global events</strong></p> 
<ul> 
<li><a href="https://clickhouse.com/company/events/v24-10-community-release-call?utm_source=clickhouse&amp;utm_medium=email&amp;utm_campaign=202410-newsletter" target="_blank" id="">Release call 24.10</a> - Oct 31<br></li> 
<li><a href="https://clickhouse.com/company/events/202411-cloud-update-live?utm_source=clickhouse&amp;utm_medium=email&amp;utm_campaign=202410-newsletter" target="_blank">ClickHouse Cloud Live Update</a> -&nbsp;Nov 12<br></li> 
</ul> 
<p><strong>Free training</strong></p> 
<ul> 
<li><a href="https://clickhouse.com/company/events/202410-emea-clickhouse-bigquery-workshop?utm_source=clickhouse&amp;utm_medium=email&amp;utm_campaign=202410-newsletter" target="_blank" id="">BigQuery to ClickHouse Workshop</a> - Oct 23<br></li> 
<li><a href="https://clickhouse.com/company/events/202410-emea-query-optimization?utm_source=clickhouse&amp;utm_medium=email&amp;utm_campaign=202410-newsletter" target="_blank" id="">Query optimization with ClickHouse workshop</a> - Oct 30</li> 
<li><a href="https://clickhouse.com/company/events/clickhouse-fundamentals?utm_source=clickhouse&amp;utm_medium=email&amp;utm_campaign=202410-newsletter" target="_blank" id="">ClickHouse Fundamentals</a> - Nov 6</li> 
<li>Migrating from Postgres to ClickHouse Workshop<br></li> 
<ul> 
<li><a href="https://clickhouse.com/company/events/202411-apj-postgres-to-clickhouse-migration?utm_source=clickhouse&amp;utm_medium=email&amp;utm_campaign=202410-newsletter" target="_blank" id="">Asia Pacific</a> - Nov 20</li> 
<li><a href="https://clickhouse.com/company/events/202411-emea-postgres-to-clickhouse-migration?utm_source=clickhouse&amp;utm_medium=email&amp;utm_campaign=202410-newsletter" target="_blank">Europe</a> - Nov 27</li> 
</ul> 
</ul> 
<p><strong>Events in AMER</strong></p> 
<ul> 
<li><a href="https://clickhouse.com/company/events/202410-amer-la-coffee-with-clickhouse?utm_source=clickhouse&amp;utm_medium=email&amp;utm_campaign=202410-newsletter" target="_blank" id="">Coffee with ClickHouse in Santa Monica</a> - Oct 25</li> 
<li><a href="https://clickhouse.com/company/events/202411-amer-kubecon?utm_source=clickhouse&amp;utm_medium=email&amp;utm_campaign=202410-newsletter" target="_blank" id="">KubeCon North America</a> - Nov 12-15<br></li> 
<li><a href="https://clickhouse.com/company/events/202411-amer-microsoft-ignite?utm_source=clickhouse&amp;utm_medium=email&amp;utm_campaign=202410-newsletter" target="_blank" id="">Microsoft Ignite - Chicago</a> - Nov 19-22<br></li> 
</ul> 
<p><strong>Events in EMEA</strong></p> 
<ul> 
<li><a href="https://www.meetup.com/clickhouse-spain-user-group/events/303096564" target="_blank" id="">Meetup in Madrid</a> - Oct 22<br></li> 
<li><a href="https://clickhouse.com/company/events/202410-emea-coffee-with-clickhouse?utm_source=clickhouse&amp;utm_medium=email&amp;utm_campaign=202410-newsletter" target="_blank" id="">Coffee with ClickHouse</a> - Oct 23</li> 
<li><a href="https://www.meetup.com/open-source-real-time-data-warehouse-real-time-analytics/events/302938622/" target="_blank" id="">Meetup in Oslo</a> - Oct 31</li> 
<li><a href="https://www.meetup.com/clickhouse-spain-user-group/events/303096876/?eventOrigin=network_page" target="_blank" id="">Meetup in Barcelona</a> - Nov 12</li> 
<li><a href="https://www.meetup.com/clickhouse-belgium-user-group/events/303049405" target="_blank" id="">Meetup in Ghent</a> - Nov 19</li> 
<li><a href="https://www.meetup.com/clickhouse-dubai-meetup-group/events/303096989/" target="_blank" id="">Meetup in Dubai</a> - Nov 21</li> 
<li><a href="https://www.meetup.com/clickhouse-france-user-group/events/303096434" target="_blank" id="">Meetup in Paris</a> - Nov 26</li> 
</ul> 
<p><strong>Events in Asia Pacific</strong></p> 
<ul> 
<li><a href="https://clickhouse.com/company/events/202410-dataai-summit-vic-melbourne?utm_source=clickhouse&amp;utm_medium=email&amp;utm_campaign=202410-newsletter" target="_blank">Data &amp; AI Summit VIC</a> - Oct 22<br></li> 
</ul>


## ClickHouse for Embedded Analytics: First Impressions and Unexpected Challenges

Jorin Vogel recently started using ClickHouse for an embedded analytics project and shared his first thoughts. He also described things he wished he’d known before starting, including how materialized views work and working with duplicate data. This is a good read if you’re just starting your ClickHouse journey.

[Read the blog post](https://jorin.me/clickhouse-for-embedded-analytics-first-impressions-and-unexpected-challenges/?utm_source=clickhouse&utm_medium=web&utm_campaign=202410-newsletter)

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## Using ClickHouse for High-Volume Data Pipeline Processing and Asynchronous Updates

![pipeline.png](https://clickhouse.com/uploads/pipeline_bcfce69e8c.png)

<p>Marais Kruger works at Evinced (a company focused on accessibility compliance for enterprise clients) and has written a blog post about this experience building a ClickHouse-based data pipeline.</p><p>Marais explains how they designed their pipeline to handle a large volume of incoming data while also handling infrequent updates to that data. He also describes how they made writes idempotent using ClickHouse’s duplicate block detection and a setting used to ensure similar behavior with dependent materialized views.</p><p>This one is a good read for the ClickHouse enthusiast or anyone curious about how to design data pipelines at scale.</p><p><a href="https://blog.devgenius.io/architecting-for-scale-e998fc0adef0?utm_source=clickhouse&amp;utm_medium=web&amp;utm_campaign=202410-newsletter" target="_blank">Read the blog post</a></p>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## 24.9 release

![Blog Banner 24.9 release.png](https://clickhouse.com/uploads/Blog_Banner_24_9_release_fee8640903.png)

<p>The 24.9 release introduced the <span style="color: #41d76b; font-family: terminal, monaco;">APPEND</span> clause for working with refreshable materialized views. When configured, the materialized view’s query will append results to the end of the destination table rather than replacing everything. This is useful if you want to capture snapshots of data from other tables or poll data from an external API and store it in ClickHouse.</p><p>This release also made response headers available when using the <span style="font-family: terminal, monaco; color: #41d76b;">url</span> table function, automatic inference of the <span style="font-family: terminal, monaco; color: #41d76b;">Variant</span> data type, and aggregate functions to query the new <span style="font-family: terminal, monaco; color: #41d76b;">JSON</span> data type.</p><p><a href="https://clickhouse.com/blog/clickhouse-release-24-09">Read the release post</a></p>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## The pancake SQL pattern

![pancake.png](https://clickhouse.com/uploads/pancake_22852d5f23.png)

<p>Jacek Migdal had a tricky problem: One of the Quesma dashboards was sending up to 10 queries to populate a single panel, putting the ClickHouse database under pressure.&nbsp;</p><p>Jacek was trying to solve this problem and had a lightbulb moment while feeding his toddler pancakes: Could the dashboard queries be redesigned to look more like pancakes?</p><p>Rather than spawning multiple queries, they put everything into one query. The aggregations would be stacked on each other, like a pancake, where each layer is a grouping with a limit, and between layers, they have metric aggregations—our pancake “fillings.”</p><p>It worked, and they’re seeing a 50x increase in performance.</p><p><a href="https://quesma.com/blog-detail/pancake-sql-pattern">Read the blog post</a></p>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## ClickHouse Cloud Live Update: September 2024

![Cloud monthly update feature.png](https://clickhouse.com/uploads/Cloud_monthly_update_feature_41fa8ef49c.png)

<p>We had a special guest, <a href="https://www.linkedin.com/in/dunithd/">Dunith Danushka</a> from Redpanda, join us for our latest ClickHouse Cloud update call. Dunith and Mark Needham showed how to use the combination of Redpanda Serverless, ClickHouse Cloud, and OpenAI to power a sports commentary Copilot application.</p><p>We also had updates on some upcoming features in ClickHouse Cloud, including Bring Your Own Cloud, Compute-Compute separation, and the JSON data type.</p><p><a href="https://clickhouse.com/videos/202409-clickhouse-cloud-live-updates">Watch the recording</a></p>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## Quick reads

<ul> 
<li>Juan S. Carrillo <a href="https://clickhouse.com/blog/semantic-versioning-udf">wrote a User Defined Function (UDF)</a> to make it easier to sort software versions.</li> 
<li>Rafal Kwasny explores various options for data storage and focuses on <a href="https://rafalkwasny.com/clickhouse-tick-store">using ClickHouse for high-performance financial data analysis</a>.</li> 
<li>Alexey Milovidov <a href="https://clickhouse.com/videos/my-favorite-clickhouse-features">shared his favorite ClickHouse features of 2024</a> at a recent San Francisco meetup.</li> 
<li>Sai Srirampur and Bryan Clark wrote a blog post explaining how to <a href="https://neon.tech/blog/postgres-meets-analytics-cdc-from-neon-to-clickhouse-via-peerdb">combine ClickHouse and Neon for real-time analytics on transactional data</a> using PeerDB to sync the data.</li> 
</ul>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## Post of the month

<p>Our favorite post this month was by <a href="https://x.com/CarlLindesvard/">Carl Lindesvärd</a> about ClickHouse’s compression rate, a somewhat underrated feature!</p>

![tweet_1842113023890137251_20241016_155508_via_10015_io.png](https://clickhouse.com/uploads/tweet_1842113023890137251_20241016_155508_via_10015_io_4844142657.png)

