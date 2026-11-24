---
title: "Your agents don't care that you're a batch shop"
date: "2026-11-24T08:22:07.825Z"
author: "Jake Vernon"
category: "Engineering"
excerpt: "Once agents start querying your data at scale, you need a real-time engine. Even if your data arrives in nightly batches. Even if you only query old data."
---

# Your agents don't care that you're a batch shop

## TL;DR

Once agents start querying your data at scale, you need a real-time engine. Even if your data arrives in nightly batches. Even if you only query old data. Efficient query execution means more answers from the same compute, helping control costs as agent demand grows.

## The wrong question

"Where does real-time fit in our business?" Trading desks and risk teams rarely ask me that. They already know, and they come looking for it. The question comes from everyone else: the business units that hear real-time and picture a dashboard with a number that blinks. When they can't find one, the verdict is "we're a batch shop, real-time isn't for us."

That verdict rests on a narrow definition: a fast answer on fresh data, shown to a human. Real-time is that, and it is also what sets the cost of every question your agents ask, including the ones asked of yesterday's data.

Real-time describes how efficiently the system produces an answer. Seen that way, it stops being a use case you shop for and becomes the cost and capacity element of your entire data estate. Agents are about to make that element matter to firms that have never run a low-latency workload.

## Speed is the symptom. Efficiency is the property.

A query returns in 200 ms instead of 20 seconds for one reason: the engine did less work. It read fewer bytes, burned fewer CPU cycles and held memory for less time. Latency is the receipt for that work.

<div class="blog-image-figure" style="margin:0 0 24px;max-width:100%;">
  <img src="/uploads/batch_shop_visual_01_f60d43c368.png" alt="Real-time query latency and four engine properties" width="1600" height="900" style="display:block;width:100%;max-width:100%;height:auto;margin:0;">
  <p class="blog-image-caption" style="margin:8px 0 0;font-family:inherit;font-size:0.8em;line-height:1.5;font-weight:400;font-style:normal;color:#aaa;text-align:left;">what real-time delivers · 1 visible outcome, 4 engine properties</p>
</div>

Everything in the lower band is something you pay for. A query that finishes 100 times sooner hands its cores back 100 times sooner. Those cores are then free for the next query, the next user or the next agent, on the same hardware.

This is why "we don't need sub-second" misses the point. You may not need the answer in 200 ms. You do want to pay for 200 ms of compute instead of 20 seconds of it.

## The batch shop that thinks it's exempt

Much of financial services runs on batch, and for good reasons. End-of-day risk, overnight P&L, regulatory reporting, month-end close and reconciliation all work this way. Data lands on a schedule, jobs run in a window, and people read the output the next morning.

In that world, slow queries hide well. The warehouse is sized for the batch window, and a 40-second ad hoc query costs an analyst a sip of coffee. Humans are a natural rate limiter: a desk of 20 quants asks a few hundred questions a day.

So the firm concludes it will never have a real-time workload. It is right about its data freshness and wrong about its query load. The workload that breaks the model is already in pilot on the same floor, and it never stops for coffee.

## Agents change the math

An analyst asks one question and runs one query. An agent given the same question explores. It lists tables, reads schemas, samples rows, runs a first cut, checks it against a second source, hits an error and retries. One business question becomes tens of queries.

<div class="blog-image-figure" style="margin:0 0 24px;max-width:100%;">
  <img src="/uploads/batch_shop_visual_02_9ced02f69e.png" alt="An analyst query compared with an agent chain of six or more queries" width="1600" height="900" style="display:block;width:100%;max-width:100%;height:auto;margin:0;">
  <p class="blog-image-caption" style="margin:8px 0 0;font-family:inherit;font-size:0.8em;line-height:1.5;font-weight:400;font-style:normal;color:#aaa;text-align:left;">analyst versus agent · 1 query against a chain of 6 or more</p>
</div>

Three things change at once:

- **Volume.** Agents don't sleep, and a desk can run hundreds of them in parallel.
- **Concurrency.** Their queries arrive in bursts instead of spreading across a working day.
- **Compounding latency.** An agent's steps run in sequence. Thirty queries at 10 seconds each is five minutes before the agent says anything. At 200 ms each it is six seconds.

The rest is queueing theory. Throughput on a fixed cluster is roughly its cores divided by the core-seconds each query holds. If every query holds resources for 10 seconds, a handful of agents saturates the cluster and everyone behind them waits.

<div class="blog-image-figure" style="margin:0 0 24px;max-width:100%;">
  <img src="/uploads/batch_shop_visual_03_71e8b3004e.png" alt="Illustrative compute-slot capacity at two query hold times" width="1600" height="900" style="display:block;width:100%;max-width:100%;height:auto;margin:0;">
  <p class="blog-image-caption" style="margin:8px 0 0;font-family:inherit;font-size:0.8em;line-height:1.5;font-weight:400;font-style:normal;color:#aaa;text-align:left;">illustrative · one compute slot, 60 seconds, two hold times</p>
</div>

On a credit-metered cloud warehouse, the standard fix for that queue is to size up or add clusters. You buy your way out. On an engine that finishes in milliseconds, the same cores turn over 50 times in the same interval, so the next agent takes resources that are already free.

A batch shop can keep its stale data and still need this. The agent may be querying yesterday's positions. It still needs each answer fast and cheap, because it asks so many questions to get to one.



---

## Put your agents’ queries to the test

Run your analytical queries on ClickHouse Cloud and compare response times and compute use.

[Try ClickHouse Cloud](https://console.clickhouse.cloud/signUp?loc=blog-cta-3125-put-your-agents-queries-to-the-test-try-clickhouse-cloud&utm_blogctaid=3125)

---

## The workload nobody budgets for

The people driving this load are not engineers. A PM, a product controller or a compliance analyst asks an agent a question and expects it to work. They never see a query, a cluster or an invoice. Agents make it easy to be irresponsible with a budget you don't know you're spending.

<div class="blog-image-figure" style="margin:0 0 24px;max-width:100%;">
  <img src="/uploads/batch_shop_visual_04_15f0c8e3e7.png" alt="Agent workloads across three offices and nine functions" width="1600" height="900" style="display:block;width:100%;max-width:100%;height:auto;margin:0;">
  <p class="blog-image-caption" style="margin:8px 0 0;font-family:inherit;font-size:0.8em;line-height:1.5;font-weight:400;font-style:normal;color:#aaa;text-align:left;">where agent load comes from · 3 offices, 9 functions</p>
</div>

Now scale it the way a firm is organized. Assume 8 users in a pod, 5 pods on a desk, and 1,000 agent queries per user per day inside an eight-hour day.

| Scale | Users | Queries a day | In flight at 12 s | In flight at 0.4 s |
| --- | --- | --- | --- | --- |
| 1 pod | 8 | 8,000 | 3 | under 1 |
| 1 desk (5 pods) | 40 | 40,000 | 17 | under 1 |
| 10 desks | 400 | 400,000 | 167 | 6 |
| 50 desks | 2,000 | 2,000,000 | 833 | 28 |
| 125 desks | 5,000 | 5,000,000 | 2,083 | 69 |

<div class="blog-image-figure" style="margin:0 0 24px;max-width:100%;">
  <img src="/uploads/batch_shop_visual_05_66ae7e5175.png" alt="Illustrative queries in flight as agent usage scales" width="1600" height="900" style="display:block;width:100%;max-width:100%;height:auto;margin:0;">
  <p class="blog-image-caption" style="margin:8px 0 0;font-family:inherit;font-size:0.8em;line-height:1.5;font-weight:400;font-style:normal;color:#aaa;text-align:left;">illustrative · 40 users a desk, 1,000 agent queries per user per day, 8-hour day</p>
</div>

Both lines rise with every desk. The slope is what you pay for, and hold time sets the slope. Here is what each traditional cloud pricing model does with the steeper line.

| Pricing model | What happens as desks scale | Where it lands |
| --- | --- | --- |
| Credit-metered warehouse | Queries queue at the concurrency limit, so clusters get added, each at the full warehouse rate | Chargeback to the desk |
| Cluster-based lakehouse SQL | Autoscaling adds clusters as concurrency rises, billed per cluster-hour | Run-the-bank budget overrun |
| Per-query, priced on data scanned | Every exploratory query is its own charge, used or not | A line item per question |
| Real-time engine | Cores free up in milliseconds, so the same compute absorbs far more desks | Headroom |

Hedge funds feel this faster than banks. At a multi-manager platform, every pod is its own P&L. Technology cost is netted against the pod or passed through to investors. An agent bill that scales with query hold time is a drag on net returns, and it grows with every pod you add.

## Where the P&L takes the hit

The agent compute bill is a product of five terms, and you only control one of them.

<div class="blog-image-figure" style="margin:0 0 24px;max-width:100%;">
  <img src="/uploads/batch_shop_visual_06_34df831f1e.png" alt="Five factors in the agent query cost driver tree" width="1600" height="900" style="display:block;width:100%;max-width:100%;height:auto;margin:0;">
  <p class="blog-image-caption" style="margin:8px 0 0;font-family:inherit;font-size:0.8em;line-height:1.5;font-weight:400;font-style:normal;color:#aaa;text-align:left;">driver tree · 5 terms, 1 controllable</p>
</div>

The first three terms rise by design, because that is what deploying agents means. The vendor sets the price. Compute-seconds per query is the only term your architecture decides.

Here is an illustrative desk: 50 agents, 100 tasks a day each, 40 queries per task. That is 200,000 queries a day. Put your own numbers in; the ratio is what carries over.

|  | Query holds compute for 12 s | Query holds compute for 0.4 s |
| --- | --- | --- |
| Compute held per day | 667 hours | 22 hours |
| Average queries in flight | 28 | 1 |
| Agent wait per 40-query task | 8 minutes | 16 seconds |

That is a 30-fold gap on the same workload. In financial services it lands in specific places:

- **Front office: pre-trade risk and limit checks.** An agent checks exposure against limits before an order goes out. If it queues behind other agents, the order waits and you eat the slippage, or the check gets bypassed and you carry a limit breach.
- **Middle office: intraday P&L explain.** Desk heads want attribution at T+0. Agents can deliver it by rescanning positions, trades and market data all day. On metered compute that cost is charged back to the desk and shows up in its cost-to-income ratio.
- **Front office: TCA and best execution.** Investigating one bad fill means as-of joins of orders against tick data across billions of rows. One investigation is cheap. A thousand a day across every algo and venue is a budget line.
- **Middle office: surveillance and AML alert triage.** Each alert pulls months of transaction history. Slow queries grow the backlog, and a backlog becomes headcount or regulatory exposure.
- **Back office: batch window contention.** Agents working overnight compete with EOD risk and regulatory reporting jobs. T+1 settlement already squeezed that window. A missed batch SLA costs more than any cloud invoice.
- **Every office: the FinOps surprise.** Autoscaling hides the queue until the invoice arrives. Spend that used to track headcount now tracks agent count, and nobody budgeted for that.

## This is an architecture question

You cannot tune a batch engine into this. Work per query is set by design decisions made years before your agents showed up. Whatever you run, these are the properties to look for.

| Property | What it means | Why agents care |
| --- | --- | --- |
| Reads less | Columnar storage and compression, so a query touches only the columns it needs | Fewer bytes and less I/O per question |
| Skips more | Indexes that rule data out before reading it | Exploratory queries don't scan the table |
| Uses every cycle | Vectorized execution across all cores | Fewer CPU cycles per row |
| Precomputes | Aggregates maintained as data arrives | Repeated questions hit ready results |
| Isolates workloads | Separate compute for ingest, batch and agent reads | Agents can't starve the batch run |
| Caps runaways | Limits on time, memory and rows per user or role | A runaway agent gets cut off, not a bigger cluster |

A disclosure: I lead field engineering for ClickHouse in the Americas, and it is one engine built this way. The checklist stands without it.

You also don't have to rip out batch. Every firm I talk to has an Iceberg strategy. Keep the lake as the system of record and keep the heavy transformations where they run today. Serve the data agents need from a real-time engine, or query it in place on the lake.

## You can measure this today

None of this has to be taken on faith. Agents and queries both emit traces. Every model call, tool call and query is a span with a start, an end and a cost.

<div class="blog-image-figure" style="margin:0 0 24px;max-width:100%;">
  <img src="/uploads/batch_shop_visual_07_f6a8b84be2.png" alt="Illustrative nine-second agent task with six spans" width="1600" height="900" style="display:block;width:100%;max-width:100%;height:auto;margin:0;">
  <p class="blog-image-caption" style="margin:8px 0 0;font-family:inherit;font-size:0.8em;line-height:1.5;font-weight:400;font-style:normal;color:#aaa;text-align:left;">illustrative trace · 1 agent task, 6 spans</p>
</div>

In this illustrative trace, one query holds 4.6 of the task's 9 seconds. That is where the compute-seconds term lives, and you only find it if you trace.

There are two layers of telemetry, and you want both:

- **Agent tracing.** What the agent did: model requests, tool calls, tokens and cost.
- **Infrastructure telemetry.** Logs, metrics and traces from the services and databases the agent hits, collected through OpenTelemetry. This is where a slow query shows up as CPU, memory and rows read.

Measure with whatever you already have. Instrument one agent pilot, find the spans that hold the compute, and put a price on them. We pair Langfuse for the agent layer with ClickHouse Observability for the infrastructure layer, and any stack that gives you both views will do.

Measure the whole path, too. A 50 ms query can still be expensive to serve, because the cost also sits in ingesting the data, ordering it, indexing it and keeping aggregates fresh. [CostBench](https://clickhouse.com/benchmarks/costbench), an open benchmark that ClickHouse publishes, prices that full path on a market-data workload: NBBO quotes arriving at a million a second while dashboards and drill-downs run. The code and pricing assumptions are public, so rerun it on your own workload before you trust anyone's number, including mine.

## Ask a different question

Stop asking where real-time fits. Ask how many compute-seconds each answer costs you, and what happens to that number when the ones asking are agents.

Fast answers on fresh data still count. Add the agent load to them, because it is the one that reaches the P&L.

Three things worth doing this quarter:

1. Measure compute-seconds per query on your current platform, by workload.
2. Take one agent pilot and count its queries per task. Multiply by the rollout plan.
3. Run the same queries on a real-time engine and compare hold time, since latency alone understates the gap.

Two caveats, because this is not magic. A fast engine does not fix a badly behaved agent, so you still need guardrails on what agents can run. And cheaper queries invite more queries, so expect the saving to appear as headroom before it appears as a smaller bill.

This is why you need real-time, whether or not a single dashboard in your firm ever blinks. It decides whether your agents scale with the business or your agent bill scales faster than it. The batch shops have the most to gain, because they have never had to count the cost of a question, and their agents are about to ask millions of them.
