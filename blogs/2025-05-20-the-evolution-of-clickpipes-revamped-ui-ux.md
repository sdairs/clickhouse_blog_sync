---
title: "The Evolution of ClickPipes: Revamped UI/UX, ClickPipes API and Terraform Provider, Prometheus metrics, and more!"
date: "2025-05-20T15:56:30.004Z"
author: "ClickPipes Team"
category: "Product"
excerpt: "ClickPipes evolves with a revamped UI/UX, new API and Terraform Provider, AWS PrivateLink integration, notification system, Prometheus metrics for observability, and centralized system tables for enhanced data pipeline management."
---

# The Evolution of ClickPipes: Revamped UI/UX, ClickPipes API and Terraform Provider, Prometheus metrics, and more!

Since its inception, ClickPipes has simplified the process of setting up robust continuous data pipelines to ClickHouse Cloud, allowing users to connect sources like Apache Kafka, Amazon S3, Google Cloud Storage, Amazon Kinesis, PostgreSQL, and now MySQL with just a few clicks.

This has enabled organizations to focus more on deriving insights from their data rather than managing complex ingestion processes. As of today, ClickPipes has successfully moved more than **20 trillion rows** to ClickHouse Cloud.

![0_clickpipes.png](https://clickhouse.com/uploads/0_clickpipes_8ccd16e87f.png)

Today, we are introducing a new set of features designed to make ClickPipes a first-class tool in every developer's toolkit. These capabilities are built to support scale, automation, security, and observability in modern data architectures. 

But first, let’s start with usability improvements:

## Revamped UI

The ClickPipes user interface has been redesigned for greater clarity and efficiency. From configuring sources to monitoring pipeline health, every task is now more intuitive and discoverable, with polished UI animations and transitions.

![1_clickpipes.gif](https://clickhouse.com/uploads/1_clickpipes_3969a2a564.gif)

## ClickPipes Editing

With support for editing, users can now modify running ClickPipes pipelines without deleting and recreating them. This includes updating ClickPipes names, schema mappings, and connection settings, allowing teams to iterate quickly while maintaining continuity of service.

![2_clickpipes.gif](https://clickhouse.com/uploads/2_clickpipes_9f72aebfd0.gif)


## ClickPipes API and Terraform Provider

ClickPipes now includes dedicated API endpoints, part of the [ClickHouse Cloud OpenAPI](https://clickhouse.com/docs/cloud/manage/api/api-overview), and a Terraform provider. 
These tools support automated management of pipeline configurations and simplify integration into CI/CD pipelines.


<pre><code type='click-ui' language='json'>
{
  "name": "???? I was created using API!",
  "source": {
    "kafka": {
      "type": "confluent",
      "format": "JSONEachRow",
      "authentication": "PLAIN",
      "credentials": {
        "username": "xxx",
        "password": "xxx"
      },
      "brokers": "{{kafka_broker_url_and_port}}",
      "topics": "cell_towers"
    }
  },
  "destination": {
    "database": "default",
    "table": "my_table",
    "managedTable": true,
    "tableDefinition": {
      "engine": {
        "type": "MergeTree"
      }
    },
    "columns": [
      {
        "name": "area",
        "type": "Int64"
      },
      {
        "name": "averageSignal",
        "type": "Int64"
      }
    ]
  }
}
</code></pre>

With infrastructure as code, teams can consistently deploy and manage ingestion workflows across environments and version pipelines, improving collaboration and automation. 
The ClickPipes Terraform provider is available in our official Terraform [registry entry](https://registry.terraform.io/providers/ClickHouse/clickhouse/3.2.0-alpha1/docs/resources/clickpipe) (part of the 3.2.0-alpha1 version at the time of writing).

<pre><code type='click-ui'>
resource "clickhouse_clickpipe" "kafka_clickpipe" {
  name           = "My Kafka ClickPipe"
  description    = "Data pipeline from Kafka to ClickHouse"

  service_id     = "e9465b4b-f7e5-4937-8e21-8d508b02843d"

  scaling {
    replicas = 1
  }

  state = "Running"

  source {
    kafka {
      type = "confluent"
      format = "JSONEachRow"
      brokers = "my-kafka-broker:9092"
      topics = "my_topic"

      consumer_group = "clickpipe-test"

      credentials {
        username = "user"
        password = "***"
      }
    }
  }

  destination {
    table    = "my_table"
    managed_table = true

    tableDefinition {
      engine {
        type = "MergeTree"
      }
    }

    columns {
      name = "my_field1"
      type = "String"
    }

    columns {
      name = "my_field2"
      type = "UInt64"
    }
  }

  field_mappings = [
    {
      source_field = "my_field"
      destination_field = "my_field1"
    }
  ]
}
</code></pre>

**NOTE:** The Terraform Provider is currently not available for Postgres and MySQL CDC ClickPipes. 
However, you can manage these ClickPipes via [OpenAPI](https://clickhouse.com/docs/integrations/clickpipes/postgres/faq#can-clickpipe-creation-be-automated-or-done-via-api-or-cli), which is available in Beta. 
Terraform support for CDC ClickPipes is planned for later in 2025.

## AWS PrivateLink Self-Service

We introduced support for AWS PrivateLink within ClickPipes, enabling customers to securely ingest data into ClickHouse Cloud using private network paths. 
With this set of features, users can create private endpoints that facilitate direct communication between their AWS Virtual Private Clouds (VPCs) and ClickHouse Cloud. 
Additionally, ClickPipes now supports reverse private endpoints, which allow ClickHouse Cloud to securely initiate connections to private customer resources.

![3_clickpipes.png](https://clickhouse.com/uploads/3_clickpipes_810c9f5005.png)

![4_clickpipes.png](https://clickhouse.com/uploads/4_clickpipes_7d6644e2b3.png)


The integration supports popular AWS services, including Amazon RDS, Amazon MSK, and other VPC-based resources. Configuration is designed to be straightforward, with documentation available to guide users through the setup process. To learn more and get started, refer to the full guide on [AWS PrivateLink for ClickPipes.](https://clickhouse.com/docs/integrations/clickpipes/aws-privatelink)

## Notifications

A built-in notification system provides real-time alerts about pipeline activity. 
Users can stay updated on ingestion health, failure events, and operational changes.

![5_clickpipes.png](https://clickhouse.com/uploads/5_clickpipes_d4bd32b519.png)

This feature reduces operational blind spots and enables proactive issue resolution. We support receiving notifications through email, ClickHouse Cloud UI, and Slack. More details can be found on the notifications [documentation page](https://clickhouse.com/docs/cloud/notifications).

![6_clickpipes.png](https://clickhouse.com/uploads/6_clickpipes_d207817c7b.png)

## Prometheus Exporter for Observability

ClickPipes now produces Prometheus metrics, part of the [ClickHouse Cloud Prometheus integration](https://clickhouse.com/docs/integrations/prometheus), making ingestion metrics available for dashboards in Grafana, Datadog, and other observability tools.

![7_clickpipes.png](https://clickhouse.com/uploads/7_clickpipes_7acf55e924.png)


Metrics include ingestion volume (bytes or number of rows) and error counts, giving engineering teams the insight needed to maintain performance. The documentation includes integration guides for [Grafana](https://clickhouse.com/docs/integrations/prometheus#integrating-with-grafana) and [Datadog](https://clickhouse.com/docs/integrations/prometheus#integrating-with-datadog).

## System Tables Centralization

Finally, a centralized system table aggregates ClickPipes-related logs, making it possible to monitor Kafka/Kinesis/S3 pipelines from a single SQL interface, the same way users monitor all the ClickHouse services activity, like merges and queries. 

![8_clickpipes.png](https://clickhouse.com/uploads/8_clickpipes_7ef2bbaec6.png)

This design enables users to query pipeline status and health using familiar SQL syntax, build dashboards, and create custom alerts using third-party tooling. The feature is currently in private preview and will soon be generalized to Kafka/Kinesis/S3 ClickPipes users.

## Why This Matters?

These new capabilities help complete the feature landscape of ClickPipes, taking numerous steps towards a complete ingestion platform for ClickHouse Cloud. Together, they provide:

* A streamlined experience with the revamped UI  
* Flexibility with editable pipelines  
* Automation through the ClickPipes API and Terraform  
* Secure, private connectivity via AWS PrivateLink  
* Visibility and alerts through notifications  
* Observability with Prometheus and the upcoming centralized system tables

We look forward to hearing your feedback and continuing to evolve ClickPipes to meet your needs. 
This release is a major step toward a more automated, observable, and developer-friendly ingestion experience.
