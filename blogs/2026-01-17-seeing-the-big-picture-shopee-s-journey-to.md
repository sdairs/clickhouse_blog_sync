---
title: "Seeing the Big Picture: Shopee’s Journey to Distributed Tracing with ClickHouse"
date: "2024-06-13T10:50:08.448Z"
author: "ClickHouse Team"
category: "User stories"
excerpt: "As Southeast Asia’s leading ecommerce platform, Shopee handles millions of transactions and huge amounts of data each day."
---

# Seeing the Big Picture: Shopee’s Journey to Distributed Tracing with ClickHouse

<blockquote>
<p style="margin-bottom:5px">"Adopting ClickHouse has enhanced our data analytics capabilities, supporting the growing demands of our internal teams efficiently and cost-effectively."</p><p style="font-weight: bold;">Frank Chen, Expert OLAP Engineer @ Shopee</p>
</blockquote>


<iframe width="768" height="432" src="https://www.youtube.com/embed/_BVy-V2wy9s" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>


<p>&nbsp;</p>


As Southeast Asia’s leading ecommerce platform, <a href="https://shopee.com/?utm_source=clickhouse" target="_blank">Shopee</a> handles millions of transactions and huge amounts of data each day. To ensure smooth operations and a top-notch user experience, understanding system performance and diagnosing issues quickly is crucial.



Four years ago, Shopee engineer Frank Chen and his team recognized the challenges posed by their rapidly growing platform. They had earlier introduced ClickHouse as an OLAP database management system. After it was widely adopted to serve a variety of business needs, they decided to use ClickHouse to implement a technique called distributed tracing. Since then, it has supported hundreds of internal projects geared at ensuring high performance and reliability, transforming Shopee’s approach to data management and system observability.

“Adopting ClickHouse has enhanced our data analytics capabilities, supporting the growing demands of our internal teams efficiently and cost-effectively,” Frank says.


## Gaining Clarity

Managing data efficiently in a complex microservices architecture is no small feat. Distributed tracing is a technique that provides visibility by monitoring and tracking requests as they travel through various services within a system. This visibility is essential for quickly identifying and addressing performance bottlenecks or errors, and ensuring smooth operations.

For Shopee, distributed tracing provides an in-depth view of how data flows across their ecommerce platform. These real-time insights allow hundreds of internal users to pinpoint exactly where delays or failures occur, make informed decisions, and implement fixes that enhance the platform’s overall performance and reliability.


## A Growing Challenge

In 2020, Shopee was growing rapidly, spurred in part by the COVID-19 pandemic. As daily transactions surged, the platform’s engineers faced a growing number of user queries around latency, failures, and inconsistent responses — issues that could seriously disrupt user experience and operational efficiency if not addressed.

The data engineering team recognized that Shopee’s existing data management solutions were insufficient for the scale and complexity of the challenges they were facing. Understanding the root causes would require detailed diagnostics capable of efficiently managing vast amounts of data and asynchronous processes. They decided to develop a more robust, scalable solution to maintain and improve their service quality — one that could provide comprehensive insights into the system’s performance and help Shopee’s engineers manage data more effectively.


## The Right Tool for the Job

In their search for the right solution, Frank and his team evaluated several database management systems. They had previously relied on database engines like Druid, Hive, and Presto; but while these systems offered advantages in certain areas, they had specific limitations and fell short in supporting the nuanced needs of distributed tracing. 

After introducing ClickHouse as an OLAP DBMS and experiencing its strengths, they decided to further explore its potential. Extensive testing and comparison showed that ClickHouse outperformed other solutions like Elasticsearch in three key areas: performance, compatibility, and cost-efficiency for large-scale operations.

“ClickHouse is very fast and excels at handling high cardinality calculations, providing rapid query responses,” Frank says. “Unlike Elasticsearch, ClickHouse supports MySQL-compatible SQL and JDBC, lowering the learning curve for users familiar with these databases. And it has lower hardware requirements, optimizing both memory and disk consumption.”

The open-source nature of ClickHouse also played a role. It not only aligned with Shopee’s engineering ethos but allowed their team to modify and improve the database to fit their specific needs. This flexibility added to a sense of community and shared innovation among Shopee’s engineers, helping them solve difficult data processing problems together.


## Implementing ClickHouse

The implementation involved multiple components of Shopee’s infrastructure, and included the development of several fully managed ClickHouse services to ensure efficient data handling and system observability for Shopee’s engineers:


* **ClickHouse Manager**: Streamlines resource allocation and cluster deployment, ensuring each service has the required computational power and storage.

* **ClickHouse Gateway**: Acts as the entry point for all incoming queries, efficiently routing them to the appropriate clusters for precise and rapid processing. 

* **ClickHouse Console**: Offer a web-based interface for managing queries, allowing engineers to perform ad hoc queries and manage data easily. 

* **ClickHouse Monitoring**: Provides real-time monitoring and alerts for the ClickHouse infrastructure, including distributed tracing to track data flow and quickly resolve performance issues.


![shopee-diagram.png](https://clickhouse.com/uploads/shopee_diagram_267fe63c2f.png)


At the core of Shopee’s ClickHouse infrastructure are dozens of ClickHouse clusters, including several cluster types each optimized for different data processing needs:


* **ClickHouse MPP SSD on K8S**: Uses Massively Parallel Processing (MPP) on SSD storage within Kubernetes environments for fast data processing of high-priority tasks.
* **ClickHouse MPP HDD on K8S**: Uses HDD storage for less time-sensitive tasks, leveraging cost-effectiveness without sacrificing functionality.
* **ClickHouse Computing and Storage Separation on K8S**: Separates computing and storage resources using ClickHouse’s zero-copy feature for scalable, flexible resource allocation. Shopee uses Apache OZone as the S3-compatible storage service, leveraging its HDFS integration for efficient data management.
* **ClickHouse Cold & Hot Separation Storage**: Optimizes storage by categorizing data into frequently accessed (hot) and less accessed (cold) types, improving performance while reducing costs.

Implementing ClickHouse was a meticulous process that required careful planning and execution. The end result for Shopee’s hundreds of internal users is a robust system that not only addressed short-term needs but laid a strong foundation for future scalability.


## Distributed Tracing in Action

Shopee’s implementation of ClickHouse has made a huge impact. With distributed tracing, the engineering team can monitor and optimize data flows in real-time, with visibility into system operations that allows them to quickly identify and resolve bottlenecks. 

Here’s how they’ve done it:

* **Trace and Span Management**: Shopee uses unique identifiers to monitor queries effectively. Each trace consists of multiple spans, representing distinct units of work within a query. By managing these traces and spans, the engineering team can follow the lifecycle of each request, identifying where and why delays or errors occurred.

* **Context Propagation**: Maintaining tracing context across different services and threads is essential. Shopee ensures that the tracing context is propagated consistently as requests travel through various microservices. This continuity allows for a comprehensive view of the entire request path, making it easier to pinpoint issues.

* **Data Storage and Processing**: Shopee uses ClickHouse’s system tables and materialized views for efficient data handling. System tables store internal states and logs, while materialized views provide pre-computed results to speed up query processing. This setup ensures that data is not only stored efficiently but is also readily accessible for real-time analysis.

“We now ingest up to 3 million rows per second using just 20 CPU cores on the ClickHouse server, achieving a 1:8 compression ratio without any tuning,” Frank says. “For data stored on SSDs, the time to search a specific trace ID from a dataset of over 30 billion rows on one ClickHouse instance is measured in mere seconds.”


## Real-World Wins

Distributed tracing has helped Shopee identify and address a variety of challenges, leading to significant improvements in system performance and reliability.


### 1. Identifying the Bottleneck

In one instance, Shopee found that the response time for a query was 118 seconds. Using distributed tracing, they determined that the majority of this time was spent on the ClickHouse Gateway side rather than the ClickHouse side. Further investigation revealed that the client was sending data to ClickHouse very slowly. By enabling data compression on the client side, they were able to reduce the payload size and speed up response times.

### 2. Solving Network Problems

Shopee received feedback about inconsistent query responses. In one example, tracing logs helped them identify that a request was being misrouted due to a DNS cache problem in Kubernetes. Fixing the DNS cache issue ensured that queries were routed correctly, maintaining the integrity and accuracy of the data processing pipeline.

### 3. Understanding Distributed Joins

The complexity of distributed joins can strain system resources. Distributed tracing provides a clear visualization of how these joins are executed. By adjusting settings, Shopee’s engineers were able to streamline this process, issuing fewer subqueries and improving overall performance. This optimization made the queries simpler and more efficient.

### 4. Diagnosing Query Timeouts

Distributed tracing helped Shopee’s team find and fix DDL timeout issues. For example, tracing logs showed that one database server was taking longer to process a query than others. Further investigation found that the delay was caused by a blocking DDL operation on that specific node. Resolving this bottleneck ensured smoother, more reliable data operations.

### 5. Troubleshooting Materialized Views

Users sometimes reported that their INSERT queries failed with errors seemingly unrelated to the target table. Shopee’s distributed tracing logs revealed that these failures were actually caused by issues within materialized views. By diagnosing and fixing these issues, Shopee made the data insertion process more reliable and efficient.

“ClickHouse is a super fast and powerful analytics database that can lower users’ hardware costs,” Frank says. “It’s versatile enough for various applications, from fraud detection and user behavior analysis to log and metrics storage. In many scenarios, it can even replace traditional databases like MySQL or search engines like Elasticsearch.”


## Built to Scale

As Shopee continues to expand its ecommerce platform, powering millions of transactions in nearly a dozen countries and territories across Southeast Asia, distributed tracing allows its engineers to stay on top of performance issues and ensure smooth operations. ClickHouse has been pivotal to the company’s data management and overall business success, allowing Shopee to handle more transactions without compromising quality.

“Four years ago, we chose ClickHouse for its speed and performance,” Frank says. “Since then, it has become the backbone for all of our data applications.”

Shopee’s journey with ClickHouse is just the beginning. With ClickHouse’s open-source database at the core of its data management system, Shopee is well-equipped to keep scaling and innovating. To learn more about how ClickHouse can elevate your company’s data capabilities, [download ClickHouse](https://clickhouse.com/docs/en/getting-started/quick-start) and join our growing community of developers.

Slides from the presentation can be [seen here](https://github.com/ClickHouse/clickhouse-presentations/blob/2b0ef2914ff594c0a0f8800d5150e5b31323be98/meetup105/Shopee%20-%20Distributed%20Tracing%20in%20ClickHouse.pdf).
