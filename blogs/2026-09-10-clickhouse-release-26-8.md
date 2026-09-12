---
title: "ClickHouse release 26.8"
date: "2026-09-11T13:12:38.318Z"
author: "ClickHouse"
category: "Engineering"
excerpt: "ClickHouse 26.8 LTS introduces background queries, pipelined SQL, new text tokenizers, expanded data lake integrations, and faster Parquet, aggregation, and join queries."
---

# ClickHouse release 26.8

Another month goes by, which means it’s time for another release! 

<p>The ClickHouse 26.8 release contains 98 new features &#127815; 128 performance optimizations &#127776; 556 bug fixes &#128029; and is a long-term support release.</p>

This release brings background queries, pipelined SQL, new text tokenizers, expanded data lake integrations, and performance improvements for Parquet, GROUP BY, and joins.

## New contributors {#new-contributors}

A special welcome to all the new contributors in 26.8! The growth of ClickHouse's community is humbling, and we are always grateful for the contributions that have made ClickHouse so popular.

Below are the names of the new contributors:

*Aashish Kohli, AbdullahKaya, Alex Budkar, Alex Kalmakov, Alexey Elkin, Amog Iska, Amogh-Bharadwaj, Andrey Tsarevskiy, Andy Bradshaw, Avinash Kamath, Bartok, Bartok9, Chris Lu, Christian Bianchi, ClickGap, Daniel Q. Kim, David Dallakyan, Dean Chen, Dergousov Maksim, Diego Gomes Tomé, Dmitrii Tunikov, Eduardo Gómez, Emil Sadek, George MacRorie, Hamid, Hank Cui, Haowen Feng (from Dev Box), Ilia Demianenko, Ivan Shelestov, James Sanders, Jose Muñoz, KD2YCU, Kirill Shcherbatov, Kirill Shokhin, Konstantin Plis, Kseniia, Nikolai Ovchinnikov, Nishant, Nishant Agarwal, Nuno Adrego, Perfloop Agent, Rahul Malik, RamiDarwiche, Raymond Lee, Ria Khatoniar, Ria-K912, Rohith Pariki, RohithPariki, Schum, Sean Reid, Sergey Chernov, Shawn Chen, Stanislav, Steve Lerner, Tod Trevillian, UberDever, Utkal Singh, Valery Petrov, VighneshPath, Vladimir Chemeris, William Hatcher, Yecine Megdiche, Yiyang Shao, ZachEddy, Zeynel Koca, a.akhondi, addshore, amirreza1307, avinash, deusgaudio, francisconeves-clickhouse, gelsonbagetti, gudauu, kalyanamdewri, locadex-agent\[bot\], pavol kutaj, quantrail-admin, vahid, vahid sohrabloo, yisamlee, yiyang-shao, zainulabidin302, Éco*

Hint: if you’re curious how we generate this list… [here](https://gist.github.com/gingerwizard/5a9a87a39ba93b422d8640d811e269e9).

<iframe width="768" height="432" src="https://www.youtube.com/embed/5A9gRYE0v2M?si=4pD3DBREk8UJKUQW" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

You can also [view the slides from the presentation](https://presentations.clickhouse.com/2026-release-26.8).

## Run a query in the background {#run_a_query_in_the_background}

### Contributed by Miсhael Stetsyuk

It’s now possible to run a query in the background. The query will return immediately and then run until completion, regardless of what happens to your connection.

This feature is useful for long-running queries that ingest data into ClickHouse or export data from it, allowing them to continue even if the client disconnects.

We have a ClickHouse server running with the [UK property prices dataset](https://clickhouse.com/docs/get-started/sample-datasets/uk-price-paid) imported and then copied a few times using the following query:

<pre><code type='click-ui' language='sql'>
ALTER TABLE uk_price_paid
ATTACH PARTITION ID 'all'
FROM uk_price_paid;
</code></pre>

This gets us up to a little over 240 million rows:

<pre><code type='click-ui' language='sql'>
SELECT count() FROM uk_price_paid;
</code></pre>

```shell
┌───count()─┐
│ 243619704 │
└───────────┘
```

Next, we can run the following query to write the data in the `uk_price_paid` table to a file on a local HTTP server. 

<pre><code type='click-ui' language='sql'>
INSERT INTO FUNCTION url('http://localhost:8080/uploads/london-sales.parquet', 'Parquet')
SELECT * FROM uk_price_paid
SETTINGS run_query_in_background = 1;
</code></pre>

```shell
Query id: 59eabb9f-33f4-412b-b2f3-b090fe7b4bbf

Ok.

0 rows in set. Elapsed: 0.001 sec.
```

We can query `system.processes` to check on the progress of background queries: 

<pre><code type='click-ui' language='sql'>
SELECT query_id, query,
      round(elapsed, 2) AS elapsed_seconds,
      read_rows, written_rows
FROM system.processes
WHERE query NOT ILIKE '%system.processes%'
ORDER BY elapsed DESC;
</code></pre>

```shell
Row 1:
──────
query_id:        59eabb9f-33f4-412b-b2f3-b090fe7b4bbf
query:           INSERT INTO FUNCTION url('http://localhost:8080/uploads/uk.parquet', 'Parquet')
SELECT * FROM uk_price_paid
SETTINGS run_query_in_background = 1;
elapsed_seconds: 8.52
read_rows:       179243204 -- 179.24 million
written_rows:    179243204 -- 179.24 million
```

Once the query’s finished, we can query `system.query_log` to see how long it took:

<pre><code type='click-ui' language='sql'>
SELECT event_time, type, query_duration_ms,
      read_rows, result_rows
FROM system.query_log
WHERE query_id = '59eabb9f-33f4-412b-b2f3-b090fe7b4bbf'
ORDER BY event_time;
</code></pre>

```shell
┌──────────event_time─┬─type────────┬─query_duration_ms─┬─read_rows─┬─result_rows─┐
│ 2026-09-03 12:32:05 │ QueryStart  │                 0 │         0 │           0 │
│ 2026-09-03 12:32:17 │ QueryFinish │             11798 │ 243619704 │   243619704 │
└─────────────────────┴─────────────┴───────────────────┴───────────┴─────────────┘
```

## PostgreSQL-style regular-expression operators {#postgresql-style_regular-expression_operators}

### Contributed by Alexey Milovidov

ClickHouse now supports the following PostgreSQL-style regex operators:

*  `~` returns 1 when the string matches the regular expression, using case-sensitive matching.  
*  `~*` returns 1 when the string matches the regular expression, using case-insensitive matching.  
*  `!~` returns 1 when the string does not match the regular expression, using case-sensitive matching.  
* `!~*` returns 1 when the string does not match the regular expression, using case-insensitive matching.

The following query shows how to use all the operators to match parts of the term `Baker Street`:

<pre><code type='click-ui' language='sql'>
SELECT
      'Baker Street' ~ 'street$' AS matchesCaseSensitively,
      'Baker Street' ~* 'street$' AS matchesCaseInsensitively,
      'Baker Street' !~ 'street$' AS doesNotMatchCaseSensitively,
      'Baker Street' !~* 'street$' AS doesNotMatchCaseInsensitively
FORMAT Vertical;
</code></pre>

```shell
Row 1:
──────
matchesCaseSensitively:        0
matchesCaseInsensitively:      1
doesNotMatchCaseSensitively:   1
doesNotMatchCaseInsensitively: 0
```

> **A small disclaimer:** These operators come with a disclaimer from Alexey, who implemented them: he isn’t a fan and thinks they make SQL look a little too much like Bash or Perl. PostgreSQL compatibility won this round.
> The same change means that `psql` commands such as `\d`, `\dt`, and `\dv` now work when connected to ClickHouse over the PostgreSQL wire protocol. However, `\d <table>` still uses some PostgreSQL syntax that ClickHouse doesn’t yet support.

## Array as an array subscript {#array_as_an_array_subscript}

### Contributed by folly

The subscript operator now accepts an array of indices and returns the elements at all given positions. This makes it possible to gather, reorder, or sample array elements in a single expression, which is convenient when used with arraySort and topK-style functions.

Let’s have a look at a simple example:

<pre><code type='click-ui' language='sql'>
WITH arrayMap(x -&gt; rand(x), range(1, 10)) AS random_values
SELECT random_values[[1, 3, 5]];
</code></pre>

```shell
┌─arrayElement(ran⋯ues, [1, 3, 5])─┐
│ [344408953,1157293782,407846805] │
└──────────────────────────────────┘
```

A more realistic use is selecting quarterly checkpoints from a monthly time series. The following query builds an ordered array of each district’s monthly median prices, then selects January, April, July, and October in one expression:

<pre><code type='click-ui' language='sql'>
WITH monthlyPrices AS
(
    SELECT district, toStartOfMonth(date) AS month,
           round(median(price)) AS medianPrice
    FROM uk_price_paid
    WHERE town = 'LONDON'
      AND district IN ('CAMDEN', 'CITY OF WESTMINSTER', 'KENSINGTON AND CHELSEA')
      AND date &gt;= '2024-01-01' AND date &lt; '2025-01-01'
    GROUP BY district, month
)
SELECT district,
       arraySort(groupArray((month, medianPrice)))[[1, 4, 7, 10]] AS quarterlyPrices
FROM monthlyPrices
GROUP BY district
HAVING count() = 12
ORDER BY district;
</code></pre>

```shell
Row 1:
──────
district:        CAMDEN
quarterlyPrices: [('2024-01-01',760000),('2024-04-01',731000),('2024-07-01',762500),('2024-10-01',805000)]

Row 2:
──────
district:        CITY OF WESTMINSTER
quarterlyPrices: [('2024-01-01',1215000),('2024-04-01',1037500),('2024-07-01',935000),('2024-10-01',875000)]

Row 3:
──────
district:        KENSINGTON AND CHELSEA
quarterlyPrices: [('2024-01-01',1205000),('2024-04-01',1187500),('2024-07-01',1100000),('2024-10-01',1200000)]
```

## Query to JSON to query {#query_to_json_to_query}

### Contributed by Alexey Milovidov, Nikita Fomichev

It’s now possible to convert a query to its Abstract Syntax Tree in JSON and to query ClickHouse using an Abstract Syntax Tree in JSON.

The `parseQueryToJSON` function returns an Abstract Syntax Tree in JSON format. We’ll use a simple `count()` to demonstrate this function, as the output is extremely verbose:

<pre><code type='click-ui' language='sql'>
SELECT parseQueryToJSON($sql$
SELECT count() FROM uk_price_paid
$sql$)::JSON
FORMAT Vertical;
</code></pre>

```json
{
  "type": "SelectWithUnionQuery",
  "union_mode": "UNION_DEFAULT",
  "list_of_selects": {
    "type": "ExpressionList",
    "children": [
      {
        "type": "SelectQuery",
        "select": {
          "type": "ExpressionList",
          "children": [
            {"type": "Function", "name": "count",
             "arguments": {"type": "ExpressionList"}}
          ]
        },
        "tables": {
          "type": "TablesInSelectQuery",
          "children": [
            {"type": "TablesInSelectQueryElement",
             "table_expression": {
               "type": "TableExpression",
               "database_and_table_name": {
                 "type": "TableIdentifier", "name": "uk_price_paid"}}}
          ]
        }
      }
    ]
  }
}
```

The JSON describes the query as a tree of typed nodes:  identifiers, literals, functions, and clauses. 

Because it's ordinary JSON, any language with a JSON library can analyze, validate, rewrite, or generate queries without embedding a SQL parser. 

The conversion runs both ways: `formatQueryFromJSON` turns the tree back into SQL, so you can always read back what you built:

<pre><code type='click-ui' language='sql'>
SELECT formatQueryFromJSON(parseQueryToJSON($sql$
SELECT count() FROM uk_price_paid
$sql$));
</code></pre>

```shell
┌─formatQueryFromJ⋯_price_paid\n'))─┐
│ SELECT count() FROM uk_price_paid │
└───────────────────────────────────┘
```

ClickHouse 26.8 also adds an experimental dialect, `clickhouse_json`, that lets you send a JSON AST instead of SQL. It's gated behind the `enable_json_ast_dialect` setting, then selected like any other dialect:

<pre><code type='click-ui' language='sql'>
SET enable_json_ast_dialect = 1, dialect = 'clickhouse_json';
</code></pre>

If we paste the AST for `SELECT count() FROM uk_price_paid` that we created earlier, we get:

```shell
┌───count()─┐
│ 243619704 │
└───────────┘
```

We're not expecting you to start writing your queries as JSON syntax trees! This feature is more for machines than people. 

Anything that generates queries can generate a JSON syntax tree instead of SQL, which means there’s no need for string concatenation, no more horrible escaping bugs, and maybe most importantly, no SQL injection surface.

## CREATE USER ... VALID FOR {#create_user__valid_for}

### Contributed by Alexey Milovidov

Before ClickHouse 26.8, it was already possible to create time-limited users using the `VALID UNTIL` syntax:

<pre><code type='click-ui' language='sql'>
CREATE USER mark
IDENTIFIED WITH no_password
VALID UNTIL '2026-10-04';
</code></pre>

ClickHouse 26.8 adds `VALID FOR INTERVAL` syntax, which computes the deadline starting from the current time. So, to have a user valid for two weeks from now, we’d run the following query:

<pre><code type='click-ui' language='sql'>
CREATE USER mark
IDENTIFIED WITH no_password
VALID FOR INTERVAL 2 WEEKS;
</code></pre>

We can then check when this user is valid until:

<pre><code type='click-ui' language='sql'>
SHOW CREATE USER mark
FORMAT LineAsString;
</code></pre>

The output of this query will all be on one line, so we’ve manually formatted it for ease of reading:

```shell
CREATE USER mark 
IDENTIFIED WITH no_password 
VALID UNTIL '2026-09-18 10:06:29'
```

We can also use this syntax when altering the user. To have the user instead be valid for one week from now, we’d run the following query:

<pre><code type='click-ui' language='sql'>
ALTER USER mark VALID FOR INTERVAL 1 WEEK;
</code></pre>

```shell
CREATE USER mark 
IDENTIFIED WITH no_password 
VALID UNTIL '2026-09-11 10:08:34'
```

## Pipelined SQL {#pipelined_sql}

### Contributed by Alexey Milovidov

ClickHouse 26.8 introduces pipelined SQL, which lets you write queries top-down, with each step following the previous.

You can learn more in the [Pipelined SQL in ClickHouse 26.8](https://clickhouse.com/blog/pipelined-sql-26.8) blog post.

## ClickHouse as a streaming HTTP API {#clickhouse_as_a_streaming_http_api}

### Contributed by Alexey Milovidov

ClickHouse 26.8 also introduces several features that make it reasonably easy to add a lightweight HTTP API around your tables and common queries.  

You can learn more in the [ClickHouse as a streaming HTTP API](https://clickhouse.com/blog/clickhouse-streaming-http-api) blog post.

## system.user_query_log {#systemuser_query_log}

### Contributed by Yue Ni, Alexey Milovidov

ClickHouse 26.8 also introduces a new system table, `system.user_query_log`, which only includes the queries for the current user.

This means that every user can see their own query history without needing access to the `system.query_log` table.

Queries to `system.query_log` will still return a permission denied exception if your user doesn’t have access to that table.

## Atomic POPULATE {#atomic_populate}

### Contributed by Alexey Milovidov

An [incremental materialized view](https://clickhouse.com/docs/concepts/features/materialized-views/incremental-materialized-view) is equivalent to a trigger that runs a query on blocks of data as they’re inserted into a table. 

When creating an incremental materialized view and populating it on creation, a race condition caused it to skip records inserted during the population. In ClickHouse 26.8, this has been fixed.

When you call `CREATE MATERIALIZED VIEW ... POPULATE`, the view is subscribed to new inserts on the source table, and a snapshot of the existing data is captured together, under a brief exclusive lock on the source table, so that every row inserted concurrently with the population is delivered exactly once.

This functionality is enabled by default, but we can disable it by setting `materialized_views_populate_atomically` to `0`, which lets us demonstrate the previous behavior.

First, let’s create a source table containing 100,000 rows:

<pre><code type='click-ui' language='sql'>
CREATE TABLE src (id UInt64) 
ORDER BY id;
INSERT INTO src 
SELECT number FROM numbers(100000);
</code></pre>

And a destination one:

<pre><code type='click-ui' language='sql'>
CREATE TABLE dst (id UInt64) 
ORDER BY id;
</code></pre>

Next, we’ll have one query inserting 50 rows and another query creating a materialized view that populates the `dst` table.

For a row to fall through the gap, its `INSERT` has to still be in flight when `POPULATE` takes its snapshot of the source table. Most inserts finish too quickly for that, so we use `sleepEachRow` to spread 50 rows over about two and a half seconds, and start the `CREATE` while that insert is still running.

We're also using `POPULATE` together with `TO`, which was a syntax error before 26.8. The view backfills the existing `dst` table from the data already in `src`.

<pre><code type='click-ui' language='bash'>
./clickhouse client -q "
  INSERT INTO src SELECT number + 100000 FROM numbers(50)
  WHERE sleepEachRow(0.05) = 0;" &amp;

sleep 0.5

./clickhouse client -m -q "
  SET materialized_views_populate_atomically = 0;
  CREATE MATERIALIZED VIEW mv TO dst
  POPULATE AS SELECT id FROM src;"

wait
</code></pre>

Once this has finished running, we can compare the source table against the destination one:

<pre><code type='click-ui' language='sql'>
SELECT (SELECT count() FROM src) AS sourceRows,
       (SELECT count() FROM dst) AS dstRows,
       (SELECT uniqExact(id) FROM dst) AS dstDistinct,
       sourceRows - dstRows AS lost,
       dstRows - dstDistinct AS duplicated
FORMAT PrettyCompact;
</code></pre>

```shell
┌─sourceRows─┬─dstRows─┬─dstDistinct─┬─lost─┬─duplicated─┐
│     100050 │  100000 │      100000 │   50 │          0 │
└────────────┴─────────┴─────────────┴──────┴────────────┘
```

All 50 records are in the source table, but none are in the destination table. The insert started before `mv` existed, so it didn’t push to it, and it committed after the population snapshot was taken, so the backfill didn't see it either.

It's exactly 50 because an insert decides which views will receive its data once, when the query starts, rather than per row or per block. So the whole insert either arrives or it doesn't.

If we drop `mv`, `src`, and `dst`, and then recreate `src` and `dst`, we can create the materialized view, but this time with `materialized_views_populate_atomically` set to `1`:

<pre><code type='click-ui' language='bash'>
./clickhouse client -q "
  INSERT INTO src SELECT number + 100000 FROM numbers(50)
  WHERE sleepEachRow(0.05) = 0;" &amp;

sleep 0.5

./clickhouse client -m -q "
  SET materialized_views_populate_atomically = 1;
  CREATE MATERIALIZED VIEW mv TO dst
  POPULATE AS SELECT id FROM src;"

wait
</code></pre>

And this time, we’ll get the following output when we count the records in each table:

```shell
┌─sourceRows─┬─dstRows─┬─dstDistinct─┬─lost─┬─duplicated─┐
│     100050 │  100050 │      100050 │    0 │          0 │
└────────────┴─────────┴─────────────┴──────┴────────────┘
```

## Japanese and Chinese tokenizer support {#japanese_and_chinese_tokenizer_support}

### Contributed by Robert Schulze, Amos Bird, Jimmy Aguilar Mena

The default tokenizer in ClickHouse (used by the `tokens`, `hasAllTokens`, and `hasAnyTokens` functions) is `splitByNonAlpha` which splits a string by whitespace and punctuation characters into an array of substrings. Unlike English and other Indo-European languages, Chinese and Japanese text have no spaces between words, so unique tokenizers are required.

26.8 addresses this with two purpose-built tokenizers:

* **japanese** - The Japanese tokenizer relies on the MeCab morphological analyzer and requires an external MeCab dictionary specified in the server configuration  
* **chinese** - a jieba-style tokenizer combining a dictionary with an HMM (hidden Markov model) for segmenting unknown sequences, e.g. splitting ClickHouse是一个快速的开源数据库 into ClickHouse, 是, 一个, 快速, 的, 开源, 数据库 rather than one blob or single characters.

#### Japanese

To use the Japanese tokenizer, you’ll first need to configure a dictionary. In this example, we’ll use [UniDic](https://clrd.ninjal.ac.jp/unidic/). Once you’ve downloaded the .zip archive from the website, you’ll need to get the SHA256 of the archive, which ClickHouse uses to verify the dictionary before loading it:

<pre><code type='click-ui' language='bash'>
sha256sum /var/lib/clickhouse/unidic-cwj-202512.zip
</code></pre>

```shell
d94216b589d15d05c408ed59abc5259086703ebbac14e225b5314e4cd106c4db
```

Add a new tokenizer in `/etc/clickhouse-server/config.d/tokenizers.xml` to define a custom configuration that gets merged into your primary `config.xml` file when the server starts.

```xml
<clickhouse>
  <tokenizer>
    <japanese>
      <dictionary_location>file:///var/lib/clickhouse/unidic-cwj-202512.zip</dictionary_location>
      <dictionary_sha>d94216b589d15d05c408ed59abc5259086703ebbac14e225b5314e4cd106c4db</dictionary_sha>
    </japanese>
  </tokenizer>
</clickhouse>
```

 > **Note**
>
> You can also specify a dictionary via HTTP/HTTPS URL or in S3-compatible storage

If your server is already running, make sure to restart it so the configuration takes effect. You can now create a text index and query it like this:

<pre><code type='click-ui' language='sql'>
CREATE TABLE reviews
(
    id UInt64,
    text String,
    INDEX text_idx text TYPE text(tokenizer = 'japanese')
)
ENGINE = MergeTree
ORDER BY id;

INSERT INTO reviews VALUES
(1, '渋谷の新しい寿司屋で美味しいうにを食べた'),      -- "ate" (食べた)
(2, '大阪のラーメンは最高だった、また食べたい'),      -- "want to eat" (食べたい)
(3, '京都で抹茶アイスを食べながら散歩した'),          -- "while eating" (食べながら)
(4, '新幹線に乗って富士山を見に行った');              -- no mention of eating

SELECT id, text
FROM reviews
WHERE hasAnyTokens(text, ['食べ'], 'japanese')
ORDER BY id;
</code></pre>

| id | text |
| :--- | :--- |
| 1 | 渋谷の新しい寿司屋で美味しいうにを食べた |
| 2 | 大阪のラーメンは最高だった、また食べたい |
| 3 | 京都で抹茶アイスを食べながら散歩した |

3 rows in set. Elapsed: 0.007 sec.

In the example above, `食べた`, `食べたい`, and `食べながら` are all different forms of the verb `食べる` ("to eat"), but the tokenizer segments each of them down to the stem `食べ` plus a separate conjugation particle. So a single-token search for `食べ` correctly pulls rows 1–3, and skips row 4.

For more details, read [the Japanese tokenizer docs](https://clickhouse.com/docs/reference/engines/table-engines/mergetree-family/textindexes#japanese-tokenizer-dictionary)

#### Chinese

Unlike the Japanese tokenizer, which requires downloading an external dictionary archive and configuring it in your server XML configuration, the Chinese tokenizer requires no server configuration setup. Its embedded dictionary and hidden Markov model data (derived from cppjieba) are built directly into ClickHouse.

The `chinese` tokenizer allows you to specify a granularity parameter. By default, it is set to `coarse_grained` but if you pass `fine_grained` you can index overlapping sub-words to improve search recall at the cost of a larger index.

The query below creates two tables. The first has an index using the `chinese` tokenizer with the default `coarse_grained` granularity parameter, and the second has an index using the `fine_grained` parameter.

Four strings are inserted into both tables, either containing the word `大学` ("university") standalone (row 1), embedded inside a longer compound word (rows 2 and 3), or not at all (row 4).

<pre><code type='click-ui' language='sql'>
CREATE TABLE table_coarse
(
    key UInt64,
    str String,
    INDEX text_idx str TYPE text(tokenizer = chinese) -- default: coarse_grained
)
ENGINE = MergeTree ORDER BY key;

CREATE TABLE table_fine
(
    key UInt64,
    str String,
    INDEX text_idx str TYPE text(tokenizer = chinese('fine_grained'))
)
ENGINE = MergeTree ORDER BY key;

INSERT INTO table_coarse VALUES
    (1, '他考上了大学，很开心'), -- standalone 大学
    (2, '北京邮电大学的通信工程专业很强'), -- compound 北京邮电大学
    (3, '我毕业于北京大学计算机系'), -- compound 北京大学
    (4, '今天天气不错，适合散步'); -- no mention

INSERT INTO table_fine SELECT * FROM table_coarse;
</code></pre>

The queries below use the `hasAllTokens` function to search for `大学` ("university"), first on the table using the default `coarse_grained` parameter in its `chinese` index, then for the second table using the `fine_grained` parameter.

For the first table, only `他考上了大学，很开心` ("He got into university and was very happy."), the sentence with a standalone mention of `大学`, is returned. For the second table, both the sentence with the standalone mention of `大学` and the sentences with the compound mentions are returned:

<pre><code type='click-ui' language='sql'>
SELECT
    key,
    str
FROM table_coarse
WHERE hasAllTokens(str, '大学')
ORDER BY key ASC;
</code></pre>

Query ID: `7e348059-9cd1-4f72-8026-8d76266050e4`

| key | str |
| :--- | :--- |
| 1 | 他考上了大学，很开心 |

1 row in set. Elapsed: 0.002 sec.

<pre><code type='click-ui' language='sql'>
SELECT
    key,
    str
FROM table_fine
WHERE hasAllTokens(str, '大学')
ORDER BY key ASC;
</code></pre>

Query ID: `4da23c89-8a10-4099-9637-bd2a14f6aa1b`

| key | str |
| :--- | :--- |
| 1 | 他考上了大学，很开心 |
| 2 | 北京邮电大学的通信工程专业很强 |
| 3 | 我毕业于北京大学计算机系 |

3 rows in set. Elapsed: 0.002 sec.

This is because the `chinese` tokenizer treats `北京大学` ("Peking University") and `北京邮电大学` ("Beijing University of Posts and Telecommunications") as single dictionary tokens in coarse mode so searching for the sub-token 大学 alone never matches those rows under coarse tokenization, even though a human reading the sentence would know that both sentences are relevant matches for "university". `fine_grained` mode is specifically the setting that additionally breaks these compounds apart into their overlapping sub-words like `北京` ("Beijing"), `邮电` ("Post and Telecommunications") or `大学` ("University") which is why it's the one that picks up rows 2 and 3.

## New tokenizers: `icu` and `splitByRegexp` {#new_tokenizers_icu_and_splitbyregexp}

### Contributed by Jimmy Aguilar Mena

Whilst Jieba is designed for simplified and traditional Chinese, and MeCab is primarily intended for Japanese - [ICU](https://icu.unicode.org/) (International Components for Unicode), is a generalized, rule-based multilingual library that uses standard boundary analysis algorithms, we might reasonably ask about how to tokenize text for other languages that don't place whitespace between words - such as Thai, Lao, Khmer or Burmese?

Version 26.8 adds a new `icu(locale)` tokenizer to ClickHouse which splits strings into word tokens using the library's Unicode word segmentation. For scripts that do not put whitespace between words, ICU applies dictionary-based segmentation which ensures that text is split into meaningful multi-character words instead of single characters.

Before 26.8, if you had tried to tokenize text for Thai, Lao, Khmer or Burmese, using a non-ASCII tokenizer like `asciiCJK`, you would have run into a single-character fragmentation problem because `asciiCJK` treats every non-ASCII character as its own token. Take for example, the Thai word `บ้าน` ("house"):

<pre><code type='click-ui' language='sql'>
SELECT tokens('บ้าน', 'asciiCJK');
</code></pre>

```shell
┌─tokens('บ้าน', 'asciiCJK')─┐
│ ['บ','้','า','น']          │
└───────────────────────────┘
```

`บ` and `น` are consonants, `้` is a tone mark, `า` is a vowel sign, so the tokenization has fragmented the word into four meaningless pieces. `hasAllTokens` only checks that every needle fragment exists *somewhere* in the row, so two completely unrelated real Thai words can each contribute a piece and produce a false positive on a search for "house" against a completely unrelated sentence like "The horse is on the mountain":

<pre><code type='click-ui' language='sql'>
-- "ม้าอยู่บนภูเขา" = "The horse is on the mountain" (no usage of "house")
SELECT tokens('ม้าอยู่บนภูเขา', 'asciiCJK');
</code></pre>

```shell
┌─tokens('ม้าอยู่บนภูเขา', 'asciiCJK')──────────────────────┐
│ ['ม','้','า','อ','ย','ู','่','บ','น','ภ','ู','เ','ข','า'] │
└───────────────────────────────────────────────────────┘
```

<pre><code type='click-ui' language='sql'>
SELECT hasAllTokens('ม้าอยู่บนภูเขา', 'บ้าน', 'asciiCJK');
</code></pre>

```shell
┌─hasAllTokens⋯'asciiCJK')─┐
│                        1 │
└──────────────────────────┘
-- false positive
```

Compare this with what happens when the `icu` tokenizer is used with `locale` set to `th`:

<pre><code type='click-ui' language='sql'>
SELECT tokens('ม้าอยู่บนภูเขา', 'icu', 'th');
</code></pre>

```shell
┌─tokens('ม้าอยู่⋯icu', 'th')─┐
│ ['ม้า','อยู่','บน','ภูเขา']  │
└──────────────────────────┘
-- "horse", "is/located", "on", "mountain"
```

<pre><code type='click-ui' language='sql'>
SELECT hasAllTokens('ม้าอยู่บนภูเขา', 'บ้าน', 'icu(''th'')');
</code></pre>

```shell
┌─hasAllTokens⋯u(\'th\')')─┐
│                        0 │
└──────────────────────────┘
```

 > **Tip**
>
> You can query the `system.collations` table for a list of all the supported ICU locales:

For situations requiring more control, 26.8 introduces the `splitByRegexp` tokenizer which allows you to split text into tokens using a regular expression as the separator.

ClickHouse's default tokenizer `splitByNonAlpha` splits on every non-alphanumeric ASCII character, which means that text like `C++`, `C#`, and `F#` all collapse to the same bare letter:

<pre><code type='click-ui' language='sql'>
SELECT
    tokens('C++', 'splitByNonAlpha'),
    tokens('C#', 'splitByNonAlpha'),
    tokens('F#', 'splitByNonAlpha')
FORMAT Vertical;
</code></pre>

```shell
tokens('C++'⋯yNonAlpha'): ['C']
tokens('C#',⋯yNonAlpha'): ['C']
tokens('F#',⋯yNonAlpha'): ['F']
```

In practice this means that a search for "C#" can return a false-positive like "I am an expert in C++":

<pre><code type='click-ui' language='sql'>
SELECT hasAllTokens('I am an expert in C++', 'C#', 'splitByNonAlpha');
</code></pre>

```shell
┌─hasAllTokens⋯yNonAlpha')─┐
│                        1 │
└──────────────────────────┘
```

Additionally, `hasToken` rejects needles which contain separator characters, so there is no way to search for the literal term `C++` or `C#` at all with `splitByNonAlpha`.

With `splitByRegexp`, you can define the separator pattern explicitly so characters `#` and `+` are treated as part of the word:

<pre><code type='click-ui' language='sql'>
CREATE TABLE hold_my_beer
(
id UInt64,
description String,
INDEX idx description TYPE text(tokenizer = splitByRegexp('[^\p{L}\p{N}#+]+'))
)
ENGINE = MergeTree ORDER BY id;

INSERT INTO hold_my_beer VALUES
    (1, 'I am an expert in C++'),
    (2, 'I am an expert in C#'),
    (3, 'I use Arch');
    
SELECT id, description FROM hold_my_beer WHERE hasAllTokens(description, 'C++') OR hasAllTokens(description, 'C#');
</code></pre>

```shell
┌─id─┬─description───────────┐
│  1 │ I am an expert in C++ │
│  2 │ I am an expert in C#  │
└────┴───────────────────────┘
```

## `URL` database engine {#the_url_database_engine}

### Contributed by Alexey Milovidov

In last month's [26.7 release blog post](https://clickhouse.com/blog/clickhouse-release-26-07#unification-of-url) we wrote about how the `url` table function and `URL` table engines can now dispatch to the right backend based on the specified URL schema with support for file paths, S3, GCS, Azure, and HDFS in addition to HTTP.

26.8 introduces a new `URL` **database engine** which allows you to specify a URL prefix and query any path on the remote server as a table.

In last month's post our example showed you how you can directly query an s3 bucket with the `url` table engine:

<pre><code type='click-ui' language='sql'>
SELECT count(), avg(star_rating) FROM url('s3://datasets-documentation/amazon_reviews/amazon_reviews_2015.snappy.parquet');
</code></pre>

You can now specify `s3://datasets-documentation/amazon_reviews` as the prefix and query each of the files in the bucket as a separate table:

<pre><code type='click-ui' language='sql'>
CREATE DATABASE datasets
ENGINE = URL('https://datasets-documentation.s3.eu-west-3.amazonaws.com/amazon_reviews/');
USE datasets;

SELECT count() FROM 'amazon_reviews_2015.snappy.parquet';
</code></pre>

```shell
┌──count()─┐
│ 41905631 │ -- 41.91 million
└──────────┘
```

<pre><code type='click-ui' language='sql'>
SELECT count() 
FROM 'amazon_reviews_2014.snappy.parquet';
</code></pre>

```shell
┌──count()─┐
│ 44127569 │ -- 44.13 million
└──────────┘
```

In `clickhouse-local` the default database is now also an overlay on top of `URL`, allowing you to conveniently query local files, URLs, S3 data, or regular tables in the default database:

<pre><code type='click-ui' language='sql'>
SELECT * FROM 'hits.tsv';
SELECT * FROM 'https://example.com/hits.tsv';
SELECT * FROM 's3://mybucket/hits.tsv';
SELECT * FROM table;
</code></pre>

## `bigquery` table function and `BigQuery` table engine {#bigquery_table_function_and_bigquery_table_engine}

### Contributed by Alexey Milovidov

For those who have not yet migrated their workloads from BigQuery to ClickHouse, `26.8` makes it easier than ever to do so with the introduction of the `bigquery` table function and `BigQuery` table engine.

Let's see how it works using an existing Stack Overflow posts BigQuery project ([setup steps](https://pastila.nl/?003f30a0/ab5c593a768497695e7e0c9957cf118d#2FvhCYiX4UryqoULfQ/vfA==GCM)).

We'll use the `bigquery` table function to take a look at the data shape first. For this we'll need to pass a service key to the `bigquery` table function.

Create a named collection and replace `your_service_key` below with the contents of the `.json` service key obtained from Google console:

```xml
<clickhouse>
    <named_collections>
        <bigquery_credentials>
            <project>bigquery-clickhouse</project>
            <dataset>stackoverflow</dataset>
            <table>badges</table>
            <service_account_key><![CDATA[your_service_key]]></service_account_key>
        </bigquery_credentials>
    </named_collections>
</clickhouse>
```

Confirm your named collection is present:

<pre><code type='click-ui' language='sql'>
SELECT *
FROM system.named_collections;
</code></pre>

```shell
┌─name────────┬─collection───────────────────────────────────────────────────────────────────┬─source─┬─create_query─┐
│ my_bigquery │ {'dataset':'[HIDDEN]','project':'[HIDDEN]','service_account_key':'[HIDDEN]'} │ CONFIG │              │
└─────────────┴──────────────────────────────────────────────────────────────────────────────┴────────┴──────────────┘
```

Now use the named collection as the argument to the `bigquery` table function to see the data shape:

<pre><code type='click-ui' language='sql'>
DESCRIBE TABLE bigquery(bigquery_credentials);
</code></pre>

```shell
Query id: dd1e8285-b286-4892-8770-eeed49ef6919

┌─name─────┬─type───────────────────────────┬─default_type─┬─default_expression─┬─comment─┬─codec_expression─┬─ttl_expression─┐
│ Id       │ Nullable(Int64)                │              │                    │         │                  │                │
│ UserId   │ Nullable(Int64)                │              │                    │         │                  │                │
│ Name     │ Nullable(String)               │              │                    │         │                  │                │
│ Date     │ Nullable(DateTime64(6, 'UTC')) │              │                    │         │                  │                │
│ Class    │ Nullable(Int64)                │              │                    │         │                  │                │
│ TagBased │ Nullable(Int64)                │              │                    │         │                  │                │
└──────────┴────────────────────────────────┴──────────────┴────────────────────┴─────────┴──────────────────┴────────────────┘

6 rows in set. Elapsed: 0.602 sec.
```

You can now easily create the same table locally and insert the data:

<pre><code type='click-ui' language='sql'>
CREATE TABLE bq_badges
(
    Id       Int64,
    UserId   Int64,
    Name     LowCardinality(String),
    Date     DateTime64(6, 'UTC'),
    Class    Int64,
    TagBased Int64
)
ENGINE = MergeTree
ORDER BY (Id);

INSERT INTO bq_badges SELECT * FROM bigquery(bigquery_credentials) LIMIT 5; -- I don't want to max out my credit card

SELECT * FROM bq_badges;
</code></pre>

```shell
┌───────Id─┬───UserId─┬─Name────────┬───────────────────────Date─┬─Class─┬─TagBased─┐
│  3336768 │  1033808 │ Copy Editor │ 2012-05-03 22:19:43.187000 │     1 │        0 │
│  6687355 │    19299 │ .net        │ 2013-06-15 03:03:52.690000 │     1 │        1 │
│ 12885730 │  3892259 │ Copy Editor │ 2015-01-31 14:43:59.373000 │     1 │        0 │
│ 39830489 │ 10659482 │ Copy Editor │ 2020-12-09 11:16:11.410000 │     1 │        0 │
│ 40413130 │  1386551 │ Copy Editor │ 2021-01-29 18:00:54.783000 │     1 │        0 │
└──────────┴──────────┴─────────────┴────────────────────────────┴───────┴──────────┘

5 rows in set. Elapsed: 0.005 sec.
```


## S3 Tables {#s3_tables}

### Contributed by Konstantin Vedernikov

ClickHouse 26.8 adds write support for Amazon S3 Tables, AWS’s managed service for Iceberg tables. Alongside querying existing tables, you can now insert data and create new tables.

First, let’s enable the Iceberg catalog integration and writes:

<pre><code type='click-ui' language='sql'>
SET allow_database_iceberg = 1;
SET allow_insert_into_iceberg = 1;
</code></pre>

With AWS credentials configured to access your table bucket, we can connect using the `DataLakeCatalog` database engine. Replace the region and warehouse ARN below with your own:

<pre><code type='click-ui' language='sql'>
CREATE DATABASE tables
ENGINE = DataLakeCatalog(
    'https://s3tables.us-east-1.amazonaws.com/iceberg'
)
SETTINGS
    catalog_type = 's3tables',
    region = 'us-east-1',
    warehouse = 'arn:aws:s3tables:us-east-1:123456789012:bucket/analytics';
</code></pre>

We can then list the available tables and query one. For example, if your bucket contains an `events` table in the `ns` namespace:

<pre><code type='click-ui' language='sql'>
SHOW TABLES FROM tables;

SELECT *
FROM tables.`ns.events`
LIMIT 10;
</code></pre>

We can now also write to the table, supplying values that match its schema:

<pre><code type='click-ui' language='sql'>
-- Replace … with values matching your table's columns.
INSERT INTO tables.`ns.events` VALUES (…);
</code></pre>


## Snowflake Horizon {#snowflake_horizon}

### Contributed by Melvyn Peignon

ClickHouse 26.8 adds support for reading and writing Iceberg tables through the Snowflake Horizon catalog. ClickHouse reads the underlying data files directly from object storage.

Let’s enable the Iceberg catalog integration and writes, then connect to the catalog. Replace the account endpoint, database name, personal access token, and Snowflake role below with your own. The role needs access to the Iceberg tables you want to use.

<pre><code type='click-ui' language='sql'>
SET allow_database_iceberg = 1;
SET allow_insert_into_iceberg = 1;

CREATE DATABASE horizon
ENGINE = DataLakeCatalog(
    'https://&lt;org&gt;-&lt;account&gt;.snowflakecomputing.com/polaris/api/catalog'
)
SETTINGS
    catalog_type = 'horizon',
    warehouse = 'ICEBERG_DB',
    catalog_credential = '&lt;PAT&gt;',
    auth_scope = 'session:role:&lt;ROLE&gt;',
    vended_credentials = 1;
</code></pre>

We can then list the available tables and query one. For example, if your catalog contains a `trades` table in the `schema` namespace:

<pre><code type='click-ui' language='sql'>
SHOW TABLES FROM horizon;

SELECT *
FROM horizon.`schema.trades`
LIMIT 10;
</code></pre>

To insert data, supply values that match the table’s schema:

<pre><code type='click-ui' language='sql'>
-- Replace … with values matching your table's columns.
INSERT INTO horizon.`schema.trades` VALUES (…);
</code></pre>

ClickHouse commits the changes through the Horizon catalog.

## Puffin file format {#puffin_file_format}

### Contributed by Konstantin Vedernikov

ClickHouse 26.8 adds support for the Puffin file format, which Apache Iceberg uses to store statistics and deletion vectors.

Let’s see how this works using a small sample file from the ClickHouse test suite:

<pre><code type='click-ui' language='sql'>
SELECT referenced_data_file, deleted_rows
FROM url(
    'https://raw.githubusercontent.com/ClickHouse/ClickHouse/693dee22dda0d7ff23343c326754ccfc24f3237f/tests/queries/0_stateless/data_puffin/file_properties_ok.puffin',
    'Puffin'
);
</code></pre>

```shell
┌─referenced_data_file───────────┬─deleted_rows─┐
│ /data/table/part-00000.parquet │ [2,5]        │
└───────────────────────────────┴──────────────┘
```

This tells us that row positions 2 and 5 in the referenced Parquet file are marked as deleted. We don’t need access to that Parquet file—the deletion information is stored in the Puffin file itself. This can help explain why rows present in a data file don’t appear when querying the Iceberg table.

We can also use the `PuffinMetadata` format to inspect the blob’s type and properties:

<pre><code type='click-ui' language='sql'>
SELECT blob_type, properties
FROM url(
    'https://raw.githubusercontent.com/ClickHouse/ClickHouse/693dee22dda0d7ff23343c326754ccfc24f3237f/tests/queries/0_stateless/data_puffin/file_properties_ok.puffin',
    'PuffinMetadata'
);
</code></pre>

For this file, the blob type is `deletion-vector-v1`, and its properties include a `cardinality` of `2`, matching the two deleted row positions above.


## Prefetching manifest files in Iceberg {#prefetching_manifest_files_in_iceberg}

### Contributed by Asya Shneerson and Konstantin Vedernikov

Before reading data from an Iceberg table, ClickHouse reads manifest files that describe its data and delete files. Fetching and processing this metadata can add noticeable startup time, especially when it requires many requests to object storage.

In 26.8, ClickHouse prefetches the next manifest file while parsing the current one, overlapping storage reads with CPU work.

Delete manifests are also read and decoded concurrently. Since these must be processed before reading data files, this helps queries on tables with many delete files start faster. The `iceberg_delete_manifest_decode_concurrency` setting controls how many delete manifests are decoded at once and defaults to `4`.

This release also fixes the S3 bucket-region cache for data lake catalogs, avoiding repeated requests to determine a bucket’s region.


## Native Parquet improvements {#native_parquet_improvements}

### Contributed by Alexey Milovidov and Vasily Chekalkin

ClickHouse 26.8 brings several improvements to Parquet reading, helping queries skip unnecessary data.

For queries with `ORDER BY` and `LIMIT`, ClickHouse can read the columns needed for sorting and filtering first, then fetch the remaining columns only for rows that survive the limit. This optimization is enabled by default.

Let’s find the ten latest events in a public Parquet dataset, using `WatchID` to break ties:

<pre><code type='click-ui' language='sql'>
SELECT URL, Title
FROM s3(
    'https://clickhouse-public-datasets.s3.amazonaws.com/hits_compatible/hits.parquet',
    NOSIGN
)
ORDER BY EventTime DESC, WatchID DESC
LIMIT 10
SETTINGS query_plan_optimize_lazy_materialization_for_object_storage = 1;
</code></pre>

We can compare this with lazy reading disabled by setting `query_plan_optimize_lazy_materialization_for_object_storage` to `0`. In repeated checks on ClickHouse 26.8.2.7, the query read approximately 6.6–6.7 GB from S3 with the optimization disabled and 1.5 GB with it enabled, returning the same ten rows.

Dictionary-based filtering also helps ClickHouse skip data for equality and `IN` conditions. Let’s find rows matching a particular phone model:

<pre><code type='click-ui' language='sql'>
SELECT count()
FROM s3(
    'https://clickhouse-public-datasets.s3.amazonaws.com/hits_compatible/hits.parquet',
    NOSIGN
)
WHERE MobilePhoneModel = 'GT-C3262';
</code></pre>

```shell
┌─count()─┐
│     200 │
└─────────┘
```

When a column chunk is fully dictionary-encoded, ClickHouse can skip its row group if the requested value is absent from the dictionary. This helps even when min/max statistics cannot rule out a match and Bloom filters are unavailable.

With dictionary filtering enabled, this query processed 12 data pages, compared with 226 when disabled. Both queries returned `200`. The `input_format_parquet_dictionary_filter_push_down` setting defaults to `1048576` (a 1 MiB dictionary-page limit); setting it to `0` disables the optimization.

GeoParquet queries also benefit from spatial pruning. ClickHouse uses bounding-box information to skip irrelevant row groups and pages, and applies spatial predicates during row reading.

## GROUP BY performance improvements {#group_by_performance_improvements}

### Contributed by Nihal Z. Miaji, Dmitriy Terenichev, Konstantin Bogdanov, Harikrishnan Prabakaran

The 26.8 release also sees a series of performance improvements for GROUP BYs, including:

* A new algorithm for parallel `GROUP BY` that adaptively combines the approaches used by the merging and splitting aggregators.  
* The 26.7 release fused `GROUP BY` with `ORDER BY LIMIT` for tables sorted by key. 26.8 does it for any read order, pruning groups that cannot appear in the result.  
* `GROUP BY` with a single-string key now uses much smaller hash table cells.  
* The final merge step in parallel `GROUP BY` queries now uses multiple threads, preventing it from becoming a single-threaded bottleneck.

We will go into more detail about these optimizations in a separate post.

## Joins {#joins}

### Contributed by Han Fei, Anton Popov, Robert Schulze, Alexey Milovidov, Vladimir Cherkasov, Alexander Gololobov

And as with every release, we have more improvements around joins, including:

* Column statistics are now built on `INSERT` by default for small tables, resulting in a 29% improvement across all TPC-H benchmarks.  
* JOINS whose condition was two inequalities used to be executed as a filtered `CROSS JOIN`. They will now use the sort-based `IEJoin` algorithm instead.  
* A new merge join algorithm, `parallel_full_sorting_merge`, that runs on all cores. The input is sharded by the keys' hash into independent per-shard merge joins.  
* A cost-based optimizer for distributed query plans. The new cost-based optimizer uses cardinality estimates to choose how distributed joins, aggregations, sorting, and data movement should be executed.

We’ll also write in more detail about these features in a separate post.


---

## Get started today

Interested in seeing how ClickHouse works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-1966-get-started-today-sign-up&utm_blogctaid=1966)

---