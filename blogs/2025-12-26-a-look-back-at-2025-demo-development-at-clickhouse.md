---
title: "A look back at 2025 demo development at ClickHouse"
date: "2025-12-26T09:13:30.305Z"
author: "Lionel Palacin"
category: "Engineering"
excerpt: "Have a look at some of the most notable demos we built this year, and how they help people feel the speed of ClickHouse through real, hands-on examples."
---

# A look back at 2025 demo development at ClickHouse

As the year comes to an end and things slow down a bit, it feels like a good moment to zoom out and look back at the work we did as a team. I spend a lot of my time at ClickHouse working on demos, something I really enjoy, and I thought I would do a review of the most significant demos we built this year.

That idea was reinforced by a conversation I had with my colleague Tom Schreiber before the holidays. He [spends a lot of his time benchmarking ClickHouse](https://clickhouse.com/blog/what-really-matters-for-performance-lessons-from-a-year-of-benchmarks) and he shared a reflection that stuck with me:

> Benchmarks are great for measuring and understanding how fast ClickHouse is, but demos help people actually feel and experience that speed.

That feels very true. Nothing beats a real-world example that shows how ClickHouse performance makes it possible to build impressive applications at scale. And it's not just us saying this. Customers like Tesla, which has ingested [over a quadrillion rows into ClickHouse](https://clickhouse.com/blog/how-tesla-built-quadrillion-scale-observability-platform-on-clickhouse), or GitLab, [which serves sub-second queries to tens of millions of users](https://clickhouse.com/blog/how-gitlab-uses-clickhouse-to-scale-analytical-workloads), would likely agree.

That's a common theme across the demos featured in this post, and a good place to start looking at what we built this year.

## StockHouse: Real-time market analytics

[StockHouse](https://stockhouse.clickhouse.com/) is a real-time market analytics application built on live stock and crypto data from [Massive APIs](https://massive.com/). It streams ticks over WebSocket APIs, ingests them into ClickHouse, and renders a dashboard built using [Perspective](https://perspective-dev.github.io/) that updates within milliseconds.


<video autoplay="0" muted="1" loop="1" controls="1">
  <source src="https://clickhouse.com/uploads/stockhouse_video_e56eb55db3.mp4" type="video/mp4" />
</video>

> What I love about this demo is how tangible ClickHouse speed becomes. When prices move, charts move with them, without buffering or visible lag.

From an engineering perspective, StockHouse shows how little configuration is needed to ingest real-time data into ClickHouse. [The Go ingester](https://clickhouse.com/blog/building-stockhouse#ingester-in-go) connects directly to Massive's WebSocket APIs and writes batches using the native ClickHouse interface. There is no complex pipeline or external stream processor involved.

On the query side, [the demo relies on materialized views](https://clickhouse.com/blog/building-stockhouse#pre-aggregation-with-materialized-views). Raw ticks are stored as-is, but the queries that feed the live UI read from pre-aggregated tables. Daily open, close, volume, and last update timestamps are computed at insert time, so dashboard queries stay simple and fast.

The pattern is straightforward: raw events for flexibility, materialized views for speed, and queries that consistently run in a few milliseconds. This is a common ClickHouse design, but seeing it applied to live market data makes the tradeoffs very clear.

StockHouse is a good reference for anyone building real-time dashboards, whether the data comes from financial markets, sensors, or observability pipelines. And it's [open source](https://github.com/ClickHouse/stockhouse/).

## ClickGems: open analytics for the RubyGems ecosystem

[ClickGems](https://clickgems.clickhouse.com/) started as a simple request from the [Ruby Central team](https://rubycentral.org/). They wanted an easier way for the community to explore RubyGems download statistics using SQL. [After loading the data](https://clickhouse.com/blog/announcing-ruby-gem-analytics-powered-by-clickhouse) into our [SQL Playground](https://sql.clickhouse.com/?query_id=HVMKR3JXFT4DA8NMAPGXKM), it quickly became clear that it deserved a dedicated interface.

<video autoplay="0" muted="1" loop="1" controls="1">
  <source src="https://clickhouse.com/uploads/Click_Gems_video_5364337b67.mp4" type="video/mp4" />
</video>

[ClickGems is essentially a RubyGems-focused version of ClickPy.](https://clickhouse.com/blog/announcing-clickgems) It uses the same codebase and the same approach: expose large public datasets, back them with ClickHouse, and let users explore them through fast, transparent SQL-powered visualizations. This approach has proven to scale well. [ClickPy](https://clickpy.clickhouse.com/) crossed the **two trillion row mark this year**, and ClickGems benefits from the same design choices.

> What I love about this demo is the collaboration. Ruby Central helped with data ingestion and validation, Metabase enabled shareable charts, and together they made ClickGems useful in practice.

From a technical standpoint, ClickGems reinforces a pattern we use across demos. Data is ingested in raw form, then materialized views aggregate it into shapes that match common queries. Each chart is backed by a SQL query that users can inspect and run themselves. There is no hidden logic between the visualization and the database.

ClickGems is now a free analytics site for more than 200,000 gems, covering years of download history. It also serves as a [practical example](https://github.com/ClickHouse/clickpy/tree/clickgems) of how ClickHouse can power public, read-heavy analytics workloads at scale.

## AgentHouse: querying data with natural language

[AgentHouse](https://accounts.google.com/) explores a different angle. Instead of building another dashboard, we wanted to show how ClickHouse can act as a backend for [agentic applications](https://clickhouse.com/ai).

<video autoplay="0" muted="1" loop="1" controls="1">
  <source src="https://clickhouse.com/uploads/agenthouse_v3_2b08d0a474.mp4" type="video/mp4" />
</video>

---

## Get started today

Interested in seeing how ClickHouse works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-29-get-started-today-sign-up&utm_blogctaid=29)

---

AgentHouse is built on top of [LibreChat](https://www.librechat.ai/) and ClickHouse, using [ClickHouse MCP server](https://github.com/ClickHouse/mcp-clickhouse) to query real datasets hosted in ClickHouse Cloud. Users can ask questions using natural language, see the generated SQL, and get instant answers based on real data.

> What I love about this demo is how clearly it shows what agentic applications can look like in practice. There is no abstraction or mock setup. The LLM generates SQL, runs it against live data in ClickHouse, and reasons over real results, which makes the architecture easy to understand.

AgentHouse uses the same datasets available in our [SQL Playground](https://sql.clickhouse.com/), including RubyGems, PyPI, GitHub, and Hacker News. This makes it a safe environment to explore how natural language interfaces behave on large, real-world datasets.

For us, AgentHouse is less about replacing SQL and more about expanding how people interact with data. It shows how ClickHouse fits into LLM-driven systems without giving up transparency, performance, or control.

## ClickStack demo: Observability on ClickHouse, end to end

We built the [ClickStack demo](https://play-clickstack.clickhouse.com/search) to give users an easy way to experience what observability on top of ClickHouse actually looks like. The idea is to put yourself in the role of an SRE and use the stack to [investigate a real application incident](https://clickhouse.com/docs/use-cases/observability/clickstack/getting-started/remote-demo-data), using the same workflows you would rely on in production.

The demo [is based on the official OpenTelemetry demo](https://github.com/ClickHouse/opentelemetry-demo), which simulates a microservices-based e-commerce application with traffic generated by a load generator. All services are instrumented with OpenTelemetry and emit logs, traces, metrics, and session data through a standard OTel Collector into ClickHouse.

<video autoplay="0" muted="1" loop="1" controls="1">
  <source src="https://clickhouse.com/uploads/Click_Stack_video_751cbef773.mp4" type="video/mp4" />
</video>

The dataset contains roughly 40 hours of telemetry and is replayed daily with timestamps shifted into the current time window. All signals are stored as wide events in ClickHouse and explored through HyperDX, without separate backends for logs, metrics, or traces.

> What I love about this demo is that it mirrors how an SRE actually works: starting from a vague symptom, narrowing it down through logs, confirming behavior with traces and metrics, and validating impact from the user’s perspective.


## Special mention to Alexey

Alexey Milovidov, ClickHouse CTO and co-founder, loves adopting new datasets and building demos to make it easy to explore them, using ClickHouse, always, obviously.

This year, he extended a visualization tool he originally built for air traffic data and used it for several new demos. [One of the first ](https://clickhouse.com/blog/fsq)was based on Foursquare data, showing places such as shops, restaurants, parks, playgrounds, and monuments on a map.

![fsq-screenshot.png](https://clickhouse.com/uploads/fsq_screenshot_f3955a7908.png)

Later, Alexey explored an unusual dataset derived from airplane telemetry to infer weather conditions. The data was ingested into ClickHouse and the [experiments were reproduced end to end](https://clickhouse.com/blog/planes-weather).

![weather-screenshots.png](https://clickhouse.com/uploads/weather_screenshots_450ade09a4.png)

[He then moved on to a dataset focused on bird observations](https://clickhouse.com/blog/birds), which was again ingested into ClickHouse and visualized on [adbs.exposed](https://adsb.exposed/?dataset=Birds&zoom=5&lat=52.2278&lng=5.0977).

![birds-screenshot.png](https://clickhouse.com/uploads/birds_screenshot_66eab44304.png)

And that still was not enough. A few weeks before the end of the year, Alexey [launched a new website](https://clickhouse.com/blog/velocity) to track GitHub activity across the ClickHouse team.

![velocity-screenshot.png](https://clickhouse.com/uploads/velocity_screenshot_ad779dfae3.png)

Thanks, Alexey, for all the demos this year.

## Why these demos matter

Looking back, these demos cover very different use cases, from real-time dashboards to public analytics sites to agent-driven interfaces. But they all rely on the same core ideas. Store raw data, shape it with materialized views, keep queries explicit, and let performance simplify the rest of the system.

All of these demos are built in the open. The code, schemas, and queries are there to be read, reused, and adapted. They are not reference architectures on slides, but working systems that developers can take apart and build on for their own applications.
That openness matters, especially when combined with real data and real scale. As I discussed with Tom in the introduction, demos make it possible to feel the speed and scale that ClickHouse allows us to operate at. You can see queries return in milliseconds, watch dashboards update live, and explore datasets that would be impractical to handle with many other systems.

For me, this is where demos complement benchmarks. 

We will keep building more of them in 2026.