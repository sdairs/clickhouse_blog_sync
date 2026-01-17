---
title: "April 2024 Newsletter"
date: "2024-04-17T17:15:50.242Z"
author: "ClickHouse Team"
category: "Community"
excerpt: "Welcome to the April ClickHouse newsletter where we round up what’s been happening in real-time data warehouses over the last month."
---

# April 2024 Newsletter

Welcome to the April ClickHouse newsletter where we round up what’s been
happening in real-time data warehouses over the last month.

This month, we have the 24.3 release, building a rate limiter, a migration
from MySQL to ClickHouse story, meetup videos, and more!

## Inside this issue

<ul>
  <li><a href="/blog/newsletter-april-2024#featured-community-member" >Featured community member</a></li>
  <li><a href="/blog/newsletter-april-2024#upcoming-events" >Upcoming events</a></li>
  <li><a href="/blog/newsletter-april-2024#243-release" >24.3 release</a></li>
  <li><a href="/blog/newsletter-april-2024#storing-continuous-profiling-data-in-clickhouse" >Storing Continuous Profiling Data in ClickHouse</a></li>
  <li><a href="/blog/newsletter-april-2024#migrating-to-clickhouse-releems-journey" >Migrating to ClickHouse: Releem's Journey</a></li>
  <li>
    <a href="/blog/newsletter-april-2024#how-we-built-a-19-pib-logging-platform-with-clickhouse-and-saved-millions" >How we Built a 19 PiB Logging Platform with ClickHouse and Saved Millions</a>
  </li>
  <li><a href="/blog/newsletter-april-2024#building-a-rate-limiter-with-clickhouse" >Building a Rate Limiter with ClickHouse</a></li>
  <li><a href="/blog/newsletter-april-2024#video-corner" >Video Corner</a></li>
  <li><a href="/blog/newsletter-april-2024#clickhouse-cloud-updates" >ClickHouse Cloud Updates</a></li>
  <li><a href="/blog/newsletter-april-2024#post-of-the-month" >Post of the month</a></li>
</ul>

## Featured community member

This month's featured community member is Shivji kumar Jha, a Staff Engineer
for Data Platforms at Nutanix.

![april2024-featuredmember.png](https://clickhouse.com/uploads/april2024_featuredmember_4356cb31d7.png)

Shiv leads a five-member team, managing and supporting Nutanix's data
platform, which acts as a service for messaging, streaming, event sourcing,
analytics, and time series databases. Shiv actively engages with the
communities of the technologies used at Nutanix, including ClickHouse.

We recently hosted a ClickHouse meetup in Nutanix’s office in Bangalore,
India. Shiv was invaluable in making this event happen, helping organize it,
and acting as an MC for the evening. He recorded all the talks and
<a href="https://www.youtube.com/playlist?list=PLA7KYGkuAD06bXmVPWe6ohM618pVKUZfg" target="_blank">uploaded them</a> to YouTube afterward. Shiv also participated in <a href="https://clickhouse.com/company/events/2024-05-15-live-q-and-a?utm_source=clickhouse&amp;utm_medium=website&amp;utm_campaign=202404-newsletter" target="_blank">a follow-up Q&amp;A session on 15th April</a> to address unanswered questions from the meetup.

Thanks for all your work Shiv and we’ll see you at the next meetup!

<a href="https://www.linkedin.com/in/shivjijha/">Follow Shivji on LinkedIn</a>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## Upcoming events

<ul>
  <li>
    <a href="https://www.meetup.com/clickhouse-denmark-meetup-group/events/299629133/" target="_blank" >Copenhagen Meetup</a> - April 23rd
  </li>
  <li>
    <a href="https://clickhouse.com/company/events/clickhouse-fundamentals?utm_source=clickhouse&amp;utm_medium=website&amp;utm_campaign=202404-newsletter" target="_blank">FREE ClickHouse Training</a> - April 24th &amp; 25th

  </li>
  <li>
    <a
      href="https://clickhouse.com/company/events/2024-04-aws-summit-london?utm_source=clickhouse&amp;utm_medium=website&amp;utm_campaign=202404-newsletter" target="_blank">AWS Summit London</a> - April 24th
  </li>
  <li>
    <a
      href="https://clickhouse.com/company/events/v24-4-community-release-call?utm_source=clickhouse&amp;utm_medium=website&amp;utm_campaign=202404-newsletter" target="_blank">v24.4 ClickHouse Community Call</a> - April 30th
  </li>
  <li>
    <a href="https://www.meetup.com/clickhouse-bangalore-user-group/events/300405581/" target="_blank">Bengaluru Meetup</a>
    - May 4th
  </li>
  <li>
    <a href="https://clickhouse.com/company/events/2024-05-aws-summit-berlin?utm_source=clickhouse&amp;utm_medium=website&amp;utm_campaign=202404-newsletter" target="_blank">AWS Summit Berlin</a>
    - May 15th
  </li>
  <li>
    <a href="https://www.meetup.com/clickhouse-stockholm-user-group/events/299752651/"
      target="_blank" >Stockholm Meetup</a> - May 22nd
  </li>
  <li>
    <a href="https://www.meetup.com/clickhouse-dubai-meetup-group/events/299629189/" target="_blank">Dubai Meetup</a>
    - May 28th
  </li>
</ul>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## 24.3 release

![Release blog cover (2).png](https://clickhouse.com/uploads/Release_blog_cover_2_0aff4edfa7.png)

The big feature in the 24.3 release is the analyzer being enabled by default.
Analyzer is a new query analysis and optimization infrastructure that’s been
in the works for a couple of years and lets you have multiple
<span style="font-family: 'courier new', courier">ARRAY JOIN</span> clauses in
a query, treats tuple elements like columns, handles queries with nested CTEs
and sub-queries, and more.

<a href="https://clickhouse.com/blog/clickhouse-release-24-03?utm_source=clickhouse&amp;utm_medium=website&amp;utm_campaign=202404-newsletter" target="_blank">Read the release post</a>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## Storing Continuous Profiling Data in ClickHouse

![2024-04-15_14-02-36.png](https://clickhouse.com/uploads/2024_04_15_14_02_36_0c5c8f21bf.png)

Coroot is an open-source tool for observability that turns observability data
into actionable insights. Nikolay Sivko wrote a blog post in which he
describes how they built their own storage system for profiling data based on
ClickHouse. After defining continuous profiling, Nikolay takes us through the
data model and gives examples of queries that check on the performance of a
service.

<a href="https://coroot.com/blog/storing-continuous-profiling-data-in-clickHouse?utm_source=clickhouse&amp;utm_medium=website&amp;utm_campaign=202404-newsletter" target="_blank">Read the blog post</a>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## Migrating to ClickHouse: Releem's Journey

Releem is a MySQL performance tuning tool that automatically detects
performance degradation and optimizes configuration files. To do this, they
collect metrics from hundreds of database servers across various operating
systems and cloud solutions.

They used to store these metrics in MySQL, which started to struggle once it
reached almost 5 billion records. Enter ClickHouse, which helped shrink the
database size by 20 times, cut aggregation query times from 45 to 2 minutes,
and reduced the page load time of the Releem dashboard by 25%.

<a href="https://releem.com/blog/migrating-to-clickhouse?utm_source=clickhouse&amp;utm_medium=website&amp;utm_campaign=202404-newsletter" target="_blank" >Read the blog post</a>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## How we Built a 19 PiB Logging Platform with ClickHouse and Saved Millions

![logging_thumbnail.png](https://clickhouse.com/uploads/logging_thumbnail_f5cabe3803.png)

<a href="https://www.linkedin.com/in/rory-crispin/" target="_blank"
    >Rory Crispin</a>, SRE at ClickHouse, shared his experience building a platform for the logging data generated by ClickHouse Cloud. Rory takes us through key design decisions, including whether to use Kafka and structured vs unstructured logging. He also explains why the team decided to use OpenTelemetry to collect metrics and does a cost comparison of the in-house solution vs using an off-the-shelf product like Datadog.&nbsp;

<a href="https://clickhouse.com/blog/building-a-logging-platform-with-clickhouse-and-saving-millions-over-datadog?utm_source=clickhouse&amp;utm_medium=website&amp;utm_campaign=202404-newsletter" target="_blank">Read the blog post</a>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## Building a Rate Limiter with ClickHouse

![2024-04-15_13-55-49.png](https://clickhouse.com/uploads/2024_04_15_13_55_49_cc7d77b5b5.png)

If you were going to build a rate limiter, the obvious choice for storing the
data would be Redis. But Brad Lhotsky, Systems and Security Administrator at
Craigslist, was curious whether ClickHouse would be fit-for-purpose and used
it to build a proof-of-concept. Brad shared the slides of a talk explaining
how he imported data from Kafka, built a bridge from the ACL API to
ClickHouse, and tested high availability, all in just one week.

<a href="https://speakerdeck.com/reyjrar/breaking-the-rules-rate-limiting-with-clickhouse?utm_source=clickhouse&amp;utm_medium=website&amp;utm_campaign=202404-newsletter" target="_blank">View the slide deck</a>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## Video corner

<ul>
  <li>
    At the New York City meetup, Adam Azzam presented how Prefect
    <a href="https://www.youtube.com/watch?v=OKxCrcSWT1g" target="_blank">uses ClickHouse to enable real-time event drive orchestration</a>.
  </li>
  <li>
    Mark Needham walked us through some of the most common
    <a href="https://www.youtube.com/watch?v=7ApwD0cfAFI" target="_blank">aggregate function combinators</a>
    and showed how and why we might use them.
  </li>
  <li>
    At Kubecon Europe 2024, Manish Gill discussed
    <a href="https://www.youtube.com/watch?v=AFoMsLMZKik" target="_blank">the challenges of auto-scaling databases in Kubernetes</a>, using ClickHouse Cloud as a case study.
  </li>
</ul>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## ClickHouse Cloud Updates

![Cloud Monthly Update Highlights (1).png](https://clickhouse.com/uploads/Cloud_Monthly_Update_Highlights_1_3aa0dcc0fa.png)

<ul>
  <li>
    Over the last 9 months, we’ve been rebuilding the UI for ClickHouse Cloud
    and
    <a
      href="https://clickhouse.com/blog/new-clickhouse-cloud-experience?utm_source=clickhouse&amp;utm_medium=website&amp;utm_campaign=202404-newsletter"
      target="_blank">last week, started rolling it out to everybody</a>.
  </li>
  <li>
    Today,
    <a
      href="https://clickhouse.com/cloud/clickpipes?utm_source=clickhouse&amp;utm_medium=website&amp;utm_campaign=202404-newsletter"
      target="_blank"
      id=""
      >ClickPipes</a>
    introduces beta support for continuous data ingestion from S3 and GCS. Let
    us know if you’re interested in giving this a try by replying to this email!
  </li>
  <li>
    Tokyo (ap-northeast-1) has been added as a new region for AWS. 
    <a
      href="https://clickhouse.cloud/signUp?utm_source=clickhouse&amp;utm_medium=website&amp;utm_campaign=202404-newsletter"
      target="_blank">Sign up now</a>.
    
  </li>
</ul>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## Post of the month

Our favorite post this month was by
<a href="https://twitter.com/divyenduz">Divyendu Singh</a> about real-time
monitoring.

![tweet-1775832353572544681 (1).png](https://clickhouse.com/uploads/tweet_1775832353572544681_1_2db9cd6f7b.png)

<a href="https://twitter.com/divyenduz/status/1775832353572544681"
target="_blank">See it here</a>
