---
title: "Measuring real-time performance per dollar under continuous load: CostBench’s first end-to-end results"
date: "2026-09-08T07:38:02.697Z"
author: "Tom Schreiber and Lionel Palacin"
category: "Engineering"
excerpt: "CostBench puts cloud data warehouses under continuous load. Across the complete path from fresh data to fast answers, ClickHouse Cloud delivers 412–1,996× better performance per dollar."
---

# Measuring real-time performance per dollar under continuous load: CostBench’s first end-to-end results

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

**Real-time performance per dollar depends on both the cost of keeping incoming data query-ready and how much work that preparation leaves for the query engine.**

* CostBench measures both effects as one continuous workload under sustained load: fresh rows are ingested and made query-ready while aggregate and drill-down queries continue to run. 
* We tested ClickHouse Cloud, Snowflake, BigQuery, and Redshift Serverless using each vendor’s recommended real-time ingest path, streaming more than 100 billion stock-market quotes at a target rate of 1 million rows per second. 
* ClickHouse Cloud had the lowest fresh-data-path cost, query-serving cost, and accumulated runtime. The tested alternatives delivered **412–1,996× worse end-to-end performance per dollar.** 
* This post launches a series of 1:1 analyses tracing the architectures and billing behind those results.

##  The path from fresh data to fast queries shapes performance per dollar

A [real-time analytics system](https://clickhouse.com/blog/selecting-a-real-time-analytical-database) never works on a finished dataset. New rows keep arriving while users, applications, and agents query data that may already span billions or [trillions](https://clickhouse.com/blog/how-tesla-built-quadrillion-scale-observability-platform-on-clickhouse) of rows. Each new row must become query-ready while those queries continue to run.

[CostBench](https://clickhouse.com/blog/costbench-data-warehouse-cost-performance)’s first results show that query engines are only part of what separates cloud data warehouses: 
 
> Systems vary dramatically in the cost and efficiency of carrying incoming data from arrival to query readiness.  
 
**Under sustained load, that work can shape performance per dollar as much as query execution itself: it carries its own direct cost, and the state it produces determines how much work remains for the query engine.**

This first end-to-end round tested ClickHouse Cloud, Snowflake, BigQuery, and Redshift Serverless using push-based ingestion.  
 
CostBench measured the complete workload-ingestion, ongoing query-readiness work, and aggregate and drill-down query serving-all running together. This post first explains what **query-ready** means, then shows how the benchmark measures both effects and presents the overall results. The 1:1 posts that follow trace those results through each provider’s architecture and billing model.


## What makes data query-ready

Consider a common analytical pattern: filter a contiguous range of rows, such as all events for a specific day in a web analytics table, then group and aggregate the results:
<pre>
<code type='click-ui' language='sql' show_line_numbers='false'>
SELECT
    URL,
    COUNT(*) AS pageviews,
    COUNT(DISTINCT User) AS users
FROM hits
WHERE Day = 'D2'
GROUP BY URL;
</code>
</pre>

This is exactly the kind of query analytical systems are built to run fast. To do so, they keep data **query-ready** by **minimizing how much data the query engine must read and how much repeated work it must do**. 

For a typical analytical query like this one, that translates into three requirements: store data by column, organize it for chunk pruning, and pre-aggregate repeated calculations.


### Store data by column

Most analytical queries do not need every column in a table. They may filter by one column, group by another, and calculate aggregates from a third. The example query uses only Day, User, and URL.

[Columnar storage](https://en.wikipedia.org/wiki/Data_orientation) lets the engine read those three columns directly and skip every other column, even if the table contains hundreds.

![01_columnar_storage_skips_unrelated_columns.png](https://clickhouse.com/uploads/01_columnar_storage_skips_unrelated_columns_31152a563a.png)


### Organize data for chunk pruning

Analytical engines process column values in chunks, which enables efficient [vectorized execution](https://en.wikipedia.org/wiki/Single_instruction,_multiple_data). 

Chunks are also the unit of pruning. Before reading a chunk, the engine checks its metadata and skips it when its values fall outside the query’s filter. Pruning works best when the physical layout keeps similar values together, for example by [sorting](https://en.wikipedia.org/wiki/Database_index#Clustered) on the filtered column. In the example below, ordering by Day lets the engine read only the D2 chunk and skip the D1 and D3 chunks.

![02_ordered_data_enables_chunk_pruning.png](https://clickhouse.com/uploads/02_ordered_data_enables_chunk_pruning_c33229dae2.png)

### Pre-aggregate repeated calculations

At billions or trillions of rows, scanning and aggregating the raw data for every query is too slow for interactive analytics.

[Pre-aggregations](https://en.wikipedia.org/wiki/Aggregate_(data_warehouse)) move that repeated work out of each query. They maintain a much smaller set of summarized rows, reducing both the data read and the grouping and aggregation performed at query time. The summaries retain the grouping dimensions and aggregate results the queries need, allowing the query engine to combine prepared results instead of repeating those calculations over individual events.

For time-sensitive use cases such as fraud detection, the pre-aggregated rows must also remain current with the event-level data, ideally updating at the same time new events become queryable.

Because analytical queries often still filter these summarized rows, pre-aggregated data also benefits from a pruning-friendly physical layout.

The example below turns nine events into three daily rows ordered by Day. For `WHERE Day = 'D1'`, the engine reads only the D1 row and skips the D2 and D3 rows.

![03_pre_aggregation_reduces_query_time_work.png](https://clickhouse.com/uploads/03_pre_aggregation_reduces_query_time_work_8f947cbb58.png)


Together, columnar storage, pruning-friendly layouts, and current pre-aggregations make analytical data query-ready.




---

## Up to 1,996× better real-time performance per dollar

That’s what ClickHouse Cloud delivered in CostBench under continuous load. See what it can do for your data - sign up today.

[Try ClickHouse Cloud](https://console.clickhouse.cloud/signUp?loc=blog-cta-1818-up-to-1-996-better-real-time-performance-per-dollar-try-clickhouse-cloud&utm_blogctaid=1818)

---

##  Real-time systems must make fresh data query-ready as it arrives


With a fixed dataset, that preparation can happen before queries begin. In a real-time system, new rows arrive continuously while queries keep running. 
 
> “A real-time system should have access to real-time data so it's viable for making real-time decisions based on the **freshest data.**” — [Instacart Engineering](https://tech.instacart.com/real-time-fraud-detection-with-yoda-and-clickhouse-bd08e9dbe3f4) 
 
We call the continuous work that carries each new row from arrival to query readiness the **fresh-data path**. It comprises three responsibilities that must remain active in parallel:


<video autoplay="1" muted="1" loop="1" controls="0">
  <source src="https://clickhouse.com/uploads/04_real_time_system_always_in_motion_loop_9639107a41.mp4" type="video/mp4" />
</video>

① **Ingest fresh data** **into columnar storage** as it arrives.

② **Maintain pruning-friendly physical layouts** for event-level and pre-aggregated data through sorting, clustering, partitioning, or equivalent structures. 
 
③ **Maintain current pre-aggregations** as new data arrives, keeping common grouping and aggregation work out of query time.

These are logical responsibilities, not a strict execution sequence. A system may fuse them in a single write path - for example, sorting incoming rows, computing pre-aggregations, and sorting those results before either representation is written to storage. Other systems complete some of this work asynchronously after ingestion. 
 
Indexes, metadata, compaction, and other provider-specific structures also affect the cost and efficiency of this work.

**Alongside the fresh-data path, the query engine serves two typical analytical paths. Both depend on the preparation described above:**


* **Pre-aggregated path:** Interactive aggregate queries depend on ③ to keep repeated grouping and aggregation out of query time. If they filter the summarized rows, they also depend on ② to prune irrelevant chunks. 

* **Event-level path:** Selective drill-down queries read event-level data directly and therefore depend on ② to avoid scanning most of the data. Even when these queries take seconds, pruning is what makes them feasible at scale; they may still group or aggregate the remaining rows.


##  An efficient fresh-data path lowers its own cost - and the work left for queries

> A system can sustain ingestion while its query readiness falls behind.

That can affect:

- **Answer freshness:** A suspicious payment may be ingested immediately yet reach the fraud query too late.
- **Query efficiency:** When layout or pre-aggregation work remains unfinished, queries must scan more data, reconcile newer rows, or repeat grouping and aggregation at query time.

That extra query work increases:

- latency
- read-side compute
- query-serving cost.

An efficient fresh-data path therefore reduces both the **direct cost of preparing data** and the **runtime and cost of the queries** it serves.



## CostBench measures both effects together

CostBench follows the same continuously growing dataset from ingestion through row visibility, event-level layout maintenance, and pre-aggregation freshness, while aggregate and drill-down queries run on a fixed schedule. The query definitions stay fixed, but their answers must continually account for newly arriving data. This makes both sides visible: the direct cost of keeping data query-ready and the performance and cost of serving queries from the state the system actually achieved.

> The first results show that some systems sustained ingestion while pre-aggregation lag accumulated or query latency rose - moving more work onto the read path and driving up query-serving cost.


### How CostBench keeps the comparison fair

This  round used **push-based ingestion** across **ClickHouse Cloud**, **Snowflake**, **BigQuery**, and **Redshift Serverless**: one shared client sent the stream directly through each system’s recommended low-latency ingest path. Four controls kept the comparison like-for-like while respecting each system’s architecture:



* **Same workload:** Each system received the same 113.2-billion-row National Best Bid and Offer (NBBO) stock-market quotes dataset, schema, layout intent, target ingestion rate of 1 million rows per second, queries, and cadence. 

* **Comparable resources:** We aligned read-side compute where a meaningful comparison was possible and used the smallest tested configurable fresh-data-path compute that sustained the target during calibration. 

* **Complete platform paths:** Each system used its recommended real-time architecture with a low latency push-based ingestion path. Managed and serverless services retained their native scaling, and their metered work remained in the benchmark’s cost. 

* **One shared harness:** The same source files, decoding logic, client host, rate controller, scheduler, timing, and recording logic drove every system; only the destination adapter changed.

We configured matching sorting or clustering keys across systems for both raw data and daily pre-aggregations. These layouts support the workload’s stock-symbol filters. The pre-aggregations group quotes by stock symbol and day, maintaining the counts, sums, and price minima and maxima that the aggregate queries use. Each system therefore had to keep the same preparation current for the same query workload as new rows arrived.



Later rounds may also test **pull-based** variants using one shared external stream, to give a more complete picture of real-time performance per dollar.





<video autoplay="1" muted="1" loop="1" controls="0">
  <source src="https://clickhouse.com/uploads/05_first_end_to_end_real_time_workload_loop_8361702446.mp4" type="video/mp4" />
</video>

> The shared harness holds the workload constant. CostBench measures how each system handles it.

<details class="note-box">
  <summary>BENCHMARK METHODOLOGY AND FAIRNESS CONTROLS (click to expand)</summary>
  <div class="note-body">
    <p class="note-heading"><strong>INGESTION MODEL</strong></p>
    <p>
      The client read NBBO data from Parquet files, decoded it into raw rows, and pushed the stream directly into each platform’s target tables through its vendor-recommended low-latency real-time ingest path. Later rounds will test pull-based variants using one shared external stream.
    </p>
    <p class="note-heading"><strong>WORKLOAD MODEL</strong></p>
    <p>
      In a <a href="https://clickhouse.com/blog/selecting-a-real-time-analytical-database">real-time analytics system</a>, new events are generated continuously at the source at an application-driven rate. Future rows do not yet exist, so the database is never handed a complete backlog to load as quickly as possible. CostBench reproduces that operating condition by using the Parquet files as a deterministic source, decoding their rows, and releasing them as a paced continuous stream while each platform keeps the arriving data query-ready and serves scheduled queries.
    </p>
    <p class="note-heading"><strong>DATASET AND ACTIVE WINDOW</strong></p>
    <p>
      Every system received the same complete 113.2-billion-row dataset of narrow, 12-column National Best Bid and Offer (NBBO) stock-market quotes.
    </p>
    <p>
      All systems used the following sorting or clustering keys:
    </p>
    <ul>
      <li>
        <strong>Event-level data:</strong> <code>(sym, t)</code> — stock symbol and event timestamp.
      </li>
      <li>
        <strong>Daily pre-aggregations:</strong> <code>(sym, day)</code> — stock symbol and day.
      </li>
    </ul>
    <p>
      The harness replayed the entire source as one uninterrupted stream toward a target rate of 1 million rows per second and continued until the final source row had been ingested. At exactly the target rate, that active-ingestion window would last about 31.4 hours; observed durations varied by system.
    </p>
    <p class="note-heading"><strong>SHARED INGESTION CLIENT</strong></p>
    <p>
      The same source files, schema, row-decoding logic, and workload-generation code drove ClickHouse Cloud, Snowflake, BigQuery, and Redshift Serverless. For every system, the client ran on the same AWS EC2 m6i.8xlarge instance, used the same rate controller, and adjusted batch size and worker parallelism to pace the destination toward the target.
    </p>
    <p class="note-heading"><strong>BEST-PRACTICE PLATFORM CONFIGURATION</strong></p>
    <p>
      Only the destination-specific delivery adapter changed. Inside each platform, we used its vendor-recommended low-latency push-based real-time ingest path and documented best practices for keeping incoming data query-ready. Differences between those paths are part of the benchmark.
    </p>
    <p class="note-heading"><strong>RESOURCE-SIZING POLICY</strong></p>
    <p>
      We aligned read-side compute by estimated CPU capacity wherever the platforms allowed a meaningful comparison. For configurable fresh-data-path compute, we used the smallest tested configuration that sustained the target rate of 1 million rows per second during calibration while keeping incoming data query-ready. Managed and serverless components used their native scaling, and their metered work remained part of the benchmark’s cost. Observed end-to-end throughput is reported separately from the configured target.
    </p>
    <p class="note-heading"><strong>SHARED QUERY DRIVER</strong></p>
    <p>
      From the beginning of ingestion through the final source row, the same four interactive aggregate queries ran every 10 minutes and the same two selective drill-down queries every hour, using identical fixed-rate scheduling, timing, and result-recording logic.
    </p>
    <p class="note-heading"><strong>QUERY WORKLOAD</strong></p>
    <p>
      The workload is deliberately designed to stress test the efficiency of the fresh-data path: queries run throughout ingestion, and their answers must account for newly arriving data rather than a fixed historical slice. Each system must therefore keep preparing fresh data for those queries while continuing to serve them.
    </p>
    <p>
      The query labels describe the data path, not whether the SQL itself contains aggregation: aggregate queries read maintained pre-aggregations; drill-down queries calculate directly from event-level rows.
    </p>
    <p class="note-subheading"><strong>How fresh arrivals enter the queries</strong></p>
    <p>
      All six queries cover the history ingested so far, without a date or time cutoff:
    </p>
    <ul>
      <li>
        <strong>Queries filtered by symbol (A1, A2, D1, D2):</strong> The selected symbols stay the same, but their matching data keeps growing as more quotes arrive. For example, sym = 'AAPL' includes newly ingested Apple quotes alongside its earlier quotes. The eight-symbol watchlist works the same way.
      </li>
      <li>
        <strong>Queries without symbol filters (A3, A4):</strong> These cover all symbols through the maintained daily pre-aggregations. Newly ingested quotes contribute to the summaries queried for historical price ranges and daily market activity.
      </li>
    </ul>
    <p>
      For aggregate queries, those incoming quotes must be incorporated into the pre-aggregations. For drill-down queries, the new event-level rows must be available in a layout that supports efficient filtering.
    </p>
    <p class="note-subheading"><strong>What each query does</strong></p>
    <p>
      <strong><a href="https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/clickhouse-cloud/queries_mv.sql">Interactive aggregate queries (A1–A4)</a></strong> read the continuously maintained daily pre-aggregation. A1 returns an all-time summary for one symbol; A2 summarizes an eight-symbol watchlist; A3 finds the largest historical price ranges by symbol; and A4 returns market-wide activity by day. A1 and A2 use the leading sym layout key, while A3 and A4 read the complete rollup.
    </p>
    <p>
      <strong><a href="https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/clickhouse-cloud/queries_raw.sql">Selective drill-down queries (D1–D2)</a></strong> read event-level data directly for one symbol across its complete history. D1 builds hourly OHLCV bars with VWAP, volatility, spread, and quote count. D2 returns a single-row risk-and-liquidity profile covering mid-price volatility, spread distribution and tail percentiles, order-book imbalance, and spread-versus-depth correlation.
    </p>
    <p class="note-subheading"><strong>How preparation matches the queries</strong></p>
    <p>
      The workload exercises both forms of preparation. D1/D2 filter the raw data by <code>sym</code>, the leading column of <code>(sym, t)</code>. A1/A2 filter the daily summaries by that same leading column in <code>(sym, day)</code>; A3/A4 read summaries across all symbols.
    </p>
    <p>
      The daily pre-aggregation groups by <code>(sym, day)</code> and maintains the counts, sums, minima, and maxima used by A1–A4. For example, total quotes comes from summing prepared quote counts, while average spread comes from dividing the accumulated spread sum by the accumulated quote count.
    </p>
    <p class="note-heading"><strong>CACHE POLICY</strong></p>
    <p>
      Query-result caching was disabled on every system so measured runtimes reflect query execution rather than retrieval of a previously computed answer. This also matches the workload’s freshness requirement: newly arriving data must contribute to the answers, so an earlier cached result may no longer be current.
    </p>
    <p>
      Ordinary underlying data caches were allowed to remain warm, reflecting continuous operation. These caches can reduce the cost of reading data, but they do not replace query execution: the engine must still account for new arrivals and perform the filtering, reconciliation, or aggregation required by each query.
    </p>
  </div>
</details>

The [full benchmark definition, accepted runs, results, cost summaries, and reproduction steps](https://github.com/ClickHouse/CostBench/tree/main/full-path-realtime/quotes) are open in the CostBench repository.

*Databricks Lakehouse/RT remains in [beta](https://docs.databricks.com/gcp/en/compute/sql-warehouse/real-time), so it is outside this first comparison and will be tested after general availability.*


## CostBench ranks systems by real-time performance per dollar

Cloud platforms pair fundamentally different billing models with often radically different fresh-data paths and query engines. To compare cost and performance across them, CostBench combines three inputs into one lower-is-better score: 


**① Fresh-data-path cost:** Complete-ingest cost for continuous ingestion, event-level layout maintenance, and pre-aggregation. 


**② Normalized query-serving cost:** Cost of executing the same scheduled queries at each system’s applicable read-side rate.

**③ Total query runtime:** Accumulated end-to-end runtime for that query workload during active ingestion.


<video autoplay="1" muted="1" loop="1" controls="0">
  <source src="https://clickhouse.com/uploads/06_costbench_end_to_end_score_loop_a41cd21cb8.mp4" type="video/mp4" />
</video>

> The score rewards systems that keep incoming data query-ready economically and serve the workload quickly. Lower is better.

Database storage costs are excluded from the score because their impact is small over the benchmark’s duration; see the calculation note below.

<details class="note-box">
  <summary>SCORE CALCULATION AND METERING NORMALIZATION (click to expand)</summary>
  <div class="note-body">
    <p class="note-heading"><strong>WHAT THE FULL-PATH SCORE MEANS</strong></p>
    <p>
      The score answers one question:<br>
      <strong>Where do you get the most full-path real-time performance per dollar spent?</strong>
    </p>
    <p>
      It combines the cost of keeping continuously arriving data query-ready with the cost and total runtime of serving the same query schedule. A lower score means a better combination of lower end-to-end cost and faster query serving under continuous ingestion.
    </p>
    <p class="note-heading"><strong>CALCULATION</strong></p>
    <p>
      End-to-end score = (fresh-data-path cost + normalized query-serving cost) × total query runtime. Lower is better.
    </p>
    <p class="note-heading"><strong>FRESH-DATA-PATH COST</strong></p>
    <p>
      The fresh-data-path component uses the complete-ingest cost of accepting the full 113.2-billion-row stream and keeping event-level and pre-aggregated data query-ready. Configured compute is priced for its observed active duration; managed and serverless services use their metered work.
    </p>
    <p class="note-heading"><strong>NORMALIZED QUERY-SERVING COST</strong></p>
    <p>
      We normalize query cost as <strong>accumulated end-to-end runtime × read-side compute price</strong>, as if compute were billed per second. <strong>This compares how much query work each system completes for the same amount of paid compute time.</strong> Per-second normalization removes differences in idle timeouts and minimum billing windows.
    </p>
    <p>
      For this benchmark, we apply that calculation to equal numbers of query executions while ingestion is running, matched by dataset progress. Each execution’s full end-to-end runtime is multiplied by the applicable read-side compute rate, and the costs are summed. The result is a normalized comparison cost rather than a reconstruction of actual bills.
    </p>
    <p class="note-heading"><strong>WHAT ABOUT STORAGE COSTS?</strong></p>
    <p>
      Database storage is excluded from the score. Earlier CostBench experiments with approximately 113.2 billion rows illustrate its limited impact over a short ingest run: the <a href="https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/snowflake/results/t2/storage.json">measured raw-table and pre-aggregation footprints</a> corresponded to approximately <strong>$9.83 per month for ClickHouse Cloud and $16.07 for Snowflake</strong>, using the benchmark’s recorded <a href="https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/clickhouse-cloud/costs/summarize_queries.sh#L43-L47">ClickHouse</a> and <a href="https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/snowflake/costs/pricings/gen2_warehouse.json">Snowflake</a> storage rates.
    </p>
    <p>
      Charging those complete footprints for an entire <strong>37-hour run</strong> would add approximately <strong>$0.50 and $0.81</strong>, respectively, using a 730-hour month. This deliberately charges the final footprint throughout, even though the dataset grows during ingestion. For context, the current comparison’s fresh-data-path costs are <strong>$28.69 and $79.42</strong>, respectively. These storage estimates illustrate scale; they are not measured storage bills for the current runs. <a href="https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/snowflake/results/t2/charts/run14/full_path_cost_performance_clickhouse_vs_snowflake_summary.json">Current cost results</a>.
    </p>
    <p>
      Storage costs become more important over longer retention periods. This exclusion concerns database storage; required ingestion infrastructure, including <a href="https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/redshift-serverless/results/t2/msk_cost.json">Redshift’s MSK broker storage</a>, remains included in the fresh-data-path cost.
    </p>
    <p class="note-heading"><strong>BOUNDARY AND EXCLUSIONS</strong></p>
    <p>
      Fresh-data-path cost covers the complete 113.2-billion-row ingest. Query-serving cost and total runtime cover matched, accepted queries during active ingestion. Storage, free tiers, discounts, idle capacity, minimum billing, post-ingestion queries, failed attempts, and standing fallback capacity are excluded. Provider-specific fallback allocations in the accepted query-cost model remain included.
    </p>
    <p class="note-heading"><strong>RANKING</strong></p>
    <p>
      The system with the lowest absolute score becomes the 1× baseline. Every other system is reported as N× worse.
    </p>
    <p class="note-heading"><strong>RELATED METHODOLOGY</strong></p>
    <p>
      This extends CostBench’s earlier <a href="https://clickhouse.com/blog/cloud-data-warehouses-cost-performance-comparison#a-note-on-metering-granularity">metering-granularity</a> and <a href="https://clickhouse.com/blog/cloud-data-warehouses-cost-performance-comparison#how-we-measure-overall-cost-performance-ranking">ranking methodology</a> from query-side tests to the complete fresh-data path.
    </p>
  </div>
</details>

## The fresh-data path widens the performance-per-dollar gap


We began with a thesis: 

> Under sustained load, keeping data query-ready can shape performance per dollar as much as query execution itself.  
 
The results now show just how large that impact can be.


### Query-side only: a 32–101× gap

 
The earlier [query-side comparison](https://clickhouse.com/blog/cloud-data-warehouses-cost-performance-comparison) measured already-loaded, query-ready data, isolating query-serving cost and runtime.

Within that boundary, Snowflake, Redshift Serverless, and BigQuery Capacity delivered **32× to 101× worse query-side cost-performance than ClickHouse.**




<video autoplay="1" muted="1" loop="1" controls="0">
  <source src="https://clickhouse.com/uploads/07_query_side_performance_per_dollar_loop_06258f79e5.mp4" type="video/mp4" />
</video>



### With the fresh-data path: a 412–1,996× gap

The end-to-end comparison adds the continuous cost of ingesting new rows and maintaining their query-ready state. The benchmark adds that cost to normalized query-serving cost and combines the total with accumulated query runtime during active ingestion.


<video autoplay="1" muted="1" loop="1" controls="0">
  <source src="https://clickhouse.com/uploads/08_end_to_end_performance_per_dollar_loop_5da8f659cf.mp4" type="video/mp4" />
</video>

The result closes the loop: 

> Once the fresh-data path is included, the performance-per-dollar gap expands from **32–101×** on the isolated query side to **412–1,996×** end to end. 


The final animation separates the two dimensions behind that wider score: end-to-end cost and accumulated query runtime.

<video autoplay="1" muted="1" loop="1" controls="0">
  <source src="https://clickhouse.com/uploads/09_end_to_end_cost_vs_accumulated_query_loop_19ce969e42.mp4" type="video/mp4" />
</video>

**ClickHouse Cloud is purpose-built end to end for fast answers on continuously fresh data** - and the yellow point shows the effect on both sides of the score:



* **Fresh-data path:** As the 1:1 analyses will show, ClickHouse Cloud had the lowest-cost fresh-data path and was the only tested system that kept both its event-level and pre-aggregated data current as ingestion continued. 

* **Query serving:** Because it completed that work as rows arrived, its query engine had less filtering, grouping, and aggregation work left to do - resulting in the lowest accumulated query runtime and the lowest normalized query-serving cost.

> **ClickHouse Cloud’s advantage compounded:** the lowest-cost fresh-data path kept data query-ready as it arrived, leaving less work - and therefore less runtime and cost - for the measured query workload.

The CostBench end-to-end real-time path series continues with 1:1 analyses of each provider’s architecture and billing model, tracing where query-readiness work happens, where it falls behind, and how those choices shape performance per dollar.
