---
title: "Postgres at Open House NYC"
date: "2026-10-13T15:35:19.448Z"
author: "Sai Srirampur and Kaushik Iska"
category: "Product"
excerpt: "At Open House NYC, we showed how ClickHouse Managed Postgres and ClickHouse work as one stack, with a live WalShadow demo replicating Postgres into ClickHouse in under a second, plus the same-week Google Cloud and chdb extension launches."
---

# Postgres at Open House NYC

Last month, we took the stage at [ClickHouse Open House NYC](https://clickhouse.com/openhouse/nyc-2026) to share what we've been building toward for a while: **Postgres for transactions, ClickHouse for analytics, as one integrated stack.** It was a busy week for the team. [We launched WalShadow in private preview](https://clickhouse.com/blog/introducing-walshadow), opened the [Google Cloud private preview of ClickHouse Managed Postgres](https://clickhouse.com/blog/postgres-managed-by-clickhouse-gcp-private-preview), and [released the `chdb` Postgres extension](https://clickhouse.com/blog/introducing-chdb-postgres).

## Postgres in the Open House keynote {#postgres_in_the_open_house_keynote}

On stage in the opening keynote, we walked through the Managed Postgres story, introduced [WalShadow](https://github.com/ClickHouse/walshadow), and followed it with a live demo under a heavy write burst. Below is a recap of what we shared on stage and what shipped around it.

[Watch our segment of the Open House NYC keynote](https://www.youtube.com/watch?v=w31j77m-zm8&t=1442s) (starts at 24:02).

<iframe width="768" height="432" src="https://www.youtube.com/embed/w31j77m-zm8?start=1442" frameborder="0" allowfullscreen></iframe>

## Postgres and ClickHouse, together {#postgres_and_clickhouse_together}

We started with a pattern we see over and over again. Teams build their application on Postgres, then add ClickHouse as growing data volumes slow down their dashboards and analytical queries. Postgres handles transactions, ClickHouse handles analytics, and each database does the job it's built for. Thousands of companies run exactly this stack.

![](https://clickhouse.com/uploads/openhousenyc_oct2026_image1_363eec1e27.png)

The journey itself isn't new. What's new is how quickly AI-native companies move through that journey. We sampled ten of our thousand-plus AI-native customers using Postgres ClickPipes and found that their data volumes had grown by more than 1,000% in just six months. They're hitting the analytics wall faster than any other customer category we've seen, creating demand for best-in-class solutions to handle both their transactional workloads and their analytics.

Helping teams connect these two databases is a personal story for us, too. We co-founded PeerDB to make replicating data from Postgres into ClickHouse easy. ClickHouse [acquired PeerDB](https://clickhouse.com/blog/clickhouse-welcomes-peerdb-adding-the-fastest-postgres-cdc-to-the-fastest-olap-database) in 2024, and today PeerDB powers the Postgres CDC connector in ClickPipes, used by more than a thousand customers.

## ClickHouse Managed Postgres {#clickhouse_managed_postgres}

That's the idea behind [ClickHouse Managed Postgres](https://clickhouse.com/cloud/postgres): we now run both sides of the stack in ClickHouse Cloud and make them work together natively. In the keynote we focused on three things:

- **Postgres on local NVMe storage.** Disks are physically attached to the VM, which gives 2x to 10x better performance for transactional workloads, with high availability across zones (up to two standbys), backups, read replicas, a Prometheus endpoint, Terraform, and ClickHouse Agents.
- **Native CDC into ClickHouse.** Sync tables from Postgres to ClickHouse in a few clicks, without building and running your own pipelines.
- **[pg_clickhouse](https://github.com/ClickHouse/pg_clickhouse).** An open-source extension that lets you query ClickHouse from Postgres, so your application can use a single Postgres interface for both transactions and analytics.

## WalShadow: sub-second replication from physical WAL {#walshadow_sub_second_replication_from_physical_wal}

Then came the big announcement. Until now, the standard way to replicate Postgres into ClickHouse was ClickPipes or PeerDB, both built on Postgres logical replication. [WalShadow](https://clickhouse.com/blog/introducing-walshadow) takes a different path.

![](https://clickhouse.com/uploads/openhousenyc_oct2026_image2_1468b04f40.png)

WalShadow is an open-source engine that replicates Postgres into ClickHouse from the **physical WAL**, the same stream a Postgres streaming replica consumes. Instead of asking the source database to decode changes through a logical replication slot, WalShadow decodes the WAL outside the source, builds ClickHouse-native blocks, and inserts them in parallel. A schema-only shadow Postgres instance tracks the live catalog, so schema changes like `ADD COLUMN`, `RENAME COLUMN`, `DROP COLUMN`, and `CREATE TABLE` flow through. In effect, ClickHouse becomes an analytical physical standby.

This one is bittersweet for us, because the benchmark we showed on stage compares WalShadow with PeerDB, the project we created. On modest 8-vCPU instances:

- **Latency:** around 200 ms from commit in Postgres to visible in ClickHouse, compared with around 10 seconds for PeerDB. For reference, a native Postgres physical replica came in at around 50 ms.
- **Throughput:** around 300,000 rows per second, keeping pace with the source's insert rate. PeerDB sustained about 120,000.

The full methodology is in the [announcement post](https://clickhouse.com/blog/introducing-walshadow).

There are two ways to try it:

1. **Open source.** The [GitHub repository](https://github.com/ClickHouse/walshadow) has a Docker quick start, the architecture docs, and the benchmark harness, so you can reproduce the numbers yourself. It supports Postgres 17, and 18.
2. **Private preview on ClickHouse Managed Postgres.** A fully managed experience, set up in a few clicks. It's exclusive to ClickHouse Managed Postgres because WalShadow needs access to the physical WAL, which most managed Postgres services don't expose. Because we run both sides of the stack, we can wire it directly into the Postgres replication layer. [Sign up for the private preview](https://clickhouse.com/cloud/postgres/walshadow).

### The demo

Kaushik then showed WalShadow running on ClickHouse Managed Postgres. The demo instance had been processing roughly 170 million transactions in the past hour, close to 50,000 per second, at under 50% CPU. Built-in Query Insights, powered by the open-source [pg_stat_ch](https://github.com/ClickHouse/pg_stat_ch) extension, showed per-query statistics streaming into ClickHouse.

When you click "Sync to ClickHouse," you now get two options: ClickPipes, which still works for RDS and other Postgres providers, or WalShadow for Managed Postgres. With WalShadow, there's no publication or logical replication slot to configure on the primary. You pick the tables and columns, choose initial load plus CDC or CDC only, and start.

Since we were in New York, the scenario was a trading platform: Postgres takes the trades, and ClickHouse runs the micro-aggregations that catch market manipulation. At around 45,000 to 50,000 trades per second, WalShadow kept ClickHouse under 400 ms behind. Then Kaushik triggered a simulated manipulation burst with 10x the load. The WalShadow-fed pipeline flagged the anomaly in under 500 ms. The ClickPipes-fed one took more than 15 seconds. When every second of fraud costs money, that gap matters.

Want a closer look? Here's our WalShadow launch video:

<iframe width="768" height="432" src="https://www.youtube.com/embed/RK0yBeK2OPw" frameborder="0" allowfullscreen></iframe>

## ClickHouse Managed Postgres on Google Cloud (private preview) {#clickhouse_managed_postgres_on_google_cloud}

One of the most common questions we've heard since launching on AWS is "When can I run this on Google Cloud?" Now you can. [ClickHouse Managed Postgres is in private preview on GCP](https://clickhouse.com/blog/postgres-managed-by-clickhouse-gcp-private-preview).

It's the same service: Postgres on [GCP Local SSD](https://cloud.google.com/compute/docs/disks/local-ssd), native CDC into ClickHouse Cloud over in-region ClickPipes, and pg_clickhouse, all inside Google Cloud. That means no cross-cloud hop between your transactional and analytical data. You can deploy in any GCP region where ClickHouse Cloud runs, and provision with the console, the OpenAPI, Terraform (`cloud_provider = "gcp"`), or `clickhousectl`.

If you're coming from Cloud SQL or AlloyDB, [Postgres to Postgres ClickPipes](https://clickhouse.com/blog/clickpipes-postgres-to-postgres) gives you a low-downtime migration path, and our team works hands-on with preview customers. We're keeping the preview small, so [join the GCP waitlist](https://clickhouse.com/cloud/postgres#gcp-waitlist).

## chdb Postgres extension: fast imports from cloud storage {#chdb_postgres_extension}

The third launch is for anyone who loads data into Postgres from object storage. The [chdb extension](https://clickhouse.com/blog/introducing-chdb-postgres) brings the [chDB](https://clickhouse.com/docs/chdb) engine, the embeddable ClickHouse engine, to Postgres imports and exports.

It ships as two pieces: a `chdb` extension with a `chdb_query()` function, and a `chdb_hook` module that extends `COPY` to read from and write to S3, Google Cloud Storage, Azure Blob Storage, HDFS, HTTP, and local files:

<pre><code type='click-ui' language='sql'>
LOAD 'chdb_hook';
COPY times FROM 's3://datasets-documentation/my-test-bucket-768/some_prefix/some_file_1.csv';
</code></pre>

Because it builds on ClickHouse, it reads and writes a wide range of [ClickHouse formats](https://clickhouse.com/docs/reference/formats/index), including Parquet, Avro, ORC, Arrow, and Protobuf.

In our benchmark importing the NYC Taxi dataset from S3, it was the most consistent of the four extensions we tested, while the two DuckDB-based extensions took around 2 to 3x as long for CSV, JSON, and Parquet. chdb runs the engine in a short-lived helper process rather than inside the Postgres backend, so it only uses resources while a command is running.

It's open source on [GitHub](https://github.com/ClickHouse/pg_chdb), and included with pg_clickhouse on ClickHouse Managed Postgres.

## What's next {#whats_next}

WalShadow in particular has started some great conversations, including a feature in [Postgres Weekly #665](https://postgresweekly.com/issues/665).

As we said on stage, WalShadow is one big step toward unifying Postgres and ClickHouse, and it won't be the last. Our goal hasn't changed: world-class Postgres, natively integrated with ClickHouse, so you get the best of OLTP and OLAP in one data stack.

A big thank you to everyone who came to Open House NYC and stopped by to talk Postgres, and to the events team who made the day run so smoothly. See you at the next one!

---

## Get started with ClickHouse Managed Postgres today

Interested in seeing how ClickHouse Managed Postgres works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?intent=pg&loc=blog-cta-2584-get-started-with-clickhouse-managed-postgres-today-sign-up&utm_blogctaid=2584)

---