---
title: "Why Databricks can’t match ClickHouse Cloud for real-time analytics"
date: "2026-10-06T12:26:14.709Z"
author: "Tom Schreiber and Lionel Palacin"
category: "Engineering"
excerpt: "ClickHouse Cloud delivered 752× better performance per dollar than Databricks in CostBench. We trace the gap from fresh data arriving to fast answers coming back."
---

# Why Databricks can’t match ClickHouse Cloud for real-time analytics

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

Real-time systems differ dramatically in the cost and efficiency of making incoming data query-ready.
**In this series, we trace the path from data arrival to answers**, showing how it shapes preparation cost, query cost, and query runtime.

Here, we compare ClickHouse Cloud and Databricks while streaming 113.2 billion quotes and running queries. **ClickHouse Cloud delivered 752× better end-to-end performance per dollar** than the tested Databricks stack, whose summaries could lag behind incoming data.

## From fresh data to fast answers

[Real-time analytics](https://clickhouse.com/blog/selecting-a-real-time-analytical-database) has to stay fast as fresh data arrives. **[CostBench](https://clickhouse.com/blog/costbench-data-warehouse-cost-performance) tests this under continuous ingestion: queries run while the dataset grows.** Efficient preparation lowers the cost of making that data [query-ready](https://clickhouse.com/blog/costbench-real-time-performance-per-dollar#what-makes-data-query-ready) and reduces the work left for queries, lowering their cost and runtime.

Columnar storage lets queries skip unused fields; ordering lets drill-downs skip unrelated quotes; current pre-aggregations let interactive aggregations combine prepared summaries. The diagram below shows how this [fresh-data path](https://clickhouse.com/blog/costbench-real-time-performance-per-dollar#real-time-systems-must-make-fresh-data-query-ready-as-it-arrives) shapes the scanning and aggregation left for queries as preparation keeps up or falls behind. 

<iframe src="/uploads/01_fresh_data_path_query_work_balance_5a208c9817.html" frameborder="0" style="width: 100%; height: 500px; max-height: 800px;"></iframe>

CostBench measures ① preparation cost, ② query cost, and ③ runtime, then combines them into one [end-to-end performance-per-dollar score](https://clickhouse.com/blog/costbench-real-time-performance-per-dollar#turning-runtime-and-cost-into-performance-per-dollar).

This article follows those three effects through the ClickHouse–Databricks comparison, from preparing incoming data to serving queries.

This comparison uses Databricks Serverless SQL for query serving. Lakehouse//RT, Databricks’ new real-time warehouse currently in Beta, is not included.

## The workload and the result

> **ClickHouse Cloud delivered 752× better end-to-end performance per dollar than Databricks in this continuous-ingestion workload.**

Both systems used their recommended low-latency ingestion paths and native preparation features: ClickHouse asynchronous inserts; Databricks [Zerobus Ingest](https://docs.databricks.com/aws/en/ingestion/zerobus-overview#advantages), liquid clustering, and incremental materialized views. CostBench streamed **113.2 billion stock-market quotes** at a target of **1 million rows per second**, using matching sorting or clustering keys and daily pre-aggregations by stock symbol. **During ingestion, four interactive aggregate queries ran every ten minutes; two drill-down queries ran every hour.** Queries covered the growing history through the raw tables or maintained summaries. **Read-side compute was matched at 16 CPUs**, with query-result caching disabled.  
 
CostBench calculates its **end-to-end performance-per-dollar score** using the formula shown below: **Score = (① preparation cost + ② normalized query cost) × ③ accumulated query runtime.**

<iframe src="/uploads/02_costbench_end_to_end_score_ce47f605f4.html" frameborder="0" style="width: 100%; height: 500px; max-height: 800px;"></iframe>

Preparation cost covers the complete fresh-data path. Normalized query cost prices recorded query runtimes at the applicable read-side compute rates. Accumulated query runtime is the sum of query durations. **Lower scores are better.**


<details class="note-box">
  <summary>HOW DID WE MEASURE ① ② ③? (click to expand)</summary>
  <div class="note-body">
<iframe src="/uploads/02a_how_did_we_measure_0d6eefd769.html" frameborder="0" style="width: 100%; height: 500px; max-height: 800px;"></iframe>
<iframe src="/uploads/02b_shared_costbench_harness_4f45aad9e9.html" frameborder="0" style="width: 100%; height: 500px; max-height: 800px;"></iframe>
    <p class="note-heading"><strong>SHARED HARNESS</strong></p>
    <p>Both systems used the same source dataset, schema, workload definitions, pacing model, query schedule, and result format. Destination-specific adapters handled delivery and timing. <a href="https://clickhouse.com/blog/costbench-real-time-performance-per-dollar">Part 1</a> explains the shared methodology; the <a href="https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/databricks/DATABRICKS_BENCHMARK_CONTRACT.md">Databricks benchmark contract</a> records this provider’s implementation.</p>
    <p class="note-heading"><strong>DATASET AND PREPARATION</strong></p>
    <p>The complete <a href="https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes#dataset">NBBO dataset</a> contains 113,219,565,734 narrow, 12-column rows. Raw tables used (sym, t), stock symbol and event timestamp; daily summaries used (sym, day), stock symbol and UTC day. The summaries maintained the counts, sums, and price minima and maxima used by the aggregate queries.</p>
    <p class="note-heading"><strong>CONTINUOUS WORKLOAD</strong></p>
    <p>Fresh rows were paced toward 1 million per second while aggregate and drill-down queries ran on their ten-minute and hourly schedules. This models data being generated continuously and prepared as it arrives, rather than measuring how quickly an existing dataset can be bulk-loaded or backfilled. The Databricks MV path retained its native snapshot semantics; matching ingestion progress does not make both systems’ summaries equally fresh.</p>
    <p class="note-heading"><strong>RECOMMENDED STACK AND SIZING</strong></p>
    <p>ClickHouse Cloud used a 16-CPU, 64-GiB read node. Databricks used an X-Small Serverless SQL warehouse fixed at one cluster, approximately 16 worker vCPUs; this sizing does not imply identical hardware or memory. <a href="https://docs.databricks.com/aws/en/tables/clustering">Liquid clustering</a>, <a href="https://docs.databricks.com/aws/en/optimizations/predictive-optimization">Predictive Optimization</a>, and triggered incremental MV refresh were enabled. Lakehouse//RT was unavailable in the test workspace, so the accepted comparison uses the <a href="https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/databricks/REAL_SERVERLESS_BASELINE.md">Serverless SQL baseline</a>.</p>
    <p class="note-heading"><strong>① PREPARATION COST</strong></p>
    <p>The full ingest includes ClickHouse’s complete two-node HA ingest service and Databricks’ Zerobus ingestion, asynchronous clustering, and MV refresh. Databricks ingestion and refresh use allocated DBU usage; clustering uses the accepted Predictive Optimization DBU allocation. All three appear in the <a href="https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/databricks/costs/out/serverless_20260918/fresh_data_path.json">preparation-cost model</a>.</p>
    <p class="note-heading"><strong>② QUERY COST AND ③ RUNTIME</strong></p>
    <p>Each accepted query’s recorded duration is priced at its read-side compute rate and added to accumulated runtime. Databricks uses Query History total duration, excluding result fetch; ClickHouse uses its recorded runner duration. These normalized costs represent accepted query work, not complete warehouse invoices. The query-comparison and pricing notes below detail the timing and boundaries.</p>
    <p class="note-heading"><strong>TARGET VERSUS OBSERVED RATE</strong></p>
    <p>Databricks completed the durable-ingest window in about 31.5 hours, averaging approximately 1 million rows/s. ClickHouse completed its ingest in about 36.75 hours, averaging approximately 0.86 million rows/s. The target was shared; observed progress differed. Databricks’ <a href="https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/databricks/results/serverless_baseline_full_20260918T170453Z/run_context.json">final reconciliation</a> confirmed all 113,219,565,734 rows with no duplicate surplus. Durability acknowledgment and table query visibility are separate milestones.</p>
    <p class="note-heading"><strong>REPORTING WINDOW</strong></p>
    <p>Per-query latency charts stop at 100 billion rows. Preparation costs cover the full active ingest; accumulated query cost and runtime use the accepted active-ingestion observations, ending at each workload’s shared comparison horizon. Post-ingestion queries and maintenance are outside the headline score. Displayed totals are rounded.</p>
  </div>
</details>


ClickHouse Cloud led in all three measured components:



**① Preparation cost:** $28.69 versus $695.60.<br/>
**② Normalized query cost:** about $0.05 versus $2.65.<br/>
**③ Accumulated query runtime:** 56.39 seconds versus 29.10 minutes.

The charts below track those costs and runtimes as ingestion progresses.

<iframe src="/uploads/03_accumulated_cost_and_runtime_d6c3816599.html" frameborder="0" style="width: 100%; height: 500px; max-height: 800px;"></iframe>

The score breakdown below combines the two advantages: **24.3× lower combined preparation and normalized query cost**, multiplied by **31× lower accumulated query runtime**, gives ClickHouse Cloud its overall performance-per-dollar lead. 

<iframe src="/uploads/04_final_ranking_score_589730ff8a.html" frameborder="0" style="width: 100%; height: 500px; max-height: 800px;"></iframe>

<details class="note-box">
  <summary>PRICING, FORMULAS, AND THE 752× SCORE (click to expand)</summary>
  <div class="note-body">
    <p class="note-heading"><strong>PRICING BASIS</strong></p>
    <p>ClickHouse Cloud uses $0.3903 per compute unit (CU) per hour. Databricks uses checked-in public list rates for AWS eu-west-1, Premium: $0.39 per DBU for allocated ingestion and maintenance, and $0.91 per DBU for Serverless SQL. The <a href="https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/databricks/results/serverless_baseline_full_20260918T170453Z/charts/full_path_cost_performance_clickhouse_vs_databricks_summary.json">accepted summary</a> preserves full precision; these are modeled list-price costs, not a historical invoice reconstruction.</p>
    <p class="note-heading"><strong>① COMPLETE PREPARATION COST</strong></p>
    <p>This covers the active ingest of all 113,219,565,734 rows, including the required preparation components.</p>
    <p class="note-heading"><strong>CLICKHOUSE CLOUD</strong></p>
    <p>2 CUs × 36.75 hours × $0.3903/CU-hour = <strong>$28.68705</strong>, including both HA ingest nodes.</p>
    <p class="note-heading"><strong>DATABRICKS INGESTION</strong></p>
    <p><a href="https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/databricks/results/serverless_baseline_full_20260918T170453Z/ingest/zerobus_ingest_allocation.csv">Allocated Zerobus usage</a>, 1,098.9261167 DBUs × $0.39 = <strong>$428.58119</strong>. This accepted DBU allocation is used in the headline rather than converting the source’s byte volume into a pricing proxy.</p>
    <p class="note-heading"><strong>DATABRICKS CLUSTERING</strong></p>
    <p>The <a href="https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/databricks/results/serverless_baseline_full_20260918T170453Z/ingest/predictive_optimization_allocation.csv">Predictive Optimization allocation</a> contains 151.8613011 DBUs × $0.39 = <strong>$59.22591</strong>. This component uses Predictive Optimization’s operation-level DBU allocation. It is a modeled maintenance charge rather than an invoiced amount.</p>
    <p class="note-heading"><strong>DATABRICKS MV REFRESH</strong></p>
    <p>532.8145064 allocated DBUs × $0.39 = <strong>$207.79766</strong>. Together, ingestion, clustering, and refresh total <strong>$695.60475</strong> in the <a href="https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/databricks/costs/out/serverless_20260918/fresh_data_path.json">accepted preparation model</a>.</p>
    <p class="note-heading"><strong>② NORMALIZED QUERY COST</strong></p>
    <p>Each accepted query’s recorded duration is multiplied by the per-second read-side compute rate. This models accepted work; it excludes idle capacity and minimum warehouse billing.</p>
    <p class="note-heading"><strong>CLICKHOUSE CLOUD</strong></p>
    <p>8 CUs × $0.3903/CU-hour × (10.312s aggregate + 46.074s drill-down) ÷ 3,600 = <strong>$0.04890</strong>.</p>
    <p class="note-heading"><strong>DATABRICKS SERVERLESS SQL</strong></p>
    <p>X-Small is priced at 6 DBUs/hour × $0.91/DBU = <strong>$5.46/hour</strong>. Aggregate work: 613.164s × $5.46/hour ÷ 3,600 = <strong>$0.92997</strong>.</p>
    <p class="note-heading"><strong>DATABRICKS DRILL-DOWN WORK</strong></p>
    <p>1,133.002s × $5.46/hour ÷ 3,600 = <strong>$1.71839</strong>. Total normalized query cost: <strong>$2.64835</strong>.</p>
    <p class="note-heading"><strong>ALLOCATION BOUNDARY</strong></p>
    <p>Databricks ingestion and maintenance are allocated to the <a href="https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/databricks/costs/scopes/serverless_20260918.json">producer-active window</a>, 2026-09-18 17:04:53 UTC through 2026-09-20 00:33:42.627 UTC, with an exclusive end. Post-ingestion maintenance, validation/control SQL, database storage, producer infrastructure, network charges, and idle/minimum warehouse charges are excluded. Maintenance was observed after ingestion but that later work is not charged to this score.</p>
    <p class="note-heading"><strong>③ ACCUMULATED QUERY RUNTIME</strong></p>
    <p>ClickHouse: 10.312s aggregate + 46.074s drill-down = <strong>56.386s</strong>. Databricks: 613.164s aggregate + 1,133.002s drill-down = <strong>1,746.166s</strong>.</p>
    <p class="note-heading"><strong>COMPARISON BOUNDARY</strong></p>
    <p>① covers the complete active ingest. ② and ③ use 189 four-query aggregate batches and 32 two-query drill-down batches. Their row-count comparison horizons differ from the 100-billion-row latency plots. Durability alignment does not establish identical query-visible rows or MV freshness. This is the complete modeled preparation path plus normalized query work, not the full provider bill.</p>
    <p class="note-heading"><strong>FINAL SCORE</strong></p>
    <p>ClickHouse: ($28.68705 + $0.04890) × 56.386 = <strong>1,620.30528</strong>. Databricks: ($695.60475 + $2.64835) × 1,746.166 = <strong>1,219,265.82646</strong>. The ratio is <strong>752.491×</strong>, rounded to <strong>752×</strong>, using the <a href="https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/databricks/results/serverless_baseline_full_20260918T170453Z/charts/full_path_cost_performance_clickhouse_vs_databricks_summary.json">full-precision inputs</a>.</p>
  </div>
</details>



---

## 752× better real-time performance per dollar

Interested in seeing how ClickHouse works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-2536-752-better-real-time-performance-per-dollar-sign-up&utm_blogctaid=2536)

---

All benchmark code and results are available in the [CostBench repository](https://github.com/ClickHouse/CostBench/tree/main/full-path-realtime/quotes). The stock-quotes dataset requires a [separate data license](https://github.com/ClickHouse/CostBench/tree/main/full-path-realtime/quotes#data-source-and-licensing), so the data itself cannot be redistributed.

To explain that result, we follow the same path as the data: preparation first, then query serving.


## How ClickHouse Cloud prepares incoming data

The benchmark used a dedicated ClickHouse Cloud ingest service with **two 2-CPU nodes for high availability**, the smallest HA configuration that sustained the target during calibration. The shared client sent rows through [asynchronous inserts](https://clickhouse.com/blog/asynchronous-data-inserts-in-clickhouse) built into each node.

The diagram below shows those same nodes handling ① columnar storage, ② ordering raw data, and ③ ordered pre-aggregation, plus background merges, on **four CPU cores in total**.

<iframe src="/uploads/05_clickhouse_fresh_data_path_fb0a4cca05.html" frameborder="0" style="width: 100%; height: 500px; max-height: 800px;"></iframe>


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

Now follow the same three preparation tasks through Databricks, where ingestion, clustering, and MV refresh use separate services.


## How Databricks prepares incoming data

The benchmark used [Zerobus Ingest](https://docs.databricks.com/aws/en/ingestion/zerobus-ingest), Databricks’ managed path for pushing rows directly into Delta tables, through Arrow Flight streams.

As shown below, Zerobus handles ① columnar storage; asynchronous serverless clustering handles ② ordering raw data; a separate serverless MV pipeline handles ③ pre-aggregation.

<iframe src="/uploads/06_databricks_fresh_data_path_eb76667a8f.html" frameborder="0" style="width: 100%; height: 500px; max-height: 800px;"></iframe>

**① Store in columns:** Zerobus buffers incoming rows and publishes them into a managed Delta table backed by columnar Parquet files. A durability acknowledgment confirms that Zerobus has durably accepted the data; it does not guarantee immediate visibility in the table.

**② Order data:** The raw table used [liquid clustering](https://docs.databricks.com/aws/en/tables/clustering) on (sym, t), matching ClickHouse’s sorting key. [Predictive Optimization](https://docs.databricks.com/aws/en/optimizations/predictive-optimization) ran clustering asynchronously on serverless compute, so newly published files could be queried before that layout work finished. 
 
**③ Order and pre-aggregate data:** A separate [serverless pipeline](https://docs.databricks.com/aws/en/ldp/dbsql/materialized) incrementally refreshed daily summaries, clustered by (sym, day). The [tested definition](https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/databricks/create_full_serverless_baseline_r3_20260918.sql) used REFRESH POLICY INCREMENTAL STRICT and TRIGGER ON UPDATE AT MOST EVERY INTERVAL 1 MINUTE. The trigger uses Databricks’[ minimum supported interval of 1 minute](https://docs.databricks.com/gcp/en/ldp/dbsql/schedule-refreshes#trigger-on-update); it limits refresh starts, not completion time. 



<details class="note-box">
  <summary>WHY THESE INGESTION PATHS, AND HOW WERE THEY BUFFERED? (click to expand)</summary>
  <div class="note-body">
    <p class="note-heading"><strong>THE SAME INGESTION PROBLEM</strong></p>
    <p>Applications produce frequent writes that must become efficient storage writes. Both destinations used direct application-to-table ingestion with managed buffering. No Kafka broker, file landing stage, or Auto Loader job was added to the measured path.</p>
    <p class="note-heading"><strong>DATABRICKS’ MANAGED PATH</strong></p>
    <p>The <a href="https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/databricks/REAL_SERVERLESS_BASELINE.md">accepted runner</a> used the Zerobus Arrow Flight DoPut interface, with 16 concurrent streams and 50,000-row client batches. Streams rotated every ten minutes; SDK recovery and bounded retries were enabled. Zerobus ingestion compute was allocated and priced separately from clustering, MV refresh, and SQL serving.</p>
    <p class="note-heading"><strong>CLICKHOUSE’S NATIVE PATH</strong></p>
    <p>Ordinary INSERT requests with async_insert enabled were buffered on each receiving node. An <a href="https://clickhouse.com/docs/optimize/asynchronous-inserts">adaptive flush timeout</a> responded to incoming traffic. Ordering and pre-aggregation ran on the ingest nodes; the dedicated <a href="https://clickhouse.com/docs/cloud/reference/warehouses">ingest service</a> shared storage with the independently sized read service.</p>
    <p class="note-heading"><strong>SHARED PACING</strong></p>
    <p>Both adapters read the same Parquet dataset and decoded the same schema under the same target-rate model. Parallelism and client batch sizes were adapted to each destination’s API; they were not forced to be identical.</p>
    <p class="note-heading"><strong>CLICKHOUSE BATCHES</strong></p>
    <p>The client sent 3,000-row batches through asynchronous inserts. Default buffering flushed at the first of three thresholds: 100 MiB buffered, an adaptive timeout between 50 milliseconds and 1 second, or 450 queued insert queries.</p>
    <p class="note-heading"><strong>DATABRICKS BATCHES</strong></p>
    <p>Each Arrow Flight stream sent 50,000-row batches with IPC compression disabled. The target rate was based on logical source rows, with acknowledged durable progress recorded separately from table visibility. Those batches were not staged as files for a later bulk load.</p>
    <p class="note-heading"><strong>BATCH-SIZE BOUNDARY</strong></p>
    <p>These are client delivery batch sizes. Both systems buffer delivery into storage writes, so 3,000 and 50,000 rows do not specify final part or Parquet-file sizes.</p>
    <p class="note-heading"><strong>RETRIES AND RECONCILIATION</strong></p>
    <p>Zerobus used durable stream offsets and SDK recovery. The <a href="https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/databricks/results/serverless_baseline_full_20260918T170453Z/validation/validation_report_settled_20260921T092624Z.json">settled validation</a> confirmed exact row reconciliation and no duplicate surplus. ClickHouse supports insert deduplication for retries, including dependent materialized views. The final row check validates delivery, not equal summary freshness during ingestion.</p>
    <p class="note-heading"><strong>INCREMENTAL MAINTENANCE</strong></p>
    <p>The raw Delta table enabled row tracking, change data feed, and deletion vectors. The MV passed incremental eligibility checks and used INCREMENTAL STRICT. The <a href="https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/databricks/results/serverless_baseline_full_20260918T170453Z/evidence/mv_refresh_summary.json">refresh evidence</a> recorded 1,028 incremental group-aggregate refreshes and zero full refreshes across the collected run, including its post-ingestion observation period.</p>
    <p class="note-heading"><strong>WHAT WAS TESTED</strong></p>
    <p>The serving layer was Serverless SQL X-Small. Lakehouse//RT was not available in the workspace and was not tested. This article describes the accepted configuration and its results, rather than projecting the performance of an unavailable serving product.</p>
  </div>
</details>

> The result: Databricks can expose raw data before clustering finishes, while its pre-aggregations advance through a separate refresh cycle. 

## What this means for freshness and preparation cost


### Pre-aggregation lag

ClickHouse updates summaries during inserts; Databricks refreshes them asynchronously. The chart below follows Databricks’ refresh cadence: **observed completed refreshes were about 1.8 minutes apart on average, reaching about 2.0 minutes in the plotted trend**.

<iframe src="/uploads/07_pre_aggregation_lag_54dd069d49.html" frameborder="0" style="width: 100%; height: 500px; max-height: 800px;"></iframe>


These are intervals between observed refresh completions, rather than an exact measurement of how far every summary trails the raw table. Between refreshes, queries against the Databricks MV can return older summaries.


<details class="note-box">
  <summary>HOW WAS PRE-AGGREGATION FRESHNESS MEASURED? (click to expand)</summary>
  <div class="note-body">
    <p class="note-heading"><strong>DATABRICKS SERIES</strong></p>
    <p>The <a href="https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/databricks/results/serverless_baseline_full_20260918T170453Z/freshness/mv_freshness_20260918T170453Z.jsonl">freshness history</a> was polled once a minute. The plotted metric is the time between distinct observed completed refresh IDs: floor(current completed_at − previous observed completed_at), in seconds. The selected active-ingestion evidence contains 1,021 such intervals; compact polling can miss intermediate completions.</p>
    <p class="note-heading"><strong>SMOOTHING AND READOUTS</strong></p>
    <p>A centered 61-observation rolling mean averages about 1.8 minutes across the interval observations. An additional 11-observation display mean and shape-preserving interpolation produce a plotted peak of about 2.0 minutes. Readouts follow that displayed curve. This is a refresh-interval proxy, not a directly polled raw-to-MV watermark lag or a per-query stale-row count.</p>
    <p class="note-heading"><strong>CLICKHOUSE BASELINE</strong></p>
    <p>The zero line is a benchmark-semantic baseline, not a separately polled provider metric. The raw table and incremental MV consume the same flushed insert block, with no independent summary-refresh interval between them. It does not claim zero source-to-query ingestion delay.</p>
  </div>
</details>

> ClickHouse kept summaries current during ingestion; Databricks’ observed refreshes were roughly 1.8 minutes apart, leaving queries able to read older summaries.

That freshness difference follows the data into queries. First, the next chart accounts for what each preparation path cost.


### Cost of keeping incoming data query-ready

ClickHouse handles ① columnar storage, ② ordering raw data, and ③ ordered pre-aggregation within its engine. Databricks spreads that work across ingestion, serverless clustering, and MV refresh. The chart below compares their accumulated preparation costs.

<iframe src="/uploads/08_fresh_data_path_cost_24599d3b47.html" frameborder="0" style="width: 100%; height: 500px; max-height: 800px;"></iframe>


ClickHouse’s complete ingest service cost **$28.69**. Databricks’ modeled preparation cost totaled **$695.60**: **$428.58** for Zerobus ingestion (①), **$59.23** for asynchronous clustering (②), and **$207.80** for MV refresh (③). Ingestion and refresh use allocated DBU usage; the folded pricing note gives the boundaries. 
 
> **ClickHouse handled columnar storage, ordering, and pre-aggregation at 24.2× lower preparation cost in this run.** 
 
Now follow the raw data and summaries into query serving.


## How ClickHouse Cloud serves queries

Ordered raw data lets drill-downs skip unrelated rows; pre-aggregations let interactive aggregations combine prepared results instead of recalculating them from individual quotes. The diagram below follows both paths through ClickHouse Cloud’s read service: **one node with 16 CPUs and 64 GiB of memory**, matching Databricks’ X-Small worker CPU count.


<iframe src="/uploads/09_clickhouse_query_serving_462877d424.html" frameborder="0" style="width: 100%; height: 500px; max-height: 800px;"></iframe>

**Drill-downs:** Queries prune ordered raw data in the [event-level MergeTree table](https://clickhouse.com/docs/engines/table-engines/mergetree-family/mergetree). Filtering by symbol, the leading column of its (sym, t) sorting key, lets the read service skip unrelated quotes.

**Interactive aggregations:** Queries read [current pre-aggregations](https://clickhouse.com/docs/materialized-view/incremental-materialized-view) from the [AggregatingMergeTree table](https://clickhouse.com/docs/engines/table-engines/mergetree-family/aggregatingmergetree), combining prepared counts, sums, minima, and maxima from a much smaller set of daily summary rows. There is no independent refresh to wait for. 
 
> The result: drill-downs prune ordered raw data; interactive aggregations read summaries kept current during ingestion.

Databricks uses the same two query paths, but asynchronous preparation changes what queries can read.


## How Databricks serves queries

The diagram below shows an **X-Small [Serverless SQL warehouse](https://docs.databricks.com/aws/en/compute/sql-warehouse/warehouse-types)** serving both workloads, fixed at one cluster with [16 worker vCPUs](https://docs.databricks.com/aws/en/compute/sql-warehouse/warehouse-behavior#sizing-and-cluster-provisioning).

<details class="note-box">
  <summary>WHY WASN’T LAKEHOUSE//RT INCLUDED? (click to expand)</summary>
  <div class="note-body">
    <p>Lakehouse//RT is currently in Beta. We have requested access but have not yet received it.</p>
    <p>Once Lakehouse//RT is generally available and we have access, we plan to repeat the full CostBench workload with Lakehouse//RT serving the queries and publish the results.</p>
  </div>
</details>

<iframe src="/uploads/10_databricks_query_serving_cf84562b72.html" frameborder="0" style="width: 100%; height: 500px; max-height: 800px;"></iframe>

**Drill-downs:** Queries read the [Delta table](https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/databricks/create_full_serverless_baseline_r3_20260918.sql) directly and filter by symbol. Liquid clustering on (sym, t) helps skip unrelated files after clustering runs, but newly published files can remain unclustered until asynchronous maintenance catches up.

**Interactive aggregations:** Queries read daily summaries from the [incremental MV](https://docs.databricks.com/aws/en/ldp/dbsql/materialized). They see the last completed refresh snapshot; newer raw rows are not automatically combined with it at query time. The answer can therefore omit data that has already reached the raw table.

**The distinction shown by the two paths:** Drill-downs can scan data whose clustering is unfinished; interactive aggregations can read summaries whose refresh is unfinished. Both arise from preparation that advances separately from ingestion.

<details class="note-box">
  <summary>WHAT DO DATABRICKS’ REFRESH AND VISIBILITY GUARANTEES MEAN? (click to expand)</summary>
  <div class="note-body">
    <p class="note-heading"><strong>SNAPSHOT CONTRACT</strong></p>
    <p>A <a href="https://docs.databricks.com/aws/en/ldp/dbsql/materialized#refresh-a-materialized-view">refresh</a> updates the MV from its source table. The measured aggregate queries read that materialized result directly. They did not force a synchronous refresh before each query or merge a raw-table delta into the answer. The measured latency therefore includes Databricks’ native allowance for stale summaries.</p>
    <p class="note-heading"><strong>TRIGGER CONTRACT</strong></p>
    <p><a href="https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-create-materialized-view">TRIGGER ON UPDATE</a> schedules refreshes when upstream data changes. AT MOST EVERY INTERVAL 1 MINUTE imposes a minimum interval between triggers, not a one-minute maximum on data age or refresh completion.</p>
    <p class="note-heading"><strong>INCREMENTAL CONTRACT</strong></p>
    <p>INCREMENTAL STRICT controls the maintenance method: eligible changes are processed incrementally rather than silently falling back to a full rebuild. It does not tie MV visibility to each ingested block or make the MV continuously current.</p>
    <p class="note-heading"><strong>VISIBILITY CONTRACT</strong></p>
    <p>The runner’s raw_rows records acknowledged durable ingestion progress. Zerobus can durably accept rows before they are published into the Delta table. A query pair aligned by durable ingestion progress is therefore not proof that both queries saw exactly the same raw-row count or an equally fresh summary snapshot.</p>
    <p class="note-heading"><strong>COMPARISON BOUNDARY</strong></p>
    <p>The headline preserves the tested MV-serving path, including its freshness behavior. A design that forced a refresh or queried and re-aggregated the raw table would have a different latency and cost profile; that work is not included in this result.</p>
  </div>
</details>

> The result: Databricks drill-downs may scan newly arrived, unclustered data; interactive aggregations may read summaries from an earlier refresh.


## What this means for query performance and cost


### Drill-downs over ordered raw data

Both systems used (sym, t) keys, but ClickHouse ordered rows during inserts while Databricks clustered files asynchronously. [D1 and D2](https://clickhouse.com/blog/costbench-real-time-performance-per-dollar#the-query-workload) query one stock’s growing history directly: hourly price summaries and a risk-and-liquidity profile. The chart below follows that raw-data path, bypassing the materialized views.

<iframe src="/uploads/11_drill_down_query_latency_4a00019f1b.html" frameborder="0" style="width: 100%; height: 500px; max-height: 800px;"></iframe>

ClickHouse Cloud is yellow; Databricks is red.

<details class="note-box">
  <summary>HOW WERE QUERY LATENCIES AND ACCUMULATED RESULTS COMPARED? (click to expand)</summary>
  <div class="note-body">
    <p class="note-heading"><strong>QUERY DEFINITIONS</strong></p>
    <p><a href="https://clickhouse.com/blog/costbench-real-time-performance-per-dollar#the-query-workload">Part 1</a> describes A1–A4 and D1–D2. Both systems used the same analytical workload and schedule, with SQL adapted to each engine. Counts, sums, and extrema were compared exactly; the approximate-percentile portion of D2 used the <a href="https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/databricks/DATABRICKS_BENCHMARK_CONTRACT.md">contract’s explicit tolerance</a>. MV freshness was not assumed to be identical.</p>
    <p class="note-heading"><strong>CACHE POLICY</strong></p>
    <p>Query-result caching was disabled. Databricks’ compact query evidence reported no result-cache hits for accepted queries. Underlying data caches were allowed to warm normally; the benchmark did not flush them between queries.</p>
    <p class="note-heading"><strong>TIMING</strong></p>
    <p>Databricks latency uses <a href="https://docs.databricks.com/aws/en/admin/system-tables/query-history">Query History</a> total_duration_ms ÷ 1,000, excluding result-fetch time. ClickHouse uses its recorded query duration. These timing conventions are retained in normalized query cost. Median, P99, and maximum statistics pool unsmoothed per-query observations through 100 billion rows; P99 uses linear interpolation.</p>
    <p class="note-heading"><strong>LATENCY CHARTS</strong></p>
    <p>Each system is plotted at its own observed ingestion progress. Aggregate trends use a centered seven-observation rolling median; drill-downs use five observations, with shrinking edge windows. No outliers are removed. The curves are display smoothing; the statistics and accumulated totals use the original recorded durations.</p>
    <p class="note-heading"><strong>INTERACTIVE READOUTS</strong></p>
    <p>Values below the plots follow the displayed trends at the selected row count. Logarithmic scales keep milliseconds and seconds readable together; Linear shows absolute differences. Each chart has its own playback and row-position controls.</p>
    <p class="note-heading"><strong>ACCEPTED ACCUMULATED WORKLOAD</strong></p>
    <p>The <a href="https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/databricks/results/serverless_baseline_full_20260918T170453Z/integration/manifest.json">accepted selection</a> contains 189 four-query aggregate batches and 32 two-query drill-down batches per system: <strong>756 + 64 = 820 executions</strong>. ClickHouse observations were aligned with Databricks durability progress, through 112.849 billion rows for aggregation and 111.649 billion for drill-downs. The first full-dataset observation and later post-ingestion samples are excluded.</p>
    <p class="note-heading"><strong>ACCUMULATED CHARTS</strong></p>
    <p>Query durations are added at corresponding ingestion counts as step sums, without smoothing or interpolating future executions into earlier positions. Preparation-cost lines allocate the complete-ingest total proportionally by row progress; they are not metered cost-at-time traces. The score sums query durations, not elapsed ingestion time.</p>
  </div>
</details>

**ClickHouse Cloud:**



* **722.5 ms median** - 22.1× faster than Databricks
* **1.15 s P99** - 42.7× faster
* **1.18 s maximum** - 48.2× faster

Accumulated runtime was **46.07 seconds** across the 32 two-query batches. The ordered raw-data path kept both drill-downs near or below one second as the table grew.

**Databricks:**



* **15.99 s median**
* **49.11 s P99**
* **56.90 s maximum**

Accumulated runtime was **18.88 minutes** across the same 32 batches. The curves show substantially more time spent reading the growing raw table; asynchronous clustering can leave new files less organized for symbol filters.

> **Across the drill-down workload, ClickHouse Cloud was 24.6× faster overall.**


### Interactive aggregations over ordered pre-aggregated data

Daily pre-aggregations let [A1–A4](https://clickhouse.com/blog/costbench-real-time-performance-per-dollar#the-query-workload) combine prepared counts, sums, and price minima and maxima. A1–A2 filter summaries by symbol; A3–A4 read across all symbols. ClickHouse reads summaries maintained during inserts; Databricks reads the last refreshed snapshot. The chart below compares latency as ingestion continues.

<iframe src="/uploads/12_aggregate_query_latency_0c61a5cd9a.html" frameborder="0" style="width: 100%; height: 500px; max-height: 800px;"></iframe>

**ClickHouse Cloud:**



* **13 ms median** - 60.2× faster than Databricks
* **42 ms P99** - 48.4× faster
* **111 ms maximum** - 47.7× faster

Accumulated runtime was **10.31 seconds** across the 189 four-query batches.

**Databricks:**



* **782 ms median**
* **2.02 s P99**
* **5.30 s maximum**

Accumulated runtime was **10.22 minutes** across the same 189 batches. These queries read the MV snapshot without waiting for its next refresh. ClickHouse was faster even while maintaining summaries with the raw-data insert path; Databricks’ measured speed did not come with the same freshness.

> **Across the interactive-aggregation workload, ClickHouse Cloud was 59.5× faster overall, with summaries maintained during inserts.**


### Accumulated query cost and runtime

The two query paths add up differently: drill-downs account for most of Databricks’ accumulated runtime. The charts below combine both workloads and price their recorded durations using the benchmark’s read-side cost model.

<iframe src="/uploads/13_query_runtime_and_cost_274ef23224.html" frameborder="0" style="width: 100%; height: 500px; max-height: 800px;"></iframe>

ClickHouse Cloud accumulated **56.39 seconds** of query runtime and Databricks **29.10 minutes**. Their normalized query-serving costs were about **$0.05** and **$2.65**, respectively. These are costs for the query work, not complete warehouse invoices.

> **Across the query workload, ClickHouse Cloud was 31× faster overall, with 54.2× lower normalized query cost.**


## From the field: Gala

Gala’s migration from Databricks to ClickHouse Cloud shows the production benefits of faster analytics at lower cost: more data available for analysis and self-service analytics accessible to more teams. On AWS, the team added continuous ingestion from more sources and rolled out Metabase so business teams could explore data themselves. By the end of the migration, it had decommissioned Databricks.

With the new layout configured correctly from the start, queries on previously unoptimized tables went from minutes to **under 1 second**. The data available for analysis grew from **3 TB to 9 TB** during the migration, while initial costs were **30% lower**. “We just don’t think about our data infrastructure as much anymore,” says Mike Rexford, Gala’s lead data analyst. [Read Gala’s migration story](https://clickhouse.com/blog/gala).


## Databricks can’t match ClickHouse Cloud for real-time analytics

While fresh data kept arriving, ClickHouse Cloud led across the complete tested path:



**① Preparation cost: 24.2× lower** for ingestion, ordering, and pre-aggregation.<br/>
**② Normalized query cost: 54.2× lower** for the queries.<br/>
**③ Accumulated query runtime: 31× lower** across both query workloads.

The final chart brings these results together, plotting combined preparation and normalized query cost against accumulated query runtime as fresh data arrives.

<iframe src="/uploads/14_end_to_end_cost_vs_accumulated_query_clickhouse_databricks_ad5693797e.html" frameborder="0" style="width: 100%; height: 500px; max-height: 800px;"></iframe>



Up is lower total modeled cost; right is lower accumulated query runtime. 

> ClickHouse Cloud delivered 752× better end-to-end performance per dollar while continuously ingesting data and serving queries, with summaries kept current during inserts.

The difference begins as data arrives. ClickHouse prepares ordered raw data and current summaries on the insert path. Databricks adds separate clustering and refresh services, and its queries can encounter unfinished layout work or older summaries. In this workload, those services cost more to run, and both query paths still took longer.

That is why Databricks can’t match ClickHouse Cloud for real-time analytics.





