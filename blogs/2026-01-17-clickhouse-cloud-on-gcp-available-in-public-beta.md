---
title: "ClickHouse Cloud on GCP Available in Public Beta"
date: "2023-05-11T14:01:47.953Z"
author: "Krithika Balagurunathan"
category: "Product"
excerpt: "ClickHouse Cloud is now available on Google Cloud Platform (GCP) in public Beta. "
---

# ClickHouse Cloud on GCP Available in Public Beta

## ClickHouse Cloud is now available on Google Cloud Platform (GCP) in public Beta. 

ClickHouse Cloud was launched on December 6, 2022, enabling ClickHouse users to build real-time applications without the devops overhead of a self-managed installation.

TL;DR - Get started [now](https://clickhouse.cloud/signUp?loc=gcp-beta-blog) by launching a GCP service in minutes.

One of the key benefits of ClickHouse Cloud is the simplicity of getting started. With just a few clicks, you can set up a service, and autoscale automatically based on your workload's needs, so you never have to overprovision or pay for unused capacity. We have already seen a number of ClickHouse users using ClickHouse as a [‘speed layer’](https://clickhouse.com/blog/clickhouse-bigquery-migrating-data-for-realtime-queries?loc=gcp-beta-blog) atop BigQuery. This announcement allows these users to keep their data resident in a single cloud provider.

## Depending on your needs, you can select from two different options:

* Development: Best suited for small workloads
    * Storage: Up to 1 TB
    * Memory: 16 GiB
* Production: Designed for production environments and workloads that need additional storage and memory
    * Storage: Unlimited
    * Memory: 24 GiB+ total memory

## Feature Highlights

ClickHouse Cloud on GCP offers the following features:

* **Google Cloud Storage integration**: Out-of-the-box integration to move from cloud storage to ClickHouse Cloud. And several other integrations for you to build end-to-end solutions, see more information [here](https://clickhouse.com/docs/en/integrations?loc=gcp-beta-blog).
* **End-to-end encryption**: At ClickHouse, security is a top priority, and the service offers encryption on the wire with TLS and data-at-rest encryption with Google Cloud Storage encryption.
* **Endpoint security**: The IP Access List feature offers the ability to secure endpoints so only select IPs can access data.
* **Built in SQL Console** for data exploration and visualization: 
    * Seamlessly and securely connect to your database
    * Explore and query your data instantly
    * Build rich visualizations from your query results in 2-3 clicks
    * Collaborate with your team using shared queries

It takes just a few minutes to set up your new service in GCP and get going. See the steps below:

![Getting Started With GCP Beta](https://clickhouse.com/uploads/gcp_console_2fe9217226.gif)

## Stay tuned for the GA announcement. We have a few additional things in the works, including:

* **Disaster Recovery**: Default daily backups for both Development and Production instances.
* **Subscription via the Google Cloud Marketplace**: For users that want to integrate their billing through Google Cloud.
* **Private Service Connect**: Advanced protection of your data on the wire by using Google Cloud’s private network.
* **Service Level Agreements**: For users that sign up for committed spend contracts.
* **Compliance Certification**: SOC 2 Type II and ISO 27001.

## Get Started

To get started, sign up [here](https://clickhouse.cloud/signUp?loc=gcp-beta-blog). ClickHouse Cloud offers users a 30-day trial with $300 in usage credits. The service is available in three major geographies:

* AMER: Iowa - us-central1
* EMEA: Netherlands - europe-west4
* APAC: Singapore - asia-southeast1

If you choose to continue using the service at the end of the trial, you can add a credit card to continue on a pay-as-you-go monthly plan, or reach out to us for volume-based discounts as a part of our Enterprise package.

To learn more, [contact us](https://clickhouse.com/company/contact?loc=gcp-beta-blog) or visit our [pricing page](https://clickhouse.com/pricing?loc=gcp-beta-blog) for more detail. 
