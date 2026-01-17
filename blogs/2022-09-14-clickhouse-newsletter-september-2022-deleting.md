---
title: "ClickHouse Newsletter September 2022: Deleting data can make you feel better"
date: "2022-09-14T19:01:02.873Z"
author: "Christoph Wurm"
category: "Product"
excerpt: "ClickHouse Newsletter September 2022: Deleting data can make you feel better"
---

# ClickHouse Newsletter September 2022: Deleting data can make you feel better

It’s been an exciting month at ClickHouse. We’ve released Lightweight Deletes, one of the most highly anticipated ClickHouse features of 2022. And we’re getting close to publicly launching ClickHouse Cloud (sign up for early access [here](https://clickhouse.com/cloud)).

Read on about snazzy features in our ClickHouse 22.8 LTS (Long Term Support) release, a simple example of the new DELETE query, and a roundup of ClickHouse stories for the last month.

By the way, if you’re reading this on our website, did you know you can receive every monthly newsletter as an email in your inbox as well? Sign up [here](https://discover.clickhouse.com/newsletter.html).

## Upcoming Events

Mark your calendar:

**ClickHouse v22.9 Release Webinar**  
 * **_When?_** Thursday, September 22 @ 9 am PST / 6 pm CEST  
 * **_How do I join?_** Register [here](https://clickhouse.com/company/events/v22-9-release-webinar).  

**Silicon Valley ClickHouse Meetup**
 * **_What?_** Come hang out with other users and hear what PostHog, Grafana and Barracuda are doing with ClickHouse. 
 * **_Where?_** San Jose, CA
 * **_When?_** Wednesday, September 28 @ 6 pm PST
 * **_How do I join?_** Register [here.](https://www.meetup.com/clickhouse-silicon-valley-meetup-group/events/288140358/) 

**AWS re:Invent**
 * **_What?_** A number of the ClickHouse team are going to be at re:Invent! Interested in meeting up with us, maybe grabbing a beverage, and talking about ClickHouse? Let us know! 
 * **_Where?_** Las Vegas, NV
 * **_When?_** November 29 - December 3, 2022

## ClickHouse v22.8 LTS

Our new Long Term Support release is out with many new features:

1. **[DELETE query](https://clickhouse.com/docs/en/sql-reference/statements/delete/)** It’s finally here! Lightweight deletes were one of the most requested features in our [2022 roadmap](https://github.com/ClickHouse/ClickHouse/issues/32513) and we delivered it with many months to spare. Whenever you are currently using `ALTER TABLE … DELETE` you should switch to `DELETE FROM … WHERE` in almost all cases. It is much cheaper to execute, though still asynchronous (set `mutations_sync = 2` to wait for the query to complete).
2. **[Extended date ranges](https://github.com/ClickHouse/ClickHouse/pull/39425)** `Date32` and `DateTime64` now support dates from 1900 to 2299 (1925 to 2283 before). 
3. **[Parallel distributed insert from S3](https://github.com/ClickHouse/ClickHouse/pull/39107)** ClickHouse can already insert data very quickly on a single machine (typically millions of rows per second). But if you have a cluster of machines, you can now insert from S3 in parallel on all of them. Maybe even billions of rows a second are possible? Somebody should try it.
4. **[JSON logging](https://github.com/ClickHouse/ClickHouse/pull/39277)** ClickHouse can now output its logs in JSON format. This should make it easier to ingest into and query in log management software. You can also ingest into ClickHouse, of course.
5. **[Infer dates and numbers](https://github.com/ClickHouse/ClickHouse/pull/39186** When using schema inference, you can now tell ClickHouse to try to infer dates and numbers from strings.
6. **[Query parameters](https://github.com/ClickHouse/ClickHouse/pull/39906)** can now be set in interactive mode. For example, to define a parameter named `user` just use `SET param_user = alexey`.
7. **[More Pretty formats](https://github.com/ClickHouse/ClickHouse/pull/39646)** Here are 7 more, bringing the total to almost 70. I personally like `PrettyMonoBlock`, but all formats are really “pretty”.

Take a  look at the [release webinar slides](https://presentations.clickhouse.com/release_22.8/), the [recording](https://youtu.be/yob7AnaBJz0) and please upgrade - it is a Long Term Support release.

## Query of the Month: Deleting data can make you feel better

For this month, let’s keep it simple. And tongue in cheek, just a little bit.

If there is one new feature in ClickHouse 22.8 that you absolutely must try it’s the new DELETE query. Up to now, the only way to delete specific rows in ClickHouse was to use an `ALTER TABLE table DELETE WHERE cond` statement. It would asynchronously rewrite all data files containing rows matching the condition. Since data files in ClickHouse can by default be up to 150 GB this was very expensive and could lead to significant CPU and memory usage.

The new DELETE query takes a different approach. Instead of physically deleting all data immediately it only marks the specified rows as deleted using a hidden column. The data is still there, but it is transparently filtered out of queries. Effectively, all queries are executed with an additional condition `WHERE _deleted = false`. Later, as ClickHouse merges files in the background it will drop any rows marked as deleted during the merge process.

Let’s see how useful the new DELETE query can be.

Just for fun, let’s create a table with a portfolio of stablecoins (cost is cost of purchase per coin on January 1, 2022, price is the value on 26 August 2022):

```
CREATE TABLE mymoney engine = MergeTree ORDER BY coin AS
SELECT 'USDC' AS coin, 1000 AS amount, 1.0002 AS cost, 0.9999 AS price
UNION ALL SELECT 'USDT', 1000, 1.0001, 1.00
UNION ALL SELECT 'USTC', 1000, 1.00, 0.0275
```

And let’s calculate our portfolio return:

```
SELECT sum(amount * cost) cost, sum(amount * price) value,
value - cost gain_loss, 1 - value / cost pct  FROM mymoney
```

We lost 32% of our money! What happened? Turns out TerraUSD (USTC) was not such a [“stable” stablecoin after all](https://www.investopedia.com/terrausd-crash-shows-risks-of-algorithmic-stablecoins-5272010).

But no matter, the DELETE query will take care of this:

```
SET allow_experimental_lightweight_delete = 1
DELETE FROM mymoney WHERE coin = 'USTC'
```

And now our portfolio return looks much better. If only it was that simple…

## Reading Corner

What we’ve been reading:

1. [Cloudflare Blog: Log analytics using ClickHouse](https://blog.cloudflare.com/log-analytics-using-clickhouse/) Besides using ClickHouse for serving real-time HTTP and DNS analytics ([link](https://blog.cloudflare.com/http-analytics-for-6m-requests-per-second-using-clickhouse/), [link](https://blog.cloudflare.com/how-cloudflare-analyzes-1m-dns-queries-per-second/)) Cloudflare is also using ClickHouse for storing internal logs. By moving from Elasticsearch to ClickHouse, they were able to remove sampling, and provide fast querying while saving costs. 

2. [ClickHouse Plugin for Grafana - 2.0 Release](https://clickhouse.com/blog/clickhouse-grafana-plugin-2.0) Version 2.0 of our popular ClickHouse plugin for Grafana, now supports HTTP connections and the JSON data type, among other changes. Check it out! 

3. [Exploring massive, real-world data sets: 100+ Years of Weather Records in ClickHouse](https://clickhouse.com/blog/real-world-data-noaa-climate-data) What loading more than a century of weather data into ClickHouse looks like and how you can use it. 
4. [Getting Data Into ClickHouse - Part 1](https://clickhouse.com/blog/getting-data-into-clickhouse-part-1) and [Part 2](https://clickhouse.com/blog/getting-data-into-clickhouse-part-2-json) A walkthrough of getting Hacker News data into ClickHouse and running some fun queries on it. 
5. [MySQL CDC to Clickhouse using Decodable's Change Stream Capabilities](https://youtu.be/Nvy1HWB1mT0) Decodable shows in this video how to synchronize data from MySQL to ClickHouse. 
6. [New ClickHouse Adopters](https://clickhouse.com/docs/en/introduction/adopters/):  A fun addition this month, welcome Nintendo emulator [Dolphin](https://twitter.com/delroth_/status/1567300096160665601). Also welcome to open source ad blocker [AdGuard](https://adguard.com/en/blog/adguard-dns-2-0-goes-open-source.html) and non-profit project [OONI](https://twitter.com/OpenObservatory/status/1558014810746265600?s=20&t=hvcDU-LIrgCApP0rZCzuoA). Get yourself added as well!

Thanks for reading. We’ll see you next month!

The ClickHouse Team