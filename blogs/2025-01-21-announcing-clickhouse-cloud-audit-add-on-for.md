---
title: "Announcing ClickHouse Cloud Audit add-on for Splunk"
date: "2025-01-21T16:30:27.233Z"
author: "ClickHouse Team"
category: "Product"
excerpt: "Discover the new Splunk add-on that simplifies ingesting ClickHouse Cloud audit logs. Now available for download on Splunkbase."
---

# Announcing ClickHouse Cloud Audit add-on for Splunk

In an ongoing effort to grow the ClickHouse ecosystem so that it can easily integrate into any environment, we are excited to announce the recent release of the **ClickHouse Cloud Audit add-on for Splunk**! 

This new integration lets you easily store and analyze ClickHouse Cloud audit logs directly into [Splunk](https://www.splunk.com/), the data analytics and monitoring platform. 

It uses the [ClickHouse Cloud API](https://clickhouse.com/docs/en/cloud/manage/api/api-overview) to securely pull the audit logs from your ClickHouse Cloud organization.  The add-on is available for download on [Splunkbase](https://splunkbase.splunk.com/app/7709).

<img src="/uploads/splunk_clickhouse_add_on_1_f053ea4218.png" alt="client-only.png" class="h-auto w-auto max-w-full" style="height: 200px;">

## Installation and Configuration

Installing the add-on on your Splunk deployment is straightforward and requires only a few steps. Currently, only Splunk Enterprise deployment is supported. Approval for the Splunk Cloud availability is pending.

1.  Download and Install:

-  Download the ClickHouse Cloud Audit Add-on for Splunk from [Splunkbase](https://splunkbase.splunk.com/app/7709).
-  In Splunk Enterprise, navigate to Apps > Manage, click Install app from file, and upload the downloaded file.

2.  Gather ClickHouse Cloud Information:

-  Log in to your ClickHouse Cloud console.
-  Navigate to Organization > Organization Details to copy your Organization ID.
-  Generate an API Key with admin privileges under API Keys and save it securely.

3.  Configure Data Input in Splunk:

-  Go to Settings > Data Inputs in Splunk.
-  Select ClickHouse Cloud Audit Logs and click New.
-  Enter your Organization ID and Admin API Key to complete the setup.

Find a detailed version of the instructions on the [ClickHouse documentation website](https://clickhouse.com/docs/en/integrations/audit-splunk).

## Audit ClickHouse Cloud from Splunk

Once configured, the Cloud organization audit logs start flowing into Splunk and are ready for exploration through Splunk search and analytics tools. 

<img src="/uploads/splunk_clickhouse_add_on_2_2f18f68739.png" alt="client-only.png" class="h-auto w-auto max-w-full" style="height: 200px;">
<br />

If you need to centralize audit logs in your Splunk deployment, start using the ClickHouse Cloud Audit Logs for Splunk add-on today.