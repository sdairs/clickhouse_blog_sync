---
title: "Postgres to ClickHouse: Data Modeling Tips V2"
date: "2025-03-05T17:08:43.111Z"
author: "Lionel Palacin & Sai Srirampur "
category: "Engineering"
excerpt: "Dive into how Postgres-to-ClickHouse replication works, and learn best practices for data deduplication, custom ordering keys, optimizing JOINs, denormalization, and more."
---

# Postgres to ClickHouse: Data Modeling Tips V2

<img preview="/uploads/large_Blog_Postgres_To_Clickhouse_Data_Modeling_Tips_V2_202502_V2_1_c6a099b47b.png"  src="/uploads/Blog_Postgres_To_Clickhouse_Data_Modeling_Tips_V2_202502_V2_1_c6a099b47b.png" alt="catalogue_lakehouse.png" class="h-auto w-auto max-w-full"  style="width: 100%;">

It is becoming increasingly [common](https://clickhouse.com/blog/clickhouse-welcomes-peerdb-adding-the-fastest-postgres-cdc-to-the-fastest-olap-database#the-two-sides-of-the-data-coin) for customers to use Postgres and ClickHouse together, with Postgres powering transactional workloads and ClickHouse powering analytics. Each is a purpose-built database optimized for its respective workload. A common approach to integrating Postgres with ClickHouse is Change Data Capture (CDC). CDC continuously tracks inserts, updates, and deletes in Postgres and replicates them to ClickHouse, enabling real-time analytics.

You can implement Postgres CDC to ClickHouse using [PeerDB](https://github.com/PeerDB-io/peerdb), an open-source replication tool, or leverage a fully integrated experience in ClickHouse Cloud with [ClickPipes](https://clickhouse.com/docs/integrations/clickpipes/postgres). **Since Postgres and ClickHouse are different databases, an important aspect alongside replication is effectively modeling tables and queries in ClickHouse to maximize performance.**

This blog takes a deep dive into how Postgres CDC to ClickHouse works internally and delves into best practices for data modeling and query tuning. **We will cover topics such as data deduplication strategies, handling custom ordering keys, optimizing JOINs, materialized views (MVs) including refreshable MVs, denormalization, and more.** You can also apply these learnings to one-time migrations (not CDC) from Postgres, so we expect this to help any Postgres users looking to use ClickHouse for analytics. We published a [v1](https://clickhouse.com/blog/postgres-to-clickhouse-data-modeling-tips) of this blog late last year; this one will be an advanced version of that blog.

#### Dataset

Throughout this blog post, we will illustrate the strategies using a real-world dataset, specifically a subset of the well-known StackOverflow dataset, which we will load into PostgreSQL. This dataset is used across ClickHouse documentation, and you can find more information about it [here](https://clickhouse.com/docs/en/getting-started/example-datasets/stackoverflow). We also implemented a Python script that simulates user activity on StackOverflow. Instructions on how to reproduce the experiments can be found on [GitHub](https://github.com/ClickHouse/examples/tree/main/postgresql-clickhouse-data-modeling).

## How does data get replicated? 

### PostgreSQL logical decoding

ClickPipes and PeerDB use [Postgres Logical Decoding](https://www.pgedge.com/blog/logical-replication-evolution-in-chronological-order-clustering-solution-built-around-logical-replication) to consume changes as they happen in Postgres. The Logical Decoding process in Postgres enables clients like ClickPipes to receive changes in a human-readable format, i.e., a series of INSERTs, UPDATEs, and DELETEs. To learn more about how Logical Decoding works, you can read one of our [blogs](https://www.pgedge.com/blog/logical-replication-evolution-in-chronological-order-clustering-solution-built-around-logical-replication) that goes into full detail.

As part of the replication process, ClickPipes automatically creates corresponding tables with the most [native data-type mapping](https://docs.peerdb.io/datatypes/datatype-matrix) in ClickHouse and performs initial snapshots/backfills super [efficiently](https://blog.peerdb.io/parallelized-initial-load-for-cdc-based-streaming-from-postgres#heading-parallelized-initial-snapshot-for-cdc-based-streaming).

### ReplacingMergeTree

ClickPipes maps Postgres tables to ClickHouse using the [ReplacingMergeTree](https://clickhouse.com/docs/engines/table-engines/mergetree-family/replacingmergetree) engine. ClickHouse performs best with append-only workloads and [does not recommend](https://clickhouse.com/docs/guides/developer/mutations) frequent UPDATEs. This is where ReplacingMergeTree is particularly powerful.

With ReplacingMergeTree, updates are modeled as inserts with a newer version (`_peerdb_version`) of the row, while deletes are inserts with a newer version and `_peerdb_is_deleted` marked as true. The ReplacingMergeTree engine in background deduplicates/merges data and retains the latest version of the row for a given primary key (id), enabling efficient handling of UPDATEs and DELETEs as versioned inserts.

Below is an example of a CREATE Table statement executed by ClickPipes to create the table in ClickHouse.

<pre><code type='click-ui' language='sql'>
CREATE TABLE users
(
    `id` Int32,
    `reputation` String,
    `creationdate` DateTime64(6),
    `displayname` String,
    `lastaccessdate` DateTime64(6),
    `aboutme` String,
    `views` Int32,
    `upvotes` Int32,
    `downvotes` Int32,
    `websiteurl` String,
    `location` String,
    `accountid` Int32,
    `_peerdb_synced_at` DateTime64(9) DEFAULT now64(),
    `_peerdb_is_deleted` Int8,
    `_peerdb_version` Int64
)
ENGINE = ReplacingMergeTree(_peerdb_version)
PRIMARY KEY id
ORDER BY id;
</code></pre>

### Illustrative example

The illustration below walks through a basic example of synchronization of a table `users` between PostgreSQL and ClickHouse using ClickPipes.

<img preview="/uploads/large_postgres_cdc_data_modelling_004_d06ef24091.png"  src="/uploads/postgres_cdc_data_modelling_004_d06ef24091.png" class="h-auto w-auto max-w-full"  style="width: 100%;">

**Step 1** shows the initial snapshot of the 2 rows in PostgreSQL and ClickPipes performing the initial load of those 2 rows to ClickHouse. If you observe, both rows are copied as-is to ClickHouse.

**Step 2** shows three operations on the users table: inserting a new row, updating an existing row, and deleting another row.

**Step 3** shows how ClickPipes replicates the INSERT, UPDATE, and DELETE operations to ClickHouse as versioned inserts. The UPDATE appears as a new version of the row with ID 2, while the DELETE appears as a new version of ID 1 with is _deleted marked as true. Because of this, ClickHouse has three additional rows compared to PostgreSQL.

As a result, running a simple query like `SELECT count(*) FROM users;` may produce different results in ClickHouse and PostgreSQL. According to the [ClickHouse merge documentation](https://clickhouse.com/docs/en/merges#replacing-merges), outdated row versions are eventually discarded during the merge process. However, the timing of this merge is unpredictable, meaning queries in ClickHouse may return inconsistent results until it occurs.

How can we ensure identical query results in both ClickHouse and PostgreSQL?

## Deduplication strategy

This section discusses various approaches to ensuring your queries in ClickHouse produce results consistent with PostgreSQL.

### Default approach: Use FINAL keyword

The recommended way to deduplicate data in ClickHouse queries is to use the [FINAL modifier.](https://clickhouse.com/docs/sql-reference/statements/select/from#final-modifier) This ensures only the deduplicated rows are returned, which is ideal for ClickHouse tables synced via Postgres CDC. Add FINAL to your query.

FINAL adds some overhead to your queries. However, ClickHouse remains fast. FINAL performance has been significantly improved over multiple releases ([#73132](https://github.com/ClickHouse/ClickHouse/pull/73132), [#73682](https://github.com/ClickHouse/ClickHouse/pull/73682), [#58120](https://github.com/ClickHouse/ClickHouse/pull/58120), [#47915](https://github.com/ClickHouse/ClickHouse/pull/47915)). 

Let's look at how to apply it to three different queries.

_Note in the following queries the WHERE clause to filter out deleted rows._

- **Simple count query**: Count the number of posts.

This is the simplest query you can run to check if the synchronization went fine. The two queries should return the same count.

<pre><code type='click-ui' language='sql'>
-- PostgreSQL 
SELECT count(*) FROM posts;

-- ClickHouse 
SELECT count(*) FROM posts FINAL where _peerdb_is_deleted=0;
</code></pre>

-  **Simple aggregation with JOIN**: Top 10 users who cumulate the most number of views.

An example of an aggregation on a single table. Having duplicates here would greatly affect the result of the sum function.

<pre><code type='click-ui' language='sql'>
-- PostgreSQL 
SELECT
    sum(p.viewcount) AS viewcount,
    p.owneruserid as user_id,
    u.displayname as display_name
FROM posts p
LEFT JOIN users u ON u.id = p.owneruserid
WHERE p.owneruserid > 0
GROUP BY user_id, display_name
ORDER BY viewcount DESC
LIMIT 10;

-- ClickHouse 
SELECT
    sum(p.viewcount) AS viewcount,
    p.owneruserid AS user_id,
    u.displayname AS display_name
FROM posts AS p
FINAL
LEFT JOIN users AS u
FINAL ON (u.id = p.owneruserid) AND (u._peerdb_is_deleted = 0)
WHERE (p.owneruserid > 0) AND (p._peerdb_is_deleted = 0)
GROUP BY
    user_id,
    display_name
ORDER BY viewcount DESC
LIMIT 10
</code></pre>

#### FINAL setting

Rather than adding the FINAL modifier to each table name in the query, you can use the [FINAL setting](https://clickhouse.com/docs/operations/settings/settings#final) to apply it automatically to all tables in the query.

This setting can be applied either per query or for an entire session.

<pre><code type='click-ui' language='sql'>
-- Per query FINAL setting
SELECT count(*) FROM posts SETTINGS final = 1;

-- Set FINAL for the session
SET final = 1;
SELECT count(*) FROM posts; 
</code></pre>

#### ROW policy

An easy way to hide the redundant `_peerdb_is_deleted = 0` filter is to use [ROW policy.](https://clickhouse.com/docs/operations/access-rights#row-policy-management) Below is an example that creates a row policy to exclude the deleted rows from all queries on the table votes.

<pre><code type='click-ui' language='sql'>
-- Apply row policy to all users
CREATE ROW POLICY cdc_policy ON votes FOR SELECT USING _peerdb_is_deleted = 0 TO ALL;
</code></pre>

> Row policies are applied to a list of users and roles. We apply it to all users and roles, but depending on your environment, you should apply it only to specific users or roles. 

### Query like Postgres -- Minimize migration effort

Migrating an analytical dataset from PostgreSQL to ClickHouse often requires modifying application queries to account for differences in data handling and query execution. As mentioned in the previous section, PostgreSQL queries may need adjustments to ensure proper data deduplication in ClickHouse.

This section will explore techniques for deduplicating data while keeping the original queries unchanged.

#### Views

[Views](https://clickhouse.com/docs/sql-reference/statements/create/view#normal-view) are a great way to hide the FINAL keyword from the query, as they do not store any data and simply perform a read from another table on each access.

Below is an example of creating views for each table of our database in ClickHouse with the FINAL keyword and filter for the deleted rows.

<pre><code type='click-ui' language='sql'>
CREATE VIEW posts_view AS SELECT * FROM posts FINAL where _peerdb_is_deleted=0;
CREATE VIEW users_view AS SELECT * FROM users FINAL where _peerdb_is_deleted=0;
CREATE VIEW votes_view AS SELECT * FROM votes FINAL where _peerdb_is_deleted=0;
CREATE VIEW comments_view AS SELECT * FROM comments FINAL where _peerdb_is_deleted=0;
</code></pre>

Then, we can query the views using the same query we would use in PostgreSQL. 

<pre><code type='click-ui' language='sql'>
-- Most viewed posts
SELECT
    sum(viewcount) AS viewcount,
    owneruserid
FROM posts_view
WHERE owneruserid > 0
GROUP BY owneruserid
ORDER BY viewcount DESC
LIMIT 10
</code></pre>

#### Refreshable Material view 

Another approach is to use a [Refreshable Materialized View](https://clickhouse.com/docs/materialized-view/refreshable-materialized-view), which enables you to schedule query execution for deduplicating rows and storing the results in a destination table. With each scheduled refresh, the destination table is replaced with the latest query results.

The key advantage of this method is that the query using the FINAL keyword runs only once during the refresh, eliminating the need for subsequent queries on the destination table to use FINAL.

However, a drawback is that the data in the destination table is only as up-to-date as the most recent refresh. That said, for many use cases, refresh intervals ranging from several minutes to a few hours may be sufficient.

<pre><code type='click-ui' language='sql'>
-- Create deduplicated posts table 
CREATE table deduplicated_posts AS posts;

-- Create the Materialized view and schedule to run every hour
CREATE MATERIALIZED VIEW deduplicated_posts_mv REFRESH EVERY 1 HOUR TO deduplicated_posts AS 
SELECT * FROM posts FINAL where _peerdb_is_deleted=0 
</code></pre>

Then, you can query the table `deduplicated_posts` normally.

<pre><code type='click-ui' language='sql'>
SELECT
    sum(viewcount) AS viewcount,
    owneruserid
FROM deduplicated_posts
WHERE owneruserid > 0
GROUP BY owneruserid
ORDER BY viewcount DESC
LIMIT 10;
</code></pre>

### Advanced: Tuning merge settings

ReplicatingMergeTree engine table removes duplicates periodically, at merge time, to be precise, as documented [here](https://clickhouse.com/docs/guides/replacing-merge-tree#tuning-merges-for-better-query-performance). 

By default, merging occurs infrequently and is not frequent enough to serve as a reliable deduplication method. However, you can adjust the merge timing by modifying the table configuration.

The ReplacingMergeTree documentation [here](https://clickhouse.com/docs/guides/replacing-merge-tree#tuning-merges-for-better-query-performance) describes the three settings that can be adjusted to merge the data more frequently:

-   [min_age_to_force_merge_seconds ](https://clickhouse.com/docs/operations/settings/merge-tree-settings#min_age_to_force_merge_seconds): ClickHouse will consider merging parts that are older than this value. Default to 0 - Disabled. 
-   [min_age_to_force_merge_on_partition_only](https://clickhouse.com/docs/operations/settings/merge-tree-settings#min_age_to_force_merge_on_partition_only): Whether min_age_to_force_merge_seconds should be applied only on the entire partition and not on a subset. Default to false.

We can set these values to existing tables using the ALTER TABLE statement. For example, I could set `min_age_to_force_merge_seconds` to `10 seconds`, `min_age_to_force_merge_on_partition_only` to `true` for the table posts with the following command.

<pre><code type='click-ui' language='sql'>
-- Tune merge settings
ALTER TABLE posts MODIFY SETTING min_age_to_force_merge_seconds=10;
ALTER TABLE posts MODIFY SETTING min_age_to_force_merge_on_partition_only=true;
</code></pre>

> Tweaking these settings increases merge frequency and can drastically reduce duplicates, but it doesn’t guarantee that there will be no duplicates. This may be acceptable for some analytical workloads.

## Ordering keys

[Ordering Keys](https://clickhouse.com/docs/migrations/postgresql/designing-schemas#primary-ordering-keys-in-clickhouse) (a.k.a. sorting keys) define how data is sorted on disk and indexed for a table in ClickHouse. When replicating from Postgres, ClickPipes sets the Postgres primary key of a table as the ordering key for the corresponding table in ClickHouse. In most cases, the Postgres primary key serves as a sufficient ordering key, as ClickHouse is already optimized for fast scans, and custom ordering keys are often not required.

For larger use cases, you should include additional columns beyond the Postgres primary key in the ClickHouse ordering key to optimize queries. By default, choosing an ordering key different from the Postgres primary key can cause data deduplication issues in ClickHouse. This happens because the ordering key in ClickHouse serves a dual role: it controls data indexing and sorting while acting as the deduplication key. You can learn more about this caveat [here](https://docs.peerdb.io/mirror/ordering-key-different). The easiest way to address this issue is by defining refreshable materialized views.

### Use Refreshable Materialized Views

A simple way to define custom ordering keys (ORDER BY) is using refreshable materialized views (MVs). These allow you to periodically (e.g., every 5 or 10 minutes) copy the entire table with the desired ordering key. For more details and caveats, refer to the section [above](/blog/postgres-to-clickhouse-data-modeling-tips-v2#refreshable-material-view).

Below is an example of a Refreshable MV with a custom ORDER BY and required deduplication:

<pre><code type='click-ui' language='sql'>
CREATE MATERIALIZED VIEW posts_final
REFRESH EVERY 10 second ENGINE = ReplacingMergeTree(_peerdb_version)
ORDER BY (owneruserid,id) -- different ordering key but with suffixed postgres pkey
AS
SELECT * FROM posts FINAL 
WHERE _peerdb_is_deleted = 0; -- this does the deduplication
</code></pre>

### Custom ordering keys without refreshable materialized views

If refreshable materialized views don't work due to the scale of data, here are a few recommendations you can follow to define custom ordering keys on larger tables and overcome deduplication-related [issues](https://docs.peerdb.io/mirror/ordering-key-different).

**Choose ordering key columns that don't change for a given row**

When including additional columns in the ordering key for ClickHouse (besides the primary key from Postgres), we recommend selecting columns that don't change for each row. This helps prevent data consistency and deduplication issues with ReplacingMergeTree.

For example, in a multi-tenant SaaS application, using (`tenant_id`, `id`) as the ordering key is a good choice. These columns uniquely identify each row, and `tenant_id` remains constant for an `id` even if other columns change. Since deduplication by id aligns with deduplication by (tenant_id, id), it helps avoid data [deduplication issues](https://docs.peerdb.io/mirror/ordering-key-different) that could arise if tenant_id were to change.

**Note**: If you have scenarios where ordering keys need to include columns that change, please reach out to us at support@clickhouse.com. There are advanced methods to handle this, and we will work with you to find a solution.

**Set Replica Identity on Postgres Tables to Custom Ordering Key**

For Postgres CDC to function as expected, it is important to modify the `REPLICA IDENTITY` on tables to include the ordering key columns. This is essential for handling DELETEs accurately.

If the `REPLICA IDENTITY` does not include the ordering key columns, Postgres CDC will not capture the values of columns other than the primary key - this is a limitation of Postgres logical decoding. All ordering key columns besides the primary key in Postgres will have nulls. This affects deduplication, meaning the previous version of the row may not be deduplicated with the latest deleted version (where `_peerdb_is_deleted` is set to 1).

In the above example with `owneruserid` and `id`, if the primary key does not already include `owneruserid`, you need to have a `UNIQUE INDEX` on (`owneruserid`, `id`) and set it as the `REPLICA IDENTITY` for the table. This ensures that Postgres CDC captures the necessary column values for accurate replication and deduplication.

Below is an example of how to do this on the events table. Make sure to apply this to all tables with modified ordering keys.

<pre><code type='click-ui' language='sql'>
-- Create a UNIQUE INDEX on (owneruserid, id)
CREATE UNIQUE INDEX posts_unique_owneruserid_idx ON posts(owneruserid, id);
-- Set REPLICA IDENTITY to use this index
ALTER TABLE posts REPLICA IDENTITY USING INDEX posts_unique_owneruserid_idx;
</code></pre>

### Another option: Projections

As described in ClickHouse [documentation](https://clickhouse.com/docs/en/sql-reference/statements/alter/projection), Projections are useful for running queries on a column that is not a part of the primary key.

> The biggest caveat with Projections is that they get skipped when querying the table with the FINAL keyword and do not account for deduplication. This could work for a few use cases where duplicates (updates, deletes) are not present or are less common.

Projections are defined on the table we want to add a custom ordering key for. Then, each time a query is executed on this table, ClickHouse determines if the query execution can benefit from using one of the existing Projections.

Let's take an example where we want to order the table posts by the field `creationdate` instead of the current one id. This would benefit query that filter using a date range.

Consider the following query that finds the most viewed posts mentioning "clickhouse" in 2024.

<pre><code type='click-ui' language='sql'>
SELECT
    id,
    title,
    viewcount
FROM stackoverflow.posts
WHERE (toYear(creationdate) = 2024) AND (body LIKE '%clickhouse%')
ORDER BY viewcount DESC
LIMIT 5

5 rows in set. Elapsed: 0.617 sec. Processed 4.69 million rows, 714.67 MB (7.60 million rows/s., 1.16 GB/s.)
Peak memory usage: 147.04 MiB.
</code></pre>

By default, ClickHouse needs to do a full scan of the table as the order by is `id`, we can note in the last query processed 4.69 million rows.
Now, let's add a Projection to order by `creationdate`.

<pre><code type='click-ui' language='sql'>
-- Create the Projection
ALTER TABLE posts ADD PROJECTION creation_date_projection (
SELECT
*
ORDER BY creationdate
);

-- Materialize the Projection
ALTER TABLE posts MATERIALIZE PROJECTION creation_date_projection;
</code></pre>

Then, we run again the same query. 

<pre><code type='click-ui' language='sql'>
SELECT
    id,
    title,
    viewcount
FROM stackoverflow.posts
WHERE (toYear(creationdate) = 2024) AND (body LIKE '%clickhouse%')
ORDER BY viewcount DESC
LIMIT 5

5 rows in set. Elapsed: 0.438 sec. Processed 386.80 thousand rows, 680.42 MB (882.29 thousand rows/s., 1.55 GB/s.)
Peak memory usage: 79.37 MiB.
</code></pre>

ClickHouse utilized the Projection to execute the query, reducing rows scanned to just 386,000 compared to 4.69 million previously, while also lowering memory usage.

## JOINs and Denormalization

Since Postgres is a relational database, its data model is heavily [normalized](https://en.wikipedia.org/wiki/Database_normalization), often involving hundreds of tables. A common question users ask is whether the same data model works for ClickHouse and how to optimize JOIN performance.

### Optimizing JOINs

ClickHouse has been heavily [investing](https://clickhouse.com/docs/whats-new/changelog/2024#performance-improvement) in JOIN performance. For most use cases, running queries with JOINs (as in Postgres) on raw data in ClickHouse should perform significantly better than in Postgres.

You can run the JOIN queries without any changes and observe how ClickHouse performs.

If case you want to optimize further, here are a few techniques you can try:

- **Use subqueries or CTE for filtering**: Modify JOINs as subqueries where you filter tables within the subquery before passing them to the planner. This is usually unnecessary, but it's sometimes worth trying. Below is an example of a JOIN query using a sub-query.

<pre><code type='click-ui' language='sql'>
-- Use a subquery to reduce the number of rows to join
SELECT
    t.id AS UserId,
    t.displayname,
    t.views,
    COUNTDistinct(multiIf(c.id != 0, c.id, NULL)) AS CommentsCount
FROM (
    SELECT id, displayname, views
    FROM users
    ORDER BY views DESC
    LIMIT 10
) t
LEFT JOIN comments c ON t.id = c.userid
GROUP BY t.id, t.displayname, t.views
ORDER BY t.views DESC
SETTINGS final=1;
</code></pre>

-  **Optimize Ordering Keys**: Consider including JOIN columns in the `Ordering Key` of the table. For more details, refer to the above section on modifying the `Ordering Key`.

- **Use Dictionaries for dimension tables**: Consider creating a [dictionary](https://clickhouse.com/docs/sql-reference/dictionaries) from a table in ClickHouse to improve lookup performance during query execution. In our StackOverflow dataset, the votes table could be a good candidate for conversion into a dictionary. This [documentation](https://clickhouse.com/docs/dictionary#speeding-up-joins-using-a-dictionary) provides an example of how to use dictionaries to optimize JOIN queries with the StackOverflow dataset.

- **JOIN algorithms**: ClickHouse offers various algorithms for joining tables, and selecting the right one depends on the specific use case. This [blog](https://clickhouse.com/blog/clickhouse-fully-supports-joins-how-to-choose-the-right-algorithm-part5) explains how to choose the most suitable algorithm. Below are two examples of JOIN queries using different algorithms tailored to distinct scenarios: in the first case, the goal is to reduce memory usage, so the partial_merge algorithm is used, while in the second case, the focus is on performance, and the parallel_hash algorithm is used. Note the difference in memory used.

<pre><code type='click-ui' language='sql'>
-- Use partial merge algorithm
SELECT
    sum(p.viewcount) AS viewcount,
    p.owneruserid AS user_id,
    u.displayname AS display_name
FROM posts AS p
FINAL
LEFT JOIN users AS u
FINAL ON (u.id = p.owneruserid) AND (u._peerdb_is_deleted = 0)
WHERE (p.owneruserid > 0) AND (p._peerdb_is_deleted = 0)
GROUP BY
    user_id,
    display_name
ORDER BY viewcount DESC
LIMIT 10
FORMAT `NULL`
SETTINGS join_algorithm = 'partial_merge'

10 rows in set. Elapsed: 7.202 sec. Processed 60.42 million rows, 1.83 GB (8.39 million rows/s., 254.19 MB/s.)
Peak memory usage: 1.99 GiB.

-- Use parallel hash algorithm
SELECT
    sum(p.viewcount) AS viewcount,
    p.owneruserid AS user_id,
    u.displayname AS display_name
FROM posts AS p
FINAL
LEFT JOIN users AS u
FINAL ON (u.id = p.owneruserid) AND (u._peerdb_is_deleted = 0)
WHERE (p.owneruserid > 0) AND (p._peerdb_is_deleted = 0)
GROUP BY
    user_id,
    display_name
ORDER BY viewcount DESC
LIMIT 10
FORMAT `NULL`
SETTINGS join_algorithm = 'parallel_hash'

10 rows in set. Elapsed: 2.160 sec. Processed 60.42 million rows, 1.83 GB (27.97 million rows/s., 847.53 MB/s.)
Peak memory usage: 5.44 GiB.
</code></pre>

### Denormalization

Another approach users follow to speed up queries is denormalizing data in ClickHouse to create a more flattened table. You could do this with Refreshable Materialized views or Incremental Materialized views.

Two main strategies will be explored when [denormalizing data using materialized views](https://clickhouse.com/docs/data-modeling/denormalization). One is to flatten the raw data with no transformation simply; we'll refer to it as raw denormalization. The other approach is to aggregate the data as we denormalize it and store it in a Materialized view; we'll refer to it as aggregated denormalization. 

#### Raw denormalization with Refreshable Materialized Views

Using Refreshable Materialized views to flatten data is easy and allows for the filtering out of duplicates at refresh time, as described in the [deduplication strategy section](/blog/postgres-to-clickhouse-data-modeling-tips-v2#deduplication-strategy).

Let's take an example of how we can achieve that by flattening the table posts and users.

<pre><code type='click-ui' language='sql'>
-- Create the RMV
CREATE MATERIALIZED VIEW raw_denormalization_rmv
REFRESH EVERY 1 MINUTE ENGINE = MergeTree()
ORDER BY (id)
AS
SELECT p.*, u.* FROM posts p FINAL LEFT JOIN users u FINAL ON u.id = p.owneruserid AND u._peerdb_is_deleted = 0
WHERE p._peerdb_is_deleted = 0;
</code></pre>

After a few seconds the materialized view is populated with the result of the JOIN query. We can query it with no JOINs or FINAL keyword. 

<pre><code type='click-ui' language='sql'>
-- Number of posts and sum view for top 10 most upvoted users 
SELECT
    countDistinct(id) AS nb_posts,
    sum(viewcount) AS viewcount,
    u.id as user_id,
    displayname,
    upvotes
FROM raw_denormalization_rmv
GROUP BY
    user_id,
    displayname,
    upvotes
ORDER BY upvotes DESC
LIMIT 10
</code></pre>

#### Aggregated denormalization with Refreshable Materialized Views

It is also a common strategy to aggregate the data and store the result in separate tables using Refreshable Materialized Views for even faster access to results but at the cost of query flexibility.

Consider a query that joins the table posts, users, comments, and votes to retrieve the number of posts, votes, and comments for the most upvoted users. We will use a Refreshable Materialized View to keep the result of this query.

<pre><code type='click-ui' language='sql'>
-- Create the Refreshable materialized view
CREATE MATERIALIZED VIEW top_upvoted_users_activity_mv REFRESH EVERY 10 minute ENGINE = MergeTree()
ORDER BY (upvotes) 
AS 
SELECT
    u.id AS UserId,
    u.displayname,
    u.upvotes,
    COUNT(DISTINCT CASE WHEN p.id <> 0 THEN p.id END) AS PostCount,
    COUNT(DISTINCT CASE WHEN c.id <> 0 THEN c.id END) AS CommentsCount,
    COUNT(DISTINCT CASE WHEN v.id <> 0 THEN v.id END) AS VotesCount
FROM users AS u
LEFT JOIN posts AS p ON u.id = p.owneruserid AND p._peerdb_is_deleted=0
LEFT JOIN comments AS c ON u.id = c.userid AND c._peerdb_is_deleted=0
LEFT JOIN votes AS v ON u.id = v.userid AND v._peerdb_is_deleted=0
WHERE u._peerdb_is_deleted=0
GROUP BY
    u.id,
    u.displayname,
    u.upvotes
ORDER BY u.upvotes DESC
SETTINGS final=1;
</code></pre>

The query might take a few minutes to run. In this case, there is no need to use a Common Table Expression, as we want to process the entire dataset. 

To return the same result as the JOIN query, we run a simple query on the materialized view. 

<pre><code type='click-ui' language='sql'>
SELECT *
FROM top_upvoted_users_activity_mv
ORDER BY upvotes DESC
LIMIT 10;
</code></pre>

#### Raw denormalization using Incremental Materialized View

Incremental Materialized Views can also be used for raw denormalization, offering two key advantages over Refreshable Materialized Views (RMVs):

-   The query runs only on newly inserted rows rather than scanning the entire source table, making it a suitable choice for massive datasets, including those in the petabyte range.
-   The materialized view is updated in real-time as new rows are inserted into the source table, whereas RMVs refresh periodically.

However, a limitation is that deduplication cannot occur at insert time. Queries on the destination table still require the FINAL keyword to handle duplicates.

<pre><code type='click-ui' language='sql'>
-- Create Materialized view 
CREATE MATERIALIZED VIEW raw_denormalization_imv
ENGINE = ReplacingMergeTree(_peerdb_version)
ORDER BY (id)  POPULATE AS
SELECT p.id as id, p.*, u.* FROM posts p LEFT JOIN users u ON p.owneruserid = u.id;
</code></pre>

When querying the view, we must include the FINAL modifier to deduplicate the data. 

<pre><code type='click-ui' language='sql'>
SELECT count()
FROM raw_denormalization_imv
FINAL
WHERE _peerdb_is_deleted = 0
</code></pre>

#### Aggregated denormalization using Incremental Materialized View

Incremental Materialized View can also aggregate data as it gets synchronized from PostgreSQL. However, this is a bit more complex as we must account for duplicates and deleted rows when aggregating them. ClickHouse supports a specific table engine, [AggregatingMergeTree](https://clickhouse.com/docs/engines/table-engines/mergetree-family/aggregatingmergetree), that is specifically designed to handle this advanced use case.

Let's walk through an example to understand better how to implement this. Consider a query that calculates the number of new questions on StackOverflow per day.

<pre><code type='click-ui' language='sql'>
-- Number of Questions and Answers per day
SELECT
    CAST(toStartOfDay(creationdate), 'Date') AS Day,
    countIf(posttypeid = 1) AS Questions,
    countIf(posttypeid = 2) AS Answers
FROM posts
GROUP BY Day
ORDER BY Day DESC
LIMIT 5
</code></pre>

One challenge is that each update in PostgreSQL creates a new row in ClickHouse. Simply aggregating the incoming data and storing the result in the destination table would lead to duplicate counts.

Let’s look at what’s happening in ClickHouse when using a Materialized view with Postgres CDC. 

<img preview="/uploads/large_postgres_cdc_data_modelling_003_427f2177f7.png" src="/uploads/postgres_cdc_data_modelling_003_427f2177f7.png" class="h-auto w-auto max-w-full"  style="width: 100%;">

When the row with `id=6440` is updated in PostgreSQL, a new version is inserted into ClickHouse as a separate row. Since the Materialized View processes only the newly inserted block of rows and does not have access to the entire table at ingest time, this leads to a duplicated count.

The AggregatingMergeTree mitigates this issue by allowing the retention of only one row per primary key (or order by key) alongside the aggregated and state of the values.
Let's create a table `daily_posts_activity` to store the data. The table uses AggregatingMergeTree for the table engine and uses [AggregateFunction](https://clickhouse.com/docs/en/sql-reference/data-types/aggregatefunction) field type for the columns `Questions` and `Answers`.

<pre><code type='click-ui' language='sql'>
CREATE TABLE daily_posts_activity
(
    Day Date NOT NULL,
    Questions AggregateFunction(uniq, Nullable(Int32)),
    Answers AggregateFunction(uniq, Nullable(Int32))
)
ENGINE = AggregatingMergeTree()
ORDER BY Day;
</code></pre>

Next, we ingest data from the posts table. We use the [uniqState](https://clickhouse.com/docs/sql-reference/data-types/aggregatefunction#data-insertion) function to track the field's unique states, enabling us to eliminate duplicates.

<pre><code type='click-ui' language='sql'>
INSERT INTO daily_posts_activity
SELECT toStartOfDay(creationdate)::Date AS Day,
       uniqState(CASE WHEN posttypeid=1 THEN id END) as Questions,
       uniqState(CASE WHEN posttypeid=2 THEN id END) as Answers
FROM posts FINAL
GROUP BY Day
</code></pre>

Then, we can create the Materialized view to keep running the query on each new incoming block of rows. 

<pre><code type='click-ui' language='sql'>
CREATE MATERIALIZED VIEW daily_posts_activity_mv TO daily_posts_activity AS
SELECT toStartOfDay(creationdate)::Date AS Day,
       uniqState(CASE WHEN posttypeid=1 THEN id END) as Questions,
       uniqState(CASE WHEN posttypeid=2 THEN id END) as Answers
FROM posts
GROUP BY Day
</code></pre>

To query the `daily_posts_activity`, we have to use the function [uniqMerge](https://clickhouse.com/docs/en/sql-reference/data-types/aggregatefunction#data-selection) to combine the states and return the correct count.

<pre><code type='click-ui' language='sql'>
SELECT
    Day,
    uniqMerge(Questions) AS Questions,
    uniqMerge(Answers) AS Answers
FROM daily_posts_activity
GROUP BY Day
ORDER BY Day DESC
LIMIT 5
</code></pre>

This works great for our use case. 

The deleted rows in PostgreSQL will not be reflected in the `daily_posts_activity` aggregated table, which means that this table reports the total number of posts ever created per day but not the latest state.

## Summary 

Replicating analytical data from PostgreSQL to ClickHouse with Postgres CDC is an efficient way to scale your business, enabling real-time analysis of large datasets. By offloading analytical queries to ClickHouse, you can reduce the load on PostgreSQL while leveraging ClickHouse's high-performance capabilities.

In this blog post, we explored how ClickHouse utilizes CDC to sync data from PostgreSQL, manage duplicate rows, and optimize query performance using custom ordering keys, tips on JOINs queries and denormalization.

With these best practices, you now have the knowledge to implement PostgreSQL CDC effectively and maximize ClickHouse's speed and scalability. Get started with [ClickPipes](https://clickhouse.com/cloud/clickpipes/postgres-cdc-connector) with ClickHouse Cloud for an integrated experience or try the open-source [PeerDB](https://github.com/PeerDB-io/peerdb) for on-prem implementation.