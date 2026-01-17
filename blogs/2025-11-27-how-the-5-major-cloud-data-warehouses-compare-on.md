---
title: "How the 5 major cloud data warehouses compare on cost-performance"
date: "2025-11-27T13:40:34.632Z"
author: "Tom Schreiber & Lionel Palacin"
category: "Engineering"
excerpt: "We benchmarked the five major cloud data warehouses at 1B–100B rows using their real billing models to measure performance per dollar. Results show how cost-performance shifts as data grows."
---

# How the 5 major cloud data warehouses compare on cost-performance

> **TL;DR**<br/><br/>We benchmarked **Snowflake**, **Databricks**, **ClickHouse Cloud, BigQuery**, and **Redshift** across 1B, 10B, and 100B rows, applying each vendor’s real compute billing rules.<br/><br/>
For analytical workloads at scale, **ClickHouse Cloud delivers an order-of-magnitude better value than any other system**.

## How to compare cloud warehouse cost-performance

You have a dataset and a set of analytical queries. You have several cloud data warehouses you could run them on. And the question is straightforward:

> **Where do you get the most performance per dollar for analytical workloads?**

Price lists don’t answer that.

[They can’t](/blog/how-cloud-data-warehouses-bill-you). Different vendors meter compute differently, price capacity differently, and define “compute resources” differently, which makes their numbers incomparable at face value.

So we ran the *same* production-derived analytical workload across all five major cloud data warehouses:

* **Snowflake**
* **Databricks**
* **ClickHouse Cloud**
* **BigQuery**
* **Redshift**

And we ran it at three scales — **1B**, **10B**, and **100B** rows — to see how cost and performance evolve as data grows.

If you want the short version, here’s the spoiler: **Cost-performance doesn’t scale linearly across systems.**

> **ClickHouse Cloud delivers an order-of-magnitude better value than any other system.**

![Blog-Costs-animation01_small.gif](https://clickhouse.com/uploads/Blog_Costs_animation01_small_de9ac301cc.gif)

If you want the details, the charts, and the methodology, read on.

>**Reproducible pipeline**:<br/>All results in this post are generated using [Bench2Cost](/blog/how-cloud-data-warehouses-bill-you#before-we-dive-in-how-we-calculate-costs-with-bench2cost), our open and fully reproducible benchmarking pipeline. 
Bench2Cost applies each system’s real **compute** billing model to the raw runtimes so the cost comparisons are accurate and verifiable.
<br/><br/>
**Storage isn’t the focus**:<br/>
Bench2Cost also calculates **storage costs** for every system, but we don’t highlight them here because storage pricing is simple, similar across vendors, and negligible compared to compute for analytical workloads.
<br/><br/>
**The hidden storage win**:<br/>
That said, if you look at the raw numbers in the result JSONs we link from the charts, **ClickHouse Cloud quietly beats every other system on storage size and storage cost, often by orders of magnitude**, but that’s outside the scope of this comparison.



## Interactive benchmark explorer

Static charts are great for storytelling, but they only scratch the surface of the full dataset.

So we built something new: **a fully interactive benchmark explorer**, **embedded right here in the blog**.

You can mix and match vendors, tiers, cluster sizes, and dataset scales; switch between runtime, cost, and cost-performance ranking; and explore the complete results behind this study.

<iframe src="/uploads/benchmark_costs_dashboard_95d2e2ef2b.html" frameborder="0" style="width: 100%; height: 800px;"></iframe>


If you want to understand how we produced these numbers, everything is documented in the [Appendix](/blog/cloud-data-warehouses-cost-performance-comparison#appendix-benchmark-methodology) at the end of the post.

Let’s look at how the systems perform at each scale, starting with 1B rows.

*(As discussed in the Appendix, we use the standard 43-query ClickBench analytical workload to evaluate each system.)*


## 1B rows: the baseline

> **We include the 1B scale only as a baseline, but the more realistic stress points for modern data platforms are 10B, 100B, and above.**<br/><br/>
Today’s analytical workloads routinely operate in the tens of billions, hundreds of billions, and even trillions of rows.
[Tesla ingested **over one quadrillion rows** into ClickHouse](https://clickhouse.com/blog/how-tesla-built-quadrillion-scale-observability-platform-on-clickhouse#proving-the-system-at-scale) for a stress test, and [ClickPy](https://clickpy.clickhouse.com/), our Python client telemetry dataset, has already surpassed **[two trillion rows](https://sql.clickhouse.com/?query=U0VMRUNUCiAgICAgICAgZm9ybWF0UmVhZGFibGVRdWFudGl0eShzdW0oY291bnQpKSBBUyB0b3RhbCwgdW5pcUV4YWN0KHByb2plY3QpIGFzIHByb2plY3RzIEZST00gcHlwaS5weXBpX2Rvd25sb2Fkcw&run_query=true)**.

The [scatter plot](/blog/cloud-data-warehouses-cost-performance-comparison#how-to-read-the-scatter-plot-charts) below shows, for each of the five systems, the total runtime (horizontal axis) and total compute cost (vertical axis) for a 1-billion-row ClickBench run.

*(We simply hide the tick labels for clarity; the point positions remain fully accurate. The interactive benchmark explorer above shows the full numeric axes.)*

![Blog-Costs.008.png](https://clickhouse.com/uploads/Blog_Costs_008_3d74ce58e7.png)
*(Shown configurations represent the full spectrum for each engine; [details in Appendix](/blog/cloud-data-warehouses-cost-performance-comparison#what-configurations-we-compare).)*

At 1B rows, the chart reveals 3 clear [quadrants of behavior](/blog/cloud-data-warehouses-cost-performance-comparison#how-to-read-the-scatter-plot-charts).


<table>
  <thead>
    <tr>
      <th>Category</th>
      <th>System / Tier</th>
      <th>Runtime</th>
      <th>Cost</th>
    </tr>
  </thead>
  <tbody>
    <!-- FAST & LOWER COST -->
    <tr>
      <td colspan="4"><strong>A large group falls into the ideal quadrant — fast enough <em>and</em> reasonably priced — but with very different value-per-dollar profiles.</strong></td>
    </tr>
    <tr>
      <td><code>Fast & Low-Cost</code></td>
      <td><strong>ClickHouse Cloud</strong> (<a href="https://clickhouse.com/blog/clickhouse-parallel-replicas">9 nodes</a>)</td>
      <td><a href="https://github.com/ClickHouse/examples/blob/main/blog-examples/Bench2Cost/clickhouse-cloud/results_1B/aws.9.236.parallel_replicas.json">~23 s</a></td>
      <td>
        <a href="https://github.com/ClickHouse/examples/blob/main/blog-examples/Bench2Cost/clickhouse-cloud/results_1B/aws.9.236.parallel_replicas.json">~$0.67</a>
      </td>
    </tr>
    <tr>
      <td><code>Fast & Low-Cost</code></td>
      <td><strong>BigQuery Enterprise (capacity)</strong></td>
      <td><a href="https://github.com/ClickHouse/examples/blob/main/blog-examples/Bench2Cost/bigquery/results_1B/result_enriched.json">~38 s</a></td>
      <td><a href="https://github.com/ClickHouse/examples/blob/main/blog-examples/Bench2Cost/bigquery/results_1B/result_enriched.json">~$0.80</a></td>
    </tr>
    <tr>
      <td><code>Fast & Low-Cost</code></td>
      <td><strong>Redshift Serverless (128 RPU)</strong></td>
      <td><a href="https://github.com/ClickHouse/examples/blob/main/blog-examples/Bench2Cost/redshift-serverless/results_1B/enriched_1b.json">~64 s</a></td>
      <td><a href="https://github.com/ClickHouse/examples/blob/main/blog-examples/Bench2Cost/redshift-serverless/results_1B/enriched_1b.json">~$0.85</a></td>
    </tr>
    <tr>
      <td><code>Fast & Low-Cost</code></td>
      <td><strong>Databricks (Large)</strong></td>
      <td><a href="https://github.com/ClickHouse/examples/blob/main/blog-examples/Bench2Cost/databricks/results_1B/clickbench_Large_enriched.json">~80 s</a></td>
      <td><a href="https://github.com/ClickHouse/examples/blob/main/blog-examples/Bench2Cost/databricks/results_1B/clickbench_Large_enriched.json">~$0.62</a></td>
    </tr>
    <tr>
      <td><code>Fast & Low-Cost</code></td>
      <td><strong>Snowflake (Large)</strong></td>
      <td><a href="https://github.com/ClickHouse/examples/blob/main/blog-examples/Bench2Cost/snowflake/results_1B/large_enriched.json">~127 s</a></td>
      <td><a href="https://github.com/ClickHouse/examples/blob/main/blog-examples/Bench2Cost/snowflake/results_1B/large_enriched.json">~$0.85</a></td>
    </tr>
        <!-- FAST & HIGH COST -->
    <tr>
      <td colspan="4"><strong>These two deliver ok speed, but at a steep price.</strong></td>
    </tr>
    <tr>
      <td><code>Fast & High-Cost</code></td>
      <td><strong>Snowflake (4X-Large)</strong></td>
      <td><a href="https://github.com/ClickHouse/examples/blob/main/blog-examples/Bench2Cost/snowflake/results_1B/4xl_enriched.json">~45 s</a></td>
      <td><a href="https://github.com/ClickHouse/examples/blob/main/blog-examples/Bench2Cost/snowflake/results_1B/4xl_enriched.json">~$4.8</a></td>
    </tr>
    <tr>
      <td><code>Fast & High-Cost</code></td>
      <td><strong>Databricks (4X-Large)</strong></td>
      <td><a href="https://github.com/ClickHouse/examples/blob/main/blog-examples/Bench2Cost/databricks/results_1B/clickbench_4X-Large_enriched.json">~59 s</a></td>
      <td><a href="https://github.com/ClickHouse/examples/blob/main/blog-examples/Bench2Cost/databricks/results_1B/clickbench_4X-Large_enriched.json">~$6.1</a></td>
    </tr>
    <!-- BIGQUERY ON-DEMAND -->
    <tr>
      <td colspan="4"><strong>BigQuery On-Demand is fast, but its per-TiB scanned pricing pushes it completely out of the main plot.</strong></td>
    </tr>
    <tr>
      <td><code>Fast & High-Cost</code> (off-chart)</td>
      <td><strong>BigQuery On-Demand</strong></td>
      <td><a href="https://github.com/ClickHouse/examples/blob/main/blog-examples/Bench2Cost/bigquery/results_1B/result_enriched.json">~38 s</a></td>
      <td><a href="https://github.com/ClickHouse/examples/blob/main/blog-examples/Bench2Cost/bigquery/results_1B/result_enriched.json">~$16.9</a></td>
    </tr>
    <!-- SLOW & LOWER COST -->
    <tr>
      <td colspan="4"><strong>These tiers are inexpensive, but extremely slow.</strong></td>
    </tr>
        <tr>
      <td><code>Slow & Low-Cost</code></td>
      <td><strong>Databricks (2X-Small)</strong></td>
      <td><a href="https://github.com/ClickHouse/examples/blob/main/blog-examples/Bench2Cost/databricks/results_1B/clickbench_2X-Small_enriched.json">~712 s</a></td>
      <td><a href="https://github.com/ClickHouse/examples/blob/main/blog-examples/Bench2Cost/databricks/results_1B/clickbench_2X-Small_enriched.json">~$0.55</a></td>
    </tr>
    <tr>
      <td><code>Slow & Low-Cost</code></td>
      <td><strong>Snowflake (X-Small)</strong></td>
      <td><a href="https://github.com/ClickHouse/examples/blob/main/blog-examples/Bench2Cost/snowflake/results_1B/xs_enriched.json">~785 s</a></td>
      <td><a href="https://github.com/ClickHouse/examples/blob/main/blog-examples/Bench2Cost/snowflake/results_1B/xs_enriched.json">~$0.65</a></td>
    </tr>
  </tbody>
</table>


To compare cost-efficiency directly, the chart below collapses runtime and cost into a single cost-performance score ([definition in methodology](/blog/cloud-data-warehouses-cost-performance-comparison#how-we-measure-overall-cost-performance-ranking)):

![Blog-Costs.009.png](https://clickhouse.com/uploads/Blog_Costs_009_18d232f919.png)

The picture becomes unambiguous:



* **ClickHouse Cloud delivers the strongest overall cost-performance**; it has the lowest *runtime × cost* value, and everything else is compared against it.

* **BigQuery (capacity mode)** comes next, at roughly **2× worse** than ClickHouse for this dataset size.

* **Most other configurations fall off quickly** as their *runtime × cost* climbs: from **3–4× worse** up to **double-digit multiples** for the larger Snowflake and Databricks tiers.


> The real story begins when the data grows.<br/><br/>1B rows is still small by modern standards, and the economics change rapidly as we scale to 10B and 100B rows, where most systems start drifting sharply out of the "Fast & Low-Cost" zone.


## 10B rows: cracks start to show

The [scatter plot](/blog/cloud-data-warehouses-cost-performance-comparison#how-to-read-the-scatter-plot-charts) below shows, for each of the five systems, the total runtime (horizontal axis) and total compute cost (vertical axis) for a 10-billion-row ClickBench run.

*(As noted earlier, we hide the tick labels for visual clarity, the point positions still reflect the real underlying values. The interactive benchmark explorer above includes full numeric axes.)*

![Blog-Costs.011.png](https://clickhouse.com/uploads/Blog_Costs_011_a2429a91bc.png)
*(Shown configurations represent the full spectrum for each engine; [details in Appendix](/blog/cloud-data-warehouses-cost-performance-comparison#what-configurations-we-compare).)*

At 10B rows, the first real separation appears. Systems begin drifting out of the "Fast & Low-Cost" [quadrant](/blog/cloud-data-warehouses-cost-performance-comparison#how-to-read-the-scatter-plot-charts ) as runtimes stretch and costs rise.


<table>
  <thead>
    <tr>
      <th>Category</th>
      <th>System / Tier</th>
      <th>Runtime</th>
      <th>Cost</th>
    </tr>
  </thead>
  <tbody>
    <!-- FAST & LOWER COST -->
    <tr>
      <td colspan="4"><strong>These are the only two systems still in the ideal quadrant at 10B rows, but with very different speed profiles.</strong></td>
    </tr>
    <tr>
      <td><code>Fast & Low-Cost</code></td>
      <td><strong>ClickHouse Cloud</strong> (<a href="https://clickhouse.com/blog/clickhouse-parallel-replicas">20 nodes</a>)</td>
      <td><a href="https://github.com/ClickHouse/examples/blob/main/blog-examples/Bench2Cost/clickhouse-cloud/results_10B/aws.20.236.parallel_replicas.json">~67 s</a></td>
      <td>
        <a href="https://github.com/ClickHouse/examples/blob/main/blog-examples/Bench2Cost/clickhouse-cloud/results_10B/aws.20.236.parallel_replicas.json">~$4.27</a>
      </td>
    </tr>
    <tr>
      <td><code>Fast & Low-Cost</code></td>
      <td><strong>Databricks (Large)</strong></td>
      <td><a href="https://github.com/ClickHouse/examples/blob/main/blog-examples/Bench2Cost/databricks/results_10B/clickbench_Large_enriched.json">~604 s</a></td>
      <td><a href="https://github.com/ClickHouse/examples/blob/main/blog-examples/Bench2Cost/databricks/results_10B/clickbench_Large_enriched.json">~$4.70</a></td>
    </tr>
    <!-- FAST & HIGH COST -->
    <tr>
      <td colspan="4"><strong>These systems are still reasonably fast, but prices jump sharply as data grows.</strong></td>
    </tr>
    <tr>
      <td><code>Fast & High-Cost</code></td>
      <td><strong>Snowflake (4X-Large)</strong></td>
      <td><a href="https://github.com/ClickHouse/examples/blob/main/blog-examples/Bench2Cost/snowflake/results_10B/4xl_enriched.json">~135 s</a></td>
      <td><a href="https://github.com/ClickHouse/examples/blob/main/blog-examples/Bench2Cost/snowflake/results_10B/4xl_enriched.json">~$14.41</a></td>
    </tr>
    <tr>
      <td><code>Fast & High-Cost</code></td>
      <td><strong>Databricks (4X-Large)</strong></td>
      <td><a href="https://github.com/ClickHouse/examples/blob/main/blog-examples/Bench2Cost/databricks/results_10B/clickbench_4X-Large_enriched.json">~188 s</a></td>
      <td><a href="https://github.com/ClickHouse/examples/blob/main/blog-examples/Bench2Cost/databricks/results_10B/clickbench_4X-Large_enriched.json">~$19.28</a></td>
    </tr>
    <tr>
      <td><code>Fast & High-Cost</code></td>
      <td><strong>BigQuery Enterprise (capacity)</strong></td>
      <td><a href="https://github.com/ClickHouse/examples/blob/main/blog-examples/Bench2Cost/bigquery/results_10B/result_enriched.json">~350 s</a></td>
      <td><a href="https://github.com/ClickHouse/examples/blob/main/blog-examples/Bench2Cost/bigquery/results_10B/result_enriched.json">~$11.73</a></td>
    </tr>
    <!-- BIGQUERY ON-DEMAND -->
    <tr>
      <td colspan="4"><strong>BigQuery On-Demand runs reasonably fast, but the on-demand billing model pushes its costs high, far outside the scatter plot’s axis range.</strong></td>
    </tr>
    <tr>
      <td><code>Fast & High-Cost</code> (off-chart)</td>
      <td><strong>BigQuery On-Demand</strong></td>
      <td><a href="https://github.com/ClickHouse/examples/blob/main/blog-examples/Bench2Cost/bigquery/results_10B/result_enriched.json">~350 s</a></td>
      <td><a href="https://github.com/ClickHouse/examples/blob/main/blog-examples/Bench2Cost/bigquery/results_10B/result_enriched.json">~$169</a></td>
    </tr>
    <!-- SLOW & LOWER COST -->
    <tr>
      <td colspan="4"><strong>Costs stay low, but runtimes drift into multi-minute or multi-hour territory.</strong></td>
    </tr>
    <tr>
      <td><code>Slow & Low-Cost</code></td>
      <td><strong>Snowflake (Large)</strong></td>
      <td><a href="https://github.com/ClickHouse/examples/blob/main/blog-examples/Bench2Cost/snowflake/results_10B/large_enriched.json">~1,213 s</a></td>
      <td><a href="https://github.com/ClickHouse/examples/blob/main/blog-examples/Bench2Cost/snowflake/results_10B/large_enriched.json">~$8.09</a></td>
    </tr>
    <tr>
      <td><code>Slow & Low-Cost</code></td>
      <td><strong>Snowflake (X-Small)</strong></td>
      <td><a href="https://github.com/ClickHouse/examples/blob/main/blog-examples/Bench2Cost/snowflake/results_10B/xs_enriched.json">~9,547 s (2.6 hours)</a></td>
      <td><a href="https://github.com/ClickHouse/examples/blob/main/blog-examples/Bench2Cost/snowflake/results_10B/xs_enriched.json">~$7.96</a></td>
    </tr>
    <!-- SLOW & HIGH COST -->
    <tr>
      <td colspan="4"><strong>These two are both slower <em>and</em> more expensive than far faster alternatives.</strong></td>
    </tr>
    <tr>
      <td><code>Slow & High-Cost</code></td>
      <td><strong>Redshift Serverless (128 RPU)</strong></td>
      <td><a href="https://github.com/ClickHouse/examples/blob/main/blog-examples/Bench2Cost/redshift-serverless/results_10B/enriched_10b.json">~1,068 s</a></td>
      <td><a href="https://github.com/ClickHouse/examples/blob/main/blog-examples/Bench2Cost/redshift-serverless/results_10B/enriched_10b.json">~$13.58</a></td>
    </tr>
    <tr>
      <td><code>Slow & High-Cost</code></td>
      <td><strong>Databricks (2X-Small)</strong></td>
      <td><a href="https://github.com/ClickHouse/examples/blob/main/blog-examples/Bench2Cost/databricks/results_10B/clickbench_2X-Small_enriched.json">~17,558 s (4.9 hours)</a></td>
      <td><a href="https://github.com/ClickHouse/examples/blob/main/blog-examples/Bench2Cost/databricks/results_10B/clickbench_2X-Small_enriched.json">~$13.66</a></td>
    </tr>
  </tbody>
</table>

When we look at the [cost-performance score](/blog/cloud-data-warehouses-cost-performance-comparison#how-we-measure-overall-cost-performance-ranking), the separation becomes unmistakable:

![Blog-Costs.012.png](https://clickhouse.com/uploads/Blog_Costs_012_7d7df43431.png)

The gap widens at 10 B rows:


* **ClickHouse Cloud remains the clear leader**, keeping the top cost-performance spot by a wide margin.

* **The next-best systems are already far behind**, landing **7×–13× worse** than ClickHouse (Snowflake 4X-L, Databricks Large, Databricks 4X-Large).

* **BigQuery Enterprise** falls even further, around **14× worse**.

* After that, everything collapses into the long tail, **tens to hundreds of times worse**, including Redshift Serverless (128 RPU), Snowflake L, BigQuery On-Demand, Snowflake X-Small, and Databricks 2X-Small.


> At 10 B rows, the economics diverge sharply: ClickHouse Cloud delivers an order-of-magnitude better value than any other system.


## 100B rows: the real stress test

The [scatter plot](/blog/cloud-data-warehouses-cost-performance-comparison#how-to-read-the-scatter-plot-charts) below shows, for each of the five systems, the total runtime (horizontal axis) and total compute cost (vertical axis) for a 100-billion-row ClickBench run.

*(As noted earlier, we hide the tick labels for visual clarity, the point positions still reflect the real underlying values. The interactive benchmark explorer above includes full numeric axes.)*

![Blog-Costs.014.png](https://clickhouse.com/uploads/Blog_Costs_014_291362ced8.png)
*(Shown configurations represent the full spectrum for each engine; [details in Appendix](/blog/cloud-data-warehouses-cost-performance-comparison#what-configurations-we-compare). **Because both axes are log scale, the vertical and horizontal jumps are even larger than they appear.**)*


At 100B rows, the separation becomes dramatic. ClickHouse Cloud is the only system that remains firm in the "Fast & Low-Cost" region, even at this scale.

Every other engine is now firmly pushed into "Slow & High-Cost", with runtimes in the multi-minute to multi-hour range and costs climbing an order of magnitude higher.



<table>
  <thead>
    <tr>
      <th>Category</th>
      <th>System / Tier</th>
      <th>Runtime</th>
      <th>Cost</th>
    </tr>
  </thead>
  <tbody>
    <!-- FAST & LOW COST -->
    <tr>
      <td colspan="4">
        <strong>ClickHouse Cloud is the only system that remains fast <em>and</em> low-cost at 100B rows; the sole system in the efficiency zone.</strong>
      </td>
    </tr>
    <tr>
      <td><code>Fast & Low-Cost</code></td>
      <td><strong>ClickHouse Cloud</strong> (<a href="https://clickhouse.com/blog/clickhouse-parallel-replicas">20 nodes</a>)</td>
      <td><a href="https://github.com/ClickHouse/examples/blob/main/blog-examples/Bench2Cost/clickhouse-cloud/results_100B/aws.20.236.parallel_replicas.json">~275 s</a></td>
      <td><a href="https://github.com/ClickHouse/examples/blob/main/blog-examples/Bench2Cost/clickhouse-cloud/results_100B/aws.20.236.parallel_replicas.json">~$17.62</a></td>
    </tr>
    <!-- SLOW & HIGH COST -->
    <tr>
      <td colspan="4">
        <strong>Every other system lands in the Slow & High-Cost quadrant at 100B rows, slower <em>and</em> significantly more expensive than ClickHouse.</strong>
      </td>
    </tr>
    <tr>
      <td><code>Slow & High-Cost</code></td>
      <td><strong>Databricks (4X-Large)</strong></td>
      <td><a href="https://github.com/ClickHouse/examples/blob/main/blog-examples/Bench2Cost/databricks/results_100B/clickbench_4X-Large_enriched.json">~1,049 s</a></td>
      <td><a href="https://github.com/ClickHouse/examples/blob/main/blog-examples/Bench2Cost/databricks/results_100B/clickbench_4X-Large_enriched.json">~$107.69</a></td>
    </tr>
    <tr>
      <td><code>Slow & High-Cost</code></td>
      <td><strong>Snowflake (4X-Large)</strong></td>
      <td><a href="https://github.com/ClickHouse/examples/blob/main/blog-examples/Bench2Cost/snowflake/results_100B/4xl_enriched.json">~1,212 s</a></td>
      <td><a href="https://github.com/ClickHouse/examples/blob/main/blog-examples/Bench2Cost/snowflake/results_100B/4xl_enriched.json">~$129.26</a></td>
    </tr>
    <tr>
      <td><code>Slow & High-Cost</code></td>
      <td><strong>BigQuery Enterprise (capacity)</strong></td>
      <td><a href="https://github.com/ClickHouse/examples/blob/main/blog-examples/Bench2Cost/bigquery/results_100B/result_enriched.json">~3,870 s</a></td>
      <td><a href="https://github.com/ClickHouse/examples/blob/main/blog-examples/Bench2Cost/bigquery/results_100B/result_enriched.json">~$126.52</a></td>
    </tr>
       <tr>
      <td><code>Slow & High-Cost</code> (off-chart)</td>
      <td><strong>BigQuery On-Demand</strong></td>
      <td><a href="https://github.com/ClickHouse/examples/blob/main/blog-examples/Bench2Cost/bigquery/results_100B/result_enriched.json">~3,870 s</a></td>
      <td><a href="https://github.com/ClickHouse/examples/blob/main/blog-examples/Bench2Cost/bigquery/results_100B/result_enriched.json">~$1,692.84</a></td>
    </tr>
    <tr>
      <td><code>Slow & High-Cost</code></td>
      <td><strong>Redshift Serverless (128 RPU)</strong></td>
      <td><a href="https://github.com/ClickHouse/examples/blob/main/blog-examples/Bench2Cost/redshift-serverless/results_100B/enriched_100b.json">~5,016 s</a></td>
      <td><a href="https://github.com/ClickHouse/examples/blob/main/blog-examples/Bench2Cost/redshift-serverless/results_100B/enriched_100b.json">~$55.06</a></td>
    </tr>
    <tr>
      <td><code>Slow & High-Cost</code></td>
      <td><strong>Databricks (Large)</strong></td>
      <td><a href="https://github.com/ClickHouse/examples/blob/main/blog-examples/Bench2Cost/databricks/results_100B/clickbench_Large_enriched.json">~11,821 s</a></td>
      <td><a href="https://github.com/ClickHouse/examples/blob/main/blog-examples/Bench2Cost/databricks/results_100B/clickbench_Large_enriched.json">~$91.94</a></td>
    </tr>
    <tr>
      <td><code>Slow & High-Cost</code></td>
      <td><strong>Snowflake (Large)</strong></td>
      <td><a href="https://github.com/ClickHouse/examples/blob/main/blog-examples/Bench2Cost/snowflake/results_100B/large_enriched.json">~21,119 s</a></td>
      <td><a href="https://github.com/ClickHouse/examples/blob/main/blog-examples/Bench2Cost/snowflake/results_100B/large_enriched.json">~$140.80</a></td>
    </tr>
  </tbody>
</table>

*(Smallest warehouse sizes for Snowflake and Databricks are not shown here; they would run for multiple days at 100B rows, far outside the range of this comparison.)*

And the [cost-performance score](/blog/cloud-data-warehouses-cost-performance-comparison#how-we-measure-overall-cost-performance-ranking) view makes the gap impossible to miss:

![Blog-Costs.015.png](https://clickhouse.com/uploads/Blog_Costs_015_a93e315273.png)

At 100 B rows, cost-performance spreads increase significantly:



* **ClickHouse Cloud remains the clear leader (best overall cost-performance).**

* The next-best system, **Databricks (4X-Large)**, falls all the way to **23× worse**.

* **Snowflake (4X-L)** follows at **32× worse**.

* **BigQuery Enterprise, Redshift Serverless (128 RPU), Databricks (Large), and Snowflake (L)** land in the **hundreds× worse** range.

* **BigQuery On-Demand** collapses to the bottom of the chart at **1,350× worse**.


> We stopped at **100 billion rows** not because ClickHouse Cloud reached a limit , [it didn’t](https://clickpy.clickhouse.com/), but because pushing the same benchmark to **1 trillion rows** and above would have been **prohibitively expensive** or multi-day runtime events for most of the other systems.<br/><br/>At 100B, several warehouses already incur **$100–$1,700** compute bills for a single ClickBench run, and smaller tiers would run for days.


## Who gives you the best cost-performance?

We began with a simple question. Now we can answer it with data:

> Where do you get the most performance per dollar for analytical workloads?

As we push to larger scales — 10B and then 100B rows — the trend becomes unmistakable: every major cloud data warehouse drifts toward “Slow & High-Cost.”

**Except one.**

Across all scales, including the 100B-row stress test, **ClickHouse Cloud is the only system that stays anchored in "Fast & Low-Cost"**, while every other system becomes slower, costlier, or both.

<br/>

![Blog-Costs-animation01_small.gif](https://clickhouse.com/uploads/Blog_Costs_animation01_small_de9ac301cc.gif)
<br/>

> **For analytical workloads at scale, ClickHouse Cloud delivers an order-of-magnitude better value than any other system.**

And here’s the kicker: Snowflake and Databricks were already at their hard limits, the largest warehouse sizes they offer.

ClickHouse Cloud has no such ceiling.

We stopped at 20 compute nodes not because ClickHouse Cloud hit a limit, but because the conclusion was already decisive.

If you’d like to see exactly how we ran the benchmark, the full methodology is included in the Appendix below.

<br/><br/>
## Appendix: Benchmark methodology

This section provides the full details of how we ran the benchmark and normalized pricing across all five systems.


### The benchmark setup

We based this analysis on [ClickBench](https://benchmark.clickhouse.com/), which uses a **[production-derived, anonymized dataset](https://github.com/ClickHouse/ClickBench/?tab=readme-ov-file#overview)** and **43 realistic analytical queries** (clickstream, logs, dashboards, etc.) rather than synthetic data.

But the standard dataset is ~100 M rows, tiny by current standards. Today’s datasets are frequently in billions, trillions, even quadrillions. [Tesla ingested over one quadrillion rows into ClickHouse for a load test](https://clickhouse.com/blog/how-tesla-built-quadrillion-scale-observability-platform-on-clickhouse#proving-the-system-at-scale), and [ClickPy](https://clickpy.clickhouse.com/), our Python client telemetry dataset, has already surpassed [two trillion rows](https://sql.clickhouse.com/?query=U0VMRUNUCiAgICAgICAgZm9ybWF0UmVhZGFibGVRdWFudGl0eShzdW0oY291bnQpKSBBUyB0b3RhbCwgdW5pcUV4YWN0KHByb2plY3QpIGFzIHByb2plY3RzIEZST00gcHlwaS5weXBpX2Rvd25sb2Fkcw&run_query=true).

To understand how cost and performance evolve as data grows, **we extended ClickBench to 1B, 10B, and 100B rows** and reran the full 43-query benchmark at all three scales.

*To keep results fair and reproducible, we followed the standard [ClickBench rules](https://github.com/ClickHouse/ClickBench/?tab=readme-ov-file#overview): no tuning, no engine-specific optimizations, and no changes to min/max compute settings. This ensures that all results reflect how each system behaves out of the box, without hand-tuning or workload-specific tricks (e.g., precalculating aggregations with materialized views).*

To make results comparable across systems with incompatible billing models, we used the [Bench2Cost framework](/blog/how-cloud-data-warehouses-bill-you#before-we-dive-in-how-we-calculate-costs-with-bench2cost) from the companion post. It takes the raw per-query runtimes, applies each vendor’s actual compute pricing model, and produces a unified dataset containing **runtime, and compute cost** for every query on every system, plus **storage cost, and system metadata**.


### What configurations we compare

While the interactive benchmark explorer lets you compare *all* tiers and cluster sizes, for this post, we keep the comparison simple and consistent:



* **[Snowflake](/blog/how-cloud-data-warehouses-bill-you#snowflake) and [Databricks](/blog/how-cloud-data-warehouses-bill-you#databricks-sql-serverless)**: we include three warehouse sizes each, the **smallest**, a **mid-range size**, and the **largest** Enterprise-tier size, to cover their full practical spectrum. *(For more Snowflake-specific details, including Gen 2 warehouses, QAS, and new warehouse sizes, see the note below.)*

* **[ClickHouse Cloud](/blog/how-cloud-data-warehouses-bill-you#clickhouse-cloud)**: ClickHouse Cloud has no fixed warehouse shapes, so “small / medium / large” tiers don’t exist. Instead, we use **one fixed ClickHouse Cloud Enterprise-tier configuration** per dataset size.

* **[BigQuery](/blog/how-cloud-data-warehouses-bill-you#bigquery)**: BigQuery appears twice in the charts because it is a fully serverless system with no concept of cluster sizes, but it offers two billing models. We run the workload once (with a base capacity of 2000 slots), then price the same runtimes using both Enterprise (used **slot capacity-based**) pricing and **On-demand** (per scanned TiB) pricing.

* **[Redshift Serverless](/blog/how-cloud-data-warehouses-bill-you#redshift-serverless)**: Redshift Serverless appears once, because it likewise has no warehouse sizes or tiers. We use the **default 128-RPU base configuration**.


All pricing is taken for the same cloud provider and region (AWS us-east) where applicable; BigQuery is the exception and uses GCP us-east.

Where vendors offer multiple pricing tiers (e.g., Enterprise vs. Standard/Basic), we use the Enterprise tier for consistency, but the relative cost-performance differences remain broadly the same across tiers. You can verify this by exploring the alternative tiers in the interactive benchmark explorer.

This keeps the comparison fair, interpretable, and consistent across 1B, 10B, and 100B rows.

### A note on Snowflake Gen2, QAS, new warehouse sizes, and Interactive Warehouses

For this benchmark, we used **Snowflake’s standard Gen 1 warehouses**, which remain the default configuration in most regions today.

[Gen 2 warehouses](https://docs.snowflake.com/en/en/user-guide/warehouses-gen2) consume [25–35% more credits/hour for the same t-shirt size](https://www.snowflake.com/legal-files/CreditConsumptionTable.pdf), and their availability varies by cloud/region, so focusing on Gen 1 keeps the comparison consistent across environments.

We also **did not enable Snowflake’s Query Acceleration Service ([QAS](https://docs.snowflake.com/en/user-guide/query-acceleration-service))**.<br/>
QAS adds **serverless burst compute** on top of the warehouse, which can accelerate spiky or scan-heavy query fragments, but because [it introduces an additional billing dimension](https://docs.snowflake.com/en/user-guide/query-acceleration-service#query-acceleration-service-cost), we keep it out of this study to maintain a clean, baseline comparison.

Snowflake has also introduced **warehouse sizes larger than 4X-Large** - [specifically](https://docs.snowflake.com/en/user-guide/warehouses-overview#warehouse-size) **5X-Large** and **6X-Large**. These [launched in early 2024](https://docs.snowflake.com/en/release-notes/performance-improvements-2024) and have since expanded across clouds, but 4X-Large remains the most widely used upper tier, so we chose it as the maximum size here.

Snowflake’s [Interactive warehouses](https://docs.snowflake.com/en/user-guide/interactive) (preview) are optimized for low-latency, high-concurrency workloads. They are [priced lower](https://www.snowflake.com/legal-files/CreditConsumptionTable.pdf) per hour than standard warehouses (e.g., 0.6 vs 1 credit/hour at XS), but they enforce a [5-second timeout for SELECT queries](https://docs.snowflake.com/en/user-guide/interactive#limitations-of-interactive-warehouses) and carry a [1-hour minimum billing period](https://docs.snowflake.com/en/user-guide/interactive#cost-and-billing-considerations), with each resume triggering a full minimum charge. 

> Snowflake offers many mutually interacting performance variables — Gen 1 vs Gen 2, QAS, 5XL/6XL tiers, Interactive Warehouses. We intentionally avoided mixing these into the initial benchmark to keep the comparison clean. A Snowflake-specific follow-up piece will explore these configurations in depth.

###  A note on hot vs cold runtimes

In line with ClickBench, we report **hot** runtimes, defined as the best of three runs, and we **disabled query result caches** everywhere they exist. Cold-start benchmarking isn’t included: cloud warehouses expose very different data caching behaviors, and most don’t allow resetting OS-level page cache or restarting compute on demand. Because cold conditions can’t be standardized, they would produce neither fair nor reproducible results.

###  A note on native storage formats

Each system in this benchmark is evaluated using **its query engine’s native storage format**, for example, MergeTree in ClickHouse Cloud, Delta Lake on Databricks, Snowflake’s proprietary micro-partition format, and BigQuery’s Capacitor columnar storage. This ensures we measure each engine under the conditions it is designed and optimized for.

As a side note, several systems, including Snowflake and ClickHouse Cloud, can also query open table formats such as Delta Lake, Apache Iceberg, or Apache Hudi directly. However, this study focuses strictly on native performance and cost. A separate benchmark comparing these engines over open table formats is planned. Stay tuned.

### A note on metering granularity

To keep the comparison consistent across all five systems, we make one simplification:

**We treat all systems as if they billed compute with perfect per-second granularity.**

In reality, as detailed in the [companion post](/blog/how-cloud-data-warehouses-bill-you):



* Snowflake, Databricks, and ClickHouse Cloud only stop billing after an idle timeout, and each has a **1-minute minimum charge** when a warehouse/service is running.

* BigQuery and Redshift Serverless meter usage **per second**, but still apply **minimum charge windows** (e.g., BigQuery’s 1-minute minimum for slot consumption; Redshift Serverless’s 1-minute minimum for RPU usage).


### A note on scope and feature differences

This analysis looks at a single question:

> What does it cost to run an analytical workload as data scales?

To keep the comparison clean, we intentionally **focus only on compute cost** for the 43-query benchmark. We **do not** attempt to compare broader platform features (governance, ecosystem integrations, workload management, lakehouse capabilities, ML tooling, etc.), even though those can indirectly influence how vendors price compute.


### How we measure “Overall cost-performance ranking”

To compare systems with completely different billing models, we use one simple, scale-independent metric:

`Cost-performance score = runtime × cost`

*(smaller is better)*

This metric captures the intuition behind a cost-performance ranking:



* **Fast systems score better**
* **Low-cost systems score better**
* **Slow or High-cost systems balloon immediately**
* **Cost and runtime compound**; inefficiencies multiply each other


It directly answers the question we care about:

> **How expensive is it for this system to complete the workload?**

We normalize all results so the **best system becomes the baseline (1×)**, and every other system is shown as **N× worse**, making the ranking easy to compare at a glance.


### How to read the scatter plot charts

Two quick notes on how to read the “total runtime vs total compute cost” scatter plots we are using in the sections above:



* **Both axes use a logarithmic scale.** The differences between systems span orders of magnitude at larger data volumes, so a log–log view keeps everything readable.

* **To make the plots easier to interpret at a glance, we overlaid four quadrants** (“Fast & Low-Cost”, “Fast & High-Cost”, etc.). These quadrants are **purely visual**. They are **not** based on medians or any statistical cut-point. just a simple way to orient the reader.


What’s interesting is how systems move between quadrants as the dataset grows.



