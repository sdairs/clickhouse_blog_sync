---
title: "ClickHouse Cloud vs. Snowflake: What drives the real-time performance-per-dollar gap"
date: "2026-09-09T10:38:10.569Z"
author: "Tom Schreiber and Lionel Palacin"
category: "Engineering"
excerpt: "ClickHouse Cloud delivered 412× better performance per dollar than Snowflake in CostBench. We trace the gap from fresh data arriving to fast answers coming back."
---

# ClickHouse Cloud vs. Snowflake: What drives the real-time performance-per-dollar gap

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

In a real-time analytics system, keeping answers current and fast requires an efficient fresh-data path. [CostBench](https://clickhouse.com/blog/costbench-data-warehouse-cost-performance) compared ClickHouse Cloud and Snowflake while both ingested 113.2 billion stock-market quotes and served the same continuous query workload.

* **ClickHouse Cloud integrates ingestion, ordering, and pre-aggregation in the storage engine.** Raw data and summaries stay in sync without a separate refresh cycle, so queries inherit no unfinished preparation work.

* **Snowflake’s ingestion and pre-aggregation advance through separate services.** When preparation falls behind, current answers require additional query-time work. Its workarounds introduce trade-offs between freshness, latency, infrastructure, and cost.

* **ClickHouse Cloud delivered 412× better end-to-end real-time performance per dollar** than the tested Snowflake setup, combining a lower-cost fresh-data path with faster queries.

##  Where the 412× gap comes from

[Part 1](/blog/costbench-real-time-performance-per-dollar) showed that the [fresh-data path](/blog/costbench-real-time-performance-per-dollar#real-time-systems-must-make-fresh-data-query-ready-as-it-arrives) affects performance per dollar [twice](/blog/costbench-real-time-performance-per-dollar#an-efficient-fresh-data-path-lowers-its-own-cost---and-the-work-left-for-queries): it carries the direct cost of making new data query-ready, and it determines how much work remains for the query engine. 
 
Part 2 examines those two effects in **ClickHouse Cloud** and **Snowflake**. We ingested the same 113.2 billion stock-market quotes into both systems at 1 million rows per second, using their recommended real-time components. The same aggregate and drill-down queries ran throughout ingestion.

The diagram below shows the full measurement boundary: ingestion, ongoing [query-readiness](/blog/costbench-real-time-performance-per-dollar#what-makes-data-query-ready) work, and query serving all run together. Ordering and pre-aggregation reduce how much data queries must read and how much calculation remains. When that preparation falls behind, additional work can move into queries, increasing their latency and cost.

<video autoplay="1" muted="1" loop="1" controls="0">
  <source src="https://clickhouse.com/uploads/05_fresh_data_path_query_work_balance_loop_752d9ec108.mp4" type="video/mp4" />
</video>

That complete operating loop is the comparison boundary. Both systems received the **same stream, schema, query workload, and schedule**.  

We configured matching sorting or clustering keys across systems for both raw data and daily pre-aggregations. These layouts support the workload’s stock-symbol filters. The pre-aggregations group quotes by stock symbol and day, maintaining the counts, sums, and price minima and maxima that the aggregate queries use. Each system therefore had to keep the same preparation current for the same query workload as new rows arrived.

Query-serving compute was matched at approximately 16 CPUs, while each system retained its recommended architecture and complete metered fresh-data path.

<details class="note-box">
  <summary>BENCHMARK METHODOLOGY AND CONFIGURATION DETAILS (click to expand)</summary>
  <div class="note-body">
    <p class="note-heading"><strong>SHARED HARNESS</strong></p>
    <p>
      The same source files, schema, row-decoding logic, workload-generation code, client host (AWS EC2 m6i.8xlarge), rate controller, scheduler, timing, and result-recording logic drove both systems; only the destination-specific delivery adapter changed. <a href="/blog/costbench-real-time-performance-per-dollar#costbench-measures-both-effects-together">Full shared methodology is here.</a>
    </p>
    <p class="note-heading"><strong>REAL-TIME, NOT BULK LOAD</strong></p>
    <p>
      CostBench simulates a <a href="https://clickhouse.com/blog/selecting-a-real-time-analytical-database">real-time analytics system</a> in which fresh data is continuously generated at the source and must become query-ready as it arrives. The harness therefore models paced continuous ingestion rather than a bulk load or backfill of data that already exists.
    </p>
    <p class="note-heading"><strong>DATASET AND LAYOUT</strong></p>
    <p>
      Both systems received the same complete 113.2-billion-row <a href="https://github.com/ClickHouse/CostBench/tree/main/full-path-realtime/quotes#dataset">NBBO stock-market dataset</a>: narrow, 12-column rows.
    </p>
    <p>
      Both systems used the following sorting or clustering keys:
    </p>
    <ul>
      <li>
        <strong>Event-level data:</strong> <code>(sym, t)</code> — stock symbol and event timestamp.
      </li>
      <li>
        <strong>Daily pre-aggregations:</strong> <code>(sym, day)</code> — stock symbol and day.
      </li>
    </ul>
    <p class="note-heading"><strong>WORKLOAD AND QUERY SCHEDULE</strong></p>
    <p>
      The harness replayed the source as one continuous stream toward a target rate of <strong>1 million rows per second</strong>. From the beginning of ingestion through the final row, the same four interactive aggregate queries ran every 10 minutes and the same two selective drill-down queries every hour.
    </p>
    <p class="note-heading"><strong>RESOURCE-SIZING POLICY</strong></p>
    <p>
      We aligned query-serving compute as closely as the platforms allowed. ClickHouse Cloud used one read node with 16 CPUs and 64 GiB of memory; Snowflake used a Small Interactive Warehouse and a Gen2 Small fallback warehouse, each estimated at roughly 16 CPUs because Snowflake does not publish CPU counts. This estimate draws on <a href="https://select.dev/posts/snowflake-warehouse-sizing">SELECT.dev</a> and an <a href="https://medium.com/snowflake-engineering/deep-dive-inside-snowflakes-new-gen2-standard-warehouses-powered-by-aws-graviton3-6aacca73ae2d">independent Gen2 inspection</a>. For ingestion, ClickHouse used the smallest high-availability configuration that sustained the target during calibration-two nodes with 2 CPUs each-while Snowpipe Streaming and Interactive MV refresh ran as separately metered serverless services. Their complete metered work remains included in Snowflake’s fresh-data-path cost.
    </p>
    <p class="note-heading"><strong>THE COMPLETE FRESH-DATA PATH ON FOUR CPU CORES</strong></p>
    <p>
      The <a href="https://github.com/ClickHouse/CostBench/tree/main/full-path-realtime/quotes/clickhouse-cloud/results_t2/utilization/writer">writer-utilization results</a> show how the two-node ingest service handled continuous ingestion and background maintenance. Background <a href="https://clickhouse.com/docs/merges">merges</a> processed several million rows per second, while the maximum active-part count per partition stayed around 100. CPU usage remained around <strong>3.1 of the service’s 4 available cores</strong>, showing sustained utilization with headroom. Tracked memory usage remained within the service’s capacity.
    </p>
    <p>
      We retained two nodes for high availability, so the reported ingest cost includes <strong>both nodes of the HA deployment</strong>.
    </p>
    <p class="note-heading"><strong>BEST-PRACTICE PLATFORM CONFIGURATION</strong></p>
    <p>
      We configured each platform’s fresh-data path using its vendor-recommended low-latency components and documented best practices for keeping incoming data query-ready. Differences between those paths are part of the benchmark.
    </p>
    <p class="note-heading"><strong>RUN AND REPORTING SCOPE</strong></p>
    <p>
      For simplicity, most charts below show results through the <strong>100-billion-row milestone</strong>. The benchmark itself continued until the complete <strong>113.2-billion-row dataset</strong> had been ingested into both systems, and cost calculations cover that complete ingest.
    </p>
    <p class="note-heading"><strong>TARGET AND OBSERVED RATE</strong></p>
    <p>
      At the target rate of 1 million rows per second, ingesting 100 billion rows would take approximately 28 hours. Client-side pacing, parallel ingest streams, and batch sizing targeted-but could not guarantee-an exact end-to-end rate, and fluctuations are normal during a run lasting more than a day. Observed throughput averaged approximately <strong>0.86 million rows per second for ClickHouse</strong> and <strong>0.90 million for Snowflake</strong>. ClickHouse therefore reached 100 billion rows after roughly 32 hours and completed the 113.2-billion-row dataset after roughly 37 hours; Snowflake reached 100 billion rows after roughly 31 hours and completed the dataset after roughly 35 hours.
    </p>
  </div>
</details>

With the workload around each system held constant, the comparison now moves inside the two architectures.


## Fresh-data-path architecture

This round of [CostBench](https://clickhouse.com/blog/costbench-data-warehouse-cost-performance) used push-based ingestion: the shared client sent the same paced stream through each system’s recommended low-latency ingest path. For Snowflake, that was Snowpipe Streaming; for ClickHouse Cloud, native asynchronous inserts.

<details class="note-box">
  <summary>WHY COMPARE SNOWPIPE STREAMING WITH CLICKHOUSE ASYNCHRONOUS INSERTS? (click to expand)</summary>
  <div class="note-body">
    <p class="note-heading"><strong>THE SAME INGESTION PROBLEM</strong></p>
    <p>
      <a href="https://clickhouse.com/blog/selecting-a-real-time-analytical-database">Real-time</a> applications across <a href="https://clickhouse.com/blog/a-quadrillion-rows-across-the-three-cloud-scaling-loghouse">observability</a>, customer-facing applications, IoT, fraud detection, and analytical agents often produce small, frequent writes from many clients. The ingestion path must accept those writes continuously and combine them into efficient storage writes. Both Snowpipe Streaming and ClickHouse asynchronous inserts provide server-side buffering for this purpose.
    </p>
    <p class="note-heading"><strong>SNOWFLAKE: A MANAGED INGESTION SERVICE</strong></p>
    <p>
      <a href="https://docs.snowflake.com/en/user-guide/snowpipe-streaming/data-load-snowpipe-streaming-overview">Snowpipe Streaming lets applications submit rows</a> without managing staged files themselves. In the high-performance architecture used here, clients open channels against a <a href="https://docs.snowflake.com/en/user-guide/snowpipe-streaming/snowpipe-streaming-pipe-object">PIPE</a> object. Snowflake’s ingestion service handles buffering, schema validation, configured transformations, and optional pre-clustering before committing rows to the target table. Snowflake manages and scales the ingestion compute, with ingestion billed separately by uncompressed data volume.
    </p>
    <p class="note-heading"><strong>CLICKHOUSE: INGESTION WITHIN THE ENGINE</strong></p>
    <p>
      Applications send ordinary <code>INSERT</code> requests with <a href="https://clickhouse.com/blog/asynchronous-data-inserts-in-clickhouse">async_insert</a> enabled. Each receiving node buffers compatible requests and combines them into larger writes, with an <a href="https://clickhouse.com/blog/clickhouse-release-24-02#adaptive-asynchronous-inserts">adaptive flush timeout</a> that responds to incoming traffic. This functionality is native to both open-source ClickHouse and ClickHouse Cloud.
    </p>
    <p>
      The engine also performs ordering and transformations during ingestion. Receiving nodes sort incoming rows by each destination MergeTree-family table’s sorting key as they write data parts. Incoming data can be filtered, routed, enriched (dictionary lookups, UDFs), and reshaped on the <a href="https://github.com/ClickHouse/CostBench/tree/main/docs/clickhouse-native-ingestion">insert path</a>, before anything is stored. These operations run on the node receiving the inserts.
    </p>
    <p>
      In ClickHouse Cloud, ingestion can run on a dedicated service whose <a href="https://clickhouse.com/docs/products/cloud/features/infrastructure/warehouses">compute scales independently</a> of the services serving queries, while sharing the same stored data.
    </p>
    <p class="note-heading"><strong>RETRIES AND RECOVERY</strong></p>
    <p>
      Snowpipe Streaming’s <a href="https://docs.snowflake.com/en/user-guide/snowpipe-streaming/snowpipe-streaming-channels">offset tokens</a> record committed source progress for each channel. After a restart, the application must retrieve the last committed token, map it back to its source, and resume from the next record. Snowflake’s Kafka connector performs this mapping for Kafka partitions. For a custom application, that recovery logic belongs to the application; the offset token itself does not make resending already committed rows safe.
    </p>
    <p>
      ClickHouse supports idempotent retries through <a href="https://clickhouse.com/docs/concepts/features/operations/insert/deduplicating-inserts-on-retries">insert deduplication</a>. Retried inserts carrying the same data are detected and discarded by the server (deduplicated for synchronous and asynchronous inserts, <a href="https://clickhouse.com/blog/clickhouse-release-26-01#deduplication-of-asynchronous-inserts-with-materialized-views">including dependent materialized views</a>). After a crash or a lost acknowledgment, there's no offset bookkeeping: the client simply resends the recent batches, and ClickHouse ignores whatever already landed.
    </p>
    <p class="note-heading"><strong>WHERE CLICKPIPES FITS</strong></p>
    <p>
      <a href="https://clickhouse.com/docs/integrations/clickpipes/home">ClickPipes manages ingestion</a> from external sources such as Kafka, object storage, and Postgres. The appropriate comparison therefore depends on where the data originates:
    </p>
    <ul>
      <li>
        <strong>Applications pushing rows directly:</strong> Snowpipe Streaming and native ClickHouse asynchronous inserts - the comparison measured here.
      </li>
      <li>
        <strong>Kafka topics:</strong> Snowpipe Streaming with Snowflake’s Kafka connector and Kafka ClickPipes.
      </li>
      <li>
        <strong>Files in object storage:</strong> <a href="https://docs.snowflake.com/en/user-guide/snowpipe-streaming/data-load-snowpipe-streaming-overview#snowpipe-streaming-versus-snowpipe">classic Snowpipe</a> and Object Storage ClickPipes.
      </li>
    </ul>
    <p>
      The latter pairings compare complete integrations that consume an external source. This benchmark measures the direct application-to-table path.
    </p>
  </div>
</details>

We begin with ClickHouse Cloud and follow its [fresh-data path](/blog/costbench-real-time-performance-per-dollar#real-time-systems-must-make-fresh-data-query-ready-as-it-arrives) from incoming rows to query-ready event-level and pre-aggregated data.



<video autoplay="1" muted="1" loop="1" controls="0">
  <source src="https://clickhouse.com/uploads/02a_clickhouse_fresh_data_path_loop_f553bf54f5.mp4" type="video/mp4" />
</video>

### Ingesting the stream - ClickHouse Cloud

The benchmark used a dedicated ClickHouse Cloud ingest service with two 2-CPU nodes for high availability - the smallest HA configuration that sustained the target during calibration. The shared client sent rows through [asynchronous inserts](https://clickhouse.com/blog/asynchronous-data-inserts-in-clickhouse) built into the engine. 
 
Those same two nodes also handled sorting, incremental pre-aggregation, and background merges, running the complete [fresh-data path](https://staging.clickhouse.com/blog/costbench-real-time-performance-per-dollar#real-time-systems-must-make-fresh-data-query-ready-as-it-arrives) with **just four CPU cores in total**.


### Keeping data query-ready - ClickHouse Cloud

When **one of these two ingest nodes** flushes its asynchronous-insert buffer, it sorts the event-level rows by the target [MergeTree](https://github.com/ClickHouse/CostBench/blob/6fb94fd628b100db69bc2bf9f8d6f149eec54601/full-path-realtime/quotes/clickhouse-cloud/create.sql#L7) table’s `(sym, t)` sorting key and writes an ordered [data part](https://clickhouse.com/docs/concepts/core-concepts/parts).

In parallel, the same node executes the [incremental MV](https://github.com/ClickHouse/CostBench/blob/6fb94fd628b100db69bc2bf9f8d6f149eec54601/full-path-realtime/quotes/clickhouse-cloud/create.sql#L53)’s query over that block in memory, computes aggregate states, sorts the resulting rows by the target [AggregatingMergeTree table](https://github.com/ClickHouse/CostBench/blob/6fb94fd628b100db69bc2bf9f8d6f149eec54601/full-path-realtime/quotes/clickhouse-cloud/create.sql#L53)’s (sym, day) sorting key, and writes an ordered part containing the pre-aggregated data.

[Background merges](https://clickhouse.com/docs/concepts/core-concepts/merges) consolidate parts in both tables. Both write paths process the same flushed insert block, with ordering and pre-aggregation performed during ingestion, and no separate refresh cycle. 


> **The result: raw data and pre-aggregations stay [in sync](https://clickhouse.com/docs/resources/support-center/knowledge-base/materialized-views/are-materialized-views-inserted-asynchronously).** Both advance from the same flushed insert block; there is no separate refresh cycle between them.

We now follow the same two stages through Snowflake, where ingestion and materialized-view refresh are split across separate services.


<video autoplay="1" muted="1" loop="1" controls="0">
  <source src="https://clickhouse.com/uploads/02b_snowflake_fresh_data_path_loop_d16986cdfd.mp4" type="video/mp4" />
</video>

### Ingesting the stream - Snowflake

The benchmark used [Snowpipe Streaming’s high-performance architecture](https://docs.snowflake.com/en/user-guide/snowpipe-streaming/data-load-snowpipe-streaming-overview), which places a [managed server-side ingestion buffer](https://www.snowflake.com/en/blog/engineering/next-gen-snowpipe-streaming-architecture/) between application writes and the Interactive Table. 


### Keeping data query-ready - Snowflake

 
Snowpipe Streaming writes rows [directly](https://www.snowflake.com/en/developers/guides/interactive-tables-snowpipe-streaming-arcade-lab/) into an [Interactive Table](https://github.com/ClickHouse/CostBench/blob/254400222ce969083b67c61e51cab05a2d707df1/full-path-realtime/quotes/snowflake/t2/setup_streaming.sql#L27). With [CLUSTER_AT_INGEST_TIME=TRUE](https://docs.snowflake.com/en/user-guide/snowpipe-streaming/snowpipe-streaming-pipe-object#pre-clustering-data-during-ingestion), it pre-clusters incoming rows on the shared (sym, t) key before writing them into [micro-partitions](https://docs.snowflake.com/en/user-guide/tables-clustering-micropartitions#what-are-micro-partitions) - Snowflake’s columnar storage units. 
 
 
 
Interactive Tables carry a **storage trade-off**. In our earlier study, at roughly 113 billion rows, Snowflake’s raw Interactive Table [occupied](https://clickhouse.com/blog/real-time-analytics-cost-performance-snowflake-vs-clickhouse#storage-footprint-not-where-the-benchmark-is-decided) 2.9 TiB, compared with 701 GiB for its standard table and 362 GiB for ClickHouse’s raw table - roughly four and eight times as much storage, respectively. These measurements come from the [earlier configuration](https://clickhouse.com/blog/real-time-analytics-cost-performance-snowflake-vs-clickhouse#storage-footprint-not-where-the-benchmark-is-decided).
 
A separate Snowflake-managed [serverless service](https://docs.snowflake.com/en/user-guide/views-materialized#materialized-views-cost) refreshes the [Interactive MV](https://github.com/ClickHouse/CostBench/blob/254400222ce969083b67c61e51cab05a2d707df1/full-path-realtime/quotes/snowflake/t2/setup_streaming.sql#L71) asynchronously from that table. We configured the view with a (sym, day) clustering key, matching the sorting key of ClickHouse’s pre-aggregation table. Snowflake controls when refreshes run and how much compute they use; users cannot configure the refresh schedule or size the refresh compute. 
 


> **The result: raw data and pre-aggregations can fall out of sync.** The Interactive Table advances through ingestion, while the Interactive MV advances through a separate asynchronous refresh cycle.

<details class="note-box">
  <summary>UNDER THE HOOD: PACING BOTH SYSTEMS TOWARD 1 MILLION ROWS PER SECOND (click to expand)</summary>
  <div class="note-body">
    <p class="note-heading"><strong>SHARED CLIENT AND RATE CONTROL</strong></p>
    <p>
      Both destinations used the same Parquet source, row decoder, client-side compute, pacing logic, and eight-worker parallelism. The shared rate controller paced the stream toward 1 million rows per second. Only the delivery adapter and destination-specific batching changed.
    </p>
    <p class="note-heading"><strong>CLICKHOUSE CLOUD</strong></p>
    <p>
      The client sent <a href="https://github.com/ClickHouse/CostBench/blob/254400222ce969083b67c61e51cab05a2d707df1/full-path-realtime/quotes/clickhouse-cloud/_commands.txt#L60">3,000-row batches</a> through asynchronous inserts. Each receiving node accumulated these requests in its server-side buffer.
    </p>
    <p>
      The benchmark retained the <a href="https://clickhouse.com/blog/asynchronous-data-inserts-in-clickhouse">default buffering settings</a> used for the run. A flush occurred when the first of three thresholds was reached: 100 MiB buffered, an adaptive timeout between 50 milliseconds and 1 second, or 450 queued insert queries.
    </p>
    <p class="note-heading"><strong>SNOWFLAKE</strong></p>
    <p>
      The client called <code>append_row</code> through one Snowpipe Streaming channel per worker. The SDK selected <a href="https://www.snowflake.com/en/blog/engineering/next-gen-snowpipe-streaming-architecture/">file mode</a> and grouped those row-wise calls into client-side <a href="https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/snowflake/results/t2/stream_preview.log">NDJSON batches averaging approximately 61,500 rows</a>.
    </p>
    <p>
      Across eight channels, this produced about <a href="https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/snowflake/results/t2/stream_preview.log">14.6 file uploads per second</a>. <a href="https://docs.snowflake.com/en/user-guide/snowpipe-streaming/data-load-snowpipe-streaming-overview">Snowpipe Streaming then buffered the uploaded batches again server-side</a> before committing their rows.
    </p>
    <p class="note-heading"><strong>HOW TO READ THESE BATCH SIZES</strong></p>
    <p>
      The 3,000-row and approximately 61,500-row figures describe client-side delivery batches. Both systems performed further server-side buffering, so neither figure directly specifies the size of a final storage write.
    </p>
  </div>
</details>


## Query-serving architecture

Those different query-ready states are what the read side receives. ClickHouse Cloud serves both workloads from one 16-CPU read service; Snowflake uses an approximately matched Small Interactive Warehouse, with separate compilation and fallback behavior around it.




<video autoplay="1" muted="1" loop="1" controls="0">
  <source src="https://clickhouse.com/uploads/03a_clickhouse_query_serving_loop_d462250c34.mp4" type="video/mp4" />
</video>

### Read-side compute - ClickHouse Cloud

**Sizing:** The read service used one node with 16 CPUs and 64 GiB of memory, matching the estimated CPU count of Snowflake’s Small warehouse.

**Serving model:** That single service handled both workloads. Aggregate queries read the [always-current](https://clickhouse.com/docs/resources/support-center/knowledge-base/materialized-views/are-materialized-views-inserted-asynchronously) [AggregatingMergeTree table](https://github.com/ClickHouse/CostBench/blob/6fb94fd628b100db69bc2bf9f8d6f149eec54601/full-path-realtime/quotes/clickhouse-cloud/create.sql#L53), which advances with the same flushed insert blocks as the [raw MergeTree table](https://github.com/ClickHouse/CostBench/blob/6fb94fd628b100db69bc2bf9f8d6f149eec54601/full-path-realtime/quotes/clickhouse-cloud/create.sql#L7); current answers therefore require no query-time reconciliation. Drill-down queries read the [event-level MergeTree table](https://github.com/ClickHouse/CostBench/blob/6fb94fd628b100db69bc2bf9f8d6f149eec54601/full-path-realtime/quotes/clickhouse-cloud/create.sql#L7).

The same paths run through Snowflake’s serving layer, which adds compilation and fallback behavior around the Interactive Warehouse.



<video autoplay="1" muted="1" loop="1" controls="0">
  <source src="https://clickhouse.com/uploads/03b_snowflake_query_serving_loop_761e0521ec.mp4" type="video/mp4" />
</video>

### Read-side compute - Snowflake

**Sizing:** Snowflake does not publish the warehouse’s CPU or memory. We estimate the Small Interactive Warehouse at approximately 16 CPUs - matching ClickHouse Cloud’s 16-CPU read service - using [SELECT.dev](https://select.dev/posts/snowflake-warehouse-sizing) and an [independent Gen2 inspection](https://medium.com/snowflake-engineering/deep-dive-inside-snowflakes-new-gen2-standard-warehouses-powered-by-aws-graviton3-6aacca73ae2d); Snowflake documents an [approximately 600 GB](https://docs.snowflake.com/en/user-guide/interactive#choosing-a-size-for-an-interactive-warehouse) [local SSD](https://medium.com/snowflake/cost-effective-performance-with-snowflake-interactive-warehouses-3892ede05f4c) cache for this size.

**Serving model:** The [Interactive Warehouse](https://docs.snowflake.com/en/user-guide/interactive) was the primary service for both workloads. Aggregate queries targeted the [Interactive MV](https://github.com/ClickHouse/CostBench/blob/254400222ce969083b67c61e51cab05a2d707df1/full-path-realtime/quotes/snowflake/t2/setup_streaming.sql#L71). As discussed above, Snowflake [refreshed that view asynchronously](https://docs.snowflake.com/en/user-guide/views-materialized#understanding-how-materialized-views-are-maintained), so it could lag the [Interactive Table](https://github.com/ClickHouse/CostBench/blob/254400222ce969083b67c61e51cab05a2d707df1/full-path-realtime/quotes/snowflake/t2/setup_streaming.sql#L27). To return current results, Snowflake reconciles the unrefreshed base-table delta during [query compilation](https://community.snowflake.com/s/article/Understanding-Why-Compilation-Time-in-Snowflake-Can-Be-Higher-than-Execution-Time) in its [Cloud Services layer](https://docs.snowflake.com/en/user-guide/intro-key-concepts#cloud-services), before execution reaches the warehouse. Drill-down queries read the [Interactive Table](https://github.com/ClickHouse/CostBench/blob/254400222ce969083b67c61e51cab05a2d707df1/full-path-realtime/quotes/snowflake/t2/setup_streaming.sql#L27) directly.

**Timeout and fallback:** Interactive Warehouses [cancel queries that exceed five seconds](https://docs.snowflake.com/en/user-guide/interactive#automatically-handling-statement-timeouts), and that limit can only be lowered. We configured a separate Gen2 Small standard warehouse-also estimated at 16 CPUs-to receive eligible timed-out queries through Snowflake’s [automatic fallback mechanism](https://docs.snowflake.com/en/user-guide/interactive#automatically-handling-statement-timeouts).


## Did query readiness keep pace with ingestion?

Both systems kept their event-level tables advancing with the continuously paced stream. The difference appeared in pre-aggregation: ClickHouse kept its event-level and pre-aggregated data current together; Snowflake did not.

The chart tracks the gap between each system’s event-level and pre-aggregated data as the event-level table grows; lower is fresher.

![04_pre_aggregation_lag.png](https://clickhouse.com/uploads/04_pre_aggregation_lag_412c3b71e5.png)

**ClickHouse Cloud:** The incremental MV processed every flushed insert block as part of the insert, so the raw MergeTree and pre-aggregated AggregatingMergeTree advanced together with zero raw-to-pre-aggregated lag throughout.

**Snowflake:** Snowpipe Streaming kept the Interactive Table advancing, but the separate serverless refresh left the Interactive MV behind. Its active-ingestion trend averaged 1.4 minutes of lag and peaked at 2.0 minutes, so current aggregate answers required query-time reconciliation.

<details class="note-box">
  <summary>MEASUREMENT DETAILS: FRESHNESS (click to expand)</summary>
  <div class="note-body">
    <p class="note-heading"><strong>SNOWFLAKE LAG SERIES</strong></p>
    <p>
      The <a href="https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/snowflake/results/t2/charts/run14/mv_lag_clickhouse_vs_snowflake_wide_summary.json">MV-lag series</a> uses 2,072 active one-minute <a href="https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/snowflake/results/t2/mv_latency_20260811T111856Z.jsonl"><code>behind_by</code></a> samples. Poll timestamps were aligned to raw row count by linear interpolation between 208 active dashboard observations.
    </p>
    <p>
      Legend statistics come from a centered 61-sample rolling mean; the displayed curve adds an 11-sample centered rolling mean and shape-preserving interpolation. The resulting 1.372-minute average and 2.033-minute maximum are shown above as 1.4 and 2.0 minutes.
    </p>
    <p class="note-heading"><strong>CLICKHOUSE BASELINE</strong></p>
    <p>
      ClickHouse’s zero line is a benchmark-semantic baseline rather than a separately polled provider metric. The raw table and <a href="https://clickhouse.com/docs/resources/support-center/knowledge-base/materialized-views/are-materialized-views-inserted-asynchronously">incremental MV</a> consume the same flushed insert block, so there is no independent refresh interval between them.
    </p>
  </div>
</details>





---

## 412× better real-time performance per dollar

That’s what ClickHouse Cloud delivered compared with Snowflake in CostBench under continuous load. See what it can do for your data - sign up today.

[Try ClickHouse Cloud](https://console.clickhouse.cloud/signUp?loc=blog-cta-1866-412-better-real-time-performance-per-dollar-try-clickhouse-cloud&utm_blogctaid=1866)

---

## What happened when query readiness fell behind?

Snowflake’s pre-aggregation lag moved unfinished fresh-data-path work onto the read path. Aggregate queries inherited that work through reconciliation; drill-down queries exposed a separate event-level scaling path. 
 
All query-performance comparisons below use approximately matched 16-CPU read-side configurations: one 16-CPU ClickHouse Cloud read node and Snowflake Small warehouses estimated at approximately 16 CPUs.

<details class="note-box">
  <summary>MEASUREMENT DETAILS: HOW QUERY RESULTS WERE COMPARED (click to expand)</summary>
  <div class="note-body">
    <p>
      See Part 1 for the complete query definitions and how newly ingested data contributes to their results: <a href="/blog/costbench-real-time-performance-per-dollar">Measuring real-time performance per dollar under continuous load: CostBench’s first end-to-end results</a>.
    </p>
    <p class="note-heading"><strong>CACHE POLICY</strong></p>
    <p>
      Query-result caching was disabled on both systems, so every measured query executed. Their underlying data caches were allowed to remain warm; a warm data cache still requires the query itself to run.
    </p>
    <p class="note-heading"><strong>END-TO-END LATENCY</strong></p>
    <p>
      The measured latency is the full client-visible runtime. Snowflake’s compilation and execution phases are retained as supporting telemetry, but neither phase is subtracted from the end-to-end result.
    </p>
    <p class="note-heading"><strong>VISIBLE CURVES</strong></p>
    <p>
      The charts show results through the 100-billion-row milestone against each system’s own observed row counts, without matching by iteration or interpolating between systems.
    </p>
    <p>
      The <a href="https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/snowflake/results/t2/charts/run14/aggregate_query_latency_clickhouse_vs_snowflake_wide_summary.json">aggregate chart</a> uses a seven-observation centered rolling median and a Snowflake-only Tukey upper-fence rule; excluded points remain in its source data and summary. The <a href="https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/snowflake/results/t2/charts/run14/drilldown_query_latency_clickhouse_vs_snowflake_wide_summary.json">drill-down chart</a> uses a five-observation centered rolling median and no outlier filter.
    </p>
    <p class="note-heading"><strong>ACCUMULATED TOTALS</strong></p>
    <p>
      Runtime and normalized query cost use the accepted <a href="https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/snowflake/results/t2/charts/run14/full_path_cost_performance_clickhouse_vs_snowflake_wide_summary.json">row-count-matched active-ingestion sets</a>: 209 four-query aggregate batches and 35 two-query drill-down batches per system. The first complete-dataset observation remains part of active ingestion; later post-ingestion observations are excluded.
    </p>
  </div>
</details>

###  Aggregate queries over pre-aggregated data

Every 10 minutes during active ingestion, the benchmark ran four aggregate queries ([A1-A4](https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/clickhouse-cloud/queries_mv.sql)) against the maintained daily pre-aggregations. These summaries already contain the counts, sums, and price minima and maxima needed to calculate stock-market activity across the history ingested so far. The queries combine those prepared results across days or stocks. Their answers must include newly arrived quotes, so any lag in the pre-aggregations leaves work for the query engine. A1 and A2 also filter by stock symbol - the leading sorting or clustering column - so they can skip summaries for other stocks. 

The chart follows the query’s latency as the event-level table grows. The orange dashed line marks Snowflake’s five-second retry threshold. Blue shows the Interactive Warehouse path; purple shows executions that crossed the threshold and were attributed to the Gen2 Small fallback path. ClickHouse appears in yellow.

![05_aggregate_query_latency.png](https://clickhouse.com/uploads/05_aggregate_query_latency_5f5867cf30.png)


**ClickHouse Cloud:** Through the 100-billion-row chart window, aggregate-query latency was:

* **13 ms median** - 801× faster than Snowflake
* **42 ms P99** - 533× faster than Snowflake
* **111 ms maximum** - 218× faster than Snowflake

Its incremental MV kept the aggregate states current as part of the insert path, so queries required no reconciliation. Across [209 row-count-matched active-ingestion batches](https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/snowflake/results/t2/charts/run14/aggregate_query_latency_clickhouse_vs_snowflake_wide_summary.json), accumulated runtime was **11.36 seconds**.

**Snowflake:** Through the same chart window, aggregate-query latency was:

* **10.41 s median** - 801× slower than ClickHouse Cloud
* **22.20 s P99** - 533× slower than ClickHouse Cloud
* **24.17 s maximum** - 218× slower than ClickHouse Cloud

Queries reconciled the lagging Interactive MV with newer rows from the Interactive Table, producing the sawtooth pattern as the delta grew and refreshes reduced it. Across the same 209 matched batches, accumulated runtime was **2.11 hours**; under the accepted five-second fallback proxy, **[477 of 836 executions-57%](https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/snowflake/costs/out/t2/run14/dashboard.json)**, crossed the threshold and were attributed to the fallback path.

> **Across the interactive aggregate-query workload, ClickHouse Cloud was 669× faster than Snowflake** and kept its pre-aggregated data current without query-time reconciliation. 
 



#### Unfinished refresh work reappeared during query compilation

The phase breakdown below separates Snowflake’s end-to-end aggregate-query latency into compilation and execution.

![06_aggregate_query_compilation_breakdown.png](https://clickhouse.com/uploads/06_aggregate_query_compilation_breakdown_aee5cfe63d.png)

Snowflake’s phase telemetry attributes 85% of aggregate-query time to compilation and 15% to warehouse execution. A larger warehouse can accelerate execution, but it cannot reduce the compilation time dominating this chart. 
 
> You can’t buy your way out of the orange compilation area - only the thin blue execution band.

The diagram below shows why.



<video autoplay="1" muted="1" loop="1" controls="0">
  <source src="https://clickhouse.com/uploads/07_snowflake_compilation_bottleneck_loop_c5257ba29b.mp4" type="video/mp4" />
</video>

① An aggregate query targets the Interactive MV using the Interactive Warehouse. Although the view is behind, the query must still return current results, including rows that arrived after its last refresh.

② During **query compilation**, Snowflake’s [planner](https://arxiv.org/pdf/2504.11540) determines how to combine the materialized view with those newer rows. To do that, it loads metadata for every base-table micro-partition created since the last refresh. This compilation occurs in Snowflake’s shared **[Cloud Services layer](https://docs.snowflake.com/en/user-guide/intro-key-concepts#cloud-services)** before execution begins in the warehouse.

Snowflake manages the resources for this compilation work; users cannot resize them. Increasing warehouse size adds resources to the later execution phase.

As new micro-partitions accumulate between refreshes, each query has more metadata to process during compilation. When a refresh catches up, that work shrinks and latency drops, then begins climbing again as ingestion continues.

> **The paradox: faster Snowpipe Streaming makes current MV queries slower.**<br/>More new micro-partitions accumulate between asynchronous refreshes, so every query inherits more reconciliation work.

<details class="note-box">
  <summary>UNDER THE HOOD: RECONCILIATION, WAREHOUSE SIZE, AND FALLBACK (click to expand)</summary>
  <div class="note-body">
    <p class="note-heading"><strong>1. Two query phases</strong></p>
    <p>
      Every Snowflake aggregate query first compiles in <a href="https://docs.snowflake.com/en/user-guide/intro-key-concepts#cloud-services">shared Cloud Services</a>, independently of the warehouse, and then executes on the selected warehouse.
    </p>
    <p class="note-heading"><strong>2. How Snowflake assembles a current MV answer</strong></p>
    <p>
      When the Interactive MV is behind, Snowflake does not return stale results. During compilation, the planner reconciles the view with everything added to the Interactive Table since the last refresh, loading metadata for each new base-table micro-partition in that delta.
    </p>
    <p class="note-heading"><strong>3. Why latency rises and then resets</strong></p>
    <p>
      Snowpipe Streaming keeps creating micro-partitions while the serverless MV refresh runs asynchronously. The unrefreshed delta grows between refreshes and shrinks when a refresh catches up, producing the same rising-and-reset pattern visible in the latency curves.
    </p>
    <p class="note-heading"><strong>4. What we measured</strong></p>
    <p>
      Compilation accounted for 85% of Snowflake’s aggregate-query time; warehouse execution accounted for 15%. Under the accepted five-second fallback proxy, <a href="https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/snowflake/costs/out/t2/run14/dashboard.json">477 of 836 executions-57%</a>-crossed into the fallback-attributed path.
    </p>
    <p class="note-heading"><strong>5. Why a larger or fallback warehouse does not remove the bottleneck</strong></p>
    <p>
      Warehouse size changes only execution compute. Reconciliation has already happened in shared Cloud Services before execution reaches either the Interactive Warehouse or the Gen2 Small fallback.
    </p>
    <p class="note-heading"><strong>6. Earlier diagnostic evidence for the mechanism</strong></p>
    <p>
      In one profiled query, remote micro-partition metadata I/O consumed 4,908 ms of a 5,030 ms compilation phase-97.6%, or roughly 25 ms per partition. A parallel Small-versus-X-Large diagnostic over approximately 0.4–16.8 billion raw rows found no compilation-time improvement even though X-Large carried an 8× credit rate. These diagnostics explain the mechanism; Run14 supplies the headline measurements above.
    </p>
    <p class="note-heading"><strong>7. Cost implication</strong></p>
    <p>
      The warehouse can remain active and billable while waiting for compilation, while <a href="https://docs.snowflake.com/en/user-guide/cost-understanding-compute#cloud-service-credit-usage">Cloud Services usage can itself become billable</a> when daily Cloud Services consumption exceeds 10% of daily warehouse usage. Faster ingestion therefore increases both the reconciliation latency and its potential cost.
    </p>
    <p class="note-heading"><strong>8. How to read the fallback colors</strong></p>
    <p>
      The purple segment is an accepted elapsed-time proxy for normalized cost, not query-level proof that Snowflake physically executed on fallback. Jobs above five seconds are fallback-priced for their full end-to-end runtime; jobs at or below five seconds remain Interactive-priced. Each job enters exactly one bucket.
    </p>
    <p>
      Because the threshold is a classifier, it can miss fallback that occurred at or below five seconds; the later score box documents the complete pricing boundary.
    </p>
  </div>
</details>


###  Drill-down queries over event-level data

Every hour during active ingestion, the benchmark ran two drill-down queries ([D1-D2](https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/clickhouse-cloud/queries_raw.sql)) directly against the event-level tables. They calculate hourly price summaries and a risk-and-liquidity profile for one stock across its growing history. Their answers must include newly arrived quotes, so the event-level tables must keep new rows queryable in a layout that supports efficient filtering. Both queries filter by stock symbol - the leading column of the tables’ sorting or clustering key.

The chart follows their end-to-end latency as each event-level table grows; Snowflake appears in blue and ClickHouse in yellow.



![08_drill_down_query_latency.png](https://clickhouse.com/uploads/08_drill_down_query_latency_d345e5a2ff.png)

These queries bypassed the MV and read each event-level table directly, so this path isolates event-level layout and serving rather than MV reconciliation. Both systems used the same (sym, t) ordering/clustering and approximately 16 CPUs of read-side compute; Snowflake’s Small Interactive Warehouse additionally provided an approximately [600 GB local SSD cache](https://docs.snowflake.com/en/user-guide/interactive#choosing-a-size-for-an-interactive-warehouse).

**ClickHouse Cloud:** Through the 100-billion-row chart window, drill-down latency was:



* **722.5 ms median** - 1.38× faster than Snowflake
* **1.15 s P99** - 2.06× faster than Snowflake
* **1.18 s maximum** - 2.17× faster than Snowflake

Across [35 row-count-matched active-ingestion batches](https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/snowflake/results/t2/charts/run14/drilldown_query_latency_clickhouse_vs_snowflake_wide_summary.json), accumulated runtime was **50.47 seconds**. The ordered MergeTree path’s latency increased more gradually and remained lower at larger data volumes.

**Snowflake:** Through the same chart window, drill-down latency was:



* **993.5 ms median** - 1.38× slower than ClickHouse Cloud
* **2.37 s P99** - 2.06× slower than ClickHouse Cloud
* **2.56 s maximum** - 2.17× slower than ClickHouse Cloud

Across the same 35 matched batches, accumulated runtime was **74.81 seconds**. Despite the Interactive Warehouse’s approximately 600 GB local SSD cache, latency rose more steeply as data accumulated; **[all 70 executions remained below the five-second fallback threshold](https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/snowflake/costs/out/t2/run14/drilldown.json)**.

> **Across the matched drill-down workload, ClickHouse Cloud was 1.48× faster overall**, despite Snowflake’s approximately 600 GB local SSD cache.


#### A growing event-level table left more work for query execution

The phase breakdown below separates Snowflake’s drill-down latency into compilation and execution.

![09_drill_down_compilation_execution_breakdown.png](https://clickhouse.com/uploads/09_drill_down_compilation_execution_breakdown_33271ac5b9.png)

Snowflake’s phase telemetry shows a different bottleneck from its MV path. At the median, compilation took **225 ms** for D1 and **191 ms** for D2; execution took **643 ms** and **830 ms**, respectively-**74–81%** of provider-reported phase time. That execution work grew as the Interactive Warehouse read and filtered the expanding event-level table. Unlike MV reconciliation, it runs inside the warehouse and can be reduced with more warehouse compute.

> **The dominant drill-down layer is execution: buying a larger warehouse can reduce it.** The separate compilation layer remains outside the warehouse.

<details class="note-box">
  <summary>DEEP DIVE: THE CACHE KEPT UP. HOW DOES THIS SCALE? (click to expand)</summary>
  <div class="note-body">
    <p class="note-heading"><strong>Measured case</strong></p>
    <p>
      Snowflake documents <a href="https://docs.snowflake.com/en/user-guide/interactive#adding-an-interactive-table-to-an-interactive-warehouse">Interactive Warehouse cache warming</a> as a non-blocking background process. In an earlier diagnostic run of this workload, <a href="https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/snowflake/results/t2/query_stats_drilldowns.csv">query profiles</a> reported zero or negligible remote reads during active ingestion and a median 100% of bytes served from cache.
    </p>
    <p>
      At roughly 75 MB/s of ingest, the queried working set fit inside the Small warehouse’s approximately <a href="https://docs.snowflake.com/en/user-guide/interactive#choosing-a-size-for-an-interactive-warehouse">600 GB cache</a>, and warming kept the relevant data local. These diagnostics explain the cache behavior; Run14 supplies the headline latency measurements above.
    </p>
    <p class="note-heading"><strong>What that establishes</strong></p>
    <p>
      This was the favorable cache case: the working set fit and warming kept pace. The remaining latency came primarily from executing scans and filters over the growing event-level table, not from repeatedly fetching the working set from remote storage.
    </p>
    <p class="note-heading"><strong>Boundary 1: working-set capacity</strong></p>
    <p>
      Even the largest Interactive Warehouse-a 4X-Large-has a finite <a href="https://docs.snowflake.com/en/user-guide/interactive#choosing-a-size-for-an-interactive-warehouse">44 TB cache</a>. When a query’s working set outgrows the cache, more reads go remote. <strong>Undersize the warehouse and latency rises toward the five-second cap, sending queries that cross it to fallback; oversize it and you pay for cache you do not need.</strong>
    </p>
    <p class="note-heading"><strong>Boundary 2: warming throughput</strong></p>
    <p>
      Snowflake documents cache-warming throughput of roughly <a href="https://docs.snowflake.com/en/user-guide/interactive#resuming-and-suspending-an-interactive-warehouse">300–400 MB/s even for an X-Small warehouse</a>, and says larger warehouses warm faster. That documented X-Small rate was comfortably above this benchmark’s roughly 75 MB/s ingest rate.
    </p>
    <p>
      At higher source rates, however, query-relevant data can arrive faster than warming makes it local: the total working set may still fit while the newest rows require remote reads.
    </p>
    <p class="note-heading"><strong>Sizing implication</strong></p>
    <p>
      Snowflake customers must size the Interactive Warehouse for both how much data their queries touch and how quickly new data arrives. ClickHouse queries run directly against the ordered MergeTree table, without a separately populated serving cache to size or keep warm.
    </p>
  </div>
</details>

### Bypassing the MV moved aggregation onto the raw table

That event-level path also provides a useful control:

What happens if Snowflake’s aggregate queries bypass the lagging MV and run directly against the raw Interactive Table? 

The chart compares that path with ClickHouse’s pre-aggregated path. As in the earlier aggregate chart, the orange dashed line marks Snowflake’s five-second retry threshold. Blue shows the Interactive Warehouse path; purple shows executions that crossed the threshold and were attributed to the Gen2 Small fallback path. ClickHouse appears in yellow. The same approximately matched 16-CPU read-side sizing applies.

![10_raw_table_aggregate_latency.png](https://clickhouse.com/uploads/10_raw_table_aggregate_latency_066af5e58e.png)

**ClickHouse Cloud:** Same pre-aggregated path and results as above.

**Snowflake:** Bypassing the Interactive MV and querying the raw Interactive Table produced:

| Metric | Raw-table latency | vs. Interactive MV | vs. ClickHouse Cloud |
| --- | --- | --- | --- |
| Median | 2.47 s | 4.21× faster | 190× slower |
| P99 | 18.04 s | 1.23× faster | 433× slower |
| Maximum | 20.67 s | 1.17× faster | 186× slower |

Bypassing the lagging Interactive MV removed query-time reconciliation, but it left the aggregation work on Snowflake’s raw table. **A1 and A2** filter on sym-the leading clustering-key column - yet both show a clear latency uptrend as the Interactive Table grows. Within the measured window, more ingested data increased query-time work even on these selective paths. **ClickHouse Cloud’s pre-aggregated latency remained effectively flat across the same 100-billion-row window.**

**A3 and A4** are unfiltered full-table aggregates. Under the accepted five-second fallback proxy, **[220 of 836 executions-26%](https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/snowflake/costs/out/t2/run14/dashboard_raw_iv.json)** crossed the threshold and were attributed to the fallback path: **103 A3 executions** and **117 A4 executions**. Across the same 209 matched batches, Snowflake’s raw-table path accumulated **1.10 hours** of runtime.

**Bypassing the lagging Interactive MV made Snowflake faster by removing query-time reconciliation**-but it shifted aggregation onto the raw table. **ClickHouse Cloud’s already-current pre-aggregated path was still 347× faster across the matched workload.**

> **Across Snowflake’s two aggregate paths, unfinished fresh-data-path work reappeared at query time:**<br/><br/>• **Interactive MV:** reconciliation during **query compilation** accounts for rows missing from the pre-aggregations.<br/><br/>• **Raw Interactive Table:** scans and aggregation during **query execution** calculate the answers directly from event-level rows.<br/><br/>**ClickHouse Cloud performed the pre-aggregation during ingestion**, keeping current summaries ready for queries.





That leaves one final architectural question: can Snowflake store current pre-aggregations in a form that is fast to query?


## Why Snowflake’s query-ready path forces a freshness-latency trade-off

The two aggregate tests reveal a structural choice. Querying the Interactive MV returns current results, but Snowflake must reconcile its unrefreshed delta during compilation. Querying the raw Interactive Table avoids that reconciliation, but also removes pre-aggregation and shifts the work into scans and aggregation over a growing table.


### The obvious composition is not supported

The obvious alternative would be to store the pre-aggregated result in an auto-refreshed Interactive Table, turning aggregate queries into ordinary table reads. That would serve asynchronously refreshed results, with a minimum supported target lag of[ one minute](https://docs.snowflake.com/en/user-guide/interactive#specifying-auto-refresh-for-an-interactive-table).

Even with that freshness trade-off, the direct composition is unsupported: Snowpipe Streaming’s high-performance path lands the raw data in an Interactive Table, and Snowflake [does not support](https://docs.snowflake.com/en/user-guide/interactive#limitations-of-interactive-tables) using one Interactive Table as the auto-refresh source for another.







<video autoplay="1" muted="1" loop="1" controls="0">
  <source src="https://clickhouse.com/uploads/11_snowflake_unsupported_composition_loop_4afc68290e.mp4" type="video/mp4" />
</video>

> The component that accepts the stream cannot feed the component that keeps pre-aggregations fast.


### The supported route is a detour

The supported route lands the stream in a standard table first, then uses a refresh warehouse to maintain separate raw and pre-aggregated Interactive Tables. That adds another copy of the raw data and dedicated refresh compute. The same [one-minute](https://docs.snowflake.com/en/user-guide/interactive#specifying-auto-refresh-for-an-interactive-table) minimum target lag still applies. 



<video autoplay="1" muted="1" loop="1" controls="0">
  <source src="https://clickhouse.com/uploads/12_snowflake_supported_standard_table_detour_loop_8cc3928b2c.mp4" type="video/mp4" />
</video>

The table below is an approximate scope bridge, not a literal three-way rerun: the first two rows reuse this post’s [results](https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/snowflake/results/t2/charts/run14/aggregate_query_latency_clickhouse_vs_snowflake_wide_summary.json), while the supported-detour row summarizes the [earlier  study](https://clickhouse.com/blog/real-time-analytics-cost-performance-snowflake-vs-clickhouse#user-content-snowflake_setup_2_interactive_tables) through 100 billion rows. All three paths use approximately 16 CPUs of read-side compute; the supported detour additionally [requires](https://clickhouse.com/blog/real-time-analytics-cost-performance-snowflake-vs-clickhouse#user-content-freshness_scheduled_refresh_has_to_keep_up) the separate 128-CPU Gen2 X-Large refresh warehouse shown above.

**Aggregate-query latency and freshness during ingestion**

| fresh-data path | Median query latency | P99 query latency | Maximum query latency | Result state / refresh overhead |
| --- | --- | --- | --- | --- |
| ClickHouse Cloud · incremental MV | 13 ms | 42 ms | 111 ms | Current by design |
| Snowflake · Interactive MV | 10.41 s | 22.20 s | 24.17 s | Current via query-time reconciliation |
| Snowflake · supported detour (prior study) | 173 ms | 557 ms | 925 ms | Not continuously current: 1-minute minimum target lag; +$1,814.40 refresh warehouse through 100B rows |

**At the median, the supported detour was roughly 60× faster than Snowflake’s Interactive MV, but still roughly 13× slower than ClickHouse Cloud.** It also [adds](https://clickhouse.com/blog/real-time-analytics-cost-performance-snowflake-vs-clickhouse#user-content-freshness_scheduled_refresh_has_to_keep_up) **$1,814.40** of refresh-warehouse cost through 100 billion rows; by comparison, ClickHouse Cloud’s complete fresh-data path shown below cost **$28.69** through the full 113.2-billion-row ingest.

> **Snowflake’s trade-off: up-to-date answers or consistently fast aggregate queries.**<br/><br/>• **Interactive MV:** up-to-date answers, but reconciliation slowed query compilation.<br/><br/>• **Raw Interactive Table:** up-to-date answers, but each query had to scan and aggregate the growing raw data.<br/><br/>• **Supported detour:** fast queries, but over asynchronously refreshed pre-aggregations, with a separate refresh warehouse and a one-minute minimum target lag.<br/><br/>**ClickHouse Cloud delivered both:** current pre-aggregations and fast aggregate queries, with the preparation performed during ingestion.






<details class="note-box">
  <summary>WHAT DID THE SUPPORTED DETOUR REQUIRE? (click to expand)</summary>
  <div class="note-body">
    <p class="note-heading"><strong>RESULT CONTRACT</strong></p>
    <p>
      The supported detour serves an asynchronously refreshed pre-aggregated table instead of reconciling to a current result at query time. Its minimum supported target lag is one minute.
    </p>
    <p class="note-heading"><strong>REFRESH CAPACITY AND COST</strong></p>
    <p>
      The modeled 100-billion-row setup ran a <strong>Gen2 X-Large</strong> refresh warehouse continuously for 28 hours, adding <strong><a href="https://clickhouse.com/blog/real-time-analytics-cost-performance-snowflake-vs-clickhouse#user-content-dashboard_queries_faster_with_interactive_tables_but_still_not_as_flat">$1,814.40</a></strong> at Enterprise list price (21.6 credits/hour × 28 hours × $3/credit).
    </p>
    <p class="note-heading"><strong>SMALLER WAREHOUSES</strong></p>
    <p>
      Gen2 Small, Medium, and Large lost the one-minute target after roughly <strong>3, 8, and 15 hours</strong>. The X-Large held it for the <strong>first 24 hours</strong>, but its lag was still trending upward.
    </p>
  </div>
</details>

One final scope note: the score below covers the architecture tested in this post-Snowpipe Streaming into an Interactive Table, with pre-aggregations maintained in an Interactive MV. The supported standard-table detour above is not part of this comparison; we benchmarked its cost and performance in our [previous post](https://clickhouse.com/blog/real-time-analytics-cost-performance-snowflake-vs-clickhouse#user-content-snowflake_setup_2_interactive_tables). 



## The final result: real-time performance per dollar

Part 1 defines the CostBench scoring model in full. In short, CostBench adds the cost of keeping the dataset query-ready to the normalized cost of serving the query workload, then multiplies that combined cost by the workload’s accumulated end-to-end runtime. Lower is better. 






<video autoplay="1" muted="1" loop="1" controls="0">
  <source src="https://clickhouse.com/uploads/13_costbench_end_to_end_score_loop_88f48a4231.mp4" type="video/mp4" />
</video>

### Snowflake’s end-to-end score was 412× worse

The visual below shows the three score inputs and the final 412× result. Expand the pricing details for the source data, full formulas, matching boundary, and Snowflake fallback assumptions.

The score retains the same approximately matched 16-CPU query-serving basis: ClickHouse Cloud used one 16-CPU read node, while Snowflake’s Small query warehouses are estimated at approximately 16 CPUs. It separately includes each system’s complete fresh-data-path cost.

<details class="note-box">
  <summary>END-TO-END SCORE: PRICING, FORMULAS, AND CALCULATION BOUNDARY (click to expand)</summary>
  <div class="note-body">
    <p class="note-heading"><strong>PRICING BASIS</strong></p>
    <p>
      Enterprise pricing in AWS us-east is $3 per Snowflake <a href="https://clickhouse.com/blog/how-cloud-data-warehouses-bill-you">credit</a> and $0.3903 per ClickHouse Cloud <a href="https://clickhouse.com/blog/how-cloud-data-warehouses-bill-you">compute unit (CU)</a> per hour. Snowflake serverless charges come directly from its metering history.
    </p>
    <p class="note-heading"><strong>① FRESH-DATA-PATH COST</strong></p>
    <p>
      This covers the complete 113.2-billion-row ingest.
    </p>
    <p class="note-subheading"><strong>ClickHouse Cloud</strong></p>
    <p>
      <strong><a href="https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/clickhouse-cloud/costs/out_t2/ingest.json">2 CUs</a></strong> × 36.75 hours × $0.3903/CU-hour = $28.68705.
    </p>
    <p class="note-subheading"><strong>Snowflake</strong></p>
    <p>
      <a href="https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/snowflake/costs/out/t2/run14/snowpipe_streaming.json"><strong>Snowpipe Streaming</strong> processed</a> 4.6762 TiB and was metered at 17.71783 credits using Snowflake’s <a href="https://www.snowflake.com/legal-files/CreditConsumptionTable.pdf">0.0037-credits-per-uncompressed-GB rate</a>. 17.71783 displayed credits × $3/credit = $53.15348 using the unrounded metering values.
    </p>
    <p>
      <a href="https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/snowflake/costs/out/t2/run14/mv_refresh.json">Serverless MV refresh</a> was metered at 8.75553 credits. 8.75553 credits × $3/credit = $26.26659.
    </p>
    <p>
      <strong>Total: $53.15348 + $26.26659 = $79.42007.</strong> Ingest-time clustering is included in Snowpipe Streaming; no ingest warehouse was used.
    </p>
    <p class="note-heading"><strong>② NORMALIZED QUERY-SERVING COST</strong></p>
    <p>
      CostBench prices every matched active-ingestion query as full end-to-end runtime × the applicable per-second read-side rate. The matched schedule contains 209 × 4 = 836 aggregate executions and 35 × 2 = 70 drill-down executions per system.
    </p>
    <p class="note-subheading"><strong>ClickHouse Cloud</strong></p>
    <p>
      <strong>8 CUs</strong> × $0.3903/CU-hour × (<a href="https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/clickhouse-cloud/costs/out_t2/matched/snowflake_run14/dashboard.json">11.361s aggregate</a> + <a href="https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/clickhouse-cloud/costs/out_t2/matched/snowflake_run14/drilldown.json">50.466s drill-down</a>) ÷ 3,600 = $0.05362.
    </p>
    <p class="note-subheading"><strong>Snowflake</strong></p>
    <p>
      <strong>Interactive-priced time:</strong> (<a href="https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/snowflake/costs/out/t2/run14/dashboard.json">946.509s aggregate</a> + <a href="https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/snowflake/costs/out/t2/run14/drilldown.json">74.815s drill-down</a>) × 1.2 credits/hour × $3/credit ÷ 3,600 = $1.02132.
    </p>
    <p>
      Fallback-priced time: <a href="https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/snowflake/costs/out/t2/run14/dashboard.json">6,653.660s aggregate</a> × 2.7 credits/hour × $3/credit ÷ 3,600 = $14.97074.
    </p>
    <p>
      <strong>Total: $1.02132 + $14.97074 = $15.99207.</strong>
    </p>
    <p>
      The accepted proxy prices jobs at or below five seconds on Interactive Small and jobs above five seconds for their full elapsed time on Gen2 Small. Of 836 aggregate jobs, 477 (57.1%) crossed that threshold; no drill-down job did. Compilation is included.
    </p>
    <p>
      Standing fallback capacity, minimum billing, and an additional primary-warehouse charge for fallback-priced jobs are excluded.
    </p>
    <p class="note-heading"><strong>③ TOTAL QUERY RUNTIME</strong></p>
    <p>
      ClickHouse Cloud: 11.361s aggregate + 50.466s drill-down = 61.827s.
    </p>
    <p>
      Snowflake: 7,600.169s aggregate + 74.815s drill-down = 7,674.984s.
    </p>
    <p class="note-heading"><strong>CALCULATION BOUNDARY</strong></p>
    <p>
      ① covers the complete ingest. ② and ③ use row-count-matched observations from active ingestion only; post-ingestion observations are excluded.
    </p>
    <p>
      Storage is excluded. Database storage costs are excluded from the score, so the 412× result does not include the storage-footprint difference discussed earlier. Displayed values may be rounded, but the score uses full-precision inputs.
    </p>
    <p class="note-heading"><strong>FINAL SCORE</strong></p>
    <p>
      ClickHouse Cloud: ($28.68705 + $0.05362) × 61.827 = 1,776.9494.
    </p>
    <p>
      Snowflake: ($79.42007 + $15.99207) × 7,674.984 = 732,286.6479.
    </p>
    <p>
      <strong>Relative result: 732,286.6479 ÷ 1,776.9494 = 412.103×.</strong>
    </p>
    <p>
      The <a href="https://github.com/ClickHouse/CostBench/blob/main/full-path-realtime/quotes/snowflake/results/t2/charts/run14/full_path_cost_performance_clickhouse_vs_snowflake_wide_summary.json">exact summary</a> publishes every accepted input and the normalized-cost contract.
    </p>
  </div>
</details>

<video autoplay="1" muted="1" loop="1" controls="0">
  <source src="https://clickhouse.com/uploads/14_final_ranking_score_loop_450bdef682.mp4" type="video/mp4" />
</video>

Snowflake’s end-to-end path cost **3.32× as much** as ClickHouse Cloud’s, and its queries took **124× as long in total** across the matched workload. CostBench multiplies cost by total query runtime, so these two factors combine into a **412× worse end-to-end score**. 
 
> **Snowflake’s fresh-data path affected every score input:** Snowpipe Streaming and MV refresh added direct cost; reconciliation increased total query runtime; and that longer runtime increased normalized query-serving cost.


## What drives the real-time performance-per-dollar gap


The final view shows both dimensions of the result: ClickHouse Cloud finishes with lower end-to-end cost and less accumulated query runtime than Snowflake.


<video autoplay="1" muted="1" loop="1" controls="0">
  <source src="https://clickhouse.com/uploads/15_end_to_end_cost_vs_accumulated_query_clickhouse_snowflake_loop_47feb711c2.mp4" type="video/mp4" />
</video>

**ClickHouse Cloud**’s advantage begins with a simple, integrated architecture. Ingestion, ordering, and pre-aggregation are built into the storage engine. Raw data and summaries advance together, without a separate refresh service or cycle. Queries read current, prepared data, with no unfinished preparation work to catch up on.

**Snowflake**’s tested streaming path separates ingestion from pre-aggregation. Its raw table kept advancing, but its summaries fell behind. Returning current answers required queries to make up the difference, adding latency and cost.

The workarounds changed the trade-off. Querying raw data directly preserved freshness but repeated aggregation work. Serving separately refreshed summaries offered faster reads, but gave up continuous freshness and added infrastructure and cost.

Those architectural differences were visible in the results. During continuous ingestion through 100 billion rows, ClickHouse Cloud’s interactive aggregate queries achieved **42 ms P99 latency**, compared with **22.20 seconds** on Snowflake’s Interactive MV path.

The same architecture also kept the fresh-data path economical. Together, lower preparation cost and faster query serving produced **412× better end-to-end real-time performance per dollar** in this benchmark.

> **ClickHouse Cloud is purpose-built end to end for fast answers on continuously fresh data. Its advantage comes from how the complete system works together - from preparing each incoming row to serving current answers.**

Next in the CostBench series: ClickHouse Cloud vs. BigQuery.