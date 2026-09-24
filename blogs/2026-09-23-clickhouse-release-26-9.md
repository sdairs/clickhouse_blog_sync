---
title: "ClickHouse release 26.9"
date: "2026-09-24T11:10:17.023Z"
author: "ClickHouse"
category: "Engineering"
excerpt: "ClickHouse 26.9 introduces conditional LIMIT boundaries, incremental refreshes for append-only materialized views, disk spilling for DISTINCT, time-limited tokens, and faster min/max/count queries."
---

# ClickHouse release 26.9

September has rolled around, and ClickHouse 26.9 has arrived with another packed collection of new features.

<p>The ClickHouse 26.9 release contains 56 new features &#127809; 135 performance optimizations &#127822; and 464 bug fixes &#128063;&#65039;.</p>

This release brings conditional boundaries for `LIMIT`, incremental refreshes for append-only materialized views, and disk spilling for high-cardinality `DISTINCT` queries. 

We’ll also look at time-limited access tokens, faster `min`, `max`, and `count` queries, expanded PromQL support, and several quality-of-life improvements.

## New contributors

A special welcome to all the new contributors in 26.9\! The growth of ClickHouse's community is humbling, and we are always grateful for the contributions that have made ClickHouse so popular.

Below are the names of the new contributors:

*Aaron Harlap, Actuele AI, Alex Francoeur, Alex Prabhat Bara, AlexF, Anand Kumar Shaw, Anton Kovalenko, Aparajita Pandey, Brandon Pereira, Claude, Denys Stetsenko, Dmitrii Bezrukov, Evandro Leopoldino Gonçalves, Friedrich ten Hagen, George Viamontes, Gülçin Yıldırım Jelinek, Hamza Wasim, Hank Hoffmeier, Héctor Pablos, Itamar Tempelhof, Ivan N. Taranov, Ivan Tkachev, Ivan Tkatchev, Jithin Zachariah, Jordan Bertasso, Jords, Joshua, Juanjo, Kelly Toole, Lucas, Luis Neves, Luís Lizardo, Marat Dulin, Mike Shi, Navneet Kumar, Pablo Francisco Pérez Hidalgo, Paul Annesley, Philip Li, Pratham Nayak, Pratheesh, SamWolfberg, Sankalp Thakur, Sebastian Vercruyssse, Serhiy Bzhezytskyy, Takayuki Enomoto, Thien Phan, Vadim Ilves, XanderYoon, Yongqiang Tian, alexprabhat99, anand-tradesea, aparajita, bakhtiiartashbolotov, cuishuang, jithinzac, kasimtj, key-arg, kyungryun, linsen, maederm, mariahlynnenagy, miao tang, mosya415, ngagejason, sakshichitnis27, sleepingeight, statxc, t, tars, zhanglangning*

Hint: if you’re curious how we generate this list… [here](https://gist.github.com/gingerwizard/5a9a87a39ba93b422d8640d811e269e9).

<iframe width="768" height="432" src="https://www.youtube.com/embed/wLrTlU5LLWI?si=cKEIAtI9rm2wzHCx" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

You can also [view the slides from the presentation](https://presentations.clickhouse.com/2026-release-26.9).

## Arithmetic operations between DateTime and Time

### Contributed by Yarik Briukhovetskyi

As of ClickHouse 26.9, you can use `Time` values as offsets when adding to or subtracting from `DateTime` values. The result retains the `DateTime` value’s timezone.

Let’s have a look at some simple examples:

```sql
SELECT
    now() AS now,
    now + toTime('02:00:00'),
    toTime('04:00:00') + now,
    now64() AS now64,
    now64 - toTime('02:00:00'),
    now64 - toTime64('02:00:00.417', 3)
FORMAT Vertical;
```

```text
Row 1:
──────
now:                      2026-09-21 13:49:06
plus(now, to⋯02:00:00')): 2026-09-21 15:49:06
plus(toTime(⋯:00'), now): 2026-09-21 17:49:06
now64:                    2026-09-21 13:49:06.440
minus(now64,⋯02:00:00')): 2026-09-21 11:49:06.440
minus(now64,⋯0.417', 3)): 2026-09-21 11:49:06.023
```

If the calculation falls outside the range supported by the result type, [`date_time_overflow_behavior`](https://clickhouse.com/docs/reference/settings/formats/date-time#date_time_overflow_behavior) determines whether ClickHouse throws an exception, clamps the result to the nearest boundary, or leaves the overflow unchecked.

The maximum value that we can store in `DateTime` is `2106-02-07 06:28:15`. Let’s see what happens if we add one second to that time:

```sql
  SELECT
      toDateTime('2106-02-07 06:28:15', 'UTC')
      + toTime('00:00:01');
```

```text
┌─plus(toDateT⋯00:00:01'))─┐
│      1970-01-01 00:00:00 │
└──────────────────────────┘
```

It’s overflowed back to the minimum value of `DateTime`, which is expected as the default value of `date_time_overflow_behavior` is `ignore`.  But, maybe, we prefer to get an exception if the value overflows:

```sql
SELECT toDateTime('2106-02-07 06:28:15', 'UTC') + toTime('00:00:01')
SETTINGS date_time_overflow_behavior = 'throw';
```

```text
Received exception:
Code: 321. DB::Exception: Value 4294967296 is out of bounds of type DateTime: In scope SELECT toDateTime('2106-02-07 06:28:15', 'UTC') + toTime('00:00:01') SETTINGS date_time_overflow_behavior = 'throw'. (VALUE_IS_OUT_OF_RANGE_OF_DATA_TYPE)
```

Or, we can use `saturate`, in which case it will return the maximum value for that type:

```sql
SELECT toDateTime('2106-02-07 06:28:10', 'UTC') + toTime('00:00:10')
SETTINGS date_time_overflow_behavior = 'saturate';
```

```text
┌─plus(toDateT⋯00:00:10'))─┐
│      2106-02-07 06:28:15 │
└──────────────────────────┘
```

Finally, let’s run the timezone of the initial values and the calculated values:

```sql
SELECT
    now() AS now,
    timezoneOf(now),
    now + toTime('02:00:00') AS future,
    timezoneOf(future)
FORMAT Vertical;
```

```text
Row 1:
──────
now:                2026-09-21 14:37:21
timezoneOf(now):    Europe/London
future:             2026-09-21 16:37:21
timezoneOf(future): Europe/London
```

## PromQL private preview

### Contributed by Vitaly Baranov, Nikita Mikhaylov, Valery Petrov, Minh Vu

ClickHouse 26.9 expands PromQL support with more functions, additional Prometheus HTTP API endpoints, and direct `SELECT` queries against TimeSeries tables.

PromQL and the TimeSeries table engine are now available in private preview on ClickHouse Cloud, letting you store metrics in ClickHouse and query them from ClickStack, Grafana, clickhouse-client, or SQL.

You can learn more in the [Introducing ClickHouse's new TimeSeries engine](https://clickhouse.com/blog/introducing-promql) blog post.

## CREATE TOKEN

### Contributed by Alexey Milovidov

ClickHouse 26.9 introduces [CREATE TOKEN](https://github.com/ClickHouse/ClickHouse/pull/116957), which lets a user create a time-limited credential for applications, scripts, CI jobs, and agents without exposing or replacing their main password.

The token can be restricted to a subset of a user’s existing privileges,  reducing the impact of a leaked credential.

Let’s see how it works. First, we’ll create a small table:

```sql
CREATE TABLE ourTable
(
    id UInt8
);

INSERT INTO ourTable VALUES (1);
```

Next, let’s create a user called `alexey`:

```sql
CREATE USER alexey IDENTIFIED WITH sha256_password BY 'main-password';
GRANT SELECT, INSERT ON ourTable TO alexey;
GRANT CREATE TOKEN ON *.* TO alexey;
```

`alexey` has `SELECT` and `INSERT` power on this table, and can also create a token for himself.

Next, we’ll connect as `alexey` and create a token that lasts for 30 days and can only run `SELECT` queries against `ourTable`:

```sql
CREATE TOKEN
VALID FOR INTERVAL 30 DAY
GRANTS (SELECT ON ourTable);
```

The statement returns the generated token and its expiry:

```text
┌─token────────────────────────────┬─────────valid_until─┐
│ NXuRnBywn4HcHCIyBWC2WHT2Cfn4xQLb │ 2026-10-21 15:07:57 │
└──────────────────────────────────┴─────────────────────┘
```

ClickHouse displays the token only once, so make sure you copy it down.

We can then connect with the token and run a `SELECT` query:

```text
./clickhouse client \
--user alexey \
--password 'NXuRnBywn4HcHCIyBWC2WHT2Cfn4xQLb' \
--query "SELECT * FROM ourTable"
```

```text
1
```

That works fine, just as we expected. But what about if we try to insert into the table using our token?

```text
./clickhouse client \
--user alexey \
--password 'NXuRnBywn4HcHCIyBWC2WHT2Cfn4xQLb' \
--query "INSERT INTO ourTable VALUES (2)"
```

```text
Code: 497. DB::Exception: alexey: Not enough privileges. To execute this query, it's necessary to have the grant INSERT(id) ON db.`table`. (ACCESS_DENIED)
```

That doesn’t work as `alexey` only has `SELECT` access when authenticated using the token. 

A token never grants more privileges than the user already has, and it stops working when it expires or if the user is removed. If you don’t provide a `VALID UNTIL` or `VALID FOR`, the default lifetime is 30 minutes.

## LIMIT with boundary conditions

### Contributed by Zakhar Kravchuk and Nihal Miaji

ClickHouse 26.9 extends `LIMIT` with boundary conditions that start and stop output based on values in the ordered result stream, a capability that, to our knowledge, is not currently available in any other database.

* `AFTER` includes the row that matches its condition.  
* `UNTIL` stops before its matching row  
* You can add `ALL` to apply the boundary each time the condition matches.

Try the different combinations below to see which rows each query returns.

<iframe src="/uploads/limit_boundaries_embed_b0ba495982.html" title="How LIMIT with boundary conditions works in ClickHouse 26.9" style="width: 100%; height: 600px; border: 0;" loading="lazy"></iframe>

This functionality is particularly useful for analyzing log data, so let’s explore an Nginx dataset used in the [Compressing nginx logs 170x with column storage](https://clickhouse.com/blog/log-compression-170x) blog post.

First, let’s create a table:

```sql
CREATE TABLE nginx_logs
(
    timestamp DateTime,
    ip String,
    method LowCardinality(String),
    path String,
    status UInt16,
    response_bytes UInt64,
    referer String,
    user_agent String
)
ENGINE = MergeTree
ORDER BY (timestamp, ip, path);
```

Next, we’ll ingest the data:

```sql
INSERT INTO nginx_logs
WITH extractGroups(
    line,
    '^(\\S+) - \\S+ \\[([^\\]]+)\\] "(\\S+) (.*) [^ ]+" (\\d+) (\\d+) "([^"]*)" "(.*)"$'
) AS fields
SELECT
    assumeNotNull(parseDateTimeBestEffortOrNull(fields[2])) AS timestamp,
    fields[1] AS ip,
    fields[3] AS method,
    fields[4] AS path,
    toUInt16(fields[5]) AS status,
    toUInt64(fields[6]) AS response_bytes,
    fields[7] AS referer,
    fields[8] AS user_agent
FROM s3(
    'https://datasets-documentation.s3.eu-west-3.amazonaws.com/http_logs/nginx-66.log.gz',
    LineAsString
)
WHERE length(fields) = 8
  AND parseDateTimeBestEffortOrNull(fields[2]) IS NOT NULL;
```

Now, let’s get a quick overview of the data.

```sql
SELECT
    count() AS rows,
    min(timestamp) AS first_timestamp,
    max(timestamp) AS last_timestamp,
    countIf(status >= 500) AS server_errors
FROM nginx_logs;
```

```text
Row 1:
──────
rows:            66514081 -- 66.51 million
first_timestamp: 2019-01-24 00:00:00
last_timestamp:  2019-02-24 00:00:00
server_errors:   69857
```

The following query starts at the first \`5xx\` response and returns five requests. `AFTER` is inclusive, so the request that satisfies the condition is included.

```sql
SELECT timestamp, path, status
FROM nginx_logs
WHERE ip = '91.243.160.31'
  AND timestamp >= '2019-01-24 00:00:00'
  AND timestamp < '2019-02-03 00:00:00'
ORDER BY timestamp, ip, path, method, status, response_bytes
LIMIT 5 AFTER status >= 500;
```

```text
┌───────────timestamp─┬─path─────────────────────────────────────────────────────────┬─status─┐
│ 2019-01-24 06:54:01 │ /product/28579/57435/اجاق-گاز-صفحه-ای-داتیس-مدل-DG-503-Ultra │    500 │
│ 2019-01-24 06:54:02 │ /product/28579/57435/اجاق-گاز-صفحه-ای-داتیس-مدل-DG-503-Ultra │    500 │
│ 2019-01-24 06:54:06 │ /product/28579/57435/اجاق-گاز-صفحه-ای-داتیس-مدل-DG-503-Ultra │    500 │
│ 2019-01-24 06:54:15 │ /product/552/1168/مایکروفر-رومیزی-ال-جی-مدل-MS93SCR          │    200 │
│ 2019-01-24 06:54:16 │ /image/552/product/50x50                                     │    200 │
└─────────────────────┴──────────────────────────────────────────────────────────────┴────────┘
```

`UNTIL` is exclusive. This query starts at the first server error and stops before the first response with a status below `500`:

```sql
SELECT timestamp, path, status
FROM nginx_logs
WHERE ip = '91.243.160.31'
  AND timestamp >= '2019-01-24 00:00:00'
  AND timestamp < '2019-02-03 00:00:00'
ORDER BY timestamp, ip, path, method, status, response_bytes
LIMIT 100
    AFTER status >= 500
    UNTIL status < 500;
```

```text
┌───────────timestamp─┬─path─────────────────────────────────────────────────────────┬─status─┐
│ 2019-01-24 06:54:01 │ /product/28579/57435/اجاق-گاز-صفحه-ای-داتیس-مدل-DG-503-Ultra │    500 │
│ 2019-01-24 06:54:02 │ /product/28579/57435/اجاق-گاز-صفحه-ای-داتیس-مدل-DG-503-Ultra │    500 │
│ 2019-01-24 06:54:06 │ /product/28579/57435/اجاق-گاز-صفحه-ای-داتیس-مدل-DG-503-Ultra │    500 │
└─────────────────────┴──────────────────────────────────────────────────────────────┴────────┘
```

An `AFTER` boundary is applied only once, unless we use `ALL`, which reapplies it whenever another row matches. This query returns every server error and the next two requests after it:

```sql
SELECT timestamp, path, status
FROM nginx_logs
WHERE ip = '91.243.160.31'
  AND timestamp >= '2019-01-24 00:00:00'
  AND timestamp < '2019-02-03 00:00:00'
ORDER BY timestamp, ip, path, method, status, response_bytes
LIMIT 3 AFTER status >= 500 ALL;
```

```text
┌───────────timestamp─┬─path─────────────────────────────────────────────────────────┬─status─┐
│ 2019-01-24 06:54:01 │ /product/28579/57435/اجاق-گاز-صفحه-ای-داتیس-مدل-DG-503-Ultra │    500 │
│ 2019-01-24 06:54:02 │ /product/28579/57435/اجاق-گاز-صفحه-ای-داتیس-مدل-DG-503-Ultra │    500 │
│ 2019-01-24 06:54:06 │ /product/28579/57435/اجاق-گاز-صفحه-ای-داتیس-مدل-DG-503-Ultra │    500 │
│ 2019-01-24 06:54:15 │ /product/552/1168/مایکروفر-رومیزی-ال-جی-مدل-MS93SCR          │    200 │
│ 2019-01-24 06:54:16 │ /image/552/product/50x50                                     │    200 │
│ 2019-01-28 23:27:00 │ /product/28579/57435/اجاق-گاز-صفحه-ای-داتیس-مدل-DG-503-Ultra │    500 │
│ 2019-01-28 23:27:01 │ /product/28579/57435/اجاق-گاز-صفحه-ای-داتیس-مدل-DG-503-Ultra │    500 │
│ 2019-01-28 23:27:05 │ /product/28579/57435/اجاق-گاز-صفحه-ای-داتیس-مدل-DG-503-Ultra │    500 │
│ 2019-01-28 23:27:14 │ /product/552/1168/مایکروفر-رومیزی-ال-جی-مدل-MS93SCR          │    200 │
│ 2019-01-28 23:27:15 │ /image/552/product/50x50                                     │    200 │
│ 2019-02-02 13:43:29 │ /product/28579/57435/اجاق-گاز-صفحه-ای-داتیس-مدل-DG-503-Ultra │    500 │
│ 2019-02-02 13:43:30 │ /product/28579/57435/اجاق-گاز-صفحه-ای-داتیس-مدل-DG-503-Ultra │    500 │
│ 2019-02-02 13:43:34 │ /product/28579/57435/اجاق-گاز-صفحه-ای-داتیس-مدل-DG-503-Ultra │    500 │
│ 2019-02-02 13:43:43 │ /product/552/1168/مایکروفر-رومیزی-ال-جی-مدل-MS93SCR          │    200 │
│ 2019-02-02 13:43:44 │ /image/552/product/50x50                                     │    200 │
└─────────────────────┴──────────────────────────────────────────────────────────────┴────────┘
```

There are three separate incidents in this period, on rows 2, 7, and 12\. Within each burst, every 500 responses reapplies the three-row boundary. 

The consecutive failures therefore, extend the active window until two consecutive non-5xx requests occur after the final failure. In this example, both are successful 200 responses.

`ALL` can also reapply the starting boundary while `UNTIL` terminates each range:

```sql
SELECT timestamp, path, status
FROM nginx_logs
WHERE ip = '91.243.160.31'
  AND timestamp >= '2019-01-24 00:00:00'
  AND timestamp < '2019-02-03 00:00:00'
ORDER BY timestamp, ip, path, method, status, response_bytes
LIMIT 100
    AFTER status >= 500 ALL
    UNTIL status < 500;
```

```text
┌───────────timestamp─┬─path─────────────────────────────────────────────────────────┬─status─┐
│ 2019-01-24 06:54:01 │ /product/28579/57435/اجاق-گاز-صفحه-ای-داتیس-مدل-DG-503-Ultra │    500 │
│ 2019-01-24 06:54:02 │ /product/28579/57435/اجاق-گاز-صفحه-ای-داتیس-مدل-DG-503-Ultra │    500 │
│ 2019-01-24 06:54:06 │ /product/28579/57435/اجاق-گاز-صفحه-ای-داتیس-مدل-DG-503-Ultra │    500 │
│ 2019-01-28 23:27:00 │ /product/28579/57435/اجاق-گاز-صفحه-ای-داتیس-مدل-DG-503-Ultra │    500 │
│ 2019-01-28 23:27:01 │ /product/28579/57435/اجاق-گاز-صفحه-ای-داتیس-مدل-DG-503-Ultra │    500 │
│ 2019-01-28 23:27:05 │ /product/28579/57435/اجاق-گاز-صفحه-ای-داتیس-مدل-DG-503-Ultra │    500 │
│ 2019-02-02 13:43:29 │ /product/28579/57435/اجاق-گاز-صفحه-ای-داتیس-مدل-DG-503-Ultra │    500 │
│ 2019-02-02 13:43:30 │ /product/28579/57435/اجاق-گاز-صفحه-ای-داتیس-مدل-DG-503-Ultra │    500 │
│ 2019-02-02 13:43:34 │ /product/28579/57435/اجاق-گاز-صفحه-ای-داتیس-مدل-DG-503-Ultra │    500 │
└─────────────────────┴──────────────────────────────────────────────────────────────┴────────┘
```

Unlike the previous query, this output excludes the successful requests after each failure burst. `UNTIL` closes the range at the first non-5xx response, while `ALL` continues scanning for the next burst.

## Incremental refreshable materialized views

### Contributed by Smita Kulkarni

ClickHouse 26.9 adds `APPEND INCREMENTAL` to [refreshable materialized views](https://clickhouse.com/docs/concepts/features/materialized-views/refreshable-materialized-view). Instead of scanning the entire source table on every refresh, ClickHouse processes only the rows committed since the previous refresh.

This can be used to incrementally copy append-only data into another ClickHouse table or replicate an event stream from a MergeTree table into an Iceberg data lake.

Let’s have a look at how to use this feature with Iceberg. 

We’ll create an append-only stream of order events in ClickHouse and periodically copy them into an Iceberg table, demonstrating that each refresh processes only newly committed rows.

First, we’ll create our ClickHouse table:

```sql
CREATE TABLE order_events
(
    event_id UInt64,
    event_time DateTime,
    order_id UInt64,
    event_type LowCardinality(String),
    country LowCardinality(String),
    amount Decimal(10, 2)
)
ORDER BY (event_time, order_id, event_id)
SETTINGS
    enable_block_number_column = 1,
    enable_block_offset_column = 1,
    add_minmax_index_for_block_number_column = 1,
    add_minmax_index_for_block_offset_column = 1,
    part_minmax_index_columns = 'with_block_number_offset';
```

The block-number and block-offset columns provide the cursor that ClickHouse uses to identify rows committed after the previous refresh.

Next, we’ll enable Iceberg inserts and create an Iceberg table on my local filesystem:

```sql
SET allow_insert_into_iceberg = 1;
CREATE TABLE lake_order_events
(
    event_id UInt64,
    event_time DateTime,
    order_id UInt64,
    event_type String,
    country String,
    amount Decimal(10, 2)
)
ENGINE = IcebergLocal('lake_order_events', 'Parquet');
```

The `lake_order_events` directory contains the Iceberg metadata, manifests, and Parquet data files.

Finally, we’ll create a materialized view that will copy the newly committed events to Iceberg every hour:

```sql
CREATE MATERIALIZED VIEW order_events_to_iceberg
REFRESH EVERY 1 HOUR APPEND INCREMENTAL
TO lake_order_events
AS
SELECT event_id, event_time, order_id, event_type, country, amount
FROM order_events;
```

Time to ingest some data\!

```sql
INSERT INTO order_events VALUES
    (1, '2026-09-22 09:05:00', 1001, 'placed', 'UK',       0),
    (2, '2026-09-22 09:17:00', 1002, 'placed', 'Germany',  0),
    (3, '2026-09-22 09:20:00', 1001, 'paid',   'UK',      89.99),
    (4, '2026-09-22 09:31:00', 1002, 'paid',   'Germany', 129.00);
```

These events will be copied across to the Iceberg table when the materialized view triggers each hour, but to speed things up, we’ll trigger a refresh:

```sql
SYSTEM REFRESH VIEW order_events_to_iceberg;
SYSTEM WAIT VIEW order_events_to_iceberg;
```

And, if we query the Iceberg table:

```sql
SELECT * FROM lake_order_events;
```

```text
┌─event_id─┬─────────────────event_time─┬─order_id─┬─event_type─┬─country─┬─amount─┐
│        1 │ 2026-09-22 09:05:00.000000 │     1001 │ placed     │ UK      │      0 │
│        2 │ 2026-09-22 09:17:00.000000 │     1002 │ placed     │ Germany │      0 │
│        3 │ 2026-09-22 09:20:00.000000 │     1001 │ paid       │ UK      │  89.99 │
│        4 │ 2026-09-22 09:31:00.000000 │     1002 │ paid       │ Germany │    129 │
└──────────┴────────────────────────────┴──────────┴────────────┴─────────┴────────┘
```

All the records have made their way across. Next, let’s add some more rows to simulate changes to those orders:

```sql
INSERT INTO order_events VALUES
    (5, '2026-09-22 10:03:00', 1001, 'shipped',  'UK',        0),
    (6, '2026-09-22 10:11:00', 1002, 'refunded', 'Germany', -129.00),
    (7, '2026-09-22 10:28:00', 1003, 'placed',   'France',     0);
```

We’ll manually refresh the materialized view again and then query the Iceberg table again:

```text
┌─event_id─┬─────────────────event_time─┬─order_id─┬─event_type─┬─country─┬─amount─┐
│        1 │ 2026-09-22 09:05:00.000000 │     1001 │ placed     │ UK      │      0 │
│        2 │ 2026-09-22 09:17:00.000000 │     1002 │ placed     │ Germany │      0 │
│        3 │ 2026-09-22 09:20:00.000000 │     1001 │ paid       │ UK      │  89.99 │
│        4 │ 2026-09-22 09:31:00.000000 │     1002 │ paid       │ Germany │    129 │
│        5 │ 2026-09-22 10:03:00.000000 │     1001 │ shipped    │ UK      │      0 │
│        6 │ 2026-09-22 10:11:00.000000 │     1002 │ refunded   │ Germany │   -129 │
│        7 │ 2026-09-22 10:28:00.000000 │     1003 │ placed     │ France  │      0 │
└──────────┴────────────────────────────┴──────────┴────────────┴─────────┴────────┘
```

We can see the three new events are there. 

For an Iceberg target, ClickHouse stores the incremental cursor in the snapshot summary. The cursor and newly appended data are therefore committed as part of the same Iceberg snapshot. We can query `system.iceberg_history` to see this:

```sql
SELECT
    made_current_at, operation,
    summary['added-records'] AS added_records,
    summary['total-records'] AS total_records,
    summary['total-data-files'] AS total_data_files,
    summary['clickhouse.refresh-cursor'] != '' AS has_refresh_cursor
FROM system.iceberg_history
WHERE table = 'lake_order_events'
ORDER BY made_current_at;
```

```text
┌─────────made_current_at─┬─operation─┬─added_records─┬─total_records─┬─total_data_files─┬─has_refresh_cursor─┐
│ 2026-09-22 11:03:47.549 │ APPEND    │ 4             │ 4             │ 1                │                  1 │
│ 2026-09-22 11:04:36.247 │ APPEND    │ 3             │ 7             │ 2                │                  1 │
└─────────────────────────┴───────────┴───────────────┴───────────────┴──────────────────┴────────────────────┘
```

The first refresh added four records, while the second added only the three new events, taking the total from four to seven. We can also see that both snapshots contain a refresh cursor.

ClickHouse stores this cursor in the Iceberg snapshot alongside the newly appended data. If ClickHouse restarts, the next refresh resumes from that position instead of replaying the same events. The cursor only advances when the append succeeds, so it always stays in sync with the data.

This approach works best with append-only data, such as events, logs, audit records, and other immutable facts.

## min, max, and count from column statistics

### Contributed by Alexey Milovidov

ClickHouse stores minimum and maximum values for numeric-like columns in each data part. As of 26.9, it can use those statistics to answer min, max, and count queries without reading the underlying column data.

Let’s try it with the Nginx logs table that we used earlier. We’ll use `response_bytes` rather than `timestamp`. Since `timestamp` is the first column in the table’s sorting key, ClickHouse can already answer that query from existing metadata.

We'll prefix our query with `EXPLAIN` so that we can see the query plan:

```sql
EXPLAIN
SELECT
    min(response_bytes),
    max(response_bytes),
    count()
FROM nginx_logs;
```

```text
┌─explain──────────────────────────────────────────────────────────┐
│ Output: min(response_bytes), max(response_bytes), count()        │
│                                                                  │
│ Aggregating                                                      │
│ │  Keys:                                                         │
│ │  Aggregates: min(response_bytes), max(response_bytes), count() │
│ │  Skip merging: 0                                               │
│ └──ReadFromPreparedSource (_statistics_min_max_projection)       │
└──────────────────────────────────────────────────────────────────┘
```

If we look at the last line, we can see that instead of reading the `response_bytes` column, ClickHouse prepares the result from its column statistics.

We can disable this optimization using the setting `use_statistics_for_min_max_aggregation`, and now ClickHouse has to scan the `response_bytes` column to compute the result, as shown in the following query:

```sql
EXPLAIN
SELECT
    min(response_bytes),
    max(response_bytes),
    count()
FROM nginx_logs
SETTINGS use_statistics_for_min_max_aggregation = 0;
```

```text
┌─explain──────────────────────────────────────────────────────────┐
│ Output: min(response_bytes), max(response_bytes), count()        │
│                                                                  │
│ Aggregating                                                      │
│ │  Keys:                                                         │
│ │  Aggregates: min(response_bytes), max(response_bytes), count() │
│ │  Skip merging: 0                                               │
│ └──ReadFromMergeTree (default.nginx_logs)                        │
│       Read type: Default                                         │
│       Parts: 5 | Granules: 8122                                  │
│       Output: response_bytes                                     │
└──────────────────────────────────────────────────────────────────┘
```

## `system.session_query_ids`

### Contributed by Vladimir Cherkasov

ClickHouse 26.9 introduces a new system table, `system.session_query_ids`, which keeps track of all the query ids in the current session in execution order.

We can query that table like this:

```sql
SELECT * FROM system.session_query_ids;
```

```text
┌─sequence_number─┬─query_id─────────────────────────────┐
│               1 │ 8ebdec91-0636-44e7-9d1a-66974c2d0fe3 │
│               2 │ 471e8bef-2042-4394-9a08-3538f4ebcf85 │
│               3 │ f9757bd2-8fe3-4b14-b681-8e938a396880 │
│               4 │ 36903bb2-9f85-420b-b37b-66f0d23ce41e │
│               5 │ 4127be18-3e58-45f6-8153-5ff9a0d04675 │
│               6 │ a81309ab-3498-4ba9-9217-8145406a168d │
└─────────────────┴──────────────────────────────────────┘
```

The `system.query_log` table includes a `query_id` per entry, which means we can now check which queries we just ran, without having to manually specify query ids when querying that table:

```sql
SELECT query, query_duration_ms FROM system.query_log
WHERE query_id IN (SELECT query_id FROM system.session_query_ids)
AND type = 'QueryFinish' 
ORDER BY event_time_microseconds;
```

```text
┌─query─────────────────────────────────────────────────────────────┬─query_duration_ms─┐
│ SELECT * FROM lake_order_events;                                  │                10 │
│ system flush logs;                                                │                 0 │
│ SELECT query, query_duration_ms FROM system.query_log            ↴│                 3 │
│↳WHERE query_id IN (SELECT query_id FROM system.session_query_ids)↴│                   │
│↳  AND type = 'QueryFinish' ORDER BY event_time_microseconds;      │                   │
│ SELECT * FROM system.session_query_ids;                           │                 0 │
│ set output_format_pretty_row_numbers=0;                           │                 0 │
│ SELECT * FROM system.session_query_ids;                           │                 0 │
└───────────────────────────────────────────────────────────────────┴───────────────────┘

```

## Limits on table size and table count

### Contributed by Alexey Milovidov

ClickHouse 26.9 lets us put limits on how large an individual table can grow, as well as how many tables can be created in a database. 

This is useful for multi-tenant, temporary, and demo environments, where we don’t want one workload to consume everything.

Let’s start by creating a table that can contain a maximum of three rows:

```sql
CREATE TABLE limited_events
(
    id UInt64,
    message String
)
ENGINE = MergeTree
ORDER BY id
SETTINGS max_table_size_rows = 3;
```

We’ll insert three rows:

```sql
INSERT INTO limited_events VALUES
    (1, 'started'),
    (2, 'processing'),
    (3, 'finished');
```

If we insert one more row, it still succeeds:

```sql
INSERT INTO limited_events VALUES
    (4, 'one past limit');

SELECT count()
FROM limited_events;
```

```text
┌─count()─┐
│       4 │
└─────────┘
```

The limit is checked against the table’s current size when an `INSERT` starts. This means the `INSERT` that takes the table from three to four rows can finish. The next `INSERT` sees that the table is already over the limit and is rejected:

```sql
INSERT INTO limited_events VALUES
    (5, 'rejected');
```

```text
Code: 1016. DB::Exception: Table size limit exceeded: the total number of rows in active data parts of table default.limited_events is 4, which exceeds the 'max_table_size_rows' setting value (3). (TABLE_SIZE_LIMIT_EXCEEDED)
```

We can also limit a table by its compressed or uncompressed size using `max_table_size_bytes_compressed` and `max_table_size_bytes_uncompressed`.

We can put a limit on the number of tables in a database as well. Let’s create a database that can contain two tables:

```sql
CREATE DATABASE tenant
ENGINE = Atomic
SETTINGS max_tables = 2;
```

We can create the first two tables as usual:

```sql
CREATE TABLE tenant.events (id UInt64)
ENGINE = MergeTree
ORDER BY id;

CREATE TABLE tenant.users (id UInt64)
ENGINE = MergeTree
ORDER BY id;
```

But if we try to create a third table, ClickHouse rejects it:

```sql
CREATE TABLE tenant.audit_log (id UInt64)
ENGINE = MergeTree
ORDER BY id;
```

```text
Code: 724. DB::Exception: Too many tables in database `tenant`. The limit (database setting `max_tables`) is set to 2, the current number is 2. (TOO_MANY_TABLES)
```

## DISTINCT in external memory

### Contributed by Nihal Z. Miaji

Conceptually, `DISTINCT` needs to keep track of the values it has already seen. ClickHouse has several optimizations that reduce this work, but a high-cardinality query may still require maintaining a large in-memory set.

ClickHouse 26.9 can spill this hash set to disk, just like `GROUP BY` and `ORDER BY`, instead of allowing it to keep growing until the query runs out of memory.

Let’s see what that looks like by returning all the distinct values in a sequence of 100 million numbers, while using [`max_memory_usage`](https://clickhouse.com/docs/reference/settings/session-settings/max-memory-usage#max_memory_usage) to limit the query to 150 MB of memory:

```sql
SELECT DISTINCT number
FROM numbers_mt(100_000_000)
FORMAT `NULL`
SETTINGS max_memory_usage = 150_000_000
```

```text
Received exception:
Code: 241. DB::Exception: Query memory limit exceeded: would use 244.33 MiB (attempt to allocate chunk of 127.00 MiB), maximum: 143.05 MiB: While executing ExternalDistinctTransform. (MEMORY_LIMIT_EXCEEDED)
```

It's unable to process the query as there isn't enough memory. We can allow `DISTINCT` to spill its intermediate state to disk by setting [`max_bytes_before_external_distinct`](https://clickhouse.com/docs/reference/settings/session-settings/max-bytes#max_bytes_before_external_distinct):

```sql
SELECT DISTINCT number
FROM numbers_mt(100_000_000)
FORMAT `NULL`
SETTINGS
    max_memory_usage = 150_000_000,
    max_bytes_before_external_distinct = 25_000_000;
```

```text
0 rows in set. Elapsed: 1.676 sec. Processed 100.00 million rows, 800.00 MB (59.65 million rows/s., 477.21 MB/s.)
Peak memory usage: 105.63 MiB.
```

This time, ClickHouse starts writing the `DISTINCT` data to temporary files when it reaches around 25 MB. The whole query can use up to 150 MB, leaving enough memory to read and merge those files at the end.

There's one more interesting thing to keep in mind when using this feature. Spilling to disk reduces memory usage, but it doesn't remove the need for memory completely. ClickHouse still needs memory for buffers, the query pipeline, and merging those temporary files that it's spilled to disk.

Let's see what happens if we reduce the overall query limit to 100 MB, while keeping the spill to disk threshold at 25 MB:

```sql
SELECT DISTINCT number
FROM numbers_mt(100_000_000)
FORMAT `NULL`
SETTINGS
    max_memory_usage = 100_000_000,
    max_bytes_before_external_distinct = 25_000_000;
```

```text
Received exception:
Code: 241. DB::Exception: Query memory limit exceeded: would use 98.94 MiB (attempt to allocate chunk of 4.13 MiB), maximum: 95.37 MiB: While executing BufferingFromFileSource. (MEMORY_LIMIT_EXCEEDED)
```

The data has been spilled successfully, but ClickHouse runs out of memory while reading the temporary files back. We can tell from `BufferingFromFileSource` that the failure occurred during processing of the spilled files, rather than during the construction of the original in-memory set.

To fix that, we need to increase `max_memory_usage` back to 150MB.

> ClickHouse automatically enables external `DISTINCT` when [`max_bytes_ratio_before_external_distinct`](https://clickhouse.com/docs/reference/settings/session-settings/max-bytes#max_bytes_ratio_before_external_distinct) is set to `0.5`. This means that `DISTINCT` starts spilling when it reaches half of the memory available.

## Bracket syntax for JSON subcolumns

### Contributed by Pavel Kruglov

ClickHouse 26.9 adds bracket syntax for accessing paths in a `JSON` value. This makes it easier to write nested paths work with keys that contain characters such as dots or spaces.

Let's have a look at how this works with help from an in-memory example:

```sql
WITH '{
    "user": {"name": "Alex"},
    "release.version": "26.9",
    "first name": "Alexey",
    "tags": ["database", "analytics"]
}'::JSON AS json
SELECT
    json.user.name AS dot_notation,
    json['user']['name'] AS bracket_notation,
    json['release.version'] AS release_version,
    json['first name'] AS first_name;
```

```text
┌─dot_notation─┬─bracket_notation─┬─release_version─┬─first_name─┐
│ Alex         │ Alex             │ 26.9            │ Alexey     │
└──────────────┴──────────────────┴─────────────────┴────────────┘
```

---

## Get started today

Interested in seeing how ClickHouse works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-2268-get-started-today-sign-up&utm_blogctaid=2268)

---