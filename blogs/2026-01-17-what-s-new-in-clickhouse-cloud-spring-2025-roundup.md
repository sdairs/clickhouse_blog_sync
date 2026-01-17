---
title: "What's new in ClickHouse Cloud: spring 2025 roundup"
date: "2025-04-24T16:25:07.018Z"
author: "Mihir Gokhale"
category: "Product"
excerpt: "Spring 2025 brings major updates to ClickHouse Cloud - from BYOC and native CDC connectors to Slack alerts, usage APIs, and expanded regional support."
---

# What's new in ClickHouse Cloud: spring 2025 roundup

![whast_new_2025.png](https://clickhouse.com/uploads/whast_new_2025_67023db754.png)

If you live in the northern hemisphere, spring is here! As flowers bloom and animals come out of hibernation, we’ve been bringing the power of ClickHouse to ClickHouse Cloud. Over the past few months, we’ve delivered a wave of new features and improvements — all designed to give you the most powerful backend for your real-time data as you spring into the new season. Here’s a look at what’s new from the [ClickHouse Cloud Changelog](https://clickhouse.com/docs/whats-new/changelog/cloud).

## Bring Your Own Cloud (BYOC) - now Generally Available for AWS

In February, we [introduced a new deployment model](https://clickhouse.com/blog/announcing-general-availability-of-clickhouse-bring-your-own-cloud-on-aws) for ClickHouse by launching Bring Your Own Cloud (BYOC) in GA for AWS. With BYOC, you can deploy ClickHouse Cloud directly into your own AWS account, maintaining full control of your data while we manage the operations. It’s the best of both worlds: the power of ClickHouse with the security and compliance benefits of a single-tenant environment.

![byoc.png](https://clickhouse.com/uploads/byoc_5942e30172.png)

Learn more about the architecture, onboarding process, and operations about our BYOC offering [here](https://clickhouse.com/blog/building-clickhouse-byoc-on-aws). To request access or add yourself to the waitlist for GCP or Azure, please submit your information [here](https://clickhouse.com/cloud/bring-your-own-cloud). 

## Native Postgres Change Data Capture (CDC) - in public beta

After [joining forces with PeerDB](https://clickhouse.com/blog/clickhouse-acquires-peerdb-to-boost-real-time-analytics-with-postgres-cdc-integration), in February we announced the public beta of a native Postgres CDC connector, making it easier than ever to capture and replicate Postgres changes into ClickHouse in near real-time. 

<blockquote>
<p>“ClickPipes for Postgres has made it incredibly easy for us to keep our billing data in Postgres synchronized with ClickHouse for efficient analytics. The CDC experience is blazing fast, ensuring data freshness within seconds while minimizing the load on our production Postgres database. An invaluable solution for seamlessly integrating Postgres with ClickHouse!”</p><p>Mo Abedi, Software Engineer in Billing team, Neon.tech</p>
</blockquote>

Learn more about this feature in our [launch blog](https://clickhouse.com/blog/postgres-cdc-connector-clickpipes-public-beta). During the public beta, if you face issues, have questions, or want to chat with the team working on this feature, please reach out to [db-integrations-support@clickhouse.com](mailto:db-integrations-support@clickhouse.com).

## Native MySQL Change Data Capture (CDC) - in private preview

When we launched the Postgres CDC connector, we got overwhelming requests for a similar MySQL connector - so we developed a ClickHouse native CDC connector purpose built for MySQL which is now in private preview. You can use this connector for both continuous replication and one-time migration from MySQL, no matter where it's running—whether in the cloud (RDS, Aurora, CloudSQL, Azure, etc.) or on-premises.

Some key features of this connector include blazing fast backfills during the initial load, continuous replication from MySQL, schema change replication, and more. 

Learn more in our [launch blog](https://clickhouse.com/blog/mysql-cdc-connector-clickpipes-private-preview), and sign up for the Private Preview [here](https://clickhouse.com/cloud/clickpipes/mysql-cdc-connector).

## Slack notifications for Cloud events

Monitor your ClickHouse Cloud deployment without leaving Slack. ClickHouse Cloud already sends notifications for key events — such as billing, scaling, and ClickPipes. In April, we started allowing users to deliver these notifications directly to your Slack workspace using the ClickHouse Cloud Slack application. 

![alert.png](https://clickhouse.com/uploads/alert_b8b6678f95.png)

To get started, admins can configure these notifications via the notification center by specifying slack channels to which notifications should be sent. Learn more [here](https://clickhouse.com/docs/cloud/notifications). 

## Monitor ClickHouse with the Resource Utilization Dashboard

Also in April, we started rolling out a new dashboard to monitor your ClickHouse Cloud deployment without leaving the ClickHouse Cloud console. The new Resource Utilization dashboard gives replica-level insights into how your cluster is sized, also how much CPU and memory load each replica is experiencing, and how much data is transferred in and out of your service. 

We scrape the metrics on this dashboard from [ClickHouse system tables](https://clickhouse.com/docs/operations/system-tables), and serve them via this dashboard to help you diagnose issues of overprovisioned or underprovisioned clusters. For one of our internal ClickHouse Cloud services, we used this dashboard to cut our ClickHouse Cloud costs by 4x! 

Questions, comments, or feedback? Reach out to [metrics-requests@clickhouse.com](mailto:metrics-requests@clickhouse.com). 

![resource_util.png](https://clickhouse.com/uploads/resource_util_dc54995e2e.png)

## New region: AWS Middle East (UAE) - me-central-1

In February, we’re announced that ClickHouse Cloud is now available in the AWS Middle East (UAE) region (me-central-1). This expansion helps us better serve customers in the Middle East who require local data residency and low-latency access. With this expansion, you can now harness the power of ClickHouse in [11 regions on AWS, 4 regions on GCP, and 3 regions on Azure](https://clickhouse.com/docs/cloud/reference/supported-regions). We also support private regions in select geographies, you can find more information or request access [here](https://clickhouse.com/docs/cloud/reference/supported-regions).

## Cross-Region Private Link - in public beta

In March, we announced the public Beta of Cross-Region Private Link - useful for customers running ClickHouse clusters across multiple AWS regions. This enables secure access between your applications and ClickHouse Cloud, no matter where they live.

Learn more [here](https://clickhouse.com/docs/manage/security/aws-privatelink).

## ClickPipes - AWS PrivateLink

Last week, we released the ability to use AWS PrivateLink and ClickPipes to establish secure connectivity between VPCs, AWS services, your on-premises systems, and ClickHouse Cloud. This can be done without exposing traffic to the public internet while moving data from sources like Postgres, MySQL, and MSK on AWS. It also supports cross-region access through VPC service endpoints. PrivateLink connectivity set-up is now fully self-serve through ClickPipes.

Learn more [here](https://clickhouse.com/docs/integrations/clickpipes/aws-privatelink).

## Usage cost API endpoint

A common ask from users was better monitoring around billing and costs, so in February we started exposing a new API endpoint to allow you to programmatically retrieve usage and cost data for your ClickHouse Cloud organization. Whether you’re building internal dashboards or automating budget tracking, it’s easier than ever to stay on top of your ClickHouse Cloud spend.

![usage_api.png](https://clickhouse.com/uploads/usage_api_225d68d4d9.png)

*Vantage Usage Report showing ClickHouse Cloud usage and costs, powered by the Usage Cost API under the hood.*

## New user roles

We expanded our role-based access control to give teams more flexibility with access control.
* New Member Role (Organization-Level): Member is an organization level role that is assigned to SAML SSO users by default and provides sign-in and profile update capabilities.
* Service-Level Roles: We also introduced two new roles that can be scoped to services:
    * Service Admin: Full control of assigned services.
    * Service Read Only: View-only access. 

These service roles can be assigned to users who already have a Member, Developer, or Billing Admin role. Refer to [Access control in ClickHouse Cloud](https://clickhouse.com/docs/cloud/security/cloud-access-management/overview) for more information.

## PCI and HIPAA compliance

Security and compliance are at the core of everything we do. In addition to an already exhaustive list of [security and compliance reports](https://clickhouse.com/docs/cloud/security/security-and-compliance), ClickHouse Cloud began to meet key requirements for PCI DSS and HIPAA in February. If you need to build analytics applications for regulated industries like healthcare and finance, we have you covered. We support PCI and HIPAA in select regions at this time, please refer to the documentation for the list of [supported regions](https://clickhouse.com/docs/cloud/reference/supported-regions#hipaa-compliant-regions). To request access, please review guidelines [here](https://clickhouse.com/docs/cloud/security/security-and-compliance).

## We’re Just getting started: summer is coming

These updates are part of our commitment to delivering the most powerful, flexible, and user-friendly ClickHouse backend for your application. As always, we'd love to hear your feedback. You can view the full changelog [here](https://clickhouse.com/docs/whats-new/changelog/cloud), engage with our team directly in our [community Slack](https://clickhousedb.slack.com/ssb/redirect), and [get started with a free trial](https://console.clickhouse.cloud/signUp).

Stay tuned for more.

