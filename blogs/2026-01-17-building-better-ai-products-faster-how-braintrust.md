---
title: "Building Better AI Products, Faster: How Braintrust Uses ClickHouse for Real-Time Data Analysis"
date: "2024-07-02T10:15:23.080Z"
author: "ClickHouse Team"
category: "User stories"
excerpt: "Braintrust is leading a transformation in how AI companies build, test, and improve their products."
---

# Building Better AI Products, Faster: How Braintrust Uses ClickHouse for Real-Time Data Analysis

<a href="https://www.braintrust.dev?utm_source=clickhouse" target="_blank">Braintrust</a> is leading a transformation in how AI companies build, test, and improve their products. Since 2023, its platform has helped companies like Zapier, Notion, and Airtable gain deeper insights into the performance of their AI models and make faster, data-driven decisions that enhance reliability and quality. By combining [real-time data processing](https://clickhouse.com/engineering-resources/what-is-real-time-analytics) with automated evaluation tools, Braintrust helps demystify the black-box nature of AI, allowing for continuous improvement and optimization.

As AI applications grow in scale and complexity, so do the challenges of efficiently managing and processing the vast amounts of data engineering teams need to understand how their models are performing, and whether or not a product change had a desired effect. Data processing delays are especially problematic when iterative improvement relies on immediate feedback.

“When you’re doing interactive analysis of an AI product, an engineer can’t run something and then wait for five minutes,” said Braintrust founder and CEO Ankur Goyal at a June 2024 San Francisco [meetup](/videos/braintrusts-take-on-clickhouse-for-realtime-analytics) for ClickHouse users.

Recognizing the need for a solution that could handle the demands of real-time data processing and provide the rapid feedback necessary for continuous improvement, Ankur created Braintrust. From day one, Braintrust was designed to ensure immediate data availability and facilitate fast iteration cycles. So it’s no surprise that as the company grew, they implemented ClickHouse to enable real-time queries at scale.

![braintrust-img1.png](https://clickhouse.com/uploads/braintrust_img1_bc7b856fc5.png)

## Braintrust Beginnings

Ankur started his first company, Impira, in 2017. It used machine learning to help companies extract and manage unstructured data such as documents, videos, images, audio, and webpages. After selling the business to Figma, he took over Figma’s AI team. 

“At both Impira and Figma, it was really, really hard for us to make changes to our AI products without breaking everything,” Ankur says.

To overcome this challenge, Ankur built internal toolkits at both companies, using evaluations to systematically test and validate AI models. This process included rigorous logging, performance tracking, output visualization, and failure analysis to enable ongoing improvements without inadvertently breaking other parts of the system. 

Then in 2023, Ankur was talking to investor and entrepreneur Elad Gil who steered him to an important realization.

“He was like, ‘Hey, you’ve built the same thing twice,’” Ankur recalls. “‘Other companies are trying to do AI stuff. Maybe they have this problem, too.’”

Ankur began talking to other software developers who were building AI-enabled products. He soon realized there was a widespread need for an enterprise-grade stack that could allow AI companies to evaluate and improve their products faster and more reliably. He raised $5.1 million in seed funding and got to work building Braintrust.


## In Search of Efficiency

At Figma, Ankur had experienced the limitations of traditional cloud data warehouses for building real-time data driven applications. Over a yearlong period, the data team had engineered a pipeline that took five minutes to process data from an experiment and make it queryable. While impressive compared to other companies where a process like this might take an hour or more, it wasn’t nearly fast enough for the interactive analysis required in modern AI development.

As he began building Braintrust, Ankur recognized the need for a more efficient database that could process large volumes of data with minimal latency. His search led him to ClickHouse, an open-source columnar database management system known for its high performance and low-latency capabilities. Right away he saw that ClickHouse’s ability to process complex queries with minimal delay was essential to meeting the demands of AI companies.

With ClickHouse, Ankur ensured that Braintrust could provide instant data availability, streamline performance tracking, and facilitate rapid iteration cycles. The integration helped Ankur and his team build a platform capable of managing complex data workflows and delivering the real-time analysis required by Braintrust’s customers.

![braintrust-img2.png](https://clickhouse.com/uploads/braintrust_img2_ddda64022d.png)

## ClickHouse at the Core

Braintrust uses a multi-database architecture to optimize performance and reliability. Initial data writes are handled by Postgres, which supports transactional integrity and complex updates. DuckDB powers the front end for lightweight, in-browser analytics.

At the heart of this architecture is ClickHouse, which provides the real-time data analytics and high-speed processing necessary for modern AI model development. Unlike other solutions, Clickhouse offers unmatched performance when it comes to handling large volumes of data and executing complex queries with minimal latency. Its columnar storage format allows for efficient compression and fast access to relevant data, making it ideally suited to meet Braintrust’s need for immediate data availability and rapid feedback cycles.

Here’s a look at how ClickHouse is integrated into Braintrust’s platform:


### 1. Real-Time Data Replication

Data written to Postgres is instantly replicated to ClickHouse. This ensures that any new data generated by experiments or user interactions is available for real-time analysis. The replication process is efficient, taking just a few hundred milliseconds to a few seconds, ensuring minimal delay and maximum availability — something they were unable to achieve with other vendors in their testing.


### 2. Columnar Storage and Compression

ClickHouse uses a columnar storage format optimized for read-heavy operations. This format allows for efficient compression and quick access to relevant data columns, allowing Braintrust to handle large data volumes without compromising on speed or performance.


### 3. Query Optimization and Execution

ClickHouse’s advanced query optimization is achieved through table primary indexes and MergeTree engines, which reduce the amount of data read against a table. These features allow Braintrust to execute complex queries rapidly and efficiently. This is critical for Braintrust’s evaluation tools, which require fast and accurate query results.


### 4. Visualization Dashboards

When you load an experiment in Braintrust, it starts by issuing a query to ClickHouse to search for the relevant data and pre-process it. The data is then sent to your browser, where DuckDB running in WASM provides the last-mile of interactivity for front-end analytics. This combination gives developers immediate insights into AI model performance, allowing them to explore data, track metrics, and identify issues in real time.


### 5. Scalability

ClickHouse’s distributed architecture and horizontal scaling is another major advantage for Braintrust. It allows Braintrust to increase data loads and run concurrent queries without degrading performance. By adding more nodes to their ClickHouse cluster, Ankur and his team maintain high performance even under the strain of large-scale data operations, ensuring consistent service quality as their customer base grows.


### 6. Fault Tolerance and Reliability

ClickHouse’s fault-tolerant features ensure data integrity and availability, even in the event of hardware failures. These include robust replication mechanisms and frequent backups, which safeguard against data loss and facilitate quick recovery from failures. The reliability they provide is important for Braintrust’s customers, as it guarantees continuous operation and consistent service.


## A New AI Frontier

Already, many of the world’s most successful AI companies rely on Braintrust’s platform to improve their product development processes. With the help of real-time analytics and automated evaluation tools, these companies have been able to build and ship higher-quality AI products faster, maintaining a competitive edge in the market.

“Braintrust fills the missing (and critical!) gap of evaluating non-deterministic AI systems,” said Mike Knoop, co-founder and head of AI at Zapier, at the time of <a href="https://www.braintrustdata.com/blog/reliable-ai?utm_source=clickhouse" target="_blank">Braintrust’s launch</a>. “We've used it to successfully measure and improve our AI-first products.”

Looking ahead, Ankur and the Braintrust team plan to continue refining their platform to meet the evolving needs of AI developers. This includes further optimizing and expanding their use of ClickHouse to handle even larger datasets and more complex queries. With its scalability and reliability, ClickHouse will continue to support Braintrust’s growth and improve its ability to deliver real-time data processing and insights to customers.

To learn more about ClickHouse and how real-time analytics can elevate your company’s AI development, [sign up for a free trial](https://clickhouse.com/cloud) and join our growing community of developers. And to experience the power of Braintrust for building and optimizing your AI applications, visit <a href="https://www.braintrust.dev?utm_source=clickhouse" target="_blank">braintrust.dev</a>!.
