---
title: "January 2025 newsletter"
date: "2025-01-14T18:37:50.702Z"
author: "ClickHouse Team"
category: "Community"
excerpt: "Welcome to the January ClickHouse newsletter, which will round up what’s happened in real-time data warehouses over the last month."
---

# January 2025 newsletter

Welcome to the first ClickHouse newsletter of 2025. This month, we have Apache Iceberg REST catalog and schema evolution in the 24.12 release. We learn how to build a product analytics solution and implement the Medallion architecture with ClickHouse. And we have videos from The All Things Open Conference!


<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>


## Inside this issue

<ul> 
<li><a href="https://clickhouse.com/blog/202501-newsletter#featured-community-member">Featured Community Member</a></li>
<li><a href="https://clickhouse.com/blog/202501-newsletter#upcoming-events">Upcoming events</a></li>
<li><a href="https://clickhouse.com/blog/202501-newsletter#2412-release">24.12 Release</a></li>
<li><a href="https://clickhouse.com/blog/202501-newsletter#building-a-product-analytics-solution-with-clickhouse">Building a product analytics solution with ClickHouse</a></li>
<li><a href="https://clickhouse.com/blog/202501-newsletter#optimizing-bulk-inserts-for-partitioned-tables">Optimizing bulk inserts for partitioned tables</a></li>
<li><a href="https://clickhouse.com/blog/202501-newsletter#from-zero-to-scale-langfuses-infrastructure-evolution">
From zero to scale: Langfuse's infrastructure evolution</a></li>
<li><a href="https://clickhouse.com/blog/202501-newsletter#building-a-medallion-architecture-with-clickhouse">Building a Medallion architecture with ClickHouse</a></li>
<li><a href="https://clickhouse.com/blog/202501-newsletter#building-a-medallion-architecture-for-bluesky-data">
Building a Medallion architecture for Bluesky data</a></li>
<li><a href="https://clickhouse.com/blog/202501-newsletter#quick-reads">Quick reads</a></li>
<li><a href="https://clickhouse.com/blog/202501-newsletter#video-corner">Video corner</a></li>
<li><a href="https://clickhouse.com/blog/202501-newsletter#post-of-the-month">Post of the month</a></li>
</ul>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## Featured community member

This month's featured community member is <a href="https://www.linkedin.com/in/andersonljason/">Jason Anderson</a>, Head of Data at Skool, a community platform.

![featured-member-202501.png](https://clickhouse.com/uploads/featured_member_202501_664885507d.png)
<p>
Jason Anderson is an experienced data and technology professional with a background in leading teams and developing data-driven solutions. He previously served as Head of Data at Mythical Games and Partner at Comp Three, focusing on machine learning, analytics, and cloud architecture. His career includes roles at IBM and PolySat, where he contributed to cloud services and satellite software development.
</p>
<p>Jason recently <a href="https://clickhouse.com/videos/skools-journey-with-clickhouse">presented his work at Skool at the ClickHouse Los Angeles meetup</a>. Jason explained how they moved from Postgres to ClickHouse to process 100M+ rows daily while delivering lightning-fast queries. There is also <a href="https://clickhouse.com/blog/how-skool-uses-clickhouse-for-observability-behavioral-analytics">a blog post that explains Skool’s use of ClickHouse in more detail</a>.
</p>

<p><a href="https://www.linkedin.com/in/andersonljason?utm_source=clickhouse&amp;utm_medium=email&amp;utm_campaign=202501-newsletter" target="_blank">Follow Jason on LinkedIn</a></p>
<br>

## Upcoming events
 
<p><strong>Global events</strong></p> 
<ul> 
<li><a href="https://clickhouse.com/company/events/v25-1-community-release-call?utm_source=clickhouse&utm_medium=email&utm_campaign=202501-newsletter" target="_blank" id="">Release call 25.1</a> - Jan 28<br></li> 

</ul> 
<p><strong>Free training</strong></p> 
<ul> 
<li><a href="https://clickhouse.com/company/events/202501-emea-query-optimization?utm_source=clickhouse&utm_medium=email&utm_campaign=202501-newsletter" target="_blank" id="">ClickHouse Query Optimization Workshop</a> - Jan 22<br></li> 
<li><a href="https://clickhouse.com/company/events/202501-amer-clickhouse-observability?utm_source=clickhouse&utm_medium=email&utm_campaign=202501-newsletter" target="_blank" id="">Using ClickHouse for Observability</a> - Jan 29</li> 
<li><a href="https://clickhouse.com/company/events/202502-emea-london-inperson-clickhouse-developer?utm_source=clickhouse&utm_medium=email&utm_campaign=202501-newsletter" target="_blank" id="">ClickHouse Developer In-Person Training - London, England</a> - Feb 4-5</li> 
<li><a href="https://clickhouse.com/company/events/202502-emea-dubai-inperson-clickhousetraining?utm_source=clickhouse&utm_medium=email&utm_campaign=202501-newsletter" target="_blank" id="">In-Person ClickHouse Training</a> - Feb 10</li> 
<li><a href="https://clickhouse.com/company/events/202502-apj-query-optimization?utm_source=clickhouse&utm_medium=email&utm_campaign=202501-newsletter" target="_blank" id="">ClickHouse Query Optimization Workshop</a> (APJ-friendly timing) - Feb 12</li> 
</ul> 

<p><strong>Events in EMEA</strong></p> 
<ul> 
<li><a href="https://www.meetup.com/clickhouse-london-user-group/events/305146729/" target="_blank" id="">Meetup in London</a> - Feb 5<br></li> 
<li><a href="https://www.meetup.com/clickhouse-dubai-meetup-group/events/303096989/" target="_blank" id="">Meetup in Dubai</a> - Feb 10<br></li> 
</ul>

<p><strong>Events in APAC</strong></p> 
<ul> 
<li><a href="https://www.alibabacloud.com/en/events/alibabacloud-developer-summit-2025?_p_lc=1" target="_blank" id="">Alibaba Developer Summit Jakarta</a> - Jan 21<br></li> 
<li><a href="https://www.meetup.com/clickhouse-tokyo-user-group/events/305126993/" target="_blank" id="">Meetup in Tokyo</a> - Jan 23<br></li> 
<li><a href="https://www.meetup.com/clickhouse-mumbai-user-group/events/305497320/" target="_blank" id="">Meetup in Mumbai</a> - Feb 1<br></li> 
<li><a href="https://www.meetup.com/clickhouse-bangalore-user-group/events/305497951/" target="_blank" id="">Meetup in Bangalore</a> - Feb 8<br></li> 
<li><a href="https://event.shoeisha.jp/devsumi/20250213" target="_blank" id="">Developers Summit Tokyo</a> - Feb 13-14<br></li> 
</ul>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## 24.12 release

![release-24.12.png](https://clickhouse.com/uploads/release_24_12_1cf63e9515.png)

<p>The final release in 2024 introduced support for the Iceberg REST catalog and schema evolution. <a href="https://www.linkedin.com/in/daniel-weeks-a1946860/">Daniel Weeks</a>, co-creator of Apache Iceberg, made a guest appearance in the 24.12 community call, so be sure to <a href="https://www.youtube.com/watch?v=bv-ut-Q6vnc">check out the recording</a>.</p>

<p>There were also Enum usability improvements, an experimental feature to sort a table by a column in reverse order, JSON subcolumns as a table’s primary key, automatic JOIN reordering, optimization of JOIN expressions, and more!</p>

<p><a href="https://clickhouse.com/blog/clickhouse-release-24-12">Read the release post</a></p>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## Building a product analytics solution with ClickHouse

![building-product-analytics-solution.png](https://clickhouse.com/uploads/building_product_analytics_solution_bfe00baa89.png)

<p>Product analytics involves collecting, analyzing, and interpreting data on how users interact with a product.
</p>
<p>Chloé Carasso leads product analytics at ClickHouse and wrote a blog post explaining how we built our in-house product analytics platform.
</p>
<p>Chloe explains why we decided to build something ourselves rather than buy an off-the-shelf solution and shares some ideas on designing and operating a ClickHouse-powered analytics solution if you're interested in this path. She also shares common queries that she runs, including cohort analysis, user paths, and measuring retention/churn.
</p>
<p><a href="https://clickhouse.com/blog/building-product-analytics-with-clickhouse" target="_blank">Read the blog post</a></p>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>


## Optimizing bulk inserts for partitioned tables

![optimizing-bulk-inserts.png](https://clickhouse.com/uploads/optimizing_bulk_inserts_b0f86fdc37.png)

<p><a href="https://www.linkedin.com/in/jesse-grodman">Jesse Grodman</a>, a Software Engineer at Triple Whale, shares some tips for quickly loading data into a highly partitioned ClickHouse table.</p>

<p>We start writing data directly into the table from S3 files, but that results in many small <a href="https://clickhouse.com/docs/en/parts">parts</a>, which isn’t ideal from a querying standpoint and can result in the <a href="https://clickhouse.com/docs/knowledgebase/exception-too-many-parts">too many parts error</a>. He explores various ways to work around this problem, including sorting the data by partition key as part of the ingestion query, which results in an out-of-memory error.
</p>

<p>Jesse discovers that sorting the data by partition key before writing it into ClickHouse works much better. He also tries first loading the data into an unpartitioned table and then populating the partitioned table afterward, doing the sorting in ClickHouse.
</p>
<p><a href="https://medium.com/@jgrodman/clickhouse-optimizing-bulk-inserts-for-partitioned-tables-9ea91b3e7c3b">Read the blog post</a></p>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## From zero to scale: Langfuse's infrastructure evolution

![from-zero-to-scale.png](https://clickhouse.com/uploads/from_zero_to_scale_4915d25e1f.png)

<p><a href="https://langfuse.com/">Langfuse</a> is an open-source LLM observability platform that participated in the Y Combinator Winter 2023 batch. The initial release of their product was written on Next.js, Vercel, and Postgres. This allowed them to get the release out of the door quickly, but they ran into problems when trying to scale the system.
</p>
<p>In the blog post, they explain their journey to solving these problems, which involved an extensive infrastructure redesign. A Redis queue was introduced to handle spiky ingestion traffic, and they sped up analytics queries with help from a ClickHouse ReplacingMergeTree table.

</p>
<p><a href="https://langfuse.com/blog/2024-12-langfuse-v3-infrastructure-evolution">Read the blog post</a></p>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## Building a Medallion architecture with ClickHouse

![building-medallion-ch.png](https://clickhouse.com/uploads/building_medallion_ch_222ec65015.png)

<p>The medallion architecture is a data design pattern that logically organizes data in a lakehouse. It aims to incrementally and progressively improve the structure and quality of data as it flows through each layer of the architecture (from Bronze ⇒ Silver ⇒ Gold layer tables). 
</p>
<p>The ClickHouse Product Marketing Engineering (PME) team was curious whether the architecture could be applied to a real-time data warehouse like ClickHouse and wrote a blog post describing their experience.
</p>

<p><a href="https://clickhouse.com/blog/building-a-medallion-architecture-with-clickhouse">Read the blog post</a></p>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## Building a Medallion architecture for Bluesky data

![building-medallion-bluesky.png](https://clickhouse.com/uploads/building_medallion_bluesky_266c2b5133.png)

<p>Following the introductory post to the Medallion architecture, the ClickHouse PME team applied this design pattern to data from the BlueSky social network.
</p>
<p>This was a perfect dataset for this experiment, as many of the records had malformed or incorrect timestamps. The dataset also contained frequent duplicates.
</p>
<p>The blog goes through a workflow that addresses these challenges, organizing this dataset into the Medallion architecture’s three distinct tiers: Bronze, Silver, and Gold. The team also heavily uses the <a href="https://clickhouse.com/blog/a-new-powerful-json-data-type-for-clickhouse">recently released JSON type</a>.
</p>

<p><a href="https://clickhouse.com/blog/building-a-medallion-architecture-for-bluesky-json-data-with-clickhouse">Read the blog post</a></p>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## Quick reads

<ul> 
<li><a href="https://www.linkedin.com/in/hellmarbecker/">Hellmar Becker</a> recently joined ClickHouse and has been taking it through its paces. In his first blog post, he explores <a href="https://blog.hellmar-becker.de/2025/01/01/new-years-greetings-from-the-data-cookbook-elf/">array processing functions</a>, and in the second, we learn how to do <a href="https://blog.hellmar-becker.de/2025/01/05/clickhouse-data-cookbook-linear-algebra-in-sql/">linear algebra in ClickHouse</a>.</li> 
<li><a href="https://www.linkedin.com/in/hardiksinghbehl/">Hardik Singh Behl</a> explores <a href="https://www.baeldung.com/spring-boot-olap-clickhouse-database">how to integrate ClickHouse into a Spring Boot application</a>. He first configures the application and establishes a database connection before performing a few CRUD operations.</li> 
<li>Andrei Tserakhau shows <a href="https://medium.com/@laskoviymishka/cdc-from-mysql-to-clickhouse-c791fe414fe1">how to transfer data from MySQL to ClickHouse</a> using Transfer, an open-source cloud-native ingestion engine.</li>
<li><a href="https://www.linkedin.com/in/shivjijha/">Shivji kumar Jha</a> explores <a href="https://www.linkedin.com/pulse/unified-data-platforms-ft-postgres-clickhouse-shivji-kumar-jha-jylqc/">how Postgres and ClickHouse can work together as a unified data management solution</a>, balancing transactional reliability with high-speed analytics.</li> 
</ul>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## Video corner

<ul> 
<li>We had two ClickHouse speakers at the <a href="https://2024.allthingsopen.org/speakers">All Things Open 2024 conference</a>. Tanya Bragin explored <a href="https://clickhouse.com/videos/all-things-open-open-source-cloud-datawarehouse">how open source technologies and datalake standards are transforming the modern data stack</a> by offering alternatives to monolithic cloud data warehouses.</li> 
<li>Zoe Steinkamp explained <a href="https://clickhouse.com/videos/all-things-open-columnar-storage">how columnar databases are revolutionizing data warehousing</a> and analytics by offering superior performance over traditional row-based systems. Zoe also demonstrated how we can build efficient analytics applications with tools like Apache Arrow, Parquet, and Pandas while reducing costs and improving query performance./li> 
<li> Mark explained the <a href="https://www.youtube.com/watch?v=EOXEW_-r10A&t=5s">various deployment modes of ClickHouse</a>, including ClickHouse Server, clickhouse-local, and chDB.</li>
<li> Avi Press explains how Scarf has <a href="https://clickhouse.com/videos/open-source-scarf">built a ClickHouse-backed data pipeline that handles ~25GB of data and 50 million events every day</a>.</li>
</ul>

<p style="
    margin-bottom: 0;
    line-height: 0;
">&nbsp;</p>

## Post of the month

<p>Our favorite post this month was by <a href="https://x.com/dschewchenko1/status/1872671222569271573">Dmytro Shevchenko</a>:</p>

![post-of-month-202501.png](https://clickhouse.com/uploads/post_of_month_202501_cb6b65fa1c.png)

<p>
<a href="https://x.com/dschewchenko1/status/1872671222569271573">Read the post</a>
</p>
