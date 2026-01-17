---
title: "Celebrating a Year of Growth"
date: "2023-12-18T12:00:51.869Z"
author: "ClickHouse Team"
category: "Product"
excerpt: "As the year draws to a close, we wanted to express our heartfelt gratitude to you for being part of the ClickHouse Cloud journey."
---

# Celebrating a Year of Growth

<p>As the year draws to a close, we wanted to express our heartfelt gratitude to you for being part of the ClickHouse Cloud journey. Your support has been instrumental in shaping an incredible year of growth, and we&rsquo;re excited to take a moment to reflect on some of the milestones that made 2023 such a remarkable year.&nbsp;</p>

## Launch &amp; Platform Expansion

<p>We launched <a href="https://clickhouse.com/blog/clickhouse-cloud-generally-available" target="_blank" style="color: #faff69 !important;">ClickHouse Cloud</a> on AWS in December 2022 - just over a year ago today. Six months later, in June 2023, , we expanded our availability to <a href="https://clickhouse.com/blog/clickhouse-cloud-on-google-cloud-platform-gcp-is-generally-available" style="color: #faff69 !important;">Google Cloud</a> in three geographies, with Azure support in the works for 2024. Since then, we&rsquo;ve continued rolling out new region support, with <a href="https://clickhouse.com/docs/en/cloud/reference/supported-regions" style="color: #faff69 !important;">12 available</a> across platforms today.&nbsp;</p>
<p>We introduced a new service type - <a href="https://clickhouse.com/pricing" style="color: #faff69 !important;">Dedicated Instances</a>, designed for customers who are looking for advanced isolation and protection of data, as well as predictable performance. This service type provides maximal flexibility when it comes to configurations, to ensure the setup is the right fit for your workload. With a Dedicated Service, customers also have the flexibility to define maintenance windows for upgrades. If you&rsquo;re interested in learning more, please <a href="https://clickhouse.com/company/contact" style="color: #faff69 !important;">let us know!</a></p>

![map-regions.png](https://clickhouse.com/uploads/map_regions_a4af1bd92a.png)

## Scale and Performance Optimizations

<p>Throughout 2023, we made several performance improvements and optimizations to ClickHouse, including the introduction of a brand-new Engine, SharedMergeTree (SMT). <a href="https://clickhouse.com/docs/en/cloud/reference/shared-merge-tree" style="color: #faff69 !important;">SharedMergeTree</a> is optimized for shared storage, the basis for our ClickHouse Cloud architecture, and results in significantly improved insert throughput and background operations performance compared to our other Engines. We haven&rsquo;t forgotten about our scaling algorithms, either! We&rsquo;ve made diligent enhancements across vertical, horizontal, and CPU-based scaling, too.</p>

## Analyst Productivity

<p>We&rsquo;ve introduced several new capabilities to our SQL Console experience that make writing and debugging queries a lot smoother.</p>

<p style="margin-bottom: 5px !important;"><img src="/uploads/compressed_cut_rag_c420958463.gif" alt="compressed_cut_rag_c420958463.gif" class="h-auto w-full max-w-full"></p>
<p style="font-style: italic !important; text-align: center !important;">AI-based Query Suggestions</p>

<p>We additionally released API support to programmatically manage your ClickHouse Cloud lifecycle operations, as well as a <a href="https://registry.terraform.io/providers/ClickHouse/clickhouse/latest" style="color: #faff69 !important;">Terraform Provider</a> to ease deployment automation.</p>

## Integrations

<p>It has been a busy year on the integrations front!</p>
<p>In September, we announced the general availability of <a href="https://clickhouse.com/cloud/clickpipes" style="color: #faff69 !important;">ClickPipes</a>, a turnkey data ingestion service for ClickHouse Cloud. Initially focused on streaming data with support for Apache Kafka, Confluent Cloud, and Amazon MSK, we are currently working on expanding the list of available connectors to include more data sources.</p>
<p>Our 2023 integrations milestones included ClickHouse ecosystem focused releases, such as:</p>
<ul>
<li>GA of our official <a href="https://github.com/ClickHouse/clickhouse-kafka-connect" style="color: #faff69 !important;">Kafka Connect Sink</a></li>
<li>Support for the <a href="https://clickhouse.com/blog/clickhouse-cloud-compatible-with-mysql" style="color: #faff69 !important;">MySQL protocol in ClickHouse Cloud</a> (read more about our <a href="https://clickhouse.com/blog/mysql-support-in-clickhouse-the-journey" target="_blank" style="color: #faff69 !important;">behind the scenes journey here</a>)</li>
<li>Improved and upgraded <a href="https://github.com/ClickHouse/dbt-clickhouse" style="color: #faff69 !important;">ClickHouse dbt adapter</a></li>
<li>Several enhancements to the <a href="https://github.com/ClickHouse/clickhouse-connect" style="color: #faff69 !important;">Python</a>, <a href="https://github.com/ClickHouse/clickhouse-js" target="_blank" style="color: #faff69 !important;">JS</a>, <a href="https://github.com/ClickHouse/clickhouse-go" style="color: #faff69 !important;">Golang</a>, and <a href="https://github.com/ClickHouse/clickhouse-java" style="color: #faff69 !important;">Java</a> language clients</li>
<li>Improvements to plugins including <a href="https://clickhouse.com/blog/introduction-to-clickhouse-and-grafana-webinar" style="color: #faff69 !important;">Grafana</a>, <a href="https://clickhouse.com/blog/metabase-clickhouse-plugin-ga-release" style="color: #faff69 !important;">Metabase</a>, <a href="https://clickhouse.com/blog/visualizing-data-with-superset" style="color: #faff69 !important;">Superset</a>, <a href="https://github.com/ClickHouse/power-bi-clickhouse" style="color: #faff69 !important;">PowerBI Desktop (Beta)</a>, and more</li>
</ul>

## Security

<p>Our continued commitment to data privacy and security is central to every part of our business and has driven significant ClickHouse milestones this year.&nbsp;</p>
<p><span style="text-style: underline;">Data at Rest Protection:</span> We introduced support for Customer Managed Encryption Keys (CMEK) for custom data-at-rest encryption and key rotation. This is available for production services deployed in AWS.&nbsp;</p>
<p><span style="text-style: underline;">Endpoint Security:</span> We released support for secure endpoints with Private Link in AWS and Private Service Connect in GCP.</p>
<p><span style="text-style: underline;">S3 Access Security:</span> We've enhanced security by enabling secure access to private S3 buckets using AWS assumed IAM roles.</p>
<p><span style="text-style: underline;">Compliance:</span> ClickHouse Cloud is certified for SOC 2 Type II and ISO 27001. You can read more on our compliance and certifications <a href="https://clickhouse.com/docs/en/manage/security/compliance-and-certification" style="color: #faff69 !important;">here</a>, and request access to these reports in our <a href="https://trust.clickhouse.com" target="_blank" style="color: #faff69 !important;">ClickHouse Trust Center.</a></p>

## Cloud Change Log

<p>And that&rsquo;s not all! We have several other releases and improvements that you can read about on our <a href="https://clickhouse.com/docs/en/whats-new/cloud" style="color: #faff69 !important;">change log</a>.</p>

## Customer Spotlights

<p>&ldquo;At Lyft, we ingest tens of millions of rows and execute millions of read queries in ClickHouse daily with volume continuing to increase. On a monthly basis, this means reading and writing more than 25TB of data.&rdquo; <a href="https://eng.lyft.com/druid-deprecation-and-clickhouse-adoption-at-lyft-120af37651fd" style="color: #faff69 !important;">Read more</a> about Lyft&rsquo;s migration to ClickHouse.</p>
<p>&ldquo;We had prototyped something in BigQuery &hellip; but we were seeing 15, 20, 25 second response times.&rdquo; Hear about how <a href="https://clickhouse.com/videos/clearbit" style="color: #faff69 !important;">Clearbit achieved a 10x cost reduction</a> moving from Postgres to ClickHouse, and how their evaluation of BigQuery as a solution was resulting in double digit response times.&nbsp;&nbsp;</p>
<p>"Moving over to ClickHouse we were basically able to cut that (Redshift) bill in half." Brooke, Co-founder and CTO of Vantage, shares how <a href="https://clickhouse.com/videos/vantage" style="color: #faff69 !important;">transitioning to ClickHouse</a> not only optimized Vantage's operations but also dramatically reduced their costs.</p>

##  Continued Reading

<ul>
<li><a href="https://clickhouse.com/blog/the-unbundling-of-the-cloud-data-warehouse" style="color: #faff69 !important;">The Unbundling of the Cloud Data Warehouse</a></li>
<li><a href="https://clickhouse.com/blog/the-state-of-sql-based-observability" style="color: #faff69 !important;">The State of SQL-based Observability</a></li>
<li><a href="https://clickhouse.com/blog/escape-rising-costs-of-snowflake-speed-and-cost-savings-clickhouse-cloud" style="color: #faff69 !important;">Escape from Snowflake's Costs</a></li>
</ul>
<p>With that, we want to close by extending our deepest appreciation for your support and partnership this year. We couldn't have asked for a better community to grow with.&nbsp;</p>
<p>We hope you have a wonderful and joyous holiday season!&nbsp;</p>

**Has your ClickHouse Cloud trial ended, but you still have more to explore? [Let us know](/company/contact?loc=year-in-review-2023) and we'll extend your FREE trial.**