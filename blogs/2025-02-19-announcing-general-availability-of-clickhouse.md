---
title: "Announcing General Availability of ClickHouse BYOC (Bring Your Own Cloud) on AWS"
date: "2025-02-19T20:36:25.062Z"
author: "ClickHouse Team"
category: "Product"
excerpt: "Today, we announce the GA of ClickHouse BYOC on AWS. A fully managed ClickHouse Cloud service deployed in your own AWS account.  Designed for large-scale deployments, with personalized support and onboarding. SOC 2 and ISO 27001 aligned. "
---

# Announcing General Availability of ClickHouse BYOC (Bring Your Own Cloud) on AWS

As enterprises modernize with cloud-native architectures on AWS, they can leverage the comprehensive security controls of AWS while meeting their specific compliance requirements and geographic regulations. AWS Virtual Private Cloud (VPC) provides the foundation for secure database deployments, where keeping sensitive data within the customer's own VPC boundary is a critical requirement. 

[ClickHouse BYOC](/cloud/bring-your-own-cloud) enables organizations to access the real-time analytical capabilities of ClickHouse Cloud, while ensuring their data remains entirely within their own AWS VPC environment, simplifying security reviews and compliance processes. In the ClickHouse BYOC architecture, the data plane consisting of storage and compute resources remains in the customer’s own VPC, rather than being transferred to the ClickHouse VPC, and the customer can leverage the extensive security controls of AWS to meet specific governance requirements.

<a href="/cloud/bring-your-own-cloud" style="background-color: #FAFF69; color: black; border: none; padding: 8px 12px; font-size: 14px; cursor: pointer; font-weight: 500; border-radius: 4px; margin: 16px auto 32px auto; display:block; max-width: 130px;">
  Request access
</a>


<blockquote>
<p>"The evolution of ClickHouse Cloud is influenced by the insights we gain from working closely with our users. Our users in banking, healthcare, and cybersecurity must adhere to data governance mandates. With ClickHouse BYOC on AWS, we make all the features of a fully-managed ClickHouse Cloud available in an operating environment known and trusted by our customers… their own AWS VPC."</p>
<p>Tanya Bragin, VP Product &amp; Marketing, ClickHouse</p></blockquote>

By adopting ClickHouse BYOC, customers can benefit from full compute-storage separation (powered by the proprietary [SharedMergeTree engine](https://clickhouse.com/blog/clickhouse-cloud-boosts-performance-with-sharedmergetree-and-lightweight-updates)), seamless vertical and horizontal scaling of compute nodes, and [compute-compute separation](https://clickhouse.com/blog/introducing-warehouses-compute-compute-separation-in-clickhouse-cloud). These capabilities enable granular isolation of workloads in multi-tenant environments and more targeted, independent allocation of compute resources, resulting in more optimized compute resource usage and lower infrastructure costs. 

<blockquote>
<p>“ClickHouse BYOC on AWS has transformed the way we deploy and manage ClickHouse, making it more streamlined and cost-effective. By moving to shared-storage architecture and utilizing compute-compute separation capability, we have significantly optimized our infrastructure costs compared to our self-managed ClickHouse deployments.”</p>
<p>Krishna Sai, CTO, SolarWinds.</p>
</blockquote>

## ClickHouse BYOC Architecture

In the BYOC deployment model, all customer data is hosted in the customer VPC on AWS. This includes data stored on disk, data processed via compute nodes (including in memory and local disk cache), and backup data. The only components hosted in the ClickHouse VPC are the web and API interfaces used to manage the organization and services, responsible for operations like user management, service start/stop, and scaling. 

Detailed logs and metrics collected by the system are stored in the customer VPC, with only the most critical telemetry and alerts allowed to leave to enable resource utilization and health monitoring. 

![ClickHouse_BYOC_Architecture.png](https://clickhouse.com/uploads/Click_House_BYOC_Architecture_bf220960fd.png)

## ClickHouse BYOC Benefits

The launch of ClickHouse BYOC on AWS is a key milestone in our journey to enable flexible, secure, and high-performance analytics for verticals and markets that need to adhere to the strictest data governance and residency mandates, including cybersecurity, banking, healthcare, and other businesses that manage sensitive PII. 

Businesses no longer need to choose between cloud-native agility and control; they can achieve both, with the following benefits:

* **Data security and control:** BYOC gives customers complete control over their data, ensuring compliance with internal security policies and regulatory requirements. Sensitive data stays within the customer’s cloud environment, and they have full visibility into system access.
* **Greater operational flexibility:** BYOC offers a hybrid deployment model, allowing customers to control their data, while relying on ClickHouse experts for database management, which includes ongoing software upgrades and patches.
* **Performance predictability:** Deploying ClickHouse Cloud data plane in a dedicated customer account ensures optimal workload isolation and gives customers greater flexibility in selecting instance types to best support their workloads.
* **Cloud spend optimization:** With BYOC, customers can continue to leverage existing cloud provider commitments and discounts, and thus optimize their cloud spending. In addition, this model supports VPC peering, which helps reduce data transfer costs, especially at large data volumes. 

<a href="/cloud/bring-your-own-cloud" style="background-color: #FAFF69; color: black; border: none; padding: 8px 12px; font-size: 14px; cursor: pointer; font-weight: 500; border-radius: 4px; margin: 16px auto 32px auto; display:block; max-width: 130px;">
  Request access
</a>

## Part of a broader collaboration

On December 10, 2024, ClickHouse, Inc. [announced](https://clickhouse.com/blog/clickhouse-announces-strategic-collaboration-agreement-with-aws-to-advance-real-time-data-analytics-and-generative-ai-innovation) a five-year strategic collaboration agreement with Amazon Web Services (AWS) to enhance real-time data warehousing, observability, business intelligence, machine learning, and generative AI solutions. This collaboration aims to integrate ClickHouse Cloud more closely with AWS services, facilitating the development of high-performance analytics and generative AI applications. General availability of ClickHouse BYOC exclusively available on AWS today is a significant milestone in this journey. 

## Get started now
If ClickHouse BYOC on AWS is the right fit for your needs, please [contact us](https://clickhouse.com/cloud/bring-your-own-cloud) to get started. 
