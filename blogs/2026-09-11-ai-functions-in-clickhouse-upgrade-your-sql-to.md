---
title: "AI Functions in ClickHouse: Upgrade your SQL to the AI age"
date: "2026-09-11T12:49:32.253Z"
author: "Andriy Yakovlev and George Larionov"
category: "Product"
excerpt: "Explore ClickHouse AI Functions for classification, generation, translation, embeddings, semantic search, and cost controls—all directly from SQL."
---

# AI Functions in ClickHouse: Upgrade your SQL to the AI age

ClickHouse now has a family of built-in [AI Functions](https://clickhouse.com/docs/reference/functions/regular-functions/ai-functions) that call an LLM or an embedding provider directly from the SQL engine. The model becomes something you call from SQL, like lower() or sum(), and it runs where your data already lives.

The functions are currently in Beta and functionality is constantly being added and improved. They arrived over the course of three releases: *aiGenerate()*, *aiClassify()*, *aiExtract()*, and *aiTranslate()* in 26.4, *aiEmbed()* in 26.6, then *aiFilter()*, *aiRedact()*, and *aiSimilarity()* in 26.8.

---

## Try AI Functions in ClickHouse Cloud

In ClickHouse Cloud, no extra configuration mentioned below is required—the functions are plug-and-play. Currently, AI Functions are in private preview in ClickHouse Cloud.

[Join the private preview](https://clickhouse.com/cloud/ai-functions-and-inference-services-waitlist?loc=blog-cta-1960-try-ai-functions-in-clickhouse-cloud-join-the-private-preview&utm_blogctaid=1960)

---

## Why we developed this {#why_we_developed_this}

All your data already lives in ClickHouse: logs, product reviews, descriptions and support tickets. Traditional LLM workflows (like RAG) pull data out of database into a separate stack to run classification or embedding tasks, then push the results back in. This approach is slow, error prone, and adds operational complexity.

The core idea behind AI Functions is to move the model to the data instead of the data to the model. Because ClickHouse already stores and can [search vectors](https://clickhouse.com/docs/guides/use-cases/ai-ml/vector-search), the full RAG cycle can run in one system rather than being stitched together across a vector database, an orchestration framework, and a separate LLM API. 

As a simple example:

```sql
SELECT aiClassify('I love this product!', ['positive', 'negative', 'neutral']);
```

Response:

```shell
positive
```

---

## AI Functions in one query

In short, AI Functions turn intricate workflows into a straightforward `SELECT` query.

[Explore AI Functions](https://clickhouse.com/docs/reference/functions/regular-functions/ai-functions?loc=blog-cta-1961-ai-functions-in-one-query-explore-ai-functions&utm_blogctaid=1961)

---

## What is in the beta {#what_is_in_the_beta}

The following [AI Functions](https://clickhouse.com/docs/reference/functions/regular-functions/ai-functions) are available for you in 26.8. **Text** functions:

* **aiClassify** - Classifies the given text into one of the provided categories using an LLM provider.  
* **aiExtract** - Extracts structured information from unstructured text using an LLM provider.  
* **aiGenerate** - Generates free-form text content from a prompt using an LLM provider.  
* **aiTranslate** - Translates the given text into the specified target language using an LLM provider.  
* **aiFilter** - Evaluates a natural-language condition against the given text using an LLM provider and returns a boolean (`UInt8`) suitable for **`WHERE`**, **`PREWHERE`**, and **`JOIN ... ON`**.  
* **aiRedact** - Detects and redacts personally identifiable information (PII) in the given text using an LLM provider.

**Embedding** functions:

* **aiEmbed** - Generates an embedding vector for the given text using the configured AI provider.  
* **aiSimilarity** - Computes the semantic similarity of two texts using the configured embedding provider.

AI Functions work by making a remote HTTP call to the configured provider's API for each input, or a batch of inputs for the embedding functions, and returning the parsed response as a native ClickHouse value. 

## Preparing the setup (OSS only) {#preparing_the_setup_oss_only}

To begin using AI Functions, you must configure two [named collections](https://clickhouse.com/docs/concepts/features/configuration/server-config/named-collections) (for text and embedding, respectively) to store your provider credentials and configuration.

We recommend configuring settings `ai_function_text_default_credentials` and `ai_function_embedding_default_credentials` with the names of the named collections. Then, all AI Functions will pick up the right endpoint automatically. It is also possible to override the settings during execution.

Example statement to create a named collection with OpenAI provider credentials: you'll need an API key from OpenAI, one with a **chat** endpoint and another with an **embedding** endpoint:

```sql
CREATE NAMED COLLECTION ai_text_credentials AS
    provider = 'openai',
    endpoint = 'https://api.openai.com/v1/chat/completions',
    model = 'gpt-5.6-terra',
    api_key = 'sk-...';

-- The embedding functions (`aiEmbed`, `aiSimilarity`) do not read `model` from the named collection.
CREATE NAMED COLLECTION ai_embedding_credentials AS
    provider = 'openai',
    endpoint = 'https://api.openai.com/v1/embeddings',
    api_key = 'sk-...';
```

> **Note:** Any OpenAI-compatible API (e.g. Ollama, LiteLLM) can be used by setting `provider = 'openai'` and pointing the endpoint to your service. Therefore, this works with a local model too.

Next, configure the default-credentials setting:

```sql
SET ai_function_text_default_credentials = 'ai_text_credentials';
SET ai_function_embedding_default_credentials = 'ai_embedding_credentials';
```

Now you are ready to run the functions. Let’s review some examples.

## Understanding your data: classify, filter {#understanding_your_data_classify_filter}

The examples below use the [Hacker News dataset](https://clickhouse.com/docs/get-started/sample-datasets/hacker-news), 28 million rows of stories and comments, loaded with the Parquet schema from that guide. The columns we care about are `title`, `comment`, `author`, `score`, `type`, and `timestamp`. Make sure you follow the setup steps above.

`aiClassify` takes a string and a constant list of labels, and returns exactly one of those labels. The model is asked to pick a bucket, so it has limited creativity here.

Front page titles are a good starting point because they are short, which keeps token usage low:

```sql
SELECT 
    title,
    aiClassify(title, ['space', 'security', 'databases', 'startups', 'programming', 'other']) AS topic
FROM hackernews
WHERE (type = 'story') AND (score < 3000) AND (title != '')
ORDER BY score DESC
LIMIT 3 FORMAT Vertical;
```

Response:

```sql
Row 1:
──────
title: SpaceX’s Falcon Heavy successfully launches
topic: space

Row 2:
──────
title: Twitter Will Allow Employees to Work at Home Forever
topic: other

Row 3:
──────
title: No Cookie for You
topic: security
```

Since the output is a `String`, it integrates seamlessly with standard SQL. You can use `aiClassify` in a subquery, then aggregate over the result. For anything you plan to query more than once, classify into a column instead of recomputing.

---

## Analyze with SQL, not Python

That is a topic breakdown of high-scoring Hacker News stories, computed without a single line of Python. In the old workflow, this would be an export, a classification job, and a load back into ClickHouse.

[Explore the dataset](https://clickhouse.com/docs/get-started/sample-datasets/hacker-news?loc=blog-cta-1962-analyze-with-sql-not-python-explore-the-dataset&utm_blogctaid=1962)

---

`aiFilter` returns `UInt8`, which means it can go straight into `WHERE` and behave like any other boolean condition. This is the function that most clearly does something SQL could not do before. Token search finds rows containing the word "database". `aiFilter` finds rows where someone is complaining about one:

```sql
SELECT author, substring(comment, 1, 100) AS snippet 
FROM (
  SELECT author, comment 
  FROM hackernews
  WHERE type = 'comment' AND ilike(comment, '%database%') 
  LIMIT 500 
)
WHERE aiFilter(comment, 'the author is describing a production incident or outage they experienced') LIMIT 3 FORMAT Vertical;
```

Response:

```sql
Row 1:
──────
author:  0x0
snippet: Wow, the database connection ip and dbname were taken from http cookies!

Row 2:
──────
author:  AccountCreated
snippet: &gt; The primary MCP database is comprised of 9 MongoDB shards
enough said.

Row 3:
──────
author:  tomazzi
snippet: The link goes to "Database Error - Error establishing a database connection" which is kind of intere
```

> **Note:** Since AI Function calls can be slow to process, it’s best to apply cheap predicates first in a subquery, then call the LLM predicate in the outer query.

## Reshaping your data: generate, translate {#reshaping_your_data_generate_translate}

Previous classification examples put text into buckets; the next two functions produce new text. We use the same dataset and same setup as above.

`aiGenerate` takes a prompt and returns whatever the model writes back. In a SQL context the prompt is usually built with `concat` from a column.

Hacker News comments are a good target because many of them are long, and this is a great candidate for summarization. In this example we also use `params` map with a `system_prompt` and `temperature` parameters that keep the output shaped consistently across rows:

```sql

SELECT
    author,
    length(comment) AS original_chars,
    aiGenerate(
        concat('Summarize this Hacker News comment in one sentence: ', comment),
        map('system_prompt', 'You are terse. Reply with one sentence and no preamble.',
            'temperature', '0.3',
            'max_tokens', '2000'
)
    ) AS summary
FROM hackernews
WHERE type = 'comment' AND length(comment) > 1000
LIMIT 3 FORMAT Vertical;
```

Response:

```sql
Row 1:
──────
author:         0-_-0
original_chars: 1076
summary:        Some VPN providers have been court-verified to keep no logs, and given their financial incentive to protect their reputation plus mandatory data retention laws in many countries, using a reputable VPN is likely more private than relying on your local ISP.

Row 2:
──────
author:         0-_-0
original_chars: 1428
summary:        The comment shares Our World in Data links comparing COVID-19 confirmed cases, deaths, and case fatality rates across several countries using 7-day rolling averages.

Row 3:
──────
author:         0-_-0
original_chars: 1337
summary:        The commenter is drawing a parallel to Wim Hof, a man famous for extreme cold endurance feats and the ability to consciously control his immune system through a method combining cold exposure, breathing, and meditation.
```

You can also do interesting patterns with generating once per group rather than once per row, something like this:

```sql
SELECT aiGenerate(
    concat(
        'Write a three-bullet digest of what Hacker News was discussing. Titles:\n',
        arrayStringConcat(groupArray(title), '\n')
    )
) AS digest;
```

`aiTranslate` takes the text and a target language, either a name or a BCP-47 code. The parameter worth knowing about is `instructions`, which passes style or dialect guidance to the model:

```sql
SELECT title, aiTranslate(title, 'Spanish', map('instructions', 'Use polite form. Keep technical terms and product names in English.')) AS title_es 
FROM hackernews
WHERE type = 'story' AND score < 3000 AND title != ''
ORDER BY score DESC LIMIT 3 FORMAT Vertical;
```

Response:

```sql
Row 1:
──────
title:    SpaceX’s Falcon Heavy successfully launches
title_es: El Falcon Heavy de SpaceX se lanza con éxito

Row 2:
──────
title:    Twitter Will Allow Employees to Work at Home Forever
title_es: Twitter Permitirá a sus Empleados Trabajar desde Casa para Siempre

Row 3:
──────
title:    No Cookie for You
title_es: Sin Cookie para Ti
```

Because both functions return `String`, they can be nested. For example, summarize a long comment, then translate the summary:

```sql
aiTranslate(
 aiGenerate( concat('Summarize in one sentence: ', comment),
            map('system_prompt', 'Reply with one sentence, no preamble.') ),
 'es-MX' ) AS resumen;
```

## The full RAG cycle, in the database {#the_full_rag_cycle_in_the_database}

Retrieval augmented generation powered by aiEmbed and vector search  

![ClickHouse AI Functions MDSN-142.jpg](https://clickhouse.com/uploads/Click_House_AI_Functions_MDSN_142_59966a8ce7.jpg)

Every stage can now be performed in SQL:

1. Embed at write time with `aiEmbed()` in a materialized view, so vectors are populated as data lands.  
2. Store data and Embeddings next to each other  
3. Index with a vector similarity index  
4. Retrieve with `cosineDistance` against the embedded data.  
5. Generate the answer with `aiGenerate` over the retrieved context

Note that `aiSimilarity()` is the convenience path for ad hoc work: it embeds both sides and returns cosine similarity in one call, which is ideal for semantic dedup or ranking a few thousand rows.

## Putting a ceiling on spend {#putting_a_ceiling_on_spend}

Unlike most ClickHouse functions, AI functions have a per-call cost in tokens and dollars, as opposed to just CPU cycles and memory usage. When deploying such functions, limiting per-query token cost and usage is likely to be front of mind. To help avoid runaway queries and hair-raising AI usage bills, we have implemented a set of quota settings which can be used to limit per-query AI function usage. 

The following session settings are used to control these quotas:

* [ai_function_max_input_tokens_per_query (default 1000000\)](https://clickhouse.com/docs/reference/settings/session-settings/ai-function#ai_function_max_input_tokens_per_query)  
* [ai_function_max_output_tokens_per_query (default 500000\)](https://clickhouse.com/docs/reference/settings/session-settings/ai-function#ai_function_max_output_tokens_per_query)  
* [ai_function_max_api_calls_per_query (default 1000\)](https://clickhouse.com/docs/reference/settings/session-settings/ai-function#ai_function_max_api_calls_per_query)

As well as a setting that controls error behavior upon reaching the quota limit: [ai_function_throw_on_quota_exceeded](https://clickhouse.com/docs/reference/settings/session-settings/ai-function#ai_function_throw_on_quota_exceeded) (default 1 - throw).

The settings above can be used like so:

```sql
SELECT
    title,
    aiClassify(title, ['space', 'security', 'databases', 'startups', 'programming', 'other']) AS topic
FROM hackernews
WHERE type = 'story' AND score > 100 AND title != ''
LIMIT 5000
SETTINGS ai_function_max_api_calls_per_query = 100;
```

The text functions issue one request per row, so a call budget is effectively a row budget. This query wants 5000 rows but is only allowed 100 requests, so it stops:

```sql
Code: 290. DB::Exception: AI API call limit reached: 100 calls made, maximum: 100.
This is controlled by the 'ai_function_max_api_calls_per_query' setting. (LIMIT_EXCEEDED)
```

The count is exact, since the quota is checked before every request is dispatched, so a query never overshoots its call budget. Setting it to `0` disables the limit.

Token quotas work the same way, but track what the provider actually reports, which is much closer to what you get billed for. Summarizing long Hacker News comments is the expensive case, since the whole comment goes into the prompt:

```sql
SELECT
    author,
    aiGenerate(
        concat('Summarize this Hacker News comment in one sentence: ', comment),
        map('system_prompt', 'You are terse. Reply with one sentence and no preamble.',
            'temperature', '0.3')
    ) AS summary
FROM hackernews
WHERE type = 'comment' AND length(comment) > 1000
LIMIT 2000
SETTINGS
    ai_function_max_input_tokens_per_query = 500000,
    ai_function_max_output_tokens_per_query = 50000;

Code: 290. DB::Exception: AI input token limit reached or exceeded: 500642 tokens consumed,
maximum: 500000. This is controlled by the 'ai_function_max_input_tokens_per_query' setting.
```

Note "reached or exceeded". A call's token cost is not known until its response comes back, so the total can overshoot by up to one in-flight request's worth per thread. Leave headroom rather than setting the limit to the exact number you can afford.

Aborting is the right default, but not always what you want. Stopping a long classification run at 99% and returning nothing is worse than returning most of it. `ai_function_throw_on_quota_exceeded = 0` turns the quota into a soft stop:

```sql
SELECT
    topic,
    count() AS stories
FROM (
    SELECT aiClassify(title, ['space', 'security', 'databases', 'startups', 'programming', 'other']) AS topic
    FROM hackernews
    WHERE type = 'story' AND score > 100 AND title != ''
    LIMIT 5000
)
WHERE topic != ''
GROUP BY topic
ORDER BY stories DESC
SETTINGS
    ai_function_max_api_calls_per_query = 1000,
    ai_function_throw_on_quota_exceeded = 0;
```

Rows past the quota receive the column's default, an empty string for `String`, and the query succeeds. The `WHERE topic != ''` filters them back out, so you get a partial but honest aggregate instead of an exception.

To see what a query actually spent, read the profile events from `system.query_log`:

```sql
SELECT
    ProfileEvents['AIAPICalls']      AS api_calls,
    ProfileEvents['AIInputTokens']   AS input_tokens,
    ProfileEvents['AIOutputTokens']  AS output_tokens,
    ProfileEvents['AIRowsProcessed'] AS rows_processed,
    ProfileEvents['AIRowsSkipped']   AS rows_skipped
FROM system.query_log
WHERE query_id = 'hn_classify' AND type = 'QueryFinish'
ORDER BY event_time DESC
LIMIT 1 FORMAT Vertical;

Row 1:
──────
api_calls:      1000
input_tokens:   24310
output_tokens:  3122
rows_processed: 1000
rows_skipped:   4000
```

`AIRowsSkipped` is the one to watch whenever `ai_function_throw_on_quota_exceeded = 0`, since it counts rows that quietly got a default value, from either a quota cut or an error. The cheapest way to size a quota is to run this over a `LIMIT 100` sample first and multiply.

Some things to keep in mind while configuring the quotas:

* **Set them in the top-level query.** A `SETTINGS` clause on a sub-query is ignored for the quota settings.  
* **They are per server, per query fragment.** Within one execution context the cap is exact and shared across every AI function, block and thread. A distributed query can dispatch up to the limit *on each shard*, so divide by your shard count.  
* **Token quotas need a provider that reports usage.** OpenAI, Anthropic and vLLM do. Providers that omit the `usage` object leave the token counters at `0`, so those limits never fire, and you should bound them with `ai_function_max_api_calls_per_query` instead.   
* **Embedding functions never produce completion tokens**, so the output-token limit does not apply to `aiEmbed` or `aiSimilarity`.  
* **Retries count against the call quota**. `ai_function_max_retries` defaults to `1`, so a budget of 1000 covers 1000 *attempts*, not 1000 rows, if the provider returns transient errors.

## Things to know before you ship {#things_to_know_before_you_ship}

Please keep in mind those concerns and limitations while shipping this to production:

* **Prompt injection**: input text steers the model, so treat output as untrusted and never feed it into generated SQL or shell commands.  
* **Non-determinism**: same rows fed into the LLM will give different answers, so use temperature = 0 and consider materializing results rather than recomputing them.   
* **Cost:** Cost and latency scale with row count, so always test with LIMIT first, and make use of the quota settings described above   
* **Security**: restrict `remote_url_allow_hosts` to your providers, keep endpoints on HTTPS, and remember the provider sees your data in cleartext after TLS termination.

## Conclusion {#conclusion}

AI Functions put classification, translation, embedding, and generation on SQL map in ClickHouse World. The full RAG loop now runs where the data already is. Looking forward to hearing from you on how you can build your apps based on this functionality.

---

## Try AI Functions in ClickHouse Cloud

AI Functions are in private preview in ClickHouse Cloud.

[Join the private preview](https://clickhouse.com/cloud/ai-functions-and-inference-services-waitlist?loc=blog-cta-1963-try-ai-functions-in-clickhouse-cloud-join-the-private-preview&utm_blogctaid=1963)

---