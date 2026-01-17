---
title: "May 2024 Newsletter"
date: "2024-05-22T09:55:35.861Z"
author: "ClickHouse Team"
category: "Community"
excerpt: "Welcome to the May ClickHouse newsletter, which will round up what’s been happening in real-time data warehouses over the last month."
---

# May 2024 Newsletter

Welcome to the May ClickHouse newsletter, which will round up what’s been happening in real-time data warehouses over the last month.

This month, we have recursive CTEs in the 24.4 release, the launch of ClickHouse developer certification, real-time fraud detection at Instacart, and more!

## Inside this issue

- [Featured community member](/blog/newsletter-may-2024#featured-community-member)
- [Upcoming events](/blog/newsletter-may-2024#upcoming-events)
- [24.4 release](/blog/newsletter-may-2024#244-release)
- [Become a ClickHouse Certified Developer](/blog/newsletter-may-2024#become-a-clickhouse-certified-developer)
- [Real-time Fraud Detection at Instacart](/blog/newsletter-may-2024#real-time-fraud-detection-at-instacart)
- [K-Means Clustering with ClickHouse](/blog/newsletter-may-2024#k-means-clustering-with-clickhouse)
- [Simplified Kubernetes Logging with Fluentbit and ClickHouse](/blog/newsletter-may-2024#simplified-kubernetes-logging-with-fluentbit-and-clickhouse)
- [The New Building Blocks of Observability](/blog/newsletter-may-2024#the-new-building-blocks-of-observability)
- [Using ClickHouse for Financial Charts](/blog/newsletter-may-2024#using-clickhouse-for-financial-charts)
- [Post of the Month](/blog/newsletter-may-2024#post-of-the-month)

## Featured community member

This month's featured community member is Dan Goodman, Co-Founder and CEO of Tangia, a service for hosting interactive live streams.

![featured-member-may2024.png](https://clickhouse.com/uploads/featured_member_may2024_7babf3516a.png)

Dan has been part of the ClickHouse community for at least 18 months and frequently gives the engineering team feedback on both missing features and how existing features can be improved.

Dan writes a blog about distributed systems, where he’s previously written about topics like range partitioning and building a Fly.io scheduler.

A few weeks ago he wrote a blog post titled <a href="https://www.aspiring.dev/instant-embeddings-clustering-with-k-means-and-clickhouse?utm_source=clickhouse&amp;utm_medium=web&amp;utm_campaign=202405-newsletter" target="_blank">Finding Trends With Approximate Embedding Clustering</a>. In the post, he explains the importance of approximation techniques when working with big datasets and walks through how to implement the Dynamic K-Means++ algorithm with ClickHouse. 

<a href="https://www.linkedin.com/in/daniel-goodman-7a813214a/" target="_blank">Follow Dan on LinkedIn</a>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## Upcoming events

<ul> 
<li><a href="https://www.meetup.com/clickhouse-dubai-meetup-group/events/299629189/" target="_blank" style="color: #faff69;">Dubai Meetup</a> - May 28th<br></li> 
<li><a href="/company/events/2024-05-aws-summit-dubai?loc=newsletter-april2024" target="_blank">AWS Summit Dubai</a> - May 29th</li> 
<li><a href="/company/events/v24-5-community-release-call?loc=newsletter-april2024" target="_blank" id="">v24.5 Community Call</a> - May 30th<br></li> 
<li><a href="https://www.meetup.com/clickhouse-silicon-valley-meetup-group/events/300523061/" target="_blank" id="">San Francisco Meetup</a> - June 4th</li> 
<li><a href="/company/events/2024-06-aws-summit-stockholm?loc=newsletter-april2024" target="_blank">AWS Summit Stockholm</a> - June 4th<br></li> 
<li><a href="https://www.meetup.com/clickhouse-tokyo-user-group/events/300798053/" target="_blank" id="">Tokyo Meetup</a> - June 5th</li> 
<li><a href="/company/events/2024-06-aws-summit-madrid?loc=newsletter-april2024" target="_blank">AWS Summit Madrid</a> - June 5th<br></li> 
<li><a href="/company/events/clickhouse-fundamentals?loc=newsletter-april2024" target="_blank">ClickHouse Fundamentals</a> - June 26th &amp; 27th<br></li> 
<li><a href="/company/events/2024-06-aws-summit-dc?loc=newsletter-april2024" target="_blank">AWS Summit D.C.</a> - June 26th</li> 
<li><a href="https://www.meetup.com/clickhouse-netherlands-user-group/events/300781068/" target="_blank" id="">Amsterdam Meetup</a> - June 27th</li> 
<li><a href="https://www.meetup.com/clickhouse-france-user-group/events/300783448/" target="_blank" id="">Paris Meetup</a> - July 9th</li> 
<li><a href="https://www.meetup.com/clickhouse-new-york-user-group/events/300595845/" target="_blank" id="">New York Meetup</a> - July 9th</li> 
</ul>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## 24.4 release

![24.4-release.png](https://clickhouse.com/uploads/24_4_release_2b721e4021.png)

The standout feature in the 24.4 release is recursive CTEs (Common Table Expressions), and we made a London Underground-themed example to show you how they work. This release also sees improvements to JOIN performance and the QUALIFY clause to filter the values of window functions.

<a href="/blog/clickhouse-release-24-04?loc=newsletter-april2024" _blank="" target="_blank">Read the release post</a>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## Become a ClickHouse Certified Developer

![certified-developer.png](https://clickhouse.com/uploads/certified_developer_c745754b9a.png)

<p>Rich Raposa <a href="/blog/first-official-clickhouse-certification?loc=newsletter-april2024" id="">recently announced</a> the launch of the official ClickHouse Developer Certification Program, the only certification directly from ClickHouse.</p> 
<p>This certification program validates developers’ proficiency in using ClickHouse to build robust, high-performance data solutions. This certification will showcase your mastery of ClickHouse and help you distinguish yourself as a trusted database management and analytics expert.</p> 
<p><a href="/learn/certification?loc=newsletter-april2024"  style="color: #faff69;">Learn more about certification</a></p>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## Real-time Fraud Detection at Instacart

![instacart.png](https://clickhouse.com/uploads/instacart_73a07488a3.png)

<p>Nick Shieh, Shen Zhu, and Xiaobing Xia have written a blog post where they walk us through Yoda, a decision platform service they built at Instacart to detect fraudulent activities and take action quickly. ClickHouse was chosen as the primary real-time datastore for this system because it can both ingest and query large amounts of data in real time. I especially liked the part of the post where they describe how real-time features fed into the service are derived from ClickHouse SQL queries.</p> 
<p><a href="https://tech.instacart.com/real-time-fraud-detection-with-yoda-and-clickhouse-bd08e9dbe3f4?utm_source=clickhouse&amp;utm_medium=web&amp;utm_campaign=202405-newsletter" target="_blank">Read the blog post</a></p>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## K-Means Clustering with ClickHouse

![K-means clustering.png](https://clickhouse.com/uploads/K_means_clustering_392356d0bb.png)

<p>Recently, when helping a user who wanted to compute centroids from vectors held in ClickHouse, we realized that the same solution could be used to implement K-Means clustering. They wanted to do this at scale across potentially billions of data points while ensuring memory could be tightly managed. In this post, we show how to implement K-means clustering using just SQL and show that it can scale to billions of records while running significantly faster than the same code in scikit-learn.</p> 
<p><a href="/blog/kmeans-clustering-with-clickhouse?loc=newsletter-april2024"  >Read the blog post</a></p>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## Simplified Kubernetes Logging with Fluentbit and ClickHouse

<p>Logging is one of the hot ClickHouse use cases of the moment, so I was excited to come across this blog post by Muthukumaran. Fluentbit is a lightweight logging and metrics processor and forwarder designed for containerized environments. Muthukumaran walks us through the steps to setup a metrics server to monitor resource utilization in Kubernetes and then shows how to configure Fluentbit to get those metrics into ClickHouse.</p> 
<p><a href="https://blog.devops.dev/simplified-kubernetes-logging-with-fluentd-and-clickhouse-9c620ec2dfa9?utm_source=clickhouse&amp;utm_medium=web&amp;utm_campaign=202405-newsletter" target="_blank" style="color: #faff69;">Read the blog post</a></p>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## The New Building Blocks of Observability

 ![obs-building-blocks-3.png](https://clickhouse.com/uploads/obs_building_blocks_3_c64383af8e.png)

<p>This article focuses on what the author coins the three new elements in the observability period table: OpenTelemetry, eBPF, and ClickHouse. OpenTelemetry has emerged as the de facto standard for telemetry data, eBPF makes it possible to generate traces and metrics with zero instrumentation, and ClickHouse is used to ingest and query all this data. The article also covers a series of Observability startups that are using ClickHouse - Groundcover, SigNoz, and DeepFlow.</p> 
<p><a href="https://observability-360.com/article/ViewArticle?id=observability-building-blocks&amp;utm_source=clickhouse&amp;utm_medium=email&amp;utm_campaign=202405-newsletter" target="_blank" id="">Read the blog post</a></p>

## Using ClickHouse for Financial Charts

![SCR-20240521-odub.jpeg](https://clickhouse.com/uploads/SCR_20240521_odub_7bf15ea035.jpeg)

<p>After giving a brief crash course into when (and when not) to use ClickHouse, Adis Nezirović demonstrates how to ingest, query, and visualize financial time-series data. Along the way, he shows how to use the Null table engine to massage data and aggregate states to reduce the amount of data kept around. To conclude, Adis creates a candlestick chart using the Grafana QueryBuilder.</p>
<p><a href="https://medium.com/mop-developers/using-clickhouse-for-charts-profits-ad6dc56abf67" target="_blank" style="color: #faff69;">Read the blog post</a></p>

## Post of the Month

<p>Our favorite post this month was by <a href="https://twitter.com/ludwigABAP" target="_blank">ludwig</a> who was impressed by both the speed of ClickHouse queries and the quality of its data compression.</p> 

![tweet-1788330168999624920 (1).png](https://clickhouse.com/uploads/tweet_1788330168999624920_1_22d9878e33.png)

<p>After giving a brief crash course into when (and when not) to use ClickHouse, Adis Nezirović demonstrates how to ingest, query, and visualize financial time-series data. Along the way, he shows how to use the Null table engine to massage data and aggregate states to reduce the amount of data kept around. To conclude, Adis creates a candlestick chart using the Grafana QueryBuilder.</p> 
<p><a href="https://twitter.com/ludwigABAP/status/1788330168999624920" target="_blank" style="color: #faff69;">View the post</a></p>
