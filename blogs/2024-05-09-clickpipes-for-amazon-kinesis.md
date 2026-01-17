---
title: "ClickPipes for Amazon Kinesis"
date: "2024-05-09T08:46:31.310Z"
author: "Ryadh Dahimene"
category: "Product"
excerpt: "We’re excited to announce the beta release of our Amazon Kinesis connector for ClickPipes."
---

# ClickPipes for Amazon Kinesis

Welcome to [launch week](https://clickhouse.com/launch-week/may-2024)! We're going to be announcing a new feature of ClickHouse Cloud every day this week. So let's get to it. 

First up, we’re excited to announce the beta release of our Amazon Kinesis connector for ClickPipes.
As one of our most requested integrations, it offers a hassle-free way to ingest data from Kinesis Data Streams into a ClickHouse Cloud service.

![select-data-source.png](https://clickhouse.com/uploads/select_data_source_fa04ed344a.png)

We've also made a short video showing how this all works, which you can view below.

<iframe width="768" height="432" src="https://www.youtube.com/embed/IVmf5dO8EAI?si=8P0Kdig53VU-VYZ-" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

## The “Need for Stream”

The Amazon Web Services (AWS) cloud ecosystem offers powerful building blocks for setting up sophisticated data architectures and pipelines. Data can take various forms and come from different mediums, from object storage to databases and streaming systems. At ClickHouse, ClickPipes represents our commitment to meeting our users where they are. By offering managed data ingestion capabilities, we free up users to focus on their analytics use cases instead of building and maintaining complex data pipelines. 

For example, we recently announced the batch data loading connector for Amazon S3, which allows users to reliably load large data batches and historical uploads. Today, with the Amazon Kinesis connector for ClickPipes, AWS users can complete the picture with near real-time data streaming capabilities, unlocking event-based use cases and pipelines while keeping their architectural footprint minimal.

![kinesis.gif](https://clickhouse.com/uploads/kinesis_dd7e924579.gif)

## Lambda, Kappa architectures? Fewer Greek letters, more insights

The Lambda Architecture combines batch and stream processing for historical and real-time data, while Kappa Architecture simplifies this by relying only on stream processing, eliminating batch processing layers ([source](https://www.kai-waehner.de/blog/2021/09/23/real-time-kappa-architecture-mainstream-replacing-batch-lambda/)).  Whether handling streaming or batch data, this architecture is greatly simplified in ClickHouse Cloud, with ClickPipes providing seamless ingestion into an efficient storage engine with rich query execution capabilities. Treat your static buckets or real-time streams as data sources that will automatically be kept in sync by ClickPipes, allowing you to focus on deriving insights from the data. This represents an additional step towards enabling the [real-time data warehouse](https://clickhouse.com/blog/the-unbundling-of-the-cloud-data-warehouse) use case, unifying data at the warehouse level.

![rtdwh.png](https://clickhouse.com/uploads/rtdwh_39cce2d0ca.png)

## Under the hood: A focus on reliability

ClickPipes for Kinesis leverages our existing streaming ingestion infrastructure for Apache Kafka to ingest Kinesis Data Streams. Our Kinesis consumer implementation differs from Kafka in two main ways: Checkpointing is done on the consumer side for Kinesis. To support this we write reading checkpoints (called SequenceNumbers) to the customer’s ClickHouse DB instances leveraging the ClickHouse key-value store [KeeperMap](https://clickhouse.com/docs/en/engines/table-engines/special/keeper-map). Additionally, to read Kinesis streams, ClickPipes reads concurrently through multiple shards provided by the Kinesis stream. Shards have fixed throughput and hard limits, so Kinesis scales itself by adding and removing shards. We consistently check the number of shards and read each shard as it scales.

![clickpipes-kinesis-arch.png](https://clickhouse.com/uploads/clickpipes_kinesis_arch_d9a3dd424e.png)

## An ever-growing ecosystem of managed connectors

It has been a busy quarter for the ClickPipes team. After adding Avro support for our set of Kafka connectors, the release of the batch data loading connector for Amazon S3 and Google Cloud Storage (GCS), and now the Amazon Kinesis support, the ClickPipes ecosystem continues its expansion both in-depth and breadth. Coming next in our roadmap:

* PostgreSQL Change Data Capture (CDC) connector for ClickPipes
* Continuous mode for the batch data loading connector for Amazon S3 and Google Cloud Storage (allows monitoring a remote bucket and ingesting newly added files)
* Offset control for the ClickPipes Kafka Connector
* ClickPipes duplication (allowing the creation of new ClickPipes from an existing configuration)
* ClickPipes public API
* Improved observability and notification 

This is far from a representative list of what the next quarters will bring. As always, we encourage you to share your use cases and requirements to help shape our roadmap. Please feel free to reach out to us!
