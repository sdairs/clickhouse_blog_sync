---
title: "ClickHouse Release 26.6"
date: "2026-07-01T13:11:27.127Z"
category: "Engineering"
excerpt: "ClickHouse 26.6 is here! In this release, we have hypothetical skip indexes, cascading refreshable materialized views, experimental support for continuous queries, and more!"
---

# ClickHouse Release 26.6

Another month goes by, which means it’s time for another release! 

<p>The ClickHouse 26.6 release contains 56 new features &#127774; 79 performance optimizations &#127958;&#65039; 366 bug fixes &#127846;</p>

This release introduces hypothetical skip indexes, cascading refreshable materialized views, experimental support for continuous queries, and more!

## New contributors {#new_contributors}

A special welcome to all the new contributors in 26.6! The growth of ClickHouse's community is humbling, and we are always grateful for the contributions that have made ClickHouse so popular.

Below are the names of the new contributors:

*Aditya Chopra, Alasdair Brown, Almaz Kunpeissov, Andriy Yakovlev, Antonio Filipovic, Asya Shneerson, Avenir Voronov, Dmitriy Borisenko, Elian Gidoni, Hanzi Jiang, Harikrishnan Prabakaran, Joe Smith, Joey Yu, Le Zhang, Lefteris Gilmaz, Maksim Dergousov, Maksim Moisiuk, Mathuranath Metivier, Minh Vu, Mohamed Abdelhalim, Mohamed Hussain, MunMunMiao, Patrick Pichler, Ramarajusairajesh, Rory Shanks, SKULLFIRE07, Saarthak Gupta, Sacheendra Talluri, Sergey Kuznetsov, Thomas Cabral, Valerii Mordovskii, Valerii Petrov, Varoon Pazhyanur, Venkata Vineel, Vinayak Joshi, Walt Ribeiro, Youssef Kadry, abdelhalim, abduldjafar, alexbakharew, andyzzhao, bernardlim, daxzel, harikrishnan94, leonard9893, linjiayu, mzitnik, ofeliacode, siwakorn.r, sugaf1204, thewisenerd, uber, uwezkhan, valerypetrov, yousefQadry, zhiqiang-hhhh*

Hint: if you’re curious how we generate this list… [here](https://gist.github.com/gingerwizard/5a9a87a39ba93b422d8640d811e269e9).

<iframe width="768" height="432" src="https://www.youtube.com/embed/-NmqMH9y4EY?si=Pr5MVBncQC-1KfHs" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

You can also [view the slides from the presentation](https://presentations.clickhouse.com/2026-release-26.6).

## Hypothetical skip indexes {#hypothetical_skip_indexes}

### Contributed by Yarik Briukhovetskyi

Starting from ClickHouse 26.6, it’s possible to ask "what if I had this skip index?" without having to build it.

Hypothetical indexes live only in the current session and are invisible to other sessions and discarded when the session ends.

<iframe width="768" height="432" src="https://www.youtube.com/embed/sm5f0vpiCRE?si=2NIVsQD6VYy-w1rf" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>


We tried them out on the [UK properties dataset](https://clickhouse.com/docs/getting-started/example-datasets/uk-price-paid), having duplicated the partitions a few times so that we had more rows to work with:

<pre><code type='click-ui' language='sql'>
ALTER TABLE uk_price_paid
ATTACH PARTITION ID 'all'
FROM uk_price_paid;
</code></pre>

We have almost 500 million rows:

<pre><code type='click-ui' language='sql'>
SELECT count() FROM uk_price_paid;
</code></pre>

```shell
┌───count()─┐
│ 487239408 │ -- 487.24 million
└───────────┘

1 row in set. Elapsed: 0.006 sec.
```

We run the following query to find the districts in London with the most sales:

<pre><code type='click-ui' language='sql'>
SELECT district, count(), round(avg(price)) AS avgPrice
FROM uk_price_paid
WHERE town = 'LONDON'
GROUP BY ALL
ORDER BY count() DESC
LIMIT 10;
</code></pre>

```shell
┌─district────────────┬─count()─┬─avgPrice─┐
│ WANDSWORTH          │ 3258048 │   496367 │
│ LAMBETH             │ 2354352 │   402424 │
│ CITY OF WESTMINSTER │ 2164304 │  1215976 │ -- 1.22 million
│ TOWER HAMLETS       │ 2098864 │   473783 │
│ LEWISHAM            │ 2022208 │   291688 │
│ SOUTHWARK           │ 1998816 │   462604 │
│ BARNET              │ 1942384 │   449124 │
│ GREENWICH           │ 1874464 │   316369 │
│ WALTHAM FOREST      │ 1813360 │   270709 │
│ NEWHAM              │ 1706352 │   284768 │
└─────────────────────┴─────────┴──────────┘

10 rows in set. Elapsed: 0.317 sec. Processed 487.24 million rows, 1.20 GB (1.54 billion rows/s., 3.80 GB/s.)
Peak memory usage: 894.97 KiB.
```

We can probably improve the performance of this query by adding a set skip index on the `town` column. 

A set skip index would store the unique values for that column for the provided number of granules. At query time, ClickHouse could refer to this skip-index set to determine whether it needs to scan a particular granule/granules.

Before 26.6, we’d need to create that skip index and test it out, but now we can create a hypothetical index instead. And, in fact, we’re going to create two hypothetical indexes so that we can see the difference between creating a skip index per granule compared to one for every 128 granules:

<pre><code type='click-ui' language='sql'>
CREATE HYPOTHETICAL INDEX town_set_10_granularity_1
ON uk_price_paid (town)
TYPE set(10)
GRANULARITY 1;

CREATE HYPOTHETICAL INDEX town_set_10_granularity_128
ON uk_price_paid (town)
TYPE set(10)
GRANULARITY 128;
</code></pre>

Once we’ve done that, we can prefix our district query with `EXPLAIN WHATIF`:

<pre><code type='click-ui' language='sql'>
EXPLAIN WHATIF
SELECT district, count(), round(avg(price)) AS avgPrice
FROM uk_price_paid
WHERE town = 'LONDON'
GROUP BY ALL
ORDER BY count() DESC
LIMIT 10;
</code></pre>

When we run that query, ClickHouse will read table data to build the candidate index in memory, and scan counts against the session's read limits and quotas. The output of running the query is shown below:

```shell
┌─explain───────────────────────────────────────────────┐
│ Baseline (after PK + partition + existing indexes):   │
│   table:       default.uk_price_paid                  │
│   parts:       3                                      │
│   marks:       59479                                  │
│   est_bytes:   831.90 MiB                             │
│                                                       │
│ With town_set_10_granularity_128 (set, hypothetical): │
│   status:       applicable                            │
│   marks:        13702                                 │
│   est_bytes:    191.64 MiB                            │
│   skip_ratio:   77.0%                                 │
│                                                       │
│ Estimation:                                           │
│   source:           empirical                         │
│   empirical_status: ok                                │
│   sampled_parts:    3 / 3                             │
│   sampled_marks:    59479 / 118964                    │
│   elapsed_us:       3826267                           │
│                                                       │
│ With town_set_10_granularity_1 (set, hypothetical):   │
│   status:       applicable                            │
│   marks:        4663                                  │
│   est_bytes:    65.22 MiB                             │
│   skip_ratio:   92.2%                                 │
│                                                       │
│ Estimation:                                           │
│   source:           empirical                         │
│   empirical_status: ok                                │
│   sampled_parts:    3 / 3                             │
│   sampled_marks:    59479 / 118964                    │
│   elapsed_us:       4283731                           │
│                                                       │
└───────────────────────────────────────────────────────┘

32 rows in set. Elapsed: 8.115 sec. Processed 974.48 million rows, 1.95 GB (120.08 million rows/s., 240.11 MB/s.)
Peak memory usage: 269.35 KiB.
```

If we look at row 12, we can see that the index for 128 granules will skip 77% of granules for this query, whereas on row 25, the index per granule would instead skip 92% of granules. 

This gives us some useful information before deciding whether to create a skip index and what settings to use.

## Cascading refreshable materialized views {#cascading_refreshable_materialized_views}

### Contributed by Michael Kolupaev

ClickHouse 26.6 introduces an overhaul of how dependencies work for refreshable materialized views.

Before this release, it was possible to create dependencies between refreshable materialized views, but the dependent views still ran on their own independent timers. This meant that latency could build up between stages if the schedules drifted, and views could skip or lag by a full refresh cycle.

Let’s have a look at how to set things up with the following set of tables that represent IMDB data:

<pre><code type='click-ui' language='sql'>
CREATE TABLE actor_summary
(
    `id` UInt32,
    `name` String,
    `movies` UInt16,
    `avg_rank` Float32,
    `genres` UInt16,
    `directors` UInt16,
    `updated_at` DateTime
)
ENGINE = MergeTree
ORDER BY movies;
</code></pre>

<pre><code type='click-ui' language='sql'>
CREATE TABLE actor_rank
(
    `id` UInt32,
    `name` String,
    `movies` UInt16,
    `avg_rank` Float32,
    `genres` UInt16,
    `directors` UInt16,
    `updated_at` DateTime
)
ENGINE = MergeTree
ORDER BY movies;
</code></pre>

<pre><code type='click-ui' language='sql'>
CREATE TABLE actor_rank_over_time
(
    `id` UInt32,
    `name` String,
    `avg_rank` Float32,
    `as_of` DateTime
)
ENGINE = MergeTree
ORDER BY as_of;
</code></pre>

We previously populated these tables like this:

<pre><code type='click-ui' language='sql'>
CREATE MATERIALIZED VIEW actor_summary_mv
REFRESH EVERY 2 MINUTES TO actor_summary AS
...
</code></pre>

<pre><code type='click-ui' language='sql'>
CREATE MATERIALIZED VIEW actor_rank_mv
REFRESH EVERY 1 MINUTE DEPENDS ON actor_summary_mv
TO imdb.actor_rank AS
SELECT *
FROM actor_summary
WHERE movies > 10
ORDER BY avg_rank DESC
LIMIT 5;
</code></pre>

<pre><code type='click-ui' language='sql'>
CREATE MATERIALIZED VIEW actor_rank_over_time_mv
REFRESH EVERY 1 MINUTE DEPENDS ON actor_rank_mv
APPEND
TO imdb.actor_rank_over_time AS
SELECT id, name, avg_rank, now() AS as_of
FROM actor_rank
ORDER BY avg_rank DESC
LIMIT 1;
</code></pre>

Now, only `actor_summary_mv` has a timer, but we don’t need to specify one for `actor_rank_mv` or `actor_rank_over_time_mv`. So, we end up with the following:

<pre><code type='click-ui' language='sql'>
CREATE MATERIALIZED VIEW actor_summary_mv
REFRESH EVERY 2 MINUTES TO actor_summary AS
...
</code></pre>

<pre><code type='click-ui' language='sql'>
CREATE MATERIALIZED VIEW actor_rank_mv
REFRESH DEPENDS ON actor_summary_mv
TO imdb.actor_rank AS
SELECT *
FROM actor_summary
WHERE movies > 10
ORDER BY avg_rank DESC
LIMIT 5;

</code></pre>

<pre><code type='click-ui' language='sql'>
CREATE MATERIALIZED VIEW actor_rank_over_time_mv
REFRESH DEPENDS ON actor_rank_mv
APPEND
TO actor_rank_over_time AS
SELECT id, name, avg_rank, now() AS as_of
FROM imdb.actor_rank
ORDER BY avg_rank DESC
LIMIT 1;
</code></pre>

## ALTER TABLE … ADD ENUM VALUES {#alter_table_add_enum_values}

### Contributed by Ilya Golshtein

We can write the following query to find the enum columns in our `uk_price_paid` table:

<pre><code type='click-ui' language='sql'>
SELECT name, type
FROM system.columns
WHERE table = 'uk_price_paid'
  AND database = 'default'
  AND type LIKE 'Enum%'
FORMAT Vertical;
</code></pre>

```shell
Row 1:
──────
name: type
type: Enum8('other' = 0, 'terraced' = 1, 'semi-detached' = 2, 'detached' = 3, 'flat' = 4)

Row 2:
──────
name: duration
type: Enum8('unknown' = 0, 'freehold' = 1, 'leasehold' = 2)
```

Prior to ClickHouse 26.6, if we wanted to add a new enum value, we’d need to also provide the existing values when doing so:

<pre><code type='click-ui' language='sql'>
ALTER TABLE uk_price_paid
MODIFY COLUMN type Enum8(
 'other' = 0, 
 'terraced' = 1,
 'semi-detached' = 2,
 'detached' = 3,
 'flat' = 4,
 'royal' = 5
);
</code></pre>

It’s now possible to append a new value using the `ADD ENUM VALUES` syntax:

<pre><code type='click-ui' language='sql'>
ALTER TABLE uk_price_paid 
MODIFY COLUMN type
ADD ENUM VALUES('royal' = 5);
</code></pre>

And if we re-run the query to show our enum columns:

```shell
Row 1:
──────
name: type
type: Enum8('other' = 0, 'terraced' = 1, 'semi-detached' = 2, 'detached' = 3, 'flat' = 4, 'royal' = 5)

Row 2:
──────
name: duration
type: Enum8('unknown' = 0, 'freehold' = 1, 'leasehold' = 2)

2 rows in set. Elapsed: 0.006 sec.
```

## help in the CLI {#help_in_the_cli}

### Contributed by Alexey Milovidov

If you’re in the ClickHouse zone and need to look up some documentation, there’s no need to move out of the CLI to search the docs or ask your AI agent for the answer. Instead, you can type `help` followed by the topic, and you’ll get back in-line documentation.

<pre><code type='click-ui' language='bash'>
help Geometry;
</code></pre>

```shell
GEOMETRY  (Data Type)
─────────────────────────────────────────────────────────────────────────────────────────

Alias of Geometry.

Geometry  (Data Type)
─────────────────────────────────────────────────────────────────────────────────────────

Geometry is a Variant type that can hold any of the geometric data types: Point,
LineString, MultiLineString, Polygon, MultiPolygon, or Ring.

Syntax

    Geometry

Related: Point
```

This is backed by the new `system.documentation` table, which you can also query directly:

<pre><code type='click-ui' language='sql'>
SELECT type, count()
FROM system.documentation
GROUP BY type
ORDER by count() DESC
LIMIT 10;

</code></pre>

```shell
┌─type───────────────┬─count()─┐
│ Function           │    1593 │
│ Setting            │    1549 │
│ Server Setting     │     412 │
│ MergeTree Setting  │     316 │
│ Aggregate Function │     197 │
│ Data Type          │     140 │
│ Format             │     109 │
│ Table Engine       │      79 │
│ Table Function     │      66 │
│ Dictionary Layout  │      19 │
└────────────────────┴─────────┘

10 rows in set. Elapsed: 0.019 sec. Processed 4.54 thousand rows, 4.36 MB (240.42 thousand rows/s., 230.69 MB/s.)
Peak memory usage: 6.18 MiB.
```

## Transform clickhouse-local to a server {#transform_clickhouse_local_to_a_server}

### Contributed by Alexey Milovidov

[clickhouse-local](https://clickhouse.com/docs/concepts/features/tools-and-utilities/clickhouse-local) is our go-to tool for doing any ad hoc data analysis, but sometimes you want to hook up your ClickHouse instance to external tools, which wasn’t straightforward.

As of 26.6, you can now have clickhouse-local listen for connections on the fly:

<pre><code type='click-ui' language='bash'>
SYSTEM START LISTEN TCP;
SYSTEM START LISTEN HTTP;
</code></pre>

You can then connect to it as you’re running ClickHouse Server. And once you’re done, it’s easy enough to stop listening on those ports:

<pre><code type='click-ui' language='bash'>
SYSTEM STOP LISTEN TCP;
SYSTEM STOP LISTEN HTTP;
</code></pre>

## Lighter, faster query startup {#lighter_faster_query_startup}

### Contributed by Raúl Marín, Dmitry Novik, Max Justus Spransy, Azat Khuzhin

There are a series of improvements in 26.6 that significantly reduce per-query overhead for simple queries.

Deeply nested queries, in particular, are now analyzed more efficiently. Let’s run the following (unnecessarily complex) query:

<pre><code type='click-ui' language='sql'>
SELECT * FROM (SELECT * FROM (SELECT * FROM (SELECT * FROM (
SELECT * FROM (SELECT * FROM (SELECT * FROM (SELECT * FROM (
SELECT * FROM (SELECT * FROM (SELECT * FROM (SELECT * FROM (
SELECT * FROM (SELECT * FROM (SELECT * FROM (SELECT * FROM (
SELECT * FROM (SELECT * FROM (SELECT * FROM (
    SELECT * FROM uk_price_paid LIMIT 10
)))))))))))))))))));
</code></pre>

Against 26.5:

```shell
10 rows in set. Elapsed: 0.098 sec.
10 rows in set. Elapsed: 0.102 sec.
10 rows in set. Elapsed: 0.100 sec.
```

And against 26.6:

```shell
10 rows in set. Elapsed: 0.030 sec.
10 rows in set. Elapsed: 0.036 sec.
10 rows in set. Elapsed: 0.050 sec.
```

The best time on 26.6 was 30 milliseconds, compared to the best of 98 milliseconds on 26.5, a roughly 3 times improvement.

## Continuous queries {#continuous_queries}

### Contributed by Mikhail Artemenko

We also have the introduction of streaming queries in experimental mode. You can now write a query that never ends by appending `STREAM`. The query will keep emitting new rows as they are inserted.

To enable this feature, you can use the following setting:

<pre><code type='click-ui' language='bash'>
SET enable_streaming_queries = 1;
</code></pre>

And then, we could write the following query that blocks and keep streaming new rows:

<pre><code type='click-ui' language='sql'>
SELECT id, msg 
FROM live_events STREAM;
</code></pre>

As new rows are added to `live_events`, they would be returned by the above query. 

This feature can also be used in a more advanced mode with cursors:

<pre><code type='click-ui' language='sql'>
SELECT _block_number AS bn, _block_offset AS bo, id, msg
FROM events STREAM 
CURSOR {'all': {'block_number': 2, 'block_offset': 0}};
</code></pre>

As of ClickHouse 26.6, this feature is only available for Linux.


---

## Get started today

Interested in seeing how ClickHouse works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-1150-get-started-today-sign-up&utm_blogctaid=1150)

---

<style>
pre code { white-space: pre !important; }
</style>