---
title: "Modeling Machine Learning Data in OLAP databases"
date: "2024-08-08T09:29:52.130Z"
author: "Dale McDiarmid"
category: "Engineering"
excerpt: "Learn how to model machine learning data in OLAP databases to accelerate your pipelines and enable the fast building of features over potentially billions of rows."
---

# Modeling Machine Learning Data in OLAP databases

In this article, we explore the world of MLOps and how data in OLAP databases can be modeled and transformed to allow it to act as an efficient feature store for training ML models. While the lessons shared are applicable to a range of OLAP systems, we will use ClickHouse as an example to demonstrate these techniques - for no reason other than we know it well!

The approaches discussed in this blog are used by [existing ClickHouse users](https://clickhouse.com/blog/transforming-ad-tech-how-cognitiv-uses-clickhouse-to-build-better-machine-learning-models), who we thank for sharing their techniques, as well as out of the box feature stores.

We focus on using an ClickHouse as a data source, offline store, and transformation engine. These components of a feature store are fundamental to delivering data efficiently and correctly to model training. While most out-of-the-box feature stores provide abstractions, we peel back the layers and describe how data can be modeled efficiently to build and serve features. For users looking to build their own feature store, or just curious as to the techniques existing stores use, read on.

## Why ClickHouse?

We have explored what a feature store is [in previous blog posts](https://clickhouse.com/blog/powering-featurestores-with-clickhouse) and recommend users are familiar with the concept before diving into this one. In its simplest form, a feature store is a centralized repository for storing and managing data that will be used to train ML models, aiming to improve collaboration and reusability and reduce model iteration time. 

As a real-time data warehouse, ClickHouse can fulfill two primary components of a feature store beyond simply providing a datasource.

![feature_store_clickhouse.png](https://clickhouse.com/uploads/feature_store_clickhouse_baabeb2e00.png)

1. **Transformation Engine**: ClickHouse utilizes SQL for declaring data transformations, optimized by its analytical and statistical functions. It supports querying data from various sources, such as Parquet, Postgres, and MySQL, and performs aggregations over petabytes of data. Materialized views allow data transformations at insert time. Additionally, ClickHouse can be used in Python via chDB for transforming large data frames.
2. **Offline Store**: ClickHouse can persist query results through `INSERT INTO SELECT` statements, automatically generating table schemas. It supports efficient data iteration and scaling, with features often represented in tables with timestamps for point-in-time queries. ClickHouse’s sparse indices and `ASOF LEFT JOIN` clause facilitate fast filtering and feature selection, optimizing data preparation for training pipelines. This work is parallelized and executed across a cluster, enabling the offline store to scale to petabytes while keeping the feature store lightweight.

In this post, we show how data can be modeled and managed in ClickHouse to perform these roles.

## High-level steps

When using ClickHouse as the basis for your offline feature store, we think of the steps to train a model as consisting of the following:

1. **Exploration** - Familiarize yourself with source data in ClickHouse with SQL queries.

2. **Identify the data subset and features** - Identify the possible features, their respective entities, and the subset of data needed to produce them. We refer to the subset from this step as the "feature subset."

3. **Creating Features** - Create the SQL queries required to generate the features.

4. **Generating model data** - Combine the features appropriately to produce a set of feature vectors, usually achieved using an ASOF JOIN on a common key and timestamp proximity.

5. **Generating test and training sets** - Split the "feature subset" into a test and training set (and possibly validation).

6. **Train model** - Train model(s) using the training data, possibly with different algorithms.

7. **Model selection & tuning** - Evaluate models against the validation set, choose the best model, and fine-tune hyperparameters.

8. **Model evaluation** - Evaluate the final model against the test set. If performance is sufficient, stop; otherwise, return to 2.

We concern ourselves with steps (1) to (5) as these are ClickHouse-specific. One of the key properties of the above process is that it is highly iterative. Steps (3) and (4) could be loosely referred to as "Feature engineering" and something that typically consumes more time than choosing the model and refining the hyperparameters. Optimizing this process and ensuring ClickHouse is used as efficiently as possible can, therefore, deliver significant time and cost savings.

We explore each of these steps below and propose a flexible approach that optimally leverages ClickHouse features, allowing users to iterate efficiently.

## Dataset & Example

For our example, we use the following web analytics dataset, described [here](https://clickhouse.com/docs/en/getting-started/example-datasets/metrica). This dataset consists of 100m rows, with an event representing a request to a specific URL. The ability to train machine learning models on web analytics data in ClickHouse is a common use case we see amongst users<sub><a href="https://clickhouse.com/blog/transforming-ad-tech-how-cognitiv-uses-clickhouse-to-build-better-machine-learning-models">[1]</a><a href="https://clickhouse.com/blog/adgreetz-processes-millions-of-daily-ad-impressions">[2]</a></sub>.

Due to its size, the following table has been truncated to columns we will use. See [here](https://pastila.nl/?00acf5da/2295705307eb4090c33cb5f0f5b8d472#kSJRFJM6RcULiQUo90npfA==) for the full schema.

<pre style="font-size: 14px;"><code class="hljs language-sql"><span class="hljs-keyword">CREATE</span> <span class="hljs-keyword">TABLE</span> default.web_events
(
   `EventTime` DateTime,
   `UserID` UInt64,
   `URL` String,
   `UserAgent` UInt8,
   `RefererCategoryID` UInt16,
   `URLCategoryID` UInt16,
   `FetchTiming` UInt32,
   `ClientIP` UInt32,
   `IsNotBounce` UInt8,
   <span class="hljs-comment">-- many more columns...</span>
)
ENGINE <span class="hljs-operator">=</span> MergeTree
<span class="hljs-keyword">PARTITION</span> <span class="hljs-keyword">BY</span> toYYYYMM(EventDate)
<span class="hljs-keyword">ORDER</span> <span class="hljs-keyword">BY</span> (CounterID, EventDate, intHash32(UserID))
</code></pre>

To illustrate the modeling steps, let's suppose we wish to use this dataset to build a model that predicts whether a user will bounce when a request arrives. If we consider the above source data, this is denoted by the column `IsNotBounce.` This represents our target class or label.

<blockquote style="font-size: 14px;">
<p>We aren't going to actually build this model and provide the Python code, rather focusing on the data modeling process. For this reason, our choice of features is illustrative only.</p>
</blockquote>

## Step 1 - Exploration

Exploring and understanding the source data requires users to become familiar with ClickHouse SQL. We recommend users familiarize themselves with ClickHouse's wide range of [analytical functions](https://clickhouse.com/docs/en/sql-reference/functions) during this step. Once familiar with the data, we can begin identifying the features for our model and the subset of the data required to produce them.

## Step 2 - Features and subsets

To predict whether a visit will bounce, our model will require a training set where each data point contains appropriate features assembled into a feature vector. Typically, these features will be based on a subset of the data.

We've explored the concept of features and feature vectors in other blogs and how they loosely correlate to a column and row of a **result set**, respectively. Importantly, they need to be available at training and request time.

![features.png](https://clickhouse.com/uploads/features_7d40dbf1cd.png)

<blockquote style="font-size: 14px;">
<p>Note we emphasized "result set" above. A feature vector is rarely just a row from a table with the features of a subset of the columns. Often, a complex query must be issued to compute the feature from an aggregation or transformation.</p>
</blockquote>

### Identifying features

Before identifying features, we should be aware of two of the key properties that will influence our modeling process:

* **Association with entities** - Features are typically associated with an `entity` with which they are associated or "keyed". For our problem, the features we think might be useful in making a prediction might be a mixture of user or domain-based. A user-based feature would be request-specific, e.g., the user's age, client IP, or user agent. A domain feature would be associated with the page visited e.g. `number of visits per year`.

    Associating features with an instance of an entity requires the entity to have a key or identifier. In our case we need an identifier for the user and a domain value. These are available from the `UserID` and `URL` columns, respectively. The domain can be extracted from the URL using the domain function in ClickHouse, i.e., `domain(URL)`.

* **Dynamic & complex** - While certain features remain relatively static, e.g., the user's age, others, such as the client IP, will exhibit changes over time. In such cases, we need to access the feature’s value as it existed at a specific timestamp. This is key for creating point-in-time correct training sets.

    While some features will likely be simple, e.g., whether the device is mobile or the client IP, other more complicated features require aggregate statistics, which change over time - and this is where ClickHouse excels!

### Example features

For example, suppose we consider the following features to be useful in predicting whether a website visit will bounce. All of our features are associated with a timestamp as they are dynamic and change over time.

* **User-agent of the visit** -  Associated with the user entity and available in the column `UserAgent`.
* **Category of the referrer** - (e.g., search engine, social media, direct). A user feature available through the column `RefererCategoryID`.
* **Number of domains visited per hour** - at the time the user made the request. Requires a `GROUP BY` to compute this user feature.
* **Number of unique IPs visiting the domain per hour** - Domain feature requiring a `GROUP BY`.
* **Category of the page** - User feature available through the column `URLCategoryID`.
* **Average request time for the domain per hour** - Requires a `GROUP BY` to compute this from the `FetchTiming` column.

<blockquote style="font-size: 14px;">
<p>These features might not be ideal and illustrative only. Linking many of these features to the user entity is somewhat simplistic. For instance, some features would be more accurately associated with the request or session entity.</p>
</blockquote>

### Feature subsets

Once we have an idea of the features we will use, we can identify the required subset of the data needed to build them. This step is optional as sometimes users wish to use the whole data, or the data isn't large and complex enough to warrant this step.

When applied, we often see users creating tables for their model data - we refer to these as the "feature subset". These consist of:

* The entity values for each feature vector.
* A timestamp of the event if it exists.
* Class label.
* The columns needed to produce the planned features. Users may wish to add other columns that they consider useful in future iterations.

This approach provides several advantages:

* Allows the data to be ordered and optimized for future accesses. Typically, the model data will be read and filtered differently than the source data. These tables can also generate features faster than the source data when producing a final training set.
* A subset or transformed set of data may be required for the model. Identifying, filtering, and transforming this subset may be an expensive query. By inserting the data into an intermediate model table, this query only has to be executed once. Subsequent feature generation and model training runs can thus obtain the data efficiently from this table.

    We can use this step to de-duplicate any data. While the raw data might not contain duplicates, the resulting subset may if we extract a subset of the columns for features.

Suppose for our model we create an intermediate table `predict_bounce_subset`. This table needs the `EventTime`, the label `IsNotBounce`, and the entity keys `Domain` and `UserID`. Additionally, we include the simple feature columns `UserAgent`, `RefererCategoryID` , and `URLCategoryID`, as well as those needed to produce our aggregate features - `FetchTiming` and `ClientIP`.

<pre style="font-size: 14px;"><code class="hljs language-sql"><span class="hljs-keyword">CREATE</span> <span class="hljs-keyword">TABLE</span> predict_bounce_subset
(
  EventTime DateTime64,
  UserID UInt64,
  Domain String,
  UserAgent UInt8,
  RefererCategoryID UInt16,
  URLCategoryID UInt16,
  FetchTiming UInt32,
  ClientIP UInt32,
  IsNotBounce UInt8
)
ENGINE <span class="hljs-operator">=</span> ReplacingMergeTree
<span class="hljs-keyword">ORDER</span> <span class="hljs-keyword">BY</span> (EventTime, Domain, UserID, UserAgent, RefererCategoryID, URLCategoryID, FetchTiming, ClientIP, IsNotBounce)
<span class="hljs-keyword">PRIMARY</span> KEY (EventTime, Domain, UserID)
</code></pre>

We use a [ReplacingMergeTree](https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/replacingmergetree) as our table engine. This engine de-duplicates rows that have the same values in the ordering key columns. This is performed [asynchronously in the background at merge tree](), although we can ensure we don't receive duplicates at query time using the [`FINAL` modifier](https://clickhouse.com/docs/en/sql-reference/statements/select/from#final-modifier). This approach to deduplication tends to be more resource efficient than the alternative in this scenario - using a `GROUP BY` of the columns we wish to de-duplicate data by at insert time below. Above, we assume all columns should be used to identify unique rows. It is possible to have events with the same `EventTime`, `UserID`, `Domain`, e.g. multiple requests made when visiting a domain with different `FetchTiming` values.

Further details on the [ReplacingMergeTree](https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/replacingmergetree) can be found here.

<blockquote style="font-size: 14px;">
<p>As an optimization, we only load a subset of the ordering keys into the primary key (held in memory) via the <code>PRIMARY KEY</code> clause. By default, all columns in the <code>ORDER BY</code> are loaded. In this case, we will likely only want to query by the <code>EventTime</code>, <code>Domain</code>, and <code>UserID</code>.</p>
</blockquote>

Suppose we wish to only train our bounce prediction model on events not associated with bots - identified by `Robotness=0`. We also will require a `Domain` and `UserID` value.

We can populate our `predict_bounce_subset` table using an `INSERT INTO SELECT`, reading the rows from `web_events` and applying filters that reduce our data size to 42m rows.

<pre style="font-size: 14px;"><code class="hljs language-sql"><span class="hljs-keyword">INSERT</span> <span class="hljs-keyword">INTO</span> predict_bounce_subset <span class="hljs-keyword">SELECT</span>
	EventTime,
	UserID,
	domain(URL) <span class="hljs-keyword">AS</span> Domain,
	UserAgent,
	RefererCategoryID,
	URLCategoryID,
	FetchTiming,
	ClientIP,
	IsNotBounce
<span class="hljs-keyword">FROM</span> web_events
<span class="hljs-keyword">WHERE</span> Robotness <span class="hljs-operator">=</span> <span class="hljs-number">0</span> <span class="hljs-keyword">AND</span> Domain <span class="hljs-operator">!=</span> <span class="hljs-string">''</span> <span class="hljs-keyword">AND</span> UserID <span class="hljs-operator">!=</span> <span class="hljs-number">0</span>

<span class="hljs-number">0</span> <span class="hljs-keyword">rows</span> <span class="hljs-keyword">in</span> set. Elapsed: <span class="hljs-number">7.886</span> sec. Processed <span class="hljs-number">99.98</span> million <span class="hljs-keyword">rows</span>, <span class="hljs-number">12.62</span> GB (<span class="hljs-number">12.68</span> million <span class="hljs-keyword">rows</span><span class="hljs-operator">/</span>s., <span class="hljs-number">1.60</span> GB<span class="hljs-operator">/</span>s.)

<span class="hljs-keyword">SELECT</span> formatReadableQuantity(<span class="hljs-built_in">count</span>()) <span class="hljs-keyword">AS</span> count
<span class="hljs-keyword">FROM</span> predict_bounce_subset <span class="hljs-keyword">FINAL</span>

┌─count─────────┐
│ <span class="hljs-number">42.89</span> million │
└───────────────┘

<span class="hljs-number">1</span> <span class="hljs-type">row</span> <span class="hljs-keyword">in</span> set. Elapsed: <span class="hljs-number">0.003</span> sec.
</code></pre>

<blockquote style="font-size: 14px;">
<p>Note the use of the <code>FINAL</code> clause above to ensure we only count unique rows.</p>
</blockquote>

### Updating feature subsets

While some subsets of data are static, others will be subject to change as new events arrive in the source table. Often, users, therefore, need to keep subsets up-to-date. While this can be achieved with scheduled queries that rebuild the tables (e.g., using dbt), ClickHouse (incremental) Materialized views can be used to maintain these.

Materialized views allow users to shift the cost of computation from query time to insert time. A ClickHouse materialized view is just a trigger that runs a query on blocks of data as they are inserted into a table e.g., the `web_events` table. The results of this query are then inserted into a second "target" table - the subset table in our case. Should more rows be inserted, results will again be sent to the target table. This merged result is the equivalent of running the query over all of the original data.

![feature_store_mv.png](https://clickhouse.com/uploads/feature_store_mv_7b51b97cf9.png)

A materialized which maintains our `predict_bounce_subset` is shown below:

<pre style="font-size: 14px;"><code class="hljs language-sql"><span class="hljs-keyword">CREATE</span> MATERIALIZED <span class="hljs-keyword">VIEW</span> predict_bounce_subset_mv <span class="hljs-keyword">TO</span> predict_bounce_subset <span class="hljs-keyword">AS</span>
<span class="hljs-keyword">SELECT</span>
   EventTime,
   UserID,
   domain(URL) <span class="hljs-keyword">AS</span> Domain,
   UserAgent,
   RefererCategoryID,
   URLCategoryID,
   FetchTiming,
   ClientIP,
   IsNotBounce
<span class="hljs-keyword">FROM</span> web_events
<span class="hljs-keyword">WHERE</span> Robotness <span class="hljs-operator">=</span> <span class="hljs-number">0</span> <span class="hljs-keyword">AND</span> Domain <span class="hljs-operator">!=</span> <span class="hljs-string">''</span> <span class="hljs-keyword">AND</span> UserID <span class="hljs-operator">!=</span> <span class="hljs-number">0</span>
</code></pre>


This is a simple example, and we recommend that users learn more about the power of materialized views [here](https://clickhouse.com/docs/en/materialized-view). For the subsequent steps, we assume we will use the model table `predict_bounce_subset`.

## Step 3 - Creating Features

For model training, we'll need to assemble our planned features into a set of feature vectors with the label `IsNotBounce` i.e.

![feature.png](https://clickhouse.com/uploads/feature_9c3c5fe592.png)

Note how we assemble our feature vector from features from multiple entities. In many cases we are looking for the feature value at the closest point in time from another entity.

An experienced SQL developer familiar with ClickHouse could probably formulate a query that produced the above feature vector. While possible, this will invariably not only be a complex and computationally expensive query - especially over larger datasets of billions of rows.

Furthermore as noted, our feature vectors are dynamic and potentially consist of any number of combinations of different features during different training iterations. Additionally, ideally different engineers and data scientists would be using the same definition of a feature as well as writing the queries as optimally as possible.

Given the above demands, it makes sense to materialize our features into tables writing the results of the query into a table using `INSERT INTO SELECT`. This effectively means we perform the feature generation once, writing the results to a table from which they can be efficiently read and reused when iterating. This also allows us to declare the feature query once, optimally, and share the results with other engineers and scientists.

<blockquote style="font-size: 14px;">
<p>For now, we omit how users might wish to declare, version control, and share their feature definitions. SQL is, after all, code. There are several solutions to this problem, some of which solve different challenges - see "Build or Adopt".</p>
</blockquote>

### Feature tables

A feature table contains instances of a feature associated with an entity and, optionally, a timestamp. We have seen our users employ two table models for features - either creating a table **per feature** or **per entity**. Each approach has its respective pros and cons we explore below. Both of these allow re-usability of the features though, with the advantage they ensure the data is compressed well.

<blockquote style="font-size: 14px;">
<p>You don't need to create a feature table for every feature. Some can be consumed from the model table as-is, in cases where they are represented by a column value.</p>
</blockquote>

### Feature tables (per feature)

With a table per feature, the table name denotes the feature itself. The primary advantage of this approach is it potentially simplifies later joins. Additionally, it means users can use materialized views to maintain these tables as the source data changes - see "Updating".

The disadvantage of this approach is it doesn't scale as well as the "per event". Users with thousands of features will have thousands of tables. While possibly manageable, creating materialized views to maintain each of these is not viable.

As an example, consider the table responsible for storing the domain feature "number of unique IPs for each domain".

<pre style="font-size: 14px;"><code class="hljs language-sql"><span class="hljs-keyword">CREATE</span> <span class="hljs-keyword">TABLE</span> number_unique_ips_per_hour
(
  Domain String,
  EventTime DateTime64,
  <span class="hljs-keyword">Value</span> Int64
)
ENGINE <span class="hljs-operator">=</span> MergeTree
<span class="hljs-keyword">ORDER</span> <span class="hljs-keyword">BY</span> (Domain, EventTime)
</code></pre>

We have chosen the `ORDER BY` key to optimize both [compression and future reads](https://clickhouse.com/docs/en/data-modeling/schema-design#choosing-an-ordering-key). We can populate our feature table using a simple `INSERT INTO SELECT` with an aggregation to compute our feature.

<pre style="font-size: 14px;"><code class="hljs language-sql"><span class="hljs-keyword">INSERT</span> <span class="hljs-keyword">INTO</span> number_unique_ips_per_hour <span class="hljs-keyword">SELECT</span>
   Domain,
   toStartOfHour(EventTime) <span class="hljs-keyword">AS</span> EventTime,
   uniqExact(ClientIP) <span class="hljs-keyword">AS</span> <span class="hljs-keyword">Value</span>
<span class="hljs-keyword">FROM</span> predict_bounce_subset <span class="hljs-keyword">FINAL</span>
<span class="hljs-keyword">GROUP</span> <span class="hljs-keyword">BY</span>
   Domain,
   EventTime

<span class="hljs-number">0</span> <span class="hljs-keyword">rows</span> <span class="hljs-keyword">in</span> set. Elapsed: <span class="hljs-number">0.777</span> sec. Processed <span class="hljs-number">43.80</span> million <span class="hljs-keyword">rows</span>, <span class="hljs-number">1.49</span> GB (<span class="hljs-number">56.39</span> million <span class="hljs-keyword">rows</span><span class="hljs-operator">/</span>s., <span class="hljs-number">1.92</span> GB<span class="hljs-operator">/</span>s.)

<span class="hljs-keyword">SELECT</span> <span class="hljs-built_in">count</span>()
<span class="hljs-keyword">FROM</span> number_unique_ips_per_hour

┌─<span class="hljs-built_in">count</span>()─┐
│  <span class="hljs-number">613382</span> │
└─────────┘
</code></pre>

We choose to use `Domain` and `Value` as the column name for entity and feature value. This makes our future queries a little simpler. Users may wish to use a generic table structure for all features, with an `Entity` and `Value` column. 

<pre style="font-size: 14px;"><code class="hljs language-sql"><span class="hljs-keyword">CREATE</span> <span class="hljs-keyword">TABLE</span> <span class="hljs-operator">&lt;</span>feature_name<span class="hljs-operator">&gt;</span>
(
  Entity Variant(UInt64, Int64, String),
  EventTime DateTime64,
  <span class="hljs-keyword">Value</span> Variant(UInt64, Int64, Float64)
)
ENGINE <span class="hljs-operator">=</span> MergeTree
<span class="hljs-keyword">ORDER</span> <span class="hljs-keyword">BY</span> (Entity, EventTime)
</code></pre>

This requires the use of the `Variant` type. This type allows a column to support a union of other data types e.g. `Variant(String, Float64, Int64)` means that each row of this type has a value of either type `String`, `Float64` `Int64` or none of them (NULL value). 

This feature is currently experimental and optional for the above approach but required for the "Per entity" approach described below.

### Feature tables (per entity)

In a per entity approach we use the same table for all features which are associated with the same entity. In this case, we use a column, `FeatureId` below, to denote the name of the feature.

The advantage of this approach is its scalability. A single table can easily hold thousands of features.

The principal disadvantage is that currently materialized views are not supported by this approach.

Note we are forced to use the new `Variant` type in the below example for the domain features. While this table supports `UInt64`, `Int64`, and `Float64` feature values, it could potentially support more.

<pre style="font-size: 14px;"><code class="hljs language-sql"><span class="hljs-comment">-- domain Features</span>
<span class="hljs-keyword">SET</span> allow_experimental_variant_type<span class="hljs-operator">=</span><span class="hljs-number">1</span>
<span class="hljs-keyword">CREATE</span> <span class="hljs-keyword">TABLE</span> domain_features
(
  Domain String,
  FeatureId String,
  EventTime DateTime,
  <span class="hljs-keyword">Value</span> Variant(UInt64, Int64, Float64)
)
ENGINE <span class="hljs-operator">=</span> MergeTree
<span class="hljs-keyword">ORDER</span> <span class="hljs-keyword">BY</span> (FeatureId, Domain, EventTime)
</code></pre>

This table's `ORDER BY` is optimized for filtering by a specific `FeatureId` and `Domain` - the typical access pattern we will see later.

To populate our "number of unique IPs for each domain" feature into this table, we need a similar query to that used earlier:

<pre style="font-size: 14px;"><code class="hljs language-sql"><span class="hljs-keyword">INSERT</span> <span class="hljs-keyword">INTO</span> domain_features <span class="hljs-keyword">SELECT</span>
   Domain,
   <span class="hljs-string">'number_unique_ips_per_hour'</span> <span class="hljs-keyword">AS</span> FeatureId,
   toStartOfHour(EventTime) <span class="hljs-keyword">AS</span> EventTime,
   uniqExact(ClientIP) <span class="hljs-keyword">AS</span> <span class="hljs-keyword">Value</span>
<span class="hljs-keyword">FROM</span> predict_bounce_subset <span class="hljs-keyword">FINAL</span>
<span class="hljs-keyword">GROUP</span> <span class="hljs-keyword">BY</span>
   Domain,
   EventTime

<span class="hljs-number">0</span> <span class="hljs-keyword">rows</span> <span class="hljs-keyword">in</span> set. Elapsed: <span class="hljs-number">0.573</span> sec. Processed <span class="hljs-number">43.80</span> million <span class="hljs-keyword">rows</span>, <span class="hljs-number">1.49</span> GB (<span class="hljs-number">76.40</span> million <span class="hljs-keyword">rows</span><span class="hljs-operator">/</span>s., <span class="hljs-number">2.60</span> GB<span class="hljs-operator">/</span>s.)

<span class="hljs-keyword">SELECT</span> <span class="hljs-built_in">count</span>()
<span class="hljs-keyword">FROM</span> domain_features

┌─<span class="hljs-built_in">count</span>()─┐
│  <span class="hljs-number">613382</span> │
└─────────┘
</code></pre>

<blockquote style="font-size: 14px;">
<p>Users new to ClickHouse may wonder if the "per feature" approach allows faster retrieval of features than the "per entity" approach. Due to the use of ordering keys and ClickHouse sparse indices, there should be no difference here.</p>
</blockquote>

### Updating feature tables

While some features are static, we often want to ensure they are updated as the source data or subsets change. As described for "Updating subsets", we can achieve this with Materialized views.

In the case of feature tables, our materialized views are typically more complex as the results are often the results of aggregation and not just simple transformations and filtering. As a result, the query executed by the materialized view will produce partial aggregation states. These partial aggregation states represent the intermediate state of the aggregation, which the target feature table can merge together. This requires our feature table to use the [AggregatingMergeTree](https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/aggregatingmergetree) with appropriate `AggregateFunction` types.

We provide an example below for a "per feature" table `number_unique_ips_per_hour.`

<pre style="font-size: 14px;"><code class="hljs language-sql"><span class="hljs-keyword">CREATE</span> <span class="hljs-keyword">TABLE</span> number_unique_ips_per_hour
(
  Entity String,
  EventTime DateTime64,
  <span class="hljs-comment">-- the AggregateFunction merges states produced by the view</span>
  <span class="hljs-keyword">Value</span> AggregateFunction(uniqExact, UInt32)
)
ENGINE <span class="hljs-operator">=</span> AggregatingMergeTree
<span class="hljs-keyword">ORDER</span> <span class="hljs-keyword">BY</span> (Entity, EventTime)

<span class="hljs-keyword">CREATE</span> MATERIALIZED <span class="hljs-keyword">VIEW</span> number_unique_ips_per_hour_mv <span class="hljs-keyword">TO</span> number_unique_ips_per_hour <span class="hljs-keyword">AS</span>
<span class="hljs-keyword">SELECT</span>
   domain(URL) <span class="hljs-keyword">AS</span> Entity,
   toStartOfHour(EventTime) <span class="hljs-keyword">AS</span> EventTime,
   <span class="hljs-comment">-- our view uses the -State suffix to generate intermediate states</span>
   uniqExactState(ClientIP) <span class="hljs-keyword">AS</span> <span class="hljs-keyword">Value</span>
<span class="hljs-keyword">FROM</span> predict_bounce_subset
<span class="hljs-keyword">GROUP</span> <span class="hljs-keyword">BY</span>
   Entity,
   EventTime
</code></pre>

As new rows are inserted into the `predict_bounce_subset` table, our `number_unique_ips_per_hour` feature table will be updated.

When querying `number_unique_ips_per_hour`, we must either use the `FINAL` clause or `GROUP BY Entity, EventTime` to ensure aggregation states are merged along with the [`-Merge`](https://clickhouse.com/docs/en/sql-reference/aggregate-functions/combinators#-merge) variant of the aggregation function (in this case, `uniqExact`). As shown this below, this alters the query used to fetch entities - see [here](https://clickhouse.com/docs/en/materialized-view#a-more-complex-example) for further details.

<pre style="font-size: 14px;"><code class="hljs language-sql"><span class="hljs-comment">-- Select entities for a single domain</span>
<span class="hljs-keyword">SELECT</span>
   EventTime,
   Entity,
   uniqExactMerge(<span class="hljs-keyword">Value</span>) <span class="hljs-keyword">AS</span> <span class="hljs-keyword">Value</span>
<span class="hljs-keyword">FROM</span> number_unique_ips_per_hour
<span class="hljs-keyword">WHERE</span> Entity <span class="hljs-operator">=</span> <span class="hljs-string">'smeshariki.ru'</span>
<span class="hljs-keyword">GROUP</span> <span class="hljs-keyword">BY</span>
   Entity,
   EventTime
<span class="hljs-keyword">ORDER</span> <span class="hljs-keyword">BY</span> EventTime <span class="hljs-keyword">DESC</span> LIMIT <span class="hljs-number">5</span>

┌───────────────EventTime─┬─Entity────────┬─<span class="hljs-keyword">Value</span>─┐
│ <span class="hljs-number">2013</span><span class="hljs-number">-07</span><span class="hljs-number">-31</span> <span class="hljs-number">23</span>:<span class="hljs-number">00</span>:<span class="hljs-number">00.000</span> │ smeshariki.ru │  <span class="hljs-number">3810</span> │
│ <span class="hljs-number">2013</span><span class="hljs-number">-07</span><span class="hljs-number">-31</span> <span class="hljs-number">22</span>:<span class="hljs-number">00</span>:<span class="hljs-number">00.000</span> │ smeshariki.ru │  <span class="hljs-number">3895</span> │
│ <span class="hljs-number">2013</span><span class="hljs-number">-07</span><span class="hljs-number">-31</span> <span class="hljs-number">21</span>:<span class="hljs-number">00</span>:<span class="hljs-number">00.000</span> │ smeshariki.ru │  <span class="hljs-number">4053</span> │
│ <span class="hljs-number">2013</span><span class="hljs-number">-07</span><span class="hljs-number">-31</span> <span class="hljs-number">20</span>:<span class="hljs-number">00</span>:<span class="hljs-number">00.000</span> │ smeshariki.ru │  <span class="hljs-number">3893</span> │
│ <span class="hljs-number">2013</span><span class="hljs-number">-07</span><span class="hljs-number">-31</span> <span class="hljs-number">19</span>:<span class="hljs-number">00</span>:<span class="hljs-number">00.000</span> │ smeshariki.ru │  <span class="hljs-number">3926</span> │
└─────────────────────────┴───────────────┴───────┘

<span class="hljs-number">5</span> <span class="hljs-keyword">rows</span> <span class="hljs-keyword">in</span> set. Elapsed: <span class="hljs-number">0.491</span> sec. Processed <span class="hljs-number">8.19</span> thousand <span class="hljs-keyword">rows</span>, <span class="hljs-number">1.28</span> MB (<span class="hljs-number">16.67</span> thousand <span class="hljs-keyword">rows</span><span class="hljs-operator">/</span>s., <span class="hljs-number">2.61</span> MB<span class="hljs-operator">/</span>s.)
Peak memory usage: <span class="hljs-number">235.93</span> MiB.
</code></pre>

While a little more complex, intermediate aggregation states allow us to use the above table to generate features for different times. For example, we could compute the number of unique IPs per domain per day from the above table using [this query](https://pastila.nl/?021fe212/fe019875509a4475994130627bae9798#rIizu/2ZAJI1h66cUUX/bQ==), something we couldn't do with our original feature table.

Users may notice that our subset table `predict_bounce_subset` is being updated with a materialized view already, which in turn has Materialized views attached to it. As shown below, this means our Materialized views are effectively "chained". For more examples of chaining Materialized views, see [here](https://clickhouse.com/blog/chaining-materialized-views).

![chained_mvs.png](https://clickhouse.com/uploads/chained_mvs_4878676d59.png)

### Updating per entity feature tables

The above "per feature" approach to modeling means a materialized view per feature table (a materialized view can send results to only one table). In larger use cases, this becomes a constraint on scaling - materialized views incur an insert time overhead, and we don't recommend more than 10 on a single table.

A "per entity" feature table model reduces the number of feature tables. In order to encapsulate multiple queries for different features would require us to use Variant type with `AggregateFunction` types. This is currently not supported.

As an alternative, users can use Refreshable Materialized Views (currently experimental). Unlike ClickHouse's incremental materialized views, these views periodically execute the view query over the entire dataset, storing the results in a target table whose contents are atomically replaced. 

![refreshable_views.png](https://clickhouse.com/uploads/refreshable_views_1640f82594.png)

Users can use this capability to periodically update feature tables on a schedule. We provide an example of this below, where the "number of unique IPs for each domain" is updated every 10 minutes.

<pre style="font-size: 14px;"><code class="hljs language-sql"><span class="hljs-comment">--enable experimental feature</span>
<span class="hljs-keyword">SET</span> allow_experimental_refreshable_materialized_view <span class="hljs-operator">=</span> <span class="hljs-number">1</span>

<span class="hljs-keyword">CREATE</span> MATERIALIZED <span class="hljs-keyword">VIEW</span> domain_features_mv REFRESH <span class="hljs-keyword">EVERY</span> <span class="hljs-number">10</span> MINUTES <span class="hljs-keyword">TO</span> domain_features <span class="hljs-keyword">AS</span>
<span class="hljs-keyword">SELECT</span>
   Domain,
   <span class="hljs-string">'number_unique_ips_per_hour'</span> <span class="hljs-keyword">AS</span> FeatureId,
   toStartOfHour(EventTime) <span class="hljs-keyword">AS</span> EventTime,
   uniqExact(ClientIP) <span class="hljs-keyword">AS</span> <span class="hljs-keyword">Value</span>
<span class="hljs-keyword">FROM</span> predict_bounce_subset
<span class="hljs-keyword">GROUP</span> <span class="hljs-keyword">BY</span>
   Domain,
   EventTime
</code></pre>

Further details on Refreshable Materialized views can be found [here](https://clickhouse.com/docs/en/materialized-view/refreshable-materialized-view).

## Step 4 - Generating model data

With our features created, we can begin the process of combining these into our model data - which will form the basis of our training, validation and test set.

The rows in this table will form the basis of our model, with each row corresponding to a feature vector. To generate this, we need to join our features. Some of these features will come from feature tables, others directly from our "features subset" table i.e. `predict_bounce_subset` above.

As the feature subset table contains our events with the label, timestamp, and entity keys, it makes sense for this to form the base table of the join (left-hand side). This is also likely to be the largest table, making it a sensible [choice for the left-hand side of the join](https://clickhouse.com/docs/en/guides/joining-tables#optimizing-join-performance).

Features will be joined to this table based on two criteria:

* the closest timestamp (`EventTime`) for each feature to the row in the feature subset table (`predict_bounce_subset`).
* the corresponding entity column for the feature table, e.g., `UserID` or `Domain.`

**To join based on this equi join AND the closest time requires an `ASOF JOIN`.**

We will send the results of this join to a table, using an `INSERT INTO`, which we refer to as the "model table". This will be used to produce future training, validation and test sets.

Before exploring the join, we declare our "model table" `predict_bounce`.

<pre style="font-size: 14px;"><code class="hljs language-sql"><span class="hljs-keyword">CREATE</span> <span class="hljs-keyword">TABLE</span> predict_bounce_model (
   <span class="hljs-type">Row</span> UInt64,
   EventTime DateTime64,
   UserID UInt64,
   Domain String,
   UserAgent UInt8,
   RefererCategoryID UInt16,
   URLCategoryID UInt16,
   DomainsVisitedPerHour UInt32 COMMENT <span class="hljs-string">'Number of domains visited in last hour by the user'</span>,
   UniqueIPsPerHour UInt32 COMMENT <span class="hljs-string">'Number of unique ips visiting the domain per hour'</span>,
   AverageRequestTime Float32 COMMENT <span class="hljs-string">'Average request time for the domain per hour'</span>,
   IsNotBounce UInt8,
) ENGINE <span class="hljs-operator">=</span> MergeTree
<span class="hljs-keyword">ORDER</span> <span class="hljs-keyword">BY</span> (<span class="hljs-type">Row</span>, EventTime)
</code></pre>

The `Row` column here will contain a unique entry for each row in the dataset. We make this part of our `ORDER BY` and exploit it later to produce training and test sets efficiently.

### Joining and aligning features

To join and align features based on the entity key and timestamp, we can use the ASOF. How we construct our JOIN depends on several factors whether we are using "per feature" or "per entity" feature tables.

Let's assume we are using "per feature" tables and have the following available:

* `number_unique_ips_per_hour` - containing the number of unique ips visiting **each domain** per hour. Example above.
* `domains_visited_per_hour` - Number of domains visited in last hour by **each user**. Generated using the queries [here](https://pastila.nl/?02af4d88/82927122387952892b23b7e8e90738bd#tsngZtbhHCxFhr5mVuB07w==).
* `average_request_time` - Average request time for **each domain** per hour. Generated using the queries [here](https://pastila.nl/?07708678/211b6c5f5d81b9818496b91efaaa78f7#SX1/LZuj+7fsAYPSsvu4qQ==).

Our JOIN here is quite straightforward:

<pre style="font-size: 14px;"><code class="hljs language-sql"><span class="hljs-keyword">INSERT</span> <span class="hljs-keyword">INTO</span> predict_bounce_model <span class="hljs-keyword">SELECT</span>
   rand() <span class="hljs-keyword">AS</span> <span class="hljs-type">Row</span>,
   mt.EventTime <span class="hljs-keyword">AS</span> EventTime,
   mt.UserID <span class="hljs-keyword">AS</span> UserID,
   mt.Domain <span class="hljs-keyword">AS</span> Domain,
   mt.UserAgent,
   mt.RefererCategoryID,
   mt.URLCategoryID,
   dv.Value <span class="hljs-keyword">AS</span> DomainsVisitedPerHour,
   uips.Value <span class="hljs-keyword">AS</span> UniqueIPsPerHour,
   art.Value <span class="hljs-keyword">AS</span> AverageRequestTime,
   mt.IsNotBounce
<span class="hljs-keyword">FROM</span> predict_bounce_subset <span class="hljs-keyword">AS</span> mt <span class="hljs-keyword">FINAL</span>
ASOF <span class="hljs-keyword">JOIN</span> domains_visited_per_hour <span class="hljs-keyword">AS</span> dv <span class="hljs-keyword">ON</span> (mt.UserID <span class="hljs-operator">=</span> dv.UserID) <span class="hljs-keyword">AND</span> (mt.EventTime <span class="hljs-operator">&gt;=</span> dv.EventTime)
ASOF <span class="hljs-keyword">JOIN</span> number_unique_ips_per_hour <span class="hljs-keyword">AS</span> uips <span class="hljs-keyword">ON</span> (mt.Domain <span class="hljs-operator">=</span> uips.Domain) <span class="hljs-keyword">AND</span> (mt.EventTime <span class="hljs-operator">&gt;=</span> uips.EventTime)
ASOF <span class="hljs-keyword">JOIN</span> average_request_time <span class="hljs-keyword">AS</span> art <span class="hljs-keyword">ON</span> (mt.Domain <span class="hljs-operator">=</span> art.Domain) <span class="hljs-keyword">AND</span> (mt.EventTime <span class="hljs-operator">&gt;=</span> art.EventTime)

<span class="hljs-number">0</span> <span class="hljs-keyword">rows</span> <span class="hljs-keyword">in</span> set. Elapsed: <span class="hljs-number">13.440</span> sec. Processed <span class="hljs-number">89.38</span> million <span class="hljs-keyword">rows</span>, <span class="hljs-number">3.10</span> GB (<span class="hljs-number">6.65</span> million <span class="hljs-keyword">rows</span><span class="hljs-operator">/</span>s., <span class="hljs-number">230.36</span> MB<span class="hljs-operator">/</span>s.)
Peak memory usage: <span class="hljs-number">2.94</span> GiB.

<span class="hljs-keyword">SELECT</span> <span class="hljs-operator">*</span> <span class="hljs-keyword">FROM</span> predict_bounce_model LIMIT <span class="hljs-number">1</span> FORMAT Vertical

<span class="hljs-type">Row</span> <span class="hljs-number">1</span>:
──────
<span class="hljs-type">Row</span>:               	<span class="hljs-number">57</span>
EventTime:         	<span class="hljs-number">2013</span><span class="hljs-number">-07</span><span class="hljs-number">-10</span> <span class="hljs-number">06</span>:<span class="hljs-number">11</span>:<span class="hljs-number">39.000</span>
UserID:            	<span class="hljs-number">1993141920794806602</span>
Domain:            	smeshariki.ru
UserAgent:         	<span class="hljs-number">7</span>
RefererCategoryID: 	<span class="hljs-number">16000</span>
URLCategoryID:     	<span class="hljs-number">9911</span>
DomainsVisitedPerHour: <span class="hljs-number">1</span>
UniqueIPsPerHour:  	<span class="hljs-number">16479</span>
AverageRequestTime:	<span class="hljs-number">182.69382</span>
IsNotBounce:       	<span class="hljs-number">0</span>
</code></pre>

While similar, this join becomes a little more complex (and costly) if using "per entity" feature tables. Assuming we have the feature tables `domain_features` and `user_features` populated with [these queries](https://pastila.nl/?00226ff6/666bf2f425b877ae8cdf08bf2dfa3ee5#0q0sxENDDPzchVE7DZZJRA==).

<pre style="font-size: 14px;"><code class="hljs language-sql"><span class="hljs-keyword">INSERT</span> <span class="hljs-keyword">INTO</span> predict_bounce_model <span class="hljs-keyword">SELECT</span>
   rand() <span class="hljs-keyword">AS</span> <span class="hljs-type">Row</span>,
   mt.EventTime <span class="hljs-keyword">AS</span> EventTime,
   mt.UserID <span class="hljs-keyword">AS</span> UserID,
   mt.Domain <span class="hljs-keyword">AS</span> Domain,
   mt.UserAgent,
   mt.RefererCategoryID,
   mt.URLCategoryID,
   DomainsVisitedPerHour,
   UniqueIPsPerHour,
   AverageRequestTime,
   mt.IsNotBounce
<span class="hljs-keyword">FROM</span> predict_bounce_subset <span class="hljs-keyword">AS</span> mt <span class="hljs-keyword">FINAL</span>
ASOF <span class="hljs-keyword">LEFT</span> <span class="hljs-keyword">JOIN</span> (
   <span class="hljs-keyword">SELECT</span> Domain, EventTime, Value.UInt64 <span class="hljs-keyword">AS</span> UniqueIPsPerHour
   <span class="hljs-keyword">FROM</span> domain_features
   <span class="hljs-keyword">WHERE</span> FeatureId <span class="hljs-operator">=</span> <span class="hljs-string">'number_unique_ips_per_hour'</span>
) <span class="hljs-keyword">AS</span> df <span class="hljs-keyword">ON</span> (mt.Domain <span class="hljs-operator">=</span> df.Domain) <span class="hljs-keyword">AND</span> (mt.EventTime <span class="hljs-operator">&gt;=</span> df.EventTime)
ASOF <span class="hljs-keyword">LEFT</span> <span class="hljs-keyword">JOIN</span> (
   <span class="hljs-keyword">SELECT</span> Domain, EventTime, Value.Float64 <span class="hljs-keyword">AS</span> AverageRequestTime
   <span class="hljs-keyword">FROM</span> domain_features
   <span class="hljs-keyword">WHERE</span> FeatureId <span class="hljs-operator">=</span> <span class="hljs-string">'average_request_time'</span>
) <span class="hljs-keyword">AS</span> art <span class="hljs-keyword">ON</span> (mt.Domain <span class="hljs-operator">=</span> art.Domain) <span class="hljs-keyword">AND</span> (mt.EventTime <span class="hljs-operator">&gt;=</span> art.EventTime)
ASOF <span class="hljs-keyword">LEFT</span> <span class="hljs-keyword">JOIN</span> (
   <span class="hljs-keyword">SELECT</span> UserID, EventTime, Value.UInt64 <span class="hljs-keyword">AS</span> DomainsVisitedPerHour
   <span class="hljs-keyword">FROM</span> user_features
   <span class="hljs-keyword">WHERE</span> FeatureId <span class="hljs-operator">=</span> <span class="hljs-string">'domains_visited_per_hour'</span>
) <span class="hljs-keyword">AS</span> dv <span class="hljs-keyword">ON</span> (mt.UserID <span class="hljs-operator">=</span> dv.UserID) <span class="hljs-keyword">AND</span> (mt.EventTime <span class="hljs-operator">&gt;=</span> dv.EventTime)

<span class="hljs-number">0</span> <span class="hljs-keyword">rows</span> <span class="hljs-keyword">in</span> set. Elapsed: <span class="hljs-number">12.528</span> sec. Processed <span class="hljs-number">58.65</span> million <span class="hljs-keyword">rows</span>, <span class="hljs-number">3.08</span> GB (<span class="hljs-number">4.68</span> million <span class="hljs-keyword">rows</span><span class="hljs-operator">/</span>s., <span class="hljs-number">245.66</span> MB<span class="hljs-operator">/</span>s.)
Peak memory usage: <span class="hljs-number">3.16</span> GiB.
</code></pre>

<blockquote style="font-size: 14px;">
<p>The above joins use a hash join. 24.7 added support for the <code>full_sorting_merge</code> algorithm for <code>ASOF JOIN</code>. This algorithm can exploit the sort order of the tables being joined, thus avoiding a sorting phase prior to joining. The joined tables can be filtered by each other's join keys prior to any sort and merge operations in order to minimize the amount of processed data. This will allow the above queries to be as fast while consuming fewer resources.</p>
</blockquote>

## Step 5 - Generating test and training sets

With model data generated, we can produce training, validation, and test sets as required. Each of these will consist of different percentages of the data e.g. 80, 10, 10. Across query executions these need to be consistent results - we can't allow test data to seep into training and vise versa. Furthermore, the result sets need to be stable - some algorithms can be influenced by the order in which the data is delivered, delivering different results.

To achieve consistency and stability of results while also ensuring queries return rows quickly, we can exploit the `Row` and `EventTime` columns.

Suppose we wish to obtain 80% of the data for our training in order of `EventTime`. This can be obtained from our `predict_bounce_model` table with a simple query that performs a `mod 100` on the `Row` column:

<pre style="font-size: 14px;"><code class="hljs language-sql"><span class="hljs-keyword">SELECT</span> <span class="hljs-operator">*</span> <span class="hljs-keyword">EXCEPT</span> <span class="hljs-type">Row</span>
<span class="hljs-keyword">FROM</span> predict_bounce_model
<span class="hljs-keyword">WHERE</span> (<span class="hljs-type">Row</span> <span class="hljs-operator">%</span> <span class="hljs-number">100</span>) <span class="hljs-operator">&lt;</span> <span class="hljs-number">80</span>
<span class="hljs-keyword">ORDER</span> <span class="hljs-keyword">BY</span> EventTime, <span class="hljs-type">Row</span> <span class="hljs-keyword">ASC</span>
</code></pre>

We can confirm these rows deliver stable results with a few simple queries:

<pre style="font-size: 14px;"><code class="hljs language-sql"><span class="hljs-keyword">SELECT</span>
   groupBitXor(sub) <span class="hljs-keyword">AS</span> hash,
   <span class="hljs-built_in">count</span>() <span class="hljs-keyword">AS</span> count
<span class="hljs-keyword">FROM</span>
(
   <span class="hljs-keyword">SELECT</span> sipHash64(concat(<span class="hljs-operator">*</span>)) <span class="hljs-keyword">AS</span> sub
   <span class="hljs-keyword">FROM</span> predict_bounce_model
   <span class="hljs-keyword">WHERE</span> (<span class="hljs-type">Row</span> <span class="hljs-operator">%</span> <span class="hljs-number">100</span>) <span class="hljs-operator">&lt;</span> <span class="hljs-number">80</span>
   <span class="hljs-keyword">ORDER</span> <span class="hljs-keyword">BY</span>
       EventTime <span class="hljs-keyword">ASC</span>,
       <span class="hljs-type">Row</span> <span class="hljs-keyword">ASC</span>
)

┌─────────────────hash─┬────count─┐
│ <span class="hljs-number">14452214628073740040</span> │ <span class="hljs-number">34315802</span> │
└──────────────────────┴──────────┘

<span class="hljs-number">1</span> <span class="hljs-type">row</span> <span class="hljs-keyword">in</span> set. Elapsed: <span class="hljs-number">8.346</span> sec. Processed <span class="hljs-number">42.89</span> million <span class="hljs-keyword">rows</span>, <span class="hljs-number">2.74</span> GB (<span class="hljs-number">5.14</span> million <span class="hljs-keyword">rows</span><span class="hljs-operator">/</span>s., <span class="hljs-number">328.29</span> MB<span class="hljs-operator">/</span>s.)
Peak memory usage: <span class="hljs-number">10.29</span> GiB.

<span class="hljs-comment">--repeat query, omitted for brevity</span>

┌─────────────────hash─┬────count─┐
│ <span class="hljs-number">14452214628073740040</span> │ <span class="hljs-number">34315802</span> │
└──────────────────────┴──────────┘
</code></pre>

Similarly, a training set and validation set could be obtained with the following, each constituting 10% of the data:

<pre style="font-size: 14px;"><code class="hljs language-sql"><span class="hljs-comment">-- validation</span>
<span class="hljs-keyword">SELECT</span> <span class="hljs-operator">*</span> <span class="hljs-keyword">EXCEPT</span> <span class="hljs-type">Row</span>
<span class="hljs-keyword">FROM</span> predict_bounce_model
<span class="hljs-keyword">WHERE</span> (<span class="hljs-type">Row</span> <span class="hljs-operator">%</span> <span class="hljs-number">100</span>) <span class="hljs-keyword">BETWEEN</span> <span class="hljs-number">80</span> <span class="hljs-keyword">AND</span> <span class="hljs-number">89</span>
<span class="hljs-keyword">ORDER</span> <span class="hljs-keyword">BY</span> EventTime, <span class="hljs-type">Row</span> <span class="hljs-keyword">ASC</span>
<span class="hljs-comment">-- test</span>
<span class="hljs-keyword">SELECT</span> <span class="hljs-operator">*</span> <span class="hljs-keyword">EXCEPT</span> <span class="hljs-type">Row</span>
<span class="hljs-keyword">FROM</span> predict_bounce_model
<span class="hljs-keyword">WHERE</span> (<span class="hljs-type">Row</span> <span class="hljs-operator">%</span> <span class="hljs-number">100</span>) <span class="hljs-keyword">BETWEEN</span> <span class="hljs-number">90</span> <span class="hljs-keyword">AND</span> <span class="hljs-number">100</span>
<span class="hljs-keyword">ORDER</span> <span class="hljs-keyword">BY</span> EventTime, <span class="hljs-type">Row</span> <span class="hljs-keyword">ASC</span>
</code></pre>


The exact approach here users use may depend on how they want to separate their training and test set. For our model, it may be better to use all data before a fixed point in time for training, with the test set using all rows after this. Above, our training and test sample data contain data from the full period. This may cause leakage of some information between the two sets e.g. events from the same page visit. We overlook this for the purposes of an example. We recommend adjusting the ordering key on your model table based on how you intend to consume rows - see [here](https://clickhouse.com/docs/en/data-modeling/schema-design#choosing-an-ordering-key) for recommendations on selecting an ordering key.

## Build vs Adopt

The process described involves multiple queries and complex procedures. When building an offline feature store with ClickHouse, users typically take one of the following approaches:

1. **Build Their Own Feature Store**: This is the most advanced and complex approach, allowing users to optimize processes and schemas for their specific data. It's often adopted by companies where the feature store is crucial to their business and involves large data volumes, such as in ad-tech.

2. **Dbt + Airflow**: Dbt is popular for managing data transformations and handling complex queries and data modeling. When combined with Airflow, a powerful workflow orchestration tool, users can automate and schedule the above processes. This approach offers modular and maintainable workflows, balancing custom solutions with existing tools to handle large data volumes and complex queries without a fully custom-built feature store or the workflows imposed by an existing solution.

3. **Adopt a Feature Store with ClickHouse**: Feature stores like Featureform integrate ClickHouse for data storage, transformation, and serving offline features. These stores manage processes, version features, and enforce governance and compliance rules, reducing data engineering complexity for data scientists. Adopting these technologies depends on how well the abstractions and workflows fit the use case.

![featureform.png](https://clickhouse.com/uploads/featureform_cf5b1cb84f.png)
_Credit: Featureform Feature Store_

## ClickHouse at inference time

This blog post discusses using ClickHouse as an offline store for generating features for model training. Once trained, a model can be deployed for predictions, requiring real-time data like user ID and domain. Precomputed features, such as "domains visited in the last hour," are necessary for predictions but are too costly to compute during inference. These features need to be served based on the most recent data version, especially for real-time predictions.

ClickHouse, as a real-time analytics database, can handle highly concurrent queries with low latency and high write workloads, thanks to its log-structured merge tree. This makes it suitable for serving features in an online store. Features from the offline store can be materialized to new tables in the same ClickHouse cluster or a different instance using existing capabilities. Further details on this process will be covered in a later post.

## Conclusion

This blog has outlined common data modeling approaches for using ClickHouse as an offline feature store and transformation engine. While not exhaustive, these approaches provide a starting point and align with techniques used in feature stores like Featureform, which integrates with ClickHouse. We welcome contributions and ideas for improvement. If you're using ClickHouse as a feature store, let us know!

Learn how to model machine learning data in ClickHouse to accelerate your pipelines and enable the fast building of features over potentially billions of rows.




