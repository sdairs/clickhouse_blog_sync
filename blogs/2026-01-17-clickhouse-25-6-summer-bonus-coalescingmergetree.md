---
title: "ClickHouse 25.6 summer bonus: CoalescingMergeTree table engine"
date: "2025-07-14T07:27:24.328Z"
author: "ClickHouse Team"
category: "Engineering"
excerpt: "CoalescingMergeTree is a new table engine in ClickHouse 25.6 that consolidates sparse, append-only updates on disk. Ideal for IoT, ETL, and enrichment pipelines where data arrives in fragments over time."
---

# ClickHouse 25.6 summer bonus: CoalescingMergeTree table engine

<p>Our <a href="https://clickhouse.com/blog/clickhouse-release-25-06">ClickHouse 25.6 release post</a> was already packed, but it turns out we left one very cool new feature in the cooler. &#128526;</p>

So here’s your **summer bonus blog**, just in time for your beach read: a dedicated spotlight on CoalescingMergeTree, a brand new table engine designed to consolidate sparse updates and reduce your row count without sacrificing fidelity.

<p>If you’re the type to check ClickHouse updates between sunscreen applications, this one’s for you. &#127965;&#65039;</p>

Let’s dive in.


## CoalescingMergeTree table engine


### Contributed by Konstantin Vedernikov

It’s not every day the [MergeTree table engine family](https://clickhouse.com/docs/engines/table-engines/mergetree-family) gets a new member, so when it does, it’s worth celebrating with a dedicated post.

The newest addition, [CoalescingMergeTree](https://clickhouse.com/docs/engines/table-engines/mergetree-family/coalescingmergetree), gradually consolidates sparse records over time and is especially useful when:


* You want to efficiently retain only the most complete version of each entity.
* You’re okay with eventual (on-disk) consolidation during merges.
* You want to avoid full row overwrites (e.g. via ReplacingMergeTree) and just fill in missing values.

A great example: **IoT device state or configuration snapshots**. (Think: observability for a car fleet, e.g., [Tesla](/blog/how-tesla-built-quadrillion-scale-observability-platform-on-clickhouse))

In modern connected vehicles like electric cars, telemetry updates are fragmented across subsystems:


* The battery reports its charge
* The GPS module sends location
* The software updater reports firmware
* Sensors periodically update temperature and speed

We want to combine these incremental, sparse updates into a complete per-vehicle view using CoalescingMergeTree.



### Table Definition

<pre><code type='click-ui' language='sql' show_line_numbers='false'>
CREATE TABLE electric_vehicle_state
(
    vin String, -- vehicle identification number
    last_update DateTime64 Materialized now64(), -- optional (used with argMax)
    battery_level Nullable(UInt8), -- in %
    lat Nullable(Float64), -- latitude (°)
    lon Nullable(Float64), -- longitude (°)
    firmware_version Nullable(String),
    cabin_temperature Nullable(Float32), -- in °C
    speed_kmh Nullable(Float32) -- from sensor
)
ENGINE = CoalescingMergeTree
ORDER BY vin;
</code></pre>

### Example Inserts

<pre><code type='click-ui' language='sql' show_line_numbers='false'>
-- ① Initial battery and firmware readings
INSERT INTO electric_vehicle_state VALUES
('5YJ3E1EA7KF000001', 82, NULL, NULL, '2024.14.5', NULL, NULL);

-- ② GPS reports in later
INSERT INTO electric_vehicle_state VALUES
('5YJ3E1EA7KF000001', NULL, 37.7749, -122.4194, NULL, NULL, NULL);

-- ③ Sensor update: temperature + speed
INSERT INTO electric_vehicle_state VALUES
('5YJ3E1EA7KF000001', NULL, NULL, NULL, NULL, 22.5, 67.3);

-- ④ Battery drops to 78%
INSERT INTO electric_vehicle_state VALUES
('5YJ3E1EA7KF000001', 78, NULL, NULL, NULL, NULL, NULL);

-- ⑤ Another car, initial firmware and temp readings
INSERT INTO electric_vehicle_state VALUES
('5YJ3E1EA7KF000099', NULL, NULL, NULL, '2024.14.5', 19.2, NULL);
</code></pre>

### Why not just use UPDATE?

In many databases, handling state changes like these would involve updating the existing row, for example, issuing an UPDATE to set the latest temperature or firmware version. ClickHouse itself **does** support fast and frequent single-row UPDATEs, [watch](https://youtu.be/UN0RM56uiFI?si=9TgYbUZWYe1ZzTTm) our update (ha!) on that at the recent [Open House 2025 user conference](https://clickhouse.com/openhouse), and for some workloads, they’re perfectly viable.  

But in high-throughput IoT scenarios, that pattern can be inefficient: an UPDATE requires locating the row with the previous state, rewriting it, and often locking or rewriting more data than necessary. 

ClickHouse encourages a simpler, append-only model: just insert the new fields as they arrive. CoalescingMergeTree takes that one step further by letting the engine coalesce those sparse inserts into a complete, compact record automatically, during background merges (we will dive into that below). It’s a better fit for high-ingest, high-cardinality use cases where updates are frequent but partial.

> ClickHouse is especially optimized for insert workloads: [inserts are fully isolated](https://clickhouse.com/docs/concepts/why-clickhouse-is-so-fast#storage-layer-concurrent-inserts-are-isolated-from-each-other), run in parallel without interfering with each other, and hit disk at full speed, because there are no global structures to lock or update (e.g., a global B++ index). Inserts are kept lightweight by [deferring additional work](https://clickhouse.com/docs/concepts/why-clickhouse-is-so-fast#storage-layer-merge-time-computation)—such as record consolidation—to background merges.<br/><br/>This architecture supports extremely high-throughput ingestion; in one production deployment, ClickHouse sustained [over 1 billion rows per second](/blog/how-tesla-built-quadrillion-scale-observability-platform-on-clickhouse#proving-the-system-at-scale) with stable memory and CPU usage.

### The catch: trillions of rows

In high-volume IoT setups, data arrives constantly from thousands (or millions) of devices. Each update often modifies only one or two fields, leading to massive tables full of sparse, redundant rows.

To reconstruct the latest full state per device, you need to pull the most recent non-null value for each column. ClickHouse already supports this using the [argMax()](https://clickhouse.com/docs/sql-reference/aggregate-functions/reference/argmax) aggregate function, **even if the table uses a regular MergeTree engine**. 

Here’s the current content of the `electric_vehicle_state` table after a few sparse updates (assuming no part merges have occurred yet, we’ll explain this further below). `last_update` timestamps are shortened for brevity:

<pre><code type='click-ui' language='sql' show_line_numbers='false'>
SELECT
    vin,
    right(toString(last_update), 12) AS last_update,
    battery_level AS batt,
    lat,
    lon,
    firmware_version AS fw,
    cabin_temperature AS temp,
    speed_kmh AS speed
FROM electric_vehicle_state
ORDER BY vin ASC;
</code></pre>

<pre><code type='click-ui' language='text' show_line_numbers='false'>
┌─vin───────────────┬─last_update──┬─batt─┬─────lat─┬───────lon─┬─fw────────┬─temp─┬─speed─┐
│ 5YJ3E1EA7KF000001 │ 10:41:37.731 │   82 │    ᴺᵁᴸᴸ │      ᴺᵁᴸᴸ │ 2024.14.5 │ ᴺᵁᴸᴸ │  ᴺᵁᴸᴸ │
│ 5YJ3E1EA7KF000001 │ 10:41:37.734 │ ᴺᵁᴸᴸ │ 37.7749 │ -122.4194 │ ᴺᵁᴸᴸ      │ ᴺᵁᴸᴸ │  ᴺᵁᴸᴸ │
│ 5YJ3E1EA7KF000001 │ 10:41:37.737 │ ᴺᵁᴸᴸ │    ᴺᵁᴸᴸ │      ᴺᵁᴸᴸ │ ᴺᵁᴸᴸ      │ 22.5 │  67.3 │
│ 5YJ3E1EA7KF000001 │ 10:41:37.739 │   78 │    ᴺᵁᴸᴸ │      ᴺᵁᴸᴸ │ ᴺᵁᴸᴸ      │ ᴺᵁᴸᴸ │  ᴺᵁᴸᴸ │
│ 5YJ3E1EA7KF000099 │ 10:41:37.742 │ ᴺᵁᴸᴸ │    ᴺᵁᴸᴸ │      ᴺᵁᴸᴸ │ 2024.14.5 │ 19.2 │  ᴺᵁᴸᴸ │
└───────────────────┴──────────────┴──────┴─────────┴───────────┴───────────┴──────┴───────┘
</code></pre>


And here’s how you’d query the **latest state per device** using argMax():

<pre><code type='click-ui' language='sql' show_line_numbers='false'>
SELECT
    vin,
    argMax(battery_level, last_update) AS batt,
    argMax(lat, last_update) AS lat,
    argMax(lon, last_update) AS lon,
    argMax(firmware_version, last_update) AS fw,
    argMax(cabin_temperature, last_update) AS temp,
    argMax(speed_kmh, last_update) AS speed
FROM electric_vehicle_state
GROUP BY vin
ORDER BY vin;
</code></pre>


<pre><code type='click-ui' language='text' show_line_numbers='false'>
┌─vin───────────────┬─batt─┬─────lat─┬───────lon─┬─fw────────┬─temp─┬─speed─┐
│ 5YJ3E1EA7KF000001 │   78 │ 37.7749 │ -122.4194 │ 2024.14.5 │ 22.5 │  67.3 │
│ 5YJ3E1EA7KF000099 │ ᴺᵁᴸᴸ │    ᴺᵁᴸᴸ │      ᴺᵁᴸᴸ │ 2024.14.5 │ 19.2 │  ᴺᵁᴸᴸ │
└───────────────────┴──────┴─────────┴───────────┴───────────┴──────┴───────┘
</code></pre>

> **argMax works well here because it keeps only the latest non-null value per column.**<br/>Specifically, `argMax(x, t)` returns the value of `x` from the row with the largest `t` (e.g., latest timestamp `t`) **where x is not null**. If rows with even larger `t` values (e.g., newer rows) exist but x is null in those, they are skipped.

However, relying purely on regular MergeTree and argMax() means:

* All rows must be scanned
* Aggregation must be computed on the fly, every time

This becomes inefficient at scale, especially when the table grows to billions or trillions of rows.


### Why CoalescingMergeTree helps

With CoalescingMergeTree, ClickHouse physically consolidates rows that share the same sorting key (e.g. VIN). During [background part merges](https://clickhouse.com/docs/merges), it keeps only the latest non-null value per column, effectively pre-aggregating the state **on disk**:

![Blog-release-25.6.001.png](https://clickhouse.com/uploads/Blog_release_25_6_001_8a3ebc6e3b.png)

The diagram above shows how sparse updates from different subsystems (battery, GPS, sensors) are gradually merged into a single consolidated state by CoalescingMergeTree. Each update only modifies a subset of columns, and ClickHouse automatically combines rows that share the same sorting key (`vin` in this example) during background merges to form the latest complete state per vehicle.

We visualized seven [data parts](https://clickhouse.com/docs/parts): the original inserts (①–④), intermediate merged parts (⑤, ⑥), and the final active part ⑦. After merging, parts ①–⑥ become inactive and are automatically removed. All queries now run efficiently over the single, compact part ⑦.

> Note: **“Latest”** here is not determined by a row's timestamp column, but by the **insertion order** of rows. During merges, `CoalescingMergeTree` uses the **physical on-disk order** of rows from the parts being merged. For each column, it keeps the latest non-null value for a given sorting key, where “latest” means the value from the last (i.e., newest) applicable row in the **most recently written part** among the parts being merged.<br/><br/>For example, in the diagram above, parts ①–⑦ are shown in write order, with ① being the earliest and ⑦ the latest.

This drastically reduces:

* The number of rows per device
* The amount of data scanned during queries

###  Reading the latest state: argMax or FINAL

In high-ingest scenarios like IoT, **background merges are perpetually behind** (i.e., merges run continuously, but inserts outpace them, think of it as a lagging consolidation window).

**To maintain accuracy despite that**, we still use `GROUP BY` and `argMax()`, but now over far fewer rows, since background merges have already handled most of the consolidation.

> (In the diagram above, we skipped the `last_update` column for clarity. It plays no role in CoalescingMergeTree’s merge logic. Like all other columns, its latest non-null value is retained automatically during merges. However, if you’re using `argMax()`, a timestamp like `last_update` is required to determine which row is considered “latest” at query time.)

<pre><code type='click-ui' language='sql' show_line_numbers='false'>
SELECT
    vin,
    argMax(battery_level, last_update) AS batt,
    argMax(lat, last_update) AS lat,
    argMax(lon, last_update) AS lon,
    argMax(firmware_version, last_update) AS fw,
    argMax(cabin_temperature, last_update) AS temp,
    argMax(speed_kmh, last_update) AS speed
FROM electric_vehicle_state
GROUP BY vin
ORDER BY vin;
</code></pre>

<pre><code type='click-ui' language='text' show_line_numbers='false'>
┌─vin───────────────┬─batt─┬─────lat─┬───────lon─┬─fw────────┬─temp─┬─speed─┐
│ 5YJ3E1EA7KF000001 │   78 │ 37.7749 │ -122.4194 │ 2024.14.5 │ 22.5 │  67.3 │
│ 5YJ3E1EA7KF000099 │ ᴺᵁᴸᴸ │    ᴺᵁᴸᴸ │      ᴺᵁᴸᴸ │ 2024.14.5 │ 19.2 │  ᴺᵁᴸᴸ │
└───────────────────┴──────┴─────────┴───────────┴───────────┴──────┴───────┘
</code></pre>

Just for completeness: if all parts have been fully merged and no new rows are being inserted, a simple `SELECT *` without `GROUP BY` is sufficient:

<pre><code type='click-ui' language='sql' show_line_numbers='false'>
OPTIMIZE TABLE electric_vehicle_state FINAL; -- force merge all parts into a single part

SELECT -- select from the fully consolidated, merged part
    vin,
    battery_level AS batt,
    lat AS lat,
    lon AS lon,
    firmware_version AS fw,
    cabin_temperature AS temp,
    speed_kmh AS speed
FROM electric_vehicle_state
ORDER BY vin;
</code></pre>

<pre><code type='click-ui' language='text' show_line_numbers='false'>
┌─vin───────────────┬─batt─┬─────lat─┬───────lon─┬─fw────────┬─temp─┬─speed─┐
│ 5YJ3E1EA7KF000001 │   78 │ 37.7749 │ -122.4194 │ 2024.14.5 │ 22.5 │  67.3 │
│ 5YJ3E1EA7KF000099 │ ᴺᵁᴸᴸ │    ᴺᵁᴸᴸ │      ᴺᵁᴸᴸ │ 2024.14.5 │ 19.2 │  ᴺᵁᴸᴸ │
└───────────────────┴──────┴─────────┴───────────┴───────────┴──────┴───────┘
</code></pre>


**Alternatively, in scenarios with a constant stream of updates**, you can avoid aggregating at query time by applying CoalescingMergeTree's coalescing logic (described above with the diagram) **ephemerally** using the `FINAL` modifier. This doesn’t finalize merges on disk—it performs an in-memory merge of all relevant parts as they existed when the query began, producing fully consolidated rows without needing `GROUP BY` or `argMax()`:

<pre><code type='click-ui' language='sql' show_line_numbers='false'>
SELECT
    vin,
    battery_level AS batt,
    lat AS lat,
    lon AS lon,
    firmware_version AS fw,
    cabin_temperature AS temp,
    speed_kmh AS speed
FROM electric_vehicle_state FINAL
ORDER BY vin;
</code></pre>

<pre><code type='click-ui' language='text' show_line_numbers='false'>
┌─vin───────────────┬─batt─┬─────lat─┬───────lon─┬─fw────────┬─temp─┬─speed─┐
│ 5YJ3E1EA7KF000001 │   78 │ 37.7749 │ -122.4194 │ 2024.14.5 │ 22.5 │  67.3 │
│ 5YJ3E1EA7KF000099 │ ᴺᵁᴸᴸ │    ᴺᵁᴸᴸ │      ᴺᵁᴸᴸ │ 2024.14.5 │ 19.2 │  ᴺᵁᴸᴸ │
└───────────────────┴──────┴─────────┴───────────┴───────────┴──────┴───────┘
</code></pre>

> Note: With the `FINAL` modifier in the query, the table’s `last_update` field becomes optional because `FINAL` applies CoalescingMergeTree’s **own merge logic** at query time. That logic determines recency based on the **insertion order** of rows, not a timestamp column.<br/><br/>However, if you query without `FINAL` and rely on `argMax()` instead, a timestamp like `last_update` is still needed to correctly identify the latest non-null values at query time when parts haven’t fully merged—because at that point, the query engine doesn’t have direct access to the write timestamps of data parts or physical row numbers to reliably infer insertion order.



### Recommended storage pattern: raw + coalesced tables

We recommend using CoalescingMergeTree together with a regular MergeTree table (typically via a [materialized view](https://clickhouse.com/docs/materialized-views)):



* Use the MergeTree table to store the raw event stream, keeping the full history of all incoming updates from each vehicle or device. 

* Use a CoalescingMergeTree table to store a coalesced view, for example, the latest known state per vehicle, ideal for dashboards, periodic reports, or analytical queries.

This dual-table pattern ensures you retain all granular data while still benefiting from the efficiency of physical row consolidation. It also provides a safety net: if the sorting key doesn’t uniquely identify each event, your raw table still holds the complete record for recovery or reprocessing.

### More use cases

Beyond IoT snapshots, CoalescingMergeTree is helpful anywhere sparse, append-only updates gradually enrich a record. For example:



* **User profile enrichment** — fields like email, phone, or location get filled in as the user interacts. 

* **Security audit trails** — events slowly add context (e.g., actor identity, affected system). 

* **ETL pipelines with late-arriving dimensions** — enrichment steps populate missing fields. 

* **Patient health records** — lab results, doctor notes, and vitals arrive over time from different systems. 

* **Ad or campaign tracking** — impressions and clicks arrive from different systems at different times. 

* **Customer support cases** — tickets evolve as more info (severity, resolution notes) is gathered.

In all these cases, CoalescingMergeTree reduces storage costs and query latency without sacrificing completeness.


## **That’s it, back to your regularly scheduled summer**

Now that your ClickHouse knowledge is refreshed, it’s time to refresh yourself.

<p>We’ll be here when you get back. &#127958;&#65039;&#127865;</p>

Happy summer, and happy querying!


