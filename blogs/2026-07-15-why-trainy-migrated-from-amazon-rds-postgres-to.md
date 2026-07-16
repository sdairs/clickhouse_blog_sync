---
title: "Why Trainy migrated from Amazon RDS Postgres to ClickHouse Managed Postgres "
date: "2026-07-15T21:57:40.508Z"
author: "ClickHouse"
category: "User stories"
excerpt: "Trainy moved Pluto's metadata layer from Amazon RDS to ClickHouse Managed Postgres, cutting costs and making page loads up to 3x faster while unifying OLAP and OLTP under one vendor."
---

# Why Trainy migrated from Amazon RDS Postgres to ClickHouse Managed Postgres 

## Summary

- Trainy runs Pluto, its open-source experiment tracker, on ClickHouse Cloud for metrics analytics and Postgres managed by ClickHouse for run operations.
- Migrating from Amazon RDS to ClickHouse Managed Postgres reduced costs, made initial page loads up to 3x faster, and brought OLAP and OLTP under one roof.
- Visualization queries over runs with hundreds of thousands of steps return in 50 to 100ms. Ingestion is fast and 100% reliable, with zero dropped data points.


Before they founded [Trainy](https://www.trainy.ai/), a Y Combinator company, Roanak Baviskar and Andrew Aikawa were ML engineers on the same team. They shared a pool of more than 100 GPU machines with around 20 other engineers, allocating it "basically by having a whiteboard and calling dibs." Every engineer had their own deadlines and compute needs. As Roanak says, "it became really difficult to align what the company needed with how the compute was allocated."

Roanak and Andrew started Trainy to solve that problem. The first of two core products is Konduktor, a CLI that engineers use to schedule AI workloads across their machines. It handles things like GPU health, network health, logging, and debugging, so that ML engineers can, as Roanak puts it, "purely focus on ML engineering and not DevOps."

We caught up with Roanak and Andrew to learn about Trainy's newest product, Pluto, and how migrating from Amazon RDS to [ClickHouse Managed Postgres](https://clickhouse.com/cloud/postgres) helped them make the product faster and cheaper to run, while bringing it under one unified roof.

## Pluto: an open-source experiment tracker

An ML engineer's job has essentially two halves. One is training models and setting up the compute to do it. That's what Konduktor addresses. The other is analyzing the results, working through the runs, metrics, and comparisons that tell you what to change next.

For years, the best tool for that second half was Neptune AI. But in late 2025, Neptune was acquired by OpenAI, and the product was shut down. That left many of Trainy's customers without the experiment tracker their workflows were built around. They had tried the main alternative, Weights & Biases, but it couldn't give them the same performance at scale.

So Trainy built [Pluto](https://www.trainy.ai/pluto), an open-source experiment tracker. The open-source part is incredibly important to customers. "It essentially prevents a Neptune situation from ever happening again," Roanak says. "Even if we were to get acquired, it can't be taken away from them."

Performance matters a lot too. An ML engineer looks at dozens of training runs at once, each carrying thousands of metrics, hunting for the architectural or hyperparameter change that moves the model. "You're looking at a ton of different dashboards all day," Roanak says. "You're expecting those dashboards to load very fast, you're expecting them to update really quickly, and you're expecting to ingest a very large amount of data very quickly as well."

For teams that also run Konduktor, the two products work together as one system, and Trainy is building integrations on top of that. One customer connected Pluto to Linear through an MCP layer, letting them launch GPU jobs through Konduktor and summarize their experiments from Claude Code, without ever opening the web UI.

## Choosing ClickHouse Cloud for experiment tracking

One of Pluto's core features is surfacing summary views across many runs and many steps. That requirement alone, Andrew says, pointed them toward an OLAP database. They knew of ClickHouse's reputation from many other observability leaders from their network who already relied on it. "There must be a reason for that," Roanak says.

They started with [ClickHouse Cloud](https://clickhouse.com/cloud) on AWS. "Onboarding was really easy," Andrew says. Within a couple hours he had spun up an instance from the console, pulled the database connection strings, and wired them into their EKS deployment as an environment variable.

One of the first benefits they saw was [how easy it was to manage scaling](https://clickhouse.com/docs/manage/scaling). This was especially useful early on when traffic came in bursts and the service sat idle between them. "That was nice in terms of optimizing cost at the beginning," Andrew says. "We don't have to think about scaling our ClickHouse instances by ourselves. We just get that out of the box."

As they grew, [query insights](https://clickhouse.com/docs/cloud/get-started/query-insights) became another important feature. As Andrew explains, finding performance bottlenecks and figuring out whether they're coming from their own services or from unoptimized queries is one of the harder parts of building the app. "Having query insights on the console gets us 80-90% of the way there in figuring out what makes our query slow, and helps us iterate a lot faster than if we had to build that tooling ourselves."

From day one, ingestion has been 100% reliable, which Roanak notes is "super important" for an experiment tracker. "We've never dropped a data point since the first customer that was ever logged," he says. "ClickHouse has definitely made that possible."

For the ML engineers who use Pluto, it all comes back to performance. "Given that this is an experiment tracking app, your query speed is everything," Roanak says. Customer runs often carry hundreds of thousands of steps, and the queries behind Pluto's visualizations typically return in 50 to 100 milliseconds at the P50. That speed is "make or break for the application," Roanak says, and ClickHouse Cloud is what lets them deliver for customers.

## Migrating away from RDS Postgres

Not all of Pluto's data belongs in an OLAP store. As Andrew explains, metrics behave like observability data, where you want averages and min/max operations over time. Those live in ClickHouse. Everything else is relational and lives in Postgres, from the run's creation time to the hyperparameters that started it to any other metadata a user wants to track.

Trainy first built that Postgres layer on Amazon RDS, but it became a problem on two fronts. The first was cost. "The defaults we started with on RDS were way too expensive for the volume we were seeing," Andrew says. The other problem was speed. "We were seeing slower load times, because when users initially loaded pages, the app had to request metadata about their experiments from RDS."

They were already happy ClickHouse Cloud users, so when [ClickHouse announced a managed Postgres service](https://clickhouse.com/blog/postgres-managed-by-clickhouse), it appealed right away. "Since we were already on ClickHouse Cloud, it made it really easy to try and just work in the same account," Roanak says.

One of the big draws was storage. ClickHouse Managed Postgres runs on local NVMe rather than the network-attached storage most managed Postgres services use. Because that storage sits next to the compute instead of across a network hop, disk access is faster. "NVMe storage was a very big boon, and ended up being a very big boon for our actual consumers of our web application," Andrew says.

Since Pluto's analytics already ran on ClickHouse Cloud, moving the metadata layer there kept both databases in one account, under one vendor. That metadata isn't trivial, roughly 40 to 50 GB at the time of migration, and it's expected to grow as the platform scales.

## Up to 3x faster page loads with ClickHouse Managed Postgres

Comparing session data from before and after the move, initial page loads on Postgres managed by ClickHouse are 2 to 3 times faster than on Amazon RDS. Since those page loads depend on fetching run metadata, a faster store means a faster app for users. "Overall, it's a lot more responsive," Andrew says. "Those milliseconds genuinely matter to the customer experience, because users are refreshing a dashboard 300 times a day. It adds up a lot," Roanak adds.

![exec-1212310f-a6be-4b1b-8256-ab61edc191da.png](https://clickhouse.com/uploads/exec_1212310f_a6be_4b1b_8256_ab61edc191da_4bc9a9f3c3.png)

*A Slack message Andrew sent to the ClickHouse team after the migration.*

Trainy tracks page-load performance through telemetry and works to improve it with every release. Since moving to Postgres managed by ClickHouse, users have noticed the difference. One remarked, "This is the fastest it's ever looked."

Another user relies on a complex query to identify which runs completed and which crashed. Previously, it took 10–15 minutes to execute. Now, it returns results in just five seconds.

> Pushing performance and reducing latency is the number-one most important thing to improving our customer experience on the Pluto side. And so it was a no-brainer once we saw the results we were getting with Postgres managed by ClickHouse."
>
> — Roanak Baviskar, Co-Founder and CEO

## What's next for Trainy and ClickHouse

One of Trainy's next priorities is deepening agentic access to the data in Pluto, across both ClickHouse and Postgres. Building on the MCP integration they've already started, engineers can automate experiments and let an agent optimize a model, similar to the example Andrej Karpathy showed with his [autoresearch](https://github.com/karpathy/autoresearch) project.

Another is financial ops. A director of ML engineering wants to know what each project cost last month or last quarter. That means joining GPU-hour and system-level metrics in ClickHouse with the run operations in Postgres. Today those live in separate stores, but unifying the query would provide a single view of which researcher and project spent how many GPU hours, and, as Andrew puts it, "give insights to people on where to prioritize their GPU spend."

Both priorities map onto capabilities ClickHouse Cloud offers natively. [ClickHouse's remote MCP server](https://clickhouse.com/docs/cloud/features/ai-ml/remote-mcp) gives agents a governed, permission-scoped way into the ClickHouse data, while [ClickPipes](https://clickhouse.com/cloud/clickpipes), the platform's managed ingestion service, can replicate Postgres data into ClickHouse through CDC, so metrics and metadata can be queried together.

After starting Trainy three years ago to solve the problem of chaotic and misaligned compute allocation, Roanak and Andrew are in lockstep on how to describe ClickHouse Cloud: "reliable, easy, fast."


---

## Try Postgres managed by ClickHouse

ClickHouse + Postgres has become the unified data stack for applications that scale. With Managed Postgres now available in ClickHouse Cloud, this stack is a day-1 decision.

[Sign up](https://clickhouse.com/cloud/postgres?loc=blog-cta-1326-try-postgres-managed-by-clickhouse-sign-up&utm_blogctaid=1326)

---