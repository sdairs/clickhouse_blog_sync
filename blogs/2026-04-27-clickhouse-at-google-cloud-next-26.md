---
title: "ClickHouse at Google Cloud Next '26"
date: "2026-04-27T11:34:34.340Z"
author: "ClickHouse"
category: "Product"
excerpt: "Google Cloud Next is one of the biggest moments in the cloud calendar, and this year ClickHouse made a splash. Not just with a booth, house party and some swag, but a wave of product launches, integrations, and a deepening partnership with Google Cloud."
---

# ClickHouse at Google Cloud Next '26

Google Cloud Next is one of the biggest moments in the cloud calendar, and this year ClickHouse made a splash. Not just with a booth, house party and some swag, but a wave of product launches, integrations, and a deepening partnership with Google Cloud.

![image1.jpeg](https://clickhouse.com/uploads/image1_5f14217c2a.jpeg)

This post rounds up our biggest announcements and supporting launches that make ClickHouse a more native part of the Google Cloud ecosystem.

## ClickHouse Cloud on Google Axion {#clickhouse_cloud_on_google_axion}

Google Axion is Google's first custom ARM-based processor, built on ARM Neoverse V2 and offered through the C4A instance family. It represents a meaningful strategic investment from Google in custom silicon designed specifically for cloud-native workloads, with higher memory bandwidth and better performance per watt than comparable x86 offerings.

ClickHouse turns out to be a particularly good match for Axion. ClickHouse is built to push hardware as much as possible, and Axion instances don't flinch under that pressure. Where traditional processors can slow down when queries get heavy and sustained, Axion keeps consistent performance throughout. The result is that the speed gains compound in exactly the workloads where you need them most. The numbers bear this out. In our benchmark run in March 2026, ClickHouse Cloud on Axion took the #1 spot on [ClickBench](https://benchmark.clickhouse.com/) ranking across all systems and configurations. We saw 30-55% faster query performance and data load times cut roughly in half, from 64 seconds down to 26.

The migration to Axion is ongoing and will be transparent for existing customers. For the full technical breakdown, read the [dedicated Axion blog post](https://clickhouse.com/blog/google-axion).

## Query Google Cloud Lakehouse directly from ClickHouse {#query_google_cloud_lakehouse_directly_from_clickhouse}

The second major co-announcement at Google Next is our Lakehouse Runtime Catalog integration. Lakehouse Runtime Catalog is Google's unified metadata layer for Iceberg tables stored in Google Cloud Storage. With ClickHouse's new native integration, you can point ClickHouse directly at your Iceberg tables managed by Google's Lakehouse Runtime Catalog and query them as if they were native ClickHouse tables. No data movement, no duplication, no ETL pipeline to maintain.

Google is making sustained investments in GCS as an open data platform. Iceberg, Dataplex, and Lakehouse are the layers being built on top of it. ClickHouse's native support for this stack means you can use the right tool for the right job. Lakehouse Runtime Catalog for catalog management and governance, ClickHouse for fast, real-time analytical queries.

The integration uses ClickHouse's DataLakeCatalog engine with `catalog_type='biglake'`. You connect to the Lakehouse Runtime Catalog, and ClickHouse handles schema discovery automatically from the catalog.

You can learn more about the integration in our [dedicated blog post](https://clickhouse.com/blog/google-lakehouse-runtime).

## BYOC on the Google Cloud Marketplace {#byoc_on_the_google_cloud_marketplace}

For enterprise teams with specific data residency requirements, compliance constraints, or a strong preference for keeping compute inside their own GCP account, Bring Your Own Cloud (BYOC) is now generally available on the Google Cloud Marketplace.

BYOC lets you run ClickHouse's managed service while keeping your data and compute entirely within your own GCP account. ClickHouse manages the control plane, and you own the data plane. For many enterprise customers or organizations with hard data residency requirements, this is the preferred choice of deployment, and it's now available through the Marketplace. Which means you can apply existing GCP committed spend toward ClickHouse BYOC.

If your team has been evaluating ClickHouse Cloud on GCP but needed BYOC as a prerequisite to move forward, sign up on the Marketplace and learn more about this release in our [dedicated blog post](https://clickhouse.com/blog/byoc-gcp-ga).

## ClickHouse support for Google Antigravity {#clickhouse_support_for_google_antigravity}

Google Antigravity, Google's AI-native IDE, now has support for ClickHouse through its MCP server. This is part of ClickHouse's broader investment in the [Agentic Data Stack](https://clickhouse.com/ai).

Once connected via OAuth, you never have to orient yourself in your own data again. The agent automatically discovers your organizations, services, databases, and tables. You can ask natural language questions against massive data sets and get answers at ClickHouse speeds. The agent translates your intent into ClickHouse SQL, executes it, and returns structured results in the same conversation.

Going beyond chat, Antigravity generates interactive React-based charts as Artifacts, rendered live in the IDE's integrated browser. When you want to dig deeper into something you see in a chart, you can drag a box over it, leave a comment, and the agent responds to that visual context, queries ClickHouse again, and updates the Artifact in place.

This integration makes it really simple to embed a scalable real-time analytics solution inside your application. We're excited to see what (and how) our community builds with our new native integration for Antigravity. For the full walkthrough, read the [dedicated Antigravity blog post](https://clickhouse.com/blog/google-antigravity).

## GCS ClickPipes support for unordered mode {#gcs_clickpipes_support_for_unordered_mode}

We recently shipped support for unordered mode for our customers running large-scale data pipelines on Google Cloud Storage.

Our original GCS ClickPipes connector required files to arrive in lexicographical order. If you had a backfill, a retry, or late-arriving data with a filename that sorted earlier than already-processed files, those files would be silently skipped. For production pipelines, this is the kind of thing that can impact data quality.

Unordered mode eliminates that constraint entirely. Instead of polling the bucket every 30 seconds and looking for the next file in sequence, ClickPipes now listens for `OBJECT_FINALIZE` Pub/Sub notifications from GCS and processes any new file the moment it lands regardless of its name or order. Exactly-once semantics are guaranteed through a metadata store that tracks processing state across systems, so you don't have to worry about duplicates either.

You can read more about GCS in unordered mode in our [dedicated blog](https://clickhouse.com/blog/clickpipes-gcs-unordered-mode).

## What's coming next {#whats_coming_next}

We're just getting started and our partnership with Google Cloud is only getting stronger. Here's what you can expect later this year.

### Pub/Sub to ClickHouse Dataflow Template

For teams already running Pub/Sub pipelines, we're finalizing a new Dataflow template that brings ClickHouse in as a managed streaming destination. Built in collaboration with the Google Cloud team, it includes flexible windowing, dual dead-letter routing, and configurable write tuning so nothing gets silently dropped. This should be available very soon, stay tuned.

### ClickHouse Sink for Dataflow Job Builder

We're adding official Beam YAML support and a ClickHouse sink to Google's Dataflow Job Builder. Once available, you'll be able to visually assemble a pipeline in the Dataflow console and connect ClickHouse as the destination to any source you're already using. That includes GCP-native sources like BigQuery, GCS, Pub/Sub, and Spanner, or external sources like MySQL, Oracle, and Iceberg. View the [full list of supported sources](https://beam.apache.org/releases/yamldoc/current/).

### BigQuery CDC for ClickPipes

Earlier this year, we announced our [BigQuery ClickPipes in Private Preview](https://clickhouse.com/blog/bigquery-clickpipe-private-preview). Demand has been high, and we're looking to continue investing in this ClickPipe by providing Change Data Capture replication to ClickHouse. This will be a fully managed ClickPipes that captures changes from BigQuery tables in near real-time and lands them in ClickHouse. The same CDC experience we already offer for Postgres, MySQL, and MongoDB, extended to Google's flagship data warehouse.

### Google Cloud Pub/Sub ClickPipes

In addition to the Dataflow template, we're building a native Pub/Sub connector directly in ClickPipes. The Dataflow template and the ClickPipes serve different audiences: Dataflow gives you more control over windowing, transformations, and error routing, while the ClickPipes connector will offer a simpler, fully managed experience for teams that want ingestion from Pub/Sub to be as easy as any other ClickPipes.

### Private Service Connect for ClickPipes on Google Cloud

Many of our customers run their entire production workloads on GCP. For those that do, Private Service Connect has been a highly requested solution for secure, private connectivity between GCP-hosted data sources and ClickPipes. We're excited to be working on this solution and can't wait to make it available for our joint customers.

### Managed Postgres on GCP

Earlier this year, we [launched a managed Postgres service](https://clickhouse.com/blog/postgres-managed-by-clickhouse) in private preview around a simple idea: Postgres and ClickHouse are better together. NVMe-backed Postgres handles your transactions, ClickHouse handles your analytics, and native CDC replication keeps the two in sync in real time. We're excited to share that we're working on the infrastructure to support expansion into GCP later this year.

## Wrap-up {#wrap_up}

Beyond the product announcements, Google Cloud Next was a blast this year. It was amazing connecting with the broader Google community, getting face time with our customers, and letting loose at our [House Party with the Chainsmokers](https://clickhouse.com/houseparty/google-next). If you were there, you know. If you weren't, we can't wait to see you next year.

The conversations we had on the floor this week confirmed what we've been building toward. The way the data ecosystem is evolving, there's a real appetite for fast, open analytics deeply integrated into the Google Cloud ecosystem.


---

## Get started today

Interested in seeing how ClickHouse works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-515-get-started-today-sign-up&utm_blogctaid=515)

---