---
title: "Visualizing Data with ClickHouse - Part 1 - Grafana"
date: "2022-10-05T21:51:08.426Z"
author: "Dale McDiarmid"
category: "Engineering"
excerpt: "Visualizing data in ClickHouse with Grafana"
---

# Visualizing Data with ClickHouse - Part 1 - Grafana

This blog post is part of a series:
- [Visualizing Data with ClickHouse - Part 2 - Superset](https://clickhouse.com/blog/visualizing-data-with-superset)
- [Visualizing Data with ClickHouse - Part 3 - Metabase](https://clickhouse.com/blog/visualizing-data-with-metabase)

## Introduction

At ClickHouse, we are passionate about supporting our ecosystem. This includes providing users with the widest possible range of choices when it comes to visualizing data. Each part of this blog series will explore an option for visualizing your data in ClickHouse: Grafana, Superset, and Metabase. 

While each of these can be used with almost any type of data inserted into ClickHouse, they each have their respective strengths. We touch on when these might be appropriate, and each demonstrates features we find impressive. 

Often a decision on visualization tooling comes down to a specific feature set applicable to your data type or simply a personal preference of your users. While we hope this post assists in any selection process you need to make, we encourage our users to try them! All of these tools are free to use, and trivial to get started with.

This post references datasets from our "Getting Data into ClickHouse" blog series<sub><a href="https://clickhouse.com/blog/getting-data-into-clickhouse-part-1">[1]</a></sub><sub><a href="https://clickhouse.com/blog/getting-data-into-clickhouse-part-2-json">[2]</a></sub><sub><a href="https://clickhouse.com/blog/getting-data-into-clickhouse-part-3-s3">[3]</a></sub> These datasets are available in our [play.clickhouse.com](https://play.clickhouse.com/play?user=play) environment in the `blogs` database. Users should be able to reproduce all examples using the `explorer` user (no password required).

## Grafana

Since originating as a fork of Kibana in 2014, Grafana has grown to be one of the most popular visualization techniques for time series data. The code has long diverged from its Kibana roots, extending its support for datastores, adding new visualizations, and expanding beyond a simple dashboarding tool. While applicable to BI use cases, it predominately focuses on serving the Observability use case, with excellent support for dedicated views for logs and traces. 

At ClickHouse, we continue to work closely with the Grafana team to invest in the official OSS ClickHouse plugin, allowing users to visualize data in real-time effortlessly. We recently released [version 2.x of the Grafana plugin for ClickHouse](https://clickhouse.com/blog/clickhouse-grafana-plugin-2.0), which included long-awaited features like JSON and HTTP support. In our examples, we utilize [Grafana Cloud](https://grafana.com/auth/sign-in/), which provides a generous free tier more than sufficient for querying data in our [ClickHouse Cloud](https://clickhouse.cloud/signUp) service. The instructions for installing the official ClickHouse plugin can be found [here](https://clickhouse.com/docs/en/connect-a-ui/grafana-and-clickhouse). These should be identical for self-managed instances.

To connect Grafana to ClickHouse a user is simply required to create a ClickHouse Datasource - effectively an instantiation of the plugin. Users can create multiple data sources: each potentially connecting to a different ClickHouse service or possibly providing access to the same instance with different credentials. We illustrate this process below:

<a href="/uploads/grafana_1_datasource_81c6357583.gif" target="_blank">
         <img alt="grafana-1-datasource.gif" src="/uploads/grafana_1_datasource_81c6357583.gif" style="width: 100%;">
</a>

<br />
Visualizing data in Grafana requires us to create a dashboard. From here, the user can add a visualization panel and specify that this should use our ClickHouse data source.
<br /><br />

<a href="/uploads/grafana_2_create_visual_2_f2a043d353.gif" target="_blank">
         <img alt="grafana-2-create-visual-2.gif" src="/uploads/grafana_2_create_visual_2_f2a043d353.gif" style="width: 100%;">
</a>

<br />
When creating a visual, the user is required to be familiar with SQL concepts. However, a visual query builder assists with constructing ClickHouse SQL for most chart types. With Granfana focusing on time-series data, most charts require the user to define a DateTime/Date column along with a numerical value.

In the example below, we use the [hacker news dataset from an earlier post](https://clickhouse.com/blog/getting-data-into-clickhouse-part-1), to create a simple bar chart showing ClickHouse activity over time. Notice how we initially use the query builder to get started, before editing the SQL directly to capture posts per month.

<a href="/uploads/grafana_3_simple_bar_2_26cea715dd.gif" target="_blank">
         <img alt="grafana-3-simple-bar-2.gif" src="/uploads/grafana_3_simple_bar_2_26cea715dd.gif" style="width: 100%;">
</a>

<br />
<pre style='background-color: #222222; border-radius: 8px; padding: 24px; color: #FFFFFF; display: flex; position: relative; white-space: pre-wrap;'>
<div style='color: #FFFFFF; margin-top: -24px; max-width: 98%;'>
SELECT count() as `posts per month`, toStartOfMonth(time) as month FROM default.hackernews WHERE type IN ('comment', 'story') AND (text ILIKE '%ClickHouse%' OR title ILIKE '%ClickHouse%') GROUP BY month ORDER BY month LIMIT 1000
</div> <a style='height: 32px; width: 32px; text-align: center; line-height: 1.3; position: absolute; font-size: 24px; top: 24px; right: 24px; color: #FFFFFF; background: rgba(0,0,0,0.8); border-radius: 8px;' href="https://sql.clickhouse.com?query_id=JYYNJM7UWYX5RIWU7GPGTJ" target="_blank">✎</a>
</pre>
</p>

Multi-line charts, i.e., those with more than one series, require a string column in addition to the standard Date/DateTime and numeric columns. This string column thus defines the series key. Below we utilize the forex dataset from our [previous post](https://clickhouse.com/blog/getting-data-into-clickhouse-part-3-s3), to show the price of various currency pairs where the USD is the base.  Note we use a SQL query here with the filter `$__timeFilter`, which automatically injects our selected time range into the query as a filter - thus allowing us to drill down. We use the [argMax](https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/argmax/) function to get the close price each day. Finally, we use `SETTINGS max_result_rows = 10000` to allow us to get a larger dataset from [play.clickhouse.com](https://play.clickhouse.com/play?user=play).

<a href="/uploads/grafana_4_multi_line_2_e8daf9fcd9.gif" target="_blank">
         <img alt="grafana-4-multi-line-2.gif" src="/uploads/grafana_4_multi_line_2_e8daf9fcd9.gif" style="width: 100%;">
</a>

<br />
<pre style='background-color: #222222; border-radius: 8px; padding: 24px; color: #FFFFFF; display: flex; position: relative; white-space: pre-wrap;'>
<div style='color: #FFFFFF; margin-top: -24px; max-width: 98%;'>
SELECT toStartOfDay(datetime) as time, quote, argMax(bid,datetime) as close
FROM blogs.forex
WHERE (base ='EUR') AND quote IN ('GBP', 'USD', 'NZD', 'CAD') AND $__timeFilter(datetime)
GROUP BY time, quote
ORDER BY time ASC, quote ASC
SETTINGS max_result_rows=10000
</div> <a style='height: 32px; width: 32px; text-align: center; line-height: 1.3; position: absolute; font-size: 24px; top: 24px; right: 24px; color: #FFFFFF; background: rgba(0,0,0,0.8); border-radius: 8px;' href="https://sql.clickhouse.com?query_id=G5QCEZE3VY4CDVFE7MSIAE" target="_blank">✎</a>
</pre>
</p>

A little more work is required for less standard visualizations, such as heatmap and candlestick. Candlestick visualizations require a value for each time period indicating the open, close (using [argMin](https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/argmin)), low, and high values. This naturally fits our forex dataset, allowing us to visualize how prices change over time. 

<a href="/uploads/grafana_5_candle_stick_2_1ebaee5f4b.gif" target="_blank">
         <img alt="grafana-5-candle_stick-2.gif" src="/uploads/grafana_5_candle_stick_2_1ebaee5f4b.gif" style="width: 100%;">
</a>

<br />
<pre style='background-color: #222222; border-radius: 8px; padding: 24px; color: #FFFFFF; display: flex; position: relative; white-space: pre-wrap;'>
<div style='color: #FFFFFF; margin-top: -24px; max-width: 98%;'>
SELECT toStartOfDay(datetime) as day, argMin(ask, datetime) as open, argMax(ask,datetime) as close, max(ask) as high, min(ask) as low
FROM blogs.forex
WHERE (base ='EUR') AND quote ='USD' AND $__timeFilter(datetime)
GROUP BY day
ORDER BY day ASC
SETTINGS max_result_rows=10000
</div> <a style='height: 32px; width: 32px; text-align: center; line-height: 1.3; position: absolute; font-size: 24px; top: 24px; right: 24px; color: #FFFFFF; background: rgba(0,0,0,0.8); border-radius: 8px;' href="https://sql.clickhouse.com?query_id=NJPUOAHZYRPELRF6DY2XFT" target="_blank">✎</a>
</pre>
</p>

Heatmaps in Grafana require us to bucket our geo data and provide a numerical value to control the color scale. Our weather dataset, from a [previous post](https://clickhouse.com/blog/real-world-data-noaa-climate-data), provides us with a simple means to demonstrate this. We use the ClickHouse [geoHashEncode](https://clickhouse.com/docs/en/sql-reference/functions/geo/geohash/#geohashencode) function to aggregate on our [Point](https://clickhouse.com/docs/en/sql-reference/data-types/geo/#point) field, finding the max temperature recorded for each grid. These can then be plotted using the GeoMap visualization as a heatmap to show the hottest areas of the United States and Mexico. Note the geographic restriction via the polygon dictionary - a filter optimization explored [here](https://clickhouse.com/blog/real-world-data-noaa-climate-data).

<a href="/uploads/grafana_6_map_4673cb2d47.gif" target="_blank">
         <img alt="grafana-6-map.gif" src="/uploads/grafana_6_map_4673cb2d47.gif" style="width: 100%;">
</a>

<br />
<pre style='background-color: #222222; border-radius: 8px; padding: 24px; color: #FFFFFF; display: flex; position: relative; white-space: pre-wrap;'>
<div style='color: #FFFFFF; margin-top: -24px; max-width: 98%;'>
SELECT geoHash, geohashDecode(geoHash) as lon_lat, max(tempMax)/10 as max_temp
FROM blogs.noaa
WHERE date > '1970-01-01' and dictGet(blogs.country_polygons, 'name', location) IN ('United States of America', 'Mexico')
GROUP BY geohashEncode(location.1, location.2, 3) as geoHash SETTINGS max_result_rows = 100000
</div> <a style='height: 32px; width: 32px; text-align: center; line-height: 1.3; position: absolute; font-size: 24px; top: 24px; right: 24px; color: #FFFFFF; background: rgba(0,0,0,0.8); border-radius: 8px;' href="https://sql.clickhouse.com?query_id=NHQIA2R29W9QCV8QL9EPNA" target="_blank">✎</a>
</pre>
</p>

The above examples focus on datasets from our previous posts. Grafana, however, is typically used for the Observability use case. While a post dedicated to using Grafana with Observability data is justified (coming soon!), here we demonstrate the use of the [JSON log data available in play.clickhouse.com](https://sql.clickhouse.com?query_id=PT6BDKJPNWWYVOSFHJ2N9H) to build a simple view in Grafana’s log explorer. We offset this data to the last 24 hrs in order to simplify the visualization. Note we also create a level field from the status code to ensure our logs are categorized and color-coded.

<a href="/uploads/grafana_7_logs_2_666a64f353.gif" target="_blank">
         <img alt="grafana-7-logs-2.gif" src="/uploads/grafana_7_logs_2_666a64f353.gif" style="width: 100%;">
</a>

<br />
<pre style='background-color: #222222; border-radius: 8px; padding: 24px; color: #FFFFFF; display: flex; position: relative; white-space: pre-wrap;'>
<div style='color: #FFFFFF; margin-top: -24px; max-width: 98%;'>
SELECT
    now() - (toDateTime('1998-05-08 13:44:46') - timestamp) AS log_time,
    multiIf(message.status > 500, 'critical', message.status > 400, 'error', message.status > 300, 'warning', 'info') AS level,
    message.request.method AS method,
    message.status AS status,
    message.size AS size,
    message.request AS log
FROM blogs.http_logs
ORDER BY timestamp DESC
LIMIT 10000
</div> <a style='height: 32px; width: 32px; text-align: center; line-height: 1.3; position: absolute; font-size: 24px; top: 24px; right: 24px; color: #FFFFFF; background: rgba(0,0,0,0.8); border-radius: 8px;' href="https://sql.clickhouse.com?query_id=24AZ83BWSK7DYB24TDJHZD" target="_blank">✎</a>
</pre>
</p>

## Conclusion

In this post, we have shown some simple visualization techniques using the Grafana plugin. Next time we will explore Superset and its greater focus on BI use cases.

*If you’re enthusiastic about the latest technologies and are passionate about Open Source, we’re currently hiring for our [integrations team](https://clickhouse.com/company/careers) and would love to hear from you.*