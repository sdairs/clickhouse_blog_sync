---
title: "Building Real‑Time AI: Highlights from the AWS MCP Hackathon in San Francisco"
date: "2025-11-19T14:17:04.385Z"
author: "Zoe Steinkamp"
category: "Community"
excerpt: "How teams used ClickHouse to power agents with streaming data, sub‑second analytics, and production‑ready dashboards at the AWS MCP Hackathon."
---

# Building Real‑Time AI: Highlights from the AWS MCP Hackathon in San Francisco

## Summary

* Builders prototyped **next‑gen AI agents** that act on live data - adtech, AI ops, and digital health were standouts.

* **ClickHouse** served as the real‑time analytics backbone across stacks with **Temporal**, **AWS Bedrock**, **Confluent Kafka**, **Slack**, and **React**.

* Below: **three project spotlights**, with what they built, why it matters, and how ClickHouse made the difference.

## Why we showed up

We were proud to sponsor the **AWS MCP Hackathon** in San Francisco \- two fast‑paced days where developers and AI enthusiasts built agents that reason, automate, and act on streaming data. The event was a great showcase for how **ClickHouse** powers real‑time observability, low‑latency predictions, and analytics that feel instantaneous in a product UI.

In the remainder of this post, we’ll spotlight three projects that demonstrate what's possible when AI agents have instant access to live data, ranging from ad bidding to incident response and healthcare monitoring.

## First Place : Ad Optimizer Agent

**What they built:** A real‑time agent that predicts **ad bidding prices** from time‑series ad signals.

**How it works:** **Confluent Kafka** streams events into ClickHouse for feature computation; the agent reacts to fresh signals and updates bids.

**Why ClickHouse:** Millisecond‑class aggregations and joins on streaming data made model features instantly queryable. The team preferred ClickHouse over batch‑oriented options for **low‑latency, scalable** analytics on hot data.

**Learn more:** [https://devpost.com/software/rokko-the-ad-optimizer-agent](https://devpost.com/software/rokko-the-ad-optimizer-agent) 

## Second Place \- AI Ops Agent

**What they built:** An “**AI incident commander**” for reliability when APIs or models fail.

**Architecture at a glance:**

* **Temporal** for durable orchestration, retries, and fallbacks  
* **AWS Bedrock** calls for incident analysis and root‑cause explanations  
* **ClickHouse** for storing incident timelines, prompts/responses, and metrics for post‑mortems  
* **Slack** for publishing crisp summaries and action plans

**Team reflections from the hackathon:**

* **Inspiration:** Brainstorming with ChatGPT

* **Approach:** Ship the core loop fast; iterate in public

* **Challenge:** Presenting a partial build while conveying the full vision

* **Advice:** “**Fake it till you make it** \- how you tell the story matters”

**Learn more:** [https://devpost.com/software/incidentlogica](https://devpost.com/software/incidentlogica) 

![](https://clickhouse.com/uploads/image4_f1b628041c.jpg)

![](https://clickhouse.com/uploads/image3_7ca3b4c411.jpg)

![](https://clickhouse.com/uploads/image2_c9bef921cf.png)

![](https://clickhouse.com/uploads/image1_1fbc6fc3d6.png)


## Spotlight  - GlucoTrack Predictive Agent

**The idea:** Managing Type 1 diabetes is hard. Using the **OhioT1DM** dataset, the team simulated **glucose spikes, meals, and daily patterns** and then offered a tool that **monitors and forecasts** future glucose trends, blending preventive guidance with real‑time stats.

**Build approach:**

* A synthetic glucose spike generator with AWS Bedrock \+ Temporal

* An AI agent to analyze patterns and simulate meal impacts

* A real‑time dashboard \+ chatbot for end users

* ClickHouse as the backbone for time‑series ingestion and sub‑second queries into the React UI

**The hardest part (and the fix):**

Early trend plots across time windows lagged. Moving fully to ClickHouse (with tuned schema \+ queries) restored smooth, low‑latency dashboards; even under load.

**What’s next:**

Evaluate on anonymized real‑world data and add smarter predictive modeling with multimodal signals (activity \+ meal logs alongside glucose).

**Advice to future hackers:**

Pick a problem you care about, choose tech that lets you move fast, avoid over‑engineering, and optimize the core loop. Great teams ship great hacks.

“We could run heavy queries on streaming glucose data and still get instant dashboards, which made our project feel like a real product instead of a demo.”  *GlucoTrack team*

---

## **What we saw across teams**

* **Streaming → features → actions:** Event streams (often via **Kafka**) landed in ClickHouse, where teams computed features and fed agents that **act in real time**.

* **Orchestration matters:** **Temporal** gave reliability superpowers (retries, fallbacks, idempotency) for LLM work.

* **Production‑grade UX:** React dashboards reading from ClickHouse made **analytics feel instantaneous**, even during demos.

* **Observability by default:** Storing prompts, traces, and metrics made it easy to **explain model behavior** and iterate.

---

## **Thank you**

Huge thanks to **AWS**, organizers, and every builder who shipped, demoed, and shared learnings. We’re excited to sponsor more AI hackathons and to partner with teams who want to push what’s possible with **real‑time, data‑driven agents**.

The AWS Hackathon highlighted the potential for innovation at the intersection of streaming data, AI, and real-time analytics. ClickHouse is excited to join more AI hackathons in the future and is actively looking for partners who want to collaborate on the next generation of real-time, data-driven solutions.

ClickHouse is excited to start having more involvement in hackathons across the world, as we believe our ease of use and scalability make us an ideal hackathon technology. 