---
title: "ClickHouse and the MTA Data Challenge"
date: "2024-10-24T16:34:04.523Z"
author: "The PME Team"
category: "Engineering"
excerpt: "For the MTA data challenge, we analyzed NYC’s MTA turnstile dataset, focusing on loading and cleaning historical data. In our new playground, users can explore the data with over 220 example queries across 35 datasets."
---

# ClickHouse and the MTA Data Challenge

We love [open data challenges](https://clickhouse.com/blog/clickhouse-1-trillion-row-challenge) at ClickHouse, so when we saw that MTA (Metropolitan Transportation Authority) had[ announced such a challenge](https://new.mta.info/article/mta-open-data-challenge) on their website, we couldn’t resist the temptation to contribute. We’ve focused on the turnstile dataset allowing analysis of subway usage in NYC, making this available in our new playground where users can query the data for free.

<blockquote style="font-size: 15px;">
<p>The MTA (Metropolitan Transportation Authority) operates public transportation systems in New York City, including subways, buses, and commuter rail services, serving millions of passengers daily. The MTA Open Data Challenge is a month-long competition aimed at developers and data enthusiasts. MTA encourages participants to use their datasets to create projects that creatively leverage the data, whether through web apps, visualizations, or reports. Submissions must use at least one dataset from data.ny.gov, and will be judged on creativity, utility, execution, and transparency.</p>
</blockquote>

While the MTA challenge has 176 datasets to play around with, most of them are quite small, with only a few hundred rows. They still make excellent resources, but they aren’t really the volume of data to which ClickHouse is best suited. 

ClickHouse is an OLAP database designed for scale, and we, therefore, wanted to find the largest dataset to explore! This happens to be the [turnstile dataset](https://data.ny.gov/browse?q=turnstile&sortBy=relevance), which contains 100 million rows over all the years. This dataset contains information on entry/exit values for turnstiles in New York City, thus allowing an analysis of the movement of people around the city. At first glance, this dataset seemed quite simple, but as we found out, it required significantly more effort to clean and provide in usable form than first expected. 

<blockquote style="font-size: 15px;">
<p>The dataset itself covers the years 2014 to 2022. A (much cleaner) version of the turnstile data is available for more recent years. We’ve also loaded this dataset and provided example queries. In the interest of making all of the data available, however, we focus on the historical data in this blog.</p>
</blockquote>

In this post, we’ll explore the steps to load and clean this data to make it usable for further analysis so others can reproduce it in their own ClickHouse instance. This highlights some of the key features ClickHouse makes available for data engineering with many of the steps and queries reusable for other datasets.

![example_sql_clickhouse.png](https://clickhouse.com/uploads/example_sql_clickhouse_6b6cac3cb8.png)

For those just interested in the final dataset, we’ve made it available in our new [ClickHouse playground](https://sql.clickhouse.com), where we’ve got more than 220 queries and 35 datasets for you [to try out!](https://sql.clickhouse.com/?query_id=HPN5AHXEHK1NM2NB9S3AV2) To contribute new queries and datasets, [visit the demo repository](https://github.com/ClickHouse/sql.clickhouse.com).

<blockquote style="font-size: 14px;">
<p>All of the steps in this blog can be reproduced with<a href="https://clickhouse.com/docs/en/operations/utilities/clickhouse-local"> clickhouse-local</a>, an easy-to-use version of ClickHouse that is ideal for developers who need to perform fast processing on local and remote files using SQL without having to install a full database server.</p>
</blockquote>

## Initial data exploration and load

To simplify loading, we’ve made the turnstile data (distributed as TSV files) available on a public bucket. We can explore the columns available with a simple S3 query. This relies on ClickHouse schema inference to infer the column types:

<pre style="font-size: 13px;"><code class="hljs language-sql"><span class="hljs-keyword">DESCRIBE</span> <span class="hljs-keyword">TABLE</span> s3(<span class="hljs-string">'https://datasets-documentation.s3.eu-west-3.amazonaws.com/mta/*.tsv'</span>)
SETTINGS describe_compact_output <span class="hljs-operator">=</span> <span class="hljs-number">1</span>

┌─name───────────────────────────────────────────────────────┬─type────────────────────┐
│ C<span class="hljs-operator">/</span>A                                                    	 │ Nullable(String)    	   │
│ Unit                                                   	 │ Nullable(String)    	   │
│ SCP                                                    	 │ Nullable(String)    	   │
│ Station                                                	 │ Nullable(String)    	   │
│ Line Name                                              	 │ Nullable(String)    	   │
│ Division                                               	 │ Nullable(String)    	   │
│ <span class="hljs-type">Date</span>                                                   	 │ Nullable(DateTime64(<span class="hljs-number">9</span>)) │
│ <span class="hljs-type">Time</span>                                                   	 │ Nullable(String)    	   │
│ Description                                            	 │ Nullable(String)    	   │
│ Entries                                                	 │ Nullable(Int64)     	   │
│ Exits                                                  	 │ Nullable(Int64)     	   │
└────────────────────────────────────────────────────────────┴─────────────────────────┘


<span class="hljs-number">11</span> <span class="hljs-keyword">rows</span> <span class="hljs-keyword">in</span> set. Elapsed: <span class="hljs-number">0.309</span> sec.
</code></pre>

If we sample the data and review the[ dataset description](https://data.ny.gov/api/views/i55r-43gk/files/e348e3e7-9998-4e5e-926b-bdf04b62610e?download=true&filename=MTA_SubwayTurnstileUsageData2014_Overview.pdf), we can see that each row represents the entry and exit counts for a turnstile reported at a specific time. The description highlights these counts are reported periodically, so these statistics represent the previous period. Below, we query the data directly in S3 (in-place):
<pre style="font-size: 13px;"><code class="hljs language-sql"><span class="hljs-keyword">SELECT</span> <span class="hljs-operator">*</span>
<span class="hljs-keyword">FROM</span> s3(<span class="hljs-string">'https://datasets-documentation.s3.eu-west-3.amazonaws.com/mta/*.tsv'</span>)
LIMIT <span class="hljs-number">1</span>
FORMAT Vertical

<span class="hljs-type">Row</span> <span class="hljs-number">1</span>:
──────
C<span class="hljs-operator">/</span>A:                                                        A002
Unit:                                                       R051
SCP:                                                        <span class="hljs-number">02</span><span class="hljs-number">-00</span><span class="hljs-number">-00</span>
Station:                                                    LEXINGTON AVE
Line Name:                                                  NQR456
Division:                                                   BMT
<span class="hljs-type">Date</span>:                                                       <span class="hljs-number">2014</span><span class="hljs-number">-12</span><span class="hljs-number">-31</span> <span class="hljs-number">00</span>:<span class="hljs-number">00</span>:<span class="hljs-number">00.000000000</span>
<span class="hljs-type">Time</span>:                                                       <span class="hljs-number">23</span>:<span class="hljs-number">00</span>:<span class="hljs-number">00</span>
Description:                                                REGULAR
Entries:                                                    <span class="hljs-number">4943320</span>
Exits                                                     : <span class="hljs-number">1674736</span>

<span class="hljs-number">1</span> <span class="hljs-keyword">rows</span> <span class="hljs-keyword">in</span> set. Elapsed: <span class="hljs-number">1.113</span> sec.
</code></pre>

For easier processing and to prevent repeated downloads of the data, we can load this data into a local table. To create this table from the inferred schema and load the data, we can use the following. 

```sql
CREATE TABLE subway_transits_2014_2022_raw
ENGINE = MergeTree
ORDER BY tuple() EMPTY
AS SELECT *
FROM s3('https://datasets-documentation.s3.eu-west-3.amazonaws.com/mta/*.tsv')
```


This creates an empty table using the schema. We’ll use this as a staging table for data exploration only and, for now, omit[ an ordering key](https://clickhouse.com/docs/en/optimize/sparse-primary-indexes): Loading this data becomes a simple `INSERT INTO SELECT`:

```sql
INSERT INTO subway_transits_2014_2022_raw
SETTINGS max_insert_threads = 16, parallel_distributed_insert_select = 2
SELECT *
FROM s3Cluster('default', 'https://datasets-documentation.s3.eu-west-3.amazonaws.com/mta/*.tsv')
SETTINGS max_insert_threads = 16, parallel_distributed_insert_select = 2

0 rows in set. Elapsed: 39.236 sec. Processed 94.88 million rows, 13.82 GB (2.42 million rows/s., 352.14 MB/s.)
Peak memory usage: 1.54 GiB.

SELECT count()
FROM subway_transits_2014_2022_raw

┌──count()─┐
│ 94875892 │ -- 94.88 million
└──────────┘

1 row in set. Elapsed: 0.002 sec.

```

<blockquote style="font-size: 14px;">
<p>We’ve applied some simple optimizations to speed up this load, such as using the s3Cluster function. You can read more about these in the<a href="https://clickhouse.com:8443/docs/en/integrations/s3/performance"> Optimizing for S3 Insert and Read Performance guide</a>*.  The above timings (and subsequent) are from our sql.clickhouse.com environment, which consists of 3 nodes, each with 30vCPUs. Your performance will vary, but given the size of the dataset will heavily depend on network connection.</p>
</blockquote>

## Schema improvements

Examining the table schema reveals plenty of opportunities for optimization.

```sql
SHOW CREATE TABLE subway_transits_2014_2022_raw
CREATE TABLE subway_transits_2014_2022_raw
(
	`C/A` Nullable(String),
	`Unit` Nullable(String),
	`SCP` Nullable(String),
	`Station` Nullable(String),
	`Line Name` Nullable(String),
	`Division` Nullable(String),
	`Date` Nullable(DateTime64(9)),
	`Time` Nullable(String),
	`Description` Nullable(String),
	`Entries` Nullable(Int64),
	`Exits                                                 	` Nullable(Int64)
)
ENGINE = SharedMergeTree('/clickhouse/tables/{uuid}/{shard}', '{replica}')
ORDER BY tuple()
```

Aside from the column names being less than ideal (lowercase with no special chars is preferred), the Nullable type isn’t required. This[ consumes additional space](https://clickhouse.com/docs/en/cloud/bestpractices/avoid-nullable-columns) to differentiate between a Null and empty value and should be avoided. Furthermore, our `Date` and `Time` should be combined into a `date_time` column - ClickHouse has a rich set of[ date time functions](https://clickhouse.com/docs/en/sql-reference/functions/date-time-functions) that enable a DateTime type to be queried with respect to time, date, or both.

A quick check of the[ column descriptions for the data](https://data.ny.gov/api/views/ug6q-shqc/files/5fea1a03-cb1b-45af-b05f-a121019e949e?download=true&filename=MTA_SubwayTurnstileUsageData2015_DataDictionary.pdf)<span style="text-decoration:underline;"> </span>reveals some additional opportunities for optimization. The entries and exits cannot exceed an Int32, after which they wrap around (separate issue), and can only be positive. Most of the String columns are also low cardinality, something we can confirm with a quick query:

```sql
SELECT
    uniq(`C/A`),
    uniq(Unit),
    uniq(SCP),
    uniq(Station),
    uniq(`Line Name`),
    uniq(Division),
    uniq(Description)
FROM subway_transits_2014_2022_raw
FORMAT Vertical

Query id: c925aaa4-6302-41e4-9f1e-1ba88587c3bc

Row 1:
──────
uniq(C/A):         762
uniq(Unit):        476
uniq(SCP):         334
uniq(Station):     579
uniq(Line Name):   130
uniq(Division):    7
uniq(Description): 2

1 row in set. Elapsed: 0.959 sec. Processed 94.88 million rows, 10.27 GB (98.91 million rows/s., 10.71 GB/s.)
Peak memory usage: 461.18 MiB.
```

It therefore makes sense to make these a `LowCardinality(String)` type[ which will lead to better compression and faster queries](https://clickhouse.com/docs/en/data-compression/compression-in-clickhouse)! 

Anyone from NYC will also be familiar with the line naming system. The column `Line Name` denotes the lines available from the turnstile i.e.

“The train lines that stop at the station, such as 456”

![4523572781_c8f1c3a4b6_o.jpg](https://clickhouse.com/uploads/4523572781_c8f1c3a4b6_o_711cf233fc.jpg)
456 thus represents the 4, 5 and 6 lines. Glancing over the data revealed these aren’t consistently ordered. For example, `456NQR` is the same as  `NQR456`:

```sql
SELECT `Line Name`
FROM subway_transits_2014_2022_raw
WHERE (`Line Name` = 'NQR456') OR (`Line Name` = '456NQR')
LIMIT 1 BY `Line Name`

┌─Line Name─┐
│ NQR456	│
│ 456NQR	│
└───────────┘

2 rows in set. Elapsed: 0.059 sec. Processed 94.88 million rows, 1.20 GB (1.60 billion rows/s., 20.20 GB/s.)
Peak memory usage: 105.88 MiB.
```

To simplify future queries we tokenize this string into an `Array(LowCardinality(String))` and sort the values.

Finally, `station` and `date_time` seem like reasonable first choices for[ our ordering key](https://clickhouse.com/docs/en/optimize/sparse-primary-indexes). 

Our table schema thus becomes:

```sql
CREATE TABLE subway_transits_2014_2022_v1
(
   `ca` LowCardinality(String),
   `unit` LowCardinality(String),
   `scp` LowCardinality(String),
   `station` LowCardinality(String),
   `line_names` Array(LowCardinality(String)),
   `division` LowCardinality(String),
   `date_time` DateTime32,
   `description` LowCardinality(String),
   `entries` UInt32,
   `exits` UInt32
)
ENGINE = MergeTree
ORDER BY (station, date_time)
```

We can load this data by reading from our earlier `subway_transits_2014_2022_raw` table, using a `SELECT` to transform the rows.

```sql
INSERT INTO subway_transits_2014_2022_v1 SELECT
	`C/A` AS ca,
	Unit AS unit,
	SCP AS scp,
	Station AS station,
	arraySort(ngrams(assumeNotNull(`Line Name`), 1)) AS line_names,
	Division AS division,
	parseDateTimeBestEffort(trimBoth(concat(CAST(Date, 'Date32'), ' ', Time))) AS date_time,
	Description AS description,
	Entries AS entries,
	`Exits                                                 	` AS exits
FROM subway_transits_2014_2022_raw
SETTINGS max_insert_threads = 16

0 rows in set. Elapsed: 4.235 sec. Processed 94.88 million rows, 14.54 GB (22.40 million rows/s., 3.43 GB/s.)
```

## Cleaning the MTA transit dataset

Let’s now go through the steps that we took to clean the data. We found a couple of major issues, which we’ll go through in turn.

### Challenge 1: cumulative values and outliers

MTA provides a longer form[ description of the data](https://data.ny.gov/api/views/ug6q-shqc/files/29edbef3-268e-461d-95f1-374b1c8a6f9d?download=true&filename=MTA_SubwayTurnstileUsageData2015_Overview.pdf), which provides insight into some data quality issues and challenges. Not least, the `entries` and `exit` values are cumulative.

*> Data is provided about every four hours for the cumulative register values for entries and exits for each turnstile, similar to odometer readings. The four-hour intervals will differ from other stations due to the need for staggering to prevent flooding the system with audit readings all at once. Systemwide, stations have been set to begin audit transmittal between 00 to 03 hours, then every four hours after the first audit of the day. The number of people who entered or exited a turnstile in a period can be obtained by comparing it to an earlier reading.*

These cumulative values are challenging to use and would require queries to compute time ordered derivatives for every turnstile.  We note that the 4 hour periodic delivery of data will make attributing usage of a station to specific periods still very imprecise. This is something we can't resolve, so counts below the granularity of this period are unlikely to be accurate.

These values also have some clear data quality issues:

*> Turnstile audits are often not available every four hours, turnstiles sometimes count down instead of up, exit and entry counters periodically get reset, and the timestamps for audits vary between turnstiles. In addition, the data is 10 digits long and will roll over to zero on overflow.*

Ideally we'd like to compute the number of entries and exits for each row based on the difference to the previous time value for the turnstile. This requires us to reliably be able to identify a turnstile.

While turnstiles have an `scp` identifier, this is not unique across stations. Instead we can use a combination of the scp, ca (booth identifier at station) and unit(remote unit ID of the station) to identify a specific station.

To compute the number of entries and exits for each turnstile, requires a[ window function](https://clickhouse.com/docs/en/sql-reference/window-functions). The following computes the columns `entries_change` and `exits_change` for each row.

<pre style="font-size: 14px;"><code class="hljs language-sql"><span class="hljs-keyword">WITH</span> <span class="hljs-number">1000</span> <span class="hljs-keyword">AS</span> threshold_per_hour
<span class="hljs-keyword">SELECT</span>
    <span class="hljs-operator">*</span>,
    <span class="hljs-keyword">any</span>(date_time) <span class="hljs-keyword">OVER</span> (<span class="hljs-keyword">PARTITION</span> <span class="hljs-keyword">BY</span> ca, unit, scp <span class="hljs-keyword">ORDER</span> <span class="hljs-keyword">BY</span> date_time <span class="hljs-keyword">ASC</span> <span class="hljs-keyword">ROWS</span> <span class="hljs-keyword">BETWEEN</span> <span class="hljs-number">1</span> PRECEDING <span class="hljs-keyword">AND</span> <span class="hljs-keyword">CURRENT</span> <span class="hljs-type">ROW</span>) <span class="hljs-keyword">AS</span> p_date_time,
    <span class="hljs-keyword">any</span>(entries) <span class="hljs-keyword">OVER</span> (<span class="hljs-keyword">PARTITION</span> <span class="hljs-keyword">BY</span> ca, unit, scp <span class="hljs-keyword">ORDER</span> <span class="hljs-keyword">BY</span> date_time <span class="hljs-keyword">ASC</span> <span class="hljs-keyword">ROWS</span> <span class="hljs-keyword">BETWEEN</span> <span class="hljs-number">1</span> PRECEDING <span class="hljs-keyword">AND</span> <span class="hljs-keyword">CURRENT</span> <span class="hljs-type">ROW</span>) <span class="hljs-keyword">AS</span> p_entries,
    <span class="hljs-keyword">any</span>(exits) <span class="hljs-keyword">OVER</span> (<span class="hljs-keyword">PARTITION</span> <span class="hljs-keyword">BY</span> ca, unit, scp <span class="hljs-keyword">ORDER</span> <span class="hljs-keyword">BY</span> date_time <span class="hljs-keyword">ASC</span> <span class="hljs-keyword">ROWS</span> <span class="hljs-keyword">BETWEEN</span> <span class="hljs-number">1</span> PRECEDING <span class="hljs-keyword">AND</span> <span class="hljs-keyword">CURRENT</span> <span class="hljs-type">ROW</span>) <span class="hljs-keyword">AS</span> p_exits,
    dateDiff(<span class="hljs-string">'hour'</span>, p_date_time, date_time) <span class="hljs-keyword">AS</span> hours,
    if((entries <span class="hljs-operator">&lt;</span> p_entries) <span class="hljs-keyword">OR</span> (((entries <span class="hljs-operator">-</span> p_entries) <span class="hljs-operator">/</span> if(hours <span class="hljs-operator">&gt;</span> <span class="hljs-number">0</span>, hours, <span class="hljs-number">1</span>)) <span class="hljs-operator">&gt;</span> threshold_per_hour), <span class="hljs-number">0</span>, entries <span class="hljs-operator">-</span> p_entries) <span class="hljs-keyword">AS</span> entries_change,
    if((exits <span class="hljs-operator">&lt;</span> p_exits) <span class="hljs-keyword">OR</span> (((exits <span class="hljs-operator">-</span> p_exits) <span class="hljs-operator">/</span> if(hours <span class="hljs-operator">&gt;</span> <span class="hljs-number">0</span>, hours, <span class="hljs-number">1</span>)) <span class="hljs-operator">&gt;</span> threshold_per_hour), <span class="hljs-number">0</span>, exits <span class="hljs-operator">-</span> p_exits) <span class="hljs-keyword">AS</span> exits_change
<span class="hljs-keyword">FROM</span> subway_transits_2014_2022_v1
<span class="hljs-keyword">ORDER</span> <span class="hljs-keyword">BY</span>
    ca <span class="hljs-keyword">ASC</span>,
    unit <span class="hljs-keyword">ASC</span>,
    scp <span class="hljs-keyword">ASC</span>,
    date_time <span class="hljs-keyword">ASC</span>
</code></pre>

A few important points for the query:

* We order by `ca`, `unit`, `scp`, and `date_time` (ascending). This ensures the rows for each turnstile are processed together in increasing time order, allowing us to compute the delta.
* The function creates a window for each turnstile using `PARTITION BY ca, unit, scp`. Within each window the data is again ordered by increasing time. The `ROWS BETWEEN 1 PRECEDING AND CURRENT ROW` clause is used to add the columns `p_entries` and `p_exits`. These contain the previous entries and exit values for each row. The time from the previous row is captured in `p_date_time`.
* The columns `entries_change` and `exits_change` contain the delta between the previous and current values for the entries and exits, respectively. Importantly, if the change is negative, we return a value of 0, assuming this represents a rollover. Additionally, an analysis of the data revealed **significant outlier values** where the change would be unrealistically high e.g. 10,000 people used a turnstile in an hour. If the change exceeds a threshold of N per hour (1000), we also return 0 to filter out these values. Choosing a value threshold was based on the number of realistic people who could pass through a turnstile in our hour ([10-15 people per minute](https://www.turnstiles.us/turnstile-passthrough-rates-how-many-people-can-pass-per-minute/)). This approach is imperfect with more sophisticated approaches which consider historical trends possible.

### Challenge 2: missing/inconsistent station names

While the datasets for each year use the same schema, the [dataset for 2022](https://data.ny.gov/Transportation/MTA-Subway-Turnstile-Usage-Data-2022/k7j9-jnct/about_data) is missing station names.

```sql
SELECT toYear(date_time) AS year
FROM mta.subway_transits_2014_2022_v1
WHERE station = ''
GROUP BY year

   ┌─year─┐
1. │ 2022 │
   └──────┘

1 row in set. Elapsed: 0.016 sec. Processed 10.98 million rows, 54.90 MB (678.86 million rows/s., 3.39 GB/s.)
Peak memory usage: 98.99 MiB.
```

To make this dataset more usable, we would ideally populate the station name for 2022 based on a unique turnstile id to station name mapping (populated from earlier data).

However, if we analyze the station names, we can see they are rarely consistent, even for the same turnstile! For example, inconsistent use of `AV` and `AVE` for “avenue” appears to result in multiple entries for the same station.

```sql
SELECT DISTINCT station
FROM subway_transits_2014_2022_v1
WHERE station LIKE '%AV%'
ORDER BY station ASC
LIMIT 10
FORMAT PrettyCompactMonoBlock

┌─station──────┐
│ 1 AV         │
│ 1 AVE        │
│ 138 ST-3 AVE │
│ 14 ST-6 AVE  │
│ 149 ST-3 AVE │
│ 18 AV        │
│ 18 AVE       │
│ 2 AV         │
│ 2 AVE        │
│ 20 AV        │
└──────────────┘

10 rows in set. Elapsed: 0.024 sec. Processed 36.20 million rows, 41.62 MB (1.53 billion rows/s., 1.75 GB/s.)
Peak memory usage: 26.68 MiB.
```

If we can establish a turnstile to station name mapping, we can address simple issues like this by just picking one of the names consistently (e.g. always the longest) and remapping all of the data. Note this won't address more complex mappings, such as mapping the names '42 ST-TIMES SQ', and 'TIMES SQ-42 ST' to "TIMES SQ". We can defer these to query time for now.

To hold our mapping, we can use a dictionary. This in-memory structure will allow a station name lookup by a tuple of `(ca, unit, scp)` . We populate this dictionary with the query shown below, selecting the longest station name for each turnstile. The latter is achieved by producing a distinct list of station names assigned to each `(ca, unit, scp)` via the `groupArrayDistinct` function. This is then sorted by length, with the first (longest) entry selected.

```sql
CREATE DICTIONARY station_names
(
`ca` String,
`unit` String,
`scp` String,
`station_name` String
)
PRIMARY KEY (ca, unit, scp)
SOURCE(CLICKHOUSE(QUERY $query$
   SELECT
       ca,
       unit,
       scp,
       arrayReverseSort(station -> length(station), groupArrayDistinct(station))[1] AS station_name
   FROM subway_transits_2014_2022_v1
   WHERE station != ''
   GROUP BY
       ca,
       unit,
       scp
$query$))
LIFETIME(MIN 0 MAX 0)
LAYOUT(complex_key_hashed())
```

<blockquote style="font-size: 15px;">
<p>For more details on dictionaries, including the types available and how to configure them, see the Dictionaries documentation.</p>
</blockquote>

We can efficiently retrieve a specific station name using the dictGet` function. For example:

```sql
SELECT dictGet(station_names, 'station_name', ('R148', 'R033', '01-04-01'))

┌─name───────────┐
│ 42 ST-TIMES SQ │
└────────────────┘

1 row in set. Elapsed: 0.001 sec.
```

<blockquote style="font-size: 15px;">
<p>Note the first time the dictionary is invoked, the request might be slow depending on whether the data is loaded eagerly on creation or lazily on the first request. This can be<a href="https://clickhouse.com/docs/en/operations/server-configuration-parameters/settings#dictionaries_lazy_load"> configured using dictionaries_lazy_load</a>.</p>
</blockquote>

### Combining solutions for final data

We can now combine our window function and dictionary lookup to produce a final version of the data. The idea here is simple: execute a query using the window function and `dictGet` against v1 of our table, inserting the results into a new table. Our final table schema:

```sql
CREATE TABLE mta.subway_transits_2014_2022_v2
(
    `ca` LowCardinality(String),
    `unit` LowCardinality(String),
    `scp` LowCardinality(String),
    `line_names` Array(LowCardinality(String)),
    `division` LowCardinality(String),
    `date_time` DateTime,
    `description` LowCardinality(String),
    `entries` UInt32,
    `exits` UInt32,
    `station` LowCardinality(String),
    `entries_change` UInt32,
    `exits_change` UInt32
)
ENGINE = MergeTree
ORDER BY (ca, unit, scp, date_time)
```

Using an `INSERT INTO SELECT`:

<pre style="font-size: 14px;"><code class="hljs language-sql"><span class="hljs-keyword">INSERT</span> <span class="hljs-keyword">INTO</span> mta.subway_transits_2014_2022_v2 <span class="hljs-keyword">WITH</span> <span class="hljs-number">2000</span> <span class="hljs-keyword">AS</span> threshold_per_hour  <span class="hljs-keyword">SELECT</span>
   ca, unit, scp, line_names, division, date_time, description, entries, exits,
   dictGet(station_names, <span class="hljs-string">'station_name'</span>, (ca, unit, scp)) <span class="hljs-keyword">as</span> station,
   entries_change, exits_change
<span class="hljs-keyword">FROM</span>
(
  <span class="hljs-keyword">SELECT</span>
       <span class="hljs-operator">*</span>,
       <span class="hljs-keyword">any</span>(date_time) <span class="hljs-keyword">OVER</span> (<span class="hljs-keyword">PARTITION</span> <span class="hljs-keyword">BY</span> ca, unit, scp <span class="hljs-keyword">ORDER</span> <span class="hljs-keyword">BY</span> date_time <span class="hljs-keyword">ASC</span> <span class="hljs-keyword">ROWS</span> <span class="hljs-keyword">BETWEEN</span> <span class="hljs-number">1</span> PRECEDING <span class="hljs-keyword">AND</span> <span class="hljs-keyword">CURRENT</span> <span class="hljs-type">ROW</span>) <span class="hljs-keyword">AS</span> p_date_time,
       <span class="hljs-keyword">any</span>(entries) <span class="hljs-keyword">OVER</span> (<span class="hljs-keyword">PARTITION</span> <span class="hljs-keyword">BY</span> ca, unit, scp <span class="hljs-keyword">ORDER</span> <span class="hljs-keyword">BY</span> date_time <span class="hljs-keyword">ASC</span> <span class="hljs-keyword">ROWS</span> <span class="hljs-keyword">BETWEEN</span> <span class="hljs-number">1</span> PRECEDING <span class="hljs-keyword">AND</span> <span class="hljs-keyword">CURRENT</span> <span class="hljs-type">ROW</span>) <span class="hljs-keyword">AS</span> p_entries,
       <span class="hljs-keyword">any</span>(exits) <span class="hljs-keyword">OVER</span> (<span class="hljs-keyword">PARTITION</span> <span class="hljs-keyword">BY</span> ca, unit, scp <span class="hljs-keyword">ORDER</span> <span class="hljs-keyword">BY</span> date_time <span class="hljs-keyword">ASC</span> <span class="hljs-keyword">ROWS</span> <span class="hljs-keyword">BETWEEN</span> <span class="hljs-number">1</span> PRECEDING <span class="hljs-keyword">AND</span> <span class="hljs-keyword">CURRENT</span> <span class="hljs-type">ROW</span>) <span class="hljs-keyword">AS</span> p_exits,
       dateDiff(<span class="hljs-string">'hour'</span>, p_date_time, date_time) <span class="hljs-keyword">AS</span> hours,
       if((entries <span class="hljs-operator">&lt;</span> p_entries) <span class="hljs-keyword">OR</span> (((entries <span class="hljs-operator">-</span> p_entries) <span class="hljs-operator">/</span> if(hours <span class="hljs-operator">&gt;</span> <span class="hljs-number">0</span>, hours, <span class="hljs-number">1</span>)) <span class="hljs-operator">&gt;</span> threshold_per_hour), <span class="hljs-number">0</span>, entries <span class="hljs-operator">-</span> p_entries) <span class="hljs-keyword">AS</span> entries_change,
       if((exits <span class="hljs-operator">&lt;</span> p_exits) <span class="hljs-keyword">OR</span> (((exits <span class="hljs-operator">-</span> p_exits) <span class="hljs-operator">/</span> if(hours <span class="hljs-operator">&gt;</span> <span class="hljs-number">0</span>, hours, <span class="hljs-number">1</span>)) <span class="hljs-operator">&gt;</span> threshold_per_hour), <span class="hljs-number">0</span>, exits <span class="hljs-operator">-</span> p_exits) <span class="hljs-keyword">AS</span> exits_change
   <span class="hljs-keyword">FROM</span> subway_transits_2014_2022_v1
   <span class="hljs-keyword">ORDER</span> <span class="hljs-keyword">BY</span>
       ca <span class="hljs-keyword">ASC</span>,
       unit <span class="hljs-keyword">ASC</span>,
       scp <span class="hljs-keyword">ASC</span>,
       date_time <span class="hljs-keyword">ASC</span>
  
) SETTINGS max_insert_threads<span class="hljs-operator">=</span><span class="hljs-number">16</span>

<span class="hljs-number">0</span> <span class="hljs-keyword">rows</span> <span class="hljs-keyword">in</span> set. Elapsed: <span class="hljs-number">24.305</span> sec. Processed <span class="hljs-number">94.88</span> million <span class="hljs-keyword">rows</span>, <span class="hljs-number">2.76</span> GB (<span class="hljs-number">3.90</span> million <span class="hljs-keyword">rows</span><span class="hljs-operator">/</span>s., <span class="hljs-number">113.67</span> MB<span class="hljs-operator">/</span>s.)

</code></pre>

Our final table:

```sql
SELECT *
FROM mta.subway_transits_2014_2022_v2
LIMIT 1
FORMAT Vertical

Row 1:
──────
ca:             A002
unit:           R051
scp:            02-00-00
line_names:     ['4','5','6','N','Q','R']
division:       BMT
date_time:      2014-01-02 03:00:00
description:    REGULAR
entries:        4469306
exits:          1523801
station:        LEXINGTON AVE
entries_change: 0
exits_change:   0

1 rows in set. Elapsed: 0.005 sec.
```

## Sample queries for the MTA transit dataset

You can run the following queries in the ClickHouse playground. We’ve provided some default charts for each query to get you started. 

**If you’d like to suggest further queries or improvements, for the MTA dataset or others, please don’t hesitate to reach out and raise an issue on the[ demo’s repo](https://github.com/ClickHouse/sql.clickhouse.com).**

Lets first confirm the most popular stations align with official figures. For example, we’ll use 2018:

<pre style='background-color: #222222; border-radius: 8px; padding: 24px; color: #FFFFFF; display: flex; position: relative; white-space: pre-wrap;'>
<div style='color: #FFFFFF; margin-top: -24px; max-width: 98%;'>

SELECT
    station,
    sum(entries_change) AS total_entries,
    formatReadableQuantity(total_entries) AS total_entries_read
FROM mta.subway_transits_2014_2022_v2
WHERE toYear(date_time) = '2018'
GROUP BY station
ORDER BY sum(entries_change) DESC
LIMIT 10

</div> <a style='height: 32px; width: 32px; text-align: center; line-height: 1.3; position: absolute; font-size: 24px; top: 24px; right: 24px; color: #FFFFFF; background: rgba(0,0,0,0.8); border-radius: 8px;' href="https://sql.clickhouse.com/?query_id=4MGH76GE6QN6WA6H8TCYKR&run_query=true&tab=charts" target="_blank">✎</a>
</pre>
</p>


![query_1.png](https://clickhouse.com/uploads/query_1_cb5c5d11bc.png)

The quality of our results is impacted by both the data, which is extremely noisy, and the method we used to remove outliers. However, these do appear to align with the[ high-level numbers reported by MTA](https://new.mta.info/agency/new-york-city-transit/subway-bus-ridership-2022). Note also that some station entries, such as Times Square, have separate entry points in our data, i.e., '42 ST-TIMES SQ' and 'TIMES SQ-42 ST' to'TIMES SQ`. We leave this cleanup exercise as a to-do and currently resolve using conditionals at query time.

If we examine the traffic for the top 10 stations over the full period, the decline as a result of COVID is obvious:

<pre style='background-color: #222222; border-radius: 8px; padding: 24px; color: #FFFFFF; display: flex; position: relative; white-space: pre-wrap;'>
<div style='color: #FFFFFF; margin-top: -24px; max-width: 98%;'>

SELECT
    station,
    toYear(date_time) AS year,
    sum(entries_change) AS total_entries
FROM mta.subway_transits_2014_2022_v2
WHERE station IN (
    SELECT station
    FROM mta.subway_transits_2014_2022_v2
    GROUP BY station
    ORDER BY sum(entries_change) DESC
    LIMIT 10
)
GROUP BY
    year,
    station
ORDER BY year ASC

</div> <a style='height: 32px; width: 32px; text-align: center; line-height: 1.3; position: absolute; font-size: 24px; top: 24px; right: 24px; color: #FFFFFF; background: rgba(0,0,0,0.8); border-radius: 8px;' href="https://sql.clickhouse.com/?query_id=KADCUSBZG3UWVV2N4QUJXW&run_query=true&tab=charts" target="_blank">✎</a>
</pre>
</p>

![query_2.png](https://clickhouse.com/uploads/query_2_cd8cd4544f.png)

Despite our efforts, this data still remains very noisy. There are obvious anomalies which require further efforts to remove - we welcome suggestions on approaches. Conversely, the transit data from 2022 appears to be much more reliable and of higher quality. We’ve also loaded this into the `transit_data` table and provided some example queries.

Using this data, we can observe daily commuter patterns to show which stations are busy during which rush hour:

<pre style='background-color: #222222; border-radius: 8px; padding: 24px; color: #FFFFFF; display: flex; position: relative; white-space: pre-wrap;'>
<div style='color: #FFFFFF; margin-top: -24px; max-width: 98%;'>

SELECT
    station_complex,
    toHour(hour_of_day) AS hour,
    CAST(avg(total_entries), 'UInt64') AS avg_entries
FROM
(
    SELECT
        toStartOfHour(transit_timestamp) AS hour_of_day,
        station_complex,
        sum(ridership) AS total_entries
    FROM mta.transit_data
    WHERE toDayOfWeek(transit_timestamp) <= 5
    GROUP BY
        station_complex,
        hour_of_day
)
GROUP BY
    hour,
    station_complex
ORDER BY
    hour ASC,
    avg_entries DESC
LIMIT 3 BY hour

</div> <a style='height: 32px; width: 32px; text-align: center; line-height: 1.3; position: absolute; font-size: 24px; top: 24px; right: 24px; color: #FFFFFF; background: rgba(0,0,0,0.8); border-radius: 8px;' href="https://sql.clickhouse.com/?query_id=HPN5AHXEHK1NM2NB9S3AV2&run_query=true&tab=charts" target="_blank">✎</a>
</pre>
</p>

![query_3.png](https://clickhouse.com/uploads/query_3_571e11865d.png)

We can also easily compare weekend vs weekday traffic. This highlights some obvious times of the year e.g. 4th July, when commuter traffic is significantly lower.

<pre style='background-color: #222222; border-radius: 8px; padding: 24px; color: #FFFFFF; display: flex; position: relative; white-space: pre-wrap;'>
<div style='color: #FFFFFF; margin-top: -24px; max-width: 98%;'>

SELECT
    toStartOfWeek(transit_timestamp) AS week,
    'weekday' AS period,
    sum(ridership) AS total
FROM mta.transit_data
WHERE toDayOfWeek(transit_timestamp) <= 5
GROUP BY week
ORDER BY week ASC
UNION ALL
SELECT
    toStartOfWeek(transit_timestamp) AS week,
    'weekend' AS period,
    sum(ridership) AS total
FROM mta.transit_data
WHERE toDayOfWeek(transit_timestamp) > 5
GROUP BY week
ORDER BY week ASC

</div> <a style='height: 32px; width: 32px; text-align: center; line-height: 1.3; position: absolute; font-size: 24px; top: 24px; right: 24px; color: #FFFFFF; background: rgba(0,0,0,0.8); border-radius: 8px;' href="https://sql.clickhouse.com/?query_id=STHDUVXOFZFGF2JCHJGB5Y&run_query=true&tab=charts" target="_blank">✎</a>
</pre>
</p>

![query_4.png](https://clickhouse.com/uploads/query_4_07bce635ab.png)

## Conclusion

We had fun working on the MTA challenge (at least as much fun as you can have when cleaning data!) and hope that our work has made it easier for everyone to do some fun analysis of the data.

We’d love it if you shared any queries (and charts) you came up with on the [demo repository](https://github.com/ClickHouse/sql.clickhouse.com).
