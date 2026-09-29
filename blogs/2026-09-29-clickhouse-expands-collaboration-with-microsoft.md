---
title: "ClickHouse expands collaboration with Microsoft, bringing Fabric integration, deeper OneLake interoperability, and enterprise deployment flexibility"
date: "2026-09-29T07:24:08.283Z"
author: "Alex Francoeur and Aditya Chidurala"
category: "Company and culture"
excerpt: "ClickHouse expands its Microsoft collaboration with a native Fabric workload, OneLake read and write capabilities, and ClickHouse BYOC availability in the Microsoft Marketplace."
---

# ClickHouse expands collaboration with Microsoft, bringing Fabric integration, deeper OneLake interoperability, and enterprise deployment flexibility

**Barcelona, September 29, 2026 —** ClickHouse, the company behind the open-source, real-time analytical database that has become the data layer for the AI era, today at The European Microsoft Fabric + SQL Community Conference announced a significant expansion of its strategic collaboration with Microsoft. The announcement encompasses four major milestones: the launch of the native ClickHouse workload for Microsoft Fabric, the general availability of OneLake read, the public preview of OneLake write, and the availability of ClickHouse Bring Your Own Cloud (BYOC) in the Microsoft Marketplace.

This expansion builds on ClickHouse's growing presence within the Microsoft ecosystem, where data-intensive organizations rely on [ClickHouse Cloud on Azure](https://marketplace.microsoft.com/en-us/product/saas/clickhouse.clickhouse_cloud?tab=overview) to power real-time observability, business intelligence, AI/ML pipelines, and analytical applications at scale. The deepened collaboration reflects a shared commitment between ClickHouse and Microsoft to give data teams fast, flexible, and open infrastructure for the next generation of analytics and AI.

"Expanding our collaboration with Microsoft brings ClickHouse performance and deployment flexibility to where our customers' data increasingly lives," said Yury Izrailevsky, President, Product & Engineering at ClickHouse. "Our engineering teams have worked closely together so that these capabilities are seamlessly integrated into the Microsoft data platform rather than layered on top of it, and joint customers no longer have to trade off between the platforms they've standardized on."

## Sub-second analytics with the ClickHouse workload for Microsoft Fabric {#clickhouse_workload_for_microsoft_fabric}

The ClickHouse workload for Microsoft Fabric is now available in public preview through the Fabric workload hub. It brings the ClickHouse query engine directly into the Fabric experience, so data teams can accelerate OneLake queries to sub-second response times without leaving Fabric.

For joint customers, the value is straightforward. Fabric provides the unified data estate, the governance, and the business user surface area. ClickHouse provides the speed. Highly concurrent agentic workloads, real-time interactive dashboards, and observability that were previously impractical to serve directly from a lakehouse now run at the latency users expect, with no separate cluster to provision, and no ETL pipeline to maintain.

"We’ve long believed that unifying data in OneLake using open, standards-based formats will enable customers to innovate faster," said Dipti Borkar, Vice President, Microsoft IQ and OneLake, Microsoft. "With the ClickHouse workload available in Fabric, running on OneLake, joint customers have more best-in-class analytical engines to choose from to deliver analytics and AI, without moving or copying data between platforms. This collaboration is a strong example of our partner ecosystem extending what teams can do on a single, unified data estate."

[Learn more](https://clickhouse.com/blog/clickhouse-for-microsoft-fabric?utm_medium=referral&utm_source=press&utm_campaign=microsoft-fabcon-press)

## Reading Apache Iceberg tables from OneLake (GA) {#reading_apache_iceberg_tables_from_onelake}

ClickHouse support for reading Iceberg tables from OneLake using OneLake Table APIs is now generally available. Customers can query Iceberg tables managed in OneLake directly from ClickHouse, with no data duplication and no ingestion step.

This removes the friction that has historically forced data teams to choose between a governed lakehouse and a fast analytical engine. Organizations can keep OneLake as the single source of truth for their data estate while applying ClickHouse's query engine to the full breadth of it.

[Learn more](https://clickhouse.com/blog/clickhouse-integrates-with-microsoft-onelake?utm_medium=referral&utm_source=press&utm_campaign=microsoft-fabcon-press)

## Writing Apache Iceberg tables to OneLake (public preview) {#writing_apache_iceberg_tables_to_onelake}

ClickHouse support for writing Iceberg tables to OneLake using OneLake Table APIs with credential vending is now in public preview. This allows ClickHouse users to write results back into OneLake as governed, open-format tables that any Fabric engine can read.

This brings the data lifecycle full circle. Data can be read from OneLake, transformed and aggregated at ClickHouse speed, and written back into the lakehouse where Power BI, notebooks, and the rest of the Fabric ecosystem consume it.

[Learn more](https://clickhouse.com/blog/clickhouse-now-writes-to-microsoft-onelake?utm_medium=referral&utm_source=press&utm_campaign=microsoft-fabcon-press)

## ClickHouse BYOC is now available in the Microsoft Marketplace {#clickhouse_byoc_in_microsoft_marketplace}

ClickHouse Bring Your Own Cloud (BYOC) is now available to Azure customers through the Microsoft Marketplace. BYOC lets organizations run ClickHouse Cloud inside their own Azure tenant, giving them the operational simplicity of a fully managed service without relinquishing control of their data environment. Data never leaves the customer's environment; IAM policies, network controls, and encryption configuration remain under the customer's direct ownership, while ClickHouse manages provisioning, upgrades, monitoring, and scaling. For enterprises operating under strict data residency, compliance, or sovereignty requirements, BYOC provides a path to adopt ClickHouse Cloud without compromise.

Availability in Microsoft Marketplace means both products can be procured through existing Microsoft agreements and count toward Microsoft Azure Consumption Commitments (MACC), removing procurement friction for enterprise buyers.

[Learn more](https://marketplace.microsoft.com/en-gb/product/clickhouse.byoc_clickhouse_cloud)

## About ClickHouse {#about_clickhouse}

ClickHouse, Inc. is the company behind ClickHouse, the open-source, real-time analytical database that has become the data layer for the AI era. Built for the speed, scale, and efficiency that modern applications and AI agents demand, ClickHouse lets companies run real-time analytics, data warehousing, observability, AI, and agent observability, and transactional workloads. More than 4,000 customers, including DoorDash, Ramp, Meta, Tesla, Cisco, and Visa, build on ClickHouse. Headquartered in the San Francisco Bay Area with offices in Amsterdam, London, New York, Singapore, Sydney, and Tokyo, ClickHouse is backed by investors including Dragoneer Investment Group, Khosla Ventures, Coatue, Altimeter Capital, Index Ventures, Benchmark, J.P. Morgan Private Capital, BDT & MSD Partners, Craft Ventures, and 20VC. Learn more at [clickhouse.com](http://clickhouse.com?utm_medium=referral&utm_source=press&utm_campaign=microsoft-fabcon-press).


---

## Get started today

Interested in seeing how ClickHouse works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-2428-get-started-today-sign-up&utm_blogctaid=2428)

---