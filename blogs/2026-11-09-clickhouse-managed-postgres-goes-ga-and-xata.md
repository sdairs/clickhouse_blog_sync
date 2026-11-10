---
title: "ClickHouse Managed Postgres goes GA and Xata acquisition brings agentic capabilities to the service"
date: "2026-11-09T16:56:11.397Z"
author: "Sai Srirampur"
category: "Product"
excerpt: "ClickHouse Managed Postgres, our NVMe-backed Postgres service natively connected to ClickHouse, is generally available, and we're acquiring Xata to add instant branching, cloning and scale-to-zero for developers and AI agents."
---

# ClickHouse Managed Postgres goes GA and Xata acquisition brings agentic capabilities to the service

Production-grade applications need a strong database foundation for predictable performance and always-on reliability. As AI agents help build and run software, that foundation also needs to support fully isolated, cost-effective environments that can be provisioned quickly and cloned instantly. With ClickHouse Managed Postgres, we’re building toward that future: **one complete Postgres experience, from the first experiment to production at scale.**

Today, we’re announcing the general availability of [**ClickHouse Managed Postgres**](https://clickhouse.com/cloud/postgres), our high-performance, enterprise-grade Postgres service, and the [**acquisition of Xata**](https://xata.io/blog/xata-is-joining-clickhouse) to expand the platform with instant branching, cloning, and serverless capabilities for developers and AI agents.

Over the past 10 months, our local NVMe-backed Postgres service has delivered up to 10× performance improvements and better reliability for customers. It now supports hundreds of production customers, from fast-growing AI-native startups to enterprises running multi-terabyte workloads, spanning both greenfield applications and migrations from Aurora, RDS, [Neon](https://clickhouse.com/blog/neon-to-clickhouse-managed-postgres), and more. Native CDC through [WalShadow](https://clickhouse.com/blog/introducing-walshadow) and ClickPipes, alongside extensions such as [`pg_clickhouse`](https://github.com/ClickHouse/pg_clickhouse), brings transactions and analytics together, powered by best-of-breed databases: Postgres and ClickHouse.

[Clay](https://www.clay.com/), one of the fastest-growing AI companies in the world, is already using ClickHouse Managed Postgres to power its next-generation platform.

> “ClickHouse Managed Postgres and WALShadow opens up a new way of thinking about databases at Clay. The raw speed of NVMe combined with low latency replication to ClickHouse allows us to build high throughput operational systems with massive scale real time visibility, unlocking experiences for customers that simply weren't possible in the past. We're currently powering our next generation platform with it at scale, and are looking forward to what comes next!”
>
> — Graham Cantor-Cooke, Principal Engineer, Clay Inc.

With Xata, we’re extending this strong foundation with agentic capabilities. Instant branches and clones, automatic idling, and scale to zero, powered by [Xatastor’s](https://xata.io/blog/xatastor-zfs-nvme-of-for-millions-of-postgres-databases) state-of-the-art copy-on-write storage, make it ideal for agents and developers to build, preview, and test features in isolated Postgres environments. With this acquisition, we are also welcoming world-class engineering talents led by Monica Sabru and Tudor Golubenco.

In the coming months, we’ll fully integrate Xata into ClickHouse Managed Postgres. Customers will get local NVMe-backed Postgres for mission-critical production workloads, tightly coupled with serverless Postgres for development workflows, agent sandboxing, and agent memory, all integrated with the ClickHouse database for world-class analytics.

Below is a testimonial from David AI, a joint customer of ClickHouse and Xata that migrated from Neon Postgres.

> “As an AI company working with large volumes of data, we need reliable infrastructure that help us move fast. We moved from Neon to ClickHouse Managed Postgres for better reliability and performance, and our users immediately noticed how much faster everything felt. Xata’s branching has been a great fit for our devs (and AI coding agents!), making it easy to build and test in parallel. Bringing both together means high-performance Postgres and instant branching in a single platform, simplifying our infrastructure and giving our team more time to build”
>
> — Jarrod Servilla, Platform Engineer, David AI

<iframe
  width="768"
  height="432"
  src="https://www.youtube.com/embed/HflbD1FW-eg"
  title="ClickHouse Managed Postgres Goes GA + Xata Acquisition"
  frameborder="0"
  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
  allowfullscreen>
</iframe>

## Available today: Fast, enterprise-grade Postgres unified with ClickHouse {#available_today}

### Local NVMe performance

Local NVMe-backed storage delivers [2–10X performance improvements](https://clickhouse.com/blog/postgresbench) for OLTP workloads.

> Note: Managed Postgres is generally available on AWS today. On [GCP it's in private preview](https://clickhouse.com/blog/postgres-managed-by-clickhouse-gcp-private-preview), with general availability coming soon.

### Postgres and ClickHouse, natively connected

[WalShadow](https://github.com/ClickHouse/walshadow/blob/main/docs/quickstart.md) consumes physical WAL for sub-second replication. ClickPipes offers a battle-tested alternative at no additional cost. With `pg_clickhouse`, applications can query ClickHouse through the Postgres interface, reducing migration effort and enabling federated queries across transactions and analytics.

Customers across all industries, including Infinitas Learning, Clay, and ShipSideKick, are seeing performance gains first hand, and benefiting from the unified Postgres and ClickHouse platform. Customers also benefit from the comprehensive [platform capabilities](https://clickhouse.com/docs/products/managed-postgres/overview) including:

* **High availability and reliability:** Up to two standbys across availability zones, automatic failover, automated backups, point-in-time recovery and more.
* **Connection management and read scaling:** Built-in PgBouncer connection pooling and dedicated read replicas.
* **Built-in observability:** Query Insights, ClickHouse Agents, logs, metrics, and a Prometheus endpoint.
* **Enterprise-grade security:** SAML/SSO, RBAC, IP allow-listing, private connectivity, and encryption at rest and in transit.
* **Infrastructure as code and automation:** OpenAPI, Terraform, and the ClickHouse CLI give developers and agents programmatic control.

All within ClickHouse Cloud, with a consistent experience across Managed Postgres and ClickHouse. Explore the [documentation](https://clickhouse.com/docs/products/managed-postgres/overview) for the full set of platform features and capabilities.

> With GA, the beta discount ends, and backup storage and public network egress become billable, as previously communicated to existing customers. We expect these additional charges to be modest for most customers. Pricing remains competitive, with native ClickHouse connectivity and ClickPipes replication included. See the [pricing calculator](https://clickhouse.com/pricing?service=postgres#pricing-calculator) for details.

## Coming next: Agentic capabilities, one complete Postgres experience {#coming_next}

Xata extends this production foundation with instant branches and clones, automatic idling, and scale to zero, powered by Xatastor’s copy-on-write storage. We plan to integrate these capabilities into ClickHouse Managed Postgres through two complementary paths.

> If you need instant branching and cloning today, we’re actively onboarding customers to Xata and can help you [get started](https://console.xata.io/signup).

**Instant branches and clones for local NVMe-backed Postgres.** Developers and agents will be able to build, preview, and test against isolated copies of production data, with automatic idling and scale to zero for these branch environments. These capabilities will be tightly coupled with NVMe-backed production Postgres, delivering **one unified experience within ClickHouse Cloud**. Workflows that customers such as David AI currently run across two separate platforms will become native to a single unified platform.

**A dedicated tier for agents.** A new tier within ClickHouse Managed Postgres will support agent sandboxing, agent memory, and agent-first workloads where elastic compute and ephemeral environments matter. Copy-on-write storage, instant branching and cloning, automatic idling, and scale to zero will make it economical to run millions of intermittently active Postgres environments.

Together, ClickHouse Managed Postgres will provide an end-to-end solution for developers to build, test, deploy, and scale AI-native applications, from POC to production faster. Stay tuned for updates as we bring these capabilities into ClickHouse Managed Postgres.

---

## Get started with ClickHouse Managed Postgres today

Interested in seeing how ClickHouse Managed Postgres works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?intent=pg&loc=blog-cta-2978-get-started-with-clickhouse-managed-postgres-today-sign-up&utm_blogctaid=2978)

---