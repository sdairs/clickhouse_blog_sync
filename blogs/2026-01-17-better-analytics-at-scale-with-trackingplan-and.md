---
title: "Better Analytics at Scale with Trackingplan and ClickHouse"
date: "2024-01-23T11:44:43.347Z"
author: "Trackingplan"
category: "User stories"
excerpt: "Read about how Trackingplan leverages ClickHouse to provide a complete testing solution for analytics at scale."
---

# Better Analytics at Scale with Trackingplan and ClickHouse

## Introduction

For many businesses, their website is a critical product for which analytics are essential in both revenue and making informed business decisions. [Trackingplan](https://www.trackingplan.com/) provides a complete testing solution for web, iOS, Android and backend analytics powered by ClickHouse.

By intercepting and sampling data sent to platforms such as Google Analytics, Segment, and MixPanel, as well as ad attributing tools for social media, Trackingplan can detect issues with marketing and product ''tracking plans'' that emerge as the result of changing requirements and library changes. By ensuring that this data is complete and consistent with historically learned examples, Trackingplan ensures that mission-critical marketing reports are precise and robustly generated. These capabilities range from simple detection of missing data streams to more complex schema inconsistencies or anomalous event detection. Users of Trackingplan can report marketing funnel statistics with confidence that they have been fully tested and are consistent across all sources.

ClickHouse forms the backbone of Trackingplans offering, as the database for storing  analytic events from their users. ClickHouse’s lightning-fast aggregations and analytical functions designed for analytics, allow data inconsistency issues to be quickly detected and rectified.

![debug_warning_tracking_plan.png](https://clickhouse.com/uploads/debug_warning_tracking_plan_e115da2dac.png)

## Migrating from DynamoDB

Trackingplan’s initial offering was based on AWS DynamoDB. This offered a simple means of getting started while data access patterns were being understood and exact query requirements were identified. While DynamoDB offers fast reads for fetching rows, its limited analytical abilities required Trackingplan to perform most processing prior to data insertion using Python-based (Pyspark) ETL pipelines. This meant any required statistics were precomputed prior to insertion, allowing Dynamo to deliver simple, fast reads.

This approach, while sufficient initially, has some obvious limitations. The computation of new statistics required the data to be reprocessed and backfilled. This lack of flexibility was compounded by Trackingplan’s ever-improving product offering, which needed to explain the causes of the issues. As more and more statistics were computed, it became apparent the full data was often required to explain a detected issue to the end user.

On realizing that an analytical database capable of serving dynamic queries on the full data was required, Trackingplan began the evaluation of alternatives.

> "We wanted to be able to answer those questions we couldn’t foresee the user would ask. We could not know in advance all of the use cases and features needed by our users and needed an analytical solution"

## Choosing ClickHouse

Before deciding on ClickHouse, Trackingplan evaluated 4 alternatives: Snowflake, BigQuery, Athena and Redshift. Snowflake and BigQuery were excluded due to their pricing being multiples of the alternatives, with Trackingplan’s continuous query workload not expected to benefit from their ability to idle or only charge for bytes scanned. While Redshift was considered, testing confirmed it to be significantly slower than ClickHouse for the sample queries. Queries in Athena were 20x slower than ClickHouse. 

**For ad hoc data analysis, Trackingplan found ClickHouse to be 20x faster than Athena.**

ClickHouse meanwhile offered unparalleled performance even on ad-hoc analytical queries for which no optimizations, e.g., Materialized views, had been applied and for which linear scans were required. Millisecond performance on optimized dashboard queries and low second-level performance on even the most complex ad-hoc GROUP BY queries, over hundreds of millions of rows, convinced Trackingplan to build the next iteration of their product on ClickHouse.

> "With ClickHouse being a fast OLAP we can answer unplanned queries. Even if not processed ahead of time, queries always work even if they take a few seconds. This ability to inspect and work with raw data is a deal breaker."

Once ClickHouse had been selected as the preferred database, Trackingplan evaluated vendors. Preferring a native ClickHouse service over a ClickHouse-based platform, with an additional preference to work with the maintainers of the technology, Trackingplan selected ClickHouse Cloud. The cost benefits of a solution that separated storage and compute provided additional compelling reasons to utilize Cloud over OSS.

## Adopting ClickHouse

The adoption of ClickHouse was made simple by its native SQL interface - a skill possessed by all of Trackingplan’s development team. This experience was made even easier by the additional specialized analytical functions offered by ClickHouse, which significantly simplify analytical queries.

While ClickHouse’s flexible querying capabilities were appreciated, Trackingplan still recognized the need to perform optimization on some queries. The pre-computation of statistics, for which Python was used with Dynamo, logically mapped to ClickHouse Materialized Views. The incremental nature of these views is particularly relevant to Trackingplan’s use case, which effectively produces time series data. By precomputing aggregation results at insert time and ensuring they were updated as new data was inserted, Trackingplan was able to accelerate specific important queries and reduce their required resource footprint. More specifically, Materialized views are used to accelerate the most common dashboard queries showing live statistics - ensuring the dashboard is highly responsive while remaining interactive.

![tracking_plan_health_summary.png](https://clickhouse.com/uploads/tracking_plan_health_summary_02f22f00eb.png)

> We can still optimize queries for use cases we can foresee, like we did with Dynamo, by precomputing statistics using materializations

Once a user needs to perform a deeper analysis of data, e.g., searching for click-through rates for a specific page, the cross-product of the materializations becomes unfeasibly large. At this point, Trackingplan relies on ClickHouse’s ad hoc query capabilities with sensible primary keys to ensure most queries still return in the millisecond range.

![tracking_plan_properties.png](https://clickhouse.com/uploads/tracking_plan_properties_646379ce54.png)

The dynamic nature of analytics data means schemas need to be flexible. To capture dynamic user-specific properties, Trackingplan exploits ClickHouse’s Map and Array types. The aggregation functions for these types allow them to answer even the most complex questions. 

## Ever increasing volumes

Trackingplan currently has around 30 Billion rows in ClickHouse. This data volume continues to grow at over 400 % per year. While current access patterns use only the last 30 days of data, a high compression rate in ClickHouse may allow Trackingplan to keep all of the raw events, unlocking potential use cases involving historical analysis in the future.

Currently, all data is stored in a single set of tables with the customer id as a component of the ordering key. This is optimized for the most common access pattern: analytics per user. This approach to multi-tenancy represents the simplest approach, with a table per customer also possible. Should customers need complete data separation at the storage layer, ClickHouse Cloud allows Trackingplan to achieve this by simply creating a dedicated service per customer.

## Tips and Tricks & Future improvements

Trackingplan recommends learning about ClickHouse ordering keys for query performance. While many other optimization techniques exist, they found this to be the most effective initial step and sufficient in most cases to get good query performance.

Upon identifying a popular query pattern by their users or a requirement for a new statistic to be exposed, Trackingplan creates a materialized view to optimize the query and reduce cluster load. Once the view has been created, data is backfilled for the previous 30 days using the views query and an `INSERT INTO SELECT`. This is possible as the raw data exists in ClickHouse.

Trackingplan leverages the scaling API of ClickHouse Cloud and its widespread presence across data centers in various geographical regions, a crucial aspect for ensuring compliance with local privacy regulations. Since their periods of high usage are predictable e.g. black friday, they scale their services prior to these occurring. Once they detect usage has returned to lower levels, the services are proactively reduced to minimize spend.

Finally, Trackingplan is excited about a number of features under development in ClickHouse Cloud. Specifically, they look forward to being able to separate compute for insertion and querying - with separate services for each, thus allowing resources to be scaled independently for these functions. 

## Learn more about Trackingplan

Fix your user data at its source, discover the truth about the data you are collecting, enforce your business rules, and fix bugs before they impact your reports and decisions with [Trackingplan](https://www.trackingplan.com/). Get your free plan and Enterprise trials [here](https://www.trackingplan.com/pricing).
