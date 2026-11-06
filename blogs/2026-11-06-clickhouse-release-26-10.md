---
title: "ClickHouse release 26.10"
date: "2026-11-06T11:45:40.479Z"
author: "ClickHouse"
category: "Engineering"
excerpt: "ClickHouse 26.10 introduces function composition, more flexible joins, faster GROUP BY queries, disk spilling for IN subqueries, an experimental columns cache, and Freeform and SQLite formats."
---

# ClickHouse release 26.10

Another month goes by, which means it’s time for another release! 

<p>The ClickHouse 26.10 release contains 104 new features &#127875; 225 performance optimizations &#127810; and 739 bug fixes &#129417;.</p>

This release brings function composition for more readable SQL, more flexible JOIN conditions, and new ways to work with text and SQLite files. 

We also have faster GROUP BY queries, disk spilling for IN subqueries, and an experimental columns cache that saves repeated reads from decompressing and deserializing the same data.

## New contributors

A special welcome to all the new contributors in 26.10! The growth of ClickHouse's community is humbling, and we are always grateful for the contributions that have made ClickHouse so popular.

Below are the names of the new contributors:

*ARON, Aarav, Abdullah Kaya, Akanshaak, Aleh Strakachuk, Aleksandr Efimov, Alexey Sitnikov, Andrea Debernardi, Andrew Wilkins, Angelica Ismailos, Armin Braun, Arvind Kumar, Ashish Choubey, Azarudeen Shariff A, Azhar Izzannada E, Bentsi Leviav, Chester, Craig Ringer, David Rolfe, Denis Voytyuk, Dimitri König, Frank Denis, Fábio Neves, GON, Gheorghe Pucea, Ilias, Ilias Aberkane, Javier G. Sogo, Jay Pokale, Jaysurya Ray, Jonathan Ackerman, Knut-Aage-Hofseth, Krithika Balagurunathan, LeeTeng2001, LyJacky, Maksim Andreev, Mike Lewis, Mishalski, Mohammed Sohail, Nick Akey, Oleg Milanov, Prince Maurya, RJ, Ray Winkelman, Rion Bora, Sam Wolfberg, Shahzeb Ali, Thomas Sileghem, Tom Alard, Unamed, Uwez Khan, Vadim Lopatin, Vector, Vitaly Pryakhin, Vlad, VrtxOmega, Zach Rippas, ZainnQureshii, ajay tomar, amogiska, antonioscaramuzzino, arc1999, artemkulyk, awss, azharizz, bentsileviav, bisht2050, clickgapai, comino, dhruvtaneja-ch, dosedaf, erezrokah, gonappuccino, jacky, linjiayu1025-collab, namtran1812, seva-potapov, sunliqiang, superdiaodiao, tianhui-fu, tridao, turbolytics, turbolytics.io, ultrabig, vector524*

Hint: if you’re curious how we generate this list… [here](https://gist.github.com/gingerwizard/5a9a87a39ba93b422d8640d811e269e9).

<iframe width="768" height="432" src="https://www.youtube.com/embed/k30ikPXNpTQ?si=oNEc1DPhJU-Lh3rm" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

You can also [view the slides from the presentation](https://presentations.clickhouse.com/2026-release-26.10).

## Function composition operator

### Contributed by Ivan Esipov and Alexey Milovidov

If you’ve used ClickHouse’s higher-order functions, like [`arrayMap`](https://clickhouse.com/docs/reference/functions/regular-functions/array-functions#arrayMap) and [`arrayFilter`](https://clickhouse.com/docs/reference/functions/regular-functions/array-functions#arrayFilter), you’ll know that the lambda you pass in can quickly turn into a series of nested function calls. ClickHouse 26.10 adds a [function composition operator](https://clickhouse.com/docs/reference/operators#function-composition-operator), which means we can now create a pipeline of functions joined with the `|` operator, making these lambdas easier to read.

Let’s see how the two styles compare when extracting site names from some URLs.
We're going to lowercase the URL, strip the `www` prefix, take the first significant subdomain, and then uppercase it.

```sql
WITH [
    'https://WWW.ClickHouse.com/docs',
    'https://GitHub.com/ClickHouse/ClickHouse',
    'https://www.anthropic.com/news'
] AS urls
SELECT
    arrayMap(x -> upper(firstSignificantSubdomain(domainWithoutWWW(lower(x)))), urls) AS with_lambda,
    arrayMap(lower | domainWithoutWWW | firstSignificantSubdomain | upper, urls) AS with_composition
FORMAT Vertical;
```

```text
Row 1:
──────
with_lambda:      ['CLICKHOUSE','GITHUB','ANTHROPIC']
with_composition: ['CLICKHOUSE','GITHUB','ANTHROPIC']
```

Both columns give the same result, but the composed version reads more like a list of steps. Each function here can be called with just the value passed along, so we didn’t need to say where it should go.

To pass additional arguments to a function, use `_` to mark where the value from the pipeline goes. For example, `substring(_, 1, 3)` takes the first three characters of the string passed along:

```sql
WITH ['ClickHouse', 'Anthropic', 'OpenAI'] AS companies
SELECT
    arrayMap(x -> substring(upper(x), 1, 3), companies) AS with_lambda,
    arrayMap(upper | substring(_, 1, 3), companies) AS with_composition
FORMAT Vertical;
```

```text
Row 1:
──────
with_lambda:      ['CLI','ANT','OPE']
with_composition: ['CLI','ANT','OPE']
```

Higher-order functions can also take several arrays of the same length, which they process position by position. In that case, use `_1` for the element from the first array, `_2` for the matching element from the second, and so on. Let’s work out the line totals for an order by multiplying each price by its quantity, and then format the results as prices:

```sql
WITH
    [49.99, 189.00, 19.50] AS prices,
    [2, 1, 4] AS quantities
SELECT
    arrayMap(multiply(_1, _2) | toString | concat('$', _), prices, quantities) AS line_totals;
```

```text
┌─line_totals─────────────┐
│ ['$99.98','$189','$78'] │
└─────────────────────────┘
```

Placeholders also work on their own, without `|`, as a shorter way of writing a lambda. For example, `_1 * _2` means the same thing as `(price, quantity) -> price * quantity`, as shown in the following example:

```sql
WITH
    ['Keyboard', 'Monitor', 'Mouse'] AS products,
    [49.99, 189.00, 19.50] AS prices,
    [2, 1, 4] AS quantities
SELECT
    arrayMap(_1 * _2, prices, quantities) AS line_totals,
    arrayMap(concat(_1, ' x', toString(_2)), products, quantities) AS order_lines
FORMAT Vertical;
```

```text
Row 1:
──────
line_totals: [99.98,189,78]
order_lines: ['Keyboard x2','Monitor x1','Mouse x4']
```

Under the hood, ClickHouse turns the pipeline into an ordinary lambda during query analysis. We can see this by running [`EXPLAIN SYNTAX`](https://clickhouse.com/docs/reference/statements/explain#explain-syntax) with `run_query_tree_passes = 1`, which shows the query after the analyzer has rewritten it:

```sql
EXPLAIN SYNTAX run_query_tree_passes = 1
SELECT arrayMap(
    lower | domainWithoutWWW | firstSignificantSubdomain | upper,
    ['https://WWW.ClickHouse.com/docs']
) AS sites;
```

```text
SELECT arrayMap(lambda(tuple(__composed_arg_1), upper(firstSignificantSubdomain(domainWithoutWWW(lower(__composed_arg_1))))), _CAST(['https://WWW.ClickHouse.com/docs'], 'Array(String)')) AS sites
FROM system.one AS __table1
```

The `|` chain has become a lambda with the same nested expression we started with, so the two styles run in exactly the same way and you can use whichever one you prefer.

## Quotas on inserted rows

### Contributed by Alexey Milovidov

[Quotas](https://clickhouse.com/docs/reference/statements/create/quota) let you limit how much a user can do in a given time interval. ClickHouse 26.10 adds a `written_rows` counter, so you can cap ingestion by the number of rows a user writes.

Let’s create a table and an `ingest` user who can write at most 100,000 rows, across no more than 250 inserts, per minute:

```sql
CREATE TABLE events (id UInt64) 
ORDER BY id;
```

```sql
CREATE USER ingest IDENTIFIED WITH no_password;
GRANT INSERT, SELECT ON default.events TO ingest;
```

```sql
CREATE QUOTA ingest_limit
FOR INTERVAL 1 minute MAX written_rows = 100000, query_inserts = 250
TO ingest;
```

The first insert of 60,000 rows goes through without any problems:

```sql
INSERT INTO events 
SELECT number 
FROM numbers(60000);
```

But if we run the same insert again within that minute, it takes us over the limit:

```text
Received exception:
Code: 201. DB::Exception: Quota for user `ingest` for 60s has been exceeded: written_rows = 120000/100000. Interval will end at 2026-10-23 14:00:00. Name of quota template: `ingest_limit`. (QUOTA_EXCEEDED)
```

The rejected insert doesn’t write any data, so the table still contains 60,000 rows. As with other quotas, you can see how close each user is to their limits in [`system.quotas_usage`](https://clickhouse.com/docs/reference/system-tables/quotas_usage):

```sql
SELECT quota_name, written_rows, max_written_rows, query_inserts, max_query_inserts
FROM system.quotas_usage
WHERE quota_name = 'ingest_limit'
FORMAT Vertical;
```

```text
Row 1:
──────
quota_name:        ingest_limit
written_rows:      120000
max_written_rows:  100000
query_inserts:     2
max_query_inserts: 250
```

## New Array and Map functions

### Contributed by Minh Vu, Jimmy Aguilar Mena, UnamedRus, and Alexey Milovidov

This 26.10 release also brings a handful of new functions for working with arrays and maps. 

[`arrayMinIndex`](https://clickhouse.com/docs/reference/functions/regular-functions/array-functions#arrayMinIndex) and [`arrayMaxIndex`](https://clickhouse.com/docs/reference/functions/regular-functions/array-functions#arrayMaxIndex) return the position of the smallest and largest element, optionally after applying a lambda to each one. [`arrayRemoveAt`](https://clickhouse.com/docs/reference/functions/regular-functions/array-functions#arrayRemoveAt) removes the element at a given position, and negative positions count back from the end.

Let’s see what each of them returns on some small arrays:

```sql
WITH [2,5,10,9,7] AS values

SELECT
    arrayMinIndex(values) AS min_index,
    arrayMaxIndex(values) AS max_index,
    arrayMaxIndex(x -> length(x), ['a', 'abc', 'ab', 'abcd']) AS longest_index,
    arrayRemoveAt(values, 2) AS remove_second,
    arrayRemoveAt(values, -1) AS remove_last
FORMAT Vertical;
```

```text
Row 1:
──────
min_index:     1
max_index:     3
longest_index: 4
remove_second: [2,10,9,7]
remove_last:   [2,5,10,9]
```

> Array indexes in ClickHouse start at 1, so the smallest value, `2`, which is in first position in the array, has an index of `1`

We could then can pass the results straight into another array to look up a matching value. In the following example, we find the coldest and warmest days of the week, and then drop Friday from the list:

```sql
WITH
    ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'] AS days,
    [18.5, 21.2, 16.9, 24.3, 22.0] AS temps
SELECT
    days[arrayMinIndex(temps)] AS coldest,
    days[arrayMaxIndex(temps)] AS warmest,
    arrayRemoveAt(days, -1) AS without_friday;
```

```text
┌─coldest─┬─warmest─┬─without_friday────────────┐
│ Wed     │ Thu     │ ['Mon','Tue','Wed','Thu'] │
└─────────┴─────────┴───────────────────────────┘
```

For maps, [`mapRemove`](https://clickhouse.com/docs/reference/functions/regular-functions/tuple-map-functions#mapRemove) drops a key, [`mapEntries`](https://clickhouse.com/docs/reference/functions/regular-functions/tuple-map-functions#mapEntries) returns the key-value pairs as an array of tuples, and [`mapContainsKeyValue`](https://clickhouse.com/docs/reference/functions/regular-functions/tuple-map-functions#mapContainsKeyValue) checks whether a map contains a specific key-value pair:

```sql
WITH map('env', 'prod', 'region', 'eu-west-1', 'team', 'payments') AS labels
SELECT
    mapRemove(labels, 'team') AS without_team,
    mapEntries(labels) AS entries,
    mapContainsKeyValue(labels, 'env', 'prod') AS is_prod
FORMAT Vertical;
```

```text
Row 1:
──────
without_team: {'env':'prod','region':'eu-west-1'}
entries:      [('env','prod'),('region','eu-west-1'),('team','payments')]
is_prod:      1
```

`mapContainsKeyValue` can also use [text indexes](https://clickhouse.com/docs/reference/engines/table-engines/mergetree-family/textindexes), which makes filtering on labels a lot quicker when you have plenty of rows.

Finally, the [`-Map` combinator](https://clickhouse.com/docs/reference/functions/aggregate-functions/combinators#-map) no longer needs a `Map` column. You can pass the key as the last argument instead, which makes it easy to aggregate per key directly from rows:

```sql
SELECT
    sumMap(views, country) AS views_by_country,
    argMaxMap(page, views, country) AS top_page_by_country
FROM VALUES('country String, page String, views UInt32',
    ('UK', '/docs', 120), ('UK', '/blog', 340),
    ('US', '/docs', 910), ('US', '/pricing', 450),
    ('DE', '/blog', 75));
```

```text
┌─views_by_country─────────────┬─top_page_by_country──────────────────────┐
│ {'DE':75,'UK':460,'US':1360} │ {'DE':'/blog','UK':'/blog','US':'/docs'} │
└──────────────────────────────┴──────────────────────────────────────────┘
```

## SQL-compatible integer division

### Contributed by Ilya Yatsishin

In ClickHouse, dividing one integer by another has always returned a floating-point number, so `7 / 2` gives you `3.5`. PostgreSQL, SQL Server, and SQLite all truncate that to `3` instead.

Alexey’s take on the release call was that ClickHouse is right and everyone else is wrong, but if you’re porting queries from another database and need them to be wrong in the same way, there’s now a setting for that. Here’s the default behaviour:

```sql
SELECT 7 / 2, -7 / 2, 7 / 2.0, toTypeName(7 / 2);
```

```text
┌─divide(7, 2)─┬─divide(-7, 2)─┬─divide(7, 2.)─┬─toTypeName(divide(7, 2))─┐
│          3.5 │          -3.5 │           3.5 │ Float64                  │
└──────────────┴───────────────┴───────────────┴──────────────────────────┘
```

And if you prefer the PostgreSQL way, you can enable [`sql_compatible_division_for_integers`](https://clickhouse.com/docs/reference/settings/session-settings/other#sql_compatible_division_for_integers):

```sql
SET sql_compatible_division_for_integers = 1;

SELECT 7 / 2, -7 / 2, 7 / 2.0, toTypeName(7 / 2);
```

```text
┌─divide(7, 2)─┬─divide(-7, 2)─┬─divide(7, 2.)─┬─toTypeName(divide(7, 2))─┐
│            3 │            -3 │           3.5 │ UInt8                    │
└──────────────┴───────────────┴───────────────┴──────────────────────────┘
```

The result is truncated towards zero and keeps an integer type, while dividing by a floating-point number still gives you a float. With the setting enabled, dividing by zero throws an error rather than returning `inf`:

```sql
SET sql_compatible_division_for_integers = 1;

SELECT 1 / 0;
```

```text
Received exception:
Code: 153. DB::Exception: Division by zero: In scope SELECT divideExact(1, 0) AS `divide(1, 0)`. (ILLEGAL_DIVISION)
```

The setting is disabled by default. Views and other stored definitions keep the division behaviour they were created with, so enabling it won’t change the results of your existing views.

## IN subqueries can spill to disk

### Contributed by Nihal Z. Miaji

When we use `IN` with a subquery, ClickHouse builds a set of the values returned by that subquery and checks the outer query’s rows against it. A large set can use a lot of memory. ClickHouse 26.10 adds the ability to [spill this set to disk](https://clickhouse.com/docs/reference/statements/in#in-in-external-memory), allowing the query to complete with a smaller memory limit.

Let’s try it with the [UK property prices dataset](https://clickhouse.com/docs/get-started/sample-datasets/uk-price-paid), which contains property sales in England and Wales since 1995. We want to count sales in 2024 at addresses that also have a recorded sale before 2024. We’ll match on the postcode and the two address fields, `addr1` and `addr2`, which identify the building and, where applicable, the flat. This is an address-based match rather than a permanent property identifier, and we’re counting sales rather than distinct properties.

First, let’s give the query a 4 GiB memory limit and leave spilling disabled:

```sql
SELECT count() AS repeat_address_sales_2024
FROM uk_price_paid
WHERE date >= '2024-01-01'
  AND date < '2025-01-01'
  AND (postcode1, postcode2, addr1, addr2) IN
  (
      SELECT postcode1, postcode2, addr1, addr2
      FROM uk_price_paid
      WHERE date < '2024-01-01'
  )
SETTINGS max_threads = 2,
         max_memory_usage = '4Gi',
         max_bytes_before_external_set = 0;
```

```text
┌─repeat_address_sales_2024─┐
│                    558458 │
└───────────────────────────┘

1 row in set. Elapsed: 5.777 sec. Processed 60.90 million rows, 966.34 MB (10.54 million rows/s., 167.27 MB/s.)
Peak memory usage: 1.96 GiB.
```

The subquery reads 29.3 million earlier sales to build its set of addresses. On ClickHouse 26.10, this query used 1.96 GiB of peak memory. Let's see what happens if we reduce the memory limit to 512 MiB:

```sql
SELECT count() AS repeat_address_sales_2024
FROM uk_price_paid
WHERE date >= '2024-01-01'
  AND date < '2025-01-01'
  AND (postcode1, postcode2, addr1, addr2) IN
  (
      SELECT postcode1, postcode2, addr1, addr2
      FROM uk_price_paid
      WHERE date < '2024-01-01'
  )
SETTINGS max_threads = 2,
         max_memory_usage = '512Mi',
         max_bytes_before_external_set = 0;
```

```text
Elapsed: 0.978 sec. Processed 7.93 million rows, 122.04 MB (8.10 million rows/s., 124.75 MB/s.)

Received exception:
Code: 241. DB::Exception: Query memory limit exceeded: would use 537.51 MiB (attempt to allocate chunk of 63.96 MiB), maximum: 512.00 MiB: While executing CreatingSetsTransform. (MEMORY_LIMIT_EXCEEDED)
```

ClickHouse runs out of memory. We can now enable spilling by setting [`max_bytes_before_external_set`](https://clickhouse.com/docs/reference/settings/session-settings/max-bytes#max_bytes_before_external_set). Let’s use a threshold of 128 MiB, keeping the query’s overall memory limit at 512 MiB:

```sql
SELECT count() AS repeat_address_sales_2024
FROM uk_price_paid
WHERE date >= '2024-01-01'
  AND date < '2025-01-01'
  AND (postcode1, postcode2, addr1, addr2) IN
  (
      SELECT postcode1, postcode2, addr1, addr2
      FROM uk_price_paid
      WHERE date < '2024-01-01'
  )
SETTINGS max_threads = 2,
         max_memory_usage = '512Mi',
         max_bytes_before_external_set = '128Mi';
```

```
┌─repeat_address_sales_2024─┐
│                    558458 │
└───────────────────────────┘

1 row in set. Elapsed: 3.185 sec. Processed 60.90 million rows, 966.48 MB (19.12 million rows/s., 303.44 MB/s.)
Peak memory usage: 203.11 MiB.
```

This time we have a peak memory usage of 203 MiB. That’s above our 128 MiB spill threshold, which tells ClickHouse when to start spilling rather than imposing a hard memory limit. The query also needs memory to read and process data, so we set the spill threshold below the overall 512 MiB limit.

If we look at profile events, by pressing the space bar while the query's running, we'll see that ClickHouse spilled one set to disk and wrote four parts:

```text
SetsSpilledToDisk:          1
ExternalSetWritePart:       4
ExternalSetCompressedBytes: 470342352
```

The following table summarizes the various configurations we used:


| Memry limit | Spilling | Result | Peak memory |
|---|---|---|---|
| 4 GiB | Disabled | 558,458 | 1.96 GiB |
| 512 MiB | Disabled | Memory limit exceeded | — |
| 512 MiB | 128 MiB | 558,458 | 203 MiB |

## Faster GROUP BY with LowCardinality columns

### Contributed by artemkulyk, Samuel Krempaský, and Alexey Milovidov

ClickHouse 26.10 improves grouping by multiple [`LowCardinality`](https://clickhouse.com/docs/reference/data-types/lowcardinality) columns. It can serialize the grouping keys directly from their dictionaries and cache aggregate-state lookups for repeated combinations of keys.

Let’s reuse our `uk_price_paid` table to count sales and calculate the average price for each combination of county, district, town, and outward postcode. All four grouping columns have a column type of `LowCardinality(String)`:

```sql
SELECT
    county,
    district,
    town,
    postcode1,
    count() AS sales,
    avg(price) AS average_price
FROM uk_price_paid
GROUP BY county, district, town, postcode1
SETTINGS use_query_cache = 0
FORMAT Null;
```

We use [`FORMAT Null`](https://clickhouse.com/docs/reference/formats/Null) to run the query without printing its 15,409 result rows, so terminal output doesn’t affect the comparison.

Let’s run the query three times on ClickHouse 26.9:

```text
0 rows in set. Elapsed: 0.289 sec. Processed 30.45 million rows, 331.39 MB (105.20 million rows/s., 1.14 GB/s.)
Peak memory usage: 170.67 MiB.

0 rows in set. Elapsed: 0.269 sec. Processed 30.45 million rows, 331.39 MB (113.29 million rows/s., 1.23 GB/s.)
Peak memory usage: 171.81 MiB.

0 rows in set. Elapsed: 0.255 sec. Processed 30.45 million rows, 331.39 MB (119.19 million rows/s., 1.30 GB/s.)
Peak memory usage: 177.98 MiB.
```

And now three times on ClickHouse 26.10, using the same data and table layout. Both versions use the default 12 threads on my machine:

```text
0 rows in set. Elapsed: 0.242 sec. Processed 30.45 million rows, 331.39 MB (125.90 million rows/s., 1.37 GB/s.)
Peak memory usage: 128.49 MiB.

0 rows in set. Elapsed: 0.181 sec. Processed 30.45 million rows, 331.39 MB (168.49 million rows/s., 1.83 GB/s.)
Peak memory usage: 124.16 MiB.

0 rows in set. Elapsed: 0.171 sec. Processed 30.45 million rows, 331.39 MB (178.37 million rows/s., 1.94 GB/s.)
Peak memory usage: 127.35 MiB.
```

If we take the best time from each version, the query took 255 milliseconds on 26.9 and 171 milliseconds on 26.10, meaning 26.10 is just over 30% quicker. 

## Top-K dynamic filtering for GROUP BY

### Contributed by Alexey Milovidov and Konstantin Bogdanov

[ClickHouse 25.12](https://clickhouse.com/blog/clickhouse-release-25-12) introduced dynamic filtering for `ORDER BY … LIMIT` queries, using the current Top-K boundary to avoid unnecessary column reads and skip granules through minmax indexes. ClickHouse 26.10 extends this approach to `GROUP BY` queries and adds granule skipping through the [primary index](https://clickhouse.com/docs/concepts/core-concepts/primary-indexes).

Let’s reuse our UK property data to find the ten most recent dates with recorded sales, along with the number of sales and their average price. We’ll create a separate table containing the two columns used by the query, sorted by `date`. This layout lets ClickHouse use both mechanisms: filter older sales before reading their prices, and use the primary index to skip granules whose dates are all older than the cutoff.

```sql
CREATE TABLE uk_price_paid_by_date
ENGINE = MergeTree
ORDER BY date
AS SELECT date, price FROM uk_price_paid;

OPTIMIZE TABLE uk_price_paid_by_date FINAL;
```

This copies all 30m sales and merges the new table into a single part. We’ll run the query on ClickHouse 26.10 so we can see what the output looks like:

```sql
SELECT
    date,
    count() AS sales,
    round(avg(price)) AS average_price
FROM uk_price_paid_by_date
GROUP BY date
ORDER BY date DESC
LIMIT 10
SETTINGS
    enable_group_by_top_k_dynamic_filtering = 0,
    use_query_condition_cache = 0,
    use_query_cache = 0;
```

The query returns the following ten dates:

```text
┌───────date─┬─sales─┬─average_price─┐
│ 2025-07-31 │    26 │        300021 │
│ 2025-07-30 │    39 │        316864 │
│ 2025-07-29 │    92 │        344986 │
│ 2025-07-28 │   220 │        317645 │
│ 2025-07-27 │     4 │        242998 │
│ 2025-07-25 │   926 │        316243 │
│ 2025-07-24 │   388 │        358814 │
│ 2025-07-23 │   437 │        347647 │
│ 2025-07-22 │   373 │        332035 │
│ 2025-07-21 │   662 │        337260 │
└────────────┴───────┴───────────────┘
```

Time to test it with and without the optimization using clickhouse-local. The timings come from the CLI’s `--time` output, and the read counts/peak memory come from `--print-profile-events`:

| Run | Query time | Rows read | Data processed | Peak memory |
|---|---|---|---|---|
| 1 | 45 ms | 30,452,463 | 182.71 MB | 7.18 MiB |
| 2 | 27 ms | 30,452,463 | 182.71 MB | 7.26 MiB |
| 3 | 31 ms | 30,452,463 | 182.71 MB | 7.26 MiB |

Changing [`enable_group_by_top_k_dynamic_filtering`](https://clickhouse.com/docs/reference/settings/session-settings/enable#enable_group_by_top_k_dynamic_filtering) to `1` gives us:

| Run | Query time | Rows read | Data processed | Peak memory |
|---|---|---|---|---|
| 1 | 9 ms | 1,728,263 | 10.37 MB | 7.30 MiB |
| 2 | 8 ms | 1,793,672 | 10.50 MB | 7.30 MiB |
| 3 | 10 ms | 1,728,263 | 10.11 MB | 7.24 MiB |

From the table of results, we can see that with filtering enabled, ClickHouse reads around 94% fewer rows. The runs with the optimization skipped 3,529, 3,521, and 3,529 granules respectively, whereas no granules were skipped without it. The exact amount of work varies as the parallel aggregation streams discover and publish their cutoffs.

We can confirm that whole granules were skipped using the `TopKGranulesSkippedByPrimaryKey` profile event. With `--print-profile-events --profile-events-delay-ms=-1`, the CLI reports the final event totals. For the first enabled run, the relevant values were:

```text
SelectedRows:                     1728263
SelectedBytes:                    10369578
TopKGranulesSkippedByPrimaryKey:  3529
```

## Columns cache

### Contributed by Alexey Milovidov

ClickHouse 26.10 introduces an experimental columns cache, which keeps deserialized column data in memory, saving subsequent queries from decompressing and deserializing it again.

Let’s reuse our UK property dataset to count sales where the first address field contains `HOUSE`. We'll create a copy containing the price and address columns, keeping the original sort order:

```sql
CREATE TABLE uk_price_paid_columns_cache
ENGINE = MergeTree
ORDER BY (postcode1, postcode2, addr1, addr2)
SETTINGS min_bytes_for_wide_part = 0,
         min_rows_for_wide_part = 0
AS SELECT postcode1, postcode2, addr1, addr2, price FROM uk_price_paid;
```

The cache currently supports [wide MergeTree parts](https://clickhouse.com/docs/reference/engines/table-engines/mergetree-family/mergetree#data-storage). Setting both size thresholds to `0` forces this format.

First, let's run the query with the columns cache disabled:

```sql
SELECT count() AS house_sales
FROM uk_price_paid_columns_cache
WHERE addr1 LIKE '%HOUSE%'
SETTINGS use_columns_cache = 0,
         use_query_cache = 0,
         use_query_condition_cache = 0,
         log_queries = 1,
         log_profile_events = 1,
         log_comment = 'sorted-columns-cache:off-1';
```

```text
┌─house_sales─┐
│      904871 │
└─────────────┘
```

After one unmeasured run to warm the filesystem cache, we'll run this query three times, using `sorted-columns-cache:off-1`, `sorted-columns-cache:off-2`, and `sorted-columns-cache:off-3` as the log comments.

Then we'll change [`use_columns_cache`](https://clickhouse.com/docs/reference/settings/session-settings/use#use_columns_cache) to `1` and run it three more times, using comments `sorted-columns-cache:on-1`, `sorted-columns-cache:on-2`, and `sorted-columns-cache:on-3`. The first enabled run populates the columns cache, and the next two reuse it.

With caching enabled, the query caches `addr1`. It doesn't read `price`, for example, so that column isn't cached. But, if we added a condition on `price`, any data read from that column would also be cached.

With query logging enabled, we can retrieve the timings and cache counters from [`system.query_log`](https://clickhouse.com/docs/reference/system-tables/query_log), using the following query:

```sql
SYSTEM FLUSH LOGS;

SELECT
    log_comment AS run,
    query_duration_ms AS queryTime,
    ProfileEvents['ColumnsCacheHits'] AS cacheHits,
    ProfileEvents['ColumnsCacheMisses'] AS cacheMisses,
    ProfileEvents['SelectedRows'] AS selectedRows
FROM
(
    SELECT *
    FROM system.query_log
    WHERE type = 'QueryFinish'
      AND startsWith(log_comment, 'sorted-columns-cache:')
      AND log_comment != 'sorted-columns-cache:warmup'
    ORDER BY query_start_time_microseconds DESC
    LIMIT 6
)
ORDER BY query_start_time_microseconds
FORMAT Markdown;
```

| run | queryTime | cacheHits | cacheMisses | selectedRows |
|:-|-:|-:|-:|-:|
| sorted-columns-cache:off-1 | 34 | 0 | 0 | 30452463 |
| sorted-columns-cache:off-2 | 32 | 0 | 0 | 30452463 |
| sorted-columns-cache:off-3 | 33 | 0 | 0 | 30452463 |
| sorted-columns-cache:on-1 | 37 | 0 | 3718 | 30452463 |
| sorted-columns-cache:on-2 | 12 | 3718 | 0 | 30452463 |
| sorted-columns-cache:on-3 | 12 | 3718 | 0 | 30452463 |

With the columns cache disabled, the query takes 32–34 milliseconds. `cacheHits` is 0 because ClickHouse isn't looking in the cache. 

The run in which the cache gets populated takes 37 milliseconds, and the next two runs that use the cache each take 12 milliseconds, with all 3,718 granules of `addr1` read from the columns cache.

`SelectedRows` stays the same: ClickHouse still evaluates the filter against all 30.45 million rows, but it can reuse the decoded address data. The cache stores column data rather than the query result, so other queries reading the same data can benefit too.

## LATERAL JOIN

### Contributed by Dimitri König and Alexey Milovidov

ClickHouse 26.10 adds experimental support for [`LATERAL JOIN`](https://clickhouse.com/docs/reference/statements/select/join#lateral-join), which lets a subquery reference columns from a table that appears before it. We can enable it by setting `allow_experimental_lateral_join = 1`.

We'll use the [IMDb dataset from our joins examples](https://clickhouse.com/blog/clickhouse-fully-supports-joins-part1#test-data-and-resources) to find the three highest-rated films for each of three actors. The `actors` table contains their names, `movies` contains film details and ratings, and `roles` connects actors to the films they appeared in.

```sql
SELECT
    concat(a.first_name, ' ', a.last_name) AS actor,
    top_titles.name AS title,
    top_titles.year AS year,
    round(top_titles.rank, 1) AS rating
FROM actors AS a
JOIN LATERAL
(
    SELECT m.id, m.name, m.year, m.rank
    FROM roles AS r
    INNER JOIN movies AS m ON r.movie_id = m.id
    WHERE r.actor_id = a.id
      AND m.rank IS NOT NULL
    GROUP BY m.id, m.name, m.year, m.rank
    ORDER BY m.rank DESC, m.year DESC, m.id
    LIMIT 3
) AS top_titles ON true
WHERE (a.first_name, a.last_name) IN
    (('Tom', 'Hanks'), ('Meryl', 'Streep'), ('Denzel', 'Washington'))
ORDER BY actor, rating DESC, year DESC, top_titles.id
SETTINGS allow_experimental_lateral_join = 1;
```

Line 12 is the important one: `WHERE r.actor_id = a.id`. The `a.id` value comes from `actors AS a` in the outer query. The `LATERAL` lets our inner query use that value, which means we find the top three films for this actor. `LIMIT 3` applies per actor, rather than selecting three films across the whole dataset.

For each selected actor, the inner query finds their roles, joins them to the film details, and excludes films without a rating. The `GROUP BY` removes duplicate films where an actor has multiple role records. It then sorts by rating, using the year and film ID to break ties, and returns the top three.

```text
┌─actor─────────────┬─title──────────────────┬─year─┬─rating─┐
│ Denzel Washington │ Glory                  │ 1989 │    8.1 │
│ Denzel Washington │ Much Ado About Nothing │ 1993 │    7.5 │
│ Denzel Washington │ Antwone Fisher         │ 2002 │    7.4 │
│ Meryl Streep      │ Manhattan              │ 1979 │    8.2 │
│ Meryl Streep      │ Deer Hunter, The       │ 1978 │    8.1 │
│ Meryl Streep      │ Adaptation.            │ 2002 │    7.9 │
│ Tom Hanks         │ Saving Private Ryan    │ 1998 │    8.3 │
│ Tom Hanks         │ Green Mile, The        │ 1999 │    8.1 │
│ Tom Hanks         │ Toy Story 2            │ 1999 │    8.1 │
└───────────────────┴────────────────────────┴──────┴────────┘
```

We get nine rows: three films for each actor. 

## JOINs with arbitrary conditions

### Contributed by Vladimir Cherkasov and Alexey Milovidov

ClickHouse 26.10 also supports [JOINs with arbitrary `ON` conditions](https://clickhouse.com/docs/reference/statements/select/join#join-with-an-arbitrary-on-condition), including those without an equality condition between the tables. Let's use this to categorize website traffic using URL patterns.

First, we'll create a table containing page view counts:

```sql
CREATE TABLE page_views
(
    path String,
    views UInt64
);

INSERT INTO page_views VALUES
    ('/docs/getting-started', 1200),
    ('/docs/sql-reference/functions', 850),
    ('/blog/clickhouse-release-26-10', 2400),
    ('/pricing', 600),
    ('/about', 300);
```

We'll store the categorization rules in a separate table. The `%` wildcard matches any sequence of characters:

```sql
CREATE TABLE page_categories
(
    pattern String,
    category String
);

INSERT INTO page_categories VALUES
    ('/docs/%', 'Documentation'),
    ('/blog/%', 'Blog'),
    ('/pricing', 'Pricing');
```

We can now join the tables using [`LIKE`](https://clickhouse.com/docs/reference/functions/regular-functions/string-search-functions#like) to match each path to a category:

```sql
SELECT p.path, p.views, c.category
FROM page_views AS p
LEFT JOIN page_categories AS c ON p.path LIKE c.pattern
ORDER BY p.views DESC;
```

```text
┌─path───────────────────────────┬─views─┬─category──────┐
│ /blog/clickhouse-release-26-10 │  2400 │ Blog          │
│ /docs/getting-started          │  1200 │ Documentation │
│ /docs/sql-reference/functions  │   850 │ Documentation │
│ /pricing                       │   600 │ Pricing       │
│ /about                         │   300 │               │
└────────────────────────────────┴───────┴───────────────┘
```

Keep in mine that the flexibility of arbitrary joins can be expensive: the block nested loop join checks every pair of rows, so it can be as slow as a cross join and is used as a last resort by the query planner.

## Freeform input format

### Contributed by Tri Dao and Alexey Milovidov

ClickHouse 26.10 also adds the `Freeform` input format, which infers columns and their types from consistently structured text.

Let's see how it works by piping the output of `ls -l` into [clickhouse-local](https://clickhouse.com/docs/concepts/features/tools-and-utilities/clickhouse-local). The piped input will be available as `table` and can be queried the same way as any other table. The following query desribes the output of `ls -l`:

```bash
ls -l **/*.parquet | 
./clickhouse --input-format Freeform --query "DESCRIBE TABLE table"
```

```text
c0	String
c1	Int64
c2	String
c3	String
c4	Int64
c5	Int64
c6	String
c7	Int64
c8	Int64
c9	String
```

We can see from this output that `ls -l` outputs 10 columns, which are named `c0` to `c9`. We can query `table` to return all columns with the following query;

```bash
ls -l **/*.parquet | 
./clickhouse --input-format Freeform --query "FROM table FORMAT Vertical"
```

```text
Row 1:
──────
c0: -rw-r--r--@
c1: 1
c2: markhneedham
c3: staff
c4: 2048074919 -- 2.05 billion
c5: 30
c6: Oct
c7: 16
c8: 23
c9: benchmarks/amazon-columns-cache/data/amazon_reviews_2010.snappy.parquet

Row 2:
──────
c0: -rw-r--r--@
c1: 1
c2: markhneedham
c3: staff
c4: 3013406813 -- 3.01 billion
c5: 30
c6: Oct
c7: 16
c8: 27
c9: benchmarks/amazon-columns-cache/data/amazon_reviews_2011.snappy.parquet
```

Let's give the columns meaningful names, format the file sizes, and combine the date fields into a timestamp. This listing doesn't include a year, so we'll use the current year for these recent files:

```bash
ls -l **/*.parquet |
./clickhouse --input-format Freeform --query "
    SELECT
        c9 AS file,
        formatReadableSize(c4) AS size,
        parseDateTimeBestEffort(
            format('{} {} {} {}:{}', c5, c6, toYear(today()), c7, c8)
        ) AS modified
    FROM table
    ORDER BY c4 DESC
    FORMAT Vertical"
```

```text
Row 1:
──────
file:     benchmarks/amazon-columns-cache/data/amazon_reviews_2011.snappy.parquet
size:     2.81 GiB
modified: 2026-10-30 16:27:00

Row 2:
──────
file:     benchmarks/amazon-columns-cache/data/amazon_reviews_2010.snappy.parquet
size:     1.91 GiB
modified: 2026-10-30 16:23:00
```

## SQLite import and export

### Contributed by Yue Ni and Alexey Milovidov

ClickHouse already supports querying SQLite databases through a [database engine](https://clickhouse.com/docs/reference/engines/database-engines/sqlite), [table engine](https://clickhouse.com/docs/reference/engines/table-engines/integrations/sqlite), and [table function](https://clickhouse.com/docs/reference/functions/table-functions/sqlite). Version 26.10 adds [SQLite as an input and output format](https://clickhouse.com/docs/reference/formats/SQLite), letting us [export query results](https://clickhouse.com/docs/reference/statements/select/into-outfile) directly into a SQLite database file, ready to open with SQLite tools or share with someone else.

Let's reuse our IMDb `movies` table to count films and calculate their average rating for each year of the 1990s:

```sql
SELECT
    year,
    toInt64(count()) AS films,
    round(avg(rank), 2) AS average_rating
FROM movies
WHERE year BETWEEN 1990 AND 1999
GROUP BY year
ORDER BY year
INTO OUTFILE 'films.sqlite'
SETTINGS output_format_sqlite_table_name = 'films_by_year';
```

ClickHouse uses the SQLite format becaues of the `.sqlite` extension of the output file, but we can also specify the output explicitly by specifying `FORMAT SQLite` after the file name. We write ten results in a table called `films_by_year`.

We can open the file with the `sqlite3` command-line tool and query it:

```bash
sqlite3 -header -column films.sqlite \
  'SELECT * FROM films_by_year ORDER BY year LIMIT 5;'
```

```text
year  films  average_rating
----  -----  --------------
1990  6098   5.33
1991  6068   5.69
1992  6580   5.53
1993  6900   5.55
1994  7502   5.43
```

ClickHouse can also read the file back, inferring the column names and types:

```sql
SELECT *
FROM file('films.sqlite')
ORDER BY year
LIMIT 5;
```

```text
┌─year─┬─films─┬─average_rating─┐
│ 1990 │  6098 │           5.33 │
│ 1991 │  6068 │           5.69 │
│ 1992 │  6580 │           5.53 │
│ 1993 │  6900 │           5.55 │
│ 1994 │  7502 │           5.43 │
└──────┴───────┴────────────────┘
```

## String filtering during the scan

### Contributed by Alexey Milovidov

ClickHouse 26.10 can check string filters such as `LIKE`, `startsWith`, and `endsWith` while deserializing a column, avoiding copying non-matching strings into memory. The optimization is enabled by default through `apply_string_filters_during_scan`.

Let's try it with the [Amazon reviews dataset](https://clickhouse.com/blog/clickhouse-gets-lazier-and-faster-introducing-lazy-materialization). We'll load the 2010 and 2011 Parquet files from our Freeform example into a MergeTree table, giving us 9.98 million reviews:

```sql
CREATE TABLE amazon_reviews
ENGINE = MergeTree
ORDER BY tuple()
AS SELECT *
FROM file('benchmarks/amazon-columns-cache/data/amazon_reviews_{2010,2011}.snappy.parquet');
```

We want to count reviews containing the word `disappointed`. First, let's disable the optimization, along with the columns cache, query cache, and query condition cache:

```sql
SELECT count() AS matching_reviews
FROM amazon_reviews
WHERE review_body LIKE '%disappointed%'
SETTINGS apply_string_filters_during_scan = 0,
         use_columns_cache = 0,
         use_query_cache = 0,
         use_query_condition_cache = 0;
```

```text
┌─matching_reviews─┐
│           293115 │
└──────────────────┘
```

We ran this on ClickHouse 26.10 with the default 12 threads, after merging the table into one Wide part. After one warm-up with each setting, we alternated three measured runs with the optimization disabled and enabled. The timings and peak memory figures below come from `system.query_log`.

With `apply_string_filters_during_scan = 0`:

| Run | Query time | Peak memory |
|---|---|---|
| 1 | 1.204 s | 128.66 MiB |
| 2 | 1.303 s | 127.93 MiB |
| 3 | 1.251 s | 129.05 MiB |

Changing `apply_string_filters_during_scan` to `1` gives us:

| Run | Query time | Peak memory |
|---|---|---|
| 1 | 1.091 s | 2.54 MiB |
| 2 | 1.333 s | 2.54 MiB |
| 3 | 1.232 s | 2.54 MiB |

Every run returns the same 293,115 matches. Execution time is similar, but peak memory drops from around 129 MiB to 2.54 MiB, a reduction of about 98%.



---

## Get started today

Interested in seeing how ClickHouse works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-2892-get-started-today-sign-up&utm_blogctaid=2892)

---