---
title: "Building a Chatbot for Hacker News and Stack Overflow with LlamaIndex and ClickHouse"
date: "2024-02-28T14:37:40.711Z"
author: "Dale McDiarmid"
category: "Engineering"
excerpt: "Using  the new ClickHouse LlamaIndex  integration, we built a chatbot for Hacker News and Stack Overflow, taking advantage of the ability to combine structured and unstructured datasets. "
---

# Building a Chatbot for Hacker News and Stack Overflow with LlamaIndex and ClickHouse

## Introduction

Hacker News and StackOverflow contain lots of data on the state of developer tooling, both in terms of the things people are excited about and the things that they’re struggling with. Although these tools are used on a post-by-post basis, if you aggregate all the data together, they give you a great overview of the ecosystem. As avid users of both, we wanted to know the answer to questions such as:

**“What are the main opinions of the infrastructure tool that people working in organizations over 1000 people most want to work with?"**

In this blog post, we will build an LLM-backed chatbot, "HackBot", that lets us answer these questions using ClickHouse, LlamaIndex, Streamlit, and OpenAI. **You will learn how to:**

* Store and query vectors in ClickHouse
* Use LlamaIndex to convert text to SQL queries and then execute those against Stack Overflow surveys in ClickHouse using the new ClickHouse-Llama Index integration.
* Do vector search on Hacker News with metadata filtering using LlamaIndex
* Combine the two search approaches to provide a rich context to an LLM
* Quickly build a chat-based UI using Streamlit

## Some Context

Last year, [we explored how ClickHouse can be used as a vector database](https://clickhouse.com/blog/vector-search-clickhouse-p2) when users need highly performant linear scans for accurate results and/or the ability to combine vector search with filtering and aggregating on metadata through SQL. Users can use these capabilities to provide context to LLM-based applications through Retrieval-augmented generation (RAG) pipelines. As our investment in the underlying support for Vector search continues[[1][2][3]](https://github.com/ClickHouse/ClickHouse/pull/60202), we recognize that supporting users in building applications that rely on Vector search requires us to also invest in the surrounding ecosystem.

In this spirit, we have recently added [support for ClickHouse to LlamaIndex](https://github.com/run-llama/llama_index/pull/10583) as well as enhancing [Langchain’s support for ClickHouse exact matching](https://github.com/langchain-ai/langchain/pulls?q=is%3Apr+is%3Aopen+ClicKhouse) and templates to simplify the getting started experience.

As part of improving these integrations, we’ve also spent a little time putting them into practice and building an application called HackBot. This application will be based on LlamaIndex. In particular, we’ll be using the combination of ClickHouse and LlamaIndex to combine both structured results from SQL tables with unstructured vector searches to provide context to an LLM.

If you’re curious how we built the following in less than a couple of hundred lines of code (hint: Streamlit helps here), read on or just read the code [here](https://github.com/ClickHouse/examples/tree/main/blog-examples/llama-index/hacknernews_app)…

![hackbot.png](https://clickhouse.com/uploads/hackbot_509f845c3e.png)

## Why LlamaIndex?

We've discussed the concept of Retrieval-Augmented Generation (RAG)  [in previous posts](https://clickhouse.com/blog/retrieval-augmented-generation-rag-with-clickhouse-bedrock) and how this technique aims to combine the power of pre-trained language models with the benefits of information retrieval systems. The objective here is typically straightforward: to enhance the quality and relevance of generated text by providing the model with additional information (context) obtained from other sources (usually via vector search). 

While users can, in theory, build these RAG flows by hand, LlamaIndex provides a flexible data framework and toolkit for connecting data sources to large language models. By providing many of the existing workflows as a library of functions, as well as support for inserting data to and querying virtually any datastore, developers can focus on components of the system that will impact the quality of results vs. concerning themselves with the application "glue." We'll use LlamaIndex's query interface in this blog post to keep our code minimal. 

<blockquote style="font-size: 14px;">
<p>One of the strengths of the LlamaIndex is its ability to operate with a huge range of integrations. As well as a pluggable vector store interface, users can integrate their LLM, embedding model, graph store, and document store, along with the ability to hook in and customize almost any step of the RAG pipeline. All of these integrations can be browsed through the <a href="https://llamahub.ai/?tab=storage">LlamaHub</a>.</p>
</blockquote>

## Our application

To illustrate the benefits of LlamaIndex, let's consider our application "HackBot". This will take questions that aim to obtain a summary of people's opinions from Hacker News and surveys performed by Stack Overflow. In our proof of concept, these questions will take three general forms:

1. **Structured** questions that can be answered from Stack Overflow survey data e.g. "What is the most popular database?". To answer this, a SQL query must be generated before a response is passed back to the user. We've explored the challenge of natural language to SQL generation in [previous blogs](https://clickhouse.com/blog/retrieval-augmented-generation-rag-with-clickhouse-bedrock).
2. **Unstructured** questions summarizing people's opinions on technology e.g. "What are people saying about ClickHouse?". This requires a vector search against Hacker News posts to identify relevant comments. These can then be provided as context to the LLM for the generation of a natural language response.
3. **Structured + Unstructured** questions. In this case, the user may pose a question that requires context to be obtained from both the survey results and the posts. For example, suppose a user asks, "What are people saying about the most popular database?" In this case, we first need to establish the most popular database from survey results before using this to search for opinions in the Hacker News posts. Only then can this context be provided to the LLM for response generation.

Supporting these leads to a reasonably complex RAG flow with a pipeline for each of the above containing multiple decision points:

![Determine question type.png](https://clickhouse.com/uploads/Determine_question_type_52c98cb110.png)

![Structured (1).png](https://clickhouse.com/uploads/Structured_1_2b9279e1c6.png)

![Unstructured pipeline.png](https://clickhouse.com/uploads/Unstructured_pipeline_a13afb5f2f.png)

![Structured + unstructured.png](https://clickhouse.com/uploads/Structured_unstructured_f1385f8be9.png)

Our problem is simplified by using ClickHouse, which can act as both the structured source of information (surveys) available via SQL and the unstructured via vector search. However, usually, this would require a significant amount of application glue and testing, from making sure prompts were effective to parsing responses at decision points.

Fortunately, LlamaIndex allows all of this complexity to be encapsulated and handled through an existing set of library calls.

### Datasets

Any good application first needs data. As mentioned, our Hacker News (HN) and Stack Overflow posts represent our structured and unstructured data that will power our app. Our HN data is here over 28m rows and NGiB, while Stack Overflow is significantly smaller at only 83439 responses.

Our Hacker News rows consist of the user's comment and associated metadata, e.g. the time it was posted, their username, and the score of the post. The text has been embedded using the `sentence-transformers/all-MiniLM-L6-v2` to produce a 384 dimension vector. This results in the following schema:

```sql
CREATE TABLE hackernews
(
    `id` String,
    `doc_id` String,
    `comment` String,
    `text` String,
    `vector` Array(Float32),
    `node_info` Tuple(start Nullable(UInt64), end Nullable(UInt64)),
    `metadata` String,
    `type` Enum8('story' = 1, 'comment' = 2, 'poll' = 3, 'pollopt' = 4, 'job' = 5),
    `by` LowCardinality(String),
    `time` DateTime,
    `title` String,
    `post_score` Int32,
    `dead` UInt8,
    `deleted` UInt8,
    `length` UInt32,
    `parent` UInt32,
    `kids` Array(UInt32)
)
ENGINE = MergeTree
ORDER BY (toDate(time), length, post_score)
```

You may notice we have a `comment` column as well as a `text` column. The latter of these contains both the `comment` as well as the text of the parent and children of the post e.g. if someone responds to a comment, it becomes a child. The goal here is to simply provide more context to the LLM when a row is returned. For how we generated this data, see [here](https://gist.github.com/gingerwizard/fc18cf5a3b9945b626cecb88a2deaa49). 

The `metadata` column contains the fields which can be queried automatically by LlamaIndex workflows e.g. if they determine additional filters are required to answer a question. For our current implementation, we use a string containing JSON for this column. In the future, once production is ready, we plan to move this to the JSON type for better query performance. For now, we replicate all columns to this string, thus making them available to LlamaIndex e.g.

```json
{"deleted":0,"type":"story","by":"perler","time":"2006-10-13 14:46:50","dead":0,"parent":0,"poll":0,"kids":[454479],"url":"http:\/\/www.techcrunch.com\/2006\/10\/13\/realtravel-trip-planner-cut-paste-share-travel-tips\/","post_score":2,"title":"RealTravel Trip Planner: Cut, Paste & Share Travel Tips","parts":[],"descendants":0}
```

Experienced users of ClickHouse will notice the ordering key. This will facilitate fast querying later in our application for queries that are filtered by date, post length (number of tokens in text), and the score assigned by HN. 

If you want to follow along, we’ve put all the data in a Parquet file in an S3 bucket. You can insert the data by running the following command:

```sql
INSERT INTO hackernews SELECT * FROM s3('https://datasets-documentation.s3.eu-west-3.amazonaws.com/hackernews/embeddings/hackernews-llama.parquet')
```

Our HN data covers the period from Oct 2006 to Oct 2021. To ensure our Stack Overflow data aligns with this, we will load just the survey results from 2021. 

<blockquote style="font-size: 14px;">
<p>Extending these datasets would be a reasonably straightforward exercise, although the survey columns do differ across years. Reconciling this data across years would allow questions such as “What were people in 2022 saying about the most popular web technology?” We leave this an exercise for the enthusiastic reader.</p>
</blockquote>

This data contains a significant number of columns as shown in the schema below:

<pre style="font-size: 14px;"><code class="hljs language-sql"><span class="hljs-keyword">CREATE</span> <span class="hljs-keyword">TABLE</span> surveys
(
   `response_id` Int64,
   `development_activity` Enum8(<span class="hljs-string">'I am a developer by profession'</span> <span class="hljs-operator">=</span> <span class="hljs-number">1</span>, <span class="hljs-string">'I am a student who is learning to code'</span> <span class="hljs-operator">=</span> <span class="hljs-number">2</span>, <span class="hljs-string">'I am not primarily a developer, but I write code sometimes as part of my work'</span> <span class="hljs-operator">=</span> <span class="hljs-number">3</span>, <span class="hljs-string">'I code primarily as a hobby'</span> <span class="hljs-operator">=</span> <span class="hljs-number">4</span>, <span class="hljs-string">'I used to be a developer by profession, but no longer am'</span> <span class="hljs-operator">=</span> <span class="hljs-number">5</span>, <span class="hljs-string">'None of these'</span> <span class="hljs-operator">=</span> <span class="hljs-number">6</span>, <span class="hljs-string">'NA'</span> <span class="hljs-operator">=</span> <span class="hljs-number">7</span>),
   `employment` Enum8(<span class="hljs-string">'Independent contractor, freelancer, or self-employed'</span> <span class="hljs-operator">=</span> <span class="hljs-number">1</span>, <span class="hljs-string">'Student, full-time'</span> <span class="hljs-operator">=</span> <span class="hljs-number">2</span>, <span class="hljs-string">'Employed full-time'</span> <span class="hljs-operator">=</span> <span class="hljs-number">3</span>, <span class="hljs-string">'Student, part-time'</span> <span class="hljs-operator">=</span> <span class="hljs-number">4</span>, <span class="hljs-string">'I prefer not to say'</span> <span class="hljs-operator">=</span> <span class="hljs-number">5</span>, <span class="hljs-string">'Employed part-time'</span> <span class="hljs-operator">=</span> <span class="hljs-number">6</span>, <span class="hljs-string">'Not employed, but looking for work'</span> <span class="hljs-operator">=</span> <span class="hljs-number">7</span>, <span class="hljs-string">'Retired'</span> <span class="hljs-operator">=</span> <span class="hljs-number">8</span>, <span class="hljs-string">'Not employed, and not looking for work'</span> <span class="hljs-operator">=</span> <span class="hljs-number">9</span>, <span class="hljs-string">'NA'</span> <span class="hljs-operator">=</span> <span class="hljs-number">10</span>),
   `country` LowCardinality(String),
   `us_state` LowCardinality(String),
   `uk_county` LowCardinality(String),
   `education_level` Enum8(<span class="hljs-string">'Secondary school (e.g. American high school, German Realschule or Gymnasium, etc.)'</span> <span class="hljs-operator">=</span> <span class="hljs-number">1</span>, <span class="hljs-string">'Bachelor'</span>s degree (B.A., B.S., B.Eng., etc.)<span class="hljs-string">' = 2, '</span>Master<span class="hljs-string">'s degree (M.A., M.S., M.Eng., MBA, etc.)'</span> <span class="hljs-operator">=</span> <span class="hljs-number">3</span>, <span class="hljs-string">'Other doctoral degree (Ph.D., Ed.D., etc.)'</span> <span class="hljs-operator">=</span> <span class="hljs-number">4</span>, <span class="hljs-string">'Some college/university study without earning a degree'</span> <span class="hljs-operator">=</span> <span class="hljs-number">5</span>, <span class="hljs-string">'Something else'</span> <span class="hljs-operator">=</span> <span class="hljs-number">6</span>, <span class="hljs-string">'Professional degree (JD, MD, etc.)'</span> <span class="hljs-operator">=</span> <span class="hljs-number">7</span>, <span class="hljs-string">'Primary/elementary school'</span> <span class="hljs-operator">=</span> <span class="hljs-number">8</span>, <span class="hljs-string">'Associate degree (A.A., A.S., etc.)'</span> <span class="hljs-operator">=</span> <span class="hljs-number">9</span>, <span class="hljs-string">'NA'</span> <span class="hljs-operator">=</span> <span class="hljs-number">10</span>),
   `age_started_to_code` Enum8(<span class="hljs-string">'Younger than 5 years'</span> <span class="hljs-operator">=</span> <span class="hljs-number">1</span>, <span class="hljs-string">'5 - 10 years'</span> <span class="hljs-operator">=</span> <span class="hljs-number">2</span>, <span class="hljs-string">'11 - 17 years'</span> <span class="hljs-operator">=</span> <span class="hljs-number">3</span>, <span class="hljs-string">'18 - 24 years'</span> <span class="hljs-operator">=</span> <span class="hljs-number">4</span>, <span class="hljs-string">'25 - 34 years'</span> <span class="hljs-operator">=</span> <span class="hljs-number">5</span>, <span class="hljs-string">'35 - 44 years'</span> <span class="hljs-operator">=</span> <span class="hljs-number">6</span>, <span class="hljs-string">'45 - 54 years'</span> <span class="hljs-operator">=</span> <span class="hljs-number">7</span>, <span class="hljs-string">'55 - 64 years'</span> <span class="hljs-operator">=</span> <span class="hljs-number">8</span>, <span class="hljs-string">'Older than 64 years'</span> <span class="hljs-operator">=</span> <span class="hljs-number">9</span>, <span class="hljs-string">'NA'</span> <span class="hljs-operator">=</span> <span class="hljs-number">10</span>),
   `how_learned_to_code` <span class="hljs-keyword">Array</span>(String),
   `years_coding` Nullable(UInt8),
   `years_as_a_professional_developer` Nullable(UInt8),
   `developer_type` <span class="hljs-keyword">Array</span>(String),
   `organization_size` Enum8(<span class="hljs-string">'Just me - I am a freelancer, sole proprietor, etc.'</span> <span class="hljs-operator">=</span> <span class="hljs-number">1</span>, <span class="hljs-string">'2 to 9 employees'</span> <span class="hljs-operator">=</span> <span class="hljs-number">2</span>, <span class="hljs-string">'10 to 19 employees'</span> <span class="hljs-operator">=</span> <span class="hljs-number">3</span>, <span class="hljs-string">'20 to 99 employees'</span> <span class="hljs-operator">=</span> <span class="hljs-number">4</span>, <span class="hljs-string">'100 to 499 employees'</span> <span class="hljs-operator">=</span> <span class="hljs-number">5</span>, <span class="hljs-string">'500 to 999 employees'</span> <span class="hljs-operator">=</span> <span class="hljs-number">6</span>, <span class="hljs-string">'1,000 to 4,999 employees'</span> <span class="hljs-operator">=</span> <span class="hljs-number">7</span>, <span class="hljs-string">'5,000 to 9,999 employees'</span> <span class="hljs-operator">=</span> <span class="hljs-number">8</span>, <span class="hljs-string">'10,000 or more employees'</span> <span class="hljs-operator">=</span> <span class="hljs-number">9</span>, <span class="hljs-string">'I don'</span>t know<span class="hljs-string">' = 10, '</span>NA<span class="hljs-string">' = 11),
   `compensation_total` Nullable(UInt64),
   `compensation_frequency` Enum8('</span>Weekly<span class="hljs-string">' = 1, '</span>Monthly<span class="hljs-string">' = 2, '</span>Yearly<span class="hljs-string">' = 3, '</span>NA<span class="hljs-string">' = 4),
   `language_have_worked_with` Array(String),
   `language_want_to_work_with` Array(String),
   `database_have_worked_with` Array(String),
   `database_want_to_work_with` Array(String),
   `platform_have_worked_with` Array(String),
   `platform_want_to_work_with` Array(String),
   `web_framework_have_worked_with` Array(String),
   `web_framework_want_to_work` Array(String),
   `other_tech_have_worked_with` Array(String),
   `other_tech_want_to_work` Array(String),
   `infrastructure_tools_have_worked_with` Array(String),
   `infrastructure_tools_want_to_work_with` Array(String),
   `developer_tools_have_worked_with` Array(String),
   `developer_tools_want_to_work_with` Array(String),
   `operating_system` Enum8('</span>MacOS<span class="hljs-string">' = 1, '</span>Windows<span class="hljs-string">' = 2, '</span>Linux<span class="hljs-operator">-</span>based<span class="hljs-string">' = 3, '</span>BSD<span class="hljs-string">' = 4, '</span>Other (please specify):<span class="hljs-string">' = 5, '</span>Windows Subsystem <span class="hljs-keyword">for</span> Linux (WSL)<span class="hljs-string">' = 6, '</span>NA<span class="hljs-string">' = 7),
   `frequency_visit_stackoverflow` Enum8('</span>Multiple times <span class="hljs-keyword">per</span> <span class="hljs-keyword">day</span><span class="hljs-string">' = 1, '</span>Daily <span class="hljs-keyword">or</span> almost daily<span class="hljs-string">' = 2, '</span>A few times <span class="hljs-keyword">per</span> week<span class="hljs-string">' = 3, '</span>A few times <span class="hljs-keyword">per</span> <span class="hljs-keyword">month</span> <span class="hljs-keyword">or</span> weekly<span class="hljs-string">' = 4, '</span>Less than once <span class="hljs-keyword">per</span> <span class="hljs-keyword">month</span> <span class="hljs-keyword">or</span> monthly<span class="hljs-string">' = 5, '</span>NA<span class="hljs-string">' = 6),
   `has_stackoverflow_account` Enum8('</span>Yes<span class="hljs-string">' = 1, '</span><span class="hljs-keyword">No</span><span class="hljs-string">' = 2, '</span><span class="hljs-keyword">Not</span> sure<span class="hljs-operator">/</span>can\<span class="hljs-string">'t remember'</span> <span class="hljs-operator">=</span> <span class="hljs-number">3</span>, <span class="hljs-string">'NA'</span> <span class="hljs-operator">=</span> <span class="hljs-number">4</span>),
   `frequency_use_in_stackoverflow` Enum8(<span class="hljs-string">'Multiple times per day'</span> <span class="hljs-operator">=</span> <span class="hljs-number">1</span>, <span class="hljs-string">'Daily or almost daily'</span> <span class="hljs-operator">=</span> <span class="hljs-number">2</span>, <span class="hljs-string">'A few times per week'</span> <span class="hljs-operator">=</span> <span class="hljs-number">3</span>, <span class="hljs-string">'A few times per month or weekly'</span> <span class="hljs-operator">=</span> <span class="hljs-number">4</span>, <span class="hljs-string">'Less than once per month or monthly'</span> <span class="hljs-operator">=</span> <span class="hljs-number">5</span>, <span class="hljs-string">'I have never participated in Q&amp;A on Stack Overflow'</span> <span class="hljs-operator">=</span> <span class="hljs-number">6</span>, <span class="hljs-string">'NA'</span> <span class="hljs-operator">=</span> <span class="hljs-number">7</span>),
   `consider_self_active_community_member` Enum8(<span class="hljs-string">'Yes, definitely'</span> <span class="hljs-operator">=</span> <span class="hljs-number">1</span>, <span class="hljs-string">'Neutral'</span> <span class="hljs-operator">=</span> <span class="hljs-number">2</span>, <span class="hljs-string">'Yes, somewhat'</span> <span class="hljs-operator">=</span> <span class="hljs-number">3</span>, <span class="hljs-string">'No, not at all'</span> <span class="hljs-operator">=</span> <span class="hljs-number">4</span>, <span class="hljs-string">'No, not really'</span> <span class="hljs-operator">=</span> <span class="hljs-number">5</span>, <span class="hljs-string">'NA'</span> <span class="hljs-operator">=</span> <span class="hljs-number">6</span>, <span class="hljs-string">'Not sure'</span> <span class="hljs-operator">=</span> <span class="hljs-number">7</span>),
   `member_other_communities` Enum8(<span class="hljs-string">'Yes'</span> <span class="hljs-operator">=</span> <span class="hljs-number">1</span>, <span class="hljs-string">'No'</span> <span class="hljs-operator">=</span> <span class="hljs-number">2</span>, <span class="hljs-string">'NA'</span> <span class="hljs-operator">=</span> <span class="hljs-number">4</span>),
   `age` Enum8(<span class="hljs-string">'Under 18 years old'</span> <span class="hljs-operator">=</span> <span class="hljs-number">1</span>, <span class="hljs-string">'18-24 years old'</span> <span class="hljs-operator">=</span> <span class="hljs-number">2</span>, <span class="hljs-string">'25-34 years old'</span> <span class="hljs-operator">=</span> <span class="hljs-number">3</span>, <span class="hljs-string">'35-44 years old'</span> <span class="hljs-operator">=</span> <span class="hljs-number">4</span>, <span class="hljs-string">'45-54 years old'</span> <span class="hljs-operator">=</span> <span class="hljs-number">5</span>, <span class="hljs-string">'55-64 years old'</span> <span class="hljs-operator">=</span> <span class="hljs-number">6</span>, <span class="hljs-string">'65 years or older'</span> <span class="hljs-operator">=</span> <span class="hljs-number">7</span>, <span class="hljs-string">'NA'</span> <span class="hljs-operator">=</span> <span class="hljs-number">8</span>, <span class="hljs-string">'Prefer not to say'</span> <span class="hljs-operator">=</span> <span class="hljs-number">9</span>),
   `annual_salary` Nullable(UInt64)
)
ENGINE <span class="hljs-operator">=</span> MergeTree
<span class="hljs-keyword">ORDER</span> <span class="hljs-keyword">BY</span> tuple()
</code></pre>

<blockquote style="font-size: 14px;">
<p>The column names here are very descriptive, e.g., <code>infrastructure_tools_have_worked_with</code> describes a list of tools a user wants to work with. These column names have been selected for the same reason we’ve also chosen here to liberally use the Enum type over LowCardinality. These choices make the data self-descriptive. Later, our LLM will need to consider this schema when generating SQL queries. By using Enums and self-describing column names, it avoids the need to provide additional context with an explanation of the meaning and possible values in each column.</p>
</blockquote>

Parsing this data from its original format requires a few SQL functions. While the original commands can be found [here](https://gist.github.com/gingerwizard/d3b32ed801973498e87145ed0c6e4bdb), we again provide the final data in Parquet in the interest of brevity:

```sql
INSERT INTO surveys SELECT * FROM s3('https://datasets-documentation.s3.eu-west-3.amazonaws.com/stackoverflow/surveys/2021/surveys-llama.parquet')
```

It is worth noting that data can be inserted into [ClickHouse via LlamaIndex](https://github.com/run-llama/llama_index/blob/main/docs/examples/vector_stores/ClickHouseIndexDemo.ipynb). We chose to do this directly via the ClickHouse client for performance and brevity reasons.

## Building a RAG pipeline in LlamaIndex

LlamaIndex is available in both Python and Typescript. For our examples, we’ll use Python for no other reason than I prefer it :).

Rather than build our RAG flow in one go, we’ll assemble the building blocks first: testing a separate query engine for structured and unstructured queries.

<blockquote style="font-size: 14px;">
<p style="">To install the ClickHouse integration for LlamaIndex, you can simply use <code>pip install llama-index-vector-stores-clickhouse</code></p>
</blockquote>

### Generating SQL with LlamaIndex

As mentioned above, we will need to convert some questions to SQL queries against our Stack Overflow data. Rather than building a prompt including our schema, making an HTTP request to ChatGPT, and parsing the response, we can rely on LlamaIndex to do this with a few calls. The following notebook is available [here](https://github.com/ClickHouse/examples/blob/main/blog-examples/llama-index/hacknernews_app/structured_nl_to_sql.ipynb).

<pre style="font-size: 12px;"><code class="hljs language-python">CLICKHOUSE_TEXT_TO_SQL_TMPL = (
    <span class="hljs-string">"Given an input question, first create a syntactically correct {dialect} "</span>
    <span class="hljs-string">"query to run, then look at the results of the query and return the answer. "</span>
    <span class="hljs-string">"You can order the results by a relevant column to return the most "</span>
    <span class="hljs-string">"interesting examples in the database.\n\n"</span>
    <span class="hljs-string">"Never query for all the columns from a specific table, only ask for a "</span>
    <span class="hljs-string">"few relevant columns given the question.\n\n"</span>
    <span class="hljs-string">"Pay attention to use only the column names that you can see in the schema "</span>
    <span class="hljs-string">"description. "</span>
    <span class="hljs-string">"Be careful to not query for columns that do not exist. "</span>
    <span class="hljs-string">"Pay attention to which column is in which table. "</span>
    <span class="hljs-string">"Also, qualify column names with the table name when needed. \n"</span>
    <span class="hljs-string">"If needing to group on Array Columns use the ClickHouse function arrayJoin e.g. arrayJoin(columnName) \n"</span>
    <span class="hljs-string">"For example, the following query identifies the most popular database:\n"</span>
    <span class="hljs-string">"SELECT d, count(*) AS count FROM so_surveys GROUP BY "</span>
    <span class="hljs-string">"arrayJoin(database_want_to_work_with) AS d ORDER BY count DESC LIMIT 1\n"</span>
    <span class="hljs-string">"You are required to use the following format, each taking one line:\n\n"</span>
    <span class="hljs-string">"Question: Question here\n"</span>
    <span class="hljs-string">"SQLQuery: SQL Query to run\n"</span>
    <span class="hljs-string">"SQLResult: Result of the SQLQuery\n"</span>
    <span class="hljs-string">"Answer: Final answer here\n\n"</span>
    <span class="hljs-string">"Only use tables listed below.\n"</span>
    <span class="hljs-string">"{schema}\n\n"</span>
    <span class="hljs-string">"Question: {query_str}\n"</span>
    <span class="hljs-string">"SQLQuery: "</span>
)

CLICKHOUSE_TEXT_TO_SQL_PROMPT = PromptTemplate(
    CLICKHOUSE_TEXT_TO_SQL_TMPL,
    prompt_type=PromptType.TEXT_TO_SQL,
)
<span class="hljs-comment"># (1) Query engine for ClickHouse exposed through SQLAlchemy</span>
engine = create_engine(
    <span class="hljs-string">f'clickhouse+native://<span class="hljs-subst">{username}</span>:<span class="hljs-subst">{password}</span>@<span class="hljs-subst">{host}</span>:'</span> +
    <span class="hljs-string">f'<span class="hljs-subst">{native_port}</span>/<span class="hljs-subst">{database}</span>?compression=lz4&amp;secure=<span class="hljs-subst">{secure}</span>'</span>
)
sql_database = SQLDatabase(engine, include_tables=[<span class="hljs-string">"surveys"</span>], view_support=<span class="hljs-literal">True</span>)


<span class="hljs-comment"># (2) Natural language to SQL query engine</span>
nl_sql_engine = NLSQLTableQueryEngine(
    sql_database=sql_database,
    tables=[<span class="hljs-string">"surveys"</span>],
    text_to_sql_prompt=CLICKHOUSE_TEXT_TO_SQL_PROMPT,
    llm=OpenAI(model=<span class="hljs-string">"gpt-4"</span>),
    verbose=<span class="hljs-literal">True</span>
)

response = nl_sql_engine.query(<span class="hljs-string">"What is the most popular database?"</span>)

<span class="hljs-built_in">print</span>(<span class="hljs-string">f"SQL query: <span class="hljs-subst">{response.metadata[<span class="hljs-string">'sql_query'</span>]}</span>"</span>)
<span class="hljs-built_in">print</span>(<span class="hljs-string">f"Answer: <span class="hljs-subst">{<span class="hljs-built_in">str</span>(response)}</span>"</span>)
</code></pre>

The key component here is the use of the [`NLSQLTableQueryEngine`](https://docs.llamaindex.ai/en/stable/understanding/putting_it_all_together/structured_data.html#natural-language-sql) engine at (2), which handles the querying of our LLM model (OpenAI gpt-4), passing the schema and prompt. On extracting the SQL query from the response, it executes this against our ClickHouse instance before building a response.

The above outputs MySQL as the most popular database (according to Stack Overflow in 2021!):

```
SQL query: SELECT d, count(*) AS count FROM surveys GROUP BY arrayJoin(database_have_worked_with) AS d ORDER BY count DESC LIMIT 1
Answer: The most popular database is MySQL.
```

You’ll notice that we have used a custom prompt rather than the default prompt offered by Llama. This is necessary as our `survey` table contains `Array(String)` columns. To aggregate these and return the required scalar, we need to use the [arrayJoin](https://clickhouse.com/docs/en/sql-reference/functions/array-join#important-note) function. We, therefore, include an example of this in our template. For how this compares with the default prompt, see [here](https://www.diffchecker.com/k3z1umdv/).

### Vector search for context with LlamaIndex

To handle our unstructured questions, we need the ability to convert questions to a vector embedding for querying ClickHouse before passing these results to our LLM for response generation. Ideally, this would also exploit the metadata on our Hacker News posts as well, e.g., so users can ask questions like “What is the user `zX41ZdbW` mostly posting about?” This requires us to tell Llama which fields are available for querying in our `metadata` column.

<pre style="font-size: 12px;"><code class="hljs language-python">CLICKHOUSE_CUSTOM_SUFFIX = <span class="hljs-string">"""
The following is the datasource schema to work with.
IMPORTANT: Make sure that filters are only used as needed and only suggest filters for fields in the data source.

Data Source:
{info_str}

User Query:
{query_str}

Structured Request:
"""</span>

CLICKHOUSE_VECTOR_STORE_QUERY_PROMPT_TMPL = PREFIX + EXAMPLES + CLICKHOUSE_CUSTOM_SUFFIX
Settings.embed_model = FastEmbedEmbedding(
       model_name=<span class="hljs-string">"sentence-transformers/all-MiniLM-L6-v2"</span>,
       max_length=<span class="hljs-number">384</span>,
       cache_dir=<span class="hljs-string">"./embeddings/"</span>
   )
client = clickhouse_connect.get_client(
   host=host, port=port, username=username, password=password,
   secure=secure
)
<span class="hljs-comment"># (1) Build a ClickHouseVectorStore</span>
vector_store = ClickHouseVectorStore(clickhouse_client=client, table=<span class="hljs-string">"hackernews"</span>)
vector_index = VectorStoreIndex.from_vector_store(vector_store)
<span class="hljs-comment"># (2) Inform the retriever of the available metadata fields</span>
vector_store_info = VectorStoreInfo(
       content_info=<span class="hljs-string">"Social news posts and comments from users"</span>,
       metadata_info=[
           MetadataInfo(
               name=<span class="hljs-string">"post_score"</span>, <span class="hljs-built_in">type</span>=<span class="hljs-string">"int"</span>, description=<span class="hljs-string">"Score of the comment or post"</span>,
           ),
           MetadataInfo(
               name=<span class="hljs-string">"by"</span>, <span class="hljs-built_in">type</span>=<span class="hljs-string">"str"</span>, description=<span class="hljs-string">"the author or person who posted the comment"</span>,
           ),
           MetadataInfo(
               name=<span class="hljs-string">"time"</span>, <span class="hljs-built_in">type</span>=<span class="hljs-string">"date"</span>, description=<span class="hljs-string">"the time at which the post or comment was made"</span>,
           ),
       ]
   )

<span class="hljs-comment"># (3) A retriever for vector store index that uses an LLM to automatically set vector store query parameters.</span>
vector_auto_retriever = VectorIndexAutoRetriever(
   vector_index, vector_store_info=vector_store_info, similarity_top_k=<span class="hljs-number">10</span>,
   prompt_template_str=CLICKHOUSE_VECTOR_STORE_QUERY_PROMPT_TMPL, llm=OpenAI(model=<span class="hljs-string">"gpt-4"</span>),
)


<span class="hljs-comment"># Query engine to query engine based on context</span>
retriever_query_engine = RetrieverQueryEngine.from_args(vector_auto_retriever, llm=OpenAI(model=<span class="hljs-string">"gpt-4"</span>))

response = retriever_query_engine.query(<span class="hljs-string">"What is the user zX41ZdbW saying about ClickHouse?"</span>)

<span class="hljs-built_in">print</span>(<span class="hljs-string">f"Answer: <span class="hljs-subst">{<span class="hljs-built_in">str</span>(response)}</span>"</span>)
</code></pre>

Here we first construct a [`ClickHouseVectorStore`](https://github.com/run-llama/llama_index/blob/da5f941662b65d2e3fe2100f2b58c3ba98d49e90/llama-index-integrations/vector_stores/llama-index-vector-stores-clickhouse/llama_index/vector_stores/clickhouse/base.py#L116) at (1), using this to build a [`VectorIndexAutoRetriever`](https://docs.llamaindex.ai/en/stable/examples/vector_stores/LanternAutoRetriever.html#define-vectorindexautoretriever) at (3). Notice how we also inform this retriever of the available metadata information, which uses this to add filters to our ClickHouse vector query automatically. Our `sentence-transformers/all-MiniLM-L6-v2` model is set globally and will be used to create an embedding for any text passed through the later `query` method prior to querying ClickHouse:

<blockquote style="font-size: 14px;">
<p>We have also adapted the default prompt since we found filters would be injected even if they weren’t present in the metadata.</p>
</blockquote>

This can be seen in logs if we run [the notebook](https://github.com/ClickHouse/examples/blob/main/blog-examples/llama-index/hacknernews_app/unstructured_nl_with_vector_store.ipynb).

`Using filters: [('by', '==', 'zX41ZdbW')]`

Our final response suggests that `zX41ZdbW` is quite knowledgeable on ClickHouse, which is good news as he’s the CTO! 

<blockquote style="font-size: 14px;">
<p>"The user zX41ZdbW has shared several insights about ClickHouse. They mentioned that ClickHouse has seen a 1.6 times performance improvement after simply adding __restrict in aggregate functions. They also mentioned that they patched Ryu in ClickHouse to provide nicer representations and to have better performance for floats that appear to be integers. They also shared that ClickHouse can do batch DELETE operations for data cleanup, which can fulfill the needs for data cleanup, retention, and GDPR requirements. They also mentioned that they are looking forward to a blog post for more references for comparison to optimize ClickHouse performance."</p>
</blockquote>

Under the hood, this code invokes the [`ClickHouseVectorStore`](https://github.com/run-llama/llama_index/tree/main/llama-index-integrations/vector_stores/llama-index-vector-stores-clickhouse), which issues a [cosineDistance](https://clickhouse.com/docs/en/sql-reference/functions/distance-functions#cosinedistance) (similar to those discussed in [our earlier blogs](https://clickhouse.com/blog/vector-search-clickhouse-p1)) query to identify the conceptually similar posts.

### Combining structured and unstructured

Armed with the above query engines, we can combine these with the [`SQLAutoVectorQueryEngine`](https://docs.llamaindex.ai/en/stable/examples/query_engine/SQLAutoVectorQueryEngine.html#define-sqlautovectorqueryengine) engine. The docs for this engine summarize its functionality well:

<blockquote style="font-size: 14px;">
<p>SQL + Vector Index Auto Retriever Query Engine.</p><p>
This query engine can query both a SQL database as well as a vector database. It will first decide whether it needs to query the SQL database or vector store. If it decides to query the SQL database, it will also decide whether to augment information with retrieved results from the vector store. We use the <a href="https://docs.llamaindex.ai/en/stable/examples/vector_stores/LanternAutoRetriever.html#define-vectorindexautoretriever">VectorIndexAutoRetriever</a> to retrieve results.</p>
</blockquote>

Using the `nl_sql_engine` and `retriever_query_engine` engines with the [`SQLAutoVectorQueryEngine`](https://docs.llamaindex.ai/en/stable/examples/query_engine/SQLAutoVectorQueryEngine.html#define-sqlautovectorqueryengine) requires only a few lines of code. For this query engine to determine whether to issue a SQL query or vector search to ClickHouse, we need to provide it with context (2) as to what information these engines provide. This is provided by creating a [`QueryEngineTool`](https://docs.llamaindex.ai/en/stable/examples/query_engine/RetrieverRouterQueryEngine.html#define-query-engine-and-tool-for-these-indices) from each with a description detailing its purpose.

<pre style="font-size: 14px;"><code class="hljs language-python"><span class="hljs-comment"># (1) create engines as above</span>
vector_auto_retriever = VectorIndexAutoRetriever(
    vector_index, vector_store_info=vector_store_info, similarity_top_k=<span class="hljs-number">10</span>,
    prompt_template_str=CLICKHOUSE_VECTOR_STORE_QUERY_PROMPT_TMPL, llm=OpenAI(model=<span class="hljs-string">"gpt-4"</span>),
    <span class="hljs-comment"># require context to be of a specific length</span>
    vector_store_kwargs={<span class="hljs-string">"where"</span>: <span class="hljs-string">f"length &gt;= 20"</span>}
)

retriever_query_engine = RetrieverQueryEngine.from_args(vector_auto_retriever, llm=OpenAI(model=<span class="hljs-string">"gpt-4"</span>))

<span class="hljs-comment"># (2) provide descriptions of each engine to assist SQLAutoVectorQueryEngine</span>
sql_tool = QueryEngineTool.from_defaults(
   query_engine=nl_sql_engine,
   description=(
       <span class="hljs-string">"Useful for translating a natural language query into a SQL query over"</span>
       <span class="hljs-string">f" a table: <span class="hljs-subst">{stackoverflow_table}</span>, containing the survey responses on"</span>
       <span class="hljs-string">f" different types of technology users currently use and want to use"</span>
   ),
)
vector_tool = QueryEngineTool.from_defaults(
   query_engine=retriever_query_engine,
   description=(
       <span class="hljs-string">f"Useful for answering semantic questions abouts users comments and posts"</span>
   ),
)

<span class="hljs-comment"># (3) engine to query both a SQL database as well as a vector database</span>
sql_auto_vector_engine = SQLAutoVectorQueryEngine(
   sql_tool, vector_tool, llm=OpenAI(model=<span class="hljs-string">"gpt-4"</span>)
)

response = sql_auto_vector_engine.query(<span class="hljs-string">"What are people's opinions on the web technology that people at companies with less than 100 employees want to work with?"</span>)

<span class="hljs-built_in">print</span>(<span class="hljs-built_in">str</span>(response))
</code></pre>

With this, we can now answer richer questions such as “What are people’s opinions on the web technology that people at companies with less than 100 employees want to work with?” which require both data sources.

<blockquote style="font-size: 14px;">
<p>You’ll notice we’ve recreated our <code>VectorIndexAutoRetriever</code> with the parameter <code>vector_store_kwargs={"where": f"length &gt;= 20"}</code> at (1). This adds an additional where filter to any vector queries to ClickHouse, restricting results to comments with at least 20 terms. Testing showed this improved the quality of results significantly.</p>
</blockquote>

When we run this notebook, the logs are revealing. Initially, we can see an LLM is used to assess the type of question being asked. This establishes we need to query against the surveys. This is achieved using LlamaIndex’s [router functionality](https://docs.llamaindex.ai/en/stable/examples/retrievers/router_retriever.html), capable of choosing between our two different retriever engines by invoking ChatGPT with the descriptions provided above:

```bash
INFO:llama_index.core.query_engine.sql_join_query_engine:> Querying SQL database: The first choice is about translating natural language queries into SQL queries over a survey table. This could be used to analyze the responses of people at companies with less than 100 employees about the web technology they want to work with.
```

ChatGPT is, in turn, used to obtain a SQL query. Note the filter on `organization_size` and how the LLM has restricted this to the correct values (thanks to our use of an Enum):

```sql
SELECT
    arrayJoin(web_framework_want_to_work) AS web_tech,
    COUNT(*) AS count
FROM surveys
WHERE organization_size IN (1, 2, 3, 4)
GROUP BY web_tech
ORDER BY count DESC
LIMIT 5
```

This query is executed against ClickHouse, which identifies React.js as the web technology most users want to work with at smaller companies:

```bash
Based on the survey results, the top five web technologies that people at companies with less than 100 employees want to work with are React.js (9765 votes), Vue.js (6821 votes), Express (4657 votes), Angular (4415 votes), and jQuery (3397 votes).
```

The results of this query are then used to expand the original question, again using our LLM via a [SQLAugmentQueryTransform](https://docs.llamaindex.ai/en/stable/api_reference/query/query_engines/sql_join_query_engine.html#llama_index.core.query_engine.sql_join_query_engine.SQLAugmentQueryTransform) behind the scenes:

```bash
What are the reasons people at companies with less than 100 employees want to work with React.js, Vue.js, Express, Angular, and jQuery?
```

The above question will be embedded using our `sentence-transformers/all-MiniLM-L6-v2` model. This embedding will again be used to query ClickHouse via the `ClickHouseVectorStore` to identify relevant Hacker News comments to provide context and answer our question.

```none
People at smaller companies may prefer to work with React.js, Vue.js, Express, Angular, and jQuery for a variety of reasons. These technologies are widely recognized and supported by large communities, which can be advantageous for troubleshooting and learning new methods. They can also streamline and structure the development process. Furthermore, familiarity with these technologies can be a career asset for developers, as they are frequently sought after in job listings. However, the choice of technology may also be influenced by the project's specific requirements and limitations.
```

## Something prettier with Streamlit

While the above provides the mechanics of our application, users expect something a little more visually engaging than a notebook! For building applications quickly, we’re fans of [Streamlit](https://streamlit.io/). This allows users to build applications in just Python, turning data scripts into shareable web apps in a few minutes.

For an introduction to using StreamLit with ClickHouse, the following video from Data Mark should get you started:

<iframe width="768" height="432" src="https://www.youtube.com/embed/2Tra0DU1tfM?si=ijIPQyu7ISIiAPyq" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>

<p></p>
For our application, we really just need a ChatBot interface where users can enter questions. As the above code needs an [API key for OpenAI](https://platform.openai.com/account/api-keys), the user should also be able to provide this through the interface. Additionally, since we found that filtering Hacker News posts to those above a certain length improved the quality of the context, we also ideally wanted to provide this as an optional filter the user could modify. Finally, additional filters on post score and date were desirable since we might later expand the dataset to surveys beyond 2021.

Fortunately, Streamlit already has an [excellent gallery of example applications](https://streamlit.io/gallery?category=llms), with even one for [LlamaIndex, which takes only 43 lines of code!](https://blog.streamlit.io/build-a-chatbot-with-custom-data-sources-powered-by-llamaindex/) By combining a few other relevant examples [[1][2]](https://llm-examples.streamlit.app/), familiarizing ourselves with the concepts behind [Streamlit caching](https://docs.streamlit.io/library/advanced-features/caching), and incorporating our `SQLAutoVectorQueryEngine` we can achieve something quite usable in 50 lines of Python! 

<pre style="font-size: 14px;"><code class="hljs language-python">st.set_page_config(
   page_title=<span class="hljs-string">"Get summaries of Hacker News posts enriched with Stackoverflow survey results, powered by LlamaIndex and ClickHouse"</span>,
   page_icon=<span class="hljs-string">"????????"</span>, layout=<span class="hljs-string">"centered"</span>, initial_sidebar_state=<span class="hljs-string">"auto"</span>, menu_items=<span class="hljs-literal">None</span>)
st.title(<span class="hljs-string">"????HackBot powered by LlamaIndex ???? and ClickHouse ????"</span>)
st.info(
   <span class="hljs-string">"Check out the full [blog post](https://clickhouse.com/blog/building-a-hackernews-chat-bot-with-llama-index-with-clickhouse/) for this app"</span>,
   icon=<span class="hljs-string">"????"</span>)
st.caption(<span class="hljs-string">"A Streamlit chatbot ???? for Hacker News powered by LlamaIndex ???? and ClickHouse ????"</span>)

<span class="hljs-comment"># Llama Index code here</span>

<span class="hljs-comment"># identify the value ranges for our score, length and date widgets</span>
<span class="hljs-keyword">if</span> <span class="hljs-string">"max_score"</span> <span class="hljs-keyword">not</span> <span class="hljs-keyword">in</span> st.session_state.keys():
   client = clickhouse()
   st.session_state.max_score = <span class="hljs-built_in">int</span>(
       client.query(<span class="hljs-string">"SELECT max(post_score) FROM default.hackernews_llama"</span>).first_row[<span class="hljs-number">0</span>])
   st.session_state.max_length = <span class="hljs-built_in">int</span>(
       client.query(<span class="hljs-string">"SELECT max(length) FROM default.hackernews_llama"</span>).first_row[<span class="hljs-number">0</span>])
   st.session_state.min_date, st.session_state.max_date = client.query(
       <span class="hljs-string">"SELECT min(toDate(time)), max(toDate(time)) FROM default.hackernews_llama WHERE time != '1970-01-01 00:00:00'"</span>).first_row


<span class="hljs-comment"># set the initial message on load. Store in the session.</span>
<span class="hljs-keyword">if</span> <span class="hljs-string">"messages"</span> <span class="hljs-keyword">not</span> <span class="hljs-keyword">in</span> st.session_state:
   st.session_state.messages = [
       {<span class="hljs-string">"role"</span>: <span class="hljs-string">"assistant"</span>, <span class="hljs-string">"content"</span>: <span class="hljs-string">"Ask me a question about opinions on Hacker News and Stackoverflow!"</span>}]


<span class="hljs-comment"># build the sidebar with our filters</span>
<span class="hljs-keyword">with</span> st.sidebar:
   score = st.slider(<span class="hljs-string">'Min Score'</span>, <span class="hljs-number">0</span>, st.session_state.max_score, value=<span class="hljs-number">0</span>)
   min_length = st.slider(<span class="hljs-string">'Min comment Length (tokens)'</span>, <span class="hljs-number">0</span>, st.session_state.max_length, value=<span class="hljs-number">20</span>)
   min_date = st.date_input(<span class="hljs-string">'Min comment date'</span>, value=st.session_state.min_date, min_value=st.session_state.min_date,
                            max_value=st.session_state.max_date)
   openai_api_key = st.text_input(<span class="hljs-string">"Open API Key"</span>, key=<span class="hljs-string">"chatbot_api_key"</span>, <span class="hljs-built_in">type</span>=<span class="hljs-string">"password"</span>)
   openai.api_key = openai_api_key
   <span class="hljs-string">"[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"</span>
   <span class="hljs-string">"[View the source code](https://github.com/ClickHouse/examples/blob/main/blog-examples/llama-index/hacknernews_app/hacker_insights.py)"</span>


<span class="hljs-comment"># grab the users OPENAI api key. Don’t allow questions if not entered.</span>
<span class="hljs-keyword">if</span> <span class="hljs-keyword">not</span> openai_api_key:
   st.info(<span class="hljs-string">"Please add your OpenAI API key to continue."</span>)
   st.stop()
<span class="hljs-keyword">if</span> prompt := st.chat_input(placeholder=<span class="hljs-string">"Your question about Hacker News"</span>):
   st.session_state.messages.append({<span class="hljs-string">"role"</span>: <span class="hljs-string">"user"</span>, <span class="hljs-string">"content"</span>: prompt})
<span class="hljs-comment"># Display the prior chat messages</span>
<span class="hljs-keyword">for</span> message <span class="hljs-keyword">in</span> st.session_state.messages:
   <span class="hljs-keyword">with</span> st.chat_message(message[<span class="hljs-string">"role"</span>]):
       st.write(message[<span class="hljs-string">"content"</span>])

<span class="hljs-comment"># If last message is not from assistant, generate a new response</span>
<span class="hljs-keyword">if</span> st.session_state.messages[-<span class="hljs-number">1</span>][<span class="hljs-string">"role"</span>] != <span class="hljs-string">"assistant"</span>:
   <span class="hljs-keyword">with</span> st.chat_message(<span class="hljs-string">"assistant"</span>):
       <span class="hljs-keyword">with</span> st.spinner(<span class="hljs-string">"Thinking..."</span>):
           <span class="hljs-comment"># Query our engine for the answer and write to the page</span>
           response = <span class="hljs-built_in">str</span>(get_engine(min_length, score, min_date).query(prompt))
           st.write(response)
           st.session_state.messages.append({<span class="hljs-string">"role"</span>: <span class="hljs-string">"assistant"</span>, <span class="hljs-string">"content"</span>: response})
</code></pre>

We recommended the Streamlit [tutorials](https://docs.streamlit.io/get-started/tutorials) and [examples](https://streamlit.io/gallery?category=llms&ref=blog.streamlit.io) to help you understand the concepts here, especially around [caching](https://docs.streamlit.io/library/advanced-features/caching). Our final application can be found [here](https://github.com/ClickHouse/examples/blob/main/blog-examples/llama-index/hacknernews_app/hackbot.py).

<a target="_blank" href="/uploads/hackbot_v6_636ac1edf0.gif"><img src="/uploads/hackbot_v6_636ac1edf0.gif"/></a>

## A few observations

The above application represents a reasonably simple RAG pipeline that requires very little code. Despite this, the pipeline can be quite fragile, with multiple steps that can fail, causing the use of the incorrect decision branch or an answer to not be returned. We've only sampled a tiny percentage of the possible questions and not tested the app's ability to respond across a diverse set.

Building an LLM-based application for a proof of concept or demo is very different from deploying something robust and reliable to production. In our limited experience, this is extremely challenging, with introspection of the pipeline particularly tricky. Be wary of any blogs or content that suggest otherwise! Obtaining predictable behavior from something that has inherent randomness requires a little more than a few hundred lines of Python and a few hours of work.

To overcome this, we see enormous value in anything that provides observability into RAG pipelines, allowing issues to be diagnosed and test sets to be easily evaluated. We're therefore extremely encouraged to see the recent product developments by [LlamaIndex](https://www.llamaindex.ai/enterprise) and [LangChain](https://www.langchain.com/langsmith), and we look forward to trying these products.

With respect to our above application, feel free to experiment and enhance it. There are some obvious areas of improvement. For example, the application has no memory of previously answered questions, not considering these as context for future questions. This is easily added through the concept of [memory](https://docs.llamaindex.ai/en/stable/api_reference/memory.html) in LlamaIndex. Additionally, adding survey results from other years seems like a logical addition. Being able to ask questions such as "How have people's opinions changed on the database they most wanted to work with in 2019 vs 2023?"

## Conclusion

Our ongoing investment in supporting vector search consists of a few parallel tracks:

* Further improving the performance of linear scans e.g. improved [vectorization of distance functions](https://github.com/ClickHouse/ClickHouse/pull/60202)
* Moving our support for approximate techniques, such as HNSW, from experimental to production
* Investment in the wider ecosystem for which Vector search is used

In this blog, we’ve explored an improvement that falls into the last of these - ClickHouse’s integration with LlamaIndex, building an example application to answer questions about people’s opinions on technologies based on Hacker News posts and Stack Overflow survey results.

Finally, if you’re curious as to what people are saying about ClickHouse (with the caveat that our posts go up to 2021 only)…

![clickhouse_hackbot.png](https://clickhouse.com/uploads/clickhouse_hackbot_e6360bb8f4.png)