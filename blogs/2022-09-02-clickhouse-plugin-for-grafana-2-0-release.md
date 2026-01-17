---
title: "ClickHouse Plugin for Grafana - 2.0 Release"
date: "2022-09-02T10:14:48.315Z"
author: "Dale McDiarmid"
category: "Engineering"
excerpt: "The 2.0 release of the ClickHouse plugin for Grafana improves filtering while adding support for HTTP and JSON."
---

# ClickHouse Plugin for Grafana - 2.0 Release

![Blog post.png](https://clickhouse.com/uploads/Blog_post_4b5c626548.png)

[Back in May](https://grafana.com/blog/2022/05/05/introducing-the-official-clickhouse-plugin-for-grafana/) 2022, we released a [first-party ClickHouse plugin for Grafana](https://grafana.com/grafana/plugins/grafana-clickhouse-datasource/), developed by Grafana in collaboration with ClickHouse. As part of our commitment to maintaining and improving this plugin, we are pleased to announce the release of version 2.0.

This major release includes a fundamental change to how we parse ClickHouse queries, which should help resolve a common set of issues encountered by our users around ad-hoc filters. We’ve also added support for using HTTP as the transport protocol and enhanced support for ClickHouse data types, including JSON.

## A better way to handle filters

When we initially developed the plugin, we wanted to use the latest plugin framework for Grafana. This ensures we support features such as Alerting, which has server-side dependencies. Through this new framework, we supported an initial implementation of Ad-hoc filters. This powerful Grafana feature is [only supported for the most popular data sources](https://grafana.com/docs/grafana/latest/variables/variable-types/add-ad-hoc-filters/), allowing users to filter all visualizations by selecting a column, operator, and value. While our initial offering largely worked, it relied on parsing SQL queries using a client-side [AST ](https://en.wikipedia.org/wiki/Abstract_syntax_tree)implementation. Even for experienced developers, this represents a complex problem - especially since ClickHouse SQL has several extensions to aid users in building analytical queries. This implementation was subsequently the source of  [several issues](https://github.com/grafana/clickhouse-datasource/issues?q=is%3Aissue+label%3A%22AST+2.0%22+), mainly associated with using [Grafana variables, templates](https://grafana.com/docs/grafana/latest/variables/), and subqueries.

Rather than investing more time in the AST parser, we contacted a team who had already solved this problem optimally: our friends in the ClickHouse core development team. After some [brief discussions](https://github.com/ClickHouse/ClickHouse/issues/29922), `additional_table_filters` were [born in 22.7](https://github.com/ClickHouse/ClickHouse/pull/38475). This allows any filter to be sent with a query as part of the SETTINGS. On parsing the query, ClickHouse can inject these filters into the appropriate clauses. 

Feel free to test any of the examples below against [sql.clickhouse.com](https://sql.clickhouse.com). Any tables are available in the `blogs` database, so `FROM <table>` clauses should be adjusted accordingly, i.e. `FROM blogs <table>`.

Consider the simple query from the [UK property price dataset](https://clickhouse.com/docs/en/getting-started/example-datasets/uk-price-paid).

<pre>
  <code type='click-ui' language='sql' runnable='true' run='false' play_link="https://sql.clickhouse.com?query_id=9IUASIZZPK6JYG3BU4RPUM">
SELECT
    toStartOfYear(date) AS time,
    town,
    round(avg(price)) AS price
FROM uk.uk_price_paid
WHERE town IN (
    SELECT town
    FROM uk.uk_price_paid
    WHERE town != 'GATWICK'
    GROUP BY town
    ORDER BY avg(price) DESC
    LIMIT 10
)
GROUP BY
    time,
    town
ORDER BY time ASC
</code>
</pre>

This simple query tells us the average price per town, for the top 10 most expensive towns in the UK, over time. Note that we exclude Gatwick as it represents an anomaly. This naturally renders as an area or line chart in Grafana. A logical filter here might be for the user to filter by town. Ensuring this is injected in the correct part of the query represents a challenge. A JavaScript-based solution, while possible, would need to cover all possible fringe cases. E.g., here we would optimally inject the town filter into the IN clause and AND with the `town != 'Gatwick'`.

<a href="/uploads/prices_per_town_a74296ab09.png" target="_blank">
         <img alt="prices_per_town.png" src="/uploads/prices_per_town_a74296ab09.png">
</a>

> Note: Due to insufficient permissions to use `additional_table_filters`, Adhoc filters will not work if using sql.clickhouse.com as your ClickHouse data source. See "Be aware of changes" below for further detail.

Adding an ad hoc filter and selecting `town=London`, causes Grafana to send the following query:

<pre>
  <code type='click-ui' language='sql'>
SELECT toStartOfYear(date) AS time, town, round(avg(price)) AS price
FROM uk_price_paid
WHERE town IN (SELECT town
               FROM uk_price_paid
               WHERE uk_price_paid.town != 'GATWICK'
               GROUP BY town
               ORDER BY avg(price) DESC
               LIMIT 10)
GROUP BY time, town
ORDER BY time SETTINGS additional_table_filters = {'uk_price_paid' : 'town = \'LONDON\' '}
</code>
</pre>


ClickHouse, in turn, does the hard work of figuring out where this clause needs to be added - note how the filter is specified as a map where the key is equal to the table name `uk_price_paid`.

<a href="/uploads/filtered_london_13f9c3c9b2.png" target="_blank">
         <img alt="filtered_london.png" src="/uploads/filtered_london_13f9c3c9b2.png">
</a>

Adding further filters is trivial. In the example below, we filter by district, focusing on Hackney.


<pre>
  <code type='click-ui' language='sql'>
SELECT toStartOfYear(date) AS time, town, round(avg(price)) AS price
FROM uk_price_paid
WHERE town IN (SELECT town
               FROM uk_price_paid
               WHERE uk_price_paid.town != 'GATWICK'
                 AND uk_price_paid.town == 'LONDON'
               GROUP BY town
               ORDER BY avg(price) DESC
               LIMIT 10)
GROUP BY time, town
ORDER BY time settings additional_table_filters = {'uk_price_paid' : 'town = \'LONDON\' AND district = \'HACKNEY\' '}
</code>
</pre>

<a href="/uploads/filtered_camden_7919d081a8.png" target="_blank">
         <img alt="filtered_camden.png" src="/uploads/filtered_camden_7919d081a8.png">
</a>

For the correct result, ClickHouse needs to ensure the filter is injected into the top level WHERE clause.

While added in response to a Grafana requirement, this feature is available for wider tooling to exploit and improve their offerings. Please let us know if this proves useful!

## The need for HTTP

Under the hood, the Grafana plugin uses the [clickhouse-go](https://github.com/ClickHouse/clickhouse-go) client for sending queries to ClickHouse. Historically, this client communicated over the ClickHouse binary protocol using the native format. This represents the most efficient means of communication and was selected for performance reasons. This makes sense for INSERT heavy use cases but less so for the aggregation queries commonly used in Grafana. Our users often require traffic to be transmitted over HTTP to allow switching on load balancers or to utilize proxy solutions such as [ch-proxy](https://www.chproxy.org/). 

Support for native format over HTTP has been added to the clickhouse-go driver thanks to a [community contribution](https://github.com/ClickHouse/clickhouse-go/issues/597). This capability is now exposed in Grafana and can be selected at a data source level. 

<a href="/uploads/config_datasource_2fa482a6bf.png" target="_blank">
         <img alt="config_datasource.png" src="/uploads/config_datasource_2fa482a6bf.png">
</a>

For those trying this feature, recall that HTTP uses a different port than Native - 8123/8443 for HTTP/HTTPS by default. Finally, we have separated the connection and query timeouts which previously used the same value.

## Welcome semi-structured data

ClickHouse 22.6 added[ support for JSON](https://clickhouse.com/blog/getting-data-into-clickhouse-part-2-json) as a data type. The JSON Object type is advantageous when dealing with complex nested structures, which are subject to change. The type automatically infers the columns from the structure during insertion and merges these into the existing table schema. Columns will be created as required, allowing the user to handle semi-structured data without maintaining a schema. This capability has many uses, not least simplifying the use of ClickHouse as a log storage engine.

Shortly after its addition to ClickHouse, support for JSON was added to the clickhouse-go client. This support has now been implemented in our Grafana plugin in v2.0.

JSON leaf nodes can now be used like any other column of the equivalent primitive type for charting. Columns that represent a JSON object or list of JSON objects are handled like the Tuple and Nested types in ClickHouse, respectively. In Grafana, this means rendering them as JSON strings. While this is not compatible with Grafana charting, JSON objects can be displayed in the [Explore view](https://grafana.com/docs/grafana/latest/explore/logs-integration/#logs-visualization) or [Logs Panel](https://grafana.com/docs/grafana/latest/visualizations/logs-panel/) - a useful addition for those storing structured logs in ClickHouse.

For testing this feature, users can use a subset of the logs dataset described [here](https://clickhouse.com/docs/en/guides/developer/working-with-json/json-other-approaches). Here we use a simple schema:


<pre>
  <code type='click-ui' language='sql'>
SET allow_experimental_object_type=1;

CREATE TABLE http_logs
(
    `message` JSON,
    `timestamp` DateTime
)
ENGINE = MergeTree()
ORDER BY timestamp;

INSERT INTO http_logs (timestamp, message) SELECT
    `@timestamp` AS timestamp,
    concat('{"status":', toString(status), ', "size":', toString(size), ', "clientip": "', toString(clientip), '", "request": ', toJSONString(request), '}') AS message
FROM s3('https://datasets-documentation.s3.eu-west-3.amazonaws.com/http/documents-01.ndjson.gz', 'JSONEachRow')
</code>
</pre>

We insert the data above from a publically available s3 bucket - feel free to experiment or alternatively use [sql.clickhouse.com](https://sql.clickhouse.com)! Note we ensure we have a time column `timestamp` separate from the JSON. Each row looks like the following due to moving all columns under the message field.

```
{"message":{"clientip":"40.135.0.0","request":{"method":"GET","path":"\/images\/hm_bg.jpg","version":"HTTP\/1.0"},"size":24736,"status":200},"timestamp":"1998-04-30 19:30:17"}
```

These JSON logs can now be rendered in the Explore view, or Logs Panel. We infer a “level” field from the response status, which controls the color rendering. We recommend imposing a LIMIT on all queries to avoid timeouts since Grafana requires the complete result set to be converted to frames. 

Histogram rendering for the Explore view is based on the returned results, although we plan for later versions to compute a full range log distribution [similar to Loki and Elasticsearch](https://grafana.com/docs/grafana/latest/explore/logs-integration/#logs-visualization). To ensure users aren’t required to adjust the time frame in Grafana, we shift this dataset to the current timeframe using the dataset’s max date.


<pre>
  <code type='click-ui' language='sql' play_link="https://sql.clickhouse.com?query_id=24AZ83BWSK7DYB24TDJHZD" runnable="true">
SELECT
    now() - (toDateTime('1998-05-08 13:44:46') - timestamp) AS log_time,
    multiIf(message.status > 500, 'critical', message.status > 400, 'error', message.status > 300, 'warning', 'info') AS level,
    message.request.method AS method,
    message.status AS status,
    message.size AS size,
    message.request AS log
FROM logs.http_logs
ORDER BY timestamp DESC
LIMIT 10000
</code>
</pre>

<a href="/uploads/explore_d50f59fbad.png" target="_blank">
         <img alt="explore.png" src="/uploads/explore_d50f59fbad.png">
</a>

Both the Logs Panel and Explore view are sensitive to field names. For results to be shown using the log visualization mode of Explore (including the histogram), rows must contain and be ordered by a “log_time” field.

JSON support required a rewrite of how we handle ClickHouse types within the plugin. Coverage should now be comprehensive with all types supported, including complex types such as Tuple and Nested that we needed to support as part of the JSON effort.

## Changes in Variables

Historically, we relied on the AST to automatically optimize IN conditions in WHERE clauses for the case where users selected “All” for a variable. The plugin would effectively remove the use of the variable from any WHERE clauses, thus avoiding the need to send the condition. While a nice feature, this relied on the AST and assumed a full understanding of the ClickHouse SQL dialect. In version 2.0, we defer this optimization to the user who should wrap IN clauses, which use a variable, with the macro __conditionalAll.  

For example, suppose we are visualizing house prices for London and wish to allow filtering by a user selected district i.e, via `district IN (${district:singlequote})`:

<a href="/uploads/district_3281661460.png" target="_blank">
         <img alt="district.png" src="/uploads/district_3281661460.png">
</a>

Our variable filter would look like this - note the ability to select an “All” option:

<a href="/uploads/filter_district_b9843fd471.png" target="_blank">
         <img alt="filter_district.png" src="/uploads/filter_district_b9843fd471.png">
</a>

If All is selected, the query becomes:

<pre>
  <code type='click-ui' language='sql' play_link="https://sql.clickhouse.com?query_id=F2EBMWNXBFRG722XG2MGGV" runnable="true">
SELECT
    toStartOfYear(date) AS time,
    district,
    round(avg(price)) AS price
FROM uk.uk_price_paid
WHERE (district IN (
    SELECT district
    FROM uk.uk_price_paid
    WHERE town = 'LONDON'
    GROUP BY district
    ORDER BY avg(price) DESC
    LIMIT 10
)) AND (district IN ('TOWER HAMLETS', 'HACKNEY', 'NEWHAM', 'CITY OF LONDON', 'WALTHAM FOREST', 'REDBRIDGE', 'BARKING AND DAGENHAM', 'HAVERING', 'HARINGEY', 'EPPING FOREST', 'ISLINGTON', 'CAMDEN', 'CITY OF WESTMINSTER', 'BARNET', 'HARROW', 'HILLINGDON', 'ENFIELD', 'EALING', 'HOUNSLOW', 'HAMMERSMITH AND FULHAM', 'LEWISHAM', 'BRENT', 'WANDSWORTH', 'SOUTHWARK', 'LAMBETH', 'GREENWICH', 'KENSINGTON AND CHELSEA', 'MERTON', 'BROMLEY', 'RICHMOND UPON THAMES', 'CROYDON', 'BEXLEY', 'KINGSTON UPON THAMES', 'HARLOW', 'SUTTON', 'CITY OF BRISTOL', 'MALVERN HILLS', 'THURROCK', 'RHONDDA CYNON TAFF'))
GROUP BY
    time,
    district
ORDER BY time ASC
</code>
</pre>

Whilst fine for variables with only a few values, such as districts in London, it becomes a performance overhead for longer lists. To optimize, the user can surround the clause with an `__conditionalAll` e.g.

<pre>
  <code type='click-ui' language='sql'>
SELECT toStartOfYear(date) AS time,
       town,
       round(avg(price))   AS price
FROM uk_price_paid
WHERE town IN (
    SELECT town
    FROM uk_price_paid
    WHERE town != 'GATWICK' AND $__conditionalAll(district IN (${district:singlequote}), $district)
    GROUP BY town
    ORDER BY avg(price) DESC
    LIMIT 10
)
GROUP BY time, town
ORDER BY time ASC
</code>
</pre>


On selecting “All” the district restriction is simply replaced with a `1=1` condition.

<pre>
  <code type='click-ui' language='sql' play_link="https://sql.clickhouse.com?query_id=8VHKVFS4NZFQGTZNKOWTH1" runnable="true">
SELECT
    toStartOfYear(date) AS time,
    district,
    round(avg(price)) AS price
FROM uk.uk_price_paid
WHERE (district IN (
    SELECT district
    FROM uk.uk_price_paid
    WHERE uk_price_paid.town = 'LONDON'
    GROUP BY district
    ORDER BY avg(price) DESC
    LIMIT 10
)) AND (1 = 1)
GROUP BY
    time,
    district
ORDER BY time ASC
</code>
</pre>

## Be aware of changes

As well as the large additions described above, we’ve fixed [several bugs](https://github.com/grafana/clickhouse-datasource/issues?q=is%3Aissue+label%3Abug+is%3Aclosed) with this release. The removal of the AST specifically means this release does have some breaking changes, beyond the need to manually optimize IN filters, that users should be aware of:

* The new Adhoc filter implementation relies on the `additional_table_filters` feature and thus ClickHouse 22.7. Older versions of ClickHouse will not populate filters. Do not upgrade your plugin if you cannot move to a version of ClickHouse greater or equal to this release.
* `additional_table_filters` are passed in SETTINGS with the query itself. This is not permitted for read-only users unless [readonly=2](https://clickhouse.com/docs/en/operations/settings/permissions-for-queries/#settings_readonly). This is not ideal, and we would not recommend setting this for public instances of ClickHouse. We recognize improvement is required here. [Stay tuned](https://github.com/ClickHouse/ClickHouse/issues/40244).

For the reasons above, Adhoc filters will not work against sql.clickhouse.com.

For users wanting to contribute or follow the latest issues and improvements, the official ClickHouse plugin is an [open-source project](https://github.com/grafana/clickhouse-datasource) hosted on GitHub and implemented in TypeScript and Go. We always value your feedback and encourage users to raise issues so we can continue to improve the plugin.

