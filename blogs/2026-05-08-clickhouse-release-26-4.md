---
title: "ClickHouse Release 26.4"
date: "2026-05-08T15:27:25.995Z"
category: "Engineering"
excerpt: "ClickHouse 26.4 is here! In this release, more features become SQL compatible, COUNT DISTINCT gets faster, EXPLAIN gets even prettier, and more"
---

# ClickHouse Release 26.4

Another month goes by, which means it’s time for another release!

<p>The ClickHouse 26.4 release contains 39 new features &#127799; 45 performance optimizations &#128007; 238 bug fixes &#128029;</p>

This release sees more features become SQL compatible, faster COUNT DISTINCT, even prettier EXPLAIN, and more!

## New contributors

A special welcome to all the new contributors in 26.4! The growth of ClickHouse's community is humbling, and we are always grateful for the contributions that have made ClickHouse so popular.

Below are the names of the new contributors:

*Alexander Kuleshov, Alsu, Anton Frost, Aruj Bansal, Asya, ClickGap AI Bot, Denys Melnyk, Diego Gomes Tome, Dustin Healy, Evgeny Kuzin, Farid Adam, Francisco Garcia Florez, Gagan Dhakrey, Gleb Popov, Groene AI, Ivan Mantova, Jaap Elst, Jack Knudson, James Cunningham, JingYanchao, K, Kc Balusu, Matheus Nerone, Michael Russell, MukundaKatta, Nikita Semenov, Pavel Kravtsov, Peng, RenzoMXD, Sergey Veletskiy, Takumi Hara, Timothy Kurniawan, Wenyu Chen, XiaoBinMu, Yuri Fedoseev, ashrithb, asyablue22, dwagner-decix, egor romanov, groeneai, liuguangliang, manerone, nerve-bot, simonhammes, sourcelliu, xiaobin*

Hint: if you’re curious how we generate this list… [here](https://gist.github.com/gingerwizard/5a9a87a39ba93b422d8640d811e269e9).

<iframe width="768" height="432" src="https://www.youtube.com/embed/9lSVy7k2EoI?si=wKu80nxcUDMo_BE6" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

You can also [view the slides from the presentation](https://presentations.clickhouse.com/2026-release-26.4/).

## SQL compatibility: VALUES as table expression, EXTRACT, SET TIME ZONE

The 26.4 release sees more features become [compatible with standard SQL syntax](https://presentations.clickhouse.com/2026-release-26.4/?full#16). We’ll look at just a few of them, but you can see the [presentation slide deck](https://presentations.clickhouse.com/2026-release-26.4/?full#16) for more.

### VALUES as a table expression

#### Contributed by Desel72

First up, `VALUES`. Before this release, you could call it like this:

<pre><code type='click-ui' language='sql'>
SELECT * 
FROM VALUES((1, 'a'), (2, 'b'), (3, 'c'));
</code></pre>

```shell
   ┌─c1─┬─c2─┐
1. │  1 │ a  │
2. │  2 │ b  │
3. │  3 │ c  │
   └────┴────┘
```

Whereas now, we can also call it as a table expression, as shown below:

<pre><code type='click-ui' language='sql'>
SELECT * 
FROM (VALUES (1, 'a'), (2, 'b'), (3, 'c'));
</code></pre>

```shell
   ┌─c1─┬─c2─┐
1. │  1 │ a  │
2. │  2 │ b  │
3. │  3 │ c  │
   └────┴────┘
```

We can now also alias columns, which is useful when using `VALUES` in a join query. For example, instead of the following:

<pre><code type='click-ui' language='sql'>
SELECT
    c.c2,
    o.c2
FROM VALUES((1, 'Alice'), (2, 'Bob')) AS c
INNER JOIN VALUES((1, 250), (2, 100), (1, 75)) AS o 
ON c.c1 = o.c1;
</code></pre>

```shell
   ┌─c2────┬─o.c2─┐
1. │ Alice │  250 │
2. │ Alice │   75 │
3. │ Bob   │  100 │
   └───────┴──────┘
```

We can name the columns, which makes the query easier to understand:

<pre><code type='click-ui' language='sql'>
SELECT c.name, o.amount
  FROM (VALUES (1, 'Alice'), (2, 'Bob')) AS c(id, name)
  JOIN (VALUES (1, 250), (2, 100), (1, 75)) AS o(customer_id, amount)
  ON c.id = o.customer_id;
</code></pre>

```shell
   ┌─name──┬─amount─┐
1. │ Alice │    250 │
2. │ Alice │     75 │
3. │ Bob   │    100 │
   └───────┴────────┘
```

### EXTRACT

#### Contributed by Alexey Milovidov

The `EXTRACT` operator (used when working with dates) now supports PostgreSQL-style units, as shown in the following query:

<pre><code type='click-ui' language='sql'>
SELECT
  EXTRACT(EPOCH      FROM now())   AS epoch,
  EXTRACT(DOW        FROM today()) AS dayOfWeek,
  EXTRACT(DOY        FROM today()) AS dayOfYear,
  EXTRACT(ISODOW     FROM today()) AS isoDOW,
  EXTRACT(ISOYEAR    FROM today()) AS isoYear,
  EXTRACT(WEEK       FROM today()) AS isoWeek,
  EXTRACT(CENTURY    FROM today()) AS century,
  EXTRACT(DECADE     FROM today()) AS decade,
  EXTRACT(MILLENNIUM FROM today()) AS millennium;
</code></pre>

```shell
Row 1:
──────
epoch:      1777992683
dayOfWeek:  2
dayOfYear:  125
isoDOW:     2
isoYear:    2026
isoWeek:    19
century:    21
decade:     202
millennium: 3
```

### SET TIME ZONE

#### Contributed by phulv94

There is also a new SQL standard alias for setting the time zone. First, let’s check my current time zone:

<pre><code type='click-ui' language='sql'>
SELECT timezone(), formatDateTime(now(), '%Y-%m-%d %H:%M:%S %z');
</code></pre>

```shell
   ┌─timezone()────┬─formatDateTim⋯H:%M:%S %z')─┐
1. │ Europe/London │ 2026-05-05 15:May:47 +0100 │
   └───────────────┴────────────────────────────┘
```

And now, we’ll set it to be Amsterdam instead:

<pre><code type='click-ui' language='sql'>
SET TIME ZONE 'Europe/Amsterdam';
</code></pre>

And if we re-run the above query:

```shell
   ┌─timezone()───────┬─formatDateTim⋯H:%M:%S %z')─┐
1. │ Europe/Amsterdam │ 2026-05-05 16:May:59 +0200 │
   └──────────────────┴────────────────────────────┘
```

### Other compatibility improvements

And that’s not all - there is also now support for [NATURAL JOIN](https://presentations.clickhouse.com/2026-release-26.4/?full#17), [OVERLAY](https://presentations.clickhouse.com/2026-release-26.4/?full#18) is drop-in compatible, [compound INTERVAL literals](https://presentations.clickhouse.com/2026-release-26.4/?full#22) are supported, and more!

## LIKE uses text index

### Contributed by Elmi Ahmadov

From ClickHouse 25.4, when a `LIKE`/`ILIKE` query pattern is `%<alpha-numeric-characters-without-spaces>%` and the text index tokenizer is `splitByNonAlpha`, ClickHouse uses the [inverted index](https://clickhouse.com/blog/clickhouse-full-text-search-object-storage) to speed up those queries. It does this by scanning the inverted index dictionary rather than performing a full-table scan to find the matching pattern.

Let’s have a look at how this works with our trusty HackerNews dataset, first using [clickhousectl](https://clickhouse.com/blog/getting-started-clickhousectl) to get ClickHouse 26.4 running on my laptop:

<pre><code type='click-ui' language='bash'>
chctl local install 26.4
</code></pre>

And then we’ll start it up:

<pre><code type='click-ui' language='bash'>
chctl local server start --version 26.4
</code></pre>

And connect using the ClickHouse client:

<pre><code type='click-ui' language='bash'>
chctl local client --name default -mn
</code></pre>

Next, we’ll create our HackerNews table:

<pre><code type='click-ui' language='sql'>
CREATE TABLE hackernews
(
    `id` Int64,
    `deleted` Int64,
    `type` String,
    `by` String,
    `time` DateTime64(9),
    `text` String,
    `dead` Int64,
    `parent` Int64,
    `poll` Int64,
    `kids` Array(Int64),
    `url` String,
    `score` Int64,
    `title` String,
    `parts` Array(Int64),
    `descendants` Int64
    GRANULARITY 128
)
ORDER BY time;
</code></pre>

We’ll then insert the data:

<pre><code type='click-ui' language='sql'>
INSERT INTO hackernews 
SELECT *
FROM url('https://datasets-documentation.s3.eu-west-3.amazonaws.com/hackernews/hacknernews.csv.gz', 'CSVWithNames')
</code></pre>

And next, we’ll add a text index on the `text` column using the `splitByNonAlpha` tokenizer:

<pre><code type='click-ui' language='sql'>
ALTER TABLE hackernews
ADD INDEX text_tokens_idx text 
TYPE text(tokenizer='splitByNonAlpha') 
GRANULARITY 1;
</code></pre>

And materialize that index:

<pre><code type='click-ui' language='sql'>
ALTER TABLE hackernews
(MATERIALIZE INDEX text_tokens_idx)
SETTINGS mutations_sync = 1;
</code></pre>

This optimization is already enabled in 26.4, but can be controlled using the `use_text_index_like_evaluation_by_dictionary_scan` setting. The following query counts how many Hacker News posts mentioned Kubernetes:

<pre><code type='click-ui' language='sql'>
SELECT count()
FROM hackernews
WHERE text LIKE '%Kubernetes%'
SETTINGS use_text_index_like_evaluation_by_dictionary_scan=0;
</code></pre>

```shell
   ┌─count()─┐
1. │   20070 │
   └─────────┘

1 row in set. Elapsed: 0.832 sec. Processed 18.25 million rows, 6.29 GB (21.93 million rows/s., 7.56 GB/s.)
Peak memory usage: 88.18 MiB.

1 row in set. Elapsed: 0.624 sec. Processed 18.25 million rows, 6.29 GB (29.23 million rows/s., 10.08 GB/s.)
Peak memory usage: 87.93 MiB.

1 row in set. Elapsed: 0.638 sec. Processed 18.25 million rows, 6.29 GB (28.60 million rows/s., 9.86 GB/s.)
Peak memory usage: 86.01 MiB.
```

And now using the optimization:

<pre><code type='click-ui' language='sql'>
SELECT count()
FROM hackernews
WHERE text LIKE '%Kubernetes%'
SETTINGS use_text_index_like_evaluation_by_dictionary_scan=1;
</code></pre>

```shell
   ┌─count()─┐
1. │   20070 │
   └─────────┘

1 row in set. Elapsed: 0.208 sec. Processed 18.25 million rows, 18.25 MB (87.53 million rows/s., 87.53 MB/s.)
Peak memory usage: 2.07 MiB.

1 row in set. Elapsed: 0.225 sec. Processed 18.25 million rows, 18.25 MB (80.98 million rows/s., 80.98 MB/s.)
Peak memory usage: 2.07 MiB.

1 row in set. Elapsed: 0.234 sec. Processed 18.25 million rows, 18.25 MB (77.83 million rows/s., 77.83 MB/s.)
Peak memory usage: 2.07 MiB.
```

The number of rows processed is the same, but the query using the optimization has a best runtime of 208 milliseconds, compared to 624 milliseconds, a little over 3 times faster.

If we compare the query plans, we can see that the one using the optimization scans more than 1,000 fewer granules.

No use of inverted index:

```shell
    ┌─explain─────────────────────────────────────────────────────────┐
 1. │ Output: count()                                                 │
 2. │                                                                 │
 3. │ Aggregating                                                     │
 4. │ └──Filter ((WHERE + Change column names to column identifiers)) │
 5. │    └──ReadFromMergeTree (default.hackernews)                    │
 6. │          Indexes:                                               │
 7. │            PrimaryKey                                           │
 8. │              Condition: true                                    │
 9. │              Parts: 6/6                                         │
10. │              Granules: 3533/3533                                │
11. │            Skip                                                 │
12. │              Name: text_tokens_idx                              │
13. │              Description: text GRANULARITY 100000000            │
14. │              Condition: (mode: All; tokens: [])                 │
15. │              Parts: 6/6                                         │
16. │              Granules: 3533/3533                                │
17. │            Ranges: 6                                            │
    └─────────────────────────────────────────────────────────────────┘
```

Uses inverted index:

```shell
    ┌─explain──────────────────────────────────────────────┐
 1. │ Output: count()                                      │
 2. │                                                      │
 3. │ Aggregating                                          │
 4. │ └──Filter                                            │
 5. │    └──ReadFromMergeTree (default.hackernews)         │
 6. │          Indexes:                                    │
 7. │            PrimaryKey                                │
 8. │              Condition: true                         │
 9. │              Parts: 6/6                              │
10. │              Granules: 3533/3533                     │
11. │            Skip                                      │
12. │              Name: text_tokens_idx                   │
13. │              Description: text GRANULARITY 100000000 │
14. │              Condition: (mode: All; tokens: [])      │
15. │              Parts: 6/6                              │
16. │              Granules: 2247/3533                     │
17. │            Ranges: 190                               │
    └──────────────────────────────────────────────────────┘
```

## Faster COUNT DISTINCT

### Contributed by Jiebin Sun

There are a couple of improvements to `uniqExact` (used by `COUNT(DISTINCT ...)`) on high-core-count machines:

- ClickHouse no longer spawns redundant threads during the merge phase. uniqExact uses a two-level hash table with 256 buckets, but previously, ClickHouse would spawn up to `max_threads` threads regardless, and many of them would have nothing to do and exit immediately.
- When merging N intermediate hash tables (one per aggregation thread), the thread pool was initialized N times, causing `O(N × threads)` total thread spawns and severe lock contention. Now, all N hash tables are merged in a single pass - each thread processes one bucket across all hash tables at once, reducing thread pool initializations from `O(N)` to `O(1)`.

In some of our benchmarks, we saw speedups of 3 to 15 times on a 288-core machine.

This, however, is very much an optimization for machines with many cores - I tried it out on the HackerNews dataset on my Mac M2 Max (which has 12 cores) and didn’t see any improvement!

## Even prettier EXPLAIN

### Contributed by Kirill Kopnev

`EXPLAIN PLAN pretty=1` now prints expressions in a human-readable form, shows top-level output columns and per-step output columns, and labels JOINs with estimated row counts and locality.

Let’s see how this works with the following query:

<pre><code type='click-ui' language='sql'>
EXPLAIN pretty = 1
SELECT by, count()
FROM hackernews
WHERE (text LIKE '%OpenAI%') AND (text LIKE '%Google%')
GROUP BY ALL
ORDER BY count() DESC, by
LIMIT 10;
</code></pre>

26.3

<pre style="overflow-x:auto;white-space:pre"><code class="hljs language-shell mb-9 border border-solid border-neutral-750" style="word-break:normal;white-space:pre">
   ┌─explain────────────────────────────────────────────────────────────────────────────┐
1. │ Expression (Project names)                                                         │
2. │ └──Limit (preliminary LIMIT)                                                       │
3. │    └──Sorting (Sorting for ORDER BY)                                               │
4. │       └──Expression ((Before ORDER BY + Projection))                               │
5. │          └──Aggregating                                                            │
6. │             └──Expression (Before GROUP BY)                                        │
7. │                └──Expression ((WHERE + Change column names to column identifiers)) │
8. │                   └──ReadFromMergeTree (default.hackernews)                        │
   └────────────────────────────────────────────────────────────────────────────────────┘
</code></pre>

26.4

```shell
    ┌─explain─────────────────────────────────────────────────────┐
 1. │ Output: by, count()                                         │
 2. │                                                             │
 3. │ Expression (Project names)                                  │
 4. │ └──Limit (preliminary LIMIT)                                │
 5. │    └──Sorting (Sorting for ORDER BY)                        │
 6. │       └──Expression ((Before ORDER BY + Projection))        │
 7. │          └──Aggregating                                     │
 8. │             └──Expression (Before GROUP BY)                 │
 9. │                └──Expression                                │
10. │                   └──ReadFromMergeTree (default.hackernews) │
    └─────────────────────────────────────────────────────────────┘
```

## JSONAllValues + text index

### Contributed by Anton Popov

ClickHouse 26.4 adds the `JSONAllValues`, which returns every leaf value of a JSON column as `Array(String)`. We can create a text index on top of this, enabling more efficient filtering on JSON subcolumns.

Let’s have a look at how this works with help from the [StatsBomb dataset](https://github.com/statsbomb/open-data/tree/master). Let’s get a subset of the data on our machine by running the following:

<pre><code type='click-ui' language='bash'>
git clone --filter=blob:none --sparse https://github.com/statsbomb/open-data.git
cd open-data
git sparse-checkout set data/events
</code></pre>

We’ll create the following table using clickhouse-local:

<pre><code type='click-ui' language='sql'>
 CREATE TABLE events (
      match_id UInt32,
      json JSON(id String, index UInt32),
      INDEX vals JSONAllValues(json) TYPE text(tokenizer = 'ngrams') GRANULARITY 1
  )
  ENGINE = MergeTree
  ORDER BY (match_id, json.index);
</code></pre>

And then insert the data:

<pre><code type='click-ui' language='sql'>
INSERT INTO events
SELECT
  toUInt32(replaceRegexpOne(_file, '\\.json$', '')) AS match_id,
  json
FROM file('open-data/data/events/*.json', JSONAsObject);
</code></pre>

```shell
12188949 rows in set. Elapsed: 1275.404 sec. Processed 12.19 million rows, 10.48 GB (9.56 thousand rows/s., 8.22 MB/s.)
Peak memory usage: 1.87 GiB.
```

Just for our understanding of how the index works, let’s have a look at what the `JSONAllValues` function returns:

<pre><code type='click-ui' language='sql'>
SELECT JSONAllValues(json) FROM events LIMIT 1
FORMAT Vertical;
</code></pre>

```shell
JSONAllValues(json): ['[36.4,21.7]','1.013174','000000b5-8156-429d-9088-e62a6ac2ea0d','2529','[36.8,20]','60','2','4','From Throw In','10958','Chris Smalling','5','Left Center Back','123','39','Manchester United','[\'5fbbde9b-74ab-48e9-9873-ef956db384de\',\'fd43cc18-c37b-438a-8a40-a8bb50e59469\']','18','39','Manchester United','00:15:18.727','43','Carry']
```

The dataset has just over 12 million records, which isn’t really enough to see the impact of the index, so we’ll duplicate the data a bunch of times:

<pre><code type='click-ui' language='sql'>
ALTER TABLE events
ATTACH PARTITION ID 'all'
FROM events;
</code></pre>

```shell
0 rows in set. Elapsed: 3.892 sec.
0 rows in set. Elapsed: 7.957 sec.
0 rows in set. Elapsed: 15.894 sec.
0 rows in set. Elapsed: 33.655 sec.
0 rows in set. Elapsed: 68.870 sec.
```

And now we’ve got a lot more records:

<pre><code type='click-ui' language='sql'>
SELECT count()
FROM events;
</code></pre>

```shell
   ┌───count()─┐
1. │ 390046368 │ -- 390.05 million
   └───────────┘
```

The following query returns the number of rows related to Lionel Messi:

<pre><code type='click-ui' language='sql'>
SELECT count()
FROM events
WHERE json.player.name = 'Lionel Andrés Messi Cuccittini'
SETTINGS use_skip_indexes = 1;
</code></pre>

We can disable the text index by setting `use_skip_indexes = 0`. Running this query gives us the following result:

```shell
   ┌─count()─┐
1. │ 4268960 │ -- 4.27 million
   └─────────┘
```

We’ll run it three times without the index:

```shell
1 row in set. Elapsed: 1.505 sec. Processed 390.05 million rows, 13.87 GB (259.20 million rows/s., 9.22 GB/s.)
Peak memory usage: 48.23 MiB.

1 row in set. Elapsed: 1.666 sec. Processed 390.05 million rows, 13.87 GB (234.12 million rows/s., 8.32 GB/s.)
Peak memory usage: 48.23 MiB.

1 row in set. Elapsed: 1.668 sec. Processed 390.05 million rows, 13.87 GB (233.88 million rows/s., 8.32 GB/s.)
Peak memory usage: 48.23 MiB.
```

And three times with the index:

```shell
1 row in set. Elapsed: 1.139 sec. Processed 80.64 million rows, 3.23 GB (70.80 million rows/s., 2.84 GB/s.)
Peak memory usage: 69.25 MiB.

1 row in set. Elapsed: 1.096 sec. Processed 80.64 million rows, 3.23 GB (73.61 million rows/s., 2.95 GB/s.)
Peak memory usage: 68.93 MiB.

1 row in set. Elapsed: 1.087 sec. Processed 80.64 million rows, 3.23 GB (74.21 million rows/s., 2.97 GB/s.)
Peak memory usage: 74.13 MiB.
```

From the processed rows, we can see that the index reduces the amount of data to scan by almost 5 times. The best time without the index is 1,505 milliseconds, compared to 1,087 milliseconds with the index, an improvement of around 50%.


---

## Get started today

Interested in seeing how ClickHouse works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-555-get-started-today-sign-up&utm_blogctaid=555)

---