---
title: "September 2024 newsletter"
date: "2024-09-19T13:37:36.533Z"
author: "ClickHouse Team"
category: "Community"
excerpt: "Welcome to the September ClickHouse newsletter, which will round up what’s happened in real-time data warehouses over the last month."
---

# September 2024 newsletter

Welcome to the September ClickHouse newsletter, which will round up what’s
happened in real-time data warehouses over the last month. This month, we have
the much-awaited JSON data type, our 1st ClickHouse research paper, a Private
Preview of BYOC on AWS, better PyPi stats with Ibis, and&nbsp;more!

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>


## Inside this issue

- [Featured community member](https://clickhouse.com/blog/202409-newsletter#featured-community-member)
- [Upcoming events](https://clickhouse.com/blog/202409-newsletter#upcoming-events)
- [VLDB 2024: First ClickHouse research paper](https://clickhouse.com/blog/202409-newsletter#vldb-2024-first-clickhouse-research-paper)
- [How Reco leverages advanced analytics to detect sophisticated SaaS threats](https://clickhouse.com/blog/202409-newsletter#how-reco-leverages-advanced-analytics-to-detect-sophisticated-saas-threats)
- [24.8 LTS release](https://clickhouse.com/blog/202409-newsletter#248-lts-release)
- [Better PyPI stats with Ibis, ClickHouse, and Shiny](https://clickhouse.com/blog/202409-newsletter#better-pypi-stats-with-ibis-clickhouse-and-shiny)
- [ClickHouse Cloud: BYOC AWS in Private Preview](https://clickhouse.com/blog/202409-newsletter#clickhouse-cloud-byoc-aws-in-private-preview)
- [Quick reads](https://clickhouse.com/blog/202409-newsletter#quick-reads)
- [Post of the month](https://clickhouse.com/blog/202409-newsletter#post-of-the-month)

<p style="margin-bottom: 0;line-height: 0;">&nbsp;</p>

## Featured community member

![sep2024featuredmember.png](https://clickhouse.com/uploads/sep2024featuredmember_eec8525999.png)

<p>
  beehiiv is a newsletter platform that helps creators, publishers, and
  businesses build and grow their email audiences. They collect events capturing
  every time an email is processed, every time it lands in an inbox, every time
  it’s deferred, every time it’s bounced, every time you open it, every time you
  click a link, and so on.
</p>
<p>
  Eric has worked at beehiv for just over a year and was responsible for moving data operations from Postgres to ClickHouse Cloud. There’s <a href="https://clickhouse.com/blog/data-hive-the-story-of-beehiivs-journey-from-postgres-to-clickhouse?utm_source=clickhouse&amp;utm_medium=web&amp;utm_campaign=202409-newsletter">a user story on the work he and his team did</a>, and he also presented at the
  <a href="https://clickhouse.com/videos/transistion-from-postgres-to-clickhouse?utm_source=clickhouse&amp;utm_medium=web&amp;utm_campaign=202409-newsletter">New York meetup in the summer</a>.
</p>
<p>
  Eric previously worked as a Tech Lead at Arthur.ai, where he architected and built the company's data ingestion pipeline, storage, and much of the backend infrastructure.
</p>
<p>
  <a
    href="https://www.linkedin.com/in/eric-abis-30a03a13?utm_source=clickhouse&amp;utm_medium=web&amp;utm_campaign=202409-newsletter" target="_blank" >Follow Eric on LinkedIn</a>
</p>


<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## Upcoming events

<p><strong>Global events</strong></p>
<ul>
  <li>
    <a href="https://clickhouse.com/company/events/202409-cloud-update-live?utm_source=clickhouse&amp;utm_medium=web&amp;utm_campaign=202409-newsletter" >ClickHouse Cloud Live Update</a> - Sep 24
  </li>
  <li>
    <a href="https://clickhouse.com/company/events/v24-9-community-release-call?utm_source=clickhouse&amp;utm_medium=web&amp;utm_campaign=202409-newsletter">24.9 release community call</a>
    - Sep 26
  </li>
</ul>
<p><strong>Free training</strong></p>
<ul>
  <li>
    <a href="https://clickhouse.com/company/events/202409-amer-query-optimization?utm_source=clickhouse&amp;utm_medium=web&amp;utm_campaign=202409-newsletter">Query optimization with ClickHouse workshop</a>
    - Sep 25<strong><br /></strong>
  </li>
  <li>
    <a href="https://clickhouse.com/company/events/202410-apj-singapore-inperson-training?utm_source=clickhouse&amp;utm_medium=web&amp;utm_campaign=202409-newsletter">In-Person ClickHouse Workshop</a>
    - Singapore - Oct 3<br />
  </li>
</ul>
<p><strong>Events in EMEA</strong></p>
<ul>
  <li>
    <a href="https://www.meetup.com/clickhouse-meetup-israel/events/303095121" target="_blank">Meetup in Tel Aviv</a>
    - Sep 22
  </li>
  <li>
    <a href="https://www.meetup.com/clickhouse-spain-user-group/events/303096564" target="_blank">Meetup in Madrid</a>
    - Oct 22
  </li>
  <li>
    <a href="https://www.meetup.com/clickhouse-spain-user-group/events/303096876/?eventOrigin=network_page" target="_blank">Meetup in Barcelona</a>
    - Oct 29
  </li>
  <li>
    <a href="https://www.meetup.com/open-source-real-time-data-warehouse-real-time-analytics/events/302938622/" target="_blank">Meetup in Oslo</a>
    - Oct 31
  </li>
  <li>
    <a href="https://www.meetup.com/clickhouse-belgium-user-group/events/303049405" target="_blank">Meetup in Ghent</a>
    - Nov 19
  </li>
  <li>
    <a href="https://www.meetup.com/clickhouse-dubai-meetup-group/events/303096989/" target="_blank">Meetup in Dubai</a>
    - Nov 21
  </li>
  <li>
    <a href="https://www.meetup.com/clickhouse-france-user-group/events/303096434" target="_blank">Meetup in Paris</a>
    - Nov 26
  </li>
</ul>
<p><strong>Events in Asia Pacific</strong></p>
<ul>
  <li>
    <a href="https://clickhouse.com/company/events/202409-dataengbytes-sydney?utm_source=clickhouse&amp;utm_medium=web&amp;utm_campaign=202409-newsletter">DataEngBytes - Sydney</a>
    - Sep 24<strong><br /></strong>
  </li>
  <li>
    <a href="https://clickhouse.com/company/events/202409-dataengbytes-perth?utm_source=clickhouse&amp;utm_medium=web&amp;utm_campaign=202409-newsletter">DataEngBytes - Perth</a>
    - Sep 27<br />
  </li>
  <li>
    <a href="https://clickhouse.com/company/events/202410-dataengbytes-melbourne?utm_source=clickhouse&amp;utm_medium=web&amp;utm_campaign=202409-newsletter">DataEngBytes - Melbourne</a>
    - Oct 1<br />
  </li>
  <li>
    <a href="https://clickhouse.com/company/events/202410-dataengbytes-auckland?utm_source=clickhouse&amp;utm_medium=web&amp;utm_campaign=202409-newsletter">DataEngBytes - Auckland</a>
    - Oct 4<br />
  </li>
  <li>
    <a href="https://www.bigdataworldasia.com/2024-conference-programme/how-open-source-is-re-shaping-the-cloud-data-warehouse-landscape?utm_source=clickhouse&amp;utm_medium=web&amp;utm_campaign=202409-newsletter" target="_blank">Big Data &amp; AI World Asia</a>
    - Oct 10
  </li>
  <li>
    <a href="https://clickhouse.com/company/events/202410-cloudexcellence-summit-sydney?utm_source=clickhouse&amp;utm_medium=web&amp;utm_campaign=202409-newsletter">Cloud Excellence Summit NSW</a>
    - Oct 17<br />
  </li>
  <li>
    <a href="https://clickhouse.com/company/events/202410-dataai-summit-vic-melbourne?utm_source=clickhouse&amp;utm_medium=web&amp;utm_campaign=202409-newsletter">Data &amp; AI Summit VIC</a>
    - Oct 22<br />
  </li>
</ul>


<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## VLDB 2024: First ClickHouse research paper

![vldbpaper.png](https://clickhouse.com/uploads/vldbpaper_2172677f18.png)

<p>
  It’s been almost a year in the making, and at the end of August, we presented
  our first research paper at VLDB 2024.&nbsp;
</p>
<p>
  VLDB—the international conference on very large databases—is widely regarded
  as one of the leading conferences in data management. VLDB generally has an
  acceptance rate of ~20% among the hundreds of submissions.
</p>
<p>
  The paper concisely describes ClickHouse's most interesting architectural and
  system design components, which make it so fast. We’ve embedded the PDF of the
  paper in the blog post linked below.
</p>
<p>
  <a href="https://clickhouse.com/blog/first-clickhouse-research-paper-vldb-lightning-fast-analytics-for-everyone?utm_source=clickhouse&amp;utm_medium=web&amp;utm_campaign=202409-newsletter">Read the blog post</a>
</p>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## How Reco leverages advanced analytics to detect sophisticated SaaS threats

<p>
  Reco is a full-lifecycle SaaS security solution that uses ClickHouse as the
  foundation of its advanced analytics system. Nir Barak explains how ClickHouse
  gives them a holistic view of data across multiple layers and allows them to
  detect outliers and anomalies.
</p>
<p>
  <a href="https://www.reco.ai/blog/how-reco-leverages-advanced-analytics-to-detect-sophisticated-saas-threats?utm_source=clickhouse&amp;utm_medium=web&amp;utm_campaign=202409-newsletter" target="_blank">Read the blog post</a>
</p>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## 24.8 LTS release

![release24.8.png](https://clickhouse.com/uploads/release24_8_346c30e897.png)

<p>
  The 24.8 release is here, and it has an exciting feature that I (and many of
  you) have been waiting for - the new JSON data type!&nbsp;
</p>
<p>
  It’s in experimental mode, but that didn’t stop us from taking it through its
  paces while exploring structured data of events in football/soccer matches.
</p>
<p>
  This release also introduces the TimeSeries table engine, which can store
  Prometheus data, and a new Kafka table engine that supports exactly-once event
  processing.
</p>
<p>
  <a href="https://clickhouse.com/blog/clickhouse-release-24-08?utm_source=clickhouse&amp;utm_medium=web&amp;utm_campaign=202409-newsletter">Read the release post</a>
</p>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## Better PyPI stats with Ibis, ClickHouse, and Shiny

![pypistats.png](https://clickhouse.com/uploads/pypistats_67a959ca27.png)

<p>
  <a href="https://clickpy.clickhouse.com?utm_source=clickhouse&amp;utm_medium=web&amp;utm_campaign=202409-newsletter" target="_blank">ClickPy</a>
  is a ClickHouse-backed application that analyzes the download of Python
  packages published on PyPI. In addition to the front-end application, you can
  also query the underlying data, which is exactly what Cody Peterson has
  done.&nbsp;
</p>
<p>
  Cody shows how to connect to ClickPy using
  <a href="https://clickhouse.com/blog/introduction-to-ibis?utm_source=clickhouse&amp;utm_medium=web&amp;utm_campaign=202409-newsletter">Ibis</a>
  and then explores the seasonality of downloads of the clickhouse-connect
  package by day of the week and month. The results are visualized using
  <a href="http://plot.ly?utm_source=clickhouse&amp;utm_medium=web&amp;utm_campaign=202409-newsletter" target="_blank">plot.ly</a>, and Cody then puts everything together into a <a href="https://shiny.posit.co/py?utm_source=clickhouse&amp;utm_medium=web&amp;utm_campaign=202409-newsletter" target="_blank">Shiny</a>
  application.&nbsp;
</p>
<p>
  <a href="https://ibis-project.org/posts/better-pypi-stats?utm_source=clickhouse&amp;utm_medium=web&amp;utm_campaign=202409-newsletter" target="_blank">Read the blog post</a>
</p>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## ClickHouse Cloud: BYOC AWS in Private Preview

![byoc.png](https://clickhouse.com/uploads/byoc_943e12d96d.png)

<p>
  ClickHouse Cloud has been
  <a href="https://clickhouse.com/blog/clickhouse-cloud-generally-available?utm_source=clickhouse&amp;utm_medium=web&amp;utm_campaign=202409-newsletter">running for almost two years</a> and supports all the major cloud platforms, AWS, Azure, and GCP. So far, it’s
  been a SaaS offering that runs entirely on ClickHouse’s cloud account, which
  made it a non-starter for users with strict data residency and compliance
  requirements.&nbsp;
</p>
<p>
  We’re therefore happy to announce the Private Preview release of Bring Your
  Own Cloud (BYOC) on AWS. BYOC is a fully managed ClickHouse Cloud service
  deployed to your AWS account.
</p>
<p>
  The waiting list is now open, so be sure to sign up, and we’ll contact you to
  set you&nbsp;up.
</p>
<p>
  <a href="https://clickhouse.com/cloud/bring-your-own-cloud?utm_source=clickhouse&amp;utm_medium=web&amp;utm_campaign=202409-newsletter">Join the waitlist</a>
</p>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## Quick reads

<ul>
  <li>
    Heng Ma shows how to
    <a href="https://risingwave.com/blog/real-time-data-enrichment-and-analytics-with-risingwave-and-clickhouse?utm_source=clickhouse&amp;utm_medium=web&amp;utm_campaign=202409-newsletter" target="_blank">build a system that enriches shopping cart events with product details</a>. Using Rising Wave, a Kafka event data stream is joined with a product
    catalog, and the enriched events are written to ClickHouse using the Rising
    Wave-ClickHouse connector.&nbsp;
  </li>
  <li>
    Auxten released
    <a href="https://clickhouse.com/blog/chdb-pandas-dataframes-87x-faster?utm_source=clickhouse&amp;utm_medium=web&amp;utm_campaign=202409-newsletter">a new version of chDB</a>, the in-process embedded version of ClickHouse, that can query Pandas DataFrames 87 times faster than the initial version.
  </li>
  <li>
    I loved
    <a href="https://www.youtube.com/watch?v=_jjvaFWWKqg" target="_blank">this video</a>
    from Jess Archer’s talk at Laracon US 2024. It is an excellent introduction
    to ClickHouse and shows where it’s better than MySQL.
  </li>
  <li>
    Sai Srirampur
    <a href="https://clickhouse.com/blog/postgres-to-clickhouse-data-modeling-tips?utm_source=clickhouse&amp;utm_medium=web&amp;utm_campaign=202409-newsletter">shares his tips for ClickHouse data modeling aimed at Postgres users</a>. He explains various strategies to handle duplicates when using the
    ReplacingMergeTree table engine, how to handle null values, and the
    importance of ordering keys<br />
  </li>
</ul>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## Post of the month



<p>
  Our favorite post this month was by
  <a href="https://x.com/medriscoll" target="_blank">Michael Driscoll</a> about
  the new JSON data type:
</p>

![tweet_1831900730254582115_20240919_134823_via_10015_io.png](https://clickhouse.com/uploads/tweet_1831900730254582115_20240919_134823_via_10015_io_b20a8a502c.png)