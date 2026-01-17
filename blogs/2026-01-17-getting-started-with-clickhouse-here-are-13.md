---
title: "Getting started with ClickHouse? Here are 13 \"Deadly Sins\" and how to avoid them"
date: "2022-10-26T18:15:59.928Z"
author: "Dale McDiarmid, Tom Schreiber & Geoff Genz"
category: "Engineering"
excerpt: "The 13 most common getting started issues with ClickHouse"
---

# Getting started with ClickHouse? Here are 13 "Deadly Sins" and how to avoid them

> This blog post was originally published in 2022. While much of the guidance remains valuable, we recommend referring to the latest, actively maintained best practices for [ClickHouse self-managed](https://clickhouse.com/docs/best-practices) and [ClickHouse Cloud](https://clickhouse.com/docs/cloud/bestpractices). These resources reflect the most current recommendations for optimizing performance, reliability, and cost efficiency in both self-managed and cloud environments.

![getting-started-challenges.png](https://clickhouse.com/uploads/getting_started_challenges_5c021cb7e3.png)

## Introduction

At ClickHouse, we are constantly thinking about our getting started experience and how we can help users get value from our products in the shortest possible time. While most users have a smooth onboarding, we appreciate that ClickHouse is a complex piece of software that introduces new concepts for many. Coupled with the challenges of managing ClickHouse at scale, this was one of the reasons that led us to develop our serverless [ClickHouse Cloud](https://clickhouse.cloud/signUp) solution, which automatically handles many of the common getting-started and subsequent scaling challenges.

However, some issues are simply the result of misconfiguration or, more commonly, misunderstanding of ClickHouse behavior and appropriate feature usage. In this post, we highlight the top 13 problems we see our new users encounter as the result of either using ClickHouse in an anti-pattern or simply not adhering to best usage practices: aka, the 13 deadly sins of getting started with ClickHouse. All of these apply to self-managed users, with a subset still having relevance to [ClickHouse Cloud](https://clickhouse.cloud/signUp). For each, we recommend a resolution or correct approach.

## 1. Too many parts

An often-seen [ClickHouse error](https://github.com/ClickHouse/ClickHouse/search?p=2&q=%22too+many+parts%22&type=issues), this usually points to incorrect ClickHouse usage and lack of adherence to best practices. This error will often be experienced when inserting data and will be present in ClickHouse logs or in a response to an INSERT request.  To understand this error, users need to have a basic understanding of the concept of a part in ClickHouse.

A table in ClickHouse consists of data parts sorted by the user's specified primary key (by default, the ORDER BY clause on table creation but see [Index Design](https://clickhouse.com/docs/en/guides/improving-query-performance/sparse-primary-indexes/sparse-primary-indexes-design) for the details). When data is inserted in a table, separate data parts are created, and each of them is lexicographically sorted by primary key. For example, if the primary key is `(CounterID, Date)`, the data in the part is sorted first by `CounterID`, and within each `CounterID` value by `Date`. In the background, ClickHouse merges data parts for more efficient storage, similar to a [Log-structured merge tree](https://en.wikipedia.org/wiki/Log-structured_merge-tree). Each part has its own primary index to allow efficient scanning and identification of where values lie within the parts. When parts are merged, then the merged part’s primary indexes are also merged.

![sins-01-parts.png](https://clickhouse.com/uploads/sins_01_parts_db7108e636.png)

As the number of parts increases, queries invariably will slow as a result of the need to evaluate more indices and read more files. Users may also experience slow startup times in cases where the part count is high. The creation of too many parts thus results in more internal merges and “pressure” to keep the number of parts low and query performance high. While merges are concurrent, in cases of misuse or misconfiguration, the number of parts can exceed internal configurable limits[[1]](https://clickhouse.com/docs/en/operations/settings/merge-tree-settings/#parts_to_throw_insert)[[2]](https://clickhouse.com/docs/en/operations/settings/merge-tree-settings/#max_parts_in_total). While these limits can be adjusted, at the expense of query performance, the need to do so will more often point to issues with your usage patterns. As well as causing query performance to degrade, high part counts can also place greater pressure on ClickHouse Keeper in replicated configurations.

So, how is it possible to have too many of these parts?

### Poorly chosen partitioning key

A common reason is using a partition key with excessive [cardinality](https://en.wikipedia.org/wiki/Cardinality). On creating a table, users can specify a column as a partition key by which data will be separated. A new file system directory will be created for every key value. This is typically a data management technique, allowing users to cleanly separate data logically in a table, e.g., by day. Operations such as DROP PARTITION subsequently allow fast deletion of data subsets. This powerful feature can, however, easily be misused, with users interpreting it as a simple optimization technique for queries. Importantly, parts belonging to different partitions are never merged. If a key of high cardinality, e.g., `date_time_ms`, is chosen as a partition key then parts spread across thousands of folders will never be merge candidates - exceeding preconfigured limits and causing the dreaded "Too many inactive parts (N). Parts cleaning are processing significantly slower than inserts" error on subsequent INSERTs. Addressing this problem is simple: choose a sensible partition key with cardinality &lt; 1000.

![sins-02-partitioning.png](https://clickhouse.com/uploads/sins_02_partitioning_14b984c2bf.png)

### Many small inserts

As well as the poor selection of a partition key, this issue can manifest itself as a result of many small inserts. Each INSERT into ClickHouse results in an insert block being converted to a part. To keep the number of parts manageable, users should therefore buffer data client-side and insert data as batches - ideally, at least [1000 rows](https://clickhouse.com/docs/en/about-us/performance/#performance-when-inserting-data), although this should be tuned. If client-side buffering is not possible, users can defer this task to ClickHouse through [async inserts.](https://clickhouse.com/docs/en/operations/settings/settings/#async-insert) In this case, ClickHouse will buffer inserts on the local disk before merging them together for insertion into the underlying table.

![sins-03-async_inserts.png](https://clickhouse.com/uploads/sins_03_async_inserts_f51b9d0035.png)

[Buffer tables](https://clickhouse.com/docs/en/engines/table-engines/special/buffer/) are also an alternative option here but are less resilient to failure as they hold inserts in memory until a flush occurs. They do have some advantages over async inserts- principally the data will be queryable whilst in the buffer and their compatibility as a buffer to the target table of a materialized view.

### Excessive materialized views

Other possible causes of this error are excessive materialized views. Materialized views are, in effect, a trigger that runs when a block is inserted into a table. They transform the data e.g., through a GROUP BY, before inserting the result into a different table. This technique is often used to accelerate certain queries by precomputing aggregations at INSERT time. Users can create these materialized views, potentially resulting in many parts. Generally, we recommended that users create views while being aware of the costs and consolidate them where possible.

![sins-04-mvs.png](https://clickhouse.com/uploads/sins_04_mvs_1f872af2fa.png)

The above list is not an exhaustive cause of this error. For example, mutations (as discussed below) can also cause merge pressure and an accumulation of parts. Finally, we should note that this error, while the most common, is only one manifestation of the above misconfigurations. For example, users can experience other issues as a result of a poor partitioning key. These include, but are not limited to, “no free inodes on the filesystem”, backups taking a long time, and delays on replication (and high load on ClickHouse Keeper).

## 2. Going horizontal too early

We often have new self-managed users asking us to provide recommendations around orchestration and how to scale to dozens, if not hundreds, of nodes. While technologies such as Kubernetes have made the deployment of multiple instances of stateless applications relatively simple, this pattern should, in nearly all cases, not be required for ClickHouse. Unlike other databases, which may be restricted to a machine size due to inherent limits, e.g., JVM heap size, ClickHouse was designed from the ground up to utilize the full resources of a machine. We commonly find successful deployments with ClickHouse deployed on servers with hundreds of cores, terabytes of RAM, and petabytes of disk space. Most analytical queries have a sort, filter, and aggregation stage. Each of these can be parallelized independently and will, by default, use as many [threads as cores](https://clickhouse.com/docs/en/operations/settings/settings/#settings-max_threads), thus utilizing the full machine resources for a query.

![sins-05-vertical_scale.png](https://clickhouse.com/uploads/sins_05_vertical_scale_d36926028c.png)

Scaling vertically first has a number of benefits, principally cost efficiency, lower cost of ownership (with respect to operations), and better query performance due to the minimization of data on the network for operations such as JOINs. Of course, users need redundancy in their infrastructure, but two machines should be sufficient for all but the largest use cases.

For this reason, in addition to simpler scaling mechanics, we prefer to auto-scale vertically in [ClickHouse Cloud](https://clickhouse.cloud/signUp) before considering horizontal scaling. In summary, go vertical before going horizontal!

## 3. Mutation Pain

While rare in OLAP use cases, the need to modify data is sometimes unavoidable. To address this requirement, ClickHouse offers [mutation](https://clickhouse.com/docs/en/sql-reference/statements/alter/#mutations) functionality which allows users to modify inserted data through [ALTER queries](https://clickhouse.com/docs/en/sql-reference/statements/alter/update/). ClickHouse performs best on immutable data, and any design pattern which requires data to be updated post-insert should be reviewed carefully.

Internally, mutations work by rewriting whole data parts. This process relies on the same thread pool as merges. Note also that the mutation needs to be applied on all replicas [by default](https://clickhouse.com/docs/en/operations/settings/settings/#always_fetch_merged_part). For this reason, mutations are both CPU and IO-intensive and should be scheduled cautiously with permission to run limited to administrators. Resource pressure as a result of mutations manifests itself in several ways. Typically, normally scheduled merges accumulate, which in turn causes our earlier “too many parts” issue. Furthermore, users may experience replication delays. The [system.mutations](https://clickhouse.com/docs/en/operations/system-tables/mutations#system_tables-mutations) table should give administrators an indication of currently scheduled mutations. Note that mutations can be cancelled, but not rolled back, with the [KILL MUTATION ](https://clickhouse.com/docs/en/sql-reference/statements/kill#kill-mutation)query.

![sins-06-mutations.png](https://clickhouse.com/uploads/sins_06_mutations_647f7d67d9.png)

### Deduplication

We often see users needing to schedule merges as a result of duplicate data. Typically we suggest users address this issue upstream and deduplicate prior to insertion into ClickHouse. If this is not possible, users have a number of options: deduplicate at query time or utilize a [ReplacingMergeTree](https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/replacingmergetree/).

Deduplicating at query time can be achieved by grouping the data on the fields, which uniquely identify a row, and using the [argMax](https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/argmax/) function with a date field to identify the last value for other fields. [ReplacingMergeTree](https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/replacingmergetree/) allows rows with the same sorting key (ORDER BY key) to be deduplicated on merges. Note this is “best effort” only: sometimes parts will not be merged with the merge process scheduled at non-deterministic intervals. It, therefore, does not guarantee the absence of duplicates. Users can also utilize the [FINAL](https://clickhouse.com/docs/en/sql-reference/statements/select/from/#drawbacks) modifier to force this deduplication at `SELECT` time (again, use cautiously as it is resource intensive and can be slow despite [recent improvements](https://github.com/ClickHouse/ClickHouse/pull/36396)) or force merging on disk via an [OPTIMIZE FINAL](https://clickhouse.com/docs/en/manage/tuning-for-cloud-cost-efficiency/#avoid-using-optimize-final).

In the case where data needs to be deleted from ClickHouse e.g., for compliance or deduplication reasons, users can also utilize lightweight deletes instead of mutations. These take the form of a [DELETE statement](https://clickhouse.com/docs/en/sql-reference/statements/delete/) which accepts WHERE clause to filter rows. This marks rows as deleted only. These marks will be used to filter rows out at query time and will be removed when parts are merged.

![sins-07-lightweight_deletes.png](https://clickhouse.com/uploads/sins_07_lightweight_deletes_e11f6a6988.png)

**Note:** this feature is experimental and requires the setting `SET allow_experimental_lightweight_delete = true;`. It is more efficient than using a mutation in most cases, with the exception of if you are doing a large-scale bulk delete.

## 4. Unnecessary use of complex types

As well as supporting the usual primitive types, ClickHouse has rich support for complex types such as [Nested](https://clickhouse.com/docs/en/sql-reference/data-types/nested-data-structures/nested/#nestedname1-type1-name2-type2-), [Tuple](https://clickhouse.com/docs/en/sql-reference/data-types/tuple), [Map](https://clickhouse.com/docs/en/sql-reference/data-types/map), and even [JSON](https://clickhouse.com/docs/en/guides/developer/working-with-json/json-semi-structured). These are supported for good reasons - sometimes, there is no other way to model data, but we recommend using primitive types where possible since they offer the best insertion and query time performance.

As an example, we have recently seen users keen to exploit the [JSON features](https://clickhouse.com/blog/getting-data-into-clickhouse-part-2-json) added to ClickHouse in 22.4. This powerful feature allows the table schema to be dynamically inferred from the data, avoiding the need for the user to specify column types. Use this capability with caution and not as a replacement for avoiding specifying columns explicitly. Specifically, this feature has limitations users should be aware of:

* Increased cost at insert time as columns need to be dynamically created
* Sub-optimal type usage, i.e., no codecs and unnecessary use of Nullable.
* No ability to use JSON columns in a primary key

The last two of these invariably lead to poorer compression and query/insert performance. Rather than using it for all of your rows, use this specific type for selective columns e.g., Kubernetes tags, where the data is subject to change. In summary, if you know your schema…specify it!

_**Note: The JSON Object type is experimental and is undergoing improvements. Our advice with respect to this feature is evolving and may therefore change in later versions.**_

We additionally often see users reaching for the [Nullable](https://clickhouse.com/docs/en/sql-reference/data-types/nullable/#storage-features) type. This allows the value Null to be differentiated from the default value for a type. This can be useful but requires an additional Uint8 column to determine which values are null. This incurs an extra byte per value with respect to storage (although it compresses well), as well as adding a query time overhead. Only use Nullable if you really need it!

## 5. Deduplication at insert time

New users to [ClickHouse Cloud](https://clickhouse.cloud/signUp) are often surprised by ClickHouse’s deduplication strategy. This usually occurs when identical inserts appear to not have any effect. For example, consider the following:

<pre style='background-color: #222222; border-radius: 8px; padding: 24px; color: #FFFFFF; display: flex; position: relative; white-space: pre-wrap;'>
<div style='color: #FFFFFF; margin-top: -24px; max-width: 98%;'>
CREATE TABLE temp
(
   `timestamp` DateTime,
   `value` UInt64
)
ENGINE = MergeTree
ORDER BY tuple()

INSERT INTO temp VALUES ('2022-10-21', 10), ('2022-10-22', 20), ('2022-10-23', 15), ('2022-10-24', 18)
INSERT INTO temp VALUES ('2022-10-21', 10), ('2022-10-22', 20), ('2022-10-23', 15), ('2022-10-24', 18)

clickhouse-cloud :) SELECT * FROM temp

SELECT *
FROM temp

┌───────────timestamp─┬─value─┐
│ 2022-10-21 00:00:00 │    10 │
│ 2022-10-22 00:00:00 │    20 │
│ 2022-10-23 00:00:00 │    15 │
│ 2022-10-24 00:00:00 │    18 │
└─────────────────────┴───────┘
</div>
</pre>
</p>

A new user might be surprised by the result here, especially if their prior experience was on a single local instance of ClickHouse. This behavior is the result of the [`replicated_deduplication_window`](https://clickhouse.com/docs/en/operations/settings/merge-tree-settings/#replicated-deduplication-window) setting.

When data is inserted into ClickHouse, it creates [one or more](https://clickhouse.com/docs/en/operations/settings/settings/#settings-max_insert_block_size) blocks (parts). In replicated environments, such as [ClickHouse Cloud](https://clickhouse.cloud/signUp), a hash is also written in ClickHouse Keeper. Subsequent inserted blocks are compared against these hashes and ignored if a match is present. This is useful since it allows clients to safely retry inserts in the event of no acknowledgement from ClickHouse e.g., because of a network interruption. This requires blocks to be identical i.e., the same size with the same rows in the same order. These hashes are stored for only the most recent 100 blocks, although this can be [modified](https://clickhouse.com/docs/en/operations/settings/merge-tree-settings/#replicated-deduplication-window). Note higher values will slow down inserts due to the need for more comparisons.

![sins-08-deduplication.png](https://clickhouse.com/uploads/sins_08_deduplication_c9f39896d5.png)

This same behavior can be enabled for non-replicated instances via the setting [`non_replicated_deduplication_window`](https://clickhouse.com/docs/en/operations/settings/merge-tree-settings/#replicated-deduplication-window). In this case, the hashes are stored on a local disk.

## 6. Poor Primary Key Selection

Users new to ClickHouse often struggle to fully understand its unique primary key concepts. Unlike [B(+)-](https://en.wikipedia.org/wiki/B%2B_tree)Tree-based OLTP databases, which are optimized for fast location of specific rows, ClickHouse utilizes a sparse index designed for millions of inserted rows per second and petabyte-scale datasets.  In contrast to OLTP databases, this index relies on the data on disk being sorted for fast identification of groups of rows that could possibly match a query - a common requirement in analytical queries. The index, in effect, allows the matching sections of part files to be rapidly identified before they are streamed into the processing engine. For more detail on the layout of the data on disk, we highly [recommend this guide](https://clickhouse.com/docs/en/guides/improving-query-performance/sparse-primary-indexes/sparse-primary-indexes-design/#data-is-stored-on-disk-ordered-by-primary-key-columns).

![sins-09-primary_index.png](https://clickhouse.com/uploads/sins_09_primary_index_d3f166fa7d.png)

The effectiveness of this approach, for both query performance and compression, relies on the user selecting good primary key columns via the [ORDER BY](https://clickhouse.com/docs/en/getting-started/example-datasets/nypd_complaint_data/#order-by-and-primary-key-clauses) clause when creating a table. In general, users should select columns for which they will often filter tables with more than 2 to 3 columns rarely required. The order of these columns is critical and can affect the compression and filtering by columns other than the first entry. For both the efficient filtering of secondary key columns in queries and the compression ratio of a table's column files, it is optimal to order the columns in a primary key by their cardinality in ascending order. A full explanation of the reasoning can be found [here](https://clickhouse.com/docs/en/guides/improving-query-performance/sparse-primary-indexes/sparse-primary-indexes-cardinality).

## 7. Overuse of Data Skipping indices

Primary keys are rightly the first tool users turn to when needing to accelerate queries. However, tables are limited to a single primary key, and query access patterns can render this ineffective i.e., for diverse use cases, queries which cannot exploit the primary key efficiently are inevitable. In these cases ClickHouse can be forced to perform a full table scan of each column when applying a WHERE clause condition. Often this will still be sufficiently fast, but in some cases users reach for [data skipping indices](https://clickhouse.com/docs/en/guides/improving-query-performance/skipping-indexes), hoping to accelerate these queries easily.

These indices add data structures which allow ClickHouse to skip reading significant chunks of data that are guaranteed to have no matching values. More specifically, they create an [index over blocks granules](https://clickhouse.com/docs/en/guides/improving-query-performance/skipping-indexes/#basic-operation) (effectively marks) allowing these to be skipped if the WHERE clause is not satisfied.

![sins-10-skipping_index.png](https://clickhouse.com/uploads/sins_10_skipping_index_21ace4e3eb.png)

In some circumstances, these can accelerate specific queries, but are typically overused, not intuitive and [require careful design to be effective](https://clickhouse.com/docs/en/guides/improving-query-performance/skipping-indexes/#skip-index-types). As a result, we often see them simply complicating table design and slowing insert performance [while rarely (if ever) improving query performance](https://clickhouse.com/docs/en/guides/improving-query-performance/sparse-primary-indexes/sparse-primary-indexes-multiple#note-about-data-skipping-index). We always encourage users to read the concepts and [best practices](https://clickhouse.com/docs/en/guides/improving-query-performance/skipping-indexes/#skip-best-practices).

In most cases skip indices should only be considered once other alternatives have been exhausted - specifically this advanced functionality should only be used after investigating other alternatives such as modifying the primary key (see [Options for creating additional primary indexes](https://clickhouse.com/docs/en/guides/improving-query-performance/sparse-primary-indexes/sparse-primary-indexes-multiple#options-for-creating-additional-primary-indexes)), using projections or materialized views. In general, only consider skip-indices if there is a strong correlation between the primary key and the targeted, non-primary column/expression. In the absence of any real correlation, the skipping index will match for most blocks - resulting in all granules being read into memory and evaluated. In this case, the index cost has been incurred for no benefit, effectively slowing the full table scan.

## 8. LIMIT doesn’t always short circuit + point lookups

We often find OLTP users new to ClickHouse reaching for the LIMIT clause to optimize queries by limiting the number of results returned. If coming from an OLTP database this should intuitively optimize queries: less data returned = faster result, surely? Yes and no.

The effectiveness of this technique depends on whether the query can be run entirely in a [streaming fashion](https://clickhouse.com/docs/en/sql-reference/statements/select/#implementation-details). Some queries, such as `SELECT * FROM table LIMIT 10` will scan only a few [granules](https://clickhouse.com/docs/en/guides/improving-query-performance/sparse-primary-indexes/sparse-primary-indexes-design) of the first few parts before reaching 10 results and returning the result to the user. This is also true for cases where the user orders the SELECT by a primary key field due to the [`optimize_in_read_order`](https://clickhouse.com/docs/en/sql-reference/statements/select/order-by/#optimization-of-data-reading) setting defaulting to 1. However, if the user runs `SELECT a from table ORDER BY b LIMIT N`, whereby the table is ordered by `a` and not by `b`, ClickHouse cannot avoid reading the entire table i.e., no early termination of the query is possible.

For aggregations, things are a little more complex. A full table scan is also required unless the user is grouping by the primary key and sets [`optimize_aggregation_in_order=1`](https://clickhouse.com/docs/en/operations/settings/settings/#optimize_aggregation_in_order). In this case, a propagation signal is sent once sufficient results are acquired. Provided previous steps of the query are capable of streaming the data, e.g., filter, then this mechanism will work, and the query will terminate early. Normally, however, an aggregation must consume all table data before returning and applying the LIMIT as the final stage.

As an example, we create and load the table from our [UK Property Price Paid tutorial](https://clickhouse.com/docs/en/getting-started/example-datasets/uk-price-paid) with 27.55 million rows. This dataset is available within our play.clickhouse.com environment.

With `optimize_aggregation_in_order=0` this aggregation query, that is grouping by the primary keys, performs a full table scan before applying the LIMIT 1 clause:

<pre style='background-color: #222222; border-radius: 8px; padding: 24px; color: #FFFFFF; display: flex; position: relative; white-space: pre-wrap;'>
<div style='color: #FFFFFF; margin-top: -24px; max-width: 98%;'>
clickhouse-cloud :) SELECT
    postcode1, postcode2,
    formatReadableQuantity(avg(price)) AS avg_price
FROM uk_price_paid
GROUP BY postcode1, postcode2
LIMIT 1;

┌─postcode1─┬─postcode2─┬─avg_price───────┐
│ AL4       │ 0DE       │ 335.39 thousand │
└───────────┴───────────┴─────────────────┘

Elapsed: 3.028 sec, read 27.55 million rows, 209.01 MB.
</div> <a style='height: 32px; width: 32px; text-align: center; line-height: 1.3; position: absolute; font-size: 24px; top: 24px; right: 24px; color: #FFFFFF; background: rgba(0,0,0,0.8); border-radius: 8px;' href="https://sql.clickhouse.com?query_id=HDNRS1WAM3BEZKOEUWRAF3" target="_blank">✎</a>
</pre>
</p>

With `optimize_aggregation_in_order=1`, the query is able to shortcut and as a result process less data:

<pre style='background-color: #222222; border-radius: 8px; padding: 24px; color: #FFFFFF; display: flex; position: relative; white-space: pre-wrap;'>
<div style='color: #FFFFFF; margin-top: -24px; max-width: 98%;'>
clickhouse-cloud :) SELECT
       postcode1, postcode2,
       formatReadableQuantity(avg(price))  AS avg_price
FROM uk_price_paid
GROUP BY postcode1, postcode2
LIMIT 1
SETTINGS optimize_aggregation_in_order = 1;

┌─postcode1─┬─postcode2─┬─avg_price───────┐
│ AL4       │ 0DE       │ 335.39 thousand │
└───────────┴───────────┴─────────────────┘

Elapsed: 0.999 sec, read 4.81 million rows, 36.48 MB.
</div>
</pre>
</p>

We also see even experienced users being caught by less obvious LIMIT behavior in multi-node environments where a table has many shards.[ Sharding allows users](https://clickhouse.com/company/events/scaling-clickhouse) to split or replicate their data across multiple instances of ClickHouse. When a query with a LIMIT N clause is sent to a sharded table e.g. via a distributed table, this clause will be propagated down to each shard. Each shard will, in turn, need to collate the top N results, returning them to the coordinating node. This can prove particularly resource-intensive when users run queries that require a full table scan. Typically these are “point lookups” where the query aims to just identify a few rows. While [this can be achieved in ClickHouse with careful index design](https://clickhouse.com/docs/en/guides/improving-query-performance/sparse-primary-indexes/sparse-primary-indexes-uuids) a non-optimized variant, coupled with a LIMIT clause, can prove extremely resource-intensive.

## 9. IP Filtering in Cloud

At ClickHouse, we consider security a first-class citizen and consider this in everything we do. This is epitomized by the need for users to specify the IP addresses from which access is permitted when first creating a cluster. By default, we encourage users to be restrictive and modify the allow list as needed. This, unfortunately, can lead to some confusion when users attempt to connect to external Cloud services, e.g., when connecting from Grafana Cloud. We will continue to optimize this experience and provide helpful guidance when this is the case, but we also recommend users obtain the IPs of any external services early during cluster creation to avoid frustrating connection-denied errors.

![ip-filtering-10.png](https://clickhouse.com/uploads/ip_filtering_10_08eff2f4a2.png)

## 10. Readonly tables

Although not an issue in [ClickHouse Cloud](https://clickhouse.cloud/signUp), read-only tables continue to raise their head in self-managed clusters. This occurs in replicated environments when a node loses its connection to ZooKeeper. This is typically nearly always the result of ZooKeeper issues. While many of the challenges associated with ZooKeeper were addressed with the release of ClickHouse Keeper, under-resourcing of this component can still cause this issue to manifest itself. Common causes are the hosting of the keeper on the same host as ClickHouse in production or poorly tuned ZooKeeper JVM resources. This is usually easily resolved by ensuring this component is separated on dedicated hardware and given adequate resources.

## 11. Memory Limit Exceeded for Query

As a new user, ClickHouse can often seem like magic - every query is super fast, even on the largest datasets and most ambitious queries. Invariably though, real-world usage tests even the limits of ClickHouse. Queries exceeding memory can be the result of a number of causes. Most commonly, we see large joins or aggregations on high cardinality fields. If performance is critical, and these queries are required, we often recommend users simply scale up - something [ClickHouse Cloud](https://clickhouse.cloud/signUp) does automatically and effortlessly to ensure your queries remain responsive. We appreciate, however, that in self-managed scenarios, this is sometimes not trivial, and maybe optimal performance is not even required. Users, in this case, have a few options.

### Aggregations

For memory-intensive aggregations or sorting scenarios, users can use the settings [`max_bytes_before_external_group_by`](https://clickhouse.com/docs/en/operations/settings/query-complexity/#settings-max_bytes_before_external_group_by) and [`max_bytes_before_external_sort`](https://clickhouse.com/docs/en/sql-reference/statements/select/order-by/#implementation-details) respectively. The former of these is discussed extensively [here](https://clickhouse.com/docs/en/sql-reference/statements/select/group-by/#group-by-in-external-memory). In summary, this ensures any aggregations can “spill” out to disk if a memory threshold is exceeded. This will invariably impact query performance but will help ensure queries do not OOM. The latter sorting setting helps address similar issues with memory-intensive sorts. This can be particularly important in distributed environments where a coordinating node receives sorted responses from child shards. In this case, the coordinating server can be asked to sort a dataset larger than its available memory. With  [`max_bytes_before_external_sort`](https://clickhouse.com/docs/en/sql-reference/statements/select/order-by/#implementation-details), sorting can be allowed to spill over to disk. This setting is also helpful for cases where the user has an `ORDER BY` after a `GROUP BY` with a `LIMIT`, especially in cases where the query is distributed.

### JOINs

For joins, users can select different JOIN algorithms, which can assist in lowering the required memory. By default, joins use the hash join, which offers the most completeness with respect to features and often the best performance. This algorithm loads the right-hand table of the JOIN into an in-memory hash table, against which the left-hand table is then evaluated. To minimize memory, users should thus place the smaller table on the right side. This approach still has limitations in memory-bound cases, however. In these cases, `partial_merge` join can be enabled via the [`join_algorithm`](https://clickhouse.com/docs/en/operations/settings/settings#settings-join_algorithm) setting. This derivative of the [sort-merge algorithm](https://en.wikipedia.org/wiki/Sort-merge_join), first sorts the right table into blocks and creates a min-max index for them. It then sorts parts of the left table by the join key and joins them over the right table. The min-max index is used to skip unneeded right table blocks. This is less memory-intensive at the expense of performance. Taking this concept further, the `full_sorting_merge` algorithm allows a JOIN to be performed when the right-hand side is very large and doesn't fit into memory and lookups are impossible, e.g. a complex subquery. In this case, both the right and left side are sorted on disk if they do not fit in memory, allowing large tables to be joined.

![sins-11-joins.png](https://clickhouse.com/uploads/sins_11_joins_ebf4162f6a.png)

Since 20.3, ClickHouse has supported an `auto` value for the `join_algorithm` setting. This instructs ClickHouse to [apply an adaptive join approach](https://clickhouse.com/docs/en/about-us/distinctive-features/#adaptive-join-algorithm), where the hash-join algorithm is preferred until memory limits are violated, at which point the partial_merge algorithm is attempted. Finally, concerning joins, we encourage readers to be aware of the behavior of distributed joins and how to minimize their memory consumption - more information [here](https://clickhouse.com/docs/en/sql-reference/operators/in#distributed-subqueries).

### Rogue queries

Other causes for memory issues are unrestricted users. In these cases, we see users issuing rogue queries with no [quotas](https://clickhouse.com/docs/en/operations/quotas/) or [restrictions on query complexity](https://clickhouse.com/docs/en/operations/settings/query-complexity/). These controls are essential in providing a robust service if exposing a ClickHouse instance to a broad and diverse set of users. Our own [play.clickhouse.com](https://play.clickhouse.com/play?user=play) environment uses these effectively to restrict usage and provide a stable environment.

ClickHouse also recently introduced new [Memory overcommit capabilities](https://clickhouse.com/docs/en/operations/settings/memory-overcommit/). Historically queries would be limited by the [`max_memory_usage`](https://clickhouse.com/docs/en/operations/settings/query-complexity/#settings_max_memory_usage) setting (default 10GB), which provided a hard and rather crude limit. Users could raise this at the expense of a single query, potentially impacting other users. Memory overcommit allows more memory-intensive queries to run, provided sufficient resources exist. When the [max server memory limit is reached](https://clickhouse.com/docs/en/operations/server-configuration-parameters/settings#max_server_memory_usage), ClickHouse will determine which queries are most overcommitted and try to kill the query. This may or may not be the query that triggered this condition. If not, the query will wait a period to allow the high-memory query to be killed before continuing to run. This allows low-memory queries to always run, while more intensive queries can run when the server is idle, and resources are available. This behavior can be tuned at a [server and user](https://clickhouse.com/docs/en/operations/settings/memory-overcommit) level.

## 12. Issues relating to Materialized Views

[Materialized views ](https://clickhouse.com/docs/en/sql-reference/statements/create/view/#materialized-view)are a powerful feature of ClickHouse. By allowing the reorientation and transformation of data at insert time, users can optimize for specific queries. We often see users [using this technique](https://clickhouse.com/docs/en/guides/improving-query-performance/sparse-primary-indexes/sparse-primary-indexes-multiple#option-2-materialized-views) when more than a [single primary index ](https://clickhouse.com/docs/en/guides/improving-query-performance/sparse-primary-indexes/sparse-primary-indexes-multiple#options-for-creating-additional-primary-indexes)is required. There are a number of common issues with materialized views, probably sufficient for their own blog post. Summarizing the most common:

* We often see users misunderstanding how Materialized views work. They have no knowledge of the source table data and are effectively only triggers on inserts - capable of running over the inserted data block only. They have no visibility of merges, partition drop, or mutations. If users change the source table, they must, therefore, also update any attached materialized views - there is no functionality for keeping these in sync.
* Users add too many materialized views to a single table. These views aren’t free and must be run on each insert. More than 50 materialized views for a table is typically excessive and will slow inserts. As well as the compute overhead, each materialized view will create a new part from the block over which it runs - potentially causing the “Too Many Parts” issue discussed earlier. Note that performance can be improved by parallelizing the running of the views via the setting [`parallel_view_processing`](https://github.com/ClickHouse/ClickHouse/blob/06fe6f3c8b54898c744040a4f5f8929499cea8ca/src/Core/Settings.h#L430).
* [State functions](https://clickhouse.com/docs/en/sql-reference/aggregate-functions/combinators/#-state) are a compelling feature of ClickHouse and allow data to be summarized for later queries using [Aggregate functions](https://clickhouse.com/docs/en/sql-reference/data-types/aggregatefunction/). Materialized views with many of these, especially those computing quantile states, can be CPU intensive and lead to slow inserts.
* We often see users mismatching the columns of a target [aggregation](https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/aggregatingmergetree)/[summing](https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/summingmergetree/) merge tree with those of the materialized view. The ORDER BY clause of the target table must be consistent with the GROUP BY of the SELECT clause in the materialized view. Correct examples are shown below:

<pre style='background-color: #222222; border-radius: 8px; padding: 24px; color: #FFFFFF; display: flex; position: relative; white-space: pre-wrap;'>
<div style='color: #FFFFFF; margin-top: -24px; max-width: 98%;'>
CREATE MATERIALIZED VIEW test.basic
ENGINE = AggregatingMergeTree() PARTITION BY toYYYYMM(StartDate) ORDER BY (CounterID, StartDate)
AS SELECT
   CounterID,
   StartDate,
   sumState(Sign)    AS Visits,
   uniqState(UserID) AS Users
FROM test.visits
GROUP BY CounterID, StartDate;
</div>
</pre>
</p>

<pre style='background-color: #222222; border-radius: 8px; padding: 24px; color: #FFFFFF; display: flex; position: relative; white-space: pre-wrap;'>
<div style='color: #FFFFFF; margin-top: -24px; max-width: 98%;'>
CREATE MATERIALIZED VIEW test.summing_basic
ENGINE = SummingMergeTree
PARTITION BY toYYYYMM(d)
ORDER BY (CounterID, StartDate)
AS SELECT CounterID, StartDate, count() AS cnt
FROM source
GROUP BY CounterID, StartDate;
</div>
</pre>
</p>

* Similar to the above, the column names of the materialized view’s SELECT must match those of the destination table - do not rely on the order of the columns. Utilize alias to ensure these match. Note that the target table can have default values, so the view’s columns can be a subset of the target table. A correct example is shown below - note the need to alias `count() as counter`:

<pre style='background-color: #222222; border-radius: 8px; padding: 24px; color: #FFFFFF; display: flex; position: relative; white-space: pre-wrap;'>
<div style='color: #FFFFFF; margin-top: -24px; max-width: 98%;'>
CREATE MATERIALIZED VIEW
test.mv1 (timestamp Date, id Int64, counter Int64)
ENGINE = SummingMergeTree
ORDER BY (timestamp, id)
AS
SELECT timestamp, id, count() as counter
FROM source
GROUP BY timestamp, id;
</div>
</pre>
</p>

## 13. Experimental features in production

At ClickHouse, we regularly release new features. In some cases, new features are marked “experimental”, which means they would benefit from a period of real-world usage and feedback from the community. Eventually, these features evolve to the point of being deemed “production ready”, or deprecated if it turns out they are not generally useful or there is another way to achieve the original goal. While we encourage users to try out experimental features, we caution against building the core functionality of your apps around them or relying on them in production. For this reason, we require users to request these to be enabled on [ClickHouse Cloud](https://clickhouse.cloud/signUp) and understand the caveats and risks.

We label all features as experimental in our docs, and any usage requires the user to set a setting to enable a specific experimental feature, e.g. `SET allow_experimental_lightweight_delete = true`.

## Conclusion

If you've read this far you should be well prepared to manage a ClickHouse cluster in production - or at least avoid many of the common pitfalls! Managing ClickHouse Clusters with petabytes of data invariably brings its challenges, however, even for the most experienced operators. To avoid these challenges and still experience the speed and power of ClickHouse, try [ClickHouse Cloud](https://clickhouse.cloud/signUp) and [start a free trial now](https://clickhouse.cloud/signUp).
