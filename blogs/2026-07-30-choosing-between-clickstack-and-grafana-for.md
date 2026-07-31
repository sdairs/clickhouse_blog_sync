---
title: "Choosing Between ClickStack and Grafana for ClickHouse Observability"
date: "2026-07-30T14:32:50.201Z"
author: "Alex Fedotyev and David Ryder"
category: "Engineering"
excerpt: "Using ClickHouse for observability and wondering which interface best fits your workflows? We explore ClickStack, Grafana, and when it makes sense to use both."
---

# Choosing Between ClickStack and Grafana for ClickHouse Observability

## TL;DR

Choose ClickStack when ClickHouse is your primary observability store, and you want a unified experience across logs, traces, metrics, sessions, and investigations, and are embracing a philosophy of building your own SRE agents. Choose Grafana when ClickHouse is one part of a broader, heterogeneous monitoring estate spanning multiple systems and data sources. However, many teams also use both, with Grafana for cross-data-source visualization and ClickStack providing an integrated ClickHouse observability experience, with the MCP layer powering their own SRE agents and investigation workflows.

As the ClickHouse database has become an increasingly popular choice for observability data, the conversation has shifted. For many teams, the decision about the storage engine has already been made thanks to ClickHouse’s combination of high ingestion rates, industry-leading compression, fast analytical queries, and the ability to retain raw telemetry for long periods without relying on aggressive sampling or rollups.

The next question is which interface to build on top of it. Historically, that meant just choosing a visualization layer. Increasingly, it also means choosing the platform that powers emerging agentic workflows. 

For ClickHouse users, two options have emerged as the most common: Using Grafana with the ClickHouse plugin or ClickStack, an observability platform built specifically for ClickHouse.
In this post, we’ll look at the strengths of each approach, the different philosophies behind their design, and when each is the right tool for the job.

> This blog assumes you’ve already selected ClickHouse as your observability backend. The question is no longer which storage engine to use, but which experience best fits your engineers. We compare ClickStack and Grafana (using the ClickHouse plugin) as the user and agentic interfaces for ClickHouse, not ClickStack versus the broader Grafana LGTM ecosystem, which has its own strengths and tradeoffs.

## Philosophical differences

It can be helpful to understand how the two tools start from different assumptions about how engineers work. 

> Throughout the comparisons in this blog, Grafana refers specifically to the core Grafana OSS experience when connected to ClickHouse through the ClickHouse data source plugin, including dashboards, visualizations, Explore, and alerting. It does not refer to the broader Grafana Cloud platform and the associated LGTM stack, which offer additional capabilities and have their own strengths and tradeoffs.

Grafana follows a broad “big tent” philosophy, providing a common interface across many data sources and operational systems. Its roots are in monitoring-first workflows, where an alert from Prometheus metrics directs an engineer to a dashboard, which then leads to traces, logs, profiles, or other signals to isolate the cause of an issue.

![grafana_connections.png](https://clickhouse.com/uploads/grafana_connections_1257eccee8.png)

_Grafana supports a wide range of data sources through its plugin architecture_

The monitoring-first model works well when the failure mode is already understood and represented in a dashboard or alert. It is less effective during an unfamiliar 3 a.m. incident, where an unexpected latency spike falls outside predefined views and thresholds.

ClickStack is built for these unknowns with an investigation-first philosophy. Rather than assuming the relevant question, dashboard, or signal path has already been defined, it encourages engineers to begin with the telemetry itself, search for patterns, test hypotheses, and follow the data until the root cause becomes clear. This is particularly well-suited to ClickHouse, where logs, traces, metrics, sessions, and wider application context can be queried and correlated within a single analytical engine.

![clickstack_correlation.png](https://clickhouse.com/uploads/clickstack_correlation_0a215217d3.png)

_ClickStack exposes logs, metrics, and traces as a correlated signal_



---

## Get started today

Interested in seeing how ClickStack works on your observability data? Get started with ClickHouse Cloud and Managed ClickStack in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?intent=o11y&loc=blog-cta-1459-get-started-today-sign-up&utm_blogctaid=1459)

---

## Shared data, different experiences

It is important to emphasize that the choice of interface does not determine how telemetry is delivered to ClickHouse. While OpenTelemetry is the standard path for many teams, ClickHouse can also receive data through agents and pipelines such as Fluent Bit, Fluentd, Logstash, and Vector, using OpenTelemetry formats or native ClickHouse integrations.

Once the data is in ClickHouse, both ClickStack and Grafana can work with standard OpenTelemetry schemas or custom tables. The difference lies in how each interface exposes that data to the user.

Grafana’s "big tent" philosophy allows it to support many different data sources through a common interface. This flexibility is one of its greatest strengths, but it also means more explicit configuration is often required. Correlations, dashboard variables, and query behavior must be defined within Grafana’s general-purpose abstractions, with users often needing to use SQL or the query-building capabilities available through dashboards and Explore.

Grafana does build deeper, purpose-built experiences around its own data stores, but the ClickHouse plugin is constrained by Grafana’s general-purpose data source framework and the capabilities it exposes through dashboards and Explore. 

> We [continue to invest in the ClickHouse Grafana plugin](https://clickhouse.com/blog/grafana-plugin-vision) to make the workflows available through Grafana’s data source framework smoother and reduce the amount of SQL users need to write. This includes more native filtering, exploration, variables, annotations, and query-building experiences across dashboards and Explore.

![grafana_query_builder.png](https://clickhouse.com/uploads/grafana_query_builder_3f01836bbf.png)

_The Grafana ClickHouse plugin’s new compact query mode is designed to reduce the need to write SQL._

Conversely, ClickStack is built specifically for ClickHouse and can therefore optimize the experience around its data model and analytical capabilities. It provides purpose-built experiences for logs, traces, metrics, and sessions, with correlations handled as a native part of the product. Search-first and click-driven workflows abstract much of the underlying SQL, while still allowing users to write SQL when they need more advanced analysis.

Ultimately, this makes the decision relatively low risk. The data remains in ClickHouse, the ingestion pipeline does not need to change, and adding the second interface later does not require duplicating storage.

## When to choose ClickStack

Choose ClickStack when engineers spend most of their time investigating observability data, rather than consuming predefined dashboards or following predetermined workflows from alerts into logs and traces.

This is reflected in the fact that its primary workflow is search, with additional data analysis tools such as [Event Deltas](/docs/clickstack/features/event-deltas) and [Event patterns](/docs/clickstack/features/event-patterns) complementing this. 

![clickstack_search.png](https://clickhouse.com/uploads/clickstack_search_ab89556697.png)

_ClickStack offers an investigative first experience with searching a prominent workflow_

Engineers can begin with familiar Lucene-style syntax, filter and group events, inspect value distributions, compare time ranges, move between logs and traces, and create visualizations as the investigation develops. SQL remains available for advanced analysis, but it is not required for every step.

ClickStack is also the stronger choice when ClickHouse is the primary or sole observability store. Because it is optimized for a single engine, it can combine logs, metrics, traces, and sessions into a correlated experience, while generating optimized ClickHouse queries, applying filters automatically, targeting optimized schemas, and exposing database-specific capabilities without fitting them into a generic data source abstraction.

ClickStack is designed for an [open agentic future](/blog/the-future-of-observability-not-one-proprietary-ai-agent-thousands-by-teams) with a “bring-your-own-agent” philosophy. Teams can bring observability into the coding assistants, IDEs, internal agents, chat tools, and automation frameworks they already use, rather than adopting a prescribed proprietary agent. 

To enable this, it provides an [MCP server](/docs/clickstack/mcp) that exposes higher-level observability tools for searching logs, traces, and metrics, identifying patterns, investigating regressions, and managing ClickStack resources. Agents can work through these purpose-built operations rather than constructing every investigation directly in SQL - this results in more accurate evaluations, greater tool efficiency, and higher consistency.

![clickstack_sre_stack.png](https://clickhouse.com/uploads/clickstack_sre_stack_e064da8317.png)

This open model creates a collaboration challenge: investigations may take place across different assistants, IDEs, and local tools, making their reasoning and evidence difficult to preserve and share. [ClickStack AI notebooks](/blog/observability-mcp-server-ai-notebooks) provide a common surface where the sequence of queries, hypotheses, evidence, and conclusions can be captured. The result is not only an answer, but a reusable investigation that engineers and future agents can review and extend.


<video autoplay="1" muted="1" loop="1" controls="0">
  <source src="https://clickhouse.com/uploads/ai_notebook_68c9c66d8e.mp4" type="video/mp4" />
</video>

Grafana provides its own proprietary AI assistant and an architecture that can integrate with MCP servers. When ClickHouse is the underlying observability store, it defaults to using the [Grafana MCP server](https://grafana.com/docs/grafana-cloud/machine-learning/assistant/configure/cloud-mcp/#clickhouse) to query the data directly with SQL. Teams can instead deploy ClickStack alongside Grafana as a headless agentic layer and connect its higher-level observability MCP tools.

In summary, lean towards ClickStack when you need a search-first investigative experience, native correlation across telemetry signals, session replay, or a ClickHouse-native interface that abstracts common SQL workflows. It is also the stronger fit when you want to build agentic SRE workflows around your own models, assistants, and tools rather than adopt a prescribed AI experience.

## When to choose Grafana with the ClickHouse plugin

Choose Grafana for ClickHouse when your main requirement is a consistent interface across a heterogeneous environment.

Many organizations already use Grafana as the shared dashboarding layer for infrastructure, applications, cloud services, business metrics, and operational tools. In these environments, ClickHouse is one important data source among many. The ClickHouse plugin allows teams to introduce ClickHouse without replacing the dashboards, alerting workflows, and operational practices they already use.

Grafana remains particularly strong for complex dashboard estates. Teams can build highly customized views, combine panels from different backends, manage alerting policies, and extend the platform through a broad plugin ecosystem. It is also a natural choice for Prometheus-centric organizations with established PromQL workflows.

> PromQL support in ClickHouse and ClickStack remains experimental. At the time of writing, compatibility covers roughly 65% of the PromQL test suite and continues to improve. As the implementation matures, we expect more Prometheus metric workloads requiring PromQL workloads to run directly on ClickHouse, potentially reducing the need to retain Grafana solely for these use cases.

Lean towards Grafana when you need a common dashboarding layer across several databases and vendors, depend on Prometheus-driven alerting workflows, or already operate a significant Grafana estate. It is also the stronger option when teams want to combine telemetry with operational or business data that may live outside ClickHouse.

Grafana’s architecture is deliberately multi-engine. Its strength lies in presenting data from different systems through a common framework. The tradeoff is that ClickHouse must operate within the same general-purpose abstractions as every other data source, limiting how far the experience can be optimized around ClickHouse itself. The plugin can provide query builders, dashboards, Explore, and alerting, but the surrounding experience must remain consistent with the rest of Grafana.

Neither model is universally better: Grafana's multi-engine design prioritizes flexibility across a broad technology estate, while ClickStack’s single-engine design enables tighter integration, simpler correlation, and deeper optimization around ClickHouse.

## Many teams use both

For many organizations, the best answer is to use both tools.

Grafana can remain the home for highly curated dashboards, cross-system monitoring, Prometheus workflows, and established alerting. ClickStack can provide a deeper investigative environment for full-fidelity telemetry stored in ClickHouse, while also acting as the agentic interface, with its MCP interface and notebooks, for sharing investigations.

![mixed_clickstack_grafana.png](https://clickhouse.com/uploads/mixed_clickstack_grafana_aab934917c.png)

> A common deployment model for teams to retain Grafana as their dashboarding layer while deploying ClickStack headlessly and connecting Grafana to the ClickStack MCP server. This preserves the familiar Grafana experience while using ClickStack as the agentic investigation layer.

Since both interfaces can operate over the same underlying data, teams do not need separate ingestion pipelines or duplicate storage. 

## Some practical decision rules

Choose ClickStack when observability is the primary workload, and ClickHouse is the main telemetry store, especially when engineers need search-first investigation, native correlation, session replay, and support for open agentic workflows.

Choose Grafana when you already operate a broad observability datastore estate, need to combine ClickHouse with several other systems, or maintain a large number of cross-system dashboards that depend on Prometheus and shared alerting workflows.

> The Prometheus recommendation is likely to change over time as PromQL and Prometheus support continue to develop in ClickHouse and ClickStack. Check the latest product documentation when making this decision.

Alternatively, use both when Grafana already serves your monitoring estate, but your engineers need a more specialized environment for investigating ClickHouse telemetry and are looking for a platform on which to build their agentic SRE workflows. 

## Conclusion

The interface decision should follow the way your team works. Grafana with the ClickHouse plugin is the stronger fit for multi-engine environments that value a common visualization, monitoring, and alerting layer across many systems. ClickStack is the stronger fit when ClickHouse is the center of the observability architecture, and engineers need a cohesive environment for investigation, correlation, and build your own agent-led analysis.

The choice is also adaptable and can change over time. Your telemetry remains in ClickHouse, and the same data can support both experiences. Start with the interface that matches your current operating model, then add the other if your requirements expand.
