---
title: "Why Flock Safety turned to ClickHouse for real-time vehicle traffic analytics"
date: "2025-04-28T23:27:27.633Z"
author: "ClickHouse Team"
category: "User stories"
excerpt: "“With ClickHouse, our customers now have real-time analytics for their camera traffic, and there are no more constraints on size or row-level security.” ~ Leon Kozlowski, Data Engineering Manager"
---

# Why Flock Safety turned to ClickHouse for real-time vehicle traffic analytics

<p>
<a href="https://www.flocksafety.com/">Flock Safety</a> is on a mission to make communities safer. Founded in Atlanta in 2017, their products include automated license plate readers, video cameras, and gunfire detection systems, all designed to deter crime and aid criminal investigations. Today, Flock Safety serves over 5,000 communities nationwide, with customers ranging from law enforcement agencies to neighborhood associations to major businesses.
</p>
<p>
Beyond hardware, the company offers a suite of software solutions, including a <a href="https://www.flocksafety.com/traffic-analytics-business">traffic analytics platform</a> that builds on their popular license plate recognition technology. It provides aggregated vehicle counts, delivering insights to help customers optimize security staffing, operations, and traffic safety. 
</p>
<p>
“This unlocks a lot of potential for customers to look at insights based on the images that their cameras are capturing,” says Leon Kozlowski, data engineering manager at Flock Safety.
</p>
<p>
But scaling any data platform comes with challenges, like long refresh times, size constraints, and data availability.
</p>
<p>
At a <a href="https://www.youtube.com/watch?v=dN4yrzn8Td4">December 2024 ClickHouse meetup in New York City</a>, Leon described Flock Safety’s search for a better data architecture — a journey that led them to <a href="https://clickhouse.com/cloud">ClickHouse Cloud</a>.
</p>
<h2>The analytics bottleneck</h2>


<p>
Flock Safety’s original analytics pipeline relied on Amazon Redshift, DBT, and Prefect, with Amazon QuickSight’s SPICE layer handling dashboards. Data was shared from a provisioned Redshift cluster to a Redshift Serverless instance, where DBT and Prefect transformed it into analytics models. From there, the processed data was synced into SPICE, an in-memory database that powered QuickSight reports. While this setup offered a structured way to process large volumes of data, it came with limitations that made real-time insights impossible.
</p>
<p>


![FS1.png](https://clickhouse.com/uploads/FS_1_b8ad7ac621.png)
<p style="text-align: center">
Flock Safety’s pre-ClickHouse data architecture.
<p/>

The first challenge was the daily refresh cadence. “The transformation layer only ran once a day, both because of the volume of data and the way our architecture was designed to surface that data to customers,” Leon says. This meant customers could only see updates from the previous day or earlier. “They had no intraday context into their data,” he adds.
</p>
<p>
Then came the issue of long refresh times. Syncing data into SPICE was slow, with some datasets taking up to four hours to process. “This was probably the biggest issue with the old architecture,” Leon says. During that window, data was completely unavailable, leaving customers stuck with outdated information. As a workaround, the team ran refreshes overnight to minimize disruptions, but as Leon notes, “That type of downtime is really not going to be tolerated, especially for law enforcement customers.”
</p>
<p>
Size constraints compounded the problem. SPICE had a hard limit of 1TB or 1 billion rows per dataset. Customers weren’t just missing real-time updates — they were losing valuable historical insights.
</p>
<h2>The search for a better architecture</h2>


<p>
Recognizing the limitations of their existing setup, Leon and the team set out to find an architecture that could support real-time analytics at scale without sacrificing performance.
</p>
<p>
They first explored running direct queries on Redshift instead of syncing data into SPICE. The goal was to speed up queries by removing the in-memory later. However, as Leon points out, “The concurrency limits on Redshift meant this wasn’t a scalable approach.”
</p>
<p>
Next, they tested Aurora PostgreSQL, thinking its transactional capabilities might offer better performance. The idea was to sync data from Redshift into Aurora and run QuickSight queries directly. But the results were even worse: “This wasn’t even able to return data to the caller within the timeout specified by Amazon QuickSight,” Leon explains. If a query couldn’t return results without timing out, it wasn’t a viable solution for Flock Safety’s customers.
</p>
<p>
They then turned to S3 and Trino, attempting to use Trino’s federated queries on data stored in S3. This approach took some “funky partitioning” to optimize query performance, but even with aggressive tuning, the system still struggled under load. Like Aurora, Trino queries frequently exceeded timeout limits. After testing multiple configurations, Leon says that “these three options definitely were not viable for the SLA we want to provide to our customers.”
</p>
<p>
Finally, they turned to ClickHouse. With its <a href="https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/aggregatingmergetree">AggregatingMergeTree</a> tables and <a href="https://clickhouse.com/docs/en/materialized-view">materialized views</a>, the database provided “real-time data with direct queries to ClickHouse, rather than using SPICE,” Leon says. The difference could be seen right away: queries were fast, data was available at all times, and they could extend retention without worrying about in-memory constraints. After a rigorous POC, ClickHouse was the clear winner.
</p>
<h2>Flock Safety’s new data pipeline</h2>


<p>
Flock Safety’s new ClickHouse-based architecture starts with ingestion. Images captured by the company’s cameras are sent to the cloud, where machine learning models extract metadata such as vehicle type, make, and license plate state. This information is then pushed to Amazon Simple Notification Service (SNS), which triggers Amazon Kinesis Data Firehose to deliver the structured data into Amazon S3. At the same time, transactional data from RDS databases is streamed via Debezium into the same S3 storage layer. 
</p>
<p>
From there, <a href="https://clickhouse.com/cloud/clickpipes">ClickPipes</a> ingests data into ClickHouse. “It’s extremely performant, with very low latency,” Leon says of ClickPipes. “This architecture has been very scalable in getting data into ClickHouse.” At its peak, ClickPipes processes over 20 MB per second, allowing Flock Safety’s traffic analytics platform to handle over 1 billion ML predictions per day with zero downtime.
</p>
<p>


![FS2.png](https://clickhouse.com/uploads/FS_2_71691c1bbb.png)

</p>
<p style="text-align: center">
Data ingestion in Flock Safety’s new ClickHouse-based architecture.
</p>
<p>
Data transformation occurs automatically upon ingestion into ClickHouse. ML predictions are inserted into dedicated tables, and materialized views use <a href="https://clickhouse.com/docs/en/sql-reference/data-types/aggregatefunction">AggregateFunction </a>data types with functions like uniqState to precompute key metrics for simpler queries. “This means there’s no more need for DBT or Prefect to orchestrate any of these transformations,” Leon says. Aggregated data is then stored in AggregatingMergeTree destination tables, supporting fast, real-time queries without the need for batch processing.
</p>
<p>
From there, the data is enriched with additional context. <a href="https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/replacingmergetree">ReplacingMergeTree</a> dimension tables store metadata like camera locations and organization-level access rules. With this structure, Amazon QuickSight queries ClickHouse directly, bypassing SPICE’s limitations and ensuring that users always see the most up-to-date information.
</p>
<p>

![FS3.png](https://clickhouse.com/uploads/FS_3_dcfa9ecffd.png)

</p>
<p style="text-align: center">
ClickHouse’s table structure and integration with Amazon QuickSight.
</p>
<p>
Flock Safety’s transition to ClickHouse was surprisingly smooth, Leon says, thanks to its compatibility with existing ingestion processes. “If anything, the challenge was getting ramped up on table architectures like ReplacingMergeTree and AggregatingMergeTree, but we got a lot of help from Jake, Larry, Shri, and the ClickHouse Cloud team.”
</p>
<h2>Real-time insights, safer communities</h2>


<p>
Switching from Redshift to ClickHouse Cloud has delivered huge benefits for Flock Safety’s traffic analytics platform. Removing SPICE eliminated downtime, giving customers 24/7 access to the latest data. Now, instead of waiting for daily refreshes, customers can see real-time traffic trends as they happen. Queries that once took minutes now complete in under five seconds, even for the platform’s largest customers.
</p>
<p>
ClickHouse has also unlocked long-term data retention. With ClickHouse Cloud’s scalable architecture, they can store significantly more  traffic count data, giving customers richer insights and deeper trend analysis.
</p>
<p>
Leon describes the difference as night and day. “With ClickHouse, our customers now have real-time analytics for their camera traffic, and there are no more constraints on size or row-level security.” With a scalable, high-performance database, Flock Safety can keep expanding its analytics capabilities, helping communities stay safer with smarter, data-driven decisions.
</p>
<p>
To learn more about ClickHouse and see how it can improve the speed and scalability of your team’s data operations, <a href="https://clickhouse.com/cloud">try ClickHouse Cloud free for 30 days</a>.
</p>