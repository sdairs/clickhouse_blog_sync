---
title: "ClickHouse Cloud: Fast, Updatable Lookups with the Join Table Engine"
date: "2026-05-12T15:55:17.028Z"
author: "Hellmar Becker"
category: "Engineering"
excerpt: "Learn how ClickHouse Cloud's Join table engine enables fast, updatable in-memory lookups for dimensional modeling — with automatic upserts, deduplication, and data compaction powered by ReplacingMergeTree under the hood."
---

# ClickHouse Cloud: Fast, Updatable Lookups with the Join Table Engine

## Dictionaries in ClickHouse {#dictionaries-in-clickhouse}

When you move data from your transactional or event-based data sources to an analytical database like ClickHouse, you will likely consider modeling a dimensional schema according to the [Kimball methodology](https://en.wikipedia.org/wiki/Dimensional_modeling).

> [Dimensional modeling](https://en.wikipedia.org/wiki/Dimensional_modeling) always uses the concepts of facts (measures), and dimensions (context). Facts are typically (but not always) numeric values that can be aggregated, and dimensions are groups of hierarchies and descriptors that define the facts.

It follows that fact tables are typically immutable, and data are appended to them; whereas dimension tables are smaller, and subject to (infrequent) updates ([slowly changing dimensions](https://en.wikipedia.org/wiki/Slowly_changing_dimension)). When you run an analytical query, you have to join those dimensions against the fact table.

One common approach to do this in ClickHouse is to have a copy of the dimension data in memory in a [Dictionary](https://clickhouse.com/docs/engines/table-engines/special/dictionary). This approach enables [Direct Joins](https://clickhouse.com/blog/clickhouse-fully-supports-joins-direct-join-part4#direct-join) and is [recommended for optimizing join performance](https://clickhouse.com/blog/postgres-to-clickhouse-data-modeling-tips-v2#optimizing-joins).

A Dictionary is set up by specifying, among others, the `SOURCE` and `LIFETIME` attributes. ClickHouse pulls fresh data from the source and uses `LIFETIME` to determine how often it should refresh the Dictionary. But some customers asked me: Isn't there a way to update a Dictionary like a regular table? And indeed, there is a way to achieve this, using another special table engine.

## The `Join` table engine {#the-join-table-engine}

The [`Join` table engine](https://clickhouse.com/docs/engines/table-engines/special/join) is just what we need here. It is an in-memory structure, laying out data for a *specific* type of join that has to be stated in the table definition, and it is backed by a persistence layer. Setting up the `Join` table, you need to configure

- *join strictness*
- *join type*
- the *key column(s)* you want to use in the join.

### Join strictness {#join-strictness}

This can be `ANY` or `ALL`. With `ALL`, all matching rows are taken from the `Join` table; `ANY` takes only the latest one.

This means with `ANY` type *an **`INSERT`** becomes an **`UPSERT`** by key:* you update a dimension row by inserting another row with the same key.

### Join Type {#join-type}

One of ClickHouse's [join types](https://clickhouse.com/docs/sql-reference/statements/select/join#supported-types-of-join), like `INNER` or `LEFT` or `RIGHT`. For dimensional modeling, you will mostly use `LEFT`.

## Querying a `Join` table {#querying-a-join-table}

While a `Join` table can be queried like any regular table using `SELECT`, there are two more ways of using it:

1. If you place the `Join` table in a `JOIN` query where the join parameters match the ones in the definition of the table, ClickHouse will automatically know to use the Direct Join algorithm.
2. You can look up values for a given key using `joinGet`. This works just like `dictGet` for Dictionaries.

## Drawbacks in the open source implementation {#drawbacks-in-the-open-source-implementation}

So a `Join` table with `ANY LEFT` join condition would be just the thing to implement a [Type 1 slowly changing dimension](https://en.wikipedia.org/wiki/Slowly_changing_dimension#Type_1:_overwrite), right? You can update values for a given key and have a high performing join. Why don't we use it all the time, then?

It turns out that the implementation of the `Join` table engine in open source ClickHouse has a couple of drawbacks that make it less suitable for this use case:

1. **`Join` tables are not distributed**; each cluster node would have to maintain its own copy/version of the table.
2. **The persistence layer is not built for frequent inserts/updates**. The Join table engine persists data as compressed Native-format .bin files in the table's data directory on disk (one file per INSERT batch). On server startup, these files are read back sequentially and the in-memory HashJoin hash table is reconstructed from them. This means each update will create a new numbered .bin file. There is no background compaction process — files are never merged automatically. Over time, this leads to performance degradation.

## Implementation in ClickHouse Cloud {#implementation-in-clickhouse-cloud}

**These issues have been solved very elegantly in ClickHouse Cloud.** In ClickHouse Cloud, a `Join` table is actually transparently implemented as a `SharedJoin` table with a MergeTree family backing table:

- for `ALL` join, this is a `MergeTree` table
- for `ANY` join, a `ReplacingMergeTree` table.

You can find these tables in `system.tables`. The naming convention for the underlying table is `.inner_id.SharedJoin.<uuid of Join table>`.

> **Note:** there is a setting [`join_any_take_last_row`](https://clickhouse.com/docs/operations/settings/settings#join_any_take_last_row) that is **not** honored

The in-memory table is populated from the persistent (underlying) table using a query (which includes `FINAL` in the case of `ANY` join) on insert to Join table (with filter to select only newest data) and on table load on startup.

## Example: Data Enrichment {#example-data-enrichment}

Probably the most meaningful use case is enrichment / dimensional modeling with an `ANY LEFT` join. To illustrate this specific case, let's take the example from the ClickHouse [docs](https://clickhouse.com/docs/engines/table-engines/special/join#example) and modify it a bit:

<pre><code type='click-ui' language='sql'>
-- Create the fact table and insert some data
CREATE OR REPLACE TABLE id_val (
    `id` UInt32,
    `val` UInt32
) ENGINE = MergeTree
ORDER BY (id);

INSERT INTO id_val VALUES
    (1, 11), (2, 12), (3, 13);

-- Creating the right-side Join table:
CREATE OR REPLACE TABLE id_val_join (
    `id` UInt32,
    `val` UInt8
) ENGINE = Join(ANY, LEFT, id);

-- Insert some values
INSERT INTO id_val_join VALUES
    (1, 21), (1, 22), (3, 23);

-- Enrichment query
SELECT *
FROM id_val
ANY LEFT JOIN id_val_join USING (id);
</code></pre>

```shell
   ┌─id─┬─val─┬─id_val_join.val─┐
1. │  1 │  11 │              22 │
2. │  2 │  12 │               0 │
3. │  3 │  13 │              23 │
   └────┴─────┴─────────────────┘
```

Now, let's find out what happens in the `Join` table and in the underlying table when we upsert an entry for key `1`.

<pre><code type='click-ui' language='sql'>
-- And another insert
INSERT INTO id_val_join VALUES (1,42);
</code></pre>

Look up the underlying table:

<pre><code type='click-ui' language='sql'>
SELECT database, name, uuid, engine
FROM system.tables
WHERE name = 'id_val_join'
FORMAT Vertical;
</code></pre>

```shell
database:                         default
name:                             id_val_join
uuid:                             64f169ee-977d-46c2-b067-580fdf8c1d4b
engine:                           SharedJoin
```

The `Join` table deduplicates and keeps the latest entry only:

<pre><code type='click-ui' language='sql'>
SELECT * FROM id_val_join;
</code></pre>

```shell
   ┌─id─┬─val─┐
1. │  3 │  23 │
2. │  1 │  42 │
   └────┴─────┘
```

Constructing the underlying `ReplacingMergeTree` table from the UUID, we see this one retains the duplicates until they are merged out:

<pre><code type='click-ui' language='sql'>
SELECT * FROM default.`.inner_id.SharedJoin.64f169ee-977d-46c2-b067-580fdf8c1d4b`;
</code></pre>

```shell
   ┌─id─┬─val─┐
1. │  1 │  22 │
2. │  3 │  23 │
3. │  1 │  42 │
   └────┴─────┘
```

Finally, running the enrichment query again, we see how the updated dimension entry reflects in the result:

<pre><code type='click-ui' language='sql'>
SELECT *
FROM id_val
ANY LEFT JOIN id_val_join USING (id);
</code></pre>

```shell
   ┌─id─┬─val─┬─id_val_join.val─┐
1. │  1 │  11 │              42 │
2. │  2 │  12 │               0 │
3. │  3 │  13 │              23 │
   └────┴─────┴─────────────────┘
```

Every time you insert a new row or a set of rows:

- The data is inserted into the underlying `ReplacingMergeTree` table.
- The in-memory representation is updated on insert to the Join table (with a filter on block ID to select only newest data) and on table load on startup.
- This query also applies `FINAL`, so the in-memory `Join` table will never have duplicates.
- The `join_any_take_last_row` is ignored. You always get the latest entry.

## Conclusion {#conclusion}

- The `Join` table engine in ClickHouse provides a precomputed hash map that can be used to speed up JOINs.
- Like a dictionary, a `Join` table is kept in memory. But it is backed by a persistence layer (saved in files).
- In ClickHouse Cloud, `Join` tables are automatically clustered and backed by full `MergeTree` tables, making them suitable for frequent updates.
- In particular, for dimensional modeling in ClickHouse Cloud, use `Join(ANY, LEFT, id)` — upserting, deduplication, and data compaction is automatically handled by the underlying `ReplacingMergeTree`!


---

## Get started today

Interested in seeing how ClickHouse works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-560-get-started-today-sign-up&utm_blogctaid=560)

---