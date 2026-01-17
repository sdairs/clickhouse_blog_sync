---
title: "Introducing ClickHouse Government on AWS"
date: "2025-06-09T09:15:42.728Z"
author: "Leticia Webb"
category: "Product"
excerpt: "We are excited to introduce ClickHouse Government, a solution specifically designed for the public sector. "
---

# Introducing ClickHouse Government on AWS

We are excited to introduce ClickHouse Government, a solution specifically designed for the public sector. Performance, cost savings, ease of deployment, and security. Intrigued? Read on and join our [waitlist](https://clickhouse.com/government)! 

## Our story

ClickHouse, Inc., founded in 2021 and headquartered in the California Bay Area, is incorporated in Delaware. As the creators of the widely adopted open-source ClickHouse database, the company launched the proprietary cloud-native architecture supporting ClickHouse Cloud on AWS in December, 2022. Today, ClickHouse Cloud runs globally across AWS, GCP, and Azure, with support for Bring Your Own Cloud (BYOC) deployments on AWS.

## Architecture

Our cloud-native architecture is built for separation of compute and storage, which significantly improves resource utilization. We deploy compute via Kubernetes due to its built-in functionality for scaling, scheduling, monitoring, and easy integration with load balancers. The ClickHouse Operator enables automating cluster configuration and events. ClickHouse utilizes object storage such as AWS’s Simple Storage Service (S3) to achieve scalability and cost benefits while maintaining insert and query performance.

ClickHouse Government is built using this architecture to achieve the same performance we enjoy in our own cloud environment, packaged to be deployed to yours. The package is initially available in AWS, and we are taking requests for additional clouds or hardware-based environments.

![ClickHouse Government Diagram.webp](https://clickhouse.com/uploads/Click_House_Government_Diagram_4d513727c3.webp)

## Feature-rich

In addition to the separation of compute and storage we enjoy in our cloud, ClickHouse Government will stay close to the version we run in ClickHouse Cloud. This provides proprietary features, such as [SharedMergeTree](https://clickhouse.com/docs/cloud/reference/shared-merge-tree). This unique table engine offers higher insert throughput, improved throughput of background merges, improved throughput of mutations, and more lightweight strong consistency for select queries. Additionally, as we add new features, functionality is thoroughly tested to ensure it continues to meet our standards.

## Compression

ClickHouse Cloud also benefits from the [ZSTD compression algorithm](https://clickhouse.com/docs/data-compression/compression-in-clickhouse#compression-in-clickhouse-cloud), which has the advantage of being consistently fast on decompression (around 20% variance) and having the ability to be parallelized. Based on the vendor and use-case, some customers have reported using 50% less disk space than Postgres, 38% better compression than Snowflake and 30x better compression than BigQuery (learn more on our [Use Cases](https://clickhouse.com/use-cases) page).

## Performance and cost efficiency

Architecture, features, and efficient compression ratios working hand-in-hand have helped ClickHouse Cloud customers achieve near unbelievable levels of speed and compression, resulting in 2-10x improved performance and 3-5x cost savings over other providers. At a time when government missions are expanding while budgets are tightening, ClickHouse Government is built with the same architecture, features and compression ratios as ClickHouse Cloud, enabling public sector customers to achieve both cost reduction while delivering performance improvements.

![2025-06-09_10-21-04.png](https://clickhouse.com/uploads/2025_06_09_10_21_04_412d17efeb.png)

## Ease of implementation

ClickHouse Government is pre-configured for FIPS 140-3 level encryption utilizing OpenSSL and baseline security hardening. Deployment is initially supported via Helm charts using a pull-based process to respect the most secure of boundaries. Build guides are available to configure required resources and will be improved and automated over time.

## Security and compliance

While ClickHouse Government comes pre-configured with additional security controls, we also make the process of fulfilling security needs such as FedRAMP Moderate, FedRAMP High, IL 2, 4, 5, and 6 to obtain an Authorization to Operate (ATO), we also want to make your journey a little easier. This package is accompanied by National Institute for Standards and Technology (NIST) Risk Management Framework (RMF) documentation and NIST 800-53 control mapping. 

## Availability

ClickHouse Government on AWS will be available in private preview starting June 10. Come visit our booth at the AWS Summit in Washington, DC on June 10 and 11 to learn more or join our [waitlist](https://clickhouse.com/government) where you can ask about this offering or future cloud or bare metal deployments.
