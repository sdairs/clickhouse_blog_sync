---
title: "How QuickCheck uses ClickHouse to bring banking to the Unbanked"
date: "2022-07-11T23:23:24.540Z"
author: "Luis Rodrigues"
category: "User stories"
excerpt: "How QuickCheck uses ClickHouse to bring banking to the Unbanked"
---

# How QuickCheck uses ClickHouse to bring banking to the Unbanked

<!-- Yay, no errors, warnings, or alerts! -->

In this blog post we hear from Luis Rodrigues, the co-founder and CTO of QuickCheck, a fast-growing Fintech startup based in Lagos, Nigeria.

In Nigeria, over 60 million Nigerian adults are excluded from banking services and 100 million do not have access to credit. QuickCheck, with the mission of providing financial services to underserved consumers, leverages artificial intelligence to offer app-based neo-banking products. 

The QuickCheck mobile app has been downloaded by more than 2 million people and has processed over 4.5 million micro-credit applications. The team of 150+ people is located between Nigeria and Portugal.


## **ClickHouse for Multiple Use Cases**

QuickCheck started using ClickHouse 2 years ago for multiple use cases including financial data analysis, fraud analysis, and monitoring data. Currently, more than 50 people within the company use dashboards powered by ClickHouse for their daily tasks.

The QuickCheck application analyzes the entire history of a customer’s loans data, using daily snapshots. Hundreds of thousands of rows of data are loaded into ClickHouse daily. On top of this data we perform analysis of portfolio risk and build the financial metrics needed for portfolio analysis.

![quickcheck1.png](https://clickhouse.com/uploads/quickcheck1_bc35b189ad.png)

![quickcheck2.png](https://clickhouse.com/uploads/quickcheck2_31cc6c8054.png)

ClickHouse is also used for our operational dashboards. We aggregate data from different services into ClickHouse and use Metabase for dashboards. 

![QuickCheck_UI.webp](https://clickhouse.com/uploads/Quick_Check_UI_854836e406.webp)

Our fraud team uses ClickHouse to collect data for their scoring models. We collect tens of thousands of data points from customers’ phones and other more traditional sources. ClickHouse is used as a way to process all of these SMS messages and extract valuable information used for the scoring and fraud models. 

_I love ClickHouse because the team that manages it says_ – _it just runs, magically_, _it’s amazing_


## ClickHouse Architecture 

![quickcheck3.png](https://clickhouse.com/uploads/quickcheck3_63e0038fa7.png)

The above diagram shows QuickCheck’s current ClickHouse architecture. Data is in Postgres and gets replicated by Python into ClickHouse. Metabase is on top for the UI. Everybody writes queries in SQL. Some people use machine learning models for data science and fraud detection. They connect directly with SQLAlchemy.

What is also important to mention is that ClickHouse is a column-oriented database that doesn’t support transactions and updates/deletes are very slow. All transaction data should be kept in Postgres (or another OLTP database) and ClickHouse should be used for what it does best: OLAP queries. However, we are excited about the [transaction support](https://github.com/ClickHouse/ClickHouse/issues/22086) experiments released in [22.4](https://clickhouse.com/docs/en/whats-new/changelog/) and look forward to experimenting.


## **Instant in ClickHouse vs Forever in Postgres**

For me, what matters about ClickHouse is the sheer performance it has. You write an aggregate query across hundreds of thousands of rows and the result is there and if you want to draw a dashboard on that, it’s instant. That is basically the reason why we started using it, for dashboarding. 

We realized we had so much data in Postgres, which was taking forever to process, so we started moving it to ClickHouse. It is instant in ClickHouse vs forever in Postgres. 

If I try to do a financial analysis of the last year it’s impossible to do in Postgres, the database is going to time out, it will never finish. This happens because we have 100s of millions of rows that store the status and properties of each individual loan every day since it was granted. In ClickHouse it takes less than 5 seconds.


## **ClickHouse Features**

The main features of ClickHouse we currently use are:



* Aggregation functions (AVG, SUM, etc) across 100s of millions of rows to create dashboards
* Window and statistical and functions
* Column compression to save on disk space usage


## **Advice to other ClickHouse users**

My advice to others thinking of using ClickHouse is to just try it. If you have queries that are very slow, you should test it in ClickHouse. We are very happy with the performance and with everything. 

Visit [https://quickcheck.ng/](https://quickcheck.ng/) for more information. 
