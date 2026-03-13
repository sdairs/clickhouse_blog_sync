---
title: "5 ways to parse Dates and DateTimes in ClickHouse"
date: "2026-03-12T17:20:54.354Z"
author: "Mark Needham"
category: "Engineering"
excerpt: "5 Ways to Parse Dates and DateTimes in ClickHouse"
---

# 5 ways to parse Dates and DateTimes in ClickHouse

Dates come in all shapes and sizes - Unix timestamps from event streams, weird looking numeric dates from legacy database exports, ISO 8601 strings from APIs, and more. Lucky for us, ClickHouse has a rich set of functions to handle all of them and that's what we're going to explore in this blog post.

We'll start with the most explicit approaches: converting Unix timestamps with `fromUnixTimestamp`, parsing packed numeric dates with `YYYYMMDDToDate`, and parsing known format strings with `parseDateTime`. Then we'll look at the `parseDateTimeBestEffort` family for when the format is unknown or mixed. 

Finally, we'll cover how casting dates with the `cast_string_to_date_time_mode` setting might be a better choice than explicit function calls for some use cases.

<iframe width="768" height="432" src="https://www.youtube.com/embed/hVEAzVz_xIY?si=-8QknStXsAO9iMjI" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

## Unix timestamps {#unix_timestamps}

First up, Unix timestamps! Unix timestamps represent the number of seconds since January 1st, 1970. We can use the [`fromUnixTimestamp`](https://clickhouse.com/docs/en/sql-reference/functions/date-time-functions#fromUnixTimestamp) function to convert them:

<pre><code type='click-ui' language='sql' runnable='true'>
SELECT
    fromUnixTimestamp(1704067295) AS val1, toTypeName(val1);
</code></pre>

This returns a `DateTime` type. If you have milliseconds since January 1st, 1970, there's a different function — [`fromUnixTimestamp64Milli`](https://clickhouse.com/docs/en/sql-reference/functions/type-conversion-functions#fromUnixTimestamp64Milli) — and the type comes back as `DateTime64(3)`, where the `3` means precision up to milliseconds. 

<pre><code type='click-ui' language='sql' runnable='true'>
SELECT
    fromUnixTimestamp64Milli(1704067295123) AS val2, toTypeName(val2);
</code></pre>

For microseconds, [`fromUnixTimestamp64Micro`](https://clickhouse.com/docs/en/sql-reference/functions/type-conversion-functions#fromUnixTimestamp64Micro) returns `DateTime64(6)`:

<pre><code type='click-ui' language='sql' runnable='true'>
SELECT
    fromUnixTimestamp64Micro(1704067295123456) AS val3, toTypeName(val3);
</code></pre>

## Numeric date formats {#numeric_date_formats}

Sometimes dates are represented as plain numbers encoding the year, month, and day — with no separators or formatting. This is common in legacy database exports or flat files from mainframes. The function [`YYYYMMDDToDate`](https://clickhouse.com/docs/en/sql-reference/functions/date-time-functions#YYYYMMDDToDate) handles this:

<pre><code type='click-ui' language='sql' runnable='true'>
SELECT
    YYYYMMDDToDate(20240115) AS val1, toTypeName(val1);
</code></pre>

If the number also includes time information, [`YYYYMMDDhhmmssToDateTime`](https://clickhouse.com/docs/en/sql-reference/functions/date-time-functions#YYYYMMDDhhmmssToDateTime) handles that too:

<pre><code type='click-ui' language='sql' runnable='true'>
SELECT
    YYYYMMDDhhmmssToDateTime(20240115143022) AS val2, toTypeName(val2);
</code></pre>

## Known format strings {#known_format_strings}

APIs often return dates as strings. If you know the format, you can use [`parseDateTime`](https://clickhouse.com/docs/en/sql-reference/functions/type-conversion-functions#parseDateTime) with a MySQL date format string:

<pre><code type='click-ui' language='sql' runnable='true'>
SELECT
    parseDateTime('15/01/2024 14:30:22', '%d/%m/%Y %H:%i:%s') AS val1,
    toTypeName(val1);
</code></pre>

This returns a `DateTime` including the timezone. 

If you prefer Joda date format strings, there's [`parseDateTimeInJodaSyntax`](https://clickhouse.com/docs/en/sql-reference/functions/type-conversion-functions#parseDateTimeInJodaSyntax) which produces the same output:

<pre><code type='click-ui' language='sql' runnable='true'>
SELECT
    parseDateTimeInJodaSyntax('15/01/2024 14:30:22', 'dd/MM/yyyy HH:mm:ss') AS val2,
    toTypeName(val2);
</code></pre>

## Best effort parsing of DateTimes {#best_effort_parsing}

The previous three approaches all assumed we knew the exact date format. But what if we don't? That's where the [`parseDateTimeBestEffort`](https://clickhouse.com/docs/en/sql-reference/functions/type-conversion-functions#parseDateTimeBestEffort) family of functions comes in. Imagine we have dates in a mix of different formats:

<pre><code type='click-ui' language='sql' runnable='true'>
WITH dates AS (
    SELECT '2024-01-15T14:30:22.000Z' AS raw
    UNION ALL
    SELECT '2024-01-15' AS raw
    UNION ALL
    SELECT '1704067295' AS raw
)
SELECT raw, parseDateTimeBestEffort(raw) AS val, toTypeName(val)
FROM dates;
</code></pre>

We can also convert to `DateTime64` using [`parseDateTimeBestEffort64`](https://clickhouse.com/docs/en/sql-reference/functions/type-conversion-functions#parseDateTime64BestEffort), like the earlier functions:

<pre><code type='click-ui' language='sql' runnable='true'>
WITH dates AS (
    SELECT '2024-01-15T14:30:22.000Z' AS raw
    UNION ALL
    SELECT '2024-01-15' AS raw
    UNION ALL
    SELECT '1704067295' AS raw
)
SELECT raw, parseDateTime64BestEffort(raw) AS val, toTypeName(val)
FROM dates;
</code></pre>

What happens if we include a completely invalid date? 

<pre><code type='click-ui' language='sql' runnable='true'>
WITH dates AS (
    SELECT '2024-01-15T14:30:22.000Z' AS raw
    UNION ALL
    SELECT '2024-01-15' AS raw
    UNION ALL
    SELECT '1704067295' AS raw
    UNION ALL
    SELECT 'not a date' AS raw
)
SELECT raw, parseDateTime64BestEffort(raw) AS val, toTypeName(val)
FROM dates;
</code></pre>

ClickHouse throws an exception! 

We can work around this with the [`parseDateTimeBestEffort64OrNull`](https://clickhouse.com/docs/en/sql-reference/functions/type-conversion-functions#parseDateTime64BestEffortOrNull) variant, which returns `NULL` instead:

<pre><code type='click-ui' language='sql' runnable='true'>
WITH dates AS (
    SELECT '2024-01-15T14:30:22.000Z' AS raw
    UNION ALL
    SELECT '2024-01-15' AS raw
    UNION ALL
    SELECT '1704067295' AS raw
    UNION ALL
    SELECT 'not a date' AS raw
)
SELECT raw, parseDateTime64BestEffortOrNull(raw) AS val, toTypeName(val)
FROM dates;
</code></pre>

Or if you'd rather get an actual datetime value, [`parseDateTimeBestEffort64OrZero`](https://clickhouse.com/docs/en/sql-reference/functions/type-conversion-functions#parseDateTime64BestEffortOrZero) falls back to January 1st, 1970 at midnight:

<pre><code type='click-ui' language='sql' runnable='true'>
WITH dates AS (
    SELECT '2024-01-15T14:30:22.000Z' AS raw
    UNION ALL
    SELECT '2024-01-15' AS raw
    UNION ALL
    SELECT '1704067295' AS raw
    UNION ALL
    SELECT 'not a date' AS raw
)
SELECT raw, parseDateTime64BestEffortOrZero(raw) AS val, toTypeName(val)
FROM dates;
</code></pre>

## Casting {#casting}

If you'd rather avoid calling explicit parse functions throughout your queries, you can cast string values directly to date types using `::DateTime`. However, there's an important setting to be aware of: `cast_string_to_date_time_mode`.

By default it's set to `basic`, which handles standard formats like `YYYY-MM-DD` and `YYYY-MM-DD HH:MM:SS`, but anything else will fail. For broader format support, change it to `best_effort`. Note that this setting still throws an exception for completely invalid dates.

You can pass the setting inline per query:

<pre><code type='click-ui' language='sql' runnable='true'>
WITH dates AS (
    SELECT '2024-01-15T14:30:22.000Z' AS raw
    UNION ALL
    SELECT '2024-01-15' AS raw
    UNION ALL
    SELECT '1704067295' AS raw
)
SELECT raw, raw::DateTime AS val, toTypeName(val)
FROM dates
SETTINGS cast_string_to_date_time_mode = 'best_effort';
</code></pre>

Or configure it at the session level so you don't need it in every query:

<pre><code type='click-ui' language='sql'>
SET cast_string_to_date_time_mode = 'best_effort';
</code></pre>

Then the same query works without the `SETTINGS` clause:

<pre><code type='click-ui' language='sql'>
WITH dates AS (
    SELECT '2024-01-15T14:30:22.000Z' AS raw
    UNION ALL
    SELECT '2024-01-15' AS raw
    UNION ALL
    SELECT '1704067295' AS raw
)
SELECT raw, raw::DateTime AS val, toTypeName(val)
FROM dates;
</code></pre>

Finally, imagine that we have the following file that contains a variety of dates:

*dates.csv*
```csv
raw
2024-01-15T14:30:22.000Z
2024-01-15
1704067295
```

We can parse the dates in that file using the same approach:

<pre><code type='click-ui' language='sql'>
SELECT raw, raw::DateTime AS val, toTypeName(val)
FROM file('dates.csv', CSVWithNames);
</code></pre>

```shell
┌─raw──────────────────────┬─────────────────val─┬─toTypeName(val)─┐
│ 2024-01-15T14:30:22.000Z │ 2024-01-15 14:30:22 │ DateTime        │
│ 2024-01-15               │ 2024-01-15 00:00:00 │ DateTime        │
│ 1704067295               │ 2024-01-01 00:01:35 │ DateTime        │
└──────────────────────────┴─────────────────────┴─────────────────┘
```

---

## Get started today

Interested in seeing how ClickHouse works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-100-get-started-today-sign-up&utm_blogctaid=100)

---