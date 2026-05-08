---
title: "Gala supercharges analytics performance with ClickHouse on AWS"
date: "2026-05-04T13:18:58.453Z"
author: "ClickHouse"
category: "User stories"
excerpt: "Learn how Gala migrated to the ClickHouse Cloud data platform on AWS to improve analytics performance and cut costs"
---

# Gala supercharges analytics performance with ClickHouse on AWS

## Benefits

* 3x increase in data analytics capacity
* 30% reduction in costs
* Query times reduced from minutes to sub-second

[Gala](https://games.gala.com/) runs a blockchain-powered platform where users can enjoy their favorite games and other media and access a range of decentralized finance products. The company is reliant on analytics to improve game performance, identify new development opportunities, and support marketing planning. But its existing data platform was struggling to cope with the amount of data it needed to ingest and process. After an assessment of the solutions on the market, Gala chose AWS Partner [ClickHouse](https://clickhouse.com/) to deliver the robust data infrastructure that it needed. Built on Amazon Web Services (AWS), the platform offers faster ingestion and has delivered insights that have led to improved productivity for the Gala engineering and marketing teams, better gaming experiences for players, and reduced costs.

## Scaling a growing mountain of data

Gala was formed in 2019 by Zynga co-founder Eric Schiermeyer and offers popular multi-player games like Spider Tanks and GRIT, along with music and video content. The company was built on a blockchain platform to give users transparent ownership of assets and purchases and to encourage greater buy-in and engagement with the gaming ecosystem. The company also created a decentralized exchange to allow users to trade with each other without an intermediary.

Data is critical for product development. The company’s fast-paced games generate huge amounts of telemetry data from user interactions, which is crucial for understanding player behavior, optimizing monetization, experimenting, and improving the overall gaming experience. But as the company’s games portfolio expanded and its user base grew, its existing data infrastructure struggled with the volume of data.

In addition to product development, the company’s marketing teams needed analytics data to help direct effective campaigns and strategies. Meanwhile, its engineering teams were spending an increasing amount of time managing the data infrastructure rather than focusing on more strategic initiatives. This needed to change if the business was going to continue to grow. The leadership team at Gala decided to review the data platform market for a suitable replacement for its existing Databricks system.

## A quick migration to a ‘Rocket-Fast’ data platform

After an investigation of leading data platforms, the company chose to migrate to [ClickHouse Cloud](https://clickhouse.com/cloud) on AWS, through the AWS Marketplace. The platform was chosen for the scalability and performance improvements it offered and for its lower costs. Because much of Gala’s infrastructure was already built on AWS, it was a natural fit for hosting the ClickHouse Cloud platform.

The initial workload was ingesting its blockchain data from Kafka, but the team quickly recognized the performance and cost benefits possible by powering their analytical dashboards on AWS. Gala has since expanded data sources to include Airbyte, [Amazon S3](https://aws.amazon.com/s3), and Fivetran for continuous ingestion of data.

After the team had completed the ingestion of multiple data sources into ClickHouse Cloud, the next stage was the optimization of queries, resources, and connectors, with a focus on further reducing costs and improving efficiency. “ClickHouse is well known as one of the fastest database systems out there,” says Mike Rexford, lead data analyst at Gala. “And that has proven itself out, especially when you’re using its features to their fullest. It is rocket fast.”

Another early catalyst for change was to make analytics and business intelligence (BI) capabilities available to the broader company and make data products more accessible to employees without the relevant technical skills. The company wanted to use Metabase, a user-friendly, open-source BI and data visualization tool, to enable this but its previous system couldn’t serve the necessary data at the required speed. ClickHouse Cloud was able to support the rollout of Metabase and enable business teams across the company to run their own queries and analytics on the tool. This was enabled by using ClickHouse Cloud’s ability to save queries and run API endpoints directly to those saved queries. This change helped remove technical barriers to its analytics.

Gala found the support from ClickHouse “super responsive” despite being in distant time zones. Technical support was particularly helpful for system-based concerns relating to early data ingestion issues. The company’s small internal technical team appreciated that, if there was a criticism or a problem, ClickHouse listened and fixed the problem or removed it in the next release.

## Sub-second performance and a 30% cost reduction

Performance has improved significantly. “We did have a few unoptimized tables in our previous platform we were struggling with. We had query times in the minutes,” says Keith Cook, data engineer at Gala. “Once we switched over to ClickHouse, we got the indexing correct from the get-go and ended up with sub-second query times on the same tables.”

Using ClickHouse Cloud on AWS has enabled the company to increase the amount of data available for analysis, rising from 3 TB at the start of the project in February 2024 to 9 TB by the completion of the migration in December 2024, when it decommissioned its old system. The initial costs for working in ClickHouse were 30 percent lower than on its previous data platform. The next steps are to use the ClickHouse ClickPipes data-processing pipeline to build an even more efficient extract, load, transform (ELT) function.

In addition to faster performance and scalability, ClickHouse has delivered greater reliability, which means that Gala’s engineers spend less time in maintenance mode. “We just don’t think about our data infrastructure as much anymore,” says Rexford. “If something is running slowly and people are wondering what is causing the bottleneck, we know for sure it’s not the database.”