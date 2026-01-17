---
title: "Trillabit Utilizes the Power of ClickHouse for Fast, Scalable Results Within Their Self-Service, Search-Driven Analytics Offering"
date: "2023-01-29T17:17:05.835Z"
author: " Keith Riddolls"
category: "User stories"
excerpt: "We welcome Trillabit as a guest to our blog. Read on to hear from Keith Riddolls (CEO/Founder) to find out why they chose ClickHouse over Apache Solr and Snowflake to power their reporting and business intelligence platform."
---

# Trillabit Utilizes the Power of ClickHouse for Fast, Scalable Results Within Their Self-Service, Search-Driven Analytics Offering

_We welcome Trillabit as a guest to our blog. Read on to hear from Keith Riddolls (CEO/Founder) to find out why they chose ClickHouse over Apache Solr and Snowflake to power their reporting and business intelligence platform._

TrillaBit Quick Intelligence is a dynamic SaaS platform for reporting and business intelligence, utilizing the power of ClickHouse for fast scalable results. 

Quick Intelligence isn’t just a visualization tool, but a full end-to-end, enterprise-grade platform. Handling multi-tenancy and security, while allowing for dynamic data exploration on big data. Embedded or standalone, Quick Intelligence can integrate with  ClickHouse where-ever it is deployed.  

## Working with ClickHouse

In the beginning, TrillaBit started with Apache Solr. Why not?! TrillaBit is a search-driven analytics platform, so why not use a search-driven data backend? Solr is capable of some levels of data aggregation, the models are dynamic and the indexing is ideal for search purposes.

However, we soon ran into a number of challenges. Solr, being a key-value store is more suited to search than it is to high-volume non-linear aggregation or data compression for performance. Its query language isn’t as mature as SQL and it doesn’t really handle joins. 

When implementing real company data from many sources, we found more flexibility was required in different scenarios. There’s the ‘get it up and running with as little effort and cost as possible’ i.e. use the data where it is, how it is. Then there’s the ‘let’s get this done right’ i.e. build out the data warehouse with star schema models and dimension fact tables and move data to these structures. These scenarios require more of a data warehouse solution than a search engine. 

### The Goal

The goal was to start with something that could be managed at a low cost and could be implemented within our environment for hands-on experience and understanding. We wanted to understand the technology in some detail before handing it off to a managed service. 


Snowflake being the popular contender was simply too expensive and didn’t allow for that full on-prem implementation. See: [Why is Snowflake so expensive? ](https://blog.devgenius.io/why-is-snowflake-so-expensive-92b67203945)

ClickHouse was an excellent alternative, with fast [performance](https://clickhouse.com/docs/en/about-us/performance/#:~:text=Under%20the%20same%20conditions%2C%20ClickHouse,of%20100%20queries%20per%20second.) and low cost using the [open source community version](https://github.com/ClickHouse/ClickHouse). Setting up ClickHouse on-premise / self-managed (AWS), allowed us to get fast, hands-on experience to best understand how it fit into our environment.  

Here are some of the preferred features we found while digging in: 

**Integration Engines**

ClickHouse allows ways to make your life so much easier when it comes to data ingestion. The table engine features were fantastic for connecting to data where it sat in different stores and forms. 

The [table engines for integrations](https://clickhouse.com/docs/en/engines/table-engines/integrations/) are great features that allow for direct connections to other relational stores like MySQL or Postgres. Simply connect and run! The TrillaBit product runs on metadata that is managed in relational stores. The ability to connect to this without moving data allows for lookups, joins, and views within ClickHouse itself and has huge benefits for speed of integration.

TrillaBit has streaming endpoints for clients to post fast network and IoT streaming data. Behind that, is Kafka. The [Kafka table engine](https://clickhouse.com/docs/en/integrations/kafka/kafka-table-engine) worked great for connecting and using data through ClickHouse efficiently. 

Although currently used to a lesser extent by TrillaBit, ClickHouse does allow for direct S3 integration through the [S3 table engine](https://clickhouse.com/docs/en/engines/table-engines/integrations/s3/) for loading & offloading.

**Data Management Engines**

When storing and managing data in ClickHouse the [MergeTree family](https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/) has many useful features. TrillaBit primarily uses the [ReplacingMergeTree](https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/replacingmergetree) to remove duplicates based on a sort key. We often receive delta changes on existing records, and by replacing them based on the primary key, we can easily retain the currently accurate state without duplication and with minimal code.  The [AggregatingMergeTree](https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/aggregatingmergetree) reduces coding and management of incremental aggregation on constantly flowing data, again reducing custom coding and processing.

**AirByte and JSON**

For some client integrations where the movement of data is required, TrillaBit will utilize Airbyte. For fast POCs, data is ingested in raw JSON format. Then through views, the JSON structure is read and flipped to a table structure with a simple query like this:


```
SELECT 	toInt64(JSON_VALUE(_airbyte_data,'$.id')) AS location_id,
JSON_VALUE(_airbyte_data,'$.name') AS location_name,
JSON_VALUE(_airbyte_data,'$.address') AS address,
JSON_VALUE(_airbyte_data,'$.city') AS city,
JSON_VALUE(_airbyte_data,'$.state') AS state,
JSON_VALUE(_airbyte_data,'$.zip') AS zip,
JSON_VALUE(_airbyte_data,'$.country') AS country,
toDecimal64(nullIf(lower(JSON_VALUE(_airbyte_data,'$.longitude')),'null'),12) AS longitude,
toDecimal64(nullIf(lower(JSON_VALUE(_airbyte_data,'$.latitude')),'null'),12) AS latitude,
FROM mydb._airbyte_raw_stg_Location;
```

This feature, like others, has reduced our time to implement and experiment by days if not weeks! 

The final thing to note about working with ClickHouse is the [great community contributing to knowledge](https://www.meetup.com/pro/clickhouse/). The amount of information found on ClickHouse from its community, cloud supporters, and ClickHouse Inc is a valuable resource in and of itself.  

With ClickHouse and this [knowledge base](https://clickhouse.com/docs/en/home/), TrillaBit has been able to get everything up and running quickly, starting with  [open-source](https://github.com/ClickHouse/ClickHouse).   

**ClickHouse Cloud**

As TrillaBit grows, we are now moving to ClickHouse Cloud. Offloading the cluster management to the cloud allows us to focus on our product. ClickHouse Cloud also has an excellent security profile with PCI and SOC II compliance giving clients further peace of mind. See the [ClickHouse Trust Center](https://trust.clickhouse.com/).   

## Exploring your ClickHouse data with Quick Intelligence by TrillaBit

TrillaBit is solving the BI Assembly line problem in a cost-effective way. Quick Intelligence isn’t just a tool, but an end-to-end platform that allows users to ask a question in a search bar and get immediate visual answers. 

Utilizing ClickHouse because of its incredible performance at scale, it finds the data and instantly graphs it for you. Once you visualize the data you can easily drill down into the area of interest to uncover further insights and expose record-level detail at any point. 

A metadata-driven system allows business users to explore data in their own way, asking new questions and getting immediate answers in seconds. 

![TrillaBit_quickintelligence.png](https://clickhouse.com/uploads/Trilla_Bit_quickintelligence_67f118b1a1.png)

**Save and Share**

When users find something interesting and valuable in their data, they often want to save and share it with others, either inside or outside the tool. There are many ways to do this. Creating dashboards on the fly and sharing them with individuals or groups is one way. With Quick Intelligence, this is as simple as pinning visualizations to a dashboard or creating a new one in seconds. 

![Trillabit_securityvuln.png](https://clickhouse.com/uploads/Trillabit_securityvuln_d90e8e4b60.png)
![Trillabit_sales.png](https://clickhouse.com/uploads/Trillabit_sales_b3237eec74.png)

Users can also export their KPIs as images for PowerPoint presentations, word or email. You can also drill right down to the underlying raw data and export it to Excel to share with a colleague.

**To Embed or not to Embed**
Companies that want to use this functionality as their own have the option to embed Quick Intelligence into their own product. They can skin it to look like their own brand or to look like any of their client’s brands at the account level.
Other companies who want to use this internally are able to have all of this functionality in a standalone UI.

Additionally Standalone and embedded are available in a single implementation. For the best of both worlds. 

![Trillabit_dark1.png](https://clickhouse.com/uploads/Trillabit_dark1_65e97b9edc.png)
![Trillabit_dark2.png](https://clickhouse.com/uploads/Trillabit_dark2_d315e0c44e.png)

**Security and scale**
TrillaBit Quick Intelligence utilizes ABAC policy control.  It allows for multi-tenant capabilities and can secure data for many departments. 

A large part of the backend scalability comes from the efficient performance of ClickHouse. Whether it's your ClickHouse environment, ClickHouse Cloud or having TrillaBit manage everything, the product is versatile and able to handle several configurations.

TrillaBit scales to IoT and network-level traffic volumes of data, easily handling trillions of rows while providing real-time analytics.

## Getting Started with TrillaBit on ClickHouse

TrillaBit is an enterprise-grade platform. If you have ClickHouse already, TrillaBit can connect to it and you’ll be up and running in no time! 

TrillaBit is metadata-driven, so the only thing required is the data. 

If you’re looking to run your own data warehouse in ClickHouse and have TrillaBit run on that, just let us know. We’ll integrate with your ClickHouse deployment and guide you through the whole process.

If you want to be completely hands-off, TrillaBit can handle the end-to-end process for you. Your business users or clients will be able to just start exploring on their own and gathering insights. 

Please feel free to reach out: [Contactus@Trillabit.com](mailto:Contactus@Trillabit.com)

