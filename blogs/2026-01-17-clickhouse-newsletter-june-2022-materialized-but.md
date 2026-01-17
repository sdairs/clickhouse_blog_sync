---
title: "ClickHouse Newsletter June 2022: Materialized, but still real-time"
date: "2022-07-11T23:06:41.132Z"
author: "Christoph Wurm"
category: "Product"
excerpt: "Our regular May release has new features for those of you running large memory-hungry workloads, we talk about querying incomplete time series data and bring you some reading material to enjoy on your garden or balcony at the end."
---

# ClickHouse Newsletter June 2022: Materialized, but still real-time



Welcome to summer in the northern hemisphere and to your monthly dose of ClickHouse goodness. Also, our regular May release has new features for those of you running large memory-hungry workloads, we talk about querying incomplete time series data and bring you some reading material to enjoy on your garden or balcony at the end.


## **Upcoming Events**

Mark your calendars for this:

**ClickHouse v22.6 Release Webinar**  
 * **_When?_** Thursday, June 16 @ 9 am PDT / 5 pm GMT  
 * **_How do I join?_** Register [here](https://clickhouse.com/company/events/v22-6-release-webinar/).


## **ClickHouse v22.5**

What’s in our regular monthly May release:



1. **Memory Overcommit** [In version 22.2](https://clickhouse.com/blog/clickhouse-22-2-released/) we released memory overcommit as an experimental feature. It consists of a soft and a hard limit, allowing queries to burst beyond the soft limit when possible, making it easier to run very different queries on the same ClickHouse instance. In 22.5, memory overcommit is [turned on by default](https://github.com/ClickHouse/ClickHouse/pull/35921) and the old `max_memory_usage` setting has been removed from the default settings.
2. **[Parallel hash joins](https://github.com/ClickHouse/ClickHouse/pull/36415)** A new join type splits a join into multiple blocks and executes them in parallel. This is especially useful for large joins, where a high parallelism can decrease query execution time by over 80%. Try it with your join queries by setting `join_algorithm = 'parallel_hash'`.
3. **[Grouping sets](https://github.com/ClickHouse/ClickHouse/pull/33631)** GROUP BY has a new modifier `GROUPING SETS` which allows you to specify aggregating by any columns. By the way, did you know about the existing modifiers `WITH TOTALS`, `WITH ROLLUP` and `WITH CUBE`?
4. **FIPS** We [switched](https://github.com/ClickHouse/ClickHouse/pull/35914) to an updated BoringSSL module, ClickHouse is now FIPS compliant!
5. Lastly, we’ve also added a new setting which (when turned on) causes “inevitable, unavoidable, fatal and life-threatening performance degradation”. We’ll leave it up to you to find out what it is. Don’t use it in production.

Take a  look at the [release webinar slides](https://presentations.clickhouse.com/release_22.5/), the [recording](https://youtu.be/jkXmXrmjaKQ?t=469) and please upgrade (unless you want to stay on an LTS release).


## **Query of the Month: Materialized, but still real-time**

ClickHouse is often used to store high frequency time series data. For example, financial tick data (prices of stocks, bonds, crypto, etc.) or sensor data.

One of the characteristics of this kind of data is that to get a complete and accurate picture it is often necessary to look potentially far back. For example, not every tick record for a stock is going to have all information needed to display a real-time summary of a stock on a financial website or mobile app – usually that’s at least the current price as well as most recent open, low/high, 52-week low/high price and the volume. This is for a variety of reasons, but mostly it’s because much of this data does not change – the open price is the same throughout the day, so there is no reason to include it in every record.

Similarly, an IoT device or sensor might report a variety of metrics, e.g. several temperature values in different places, pressure, voltage, flow rate and/or many other things. This data can often be incomplete at a given point in time – data arrives late, devices go temporarily or permanently offline, not all information is measured all of the time, etc.

To still be able to get an accurate picture of the data using ClickHouse it is often necessary to employ “point-in-time queries” that start at a given timestamp – this could be the current time, or at some meaningful point in the past. A common way to write queries in ClickHouse that will find the most recent values for different metrics stored as separate columns is to use the `argMax(arg, val)` function. For a given column `val` it will find the maximum value and return the corresponding `arg` column. With a time series dataset this would be something like `argMax(temp, timestamp)` finding the most recent temperature reading.

Because frequent queries like threshold alert triggers might not just be looking at a single column, queries will often end up looking something like this:


```
SELECT device_id, timestamp,
	argMax(temp1, timestamp),
	argMax(pressure, timestamp),
	argMax(flowRate, timestamp)
FROM readings
WHERE device_id IN (<list_of_devices>)
GROUP BY device_id
```


Turns out, this is a very expensive query! For every `device_id` and `argMax` function, ClickHouse needs to scan all records until it finds the most recent value.

A common way to speed up this kind of query is to use a materialized view, pre-aggregating the most recent values for all devices for a given time period. However, this only works well if all metrics are known beforehand (no new columns are ever added) and it will reduce the granularity of the data no longer allowing accurate point-in-time queries for an arbitrary timestamp. Instead, you can combine the two and achieve both the performance improvement of a materialized view and the flexibility of querying raw data. The approach is to generate a materialized view and use it to query all historical data, but combine it with the real-time data up to the most recent requested timestamp.

Start by creating a summary table that the materialized view will write 15-minute summaries of the data to (or any other interval that makes sense, e.g. 5 minutes or 1 hour):


```
CREATE TABLE readings_15min
	device_id LowCardinality(String),
	timestamp_start DateTime64,
	temp AggregateFunction(argMax, Nullable(Float64), DateTime64),
	pressure AggregateFunction(argMax, Nullable(Float64), DateTime64),
	flowRate AggregateFunction(argMax, Nullable(Float64), DateTime64)
ENGINE = AggregatingMergeTree
ORDER BY (timestamp_start, device_id)
```


Create the materialized view:


```
CREATE MATERIALIZED VIEW readings_mv TO readings_15min 
AS SELECT toStartOfFifteenMinutes(timestamp) AS timestamp_start,
	device_id,
	argMaxState(temp, timestamp) AS temp,
	argMaxState(pressure, timestamp) AS pressure,
	argMaxState(flowRate, timestamp) AS flowRate
FROM readings
GROUP BY device_id, toStartOfFifteenMinutes(timestamp)
```


When querying, combine data from both the materialized view and the most recent data from the raw data, combining the results in a final aggregation to get the correct result:


```
WITH '2022-06-06 15:02:00'::DateTime64 as point_in_time
SELECT
	device_id,
	argMax(temp, timestamp_outer) as temp,
	argMax(pressure, timestamp_outer) as pressure,
	argMax(flowRate, timestamp_outer) as flowRate
FROM
	(SELECT max(timestamp_start) as timestamp_outer,
       device_id,
       argMaxMerge(temp) as temp,
       argMaxMerge(pressure) as pressure,
       argMaxMerge(flowRate) as flowRate
	FROM readings_15min 
	WHERE timestamp_start <= toStartOfFifteenMinute(point_in_time)
	GROUP BY device_id
	UNION ALL
	SELECT max(timestamp) as timestamp_outer,
		device_id
		argMax(temp, timestamp) as temp,
		argMax(pressure, timestamp) as pressure,
		argMax(flowRate, timestamp) as flowRate
	FROM readings
	WHERE timestamp BETWEEN toStartOfFifteenMinute(point_in_time) AND point_in_time
	GROUP BY device_id)
GROUP BY device_id
```


Notice the `UNION ALL` clause combining values from the two tables and the complementing `WHERE` conditions.

In a recent test on a dataset of over 200 million rows this approach reduced query times by 98%!


## Reading Corner

What we’ve been reading:

1. We benchmarked ClickHouse on the new AWS Graviton 3 machines – and the results are impressive, [take a look](https://twitter.com/ClickHouseDB/status/1529200554601234434).
2. [Lesser Known Features of ClickHouse](https://pradeepchhetri.xyz/clickhouselesserknownfeatures/): Data transformation with headless ClickHouse, user defined functions, queries on files and other databases, anonymizing data and other cool built-in ClickHouse features.
3. ClickHouse [has more](https://twitter.com/SemenovBv/status/1522596825227837442) active committers (349) than any other open-source database!
4. Aaron Katz, CEO of ClickHouse Inc., [spoke](https://open.spotify.com/episode/15rg6lA4HIADLMHvBJ3SGo) on dbt’s “The Analytics Engineering Podcast”.
5. [Apache SeaTunnel](https://seatunnel.apache.org/), a high-performance data integration framework, added support for generating ClickHouse data files off-server using clickhouse-local and wrote about it [here](https://developpaper.com/how-to-realize-10-billion-level-data-synchronization-based-on-clickhouse-of-seatunnel/).
6. Yugabyte [wrote](https://blog.yugabyte.com/change-data-capture-cdc-yugabytedb-clickhouse/) about using Debezium and Kafka to write a change data capture (CDC) stream to ClickHouse.
7. [New ClickHouse Adopters](https://clickhouse.com/docs/en/introduction/adopters/)**: **A big crowd this month! Welcome to [Uptrace](https://uptrace.dev/open-source/), [Luabase](https://luabase.com/), [June](https://www.june.so/), [PoeticMetric](https://www.poeticmetric.com/), [WebGazer](https://www.webgazer.io/), [GraphQL Hive](https://graphql-hive.com/), [Xenoss](https://xenoss.io/), [ClickVisual](https://clickvisual.gocn.vip/), [G-Core Labs](https://gcorelabs.com/), [TeamApt](https://www.teamapt.com/), and [QuickCheck](https://quickcheck.ng/). Get yourself added as well!

Thanks for reading. We’ll see you next month!

The ClickHouse Team

Photo by [Maxim Hopman](https://unsplash.com/@nampoh?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText) on [Unsplash](https://unsplash.com/?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText)
