---
title: "New functions you might have missed in 2025"
date: "2025-12-17T13:45:26.027Z"
author: "Mark Needham"
category: "Engineering"
excerpt: "Over 100 functions were added to ClickHouse in 2025. These were some of my favorites."
---

# New functions you might have missed in 2025

My colleague, Tom Schreiber, and I write a blog post after each ClickHouse release, focusing on the significant changes in each release, such as new data lake catalogs or improvements in join performance. 

But in each release, there are often new functions that we don’t get around to covering. In this blog post, I will highlight some of the new functions introduced in 2025 that you may have overlooked.

## How many functions were introduced in 2025?

First up, did you know that you can find out how many functions were introduced in 2025 by running the following query:

<pre><code type='click-ui' language='sql'>
select count() 
FROM system.functions 
WHERE introduced_in LIKE '25%';
</code></pre>

```shell
┌─count()─┐
│     119 │
└─────────┘
```

We can also count how many were introduced in each version. To do that, we’re going to borrow [a user-defined function that sorts semantic versions](https://clickhouse.com/blog/semantic-versioning-udf): 

<pre><code type='click-ui' language='sql'>
CREATE FUNCTION sortableSemVer AS version -> 
  arrayMap(
    x -> toUInt32OrZero(x), 
    splitByChar('.', extract(version, '(d+(.d+)+)'))
  );
</code></pre>

And then, we can write the following query:

<pre><code type='click-ui' language='sql'>
SELECT introduced_in, count()
FROM system.functions
WHERE introduced_in LIKE '25%'
GROUP BY ALL
ORDER BY sortableSemVer(introduced_in);
</code></pre>

```shell
┌─introduced_in─┬─count()─┐
│ 25.1          │       2 │
│ 25.2          │       2 │
│ 25.3          │       3 │
│ 25.4          │       7 │
│ 25.5          │      18 │
│ 25.6          │      17 │
│ 25.7          │      25 │
│ 25.8          │      18 │
│ 25.9          │       8 │
│ 25.10         │      10 │
│ 25.11         │       7 │
│ 25.12         │       2 │
└───────────────┴─────────┘
```

We can get a list of the functions by running the following query:

<pre><code type='click-ui' language='sql'>
 SELECT
    name,
    introduced_in AS version,
    if(length(description) > 80,
       substring(description, 1, 80) || '...',
       description) AS description
FROM system.functions
WHERE introduced_in LIKE '25%'
ORDER BY sortableSemVer(introduced_in);
</code></pre>

The results are limited to ten rows for brevity:

```shell
Row 1:
──────
name:        variantElement
version:     25.2
description:
Extracts a column with specified type from a `Variant` column.


Row 2:
──────
name:        numericIndexedVectorPointwiseMultiply
version:     25.7
description:
Performs pointwise multiplication between a numericIndexedVector and either ano...

Row 3:
──────
name:        __patchPartitionID
version:     25.5
description:
Internal function. Receives the name of a part and a hash of patch part's colum...

Row 4:
──────
name:        readWKBPolygon
version:     25.5
description:
                Parses a Well-Known Binary (WKB) representation of a Polygon ge...

Row 5:
──────
name:        initialQueryStartTime
version:     25.4
description:
Returns the start time of the initial current query.
`initialQueryStartTime` re...
```

Let’s take a look at some of the new functions!

## mapContainsValueLike

[mapContainsValueLike](https://clickhouse.com/docs/sql-reference/functions/tuple-map-functions#mapcontainsvaluelike) was added in ClickHouse 25.5 and checks whether a map contains a value that matches the specified pattern using the `LIKE` operator.

So, imagine we have the following query, which returns company names and use case details:

<pre><code type='click-ui' language='sql'>
SELECT
        'Netflix' AS company,
        map('use_case', 'streaming analytics', 'scale', '5 petabytes daily') AS details
    UNION ALL
    SELECT
        'Tesla',
        map('use_case', 'observability platform', 'scale', 'quadrillion rows', 'feature', 'vector search')
    UNION ALL
    SELECT
        'Anthropic',
        map('use_case', 'AI observability', 'scale', 'billions of events')
    UNION ALL
    SELECT
        'Uber',
        map('use_case', 'ride analytics', 'scale', 'petabyte scale')
FORMAT Vertical;
</code></pre>

```shell
Row 1:
──────
company: Netflix
details: {'use_case':'streaming analytics','scale':'5 petabytes daily'}

Row 2:
──────
company: Tesla
details: {'use_case':'observability platform','scale':'quadrillion rows','feature':'vector search'}

Row 3:
──────
company: Anthropic
details: {'use_case':'AI observability','scale':'billions of events'}

Row 4:
──────
company: Uber
details: {'use_case':'ride analytics','scale':'petabyte scale'}
```

We could then write the following query to check whether any of the values in the maps contain the terms `obser`, `petabyte`, or `vector`:

<pre><code type='click-ui' language='sql'>
WITH useCases AS (
    SELECT
        'Netflix' AS company,
        map('use_case', 'streaming analytics', 'scale', '5 petabytes daily') AS details
    UNION ALL
    SELECT
        'Tesla',
        map('use_case', 'observability platform', 'scale', 'quadrillion rows', 'feature', 'vector search')
    UNION ALL
    SELECT
        'Anthropic',
        map('use_case', 'AI observability', 'scale', 'billions of events')
    UNION ALL
    SELECT
        'Uber',
        map('use_case', 'ride analytics', 'scale', 'petabyte scale')
)
SELECT
    company,
    details,
    mapContainsValueLike(details, '%observ%') AS is_observability,
    mapContainsValueLike(details, '%petabyte%') AS petabyte_scale,
    mapContainsValueLike(details, '%vector%') AS has_vector_search
FROM useCases
FORMAT Vertical;
</code></pre>

And we’ll get back the following:

```shell
Row 1:
──────
company:           Netflix
details:           {'use_case':'streaming analytics','scale':'5 petabytes daily'}
is_observability:  0
petabyte_scale:    1
has_vector_search: 0

Row 2:
──────
company:           Tesla
details:           {'use_case':'observability platform','scale':'quadrillion rows','feature':'vector search'}
is_observability:  1
petabyte_scale:    0
has_vector_search: 1

Row 3:
──────
company:           Anthropic
details:           {'use_case':'AI observability','scale':'billions of events'}
is_observability:  1
petabyte_scale:    0
has_vector_search: 0

Row 4:
──────
company:           Uber
details:           {'use_case':'ride analytics','scale':'petabyte scale'}
is_observability:  0
petabyte_scale:    1
has_vector_search: 0
```

## perimeterCartesian

[`perimeterCartesian`](https://clickhouse.com/docs/sql-reference/functions/geo/geometry#perimetercartesian) was added in ClickHouse 25.10 and calculates the perimeter of the given Geometry object in the Cartesian (flat) coordinate system. 

Let’s have a look at how it works when computing the perimeter of a square:

<pre><code type='click-ui' language='sql'>
SELECT perimeterCartesian(readWKT('POLYGON((0 0,1 0,1 1,0 1,0 0))'));
</code></pre>

```shell
┌─perimeterCar⋯ 1,0 0))'))─┐
│                        4 │
└──────────────────────────┘
```

We also have [`perimeterSpherical`](https://clickhouse.com/docs/sql-reference/functions/geo/geometry#perimeterspherical), which calculates the perimeter of a Geometry object on the surface of a sphere. So, if we want to compute the perimeter of the M25 motorway that goes around London, we can use `perimeterSpherical` instead:

<pre><code type='click-ui' language='sql'>
WITH
    readWKT('POLYGON((0.13870239257812503 51.2968127854147, 0.16342163085937503 51.37403072457134, 0.212860107421875 51.41516045575089, 0.27053833007812506 51.483627853536014, 0.27328491210937506 51.54686881000932, 0.25405883789062506 51.633894901713354, 0.13870239257812503 51.67308742846449, 0.08102416992187501 51.695224736990404, -0.023345947265625003 51.68500886266592, -0.12222290039062501 51.69352225137908, -0.29525756835937506 51.71224607096211, -0.37490844726562506 51.71905281158759, -0.44631958007812506 51.68330599278565, -0.49850463867187506 51.64412230646439, -0.5259704589843751 51.55028473901506, -0.5039978027343751 51.51440469156115, -0.5369567871093751 51.44255973575031, -0.5177307128906251 51.37403072457134, -0.41061401367187506 51.30883300776494, -0.29525756835937506 51.30539897974217, -0.15243530273437503 51.272762896039936, 0.04531860351562501 51.272762896039936, 0.13870239257812503 51.2968127854147))') AS m25,
    perimeterSpherical(m25) AS per_rad
SELECT
    per_rad,
    per_rad * 6371000 AS per_meters,
    per_rad * 6371 AS per_km;
</code></pre>

This function returns the length in radians on a unit sphere, so we need to multiply by the Earth’s radius to get a result in meters or kilometers:

```shell
┌──────────────per_rad─┬─────────per_meters─┬─────────────per_km─┐
│ 0.027954722202348813 │ 178099.53515116428 │ 178.09953515116428 │
└──────────────────────┴────────────────────┴────────────────────┘
```

This motorway is actually 188 km in diameter, so we’re not too far off - we’ll put the difference down to my poor polygon drawing.

## HMAC

[HMAC](https://clickhouse.com/docs/sql-reference/functions/encryption-functions) (Hash-based Message Authentication Code) is a cryptographic construction used to verify the integrity and authenticity of a message simultaneously. ClickHouse 25.12 adds this function. 

Let’s have a look at how to use it by generating a signature for the word ‘ClickHouse’. The result is returned in hexadecimal format, so we’ll use the [`hex`](https://clickhouse.com/docs/sql-reference/functions/encoding-functions#hex) function to return it as a string:

<pre><code type='click-ui' language='sql'>
SELECT hex(HMAC('sha256', 'ClickHouse', 'mySecretKey'))
</code></pre>

```shell
┌─hex(HMAC('sha256', 'ClickHouse', 'mySecretKey'))─────────────────┐
│ 5A79F3AA2874164CFD9811F9D1DBCEBE428C9BC52A7F57303EC6BAFCD6C9377B │
└──────────────────────────────────────────────────────────────────┘
```

The message 'ClickHouse' and its signature can then be sent to another party. The recipient can verify the message's authenticity by computing the HMAC with their copy of the secret key and comparing it to the provided signature.

## argAndMin and argAndMax

ClickHouse 25.11 introduced the [argAndMax](https://clickhouse.com/docs/sql-reference/aggregate-functions/reference/argandmax) and [argandMin](https://clickhouse.com/docs/sql-reference/aggregate-functions/reference/argandmin) functions. Let’s explore these functions using the [UK property prices dataset](https://clickhouse.com/docs/getting-started/example-datasets/uk-price-paid).

Let’s say we want to get the most expensive property sold in 2025. We could write this query:

<pre><code type='click-ui' language='sql'>
SELECT max(price) 
FROM uk_price_paid 
WHERE toYear(date) = 2025;
</code></pre>

```shell
┌─max(price)─┐
│  127700000 │ -- 127.70 million
└────────────┘
```

   
What about getting the town corresponding to the maximum price? We can use the `argMax` function to do this:

<pre><code type='click-ui' language='sql'>
SELECT argMax(town, price) 
FROM uk_price_paid 
WHERE toYear(date) = 2025;
</code></pre>

```shell
┌─argMax(town, price)─┐
│ PURFLEET-ON-THAMES  │
└─────────────────────┘
```

The `argAndMax`  function lets us get the town as well as the corresponding maximum price:

<pre><code type='click-ui' language='sql'>
SELECT argAndMax(town, price) 
FROM uk_price_paid 
WHERE toYear(date) = 2025;
</code></pre>

```shell
┌─argAndMax(town, price)───────────┐
│ ('PURFLEET-ON-THAMES',127700000) │
└──────────────────────────────────┘
```

We can do the same with `argAndMin` to find the town and the corresponding minimum price:

<pre><code type='click-ui' language='sql'>
SELECT argAndMin(town, price) 
FROM uk_price_paid 
WHERE toYear(date) = 2025;
</code></pre>

```shell
┌─argAndMin(town, price)─┐
│ ('CAMBRIDGE',100)      │
└────────────────────────┘
```

That looks like bad data, as it’s fairly unlikely that a property was sold for £100 in 2025!

## sparseGrams

[`sparseGrams`](https://clickhouse.com/docs/sql-reference/functions/string-functions#sparseGrams) was added in ClickHouse 25.5, and finds all substrings of a given string that have a length of at least `n`, where the hashes of the `(n-1)` -grams at the borders of the substring are strictly greater than those of any `(n-1)`-gram inside the substring. It uses CRC32 as a hash function.

<iframe width="768" height="432" src="https://www.youtube.com/embed/K5LzKT4geq8?si=f1qDbYPBtyaWTZBx" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

Let’s see how it works:

<pre><code type='click-ui' language='sql'>
SELECT sparseGrams('ClickHouse') FORMAT Vertical;
</code></pre>

```shell
Row 1:
──────
sparseGrams('ClickHouse'): ['Cli','lic','ick','lick','ckH','kHo','ckHo','lickHo','Hou','ous','Hous','use']
```

The GitHub team invented this function, which can serve as a suitable replacement for n-grams when building search indexes.

## stringBytesUniq

Introduced in ClickHouse 25.6, [`stringBytesUniq`](https://clickhouse.com/docs/sql-reference/functions/string-functions#stringBytesUniq) counts the number of unique bytes in a string.  Let’s have a look at some examples:

<pre><code type='click-ui' language='sql'>
SELECT
    stringBytesUniq('ClickHouse') AS ch,
    stringBytesUniq('Alexey Milovidov') AS alexey,
    stringBytesUniq('AAAAA') AS a;
</code></pre>

```shell
┌─ch─┬─alexey─┬─a─┐
│ 10 │     11 │ 1 │
└────┴────────┴───┘
```

## financialInternalRateOfReturn

Introduced in ClickHouse 25.7, [`financialInternalRateOfReturn`](https://clickhouse.com/docs/sql-reference/functions/financial-functions) tells us the rate of return (on, for example, an investment) if it were computed annually. 

So, imagine we buy Apple stock at $113 in 2020, do nothing in 2021, 2022, 2023, and 2024, and then sell at $231 in 2025. We can work out the internal rate of return by running the following query:

<pre><code type='click-ui' language='sql'>
SELECT financialInternalRateOfReturn([-113, 0, 0, 0, 0, 231])
</code></pre>

```shell
┌─financialInt⋯0, 0, 231])─┐
│      0.15373669910090634 │
└──────────────────────────┘
```

This is equivalent to making a 15% return for every year between 2020 and 2025. We can check the logic by running the following query:

<pre><code type='click-ui' language='sql'>
SELECT 113 * power(1.15373669910090634, 5);
</code></pre>

```shell
┌─multiply(113⋯009064, 5))─┐
│       230.99999999999997 │
└──────────────────────────┘
```

There’s also a sister function, [`financialInternalRateOfReturnExtended`](https://clickhouse.com/docs/sql-reference/functions/financial-functions#financialInternalRateOfReturnExtended), which we can use to compute our rate of return when the cash flows occur at irregular intervals, i.e., on specific dates.

So we can use our same example of Apple stocks, but this time using the exact dates that we bought and sold the stock:

<pre><code type='click-ui' language='sql'>
SELECT financialInternalRateOfReturnExtended(
  [-113, 231],
  [toDate('2020-09-11'), toDate('2025-03-05')]
);
</code></pre>

```shell
┌─financialInt⋯5-03-05')])─┐
│      0.17295574412431242 │
└──────────────────────────┘
```

This time our rate of return is just over 17%.

## toInterval

Introduced in ClickHouse 25.4, [`toInterval`](https://clickhouse.com/docs/sql-reference/functions/type-conversion-functions#toInterval) creates an interval value from a numeric value and a unit string. 

We already have individual functions to perform this task (e.g., toIntervalSecond, toIntervalMinute, toIntervalDay, etc.), but this consolidates them under a single function.

Let’s see how to use it:

<pre><code type='click-ui' language='sql'>
SELECT
    toInterval(5, 'second') AS seconds,
    toTypeName(seconds) AS secType,
    toInterval(3, 'day') AS days,
    toTypeName(days) AS daysType,
    toInterval(2, 'month') AS months,
    toTypeName(months) AS monthsType;
</code></pre>

```shell

┌─seconds─┬─secType────────┬─days─┬─daysType────┬─months─┬─monthsType────┐
│       5 │ IntervalSecond │    3 │ IntervalDay │      2 │ IntervalMonth │
└─────────┴────────────────┴──────┴─────────────┴────────┴───────────────┘
```

We can also use this function to add to an existing DateTime, as shown below:

<pre><code type='click-ui' language='sql'>
WITH toDateTime('2025-12-17 12:32:12') AS currentTime
SELECT
    currentTime,
    currentTime + toInterval(7, 'day') + toInterval(23, 'hour') AS nextWeek;
</code></pre>

```shell
┌─────────currentTime─┬────────────nextWeek─┐
│ 2025-12-17 12:32:12 │ 2025-12-25 11:32:12 │
└─────────────────────┴─────────────────────
```

## timeSeriesRange

Introduced in version 25.8, [`timeSeriesRange`](https://clickhouse.com/docs/sql-reference/functions/time-series-functions#timeSeriesRange) allows us to generate a range of timestamps. It’s like the range function, but for DateTimes.

It returns an array of values, but we can use the `arrayJoin` function to explode the array into individual rows:

<pre><code type='click-ui' language='sql'>
SELECT arrayJoin(
  timeSeriesRange(
    '2025-06-01 00:00:00'::DateTime, 
    '2025-06-01 00:01:00'::DateTime, 
    10
)) AS ts;
</code></pre>

```shell
┌──────────────────ts─┐
│ 2025-06-01 00:00:00 │
│ 2025-06-01 00:00:10 │
│ 2025-06-01 00:00:20 │
│ 2025-06-01 00:00:30 │
│ 2025-06-01 00:00:40 │
│ 2025-06-01 00:00:50 │
│ 2025-06-01 00:01:00 │
└─────────────────────┘
```

We could then work out how long it’s been since each of those times:	

<pre><code type='click-ui' language='sql'>
WITH toDateTime('2025-12-17 12:32:12') AS currentTime
SELECT arrayJoin(
  timeSeriesRange(
    '2025-06-01 00:00:00'::DateTime, 
    '2025-06-01 00:01:00'::DateTime, 
    10
)) AS ts,
  formatReadableTimeDelta(now() - ts) AS timeAgo;
</code></pre>

```shell
┌──────────────────ts─┬─timeAgo────────────────────────────────────────────────┐
│ 2025-06-01 00:00:00 │ 6 months, 16 days, 14 hours, 10 minutes and 41 seconds │
│ 2025-06-01 00:00:10 │ 6 months, 16 days, 14 hours, 10 minutes and 31 seconds │
│ 2025-06-01 00:00:20 │ 6 months, 16 days, 14 hours, 10 minutes and 21 seconds │
│ 2025-06-01 00:00:30 │ 6 months, 16 days, 14 hours, 10 minutes and 11 seconds │
│ 2025-06-01 00:00:40 │ 6 months, 16 days, 14 hours, 10 minutes and 1 second   │
│ 2025-06-01 00:00:50 │ 6 months, 16 days, 14 hours, 9 minutes and 51 seconds  │
│ 2025-06-01 00:01:00 │ 6 months, 16 days, 14 hours, 9 minutes and 41 seconds  │
└─────────────────────┴────────────────────────────────────────────────────────┘
```