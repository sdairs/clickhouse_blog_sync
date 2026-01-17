---
title: "Azure Blob Storage connector for ClickPipes is now Generally Available"
date: "2025-09-24T12:31:53.871Z"
author: "Marta Paes"
category: "Product"
excerpt: "We’re excited to announce the general availability of the Azure Blob Storage connector for ClickPipes. Natively integrated with ClickHouse Cloud, this connector enables blazing-fast load from Azure Blob Storage with just a few clicks."
---

# Azure Blob Storage connector for ClickPipes is now Generally Available

![azure-blog-banner.png](https://clickhouse.com/uploads/azure_blog_banner_5fda937064.png)

We're excited to announce that the **Azure Blob Storage connector for [ClickPipes](https://clickhouse.com/cloud/clickpipes?utm_source=google.com&utm_medium=paid_search&utm_campaign=21862172336_181837693625&utm_content=764403839926&utm_term=clickpipes_g_c&gad_source=1&gad_campaignid=21862172336&gclid=CjwKCAjwisnGBhAXEiwA0zEOR3kM4ZBQO0_NpfRPpYU2YWG5onZqwF-Kf8m845Ol2IJeyN96r0k8DxoCit4QAvD_BwE)**  is now Generally Available! You can seamlessly load files from Azure Blob Storage into ClickHouse Cloud with even **better performance**, and leverage the new support for **programmatic access** (via OpenAPI and Terraform) to manage your ClickPipes with confidence.

Over the past few months, the connector has gone through an extensive beta phase, with customers moving anywhere between a few GiB to **as much as 60+ PiB of data** into ClickHouse Cloud — validating its reliability and scalability for both small- and enterprise-scale data lake analytics workloads.

> [Sign up for ClickHouse Cloud](https://console.clickhouse.cloud/signup) today to try out the [Azure Blob Storage connector for ClickPipes](https://clickhouse.com/cloud/clickpipes)!

![azure-blog.gif](https://clickhouse.com/uploads/azure_blog_d52244e13f.gif)

## What's new?

Based on customer feedback, and to align the connector with the product experience for other object storage ClickPipes, the Azure Blob Storage connector has been upgraded with:

### Custom HTTP client for better performance

From the rollout of ClickHouse v25.8 to ClickHouse Cloud, the connector will leverage a new, custom HTTP client that delivers more consistent and better performance than the original Azure SDK native client. This brings the connector to parity with object storage ClickPipes for other cloud providers, when it comes to performance.

### Terraform and OpenAPI support

For mature ClickPipes deployments using workflow automation and Infrastructure as Code (IaC), a new `azureblobstorage`  source type is available in [the ClickPipes OpenAPI specification](https://clickhouse.com/docs/cloud/manage/api/swagger#tag/ClickPipes), as well as the ClickHouse Terraform Provider ([3.6.0-alpha1](https://github.com/ClickHouse/terraform-provider-clickhouse/releases/tag/v3.6.0-alpha1)+). Here's an example of how you'd configure an Azure Blob Storage ClickPipe resource in Terraform:

> **Note**: ClickPipes resources are only supported in [alpha releases](https://registry.terraform.io/providers/ClickHouse/clickhouse/3.7.0-alpha1/docs/resources/clickpipe) of the ClickHouse Terraform provider. Regardless, support for object storage ClickPipes is considered **stable**.

```
resource "clickhouse_clickpipe" "azure_blob" {
  name        = "Azure Blob Storage ClickPipe"
  service_id = var.service_id

  source = {
    object_storage = {
      type    = "azureblobstorage"
      format  = "JSONEachRow"

      path                  = var.azure_path              
      azure_container_name  = var.azure_container_name
      connection_string     = var.azure_connection_string

      authentication = "CONNECTION_STRING"
    }
  }

  destination = {
    table         = "my_azure_data_table"
    managed_table = true

    table_definition = {
      engine = {
        type = "MergeTree"
      }
    }

    columns = [
      {
        name = "id"
        type = "UInt64"
      }, {
        name = "name"
        type = "String"
      }, {
        name = "timestamp"
        type = "DateTime"
      }
    ]
  }

  field_mappings = [
    {
      source_field      = "user_id"
      destination_field = "id"
    }, {
      source_field      = "user_name"
      destination_field = "name"
    }, {
      source_field      = "created_at"
      destination_field = "timestamp"
    }
  ]
}
```

In addition to these improvements, it's worth recapping the base capabilities of the Azure Blob Storage connector:

### Built for reliability

Built on top of the [azureBlobStorage](https://clickhouse.com/docs/sql-reference/table-functions/azureBlobStorage) table function, with additional layers of reliability to handle real-world scale. The connector gracefully handles **automatic retries** on failures and guarantees **exactly-once delivery semantics**, so you don't have to worry about data consistency or partial loads.

### Secure by design

Supports ingestion from **private buckets** using connection strings with account credentials or storage account URLs. You can also use **Shared Access Signatures (SAS)** within the connection string for secure, time-limited access.

### Optimized for performance

The connector dynamically adjusts **ingestion parallelism** and **ClickHouse tuning** based on your cloud instance size and workload. It's built to move terabytes of data quickly and efficiently with no need for manual tuning.

### Fully managed experience

The connector is fully integrated into the ClickHouse Cloud experience. It provides **built-in metrics and monitoring, detailed logs** for error diagnosis and debugging, **in-place pipe editing** (e.g., adding columns), and more.

## Pricing

Object storage ClickPipes have a predictable pricing model based on data volume, with minimal added compute cost. The Azure Blob Storage connector for ClickPipes is **10-25x more cost-effective** than using third-party ETL tools, reflecting our commitment to offering ClickPipes as a seamless but affordable option to connect ClickHouse Cloud and your various data sources. For more details, see the [ClickPipes billing documentation](https://clickhouse.com/docs/cloud/reference/billing/clickpipes/streaming-and-object-storage).

## Getting started with the Azure Blob Storage connector

The Azure Blob Storage connector is available to new and existing ClickHouse Cloud customers, in all service tiers. To get started, navigate to the Data Sources tab in the ClickHouse Cloud console, configure the connection details for your storage container, and you're good to go! For step-by-step instructions, frequently asked questions, and gotchas, check out the [documentation for object storage ClickPipes](https://clickhouse.com/docs/integrations/clickpipes/object-storage).

> Ready to eliminate your ETL complexity and reduce your data movement costs? [Try the Azure Blob Storage connector today](https://clickhouse.com/cloud) and experience a fully managed, native integration experience with ClickHouse Cloud — the world's fastest analytics database.

