---
title: "What's new in ClickStack. September '25."
date: "2025-09-30T15:45:49.591Z"
author: "The ClickStack Team"
category: "Product"
excerpt: "Discover what’s new in ClickStack this month, including importing and exporting dashboards, custom aggregations, chunking time windows, and more!"
---

# What's new in ClickStack. September '25.

Welcome to the September edition of What's New in ClickStack - the open-source observability stack for ClickHouse. Each month, we highlight the latest updates across the stack, combining new ClickHouse capabilities with HyperDX UI enhancements to unlock fresh workflows, smarter visualizations, and a smoother experience.

This release introduces dashboard import/export, support for custom aggregations, and the ability to extend the configuration for the OTel collector. We’ve also delivered several performance improvements, including time-window chunking and better support for gauge metrics with the delta function.

## New contributors

Building an open-source observability stack is a team sport - and our community makes it possible. A big thank you to this month's new contributors! Every contribution, big or small, helps make ClickStack better for everyone.

[@elizabetdev](https://github.com/elizabetdev) [@brandon-pereira](https://github.com/brandon-pereira) [@pulpdrew](https://github.com/pulpdrew)

## Import/export dashboards

One of the most requested features from the community has arrived: you can now import and export dashboards in HyperDX. This makes it easier than ever to share dashboards with teammates or contribute them back to the wider community.

Dashboards can be exported as **versioned JSON files**, ensuring compatibility today while giving us the flexibility to evolve the format and add new functionality in the future. 

Consider the following simple dashboard showing analytics on our [public demo ClickPy](https://clickhouse.com/blog/instrumenting-your-app-with-otel-clickstack). Exporting requires a simple click, producing a JSON file users can share.

![export_dashboard.gif](https://clickhouse.com/uploads/export_dashboard_e066be3f13.gif)


Importing is equally simple. Users can simply create a new saved dashboard and import the JSON file. To ensure portability, when importing a dashboard you’ll need to map its data sources (logs, traces, or metrics) to those already defined in HyperDX, so all visualizations connect correctly.  

![import_dashboard.gif](https://clickhouse.com/uploads/import_dashboard_167dea8e12.gif)

Looking ahead, we believe this feature opens the door to **out-of-the-box experiences**. Expect to see official, ready-to-use dashboards (for example, monitoring NGINX, Kafka, Redis etc) that can be imported directly into your environment. Stay tuned as we begin developing these out in the coming months!


<div class="my-6"><div class="rounded-lg bg-white/10 p-4"><h3 class="text-inherit undefined Typography_suiTitleh3__JlLe2  group/mdHeader toc-ignore" id="test">Get started with ClickStack
</h3><p>Ready to explore the world's fastest and most scalable open source observability stack? Start locally in seconds.</p><a class=" w-full" target="_self" href="https://clickhouse.com/docs/use-cases/observability/clickstack/getting-started?loc=blog-o11y-global-cta&amp;utm_source=clickhouse&amp;utm_medium=web&amp;utm_campaign=blog"><button class="styles_button__3smpn mt-6 w-full font-medium" data-type="primary"><span class="flex items-center whitespace-nowrap">Start exploring</span></button></a></div></div>


## Custom collector configuration

September introduces the ability to **modify the OpenTelemetry Collector configuration** distributed with ClickStack.

ClickStack is built from three core components: **HyperDX** as the visualization layer, **ClickHouse** as the analytics engine that stores and supports querying of observability data efficiently, and an opinionated distribution of the **OTel Collector**. The collector configuration is managed through HyperDX using OpAmp to ensure ingestion remains secure - by requiring the ingestion API key that HyperDX provides in the UI. While this model guarantees security and configuration consistency, it has historically made customization difficult for users.

To extend the configuration, users can now supply their own OTel Collector Yaml, which is merged with the base configuration delivered via OPAMP. The custom file should be mounted into the container at `/etc/otelcol-contrib/custom.config.yaml`.

For example, if you’re deploying ClickStack locally and want to monitor host system metrics or local log files, you previously had to run a second OTel Collector with the right configuration and forward data into ClickStack’s ingestion endpoint provided by its packaged collector. 

With the new extension mechanism, you can simply define the extra receivers you need and mount the file into the container - enabling host metrics and logs to flow into your local deployment with a single command.

A receiver configuration for local monitoring would typically look something like the following. 

> Note that we also need to ensure we have the required pipelines to route the data from our receivers to the clickhouse exporter defined in the base configuration:

<pre><code type='click-ui' language='yaml'>
# local-monitoring.yaml
receivers:
  filelog:
    include:
      - /var/host/log/**/*.log # Linux
      - /var/host/log/syslog
      - /var/host/log/messages
      - /private/var/log/*.log # macOS
      - /tmp/all_events.log # macos - see below
    start_at: beginning # modify to collect new files only

  hostmetrics:
    collection_interval: 1s
    scrapers:
      cpu:
        metrics:
          system.cpu.time:
            enabled: true
          system.cpu.utilization:
            enabled: true
      memory:
        metrics:
          system.memory.usage:
            enabled: true
          system.memory.utilization:
            enabled: true
      filesystem:
        metrics:
          system.filesystem.usage:
            enabled: true
          system.filesystem.utilization:
            enabled: true
      paging:
        metrics:
          system.paging.usage:
            enabled: true
          system.paging.utilization:
            enabled: true
          system.paging.faults:
            enabled: true
      disk:
      load:
      network:
      processes:

service:
  pipelines:
    logs/host:
      exporters:
        - clickhouse
      processors:
        - memory_limiter
        - transform
        - batch
      receivers: [filelog]
    metrics/host:
      exporters:
        - clickhouse
      processors:
        - memory_limiter
        - batch
      receivers: [hostmetrics]
</code></pre>


To include this in the OTel collector, we simply need to mount this file into our container when deploying ClickStack:

<pre><code type='click-ui' language='bash'>
docker run --name clickstack-o11y \
  -p 8080:8080 -p 4317:4317 -p 4318:4318 \
  -v "$(pwd)/local-monitoring.yaml:/etc/otelcol-contrib/custom.config.yaml:ro" \
  -v /var/log:/var/host/log:ro \
  -v /private/var/log:/private/var/log:ro \
  --user 0:0 \
  docker.hyperdx.io/hyperdx/hyperdx-all-in-one
</code></pre>  


> In this example, we also mount paths from our local file system to ensure the collector can read our host log files. This is an **example only** and should not be used in production, as it grants the container root access to read our system metrics and log files.

When we log into HyperDX, we should immediately see our local logs and be able to explore metrics as shown in [our local monitoring guide](https://clickhouse.com/docs/use-cases/observability/clickstack/getting-started/local-data):

![custom_collector.png](https://clickhouse.com/uploads/custom_collector_c6c3de736a.png)

This simple example highlights how the feature improves the getting-started experience, but the same flexibility is critical at scale. Users may want to pull events from Kafka, open a syslog interface for log ingestion, or configure tail and head sampling for traces. In rare cases, users may even need to adjust the ClickHouse exporter configuration - particularly in high-throughput environments where additional tuning is required.

## Custom aggregations

Historically, HyperDX limited chart building to a small set of common aggregation types. These included min, max, mean, median, and percentiles like the 90th, 95th, and 99th. While they covered most use cases, they constrained more advanced analysis.

With the latest release, users can now unlock the full analytical capabilities of ClickHouse by selecting “none” as the aggregation type. This allows you to directly specify any ClickHouse aggregation function, exposing more than [100 analytical options](https://clickhouse.com/docs/sql-reference/aggregate-functions/reference) for deeper and more flexible exploration of your data.

For example, consider the following visualization, which plots both the average response time and the variance for our ClickPy demo queries. Standard deviation can reveal fluctuations that an average alone might hide. While not exposed as a native option in HyperDX, it can be achieved by selecting “None” and using the [`stddevPop`](https://clickhouse.com/docs/sql-reference/aggregate-functions/reference/stddevpop) function directly as an expression.

![custom_aggregations.png](https://clickhouse.com/uploads/custom_aggregations_fd62b4788f.png)

## Chunking time windows

Previously, HyperDX executed a single query to load search results in the Search view. This was fine for smaller datasets or narrow time ranges, but it became inefficient at scale. Queries scanned the entire time window uniformly, rather than prioritizing resources to the recent data that users typically care about.

With the September release, HyperDX now **chunks query execution by time window**, starting with the most recent data. Subsequent windows are queried only if needed, and once the required number of results is reached, the remaining queries are canceled.

This approach prioritizes resources to deliver the freshest results first, while reducing overall execution time and system load.

![5_clickstack_september2025.gif](https://clickhouse.com/uploads/5_clickstack_september2025_a95d9a36de.gif)

Consider the above query over a four-hour time range. Instead of executing one large query, HyperDX splits it into sub-queries, each covering a smaller window. In this example, each query spans one hour: the first returns three results, the second adds two, and the third adds five. Because the interface only requires ten results, the final query is canceled.

In practice, HyperDX handles much larger time ranges and higher data volumes. By applying this chunking approach to search results, it ensures ClickHouse resources are focused on retrieving the most recent data first.

We are exploring how to apply this technique in other parts of HyperDX. For example, histogram views could be loaded asynchronously in chunks, allowing database resources to deliver quick responses and keep the interface interactive instead of forcing users to wait for results for the entire time range to complete.

## Delta function

The September release also adds support for applying a **delta function to gauge metrics**, matching the behavior of Prometheus’s [`delta()`](https://prometheus.io/docs/prometheus/latest/querying/functions/#delta) function.

A **gauge** is a metric that represents a single numerical value that can move up or down. Typical examples include system temperature, memory usage, or the number of concurrent requests. Unlike counters, which only increase until reset, gauges can fluctuate freely.

The `delta()` function basically aims to show you how much a gauge has changed over a given time window, adjusted so each window is comparable no matter when the samples landed.

The `delta()` function calculates the difference between the first and last value of a gauge within a time range window (the bucket or lookback range) e.g.  `[1m]`. A new bucket is created at each evaluation step, covering the preceding range. 

> Note that the raw difference will be extrapolated to represent the full duration of the bucket, ensuring consistent comparisons across time windows. For example, if a one-minute bucket contains two points 30 seconds apart with a difference of 10, the result is scaled to 20 to represent the full minute.

Since each bucket may contain multiple series (distinguished by attributes such as host or service), multiple delta values can exist per bucket. The aggregation function (such as min, max, or avg) specified by the user is then applied across the deltas to produce the value displayed.

Examples of using `delta()` include tracking changes in pod memory usage. A positive delta consistently above zero indicates a pod’s memory footprint is steadily increasing, which can be an early sign of a memory leak and worth alerting on.

![delta_function_v2.gif](https://clickhouse.com/uploads/delta_function_v2_b3e10f1179.gif)

Consider the metric `k8s.pod.memory.working_set` above for the ClickHouse pod. Plotting the raw gauge value shows the absolute memory usage of a pod. By applying` delta`, you can instead visualize how much memory usage has changed within each interval. A sustained positive delta highlights the pod is steadily consuming more memory over time, while negative deltas indicate memory being released.

<div class="my-6"><div class="rounded-lg bg-white/10 p-4"><h3 class="text-inherit undefined Typography_suiTitleh3__JlLe2  group/mdHeader toc-ignore" id="test">Get started with ClickStack</h3><p>Discover the world’s fastest and most scalable open source observability stack, in seconds.</p><a class=" w-full" target="_self" href="https://clickhouse.com/docs/use-cases/observability/clickstack/getting-started?loc=blog-o11y-global-cta&amp;utm_source=clickhouse&amp;utm_medium=web&amp;utm_campaign=blog"><button class="styles_button__3smpn mt-6 w-full font-medium" data-type="primary"><span class="flex items-center whitespace-nowrap">Try now</span></button></a></div></div>

