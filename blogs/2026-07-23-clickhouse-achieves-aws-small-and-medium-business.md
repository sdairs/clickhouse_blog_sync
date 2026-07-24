---
title: "ClickHouse achieves AWS Small and Medium Business Competency"
date: "2026-07-23T18:54:44.595Z"
author: "Aditya Chidurala"
category: "Company and culture"
excerpt: "ClickHouse has achieved the AWS Small and Medium Business Competency, joining a select group of AWS Partners recognized for deep expertise in real-time analytics for small and medium businesses."
---

# ClickHouse achieves AWS Small and Medium Business Competency

## Summary

ClickHouse has achieved the AWS Small and Medium Business Competency, joining a select group of AWS Partners recognized for deep expertise in real-time analytics for small and medium businesses.

We're excited to announce that ClickHouse has achieved the AWS Small and Medium Business (SMB) Competency

The designation recognizes AWS Partners with validated technical expertise and demonstrated customer success serving small and medium businesses, which AWS defines as companies with annualized revenue under $100 million. Partners must show a sustained base of more than 100 active SMB customers on their AWS-hosted SaaS product.

Earning it means AWS has reviewed our production architectures, our security and operational practices, and our customer outcomes, and it reflects the work we've done with lean teams that punch far above their weight on ClickHouse Cloud.


## Meeting the unique demands of SMB data

Almost every SMB analytics story starts the same way. The product launches on PostgreSQL, the business grows, and the analytical queries that returned in milliseconds at launch now take minutes. The usual answers don't fit a small company: hiring a data engineering team is expensive, pre-aggregating throws away the raw data the business will want later, and running an analytics cluster yourself trades one operational burden for another. 

ClickHouse Cloud is built for teams in that position. It's a fully managed service, so there's no database to install, patch, or capacity plan, and [ClickPipes](https://clickhouse.com/cloud/clickpipes) replicates PostgreSQL data through change data capture in a few clicks, so the operational database keeps doing its job while analytics move to an engine designed for them. [Compute-compute separation](https://clickhouse.com/docs/cloud/reference/warehouses) isolates ingestion from customer-facing queries on shared storage, so each workload pays only for what it uses. Pricing starts with a $300 free trial and scales pay-as-you-go. Procurement runs through [AWS Marketplace](https://aws.amazon.com/marketplace/pp/prodview-p4gwofrqpkltu), where SMBs can apply existing AWS commitments and keep billing consolidated, moving to a committed contract only when the numbers justify it. And for teams that would rather run one platform than two, ClickHouse Cloud also offers Postgres managed by ClickHouse, so the transactional database that starts the story and the analytics engine that scales it live side by side, with CDC built in.

---

## Get started today

Interested in seeing how ClickHouse works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-1383-get-started-today-sign-up&utm_blogctaid=1383)

---

## Customer success from sewer pipes to newsletters

[SewerAI](https://clickhouse.com/blog/sewerai-sewer-management-at-scale) uses computer vision to detect defects in sewer and stormwater inspection footage for cities, water utilities, and engineering firms. Its analytics run on ClickHouse Cloud, with ClickPipes replicating Amazon RDS for PostgreSQL through change data capture and refreshable materialized views joining more than 40 tables into a single denormalized table holding hundreds of billions of rows. Municipal queries that took minutes on Postgres now return in seconds, and when data volume tripled and read and write operations grew tenfold over three months, compute usage stayed flat. "We didn't have any more failing updates. Because of that, we didn't have backlogs. Our analytics were up to date, and our customers were happy," says Sabrina Kell, Senior Software Engineer at SewerAI.

[Rapid Delivery Analytics](https://clickhouse.com/blog/rda-tracks-real-time-cpg-performance-with-clickhouse), a digital-shelf analytics platform for quick commerce, runs a team of under 25 people serving CPG brands like PepsiCo and Unilever across more than 40 delivery apps in over 100 countries. ClickHouse Cloud on AWS ingests more than 500 GB of raw data a day, search queries return in under a second, and daily aggregations across billions of rows complete in under an hour. "ClickHouse Cloud is the core of our solution. It gives us the kind of capabilities and infrastructure you'd expect from a much bigger, better-known corporation, while still letting us stay lean," says co-founder and CEO Andrey Dyatlov.

[m3ter](https://clickhouse.com/blog/why-m3ter-clickhouse-cloud), the usage-based billing platform, has a requirement most databases can't meet: store every raw usage event without pre-aggregating, because customers change pricing mid-cycle and rerate their bills, then aggregate hundreds of millions of events a month fast enough for near-real-time invoices. On ClickHouse Cloud, queries average under 100 ms, compression runs at 11.4x, and the database cost for its rating workload dropped roughly 85% against the previous solution. Storage offloads to Amazon S3, AWS PrivateLink keeps billing data off the public internet, and the whole deployment was purchased through AWS Marketplace.

[beehiiv](https://clickhouse.com/blog/data-hive-the-story-of-beehiivs-journey-from-postgres-to-clickhouse), the newsletter platform sending billions of emails a month, moved analytics off PostgreSQL when its team spent more time fighting scalability fires than shipping features. Amazon MSK now streams every send, open, click, and web session into ClickHouse Cloud, with Postgres CDC ClickPipes syncing operational context alongside. Publishers who once waited hours after an email blast see performance data in seconds, median query latency sits at 22 ms, and the main analytics table has grown past 177 billion rows.

The pattern repeats across the SMB base. [Padlet](https://clickhouse.com/blog/padlet) ingested nearly 8 billion classroom events in a single month on ClickHouse Cloud with a median latency of 45 ms. [Mintlify](https://clickhouse.com/blog/mintlify) replaced PostHog with ClickHouse Cloud, cut dashboard load times to under a second at 60% lower cost, and estimates a 30% NPS improvement. You'll find more in our [user stories on AWS](https://clickhouse.com/user-stories?cloudProvider=aws).


## Looking ahead

SMBs are adopting AI faster than they're hiring data teams, and the two trends only work together if the data layer holds up. We're continuing to invest here, from ClickPipes and Postgres CDC ingestion to the [ClickHouse MCP server](https://clickhouse.com/ai) that lets AI agents query business data directly, all on a service that starts at $300 in credits and grows to a committed contract without a replatform. If you're a small team with a big data problem on AWS, we'd love to work with you.

[Get started](https://clickhouse.cloud/signUp?loc=blog-cta-footer&utm_source=clickhouse&utm_medium=web&utm_campaign=blog) with ClickHouse Cloud today and receive $300 in credits. At the end of your 30-day trial, continue with a pay-as-you-go plan, or [contact us](https://clickhouse.com/company/contact?loc=blog-cta-footer) to learn more about our volume-based discounts. Visit our [pricing page](https://clickhouse.com/pricing?loc=blog-cta-header) for details.