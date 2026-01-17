---
title: "Accelerating ClickHouse queries on JSON data for faster Bluesky insights"
date: "2025-03-16T15:39:12.690Z"
author: "Tom Schreiber"
category: "Engineering"
excerpt: "Learn how to guarantee sub-100ms ClickHouse response times for snappy dashboards—no matter how many billions of JSON documents your table holds."
---

# Accelerating ClickHouse queries on JSON data for faster Bluesky insights

## Why real-time dashboard speed matters

For real-time analytical applications (e.g. dashboards) to feel **snappy**, response times should align with these human-perceived performance guidelines, as outlined by [Jakob Nielsen](https://www.nngroup.com/articles/response-times-3-important-limits/), [mental chronometry research](https://en.wikipedia.org/wiki/Mental_chronometry), and further insights from [Jakob Nielsen](https://www.nngroup.com/articles/website-response-times/) and [Steve Henty](https://slhenty.medium.com/ui-response-times-acec744f3157):


<div style="padding: 12px; border: 1px solid #323232; border-radius: 5px; background-color: #2E2E2D; color: white; font-family: Arial, sans-serif; line-height: 1.4;">
  <p style="color: #00FF00; font-weight: bold; margin-bottom: 4px;">&lt;100ms (instant) <span style="color: white; font-weight: normal;">— Feels instant, ideal for filtering or quick updates.</span></p>

  <p style="color: #00BFFF; font-weight: bold; margin-bottom: 4px;">100ms - 500ms (very fast) <span style="color: white; font-weight: normal;">— Smooth, great for charts, tab switches, or summaries.</span></p>

  <p style="color: #FFA500; font-weight: bold; margin-bottom: 4px;">500ms - 1s (noticeable delay) <span style="color: white; font-weight: normal;">— Users notice the wait. Acceptable for complex queries.</span></p>

  <p style="color: #FF4500; font-weight: bold; margin-bottom: 4px;">1s - 2s (slow but tolerable) <span style="color: white; font-weight: normal;">— Feels sluggish. Use loading indicators.</span></p>

  <p style="color: #FF0000; font-weight: bold; margin-bottom: 4px;">&gt;2s (too slow) <span style="color: white; font-weight: normal;">— Feels unresponsive. Users lose focus.</span></p>
</div>


<br/>

Achieving sub-500ms—or even sub-100ms—queries at scale, especially with billions of JSON documents, is challenging without the right database. Most systems slow down as datasets grow, resulting in sluggish dashboards and frustrated users.

In this post, we showcase proven query acceleration techniques through three typical real-time dashboard scenarios, where all dashboard queries logically process **4+ billion Bluesky JSON documents (1.6 TiB of data)**—all running on a **normal, modestly sized machine**—yet:
<p>
① Achieve <strong style="color: #00FF00;">guaranteed instantaneous (&lt;100ms) ClickHouse response times</strong>.<br/>
② Maintain speed, <strong style="color: #00FF00;">no matter how many more billions of documents are stored</strong>.<br/>
③ Always run on the latest data or with minimal delay.<br/>
④ Use minimal CPU & memory, consuming just KBs to low MBs of RAM.
</p>

The table below previews the optimizations we’ll achieve—demonstrating how ClickHouse can sustain real-time dashboard performance at any scale, even with billions of JSON documents.

<style>
  .table-container {
    overflow-x: auto;
    max-width: 100%;
  }
  table {
    border-collapse: collapse;
    width: 100%;
    min-width: 600px; /* Ensures table doesn't shrink too much */
  }
  th, td {
    border: 1px solid #444;
    padding: 8px;
    text-align: center;
    vertical-align: middle;
  }
  th span {
    display: block;
    white-space: nowrap;
  }
  .dashboard-title {
    font-weight: bold;
    text-align: left;
    border-bottom: none;
    color: #FDFF88;
  }
  .query-type {
    font-weight: bold;
    white-space: nowrap;
  }
  .accelerated-query {
    color: #00FF00;
    font-weight: bold;
  }
  
  /* Responsive adjustments */
  @media (max-width: 768px) {
    table {
      font-size: 14px;
    }
    th, td {
      padding: 6px;
    }
    th span {
      display: inline;
      white-space: normal;
    }
  }
</style>

<div class="table-container">
  <table>
    <tr>
      <th></th>
      <th><span>① Response</span><span>time</span></th>
      <th><span>② Maintains speed</span><span>as data grows</span></th>
      <th><span>③ Runs over</span><span>latest data</span></th>
      <th><span>④ Minimized CPU &</span><span>memory costs</span></th>
    </tr>
    <tr>
      <td class="dashboard-title" colspan="5">Dashboard 1: Tracking Bluesky activity trends</td>
    </tr>
    <tr>
      <td class="query-type">Accelerated query</td>
      <td class="accelerated-query">6 ms</td>
      <td>✅</td>
      <td>✅</td>
      <td>✅</td>
    </tr>
    <tr>
      <td class="dashboard-title" colspan="5">Dashboard 2: Ranking the most popular Bluesky events</td>
    </tr>
    <tr>
      <td class="query-type">Accelerated query</td>
      <td class="accelerated-query">7 ms</td>
      <td>✅</td>
      <td>✅</td>
      <td>✅</td>
    </tr>
    <tr>
      <td class="dashboard-title" colspan="5">Dashboard 3: Discovering the most reposted Bluesky posts</td>
    </tr>
    <tr>
      <td class="query-type">Accelerated query</td>
      <td class="accelerated-query">3 ms</td>
      <td>✅</td>
      <td>5s delay</td>
      <td>✅</td>
    </tr>
  </table>
</div>


Before diving into the optimizations, we’ll first introduce our Bluesky dataset and hardware. Then, through three selected real-time dashboard scenarios, we’ll demonstrate exactly how to achieve—and sustain—instantaneous (&lt;100ms) query performance at any scale.

> **TL;DR? Jump straight to the key takeaways!**  
> If you're looking for the final results and optimization insights, skip ahead to  
> [Mission accomplished: sustained <100ms query times](/blog/accelerating-clickhouse-json-queries-for-fast-bluesky-dashboards#mission-accomplished-sustained-100ms-query-performance).

## The Bluesky JSON dataset

Our example dataset is a real-time JSON event stream scraped from [Bluesky](https://bsky.social/about), a popular social media platform. As [detailed](https://clickhouse.com/blog/building-a-medallion-architecture-for-bluesky-json-data-with-clickhouse#reading-bluesky-data) in another post, we continuously ingest new [events](https://github.com/bluesky-social/jetstream?tab=readme-ov-file#example-events) (e.g. post, like, repost). 

### How we store Bluesky JSON data in ClickHouse

Below is the schema of the ClickHouse table storing the full, constantly growing Bluesky dataset, accessible through our [ClickHouse SQL playground](/blog/accelerating-clickhouse-json-queries-for-fast-bluesky-dashboards#test-all-queries-live):

<pre>
<code type='click-ui' language='sql'>
CREATE TABLE bluesky.bluesky
(
  kind LowCardinality(String),
  data JSON,
  bluesky_ts DateTime64(6)
)
ENGINE = MergeTree
ORDER BY (kind, bluesky_ts);
</code>
</pre>

The data column uses our [revamped](https://clickhouse.com/blog/a-new-powerful-json-data-type-for-clickhouse) JSON type to store original Bluesky JSON documents.

> To speed up specific queries, we previously extracted and stored the event kind and event time as top-level columns and sorting keys. However, this is no longer necessary, as our JSON type now [supports](https://clickhouse.com/blog/clickhouse-release-24-12#json-subcolumns-as-table-primary-key) using JSON paths directly as sorting and primary key columns.


### How big is the dataset?

We began ingesting data in late December last year. As of March 2025, the table holds 4+ billion Bluesky event JSON documents, with a total uncompressed size exceeding 1.6 TiB:

<pre><code type='click-ui' language='sql' runnable='true' show_statistics='true' run='true' view='table' play_link='https://sql.clickhouse.com/?query=U0VMRUNUCiAgICBmb3JtYXRSZWFkYWJsZVF1YW50aXR5KHN1bShyb3dzKSkgQVMgZG9jcywKICAgIGZvcm1hdFJlYWRhYmxlU2l6ZShzdW0oZGF0YV91bmNvbXByZXNzZWRfYnl0ZXMpKSBBUyBkYXRhX3NpemUKRlJPTSBzeXN0ZW0ucGFydHMKV0hFUkUgYWN0aXZlIEFORCAoZGF0YWJhc2UgPSAnYmx1ZXNreScpIEFORCAoYHRhYmxlYCA9ICdibHVlc2t5Jyk7&run_query=true&tab=results'>
SELECT
    formatReadableQuantity(sum(rows)) AS docs,
    formatReadableSize(sum(data_uncompressed_bytes)) AS data_size
FROM system.parts
WHERE active AND (database = 'bluesky') AND (table = 'bluesky');
</code></pre>

Static result for the query above from March 2025:
<pre><code type='click-ui' language='text' show_line_numbers='false'>
┌─docs─────────┬─data_size─┐
│ 4.14 billion │ 1.61 TiB  │
└──────────────┴───────────┘
</code></pre>

### How fast is it growing?

Monthly, the table grows currently by ~1.5 billion documents:

<pre><code type='click-ui' language='sql' runnable='true' show_statistics='true' run='true'  view='chart' chart_config='eyJ0eXBlIjoiaG9yaXpvbnRhbCBiYXIiLCJjb25maWciOnsieGF4aXMiOiJtb250aCIsInlheGlzIjoiZG9jcyIsInRpdGxlIjoiSW5nZXN0ZWQgQmx1ZXNreSBldmVudHMgcGVyIG1vbnRoIn19' play_link='https://sql.clickhouse.com?query=U0VMRUNUCiAgICB0b1N0YXJ0T2ZNb250aChibHVlc2t5X3RzKSBBUyBtb250aCwKICAgIGNvdW50KCkgQVMgZG9jcwpGUk9NIGJsdWVza3kuYmx1ZXNreQpHUk9VUCBCWSBtb250aApPUkRFUiBCWSBtb250aCBERVNDCkxJTUlUIDEwClNFVFRJTkdTIGVuYWJsZV9wYXJhbGxlbF9yZXBsaWNhcz0xOw&chart=eyJ0eXBlIjoiaG9yaXpvbnRhbCBiYXIiLCJjb25maWciOnsieGF4aXMiOiJtb250aCIsInlheGlzIjoiZG9jcyIsInRpdGxlIjoiSW5nZXN0ZWQgQmx1ZXNreSBldmVudHMgcGVyIG1vbnRoIn19&run_query=true'>
SELECT
    toStartOfMonth(bluesky_ts) AS month,
    count() AS docs
FROM bluesky.bluesky
GROUP BY month
ORDER BY month DESC
LIMIT 10
SETTINGS enable_parallel_replicas=1;
</code></pre>

We began ingesting Bluesky event data in late December last year, so that month has a lower data volume compared to subsequent months. Additionally, February was a short month this year with only 28 days.

Daily, the table currently grows by ~50 million Bluesky events:

<pre><code type='click-ui' language='sql' runnable='true' show_statistics='true' run='true'  view='chart' chart_config='eyJ0eXBlIjoiaG9yaXpvbnRhbCBiYXIiLCJjb25maWciOnsieGF4aXMiOiJkYXkiLCJ5YXhpcyI6ImRvY3MiLCJ0aXRsZSI6IkluZ2VzdGVkIEJsdWVza3kgZXZlbnRzIHBlciBkYXkifX0' play_link='https://sql.clickhouse.com/?query=U0VMRUNUCiAgICB0b1N0YXJ0T2ZEYXkoYmx1ZXNreV90cykgQVMgZGF5LAogICAgY291bnQoKSBBUyBkb2NzCkZST00gYmx1ZXNreS5ibHVlc2t5CldIRVJFIGRheSA8IHRvU3RhcnRPZkRheShub3coKSkKR1JPVVAgQlkgZGF5Ck9SREVSIEJZIGRheSBERVNDCkxJTUlUIDEwClNFVFRJTkdTIGVuYWJsZV9wYXJhbGxlbF9yZXBsaWNhcz0xOw&chart=eyJ0eXBlIjoiaG9yaXpvbnRhbCBiYXIiLCJjb25maWciOnsieGF4aXMiOiJkYXkiLCJ5YXhpcyI6ImRvY3MiLCJ0aXRsZSI6IkluZ2VzdGVkIEJsdWVza3kgZXZlbnRzIHBlciBkYXkifX0&run_query=true&tab=charts'>
SELECT
    toStartOfDay(bluesky_ts) AS day,
    count() AS docs
FROM bluesky.bluesky
WHERE day < toStartOfDay(now())
GROUP BY day
ORDER BY day DESC
LIMIT 10
SETTINGS enable_parallel_replicas=1;
</code></pre>


> This rapid growth means that without the right optimizations, queries will inevitably slow down. 

So how do we sustain real-time performance, no matter the dataset size and growth rate? Read on...

## Test all queries live!

Or let this blog run them for you.

Every Bluesky table, acceleration technique, and query from this blog is available in our [ClickHouse SQL playground](https://clickhouse.com/blog/announcing-the-new-sql-playground), where you can explore and run every example yourself.

In fact, every query in this blog **runs live** in the playground, allowing you to see results in real-time as you read.

> Our public ClickHouse SQL playground [enforces](https://clickhouse.com/blog/announcing-the-new-sql-playground#running-cost-efficient-demo-playgrounds) quotas, access control, and [query complexity limits](https://clickhouse.com/docs/operations/settings/query-complexity) to ensure fair usage and prevent resource monopolization. As a result, expensive queries will hit execution restrictions. <br/><br/>To provide complete and accurate execution statistics, we ran some queries for this blog using an unrestricted admin user connected to the ClickHouse Cloud playground service via [clickhouse-client](https://clickhouse.com/docs/interfaces/cli).

## Our ClickHouse hardware setup

Our ClickHouse SQL playground [runs](https://clickhouse.com/blog/announcing-the-new-sql-playground#running-cost-efficient-demo-playgrounds) on a ClickHouse Cloud service with at least three compute nodes, each equipped with **59 CPU cores** and **236 GiB RAM**. While the cluster ensures high availability and scalability, **each dashboard query in this post runs on a single node**, as we did not enable ClickHouse Cloud’s [parallel replicas](https://clickhouse.com/docs/deployment-guides/parallel-replicas). Apart from ClickHouse Cloud using shared object storage, this makes the performance results directly comparable to what can be achieved on a standalone ClickHouse instance with similar CPU and RAM.

In the rest of this post, we’ll show you how to achieve guaranteed instantaneous (<100ms) ClickHouse query response times on this hardware—no matter how many billions of JSON documents are stored in the Bluesky table. We’ll walk through three real-time dashboard scenarios, applying proven acceleration techniques step by step.


## Dashboard 1: Tracking Bluesky activity trends

![Blog-bluesky-faster.003.png](https://clickhouse.com/uploads/Blog_bluesky_faster_003_0f12566d3d.png)


Our first scenario is a real-time dashboard [showing](https://sql.clickhouse.com?query=U0VMRUNUIGV2ZW50LCBob3VyX29mX2RheSwgc3VtKGNvdW50KSBhcyBjb3VudApGUk9NIGJsdWVza3kuZXZlbnRzX3Blcl9ob3VyX29mX2RheQpXSEVSRSBldmVudCBpbiBbCiAgICAnYXBwLmJza3kuZmVlZC5wb3N0JywKICAgICdhcHAuYnNreS5mZWVkLnJlcG9zdCcsCiAgICAnYXBwLmJza3kuZmVlZC5saWtlJ10KR1JPVVAgQlkgZXZlbnQsIGhvdXJfb2ZfZGF5Ck9SREVSIEJZIGhvdXJfb2ZfZGF5Ow&chart=eyJ0eXBlIjoiYmFyIiwiY29uZmlnIjp7InRpdGxlIjoiTnVtYmVyIG9mIGV2ZW50cyBwZXIgaG91ciBvZiBkYXkiLCJ4YXhpcyI6ImhvdXJfb2ZfZGF5IiwieWF4aXMiOiJjb3VudCIsInNlcmllcyI6ImV2ZW50Iiwic3RhY2siOmZhbHNlfX0&chart=eyJ0eXBlIjoiYmFyIiwiY29uZmlnIjp7InRpdGxlIjoiTnVtYmVyIG9mIGV2ZW50cyBwZXIgaG91ciBvZiBkYXkiLCJ4YXhpcyI6ImhvdXJfb2ZfZGF5IiwieWF4aXMiOiJjb3VudCIsInNlcmllcyI6ImV2ZW50Iiwic3RhY2siOmZhbHNlfX0&run_query=true&tab=charts) the most popular Bluesky event types by hour—essentially visualizing when people are active on Bluesky during the day.


### Baseline query: counting events by hour (44s)

A potential query powering this dashboard calculates the most popular Bluesky event types using a `count` aggregation across the complete Bluesky dataset:

<pre><code type='click-ui' language='sql' runnable='true' show_statistics='true' run='false'  view='table'  play_link='https://sql.clickhouse.com/?query=U0VMRUNUCiAgICBkYXRhLmNvbW1pdC5jb2xsZWN0aW9uIEFTIGV2ZW50LAogICAgdG9Ib3VyKGJsdWVza3lfdHMpIEFTIGhvdXJfb2ZfZGF5LAogICAgY291bnQoKSBBUyBjb3VudApGUk9NIGJsdWVza3kuYmx1ZXNreQpXSEVSRSBraW5kID0gJ2NvbW1pdCcKICBBTkQgZXZlbnQgaW4gWwogICAgJ2FwcC5ic2t5LmZlZWQucG9zdCcsCiAgICAnYXBwLmJza3kuZmVlZC5yZXBvc3QnLCAKICAgICdhcHAuYnNreS5mZWVkLmxpa2UnXQpHUk9VUCBCWSBldmVudCwgaG91cl9vZl9kYXk7&tab=results'>
 SELECT
    data.commit.collection AS event,
    toHour(bluesky_ts) AS hour_of_day,
    count() AS count
FROM bluesky.bluesky
WHERE kind = 'commit'
  AND event in [
    'app.bsky.feed.post',
    'app.bsky.feed.repost',
    'app.bsky.feed.like']
GROUP BY event, hour_of_day;
</code></pre>

⚠️ Pressing ▶️ for the query above won’t get you far because it most likely exceeds the max runtime limits and query complexity restrictions [enforced](/blog/accelerating-clickhouse-json-queries-for-fast-bluesky-dashboards#test-all-queries-live) by our public playground.

Execution statistics from running the query via `clickhouse-client` without playground quotas or restrictions:
<pre><code type='click-ui' language='text' show_line_numbers='false'>
Elapsed: 44.901 sec. Processed 4.12 billion rows, 189.18 GB (91.84 million rows/s., 4.21 GB/s.)
Peak memory usage: 775.96 MiB.
</code></pre>


The query runs in 44 seconds (and consumes 776 MiB of memory) which is way too slow for a responsive dashboard.

<div style="padding: 12px; border: 1px solid #323232; border-radius: 5px; background-color: #2E2E2D; color: white; font-family: Arial, sans-serif; line-height: 1.4;">
  <p style="color: #FF0000; font-weight: bold; margin-bottom: 4px;">&gt;2s (too slow) <span style="color: white; font-weight: normal;">— Feels unresponsive. Users lose focus.</span></p>
</div>

<br/>

> ClickHouse processes the Bluesky JSON data with the aggregation query above thousands of times [faster](/blog/json-bench-clickhouse-vs-mongodb-elasticsearch-duckdb-postgresql#aggregation-performance-of-query--2) than other leading JSON data stores. On our [hardware](/blog/accelerating-clickhouse-json-queries-for-fast-bluesky-dashboards#our-clickhouse-hardware-setup), it achieves a throughput of 91.84 million docs per second (4.21 GB/s).

The sheer amount of data (4+ billion documents, constantly growing) prevents achieving a sub-100ms response directly. Instead of scanning billions of rows on every query, what if we could pre-aggregate the data as new events arrive? That’s where incremental materialized views come in.

### How incremental aggregation unlocks speed

To achieve instantaneous responses, we need to incrementally pre-aggregate the data in real-time—continuously updating aggregates as new Bluesky events arrive:

![Blog-bluesky-faster.004.png](https://clickhouse.com/uploads/Blog_bluesky_faster_004_b76e83ba6a.png)

We store and update pre-aggregated data in the table  ① `events_per_hour_of_day`, which ③ powers our example dashboard. An ② incremental materialized view ensures that this table remains continuously updated as new data arrives in the source table.

> [Incremental aggregation](https://clickhouse.com/blog/clickhouse_vs_elasticsearch_mechanics_of_count_aggregations#clickhouse-3) using materialized views is highly resource efficient, particularly when source tables contain billions or even trillions of rows. Rather than recalculating aggregates from the entire dataset every time new data arrives, ClickHouse efficiently computes [partial aggregation states](https://clickhouse.com/blog/clickhouse_vs_elasticsearch_mechanics_of_count_aggregations#-multi-core-parallelization) from **only newly inserted rows**, incrementally [merging](https://clickhouse.com/docs/merges#aggregating-merges) these states with existing aggregates in the background.

Here’s the DDL statement defining the `events_per_hour_of_day` table, which stores our pre-aggregated data:
<pre>
<code type='click-ui' language='sql'>
CREATE TABLE bluesky.events_per_hour_of_day
(
    event LowCardinality(String),
    hour_of_day UInt8,
    count SimpleAggregateFunction(sum, UInt64)
)
ENGINE = AggregatingMergeTree
ORDER BY (event, hour_of_day);
</code>
</pre>

This is the incremental materialized view definition. At its core is a transformation query that’s triggered whenever new rows arrive in the Bluesky dataset. The query pre-aggregates incoming rows and inserts the results into the `events_per_hour_of_day` target table, where ClickHouse incrementally continues the aggregation through [background merges](https://clickhouse.com/docs/merges#aggregating-merges):
<pre>
<code type='click-ui' language='sql'>
CREATE MATERIALIZED VIEW bluesky.events_per_hour_of_day_mv
TO bluesky.events_per_hour_of_day
AS SELECT
    data.commit.collection::String AS event,
    toHour(bluesky_ts) as hour_of_day,
    count() AS count
FROM bluesky.bluesky
WHERE (kind = 'commit')
GROUP BY event, hour_of_day;
</code>
</pre>

### Storage impact of pre-aggregation


Let’s check the size of the `events_per_hour_of_day` target table when its data is fully in sync with the 4+ billion-row Bluesky dataset—either through real-time updates or via [backfilling](https://clickhouse.com/docs/data-modeling/backfilling) if materialized views were added to an existing table:

<pre><code type='click-ui' language='sql' runnable='true' show_statistics='true' run='true' view='table' play_link='https://sql.clickhouse.com/?query=U0VMRUNUCiAgICBmb3JtYXRSZWFkYWJsZVF1YW50aXR5KHN1bShyb3dzKSkgQVMgcm93cywKICAgIGZvcm1hdFJlYWRhYmxlU2l6ZShzdW0oZGF0YV91bmNvbXByZXNzZWRfYnl0ZXMpKSBBUyBkYXRhX3NpemUKRlJPTSBzeXN0ZW0ucGFydHMKV0hFUkUgYWN0aXZlIEFORCAoZGF0YWJhc2UgPSAnYmx1ZXNreScpIEFORCAoYHRhYmxlYCA9ICdldmVudHNfcGVyX2hvdXJfb2ZfZGF5Jyk7Cg&chart=eyJ0eXBlIjoiYmFyIiwiY29uZmlnIjp7InRpdGxlIjoiTnVtYmVyIG9mIGV2ZW50cyBwZXIgaG91ciBvZiBkYXkiLCJ4YXhpcyI6ImhvdXJfb2ZfZGF5IiwieWF4aXMiOiJjb3VudCIsInNlcmllcyI6ImV2ZW50Iiwic3RhY2siOmZhbHNlfX0&run_query=true&tab=results'>
SELECT
    formatReadableQuantity(sum(rows)) AS rows,
    formatReadableSize(sum(data_uncompressed_bytes)) AS data_size
FROM system.parts
WHERE active AND (database = 'bluesky') AND (table = 'events_per_hour_of_day');
</code></pre>

Static result for the query above from March 2025:
<pre><code type='click-ui' language='text' show_line_numbers='false'>
┌─rows───┬─data_size─┐
│ 892.00 │ 11.24 KiB │
└────────┴───────────┘
</code></pre>

As you can see, the table containing the pre-aggregated data is drastically smaller than the full Bluesky dataset table, in both row count and (uncompressed) total data size.

> **The size of pre-aggregated data remains independent of the source table**: The materialized view updates its target table in real-time as new data arrives. However, once fully [merged](https://clickhouse.com/docs/merges#aggregating-merges), its row count and total size stay constant—regardless of how much the complete Bluesky dataset grows.

This property is key—it guarantees instantaneous (<100ms) ClickHouse query response times. Why? Because the maximum* fully merged size of the materialized view’s target table depends only on the number of unique Bluesky events ([currently](https://sql.clickhouse.com?query=U0VMRUNUCiAgZXZlbnQsCiAgc3VtKGNvdW50KSBBUyBjb3VudCwKICB1bmlxTWVyZ2UodXNlcnMpIEFTIHVzZXJzCkZST00gYmx1ZXNreS50b3BfZXZlbnRfdHlwZXMKR1JPVVAgQlkgZXZlbnQKT1JERVIgQlkgY291bnQgREVTQzs&chart=eyJ0eXBlIjoibGluZSIsImNvbmZpZyI6eyJ4YXhpcyI6InllYXIiLCJ5YXhpcyI6Ijk5dGhfYXZnX3RlbXAiLCJzZXJpZXMiOiJjb3VudHJ5IiwidGl0bGUiOiJUZW1wZXJhdHVyZSBieSBjb3VudHJ5IGFuZCB5ZWFyIn19&run_query=true&tab=results) 109), multiplied by 24 hours in a day—not on the overall and ever-growing size of the full Bluesky dataset.

Since the data size stays stable, the optimized query’s runtime remains stable too!

*Not all events occur in every hour of the day.

### Achieving 6ms query performance

Now we can run the query from above over the `events_per_hour_of_day` table with pre-aggregated data:
<pre><code type='click-ui' language='sql' runnable='true' show_statistics='true' run='true'  view='chart' chart_config='eyJ0eXBlIjoiYmFyIiwiY29uZmlnIjp7InRpdGxlIjoiTnVtYmVyIG9mIGV2ZW50cyBwZXIgaG91ciBvZiBkYXkiLCJ4YXhpcyI6ImhvdXJfb2ZfZGF5IiwieWF4aXMiOiJjb3VudCIsInNlcmllcyI6ImV2ZW50Iiwic3RhY2siOmZhbHNlfX0' play_link='https://sql.clickhouse.com?query=U0VMRUNUIGV2ZW50LCBob3VyX29mX2RheSwgc3VtKGNvdW50KSBhcyBjb3VudApGUk9NIGJsdWVza3kuZXZlbnRzX3Blcl9ob3VyX29mX2RheQpXSEVSRSBldmVudCBpbiBbCiAgICAnYXBwLmJza3kuZmVlZC5wb3N0JywKICAgICdhcHAuYnNreS5mZWVkLnJlcG9zdCcsCiAgICAnYXBwLmJza3kuZmVlZC5saWtlJ10KR1JPVVAgQlkgZXZlbnQsIGhvdXJfb2ZfZGF5Ck9SREVSIEJZIGhvdXJfb2ZfZGF5Ow&chart=eyJ0eXBlIjoiYmFyIiwiY29uZmlnIjp7InRpdGxlIjoiTnVtYmVyIG9mIGV2ZW50cyBwZXIgaG91ciBvZiBkYXkiLCJ4YXhpcyI6ImhvdXJfb2ZfZGF5IiwieWF4aXMiOiJjb3VudCIsInNlcmllcyI6ImV2ZW50Iiwic3RhY2siOmZhbHNlfX0&run_query=true&tab=charts'>
SELECT event, hour_of_day, sum(count) as count
FROM bluesky.events_per_hour_of_day
WHERE event in [
    'app.bsky.feed.post',
    'app.bsky.feed.repost',
    'app.bsky.feed.like']
GROUP BY event, hour_of_day
ORDER BY hour_of_day;
</code></pre>

Execution statistics queried via [unrestricted](/blog/accelerating-clickhouse-json-queries-for-fast-bluesky-dashboards#test-all-queries-live) `clickhouse-client`:
<pre>
<code type='click-ui' language='text' show_line_numbers='false'>
Elapsed: 0.006 sec.
</code>
</pre>


Now, the query runs in just 6 milliseconds instead of 44 seconds—well within our <100ms “snappy” threshold. Since its input table is continuously updated by an incremental materialized view, it always operates on the latest data while maintaining a constant runtime, regardless of the base table’s growth.


<div style="padding: 12px; border: 1px solid #323232; border-radius: 5px; background-color: #2E2E2D; color: white; font-family: Arial, sans-serif; line-height: 1.4;">
  <p style="color: #00FF00; font-weight: bold; margin-bottom: 4px;">&lt;100ms (instant) <span style="color: white; font-weight: normal;">— Feels instant, ideal for filtering or quick updates.</span></p>
</div>


### How much memory does it use? (186KiB vs 776 MiB)

To understand the efficiency of our approach, let’s break down how data flows from raw JSON ingestion to a real-time dashboard query. The diagram below illustrates this process, followed by a detailed look at memory usage across each stage.

![Blog-bluesky-faster-v3.003.png](https://clickhouse.com/uploads/Blog_bluesky_faster_v3_003_fca9db8d35.png)

| **Metric**         | **Baseline query**                                                          | **① Incremental MV**                                                                    | **② Optimized query**                                                       |
|--------------------|-----------------------------------------------------------------------------|-----------------------------------------------------------------------------------------|-----------------------------------------------------------------------------|
| **Memory usage**   | 775.96 MiB                                                                  | 314.74 MiB                                                                              | 186.15 KiB                                                                  |
| **Rows processed** | 4.12 billion                                                                | ~646.76k per update                                                                     | 892 rows                                                                    |
| **Duration**       | 44.9 sec                                                                    | ~998 ms per update                                                                      | Instantaneous                                                               |
| **Metrics source** | [Execution statistics](/blog/accelerating-clickhouse-json-queries-for-fast-bluesky-dashboards#baseline-query-counting-events-by-hour-44s) | [Query views log](https://gist.github.com/tom-clickhouse/564538c9170e1c85654947c37b80f80c) | [Query log](https://gist.github.com/tom-clickhouse/6168828baf620ae6c7a23da3968cba1e) |


The final query runs with just **186 KiB of memory**, a dramatic reduction from the **775.96 MiB** used by the baseline query. Even when factoring in the **314 MiB** used by the incremental materialized view to process new rows, the total memory footprint remains well below the baseline—ensuring real-time performance at scale.

> This demonstrates how incremental pre-aggregation drastically reduces both query latency and resource consumption while ensuring the dashboard remains responsive at scale.


## Dashboard 2: Ranking the most popular Bluesky events

![Blog-bluesky-faster.005.png](https://clickhouse.com/uploads/Blog_bluesky_faster_005_6e198707f6.png)

Our second scenario is a real-time dashboard [showing](https://sql.clickhouse.com?query=U0VMRUNUCiAgZXZlbnQsCiAgc3VtKGNvdW50KSBBUyBjb3VudCwKICB1bmlxTWVyZ2UodXNlcnMpIEFTIHVzZXJzCkZST00gYmx1ZXNreS50b3BfZXZlbnRfdHlwZXMKR1JPVVAgQlkgZXZlbnQKT1JERVIgQlkgY291bnQgREVTQzs&chart=eyJ0eXBlIjoibGluZSIsImNvbmZpZyI6eyJ4YXhpcyI6InllYXIiLCJ5YXhpcyI6Ijk5dGhfYXZnX3RlbXAiLCJzZXJpZXMiOiJjb3VudHJ5IiwidGl0bGUiOiJUZW1wZXJhdHVyZSBieSBjb3VudHJ5IGFuZCB5ZWFyIn19&run_query=true&tab=results) the most frequent Bluesky event types with the count of unique users per event type.


### Baseline query: counting unique users (56s)

We run a potential dashboard query over the full Bluesky dataset, extending the count aggregation (as used in the dashboard 1 query) with a `uniq` aggregation. This annotates each event not only with its total occurrence but also with the number of unique users:

<pre><code type='click-ui' language='sql' runnable='true' show_statistics='true' run='false'  view='table'  play_link='https://sql.clickhouse.com/?query=U0VMRUNUCiAgICBkYXRhLmNvbW1pdC5jb2xsZWN0aW9uIEFTIGV2ZW50LAogICAgY291bnQoKSBBUyBjb3VudCwKICAgIHVuaXEoZGF0YS5kaWQpIEFTIHVzZXJzCkZST00gYmx1ZXNreS5ibHVlc2t5CldIRVJFIGtpbmQgPSAnY29tbWl0JwpHUk9VUCBCWSBldmVudApPUkRFUiBCWSBjb3VudCBERVNDOw&chart=eyJ0eXBlIjoibGluZSIsImNvbmZpZyI6eyJ4YXhpcyI6InllYXIiLCJ5YXhpcyI6Ijk5dGhfYXZnX3RlbXAiLCJzZXJpZXMiOiJjb3VudHJ5IiwidGl0bGUiOiJUZW1wZXJhdHVyZSBieSBjb3VudHJ5IGFuZCB5ZWFyIn19&tab=results'>
SELECT
    data.commit.collection AS event,
    count() AS count,
    uniq(data.did) AS users
FROM bluesky.bluesky
WHERE kind = 'commit'
GROUP BY event
ORDER BY count DESC;
</code></pre>

Execution statistics queried via [unrestricted](/blog/accelerating-clickhouse-json-queries-for-fast-bluesky-dashboards#test-all-queries-live) `clickhouse-client`:
<pre>
<code type='click-ui' language='text' show_line_numbers='false'>
Elapsed: 55.966 sec. Processed 4.41 billion rows, 387.45 GB (78.80 million rows/s., 6.92 GB/s.)
Peak memory usage: 1000.24 MiB.
</code>
</pre>


<div style="padding: 12px; border: 1px solid #323232; border-radius: 5px; background-color: #2E2E2D; color: white; font-family: Arial, sans-serif; line-height: 1.4;">
  <p style="color: #FF0000; font-weight: bold; margin-bottom: 4px;">&gt;2s (too slow) <span style="color: white; font-weight: normal;">— Feels unresponsive. Users lose focus.</span></p>
</div>

<br/>

At 56 seconds, this query is far too slow for a responsive dashboard. A more efficient approach is needed to keep query times low as data grows. Instead of scanning billions of rows on demand, we pre-aggregate and maintain an optimized table for real-time analytics.

### From slow queries to real-time analytics

Similar to the first dashboard, We store and update pre-aggregated data in an additional table  ① `top_event_types`, which ③ powers our second example dashboard. An ② incremental materialized view ensures that this table remains continuously updated as new data arrives in the source table:

![Blog-bluesky-faster.006.png](https://clickhouse.com/uploads/Blog_bluesky_faster_006_0519dc5848.png)

Here’s the DDL statement for the `top_event_types` table, where we store the pre-aggregated results:
<pre>
<code type='click-ui' language='sql'>
CREATE TABLE bluesky.top_event_types
(
	event LowCardinality(String),
	count SimpleAggregateFunction(sum, UInt64),
	users AggregateFunction(uniq, String)
)
ENGINE = AggregatingMergeTree
ORDER BY event;
</code>
</pre>

This is DDL for the incremental materialized view sending pre-aggregated data to the `top_event_types` table:
<pre>
<code type='click-ui' language='sql'>
CREATE MATERIALIZED VIEW bluesky.top_event_types_mv 
TO bluesky.top_event_types
AS
SELECT
  data.commit.collection::String AS event,
  count() AS count,
  uniqState(data.did::String) AS users
FROM bluesky.bluesky
WHERE kind = 'commit'
GROUP BY event;
</code>
</pre>

### How much space do the aggregates take?

We check the size of the `top_event_types` target table when its data is fully in sync with the 4+ billion rows full Bluesky dataset table:

<pre><code type='click-ui' language='sql' runnable='true' show_statistics='true' run='true' view='table' play_link='https://sql.clickhouse.com?query=U0VMRUNUCiAgICBmb3JtYXRSZWFkYWJsZVF1YW50aXR5KHN1bShyb3dzKSkgQVMgcm93cywKICAgIGZvcm1hdFJlYWRhYmxlU2l6ZShzdW0oZGF0YV91bmNvbXByZXNzZWRfYnl0ZXMpKSBBUyBkYXRhX3NpemUKRlJPTSBzeXN0ZW0ucGFydHMKV0hFUkUgYWN0aXZlIEFORCAoZGF0YWJhc2UgPSAnYmx1ZXNreScpIEFORCAodGFibGUgPSAndG9wX2V2ZW50X3R5cGVzJyk7Cg&chart=eyJ0eXBlIjoiYmFyIiwiY29uZmlnIjp7InRpdGxlIjoiTnVtYmVyIG9mIGV2ZW50cyBwZXIgaG91ciBvZiBkYXkiLCJ4YXhpcyI6ImhvdXJfb2ZfZGF5IiwieWF4aXMiOiJjb3VudCIsInNlcmllcyI6ImV2ZW50Iiwic3RhY2siOmZhbHNlfX0&run_query=true&tab=results'>
SELECT
    formatReadableQuantity(sum(rows)) AS rows,
    formatReadableSize(sum(data_uncompressed_bytes)) AS data_size
FROM system.parts
WHERE active AND (database = 'bluesky') AND (table = 'top_event_types');
</code></pre>

Static result for the query above from March 2025:
<pre>
<code type='click-ui' language='text' show_line_numbers='false'>
┌─rows───┬─data_size─┐
│ 109.00 │ 2.27 MiB  │
└────────┴───────────┘
</code>
</pre>


> **The size of pre-aggregated data remains independent of the source table**: Again, the (fully merged) target table’s size and row count remain constant, independent of the growth of the total Bluesky dataset size. It depends solely on the number of unique Bluesky events ([currently](https://sql.clickhouse.com?query=U0VMRUNUCiAgZXZlbnQsCiAgc3VtKGNvdW50KSBBUyBjb3VudCwKICB1bmlxTWVyZ2UodXNlcnMpIEFTIHVzZXJzCkZST00gYmx1ZXNreS50b3BfZXZlbnRfdHlwZXMKR1JPVVAgQlkgZXZlbnQKT1JERVIgQlkgY291bnQgREVTQzs&chart=eyJ0eXBlIjoibGluZSIsImNvbmZpZyI6eyJ4YXhpcyI6InllYXIiLCJ5YXhpcyI6Ijk5dGhfYXZnX3RlbXAiLCJzZXJpZXMiOiJjb3VudHJ5IiwidGl0bGUiOiJUZW1wZXJhdHVyZSBieSBjb3VudHJ5IGFuZCB5ZWFyIn19&run_query=true&tab=results) 109).

Again, this property ensures instantaneous (&lt;100ms) ClickHouse query response times, regardless of the overall and constantly growing size of the complete Bluesky dataset.


### Final optimized query: 7ms response time

We run the query from above over the `top_event_types` table with pre-aggregated data:

<pre><code type='click-ui' language='sql' runnable='true' show_statistics='true' run='true'  view='table'  play_link='https://sql.clickhouse.com?query=U0VMRUNUCiAgZXZlbnQsCiAgc3VtKGNvdW50KSBBUyBjb3VudCwKICB1bmlxTWVyZ2UodXNlcnMpIEFTIHVzZXJzCkZST00gYmx1ZXNreS50b3BfZXZlbnRfdHlwZXMKR1JPVVAgQlkgZXZlbnQKT1JERVIgQlkgY291bnQgREVTQzs&chart=eyJ0eXBlIjoibGluZSIsImNvbmZpZyI6eyJ4YXhpcyI6InllYXIiLCJ5YXhpcyI6Ijk5dGhfYXZnX3RlbXAiLCJzZXJpZXMiOiJjb3VudHJ5IiwidGl0bGUiOiJUZW1wZXJhdHVyZSBieSBjb3VudHJ5IGFuZCB5ZWFyIn19&run_query=true&tab=results'>
SELECT
  event,
  sum(count) AS count,
  uniqMerge(users) AS users
FROM bluesky.top_event_types
GROUP BY event
ORDER BY count DESC;
</code></pre>

Execution statistics queried via [unrestricted](/blog/accelerating-clickhouse-json-queries-for-fast-bluesky-dashboards#test-all-queries-live) `clickhouse-client`:
<pre>
<code type='click-ui' language='text' show_line_numbers='false'>
Elapsed: 0.007 sec.
</code>
</pre>


The query completes in 7 milliseconds, instead of taking 56 seconds.

<div style="padding: 12px; border: 1px solid #323232; border-radius: 5px; background-color: #2E2E2D; color: white; font-family: Arial, sans-serif; line-height: 1.4;">
  <p style="color: #00FF00; font-weight: bold; margin-bottom: 4px;">&lt;100ms (instant) <span style="color: white; font-weight: normal;">— Feels instant, ideal for filtering or quick updates.</span></p>
</div>


### Memory consumption of the optimized query (16 MiB vs 1 GiB)

To quantify the efficiency of our approach, the table below compares memory usage at each stage—showing how incremental materialized views dramatically reduce query overhead.

![Blog-bluesky-faster-v3.006.png](https://clickhouse.com/uploads/Blog_bluesky_faster_v3_006_ffef95ed04.png)

| **Metric**         | **Baseline query**                                                          | **① Incremental MV**                                                                    | **② Optimized query**                                                       |
|--------------------|-----------------------------------------------------------------------------|-----------------------------------------------------------------------------------------|-----------------------------------------------------------------------------|
| **Memory usage**   | 1 GiB                                                                       | 276.47 MiB                                                                             | 16.58 MiB                                                                   |
| **Rows processed** | Full dataset                                                                | ~571.42k per update                                                                     | 109 rows                                                                    |
| **Duration**       | 56 sec                                                                      | ~746 ms per update                                                                      | Instantaneous                                                               |
| **Metrics source** | [Execution statistics](/blog/accelerating-clickhouse-json-queries-for-fast-bluesky-dashboards#baseline-query-counting-unique-users-56s) | [Query views log](https://gist.github.com/tom-clickhouse/ee2ebbd5868fc99e1ff03439b76a7043) | [Query log](https://gist.github.com/tom-clickhouse/7bc8ba48b32b1c4bd39a97a4d8971b79) |

The optimized query consumes just **16 MiB** of memory, a sharp contrast to the **1 GiB** used by the baseline query. Even when factoring in the **276 MiB** required by the incremental materialized view to process new rows, the total memory footprint remains significantly lower—ensuring fast, efficient real-time analytics.

> Once again, incremental pre-aggregation minimizes memory usage while maintaining low query latency, making large-scale JSON analytics highly efficient.


## Dashboard 3: Discovering the most reposted Bluesky posts

![Blog-bluesky-faster.007.png](https://clickhouse.com/uploads/Blog_bluesky_faster_007_2b5f4e1e16.png)

Our third scenario is a real-time dashboard [highlighting](https://sql.clickhouse.com?query=U0VMRUNUICoKRlJPTSBibHVlc2t5LnJlcG9zdHNfcGVyX3Bvc3RfdG9wMTBfdjIKT1JERVIgQlkgcmVwb3N0cyBERVNDOw&chart=eyJ0eXBlIjoiYmFyIiwiY29uZmlnIjp7InRpdGxlIjoiTnVtYmVyIG9mIGV2ZW50cyBwZXIgaG91ciBvZiBkYXkiLCJ4YXhpcyI6ImhvdXJfb2ZfZGF5IiwieWF4aXMiOiJjb3VudCIsInNlcmllcyI6ImV2ZW50Iiwic3RhY2siOmZhbHNlfX0&run_query=true&tab=results) the most reposted Bluesky posts.

### Challenges in identifying reposts efficiently

At first glance, identifying the most reposted Bluesky posts seems simple. However, this dashboard introduces some key challenges:

- **Repost events don’t contain post content**: They only store the [CID](https://blueskydirectory.com/glossary/cid) (Content Identifier) of the original post—without text:

![Blog-bluesky-faster.001.png](https://clickhouse.com/uploads/Blog_bluesky_faster_001_4295ba4b79.png)

- **Counting reposts is expensive**: To compute the number of reposts per post, we must aggregate on the high-cardinality `cid` JSON path, which slows queries.

- **Posts don’t contain user handles**: BLuesky event JSON documents track only the [DID](https://blueskydirectory.com/glossary/cid) (Decentralized Identifier) of users—not their actual username or handle:

![Blog-bluesky-faster.001.png](https://clickhouse.com/uploads/Blog_bluesky_faster_001_80577d40e2.png)

Before solving these problems, let’s look at a baseline query to find the most reposted posts.



### Why repost queries are slow  (baseline: 37s execution time)


Before we address these aforementioned issues—enriching most reposted posts with content and mapping DIDs to user handles—let’s start with a basic query to retrieve the top 10 most reposted posts:

<pre><code type='click-ui' language='sql' runnable='true' show_statistics='true' run='false'  view='table'  play_link='https://sql.clickhouse.com?query=U0VMRUNUCiAgICBkYXRhLmNvbW1pdC5yZWNvcmQuc3ViamVjdC5jaWQgQVMgY2lkLAogICAgY291bnQoKSBBUyByZXBvc3RzCkZST00gYmx1ZXNreS5ibHVlc2t5CldIRVJFIGRhdGEuY29tbWl0LmNvbGxlY3Rpb24gPSAnYXBwLmJza3kuZmVlZC5yZXBvc3QnCkdST1VQIEJZIGNpZApPUkRFUiBCWSBjaWQgREVTQwpMSU1JVCAxMDs&chart=eyJ0eXBlIjoiYmFyIiwiY29uZmlnIjp7InRpdGxlIjoiTnVtYmVyIG9mIGV2ZW50cyBwZXIgaG91ciBvZiBkYXkiLCJ4YXhpcyI6ImhvdXJfb2ZfZGF5IiwieWF4aXMiOiJjb3VudCIsInNlcmllcyI6ImV2ZW50Iiwic3RhY2siOmZhbHNlfX0&tab=results'>
SELECT
    data.commit.record.subject.cid AS cid,
    count() AS reposts
FROM bluesky.bluesky
WHERE data.commit.collection = 'app.bsky.feed.repost'
GROUP BY cid
ORDER BY cid DESC
LIMIT 10;
</code></pre>

Execution statistics queried via [unrestricted](/blog/accelerating-clickhouse-json-queries-for-fast-bluesky-dashboards#test-all-queries-live) `clickhouse-client`:
<pre>
<code type='click-ui' language='text' show_line_numbers='false'>
Elapsed: 37.234 sec. Processed 4.14 billion rows, 376.91 GB (111.26 million rows/s., 10.12 GB/s.)
Peak memory usage: 45.43 GiB.
</code>
</pre>

<div style="padding: 12px; border: 1px solid #323232; border-radius: 5px; background-color: #2E2E2D; color: white; font-family: Arial, sans-serif; line-height: 1.4;">
  <p style="color: #FF0000; font-weight: bold; margin-bottom: 4px;">&gt;2s (too slow) <span style="color: white; font-weight: normal;">— Feels unresponsive. Users lose focus.</span></p>
</div>

<br/>

Clearly, this approach is too slow. Aggregating on the high-cardinality `cid` JSON path results in a 37-second query and 45 GiB of memory usage—far from usable for real-time dashboards. To make repost lookups efficient, we need a better strategy. The first step is pre-aggregating repost counts


## Accelerating repost queries for real-time insights


As usual, we store and update pre-aggregated data in an additional table, ① `reposts_per_post`, which serves as ③ input for the dashboard query. An ② incremental materialized view ensures this table remains continuously updated as new data arrives in the source table:

![Blog-bluesky-faster.008.png](https://clickhouse.com/uploads/Blog_bluesky_faster_008_30bd4845a1.png)


Below are the DDL statements for the `reposts_per_post` table and its associated incremental materialized view:

<pre>
<code type='click-ui' language='sql'>
CREATE TABLE bluesky.reposts_per_post
(
    cid String,
    reposts SimpleAggregateFunction(sum, UInt64)
)
ENGINE = AggregatingMergeTree
ORDER BY (cid);
</code>
</pre>

<pre>
<code type='click-ui' language='sql'>
CREATE MATERIALIZED VIEW bluesky.reposts_per_post_mv TO bluesky.reposts_per_post
AS 
SELECT
    data.commit.record.subject.cid::String AS cid,
    count() AS reposts
FROM bluesky.bluesky
WHERE data.commit.collection = 'app.bsky.feed.repost'
GROUP BY cid;
</code>
</pre>

### Measuring pre-aggregated data size

We check the size of the `reposts_per_post` target table when its data is fully in sync with the 4+ billion rows full Bluesky dataset table:
<pre><code type='click-ui' language='sql' runnable='true' show_statistics='true' run='true' view='table' play_link='https://sql.clickhouse.com?query=U0VMRUNUCiAgICBmb3JtYXRSZWFkYWJsZVF1YW50aXR5KHN1bShyb3dzKSkgQVMgcm93cywKICAgIGZvcm1hdFJlYWRhYmxlU2l6ZShzdW0oZGF0YV91bmNvbXByZXNzZWRfYnl0ZXMpKSBBUyBkYXRhX3NpemUKRlJPTSBzeXN0ZW0ucGFydHMKV0hFUkUgYWN0aXZlIEFORCAoZGF0YWJhc2UgPSAnYmx1ZXNreScpIEFORCAodGFibGUgPSAncmVwb3N0c19wZXJfcG9zdCcpOw&chart=eyJ0eXBlIjoiYmFyIiwiY29uZmlnIjp7InRpdGxlIjoiTnVtYmVyIG9mIGV2ZW50cyBwZXIgaG91ciBvZiBkYXkiLCJ4YXhpcyI6ImhvdXJfb2ZfZGF5IiwieWF4aXMiOiJjb3VudCIsInNlcmllcyI6ImV2ZW50Iiwic3RhY2siOmZhbHNlfX0&run_query=true&tab=results'>
SELECT
    formatReadableQuantity(sum(rows)) AS rows,
    formatReadableSize(sum(data_uncompressed_bytes)) AS data_size
FROM system.parts
WHERE active AND (database = 'bluesky') AND (table = 'reposts_per_post');
</code></pre>

Static result for the query above from March 2025:
<pre>
<code type='click-ui' language='text' show_line_numbers='false'>
┌─rows──────────┬─data_size─┐
│ 50.62 million │ 3.58 GiB  │
└───────────────┴───────────┘
</code>
</pre>


Note: The incremental materialized view’s target table is smaller than the full Bluesky dataset table but still **substantial** in both row count and total (uncompressed) size.

> In this scenario, **the size of pre-aggregated data depends on the source table**: While an incremental materialized view can pre-calculate repost counts, its target table grows alongside the source dataset. Its size and row count scale directly with the ever-increasing number of posts and reposts, as it tracks counts for all existing and future posts.

As we will see below, this impacts query performance, but we’ll revisit this shortly and introduce an additional technique to **break** this dependency.

### Optimized query: still not fast enough (1.7s)

We run the query from above over the `reposts_per_post` table with pre-aggregated data:
<pre><code type='click-ui' language='sql' runnable='true' show_statistics='true' run='false' view='table' play_link='https://sql.clickhouse.com/?query=U0VMRUNUCiAgY2lkLAogIHN1bShyZXBvc3RzKSBBUyByZXBvc3RzCkZST00gYmx1ZXNreS5yZXBvc3RzX3Blcl9wb3N0CkdST1VQIEJZIGNpZApPUkRFUiBCWSByZXBvc3RzIERFU0MKTElNSVQgMTA&run_query=true&tab=results'>
SELECT
  cid,
  sum(reposts) AS reposts
FROM bluesky.reposts_per_post
GROUP BY cid
ORDER BY reposts DESC
LIMIT 10;
</code></pre>

Execution statistics queried via [unrestricted](/blog/accelerating-clickhouse-json-queries-for-fast-bluesky-dashboards#test-all-queries-live) `clickhouse-client`:
<pre>
<code type='click-ui' language='text' show_line_numbers='false'>
Elapsed: 1.732 sec. Processed 50.62 million rows, 3.85 GB (29.23 million rows/s., 2.22 GB/s.)
Peak memory usage: 9.66 GiB.
</code>
</pre>

In this case, even with pre-aggregated data, the query response isn’t yet instantaneous—though faster (37 seconds and 45 GiB memory usage before), it’s still above the desired <100ms “snappy” threshold.

<div style="padding: 12px; border: 1px solid #323232; border-radius: 5px; background-color: #2E2E2D; color: white; font-family: Arial, sans-serif; line-height: 1.4;">
  <p style="color: #FF4500; font-weight: bold; margin-bottom: 4px;">1s - 2s (slow but tolerable) <span style="color: white; font-weight: normal;">— Feels sluggish. Use loading indicators.</span></p>
</div>

<br/>

As mentioned above, **the materialized view’s target table grows alongside the base dataset itself**. 

> As a result, even the optimized query over this pre-aggregated data will inevitably slow down as the Bluesky dataset grows.

We need a smarter approach. Do we really need repost counts for every post? No—we only care about the top N most reposted posts. While incremental materialized views alone aren’t directly feasible for maintaining such limited top-N results, we can solve this elegantly with a **refreshable materialized view**, ensuring we keep only the most relevant reposted posts.

### Breaking the performance bottleneck: A smarter approach

We retain the `reposts_per_post` table along with its incremental materialized view. Additionally, we introduce ① a [refreshable materialized view](https://clickhouse.com/docs/materialized-view/refreshable-materialized-view) to continuously maintain the ② compact `reposts_per_post_top10` table, which serves as ③ input for the dashboard query. This table is regularly updated—atomically and without affecting running queries—containing only the current top 10 most-reposted posts:

![Blog-bluesky-faster.009.png](https://clickhouse.com/uploads/Blog_bluesky_faster_009_0aa688d346.png)

The DDL statement for `reposts_per_post_top10` is identical to `reposts_per_post`:
<pre>
<code type='click-ui' language='sql'>
CREATE TABLE bluesky.reposts_per_post_top10
(
    cid String,
    reposts UInt64
)
ENGINE = MergeTree
ORDER BY ();
</code>
</pre>

This is the definition for the refreshable materialized view:

<pre>
<code type='click-ui' language='sql'>
CREATE MATERIALIZED VIEW bluesky.reposts_per_post_top10_mv
REFRESH EVERY 10 MINUTE TO bluesky.reposts_per_post_top10
AS
SELECT
    cid,
    sum(reposts) AS reposts
FROM bluesky.reposts_per_post
GROUP BY cid
ORDER BY reposts DESC
LIMIT 10;
</code>
</pre>

We configured the view to run once every 10 minutes. 

> An incremental materialized view updates its target table in real-time, staying in sync with its source, while a refreshable materialized view updates at fixed intervals, with the lower bound set by its update query duration.

Running this refreshable materialized view query directly on the complete dataset [would](/blog/accelerating-clickhouse-json-queries-for-fast-bluesky-dashboards#why-repost-queries-are-slow--baseline-37s-execution-time) take 37 seconds and consume 45 GiB of memory—far too heavy for frequent execution. 

However, querying the pre-aggregated and always in sync `reposts_per_post` table achieves the same result [in](/blog/accelerating-clickhouse-json-queries-for-fast-bluesky-dashboards#optimized-query-still-not-fast-enough-17s) just 1.7 seconds and uses only 10 GiB of memory, significantly reducing resource usage.

> We pair a refreshable materialized view with an incremental one to maximize resource efficiency.

### Compact data, instant results

Now, the best part—as expected, the `reposts_per_post_top10` table, when fully synced with the 4+ billion-row Bluesky dataset, consistently holds exactly 10 rows, totaling just about 680 bytes:
<pre><code type='click-ui' language='sql' runnable='true' show_statistics='true' run='true' view='table' play_link='https://sql.clickhouse.com/?query=U0VMRUNUCiAgICBmb3JtYXRSZWFkYWJsZVF1YW50aXR5KHN1bShyb3dzKSkgQVMgcm93cywKICAgIGZvcm1hdFJlYWRhYmxlU2l6ZShzdW0oZGF0YV91bmNvbXByZXNzZWRfYnl0ZXMpKSBBUyBkYXRhX3NpemUKRlJPTSBzeXN0ZW0ucGFydHMKV0hFUkUgYWN0aXZlIEFORCAoZGF0YWJhc2UgPSAnYmx1ZXNreScpIEFORCAoYHRhYmxlYCA9ICdyZXBvc3RzX3Blcl9wb3N0X3RvcDEwJyk7Cg&chart=eyJ0eXBlIjoiYmFyIiwiY29uZmlnIjp7InRpdGxlIjoiTnVtYmVyIG9mIGV2ZW50cyBwZXIgaG91ciBvZiBkYXkiLCJ4YXhpcyI6ImhvdXJfb2ZfZGF5IiwieWF4aXMiOiJjb3VudCIsInNlcmllcyI6ImV2ZW50Iiwic3RhY2siOmZhbHNlfX0&run_query=true&tab=results'>
SELECT
    formatReadableQuantity(sum(rows)) AS rows,
    formatReadableSize(sum(data_uncompressed_bytes)) AS data_size
FROM system.parts
WHERE active AND (database = 'bluesky') AND (table = 'reposts_per_post_top10');
</code></pre>

Static result for the query above from March 2025:
<pre>
<code type='click-ui' language='text' show_line_numbers='false'>
┌─rows──┬─data_size─┐
│ 10.00 │ 680.00 B  │
└───────┴───────────┘
</code>
</pre>


> **The size of pre-aggregated data remains independent of the source table**: Now, similar to the previous two dashboard examples, the target table’s size and row count is fixed at 10 rows taking 680 bytes in total size, regardless of how large the original Bluesky dataset table grows.


### Final optimization: sub-100ms queries

And here’s the payoff—running the query against the compact `reposts_per_post_top10` table (always exactly 10 rows) guarantees instantaneous (&lt;100ms) response times, every single time:

<pre><code type='click-ui' language='sql' runnable='true' show_statistics='true' run='true' view='table' play_link='https://sql.clickhouse.com/?query=U0VMRUNUICoKRlJPTSBibHVlc2t5LnJlcG9zdHNfcGVyX3Bvc3RfdG9wMTAKT1JERVIgQlkgcmVwb3N0cyBERVNDOw&chart=eyJ0eXBlIjoiYmFyIiwiY29uZmlnIjp7InRpdGxlIjoiTnVtYmVyIG9mIGV2ZW50cyBwZXIgaG91ciBvZiBkYXkiLCJ4YXhpcyI6ImhvdXJfb2ZfZGF5IiwieWF4aXMiOiJjb3VudCIsInNlcmllcyI6ImV2ZW50Iiwic3RhY2siOmZhbHNlfX0&run_query=true&tab=results'>
SELECT *
FROM bluesky.reposts_per_post_top10
ORDER BY reposts DESC;
</code></pre>

Execution statistics queried via [unrestricted](/blog/accelerating-clickhouse-json-queries-for-fast-bluesky-dashboards#test-all-queries-live) `clickhouse-client`:
<pre>
<code type='click-ui' language='text' show_line_numbers='false'>
Elapsed: 0.002 sec.
</code>
</pre>


<div style="padding: 12px; border: 1px solid #323232; border-radius: 5px; background-color: #2E2E2D; color: white; font-family: Arial, sans-serif; line-height: 1.4;">
  <p style="color: #00FF00; font-weight: bold; margin-bottom: 4px;">&lt;100ms (instant) <span style="color: white; font-weight: normal;">— Feels instant, ideal for filtering or quick updates.</span></p>
</div>



### Memory comparison: 28 KiB vs 45 GiB


To illustrate how our optimized approach drastically reduces memory usage, the table below compares memory consumption across all three key components.

![Blog-bluesky-faster-v3.011.png](https://clickhouse.com/uploads/Blog_bluesky_faster_v3_011_69f9dc837a.png)

| **Metric**         | **Baseline query**                                                          | **① Incremental MV**                                                                    | **② Refreshable MV**                                                                          | **③ Optimized query**                                                     |
|--------------------|-----------------------------------------------------------------------------|-----------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------|
| **Memory usage**   | 45 GiB                                                                      | 37.62 MiB                                                                              | [~10 GiB](/blog/accelerating-clickhouse-json-queries-for-fast-bluesky-dashboards#optimized-query-still-not-fast-enough-17s)                                                                                   | 28.44 KiB                                                                  |
| **Rows processed** | Full dataset                                                                | ~647.18k per update                                                                    | 54.4 million per refresh                                                                      | 10 rows (Top 10)                                                           |
| **Duration**       | 37 sec                                                                      | ~412 ms per update                                                                     | 2.6 sec per refresh                                                                           | Instantaneous                                                               |
| **Metrics source** | [Execution statistics](/blog/accelerating-clickhouse-json-queries-for-fast-bluesky-dashboards#baseline-query-counting-unique-users-56s) | [Query views log](https://gist.github.com/tom-clickhouse/6a60bdf39a6d92f306e90d134c240255) | [View refreshes log](https://gist.github.com/tom-clickhouse/477fe6f00a56b0061619ad2c8332a476) | [Query log](https://gist.github.com/tom-clickhouse/2974298dbe6e3037a6e398088aa01f57) |


> Even at peak usage, the combined memory footprint of all three components stays significantly lower than the original **45 GiB baseline**, demonstrating the efficiency of this approach.


## Enriching repost results with post content


As mentioned earlier, this scenario introduces an additional challenge: the dashboard must display the most reposted Bluesky posts, but repost events contain only post identifiers (CIDs), not the actual post content. 

![Blog-bluesky-faster.001.png](https://clickhouse.com/uploads/Blog_bluesky_faster_001_4295ba4b79.png)

We tackle this efficiently by:

1. Creating an ① incremental materialized view to pre-populate a ② dedicated `cid_to_text table` with the content of each new post, optimized for fast CID lookups.

2. Extending our refreshable materialized view to leverage this structure, enabling an efficient ③ join to retrieve and store the text content for the top 10 reposted posts in the compact `reposts_per_post_top10` table, which ④ serves as input for the dashboard query.

![Blog-bluesky-faster.010.png](https://clickhouse.com/uploads/Blog_bluesky_faster_010_f70827c6c9.png)


The primary key `(kind, bluesky_ts)` of the complete Bluesky dataset [table](/blog/accelerating-clickhouse-json-queries-for-fast-bluesky-dashboards#how-we-store-bluesky-json-data-in-clickhouse) isn’t optimal for quick lookups of post content by CID, especially at billions of rows. To solve this, we create a dedicated `cid_to_text` table with a primary key optimized specifically for efficient CID-based text retrieval:

<pre>
<code type='click-ui' language='sql'>
CREATE TABLE bluesky.cid_to_text
(
    cid String,
    did String,
    text String
)
ENGINE = MergeTree
ORDER BY (cid);
</code>
</pre>

This is the DDL for the incremental materialized view populating the `cid_to_text` table whenever a new text is posted:
<pre>
<code type='click-ui' language='sql'>
CREATE MATERIALIZED VIEW bluesky.cid_to_text_mv 
TO bluesky.cid_to_text
AS 
SELECT
    data.commit.cid AS cid,
    data.did AS did,
    data.commit.record.text AS text
FROM bluesky.bluesky
WHERE (kind = 'commit') AND (data.commit.collection = 'app.bsky.feed.post');
</code>
</pre>


Note that the `cid_to_text` table’s size scales with the complete Bluesky dataset. However, since it’s only queried periodically by the refreshable view—which doesn’t require instantaneous response times—this dependency is acceptable and won’t impact real-time dashboard performance.


### Optimizing joins with fast post content lookups

Before presenting the DDL for the final refreshable materialized view, let’s first examine the join query it will leverage. This query identifies the top 10 reposted posts and enriches them with their text content by joining two optimized tables: the pre-aggregated `reposts_per_post` table (left side of the join), and the dedicated `cid_to_text table` (right side of the join for retrieving the text per CID from the left side):
<pre>
<code type='click-ui' language='sql'>
WITH top_reposted_cids AS
(
  SELECT
    cid,
    sum(reposts) AS reposts
  FROM bluesky.reposts_per_post
  GROUP BY cid
  ORDER BY reposts DESC
  LIMIT 10
)
SELECT
    t2.did AS did,
    t1.reposts AS reposts,
    t2.text AS text
FROM top_reposted_cids AS t1
LEFT JOIN bluesky.cid_to_text AS t2
ON t1.cid = t2.cid;
</code>
</pre>

Execution statistics queried via [unrestricted](/blog/accelerating-clickhouse-json-queries-for-fast-bluesky-dashboards#test-all-queries-live) `clickhouse-client`:
<pre>
<code type='click-ui' language='text' show_line_numbers='false'>
Elapsed: 295.427 sec. Processed 379.42 million rows, 85.14 GB (1.28 million rows/s., 288.18 MB/s.)
Peak memory usage: 126.77 GiB.
</code>
</pre>

Ouch—almost 300 seconds and 127 GiB of memory usage clearly isn’t ideal.

The issue here is that the join query planner doesn’t [yet](https://github.com/ClickHouse/ClickHouse/issues/74046) push down filter conditions based on the left hand side to the right hand side of the join. But we can simply do that manually and very efficiently by exploiting the primary key of the right hand side table for the join:

<pre><code type='click-ui' language='sql' runnable='true' show_statistics='true' run='false' view='table' play_link='https://sql.clickhouse.com/?query=V0lUSCB0b3BfcmVwb3N0ZWRfY2lkcyBBUwooCiAgU0VMRUNUCiAgICBjaWQsCiAgICBzdW0ocmVwb3N0cykgQVMgcmVwb3N0cwogIEZST00gYmx1ZXNreS5yZXBvc3RzX3Blcl9wb3N0CiAgR1JPVVAgQlkgY2lkCiAgT1JERVIgQlkgcmVwb3N0cyBERVNDCiAgTElNSVQgMTAKKQpTRUxFQ1QKICAgIHQyLmRpZCBBUyBkaWQsCiAgICB0MS5yZXBvc3RzIEFTIHJlcG9zdHMsCiAgICB0Mi50ZXh0IEFTIHRleHQKRlJPTSB0b3BfcmVwb3N0ZWRfY2lkcyBBUyB0MQpMRUZUIEpPSU4KKAogICAgU0VMRUNUICoKICAgIEZST00gYmx1ZXNreS5jaWRfdG9fdGV4dAogICAgV0hFUkUgY2lkIElOIChTRUxFQ1QgY2lkIEZST00gdG9wX3JlcG9zdGVkX2NpZHMpCikgQVMgdDIgT04gdDEuY2lkID0gdDIuY2lkOw&tab=results'>
WITH top_reposted_cids AS
(
  SELECT
    cid,
    sum(reposts) AS reposts
  FROM bluesky.reposts_per_post
  GROUP BY cid
  ORDER BY reposts DESC
  LIMIT 10
)
SELECT
    t2.did AS did,
    t1.reposts AS reposts,
    t2.text AS text
FROM top_reposted_cids AS t1
LEFT JOIN
(
    SELECT *
    FROM bluesky.cid_to_text
    WHERE cid IN (SELECT cid FROM top_reposted_cids)
) AS t2 ON t1.cid = t2.cid;
</code></pre>

Execution statistics queried via [unrestricted](/blog/accelerating-clickhouse-json-queries-for-fast-bluesky-dashboards#test-all-queries-live) `clickhouse-client`:
<pre>
<code type='click-ui' language='text' show_line_numbers='false'>
Elapsed: 3.681 sec. Processed 102.37 million rows, 7.78 GB (27.81 million rows/s., 2.11 GB/s.)
Peak memory usage: 9.91 GiB.
</code>
</pre>


By pre-filtering the large `cid_to_text` table on the right-hand side of the join with the CIDs of the top 10 most reposted posts—an efficient operation that leverages the table’s primary key—the query now completes in 3.6 seconds instead of 300 and uses only 9.91 GiB of RAM instead of 127 GiB.


### Maintaining the top 10 reposted posts efficiently

We use the join query from above as the query for our final refreshable materialized view that regularly updates this target table with the top 10 most reposted posts and their texts (plus the [DID](https://docs.bsky.app/docs/advanced-guides/resolving-identities)s of their original authors):
<pre>
<code type='click-ui' language='sql'>
CREATE TABLE bluesky.reposts_per_post_top10_v2
(
  did String,
  reposts UInt64,
  text String
)
ENGINE = MergeTree
ORDER BY ();
</code>
</pre>

This is the DDL for the refreshable materialized view:
<pre>
<code type='click-ui' language='sql'>
CREATE MATERIALIZED VIEW bluesky.reposts_per_post_top10_mv_v2
REFRESH EVERY 10 MINUTE TO bluesky.reposts_per_post_top10_v2
AS
WITH top_reposted_cids AS
(
  SELECT
    cid,
    sum(reposts) AS reposts
  FROM bluesky.reposts_per_post
  GROUP BY cid
  ORDER BY reposts DESC
  LIMIT 10
)
SELECT
    t2.did AS did,
    t1.reposts AS reposts,
    t2.text AS text
FROM top_reposted_cids AS t1
LEFT JOIN
(
    SELECT *
    FROM bluesky.cid_to_text
    WHERE cid IN (SELECT cid FROM top_reposted_cids)
) AS t2 ON t1.cid = t2.cid;
</code>
</pre>

### How small is the final aggregated data?

As expected, when the `reposts_per_post_top10_v2` table is fully in sync with the 4+ billion rows full Bluesky dataset table, it consistently contains always exactly 10 rows, totaling just 2.35 KiB in size:

<pre><code type='click-ui' language='sql' runnable='true' show_statistics='true' run='true' view='table' play_link='https://sql.clickhouse.com/?query=U0VMRUNUCiAgICBmb3JtYXRSZWFkYWJsZVF1YW50aXR5KHN1bShyb3dzKSkgQVMgcm93cywKICAgIGZvcm1hdFJlYWRhYmxlU2l6ZShzdW0oZGF0YV91bmNvbXByZXNzZWRfYnl0ZXMpKSBBUyBkYXRhX3NpemUKRlJPTSBzeXN0ZW0ucGFydHMKV0hFUkUgYWN0aXZlIEFORCAoZGF0YWJhc2UgPSAnYmx1ZXNreScpIEFORCAoYHRhYmxlYCA9ICdyZXBvc3RzX3Blcl9wb3N0X3RvcDEwX3YyJyk7&chart=eyJ0eXBlIjoiYmFyIiwiY29uZmlnIjp7InRpdGxlIjoiTnVtYmVyIG9mIGV2ZW50cyBwZXIgaG91ciBvZiBkYXkiLCJ4YXhpcyI6ImhvdXJfb2ZfZGF5IiwieWF4aXMiOiJjb3VudCIsInNlcmllcyI6ImV2ZW50Iiwic3RhY2siOmZhbHNlfX0&run_query=true&tab=results'>
SELECT
    formatReadableQuantity(sum(rows)) AS rows,
    formatReadableSize(sum(data_uncompressed_bytes)) AS data_size
FROM system.parts
WHERE active AND (database = 'bluesky') AND (table = 'reposts_per_post_top10_v2');
</code></pre>

Static result for the query above from March 2025:
<pre>
<code type='click-ui' language='text' show_line_numbers='false'>
┌─rows──┬─data_size─┐
│ 10.00 │ 2.35 KiB  │
└───────┴───────────┘
</code>
</pre>



### Final optimized query: 3ms response time for instant results

Running the query against the compact `reposts_per_post_top10_v2` table (always exactly 10 rows) guarantees instantaneous response times, every single time:

<pre><code type='click-ui' language='sql' runnable='true' show_statistics='true' run='true'  view='table'  play_link='https://sql.clickhouse.com/?query=U0VMRUNUICoKRlJPTSBibHVlc2t5LnJlcG9zdHNfcGVyX3Bvc3RfdG9wMTBfdjIKT1JERVIgQlkgcmVwb3N0cyBERVNDOw&chart=eyJ0eXBlIjoiYmFyIiwiY29uZmlnIjp7InRpdGxlIjoiTnVtYmVyIG9mIGV2ZW50cyBwZXIgaG91ciBvZiBkYXkiLCJ4YXhpcyI6ImhvdXJfb2ZfZGF5IiwieWF4aXMiOiJjb3VudCIsInNlcmllcyI6ImV2ZW50Iiwic3RhY2siOmZhbHNlfX0&run_query=true&tab=results'>
SELECT *
FROM bluesky.reposts_per_post_top10_v2
ORDER BY reposts DESC;
</code></pre>

Execution statistics queried via [unrestricted](/blog/accelerating-clickhouse-json-queries-for-fast-bluesky-dashboards#test-all-queries-live) `clickhouse-client`:
<pre>
<code type='click-ui' language='text' show_line_numbers='false'>
Elapsed: 0.003 sec.
</code>
</pre>


<div style="padding: 12px; border: 1px solid #323232; border-radius: 5px; background-color: #2E2E2D; color: white; font-family: Arial, sans-serif; line-height: 1.4;">
  <p style="color: #00FF00; font-weight: bold; margin-bottom: 4px;">&lt;100ms (instant) <span style="color: white; font-weight: normal;">— Feels instant, ideal for filtering or quick updates.</span></p>
</div>


### Memory usage of accelerated query (45 KiB vs 45 GiB)

Our optimization now includes four key components, each playing a role in drastically reducing memory consumption while maintaining real-time performance.

![Blog-bluesky-faster-v3.013.png](https://clickhouse.com/uploads/Blog_bluesky_faster_v3_013_a62baefe3a.png)

| **Metric**         | **Baseline query**                                                          | **① Incremental MV** (`reposts_per_post_mv`)                                           | **② Incremental MV** (`cid_to_text_mv`)                                        | **③ Refreshable MV** (`reposts_per_post_top10_mv_v2`)                                         | **④ Optimized query**                                                      |
|--------------------|-----------------------------------------------------------------------------|-----------------------------------------------------------------------------------------|--------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------|
| **Memory usage**   | 45 GiB                                                                      | 37.62 MiB                                                                              | 327.70 MiB                                                                     | [~10 GiB](/blog/accelerating-clickhouse-json-queries-for-fast-bluesky-dashboards#optimizing-the-join-for-fast-text-lookup)                                                                                    | 45.71 KiB                                                                  |
| **Rows processed** | Full dataset                                                                | ~647.18k per update                                                                    | ~646.20k per update                                                            | 109.69 million per refresh                                                                    | 10 rows (Top 10)                                                           |
| **Duration**       | 37 sec                                                                      | ~412 ms per update                                                                     | ~1.27 sec per update                                                           | 3.65 sec per refresh                                                                          | Instantaneous                                                               |
| **Metrics source** | [Execution statistics](/blog/accelerating-clickhouse-json-queries-for-fast-bluesky-dashboards#optimized-query-still-not-fast-enough-17s) | [Query views log](https://gist.github.com/tom-clickhouse/85f68107989a9dcc15c88069b50b46f5) | [Query views log](https://gist.github.com/tom-clickhouse/b31067309822b73d52beaee2ba147837) | [View refreshes log](https://gist.github.com/tom-clickhouse/7ca341f1813bfc97c2dc9f8caa0c050a) | [Query log](https://gist.github.com/tom-clickhouse/6877b725afe4229316a1b622f2caf1fb) |




> The total memory usage across all four components—37.62 MiB, 327.70 MiB, 10 GiB, and 45.71 KiB—remains lower than the 45 GiB consumed by the baseline query.


## Mapping DIDs to user handles in real-time

So far, this third real-time dashboard scenario has presented two key challenges:

1. **Efficient top-N retrieval**: Incremental materialized views alone weren’t sufficient, requiring a **refreshable materialized view** to maintain the top N most reposted posts.

2. **Enriching repost data**: Since repost events contain only the post identifier (CID) and not the text, we needed to **join two tables** to retrieve and display the full post content.

But there’s still one missing piece—right now, we’re displaying reposts by [DID](https://docs.bsky.app/docs/advanced-guides/resolving-identities), which doesn't look good on a dashboard. Next, let’s map those IDs to real user [handles](https://docs.bsky.app/docs/advanced-guides/resolving-identities) in real-time.


The JSON documents for post, repost, like events, and similar Bluesky actions do not contain user handles or names—only their DIDs:

![Blog-bluesky-faster.001.png](https://clickhouse.com/uploads/Blog_bluesky_faster_001_80577d40e2.png)

Unlike DIDs, handles and names can change at any time due to `identity` events in Bluesky:

![Blog-bluesky-faster.002.png](https://clickhouse.com/uploads/Blog_bluesky_faster_002_821026cca7.png)

Fortunately, ClickHouse offers a perfect solution for this scenario: **updatable in-memory dictionaries**, allowing efficient real-time lookups and seamless updates.

[Dictionaries](https://clickhouse.com/docs/en/sql-reference/dictionaries) are a [key feature](https://clickhouse.com/blog/faster-queries-dictionaries-clickhouse) of ClickHouse providing in-memory [key-value](https://en.wikipedia.org/wiki/Key%E2%80%93value_database) representation of data from various internal and external sources, optimized for super-low latency lookup queries.

The diagram below illustrates how, in our dashboard scenarios, an in-memory dictionary is created and loaded to enable efficient real-time lookups for dynamic metadata, such as user handles, allowing dashboards to be enriched on-the-fly with up-to-date information at query time:

![Blog-bluesky-faster.011.png](https://clickhouse.com/uploads/Blog_bluesky_faster_011_0aab10dc01.png)

We create (see below) an ① handle_per_user_dict dictionary to map persistent, long-term Bluesky user identifiers ([DIDs](https://docs.bsky.app/docs/advanced-guides/resolving-identities)) to their latest corresponding user handles. When a user changes their handle, the Bluesky API streams an `identity` JSON document. By grouping these documents by DID value, we use the [argMax](https://clickhouse.com/docs/sql-reference/aggregate-functions/reference/argmax) aggregate function in ClickHouse to retrieve the handle from the latest identity document per unique DID—forming the basis of the ② dictionary load query.

Like refreshable materialized views, a dictionary can be periodically updated atomically—ensuring that queries performing lookups remain unaffected—by periodically executing its load query. 

To avoid repeatedly running the `argMax` aggregation on the ever-growing 4+ billion-row Bluesky dataset, we introduce an **efficiency optimization**, as illustrated in the next diagram:

![Blog-bluesky-faster.012.png](https://clickhouse.com/uploads/Blog_bluesky_faster_012_c328034409.png)

We introduce an ① additional incremental materialized view that runs the argMax aggregation only on newly inserted blocks of rows, storing the pre-aggregated data in a ② ReplacingMergeTree table. This table’s [background merges](https://clickhouse.com/docs/merges#replacing-merges) ensure that only the latest handle per unique DID is retained. The dictionary’s ③ load query then runs against this smaller table, using the [FINAL](https://clickhouse.com/docs/sql-reference/statements/select/from#final-modifier) modifier to finalize row replacements from unmerged parts at query time.

Next, we present the DDL statements to set this up.

This is the DDL for the incremental materialized view’s target table:
<pre>
<code type='click-ui' language='sql'>
CREATE TABLE bluesky.handle_per_user
(
    did String,
    handle String
)
ENGINE = ReplacingMergeTree
ORDER BY (did);
</code>
</pre>

This is the incremental materialized view:
<pre>
<code type='click-ui' language='sql'>
CREATE MATERIALIZED VIEW bluesky.handle_per_user_mv 
TO bluesky.handle_per_user
AS 
SELECT
    data.identity.did::String AS did,
    argMax(data.identity.handle, bluesky_ts) AS handle
FROM bluesky.bluesky
WHERE (kind = 'identity')
GROUP BY did;
</code>
</pre>

Finally, we create the in-memory dictionary with a query against the materialized view’s target table to load its content. We also set a time interval (in seconds) for updates, allowing ClickHouse to randomly distribute the update time within this range—helping to balance the load when updating across a large number of servers:

<pre>
<code type='click-ui' language='sql'>
CREATE DICTIONARY bluesky.handle_per_user_dict
(
    did String,
    handle String
)
PRIMARY KEY (did)
SOURCE(CLICKHOUSE(QUERY $query$
    SELECT did, handle
    FROM bluesky.handle_per_user FINAL
$query$))
LIFETIME(MIN 300 MAX 360)
LAYOUT(complex_key_hashed());
</code>
</pre>

Note that dictionaries are either loaded at server startup or at first use, depending on the [dictionaries_lazy_load](https://clickhouse.com/docs/operations/server-configuration-parameters/settings#dictionaries_lazy_load) setting.

Users can also manually trigger a load by running a SYSTEM command. When used with the ON CLUSTER clause, this ensures that all compute nodes in our Cloud service load the dictionary into memory:

<pre>
<code type='click-ui' language='sql'>
SYSTEM RELOAD DICTIONARY bluesky.handle_per_user_dict ON cluster default;
</code>
</pre>

Now the dictionary is ready to be used ad-hocly in our dashboard queries for mapping DIDs to user handles, for example:

<pre><code type='click-ui' language='sql' runnable='true' show_statistics='true' run='true'  view='table'  play_link='https://sql.clickhouse.com/?query=U0VMRUNUIGRpY3RHZXQoJ2JsdWVza3kuaGFuZGxlX3Blcl91c2VyX2RpY3QnLCAnaGFuZGxlJywgJ2RpZDpwbGM6ZW10bWtscjc1eXJidXV0aDRhdnZ1dG9zJykgQVMgaGFuZGxlOw&run_query=true&tab=results'>
SELECT dictGet('bluesky.handle_per_user_dict', 'handle', 'did:plc:emtmklr75yrbuuth4avvutos') AS handle;
</code></pre>

Static result for the query above from March 2025:
<pre>
<code type='click-ui' language='text' show_line_numbers='false'>
┌─handle──────────────┐
│ agbogho.bsky.social │
└─────────────────────┘

1 row in set. Elapsed: 0.001 sec.
</code>
</pre>

### Final query: real-time repost rankings with user handles (3ms response time) 

With everything in place, we can now run our final dashboard 3 query, using the dictionary to fetch the latest handles for the DIDs of the top 10 most reposted posts:

<pre><code type='click-ui' language='sql' runnable='true' show_statistics='true' run='true'  view='table'  play_link='https://sql.clickhouse.com/?query=U0VMRUNUCiAgICBkaWN0R2V0T3JEZWZhdWx0KCdibHVlc2t5LmhhbmRsZV9wZXJfdXNlcl9kaWN0JywgJ2hhbmRsZScsIGRpZCwgZGlkKSBhcyB1c2VyLAogICAgcmVwb3N0cywKICAgIHRleHQKRlJPTSBibHVlc2t5LnJlcG9zdHNfcGVyX3Bvc3RfdG9wMTBfdjIKT1JERVIgQlkgcmVwb3N0cyBERVND&run_query=true&tab=results'>
SELECT
  dictGetOrDefault(
    'bluesky.handle_per_user_dict',
    'handle', did, did) as user,
  reposts,
  text
FROM bluesky.reposts_per_post_top10_v2
ORDER BY reposts DESC;
</code></pre>

Execution statistics queried via [unrestricted](/blog/accelerating-clickhouse-json-queries-for-fast-bluesky-dashboards#test-all-queries-live) `clickhouse-client`:
<pre>
<code type='click-ui' language='text' show_line_numbers='false'>
Elapsed: 0.003 sec.
</code>
</pre>


Note that we use the [dictGetOrDefault](https://clickhouse.com/docs/sql-reference/functions/ext-dict-functions#dictget-dictgetordefault-dictgetornull) function, which returns the DID if no mapping is found in the dictionary. 

In theory, the dictionary could contain as many entries as there are Bluesky users—currently [around 30 million](https://www.theverge.com/news/602049/bluesky-now-has-30-million-users). However, since we began ingesting Bluesky event data in real-time in December 2024, it only includes mappings from handle or name change events recorded since that date.

As of March 2025, the dictionary contains **~8 million entries**, consuming **1.12 GiB** of memory (queried via [unrestricted](/blog/accelerating-clickhouse-json-queries-for-fast-bluesky-dashboards#test-all-queries-live) `clickhouse-client`):
<pre>
<code type='click-ui' language='sql'>
SELECT
    status,
    element_count AS entries,
    formatReadableSize(bytes_allocated) AS memory_allocated,
    formatReadableTimeDelta(loading_duration) AS loading_duration
FROM system.dictionaries
WHERE database = 'bluesky' AND name = 'handle_per_user_dict';
</code>
</pre>

<pre>
<code type='click-ui' language='text' show_line_numbers='false'>
┌─status─┬─entries─┬─memory_allocated─┬─loading_duration─┐
│ LOADED │ 7840778 │ 1.12 GiB         │ 4 seconds        │
└────────┴─────────┴──────────────────┴──────────────────┘
</code>
</pre>

With **30 million entries**, we estimate the dictionary size would reach **~4.5 GiB**.

If the number of Bluesky users continues to grow, we may need to revisit whether an in-memory dictionary remains the best approach.

### Memory overhead from dictionary usage

To efficiently maintain an up-to-date dictionary without scanning the full 4+ billion-row dataset, we introduced an **incremental materialized view** to pre-aggregate handle changes. The dictionary itself refreshes at regular intervals via a **load query**, ensuring minimal overhead.

![Blog-bluesky-faster-v3.018.png](https://clickhouse.com/uploads/Blog_bluesky_faster_v3_018_6fe53eb2b3.png)

| **Metric**         | **Baseline query**                                                          | **① Incremental MV** (`handle_per_user_mv`)                                     | **② Dictionary load query**                                       | **③ Dictionary storage (projected at 30M entries)**                                                                |
|--------------------|-----------------------------------------------------------------------------|---------------------------------------------------------------------------------|-------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------|
| **Memory usage**   | 45 GiB                                                                      | 5.77 KiB                                                                       | 479 MiB                                                           | 1.12 GiB → **4.5 GiB (projected)**                                                                                 |
| **Rows processed** | Full dataset                                                                | ~645.87k per update                                                            | 8.89 million per refresh                                          | 30 million entries (projected)                                                                                     |
| **Duration**       | Long-running                                                               | ~285 ms per update                                                             | 106 ms per refresh                                                | N/A                                                                                                                |
| **Metrics source** | [Execution statistics](/blog/accelerating-clickhouse-json-queries-for-fast-bluesky-dashboards#optimized-query-still-not-fast-enough-17s) | [Query views log](https://gist.github.com/tom-clickhouse/1ef72e5ea818ee5a374d10e195e8fb3e) | [Query log](https://gist.github.com/tom-clickhouse/f317a1926455cf66c95adcc7ecda0861) | Estimated based on [dictionaries](https://gist.github.com/tom-clickhouse/d852e414aa8f8d098009f4ee6a51eefc) metrics |

Even after factoring in the dictionary and its updates, plus the [previously analysed](/blog/accelerating-clickhouse-json-queries-for-fast-bluesky-dashboards#memory-usage-of-accelerated-query-45-kib-vs-45-gib) optimized dashboard query, the **total memory usage across all components remains well below the 45 GiB baseline query**. 

> By carefully structuring incremental updates and periodic dictionary refreshes, we achieve efficient, low-latency lookups without the memory burden of full dataset scans.



Now, let’s step back and see the impact of these optimizations across all three dashboard scenarios.

## Mission accomplished: sustained <100ms query performance 

With our optimizations, dashboard queries now run in **under 100ms**, no matter how much the dataset grows—even on moderate hardware. The key? Ensuring queries always operate on small, stable, and pre-aggregated data.

Despite **4+ billion JSON documents**, with **1.5 billion new documents added every month**, our input tables remain compact:

| **Scenario**                         | **Pre-aggregated table**    | **Rows** | **Size**  |
|--------------------------------------|-----------------------------|---------|----------|
| **Dashboard 1: Activity by hour**    | `events_per_hour_of_day`    | 892     | 11.24 KiB |
| **Dashboard 2: Ranked event types**  | `top_event_types`           | 109     | 2.27 MiB  |
| **Dashboard 3: Most reposted posts** | `reposts_per_post_top10_v2` | 10      | 2.35 KiB  |

### The secret to fast queries at scale

The trick is simple: **never scan the full dataset, but always stay up-to-date**.
- **Dashboards 1 & 2**: **Incremental materialized views** continuously update pre-aggregated tables in real-time.
- **Dashboard 3**: A **refreshable materialized view** maintains only the most relevant top-N results.

This ensures dashboard queries always run on **small, stable, and fresh tables**, regardless of dataset growth.


### From sluggish to snappy: Before vs. after  

| **Dashboard**           | **Baseline query** | **Optimized query** | **Speedup**        | **Memory usage reduction** |
|-------------------------|--------------------|---------------------|--------------------|----------------------------|
| **Activity by hour**    | **44s** (775 MiB)  | **6ms** (186 KiB)   | ~7,300× faster    | -99.97% RAM                |
| **Ranked event types**     | **56s** (1 GiB)    | **7ms** (16 MiB)    | ~8,000× faster    | -98.4% RAM                 |
| **Most reposted posts** | **37s** (45 GiB)   | **3ms** (45 KiB)    | ~12,300× faster   | -99.99% RAM                |

### Final takeaways for ClickHouse users  

✅ **Incremental materialized views** guarantee fast response times when pre-aggregated data remains independent of source table growth.  

✅ **Refreshable materialized views**, often paired with incremental ones for efficiency, help when pre-aggregated data from incremental materialized views alone still depends on the source table’s growth. They balance performance and freshness by maintaining small and stable top-N query inputs.

✅ **In-memory dictionaries** enrich dashboards with real-time metadata lookups.  

By keeping input tables small and independent of dataset growth, ClickHouse delivers real-time JSON analytics with sustained performance at any scale.