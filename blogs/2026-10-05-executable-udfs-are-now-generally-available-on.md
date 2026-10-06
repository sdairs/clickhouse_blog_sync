---
title: "Executable UDFs are now generally available on ClickHouse Cloud"
date: "2026-10-05T14:46:00.886Z"
author: "Francisco Neves, San Tran, Jia Xu, Zach Naimon, Ilya Andreev, Hanzi Jiang and Kevin Zhang"
category: "Product"
excerpt: "Executable UDFs are now generally available on ClickHouse Cloud across AWS, GCP, and Azure, with native runtimes, network access, observability, and API and Terraform support."
---

# Executable UDFs are now generally available on ClickHouse Cloud

> TL;DR
> Executable UDFs are GA on ClickHouse Cloud across AWS, GCP, and Azure, with a Native runtime for compiled Rust/Go/C++/JavaScript, network access, memory limits, a `deterministic` flag, Cloud API + Terraform support, and per-query UDF metrics in 26.6+. Below, we use them to count and price LLM tokens and grade completions inside ClickHouse.

*Note: companion code here - *[*github.com/ClickHouse/llm-token-udf*](https://github.com/ClickHouse/llm-token-udf)*.*

Four months ago we put executable UDFs into public beta on ClickHouse Cloud: write a function in Python, upload it as a zip, call it from SQL like any built-in.  The requests we got during the beta were pretty consistent.  People wanted to upload compiled code rather than Python, wanted UDFs on Azure, wanted network access without opening a support ticket, and wanted to see what their UDFs were doing to the cluster.

Today, we are happy to announce that **executable UDFs are generally available on ClickHouse Cloud** on AWS, GCP, and Azure.  Since the beta announcement, we have added:

- Native runtime - upload a precompiled, statically linked binary instead of a Python script.  Rust, Go, C++, and JavaScript (compiled with Bun <!-- VERIFY: pinned version + target -->) are supported today.
- Network access - the private-beta feature from the beta post is now available in every organization.  UDFs can make outbound calls to public endpoints.
- Azure - UDFs now run on all three clouds.
- A per-process memory limit, and a `deterministic` flag that lets the query cache serve queries that call your UDF.
- 12 UDF endpoints in the Cloud API, and `clickhouse_udf` / `clickhouse_udf_attachment` resources in the Terraform provider (3.24.0+) with per-service version pinning.
- 8 `ProfileEvents` counters and 2 asynchronous metrics in ClickHouse 26.6+, so a query's UDF cost (wall time, pool wait, CPU, memory, bytes over the pipe) shows up in `system.query_log` next to everything else.

UDFs are not billed separately.  They run inside your service's pods and consume the same CPU and memory as your queries.

The beta post scored ~6 billion stock trades with a PyTorch autoencoder.  This time we built something closer to what most of you told us you're doing with UDFs, which is accounting - in this case, working out where an LLM bill goes using the prompts you're already logging into ClickHouse.  Full source for the UDFs, SQL, and Terraform is at [github.com/ClickHouse/llm-token-udf](https://github.com/ClickHouse/llm-token-udf).

## Why tokens?

If you run anything on top of an LLM, you log the calls somewhere: prompt, completion, model, latency, probably a trace ID.  Increasingly that somewhere is ClickHouse, via ClickStack, Langfuse, or an OpenTelemetry collector using the GenAI semantic conventions.

What you don't reliably have is a token count.  Providers return `usage` on most responses, but not on streamed ones (some do, some don't, some only with a flag), not through every proxy, and not from self-hosted models.  In the synthetic dataset below, ~30% of spans arrive with no usage at all, which is roughly what you'd see if you stream responses to users.  And when `usage` is present, it's a total.  It can't tell you that 41% of your support bot's input spend is a system prompt that hasn't changed since March, or that your retrieval layer started returning twice as many chunks last Tuesday.

Counting tokens is a library call (`tiktoken` in Python, `tiktoken-rs` in Rust), so the problem is not the counting.  The problem is that the library lives in code and the prompts live in a table.  You can export the prompts, count them in a notebook, and load the counts back, which is slow, stale, and one more pipeline to babysit.  You can implement byte-pair encoding over a 200k-entry vocabulary with `arrayFold` (please don't).  Or you can put the library next to the data.

## What we built

Two UDFs and some SQL:

- `count_tokens(model, text) -> UInt32` - a Rust binary on the Native runtime.  Deterministic and CPU-bound, called four times per span at insert time by a materialized view.
- `judge_response(prompt, completion) -> Tuple(score, verdict, reason)` - a Python UDF with network access that asks Claude to grade a sample of completions, with the output constrained via tool-use.  Called every 10 minutes by a refreshable materialized view.

Everything else is ordinary ClickHouse: a dictionary of model prices (pulled from a public price list with `url()`, since fetching a JSON file is not a job for a UDF), two materialized views, and the queries.

```text
┌───────────────────────────┐
│  llm_spans                │     ← prompts, completions, model, usage (often NULL)
└──────────────┬────────────┘
               │ INSERT
               ▼
┌───────────────────────────┐
│  llm_span_tokens_mv       │     ← fires on every INSERT
│  (calls count_tokens ×4)  │
└──────────────┬────────────┘
               │
               ▼
┌───────────────────────────┐     ┌──────────────────────────┐
│  llm_span_tokens          │ ⟵─┤  model_prices (dict)     │ ← url() + refreshable MV, daily
│  system / context / user /│     └──────────────────────────┘
│  completion token counts  │
└───────────────────────────┘
               ▲
               │ every 10 min, 2% sample
┌──────────────┴────────────┐
│  llm_evals_mv             │     ← refreshable MV, APPEND
│  (calls judge_response)   │        over the network
└───────────────────────────┘
```

## The tokenizer, as a Native UDF

The Native runtime (not to be confused with ClickHouse's `Native` *format*, which is one of the I/O format options for any UDF) takes a zip with two folders, `amd64/` and `arm64/`, each containing a statically linked Linux executable named `main` plus any data files you want alongside it at runtime.  Both architectures are required because ClickHouse Cloud runs on both.  The binary runs with no arguments and nothing is installed for you, so everything it needs has to be compiled in.

`count_tokens` is ~100 lines of Rust around `tiktoken-rs`.  Most of it is the wire protocol, which is the same one a Python UDF speaks, just in binary:

```rust
// Deploy as: executable_pool, runtime = Native, format = RowBinary,
// send_chunk_header = true, deterministic = true.
// Arguments: (model String, text String) -> UInt32
fn main() {
    let mut tok = Tokenizers::load();           // reads models.json from the binary's directory
    let mut stdin = BufReader::with_capacity(1 << 20, io::stdin().lock());
    let mut stdout = BufWriter::with_capacity(1 << 20, io::stdout().lock());
    let (mut header, mut model, mut text) = (String::new(), Vec::new(), Vec::new());

    loop {
        // 1. chunk header: row count as decimal text + '\n' (send_chunk_header)
        header.clear();
        match stdin.read_line(&mut header) {
            Ok(0) => return,                    // pipe closed; pool process exits cleanly
            Ok(_) => {}
            Err(e) => die(&format!("reading chunk header: {e}")),
        }
        let rows: usize = header.trim().parse().unwrap_or_else(|_| die("bad chunk header"));

        // 2. N RowBinary rows: each String is a LEB128 length + raw bytes
        for i in 0..rows {
            read_string(&mut stdin, &mut model)
                .and_then(|_| read_string(&mut stdin, &mut text))
                .unwrap_or_else(|e| die(&format!("row {i}: {e}")));
            let n = tok.count(&String::from_utf8_lossy(&model), &String::from_utf8_lossy(&text));
            stdout.write_all(&n.to_le_bytes()).unwrap_or_else(|_| process::exit(1));
        }
        // 3. N UInt32 answers, flushed once per chunk
        stdout.flush().unwrap_or_else(|_| process::exit(1));
    }
}
```

We used `RowBinary` rather than the `TabSeparated` format from the beta demo.  TSV was fine for 14 numeric features, but prompts are full of tabs, newlines, and backslashes that would need escaping on both sides of the pipe, whereas RowBinary is binary-safe and ClickHouse doesn't have to format text on the way out or parse it on the way back in.  In our testing, moving a UDF from `TabSeparatedRaw` to `RowBinary` is worth ~20% on its own.

The chunk header is the other half of the protocol.  With `send_chunk_header` on, ClickHouse writes the row count before each chunk, so the process reads exactly that many rows, processes them, and flushes once.  Without it, a UDF that buffers output has no way of knowing when a block ends.  During the beta we debugged a UDF that flushed every 128 rows and therefore hung on every block whose size wasn't a multiple of 128 (ie - the last block of nearly every query) until the read timeout fired.  If your UDF doesn't flush per row, turn this on.

The model-to-encoding mapping (`gpt-4o` → `o200k_base`, `gpt-4` → `cl100k_base`, and so on) lives in a `models.json` next to the binary, so when a new model comes out we edit a text file and upload a new version instead of recompiling.  One detail that cost us a review cycle: the data files are deployed next to the binary, but the process does not start in that directory (the bundle lives under `/scripts`, the working directory is `/`), so the binary resolves `models.json` relative to its own path rather than to the working directory, and exits with an error if the file isn't there instead of quietly carrying on without it.  Models we don't recognize fall back to `o200k_base`.  That is an approximation for non-OpenAI tokenizers, but it's good enough for cost attribution, and the provider's own `usage` takes precedence whenever it's present (more on that below).

Building both architectures from a laptop is two `cargo` commands with the musl targets:

```bash
cargo build --release --target x86_64-unknown-linux-musl
cargo build --release --target aarch64-unknown-linux-musl
# -> count_tokens.zip: amd64/main, amd64/models.json, arm64/main, arm64/models.json
```

The binaries are ~7MB each and the zip is 6.6MB.

### Deploying it

The deployment surface is the same upload screen as the beta, with a few new fields:

| **Field** | **Value** |
| --- | --- |
| Name | `count_tokens` |
| Type | `executable_pool` |
| Runtime type | `Native` |
| Format | `RowBinary` |
| Send chunk header | `true` |
| Deterministic | `true` |
| Memory limit | `512 MiB` |
| Pool size | `4` |
| Arguments | `model String`, `text String` |
| Return type | `UInt32` |

Two of these are new since the beta.  'Deterministic' tells ClickHouse that the function returns the same output for the same input, which is what the query cache needs to know before it will store a result.  During the beta, every Cloud UDF was treated as non-deterministic, so `use_query_cache = 1` on a query that called one failed with `QUERY_CACHE_USED_WITH_NONDETERMINISTIC_FUNCTIONS`.  With the flag set, the second run of this dashboard query comes back from the cache in 0 ms with zero UDF invocations:

```sql
SELECT feature, sum(count_tokens(model, system_prompt)) AS system_tokens
FROM llm_spans
WHERE toDate(ts) = '2026-10-01'    -- a literal on purpose: today() is itself non-deterministic
GROUP BY feature
SETTINGS use_query_cache = 1;
```

```text
┌─query_duration_ms─┬─QueryCacheHits─┬─QueryCacheMisses─┬─udf_invocations─┐
│               209 │              0 │                1 │              14 │   ← first run
│                 0 │              1 │                0 │               0 │   ← second run
└───────────────────┴────────────────┴──────────────────┴─────────────────┘
```

'Memory limit' caps the memory available to each sandbox process; the default is 4 GiB.  The limit applies to virtual address space rather than resident memory, which matters because some runtimes reserve far more address space than they touch.  Our Rust binary sits at 43 MiB virtual / 39 MiB resident per process, the Python version at 103 / 93 MiB, and the Go version reserves ~1.2 GiB of address space while using 29 MiB.  In other words, size the limit for the runtime, not the workload, and give Go plenty of headroom.

### Wiring it into ingest

We'll call `count_tokens` from a materialized view, so the tokenizer runs exactly once per span, at insert time:

```sql
CREATE MATERIALIZED VIEW llm_span_tokens_mv TO llm_span_tokens AS
SELECT
    ts, trace_id, span_id, service, feature, customer_id, model,
    count_tokens(model, system_prompt)     AS system_tokens,
    count_tokens(model, retrieved_context) AS context_tokens,
    count_tokens(model, user_prompt)       AS user_tokens,
    count_tokens(model, completion)        AS completion_tokens,
    provider_input_tokens,
    provider_output_tokens,
    sipHash64(system_prompt)               AS system_prompt_hash
FROM llm_spans;
```

Every `INSERT INTO llm_spans` fires this view, counts four components per span, and lands the result in `llm_span_tokens`.  Every query after that is an aggregation over integers.

For a sense of throughput, 100,000 synthetic spans (351 MiB of prompt text, 69M tokens) go through this view in 5.2 seconds on a 4 vCPU box with a pool of 4, ie - ~13M tokens/sec, or ~19k spans/sec.

### Pricing it

Token counts become dollars with a price per token.  LiteLLM maintains a public price list as a JSON file, and since fetching a file is a job for `url()` rather than a UDF, we'll wrap the fetch in a refreshable materialized view that re-pulls it daily and feeds a dictionary:

```sql
CREATE MATERIALIZED VIEW model_prices_mv
REFRESH EVERY 1 DAY
TO model_prices
AS
SELECT
    kv.1                                                   AS model,
    JSONExtractString(kv.2, 'litellm_provider')            AS provider,
    JSONExtractFloat(kv.2, 'input_cost_per_token')         AS input_cost_per_token,
    JSONExtractFloat(kv.2, 'output_cost_per_token')        AS output_cost_per_token,
    JSONExtractFloat(kv.2, 'cache_read_input_token_cost')  AS cache_read_input_token_cost,
    now()                                                  AS updated_at
FROM
(
    SELECT arrayJoin(JSONExtractKeysAndValuesRaw(json)) AS kv
    FROM url('https://raw.githubusercontent.com/BerriAI/litellm/main/model_prices_and_context_window.json',
             JSONAsString, 'json String')
)
WHERE JSONHas(kv.2, 'input_cost_per_token');
```

That gives us 3,683 priced models, refreshed once a day and looked up with `dictGet`.  The cost query uses the provider's `usage` where it exists and our count where it doesn't:

```sql
SELECT
    toDate(ts) AS day,
    feature,
    round(sum(coalesce(provider_input_tokens, system_tokens + context_tokens + user_tokens)
            * dictGet('model_prices_dict', 'input_cost_per_token', model)
          + coalesce(provider_output_tokens, completion_tokens)
            * dictGet('model_prices_dict', 'output_cost_per_token', model)), 2)  AS est_cost_usd,
    countIf(provider_input_tokens IS NULL)                         AS spans_filled_by_udf,
    count()                                                        AS spans
FROM llm_span_tokens
GROUP BY day, feature
ORDER BY day DESC, est_cost_usd DESC;
```

```text
┌────────day─┬─feature───────┬─est_cost_usd─┬─spans_filled_by_udf─┬─spans─┐
│ 2026-09-30 │ sql_assistant │         3.25 │                 558 │  1781 │
│ 2026-09-30 │ support_bot   │         3.24 │                 539 │  1759 │
│ 2026-09-30 │ docs_search   │         3.06 │                 535 │  1796 │
│ 2026-09-30 │ summarizer    │         2.93 │                 527 │  1818 │
└────────────┴───────────────┴──────────────┴─────────────────────┴───────┘
```

Where the provider did report usage, we can check our own work against it.  The difference between `provider_input_tokens` and our three component counts is the chat-template overhead (role markers and message framing), which for a given model should be a stable dozen or so tokens.  If it drifts, either the provider changed its template or our `models.json` is wrong for that model, and either way it's a one-line `quantile` query to find out.

### What the components tell you

The system prompt is static text sent on every call, and providers now bill cached prefix tokens at 50-90% off list depending on the provider (that's the `cache_read_input_token_cost` column above).  So 'how much of my input spend is the system prompt?' is the same question as 'how much would prompt caching save me?':

```sql
SELECT
    feature,
    sum(system_tokens)                                              AS sys_tokens,
    sum(system_tokens + context_tokens + user_tokens)               AS input_tokens,
    round(sys_tokens / input_tokens * 100, 1)                       AS system_pct,
    round(sum(system_tokens
              * (dictGet('model_prices_dict', 'input_cost_per_token', model)
                 - dictGet('model_prices_dict', 'cache_read_input_token_cost', model))), 2)
                                                                    AS usd_saved_if_cached
FROM llm_span_tokens
WHERE ts >= now() - INTERVAL 7 DAY
GROUP BY feature
ORDER BY usd_saved_if_cached DESC;
```

```text
┌─feature───────┬─sys_tokens─┬─input_tokens─┬─system_pct─┬─usd_saved_if_cached─┐
│ support_bot   │    3483276 │      8461730 │       41.2 │                4.04 │
│ sql_assistant │    3237735 │      8382894 │       38.6 │                3.78 │
│ docs_search   │    2213208 │      7287850 │       30.4 │                2.61 │
│ summarizer    │    1552014 │      6999309 │       22.2 │                1.81 │
└───────────────┴────────────┴──────────────┴────────────┴─────────────────────┘
```

The dollar figures are small because the dataset is small (100k spans over two weeks); multiply by your own volume.  The point is that this query can't be written from `usage` totals at all.  It needs the components, and the components come from the tokenizer.

## Judging a sample, over the network

Cost is one half of the accounting; whether the completions were any good is the other, and the usual approach is to have a second model grade a sample.  That is a network call to an LLM API from inside the database, which is what network-enabled UDFs are for.

`judge_response` is a Python UDF (~120 lines) that posts the prompt and completion to Claude with a tool-use schema whose `verdict` field is an enum of `pass`, `partial`, and `fail`, and whose `score` is an integer from 1 to 5.  The model is required to call the tool, so the response is always parseable and the verdict is always one of the three values:

```python
# abridged - full file in the repo
JUDGE_TOOL = {
    "name": "report_verdict",
    "description": "Grade how well the completion answers the prompt.",
    "input_schema": {
        "type": "object",
        "properties": {
            "score":   {"type": "integer", "minimum": 1, "maximum": 5},
            "verdict": {"type": "string", "enum": ["pass", "partial", "fail"]},
            "reason":  {"type": "string", "maxLength": 200},
        },
        "required": ["score", "verdict", "reason"],
    },
}

def main() -> None:
    for line in sys.stdin:                       # JSONEachRow in ...
        if not line.strip():
            continue
        row = json.loads(line)
        score, verdict, reason = judge(row["prompt"], row["completion"])
        sys.stdout.write(json.dumps({"result": [score, verdict, reason]}) + "\n")   # ... JSONEachRow out
        sys.stdout.flush()
```

This one uses `JSONEachRow` rather than `RowBinary`, since throughput is beside the point when every row is an HTTPS round trip and JSON makes the tuple return type easy to emit.  Each pool process keeps a `requests.Session` open for its lifetime, caches results per `(prompt, completion)` so re-judging is free, and retries on 429/529 with backoff.  It also fails soft - a bad API call returns `(0, 'error', reason)` rather than killing the query - because it runs unattended.

On the API key: there is no secrets manager for UDFs yet (see below), so the key ships in a `config.json` inside the zip rather than appearing anywhere in SQL.  The sandbox has no cloud identity of its own (no instance role, no metadata endpoint, no inherited environment), so the only credentials a UDF has are the ones you give it.

| **Field** | **Value** |
| --- | --- |
| Name | `judge_response` |
| Type | `executable_pool` |
| Runtime type | `python3.11` |
| Format | `JSONEachRow` |
| Network access | enabled |
| Deterministic | `false` |
| Max command exec time (s) | `30` |
| Pool size | `4` |
| Arguments | `prompt String`, `completion String` |
| Return type | `Tuple(UInt8, String, String)` |

The eval loop itself is a refreshable materialized view.  Every 10 minutes it takes a deterministic 2% sample of the last 10 minutes of spans, judges them, and appends the results:

```sql
CREATE MATERIALIZED VIEW llm_evals_mv
REFRESH EVERY 10 MINUTE
APPEND TO llm_evals
AS
WITH judge_response(
        concat(system_prompt, '\n\n', retrieved_context, '\n\nUser: ', user_prompt),
        completion
     ) AS j
SELECT
    ts, trace_id, span_id, feature, model,
    j.1   AS score,
    j.2   AS verdict,
    j.3   AS reason,
    now() AS judged_at
FROM llm_spans
WHERE ts >= now() - INTERVAL 10 MINUTE
  AND cityHash64(trace_id) % 100 < 2;
```

There is no scheduler or eval service in this picture, just a view with a refresh interval.  The same `GROUP BY feature, model` you'd write for cost gives you fail rates by feature and model, and because `llm_evals` and `llm_span_tokens` share `span_id`, 'which expensive prompts are also failing' is a join.

## What it costs to run

The biggest gap in the beta was observability.  A UDF runs in a separate process, so `system.query_log` showed the query's own CPU and memory and nothing about the children, and when a customer asked whether their UDF or their query was slow, neither of us could answer from the system tables.

ClickHouse 26.6 added eight `ProfileEvents` for executable UDFs, and they now appear in `system.query_log`, `system.events`, and `system.metric_log` on every Cloud service:

| **ProfileEvent** | **What it measures** |
| --- | --- |
| `ExecutableUserDefinedFunctionInvocations` | Number of UDF invocations (one per chunk) |
| `ExecutableUserDefinedFunctionElapsedMicroseconds` | Wall-clock time spent in UDF calls |
| `ExecutableUserDefinedFunctionPoolWaitMicroseconds` | Time spent waiting for a free pool process |
| `ExecutableUserDefinedFunctionUserTimeMicroseconds` | User-mode CPU consumed by the child processes |
| `ExecutableUserDefinedFunctionSystemTimeMicroseconds` | Kernel-mode CPU consumed by the child processes |
| `ExecutableUserDefinedFunctionPeakMemoryByteSeconds` | Per-process peak memory integrated over wall time |
| `ExecutableUserDefinedFunctionInputBytes` | Bytes written to the children's stdin |
| `ExecutableUserDefinedFunctionOutputBytes` | Bytes read from the children's stdout |

Two asynchronous metrics, `ExecutableUserDefinedFunctionProcesses` and `ExecutableUserDefinedFunctionMemoryResidentBytes`, report how many UDF processes are alive on the server right now and how much resident memory they hold (summed per process, so an upper bound).

With these in place, the question of which language to write a UDF in becomes a `query_log` query.  We wrote `count_tokens` three times - Rust on the Native runtime, Python with `tiktoken`, and Go with a pure-Go tokenizer - and ran the materialized view's workload (100k spans, 4 counts each, 351 MiB of text) through each:

```sql
SELECT
    extract(query, 'AS (\\w+)_tokens')                                            AS impl,
    query_duration_ms,
    ProfileEvents['ExecutableUserDefinedFunctionInvocations']                     AS invocations,
    round(ProfileEvents['ExecutableUserDefinedFunctionElapsedMicroseconds'] / 1e6, 2) AS udf_wall_s,
    round((ProfileEvents['ExecutableUserDefinedFunctionUserTimeMicroseconds']
         + ProfileEvents['ExecutableUserDefinedFunctionSystemTimeMicroseconds']) / 1e6, 2) AS udf_cpu_s,
    formatReadableSize(ProfileEvents['ExecutableUserDefinedFunctionInputBytes'])  AS udf_in
FROM system.query_log
WHERE type = 'QueryFinish' AND ProfileEvents['ExecutableUserDefinedFunctionInvocations'] > 0
ORDER BY event_time_microseconds;
```

```text
┌─impl─┬─query_duration_ms─┬─invocations─┬─udf_wall_s─┬─udf_cpu_s─┬─udf_in─────┐
│ rs   │              5161 │         144 │       7.05 │      6.94 │ 355.09 MiB │
│ py   │              7207 │         144 │      10.05 │      9.94 │ 355.09 MiB │
│ go   │             15028 │         144 │      20.97 │     26.14 │ 355.09 MiB │
└──────┴───────────────────┴─────────────┴────────────┴───────────┴────────────┘
```

Rust is 1.4x faster than Python here and 2.9x faster than Go, which is not the order we expected going in.  Python is close because `tiktoken`'s core is Rust; the 1.4x is the interpreter loop and the pipe handling.  Go is slow because the pure-Go tokenizer library is slow, and the Native runtime does nothing about a slow library.  Simply put, the runtime removes the interpreter and the dependency install and lets you ship the library you already have, but the library still has to be fast.  (For CPU-bound Python with no native core underneath it, the picture is different: a design-partner customer measured ~25x moving a string-matching UDF from Python to Go.)

The counts, for what it's worth, were identical across all three implementations, and matched `tiktoken` itself on 1,200 spot-checked values.

## Terraform

Everything above was set up in the console.  For anything headed to production you'll probably want it in code, and the Terraform provider (3.24.0+) now has two resources for that: `clickhouse_udf` publishes a new version whenever the zip's hash changes and waits for the build, and `clickhouse_udf_attachment` binds one version to one service.

```hcl
resource "clickhouse_udf" "count_tokens" {
  function_name = "count_tokens"
  runtime       = "native"
  type          = "executable_pool"
  format        = "RowBinary"
  return_type   = "UInt32"
  arguments     = [{ name = "model", type = "String" }, { name = "text", type = "String" }]

  pool_size                  = 4
  send_chunk_header          = true
  max_command_execution_time = 10

  source_archive_path = "${path.module}/../udf/count_tokens_rs/count_tokens.zip"
  source_archive_hash = filebase64sha256("${path.module}/../udf/count_tokens_rs/count_tokens.zip")
}

# Dev follows every successful build.
resource "clickhouse_udf_attachment" "dev" {
  function_name = clickhouse_udf.count_tokens.function_name
  service_id    = var.dev_service_id
  version       = clickhouse_udf.count_tokens.version
}

# Prod stays where you pinned it.
resource "clickhouse_udf_attachment" "prod" {
  function_name = clickhouse_udf.count_tokens.function_name
  service_id    = var.prod_service_id
  version       = var.count_tokens_prod_version
}
```

This mirrors how versions work in the console.  Versions are immutable, a new zip is a new version, and versions are attached per service, so you can run v7 on dev while prod stays on v6 and roll back a single service without touching the others.  A service holds one version of a function at a time.  For `executable_pool` UDFs the long-lived pool processes keep serving the old version until the pool is refreshed, so the console has a 'Reload UDF' action next to each attached service that runs `SYSTEM RELOAD FUNCTION` for you.  Two of the newer settings, `deterministic` and the memory limit, aren't in the provider schema yet, so for the time being those are set in the console or via the API.

The same lifecycle is available in the [Cloud API](https://clickhouse.com/docs/products/cloud/api-reference/udf/udf-create): create an upload URL, push the zip, create the function or a new version, attach it to a service.

## What we learned in beta

Four months of beta support threads reduce to a short list.

Use `executable_pool`.  With plain `executable`, ClickHouse starts a fresh sandboxed process for every block of data; with `executable_pool`, a pool of long-lived processes is reused across blocks and queries, which is faster, keeps your model or vocabulary warm in memory, and holds up under load in a way that per-block process spawning does not.  We have yet to see a Cloud workload where `executable` was the right choice.

Fewer, bigger chunks.  Every invocation has a fixed setup cost on both sides of the pipe.  The same 5,000-row query took 165 ms as one chunk and 1,544 ms with `max_block_size = 1`, ie - 5,000 invocations.  If `ExecutableUserDefinedFunctionInvocations` is in the hundreds of thousands for a single query, raise `preferred_block_size_bytes` (we've used `100000000`) and check the counter again.

Pool size is per replica, and `max_threads` is the ceiling.  A query uses at most `max_threads` pool processes at once, so a pool of 64 on a 16-thread query is a pool of 16.  Start at 4, and raise it when `ExecutableUserDefinedFunctionPoolWaitMicroseconds` says so, bearing in mind that each process holds its own copy of whatever you load at startup.

Flush per chunk, not per N rows.  Turn on `send_chunk_header` and read exactly that many rows.  Covered above, but it accounted for more beta support threads than anything else.

Fail loudly.  A UDF that can't find a bundled file, can't parse a config, or gets a row it doesn't understand should write one line to stderr and exit non-zero.  ClickHouse surfaces the stderr in the query error, so the problem is visible in the first query rather than in a wrong number three dashboards later.  Our first `count_tokens` treated a missing `models.json` as "no rules" and tokenized every model as `o200k_base`; the counts looked plausible, and nobody would have noticed until a `gpt-4` bill didn't reconcile.

Know when a UDF is the wrong tool.  Every row crosses a process boundary through a pipe and is serialized on the way, and that cost can't be optimized away.  For trivial per-row work it dominates - a no-op UDF over billions of rows will be several times slower than the equivalent built-in in any language.  UDFs pay for themselves on logic SQL can't express (a tokenizer, a model, a parser, an API call), not on logic it can.

The first UDF on a service restarts it.  Attaching your first UDF adds a helper container to the service's pods, which means a rolling restart; the second UDF onward does not, and removing the last one restarts again.  Treat the first attach like a maintenance window.

## What we're building next

- Secrets - the number one ask: environment variables or secret references for UDFs, so API keys don't ship inside the zip.  We have a design that ties UDF inputs to named collections with proper access separation, and it's next on the list.
- Runtime config without a rebuild - pool size, timeouts, and memory limits are tied to a version today.  We're decoupling them so a `clickhouse_udf_attachment` can override them per service without publishing a new version.
- Network access for Native UDFs - today the Native runtime is compute-only and outbound network is Python-only.
- More runtimes - WebAssembly UDFs exist in open-source ClickHouse as an experimental feature and aren't in Cloud yet; we're looking at that, and at curated per-language runtimes, as the longer-term shape.

## Try it yourself

Executable UDFs are generally available today in every ClickHouse Cloud organization on AWS, GCP, and Azure, with nothing to enable.  Open 'User-defined functions' from your organization menu in the console, or start from the [docs](https://clickhouse.com/docs/products/cloud/features/sql-console-features/user-defined-functions), the [Cloud API reference](https://clickhouse.com/docs/products/cloud/api-reference/udf/udf-create), or the [Terraform resources](https://registry.terraform.io/providers/ClickHouse/clickhouse/latest/docs/resources/udf).

The full project is at [github.com/ClickHouse/llm-token-udf](https://github.com/ClickHouse/llm-token-udf):

```text
llm-token-udf/
├── udf/
│   ├── count_tokens_rs/   # the Native UDF (Rust): source, build script, zip layout
│   ├── count_tokens/      # the same UDF in Go
│   ├── count_tokens_py/   # the same UDF in Python
│   └── judge_response/    # the network UDF (Python, Anthropic tool-use)
├── sql/                   # schema, MVs, prices, evals, and every query in this post
├── terraform/             # clickhouse_udf + dev/prod attachments
└── local/                 # XML config for running the same UDFs against open-source ClickHouse
```

If you port a Python UDF to the Native runtime and measure the difference, or build something we haven't thought of, drop us a note!

### Get started today
