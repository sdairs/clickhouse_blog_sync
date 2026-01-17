---
title: "Property Finder Optimizes Database Performance, Reduces Costs by 50% with ClickHouse on AWS"
date: "2025-07-22T18:31:27.762Z"
author: "AWS"
category: "User stories"
excerpt: "\"ClickHouse and AWS are the most trusted collaborators we have. We’ve benefited massively from our joint product roadmap\" Khaled Thabit - Director of Data Engineering, Property Finder"
---

# Property Finder Optimizes Database Performance, Reduces Costs by 50% with ClickHouse on AWS

This was originally [published by AWS](https://aws.amazon.com/solutions/case-studies/property-finder-clickhouse/). 

## Benefits

- **50%** reduction in operating costs
- **5x** improvement in database performance
- **96%** improvement in database query speed

## Overview

[Property Finder](http://propertyfinder.ae/) is a real estate classified platform that home seekers and investors use to find properties to purchase or rent. Headquartered in the United Arab Emirates, the company operates in several markets, including Bahrain, Egypt, Qatar, and Saudi Arabia. Using Property Finder, home buyers and investors can analyze a wealth of market data that it collects to make better decisions. However, its systems were decentralized across regions, which was impacting analytics performance, and its computing resources were overprovisioned. Property Finder ran a competitive proof of concept with a number of technical partners and chose a database solution operated by [AWS Partner](https://partners.amazonaws.com/partners/0018a00001mU61yAAC/ClickHouse) [ClickHouse](https://clickhouse.com/). Running on ClickHouse and Amazon Web Services (AWS), Property Finder’s website performance has improved 5 times while operational costs have been cut by 50 percent.


## About Property Finder

Property Finder is a pioneering property portal in the Middle East and North Africa (MENA) region, dedicated to shaping an inclusive future for real estate while spearheading the region’s growing tech ecosystem. At its core is a clear and powerful purpose: To change living for good in the region. Founded on the value of great ambitions, Property Finder connects millions of property seekers with thousands of real estate professionals every day. The platform offers a seamless and enriching experience, empowering both buyers and renters to make informed decisions


## Opportunity | Addressing Database Performance in Multiple Regions

Every day, Property Finder connects millions of property seekers with thousands of real estate professionals. With millions of visitors per month and 700,000 homes listed on its platform, it’s one of the most widely used property portals in the region. Data is key to Property Finder’s user experience. The website provides information to home seekers about properties and communities to help inform decisions. But it also provides rich and detailed market insights for real estate agents and investors to help them understand how their property listings are performing against their competitors and to track trends. It’s therefore essential that its valuable commercial data is stored and served securely and that its analytics service delivers insights at speed.

Property Finder’s previous solution was based on AWS, but teams were using different systems to interrogate and report on data. The result was an increasingly complicated infrastructure with increasing operational costs. Crucially, the company didn’t have a single source of truth, because data was being stored in multiple locations for processing by different teams. Property Finder decided to migrate its database operations to a central solution that could provide optimized analytics capabilities for the whole company.

:::global-blog-cta:::

The company spoke to AWS about how to go about finding a technical partner to improve its database solution. It had an urgent need to improve performance for both its internal teams and customers and wanted to reduce its costs. Based on suggestions from AWS, Property Finder identified 5 suppliers that it could potentially work with and invited them to run a proof of concept (PoC) on its data and selected workloads.


## Solution | After a Competitive Proof of Concept, a Successful Partnership and Solution

Property Finder chose ClickHouse because it provided the best mix of performance and cost savings during the PoC. One of the benefits of the PoC was that, in addition to identifying the best technology fit for its needs, the company also identified the best people fit with the ClickHouse team, both for the initial project and to help build a product roadmap. “Outside the technical PoC, it was​​ important to get feedback from the Property Finder team on what they were looking for in terms of new functions and features so that we can grow together,” says Arno van Driel, vice-president EMEA at ClickHouse. “That's the way I would describe our relationship over the past two years as a positive and ongoing dialogue.”

Central to ClickHouse’s solution was its open source, column-oriented database designed for online analytical processing on very large datasets. After the PoC, the first step was to understand both the data landscape and the level of database knowledge in Property Finder. ClickHouse initially checked in with Property Finder on a weekly basis to optimize the way the data was indexed and how it was accessed and queried. After this was done, work focused on optimizing individual use cases. Another key technical capability was the availability of ClickHouse connectors and [ClickPipes](https://clickhouse.com/cloud/clickpipes)—a data integration engine—that enable different types of company databases, such as PostgreSQL or MySQL, to connect to a central database.

The company is using some key AWS AI capabilities. With [Amazon Bedrock](https://aws.amazon.com/bedrock/), Property Finder’s data engineering teams can make sophisticated database requests in plain language, which are then translated into SQL query strings. The company is also using [Amazon SageMaker](https://aws.amazon.com/sagemaker/) to build data science models that are trained on huge amounts of data to help it predict market churn and make pricing forecasts.

The ClickHouse database runs on [Amazon Elastic Compute Cloud](https://aws.amazon.com/ec2/) (Amazon EC2) for compute power and uses [Amazon Simple Storage Service](https://aws.amazon.com/s3/) (Amazon S3) for its data lake. The company’s data is commercially highly sensitive, so it uses [AWS PrivateLink](https://aws.amazon.com/privatelink/) to establish a secure connection between the company’s virtual private clouds (VPCs) and AWS without exposing data on the public internet. The serverless extract, transform, and load service [AWS Glue](https://aws.amazon.com/glue/) is used for data transformation. The solution was deployed in multiple [AWS Regions](https://aws.amazon.com/about-aws/global-infrastructure/regions_az/) to satisfy the data residency requirements of certain countries. AWS Regions provides geographically isolated AWS data center clusters that offer redundancy and low-latency performance.


## Outcome | Operating Costs Reduced by 50%, Database Performance Increases 5x

With the ClickHouse database hosted on AWS, Property Finder now has a single source of truth. Performance has improved significantly, with responses, on average, 5 times faster than before, and with some test cases running up to 500 times faster. The company’s customers have reported an improved user experience and have submitted positive reviews about the product. Database queries that used to take 50 seconds now take just 2 seconds to run, a 96 percent improvement.

Immediately after the March 2023 migration, operating costs dropped by 30 percent, and the ClickHouse team has continued to work on the system to further improve performance and efficiency. Today, costs are just 50 percent of what they were with the previous system. “The team at ClickHouse does not stop optimizing database performance,” says Khaled Thabit, Property Finder’s director of data engineering . “We can clearly see this as we track the system performance daily on AWS."

With ClickHouse running on AWS, Thabit reports that the business can easily and seamlessly scale when demand increases, and it no longer needs to overprovision compute resources to ensure availability. All of the company’s infrastructure is hosted on AWS. “ClickHouse and AWS are the most trusted collaborators we have,” says Thabit. “We’ve benefited massively from our joint product roadmap, and there are many new features being released that are super useful for us in our day-to-day operations.”

*See how ClickHouse Cloud can power real-time analytics at scale—[try it free for 30 days](https://clickhouse.com/cloud).*
