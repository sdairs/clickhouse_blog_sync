---
title: "Why BigQuery can’t match ClickHouse Cloud for real-time analytics"
date: "2026-10-08T10:49:15.465Z"
author: "Tom Schreiber and Lionel Palacin"
category: "Engineering"
excerpt: "ClickHouse Cloud delivered 438× better performance per dollar than BigQuery in CostBench. We trace the gap from fresh data arriving to fast answers coming back."
---

# Why BigQuery can’t match ClickHouse Cloud for real-time analytics

<style>
details.note-box {
  margin: 28px 0;
  background: #2B2B2B;
  color: #E2E8F0;
  border-left: 5px solid rgba(255,255,255,.1);
  border-radius: 12px;
}

details.note-box > summary {
  position: relative;
  padding: 18px 48px 18px 24px;
  cursor: pointer;
  list-style: none;
  font-size: 14px;
  font-weight: 600;
  line-height: 1.5;
  text-transform: uppercase;
  border-radius: 10px;
}

details.note-box > summary::-webkit-details-marker {
  display: none;
}

details.note-box > summary:hover {
  background: rgba(255,255,255,.05);
}

details.note-box > summary::after {
  content: "▶";
  position: absolute;
  right: 20px;
  color: #A0AEC0;
  font-size: 12px;
  transition: transform .2s;
}

details.note-box[open] > summary::after {
  transform: rotate(90deg);
}

details.note-box > .note-body {
  padding: 8px 24px 28px;
}

/* Comfortable line spacing */
details.note-box > .note-body > p,
details.note-box > .note-body li {
  font-size: 15px;
  line-height: 1.7;
}

/* Space between paragraphs */
details.note-box > .note-body > p {
  margin: 0 0 14px;
  padding: 0;
}

/* Larger breaks before main sections */
details.note-box > .note-body > p.note-heading {
  margin: 28px 0 8px;
  font-size: 14px;
  line-height: 1.5;
  letter-spacing: .025em;
  color: #E2E8F0;
}

/* Smaller breaks before subsections */
details.note-box > .note-body > p.note-subheading {
  margin: 22px 0 8px;
  line-height: 1.5;
  color: #E2E8F0;
}

details.note-box > .note-body > .note-heading:first-child {
  margin-top: 0;
}

/* Consistent list spacing */
details.note-box > .note-body > ul {
  margin: 0 0 16px;
  padding: 0 0 0 22px;
}

details.note-box > .note-body li {
  margin: 0;
  padding: 0;
}

details.note-box > .note-body li + li {
  margin-top: 8px;
}

details.note-box > .note-body > :last-child {
  margin-bottom: 0;
}
</style>

## TL;DR

Real-time systems vary dramatically in the cost and efficiency of carrying incoming data from arrival to query readiness. In this series, we follow that path to see how it shapes preparation cost, query cost, and query runtime.

Here, ClickHouse Cloud and BigQuery ingest 113.2 billion quotes while queries run. ClickHouse Cloud delivered **438× better end-to-end performance per dollar** under BigQuery Capacity pricing, and **512×** under On-demand pricing. The comparison traces where those differences begin.


## From fresh data to fast answers

[Real-time analytics](https://clickhouse.com/blog/selecting-a-real-time-analytical-database) must keep answering quickly as new data arrives. **[CostBench](https://clickhouse.com/blog/costbench-data-warehouse-cost-performance) tests that directly: queries run throughout continuous ingestion, and answers include newly arrived data.** Preparing that data efficiently lowers the cost of keeping it [query-ready](https://clickhouse.com/blog/costbench-real-time-performance-per-dollar#what-makes-data-query-ready) and leaves less work for queries, reducing their cost and runtime.

Columnar storage lets queries skip unused fields; ordering lets drill-downs skip unrelated quotes; current pre-aggregations let interactive aggregations combine prepared summaries. The diagram below follows how the [fresh-data path](https://clickhouse.com/blog/costbench-real-time-performance-per-dollar#real-time-systems-must-make-fresh-data-query-ready-as-it-arrives) changes query work as preparation keeps up or falls behind.


<iframe src="/uploads/01_fresh_data_path_query_work_balance_0bd1d8c818.html" frameborder="0" style="width: 100%; height: 500px; max-height: 800px;"></iframe>

CostBench measures ① preparation cost, ② query cost, and ③ runtime, then combines them into one [end-to-end performance-per-dollar score](https://clickhouse.com/blog/costbench-real-time-performance-per-dollar#turning-runtime-and-cost-into-performance-per-dollar).

This article follows those three effects through the ClickHouse-BigQuery comparison, from preparing incoming data to serving queries.


## The workload and the result

> **ClickHouse Cloud delivered 438× better end-to-end performance per dollar than BigQuery under Capacity pricing, and 512× under On-demand pricing, while ingestion and queries ran together.**

Both systems used their recommended real-time ingestion paths and native preparation features: ClickHouse asynchronous inserts; BigQuery Storage Write API committed streams, clustering, and incremental materialized views. CostBench streamed **113.2 billion stock-market quotes** at a target of **1 million rows per second**, with equivalent sorting or clustering keys and daily pre-aggregations by stock symbol. **Throughout ingestion, four interactive aggregate queries ran every ten minutes; two drill-down queries over raw quotes ran every hour.** Each query covered the history ingested so far, including newly arrived quotes. Query-result caching was disabled. 
 
CostBench calculates its **end-to-end performance-per-dollar score** using the formula shown below: **Score = (① preparation cost + ② normalized query cost) × ③ accumulated query runtime.** 

<iframe src="/uploads/02_costbench_end_to_end_score_1f0127fcd0.html" frameborder="0" style="width: 100%; height: 500px; max-height: 800px;"></iframe>

Preparation cost covers the complete fresh-data path. Normalized query cost prices the resources consumed by the queries; accumulated query runtime is the sum of their durations. **Lower scores are better.** BigQuery Capacity and On-demand are alternative prices for the same measured workload, with the same query latencies.






<details class="note-box">
  <summary>HOW DID WE MEASURE ① ② ③? (click to expand)</summary>
  <div class="note-body">
<iframe src="/uploads/02a_how_did_we_measure_e9e2d7852a.html" frameborder="0" style="width: 100%; height: 500px; max-height: 800px;"></iframe>
<iframe src="/uploads/02b_shared_costbench_harness_02f52cbc8c.html" frameborder="0" style="width: 100%; height: 500px; max-height: 800px;"></iframe>
    <p class="note-heading"><strong>SHARED HARNESS</strong></p>
    <p>Both systems used the same source dataset, schema, analytical workload, pacing model, query schedule, and result format. Destination-specific adapters handled delivery and timing. <a href="https://clickhouse.com/blog/costbench-real-time-performance-per-dollar">Part 1</a> explains the shared methodology; the <a href="https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/bigquery/BIGQUERY_BENCHMARK_CONTRACT.md">BigQuery benchmark contract</a> records this provider’s implementation.</p>
    <p class="note-heading"><strong>DATASET AND PREPARATION</strong></p>
    <p>The complete <a href="https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes#dataset">NBBO dataset</a> contains 113,219,565,734 narrow, 12-column rows. Raw tables used (sym, t), stock symbol and event timestamp; daily summaries used (sym, day), stock symbol and UTC day. The summaries maintained the counts, sums, and price minima and maxima used by the aggregate queries.</p>
    <p class="note-heading"><strong>CONTINUOUS WORKLOAD</strong></p>
    <p>Fresh rows were paced toward 1 million per second while aggregate and drill-down queries ran on their ten-minute and hourly schedules. This models data generated continuously and prepared as it arrives. BigQuery’s <a href="https://docs.cloud.google.com/bigquery/docs/materialized-views-create#use_materialized_views_with_max_staleness_option">max_staleness option</a> was left unset, so MV queries had to include newer base-table data.</p>
    <p class="note-heading"><strong>RECOMMENDED STACK AND SIZING</strong></p>
    <p>ClickHouse Cloud used a 16-CPU, 64-GiB read node. BigQuery used <a href="https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/bigquery/REAL_RUN.md">on-demand serverless query compute</a>, with dynamically assigned slots and no fixed reservation. This is not a comparison of two fixed 16-CPU allocations. The Capacity alternative prices the same measured slot consumption at the Enterprise list rate; it does not represent a separate capacity run.</p>
    <p class="note-heading"><strong>① PREPARATION COST</strong></p>
    <p>The full path includes ClickHouse’s complete two-node HA ingest service and BigQuery’s Storage Write API ingestion plus automatic MV refresh. BigQuery’s automatic reclustering has <a href="https://docs.cloud.google.com/bigquery/docs/clustered-tables#clustered_table_pricing">no separate charge</a>. Both Capacity and On-demand preparation totals retain the same ingestion meter and price refresh resources under their respective compute models.</p>
    <p class="note-heading"><strong>② QUERY COST AND ③ RUNTIME</strong></p>
    <p>ClickHouse query cost is recorded duration multiplied by its read-side compute rate. BigQuery Capacity uses job slot-seconds; On-demand uses billed bytes. Both BigQuery alternatives use the same recorded query durations for ③. These normalized costs describe accepted query work, rather than complete provider invoices.</p>
    <p class="note-heading"><strong>TARGET VERSUS OBSERVED RATE</strong></p>
    <p>BigQuery acknowledged the full logical dataset in about <strong>31.5 hours</strong>, averaging <strong>999,495 rows/s</strong>; ClickHouse completed its ingest in about <strong>36.75 hours</strong>, averaging approximately <strong>0.86 million rows/s</strong>. The <a href="https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/bigquery/results/bq-full-t2-20260810_152224/ingest/ingest_summary.json">ingest summary</a> records BigQuery’s acknowledged rows separately from the provider’s successful-write meter. That meter contains 113,172,471,254 successful rows; ClickHouse’s write-cost evidence contains 113,217,743,918 rows, a 0.040% difference. The query comparison uses the 113,219,565,734-row reference horizon.</p>
    <p class="note-heading"><strong>REPORTING WINDOW</strong></p>
    <p>Per-query latency plots stop at 100 billion rows. Preparation costs retain the complete ingestion meter and collected refresh usage. Accumulated query cost and runtime use the accepted active-ingestion observations through the reference endpoint; later query observations are excluded. Displayed totals are rounded. The pricing note states the refresh-export boundary and exclusions.</p>
  </div>
</details>


ClickHouse Cloud led in all three measured components:



① **Preparation cost:** $28.69 versus $243.09 Capacity / $264.59 On-demand.<br/>
② **Normalized query cost:** about $0.05 versus $4.75 Capacity / $24.80 On-demand.<br/>
③ **Accumulated query runtime:** 58.29 seconds versus 49.36 minutes under either BigQuery pricing model.

The charts below show how those costs and runtimes accumulated while data arrived.

<iframe src="/uploads/03_accumulated_cost_and_runtime_61fb780a64.html" frameborder="0" style="width: 100%; height: 500px; max-height: 800px;"></iframe>


The next chart applies the score formula to those components: ClickHouse’s **8.62× lower combined cost** under Capacity pricing, or **10.07× lower** under On-demand, combines with **50.8× lower accumulated query runtime**. 

<iframe src="/uploads/04_final_ranking_score_fbd47268f0.html" frameborder="0" style="width: 100%; height: 500px; max-height: 800px;"></iframe>


<details class="note-box">
  <summary>PRICING, FORMULAS, AND THE 438× / 512× SCORES (click to expand)</summary>
  <div class="note-body">
    <p class="note-heading"><strong>PRICING BASIS</strong></p>
    <p>ClickHouse Cloud uses <strong>$0.3903 per compute unit (CU) per hour</strong>. BigQuery uses the checked-in <a href="https://cloud.google.com/bigquery/pricing">US list rates</a>: <strong>$0.025/GiB</strong> for Storage Write API ingestion, <strong>$0.06/slot-hour</strong> for Enterprise Capacity, and <strong>$6.25/TiB</strong> for On-demand analysis. The <a href="https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/bigquery/results/bq-full-t2-20260810_152224/charts/full_path_cost_performance_clickhouse_vs_bigquery_wide_summary.json">accepted summary</a> retains full-precision inputs. Capacity and On-demand are alternative modeled costs for the same jobs.</p>
    <p class="note-heading"><strong>① COMPLETE PREPARATION COST</strong></p>
    <p>This covers the complete streaming-ingestion meter, automatic reclustering at no separate charge, and the collected MV-refresh usage.</p>
    <p class="note-heading"><strong>CLICKHOUSE CLOUD</strong></p>
    <p>2 CUs × 36.75 hours × $0.3903/CU-hour = <strong>$28.68705</strong>, including both HA ingest nodes.</p>
    <p class="note-heading"><strong>BIGQUERY INGESTION</strong></p>
    <p>The <a href="https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/bigquery/costs/out/bq-full-t2-20260810_152224/ingest.json">Write API meter</a> records <strong>9,642.7384687 GiB × $0.025/GiB = $241.06846172</strong>, using successful input bytes. Client-acknowledged Arrow bytes and provider-metered input bytes are distinct measures.</p>
    <p class="note-heading"><strong>BIGQUERY CLUSTERING</strong></p>
    <p>Automatic reclustering is included without a separate charge. No paid manual reorganization job is added.</p>
    <p class="note-heading"><strong>BIGQUERY MV REFRESH</strong></p>
    <p>The <a href="https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/bigquery/costs/out/bq-full-t2-20260810_152224/mv_refresh.json">362-job export</a> contains <strong>121,166.568 slot-seconds</strong>, priced at $0.06/slot-hour for <strong>$2.0194428</strong>, or <strong>4,137,783,656,448 billed bytes</strong>, priced at $6.25/TiB for <strong>$23.52057695</strong>. Preparation totals are <strong>$243.08790452 Capacity</strong> and <strong>$264.58903867 On-demand</strong>.</p>
    <p class="note-heading"><strong>② NORMALIZED QUERY COST</strong></p>
    <p>BigQuery prices the same accepted query jobs by consumed slot-seconds or billed bytes. ClickHouse prices recorded duration at its read-side rate.</p>
    <p class="note-heading"><strong>CLICKHOUSE CLOUD</strong></p>
    <p>8 CUs × $0.3903/CU-hour × (10.324s aggregate + 47.962s drill-down) ÷ 3,600 ≈ <strong>$0.05055</strong>, using the rounded cost-summary inputs.</p>
    <p class="note-heading"><strong>BIGQUERY CAPACITY</strong></p>
    <p>Aggregate jobs cost <strong>$4.29558297</strong> and drill-down jobs <strong>$0.45264198</strong>, totaling <strong>$4.74822495</strong>. The combined <strong>79.1370825 slot-hours × $0.06/slot-hour</strong> allocation uses recorded job slot consumption.</p>
    <p class="note-heading"><strong>BIGQUERY ON-DEMAND</strong></p>
    <p>Aggregate jobs cost <strong>$20.94800472</strong> and drill-down jobs <strong>$3.85683775</strong>, totaling <strong>$24.80484247</strong>. The combined billed volume is <strong>3.9687748 TiB × $6.25/TiB</strong>. This is an alternative to Capacity pricing, not an added component.</p>
    <p class="note-heading"><strong>COST BOUNDARY</strong></p>
    <p>The preparation model keeps the full successful-write meter and all 362 collected refresh jobs, including the terminal refresh after producer completion. Query totals exclude later post-ingestion observations and evidence-collector jobs. Database storage, free tiers, discounts, idle/minimum capacity charges, producer infrastructure, and network charges are excluded.</p>
    <p class="note-heading"><strong>③ ACCUMULATED QUERY RUNTIME</strong></p>
    <p>ClickHouse: <strong>10.324s aggregate + 47.962s drill-down = 58.286s</strong>. BigQuery: <strong>2,751.868s aggregate + 209.518s drill-down = 2,961.386s</strong> under either pricing model.</p>
    <p class="note-heading"><strong>COMPARISON BOUNDARY</strong></p>
    <p>① retains complete-ingest preparation usage. ② and ③ use 190 four-query aggregate batches and 33 two-query drill-down batches, aligned by row progress through the reference horizon. Latency statistics use the separate 100-billion-row window. The Capacity alternative changes the price applied to measured resources; it does not change query hardware or rerun the workload.</p>
    <p class="note-heading"><strong>FINAL SCORES</strong></p>
    <p>ClickHouse: <strong>($28.68705 + $0.05055) × 58.286 = 1,674.99975</strong>. BigQuery Capacity: <strong>($243.08790452 + $4.74822495) × 2,961.386 = 733,938.44411</strong>, a <strong>438.172×</strong> ratio. BigQuery On-demand: <strong>($264.58903867 + $24.80484247) × 2,961.386 = 857,006.98809</strong>, a <strong>511.646×</strong> ratio. Headline values round to <strong>438× and 512×</strong>.</p>
  </div>
</details>



---

## 438× better real-time performance per dollar

Interested in seeing how ClickHouse works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-2555-438-better-real-time-performance-per-dollar-sign-up&utm_blogctaid=2555)

---

All benchmark code and results are available in the [CostBench repository](https://github.com/ClickHouse/CostBench/tree/main/full-path-realtime/quotes). The stock-quotes dataset requires a [separate data license](https://github.com/ClickHouse/CostBench/tree/main/full-path-realtime/quotes#data-source-and-licensing), so the data itself cannot be redistributed.

To explain that result, we follow the same path as the data: preparation first, then query serving.


## How ClickHouse Cloud prepares incoming data

The benchmark used a dedicated ClickHouse Cloud ingest service with **two 2-CPU nodes for high availability**, the smallest HA configuration that sustained the target during calibration. The shared client sent rows through [asynchronous inserts](https://clickhouse.com/blog/asynchronous-data-inserts-in-clickhouse) built into each node.

The diagram below shows those same nodes handling ① columnar storage, ② ordering raw data, and ③ ordered pre-aggregation, plus background merges, on **four CPU cores in total**.

<iframe src="/uploads/05_clickhouse_fresh_data_path_ef0670f098.html" frameborder="0" style="width: 100%; height: 500px; max-height: 800px;"></iframe>


**① Store in columns and ② order data:** When an ingest node flushes its asynchronous-insert buffer, it sorts raw quotes by the [MergeTree](https://clickhouse.com/docs/engines/table-engines/mergetree-family/mergetree) table’s (sym, t) key, stock symbol and event timestamp, and writes an ordered [data part](https://clickhouse.com/docs/parts).

**③ Order and pre-aggregate data:** The same node runs the [incremental MV](https://clickhouse.com/docs/materialized-view/incremental-materialized-view) query over the incoming block in memory, computes aggregate states, and sorts the results by the [AggregatingMergeTree](https://clickhouse.com/docs/engines/table-engines/mergetree-family/aggregatingmergetree) table’s (sym, day) key before writing an ordered part containing the summaries.

[Background merges](https://clickhouse.com/docs/merges) consolidate parts in both tables.

> The result: raw data and pre-aggregations [advance together](https://clickhouse.com/docs/resources/support-center/knowledge-base/materialized-views/are-materialized-views-inserted-asynchronously) from the same flushed insert block, without a separate refresh cycle.

<details class="note-box">
  <summary>HOW MUCH WORK DID THE FOUR-CORE INGEST SERVICE HANDLE? (click to expand)</summary>
  <div class="note-body">
    <p>The <a href="https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/clickhouse-cloud/results_t2">ClickHouse writer-utilization results</a> show ingestion continuing alongside background maintenance. CPU usage remained around 3.1 of the 4 available cores, tracked memory stayed within capacity, background merges processed several million rows per second, and the maximum active-part count per partition stayed around 100. These diagnostics describe the ClickHouse source run reused for this comparison.</p>
    <p>Both nodes were retained for high availability, so the preparation cost includes the complete two-node deployment.</p>
  </div>
</details>

Now follow the same three preparation tasks through BigQuery, where streaming ingestion, clustering, and MV refresh advance separately.


## How BigQuery prepares incoming data

The benchmark used [BigQuery’s Storage Write API](https://docs.cloud.google.com/bigquery/docs/write-api-grpc) with application-created committed streams, sending Arrow record batches over long-lived gRPC connections. Successful appends made the rows available for queries.

As shown below, the streaming path handles ① columnar storage, while BigQuery manages ② clustering and ③ incremental MV refresh asynchronously.

<iframe src="/uploads/06_bigquery_fresh_data_path_00e0e64dfb.html" frameborder="0" style="width: 100%; height: 500px; max-height: 800px;"></iframe>

**① Store in columns:** The Storage Write API delivers rows into a [native BigQuery table](https://docs.cloud.google.com/bigquery/docs/tables-intro#standard-tables). BigQuery manages columnar storage separately from query compute; an acknowledged committed append does not guarantee that the table’s clustering is fully optimized.

**② Order data:** The raw table used [CLUSTER BY sym, t](https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/bigquery/create.sql), giving symbol filters a way to prune storage blocks. BigQuery maintains that layout with [automatic reclustering](https://docs.cloud.google.com/bigquery/docs/clustered-tables#automatic_reclustering); it does not guarantee that every appended batch is already ordered. 
 
**③ Order and pre-aggregate data:** A [native incremental MV](https://docs.cloud.google.com/bigquery/docs/materialized-views-intro#types) grouped quotes by (sym, day), maintaining counts, sums, and price extrema, with the same clustering key. Automatic refresh was enabled with refresh_interval_minutes = 1, the [minimum supported interval](https://docs.cloud.google.com/bigquery/docs/materialized-views-manage#frequency_cap). This allows automatic refreshes no more often than once per minute; it does not guarantee that summaries become current within one minute. 


> The result: BigQuery can make new rows queryable before clustering catches up, while pre-aggregations advance through a separate refresh cycle. 
 
 <details class="note-box">
  <summary>WHY THESE INGESTION PATHS, AND HOW WERE THEY BUFFERED? (click to expand)</summary>
  <div class="note-body">
    <p class="note-heading"><strong>THE SAME INGESTION PROBLEM</strong></p>
    <p>Frequent application writes must become efficient storage writes. ClickHouse buffered INSERT requests on its ingest nodes. BigQuery accepted Arrow batches through committed Storage Write API streams, without a Kafka broker or file landing stage in the measured path.</p>
    <p class="note-heading"><strong>BIGQUERY’S STREAMING PATH</strong></p>
    <p>The <a href="https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/bigquery/REAL_RUN.md">full-run configuration</a> used <strong>40 committed streams</strong>, explicit row offsets, <strong>131,000-row client batches</strong>, and a 16,000,000-byte request limit. A global rate controller paced append starts toward 1 million rows/s. Successful acknowledgments, rather than rows merely read from Parquet, defined progress.</p>
    <p class="note-heading"><strong>CLICKHOUSE’S NATIVE PATH</strong></p>
    <p>Ordinary INSERT requests with async_insert enabled were buffered on each receiving node. An <a href="https://clickhouse.com/docs/optimize/asynchronous-inserts">adaptive flush timeout</a> responded to incoming traffic. Ordering and pre-aggregation ran on the ingest nodes; the dedicated <a href="https://clickhouse.com/docs/cloud/reference/warehouses">ingest service</a> shared storage with the independently sized read service.</p>
    <p class="note-heading"><strong>SHARED PACING</strong></p>
    <p>Both adapters read the same Parquet dataset and decoded the same schema under the same target-rate model. Parallelism and client batch sizes were adapted to each destination’s API; they were not forced to be identical.</p>
    <p class="note-heading"><strong>CLICKHOUSE BATCHES</strong></p>
    <p>The client sent 3,000-row batches through asynchronous inserts. Default buffering flushed at the first of three thresholds: 100 MiB buffered, an adaptive timeout between 50 milliseconds and 1 second, or 450 queued insert queries.</p>
    <p class="note-heading"><strong>BIGQUERY BATCHES</strong></p>
    <p>Each worker owned one committed stream and sent serialized Arrow record batches. This was live streaming delivery; rows were not uploaded as files for a later load job. No pending-stream batch commit was used.</p>
    <p class="note-heading"><strong>BATCH-SIZE BOUNDARY</strong></p>
    <p>The 3,000-row ClickHouse and 131,000-row BigQuery sizes describe client delivery. They do not specify the final MergeTree part or BigQuery storage-block size.</p>
    <p class="note-heading"><strong>RETRIES AND RECONCILIATION</strong></p>
    <p>Explicit offsets let BigQuery detect an exact replay after a lost acknowledgment. The <a href="https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/bigquery/BIGQUERY_BENCHMARK_CONTRACT.md">client contract</a> counts a confirmed replay once and reconnects. This provides exactly-once retry handling within the live run, rather than crash-resumable source checkpointing. Client acknowledgments, provider successful-write rows, and table metadata are kept as distinct evidence.</p>
    <p class="note-heading"><strong>INCREMENTAL MAINTENANCE</strong></p>
    <p>The MV definition used supported COUNT, MIN, MAX, and SUM operations over an append-only source. The <a href="https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/bigquery/costs/out/bq-full-t2-20260810_152224/mv_refresh.json">refresh-job export</a> contains <strong>362 successful automatic refresh jobs</strong> with no failed jobs. Refresh slot-seconds and billed bytes are recorded independently from the dashboard jobs.</p>
    <p class="note-heading"><strong>LAYOUT AND PARTITIONING</strong></p>
    <p>The raw table was deliberately unpartitioned because D1 and D2 filter by symbol across the full ingested history, without a time predicate. Clustering on (sym, t) serves that workload. Automatic reclustering is managed and free of a separate compute charge; a manual rewrite was not added to the benchmark.</p>
  </div>
</details>


## What this means for freshness and preparation cost


### Pre-aggregation lag

ClickHouse updates summaries during inserts; BigQuery refreshes them asynchronously. The chart below shows **one observed lag maximum per complete refresh cycle**: BigQuery’s plotted cycle peaks average **4.9 minutes** and reach **6.1 minutes**. ClickHouse’s raw data and summaries advance together in this setup.

<iframe src="/uploads/07_pre_aggregation_lag_c42ee28fd6.html" frameborder="0" style="width: 100%; height: 500px; max-height: 800px;"></iframe>

This measures summary maintenance lag. BigQuery still returns current MV answers by including newer base-table rows at query time.

<details class="note-box">
  <summary>HOW WAS PRE-AGGREGATION LAG MEASURED? (click to expand)</summary>
  <div class="note-body">
    <p class="note-heading"><strong>BIGQUERY SERIES</strong></p>
    <p>The <a href="https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/bigquery/results/bq-full-t2-20260810_152224/charts/mv_lag_clickhouse_vs_bigquery_wide_summary.json">freshness monitor</a> sampled <a href="https://docs.cloud.google.com/bigquery/docs/information-schema-materialized-views#schema">refresh_watermark</a> once a minute. Lag is the elapsed time from that watermark to the observation. <strong>1,889 active samples</strong> are included through the first full-row observation; <strong>441 later samples</strong> are excluded. This is a maintenance-watermark measure, not answer staleness.</p>
    <p class="note-heading"><strong>DISPLAY AND READOUTS</strong></p>
    <p>The chart selects one measured maximum from each fully observed refresh-watermark cycle, producing <strong>359 cycle peaks</strong>. The first and last partial cycles are excluded. Their mean is <strong>4.861 minutes</strong> and maximum <strong>6.100 minutes</strong>, rounded to 4.9 and 6.1. The full active raw series has an <strong>8.023-minute startup peak</strong> that is outside this cycle-peak display. Readouts follow the displayed curve.</p>
    <p class="note-heading"><strong>CLICKHOUSE BASELINE</strong></p>
    <p>The zero line is a benchmark-semantic baseline, not a separately polled provider metric. The raw table and incremental MV consume the same flushed insert block, with no independent summary-refresh interval between them. It does not claim zero source-to-query ingestion delay.</p>
  </div>
</details>

> ClickHouse maintained summaries alongside raw data; BigQuery’s plotted refresh-cycle lag peaks averaged 4.9 minutes, leaving newer rows to be included at query time.

Those newer rows add work to queries. First, compare the cost of the preparation path itself.


### Cost of keeping incoming data query-ready

ClickHouse handles ① columnar storage, ② ordering raw data, and ③ ordered pre-aggregation within its engine. BigQuery combines separately priced streaming ingestion and MV maintenance; automatic reclustering adds no separate charge. The chart below compares the complete preparation costs under both BigQuery pricing models.

<iframe src="/uploads/08_fresh_data_path_cost_71bc08de76.html" frameborder="0" style="width: 100%; height: 500px; max-height: 800px;"></iframe>

ClickHouse’s complete ingest service cost **$28.69**. BigQuery’s Storage Write API cost **$241.07** (①); automatic reclustering (②) had no separate charge. MV refresh (③) adds **$2.02** under Capacity pricing or **$23.52** under On-demand, giving preparation totals of **$243.09** and **$264.59**, respectively. 
 
> ClickHouse handled the complete preparation path at **8.5× lower cost than BigQuery Capacity**, and **9.2× lower than On-demand**. 
 
Now follow the raw data and summaries into query serving.


## How ClickHouse Cloud serves queries

Ordered raw data lets drill-downs skip unrelated rows; pre-aggregations let interactive aggregations combine prepared results instead of recalculating them from individual quotes. The diagram below shows both paths through ClickHouse Cloud’s read service: **one node with 16 CPUs and 64 GiB of memory**.

<iframe src="/uploads/09_clickhouse_query_serving_3cdd0e160e.html" frameborder="0" style="width: 100%; height: 500px; max-height: 800px;"></iframe>

**Drill-downs:** Queries prune ordered raw data in the [event-level MergeTree table](https://clickhouse.com/docs/engines/table-engines/mergetree-family/mergetree). Filtering by symbol, the leading column of its (sym, t) sorting key, lets the read service skip unrelated quotes.

**Interactive aggregations:** Queries read current pre-aggregations from the [AggregatingMergeTree table](https://clickhouse.com/docs/engines/table-engines/mergetree-family/aggregatingmergetree), combining prepared counts, sums, minima, and maxima from a much smaller set of daily summary rows. There is no independent refresh to wait for. 
 
> The result: drill-downs prune ordered raw data; interactive aggregations read summaries kept current during ingestion.

BigQuery follows the same two query paths, with additional work when clustering or summary refresh falls behind.


## How BigQuery serves queries

The diagram below follows both workloads through [BigQuery’s serverless compute pool](https://docs.cloud.google.com/bigquery/docs/slots). Slots are assigned dynamically; there is no dedicated warehouse with a fixed CPU count in this run.


<iframe src="/uploads/10_bigquery_query_serving_af78b7f070.html" frameborder="0" style="width: 100%; height: 500px; max-height: 800px;"></iframe>


**Drill-downs:** Queries read the [clustered raw table](https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/bigquery/queries_raw.sql) directly. Filtering on sym can prune unrelated blocks, but newly arrived data may need scanning before reclustering has optimized its layout.

**Interactive aggregations:** Queries target the [incremental MV](https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/bigquery/queries_mv.sql) and combine its summaries with changes added to the base table since the last refresh. This [catch-up work](https://docs.cloud.google.com/bigquery/docs/materialized-views-use#incremental_updates) keeps answers current even when the MV watermark trails incoming data.

Both paths can therefore encounter unfinished preparation: drill-downs may scan data whose clustering is incomplete; aggregate queries must include rows that refresh has not yet summarized.

<details class="note-box">
  <summary>HOW DO BIGQUERY’S CURRENT ANSWERS AND COMPUTE MODELS WORK? (click to expand)</summary>
  <div class="note-body">
    <p class="note-heading"><strong>CURRENT-ANSWER CONTRACT</strong></p>
    <p>With max_staleness unset, a direct materialized-view query includes base-table changes not yet represented in the MV. A lagging refresh watermark does not mean that the returned answer is stale. It means some of the preparation remains on the query path.</p>
    <p class="note-heading"><strong>REFRESH CONTRACT</strong></p>
    <p>The one-minute refresh interval is a frequency cap. Automatic refresh is best effort and can complete less often under load. Refresh-watermark lag and query latency are measured separately; the benchmark does not assign the entire latency gap to delta processing.</p>
    <p class="note-heading"><strong>COMPUTE CONTRACT</strong></p>
    <p>The measured jobs ran on on-demand, dynamically allocated slots. Enterprise Capacity pricing applies $0.06 per slot-hour to the measured job slot-seconds. It does not replay the jobs on a fixed reservation or change their measured latencies.</p>
    <p class="note-heading"><strong>ON-DEMAND CONTRACT</strong></p>
    <p>The alternative applies $6.25 per TiB to each job’s billed bytes. Bytes and slot-seconds describe the same jobs under different pricing conventions; their costs are never added together.</p>
    <p class="note-heading"><strong>VISIBILITY BOUNDARY</strong></p>
    <p>A successful committed append makes rows queryable, while table metadata can update later. The runner’s progress signal uses acknowledged rows. Queryability, metadata updates, clustering, and summary refresh remain distinct milestones.</p>
  </div>
</details>

> The result: BigQuery drill-downs can scan newly arrived data before clustering catches up; interactive aggregations include the newer rows its summaries have not yet incorporated.


## What this means for query performance and cost


### Drill-downs over ordered raw data

Both systems used (sym, t) keys, with ClickHouse ordering rows during inserts and BigQuery managing clustering asynchronously. [D1 and D2](https://clickhouse.com/blog/costbench-real-time-performance-per-dollar#the-continuous-query-workload) investigate one stock’s growing history directly: hourly price summaries and a risk-and-liquidity profile. The chart below follows this raw-data path, bypassing the pre-aggregation MV.

<iframe src="/uploads/11_drill_down_query_latency_41c78bd93b.html" frameborder="0" style="width: 100%; height: 500px; max-height: 800px;"></iframe>

ClickHouse Cloud is yellow; BigQuery is blue.

<details class="note-box">
  <summary>HOW WERE QUERY LATENCIES AND ACCUMULATED RESULTS COMPARED? (click to expand)</summary>
  <div class="note-body">
    <p class="note-heading"><strong>QUERY DEFINITIONS</strong></p>
    <p>Part 1 describes A1-A4 and D1-D2. The <a href="https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/bigquery/queries_raw.sql">BigQuery SQL</a> preserves the symbol filters, full-history scope, grouping, ordering, and limits. D2 uses population central moments and APPROX_QUANTILES for percentiles; the percentile algorithm differs from ClickHouse’s quantilesTDigest and requires tolerance-based comparison.</p>
    <p class="note-heading"><strong>CACHE POLICY</strong></p>
    <p>Query-result caching was disabled with <a href="https://docs.cloud.google.com/bigquery/docs/cached-results#disabling_retrieval_of_cached_results">use_query_cache=False</a>. Underlying data caches were allowed to operate normally; they were not flushed between queries.</p>
    <p class="note-heading"><strong>TIMING</strong></p>
    <p>BigQuery latency is the completed job’s finalExecutionDurationMs divided by 1,000; ClickHouse uses its recorded runner duration. Median, P99, and maximum pool unsmoothed per-query observations with <strong>0 &lt; raw_rows ≤ 100 billion</strong>. P99 uses linear interpolation. The recorded timing convention is retained in accumulated runtime.</p>
    <p class="note-heading"><strong>LATENCY CHARTS</strong></p>
    <p>Each system is plotted at its own observed ingestion progress. Aggregate trends use a centered seven-observation rolling median; drill-downs use five observations, with shrinking edge windows. No outliers are removed. The curves are display smoothing; the statistics and accumulated totals use the original recorded durations.</p>
    <p class="note-heading"><strong>INTERACTIVE READOUTS</strong></p>
    <p>Values below the plots follow the displayed trends at the selected row count. Logarithmic scales keep milliseconds and seconds readable together; Linear shows absolute differences. Each chart has its own playback and row-position controls.</p>
    <p class="note-heading"><strong>ACCEPTED ACCUMULATED WORKLOAD</strong></p>
    <p>The <a href="https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/bigquery/results/bq-full-t2-20260810_152224/charts/full_path_cost_performance_clickhouse_vs_bigquery_wide_summary.json">selection</a> contains <strong>190 four-query aggregate batches</strong> and <strong>33 two-query drill-down batches</strong> per system: <strong>760 + 66 = 826 executions</strong>. ClickHouse observations are aligned with BigQuery row progress through the <strong>113,219,565,734-row reference horizon</strong>. The initial observation is retained where present; later post-ingestion observations are excluded.</p>
    <p class="note-heading"><strong>ACCUMULATED CHARTS</strong></p>
    <p>Query durations are added at corresponding ingestion counts as step sums, without smoothing or interpolating future executions into earlier positions. Preparation-cost lines allocate the complete-ingest total proportionally by row progress; they are not metered cost-at-time traces. The score sums query durations, not elapsed ingestion time.</p>
  </div>
</details>

**ClickHouse Cloud:**



* **722.5 ms median** - 4.47× faster than BigQuery
* **1.15 s P99** - 3.90× faster
* **1.18 s maximum** - 4.05× faster

Accumulated runtime was **47.96 seconds** across the 33 two-query batches. Both drill-downs stayed near or below one second for most of the plotted window.

**BigQuery:**



* **3.232 s median**
* **4.49 s P99**
* **4.78 s maximum**

Accumulated runtime was **209.52 seconds** across the same 33 batches. Both BigQuery drill-downs remained in the multi-second range as the raw table grew.

> Across the drill-down workload, ClickHouse Cloud was **4.37× faster overall**.


### Interactive aggregations over ordered pre-aggregated data

Daily pre-aggregations let [A1-A4](https://clickhouse.com/blog/costbench-real-time-performance-per-dollar#the-continuous-query-workload) combine prepared counts, sums, and price minima and maxima. A1-A2 filter summaries by symbol; A3-A4 read across all symbols. ClickHouse reads current summaries; BigQuery must also include newer base-table rows. The chart below shows aggregate latency while ingestion continues.

<iframe src="/uploads/12_aggregate_query_latency_994f189502.html" frameborder="0" style="width: 100%; height: 500px; max-height: 800px;"></iframe>

**ClickHouse Cloud:**



* **13 ms median** - 270× faster than BigQuery
* **42 ms P99** - 141× faster
* **111 ms maximum** - 62.5× faster

Accumulated runtime was **10.32 seconds** across the 190 four-query batches.

**BigQuery:**



* **3.508 s median**
* **5.86 s P99**
* **6.93 s maximum**

Accumulated runtime was **45.86 minutes** across the same 190 batches. All four aggregate queries remained in seconds while ClickHouse served them in milliseconds. BigQuery’s current-answer path includes newer rows alongside the refreshed summaries.

> Across the interactive-aggregation workload, ClickHouse Cloud was **267× faster overall**, with summaries maintained during inserts.


### Accumulated query cost and runtime

Interactive aggregations account for most of BigQuery’s accumulated query runtime. The charts below combine both workloads and show their query costs under Capacity and On-demand pricing.

<iframe src="/uploads/13_query_runtime_and_cost_d6b148c2ca.html" frameborder="0" style="width: 100%; height: 500px; max-height: 800px;"></iframe>

ClickHouse Cloud accumulated **58.29 seconds** of query runtime and BigQuery **49.36 minutes**. Normalized query cost was about **$0.05** for ClickHouse, versus **$4.75 Capacity** or **$24.80 On-demand** for BigQuery. 

> ClickHouse Cloud served the query workload **50.8× faster overall**, with **94× lower normalized query cost than BigQuery Capacity**, and **491× lower than On-demand**.


## From the field: METRO Markets and Fountain

METRO Markets’ adoption of ClickHouse Cloud shows the production benefits of faster queries and more predictable costs for real-time analytics. The team chose ClickHouse after testing it alongside BigQuery and Snowflake against its production queries. ClickHouse ran faster on both large and small queries, with one query improving from **four seconds to under 200 milliseconds**. It now powers near-real-time seller dashboards and company-wide analytics, while giving the team more predictable costs. [Read METRO Markets’ story](https://clickhouse.com/blog/metro-markets-data-warehouse).

Fountain’s move from a batch analytics stack that included BigQuery to ClickHouse Cloud shows the production benefits of fresher data and faster queries for real-time applications. It now uses ClickPipes and ClickHouse Cloud to power its frontline hiring platform, Cue. Data refresh delays fell from three hours to under two minutes, most queries now return in under a second, and the company reports roughly **66% lower platform costs**. Incremental materialized views prepare incoming data as it arrives, reducing the work needed at query time. [Read Fountain’s story](https://clickhouse.com/blog/fountain-agentic-ai-for-high-volume-hiring). 
 
CostBench evaluates that efficiency across the complete analytics path, from preparing incoming data to serving queries. 


## BigQuery can’t match ClickHouse Cloud for real-time analytics

While fresh data kept arriving, ClickHouse Cloud led in all three measured components:



① Preparation cost: 8.5× lower than BigQuery Capacity / 9.2× lower than On-demand.<br/>
② Normalized query cost: 94× lower than Capacity / 491× lower than On-demand.<br/>
③ Accumulated query runtime: 50.8× lower under either BigQuery pricing model.

The final chart brings these results together, plotting combined preparation and normalized query cost against accumulated query runtime as fresh data arrives.

<iframe src="/uploads/14_end_to_end_cost_vs_accumulated_query_clickhouse_bigquery_9087c57adb.html" frameborder="0" style="width: 100%; height: 500px; max-height: 800px;"></iframe>

Up is lower total modeled cost; right is lower accumulated query runtime. 

> **ClickHouse Cloud delivered 438× better end-to-end performance per dollar than BigQuery Capacity, and 512× better than On-demand, while continuously ingesting data and serving current answers.**

The difference starts before a query arrives. ClickHouse orders raw data and builds current summaries during inserts. BigQuery makes new rows queryable while clustering and MV refresh continue in the background; its aggregate queries include the rows refresh has not yet summarized.

 
That is why BigQuery can’t match ClickHouse Cloud for real-time analytics.




