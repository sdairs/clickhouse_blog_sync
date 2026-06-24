---
title: "The end-to-end cost-performance of real-time analytics: Snowflake vs. ClickHouse Cloud"
date: "2026-06-24T06:11:38.285Z"
author: "Tom Schreiber, Mark Needham and Lionel Palacin"
category: "Engineering"
excerpt: "Real-time analytics is more than fast queries. CostBench compares Snowflake and ClickHouse Cloud across the full path: continuous ingest, query-ready data maintenance, freshness, query latency, and cost."
---

# The end-to-end cost-performance of real-time analytics: Snowflake vs. ClickHouse Cloud

## TL;DR {tldr}

A benchmark for real-time analytics needs to measure the system end-to-end: fresh data in, query-ready data maintained, fast answers out, and the cost of keeping that full path running.

That is what CostBench measures. It captures the cost and latency of continuous ingest, data maintenance, and query execution together, because different systems spend work in different places.

A read-only benchmark on a static dataset can show how fast queries return once the data is already prepared. It does not show the cost of making that data query-ready, or whether queries stay fast while fresh data is continuously arriving and being maintained in parallel.

In this post, we use CostBench to compare Snowflake and ClickHouse Cloud across that full real-time analytics path.

## Real-time analytics does not start when a query runs {#realtime_analytics_does_not_start_when_a_query_runs}

> Real-time analytics starts when fresh data arrives.

Before a dashboard, user, or AI agent can get a fast answer, the system has already done a lot of work: ingesting new rows, organizing them for pruning, maintaining derived tables, preserving freshness, and keeping read capacity available for low-latency queries.

That full path is what [CostBench](https://clickhouse.com/blog/costbench-data-warehouse-cost-performance) is designed to measure: not just the final read query, but the full running system that turns fresh data into fast answers.

That was also the core idea behind our [earlier benchmark on query-ready data](https://clickhouse.com/blog/write-side-cost-performance-snowflake-clickhouse). We measured one important aspect of this path: the cost-performance of continuously ingesting data **and** keeping raw data physically organized for fast analytical reads.

Snowflake [responded](https://www.snowflake.com/en/blog/engineering/efficient-snowflake-ingestion-query-ready/) to that benchmark with a set of recommendations: use different ingestion methods, use larger warehouses for loading, and use Snowflake’s newer real-time features where available.

Some of those recommendations improve a Snowflake setup. Others answer a different question, such as how quickly Snowflake can batch-load data, when the objective is maximum throughput rather than sustained query-readiness. But all of them point back to the same principle we started with:

> A real-time analytics system should be benchmarked as a full path, not as isolated ingest, maintenance, or read tests.

That is what this post does. We use CostBench to rerun the comparison as an end-to-end benchmark: continuous ingest, raw-data organization, pre-aggregation freshness, and continuous query serving. We test two Snowflake paths: the broadly available standard-table setup and the newer Interactive Tables setup.

All benchmark code and results are available in the [CostBench repository](https://github.com/ClickHouse/CostBench/tree/main/full-path-realtime/quotes). The stock-quotes dataset requires a [separate data license](https://github.com/ClickHouse/CostBench/tree/main/full-path-realtime/quotes#data-source--licensing), so the data itself cannot be redistributed.

## CostBench measures the complete analytics path {#costbench_measures_the_complete_analytics_path}

That is the methodology behind CostBench.

CostBench measures cost-performance across the complete analytics path:

![super_cool_01.gif](https://clickhouse.com/uploads/super_cool_01_8e3ad63faf.gif)

① Fresh data arrives continuously.

② The system writes that data and makes it [query-ready](https://clickhouse.com/blog/write-side-cost-performance-snowflake-clickhouse#what-does-query-ready-mean).

③ Raw data is kept in an ordered layout, so later queries can skip most of the table instead of scanning everything.

④ The system maintains pre-aggregated data, so the lowest-latency queries read even less at query time.

⑤ Finally, the system has to serve fast answers continuously, while ingest and maintenance keep running in the background.

> **CostBench is not a bulk-load or backfill benchmark**  
CostBench simulates a [real-time analytics system](https://clickhouse.com/blog/selecting-a-real-time-analytical-database) in which fresh data is continuously generated at the source and must become query-ready as it arrives. It is not a bulk-load or backfill benchmark that asks how quickly a system can load data that already exists. 

In this post, we apply that methodology to Snowflake and ClickHouse.



---

## Get started with real-time analytics on ClickHouse Cloud

Ingest fresh data, keep it query-ready, and serve low-latency queries with ClickHouse Cloud. Get started in minutes with $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-1021-get-started-with-real-time-analytics-on-clickhouse-cloud-sign-up&utm_blogctaid=1021)

---


## What our first benchmark measured: query-ready raw data {#what_our_first_benchmark_measured_queryready_raw_data}

Our [original benchmark](https://clickhouse.com/blog/write-side-cost-performance-snowflake-clickhouse) measured one important part of the full [real-time analytics](https://clickhouse.com/blog/selecting-a-real-time-analytical-database) path: the cost of continuously turning newly written raw data into query-ready raw data.

Below is the original setup, along with Snowflake's main comments that it helps clarify.

![super_cool_02.gif](https://clickhouse.com/uploads/super_cool_02_cfb22bda80.gif)

### **① Dataset and ordering key** {#dataset_and_ordering_key}

We used the [ClickBench](https://benchmark.clickhouse.com/) web analytics dataset, with [more than 100 columns and the original multi-column sorting key](https://github.com/ClickHouse/ClickBench/blob/main/clickhouse-cloud/create.sql) used by the ClickBench [workload](https://github.com/ClickHouse/ClickBench/blob/main/clickhouse-cloud/queries.sql).

That choice was deliberate. Many ClickBench queries benefit from this ordering in ClickHouse, so to keep later query performance measurements fair, we used the equivalent clustering key in Snowflake.

> **Snowflake’s comment:** use a simpler clustering key, and avoid the artificial arrival pattern created by repeating the original ClickBench dataset to reach 100 billion rows.

That is fair, and we address both in the expanded benchmark below. But they actually answer different questions: how data arrives, and what physical layout the system has to maintain for the workload.

### **② Continuous ingest at a fixed rate** {#continuous_ingest_at_a_fixed_rate}

We ingested data continuously at roughly 1 million rows per second, or about 1 GB of uncompressed data per second.

This was not a maximum-throughput loading test. The ingest rate was intentionally fixed to simulate a real-time workload where new data arrives continuously, and the goal was to use the smallest, lowest-cost Snowflake setup that could sustain that rate while keeping the table query-ready.

> **Snowflake’s comment:** use COPY INTO, Snowpipe Streaming, larger warehouses, and Gen2 warehouses.

Those are reasonable choices for other ingest tests. But in this benchmark, the loading mechanism was secondary. The question was not how quickly Snowflake could finish loading 100 billion rows, but what it would cost to keep up with a fixed real-time ingest rate as common in real-time analytics use cases.

### **③ Query-ready raw data, not pre-aggregation** {#queryready_raw_data_not_preaggregation}

The first benchmark focused on the base table: newly written raw data in, query-ready raw data out. It did not measure materialized views.

> **Snowflake’s comment:** broader production setups should include more of the data pipeline.

Agreed. That is exactly what CostBench adds next: derived-data maintenance, freshness, and reads alongside ingest and raw-data organization.

### **④ Reads measured after loading** {#reads_measured_after_loading}

After the table reached 100 billion rows, we ran the ClickBench query workload once to validate query performance.

So the first benchmark did not measure continuous serving while ingest, clustering, refresh, or other maintenance work continued in the background.

> **Snowflake’s comment:** use Interactive Tables and Interactive Warehouses for high-concurrency, low-latency serving.

Fair enough. Interactive Tables were not part of the first benchmark because that benchmark used the Snowflake path most customers could actually use: standard tables with clustering. Interactive Tables are a newer feature and are currently available only in selected regions.

For the expanded benchmark, we therefore test both paths: the broadly available Snowflake setup using standard tables and materialized views, and an Interactive Tables setup in a supported region.

## The expanded benchmark addresses the broader question {#the_expanded_benchmark_addresses_the_broader_question}

Before Snowflake published its response, we had already started applying the new CostBench methodology to [a broader full-path benchmark](https://github.com/ClickHouse/CostBench/tree/main/full-path-realtime/quotes).

This time, we intentionally started at the easier end of the spectrum: a much simpler dataset and ordering key, a cleaner arrival pattern, and continuous reads while data keeps moving, a setup that removes several of the factors Snowflake objected to in the original ClickBench test.

We will repeat this with heavier datasets later. But first, we wanted to measure the full path in the cleanest possible case.

![super_cool_03.gif](https://clickhouse.com/uploads/super_cool_03_511670f5b9.gif)

### **① Simpler dataset, timestamp-ordered ingest** {#simpler_dataset_timestampordered_ingest}

We use [a real stock market quotes dataset](https://github.com/ClickHouse/CostBench/tree/main/full-path-realtime/quotes#dataset) licensed from a [data provider](https://github.com/ClickHouse/CostBench/tree/main/full-path-realtime/quotes#data-source--licensing), with access to hundreds of billions of rows.

Compared with ClickBench, it has a much simpler shape: [12 columns](https://github.com/ClickHouse/CostBench/tree/main/full-path-realtime/quotes#schema-vendor-agnostic), a simple two-column sorting key, and a natural timestamp order.

We ingest the data in strict timestamp order at steady rate of 1 million rows per second. At that rate, the system receives 100 billion fresh rows every 28 hours.

### **② Simple clustering key** {#simple_clustering_key}

This time, the sorting/clustering key are just two columns: `(sym, t)` - the stock symbol and the timestamp. This is as natural and simple as it can get.

ClickHouse [sorts](https://github.com/ClickHouse/CostBench/blob/6fb94fd628b100db69bc2bf9f8d6f149eec54601/full-path-realtime/quotes/clickhouse-cloud/create.sql#L22) the raw table by those columns, and Snowflake [clusters](https://github.com/ClickHouse/CostBench/blob/6fb94fd628b100db69bc2bf9f8d6f149eec54601/full-path-realtime/quotes/snowflake/create.sql#L58) the raw table by those columns.

### **③ Pre-aggregations included** {#preaggregations_included}

Unlike the original benchmark, this run includes continuously maintained pre-aggregations.

That means we also measure the cost of keeping derived data fresh while new rows keep arriving.

### **④ Continuous queries on the matching layouts** {#continuous_queries_on_the_matching_layouts}

This time, queries run continuously while fresh data continues to arrive.

The workload includes two query types: **dashboard queries against the pre-aggregated data**, and **drill-down queries against the raw data** with filters matching the raw table’s ordering/clustering key.

**We keep the systems’ caches enabled**. In benchmarks with static data, we usually disable query-result caches to avoid measuring memory lookups instead of pure engine performance. Here, the data is constantly changing, so caches are much less useful, and leaving them enabled better reflects real-world usage.

**We run each query once per round**. That mirrors how these queries are used in practice: a dashboard refresh, a user drill-down, or an exploratory ad-hoc query happens once against the latest state of the data.

That simulates the real-time scenario more directly: ingest, maintenance, freshness, and reads all happen at the same time.

## ClickHouse Cloud setup {#clickhouse_cloud_setup}

For ClickHouse Cloud, we used separate services for ingest and reads, so the write path and query path were [isolated](https://clickhouse.com/blog/introducing-warehouses-compute-compute-separation-in-clickhouse-cloud) from each other.

![super_cool_04.gif](https://clickhouse.com/uploads/super_cool_04_ed5d57168d.gif)

### **① Client setup** {#client_setup}

The [client](https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/clickhouse-cloud/ingest_parquet_dir.py) (benchmark driver) is kept intentionally simple and it performs the the same work for ClickHouse and Snowflake. 

It reads Parquet row groups directly from existing Parquet files in binary form, combines them into batches of roughly 1 million rows, and sends those batches to the target system. There is no decoding, no decompression, no encoding, and no compression on the client side.

That matters because Snowflake’s response called out client-side cost as a missing factor in the first benchmark. In this setup, the client work is identical for both systems and uses very little CPU and memory, so client-side cost is no longer a meaningful differentiator.

### **② Ingest service** {#ingest_service}

Ingest runs on a dedicated ClickHouse Cloud service with 2 nodes, each using 2 CPUs and 8 GiB of memory.

That was [enough](https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/clickhouse-cloud/results/utilization/writer/README_clickhouse_writer_utilization.md) to ingest 1 million rows-per-second data stream continuously, sort the incoming data, and update the pre-aggregated data, while keeping the total number of active data parts across the tables at around 60 at any given time via [continuous background merges](https://clickhouse.com/docs/merges).

> This efficiency also matters in practice: it lets us run demos like [StockHouse](https://stockhouse.clickhouse.com/) cost-effectively, with the same market data used in this benchmark streaming in **live** and becoming query-ready as it arrives.

### **③ Sorted raw data and materialized views** {#sorted_raw_data_and_materialized_views}

ClickHouse writes the raw data directly to disk in [sorted form](https://clickhouse.com/blog/write-side-cost-performance-snowflake-clickhouse#clickhouse-ordering-on-the-write-path), using a MergeTree table. This is the table that serves the raw-data drill-down workload.

At the same time, an incremental materialized view maintains the pre-aggregated data in an AggregatingMergeTree table as new rows arrive. This is the table that serves the dashboard workload.

Code: [raw MergeTree table](https://github.com/ClickHouse/CostBench/blob/6fb94fd628b100db69bc2bf9f8d6f149eec54601/full-path-realtime/quotes/clickhouse-cloud/create.sql#L7), [AggregatingMergeTree table](https://github.com/ClickHouse/CostBench/blob/6fb94fd628b100db69bc2bf9f8d6f149eec54601/full-path-realtime/quotes/clickhouse-cloud/create.sql#L31), and [incremental materialized view](https://github.com/ClickHouse/CostBench/blob/6fb94fd628b100db69bc2bf9f8d6f149eec54601/full-path-realtime/quotes/clickhouse-cloud/create.sql#L53).

> At any time during the benchmark, the raw MergeTree table remains sorted for fast drill-downs, and the AggregatingMergeTree table stores the pre-aggregated data for the dashboard queries, with no freshness gap to the base table. Both tables stay up-to-date and [ready for queries](https://clickhouse.com/blog/write-side-cost-performance-snowflake-clickhouse#what-does-query-ready-mean) all the time.

### **④ Read service** {#read_service}

Read queries run on a [separate](https://clickhouse.com/blog/introducing-warehouses-compute-compute-separation-in-clickhouse-cloud) ClickHouse Cloud service with 1 node and 16 CPUs.

> We use the same amount of read compute for the Snowflake setups, so read-side capacity is aligned across systems.

Note: It is widely [understood](https://select.dev/posts/snowflake-warehouse-sizing) that a Snowflake Gen2 Small warehouse on AWS [uses](https://medium.com/snowflake-engineering/deep-dive-inside-snowflakes-new-gen2-standard-warehouses-powered-by-aws-graviton3-6aacca73ae2d) 16 AWS Graviton3 cores. ClickHouse Cloud also uses AWS Graviton3 cores in AWS deployments, so the comparison aligns both read paths on 16 cores of the same CPU generation.

### **⑤ Continuous query workload** {#continuous_query_workload}

To simulate a continuous read workload, we run two types of queries periodically throughout the benchmark.

Every 10 minutes, we send [4 dashboard queries](https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/clickhouse-cloud/queries_mv.sql) against the pre-aggregated table.

Every hour, we send [2 ad-hoc drill-down queries](https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/clickhouse-cloud/queries_raw.sql) against the raw table. These drill-down queries use filters that match the raw table’s sort order.

> We run the same query schedule on Snowflake, with equivalent physical layouts: the raw data is clustered by the same key, and the aggregated data is pre-aggregated in the same way.

## Snowflake setup 1: standard tables and materialized views {#snowflake_setup_1_standard_tables_and_materialized_views}

The first Snowflake setup uses the path most Snowflake customers can use today: standard tables, standard [materialized views](https://docs.snowflake.com/en/user-guide/views-materialized), and Gen2 warehouses.

![super_cool_05.gif](https://clickhouse.com/uploads/super_cool_05_40334945a6.gif)


### **① Client setup** {#client_setup_2}

> The [client](https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/snowflake/ingest.py) setup (benchmark driver) is the same as in the ClickHouse setup.

It reads Parquet row groups directly in binary form, combines them into batches of roughly 1 million rows, and sends those batches to Snowflake. This time, the client uses `COPY INTO` to load the Parquet data into the raw table.

As mentioned earlier, the client does no decoding, no decompression, no encoding, and no compression. The amount of performed client-side work is therefore exactly the same as for ClickHouse.

### **② Ingest warehouse** {#ingest_warehouse}

For ingest, we again chose the smallest Snowflake warehouse that could sustain the fixed 1 million rows per second ingest rate.

But this time, following Snowflake’s recommendation, we use Gen2 hardware: specifically, a Gen2 X-Small warehouse with 8 CPUs.

> The goal is still not maximum load throughput. 

The goal is the lowest-cost setup that can sustain with the fixed ingest rate to ​​simulate a real-time workload where new data arrives continuously.

### **③ Serverless clustering** {#serverless_clustering}

The raw data is written into a standard Snowflake table. This is the table that serves the hourly raw-data drill-down workload.

The data ordering is then handled by Snowflake’s [serverless clustering service](https://docs.snowflake.com/en/user-guide/tables-auto-reclustering) in the background, as in the original benchmark. The goal is to keep the raw table physically optimized for the drill-down queries.

Code: [raw Snowflake table](https://github.com/ClickHouse/CostBench/blob/6fb94fd628b100db69bc2bf9f8d6f149eec54601/full-path-realtime/quotes/snowflake/create.sql#L44).

### **④ Materialized view refresh** {#materialized_view_refresh}

To include pre-aggregation in the end-to-end benchmark, we use a Snowflake materialized view over the raw table. This view is queried by the dashboard workload.

Materialized views are an Enterprise-only Snowflake feature. Refresh work is handled by Snowflake’s [serverless materialized view refresh service](https://docs.snowflake.com/en/user-guide/views-materialized#materialized-views-cost) in the background.

Code: [Snowflake materialized view](https://github.com/ClickHouse/CostBench/blob/6fb94fd628b100db69bc2bf9f8d6f149eec54601/full-path-realtime/quotes/snowflake/create.sql#L79).

### **⑤ Read warehouse** {#read_warehouse}

As in the ClickHouse setup, we use separate warehouses for ingest and reads, so the write path and query path are isolated from each other.

For reads, we use a Gen2 Small warehouse with 16 CPUs.

> This matches the read-side CPU count used in ClickHouse.

### **⑥ Continuous query workload** {#continuous_query_workload_2}

We run the same continuous query schedule as in ClickHouse.

Every 10 minutes, we run [4 queries against the pre-aggregated data](https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/snowflake/queries_mv.sql), simulating dashboard refreshes.

Every hour, we run [2 raw-data drill-down queries](https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/snowflake/queries_raw.sql) against the raw table.

## **Snowflake setup 2: Interactive Tables** {#snowflake_setup_2_interactive_tables}

The second Snowflake setup uses [Interactive Tables](https://docs.snowflake.com/en/user-guide/interactive) for both the raw data and the pre-aggregated data.

Interactive Tables are currently [available only in selected regions](https://docs.snowflake.com/en/user-guide/interactive#label-interactive-region-availability). To test them, we had to create a Snowflake account in a supported region. For that reason, we include both Snowflake paths: the broadly available setup using standard tables and materialized views, and the newer Interactive Tables setup where available.

![super_cool_06.gif](https://clickhouse.com/uploads/super_cool_06_71a35fb20c.gif)

### **① Client setup** {#client_setup_3}

The [client](https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/snowflake/ingest.py) is the same as in the ClickHouse setup and the first Snowflake setup.

It reads Parquet row groups directly in binary form, combines them into batches of roughly 1 million rows, and uses `COPY INTO` to load the data into Snowflake. The client does no decoding, no decompression, no encoding, and no compression.

### **② Ingest warehouse** {#ingest_warehouse_2}

As before, ingest uses the **smallest Snowflake warehouse** that could sustain the fixed 1 million rows per second ingest rate.

We use a Gen2 X-Small warehouse with 8 CPUs.

### **③ Raw data refresh** {#raw_data_refresh}

Incoming data first lands in a standard Snowflake table. The raw Interactive Table is then maintained from that source table by a user-managed warehouse, with refreshes triggered as needed to meet the configured target lag. This corresponds to the standard Interactive Tables pattern.

> We use a 10-minute target lag for the raw Interactive Table, which serves the hourly drill-down workload.

*(Direct ingest into Interactive Tables is possible through Snowflake-managed ingest paths, which we treat [separately](/blog/real-time-analytics-cost-performance-snowflake-vs-clickhouse#outlook_more_paths_and_heavier_workloads) because it does not cover the pre-aggregated path measured here.)*

Code and docs: [standard Snowflake table](https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/snowflake/create.sql#L44), [raw Interactive Table](https://github.com/ClickHouse/CostBench/blob/6fb94fd628b100db69bc2bf9f8d6f149eec54601/full-path-realtime/quotes/snowflake/ops/setup_interactive.sh#L59), [target lag refresh behavior](https://docs.snowflake.com/en/user-guide/interactive#specifying-auto-refresh-for-an-interactive-table), and [insert-only limitation](https://docs.snowflake.com/en/user-guide/snowpipe-streaming/snowpipe-streaming-table-support#insert-only-operations).


### **④ Pre-aggregated data refresh** {#preaggregated_data_refresh}

The pre-aggregated data is also stored in an Interactive Table.

Here, the refresh warehouse regularly transfers the new rows since the previous refresh, aggregates them, and merges the result into the pre-aggregated Interactive Table.

> We use a 1-minute target lag, which is the smallest target lag available.  
> This is the table that serves the dashboard workload, so we configure the freshest pre-aggregation path Snowflake allows.

That lets us compare it with ClickHouse incremental materialized views, which update on the ingest path, and measure what it costs to get as close as possible to that freshness model in Snowflake. Snowflake also offers Interactive Materialized Views; we [will](/blog/real-time-analytics-cost-performance-snowflake-vs-clickhouse#outlook_more_paths_and_heavier_workloads) test that path separately.

We use a Gen2 X-Large warehouse for refreshes, after a Small, Medium, and Large warehouse could not reliably keep the pre-aggregation refresh within the 1-minute target lag.

Code and docs: [pre-aggregated Interactive Table](https://github.com/ClickHouse/CostBench/blob/6fb94fd628b100db69bc2bf9f8d6f149eec54601/full-path-realtime/quotes/snowflake/ops/setup_interactive.sh#L50), [aggregation query](https://github.com/ClickHouse/CostBench/blob/6fb94fd628b100db69bc2bf9f8d6f149eec54601/full-path-realtime/quotes/snowflake/ops/setup_interactive.sh#L54), [target lag behavior](https://docs.snowflake.com/en/user-guide/interactive#specifying-auto-refresh-for-an-interactive-table), [Interactive Materialized Views](https://docs.snowflake.com/en/user-guide/interactive#materialized-view-support-for-interactive-tables), and [refresh-size comparison](/blog/real-time-analytics-cost-performance-snowflake-vs-clickhouse#freshness_scheduled_refresh_has_to_keep_up).

### **⑤ Interactive read warehouse** {#interactive_read_warehouse}

For reads, we use a Small [Interactive Warehouse](https://docs.snowflake.com/en/user-guide/interactive) with 16 CPUs.

> This matches the read-side CPU count used for ClickHouse and the first Snowflake setup.

Unlike a standard warehouse, the Interactive Warehouse also comes with a [large cache](https://docs.snowflake.com/en/user-guide/interactive#choosing-a-size-for-an-interactive-warehouse). For a Small Interactive Warehouse, that cache is roughly 600 GB, allowing the working set of Interactive Tables to be kept in memory.

Note that Interactive Warehouses have a 1-hour minimum billing duration, and auto-suspend has a minimum setting of 24 hours. In this benchmark, that billing model fits the workload: we are measuring a continuously running real-time analytics service, with ongoing ingest, refresh, and queries.

### **⑥ Continuous query workload** {#continuous_query_workload_3}

We run the same continuous query schedule as before.

Every 10 minutes, we run [4 queries against the pre-aggregated data](https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/snowflake/queries_mv_it.sql), simulating dashboard refreshes.

Every hour, we run [2 raw-data drill-down queries](https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/snowflake/queries_raw_it.sql) against the raw Interactive table.

## Results: ClickHouse vs. Snowflake standard tables {#results_clickhouse_vs_snowflake_standard_tables}

First, we compare ClickHouse with the Snowflake [setup](/blog/real-time-analytics-cost-performance-snowflake-vs-clickhouse#snowflake_setup_1_standard_tables_and_materialized_views) most customers can use today: standard tables, standard materialized views, serverless clustering, serverless MV refresh, and Gen2 warehouses.

### Performance: latency and freshness under continuous ingest {#performance_latency_and_freshness_under_continuous_ingest}

> Both systems use the same read-side compute for these measurements: 16 AWS Graviton3 cores.

The query schedule is also identical.

#### Dashboard queries: pre-aggregations only help if they stay fresh {#dashboard_queries_preaggregations_only_help_if_they_stay_fresh}

This chart shows the 4 dashboard queries we run every 10 minutes against the pre-aggregated data. The x-axis is the number of rows ingested into the raw table, from the start of the run to 100 billion rows after roughly 28 hours. The y-axis is query latency.

![Blog-Snowflake-response-02.002.png](https://clickhouse.com/uploads/Blog_Snowflake_response_02_002_5961766d69.png)

*All per-query run details are available in the CostBench repository: [ClickHouse](https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/clickhouse-cloud/results/mv/dashboard_20260609T154019Z.jsonl), [Snowflake](https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/snowflake/results/t0/dashboard_20260609T154304Z.jsonl).*

ClickHouse stays almost completely flat as the raw table grows, with dashboard queries remaining in the single-digit millisecond range. That is because ClickHouse updates the pre-aggregated table on the ingest path, so it stays fresh and query-ready continuously.

Snowflake’s standard materialized-view setup behaves very differently. Query latency is much higher and fluctuates heavily: simpler dashboard queries stay around the low seconds, while heavier dashboard queries jump into the high single-digit to tens-of-seconds range.

The reason is freshness. Snowflake materialized views still return results for the latest ingested data, even when the materialized view itself is behind. In that case, Snowflake has to combine the materialized view with the missing rows from the raw table at query time. For a dashboard workload, that means refreshes do not just get slower; they become unpredictable.

#### Freshness lag: the hidden cost behind slow dashboards {#freshness_lag_the_hidden_cost_behind_slow_dashboards}

The next chart shows the underlying freshness lag directly.

![Blog-Snowflake-response-02.003.png](https://clickhouse.com/uploads/Blog_Snowflake_response_02_003_8b2b3d9fbe.png)

*We measured this lag by [polling](https://github.com/ClickHouse/CostBench/blob/6fb94fd628b100db69bc2bf9f8d6f149eec54601/full-path-realtime/quotes/snowflake/ops/mv_latency.sh#L39) Snowflake’s materialized-view metadata once per minute with `SHOW MATERIALIZED VIEWS`; the detailed freshness samples are available [here](https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/snowflake/results/t0/mv_latency_20260609T154304Z.jsonl) - see the behind_by column.*

ClickHouse stays current because its materialized views are updated synchronously on the ingest path.

Snowflake’s materialized view is refreshed by a serverless background service with no freshness SLA and no user control over when it runs or how much compute it uses. In this run, the Snowflake materialized view was continuously behind, with lag repeatedly reaching roughly 60 to 72 minutes.

#### Drill-down queries: clustering helps, but does not keep latency flat {#drilldown_queries_clustering_helps_but_does_not_keep_latency_flat}

The next chart shows the 2 drill-down queries we run every hour against the raw data. The x-axis is the number of rows ingested into the raw table, from the start of the run to 100 billion rows after roughly 28 hours. The y-axis is query latency.

![Blog-Snowflake-response-02.004.png](https://clickhouse.com/uploads/Blog_Snowflake_response_02_004_8f3328b964.png)

*All per-query run details are available in the CostBench repository: [ClickHouse](https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/clickhouse-cloud/results/raw/drilldown_20260617T162929Z.jsonl), [Snowflake](https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/snowflake/results/t0/drilldown_20260617T155914Z.jsonl).*

These queries use filters that match the raw table’s ordering/clustering key. In other words, both systems get the same physical-layout advantage: ClickHouse sorts by the key, and Snowflake clusters by the same key.

Even then, the pattern is the same as in our [initial read-side benchmark](https://clickhouse.com/blog/cloud-data-warehouses-cost-performance-comparison): as the dataset grows, the systems diverge. ClickHouse stays roughly flat, largely unimpressed by data size. Snowflake gets progressively slower, reaching several seconds by the end of the run.

### Cost: ingest, maintenance, and reads {#cost_ingest_maintenance_and_reads}

For cost, we use Enterprise pricing for AWS us-east. This gives Snowflake access to materialized views, which require Enterprise Edition; ClickHouse materialized views are available even in the open-source version.

#### Fresh-data path cost: keeping data query-ready {#freshdata_path_cost_keeping_data_queryready}

The next chart shows the total fresh-data path cost for the first 28 hours of the run: ingesting 100 billion fresh rows at a continuous rate of 1 million rows per second, while keeping the raw data sorted/clustered and the pre-aggregated data maintained.

![Blog-Snowflake-response-02.005.png](https://clickhouse.com/uploads/Blog_Snowflake_response_02_005_6636922c38.png)

For ClickHouse, the ingest service uses 2 nodes with 2 CPUs and 8 GiB RAM per node. In [ClickHouse Cloud pricing](https://clickhouse.com/blog/how-cloud-data-warehouses-bill-you#clickhouse-cloud), that corresponds to 2 compute units. Over the 28-hour run: 2 compute units × 28 hours × $0.3903/hour \= **$21.86.**

For Snowflake, the ingest warehouse is a Gen2 X-Small warehouse. At [1.35 credits/hour](https://www.snowflake.com/legal-files/CreditConsumptionTable.pdf) and $3 per credit, the ingest warehouse cost is: 1.35 credits/hour × 28 hours × $3/credit \= **$113.40.**

The remaining Snowflake write-side costs come from serverless services. We take the consumed credits from Snowflake system tables and multiply by the same $3 per credit price: serverless clustering: [54.12 credits](https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/snowflake/results/system_tables/clustering-raw_table-details.md) × $3 \= **$162.37**; serverless materialized-view refresh: [3.60 credits](https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/snowflake/results/system_tables/refresh-mv_table-details.md) × $3 \= **$10.8.**

Together, Snowflake’s fresh-data path costs **$286.58**.

Before query cost is included, Snowflake’s standard setup already costs about **13× more** to keep fresh data query-ready.

#### Query cost: serving the same schedule {#query_cost_serving_the_same_schedule}

Finally, we measure the read side: how much runtime and query cost each system needs to serve the same continuous query schedule over the 28-hour run.

For query cost, we use the same [simplification](https://clickhouse.com/blog/cloud-data-warehouses-cost-performance-comparison#a-note-on-metering-granularity) as in the initial [read-side benchmark](https://clickhouse.com/blog/cloud-data-warehouses-cost-performance-comparison) methodology: accumulated query runtime × read-side compute price, as if query compute were billed with perfect per-second granularity.

In reality, both Snowflake and ClickHouse Cloud continue [billing](https://clickhouse.com/blog/how-cloud-data-warehouses-bill-you) until a configurable idle timeout is reached. But this normalization compares query-engine efficiency directly: 

> For a given amount of paid compute time, how much query work can the system complete?

The chart below shows the result.

![Blog-Snowflake-response-02.006.png](https://clickhouse.com/uploads/Blog_Snowflake_response_02_006_8b1789565f.png)

*All per-query run details are available in the CostBench repository: ClickHouse [dashboard queries](https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/clickhouse-cloud/results/mv/dashboard_20260609T154019Z.jsonl) and [drill-down queries](https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/clickhouse-cloud/results/raw/drilldown_20260617T162929Z.jsonl), Snowflake [dashboard queries](https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/snowflake/results/t0/dashboard_20260609T154304Z.jsonl) and [drill-down queries](https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/snowflake/results/t0/drilldown_20260617T155914Z.jsonl)*.

For query cost, we use the accumulated runtime of the continuous read workload and multiply it by the price of the read-side compute.

ClickHouse uses one read service with 16 CPUs and 64 GiB RAM, which corresponds to 8 compute units: 8 compute units × $0.3903/hour × 70.4 seconds \= **$0.061**

Snowflake uses a Gen2 Small read warehouse with 16 CPUs. At 2.7 credits/hour and $3 per credit, that is $8.10/hour: 2.7 credits/hour × $3/credit × 5,017 seconds \= **$11.288**

That makes ClickHouse about 185× cheaper on query compute for this workload, before we combine it with the fresh-data path cost.

### Cost-performance: the full-path score {#costperformance_the_fullpath_score}

> Where do you get the most full-path real-time performance per dollar spent?

To compare full-path real-time cost-efficiency directly, we collapse cost and performance into a single lower-is-better score.

The score is:

**(fresh-data path cost + query cost) × total query runtime**

This captures the basic cost-performance tradeoff: systems score better when they keep the path cheap and serve queries quickly. Expensive systems score worse. Slow systems score worse. And when a system is both expensive and slow, the two effects compound.

![Blog-Snowflake-response-02.007.png](https://clickhouse.com/uploads/Blog_Snowflake_response_02_007_12778f7554.png)

Snowflake’s standard setup scores **969× worse**.

That is the compounding effect: Snowflake pays more to keep the path running and still needs much more runtime to serve the same continuous query schedule.

And this is before spending the budget difference. At Snowflake’s spend level, ClickHouse could scale up to larger services and reduce latency even further while still staying below the same total cost.

## Results: ClickHouse vs. Snowflake Interactive Tables {#results_clickhouse_vs_snowflake_interactive_tables}

In the previous section, we measured ClickHouse against Snowflake’s broadly available standard-table path. Next, we repeat the same CostBench workload against Snowflake’s [Interactive Tables setup](/blog/real-time-analytics-cost-performance-snowflake-vs-clickhouse#snowflake_setup_2_interactive_tables).

The workload, client behavior, ingest rate, query schedule, and read-side CPU count stay the same. What changes is the Snowflake serving path: raw and pre-aggregated data now sit in Interactive Tables, refreshed by a user-managed warehouse and served by an Interactive Warehouse with a large cache.

As a reminder:

> Both systems use the same read-side compute for these measurements: 16 AWS Graviton3 cores.

### Performance: Interactive Tables improve reads, but do not remove the gap {#performance_interactive_tables_improve_reads_but_do_not_remove_the_gap}

The charts use the same format as above: x-axis is raw rows ingested, up to 100 billion rows after roughly 28 hours; y-axis is query latency.

#### Dashboard queries: faster with Interactive tables, but still not as flat {#dashboard_queries_faster_with_interactive_tables_but_still_not_as_flat}

For dashboard queries, Interactive Tables in combination with an interactive warehouse dramatically improve Snowflake’s latency compared with the standard materialized-view setup. But ClickHouse still stays lower and flatter, despite using the same read-side CPU count.

![Blog-Snowflake-response-02.009.png](https://clickhouse.com/uploads/Blog_Snowflake_response_02_009_7141f2ac69.png)

*All per-query run details are available in the CostBench repository: [ClickHouse](https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/clickhouse-cloud/results/mv/dashboard_20260609T154019Z.jsonl), [Snowflake](https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/snowflake/results/t1/dashboard_20260617T154602Z.jsonl).*

> **Interactive pre-aggregated results are one refresh cycle behind.**<br/>Even when Snowflake dashboard queries return quickly, they read from a pre-aggregated Interactive Table with a 1-minute target lag.<br/>ClickHouse stays both faster and current because pre-aggregation happens on the ingest path.

#### Freshness: scheduled refresh has to keep up {#freshness_scheduled_refresh_has_to_keep_up}

The next chart shows what it takes to keep pre-aggregations fresh in the Interactive Tables setup.

![Blog-Snowflake-response-02.010.png](https://clickhouse.com/uploads/Blog_Snowflake_response_02_010_a75c3d811c.png)

*We measured this lag by [polling](https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/snowflake/ops/it_refresh.sh) Snowflake’s INFORMATION_SCHEMA.INTERACTIVE_TABLE_REFRESH_HISTORY table once per minute`, results are [here](https://github.com/ClickHouse/CostBench/tree/main/full-path-realtime/quotes/snowflake/results/t1/it_refresh).*

ClickHouse stays current throughout the run because its materialized views are updated synchronously as new rows are inserted.

The raw Interactive Table behaved as expected: with a 10-minute refresh target, it stayed within that target across the tested warehouse sizes. That kept the raw table fresh enough for the hourly drill-down workload.

The harder part was the pre-aggregated Interactive Table. As mentioned earlier, we used the smallest refresh interval Snowflake allows, 1 minute, because this table serves the stock-quotes dashboard workload and is the closest Snowflake can get to ClickHouse materialized views. 

A Gen2 Small refresh warehouse fell behind after roughly 3 hours, Gen2 Medium after roughly 8 hours, and Gen2 Large after roughly 15 hours. The red crosses mark the point where each setup could no longer keep the pre-aggregated Interactive Table within the configured 1-minute target.

This is not because Snowflake re-aggregates the entire raw table on every refresh. The refresh into the pre-aggregated Interactive Table is incremental, as confirmed by a system-table query for our setup. Even so, the refresh warehouse still has to process the new rows, aggregate them, and merge the result into the target table before the next refresh is due.

That is why the final setup uses a Gen2 X-Large refresh warehouse. It kept both Interactive Tables within their configured targets over the first 24 hours. 

> The pre-aggregation lag is still creeping upward. It does not break the 1-minute target on day one, but the curve is not flat. For longer runs, Snowflake would need either more refresh compute or a looser freshness target.

#### Drill-down queries: Interactive warehouse cache helps, but scaling still shows {#drilldown_queries_interactive_warehouse_cache_helps_but_scaling_still_shows}

For drill-down queries, Interactive Tables improve Snowflake substantially compared with the standard-table setup. 

![Blog-Snowflake-response-02.011.png](https://clickhouse.com/uploads/Blog_Snowflake_response_02_011_d5d25d84eb.png)

*All per-query run details are available in the CostBench repository: [ClickHouse](https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/clickhouse-cloud/results/raw/drilldown_20260617T162929Z.jsonl), [Snowflake](https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/snowflake/results/t1/drilldown_20260617T154602Z.jsonl).*

But the improvement does not stay flat as data volume grows.

Even though the working set still fits in the Interactive Warehouse cache throughout the first 100 billion rows, Snowflake latency rises with data size. ClickHouse stays much flatter, even without an Interactive Warehouse cache. For one drill-down query, Snowflake is already slower than ClickHouse around 50 billion rows; by the end of the run, both drill-down queries are at or above ClickHouse latency.

> **Takeaway:** Even on a lightweight dataset, after only about one day of a [modest](https://clickhouse.com/blog/how-tesla-built-quadrillion-scale-observability-platform-on-clickhouse) ingest at 1 million rows per second, Snowflake Interactive Tables are already at or above ClickHouse latency for the drill-down workload.

**Scaling note**

The important point is that latency already grows while the working set still fits in the Interactive Warehouse cache.

That raises the next scaling question: what happens when the working set no longer fits, even in the largest available Interactive Warehouse cache?

Snowflake’s Interactive Warehouse model also has a hard 5-second query timeout. Once queries cross that threshold, [Snowflake recommends a fallback warehouse](https://docs.snowflake.com/en/user-guide/interactive#automatically-handling-statement-timeouts). That adds another cost dimension: the fallback warehouse has to be available when needed, and the user-visible runtime includes the failed attempt plus the retry on the fallback compute.

### Cost: ingest and refresh {#cost_ingest_and_refresh}

Interactive Tables make the query path cheaper than the standard Snowflake setup, but the cost moves to refresh.

#### Fresh-data path cost: refresh becomes the dominant component {#freshdata_path_cost_refresh_becomes_the_dominant_component}

![Blog-Snowflake-response-02.012.png](https://clickhouse.com/uploads/Blog_Snowflake_response_02_012_e41ab31195.png)

For ClickHouse, the fresh-data path is unchanged: the same ingest service handles ingest, sorting, merges, and materialized-view updates. As before, that costs: 2 compute units × 28 hours × $0.3903/hour \= **$21.86.**

For Snowflake, the ingest warehouse is also unchanged. The Gen2 X-Small ingest warehouse costs: 1.35 credits/hour × 28 hours × $3/credit \= **$113.40.**

The difference is refresh. To keep the pre-aggregated Interactive Table at Snowflake’s minimum 1-minute target, the refresh warehouse effectively has to run continuously. The final setup uses a Gen2 X-Large refresh warehouse. At 21.6 credits/hour and $3 per credit, that costs: 21.6 credits/hour × 28 hours × $3/credit \= **$1,814.40.**

Together, Snowflake’s Interactive Tables fresh-data path costs $1,927.80.

Before query cost is included, that is about 88× more than ClickHouse to keep the fresh-data path query-ready.

#### Query cost: interactive table reads get closer {#query_cost_interactive_table_reads_get_closer}

For query cost, we use the same per-second runtime normalization [described](/blog/real-time-analytics-cost-performance-snowflake-vs-clickhouse#query_cost_serving_the_same_schedule) in the standard setup section.

The chart below shows the total accumulated runtime and query cost for the Interactive Tables read workload.

![Blog-Snowflake-response-02.013.png](https://clickhouse.com/uploads/Blog_Snowflake_response_02_013_c6361b732c.png)

*All per-query run details are available in the CostBench repository: ClickHouse [dashboard queries](https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/clickhouse-cloud/results/mv/dashboard_20260609T154019Z.jsonl) and [drill-down queries](https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/clickhouse-cloud/results/raw/drilldown_20260617T162929Z.jsonl), Snowflake [dashboard queries](https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/snowflake/results/t1/dashboard_20260617T154602Z.jsonl) and [drill-down queries](https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/snowflake/results/t1/drilldown_20260617T154602Z.jsonl)*.

ClickHouse uses the same read service as before: 16 CPUs and 64 GiB RAM, or 8 compute units. 8 compute units × $0.3903/hour × 70.4 seconds \= **$0.061**

Snowflake uses a Small Interactive Warehouse. At 1.2 credits/hour and $3 per credit, that is $3.60/hour. 1.2 credits/hour × $3/credit × 144 seconds \= **$0.144**

ClickHouse is still about **2× faster** and **2.4× cheaper** on query compute, using the same read-side CPU count.

### Cost-performance: the full-path score {#costperformance_the_fullpath_score_2}

Now we can compare the full path directly: what it costs to keep fresh data query-ready, and how much runtime the system needs to serve the continuous workload.

![Blog-Snowflake-response-02.014.png](https://clickhouse.com/uploads/Blog_Snowflake_response_02_014_38a48b41f8.png)

Interactive Tables improve Snowflake’s score substantially compared with the standard setup.

But the full path is still much more expensive to run. Snowflake’s Interactive Tables setup scores **180× worse**.

That gap matters: 

> ClickHouse users could spend more on larger compute, beat the Interactive Tables latency by a wider margin, and still stay below Snowflake’s total cost.

## Why freshness mechanics matter {#why_freshness_mechanics_matter}

The results above also show a more basic difference in how each system keeps derived data fresh while new rows keep arriving.

![Blog-Snowflake-response-02.015.png](https://clickhouse.com/uploads/Blog_Snowflake_response_02_015_49b5b36e24.png)

① **Fresh data arrives continuously.**  
That is the starting point of the whole benchmark: the base table is constantly moving, so pre-aggregations have to keep up with a live stream, not a static dataset.

② **Snowflake materialized views refresh asynchronously.**  
That is exactly what showed up in the standard Snowflake setup: while ingest continued, the materialized view was repeatedly **60 to 72 minutes behind** the base table. Snowflake still returns up-to-date query results by combining the materialized view with missing rows from the raw table at query time, but that is also why dashboard latency became slow and unpredictable.

③ **Snowflake Interactive Tables use scheduled refresh.**  
Interactive Tables improve freshness control, but they still work through scheduled refreshes. For pre-aggregations, the smallest target lag is **1 minute**. That means the refresh warehouse becomes part of the continuous write path: it has to run at that cadence during ingest, and it has to be sized so each refresh finishes before the next one is due. If it cannot, lag accumulates. As the table grows, maintaining that 1-minute target becomes a scaling and cost problem.

④ **ClickHouse incremental materialized views update on ingest.**  
 ClickHouse takes a different path: materialized views are updated synchronously as new data is inserted. The pre-aggregated table therefore stays aligned with the base table instead of waiting for a separate refresh cycle.

⑤ **That changes which real-time use cases are possible.**  
 For dashboards, a 1-minute refresh target may be acceptable. For sub-minute decisioning workloads, especially in financial services and fraud detection, where the useful freshness window is measured in hundreds of milliseconds, scheduled refresh is already too late. In those cases, freshness determines whether the system can support the workload at all.

## Outlook: more paths and heavier workloads {#outlook_more_paths_and_heavier_workloads}

CostBench is a framework for testing the full real-time analytics path under different system designs.

### Managed ingest paths {#managed_ingest_paths}

The next variant we want to test is Snowflake’s managed ingest path, where Snowpipe Streaming can write directly into a raw-data Interactive Table, but [cannot directly maintain the pre-aggregated data](https://docs.snowflake.com/en/user-guide/snowpipe-streaming/snowpipe-streaming-table-support#insert-only-operations). 

![super_cool_07.gif](https://clickhouse.com/uploads/super_cool_07_47ea6fcb27.gif)

The comparable ClickHouse path is [ClickPipes](https://clickhouse.com/cloud/clickpipes). 

That will let us compare managed ingest on both sides without the lightweight client used in this benchmark writing the data directly.

### Higher query concurrency {#higher_query_concurrency}

We will also use the same framework to push the read side harder and scale the query workload independently, and test higher concurrency while fresh data continues to arrive.

### Heavier real-time datasets {#heavier_realtime_datasets}

As mentioned at the beginning, this run deliberately started at the easier end of the spectrum: a small, narrow dataset, a simple sorting key, and an arrival pattern that is favorable to Snowflake. 

Next, we will repeat the test at the other end: a much wider, heavier dataset with the kind of shape common in ClickHouse real-time analytics workloads.

That will show both sides of the spectrum: the clean case that gives Snowflake the best chance, and the heavier case where ClickHouse is designed to shine.

And of course, we are open to other setups Snowflake thinks should be tested. The framework is flexible; the important thing is that the comparison stays full-path.

## Conclusion: the full path changes the answer {#conclusion_the_full_path_changes_the_answer}

Snowflake’s response helped sharpen the question. Many of the suggestions were valid optimizations: simplify clustering, move reads to Interactive Tables, or tune the refresh path.

But real-time systems are full-path systems. Improving one stage can move the cost somewhere else: faster reads can require more refresh compute, fresher pre-aggregations can require a continuously running refresh warehouse, and better physical organization can increase maintenance work.

So we measured the whole path.

Some results improved. Interactive Tables made Snowflake reads much faster than the standard materialized-view setup. But once we measured the full path - ingest, physical organization, pre-aggregation freshness, refresh cost, and continuous query serving - the tradeoff became clearer.

In the original query-ready-data benchmark, ClickHouse delivered **28× better** write-side cost-performance than Snowflake. In this expanded benchmark, ClickHouse delivered **969× better** cost-performance than Snowflake’s standard materialized-view setup, and **180× better** than Snowflake’s Interactive Tables setup.

That is the main takeaway: [real-time analytics is not just about making queries fast](https://clickhouse.com/blog/selecting-a-real-time-analytical-database), but about keeping fresh data query-ready, keeping derived data fresh, and serving low-latency queries continuously without turning refresh into the dominant cost.

For sub-minute decisioning workloads, the freshness model matters even more. Among the tested paths, only ClickHouse incremental materialized views keep pre-aggregations continuously in sync with the base table without any lag.

> ClickHouse is built for cost-efficient real-time analytics across the full path. MergeTree tables keep raw data ordered and query-ready. AggregatingMergeTree tables keep pre-aggregations fresh with no refresh gap. And the query engine keeps latency low as data grows.

Our latest [migration story](https://clickhouse.com/blog/appcues-customer-engagement-analytics) shows the same full-path efficiency in production. Appcues moved real-time customer-facing analytics from Snowflake to ClickHouse Cloud. Across **1.31 PB of data and 410 billion events**. P95 query latency dropped from 20+ seconds to under 2 seconds, ingestion latency dropped from 10+ minutes to about 5 seconds, and analytics spend fell even as new workloads were added.

That is the path CostBench is designed to evaluate. We will keep testing more systems, more ingest paths, heavier datasets, and higher concurrency. Stay tuned.
