---
title: "ClickHouse achieves AWS Cloud Operations Competency"
date: "2026-06-26T08:27:37.218Z"
author: "Aditya Chidurala"
category: "Company and culture"
excerpt: "ClickHouse has achieved the AWS Cloud Operations Competency in Monitoring and Observability. Teams like Modal, Exabeam, and Langfuse run full-fidelity logs, metrics, and traces on ClickHouse, querying them in real time without sampling or runaway cost."
---

# ClickHouse achieves AWS Cloud Operations Competency

## Summary

ClickHouse has achieved the AWS Cloud Operations Competency, joining a select group of AWS Partners recognized for deep expertise in monitoring, logging, and observability at scale.

We're excited to announce that ClickHouse has achieved the **AWS Cloud Operations Competency** in the **Monitoring and Observability** category.

The designation recognizes AWS Partners with validated technical expertise and demonstrated customer success, helping teams operate reliable systems on AWS through full-fidelity logs, metrics, and traces.

Earning it means AWS has reviewed our production architectures, our security and operational practices, and our customer outcomes, and it reflects the work we've done with engineering teams running observability and security operations on ClickHouse Cloud across AWS.

## Meeting the unique demands of observability data 

Observability data is the hardest workload most teams will ever store. A single service emits logs, metrics, and traces continuously, every container and pod adds cardinality, and an agent run can produce hundreds of spans before a user notices anything is wrong. Legacy stacks force a trade most operators hate: sample the data, drop fields, or cap retention at two weeks to keep the bill down, which is precisely when an incident sends query volume through the roof and the dashboard slows to a crawl. The result is blind spots in the exact moment visibility matters most.

The workload underneath is high-volume, high-cardinality, and high-concurrency, with freshness as a hard requirement, and that's the workload ClickHouse was built for. Columnar storage with heavy compression keeps full-fidelity telemetry affordable instead of forcing sampling, the parallel query engine returns sub-second answers under thousands of concurrent users, and [ClickPipes](https://clickhouse.com/cloud/clickpipes) streams events continuously from Amazon Kinesis, Amazon MSK, and Amazon S3. [Compute-compute separation](https://clickhouse.com/docs/cloud/reference/warehouses) keeps ingestion from slowing the investigations your on-call engineers depend on, and [ClickStack](https://clickhouse.com/clickstack), our OpenTelemetry-native observability stack, unifies logs, metrics, and traces as wide events on top of it. On AWS, all of it runs with private networking through AWS PrivateLink, multi-region deployment, and AWS Marketplace billing.


---

## Get started today

Interested in seeing how ClickHouse works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-1108-get-started-today-sign-up&utm_blogctaid=1108)

---

## Customer success across monitoring, security, and AI 

Teams running large-scale infrastructure on AWS use ClickHouse Cloud to see what their systems are doing in real time. [Modal](https://clickhouse.com/blog/modal-real-time-observability-ai-workloads), an infrastructure platform for AI workloads across thousands of GPUs and containers, moved to ClickHouse Cloud after hitting read and write limits, and now runs a single table that ingests 1 to 2 million events per minute, stores roughly 500 billion logs, and still returns sub-second queries. [Lovable](https://clickhouse.com/blog/lovable-ai-powered-observability), the fastest-growing software company in history at over $100 million in subscription revenue eight months after launch, runs observability and AI-powered debugging across millions of generated apps, using the ClickHouse MCP server to investigate billions of logs with natural-language prompts and serving real-time analytics in under 50ms. [Tekion](https://clickhouse.com/blog/tekion-adopts-clickhouse-cloud-to-power-application-performance-and-metrics-monitoring), which runs a cloud platform for the automotive retail industry, adopted ClickHouse Cloud for application performance and metrics monitoring and cut two months of data from 27 TB to 2.5 TB, a 10x storage reduction, while ingesting 1.2 million records per minute and freeing up 25% of its Spark resources.

Security teams put the same engine to work on threat detection. [Exabeam](https://clickhouse.com/blog/exabeam-clickhouse-security-analytics), a security operations platform, runs ClickHouse Cloud across 10 global regions, ingesting 1.2 million events per second per region and more than 80 billion events daily, with over a trillion events stored, about 3.5 petabytes of raw data compressed to 200 TiB. "ClickHouse has helped us lower mean time to detection," says Vinayak Saokar, VP of Engineering at Exabeam. [Harvey](https://clickhouse.com/blog/how-harvey-uses-clickhouse-for-proactive-threat-detection), the legal AI company, turned to ClickHouse Cloud with security analytics platform RunReveal to restructure how it processes network logs, selecting primary indexes on source IPs, destination IPs, and destination ports and pre-computing aggregations with materialized views to track network activity over time.

Digital-native platforms run their core operational visibility on ClickHouse Cloud. [Qonto](https://clickhouse.com/blog/qonto), a digital bank serving more than 600,000 businesses across eight European markets, migrated from Grafana Tempo to ClickHouse Cloud for unified traces, logs, and events, compressed 231 TB of high-cardinality data down to 376 GB for a 99.84% ratio that saves an estimated $70,000 a year in S3 costs, and built an AI incident companion on the ClickHouse MCP server that anyone can query in plain English. For Javier Ortiz, who leads SRE Observability at Qonto, "cardinality was a scary word for us, now it's something I actively root for." Sony LIV ingests tens of millions of video streaming events into ClickHouse Cloud to monitor quality of service and quality of experience in real time, and reports that the platform helps it optimize costs and keep services highly available. Laravel built [Nightwatch](https://aws.amazon.com/blogs/big-data/how-laravel-nightwatch-handles-billions-of-observability-events-in-real-time-with-amazon-msk-and-clickhouse-cloud), its first-party observability product, on a dual-database pipeline that keeps transactional data in Amazon RDS for PostgreSQL and routes telemetry to ClickHouse Cloud through ClickPipes subscribing directly to Amazon MSK, processing over a billion events a day at sub-second query latency.

Observability vendors build their products on ClickHouse Cloud too. [Langfuse](https://clickhouse.com/blog/langfuse-llm-analytics), the open-source LLM observability and evaluation platform that joined ClickHouse in 2026, moved its trace storage from Postgres to ClickHouse Cloud and cut query latency from minutes to near real-time, with a wide-table rewrite delivering up to 200x faster queries on a single project handling billions of events. [Respan](https://clickhouse.com/blog/respan-ai-llm-observability), an AI gateway with built-in LLM observability, outgrew Postgres at 50 to 100 writes per second and migrated ingestion and analytics to ClickHouse Cloud, where it now handles 50 million events a day with incremental materialized views keeping dashboards fast into the billions of rows. You'll find more in our [observability user stories](https://clickhouse.com/user-stories?useCase=2&cloudProvider=aws).


## Looking ahead 

Observability is moving into the agentic era, where on-call engineers and AI agents investigate incidents together and the signal is rarely at the top of the trace. We're continuing to invest here, from the [ClickStack MCP server](https://clickhouse.com/blog/announcing-managed-clickstack-mcp-server) that gives agents structured investigation tools over logs, metrics, and traces, to [AI Notebooks](https://clickhouse.com/blog/observability-mcp-server-ai-notebooks) for step-by-step root-cause analysis, to fully managed ClickStack on ClickHouse Cloud. If you're running observability or security operations on AWS and want to stop sampling your data to control cost, we'd love to work with you.
