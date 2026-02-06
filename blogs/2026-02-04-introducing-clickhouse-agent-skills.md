---
title: "Introducing ClickHouse Agent Skills"
date: "2026-02-04T19:36:28.542Z"
author: "Al Brown and Doneyli De Jesus"
category: "Product"
excerpt: "We’re releasing ClickHouse Agent Skills: a set of open-source, packaged skills encoded with ClickHouse best practices learned by our engineers and community. "
---

# Introducing ClickHouse Agent Skills

We’re releasing the official [ClickHouse Agent Skills](https://github.com/ClickHouse/agent-skills): a set of open-source, packaged skills encoded with ClickHouse best practices learned by our engineers and community. 

These skills provide your AI assistant with 28 prioritized rules for schema design, query optimization, and data ingestion. It helps your agent go from a general-purpose LLM to a ClickHouse power user. 

[The repo is open and Apache licensed for everyone to contribute to](https://github.com/ClickHouse/agent-skills), so if you've got some hard-won lessons about how to best use ClickHouse, we'd love for you to share.

<video autoplay="1" muted="1" loop="1" controls="1">
  <source src="https://clickhouse.com/uploads/dons_agent_skills_demo_90f83c3a19.mp4" type="video/mp4" />
</video>

## Get started

You can add these skills to your local environment in seconds:

```shell
npx skills add clickhouse/agent-skills
```

The CLI will detect which agentic interfaces you have installed and drop the instructions in the right place.

Agents that support skills should start to use them automatically when appropriate, but you can also manually invoke them (for example, in Claude Code, you can use `/clickhouse-best-practices`).

## Why we built this

LLMs are a great accelerator, and we believe that they are only going to become more common in developer workflows as we build towards [agentic analytics](https://clickhouse.com/blog/agent-facing-analytics). But, they don't (yet?) always get specialised systems like ClickHouse exactly right. 

We’ve seen some developers hit walls when LLMs make functional, but less-than-perfect, choices:

* Choosing the wrong ORDER BY or data types.  
* Writing JOINs that don't scale or failing to batch inserts.  
* Missing out on Materialized Views or specialized indexes.

These choices can lead to friction later down the line when you reach production, or need to scale. We want to support developers using AI, and while our docs contain a wealth of information on how to do these things correctly, LLMs don’t always find the right information at the right time.

## What’s in the box?

We’ve built these skills using the [Agent Skills](https://agentskills.io/) specification recently released by Anthropic. It’s a lightweight, agent-agnostic format that allows us to encode deep domain knowledge into a format that LLMs can invoke when they actually need it.

The initial release focuses on the high-impact best practices that are relevant to almost all ClickHouse users:


- **Schema design**  
  - Primary Key selection  
  - Data Types  
- **Query performance**  
  - JOIN optimization  
  - Mutation avoidance  
- **Data ingestion**  
  - Insert batching  
  - Async inserts  
- **Advanced tools**  
  - Materialized Views  
  - Partitioning strategies

## What's next?

This is just the start. We’re going to keep expanding this with deeper knowledge on cluster configurations, engine-specific optimizations, complex data pipeline patterns, and more. 

Check out the [repo](https://github.com/ClickHouse/agent-skills) and [join us in Slack](http://clickhouse.com/slack) to let us know what rules we should add next.