---
title: "How Artemis Security runs 69x faster detection queries with ClickHouse Cloud"
date: "2026-07-01T13:47:42.556Z"
author: "ClickHouse"
category: "User stories"
excerpt: "Artemis Security cut detection query times 69x and investigative lookups up to 60x using ClickHouse query coalescing, materialized extraction, and AI-powered debugging with Claude."
---

# How Artemis Security runs 69x faster detection queries with ClickHouse Cloud

## Summary

* Artemis is an AI-native threat detection platform that uses ClickHouse to run real-time security analytics across terabytes of daily log data from enterprise customers.  
* Coalescing hundreds of individual detection rule queries into single scans reduced query overhead by 69x; batches of over 100 rules execute in under a second.  
* Extracting frequently-queried sub-columns from JSON into a parallel materialized table delivered 30-60x faster investigative queries and up to 400x lower CPU consumption.

Today's cyber threat landscape has fundamentally changed. Attackers are using AI to move faster, probe deeper, and evade the signature-based detection rules that traditional SIEMs were built around, making it harder and harder for legacy tools to keep up.

[Artemis](https://artemissecurity.com/) is an AI-native threat detection platform built for this new reality. As co-founder and CTO Dan Shiebler explains, "We work with companies to take all of the logs and telemetry from different sources—cloud sources, identity sources, network sources, endpoints—and do real-time analytics to identify potential cyber attacks and other strange behavior." Rather than relying on static rules, detection is handled by AI agents that continuously query incoming data, investigate potential threats, and surface cases to security teams.

The New York-based startup, which [came out of stealth in April 2026](https://fortune.com/2026/04/15/exclusive-artemis-raises-70m-to-help-fight-ai-powered-attacks-with-ai/) with $70 million in funding, is already trusted by security teams at companies like Wix, Mercury, Lemonade, and Upwork. "As a result, we're ingesting and processing an enormous amount of data," Dan says. "The hardest problems we face are problems at the data plane."

Every day, Artemis ingests many terabytes of compressed log data (tens of billions of rows) and runs around millions queries against trillions of rows. Detection rules run continuously against the freshest incoming data, scanning for individual behavior patterns across every customer environment. "You might see something malicious and say, 'Is there any indication of something similar anywhere else in my estate?'" Dan says. "You need to be able to surface that kind of needle in a haystack very quickly."

Because understanding whether a behavior is anomalous depends on knowing if it has happened before, the system also needs to aggregate months of historical data in real time. Has the user logged in from this IP address before? Is this sequence of events normal for this organization? Making things harder still, logs arrive from dozens of different systems and telemetry sources. As Dan notes, this has been a "consistent point of difficulty when trying to build a system that can perform aggregations over evolving semi-structured schemas."

Dan and Artemis' software engineer Sergey spoke at an [April 2026 ClickHouse meetup in NYC](https://clickhouse.com/videos/meetupny-march01), where they shared how Artemis uses ClickHouse Cloud on AWS to keep organizations secure, including three engineering solutions that have made the platform even faster and more efficient.

<iframe width="768" height="432" src="https://www.youtube.com/embed/JzHtHUSXf58" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

## Solution #1: Query coalescing for 69x faster detection

Artemis runs hundreds of detection rules per customer, each one a SQL query that scans a rolling window of fresh log data looking for a specific pattern (e.g. a deleted IAM policy, a newly created access key, a suspicious login sequence). In a naive implementation, 150 rules per customer translates to thousands of queries per cycle, each scanning the same data range independently. As Dan and Sergey put it, the overhead is multiplicative.

The fix came when Dan asked the team, "If all these rules are querying the same time window of the same data, why not run them as one query?" The technique they built, which they call query coalescing, uses ClickHouse's native functions to combine all individual rule predicates into a single query that sweeps the data once and tags each matching row with the rule ID that triggered it. "We just run one query instead of 500," Sergey says.

With ClickHouse's internal caching, Sergey assumed any gains would be modest. But when he ran a quick POC, he says, "It turned out crazy." A single coalesced query completed in 2.5 seconds versus 173—69x faster, using 46x less CPU and 100x less memory I/O. In production, batches of over 100 detection rules now execute in less than a second. A customer with 150 CloudTrail rules runs just two coalesced batches instead of 150 standalone queries.

That said, Sergey notes that "stuff is not always as easy as it seems when you run a quick experiment." For one, not all queries can be coalesced. CTEs, JOINs, GROUP BY, LIMIT, subqueries, and lambdas all break inside ARRAY JOIN. So the team built a lightweight runtime classifier that automatically excludes around 15% of rules with no manual opt-in required.

They also ran into ClickHouse's 256 KB max_query_size limit. The fix was to bump the limit to 1 MB and add size-aware batching with a binary-split fallback. If a batch fails, the system splits it in half to isolate the problematic rule, so one bad query never poisons an entire batch.

Sergey acknowledges that the system requires ongoing maintenance. The security research team regularly writes queries that push the classifier's heuristics, and keeping the coalescing percentage high means regularly tuning it for new edge cases. "It's an investment in platform stability, not set-and-forget," he says. "Overall, we find it quite worth it. Oftentimes, it's not through working with our great ClickHouse solution architects, reading documentation, or doing schema optimizations that get you the biggest results. Sometimes it pays to take a step back and look at your application usage."

## Solution #2: AI-powered ClickHouse debugging with Claude

Diagnosing performance issues in a high-throughput ClickHouse deployment isn't exactly straightforward. For Artemis, understanding what went wrong means correlating signals across ClickHouse system tables, CloudWatch metrics, Datadog dashboards, the application database, and source code. Doing that manually takes time, requires deep familiarity with the infrastructure, and is error-prone even for experienced engineers.

Artemis's solution is a Claude Code skill they call "/poke" (named in part for one of the office's favorite food options), a single debugging command that ties all of those systems together in one interface. A natural language prompt is enough to kick off an autonomous investigation. Sergey says he runs it around 20 times a day and calls it the team's "Swiss Army knife command" for infrastructure debugging.

The /poke skill is built on a relatively simple markdown file containing example ClickHouse system table queries, references to internal architecture documentation, and pointers to relevant source code. That context is enough for Claude to autonomously generate queries, pull data from multiple systems, write Python and bash scripts on the fly to massage the results, and surface actionable recommendations. "It performs crazy well," Sergey says.

When Artemis's dedicated "burst" ClickHouse instance (used to isolate expensive agentic investigation queries from the main ingestion pipeline) started degrading, Sergey had a choice between debugging it the "old-school" way or using /poke. Opting for the latter, in 90 seconds, a five-word prompt (/poke "burst instance performance degraded") triggered Claude to query [system.processes](https://clickhouse.com/docs/operations/system-tables/processes) for long-running queries, find investigation queries consuming 8+ GiB of memory and reading 42 TiB with no time bound, cross-reference the app database to identify which case investigation triggered it, and suggest steps for remediation (killing the queries, adding time-bound guardrails, and setting per-user memory limits).

"With our /poke command, anyone on our team without any engineering experience can do a better job than I was doing manually, and much faster," Sergey says. "LLMs, especially the latest iterations, are surprisingly good at working with ClickHouse."

## Solution #3: Materialized extraction for 30-60x faster investigative queries

The third optimization is, as Sergey puts it, less about AI specifically and more what you'd expect from a database-related talk. "We did something with our database, and now all of our queries are much faster—that kind of story," he jokes.

The problem was performance on investigative queries. These are the needle-in-a-haystack lookups that Artemis's investigative agents and security analysts depend on (e.g. finding every event involving a specific IP address, tracing a user's activity over the past 30 days, surfacing anomalies within a narrow time window). Speed on these queries can be the difference between catching an attack in progress and reconstructing it after the fact.

The root cause was Artemis's use of ClickHouse's JSON columns to handle the diversity of incoming log formats. With dozens of source types all landing in a single multi-tenant [SharedMergeTree table](https://clickhouse.com/docs/cloud/reference/shared-merge-tree), JSON columns are "on the surface, an ideal match for our use case," Sergey says, flexible enough to accommodate constantly evolving schemas without requiring upfront normalization. But every query against a JSON column parses it at read time, and there's no efficient way to index deeply nested fields, leading to performance issues.

Working iteratively with ClickHouse's solution architects, Sergey and the team arrived at [materialized views](https://clickhouse.com/docs/materialized-views) as the solution. Rather than modifying the main table (DDL operations on a live production table being, as Sergey notes, "sometimes not ideal, sometimes risky") they extracted the most frequently-queried sub-columns into a parallel table with native ClickHouse types, populated automatically on every INSERT.

They also developed a "hybrid two-step" query pattern: filter first on the extracted table to find a narrow time range, then query the full JSON table only for that slice. This gives them fast lookups without sacrificing access to the complete schema.

With this approach, filtering on status and event code dropped from around 12 seconds in the main table to 0.2 seconds in the extracted table, a 60x speed improvement. Grouping by source IP fell from 45 seconds to 1.5 seconds, and CPU consumption per query dropped by 60x to 400x depending on the workload, what Sergey calls a "massive reduction."

## Building the future of AI-powered cybersecurity

Artemis's user base is expanding fast, its data volumes are growing every week, and the threat landscape it's defending against is getting more sophisticated just as quickly.

The three optimizations Dan and Sergey shared are part of an infrastructure layer built to scale without a proportional increase in cost or complexity. Detection queries run 69x faster, investigative lookups that once took 45 seconds complete in less than two, and any engineer on the team, regardless of their ClickHouse experience, can diagnose and resolve infrastructure problems in a matter of minutes.

"We're growing extremely quickly," Dan says. With ClickHouse Cloud, they have a data foundation that gets faster and more efficient as the data grows, so Artemis can stay a step ahead of the AI-powered attackers it's built to stop.

---

## Get started today

Interested in seeing how ClickHouse works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-1151-get-started-today-sign-up&utm_blogctaid=1151)

---