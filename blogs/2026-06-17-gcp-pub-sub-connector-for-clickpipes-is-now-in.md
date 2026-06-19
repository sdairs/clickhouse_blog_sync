---
title: "GCP Pub/Sub connector for ClickPipes is now in Private Preview"
date: "2026-06-17T20:53:04.615Z"
author: "Marta Paes"
category: "Engineering"
excerpt: "Stream data from Pub/Sub in a few clicks for blazing-fast analytics over GCP infrastructure logs, application events, and operational signals. No routing through GCS or Dataflow required."
---

# GCP Pub/Sub connector for ClickPipes is now in Private Preview

## Summary

Stream data from Pub/Sub in a few clicks for blazing-fast analytics over GCP infrastructure logs, application events, and operational signals. No routing through GCS or Dataflow required.

Pub/Sub is the primary messaging layer for a wide range of GCP services: Cloud Logging, Cloud Monitoring, GKE workloads, and custom event producers across the GCP stack. As more teams route their GCP infrastructure logs, application events, and operational signals to ClickHouse Cloud, we wanted to lower the barrier to get this data in.

Today, we're announcing a new **GCP Pub/Sub connector for [ClickPipes](https://clickhouse.com/cloud/clickpipes)**, now available in Private Preview! You can seamlessly stream data from GCP Pub/Sub into ClickHouse Cloud in **real time** with a few clicks and **no additional infrastructure**. The connector supports all **common formats** (JSON, Avro, Protobuf) and **schema registry integration**, with attribute-based message filtering, flexible seek options, and per-key ordered delivery. Like all ClickPipes connectors, it can also be managed programmatically via OpenAPI and the ClickHouse Terraform provider.


---

## GCP Pub/Sub connector for ClickPipes

Join the waitlist today to try out the GCP Pub/Sub connector for ClickPipes!


[Join the waitlist](https://clickhouse.com/cloud/clickpipes?loc=blog-cta-925-gcp-pub-sub-connector-for-clickpipes-join-the-waitlist&utm_blogctaid=925#pubsub-private-preview)

---

<video autoplay="1" muted="1" loop="1" controls="0">
  <source src="https://clickhouse.com/uploads/pubsub_compressed_23960bbecb.mp4" type="video/mp4" />
</video>

## Why build a ClickPipe?

**Simpler than building your own pipeline.** Previously, getting data from Pub/Sub into ClickHouse meant routing through GCS or standing up a Dataflow pipeline. The Pub/Sub ClickPipe handles all of this automatically: point it at your topic, configure your target table, and the connector manages subscription lifecycle, schema inference, and message delivery for you.

**Built for continuous ingestion.** ClickPipes consumes messages in real-time, optimizing ingestion performance out-of-the-box and eliminating trade-offs between freshness and cost. The connector scales horizontally and vertically for high-throughput topics, is optimized for ClickHouse Cloud's architecture, and handles failures gracefully with configurable replicas and automatic retries.

**Fully managed and native to ClickHouse Cloud.** Built-in metrics, monitoring, and detailed logs give you visibility into your pipeline without standing up external tooling. You can edit ClickPipes in place (*e.g.* add columns, adjust ingestion settings) without recreating them from scratch.

## Main features

### Integration with schema registry

All common serialization formats are supported: **JSON**, **Avro**, and **Protobuf**; including native integration with the **Pub/Sub Schema Registry**. Schemas and field types are inferred and mapped automatically to a target table with ClickHouse native data types. Compressed payloads are **detected and decompressed automatically**, with no additional configuration needed.

### Configurable start offsets

The starting offset supports Pub/Sub's native [seek feature](https://docs.cloud.google.com/pubsub/docs/replay-overview), giving you precise **control over where ingestion begins**: latest, earliest, or a specific timestamp for backfills and point-in-time replay for failure scenarios.

### Message filtering

During ClickPipe creation, you can configure a Pub/Sub [subscription filter](https://docs.cloud.google.com/pubsub/docs/subscription-message-filter) on message attributes to drop messages before they are pulled from the subscription, reducing ingestion volume and associated costs.

### Terraform & Open API support

For mature ClickPipes deployments using workflow automation and Infrastructure as Code (IaC), a new `pubsub` source type is available in [the ClickPipes OpenAPI specification](https://clickhouse.com/docs/cloud/manage/api/swagger#tag/ClickPipes), as well as the ClickHouse Terraform Provider ([3.16.0+](https://github.com/ClickHouse/terraform-provider-clickhouse/releases/tag/v3.16.0)). Here's an example of how you'd configure a GCP Pub/Sub ClickPipe resource in Terraform:

```
resource "clickhouse_clickpipe" "pubsub" {
  service_id = var.service_id
  name       = var.pipe_name

  source = {
    pubsub = {
      format         = "JSONEachRow"
      project_id     = var.gcp_project_id
      topic          = var.pubsub_topic
      authentication = "SERVICE_ACCOUNT"
      seek_type      = "latest"

      service_account_key = {
        service_account_file = var.gcp_service_account_b64
      }
    }
  }

  destination = {
    table         = var.table
    managed_table = true

    table_definition = {
      engine = {
        type = "MergeTree"
      }
    }

    columns = [
      {
        name = "my_field1"
        type = "String"
      },
      {
        name = "my_field2"
        type = "UInt64"
      },
    ]
  }

  field_mappings = [
    {
      source_field      = "my_field"
      destination_field = "my_field1"
    }
  ]
}

output "clickpipe_id" {
  value = clickhouse_clickpipe.pubsub.id
}
```

## How to sign up for Private Preview?

The GCP Pub/Sub connector is available upon request, and **free** to use during Private Preview. Fill out [this form](https://clickhouse.com/cloud/clickpipes#pubsub-private-preview) to join the waitlist, or reach out to your ClickHouse Cloud account manager. To get started with step-by-step instructions, check out the [documentation for GCP Pub/Sub ClickPipes](https://clickhouse.com/docs/integrations/clickpipes/pubsub).


---

## Ready to test ClickHouse with your Pub/Sub data?

Ready to test ClickHouse with your Pub/Sub data?

In our benchmarks, ClickHouse delivers up to 4x faster query performance and significant cost savings for interactive analytics. Join the waitlist today to try it out for yourself with the new GCP Pub/Sub connector for ClickPipes.


[Join the waitlist](https://clickhouse.com/cloud/clickpipes?loc=blog-cta-926-ready-to-test-clickhouse-with-your-pub-sub-data-join-the-waitlist&utm_blogctaid=926#pubsub-private-preview)

---