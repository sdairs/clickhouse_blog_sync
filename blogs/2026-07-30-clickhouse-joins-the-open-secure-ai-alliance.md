---
title: "ClickHouse joins the Open Secure AI Alliance"
date: "2026-07-30T19:44:40.842Z"
author: "ClickHouse"
category: "Company and culture"
excerpt: "ClickHouse is joining the Open Secure AI Alliance alongside NVIDIA and other industry leaders to help build open tools that keep AI agents secure."
---

# ClickHouse joins the Open Secure AI Alliance

## Summary

* ClickHouse is joining the Open Secure AI Alliance alongside NVIDIA and other industry leaders to help build open tools that keep AI agents secure.
* Langfuse is our open-source, MIT-licensed platform for agent tracing, evaluations, and guardrail monitoring. It works with any model and harness, runs air-gapped on your own infrastructure, and stores every trace in ClickHouse, which is also open-source under Apache 2.0.
* Agents need open audit trails. In the alliance, we're building open instrumentation for agent forensics, open evaluation pipelines for detecting anomalous agent behavior, and reference architectures for air-gapped agent observability.

![osaia-logo-garden_press-kit_3840x2160.png](https://clickhouse.com/uploads/osaia_logo_garden_press_kit_3840x2160_35e084e721.png)

This month, an AI agent escaped its sandbox and gained access to Hugging Face's production servers. Containing the intrusion meant reconstructing what the agent actually did: reviewing more than 17,000 actions with an open-weight model running on Hugging Face’s own infrastructure, after safety guardrails on hosted closed models blocked their first forensic attempts.

The incident became one of the founding lessons of the [Open Secure AI Alliance](https://blogs.nvidia.com/blog/open-secure-ai-alliance/). The alliance builds and shares open models, harnesses, tools, and techniques so defenders can inspect, adapt, and run AI security systems on their own infrastructure. ClickHouse is joining alongside NVIDIA and other industry leaders to help build open tools that keep AI agents secure.


## Agent security runs on evidence 

When an agent gets compromised, the investigation comes down to the record of what it actually did: every model call, tool invocation, retrieval, and intermediate decision. The same is true when an agent simply misbehaves. That record is the evidence layer of agent security, and it should be open, inspectable, and accessible to every team that needs it, from the engineers running the agent to security and compliance.


## Langfuse: the open audit layer for AI agents 

[Langfuse](https://langfuse.com) is our open-source, [MIT-licensed](https://github.com/langfuse/langfuse) platform for agent tracing, evaluations, and guardrail monitoring. Engineering teams use it to see, score, and prove what their LLM applications and agents do in production. More than 100,000 engineers build on Langfuse, including teams at 21 of the Fortune 50, and the platform processes over 10 billion observations a month. The open-source project has 32,000 GitHub stars and more than 300 contributors.

**Any model:** Langfuse traces agents built on open-weight models you run yourself and on closed APIs, in one audit plane. When an incident forces a model switch mid-response, the evidence layer stays put.

**Any harness:** Native instrumentation covers LangChain, LlamaIndex, the Vercel AI SDK, and the OpenAI SDK. Everything else connects through OpenTelemetry.

**Guardrails you can measure:** Evaluations run on live traffic and score every output, so teams see when a guardrail fires, drifts, or fails. Langfuse monitors guardrail pipelines built with popular libraries, including [NVIDIA NeMo Guardrails, LLM Guard, and other libraries](https://langfuse.com/docs/security-and-guardrails#1-run-time-security-measures), so teams can compare checks on real traffic and prove which ones actually catch attacks. Organizations in highly regulated industries also use Langfuse traces as their record-keeping layer to meet compliance obligations, including those under the EU AI Act.

**Your infrastructure:** Langfuse runs in an air-gapped environment on your own infrastructure. Traces never have to leave the network on which they were created.


## Open at every layer

Langfuse stores every trace in ClickHouse. Agent traces are analytical data at scale: Langfuse alone writes more than 10 billion observations a month into ClickHouse, spans, tool calls, and evaluation scores that responders need to query in seconds while an incident unfolds. That is the workload ClickHouse was built for.

ClickHouse is an open-source project under the Apache 2.0 license, with hundreds of millions of downloads over the past decade. Security teams already run some of their heaviest workloads on it. [Cisco Talos runs its threat intelligence reputation service on ClickHouse Cloud](https://clickhouse.com/blog/cisco), classifying file hashes so researchers can make fast security decisions. Cloudflare has publicly written about [running ClickHouse within its bot management platform](https://blog.cloudflare.com/cloudflare-bot-management-machine-learning-and-more/), logging every detection on a network that averages 11 million requests per second.  Both are fellow alliance members. [ClickStack](https://clickhouse.com/clickstack), our open-source observability stack, brings OpenTelemetry-native logs, metrics, and traces into a single engine.


## Contributing to the open domain

NVIDIA’s [announcement](https://blogs.nvidia.com/blog/open-secure-ai-alliance/) of the Open Secure AI Alliance names the full agent stack that security depends on: identity, permissions, harnesses, guardrails, logs, and evaluation. Our contribution focuses on :



* **Open instrumentation and trace schemas for agent forensics,** built on OpenTelemetry, so incident responders can reconstruct agent behavior across harnesses instead of per vendor.
* **Open evaluation pipelines for detecting anomalous agent behavior,** runnable with open-weight models as judges on infrastructure you control.
* **Reference architectures for air-gapped agent observability,** so regulated and sovereign environments get the same audit capability as everyone else.


## What comes next

Attackers already use frontier AI. Defenders need to see what their agents are doing, prove it afterward, and run that capability on infrastructure they control. Agent security runs on evidence, and traces are that evidence, which is why the audit layer for AI agents should be as open as the models they run on.  The time is now, and that is exactly why ClickHouse joined the alliance to help build open and trusted auditing for AI and agents.  

Self-host [Langfuse](https://langfuse.com/) and you run the whole stack yourself, from the tracing UI down to the database, and you can read the source for every layer.