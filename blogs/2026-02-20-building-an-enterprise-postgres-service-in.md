---
title: "Building an enterprise Postgres service in ClickHouse Cloud"
date: "2026-02-20T10:05:10.287Z"
author: "Sai Srirampur"
category: "Product"
excerpt: "We’ve been investing heavily in state-of-the-art features to ensure customers get an enterprise-grade Postgres experience."
---

# Building an enterprise Postgres service in ClickHouse Cloud

As we build [Postgres managed by ClickHouse](https://clickhouse.com/cloud/postgres), an NVMe-backed Postgres service native integrated with ClickHouse, our top priority (P0) is delivering an always-available, reliable, and operationally observable managed Postgres offering. We believe this is table stakes for OLTP workloads!

With that vision in mind, we’ve been investing heavily in state-of-the-art features to ensure customers get an enterprise-grade Postgres experience. In this blog, we highlight several key features we’ve shipped over the past few months and share a preview of what’s ahead on our roadmap to further strengthen platform maturity and enterprise readiness. Let’s get started!

## Cross AZ HA

Postgres managed by ClickHouse supports up to two synchronous standbys spread across availability zones, protecting you from node, rack, or full AZ failures. With 2 standbys configured, we use [quorum-based streaming replication](https://www.postgresql.org/docs/current/runtime-config-replication.html#GUC-SYNCHRONOUS-STANDBY-NAMES): a write is acknowledged when at least one standby confirms it. This provides strong durability guarantees, without turning every commit into a latency tax. In the event of a failure, failover is automatic, promoting a standby with minimal disruption.

![quorum-based streaming replication](https://clickhouse.com/uploads/552707022_938b77d4_1c8d_4fae_ab97_c0ed6edacee2_92b4642245.jpg)

For cost-sensitive workloads that require high availability, but aren’t tier 0, you have the flexibility to choose 1 cross-AZ standby. It uses synchronous replication to provide strong availability, while offering lesser fault tolerance than a two-standby quorum configuration.

> An important architectural nuance: our HA standbys are not exposed for reads, ensuring that we prioritize failover readiness and data durability over opportunistic read scaling.

HA standbys are reserved strictly for failover and are not exposed for read traffic. Read traffic on standbys can compete with WAL replay, increasing replication lag, and can delay failover readiness. Long-running queries on replicas can also interfere with VACUUM and bloat control on primary. We avoid those trade-offs by keeping standbys focused solely for HA. If you need read scaling, **we provide separate read replicas designed specifically for that purpose**. You can read more about how our HA

## Reliable CDC to ClickHouse (failover-safe slots)

The service comes with native ClickHouse integration with built-in Change Data Capture (CDC), enabling continuous replication of transactional data into ClickHouse for real-time analytics. The integration is powered by ClickPipes/PeerDB, a battle tested replication engine supporting 100s of Postgres customers.

> A unique reliability feature of the service is built-in failover replication slots, preventing resyncs on primary failover.

In most managed Postgres services, logical replication slots are tied to the primary instance. During high-availability failovers, maintenance events, or scaling operations, these slots can be lost or require manual recreation, interrupting CDC pipelines and potentially forcing full re-syncs.

Postgres by ClickHouse includes built-in infrastructure for failover replication slots when syncing data to ClickHouse. These slots are preserved across HA failovers and scaling operations. As a result, CDC pipelines continue running without manual intervention or slot re-creation when the primary changes, reducing the risk of costly resyncs on large databases.

## Backups, PITR and Forks

High availability protects you from infrastructure failures. Backups protect you from everything else.

Every Postgres service includes **automatic backups** with support for **point-in-time recovery (PITR)** and **forks**. We use **WAL-G**, a widely adopted open-source tool, to take full base backups and continuously archive WAL to object storage (S3-compatible). WAL-G is well tuned to perform full backups and restores, as well as WAL archival and retrieval, in parallel to meet the high throughput demands of large-scale workloads. We also use the [`wal-g` daemon](https://github.com/wal-g/wal-g/blob/master/docs/PostgreSQL.md#daemon), as it runs as a persistent process, eliminating per-WAL process startup overhead and enabling efficient, low-latency, and reliable WAL shipping under sustained write volumes.

<video autoplay="1" muted="1" loop="1" controls="0">
  <source src="https://clickhouse.com/uploads/backups_e_4d72767073.mp4" type="video/mp4" />
</video>


Continuous WAL archiving allows you to restore your database to an exact timestamp within the retention window (default 7 days), not just to the last snapshot. Forks are built on the same mechanism. You can create a new Postgres service from any recovery point, making it easy to test migrations, debug issues, or run backfills without impacting production.

Together with HA, backups provide a second layer of protection, covering not just infrastructure failures, but human error and application bugs as well.

## Zero compromise security

Postgres managed by ClickHouse is designed with practical, production-grade security controls across network access, encryption, and isolation.

> A key architectural differentiator is that **every Postgres cluster runs inside its own dedicated, isolated VPC.** 

This provides hard network-level isolation between customer environments, with no shared runtime and no cross-database interference. The result is strong blast-radius containment and reduced multi-tenant risk. While many managed database services rely on container orchestration platforms with shared networking layers, we provision dedicated environments per cluster to deliver a higher level of separation by default.

![dedicated, isolated VPCs](https://clickhouse.com/uploads/552707023_277c2c51_35a9_4343_9a77_77ee0d1edca1_14eec91d6a.jpg)

At the network layer, access can be restricted using [IP allow-listing](https://clickhouse.com/docs/cloud/managed-postgres/security#ip-whitelisting), ensuring that only approved application servers, VPN endpoints, bastion hosts, or CI/CD systems can connect to the database.

All data is [encrypted](https://clickhouse.com/docs/cloud/managed-postgres/security#encryption) both in transit and at rest. Client connections are secured with TLS (SSL) to protect against interception and man-in-the-middle attacks. Encrypted connections can be strictly enforced, and for environments requiring stronger authentication guarantees, certificate-based client verification can be used. Data at rest, including NVMe storage and object storage used for backups and WAL archives,  is encrypted using AES-256, the industry-standard encryption algorithm widely adopted across cloud providers. Encryption keys are securely managed by the underlying cloud infrastructure.

For environments requiring stronger network isolation, [Private Link support](https://clickhouse.com/docs/cloud/managed-postgres/security#private-link) enables private connectivity between your VPC and the Postgres service, ensuring that database traffic does not traverse the public internet.

## Monitoring

The Postgres service comes with built-in, out-of-the-box metrics that provide visibility into both system health and database performance. Today, it includes 10+ core metrics, allowing you to monitor CPU usage, memory consumption, disk I/O, storage growth, and network traffic, alongside Postgres-specific signals such as connections, transaction throughput, cache hit ratios, row activity, and deadlocks.

<video autoplay="1" muted="1" loop="1" controls="0">
  <source src="https://clickhouse.com/uploads/monitoring_e_47a46f2b86.mp4" type="video/mp4" />
</video>

We’re actively expanding operational visibility, including Query Performance Insights and more comprehensive logging.

## Looking Ahead

As we execute on **our vision of delivering a unified data stack for OLTP and OLAP by combining Postgres and ClickHouse**, providing an enterprise-grade experience is a given!

In the coming quarters, we’re expanding the platform’s enterprise readiness across reliability, performance, and operational depth. A few features include support for additional cloud providers (GCP), CDC v2 for close to sub-second replication into ClickHouse, and Query Performance Insights (QPI) for deeper visibility into query behavior and database internals.

We’re also investing in core platform capabilities such as storage autoscaling, OpenAPI and Terraform support for IaC, one-click fully managed Postgres-to-Postgres migrations, improved operational visibility (e.g., scaling progress), a built-in intuitive SQL console and more.

Stay tuned.

---

## Try Postgres managed by ClickHouse

ClickHouse + Postgres has become the unified data stack for applications that scale. With Managed Postgres now available in ClickHouse Cloud, this stack is a day-1 decision.

[Get access](https://clickhouse.com/cloud/postgres?loc=blog-cta-71-try-postgres-managed-by-clickhouse-get-access&utm_blogctaid=71)

---