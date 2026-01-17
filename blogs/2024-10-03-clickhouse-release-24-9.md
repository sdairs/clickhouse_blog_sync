---
title: "ClickHouse Release 24.9"
date: "2024-10-03T15:42:22.761Z"
author: "The ClickHouse Team"
category: "Engineering"
excerpt: "ClickHouse 24.9 is available. In this post, you will learn about APPEND for refreshable materialized views, variant types for schema inference, and aggregate functions to analyze JSON"
---

# ClickHouse Release 24.9

Another month goes by, which means it’s time for another release! 

<p>
ClickHouse version 24.9 contains <b>23 new features</b> &#127873; <b>14 performance optimisations</b> &#x1F6F7;  <b>76 bug fixes</b> &#128027;
</p>

In this release, we’ve got the `APPEND` clause for refreshable materialized views, new functions for the `JSON` data type, and the `Variant` type can be returned by automatic schema inference.

## New Contributors

As always, we send a special welcome to all the new contributors in 24.9! ClickHouse's popularity is, in large part, due to the efforts of the community that contributes. Seeing that community grow is always humbling.

Below are the names of the new contributors:

*1on, Alexey Olshanskiy, Alexis Arnaud, Austin Bruch, Denis Hananein, Dergousov, Gabriel Mendes, Konstantin Smirnov, Kruglov Kirill, Marco Vilas Boas, Matt Woenker, Maxim Dergousov, Michal Tabaszewski, NikBarykin, Oleksandr, Pedro Ferreira, Rodrigo Garcia, Samuel Warfield, Sergey (Finn) Gnezdilov, Tuan Pham Anh, Zhigao Hong, baolin.hbl, gao chuan, haozelong, imddba, kruglov, leonkozlowski, m4xxx1m, marco-vb, megao, mmav, neoman36, okunev, siyuan*

Hint: if you’re curious how we generate this list… [here](https://gist.github.com/gingerwizard/5a9a87a39ba93b422d8640d811e269e9).

<iframe width="768" height="432" src="https://www.youtube.com/embed/ray6wJGCHbs?si=LR9zkciylnIYcb0X" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>


You can also [view the slides from the presentation](https://presentations.clickhouse.com/release_24.9).


## APPEND for Refreshable Materialized Views

### Contributed by Michael Kolupaev

[Refreshable Materialized Views](https://clickhouse.com/docs/en/materialized-view/refreshable-materialized-view) is an experimental version of materialized views that store the result of a query for quick retrieval later. In this release, we’ve added `APPEND` functionality, which means that rather than replacing the whole view, new rows will be added to the end of the table.

One use of this feature is to capture snapshots of values at a point in time. For example, let’s imagine that we have an `events` table populated by a stream of messages from Redpanda, Kafka, or another streaming data platform.


```sql
SELECT *
FROM events
LIMIT 10

Query id: 7662bc39-aaf9-42bd-b6c7-bc94f2881036

┌──────────────────ts─┬─uuid─┬─count─┐
│ 2008-08-06 17:07:19 │ 0eb  │   547 │
│ 2008-08-06 17:07:19 │ 60b  │   148 │
│ 2008-08-06 17:07:19 │ 106  │   750 │
│ 2008-08-06 17:07:19 │ 398  │   875 │
│ 2008-08-06 17:07:19 │ ca0  │   318 │
│ 2008-08-06 17:07:19 │ 6ba  │   105 │
│ 2008-08-06 17:07:19 │ df9  │   422 │
│ 2008-08-06 17:07:19 │ a71  │   991 │
│ 2008-08-06 17:07:19 │ 3a2  │   495 │
│ 2008-08-06 17:07:19 │ 598  │   238 │
└─────────────────────┴──────┴───────┘
```

This dataset has `4096` values in the `uuid` column, and we can write the following query to find the ones with the highest total count:

```sql
SELECT
    uuid,
    sum(count) AS count
FROM events
GROUP BY ALL
ORDER BY count DESC
LIMIT 10

┌─uuid─┬───count─┐
│ c6f  │ 5676468 │
│ 951  │ 5669731 │
│ 6a6  │ 5664552 │
│ b06  │ 5662036 │
│ 0ca  │ 5658580 │
│ 2cd  │ 5657182 │
│ 32a  │ 5656475 │
│ ffe  │ 5653952 │
│ f33  │ 5653783 │
│ c5b  │ 5649936 │
└──────┴─────────┘
```


Let’s say we want to capture the count for each `uuid` every 10 seconds and store it in a new table called `events_snapshot`. The schema of `events_snapshot` would look like this:


```sql
CREATE TABLE events_snapshot (
    ts DateTime32,
    uuid String,
    count UInt64
) 
ENGINE = MergeTree 
ORDER BY uuid;
```


We could then create a refreshable materialized view to populate this table:


```sql
SET allow_experimental_refreshable_materialized_view=1;

CREATE MATERIALIZED VIEW events_snapshot_mv
REFRESH EVERY 10 SECOND APPEND TO events_snapshot
AS SELECT
    now() AS ts,
    uuid,
    sum(count) AS count
FROM events
GROUP BY ALL;
```


We can then query `events_snapshot` to get the count over time for a specific `uuid`:


```sql
SELECT *
FROM events_snapshot
WHERE uuid = 'fff'
ORDER BY ts ASC
FORMAT PrettyCompactMonoBlock

┌──────────────────ts─┬─uuid─┬───count─┐
│ 2024-10-01 16:12:56 │ fff  │ 5424711 │
│ 2024-10-01 16:13:00 │ fff  │ 5424711 │
│ 2024-10-01 16:13:10 │ fff  │ 5424711 │
│ 2024-10-01 16:13:20 │ fff  │ 5424711 │
│ 2024-10-01 16:13:30 │ fff  │ 5674669 │
│ 2024-10-01 16:13:40 │ fff  │ 5947912 │
│ 2024-10-01 16:13:50 │ fff  │ 6203361 │
│ 2024-10-01 16:14:00 │ fff  │ 6501695 │
└─────────────────────┴──────┴─────────┘
```

## Variant Types in schema inference

### Contributed by Shaun Struwig

ClickHouse now supports automatic usage of the `Variable` data type for schema inference. This feature is disabled by default but enabled by setting ``input_format_try_infer_variants`.`

Let’s have a look at how it works when reading the following file:

*data1.json*
```json
{"id": [1], "name": "Mark"}
{"id": "agerty", "name": "Dale"}
```


The `id` field is an array of integers on the first row and a string on the second. Let’s query the file and return the type of the `id` column:


```sql
select *, toTypeName(id)
FROM file('data1.json')
SETTINGS input_format_try_infer_variants=1;

┌─id─────┬─name─┬─toTypeName(id)──────────────────────────┐
│ [1]    │ Mark │ Variant(Array(Nullable(Int64)), String) │
│ agerty │ Dale │ Variant(Array(Nullable(Int64)), String) │
└────────┴──────┴─────────────────────────────────────────┘
```


If we do that query without setting ``input_format_try_infer_variants=1``, we’ll see the following error message instead:


```text
Received exception:
Code: 636. DB::Exception: The table structure cannot be extracted from a JSON format file. Error:
Code: 53. DB::Exception: Automatically defined type String for column 'id' in row 1 differs from type defined by previous rows: Array(Int64). You can specify the type for this column using setting schema_inference_hints. (TYPE_MISMATCH) (version 24.9.1.3278 (official build)).
You can specify the structure manually: (in file/path/to/24.9/data1.json). (CANNOT_EXTRACT_TABLE_STRUCTURE)
```


Remember that the `Variant` data type won’t always be inferred where you want (or even expect) it to be inferred. For example, if the values in the `id` field can be cast to `String`, that will be the inferred type even if the `Variant` type could also be inferred. This is the case in the following file:

*data2.json*
```json
{"id": 1, "name": "Mark"}
{"id": "agerty", "name": "Dale"}
{"id": "2021-01-04", "name": "Tom"}
```


If we run the following query:


```sql
select *, toTypeName(id)
FROM file('data2.json')
SETTINGS input_format_try_infer_variants=1;

┌─id─────────┬─name─┬─toTypeName(id)───┐
│ 1          │ Mark │ Nullable(String) │
│ agerty     │ Dale │ Nullable(String) │
│ 2021-01-04 │ Tom  │ Nullable(String) │
└────────────┴──────┴──────────────────┘
```


The `id` column is inferred as `Nullable(String)` because every value can be cast to a string. You can still have it infer the `id` column as `Variant`, but you’ll have to supply a hint:


```sql
SET allow_experimental_variant_type=1;

SELECT *, toTypeName(id) 
FROM  file('data2.json') 
SETTINGS schema_inference_hints='id Variant(String, Int64, Date)';

┌─id─────────┬─name─┬─toTypeName(id)───────────────┐
│ 1          │ Mark │ Variant(Date, Int64, String) │
│ agerty     │ Dale │ Variant(Date, Int64, String) │
│ 2021-01-04 │ Tom  │ Variant(Date, Int64, String) │
└────────────┴──────┴──────────────────────────────┘
```

## Aggregate functions to analyze JSON

### Contributed by Pavel Kruglov

In the [24.8 release post](https://clickhouse.com/blog/clickhouse-release-24-08), we learned about the new `JSON` data type. This release sees more functions to operate on data in the `JSON` and `Dynamic` data types. Let’s see how to use them on this sample dataset:

*data3.json*
```json
{"id": 1, "name": "Mark"}
{"id": "agerty", "name": "Dale"}
{"id": "2021-01-04", "name": "Tom"}
{"id": ["1", 2, "3"], "name": "Alexey", "location": "Netherlands"}
```

We have the <code>[distinctJSONPaths](https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/distinctjsonpaths)</code> function, which returns distinct JSON paths. 

```sql
SELECT distinctJSONPaths(json)
FROM file('data3.json', JSONAsObject)
FORMAT Vertical;

Row 1:
──────
distinctJSONPaths(json): ['id','location','location.city','location.country','name']
```

If you want to return the types as well, `distinctJSONPathsAndTypes` does that:

```sql
SELECT distinctJSONPathsAndTypes(json)
FROM file('data3.json', JSONAsObject)
FORMAT Vertical;

Row 1:
──────
distinctJSONPathsAndTypes(json): {'id':['Array(Nullable(String))','Int64','String'],'location':['String'],'location.city':['String'],'location.country':['String'],'name':['String']}
```

Finally, we have <code>[distinctDynamicTypes](https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/distinctdynamictypes)</code>, which returns distinct types for <code>Dynamic</code> columns.

```sql
SELECT distinctDynamicTypes(json.id)
FROM file('data3.json', JSONAsObject)
FORMAT Vertical

Row 1:
──────
distinctDynamicTypes(json.id): ['Array(Nullable(String))','Int64','String']
```

## _headers column for URL engine

### Contributed by Flynn

When you query the `url` table function, you can now access the response headers via the `_headers` virtual column:


```sql
SELECT _headers
FROM url(
'https://en.wikipedia.org/w/api.php?action=query&list=recentchanges&rcprop=title%7Cids%7Csizes%7Cflags%7Cuser%7Cuserid%7Ctimestamp&format=json&rcdir=newer'
)
LIMIT 1
FORMAT Vertical;


Row 1:
──────
_headers: {'accept-ranges':'bytes','age':'0','cache-control':'private, must-revalidate, max-age=0','content-disposition':'inline; filename=api-result.json','content-type':'application/json; charset=utf-8','date':'Tue, 01 Oct 2024 15:32:59 GMT','nel':'{ "report_to": "wm_nel", "max_age": 604800, "failure_fraction": 0.05, "success_fraction": 0.0}','report-to':'{ "group": "wm_nel", "max_age": 604800, "endpoints": [{ "url": "https://intake-logging.wikimedia.org/v1/events?stream=w3c.reportingapi.network_error&schema_uri=/w3c/reportingapi/network_error/1.0.0" }] }','server':'mw-api-ext.codfw.main-54d5bc66d9-98km5','server-timing':'cache;desc="pass", host;desc="cp3067"','set-cookie':'WMF-Last-Access=01-Oct-2024;Path=/;HttpOnly;secure;Expires=Sat, 02 Nov 2024 12:00:00 GMT','strict-transport-security':'max-age=106384710; includeSubDomains; preload','transfer-encoding':'chunked','vary':'Accept-Encoding,Treat-as-Untrusted,X-Forwarded-Proto,Cookie,Authorization','x-cache':'cp3067 miss, cp3067 pass','x-cache-status':'pass','x-client-ip':'82.35.72.115','x-content-type-options':'nosniff','x-frame-options':'DENY'}
```

## overlay function

If you need to replace a string fragment with another string, that just got easier with the `overlay` function. You provide the initial string, the replacement string, and then the index where you want the replacement string to start and how many characters should be replaced.

We can use this function to make sure everyone knows that [chDB](https://clickhouse.com/docs/en/chdb) is cool as well!

```sql
SELECT overlay('ClickHouse is cool', 'and chDB are', 12, 2) AS res

┌─res──────────────────────────┐
│ ClickHouse and chDB are cool │
└──────────────────────────────┘
```

