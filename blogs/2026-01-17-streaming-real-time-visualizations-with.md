---
title: "Streaming Real-Time Visualizations with ClickHouse, Apache Arrow and Perspective"
date: "2024-10-02T14:56:45.193Z"
author: "Dale McDiarmid"
category: "Engineering"
excerpt: "Read about how ClickHouse can stream results in Arrow over HTTP, making it simple to integrate with high-performance visualization libraries such as Perspective."
---

# Streaming Real-Time Visualizations with ClickHouse, Apache Arrow and Perspective

As a company founded in open-source, we love to promote other OSS projects that impress us either because they look technically impressive, resonate with our obsession with performance, or we feel will genuinely help our users. On discovering the UI library [Perspective](https://perspective.finos.org/), we realized this ticked all of these requirements, allowing users to build truly [real-time visualizations](https://clickhouse.com/engineering-resources/real-time-data-visualization) on top of ClickHouse data! Keen to see if the library could be easily integrated with ClickHouse, we've built a simple demo application that provides rich visualization capabilities by streaming Forex data using Apache Arrow straight to the browser, all in a little more than 100 lines of code!

![forex_demo.png](https://clickhouse.com/uploads/forex_demo_f7a306db18.png)

The example should be easily adapted and allow users to visualize any dataset as it is streamed into ClickHouse. Let us know your thoughts, and shout out to Perspective for building such a cool library!

If you want to run the [example perspective app](https://github.com/ClickHouse/perspective-forex), we've provided a ClickHouse instance for you to use. Alternatively, play with a hosted version [here](https://perspective-clickhouse.vercel.app/). Finally, we'll explore how fast we can stream data and why the current approach isn't ideal, but some ideas for future ClickHouse features that will address these deficiencies.

## What is Perspective?

The **[Perspective Library](https://perspective.finos.org/)** is a high-performance data analytics and visualization tool designed to handle real-time and streaming datasets efficiently. It offers interactive and customizable visualizations, such as heat maps, line charts, and tree maps. Like ClickHouse, Perspective is built with performance in mind. Its core is written in Rust and C++ and compiled into WebAssembly. This enables it to process millions of data points in the browser and respond to continuous data streams.

Beyond simple rendering, Perspective offers fast operations for pivoting, filtering, and aggregating datasets in the browser or server side and performing expressions [using ExprTK](https://www.partow.net/programming/exprtk/index.html).  While this isn't designed for the petabyte scale seen in ClickHouse, it allows a 2nd level of data transformation on rows delivered to the client - reducing the need for further queries if the required data is already available and requires only a simple transformation to achieve the desired visual.

This makes it ideal for ClickHouse-powered applications where real-time insights and smooth interactivity are critical. With its support for both Python and JavaScript, it can be integrated into both backend analytics pipelines and web-based interfaces.

While Perspective complements ClickHouse perfectly for standard visualization needs, we were particularly interested in its ability to handle streaming data, maintaining a constant memory overhead by only retaining the latest N rows. We were curious how easy it would be to tail a continuously updated dataset, loading only the new delta into the browser where only the latest subset of points were retained and summarized.

<blockquote style="font-size: 14px;">
<p>While we focus on the javascript integration with Perspective, users can also use Perspective in Python with a JupyterLab widget and client library for interactive data analysis in a notebook.</p>
</blockquote>

## ClickHouse for streaming data?

While ClickHouse is not a stream processing engine but rather an OLAP database, it has features that provide functionality such as [Incremental Materialized views](https://clickhouse.com/docs/en/materialized-view), which allow much of the same functionality seen in technologies such as Apache Flink. These views are triggers that execute a query (which can include aggregates) on a block of data as it is inserted, storing the results in a different table for later use.

![mv_simple.png](https://clickhouse.com/uploads/mv_simple_31f168288b.png)

While many simple stream processing capabilities can replicate the simpler transforms and aggregates people perform in engines such as Flink to simplify architectures, we acknowledge these technologies work in unison, with the latter providing additional capabilities for advanced cases. When used for stream processing, ClickHouse has the added benefit of efficiently storing all of your data - allowing historical data to be queried.

In our case, we wanted to attempt streaming the latest rows in ClickHouse to Perspective for rendering. For our example, we'll crudely simulate the requirement to visualize forex trades as they arrive in ClickHouse. This will likely be most useful to a trader, with rows persisted for future historical analysis if required.

## Dataset - Forex

For our example, we'll use a forex dataset. Forex trading is the trading of currencies from different countries against each other, where a trader can either buy a base currency with a quote currency from the broker (at an `ask price`) or sell a base currency and receive the quote in return (at the `bid` price). The dataset tracks the price changes of each currency pair over time—what's important is that they change quickly!

For those not familiar with Forex trading, we recommend reading a [short section from this earlier post](https://clickhouse.com/blog/getting-data-into-clickhouse-part-3-s3#a-little-bit-about-forex), where we summarize the concepts.

The full dataset, available in a [public S3 bucket](https://github.com/ClickHouse/perspective-forex?tab=readme-ov-file#dataset), was downloaded from [www.histdata.com](www.histdata.com) and covers the years 2000 to 2022. It has 11.5 billion rows and 66 currency pairs (around 600GB decompressed).

While simple, the schema for this dataset is ideal for our example. Each row represents a tick. Timestamps here are to ms granularity, with columns indicating the base and quote currency and the ask and bid quotes.

<pre style="font-size: 14px;"><code class="hljs language-sql"><span class="hljs-keyword">CREATE</span> <span class="hljs-keyword">TABLE</span> forex
(
   `datetime` DateTime64(<span class="hljs-number">3</span>),
   `bid` <span class="hljs-type">Decimal</span>(<span class="hljs-number">11</span>, <span class="hljs-number">5</span>),
   `ask` <span class="hljs-type">Decimal</span>(<span class="hljs-number">11</span>, <span class="hljs-number">5</span>),
   `base` LowCardinality(String),
   `quote` LowCardinality(String)
)
ENGINE <span class="hljs-operator">=</span> MergeTree
<span class="hljs-keyword">ORDER</span> <span class="hljs-keyword">BY</span> (datetime, base, quote)
</code></pre>

<blockquote style="font-size: 14px;">
<p>Ticks record when the price of a stock or commodity changes by a predetermined amount or fractional change, i.e., a tick occurs when the price moves up or down by a specific amount or fractional change. A tick in Forex will happen when the bid or quote price changes.</p>
</blockquote>

Since a streaming feed for Forex is not available, we'll simulate this by loading a year's worth of data from parquet format and offsetting it to the current time. You can replicate this dataset if they wish to try the app on a local instance - see [here](https://github.com/ClickHouse/perspective-forex?tab=readme-ov-file#dataset).

<blockquote style="font-size: 14px;">
<p>Note that tick data does not represent an actual trade/exchange. The number of trades/exchanges per second is significantly higher! Nor does it capture the agreed price or the volume of the currency exchanged (logically 0 in the source data and hence ignored). Rather, it simply marks when the prices change by a unit known as <a href="https://clickhouse.com/blog/getting-data-into-clickhouse-part-3-s3#pips-and-ticks">the pip</a>.</p>
</blockquote>

## Connecting Perspective to ClickHouse with Arrow

### Some boilerplate

Setting up and configuring perspective requires [importing several packages](https://github.com/ClickHouse/perspective-forex/blob/main/index.html#L6-L8) with a little boilerplate code. The [public examples](https://perspective.finos.org/examples/) are excellent, but in summary, we create a worker and table. A worker represents a web worker process that offloads heavy operations, such as updates, from the browser's main renderer thread - ensuring that the interface remains responsive, even when streaming large real-time datasets. The table represents the primary data structure that can be updated dynamically with new data.

<pre style="font-size: 14px;"><code class="hljs language-js"><span class="hljs-keyword">import</span> perspective <span class="hljs-keyword">from</span> <span class="hljs-string">"https://cdn.jsdelivr.net/npm/@finos/perspective@3.0.0/dist/cdn/perspective.js"</span>;
<span class="hljs-keyword">const</span> forex_worker = <span class="hljs-keyword">await</span> perspective.<span class="hljs-title function_">worker</span>();
<span class="hljs-comment">// fetch some rows... </span>
<span class="hljs-keyword">const</span> forex_table = <span class="hljs-keyword">await</span> market_worker.<span class="hljs-title function_">table</span>(rows, { <span class="hljs-attr">limit</span>: <span class="hljs-number">20000</span> })
</code></pre>

<blockquote style="font-size: 14px;">
<p>We've kept our example as simple as possible, importing the package via CDN and avoiding any dependencies apart from perspective. Users integrating Perspective into existing applications or building production applications are recommended to explore the examples for <a href="https://perspective.finos.org/docs/js/#installation">common JS frameworks and build tooling</a>.</p>
</blockquote>

Perspective provides a number of [deployment models](https://perspective.finos.org/docs/server/)) that determine how data is loaded and bound, each with its respective pros and cons. For our example, we'll use the [client-only](https://perspective.finos.org/docs/server/#client-only) approach, with the data streamed to the browser, a few lines of Javascript fetching the data from ClickHouse over HTTP, and the WebAssembly library running all calculations and UI interactions.

### Streaming latest trades

When creating the table, as shown below, we limit the number of rows retained to restrict the memory overhead.

<pre style="font-size: 14px;"><code class="hljs language-js"><span class="hljs-keyword">const</span> forex_table = <span class="hljs-keyword">await</span> market_worker.<span class="hljs-title function_">table</span>(rows, { <span class="hljs-attr">limit</span>: <span class="hljs-number">20000</span> });
</code></pre>

For our example, we'll constantly add new rows to this table as new trades become available, relying on Perspective to retain only the latest 20k.

As of the time of writing, ClickHouse doesn't support web sockets or a means to stream changed rows to a client. We, therefore, use a polling approach to fetch the latest rows over HTTP. With Perspective preferring data in Apache Arrow format, we exploit ClickHouse's ability to return data in this format, which has the added benefit of minimizing the data transferred.

Forex ticks occur quickly, with up to 35 per second for the highest volume currency pairs. We want to fetch these as quickly as possible - ideally every 30-50ms, to ensure all values are visualized. Our query, therefore, needs to execute quickly, with each connected client issuing 10s of queries per second. Across all connected clients, we'd expect 100s of queries per second - something ClickHouse, contrary to some misconceptions, is comfortable serving.

Our query simply filters on the timestamp of the event, which is the first entry in our primary key [thus ensuring filtering is optimized](https://clickhouse.com/docs/en/optimize/sparse-primary-indexes). As all clients are issuing requests for approximately the same time period i.e. now, and monotonically increasing, our queries should be cache friendly. Testing showed that while our query executes in less than 10ms even on the full 11 billion row dataset, the HTTP round trip time to a ClickHouse instance is optimistically (same region) 20-30ms. We therefore just use a simple sliding window from the current time to the previous fetch time. This is continuously executed, retrieving rows as quickly as ClickHouse can serve them.

![sliding_window.png](https://clickhouse.com/uploads/sliding_window_a19e99b1cf.png)

The simplified diagram above assumes that each query execution takes exactly 50ms. Our query fetches all of the columns as well as computing the [spread](https://www.babypips.com/learn/forex/what-is-a-spread-in-forex-trading) (difference between the `ask` and `bid`). Ideally, we'd also like to show the change in the current bid - this is useful in trading.  To ensure the first values for each pair have the correct change value, we need to make sure we have the last price outside of the current window for each currency pair. For this, we query slightly more data than we return, as shown above and in our final query below.

<pre style="font-size: 14px;"><code class="hljs language-sql"><span class="hljs-keyword">SELECT</span> <span class="hljs-operator">*</span>
<span class="hljs-keyword">FROM</span>
(
   <span class="hljs-keyword">SELECT</span>
       concat(base, <span class="hljs-string">'.'</span>, quote) <span class="hljs-keyword">AS</span> base_quote,
       datetime <span class="hljs-keyword">AS</span> last_update,
       bid,
       ask,
       ask <span class="hljs-operator">-</span> bid <span class="hljs-keyword">AS</span> spread,
       ask <span class="hljs-operator">-</span> <span class="hljs-keyword">any</span>(ask) <span class="hljs-keyword">OVER</span> (<span class="hljs-keyword">PARTITION</span> <span class="hljs-keyword">BY</span> base_quote <span class="hljs-keyword">ORDER</span> <span class="hljs-keyword">BY</span> base_quote <span class="hljs-keyword">ASC</span>, datetime <span class="hljs-keyword">ASC</span> <span class="hljs-keyword">ROWS</span> <span class="hljs-keyword">BETWEEN</span> <span class="hljs-number">1</span> PRECEDING <span class="hljs-keyword">AND</span> <span class="hljs-keyword">CURRENT</span> <span class="hljs-type">ROW</span>) <span class="hljs-keyword">AS</span> chg
   <span class="hljs-keyword">FROM</span> forex
   <span class="hljs-keyword">WHERE</span> datetime <span class="hljs-operator">&gt;</span> {prev_lower_bound:DateTime64(<span class="hljs-number">3</span>)} <span class="hljs-keyword">AND</span> datetime <span class="hljs-operator">&lt;=</span> {upper_bound:DateTime64(<span class="hljs-number">3</span>)}
   <span class="hljs-keyword">ORDER</span> <span class="hljs-keyword">BY</span>
       base_quote <span class="hljs-keyword">ASC</span>,
       datetime <span class="hljs-keyword">ASC</span>
)
<span class="hljs-keyword">WHERE</span> datetime <span class="hljs-operator">&gt;</span> {lower_bound:DateTime64(<span class="hljs-number">3</span>)} <span class="hljs-keyword">AND</span> datetime <span class="hljs-operator">&lt;=</span> {upper_bound:DateTime64(<span class="hljs-number">3</span>)}
<span class="hljs-keyword">ORDER</span> <span class="hljs-keyword">BY</span> last_update <span class="hljs-keyword">ASC</span>

┌─base_quote─┬─────────────last_update─┬─────bid─┬────────ask─┬──spread─┬──────chg─┐
│ AUD.CAD    │ <span class="hljs-number">2024</span><span class="hljs-number">-09</span><span class="hljs-number">-19</span> <span class="hljs-number">13</span>:<span class="hljs-number">25</span>:<span class="hljs-number">30.840</span> │ <span class="hljs-number">0.97922</span> │    <span class="hljs-number">0.97972</span> │  <span class="hljs-number">0.0005</span> │ <span class="hljs-number">-0.00002</span> │
│ XAG.USD    │ <span class="hljs-number">2024</span><span class="hljs-number">-09</span><span class="hljs-number">-19</span> <span class="hljs-number">13</span>:<span class="hljs-number">25</span>:<span class="hljs-number">30.840</span> │  <span class="hljs-number">17.858</span> │   <span class="hljs-number">17.90299</span> │ <span class="hljs-number">0.04499</span> │  <span class="hljs-number">0.00499</span> │
│ AUD.JPY    │ <span class="hljs-number">2024</span><span class="hljs-number">-09</span><span class="hljs-number">-19</span> <span class="hljs-number">13</span>:<span class="hljs-number">25</span>:<span class="hljs-number">30.840</span> │   <span class="hljs-number">97.28</span> │      <span class="hljs-number">97.31</span> │    <span class="hljs-number">0.03</span> │   <span class="hljs-number">-0.001</span> │
│ AUD.NZD    │ <span class="hljs-number">2024</span><span class="hljs-number">-09</span><span class="hljs-number">-19</span> <span class="hljs-number">13</span>:<span class="hljs-number">25</span>:<span class="hljs-number">30.840</span> │ <span class="hljs-number">1.09886</span> │    <span class="hljs-number">1.09946</span> │  <span class="hljs-number">0.0006</span> │  <span class="hljs-number">0.00004</span> │
...
│ EUR.AUD    │ <span class="hljs-number">2024</span><span class="hljs-number">-09</span><span class="hljs-number">-19</span> <span class="hljs-number">13</span>:<span class="hljs-number">25</span>:<span class="hljs-number">30.840</span> │ <span class="hljs-number">1.43734</span> │    <span class="hljs-number">1.43774</span> │  <span class="hljs-number">0.0004</span> │ <span class="hljs-number">-0.00002</span> │
└────────────┴─────────────────────────┴─────────┴────────────┴─────────┴──────────┘

<span class="hljs-number">25</span> <span class="hljs-keyword">rows</span> <span class="hljs-keyword">in</span> set. Elapsed: <span class="hljs-number">0.012</span> sec. Processed <span class="hljs-number">24.57</span> thousand <span class="hljs-keyword">rows</span>, <span class="hljs-number">638.82</span> KB (<span class="hljs-number">2.11</span> million <span class="hljs-keyword">rows</span><span class="hljs-operator">/</span>s., <span class="hljs-number">54.98</span> MB<span class="hljs-operator">/</span>s.)
Peak memory usage: <span class="hljs-number">5.10</span> MiB.
</code></pre>

<blockquote style="font-size: 14px;">
<p>Note how we apply a time range filter to the argMax so we don't need to perform a complete scan over all rows where the time &lt; lower bound (rather <code>lower bound - 5 mins &lt; time &lt; lower bound</code>).</p>
</blockquote>

Our final function for fetching the next rows can be found [here](https://github.com/ClickHouse/perspective-forex/blob/ffc48caf4b7395f6d02b12f9920b8754f8035d86/index.js#L47-L51). This uses the above query, requesting the data in Arrow format and reading the response into an ArrayBuffer as required by Perspective.

<blockquote style="font-size: 14px;">
<p>We don't use the <a href="https://clickhouse.com/docs/en/integrations/javascript">ClickHouse JS library,</a> mainly to minimize dependencies but also because our code is so simple. We recommend that complex applications use this.</p>
</blockquote>

## Initial application

Our application, shown below, invokes the above function to fetch rows [in a continuous loop](https://github.com/ClickHouse/perspective-forex/blob/ffc48caf4b7395f6d02b12f9920b8754f8035d86/index.js#L72):

![simple_forex.gif](https://clickhouse.com/uploads/simple_forex_5b63c6b76d.gif)

Our [loop computes also the average fetch time](https://github.com/ClickHouse/perspective-forex/blob/ffc48caf4b7395f6d02b12f9920b8754f8035d86/index.js#L83-L85) (averaged across the latest 10 requests). The performance here will depend on how close you are to the ClickHouse cluster, with the latency dominated by the HTTP fetch time. With reasonable proximity to a ClickHouse service, we were able to reduce this to about 30ms.

While we display the datagrid for the out of the box visualization, users can easily modify the visualization type and apply transformations. In the example below, we switch to a scatter visualization to plot the bid and ask prices for the `EUR-GBP` currency pair.

![forex_simple_line.gif](https://clickhouse.com/uploads/forex_simple_line_78fbb99645.gif)

Curious to test the CPU load for this, we initiated 20 concurrent clients resulting in almost 200 queries per second. Even with this load, ClickHouse uses less than 2 cores.

![cpu.png](https://clickhouse.com/uploads/cpu_df004dba1c.png)

### Not quite streaming, yet

In reality, the above, in a real scenario, could potentially miss rows if tracking the current time due to ClickHouse's eventual consistency model. Even though this can be mitigated with [careful configuration](https://clickhouse.com/docs/en/operations/settings/settings#settings-select_sequential_consistency), it's suboptimal. Rows are also likely to incur some insert latency, so we'd want to offset our query from the current time rather than just using `now()`.

We acknowledge these deficiencies and have begun [exploring the concept of streaming queries](https://github.com/ClickHouse/ClickHouse/pull/63312), which would reliably only return new rows as they match a specified query. This would remove the need for polling, with the client simply opening an HTTP connection with the query and receiving rows as they arrive.

## A speed test - with Arrow Stream

While following the ticks in real time is probably the most useful, we were curious to see how fast Perspective could actually handle the data. For this we wanted to stream the entire dataset to Perspective in ascending date order, again only keeping the last N data points. Our query, in this case, becomes:

<pre style="font-size: 14px;"><code class="hljs language-sql"><span class="hljs-keyword">SELECT</span> concat(base, <span class="hljs-string">'.'</span>, quote) <span class="hljs-keyword">AS</span> base_quote,
	datetime <span class="hljs-keyword">AS</span> last_update,
	<span class="hljs-built_in">CAST</span>(bid, <span class="hljs-string">'Float32'</span>) <span class="hljs-keyword">AS</span> bid,
	<span class="hljs-built_in">CAST</span>(ask, <span class="hljs-string">'Float32'</span>) <span class="hljs-keyword">AS</span> ask,
	ask <span class="hljs-operator">-</span> bid <span class="hljs-keyword">AS</span> spread
<span class="hljs-keyword">FROM</span> forex
<span class="hljs-keyword">ORDER</span> <span class="hljs-keyword">BY</span> datetime <span class="hljs-keyword">ASC</span>
FORMAT ArrowStream
SETTINGS output_format_arrow_compression_method<span class="hljs-operator">=</span><span class="hljs-string">'none'</span>
</code></pre>

<blockquote style="font-size: 14px;">
<p>Note how we've dropped the computation of the change per currency pair. This requires a window function that doesn't exploit the<a href="https://clickhouse.com/docs/en/operations/settings/settings#optimize_read_in_order"> optimize_read_in_order</a> and prevents an immediate stream of the results.</p>
</blockquote>

For this, you'll notice we don't just use Arrow format. This would require us to download the entire dataset [>60GB compressed in ClickHouse](https://sql.clickhouse.com?query_id=6B6MXXER1XG8J2QVTY3NMA) and convert it to a table for Perspective. Even in Arrow format, this is a little large for a browser!

Instead we exploit ClickHouse's support for the Arrow Stream format, reading the data in chunks and passing this to perspective. While previously we could do all the work without a dependency, for this we need the [Arrow js lib](https://arrow.apache.org/docs/js/). While this makes consuming Arrow files trivial, to support streaming we need a bit more JS. Our final function which streams the entire dataset a batch at a time is shown below.

<pre style="font-size: 14px;"><code class="hljs language-js"><span class="hljs-keyword">async</span> <span class="hljs-keyword">function</span> <span class="hljs-title function_">get_all_rows</span>(<span class="hljs-params">table, lower_bound</span>) {
   <span class="hljs-keyword">const</span> view = <span class="hljs-keyword">await</span> table.<span class="hljs-title function_">view</span>({ <span class="hljs-comment">// Create a view with aggregation to get the maximum datetime value</span>
       <span class="hljs-attr">columns</span>: [<span class="hljs-string">"last_update"</span>], <span class="hljs-comment">// Column you're interested in</span>
       <span class="hljs-attr">aggregates</span>: { <span class="hljs-attr">last_update</span>: <span class="hljs-string">"max"</span> } <span class="hljs-comment">// Aggregate by the maximum of datetime</span>
   });
   <span class="hljs-keyword">const</span> response = <span class="hljs-keyword">await</span> <span class="hljs-title function_">fetch</span>(clickhouse_url, {
       <span class="hljs-attr">method</span>: <span class="hljs-string">'POST'</span>,
       <span class="hljs-attr">body</span>: <span class="hljs-string">`SELECT concat(base, '.', quote) AS base_quote, datetime AS last_update, bid::Float32 as bid,  ask::Float32 as ask, ask - bid AS spread
              FROM forex WHERE datetime &gt; <span class="hljs-subst">${lower_bound}</span>::DateTime64(3) ORDER BY datetime ASC FORMAT ArrowStream SETTINGS output_format_arrow_compression_method='none'`</span>,
       <span class="hljs-attr">headers</span>: { <span class="hljs-string">'Authorization'</span>: <span class="hljs-string">`Basic <span class="hljs-subst">${credentials}</span>`</span> }
   });
   <span class="hljs-keyword">const</span> reader = <span class="hljs-keyword">await</span> <span class="hljs-title class_">RecordBatchReader</span>.<span class="hljs-title function_">from</span>(response);
   <span class="hljs-keyword">await</span> reader.<span class="hljs-title function_">open</span>();
   <span class="hljs-keyword">for</span> <span class="hljs-keyword">await</span> (<span class="hljs-keyword">const</span> recordBatch <span class="hljs-keyword">of</span> reader) {  <span class="hljs-comment">// Continuously read from the stream</span>
       <span class="hljs-keyword">if</span> (real_time) { <span class="hljs-comment">// set to false if we want to stop the stream</span>
           <span class="hljs-keyword">await</span> view.<span class="hljs-title function_">delete</span>();
           <span class="hljs-keyword">return</span>;
       }
       <span class="hljs-keyword">const</span> batchTable = <span class="hljs-keyword">new</span> <span class="hljs-title class_">Table</span>(recordBatch); <span class="hljs-comment">// currently required, see https://github.com/finos/perspective/issues/1157</span>
       <span class="hljs-keyword">const</span> ipcStream = <span class="hljs-title function_">tableToIPC</span>(batchTable, <span class="hljs-string">'stream'</span>);
       <span class="hljs-keyword">const</span> bytes = <span class="hljs-keyword">new</span> <span class="hljs-title class_">Uint8Array</span>(ipcStream);
       table.<span class="hljs-title function_">update</span>(bytes);
       <span class="hljs-keyword">const</span> result = <span class="hljs-keyword">await</span> view.<span class="hljs-title function_">to_columns</span>();
       <span class="hljs-keyword">const</span> maxDateTime = result[<span class="hljs-string">"last_update"</span>][<span class="hljs-number">0</span>];
       <span class="hljs-variable language_">document</span>.<span class="hljs-title function_">getElementById</span>(<span class="hljs-string">"last_updated"</span>).<span class="hljs-property">textContent</span> = <span class="hljs-string">`Last updated: <span class="hljs-subst">${<span class="hljs-keyword">new</span> <span class="hljs-built_in">Date</span>(maxDateTime).toISOString()}</span>`</span>;
       total_size += (bytes.<span class="hljs-property">length</span>);
       <span class="hljs-variable language_">document</span>.<span class="hljs-title function_">getElementById</span>(<span class="hljs-string">"total_download"</span>).<span class="hljs-property">textContent</span> = <span class="hljs-string">`Total Downloaded: <span class="hljs-subst">${prettyPrintSize(total_size,<span class="hljs-number">2</span>)}</span>`</span>;
   }
}
</code></pre>

This code could be more efficient than it is - mainly as Perspective currently [requires an array of bytes](https://github.com/finos/perspective/issues/1157) for the update call. This forces us to convert our batch to a table and stream this to an array. We also use a Perspective view, conceptually similar to a materialized view in ClickHouse - executing an aggregation on the table data as it's loaded. In this case, we use the view to simply compute the maximum streamed date, which we show in the final UI.

With a little additional code to switch between the earlier "real-time" polling mode and this "streaming mode," we have our final app. Switching to streaming mode shows the performance of Perspective:

![super_fast_forex.gif](https://clickhouse.com/uploads/super_fast_forex_ab5036cd9d.gif)

The line chart on a currency pair shows how we're able to render thousands of data points per second with at least 25MiB/sec streamed to the browser.

You can play with the final application [here](https://perspective-clickhouse.vercel.app/).

## Conclusion

We've used this blog to explore a popular open-source visualization library, Perspective, which has useful applications for ClickHouse with synergies in performance and the ability to handle large volumes of data arriving quickly! Thanks to Apache Arrow, we can integrate ClickHouse with Perspective in only a few lines of JavaScript. In the process, we've also identified some of the limitations of ClickHouse's ability to handle streaming data and highlighted current work we hope will address these.
