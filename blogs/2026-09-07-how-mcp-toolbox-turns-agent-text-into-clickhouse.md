---
title: "How MCP Toolbox turns agent text into ClickHouse vectors"
date: "2026-09-07T13:45:04.721Z"
author: "Pete Hampton"
category: "Product"
excerpt: "Google's MCP Toolbox for Databases embeds agent text into vectors on insert and search, then lets ClickHouse rank the results - no embedding service to build or maintain. Here's how to set it up, and what it looks like end to end."
---

# How MCP Toolbox turns agent text into ClickHouse vectors

If you've built an AI agent that needs semantic search, you've probably hit the same awkward gap everyone hits: your LLM speaks text, your database speaks SQL and vectors, and something in the middle has to do the translation. Usually that *something* ends up being bespoke application code or tools you write and maintain \- accept a query string, call an embedding API, format the vector, splice it into SQL, hope you escaped everything correctly.

[MCP Toolbox for Databases](https://github.com/googleapis/mcp-toolbox) by Google closes that gap natively, and it works with ClickHouse out of the box. You declare a Gemini embedding model in YAML, mark a tool parameter as `embeddedBy` that model, and Toolbox handles the entire `text → vector → search` pipeline transparently. The agent never sees a vector. It sends `"how do I configure TTL on a table?"` and gets back ranked rows.

In this post I'll cover what MCP Toolbox is, how to install and set it up, how to use its prebuilt ClickHouse tools, and then the main event: building an ingestion tool that embeds on insert and a search tool that embeds the query and ranks by cosine distance \- with no embedding service of your own to write or maintain. Then we'll load a synthetic corpus through it and look at what actually comes back.

> Want to try it out? Give this post to your coding agent and let it follow the steps and set everything up for you.

Everything below was run end to end against Toolbox **1.9.0** and a **ClickHouse Cloud 26.4.1** service, the stable releases at the time of writing.

## What is MCP Toolbox?

MCP Toolbox for Databases is Google's open-source (Apache 2.0) Model Context Protocol server, originally released as `genai-toolbox` before MCP existed and since renamed. It's a single Go binary that sits between AI agents and your databases, and it serves two distinct purposes:

1. **A ready-to-use MCP server.** Point it at databases such as ClickHouse and Postgres with a `--prebuilt` flag and any MCP client - Claude Code, Gemini CLI, Codex, your IDE - instantly gets generic tools like `execute_sql` and `list_tables`. Great for exploration and development.  
2. **A custom tools framework.** Define curated, parameterized SQL statements in YAML and expose *those* as tools instead of raw SQL access. This is a great pattern for production as the agent can only invoke the queries you wrote, passing typed parameters that the driver escapes on its way to the database.

Alongside ClickHouse it supports PostgreSQL, MySQL, SQL Server, Oracle, MongoDB, Redis, Valkey, Elasticsearch, Neo4j, Cassandra, Snowflake, Trino, CockroachDB, TiDB, and the Google Cloud fleet (AlloyDB, BigQuery, Cloud SQL, Spanner, Firestore). A single `tools.yaml` can define sources across several of them, so one MCP endpoint can expose tools for your ClickHouse analytics and a Postgres app database side by side. That isn't federation, though \- each tool binds to exactly one source, so an agent correlates the two by making two calls and joining the results in its own context, not in SQL.

Under the hood you also get connection pooling, optional authenticated tool invocation, and OpenTelemetry metrics and traces for free.

## Installation

Pick whichever fits your setup:


```shell
# Homebrew (macOS / Linux)
brew install mcp-toolbox

# Or grab the binary directly (see the releases page for versions/platforms)
export VERSION=1.9.0
curl -L -o toolbox https://storage.googleapis.com/mcp-toolbox-for-databases/v$VERSION/darwin/arm64/toolbox
chmod +x toolbox

# Or Docker
docker pull us-central1-docker.pkg.dev/database-toolbox/toolbox/toolbox:$VERSION

# Or zero-install via npx (convenient, but not the fastest startup)
npx @toolbox-sdk/server --config tools.yaml
```

Verify with `toolbox --version`. The server listens on `127.0.0.1:5000` by default \- loopback, not all interfaces, which is the right default for a process holding database credentials. Here is an example tools.yaml


```text
kind: source
name: my-clickhouse
type: clickhouse
host: ${CLICKHOUSE_HOST}
port: ${CLICKHOUSE_PORT}
database: ${CLICKHOUSE_DATABASE}
user: ${CLICKHOUSE_USER}
password: ${CLICKHOUSE_PASSWORD}
protocol: ${CLICKHOUSE_PROTOCOL}
secure: true

---
kind: tool
name: execute_sql
type: clickhouse-execute-sql
source: my-clickhouse
description: Execute a SQL query against ClickHouse and return the rows.

---
kind: tool
name: list_databases
type: clickhouse-list-databases
source: my-clickhouse
description: List all databases in ClickHouse.

---
kind: tool
name: list_tables
type: clickhouse-list-tables
source: my-clickhouse
description: List the tables in a ClickHouse database.

---
kind: embeddingModel
name: gemini-embedder
type: gemini
model: gemini-embedding-001
project: ${GOOGLE_CLOUD_PROJECT}
location: ${GOOGLE_CLOUD_LOCATION}
dimension: 768

---
kind: tool
name: insert_doc
type: clickhouse-sql
source: my-clickhouse
description: Indexes a new document and its vector embedding.
statement: |
  INSERT INTO vectors.documents (content, embedding) VALUES (?, ?)
parameters:
  - name: content
    type: string
    description: The text content to store.
  - name: text_to_embed
    type: string
    description: Hidden copy of content, embedded as a vector.
    valueFromParam: content
    embeddedBy: gemini-embedder

---
kind: tool
name: search_docs
type: clickhouse-sql
source: my-clickhouse
description: Finds the most semantically similar documents to a query.
statement: |
  SELECT content, cosineDistance(embedding, ?) AS distance
  FROM vectors.documents
  ORDER BY distance ASC
  LIMIT 5
parameters:
  - name: query
    type: string
    description: The natural-language search query.
    embeddedBy: gemini-embedder

---
kind: toolset
name: semantic_search
tools:
  - insert_doc
  - search_docs

---
kind: toolset
name: clickhouse_explore
tools:
  - execute_sql
  - list_databases
  - list_tables
```

An FYI before you write any YAML: **1.9 prefers a flat config format**. Each resource is its own YAML document with `kind`, `name`, and `type` keys, separated by `---`. Older examples on the internet use a nested format (`sources:` → `my-clickhouse:` → …) where `kind` carries the type. That older shape still parses and runs fine in 1.9  (I kept a nested config around and it executed happily) so nothing is broken if you have one. `toolbox migrate` converts it when you want the new shape, and all the examples below use it.

## Quick start: prebuilt ClickHouse tools

You can use Toolbox as a generic ClickHouse MCP server, similar to connecting it to [mcp-clickhouse](https://github.com/clickhouse/mcp-clickhouse) or the [ClickHouse Cloud MCP server](https://clickhouse.com/docs/products/cloud/features/ai-ml/mcp/remote-mcp). Add this to your MCP client config (e.g. `.mcp.json` for Claude Code or `claude_desktop_config.json` for Claude Desktop):


```json
{
  "mcpServers": {
    "clickhouse": {
      "command": "npx",
      "args": ["-y", "@toolbox-sdk/server", "--prebuilt=clickhouse", "--stdio"],
      "env": {
        "CLICKHOUSE_HOST": "your-instance.clickhouse.cloud",
        "CLICKHOUSE_PORT": "8443",
        "CLICKHOUSE_USER": "default",
        "CLICKHOUSE_PASSWORD": "…",
        "CLICKHOUSE_DATABASE": "default",
        "CLICKHOUSE_PROTOCOL": "https"
      }
    }
  }
}
```

All six of those variables are required, and the prebuilt config fails fast and tells you exactly which one is missing, which is nicer than a connection timeout. Note that `CLICKHOUSE_HOST` is a bare hostname: scheme and port live in `CLICKHOUSE_PROTOCOL` and `CLICKHOUSE_PORT`, so `https://host:8443` in the host field won't work.

That gives your agent three tools immediately: `execute_sql`, `list_databases`, and `list_tables`. You can now ask "what's the schema of my events table?" and the agent figures it out.

Toolbox is refreshingly blunt about what this mode is for, logging a warning on every start:

> These prebuilt configs are intended for 'build-time' use cases, where agents are helping trusted developers build things. They are not secure enough for 'run time' use cases, where the agent will be talking to potentially untrusted developers.

Which is the cue for the curated tools below.

## Native text → vector → search

ClickHouse also has strong [vector search](https://clickhouse.com/blog/vector-search-clickhouse-p1) support, and includes distance functions such as cosine and support for HNSW indexes. Toolbox's custom tools framework has first-class *embedding models* as a resource type. When a tool parameter carries an `embeddedBy: <model-name>` hint, Toolbox intercepts the raw text at invocation time, batches it to the embedding model's API, and binds the resulting vector to the statement's `?` placeholder.

For ClickHouse specifically, the vector is handed to the `clickhouse-go` driver as a raw `[]float32` rather than a string you assembled yourself:


```go
// internal/embeddingmodels/embeddingmodels.go
// FormatVectorForClickHouse returns the raw []float32 slice, which the
// clickhouse-go driver binds natively to Array(Float32) parameters.
func FormatVectorForClickHouse(vectorFloats []float32) any {
    if len(vectorFloats) == 0 {
        return []float32{}
    }
    return vectorFloats
}
```

That means your SQL can use ClickHouse's vector functions directly against a parameter placeholder. There are exactly two of these formatters in the codebase \- one for pgvector, one for ClickHouse.

Don’t be confused by the `?`,  it's not the same as a "prepared statement". I pulled the executed statement back out of `system.query_log`, and the vector arrives **inlined as a literal**:


```text
query_head: SELECT content, cosineDistance(embedding, [-0.002279004, 0.012003845, 0.0052243723, …
query_len:  10626
param_1 present in Settings: 0
```

There is no server-side parameter binding here, no `param_*` settings, just a ten-kilobyte SQL string that `clickhouse-go` interpolated client-side. I tested some basic injection to see how this affects security, by putting `x') AS a FROM system.one WHERE 1=1 UNION ALL SELECT version(--` into a `string` parameter. It comes back as that exact text in a result column, not as executed SQL. So the guarantee is *the driver serialises typed values for you and escapes them*, which removes the injection class you'd create by hand-building literals. It just isn't a prepared statement.

It has its downsides, too. Every embedded query writes its full text, vector included, into `query_log`. A busy search tool will inflate that table considerably, and vectors are the least compressible thing you could put there.

### Step 1: The ClickHouse table

We need a table to hold documents and their embeddings. A few deliberate choices here:


```sql
CREATE DATABASE vectors;

CREATE TABLE vectors.documents
(
    id        UUID DEFAULT generateUUIDv4(),
    content   String,
    embedding Array(Float32),
    INDEX idx_embedding embedding TYPE vector_similarity('hnsw', 'cosineDistance', 768)
)
ENGINE = MergeTree
ORDER BY (id);
```

Notes on the schema:

- **`Array(Float32)`** is the canonical embedding column type in ClickHouse, and it's what Toolbox binds to.  
- **The `vector_similarity` skipping index** gives you approximate nearest neighbor (HNSW) search. The third argument (`768`) is the vector dimension and **must match the `dimension` you configure on the embedding model**. On 26.4 both `allow_experimental_vector_similarity_index` and `enable_vector_similarity_index` were already `1`, so no setting change was needed; on older releases you may need to enable them yourself. For small corpora (up to a few million rows) you can skip the index entirely - brute-force `cosineDistance` over a columnar `Array(Float32)` is fast, and you can always add the index later with `ALTER TABLE ... ADD INDEX`.  
- **Pick cosine and stick to it.** `gemini-embedding-001` output at 768 dimensions is **not** unit-normalized - across my corpus the L2 norms ran 0.5788 to 0.5928, averaging 0.5862. `cosineDistance` normalizes internally so it doesn't care, but `L2Distance` will rank differently and skew with magnitude, and because the index above declares `'cosineDistance'`, an `L2Distance` query gets no index help at all. Choose one metric, declare it in the index, and use it consistently.  
- **`ORDER BY` won't accelerate the vector search itself** - ANN search goes through the skipping index. Choose your `ORDER BY` based on the metadata filters you'll combine with vector search (tenant, category, date). It's effectively immutable, `ALTER TABLE … MODIFY ORDER BY` can only append columns, not reorder or remove them, so decide before you load data. If your search tool will always filter by, say, `category`, put that first: `ORDER BY (category, id)`.

On ClickHouse Cloud you get the shared-storage engine substituted automatically, with the index carried through intact:


```sql
CREATE TABLE vectors.documents
(
    `id` UUID DEFAULT generateUUIDv4(),
    `content` String,
    `embedding` Array(Float32),
    INDEX idx_embedding embedding TYPE vector_similarity('hnsw', 'cosineDistance', 768) GRANULARITY 100000000
)
ENGINE = SharedMergeTree('/clickhouse/tables/{uuid}/{shard}', '{replica}')
ORDER BY id
SETTINGS index_granularity = 8192
```

### Step 2: The Toolbox configuration

Everything lives in one `tools.yaml`. Three kinds of resources: a source, an embedding model, and the tools.

**The source**  
ClickHouse Cloud connects over HTTPS on 8443; a local instance uses HTTP on 8123:


```text
kind: source
name: my-clickhouse
type: clickhouse
host: ${CLICKHOUSE_HOST}
port: ${CLICKHOUSE_PORT}
database: ${CLICKHOUSE_DATABASE}
user: ${CLICKHOUSE_USER}
password: ${CLICKHOUSE_PASSWORD}
protocol: ${CLICKHOUSE_PROTOCOL}
secure: true
```

**The embedding model**  
As of 1.9, `gemini` is the *only* supported provider - there's a single `gemini` package under `internal/embeddingmodels`, and `openai`, `ollama`, `bedrock` and friends are all rejected at config parse time. If you need a different provider today, you're embedding outside Toolbox.

There are two ways to authenticate, and the choice is implied by which fields you set. An API key from Google AI Studio:


```text
kind: embeddingModel
name: gemini-embedder
type: gemini
model: gemini-embedding-001
apiKey: ${GOOGLE_API_KEY}
dimension: 768
```

Or `project` and `location` instead of `apiKey`, which switches it to the Vertex AI backend and picks up your Application Default Credentials:


```text
kind: embeddingModel
name: gemini-embedder
type: gemini
model: gemini-embedding-001
project: ${GOOGLE_CLOUD_PROJECT}
location: ${GOOGLE_CLOUD_LOCATION}   # e.g. us-central1
dimension: 768
```

With `gcloud auth application-default login` already done, that second form works with no further setup, and the server confirms which path it took on startup:


```text
INFO "Using Vertex AI backend for Gemini embedding" "my-project" "us-central1"
INFO "Initialized 1 embeddingModels: gemini-embedder"
```

The field list is short and strict: `model`, `dimension`, and then either `apiKey` or `project` \+ `location`. Plausible-looking extras (`useVertex`, `taskType`, `outputDimensionality`) are all rejected as unknown fields. You can see the reason for rejecting these fields in the source:


```go
// internal/embeddingmodels/gemini/gemini.go
embedConfig := &genai.EmbedContentConfig{
    TaskType: "SEMANTIC_SIMILARITY",
}

if m.Dimension > 0 {
    embedConfig.OutputDimensionality = genai.Ptr(m.Dimension)
}
```

First, `dimension` maps straight onto `OutputDimensionality`, which tells you the field *instructs* the model rather than describing it. Set `dimension: 512` against the same `gemini-embedding-001` and you get a 512-element vector back. So there's no model output dimension you need to look up; the only thing `dimension` has to agree with is the width declared in your column's `vector_similarity` index. Because Toolbox has no idea what that is, a disagreement surfaces as a ClickHouse error on insert or search, not as a config parse failure. Get it right up front.

Second, and more consequentially for a semantic search post: **`taskType` is hardcoded to `SEMANTIC_SIMILARITY`**, which is why the config field is rejected. Google's own guidance for retrieval is asymmetric - embed your documents as `RETRIEVAL_DOCUMENT` and your queries as `RETRIEVAL_QUERY`, so that the two sides land in the space the model was tuned for. Toolbox gives you neither, and no override. `SEMANTIC_SIMILARITY` optimises for "are these two texts alike?", which is a subtly different question from "does this document answer this query?", and it's the same task type on both the ingest and search paths.

In practice it still works well, as the results below show. But it's a plausible contributor to the compressed distance spread you'll see there - everything landing between 0.15 and 0.30 rather than spreading out - and if you need to squeeze retrieval quality, this is the knob you'd reach for first and the one you can't currently turn. Embedding outside Toolbox is the only way to set it today.

**The ingestion tool**  
Here's the clever bit. On insert you need the same text twice - once to store as `String`, once to embed into the vector column. Asking an LLM to repeat an identical string across two parameters is wasteful and error-prone, so Toolbox has `valueFromParam`: a hidden parameter that mirrors another parameter's value. It never appears in the tool manifest - the agent doesn't know it exists:


```text
kind: tool
name: insert_doc
type: clickhouse-sql
source: my-clickhouse
description: Indexes a new document and its vector embedding.
statement: |
  INSERT INTO vectors.documents (content, embedding) VALUES (?, ?)
parameters:
  - name: content
    type: string
    description: The text content to store.
  - name: text_to_embed
    type: string
    description: Hidden copy of content, embedded as a vector.
    valueFromParam: content
    embeddedBy: gemini-embedder
```

Asking the server for its tool manifest over MCP returns a single property for `insert_doc`:


```text
- execute_sql    | params: sql
- insert_doc     | params: content
- list_databases | params: none
- list_tables    | params: database
- search_docs    | params: query
```

**The search tool.**   
The agent supplies plain text; Toolbox embeds it and binds the vector to the `?`:


```text
kind: tool
name: search_docs
type: clickhouse-sql
source: my-clickhouse
description: Finds the most semantically similar documents to a query.
statement: |
  SELECT content, cosineDistance(embedding, ?) AS distance
  FROM vectors.documents
  ORDER BY distance ASC
  LIMIT 5
parameters:
  - name: query
    type: string
    description: The natural-language search query.
    embeddedBy: gemini-embedder
```

Optionally, group them into a toolset so clients can load just these two:


```text
kind: toolset
name: semantic_search
tools:
  - insert_doc
  - search_docs
```

Two constraints to remember. Only `string`\-typed parameters can declare `embeddedBy`, which the config parser catches before the server will even start:


```text
ERROR "unable to parse config file at \"tools.yaml\": document 3: error unmarshaling
tool \"dim_probe\": … parameter type \"integer\" cannot specify 'embeddedBy'"
```

The referenced embedding model must also be defined in the same configuration - but that one is *not* checked at parse time. A tool pointing at a model that doesn't exist loads happily and fails on first use, which is a much worse place to find out:


```text
ERROR "error embedding parameters: embedding model does not exist: does-not-exist"
```

### Step 3: Run it


```shell
./toolbox --config tools.yaml   # listens on 127.0.0.1:5000
```

I usually go straight to the bundled UI at `http://127.0.0.1:5000/ui` (add `--ui` when you start the server) to eyeball what loaded. But before wiring up a client at all, you can exercise a tool straight from the shell:


```shell
toolbox invoke search_docs '{"query":"making queries faster"}' \
  --config tools.yaml --log-level ERROR
```

The `--log-level ERROR` matters if you're piping into `jq`: Toolbox writes its startup log lines to stdout alongside the JSON result, so a default-level invocation produces output that isn't valid JSON. This one-liner is the fastest way to prove your embedding credentials work before you start debugging a client integration.

## Loading a corpus

A two-row demo doesn't tell you much about whether semantic search is working, so we can load something with enough topical spread to be falsifiable: 57 short documents across five clusters - ClickHouse internals, operations and Kubernetes, general programming, cooking, and hillwalking. Retrieval that's actually semantic should cross those cluster boundaries when the wording demands it and stay inside them when it doesn't.

Ingestion goes through the `insert_doc` tool itself, so Toolbox does all the embedding. Note that **the `/api/tool/<name>/invoke` REST endpoints are off by default in 1.9**, and hitting one without the flag returns `410 Gone` with an error:


```json
{"status":"Gone","error":"/api native endpoints are disabled by default. Please use the standard /mcp JSON-RPC endpoint"}
```

Start the server with `--enable-api` and the same request returns `200` with correctly ranked results, so the REST route is available if you want the simpler client. I went with MCP JSON-RPC instead, for two reasons: it needs no extra flag, and it's the transport your agents will use anyway, so the seeding path exercises the same code as production traffic.

The whole client is about twenty lines:


```py
def invoke(url: str, tool: str, arguments: dict) -> dict:
    """Call a tool over Toolbox's MCP JSON-RPC endpoint."""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {"name": tool, "arguments": arguments},
    }
    request = urllib.request.Request(
        f"{url}/mcp",
        data=json.dumps(payload).encode(),
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        },
    )
    with urllib.request.urlopen(request) as response:
        body = json.load(response)
    if "error" in body:
        raise RuntimeError(body["error"]["message"])
    return body["result"]
```

The `Accept: application/json, text/event-stream` header is what the streamable-HTTP MCP transport specifies. Toolbox 1.9 happens to answer without it too, but send it anyway \- it costs nothing and it's what a spec-compliant client does.

Then fan the corpus out across a small thread pool:


```py
with ThreadPoolExecutor(max_workers=8) as pool:
    failures = [failure for failure in pool.map(insert, documents) if failure]
```

```text
$ python3 seed_documents.py --url http://127.0.0.1:5000
inserted 57/57 in 4.1s
```

Four seconds for 57 documents, at concurrency 8, with an embedding round trip to Vertex AI inside every single one. Confirming what landed:


```sql
SELECT count() AS docs, any(length(embedding)) AS dims
FROM vectors.documents
```

```text
   ┌─docs─┬─dims─┐
1. │   57 │  768 │
   └──────┴──────┘
```

And what it costs to store, which is more interesting than it sounds. Be careful which columns you ask for, though: `data_uncompressed_bytes` covers column data only, while `bytes_on_disk` includes the secondary indices, so comparing those two directly tells you nothing. Break the index out separately:


```sql
SELECT sum(rows) AS docs,
       formatReadableSize(sum(data_uncompressed_bytes))              AS col_uncompressed,
       formatReadableSize(sum(data_compressed_bytes))                AS col_compressed,
       formatReadableSize(sum(secondary_indices_uncompressed_bytes)) AS idx_uncompressed,
       formatReadableSize(sum(secondary_indices_compressed_bytes))   AS idx_compressed,
       formatReadableSize(sum(bytes_on_disk))                        AS on_disk
FROM system.parts
WHERE database = 'vectors' AND table = 'documents' AND active
```

```text
   ┌─docs─┬─col_uncompressed─┬─col_compressed─┬─idx_uncompressed─┬─idx_compressed─┬─on_disk────┐
1. │   57 │ 178.36 KiB       │ 162.34 KiB     │ 100.77 KiB       │ 69.05 KiB      │ 231.85 KiB │
   └──────┴──────────────────┴────────────────┴──────────────────┴────────────────┴────────────┘
```

Embeddings really are close to incompressible - 178.36 KiB down to 162.34 KiB is a compression ratio of **1.1x**, where log and metric columns often manage 10x or more, because high-entropy floats give the codecs nothing to work with. (That figure covers all three columns, but `embedding` is most of it; `content` is a few KiB of the total.) And the HNSW index is **29.8% of the part** at this scale, 69 KiB of the 232 KiB total, buying you nothing over a brute-force scan of 57 rows. So if you’re asking "should I add the index?" for a small corpus: not yet.

## Searching it

Now the part that either works or doesn't. Four queries, none of which share meaningful keywords with the documents they should retrieve, top three hits each with cosine distance:

**"making queries faster"**


```text
0.1653  Distributed tables fan a query out to shards and merge the partial results…
0.1708  Dictionaries hold reference data in memory so joins become key lookups…
0.1715  Reading fewer columns is the single biggest lever on scan performance…
```

**"why did my container get killed"**


```text
0.1833  The OOMKilled reason on a terminated container means it exceeded its memory limit…
0.2313  Liveness probes restart a container; readiness probes only remove it from…
0.2345  A pod stuck in CrashLoopBackOff is usually failing its own startup…
```

**"staying safe in bad weather on a hill"**


```text
0.1565  Pitching a tent on a slight rise keeps you dry when overnight rain pools…
0.1667  Mountain weather can turn within an hour, so carry a shell even on a clear morning.
0.2069  Navigating with a map and compass still works when the phone battery dies…
```

The second one is my favourite: "why did my container get killed" retrieves the OOMKilled note first, and the words *killed* and *container* aside, the query shares nothing with it - no "memory", no "limit". All three hits stay inside the twelve-document operations cluster, and none of the other 45 intrude.

And then the one that's less impressive:

**"what should I make for dinner"**


```text
0.2853  Sourdough starter needs feeding with equal parts flour and water roughly…
0.2943  Baking is closer to chemistry than cooking, so weigh your flour rather than…
0.3030  Distributed traces show where a request spent its time; metrics tell you…
```

The top two are in the right cluster, but a distributed tracing note has crashed the dinner party at rank three. The whole result set sits between 0.28 and 0.30, a much flatter and more distant spread than the 0.16-0.23 of the good queries. My corpus simply contains no document that answers "what should I make for dinner" - it has cooking *technique*, not recipes - and a pure top-k search always returns k rows whether or not any of them deserve to be there. In production you'd apply a distance threshold (`WHERE distance < 0.25`, tuned against your own data) so the tool can return nothing rather than return noise. An agent handed three irrelevant rows will usually try to use them.

## Using it: MCP clients and application SDKs

### From an MCP client (Claude Code, Gemini CLI, …)

Point your client at the running server over HTTP:


```json
{
  "mcpServers": {
    "clickhouse-semantic-search": {
      "type": "http",
      "url": "http://127.0.0.1:5000/mcp/semantic_search"
    }
  }
}
```

`http://127.0.0.1:5000/mcp` exposes every tool in the file; appending a toolset name scopes it to that toolset.

If you'd rather not manage a long-running server, let the client own the process over stdio. This form also solves credential loading, since MCP clients don't source your shell profile:


```json
{
  "mcpServers": {
    "clickhouse-toolbox": {
      "command": "sh",
      "args": [
        "-c",
        "set -a; . \"$HOME/.config/clickhouse.env\"; set +a; exec toolbox --config /path/to/tools.yaml --stdio"
      ]
    }
  }
}
```

One gotcha that cost me more time than it should have, and whose real cause is not the obvious one. I added the embedding model and vector tools to `tools.yaml`, and an already-running Toolbox process carried on serving the old three-tool manifest. `tools/list` didn't include `insert_doc`, and calling it anyway returned `invalid tool name: tool with name "insert_doc" does not exist` - which sends you hunting for a YAML bug that isn't there.

My first assumption was that hot reload had failed. It hadn't: reload works fine, for both an in-place append and an atomic replace, within a second or two. The actual culprit is that **`${VAR}` interpolation resolves against the running process's environment**. That server had been started *before* I added `GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_LOCATION` to my env file, so every reload attempt hit a variable it couldn't resolve, and Toolbox - reasonably - kept the last config that worked. What makes it hard to spot is the log level:


```text
WARN "error loading configs unable to parse config file at \"tools.yaml\":
error parsing environment variables: environment variable not found: \"GOOGLE_CLOUD_PROJECT\""
```

That's a `WARN`, not an `ERROR`, buried in request logs, on a server you probably started in another terminal an hour ago. So: hot reload is real and you can lean on it for statement and parameter changes, but any edit that introduces a *new environment variable* needs a restart, because a running process can't see variables that didn't exist when it forked.

Now the interaction looks like this from the agent's perspective:

> **User:** Save this note: "ClickHouse skipping indexes store metadata about granules so queries can skip blocks that definitely don't match."  
>   
> **Agent:** *calls `insert_doc(content="ClickHouse skipping indexes store…")`* - Toolbox copies the content into the hidden parameter, embeds it into a 768-dim vector, and binds both to the INSERT.  
>   
> **User:** What did I save about making queries faster?  
>   
> **Agent:** *calls `search_docs(query="making queries faster")`* - Toolbox embeds the query and ClickHouse ranks by cosine distance.

The agent's tool call and the database query are both plain text and plain SQL. The vector layer is invisible.

### From application code

For custom agents, Toolbox ships client SDKs for Python, JavaScript/TypeScript, Go, and Java, with framework adapters for LangChain/LangGraph, LlamaIndex, and Google's ADK. The core Python SDK:


```shell
pip install toolbox-core
```

```py
import asyncio
from toolbox_core import ToolboxClient

async def main():
    async with ToolboxClient("http://127.0.0.1:5000") as client:
        # Load the toolset and hand the tools to your agent framework…
        tools = await client.load_toolset("semantic_search")

        # …or invoke a tool directly. The string is embedded server-side;
        # your application never touches a vector.
        search = await client.load_tool("search_docs")
        results = await search(query="how do I make queries faster?")
        print(results)

asyncio.run(main())
```

Or drop the tools straight into a LangGraph agent:


```py
from toolbox_langchain import ToolboxClient
from langgraph.prebuilt import create_react_agent

async with ToolboxClient("http://127.0.0.1:5000") as client:
    tools = client.load_toolset("semantic_search")
    agent = create_react_agent(model, tools)
```

Either way, the embedding step stays server-side in Toolbox - swap `gemini-embedding-001` for another model or change the dimension, and no application code changes.

## Production notes

A few things worth knowing before you take this past a demo:

- **Batching.** If a single invocation has multiple embedded parameters using the same model, Toolbox batches them into one embedding API call. But each *tool invocation* still embeds inline - my 57 documents meant 57 separate round trips to Vertex AI, which is fine at 4.1 seconds and very much not fine at a million rows. For bulk ingestion, embed offline and load with a proper batch pipeline (tens of thousands of rows per `INSERT`, or `async_insert=1` if you must trickle). Save `insert_doc` for agent-driven, one-at-a-time writes.  
- **Return nothing rather than noise.** As the dinner query showed, top-k always returns k rows. Add a distance threshold to search tools that an agent will act on.  
- **Driver-escaped parameters, not prepared statements.** Regular `parameters` are serialised and escaped by `clickhouse-go` from typed values, which removes the injection class - but the statement reaches the server as one interpolated string, vector literal and all, so don't describe this as server-side binding and do expect fat `query_log` entries. Toolbox also supports `templateParameters` for things like table names, and those are plain string substitution with no escaping at all, so keep anything user-controlled in regular parameters.  
- **Exact vs. approximate.** `cosineDistance` with no index is exact and O(n); the `vector_similarity` HNSW index makes it approximate and fast. At 57 rows the index is 29.8% of the part and earns nothing, so brute force is the whole story at this scale. Test recall on your own data before flipping to ANN.  
- **You can't set the embedding task type.** `SEMANTIC_SIMILARITY` is hardcoded, so the asymmetric `RETRIEVAL_DOCUMENT` / `RETRIEVAL_QUERY` pairing Google recommends for search isn't available. If retrieval quality is the thing you're optimising, embed outside Toolbox.  
- **Observability and auth.** Toolbox emits OpenTelemetry traces (including the embedding call) and metrics out of the box, and tools can require authenticated invocation - worth wiring up before exposing write tools like `insert_doc`.  
- **Bind address and origins.** The default listener is loopback-only, but `--allowed-origins` and `--allowed-hosts` both default to `*`, and Toolbox warns about DNS-rebinding risk on every start. Set them explicitly.

## Wrapping up

The pattern here generalizes well beyond a toy documents table: any ClickHouse table with an `Array(Float32)` column becomes agent-searchable with about forty lines of YAML - just a declarative statement of *which parameters mean text* and *which model turns them into vectors*. And the same `embeddedBy` machinery drives pgvector on Postgres, the only other engine with a vector formatter in the codebase.

The rough edges are mostly in the plumbing rather than the idea - Gemini is the only embedding provider, the REST endpoints need an opt-in flag, and a config that gains a new environment variable needs a restart rather than a reload. The one that isn't plumbing is the hardcoded `SEMANTIC_SIMILARITY` task type, which puts a ceiling on retrieval quality. Given ClickHouse's brute-force vector performance on columnar data and its maturing HNSW index, this combination - MCP Toolbox for the agent boundary, ClickHouse for storage and ranking - is still one of the fastest paths I've seen from "we have text in a table" to "our agent can search it semantically."

---

*MCP Toolbox is open source (Apache 2.0) at [github.com/googleapis/mcp-toolbox](https://github.com/googleapis/mcp-toolbox). Full docs at [mcp-toolbox.dev](https://mcp-toolbox.dev/documentation/introduction/), including the [ClickHouse integration](https://mcp-toolbox.dev/integrations/clickhouse/source) and [embedding models reference](https://mcp-toolbox.dev/documentation/configuration/embedding-models/). Tested against Toolbox 1.9.0 and ClickHouse Cloud 26.4.1.*  
