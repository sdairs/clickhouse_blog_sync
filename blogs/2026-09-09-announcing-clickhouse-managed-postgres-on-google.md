---
title: "Announcing ClickHouse Managed Postgres on Google Cloud"
date: "2026-09-10T05:32:31.996Z"
author: "Kunal Gupta"
category: "Product"
excerpt: "ClickHouse Managed Postgres is expanding to Google Cloud, bringing NVMe-backed storage, native CDC into ClickHouse, and a unified query layer via pg_clickhouse to GCP private preview customers."
---

# Announcing ClickHouse Managed Postgres on Google Cloud

**TL;DR:** ClickHouse Managed Postgres is now available in Private Preview on Google Cloud. It is the same fully managed, NVMe-backed Postgres service we launched on AWS earlier this year, with native CDC into ClickHouse and a unified query layer via pg_clickhouse, now running inside GCP. Access is limited during the preview, so [sign up for the GCP waitlist](https://clickhouse.com/cloud/postgres#gcp-waitlist) and our team will reach out to get you onboarded.

When we [launched ClickHouse Managed Postgres](https://clickhouse.com/blog/postgres-managed-by-clickhouse) in April, we said we would expand beyond AWS to other cloud providers, starting with GCP. Since then, the service has moved to [public beta](https://clickhouse.com/blog/postgres-managed-by-clickhouse-beta), with hundreds of customers now running multi-terabyte production workloads. 

Along the way, one request has come up more than almost any other: **"When can I run this on Google Cloud?"** Many of the teams talking to us already run ClickHouse Cloud on GCP, or have their transactional data in Cloud SQL and AlloyDB. They want the same unified data stack, Postgres for transactions and ClickHouse for analytics, without leaving GCP.

Today, we are opening the Private Preview of ClickHouse Managed Postgres on Google Cloud.



Before we get into the details, here’s a quick demo of ClickHouse Managed Postgres on GCP:

<video autoplay="1" muted="1" loop="1" controls="0">
  <source src="https://clickhouse.com/uploads/GCP_Final_web_0b7a31c06b.mp4" type="video/mp4" />
</video>

## Why this matters for teams on Google Cloud {#why_this_matters_for_teams_on_google_cloud}

The architecture we have been building toward is simple: Postgres for OLTP, ClickHouse for OLAP, with continuous replication between the two and a single query layer on top. That pattern is already followed by thousands of companies, and it is the foundation AI-native applications are converging on, where agent-driven workloads need answers from both the transactional and analytical side of the stack.

Until now, teams on GCP could get half of that natively. ClickHouse Cloud has run on Google Cloud for years, and earlier this year we brought [ClickPipes natively to GCP](https://clickhouse.com/blog/open-house-2026-day-1#user-content-clickpipes) with in-region ingestion and Private Service Connect support. The Postgres side, however, still had to live on AWS or on a third-party provider, which meant cross-cloud replication, egress costs, and two sets of networking and compliance to manage.

With ClickHouse Managed Postgres on GCP, the whole stack sits inside Google Cloud:

- [**Postgres on local NVMe**](https://clickhouse.com/blog/postgres-managed-by-clickhouse), in the same GCP region as your application and your ClickHouse Cloud service  
- **Native CDC into ClickHouse** over GCP-native networking, with no cross-cloud hop  
- [**pg_clickhouse**](https://clickhouse.com/docs/products/managed-postgres/extensions/pg_clickhouse/introduction) so your application can query both engines through a single Postgres connection

![](https://clickhouse.com/uploads/managed_postgres_gcp_sep2026_image1_7afa326329.png)

## What you get in the private preview {#what_you_get_in_the_private_preview}

The GCP service is built on the same architecture as the AWS service, here is what it looks like on Google Cloud.

### NVMe-backed Postgres, on GCP local SSD

The performance story is the same one that has defined this service from day one. Most managed Postgres offerings run on network-attached storage, which adds a network round-trip to every disk access. ClickHouse Managed Postgres runs on [GCP Local SSD](https://cloud.google.com/compute/docs/disks/local-ssd), NVMe storage physically attached to the VM running your database. Disk latency drops from milliseconds to microseconds, IOPS stop being the ceiling, and the workloads that suffer most on network storage (heavy updates, vacuums, WAL spikes, tail latency under load) get the largest gains.

### Native integration with ClickHouse Cloud on GCP

Every service comes with the two integration features that make this a unified data stack rather than two databases side by side:

- [**Postgres to ClickHouse replication**](https://clickhouse.com/docs/products/managed-postgres/overview)**.** Sync your Postgres tables to ClickHouse Cloud in a few clicks using the [Postgres CDC connector in ClickPipes](https://clickhouse.com/docs/integrations/clickpipes/postgres/index). Initial load plus continuous CDC, with replication latency measured in seconds. With ClickPipes now running natively in GCP, replication stays in-region.  
- [**pg_clickhouse**](https://clickhouse.com/docs/products/managed-postgres/extensions/pg_clickhouse/introduction)**.** The [open-source Postgres extension](https://github.com/ClickHouse/pg_clickhouse) that lets Postgres act as a unified query layer, pushing filters, joins, aggregations and more down to ClickHouse. Build applications that span transactions and analytics without managing two connections in your code.

### Enterprise-grade, from the first service

The Private Preview includes the managed-service features you expect for production workloads:

- [High availability](https://clickhouse.com/docs/products/managed-postgres/high-availability) with two standbys across zones, using quorum-based replication  
- [Automatic backups with point-in-time recovery and forks](https://clickhouse.com/docs/products/managed-postgres/backup-and-restore)  
- [Read replicas](https://clickhouse.com/docs/products/managed-postgres/read-replicas) for read-heavy workloads  
- [Connection pooling with PgBouncer](https://clickhouse.com/blog/pgbouncer-clickhouse-managed-postgres)  
- [90+ Postgres extensions](https://clickhouse.com/docs/products/managed-postgres/extensions)  
- Integrated monitoring, logs and [Query Insights](https://clickhouse.com/blog/postgres-query-insights-clickhouse-cloud)  
- [ClickHouse Agents](https://clickhouse.com/blog/clickhouse-agents-managed-postgres) for exploring and tuning your Postgres data in plain English  
- [Scheduled upgrades](https://clickhouse.com/blog/introducing-scheduled-upgrades-in-clickhouse-managed-postgres) for platform upgrades and Postgres patches

### Infrastructure as code

GCP is a first-class provider across the automation surface. The [OpenAPI](https://clickhouse.com/docs/products/managed-postgres/openapi) create endpoint accepts `gcp` as the provider, and the [Terraform provider](https://clickhouse.com/docs/products/managed-postgres/terraform) accepts it in `cloud_provider`:

```hcl
resource "clickhouse_postgres_service" "example" {
  name           = "my-postgres-gcp"
  cloud_provider = "gcp"
  region         = "us-central1"
  size           = "<size>"
  ha_type        = "async"
}
```

You can also provision from the [`clickhousectl` CLI](https://clickhouse.com/docs/concepts/features/interfaces/cli):

<pre><code type='click-ui' language='bash'>
clickhousectl cloud postgres create \
  --name my-pg \
  --provider gcp \
  --region us-central1 \
  --size c4-standard-4 \
  --pg-version 18
</code></pre>

## Migrating from Cloud SQL, AlloyDB, or anywhere else {#migrating_from_cloud_sql_alloydb_or_anywhere_else}

Several of our beta customers came to us from Cloud SQL. If your Postgres is already on GCP, [Postgres to Postgres ClickPipes](https://clickhouse.com/blog/clickpipes-postgres-to-postgres) gives you a fully managed, low-downtime migration path: continuous replication from your existing database, automated schema migration, and a cutover you control. The same workflow applies whether you are coming from Cloud SQL, AlloyDB, RDS, Aurora, Neon, or self-managed Postgres.

Our team works hands-on with Private Preview customers on migrations, so you do not have to plan the move alone.

## What to expect during the private preview {#what_to_expect_during_the_private_preview}

We are deliberately keeping the GCP preview small so that we can work closely with each team and learn what they need before opening it up more broadly. A few things to know:

- **Access is by invitation from the waitlist.** [Sign up](https://console.clickhouse.cloud/signUp?intent=PG), and our team will reach out to discuss your workload and [get you access](https://clickhouse.com/cloud/postgres#gcp-waitlist).  
- **Available in every GCP region where ClickHouse Cloud runs.** You can deploy Postgres in any of the [GCP regions supported by ClickHouse Cloud](https://clickhouse.com/docs/cloud/reference/supported-regions#google-cloud-regions), so it can sit right next to your existing ClickHouse Cloud service.  
- **A wide range of compute and storage configurations.** Choose from Local SSD-backed machine shapes spanning small development instances to storage-heavy production clusters, so you can size for your workload rather than fit it to a fixed tier.  
- **Feature parity is the goal.** The GCP service runs the same stack as AWS. Where a feature is not yet available on GCP, we will tell you up front and share when it is coming.

Your feedback during this period directly shapes the roadmap, the same way the AWS private preview did for the features we shipped in beta.




## Get started {#get_started}

ClickHouse Managed Postgres on Google Cloud is in Private Preview today.

If you are on AWS, you do not need to wait. ClickHouse Managed Postgres is in [public beta on AWS](https://clickhouse.com/blog/postgres-managed-by-clickhouse-beta) today. [Sign up for ClickHouse Cloud](https://console.clickhouse.cloud/signUp?intent=PG) to provision your first NVMe-backed Postgres service.

To learn more, visit the [ClickHouse Managed Postgres](https://clickhouse.com/cloud/postgres) page or jump into the [documentation](https://clickhouse.com/docs/cloud/managed-postgres).

---

## Get started with ClickHouse Managed Postgres today

Interested in seeing how ClickHouse Managed Postgres works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?intent=pg&loc=blog-cta-1905-get-started-with-clickhouse-managed-postgres-today-sign-up&utm_blogctaid=1905)

---