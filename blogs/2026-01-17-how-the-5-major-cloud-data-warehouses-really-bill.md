---
title: "How the 5 major cloud data warehouses really bill you: A unified, engineer-friendly guide"
date: "2025-11-27T12:30:01.434Z"
author: "Tom Schreiber & Lionel Palacin"
category: "Engineering"
excerpt: "This guide explains how the five major cloud data warehouses—Snowflake, Databricks, ClickHouse Cloud, BigQuery, and Redshift—allocate, meter, and bill compute, giving engineers a clear understanding of what the billing units mean and how to compare them."
---

# How the 5 major cloud data warehouses really bill you: A unified, engineer-friendly guide

> **TL;DR**<br/><br/>Price lists don’t tell you real costs.<br/><br/>Compute models do.<br/><br/>This post explains how all five major cloud data warehouses actually turn your queries into dollars, so you can compare them on equal footing.<br/><br/>**If you build, optimize, or pay for analytical workloads, this gives you the lens you need to understand true compute costs.**

<br/>

**Prefer a visual walkthrough?**<br/>
This post started as a whiteboard-style walkthrough of how the major cloud data warehouses actually turn queries into compute costs.
If you’d rather watch the explanation, the video below covers the same mental model and examples.

<iframe width="768" height="432" src="https://www.youtube.com/embed/cEhFUefOOfA?si=lJlMZkVJPnrrOeFe" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

*(The video follows the same structure as this post, so you can switch between reading and watching at any point.)*

<br/>

## Why compute billing is so confusing

You have a dataset and a set of analytical queries. You have more cloud data warehouse options than ever. And before you can answer the obvious question:

> Which one gives you the best performance per dollar?

You need to understand something much simpler:

> How do these systems actually bill you for compute?

That should be straightforward. Every vendor has a public price list. But in practice, price lists are almost meaningless because:

* Each platform measures compute differently (“credits”, “DBUs”, “compute units”, “slot-seconds”, “RPUs”, …)

* These units map to fundamentally different execution models

* Query runtimes scale differently as data grows

* And the same query can burn radically different amounts of compute depending on the query engine


So even with all price lists in front of you, you still can’t answer “which one is cheaper?” Not without understanding what their billing units *really* mean.

This post is step 1 in that journey:

> A clear, no-nonsense explanation of how all five major cloud data warehouses allocate, scale, and bill compute.

When you’re done, you’ll understand how CPU cycles become dollars in:



* **Snowflake**

* **Databricks (SQL Serverless)**

* **ClickHouse Cloud**

* **Google BigQuery**

* **Amazon Redshift Serverless**

>**What about storage costs?**<br/>This post focuses entirely on **compute costs**, because that’s where the real differences between systems lie. Storage costs, by comparison, are **much simpler** and, crucially, often **negligible relative to compute**, since most systems store data in low-cost cloud object storage with very similar pricing.
That said, our **Bench2Cost** framework (see next section) does fully calculate storage costs for every system. We simply don’t highlight them here because they don’t materially affect the comparison.

## Before we dive in: How we calculate costs with Bench2Cost

This post is the foundation for a broader cost-comparison analysis we built on top of [ClickBench](https://benchmark.clickhouse.com).

> If you’re here only to understand how each system’s compute model and billing work, you can skip this section and the small **How Bench2Cost computes … costs** subsections at the end of each system. Those parts are only relevant if you want to see how we translate benchmark results into real dollar costs for the [companion cost-comparison analysis](https://clickhouse.com/blog/cloud-data-warehouses-cost-performance-comparison).

To make benchmark results comparable across systems with radically different billing models, we built a framework for attaching real price tags to ClickBench (or any benchmark, really). We call it **Bench2Cost**.

Everything in this study is fully reproducible; the [Bench2Cost repository](https://github.com/ClickHouse/examples/tree/main/blog-examples/Bench2Cost) includes all scripts, pricing models, and generated datasets we used.

At a high level, Bench2Cost does three things:

1. **Takes existing raw ClickBench runtimes**
2. **Looks up the system’s compute pricing model**
3. **Produces an enriched JSON file** that contains, for every query:
    * runtime
    * compute cost

*(Additionally, Bench2Cost also calculates storage costs.)*

Each system’s section later in this post contains a small **How Bench2Cost computes … costs** subsection at the end that shows how exactly we applied Bench2Cost to each system (e.g., which benchmark file we used, what pricing data we mapped in, etc.).

This allows us to perform a clean comparison of the costs-per-benchmark across Snowflake, Databricks, ClickHouse Cloud, BigQuery, and Redshift Serverless.

With that foundation in place, let’s walk through how each system actually allocates and bills compute.

## Snowflake

<div style="border-radius:12px; padding:24px 28px; margin:28px 0; background:#111317; border:1px solid #1f242a; box-shadow:0 8px 18px rgba(0,0,0,0.45); color:#f4f4f5;">
  <div style="font-size:20px; font-weight:600; margin:0 0 4px;">Snowflake compute pricing TL;DR</div>
  <div style="font-size:14px; color:#9ca3af; margin:0;">Warehouses are fixed t-shirt sizes; each size consumes a fixed number of credits per hour while running.<br/>(Values shown are for standard Gen 1 warehouses.)</div>
  <div style="font-size:13px; color:#6b7280; margin-top:4px;">(Prices as of November 2025)</div>
  <div style="height:1px; background:#1d2126; margin:16px 0 20px;"></div>
  <div style="display:flex; gap:40px; flex-wrap:wrap;">
    <div style="flex:1; min-width:260px;">
      <div style="font-weight:600; margin-bottom:6px;">Billing units</div>
      <ul style="margin:0; padding-left:20px;">
        <li><strong style="color:#fdff88;">Credits per hour</strong> (Snowflake’s compute billing unit)</li>
      </ul>
      <div style="font-weight:600; margin-top:18px; margin-bottom:6px;">Example warehouse sizes</div>
      <ul style="margin:0; padding-left:20px;">
        <li>X-Small → <strong style="color:#fdff88;">1 credit / hour</strong></li>
        <li>Small → <strong style="color:#fdff88;">2 credits / hour</strong></li>
        <li>Medium → <strong style="color:#fdff88;">4 credits / hour</strong></li>
      </ul>
    </div>
    <div style="flex:1; min-width:260px;">
      <div style="font-weight:600; margin-bottom:6px;">Price per credit (AWS, US East)</div>
      <ul style="margin:0; padding-left:20px;">
        <li>Standard: <strong style="color:#fdff88;">$2.00 / credit / hour</strong></li>
        <li>Enterprise: <strong style="color:#fdff88;">$3.00 / credit / hour</strong></li>
        <li>Business Critical: <strong style="color:#fdff88;">$4.00 / credit / hour</strong></li>
      </ul>
    </div>
  </div>
</div>

### Compute model: provisioned warehouses

Snowflake is the canonical example of a **provisioned-cluster compute model**: you choose a warehouse size and pay for its uptime, not per individual query.

Under the hood, Snowflake’s warehouses are fixed-size clusters that run Snowflake’s query engine (engine paper: [The Snowflake Elastic Data Warehouse](https://www.cs.cmu.edu/~15721-f24/papers/Snowflake.pdf)).

Each warehouse has a **t-shirt size** (XS, S, M, …), and that size determines both:

* **How many compute nodes you get** (shown in the diagram below)
* **How many “credits” are consumed per hour**

For example:



* **XS → 1 node → 1 credit/hour**
* **S → 2 nodes → 2 credits/hour**
* **M → 4 nodes → 4 credits/hour**

![Blog-Costs.001.png](https://clickhouse.com/uploads/Blog_Costs_001_aa09baa628.png)
*(Note: Snowflake does not publish hardware specs, but it is widely [understood](https://select.dev/posts/snowflake-warehouse-sizing) that each node roughly corresponds to **8 vCPUs, 16 GiB RAM, and ~200 GB local disk cache**.)*


> **Note on Snowflake warehouse generations and Interactive warehouses**:<br/><br/>
All examples in this guide use Snowflake’s standard (Gen 1) warehouses, which remain the default unless users explicitly select Gen2.<br/><br/>Snowflake’s newer [Gen 2 warehouses](https://docs.snowflake.com/en/en/user-guide/warehouses-gen2) run on updated hardware and [consume 25–35% more credits per hour than Gen 1 for the same size](https://www.snowflake.com/legal-files/CreditConsumptionTable.pdf).<br/><br/>
Snowflake’s [Interactive warehouses](https://docs.snowflake.com/en/user-guide/interactive) (in preview as of November 2025) are optimized for low-latency, high-concurrency workloads. They are [priced lower](https://www.snowflake.com/legal-files/CreditConsumptionTable.pdf) per hour than standard warehouses (e.g., 0.6 vs 1 credit/hour at XS), but they enforce a [5-second timeout for SELECT queries](https://docs.snowflake.com/en/user-guide/interactive#limitations-of-interactive-warehouses) and carry a [1-hour minimum billing period](https://docs.snowflake.com/en/user-guide/interactive#cost-and-billing-considerations), with each resume triggering a full minimum charge. 

### Scaling: vertical vs. multi-cluster

Snowflake scales in two ways, and **each form of scaling affects your bill**:



1. Vertical scaling (manual resize)<br/><br/>



    * You manually choose a bigger warehouse size (e.g., **S → M → L**)
    
    * More nodes → more parallelism → faster queries…but also **more credits/hour**, billed linearly.
    
    
2. Horizontal scaling (multi-cluster, automatic)<br/><br/>



    * Snowflake can automatically add more clusters of the **same size** when concurrency spikes.
    * These extra clusters **do not speed up single queries**; they only provide additional capacity for incoming queries, thereby preventing queries from queuing up.
    * Snowflake’s Standard/Economy [policies](https://docs.snowflake.com/en/user-guide/warehouses-multicluster#setting-the-scaling-policy-for-a-multi-cluster-warehouse) control when extra clusters start/stop.
    * Each active extra cluster **bills its own credits/hour**, identical to the primary cluster.


### **Query Acceleration Service (QAS)**

Snowflake offers an optional enterprise-level feature called **[Query Acceleration Service (QAS)](https://docs.snowflake.com/en/user-guide/query-acceleration-service)**.

When enabled, Snowflake will automatically use **additional serverless compute resources** to accelerate “spiky” or scan-heavy parts of a query.

Note that [this introduces an additional billing dimension](https://docs.snowflake.com/en/user-guide/query-acceleration-service#query-acceleration-service-cost).

### Compute pricing

*(Official pricing, November 2025 → [https://www.snowflake.com/en/pricing-options](https://www.snowflake.com/en/pricing-options/))*

Pricing depends on **Edition** (Standard, Enterprise, Business Critical) and **Cloud/Region**, e.g. in AWS, US-East:



* **Standard → $2.00 per credit/hour**
* **Enterprise → $3.00 per credit/hour**
* **Business Critical → $4.00 per credit/hour**


### Metering granularity

*(Metering behavior, November 2025 → Snowflake docs: [How credits are charged](https://docs.snowflake.com/en/user-guide/warehouses-considerations#how-are-credits-charged-for-warehouses))*

Snowflake bills per second, with a 1-minute minimum each time a warehouse is running.

Warehouses support AUTO-SUSPEND and AUTO-RESUME, so you can automatically shut them down after a period of inactivity and restart when a query arrives. You are billed while the warehouse is running, regardless of actual CPU usage.

Warehouse AUTO-RESUME is generally very fast (e.g. [1 or 2 seconds](https://docs.snowflake.com/en/user-guide/warehouses-considerations?utm_source=chatgpt.com#automating-warehouse-suspension)); depending on the size of the warehouse and the availability of compute resources to provision, it can take longer.

> **Interactive warehouses** meter per second but enforce a [1-hour minimum](https://docs.snowflake.com/en/user-guide/interactive#cost-and-billing-considerations), and every resume starts a new minimum billing window. 


### How Bench2Cost computes Snowflake costs

<details>
  <summary>Click to see the pricing logic</summary>
<p>
<br/>
To translate Snowflake’s ClickBench runtimes into dollars, we applied our “Bench2Cost” pipeline, which joins existing <strong>raw benchmark timings</strong>, <strong>warehouse configuration</strong>, and <strong>Snowflake’s pricing tables</strong> into one unified cost dataset.
</p>
<p>
<br/>
Snowflake’s ClickBench results (e.g., <a href="https://github.com/ClickHouse/examples/blob/main/blog-examples/Bench2Cost/snowflake/clickbench/results_100b/4xl.json">4xl.json</a>) contain runtimes measured on a fixed warehouse size, in this case a <strong>4X-Large (128 credits/hour)</strong> warehouse.
</p>
<p>
<br/>
Separately, we encoded Snowflake’s official pricing data (warehouse T-shirt sizes, credits/hour, and per-credit dollar prices across editions and regions) into <a href="https://github.com/ClickHouse/examples/blob/main/blog-examples/Bench2Cost/snowflake/pricings/standard_warehouse.json">standard_warehouse.json</a>.
</p>
<p>
<br/>
A script (<a href="enrich.sh">enrich.sh</a>) merges these inputs:
</p>
<ul>

<li>identifies the warehouse size used in the benchmark (e.g., 4X-Large)</li>

<li>multiplies each query’s runtime by <strong>credits/hour × price per credit</strong></li>

<li>attaches Snowflake storage pricing</li>

<li>outputs a fully enriched file (<a href="https://github.com/ClickHouse/examples/blob/main/blog-examples/Bench2Cost/snowflake/results_100B/4xl_enriched.json">4xl_enriched.json</a>) containing:</li>
<ul>

<li>per-query runtime</li>

<li>per-query compute cost</li>

<li>total monthly storage cost</li>
</ul></li>
</ul>
<p>
This enriched dataset is what we use later in the <a href="https://clickhouse.com/blog/cloud-data-warehouses-cost-performance-comparison">high-level comparison post</a> where we evaluate cost-per-benchmark across the five systems.
</p>
</details>

Databricks uses a similar provisioned-cluster model, but replaces Snowflake’s credits with DBUs.


## Databricks (SQL Serverless)

<div style="border-radius:12px; padding:24px 28px; margin:28px 0; background:#111317; border:1px solid #1f242a; box-shadow:0 8px 18px rgba(0,0,0,0.45); color:#f4f4f5;">
  <div style="font-size:20px; font-weight:600; margin:0 0 4px;">Databricks compute pricing TL;DR</div>
  <div style="font-size:15px; color:#9ca3af; margin:0;">Each SQL warehouse size has a fixed DBU burn-rate per hour.</div>
  <div style="font-size:13px; color:#6b7280; margin-top:4px;">(Prices as of November 2025)</div>
  <div style="height:1px; background:#1d2126; margin:16px 0 20px;"></div>
  <div style="display:flex; gap:40px; flex-wrap:wrap;">
    <div style="flex:1; min-width:260px;">
      <div style="font-weight:600; margin-bottom:6px;">Billing units</div>
      <ul style="margin:0; padding-left:20px;">
        <li><strong style="color:#fdff88;">DBUs per hour</strong> (DBU = Databricks Unit, Databricks’ abstract compute billing unit)</li>
      </ul>
      <div style="font-weight:600; margin-top:18px; margin-bottom:6px;">Example warehouse sizes</div>
      <ul style="margin:0; padding-left:20px;">
        <li>2X-Small → <strong style="color:#fdff88;">4 DBUs / hour</strong></li>
        <li>Small → <strong style="color:#fdff88;">12 DBUs / hour</strong></li>
        <li>Medium → <strong style="color:#fdff88;">24 DBUs / hour</strong></li>
      </ul>
    </div>
    <div style="flex:1; min-width:260px;">
      <div style="font-weight:600; margin-bottom:6px;">Price per DBU (AWS, US East)</div>
      <ul style="margin:0; padding-left:20px;">
        <li>Premium: <strong style="color:#fdff88;">$0.70 / DBU / hour</strong></li>
        <li>Enterprise: <strong style="color:#fdff88;">$0.70 / DBU / hour</strong></li>
      </ul>
    </div>
  </div>
  <div style="font-size:12px; color:#6b7280; margin-top:16px;">
    (Note: Premium and Enterprise DBU prices are identical as of November 2025. This is not a typo.)
  </div>
</div>

### Compute model: fixed-shape warehouses

Like Snowflake, Databricks SQL Serverless uses a **provisioned-cluster model**: you pick a warehouse size, and Databricks brings up a **fixed-shape cluster** (engine paper: [Photon: A Fast Query Engine for Lakehouse Systems](https://people.eecs.berkeley.edu/~matei/papers/2022/sigmod_photon.pdf)) that runs until you shut it down or it auto-stops when idle.

Each warehouse size (2X-Small, Small, Medium, …) corresponds to a fixed cluster with:

* **One driver node**
* **Multiple executor nodes** (the main cost driver)


Your chosen **cluster size** determines:



* **How many executors you get**
* **How many DBUs per hour the cluster burns** (DBU = Databricks Unit, Databricks’ abstract compute billing unit)


Examples:

* **2X-Small** → ~1 executor → **4 DBUs/hour**
* **Small** → ~3 executors → **12 DBUs/hour**
* **Medium** → ~6 executors → **24 DBUs/hour**

![Blog-Costs.002.png](https://clickhouse.com/uploads/Blog_Costs_002_c7cc179f23.png)
*(Note that Databricks abstracts the exact hardware and node counts, so the diagram is illustrative, not literal. For clarity, we omit driver nodes.)*

Larger sizes mean more executors → more parallelism → faster queries.

But **billing is strictly linear with DBUs/hour**, regardless of how much CPU your queries actually consume internally.


### Scaling: vertical vs multi-cluster

Databricks warehouses scale in two ways, and each directly affects your cost:

**1. Vertical scaling (manual resize)**



* You explicitly choose a bigger warehouse size (2X-Small → Small → Medium).
* Larger sizes have more executors and burn proportionally more **DBUs/hour**.
* This makes individual queries faster, but increases hourly burn.

**2. Horizontal scaling (multi-cluster, automatic)**



* In the UI you set **Min / Max clusters** for a given size.
* When concurrency increases, Databricks automatically launches **additional clusters of the same size** to handle queued queries.
* **These extra clusters do not speed up single queries**; they only provide additional capacity for incoming queries, thereby preventing queries from queuing up.
* **Each extra cluster bills its own DBUs/hour** while it is active. \
Example: running 3 × “Small” clusters means **3 × 12 DBUs/hour**.


### Compute pricing

*(Official pricing, November 2025 → [https://www.databricks.com/product/pricing/databricks-sql](https://www.databricks.com/product/pricing/databricks-sql))*

Finally, DBU → USD conversion depends on:



* **Edition / tier** (Standard, Premium, Enterprise)
* **Cloud & region** (AWS, Azure, GCP)

Typical AWS (US-East) pricing:



* **Premium** → ~$0.70 / DBU/hour
* **Enterprise** → ~$0.70 / DBU/hour

*(Note: Premium and Enterprise DBU prices are identical as of November 2025. This is not a typo.)*

### Metering granularity

*(Metering behavior, November 2025 → Databrick docs: [How does Databricks pricing work?](https://www.databricks.com/product/databricks-pricing))*

Databricks bills DBUs with per-second granularity while the warehouse is active.

SQL Warehouses have an auto-stop idle timeout, so you can automatically shut them down after a configured period of inactivity.

Warehouses automatically start again (“auto-start”) when a new query arrives.

Billing continues until the warehouse fully stops, regardless of CPU utilization.

Warehouses have a rapid startup time (typically [between 2 and 6 seconds](https://docs.databricks.com/aws/en/compute/sql-warehouse/warehouse-types?utm_source=chatgpt.com#serverless-sql-warehouses)).


### How Bench2Cost computes Databricks costs

<details>
  <summary>Click to see the pricing logic</summary>
<p>
<br/>
To convert Databricks’ ClickBench runtimes into dollars, we ran the same <strong>Bench2Cost</strong> pipeline used for Snowflake, this time joining the raw benchmark timings with Databricks’ <strong>warehouse-size → DBUs/hour</strong> mapping and <strong>DBU → dollar </strong>pricing.
</p>
<p>
<br/>
For example, a Databricks ClickBench file (<a href="https://github.com/ClickHouse/examples/blob/main/blog-examples/Bench2Cost/databricks/clickbench/large/results_100B/clickbench_4X-Large.json">clickbench_4X-Large.json</a>) contains runtimes measured on a fixed SQL warehouse size, here a <strong>4X-Large</strong> warehouse (528 DBUs/hour).
</p>
<p>
<br/>
Separately, we encoded Databricks’ official pricing tables (cluster sizes, DBUs/hour, and DBU prices per cloud/region/tier) into <a href="https://github.com/ClickHouse/examples/blob/main/blog-examples/Bench2Cost/databricks/pricings/sql_serverless_compute.json">sql_serverless_compute.json</a>.
</p>
<p>
<br/>
The enrichment script (<a href="enrich.sh">enrich.sh</a>) merges these inputs and:
</p>
<ul>

<li>detects the warehouse size used in the benchmark (4X-Large)</li>

<li>multiplies each query’s runtime by <strong>DBUs/hour × DBU price</strong></li>

<li>attaches Databricks storage pricing</li>

<li>writes out an enriched file (<a href="https://github.com/ClickHouse/examples/blob/main/blog-examples/Bench2Cost/databricks/results_100B/clickbench_4X-Large_enriched.json">clickbench_4X-Large_enriched.json</a>) containing</li>
<ul>

<li>per-query runtime</li>

<li>per-query compute cost</li>

<li>total storage cost</li>
</ul></li>
</ul>
<p>
This enriched dataset feeds into the <a href="https://clickhouse.com/blog/cloud-data-warehouses-cost-performance-comparison">high-level comparison post</a> where we evaluate the <strong>true cost-per-benchmark</strong> across all five systems.
</p>
</details>

ClickHouse Cloud also uses provisioned compute, but with fully flexible node sizes and a normalized billing unit.


## ClickHouse Cloud

<div style="border-radius:12px; padding:24px 28px; margin:28px 0; background:#111317; border:1px solid #1f242a; box-shadow:0 8px 18px rgba(0,0,0,0.45); color:#f4f4f5;">
  <div style="font-size:20px; font-weight:600; margin:0 0 4px;">ClickHouse Cloud compute pricing TL;DR</div>
  <div style="font-size:15px; color:#9ca3af; margin:0;">A service size defines how many compute units your cluster consumes per hour.</div>
  <div style="font-size:13px; color:#6b7280; margin-top:4px;">(Prices as of November 2025)</div>
  <div style="height:1px; background:#1d2126; margin:16px 0 20px;"></div>
  <div style="display:flex; gap:40px; flex-wrap:wrap;">
    <div style="flex:1; min-width:260px;">
      <div style="font-weight:600; margin-bottom:6px;">Billing units</div>
      <ul style="margin:0; padding-left:20px;">
        <li><strong style="color:#fdff88;">Compute units per hour</strong> (1 compute unit = 8 GiB RAM + 2 vCPU)</li>
      </ul>
      <div style="font-weight:600; margin-top:18px; margin-bottom:6px;">Example service sizes</div>
      <ul style="margin:0; padding-left:20px;">
        <li>2-node service (8 GiB RAM / node) → <strong style="color:#fdff88;">2 compute units / hour</strong></li>
        <li>3-node service (16 GiB RAM / node) → <strong style="color:#fdff88;">6 compute units / hour</strong></li>
        <li>4-node service (32 GiB RAM / node) → <strong style="color:#fdff88;">16 compute units / hour</strong></li>
      </ul>
    </div>
    <div style="flex:1; min-width:260px;">
      <div style="font-weight:600; margin-bottom:6px;">Price per compute unit (AWS, US East)</div>
      <ul style="margin:0; padding-left:20px;">
        <li>Basic: <strong style="color:#fdff88;">$0.22 / unit / hour</strong></li>
        <li>Scale: <strong style="color:#fdff88;">$0.30 / unit / hour</strong></li>
        <li>Enterprise: <strong style="color:#fdff88;">$0.39 / unit / hour</strong></li>
      </ul>
    </div>
  </div>
</div>

### Compute model: flexible services, compute units

ClickHouse Cloud is a provisioned-compute service built on the ClickHouse engine (engine paper: [ClickHouse - Lightning Fast Analytics for Everyone](https://www.vldb.org/pvldb/vol17/p3731-schulze.pdf)), but with fully flexible node sizing instead of fixed warehouse shapes.

A service has two independent dimensions:

**1. Number of compute nodes (horizontal dimension)**



* You choose **any number of nodes** for a service—1, 2, 3… or dozens, or hundreds.

* This controls both **inter-query scaling** (how many queries can run concurrently) and **intra-query scaling** ([how much parallel CPU+RAM a single query can use across nodes](https://clickhouse.com/blog/clickhouse-parallel-replicas)).

**2. Size of each compute node (vertical dimension)**



* Each compute node can be provisioned with a **wide range of RAM/vCPU configurations.**
* Examples include 8 GiB/2 vCPU, 16 GiB/4 vCPU, 32 GiB/8 vCPU, all the way to 356 GiB/89 vCPU, and many intermediate sizes.

To bill such flexible service sizes uniformly, ClickHouse uses a **normalized compute unit**:

**1 compute unit = 8 GiB RAM + 2 vCPU**

All possible DRAM/vCPU node configurations are multiples of this.

ClickHouse Cloud calculates the total compute units for a service as:

**Total compute units = (# of nodes) × (compute units per node)**

A service consumes **exactly its total number of compute units per hour** while it is running.

The diagram below shows typical examples:



* **2-node service with 8 GiB RAM + 2 vCPU per node**
  <br/>→ 1 compute unit per node
  <br/>→ **2 compute units/hour**

* **3-node service with 16 GiB RAM + 4 vCPU per node**
  <br/>→ 2 compute units per node
  <br/>→ **6 compute units/hour**

* **4-node service with 32 GiB RAM + 8 vCPU per node**
  <br/>→ 4 compute units per node
  <br/>→ **16 compute units/hour**

This is different from Snowflake and Databricks: node sizes aren’t tied to fixed t-shirt sizes.

![Blog-Costs.003.png](https://clickhouse.com/uploads/Blog_Costs_003_927c26b1a7.png)

### Scaling: auto-vertical + manual horizontal

ClickHouse Cloud scales in two ways, and both directly affect how many **compute units/hour** a service consumes.

**1. Vertical scaling (change size of all nodes, automatically)**

In ClickHouse Cloud, node size (RAM + vCPUs) can scale [automatically](https://clickhouse.com/docs/manage/scaling) up and down based on CPU and memory pressure, within a configurable min/max range.

This contrasts with systems like Snowflake and Databricks, where vertical scaling is always manual, and you must explicitly choose a larger or smaller warehouse/cluster.

**2. Horizontal scaling (add or remove nodes, manually)**

Unlike Snowflake or Databricks, where clusters have a hard upper compute size limit and additional clusters only improve **inter-query** concurrency and a single query always runs on *one* cluster, ClickHouse Cloud’s horizontal scaling is effectively unbounded. Adding more nodes increases:



* **inter-query scaling:** more queries can run at the same time, and
* **intra-query scaling:** a *single* query can use CPU cores and RAM across **all** nodes in the service (via [distributed execution](https://clickhouse.com/blog/clickhouse-parallel-replicas)).

This means horizontal scaling in ClickHouse accelerates both throughput *and* individual query performance. Scaling the number of nodes is currently manual, but **automatic horizontal scaling** is in active development.

*(ClickHouse Cloud also supports [Warehouses](https://clickhouse.com/blog/introducing-warehouses-compute-compute-separation-in-clickhouse-cloud), a form of **compute-compute separation**, that lets you isolate compute for different workloads while still sharing the same data.)*

### Compute pricing

*(Official pricing, November 2025 → [https://clickhouse.com/pricing](https://clickhouse.com/pricing))*

Pricing depends on the **tier** (Basic, Scale, Enterprise) and **cloud/region**, with typical AWS US-East pricing around:



* **Basic:** ~$0.22 per compute unit/hour
* **Scale:** ~$0.30 per compute unit/hour
* **Enterprise:** ~$0.39 per compute unit/hour


### Metering granularity

*(Metering behavior, November 2025 → *ClickHouse Cloud* docs: [How is compute metered?](https://clickhouse.com/docs/cloud/manage/billing/overview#how-is-compute-metered))*

ClickHouse Cloud meters compute per minute in normalized compute units.

Services can be configured with an idle timeout, causing the compute layer to stop automatically after a period of inactivity. When a new query arrives, the service automatically resumes (“auto-start”) and begins consuming compute units again.

Billing continues while the service is active, even if no queries are running.

Services may take [20-30 seconds](https://clickhouse.com/docs/manage/scaling#automatic-idling) to resume after idling.


### How Bench2Cost computes ClickHouse Cloud costs

<details>
  <summary>Click to see the pricing logic</summary>
<p>
<br/>
As with Snowflake and Databricks, ClickHouse Cloud goes through the same Bench2Cost pipeline. For compute we start from an existing ClickBench result file for a fixed service size, for example a <strong>3-node, 64 GiB</strong> service captured in <a href="https://github.com/ClickHouse/examples/blob/main/blog-examples/Bench2Cost/clickhouse-cloud/results/aws.3.64.json">aws.3.64.json</a>. Separately, <a href="https://github.com/ClickHouse/examples/tree/main/blog-examples/Bench2Cost/clickhouse-cloud/pricings">we encode ClickHouse Cloud list prices</a> per <strong>compute unit / hour</strong> and per <strong>TB-month of storage</strong> for each tier (Basic, Scale, Enterprise).
</p>
<p>
<br/>
The Bench2Cost script (<a href="enrich.sh">enrich.sh</a>) then:
</p>
<ul>

<li>reads the service configuration (3 nodes × 2 compute units per node) and derives the total <strong>compute units / hour</strong> for the benchmarked service,</li>

<li>multiplies each query’s runtime by that burn-rate and the tier’s <strong>$/unit/hour</strong> to get a per-query <strong>compute cost</strong>,</li>

<li>adds a <strong>monthly storage cost</strong> based on the dataset size and the <strong>$/TB-month</strong> price,</li>

<li>writes out an enriched JSON file (<a href="https://github.com/ClickHouse/examples/blob/main/blog-examples/Bench2Cost/clickhouse-cloud/results/aws.3.64.json">aws.3.64_enriched.json</a>) that includes, for each tier:</li>
<ul>

<li>per-query runtimes,</li>

<li>per-query compute costs,</li>

<li>total monthly storage cost.</li>
</ul></li>
</ul>
<p>
That enriched file is what we use later in the [companion post](https://clickhouse.com/blog/cloud-data-warehouses-cost-performance-comparison) when we compare ClickHouse Cloud’s cost-per-benchmark against the other systems.
</p>
</details>


BigQuery takes a completely different approach. No clusters to size at all.


## BigQuery

<div style="border-radius:12px; padding:24px 28px; margin:28px 0; background:#111317; border:1px solid #1f242a; box-shadow:0 8px 18px rgba(0,0,0,0.45); color:#f4f4f5;">
  <div style="font-size:20px; font-weight:600; margin:0 0 4px;">BigQuery compute pricing TL;DR</div>
  <div style="font-size:15px; color:#9ca3af; margin:0;">You pay either per data scanned (on-demand) or by the active slot-time used by your queries (capacity).</div>
  <div style="font-size:13px; color:#6b7280; margin-top:4px;">(Prices as of November 2025)</div>
  <div style="height:1px; background:#1d2126; margin:16px 0 20px;"></div>
  <div style="display:flex; gap:40px; flex-wrap:wrap;">
    <div style="flex:1; min-width:260px;">
      <div style="font-weight:600; margin-bottom:6px;">Billing units</div>
      <ul style="margin:0; padding-left:20px;">
        <li>On-demand: <strong style="color:#fdff88;">Bytes scanned</strong></li>
        <li>Capacity: <strong style="color:#fdff88;">Slot-hours</strong> (active slot time, slots = logical units of compute)</li>
      </ul>
      <div style="font-weight:600; margin-top:18px; margin-bottom:6px;">Examples</div>
      <ul style="margin:0; padding-left:20px;">
        <li>Query scanning 2 TiB → <strong style="color:#fdff88;">2 TiB billed</strong></li>
        <li>Project using 500 slots for 1 hour → <strong style="color:#fdff88;">500 slot-hours billed</strong></li>
      </ul>
    </div>
    <div style="flex:1; min-width:260px;">
      <div style="font-weight:600; margin-bottom:6px;">Price per unit (GCP, US East)</div>
      <ul style="margin:0; padding-left:20px;">
        <li>On-demand: <strong style="color:#fdff88;">$6.25 / TiB scanned</strong></li>
        <li>Capacity (Standard): <strong style="color:#fdff88;">$0.04 / slot / hour</strong></li>
        <li>Capacity (Enterprise): <strong style="color:#fdff88;">$0.06 / slot / hour</strong></li>
        <li>Capacity (Enterprise Plus): <strong style="color:#fdff88;">$0.10 / slot / hour</strong></li>
      </ul>
    </div>
  </div>
</div>

### Compute model: slots on serverless shared compute

The three systems we covered so far — **Snowflake, Databricks, and ClickHouse Cloud** — all follow the **Provisioned Clusters** model: you reserve a fixed amount of compute resources, and you pay for the time that provisioned compute is running.

**BigQuery is completely different.**

BigQuery uses a **Serverless Shared Compute** model: there are **no warehouses or clusters to size**, and queries run on a large **shared, pre-provisioned compute fabric**. You only pay for **what each query actually consumes**, not for the size or uptime of a cluster.

What follows is a concise breakdown of how BigQuery’s compute model works, how it scales, and how billing is derived from that model.

BigQuery executes each query using its engine, running on a shared pool of pre-provisioned compute (engine paper: [Dremel: Interactive Analysis of Web-Scale Datasets](https://storage.googleapis.com/gweb-research2023-media/pubtools/3293.pdf)). For each query, the engine:

**① Allocates [slots](https://docs.cloud.google.com/bigquery/docs/slots)** — logical units of compute that roughly correspond to concurrent execution threads.

**② Schedules those slots** across many machines in the shared serverless fabric.

The number of slots used is **dynamic** and depends on the query plan:



* **Scan & filter** stages can be highly parallel (many slots) if there are lots of partitions or column chunks to read.
* **Aggregation** stages often use fewer slots, shaped by grouping cardinality and data distribution.
* **Final merge** stages usually need only a handful of slots to combine partial results.

In other words, BigQuery tries to give each stage **as much parallelism as it can actually use**, and that slot allocation can change from stage to stage.

Users are billed by the amount of **active slot-time** a query consumes.

The diagram below shows how BigQuery allocates slots to each stage and schedules them across its serverless compute fabric:

![Blog-Costs.004.png](https://clickhouse.com/uploads/Blog_Costs_004_3afcac3bb3.png)

#### Example

To make this concrete, imagine a query with a **wall-clock runtime of 20 seconds**, consisting of three sequential stages:

Stage 1 — Scan



* **Duration:** 12 seconds
* **Slots used:** 1,000
* **Slot-time:** 12 seconds × 1,000 slots = **12,000 slot-seconds**

Stage 2 — Aggregation



* **Duration:** 6 seconds
* **Slots used:** 600
* **Slot-time:** 6 seconds × 600 slots = **3,600 slot-seconds**

Stage 3 — Final merge



* **Duration:** 2 seconds
* **Slots used:** 4
* **Slot-time:** 2 seconds × 4 slots = **8 slot-seconds**

Now sum up the slot-time:



* **Total slot-seconds:** 12,000 + 3,600 + 8 = **15,608 slot-seconds**
* **Wall-clock runtime:** **20 seconds**
* **Billed compute:** **15,608 slot-seconds**

So even though the user only sees a **20-second query**, BigQuery’s billing reflects the **aggregate parallel work** across all slots and stages.


### Scaling: dynamic slot allocation

BigQuery automatically scales slot usage up or down based on how much parallelism each query stage can use.

**Slot scaling limits**

You buy a [fixed reservation of slots](https://docs.cloud.google.com/bigquery/docs/reservations-intro) for your workload. BigQuery will use **exactly up to that many slots**, never more. The only time this limit changes is when *you* resize the reservation.

Alternatively, with on-demand pricing (see below), you will have access to [up to 2,000 concurrent slots](https://docs.cloud.google.com/bigquery/docs/reservations-intro), shared among all queries in a single project.


### Compute pricing

*(Official pricing, November 2025 → [https://cloud.google.com/bigquery/pricing](https://cloud.google.com/bigquery/pricing))*

Slot prices depend on **Edition** (Standard / Enterprise / Enterprise Plus) and commitment model (on-demand vs. 1- or 3-year CUDs).

For **on-demand, hourly billing** in **US-East** (South Carolina):



* **Standard Edition** → **$0.04 per slot-hour**
* **Enterprise Edition** → **$0.06 per slot-hour**
* **Enterprise Plus Edition** → **$0.10 per slot-hour**

(Commitments reduce these to ~$0.032–0.09 per slot-hour depending on term and edition)

BigQuery also offers an alternative (and actually the **default**) pricing model: **on-demand query pricing**.

Instead of paying for slot-hours, you simply pay for the **amount of data each query scans**, regardless of how many slots the engine used internally.

![Blog-Costs.005.png](https://clickhouse.com/uploads/Blog_Costs_005_f2231c9ea7.png)

For **US-East (South Carolina)**:



* **First 1 TiB/month per account is free**
* **After that: $6.25 per TiB scanned**

Billing is per-query and purely based on logical bytes scanned (after pruning, filters, clustering, etc.). Slot allocation and scale-out are fully internal and do not affect the bill under on-demand pricing.


### Metering granularity

**Capacity-based (slots):**

*(Metering behavior, November 2025 → *BigQuery* docs: [Capacity compute pricing details](https://cloud.google.com/bigquery/pricing))*

BigQuery bills slot usage **per second**, with a **1-minute minimum** each time slot capacity is consumed.

**On-demand (bytes scanned):**

*(Metering behavior, November 2025 → BigQuery docs: [On-demand compute pricing details](https://cloud.google.com/bigquery/pricing))*

For on-demand queries, there is **no time-based metering at all**.

BigQuery charges **purely per byte scanned**, with the first **1 TiB per month free**.

Because BigQuery allocates compute dynamically within a shared pool, there is no warehouse/service to idle or suspend. Idle timeout concepts do not apply.

Because compute is always available from the shared pool, there is effectively no startup delay: queries can be executed immediately at any time.


### How Bench2Cost computes BigQuery costs

<details>
  <summary>Click to see the pricing logic</summary>
<p>
<br/>
BigQuery required more work, because it supports <strong>two different billing models </strong>(capacity-based slots and on-demand bytes-scanned), and because the engine exposes both <strong>billed slot-seconds</strong> and <strong>billed bytes</strong> per query.
</p>
<p>
<br/>
To make Bench2Cost work for BigQuery, we extended the benchmark runner and added a dedicated enrichment step:
</p>
<br/>
<h4>1. Extending the ClickBench runner to capture BigQuery billing metrics</h4>

<p>
<br/>
We added a BigQuery-specific runner (<a href="https://github.com/ClickHouse/examples/blob/main/blog-examples/Bench2Cost/bigquery/clickbench/bigquery_extended/run_bq_bench.sh">run_bq_bench.sh</a>) that wraps each query execution in the BigQuery CLI and extracts three things:
</p>
<br/>
<ul>

<li><strong>Wall-clock runtime</strong></li>

<li><strong>Billed slot-seconds</strong> (jobQueryStatistics.totalSlotMs)</li>

<li><strong>Billed bytes</strong> (jobQueryStatistics.totalBytesProcessed)</li>
</ul>
<p>
This required rerunning the entire ClickBench suite to ensure every query produced the necessary metadata.
</p>
<br/>
<h4>2. Mapping BigQuery’s two pricing models</h4>
<p>
<br/>
We created a pricing descriptor file, <a href="https://github.com/ClickHouse/examples/blob/main/blog-examples/Bench2Cost/bigquery/pricings/serverless.json">serverless.json</a>, containing:
</p>
<br/>
<ul>
<li><strong>Capacity-based compute pricing<br></strong>(Standard / Enterprise / Enterprise Plus), with per-slot-second rates per region</li>

<li><strong>On-demand compute pricing</strong></li>

<li><strong>Storage pricing</strong> for both logical and physical storage<br>(active + long-term tiers)</li>
</ul>
<p>
This matches the structure we already used for the other engines.
</p>
<br/>
<h4>3. Enriching the benchmark results with costs</h4>
<p>
<br/>
A dedicated script (<a href="enrich.sh">enrich.sh</a>) takes:
</p>
<ul>

<li>The raw benchmark results (<a href="https://github.com/ClickHouse/examples/blob/main/blog-examples/Bench2Cost/bigquery/clickbench/bigquery_extended/results/result.json">result.json</a>)</li>

<li>The pricing metadata (<a href="https://github.com/ClickHouse/examples/blob/main/blog-examples/Bench2Cost/bigquery/pricings/serverless.json">serverless.json</a>)</li>
</ul>
<p>
It then computes (and outputs into <a href="https://github.com/ClickHouse/examples/blob/main/blog-examples/Bench2Cost/bigquery/results/result_enriched.json">result_enriched.json</a>):
</p>
<ul>
<li><strong>Capacity-mode costs <br></strong></li>

<li><strong>On-demand costs<br></strong></li>

<li><strong>Estimated monthly storage costs</strong>
</details>


Redshift Serverless takes a similar serverless approach, but with predictive ML-driven scaling.


## Redshift Serverless

<div style="border-radius:12px; padding:24px 28px; margin:28px 0; background:#111317; border:1px solid #1f242a; box-shadow:0 8px 18px rgba(0,0,0,0.45); color:#f4f4f5;">
  <div style="font-size:20px; font-weight:600; margin:0 0 4px;">Redshift Serverless compute pricing TL;DR</div>
  <div style="font-size:15px; color:#9ca3af; margin:0;">You configure a minimum and maximum number of RPUs; Redshift automatically adjusts within that range using ML-based predictive scaling.</div>
  <div style="font-size:13px; color:#6b7280; margin-top:4px;">(Prices as of November 2025)</div>
  <div style="height:1px; background:#1d2126; margin:16px 0 20px;"></div>
  <div style="display:flex; gap:40px; flex-wrap:wrap;">
    <div style="flex:1; min-width:260px;">
      <div style="font-weight:600; margin-bottom:6px;">Billing units</div>
      <ul style="margin:0; padding-left:20px;">
        <li><strong style="color:#fdff88;">RPU-hours</strong> (RPU = Redshift Processing Unit)</li>
      </ul>
      <div style="font-weight:600; margin-top:18px; margin-bottom:6px;">Example usage</div>
      <ul style="margin:0; padding-left:20px;">
        <li>Query using 4 RPUs for 60 s → <strong style="color:#fdff88;">240 RPU-seconds billed</strong></li>
        <li>Scaling spike to 24 RPUs → <strong style="color:#fdff88;">billed only for active RPU-seconds</strong></li>
      </ul>
    </div>
    <div style="flex:1; min-width:260px;">
      <div style="font-weight:600; margin-bottom:6px;">Price per RPU (AWS, US East)</div>
      <ul style="margin:0; padding-left:20px;">
        <li><strong style="color:#fdff88;">$0.36 / RPU / hour</strong></li>
      </ul>
    </div>
  </div>
</div>

### Compute model: serverless RPUs

Redshift Serverless, like BigQuery, uses a **Serverless Shared Compute** model: there are no clusters to size, and queries run on a large pool of pre-provisioned compute managed entirely by AWS. Instead of warehouses or fixed cluster sizes, Redshift allocates compute in **Redshift Processing Units ([RPUs](https://docs.aws.amazon.com/redshift/latest/mgmt/serverless-capacity.html))**, bundles of CPU and memory, and automatically adjusts how many RPUs are used based on workload demand (engine paper: [Amazon Redshift Re-Architected](https://assets.amazon.science/4b/37/223ac61e450898244a31bed53734/amazon-redshift-re-invented.pdf)).

A unique aspect of Redshift Serverless is its **[ML-based predictive scaling (RAIS)](https://assets.amazon.science/64/da/6f7ad2174272ae22a20f6058baca/intelligent-scaling-in-amazon-redshift.pdf)**: Redshift analyzes query structure, expected scan sizes, concurrency, and historical patterns to pre-allocate compute *before* heavy queries are run. This allows scaling to happen proactively rather than reactively.

You are billed for **RPU-time** while compute is active.

The diagram below illustrates how RPUs scale within a workgroup’s configured range:

![Blog-Costs.006.png](https://clickhouse.com/uploads/Blog_Costs_006_4f05cc9507.png)
*([Each RPU is equivalent to 16 GB memory and 2 vCPU](https://medium.com/@surojitchowdhury/exploring-aws-redshift-serverless-a-closer-look-59e531790722))*


#### Example

Suppose a query arrives and Redshift decides, based on its ML-based predictive model, to run it with **16 RPUs** (as sketched in the diagram above).

If the query’s wall-clock runtime is **60 seconds**, then the billed compute is simply:

**16 RPUs × 60 seconds = 960 RPU-seconds**


### Scaling: ML-driven predictive allocation

Redshift Serverless automatically scales the compute assigned to your workgroup within a range you configure. The range has two bounds:



* **Base capacity** — the minimum number of RPUs always available to your workgroup ([default 128 RPUs](https://docs.aws.amazon.com/redshift/latest/mgmt/serverless-capacity.html), configurable from **4 to 512 RPUs**, or up to **1024 RPUs** in select regions).
* **Maximum capacity** — the upper limit that Redshift is allowed to scale to under load.

Scaling is:



* **Automatic** (no clusters or nodes to resize)
* **Predictive** (ML models pre-allocate RPUs when heavy queries are likely)
* **Constrained** by your configured base and max limits to keep costs predictable

When load drops, Redshift scales down toward the base capacity, releasing unused RPUs. RPUs will drop to zero if you don't run queries in the Redshift serverless environment, and if this remains at zero for an extended period, a cold start will occur (see the Metering granularity section below).

> **How Redshift’s scaling differs from BigQuery’s**<br/><br/>BigQuery scales threads dynamically during execution; Redshift scales the entire compute envelope upfront: Compared with BigQuery’s slot-based model, Redshift Serverless **adjusts the entire query’s compute size (RPUs) upfront**, whereas BigQuery **redistributes many small execution threads (slots) across stages while the query runs**. <br/><br/>Once Redshift selects the RPU level, the whole query runs on that fixed amount of compute.


### Compute pricing

*(Official pricing, November 2025 → [https://aws.amazon.com/redshift/pricing/](https://aws.amazon.com/redshift/pricing/))*

For **US East (N. Virginia)**, the on-demand price is **$0.375 per RPU-hour**.


### Metering granularity

*(Metering behavior, November 2025 → AWS docs: [Amazon Redshift Serverless compute pricing details](https://aws.amazon.com/redshift/pricing/))*

Redshift Serverless bills RPU usage per second, with a 60-second minimum charge.

Redshift automatically manages compute capacity and instantly scales to zero when not in use. There is no manual idle-timeout setting, the service auto-pauses internally until new queries arrive.

Redshift Serverless typically resumes quickly when the warm pool is still active. However, after longer idle periods, AWS may de-allocate resources and a cold start can introduce tens of seconds of delay, even though this behavior is not surfaced explicitly in public documentation.


### How Bench2Cost computes Redshift Serverless costs

<details>
  <summary>Click to see the pricing logic</summary>
<p>
<br/>
Mapping Redshift Serverless to cost follows the same Bench2Cost pattern as the other engines, with one important twist:
</p>
<p>
<br/>
<strong>Redshift does not bill for wall-clock runtime. It bills for RPU-time.</strong>
</p>
<p>
<br/>
That means:
</p>
<p>
<br/>
RPU-time = (wall-clock runtime) × (RPUs actively used)<br><br>…and the raw ClickBench output only contains wall-clock runtime.
</p>
<p>
<br/>
To compute real dollar costs, we extended the ClickBench runner to also fetch <strong>billed RPU-seconds</strong> for every query using Redshift’s system tables and AWS APIs.
</p>
<p>
<br/>
That extension lives in <a href="https://github.com/ClickHouse/examples/blob/main/blog-examples/Bench2Cost/redshift-serverless/clickbench/redshift-serverless_extended/get_metrics.sh">get_metrics.sh</a>
</p>
<p>
<br/>
With that in place, the pipeline works like this:
</p>
<br/>
<ol>

<li><strong>Re-run ClickBench with the extended runner<br></strong>This produced a Redshift-specific result file containing both the usual wall-clock runtimes <strong>and</strong> the RPU-time for every execution: e.g. <a href="https://github.com/ClickHouse/examples/blob/main/blog-examples/Bench2Cost/redshift-serverless/clickbench/redshift-serverless_extended/results/serverless_100m.json">serverless_100m.json</a><br></li>

<li><strong>Load Redshift’s pricing model<br></strong>Bench2Cost uses a pricing descriptor (<a href="https://github.com/ClickHouse/examples/blob/main/blog-examples/Bench2Cost/redshift-serverless/pricings/serverless.json">serverless.json</a>) that contains RPU rates and storage pricing.<br></li>

<li><strong>Enrich results with dollar costs<br></strong>The enrich.sh script joins the benchmark results with the pricing model and emits a fully enriched JSON file containing per-query compute cost (based on RPU-time) and storage cost: e.g. <a href="https://github.com/ClickHouse/examples/blob/main/blog-examples/Bench2Cost/redshift-serverless/results/enriched_100m.json">enriched_100m.json</a> </li>
</ol>
<p>
The output has:
</p>
<br/>
<ul>

<li>wall-clock time</li>

<li>billed RPU-time</li>

<li>compute cost in USD</li>

<li>storage cost in USD</li>
</ul>
<p>
<br/>
This now aligns Redshift with the other systems for the final cost-per-query comparison.
</p>
</details>

And that’s the last system. We’ve now walked through how all five major cloud data warehouses actually meter compute. Let’s wrap up and look at what all this tells us about cloud data warehouse economics.

## What this tells us about cloud data warehouse economics

We just walked through how all five major cloud data warehouses really meter compute. And the core lesson is simple:

> Raw runtime doesn’t determine cost. Billing models do.

**Snowflake**, **Databricks**, and **ClickHouse Cloud** all use **provisioned capacity**, but ClickHouse is the outlier in the best way:

* Snowflake/Databricks: opaque billing units.

* **ClickHouse: hardware-grounded compute units (8 GiB RAM + 2 vCPU).**

* It’s also the only system with **unbounded horizontal scale** and **automatic vertical scale**, so a single query can use CPU and RAM across *all* nodes.

**BigQuery** and **Redshift Serverless** take the opposite approach: **serverless shared compute**. You don’t size anything; you simply pay for what the engine decides your query consumes.

Every system defines “what you pay for” differently, which is why price lists alone tell you nothing.

That’s why we built **Bench2Cost**, a clean, vendor-neutral way to turn benchmark runtimes into comparable cost-per-query numbers.


This post gave you the mental model.

The [companion post](https://clickhouse.com/blog/cloud-data-warehouses-cost-performance-comparison) answers the question you actually care about:

> Which system delivers the best overall cost-performance for analytical queries?

And here’s the teaser:

> For analytical workloads at scale, **ClickHouse Cloud delivers an order-of-magnitude better value than any other system**.
<br/>
![Blog-Costs-animation01_small.gif](https://clickhouse.com/uploads/Blog_Costs_animation01_small_de9ac301cc.gif)


