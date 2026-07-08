---
title: "chDB as the Agent's Local Data Engine"
date: "2026-07-07T15:58:57.069Z"
author: "Auxten Wang and Nakul Mishra (AWS)"
category: "Engineering"
excerpt: "chDB embeds a full ClickHouse query engine inside an agent's own process, turning data access, memory, and federation into local function calls instead of network round trips, cutting the latency, retries, and token waste that come with remote queries."
---

# chDB as the Agent's Local Data Engine

## The shape of the problem {#the_shape_of_the_problem}

A chatbot is one request and one response. An **agent** is a loop: it plans, calls a tool, reads the result, reasons, calls another tool, and repeats — typically **5 to 20 tool calls per turn**, very often *sequential*. A large share of those calls are data access: *recall what the user told me earlier, look up the recent events, join this against the catalog.*

![](https://clickhouse.com/uploads/ch_DB_Local_Data_Engine_1_ad33555d2a.png)

Two things happen when that data lives on the other side of a network:

1. **Latency compounds.** 50 ms of round-trip time times ten calls is half a second of dead air the user feels as "the agent is slow" — before the model has done any thinking. Multi-call turns are the fat tail that dominates an agent's p95 task time. [\[7\]](#sources)
2. **Instability becomes a cost center.** Networks jitter and occasionally fail. A single dropped packet triggers a TCP retransmit that adds 200 ms–1 s; a 0.1% packet-loss event alone has been measured to add ~2 s at p99.9. [\[1\]\[3\]](#sources) And in an agent, "the query failed" doesn't end there — it kicks off a retry loop that re-bills the whole context window, and then a detour. That is where the tokens go. [\[5\]\[6\]](#sources)

chDB attacks both at the root: it puts a full ClickHouse query engine *inside the agent's process*. The data layer travels with the agent, so insight latency is bounded by CPU, not by the network.

This article lays out the three ways that matters — **local agent memory**, **a federation hub**, and **stability/token savings** — and backs the third with a first-principles argument plus a table of independent, real-world data.

---

## 1. chDB as Local Agent Memory {#1_chdb_as_local_agent_memory}

Within a single session an agent hammers the same small working set: it revisits *today's* data, it recalls older data the moment the user references it, and it stores distilled preferences and decisions to act on later. Every one of those wants a fast, deterministic local query — not a trip to a warehouse.

First, get clear on what memory is. Here is an all-too-familiar agent failure: *yesterday* it hit a constraint and worked out a fix that stuck; *today*, facing the same task, it reads only the prompt — not yesterday's fix — so it runs the failed plan again and burns tool calls on retries. The model isn't dumb — the right context just wasn't **queryable at the moment it was needed**.

An agent's context is just a pile of data: instructions, working data, memory, eval history. "Memory" was never about stuffing more into the prompt — it is about **pulling the few rows that matter *right now* with a single query**. Recall is a query, not a bigger prompt.

![](https://clickhouse.com/uploads/ch_DB_Local_Data_Engine_2_eb65d031bc.jpg)

chDB is a good fit because it inherits the **ClickHouse kernel**, which natively handles, in one engine:

- **Structured data**, **time-series**, and **vector storage + vector search**, plus inverted indexes for text.
- Pair that with a **local embedding model** (here, Alibaba's Qwen) and chDB's purely local storage, and you have an efficient, fully on-box memory: embed and recall without anything leaving the machine.

This is the crux of "why a database, not a vector store": **vector search is just an index; agent memory is the whole database around it.** SQLite holds small state but has no columnar scans, no vectors, and can't read remote files; Pandas is great in memory but dies past RAM and can't query files you never loaded; a pure vector DB only does similarity — it can't filter + JOIN + aggregate + audit in the *same query*. Pulling out "the few memories that matter now" needs exactly that union of capabilities.

**Archive the raw, search the compressed.** The industry consensus is to keep the rawest data as an archive — like the deep stacks of a library: rarely read, but there for the moment the agent needs to go dig. ClickHouse compresses raw data *and searches on the compressed data efficiently*, so archiving costs almost nothing in retrieval speed.

That unlocks a tidy ingestion pattern. An agent produces memories as a continuous trickle of small batches — which is exactly the workload that *wrecks* an online OLAP warehouse if you write it directly. Instead:

<pre><code type='click-ui' language='python'>
# Hot memory lives locally, written at trickle speed with no warehouse pressure
sess = chdb.session.Session("/tmp/agent")
sess.query("INSERT INTO memory VALUES (...)")   # cheap, local, no network

# Then sync to the warehouse on a sane cadence — hourly / daily archival
# (relieving the online warehouse from a storm of tiny writes)
</code></pre>

**Memory should be a history — so don't *update* it, *append* to it.** Agent memory has a lifecycle: *remember* (an explicit decision) → *recall* (similarity + filter) → *conflict* (new information that's similar to, but differs from, an old belief) → *revise* (the better belief wins). Say the old memory is "this repo uses Poetry," and it later becomes "this repo standardizes on uv" — you usually want not just the current answer, but **how that belief evolved**.

![chDB Local Data Engine Revised (1).png](https://clickhouse.com/uploads/ch_DB_Local_Data_Engine_Revised_1_f25f27ce8e.png)

To keep that revision trail intact, the right move is the plainest **MergeTree + append-only**: every revision is a new immutable row with a `version` (or timestamp) column; deletes are a soft `is_deleted` flag, not a real delete. The belief's evolution is preserved in full, and append-only happens to be ClickHouse's fastest, zero-write-amplification path.

<pre><code type='click-ui' language='sql'>
CREATE TABLE memory
(
    memory_id   UUID,
    content     String,
    embedding   Array(Float32),
    version     UInt64,                 -- or a DateTime64 timestamp
    is_deleted  UInt8 DEFAULT 0,
    created_at  DateTime64(3) DEFAULT now64()
)
ENGINE = MergeTree
ORDER BY (memory_id, version);
</code></pre>

One table then answers three kinds of question (`cosineDistance` tells you how close two pieces of text are, where 0 means identical):

<pre><code type='click-ui' language='sql'>
-- Current state + semantic recall: take each memory's latest version, drop deletes, then rank by similarity
-- (order matters: filtering is_deleted first would resurrect the older version of a deleted memory)
SELECT content,
       1 - cosineDistance(embedding, {q:Array(Float32)}) AS meaning
FROM (
    SELECT * FROM memory
    ORDER BY memory_id, version DESC
    LIMIT 1 BY memory_id
)
WHERE is_deleted = 0
ORDER BY meaning DESC
LIMIT 8;

-- Full history: just scan
SELECT * FROM memory WHERE memory_id = {id:UUID} ORDER BY version;

-- Point-in-time: "what did the agent believe as of version t"
SELECT * FROM (
    SELECT * FROM memory
    WHERE version <= {t:UInt64}
    ORDER BY memory_id, version DESC
    LIMIT 1 BY memory_id
) WHERE is_deleted = 0;
</code></pre>

Need to slice by project, tags, or task history? Add a few `WHERE` / `JOIN` lines. And if you read the current state very often and don't want to scan history every time, the cleanest approach is a Materialized View that projects the current state into a ReplacingMergeTree mirror table: **the base table (MergeTree) keeps the full history for audit and retrospection, while the mirror serves only the hot-path current state** — far cleaner than forcing one engine to do both.

**Memory ≈ Observability ≈ History.** Here is the elegant part. The data an agent keeps *for memory* overlaps heavily with what an observability stack keeps. With ClickHouse's acquisition of **Langfuse** (LLM observability), chDB can serve all three locally — observability traces, agent memory, and conversation history — as a *single query surface*. Three concepts collapse into one, and on serverless pricing that becomes a genuinely clever architecture.

And the three are isomorphic by nature: an observability trace is never *rewritten* — it is append-only by construction, the same shape as the memory model above. Columnar + append-only both dodges the write amplification of in-place UPDATEs and keeps the full history as an audit trail. Langfuse choosing to build LLM observability on ClickHouse is a sideways confirmation of exactly this.

**This pattern is already packaged as open source.** The whole thing — lifecycle, recall, local-first — is open-sourced as [`auxten/clickmem`](https://github.com/auxten/clickmem) (built on chDB): create a memories table → write explicit decisions → recall with "similarity + filter" → evaluate which memory actually helped; embeddings run locally with `Qwen/Qwen3-Embedding-0.6B`, nothing leaving the box. Want to build the core yourself? Use it as a template.

![](https://clickhouse.com/uploads/ch_DB_Local_Data_Engine_4_3b2028419a.jpg)

---

## 2. A Federation Hub: data access becomes a function call {#2_a_federation_hub_data_access_becomes_a_function_call}

chDB inherits ClickHouse's support for **80+ data formats** (CSV — including dirty CSV with schema sniffing — Parquet, ORC, JSON, Arrow, and more) and a wide range of access paths: **local files, HTTP/HTTPS, S3/GCS/Azure, FTP, HDFS**, even a CSV inside a zip behind a URL. It just reads them.

That makes chDB a **data federation hub**: one SQL statement can join a local file, a remote ClickHouse table, an in-process Pandas DataFrame, and a third-party database (MySQL, PostgreSQL, MongoDB, Redis) — each treated as a table.

<pre><code type='click-ui' language='python'>
# One query. Four sources. No connection pools, no credential brokering,
# no risk of DDoS-ing production RDS when 1,000 agents fire at once.
chdb.query("""
    SELECT u.tier, avg(t.amount), p.category
    FROM s3('s3://lake/txn.parquet')                  AS t
    JOIN postgresql('rds:5432','users', ...)          AS u USING (uid)
    JOIN remote('clickhouse-cloud','products', ...)   AS p USING (sku)
    WHERE t.ts > now() - INTERVAL 1 HOUR
    GROUP BY u.tier, p.category
""")
</code></pre>

Two properties make this especially good *for agents*:

- **Agents are fluent in pandas.** chDB v4 ships a thorough pandas-compatible API. Pandas is the lingua franca of Python data science — Spark and most modern dataframe libraries were shaped by it — and LLMs write it extremely well. So an agent can express local + remote filtering and shaping *in the idiom it is best at*, and chDB compiles it down to the optimized engine.
- **SQL is declarative — it describes intent, not mechanism.** That is arguably *the* reason SQL has survived for decades: you say *what* you want, not *how* to compute it. ClickHouse's extensions follow the same philosophy. The payoff for agents is focus: the agent spends its tokens on *business intent*, not on hand-writing brittle ETL and data-plumbing code.

---

## 3. Stability and Token Optimization (the part that matters most) {#3_stability_and_token_optimization_the_part_that_matters_most}

Localizing data removes network uncertainty. A local query has no wire to traverse, so its return is fast and — the word that matters — **stable**. And stability is not merely a latency nicety. In an agent loop, **stability is a token problem.**

### Why a flaky data call costs *tokens*, not just milliseconds {#why_a_flaky_data_call_costs_tokens_not_just_milliseconds}

When a tool call fails, an agent does not shrug it off the way a microservice does. The documented behavior is:

1. The model receives the error and **retries** — and in an agent loop, *every retry re-sends the full conversation context to the LLM*. A retry costs a whole context window, not one cheap HTTP round-trip. [\[6\]](#sources)
2. If retries keep failing, the model "gets creative" and **takes a detour** — trying a different query, a different tool, a different plan. More tokens, more latency, for data it already needed.

In production traces this waste is pervasive and usually invisible, because the turn eventually *succeeds* — the cost only shows up on the bill. [\[5\]](#sources)

### A concrete detour {#a_concrete_detour}

> A customer-support agent is mid-session and needs the user's recent preference history to answer. It issues a query to the warehouse. The warehouse is briefly busy — a `Server busy`, a disk stall, a dropped packet. The model gets the error, **re-sends its 14k-token context** and retries. Still slow. It retries again. Then it "reroutes": maybe it queries a different table, or asks for a broader slice and filters in its own head. Several thousand tokens and several seconds later, it has the answer it could have had instantly.
>
> The same agent backed by chDB calls `sess.query(...)`, gets the rows in **sub-millisecond time, deterministically, every single time**, and never enters the retry/detour spiral at all.

![](https://clickhouse.com/uploads/ch_DB_Local_Data_Engine_5_2e7180206b.jpg)

### Think it through: why local is necessarily more stable {#think_it_through_why_local_is_necessarily_more_stable}

**A local query is a function call.** Its latency distribution is a tall, narrow spike set by CPU and memory bandwidth — no RTT, no jitter, no packet loss, no server-side queueing. Its p50 and p99 are practically the same number. **Determinism** is the point: the same speed every time.

**A remote query, however fast the server, still has to cross the wire.** Base RTT + jitter + the occasional TCP retransmit + server-side contention stack up, which means its p99/p999 is set not by compute but by the worst network event. In other words, the remote tail is **structural** — you can't optimize it away, because it isn't in your process at all.

**And the killer is compounding.** Let the success probability of a single call be `(1 − p)`. Then a turn of N *sequential* calls all succeeds with probability `(1 − p)^N`. At N = 10, even with p of just 2%, about **18%** of turns hit at least one failure — which lines up neatly with the field observation that a "2% tool error rate → ~20% agent failure." [\[4\]](#sources) And each failure isn't a cheap HTTP retry; it's a retry that **re-bills the entire context window**, usually followed by a detour. [\[6\]](#sources)

So the causal chain is clear: **network instability → token-priced retries → even-more-token detours** — and where it finally shows up is the invoice, not the latency chart. Localizing the hot path cuts the chain at its source.

### This isn't theory — it shows up in the wild {#this_isnt_theory_it_shows_up_in_the_wild}

Every link in that argument is grounded in independent, public engineering write-ups. The pattern — *remote calls → instability → token waste* — is widely observed:

| Observation | The number | Source |
| --- | --- | --- |
| Uncontrolled retries during an outage vs a circuit-broken path (one conversation, 30 s window) | **~200x** token cost (~$2 → ~$0.01) | [\[6\]](#sources) |
| A real traced retry loop: 7 retries on a 14k-token prompt to discover a `429` | **~100,000 tokens**; that one loop = **18%** of monthly tokens; hidden bottlenecks ate **47%** of tokens over 30 days | [\[5\]](#sources) |
| A modest tool error rate amplifies into agent failure | a **2%** tool error rate → **~20%** agent failure; **90.8%** of retries in a 200-task benchmark were spent on non-retryable errors | [\[4\]](#sources) |
| Network tail latency | **0.1%** packet loss → **~2 s** at p99.9; a TCP retransmit adds **200 ms–1 s** | [\[1\]\[3\]](#sources) |
| Retry stacking across layers | a 5-deep call chain retrying 3x per layer multiplies DB load **243x** | [\[8\]](#sources) |
| Latency compounding | agents make **5–20** tool calls/turn; multi-call turns dominate the p95 tail | [\[7\]](#sources) |

The takeaway is simple: the most reliable network call is the one you don't make. Memory and hot data that get queried over and over within a session are exactly the things that should be **local**.

---

## 4. Bringing it to AWS: chDB × AWS Lambda MicroVMs {#4_bringing_it_to_aws_chdb_aws_lambda_microvms}

The architecture gets concrete here — and it is not just an idea. **chDB is the only data-infrastructure launch partner invited for [AWS Lambda MicroVMs](https://aws.amazon.com/lambda/lambda-microvms/).** [\[9\]](#sources)

**What Lambda MicroVMs is.** It is a new serverless compute primitive that fuses three things: VM-level isolation, near-instant launch and resume, and state persistence across interactions. It is built on the same **Firecracker** virtualization that powers **15 trillion+** Lambda invocations a month, purpose-built to run user- or AI-generated code. You start a MicroVM, connect over a **dedicated HTTPS endpoint**, and begin executing code — each MicroVM has its own kernel, memory, and disk state, retained for up to **8 hours**, automatically **suspended** when idle and **resumed** on demand, with **no charge while suspended**. [\[9\]](#sources)

**Why it and chDB are a perfect match.** This is exactly where the article's three pillars land in the cloud:

- **One private chDB per isolated workload.** Firecracker hardware isolation + snapshot-based fast starts + suspend/resume let every MicroVM carry its own *private* chDB engine — hot from the first millisecond, billed only while it actually runs. There's no shared database to scale, and nothing for a thousand agents to overload at once.
- **Small questions in, small answers out.** chDB pushes compute down to the data and returns only small results — a natural fit for that dedicated endpoint: the heavy lifting happens inside the VM, and all that crosses the endpoint is a small request and a small answer.
- **"Thinking in place," with zero network round-trips.** Inside the MicroVM, the agent and chDB share one process; memory, federated SQL, and vector search all happen at CPU speed — the "network instability → token waste" chain from Section 3 is physically severed here.

![](https://clickhouse.com/uploads/ch_DB_Local_Data_Engine_6_c14609e44a.jpg)

**We're building a set of reference architectures on this combination:**

- **A federated query hub** — inside a single MicroVM, one query joins local data, S3, a CDN, and Postgres.
- **Isolated CI/CD runners** — every test gets a clean chDB, with no shared server to drag down.
- **On-demand sandboxes** — an AI agent can spend hours reproducing a bug inside a disposable VM.
- **A per-session "agent brain"** — chDB is the local memory and federation layer the agent thinks with, suspended and resumed right alongside the user's session.

**See it running.** [`nklmish/chdb-lambda-microvm-demo`](https://github.com/nklmish/chdb-lambda-microvm-demo) is a worked example of exactly this — a natural-language *NYC Taxi analytics agent* that carries its own in-process chDB inside a Lambda MicroVM: local append-only memory, single-SQL federation out to S3 / PostgreSQL / ClickHouse Cloud, and sub-millisecond recall, with each MicroVM snapshot-hot and billed only while it runs.

In code, stateless and stateful are each just two lines:

<pre><code type='click-ui' language='python'>
# Stateless: one-shot federated query — an ad-hoc agent tool call, or ETL inside the MicroVM
chdb.query("SELECT ... FROM s3(...) JOIN postgresql(...) ...")

# Stateful: a persistent MergeTree for agent memory / session state, surviving the MicroVM's suspend/resume
sess = chdb.session.Session(path="/session/acme")   # per-session isolation
sess.query("SELECT * FROM memory WHERE ...")
</code></pre>

(If you're already building agents on **Bedrock AgentCore**, the same "per-session chDB" model applies just as well — AgentCore Runtime is also built on Firecracker microVMs, and its **Memory**, **Gateway**, and **Observability** services map one-to-one onto the memory + federation + Langfuse story above. [\[10\]](#sources))

**Graduating to ClickHouse Cloud** When the working set outgrows local capacity, point the *same* SQL at the warehouse:

<pre><code type='click-ui' language='python'>
# Day 1: hot memory is local
sess.query("SELECT * FROM memory WHERE ...")

# Day 100: the dataset grew → federate to Cloud. Same SQL, same types, same engine.
sess.query("CREATE VIEW memory AS SELECT * FROM remote('cloud...', memory)")
sess.query("SELECT * FROM memory WHERE ...")   # unchanged
</code></pre>

No other embedded engine can offer this, because no other embedded engine shares its query plane with a managed cloud warehouse.

---

## Closing {#closing}

Three pillars, one idea:

- **Local agent memory** — structured + time-series + vector in one engine; an append-only revision model that preserves the belief's evolution and gives you "time travel" for free, collapsing memory, observability, and history onto a single local query surface (chDB + Langfuse).
- **A federation hub** — one declarative SQL (or fluent pandas) across local files, remote ClickHouse, DataFrames, and third-party DBs, so the agent spends tokens on intent, not plumbing.
- **Stability and token savings** — localizing the hot path removes the network's jitter and failures, and with them the retry/detour spiral that quietly drains an agent's token budget.

> **ClickHouse Cloud is where your data lives; chDB is what your agent thinks with; and Lambda MicroVMs is where it gets to think, in private.**

### Get started {#get_started}

chDB is one line away:

<pre><code type='click-ui' language='bash'>
pip install chdb
</code></pre>

- **Give your agent a local memory.** Point a `Session` at a path and you get a persistent MergeTree — vectors, time-series, and structured rows in one engine, queried at CPU speed. For a ready-made "memory lifecycle + recall" implementation, see the open-source [`auxten/clickmem`](https://github.com/auxten/clickmem).
- **Federate in a single query.** Join local files, S3/Parquet, Postgres, and remote ClickHouse with no connection pools and no credential brokering.
- **Run it privately inside an isolated sandbox.** On AWS Lambda MicroVMs, every session carries its own private chDB — millisecond warm starts, billed by runtime, disposable — with no shared server to overload.
- **Graduate when you outgrow local.** Point the same SQL at ClickHouse Cloud via `remote()` — zero refactoring.

Docs: [https://clickhouse.com/docs/chdb](https://clickhouse.com/docs/chdb) · Source: [https://github.com/chdb-io/chdb](https://github.com/chdb-io/chdb)

---

## Sources {#sources}

1. *Latency and Tail Latency at Scale in Distributed Systems* — TCP retransmit (RTO) adds ~200 ms–1 s. [https://rahulsuryawanshi.com/distributed-systems/scalability-performance/tail-latency/](https://rahulsuryawanshi.com/distributed-systems/scalability-performance/tail-latency/)
2. *Tail Latency (P99) Optimization* — cross-zone packet loss ~0.1–1%. [https://systemdr.systemdrd.com/p/tail-latency-p99-optimization-why](https://systemdr.systemdrd.com/p/tail-latency-p99-optimization-why)
3. *What Is P99 Latency?* (Aerospike) — 0.1% packet loss → ~2 s at p99.9. [https://aerospike.com/blog/what-is-p99-latency/](https://aerospike.com/blog/what-is-p99-latency/)
4. *Retry Amplification: How a 2% Tool Error Rate Becomes a 20% Agent Failure* — ~10k wasted input tokens on a 3-retry give-up; 90.8% of retries on non-retryable errors. [https://tianpan.co/blog/2026-04-23-retry-amplification-agent-tool-error-rate-cascade](https://tianpan.co/blog/2026-04-23-retry-amplification-agent-tool-error-rate-cascade)
5. *I Turned on Agent Tracing for 30 Days* — 7 retries on a 14k-token prompt ≈ 100k tokens; one retry loop = 18% of monthly tokens; 47% of tokens eaten by hidden bottlenecks. [https://dev.to/kenimo49/i-turned-on-agent-tracing-for-30-days-4-hidden-bottlenecks-were-eating-47-of-my-tokens-1pa6](https://dev.to/kenimo49/i-turned-on-agent-tracing-for-30-days-4-hidden-bottlenecks-were-eating-47-of-my-tokens-1pa6)
6. *The Retry Storm Problem in Agentic Systems* — uncontrolled retries cost ~200x vs circuit-broken. [https://tianpan.co/blog/2026-04-10-retry-storm-agentic-systems-cascading-failure](https://tianpan.co/blog/2026-04-10-retry-storm-agentic-systems-cascading-failure)
7. *Cost & Latency Engineering for AI Agents* — multi-call turns dominate the p95 tail. [https://learnaivisually.com/tracks/agent-engineering/cost-latency](https://learnaivisually.com/tracks/agent-engineering/cost-latency)
8. *Timeouts, retries, and backoff with jitter* (Amazon Builders' Library) — 5-deep retry stack → 243x DB load. [https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/)
9. *AWS Lambda MicroVMs* — a Firecracker-based serverless compute primitive: VM-level isolation, near-instant launch/resume, state retained up to 8 hours, no charge while suspended; chDB is an invited data-infrastructure launch partner. [https://aws.amazon.com/lambda/lambda-microvms/](https://aws.amazon.com/lambda/lambda-microvms/)
10. *What is Amazon Bedrock AgentCore?* — Runtime (Firecracker microVMs), Memory, Gateway, Observability. [https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/what-is-bedrock-agentcore.html](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/what-is-bedrock-agentcore.html)
