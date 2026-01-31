---
title: "Monitoring Temporal Cloud with ClickStack"
date: "2026-01-28T14:25:05.781Z"
author: "The ClickStack Team"
category: "Product"
excerpt: "Learn how ClickStack integrates with Temporal Cloud to deliver fast, scalable observability for high-cardinality metrics, helping you spot bottlenecks, debug failures, and understand workflow health in minutes."
---

# Monitoring Temporal Cloud with ClickStack

When your mission-critical workflows span days, weeks, or even months, every data observability data point counts. That's why we're excited to announce the integration between [ClickStack](https://clickhouse.com/use-cases/observability) and [Temporal Cloud's OpenMetrics endpoint](https://docs.temporal.io/cloud/metrics/openmetrics/), bringing high performance observability to your durable execution platform.

![temporal_dashboard.png](https://clickhouse.com/uploads/temporal_dashboard_ed1d16163e.png)

## What is Temporal?

Temporal is a durable execution platform that helps developers build reliable applications. Temporal lets you focus on business logic rather than writing complex error handling, retry logic, and state management code to survive failures.
Your business logic runs as a Temporal Workflow, whether that means processing payments, orchestrating agents, or managing long-running shopping cart experiences. If a server crashes, the network fails, or a service goes down, Temporal automatically recovers and resumes execution exactly where it left off. No lost progress, no orphaned processes.

### What is ClickStack?

[ClickStack](https://clickhouse.com/docs/use-cases/observability/clickstack/getting-started) is a cloud-native observability stack built on ClickHouse for high-performance storage and querying of logs, metrics, and traces. It’s designed for teams dealing with large volumes of telemetry and high-cardinality data, where traditional observability platforms either fall over or become cost-prohibitive.

ClickStack focuses on horizontal scalability, efficient compression, and predictable query performance, even as data volumes grow into the petabyte range. It’s commonly used for log analytics, operational monitoring, and deep investigation of production systems where ingestion rate and retention really matter.

---

## Get started with ClickStack

Explore the ClickHouse-powered open source observability stack built for OpenTelemetry at scale.

[Get started](https://clickhouse.com/o11y?loc=blog-cta-46-get-started-with-clickstack-get-started&utm_blogctaid=46)

---

ClickStack consists of:

* **HyperDX UI**, a purpose-built frontend for exploring and visualizing observability data
* **A custom-built OpenTelemetry Collector**, with an opinionated schema for logs, metrics, and traces
* **ClickHouse**, the high-performance analytical database at the core of the stack

[Watch on YouTube](https://youtube.com/watch?v=WBe7ZwTRWuQ)


## Why ClickStack and Temporal Cloud belong together

Running Temporal at scale means managing potentially thousands of concurrent workflows, each with its own activities, timers, and state transitions. When something goes wrong, or when you need to optimize performance, you need to be able to navigate the wealth of observability information coming out of the system.

This is where ClickStack helps. Built on ClickHouse, ClickStack handles the high cardinality metrics that Temporal generates with ease. ClickStack processes queries across Task Queues, Workflow Types, and Namespaces in milliseconds, so you can get to the needle in the haystack quickly.

For teams already running ClickStack, adding Temporal metrics means unified observability. Alternatively, for users running Temporal, ClickStack offers an out-of-box open-source observability solution that users can [get started with in minutes](https://clickhouse.com/docs/use-cases/observability/clickstack/getting-started). Understand how the health of a database affects Task processing backlogs. Track how deployment changes affect Workflow latency. Build dashboards that show the complete picture of your system's health.

## Getting started: Connecting Temporal Cloud to ClickStack

The integration uses the [OpenTelemetry Collector's Prometheus receiver](https://opentelemetry.io/docs/collector/configuration/#receivers) to scrape metrics from Temporal Cloud. [Full instructions on how to set up the integration are available](https://clickhouse.com/docs/use-cases/observability/clickstack/integrations/temporal-metrics), but the gist is once you have a Temporal Cloud API Key that has permission to read metrics, you create the configuration file in the OpenTelemetry Collector like this:


```yaml
receivers:
  prometheus/temporal:
    config:
      scrape_configs:
      - job_name: 'temporal-cloud'
        scrape_interval: 60s
        scheme: https
        authorization:
          type: Bearer
          credentials_file: <TEMPORAL CLOUD API KEY PATH>
        static_configs:
          - targets: ['metrics.temporal.io']
        metrics_path: '/v1/metrics'

processors:
  resource:
    attributes:
      - key: service.name
        value: "temporal"
        action: upsert

service:
  pipelines:
    metrics/temporal:
      receivers: [prometheus/temporal]
      processors: [resource, memory_limiter, batch]
      exporters: [clickhouse]
```

[Run code block](null)

Once deployed, open the ClickStack UI, HyperDX, and navigate to the Metrics explorer. Search for metrics starting with `temporal_cloud` to confirm data is flowing. You can import the [pre-built Temporal dashboard](https://clickhouse.com/docs/use-cases/observability/clickstack/integrations/temporal-metrics#dashboards) and immediately visualize Workflow success rates, Actions consumption against your limits, and Task Queue backlogs.

## What's Next

With Temporal metrics flowing into ClickStack, you can set up alerts on critical thresholds, build custom dashboards for your specific workflow patterns, and correlate workflow performance with the rest of your observability data.

For full configuration details and troubleshooting guidance, check out the[ complete documentation](https://clickhouse.com/docs/use-cases/observability/clickstack/integrations/temporal-metrics).

Your durable workflows deserve scalable observability. With ClickStack and [Temporal Cloud](https://temporal.io/cloud) working together, you get both.
