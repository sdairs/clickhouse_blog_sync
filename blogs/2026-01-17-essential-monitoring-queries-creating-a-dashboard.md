---
title: "Essential Monitoring Queries: Creating a Dashboard in ClickHouse Cloud"
date: "2025-05-20T12:11:18.873Z"
author: "Mihir Gokhale"
category: "Product"
excerpt: "A short, easy-to-follow guide to building your own monitoring dashboard in ClickHouse Cloud. Real-time visibility. Zero setup. Just a few clicks."
---

# Essential Monitoring Queries: Creating a Dashboard in ClickHouse Cloud

Monitoring ClickHouse can feel scattered, especially when jumping between system tables and ad hoc queries. In a [previous blog post](https://clickhouse.com/blog/monitoring-troubleshooting-select-queries-clickhouse), the ClickHouse Support team provided some “essential monitoring queries” to help users monitor their ClickHouse instance using ClickHouse’s powerful system tables. In this post, we’ll turn those essential queries from our earlier blog into a centralized, reusable dashboard in ClickHouse Cloud, giving you real-time visibility in just a few clicks.

Here’s the end result of what we’ll create:

![Untitled2.gif](https://clickhouse.com/uploads/Untitled2_daa070c137.gif)

We’ll start by running a query on `system.part`s to provide a global overview of my cluster. Specifically, it shows the biggest tables in terms of rows, data and primary key size:

<pre>
<code type='click-ui' language='sql'>
SELECT
    table,
    sum(rows) AS rows,
    max(modification_time) AS latest_modification,
    formatReadableSize(sum(bytes)) AS data_size,
    formatReadableSize(sum(primary_key_bytes_in_memory)) AS primary_keys_size,
    any(engine) AS engine,
    sum(bytes) AS bytes_size
FROM clusterAllReplicas(default, system.parts)
WHERE active
GROUP BY
    database,
    table
ORDER BY bytes_size DESC
</code>
</pre>

In ClickHouse Cloud, we’ll save this query, and add it to a new dashboard - `Monitoring SELECT queries`:

![unnamed (1).png](https://clickhouse.com/uploads/unnamed_1_efc260a1d6.png)

![unnamed (2).png](https://clickhouse.com/uploads/unnamed_2_e88c2e9e9f.png)

When I navigate to the Dashboards tab, I’ll now see a brand new dashboard with a table component that I just added:

![unnamed (3).png](https://clickhouse.com/uploads/unnamed_3_62ac8852c9.png)

I’ll keep adding a few more queries from the blog post to this dashboard as tables. I’ll create my first line chart showing average query duration and number of requests, which works great as a time-series line graph in the SQL console:

![unnamed (4).png](https://clickhouse.com/uploads/unnamed_4_50b86a0016.png)

I’ll add this visualization to our dashboard. I’ll also add a legend and change the formatting of my series so hovering over the series only shows one decimal point:

![unnamed (5).png](https://clickhouse.com/uploads/unnamed_5_5c0d199cea.png)

Finally, I’ll add one more table showing which users have been running the most queries recently. I now have a dashboard which I can keep reference to monitor queries on my cluster. As a final step, I’ll use ClickHouse [Query Parameters](https://clickhouse.com/docs/sql-reference/syntax#defining-and-using-query-parameters) to add a time-based filter to my line chart so the dashboard is interactive. I’ll modify the underlying query, and save it:

![unnamed (6).png](https://clickhouse.com/uploads/unnamed_6_a99e3a5922.png)

I’ll configure a "Filter" as the value source for this filter, and keep a 3-day default:

![unnamed (7).png](https://clickhouse.com/uploads/unnamed_7_726a732d61.png)

Now, viewers of my dashboard can toggle how many days of data they see on the line graph:

![unnamed (8).png](https://clickhouse.com/uploads/unnamed_8_c76c2a1edf.png)

Here’s the final result! Each dashboard has a custom URL, so it’s easy to share this dashboard with colleagues in the same Cloud organization via the browser’s URL:

![Untitled2.gif](https://clickhouse.com/uploads/Untitled2_daa070c137.gif)

With this dashboard in place, you’ll spend less time hunting down queries you previously wrote, and more time optimizing performance. Try building your own with sample queries, or customize queries to fit your specific workload.