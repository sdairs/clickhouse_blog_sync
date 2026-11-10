---
title: "Langfuse launches AI Gateway"
date: "2026-11-09T16:57:37.502Z"
author: "Marc Klingen, Tobias Wochinger, Hassieb Pakzad and Leonard Wolters"
category: "Product"
excerpt: "One open source entry point for all AI usage in your company. See every model call, who made it and what it cost, natively traced in Langfuse."
---

# Langfuse launches AI Gateway

> Every AI application generates a constant stream of data: prompts, model calls, costs and evaluation results. Storing and querying that data at scale is exactly what ClickHouse was built for. That’s why Langfuse runs on ClickHouse, and why it joined ClickHouse in January. Langfuse is the open-source AI engineering platform that thousands of teams use to trace, evaluate and improve their AI applications, from prompt management to production monitoring. Today, Langfuse is launching the AI Gateway in public beta, so every model call, including those made by coding agents, lands in one place with who made it and what it cost. Here’s the Langfuse team with the details.

Today, we are launching [Langfuse AI Gateway](https://langfuse.com/docs/gateway/overview) in public beta. We're excited to introduce our next product. Thank you to everyone who shared feedback that this is what you want us to build next to establish a unified way use models, track costs, and govern access to AI.

## Why we built Langfuse AI Gateway {#why-we-built-langfuse-ai-gateway}

Over the last three years, something changed in how companies use AI. It is no longer one chatbot built by one team. It is coding agents on every engineer's laptop, AI assistants in every team, workflow tools adopted bottom-up, and dozens of custom AI apps in production.

It is becoming increasingly hard for companies to answer the questions: **who in our organization uses which models, what for, how much does it cost, is it secure, and how can we optimize and govern it?**

Managing AI usage within a company is becoming its own discipline:

- **Platform teams** are asked to make AI adoption safe, simple, and affordable at scale.
- **Finance teams** need to track AI costs across providers and teams every month.

[Langfuse AI Gateway](https://langfuse.com/docs/gateway/overview) is a central entry point to govern all AI traffic that is easy to host, adopt, and enforce. It can log all requests natively in Langfuse, so you can analyze AI usage and make decisions based on it.

## Langfuse is uniquely positioned for this {#langfuse-is-uniquely-positioned-for-this}

Langfuse is the [leading open source project](https://langfuse.com/adoption) for AI observability and evals (35k+ GitHub stars, 90B+ observations/month, 90M+ package downloads/month). 21 of the Fortune 50 and leading AI-native businesses like Ramp, Hugging Face, and Canva rely on Langfuse to understand and improve their AI agents. Open source is important here as an AI gateway needs to be scalable, reliable, and self-hosting it air-gapped can solve many security concerns in regulated industries.

Adding a gateway was widely requested by our users. To get a complete picture of your company's AI usage, you need to see every model call. Our [100+ integrations](https://langfuse.com/integrations) already cover many of the AI agents you build, but much of a company's AI usage happens in tools nobody instruments, like coding agents, internal assistants, and scripts. A gateway sits centrally, where every call passes, so nothing is missed. And unlike a standalone gateway, which can only count tokens and cost, Langfuse turns each call into a full trace you can search, evaluate, and improve. This is why adding a native gateway is a natural next step for Langfuse.

## Our gateway goes far beyond cost accounting {#our-gateway-goes-far-beyond-cost-accounting}

Most gateways tell you what AI costs. Langfuse AI Gateway goes further, because every call through it becomes a full Langfuse trace (opt-in).

**See your spend.** Cost and usage for every call land in one AI spend [dashboard](https://langfuse.com/docs/metrics/overview), by model and provider. Set spend limits per key and get [alerted](https://langfuse.com/docs/observability/features/alerts) before anyone runs into a surprise bill.

<video autoplay="1" muted="1" loop="1" controls="0">
  <source src="https://clickhouse.com/uploads/261106_gateway_analytics_cabf7141cc.mp4" type="video/mp4" />
</video>

**Know who spends it.** Every key belongs to a person or service and can carry a team or cost center, so AI spend breaks down the way your company is organized.

**Understand what it's spent on.** Each call is a complete trace, not just a cost line. You can see what an application or a team actually did with a model, and use the same [search](https://langfuse.com/docs/observability/features/full-text-search), [evaluations](https://langfuse.com/docs/evaluation/overview), and [annotation](https://langfuse.com/docs/evaluation/evaluation-methods/annotation-queues) you already use in Langfuse. Or simply ask [Halo](https://langfuse.com/docs/api-and-data-platform/features/halo): "What does this team use Claude Code for?"

<video autoplay="1" muted="1" loop="1" controls="0">
  <source src="https://clickhouse.com/uploads/251106_gateway_halo_49f341c28f.mp4" type="video/mp4" />
</video>

**Control which models are used and keep them secure.** Approve models centrally, so expensive or unvetted ones don't creep in unnoticed. You decide what gets recorded: usage and cost only, full prompts and responses, or nothing at all.

<video autoplay="1" muted="1" loop="1" controls="0">
  <source src="https://clickhouse.com/uploads/261106_gateway_modelcontrol_c3a3f2873a.mp4" type="video/mp4" />
</video>

**Incrementally adopt deeper tracing.** Enforce logging of every model call by mandating the gateway, and let teams incrementally add more detail to their AI traces in Langfuse, such as the tool call executions of complex agents, via OpenTelemetry or one of our 50+ integrations. OpenTelemetry distributed tracing merges these traces within Langfuse.

![Gateway ingestion settings with Full and Usage recording modes](https://clickhouse.com/uploads/langfuse_ai_gateway_nov2026_ingestion_modes_2fce6b0769.png)

**Use Langfuse as memory for agents.** All data in Langfuse is available via [MCP](https://langfuse.com/docs/api-and-data-platform/features/mcp-server) and [CLI](https://langfuse.com/docs/api-and-data-platform/features/cli), so you can give agents access to search all AI requests they made in the past. This is the foundation for self-improvement loops.

**Export metrics and raw logs to your data lake.** This enables any custom downstream process in finance and data teams.

## Fully open source {#fully-open-source}

- **Open source.** Like the rest of Langfuse, the core gateway is MIT-licensed. [Run it in your own infrastructure](https://langfuse.com/self-hosting/configuration/ai-gateway), or use it fully managed in Langfuse Cloud.
- **Easy to self-host.** Deploy it as a single 22MB Docker image alongside your existing Langfuse instance, with no extra dependencies. [Read the docs](https://langfuse.com/self-hosting/configuration/ai-gateway).
- **Your keys, no markup.** You keep your contracts, rates, and compliance agreements, such as zero data retention, with model/cloud providers. We don't resell tokens.

## Built for maximum performance and predictable scaling {#built-for-maximum-performance-and-predictable-scaling}

- **Built in Rust.** We built the gateway in Rust for high performance, availability, and reliability, even during usage peaks.
- **High speed.** <3ms median latency with tracing on.
- **High reliability.** 1,000+ concurrent streams on a single 2 vCPU node.
- **Predictable scaling.** Memory footprint scales in line with load.

## What's next {#whats-next}

This is only the beginning. We have a strong roadmap for AI Gateway to help govern AI usage:

- **Cost:** spend limits by team, user, or API key
- **Reliability:** fallbacks between providers
- **Safety:** guardrails and PII redaction
- **Access:** user provisioning (SCIM)
- **More providers:** Bedrock, Vertex, Google AI Studio, and custom providers
- **Model routing:** automatically pick the best model for the task

If you are interested in being a design partner on one of these, [reach out to us](https://langfuse.com/talk-to-us).

## How to get started {#how-to-get-started}

The gateway is in public beta, and you can try it out today. If you're an admin, [set up the gateway for your organization](https://langfuse.com/docs/gateway/get-started/admin-setup), then create a gateway key under **Organization settings → AI Gateway**.

Point your app or coding agent at your region's gateway host (for example, `https://gateway.cloud.langfuse.com`) and use the gateway key instead of your provider key. Open the ingestion project in Tracing to see incoming traffic.

<pre><code type='click-ui' language='python'>import os

from openai import OpenAI

# Before: client = OpenAI()
client = OpenAI(
    base_url="https://gateway.cloud.langfuse.com/openai/",
    api_key=os.environ["LANGFUSE_GATEWAY_KEY"],
)</code></pre>

For a full walkthrough of setting up Claude Code, Codex, and more, see [Send your first request](https://langfuse.com/docs/gateway/get-started/first-request).

Langfuse is part of ClickHouse since January and the Langfuse AI Gateway is one of many big launches at today. We're announcing the **largest expansion of the ClickHouse platform** since the launch of ClickHouse Cloud, introducing new capabilities across postgres, observability, security, and AI engineering. [Read more](https://clickhouse.com/blog/announcing-clickhouse-platform-largest-expansion?utm_medium=referral&utm_source=langfuse&utm_campaign=unified-platform-launch).

## FAQ

### Question 1: Is Langfuse AI Gateway open source?

Yes. The gateway is MIT-licensed and runs on Langfuse Cloud and self-hosted deployments.### Question 2: Do I need to change my code?

No. Change the base URL and use a gateway key. Requests and responses stay in the provider's native format, whether you build custom agents or use a coding agent harness on your own machine.### Question 3: Does Langfuse record my prompts?

Only if you opt in. By default, the gateway records metadata, usage, and cost, not content. Pass-through mode records nothing, and self-hosting keeps all data on your infrastructure. Turn on full logging, and every request becomes a complete Langfuse trace you can debug, evaluate, and turn into datasets, all without touching your code.### Question 4: Which providers are supported?

OpenAI and Anthropic in the beta. OpenRouter, AWS, GCP, Azure, and custom inference APIs follow very soon.### Question 5: What does it cost?

You can self-host the gateway for free. Langfuse Cloud currently charges only if you decide to log requests; non-logged requests are free.

---

## Get started today

Interested in seeing how ClickHouse works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-2981-get-started-today-sign-up&utm_blogctaid=2981)

---