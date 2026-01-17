---
title: "How Rapid Delivery Analytics tracks real-time CPG performance with ClickHouse Cloud"
date: "2025-06-06T17:23:29.845Z"
author: "ClickHouse Team"
category: "User stories"
excerpt: "“ClickHouse Cloud is the core of our solution. It gives us the kind of capabilities and infrastructure you’d expect from a much bigger, better-known corporation, while still letting us stay lean.”  Andrey Dyatlov, Co-founder and CEO"
---

# How Rapid Delivery Analytics tracks real-time CPG performance with ClickHouse Cloud

In recent years, the rise of rapid delivery (also known as quick commerce or “q-commerce”) has changed how people shop for groceries and convenience goods. Apps like Uber Eats, Flink, and DoorDash now deliver everything from cereal to shampoo in under two hours. 

But while shoppers love the convenience, consumer packaged goods (CPG) brands have struggled to keep up. With dozens of apps and hundreds of thousands of delivery zones, it’s hard to know where products are showing up, let alone how they’re performing.

[Rapid Delivery Analytics](https://rda.team/) (RDA) is out to change that. The Paris-based startup offers a digital shelf analytics platform built specifically for rapid delivery, giving brands real-time visibility into stock levels, search rankings, pricing, promotions, and more. With coverage across more than 40 delivery apps in over 100 countries, it helps global CPG brands like PepsiCo and Unilever stay on their game in a frenetic, fragmented channel.

We caught up with RDA co-founder and CEO Andrey Dyatlov to talk about the role of data in rapid delivery, why his team chose ClickHouse to power their analytics engine, and how [ClickHouse Cloud](https://clickhouse.com/cloud) on AWS has become core to their platform as they scale.

:::global-blog-cta:::

## Built for speed from day one

For nearly a decade, Andrey and his co-founder Vlad Gafarov have worked with the world’s biggest CPG brands, helping them navigate the evolving world of ecommerce. But when COVID-19 hit, everything changed. Traditional sales and merchandising models no longer applied. “We had to find a new way to work with them,” Andrey recalls. “We needed to rethink what to build, and how we could keep supporting them based on our experience.”

In early conversations with clients, one theme kept coming up: a new wave of ecommerce was taking shape around ultra-fast, mobile-first delivery. New platforms were launching overnight, promising groceries and convenience goods in just a few hours. At the same time, traditional retailers were racing to establish their own presence in the space. “But for the brands—our customers—it was all a black box,” Andrey says. 

From the start, the team understood that rapid delivery was unlike any other ecommerce channel. While most analytics tools were built for traditional ecommerce or brick-and-mortar channels, RDA focused on the unique challenges of q-commerce: extreme geographic granularity, fast-changing assortments, and the need to monitor everything from pricing and promotions to search performance in near real time. “We saw a huge opportunity to create a solution for this particular side of ecommerce,” Andrey says.

They began building with Postgres, a familiar choice. But as Andrey puts it, “It didn’t take long to realize something had to change.” As data volumes grew and customer expectations rose, the team needed an architecture that could scale with them over the long run.


## ClickHouse Cloud enters the chat

The team began to rethink the fundamentals of their stack. Postgres had worked “quite well” early on, Andrey says, especially when paired with TimescaleDB. But it was ultimately built for transactional (OLTP) workloads, not the kind of analytical (OLAP) queries RDA needed to run across billions of rows. “We needed a better way to run OLAP queries,” he says.

Several team members were already familiar with ClickHouse, so they started with a self-hosted deployment. The results were positive: faster queries, better compression, and a structure that fit their high-volume, time-based metrics. They also tested Amazon Redshift as part of the evaluation, but it didn’t stick. “We didn’t find anything that caught our eye,” Andrey says.

While ClickHouse met their performance needs, running it themselves introduced new challenges. Their workloads weren’t static: some jobs required short bursts of intense compute, while others needed to stay lean. “That’s where ClickHouse Cloud entered the chat, so to speak,” Andrey says. “We needed the API to upscale and downscale really fast, so we could run a lot of aggregations, then downscale again.”

ClickHouse Cloud’s flexibility helped unlock new efficiencies. “It’s about cost savings,” Andrey explains. “And it’s about having the extra capacity available anytime, which is really, really helpful when we have something important to do with this amount of data.”


## Real-time analytics at scale

Today, ClickHouse Cloud powers the core of RDA’s analytics engine, from data ingestion and aggregation to the dashboards brands rely on for daily decisions. The platform ingests more than 500 GB of raw data per day, covering 40+ apps, hundreds of thousands of delivery zones, and billions of product listings. “The amount of data is insane, to be honest,” Andrey says.

ClickHouse plays a central role in processing and aggregating that data efficiently. RDA uses it to calculate key metrics on a daily basis, storing the results in a format optimized for fast access by both internal teams and external users. For clients who need direct access, RDA exports data from ClickHouse to S3, Postgres, or other downstream systems.

Performance has been impressive. Aggregations that span billions of rows complete in under an hour, and search queries typically return in less than a second. As Andrey explains, that kind of speed matters, especially for clients with real-time alerting or transactional workflows tied to data. “Some of our clients have a transactional model where they need to pull something from the table quickly, as part of an alerts pipeline or similar use case,” he says. “That low-latency access is important for them and for us.”


## Growing without slowing down

Currently, RDA is adopting one of ClickHouse Cloud’s newest features: [compute-compute separation](https://clickhouse.com/blog/introducing-warehouses-compute-compute-separation-in-clickhouse-cloud). The team is isolating ingestion from analytics, giving each workload its own dedicated resources. That means keeping a lightweight service running continuously for ingesting data, while scaling up compute only when needed for heavy aggregations or client-facing queries. “This will save us a lot of time and money,” Andrey says.

For a data-heavy startup in a fast-moving space, that kind of flexibility is essential. ClickHouse Cloud has already helped RDA ingest, aggregate, and query billions of rows daily without performance trade-offs or infrastructure complexity. Now, with features like workload isolation and autoscaling, the team has even more control as they grow, onboard new customers, and expand globally, without needing to operate like a large enterprise.

“We’re still a startup, but we work with very big companies,” Andrey says. “ClickHouse Cloud is the core of our solution. It gives us the kind of capabilities and infrastructure you’d expect from a much bigger, better-known corporation, while still letting us stay lean.”

To learn more about ClickHouse and see how it can bring speed and scalability to your team’s data operations, [try ClickHouse Cloud free for 30 days](https://clickhouse.com/cloud).