---
title: "How Changan Ford cut costs by 40% and powered precision marketing with ClickHouse Enterprise Edition"
date: "2025-09-19T11:46:02.948Z"
author: "ClickHouse Team"
category: "User stories"
excerpt: "Changan Ford migrated their Customer Data Platform to ClickHouse Enterprise Edition, cut costs by 40%, eased the operational workload, and gave the team stability and confidence even during their most demanding campaigns."
---

# How Changan Ford cut costs by 40% and powered precision marketing with ClickHouse Enterprise Edition

[Changan Ford](https://corporate.ford.com/operations/locations/global-plants/changan-ford-automobile-co-ltd-engine-plant.html) was founded in 2001 as a joint venture between Changan Automobile Group, one of China’s largest automakers, and Ford Motor Company. In 2017, as part of its digital transformation strategy, the company established a digital marketing department and built a Customer Data Platform (CDP) to unify data from a wide range of online and offline, internal and external sources. With a complete view of each customer, frontline teams could run targeted marketing campaigns and deliver more personalized after-sales services.

At first, the CDP ran on ClickHouse’s open-source Community Edition, powering real-time segmentation queries across trillions of rows. But as the platform grew, so did its demands. Storing seven years of historical data—over 100 TB—sent storage costs climbing. Traffic spikes during marketing campaigns strained the fixed-resource cluster. Scaling had to be done manually, slowing the team down, and OOM errors became increasingly common.

In 2024, Changan Ford migrated to ClickHouse Enterprise Edition (also known as [ClickHouse Cloud](https://clickhouse.com/cloud)) on Alibaba Cloud. With compute-storage separation, serverless elasticity, and OSS-based storage, the new system cut costs by 40%, eased the operational workload, and gave the team stability and confidence even during their most demanding campaigns.

## A unified view of the customer

Changan Ford’s digital marketing team relies on the CDP for everything from building detailed user profiles to running analytics, targeting ads, and segmenting audiences. To make that possible, they built a platform that collects data across three main categories:

* **Basic data**: Core attributes like customer profiles and vehicle information.  
* **Offline behavior**: In-store and other offline activity, including maintenance records, purchase history, visit frequency, and order generation.  
* **Online behavior**: Interactions across digital touchpoints such as mobile apps, ecommerce portals, WeChat customer service, and private domain traffic. This covers everything from browsing history and ad clicks to purchases, conversations, and social engagement.

![ford_cs_img1.png](https://clickhouse.com/uploads/ford_cs_img1_6b3217d14c.png)
*Changan Ford’s system architecture with application, flat platform, and infrastructure layers.*

Data is cleaned and processed using Apache Flink and Apache Spark, then consolidated into wide tables for storage. This setup supports real-time use cases like tag-based audience segmentation, customer profiling, and attribution analysis. It also powers live dashboards and performance reports, giving Changan Ford’s marketing and after-sales teams the ability to measure impact and adjust strategy on the fly.

## Early architecture challenges

Changan Ford first built its CDP on ClickHouse Community Edition, running it as a self-managed cluster. It delivered impressive results, handling trillions of rows with ease, achieving a 5x compression ratio, running ultra-fast wide table queries, and integrating smoothly with Flink, Kafka, Spark, and other data sources. As a columnar OLAP database, it was more than capable of handling the heavy workloads behind tag-based audience segmentation, customer profiling, attribution analysis, and real-time dashboards and reports.

But by 2024, the system had grown to more than 100 TB of historical data—seven-plus years’ worth—and cracks were starting to show. As the business expanded, three main challenges emerged: rising costs, stability issues, and mounting O&M demands.

![ford_cs_img2.png](https://clickhouse.com/uploads/ford_cs_img2_52dac3227e.png)
*End-to-end data flow from source systems to ClickHouse-powered applications.*

### Storage and compute costs

To meet business requirements for long-term data retention, all historical data had to remain permanently online. This drove up storage costs. And without tiered or serverless storage, the team had to provision cloud disks based on where they thought growth was headed, not where it actually was.

During peak hours (e.g. report generation from 9:00 a.m. to 11:00 a.m.), resource demand could spike to four times the usual load. The self-managed cluster had to be sized for these peaks, which meant paying for a lot of extra capacity that sat idle most of the day.

### System instability

Running on a fixed-spec, self-managed cluster also meant OOM (Out of Memory) errors were a regular occurrence, especially when large, bursty queries came in from specific domains. As data volumes grew and more data sources were connected, stability became harder to maintain.

### High operational complexity

During major marketing campaigns, like new vehicle launches, data volumes and query loads could surge by dozens of times. Scaling the distributed cluster to meet demand required manual intervention. This was time-consuming and complex, hindering the marketing team’s ability to respond quickly to business needs.

## Upgrading to ClickHouse Enterprise Edition

To solve the cost, stability, and scaling issues, Changan Ford’s cloud technology team partnered with the digital marketing department to replace their self-managed ClickHouse Community Edition cluster with ClickHouse Enterprise Edition on Alibaba Cloud. 

The managed service maintains 100% compatibility with open-source ClickHouse but adds key advantages like compute-storage separation and serverless elasticity. This means lower storage costs for large-scale datasets, far less manual work for horizontal scaling and resource management, improved system stability, and no more paying for idle capacity.

![ford_cs_img3.png](https://clickhouse.com/uploads/ford_cs_img3_6c8cb0399c.png)
*Compute-storage separation architecture in ClickHouse Cloud (and ClickHouse Enterprise Edition)*

The core innovation of ClickHouse Enterprise Edition is compute-storage separation. By decoupling compute and storage, each can scale independently, with storage centrally managed via OSS (Object Storage Service). Compute nodes automatically scale up or down based on load, making it easy to handle peak traffic without overprovisioning.

The Enterprise Edition also introduces a serverless computing model that automatically adjusts resources in real time to match actual business demand. Compared to traditional fixed resource allocation, this model dynamically allocates compute power as needed, cutting idle resource costs and keeping performance smooth even during expected surges.

Full syntax compatibility between ClickHouse’s Community and Enterprise Editions meant that Changan Ford didn’t need to adapt their business operations or any applications during testing and migration. The migration process was a simple transfer of historical data from the old self-managed cluster to the new Enterprise Edition cluster.

## Matching resources to demand

Outside of big marketing campaigns, Changan Ford’s cluster usage follows a predictable rhythm of daily peaks and valleys. With serverless elastic computing, ClickHouse Enterprise Edition on Alibaba Cloud scales compute resources up or down in real time to match exactly what’s happening in the business.

![ford_cs_img4.png](https://clickhouse.com/uploads/ford_cs_img4_0e0601443a.png)
*CPU usage, CCU, and memory usage fluctuations in Changan Ford’s customer data platform.*

Here’s how that plays out in practice:

* **Second-level elastic scaling**: During busy periods like marketing campaigns or reporting periods, compute power ramps up within seconds to handle complex queries and high-concurrency workloads. When things quiet down, it automatically scales back to the minimum, eliminating idle waste.

* **Precise cost control**: The pay-as-you-go billing model, paired with elastic scaling, has reduced off-peak costs by more than 70%.

* **Performance and stability assurance**: Pre-set thresholds and intelligent scheduling algorithms detect shifts in demand and respond instantly, keeping latency low and throughput high even during sudden spikes or complex queries.

This dynamic scaling means the cluster grows or shrinks in sync with real business needs. Changan Ford can align resources perfectly with business cycles, saving money while optimizing performance and user experience. 

On the storage side, OSS not only lowers unit prices but also delivers serverless storage. With billing tied to actual data volume, there’s no need to pre-purchase cloud disks “just in case,” eliminating idle storage and driving costs down even further.

## Stability, scalability, and 40% cost savings

Switching to ClickHouse Enterprise Edition instantly made Changan Ford’s CDP more flexible and scalable. The elastic, fully managed architecture has delivered notable improvements in three important areas:

### Cost optimization

Migrating from a self-managed ClickHouse cluster to ClickHouse Enterprise Edition on Alibaba Cloud **cut annual compute and storage costs by more than 40%**. With compute-storage separation and an elastic, pay-as-you-go billing model, resources are provisioned only when they’re actually needed.

During peak periods, compute power scales up automatically; during quieter times, it scales back down, avoiding the waste typical of fixed-spec clusters.

### Improved system stability

During marketing campaigns and busy reporting windows, compute resources **scale within seconds** to handle complex queries and high-concurrency workloads, keeping performance consistent for marketing and analytics teams.

In the first six months after migration, **Changan Ford experienced zero OOM incidents**. The new architecture has eliminated the instability caused by large or bursty queries, providing a reliable foundation for data-driven marketing.

### Increased O&M efficiency

Scaling nodes, once a manual process, **now takes just minutes**. Business read/write operations stay smooth, and O&M pressure is eased well before any marketing surge hits.

With infrastructure and maintenance handled by ClickHouse’s managed service, the marketing team can focus less on cluster management and more on driving strategic initiatives and innovation.

## Getting even more from their data

With the CDP now running smoother, cheaper, and more reliably on ClickHouse Enterprise Edition, Changan Ford is already exploring new ways to put its data to work.

Next on the roadmap is expanding the platform’s role in after-sales analytics, customer profiling, and supply chain optimization. By consolidating more workloads on the same elastic infrastructure, the team aims to improve inventory forecasting, gain deeper behavioral insights, and uncover more opportunities for personalization across the customer journey.

The shift to ClickHouse Enterprise Edition has solved Changan Ford’s cost and performance challenges. Just as important, it’s given them a data foundation that can grow with the business. With real-time scaling, OSS-based storage, and fully managed operations, the Chinese automotive leader now has the flexibility to move faster, adapt more quickly, and extract even more value from every data point.

Curious what ClickHouse Cloud can do for your data operations? [Try it free for 30 days.](https://clickhouse.com/cloud) 