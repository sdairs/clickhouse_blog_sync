---
title: "ClickHouse achieves AWS Retail Competency"
date: "2026-06-12T21:17:44.488Z"
author: "Aditya Chidurala"
category: "Company and culture"
excerpt: "ClickHouse has achieved the AWS Retail Competency, joining a select group of AWS Partners recognized for deep expertise in helping retailers turn live operational data into real-time decisions."
---

# ClickHouse achieves AWS Retail Competency

## Summary

ClickHouse has achieved the AWS Retail Competency, joining a select group of AWS Partners recognized for deep expertise in real-time analytics for retail.


We're excited to announce that ClickHouse has achieved the **AWS Retail Competency** in the **Advanced Data Insights** category.  

The designation recognizes AWS Partners with validated technical expertise and demonstrated customer success, helping retailers consolidate data silos and turn live operational data into decisions. 

Earning it means AWS has reviewed our production architectures, our security and operational practices, and our customer outcomes, and it reflects the work we've done with some of the largest retailers, marketplaces, and commerce platforms running on AWS.


## Meeting the unique demands of retail data

An inventory position that was accurate an hour ago is wrong by lunchtime, prices and promotions have to follow demand as it moves, and a supply chain spanning thousands of stores and millions of SKUs produces change faster than any nightly batch can absorb. Personalization and retail media further tighten the window, because the signal that matters is what a shopper did 30 seconds ago. The calendar compounds all of it, with Black Friday and year-end peaks multiplying traffic at exactly the moment a slow dashboard costs the most.

The workload underneath is high-volume, high-cardinality, and high-concurrency, with freshness as a hard requirement, and that's the workload ClickHouse was built for. Columnar storage with heavy compression keeps full event history affordable, the parallel query engine returns sub-second answers under thousands of concurrent users, [ClickPipes](https://clickhouse.com/cloud/clickpipes) streams data continuously from Kafka and Amazon S3, and [compute-compute separation](https://clickhouse.com/docs/cloud/reference/warehouses) keeps ingestion from slowing the queries your merchandisers, operators, and customers depend on. On AWS, all of it runs with private networking, multi-region deployment, and AWS Marketplace billing.


---

## Get started today

Interested in seeing how ClickHouse works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-883-get-started-today-sign-up&utm_blogctaid=883)

---

## Customer success from marketplaces to fulfillment centers

[Mercado Libre](https://clickhouse.com/videos/mercado-libre-meetup), the largest e-commerce and fintech company in Latin America, runs more than 35,000 microservices serving over 15 million requests per second. Its observability events platform on ClickHouse Cloud captures 100% of traces for critical business flows like payments and logistics, ingesting roughly 90 TB of new data every day, and trace lookups that used to take 15 to 20 minutes now return in about 2 seconds. 

[Picnic](https://clickhouse.com/blog/picnic-real-time-analytics), the online grocer that describes itself as "a million tiny supermarkets, one for every customer," gives 20+ highly automated fulfillment centers shift-by-shift visibility into orders, inventory, and staffing through its real-time insights platform on ClickHouse Cloud. Analysts and floor teams build their own dashboards, with thousands of Grafana views in production and every data model managed as code in dbt. "ClickHouse is very easy to operate, very cost-effective, and scaling is really simple with ClickHouse Cloud. We're very happy with it," says Max Sumrall, Software Engineer at Picnic.

Some of the largest retail platforms on AWS run ClickHouse behind the scenes. A major live shopping marketplace ingests petabytes of event streams from Kafka through ClickPipes and serves more than half a million queries per hour at peak, with compute-compute separation keeping operator dashboards fast through Black Friday. One of the world's largest fashion retailers runs ClickHouse Cloud across two EU regions, Ireland for operational analytics and Frankfurt for financial reporting, meeting data residency requirements while isolating high-concurrency BI from continuous ingestion across its brand portfolio.

Retail intelligence providers build their products on ClickHouse, too. [Datavations](https://clickhouse.com/blog/18x-faster-15x-cheaper-datavations-clickhouse-story), which delivers market intelligence for the home improvement industry, rebuilt its pipeline on ClickHouse Cloud. "We've seen a 15x cost reduction in cloud expenses, with an 18x increase in processing speed and 5x uplift in analyst efficiency," says Jacob Lucas, Co-founder and Head of Engineering. [Rapid Delivery Analytics](https://clickhouse.com/blog/rda-tracks-real-time-cpg-performance-with-clickhouse) tracks digital shelf performance across 40+ rapid delivery apps in over 100 countries for CPG brands like PepsiCo and Unilever, ingesting more than 500 GB of raw data a day on ClickHouse Cloud on AWS. "ClickHouse Cloud is the core of our solution. It gives us the kind of capabilities and infrastructure you'd expect from a much bigger, better-known corporation, while still letting us stay lean," says co-founder and CEO Andrey Dyatlov.

E-commerce teams pick ClickHouse on measured value. [Adevinta](https://clickhouse.com/blog/serving-real-time-analytics-across-marketplaces-at-adevinta) benchmarked managed cloud databases for its seller-facing analytics dashboards and found the alternatives 2x and 6x more expensive for the workload tested, making ClickHouse Cloud the choice across its marketplaces. Minted monitors millions of real-time web performance data points on ClickHouse Cloud to keep its e-commerce experience fast. [Artly](https://clickhouse.com/blog/artly-clickhouse-barista) runs the telemetry behind its robotic barista fleet on ClickHouse, with hundreds of metrics per bot feeding drink quality and operations. And [AMP](https://clickhouse.com/blog/amp-clickhouse-oss-to-clickhouse-cloud) streams events from thousands of Shopify stores through Amazon EventBridge and Kinesis Data Firehose into ClickHouse Cloud to power merchant reporting. You'll find more in our [retail and e-commerce user stories](https://clickhouse.com/user-stories?vertical=3&cloudProvider=aws).


## Looking ahead

Retail is moving into the agentic era, where demand forecasting, dynamic pricing, and AI shopping assistants are only as good as the freshness of the data underneath them. We're continuing to invest here, from ClickPipes and Postgres CDC ingestion to the [ClickHouse MCP server](https://clickhouse.com/ai) that lets AI agents query retail data directly. If you're building retail analytics on AWS and want to move from batch reporting to real-time decision-making, we'd love to work with you.

[Get started](https://clickhouse.cloud/signUp?loc=blog-cta-footer&utm_source=clickhouse&utm_medium=web&utm_campaign=blog) with ClickHouse Cloud today and receive $300 in credits. At the end of your 30-day trial, continue with a pay-as-you-go plan, or [contact us](https://clickhouse.com/company/contact?loc=blog-cta-footer) to learn more about our volume-based discounts. Visit our [pricing page](https://clickhouse.com/pricing?loc=blog-cta-header) for details.
