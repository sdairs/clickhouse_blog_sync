---
title: "ClickHouse at AWS re:Invent 2024 - Product Announcement Roundup"
date: "2024-11-26T10:22:16.613Z"
author: "The ClickHouse Team"
category: "Product"
excerpt: "We are excited to join AWS re:Invent this year and have a series of product announcements around the event."
---

# ClickHouse at AWS re:Invent 2024 - Product Announcement Roundup

We are excited to join AWS re:Invent this year! 

In addition to throwing an incredible [\[Click\]House Party](https://clickhouse.com/houseparty/vegas-2024), we are making a score of product announcements: 

<style>
.mini-heading {
    font-weight:600;
}    
</style>

<ul>

<li>
<a href="/blog/reinvent-2024-product-announcements#bring-your-own-cloud-deployment-for-aws-beta" class="mini-heading">Bring-Your-Own-Cloud deployment for AWS (Beta)</a>
</li>

<li>
<a href="/blog/reinvent-2024-product-announcements#integrate-rds-postgres-and-clickhouse-cloud-with-postgres-cdc-connector-in-clickpipes-private-preview" class="mini-heading">Postgres CDC connector in ClickPipes (Private Preview)</a>
</li>

<li>
<a href="/blog/reinvent-2024-product-announcements#cross-vpc-resource-access-through-aws-privatelink-and-vpc-lattice-launch-partner" class="mini-heading">AWS PrivateLink and VPC Lattice (Launch Partner)</a>
</li>

<li>
<a href="/blog/reinvent-2024-product-announcements#dashboards-beta" class="mini-heading">Dashboards (Beta)</a>
</li>

<li>
<a href="/blog/reinvent-2024-product-announcements#query-api-endpoints-ga" class="mini-heading">Query API Endpoints (GA)</a>
</li>

<li>
<a href="/blog/reinvent-2024-product-announcements#native-json-support-beta" class="mini-heading">Native JSON support (Beta)</a>
</li>

<li>
<a href="/blog/reinvent-2024-product-announcements#vector-search-using-vector-similarity-indexes-early-access" class="mini-heading">Vector search using vector similarity indexes (Early Access)</a>
</li>

</ul>

Please read the summary below and come by our booth #1737 to find out more!

## Bring-Your-Own-Cloud deployment for AWS (Beta)

We are excited to announce the Beta launch of Bring-Your-Own-Cloud (BYOC) for AWS! 

This new deployment model allows you to deploy and run ClickHouse Cloud in your own AWS account, giving you the best of both worlds: the performance, scalability, and simplicity of ClickHouse Cloud with the control and security of running in your own environment. No need to worry about managing setup, scaling, or upgrades—we handle it all for you.

This deployment is designed for customers with stringent data residency and security requirements, such as financial services, cybersecurity, healthcare, and other industries that manage PII or other sensitive information and need to comply with advanced data protection requirements. We support deployments in 11+ [AWS regions](https://clickhouse.com/docs/en/cloud/reference/supported-regions#aws-regions) with more coming soon! 

![0_reinvent.png](https://clickhouse.com/uploads/0_reinvent_380869ad8b.png)

<p>&#x1F449; <strong><a href="https://clickhouse.com/cloud/bring-your-own-cloud">Join the BYOC waitlist</a></strong></p>

## Integrate RDS Postgres and ClickHouse Cloud with Postgres CDC connector in ClickPipes (Private Preview) 

We are excited to announce the private preview of the Postgres Change Data Capture (CDC) connector in ClickPipes! 

This turnkey integration enables customers to replicate their Postgres databases to ClickHouse Cloud in just a few clicks and leverage ClickHouse for blazing-fast analytics. You can use this connector for both continuous replication and one-time migrations from Postgres. This integration eliminates the need for external ETL tools, which are often expensive, slow, and do not scale for Postgres. With features like parallel snapshotting, you can achieve 10x faster initial loads and replication latency as low as a few seconds for continuous replication (CDC).

The Postgres CDC connector for ClickPipes supports any Postgres database, whether running in the cloud or on-premise, as a data source—including [AWS RDS for PostgreSQL](https://aws.amazon.com/rds/postgresql/). In fact, RDS Postgres is the most commonly used data source among our customers. This includes customers such as [SpotOn](https://www.spoton.com/), [Vueling](https://www.vueling.com/), [Daisychain](https://www.daisychain.app/) and others already integrating their RDS Postgres databases with ClickHouse Cloud using this connector.

![1_reinvent.png](https://clickhouse.com/uploads/1a_reinvent_5b2aeae5c3.png)

This launch marks a major milestone following the [PeerDB acquisition](https://clickhouse.com/blog/clickhouse-welcomes-peerdb-adding-the-fastest-postgres-cdc-to-the-fastest-olap-database), made just a few months ago, for a native integration of Postgres with ClickHouse. It builds on a common trend across customers like [GitLab](https://about.gitlab.com/blog/2022/04/29/two-sizes-fit-most-postgresql-and-clickhouse/), [LangChain](https://clickhouse.com/blog/langchain-why-we-choose-clickhouse-to-power-langchain), [Cloudflare](https://blog.cloudflare.com/http-analytics-for-6m-requests-per-second-using-clickhouse/) and [Instacart](https://tech.instacart.com/real-time-fraud-detection-with-yoda-and-clickhouse-bd08e9dbe3f4) that rely on Postgres and ClickHouse to address most of their data challenges. Postgres powers their mission-critical transactional and web applications, while ClickHouse powers analytics. Both are purpose-built databases designed for distinct workloads and share the same Open Source ethos. With the release of the Postgres CDC connector, we are making the Postgres + ClickHouse integration even easier for customers.

<p>&#x1F449; <strong><a href="https://clickhouse.com/cloud/clickpipes/postgres-cdc-connector">Sign up for the private preview</a></strong></p>

## Cross-VPC resource access through AWS PrivateLink and VPC Lattice (Launch Partner)

We are proud to announce that we are an AWS Launch Partner for Cross-VPC resource access with PrivateLink and VPC Lattice! 

With ClickPipes, you can now grant uni-directional access to a specific data source like AWS MSK. With Cross-VPC resource access with AWS PrivateLink and VPC Lattice, you can share individual resources across VPC and account boundaries, or even from on-premise networks without compromising on privacy and security when going over a public network.

![2_reinvent.png](https://clickhouse.com/uploads/2a_reinvent_bbccb49ee1.png)

Supporting this new PrivateLink feature coincides with our most recent accreditation status as a AWS PrivateLink Service Ready Partner. We went through a stringent validation process with the AWS team to demonstrate our technical capabilities, verification of our solution and security processes, so you can be sure the integration is robust. Our new integration with PrivateLink and VPC Lattice further enhances our dedication to giving you the best and most secure ClickHouse experience on AWS.

<p>&#x1F449; <strong>To get started and set up a resource share, you can read the <a href="https://clickhouse.com/blog/clickpipes-crossvpc-resource-endpoints" >announcement blog post</a></strong> that walks you through how to configure Cross-VPC resource access through PrivateLink and VPC Lattice.</p>

## Dashboards (Beta)

![3_reinvent.png](https://clickhouse.com/uploads/3_reinvent_b0ed0d0c7f.png)

We are excited to announce the Beta launch of Dashboards in ClickHouse Cloud! 

With this new capability, you can use the most powerful real-time database to visualize and share your data across your organization. ClickHouse Cloud’s SQL console allows users to query data using saved queries. With Dashboards, users can turn saved queries into visualizations, organize visualizations onto dashboards, and interact with dashboards using [query parameters](https://clickhouse.com/docs/en/sql-reference/syntax#defining-and-using-query-parameters). 

We hope that ClickHouse Cloud native Dashboards will help you to expand access to your real-time data. 

<p>&#x1F449; <strong>To get started follow <a href="https://clickhouse.com/docs/en/cloud/manage/dashboards">the dashboards documentation</a></strong></p>

## Query API Endpoints (GA)

![4_reinvent.png](https://clickhouse.com/uploads/4_reinvent_7dd1562cc8.png)

We are excited to announce the GA release of Query API Endpoints in ClickHouse Cloud!

Already used in production by customers with thousands of active endpoints serving millions of requests daily, Query API Endpoints allow you to spin up RESTful API endpoints for saved queries in just a couple of clicks and begin consuming data in your application without wrangling language clients or authentication complexity.  Our [blog post announcing the beta launch](https://clickhouse.com/blog/automatic-query-endpoints) describes the core functionality in greater detail, but since the initial launch, we have shipped a number of improvements including:

* Reducing endpoint latency, especially for cold-starts  
* Increased endpoint RBAC controls  
* Configurable CORS-allowed domains  
* Result streaming  
* Support for all ClickHouse-compatible output formats

In addition to these improvements, we are excited to announce *generic query API endpoints* that, leveraging our existing framework, allow you to execute arbitrary SQL queries against your ClickHouse Cloud service(s).  Generic endpoints can be enabled and configured from the service settings page.  

…and that’s not all! In the near term, we are planning to add support for programmatic creation and management of endpoints (via Cloud API and Terraform), version control, cache configuration, and more latency reductions. As always, please reach out to us with any feedback or feature requests!

<p>&#x1F449; <strong>To get started follow <a href="https://clickhouse.com/docs/en/get-started/query-endpoints">the Query API Endpoints documentation</a></strong></p>

## Native JSON support (Beta)

We are launching the Beta of native JSON support in ClickHouse Cloud!

The native JSON support feature received a dizzying amount of interest from our community recently—and for good reason! It’s a powerful addition that makes it much easier to migrate from systems like [Elasticsearch](https://clickhouse.com/blog/clickhouse_vs_elasticsearch_the_billion_row_matchup) or [Rockset](https://clickhouse.com/comparison/rockset), and also to load JSON data directly to ClickHouse. 

![5_reinvent.png](https://clickhouse.com/uploads/5_reinvent_f033e1a015.png)

Building this feature was no small task. It relied on multiple foundational components, such as the dynamic and variant data types, to handle its complexity, you can read more about it in our recent blog post, [How we built a new powerful JSON data type for ClickHouse](https://clickhouse.com/blog/a-new-powerful-json-data-type-for-clickhouse). For this reason, we initially released it as experimental and conducted a private preview with selected customers. The feedback we received has been very positive. It helped us enrich the feature roadmap and gave us a lot of confidence in moving it to [beta](https://github.com/ClickHouse/ClickHouse/pull/72294) so more users can start taking advantage of it.

<p>&#x1F449; <strong>To get started, please <a href="https://clickhouse.com/docs/en/cloud/support">contact support</a> to enable on your cloud service.</strong></p>

## Vector search using vector similarity indexes (Early Access)
Last, but certainly not least – we are announcing vector similarity indexes for approximate vector search in early access!

ClickHouse already offers robust support for vector-based use cases, with a wide range of [distance functions](https://clickhouse.com/docs/en/sql-reference/functions/distance-functions) and the ability to perform linear scans. In addition, more recently we added an experimental [approximate vector search approach](https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/annindexes) powered by the [usearch](https://github.com/unum-cloud/usearch) library and the Hierarchical Navigable Small Worlds (HNSW) approximate nearest neighbor search algorithm. Today, we are excited to announce that this feature is soon entering Beta in ClickHouse Cloud, and we are opening early access registration for users to test it on their own data. 

![6_reinvent.png](https://clickhouse.com/uploads/6_reinvent_c6579d4aa9.png)

<p>&#x1F449; <strong>To get started, please <a  href="https://clickhouse.com/cloud/vector-search-index-waitlist">sign up for the early access waitlist</a>.</strong></p>

## Get started now!

We hope you enjoyed these announcements. If you are not yet a ClickHouse Cloud user on AWS, please sign up via [AWS Marketplace](https://aws.amazon.com/marketplace/pp/prodview-jettukeanwrfc?trk=cf6e7ff3-7f21-4339-8254-6e13f0d635d7&sc_channel=el&source=clickhouse) or directly at [ClickHouse Cloud](https://clickhouse.cloud/signUp). Either way, you’ll enjoy a $300 credit toward your free trial, and even more benefits if you are part of the [AWS Startup program](https://aws.amazon.com/startups/offers/clickhouse?lang=en-US). 