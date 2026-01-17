---
title: "MongoDB CDC connector for ClickPipes is now in Public Beta"
date: "2026-01-13T14:56:03.889Z"
author: "Marta Paes"
category: "Product"
excerpt: "Replicate data from MongoDB into ClickHouse Cloud in just a few clicks for blazing-fast analytics on document-based data. Now with more connectivity options, improved reliability, and support for DocumentDB."
---

# MongoDB CDC connector for ClickPipes is now in Public Beta

## Summary

Replicate data from MongoDB into ClickHouse Cloud in just a few clicks for blazing-fast analytics on document-based data. Now with more connectivity options, improved reliability, and support for DocumentDB.

<p>The <a href="https://clickhouse.com/cloud/clickpipes">ClickPipes MongoDB CDC connector</a> is now in Public Beta! &#128640; </p>

After working with dozens of early access customers during Private Preview, we've added support for **sharded clusters** and **Amazon DocumentDB**, improved **reliability** for production workloads, and made it easier to **securely connect** to private MongoDB deployments.

Whether you're running a one-time migration or continuously replicating operational data for analytics, the connector delivers up to **100x faster queries** without the overhead of managing custom pipelines.

> [Sign up for ClickHouse Cloud](https://console.clickhouse.cloud/signup) today to try out the [MongoDB CDC connector for ClickPipes](https://clickhouse.com/cloud/clickpipes)!

<iframe width="768" height="432" src="https://www.youtube.com/embed/ZWM6xsaF23M?si=TlAAhBb7J5aav-pI" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

Here’s what our customers are saying:

>Before using ClickPipes, we relied on multiple tools to replicate MongoDB data into ClickHouse, many of which required constant maintenance or manual intervention. After switching to the MongoDB connector in ClickPipes, those issues disappeared: the initial setup was simple, and once configured, it required no ongoing attention. Using materialized views makes data modeling flexible and easy to evolve.
> 
> <br />
>Overall, ClickPipes has significantly reduced operational overhead and has worked great to replicate several terabytes of business data a day for analytical workloads. - <a href="https://www.rapidata.ai">Rapidata</a>

## What’s new in Public Beta?

### Broader platform compatibility

The MongoDB CDC connector initially launched with support for single [replica sets](https://www.mongodb.com/docs/manual/core/replica-set-members/). We’ve now extended support to [**sharded clusters**](https://www.mongodb.com/docs/manual/core/sharded-cluster-components/), enabling replication from common MongoDB topologies at any scale — whether you're running a single replica set or a distributed deployment with data spread across multiple shards.

We've also added compatibility with **Amazon DocumentDB**, a managed document database service that is API-compatible with MongoDB. See our [new integration guide](https://clickhouse.com/docs/integrations/clickpipes/mongodb/source/documentdb) for step-by-step instructions on how to configure DocumentDB for change stream replication.

### Secure connectivity options

To allow secure connections to MongoDB instances in private networks, which is a table stakes requirement for production environments, you can now configure both **AWS PrivateLink** and **SSH tunneling** when creating a new MongoDB ClickPipe. We've also added support for [X.509 certificate authentication](https://www.mongodb.com/docs/manual/core/security-x.509/), enabling **mutual TLS authentication** between the connector and your MongoDB deployment.

### Production-readiness

We've made significant improvements to reliability and observability based on Private Preview feedback. The connector now handles <strong>data type edge cases</strong> more gracefully (*e.g.* very large floats, dates outside the standard range) and uses enhanced error classification to <strong>automatically retry transient failures</strong> that would previously trigger unnecessary alerts.

<p>We've also refined the initial snapshot phase with smarter batching logic that measures uncompressed data size to <strong>prevent out-of-memory issues</strong>. This addresses the most significant operational issue we identified with large-scale deployments during early access: MongoDB's high JSON compression ratios caused batch sizes to balloon unexpectedly when decompressed during ingestion of very large collections. &#128165;</p>

## Main features

In addition to these Public Beta improvements, the MongoDB CDC connector provides several core capabilities designed to make real-time replication from MongoDB to ClickHouse Cloud reliable and performant:

### Real-time replication

The connector leverages MongoDB's native [Change Streams](https://www.mongodb.com/docs/manual/changestreams/) interface to capture all document changes with low latency, ensuring near real-time synchronization between MongoDB and ClickHouse Cloud. This combination creates a powerful architecture for modern applications that need both operational flexibility and analytical performance, with up to 100x faster analytics — we’re calling it the *Document Data Stack*.

![image1.png](https://clickhouse.com/uploads/image1_cba4cd460a.png)

Keep your MongoDB clusters focused on serving mission-critical operational workloads, including high-throughput CRUD operations and efficient document lookups, while ClickHouse Cloud handles complex analytical queries, reports, and business intelligence workloads without impacting upstream performance.

### Advanced JSON Support

To preserve MongoDB’s rich document structures and provide high-precision replication, the connector uses ClickHouse's powerful [native JSON data type](https://clickhouse.com/blog/a-new-powerful-json-data-type-for-clickhouse). This enables **high-performance** analytical queries on semi-structured data, at the same time o**ptimizing compression and reducing storage cost**.

### Fully managed experience

The connector is fully integrated into the ClickHouse Cloud experience. It provides **built-in metrics and monitoring** for visibility into replication health, **detailed logs** for error diagnosis and debugging, **in-place pipe editing**, and more.

## What’s next?

As we work towards General Availability (GA), we're focused on making the connector faster and more flexible for production workloads.

* **Parallel snapshot ingestion:** as is, the connector snapshots collections using a single thread, which can lead to a very long initial snapshotting phase. We’re evaluating (logical) partitioning strategies to improve initial load times for large collections.

* **Flattened mode:** we’ll add an option to automatically map top-level document fields to target columns. This will make it easier to model and query replicated data, while preserving schema evolution capabilities.

* **OpenAPI and Terraform support:** for teams managing infrastructure as code, MongoDB ClickPipes will also be available via Open API and Terraform, similar to other ClickPipe types.

**A note on billing:** usage of MongoDB CDC ClickPipes continues to be **free** until GA. Customers will be notified ahead of the GA launch to review and optimize their ClickPipes usage. You can estimate future costs by referring to [billing for Postgres CDC ClickPipes](https://clickhouse.com/docs/cloud/reference/billing/clickpipes).

## Getting started with the MongoDB CDC connector

The MongoDB CDC connector is available to new and existing ClickHouse Cloud customers, in all service tiers. To get started, navigate to the *Data Sources* tab in the ClickHouse Cloud console, configure the connection details for your MongoDB database, and you’re good to go! For step-by-step instructions, frequently asked questions, and gotchas, check out the [documentation for MongoDB ClickPipes](https://clickhouse.com/docs/integrations/clickpipes/mongodb).


---

## Try the MongoDB CDC connector today

Ready to accelerate analytics on MongoDB data? Try the MongoDB CDC connector today and experience a fully managed, native integration experience with ClickHouse Cloud - the world’s fastest analytics database.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-36-try-the-mongodb-cdc-connector-today-sign-up&utm_blogctaid=36)

---