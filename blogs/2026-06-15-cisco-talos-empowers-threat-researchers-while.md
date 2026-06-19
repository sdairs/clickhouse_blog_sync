---
title: "Cisco Talos empowers threat researchers while reducing TCO by 75% with ClickHouse Cloud"
date: "2026-06-18T16:16:41.458Z"
author: "ClickHouse"
category: "User stories"
excerpt: "Cisco Talos runs a threat intelligence reputation service on ClickHouse Cloud, classifying file hashes so researchers can make fast, accurate security decisions."
---

# Cisco Talos empowers threat researchers while reducing TCO by 75% with ClickHouse Cloud

## Summary

* Cisco Talos runs a threat intelligence reputation service on ClickHouse Cloud, classifying file hashes so researchers can make fast, accurate security decisions.  
* The team migrated a nearly 2-trillion-row, 2 PB dataset from self-managed OSS ClickHouse to ClickHouse Cloud with zero downtime and a 100% data match.  
* The move cut storage costs by \~90%, reduced TCO by \~75%, and reclaimed over 300 engineer hours a year for building new products.

[Cisco Talos](https://talosintelligence.com/) is one of the world's most trusted cybersecurity threat intelligence teams, made up of expert researchers, analysts, incident responders, and engineers. They defend [Cisco](https://www.cisco.com/site/us/en/index.html) customers and raise awareness of evolving threats within the cybersecurity community, partnering with industry and government organizations around the globe.

Senay Goitom is part of a small engineering team that provides the centralized data lake and enrichments behind that mission. One of its most important offerings is a reputation service built on a massive hash dataset, which classifies the disposition of every file artifact Talos sees, storing the verdicts for individual file hashes collected from Cisco product telemetry.

> "Our threat researchers use these data for guardrails that prevent false positive convictions of benign hashes, and our threat hunters use them to look for low prevalence hashes that might be signals for malware campaigns. In both cases, they, and by extension, our customers need fast, accurate answers." — Senay Goitom, Software Engineer, Cisco

But delivering those answers is, as Senay puts it, like searching for a needle in a haystack. In production, the dataset holds nearly 2 trillion rows, with 27 billion new rows ingested daily. On disk, that's around 192 TB of compressed data, or around 2 PB uncompressed. Because these systems power threat intelligence services for Cisco customers, latency and accuracy directly impact the company's security products.

At our [2026 Open House SF user conference](https://clickhouse.com/openhouse/san-francisco), Senay shared how he and the team moved this workload from OSS ClickHouse to [ClickHouse Cloud](https://clickhouse.com/cloud) on AWS and how it helped Cisco dramatically reduce costs with zero downtime.

## Outgrowing the old architecture

In the original design, data originated in a Databricks Delta table stored as Parquet files in S3. A custom, event-driven serverless ingestion pipeline fed a self-managed Kubernetes (EKS) cluster, where a staging table rolled up into an aggregated table behind an API endpoint. Under the old retention policy, the team kept about a petabyte of compressed, replicated data on 32 high-compute nodes, each with seven EBS volumes attached.

![](https://clickhouse.com/uploads/ciscotalos_jun2026_image1_63d917b06b.jpg)

*Cisco Talos's original self-managed architecture: a custom ingestion pipeline feeds an EKS cluster, with data flowing from a staging table to an aggregated table behind an API endpoint.*

"It worked," Senay says, "but we started experiencing some challenges." As a small team inside a threat research organization, they found that running a cluster of that size pulled them away from their actual mission. "We were spending time on upgrades, backups, and troubleshooting," he explains, "instead of building new products for our threat researchers."

That setup also tied the team's storage to compute in a costly way. "Query performance needs meant we had to tie our ever-increasing storage needs to expensive compute nodes," Senay says. "Scaling up or down, depending on traffic, was a costly process and risked service disruption for our consumers. We have to ensure customer trust, so it ultimately meant that we had to over-provision."

He highlights two other challenges beyond the operational and cost burden. The first was SOC 2 compliance. "We had to be constantly vigilant about vulnerability management," Senay says, noting that this added even more overhead to an already lean team. The other was architectural complexity. Custom ingestion, custom aggregation, and custom optimizations created a system that was "hard to maintain and harder to evolve," requiring "additional engineer hours for maintenance and incident response."

---

## Get started today

Interested in seeing how ClickHouse works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-961-get-started-today-sign-up&utm_blogctaid=961)

---

## Choosing the right real-time data platform to support threat researchers

In their search for a better solution, the team weighed three options. They quickly ruled out Snowflake because of the storage costs and complexity it would have introduced. As Senay puts it, "Our query latency needs meant that we were going to have to go with a more complicated architecture than we would under ClickHouse."

They also looked at MongoDB, but its document model "wasn't a natural fit for our aggregation workload," Senay says, "and it wasn't cost-effective at the scale that we were operating."

That left one clear option: "ClickHouse Cloud was the natural choice," Senay says. The team already knew the technology, and its [columnar storage model](https://clickhouse.com/docs/faq/general/columnar-database) "was a perfect fit for our hash lookup pattern." [Separation of storage and compute](https://clickhouse.com/docs/guides/separation-storage-compute) promised to dramatically reduce storage costs, and conversations with a ClickHouse solutions architect convinced the team they could land on a far simpler architecture than the one they were maintaining themselves.

## Rebuilding around ClickHouse Cloud

Senay and the team ran the migration in four phases. The first laid the foundation: reusable Terraform modules for the ClickHouse service, [ClickPipes](https://clickhouse.com/cloud/clickpipes), and the database resources, plus SSO/SAML integration and the deployment of both dev and prod services. Next came the data pipeline, standing up the new ingestion flow and backfilling 12 months of historical data using sharded ClickPipes.

With the pipeline in place, the team moved to shadow traffic, routing live production queries to both backends in parallel for initial data validation and performance testing. The fourth and final phase was the cutover, a comprehensive data comparison against the source at scale, followed by stakeholder sign-off and the switch itself.

The result was a vastly simplified architecture. The new design keeps the Databricks Delta table as the source, but replaces the custom ingestion code with managed building blocks. Amazon EventBridge detects new objects as they land in S3 and routes them to SQS queues, and ClickPipes handles ingestion into ClickHouse Cloud. "All of that custom code, all of that orchestration is gone," Senay says.

![](https://clickhouse.com/uploads/ciscotalos_jun2026_image2_8cb4fabb23.jpg)

*Cisco Talos's new architecture on ClickHouse Cloud: ClickPipes handles ingestion with no custom code, feeding a staging table that serves queries via AWS PrivateLink behind an API endpoint.*

Inside ClickHouse Cloud, the team uses the [SharedMergeTree table engine](https://clickhouse.com/docs/cloud/reference/shared-merge-tree), which stores data in object storage and is fully managed by ClickHouse. The Lambda function that routes queries to the backend connects over AWS PrivateLink, so traffic never goes through the public internet. Senay adds that a smart [partitioning](https://clickhouse.com/docs/partitions) strategy helped the team "drastically simplify our back end," letting them aggregate at query time rather than pre-aggregating in the cluster.

## A simpler, more cost performant backend

"From an operational perspective," Senay says, "the results speak for themselves." After a month in production, the new pipeline had ingested roughly 3,000 files a day with zero data loss and less than a minute of queue lag between a file landing in S3 and becoming queryable in ClickHouse Cloud. When the team compared API responses between the old and new backends across more than 1,000 randomly selected hashes, the match rate was 100%. All of this validation happened with zero consumer impact and zero downtime.

"And the cost story is just as dramatic," Senay adds. By breaking the dependency between storage and expensive compute, and by retiring the custom ingestion pipeline and the SOC 2 maintenance overhead that came with their old self-managed setup, the team cut storage costs by roughly 90% and reduced total cost of ownership (TCO) by about 75% across compute, storage, and engineering hours.

> "Moving to ClickHouse Cloud has allowed us to dramatically reduce our TCO by 75% and save over 300 engineer hours a year that can be spent on building new products for our threat intelligence teams." — Senay Goitom, Software Engineer, Cisco

For a small team inside one of the world's largest threat intelligence providers, that shift, from maintaining infrastructure to building on it, ultimately serves the researchers hunting threats, and the Cisco customers who depend on them.