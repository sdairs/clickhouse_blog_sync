---
title: "Drinking the OTel SODA: Send Observability Data Anywhere"
date: "2025-11-12T16:22:17.795Z"
author: "Severin Neumann"
category: "Community"
excerpt: "With community-standard instrumentation and the OTel Collector acting as a translation and routing engine, your metrics, logs, and traces are no longer trapped in a walled garden."
---

# Drinking the OTel SODA: Send Observability Data Anywhere

> This is a guest post by Severin Neumann, a member of the OpenTelemetry Governance Committee, and Head of Community at [causely.ai](https://www.causely.ai/)

For a long time, **observability has meant buying into a full stack you can’t really change**: proprietary agents to collect the data, a proprietary protocol to move it, and a proprietary backend to look at it. **Your telemetry lived inside a walled garden.** 

[**OpenTelemetry**](https://opentelemetry.io/) **(OTel) is breaking that pattern**. With community-standard instrumentation and the [OTel Collector](https://www.causely.ai/blog/using-opentelemetry-and-the-otel-collector-for-logs-metrics-and-traces) acting as a translation and routing engine, your **metrics, logs, and traces are no longer trapped in that garden**. 

## Observability isn’t a monolith 

There’s nothing inherently wrong with proprietary software; plenty of great systems are closed source. **The problem is when your data becomes proprietary** within these systems.

When collection, transport, and storage are tightly coupled to one vendor, your options shrink. Want support for a less common programming language? You might wait quarters for an agent. Want to change vendors? Prepare for weeks of reinstrumentation. Even simple ideas, like experimenting with a second backend in parallel, can become “projects.” 

**OTel changes the economics**. Today, you can instrument almost everything consistently, and, yes, it has **never been easier to swap your observability platform** without touching application code. But, it’s not just about reducing vendor lock-in; **when you own how your data moves, you can send it anywhere**. 

[I promised not to rant about this again](https://www.causely.ai/blog/reflections-on-apmdigests-observability-series-and-where-we-go-next), but I need to come back to the “observability” debate once again: the way “observability” is used as a marketing term makes it seem like collecting, processing, and storing telemetry is one big monolith. It isn’t. Your pipeline is inherently composable, and the most leverage shows up at the tail: the “backend.” Treat that tail as a junction, not a culdesac. 

## What does SODA mean? 

That’s the idea behind **SODA: Send Observability Data Anywhere**. 

SODA is simple on the surface: send a sensible combination or subset of your signals to the best tool for the job at hand. Under the hood, it means **being deliberate about what you send and where you send it**, keeping a durable copy you control, and refusing to recreate a new walled garden in the name of convenience. The OTel Collector makes this practical: you can enrich events, redact sensitive fields, apply sampling and routing policies, and fan out to multiple consumers, without touching application code. 

We should understand that **observability data is data, and often has value outside of just observability.**

## What does SODA look like in practice?

By owning the transport of your data, **your architecture becomes pluggable, and can adapt to how your needs change over time**.

In the immediate-term, it means you can **look at the most pressing concern most teams face: cost**. You may not be able to move observability vendors overnight, but by instrumenting your app with OTel, you solve one of the biggest hurdles to getting started: testing a new observability stack is one configuration change away, and you can run multiple tools in parallel for comparison or during a migration.

For long-term retention, **OTel makes it easy to store your complete historical data as a [durable copy in inexpensive object storage in open formats](https://clickhouse.com/blog/lakehouses-path-to-low-cost-scalable-no-lockin-observability)**. Doing so frees you from keeping all of your history in an expensive vendor bucket, and gives you replay: you can hydrate any alternative tool later without asking teams to reinstrument. 

From there, you can **send slices of telemetry to systems that act**. Use signals inside the cluster to make decisions, like autoscaling with [KEDA](https://keda.sh/) or the [Horizontal Pod Autoscaler](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/) (HPA), gating progressive delivery so a canary only promotes when golden metrics and dependency health agree, or flipping feature flags when error budgets trend in the wrong direction. Security teams can mirror selected logs and traces to their SIEM, while the raw truth stays immutable in cold storage.

As AI enters the observability space, **you are free to adopt new platforms that innovate in specific areas that matter to you**, without being restricted to the capabilities of your core observability platform. You can use [Causely](https://www.causely.ai/) to apply model-driven causal inference over your topology and recent changes to pinpoint likely causes for reliability issues and recommend or auto-apply safe actions. Or [OllyGarden](https://ollygarden.com/) to help improve the quality of your OTel implementation.

Your **telemetry is also product and business data in disguise**, and can enable customer-facing teams to see product usage, user journeys, or [customer impact as a result of an incident](https://www.causely.ai/blog/causely-feature-demo-clickstack). Observability data is often silo’d and unavailable to internal analytics, but OTel allows you to bridge that gap whether you have separated data platforms, or a unified data stack. Platforms like [ClickStack](https://clickhouse.com/use-cases/observability) build on-top of flexible, open datastores like ClickHouse, and demonstrate how observability and business data can be co-located and correlated within one platform.

When the pipeline is open, you can experiment with, and adopt, new tools without rearchitecting your stack. 

## Composed, not siloed 

OpenTelemetry already breaks silos at the source by giving us a shared schema and transport for metrics, logs, and traces. SODA applies the same principle at the tail. Keep signals together as shared context on a durable stream and let specialized tools subscribe to that context, hand off seamlessly, and act without duplicating or fragmenting the truth. In a composed flow, a root cause identified in one place becomes the pivot to quantify impact and drive recovery in another—without losing the thread.  

## With freedom comes responsibility

I’d like to stress an important note of caution: **“send anywhere” is not the same as “send everything everywhere.”** 

[Splitting your metrics, logs, and traces across disjointed backends that cannot be correlated is a fast path to longer MTTR and fingerpointing](https://clickhouse.com/blog/breaking-free-from-rising-observability-costs-with-open-cost-efficient-architectures). If you want a thoughtful breakdown of why unified access matters for investigations, [this article is a good primer](https://medium.com/womenintechnology/storing-all-of-your-observability-signals-in-one-place-matters-36178cd0ce10). 

The SODA posture helps to keep a coherent, durable source of truth under your control, then route purposeful subsets to the systems that extract additional value. 

## Drink some SODA and let us know what you think 

If you’ve read this far, you probably already have a mental list of places you wish your telemetry could go but currently doesn’t. That list is your SODA plan. 

Maybe you start by dual-writing to object storage and turning on replay. Maybe you add a lightweight autoscaling signal for a spiky service. Maybe you route instrumentation health to a specialized tool while keeping unified access for investigations. The point isn’t to chase a shiny mesh of destinations; it’s to get more leverage from the data you already collect: safely, cheaply, and under your control.   
   
[We’d love to hear how you’re doing SODA today](https://clickhouse.com/slack). Where are you sending telemetry beyond the one vendor you pay for? Which use cases are you covering: cost reduction, faster incident response, safer rollouts, richer product insights? Which ones do you want to see covered outside the “standard observability pipeline”?  