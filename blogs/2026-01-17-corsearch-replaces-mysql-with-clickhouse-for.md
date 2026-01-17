---
title: "Corsearch replaces MySQL with ClickHouse for content and brand protection"
date: "2024-07-09T13:36:07.053Z"
author: "ClickHouse Team"
category: "User stories"
excerpt: "Corsearch started life in 2018 as a specialist spinoff from Wolters Kluwer. The new company expanded rapidly through multiple acquisitions, consolidating its expertise to become a leader in brand protection solutions."
---

# Corsearch replaces MySQL with ClickHouse for content and brand protection

>Chase Richards has led engineering efforts at Marketly from a 2011 start-up through its acquisition in 2020. He is now VP of Engineering at a brand protection firm, Corsearch. He [joined us at a recent meetup and shared his ClickHouse experience](/videos/how-corsearch-uses-clickhouse-today).

<a href="https://corsearch.com" target="_blank">Corsearch</a> started life in 2018 as a specialist spinoff from Wolters Kluwer. The new company expanded rapidly through multiple acquisitions, consolidating its expertise to become a leader in brand protection solutions. Chase Richards is VP of Engineering and plays a key role in leading the engineering efforts that enhance Corsearch’s brand protection solutions for organizations worldwide.   The focus on tracking international trademarks and detecting conflict and infringement, anti-counterfeit measures, and content protection against piracy and cybersquatting means sifting through vast volumes of innocuous or harmless authorized data to find the infringements and bad actors. Back in 2017 (while still at Marketly) Chase was up against some challenges:

* **Limitations of transactional databases** - constraints of row-based databases, like MySQL, when applied to analytics hindered scalability and flexibility when building interactive data-driven user interfaces for external customers. 
* **Operational complexity** - multiple database backends, including MySQL, BigQuery, and MongoDB, were used to support key customer-facing applications and meant more time spent on maintenance rather than building new functionality.

## Adopting ClickHouse for anti-piracy

One of Corsearch’s primary client-facing reporting products is a search engine protection service, which supports the anti-piracy and content protection business. Corsearch scrapes millions of search results every hour, looking for infringing content. They invested heavily in developing sophisticated search engine monitoring metrics, taking inspiration from best practices in SEO and SEM like rank tracking and traffic share. They focused on making the user interface familiar and appealing to marketing teams trying to optimize search engine footprint and profile, except flipping the idea on its head. _“We told marketing teams that pirates were essentially encroaching on their territory – real estate within search result positions,”_ Chase said. Corsearch gave them the visibility and tools to fight back. 

However, the reporting interface required real-time analysis for hundreds of metrics, and that experience had to be interactive, or the marketing teams would be frustrated using it. This means that dozens of concurrent queries on recent and historical data across all active users had to execute in milliseconds. The MySQL database was not the right fit for a workload entailing 10+ filterable dimensions with daily, weekly, and monthly group-bys on top of time-series data._“We developed killer metrics and built a front end. But we were running on a pre-aggregated set of MySQL tables, with heavy table partitioning around data. It was operationally complex and still did not scale.”_ This problem became more apparent as app usage grew – queries got slower and slower and users started to leave the app. Chase told the meetup: _“It worked well at the beginning and then our client systems kept growing – great news for our start-up business – but it meant the data kept scaling up and up and up and with MySQL,  of course, there are index constraints and you are bound by a row based technology.”_

>“We got some eye-popping figures. The compression ratios alone just made managing the servers and the deployments much easier.”

## Making the switch to ClickHouse for real-time analytics

Making a database change was driven by Chase, who spent countless hours reading community content looking for new technologies and ways of optimizing performance. He came across ClickHouse thanks to a couple of 2017 Percona and Cloudflare blogs: _“I was encouraged to give ClickHouse a try. It became clear that ClickHouse could be a potential source of efficiency, reliability, and scalability.”_ The team began to replace the cumbersome MySQL setup with agile, scalable solutions that streamlined operations and enhanced client experiences. _“I built a drop-in replacement prototype around ClickHouse, using an almost identical table structure as what was in MySQL, and it was fully in production for all clients by 2019.”_ The prototype took off and became the new architecture for this product. “_It’s still in production today and still part of the pipeline.”_

The resulting benefits went beyond making the application work. ClickHouse's data compression rates for time-series data far exceeded that of MySQL (see below), which resulted in fewer servers needed to run the app, thus simplifying server management. _“We got some eye-popping figures. The compression ratios alone just made managing the servers and the deployments much easier.”_ Of course, ClickHouse does not stand still and improves data compression and performance in every release. _“ClickHouse has gotten even better. For example, low cardinality has been a massive jump forward in terms of performance and compression ratios,”_ Chase explained.

![corsearch-img1.png](https://clickhouse.com/uploads/corsearch_img1_ab1a50787b.png)

## Enhancing anti-piracy efforts with vector search

More recently, Corsearch added vector-based analytics to its existing heuristics-based approach for fraud detection. Corsearch is using embeddings from language models to create a semantic similarity search between webpage content, both across websites and time, which is used to find websites using similar language as known pirate sites and identify major changes in the content served by a website, often indicating it has gone down or been blocked (both frequent occurrences in the piracy ecosystem). _“By utilizing expert models and embeddings, we detect substantive changes in web pages and identify connections between pages that share similar characteristics,”_ explains Chase. 

Chase and his team conducted a comparative analysis of ClickHouse with dedicated vector databases, and found that while they may offer better performance for approximate indexes, they are still special-purpose systems and would need a complimentary skillset to adopt and maintain.  Instead, Corsearch is able to execute vector distance calculations bounded by multiple dimensions directly in ClickHouse, along with other methods for detecting piracy, facilitated with the SQL syntax. Thus, there is no need to maintain additional infrastructure or learn a new language.

## Adopting ClickHouse for observability

In another significant use case, Corsearch adopted ClickHouse to monitor its search engine scraping setup. The search engine service is responsible for parsing results from major search engines like Google, Yahoo, and YouTube, and must operate seamlessly. Instead of using an off–the-shelf observability tool, Chase and his team developed custom instrumentation to track search engine operations, sent telemetry to ClickHouse, and used Grafana to visualize the results and alert on potential problems. Recently this approach to observability has been termed [SQL-Based Observability](/blog/the-state-of-sql-based-observability), and has been adopted by the likes of Uber, eBay, and other technology leaders. 

From a schema perspective, it’s a straightforward table design, consisting of just two tables. One table facilitates a generic metrics system, allowing for the tracking of various metrics such as queue depths. The other table encapsulates what Chase refers to as _"the atomic unit of work,"_ which tracks an attempt to crawl a web page. The infrastructure enables the creation of charts and time series metrics effortlessly. Each column effectively becomes its own time series, ensuring that data can be materialized into its original form at any time. 

_“It works fantastically for my small team,”_ Chase told the meetup. While the instrumentation is custom, Chase admitted that if he started today, he would look into using <a href="https://opentelemetry.io/" target="_blank">OpenTelemetry</a> first, as it’s becoming a clear standard. The performance and resource efficiency benefits of ClickHouse extend to this use case as well: _“The system manages to store over 10 billion rows spanning four years in less than 325 GB on disk,”_ Chase shared. 

![corsearch-img2.png](https://clickhouse.com/uploads/corsearch_img2_a72e66a258.png)

## Future directions

ClickHouse is a key element of Corsearch's data infrastructure, unlocking key capabilities core to the business, consolidating analytical data management across multiple use cases, and streamlining operations: _“ClickHouse plays a vital role in capturing web traffic data and we've streamlined complex data pipelines by consolidating them into single ClickHouse clusters, resulting in improved efficiency and performance across the board.”_ 

Going forward, Chase shared plans to look at ClickHouse Cloud to simplify their operations even more: _“I am excited to try ClickHouse Cloud on our production workload. It's really cool to see the cloud-native architecture for running ClickHouse being developed there, which offers additional differentiation._”  Following the meetup presentation, Corsearch has started using ClickHouse Cloud for storing our embeddings generated from millions of scraped images a day for similarity searching – this allows the team to take advantage of the low operational overhead and unlimited storage provided by that service in addition to achieving faster linear distance scans on the same data sets.