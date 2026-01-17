---
title: "Scaling craft coffee: How ClickHouse powers Artly’s barista bots"
date: "2025-08-19T14:07:27.103Z"
author: "ClickHouse Team"
category: "User stories"
excerpt: "\"ClickHouse has a lot of great features. It’s very flexible and great for our use cases. The pricing is also very affordable compared to other alternatives.\"  - Tong Liu, Principal Software Architect"
---

# Scaling craft coffee: How ClickHouse powers Artly’s barista bots

Scaling a coffee business has always meant compromise. Big coffee chains can deliver consistency, but often at the expense of flavor and craft. Independent shops serve up exceptional quality, but rarely grow beyond a handful of locations.

[Artly](https://artly.coffee/) wants to change that. The Seattle-based startup builds [robotic baristas](https://www.artlybaristabot.com/)—fully autonomous machines that can make world-class coffee with the consistency and precision of industrial automation. "Our mission is to scale high-quality coffee to multiple locations," says Tong Liu, Principal Software Architect at Artly.

At the heart of Artly's system is a fine blend of what Tong calls "human craft and robot precision." Their barista bots were trained under Chief Coffee Officer, [Joe Yang](https://artly.coffee/pages/roasting-team), the 2023 U.S. Brewers Cup champion and 2024 Latte Art Champion. The robots memorize recipes and parameters for a full menu of custom drinks, from specialty espresso beverages like cappuccinos and cortados to matcha and non-caffeinated refreshers. They even pour latte art.

![artly-blog-1.png](https://clickhouse.com/uploads/artly_blog_1_b567f91eef.png)
<div style="text-align: center; font-style: italic; margin-top: 12px;">Artly Coffee’s barista bots can pour a full menu of espresso and other customizable drinks.</div>

But making the perfect cup goes beyond milk and mechanics. It's also a massive data challenge. As Tong explained at a [May 2025 ClickHouse meetup in Seattle](https://www.youtube.com/watch?v=CQKClMHm2qs), every robot generates a steady stream of telemetry and sales data that must be processed, analyzed, and acted on in near real time. As Artly expands---from retail locations in Seattle and San Francisco to partnerships with MUJI and Tesla to pop-ups at Salesforce and Microsoft---managing that data becomes just as important as the coffee itself.

## From beans to bytes

For a trained barista, making one good latte is second nature. What’s exponentially harder, Tong says, is making 10,000 great ones, across dozens of locations, in real time. "If you want every cup to be perfect, you have to make a lot of adjustments," he says. 

That’s where Artly’s data infrastructure comes in. Each barista bot collects hundreds of metrics, which the team relies on to deliver consistently great coffee at scale. 

The system runs on a hybrid cloud architecture across AWS and GCP. Each robot connects to a centralized backend where telemetry, operational logs, and sales data are stored in services like DynamoDB, S3, Elasticsearch, and ClickHouse. On the frontend, mobile and web apps handle customer ordering and remote robot management.

![artly-blog-2.png](https://clickhouse.com/uploads/artly_blog_2_72a372b48c.png)
<div style="text-align: center; font-style: italic; margin-top: 12px;">Cloud architecture powering Artly’s barista bots, analytics, remote management, and customization.</div>

Since their first demo five years ago, Artly has expanded the bot’s repertoire from basic Americanos to a fully customizable menu. Customers can tweak syrup levels, milk type, sweetness, hotness, and even choose their latte art. Operators monitor performance remotely, push updates, and troubleshoot issues. The system can even self-correct: if a metric drifts, it sends an alert and adjusts automatically before quality slips.

Managing that level of complexity takes a data layer that’s fast, flexible, and easy to maintain, especially for a startup like Artly. "We’re a very small team, so we need something that’s low-maintenance, scalable, and affordable," Tong says.

## The limits of Elasticsearch

In the early days, Artly relied on a combination of Elasticsearch and Kibana. Tong had used the stack before and could get it up and running quickly. It handled basic aggregations well, tracking total orders, total items, per-store breakdowns, and revenue. Kibana took care of visualizations, and the team could slice data by location or timeframe without much friction.

But as the business grew, they started to hit limits. “It’s very hard to implement or support any complex query,” Tong says of the old Elasticsearch-based setup.

Originally built as a search engine, Elasticsearch wasn’t designed for relational queries. "It’s based on indexes, so it doesn’t support joins very well," Tong says. If the team wanted to analyze coupon usage across user cohorts or measure customer retention across orders and locations, they had to engineer workarounds—writing custom scripts, reshaping ingestion pipelines, or duplicating data across indexes.

The more they wanted to learn from their data, the more engineering time it took for a small team focused on growth, and that overhead became unsustainable. They needed a more flexible, resilient system built for the kinds of questions they actually wanted to ask.

 :::global-blog-cta::: 

## Why they chose ClickHouse

When Artly started evaluating databases, ClickHouse quickly rose to the top. "We compared multiple OLAP databases, and in the end we chose ClickHouse," Tong says. He highlights its support for SQL as a key reason: "It’s very flexible and great for our use cases."

The new setup is powerful and refreshingly straightforward. AWS Glue moves data from DynamoDB to S3, and then into ClickHouse. Grafana sits on top for data visualization. This means no more convoluted ingestion pipelines, no more janky workarounds, and most importantly, no more limitations on what the team can ask of their data.

![artly-blog-3.png](https://clickhouse.com/uploads/artly_blog_3_6cb8d7304d.png)
<div style="text-align: center; font-style: italic; margin-top: 12px;">AWS Glue syncs data from DynamoDB to S3 to ClickHouse, with Grafana on top for dashboards.</div>


"We can query in a very flexible way," Tong explains. "We can join tables. We can use nested queries. We can filter on multiple columns."

He describes ClickHouse as high-performing and "very comprehensive." Unlike the time-series databases they tested, ClickHouse supports both time-series and non-time-series use cases. This is a big advantage for a team like Artly that works with robotic telemetry and customer purchase data side by side.

It's also been low-maintenance from day one. "After we set up the platform, we didn't have to do any extra maintenance," Tong says. "We just monitor some metrics. It's very good. There's been no issue in our production environment."

"And the pricing is very affordable compared to other alternatives," he adds.

## Faster, cheaper, and more flexible

ClickHouse has given Artly a whole new level of visibility. The team can now dig into their data to spot repeat customers, identify purchasing patterns, track how promotions are performing, and even figure out the best operating hours for each location.

"Some locations, like Pike Place or Pier 39, have more traffic on weekends and holidays," Tong says. "But for office use cases, there’s usually more traffic on weekdays. So we use ClickHouse to analyze which hours are best for each location and adjust for both winter and summer time."

Speed and affordability have also been massive wins. The team’s tests found ClickHouse to be 3.5x faster and 2.5x cheaper than other OLAP options. The performance gains mean faster decisions, and the lower cost gives them room to grow without worrying about budget.

It’s also proven rock-solid at scale. ClickHouse handles large datasets with ease and delivers the availability Artly needs to support a growing network of robots. For a small team moving fast, that kind of stability is huge.

## ClickHouse in every cup

With a strong data foundation, Artly is setting its sights on even deeper personalization. The team plans to expand its use of ClickHouse to support user behavior analysis, smarter recommendations, and more targeted promotions. 

They’re also preparing to migrate their system operation history (including things like menu updates and robot metadata) into ClickHouse to make that data easier and faster to query. "ClickHouse gives us more flexibility for those use cases," Tong says.

As Artly’s fleet of barista bots keeps growing across cities, storefronts, and pop-ups, that kind of flexibility is exactly what the team needs to keep scaling great coffee, without ever compromising on craft.





