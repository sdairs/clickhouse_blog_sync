---
title: "MongoDB CDC to ClickHouse with Native JSON Support, now in Private Preview"
date: "2025-08-11T08:21:19.068Z"
author: "Joy Gao"
category: "Product"
excerpt: "Learn about the launch of the private preview of our MongoDB CDC connector in ClickPipes, ClickHouse Cloud’s native ingestion service."
---

# MongoDB CDC to ClickHouse with Native JSON Support, now in Private Preview

Today, we're excited to announce the private preview of the [MongoDB Change Data Capture (CDC) connector](https://clickhouse.com/cloud/clickpipes/mongodb-cdc-connector) in ClickPipes! This enables customers to replicate their MongoDB collections to ClickHouse Cloud in just a few clicks and leverage ClickHouse for blazing-fast analytics on document-based data. You can use this connector for both continuous replication and one-time loads from MongoDB, whether it's running on MongoDB Atlas or self-hosted instances.

The experience is natively integrated into ClickHouse Cloud through [ClickPipes](https://clickhouse.com/cloud/clickpipes), the built-in ingestion service of ClickHouse Cloud. This eliminates the need for external ETL tools, which are often expensive and time consuming to configure and manage. This connector is powered by [PeerDB](https://github.com/PeerDB-io/peerdb), maintaining our commitment to open source with no vendor lock-in.

> You can sign up to the private preview by following [this link.](https://clickhouse.com/cloud/clickpipes/mongodb-cdc-connector)

Following the rollout of our [Postgres](https://clickhouse.com/cloud/clickpipes/postgres-cdc-connector) and [MySQL](https://clickhouse.com/cloud/clickpipes/mysql-cdc-connector) CDC connectors, we've received high demand from customers for MongoDB CDC. The rise of modern applications built on MongoDB's flexible document model, combined with the need for real-time analytics on JSON-rich data, made this integration a natural next step in our ClickPipes roadmap.

<iframe width="768" height="432" src="https://www.youtube.com/embed/ZWM6xsaF23M?si=pZzvpGE0yCJmFQMe" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

## Purpose-built for MongoDB's Document Model and ClickHouse Analytics

MongoDB's document-oriented architecture generates rich, nested JSON data that traditional ETL tools may struggle to handle efficiently. Our MongoDB CDC connector is specifically designed to bridge the gap between MongoDB's flexible schema and ClickHouse's powerful columnar analytics engine.

The connector excels at handling MongoDB's native JSON capabilities, automatically mapping complex nested documents, arrays, and embedded objects into ClickHouse's [native JSON data type](https://clickhouse.com/blog/a-new-powerful-json-data-type-for-clickhouse), which recently went GA, while maintaining query performance and analytical flexibility.

## Key Features

The MongoDB CDC connector delivers enterprise-grade performance with features designed to handle the unique needs of document-based data replication:

**Unmatched Query Performance**: MongoDB excels at operational and transactional workloads with high throughput and low-latency, and ClickHouse excels at analytical workloads of any scale, delivering real-time, blazing-fast query performance. 

**Advanced JSON Data Type Support**: Seamlessly replicate MongoDB's rich document structures using ClickHouse's powerful native JSON data types to keep your operational and analytical systems in sync with low latency and high precision. The connector preserves document structure and enables high-performance analytical queries on semi-structured data, while optimizing compression and reducing storage cost.

**Blazing Fast Initial Load (Backfills)**: Replicate terabytes of existing data across multiple MongoDB collections to ClickHouse within a few hours. You can configure the number of parallel threads to migrate multiple tables simultaneously. Soon, we plan to support intra-table parallelism, using multiple threads to replicate  a single large table.

**Real-Time Change Streams for low-latency replication**: Leverages MongoDB's native [Change Streams](https://www.mongodb.com/docs/manual/changestreams/) feature to capture all document changes with latencies as low as a few seconds, ensuring your analytical data stays synchronized with your operational MongoDB database in near real-time.

**Built-in Monitoring and Alerting**: Full observability into replication health with metrics for document throughput, replication lag, failed operations, and Change Stream status, all integrated into ClickHouse Cloud's monitoring dashboard.

**No Vendor Lock-in**: The MongoDB CDC connector is powered by PeerDB, which is fully [open source](https://github.com/PeerDB-io/peerdb/). With the exception of the UI, all components are directly extended from the PeerDB open-source project, ensuring no vendor lock-in for our customers.

## MongoDB + ClickHouse: The Document Data Stack

The combination of MongoDB and ClickHouse creates a powerful architecture for modern applications that need both operational flexibility and analytical performance. MongoDB is ideal for the transactional workloads required by modern web and AI applications, while ClickHouse delivers unmatched analytics performance for the same applications, with data stored and queried in native, document-based JSON models.

![mongo-cdc-diagram-2.png](https://clickhouse.com/uploads/mongo_cdc_diagram_2_f6e8d30ba1.png)

This integration enables several key advantages:

**Operational and Analytical Workload Separation**: Keep your MongoDB clusters focused on serving mission-critical operational workloads, including high-throughput CRUD operations and efficient document lookups, while ClickHouse handles complex analytical queries, reports, and business intelligence workloads without impacting operational performance.

**Native JSON Analytics**: Query nested JSON documents using ClickHouse's advanced JSON functions and operators, enabling sophisticated, high-performance analytics on semi-structured data.

## How to sign up for Private Preview?

You can sign up for the Private Preview by filling out [the form on this page](https://clickhouse.com/cloud/clickpipes/mongodb-cdc-connector). Our team will reach out to you within a few days and work closely with you to provide early access. Given the anticipated demand, there may be a slight delay, but we'll ensure we connect with you as soon as possible.

The Private Preview entails no cost and is fully free. This is a great opportunity for you to get firsthand experience with the native MongoDB integration in ClickHouse Cloud and directly influence the roadmap. Looking forward to having you onboard!
