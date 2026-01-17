---
title: "ClickHouse Cloud is now on Azure in Public Beta!"
date: "2024-05-20T11:03:46.699Z"
author: "Krithika Balagurunathan"
category: "Product"
excerpt: "It feels like it was just yesterday when ClickHouse Cloud first launched in December 2022. Since then, we’ve been on a whirlwind journey, expanding to Google Cloud in June 2023. And today, we’re thrilled to announce ClickHouse Cloud availability on Micros"
---

# ClickHouse Cloud is now on Azure in Public Beta!

It feels like it was just yesterday when ClickHouse Cloud first launched in December 2022. Since then, we’ve been on a whirlwind journey, expanding to Google Cloud in June 2023. And today, we’re thrilled to announce ClickHouse Cloud availability on Microsoft Azure!

This expansion reinforces our commitment to making ClickHouse the most accessible and flexible cloud analytics platform. With ClickHouse Cloud on Azure, we’re extending our reach to offer even greater flexibility and choice for running data analytics at scale on the cloud platform that best suits your needs. 

## Get Started in Minutes

To get started, [sign up](https://clickhouse.cloud/signUp?loc=blog-azure-beta) for a free trial that comes with $300 of credits. The service is offered in three regions:

* United States: West US 3 (Arizona)
* United States: East US 2 (Virginia)
* Europe: Germany West Central (Frankfurt)

## Deployment Options that Fit Your Needs

The service on Azure gives you two deployment options:

**Production**: Designed for workloads that need flexibility with scale, autoscaling, and the option to idle when not in use. This deployment option comes with unlimited storage and memory: 24GiB+ with the ability to scale vertically (up to 1 TiB) and horizontally (scale out by adding nodes).

**Dedicated**: Ideal for workloads that require advanced isolation, predictable performance, and ultimate flexibility with configurations. 

Please visit our [pricing page](https://clickhouse.com/pricing?loc=blog-azure-beta) for more information about the different options and to estimate costs.

![signup.gif](https://clickhouse.com/uploads/signup_bb5396f8e2.gif)

## Feature Highlights

Our Public Beta release on Azure offers a robust experience, including:

* **End-to-end Encryption**: All services come with on-the-wire encryption with TLS and at-rest encryption with Azure Blob Storage.
* **Azure Blob Storage Integration**: You can seamlessly move data to ClickHouse Cloud from Azure Blob Storage using the AzureBlobStorage Table Engine; see details [here](https://clickhouse.com/docs/en/engines/table-engines/integrations/azureBlobStorage).
* **Strict Endpoint Security**: All services come with configurable endpoint security controls with IP Access Lists to restrict access on the public internet, as well as[ Azure Private Link](https://azure.microsoft.com/en-us/products/private-link) support for those who want to enforce advanced protection by routing traffic on private networks.
* **Single Sign On (SSO)**: Integration with [Azure Entra ID](https://www.microsoft.com/en-us/security/business/identity-access/microsoft-entra-id) (formally Azure Active Directory) for single sign-on (Private Preview).
* **Compliance**: Our compliance program includes coverage with Azure and will be included in our SOC 2 and ISO 27001 reports, expected mid-September.
* **Setup and Lifecycle Automation**: Our [Terraform provider](https://registry.terraform.io/providers/ClickHouse/clickhouse/latest) helps you easily automate the setup and management of service lifecycle operations.

In addition, we have a [newly redesigned Cloud Console](https://clickhouse.com/blog/new-clickhouse-cloud-experience) that’s built to make using ClickHouse Cloud easier than ever with a unified operations pane, seamless data loading, instant data visualizations, dark mode, and much more.

## Integrations

Integrations are a top priority for us at ClickHouse, and our Azure release is no exception. With ClickHouse Cloud on Azure, you’ll have a seamless experience integrating ClickHouse Cloud into your existing data pipeline by leveraging our extensive catalog of [integrations](https://clickhouse.com/docs/en/integrations). Select highlights include:

* **Data Onboarding and Transformation**: Apache Kafka, dbt, [Azure Blob Storage](https://azure.microsoft.com/en-us/products/storage/blobs), MySQL, PostgreSQL, and [Azure Event Hub](https://learn.microsoft.com/en-us/azure/event-hubs/event-hubs-about) **(powered by ClickPipes)**
* **Data Visualization**: Superset, Metabase, Grafana, Deepnote, Tableau, and [PowerBI Desktop](https://powerbi.microsoft.com/en-us/desktop/)
* **Language Clients**: Python, Golang, Java, and Node.js
* **SQL Clients**: Datagrip and DBeaver

Lastly, for a seamless **managed ingestion pipeline** experience, we offer [ClickPipes](https://clickhouse.com/cloud/clickpipes), built for continuous ingestion into ClickHouse Cloud. 

## Coming Soon: General Availability 

We will be announcing the General Availability of ClickHouse Cloud on Azure in the coming weeks. This will include:

* **Azure Marketplace Subscription**: Subscription to the service through the Azure Marketplace for users who want to integrate their billing with the Azure platform.
* **Service Level Agreements (SLAs)**: Uptime guarantees for users who enter into a committed spend agreement. 

Whether you’re a seasoned data practitioner or just starting to build your very first analytics application, ClickHouse Cloud offers the flexibility, security, and the right set of features you need to unlock instant insights from your data. [Sign up](https://clickhouse.cloud/signUp?loc=blog-azure-beta), and we can’t wait to see what you build!