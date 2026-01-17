---
title: "Announcing CryptoHouse: Free Blockchain Analytics powered by ClickHouse and Goldsky"
date: "2024-08-06T10:40:36.500Z"
author: "The ClickHouse & Goldsky teams"
category: "Engineering"
excerpt: "We’re delighted to announce CryptoHouse, accessible at crypto.clickhouse.com, free blockchain analytics powered by ClickHouse and Goldsky. "
---

# Announcing CryptoHouse: Free Blockchain Analytics powered by ClickHouse and Goldsky

**TL;DR:** We’re delighted to announce CryptoHouse, accessible at [crypto.clickhouse.com](https://crypto.clickhouse.com), free blockchain analytics powered by ClickHouse. 

Existing public blockchain analytics services require scheduled, asynchronous queries, but ClickHouse offers real-time analytics, democratizing access by enabling instant query responses. Users can use SQL to query this data, which is updated in real-time, thanks to [Goldsky](https://goldsky.com/), at no cost. Our custom UI allows for saving and sharing queries and basic charting, with examples to get users started.  We welcome external contributions to the [example queries](https://github.com/ClickHouse/CryptoHouse) to help in this effort.

As of today, users of CryptoHouse can query Solana [blocks](https://crypto.clickhouse.com?query=U0VMRUNUCiAgICAqCkZST00KICAgIHNvbGFuYS5ibG9ja3MKTElNSVQKICAgIDEwMDA), [transactions](https://crypto.clickhouse.com?query=U0VMRUNUCiAgICAqCkZST00KICAgIHNvbGFuYS50cmFuc2FjdGlvbnMKTElNSVQKICAgIDEwMDA), [token_transfers](https://crypto.clickhouse.com?query=U0VMRUNUCiAgICAqCkZST00KICAgIHNvbGFuYS50b2tlbl90cmFuc2ZlcnMKTElNSVQKICAgIDEwMDA), [block_rewards](https://crypto.clickhouse.com?query=U0VMRUNUCiAgICAqCkZST00KICAgIHNvbGFuYS5ibG9ja19yZXdhcmRzCkxJTUlUCiAgICAxMDAw), [accounts](https://crypto.clickhouse.com?query=U0VMRUNUCiAgICAqCkZST00KICAgIHNvbGFuYS5hY2NvdW50cwpMSU1JVAogICAgMTAwMA), and [tokens](https://crypto.clickhouse.com?query=U0VMRUNUCiAgICAqCkZST00KICAgIHNvbGFuYS50b2tlbnMKTElNSVQKICAgIDEwMDA) for free. Similar datasets are available for Ethereum. We plan to expand the data available and expose more blockchains in the coming months!

![cryptohouse_screenshot.png](https://clickhouse.com/uploads/cryptohouse_screenshot_b1440c9cc9.png)

If you’re interested in why and how we built this service, read on…

## A need for blockchain analytics

Blockchains are complex entities that can handle thousands of transactions and smart contract executions per second. Understanding their changes and state is crucial for investors making informed decisions and developers building these contracts.

SQL is a natural language for performing these analytics, but this presents two significant challenges: (1) converting blockchain entities into a structured, row-oriented format, and (2) finding a database capable of handling the high throughput and potentially petabytes of data while serving the analytical queries users need.

## ClickHouse is the standard for blockchain analytics

As an open-source OLAP database, ClickHouse is ideal for storing blockchain data due to its column-oriented design and highly parallel execution engine. This allows queries to run over terabytes of data, delivering fast analytics across the full dataset. As a result, we have seen ClickHouse increasingly used for blockchain analytics, with companies such as Goldsky and Nansen using ClickHouse at the core of their offerings.


## Building a public service

Anyone who follows ClickHouse and is aware of our public demos will know we love to take on big datasets and build services around them. Earlier this year, we released [ClickPy](https://clickpy.clickhouse.com/), which provides free analytics on Python package downloads. More recently, [adsb.exposed](https://adsb.exposed/) wowed the community with some amazing visuals on flight data.

We’ve long known that blockchains offered the potential to satisfy our hunger for large, complex datasets. Of the popular blockchains, we knew the Solana network offers both size and complexity.  While existing solutions exist for a public blockchain analytics service, users typically have to schedule queries and wait for them to execute asynchronously - persisting the results for later retrieval. As the maintainers of ClickHouse, we knew we could serve the problem better, delivering real-time analytics on the blockchains at a fraction of the cost and democratizing access to the data by allowing users to write queries and retrieve responses in real time.

While we were comfortable with the ClickHouse side of the effort, we admittedly aren’t crypto experts. Efforts to convert the Solana blockchain into a structured row orientated format looked involved with some prerequisite for domain expertise. The "challenge" therefore remained on pause until some fortuitous meetings earlier this year.

## Enter Goldsky 

[Goldsky](https://goldsky.com/) is a product which specializes in cryptocurrency data infrastructure, providing developers with tools to build great real-time applications using data from Solana and other blockchain networks. Their platform supports developers in building reliable, data-driven Web3 applications by offering services like live data streaming of blockchain events in a structured format, with delivery straight into databases. 

While Goldsky have been users of ClickHouse for some time for their own internal use cases, they are frequently requested to send blockchain data to their customers' own ClickHouse clusters who are looking to perform analytics. While interviewing Jeff Ling, the CTO of Goldsky, for[ a user story](https://clickhouse.com/blog/clickhouse-redpanda-architecture-with-goldsky) late last year, we shared our idea of building what would become CryptoHouse. To our surprise, Jeff was eager to participate and solve the data engineering component of our problem!

## Data engineering challenges

Solana produces 3000-4000 transactions per second, with data that needs to be directly extracted from the nodes. Initially, Goldsky operationalized open-source software to provide Solana support, which equates to scraping the built-in blockchain node APIs. This approach led to an architecture where new blocks would be detected and put into a queue, with multiple workers in charge of fetching all the required transactions before putting these into the [Goldsky Mirror data streaming platform](https://goldsky.com/products/mirror) with minimal latency.

In practice, each transaction was also extracted into additional datasets, such as token transfers and account changes. The ingestion framework was adjusted to account for all the downstream transformations needed.

With the data now ingesting live into the platform, a mirror pipeline configuration was created for all the tables we wanted to support. Some transformations were needed to match the data with the table, which was optimized for efficient storage and aimed at the most common queries that users would want to run.

<pre style="font-size: 14px;"><code class="hljs language-yaml"><span class="hljs-comment"># Example pipeline for blocks - this was repeated for all tables</span>
<span class="hljs-attr">name:</span> <span class="hljs-string">clickhouse-partnership-solana</span>
<span class="hljs-attr">sources:</span>
  <span class="hljs-attr">blocks:</span>
    <span class="hljs-attr">dataset_name:</span> <span class="hljs-string">solana.edge_blocks</span>
    <span class="hljs-attr">type:</span> <span class="hljs-string">dataset</span>
    <span class="hljs-attr">version:</span> <span class="hljs-number">1.0</span><span class="hljs-number">.0</span>
<span class="hljs-attr">transforms:</span>
  <span class="hljs-attr">blocks_transform:</span>
    <span class="hljs-attr">sql:</span> <span class="hljs-string">&gt;
      SELECT hash as block_hash, `timestamp` AS block_timestamp, height, leader, leader_reward, previous_block_hash, slot, transaction_count 
      FROM blocks 
</span>    <span class="hljs-attr">primary_key:</span> <span class="hljs-string">block_timestamp,</span> <span class="hljs-string">slot,</span> <span class="hljs-string">block_hash</span>
<span class="hljs-attr">sinks:</span>
  <span class="hljs-attr">solana_blocks_sink:</span>
    <span class="hljs-attr">type:</span> <span class="hljs-string">clickhouse</span>
    <span class="hljs-attr">table:</span> <span class="hljs-string">blocks</span>
    <span class="hljs-attr">secret_name:</span> <span class="hljs-string">CLICKHOUSE_PARTNERSHIP_SOLANA</span>
    <span class="hljs-attr">from:</span> <span class="hljs-string">blocks_transform</span>
</code></pre>

Finally, since the final schema required tuples, we had difficulty converting the JSON from our dataset into the right format. To address this we make use of the [Null table engine](https://clickhouse.com/docs/en/engines/table-engines/special/null), combined with a Materialized View, to do ClickHouse-specific transformations from a JSON string to a tuple. For example, the following view and Null table are responsible for receiving inserts for the tokens dataset. The results of the Materialized View are sent to the final `solana.tokens` table: 

<pre style="font-size: 14px;"><code class="hljs language-sql"><span class="hljs-keyword">CREATE</span> <span class="hljs-keyword">TABLE</span> solana.stage_tokens
(
	`block_slot` Int64,
	`block_hash` String,
	`block_timestamp` DateTime64(<span class="hljs-number">6</span>),
	`tx_signature` String,
	`retrieval_timestamp` DateTime64(<span class="hljs-number">6</span>),
	`is_nft` Bool,
	`mint` String,
	`update_authority` String,
	`name` String,
	`symbol` String,
	`uri` String,
	`seller_fee_basis_points` <span class="hljs-type">Decimal</span>(<span class="hljs-number">38</span>, <span class="hljs-number">9</span>),
	`creators` String,
	`primary_sale_happened` Bool,
	`is_mutable` Bool
)
ENGINE <span class="hljs-operator">=</span> <span class="hljs-keyword">Null</span>

<span class="hljs-keyword">CREATE</span> MATERIALIZED <span class="hljs-keyword">VIEW</span> solana.stage_tokens_mv <span class="hljs-keyword">TO</span> solana.tokens
(
	`block_slot` Int64,
	`block_hash` String,
	`block_timestamp` DateTime64(<span class="hljs-number">6</span>),
	`tx_signature` String,
	`retrieval_timestamp` DateTime64(<span class="hljs-number">6</span>),
	`is_nft` Bool,
	`mint` String,
	`update_authority` String,
	`name` String,
	`symbol` String,
	`uri` String,
	`seller_fee_basis_points` <span class="hljs-type">Decimal</span>(<span class="hljs-number">38</span>, <span class="hljs-number">9</span>),
	`creators` <span class="hljs-keyword">Array</span>(Tuple(String, UInt8, Int64)),
	`primary_sale_happened` Bool,
	`is_mutable` Bool
)
<span class="hljs-keyword">AS</span> <span class="hljs-keyword">SELECT</span> block_slot, block_hash, block_timestamp, tx_signature, retrieval_timestamp, is_nft, mint, update_authority, name, symbol, uri, seller_fee_basis_points, arrayMap(x <span class="hljs-operator">-</span><span class="hljs-operator">&gt;</span> (x<span class="hljs-number">.1</span>, (x<span class="hljs-number">.2</span>) <span class="hljs-operator">=</span> <span class="hljs-number">1</span>, x<span class="hljs-number">.3</span>), <span class="hljs-built_in">CAST</span>(creators, <span class="hljs-string">'Array(Tuple(String, Int8, Int64))'</span>)) <span class="hljs-keyword">AS</span> creators,primary_sale_happened, is_mutable
<span class="hljs-keyword">FROM</span> solana.stage_tokens
</code></pre>

This was incredibly efficient and gave us a lot of flexibility, which allowed us to backfill the data at speeds close to 500k rows/second. 

At the edge, we could easily optimize to just having one pipeline with 10 workers to handle all edge data, which equates to around 6000 rows per second written. 

For users interested in more details about how incremental Materialized Views work in ClickHouse, we recommend [these docs](https://clickhouse.com/docs/en/materialized-view) or [this video](https://www.youtube.com/watch?v=QUigKP7iy7Y). 

<blockquote style="font-size: 14px;">
<p>When querying, users may notice that some of the Solana blocks and transactions have a <code>timestamp</code> with a value of <code>1970-01-01</code> and a <code>height</code> of 0. While Goldsky provides new data, rows prior to June 2024 have been backfilled from BigQuery. This data has Null entries for some timestamp and height values, which in ClickHouse become default values for their respective types - Date and Int64. We intend to rectify these data quality issues in the long term.</p>
</blockquote>

## ClickHouse challenges

### Ensuring fair usage

While the data volume for the Solana blockchain is unremarkable for ClickHouse, with the largest table holding transactions around 500TiB (as shown below), we wanted to provide functionality where anyone could write a SQL query. This presented problems around managing resources fairly across all users and ensuring that a single query cannot consume all available memory or CPU.

<pre style="font-size: 14px;"><code class="hljs language-sql"><span class="hljs-keyword">SELECT</span>
   `<span class="hljs-keyword">table</span>`,
   formatReadableSize(<span class="hljs-built_in">sum</span>(data_compressed_bytes)) <span class="hljs-keyword">AS</span> compressed_size,
   formatReadableSize(<span class="hljs-built_in">sum</span>(data_uncompressed_bytes)) <span class="hljs-keyword">AS</span> uncompressed_size,
   round(<span class="hljs-built_in">sum</span>(data_uncompressed_bytes) <span class="hljs-operator">/</span> <span class="hljs-built_in">sum</span>(data_compressed_bytes), <span class="hljs-number">2</span>) <span class="hljs-keyword">AS</span> ratio
<span class="hljs-keyword">FROM</span> system.parts
<span class="hljs-keyword">WHERE</span> (database <span class="hljs-operator">=</span> <span class="hljs-string">'solana'</span>) <span class="hljs-keyword">AND</span> active
<span class="hljs-keyword">GROUP</span> <span class="hljs-keyword">BY</span> `<span class="hljs-keyword">table</span>`
<span class="hljs-keyword">ORDER</span> <span class="hljs-keyword">BY</span> <span class="hljs-built_in">sum</span>(data_compressed_bytes) <span class="hljs-keyword">DESC</span>

┌─<span class="hljs-keyword">table</span>─────────────────────────┬─compressed_size─┬─uncompressed_size─┬─ratio─┐
│ transactions                  │ <span class="hljs-number">79.34</span> TiB       │ <span class="hljs-number">468.91</span> TiB        │  <span class="hljs-number">5.91</span> │
│ transactions_non_voting       │ <span class="hljs-number">17.89</span> TiB       │ <span class="hljs-number">162.20</span> TiB        │  <span class="hljs-number">9.07</span> │
│ token_transfers               │ <span class="hljs-number">3.08</span> TiB        │ <span class="hljs-number">18.84</span> TiB         │  <span class="hljs-number">6.11</span> │
│ block_rewards                 │ <span class="hljs-number">1.31</span> TiB        │ <span class="hljs-number">10.85</span> TiB         │  <span class="hljs-number">8.28</span> │
│ accounts                      │ <span class="hljs-number">47.82</span> GiB       │ <span class="hljs-number">217.88</span> GiB        │  <span class="hljs-number">4.56</span> │
│ blocks                        │ <span class="hljs-number">41.17</span> GiB       │ <span class="hljs-number">82.64</span> GiB         │  <span class="hljs-number">2.01</span> │
│ tokens                        │ <span class="hljs-number">3.42</span> GiB        │ <span class="hljs-number">10.10</span> GiB         │  <span class="hljs-number">2.96</span> │
└───────────────────────────────┴─────────────────┴───────────────────┴───────┘

<span class="hljs-number">10</span> <span class="hljs-keyword">rows</span> <span class="hljs-keyword">in</span> set. Elapsed: <span class="hljs-number">0.009</span> sec. Processed <span class="hljs-number">1.42</span> thousand <span class="hljs-keyword">rows</span>, <span class="hljs-number">78.31</span> KB (<span class="hljs-number">158.79</span> thousand <span class="hljs-keyword">rows</span><span class="hljs-operator">/</span>s., <span class="hljs-number">8.74</span> MB<span class="hljs-operator">/</span>s.)
Peak memory usage: <span class="hljs-number">99.91</span> KiB.
</code></pre>

To ensure fair usage (and predictable costs), we impose[ ClickHouse usage quotas](https://clickhouse.com/docs/en/operations/quotas), limiting the number of rows a user query can scan to 10 billion. Queries must also be completed within 60 seconds (most do, thanks to ClickHouse’s performance) with a limit of 60 queries per user per hour. Other limits concerning memory usage aim to ensure service stability and fair usage.

### Accelerating queries with Materialized Views

Some queries are invariably more computationally expensive than others. Blockchain queries also often need to scan large amounts of data, providing summary statistics over hundreds of billions of rows. To enable these sorts of queries, we provide ClickHouse Materialized Views, which shift the computation from query time to insert time. This can dramatically accelerate certain queries and allow users to obtain statistics computed across the entire dataset.  These views are incrementally updated in real time as data is inserted. As an example, consider the [following query](https://crypto.clickhouse.com?query=U0VMRUNUCiAgdG9TdGFydE9mSG91cihibG9ja190aW1lc3RhbXApIGFzIGhvdXIsCiAgYXZnKGZlZSAvIDFlOSkgQVMgYXZnX2ZlZV9zb2wsCiAgc3VtKGZlZSAvIDFlOSkgYXMgZmVlX3NvbApGUk9NCiAgc29sYW5hLnRyYW5zYWN0aW9uc19ub25fdm90aW5nCldIRVJFIGJsb2NrX3RpbWVzdGFtcCA-IHRvZGF5KCkgLSBJTlRFUlZBTCAxIE1PTlRICkdST1VQIEJZCiAgMQpPUkRFUiBCWQogIDEgQVND), which computes daily fees for every day in the last month:

<pre style="font-size: 14px;"><code class="hljs language-sql"><span class="hljs-keyword">SELECT</span>
  toStartOfDay(block_timestamp) <span class="hljs-keyword">as</span> <span class="hljs-keyword">day</span>,
  <span class="hljs-built_in">avg</span>(fee <span class="hljs-operator">/</span> <span class="hljs-number">1e9</span>) <span class="hljs-keyword">AS</span> avg_fee_sol,
  <span class="hljs-built_in">sum</span>(fee <span class="hljs-operator">/</span> <span class="hljs-number">1e9</span>) <span class="hljs-keyword">as</span> fee_sol
<span class="hljs-keyword">FROM</span>
  solana.transactions_non_voting
<span class="hljs-keyword">WHERE</span> block_timestamp <span class="hljs-operator">&gt;</span> today() <span class="hljs-operator">-</span> <span class="hljs-type">INTERVAL</span> <span class="hljs-number">1</span> <span class="hljs-keyword">MONTH</span>
<span class="hljs-keyword">GROUP</span> <span class="hljs-keyword">BY</span>
  <span class="hljs-number">1</span>
<span class="hljs-keyword">ORDER</span> <span class="hljs-keyword">BY</span> <span class="hljs-number">1</span> <span class="hljs-keyword">DESC</span>

<span class="hljs-number">31</span> <span class="hljs-keyword">rows</span> <span class="hljs-keyword">in</span> set. Elapsed: <span class="hljs-number">1.783</span> sec. Processed <span class="hljs-number">2.12</span> billion <span class="hljs-keyword">rows</span>, <span class="hljs-number">50.98</span> GB (<span class="hljs-number">1.19</span> billion <span class="hljs-keyword">rows</span><span class="hljs-operator">/</span>s., <span class="hljs-number">28.58</span> GB<span class="hljs-operator">/</span>s.)
Peak memory usage: <span class="hljs-number">454.44</span> MiB.
</code></pre>

This query scans around 2b rows and completes in 2s. Users can obtain the same result by using one of the [example queries](https://crypto.clickhouse.com?query=LS1EYWlseSBmZWVzLiBUaGlzIHVzZXMgYSBtYXRlcmlhbGl6ZWQgdmlldywgZ3JvdXBpbmcgYnkgZGF5LiBGb3IgbW9yZSBncmFudWxhciBwZXJpb2RzIHVzZSB0aGUgc29sYW5hLnRyYW5zYWN0aW9uc19ub25fdm90aW5nIHRhYmxlIGUuZy4gaHR0cHM6Ly9jcnlwdG8uY2xpY2tob3VzZS5jb20_cXVlcnk9VTBWTVJVTlVJSFJ2VTNSaGNuUlBaa2h2ZFhJb1lteHZZMnRmZEdsdFpYTjBZVzF3S1NCaGN5Qm9iM1Z5TENCaGRtY29abVZsTHpGbE9Ta2dRVk1nWVhablgyWmxaVjl6YjJ3c0lITjFiU2htWldVdk1XVTVLU0JoY3lCbVpXVmZjMjlzSUVaU1QwMGdjMjlzWVc1aExuUnlZVzV6WVdOMGFXOXVjMTl1YjI1ZmRtOTBhVzVuSUZkSVJWSkZJR0pzYjJOclgzUnBiV1Z6ZEdGdGNEbzZaR0YwWlNBOUlDQW5NakF5TkMwd055MHlOaWNnSUVkU1QxVlFJRUpaSURFZ1QxSkVSVklnUWxrZ01TQkJVME0KU0VMRUNUCiAgZGF5LAogIGF2Z01lcmdlKGF2Z19mZWVfc29sKSBhcyBhdmcsCiAgc3VtTWVyZ2UoZmVlX3NvbCkgYXMgZmVlX3NvbApGUk9NCiAgc29sYW5hLmRhaWx5X2ZlZXNfYnlfZGF5IFdIRVJFIGRheSA-IHRvZGF5KCkgLSBJTlRFUlZBTCAxIE1PTlRICkdST1VQIEJZCiAgZGF5Ck9SREVSIEJZCiAgZGF5IERFU0M) that exploits a Materialized View:

<pre style="font-size: 14px;"><code class="hljs language-sql"><span class="hljs-keyword">SELECT</span> <span class="hljs-keyword">day</span>,
	avgMerge(avg_fee_sol) <span class="hljs-keyword">AS</span> avg,
	sumMerge(fee_sol) <span class="hljs-keyword">AS</span> fee_sol
<span class="hljs-keyword">FROM</span> solana.daily_fees_by_day
<span class="hljs-keyword">WHERE</span> <span class="hljs-keyword">day</span> <span class="hljs-operator">&gt;</span> today() <span class="hljs-operator">-</span> <span class="hljs-type">INTERVAL</span> <span class="hljs-number">1</span> <span class="hljs-keyword">MONTH</span>
<span class="hljs-keyword">GROUP</span> <span class="hljs-keyword">BY</span> <span class="hljs-keyword">day</span>
<span class="hljs-keyword">ORDER</span> <span class="hljs-keyword">BY</span> <span class="hljs-keyword">day</span> <span class="hljs-keyword">DESC</span>

<span class="hljs-number">31</span> <span class="hljs-keyword">rows</span> <span class="hljs-keyword">in</span> set. Elapsed: <span class="hljs-number">0.007</span> sec. Processed <span class="hljs-number">1.38</span> thousand <span class="hljs-keyword">rows</span>, <span class="hljs-number">60.54</span> KB (<span class="hljs-number">184.41</span> thousand <span class="hljs-keyword">rows</span><span class="hljs-operator">/</span>s., <span class="hljs-number">8.11</span> MB<span class="hljs-operator">/</span>s.)
Peak memory usage: <span class="hljs-number">4.88</span> MiB.
</code></pre>

This completes in 0.007s. Note that the view aggregates by day, so for queries that require more granular statistics, e.g., by the hour for a specific day, we suggest using the source table `solana.transactions_non_voting`.

The current views were developed in collaboration with the [Solana Foundation](https://solana.org/) and optimized during testing. If users find a query which hits quota limits that they believe the community would benefit from, simply raise an issue in the project repository [here](https://github.com/ClickHouse/CryptoHouse). We can create the view and backfill the data as required. In future, we hope to automate this process and expose a build system that allows users to simply raise a view proposal or example query as a PR.

### Deduplicating data

To deliver events efficiently, Goldsky offers at least one semantics. This means that while we are guaranteed to receive all data that occurs on a chain, we may, under rare circumstances, receive an event more than once. To address this, our tables use a[ ReplacingMergeTree engine](https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/replacingmergetree).

![replacingMergeTree.png](https://clickhouse.com/uploads/replacing_Merge_Tree_620ff642aa.png)

This engine type deduplicates events with the same values for the tables ordering key (in most cases, this is the `block_timestamp` and `slot`). This deduplication process occurs asynchronously in the background and is eventually consistent. While results may be slightly inaccurate for a period if duplicate events are inserted, given the large number of rows and the tiny percentage of duplicates, we expect this to be rarely an issue, with most queries not requiring row-level accuracy. For more details on how the ReplacingMergeTree works, see [here](https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/replacingmergetree).

### Using ClickHouse Cloud 

The instance used to power the service is hosted in ClickHouse Cloud. This provides several benefits, not least the separation of storage and compute. With only one copy of the data stored in object storage, we can scale CPU and memory independently based on user demand. If we see higher user demand for this service, we can simply add more nodes - no resharding or redistribution of the data is required. As well as simplifying operations, using object storage means we can both scale infinitely (effectively) and deliver this service cost-effectively.

![storage_and_compute.png](https://clickhouse.com/uploads/storage_and_compute_855fb7afc0.png)

Finally, we exploit the [ClickHouse query cache](https://clickhouse.com/docs/en/operations/query-cache), which was added to open-source earlier this year.

## Building a UI

With the data engineering and ClickHouse challenges addressed, we wanted to provide a service users loved using, so we exposed a simple UI that allows users to write and share queries.

<a href="/uploads/cryptohouse_9af043ee72.gif" target="_blank"><img src="/uploads/cryptohouse_9af043ee72.gif"/></a>

Appreciating that users often need to visualize results, this UI also supports simple multi-dimensional charting, powered by e-charts. 

<a href="/uploads/cryptohouse_v2_4ce990d368.gif" target="_blank"><img src="/uploads/cryptohouse_v2_4ce990d368.gif"/></a>

Note that users can save their queries alongside the examples provided. However, these are not persisted in the service and only exist in the browser store.

## Tips on querying

To avoid hitting quota limits, we recommend users:

* **Use Materialized Views**. These deliberately shift computation to insert time, minimizing the number of rows user queries need to read. Many of these use AggregateFunction types, which store the intermediate result from an aggregation. This requires the use of a -Merge function when querying e.g. here. 
* **Use date filters on main tables** - The Materialized Views aggregate by day. For more granular analysis, refer to the base tables e.g., transactions. These tables contain every event and are, as a result, hundreds of billions of rows. When querying these rows, always apply a date filter to avoid exceeding a month's timespan.

## If users want more…

While we have attempted to be as generous as possible with quotas, we expect some users will want to run queries requiring more computational power than CryptoHouse offers. CryptoHouse is intended for community usage and not for organizations looking to build a service or commercial offering, so higher volumes of queries are not supported. 

If you need higher quotas or need to issue more queries for these purposes, we recommend [contacting Goldsky](https://goldsky.com/pricing), who can provide the data in a dedicated ClickHouse instance. This can also be tuned to your access patterns and requirements, delivering superior performance and lower latency queries.

## Conclusion

We’re delighted to announce that CryptoHouse is now available for our users and the crypto community. This blog post covers some of the technical details. 

For readers interested in more details, we’ll deliver a developer-focused session with Goldsky at [Solana breakpoint in September](https://solana.com/breakpoint), covering the service's internals and the challenges encountered.

We welcome users to raise issues and discussions in the [public repository](https://github.com/ClickHouse/CryptoHouse).




