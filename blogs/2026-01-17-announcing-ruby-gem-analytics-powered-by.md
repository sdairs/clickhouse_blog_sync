---
title: "Announcing Ruby Gem analytics powered by ClickHouse and Ruby Central"
date: "2025-04-11T10:11:34.264Z"
author: "The ClickHouse & Ruby Central teams"
category: "Engineering"
excerpt: "In partnership with Ruby Central, we’re excited to announce that all RubyGems download data - over 180 billion rows - is now free to query at sql.clickhouse.com; explore trends, analyze usage, and unlock insights into the Ruby ecosystem!"
---

# Announcing Ruby Gem analytics powered by ClickHouse and Ruby Central

*RubyGems analytics are now available on [ClickGems](https://clickgems.clickhouse.com/). Learn more in the [announcement blog](https://clickhouse.com/blog/announcing-clickgems).*

![Blog_RubyGemsLaunch_202504_V2.0.png](https://clickhouse.com/uploads/Blog_Ruby_Gems_Launch_202504_V2_0_0fc2c42e41.png)

Ruby developers, we have exciting news! Following the tremendous success of ClickPy for the Python community, we're thrilled to introduce free Ruby gem analytics via [sql.clickhouse.com](https://sql.clickhouse.com/?query_id=HVMKR3JXFT4DA8NMAPGXKM&chart=eyJ0eXBlIjoibGluZSIsImNvbmZpZyI6eyJ0aXRsZSI6IkdlbSBkb3dubG9hZHMgb3ZlciB0aW1lIiwieGF4aXMiOiJkYXRlIiwieWF4aXMiOiJ0b3RhbF9kb3dubG9hZHMifX0) in partnership with Ruby Central. This allows the Ruby community to do Gem analytics on all downloads since 2017 using just SQL - over 180 billion rows!

<pre><code show_statistics='true' view='chart' show_line_numbers='false' type='click-ui' language='sql' play_link='https://sql.clickhouse.com/?query=U0VMRUNUIHRvU3RhcnRPZk1vbnRoKGRhdGUpIGFzIG1vbnRoLCBzdW0oY291bnQpIGFzIHRvdGFsX2Rvd25sb2FkcyAKRlJPTSBydWJ5Z2Vtcy5kb3dubG9hZHNfcGVyX2RheSAKR1JPVVAgQlkgbW9udGggCk9SREVSIEJZIG1vbnRoIEFTQw&chart=eyJ0eXBlIjoibGluZSIsImNvbmZpZyI6eyJ0aXRsZSI6IlRvdGFsIFJ1YnkgZG93bmxvYWRzIG92ZXIgdGltZSIsInhheGlzIjoibW9udGgiLCJ5YXhpcyI6InRvdGFsX2Rvd25sb2FkcyJ9fQ' runnable='true' chart_config='eyJ0eXBlIjoibGluZSIsImNvbmZpZyI6eyJ0aXRsZSI6IlRvdGFsIFJ1YnkgZG93bmxvYWRzIG92ZXIgdGltZSIsInhheGlzIjoibW9udGgiLCJ5YXhpcyI6InRvdGFsX2Rvd25sb2FkcyJ9fQ'>
SELECT toStartOfMonth(date) as month, sum(count) as total_downloads 
FROM rubygems.downloads_per_day 
GROUP BY month 
ORDER BY month ASC
</code></pre>

If you're interested in how this service came about, read on, otherwise skip straight to the [example queries](/blog/announcing-ruby-gem-analytics-powered-by-clickhouse#example-queries) below, or head over to the [public service](https://sql.clickhouse.com/?query_id=HVMKR3JXFT4DA8NMAPGXKM&chart=eyJ0eXBlIjoibGluZSIsImNvbmZpZyI6eyJ0aXRsZSI6IkdlbSBkb3dubG9hZHMgb3ZlciB0aW1lIiwieGF4aXMiOiJkYXRlIiwieWF4aXMiOiJ0b3RhbF9kb3dubG9hZHMifX0).

## It all started with Python

![clickpy (2).png](https://clickhouse.com/uploads/clickpy_2_eca9a343e8.png)

In early 2024, we launched [ClickPy](https://clickpy.clickhouse.com), a simple app that provides analytics on Python package downloads. The dataset behind ClickPy logs every Python package download via the PyPI repository - every time a developer runs `pip install`, a row is added to ClickHouse.

Within just nine months, the [dataset surpassed 1 trillion rows](https://clickhouse.com/blog/clickpy-one-trillion-rows), with the total number of unique downloads now [exceeding 1.43 trillion](https://sql.clickhouse.com/?query=U0VMRUNUIGZvcm1hdFJlYWRhYmxlUXVhbnRpdHkoY291bnQoKSkgRlJPTSBweXBpLnB5cGkg&run_query=true) and growing by [over 2 billion rows per day](https://sql.clickhouse.com/?query=U0VMRUNUIGRhdGUsIGZvcm1hdFJlYWRhYmxlUXVhbnRpdHkoc3VtKGNvdW50KSkgQVMgdG90YWwgRlJPTSBweXBpLnB5cGlfZG93bmxvYWRzX3Blcl9kYXkgV0hFUkUgZGF0ZSA-IHRvZGF5KCkgLSBJTlRFUlZBTCAxIFdFRUsgR1JPVVAgQlkgZGF0ZSBPUkRFUiBCWSBkYXRlIEFTQw).

<pre><code show_statistics='true'  show_line_numbers='false' type='click-ui' language='sql' play_link='https://sql.clickhouse.com/?query=U0VMRUNUIGZvcm1hdFJlYWRhYmxlUXVhbnRpdHkoY291bnQoKSkgYXMgbnVtYmVyX3Jvd3MgRlJPTSBweXBpLnB5cGk&chart=eyJ0eXBlIjoibGluZSIsImNvbmZpZyI6eyJ4YXhpcyI6InllYXIiLCJ5YXhpcyI6Ijk5dGhfYXZnX3RlbXAiLCJzZXJpZXMiOiJjb3VudHJ5IiwidGl0bGUiOiJUZW1wZXJhdHVyZSBieSBjb3VudHJ5IGFuZCB5ZWFyIn19' runnable='true' >
SELECT formatReadableQuantity(count()) as number_rows FROM pypi.pypi
</code></pre>

<pre><code  show_statistics='true'  show_line_numbers='false' chart_config='eyJ0eXBlIjoibGluZSIsImNvbmZpZyI6eyJ4YXhpcyI6ImRhdGUiLCJ5YXhpcyI6InRvdGFsIiwic2VyaWVzIjoiY291bnRyeSIsInRpdGxlIjoiUHl0aG9uIGRvd25sb2FkcyBvdmVyIHRpbWUifX0' type='click-ui' view='chart' language='sql' play_link='https://sql.clickhouse.com/?query=U0VMRUNUIGRhdGUsIHN1bShjb3VudCkgQVMgdG90YWwgCkZST00gcHlwaS5weXBpX2Rvd25sb2Fkc19wZXJfZGF5CkdST1VQIEJZIGRhdGUgCk9SREVSIEJZIGRhdGUgQVND&chart=eyJ0eXBlIjoibGluZSIsImNvbmZpZyI6eyJ4YXhpcyI6ImRhdGUiLCJ5YXhpcyI6InRvdGFsIiwic2VyaWVzIjoiY291bnRyeSIsInRpdGxlIjoiUHl0aG9uIGRvd25sb2FkcyBvdmVyIHRpbWUifX0' runnable='true' >
SELECT date, sum(count) AS total 
FROM pypi.pypi_downloads_per_day
GROUP BY date 
ORDER BY date ASC
</code></pre>

In addition to the web interface, package maintainers and enthusiasts can query the dataset directly via [sql.clickhouse.com](https://sql.clickhouse.com/?query_id=FSGUF4Z8QW3F1PQGGQFRXN) using just SQL. This free service has proven incredibly popular, now serving **over half a million queries each month**! (the above example queries actually use this service).

<blockquote>
<p style="font-size: 15px;">For those curious, <a href="https://clickhouse.com/blog/clickpy-one-trillion-rows">we’ve blogged </a>and <a href="https://github.com/ClickHouse/clickpy?tab=readme-ov-file#how-is-this-all-soo-fast-whats-the-secret-sauce">documented how ClickPy works</a>, including the ClickHouse features it leverages to deliver millisecond-level performance - even on datasets with over a trillion rows - and how we maintain a stable publicly available service that users can use fairly.</p>
</blockquote>

## Welcome Ruby Central

At ClickHouse, we love large datasets. So when [Marty Haught](https://www.linkedin.com/in/martyhaught) from [Ruby Central](https://rubycentral.org/) reached out to ask if we could offer a similar service for the Ruby community, we were thrilled:

<blockquote>
<p>Hi Dale,</p>
<p>Several members of the RubyGems team were marveling at the ClickPy site and wondered if we could do something similar for RubyGems.  Do you know if ClickHouse is receptive to hosting analytics for OSS package repositories?</p>
<p>Thanks,
Marty
</p>
</blockquote>

In addition to the PyPI dataset, sql.clickhouse.com hosts over 35 public datasets, all documented and available to query for free. The opportunity to host another package dataset- especially one that’s valuable to the open source community, technically interesting, and large - was too good to pass up.

A quick call with Marty and [Samuel Giddens](https://segiddins.me/) from the Ruby Central team confirmed that, perhaps unsurprisingly, the structure of the RubyGems data is very similar to the PyPI data.

## Ruby datasets

[Ruby Central](https://rubycentral.org/) is a nonprofit organization that supports the Ruby language and its ecosystem. Among other things, they maintain the RubyGems package repository and the `gem` command-line tool - essential infrastructure for the Ruby community.

If you've ever installed a Ruby package (or "gem"), you've used RubyGems. Much like pip for Python, Ruby developers install packages with a simple command - `gem install rails`.

Behind the scenes, this triggers a request to RubyGems.org, Ruby Central's central package registry. Every time a developer installs a gem, metadata such as the package name, version, platform, and timestamp gets logged.

This produces a few interesting datasets.

### Download logs

Each row includes the timestamp, package name and version, platform details, and extensive metadata about the client environment, such as the Ruby version, operating system, whether the download was triggered by Bundler or CI, and geolocation data like country and city. It also captures technical details of the request and response, including TLS versions, HTTP status codes, response times, and caching behavior. This makes it ideal for exploring download trends, adoption patterns, and usage contexts across the Ruby ecosystem.

As well as being the largest dataset at over 180 billion rows (as of April 2025), with data available from 2017, the download logs were also the one we aspired to maintain as up-to-date as possible. Given the size of this dataset, Ruby Central offered to provide this via a GCS bucket in gzip compressed NDJSON format, with files delivered every hour.

### Daily aggregate downloads

Ruby Central also [publishes a pre-aggregated dataset ](https://github.com/segiddins/gem-daily-downloads)with daily statistics for each gem. Each row includes the package name, the date, the number of downloads that occurred on that day (`daily_downloads`), and the cumulative total up to that point (`total_downloads`). This dataset is periodically updated and can be [downloaded from github](https://github.com/segiddins/gem-daily-downloads). While not having the granularity and breadth of metadata as the above dataset, this pre-aggregated version is useful for quick analysis, making it easy to analyze trends over time without scanning raw download logs.

<blockquote style="font-size: 15px;">
<p>Experienced ClickHouse users may be wondering why we need this dataset if we have the raw data? Although it's true, we can generate aggregate daily downloads using a materialized view natively in ClickHouse (see below) or even just group by day in a query, these aggregate statistics go back to 2013 and are thus useful.</p>
</blockquote>

### Weekly data dumps

Ruby Central also [publishes weekly exports of gem metadata to GitHub](https://github.com/segiddins/rubygems-org-db-dumps), similar in spirit to the project metadata datasets available for PyPI. These provide a richer view of the Ruby ecosystem beyond just download counts:

* **attestations** – contains signed metadata for specific gem versions, including SBOMs and security attestations, stored as JSON blobs.
* **deletions** – tracks removed gem versions, recording the gem name, version, platform, and the user who deleted it.
* **dependencies** – captures declared gem dependencies along with their version requirements and scopes (e.g. runtime or development).
* **gem_downloads** – stores the total download count for each gem version, enabling point-in-time snapshots of popularity.
* **linksets** – includes links associated with each gem, such as homepage, documentation, source code, and issue tracker URLs.
* **rubygems** – the master list of all gems, with basic metadata including name, creation date, and organization info.
* **versions** – detailed records of every published gem version, including authors, descriptions, licenses, requirements, checksums, and whether it has been yanked.

These datasets make it easy to analyze package metadata, dependencies, and trends over time - powering everything from dashboards to supply chain insights.

The latter of these two datasets are usually updated weekly in github. While the daily aggregate downloads datasets are updated incrementally with new files added for the last 7 days, the weekly data dump tables are all updated with the current files replaced.

Additionally, we want to make sure all loading was performed using ClickHouse native constructs - minimizing the need for ingestion logic and processing.

## Loading the data

### Download logs

Despite being the largest dataset, the download logs are actually the simplest to load. The schema for this dataset is shown below:

<pre><code type='click-ui' language='sql' show_line_numbers='false'>
CREATE TABLE rubygems.downloads
(
	`timestamp` DateTime,
	`request_path` String,
	`request_query` String,
	`user_agent` Tuple(
    	agent_name String,
    	agent_version String,
    	bundler String,
    	ci String,
    	command String,
    	jruby String,
    	options String,
    	platform Tuple(
        	cpu String,
        	os String,
        	version String),
    	ruby String,
    	rubygems String,
    	truffleruby String),
	`tls_cipher` String,
	`time_elapsed` Int64,
	`client_continent` String,
	`client_country` String,
	`client_region` String,
	`client_city` String,
	`client_latitude` String,
	`client_longitude` String,
	`client_timezone` String,
	`client_connection` String,
	`request` String,
	`request_host` String,
	`request_bytes` Int64,
	`http2` Bool,
	`tls` Bool,
	`tls_version` String,
	`response_status` Int64,
	`response_text` String,
	`response_bytes` Int64,
	`response_cache` String,
	`cache_state` String,
	`cache_lastuse` Float64,
	`cache_hits` Int64,
	`server_region` String,
	`server_datacenter` String,
	`gem` String,
	`version` String,
	`platform` String
)
ENGINE = MergeTree
ORDER BY (gem, toDate(timestamp))
</code></pre>

Ruby Central pushes these logs as compressed JSON to a GCS bucket. ClickHouse has native support for reading both JSON and gzip files from GCS. We could, for example, query these files in place:

<pre><code type='click-ui' language='sql' show_line_numbers='false'>
SELECT
  toStartOfMonth(timestamp) AS month,
  count()
FROM gcs('https://storage.googleapis.com/clickhouse-rubygems/backfill/2017//**/*.json.gz', '<HIDDEN>', '<HIDDEN>')
GROUP BY month
ORDER BY month DESC
LIMIT 12

┌──────month─┬───count()─┐
│ 2017-12-01 │ 662622048 │
│ 2017-11-01 │ 716549049 │
│ 2017-10-01 │ 693602509 │
│ 2017-09-01 │ 686176096 │
│ 2017-08-01 │ 608606033 │
│ 2017-07-01 │ 556639959 │
│ 2017-06-01 │ 487825551 │
└────────────┴───────────┘

7 rows in set. Elapsed: 252.989 sec. Processed 4.41 billion rows, 236.12 GB (17.44 million rows/s., 933.34 MB/s.)
Peak memory usage: 902.94 MiB.
</code></pre>

To load the historical data into ClickHouse, we simply imported using an `INSERT INTO SELECT`. For example, the following query imports the entirety of 2018 (around 10 billion rows from 120k files totaling 530GB of compressed JSON) in ~ 20 minutes.

<pre><code type='click-ui' language='sql' show_line_numbers='false'>
INSERT INTO rubygems.downloads_2018
FROM s3Cluster('default', 'https://storage.googleapis.com/clickhouse-rubygems/backfill/2018/**/*.json.gz', '<HIDDEN>', '<HIDDEN>')
SETTINGS max_insert_threads = 16, min_insert_block_size_rows = 0, min_insert_block_size_bytes = 2083333333, parallel_distributed_insert_select = 2

0 rows in set. Elapsed: 1317.014 sec. Processed 10.14 billion rows, 562.52 GB (7.70 million rows/s., 427.12 MB/s.)
Peak memory usage: 47.25 GiB.
</code></pre>

<blockquote style="font-size: 15px;">
<p>You may notice we have tuned the settings for this query. These settings assign more resources to the import and parallelize the insert across all nodes (<a href="https://clickhouse.com/docs/operations/settings/settings#parallel_distributed_insert_select"><code class="undefined mb-9 border border-solid border-c3" style="word-break:break-word">parallel_distributed_insert_select = 2</code></a>), with the aim of minimizing the load time. For more information on how to tune similar imports, we recommend the guide <a href="https://clickhouse.com/docs/integrations/s3/performance">"Optimizing for S3 Insert and Read Performance"</a>.</p>
</blockquote>

While this addresses the historical backfill, to consume new files and insert them into ClickHouse, we use the [S3Queue table engine](https://clickhouse.com/docs/engines/table-engines/integrations/s3queue). 

<iframe width="768" height="432" src="https://www.youtube.com/embed/lnbWFjfZxZ4?si=jhxMQxvhk4719HxX" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
<br/>

This table engine allows the streaming consumption of data from S3 (compatible with GCS). As files are added to a bucket (hourly), ClickHouse will automatically process these files and insert them into a designated table. With this capability, users can set up simple incremental pipelines with no additional code.

<img preview="/uploads/s3_queue_1280_9753b7d95a.gif"  src="/uploads/s3_queue_4b0b6ca7cb.gif" alt="catalogue_lakehouse.png" class="h-auto w-auto max-w-full"  style="width: 100%;">

The engine works by periodically polling the bucket and tracking the files present, storing the state in a ClickHouse Keeper node. By default, the list of files retrieved on each poll is compared against the stored list to identify new files. The diagram above shows how a new file is processed (and added to Keeper) and inserted into the queue table. While this doesn’t store the data itself, [incremental materialized views](https://clickhouse.com/docs/materialized-view/incremental-materialized-view) can subscribe and transform rows before inserting them into a table for querying.

To create our pipeline we need only two DDL commands - one to create the queue, the second to create the incremental materialized view which subscribes to the changes and pushes the results to our above downloads table.

<pre><code type='click-ui' language='sql' show_line_numbers='false'>
CREATE TABLE rubygems.downloads_queue_2025_04_01
(
	`timestamp` DateTime,
	`request_path` String,
	`request_query` String,
    ...
	`gem` String,
	`version` String,
	`platform` String
)
ENGINE = S3Queue('https://storage.googleapis.com/clickhouse-rubygems/incremental/**/*.json.gz', '<HIDDEN>', '[HIDDEN]', 'JSONEachRow', 'gzip')
SETTINGS mode = 'ordered', s3queue_polling_min_timeout_ms='6000', s3queue_polling_max_timeout_ms='9000', s3queue_buckets = 30, s3queue_processing_threads_num = 10;
</code></pre>

<pre><code type='click-ui' language='sql' show_line_numbers='false'>

CREATE MATERIALIZED VIEW rubygems.downloads_2025_04_01_mv TO rubygems.downloads
AS SELECT *
FROM rubygems.downloads_queue_2025_04_01
</code></pre>

A few important notes:

* The files themselves have no natural order in their naming (within an hour). We, therefore, use the S3queue engine in `unordered` mode. This requires the table engine to track all files (in Keeper) vs exploiting a natural ordering (`ordered mode`). 

  Use of ordered mode requires a guarantee that the files are delivered in order. This mode works by maintaining a cursor of the highest lexicographical name, using this to identify new files on each iteration. Should files be delivered out of order, it can therefore potentially miss files. The current export logic of the files does not currently provide such guarantees - hence the use of `unordered` mode.

  While the ordered mode is more efficient for import (tracking only the last-seen file), it places additional constraints on how files are exported. Given the volume (almost 200 billion rows), the Ruby Central team wanted to ensure any export was performed in parallel. This makes ordering impractical: they receive one file per Fastly region per hour, and each arrival triggers a Lambda function that processes the file independently. These Lambda invocations happen concurrently, and there's no reliable or desirable way to serialize their delivery. 

  Given the possible out-of-order delivery, we thus use unordered mode with S3Queue.

* We create a new S3Queue and materialized view each day, also dropping the queue and view from the 2 days ago. This ensures each queue doesn't need to track an excessive number of files (less than a 1000). Each day's queue also thus has a 48 hour gratuitous period, in case files are delivered late. 
* We adjust the queue defaults, increasing the minimum and maximum polling time as well as increasing the number of tracked files to 2000.
* Note the pattern `**/*.json.gz` provides recursive processing of files.
* Our [sql.clickhouse.com](http://sql.clickhouse.com) environment into which we are loading this data has three nodes, each with 60 vCPUs. The setting `s3queue_processing_threads_num` assigns the number of threads for file processing per server. In addition, the ordered mode also introduces the setting `s3queue_buckets`.[ As recommended](https://clickhouse.com/docs/en/engines/table-engines/integrations/s3queue#ordered-mode), we set this to equal a multiplication of the number of replicas (3) by the number of processing threads (10).

With this in place, the data started to flow in. An example query exploring downloads per hour for the [bundler gem](https://rubygems.org/gems/bundler):

<pre><code type='click-ui' show_statistics='true'  language='sql' show_line_numbers='false' play_link='https://sql.clickhouse.com/?query=U0VMRUNUCgl0b1N0YXJ0T2ZIb3VyKHRpbWVzdGFtcCkgQVMgaG91ciwKCWNvdW50KCkKRlJPTSBydWJ5Z2Vtcy5kb3dubG9hZHMKV0hFUkUgZ2VtID0gJ2J1bmRsZXInIEFORCB0aW1lc3RhbXAgPiB0b2RheSgpIC0gSU5URVJWQUwgMSBXRUVLCkdST1VQIEJZIGhvdXIKT1JERVIgQlkgaG91ciBBU0M' runnable='true'>
SELECT
	toStartOfHour(timestamp) AS hour,
	count()
FROM rubygems.downloads
WHERE gem = 'bundler' AND timestamp > today() - INTERVAL 1 WEEK
GROUP BY hour
ORDER BY hour ASC
</code></pre>

With all data loaded from 2017, this dataset totals around 180 billion rows, compressing from around 9.5 TB of Gzipped JSON (160 TB uncompressed) to less than 5 TB in ClickHouse:

<pre><code type='click-ui' show_statistics='true'  language='sql' show_line_numbers='false' play_link='https://sql.clickhouse.com/?query=U0VMRUNUCiAgIGB0YWJsZWAsCiAgIGZvcm1hdFJlYWRhYmxlU2l6ZShzdW0oZGF0YV9jb21wcmVzc2VkX2J5dGVzKSkgQVMgdG90YWxfc2l6ZQpGUk9NIHN5c3RlbS5jb2x1bW5zCldIRVJFIChkYXRhYmFzZSA9ICdydWJ5Z2VtcycpIEFORCAoYHRhYmxlYCA9ICdkb3dubG9hZHMnKQpHUk9VUCBCWSBgdGFibGVgCk9SREVSIEJZIHN1bShkYXRhX2NvbXByZXNzZWRfYnl0ZXMpIERFU0M' runnable='true'>
SELECT
   `table`,
   formatReadableSize(sum(data_compressed_bytes)) AS total_size
FROM system.columns
WHERE (database = 'rubygems') AND (`table` = 'downloads')
GROUP BY `table`
ORDER BY sum(data_compressed_bytes) DESC
</code></pre>

### Daily aggregate downloads

Our second dataset is hosted in github and updated periodically (approximately weekly). 

To backfill this data, we simply cloned the repo and ran the following command, using clickhouse-local to parse the files and insert them into our Cloud instance:

<pre><code type='click-ui' language='bash' show_line_numbers='false'>
clickhouse local --query "SELECT replaceOne( _file, '.csv','')::Date as date, * FROM file('/data/rubygems/gem-daily-downloads/**/*.csv') FORMAT Native" | clickhouse client --host sql-clickhouse.clickhouse.com --secure --password <PASSWORD> --query "INSERT INTO rubygems.daily_downloads FORMAT Native"
</code></pre>

To incrementally update this dataset, we use a simple script.

[This bash script](https://pastila.nl/?00055456/4a1fc7fff4a462817198cb08730d3d96#HOieFBEhqSsNQsTVzQr+Pg==) incrementally updates the daily aggregate downloads dataset by querying ClickHouse for the latest date already ingested, then downloading any missing CSV files from the[ RubyGems GitHub repository](https://github.com/segiddins/gem-daily-downloads). It loops through each subsequent day, checks if a file exists, and if so, ingests it using native ClickHouse commands. This ensures the dataset stays up-to-date with minimal logic and no need for external orchestration.

Unlike the download logs, which are streamed via GCS and the S3Queue engine, this dataset is smaller, pre-aggregated, and only updated weekly - making it ideal for a simple pull-and-load pattern. By combining ClickHouse’s ability to query remote files and ingest them in place, the script keeps things lightweight while ensuring continuity in the public dataset hosted at [sql.clickhouse.com](https://sql.clickhouse.com).

We run this script in [Google Cloud Run](https://cloud.google.com/run?hl=en). 

**This dataset is around 600m rows as of April 2025.**

### Weekly data dumps

The weekly data dumps are also held in Github but are updated in their entirety i.e. all files are replaced for each update. All files belonging to a dataset can be found in a single folder e.g. the [full list of Ruby Gems and their metadata](https://github.com/segiddins/rubygems-org-db-dumps/tree/main/tables/rubygems).

This makes the files easy to consume. We simply use a [refreshable materialized view](https://clickhouse.com/docs/materialized-view/refreshable-materialized-view), which periodically executes an import query - sending the results to a target table. This same approach can be used for both the initial and incremental load.

![refreshable-mv-simple.gif](https://clickhouse.com/uploads/refreshable_mv_simple_099e709037.gif)

For example, the following refreshable materialized view executes once a week reading the Ruby Gems package files from a [github folder](https://raw.githubusercontent.com/segiddins/rubygems-org-db-dumps/refs/heads/main/tables/rubygems/part_{0..100}.csv) using the [url function](https://clickhouse.com/docs/sql-reference/table-functions/url).

<pre><code type='click-ui' language='sql' show_line_numbers='false'>
CREATE MATERIALIZED VIEW rubygems.rubygems_mv
REFRESH EVERY 1 WEEK APPEND TO rubygems.rubygems
(
	`id` UInt32,
	`name` String,
	`created_at` DateTime64(6),
	`updated_at` DateTime64(6),
	`indexed` LowCardinality(String),
	`organization_id` LowCardinality(String)
)
AS SELECT *
FROM url('https://raw.githubusercontent.com/segiddins/rubygems-org-db-dumps/refs/heads/main/tables/rubygems/part_{0..100}.csv', 'CSVWithNames')
</code></pre>

This view sends the data to the `rubygems.rubygems` table:

<pre><code type='click-ui' language='sql' show_line_numbers='false'>
CREATE TABLE rubygems.rubygems
(
	`id` UInt32,
	`name` String,
	`created_at` DateTime64(6),
	`updated_at` DateTime64(6),
	`indexed` LowCardinality(String),
	`organization_id` LowCardinality(String)
)
ENGINE = ReplacingMergeTree
ORDER BY (name, id)
</code></pre>

<blockquote style="font-size: 15px;">
<p>Users wanting to load this data, and any of the other tables in the weekly data dumps, into their own ClickHouse instance could simply create the above table and run <code class="undefined mb-9 border border-solid border-c3" style="word-break:break-word">INSERT INTO SELECT * FROM url('https://raw.githubusercontent.com/segiddins/rubygems-org-db-dumps/refs/heads/main/tables/rubygems/part_{0..100}.csv', 'CSVWithNames')</code>. For other table schemas, check out this <a href="https://sql.clickhouse.com/?query=U0hPVyBDUkVBVEUgVEFCTEUgcnVieWdlbXMudmVyc2lvbnM">sql.clickhouse.com query</a>.</p>
</blockquote>

There are a few important notes with respect to this view and sorting key.

The view uses the clause `APPEND`. This means all rows are **appended** to the target table `rubygems.rubygems` vs. the default strategy of replacement.

The above policy means the Ruby Gems data will contain duplicates. To address this, we use a ReplacingMergeTree, which de-duplicates data based on unique values of the ordering key (`name` and `id` in the above case - these uniquely identify a package). This deduplication process is eventual with duplicates removed through a background merge process.

To address this we can either use the `FINAL` keyword when querying these tables, which removes any outstanding duplicates at query time, or ensure we aggregate by the ordering keys. The overhead here is expected to be negligible as the volume of data is low ~ millions.

Note that these tables are all relatively small (for ClickHouse), with them predominantly providing metadata. As we demonstrate below, this can be useful for joining the data with other datasets:

<pre><code type='click-ui' language='sql' show_statistics='true'  show_line_numbers='false' play_link='https://sql.clickhouse.com/?query=U0VMRUNUCgluYW1lLAoJZm9ybWF0UmVhZGFibGVRdWFudGl0eSh0b3RhbF9yb3dzKSBBUyB0b3RhbF9yb3dzLAoJZm9ybWF0UmVhZGFibGVTaXplKHRvdGFsX2J5dGVzX3VuY29tcHJlc3NlZCkgQVMgdG90YWxfc2l6ZQpGUk9NIHN5c3RlbS50YWJsZXMKV0hFUkUgKGRhdGFiYXNlID0gJ3J1YnlnZW1zJykgQU5EIChlbmdpbmUgTElLRSAnJVJlcGxhY2luZ01lcmdlVHJlZScp' runnable='true'>
SELECT
	name,
	formatReadableQuantity(total_rows) AS total_rows,
	formatReadableSize(total_bytes_uncompressed) AS total_size
FROM system.tables
WHERE (database = 'rubygems') AND (engine LIKE '%ReplacingMergeTree')
</code></pre>

## Materialized views

Similar to ClickPy we wanted to create incremental materialized views to accelerate common queries for users.

In its simplest form, an incremental materialized view is simply a query that triggers when an insert is made to a table.

Key to this is the idea that Materialized views don't hold any data themselves. They simply execute a query on the inserted rows and send the results to another "target table" for storage.

Importantly, the query that runs can aggregate the rows into a smaller result set, allowing queries to run faster on the target table. This approach effectively moves work from **query time to insert time**.

<iframe width="768" height="432" src="https://www.youtube.com/embed/QUigKP7iy7Y?si=5NgO8Sb4wY-ryK2Q" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
<p></p>
As an example, we can recreate our daily aggregate downloads using the data from our raw download logs.
<p></p>
<blockquote style="font-size: 15px;">
<p>The main motivation here is that the aggregate logs are actually estimates and updated weekly, whereas the results from our materialized view will be precise and updated hourly. This also represents a simple example :)&nbsp;</p>
</blockquote>

<pre><code type='click-ui' language='sql' show_line_numbers='false'>
CREATE MATERIALIZED VIEW rubygems.downloads_per_day_mv TO rubygems.downloads_per_day
AS SELECT
	toDate(timestamp) AS date,
	gem,
	count() AS count
FROM rubygems.downloads
GROUP BY
	date,
	gem
</code></pre>

This view executes the aggregation below on blocks of data as they are inserted into the `downloads` table. 

<pre><code type='click-ui' language='sql' show_line_numbers='false'>
SELECT
	toDate(timestamp) AS date,
	gem,
	count() AS count
FROM rubygems.downloads
GROUP BY
	date,
	gem
</code></pre>

The result is sent to the "target table" `rubygems.downloads_per_day`. This, in turn, has a special engine configuration:

<pre><code type='click-ui' language='sql' show_line_numbers='false'>
CREATE TABLE rubygems.downloads_per_day
(
	`date` Date,
	`gem` String,
	`count` UInt64
)
ENGINE = SummingMergeTree
ORDER BY (gem, date)
</code></pre>

The [SummingMergeTree](https://clickhouse.com/docs/engines/table-engines/mergetree-family/summingmergetree) replaces all the rows with the same `ORDER BY` key (gem and date in this case) with one row which contains summarized values for the columns with the numeric data type. Rows with the same project value will be asynchronously merged, and the count will be summed - hence "Summing." This summing behavior means it can be incrementally updated as new data arrives in the `downloads` table.

To show how this is useful, suppose we wished to look at the downloads per day for the bundler gem. Using the original `downloads` table:

<pre><code type='click-ui' show_statistics='true'  language='sql' show_line_numbers='false' show_line_numbers='false' play_link='https://sql.clickhouse.com/?query=U0VMRUNUIHRvRGF0ZSh0aW1lc3RhbXApIGFzIGRhdGUsIGNvdW50KCkgQVMgY291bnQKRlJPTSBydWJ5Z2Vtcy5kb3dubG9hZHMgV0hFUkUgZ2VtID0gJ2J1bmRsZXInCkdST1VQIEJZIGdlbSwgZGF0ZSBPUkRFUiBCWSBkYXRlIEFTQw&chart=eyJ0eXBlIjoiYXJlYSIsImNvbmZpZyI6eyJ0aXRsZSI6IkJ1bmRlciBkb3dubG9hZHMgb3ZlciB0aW1lIiwieGF4aXMiOiJkYXRlIiwieWF4aXMiOiJjb3VudCJ9fQ' runnable='true' view='chart' chart_config='eyJ0eXBlIjoiYXJlYSIsImNvbmZpZyI6eyJ0aXRsZSI6IkJ1bmRlciBkb3dubG9hZHMgb3ZlciB0aW1lIiwieGF4aXMiOiJkYXRlIiwieWF4aXMiOiJjb3VudCJ9fQ'>
SELECT toDate(timestamp) as date, count() AS count
FROM rubygems.downloads WHERE gem = 'bundler'
GROUP BY gem, date ORDER BY date ASC
</code></pre>

For most of you, this query probably took around 7-10s to run. Contrast with the equivalent query using the materialized view table `dowloads_per_day`:

<pre><code type='click-ui' language='sql' show_statistics='true' show_line_numbers='false' show_line_numbers='false' play_link='https://sql.clickhouse.com/?query=U0VMRUNUIGRhdGUsIHN1bShjb3VudCkgQVMgY291bnQKRlJPTSBydWJ5Z2Vtcy5kb3dubG9hZHNfcGVyX2RheSBXSEVSRSBnZW0gPSAnYnVuZGxlcicKR1JPVVAgQlkgZ2VtLCBkYXRlIE9SREVSIEJZIGRhdGUgQVND&chart=eyJ0eXBlIjoiYXJlYSIsImNvbmZpZyI6eyJ0aXRsZSI6IkJ1bmRlciBkb3dubG9hZHMgb3ZlciB0aW1lIiwieGF4aXMiOiJkYXRlIiwieWF4aXMiOiJjb3VudCJ9fQ' runnable='true' view='chart' chart_config='eyJ0eXBlIjoiYXJlYSIsImNvbmZpZyI6eyJ0aXRsZSI6IkJ1bmRlciBkb3dubG9hZHMgb3ZlciB0aW1lIiwieGF4aXMiOiJkYXRlIiwieWF4aXMiOiJjb3VudCJ9fQ'>
SELECT date, sum(count) AS count
FROM rubygems.downloads_per_day WHERE gem = 'bundler'
GROUP BY gem, date ORDER BY date ASC
</code></pre>

Just a little bit faster I'm sure! Welcome to the power of incremental materialized views - we’ve shifted the computation from query time to insert time.

We maintain a few other materialized views, we use in the queries below but plan to extend these over time and on request.

## Example queries

To get our users started we’ve assembled some example queries. These largely cover the queries used in ClickPy. Feel free to try any of the queries below or head over to [sql.clickhouse.com](https://sql.clickhouse.com/?query_id=HVMKR3JXFT4DA8NMAPGXKM&chart=eyJ0eXBlIjoibGluZSIsImNvbmZpZyI6eyJ0aXRsZSI6IkdlbSBkb3dubG9hZHMgb3ZlciB0aW1lIiwieGF4aXMiOiJkYXRlIiwieWF4aXMiOiJ0b3RhbF9kb3dubG9hZHMifX0) for the full catalog.

### Most downloaded gems

Using our above materialized view:

<pre><code type='click-ui' language='sql' show_statistics='true' show_line_numbers='false' show_line_numbers='false' play_link='https://sql.clickhouse.com/?query=U0VMRUNUCiAgIGdlbSwKICAgc3VtKGNvdW50KSBBUyB0b3RhbF9kb3dubG9hZHMKRlJPTSBydWJ5Z2Vtcy5kb3dubG9hZHNfcGVyX2RheQpHUk9VUCBCWSBnZW0KT1JERVIgQlkgdG90YWxfZG93bmxvYWRzIERFU0MKTElNSVQgNQ' runnable='true' view='table'>
SELECT
   gem,
   sum(count) AS total_downloads
FROM rubygems.downloads_per_day
GROUP BY gem
ORDER BY total_downloads DESC
LIMIT 5
</code></pre>

### Emerging gems

This query uses the materialized view [`gems_downloads_max_min`](https://sql.clickhouse.com/?query=U0hPVyBDUkVBVEUgVEFCTEUgcnVieWdlbXMuZ2Vtc19kb3dubG9hZHNfbWF4X21pbg) which mains the min and max date that a gem was downloaded.

<pre><code type='click-ui' language='sql' show_statistics='true' show_line_numbers='false' show_line_numbers='false' play_link='https://sql.clickhouse.com/?query=V0lUSCAoCiAgIFNFTEVDVCBtYXgobWF4X2RhdGUpCiAgIEZST00gcnVieWdlbXMuZ2Vtc19kb3dubG9hZHNfbWF4X21pbgopIEFTIG1heF9kYXRlClNFTEVDVAogICBnZW0sCiAgIHN1bShjb3VudCkgQVMgYwpGUk9NIHJ1YnlnZW1zLmRvd25sb2Fkc19wZXJfZGF5CldIRVJFIGdlbSBJTiAoCiAgIFNFTEVDVCBuYW1lCiAgIEZST00gcnVieWdlbXMuZ2Vtc19kb3dubG9hZHNfbWF4X21pbgogICBHUk9VUCBCWSBuYW1lCiAgIEhBVklORyBtaW4obWluX2RhdGUpID49IChtYXhfZGF0ZSAtIHRvSW50ZXJ2YWxNb250aCgzKSkKKQpHUk9VUCBCWSBnZW0KT1JERVIgQlkgYyBERVNDCkxJTUlUIDcKU0VUVElOR1MgZW5hYmxlX2FuYWx5emVyPTA&chart=eyJ0eXBlIjoiYmFyIiwiY29uZmlnIjp7InRpdGxlIjoiRW1lcmdpbmcgZ2VtcyIsInhheGlzIjoiZ2VtIiwieWF4aXMiOiJjIn19' runnable='true' view='chart' chart_config='eyJ0eXBlIjoiYmFyIiwiY29uZmlnIjp7InRpdGxlIjoiRW1lcmdpbmcgZ2VtcyIsInhheGlzIjoiZ2VtIiwieWF4aXMiOiJjIiwic2VyaWVzIjoiZ2VtIiwic3RhY2siOnRydWV9fQ' clickhouse_settings='{"enable_analyzer":0}'>
WITH (
   SELECT max(max_date)
   FROM rubygems.gems_downloads_max_min
) AS max_date
SELECT
   gem,
   sum(count) AS c
FROM rubygems.downloads_per_day
WHERE gem IN (
   SELECT name
   FROM rubygems.gems_downloads_max_min
   GROUP BY name
   HAVING min(min_date) >= (max_date - toIntervalMonth(3))
)
GROUP BY gem
ORDER BY c DESC
LIMIT 7
</code></pre>

### Downloads over time for a gem

If day granularity is sufficient we can use the `downloads_per_day` view. For the bundler gem:

<pre><code type='click-ui' language='sql' show_statistics='true' show_line_numbers='false' show_line_numbers='false' play_link='https://sql.clickhouse.com/?query=U0VMRUNUCglkYXRlLAoJc3VtKGNvdW50KSBBUyB0b3RhbF9kb3dubG9hZHMKRlJPTSBydWJ5Z2Vtcy5kb3dubG9hZHNfcGVyX2RheQpXSEVSRSAoZ2VtID0gJ2J1bmRsZXInKQpHUk9VUCBCWSBkYXRlCk9SREVSIEJZIGRhdGUgQVND&chart=eyJ0eXBlIjoibGluZSIsImNvbmZpZyI6eyJ0aXRsZSI6IkJ1bmRsZXIgZG93bmxvYWRzIG92ZXIgdGltZSIsInhheGlzIjoiZGF0ZSIsInlheGlzIjoidG90YWxfZG93bmxvYWRzIn19' runnable='true' view='chart' chart_config='eyJ0eXBlIjoibGluZSIsImNvbmZpZyI6eyJ0aXRsZSI6IkJ1bmRsZXIgZG93bmxvYWRzIG92ZXIgdGltZSIsInhheGlzIjoiZGF0ZSIsInlheGlzIjoidG90YWxfZG93bmxvYWRzIn19'>
SELECT
	date,
	sum(count) AS total_downloads
FROM rubygems.downloads_per_day
WHERE (gem = 'bundler')
GROUP BY date
ORDER BY date ASC
</code></pre>

For more granular analysis the full fidelity download events can be used (we recommend filtering by date ranges in this case).

<pre><code type='click-ui' language='sql' show_statistics='true' show_line_numbers='false' show_line_numbers='false' play_link='https://sql.clickhouse.com/?query=U0VMRUNUIAogIHRvU3RhcnRPZkhvdXIodGltZXN0YW1wKSBhcyBob3VyLAogIGNvdW50KCkgYXMgdG90YWxfZG93bmxvYWRzCkZST00gcnVieWdlbXMuZG93bmxvYWRzCldIRVJFIChnZW0gPSAnYnVuZGxlcicpIEFORCB0aW1lc3RhbXAgPiBub3coKSAtIElOVEVSVkFMIDIgREFZUwpHUk9VUCBCWSBob3VyCk9SREVSIEJZIGhvdXIgQVND&chart=eyJ0eXBlIjoibGluZSIsImNvbmZpZyI6eyJ0aXRsZSI6IkJ1bmRsZXIgZG93bmxvYWRzIG92ZXIgdGltZSIsInhheGlzIjoiaG91ciIsInlheGlzIjoidG90YWxfZG93bmxvYWRzIn19' runnable='true' view='chart' chart_config='eyJ0eXBlIjoibGluZSIsImNvbmZpZyI6eyJ0aXRsZSI6IkJ1bmRsZXIgZG93bmxvYWRzIG92ZXIgdGltZSIsInhheGlzIjoiaG91ciIsInlheGlzIjoidG90YWxfZG93bmxvYWRzIn19'>
SELECT 
  toStartOfHour(timestamp) as hour,
  count() as total_downloads
FROM rubygems.downloads
WHERE (gem = 'bundler') AND timestamp > now() - INTERVAL 2 DAYS
GROUP BY hour
ORDER BY hour ASC
</code></pre>

### Downloads by Ruby version over time

For the bundler gem:

<pre><code type='click-ui' language='sql' show_statistics='true' show_line_numbers='false' show_line_numbers='false' play_link='https://sql.clickhouse.com/?query=LS1EYWlseSBnZW0gZG93bmxvYWRzIGJ5IHZlcnNpb24gb3ZlciB0aW1lLiBOT1RFOiBXZSByZWNvbW1lbmRlZCBhcHBseWluZyBhIHRpbWUgcmFuZ2UgKHdlZWtzIG1heCkgdG8gYXZvaWQgcXVvdGEgbGltaXRzLgpXSVRIIHRvcF92ZXJzaW9ucyBBUwoJKAogICAgCVNFTEVDVCB1c2VyX2FnZW50LnJ1YnkKICAgIAlGUk9NIHJ1YnlnZW1zLmRvd25sb2FkcwogICAgCVdIRVJFICh0aW1lc3RhbXAgQkVUV0VFTiAnMjAyNS0wMS0wMScgQU5EICcyMDI1LTA0LTAzJykgQU5EIChnZW0gPSAnYnVuZGxlcicpCiAgICAJR1JPVVAgQlkgdXNlcl9hZ2VudC5ydWJ5CiAgICAJT1JERVIgQlkgY291bnQoKSBERVNDCiAgICAJTElNSVQgMTAKCSkKU0VMRUNUCgl1c2VyX2FnZW50LnJ1YnkgQVMgcnVieV92ZXJzaW9uLAoJdG9TdGFydE9mSG91cih0aW1lc3RhbXApIEFTIGhvdXIsCgljb3VudCgpIEFTIGRvd25sb2FkcwpGUk9NIHJ1YnlnZW1zLmRvd25sb2FkcwpXSEVSRSAodGltZXN0YW1wIEJFVFdFRU4gJzIwMjUtMDEtMDEnIEFORCAnMjAyNS0wNC0wMycpIEFORCAoZ2VtID0gJ2J1bmRsZXInKSBBTkQgdXNlcl9hZ2VudC5ydWJ5IElOIHRvcF92ZXJzaW9ucwpHUk9VUCBCWQoJaG91ciwKCXJ1YnlfdmVyc2lvbgpPUkRFUiBCWQoJaG91ciBERVNDLAoJcnVieV92ZXJzaW9uIEFTQwo&chart=eyJ0eXBlIjoiYXJlYSIsImNvbmZpZyI6eyJ0aXRsZSI6IkdlbSBkb3dubG9hZHMgYnkgdmVyc2lvbiBvdmVyIHRpbWUiLCJ4YXhpcyI6ImhvdXIiLCJ5YXhpcyI6ImRvd25sb2FkcyIsInNlcmllcyI6InJ1YnlfdmVyc2lvbiJ9fQ' runnable='true' view='chart' chart_config='eyJ0eXBlIjoiYXJlYSIsImNvbmZpZyI6eyJ0aXRsZSI6IkdlbSBkb3dubG9hZHMgYnkgdmVyc2lvbiBvdmVyIHRpbWUiLCJ4YXhpcyI6ImhvdXIiLCJ5YXhpcyI6ImRvd25sb2FkcyIsInNlcmllcyI6InJ1YnlfdmVyc2lvbiJ9fQ'>
--Daily gem downloads by version over time. NOTE - We recommended applying a time range (weeks max) to avoid quota limits.
WITH top_versions AS
	(
    	SELECT user_agent.ruby
    	FROM rubygems.downloads
    	WHERE (timestamp BETWEEN '2025-01-01' AND '2025-04-03') AND (gem = 'bundler')
    	GROUP BY user_agent.ruby
    	ORDER BY count() DESC
    	LIMIT 10
	)
SELECT
	user_agent.ruby AS ruby_version,
	toStartOfHour(timestamp) AS hour,
	count() AS downloads
FROM rubygems.downloads
WHERE (timestamp BETWEEN '2025-01-01' AND '2025-04-03') AND (gem = 'bundler') AND user_agent.ruby IN top_versions
GROUP BY
	hour,
	ruby_version
ORDER BY
	hour DESC,
	ruby_version ASC
</code></pre>

<blockquote style="font-size: 15px;">
<p>In the future we’ll provide materialized views to accelerate this query.</p>
</blockquote>

### Downloads by system over time

For the bundler gem:

<pre><code type='click-ui' language='sql' show_statistics='true' show_line_numbers='false' show_line_numbers='false' play_link='https://sql.clickhouse.com/?query=V0lUSCBzeXN0ZW1zIEFTCgkoCiAgICAJU0VMRUNUIHVzZXJfYWdlbnQucGxhdGZvcm0ub3MKICAgIAlGUk9NIHJ1YnlnZW1zLmRvd25sb2FkcwogICAgCVdIRVJFICh0aW1lc3RhbXAgQkVUV0VFTiAnMjAyNS0wMS0wMScgQU5EICcyMDI1LTA0LTAzJylBTkQgKGdlbSA9ICdidW5kbGVyJykgQU5EICh1c2VyX2FnZW50LnBsYXRmb3JtLm9zIE5PVCBJTiAoJycsICd1bmtub3duJykpCiAgICAJR1JPVVAgQlkgdXNlcl9hZ2VudC5wbGF0Zm9ybS5vcwogICAgCU9SREVSIEJZIGNvdW50KCkgREVTQwogICAgCUxJTUlUIDUKCSkKU0VMRUNUCgl1c2VyX2FnZW50LnBsYXRmb3JtLm9zIEFTIG5hbWUsCgl0b1N0YXJ0T2ZIb3VyKHRpbWVzdGFtcCkgQVMgaG91ciwKCWNvdW50KCkgQVMgdG90YWxfZG93bmxvYWRzCkZST00gcnVieWdlbXMuZG93bmxvYWRzCldIRVJFICh0aW1lc3RhbXAgQkVUV0VFTiAnMjAyNS0wMS0wMScgQU5EICcyMDI1LTA0LTAzJykgQU5EIChnZW0gPSAnYnVuZGxlcicpIEFORCAodXNlcl9hZ2VudC5wbGF0Zm9ybS5vcyBJTiAoc3lzdGVtcykpCkdST1VQIEJZCgluYW1lLAoJaG91cgpPUkRFUiBCWQoJaG91ciBBU0MsCgluYW1lIERFU0M&chart=eyJ0eXBlIjoibGluZSIsImNvbmZpZyI6eyJ0aXRsZSI6IkJ1bmRlciBkb3dubG9hZHMgYnkgc3lzdGVtIG92ZXIgdGltZSIsInhheGlzIjoiaG91ciIsInlheGlzIjoidG90YWxfZG93bmxvYWRzIiwic2VyaWVzIjoibmFtZSJ9fQ' runnable='true' view='chart' chart_config='eyJ0eXBlIjoibGluZSIsImNvbmZpZyI6eyJ0aXRsZSI6IkJ1bmRlciBkb3dubG9hZHMgYnkgc3lzdGVtIG92ZXIgdGltZSIsInhheGlzIjoiaG91ciIsInlheGlzIjoidG90YWxfZG93bmxvYWRzIiwic2VyaWVzIjoibmFtZSJ9fQ'>
WITH systems AS
	(
    	SELECT user_agent.platform.os
    	FROM rubygems.downloads
    	WHERE (timestamp BETWEEN '2025-01-01' AND '2025-04-03')AND (gem = 'bundler') AND (user_agent.platform.os NOT IN ('', 'unknown'))
    	GROUP BY user_agent.platform.os
    	ORDER BY count() DESC
    	LIMIT 5
	)
SELECT
	user_agent.platform.os AS name,
	toStartOfHour(timestamp) AS hour,
	count() AS total_downloads
FROM rubygems.downloads
WHERE (timestamp BETWEEN '2025-01-01' AND '2025-04-03') AND (gem = 'bundler') AND (user_agent.platform.os IN (systems))
GROUP BY
	name,
	hour
ORDER BY
	hour ASC,
	name DESC
</code></pre>


<blockquote style="font-size: 15px;">
<p>In the future we’ll provide materialized views to accelerate this query.</p>
</blockquote>

### Downloads for latest Gem version (using dictionaries)

Some queries require us to use more than 1 table. The weekly metadata tables are particularly useful for more complex queries.

We also provide a number of dictionaries for users to use to accelerate queries. These in-memory structures allow key-value lookups. For example, the following two dictionaries allow the lookup of a gem's id but its name and vice versa:

<pre><code type='click-ui' language='sql' show_line_numbers='false' show_line_numbers='false'>
CREATE DICTIONARY rubygems.name_to_id
(
	`name` String,
	`id` UInt64
)
PRIMARY KEY name
SOURCE(CLICKHOUSE(QUERY 'SELECT name, id FROM rubygems.rubygems'))
LIFETIME(MIN 86400 MAX 90000)
LAYOUT(COMPLEX_KEY_HASHED())

CREATE DICTIONARY rubygems.id_to_name
(
	`id` UInt64,
	`name` String
)
PRIMARY KEY id
SOURCE(CLICKHOUSE(QUERY 'SELECT id, name FROM rubygems.rubygems'))
LIFETIME(MIN 86400 MAX 90000)
LAYOUT(FLAT())
</code></pre>

<blockquote style="font-size: 15px;">
<p>To learn more about dictionaries we recommend the <a href="https://clickhouse.com/docs/dictionary">"Dictionary" docs guide</a></p>
</blockquote>

For example, to lookup the bundler gems id:

<pre><code type='click-ui' language='sql' show_statistics='true' show_line_numbers='false' show_line_numbers='false' play_link='https://sql.clickhouse.com/?query=U0VMRUNUIGRpY3RHZXQocnVieWdlbXMubmFtZV90b19pZCwgJ2lkJywgJ2J1bmRsZXInKQo' runnable='true'>
SELECT dictGet(rubygems.name_to_id, 'id', 'bundler') AS gem_id
</code></pre>

Conversely, to look up the name from the id `19969`:

<pre><code type='click-ui' language='sql' show_statistics='true' show_line_numbers='false' show_line_numbers='false' play_link='https://sql.clickhouse.com/?query=U0VMRUNUIGRpY3RHZXQocnVieWdlbXMuaWRfdG9fbmFtZSwgJ25hbWUnLCAxOTk2OSkKCg' runnable='true'>
SELECT dictGet(rubygems.id_to_name, 'name', 19969) AS gem_name
</code></pre>

This is particularly useful in the weekly datasets, where not all tables have a gem name. For example to find the latest version of a gem we can use the `versions` table, exploiting the above dictionary for the id needed:

<pre><code type='click-ui' language='sql' show_statistics='true' show_line_numbers='false' show_line_numbers='false' play_link='https://sql.clickhouse.com/?query=U0VMRUNUIGNhbm9uaWNhbF9udW1iZXIKRlJPTSBydWJ5Z2Vtcy52ZXJzaW9ucwpXSEVSRSBydWJ5Z2VtX2lkID0gZGljdEdldChydWJ5Z2Vtcy5uYW1lX3RvX2lkLCAnaWQnLCAnYnVuZGxlcicpCk9SREVSIEJZIGFycmF5TWFwKHggLT4gdG9VSW50OE9yRGVmYXVsdCh4LCAwKSwgc3BsaXRCeUNoYXIoJy4nLCBjYW5vbmljYWxfbnVtYmVyKSkgREVTQwpMSU1JVCAx' runnable='true'>
SELECT canonical_number
FROM rubygems.versions
WHERE rubygem_id = dictGet(rubygems.name_to_id, 'id', 'bundler')
ORDER BY arrayMap(x -> toUInt8OrDefault(x, 0), splitByChar('.', canonical_number)) DESC
LIMIT 1
</code></pre>

We can now combine this with our `downloads` table to find the weekly downloads for the latest version of the gem.

<pre><code type='click-ui' language='sql' show_statistics='true'  show_line_numbers='false' play_link='https://sql.clickhouse.com/?query=V0lUSCAoCiAgICAJU0VMRUNUIGNhbm9uaWNhbF9udW1iZXIKICAgIAlGUk9NIHJ1YnlnZW1zLnZlcnNpb25zCiAgICAJV0hFUkUgcnVieWdlbV9pZCA9IGRpY3RHZXQocnVieWdlbXMubmFtZV90b19pZCwgJ2lkJywgJ2J1bmRsZXInKQogICAgCU9SREVSIEJZIGFycmF5TWFwKHggLT4gdG9VSW50OE9yRGVmYXVsdCh4LCAwKSwgc3BsaXRCeUNoYXIoJy4nLCBjYW5vbmljYWxfbnVtYmVyKSkgREVTQwogICAgCUxJTUlUIDEKCSkgQVMgbGF0ZXN0X3ZlcnNpb24KU0VMRUNUCgl0b1N0YXJ0T2ZXZWVrKHRpbWVzdGFtcCkgQVMgd2VlaywKCWNvdW50KCkgQVMgZG93bmxvYWRzCkZST00gcnVieWdlbXMuZG93bmxvYWRzCldIRVJFIChnZW0gPSAnYnVuZGxlcicpIEFORCAodmVyc2lvbiA9IGxhdGVzdF92ZXJzaW9uKQpHUk9VUCBCWSB3ZWVrCk9SREVSIEJZIHdlZWsgQVNDCg' runnable='true'>
WITH (
    	SELECT canonical_number
    	FROM rubygems.versions
    	WHERE rubygem_id = dictGet(rubygems.name_to_id, 'id', 'bundler')
    	ORDER BY arrayMap(x -> toUInt8OrDefault(x, 0), splitByChar('.', canonical_number)) DESC
    	LIMIT 1
	) AS latest_version
SELECT
	toStartOfWeek(timestamp) AS week,
	count() AS downloads
FROM rubygems.downloads
WHERE (gem = 'bundler') AND (version = latest_version)
GROUP BY week
ORDER BY week ASC
</code></pre>

## Conclusion & future plans

We’re just getting started with Ruby Gem analytics and have plenty more planned.

Next up: we’re adding more materialized views and reworking the ClickPy UI to support the Ruby dataset, making it easy for developers to explore gem trends through an interactive web experience. ClickGems, anyone?

Until then, researchers, maintainers, and curious developers can query the data freely at [sql.clickhouse.com](https://sql.clickhouse.com), with support for both raw download logs and pre-aggregated daily statistics.

A huge thank you to Marty, Samuel, and the wider Ruby Central community for their collaboration, encouragement, and ongoing support in making this possible.


