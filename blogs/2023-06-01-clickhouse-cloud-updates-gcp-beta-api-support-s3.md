---
title: "ClickHouse Cloud Updates: GCP Beta, API Support, S3 IAM roles, and more"
date: "2023-06-01T10:48:47.300Z"
author: "ClickHouse"
category: "Product"
excerpt: "It’s the end of May, and that means another newsletter from the ClickHouse team. This month we have chosen to focus on highlighting some of the exciting features that have been added to ClickHouse Cloud recently. At the bottom of the email are some upcomi"
---

# ClickHouse Cloud Updates: GCP Beta, API Support, S3 IAM roles, and more

It’s the end of May, and that means another newsletter from the ClickHouse team. This month we have chosen to focus on highlighting some of the exciting features that have been added to ClickHouse Cloud recently. At the bottom of the email are some upcoming events and a reading list. 

In short, it’s been a busy few months improving the ClickHouse Cloud service. To experience these improvements, log into your [cloud account](https://clickhouse.cloud/signIn?loc=blog-may-nl). If you aren’t yet using ClickHouse Cloud, then [start a free trial here](https://clickhouse.cloud/signUp?loc=blog-may-nl).

For descriptions of key improvements, read on. And don’t forget that we are hosting a [release call](/company/events/v23-5-release-webinar) next week highlighting all the new features in ClickHouse 23.5.

## ClickHouse Cloud Updates

### GCP Available in Public Beta

ClickHouse Cloud is now available on GCP in public beta, giving you choice and flexibility to run your analytics workloads in your preferred Cloud Service Provider. You can read more about what is included with the release [here](/blog/clickhouse-cloud-on-gcp-available-in-public-beta). We are working towards GA, which will also bring capabilities like Private Service Connect and GCP Marketplace support. 

![01-add-gcp-service.gif](https://clickhouse.com/uploads/01_add_gcp_service_7651ee4f24.gif)

### API Support for ClickHouse Cloud

We’ve recently released [API support](/blog/using-the-new-clickhouse-cloud-api-to-automate-deployments) for ClickHouse Cloud that lets you manage services programmatically. With the new Cloud API, you can seamlessly integrate managing services in your existing CI/CD pipeline. Refer to the [docs page](https://clickhouse.com/docs/en/cloud/manage/openapi) for instructions to get set up. The Terraform provider is coming soon!

![02-api.png](https://clickhouse.com/uploads/02_api_459ea22b43.png)

### S3 Access Using IAM Roles

You can now leverage IAM roles to securely access your private Amazon Simple Storage Service (S3) buckets. This feature is not currently self-service and can be enabled via a [support](https://clickhouse.cloud/signIn?loc=blog-may-nl) ticket. For more information, refer to the documentation [here](https://clickhouse.com/docs/en/cloud/manage/security/secure-s3). 

### SQL Console Improvements

SQL console gained support for materialized views and a new Heatmap chart type, among many other improvements.

![03-waterfall.png](https://clickhouse.com/uploads/03_waterfall_3dcadc14fe.png)

### Advanced Metrics Dashboard

If you need more visibility into your service health, check out the advanced dashboard (currently in beta) to view CPU usage, queries executed per second, current running queries, reads from disk and other infrastructure metrics. This can be accessed from the Metrics dashboard in the Cloud console.

![04-dashboard.png](https://clickhouse.com/uploads/04_dashboard_3088f6c7b4.png)

### Tracing Support in ClickHouse Grafana Datasource

ClickHouse Grafana datasource now supports visualization of traces. Read [this blog](/blog/storing-traces-and-spans-open-telemetry-in-clickhouse) on how to build trace monitoring with ClickHouse and Grafana. 

![05-tracing.jpg](https://clickhouse.com/uploads/05_tracing_2071c2bb9a.jpg)

### Additional Integrations

The new [integrations documentation page](https://clickhouse.com/docs/en/integrations) now lists over 75 integrations for ClickHouse.

* [dbt integration](https://clickhouse.com/docs/en/integrations/dbt) has been greatly improved. Read this [blog](/blog/clickhouse-dbt-project-introduction-and-webinar) for details. 
* [Metabase integration](https://clickhouse.com/docs/en/integrations/metabase) is now generally available. Read this [blog](/blog/metabase-clickhouse-plugin-ga-release) for details.
* [Kafka Connect](https://clickhouse.com/docs/en/integrations/kafka) sink has been tested and certified to work with Amazon MSK.

### Advanced Scaling

We have made significant improvements in service scaling policies and scaling controls, to support an even broader array of workloads. 

* **Horizontal scaling**. Workloads that require more parallelization can now be configured with any number of additional replicas (please contact [support](https://clickhouse.cloud/support) to set it up).
* **Higher vertical scale.** You can request more memory per replica beyond the self-service limit in the console (please contact [support](https://clickhouse.cloud/support) to set it up).
* **CPU based autoscaling.** CPU-bound workloads can now benefit from additional triggers for autoscaling policies (please contact [support](https://clickhouse.cloud/support) to set it up).
* **Idling interval control**. You can now configure the idling intervals per service, in addition to other idling configuration options.

### Performance and Reliability

We have made numerous performance optimizations and reliability improvements in the past months. Some examples include:

* Backups now run orders of magnitude faster
* Cold read latency has been optimized via advanced techniques like S3 prefetching
* ClickHouse [“lightweight deletes”](https://clickhouse.com/docs/en/guides/developer/lightweght-delete#:~:text=The%20idea%20behind%20Lightweight%20Delete,only%20later%20by%20subsequent%20merges.) are now production-ready

### Dedicated Services (Coming Soon)

We are introducing single-tenant dedicated services for the most mission-critical applications that require advanced levels of isolation, security, and performance consistency. If you are interested, review the details on the [pricing page](/pricing) and [contact](/company/contact) us to get access to it early!

![06-pricing.png](https://clickhouse.com/uploads/06_pricing_d64641ce5f.png)
For a detailed list of all improvements, please refer to your [changelog](https://clickhouse.com/docs/en/whats-new/changelog/cloud).

To experience these improvements, [log into your cloud account](https://clickhouse.cloud/signIn). If you aren’t yet using ClickHouse Cloud then [start a free trial](https://clickhouse.cloud/signUp?loc=blog-may-nl) 

## Upcoming Events

**ClickHouse v23.5 Release Webinar** \
June 8 @ 9 AM PDT / 6 PM CEST \
Register [here](/company/events/v23-5-release-webinar?loc=blog-may-nl).

**ClickHouse Meetup in Bangalore** \
Wednesday, June 7 @ 6:30 PM IST \
Register [here](https://www.meetup.com/clickhouse-bangalore-user-group/events/293740066).

**ClickHouse Meetup in San Francisco** \
Wednesday, June 7 @ 7 PM PDT \
Register [here](https://www.meetup.com/clickhouse-silicon-valley-meetup-group/events/293426725).

**ClickHouse Fundamentals** \
June 14 & 15 @ 8 AM EDT / 2 PM CEST \
Register [here](/company/events/clickhouse-workshop?loc=blog-may-nl).

**ClickHouse Cloud Onboarding** \
June 22 @ 6 AM PDT / 9 AM EDT / 3 PM CEST \
Register [here](/company/events/clickhouse-workshop?loc=blog-may-nl).


## Reading List

Some of our favorite reads that you may have missed include:

1. **Vector Search with ClickHouse** - [Part 1](/blog/vector-search-clickhouse-p1) and [Part 2](/blog/vector-search-clickhouse-p2) - Over the past year, Large Language Models (LLMs) along with products like ChatGPT have captured the world's imagination and have been driving a new wave of functionality built on top of them. The concept of vectors and vector search is core to powering features like recommendations, question answering, image / video search, and much more.
2. [ClickHouse: A Blazingly Fast DBMS with Full SQL Join Support - Under the Hood - Part 3](/blog/clickhouse-fully-supports-joins-part3) - We’ll continue the exploration of the ClickHouse join algorithms in this post and describe the two algorithms from the chart above that are based on external sorting: Full sorting merge join, Partial merge join. Both algorithms are non-memory bound and use a join strategy that requires the joined data to first be sorted in order of the join keys before join matches can be identified.
3. [ClickHouse: A Blazingly Fast DBMS with Full SQL Join Support - Under the Hood - Part 3](/blog/clickhouse-fully-supports-joins-part3) - We’ll continue the exploration of the ClickHouse join algorithms in this post and describe the two algorithms from the chart above that are based on external sorting: Full sorting merge join, Partial merge join. Both algorithms are non-memory bound and use a join strategy that requires the joined data to first be sorted in order of the join keys before join matches can be identified.
4. [OONI Powers its Measurement of Internet Censorship with ClickHouse](/blog/ooni-analyzes-internet-censorship-data-with-clickhouse) - The Open Observatory of Network Interference (OONI) is a non-profit free software project that empowers decentralized efforts in documenting internet censorship worldwide. OONI provides free software tools for users to test their internet connection quality, detect censorship, and measure network interference. These tests can reveal blocked or restricted websites, apps, or services and help identify technical censorship methods. OONI uses ClickHouse for handling large volumes of data, as its data storage and analytics engine.
5. [Adding Real Time Analytics to a Supabase Application With ClickHouse](/blog/adding-real-time-analytics-to-a-supabase-application) - At ClickHouse, we are often asked how ClickHouse compares to Postgres and for what workloads it should be used. With our friends at Supabase introducing Foreign Data Wrappers (FDW) for their Postgres offering, we decided to use the opportunity to revisit this topic with a webinar early last week. As well as explaining the differences between an OLTP database, such as Postgres, and an OLAP database, such as ClickHouse, we explored when you should use each for an application. And what better way to convey these ideas than with a demo that uses both capabilities?
6. [Optimizing usage-based pricing for infrastructure SaaS](https://medium.com/@tbragin/optimizing-usage-based-pricing-for-infrastructure-saas-83b6cec92d49) - Are you building a SaaS offering and at the stage of determining pricing? Or are you interested in the approach that we took to build out our own pricing model for ClickHouse Cloud? Tanya Bragin, ClickHouse VP of Product, shares her learnings and tips-and-tricks in this post.

Thank you for reading! 

The ClickHouse Team