---
title: "November 2024 newsletter"
date: "2024-11-21T14:08:25.678Z"
author: "ClickHouse Team"
category: "Community"
excerpt: "Welcome to the November ClickHouse newsletter, which will round up what’s happened in real-time data warehouses over the last month."
---

# November 2024 newsletter

Welcome to the November ClickHouse newsletter, which will round up what’s happened in real-time data warehouses over the last month.

The big news is that Refreshable Materialized Views are production-ready, and we have an official Docker image!

Alexey Milovidov was a guest on Data Talks on the Rocks, we learn how to simplify queries with dictionaries, and there’s a deep dive on the new JSON data type.

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>


## Inside this issue

<ul> 
<li><a href="https://clickhouse.com/blog/202411-newsletter#featured-community-member">Featured community member</a></li>
<li><a href="https://clickhouse.com/blog/202411-newsletter#upcoming-events">Upcoming events</a></li>
<li><a href="https://clickhouse.com/blog/202411-newsletter#2410-release">24.10 Release</a></li>
<li><a href="https://clickhouse.com/blog/202411-newsletter#alexey-milovidov-on-data-talks-on-the-rocks">Alexey Milovidov on Data Talks on the Rocks</a></li>
<li><a href="https://clickhouse.com/blog/202411-newsletter#simplifying-queries-with-clickhouse-dictionaries">Simplifying queries with ClickHouse dictionaries</a></li>
<li><a href="https://clickhouse.com/blog/202411-newsletter#building-a-financial-data-pipeline-with-alpha-vantage-and-clickhouse">Building a financial data pipeline with Alpha Vantage and ClickHouse</a></li>
<li><a href="https://clickhouse.com/blog/202411-newsletter#how-we-built-a-new-powerful-json-data-type-for-clickhouse">How we built a new powerful JSON data type for ClickHouse</a></li>
<li><a href="https://clickhouse.com/blog/202411-newsletter#clickhouse-cloud-live-update-november-2024">ClickHouse Cloud Live Update: November 2024</a></li>
<li><a href="https://clickhouse.com/blog/202411-newsletter#quick-reads">Quick reads</a></li>
<li><a href="https://clickhouse.com/blog/202411-newsletter#post-of-the-month">Post of the month</a></li>
</ul>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## Visit us at AWS re:Invent

![aws-reinvent-202411.png](https://clickhouse.com/uploads/aws_reinvent_202411_0edd3daa88.png)
<p>Are you heading to re:Invent? We are too, and would love to connect with you!</p>

<p>Book a meeting with us beforehand by emailing sales@clickhouse.com, or stop by our booth #1737 for:</p>

- A chance to meet all three of <a href="https://clickhouse.com/company/our-story">our founders</a>: Aaron, Alexey, and Yury
- Live demos
- Exclusive swag
- And a chat with ClickHouse experts

<p>Don’t miss out – we’re also hosting a ClickHouse House Party with the Chainsmokers. It’ll be one epic night you won’t want to miss! 
</p>

![house-party-202411.png](https://clickhouse.com/uploads/house_party_202411_ba778b3256.png)
<p>
<a href="https://clickhouse.com/houseparty/vegas-2024">Register for the Chainsmokers party</a>
</p>
<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## Featured community member

This month's featured community member is Lukas Biewald, co-founder and CEO at <a href="https://wandb.ai?utm_source=clickhouse&amp;utm_medium=email&amp;utm_campaign=202411-newsletter" target="_blank">Weights & Biases</a>.

![featured-202411.png](https://clickhouse.com/uploads/featured_202411_c82ec62b60.png)
<p>
Lukas has worked in machine learning for 20 years, previously co-founding Figure Eight with Chris Van Pelt, where they specialized in data labeling for machine learning applications. Appen acquired the company in March 2019. 
</p>
<p>In 2018, Lukas co-founded Weights & Biases, an MLOps platform designed to assist machine learning practitioners in tracking experiments, managing datasets, and collaborating on model development.
</p>
<p>Lukas <a href="https://clickhouse.com/videos/ai-developer-platform?utm_source=clickhouse&amp;utm_medium=email&amp;utm_campaign=202411-newsletter" target="_blank">presented</a> at the ClickHouse San Francisco meetup in September, where he shared his experience building AI applications and how they use ClickHouse as part of their Weave application. This was also written up in <a href="https://clickhouse.com/blog/weights-and-biases-scale-ai-development?utm_source=clickhouse&amp;utm_medium=email&amp;utm_campaign=202411-newsletter" target="_blank">a blog published last week</a>.</p>

<p><a href="https://www.linkedin.com/in/lbiewald?utm_source=clickhouse&amp;utm_medium=email&amp;utm_campaign=202411-newsletter" target="_blank">Follow Lukas on LinkedIn</a></p>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## Upcoming events
 
<p><strong>Global events</strong></p> 
<ul> 
<li><a href="https://clickhouse.com/company/events/v24-11-community-release-call?utm_source=clickhouse&utm_medium=email&utm_campaign=202411-newsletter" target="_blank" id="">Release call 24.11</a> - Nov 28<br></li> 

</ul> 
<p><strong>Free training</strong></p> 
<ul> 
<li><a href="https://clickhouse.com/company/events/202411-emea-postgres-to-clickhouse-migration?utm_source=clickhouse&utm_medium=email&utm_campaign=202411-newsletter" target="_blank" id="">Migrating from Postgres to ClickHouse Workshop</a> - Virtual - Nov 27<br></li> 
<li><a href="https://clickhouse.com/company/events/clickhouse-fundamentals?utm_source=clickhouse&utm_medium=email&utm_campaign=202411-newsletter" target="_blank" id="">ClickHouse Fundamentals</a> - Virtual- Dec 4</li> 
<li><a href="https://clickhouse.com/company/events/202412-emea-stockholm-inperson-clickhousetraining?utm_source=clickhouse&utm_medium=email&utm_campaign=202411-newsletter" target="_blank" id="">In-Person ClickHouse Training in Sweden</a> - Sweden- Dec 9</li> 
<li><a href="https://clickhouse.com/company/events/202412-emea-copenhagen-inperson-clickhousetraining?utm_source=clickhouse&utm_medium=email&utm_campaign=202411-newsletter" target="_blank" id="">In-Person ClickHouse Training in Denmark</a> - Denmark - Dec 9</li> 
<li><a href="https://clickhouse.com/company/events/202412-amer-manhattan-inperson-clickhouse-developer?utm_source=clickhouse&utm_medium=email&utm_campaign=202411-newsletter" target="_blank">ClickHouse Developer In-Person Training in New York</a> - Manhattan, NY - Dec 11-12</li> 
<li><a href="https://clickhouse.com/company/events/202412-global-training-clickhouse-developer?utm_source=clickhouse&utm_medium=email&utm_campaign=202411-newsletter" target="_blank">ClickHouse Developer Training</a> - Virtual - Dec 18-19</li> 

</ul> 
<p><strong>Events in AMER</strong></p> 
<ul> 
<li><a href="https://clickhouse.com/company/events/202411-amer-microsoft-ignite?utm_source=clickhouse&utm_medium=email&utm_campaign=202411-newsletter" target="_blank" id="">Microsoft Ignite</a> - Chicago - Nov 19-22</li> 
<li><a href="https://clickhouse.com/company/events/202412-amer-reinvent-meetingrequests?utm_source=clickhouse&utm_medium=email&utm_campaign=202411-newsletter" target="_blank" id="">AWS re:Invent 2024</a> - Las Vegas - Dec 2-6<br></li> 
<li><a href="https://www.meetup.com/clickhouse-new-york-user-group/events/304268174" target="_blank" id="">Meetup in New York</a> - Dec 9<br></li> 
<li><a href="https://www.meetup.com/clickhouse-silicon-valley-meetup-group/events/304286951" target="_blank" id="">Meetup in San Francisco</a> - Dec 12<br></li> 
</ul> 
<p><strong>Events in EMEA</strong></p> 
<ul> 
<li><a href="https://www.meetup.com/clickhouse-dubai-meetup-group/events/303096989/" target="_blank" id="">Meetup in Dubai</a> - Nov 21<br></li> 
<li><a href="https://www.meetup.com/clickhouse-france-user-group/events/303096434" target="_blank" id="">Meetup in Paris</a> - Nov 26</li> 
<li><a href="https://www.meetup.com/clickhouse-netherlands-user-group/events/303638814/" target="_blank" id="">Meetup in Amsterdam</a> - Dec 3</li> 
<li><a href="https://www.meetup.com/clickhouse-stockholm-user-group/events/304382411/" target="_blank" id="">Meetup in Stockholm</a> - Dec 9</li> 
</ul>
<br>

## 24.10 release

![release-24.10.png](https://clickhouse.com/uploads/release_24_10_988ee5facb.png)

<p>Refreshable Materialized Views are production-ready! That’s the big news in the 24.10 release, but we’ve also simplified table cloning with the <span style="font-family: terminal, monaco; color: #41d76b;">CLONE AS</span> clause, and there’s remote file caching, which is super helpful when querying S3 buckets.</p>

<p><a href="https://clickhouse.com/blog/clickhouse-release-24-10">Read the release post</a></p>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## Alexey Milovidov on Data Talks on the Rocks

![alexey-data talks-202411.png](https://clickhouse.com/uploads/alexey_data_talks_202411_ffc0bfdf7c.png)

<p>Data Talks on the Rocks is a series of interviews with thought leaders and founders discussing the latest trends in data and analytics. Michael Driscoll, CEO and Co-founder of Rill Data, hosts it.
</p>
<p>In episode 4, his guest was none other than Alexey Milovidov, the CTO and Co-founder of ClickHouse. In a wide-ranging conversation, they discussed the importance of hashing functions in database design, how AI might impact database technologies in the future, the development of ClickHouse's new analyzer, and more.
</p>
<p><a href="https://www.rilldata.com/blog/rill-clickhouse-alexey-milovidov-interview" target="_blank">Watch the interview</a></p>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>


## Simplifying queries with ClickHouse dictionaries

<p><a href="https://www.linkedin.com/in/jeffreyneedles/">Jeffrey Needles</a>, founder of Aggregations.io, has written a blog post explaining how to simplify queries using dictionaries.</p>

<p>Jeffrey takes us through why you’d want to use a dictionary, where data is sourced from, and how to choose the right type of key before demonstrating the performance gain from using them in a query.
</p>
<p><a href="https://aggregations.io/blog/clickhouse-dictionaries">Read the blog post</a></p>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## Building a financial data pipeline with Alpha Vantage and ClickHouse

![correlation returns-202411.png](https://clickhouse.com/uploads/correlation_returns_202411_b71341e433.png)

<p>Craig Dickson builds a high-performance data pipeline using Alpha Vantage for data acquisition and ClickHouse for data storage and analytics. 
</p>
<p>After querying the Alpha Vantage API data, Craig cleans it up in Pandas before ingesting it into ClickHouse Cloud. He then shows how to create various data visualizations using Vega-Altair.
</p>
<p><a href="https://medium.com/@thecraigdickson/building-a-financial-data-pipeline-with-alpha-vantage-and-clickhouse-5860d1e5a4be">Read the blog post</a></p>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## How we built a new powerful JSON data type for ClickHouse

![json-data-type-202411.png](https://clickhouse.com/uploads/json_data_type_202411_7b2068bbc1.png)

<p>The new JSON data type was introduced in version 24.8 in August, and we showed some examples <a href="https://clickhouse.com/blog/clickhouse-release-24-08">in the release post</a> but didn’t explore it in depth.
</p>
<p>That all changes with this blog post, where Tom Schreiber and Pavel Kruglov explain how it works under the hood. They explain how the new data type overcomes challenges like having values of multiple data types in the same JSON path, how to avoid pushing work to query time, and how to prevent an avalanche of column data files on disk. 
</p>
<p>There are lots of diagrams explaining how it all works. One to read for ClickHouse enthusiasts!</p>

<p><a href="https://clickhouse.com/blog/a-new-powerful-json-data-type-for-clickhouse">Read the blog post</a></p>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## ClickHouse Cloud Live Update: November 2024

<p>Krithika Balagurunathan and Zach Naimon joined us on our latest ClickHouse Cloud live update call. They taught us about <a href="https://clickhouse.com/cloud/bring-your-own-cloud">Bring Your Own Cloud</a> and <a href="https://clickhouse.com/docs/en/cloud/reference/compute-compute-separation">Compute-compute separation</a>, respectively. 
</p>
<p>After giving an overview of the features and a brief demo, Zach and Krithika hosted a detailed Q&A, which included the following questions:
</p>
<p>Does BYOC meet FedRAMP requirements? Can horizontal autoscaling be automated based on resource consumption? How do you migrate an existing cluster to BYOC? Can you have powerful instances for read/write nodes and less powerful instances for read-only nodes?
</p>
<p>Check out the full recording below to hear the answers to these questions and more!
</p>
<p><a href="https://clickhouse.com/videos/clickhouse-cloud-live-november-2024-byoc-compute-compute-separation">Watch the recording</a></p>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## Quick reads

<ul> 
<li>It's not really a quick read, but ClickHouse now has <a href="https://hub.docker.com/_/clickhouse">an official Docker image</a>!</li> 
<li>Carl Lindesvärd posted <a href="https://x.com/CarlLindesvard/status/1848706279293763917">a Twitter thread about the things he’s learned from six months of working with ClickHouse</a>.</li> 
<li>Ravindra Elicherla <a href="https://ravindraelicherla.medium.com/storing-tick-by-tick-webscocket-data-into-clickhouse-f4bbd29d0d65">stores tick-by-tick Webscocket data in ClickHouse</a>.</li>
<li>I came across <a href="https://github.com/FrigadeHQ/trench">Trench</a>, an event-tracking system built on Apache Kafka and ClickHouse. It powers <a href="https://github.com/FrigadeHQ/trench"> Frigade's</a> real-time event-tracking pipeline, handles large event volumes, and provides <a href="https://clickhouse.com/engineering-resources/what-is-real-time-analytics">real-time analytics</a></li> 
<li>The MetricFire team explains <a href="https://medium.com/@MetricFire/how-to-monitor-clickhouse-with-telegraf-and-metricfire-6b4aef886c49">how to monitor ClickHouse with Telegraf and MetricFire</a>.</li> 
<li>Jesse Grodman, Software Engineer at <a href="https://www.triplewhale.com/">Triple Whale</a>, shares how to <a href="https://medium.com/@jgrodman/migrating-clickhouse-data-without-adding-load-to-the-db-031d6a868b0e">move data from an unsharded ClickHouse cluster to a sharded one</a> without adding load to the existing cluster.</li> 
</ul>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## Post of the month

<p>Our favorite post this month was by <a href="https://x.com/steventey/status/1855669066817839116">Steven Tey</a> about ClickHouse’s arrayIntersect function.</p>

![tweet-202411.png](https://clickhouse.com/uploads/tweet_202411_301f2111e1.png)

<p>
<a href="https://x.com/steventey/status/1855669066817839116">Read the post</a>
</p>
