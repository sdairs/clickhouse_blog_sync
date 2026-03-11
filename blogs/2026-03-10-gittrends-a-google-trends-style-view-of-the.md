---
title: "GitTrends: A Google Trends style view of the GitHub ecosystem"
date: "2026-03-10T15:21:01.574Z"
author: "Lionel Palacin"
category: "Engineering"
excerpt: "Search and uncover technology trends across 10 billion GitHub events in real time."
---

# GitTrends: A Google Trends style view of the GitHub ecosystem

GitHub generates a constant stream of issues, pull requests, and comments. Those are known as Github events. Over time, these billions of events capture the complete lifecycle of technology: how frameworks, libraries, and tools rise and fade. But capturing that immense data stream and turning it into a real-time trends analyzer is a challenge. 

**GitTrends** make this possible. It is a new open-source demo application that works like a **specialized Google Trends for the tech world**, letting you search and compare any topic, technology, or keyword trends across **over 10 billion GitHub events in real time**. 

It is now available at [https://gittrends.clickhouse.com](https://gittrends.clickhouse.com)

> GitTrends is a public demo built to showcase ClickHouse's Full Text Search capabilities. It is fully functional, but may be missing some features or have the occasional bug. 

## How can you use GitTrends? 

Type a search term into GitTrends and instantly see how many times it was mentioned across issues, pull requests, and comments in every GitHub repository. This gives you an overview of a technology's popularity over time, the repositories driving the conversation, the developers most actively talking about it, and the actual issues and pull requests where the term appears.

![gittrend-1.png](https://clickhouse.com/uploads/gittrend_1_f90a94c48d.png)

But GitTrends gets really interesting when you start comparing.

### Compare tech adoption 

Search and compare mention trends for any keywords, exactly like Google Trends but built on the world's most relevant data source for open-source technology. Compare `ClickHouse vs Druid` to see how two analytics databases have traded momentum over time, or track `Claude vs OpenAI` to watch the AI landscape shift in real developer conversations.

![gittrends-21.png](https://clickhouse.com/uploads/gittrends_21_d1284e2bdc.png)

### Identify Ecosystems

Identify the top repositories driving the conversation around any topic. Is ClickHouse discussed mostly in its own ecosystem, or is it bleeding into data engineering and observability projects? Is OpenAI mentioned across a broad range of repos while Claude is concentrated in a handful? 

Knowing where a technology lives tells you as much as knowing how popular it is.

![gittrends-31.png](https://clickhouse.com/uploads/gittrends_31_cca45cbdc2.png)

### Drill into the Source

Move from a high-level trend to the actual conversations behind it. Select any repository and explore its underlying activity: the most active contributors, and the most mentioned issues and PRs driving the trend.

![gittrends-41.png](https://clickhouse.com/uploads/gittrends_41_81773597ae.png)

## Full Text Search at Scale

GitTrends is built around a simple idea: search any term in real time, across nearly 10 billion GitHub events with no data transformation. Rather than querying pre-computed answers, you index the raw text and search it directly at query time. That's the all promise behind the [new Full text search feature](https://clickhouse.com/blog/full-text-search-ga-release) recently released in ClickHouse. [Simply build a text index on a text column](https://clickhouse.com/docs/engines/table-engines/mergetree-family/textindexes) and use full text search.

What makes ClickHouse particularly powerful here is that Full Text Search and aggregation live in the same engine. A single query can search raw text and aggregate results in one pass, with no joins across systems, no data movement, and no latency penalty. That combination is what makes the experience feel instant rather than just fast.

The GitHub events dataset, nearly 10 billion rows of issues, pull requests, and comments, is a deliberate stress test. GitTrends still delivers fast search across all of it.

To highlight the performance of the new Full text search index, GitTrends includes a live query performance comparison. For any search, you can toggle between using Full Text Search, Bloom Filter and a Full Table Scan and watch the difference play out in real time. 

It is the clearest demonstration of what the right index buys you at scale.

## Look under the hood

GitTrends is fully open and built to be explored at every layer.

### How is the data ingested?

We have been ingesting the Github events dataset for a while now to make the dataset available in our SQL Playground for anyone to query the data using SQL and also described in this [page](https://clickhouse.com/demos/explore-github-with-clickhouse-powered-real-time-analytics) how you can query the data to build cool analysis.

The script to ingest data in ClickHouse is available [here](https://github.com/ClickHouse/sql.clickhouse.com/blob/main/load_scripts/github_events/ingest.sh). 

### What SQL query is running behind each chart?

Every chart in GitTrends is backed by a real query. Click the SQL button on any chart to open it in the SQL playground, where you can inspect it, edit it, and run it yourself.

<pre><code run='false' type='click-ui' language='sql' runnable='true' view='table'  play_link='https://sql.clickhouse.com/?query_id=TWAMA73L7QFQUY6AKWSVJL' show_statistics='true'>
SELECT
  toStartOfDay(created_at) AS bucket,
  count() AS count
FROM github.github_events
WHERE
  event_type IN ('IssueCommentEvent','IssuesEvent','PullRequestEvent','PullRequestReviewCommentEvent','PullRequestReviewEvent')
  AND hasAllTokens(body, 'clickhouse')
  AND created_at >= (now() - toIntervalMonth(1))
  AND 1=1
GROUP BY bucket
ORDER BY bucket ASC
SETTINGS
    enable_parallel_replicas = 1,
    enable_full_text_index = 1,
    use_skip_indexes = 1,
    query_plan_direct_read_from_text_index = 1,
    use_skip_indexes_on_data_read = 1
</code></pre>

Each search type, Full Text Search, Bloom Filter, and Full Table Scan, has its own query so you can see exactly what changes under the hood.

### How is the application built?

Want to deploy GitTrends locally or build something similar on your own dataset? The full source code and deployment instructions are available on GitHub.

Give the demo a try at <https://gittrends.clickhouse.com> and share with us [any feedback](https://github.com/ClickHouse/gitTrends/issues/new).
