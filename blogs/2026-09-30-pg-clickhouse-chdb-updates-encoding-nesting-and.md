---
title: "pg_clickhouse & chdb updates: Encoding, nesting, and types"
date: "2026-09-30T16:29:40.227Z"
author: "David Wheeler"
category: "Product"
excerpt: "The latest pg_clickhouse and chdb extension releases improve character encoding, interval handling, nested data, JSON, and type mappings between ClickHouse and Postgres."
---

# pg_clickhouse & chdb updates: Encoding, nesting, and types

Out now on GitHub and PGXN, [pg_clickhouse](https://clickhouse.com/docs/products/managed-postgres/extensions/pg_clickhouse/) v0.11.0 and the [chdb extension](https://clickhouse.com/docs/products/managed-postgres/extensions/chdb/)
v0.1.2 continue our dogged focus on cross-database compatibility. A slew of
these enhancements derive from our header-only C libraries, [clickhouse-c](https://github.com/serprex/clickhouse-c) and
[pg-clickhouse-c](https://github.com/ClickHouse/pg-clickhouse-c/). Let's take a look at just three of the changes in these
releases.

## What a character {#what_a_character}

First up, character encoding. In the process of developing the benchmark for
the [chdb extension post](https://clickhouse.com/blog/introducing-chdb-postgres), I discovered that [pg-clickhouse-c](https://github.com/ClickHouse/pg-clickhouse-c/) wasn't
validating character encodings on text columns. My colleague [Philip](https://clickhouse.com/authors/philip-dube) quickly
patched the library to raise an exception when any text- or json-based[^json]
type contains bytes that violate the database encoding.

This fix shipped in [chdb v0.1.1](https://pgxn.org/dist/chdb/0.1.1/), but we delayed pg_clickhouse a bit to avoid
errors for anyone with existing foreign tables that read invalidly-encoded
data. [pg_clickhouse](https://clickhouse.com/docs/products/managed-postgres/extensions/pg_clickhouse/) v0.11.0 adds a new [foreign server](https://clickhouse.com/docs/products/managed-postgres/extensions/pg_clickhouse/reference#create-server) option,
`check_encoding`, that provides encoding error handlers. The options are:

*   `fail` (default): raise an error
*   `remove`: remove invalid bytes
*   `replace`: under the UTF-8 encoding, replace invalid bytes with the
    Unicode replacement character (`�`); same as `remove` for other
    encodings
*   `truncate`: truncate the text at the first invalid byte

[chdb_hook](https://clickhouse.com/docs/products/managed-postgres/extensions/chdb/chdb_hook) v0.1.2 provides the same option for its [COPY](https://clickhouse.com/docs/products/managed-postgres/extensions/chdb/chdb_hook#copy-overloading) and [CREATE TABLE](https://clickhouse.com/docs/products/managed-postgres/extensions/chdb/chdb_hook#create-table-overloading)
commands. Both allow you to address errors resembling:

```shell
ERROR:  invalid byte sequence for encoding "UTF8": 0x81
```

Change the pg_clickhouse server configuration `check_encoding` to eliminate
the errors. The most legible will be `replace`:

<pre><code type='click-ui' language='sql'>
ALTER SERVER ch_server_name OPTIONS (ADD check_encoding 'replace');
</code></pre>

For chdb_hook, pass it as a [COPY](https://clickhouse.com/docs/products/managed-postgres/extensions/chdb/chdb_hook#copy-overloading) or [CREATE TABLE](https://clickhouse.com/docs/products/managed-postgres/extensions/chdb/chdb_hook#create-table-overloading) option:

<pre><code type='click-ui' language='sql'>
CREATE TABLE logs () WITH (
    copy_from      = 's3://chdb-lakedata-public/logs/logs-2026-08-26.csv',
    format         = 'CSVWithNames',
    check_encoding = 'replace'
);
</code></pre>

For UTF-8 encoded databases, invalid bytes will be replaced with `�`,

```shell
try=# SELECT * FROM ch_table ORDER BY id;
 id |   name
----+---------
  1 | Barrack
  2 | Ale�y
  3 | Leopold
  4 | An�n�e
```

For other database encodings, the offending characters will simply be removed:

```shell
try=# SELECT * FROM ch_table ORDER BY id;
 id |   name
----+---------
  1 | Barrack
  2 | Aley
  3 | Leopold
  4 | Ann
```

If, on the other hand, you need to retain byte compatibility, you'll need
to map the offending column to `bytea`, instead:

<pre><code type='click-ui' language='sql'>
ALTER FOREIGN TABLE ch_table ALTER name TYPE bytea;
</code></pre>

This will preserve the byte-for-byte binary data:

```shell
try=# SELECT * FROM ch_table ORDER BY id;
id |      name
----+------------------
  1 | \x4261727261636b
  2 | \x416c650079
  3 | \x4c656f706f6c64
  4 | \x416e006e8165
(4 rows)
```

But be aware that conversions to text will fail.

## Intervalid {#intervalid}

ClickHouse supports a panoply of [interval types](https://clickhouse.com/docs/reference/data-types/special-data-types/interval): `IntervalNanosecond`,
`IntervalHour`, `IntervalDay`, `IntervalYear`, and everything in between. In
previous releases, pg_clickhouse did not support these types; an attempt to
[import](https://clickhouse.com/docs/products/managed-postgres/extensions/pg_clickhouse/reference#import-foreign-schema) a ClickHouse table using one returned an error.

No more. [pg_clickhouse](https://clickhouse.com/docs/products/managed-postgres/extensions/pg_clickhouse/) v0.11.0 and [chdb_hook](https://clickhouse.com/docs/products/managed-postgres/extensions/chdb/chdb_hook) 0.1.2 import these types as
Postgres `interval` columns. So, given a ClickHouse table using, say,
`IntervalMillisecond`, as in the `duration` column here:

<pre><code type='click-ui' language='sql'>
CREATE TABLE logs (
    req_id    Int64                NOT NULL,
    start_at  DateTime64(6, 'UTC') NOT NULL,
    duration  IntervalMillisecond  NOT NULL,
    resource  Text                 NOT NULL,
    method    Enum8('GET' = 1, 'HEAD', 'POST', 'PUT', 'DELETE', 'PATCH') NOT NULL,
    node_id   Int64                NOT NULL,
    response  Int32                NOT NULL
) ENGINE = MergeTree
  ORDER BY start_at;
</code></pre>

On import, pg_clickhouse creates a table with a `duration interval` column:

| Column  |            Type             | Nullable |
| --- | --- | --- |
| req_id   | bigint                      | not null |
| start_at | timestamp(6) with time zone | not null |
| duration | interval                    | not null |
| resource | text                        | not null |
| method   | text                        | not null |
| node_id  | bigint                      | not null |
| response | integer                     | not null |

Of course pushdown also works. Say you want to count all the transactions that
*completed* before the end of the day yesterday. Just add the duration to the
start time:

```shell
try=# EXPLAIN (VERBOSE, COSTS OFF)
 SELECT COUNT(*)
   FROM logs
  WHERE start_at + duration < date_trunc('day', now());
                                                QUERY PLAN
-----------------------------------------------------------------------------------------------------------
 Foreign Scan
   Output: (count(*))
   Relations: Aggregate on (logs)
   Remote SQL: SELECT count(*) FROM "default".logs WHERE (((start_at + duration) < toStartOfDay(now64())))
(4 rows)
```

The `EXPLAIN (VERBOSE)` output shows the remote query that executes on
ClickHouse, which plainly pushes down `start_at + duration` for execution in
ClickHouse (along with the `COUNT()` aggregate[^ival_agg], of course).

The same pattern applies [chdb_hook](https://clickhouse.com/docs/products/managed-postgres/extensions/chdb/chdb_hook) v0.1.2: it imports chDB [interval types](https://clickhouse.com/docs/reference/data-types/special-data-types/interval)
as Postgres `interval` values. Both extensions also allow the interval types
to be imported as `bigint`s, instead. Simply create the foreign or copy target
table with `duration bigint` and the extension will do the rest.

## Nesting instinct {#nesting_instinct}

The pg_clickhouse http driver has supported the [JSON type](https://clickhouse.com/docs/reference/data-types/newjson) since v0.1, and
the binary driver since v0.3. However, although it would push down a
JSON property accessor, e.g.,

<pre><code type='click-ui' language='sql'>
SELECT * FROM things ORDER BY data -&gt;&gt; 'name';
</code></pre>

ClickHouse would return an error:

```shell
DB::Exception: Data types Variant/Dynamic are not allowed in ORDER BY keys, because it can lead to unexpected results.
Consider using a subcolumn with a specific data type instead
```

This error derives from the implementation of ClickHouse JSON objects:
ClickHouse wants to know a JSON property exists to sort. ClickHouse 25.3+
parameterized sub-columns assure property presence. An example:

<pre><code type='click-ui' language='sql'>
CREATE TABLE things (
    id    Int32 NOT NULL,
    data  JSON(
      id      UInt32,
      name    String,
      size    Enum('small', 'medium', 'large'),
      stocked Bool
    ) NOT NULL
) ENGINE = MergeTree PARTITION BY id ORDER BY (id);
</code></pre>

Previously, [pg_clickhouse](https://clickhouse.com/docs/products/managed-postgres/extensions/pg_clickhouse/) was unable to import parameterized JSON columns,
but v0.11.0 (and [chdb_hook](https://clickhouse.com/docs/products/managed-postgres/extensions/chdb/chdb_hook) v0.1.2), simply maps it to jsonb (or json), and
now `ORDER BY` on a property properly pushes down:

```shell
try=# SELECT * FROM things ORDER BY data ->> 'name';
 id |                              data
----+-----------------------------------------------------------------
  4 | {"id": 4, "name": "doodad", "size": "large", "stocked": false}
  3 | {"id": 3, "name": "gizmo", "size": "medium", "stocked": true}
  2 | {"id": 2, "name": "sprocket", "size": "small", "stocked": true}
  1 | {"id": 1, "name": "widget", "size": "large", "stocked": true}
(4 rows)
```

Similarly [pg_clickhouse](https://clickhouse.com/docs/products/managed-postgres/extensions/pg_clickhouse/) v0.11.0 and [chdb_hook](https://clickhouse.com/docs/products/managed-postgres/extensions/chdb/chdb_hook) v0.1.2 improved support for
unflattened [Nested type](https://clickhouse.com/docs/reference/data-types/nested-data-structures)s, as in this example:

<pre><code type='click-ui' language='sql'>
CREATE TABLE visits(
    visit_id  UInt64,
    user_id   UInt64,
    goals     Nested(
        serial    UInt32,
        order_id  String
    )
) ENGINE = MergeTree ORDER BY visit_id SETTINGS flatten_nested = 0;
</code></pre>

The [`flatten_nested=0`](https://clickhouse.com/docs/reference/settings/session-settings/other#flatten_nested) instructs ClickHouse to create a single `goals`
column formatted as an array of `Tuple(serial UInt32, order_id String)`
(rather than separate array columns for each field). Previously, neither
extension supported this structure. Now they offer two mappings.

By default [IMPORT FOREIGN SCHEMA](https://clickhouse.com/docs/products/managed-postgres/extensions/pg_clickhouse/reference#import-foreign-schema) and [chdb_hook](https://clickhouse.com/docs/products/managed-postgres/extensions/chdb/chdb_hook)'s [COPY](https://clickhouse.com/docs/products/managed-postgres/extensions/chdb/chdb_hook#copy-overloading) and
[CREATE TABLE](https://clickhouse.com/docs/products/managed-postgres/extensions/chdb/chdb_hook#create-table-overloading) commands map an unflattened Nested column to a two-dimensional
text array:

|  Column  |     Type      |
| -------- | ------------- |
| visit_id | numeric(20,0) |
| user_id  | numeric(20,0) |
| goals    | text[][]      |

This maps each item in a Nested value to an array of the textual
representation of each type:

```shell
try=# SELECT * FROM nest_bin.visits WHERE visit_id < 3 ORDER BY visit_id;
 visit_id | user_id |      goals      
----------+---------+-----------------
        1 |       1 | {{1,xx},{2,yy}}
(1 row)
```

The `goals` array contains two arrays with two text values each, the first for
`serial`, the second for `order_id`. This structure preserves the data at the
expense of its data type, although an INSERT on a pg_clickhouse table properly
converts types before inserting into ClickHouse:

<pre><code type='click-ui' language='sql'>
INSERT INTO visits
VALUES (2, 2, ARRAY[ ['3', 'aa'], ['4', 'bb'] ]);
</code></pre>

But we can do better. [pg_clickhouse](https://clickhouse.com/docs/products/managed-postgres/extensions/pg_clickhouse/) v0.11.0 also allows Nested values to map
to custom [composite types](https://www.postgresql.org/docs/current/rowtypes.html), as long as the order, type, and naming align
perfectly. Given the Nested type defined for `goals`:

```shell
Tuple(serial UInt32, order_id String)
```

We can create a type with the corresponding names and types and slot it into
the foreign table:

<pre><code type='click-ui' language='sql'>
CREATE TYPE goal_type AS (serial bigint, order_id text);
ALTER FOREIGN TABLE visits ALTER goals TYPE goal_type[];
</code></pre>

And now the Nested tuples translate to the composite type:

```shell
try=# SELECT * FROM nest_bin.visits WHERE visit_id < 3 ORDER BY visit_id;
 visit_id | user_id |        goals        
----------+---------+---------------------
        1 |       1 | {"(1,xx)","(2,yy)"}
        2 |       2 | {"(3,aa)","(4,bb)"}
```

Naturally we can also INSERT data in this format:

<pre><code type='click-ui' language='sql'>
INSERT INTO visits
VALUES (3, 3, ARRAY[row(5, 'jj'), row(6, 'zz')]::goal_type[]);
</code></pre>

The same pattern applies to [chdb_hook](https://clickhouse.com/docs/products/managed-postgres/extensions/chdb/chdb_hook) v0.1.2: When working with nested data
exported from ClickHouse or chDB, the Postgres target table can use a
multidimensional array of values or an array of an appropriately structured
composite type:

<pre><code type='click-ui' language='sql'>
CREATE TYPE event_status AS ENUM ('new', 'done');
CREATE TYPE event_point AS (x integer, y integer);
CREATE TYPE event_label AS (key text, value bigint);
CREATE TYPE event_item AS (id integer, name text);

CREATE TABLE events (
    status event_status,
    point  event_point,
    labels event_label[],
    items  event_item[]
);
</code></pre>

Then use the appropriate definitions for the data types in the `COPY` query
(or rely on one of the `*WithNamesAndTypes` formats) to import the data.

<pre><code type='click-ui' language='sql'>
COPY events FROM 's3://chdb-lakedata-public/examples/events.parquet' (
    structure $$
        status Enum8('new' = 1, 'done' = 2),
        point  Tuple(Int32, Int32),
        labels Map(String, Int64),
        items  Array(Tuple(id Int32, name String))
    $$
);
</code></pre>

Here we've used an `Array()` for the nested type; if the data was exported
from ClickHouse with unflattened ([`flatten_nested=0`](https://clickhouse.com/docs/reference/settings/session-settings/other#flatten_nested)) structure, you can use
`Nested`, instead:

<pre><code type='click-ui' language='sql'>
COPY events FROM 's3://chdb-lakedata-public/examples/events.parquet' (
    structure $$
        status Enum8('new' = 1, 'done' = 2),
        point  Tuple(Int32, Int32),
        labels Map(String, Int64),
        items  Nested(id Int32, name String)
    $$
);
</code></pre>

## Odds and ends {#odds_and_ends}

[pg_clickhouse](https://clickhouse.com/docs/products/managed-postgres/extensions/pg_clickhouse/) v0.11.0 ships a number of other improvements worth mentioning:

*   As sharp-eyed readers no doubt noticed, in addition to [interval
    mappings](#intervalid), the large integer types now map to appropriate
    Postgres numerics, and a number of other ClickHouse data types now map to
    appropriate Postgres counterparts:

    |   ClickHouse    |  PostgreSQL   |
    |---------------- | ------------- |
    | Int128          | numeric(39,0) |
    | Int256          | numeric(77,0) |
    | UInt64          | numeric(20,0) |
    | UInt128         | numeric(39,0) |
    | UInt256         | numeric(78,0) |
    | BFloat16        | float4        |
    | Time            | time          |
    | Time64(P)       | time          |
    | Tuple(...)      | text[]        |
    | Map(K,V)        | text[][]      |
    | LineString      | path          |
    | MultiLineString | path[]        |
    | MultiPolygon    | polygon[][]   |
    | Point           | point         |
    | Ring            | polygon       |
    | Polygon         | polygon[]     |

    The same mappings apply to [chdb extension](https://clickhouse.com/docs/products/managed-postgres/extensions/chdb/) v0.1.2.

*   The original `clickhouse_raw_query()` function, deprecated in v0.10.0, has
    been dropped. Update your code to use `clickhouse_query(server, sql)` to
    read rows and `CALL clickhouse_perform(server, sql)` to run statements
    that return none.

*   This release drops support for PostgreSQL 13, which has been unsupported
    by the Postgres community since September, 2025.

*   A [community contribution](https://github.com/ClickHouse/pg_clickhouse/pull/360), added pushdown for the PostgreSQL `sha224()`,
    `sha256()`, `sha384()`, and `sha512()` functions, along with supported
    constant-algorithm calls to the [pgcrypto](https://www.postgresql.org/docs/current/pgcrypto.html) extension's `digest()`
    function.

Have a look at the complete [pg_clickhouse changes](https://github.com/ClickHouse/pg_clickhouse/releases/tag/v0.11.0) and [chdb changes](https://github.com/ClickHouse/pg_chdb/releases/tag/v0.1.2) for
more details, including bug fixes. Then get them from the usual places. For
pg_clickhouse:

*   [PGXN](https://pgxn.org/dist/pg_clickhouse/)
*   [GitHub](https://github.com/ClickHouse/pg_clickhouse/releases/tag/v0.11.0)
*   [Docker](https://github.com/ClickHouse/pg_clickhouse/pkgs/container/pg_clickhouse)

And for the chdb extension:

*   [PGXN](https://pgxn.org/dist/chdb/)
*   [GitHub](https://github.com/ClickHouse/pg_chdb/releases/tag/v0.1.2)

[^json]: Yes of course JSON [prefers UTF-8](https://www.rfc-editor.org/info/rfc7159/#section-8.1) by definition, except when it's not.
    [JSON data in Postgres](https://www.postgresql.org/docs/current/datatype-json.html) must always use the database encoding.
[^ival_agg]: Unfortunately, ClickHouse interval types do not yet support
    aggregates themselves, so `avg(duration)`, for example, will fail. But do
    watch for [`avg`](https://github.com/ClickHouse/ClickHouse/pull/121458) and [`sum`](https://github.com/ClickHouse/ClickHouse/pull/121600) support in 26.10.


---

## Get started with ClickHouse Managed Postgres today

Interested in seeing how ClickHouse Managed Postgres works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?intent=pg&loc=blog-cta-2467-get-started-with-clickhouse-managed-postgres-today-sign-up&utm_blogctaid=2467)

---