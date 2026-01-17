---
title: "ClickPipes for Kafka - ClickHouse Cloud Managed Ingestion Service"
date: "2023-07-14T09:27:08.246Z"
author: "Ryadh Dahimene"
category: "Product"
excerpt: "We are pleased to announce the availability of ClickPipes in private preview, allowing ClickHouse Cloud users to insert data from Kafka using a fully managed ingestion service."
---

# ClickPipes for Kafka - ClickHouse Cloud Managed Ingestion Service

Today at ClickHouse, we are delighted to announce the release of ClickPipes for Kafka. 
This new ClickHouse Cloud experience enables users to simply connect to remote Kafka brokers and start ingesting data into their ClickHouse services right away. This new feature unlocks the full potential of ClickHouse Cloud and enables users to leverage near real-time data for insights and analytics. 

ClickPipes is a native capability of ClickHouse Cloud currently under private preview. You can [join our waitlist here](https://clickhouse.com/cloud/clickpipes#joinwaitlist).

<iframe width="768" height="432" src="https://www.youtube.com/embed/rSUHqyqdRuk" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>

## “Real-time Analytics ❤️ Real-time Data” 

Apache Kafka is a ubiquitous event streaming platform that thousands of companies use for high-performance data pipelines, streaming analytics, data integration, and mission-critical applications, often in conjunction with ClickHouse. For these reasons, it was obvious for us that we should start by providing world-class Kafka Support in ClickPipes.

![choose_datasource.png](https://clickhouse.com/uploads/choose_datasource_70485c8655.png)

For this task, we worked closely with our friends at Confluent, through the Connect with Confluent program (CwC). As the leading enterprise Kafka provider, Confluent offers a fully-managed cloud environment where users can deploy and operate Kafka clusters, Kafka Connect connectors and more. 

We announced earlier this year the availability of our official [clickhouse-kafka-connect](https://clickhouse.com/blog/kafka-connect-connector-clickhouse-with-exactly-once) sink and we demonstrated using it in Confluent Cloud via the [custom connectors feature](https://clickhouse.com/blog/real-time-event-streaming-with-kafka-connect-confluent-cloud-clickhouse). With ClickPipes, we effectively take this integration path one step further, and provide a native “zero setup” experience to integrate ClickHouse and Confluent Cloud.

## Why another ingestion solution?

Valuable insights extracted from real-time analytics applications often depend on the availability of fresh and good quality input data. It’s not uncommon for users to spend a considerable amount of time and effort building and maintaining a sophisticated ingestion layer for their application. This critical component can quickly grow in complexity and will condition the value of the whole data chain. 

With Clickhouse, users can rely on a [vibrant ecosystem of integrations](https://clickhouse.com/docs/en/integrations) for this task. But spending time moving data from point A to point B means they are left with less time to focus on the use-case itself and extracting value from data. 

With ClickPipes, we abstract this complexity away by providing a turnkey data ingestion experience. Setting-up a continuous ingestion job with ClickPipes takes less than a minute.

![clickpipes_1mn.gif](https://clickhouse.com/uploads/clickpipes_1mn_88c2bc30a1.gif)

The main advantages of ClickPipes are:

* **An easy and intuitive data onboarding:** Setting up a new ingestion pipeline takes just a few steps. Select an incoming data source and format, tune your schema, and let your pipeline run.
* **Built for continuous ingestion:** ClickPipes manages your continuous ingestion pipelines so that you don’t have to. Set up your pipeline and let us handle the rest.
* **Designed for speed and scale**: ClickPipes provides the scalability you need to handle increasing data volumes, ensuring your systems can handle future demands effortlessly.
* **Unlock your real time analytics**: Built leveraging our deep expertise in real time data management systems, ClickPipes handles the complexities of real time ingestion for optimal performance.

## Besides Confluent Cloud and Apache Kafka, what’s coming next?

ClickPipes [supports](https://clickhouse.com/docs/en/integrations/clickpipes#supported-data-sources) Confluent Cloud and Apache Kafka (at the time of this release). We will be quickly expanding the list of supported data sources and systems to turn ClickPipes into a fully fledged connectivity platform for ClickHouse Cloud. 

After Kafka, we decided to focus our efforts on supporting other types of streaming technologies like Cloud native sources of events (Amazon Kinesis, Google Pub/Sub, Azure Event Hub). We are also curious to hear from the community about what they want to see next, so please don’t hesitate to use our [contact form](https://clickhouse.com/company/contact) to let us know! We will be happy to explore anything from monitored object stores to Change-Data-Capture scenarios.

## How can I access ClickPipes?

ClickPipes Beta is already available in a private preview model. You can join our waitlist by filling out [this form](https://clickhouse.com/cloud/clickpipes#joinwaitlist) and we will reach out to you once a slot is available for testing. This private preview phase is crucial for us to validate the reliability and production readiness of the platform. 

Following this phase, we will make ClickPipes generally available in ClickHouse Cloud later this year.

You can find more information in the following pages:

* [ClickPipes Website](https://clickhouse.com/cloud/clickpipes)
* [Video demonstration](https://www.youtube.com/watch?v=rSUHqyqdRuk)
* [Documentation](https://clickhouse.com/docs/en/integrations/clickpipes)

