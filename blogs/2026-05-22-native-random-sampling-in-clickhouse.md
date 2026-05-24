---
title: "Native random sampling in ClickHouse"
date: "2026-05-22T09:53:15.900Z"
author: "Mark Needham"
category: "Engineering"
excerpt: "Learn how to use ClickHouse's SAMPLE BY clause to run fast, approximate queries on large datasets with minimal accuracy trade-off."
---

# Native random sampling in ClickHouse

Sometimes running aggregate queries against all your data isn't fast enough.
ClickHouse's native random sampling lets you execute a query against a random fraction or sample of the data instead - and with the right setup, the results stay surprisingly accurate.

<iframe width="768" height="432" src="https://www.youtube.com/embed/RHkfT7Uj38k?si=CdYvg80QWt5TBy_U" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

## Setup

We'll use the [UK house prices dataset](https://clickhouse.com/docs/getting-started/example-datasets/uk-price-paid), which has just over 30 million property transactions.
Let's first create the table:

<pre><code type='click-ui' language='sql'>
CREATE TABLE uk_price_paid
(
    price UInt32,
    date Date,
    postcode1 LowCardinality(String),
    postcode2 LowCardinality(String),
    type Enum8('terraced' = 1, 'semi-detached' = 2, 'detached' = 3, 'flat' = 4, 'other' = 0),
    is_new UInt8,
    duration Enum8('freehold' = 1, 'leasehold' = 2, 'unknown' = 0),
    addr1 String,
    addr2 String,
    street LowCardinality(String),
    locality LowCardinality(String),
    town LowCardinality(String),
    district LowCardinality(String),
    county LowCardinality(String)
)
ENGINE = MergeTree
ORDER BY (postcode1, postcode2, addr1, addr2);
</code></pre>

And then ingest the data:

<pre><code type='click-ui' language='sql'>
INSERT INTO uk_price_paid
SELECT
    toUInt32(price_string) AS price,
    parseDateTimeBestEffortUS(time) AS date,
    splitByChar(' ', postcode)[1] AS postcode1,
    splitByChar(' ', postcode)[2] AS postcode2,
    transform(a, ['T', 'S', 'D', 'F', 'O'], ['terraced', 'semi-detached', 'detached', 'flat', 'other']) AS type,
    b = 'Y' AS is_new,
    transform(c, ['F', 'L', 'U'], ['freehold', 'leasehold', 'unknown']) AS duration,
    addr1,
    addr2,
    street,
    locality,
    town,
    district,
    county
FROM url(
    'http://prod1.publicdata.landregistry.gov.uk.s3-website-eu-west-1.amazonaws.com/pp-complete.csv',
    'CSV',
    'uuid_string String,
    price_string String,
    time String,
    postcode String,
    a String,
    b String,
    c String,
    addr1 String,
    addr2 String,
    street String,
    locality String,
    town String,
    district String,
    county String,
    d String,
    e String'
) SETTINGS max_http_get_redirects=10;
</code></pre>

We can then write the following query to get a count of all the rows in the table:

<pre><code type='click-ui' language='sql'>
SELECT count()
FROM uk_price_paid;
</code></pre>

Which returns:

```shell
┌──count()─┐
│ 30452463 │ -- 30.45 million
└──────────┘

1 row in set. Elapsed: 0.002 sec.
```

## Choosing a sample key

Now let's say we want to run aggregate queries on a sample of this data, because running those queries against all the data isn't fast enough. To do that, we need to specify a sample key when we create our table.

A sample key is an expression that determines which rows get included when you sample your data. The key should be an unsigned integer (like a hash), have high cardinality, and distribute evenly across its range. One such function is [`sipHash64`](https://clickhouse.com/docs/sql-reference/functions/hash-functions#sipHash64), a cryptographic hash function that returns a 64-bit value.

We can verify this by checking how evenly it distributes `postcode1` and `postcode2`.
The following query uses `sipHash64` on `postcode1` and `postcode2` and then rounds down the hashes into 10 buckets, and each of them should hold around 10% of the values.

<pre><code type='click-ui' language='sql'>
WITH pow(2, 64) AS maxUInt64, 10 AS numBuckets
SELECT
    floor(sipHash64(postcode1, postcode2) / (maxUInt64 / numBuckets)) AS bucket,
    count() AS rows,
    round(count() / (SELECT count() FROM uk_price_paid) * 100, 2) AS pct
FROM uk_price_paid
GROUP BY bucket
ORDER BY bucket;
</code></pre>

If we run the query, we'll see the following output:

```shell
┌─bucket─┬────rows─┬───pct─┐
│      0 │ 3106578 │  10.2 │
│      1 │ 3025622 │  9.94 │
│      2 │ 3043133 │  9.99 │
│      3 │ 3033438 │  9.96 │
│      4 │ 3063534 │ 10.06 │
│      5 │ 3048884 │ 10.01 │
│      6 │ 3005960 │  9.87 │
│      7 │ 3053378 │ 10.03 │
│      8 │ 3029517 │  9.95 │
│      9 │ 3042419 │  9.99 │
└────────┴─────────┴───────┘
```

Each bucket holds right around 10% - some a little less, some a little more, but very close.
`postcode1` and `postcode2` would therefore be a good choice of key.

On the other hand, let's see what happens if we hash `county` instead:

<pre><code type='click-ui' language='sql'>
WITH pow(2, 64) AS maxUInt64, 10 AS numBuckets
SELECT
    floor(sipHash64(county) / (maxUInt64 / numBuckets)) AS bucket,
    count() AS rows,
    round(count() / (SELECT count() FROM uk_price_paid) * 100, 2) AS pct
FROM uk_price_paid
GROUP BY bucket
ORDER BY bucket;
</code></pre>

```shell
┌─bucket─┬────rows─┬───pct─┐
│      0 │ 2853723 │  9.37 │
│      1 │ 2543953 │  8.35 │
│      2 │ 4568680 │    15 │
│      3 │ 1402093 │   4.6 │
│      4 │ 5547516 │ 18.22 │
│      5 │ 1402865 │  4.61 │
│      6 │ 4854564 │ 15.94 │
│      7 │ 2820334 │  9.26 │
│      8 │ 2649867 │   8.7 │
│      9 │ 1808868 │  5.94 │
└────────┴─────────┴───────┘
```

This time, the amount of data in each bucket ranges from 4.6% to 18%, which isn't as well spread out. `county` therefore wouldn't be such a good choice for our sampling key. The reason for this is that `county` is a low cardinality column, with only 132 unique values. We therefore compute 132 hashes which are spread across 10 buckets, giving us roughly 13 counties per bucket. The number of rows per bucket is dependent on the number of properties sold in that county. 

The following query shows us how uneven the spread of property sales by county is:

<pre><code type='click-ui' language='sql'>
SELECT county,
       round((100 * count()) / sum(count()) OVER (), 2) AS pct
FROM uk_price_paid
GROUP BY county
ORDER BY pct DESC
LIMIT 10
</code></pre>

```shell
┌─county─────────────┬──pct─┐
│ GREATER LONDON     │ 12.7 │
│ GREATER MANCHESTER │ 4.45 │
│ WEST MIDLANDS      │  3.8 │
│ WEST YORKSHIRE     │  3.8 │
│ KENT               │ 2.84 │
│ ESSEX              │ 2.77 │
│ HAMPSHIRE          │  2.6 │
│ LANCASHIRE         │ 2.29 │
│ SURREY             │ 2.23 │
│ MERSEYSIDE         │ 2.13 │
└────────────────────┴──────┘
```

Greater London accounts for almost 13% of all sales, so whichever bucket it lands in will be heavily skewed.

By contrast, there are 1.32 million distinct postcode1/postcode2 combinations, which is enough to let the hash function do its job of distributing the data evenly.

## Creating the table

Next, let's create a new version of the table with our sampling key.
The [`SAMPLE BY`](https://clickhouse.com/docs/engines/table-engines/mergetree-family/mergetree#sample-by) key must be part of your primary key (i.e. your `ORDER BY` expression).
We'll add `sipHash64(postcode1, postcode2)` at the beginning of the `ORDER BY` so that we see the most benefit from sampling.

<pre><code type='click-ui' language='sql'>
CREATE TABLE uk_price_paid_sample
(
    price UInt32,
    date Date,
    postcode1 LowCardinality(String),
    postcode2 LowCardinality(String),
    type Enum8('terraced' = 1, 'semi-detached' = 2, 'detached' = 3, 'flat' = 4, 'other' = 0),
    is_new UInt8,
    duration Enum8('freehold' = 1, 'leasehold' = 2, 'unknown' = 0),
    addr1 String,
    addr2 String,
    street LowCardinality(String),
    locality LowCardinality(String),
    town LowCardinality(String),
    district LowCardinality(String),
    county LowCardinality(String)
)
ENGINE = MergeTree
ORDER BY (sipHash64(postcode1, postcode2), postcode1, postcode2, addr1, addr2)
SAMPLE BY sipHash64(postcode1, postcode2);
</code></pre>

Now let's insert the data from our original table into the new one:

<pre><code type='click-ui' language='sql'>
INSERT INTO uk_price_paid_sample
SELECT * 
FROM uk_price_paid;
</code></pre>

## Sampling the data in a table

With the table set up, it's time to do some sampling!
Data sampling is deterministic, which means the result of the same `SELECT .. SAMPLE` query is always the same.
The `SAMPLE` clause works in two modes.

The first mode is **by fraction**, where we provide a value between 0 and 1 and the query will be executed on that fraction of the data.

<pre><code type='click-ui' language='sql'>
SELECT count() 
FROM uk_price_paid_sample 
SAMPLE 0.1;
</code></pre>

This query takes the first 10% of the hash value range, effectively all rows where `sipHash64(postcode1, postcode2) < 2^64 * 0.1`.
The result of running the query is shown below:

```shell
┌─count()─┐
│ 3106578 │ -- 3.11 million
└─────────┘

1 row in set. Elapsed: 0.043 sec.
```

There are 30.45 million rows in the table, so 10% of that is 3.045 million, which is reasonably close to the 3.11 million we got back.

The second mode is **by row count**, where we specify a minimum number of rows to return:

<pre><code type='click-ui' language='sql'>
SELECT count() 
FROM uk_price_paid_sample 
SAMPLE 100000;
</code></pre>

This returns *at least* 100,000 rows. ClickHouse computes a threshold of `(100000 / estimated_table_rows) * 2^64` and selects rows whose hash falls below it.
The output of running the query is shown below:

```shell
┌─count()─┐
│  103347 │
└─────────┘

1 row in set. Elapsed: 0.009 sec.
```

In both cases, because the hash is part of the primary index, ClickHouse can quickly skip granules whose hash values are above the threshold.

## The `_sample_factor` virtual column

When using sampling, we can also use `_sample_factor`, a virtual column that tells you how many rows from the full dataset each sampled row represents.
When there's no sampling, it's 1. For a 10% sample it's 10. For the row-count sample it's around 304.5.

If we want to estimate the total number of rows, we can sum `_sample_factor`, as shown in the following query:

<pre><code type='click-ui' language='sql'>
SELECT 'None' AS sampleType, count(), sum(_sample_factor)
FROM uk_price_paid_sample

UNION ALL

SELECT 'Fraction (0.1)' AS sampleType, count(), sum(_sample_factor)
FROM uk_price_paid_sample SAMPLE 0.1

UNION ALL

SELECT 'Number (100,000)' AS sampleType, count(), sum(_sample_factor)
FROM uk_price_paid_sample SAMPLE 100000;
</code></pre>

```shell
┌─sampleType───────┬──count()─┬─sum(_sample_factor)─┐
│ None             │ 30452463 │            30452463 │
│ Fraction (0.1)   │  3106578 │            31065780 │
│ Number (100,000) │   103347 │  31471706.936610293 │
└──────────────────┴──────────┴─────────────────────┘
```

Both of the sampling techniques over estimate the total number of rows by 2-3%, which isn't too bad. 

The same principle applies to other aggregations. If we run `sum(price)` on a 10% sample, we'll get roughly 10% of the true total:

<pre><code type='click-ui' language='sql'>
SELECT sum(price) 
FROM uk_price_paid_sample 
SAMPLE 0.1;
</code></pre>

```shell
┌───sum(price)─┐
│ 741594301263 │ -- 741.59 billion
└──────────────┘
```

To get a full-dataset estimate, we need to multiply by `_sample_factor`:

<pre><code type='click-ui' language='sql'>
SELECT sum(price * _sample_factor) 
FROM uk_price_paid_sample 
SAMPLE 0.1;
</code></pre>

```shell
┌─sum(multiply⋯le_factor))─┐
│            7415943012630 │ -- 7.42 trillion
└──────────────────────────┘
```

`avg` and `count` are safe on samples without adjustment - averaging or counting a subset gives the same result as the full dataset, but any aggregation that depends on population totals, like `sum`, needs `_sample_factor` to scale back up.

Keep in mind that there will always be a little bit of error when sampling - that's the trade-off we make for faster query times.

## Sampling a real analytical query

Now let's run this against a real analytical query. For each county, town, and property type in a given year, we want the total sales, the average price, and the median. We limit to one row per county and town, otherwise we'd just get Greater London everywhere.

<pre><code type='click-ui' language='sql'>
SELECT county, town, type,
       toYear(date) AS year,
       sum(_sample_factor) AS sales,
       round(avg(price)) AS avgPrice,
       round(quantile(0.5)(price)) AS median
FROM uk_price_paid_sample
GROUP BY county, town, type, year
ORDER BY sales DESC
LIMIT 1 BY county, town
LIMIT 5;
</code></pre>

```shell
┌─county─────────────┬─town───────┬─type─────┬─year─┬─sales─┬─avgPrice─┬─median─┐
│ GREATER LONDON     │ LONDON     │ flat     │ 2006 │ 65567 │   296793 │ 242500 │
│ GREATER MANCHESTER │ MANCHESTER │ terraced │ 2004 │  9896 │    80212 │  71000 │
│ WEST MIDLANDS      │ BIRMINGHAM │ terraced │ 2002 │  8266 │    73946 │  67500 │
│ MERSEYSIDE         │ LIVERPOOL  │ terraced │ 2003 │  6507 │    52895 │  42500 │
│ WEST YORKSHIRE     │ LEEDS      │ terraced │ 2002 │  5921 │    64886 │  55000 │
└────────────────────┴────────────┴──────────┴──────┴───────┴──────────┴────────┘

```

I ran this a few times and the elapsed time is shown below:

```shell
5 rows in set. Elapsed: 0.687 sec. Processed 30.45 million rows, 290.09 MB (44.36 million rows/s., 422.55 MB/s.)
Peak memory usage: 481.82 MiB.

5 rows in set. Elapsed: 0.721 sec. Processed 30.45 million rows, 290.09 MB (42.22 million rows/s., 402.20 MB/s.)
Peak memory usage: 496.21 MiB.

5 rows in set. Elapsed: 0.748 sec. Processed 30.45 million rows, 290.09 MB (40.69 million rows/s., 387.62 MB/s.)
Peak memory usage: 500.59 MiB.
```

Now let's see what happens if we sample 10% of the data:

<pre><code type='click-ui' language='sql'>
SELECT county, town, type,
       toYear(date) AS year,
       sum(_sample_factor) AS sales,
       round(avg(price)) AS avgPrice,
       round(quantile(0.5)(price)) AS median
FROM uk_price_paid_sample SAMPLE 0.1
GROUP BY county, town, type, year
ORDER BY sales DESC
LIMIT 1 BY county, town
LIMIT 5;
</code></pre>

```shell
┌─county─────────────┬─town───────┬─type─────┬─year─┬─sales─┬─avgPrice─┬─median─┐
│ GREATER LONDON     │ LONDON     │ flat     │ 2006 │ 70500 │   287644 │ 240000 │
│ GREATER MANCHESTER │ MANCHESTER │ terraced │ 2004 │ 10380 │    75479 │  66000 │
│ WEST MIDLANDS      │ BIRMINGHAM │ terraced │ 2002 │  8480 │    73869 │  68000 │
│ MERSEYSIDE         │ LIVERPOOL  │ terraced │ 2004 │  6640 │    78769 │  68000 │
│ WEST YORKSHIRE     │ LEEDS      │ terraced │ 2002 │  6320 │    64598 │  54050 │
└────────────────────┴────────────┴──────────┴──────┴───────┴──────────┴────────┘
```

And again, we'll run it three times:

```shell
5 rows in set. Elapsed: 0.169 sec. Processed 2.91 million rows, 38.31 MB (17.23 million rows/s., 226.97 MB/s.)
Peak memory usage: 238.06 MiB.

5 rows in set. Elapsed: 0.141 sec. Processed 3.15 million rows, 41.49 MB (22.30 million rows/s., 294.09 MB/s.)
Peak memory usage: 177.00 MiB.

5 rows in set. Elapsed: 0.185 sec. Processed 2.12 million rows, 27.82 MB (11.45 million rows/s., 150.14 MB/s.)
Peak memory usage: 179.40 MiB.
```

Taking the best times of each run, it took 141 milliseconds when sampling and 687 milliseconds when querying the whole dataset, which is about 80% better.

The query plan for the sampled query is shown below:

```shell
    ┌─explain──────────────────────────────────────────────────────┐
 1. │ Expression (Project names)                                   │
 2. │   Limit                                                      │
 3. │     LimitBy                                                  │
 4. │       Expression ((Before LIMIT BY + (Before ORDER BY + Proj⋯│
 5. │         Sorting (Sorting for ORDER BY)                       │
 6. │           Expression ((Before ORDER BY + Projection))        │
 7. │             Aggregating                                      │
 8. │               Expression ((Before GROUP BY + Change column n⋯│
 9. │                 ReadFromMergeTree (default.uk_price_paid_sam⋯│
10. │                 Indexes:                                     │
11. │                   PrimaryKey                                 │
12. │                     Keys:                                    │
13. │                       sipHash64(postcode1, postcode2)        │
14. │                     Condition: (sipHash64(postcode1, postcod⋯│
15. │                     Parts: 9/9                               │
16. │                     Granules: 384/3719                       │
17. │                     Search Algorithm: binary search          │
18. │                   Ranges: 9                                  │
    └──────────────────────────────────────────────────────────────┘
```

We can see from line 16 that the query has only scanned 384/3719 granules, which explains the reduced query time.

Results-wise, the sales figures are roughly 7–8% off, average price is closer, and the medians are slightly off as well. This is probably reasonable for exploratory work.

## In summary

Sampling is useful when you need fast, approximate answers and can tolerate a small margin of error. 
If you remember only three things from this post: pick a high-cardinality column as your sampling key, put your sample key at the front of your `ORDER BY` for the fastest queries, and scale sum aggregations with `_sample_factor`.

---

## Get started today

Interested in seeing how ClickHouse works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-661-get-started-today-sign-up&utm_blogctaid=661)

---