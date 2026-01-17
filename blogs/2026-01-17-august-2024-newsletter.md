---
title: "August 2024 newsletter"
date: "2024-08-22T09:45:00.742Z"
author: "ClickHouse Team"
category: "Community"
excerpt: "Welcome to the August ClickHouse newsletter, which will round up what’s happened in real-time data warehouses over the last month."
---

# August 2024 newsletter

Welcome to the August ClickHouse newsletter, which will round up what’s happened in real-time data warehouses over the last month.

This month, we have exciting news about PeerDB joining ClickHouse, downsampling time series data, join performance improvements in the 24.7 release, and more!

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## Alexey, ClickHouse creator and CTO, goes on tour!

![Banner Alexey the rockstar.png](https://clickhouse.com/uploads/Banner_Alexey_the_rockstar_ea3688418f.png)

We are excited to share that **Alexey Milovidov, creator and CTO of ClickHouse**, will be delivering a series of technical talks around the world. Please join these events in person to hear him speak and a chance to ask him ANY question about ClickHouse! Space is limited, register below:

<ul> 
<li>Sun, Aug 25 - China Meetup, Guangzhou - <a href="https://mp.weixin.qq.com/s/GSvo-7xUoVzCsuUvlLTpCw" target="_blank">Register</a></li> 
<li>Tues, Aug 27 - VLDB Talk, Guangzhou - <a href="https://vldb.org/2024/?program-schedule" target="_blank">Schedule</a></li> 
<li>Thur, Sept 5 - San Francisco Meetup (Cloudflare) - <a href="https://www.meetup.com/clickhouse-silicon-valley-meetup-group/events/302540575" target="_blank">Register</a></li> 
<li>Mon, Sept 9 - Raleigh Meetup (Deutsche Bank) - <a href="https://www.meetup.com/clickhouse-nc-meetup-group/events/302557230" target="_blank">Register</a></li> 
<li>Tues, Sept 10 - New York Meetup (Rokt) - <a href="https://www.meetup.com/clickhouse-new-york-user-group/events/302575342" target="_blank">Register</a></li> 
<li>Thur, Sept 12 - Chicago Fireside Chat (Jump Capital) - <a href="https://lu.ma/43tvmrfw" target="_blank">Register</a></li> 
<li>Wed, Sept 18 - Warsaw AWS Cloud Day - <a href="https://aws.amazon.com/events/cloud-days/warsaw/" target="_blank">Register</a></li> 
</ul>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## Inside this issue

<ul>
<li><a href="https://clickhouse.com/blog/202408-newsletter#featured-community-member-chase-richards">Featured community member: Chase Richards</a></li>
<li><a href="https://clickhouse.com/blog/202408-newsletter#upcoming-events">Upcoming events</a></li>
<li><a href="https://clickhouse.com/blog/202408-newsletter#clickhouse-welcomes-peerdb">ClickHouse welcomes PeerDB</a></li>
<li><a href="https://clickhouse.com/blog/202408-newsletter#downsampling-time-series-data">Downsampling time series data</a></li>
<li><a href="https://clickhouse.com/blog/202408-newsletter#247-release">24.7 release</a></li>
<li><a href="https://clickhouse.com/blog/202408-newsletter#how-maxilect-transferred-clickhouse-between-geographically-distant-data-centers">How Maxilect transferred ClickHouse between geographically distant data centers</a></li>
<li><a href="https://clickhouse.com/blog/202408-newsletter#java-client-the-sequel">Java Client… the SEQUEL?!</a></li>
<li><a href="https://clickhouse.com/blog/202408-newsletter#quick-reads">Quick reads</a></li>
<li><a href="https://clickhouse.com/blog/202408-newsletter#post-of-the-month">Post of the month</a></li></ul>


<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## Featured community member: Chase Richards

This month's featured community member is Chase Richards, VP of Engineering at Corsearch.

![202408-featured.png](https://clickhouse.com/uploads/202408_featured_697afc61da.png)

<p>Chase Richards previously led engineering efforts at Marketly from a 2011 start-up through its acquisition in 2020 by Corsearch.</p>

<p>Chase recently <a href="/videos/how-corsearch-uses-clickhouse-today" target="_blank">presented at the Bellevue meetup</a> about his experience replacing MySQL with ClickHouse as the backing database for a client-facing report interface for their search engine protection service. Having done this in 2018, Chase earned his status as a trailblazer in the community.</p>

<p>More recently, Chase and his team have <a href="/blog/corsearch-replaces-mysql-with-clickhouse-for-content-and-brand-protection" target="_blank">added vector-based analytics</a> to their fraud detection model. They’re also using ClickHouse to monitor their search engine scraping setup.</p>

<p><a href="https://www.linkedin.com/in/chasesrichards/" target="_blank">Follow Chase on LinkedIn</a></p>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## Upcoming events

<ul> 
<li><a href="https://mp.weixin.qq.com/s/GSvo-7xUoVzCsuUvlLTpCw" target="_blank" id="">ClickHouse Guangzhou Meetup</a> - Aug 25</li> 
<li><a href="https://www.meetup.com/clickhouse-australia-user-group/events/302732666" target="_blank" id="">ClickHouse + Melbourne Data Engineering Meetup</a> - Aug 27<br></li> 
<li><a href="https://www.meetup.com/clickhouse-seattle-user-group/events/302518075" target="_blank" id="">ClickHouse Meetup in Bellevue</a> - Aug 27<br></li> 
<li><a href="/company/events/202409-clickhouse-developer?utm_campaign=202408-newsletter&amp;utm_source=clickhouse&amp;utm_medium=web" target="_blank">ClickHouse Developer Training</a> - Sep 3<br></li> 
<li><a href="https://www.meetup.com/clickhouse-switzerland-meetup-group/events/302267429" target="_blank" id="">ClickHouse Meetup in Zurich</a> - Sep 5</li> 
<li><a href="https://www.meetup.com/clickhouse-australia-user-group/events/302862966/" target="_blank" id="">ClickHouse + Sydney Data Engineering Meetup</a> - Sep 5<br></li> 
<li><a href="https://www.meetup.com/clickhouse-silicon-valley-meetup-group/events/302540575/" target="_blank" id="">ClickHouse Meetup @ Cloudflare - San Francisco</a> - Sep 5<br></li> 
<li><a href="/company/events/202409-kcd-sydney?utm_campaign=202408-newsletter&amp;utm_source=clickhouse&amp;utm_medium=web" target="_blank">Kubernetes Community Days - Sydney</a> - Sep 5-6<br></li> 
<li><a href="https://www.meetup.com/clickhouse-nc-meetup-group/events/302557230/" target="_blank" id="">ClickHouse Meetup in Raleigh</a> - Sep 9<br></li> 
<li><a href="https://www.meetup.com/clickhouse-toronto-user-group/events/301490855/" target="_blank" id="">ClickHouse Meetup @ Shopify - Toronto</a> - Sep 10<br></li> 
<li><a href="/company/events/202409-apj-clickhouse-admin-workshop?utm_campaign=202408-newsletter&amp;utm_source=clickhouse&amp;utm_medium=web" target="_blank">ClickHouse Admin Workshop</a> - Sep 10<br></li> 
<li><a href="/company/events/202409-amer-awssummit-toronto" target="_blank" id="">AWS Summit Toronto</a> - Sep 10<br></li> 
<li><a href="https://www.meetup.com/clickhouse-new-york-user-group/events/302575342/" target="_blank">ClickHouse Meetup @ Rokt - NYC</a> - Sep 10<br></li> 
<li><a href="/company/events/202409-emea-coffee-with-clickhouse?utm_campaign=202408-newsletter&amp;utm_source=clickhouse&amp;utm_medium=web" target="_blank">Coffee with ClickHouse - Amsterdam</a> - Sep 11<br></li> 
<li><a href="/company/events/clickhouse-fundamentals?utm_campaign=202408-newsletter&amp;utm_source=clickhouse&amp;utm_medium=web" target="_blank">ClickHouse Fundamentals</a> - Sep 11<br></li> 
<li><a href="https://lu.ma/43tvmrfw" target="_blank" id="">ClickHouse Meetup @ Jump Capital</a> - Sep 12<br></li> 
<li><a href="https://www.meetup.com/clickhouse-austin-user-group/events/302558689/" target="_blank" id="">ClickHouse Meetup - Austin</a> - Sep 17<br></li> 
<li><a href="https://www.meetup.com/clickhouse-london-user-group/events/302977267" target="_blank" id="">ClickHouse Meetup in London</a> - Sep 17<br></li> 
<li><a href="/company/events/202409-emea-awscloudday-warsaw?utm_campaign=202408-newsletter&amp;utm_source=clickhouse&amp;utm_medium=web" target="_blank">AWS Cloud Day - Warsaw</a> - Sep 18<br></li> 
<li><a href="/company/events/202409-emea-inperson-clickhouse-fundamentals?utm_campaign=202408-newsletter&amp;utm_source=clickhouse&amp;utm_medium=web" target="_blank">In-person ClickHouse Fundamentals training - Amsterdam</a> - Sep 18-19</li> 
<li><a href="/company/events/202409-emea-bigdataldn?utm_campaign=202408-newsletter&amp;utm_source=clickhouse&amp;utm_medium=web" target="_blank">Big Data LDN (London)</a> - Sep 18-19<br></li> 
<li><a href="/company/events/202409-cloud-update-live?utm_campaign=202408-newsletter&amp;utm_source=clickhouse&amp;utm_medium=web" target="_blank">ClickHouse Cloud Live Update</a> - Sep 24<br></li> 
<li><a href="/company/events/202409-dataengbytes-sydney?utm_campaign=202408-newsletter&amp;utm_source=clickhouse&amp;utm_medium=web" target="_blank">DataEngBytes - Sydney</a> - Sep 24<br></li> 
<li><a href="/company/events/202409-dataengbytes-perth?utm_campaign=202408-newsletter&amp;utm_source=clickhouse&amp;utm_medium=web" target="_blank">DataEngBytes - Perth</a> - Sep 27<br></li> 
<li><a href="/company/events/202410-dataengbytes-melbourne?utm_campaign=202408-newsletter&amp;utm_source=clickhouse&amp;utm_medium=web" target="_blank">DataEngBytes - Melbourne</a> - Oct 1<br></li> 
<li><a href="/company/events/202410-dataengbytes-auckland?utm_campaign=202408-newsletter&amp;utm_source=clickhouse&amp;utm_medium=web" target="_blank">DataEngBytes - Auckland</a> - Oct 4<br></li> 
</ul>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## ClickHouse welcomes PeerDB

![peerdb-nl.png](https://clickhouse.com/uploads/peerdb_nl_55c48390c4.png)

A couple of weeks ago, we were thrilled to announce today that ClickHouse joined forces with PeerDB, a Change Data Capture (CDC) provider focused on Postgres. 

Now, users have an easy button to sync their data from the number one transactional database to the number one analytical database. 

<a href="/blog/clickhouse-welcomes-peerdb-adding-the-fastest-postgres-cdc-to-the-fastest-olap-database">Read the announcement</a>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## Downsampling time series data

![timeseries.png](https://clickhouse.com/uploads/timeseries_561276ed91.png)

Phare is a platform for website monitoring, incident management, status pages, analytics, security, and alerting. They wanted to create a chart showing 90 days of monitoring data. As they collect one data point per minute, this meant that the chart needed to render 130,000 data points, which was both slow to do and difficult to interpret.

<p>Enter the <a href="/docs/en/sql-reference/aggregate-functions/reference/largestTriangleThreeBuckets">largestTriangleThreeBuckets</a> function, added to ClickHouse at the end of 2023. Using this function, they could remove redundant data points, making the chart quicker to create and easier to interpret.</p>

<p><a href="https://docs.phare.io/articles/downsampling-time-series-data">Read the blog post</a></p>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## 24.7 release

![356555235-1fd960de-35b0-4e39-b0d2-283cd1a49bd2.png](https://clickhouse.com/uploads/356555235_1fd960de_35b0_4e39_b0d2_283cd1a49bd2_b865c512ae.png)

The 24.7 release includes many performance improvements. These include a full sorting merge algorithm for ASOF joins, a faster parallel hash join algorithm, and improvements to the “read in order” algorithm when running queries with a high-selectivity filter.

We also have deduplication In Materialized Views, automatic named tuples, and the percent_rank window function.

<p><a href="/blog/clickhouse-release-24-07">Read the release post</a></p>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## How Maxilect transferred ClickHouse between geographically distant data centers

![maxilect.png](https://clickhouse.com/uploads/maxilect_6e6a847ec9.png)

Maxilect, an IT solutions provider for the Adtech and Fintech industries, has written an experience report on moving a ClickHouse cluster from a data center in Miami to another in Detroit.

In this blog post, Igor Ivanov and Denis Palaguta explain how they did this using the clickhouse-copier tool while keeping the service up and serving user requests.

<a href="https://maxilect-company.medium.com/how-we-transferred-the-clickhouse-database-between-geographically-distant-data-centers-ad3c853dce3f">Read the blog post</a>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## Java Client… the SEQUEL?!

![javasequel.png](https://clickhouse.com/uploads/javasequel_2ba3c969de.png)

We recently started work on revamping the ClickHouse Java client. The new version has a more intuitive, self-documenting API, and we’ve added more usage examples to the documentation. 

It’s still in alpha, but we’d love for you to try it and send us your thoughts.

<a href="/blog/java-client-sequel">Read the blog post</a>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## Quick reads

<ul> 
<li>Vladimir Ivoninskii shares his <a href="https://dzone.com/articles/7-essential-tips-for-a-production-clickhouse" target="_blank">best techniques for effectively running a production ClickHouse cluster</a>.</li> 
<li>Denys Golotiuk shows how to <a href="https://datachild.net/machinelearning/image-similarity-search-with-embeddings-based-on-sentence-transformers" target="_blank">do image similarity search</a> using vector embeddings in ClickHouse with the L2Distance function.</li> 
<li>Joe Zhou explores <a href="https://www.dragonflydb.io/blog/using-dragonfly-as-a-table-engine-for-clickhouse?hss_channel=tw-1535352010421063680" target="_blank">integrating ClickHouse with Dragonfly</a>, an ultra-high-throughput, Redis-compatible in-memory data store.<br></li> 
</ul>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## Post of the month

<p>Our <a href="https://www.linkedin.com/posts/y-combinator_congrats-to-the-team-at-peerdb-yc-s23-on-activity-7224096453613301763-M0b5/" target="_blank" id="">favorite post this month</a> was by Y Combinator about PeerDB joining ClickHouse.</p>

![ln-post202408.png](https://clickhouse.com/uploads/ln_post202408_c07e584d11.png)

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>