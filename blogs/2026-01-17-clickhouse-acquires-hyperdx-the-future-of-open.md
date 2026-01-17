---
title: "ClickHouse acquires HyperDX: The future of open-source observability"
date: "2025-03-06T16:43:41.988Z"
author: "The ClickHouse Team"
category: "Product"
excerpt: "ClickHouse acquires HyperDX to deliver the fastest, most cost-effective open-source observability with session replay, blazing-fast queries, and seamless OpenTelemetry support."
---

# ClickHouse acquires HyperDX: The future of open-source observability

![hyperdx_clickhouse.png](https://clickhouse.com/uploads/hyperdx_clickhouse_b85f02ef3e.png)

We are thrilled to announce that ClickHouse has acquired HyperDX, a fully open-source observability platform built on top of ClickHouse. This move reinforces our commitment to delivering the fastest, most cost-effective, and scalable observability platform to developers and enterprises worldwide. By integrating HyperDX's powerful UI and session replay capabilities with ClickHouse’s industry-leading database performance, we’re taking open-source observability to the next level.

## [Observability is a data problem](https://clickhouse.com/engineering-resources/best-open-source-observability-solutions)

[Observability](https://clickhouse.com/resources/engineering/what-is-observability) is fundamentally a data problem. The size of the dataset dictates how difficult and expensive it will be to build an observability platform. That’s why the choice of database is one of the most important decisions when starting an observability company or building an observability platform in-house. 

This is also why ClickHouse has been the backbone of observability platforms for years, powering logging, metrics, and tracing solutions at companies like [eBay](https://clickhouse.com/videos/monitorama-pdx-2024-distributed-tracing-all-the-warning-signs-were-out-there) and [Netflix](https://www.youtube.com/watch?v=HRh5setqGCU) or at observability startups like [Sentry](https://sentry.engineering/blog/introducing-snuba-sentrys-new-search-infrastructure) and [Instana](https://clickhouse.com/blog/ibm-instance-monitoring-clickhouse-performance). ClickHouse's disruptive storage efficiency literally flattens the cost curve, delivering 10x savings over traditional solutions, while blazing-fast query performance ensures engineers aren’t waiting on slow tooling to debug production issues. We wrote about this trend first in ["The State of SQL-Based Observability"](https://clickhouse.com/blog/the-state-of-sql-based-observability) and since then, it continued to gain steam in conversations with our customers and partners. 

However, a database alone doesn’t make an observability solution. Engineers need turnkey data ingestion and visualization, alerting, and other DevOps tooling that “just works”. Until now, ClickHouse has relied on [OpenTelemetry for data collection](https://clickhouse.com/blog/clickhouse-and-open-telemtry) and an [integration with Grafana for visualization](https://clickhouse.com/blog/clickhouse-grafana-plugin-4-0)—an approach that helped our own observability team move from an established SaaS solution to an internally-built [LogHouse](https://clickhouse.com/blog/building-a-logging-platform-with-clickhouse-and-saving-millions-over-datadog#performance-and-cost) achieving a staggering 200x cost reduction in the process. 

While this stack is still valid and delivers value (especially if a user has more than one observability store), we saw room for improvement, particularly in streamlining workflows, leveraging ClickHouse unique capabilities, and adding session replay, something existing open-source tools we looked at didn’t provide.

<blockquote style="font-size: 17px;">
<p>"ClickHouse’s analytics capabilities and open ecosystem make it a powerful technology for observability. However, the end-user experience lacked some of the comprehensive features of more established solutions. HyperDX is very exciting, bringing together an enhanced query experience with a more intuitive UI for exploratory observability workflows."</p>
<p style="font-style: normal; font-weight: bold;">Viktor Eriksson, Lovable</p>
</blockquote>

## Why HyperDX?

That’s when we found HyperDX—an open-source observability layer purpose-built on ClickHouse. HyperDX open-sourced their V2 UI in late 2024, and after testing it internally, we knew this was the missing piece. The setup was seamless, and our developers immediately saw the benefits. More importantly, we realized that our users deserved the same experience.

After speaking with the HyperDX team, it was clear we shared the same vision:

1. **Standards-Based Data Collection** – Both ClickHouse and HyperDX are committed to OpenTelemetry, with ClickHouse now maintaining the ClickHouse OpenTelemetry exporter.
2. **Open-Source First** – A robust observability stack should be available to everyone, with cloud offerings providing a simple, cost-effective operational experience.
3. **Flexible Data Access** – Users should have direct access to their observability data, with multiple ways to analyze it, and we remain deeply invested in Grafana as the best cross-data-source observability UI on the market.
4. **Blazing Fast Performance** – Query terabytes in seconds, making real-time troubleshooting seamless.

![output.gif](https://clickhouse.com/uploads/output_3efd2b01cf.gif)

## What’s Next?

This acquisition is an acceleration, not a disruption. The HyperDX team is joining ClickHouse to build the future of open-source observability. Here’s what to expect:

* **HyperDX Cloud** will continue serving and onboarding new customers.
* **The open-source project** remains actively maintained and developed.
* **Expanded roadmap** to bring even more powerful observability tools to engineers.

We’re thrilled about this next chapter and can’t wait to see how this partnership empowers our users and the broader open-source community.

If you're looking to try HyperDX, you can [get started for free on our cloud](https://www.hyperdx.io/register) or [self-host it on your own infrastructure](https://github.com/hyperdxio/hyperdx/tree/v2).

Sign up for our [newsletter](https://discover.clickhouse.com/newsletter.html) to receive updates on our joint roadmap together!
