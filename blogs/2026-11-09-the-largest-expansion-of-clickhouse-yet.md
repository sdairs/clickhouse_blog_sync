---
title: "The largest expansion of ClickHouse yet"
date: "2026-11-09T23:27:47.419Z"
author: "ClickHouse"
category: "Product"
excerpt: "ClickHouse Managed Postgres is generally available, ClickHouse Observability enters public beta, ClickHouse Security launches in private preview, Langfuse introduces an open-source AI Gateway, and ClickHouse acquires Xata."
---

# The largest expansion of ClickHouse yet

Today, we're announcing the largest expansion of the ClickHouse platform since the launch of ClickHouse Cloud, introducing new capabilities across transactions, observability, security, and AI engineering.

ClickHouse now serves more than 5,000 customers, including DoorDash, Ramp, Meta, Tesla, Cisco, and Visa. What began as an open-source analytical database has grown into a foundation for some of the world's most demanding data workloads. Now, we're bringing together purpose-built offerings that help developers build, observe, and secure modern applications with the performance, scale, and cost efficiency ClickHouse is known for.

Today's announcements include:

* [**ClickHouse Managed Postgres general availability and Xata acquisition**](https://clickhouse.com/blog/managed-postgres-ga-xata-acquisition): A fully managed, high-performance PostgreSQL service with low-latency, native ClickHouse integration. The acquisition of [Xata](https://xata.io/), the agent-native Postgres company, accelerates our roadmap for instant branching, cloning, and scale-to-zero environments for developers and AI agents.  
* [**ClickHouse Observability, launching in public beta**](https://clickhouse.com/blog/announcing-clickhouse-observability): A fully managed observability offering that lets teams ingest, retain, and investigate high-volume telemetry without sacrificing data fidelity.  
* [**ClickHouse Security, launching in private preview**](https://clickhouse.com/blog/introducing-clickhouse-security-agentic-siem): An agentic SIEM built on technology from our acquisition of RunReveal, combining large-scale security data management with AI-powered investigations.  
* [**Langfuse AI Gateway, launching in public beta**](https://langfuse.com/gateway): An open-source gateway that gives platform and finance teams greater visibility and control over AI usage, performance, and costs.

AI is fundamentally changing the demands placed on data infrastructure. Applications and agents are generating more queries, more data, and increasingly unpredictable workloads, raising the bar for performance and scale across every system. From transactions and analytics to observability, security, and AI engineering, developers need purpose-built technologies that can meet these demands without adding complexity and cost. We're expanding ClickHouse to bring these capabilities together on an open, composable foundation built for performance, scale, and cost efficiency.

## Build: ClickHouse Managed Postgres is now generally available, with Xata acquisition accelerating its agentic roadmap

[ClickHouse Managed Postgres is now generally available in ClickHouse Cloud](https://clickhouse.com/blog/managed-postgres-ga-xata-acquisition), bringing together two foundational databases for modern applications: PostgreSQL for transactions and ClickHouse for real-time analytics. Together, they give developers a powerful foundation for building data-intensive applications that require both transactional and analytical capabilities, without the complexity of managing separate integration infrastructure.

Built on NVMe-backed storage, ClickHouse Managed Postgres provides a fully managed, high-performance PostgreSQL database with native change data capture into ClickHouse, continuously replicating data with sub-second latency. The `pg_clickhouse` extension also allows developers to query analytical data in ClickHouse through a standard PostgreSQL interface. The service includes high availability and automated backups.

The acquisition of Xata accelerates the roadmap for ClickHouse Managed Postgres, bringing technology for instant database branching and cloning, along with elastic, scale-to-zero environments. These capabilities will enable developers to create isolated Postgres environments for development and testing, while also laying the foundation for a dedicated tier designed for AI agents, supporting agent sandboxing, agent memory, and other agent-first workloads.

Building on this foundation, customers are already seeing the benefits of bringing transactional and analytical workloads together. Clay, the AI-powered go-to-market platform, is powering its next-generation platform at scale with ClickHouse Managed Postgres.

“Clickhouse Managed Postgres and WALShadow opens up a new way of thinking about databases at Clay. The raw speed of NVMe combined with low latency replication to ClickHouse allows us to build high throughput operational systems with massive scale real time visibility, unlocking experiences for customers that simply weren't possible in the past. We're currently powering our next generation platform with it at scale, and are looking forward to what comes next\!”

– Graham Cantor-Cooke, Principal Engineer, Clay Inc.

## Observe: Introducing ClickHouse Observability, now in public beta

Today, we're [launching ClickHouse Observability in public beta](https://clickhouse.com/blog/announcing-clickhouse-observability), bringing a fully managed observability offering to ClickHouse Cloud.

ClickHouse Cloud is already used to power demanding observability workloads today, taking advantage of its ability to ingest, store, and query large volumes of data quickly and cost-efficiently, thus allowing engineers to diagnose issues faster while unlocking agentic SRE workloads. 

ClickHouse Observability turns that proven architecture into a fully managed cloud offering. Teams can ingest logs, metrics, traces, and session data through OpenTelemetry, investigate telemetry at scale, and retain full-fidelity high-cardinality data for longer without the cost trade-offs that have historically forced organizations to sample, drop, or aggressively expire data, which has created blind spots and prevented SRE agents from identifying the root cause of issues.

As infrastructure and applications become more complex, including those powered by AI agents, engineers need to understand behavior across models, tools, services, and infrastructure. ClickHouse Observability provides visibility into application and infrastructure, while Langfuse helps teams trace, evaluate, and improve AI models and agents.

The underlying architecture is already proven at scale. Mercado Libre, Latin America's leading commerce and fintech platform, processes approximately 400 million spans per minute using ClickHouse for observability, achieving 75x faster queries and roughly 89% compression, significantly improving its infrastructure efficiency.

[Read Mercado Libre's story](https://clickhouse.com/blog/mercado-libre-observability-on-clickhouse-cloud)

## Secure: ClickHouse Security, now in private preview, brings an agentic SIEM to ClickHouse Cloud

We're also [introducing ClickHouse Security](https://clickhouse.com/blog/introducing-clickhouse-security-agentic-siem), now available in private preview, bringing an agentic security information and event management (SIEM) offering to the ClickHouse platform.

Built on technology from our September acquisition of RunReveal, ClickHouse Security combines the analytical performance and scale of ClickHouse with security-specific data integrations, detections, and AI-powered investigations.

Security teams are dealing with more data than ever: cloud audit logs, identity events, endpoint telemetry. Legacy SIEM wasn’t built for this volume of data or for the way AI is changing security operations. The result is most security teams struggle with basic data problems and their security operations have not evolved in over a decade. ClickHouse Security, now in private preview, is the agentic SIEM  built for the next decade of scale.

Agents are part of the platform, not an add-on. Native AI agents triage alerts, query the underlying logs, and write their findings and reasoning back to the case, working from the same normalized data security teams use. Security teams can also investigate in natural language through native AI chat, asking follow-up questions to dig deeper into an alert without writing traditional queries. Teams that want to go further can build their own agentic workflows for threat hunting, detection coverage, and more with the LLM of their choice.

The foundational data management work is also built in. ClickHouse Security, built on technology from RunReveal and integrated with ClickHouse Cloud, runs on the database built for large-volume, low-latency workloads. It connects over one hundred cloud, identity, and SaaS sources through first-party integrations, so data arrives normalized and ready for investigation. Built-in pipelines filter, route, and enrich logs before they’re stored, so there’s no separate pipeline layer to buy or manage. Managed detections and custom detections-as-code cover common threats from day one.

For teams already running ClickHouse, security data can now sit alongside observability and analytics data instead of being copied into a separate SIEM.

## AI Engineering: Langfuse launches open-source AI Gateway to give teams visibility and control over usage and spend

Today, Langfuse is launching its new [open-source AI Gateway in public beta](https://langfuse.com/gateway), giving developers greater visibility and control over AI usage and spending.

Langfuse, the open-source AI engineering platform ClickHouse acquired in January, is one of the most widely adopted in the space with 35k+ GitHub stars and 90M+ package downloads per month. Teams at 21 of the Fortune 50 and leading AI-native businesses like Merck, Ramp, Hugging Face, and Canva trace, evaluate, and improve AI applications and agents with Langfuse.

As AI applications and coding agents spread across organizations, many teams lack a clear picture of which models are being used, by whom, for what purposes, and at what cost.

Developers, platform, and finance teams need visibility into model requests, token consumption, costs, output quality, and how agents interact with models and tools.

Traditionally, capturing this information requires instrumenting applications and integrating tracing libraries directly into application code.

The new Langfuse AI Gateway makes this significantly easier.

By routing model requests through Langfuse AI Gateway, organizations can automatically trace AI usage and costs with zero code changes. This makes it easier to get started with AI observability and take advantage of broader capabilities for evaluating and improving AI applications and agents.

The Langfuse AI Gateway is built in Rust to ensure high performance and reliability, and is available self-hosted or on Langfuse Cloud.

## One open, composable foundation for data-intensive applications

These launches mark a major step in the evolution of ClickHouse, bringing together the technologies developers need to build, observe, and secure modern applications on a high-performance, open, and composable foundation.

Each new product addresses a distinct need: Postgres for transactions, ClickHouse Observability for application and infrastructure monitoring, ClickHouse Security for threat detection and investigation, and Langfuse for AI engineering, now with an AI Gateway for managing model visibility and usage.

Customers are already expanding their use of ClickHouse across multiple workloads. [Physical Intelligence](https://www.pi.website/), among them, is bringing general-purpose AI into the physical world.

“Building robotics foundation models means making sense of billions of annotations and telemetry records,” says Karan Dhabalia, Engineer at Physical Intelligence. “We started with ClickHouse for observability, then expanded into real-time analytics, Postgres, and AI development with Langfuse. This shared foundation simplifies operations and helps our researchers develop better models. With ClickHouse Security now in private preview, we’re excited to see the platform grow.”

— Karan Dhabalia, Engineer, Physical Intelligence

As AI agents drive more intensive and unpredictable data workloads, we're continuing to invest in technologies that help developers build, observe, and secure their applications at scale.

And with Xata joining ClickHouse, we're extending that foundation toward a future where AI agents can provision their own database environments, develop and test applications, and interact with data more autonomously.

## Get started

* ClickHouse Managed Postgres: Generally available in ClickHouse Cloud. [Get started](https://console.clickhouse.cloud/signUp?intent=pg&loc=postgres-managed-by-clickhouse-hero&glxid=445ab576-f16e-488c-a74a-1a9aecf1b470&pagePath=%2Fcloud%2Fpostgres&origPath=%2Fclickstack&experiments=mktg-hero-signup-card%3A0&utm_ga=GA1.1.20817310.1774892807)  
* ClickHouse Observability: Available in public beta. [Try the beta](https://console.clickhouse.cloud/signUp?intent=o11y&loc=blog-cta-2921-try-clickhouse-observability-now-in-public-beta-sign-up&glxid=445ab576-f16e-488c-a74a-1a9aecf1b470&pagePath=%2Fblog%2Fannouncing-clickhouse-observability&origPath=%2Fclickstack&utm_ga=GA1.1.20817310.1774892807)  
* ClickHouse Security: Available in private preview. [Request access](https://clickhouse.com/security#request-access)  
* Langfuse AI Gateway: Available in public beta. [Explore the Gateway](https://langfuse.com/blog/introducing-gateway)


---

## Get started today

Interested in seeing how ClickHouse works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-2987-get-started-today-sign-up&utm_blogctaid=2987)

---