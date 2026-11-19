---
title: "pg_clickhouse 0.11.1: Now with pgvector, UPDATE, DELETE pushdown"
date: "2026-11-19T11:52:49.701Z"
author: "David Wheeler"
category: "Engineering"
excerpt: "pg_clickhouse 0.11.1 brings pgvector search and UPDATE, DELETE, and TRUNCATE pushdown, plus closer PostgreSQL compatibility, to ClickHouse Managed Postgres."
---

# pg_clickhouse 0.11.1: Now with pgvector, UPDATE, DELETE pushdown

Don't let the minor version increment fool you: [pg_clickhouse v0.11.1](https://github.com/ClickHouse/pg_clickhouse/releases/tag/v0.11.1),
released last week, delivers a slew of improvements and bug fixes, including
`UPDATE`, `DELETE`, `TRUNCATE`, and [pgvector](https://github.com/pgvector/pgvector) search pushdown.

## pgvector type mapping {#pgvector_type_mapping}

Let's start with the latter: [pgvector](https://github.com/pgvector/pgvector) type mapping. Given this ClickHouse table:

<pre><code type='click-ui' language='sql'>
CALL clickhouse_perform('ch_server', $$
    CREATE TABLE items (
        id       Int32,
        category String,
        v        Array(Float32)
    ) ENGINE = MergeTree ORDER BY (id);
$$);
</code></pre>

[pg_clickhouse v0.11.1](https://github.com/ClickHouse/pg_clickhouse/releases/tag/v0.11.1) lets us map the `v` column to the `vector` type:

<pre><code type='click-ui' language='sql'>
CREATE EXTENSION vector;
CREATE FOREIGN TABLE items (
    id       int NOT NULL,
    category text NOT NULL,
    v        vector(4) NOT NULL
) SERVER ch_server;
</code></pre>

We use an explicit [CREATE FOREIGN TABLE](https://clickhouse.com/docs/products/managed-postgres/extensions/pg_clickhouse/reference#create-foreign-table) rather than [IMPORT FOREIGN SCHEMA](https://clickhouse.com/docs/products/managed-postgres/extensions/pg_clickhouse/reference#import-foreign-schema)
to map the ClickHouse `Array(Float32)` column to a PostgreSQL `vector` column.
It works for ClickHouse `Array(Float64)` columns, too. Now we can insert
`vector` array values:

<pre><code type='click-ui' language='sql'>
INSERT INTO items VALUES (0, 'a', '[0,0,0,0]');

INSERT INTO items
SELECT i, (ARRAY['a', 'b', 'c'])[i % 3 + 1],
       format('[%s,%s,%s,%s]', sin(i), cos(i), sin(i * 2), cos(i * 3))::vector
  FROM generate_series(1, 100) i;
</code></pre>

And of course select them:

<pre><code type='click-ui' language='sql'>
SELECT * FROM items ORDER BY id LIMIT 5;
</code></pre>

```shell
 id | category |                       v                       
----+----------+-----------------------------------------------
  0 | a        | [0,0,0,0]
  1 | b        | [0.84147096,0.5403023,0.9092974,-0.9899925]
  2 | c        | [0.9092974,-0.41614684,-0.7568025,0.96017027]
  3 | a        | [0.14112,-0.9899925,-0.2794155,-0.91113025]
  4 | b        | [-0.7568025,-0.6536436,0.98935825,0.84385395]
(5 rows)
```

### pgvector operator pushdown

[pg_clickhouse v0.11.1](https://github.com/ClickHouse/pg_clickhouse/releases/tag/v0.11.1) also pushes down a number of [pgvector](https://github.com/pgvector/pgvector) operators and
functions, including, most simply, `=`, visible in the "Remote SQL" line from
`EXPLAIN (VERBOSE)`:

<pre><code type='click-ui' language='sql'>
EXPLAIN (COSTS OFF, VERBOSE) SELECT * FROM items WHERE v = '[0,0,0,0]';
</code></pre>

```shell
                                               QUERY PLAN                                                
---------------------------------------------------------------------------------------------------------
 Foreign Scan on public.items
   Output: id, category, v
   Remote SQL: SELECT id, category, v FROM default.items WHERE ((v = cast([0,0,0,0] as Array(Float32))))
(3 rows)
```

The results come as no surprise:

<pre><code type='click-ui' language='sql'>
SELECT * FROM items WHERE v = '[0,0,0,0]';
</code></pre>

```shell
 id | category |     v     
----+----------+-----------
  0 | a        | [0,0,0,0]
(1 row)
```

Even better, pg_clickhouse pushes down the [pgvector distance operators](https://pgxn.org/dist/vector/#Querying). For
example, `<->` pushes down to the ClickHouse [L2Distance](https://clickhouse.com/docs/reference/functions/regular-functions/distance-functions#L2Distance) function once again
visible in the "Remote SQL" line from `EXPLAIN (VERBOSE)`:

<pre><code type='click-ui' language='sql'>
EXPLAIN (VERBOSE, COSTS OFF)
SELECT id FROM items ORDER BY v &lt;-&gt; '[0.3,-0.2,0.5,0.1]' LIMIT 5;
</code></pre>

```shell
                                                               QUERY PLAN                                                                
-----------------------------------------------------------------------------------------------------------------------------------------
 Foreign Scan on public.items
   Output: id, (v <-> '[0.3,-0.2,0.5,0.1]'::vector)
   Vector Search: L2Distance on v
   Vector Index: none
   Vector Index Not Used: column "v" has no vector index
   Remote SQL: SELECT id, v FROM default.items ORDER BY L2Distance(v, cast([0.3,-0.2,0.5,0.1] as Array(Float32))) ASC NULLS LAST LIMIT 5
(6 rows)
```

And the results:

<pre><code type='click-ui' language='sql'>
SELECT id FROM items ORDER BY v &lt;-&gt; '[0.3,-0.2,0.5,0.1]' LIMIT 5;
</code></pre>

```shell
 id 
----
  0
 33
 77
 58
 14
(5 rows)
```

The complete list of [pgvector](https://github.com/pgvector/pgvector) operators and functions that push down to
ClickHouse functions:

| pgvector Operator | pgvector function   | Name                     | ClickHouse       |
| ----------------- | ------------------- | ------------------------ | ---------------- |
| `=`               |                     | [equals](https://clickhouse.com/docs/reference/functions/regular-functions/comparison-functions#equals)                 | `=`              |
| `<>`              |                     | [notEquals](https://clickhouse.com/docs/reference/functions/regular-functions/comparison-functions#notEquals)              | `<>`             |
| `<->`             | `l2_distance()`     | L2 distance              | [L2Distance](https://clickhouse.com/docs/reference/functions/regular-functions/distance-functions#L2Distance)     |
| `<+>`             | `l1_distance()`     | L1 distance              | [L1Distance](https://clickhouse.com/docs/reference/functions/regular-functions/distance-functions#L1Distance)     |
| `<=>`             | `cosine_distance()` | cosine distance          | [cosineDistance](https://clickhouse.com/docs/reference/functions/regular-functions/distance-functions#cosineDistance) |
| `<#>`             |                     | (negative) inner product | [dotProduct](https://clickhouse.com/docs/reference/functions/regular-functions/array-functions#arrayDotProduct)     |
|                   | `inner_product()`   | inner product            | [dotProduct](https://clickhouse.com/docs/reference/functions/regular-functions/array-functions#arrayDotProduct)     |
|                   | `vector_dims()`     | number of dimensions     | [length](https://clickhouse.com/docs/reference/functions/regular-functions/array-functions#length)         |

### pgvector index pushdown

Sharp readers will have noticed the "Vector" lines in the plan output:

```shell
   Vector Search: L2Distance on v
   Vector Index: none
   Vector Index Not Used: column "v" has no vector index
```

That `Vector Index Not Used` line clearly tells us the query used no [vector similarity index](https://clickhouse.com/docs/reference/engines/table-engines/mergetree-family/annindexes#vector-similarity-index). But could it use one? Let's add an index and see:

<pre><code type='click-ui' language='sql'>
CALL clickhouse_perform('ch_server', $$
    ALTER TABLE items ADD INDEX v_idx v TYPE vector_similarity('hnsw', 'L2Distance', 4);
$$);
</code></pre>

Use the L2 distance operator again:

<pre><code type='click-ui' language='sql'>
EXPLAIN (VERBOSE, COSTS OFF)
SELECT id FROM items ORDER BY v &lt;-&gt; '[0.3,-0.2,0.5,0.1]' LIMIT 5;
</code></pre>

```shell
                                                               QUERY PLAN                                                                
-----------------------------------------------------------------------------------------------------------------------------------------
 Foreign Scan on public.items
   Output: id, (v <-> '[0.3,-0.2,0.5,0.1]'::vector)
   Vector Search: L2Distance on v
   Vector Index: v_idx
   Remote SQL: SELECT id, v FROM default.items ORDER BY L2Distance(v, cast([0.3,-0.2,0.5,0.1] as Array(Float32))) ASC NULLS LAST LIMIT 5
(5 rows)
```

Et voilà! It now detects that the ClickHouse table has a `L2Distance()` index
that the ClickHouse executor may have used for the query. The results remain
unchanged:

<pre><code type='click-ui' language='sql'>
SELECT id FROM items ORDER BY v &lt;-&gt; '[0.3,-0.2,0.5,0.1]' LIMIT 5;
</code></pre>

```shell
 id 
----
  0
 33
 77
 58
 14
(5 rows)
```

pg_clickhouse detects and reports the ClickHouse usage of `vector_similarity`
indexes using the similarity functions that correspond to the supported
operators ([cosineDistance](https://clickhouse.com/docs/reference/functions/regular-functions/distance-functions#cosineDistance), [L1Distance](https://clickhouse.com/docs/reference/functions/regular-functions/distance-functions#L1Distance), etc.)

## UPDATE, DELETE, TRUNCATE {#update_delete_truncate}

[pg_clickhouse v0.11.1](https://github.com/ClickHouse/pg_clickhouse/releases/tag/v0.11.1) also introduces support for `UPDATE`, `DELETE`, and
`TRUNCATE` statements on [MergeTree](https://clickhouse.com/docs/reference/engines/table-engines/mergetree-family/mergetree) family tables. It pushes down `UPDATE`
and `DELETE` statements as lightweight [UPDATE](https://clickhouse.com/docs/reference/statements/update) or [DELETE](https://clickhouse.com/docs/concepts/features/operations/delete/lightweight-delete) statements,
respectively, and `TRUNCATE` statements as [TRUNCATE](https://clickhouse.com/docs/reference/statements/truncate) statements, naturally.

Let's put them to work on the `items` table. First, [UPDATE](https://clickhouse.com/docs/reference/statements/update) requires a couple
of ClickHouse settings to be enabled:

<pre><code type='click-ui' language='sql'>
CALL clickhouse_perform('ch_server', $$
    ALTER TABLE items
    MODIFY SETTING enable_block_number_column = 1, enable_block_offset_column = 1;
$$);
</code></pre>

And now we can make updates:

<pre><code type='click-ui' language='sql'>
UPDATE items SET v = '[1,1,1,1]' WHERE id = 0;
</code></pre>

Check our work:

<pre><code type='click-ui' language='sql'>
select * FROM items where id = 0;
</code></pre>

```shell
 id | category |     v     
----+----------+-----------
  0 | a        | [1,1,1,1]
(1 row)
```

Now `DELETE`:

<pre><code type='click-ui' language='sql'>
DELETE FROM items where id = 0;
</code></pre>

Is it gone? Yup:

<pre><code type='click-ui' language='sql'>
select * FROM items where id = 0;
</code></pre>

```shell
 id | category | v 
----+----------+---
(0 rows)
```

Do be aware that PostgreSQL `UPDATE` and `DELETE`, unlike ClickHouse's, do not
require `WHERE` clauses. In the absence of a `WHERE` clause, pg_clickhouse
inserts `WHERE true` to match the PostgreSQL behavior. But you surely don't
want to update or delete every row in a ClickHouse table! As the [docs say](https://clickhouse.com/docs/reference/statements/update):

> Lightweight updates are designed to update small amounts of rows (up to
> about 10% of the table).

Instead of deleting every row, use `TRUNCATE`:

<pre><code type='click-ui' language='sql'>
TRUNCATE items;
</code></pre>

All gone:

<pre><code type='click-ui' language='sql'>
select COUNT(*) from items;
</code></pre>

```shell
 count 
-------
     0
(1 row)
```

## Other highlights {#other_highlights}

### Linear regression aggregate pushdown

[pg_clickhouse v0.11.1](https://github.com/ClickHouse/pg_clickhouse/releases/tag/v0.11.1) also adds pushdown for the `regr_*` family of linear
regression aggregate functions on ClickHouse 26.9 or later, when [ClickHouse added them](https://www.linkedin.com/posts/alasdair-brown_clickhouse-269-adds-the-regr-family-familiar-ugcPost-7507187538965688320-ChAW/). These include:

*   [regr_avgx](https://clickhouse.com/docs/reference/functions/aggregate-functions/regr_avgx)
*   [regr_avgy](https://clickhouse.com/docs/reference/functions/aggregate-functions/regr_avgy)
*   [regr_count](https://clickhouse.com/docs/reference/functions/aggregate-functions/regr_count)
*   [regr_intercept](https://clickhouse.com/docs/reference/functions/aggregate-functions/regr_intercept)
*   [regr_r2](https://clickhouse.com/docs/reference/functions/aggregate-functions/regr_r2)
*   [regr_slope](https://clickhouse.com/docs/reference/functions/aggregate-functions/regr_slope)
*   [regr_sxx](https://clickhouse.com/docs/reference/functions/aggregate-functions/regr_sxx)
*   [regr_sxy](https://clickhouse.com/docs/reference/functions/aggregate-functions/regr_sxy)
*   [regr_syy](https://clickhouse.com/docs/reference/functions/aggregate-functions/regr_syy)

Example:

<pre><code type='click-ui' language='sql'>
EXPLAIN (VERBOSE, COSTS OFF)
      SELECT regr_avgy(b, a) FROM agg_bin.agg_numbers;
</code></pre>

```shell
                              QUERY PLAN                              
----------------------------------------------------------------------
 Foreign Scan
   Output: (regr_avgy((b)::double precision, (a)::double precision))
   Relations: Aggregate on (agg_numbers)
   Remote SQL: SELECT regr_avgyOrNull(b, a) FROM agg_test.agg_numbers
(4 rows)
```

### Aggregate NULL results

The appearance of `regr_avgyOrNull()` in the previous sample output spoils the
news, but to be clear, this release also teaches `NULL`-returning aggregates
to actually return `NULL` rather than a ClickHouse default value (e.g., `0`)
when they aggregate no values. Rather than `sum`, `avg`, and `min`, etc.,
pg_clickhouse now pushes down `sumOrNull`, `avgOrNull`, and `minOrNull`, thus
matching Postgres behavior:

<pre><code type='click-ui' language='sql'>
EXPLAIN (VERBOSE, COSTS OFF) SELECT SUM(id) FROM items;
</code></pre>

```shell
                      QUERY PLAN                       
-------------------------------------------------------
 Foreign Scan
   Output: (sum(id))
   Relations: Aggregate on (items)
   Remote SQL: SELECT sumOrNull(id) FROM default.items
(4 rows)
```

<pre><code type='click-ui' language='sql'>
SELECT SUM(id) FROM items;
</code></pre>

```shell
 sum 
-----
    
(1 row)
```

### JSON subscript pushdown

JSONB subscript syntax, `data['a']['b']`, now pushes down to ClickHouse column
"dot notation":

<pre><code type='click-ui' language='sql'>
EXPLAIN (VERBOSE, COSTS OFF)
      SELECT id FROM json_http.events WHERE props['address']['city'] = '"Paris"';
</code></pre>

```shell
                                              QUERY PLAN                                              
------------------------------------------------------------------------------------------------------
 Foreign Scan on json_http.events
   Output: id
   Remote SQL: SELECT id FROM json_test.events WHERE ((toJSONString(props.address.city) = '"Paris"'))
(3 rows)
```

### TimeZone pushdown

On ClickHouse 23.6+, pg_clickhouse now always sets `session_timezone` to match
the PostgreSQL `TimeZone`, and passes the PostgreSQL `TimeZone` to DateTime
functions, thus ensuring compatibility of `timestamp` and `timestamptz`
values:

<pre><code type='click-ui' language='sql'>
EXPLAIN (VERBOSE, COSTS OFF)
      SELECT percentile_cont(0.95) WITHIN GROUP (
        ORDER BY date_part('epoch', timezone('UTC', c))
      ) FROM t1;
</code></pre>

```shell
                                                                  QUERY PLAN                                                                   
-----------------------------------------------------------------------------------------------------------------------------------------------
 Foreign Scan
   Output: (percentile_cont('0.95'::double precision) WITHIN GROUP (ORDER BY (date_part('epoch'::text, timezone('UTC'::text, c)))))
   Relations: Aggregate on (t1)
   Remote SQL: SELECT quantileOrNull(0.95)(toUnixTimestamp(toDateTime64(toString(c, 'America/Los_Angeles'), 6, 'UTC'))) FROM functions_test.t1
(4 rows)
```

### Unconstrained NUMERIC

For bare `numeric` columns, pg_clickhouse now uses `Decimal(76, 38)`, the
largest possible ClickHouse decimal size, and raises an error for longer
values. It also properly trims trailing zeros from such values, thanks to a
[community contribution](https://github.com/ClickHouse/pg_clickhouse/pull/459):

<pre><code type='click-ui' language='sql'>
EXPLAIN (VERBOSE, COSTS OFF)
      SELECT round(regr_syy(b, a)::numeric, 4), regr_syy(b, a)::numeric FROM agg_numbers;
</code></pre>

```shell
                                                                                QUERY PLAN                                                                                 
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
 Foreign Scan
   Output: (round((regr_syy((b)::double precision, (a)::double precision))::numeric, 4)), ((regr_syy((b)::double precision, (a)::double precision))::numeric)
   Relations: Aggregate on (agg_numbers)
   Remote SQL: SELECT round(cast(regr_syyOrNull(b, a), 'Nullable(Decimal(76, 38))'), 4), cast(regr_syyOrNull(b, a), 'Nullable(Decimal(76, 38))') FROM agg_test.agg_numbers
(4 rows)
```

Running this query, the output was previously:

```shell
                    round                     |                   regr_syy                   
----------------------------------------------+----------------------------------------------
 68756.21570000000000000000000000000000000000 | 68756.21569392930381649593538520770884423405
(1 row)
```

But now is:

```shell
   round    |                   regr_syy                   
------------+----------------------------------------------
 68756.2157 | 68756.21569392930381649593538520770884423405
(1 row)
```

## And the rest {#and_the_rest}

These changes cover the highlights; peruse the [changelog](https://github.com/ClickHouse/pg_clickhouse/releases/tag/v0.11.1) for all the things. And of course [pg_clickhouse v0.11.1](https://github.com/ClickHouse/pg_clickhouse/releases/tag/v0.11.1) is
available on all new and existing [ClickHouse Managed Postgres](https://clickhouse.com/cloud/postgres) servers today.
As a minor release all installs benefit from its improvements without any
action. But do run `ALTER EXTENSION pg_clickhouse UPDATE;` to upgrade from
v0.10 or earlier.


---

## Get started with ClickHouse Managed Postgres today

Interested in seeing how ClickHouse Managed Postgres works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?intent=pg&loc=blog-cta-3096-get-started-with-clickhouse-managed-postgres-today-sign-up&utm_blogctaid=3096)

---