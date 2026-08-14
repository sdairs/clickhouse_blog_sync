---
title: "ClickStack and Hud bring runtime intelligence to AI-powered development"
date: "2026-08-13T12:53:04.085Z"
category: "Engineering"
excerpt: "ClickStack and Hud now share trace IDs, pairing service-level observability with function-level runtime forensics so coding agents can assess risky changes before they ship, catch regressions right after deploy, and fix them with real production context."
---

# ClickStack and Hud bring runtime intelligence to AI-powered development


AI now generates or assists with [42% of the code developers ship, and that share is expected to reach 65% by 2027](https://www.sonarsource.com/blog/state-of-code-developer-survey-report-the-current-reality-of-ai-coding/). ClickHouse, via its open source observability stack ClickStack, tells teams when and where something broke. Hud’s runtime code sensor tells them why, how to fix it, and whether a risky change should be allowed into production in the first place.

Today, ClickHouse and Hud are announcing an integration that closes the loop across the AI software development lifecycle. Coding agents can generate changes in minutes, but human review and traditional testing cannot always determine how those changes will behave in the real world. 

The hard problem has moved: not producing code, but knowing which changes are safe to ship, detecting problems once they are live, and giving both engineers and agents enough context to resolve them quickly. Together, ClickStack and Hud provide the stack modern engineering teams need to build and ship with AI confidently, with ClickStack providing service-level observability and Hud complementing it with the function-level runtime context needed to identify issues in code before they reach production.

This post covers how AI-forward engineering teams can implement this approach by connecting the ClickStack and Hud MCP servers to a single coding agent and using shared trace IDs to correlate service-level observability with function-level runtime context across pre-deployment checks, release monitoring, and incident response.

## Two layers, stronger together

ClickStack and Hud operate at different layers, which is exactly why they work well together.

ClickStack uses OpenTelemetry data to give teams broad visibility across complex distributed systems and infrastructure. It helps localize an issue to a service, deployment, and endpoint, at scale.

Hud operates at the code layer. Its Runtime Code Sensor captures function-level metrics and deep forensic context, connecting production behavior to the source code and changes behind it. **It requires no manual instrumentation, and it runs with low overhead in production.**

Instrumenting every function in an application with OpenTelemetry is impractical. Once ClickStack narrows the search space, Hud provides the fine-grained context needed to understand exactly what happened inside the code.

This is also what separates Hud from OpenTelemetry auto-instrumentation. 

Auto-instrumentation hooks the libraries and frameworks an application already uses, so it covers the boundaries: incoming requests, outgoing calls, and database queries. It does not reach the functions your team and your coding agents write, because those are not library calls. Hud covers that layer automatically, with no spans to add by hand and no per-function volume to pay for.

In customer-configured workflows, Hud can assess code changes before deployment against production runtime behavior and flag risky changes for review. After deployment, ClickStack uses service-level telemetry to localize issues to the affected service, deployment, or endpoint, while Hud identifies the function-level behavior and code changes behind them. Together, they give engineers and coding agents the context needed to decide whether to roll back or fix the code.

![clickstack_hud_aug2026_image3.png](https://clickhouse.com/uploads/clickstack_hud_aug2026_image3_a89c8abeb9.png)

"Like every modern engineering organization, a growing share of our code is now written with AI. We write code much faster, but the challenge has shifted to shipping just as quickly while maintaining confidence that new code won’t cause harm. ClickHouse gives us the wide operational picture at scale, while Hud gives us the runtime intelligence and next-level introspection needed to evaluate and ship AI-generated code confidently. When issues do arise, combining ClickHouse and Hud allows us to triage and resolve them quickly. For a company building with AI, that combination is the obvious choice."

*Rom Kadria,Senior Software Engineer, monday.com*

## Connecting ClickStack and Hud with trace IDs

The two datasets stay correlated through a deliberately boring mechanism: trace IDs. The forensics Hud captures are enriched with the same trace IDs that ClickStack stores with its traces and logs. That single shared key is what makes the combined system more than two products side by side.


<video autoplay="1" muted="1" loop="1" controls="0">
  <source src="https://clickhouse.com/uploads/Hud_issue_Hyper_DX_1_52a90d860b.mp4" type="video/mp4" />
</video>


When Hud identifies a failing or regressed function, its forensics pinpoint the exact traces involved and link directly to the corresponding logs in ClickHouse. This takes engineers straight to the relevant signals, without forcing them to scan low-signal data or manually narrow the investigation by timeframe. The integration also works in reverse: when ClickStack detects an issue, the agent can query Hud for the code-level context needed to understand and fix it.

## Alerts that arrive with their root cause

Many regressions start small: a query slows down, a code path consumes more resources, a function misbehaves under one specific workload. These shifts show up in function-level data before they are visible in service-level metrics or user reports.

Hud’s Runtime Code Sensor detects these issues and flags them alongside the code-level root cause of the failure or performance regression.

"Our users already trust ClickHouse to store and query their Open Telemetry data at scale. The shift now underway is from simply watching systems or investigating issues to using that data to make day-to-day engineering decisions. Hud connects observability data to the code and changes behind it, making the entire stack more useful for teams building and shipping software with AI."

*Mike Shi, Head of Observability, ClickHouse*

---

## See runtime intelligence in action with Hud and ClickStack

Discover how ClickStack and Hud help your team ship AI-generated code faster—and with confidence. Book a demo today.

[Book a demo](https://clickhouse.com/company/contact?loc=blog-cta-1528-see-runtime-intelligence-in-action-with-hud-and-clickstack-book-a-demo&utm_blogctaid=1528)

---


## Build the agentic workflows to unlock true agentic engineering

With ClickStack and Hud, teams can build agentic coding workflows that bring more runtime context into the SDLC. The integration supports bring-your-own-agent workflows, including:

1. Auto-triage and auto-fix workflows for errors and performance degradations  
2. Release monitoring workflows that flag regressions immediately upon a new release compared to previous versions, with rollback mechanisms and a code-level fix produced from Hud’s root cause data.  
3. Pre-deploy risk assessment that scores PRs against real runtime behavior from production.



![](https://clickhouse.com/uploads/clickstack_hud_aug2026_image1_8818d57a84.png)

![](https://clickhouse.com/uploads/clickstack_hud_aug2026_image4_5ae2610e6f.png)


Runtime intelligence can be used to help streamline agentic coding by focusing on the bottleneck: how the team can safely ship AI-generated code to production. An AI-generated change gets evaluated against how the affected functions actually behave in production before it ships, taking real forensic data of parameters and behavior to compare against \- so risky changes are held for review, testing, or correction. 

With ClickStack and Hud, the agent is not only reasoning over isolated alerts or static code, but over real, recent operational data with function-level context, and the history of how the application behaves \- this is what makes autonomous engineering safe enough to trust.

"AI is accelerating how quickly teams can generate code, but safely shipping it with high confidence requires production context. Hud and ClickHouse bring real production behavior at an unparalleled breadth and depth, so teams can build a production-aware AI SDLC: Gating before it ships, proactive verification once it is deployed, and fix issues as they arise \- all using real runtime truth. Together with ClickHouse, we are bringing that intelligence across the entire AI SDLC."

*Roee Adler, CEO, Hud*

## Getting started

As AI writes more software, ClickHouse and Hud are building toward a production-aware engineering stack where runtime intelligence is available at every stage of the AI SDLC. 

We’re excited to hear about your experience as we expand on this integration. 

To try it, install the Hud SDK and connect it to your ClickStack account. Runtime intelligence starts flowing alongside the OpenTelemetry data you already collect. You can [read the docs](https://docs.hud.io/docs/clickhouse-clickstack-integration) to get set up.  





---

## Try it today

Discover how ClickStack and Hud help your team ship AI-generated code faster—and with confidence. Book a demo today.

[Book a demo](https://clickhouse.com/company/contact?loc=blog-cta-1529-try-it-today-book-a-demo&utm_blogctaid=1529)

---