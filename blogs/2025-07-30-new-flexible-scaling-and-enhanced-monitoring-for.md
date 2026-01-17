---
title: "New: Flexible scaling and enhanced monitoring for streaming ClickPipes"
date: "2025-07-30T10:54:29.617Z"
author: "ClickPipes Team"
category: "Product"
excerpt: "Streaming ClickPipes now support flexible scaling and enhanced monitoring,  giving you full control over cost and performance for your evolving ingestion workloads."
---

# New: Flexible scaling and enhanced monitoring for streaming ClickPipes

## Introduction

Data ingestion workloads come in all shapes and sizes, with more or less predictable patterns. When we built [ClickPipes](https://clickhouse.com/cloud/clickpipes), we wanted to enable customers to handle any throughput, data size and topologies from the most common building blocks of data infrastructure: object storage, message brokers, and databases. Today, hundreds of customers rely on ClickPipes as a cost-effective solution to manage real-time data ingestion into ClickHouse Cloud at scale, including [Property Finder](https://clickhouse.com/blog/how-property-finder-migrated-to-clickhouse), [Flock Safety](https://clickhouse.com/blog/why-flock-safety-turned-to-clickhouse), and [Seemplicity](https://clickhouse.com/blog/seemplicity-scaled-real-time-security-analytics-with-postgres-cdc-and-clickhouse).

As the product evolves, one of the most common requests has been to provide greater flexibility in configuring streaming ClickPipes to better suit the specific needs of these diverse ingestion workloads. In response, we’re introducing **new scaling options** that allow you to control both **horizontal and vertical scaling** for your streaming ClickPipes! You can now choose the number of replicas and replica sizes directly, along with improved monitoring to help you track resource usage over time.


### How does sizing work in streaming ClickPipes?

> **Note**: database and object storage ClickPipes have a different architecture, which doesn’t require direct control over compute allocation. This new feature applies exclusively to streaming ClickPipes to give customers more control over the cost-performance ratio per ClickPipe.

ClickPipes works by deploying replica(s) within ClickHouse Cloud, each acting as a consumer of your Kafka or Kinesis streaming data source. By default, ClickPipes starts with a single Extra Small replica (0.125 vCPU, 512 MiB RAM) to process your data streams. These replicas fetch data in parallel, process and transform it as needed, commit stream offsets, and write the results directly into your ClickHouse service. This architecture enables high-throughput, scalable ingestion with fault tolerance, and efficient load distribution across replicas.

![unnamed.png](https://clickhouse.com/uploads/unnamed_357981c8a1.png)

### What are replicas?

In the context of ClickPipes, replicas are instances of your data processing pipeline that work in parallel to handle the incoming data streams. Each replica acts as a consumer of your Kafka or Kinesis stream, allowing the system to scale efficiently and maintain performance as data volumes grow. Replicas can be scaled both vertically and horizontally to match the specific needs of your workload.


## Flexible scaling options

We've introduced two new scaling options to provide you with finer control over the topology of streaming ClickPipes: number of replicas (*horizontal scaling*) and replica size (*vertical scaling*). These scaling options can be selected in the UI (shown below) when creating a new ClickPipe or editing an existing one. Scaling is also supported via [OpenAPI](https://clickhouse.com/docs/cloud/manage/api/swagger#tag/ClickPipes/paths/~1v1~1organizations~1%7BorganizationId%7D~1services~1%7BserviceId%7D~1clickpipes~1%7BclickPipeId%7D~1scaling/patch) and [Terraform](https://github.com/ClickHouse/terraform-provider-clickhouse/blob/619ba02fc70e5d672e221f424a9aeedc43fa2d0a/examples/clickpipe/multiple_pipes_example/main.tf).

![unnamed.gif](https://clickhouse.com/uploads/unnamed_8240b37fa9.gif)

### Vertical scaling

Vertical scaling, or *scaling up*, involves increasing the resources (CPU and memory) allocated to individual replicas within your ClickPipe. This is ideal for workloads that require more processing power per replica, such as Kafka or Kinesis streams with large payloads or complex schemas. Vertical scaling supports the following configurations:

| Replica size           | CPU          | Memory  |
|------------------------|--------------|--------|
| Extra Small (default)  | 0.125 Cores  | 512 Mb |
| Small                  | 0.25 Cores   | 1 Gb   |
| Medium                 | 0.5 Cores    | 2 Gb   |
| Large                  | 1 Core       | 4 Gb   |
| Extra Large            | 2 Cores      | 8 Gb   |

### Benchmarks for sizing

Below is a sample performance benchmark for a Large-sized ClickPipe replica (1 vCPU / 4 GB) ingesting data from a Kafka stream. You can use these benchmarks as a reference point when choosing the appropriate replica size for your workload. For more details and additional sizing guidance, refer to the documentation.

| Replica Size | Message Size | Data Format | Throughput |
|-------------|--------------|-------------|------------|
| Large       | 1.6 kb       | JSON        | 63 mb/s    |
| Large       | 1.6 kb       | AVRO        | 99 mb/s    |

### Horizontal scaling

Horizontal scaling, or *scaling out*, involves adding more replicas to your ClickPipe. This is highly effective for distributing workloads across multiple replicas, allowing your system to handle a higher volume of data concurrently. Kafka and Kinesis efficiently handle horizontal scaling by spreading data across multiple partitions and shards, respectively, which ClickPipes can handle by horizontally scaling proportionally.


## Enhanced resource monitoring

The details page for each ClickPipe now includes per-replica CPU and memory usage, showing average resource utilization across replicas. Additionally, the charts show the replicas CPU and memory limits — including *scale up* and *scale out* events — for easier tracking of utilization over time. This helps you better understand your workloads and plan resizing operations with confidence.

![unnamed (1).png](https://clickhouse.com/uploads/unnamed_1_301ef80db2.png)

## How does flexible scaling affect pricing?

Previously, streaming ClickPipes were priced at a flat rate of $0.05 per hour for each replica (by default, size Medium). With the introduction of configurable replica sizes, we're making Extra Small the default replica size, and updating our pricing model for streaming ClickPipes: the price now depends on both the replica size and the number of replicas you choose; starting at $0.0125. For full pricing details, refer to our [ClickPipes pricing documentation](https://clickhouse.com/docs/cloud/manage/billing/overview#clickpipes-pricing).

| Replica Size  | Compute Units | RAM      | vCPU | Price/hour (per replica) |
|---------------|----------------|---------|------|-------------------------|
| Extra Small   | 0.0625         | 512 MiB | 0.125| $0.0125                 |
| Small         | 0.125          | 1 GiB   | 0.25 | $0.025                  |
| Medium        | 0.25           | 2 GiB   | 0.5  | $0.05                   |
| Large         | 0.5            | 4 GiB   | 1.0  | $0.10                   |
| Extra Large   | 1.0            | 8 GiB   | 2.0  | $0.20                   |

> **Note**: In addition to compute charges, ClickPipes incurs a data ingestion cost of $0.04 per GB. For full pricing details, refer to our [ClickPipes pricing documentation](https://clickhouse.com/docs/cloud/manage/billing/overview#clickpipes-pricing).


## Next Steps

With flexible scaling and enhanced resource monitoring, you now have full control over the cost-performance ratio of your streaming ClickPipes, and can better prepare for changes in your data ingestion workloads. Head over to the [documentation](https://clickhouse.com/docs/integrations/clickpipes) to learn more about how to manage the deployment lifecycle of streaming ClickPipes.



