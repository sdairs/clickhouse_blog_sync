---
title: "ClickHouse Agents is now available for Managed Postgres"
date: "2026-07-03T08:58:08.210Z"
author: "Amog Iska"
category: "Product"
excerpt: "ClickHouse Agents now connects directly to Managed Postgres, so you can query your operational data in plain English, combine it with ClickHouse in a single request, and get agent-guided help monitoring, tuning, and migrating your databases."
---

# ClickHouse Agents is now available for Managed Postgres

![image1.png](https://clickhouse.com/uploads/image1_a3e34189e4.png)


## TL;DR:

[ClickHouse Agents](https://clickhouse.com/blog/clickhouse-agents-beta) is now available for **Managed Postgres** by ClickHouse. You can explore your Postgres data in plain English, query Postgres and ClickHouse together, and build agents that monitor, tune, and even help migrate your databases. All read-only by default and secure by design.

ClickHouse Agents, [launched in beta during OpenHouse](https://clickhouse.com/blog/clickhouse-agents-beta) in June 2026, is a fully managed agentic service in ClickHouse Cloud, powered by Claude. You can build agents with no code, grounded in your live data, and ask questions in plain English instead of writing SQL or wiring up tools. Teams use it for everything from self-serve data exploration to query performance analysis, getting from a question to an answer in seconds. 

Under the hood it pairs an agent builder and chat interface with a sandboxed code interpreter. It's built on an open stack: connect to any MCP-compatible system and bring your own agents, models, and tools, with ClickHouse Cloud as the data foundation and no vendor lock-in. It's built on [LibreChat](https://clickhouse.com/blog/clickhouse-acquires-librechat), the open-source AI chat platform that joined ClickHouse through a strategic acquisition and is trusted at scale by companies like [Coinbase](https://x.com/brian_armstrong/status/2070670644577280109) and Shopify.

With this release, that same agentic experience extends to all Managed Postgres services in ClickHouse Cloud. Now devs can query Postgres and ClickHouse together through an agentic interface, aligning with our vision of offering a unified data stack for OLTP and OLAP.

## **Demo**




<video autoplay="1" muted="1" loop="1" controls="0">
  <source src="https://clickhouse.com/uploads/ai_agent_video_C_1280p_crf30_e9c80d2edd.mp4" type="video/mp4" />
</video>

The demo shows how ClickHouse Agents directly link to a Managed Postgres instance. By leveraging the `run_postgres_select_query` tool, the agent parses the schema to identify available databases and tables. To evaluate service health, we utilize `get_postgres_metrics` and `list_postgres_slow_query_patterns`, surfacing real-time performance data and identifying bottlenecks automatically.

## **Use cases**

### **Query Postgres in plain English**

Point an agent at a Managed Postgres service and explore your operational data in plain English. Ask *"how many active subscriptions do we have by plan, and which churned in the last 30 days?"* and the agent inspects the schema, runs the query, and returns the answer along with the SQL it used. Access is read-only by default, so anyone on the team can explore safely with no risk of changing data.

ClickHouse Agents already lets you build custom agents backed by data in ClickHouse Cloud, and now that includes Postgres. Give an agent the context it needs (your schema, your conventions, the questions your team asks most) and it becomes a specialist over your operational data. Postgres support allows your transactional data to now feed directly into the custom agents you build.

### **Query Postgres (OLTP) and ClickHouse (OLAP) together**

Point an agent at a Postgres service and a ClickHouse service together and it can reason across both.  It queries each engine, OLTP and OLAP,  independently and merges the answers, so you can bring live operational data into your analytics

*"Take last week's signups from Postgres, match them to their event counts in ClickHouse, and show me which plans activated fastest."*

Behind that one request, the agent runs a query against Postgres for the signups, a query against ClickHouse for each user's event counts, lines the two up by user, and ranks the plans for you.

### **Migrate from Postgres to ClickHouse for analytics**

A common pattern we observed is as Postgres grows, analytical queries get slow, and teams want to move that workload to ClickHouse. A migration agent can walk you through it, capturing the steps and recommending the right data model for ClickHouse based on how your data is actually queried.

We've packaged this into a skill that walks the agent through the full workflow: discovery, access-pattern analysis, ClickHouse schema design (engine, ORDER BY, partitioning, materialized views), Postgres-to-ClickHouse type mapping, ClickPipes / PeerDB CDC ingestion, and validation. See the full [Postgres to ClickHouse migration skill](/uploads/Postgres_to_Clickhouse_Migration_Skill_f2d94fed1c.md).


<video autoplay="1" muted="1" loop="1" controls="0">
  <source src="https://clickhouse.com/uploads/ai_agent_skill_A_1280p_crf28_cfa9107793.mp4" type="video/mp4" />
</video>

It's grounded in our data-modeling guides: Postgres to ClickHouse data modeling tips (v2) and the original tips.

### **Monitor your databases**

Build an agent over [Query Insights](https://clickhouse.com/docs/cloud/managed-postgres/monitoring/query-insights) ([launch blog](https://clickhouse.com/blog/postgres-query-insights-clickhouse-cloud)) and native service metrics to keep an eye on your databases. Ask how things have trended over the week, or which queries are heaviest right now, and get a clear summary instead of building a dashboard.

The agent works from the full picture. Native metrics, available as bucketed time series over whatever window you ask for, include:

* CPU usage and memory usage  
* Disk usage and disk I/O (IOPS)  
* Network traffic  
* Connection count  
* Cache hit ratio  
* Operation throughput (fetch, insert, update, delete)  
* Deadlocks  
* Database size  
* Committed vs rolled-back transactions

And from Query Insights, for each slow query pattern (grouped by database, user, operation, and application):

* Call count and error count  
* Total, average, max, and p50 / p95 / p99 duration  
* Rows returned  
* Shared buffer cache hits and reads  
* CPU time  
* WAL bytes

### **Find and fix slow queries**

 Ask the agent why a service is slow. Query Insights surfaces the heaviest queries. EXPLAIN reveals the plan of the worst one. Service metrics show whether the server is under pressure. For example, a sequential scan on a large table points to a missing index. Adding the index can make the query much faster

We developed a skill to help the agent run this whole loop on its own. The [Postgres performance-tuning skill](/uploads/Postgres_Performance_Tuning_c0271d3463.md)) finds the slow patterns, runs EXPLAIN, checks the metrics, and returns ranked fixes.

## **Next steps**

We're just getting started. Some of the ways we want to extend ClickHouse Agents are:

* **An official performance recommendation engine, built on proper skills.** The curated skills that guide agents today graduate into a first-class recommendations engine. And they don't only run when you ask: schedule them to run on their own at the interval so insights about slow queries, schema, and capacity arrive automatically instead of waiting for you to go looking based on optimal thresholds. If your database performance starts to degrade we want to notify you before your application takes a hit.  
* **A self-healing performance tuning agent.** The next leap is from advice to action. Pair the recommendation engine with safe, automated remediation and the agent can apply fixes on its own, tuning things like autovacuum settings and other Postgres configuration, catching and resolving issues before they ever reach you.


---

## Try Postgres managed by ClickHouse

ClickHouse + Postgres has become the unified data stack for applications that scale. With Managed Postgres now available in ClickHouse Cloud, this stack is a day-1 decision.

[Sign up](https://clickhouse.com/cloud/postgres?loc=blog-cta-1199-try-postgres-managed-by-clickhouse-sign-up&utm_blogctaid=1199)

---