---
title: "March 2024 Newsletter"
date: "2024-03-18T20:04:18.944Z"
author: "ClickHouse Team"
category: "Community"
excerpt: "Welcome to the March ClickHouse newsletter where we round up what’s been happening in real-time data warehouses in the last month."
---

# March 2024 Newsletter

Welcome to the March ClickHouse newsletter where we round up what’s been happening in real-time data warehouses in the last month.

This month, we have the 24.2 release with useful features for data ingestion, Rill dashboards for ClickHouse, and 10x faster materialized views using aggregation states. 


## Inside this issue

<ul> 
<li><a href="/blog/newsletter-march-2024?utm_source=clickhouse&amp;utm_medium=web&amp;utm_campaign=202403-newsletter#featured-community-member" style="color: #faff69;">Featured community member</a></li> 
<li><a href="/blog/newsletter-march-2024?utm_source=clickhouse&amp;utm_medium=web&amp;utm_campaign=202403-newsletter#242-release" style="color: #faff69;">24.2 release</a><br></li> 
<li><a href="/blog/newsletter-march-2024?utm_source=clickhouse&amp;utm_medium=web&amp;utm_campaign=202403-newsletter#rill-dashboards-for-clickhouse" style="color: #faff69;">Rill dashboards for ClickHouse</a><br></li> 
<li><a href="/blog/newsletter-march-2024?utm_source=clickhouse&amp;utm_medium=web&amp;utm_campaign=202403-newsletter#the-one-trillion-row-challenge" style="color: #faff69;">The One Trillion Row Challenge</a></li> 
<li><a href="/blog/newsletter-march-2024?utm_source=clickhouse&amp;utm_medium=web&amp;utm_campaign=202403-newsletter#10x-faster-materialized-views-with-aggregation-states" style="color: #faff69;">10x Faster Materialized Views with Aggregation States</a></li> 
<li><a href="/blog/newsletter-march-2024?utm_source=clickhouse&amp;utm_medium=web&amp;utm_campaign=202403-newsletter#chdb-joins-the-clickhouse-family" style="color: #faff69;">chDB joins the ClickHouse family</a><br></li> 
<li><a href="/blog/newsletter-march-2024?utm_source=clickhouse&amp;utm_medium=web&amp;utm_campaign=202403-newsletter#post-of-the-month" style="color: #faff69;">Post of the month</a><br></li> 
<li><a href="/blog/newsletter-march-2024?utm_source=clickhouse&amp;utm_medium=web&amp;utm_campaign=202403-newsletter#upcoming-events" style="color: #faff69;">Upcoming events</a><br></li> 
</ul>

## Featured community member

This month's featured community member is Steve Flitcroft, VP of R&amp;D at iVendi.

![202403-community-member.png](https://clickhouse.com/uploads/202403_community_member_9cabc4e707.png)

<p>Steve is perhaps better known as redsquare on the <a href="/slack" style="color: #faff69;">ClickHouse Community Slack</a>, where he has helped a lot of users solve problems that they’ve encountered when using ClickHouse.</p> 
<p>Whether it’s questions about refreshable materialized views, how to speed up a query, or understanding ClickHouse’s table engines, Steve has got you covered!</p> 
<p><a href="https://www.linkedin.com/in/steveflitcroft/" style="color: #faff69;" target="_blank">Follow Steve on LinkedIn</a></p>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## 24.2 release

![24.2.2.png](https://clickhouse.com/uploads/24_2_2_b7ee0b202f.png)

<p>The 24.2 release added some useful features for data ingestion. Adaptive asynchronous inserts make data batching smarter &amp; more efficient. Plus, ClickHouse is now smarter at detecting file formats even if the file extension is missing or wrong. We’ve also vectorized distance functions, speeding up vector search in RAG applications.</p> 
<p><a href="/blog/clickhouse-release-24-02?utm_source=clickhouse&amp;utm_medium=web&amp;utm_campaign=202403-newsletter" style="color: #faff69;">Read the release post</a></p>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## Rill dashboards for ClickHouse

![clickhouse-rill.png](https://clickhouse.com/uploads/clickhouse_rill_7699d6f965.png)

<p>Rill is a Business Intelligence tool that lets you build fast operational dashboards with sub-second performance. Having bumped into Alexey, ClickHouse’s Co-founder and CTO, at FOSDEM, this month they added a ClickHouse connector. In a blog post, Nishant Bangarwa explains how the connector works and gives step-by-step instructions to get your first Rill/ClickHouse dashboard up and running.</p> 
<p><a href="https://www.rilldata.com/blog/operational-bi-embedded-dashboards-for-clickhouse?utm_source=clickhouse&amp;utm_medium=web&amp;utm_campaign=202403-newsletter" style="color: #faff69;"  target="_blank">Read the blog post</a></p>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## The One Trillion Row Challenge

![1trillion_row_challenge.png](https://clickhouse.com/uploads/1trillion_row_challenge_37514baf99.png)

<p>At the start of February, Dask launched the <a href="https://medium.com/coiled-hq/one-trillion-row-challenge-5bfd4c3b8aef?utm_source=clickhouse&amp;utm_medium=web&amp;utm_campaign=202403-newsletter" style="color: #faff69;"  target="_blank">1 trillion row challenge</a>, which requires entrants to query 1 trillion rows of data stored across 100,000 Parquet files in S3. Dale McDiarmid, our resident challenge expert, set to work and got the query running in under 3 minutes for $0.56 in AWS spot instances. In the blog post, Dale explains how he optimized query performance, including bottleneck detection and working out the best size of AWS machine to use.&nbsp;</p> 
<p><a href="/blog/clickhouse-1-trillion-row-challenge?utm_source=clickhouse&amp;utm_medium=web&amp;utm_campaign=202403-newsletter" style="color: #faff69;">Read the blog post</a></p>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## 10x Faster Materialized Views with Aggregation States 

![query.png](https://clickhouse.com/uploads/query_b6bfa62d41.png)

<p>Sayed Alesawy has written a blog post in which he takes us through various techniques to improve the performance of queries on observability data. An initial query on 26 million rows takes 693 seconds to run, which is reduced to 11 seconds with a materialized view. But sub-second response time is needed and this is achieved by storing <a href="/blog/aggregate-functions-combinators-in-clickhouse-for-arrays-maps-and-states#working-with-aggregation-states?utm_source=clickhouse&amp;utm_medium=web&amp;utm_campaign=202403-newsletter" style="color: #faff69;">aggregation states</a> instead of scalar values.&nbsp;</p> 
<p><a href="https://sayedalesawy.hashnode.dev/how-to-use-clickhouse-aggregation-states-to-boost-materialized-views-performance-by-more-than-10-times?utm_source=clickhouse&amp;utm_medium=web&amp;utm_campaign=202403-newsletter"  target="_blank" style="color: #faff69;">Read the blog post</a></p>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## chDB joins the ClickHouse family

![Option 6.png](https://clickhouse.com/uploads/Option_6_cff43ad3dc.png)

<p>The biggest news of the month is that chDB, an embedded SQL OLAP engine powered by ClickHouse, is now part of ClickHouse. chDB’s creator and main contributor, Auxten, is joining forces with us to focus on evolving chDB and integrating it even more closely with the ClickHouse ecosystem. We’d love to know what you’d like us to work on next, which you can do via the <a href="https://github.com/orgs/chdb-io/discussions?utm_source=clickhouse&amp;utm_medium=web&amp;utm_campaign=202403-newsletter" style="color: #faff69;"  target="_blank">chDB GitHub discussion board</a>.</p> 
<p><a href="/blog/chdb-joins-clickhouse-family?utm_source=clickhouse&amp;utm_medium=web&amp;utm_campaign=202403-newsletter" style="color: #faff69;">Read the announcement</a></p>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## Post of the month

![tweet-1765785275014557831 (2).png](https://clickhouse.com/uploads/tweet_1765785275014557831_2_0f58e6ad0e.png)

<p>My favorite tweet this month was by <a href="https://twitter.com/medriscoll"  target="_blank" style="color: #faff69;">Michael E. Driscoll</a> (Founder of Rill Data) about chDB joining ClickHouse. <a href="https://twitter.com/medriscoll/status/1765785275014557831"  target="_blank" style="color: #faff69;">See it here</a></p>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## Upcoming events

<ul> 
<li><a href="https://clickhouse.com/company/events/v24-3-community-release-call?utm_source=clickhouse&amp;utm_medium=web&amp;utm_campaign=202403-newsletter" target="_blank" style="color: #faff69;">v24.3 ClickHouse Community Call</a>&nbsp;- March 26th</li> 
<li><a href="https://clickhouse.com/company/events/clickhouse-fundamentals?utm_source=clickhouse&amp;utm_medium=web&amp;utm_campaign=202403-newsletter" target="_blank" style="color: #faff69;">FREE ClickHouse Training</a>&nbsp;- March 27th &amp; 28th</li> 
<li><a href="https://www.meetup.com/clickhouse-bangalore-user-group/events/299479850/" target="_blank" style="color: #faff69;">Bangalore Meetup</a> - March 23rd<br></li> 
<li><a href="https://clickhouse.com/company/events/2024-03-aws-summit-paris?utm_source=clickhouse&amp;utm_medium=web&amp;utm_campaign=202403-newsletter" target="_blank" style="color: #faff69;">AWS Summit Paris</a> - April 3rd</li> 
<li><a href="https://clickhouse.com/company/events/2024-04-aws-summit-amsterdam?utm_source=clickhouse&amp;utm_medium=web&amp;utm_campaign=202403-newsletter" target="_blank" style="color: #faff69;">AWS Summit Amsterdam</a> - April 9th</li> 
<li><a href="https://www.meetup.com/clickhouse-switzerland-meetup-group/events/299628922/" target="_blank" style="color: #faff69;">Zurich Meetup</a> - April 16th</li> 
<li><a href="https://www.meetup.com/clickhouse-denmark-meetup-group/events/299629133/" target="_blank" style="color: #faff69;">Copenhagen Meetup</a> - April 23rd</li> 
<li><a href="https://clickhouse.com/company/events/v24-4-community-release-call?utm_source=clickhouse&amp;utm_medium=web&amp;utm_campaign=202403-newsletter" target="_blank" style="color: #faff69;">v24.4 ClickHouse Community Call</a> - April 30th<br></li> 
<li><a href="https://www.meetup.com/clickhouse-stockholm-user-group/events/299752651/" target="_blank" style="color: #faff69;">Stockholm Meetup</a> - May 22nd<br></li> 
<li><a href="https://www.meetup.com/clickhouse-dubai-meetup-group/events/299629189/" target="_blank" style="color: #faff69;">Dubai Meetup</a> - May 28th<br></li> 
</ul>