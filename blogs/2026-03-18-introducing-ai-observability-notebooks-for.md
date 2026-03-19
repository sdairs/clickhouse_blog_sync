---
title: "Introducing AI observability notebooks for Managed ClickStack in Private Preview"
date: "2026-03-18T12:22:46.974Z"
author: "Mike Shi"
category: "Product"
excerpt: "AI-native observability notebooks for Managed ClickStack let engineers investigate logs, metrics, and traces with AI as a collaborator — keeping humans in control at every step."
---

# Introducing AI observability notebooks for Managed ClickStack in Private Preview

We are launching AI Notebooks for Managed ClickStack in private preview.

This new feature introduces a new way to investigate systems with ClickHouse-powered observability assisted by AI. It brings AI directly into the core SRE workflow, embedding it inside a structured workspace rather than isolating it in a chat window. Engineers can use it to explore logs, metrics, and traces with AI (via Anthropic's Claude models) as a collaborator in the loop. Notebooks is an AI-native workflow where the engineer remains in control and guides every step of the investigation, not an autonomous AI SRE operating independently.

Notebooks provide a persistent workspace where investigations unfold step by step against live data. Engineers can ask questions in natural language to explore anomalies, inspect the model's intermediate reasoning, run and edit real ClickHouse queries, and branch into alternative lines of inquiry without losing context. Each action becomes part of a visible workflow that can be reviewed, refined, or extended, with no hidden logic behind the scenes.

The result is a transparent, human guided environment for deep analysis across logs, metrics, and traces, where AI accelerates the work but the engineer directs the outcome.

> If you are interested in early access, you can [sign up through our private preview form](https://clickhouse.com/cloud/ai-notebooks-in-clickstack-waitlist). We are onboarding teams gradually and working closely with early users to refine the experience.

<h2 id="why_build_a_custom_ai_interface">Why build a custom AI interface?</h2>

AI is quickly becoming part of every developer tool, and observability is no exception. Rather than centering the experience around chat alone, we're providing a collaborative notebook approach that reflects how real investigations happen. Engineers have long used notebooks for exploratory analysis, iterating through queries, visualizations, and notes as they refine their understanding of a problem. Bringing that model to observability creates a space where investigations unfold step by step, with AI assisting along the way while engineers remain firmly in control.

Production debugging is iterative and structured. Engineers move between logs, metrics, and traces. They drill into aggregates, inspect raw events, adjust time ranges, and test hypotheses. Any AI system in this environment needs to support that workflow. It should accelerate analysis without pretending to replace the engineer.

For this reason, Notebooks are designed as a collaborative workflow. The SRE defines what to investigate and guides the process, using the same investigative primitives they already rely on.

<h3 id="designing_for_human_oversight">Designing for human oversight</h3>

AI can accelerate analysis, but it will never be perfect. Any production workflow has to assume that engineers will review, validate, and sometimes correct what it produces. Notebooks are designed around that reality, making collaboration between the SRE and the model efficient and explicit.

<video autoplay="1" muted="1" loop="1" controls="0">
  <source src="https://clickhouse.com/uploads/Notebook_Video_1_118f674a6e.mp4" type="video/mp4" />
</video>

<blockquote>
<p style="font-size: 15px">
Notebooks capture each step of an investigation as a cell on a shared canvas. A cell can contain a user prompt, the model's reasoning and generated query, or fully manual charts, searches, and notes added by the SRE. The investigation unfolds as a visible sequence of steps that can be inspected, edited, or extended at any time.
</p>
</blockquote>

LLM-powered steps generate ClickHouse queries and render each decision stage of the analysis as its own cell making the path to a conclusion visible before a concise summary is delivered. Responses stream in real time, allowing users to follow the investigation as it unfolds.

Importantly, engineers can modify queries or insert manual cells containing charts and searches with Notebooks designed to support a hybrid workflow. You can move from a natural language prompt to a manually crafted SQL query without leaving the workspace - adding charts, tables, event searches, or markdown notes at any stage of the investigation. Keyboard shortcuts and inline editing keep iteration fast.


<video autoplay="1" muted="1" loop="1" controls="0">
  <source src="https://clickhouse.com/uploads/Notebook_Video_Product_546ad0be34.mp4" type="video/mp4" />
</video>

<blockquote>
<p style="font-size: 15px">
Engineers are free to refine, or override AI-generated steps. The collaboration model is explicit: the AI proposes and accelerates, and the engineer inspects and decides.
</p>
</blockquote>

<h3 id="branching_workflows">Branching workflows</h3>

Users can also redirect the investigation at any point using branching capabilities.

We believe this capability is critical to effective SRE-AI collaboration. Complex incidents rarely follow a single line of inquiry. A spike in latency might prompt questions about region, deployment timing, or a downstream dependency. Each hypothesis can evolve independently.

To support this, Notebooks can branch from any cell with the user providing the context to guide the new change in direction.


<video autoplay="1" muted="1" loop="1" controls="0">
  <source src="https://clickhouse.com/uploads/Notebook_Video_Product_1_3c913f51dd.mp4" type="video/mp4" />
</video>

Alternative investigative paths will be investigated without losing prior work, preserving each line of reasoning as part of a navigable tree, where each leaf represents a concluded investigation rather than a transient chat history.

<h2 id="a_native_integration_with_clickstack_tools">A native integration with ClickStack tools</h2>

Notebooks go beyond a chat interface layered on top of SQL. They also go beyond simply exposing a database connection through an MCP server. The integration point is deeper and more opinionated, connecting the model directly to ClickStack's investigative primitives and internal APIs.

These internal APIs act as tools the model can call. Some retrieve metadata about available signals. Others perform structured searches, compute error rates for a specific service, or generate time series charts for selected metrics. Rather than asking the model to construct everything from raw SQL, we give it access to the same building blocks that power the ClickStack interface itself.

![Diagram showing the ClickStack Notebook AI flow, with tools (runSearch, runTime DrTable, getResults Slice, getFile Details, final Conclusion) feeding into ClickHouse, and the numbered request flow from user prompt through LLM to rendered notebook tile](https://clickhouse.com/uploads/564343730_b160aaa9_45e4_4997_9b19_d3e07662c2a0_8603259bae.jpg)

When you ask a question such as "Show error rate by service" or "Find the top slow queries in the last three hours," the model does not simply emit a single SQL query string. It selects and orchestrates the appropriate tools. Behind the scenes, those tools may execute multiple optimized queries, apply predefined aggregation patterns, or route requests through materialized views to assemble the final result efficiently.

This approach has several advantages. The model benefits from the same [performance optimizations built into ClickStack](/blog/clickstack-faster-observability), such as query chunking to avoid large table scans, incremental result streaming, and automatic use of precomputed views. Instead of generating unconstrained SQL, it produces a structured query specification that captures both analytical intent and visualization details, routed through focused endpoints designed for consistency.

However, everything still executes on ClickHouse. The generated SQL is visible, and engineers can modify `WHERE` and `GROUP BY` clauses or apply any supported aggregate function. The system is optimized and opinionated, but not opaque.

Today, these tools are internal to ClickStack. Over time, we expect to expose more of this surface area, enabling other systems to benefit from the same optimized investigative primitives.

<h2 id="built_for_teams">Built for teams</h2>

Notebooks are designed for collaborative environments. Investigations rarely belong to a single engineer, and our long term direction assumes multiple SREs contributing to the same analysis simultaneously. Notebooks can remain private or be shared with team members, with clear visibility into permissions and ownership. Tagging and search make them easy to organize and discover, and automatic saving ensures that investigative context is preserved rather than lost in chat history.

![The Notebooks list view in ClickStack showing private and shared notebooks with name, tags, owner, and timestamps](https://clickhouse.com/uploads/notebooks_mar2026_image2_6d2239d35e.png)

<blockquote>
<p style="font-size: 15px">
Today, shared notebooks follow a simple last write wins model while we remain in private preview. Support for more advanced concurrent collaboration is in progress as we refine the experience with early users.
</p>
</blockquote>

AI capabilities can also be enabled or disabled at the team level, giving organizations control over how and when AI assisted workflows are introduced.

<h2 id="clickhouse_as_an_ai_data_platform">ClickHouse as an AI data platform</h2>

Our approach to AI inside ClickStack is opinionated by design. Notebooks provide a structured, collaborative workspace where SREs stay within their existing observability workflows, accelerating analysis across logs, metrics, and traces. The engineer remains in control inside ClickStack, with AI assisting and proposing next steps as alternative paths are explored towards a root cause.

At the same time, this is not the only way to build AI-powered observability. ClickHouse serves as an open foundation for a growing ecosystem of AI-driven observability and agentic SRE platforms. Tools such as Resolve, WildMoose, and Traversal can build on ClickHouse as their SQL engine, benefiting from its high concurrency, low latency, and long-term data retention, which AI systems rely on for context and performance.

Each platform will bring its own abstractions and opinionated layer. We believe there is room for multiple approaches, with a shared high-performance foundation underneath them.

<h2 id="conclusion_and_looking_forward">Conclusion & looking forward</h2>

We are releasing Notebooks in private preview because we believe this workflow is useful on day one. At the same time, there is meaningful work ahead. In the near term, we are focused on refining the experience: improving sharing, enabling true concurrent editing, and tightening the overall collaboration model as more teams begin using Notebooks together.

Beyond usability improvements, there are several longer term directions we are actively exploring.

One is exposing an MCP server built on the same internal tools that power Notebooks today. These tools encapsulate optimized searches, aggregations, and charting primitives inside ClickStack. Making them accessible externally would allow other platforms, or custom user interfaces, to integrate directly with ClickStack while benefiting from the same acceleration, query optimizations, and structured constructs that Notebooks use internally. The boundary would remain clean: investigative primitives exposed with structured data and text out and accelerated SQL and underneath.

We are also exploring ways to customize global context at both the personal and team level. Observability investigations are shaped by environment, ownership, and conventions. Giving teams control over shared context will make AI assistance more aligned with how they operate.

In the shorter term, we expect to introduce Slack integration before general availability, enabling users to initiate and interact with investigations directly from Slack while preserving the structured Notebook workspace as the source of truth.

Finally, while Notebooks are intentionally collaborative and SRE guided today, we do expect workflows to evolve. AI capabilities are advancing quickly, and it is difficult to predict how autonomous these systems will become over the next year. Rather than betting on building increasingly complex orchestration to compensate for current model limitations, we are focused on getting the interaction primitives right: transparency, structured workflows, strong investigative building blocks, and tight integration with ClickHouse.

---

## Get started today

Interested in seeing how ClickHouse works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-108-get-started-today-sign-up&utm_blogctaid=108)

---