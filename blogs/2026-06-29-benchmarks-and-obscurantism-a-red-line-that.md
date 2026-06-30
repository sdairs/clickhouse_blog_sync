---
title: "Benchmarks and Obscurantism: A “red” line that should not be crossed"
date: "2026-06-29T19:06:51.282Z"
author: "Melvyn Peignon"
category: "Engineering"
excerpt: "Benchmarks only matter when they can be inspected, challenged, and reproduced. Here’s what we found when we tested Databricks’ ClickHouse claim."
---

# Benchmarks and Obscurantism: A “red” line that should not be crossed


> **TL;DR**<br/><br/>Databricks used its keynote to show ClickHouse “crashing” in a benchmark for Reyden, its new gated low-latency compute product. But the benchmark did not disclose the hardware, cost, configuration, cache settings, or enough methodology for anyone outside Databricks to reproduce or validate the result.<br/><br/>We tried to reproduce the claimed ClickHouse failure using the only clearly identified setup detail: TPC-H SF1 and Q6. ClickHouse did not crash. A single 30 vCPU node sustained about 420 QPS at sub-second P90 latency, and scaling to 15,000 QPS came down to straightforward sizing: roughly 30 to 40 untuned nodes.<br/><br/>That is the real point of this post: benchmark results are useful only when they are open, reproducible, and detailed enough to inspect. Without that, they are not evidence. They are claims you have to take on faith.


<br/>


## Why benchmark transparency matters

At ClickHouse, we love testing how our products perform across a variety of datasets and benchmarks. We strongly believe that benchmarking products in a transparent and reproducible manner is key to providing quality information to end users, and that it fosters a fair and transparent competitive landscape that ultimately pushes different technologies to innovate.

That said, comparing two software products is not a trivial task, especially when no one is equally expert in all systems evaluated. Each product has its own architecture, configuration model, optimizations, and tradeoffs, which means even the best good-faith benchmark *can* miss something important. That is why we believe benchmarks should be open, transparent, and reproducible. At the very least, this provides a common baseline that can start a conversation and highlight the nuances between systems. If experts in one of the systems see a configuration issue in the benchmark, they should be able to point it out, and the benchmark should be easy to update and rerun. That is what happened recently with Snowflake: after [our initial benchmark results](https://clickhouse.com/blog/write-side-cost-performance-snowflake-clickhouse), [Snowflake shared feedback](https://www.snowflake.com/en/blog/engineering/efficient-snowflake-ingestion-query-ready/). We incorporated their feedback, updated the setup based on all of their suggestions, and [we reran the comparison](https://clickhouse.com/blog/real-time-analytics-cost-performance-snowflake-vs-clickhouse). It's then up to the consumer of the benchmark to decide, based on the data and methodology, what matters most to them and what insights they want to extract.

> To be useful, benchmarks need to be reproducible and run with a clear methodology. If they aren't, we slowly fall into deception and[ obscurantism](https://en.wikipedia.org/wiki/Obscurantism) — or, as some like to call it, "benchmarketing."

## The Databricks Reyden benchmark

I wanted to write about benchmark transparency because I just got back from San Francisco, where I attended the Databricks Data and AI Summit — the conference where Databricks showcases its new product announcements. The one that piqued my interest the most was the Reyden announcement. If you haven't watched it, the tl;dr is that Databricks developed a new compute group that aims to address low-latency query workloads. ClickHouse was highlighted and referenced a few times during the keynote.

![unnamed.png](https://clickhouse.com/uploads/unnamed_70ab69925d.png)

This is great news for the real-time analytics space: it means more people will be working on the problem, and we might see more innovation. But as I watched the keynote, one particular benchmark caught my eye.

![unnamed (1).png](https://clickhouse.com/uploads/unnamed_1_f49bd032dd.png)

The yellowish line is ClickHouse (by the way, this is our old color, the new one is `#FAFF69`), the blue lines are Snowflake, and the red line is Databricks. As the product manager for ClickHouse, seeing that ClickHouse “crashed” during the benchmark was a big problem for me, so immediately after the keynote I set out to reproduce the benchmark and see how ClickHouse could possibly crash with that load.


## Datasets selection

During the Reyden announcement, they at least shared that two datasets were used:


* The TPC-H benchmark (with a big emphasis on TPC-H SF 1 — the smallest scale factor of the benchmark), which is also, conveniently, a sample dataset provided by Databricks.

![unnamed (2).png](https://clickhouse.com/uploads/unnamed_2_dfc06bf074.png)

* The NYC Taxi dataset. This dataset can be found in different sizes, but Databricks provides a sample that coincidentally matches the range of the query highlighted during the keynote; the sample they provide is around 22K rows.

![unnamed (3).png](https://clickhouse.com/uploads/unnamed_3_ddc2fc29ec.png)

Overall, that would be an interesting choice, for one primary reason:

> These datasets are tiny. They are so small they can fit in memory on an iPhone.<br/><br/>At that point, you are not measuring how the engine performs at scale. You are measuring how fast it can query data that is already in an in-memory cache.<br/><br/>For a query engine meant to work at any scale, I would have expected Databricks to use real world dataset in the terabyte range, not one this small.


This is yet another reason why open and transparent benchmarking is critical. Nonetheless, the only dataset for which we certainly know the size is TPC-H, as they highlight in one of the charts that they used scale factor 1. Let's use that dataset to try to reproduce Databricks' benchmark and to try to make ClickHouse[ “crash](https://en.wikipedia.org/wiki/Crash_(computing)).”


## Reproducing the “Crash”

The dataset is the only piece of information Databricks provides about their benchmark. We don't know the amount of hardware used, the settings applied during the experiment, what type of cache was enabled, the cost of the infrastructure used to run it, or even whether ClickHouse was self-managed or a cloud deployment.

I wanted to test ClickHouse directly against Reyden, so ideally I would have at least known what type of hardware was being used and what the benchmark cost. We have a Databricks account, which we use to test our various integrations with the Databricks ecosystem (Unity Catalog, Delta tables, Iceberg tables, the Spark connector, etc.). Since Reyden is gated, I reached out to my Databricks account manager to request access so I could test Reyden myself. As of the publication date of this blog post, I still haven't heard back; my request was stuck at "still waiting on approvals from the product team."

So, I cannot use Reyden in this benchmark, which complicates my testing. Given the complete lack of information about how the benchmark was done, I only have one option: rather than comparing ClickHouse to Reyden, let's try to reproduce the crash that Databricks claimed happened to ClickHouse, and let's see if we can get ClickHouse to serve more than the 1500 QPS reported by Databricks.

Before we start benchmarking, a few things are important to note:


* ClickHouse supports up to 1000 concurrent queries per node, this is a [configurable setting](https://clickhouse.com/docs/operations/settings/settings#max_concurrent_queries_for_all_users) that can be changed depending on the workload you are running
* The query used in this benchmark is Q6 of TPC-H, a very simple query that primarily tests the software's filtering and simple aggregation capabilities. You can see it below:

<pre>
<code type='click-ui' language='sql' show_line_numbers='false'>
SELECT sum(l_extendedprice * l_discount) AS revenue
FROM lineitem
WHERE l_shipdate >= '1994-01-01'
  AND l_shipdate < '1995-01-01'
  AND l_discount BETWEEN 0.05 AND 0.07
  AND l_quantity < 24
</code>
</pre>

Let's start by loading the dataset into ClickHouse. Using our native connector with[ Databricks Unity Catalog](https://clickhouse.com/docs/use-cases/data-lake/unity-catalog), I can simply connect to my Databricks environment and load the TPC-H data into ClickHouse.

My first step is to evaluate how many queries a single ClickHouse node can handle. For this specific test, I will use a 30 vCPU, 120 GB ClickHouse node. Given that the queries are very simple, we can expect them to execute very quickly on a single node. I'm not going to spend time tuning any of ClickHouse's settings; I will just point my Vegeta script at ClickHouse and send the queries.

![unnamed (4).png](https://clickhouse.com/uploads/unnamed_4_aef952de14.png)

The orange dotted line is the QPS threshold at which Databricks claimed ClickHouse crashed. The yellow line represents the performance of ClickHouse (1 node) at different QPS loads.

As you can see on the chart, a single ClickHouse node can sustain up to 420 QPS while maintaining a P90 latency below one second. If you keep increasing the QPS, ClickHouse will not have enough CPU to process incoming queries. Each query will wait for CPU and the latency will inevitably increase; as the latency increases, more and more queries will be processed concurrently, and ClickHouse will eventually reach the[ 1000 concurrent query threshold](https://clickhouse.com/docs/operations/server-configuration-parameters/settings#max_concurrent_queries) defined in our cloud and start rejecting new incoming queries. No crash, despite stressing ClickHouse quite a lot. Queries are rejected to protect the system. In this scenario, it's up to the client to simply retry the query or to increase the amount of compute allocated to the ClickHouse cluster.

You can see this behavior in action here:

![unnamed (5).png](https://clickhouse.com/uploads/unnamed_5_fe84c5680a.png)

As the number of concurrent queries increases, ClickHouse starts rejecting new queries to protect the system. This whole benchmark essentially measures one thing: how efficiently will a system leverage its CPU to process as fast as possible a query, if you can optimize this metric, any decent distributed system will be able to linearly scale as you add more nodes to the system. 

So now that we know that one node can handle up to 420 QPS, it's simple arithmetic to work out how many nodes we need to process 15,000 QPS, **without doing any other optimizations**: 

15000 / 420 = 35 nodes

> Note that there are many other ways we could increase the QPS that ClickHouse can sustain. For example, we could use max_threads = 1 to limit CPU starvation, or we could enable the query cache ([which is enabled by default in Databricks](https://docs.databricks.com/aws/en/sql/user/queries/query-caching)). Again, we have no idea what configuration was chosen for the Databricks benchmark, so we are assuming that no optimizations were done on the ClickHouse slide. Regardless, this blog post is not about how to optimize ClickHouse; it's about benchmark transparency.

This also makes it easy to figure out how many ClickHouse nodes Databricks used for their own benchmark: in the keynote, they mentioned ClickHouse crashing between 1200 and 1500 QPS, which means it was 3 nodes, or around 90 vCPUs.

For the fun of the exercise, let's test different configurations and see how they perform:

![unnamed (6).png](https://clickhouse.com/uploads/unnamed_6_b72a465e81.png)

As expected, to sustain 15K concurrent queries while keeping the P90 latency sub-second, with no additional optimizations, we need between 30 and 40 nodes.

And we can also monitor the query rejection ratio:

![unnamed (7).png](https://clickhouse.com/uploads/unnamed_7_cbaf1fd2f9.png)

So only with the 1-node and 10-node configurations do we end up with too many concurrent queries.

Still, we could stitch the metrics above onto Databricks' chart, and you'd get the chart below:

![unnamed (8).png](https://clickhouse.com/uploads/unnamed_8_249c698e17.png)

This is, of course, comparing apples to … cars — but it's essentially what was presented last week. If you were to take that chart and claim that ClickHouse is better than Reyden, that would be a mistake, because you would still be lacking critical information about how the other benchmarks were generated. What about the cost of Reyden? How does it behave when the dataset grows and you are not running the same query over and over? Does a data lake-based solution satisfy [all of your real-time requirements](https://clickhouse.com/blog/selecting-a-real-time-analytical-database)? 

This small benchmarking exercise highlighted a couple of things:



1. I was not able to make ClickHouse crash while running any of these benchmarks.
2. With a proper sizing exercise and no other optimizations, ClickHouse was able to sustain 15,000 QPS without breaking a sweat and without any tuning.
3. Many performance problems can be solved by throwing more compute at them. An important question is which system also does it more [cost-efficiently](https://clickhouse.com/blog/costbench-data-warehouse-cost-performance). 
4. We could improve the QPS even further by tuning a few settings:
    * the number of threads
    * enabling the query cache
    * creating projections
    * etc.

## Conclusion

Benchmarks are great (and a lot of fun, too). When done well, they give engineering teams real signals on where to improve. But the benchmarks Databricks showed in its keynote and their [LakeHouse//RT announcement](https://www.databricks.com/blog/introducing-lakehousert-real-time-performance-unified-lakehouse) blog do not meet that bar. They were not open, not reproducible, and not detailed enough to be meaningfully informative or actionable.

That is what makes this so surprising. Databricks has long positioned itself around openness, and they continue to make that a central part of their story today. This is the company that celebrated [dropping the DeWitt clause in 2021](https://www.databricks.com/blog/2021/11/08/eliminating-the-dewitt-clause-for-database-benchmarking.html), at a time when vendors still used licensing terms to discourage public benchmarking. Five years later, they used a keynote to present an opaque benchmark on a product competitors cannot access, with too little detail for anyone to validate the results.

Ultimately, we recommend you test the product yourself. We believe in being open, and publish everything we run in a [public GitHub repository](https://github.com/ClickHouse/CostBench) along with the data, queries, configuration, and steps needed to reproduce the results. We believe that is the only way benchmarks become useful: not as a slide in a keynote, but as something customers, engineers, and competitors can inspect, challenge, and learn from.






