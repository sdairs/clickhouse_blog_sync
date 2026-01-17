---
title: "Borderless360 Revolutionizes Real-Time Logistics Analytics: Powered by ClickHouse"
date: "2025-09-04T14:11:14.961Z"
author: " Emil Balashov, Co-Founder and CTO of Borderless360"
category: "User stories"
excerpt: "Read how Borderless360 scaled from sluggish Postgres dashboards to lightning-fast, AI-ready logistics analytics with ClickHouse to deliver real-time visibility for global ecommerce."
---

# Borderless360 Revolutionizes Real-Time Logistics Analytics: Powered by ClickHouse

Done right, logistics should feel effortless to the end customer. Packages should arrive on time. Tracking updates should be accurate. And the machine behind it should stay largely invisible.

It’s a different story for the brands doing the shipping. They need to know where their inventory is, if an order is being delayed, whether SLAs are being met, and how much they’re spending on shipping, returns, warehousing, and more. In other words, visibility is everything.

For [Borderless360](https://www.borderless360.com/), an end-to-end logistics platform for ecommerce brands founded in 2017, that mindset is baked into every part of the business. The company runs a global ecommerce fulfillment network across the US, Canada, UK, EU, Hong Kong, Japan, Australia and New Zealand, handling the entire shipping process from inventory orchestration to last-mile delivery and returns. They also handle cross border services like freight forwarding and direct injection.

“We connect couriers and warehouses around the world in a single system,” says Emil Balashov, Borderless360’s co-founder and CTO. “Most platforms are fragmented by country. We provide one global backend for everything.”

That backend doesn’t just power fulfillment and shipping. It also delivers real-time analytics, which Borderless360’s customers rely on to monitor performance, track costs, and catch operational issues before they escalate.

We chatted with Emil to learn about Borderless360’s journey, the problems they faced as they outgrew their original Postgres-based analytics setup, and how switching to ClickHouse helped them scale faster while laying the foundation for a new AI-powered future.

## Postgres wasn’t built for this

Initially, Borderless360 relied on Postgres and Metabase to power its analytics. For a few years, the stack held up fine. But as the company's order volumes and customer base grew, especially after the COVID-19 pandemic, performance began to suffer.

While great for OLTP queries, Postgres wasn't built for the kind of real-time, large-scale analytics Borderless360 needed. Filtering and aggregating across tables with hundreds of millions of rows brought dashboards to a crawl. Even with optimized queries, the database would time out or fail during peak usage, leaving customers in the dark.

"It became pretty evident that Postgres wasn't capable of aggregating data fast enough for our customers," Emil says. "For our largest customers, it took 30 seconds just to render the page and provide all the details. Sometimes it wouldn't even work at all."

Performance wasn't the only issue. As a bootstrapped company, Emil and the team found it hard to justify spending north of $3,000 a month on a solution that wasn't delivering. "We're not VC-funded, so finances are quite important to us," he says. "We had to find a solution to provide analytics to our customers in an affordable way, but also at the highest level."

## From dinner to deployment

ClickHouse wasn’t a new name to Emil. Years earlier, he’d had dinner in Shenzhen with ClickHouse creator and CTO Alexey Milovidov. So in 2023, when the time came to upgrade Borderless360’s stack with a faster, more efficient OLAP database, he knew where to turn.

![borderless_team.jpg](https://clickhouse.com/uploads/borderless_team_29c8338041.jpg)

While he expected a learning curve, Emil felt the performance boost would be worth it. "Speed is the most important thing," he recalls thinking. "Nothing else matters. We'll just go through the pain points and figure out how to work with ClickHouse."

Rather than rebuild everything from scratch, the team took a surgical approach, swapping out Postgres for ClickHouse as the OLAP engine and rewriting their existing queries. "We just changed the database provider and rewrote the SQL to the syntax ClickHouse supports. That was extremely easy to do."

Still, syncing data from Postgres to ClickHouse was a hurdle. Borderless360 was running on Heroku at the time, and the [Postgres CDC Connector for ClickPipes](https://clickhouse.com/blog/postgres-cdc-connector-clickpipes-ga) didn't exist yet. So the team built their own cron-based pipeline to move tens of thousands of records into ClickHouse each day. "It wasn't really hard," Emil says. "It just took a bit of time to learn."

They also had to rethink how to handle mutable data like financial transactions, which don't map cleanly to ClickHouse's [append-only model](https://clickhouse.com/docs/guides/inserting-data). In some cases, that meant adapting queries to exclude outdated rows instead of updating or deleting them directly.

With help from ClickHouse support, the team fine-tuned their setup and brought costs under control. "The customer support was great," Emil says. "They helped us understand and optimize what was needed to make sure it was a reasonable amount of money for us."

## Speed and savings with ClickHouse

Emil doesn't have hard numbers on just how much faster ClickHouse is than Postgres, but he knows it's not even close. "It could be hundreds of times, to be honest," he says. 

"With Postgres, a query might take 10 to 20 seconds," he explains, "and if I execute any complicated mathematical aggregations, it will probably crash. ClickHouse responds in less than a second, which is extremely impressive."

That kind of speed has made all the difference for Borderless360's customers. The team has been flooded with an overwhelming positive response. Where dashboards used to lag or fail, they now load instantly, letting users easily view shipping costs, warehouse throughput, SLA performance, and more, all in real time.

The benefits show up on the cost sheet, too. At one point, the company was paying over $3,000 a month for their Heroku setup, including more than $1,500 for Postgres alone. With ClickHouse, they brought the latter number down to around $1,000 per month.

For Emil, the move was about more than just saving money. "It's an investment in better analytics," he says. "Regardless of how much Postgres costs, it wasn't going to solve our problems. ClickHouse is obviously the right tool for what we're trying to do."

<iframe width="968" height="544" src="https://www.youtube.com/embed/lY-VFhtZ4PI?si=vz4TIha8n35MULD7" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

## A foundation for AI-driven logistics insights

The latest step in Borderless360's analytics evolution is an [AI agent](https://www.borderless360.com/platform/ai-agent/) built on top of ClickHouse. This AI-powered logistics expert can answer questions in natural language like "What's my average order volume per country?" or "How many orders failed SLA last week?"

As Emil explains, this couldn't have been done on Postgres. "It just wouldn't be possible if the request response time was more than a second, because no one would use an AI agent that thinks for 10 or 20 seconds before giving an answer."

That speed opens the door to new possibilities beyond traditional dashboards. "It gives us a lot of opportunities to develop new functionality," Emil says. "Not only analytics, but also retrieving information, summarizing it through AI tools, and providing customers with clear answers to their questions. Without ClickHouse, this wouldn't be possible."

Internally, the shift to ClickHouse has let the team invest more in data science and experimentation. With a faster, more flexible engine under the hood, they can explore operational questions in more detail, respond to support issues faster, and make smarter product decisions, without overwhelming the system.

## Shaping the future of fulfillment

As Emil and the team push forward with ClickHouse, their momentum is fueling other modernization efforts.

With ClickHouse, what started as a fix for slow dashboards has grown into a platform for AI-driven insights, greater operational agility, and a much-improved customer experience. As Emil reflects on everything they've gained since moving to ClickHouse, he comes back to one simple fact: "It just works."

In logistics, where speed and visibility are everything, he adds, "That's what customers expect."

To learn more about ClickHouse and see how it can improve the speed and scalability of your team's data operations, [try ClickHouse Cloud free for 30 days](https://clickhouse.com/cloud).

