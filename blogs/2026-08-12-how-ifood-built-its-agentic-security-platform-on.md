---
title: "How iFood built its agentic security platform on ClickHouse Cloud"
date: "2026-08-12T15:29:05.833Z"
author: "ClickHouse"
category: "User stories"
excerpt: "iFood rebuilt its in-house security platform on ClickHouse Cloud, getting 9-16x faster queries at 40-50% of the cost and unlocking agentic threat hunts that cut a week of analyst work down to two hours."
---

# How iFood built its agentic security platform on ClickHouse Cloud

## Summary

- iFood uses ClickHouse as the foundation of its in-house security platform, supporting detection, investigation, and long-term log retention across every business unit.
- iFood initially built its security platform on Databricks, which is still widely used for BI and data science, but the security team needed faster, more scalable log ingestion, long-term retention, and faster incident response.
- With ClickHouse Cloud, the team achieved 9–16x faster queries at 40–50% of the cost, while moving from hourly batch updates to near real-time data freshness.
- This shift unlocked agentic threat hunting: work that once took an analyst a week now runs in about 2 hours, with multiple sub-agents querying more than 30 TB of data in parallel.


[iFood](https://www.ifood.com.br/) is Latin America’s leading food delivery platform. Founded in 2011, it holds over 80% market share of Brazil’s food delivery sector, and has expanded into grocery, pharmacy, pet supplies, financial services, and other sectors.

Jesus Santos leads the company’s security incident response team, part of a cyber security organization of around 100 people that serves every business unit.

We caught up with Jesus to learn more about iFood’s ClickHouse journey. While Databricks continues to serve as the foundation for iFood's Lakehouse, the security incident response team found in ClickHouse an engine that could integrate into that architecture and meet their requirements: high-volume log ingestion, long-term retention, and, most importantly, fast access to data so they can respond to incidents quickly.

Learn why ClickHouse Cloud on AWS was the right fit, delivering the speed and cost efficiency needed at scale while unlocking agentic threat hunting workflows that weren’t possible before.

## Hitting a cost ceiling

When iFood’s cyber security team was formed, they chose not to buy a packaged SIEM but instead to build their own around Databricks, which the company already ran.

The problem, Jesus explains, is that security at iFood requires a lot of logs, long retention, and the ability to pull months of history fast when an incident is underway. As the operation grew past 130 TB, meeting those needs became costly to scale.

To manage spend, company leadership and the platform’s administrators introduced query timeouts, first limiting queries to 20 minutes, then reducing that limit to 10 minutes. For Jesus’s team, which needed to scan three to six months of logs to build new detections, those timeouts made the work nearly impossible. “As iFood grew in size and scale, we just couldn’t work within those parameters,” he says.

The budget constraints created additional limitations. “Within a defined budget cap on how much we could spend, we were limited in how many alerts we could create,” Jesus says. “So our goals were stuck because of the cost of the platform.”

What they needed was a platform that could meet their security team requirements, where cost was no longer the ceiling. “That’s where ClickHouse comes in,” he says.

## Cheaper and faster with ClickHouse Cloud

ClickHouse wasn’t new to iFood, there was experience pulling log files for ad-hoc queries through open-source ClickHouse.

For the security incident response team, [ClickHouse Cloud](https://clickhouse.com/cloud) was a natural choice. They ran a POC in both ClickHouse and Databricks, using one month of real production data. “We tried to be as fair as possible, giving both solutions the same schema and pretty much the same query,” Jesus says.

> “The performance-to-price ratio in ClickHouse is phenomenal. We’ve seen a 9-16x performance boost at half the cost of our previous solution.”
>
> — Jesus Santos, Security Incident Response Team Lead, iFood

With that settled, Jesus and the team began rebuilding their security tooling, from scheduling and alerting to deduplication, correlation, and on-call escalation. “We took all of our learnings and the problems we faced and created a tool that is better for us,” he says.

With ClickHouse Cloud, iFood expects to reduce costs by 40 to 50%, while getting faster performance. Data freshness also improved; where most of their data had been batched hourly before, it now arrives near real time, so investigations can move much faster. “The whole thing runs faster and smoother,” he says. “We’re pretty happy with what we’ve got.”

## iFood’s new ClickHouse-based architecture

In iFood’s security platform, logs come from all over: infrastructure and file systems, Kubernetes workloads, cloud management consoles. “Any place that generates our audit data, we probably need that data,” Jesus says. All of it lands in AWS S3 and is ingested into ClickHouse via [ClickPipes](https://clickhouse.com/cloud/clickpipes), ClickHouse Cloud’s native ingestion layer. The result is end-to-end freshness landing between 2 and 10 minutes, which Jesus says is fast enough and worth it for the reliability and ease of use ClickPipes provides. If they ever do need sub-minute freshness, Kafka remains an option, as it’s supported by ClickPipes along with many other data sources.

![ifood-log-ingestion-pipeline-clickhouse 1.jpg](https://clickhouse.com/uploads/ifood_log_ingestion_pipeline_clickhouse_1_5631097939.jpg)

*iFood’s log ingest pipeline architecture for their security platform*

For querying, the team works in SQL throughout (part of what drew them to ClickHouse in the first place). On the investigation side, analysts are used to notebooks on Databricks, where they could add cells as an inquiry unfolded and keep a running record of what an analyst looked at and when. To preserve that workflow, the team adopted [Querybook](https://www.querybook.org/), an open-source notebook platform, and they’re building their own investigation tooling on top, more tightly integrated with the AI workflows the company is pushing across every team.

For their UI, the team is standing up [ClickStack](https://clickhouse.com/clickstack), ClickHouse’s observability stack. Jesus wants it as the main way to surface operational KPIs: how many alerts they generate, how many logs they ingest, how many turn into investigations and then incidents. “A single pane of glass,” as he puts it, so anyone can see how the operation is running.

## Agentic threat hunting with ClickHouse and Langfuse

Since the migration, ClickHouse Cloud has become central to how iFood’s cyber security team builds with AI. As Jesus puts it, “ClickHouse is core to our whole CSIRT’s AI strategy.”

A prime example is agentic threat hunting. Over the past six months, the team has built tooling to run threat hunts automatically. An analyst creates a hypothesis (e.g. “Are we compromised on the AWS infrastructure side?”) and AI agents sweep across the logs to confirm or rule it out. Work that once took an analyst about a week now takes roughly two hours.

Jesus notes that endpoint detection and response (EDR) logs alone generate 1.6 TB per day, raw. A single hunt typically looks at a month or more of data, so upwards of 50 TB at a time. The target log retention is between 6-months to 1 year, that’s only possible with ClickHouse.

In the early stages of a hunt, the team generates 10 to 15 hypotheses and investigates several in parallel. They spin up sub-agents, five at a time, with each agent running its own queries. Because ClickHouse delivers fast, cost-efficient queries, those agents can iterate freely and produce stronger results. Early tests have been promising: what once took an analyst a full week to hunt manually can now be completed by an AI-agent workflow on ClickHouse in about two hours.

> “With our security data in ClickHouse, our agents can draw on months of historical context and, because queries are so fast, rapidly test multiple hypotheses at scale.”
>
> — Jesus Santos, Security Incident Response Team Lead, iFood

To understand what agents are doing and refine them to hunt better, the team uses [Langfuse](https://langfuse.com/), the open-source AI observability and evals platform [ClickHouse acquired in 2026](https://clickhouse.com/blog/clickhouse-acquires-langfuse-open-source-llm-observability), to see where each analysis succeeds or falls short and tune the agents accordingly. "Langfuse is important to us to understand in detail what's happening on the analysis side and how to tune the agents to do a better analysis," Jesus says. Adoption reaches well beyond security, iFood has trained more than 500 people on Langfuse for agent telemetry and analytics across the company.


---

## Get started today

Interested in seeing how ClickHouse works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-1512-get-started-today-sign-up&utm_blogctaid=1512)

---

## Faster detection, and a platform that’s spreading

For Jesus’s team, ClickHouse’s impact is obvious in KPIs like mean time to detect. “Alerts that before we couldn’t run more than one time each hour can now run on average every 10 minutes. We can do this now because alert execution takes only a few seconds,” he says. Mean time to respond is improving as well, thanks to fresher data and faster queries.

Looking ahead, the team plans to migrate CDN and API logs from OpenSearch to ClickHouse, taking retention from seven days to six months at a quarter of the cost. “When we finish migrating the API logs, we’ll be able to do analysis we couldn’t dream of before,” Jesus says, noting that incidents often trace back further than a week, and his team has run into cases where the suspicious behavior began a month or more before they were brought in. The goal is to capture every request hitting iFood applications.

As Jesus sees it, “What we’ve done here shows the potential, the savings, and the performance that ClickHouse can one day bring to the whole company.”
