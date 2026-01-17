---
title: "Essential Monitoring Queries - part 2 - SELECT Queries"
date: "2023-01-03T12:09:43.012Z"
author: "Camilo Sierra"
category: "Engineering"
excerpt: "Read about how to monitor and troubleshoot your SELECT queries in the second blog of this series from our support team"
---

# Essential Monitoring Queries - part 2 - SELECT Queries

![select-query-monitoring.png](https://clickhouse.com/uploads/large_select_query_monitoring_c3052d5747.png)

## Introduction

This blog post continues our series on monitoring ClickHouse. While in the [previous post](https://clickhouse.com/blog/monitoring-troubleshooting-insert-queries-clickhouse) in this series, we focused on INSERT queries, users are also interested in troubleshooting and understanding the behavior and performance of their SELECT queries. This post will provide you with queries that will help you better understand how your service is behaving, and how to improve the performance of your SELECT queries.

While the examples in this blog post assume you are using a ClickHouse Cloud instance, they can be easily modified to work on self-managed clusters. In most cases, this means modifying the FROM clause to use the table name instead of the function [`clusterAllReplicas`](https://clickhouse.com/docs/en/sql-reference/table-functions/cluster/). Alternatively, you can spin up a service in [ClickHouse Cloud](https://clickhouse.com/cloud) on a free trial in minutes, let us deal with the infrastructure and get you querying! 


## Monitoring SELECT queries

The SQL queries in this post fall into two main categories:

1. **Monitoring** - Used for understanding the ClickHouse cluster setup and usage
2. **Troubleshooting** - Required when identifying the root cause of an issue 

Let's run through a quick overview of the query topics you will see on this blog post.

<table>

 <tr>
<th>Topic</th>
<th>Summary</th>
</tr>

<tr>
<td>Global overview of your cluster</td>
<td>Useful mainly for <strong>Troubleshooting</strong>. Review how much data you have and the primary key size. These metrics are great to understand how you are using ClickHouse but can also be worth <strong>Monitoring</strong>.</td>
</tr>

<tr>
<td>Most expensive SELECT queries</td>
<td><strong>Troubleshooting</strong>. Review what are your most expensive queries to prioritise tuning efforts.</td>
</tr>

<tr>
<td>Compare metrics from two queries</td>
<td><strong>Troubleshooting</strong> and <strong>Monitoring</strong>. Use this query to iteratively improve a specific query, by comparing your original query to a new version.</td>
</tr>

<tr>
<td>SELECT query deep dive</td>
<td><strong>Troubleshooting</strong> by reviewing what ClickHouse is doing during each execution.</td>
</tr>

<tr>
<td>Average query duration and number of requests</td>
<td><strong>Monitoring</strong>. The data by table, or as an overview of your ClickHouse service is a great way to understand changes on the query or service performance. Great to define trend usage.</td>
</tr>

<tr>
<td>Number of SQL queries by client or user</td>
<td><strong>Monitoring</strong>. Provide reports about the usage of each client or user.</td>
</tr>

<tr>
<td>TOO_MANY_SIMULTANEOUS_QUERIES</td>
<td><strong>Troubleshooting</strong> and <strong>Monitoring</strong>. Useful for identifying long running or “stuck” queries when under high load. A second query assists with <strong>Troubleshooting</strong> by returning the errors and stack traces produced by failed queries.

</td>
</tr>

</table>

## Global overview of your cluster

The following query provides an overview of your service. Specifically, what are the biggest tables in terms of rows, data and primary key size. We can also see when each table was last modified:

<pre style='background-color: #222222; border-radius: 8px; padding: 24px; color: #FFFFFF; display: flex; position: relative; white-space: pre-wrap;'>
<div style='color: #FFFFFF; margin-top: -24px; max-width: 98%;'>
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
</div>
</pre>
<br />

![cluster-overview.png](https://clickhouse.com/uploads/cluster_overview_c04845cf4a.png)

## Most expensive SELECT queries

We next want to identify the most expensive queries in our ClickHouse service. The query below returns historical queries ordered by their duration, allowing us to see which ones need our attention.

We have a large number of columns that will allow us to better understand the reasons why each query was slow. This includes:

1. Columns allowing us to understand the query type and its timing.
2. The size and the amount of rows that have been read by the service to provide the result.
3. The number of rows returned in the result.
4. Any exceptions which have occurred including the stack trace.
5. The requesting user.
6. The format, functions, dictionaries and settings used.

<pre style='background-color: #222222; border-radius: 8px; padding: 24px; color: #FFFFFF; display: flex; position: relative; white-space: pre-wrap;'>
<div style='color: #FFFFFF; margin-top: -24px; max-width: 98%;'>
SELECT
    type,
    query_start_time,
    formatReadableTimeDelta(query_duration_ms) AS query_duration,
    query_id,
    query_kind,
    is_initial_query,
    query,
    concat(toString(read_rows), ' rows / ', formatReadableSize(read_bytes)) AS read,
    concat(toString(result_rows), ' rows / ', formatReadableSize(result_bytes)) AS result,
    formatReadableSize(memory_usage) AS `memory usage`,
    exception,
    concat('\n', stack_trace) AS stack_trace,
    user,
    initial_user,
    multiIf(empty(client_name), http_user_agent, concat(client_name, ' ', toString(client_version_major), '.', toString(client_version_minor), '.', toString(client_version_patch))) AS client,
    client_hostname,
    databases,
    tables,
    columns,
    used_aggregate_functions,
    used_dictionaries,
    used_formats,
    used_functions,
    used_table_functions,
    ProfileEvents.Names,
    ProfileEvents.Values,
    Settings.Names,
    Settings.Values
FROM system.query_log
WHERE (type != 'QueryStart') AND (query_kind = 'Select') AND (event_date >= (today() - 1)) AND (event_time >= (now() - toIntervalDay(1)))
ORDER BY query_duration_ms DESC
LIMIT 10
</div>
</pre>
<br />

![most-expensive-selects.png](https://clickhouse.com/uploads/most_expensive_selects_f5141df105.png)

## Compare metrics between two queries

Let's imagine that you have identified an expensive SELECT that you wish to improve from the previous query results. For this, you can compare metrics between versions of the query using their respective ids. This information is returned if you are using the `clickhouse-client`.

<pre style='background-color: #222222; border-radius: 8px; padding: 24px; color: #FFFFFF; display: flex; position: relative; white-space: pre-wrap;'>
<div style='color: #FFFFFF; margin-top: -24px; max-width: 98%;'>
clickhouse-client --host play.clickhouse.com --user play --secure
ClickHouse client version 22.13.1.160 (official build).
Connecting to play.clickhouse.com:9440 as user play.
Connected to ClickHouse server version 22.13.1 revision 54461.

play-eu :) SELECT 1

SELECT 1

Query id: 13f75255-edec-44b2-b63b-affa9d345f0f

┌─1─┐
│ 1 │
└───┘

1 row in set. Elapsed: 0.002 sec.
</div>
</pre>
<br />

However, we appreciate this information might not always be available through other clients or applications. Assuming the response to the earlier section has provided you with your baseline id, execute the next iteration of your query and collect the id with the following:

<pre style='background-color: #222222; border-radius: 8px; padding: 24px; color: #FFFFFF; display: flex; position: relative; white-space: pre-wrap;'>
<div style='color: #FFFFFF; margin-top: -24px; max-width: 98%;'>
SELECT
    query_id,
    query,
    formatReadableTimeDelta(query_duration_ms) AS query_duration
FROM clusterAllReplicas(default, system.query_log)
WHERE (type != 'QueryStart') AND (query_kind = 'Select') AND (event_time >= (now() - toIntervalHour(1)))
ORDER BY event_time DESC
LIMIT 10
</div>
</pre>
<br />

If you are unable to identify the query e.g. due to high load, add a filter for the table or query  column using the `ILIKE` function.

Once you have the two `query_id` values, you can run the following query to compare both executions.

<pre style='background-color: #222222; border-radius: 8px; padding: 24px; color: #FFFFFF; display: flex; position: relative; white-space: pre-wrap;'>
<div style='color: #FFFFFF; margin-top: -24px; max-width: 98%;'>
WITH
    query_id = '...query_id_old_version...' AS first,
    query_id = '...query_id_new_version...' AS second
SELECT
    PE.Names AS metric,
    anyIf(PE.Values, first) AS v1,
    anyIf(PE.Values, second) AS v2
FROM clusterAllReplicas(default, system.query_log)
ARRAY JOIN ProfileEvents AS PE
WHERE (first OR second) AND (event_date = today()) AND (type = 2)
GROUP BY metric
HAVING v1 != v2
ORDER BY
    (v2 - v1) / (v1 + v2) ASC,
    v2 ASC,
    metric ASC
</div>
</pre>
<br />

![compare-metrics.png](https://clickhouse.com/uploads/compare_metrics_e6a45b5f2f.png)

In general you should be looking for large differences in any metric. You can see the description of these metrics [here](https://github.com/ClickHouse/ClickHouse/blob/17c557648e4f01f2b5919952e2263db1cff4a52e/src/Common/ProfileEvents.cpp#L7). If you have any doubt or question as to the cause of difference, please open an issue with the [ClickHouse Support](https://clickhouse.cloud/support) team.

### SELECT query deep dive

It’s also possible that you have only one version of your query and you need to improve. Suppose your goal is to understand what ClickHouse is doing behind the scenes with the objective of making the query faster. For this, you will need to use ClickHouse Client. No worries if you don't have one installed, in less than two minutes we will have one running.

If you do not have an installation of the ClickHouse Client you have two options:

1. Download the executable and start the client from your terminal

<pre style='background-color: #222222; border-radius: 8px; padding: 24px; color: #FFFFFF; display: flex; position: relative; white-space: pre-wrap;'>
<div style='color: #FFFFFF; margin-top: -24px; max-width: 98%;'>
curl https://clickhouse.com/ | sh

./clickhouse client --host xx.aws.clickhouse.cloud --secure --user default --password your-password 
</div>
</pre>
<br />

2. Alternatively, you can also use docker containers to start a clickhouse-client and connect to ClickHouse cloud: 

<pre style='background-color: #222222; border-radius: 8px; padding: 24px; color: #FFFFFF; display: flex; position: relative; white-space: pre-wrap;'>
<div style='color: #FFFFFF; margin-top: -24px; max-width: 98%;'>
docker run -it --entrypoint clickhouse-client clickhouse/clickhouse-server --host xx.aws.clickhouse.cloud --secure –user default --password your-password
</div>
</pre>
<br />


This latter command benefits from making it trivial to test different client versions if required e.g.

<pre style='background-color: #222222; border-radius: 8px; padding: 24px; color: #FFFFFF; display: flex; position: relative; white-space: pre-wrap;'>
<div style='color: #FFFFFF; margin-top: -24px; max-width: 98%;'>
docker run -it --entrypoint clickhouse-client clickhouse/clickhouse-server:22.12 --host xx.aws.clickhouse.cloud --secure –user default --password your-password
</div>
</pre>
<br />

From the client terminal first set the log level to `trace` level :

<pre style='background-color: #222222; border-radius: 8px; padding: 24px; color: #FFFFFF; display: flex; position: relative; white-space: pre-wrap;'>
<div style='color: #FFFFFF; margin-top: -24px; max-width: 98%;'>
SET send_logs_level = 'trace'
</div>
</pre>
<br />

Running the query you wish to improve will cause a detailed log to be displayed in the `clickhouse-client` shell. 

Using the [UK house price dataset](https://clickhouse.com/docs/en/getting-started/example-datasets/uk-price-paid/), we will utilize the following query as an example to show the value of the contents of this log. 

<pre style='background-color: #222222; border-radius: 8px; padding: 24px; color: #FFFFFF; display: flex; position: relative; white-space: pre-wrap;'>
<div style='color: #FFFFFF; margin-top: -24px; max-width: 98%;'>
SELECT
  county,
  price
FROM uk_price_paid
WHERE town = 'LONDON'
ORDER BY price DESC
LIMIT 3

Query id: 31bc412a-411d-4717-95c1-97ac0b5e22ff

┌─county─────────┬─────price─┐
│ GREATER LONDON │ 594300000 │
│ GREATER LONDON │ 569200000 │
│ GREATER LONDON │ 523000000 │
└────────────────┴───────────┘

3 rows in set. Elapsed: 1.206 sec. Processed 27.84 million rows, 44.74 MB (23.08 million rows/s., 37.09 MB/s.)
</div>
</pre>
<br />

This query is already very fast but let's suppose we add some projections to accelerate it further. 

We can add a projection with new primary keys in order to drastically limit the amount of data ClickHouse needs to read from disk. This process is explained in detail in the recent blog post [Super charging your ClickHouse queries](https://clickhouse.com/blog/clickhouse-faster-queries-with-projections-and-primary-indexes).

<pre style='background-color: #222222; border-radius: 8px; padding: 24px; color: #FFFFFF; display: flex; position: relative; white-space: pre-wrap;'>
<div style='color: #FFFFFF; margin-top: -24px; max-width: 98%;'>
ALTER TABLE uk_price_paid
    ADD PROJECTION uk_price_paid_projection
    (
        SELECT *
        ORDER BY
            town,
            price
    )
    
ALTER TABLE uk_price_paid MATERIALIZE PROJECTION uk_price_paid_projection

SELECT
  county,
  price
FROM uk_price_paid
WHERE town = 'LONDON'
ORDER BY price DESC
LIMIT 3

Query id: f5931796-62d1-4577-9a80-dbaf21a43049

┌─county─────────┬─────price─┐
│ GREATER LONDON │ 594300000 │
│ GREATER LONDON │ 569200000 │
│ GREATER LONDON │ 448500000 │
└────────────────┴───────────┘

3 rows in set. Elapsed: 0.028 sec. Processed 2.18 million rows, 13.09 MB (78.30 million rows/s., 470.20 MB/s.)
</div>
</pre>
<br />

We can immediately see this query reads fewer rows and is considerably faster. We can also compare some metrics provided by the logs from the execution before and after the projection:

<table>

 <tr>
<th>Original query</th>
<th>Query with projection</th>
</tr>

<tr>
<td>Selected 6/6 parts by partition key, 6 parts by primary key, <strong style="color: #fbb200;">3401/3401 marks by primary key, 3401 marks to read from 6 ranges</strong></td>
<td>Selected 6/6 parts by partition key, 6 parts by primary key, <strong style="color: #fbb200;">266/3401 marks by primary key, 266 marks to read from 6 ranges</strong></td>
</tr>

<tr>
<td>Reading approx. <strong style="color: #fbb200;">27837192</strong> rows with 2 streams</td>
<td>Reading approx. <strong style="color: #fbb200;">2179072</strong> rows with 2 streams</td>
</tr>

<tr>
<td><strong style="color: #fbb200;">Read 27837192 rows, 42.67 MiB in 1.205915216 sec.</strong>, 23083871 rows/sec., 35.38 MiB/sec.</td>
<td><strong style="color: #fbb200;">Read 2179072 rows, 12.48 MiB in 0.027350854 sec.</strong>, 79671077 rows/sec., 456.28 MiB/sec.</td>
</tr>

<tr>
<td>MemoryTracker: <strong style="color: #fbb200;">Peak memory usage (for query): 73.20 MiB.</strong></td>
<td>MemoryTracker: <strong style="color: #fbb200;">Peak memory usage (for query): 1.73 MiB.</strong></td>
</tr>

<tr>
<td><Debug> TCPHandler: <strong style="color: #fbb200;">Processed in 1.209767078 sec.</strong></td>
<td><Debug> TCPHandler: <strong style="color: #fbb200;">Processed in 0.028087551 sec.</strong></td>
</tr>
</table>

As you can see the logs provided by `send_logs_level` are really useful to better understand what ClickHouse is doing and the improvements your changes provide for each query.

In the logs we can also see debug messages like this one:

<pre style='background-color: #222222; border-radius: 8px; padding: 24px; color: #FFFFFF; display: flex; position: relative; white-space: pre-wrap;'>
<div style='color: #FFFFFF; margin-top: -24px; max-width: 98%;'>
Used generic exclusion search over index for part 202211_719_719_0 with 1 steps
</div>
</pre>
<br />

As mentioned in our [documentation](https://clickhouse.com/docs/en/guides/improving-query-performance/sparse-primary-indexes/sparse-primary-indexes-multiple/#generic-exclusion-search-algorithm), the generic exclusion search algorithm is used when a query is filtering on a column that is part of a compound key, but is not the first key column is most effective when the predecessor key column has low(er) cardinality.

Again if you have any message that you don’t understand, do not hesitate to contact [ClickHouse Support](https://clickhouse.cloud/support).

## Average query duration and number of requests

It’s important to understand how many concurrent select queries a ClickHouse service is handling and for how long on average these requests are taking to be processed. This data is also great for troubleshooting, as you can see if the number of requests has had a negative impact on the response time. While for our example we count the requests across all databases and tables, this query could easily be modified to filter for one or more specific tables or databases. 

The following query is also great as a time-series visualization in SQL console. 

<pre style='background-color: #222222; border-radius: 8px; padding: 24px; color: #FFFFFF; display: flex; position: relative; white-space: pre-wrap;'>
<div style='color: #FFFFFF; margin-top: -24px; max-width: 98%;'>
SELECT
    toStartOfHour(event_time) AS event_time_h,
    count() AS count_m,
    avg(query_duration_ms) AS avg_duration
FROM clusterAllReplicas(default, system.query_log)
WHERE (query_kind = 'Select') AND (type != 'QueryStart') AND (event_time > (now() - toIntervalDay(3)))
GROUP BY event_time_h
ORDER BY event_time_h ASC
</div>
</pre>
<br />

![average_select_query_duration.png](https://clickhouse.com/uploads/average_select_query_duration_d67fe5ffae.png)

Note: `avg_duration` is in milliseconds

## Number of SQL queries by client or user

While we have seen how the total number of queries, and their duration, can be visualized across all clients, you will often need to identify hot spots from a specific user or client. In this case, performing a similar query with grouping by the client name is useful. The query below aggregates the last 10 minutes and groups by `client_name`. Feel free to adapt it if you need a larger overview of the same data.

<pre style='background-color: #222222; border-radius: 8px; padding: 24px; color: #FFFFFF; display: flex; position: relative; white-space: pre-wrap;'>
<div style='color: #FFFFFF; margin-top: -24px; max-width: 98%;'>
SELECT
    toStartOfMinute(event_time) AS event_time_m,
    if(empty(client_name), 'unknow_or_http', client_name) AS client_name,
    count(),
    query_kind
FROM clusterAllReplicas(default, system.query_log)
WHERE (type = 'QueryStart') AND (event_time > (now() - toIntervalMinute(10))) AND (query_kind = 'Select')
GROUP BY
    event_time_m,
    client_name,
    query_kind
ORDER BY
    event_time_m DESC,
    count() ASC
LIMIT 100
</div>
</pre>
<br />

![queries-by-client.png](https://clickhouse.com/uploads/queries_by_client_8b3113d890.png)

This query can also be adapted to show the top queries by user, by modifying the GROUP BY to use the `user` column instead of the `client_name`.

## Troubleshooting <code style="color: white;">TOO_MANY_SIMULTANEOUS_QUERIES</code>

This error can happen when you are handling a very large number of concurrent SELECT queries. The settings `max_concurrent_queries` and the more specific `max_concurrent_select_queries` can help you to fine-tune when this error is triggered. If this error does occur, it is important to establish that no queries are “stuck”. The results of the query below show an `elapsed` column formatted with the `formatReadableTimeDelta` function, which can be easily used to see if any of the queries are stuck.

<pre style='background-color: #222222; border-radius: 8px; padding: 24px; color: #FFFFFF; display: flex; position: relative; white-space: pre-wrap;'>
<div style='color: #FFFFFF; margin-top: -24px; max-width: 98%;'>
SELECT
    formatReadableTimeDelta(elapsed) AS time_delta,
    *
FROM clusterAllReplicas(default, system.processes)
WHERE query ILIKE 'SELECT%'
ORDER BY time_delta DESC
</div>
</pre>
<br />

![TOO_MANY_SIMULTANEOUS_QUERIES.png](https://clickhouse.com/uploads/TOO_MANY_SIMULTANEOUS_QUERIES_ea790eddd2.png)

While all of the queries in my cluster have completed in less than a second, this should be reviewed carefully if your ClickHouse service has a large and heavy number of SELECT queries.

If you identified queries that are stuck or failed in the previous query, you can review the `system.stack_trace` table to get more details on the cause with a full stack trace. This information is useful for troubleshooting.

<pre style='background-color: #222222; border-radius: 8px; padding: 24px; color: #FFFFFF; display: flex; position: relative; white-space: pre-wrap;'>
<div style='color: #FFFFFF; margin-top: -24px; max-width: 98%;'>
SELECT
    thread_id,
    query_id,
    arrayStringConcat(arrayMap((x, y) -> concat(x, ': ', y), arrayMap(x -> addressToLine(x), trace), arrayMap(x -> demangle(addressToSymbol(x)), trace)), '\n') AS n_trace
FROM clusterAllReplicas(default, system.stack_trace)
WHERE query_id IS NOT NULL
SETTINGS allow_introspection_functions = 1
</div>
</pre>
<br />

![query_stack_trace.png](https://clickhouse.com/uploads/query_stack_trace_d34db7cc9b.png)

When using the ClickHouse SQL-console, you can double click on each cell to get the full context via an inspector.

## Conclusion

In this blog post, we have reviewed different ways to troubleshoot and understand how SELECT queries are behaving in ClickHouse as well as providing the methods to help you to review your improvements and changes. We recommend proactively monitoring the results of these queries and alerting if the behavior is usual, potentially using tools such as Grafana, which has a mature ClickHouse integration and supports alerting. In the next post from this series, we will review queries to monitor and troubleshoot a distributed ClickHouse deployment.