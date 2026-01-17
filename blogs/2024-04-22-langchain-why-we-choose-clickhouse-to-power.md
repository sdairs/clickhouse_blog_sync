---
title: "LangChain - Why we Choose ClickHouse to Power LangSmith"
date: "2024-04-22T08:29:51.862Z"
author: "Ankush Gola, co-founder of LangChain"
category: "User stories"
excerpt: "Today, we interview Ankush Gola, co-founder of LangChain, about why they chose ClickHouse to power the observability features of their flagship product, LangSmith."
---

# LangChain - Why we Choose ClickHouse to Power LangSmith

<blockquote>
<p style="margin-bottom:5px">"We’ve had a positive experience with ClickHouse. It allowed us to scale LangSmith to production workloads and provide a service where users can log all of their data. We couldn’t have accomplished this without ClickHouse."</p><p style="font-weight: bold;">Ankush Gola, co-founder of LangChain</p>
</blockquote>

<iframe width="768" height="432" src="https://www.youtube.com/embed/cbngQUnZoog?si=ANSAg6OyasPenO-H" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

## Introduction

We increasingly see companies building Observability solutions with ClickHouse, benefiting from its ability to handle both the high insert workloads and the need for low latency analytical queries often seen in this use case. It's even more exciting to see innovative domain-specific solutions that can potentially unlock a new paradigm and level of developer productivity. LangChain has developed such a solution with LangSmith - a unified developer platform for LLM application observability and evaluation. LangSmith includes features for every step of the AI product development lifecycle and powers key user experiences with Clickhouse. 

With the [recent announcement](https://blog.langchain.dev/langsmith-ga/) that LangSmith has been made Generally Available, we had the pleasure of interviewing [Ankush Gola, co-founder of LangChain](https://www.linkedin.com/in/ankush-gola-77255866/), who explained the value of LangSmith to LLM application developers and why they choose ClickHouse as the database to power the user experience and ClickHouse Cloud as the service behind their hosted offering.

## What problems does LangSmith solve?

LangSmith focuses on two primary challenges users encounter when developing LLM applications: Observability and Evaluation.

### Observability

When working with LLM applications, there are invariably a lot of moving pieces with chained API calls and decision flows. This makes it challenging to understand what's going on under the hood, with users needing to debug infinite agent loops or cases where there is an excessive use of tokens. Seeing an obvious need here, LangSmith started as an observability tool to help developers diagnose and resolve these issues by giving clear visibility and debugging information at each step of an LLM sequence.

![observability_langchain_1d1bb59f36.gif](https://clickhouse.com/uploads/observability_langchain_1d1bb59f36_41d2ebc906.gif)

<p style="margin-bottom: 0.25em;"><em>Inspecting a trace from an LLM application run - powered by ClickHouse</em></p>
<p style="margin-bottom: 0.25em;"><em>Credit: LangChain</em></p>

### Evaluation

It became apparent that there was a wider breadth of other tasks users must perform when developing LLM applications that fall under the umbrella of evaluation. These include measuring the impact of changes to prompts and models, constructing datasets for benchmarking and fine-tuning, performing A/B testing, and online evaluations. LangSmith thus evolved from an observability tool to a wider all-in-one developer platform for every step of the LLM-powered application lifecycle.

![compare_tests_langchain.gif](https://clickhouse.com/uploads/compare_tests_langchain_34c7266fee.gif)
<p style="margin-bottom: 0.25em;"><em>Viewing test runs side by side - powered by ClickHouse</em></p>
<p style="margin-bottom: 0.25em;"><em>Credit: LangChain</em></p>

## How does LangSmith differ from existing tools?

Ankush explained that the building of LLM applications has led to a new development lifecycle that is very distinct and warrants its own dedicated toolkit. While there are many tools that address the wider Observability use case, LLM applications have their own unique challenges which require workflows specifically designed for the way users need to work with the data. LangSmith provides this focused experience by recognizing the common steps in the LLM application development cycle and providing tooling to overcome the commonly associated challenges.

![langsmith_workflow.png](https://clickhouse.com/uploads/langsmith_workflow_f1fd21a193.png)

<p style="margin-bottom: 0.25em;"><em>The workflows LangSmith supports at each stage of the LLM application lifecycle</em></p>
<p style="margin-bottom: 0.25em;"><em>Credit: LangChain</em></p>

## What were your requirements when choosing a database to power LangSmith?

When LangChain first launched LangSmith, they were 100% backed by Postgres. This represented the fastest way to bootstrap the application and get it into users' hands. They also weren't 100% certain as to how users would use the application and thus couldn't be certain of the workload - would they just use it as a means to evaluate LLM workflows and thus log sparsely, for example?

They quickly realized that people wanted to log a large percentage of their production data to perform specific actions such as tracing and creating datasets, running evaluation jobs, A/B testing, and monitoring performance. This meant needing to support high throughput ingestion as well as fast filtering for drill-downs on charts in the user interface. For instance, users can filter on monitoring charts that track key metrics over time. At this point, it became apparent to the LangChain team that Postgres was increasingly struggling to meet their requirements.

![langsmith_choosing_db.gif](https://clickhouse.com/uploads/langsmith_choosing_db_d02b640c69.gif)

<p style="margin-bottom: 0.25em;"><em>Viewing monitoring charts and grouping by LLM type - powered by ClickHouse</em></p>
<p style="margin-bottom: 0.25em;"><em>Credit: LangChain</em></p>

## What were the challenges you faced with Postgres?

Postgres was effective for initially bootstrapping the application, but as LangChain scaled up, they encountered challenges with its ability to ingest data at the volumes required for production. Additionally, it struggled to efficiently handle the analytical workloads they needed to support. They tried materializing statistics ahead of time, but this often didn't provide the best experience for users who could only slice the data according to the predefined materializations. These materialization jobs ran at intervals and also consumed a huge amount of compute at the required data size. Lock contention issues also became an issue when the number of requests to Postgres increased. 

<blockquote style="font-size:16px">"Ultimately, it was clear that we needed to add another database to complement Postgres for our use case and to unlock real-time insights for our users."<p style="font-weight:bold">Ankush Gola, co-founder of LangChain</p>
</blockquote>

## What specifically led you to ClickHouse?

<blockquote style="font-size:16px">"Our experience with Postgres identified a requirement for high-throughput ingest, coupled with a need for low-latency analytical queries originating from charts and statistics presented to the user. This naturally led us to believe we needed an OLAP/real-time analytical database."<p style="font-weight:bold">Ankush Gola, co-founder of LangChain</p>
</blockquote>

![LLM_Latency.png](https://clickhouse.com/uploads/LLM_Latency_e9c89c6305.png)

LangChain also identified the need to run the chosen database locally for development and CI/CD, as well as deploy it in self-managed architectures and as a Cloud-based solution. The first two requirements excluded many of the traditional closed-source cloud solutions and invariably led toward an open-source solution.

<blockquote style="font-size:16px">"We wanted something that was architecturally simple to deploy and didn’t make our infrastructure more complicated. We looked at Druid and Pinot, but these required dedicated services for ingestion, connected to queuing services such as Kafka, rather than simply accepting INSERT statements. We were keen to avoid this architectural complexity, especially given our self-managed requirements."<p style="font-weight:bold">Ankush Gola, co-founder of LangChain</p>
</blockquote>

Some simple tests showed that ClickHouse could meet their performance requirements while being architecturally simple and compatible with all of their deployment models. All of these requirements led LangChain to ultimately choose ClickHouse.

## How did you hear about ClickHouse?

<blockquote style="font-size:16px">"When you're in the database space, it's hard not to hear about ClickHouse!"<p style="font-weight:bold">Ankush Gola, co-founder of LangChain</p>
</blockquote>

Ankush knew ClickHouse was powering a number of high throughput workloads at companies such as Cloudflare.

## What challenges did you encounter with ClickHouse? 

Ankush emphasized that it's important for users not to think of ClickHouse like other database systems such as Postgres or even data warehouse solutions like BigQuery. While an extremely powerful and flexible tool, users should pay attention to their sorting keys and engine.

The important configuration setup for LangChain was ensuring they understood and leveraged their sorting keys correctly, such that ClickHouse was optimized for all the ways they expected to query the data. Since they needed to support periodic updates this led them to use the ReplacingMergeTree engine as well.

Ankush observed that the query planning capabilities aren't as advanced as Postgres, and users need a deeper understanding of the internals and query execution to optimize queries. He recommends users familiarize themselves with the [`EXPLAIN`](https://clickhouse.com/docs/en/sql-reference/statements/explain) Api is an important tool for understanding how a query will be executed. LangChain is looking forward to the new analyzer, which will hopefully address many of the needs to optimize queries manually.

## Any tips for new ClickHouse users?

While much of the LangSmith interface consists of charts and statistics over metrics and logs, it also collects and exposes a significant amount of trace data. LangSmith users expect to be able to visualize a single trace and all of its spans. The backing datastore, therefore, also needed the ability to support querying a few rows at a time. Specifically, common workflows include filtering traces by a dimension that is in the sorting key, e.g., by user feedback score, or by specific tenant and session. On identifying the subset of traces of interest, users then drill down into problematic points using the detailed trace view.

![chat-langchain.gif](https://clickhouse.com/uploads/chat_langchain_2c6acd68fa.gif)

<p style="margin-bottom: 0.25em;"><em>Logging a trace and feedback score from ChatLangChain, viewing the results in LangSmith</em></p>
<p style="margin-bottom: 0.25em;"><em>Credit: LangChain</em></p>

<p></p>
This last step requires lookup by trace ID, which is not part of the sorting key (or at least not in the first few positions). A lookup here would normally result in a full table scan.

To avoid this, LangChain uses a materialized view where the target table has the trace ID and run ID as part of the sorting key. The rows stored in these tables have columns, which are sorting keys for the main table. This allows LangChain to use these views as almost an inverted index, where they look up the sorting key value for the main table based on a trace ID or run ID. The final query to the main table then includes a filter that can be used to minimize the number of rows scanned.

The approach LangChain have identified is best illustrated as follows:

![langsmith_mvs.png](https://clickhouse.com/uploads/langsmith_mvs_e7edb2594d.png)

This approach has allowed LangChain to deal with individual row lookups efficiently, and has been easier to set up than using secondary indices and bloom filters.

<blockquote style="font-size: 16px;">
<p>The approach LangChain has applied here is the same one used by the Open Telemetry ClickHouse integration to allow efficient trace lookups.</p>
</blockquote>

## For the LangSmith cloud offering, what were the key considerations in choosing ClickHouse Cloud over self-managed?

<blockquote style="font-size:16px">"We didn't want to manage a ClickHouse cluster ourselves. Being able to spin up a Cloud service in the GCP region of our choice was pretty effortless and a no-brainer with respect to cost."<p style="font-weight:bold">Ankush Gola, co-founder of LangChain</p>
</blockquote>

## Other than ClickHouse, what are other key components of your architecture?

LangChain still uses Postgres to manage some application state. This complements ClickHouse well since they need transactional capabilities for parts of the application.

Redis is also used throughout LangSmith as both a cache and a means of supporting asynchronous job queues.

As the team experimented with multi-modal models involving images, cloud object storage has become increasingly important as the primary storage for these.

## Is there anything you’re particularly looking forward to on the ClickHouse Cloud roadmap?

Ankush expressed an interest in the availability of inverted indices in production (currently experimental) to enable faster full-text search capabilities. Currently, LangChain is using data-skipping indices to speed up text search, but feel there is further room for improvement here.

## Looking forward, what's next for LangSmith + ClickHouse? 

When we initially interviewed Ankush, he explained there were several product areas they were working to improve, including: 

* Improving support for regression testing that allows users to submit changes, e.g. to their prompt, code, or model, and then track metrics of interest to them. This should give users an intuition as to how their application is performing in real-world scenarios based on some criteria that grade the LLM responses and are important to their organization, e.g. repetitiveness and conciseness. 
* Introducing the ability to run automatic evaluators on a sample of their production data and then inspect the responses. 
* The current means of showing traces is not conducive to understanding the chat history between an LLM and a user. While the data exists here, it's just something they acknowledge they need to improve visually. 

<p>Several weeks later, these features are already released and available! &#128640; &#129327;</p> 

All of these features required ClickHouse for analytical queries. Additionally, while not a new feature, LangChain recently improved the filtering options for users, not least the full-text search. Finally, as their enterprise customer base grows, they envisage needing to support features such as RBAC and SSO, which will invariably require tighter integration with ClickHouse.



