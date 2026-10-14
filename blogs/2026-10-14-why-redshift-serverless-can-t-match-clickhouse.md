---
title: "Why Redshift Serverless can’t match ClickHouse Cloud for real-time analytics"
date: "2026-10-14T09:07:30.377Z"
author: "Tom Schreiber and Lionel Palacin"
category: "Engineering"
excerpt: "ClickHouse Cloud delivered 1,996× better performance per dollar than Redshift Serverless in CostBench. We trace the gap from fresh data arriving to fast answers coming back."
---

# Why Redshift Serverless can’t match ClickHouse Cloud for real-time analytics

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

Real-time systems differ dramatically in the cost and efficiency of making incoming data query-ready. This series traces the path from arrival to answers, showing where preparation cost, query cost, and query runtime accumulate.

Here, ClickHouse Cloud and Redshift Serverless ingest 113.2 billion quotes while queries run. ClickHouse Cloud delivered **1,996× better end-to-end performance per dollar** in the tested comparison using Redshift’s live streaming view for drill-downs. We follow the complete streaming and preparation path to explain that result.



## From fresh data to fast answers

[Real-time analytics](https://clickhouse.com/blog/selecting-a-real-time-analytical-database) has to remain fast while fresh data keeps arriving. [**CostBench**](https://clickhouse.com/blog/costbench-data-warehouse-cost-performance) **runs queries throughout continuous ingestion**, measuring the work of preparing new data alongside the work of serving answers. Efficient preparation lowers the cost of keeping data [query-ready](https://clickhouse.com/blog/costbench-real-time-performance-per-dollar#what-makes-data-query-ready) and reduces the scanning and aggregation left for queries.

Columnar storage lets queries skip unused fields; ordering lets drill-downs skip unrelated quotes; current pre-aggregations let interactive aggregations combine prepared summaries. The diagram below shows how the [fresh-data path](https://clickhouse.com/blog/costbench-real-time-performance-per-dollar#real-time-systems-must-make-fresh-data-query-ready-as-it-arrives) shapes query work as preparation keeps pace or falls behind.

<iframe src="/uploads/01_fresh_data_path_query_work_balance_1bceb14b32.html" frameborder="0" style="width: 100%; height: 500px; max-height: 800px;"></iframe>

CostBench measures ① preparation cost, ② query cost, and ③ runtime, then combines them into one [end-to-end performance-per-dollar score](https://clickhouse.com/blog/costbench-real-time-performance-per-dollar#turning-runtime-and-cost-into-performance-per-dollar).

This article follows those three effects through the ClickHouse-Redshift Serverless comparison, from preparing incoming data to serving queries.

## The workload and the result

> **ClickHouse Cloud delivered 1,996× better end-to-end performance per dollar than Redshift Serverless in this continuous-ingestion comparison.**

Both systems used their recommended real-time ingestion paths and native preparation features: ClickHouse asynchronous inserts; Redshift streaming ingestion from Amazon MSK, and incremental materialized views. CostBench streamed **113.2 billion stock-market quotes** at a target of **1 million rows per second**, with equivalent sorting-keys and daily pre-aggregations by stock symbol. **Throughout ingestion, four interactive aggregate queries ran every ten minutes; two drill-down queries ran every hour.** The Redshift comparison uses its live streaming view for drill-downs and the last completed daily-MV refresh for aggregation. Query-result caching was disabled.

CostBench calculates its **end-to-end performance-per-dollar score** using the formula shown below: **Score = (① preparation cost + ② normalized query cost) × ③ accumulated query runtime.**

<iframe src="/uploads/02_costbench_end_to_end_score_ef5edce174.html" frameborder="0" style="width: 100%; height: 500px; max-height: 800px;"></iframe>

Preparation cost covers the complete fresh-data path. Normalized query cost allocates serving resources to the accepted queries; accumulated query runtime is the sum of their durations. **Lower scores are better.** The folded notes explain the writer-capacity model, read-path choice, and summary freshness.

<details class="note-box">
  <summary>How did we measure ① ② ③? (click to expand)</summary>
  <div class="note-body">

<iframe src="/uploads/02a_how_did_we_measure_caa5d13a7a.html" frameborder="0" style="width: 100%; height: 500px; max-height: 800px;"></iframe>
<iframe src="/uploads/02b_shared_costbench_harness_12ac582777.html" frameborder="0" style="width: 100%; height: 500px; max-height: 800px;"></iframe>

<p class="note-heading"><strong>Shared harness:</strong></p>

<p>Both systems used the same source dataset, analytical workload, target-rate model, query schedule, and result format. Destination-specific adapters handled delivery and timing. <a href="https://clickhouse.com/blog/costbench-real-time-performance-per-dollar">Part 1</a> explains the shared methodology; the <a href="https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/redshift-serverless/README.md">Redshift architecture</a> records this provider’s implementation.</p>
<p class="note-heading"><strong>Dataset and preparation:</strong></p>

<p>The complete <a href="https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes#dataset">NBBO dataset</a> contains 113,219,565,734 narrow, 12-column rows. The raw-data ordering columns were (sym, t), stock symbol and event timestamp; daily summaries used (sym, day), stock symbol and UTC day, maintaining counts, sums, and price minima and maxima.</p>
<p class="note-heading"><strong>Continuous workload:</strong></p>

<p>Fresh events were paced toward 1 million per second while aggregate and drill-down queries ran on their ten-minute and hourly schedules. This models data generated continuously and prepared as it arrives. Redshift’s aggregate queries read the last completed daily-MV refresh; aligning ingestion progress does not make that snapshot equally fresh to ClickHouse’s insert-time summaries.</p>
<p class="note-heading"><strong>Recommended stack and sizing:</strong></p>

<p>ClickHouse Cloud used a 16-CPU, 64-GiB read node. Redshift used separate writer and reader workgroups connected by a live datashare. The reader was fixed at <strong>32 RPUs</strong>. RPUs are provider capacity units, not an assertion of identical CPU or memory resources. MSK used <strong>three kafka.m7g.xlarge brokers</strong>, <strong>24 partitions</strong>, replication factor three, and 500 GB of storage per broker.</p>
<p class="note-heading"><strong>① Preparation cost:</strong></p>

<p>The model includes ClickHouse’s complete two-node HA ingest service and Redshift’s writer plus MSK broker and storage costs. The accepted <a href="https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/redshift-serverless/costs/writer_capacity_assumption.json">writer-capacity scenario</a> prices <strong>32 active RPUs</strong> across the complete producer window. The original long run used 128 writer RPUs; subsequent characterization found that 32 sustained the target and 16 did not. The cost is modeled at 32; the recorded latency and freshness remain from the long run.</p>
<p class="note-heading"><strong>② Query cost and ③ runtime:</strong></p>

<p>ClickHouse prices recorded query duration at its read-side compute rate. Redshift allocates hourly reader compute_seconds to statements in proportion to their recorded elapsed time, then prices the query allocations. Accumulated runtime sums the accepted query durations. The allocation represents query work, rather than reconstructing a complete invoice.</p>
<p class="note-heading"><strong>Target versus observed rate:</strong></p>

<p>Redshift’s <a href="https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/redshift-serverless/README.md">completed run</a> ingested all <strong>113,219,565,734 rows</strong> in <strong>113,227 seconds</strong>, about <strong>31.45 hours</strong>, averaging <strong>999,933 rows/s</strong>. ClickHouse completed its ingest in about <strong>36.75 hours</strong>, averaging approximately <strong>0.86 million rows/s</strong>. The target was shared; observed progress differed. Kafka delivery, streaming-view visibility, and child-MV visibility are separate milestones.</p>
<p class="note-heading"><strong>Reporting window:</strong></p>

<p>Per-query latency plots stop at 100 billion rows. Preparation cost covers the complete producer window; accumulated query cost and runtime use the accepted active-ingestion observations through the reference endpoint. Later query observations and freshness samples are excluded. The writer model also includes both child-MV refresh paths, described below.</p>
  </div>
</details>

ClickHouse Cloud led in all three measured components:

- ① **Preparation cost:** $28.69 versus $522.03.
- ② **Normalized query cost:** about $0.05 versus $24.97.
- ③ **Accumulated query runtime:** 58.12 seconds versus 1.69 hours.

The charts below track those differences as data continues to arrive.

<iframe src="/uploads/03_accumulated_cost_and_runtime_c41c1b85c5.html" frameborder="0" style="width: 100%; height: 500px; max-height: 800px;"></iframe>

The next chart applies the score formula: **19.0× lower combined preparation and normalized query cost**, multiplied by **104.8× lower accumulated query runtime**, produces ClickHouse Cloud’s end-to-end lead.

<iframe src="/uploads/04_final_ranking_score_8a719e21e9.html" frameborder="0" style="width: 100%; height: 500px; max-height: 800px;"></iframe>

<details class="note-box">
  <summary>Pricing, formulas, and the 1,996× score (click to expand)</summary>
  <div class="note-body">
<p class="note-heading"><strong>Pricing basis:</strong></p>

<p>ClickHouse Cloud uses <strong>$0.3903 per compute unit (CU) per hour</strong>. Redshift uses the checked-in <a href="https://aws.amazon.com/redshift/pricing/"><strong>eu-west-2 rate</strong></a> <strong>of $0.467/RPU-hour</strong>. <a href="https://aws.amazon.com/msk/pricing/">MSK</a> uses <strong>$0.47175 per broker-hour</strong> and <strong>$0.116 per GB-month</strong> of broker storage. The <a href="https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/redshift-serverless/costs/out/t2/full_path_super.json">accepted full-path summary</a> retains the model and full-precision inputs.</p>
<p class="note-heading"><strong>① Complete preparation cost:</strong></p>

<p>The full-path scenario includes writer compute over the complete 113,227-second producer window, MSK broker uptime, and prorated broker storage. The writer covers streaming ingestion, background sorting, and both child-MV refreshes.</p>
<p class="note-heading"><strong>ClickHouse Cloud:</strong></p>

<p>2 CUs × 36.75 hours × $0.3903/CU-hour = <strong>$28.68705</strong>, including both HA ingest nodes.</p>
<p class="note-heading"><strong>Redshift writer:</strong></p>

<p>The <a href="https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/redshift-serverless/costs/writer_capacity_assumption.json">32-active-RPU scenario</a> uses <strong>32 × (113,227 ÷ 3,600) hours × $0.467/RPU-hour = $470.01785778</strong>. The long run used 128 writer RPUs; the 32-RPU cost scenario is grounded in subsequent keep-up characterization and is not original-run billing.</p>

<p class="note-heading"><strong>MSK:</strong></p>

<p>Three brokers × producer uptime × $0.47175/broker-hour, plus 1,500 GB × $0.116/GB-month × uptime-hours ÷ 730, totals <strong>$52.00912922</strong>.</p>
<p class="note-heading"><strong>Shared preparation path:</strong></p>

<p>Writer + MSK = <strong>$522.02698699</strong>. That complete total is charged once in this score. It is neither split between the two read alternatives nor doubled within the comparison.</p>
<p class="note-heading"><strong>② Normalized query cost:</strong></p>

<p>ClickHouse prices recorded durations. Redshift allocates each hour’s reader <a href="https://docs.aws.amazon.com/redshift/latest/dg/SYS_SERVERLESS_USAGE.html#SYS_SERVERLESS_USAGE-table-columns">SYS_SERVERLESS_USAGE.compute_seconds</a> across statements that began in that hour, in proportion to statement elapsed_time; the accepted query share is priced at $0.467/RPU-hour.</p>
<p class="note-heading"><strong>ClickHouse Cloud:</strong></p>

<p>8 CUs × $0.3903/CU-hour × (10.207s aggregate + 47.915s drill-down) ÷ 3,600 ≈ <strong>$0.05041</strong>, using the rounded cost-summary inputs.</p>
<p class="note-heading"><strong>Redshift aggregate work:</strong></p>

<p>The <a href="https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/redshift-serverless/results/t2/billed_per_query_reader.csv">committed hourly allocations</a> assign <strong>$2.955693203</strong> to the 760 aggregate executions. This uses recorded reader compute and statement duration, rather than a flat 32-RPU rate multiplied by each query’s wall time.</p>
<p class="note-heading"><strong>Redshift drill-down work:</strong></p>

<p>The 66 executions receive <strong>$22.011782831</strong>, giving total normalized query cost of <strong>$24.967476034</strong>. Together, the two workloads receive <strong>53.4635461 RPU-hours</strong> of allocated reader compute.</p>
<p class="note-heading"><strong>Allocation boundary:</strong></p>

<p>Historical evidence fields named billed_times or billed_rpu_seconds hold hourly compute allocations; their names do not establish invoice billing. Database storage, client cross-AZ transfer, producer VM cost, discounts, and later post-ingestion observations are excluded from the headline scope. MSK’s broker storage is included in its preparation component.</p>
<p class="note-heading"><strong>③ Accumulated query runtime:</strong></p>

<p>ClickHouse: <strong>10.207s aggregate + 47.915s drill-down = 58.122s</strong>. Redshift: <strong>722.871916s aggregate + 5,370.670031s drill-down = 6,093.541947s</strong>.</p>
<p class="note-heading"><strong>Comparison boundary:</strong></p>

<p>① uses the complete producer window and declared 32-RPU writer model. ② and ③ use 190 four-query aggregate batches and 33 two-query drill-down batches against the streaming view. The writer also maintains the typed child, but typed query executions are outside this score. Latency statistics use the separate 100-billion-row window.</p>
<p class="note-heading"><strong>Final score:</strong></p>

<p>ClickHouse: <strong>($28.68705 + $0.05041) × 58.122 = 1,670.27865</strong>. Redshift: <strong>($522.02698699 + $24.967476034) × 6,093.541947 = 3,333,133.70523</strong>. The ratio is <strong>1,995.555×</strong>, rounded to <strong>1,996×</strong>.</p>
  </div>
</details>


---

## 1,996× better real-time performance per dollar

Interested in seeing how ClickHouse works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-2601-1-996-better-real-time-performance-per-dollar-sign-up&utm_blogctaid=2601)

---

All benchmark code and results are available in the [CostBench repository](https://github.com/ClickHouse/CostBench/tree/main/full-path-realtime/quotes). The stock-quotes dataset requires a [separate data license](https://github.com/ClickHouse/CostBench/tree/main/full-path-realtime/quotes#data-source-and-licensing), so the data itself cannot be redistributed.

To explain that result, we follow the same path as the data: preparation first, then query serving.

## How ClickHouse Cloud prepares incoming data

The benchmark used a dedicated ClickHouse Cloud ingest service with **two 2-CPU nodes for high availability**, the smallest HA configuration that sustained the target during calibration. The shared client sent rows through [asynchronous inserts](https://clickhouse.com/blog/asynchronous-data-inserts-in-clickhouse) built into each node.

The diagram below shows those same nodes handling ① columnar storage, ② ordering raw data, and ③ ordered pre-aggregation, plus background merges, on **four CPU cores in total**.

<iframe src="/uploads/05_clickhouse_fresh_data_path_fb6df76ab2.html" frameborder="0" style="width: 100%; height: 500px; max-height: 800px;"></iframe>

**① Store in columns and ② order data:** When an ingest node flushes its asynchronous-insert buffer, it sorts raw quotes by the [MergeTree](https://clickhouse.com/docs/engines/table-engines/mergetree-family/mergetree) table’s (sym, t) key, stock symbol and event timestamp, and writes an ordered [data part](https://clickhouse.com/docs/parts).

**③ Order and pre-aggregate data:** The same node runs the [incremental MV](https://clickhouse.com/docs/materialized-view/incremental-materialized-view) query over the incoming block in memory, computes aggregate states, and sorts the results by the [AggregatingMergeTree](https://clickhouse.com/docs/engines/table-engines/mergetree-family/aggregatingmergetree) table’s (sym, day) key before writing an ordered part containing the summaries.

[Background merges](https://clickhouse.com/docs/merges) consolidate parts in both tables.

> The result: raw data and pre-aggregations [advance together](https://clickhouse.com/docs/resources/support-center/knowledge-base/materialized-views/are-materialized-views-inserted-asynchronously) from the same flushed insert block, without a separate refresh cycle.

<details class="note-box">
  <summary>How much work did the four-core ingest service handle? (click to expand)</summary>
  <div class="note-body">
<p>The <a href="https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/clickhouse-cloud/results_t2">ClickHouse writer-utilization results</a> show ingestion continuing alongside background maintenance. CPU usage remained around 3.1 of the 4 available cores, tracked memory stayed within capacity, background merges processed several million rows per second, and the maximum active-part count per partition stayed around 100. These diagnostics describe the ClickHouse source run reused for this comparison.</p>
<p>Both nodes were retained for high availability, so the preparation cost includes the complete two-node deployment.</p>
  </div>
</details>

Now follow the same preparation tasks through Redshift Serverless, from the MSK stream to the streaming view and its daily summaries.

## How Redshift Serverless prepares incoming data

The benchmark used [Redshift streaming ingestion](https://docs.aws.amazon.com/redshift/latest/dg/materialized-view-streaming-ingestion.html) from Amazon MSK directly into a materialized view, without an S3 landing stage. The view stored each quote’s payload in Redshift’s [SUPER data type](https://docs.aws.amazon.com/redshift/latest/dg/super-overview.html), with symbol and event timestamp exposed as typed sort-key columns. The charts label this read path “SUPER.”

The diagram below follows ① columnar storage in the streaming view, ② background sorting, and ③ incremental refresh of the daily aggregate MV. It shows the **32-RPU writer scenario** used for preparation pricing, separately from the query consumer.

<iframe src="/uploads/06_redshift_serverless_fresh_data_path_b7321862c5.html" frameborder="0" style="width: 100%; height: 500px; max-height: 800px;"></iframe>

**① Store in columns:** The producer sends quotes to MSK. Redshift’s writer consumes that topic into the [quotes_streamed materialized view](https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/redshift-serverless/sql/setup_streaming.sql), with AUTO REFRESH YES. The live streaming view retains the event-level payload used by the headline drill-down queries.

**② Order data:** The streaming view used SORTKEY (sym, t), with DISTSTYLE EVEN to preserve scan parallelism for symbol filters. Redshift [sorts in the background](https://docs.aws.amazon.com/redshift/latest/dg/t_Reclaiming_storage_space202.html#automatic-table-sort), so newly arrived rows can be visible before that layout work is complete.

**③ Order and pre-aggregate data:** A separate daily MV groups directly from the streaming view by (sym, day), with its own sort key. A controller repeatedly issues incremental [REFRESH MATERIALIZED VIEW ... RESTRICT](https://docs.aws.amazon.com/redshift/latest/dg/materialized-view-refresh-sql-command.html). The daily MV and a typed raw projection are sibling branches; daily summaries do not wait for the typed branch.

> The result: Redshift’s streaming view, background sorting, and daily summaries advance through separate stages, so queries can encounter unfinished preparation.

<details class="note-box">
  <summary>Why these ingestion paths, and how were they buffered? (click to expand)</summary>
  <div class="note-body">
<p class="note-heading"><strong>The same ingestion problem:</strong></p>

<p>The source produces frequent writes that must become efficient analytical storage. ClickHouse accepts them through native asynchronous inserts. Redshift’s recommended high-rate streaming path includes an MSK broker cluster plus a consuming writer workgroup; both belong in preparation cost.</p>
<p class="note-heading"><strong>Redshift’s streaming path:</strong></p>

<p>The <a href="https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/redshift-serverless/broker/produce_quotes.py">producer</a> used <strong>16 processes</strong> and lz4 compression. MSK provided three brokers across three availability zones, with 24 partitions and replication factor three. Redshift consumed the stream directly; no intermediate S3 load job was added.</p>
<p class="note-heading"><strong>ClickHouse’s native path:</strong></p>

<p>Ordinary INSERT requests with async_insert enabled were buffered on each receiving node. An <a href="https://clickhouse.com/docs/optimize/asynchronous-inserts">adaptive flush timeout</a> responded to incoming traffic. Ordering and pre-aggregation ran on the ingest nodes; the dedicated <a href="https://clickhouse.com/docs/cloud/reference/warehouses">ingest service</a> shared storage with the independently sized read service.</p>
<p class="note-heading"><strong>Shared pacing:</strong></p>

<p>Both adapters read the same Parquet dataset and decoded the same schema under the same target-rate model. Parallelism and client batch sizes were adapted to each destination’s API; they were not forced to be identical.</p>
<p class="note-heading"><strong>ClickHouse batches:</strong></p>

<p>The client sent 3,000-row batches through asynchronous inserts. Default buffering flushed at the first of three thresholds: 100 MiB buffered, an adaptive timeout between 50 milliseconds and 1 second, or 450 queued insert queries.</p>
<p class="note-heading"><strong>Redshift delivery:</strong></p>

<p>Producer acknowledgments report Kafka delivery, not completion of all downstream views. Streaming ingestion advances the raw streaming view; separate refresh transactions advance the typed projection and daily summaries.</p>
<p class="note-heading"><strong>Batch-size boundary:</strong></p>

<p>Client INSERT batches and Kafka batches are transport units. They do not define the final MergeTree part, Redshift storage block, or daily-MV refresh size.</p>
<p class="note-heading"><strong>Progress and refresh evidence:</strong></p>

<p>The monitor sampled <a href="https://docs.aws.amazon.com/redshift/latest/dg/SYS_STREAM_SCAN_STATES.html">SYS_STREAM_SCAN_STATES</a> during ingestion and journaled child refreshes. These point-in-time observations were recorded while the workload ran; they were not reconstructed from a post-run view.</p>
<p class="note-heading"><strong>Incremental maintenance:</strong></p>

<p>The two child MVs are defined directly on quotes_streamed and refreshed with RESTRICT. The refresh journal’s server status identifies incremental updates; labels such as Manual or Auto alone do not establish incremental versus full refresh. Each child refreshes independently.</p>
<p class="note-heading"><strong>Writer-capacity boundary:</strong></p>

<p>The diagram’s 32 RPUs come from the <a href="https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/redshift-serverless/costs/writer_capacity_assumption.json">accepted capacity scenario</a>: 32 RPUs sustained the target in characterization with about five seconds of median streaming lag, while 16 fell behind. The long-run measurements were recorded with a 128-RPU writer. Pricing 32 RPUs does not turn those latency or freshness measurements into a 32-RPU rerun.</p>
  </div>
</details>

## What this means for freshness and preparation cost

### Pre-aggregation lag

ClickHouse builds summaries during inserts; Redshift refreshes them separately. The chart below follows **Redshift’s Kafka event watermark to its daily aggregate MV**: the underlying active observations show **46 seconds of median lag**. ClickHouse’s zero line represents raw data and summaries advancing together.

<iframe src="/uploads/07_pre_aggregation_lag_7424acbee7.html" frameborder="0" style="width: 100%; height: 500px; max-height: 800px;"></iframe>

The Redshift series includes the streaming-ingestion and daily-refresh path, while ClickHouse’s baseline describes raw-to-summary synchronization. Queries against Redshift’s daily MV read its last completed refresh; they do not automatically add the newer streaming rows. The serving comparison below retains that freshness behavior.

<details class="note-box">
  <summary>How was pre-aggregation freshness measured? (click to expand)</summary>
  <div class="note-body">
<p class="note-heading"><strong>Redshift series:</strong></p>

<p>The <a href="https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/redshift-serverless/results/t2/charts/redshift_freshness_wide_summary.json">freshness evidence</a> uses successful daily refresh records through the active endpoint. It measures the Kafka event watermark represented in the daily MV, rather than only the interval between refresh completions. The lag sampler supplies the row-progress timeline.</p>
<p class="note-heading"><strong>Statistics and display:</strong></p>

<p>The active daily-MV series contains <strong>1,884 observations</strong>, with <strong>46 seconds median</strong>, <strong>53 seconds P95</strong>, and <strong>79 seconds maximum</strong> lag. The chart applies a centered five-observation rolling median; its displayed curve reaches about <strong>64 seconds</strong>. The first nonmonotonic lag sample and <strong>463 post-ingestion daily refreshes</strong> are excluded.</p>
<p class="note-heading"><strong>ClickHouse baseline:</strong></p>

<p>The zero line is a benchmark-semantic raw-to-summary baseline, not a separately polled source-to-query metric. The raw table and incremental MV consume the same flushed insert block. It does not claim zero ingestion delay or use the same source-watermark boundary as Redshift’s series.</p>
  </div>
</details>

> ClickHouse kept raw data and summaries together; Redshift’s daily summaries trailed the Kafka event watermark by **46 seconds at the median**.

Freshness is one consequence of the preparation path. The next chart accounts for the cost of running that path.

### Cost of keeping incoming data query-ready

ClickHouse handles ① columnar storage, ② ordering raw data, and ③ ordered pre-aggregation inside its ingest service. Redshift handles that work in its writer, fed by a separately charged MSK cluster. The chart below compares ClickHouse’s preparation cost with the **32-RPU Redshift writer scenario plus MSK**.

<iframe src="/uploads/08_fresh_data_path_cost_8b255b115c.html" frameborder="0" style="width: 100%; height: 500px; max-height: 800px;"></iframe>

ClickHouse’s complete ingest service cost **$28.69**. Redshift’s modeled preparation path totaled **$522.03**: **$470.02** for the writer, including streaming ingestion, sorting, and both child-MV refresh paths, plus **$52.01** for MSK brokers and storage. The shared path is charged once.

> ClickHouse handled the complete preparation path at **18.2× lower cost** than the Redshift writer-plus-MSK scenario.

Now follow the raw data and summaries into query serving.

## How ClickHouse Cloud serves queries

Ordered raw data lets drill-downs skip unrelated rows; pre-aggregations let interactive aggregations combine prepared results instead of recalculating them from individual quotes. The diagram below follows both paths through ClickHouse Cloud’s read service: **one node with 16 CPUs and 64 GiB of memory**.

<iframe src="/uploads/09_clickhouse_query_serving_58c9367ec0.html" frameborder="0" style="width: 100%; height: 500px; max-height: 800px;"></iframe>

**Drill-downs:** Queries prune ordered raw data in the [event-level MergeTree table](https://clickhouse.com/docs/engines/table-engines/mergetree-family/mergetree). Filtering by symbol, the leading column of its (sym, t) sorting key, lets the read service skip unrelated quotes.

**Interactive aggregations:** Queries read current pre-aggregations from the [AggregatingMergeTree table](https://clickhouse.com/docs/engines/table-engines/mergetree-family/aggregatingmergetree), combining prepared counts, sums, minima, and maxima from a much smaller set of daily summary rows. There is no independent refresh to wait for.

> The result: drill-downs prune ordered raw data; interactive aggregations read summaries kept current during ingestion.

Redshift separates serving into a consumer workgroup, reading the streaming and aggregate views through a live datashare.

## How Redshift Serverless serves queries

The diagram below shows a separate **32-RPU consumer workgroup** reading shared data from the writer. The [live datashare](https://docs.aws.amazon.com/redshift/latest/dg/datashare-overview.html) exposes the streaming view and daily aggregate MV without copying them into a second serving database.

<iframe src="/uploads/10_redshift_serverless_query_serving_1cd32e348b.html" frameborder="0" style="width: 100%; height: 500px; max-height: 800px;"></iframe>

**Drill-downs:** The [drill-down queries](https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/redshift-serverless/sql/queries_drilldown_super.sql) filter the typed sym column in quotes_streamed, then navigate and cast measure fields from the payload. Its (sym, t) sort key supports pruning, but incoming rows can be read before background sorting completes.

**Interactive aggregations:** Queries read the [daily aggregate MV](https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/redshift-serverless/sql/queries_dashboard.sql) as of its last completed refresh. They do not merge newer streaming-view rows into the answer at query time, so the returned summary can trail incoming data.

The diagram’s two paths show where preparation remains visible to readers: drill-downs can encounter unsorted data, while aggregate queries can read an earlier summary snapshot.

<details class="note-box">
  <summary>What do Redshift’s refresh and datashare guarantees mean? (click to expand)</summary>
  <div class="note-body">
<p class="note-heading"><strong>Snapshot contract:</strong></p>

<p>A query reads committed contents of the daily MV. The benchmark did not force a refresh before every query or reconstruct its answer from newer streaming rows. The measured aggregate latency therefore retains Redshift’s summary-refresh lag.</p>
<p class="note-heading"><strong>Refresh contract:</strong></p>

<p>AUTO REFRESH YES drives streaming ingestion. A controller separately refreshes the downstream MVs because Redshift does not permit <a href="https://docs.aws.amazon.com/redshift/latest/dg/materialized-view-create-sql-command.html#mv_CREATE_MATERIALIZED_VIEW-limitations">automatic refresh</a> on an MV defined on another MV. RESTRICT updates only the named child from the committed parent state. This avoids stacking the typed projection’s refresh delay into daily-summary freshness.</p>
<p class="note-heading"><strong>Live-share contract:</strong></p>

<p>Sharing exposes the writer’s committed objects to the reader workgroup. It separates read compute from preparation compute; it does not make those objects fresher or sort their newest rows before queries access them.</p>
<p class="note-heading"><strong>Read-path boundary:</strong></p>

<p>The headline drill-down results come from the live streaming view. A typed projection was also maintained and measured as an alternative. Its refresh and storage-layout work are retained in the shared preparation scenario, even though its query executions are excluded from this article’s score.</p>
<p class="note-heading"><strong>Sizing boundary:</strong></p>

<p>The reader was fixed at base=max 32 RPUs during the long run. Writer capacity is modeled separately for preparation cost. The score combines those declared cost assumptions with the recorded read-path results; it does not present them as a literal provider invoice.</p>
  </div>
</details>

> The result: Redshift drill-downs can read rows before background sorting finishes; interactive aggregations can return summaries from an earlier refresh.

## What this means for query performance and cost

### Drill-downs over ordered raw data

ClickHouse used ORDER BY (sym, t) and ordered rows during inserts; Redshift used SORTKEY (sym, t) and relied on background sorting. [D1 and D2](https://clickhouse.com/blog/costbench-real-time-performance-per-dollar#the-continuous-query-workload) investigate one stock’s growing history: hourly price summaries and a risk-and-liquidity profile. The chart follows Redshift’s live streaming view, bypassing the daily aggregate MV.

<iframe src="/uploads/11_drill_down_query_latency_44cbc98118.html" frameborder="0" style="width: 100%; height: 500px; max-height: 800px;"></iframe>

ClickHouse Cloud is yellow; Redshift Serverless is orange.

<details class="note-box">
  <summary>How were query latencies and accumulated results compared? (click to expand)</summary>
  <div class="note-body">
<p class="note-heading"><strong>Query definitions:</strong></p>

<p>Part 1 describes A1-A4 and D1-D2. The Redshift SQL preserves the symbol filter and full-history scope, with engine-specific substitutions. D1 uses window functions for first and last prices; D2 uses approximate discrete percentiles and moment calculations. Its excess-kurtosis convention differs from ClickHouse’s raw population kurtosis, so strict numerical equivalence is not asserted for that field.</p>
<p class="note-heading"><strong>Cache policy:</strong></p>

<p><a href="https://docs.aws.amazon.com/redshift/latest/dg/r_enable_result_cache_for_session.html">enable_result_cache_for_session</a> was off. Underlying data caches were allowed to operate normally; the benchmark did not flush them between queries.</p>
<p class="note-heading"><strong>Timing:</strong></p>

<p>Redshift latency uses <a href="https://docs.aws.amazon.com/redshift/latest/dg/SYS_QUERY_HISTORY.html#SYS_QUERY_HISTORY-table-columns">SYS_QUERY_HISTORY.elapsed_time</a>, converted to seconds; ClickHouse uses its recorded runner duration. Median, P99, and maximum pool unsmoothed per-query observations with <strong>0 &lt; raw_rows ≤ 100 billion</strong>. P99 uses linear interpolation. Accumulated runtime uses the same recorded timing basis.</p>
<p class="note-heading"><strong>Latency charts:</strong></p>

<p>Each system is plotted at its own observed ingestion progress. Aggregate trends use a centered seven-observation rolling median; drill-downs use five observations, with shrinking edge windows. No outliers are removed. The curves are display smoothing; the statistics and accumulated totals use the original recorded durations.</p>
<p class="note-heading"><strong>Interactive readouts:</strong></p>

<p>Values below the plots follow the displayed trends at the selected row count. Logarithmic scales keep milliseconds and seconds readable together; Linear shows absolute differences. Each chart has its own playback and row-position controls.</p>
<p class="note-heading"><strong>Accepted accumulated workload:</strong></p>

<p>The <a href="https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/redshift-serverless/results/t2/charts/full_path_cost_performance_clickhouse_vs_redshift_super_wide_summary.json">selection</a> contains <strong>190 four-query aggregate batches</strong> and <strong>33 two-query drill-down batches against the streaming view</strong> per system: <strong>760 + 66 = 826 executions</strong>. ClickHouse observations are aligned monotonically to Redshift row progress through the <strong>113,219,565,734-row reference horizon</strong>. Later post-ingestion observations are excluded.</p>
<p class="note-heading"><strong>Accumulated charts:</strong></p>

<p>Query durations are added at corresponding ingestion counts as step sums, without smoothing or interpolating future executions into earlier positions. Preparation-cost lines allocate the complete-ingest total proportionally by row progress; they are not metered cost-at-time traces. The score sums query durations, not elapsed ingestion time.</p>
  </div>
</details>

**ClickHouse Cloud:**

- **722.5 ms median** - 98.6× faster than Redshift Serverless
- **1.15 s P99** - 281× faster
- **1.18 s maximum** - 378× faster

Accumulated runtime was **47.92 seconds** across the 33 two-query batches. Both drill-downs stayed near or below one second for most of the plotted window.

**Redshift Serverless:**

- **71.27 s median**
- **322.96 s P99**
- **446.00 s maximum**

Accumulated runtime was **89.51 minutes** across the same 33 batches. Reading the growing streaming view took substantially longer, with D1’s window-based hourly summaries showing the larger latency curve.

> Across this drill-down workload, ClickHouse Cloud was **112× faster overall**.

<details class="note-box">
  <summary>Why use Redshift’s streaming view, and what about typed columns? (click to expand)</summary>
  <div class="note-body">
<p class="note-heading"><strong>Streaming view:</strong></p>

<p>The <a href="https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/redshift-serverless/sql/setup_streaming.sql">streaming view</a> keeps the payload as SUPER and promotes sym and t to typed sort-key columns. D1 and D2 filter the typed sym column, preserving pruning intent; they cast the payload’s measure fields when computing results. This is a different representation from ClickHouse’s typed raw table.</p>
<p class="note-heading"><strong>Typed alternative:</strong></p>

<p>A sibling typed MV projects the payload fields into columns, with the same (sym, t) sort key and EVEN distribution. Its queries implement the same Redshift drill-down logic. Both representations were measured during the long run.</p>
<p class="note-heading"><strong>Observed outcome:</strong></p>

<p>Across the active-ingestion comparison, the <a href="https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/redshift-serverless/results/t2/charts/drilldown_query_latency_redshift_super_vs_typed_wide_summary.json">typed alternative</a> accumulated <strong>2.11× as much drill-down runtime as the streaming view</strong>. D1 was approximately equal; D2 was <strong>4.42× slower</strong> on typed data. The primary article follows the faster measured alternative, which reads the streaming view.</p>
<p class="note-heading"><strong>Cost boundary:</strong></p>

<p>The writer-plus-MSK preparation cost includes both child refreshes and is shared unchanged between the read alternatives. The score for the streaming view charges only its aggregate and drill-down query allocations, rather than adding typed query executions.</p>
<p class="note-heading"><strong>Interpretation:</strong></p>

<p>The benchmark measures the complete recorded query outcome. It does not isolate how much of the gap comes from background sorting, payload navigation, query formulation, or other engine work. A typed layout cannot be assumed faster from a short characterization when the complete run shows otherwise.</p>
  </div>
</details>

### Interactive aggregations over ordered pre-aggregated data

Daily pre-aggregations let [A1-A4](https://clickhouse.com/blog/costbench-real-time-performance-per-dollar#the-continuous-query-workload) combine prepared counts, sums, and price minima and maxima. A1-A2 filter summaries by symbol; A3-A4 read across all symbols. ClickHouse reads current summaries; Redshift reads its last completed daily-MV refresh. The chart compares aggregate latency as ingestion continues.

<iframe src="/uploads/12_aggregate_query_latency_128abf272e.html" frameborder="0" style="width: 100%; height: 500px; max-height: 800px;"></iframe>

**ClickHouse Cloud:**

- **13 ms median** - 34.6× faster than Redshift Serverless
- **42 ms P99** - 128× faster
- **111 ms maximum** - 57.2× faster

Accumulated runtime was **10.21 seconds** across the 190 four-query batches.

**Redshift Serverless:**

- **449.4 ms median**
- **5.32 s P99**
- **6.35 s maximum**

Accumulated runtime was **12.05 minutes** across the same 190 batches. These queries read refreshed summaries without waiting for the next update. ClickHouse served them faster while maintaining summaries during inserts; Redshift’s measured latency came with a refresh-dependent freshness boundary.

> Across the interactive-aggregation workload, ClickHouse Cloud was **70.8× faster overall**, with summaries maintained during inserts.

### Accumulated query cost and runtime

Drill-downs account for most of Redshift’s accumulated query runtime. The charts below combine both workloads and show the reader compute allocated to that query work.

<iframe src="/uploads/13_query_runtime_and_cost_940b06649f.html" frameborder="0" style="width: 100%; height: 500px; max-height: 800px;"></iframe>

Across **826 accepted executions per system**, ClickHouse Cloud accumulated **58.12 seconds** of query runtime and Redshift **1.69 hours**. Normalized query-serving cost was about **$0.05** versus **$24.97**, respectively. These are costs attributed to the accepted query work, not complete provider invoices.

> ClickHouse Cloud served the query workload **104.8× faster overall**, with **495× lower normalized query cost**.

## From the field: Clay

Clay’s customers were feeling the limits of its Redshift reporting system. Credit-usage dashboards routinely timed out or took too long to load, with P95 query latency around 60 seconds.

After migrating the reporting workload to ClickHouse, Clay improved both the speed of the answers and the freshness of the data behind them. In his Open House talk, software engineer Paul Noble reports that P95 query latency fell from approximately 60 seconds to 1 second, while dashboard data freshness improved from approximately 75 seconds to 4 seconds. [Watch Clay’s migration example](https://www.youtube.com/watch?v=3NLJ0IhgsC8&t=405).

Those improvements address two requirements of customer-facing analytics: recent data and answers fast enough to use interactively. Clay’s figures describe its own production migration; CostBench measures the separate Redshift Serverless workload described above.

## Redshift Serverless can’t match ClickHouse Cloud for real-time analytics

While fresh data kept arriving, ClickHouse Cloud led in all three measured components:

- **① Preparation cost: 18.2× lower** than the Redshift writer-plus-MSK scenario.
- **② Normalized query cost: 495× lower** across the accepted query work.
- **③ Accumulated query runtime: 104.8× lower** across both query workloads.

The final chart brings these results together, plotting combined preparation and normalized query cost against accumulated query runtime as fresh data arrives.

<iframe src="/uploads/14_end_to_end_cost_vs_accumulated_query_clickhouse_redshift_serverless_b470e69354.html" frameborder="0" style="width: 100%; height: 500px; max-height: 800px;"></iframe>

Up is lower total modeled cost; right is lower accumulated query runtime.

> **ClickHouse Cloud delivered 1,996× better end-to-end performance per dollar in this streaming comparison, with summaries kept current during inserts.**

The difference starts in the preparation path. ClickHouse orders raw quotes and builds current summaries during inserts. Redshift’s stream, background sorting, and child-MV refreshes advance separately. Its drill-downs took much longer, and aggregate queries were slower even while reading refresh-dependent snapshots.

That is why Redshift Serverless can’t match ClickHouse Cloud for real-time analytics.
