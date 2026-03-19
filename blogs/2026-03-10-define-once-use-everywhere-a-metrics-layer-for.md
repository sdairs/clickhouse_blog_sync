---
title: "Define once, use everywhere: a metrics layer for ClickHouse with MooseStack"
date: "2026-03-10T14:46:25.293Z"
author: "Fiveonefour and Nakul Mishra (AWS)"
category: "Engineering"
excerpt: "This post shows a lightweight metrics layer for ClickHouse using MooseStack, an open source developer agent harness for ClickHouse."
---

# Define once, use everywhere: a metrics layer for ClickHouse with MooseStack

Let’s say you’re tracking data on revenue in your ClickHouse database. Metrics about revenue might be served up to interested parties in a variety of places: BI tools, custom dashboards, API endpoints, agentic tools, MCP servers, AI chat, etc. Are the numbers the same in every place? Maybe, maybe not. When the same metric is re-defined in multiple locations (or generated on the fly by an LLM), it's easy for that definition to skew. It happens more often than you might think. 

The below example is based on something we saw at one of our customers: their custom chat client vibe-SQLed a definition of revenue that made sense (sum of `amount`), but didn’t exclude transactions that were incomplete (Figure A: chat overstates revenue). That kind of mistake becomes impossible with a well-defined metrics layer (Figure B: chat matches actual revenue).

![](https://clickhouse.com/uploads/1_cdd0a13188.png)

![](https://clickhouse.com/uploads/2_0e4864ac05.png)

*Image 1 shows chat going rogue on the definition of revenue. Image 2 shows how the metrics layer keeps everything consistent.*

When I was at Nike, we had to work hard to make sure this didn’t happen just across our APIs. Now, there’s APIs, dashboard, chats and AI, MCP… The surface area for inconsistency has multiplied.

And what happens when we need to change that definition? We end up with two problems:

1. Metrics need to be consistent everywhere. Same definition, same answer, across chat, APIs, dashboards, and MCP. One mistake kills credibility.  
2. Metrics need to be easy to define and change safely. Add a metric once, update it once, and have every surface stay in sync when the schema changes. The developer experience needs to be better than manually crafting all this.

In this post, we’ll introduce an approach for a lightweight metrics layer (or “query layer” or “semantic layer”) on top of ClickHouse. We’ll use MooseStack, an open source developer agent harness for ClickHouse, to implement our metrics layer in code, where our coding agents can help accelerate the process.

If you want to jump straight into some sample code, check out [the repo for the demo app](https://github.com/514-labs/financial-query-layer-demo) that you can see in the screenshots above. If you want to go straight to implementing this yourself, check out [the docs](https://docs.fiveonefour.com/moosestack/reference/query-layer) or the [tutorial guide](https://docs.fiveonefour.com/guides/chat-in-your-app/tutorial). 

## Define once, project everywhere

There are a bunch of semantic / metric layer approaches out there that all have their own advantages and disadvantages (take cube.dev, dbt metrics, MetricFlow, Looker; and frontend first approaches like TanStack Table and AG Grid).

The approach we’ll cover today doesn’t rely on external systems or human processes for correctness: it's an as-code metrics layer. Define your metrics once in code. Project them to every surface.

A metric has three components:

1. The aggregation: the SQL expression (what to calculate). `SUM(amount)`, `COUNT(DISTINCT user_id)`, `AVG(duration)`.  
2. Dimensions: what to group by (how to slice it). Region, month, status. Column keys or SQL expressions.  
3. Filters: what constraints are valid (how to scope it). Which columns can be filtered, which operators are allowed.

These three components assemble into any query your surfaces need. "Revenue by region this quarter" becomes: aggregation = `sumIf(amount, status = 'completed') AS revenue`, dimension = `region`, filter = `timestamp >= Q1 start`.

Another benefit is that multiple metrics can share the same dimensions and filters. That helps keep not just business logic consistent, but also grain: how data is sliced, grouped, and compared.

The query model is the source of truth. Each surface consumes it differently:

- First party chat: the model constrains which metrics the LLM can query. No freestyle SQL. The model is the guardrail. (When you build your own chat, you have much more control over the user experience, including how tools are called).  
- MCP: the model becomes a tool definition. Same metrics in Claude Desktop, Cursor, any agent client.  
- API: the model generates parameterized SQL. Deterministic. No LLM in the loop.  
- Dashboard: the model's metadata drives the UI. Dimension pickers, metric selectors, filter controls.

[The demo application covers all of these with some toy data, so you can see how metrics are defined, and how they interact with these different surfaces.](https://github.com/514-labs/financial-query-layer-demo)

## A type-safe query model

Let’s assume you are doing your data modeling in ClickHouse, and want *everything* as easy, type-safe code, that comes with a developer harness (dev MCP, skills etc.) to make it easy to work with. If you want to implement metrics with the approach above, you can use [MooseStack's](https://github.com/514-labs/moosestack) open source `QueryModel`. 

![3.png](https://clickhouse.com/uploads/3_d129fddf9a.png)

QueryModels take Data Model objects as inputs, that represent ClickHouse tables (`OlapTable`), Views (`View`) or Materialized Views (`MaterializedView`), and let you define metrics, dimensions, and filters on top.

```typescript
// The data model — defines the table schema 
interface EventModel {
  /** When the event occurred */
  // MooseStack propagates JSDocs describing the tables and columns 
  // to ClickHouse as comments 
  event_time: Date;
  /** Unique identifier for the user who triggered the event */
  user_id: string;
  /** Lifecycle state: active, completed, or refunded */
  status: "active" | "completed" | "refunded";
  /** Geographic region where the event originated */
  region: string;
  /** Transaction value in USD */
  amount: number;
}

// The OlapTable — typed reference to the ClickHouse table
export const Events = new OlapTable<EventModel>("events", {
  orderBy: "event_time",
});

// Your query model — references the data model directly
export const eventsModel = defineQueryModel({
  name: "events",
  description: "Event analytics: user activity and engagement metrics",
  table: Events,  // <-- typed reference to the OlapTable

  dimensions: {
    region: { column: "region", description: "Geographic region" }, 
    day: {
      expression: sql.fragment`toDate(${Events.columns.event_time})`,  // <-- Column object, not a string 
      as: "time", 
      description: "Daily time bucket",
    },
    month: {
      expression: sql.fragment`toStartOfMonth(${Events.columns.event_time})`,
      as: "time",
      description: "Monthly time bucket",
    },
  },

  metrics: {
    totalEvents: { agg: sql.fragment`count(*)`, description: "Total number of events" },
    totalAmount: { agg: sql.fragment`sum(${Events.columns.amount})`, description: "Sum of all event amounts" },  // <-- Column object
    uniqueUsers: { agg: sql.fragment`uniq(${Events.columns.user_id})`, description: "Distinct users" },  // <-- Column object
  },

  filters: {
    timestamp: { column: "event_time", operators: ["gte", "lte"] as const },  // <-- typed against EventModel keys
    region: { column: "region", operators: ["eq", "in"] as const },
  },

  sortable: ["totalAmount", "totalEvents", "uniqueUsers"] as const,
});
```

[Run code block](null)

### Type safety back to the table

Since metrics are built on Data Models, you get type-safety end-to-end. In the example below, dimensions and filters are generic over `keyof Transaction`. Metrics reference `TransactionTable.columns.totalAmount` (a `Column` object, not a string). Rename or remove a field in your data model and the query model gets a compile error, not a silent wrong answer in production.  

![4.png](https://clickhouse.com/uploads/4_e21e0fc3f9.png)

Here, I changed `totalAmount` to `total_Amount` (ugh) and you can see all the dependent query models show the type-error. That keeps the metrics layer and the ClickHouse tables defined in code necessarily in sync.

### One definition, every surface

The same `eventsModel` object then becomes a chat tool, an MCP tool, and an API:

<pre><code type='click-ui' language='typescript'>
// Chat — Vercel AI SDK tool
const tool = createModelTool(transactionMetrics);
// tool.schema has the zod params, tool.buildRequest parses them, transactionMetrics.toSql generates the query
</code></pre>

<pre><code type='click-ui' language='typescript'>
// MCP — register as tool for Claude Desktop, Cursor, etc.
registerModelTools(server, [transactionMetrics], mooseUtils.client.query);
</code></pre>

<pre><code type='click-ui' language='typescript'>
// REST API — deterministic SQL, no LLM
const data = await buildQuery(transactionMetrics)
  .metrics(["revenue"])
  .dimensions(["region"])
  .orderBy(["revenue", "DESC"])
  .execute(client.query);
</code></pre>

Add a metric to the model, it shows up on every surface. 

### Metrics are still code

Importantly, it's not a config of a dashboard, or a fingers crossed attempt at prompt engineering.

Your metric definitions go through the same PR review, CI, and deployment pipeline as everything else.

## The dev harness in action

MooseStack isn’t just a developer framework. The framework and the tooling surrounding it (the dev MCP, the skills, the CLI) make up the dev agent harness ([the guide will walk you through setting it up](https://docs.fiveonefour.com/guides/chat-in-your-app/tutorial?lang=typescript)). This agent harness turns your regular coding agent (Claude Code, Cursor, etc) into a ClickHouse specialist, which can drastically accelerate your implementation of a metrics layer.

Once the harness is ready, one prompt can add a metric:

```
"Add a revenue metric. Revenue is the sum of amount for completed events only."
```

The dev harness knows your data models and your query models. It adds the metric using TypeScript and moose-lib to extend the query model object.

### The diff

```diff
metrics: {
  totalTransactions: {
    agg: count(),
    as: "totalTransactions",
    description: "Total transaction count across all statuses",
  },

  completedTransactions: {
    agg: sql`countIf(${TransactionTable.columns.status} = 'completed')`,
    as: "completedTransactions",
    description: "Count of completed (settled) transactions",
  },

+ revenue: {
+   agg: sql`
+     sumIf(
+       ${TransactionTable.columns.totalAmount},
+       ${TransactionTable.columns.status} = 'completed'
+     )
+   `,
+   as: "revenue",
+   description: "Total revenue from completed transactions only",
+ },
},
```

One edit only: add the metric to the model, and it propagates across all existing query surfaces.

### Check the blast radius

The infra map shows every surface that consumes `transactionMetrics`, which the agent can retrieve with the MooseDev MCP infra map tool call:

<pre><code type='click-ui' language='bash'>
$ get_infra_map search="transactionMetrics"

Components:
  WEB_APP  /tools               → pulls_data_from: [transactions]   # MCP tools (registerModelTools)
  WEB_APP  /revenue/by-region   → pulls_data_from: [transactions]   # Dashboard API (buildQuery)
  WEB_APP  /transaction/metrics → pulls_data_from: [transactions]   # Report builder API (buildQuery)
  CHAT     /api/chat            → pulls_data_from: [/tools]         # Chat UI (AI SDK → MCP client)
</code></pre>

Four surfaces. The new `revenue` metric is now available on all of them. Chat users can ask for it. MCP clients can query it. The API endpoint can serve it. The dashboard can display it.

### Validate the SQL

Call the MCP tool with "revenue by region this quarter" and inspect the generated SQL:

<pre><code type='click-ui' language='sql'>
SELECT
    region,
    sumIf(totalAmount, status = 'completed') AS revenue  -- constraint from the metric definition
FROM transactions
WHERE timestamp >= toStartOfQuarter(now())
     AND timestamp <= now()
GROUP BY region
ORDER BY revenue DESC
</code></pre>

The `sumIf` came from the metric definition. The `WHERE` came from the filter. The `GROUP BY` came from the dimension. Nothing was improvised. The model produced the SQL, and you can read it to verify.

<video autoplay="0" muted="0" loop="0" controls="0">
  <source src="https://clickhouse.com/uploads/harness_demo_descript_b2a0c8fcac.mp4" type="video/mp4" />
</video>

## Putting Metrics into practice

A query model only helps if your team treats it as the contract for production analytics. What we recommend is a practice like:

**Ad-hoc SQL for discovery. Query model for production.**

Chat in your product, dashboard cards, report APIs, MCP tools exposed to users or internal teams: all of those should consume the same model. That is how "revenue" stops being three implementations and becomes one definition.

Freeform chat/chat-to-SQL still has a place. We keep it for development, exploration, debugging, and analyst/admin workflows. But that is a discovery path, not a production path. Once a number matters enough to appear in a product surface, it gets promoted into the query model.

In practice, adoption looks like this:

* **Exploration first.** A developer, analyst, or PM asks a question in chat or writes an ad hoc query.  
* **Codify the metric.** Once the definition is useful and stable, it gets added to `defineQueryModel()`.  
* **Project it everywhere.** Chat tools, MCP tools, APIs, and dashboards all consume that definition.  
* **Review it like code.** Changes to metric definitions go through PR review, tests, and normal deployment.  
* **Limit bypass paths.** Production surfaces do not ship hand-written SQL for metrics that already exist in the model.

This is where the "as code" part matters. The model is not just a convenience for generating SQL. It gives the team a shared artifact to review, version, and own. Product’s definition is in that code, not in a document. Engineering refers to the same code for analytical feature development. Agents can consume it. 

The goal is not to eliminate ad hoc analysis, but to make sure ad hoc analysis is not the thing your product depends on.

That is the adoption pattern we think works best: **explore freely, standardize deliberately, serve consistently.**

## Try it out

One `defineQueryModel()`. Type-safe back to your tables and views. Chat, MCP, and API from the same definition. The dev harness builds it. The type system keeps it in sync. Code review and SDLC keeps it safe. Try it out yourself:

- [**The guide**](https://docs.fiveonefour.com/guides/chat-in-your-app/tutorial?lang=typescript)**.** Step-by-step from zero to production: data models, query models, query builder, chat, MCP, brownfield setup (`moose init --from-remote`), auth, and deployment.  
- [**The demo app**](https://github.com/514-labs/financial-query-layer-demo)**.** Check out the example implementation, including frontend with dashboard, AI chat, and report builder.   
- [**Start from 514 Hosting**](https://fiveonefour.boreal.cloud/sign-up)**.** Sign up for Fiveonefour, get a hosted ClickHouse backend, and deploy with preview branches and schema migration support. 514 Hosting proudly uses ClickHouse Cloud.

### Acknowledgements

Thanks to Nakul Mishra from AWS for feedback on the post, and for validating the Fiveonefour agent harness with AWS’s agentic coding IDE, Kiro - including the newly developed [Kiro Power for ClickHouse](https://github.com/nklmish/clickhouse-kiro-power). Nakul’s views and opinions are Nakul’s own.

Thanks to MooseStack / ClickHouse community members Lukáš Kozelnický and Michael Klein for the hands-on feedback, and the F45 team, Loyalsnap team and Oliver Naaris for feedback on the demo.