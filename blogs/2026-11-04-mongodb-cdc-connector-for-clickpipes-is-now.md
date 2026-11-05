---
title: "MongoDB CDC connector for ClickPipes is now generally available"
date: "2026-11-04T18:53:42.765Z"
author: "Marta Paes"
category: "Product"
excerpt: "The MongoDB CDC connector for ClickPipes is now generally available, with parallel snapshotting, structured ingestion into typed columns, lag and resource metrics, and Terraform and OpenAPI support."
---

# MongoDB CDC connector for ClickPipes is now generally available

## Summary

Replicate data from MongoDB into ClickHouse Cloud in just a few clicks for blazing-fast analytics on document-based data. Now with parallel snapshotting, structured ingestion mode, and programmatic configuration (Cloud API, Terraform).

When we set out to develop a CDC connector for MongoDB, it felt like an instant home run: the semi-structured nature of documents was a perfect fit for ClickHouse’s native JSON data type, ClickHouse’s columnar architecture delivered up to 100x faster analytical queries, and continuous replication with [ClickPipes](https://clickhouse.com/cloud/clickpipes) meant you could now get insights from your operational MongoDB data in seconds, not hours.

But a new CDC connector is *never* an instant home run. Someone will reshard their MongoDB cluster during business hours. Someone will bulk-delete a few billion documents to enforce a retention policy. Someone will swear a field can never be null. After moving **over 1.5PB** of data for **hundreds of production customers** and hitting all sorts of edge cases, we’re ready to announce that the MongoDB CDC connector is now Generally Available!

> *We replaced our Fivetran-based batch pipeline with MongoDB ClickPipes, streaming 250 collections across multiple MongoDB clusters directly into ClickHouse Cloud. The refactor of our data analytics platform to use ClickPipes and ClickHouse Cloud reduced data latency by over 90%. That gives Cue, our AI platform for frontline hiring, fresh data to help customers make hiring and workforce decisions in minutes* - Nate Polek, Staff Data Engineer, [Fountain](https://clickhouse.com/blog/fountain-agentic-ai-for-high-volume-hiring)

[*Sign up for ClickHouse Cloud*](https://console.clickhouse.cloud/signup) *today to try out the [MongoDB CDC connector for ClickPipes](https://clickhouse.com/cloud/clickpipes)!*

![](https://clickhouse.com/uploads/mongodb_cdc_ga_nov2026_architecture_de47492075.png)

The connector leverages MongoDB's native [Change Streams](https://www.mongodb.com/docs/manual/changestreams/) interface to capture all document changes with low latency, ensuring near real-time synchronization between MongoDB and ClickHouse Cloud. This combination creates a powerful architecture for modern applications that need both operational flexibility and analytical performance, and allows you to keep your MongoDB clusters focused on serving mission-critical operational workloads while ClickHouse Cloud handles complex analytical queries, reports, and business intelligence workloads.

## What’s new in GA? {#whats_new_in_ga}

### Parallel snapshotting for faster initial loads and resyncs

Snapshotting is a critical operation to guarantee data consistency in CDC pipelines, but it often means processing and ingesting hundreds of GBs of documents from a production cluster. You want it to be *fast*, so you get up and running and recover from failure *fast*, but have as little impact as possible upstream.

Until now, the MongoDB CDC connector snapshotted each collection using a single thread, which could make the initial load of large collections painfully long. That’s all behind us now: ClickPipes **automatically** chunks each collection into ranges based on the document ID (`_id`) and distributes the work to make your snapshots *fast* by default.

![](https://clickhouse.com/uploads/mongodb_cdc_ga_nov2026_parallel_snapshotting_b840c05c46.png)

And because real-world collections rarely grow evenly over time, ClickPipes samples each collection to pick balanced partition boundaries, so you get the same speedups even if your data arrives in bursts or as a big backfill.

### Structured ingestion mode

MongoDB's document-oriented model produces rich, nested data that traditional ETL tools often struggle to untangle. By default, MongoDB CDC ClickPipes replicate documents into ClickHouse's native JSON data type, preserving their original structure while ensuring high-performance analytical queries, efficient compression, and full flexibility as schemas evolve. That’s great if you want flexibility over convenience, but it offloads the work of flattening schemas and extracting fields to you.

With GA, you now have the option to let ClickPipes do that work for you. Structured ingestion samples your collection, infers a schema, and maps **top-level document fields** to typed ClickHouse columns at ingestion time. The result is a regular, strongly-typed table that you can query without casting or extracting fields, with some additional magic to handle documents that don’t fit the inferred schema.

#### Example: new JSON fields

Fields that are not included in the initial schema are replicated into a `_peerdb_malformed_data` JSON column, keyed by field name and flagged as `"unexpected_field": true`, so you can access the values before adding a new column to the target table without a backfill.

<pre><code type='click-ui' language='json'>
{
  "year": {
    "unexpected_field": true,
    "value": 2019
  }
}
</code></pre>

#### Example: type mismatches

Values that don't match the inferred type aren’t dropped. Instead, these values are stored in the `_peerdb_malformed_data` JSON column, keyed by field name and flagged as `"type_mismatch": true`, so you can still query them and fix the data at the source.

<pre><code type='click-ui' language='json'>
{
  "year": {
    "type_mismatch": true,
    "value": "two thousand nineteen"
  }
}
</code></pre>

In the future, we will support more complex flattening (*i.e.,* beyond top-level fields) as we continue to evolve the MongoDB CDC connector. 

### More control for production environments

Because MongoDB is schemaless, it introduced different challenges in supporting some of the same features we offer across our other CDC connectors. To bring the MongoDB CDC connector feature set closer to that of Postgres and MySQL CDC, this GA launch includes:

* **Target table configuration:** with structured ingestion, MongoDB collections land as regular, well-typed ClickHouse tables instead of a single JSON column. This means the ClickPipe creation flow now offers the same granular table configuration for MongoDB as for other CDC sources: exclude fields you don't need, partition the target table for easier operations, and choose sorting keys that match your query patterns.

* **Delete handling:** when a document is deleted, MongoDB only sends the `_id` of the document, by default, so deletes can't be matched to rows in tables that are partitioned or sorted by fields other than the primary key. To prevent this, you can now enable [pre-images](https://www.mongodb.com/docs/manual/reference/method/db.collection.watch/#std-label-db.collection.watch-change-streams-pre-and-post-images-example) per collection to include the full document values in delete events. If you routinely purge data from MongoDB to enforce retention, you can now also filter out deletes at the source and keep the full history in ClickHouse.

### Improved observability for easier troubleshooting

Although the connector has been fully integrated into the ClickHouse Cloud experience from the get-go, CDC ClickPipes was underdeveloped on the observability side: debugging a slow CDC pipe used to mean some level of guessing, or filing a support ticket to find out whether the bottleneck was upstream in MongoDB, downstream in ClickHouse, or somewhere in between.

For GA, we have extended the **built-in metrics and monitoring** to also report on **resource utilization** and **lag**. The following metrics are now available in the ClickPipes UI and the [ClickHouse Cloud Prometheus endpoint](https://clickhouse.com/docs/integrations/clickpipes/monitoring):

#### Resource utilization

You can now independently investigate scenarios where CDC ClickPipes might need to be scaled (*e.g.* during snapshotting or traffic bursts), rule out resource saturation as a root cause for replication lag, and other basic troubleshooting workflows.

![](https://clickhouse.com/uploads/mongodb_cdc_ga_nov2026_resource_utilization_557935a570.png)

* **CPU usage:** cores consumed against the allocation for all CDC ClickPipes in the service, *or how much compute the pull and push processes are using right now*.
* **Memory usage:** memory consumed against the allocation for all CDC ClickPipes in the service, *or how much RAM the pull and push processes are holding onto right now*.
* **Network receive bandwidth:** inbound throughput on the pipe, *or how much data is being pulled from the source per second*.

#### Replication lag

It's now also easier to understand the freshness of your data, and whether delays in replication are on the source side, ClickHouse side, or in between.

![](https://clickhouse.com/uploads/mongodb_cdc_ga_nov2026_replication_lag_376403b9d6.png)

* **Source lag:** how far behind the pull process is from MongoDB’s Change Streams API, *or the time between a change happening in MongoDB and ClickPipes pulling it*.
* **Destination lag:** how long it takes pulled changes to land in ClickHouse, *or the time between a change being pulled and being queryable at the destination.*
* **End-to-end lag:** the sum of both metrics above, *or total time from a change happening in MongoDB to it showing up in ClickHouse*.

### Terraform and OpenAPI support

ClickOps (*i.e.* clicking buttons in a user interface) is useful for onboarding, but teams wrangling production deployments require standard tooling like Terraform to provision and manage resources in a safe, deterministic, and version-controlled way. Like other ClickPipes types, MongoDB CDC ClickPipes can be managed using [Open API](https://clickhouse.com/docs/integrations/clickpipes/programmatic-access/openapi) and [Terraform](https://clickhouse.com/docs/integrations/clickpipes/programmatic-access/terraform) ([v3.14.0+](https://github.com/ClickHouse/terraform-provider-clickhouse/releases/tag/v3.14.0)). If you’d like to bring your existing ClickPipes under source control, follow the steps in [this blogpost](https://clickhouse.com/blog/terraform-ga#how-to-import-existing-clickpipes) to import these resources into your Terraform state.

---

Getting the last touches on the MongoDB CDC connector to make it GA-ready took more dev work than we can fit in a blogpost (and even external contributions; shoutout to **Abhash Solanki** for [his work on pre-image replication for delete events](https://github.com/PeerDB-io/peerdb/pull/4844) 🫡). If you’re curious to go more granular, we encourage you to point your agent at the [PeerDB repo](https://github.com/PeerDB-io/peerdb) for a complete overview of changes.

## Pricing {#pricing}

As part of this transition, billing for MongoDB CDC ClickPipes is now active as of November 4, 2026 and will be reflected in the next billing cycle for your ClickHouse Cloud account. The connector has a predictable pricing model based on data volume, with a fixed compute cost per service that is shared across all CDC ClickPipes of *any* type. The MongoDB CDC connector is **5-10x more cost-effective** than using third-party ETL tools, reflecting our commitment to offering ClickPipes as a seamless and affordable option to connect ClickHouse Cloud and your various data sources. For more details, see the [ClickPipes billing documentation](https://clickhouse.com/docs/products/cloud/reference/billing/clickpipes/clickpipes-for-cdc).

## Getting started with the MongoDB CDC connector {#getting_started_with_the_mongodb_cdc_connector}

The MongoDB CDC connector is available to new and existing ClickHouse Cloud customers, in all service tiers. To get started, navigate to the *Data Sources* tab in the ClickHouse Cloud console, configure the connection details for your MongoDB cluster, and you’re good to go! 

[Watch on YouTube](https://youtube.com/watch?v=3i13I4V5QIs)

For step-by-step instructions, frequently asked questions, and gotchas, check out the [documentation for MongoDB ClickPipes](https://clickhouse.com/docs/integrations/clickpipes/mongodb).

---

## Try the MongoDB CDC connector today

Ready to accelerate analytics on MongoDB data? Try the MongoDB CDC connector today and experience a fully managed, native integration experience with ClickHouse Cloud - the world’s fastest analytics database.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-2875-try-the-mongodb-cdc-connector-today-sign-up&utm_blogctaid=2875)

---