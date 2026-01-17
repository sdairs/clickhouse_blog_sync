---
title: "Building an Observability Solution with ClickHouse - Part 2 - Traces"
date: "2023-03-28T16:40:52.991Z"
author: "Dale McDiarmid"
category: "Engineering"
excerpt: "Continuing our blog series on building an Observability solution with ClickHouse we focus on storing traces in ClickHouse with OpenTelemetry."
---

# Building an Observability Solution with ClickHouse - Part 2 - Traces

## Introduction

Here at ClickHouse, we consider [Observability to be just another real-time analytics problem](/resources/engineering/observability-cost-optimization-playbook). As a high-performance real-time analytics database, ClickHouse is used for many use cases, including real-time analytics for [time series](https://clickhouse.com/blog/working-with-time-series-data-and-functions-ClickHouse) data. Its diversity of use cases has helped drive a huge range of [analytical functions](https://clickhouse.com/docs/en/sql-reference/functions/), which assist in querying most data types. These query features and high compression rates have increasingly led users to utilize ClickHouse to store Observability data. This data takes three common forms: logs, metrics, and traces. In this blog, the [second in an Observability series](https://clickhouse.com/blog/storing-log-data-in-clickhouse-fluent-bit-vector-open-telemetry), we explore how trace data can be collected, stored, and queried in ClickHouse.

We have focused this post on using [OpenTelemetry](https://clickhouse.com/engineering-resources/opentelemetry-otel) to collect trace data for storage in ClickHouse. When combined with Grafana, and recent developments in the [ClickHouse plugin](https://github.com/grafana/clickhouse-datasource/pull/329), traces are easily visualized and can be combined with logs and metrics to obtain a deep understanding of your system behavior and performance when detecting and diagnosing issues.

We have attempted to ensure that any examples can be reproduced, and while this post focuses on data collection and visualization basics, we have included some tips on schema optimization. For example purposes, we have forked the [official OpenTelemetry Demo](https://opentelemetry.io/ecosystem/demo/), adding support for ClickHouse and including an OOTB Grafana dashboard for visualizing traces. 

## What are Traces?

Telemetry is data emitted from a system about its behavior. This data can take the form of logs, metrics, and traces. A trace records the paths taken by requests (made by an application or end-user) as they propagate through multi-service architectures such as microservice and serverless applications. A single trace consists of multiple spans, each a unit of work or operation. The span provides details of an operation, principally the time it took, in addition to [other metadata](https://opentelemetry.io/docs/concepts/signals/traces/#attributes) and related log messages. These spans are hierarchy related as a tree, with the first span relating the root and covering the entire trace from start to finish. Beneath this root and each subsequent span, child operations are captured. As we navigate the tree, we can see the child operations and steps that make up the above level. This gives us ever-increasing context as to the work performed by the original request. This is visualized below:

![traces_concept.png](https://clickhouse.com/uploads/traces_concept_4908965e1c.png)

These traces, when combined with metrics and logs, can be critical in obtaining insights into the behavior of a system for the detection and resolution of issues.

## What is OpenTelemetry?

The OpenTelemetry project is a vendor-neutral open-source framework consisting of SDKs, APIs, and components that allow the ingesting, transforming, and sending of Observability data to a backend. More specifically, this consists of several main components: 

* A set of **specifications and conventions** of how metrics, logs, and traces should be collected and stored. This includes recommendations for language-specific agents and a full specification for the OpenTelemetry Line Protocol (OTLP) based on [protobuf](https://protobuf.dev/). This allows data to be transmitted between services by providing a full description of the client-server interface and the message format.
* **Language-specific libraries and SDKs** for instrumenting, generating, collecting, and exporting observability data. This is particularly relevant to the collection of trace data.
* An **OTEL Collector** written in Golang provides a vendor-agnostic implementation of receiving, processing and exporting Observability data. The OTEL Collector provides a centralized processing gateway by supporting several input formats, such as Prometheus and OTLP, and a wide range of export targets, including ClickHouse. 

In summary, OpenTelemetry standardizes the collection of logs, metrics, and traces. Importantly, it is not responsible for storing this data in an [Observability backend](https://clickhouse.com/engineering-resources/top-opentelemetry-compatible-platforms/) - this is where ClickHouse comes in!

## Why ClickHouse?

Trace data is typically represented as a single table, with each span a row, and thus can be considered just another real-time analytics problem. As well as providing high compression for this data type, ClickHouse provides a rich SQL interface with additional [analytical functions](https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference) that trivialize querying traces. When combined with Grafana, users have a highly cost-efficient way of storing and visualizing traces. While other stores may offer similar compression levels, ClickHouse is unique in combining this low latency querying as the world's fastest analytical database. In fact, these characteristics led to ClickHouse becoming a preferred backend for many commercial observability solutions like: [Signoz.io](https://signoz.io/), [Highlight.io](https://www.highlight.io/), [qryn](https://qryn.metrico.in), [BetterStack](https://betterstack.com/press/series-a/), or homegrown large-scale observability platforms like [Uber](https://www.uber.com/en-ES/blog/logging/), [Cloudflare](https://blog.cloudflare.com/http-analytics-for-6m-requests-per-second-using-clickhouse/), or [Gitlab](https://about.gitlab.com/handbook/engineering/development/ops/monitor/observability/#how-are-we-currently-using-clickhouse).

## Instrumentation Libraries

Instrumentation libraries are provided for the most popular languages. These provide both automatic instrumentation of code, where an application/services framework is exploited to capture the most common metric and trace data, and manual instrumentation techniques. While automatic instrumentation is typically sufficient, the latter allows users to instrument-specific parts of their code, potentially in more detail - capturing application-specific metrics and trace information. 

For the purposes of this blog, we are only interested in the capture of trace information. The [OpenTelemetry demo application consists of a microservices architecture](https://opentelemetry.io/docs/demo/architecture/) with many dependent services, each in a different language, to provide a reference for implementors. The simple example below shows the instrumentation of a Python Flask API to collect trace data:

```python
# These are the necessary import declarations
from opentelemetry import trace

from random import randint
from flask import Flask, request

# Acquire a tracer
tracer = trace.get_tracer(__name__)

app = Flask(__name__)

@app.route("/rolldice")
def roll_dice():
	return str(do_roll())

def do_roll():
	# This creates a new span that's the child of the current one
	with tracer.start_as_current_span("do_roll") as rollspan:
    	res = randint(1, 6)
    	rollspan.set_attribute("roll.value", res)
    	return res
```

A detailed guide on each library is well beyond the scope of this blog, and we encourage users to read the [relevant documentation for their language](https://opentelemetry.io/docs/instrumentation/).

## OTEL Collector

The OTEL collector accepts data from Observability sources, such as trace data from an instrumentation library, processes this data, and exports it to the target backend. The OTEL Collector can also provide a centralized processing gateway by supporting several input formats, such as Prometheus and OTLP, and a wide range of export targets, including ClickHouse.

The Collector uses the concept of pipelines. These can be of type logs, metrics, or traces and consist of a receiver, processor, and exporter.

![otel_collector.png](https://clickhouse.com/uploads/otel_collector_fef083663e.png)

The [receiver](https://opentelemetry.io/docs/collector/configuration/#receivers) in this architecture acts as the input for OTEL data. This can be either via a pull or push model. While this can occur over a number of protocols, trace data from instrumentation libraries will be pushed via [OTLP](https://opentelemetry.io/docs/reference/specification/protocol/) using either gRPC or HTTP. [Processors](https://opentelemetry.io/docs/collector/configuration/#processors) subsequently run on this data providing filtering, batching, and enrichment capabilities. Finally, an exporter sends the data to a backend destination via either push or pull. In our case, we will push the data to ClickHouse.

Note that while more commonly used as a gateway/aggregator, handling tasks such as batching and retries, the collector can also be deployed as an agent itself - this is useful for log collection, as described in our previous post. OTLP represents the OpenTelemetry data standard for communication between gateway and agent instances, which can occur over gRPC or HTTP. For the purposes of trace collection, the collector is simply deployed as a gateway, however, as shown below:

![otel_architecture.png](https://clickhouse.com/uploads/otel_architecture_248c22ed3a.png)

Note that more advanced architectures are possible for higher load environments. We recommend this [excellent video discussing possible options](https://www.youtube.com/watch?v=WhRrwSHDBFs).

### ClickHouse Support

ClickHouse is supported in the OTEL exporter through [a community contribution](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/exporter/clickhouseexporter), with support for logs, traces, and metrics. Communication with ClickHouse occurs over the optimized native format and protocol via the official Go client. Before using the OpenTelemetry Collector, users should consider the following points:

* The ClickHouse data model and schema that the agent uses are hard coded. As of the time of writing, there is no ability to change the types or codecs used. Mitigate this by creating the table before deploying the connector, thus enforcing your schema.
* The exporter is not distributed with the core OTEL distribution but rather as an extension through the `contrib` image. Practically this means using the correct Docker image in any HELM chart. For leaner deployments, users can [build a custom collector image](https://opentelemetry.io/docs/collector/custom-collector/) with only the required components.
* As of version 0.74, users should pre-create the database in ClickHouse before deployment if not set to the value of `default` (as used in the demo fork). 

  ```sql
    CREATE DATABASE otel
   ```
* The exporter is in alpha, and users should adhere to the advice [provided by OpenTelemetry](https://github.com/open-telemetry/opentelemetry-collector#alpha).

## Example Application

![otel_demo.png](https://clickhouse.com/uploads/otel_demo_ab40c40d7f.png)

[OpenTelemetry provides a demo application](https://opentelemetry.io/ecosystem/demo/) giving a practical example of the implementation of OpenTelemetry. This is a distributed micro-services architecture that powers a web store selling telescopes. This e-commerce use-case is useful in creating an opportunity for a wide range of simple, understandable services, e.g., recommendations, payments, and currency conversion.  The storefront is subjected to a load generator, which causes each instrumented service to generate logs, traces, and metrics. As well as providing a realistic example for practitioners to learn how to instrument in their preferred language, this demo also allows vendors to show off their OpenTelemetry integration with their Observability backend. In this spirit, we have [forked this application](github.com/clickHouse/opentelemetry-demo) and made the necessary changes to store trace data in ClickHouse. 

<a target='_blank' href='/uploads/otel_demo_architecture_4c2b4164ce.png'><img src='/uploads/otel_demo_architecture_4c2b4164ce.png'/></a>

Note the breadth of languages used in the above architecture and the number of components handling operations such as payments and recommendations. Users are recommended to [check the code](https://github.com/open-telemetry/opentelemetry-demo/tree/main/src) for the service in their preferred language. Due to the presence of a collector as a gateway, no changes have been made to any instrumentation code. This architectural separation is one of the clear benefits of OpenTelemetry - backends can be changed with just a change of the target exporter in the collector.

### Deploying Locally

The demo uses a Docker container for each service. The demo can be deployed using `docker compose` and the steps outlined in the [official documentation](https://opentelemetry.io/docs/demo/docker-deployment/), substituting the ClickHouse fork for the original repository.

```bash
git clone https://github.com/ClickHouse/opentelemetry-demo.git
cd opentelemetry-demo/
docker compose up --no-build
```

We have [modified the docker-compose file](https://github.com/ClickHouse/opentelemetry-demo/blob/main/docker-compose.yml#L685-L694) to include a ClickHouse instance in which data will be stored, available to the other services as `clickhouse`.

### Deploying with Kubernetes

The demo can easily be deployed in Kubernetes using [the official instructions](https://opentelemetry.io/docs/demo/kubernetes-deployment/). We recommend copying the [values file](https://github.com/open-telemetry/opentelemetry-helm-charts/blob/main/charts/opentelemetry-demo/values.yaml) and modifying the [collector configuration.](https://github.com/open-telemetry/opentelemetry-helm-charts/blob/185ac3ab0b3b8c83de5f6b0fa14bc6eea2607d1e/charts/opentelemetry-demo/values.yaml#L603-L660) A sample values file, which sends all spans to a ClickHouse Cloud instance, can be found [here](https://gist.github.com/gingerwizard/f63c1c809d895937fa5929ab6c7c654d#file-values-yaml-L603-L662). This can be downloaded and deployed with a modified helm command, i.e.,

```bash
helm install -f values.yaml my-otel-demo open-telemetry/opentelemetry-demo
```

### Integrating ClickHouse

In this post, we focus on exporting traces only. While logs and metrics can also be stored in ClickHouse, we use the default configuration for simplicity. Logs are not enabled by default, and metrics are sent to Prometheus.

To send trace data to ClickHouse, we must add a custom OTEL Collector configuration via the file [`otel-config-extras.yaml`](https://github.com/ClickHouse/opentelemetry-demo/blob/main/src/otelcollector/otelcol-config-extras.yml). This will be merged with the [main configuration](https://github.com/ClickHouse/opentelemetry-demo/blob/main/src/otelcollector/otelcol-config.yml), overriding any existing declarations. The additional configuration is shown below:

```yaml
exporters:
 clickhouse:
   endpoint: tcp://clickhouse:9000?dial_timeout=10s&compress=lz4
   database: default
   ttl_days: 3
   traces_table_name: otel_traces
   timeout: 5s
   retry_on_failure:
     enabled: true
     initial_interval: 5s
     max_interval: 30s
     max_elapsed_time: 300s

processors:
 batch:
   timeout: 5s
   send_batch_size: 100000

service:
 pipelines:
   traces:
     receivers: [otlp]
     processors: [spanmetrics, batch]
     exporters: [logging, clickhouse]
```

The main changes here are configuring ClickHouse as an exporter. A few key settings here:

* The endpoint setting specifies the ClickHouse host and port. Note communication occurs over TCP (port 9000). For secure connections, this should be 9440 with a `secure=true` parameter, e.g., `'clickhouse://&lt;username>:&lt;password>@&lt;host>:9440?secure=true'`. Alternatively, use the `dsn` parameter. Note we connect to host `clickhouse` here. This is the clickhouse container, added to the local deployment docker image. Feel free to modify this path, e.g., to point to a ClickHouse Cloud cluster.
* `ttl_days` - This controls data retention in ClickHouse via the TTL feature. See the section "Schema" below.

Our traces pipeline utilizes the OTLP receiver to receive trace data from the instrumentation libraries. This pipeline then passes this data to two processors:

* A [batch processor ](https://github.com/open-telemetry/opentelemetry-collector/blob/main/processor/batchprocessor/README.md)is responsible for ensuring INSERTs occur at most every 5s or when the batch size reaches 100k. This ensures inserts are batched efficiently.
* A [spanmetrics](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/processor/spanmetricsprocessor) processor. This aggregates request, error, and metrics from trace data, forwarding it to the metrics pipeline. We will utilize this in a later post on metrics.

## Schema

Once deployed, we can confirm trace data is being sent to ClickHouse using a simple SELECT on the table `otel_traces`. This represents the main data to which all spans are sent. Note we access the container using the `clickhouse-client` (it should be exposed on the host on the default 9000 port).

```sql
SELECT *
FROM otel_traces
LIMIT 1
FORMAT Vertical

Row 1:
──────
Timestamp:      	2023-03-20 18:04:35.081853291
TraceId:        	06cabdd45e7c3c0172a8f8540e462045
SpanId:         	b65ebde75f6ae56f
ParentSpanId:   	20cc5cb86c7d4485
TraceState:
SpanName:       	oteldemo.AdService/GetAds
SpanKind:       	SPAN_KIND_SERVER
ServiceName:    	adservice
ResourceAttributes: {'telemetry.auto.version':'1.23.0','os.description':'Linux 5.10.104-linuxkit','process.runtime.description':'Eclipse Adoptium OpenJDK 64-Bit Server VM 17.0.6+10','service.name':'adservice','service.namespace':'opentelemetry-demo','telemetry.sdk.version':'1.23.1','process.runtime.version':'17.0.6+10','telemetry.sdk.name':'opentelemetry','host.arch':'aarch64','host.name':'c97f4b793890','process.executable.path':'/opt/java/openjdk/bin/java','process.pid':'1','process.runtime.name':'OpenJDK Runtime Environment','container.id':'c97f4b7938901101550efbda3c250414cee6ba9bfb4769dc7fe156cb2311735e','os.type':'linux','process.command_line':'/opt/java/openjdk/bin/java -javaagent:/usr/src/app/opentelemetry-javaagent.jar','telemetry.sdk.language':'java'}
SpanAttributes: 	{'thread.name':'grpc-default-executor-1','app.ads.contextKeys':'[]','net.host.name':'adservice','app.ads.ad_request_type':'NOT_TARGETED','rpc.method':'GetAds','net.host.port':'9555','net.sock.peer.port':'37796','rpc.service':'oteldemo.AdService','net.transport':'ip_tcp','app.ads.contextKeys.count':'0','app.ads.count':'2','app.ads.ad_response_type':'RANDOM','net.sock.peer.addr':'172.20.0.23','rpc.system':'grpc','rpc.grpc.status_code':'0','thread.id':'23'}
Duration:       	218767042
StatusCode:     	STATUS_CODE_UNSET
StatusMessage:
Events.Timestamp:   ['2023-03-20 18:04:35.145394083','2023-03-20 18:04:35.300551833']
Events.Name:    	['message','message']
Events.Attributes:  [{'message.id':'1','message.type':'RECEIVED'},{'message.id':'2','message.type':'SENT'}]
Links.TraceId:  	[]
Links.SpanId:   	[]
Links.TraceState:   []
Links.Attributes:   []
```

Each row represents a span, some of which are also root spans. There are some key fields, which with a basic understanding, will allow us to construct useful queries. A full description of trace metadata is available [here](https://opentelemetry.io/docs/concepts/signals/traces/):

* **TraceId** - The Trace Id represents the trace that the Span is a part of. 
* **SpanId** - A Span's unique Id
* **ParentSpanId** - The span id of the Span’s parent span. This allows a trace call history to be constructed. This will be empty for root spans.
* **SpanName - the name of the operation**
* **[SpanKind](https://opentelemetry.io/docs/reference/specification/trace/api/#spankind)** - When a span is created, its Kind is either a Client, Server, Internal, Producer, or Consumer. This Kind hints to the tracing backend as to how the trace should be assembled. It effectively describes the relationship of the Span to its children and parents. 
* **ServiceName** - the name of the service, e.g., Adservice, from which the Span originates.
* **[ResourceAttributes](https://opentelemetry.io/docs/concepts/signals/traces/#attributes)** - key-value pairs that contain metadata that you can use to annotate a Span to carry information about the operation it is tracking. This might, for example, contain Kubernetes information, e.g., pod name or values concerning the host. Note our schema forces keys and values to be both String with a Map type.
* **SpanAttributes** - additional span level attributes, e.g., `thread.id`.
* **Duration** - duration of the Span in nanoseconds.
* **[StatusCode](https://opentelemetry.io/docs/concepts/signals/traces/#attributes)**  - Either UNSET, OK, or ERROR. The latter will be set when there is a known error in the application code, such as an exception.
* **[Events*](https://opentelemetry.io/docs/concepts/signals/traces/#span-events)** - While possibly inappropriate for dashboard overviews, these can interest the application developer. This can be thought of as a structured annotation on a Span, typically used to denote a meaningful, singular point during the Span’s duration, e.g., when a page becomes interactive. The `Events.Timestamp`, `Events.Name`, and `Events.Attributes` can be used to reconstruct the full event - note this relies on array positions.
* **[Links* ](https://opentelemetry.io/docs/concepts/signals/traces/#span-links)** - These imply a casual relationship to another span. For example, these might be asynchronous operations executed as a result of this specific operation. A processing job that is queued due to a request operation might be an appropriate span link. Here the developer might link the last Span from the first trace to the first Span in the second trace to causally associate them. In the ClickHouse schema, we again rely on Array types and associating the positions of the columns `Links.TraceId`, `Links.SpanId`, and `Links.Attributes`.

Note that the collector is opinionated on the schema, including enforcing specific codecs. While these represent sensible choices for the general case, they prevent users from tuning the configuration to their needs via collector configuration. Users wishing to modify the codecs or the ORDER BY key, e.g., fit [user-specific access patterns](https://clickhouse.com/docs/en/guides/improving-query-performance/sparse-primary-indexes/sparse-primary-indexes-intro), should pre-create the table in advance.

<pre><code class="hljs language-sql" style="font-size:12px"><span class="hljs-keyword">CREATE</span> <span class="hljs-keyword">TABLE</span> otel_traces
(
	`<span class="hljs-type">Timestamp</span>` DateTime64(<span class="hljs-number">9</span>) CODEC(Delta(<span class="hljs-number">8</span>), ZSTD(<span class="hljs-number">1</span>)),
	`TraceId` String CODEC(ZSTD(<span class="hljs-number">1</span>)),
	`SpanId` String CODEC(ZSTD(<span class="hljs-number">1</span>)),
	`ParentSpanId` String CODEC(ZSTD(<span class="hljs-number">1</span>)),
	`TraceState` String CODEC(ZSTD(<span class="hljs-number">1</span>)),
	`SpanName` LowCardinality(String) CODEC(ZSTD(<span class="hljs-number">1</span>)),
	`SpanKind` LowCardinality(String) CODEC(ZSTD(<span class="hljs-number">1</span>)),
	`ServiceName` LowCardinality(String) CODEC(ZSTD(<span class="hljs-number">1</span>)),
	`ResourceAttributes` Map(LowCardinality(String), String) CODEC(ZSTD(<span class="hljs-number">1</span>)),
	`SpanAttributes` Map(LowCardinality(String), String) CODEC(ZSTD(<span class="hljs-number">1</span>)),
	`Duration` Int64 CODEC(ZSTD(<span class="hljs-number">1</span>)),
	`StatusCode` LowCardinality(String) CODEC(ZSTD(<span class="hljs-number">1</span>)),
	`StatusMessage` String CODEC(ZSTD(<span class="hljs-number">1</span>)),
	`Events.Timestamp` <span class="hljs-keyword">Array</span>(DateTime64(<span class="hljs-number">9</span>)) CODEC(ZSTD(<span class="hljs-number">1</span>)),
	`Events.Name` <span class="hljs-keyword">Array</span>(LowCardinality(String)) CODEC(ZSTD(<span class="hljs-number">1</span>)),
	`Events.Attributes` <span class="hljs-keyword">Array</span>(Map(LowCardinality(String), String)) CODEC(ZSTD(<span class="hljs-number">1</span>)),
	`Links.TraceId` <span class="hljs-keyword">Array</span>(String) CODEC(ZSTD(<span class="hljs-number">1</span>)),
	`Links.SpanId` <span class="hljs-keyword">Array</span>(String) CODEC(ZSTD(<span class="hljs-number">1</span>)),
	`Links.TraceState` <span class="hljs-keyword">Array</span>(String) CODEC(ZSTD(<span class="hljs-number">1</span>)),
	`Links.Attributes` <span class="hljs-keyword">Array</span>(Map(LowCardinality(String), String)) CODEC(ZSTD(<span class="hljs-number">1</span>)),
	INDEX idx_trace_id TraceId TYPE bloom_filter(<span class="hljs-number">0.001</span>) GRANULARITY <span class="hljs-number">1</span>,
	INDEX idx_res_attr_key mapKeys(ResourceAttributes) TYPE bloom_filter(<span class="hljs-number">0.01</span>) GRANULARITY <span class="hljs-number">1</span>,
	INDEX idx_res_attr_value mapValues(ResourceAttributes) TYPE bloom_filter(<span class="hljs-number">0.01</span>) GRANULARITY <span class="hljs-number">1</span>,
	INDEX idx_span_attr_key mapKeys(SpanAttributes) TYPE bloom_filter(<span class="hljs-number">0.01</span>) GRANULARITY <span class="hljs-number">1</span>,
	INDEX idx_span_attr_value mapValues(SpanAttributes) TYPE bloom_filter(<span class="hljs-number">0.01</span>) GRANULARITY <span class="hljs-number">1</span>,
	INDEX idx_duration Duration TYPE minmax GRANULARITY <span class="hljs-number">1</span>
)
ENGINE <span class="hljs-operator">=</span> MergeTree
<span class="hljs-keyword">PARTITION</span> <span class="hljs-keyword">BY</span> toDate(<span class="hljs-type">Timestamp</span>)
<span class="hljs-keyword">ORDER</span> <span class="hljs-keyword">BY</span> (ServiceName, SpanName, toUnixTimestamp(<span class="hljs-type">Timestamp</span>), TraceId)
TTL toDateTime(<span class="hljs-type">Timestamp</span>) <span class="hljs-operator">+</span> toIntervalDay(<span class="hljs-number">3</span>)
SETTINGS index_granularity <span class="hljs-operator">=</span> <span class="hljs-number">8192</span>, ttl_only_drop_parts <span class="hljs-operator">=</span> <span class="hljs-number">1</span>
</code></pre>

Other than TTL (see below) there are some important observations regarding this schema:

* The **ORDER BY** clause in our schema determines how our [data is sorted and stored on disk](https://clickhouse.com/docs/en/optimize/sparse-primary-indexes). This will also control the [construction of our sparse index](https://clickhouse.com/docs/en/optimize/sparse-primary-indexes) and, most importantly, directly impact our compression levels and query performance. The current clause of `(ServiceName, SpanName, toUnixTimestamp(Timestamp), TraceId)` sorts the data in order of right to left and optimizes for queries which first filter by ServiceName. Filter restrictions by later-ordered columns will become increasingly ineffective. If your access patterns differ due to differences in your diagnosis workflows, you might modify this order and the columns used. When doing this, consider best practices to ensure the [key is optimally exploited](https://clickhouse.com/docs/en/optimize/sparse-primary-indexes#the-primary-index-is-used-for-selecting-granules). 
* **PARTITION BY** - this clause causes a physical separation of the data on disk. While useful for the efficient deletion of data (see TTL below), it can potentially [positively and negatively impact query performance](https://medium.com/datadenys/using-partitions-in-clickhouse-3ea0decb89c4). Based on the partition expression `toDate(Timestamp)`, which creates a partition by day, queries that target the most recent data, e.g., the last 24 hours, will benefit. Queries over many partitions/days (only likely if you expand your retention beyond the default of 3 days) will conversely potentially be negatively impacted. If you expand your data retention period to months or years or have access patterns that need to target a wider time range, consider using a different expression, e.g., partition by week, if you have a TTL of a year.
* **Map** - the Map type is used extensively in the above schema for attributes. This has been selected as the keys here are dynamic and application specific. The Map type’s flexibility here is useful but at some cost. Accessing a map key requires the entire column to be read and loaded. Accessing the key of a map will therefore incur a greater cost than if the key was an explicit column at the root - especially if the map is large with many keys. The difference in performance here will depend on the size of the map but can be considerable. To address this, users should [materialize](https://clickhouse.com/docs/en/sql-reference/statements/create/table#materialized) frequently queried map key/value pairs to columns on the root. These [materialized columns ](https://clickhouse.com/docs/en/sql-reference/statements/create/table#materialized)will, in turn, be populated at INSERT time from the corresponding map value and be available for fast access. We show an example below where we materialize the key `host.name` from the Map column `ResourceAttributes` to the root column `Host`:

   <pre style="font-size: 14px;"><code class="hljs language-sql"> <span class="hljs-keyword">CREATE</span> <span class="hljs-keyword">TABLE</span> otel_traces
    (
        `<span class="hljs-type">Timestamp</span>` DateTime64(<span class="hljs-number">9</span>) CODEC(Delta(<span class="hljs-number">8</span>), ZSTD(<span class="hljs-number">1</span>)),
        `HostName` String MATERIALIZED ResourceAttributes[<span class="hljs-string">'host.name'</span>],
        `ResourceAttributes` Map(LowCardinality(String), String) CODEC(ZSTD(<span class="hljs-number">1</span>)),
         ....
    )
    ENGINE <span class="hljs-operator">=</span> MergeTree
    <span class="hljs-keyword">PARTITION</span> <span class="hljs-keyword">BY</span> toDate(<span class="hljs-type">Timestamp</span>)
    <span class="hljs-keyword">ORDER</span> <span class="hljs-keyword">BY</span> (ServiceName, SpanName, toUnixTimestamp(<span class="hljs-type">Timestamp</span>), TraceId)
    TTL toDateTime(<span class="hljs-type">Timestamp</span>) <span class="hljs-operator">+</span> toIntervalDay(<span class="hljs-number">3</span>)
   </code></pre>

   Alternatively, this can be applied retrospectively once data has been inserted, and your access patterns are identified:
   
   ```sql
   ALTER TABLE otel_traces ADD COLUMN HostName String MATERIALIZED ResourceAttributes['host.name'];

   ALTER TABLE otel_traces MATERIALIZE COLUMN HostName;
   ```
   
   This process requires a mutation which can be [I/O intensive and should be scheduled with caution](https://clickhouse.com/docs/en/cloud/bestpractices/avoid-mutations).
   The Map type additionally requires the values to be the same type - String in our case. This loss of type information can require casts at query time. Furthermore, users should know the required syntax to access map keys - see “Querying Traces”.

* **Bloom filters** - To compensate for the restrictive ORDER BY key, the schema creates several [data-skipping bloom indices](https://clickhouse.com/docs/en/guides/improving-query-performance/skipping-indexes). These are designed to speed up queries that either filter by trace id or the maps or keys of our attributes. Generally, secondary indices are effective when a strong correlation between the primary key and the targeted column/expression exists, or a value is very sparse in the data. This ensures that when applying a filter matching this expression, [granules on disk ](https://clickhose.com/docs/en/optimize/skipping-indexes)that have a reasonable chance of not containing the target value can be skipped. For our specific schema, our TraceId should be very sparse and correlated with the ServiceName of the primary key. Likewise, our attribute keys and values will be correlated with the ServiceName and SpanName columns of the primary key. Generally, we consider these to be good candidates for bloom filters. The TraceId index is highly effective, but the others have not been tested under real-world workloads, so could potentially be a premature optimization until evidence suggests otherwise. We will evaluate the scalability of this model in a future post, stay tuned!

### TTL

Via the collector parameter `ttl_days`, the user is able to control the expiration of data through ClickHouse's TTL functionality. This value is reflected in the expression `TTL toDateTime(Timestamp) + toIntervalDay(3)`, which defaults to 3. Data older than this will be deleted based on an asynchronous background process. For more details on TTL, see [here](https://clickhouse.com/blog/using-ttl-to-manage-data-lifecycles-in-clickhouse).

The schemas above use [PARTITION BY](https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/mergetree/#partition-by) to assist TTL. Specifically, this allows a day's worth of data to be efficiently deleted when combined with the parameter `ttl_only_drop_parts=1`. As noted above, this may [positively and negatively impact queries](https://medium.com/datadenys/using-partitions-in-clickhouse-3ea0decb89c4).

### Trace Id Materialized View

In addition to the main table, the ClickHouse exporter creates a m[aterialized view](https://clickhouse.com/blog/using-materialized-views-in-clickhouse). A materialized view is a special trigger that stores the result of a SELECT query on data as it is inserted into a target table. This target table can summarize data (using an aggregation) in a format optimized for specific queries. In the exporter's case, the following view is created:

<pre><code class="hljs language-sql" style="font-size:14px;"><span class="hljs-keyword">CREATE</span> MATERIALIZED <span class="hljs-keyword">VIEW</span> otel_traces_trace_id_ts_mv <span class="hljs-keyword">TO</span> otel_traces_trace_id_ts
(
	`TraceId` String,
	`<span class="hljs-keyword">Start</span>` DateTime64(<span class="hljs-number">9</span>),
	`<span class="hljs-keyword">End</span>` DateTime64(<span class="hljs-number">9</span>)
) <span class="hljs-keyword">AS</span>
<span class="hljs-keyword">SELECT</span>
	TraceId,
	<span class="hljs-built_in">min</span>(<span class="hljs-type">Timestamp</span>) <span class="hljs-keyword">AS</span> <span class="hljs-keyword">Start</span>,
	<span class="hljs-built_in">max</span>(<span class="hljs-type">Timestamp</span>) <span class="hljs-keyword">AS</span> <span class="hljs-keyword">End</span>
<span class="hljs-keyword">FROM</span> otel_traces
<span class="hljs-keyword">WHERE</span> TraceId <span class="hljs-operator">!=</span> <span class="hljs-string">''</span>
<span class="hljs-keyword">GROUP</span> <span class="hljs-keyword">BY</span> TraceId
</code></pre>

This specific materialized view is running a `GROUP BY TraceId` and identifying the max and min timestamp per id. This executes on every block of data (potentially millions of rows) inserted into the table `otel_traces`. This summarized data is, in turn, inserted into a target table `otel_traces_trace_id_ts`. Below we show several rows from this table and its schema:

<pre style="font-size: 12px;"><code class="hljs language-sql"><span class="hljs-keyword">SELECT</span> <span class="hljs-operator">*</span>
<span class="hljs-keyword">FROM</span> otel_traces_trace_id_ts
LIMIT <span class="hljs-number">5</span>

┌─TraceId──────────────────────────┬─────────────────────────<span class="hljs-keyword">Start</span>─┬───────────────────────────<span class="hljs-keyword">End</span>─┐
│ <span class="hljs-number">000040</span>cf204ee714c38565dd057f4d97 │ <span class="hljs-number">2023</span><span class="hljs-number">-03</span><span class="hljs-number">-20</span> <span class="hljs-number">18</span>:<span class="hljs-number">39</span>:<span class="hljs-number">44.064898664</span> │ <span class="hljs-number">2023</span><span class="hljs-number">-03</span><span class="hljs-number">-20</span> <span class="hljs-number">18</span>:<span class="hljs-number">39</span>:<span class="hljs-number">44.066019830</span> │
│ <span class="hljs-number">00009</span>bdf67123e6d50877205680f14bf │ <span class="hljs-number">2023</span><span class="hljs-number">-03</span><span class="hljs-number">-21</span> <span class="hljs-number">07</span>:<span class="hljs-number">56</span>:<span class="hljs-number">30.185195776</span> │ <span class="hljs-number">2023</span><span class="hljs-number">-03</span><span class="hljs-number">-21</span> <span class="hljs-number">07</span>:<span class="hljs-number">56</span>:<span class="hljs-number">30.503208045</span> │
│ <span class="hljs-number">0000</span>c8e1e9f5f910c02a9a98aded04bd │ <span class="hljs-number">2023</span><span class="hljs-number">-03</span><span class="hljs-number">-20</span> <span class="hljs-number">18</span>:<span class="hljs-number">31</span>:<span class="hljs-number">35.967373056</span> │ <span class="hljs-number">2023</span><span class="hljs-number">-03</span><span class="hljs-number">-20</span> <span class="hljs-number">18</span>:<span class="hljs-number">31</span>:<span class="hljs-number">35.968602368</span> │
│ <span class="hljs-number">0000</span>c8e1e9f5f910c02a9a98aded04bd │ <span class="hljs-number">2023</span><span class="hljs-number">-03</span><span class="hljs-number">-20</span> <span class="hljs-number">18</span>:<span class="hljs-number">31</span>:<span class="hljs-number">36.032750972</span> │ <span class="hljs-number">2023</span><span class="hljs-number">-03</span><span class="hljs-number">-20</span> <span class="hljs-number">18</span>:<span class="hljs-number">31</span>:<span class="hljs-number">36.032750972</span> │
│ <span class="hljs-number">0000</span>dc7a6d15c638355b33b3c6a8aaa2 │ <span class="hljs-number">2023</span><span class="hljs-number">-03</span><span class="hljs-number">-21</span> <span class="hljs-number">00</span>:<span class="hljs-number">31</span>:<span class="hljs-number">37.075681536</span> │ <span class="hljs-number">2023</span><span class="hljs-number">-03</span><span class="hljs-number">-21</span> <span class="hljs-number">00</span>:<span class="hljs-number">31</span>:<span class="hljs-number">37.247680719</span> │
└──────────────────────────────────┴───────────────────────────────┴───────────────────────────────┘

<span class="hljs-number">5</span> <span class="hljs-keyword">rows</span> <span class="hljs-keyword">in</span> set. Elapsed: <span class="hljs-number">0.009</span> sec.


<span class="hljs-keyword">CREATE</span> <span class="hljs-keyword">TABLE</span> otel_traces_trace_id_ts
(
	`TraceId` String CODEC(ZSTD(<span class="hljs-number">1</span>)),
	`<span class="hljs-keyword">Start</span>` DateTime64(<span class="hljs-number">9</span>) CODEC(Delta(<span class="hljs-number">8</span>), ZSTD(<span class="hljs-number">1</span>)),
	`<span class="hljs-keyword">End</span>` DateTime64(<span class="hljs-number">9</span>) CODEC(Delta(<span class="hljs-number">8</span>), ZSTD(<span class="hljs-number">1</span>)),
	INDEX idx_trace_id TraceId TYPE bloom_filter(<span class="hljs-number">0.01</span>) GRANULARITY <span class="hljs-number">1</span>
)
ENGINE <span class="hljs-operator">=</span> MergeTree
<span class="hljs-keyword">ORDER</span> <span class="hljs-keyword">BY</span> (TraceId, toUnixTimestamp(<span class="hljs-keyword">Start</span>))
TTL toDateTime(<span class="hljs-keyword">Start</span>) <span class="hljs-operator">+</span> toIntervalDay(<span class="hljs-number">3</span>)
</code></pre>

As shown, the target table `otel_traces_trace_id_ts` uses `(TraceId,toUnixTimestamp(Start))` for its `ORDER BY` key.  This thus allows users to quickly identify a specific trace's time range. 

<blockquote style="font-size: 14px;">
<p>We explore the value of this materialized view in "Querying Traces" below but have found its value limited in speeding up wider queries performing TraceId lookups. However, it does provide an excellent getting started example from which users can take inspiration.</p>
</blockquote>

Users may wish to extend or modify this materialized view. For example, an array of `ServiceName` could be added to the materialized views aggregation and target table to allow fast identification of a traces service. This can be achieved by pre-creating the table and materialized view before deploying the collector or [alternatively modifying the view and table post-creation](https://clickhouse.com/docs/en/sql-reference/statements/alter/view#alter-live-view-statement). Users can also attach new materialized views to the main table to address other access pattern requirements. See [our recent blog](https://clickhouse.com/blog/using-materialized-views-in-clickhouse) for further details.

Finally, the above capability could also be implemented [using projections](https://clickhouse.com/blog/clickhouse-faster-queries-with-projections-and-primary-indexes). While these don't provide all of the capabilities of Materialized views, they are directly included in the table definition. Unlike Materialized Views, projections are updated atomically and kept consistent with the main table, with ClickHouse automatically choosing the optimal version at query time. 

## Querying Traces

The [docs for the exporter](https://github.com/open-telemetry/opentelemetry-collector-contrib/blob/main/exporter/clickhouseexporter/README.md#traces) provide some excellent getting-started queries. Users needing further inspiration can refer to [the queries](https://gist.github.com/gingerwizard/dbc250063933d76462faf117b4d56b9a) in the dashboard we present below. A few important concepts when querying for traces:

* TraceId look-ups on the main `otel_traces` table can potentially be expensive, despite the bloom filter. Should you need to drill down on a specific trace, the `otel_traces_trace_id_ts` table can potentially be used to identify the time range of the trace - as noted above. This time range then be applied as an additional filter to the `otel_traces` table, which includes the timestamp in the ORDER BY key. The query can be further optimized if the ServiceName is applied as a filter to the query (although this will limit to spans from a specific service). Consider the two query variants below and their respective timings, both of which return the spans associated with a trace. 

   Using only the `otel_traces` table:

   ```sql
   SELECT
           Timestamp,
	   TraceId,
	   SpanId,
	   SpanName
   FROM otel_traces
   WHERE TraceId = '0f8a2c02d77d65da6b2c4d676985b3ab'
   ORDER BY Timestamp ASC
   
   50 rows in set. Elapsed: 0.197 sec. Processed 298.77 thousand rows, 17.39 MB (1.51 million rows/s., 88.06 MB/s.)
   ```

   When exploiting our `otel_traces_trace_id_ts` table and using the resulting times to apply a filter:
   
   <pre><code class="hljs language-sql" style="font-size:12px;"><span class="hljs-keyword">WITH</span> <span class="hljs-string">'0f8a2c02d77d65da6b2c4d676985b3ab'</span> <span class="hljs-      keyword">AS</span> trace_id,
       (
 	      <span class="hljs-keyword">SELECT</span> <span class="hljs-built_in">min</span>(<span class="hljs-keyword">Start</span>)
 	      <span class="hljs-keyword">FROM</span> otel_traces_trace_id_ts
    	   <span class="hljs-keyword">WHERE</span> TraceId <span class="hljs-operator">=</span> trace_id
       ) <span class="hljs-keyword">AS</span> <span class="hljs-keyword">start</span>,
       (
    	   <span class="hljs-keyword">SELECT</span> <span class="hljs-built_in">max</span>(<span class="hljs-keyword">End</span>) <span class="hljs-operator">+</span> <span class="hljs-   number">1</span>
    	   <span class="hljs-keyword">FROM</span> otel_traces_trace_id_ts
    	   <span class="hljs-keyword">WHERE</span> TraceId <span class="hljs-operator">=</span> trace_id
       ) <span class="hljs-keyword">AS</span> <span class="hljs-keyword">end</span>
   <span class="hljs-keyword">SELECT</span>  <span class="hljs-type">Timestamp</span>,
       TraceId,
       SpanId,
       SpanName
   <span class="hljs-keyword">FROM</span> otel_traces
   <span class="hljs-keyword">WHERE</span> (TraceId <span class="hljs-operator">=</span> trace_id) <span class="hljs-keyword">AND</span> (<span class="hljs-type">Timestamp</span> <span class="hljs-operator">&gt;=</span> <span class="hljs-keyword">start</span>) <span class="hljs-keyword">AND</span> (<span class="hljs-type">Timestamp</span> <span class="hljs-operator">&lt;=</span> <span class="hljs-keyword">end</span>)
   <span class="hljs-keyword">ORDER</span> <span class="hljs-keyword">BY</span> <span class="hljs-type">Timestamp</span> <span class="hljs-keyword">ASC</span>

   <span class="hljs-number">50</span> <span class="hljs-keyword">rows</span> <span class="hljs-keyword">in</span> set. Elapsed: <span class="hljs-number">0.110</span> sec. Processed <span    class="hljs-number">225.05</span> thousand <span class="hljs-keyword">rows</span>, <span class="hljs-number">12.78</span> MB (<span class="hljs-number">2.05</span> million <span class="hljs-   keyword">rows</span><span class="hljs-operator">/</span>s., <span class="hljs-number">116.52</span> MB<span class="hljs-operator">/</span>s.)
   </code></pre>

   Our data volume here is small (around 200m spans and 125GB of data), so absolute timings and differences are low. While we expect these differences to widen on larger datasets, our testing suggests this   materialized view provides only moderate speedups (note the small difference in rows read) - unsurprising as the Timestamp column is the third key in the otel_traces table `ORDER BY` and can thus, at best, be used for a [generic exclusion search](https://clickhouse.com/docs/en/optimize/sparse-primary-indexes#generic-exclusion-search-algorithm). The `otel_traces` table is also already significantly benefiting from the bloom filter. A [full `EXPLAIN` of the differences](https://gist.github.com/gingerwizard/8749e42fbe51509a4bea33017fdd4b4f) in these queries shows a small difference in the number of granules read post-filtering. For this reason, we consider the use of this materialized view to be an unnecessary optimization in most cases when balanced against the increase in query complexity, although some users may find it useful for performance-critical scenarios. In later posts, we will explore the possibility of using projections to accelerate lookups by TraceId.

* The collector utilizes the Map data type for attributes. Users can use a [map notation ](https://clickhouse.com/docs/en/sql-reference/data-types/map)to access the nested keys in addition to specialized ClickHouse [map functions](https://clickhouse.com/docs/en/sql-reference/functions/tuple-map-functions#map) if filtering or selecting these columns. As noted earlier, if you frequently access these keys, we recommend materializing them as an explicit column on the table. Below we query spans from a specific host, grouping by the hour and the language of the service. We compute percentiles of span duration for each bucket - [useful in any issue diagnosis](https://opentelemetry.io/docs/demo/scenarios/recommendation-cache/).

   ```sql
   SELECT
	   toStartOfHour(Timestamp) AS hour,
	   count(*),
	   lang,
	   avg(Duration) AS avg,
	   quantile(0.9)(Duration) AS p90,
	   quantile(0.95)(Duration) AS p95,
	   quantile(0.99)(Duration) AS p99
   FROM otel_traces
   WHERE (ResourceAttributes['host.name']) = 'bcea43b12a77'
   GROUP BY
	   hour,
	   ResourceAttributes['telemetry.sdk.language'] AS lang
   ORDER BY hour ASC
  ```

   Identifying the available map keys for querying can be challenging - especially if application developers have added custom metadata. Using an [aggregator combinator function](https://clickhouse.com/blog/aggregate-functions-combinators-in-clickhouse-for-arrays-maps-and-states#working-with-aggregation-states), the following query identifies the keys within the `ResourceAttributes` column. Adapt to other columns, e.g., `SpanAttributes`, as required.

   ```sql
   SELECT groupArrayDistinctArray(mapKeys(ResourceAttributes)) AS `Resource Keys`
   FROM otel_traces
   FORMAT Vertical

   Row 1:
   ──────
   Resource Keys:    ['telemetry.sdk.name','telemetry.sdk.language','container.id','os.name','os.description','process.pid','process.executable.name','service.namespace','telemetry.auto.version','os.type','process.runtime.description','process.executable.path','host.arch','process.runtime.version','process.runtime.name','process.command_args','process.owner','host.name','service.instance.id','telemetry.sdk.version','process.command_line','service.name','process.command','os.version']

   1 row in set. Elapsed: 0.330 sec. Processed 1.52 million rows, 459.89 MB (4.59 million rows/s., 1.39 GB/s.)
   ```

## Using Grafana to Visualize & Diagnose

We recommend Grafana for visualizing and exploring trace data using the [official ClickHouse plugin](https://grafana.com/grafana/plugins/grafana-clickhouse-datasource/). [Previous posts](https://clickhouse.com/blog/visualizing-data-with-grafana) and [videos](https://www.youtube.com/watch?v=Ve-VPDxHgZU) have explored this plugin in depth. Recently we have enhanced the plugin to allow visualization of traces using the [Trace Panel](https://grafana.com/docs/grafana/latest/panels-visualizations/visualizations/traces/). This is supported as both a visualization and as a component in [Explore](https://grafana.com/docs/grafana/latest/explore/trace-integration/). This panel has [strict naming and type requirements ](https://grafana.com/docs/grafana/latest/explore/trace-integration/#data-api)for columns which, unfortunately, is not aligned with the OTEL specification at the time of writing. The following query produces the appropriate response for a trace to be rendered in the Trace visualization:

<pre><code class="hljs language-sql" style="font-size:12px"><span class="hljs-keyword">WITH</span>
	<span class="hljs-string">'ec4cff3e68be6b24f35b4eef7e1659cb'</span> <span class="hljs-keyword">AS</span> trace_id,
	(
    	<span class="hljs-keyword">SELECT</span> <span class="hljs-built_in">min</span>(<span class="hljs-keyword">Start</span>)
    	<span class="hljs-keyword">FROM</span> otel_traces_trace_id_ts
    	<span class="hljs-keyword">WHERE</span> TraceId <span class="hljs-operator">=</span> trace_id
	) <span class="hljs-keyword">AS</span> <span class="hljs-keyword">start</span>,
	(
    	<span class="hljs-keyword">SELECT</span> <span class="hljs-built_in">max</span>(<span class="hljs-keyword">End</span>) <span class="hljs-operator">+</span> <span class="hljs-number">1</span>
    	<span class="hljs-keyword">FROM</span> otel_traces_trace_id_ts
    	<span class="hljs-keyword">WHERE</span> TraceId <span class="hljs-operator">=</span> trace_id
	) <span class="hljs-keyword">AS</span> <span class="hljs-keyword">end</span>
<span class="hljs-keyword">SELECT</span>
	TraceId <span class="hljs-keyword">AS</span> traceID,
	SpanId <span class="hljs-keyword">AS</span> spanID,
	SpanName <span class="hljs-keyword">AS</span> operationName,
	ParentSpanId <span class="hljs-keyword">AS</span> parentSpanID,
	ServiceName <span class="hljs-keyword">AS</span> serviceName,
	Duration <span class="hljs-operator">/</span> <span class="hljs-number">1000000</span> <span class="hljs-keyword">AS</span> duration,
	<span class="hljs-type">Timestamp</span> <span class="hljs-keyword">AS</span> startTime,
	arrayMap(key <span class="hljs-operator">-</span><span class="hljs-operator">&gt;</span> map(<span class="hljs-string">'key'</span>, key, <span class="hljs-string">'value'</span>, SpanAttributes[key]), mapKeys(SpanAttributes)) <span class="hljs-keyword">AS</span> tags,
	arrayMap(key <span class="hljs-operator">-</span><span class="hljs-operator">&gt;</span> map(<span class="hljs-string">'key'</span>, key, <span class="hljs-string">'value'</span>, ResourceAttributes[key]), mapKeys(ResourceAttributes)) <span class="hljs-keyword">AS</span> serviceTags
<span class="hljs-keyword">FROM</span> otel_traces
<span class="hljs-keyword">WHERE</span> (TraceId <span class="hljs-operator">=</span> trace_id) <span class="hljs-keyword">AND</span> (<span class="hljs-type">Timestamp</span> <span class="hljs-operator">&gt;=</span> <span class="hljs-keyword">start</span>) <span class="hljs-keyword">AND</span> (<span class="hljs-type">Timestamp</span> <span class="hljs-operator">&lt;=</span> <span class="hljs-keyword">end</span>)
<span class="hljs-keyword">ORDER</span> <span class="hljs-keyword">BY</span> startTime <span class="hljs-keyword">ASC</span>
</code></pre>

<a href='/uploads/grafana_trace_34d527cf86.png' target='_blank'><img src='/uploads/grafana_trace_34d527cf86.png'/></a>

Using [variables](https://grafana.com/docs/grafana/latest/dashboards/variables/) and [data links](https://grafana.com/docs/grafana/latest/panels-visualizations/configure-data-links/) in Grafana, users can produce complex workflows where visualizations can be filtered interactivity. The following dashboard contains several visualizations:

* A overview of service request volume as a stacked bar
* 99th percentile of latency of each service as a multi-line
* Error rates per service as a bar
* A list of traces aggregated by traceId - the service is here the first in the span chain.
* A Trace Panel that populates when we filter to a specific trace.

This dashboard gives us some basic diagnostic capabilities around errors and performance. The OpenTelemetry demo has [existing scenarios ](https://opentelemetry.io/docs/demo/scenarios/)where the user can enable specific issues on the service. One of these scenarios involves a[ memory leak in the recommendation service](https://opentelemetry.io/docs/demo/scenarios/recommendation-cache/). Without metrics, we can’t complete the entire issue resolution flow but can identify problematic traces. We show this below:

<a href='/uploads/grafana_trace_66c848f8e5.gif' target='_blank'><img src='/uploads/grafana_trace_66c848f8e5.gif'/></a>

This dashboard is now [packaged with the plugin](https://github.com/grafana/clickhouse-datasource/pull/336), and available [with the demo](https://github.com/ClickHouse/opentelemetry-demo/blob/main/src/grafana/provisioning/dashboards/general/otel-traces-clickhouse.json).

## Using Parameterized Views

The above queries can be quite complex. For example, notice how we are forced to utilize an `arrayMap` function to ensure the attributes are correctly structured. We could defer this work to a [materialized or default column](https://clickhouse.com/docs/en/sql-reference/statements/create/table#materialized) at query time, thus simplifying the query. However, this will still require significant SQL. This can be especially tedious when visualizing a trace in the Explore view.

To simplify query syntax, ClickHouse offers parameterized views. Parametrized views are similar to normal views but can be created with parameters that are not resolved immediately. These views can be used with table functions, which specify the name of the view as the function name and the parameter values as its arguments. This can dramatically reduce the end user's required syntax in ClickHouse. Below we create a view that accepts a trace id and returns the results required for the Trace View. Although support for CTEs in parametized views [was recently added](https://github.com/ClickHouse/ClickHouse/pull/48065), but below we use the simpler query from earlier:


```sql
CREATE VIEW trace_view AS
SELECT
	TraceId AS traceID,
	SpanId AS spanID,
	SpanName AS operationName,
	ParentSpanId AS parentSpanID,
	ServiceName AS serviceName,
	Duration / 1000000 AS duration,
	Timestamp AS startTime,
	arrayMap(key -> map('key', key, 'value', SpanAttributes[key]), mapKeys(SpanAttributes)) AS tags,
	arrayMap(key -> map('key', key, 'value', ResourceAttributes[key]), mapKeys(ResourceAttributes)) AS serviceTags
FROM otel_traces
WHERE TraceId = {trace_id:String}
```

To run this view, we simply pass a trace id e.g.,

```sql
SELECT *
FROM trace_view(trace_id = '1f12a198ac3dd502d5201ccccad52967')
```

This can significantly reduce the complexity of querying for traces. Below we use the [Explore view](https://grafana.com/docs/grafana/latest/explore/) to query for a specific trace. Notice the need to set the `Format` value to `Trace` to cause rendering of the trace:

<a href='/uploads/trace_explore_e103da50d9.gif' target='_blank'><img src='/uploads/trace_explore_e103da50d9.gif'/></a>

Parametrized views are best employed for common workloads where users perform common tasks that require ad-hoc analysis, such as inspecting a specific trace.

## Compression

One of the benefits of ClickHouse for storing trace data is its high compression. Using the query below, we can see we achieve compression rates of 9x-10x on the trace data generated by this demo. This dataset was generated by running the demo while subjected to 2000 virtual users for 24 hours using the [load generator service](https://opentelemetry.io/docs/demo/services/load-generator/) provided. We have made this dataset available for public use. This can be inserted using the steps [here](https://gist.github.com/gingerwizard/1b8755a86621fd492bbd28cfab84603c). For hosting this data, we recommend a [development service in ClickHouse Cloud](https://clickhouse.cloud/signUp) (16GB, two cores), which is more than sufficient for a dataset of this size.

<pre><code style="font-size:12px;" class="hljs language-sql"><span class="hljs-keyword">SELECT</span>
	formatReadableSize(<span class="hljs-built_in">sum</span>(data_compressed_bytes)) <span class="hljs-keyword">AS</span> compressed_size,
	formatReadableSize(<span class="hljs-built_in">sum</span>(data_uncompressed_bytes)) <span class="hljs-keyword">AS</span> uncompressed_size,
	round(<span class="hljs-built_in">sum</span>(data_uncompressed_bytes) <span class="hljs-operator">/</span> <span class="hljs-built_in">sum</span>(data_compressed_bytes), <span class="hljs-number">2</span>) <span class="hljs-keyword">AS</span> ratio
<span class="hljs-keyword">FROM</span> system.columns
<span class="hljs-keyword">WHERE</span> <span class="hljs-keyword">table</span> <span class="hljs-operator">=</span> <span class="hljs-string">'otel_traces'</span>
<span class="hljs-keyword">ORDER</span> <span class="hljs-keyword">BY</span> <span class="hljs-built_in">sum</span>(data_compressed_bytes) <span class="hljs-keyword">DESC</span>

┌─compressed_size─┬─uncompressed_size─┬─ratio─┐
│ <span class="hljs-number">13.68</span> GiB   	  │ <span class="hljs-number">132.98</span> GiB    	  │  <span class="hljs-number">9.72</span> │
└─────────────────┴───────────────────┴───────┘

<span class="hljs-number">1</span> <span class="hljs-type">row</span> <span class="hljs-keyword">in</span> set. Elapsed: <span class="hljs-number">0.003</span> sec.

<span class="hljs-keyword">SELECT</span>
	name,
	formatReadableSize(<span class="hljs-built_in">sum</span>(data_compressed_bytes)) <span class="hljs-keyword">AS</span> compressed_size,
	formatReadableSize(<span class="hljs-built_in">sum</span>(data_uncompressed_bytes)) <span class="hljs-keyword">AS</span> uncompressed_size,
	round(<span class="hljs-built_in">sum</span>(data_uncompressed_bytes) <span class="hljs-operator">/</span> <span class="hljs-built_in">sum</span>(data_compressed_bytes), <span class="hljs-number">2</span>) <span class="hljs-keyword">AS</span> ratio
<span class="hljs-keyword">FROM</span> system.columns
<span class="hljs-keyword">WHERE</span> <span class="hljs-keyword">table</span> <span class="hljs-operator">=</span> <span class="hljs-string">'otel_traces'</span>
<span class="hljs-keyword">GROUP</span> <span class="hljs-keyword">BY</span> name
<span class="hljs-keyword">ORDER</span> <span class="hljs-keyword">BY</span> <span class="hljs-built_in">sum</span>(data_compressed_bytes) <span class="hljs-keyword">DESC</span>

┌─name───────────────┬─compressed_size─┬─uncompressed_size─┬───ratio─┐
│ ResourceAttributes │ <span class="hljs-number">2.97</span> GiB    	   │ <span class="hljs-number">78.49</span> GiB     	   │   <span class="hljs-number">26.43</span> │
│ TraceId        	 │ <span class="hljs-number">2.75</span> GiB    	   │ <span class="hljs-number">6.31</span> GiB      	   │	<span class="hljs-number">2.29</span> │
│ SpanAttributes 	 │ <span class="hljs-number">1.99</span> GiB    	   │ <span class="hljs-number">22.90</span> GiB     	   │   <span class="hljs-number">11.52</span> │
│ SpanId         	 │ <span class="hljs-number">1.68</span> GiB    	   │ <span class="hljs-number">3.25</span> GiB      	   │	<span class="hljs-number">1.94</span> │
│ ParentSpanId   	 │ <span class="hljs-number">1.35</span> GiB    	   │ <span class="hljs-number">2.74</span> GiB      	   │	<span class="hljs-number">2.02</span> │
│ Events.Timestamp   │ <span class="hljs-number">1.02</span> GiB        │ <span class="hljs-number">3.47</span> GiB      	   │ 	<span class="hljs-number">3.4</span>  │
│ <span class="hljs-type">Timestamp</span>      	 │ <span class="hljs-number">955.77</span> MiB  	   │ <span class="hljs-number">1.53</span> GiB      	   │	<span class="hljs-number">1.64</span> │
│ Duration       	 │ <span class="hljs-number">619.43</span> MiB  	   │ <span class="hljs-number">1.53</span> GiB      	   │	<span class="hljs-number">2.53</span> │
│ Events.Attributes  │ <span class="hljs-number">301.09</span> MiB      │ <span class="hljs-number">5.12</span> GiB      	   │   <span class="hljs-number">17.42</span> │
│ Links.TraceId  	 │ <span class="hljs-number">36.52</span> MiB       │ <span class="hljs-number">1.60</span> GiB      	   │   <span class="hljs-number">44.76</span> │
│ Events.Name    	 │ <span class="hljs-number">22.92</span> MiB       │ <span class="hljs-number">248.91</span> MiB    	   │   <span class="hljs-number">10.86</span> │
│ Links.SpanId   	 │ <span class="hljs-number">17.77</span> MiB       │ <span class="hljs-number">34.49</span> MiB     	   │	<span class="hljs-number">1.94</span> │
│ HostName       	 │ <span class="hljs-number">8.32</span> MiB        │ <span class="hljs-number">4.56</span> GiB      	   │  <span class="hljs-number">561.18</span> │
│ StatusCode     	 │ <span class="hljs-number">1.11</span> MiB    	   │ <span class="hljs-number">196.80</span> MiB        │  <span class="hljs-number">177.18</span> │
│ StatusMessage  	 │ <span class="hljs-number">1.09</span> MiB    	   │ <span class="hljs-number">219.08</span> MiB    	   │  <span class="hljs-number">201.86</span> │
│ SpanName       	 │ <span class="hljs-number">538.55</span> KiB  	   │ <span class="hljs-number">196.82</span> MiB    	   │  <span class="hljs-number">374.23</span> │
│ SpanKind       	 │ <span class="hljs-number">529.98</span> KiB  	   │ <span class="hljs-number">196.80</span> MiB    	   │  <span class="hljs-number">380.25</span> │
│ ServiceName    	 │ <span class="hljs-number">529.09</span> KiB  	   │ <span class="hljs-number">196.81</span> MiB    	   │   <span class="hljs-number">380.9</span> │
│ TraceState     	 │ <span class="hljs-number">138.05</span> KiB  	   │ <span class="hljs-number">195.93</span> MiB    	   │ <span class="hljs-number">1453.35</span> │
│ Links.Attributes   │ <span class="hljs-number">11.10</span> KiB   	   │ <span class="hljs-number">16.23</span> MiB     	   │ <span class="hljs-number">1496.99</span> │
│ Links.TraceState   │ <span class="hljs-number">1.71</span> KiB    	   │ <span class="hljs-number">2.03</span> MiB          │ <span class="hljs-number">1218.44</span> │
└────────────────────┴─────────────────┴───────────────────┴─────────┘

<span class="hljs-number">20</span> <span class="hljs-keyword">rows</span> <span class="hljs-keyword">in</span> set. Elapsed: <span class="hljs-number">0.003</span> sec.
</code></pre>

We explore schema optimization and how this compression rate can be further improved in a later blog post in this series.

## Further work

The current ClickHouse Exporter is in alpha. This state reflects the relative recency of its release and maturity. While we plan to invest in this exporter, we have identified a number of challenges and possible improvements:

* **Schema** - The schema contains a number of optimizations that potentially be premature. The use of bloom filters may be unnecessary for some workloads. As shown below, these consume space (around 1% of the total data size). 

   <pre style="font-size: 12px;"><code class="hljs language-sql"><span class="hljs-keyword">SELECT</span>
    formatReadableSize(<span class="hljs-built_in">sum</span>(secondary_indices_compressed_bytes)) <span class="hljs-keyword">AS</span> compressed_size,
    formatReadableSize(<span class="hljs-built_in">sum</span>(secondary_indices_uncompressed_bytes)) <span class="hljs-keyword">AS</span> uncompressed_size
   <span class="hljs-keyword">FROM</span> system.parts
   <span class="hljs-keyword">WHERE</span> (<span class="hljs-keyword">table</span> <span class="hljs-operator">=</span> <span class="hljs-string">'otel_traces'</span>) <span class="hljs-keyword">AND</span> active
   
   ┌─compressed_size─┬─uncompressed_size─┐
   │ <span class="hljs-number">425.54</span> MiB      │ <span class="hljs-number">1.36</span> GiB          │
   └─────────────────┴───────────────────┘
   </code></pre>
   We have found the filter on the `TraceId` column to be effective and a worthy addition to the schema. This seems to negate most of the benefit of the materialized view, which adds questionable value for the additional query and maintenance complexity. However, it provides an excellent example of how materialized views can potentially be applied to accelerate queries. We have insufficient evidence to testify to the value of other bloom filters and would recommend users experiment.
* **High memory** - We have found the OTEL collector to be very memory intensive. In the earlier configuration, we use the [batch processor](https://github.com/open-telemetry/opentelemetry-collector/blob/main/processor/batchprocessor/README.md) to send data to ClickHouse after 5s or when the batch reaches 100,000 rows. While this optimizes for ClickHouse inserts and adheres to [best practices](https://clickhouse.com/docs/en/cloud/bestpractices/bulk-inserts), it can be very memory intensive under high load - especially when [collecting logs](https://clickhouse.com/blog/storing-log-data-in-clickhouse-fluent-bit-vector-open-telemetry). This can be mitigated by reducing the flush time and/or batch size. Be aware that this requires tuning as it may cause e[xcessive parts to accumulate in ClickHouse](https://clickhouse.com/docs/knowledgebase/exception-too-many-parts). Alternatively, users may wish to use [asynchronous inserts ](https://clickhouse.com/docs/en/cloud/bestpractices/asynchronous-inserts)to send data. This will reduce the batch size but is only supported over HTTP in the exporter. To activate, use the `connection_params` in the exporter config, e.g.,

   ```yaml
   connection_params:
    	async_insert: 1
    	wait_for_async_insert: 0
  ```
   Note that this will not be as efficient for inserts to ClickHouse.
* **End-to-end delivery** - We currently see no support for end-to-end delivery guarantees. i.e., the application SDKs will consider a trace sent once the Collector receives it. If the OTEL Collector crashes, batches currently in memory will be lost. This can be mitigated by reducing the batch size (see above). However, users may also wish to consider alternative architectures involving Kafka (see [receiver](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/receiver/kafkareceiver) and [exporter](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/exporter/kafkaexporter)) or equivalent persistent queues if higher delivery guarantees are required. We have not explored the [recent persistent queues feature](https://github.com/open-telemetry/opentelemetry-collector/tree/main/exporter/exporterhelper#persistent-queue), which is in alpha but promises to improve resilience.

* **Scaling** - The above deployment only utilizes a single collector. In a high-volume production environment, it is likely users would need to deploy multiple collectors behind a load balancer. The OTEL collector supports this using a [Trace Id/Service Name load-balancing exporter](https://github.com/open-telemetry/opentelemetry-collector-contrib/blob/main/exporter/loadbalancingexporter/README.md). This ensures spans from the same trace are forwarded to the same collector. Note that we have also made no effort to tune agents or measure their resource overhead - something we recommend users research or do before production deployment. We plan to explore these topics in later posts. 
* **Sampling** - Our current implementation results in all data being stored in ClickHouse. While ClickHouse offers fantastic compression, we appreciate that users will wish to employ [sampling techniques](https://opentelemetry.io/blog/2022/tail-sampling/). This allows only a subset of traces to be stored, thus reducing hardware requirements. Be aware this[ complicates scaling](https://opentelemetry.io/blog/2022/tail-sampling/#limitations-of-opentelemetry). We will address this in a later post.

## Conclusion

This blog post shows how traces can easily be collected and stored in ClickHouse using OpenTelemetry. We have forked the OpenTelemetry demo to support ClickHouse, touched on queries and visualization techniques using Grafana, and highlighted some approaches to reducing query complexity and some of the future work for the project. For further reading, we encourage users to explore topics beyond this post, such as how the OTEL collector can be deployed at scale, handling backpressure, and delivery guarantees. We will explore these topics in a later post and add metrics data to our ClickHouse instance before also exploring how schemas can be optimized, and data managed with lifecycle features.