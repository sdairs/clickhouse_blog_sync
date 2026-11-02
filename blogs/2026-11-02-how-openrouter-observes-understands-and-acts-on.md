---
title: "How OpenRouter observes, understands, and acts on 740 million LLM requests a day with ClickHouse Cloud"
date: "2026-11-02T13:24:32.982Z"
author: "ClickHouse"
category: "User stories"
excerpt: "OpenRouter uses ClickHouse Cloud as the single store behind customer analytics, public model rankings, internal AI agents, and routing across 500+ models, as monthly requests grew 33x to 19.7 billion."
---

# How OpenRouter observes, understands, and acts on 740 million LLM requests a day with ClickHouse Cloud

## Summary

- OpenRouter uses ClickHouse Cloud as the single store behind customer analytics, public model rankings, internal AI agents, and routing across 500+ models.
- Since OpenRouter adopted ClickHouse, monthly requests have grown 33x to 19.7 billion, with 110+ trillion tokens served per week.
- Every request feeds back into ClickHouse for continuous routing evaluation; that same data now powers a Jev Router, from TypeSafe AI, that picks models based on real-world usage.

If you ask a developer which LLM they’re using, they’ll often say “it depends.” It might be a frontier model for code review, a cheaper model for summarizing support tickets, or a similar model from a different provider.

[OpenRouter](https://openrouter.ai/) sits between developers and inference providers, handling some over 1 billion requests every day. It offers a single interface to more than 500 models across over 80 providers, routing each request to the endpoint (a combination of model and provider) that best fits the user’s preferences, whether that’s price, quality, latency, or throughput.

It also handles failover, falling back to another endpoint if one runs into trouble, and publishes model rankings that no single provider could. “Because we’re a gateway and not connected to any individual provider organization, we can provide public rankings about how models are actually being used in the real world,” says senior data engineer Joe Ciesielski.

Joe joined us at [Open House 2026 in New York](https://clickhouse.com/videos/openhouse-nyc-openrouter), where he shared how [ClickHouse Cloud](https://clickhouse.com/cloud) on AWS and GCP powers those rankings and nearly everything else OpenRouter does with its analytics data. He broke their journey into three “eras,” from observing what happens on the platform, to understanding it more deeply, to acting on it with routing decisions in near real time.

<iframe width="768" height="432" src="https://www.youtube.com/embed/IHex1XNhZdU" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

## Growing up with ClickHouse

OpenRouter adopted ClickHouse Cloud in November 2024. “We saw this forthcoming need that we would have to ingest a large amount of data in very quick succession and provide many different rollups of that same data set,” Joe says. Users, providers, and the public would each need their own view of the same data, in near real time.

From November 2024 to August 2026, monthly requests grew from around 600 million to 19.7 billion, a 33x increase. OpenRouter now serves over 110 trillion tokens a week, and the raw generation log in ClickHouse holds roughly 134 billion rows.

![](https://clickhouse.com/uploads/openrouter_nov2026_image1_5599d8c34e.jpg)

Data reaches ClickHouse from multiple directions. The gateway writes request telemetry using a mix of [synchronous batched inserts](https://clickhouse.com/docs/concepts/features/operations/insert/bulkinserts) and [asynchronous inserts](https://clickhouse.com/docs/concepts/features/operations/insert/asyncinserts). The team has also been testing the new [GCP Pub/Sub connector for ClickPipes](https://clickhouse.com/blog/clickpipes-gcp-pub-sub-preview), which Joe calls “pretty fun to work with.” An asynchronous classifier anonymously tags each prompt with a task type, so OpenRouter can see how users spread their requests across model families. ClickPipes ingests data from the Postgres transactional database, and Fivetran ingests data from third-party tools.

The data lands as raw tables, while [materialized views](https://clickhouse.com/docs/concepts/features/materialized-views) turn it into rollups for activity, endpoint health, and task types. A warehouse built with dbt and Airflow sits on top.

> “Data stored across our ClickHouse data warehouses powers observability, AI agents, Slack bots, and routing decisions. The outcomes of those routing decisions are then written back to ClickHouse, creating a continuous feedback loop.”
>
> — Joe Ciesielski, Senior Data Engineer, OpenRouter

## Observability: from generation log to customer charts

“One of the benefits of using a gateway,” Joe explains, “is that you have all of your data in one place.” A team might have a contract with OpenAI, access other models through Bedrock, and hold other arrangements elsewhere. Routing through OpenRouter centralizes all of it. “We knew this was really key for our business,” he says. “We wanted to make sure that was key early on, making that data accessible to our customers.”

Request telemetry started landing, and within a few weeks the user-facing activity charts for usage and token costs were reading from ClickHouse in November 2024. By January 2025 the team had added endpoint performance rollups and the public rankings, and in February 2025 routing began reading endpoint health from the same data.

The overarching pattern is to write once and roll up many ways. As Joe puts it, “Because of how straightforward it is to add rollups, we’re able to write that telemetry one time and use materialized views to provide lots of different aggregations.”

Today, those rollups power a range of dashboards and pages:

- Activity and logs for tracking usage, costs, and errors
- Provider dashboards showing endpoint health
- Mission Control, which helps account executives understand enterprise usage
- Rankings and model pages, with public leaderboards, latency, and uptime

A unified query builder sits on top of ClickHouse and serves all of them. To build a new chart or report, engineers make a standard API call. As long as the metrics and dimensions they need are in the builder, it translates the call into SQL. The same query builder also powers OpenRouter’s public analytics endpoint.

The [rankings page](https://openrouter.ai/rankings), which shows trending models and the kinds of tasks routed to each, is “a really important flywheel for our organization,” Joe says. “Folks can peruse our public rankings page and say, ‘Hey, I see that folks are really excited about this one model, let me go on OpenRouter and try that.’ It’s really easy to screenshot, tweet about, and provide some excitement about what we’re doing.”

[Insert screen [recording](https://youtu.be/USUZi3LCF4Q) of leaderboard]

## Understand: a warehouse built for agents

In August 2025, the team decided to see what else the data could tell them. “We knew there was a lot of latent information baked into what we had available in ClickHouse,” Joe says.

Rather than spin up a separate warehouse, they built one inside ClickHouse. It follows a standard medallion architecture in dbt, moving data from sources through staging, facts and dimensions, and marts. The warehouse has a relatively small number of dbt models, around 270 by Joe’s count, and every column in each one is documented. “That’s really important for how we’re accessing the data, which is primarily through agents,” he says.

OpenRouter runs dozens of internal agents, anyone in the company can spin up a new one for their own use case. Team members talk to their agents mainly through Slack. Each agent can read the dbt documentation and comes with a small set of skills, which are essentially markdown files covering how to access ClickHouse and the quirks of querying it. This lets staff pull answers from ClickHouse without needing a deep understanding of where the data lives or how to structure a query.

If, for example, a customer writes in to say that their requests are failing, a support engineer doesn’t have to look up the customer’s ID and dig through logs and traces by hand. They can instead pass the question to the support team’s agent, which is able to:

- Find the account, its keys, and recent activity
- Trace the failing requests end to end
- Attribute each error to the provider, the customer, or OpenRouter
- Answer in Slack with the evidence attached

Every step is a ClickHouse read via a bounded support API. “That makes it a really straightforward process for all of our staff to have access to all the information that’s within our ClickHouse database,” Joe says, “without needing to dig in manually.”

## Act: continuous evaluation and the Jev Router

“Routing is really our core business,” Joe says. The goal is to get each request to the endpoint that best meets the user’s needs. “ClickHouse sits right at the center of this process of continuous evaluation, where every request that comes in becomes a piece of data that we can then use to make sure subsequent requests are better meeting those user needs.”

Users say what’s important to them (price, speed, reliability), and ClickHouse shows which providers deliver it. The loop has four steps. OpenRouter reads the user’s preference on the request, measures how each provider performs, chooses the provider that best fits the ask, and records the outcome for the next request.

The process has become more sophisticated over time. In February 2025, OpenRouter could sort by price or speed and skip providers that were down. By May 2025, it preferred providers with a record of successful requests. In 2026, the same routing extended to images, audio, video, and embeddings, and by mid-2026 the platform was scoring every provider on reliability, speed, quality, and cost.

The newest piece is the [Jev Router](https://openrouter.ai/typesafe/jev-router) from TypeSafe AI, which became available October 2026. Normally, the user picks the model and OpenRouter picks the provider. With the Jev Router, OpenRouter picks the model, too. Joe calls it a kind of “dealer’s choice mechanism” with four steps:

1. Classify: A lightweight classifier assigns the prompt one of roughly 30 fine-grained task types. These are the same task types shown on the public rankings page.
2. Rank: OpenRouter ranks models by real usage for that task, using ClickHouse data. “If you want to do a code review, for example, we’ll look at how recent users of OpenRouter are routing to different models to do code review tasks,” Joe says.
3. Filter: The ranking is filtered by the user’s constraints (e.g. capability, cost tier), honoring account-level model and provider restrictions, guardrails, and zero data retention policies.
4. Choose: The router picks an endpoint and keeps fallbacks ready.

As with the rest of OpenRouter’s routing, the outcome is then written back into ClickHouse to inform the next decision.

## Many streams, one store, one loop

Taken together, the three eras form a single cycle. Request telemetry becomes customer charts. Rollups, marts, and agents read the same data to explain what’s happening. Routers use it to pick the next endpoint, and their outcomes flow back in as new telemetry.

> “ClickHouse sits right at the center of how we use our data to make sure we’re meeting our users’ needs in the best way possible, to build observability, to deepen our understanding about what’s happening, and to make decisions around our routing.”
>
> — Joe Ciesielski, Senior Data Engineer, OpenRouter

---

## Get started today

Interested in seeing how ClickHouse works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-2827-get-started-today-sign-up&utm_blogctaid=2827)

---