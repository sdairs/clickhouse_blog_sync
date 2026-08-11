---
title: "How Musinsa scaled its audience engine with ClickHouse Cloud and reduced TCO by 71.4%"
date: "2026-08-10T14:57:17.101Z"
author: "ClickHouse"
category: "User stories"
excerpt: "Musinsa migrated its audience engine from self-hosted ClickHouse to ClickHouse Cloud, cutting storage costs by 86.5% and total cost of ownership by up to 71.4% while simplifying real-time ingestion with ClickPipes."
---

# How Musinsa scaled its audience engine with ClickHouse Cloud and reduced TCO by 71.4%

## Summary

* Musinsa, Korea’s largest fashion platform, uses ClickHouse Cloud to power a customer data platform (CDP) that targets audiences across 16.4 million members.  
* Migrating from self-hosted ClickHouse to ClickHouse Cloud helped Musinsa cut storage costs by 86.5% and total cost of ownership by up to 71.4%.  
* While ingestion previously required additional tools such as Databricks Auto Loader, ClickPipes now simplifies and scales real-time ingestion.

[Musinsa](https://global.musinsa.com/) is Korea’s largest fashion platform. Founded in 2001 as an online sneaker community, it has grown into a full-scale ecommerce platform with 16.4 million members, 7.2 million monthly active users, and around 11,000 partner brands. Recently, it has been expanding abroad, with services now running in 13 countries across Asia, North America, and Oceania.

In August 2025, Musinsa launched a customer data platform (CDP) that collects data about users, both who they are (e.g. age, gender) and actions they take (e.g. browsing, adding to cart, buying products). Marketers use that data to group users into audiences based on conditions (e.g. “men in their 30s,” “people who abandoned a cart in the last seven days”), either by hand or by letting machine learning expand a group to similar users, and reach them through channels like paid ads and targeted push notifications.

In January 2026, Musinsa expanded its CDP with MAI, an AI assistant that lets marketers get statistical data instantly by asking in natural language. The agent also shows the methods and criteria used for data analysis, so users can see how a number was derived rather than just getting the figure.

At [AWS Summit Seoul 2026](https://summitseoul.awslivestream.com/sel-prt103-s/live/), backend engineer Byeonggil Park and data engineer Minyoung Choi shared how Musinsa built the Audience Engine behind its CDP, why the growth it created outpaced their self-hosted ClickHouse setup, and how migrating to [ClickHouse Cloud](https://clickhouse.com/cloud) on AWS drove benefits across storage, compute, and the company’s real-time data pipeline.

## The challenges of self-hosting

The Audience Engine is the “most important component of the CDP,” Byeonggil says, the part that takes a condition a marketer enters and returns the group of users who match it.

To make that work, the team stores data in an exploded format, mapping each user to each audience they belong to as a separate row. At Musinsa’s scale, with over 16 million users and 2,500 audiences, that adds up to roughly 1.1 billion cohort-to-user mappings. In the worst case, adding just one audience could mean adding up to 16 million new rows. “Since the data grows exponentially,” Byeonggil says, “we had to think about how to scale both the data and our computing resources.”

For a while, that growth ran on self-hosted ClickHouse, but keeping it running became increasingly hard to sustain. “With self-hosted ClickHouse,” Byeonggil explains, “EBS storage and compute were tied to the same node, which made scaling difficult.” Because the specs were fixed, heavy queries strained the system. “There were times when we had to rely on external computing resources,” Minyoung adds. The self-hosted setup also meant a single cluster had to run multiple workloads at once; with business logic and batch jobs competing for the same resources, an expensive query in one place could drag down everything else.

The operational overhead of self-hosting only compounded the problem. “Managing ClickHouse ourselves turned out to be more burdensome than expected,” Minyoung says. “At Musinsa, the business changes very quickly and there’s always a lot to do, so it was hard to dedicate enough time to improving our infrastructure operations.”

## Why Musinsa chose ClickHouse Cloud

While the Musinsa team was considering whether and how to replace their self-hosted setup, they learned that [ClickHouse Cloud was now available in the Seoul region](https://clickhouse.com/docs/cloud/reference/supported-regions). “It was the solution we needed,” Minyoung says, “we decided to migrate to the cloud.”

Minyoung describes three main reasons why they decided to move to ClickHouse Cloud. The first was that it minimized migration risk. “Since we were already running a self-hosted setup, we could keep most of our existing configurations,” she says, “and there was no learning curve when switching to a different database.”

The second reason was operational automation, including access to ClickHouse’s solutions architects. As Minyoung puts it, “Managing operations used to be a heavy burden, but by switching to a managed service, we were able to reduce that load. Plus, having access to account support whenever we had questions or issues was a huge advantage.”

The third reason was that the managed service addressed the infrastructure constraints of self-hosting. “The managed service helped us overcome those inefficiencies of self-hosting,” Minyoung says. “This allowed us to use ClickHouse more effectively and adapt to our business.”

## Three main benefits of ClickHouse Cloud

At AWS Summit Seoul, Minyoung walked through three benefits Musinsa saw after migrating to [ClickHouse Cloud](https://clickhouse.com/cloud), grouped into three categories: storage, compute, and real-time pipelines.

## Storage

On self-hosted ClickHouse, compute and storage were combined, which, as Minyoung explains, created two problems. Adding nodes to get more compute also added storage the team didn’t need, driving up cost. And because the two were coupled, adding or removing nodes could affect the data itself, which made changes risky.

![](https://clickhouse.com/uploads/musinsa_0_b81279b5d7.jpg)

*Self-hosted ClickHouse tied storage to each node through attached EBS volumes. ClickHouse Cloud separates the layers, with compute nodes drawing on shared S3 storage.*

“ClickHouse Cloud was designed to address these drawbacks by [separating the compute and storage layers](https://clickhouse.com/docs/guides/separation-storage-compute),” Minyoung says, “allowing you to use shared storage and connect compute resources only when needed, then disconnect them when they’re not in use.” With the layers separated, Musinsa can keep more data reliably without paying for compute it doesn’t need, while storage scales on its own. “As a result, we reduced our existing data storage costs by 86.5% and were able to store and utilize much more data,” she says.

## Compute

Storage-compute separation also changed how Musinsa runs its workloads. Where a single cluster once handled everything at once, each workload now gets its own resources, sized to fit. “By separating computing resources by function and assigning the right specs to each, every task runs independently without interfering with one another,” Minyoung says. “As a result, we’re able to operate our services much more reliably.”

![](https://clickhouse.com/uploads/musinsa_1_fb1e8e703a.jpg)

*Each workload runs on its own compute over shared Amazon S3 storage, active only when needed.*

Another advantage is ClickHouse Cloud’s [automatic idling](https://clickhouse.com/docs/cloud/features/autoscaling/idling) feature, which idles a cluster when it isn’t in use. As Minyoung puts it, “This feature is especially effective for batch pipelines or periodic data loads, since resources are only used when needed and switch to idle mode the rest of the time.” [Vertical autoscaling](https://clickhouse.com/docs/cloud/features/autoscaling/vertical) does the inverse, raising resources when a query needs more memory, then scaling back down once it’s done.

Together, these changes reshaped Musinsa’s compute costs. “By introducing this computing layer,” Minyoung says, “we were able to reduce previous total cost of ownership by up to 71.4%.”

## Real-time pipelines

The last improvement was in how data gets into ClickHouse. Previously, the team relied on Databricks Auto Loader, an external stage running on a separate Spark cluster. With [ClickPipes](https://clickhouse.com/cloud/clickpipes), ClickHouse Cloud’s native ingestion layer, they can integrate data directly into ClickHouse, reducing operational overhead and Databricks costs.

![](https://clickhouse.com/uploads/musinsa_2_cfe8497013.jpg)

*Before and after: Databricks Auto Loader on an external Spark cluster gave way to ClickPipes, which ingests directly into ClickHouse Cloud and hands off to materialized views and storage.*

“ClickPipes enables real-time data ingestion from a variety of sources,” Minyoung says. “With just a simple configuration, you can easily set up real-time pipelines without the hassle of manual setup.”

> That ease of use becomes increasingly more important as we support more services. With ClickPipes, we can easily scale up with minimal effort, saving operational and overall ingestion costs.
>
> — Minyoung Choi, Data Engineer, Musinsa

## More time for what matters

With the migration to [ClickHouse Cloud](https://clickhouse.com/cloud), Musinsa’s storage costs fell sharply, compute scaled to each workload instead of one overloaded cluster, and ingestion moved inside ClickHouse.

“Ultimately, these improvements in ClickHouse Cloud helped us use fewer infrastructure resources and let us focus on our core business logic,” Minyoung says. “By simplifying our infrastructure, we were able to focus on developing CDP business logic and shift our attention from operational issues to product development.”

For anyone thinking about upgrading their database, her recommendation is clear: “Depending on your team's operational capabilities, if you're looking to reduce the burden of managing a self-hosted ClickHouse, ClickHouse Cloud is a great choice.”


---

## Get started today

Interested in seeing how ClickHouse works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-1488-get-started-today-sign-up&utm_blogctaid=1488)

---