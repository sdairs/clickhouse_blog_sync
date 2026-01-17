---
title: "Behind the scenes: How ClickHouse helps Vimeo power video analytics at scale"
date: "2024-08-15T13:05:34.097Z"
author: "ClickHouse Team"
category: "User stories"
excerpt: "For nearly 20 years, Vimeo has been a digital video powerhouse, changing the way users upload, share, and enjoy video content online."
---

# Behind the scenes: How ClickHouse helps Vimeo power video analytics at scale

For nearly 20 years, <a href="https://vimeo.com" target="_blank">Vimeo</a> has been a digital video powerhouse, changing the way users upload, share, and enjoy video content online. Initially a hosting platform for general users and video enthusiasts, today the company serves millions of professional creators and businesses, offering advanced tools for video production, distribution, and monetization.

Best-known for its sleek UI and high-quality video streaming, behind the scenes Vimeo runs an extensive backend operation, characterized by enormous data volumes from over a billion videos. According to Zeev Feldbeine, Principal Data Engineer at Vimeo, this infrastructure handles 20 billion micro-events daily — loads, plays, pauses, skips — providing real-time analytics on user behavior and video performance.

Two years ago, Zeev led a transformation of Vimeo’s data architecture, and at a [recent meetup in New York City](/videos/scalable-video-analytics), he shared their journey of adopting ClickHouse. The results are impressive, with huge improvements in query performance, cost efficiency, and overall system reliability.

## Struggling to Scale

In 2021, Vimeo’s existing OLTP infrastructure, built on Apache HBase and Apache Phoenix, was struggling to keep pace with the video platform’s rapid growth. With petabytes of data and billions of micro-events across various dimensions such as device, location, and source, the system was plagued by slow query performance and frequent outages.

“It was a mess,” Zeev says. “Large queries didn’t work. Ten percent of users got timed out. Users couldn’t get the data or analytics they wanted.”

The legacy system’s high operational costs had also become unsustainable. Despite heavy investments in hardware and maintenance, the company faced performance bottlenecks that hurt their ability to scale. As Zeev explains, “We spent a lot of money, we had an insane amount of nodes, and still outages kept happening.”

These issues were compounded by the complexity of Vimeo’s data requirements, with different video types each requiring unique analytics. Live video, in particular, demands low latency for real-time data processing, which the existing infrastructure couldn’t deliver.

“We tried to scale horizontally, but we didn’t get the results we wanted,” Zeev says. “We knew eventually we had to make a change, which finally we did.”

## A Better Data Solution

Zeev and the team kicked off a search for a long-term solution that could meet their data demands. They compared three database management systems — Apache Druid, MemSQL, and ClickHouse — to find the best combination of performance, scalability, and cost efficiency.

After a thorough evaluation that considered factors like query performance, ease of integration, and overall system reliability, ClickHouse emerged as the frontrunner thanks to its reputation for handling large-scale data analytics with lightning-fast speed and efficiency. They decided to run a proof of concept (POC) to fully test ClickHouse’s capabilities.

The POC phase was designed to simulate Vimeo’s real-world data challenges. The team started by stress-testing ClickHouse with a sample set of 25% of their total data, processing large volumes of video analytics, running complex queries, and ensuring the system could handle Vimeo’s high concurrency demands. They tested various scenarios, including data ingestion, query performance under peak loads, and system stability during simulated failures.

“Because we had faced so many outages with HBase, we wanted to make sure ClickHouse could survive any demands we put on it,” Zeev says.

The results of the POC were overwhelmingly positive. ClickHouse not only met but exceeded Vimeo’s expectations in several key areas. Query performance improved by orders of magnitude, running 10 times faster than before. The system proved highly stable, even under heavy loads, while requiring four times fewer servers and three to five times less storage.

“ClickHouse just beat everyone by far,” Zeev says. Confident that it could transform their data operations and handle growing demand, they were ready to move forward with a full-scale implementation of ClickHouse.

## Vimeo’s New Data Architecture

![vimeo-diagram-v2.png](https://clickhouse.com/uploads/vimeo_diagram_v2_7cf901733d.png)

Vimeo’s new data architecture, built on ClickHouse’s columnar storage format, allows for efficient data compression and rapid query execution. The setup is designed to handle high concurrency and massive data volumes, ensuring that real-time analytics are available to all of Vimeo’s users and internal BI teams.

Zeev and the team use ClickHouse’s MergeTree engines to optimize data storage and retrieval, greatly improving performance for complex queries. They’ve also implemented a multi-tier storage strategy, using SSDs for frequently accessed data and HDDs for archival purposes, boosting cost efficiency and speed. By integrating with Apache Spark, they’ve streamlined data ingestion, making it easier to process billions of micro-events daily.

For now, Vimeo is deploying ClickHouse in a self-managed Kubernetes environment on Google Cloud Platform. This setup provides the flexibility to scale resources dynamically based on demand, maintaining high availability and resilience. Zeev and his team have also implemented backup strategies using open-source tools like Velero, while ClickHouse’s replication features ensure data consistency across distributed nodes.

## Benefits Across the Board

Switching to ClickHouse has transformed Vimeo’s data operations and brought major benefits to the business at large. The massive improvement in query performance, with data processing times reduced from minutes to seconds, means Vimeo can offer real-time analytics and a better user experience for content creators and businesses.

The new architecture also comes with big-time cost savings in infrastructure. With significantly fewer resources needed, Vimeo has reduced its operational expenses while maintaining high performance. ClickHouse’s stability has eliminated the frequent outages and timeouts that plagued the old system, ensuring continuous and reliable access to analytics.

“Compared to other solutions we explored and what we had before, ClickHouse just blows them away,” Zeev says. “It’s very, very cheap, and the quality is extremely high.”

Finally, ClickHouse’s scalability allows Vimeo to easily plan for and accommodate future growth. The ability to handle diverse and complex data types with low latency means Vimeo’s product team can keep innovating without being limited by their data infrastructure. This flexibility is essential for meeting the evolving video needs of customers.

## Lights, Camera, ClickHouse

With ClickHouse at the core of their data operations, Vimeo is well-positioned to keep expanding their video platform. By transforming their data architecture, they’ve not only solved critical performance issues but also opened new avenues for innovation and growth.

For Zeev and his team, the switch to ClickHouse has delivered the stability, efficiency, and scalability they needed. “I feel like I could be a great salesman for ClickHouse,” Zeev says with a laugh. “It’s one of the best products I’ve ever worked with.”

To read more about the Vimeo journey, please see the Vimeo Engineering Blog ["ClickHouse is in the house: Insights gained and lessons learned from our long video analytics migration journey"](https://medium.com/vimeo-engineering-blog/clickhouse-is-in-the-house-413862c8ac28). 

Whether you want to improve performance, cut costs, or scale your business efficiently, ClickHouse provides the tools you need to transform your data operations. [Join our growing open-source community](/slack) or [try ClickHouse Cloud free for 30 days](https://clickhouse.cloud/signUp?loc=vimeo-blog).
