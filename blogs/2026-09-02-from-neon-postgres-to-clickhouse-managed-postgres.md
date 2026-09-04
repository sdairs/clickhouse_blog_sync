---
title: "From Neon Postgres to ClickHouse Managed Postgres"
date: "2026-09-03T11:40:38.135Z"
author: "Sai Srirampur"
category: "User stories"
excerpt: "Three teams share why they migrated production Postgres workloads from Neon to ClickHouse Managed Postgres and how ClickPipes helped them cut over in hours."
---

# From Neon Postgres to ClickHouse Managed Postgres

**TL;DR:** Over the past few months, a growing number of teams have migrated their production Postgres workloads from Neon to ClickHouse Managed Postgres. Their reasons vary, but common themes came up in our conversations: reliability issues under load, performance becoming less predictable as workloads grew, rising infrastructure costs, and network transfer fees. After migrating, these teams told us they saw improved reliability, faster and more consistent query performance, fewer operational issues, and lower costs. Each also completed the data migration in a matter of hours using [ClickPipes](https://clickhouse.com/docs/products/managed-postgres/migrations/clickpipes).

We spoke with three of these teams to learn more about their experience. They are at very different stages: [Shipsidekick](https://www.shipsidekick.com/) is an AI-powered logistics startup, [socialpruf.](https://socialpruf.com/) is a fast-growing real-time social intelligence platform, and [Infinitas Learning](https://www.infinitaslearning.com/) is one of Europe’s leading educational publishers. We asked each of them the same four questions. Here’s what they told us.

> "With exactly the same schema, our p99 Postgres query latency improved from seconds to single-digit milliseconds."
> 
> — Jerome van den Heuvel, Engineering Manager, Infinitas Learning

## What does your company do and how does Postgres support your product? {#what-does-your-company-do-and-how-does-postgres-support-your-product}

**Sawyer Bateman, Founder of Shipsidekick:** "We make shipping and warehousing seamless by connecting Shopify with logistics providers. Postgres powers everything—from our Next.js application on Vercel to our backend operations."

**Semyon Khlavich, Founder and CTO of socialpruf.:** "We turn social data into real-time insights for brands, talent agencies, and sports media companies. Postgres is our system of record, while ClickHouse powers our customer-facing analytics."

**Jerome van den Heuvel, Engineering Manager at Infinitas Learning:** "Infinitas Learning is one of Europe's largest educational publishers. Our Results & Insights team uses Postgres and ClickHouse to process and analyze exercises completed across our digital learning platforms."

Three different products, three different scales, but the same pattern underneath: Postgres is the system of record, and for two of the three, ClickHouse already sits next to it for analytics.

## What challenges did you experience with Neon? {#what-challenges-did-you-experience-with-neon}

The specifics differ, but the theme is the same. Neon worked well for these teams initially, but each encountered challenges as their workloads and production demands grew.

For **Shipsidekick**, it became a customer-facing problem. Sawyer told us: "Neon became a source of customer frustration. We experienced frequent crashes, outages lasting more than 10 minutes during peak hours, and connection pool exhaustion on shared gateways. Even at the maximum 16 compute units, CPU usage remained high and cache hit rates were low."

**socialpruf.** hit both reliability and cost limits as their data grew. In Semyon's words: "As we scaled to 100s of GB, Neon became unreliable and more expensive. Connection dropouts and restarts stalled our data pipelines and required manual intervention. On top of that, network transfer fees to ClickHouse grew to more than half our compute costs."

**Infinitas Learning** ran into a combination of operational and platform issues. Jerome:   
“We experienced several challenges with Neon:

* Support became slower and less responsive.  
* CPU and memory utilization increased without a clear explanation.  
* Neon's deprecation of its Azure regions required us to migrate.  
* Upgrading between major Postgres versions meant moving to an entirely new server.”

## What value have you seen since moving to ClickHouse Managed Postgres? {#what-value-have-you-seen-since-moving-to-clickhouse-managed-postgres}

Every team described the improvement as immediate, and it came from the platform change alone rather than from rewriting queries or schema.

**Shipsidekick:** "The difference was immediate: zero downtime, a 99% cache hit rate, and peak workloads using only around 10% CPU on similarly sized compute. We are paying less today, with room to downsize even further."

**socialpruf.:** "The impact was immediate: zero connection dropouts or restarts, around 30% faster queries overall, and up to 5× faster performance for some queries. One key query dropped from 42 ms to 22 ms. We also eliminated network transfer costs and now reliably handle thousands of concurrent connections with PgBouncer."

**Infinitas Learning:** "With exactly the same schema, our p99 Postgres query latency improved from seconds to single-digit milliseconds. We have also seen more reliable and predictable performance."

Two things are worth pulling out here. First, these results are consistent with the benefits of ClickHouse Managed Postgres’s architecture, which uses local NVMe storage to eliminate the network-attached storage bottleneck. That helps deliver faster and, just as importantly, more predictable query performance. Second, for teams already using ClickHouse for analytics, both systems now live on the same platform, so the network transfer fees for streaming changes from Postgres to ClickHouse simply go away.

## How did you approach the migration and what was the overall experience? {#how-did-you-approach-the-migration-and-what-was-the-overall-experience}

This was the part we were most curious about, because migration risk is usually what keeps teams on a platform they've outgrown. All three used [ClickPipes](https://clickhouse.com/docs/products/managed-postgres/migrations/clickpipes), which is built into ClickHouse Managed Postgres and handles schema migration, an optimized initial load using parallel snapshotting, and change data capture (CDC) to keep both databases in sync until cutover.

> "Our 750 GB database was migrated in under 16 hours. In comparison, migrating a smaller 250 GB database to Neon took three days and required significant manual intervention."
> 
> — Jerome van den Heuvel, Engineering Manager, Infinitas Learning

**Shipsidekick** followed the guide and cut over in a weekend. Sawyer: "The migration was fast and straightforward. We followed the Neon migration guide, moved our data in four to five hours using ClickPipes, and seamlessly cut over to ClickHouse Managed Postgres over the weekend."

**socialpruf.** first tried a manual approach before switching to ClickPipes. Semyon: "After native logical replication failed, the ClickHouse team helped us migrate 0.5 TB in just a few hours using ClickPipes. We kept both databases synchronized for a week, tested with database forks, and then completed a smooth production cutover."

**Infinitas Learning** had a direct comparison point from their earlier move onto Neon. Jerome: "The migration with ClickPipes was straightforward. We provisioned the server, created the schema, and used ClickPipes to transfer the data. Our 750 GB database was migrated in under 16 hours. In comparison, migrating a smaller 250 GB database to Neon took three days and required significant manual intervention."

> "After native logical replication failed, the ClickHouse team helped us migrate 0.5 TB in just a few hours using ClickPipes."
> 
> — Semyon Khlavich, Founder, socialpruf.

The common thread: the initial load finished in hours, CDC kept the target current while the team tested, and cutover happened on the team's own schedule.

## The migration path {#the-migration-path}

If you're considering the same move, here is the short version. The full [Neon to ClickHouse Managed Postgres migration guide](https://clickhouse.com/docs/products/managed-postgres/migrations/neon) has every step.

**1\. Prepare Neon.** Create a dedicated user with read and replication permissions, and enable logical replication under **Settings → Logical Replication** in the Neon console. Every replicated table needs a primary key or `REPLICA IDENTITY FULL`. If you use IP restrictions, allow the ClickPipes static IPs. The [Neon source setup guide](https://clickhouse.com/docs/integrations/clickpipes/postgres/source/neon-postgres) walks through this.

**2\. Migrate with ClickPipes.** From your Managed Postgres service in the ClickHouse Cloud console, go to **Data sources → Start import**, point it at Neon, and choose **Initial load + CDC**. ClickPipes migrates the schema to the empty target database, runs the parallel initial load, then keeps the target synchronized with Neon. You can watch per-table progress and replication lag in the console.

**3\. Cut over.** Once replication lag is near zero: stop writes on Neon, validate row counts and schema, reset sequences, and update your application's connection string. Keep Neon in read-only mode for a short while in case you need to roll back, then remove the ClickPipe and its replication slot.

A few things to keep in mind:

* **Branches.** Neon's copy-on-write branches are instant. In ClickHouse Managed Postgres, branches are independent deployments created via [point-in-time recovery](https://clickhouse.com/docs/products/managed-postgres/backup-and-restore), typically available within several minutes to tens of minutes depending on database size. Many teams keep a small development database with sanitized data and branch from that. See the [branching docs](https://clickhouse.com/docs/products/managed-postgres/branching).  
    
* **Neon Serverless Driver.** If your app uses `@neondatabase/serverless` (common on Vercel), replace it with a standard driver such as [node-postgres](https://node-postgres.com/). For many short-lived connections, use the [bundled PgBouncer](https://clickhouse.com/docs/products/managed-postgres/connection#pgbouncer), which runs in transaction pooling mode.  
* **Connection limits.** The default is 500 direct connections; PgBouncer supports up to 5,000 client connections, and `max_connections` can be raised in **Settings → Edit parameters**.  
* **Schema changes during migration.** CDC replicates inserts, updates, deletes, and `ADD COLUMN`. Other DDL (indexes, triggers, enum changes, constraints, functions) must be applied to the target manually before cutover. Keep the window between starting ClickPipes and cutting over short. The [migration FAQ](https://clickhouse.com/docs/products/managed-postgres/migrations/faq) covers the common errors.

## Get started {#get-started}

> "We are paying less today, with room to downsize even further."
> 
> — Sawyer Bateman, Founder, Shipsidekick

Sawyer, Semyon, and Jerome each described the move as fast and low-risk, and each is now running on faster, more predictable Postgres at lower cost.

If you’re considering a move from Neon, [ClickHouse Managed Postgres](https://clickhouse.com/cloud/postgres) is a few hours of work away. Our [migration guide](https://clickhouse.com/docs/products/managed-postgres/migrations/neon) will take you through the process and if you’d like help, [get in touch](https://clickhouse.com/company/contact) and we'll work through it with you.


---

## Get started with ClickHouse Managed Postgres today

Interested in seeing how ClickHouse Managed Postgres works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?intent=pg&loc=blog-cta-1758-get-started-with-clickhouse-managed-postgres-today-sign-up&utm_blogctaid=1758)

---