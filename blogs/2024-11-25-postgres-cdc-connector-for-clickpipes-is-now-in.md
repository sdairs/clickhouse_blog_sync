---
title: "Postgres CDC connector for ClickPipes is now in Private Preview"
date: "2024-11-25T15:46:21.517Z"
author: "Sai Srirampur"
category: "Product"
excerpt: "We are excited to announce that the Postgres CDC connector for ClickPipes is now in Private Preview. This enables customers to replicate their Postgres databases to ClickHouse Cloud in just a few clicks, eliminating the need for external ETL tools, which "
---

# Postgres CDC connector for ClickPipes is now in Private Preview

![postgres-cdc-connector-clickpipes-private-preview.png](https://clickhouse.com/uploads/postgres_cdc_connector_clickpipes_private_preview_f06bd33c0b.png)

Today, we’re excited to announce the private preview of the Postgres Change Data Capture (CDC) connector in ClickPipes! This enables customers to replicate their Postgres databases to ClickHouse Cloud in just a few clicks and leverage ClickHouse for blazing-fast analytics. You can use this connector for both continuous replication and one-time migrations use cases from Postgres.

The experience is natively integrated into ClickHouse Cloud through ClickPipes, the integration engine designed to simplify moving massive volumes of data to ClickHouse. This eliminates the need for external ETL tools, which are often expensive, slow, and don’t scale for Postgres.

**[You can sign up to the private preview by following this link](https://clickhouse.com/cloud/clickpipes/postgres-cdc-connector)**.

Just a reminder, ClickHouse [joined forces](https://clickhouse.com/blog/clickhouse-welcomes-peerdb-adding-the-fastest-postgres-cdc-to-the-fastest-olap-database) with  PeerDB, a leading Change Data Capture (CDC) provider for Postgres, a few months ago. PeerDB already supports multiple enterprise-grade workloads and has helped replicate petabytes of data from Postgres to ClickHouse. Over the past few months, the team has worked hard to natively integrate PeerDB into ClickHouse Cloud. This announcement marks the first release of this integration, enabling users to seamlessly move data from Postgres to ClickHouse.

The Postgres CDC connector was built in close collaboration with several customers and design partners who are already running production-grade workloads. Here are a few customer testimonials:

>“PeerDB has been a game-changer for us, effortlessly migrating tens of terabytes from our Postgres warehouse into ClickHouse and keeping millions of daily orders synced with just seconds of latency. We're really excited about PeerDB's native integration into ClickHouse Cloud via ClickPipes and all of the opportunities it opens up for us.”  - **[SpotOn](https://www.spoton.com/)**


>“We already reduced our Postgres to ClickHouse snapshot times from 10+ hours down to 15 minutes with PeerDB. Combining ClickHouse’s powerful analytics natively with PeerDB’s real-time data capture capabilities will greatly simplify our data processing workflows. This integration will enable us to build analytical applications faster, giving us a competitive edge in the market.” - **[Vueling](https://www.vueling.com/)**
>

Without further ado, here is the demo of Postgres CDC connector in ClickPipes:

<iframe width="768" height="432" src="https://www.youtube.com/embed/fHuFSmafYUo?si=yEFblvI2MuUBadBO" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

## Postgres + ClickHouse, a powerful data stack

Using ClickHouse and PostgreSQL through a seamless CDC integration creates a powerful data stack by combining PostgreSQL's robust transactional capabilities with ClickHouse's high-performance analytics. CDC ensures real-time synchronization, allowing ClickHouse to handle fast queries on massive datasets without burdening PostgreSQL. This integration delivers real-time insights and scalable analytics, making it an ideal solution for modern, data-driven workflows. Below are a few main advantages of this architecture:

1. **Full workload isolation:** You can continue building your OLTP application on Postgres and your OLAP application on ClickHouse, with complete workload isolation—analytics will not affect your transactional workload.
    
2. **No compromises on features:** It also allows you to build your applications using the full capabilities and features (e.g., SQL coverage, performance, etc.) of both Postgres and ClickHouse, each optimized for a specific workload.

We believe customers derive the most value in solving real-world data problems by leveraging purpose-built databases like Postgres and ClickHouse as they were designed, with full flexibility, rather than relying on alternatives that retrofit one database engine into another, compromising the full feature set of each. We are observing a clear [trend](https://x.com/kiwicopple/status/1851638636590035054) towards the Postgres + ClickHouse architecture among real-world customers.

## Key Benefits of the Postgres CDC connector

The Postgres CDC connector in ClickPipes is purpose-built for Postgres and ClickHouse, ensuring a fast, simple and a cost effective replication experience. Here are some key benefits for customers:

### Blazing Fast Performance

With features like parallel snapshotting, you can achieve 10x faster initial loads, transferring terabytes of data in hours instead of days, and experience replication latency as low as a few seconds for continuous replication (CDC).

### Super Simple

You can start replicating your Postgres databases to ClickHouse in just a few clicks and minutes. Simply add your Postgres database as a source, select the specific tables/columns you want to replicate, and you're ready to go.

### Postgres and ClickHouse native features

This connector supports native Postgres features such as replication of schema changes, partitioned tables, built-in monitoring and alerting for replication slot size, and support for complex data types such as JSONB and ARRAYs, among others.

On the ClickHouse side, it supports features such as selecting specialized table engines, configuring custom order keys, choosing nullable columns, and so on during the replication process.

### Enterprise-grade security

At ClickHouse, security is a top priority, even before performance and features. We’ve extended the same level of security to the Postgres CDC connector in ClickPipes. It includes features such as SSH tunneling and Private Link to securely connect to your Postgres databases. Data in transit is fully encrypted using SSL.

### No vendor lock-in

The Postgres CDC connector is powered by PeerDB, which is fully open source [https://github.com/PeerDB-io/peerdb/](https://github.com/PeerDB-io/peerdb/). With the exception of the UI, we have ensured that all components are directly extended from the PeerDB open-source project. This underscores our commitment to open-source and ensures there is no vendor lock-in for our customers.

## How to sign up for Private Preview?

[![postgres-cdc-clickpipes-private-preview-signup.png](https://clickhouse.com/uploads/postgres_cdc_clickpipes_private_preview_signup_12c9afced9.png)](https://clickhouse.com/cloud/clickpipes/postgres-cdc-connector)

You can sign up for the private preview by filling out the form on [this page](https://clickhouse.com/cloud/clickpipes/postgres-cdc-connector). Our team will reach out to you within a day and closely collaborate with you to provide early access. The Private Preview entails no cost and is fully free. This is a great opportunity for you to get firsthand experience with the native Postgres integration in ClickHouse Cloud and directly influence the roadmap. Looking forward to having you onboard!

