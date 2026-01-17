---
title: "Real-time Salesforce analytics with ClickHouse and Estuary Flow"
date: "2024-09-24T20:32:24.125Z"
author: "Estuary"
category: "Engineering"
excerpt: "We’re excited to welcome Estuary as they explore how to build a real-time analytics pipeline by integrating ClickHouse with Estuary Flow’s Dekaf, featuring a hands-on example using Salesforce data."
---

# Real-time Salesforce analytics with ClickHouse and Estuary Flow

![estuary_clickhouse.png](https://clickhouse.com/uploads/estuary_clickhouse_700b6a02ff.png)

The ability to [process and analyze data in real-time](https://clickhouse.com/engineering-resources/what-is-real-time-analytics) has become a critical requirement for businesses across various industries. ClickHouse, a high-performance columnar database management system, combined with Estuary Flow, a robust data integration platform makes up a real-time analytics platform that can ingest and transform data from hundreds of sources.

This article explores how integrating these technologies, facilitated by [Estuary Flow](https://estuary.dev/)'s Dekaf, works in detail. We’ll also include a hands-on example that showcases how you can build a real-time analytics pipeline over Salesforce data.

## The Power of ClickHouse

ClickHouse has gained popularity for its exceptional speed in processing analytical queries on large datasets. Its columnar storage format and parallelized query execution make it ideal for real-time analytics workloads. Recently, ClickHouse has enhanced its capabilities with ClickPipes, an integration engine that simplifies data ingestion. This is principally designed for loading large datasets from infrastructure software such as Kafka, object storage, and Postgres. With a focus on high throughput, ClickPipes delegates the integration of more nuanced business sources that have their own APIs to either custom code or data integration platforms such as Estuary.

## Estuary Flow: Bridging the Gap

While ClickHouse and ClickPipes provide the analytical horsepower and support for high throughput ingestion, [Estuary Flow](https://estuary.dev/) addresses a critical challenge in the data pipeline: seamless integration of hundreds of real-time data sources. Estuary Flow supports a wide array of sources, including CDC for databases like MongoDB, MySQL, Oracle, and SaaS platforms such as Netsuite and Salesforce for which ClickPipes is not a focus.

Historically, integrating these diverse data sources into ClickHouse required custom code or more complex configurations and integration with additional services such as Debezium. This complexity often created bottlenecks and increased the infrastructure complexity and potential for errors. However, Estuary Flow's introduction of Dekaf, a Kafka API compatibility layer, has dramatically simplified this process.

## What is Dekaf?

[Dekaf](https://docs.estuary.dev/guides/dekaf_reading_collections_from_kafka/) is Estuary Flow's innovative solution that allows consumers to read data from Estuary Flow collections as if they were Kafka topics. It also provides a schema registry API for managing schemas, enabling seamless integration with existing Kafka-based tools and workflows.

Here’s how it works:

1. **Connect to Your Data Sources with Estuary Flow:** Utilize Estuary’s connectors to capture events in real time from your sources such as Salesforce.
2. **Leverage Dekaf as your Kafka-Compatible Endpoint:** Dekaf acts as a built-in Kafka endpoint, allowing ClickHouse to read data directly from Estuary Flow collections.
3. **Ingest Data Directly into ClickHouse:** ClickHouse connects to Estuary Flow using ClickPipes, ensuring smooth and real-time data ingestion.

This integration enables you to build robust, real-time analytics applications with a streamlined architecture. By combining Estuary Flow and ClickHouse, you can quickly scale your analytics capabilities to meet the demands of modern, data-driven applications.

## Why is this good for ClickHouse users?

The integration of Dekaf with ClickHouse offers several significant advantages:

1. **Simplified Data Ingestion:** With Dekaf, ClickHouse users can now directly ingest data from hundreds of real-time sources supported by Estuary Flow without the need for intermediate systems.
2. **Delivery Guarantees:** Estuary Flow ensures exactly-once delivery semantics, maintaining the integrity of your real-time data streams.
3. **Scalability:** The integration leverages the scalable architecture of both Estuary Flow and ClickHouse, ensuring high throughput and low latency even for demanding workloads.
4. **Reduced Complexity:** By eliminating the need for additional services like Kafka and Debezium, the overall system becomes more streamlined and easier to manage.
5. **Broader Source Support:** ClickHouse users now have access to Estuary Flow's extensive library of connectors, significantly expanding the range of data sources they can work with.

## Implementing Real-time Salesforce Analytics with ClickHouse and Estuary Flow

Let’s take a look at the steps needed to set up this powerful integration.

### Configure the Real-time Salesforce Connector

1. Head over to your Estuary Flow dashboard and search for the Real-time Salesforce capture connector.

![estuary_step_1.png](https://clickhouse.com/uploads/estuary_step_1_ef1861ff89.png)

2. Provide your Salesforce credentials and necessary permissions.

![estuary_step_2.png](https://clickhouse.com/uploads/estuary_step_2_19dc6bc316.png)

3. Choose the Salesforce objects you want to stream (e.g., Accounts, Contacts, Opportunities).

![estuary_step_3.png](https://clickhouse.com/uploads/estuary_step_3_3ccf66c2e4.png)

4. Use Dekaf to expose your Estuary Flow collections as Kafka-compatible topics.

Good news, there’s nothing to configure in this step – Dekaf automatically exposes the collections that are now being hydrated from Salesforce via a Kafka-API compatible API. The connection details are the following:

* Broker Address: <strong><code>dekaf.estuary.dev</code></strong>
* Schema Registry Address: <strong><code>https://dekaf.estuary.dev</code></strong>
* Security Protocol: <strong><code>SASL_SSL</code></strong>
* SASL Mechanism: <strong><code>PLAIN</code></strong>
* SASL Username: <strong><code>{}</code></strong>
* SASL Password: <strong><code>Estuary Refresh Token</code> ([Generate](https://docs.estuary.dev/guides/how_to_generate_refresh_token/) a refresh token in the dashboard)</strong>
* Schema Registry Username: <strong><code>{}</code></strong>
* Schema Registry Password: <strong><code>The same Estuary Refresh Token as above</code></strong>

### Set up ClickPipes in ClickHouse.

To configure ClickHouse to ingest data from these collections using ClickPipes:

5. Select Apache Kafka as a Data Source

![estuary_step_5.png](https://clickhouse.com/uploads/estuary_step_5_fc540360af.png)

6. Configure access to Estuary Flow using the connection details from the previous step.

![estuary_step_6.png](https://clickhouse.com/uploads/estuary_step_6_79c43fd947.png)

7. Make sure the incoming data is parsed properly.

![estaury_step_7.png](https://clickhouse.com/uploads/estaury_step_7_e57ea74846.png)

8. Kick off the integration and wait until the ClickPipe is provisioned, this should only take a few seconds.

![estuary_step_8.png](https://clickhouse.com/uploads/estuary_step_8_091ad7b9a1.png)

9. Start analyzing your real-time data in ClickHouse! Let’s write a quick query to see if we can calculate the value of all closed deals for 2024.

![estuary_step_9.png](https://clickhouse.com/uploads/estuary_step_9_a88c9a77e9.png)

## Conclusion
The integration of ClickHouse and Estuary Flow, enabled by Dekaf, marks a significant leap forward in real-time analytics capabilities. By combining ClickHouse's analytical prowess with Estuary Flow's extensive source support and Dekaf's seamless integration, organizations can now implement robust, scalable, and efficient real-time analytics solutions with unprecedented ease.

As data continues to grow in volume and velocity, this integration provides a powerful toolkit for businesses to stay ahead in the data-driven world, turning real-time insights into actionable strategies.
