---
title: "Using TTL to Manage Data Lifecycles in ClickHouse"
date: "2023-01-31T16:12:43.876Z"
author: "Denys Golotiuk"
category: "Engineering"
excerpt: "Master the art of data lifecycle management in ClickHouse with our comprehensive guide. Enhance your ClickHouse skills and learn to maximize data efficiency."
---

# Using TTL to Manage Data Lifecycles in ClickHouse

![Data Lifecycles.png](https://clickhouse.com/uploads/Data_Lifecycles_bea551354f.png)

## Introduction

If the data that you are analyzing in ClickHouse grows over time you may want to plan to move, remove, or summarize older data on a schedule. Typically, your options here will depend on your data retention requirements and whether query SLAs vary depending on the data age. For example, while storing all dimensions at the highest available granularity on the latest data is usually required, it might be optional to store historical data with a lower level of detail.

Managing the data lifecycle can help optimize storage as well as improve query performance. ClickHouse has a simple but powerful data lifecycle management tool configured with the [`TTL`](https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/mergetree#table_engine-mergetree-ttl) clause of DDL statements.

In this blog post, we explore the `TTL` clause and how this can be used to solve a number of data management tasks.

## Automatically delete expired data

Sometimes, it no longer makes sense to store older data and it can be removed from ClickHouse. This is usually called a retention policy. Data removal is done automatically in the background based on conditions in a `TTL` statement.

Suppose we have the `events` table, and we would like to delete all records older than one month:

```sql
CREATE TABLE events
(
    `event` String,
    `time` DateTime,
    `value` UInt64
)
ENGINE = MergeTree
ORDER BY (event, time)
TTL time + INTERVAL 1 MONTH DELETE
```

We add the `TTL` statement and use the `DELETE` operation with `time + INTERVAL 1 MONTH`. This will remove a record when its `time` column value is more than one month in the past.

**Note** that records removal is an asynchronous background process, and outdated records can still be available for some time.

Let's try to insert a couple of records, including an outdated one, into the table:

```sql
INSERT INTO events VALUES('error', now() - interval 2 month, 123), ('error', now(), 123);
```

We'll find both records available in the table right after insert:

```sql
SELECT * FROM events

┌─event─┬────────────────time─┬─value─┐
│ error │ 2022-11-24 09:34:44 │   123 │
│ error │ 2023-01-24 09:34:44 │   123 │
└───────┴─────────────────────┴───────┘
```

The outdated record will be removed in the background by an "off-schedule" merge which is scheduled periodically. Sometime later:

```sql
SELECT * FROM events
┌─event─┬────────────────time─┬─value─┐
│ error │ 2023-01-24 09:34:44 │   123 │
└───────┴─────────────────────┴───────┘
```

### Managing background removal

Background removal happens every 4 hours by default and can be controlled using the [`merge_with_ttl_timeout`](https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/mergetree/#merge_with_ttl_timeout) table settings option:

```sql
CREATE TABLE events
...
TTL time + INTERVAL 1 MONTH DELETE
SETTINGS merge_with_ttl_timeout = 1200
```

Do not use values smaller than 300 seconds for this setting, as this can create I/O overhead and impact cluster performance. After some time, we can find that the outdated record no longer exists in our table:

```sql
SELECT * FROM events

┌─event─┬────────────────time─┬─value─┐
│ error │ 2023-01-24 09:34:44 │   123 │
└───────┴─────────────────────┴───────┘
```


### Filter which rows to delete

Let's assume we would like to delete only a specific type of record (e.g., where an `event` column value is `error`). We can additionally specify this in the `WHERE` clause of the `TTL` statement:

```sql
CREATE TABLE events
(
    `event` String,
    `time` DateTime,
    `value` UInt64
)
ENGINE = MergeTree
ORDER BY (event, time)
TTL time + INTERVAL 1 MONTH DELETE WHERE event = 'error'
```

Now, only outdated rows with the `event='error'` value will be removed:

```sql
INSERT INTO events VALUES('not_error', now() - interval 2 month, 123), ('error', now(), 123)
```

We can be sure the `not_error` record will not be removed (though it's older than one month):

```sql
SELECT * FROM events

┌─event─────┬────────────────time─┬─value─┐
│ error     │ 2023-01-24 09:48:05 │   123 │
│ not_error │ 2022-11-24 09:48:05 │   123 │
└───────────┴─────────────────────┴───────┘
```

### Multiple delete conditions

ClickHouse allows specifying multiple TTL statements. This allows us to be more flexible and specific about what to remove and when. Let's say we want to remove all non `error` events in 1 month and all errors after 6 months:

```sql
CREATE TABLE events
(
    `event` String,
    `time` DateTime,
    `value` UInt64
)
ENGINE = MergeTree
ORDER BY (event, time)
TTL time + INTERVAL 1 MONTH DELETE WHERE event != 'error',
    time + INTERVAL 6 MONTH DELETE WHERE event = 'error'
```

We can have any number of rules configured for the `TTL` statement.

### Move data to historical tables

We can use [Materialized Views](https://clickhouse.com/blog/using-materialized-views-in-clickhouse) in combination with a `TTL` statement to address cases where we might want to move outdated data to another table before being removed from the main table.

Suppose we want to move `error` events to the table  `errors_history` before removing them from the `events` table. First, we create a target table for a materialized view, which is of the same structure as the `events` table:

```sql
CREATE TABLE errors_history (
    `event` String,
    `time` DateTime,
    `value` UInt64
)
ENGINE = MergeTree
ORDER BY (event, time)
```

**Note** that we can't use `CREATE TABLE errors_history AS events` as this will also copy the TTL expression, which we don't want to happen. Then we create the materialized view trigger to ingest data automatically into the `errors_history` table:


```sql
CREATE MATERIALIZED VIEW errors_history_mv TO errors_history AS
SELECT * FROM events WHERE event = 'error'
```

Now, when we insert data into the `events` table, `error` events are automatically inserted into the `errors_history` table as well. On the other hand, when the `TTL` procedure removes records from the `events` table, they remain in the `errors_history` table.

## Compacting historical data using aggregations

In many cases, we don't want to delete the data, but we can afford to reduce its level of detail in order to save resources. For example, let's consider a situation when we don't want to remove `error` events from our table. At the same time, we might not need the per-second details after one month, so we can leave daily aggregated numbers.

This can be implemented using a `GROUP BY ... SET` clause of the `TTL` statement:

```sql
CREATE TABLE events
(
    `event` String,
    `time` DateTime,
    `value` UInt64
)
ENGINE = MergeTree
ORDER BY (toDate(time), event)
TTL time + INTERVAL 1 MONTH GROUP BY toDate(time), event SET value = SUM(value)
```

Several important points here:
* The `GROUP BY toDate(time), event` expression should be a prefix of the [primary key](https://clickhouse.com/docs/en/guides/improving-query-performance/sparse-primary-indexes/sparse-primary-indexes-design), so we also changed `ORDER BY (toDate(time), event)`.
* The `SET value = SUM(value)` clause will set the `value` column to the sum of all values in each group (usual behavior for the `GROUP BY` clauses in queries).
* The `time` column value will be chosen randomly during grouping (as in the case of using [`any()` aggregate function](https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/any/)).

Let's ensure the following data is inserted:

```sql
INSERT INTO events VALUES('error', now() - interval 2 month, 123),
                         ('error', now() - interval 2 month, 321);
```

After some time, when background merge happens, we can see our data is aggregated:

```sql
SELECT * FROM events
```
```results
┌─event─┬────────────────time─┬─value─┐
│ error │ 2022-11-24 12:36:23 │   444 │
└───────┴─────────────────────┴───────┘
```

## Changing compression

While it may not be feasible to remove or aggregate data, you may have more relaxed query SLAs for your historical data. To address this, we can consider using higher compression levels for older data to save more space. For example, we can ask ClickHouse to use [`LZ4HC`](https://clickhouse.com/docs/en/sql-reference/statements/create/table/#lz4hc) compression of the higher level for the data older than one month. We need to use the `RECOMPRESS` clause for this:

```sql
CREATE TABLE events
(
    `event` String,
    `time` DateTime,
    `value` UInt64
)
ENGINE = MergeTree
ORDER BY (toDate(time), event)
TTL time + INTERVAL 1 MONTH RECOMPRESS CODEC(LZ4HC(10))
```

Note that recompressed data will take less space but will also take more time to compress, thus impacting insertion times.

## Column-level TTL

We can also manage the lifecycle of a single column using `TTL`. Suppose we have a `debug` column in our table that stores additional debug information (e.g., errors backtrace). This column is only useful for one week, during which it consumes a lot of space. We can ask ClickHouse to reset it to the default value after a week:

```sql
CREATE TABLE events
(
    `event` String,
    `time` DateTime,
    `value` UInt64,
    `debug` String TTL time + INTERVAL 1 WEEK
)
ENGINE = MergeTree
ORDER BY (event, time)
```

Now let's insert an outdated record with a `debug` column value:

```sql
INSERT INTO events VALUES('error', now() - interval 1 month, 45, 'a lot of details');
```

ClickHouse will reset this `debug` column value to an empty string once the TTL processing is completed:

```sql
SELECT * FROM events

┌─event─┬────────────────time─┬─value─┬─debug─┐
│ error │ 2022-12-24 15:13:54 │    45 │       │
└───────┴─────────────────────┴───────┴───────┘
```

Note that ClickHouse will use the default value for the column `TTL`. So in case the `DEFAULT` expression is present, outdated columns will have this value assigned.

## Moving data between hot and cold storage

For local setups, consider using storage management for your data. Typically users need faster but smaller disks (called hot, e.g., SSD) and larger but slower ones (called cold, e.g., HDD or S3). ClickHouse allows setting data policy so that data is moved to a slower device once the faster device usage reaches a specific threshold. This storage policy is [configured](https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/mergetree#table_engine-mergetree-multiple-volumes_configure) in two steps - declaring a storage list and a policy.

Alternatively, consider using ClickHouse Cloud, which avoids this complexity by separating storage and compute using object storage. When coupled with intelligent caching for data queried more often, typically your newer "hot" data, tiered architectures are no longer required.

## Summary

ClickHouse provides powerful data lifecycles management tools to enable automatic removal, compaction, or movement between different storage types. Compacting and retention can be configured using the `TTL` statement at a table level. Use [disk policies](https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/mergetree#table_engine-mergetree-multiple-volumes) to manage storage or consider using [ClickHouse Cloud](https://clickhouse.com/cloud) as a reliable solution to scaling.

For more details on TTL, see our [recently published guide](https://clickhouse.com/docs/en/guides/developer/ttl/).
