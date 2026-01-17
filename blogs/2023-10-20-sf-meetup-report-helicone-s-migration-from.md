---
title: "SF Meetup Report: Helicone's Migration from Postgres to ClickHouse for Advanced LLM Monitoring"
date: "2023-10-20T12:30:04.394Z"
author: "Elissa Weve"
category: "Community"
excerpt: "Discover how Helicone transformed their LLM monitoring with ClickHouse, processing 3 million requests daily and slashing query times from 100 seconds to milliseconds."
---

# SF Meetup Report: Helicone's Migration from Postgres to ClickHouse for Advanced LLM Monitoring

<iframe width="764" height="430" src="https://www.youtube.com/embed/qflVFy6Fqm8" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>

<br/>

On August 8th, 2023, ClickHouse hosted their "ClickHouse and AI - A Summer Meetup" in San Francisco. We had the pleasure of hearing from Justin Torre, the CEO and co-founder of Helicone. [Helicone.ai](https://www.helicone.ai/) is an open-source platform designed for AI observability, offering monitoring, logging, and tracing for Large Language Models (LLMs) applications right out of the box.

Leveraging ClickHouse as a foundational component of their backend, they handle an impressive 3 million requests daily. ClickHouse enables real-time updates to their dashboards, providing users with immediate visibility into critical metrics like errors and active user counts. 

## Helicone’s Rise in the World of LLMs ##
Justin spoke about the sudden popularity and surge in LLM usage, with startups rapidly integrating such models into their services. He touched upon Helicone’s inception – initially focusing on a product called TableTalk that allowed users to interact with databases through OpenAI. They quickly realized the need for more extensive monitoring of these LLMs, leading to the creation of Helicone. Its success was driven by an easy integration strategy. By simply adding two lines of code, developers can visualize all their activities in Helicone such as real-time stats, request logs, and even error details.

![Helicone2.png](https://clickhouse.com/uploads/Helicone2_0ff1e3cc7f.png)

## The Struggle with Scaling Postgres and the Migration to ClickHouse Cloud ##

Helicone initially launched using Postgres, however this quickly presented a range of challenges, particularly when attempting to scale their dashboard features. Justin explained "we were using Postgres and Postgres just wasn't scaling for those nice dashboards. In order to get these nice dashboards, you need to do all these aggregation calls. Aggregations were taking more than 30 seconds and things were just timing out."  AI applications demand flexible data manipulation, where users need the capability to filter, segment, and dissect data dynamically.

Based on a recommendation they decided to try ClickHouse, which immediately gave impressive results. Justin explained "I did a benchmark where I copied a ton of data and then did an aggregation query and I was like… this is fast!" The appeal wasn't just about speed, but also the fact that ClickHouse is open-source, which aligns with Helicone's core values. 

The migration to ClickHouse had its share of complexities, especially around the syncing between Postgres views and ClickHouse tables. They landed on a dual-insertion approach, populating both ClickHouse and Postgres simultaneously. For newer tables and views, they use pgv2cht, which is an open-source tool they created. 

![Helicone4.png](https://clickhouse.com/uploads/Helicone4_891ec33a4a.png)

After migrating to ClickHouse Helicone experienced a drastic optimization in dashboard query performance. What previously took over 100 seconds was now executed in just 0.5 seconds. Feedback from their customers was immediate, with many commenting, "Hey, we noticed the dashboard is faster!"

![Helicone3.png](https://clickhouse.com/uploads/Helicone3_1de45e355d.png)

## Conclusion ##
Justin Torre shared Helicone's transition from its initial product, TableTalk, to its current focus on LLM observability. Their rapid growth led to scaling challenges with Postgres. However, the switch to ClickHouse transformed their performance, slashing dashboard query times. As Justin explained “It was crazy. We went from query times of over 100 seconds to just 0.5 seconds. We did so many different types of indexes and testing. It was nuts." 

This migration not only showcased ClickHouse's efficiency but also aligns with Helicone's commitment to open-source. Justin appreciated the support from the ClickHouse team, especially via the chat box in ClickHouse Cloud, which helped solve issues efficiently.

## More Details ##
- This talk was given at the [ClickHouse Community Meetup](https://www.meetup.com/clickhouse-silicon-valley-meetup-group/events/294472987/) in SF on August 8th, 2023
- The presentation materials are available [on GitHub](https://github.com/ClickHouse/clickhouse-presentations/tree/master/meetup81)
