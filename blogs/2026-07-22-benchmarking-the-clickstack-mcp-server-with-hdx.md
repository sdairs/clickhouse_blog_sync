---
title: "Benchmarking the ClickStack MCP Server with hdx-evals"
date: "2026-07-22T14:31:38.761Z"
author: "Brandon Pereira"
category: "Engineering"
excerpt: "A behind-the-scenes look at hdx-evals, the open-source framework we built to benchmark the ClickStack MCP server against a raw SQL baseline using deterministic synthetic incidents, sandboxed Claude agents, and blind LLM grading — and why the MCP scored hi"
---

# Benchmarking the ClickStack MCP Server with hdx-evals

Last month at Open House in San Francisco, [we introduced the ClickStack MCP server](https://clickhouse.com/blog/announcing-managed-clickstack-mcp-server), a set of purpose-built observability tools that give AI agents structured, high-level primitives for investigating production incidents instead of hand-assembling raw SQL. On stage, we shared early results from benchmarking the ClickStack MCP against a generic ClickHouse SQL interface: 18% more accurate root cause and remediation outcomes, 26% fewer tool calls, and 2.4x more consistent results run over run.

![clickstack_bench_0.png](https://clickhouse.com/uploads/clickstack_bench_0_3ac4970027.png)

Those numbers prompted plenty of questions about how we measured them, so this post explains exactly what we did.

Shipping MCP (Model Context Protocol) tools that agents use to investigate production incidents introduces a new kind of risk. The same question asked twice doesn't always produce the same answer, and a refactored tool, a renamed parameter, or a change in query logic can quietly degrade investigation quality in ways you won't catch without a structured way to measure them.

We needed to answer two things. First, whether each new version of the MCP produced better investigative outcomes than the last. Second, whether the MCP actually outperformed an agent with direct SQL access to ClickHouse. To do that, we built `hdx-evals`, a reproducible benchmarking framework that seeds identical synthetic telemetry, runs Claude agents against each configuration, and scores the results blindly across implementations. Because the framework runs every combination of MCP and model, a useful side benefit fell out of it: when a new model ships, we can point `hdx-evals` at it and see how it performs on the same scenarios before deciding what to run in production.

> `hdx-evals` is open source and lives in the HyperDX repository. If you want to follow along with the code, see [github.com/hyperdxio/hyperdx/tree/main/packages/hdx-eval](http://github.com/hyperdxio/hyperdx/tree/main/packages/hdx-eval).

## ClickStack MCP vs ClickHouse MCP {#clickstack_mcp_vs_clickhouse_mcp}

Before we turn to the benchmark scenarios, we’ll briefly revisit why we built a dedicated ClickStack MCP alongside the ClickHouse MCP. If you’re already familiar with the distinction, you can skip ahead to the incident scenarios.

The ClickHouse MCP gives agents direct access to ClickHouse through SQL. This is flexible, but it leaves the model to discover the schema, construct each query, and assemble multi-step investigation workflows itself. In observability investigations, this can lead to extra tool calls, inefficient queries, high-cardinality results, and inconsistent approaches between runs.

The ClickStack MCP instead provides higher-level semantic tools for common observability tasks, such as finding recurring event patterns, comparing time windows, identifying outliers, and moving between logs and traces. These tools still execute SQL underneath, but they package the query logic and return structured results that are easier for an agent to use. The aim is to improve accuracy and consistency while reducing tool calls and common query errors. The scenarios below test whether those advantages hold across different types of investigation.

![](https://clickhouse.com/uploads/clickstack_mcp_evals_jul2026_image7_b192902bf0.png)

## Incident scenarios {#incident_scenarios}

![clickstack_bench_1.png](https://clickhouse.com/uploads/clickstack_bench_1_d3af19abd6.png)

A benchmark is only as good as the incidents it tests against. If they're too clean, every agent looks brilliant. If they're too unrealistic, the results tell you nothing about how the MCP performs in production.

So each `hdx-evals` scenario simulates a real incident: tens of millions of synthetic logs and spans, seeded deterministically so every run starts from identical data, with a planted anomaly buried inside realistic noise, plus distractors: secondary issues timed and worded to look like the real problem. An agent that jumps to the first error it sees should fail. An agent that reasons through the data should not.

The data is completely synthetic rather than derived from the OpenTelemetry Demo, existing products, or recorded telemetry. Public datasets often contain well-known and documented failure modes that may already appear in a model’s training data. Reusing them could allow an agent to recognize a familiar incident instead of investigating it through the available tools, so generating original scenarios helps us test the agent’s investigative ability rather than its prior knowledge.

Traces and logs are generated deterministically in TypeScript from a seeded Pseudo-Random Number Generator (PRNG) and written directly into ClickHouse tables that mirror ClickStack's real OTel schema. Topology varies per scenario, from a single `api-server` up to 25 named e-commerce services plus ~100 procedurally-generated background services for cardinality. Volume is deliberate: `error-root-cause` alone plants only 8 failing traces inside 12M+ spans and 12M logs, so the eval measures whether the agent can isolate a small planted incident from look-alike distractors on top of a healthy baseline, not whether it can count errors.

We built five scenarios in total, each targeting a different investigative skill:

* **error-root-cause** is a payment-service database timeout cascading into checkout 500s, hidden among 24M spans and logs across 25 services. Six distractors include a CDN error burst at 10x the volume of the real signal, designed to fool any agent that reaches for `WHERE StatusCode = 'ERROR'` first.  
* **latency-spike** is a p99 (99th-percentile latency) regression affecting only enterprise tenants because of a missing index, buried in 20M spans across 5,000 tenants. A feature-flag confounder correlates 80% with the affected segment but isn't causal, and a same-latency-range distractor at an unrelated endpoint sits in the same time window.  
* **noisy-signals** asks the agent to identify logs that can be dropped or throttled to reduce ingestion and storage costs. The dataset contains 16 million logs. Each high-volume, low-value log pattern is paired with an equally common but important pattern from the same service and severity level. For example, dropping all DEBUG logs from `notification-service` would remove both routine cache-hit messages and the delivery records needed to confirm that notifications were sent.  
* **service-health-check** is a four-hour, single-service dataset of 36M events with no incident at all. Four subtle novel signals must be surfaced proportionally, and two recurring patterns must not be escalated. This one matters as much as the others, because half of a good benchmark is rewarding the right answer and the other half is penalizing a confident wrong one.  
* **segmented-regression** is an error spike across 6M traces that only appears at the intersection of two dimensions (enterprise tier and cache miss). Neither axis alone reveals the problem, so the agent has to cross-tabulate to find it. It's a textbook Simpson's Paradox setup.

Take `noisy-signals` as an example. The agent must determine which of 16 million logs can be dropped or throttled without losing important operational information. Half of the `notification-service DEBUG` logs are routine cache-hit messages that are safe to remove. The other half record notification deliveries and must be retained as an audit trail.

The two types of logs share the same service and severity level, so filtering on those fields alone cannot separate them. Grouping by the complete log message does not help either, because values within the messages vary widely. The agent must instead group similar messages into patterns, then distinguish the expendable cache logs from the essential delivery records. This scenario tests whether the MCP’s event patterns tool gives the agent the right way to do that.

![clickstack_bench_2.png](https://clickhouse.com/uploads/clickstack_bench_2_80c0014c8f.png)

## Setting up and seeding telemetry {#setting_up_and_seeding_telemetry}

Before any agent runs against an incident, `hdx-evals` builds out a ClickStack environment in three stages: provisioning, schema, and data generation.

**Provisioning** creates an evaluation account, connections, and sources, plus MCP server definitions for both the ClickStack MCP (over HTTP) and the ClickHouse MCP (over stdio). A deny-list of 11 non-investigation tools, such as dashboards, alerts, and saved searches, keeps the agent focused on query tools only. Everything is written to a single `eval.config.json`, and setup is idempotent, so it can be re-run safely.

**Schema** creates the eval tables as structural clones of ClickStack’s production OTel tables (`CREATE TABLE ... AS default.otel_traces`), so they inherit the real schema, engine, and indexes rather than an approximation. Each scenario gets six tables: raw traces and logs, plus rollup tables built from a two-stage materialized view pipeline that mirrors ClickStack’s production metadata discovery path. That means the MCP's "what fields exist?" queries hit pre-aggregated rollups instead of scanning raw data — the same optimization that powers autocomplete and facet generation in the ClickStack UI. You can [read more about how these materialized views work in the ClickStack docs](https://clickhouse.com/docs/use-cases/observability/clickstack/materialized_views).

**Data generation** writes the actual telemetry. All randomness flows through a single seeded PRNG, so a given seed and anchor time always produce byte-identical data. That's the same dataset every run, which is what makes A/B comparisons between MCPs meaningful. Data streams in batches to keep memory bounded, even at millions of rows.

Each scenario uses a fixed “current” time, which is passed to the agent with its instructions. This ensures that phrases such as “in the last 10 minutes” always refer to the same period in the seeded data, regardless of when the evaluation runs. The dataset can therefore be generated once and reused; before each run, the framework checks that it exists and creates it if necessary.

![clickstack_bench_3.png](https://clickhouse.com/uploads/clickstack_bench_3_254e26de36.png)

## The runner {#the_runner}

Once data is seeded, `hdx-evals` spawns a real Claude Code process for every (MCP, model, run) combination and lets it investigate the scenario the way an SRE would, with no scaffolding and no hints, just the question and the tools. 

| Scenario | System Prompt |
| :---- | :---- |
| error-root-cause | Checkout requests are failing for some users in the last 10 minutes. Find the root cause. |
| latency-spike | p99 latency on api-server has jumped in the last 15 minutes. What's slow and why? |
| segmented-regression | API error rate has gone up in the last 10 minutes for some users. Find the segment(s) where the regression is concentrated and what's going wrong. |
| service-health-check | Routine status check on api-server over the last hour. Summarize key SLIs (traffic, error rate, latency) and call out anything novel or worth a closer look. Don't escalate routine variance. Be concise. |
| noisy-signals | We want to cut log ingest cost. What are the top noisy signals we should drop or throttle? |

Each run gets its own sandbox: a fresh, ephemeral temp directory, a single MCP server definition (only the one being evaluated), and a tool permission file that strips out everything except investigation tools. There's no bash, write, edit, glob, or webfetch capabilities, and read access is scoped only to that run's own temp directory. This wasn't a precaution we added on a whim. In early iterations, we found Claude poking around the filesystem looking for prior run output, scoring criteria, or ground-truth answers - effectively looking for a way to cheat rather than investigate. Locking each run into its own disposable, blind sandbox closes that door entirely. There's no repo root, no prior runs, and no eval config visible from inside.

Each sandbox uses several layers of isolation. Filesystem restrictions control what the agent can access, while the deny-list limits which actions it can take. Each run also executes in its own process group, allowing the runner to terminate the agent and any subprocesses reliably during cleanup. At timeout, a graceful `SIGTERM` escalates to a `SIGKILL` against the whole process group five seconds later if anything is still alive, such as an orphaned MCP subprocess. The temp directory is always removed afterward, even if the process never successfully launched, since leaking an MCP config with live API keys is not an acceptable failure mode.

![clickstack_bench_4.png](https://clickhouse.com/uploads/clickstack_bench_4_d353d38936.png)

Runs are dispatched through a simple worker pool. Every (MCP, model, run index) triple is flattened into a queue, and workers pull the next available cell until the queue is empty. A failed run doesn't take down the batch. It's recorded as a failure, and the pool moves on.

![clickstack_bench_5.png](https://clickhouse.com/uploads/clickstack_bench_5_644c4f1ac9.png)

Each agent gets the same system prompt skeleton: a role as an SRE, the anchor time fixed so that "the last 10 minutes" means the same thing every run, and a budget of roughly 15 to 25 tool calls before it's expected to commit to an answer. We deliberately never describe the schema. The agent has to discover it through the MCP itself, because schema discovery is part of what's being evaluated, not a given. The full trajectory of every run gets recorded, including every tool call, every result, and every token spent. This lets the grading step reconstruct exactly how an agent arrived at its answer, not just what it answered.

## Grading in depth {#grading_in_depth}

Every run produces a final answer: a block of text where the agent names the root cause, cites evidence, and rules out what it didn't think was responsible. Grading that answer is a three-stage pipeline of programmatic checks, an LLM judge, and a tool-error penalty, combined into a single score.

**Programmatic checks** are weighted regex tests that run directly against the final answer. Each scenario has positive checks (does the agent name the right service, error type, span) and negative checks (does it blame a distractor it shouldn't). The negative checks aren't doing language understanding; they're matched against a tight proximity window around causal phrasing. The TLS handshake distractor check in `error-root-cause` for example, only fires if "tls handshake" appears within 80 characters of "root cause" or "caused by." So "the root cause was a database timeout; TLS handshake was ruled out" doesn't match, but "the root cause was the TLS handshake failure" does. It's a heuristic, not semantic parsing, which is why the LLM judge is there to catch what regexes can't.

**The LLM judge** scores the same final answer against predefined criteria that are difficult to assess with regex, such as whether the agent’s reasoning is coherent and whether the evidence supports its conclusions. Critically, the answer is blinded before the judge sees it, by replacing MCP-specific tool names and brand terms with anonymous labels ("MCP A", "MCP B"). This ensures the judge scores answer quality against ground truth rather than which tool the agent used to get there. The judge accounts for 60% of the combined score.

**The tool-error penalty** deducts up to 20% for agent-attributable tool failures: queries that timed out, malformed inputs, and tools called incorrectly. Infrastructure errors like rate limits, server 503s, and TCP failures are filtered out before the penalty is calculated, so the agent isn't punished for the cluster having a bad moment. The penalty is rate-based rather than count-based, so one failure in one call is treated the same as twenty failures in twenty calls.

The three combine into a single formula:

<pre><code type='click-ui' language='bash'>
combined = clamp((0.4 × programmatic + 0.6 × judge) − penalty, 0, 1)
</code></pre>

One thing worth calling out about the rubric design is that the negative checks are as important as the positive ones. In `error-root-cause`, there are five negative checks, one for each distractor, using a proximity regex that only triggers when the agent explicitly draws a causal link to the wrong service. An agent that hedges ("SMTP failures were also present but are not related to the checkout errors") passes. An agent that confidently blames the CDN fails, even if it also names the real root cause somewhere in the answer.

## What we learned {#what_we_learned}

Building an MCP server that reliably improves agent performance takes more than adding the right tools. You also have to get the details right across several dimensions at once.

**Tool descriptions and schemas matter more than they look.** Too few parameters, or parameter descriptions vague enough to be open to interpretation, and the agent can't tune queries the way it needs to. For example, a filter param described only as "filter results" forces the model to guess at syntax and semantics, so it either avoids using it or uses it inconsistently across calls. Too many parameters, on the other hand, and you see more hallucinations and lower consistency, since the model has more surface area to get wrong or conflate. Finding the right level of expressiveness is an ongoing calibration.

**Response design is the most important surface.** Returning the correct information is table stakes. What separates good MCP tools from great ones is how they behave at the edges. When too many rows are returned, the tool should provide hints to guide the agent toward a more targeted query. When an error occurs, it should return actionable next steps rather than a raw stack trace. We found that when agents hit unclear errors on their first tool call, they often abandon that tool entirely for the rest of the investigation.

**Speed compounds.** If a tool takes too long to return, agents are less likely to call it again. This is especially true early in an investigation, where the agent is still forming a hypothesis, and a slow response breaks momentum. Production-grade query performance directly shapes investigative quality.

## Results {#results}

The results below compare the ClickHouse MCP server, which gives the agent direct access to the data through SQL, with the ClickStack MCP server and its purpose-built observability tools for investigating logs and traces. ClickStack scored higher across all five scenarios, with its advantage ranging from 7 to 20 percentage points as of the time of writing.  The numbers below measure the combined overall score. Running the evals yourself yields a rich set of data points, allowing you to dissect the results along many axes.

| Scenario | ClickStack MCP | ClickHouse SQL MCP | Delta |
| :---- | :---- | :---- | :---- |
| error-root-cause | 93% | 73% | +20pp |
| noisy-signals | 64% | 45% | +19pp |
| latency-spike | 60% | 43% | +17pp |
| segmented-regression | 75% | 60% | +15pp |
| service-health-check | 61% | 54% | +7pp |

We generated these results using Claude Opus 4.6, with ten runs for each MCP in every scenario. Repeating each evaluation reduces the influence of an unusually strong or weak run. A perfect score means the agent identified every expected finding, avoided every incorrect conclusion, and satisfied the qualitative criteria assessed by the LLM judge.

## What's next for evals {#whats_next_for_evals}

The framework is working, but there's meaningful ground still to cover.

The most immediate priority is moving evals into CI. That means improving setup time, leveraging ClickHouse Cloud for pre-seeded databases to enable faster concurrency on smaller machines, containerizing the process, and wiring up GitHub Actions to run evals automatically when the MCP changes. Right now evals are a deliberate manual step, but they should be a gate.

Beyond the pipeline, we want to expand scenario coverage. The current five scenarios focus on trace and log investigation, the core SRE workflows. But ClickStack is broader than that, and dashboard generation quality, alert success rates, and metrics investigation each deserve their own scenarios. The framework is designed to accommodate them, so building them out is the next step.

The goal is a version of `hdx-evals` where every meaningful change to the ClickStack MCP, whether a new tool, a renamed parameter, or a modified response schema, runs through a reproducible benchmark before it ships. We want evals to be a first-class part of the development workflow, not an afterthought.

## Conclusion {#conclusion}

As observability becomes more agent-driven, the tools we ship for agents become part of the production incident path. Like anything else in that path, their quality has to be measurable. The numbers we shared at Open House aren't a one-time result. They're the output of a framework we run repeatedly, on deterministic data, blinded so the score reflects investigative quality rather than which tool produced it.

That's what lets us improve the ClickStack MCP with confidence. We can measure each new tool, schema change, or response tweak against the last and against a raw SQL baseline before it reaches users.

We've open-sourced `hdx-evals` so others can do the same. If you're building MCP tools for observability, or for anything where agent consistency matters, the framework, scenarios, and grading pipeline are all available at [github.com/hyperdxio/hyperdx/tree/main/packages/hdx-eval](https://github.com/hyperdxio/hyperdx/tree/main/packages/hdx-eval). We'd love to see new scenarios, grading improvements, and contributions from the community.


---

## Get started today

Interested in seeing how ClickHouse works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-1362-get-started-today-sign-up&utm_blogctaid=1362)

---

[Link](link)
