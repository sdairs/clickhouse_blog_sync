---
title: "Querying DateTimes in ClickHouse"
date: "2026-03-13T10:25:02.132Z"
author: "Mark Needham"
category: "Engineering"
excerpt: "How to query datetime columns in ClickHouse - from hourly bucketing to rush hour analysis with real taxi data."
---

# Querying DateTimes in ClickHouse

In this post we're going to look at some of the most useful ClickHouse functions for querying and filtering by dates and datetimes - things like rounding to the nearest hour or 15-minute window, filtering by time of day, and computing durations between two timestamps.

If you're working with raw date strings or timestamps that need converting first, check out another post that I wrote about [parsing dates and datetimes in ClickHouse](https://clickhouse.com/blog/parsing-dates-datetimes). This post picks up from there and focuses on what to do once your data is already in a `DateTime` column.


<iframe width="768" height="432" src="https://www.youtube.com/embed/odWa7rAtI5k?si=PkUSvscWY19bmDcu" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

## Importing the New York City taxi dataset {#importing_the_new_york_city_taxi_dataset}

Our dataset of choice is the [New York City taxi dataset](https://clickhouse.com/docs/getting-started/example-datasets/nyc-taxi), so let's get that set up in ClickHouse. First we'll create a database:

<pre><code type='click-ui' language='sql'>
CREATE DATABASE nyc_taxi;
</code></pre>

And a table:

<pre><code type='click-ui' language='sql'>
CREATE TABLE nyc_taxi.trips_small (
    trip_id             UInt32,
    pickup_datetime     DateTime,
    dropoff_datetime    DateTime,
    pickup_longitude    Nullable(Float64),
    pickup_latitude     Nullable(Float64),
    dropoff_longitude   Nullable(Float64),
    dropoff_latitude    Nullable(Float64),
    passenger_count     UInt8,
    trip_distance       Float32,
    fare_amount         Float32,
    extra               Float32,
    tip_amount          Float32,
    tolls_amount        Float32,
    total_amount        Float32,
    payment_type        Enum('CSH' = 1, 'CRE' = 2, 'NOC' = 3, 'DIS' = 4, 'UNK' = 5),
    pickup_ntaname      LowCardinality(String),
    dropoff_ntaname     LowCardinality(String)
)
ENGINE = MergeTree
PRIMARY KEY (pickup_datetime, dropoff_datetime);
</code></pre>

We can then run the following command to import the data:

<pre><code type='click-ui' language='sql'>
INSERT INTO nyc_taxi.trips_small
SELECT
    trip_id,
    pickup_datetime,
    dropoff_datetime,
    pickup_longitude,
    pickup_latitude,
    dropoff_longitude,
    dropoff_latitude,
    passenger_count,
    trip_distance,
    fare_amount,
    extra,
    tip_amount,
    tolls_amount,
    total_amount,
    payment_type,
    pickup_ntaname,
    dropoff_ntaname
FROM s3(
    'https://datasets-documentation.s3.eu-west-3.amazonaws.com/nyc-taxi/trips_{0..2}.gz',
    'TabSeparatedWithNames'
);
</code></pre>

This query imports just over 3 million records, as we can see in the output below:

```shell
3000317 rows in set. Elapsed: 32.077 sec. Processed 3.00 million rows, 256.38 MB (93.53 thousand rows/s., 7.99 MB/s.)
Peak memory usage: 536.51 MiB.
```

We can adjust the `{0..2}` in the URI to include more files if we want to import more data.

Now that we're loaded the data, it's time to write some queries. 
We'll be working with the `pickup_datetime` and `dropoff_datetime` columns:

## Trips by hour {#trips_by_hour}

Let's start by exploring taxi journeys taken on July 1st, 2015. We'll use [`toStartOfHour`](https://clickhouse.com/docs/en/sql-reference/functions/date-time-functions#tostartofhour) to round datetimes down to the nearest hour, [`toDate`](https://clickhouse.com/docs/en/sql-reference/functions/date-time-functions#todate) to filter to a single day, and [`toHour`](https://clickhouse.com/docs/en/sql-reference/functions/date-time-functions#tohour) to restrict to morning hours:

<pre><code type='click-ui' language='sql'>
SELECT
  toStartOfHour(pickup_datetime) as hour,
  count() as trips,
  round(avg(passenger_count), 1) as avg_passengers
FROM nyc_taxi.trips_small
WHERE toDate(pickup_datetime) = '2015-07-01'
AND toHour(pickup_datetime) < 13
GROUP BY hour
ORDER BY hour;
</code></pre>

```shell
┌────────────────hour─┬─trips─┬─avg_passengers─┐
│ 2015-07-01 00:00:00 │   663 │            1.7 │
│ 2015-07-01 01:00:00 │   381 │            1.6 │
│ 2015-07-01 02:00:00 │   249 │            1.8 │
│ 2015-07-01 03:00:00 │   155 │            1.6 │
│ 2015-07-01 04:00:00 │   159 │            1.5 │
│ 2015-07-01 05:00:00 │   197 │            1.5 │
│ 2015-07-01 06:00:00 │   530 │            1.6 │
│ 2015-07-01 07:00:00 │   849 │            1.6 │
│ 2015-07-01 08:00:00 │  1034 │            1.6 │
│ 2015-07-01 09:00:00 │  1033 │            1.7 │
│ 2015-07-01 10:00:00 │   898 │            1.7 │
│ 2015-07-01 11:00:00 │   900 │            1.6 │
│ 2015-07-01 12:00:00 │   961 │            1.7 │
└─────────────────────┴───────┴────────────────┘
```

It was quiet overnight, trips start to pick up around 6am, and peak around 8–9am. But was July 1st typical? Let's remove the date filter and look across all days. To do that we cast `toStartOfHour` down to a `Time` type using [`::Time`](https://clickhouse.com/docs/en/sql-reference/data-types/time) - that strips out the date and leaves just the time, so all days are grouped together:

<pre><code type='click-ui' language='sql'>
SELECT
  toStartOfHour(pickup_datetime)::Time as hour,
  count() as trips,
  round(avg(passenger_count), 1) as avg_passengers
FROM nyc_taxi.trips_small
WHERE toHour(pickup_datetime) < 13
GROUP BY hour
ORDER BY hour;
</code></pre>

```shell
┌─────hour─┬──trips─┬─avg_passengers─┐
│ 00:00:00 │ 118268 │            1.7 │
│ 01:00:00 │  86495 │            1.7 │
│ 02:00:00 │  65246 │            1.7 │
│ 03:00:00 │  47377 │            1.7 │
│ 04:00:00 │  34840 │            1.7 │
│ 05:00:00 │  32328 │            1.6 │
│ 06:00:00 │  68644 │            1.6 │
│ 07:00:00 │ 107494 │            1.6 │
│ 08:00:00 │ 132596 │            1.6 │
│ 09:00:00 │ 136228 │            1.6 │
│ 10:00:00 │ 134286 │            1.7 │
│ 11:00:00 │ 137561 │            1.7 │
│ 12:00:00 │ 145282 │            1.7 │
└──────────┴────────┴────────────────┘
```

When we look across all days we still see a reduction in journeys over night, but the increase starts a couple of hours earlier, from 6am to 7am. The number of trips then stays reasonably stable for the next four hours.

## Rush hour in 15-minute windows {#rush_hour}

When exactly does the morning rush start? Let's zoom in using [`toStartOfFifteenMinutes`](https://clickhouse.com/docs/en/sql-reference/functions/date-time-functions#tostartoffifteenminutes) to bucket by 15-minute intervals, and [`formatDateTime`](https://clickhouse.com/docs/en/sql-reference/functions/date-time-functions#formatdatetime) to make the output readable. In the `WHERE` clause we cast `pickup_datetime` to `Time` to filter just by time of day - no date needed:

<pre><code type='click-ui' language='sql'>
SELECT
  formatDateTime(toStartOfFifteenMinutes(pickup_datetime), '%r') AS timeWindow,
  count() as trips,
  round(avg(trip_distance), 2) as avgDistance
FROM nyc_taxi.trips_small
WHERE pickup_datetime::Time BETWEEN '06:00:00'::Time AND '09:59:59'::Time
AND trip_distance > 0
GROUP BY timeWindow
ORDER BY timeWindow;
</code></pre>

```shell
┌─timeWindow─┬─trips─┬─avgDistance─┐
│ 06:00 AM   │ 11601 │        4.47 │
│ 06:15 AM   │ 14645 │        3.97 │
│ 06:30 AM   │ 19033 │        3.67 │
│ 06:45 AM   │ 22795 │         3.2 │
│ 07:00 AM   │ 23179 │        3.27 │
│ 07:15 AM   │ 25465 │        3.12 │
│ 07:30 AM   │ 28350 │        3.04 │
│ 07:45 AM   │ 29914 │        2.89 │
│ 08:00 AM   │ 30444 │           3 │
│ 08:15 AM   │ 32063 │        2.91 │
│ 08:30 AM   │ 34293 │         2.8 │
│ 08:45 AM   │ 35116 │        2.63 │
│ 09:00 AM   │ 33776 │        2.74 │
│ 09:15 AM   │ 33800 │        2.72 │
│ 09:30 AM   │ 33694 │        2.73 │
│ 09:45 AM   │ 34235 │        2.63 │
└────────────┴───────┴─────────────┘
```

The surge begins at 6:30, accelerates until 7:30, and peaks at 8:45.

## What does rush hour feel like? {#rush_hour_speed}

We know when rush hour starts - but what does it feel like if you're in a taxi? We can use [`dateDiff`](https://clickhouse.com/docs/en/sql-reference/functions/date-time-functions#datediff) to compute journey duration in minutes, which lets us calculate average speed. We also use `dateDiff` in the `WHERE` clause to filter out zero-duration trips (bad data):

<pre><code type='click-ui' language='sql'>
WITH buckets AS (
  SELECT
    formatDateTime(toStartOfFifteenMinutes(pickup_datetime), '%r') AS timeWindow,
    count() as trips,
    round(avg(trip_distance), 2) as avgDist,
    round(avg(dateDiff('minute', pickup_datetime, dropoff_datetime)), 1) AS avgDuration,
    round(avg(
      trip_distance /
      (dateDiff('minute', pickup_datetime, dropoff_datetime) / 60)
    ), 1) AS avgSpeed
  FROM nyc_taxi.trips_small
  WHERE pickup_datetime::Time BETWEEN '06:00:00'::Time AND '09:59:59'::Time
  AND trip_distance > 0
  AND dateDiff('minute', pickup_datetime, dropoff_datetime) > 0
  GROUP BY timeWindow
  ORDER BY timeWindow
)
SELECT timeWindow, trips, avgDuration, avgDist, avgSpeed,
       bar(avgSpeed, 0, (SELECT max(avgSpeed) FROM buckets), 20) AS speedBar
FROM buckets
ORDER BY timeWindow ASC;
</code></pre>

```shell
┌─timeWindow─┬─trips─┬─avgDuration─┬─avgDist─┬─avgSpeed─┬─speedBar─────────────┐
│ 06:00 AM   │ 11562 │        13.2 │    4.48 │     19.3 │ ████████████████████ │
│ 06:15 AM   │ 14609 │        13.1 │    3.98 │     18.2 │ ██████████████████▊  │
│ 06:30 AM   │ 18993 │        12.5 │    3.67 │     17.3 │ █████████████████▉   │
│ 06:45 AM   │ 22754 │        11.5 │    3.21 │     16.1 │ ████████████████▋    │
│ 07:00 AM   │ 23139 │        12.3 │    3.27 │     15.4 │ ███████████████▉     │
│ 07:15 AM   │ 25428 │        12.7 │    3.12 │     14.3 │ ██████████████▊      │
│ 07:30 AM   │ 28313 │        13.9 │    3.04 │     13.5 │ █████████████▉       │
│ 07:45 AM   │ 29873 │        13.8 │    2.89 │     12.7 │ █████████████▏       │
│ 08:00 AM   │ 30411 │        14.2 │       3 │       12 │ ████████████▍        │
│ 08:15 AM   │ 32017 │        15.2 │    2.91 │     11.5 │ ███████████▉         │
│ 08:30 AM   │ 34258 │        15.4 │     2.8 │       11 │ ███████████▍         │
│ 08:45 AM   │ 35071 │        14.9 │    2.64 │     10.8 │ ███████████▏         │
│ 09:00 AM   │ 33718 │        15.3 │    2.74 │     10.9 │ ███████████▎         │
│ 09:15 AM   │ 33754 │        15.3 │    2.72 │     10.8 │ ███████████▏         │
│ 09:30 AM   │ 33657 │        15.4 │    2.73 │     10.8 │ ███████████▏         │
│ 09:45 AM   │ 34188 │        14.8 │    2.63 │     10.9 │ ███████████▎         │
└────────────┴───────┴─────────────┴─────────┴──────────┴──────────────────────┘
```

The [`bar`](https://clickhouse.com/docs/en/sql-reference/functions/other-functions#bar) function draws an ASCII bar chart scaled to the max value - a handy way to visualize relative values inline.

At 6am taxis are moving at just over 19 mph. By 8am that's down to around 12 mph - slow, but pretty standard for a big city during rush hour. It keeps getting slower as the morning wears on.

## Weekdays vs weekends {#weekdays_vs_weekends}

We've confirmed rush hour exists - but does it happen on weekends too? We can split weekday and weekend trips using [`countIf`](https://clickhouse.com/docs/en/sql-reference/aggregate-functions/combinators#-if) with [`toDayOfWeek`](https://clickhouse.com/docs/en/sql-reference/functions/date-time-functions#todayofweek): values 1–5 are weekdays, 6–7 are weekends. We then use the [`lag`](https://clickhouse.com/docs/en/sql-reference/window-functions) window function to compute the percentage change in trips between each 15-minute window:

<pre><code type='click-ui' language='sql'>
WITH trips AS (
  SELECT
    formatDateTime(toStartOfFifteenMinutes(pickup_datetime), '%r') AS timeWindow,
    countIf(toDayOfWeek(pickup_datetime) <= 5) as wdTrips,
    countIf(toDayOfWeek(pickup_datetime) > 5) as weTrips
  FROM nyc_taxi.trips_small
  WHERE trip_distance > 0
  AND pickup_datetime::Time BETWEEN '06:00:00'::Time AND '09:59:59'::Time
  GROUP BY timeWindow
  ORDER BY timeWindow
)
SELECT timeWindow, wdTrips,
  round((
    (wdTrips - lag(wdTrips) OVER (ORDER BY timeWindow)) /
    lag(wdTrips) OVER (ORDER BY timeWindow)) * 100,
  1) as wdPctChange,
  weTrips,
  round(
    ((weTrips - lag(weTrips) OVER (ORDER BY timeWindow)) /
    lag(weTrips) OVER (ORDER BY timeWindow)) * 100,
  1) as wePctChange
FROM trips
ORDER BY timeWindow;
</code></pre>

```shell
┌─timeWindow─┬─wdTrips─┬─wdPctChange─┬─weTrips─┬─wePctChange─┐
│ 06:00 AM   │    9398 │         inf │    2203 │         inf │
│ 06:15 AM   │   12254 │        30.4 │    2391 │         8.5 │
│ 06:30 AM   │   16106 │        31.4 │    2927 │        22.4 │
│ 06:45 AM   │   19727 │        22.5 │    3068 │         4.8 │
│ 07:00 AM   │   20285 │         2.8 │    2894 │        -5.7 │
│ 07:15 AM   │   22129 │         9.1 │    3336 │        15.3 │
│ 07:30 AM   │   24494 │        10.7 │    3856 │        15.6 │
│ 07:45 AM   │   25681 │         4.8 │    4233 │         9.8 │
│ 08:00 AM   │   26259 │         2.3 │    4185 │        -1.1 │
│ 08:15 AM   │   27509 │         4.8 │    4554 │         8.8 │
│ 08:30 AM   │   28891 │           5 │    5402 │        18.6 │
│ 08:45 AM   │   29154 │         0.9 │    5962 │        10.4 │
│ 09:00 AM   │   27872 │        -4.4 │    5904 │          -1 │
│ 09:15 AM   │   27268 │        -2.2 │    6532 │        10.6 │
│ 09:30 AM   │   26426 │        -3.1 │    7268 │        11.3 │
│ 09:45 AM   │   26070 │        -1.3 │    8165 │        12.3 │
└────────────┴─────────┴─────────────┴─────────┴─────────────┘
```

Weekdays show a sharp spike at 6:15–6:30, a second (smaller) increase around 7:15–7:30, and peak at 8:45 before leveling off. Weekends are different: the increase at 6:30 is gentler, and trips keep growing steadily well into the morning.


---

## Get started today

Interested in seeing how ClickHouse works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-101-get-started-today-sign-up&utm_blogctaid=101)

---