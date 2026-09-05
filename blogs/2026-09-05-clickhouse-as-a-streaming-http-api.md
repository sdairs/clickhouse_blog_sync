---
title: "ClickHouse as a streaming HTTP API"
date: "2026-09-04T13:12:17.190Z"
author: "Mark Needham"
category: "Product"
excerpt: "Learn how to build a streaming HTTP API directly in ClickHouse 26.8 with named handlers, typed parameters, pagination, framing formats, and access control."
---

# ClickHouse as a streaming HTTP API

It's common to put a thin API layer in front of ClickHouse that accepts HTTP parameters, constructs a query, and returns the results. In ClickHouse 26.8, we can do much of this directly using named HTTP handlers, result modification, and framing formats.

In this post, we're going to use these features to build a streaming HTTP API around the UK property prices dataset. We'll still need an application layer if our API has business logic, orchestration, or application-specific validation. But if it only exposes controlled ClickHouse queries, we can remove one layer from our architecture.

## Setting up the UK property prices dataset

The [UK property prices dataset](https://clickhouse.com/docs/get-started/sample-datasets/uk-price-paid) contains details of properties sold in the UK since 1995.
Let's start by creating a table:

```sql
CREATE TABLE uk_price_paid
(
    price UInt32,
    date Date,
    postcode1 LowCardinality(String),
    postcode2 LowCardinality(String),
    type Enum8(
        'terraced' = 1,
        'semi-detached' = 2,
        'detached' = 3,
        'flat' = 4,
        'other' = 0
    ),
    is_new UInt8,
    duration Enum8(
        'freehold' = 1,
        'leasehold' = 2,
        'unknown' = 0
    ),
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
```

The source CSV doesn't have a header, so ClickHouse's schema inference assigns its columns the names `c1` through `c16`. We'll use those positional names to transform the source fields while ingesting the data:

```sql
INSERT INTO uk_price_paid
SELECT
    toUInt32(c2) AS price,
    toDate(c3) AS date,
    splitByChar(' ', c4)[1] AS postcode1,
    splitByChar(' ', c4)[2] AS postcode2,
    transform(
        c5,
        ['T', 'S', 'D', 'F', 'O'],
        ['terraced', 'semi-detached', 'detached', 'flat', 'other']
    ) AS type,
    c6 = 'Y' AS is_new,
    transform(
        c7,
        ['F', 'L', 'U'],
        ['freehold', 'leasehold', 'unknown']
    ) AS duration,
    c8 AS addr1,
    c9 AS addr2,
    c10 AS street,
    c11 AS locality,
    c12 AS town,
    c13 AS district,
    c14 AS county
FROM url(
    'http://prod1.publicdata.landregistry.gov.uk.s3-website-eu-west-1.amazonaws.com/pp-complete.csv',
    'CSV'
)
SETTINGS
    schema_inference_make_columns_nullable = 0,
    max_http_get_redirects = 10;
```

## A few exploratory queries

Let's run some exploratory queries to get a feel for the data, starting with a count of transactions and the first and last transaction:

```sql
SELECT
    count() AS transactions,
    min(date) AS first_transaction,
    max(date) AS last_transaction
FROM uk_price_paid;
```

```shell
┌─transactions─┬─first_transaction─┬─last_transaction─┐
│     30452463 │        1995-01-01 │       2025-07-31 │
└──────────────┴───────────────────┴──────────────────┘
```

The following query computes the amount of disk space that the data takes:

```sql
SELECT formatReadableSize(sum(bytes_on_disk)) AS size_on_disk
FROM system.parts
WHERE database = 'default' AND table = 'uk_price_paid' AND active;
```

```shell
┌─size_on_disk─┐
│ 339.08 MiB   │
└──────────────┘
```

And if we want to find the towns and districts with the highest average sale price since the 1st January 2024, the following query does the job:

```sql
SELECT town, district, count() AS sales, round(avg(price)) AS average_price
FROM uk_price_paid
WHERE date >= '2024-01-01'
GROUP BY ALL
HAVING sales >= 100
ORDER BY average_price DESC
LIMIT 20;
```

```shell
┌─town───────────────┬─district───────────────┬─sales─┬─average_price─┐
│ LONDON             │ CITY OF WESTMINSTER    │  3830 │       2627535 │
│ LONDON             │ CITY OF LONDON         │   367 │       2523498 │
│ LONDON             │ KENSINGTON AND CHELSEA │  2694 │       2149896 │
│ PURFLEET-ON-THAMES │ THURROCK               │   126 │       1813003 │
│ VIRGINIA WATER     │ RUNNYMEDE              │   114 │       1600253 │
│ LONDON             │ CAMDEN                 │  3200 │       1331681 │
│ LEATHERHEAD        │ ELMBRIDGE              │   111 │       1273186 │
│ BARNET             │ ENFIELD                │   116 │       1235428 │
│ COBHAM             │ ELMBRIDGE              │   330 │       1222086 │
│ RADLETT            │ HERTSMERE              │   228 │       1219858 │
│ LONDON             │ RICHMOND UPON THAMES   │   708 │       1204016 │
│ BEACONSFIELD       │ BUCKINGHAMSHIRE        │   384 │       1160016 │
│ LONDON             │ HOUNSLOW               │   660 │       1157176 │
│ TRING              │ DACORUM                │   365 │       1082008 │
│ LONDON             │ HAMMERSMITH AND FULHAM │  3312 │       1059507 │
│ ESHER              │ ELMBRIDGE              │   418 │       1017787 │
│ RICHMOND           │ RICHMOND UPON THAMES   │   886 │        988095 │
│ WEYBRIDGE          │ ELMBRIDGE              │   612 │        980195 │
│ LEATHERHEAD        │ GUILDFORD              │   162 │        973938 │
│ ASCOT              │ BRACKNELL FOREST       │   147 │        962569 │
└────────────────────┴────────────────────────┴───────┴───────────────┘
```

## Configuring an API user

We'll create an `api_user` that we'll use to run all our queries against API endpoints.
This user has a default output format of `JSONEachRow` and a default limit of 10 records:

```sql
CREATE USER api_user
IDENTIFIED WITH no_password
HOST LOCAL
SETTINGS default_format = 'JSONEachRow', limit = 10;
```

The `limit` setting caps every result returned to our user at 10 rows unless a request specifies a different limit.

We'll then give this user the ability to query the `uk_price_paid` table:

```sql
GRANT SELECT ON uk_price_paid TO api_user;
```

## Create a named HTTP endpoint

We can create an HTTP endpoint using the [`CREATE HANDLER`](https://clickhouse.com/docs/reference/statements/create/handler) statement that was introduced in 26.8.
A handler requires a URL and a query to run. We can also specify which HTTP methods it supports; if we don't, it defaults to `GET`.

> **Note**
>
> Supported methods are `GET`, `POST`, `PUT` and `DELETE`.

The following handler returns the most expensive areas since the 1st January 2024, and will be queryable via a `GET` request to `/api/expensive-areas`:

```sql
CREATE HANDLER expensive_areas
URL '/api/expensive-areas'
METHODS (GET)
AS
SELECT town, district, count() AS sales, round(avg(price)) AS average_price
FROM uk_price_paid
WHERE date >= '2024-01-01'
GROUP BY ALL
HAVING sales >= 100
ORDER BY average_price DESC;
```

> **Note**
>
> The query is checked for syntactic correctness when the handler is created, but it isn't semantically analyzed. For example, ClickHouse won't check that referenced tables and columns exist until the API endpoint is called.
>
>
> Also, notice that our handler query doesn’t contain a `LIMIT` clause. The API user’s `limit` setting is applied to the final result, after HTTP-level filtering and ordering. It provides a default limit of 10 rows, which we can override for an individual request.

We can query this endpoint using cURL:

```bash
curl --silent --user 'api_user:' 'http://localhost:8123/api/expensive-areas'
```

```shell
{"town":"LONDON","district":"CITY OF WESTMINSTER","sales":3830,"average_price":2627535}
{"town":"LONDON","district":"CITY OF LONDON","sales":367,"average_price":2523498}
{"town":"LONDON","district":"KENSINGTON AND CHELSEA","sales":2694,"average_price":2149896}
{"town":"PURFLEET-ON-THAMES","district":"THURROCK","sales":126,"average_price":1813003}
{"town":"VIRGINIA WATER","district":"RUNNYMEDE","sales":114,"average_price":1600253}
{"town":"LONDON","district":"CAMDEN","sales":3200,"average_price":1331681}
{"town":"LEATHERHEAD","district":"ELMBRIDGE","sales":111,"average_price":1273186}
{"town":"BARNET","district":"ENFIELD","sales":116,"average_price":1235428}
{"town":"COBHAM","district":"ELMBRIDGE","sales":330,"average_price":1222086}
{"town":"RADLETT","district":"HERTSMERE","sales":228,"average_price":1219858}
```

This is a good start, but this query has hard-coded values for the date and number of sales, which limit its usefulness.
Let's see how to address that.

## Typed parameters

Just like a normal query, a handler query can include parameters.
The query for the following handler filters transactions by a provided town, date, and price:

```sql
CREATE HANDLER town_sales
URL '/api/town-sales'
METHODS (GET)
AS
SELECT
    date, price, type, duration,
    concat(postcode1, ' ', postcode2) AS postcode,
    district, street, addr1, addr2
FROM uk_price_paid
WHERE town = upperUTF8({town:String})
AND date >= {from:Date}
AND price >= {minimum_price:UInt32}
ORDER BY price DESC;
```

We can then call the API endpoint like this, passing in the parameters as part of the query string:

```bash
curl --silent --user 'api_user:' --get 'http://localhost:8123/api/town-sales' \
  --data-urlencode 'town=London' \
  --data-urlencode 'from=2024-01-01' \
  --data-urlencode 'minimum_price=1000000'
```

```shell
{"date":"2024-03-20","price":164300000,"type":"other","duration":"leasehold","postcode":"E14 5GX","district":"TOWER HAMLETS","street":"WATER STREET","addr1":"15","addr2":""}
{"date":"2024-03-20","price":164300000,"type":"other","duration":"leasehold","postcode":"E14 5GX","district":"TOWER HAMLETS","street":"WATER STREET","addr1":"15","addr2":""}
{"date":"2024-03-20","price":161890000,"type":"other","duration":"leasehold","postcode":"E14 5GX","district":"TOWER HAMLETS","street":"WATER STREET","addr1":"UNIT D1.1, 14","addr2":""}
{"date":"2024-12-13","price":138900000,"type":"other","duration":"leasehold","postcode":"NW1 4NT","district":"CITY OF WESTMINSTER","street":"INNER CIRCLE","addr1":"THE HOLME COTTAGE","addr2":""}
{"date":"2024-01-31","price":129706651,"type":"other","duration":"leasehold","postcode":"SW1A 2WH","district":"CITY OF WESTMINSTER","street":"THE MALL","addr1":"ADMIRALTY ARCH HOTEL","addr2":""}
{"date":"2025-03-31","price":124519556,"type":"other","duration":"freehold","postcode":"WC2E 7PS","district":"CITY OF WESTMINSTER","street":"TAVISTOCK STREET","addr1":"15","addr2":""}
{"date":"2024-01-23","price":115000000,"type":"other","duration":"freehold","postcode":"SW1Y 4SP","district":"CITY OF WESTMINSTER","street":"HAYMARKET","addr1":"HAYMARKET HOUSE, 28 - 29","addr2":"FIRST FLOOR"}
{"date":"2025-01-22","price":109500000,"type":"other","duration":"freehold","postcode":"EC2R 8EJ","district":"CITY OF LONDON","street":"POULTRY","addr1":"1","addr2":""}
{"date":"2024-07-05","price":101000000,"type":"other","duration":"freehold","postcode":"EC1R 5EN","district":"CAMDEN","street":"BACKHILL","addr1":"6","addr2":""}
{"date":"2024-11-30","price":93836616,"type":"other","duration":"leasehold","postcode":" ","district":"WANDSWORTH","street":"NINE ELMS LANE","addr1":"BUILDING A01 EMBASSY GARDENS","addr2":""}
```

We can also supply parameters as form fields in the body of a `POST` request, although we won't demonstrate a `POST` endpoint in this post.

## Typed parameters in the URL path

We can also specify parameters in the URL path.
The following handler captures `town` and `district_path` from the provided URL:

```sql
CREATE HANDLER town_sales_path
URL REGEXP '/api/town-sales/(?P<town>[^/]+)(?P<district_path>(?:/[^/]+)?)'
METHODS (GET)
AS
SELECT date, price, type, duration,
      concat(postcode1, ' ', postcode2) AS postcode,
      town, district, street, addr1, addr2
FROM uk_price_paid
WHERE town = upperUTF8({town:String})
AND (
    {district_path:String} = ''
    OR district = upperUTF8(substring({district_path:String}, 2))
);
```

A town must be provided, but a district is optional. If it's not provided, the query will only filter by town.

The following query finds sales in London:

```bash
curl --silent --user 'api_user:' --get 'http://localhost:8123/api/town-sales/LONDON'
```

```shell
{"date":"2010-10-15","price":420000,"type":"terraced","duration":"freehold","postcode":" ","town":"LONDON","district":"ISLINGTON","street":"ST CLEMENTS STREET","addr1":"1","addr2":""}
{"date":"2010-12-17","price":250000,"type":"flat","duration":"leasehold","postcode":" ","town":"LONDON","district":"TOWER HAMLETS","street":"BALTIMORE WHARF","addr1":"1","addr2":"APARTMENT 703"}
{"date":"2012-12-06","price":320000,"type":"flat","duration":"leasehold","postcode":" ","town":"LONDON","district":"BARNET","street":"LICHFIELD GROVE","addr1":"1","addr2":"FLAT 2"}
{"date":"2023-06-13","price":240000,"type":"other","duration":"leasehold","postcode":" ","town":"LONDON","district":"CITY OF LONDON","street":"GREAT ST THOMAS APOSTLE","addr1":"1 - 7","addr2":"COMMERCIAL UNIT 2"}
{"date":"2013-04-30","price":250000,"type":"semi-detached","duration":"freehold","postcode":" ","town":"LONDON","district":"GREENWICH","street":"MYRA STREET","addr1":"1 UNITY MEWS","addr2":""}
{"date":"2009-02-05","price":554000,"type":"detached","duration":"freehold","postcode":" ","town":"LONDON","district":"HACKNEY","street":"ANDRE STREET","addr1":"10","addr2":""}
{"date":"2022-12-15","price":1630000,"type":"other","duration":"leasehold","postcode":" ","town":"LONDON","district":"CAMDEN","street":"BLOOMSBURY WAY","addr1":"10","addr2":"EIGHTH FLOOR"}
{"date":"2011-07-11","price":610000,"type":"flat","duration":"leasehold","postcode":" ","town":"LONDON","district":"CAMDEN","street":"WILMOT PLACE","addr1":"10","addr2":"GROUND  FLOOR  FLAT"}
{"date":"2022-12-15","price":1630000,"type":"other","duration":"leasehold","postcode":" ","town":"LONDON","district":"CAMDEN","street":"BLOOMSBURY WAY","addr1":"10","addr2":"NINTH FLOOR"}
{"date":"2023-08-04","price":537500,"type":"other","duration":"leasehold","postcode":" ","town":"LONDON","district":"ISLINGTON","street":"DRAYTON PARK","addr1":"100","addr2":"PARKING SPACE 35"}
```

If we want to narrow that down to, say Camden, we'd do the following:

```bash
curl --silent --user 'api_user:' --get 'http://localhost:8123/api/town-sales/LONDON/CAMDEN'
```

```shell
{"date":"2002-09-25","price":900000,"type":"detached","duration":"leasehold","postcode":" ","town":"LONDON","district":"CAMDEN","street":"KILBURN HIGH ROAD","addr1":"1 - 4","addr2":"UNITS"}
{"date":"2002-03-19","price":235000,"type":"flat","duration":"leasehold","postcode":" ","town":"LONDON","district":"CAMDEN","street":"GREENCROFT GARDENS","addr1":"106","addr2":"FLAT 7"}
{"date":"2002-05-31","price":248000,"type":"flat","duration":"leasehold","postcode":" ","town":"LONDON","district":"CAMDEN","street":"CROFTDOWN ROAD","addr1":"11","addr2":"FIRST FLOOR FLAT"}
{"date":"2004-03-12","price":285000,"type":"flat","duration":"leasehold","postcode":" ","town":"LONDON","district":"CAMDEN","street":"CROFTDOWN ROAD","addr1":"11","addr2":"SECOND FLOOR FLAT"}
{"date":"2002-05-17","price":215000,"type":"flat","duration":"leasehold","postcode":" ","town":"LONDON","district":"CAMDEN","street":"HAVERSTOCK HILL","addr1":"119","addr2":"STUDIO B"}
{"date":"2002-06-26","price":239000,"type":"flat","duration":"leasehold","postcode":" ","town":"LONDON","district":"CAMDEN","street":"FITZROY STREET","addr1":"12 - 16","addr2":"FLAT 83"}
{"date":"2003-08-18","price":290000,"type":"flat","duration":"leasehold","postcode":" ","town":"LONDON","district":"CAMDEN","street":"FITZROY STREET","addr1":"12 - 16","addr2":"FLAT 88"}
{"date":"2004-09-17","price":625000,"type":"flat","duration":"leasehold","postcode":" ","town":"LONDON","district":"CAMDEN","street":"WEDDERBURN ROAD","addr1":"13","addr2":"FIRST FLOOR FLAT"}
{"date":"2005-03-08","price":290000,"type":"flat","duration":"leasehold","postcode":" ","town":"LONDON","district":"CAMDEN","street":"ABBEY ROAD","addr1":"132","addr2":"BASEMENT FLAT"}
{"date":"2003-06-27","price":310000,"type":"flat","duration":"leasehold","postcode":" ","town":"LONDON","district":"CAMDEN","street":"ABBEY ROAD","addr1":"132","addr2":"SECOND FLOOR FLAT"}
```

## General settings for result modification

Before ClickHouse 26.8, ClickHouse already supported `limit` and `offset` as parameters for out-of-band result modification.

26.8 adds support for new query settings (`filter`, `select`, `sort`, `order`, and `page`), as well as `output_format`, which explicitly overrides the output data format. Other new settings cover compression and input formats, which we won't explore in this read-only API example.

Let's see how to use these settings, starting with `order` and `limit`:

```bash
curl --silent --user 'api_user:' --get 'http://localhost:8123/api/town-sales/LONDON' \
  --data-urlencode 'order=price DESC' \
  --data-urlencode 'limit=3'
```

```shell
{"date":"2017-07-31","price":594300000,"type":"other","duration":"leasehold","postcode":"W1U 8EW","town":"LONDON","district":"CITY OF WESTMINSTER","street":"BAKER STREET","addr1":"55","addr2":"UNIT 53"}
{"date":"2018-02-08","price":569200000,"type":"other","duration":"freehold","postcode":"W1J 7BT","town":"LONDON","district":"CITY OF WESTMINSTER","street":"STANHOPE ROW","addr1":"2","addr2":""}
{"date":"2019-11-20","price":542540820,"type":"other","duration":"freehold","postcode":"NW5 2HB","town":"LONDON","district":"CAMDEN","street":"FORTESS ROAD","addr1":"36","addr2":""}
```

As we can see above, `order` accepts a SQL ordering expression. `sort` uses a more concise and URL-friendly syntax.
Prefixing a field with a `-` means descending order:

```bash
curl --silent --user 'api_user:' --get 'http://localhost:8123/api/town-sales/LONDON' \
  --data-urlencode 'sort=-price' \
  --data-urlencode 'limit=3'
```

We can also filter the results to only include properties that sold for more than £1,000,000:

```bash
curl --silent --user 'api_user:' --get 'http://localhost:8123/api/town-sales/LONDON' \
  --data-urlencode 'order=date' \
  --data-urlencode 'limit=3' \
  --data-urlencode 'filter=price > 1000000'
```

```shell
{"date":"1995-01-06","price":1250000,"type":"semi-detached","duration":"freehold","postcode":"W9 1AL","town":"LONDON","district":"CITY OF WESTMINSTER","street":"","addr1":"WHITE LODGE, 19A","addr2":""}
{"date":"1995-01-06","price":1252500,"type":"semi-detached","duration":"leasehold","postcode":"NW1 7SR","town":"LONDON","district":"CAMDEN","street":"PRINCE ALBERT ROAD","addr1":"7","addr2":""}
{"date":"1995-01-06","price":1600000,"type":"terraced","duration":"freehold","postcode":"SW10 9SW","town":"LONDON","district":"KENSINGTON AND CHELSEA","street":"HARLEY GARDENS","addr1":"2","addr2":""}
```

We can do multiple filters, as shown in the following query that returns properties sold for more than £1,000,000 in 2024 or later. We'll also add a secondary order field:

```bash
curl --silent --user 'api_user:' --get 'http://localhost:8123/api/town-sales/LONDON' \
  --data-urlencode 'order=date, price DESC' \
  --data-urlencode 'limit=3' \
  --data-urlencode 'filter=price > 1000000' \
  --data-urlencode "filter=date >= '2024-01-01'"
```

```shell
{"date":"2024-01-02","price":6000000,"type":"flat","duration":"leasehold","postcode":"NW8 7HN","town":"LONDON","district":"CITY OF WESTMINSTER","street":"ST JOHNS WOOD ROAD","addr1":"60","addr2":"APARTMENT 94"}
{"date":"2024-01-02","price":2400000,"type":"flat","duration":"leasehold","postcode":"SW19 5EF","town":"LONDON","district":"MERTON","street":"HIGH STREET WIMBLEDON","addr1":"EAGLE HOUSE","addr2":"7"}
{"date":"2024-01-02","price":1470000,"type":"flat","duration":"leasehold","postcode":"E14 9LX","town":"LONDON","district":"TOWER HAMLETS","street":"PARK DRIVE","addr1":"1","addr2":"APARTMENT 5402"}
```

Alternatively, we can combine both filter predicates using the `AND` keyword:

```bash
curl --silent --user 'api_user:' --get 'http://localhost:8123/api/town-sales/LONDON' \
  --data-urlencode 'order=date, price DESC' \
  --data-urlencode 'limit=3' \
  --data-urlencode "filter=price > 1000000 AND date >= '2024-01-01'"
```

`select` lets us choose which columns get returned:

```bash
curl --silent --user 'api_user:' --get 'http://localhost:8123/api/town-sales/LONDON' \
  --data-urlencode 'order=date, price DESC' \
  --data-urlencode 'limit=3' \
  --data-urlencode "filter=price > 1000000 AND date >= '2024-01-01'" \
  --data-urlencode "select=date,price,postcode"
```

```shell
{"date":"2024-01-02","price":6000000,"postcode":"NW8 7HN"}
{"date":"2024-01-02","price":2400000,"postcode":"SW19 5EF"}
{"date":"2024-01-02","price":1470000,"postcode":"E14 9LX"}
```

`page` lets us paginate through results. The following request gets the next three results. We include additional fields in the ordering so that rows with the same date and price are returned in a deterministic order:

```bash
curl --silent --user 'api_user:' --get 'http://localhost:8123/api/town-sales/LONDON' \
  --data-urlencode 'order=date, price DESC, postcode, district, street, addr1, addr2' \
  --data-urlencode 'limit=3' \
  --data-urlencode 'page=2' \
  --data-urlencode "filter=price > 1000000 AND date >= '2024-01-01'" \
  --data-urlencode "select=date,price,postcode"
```

```shell
{"date":"2024-01-02","price":1300000,"postcode":"E1W 1AG"}
{"date":"2024-01-02","price":1300000,"postcode":"NW1 1NB"}
{"date":"2024-01-02","price":1300000,"postcode":"W6 8JN"}
```

We can also change the output format:

```bash
curl --silent --user 'api_user:' --get 'http://localhost:8123/api/town-sales/LONDON' \
  --data-urlencode 'order=date, price DESC' \
  --data-urlencode 'limit=3' \
  --data-urlencode "filter=price > 1000000 AND date >= '2024-01-01'" \
  --data-urlencode 'output_format=JSONCompactColumns'
```

```shell
[
	["2024-01-02", "2024-01-02", "2024-01-02"],
	[6000000, 2400000, 1470000],
	["flat", "flat", "flat"],
	["leasehold", "leasehold", "leasehold"],
	["NW8 7HN", "SW19 5EF", "E14 9LX"],
	["LONDON", "LONDON", "LONDON"],
	["CITY OF WESTMINSTER", "MERTON", "TOWER HAMLETS"],
	["ST JOHNS WOOD ROAD", "HIGH STREET WIMBLEDON", "PARK DRIVE"],
	["60", "EAGLE HOUSE", "1"],
	["APARTMENT 94", "7", "APARTMENT 5402"]
]
```

## Filtering data dynamically

The 26.8 release also adds a new setting, `http_allow_filters_as_unrecognized_url_parameters`. When this setting is enabled, ClickHouse will interpret unrecognized URL parameters as `WHERE` filters.
We can enable it for our `api_user` like this:

```sql
ALTER USER api_user
ADD SETTINGS http_allow_filters_as_unrecognized_url_parameters = 1;
```

And then it simplifies the queries above that used the `filter` setting:

```bash
curl --silent --user 'api_user:' --get "http://localhost:8123/api/town-sales/LONDON" \
  --data-urlencode 'order=date,price DESC' \
  --data-urlencode 'limit=3' \
  --data-urlencode 'price>1000000' \
  --data-urlencode 'date>=2024-01-01'
```

## Listing handlers

We can query the `system.handlers` table to see the handlers that we've created:

```sql
SELECT name, url, methods
FROM system.handlers
ORDER BY name;
```

```shell
┌─name────────────┬─url───────────────────────────────────────────────────────────┬─methods─┐
│ expensive_areas │ /api/expensive-areas                                          │ ['GET'] │
│ town_sales      │ /api/town-sales                                               │ ['GET'] │
│ town_sales_path │ /api/town-sales/(?P<town>[^/]+)(?P<district_path>(?:/[^/]+)?) │ ['GET'] │
└─────────────────┴───────────────────────────────────────────────────────────────┴─────────┘
```

## Making a table an API endpoint

As well as building custom endpoints, we can also make a table an API endpoint.
To do this, we need to enable the `http_allow_path_requests` global setting:

`config.d/http-path-requests.yaml`

```yaml
http_allow_path_requests: 1
```

Because `http_allow_path_requests` cannot be changed without restarting the server, restart ClickHouse to apply the setting.

We'll need to enable a couple more settings for `api_user`:

```sql
ALTER USER api_user
ADD SETTINGS
    http_allow_table_as_file = 1,
    http_allow_database_as_path = 1;
```

* `http_allow_table_as_file` interprets the last path component as table, table.format, or table.format.compression.
* `http_allow_database_as_path` interprets a leading /database/ path component as the current database.

Once we've done that, we could write a query to return the most expensive properties in London in CSV format like this:

```bash
curl --silent --user 'api_user:' 'http://localhost:8123/default/uk_price_paid.csv?town=LONDON&sort=-price&limit=3'
```

```shell
594300000,"2017-07-31","W1U","8EW","other",0,"leasehold","55","UNIT 53","BAKER STREET","","LONDON","CITY OF WESTMINSTER","GREATER LONDON"
569200000,"2018-02-08","W1J","7BT","other",0,"freehold","2","","STANHOPE ROW","","LONDON","CITY OF WESTMINSTER","GREATER LONDON"
542540820,"2019-11-20","NW5","2HB","other",0,"freehold","36","","FORTESS ROAD","","LONDON","CAMDEN","GREATER LONDON"
```

We can also control the output format using the `format` parameter rather than as a suffix to the table name. And, as with the custom endpoints, we can specify which fields should be returned by using the `select` parameter:

```bash
curl --silent \
    --user 'api_user:' \
    --get 'http://localhost:8123/default/uk_price_paid' \
    --data-urlencode 'town=LONDON' \
    --data-urlencode 'sort=-price' \
    --data-urlencode 'limit=3' \
    --data-urlencode 'select=date,price,postcode1' \
    --data-urlencode 'format=JSONEachRow'
```

```shell
{"date":"2017-07-31","price":594300000,"postcode1":"W1U"}
{"date":"2018-02-08","price":569200000,"postcode1":"W1J"}
{"date":"2019-11-20","price":542540820,"postcode1":"NW5"}
```


## Streaming HTTP responses

Our HTTP response stream can now carry data, progress, totals, profile events, server logs, and exceptions.

A framing format wraps the query’s regular output in a stream of typed packets. In the following example, the data packet contains the `JSONEachRow` result, while the progress packet reports how much work ClickHouse performed. We disabled profile-event packets for brevity.

```bash
curl --no-buffer --silent --user 'api_user:' --get \
    'http://localhost:8123/api/town-sales/LONDON' \
    --data-urlencode 'sort=-price' \
    --data-urlencode 'limit=3' \
    --data-urlencode 'select=date,price,postcode' \
    --data-urlencode 'framing_output_format=JSONEachPacketString' \
    --data-urlencode 'send_profile_events=0'
```

```shell
{"packet":"data","data":"{\"date\":\"2017-07-31\",\"price\":594300000,\"postcode\":\"W1U 8EW\"}\n{\"date\":\"2018-02-08\",\"price\":569200000,\"postcode\":\"W1J 7BT\"}\n{\"date\":\"2019-11-20\",\"price\":542540820,\"postcode\":\"NW5 2HB\"}\n"}
{"packet":"progress","progress":{"read_rows":"2867200","read_bytes":"39810980","total_rows_to_read":"2867200","result_rows":"3","result_bytes":"902","elapsed_ns":"10055000","memory_usage":"1860249"}}
```

The `packet` field identifies what each packet contains. Here, the first packet contains the query result and the second contains the final progress counters. We use curl's `--no-buffer` option so that it displays each packet as soon as it arrives.

We can also return the query response as Server-Sent Events (SSE) by specifying the framing output format as `EventStream`:

```bash
curl --no-buffer --silent --user 'api_user:' --get \
    'http://localhost:8123/api/town-sales/LONDON' \
    --data-urlencode 'sort=-price' \
    --data-urlencode 'limit=3' \
    --data-urlencode 'select=date,price,postcode' \
    --data-urlencode 'framing_output_format=EventStream' \
    --data-urlencode 'send_profile_events=0'
```

```shell
event: data
data: eyJkYXRlIjoiMjAxNy0wNy0zMSIsInByaWNlIjo1OTQzMDAwMDAsInBvc3Rjb2RlIjoiVzFVIDhFVyJ9CnsiZGF0ZSI6IjIwMTgtMDItMDgiLCJwcmljZSI6NTY5MjAwMDAwLCJwb3N0Y29kZSI6IlcxSiA3QlQifQp7ImRhdGUiOiIyMDE5LTExLTIwIiwicHJpY2UiOjU0MjU0MDgyMCwicG9zdGNvZGUiOiJOVzUgMkhCIn0K

event: progress
data: {"read_rows":"2867200","read_bytes":"39810980","total_rows_to_read":"2867200","result_rows":"3","result_bytes":"902","elapsed_ns":"9820000","memory_usage":"1862345"}
```

You'll notice that the `data` event contains a Base64-encoded value. SSE is a line-oriented UTF-8 text protocol, whereas ClickHouse output can contain multiple lines, invalid UTF-8, or arbitrary binary data. ClickHouse therefore Base64-encodes the payload of each data packet so that it can be transported safely in a single SSE field and reconstructed byte-for-byte by the client. Other events, such as `progress`, remain readable JSON.

The previous two examples run too quickly for ClickHouse to return intermediate progress packets. To see those, the following query scans the full dataset to compute the number of sales, average price, and median price by year:

```bash
curl --no-buffer --silent --user 'api_user:' --get \
    'http://localhost:8123/' \
    --data-urlencode 'query=SELECT toYear(date) AS year, type, count() AS sales, round(avg(price)) AS average_price, quantileExact(0.5)(price) AS median_price FROM uk_price_paid GROUP BY year, type ORDER BY year, type' \
    --data-urlencode 'framing_output_format=EventStream' \
    --data-urlencode 'send_profile_events=0' \
    --data-urlencode 'interactive_delay=50000' \
    --data-urlencode 'max_threads=1'
```

`interactive_delay=50000` allows progress packets every 50 milliseconds, while `max_threads=1` slows the query enough to make them visible. We use these settings for the demo - don't do this in production!

```shell
event: progress
data: {"read_rows":"1177362","read_bytes":"8241534","total_rows_to_read":"6501466","elapsed_ns":"51300000"}

event: progress
data: {"read_rows":"14466268","read_bytes":"101263876","total_rows_to_read":"23712297","elapsed_ns":"252277000"}

event: progress
data: {"read_rows":"30452463","read_bytes":"213167241","total_rows_to_read":"30452463","elapsed_ns":"399507000"}

event: data
data: eyJ5ZWFy...Cg==

event: progress
data: {"read_rows":"30452463","read_bytes":"213167241","total_rows_to_read":"30452463","result_rows":"10","result_bytes":"917","elapsed_ns":"409242000","memory_usage":"19570057"}
```

The progress packets arrive while ClickHouse scans the table. Because this is an aggregation, the data packet arrives near the end, once ClickHouse has computed the final groups.

## Observing API requests

Requests to named handlers and direct table API paths are recorded in `system.query_log`. We can inspect recent successful HTTP requests with the following query:

```sql
SYSTEM FLUSH LOGS;

SELECT event_time, http_handler_name, http_request_url, query_duration_ms, read_rows, result_rows
FROM system.query_log
WHERE (type = 'QueryFinish') AND (http_request_url != '')
ORDER BY event_time DESC
LIMIT 3;
```

```shell
┌──────────event_time─┬─http_handler_name─┬─http_request_url───────────┬─query_duration_ms─┬─read_rows─┬─result_rows─┐
│ 2026-09-02 12:28:58 │ town_sales        │ /api/town-sales            │                12 │   2300102 │          10 │
│ 2026-09-02 12:28:16 │                   │ /default/uk_price_paid.csv │                26 │  26946287 │           3 │
│ 2026-09-02 12:28:12 │ town_sales_path   │ /api/town-sales/LONDON     │                15 │    647168 │       13958 │
└─────────────────────┴───────────────────┴────────────────────────────┴───────────────────┴───────────┴─────────────┘
```

For a named handler, `http_handler_name` contains the handler that processed the request. It is empty for a direct table API request, but `http_request_url` still records the requested path, excluding any query string.

26.8 also introduces a new system table, `system.user_query_log`, that lets users see their own query history without needing access to the full query log. We can therefore return all the API requests executed by `api_user` by running the following:

```bash
./clickhouse client --user api_user <<'SQL'
SELECT
    event_time, http_handler_name, http_request_url,
    query_duration_ms, read_rows, result_rows
FROM system.user_query_log
WHERE type = 'QueryFinish' AND http_request_url != ''
ORDER BY event_time DESC
LIMIT 3 FORMAT Pretty;
SQL
```

## Controlling access to handlers

A handler's URL can be requested by any user who can reach the HTTP server, but its query runs with the permissions of the authenticated user. There is no separate permission for invoking an individual handler.

To see this in action, let's create another API user who doesn't have access to `uk_price_paid`:

```sql
CREATE USER restricted_api_user
IDENTIFIED WITH no_password
HOST LOCAL
SETTINGS default_format = 'JSONEachRow', limit = 10;
```

We can confirm its grants by running:

```sql
SHOW GRANTS FOR restricted_api_user;
```

```shell
Ok.

0 rows in set. Elapsed: 0.002 sec.
```

Now let's try to call the `expensive_areas` handler as this user:

```bash
curl --silent --user 'restricted_api_user:' 'http://localhost:8123/api/expensive-areas'
```

We'll see the following output:

```shell
Code: 497. DB::Exception: restricted_api_user: Not enough privileges. To execute this query, it's necessary to have the grant SELECT ON default.uk_price_paid. (ACCESS_DENIED) (version 26.9.1.466 (official build))
```

As well as wrapping queries to tables, handlers can also wrap queries to views, which is a useful way to provide query access without exposing the whole table.
For example, we could create a view to expose only the aggregated result behind `expensive_areas` rather than the underlying transactions.

Let's create a user to own the view. This user will be able to query the `uk_price_paid` table, but `HOST NONE` prevents anyone from logging in to the account directly:

```sql
CREATE USER api_view_owner
IDENTIFIED WITH no_password
HOST NONE;

GRANT SELECT ON uk_price_paid
TO api_view_owner;
```

Next, we'll create a definer view containing the permitted query:

```sql
CREATE VIEW expensive_areas_api
DEFINER = api_view_owner
SQL SECURITY DEFINER
AS
SELECT town, district, count() AS sales, round(avg(price)) AS average_price
FROM uk_price_paid
WHERE date >= '2024-01-01'
GROUP BY ALL
HAVING sales >= 100;
```

`SQL SECURITY DEFINER` means that the view’s underlying query runs with `api_view_owner`’s permissions rather than the caller’s.

We'll then grant access to that view to our `restricted_api_user`:

```sql
GRANT SELECT ON expensive_areas_api
TO restricted_api_user;
```

We can then update the initial handler to query `expensive_areas_api` instead of `uk_price_paid` directly:

```sql
ALTER HANDLER expensive_areas
AS
SELECT *
FROM expensive_areas_api
ORDER BY average_price DESC;
```

The restricted user can now call the handler:

```bash
curl --silent --user 'restricted_api_user:' 'http://localhost:8123/api/expensive-areas'
```

```shell
{"town":"LONDON","district":"CITY OF WESTMINSTER","sales":3830,"average_price":2627535}
{"town":"LONDON","district":"CITY OF LONDON","sales":367,"average_price":2523498}
{"town":"LONDON","district":"KENSINGTON AND CHELSEA","sales":2694,"average_price":2149896}
{"town":"PURFLEET-ON-THAMES","district":"THURROCK","sales":126,"average_price":1813003}
{"town":"VIRGINIA WATER","district":"RUNNYMEDE","sales":114,"average_price":1600253}
{"town":"LONDON","district":"CAMDEN","sales":3200,"average_price":1331681}
{"town":"LEATHERHEAD","district":"ELMBRIDGE","sales":111,"average_price":1273186}
{"town":"BARNET","district":"ENFIELD","sales":116,"average_price":1235428}
{"town":"COBHAM","district":"ELMBRIDGE","sales":330,"average_price":1222086}
{"town":"RADLETT","district":"HERTSMERE","sales":228,"average_price":1219858}
```

But not the underlying table:

```bash
./clickhouse client -mn --user restricted_api_user --query "SELECT * FROM uk_price_paid"
```

```shell
Received exception from server (version 26.9.1):
Code: 497. DB::Exception: Received from localhost:9000. DB::Exception: restricted_api_user: Not enough privileges. To execute this query, it's necessary to have the grant SELECT ON default.uk_price_paid. (ACCESS_DENIED)
(query: SELECT * FROM default.uk_price_paid LIMIT 1)
```

This restricts the user to the data exposed by the view, rather than exclusively to the handler URL. `restricted_api_user` can query the `expensive_areas_api` view directly, but it still cannot access the underlying property transactions.

## Summary

In this post, we've used the features introduced in ClickHouse 26.8 to build an HTTP API around the UK property prices dataset. We created named endpoints with typed query-string and URL-path parameters, modified their results without changing the underlying queries, exposed a table directly through its URL, and streamed query data and progress in the same response.

We also used the query logs to observe API requests and a `SQL SECURITY DEFINER` view to expose an aggregated result without granting access to the underlying transactions. If an API only needs to expose controlled ClickHouse queries, these features can remove the need for a separate pass-through service, but we'll still want an application layer when we need business logic, orchestration, or application-specific validation.


---

## Get started today

Interested in seeing how ClickHouse works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-1772-get-started-today-sign-up&utm_blogctaid=1772)

---