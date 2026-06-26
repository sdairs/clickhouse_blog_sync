---
title: "How Vibe.co handles billions of ad impressions with ClickHouse Cloud"
date: "2026-06-25T13:30:44.974Z"
author: "ClickHouse"
category: "User stories"
excerpt: "How Vibe.co scaled from 100 GB to 2 TB of Connected TV ad impression data without rearchitecting anything, by migrating from Postgres to ClickHouse Cloud."
---

# How Vibe.co handles billions of ad impressions with ClickHouse Cloud

## Summary

* [Vibe.co](http://Vibe.co), recently acquired by Walmart, uses ClickHouse Cloud to power real-time campaign reporting for thousands of Connected TV (CTV) advertisers across billions of ad impressions.  
* The team migrated from Postgres after outgrowing its pre-aggregation architecture. The platform now serves 90+% of client campaign reports in under 100ms, and has scaled from \~100 GB to over 2 TB without rearchitecting anything.  
* They chose ClickHouse Cloud over self-hosted for operational simplicity, team support, and predictable pricing with separation of storage and compute.

When you stream a show on your Connected TV (CTV), you might notice the ads, but you probably don't think much about how they got there. Behind every ad is a chain of decisions about who to reach, when, on which platform, and at what frequency. For large brands with dedicated media teams, navigating that world has always been complex but at least manageable. For everyone else, it was often out of reach entirely.

[Vibe.co](http://Vibe.co), recently acquired by Walmart, is an all-in-one platform with a mission of making CTV advertising accessible to any brand, of any size, in under five minutes. Its customers range from household names to small businesses running their first-ever TV campaign. What unites them is access to premium streaming inventory through a self-serve platform that feels familiar to anyone who has ever run a Google or Meta ad.

Rémi Paulin is a Staff Data Engineer on Vibe's data platform team, where he has spent the last two years building the infrastructure that makes all of this possible. He's a big believer in keeping things simple: fewer moving parts means fewer things that can break, and fewer things that can break means a platform clients can actually trust. That philosophy applies to user experience, system architecture, and—yes—real-time analytics. Increasingly, it also applies to choosing infrastructure that AI agents can use as fluently as humans do — which, in practice, means picking a database that takes SQL seriously.

> "The best architecture is the simplest one that actually solves the problem. ClickHouse lets us keep the architecture simple without compromising on performance or flexibility, and that combination is rarer than it sounds." 
> 
> — Rémi Paulin, Staff Data Engineer, Vibe

## The right tool for the wrong scale

Like many startups, Vibe.co started with Postgres. As Rémi says, "It's very versatile—you can do a lot with it." But as the platform grew and ad impressions climbed into the billions, Postgres began to show its limits. "Postgres wasn't built for OLAP — once we were doing aggregation-heavy queries over billions of rows, the pre-aggregation layer became the bottleneck," Rémi says.

The problem was architectural. Postgres wasn't designed for OLAP workloads—the kind of high-volume, aggregation-heavy analytical queries that power client-facing reporting. "We had jobs that would preaggregate the data so we wouldn't explode the database in size and keep the performance acceptable," Rémi says.

It worked, but only just. Every new reporting use case meant writing a new job. Every deviation from the expected query pattern made things slow or expensive. The transformation layer had become the most fragile part of the stack.

What Rémi and the team wanted was to eliminate that middle tier entirely. Clients needed to be able to slice and dice their campaign data interactively, not just consume whatever the pre-aggregation jobs happened to produce. And internally, other teams needed to be able to build new products on top of the data without going back to the data platform for a new pipeline every time.

"We wanted to simplify the architecture," Rémi says. "We wanted to be able to just load the data directly into the database, and query it fast enough for any kind of reasonable aggregation." In this vision there would be no pre-computation required, no bespoke pipelines for every new use case or query pattern. With the right database, they could build a system that was genuinely flexible, not just flexible within the use cases they'd already anticipated.

## Why they chose ClickHouse Cloud

As a [columnar OLAP database](https://clickhouse.com/resources/engineering/what-is-columnar-database) built for performance and flexibility, ClickHouse was the logical choice to replace Postgres. The question was how to deploy it.

The team evaluated their options. They benchmarked self-hosted ClickHouse, a managed option via another vendor, and [ClickHouse Cloud](https://clickhouse.com/cloud). While the Vibe team is comfortable self-hosting and even saw a slight performance edge thanks to storage locality, Rémi was clear-eyed about the tradeoff: "As a startup, we don't have time to manage databases. We don't want to allocate human resources to self-host, and we knew it would only become worse as we scaled."

There's also something to be said for going with the people who actually build the product. "When you go managed, you're betting on the people running the service as much as the service itself," Rémi says. "Working with the team behind the team - the engineers who actually build ClickHouse - means their roadmap and ours stay aligned as we both grow."

That extends to Rémi's broader philosophy on choosing infrastructure—and partners. "Being surrounded by knowledgeable partners is definitely a good thing, especially when you want to move fast and you don't have the time to invest into reading every blog post or piece of documentation," he says. "Working with great partners gives you fresh ideas and a fresh outlook on things."

In addition to the operational simplicity and team support, Rémi was drawn to ClickHouse Cloud's [separation of storage and compute](https://clickhouse.com/docs/guides/separation-storage-compute). He contrasts it with the per-query billing used by other warehouse solutions, where every additional query against a larger dataset costs more, and growth can quickly lead to bill shock. "Whether we have more customers on the platform or existing customers with more data, we're not worried about unpredictable cost spikes," Rémi says.

## GB to TB scale, without rearchitecting anything

Since migrating to ClickHouse Cloud, Vibe has grown its stored data from ~100 GB to over 2 TB, and the architecture has barely changed. "That's one of the key measures of success," Rémi says.

> "You build something, and 20x the data volume down the line, you haven't changed the architecture, the data flows, or the way consumers access the data. We've scaled the instances a bit, but that's so much cheaper than scaling the engineering team behind all of this." 
> 
> — Rémi Paulin, Staff Data Engineer, Vibe

The two metrics Rémi watches most closely are cost and latency. He's not losing sleep over cost. "Storage is cheap," he says. "Whether you store one terabyte or five, it's not going to change the bill significantly. If the volume goes up, impressions go up, ads go up—the company is doing well. We're never going to be worried if that number goes up."

Latency is where the real work happens. ClickHouse's built-in observability gives the team fine-grained visibility into query performance across every client. The team uses a hot/cold tiering pattern built on [refreshable materialized views](https://clickhouse.com/docs/materialized-view/refreshable-materialized-view): a hot table covering the last 30 days — which serves the vast majority of client queries — sits in front of the full historical dataset, with each tier tuned to its actual query patterns. The result: under 100ms response times for 90+% of client campaign reports, across billions of impressions.

"The performance is great," Rémi says. "We're very happy with it."

## Simple, flexible, and built to scale

Ask Rémi what he wants people to take away from Vibe's story, and a few themes keep coming up: simplicity, quality, flexibility, and longevity. In his view, they're all connected.

"The fewer moving parts you have, the less risk of something breaking," he says. "The simpler the architecture, the higher the quality." Quality, in other words, isn't just about uptime or performance. It's about trust. "Our clients, but also our internal teams, are comfortable trusting what we make available to them."

Flexibility is what makes that trust scalable. With ClickHouse as the foundation, other teams at Vibe can pursue new product ideas without going back to the data platform team for a bespoke solution every time. "We want people to have a great idea and just be able to implement it," Rémi says. "Flexibility is super important if you want to move fast."

That flexibility extends to [SQL](https://clickhouse.com/docs/sql-reference). Many fast databases support SQL in name only—a long list of unsupported features buried in the documentation. ClickHouse, Rémi argues, treats it differently. "ClickHouse is designed with no compromise on that front," he says. "SQL is a first-class citizen." That matters not only for analysts and internal teams, but increasingly for the AI agents that are becoming a larger part of how data teams work. SQL is the language agents know best, and a database that speaks it fluently is a strategic asset.

The last thing Rémi keeps coming back to is longevity. The data infrastructure space moves fast, and technologies that don't move with it get left behind. Choosing a platform whose trajectory you trust is, in Rémi's view, as important as what it can do for you today. For Vibe, that means picking partners who keep pace with how the industry is evolving, and who give the team room to grow without being locked into decisions made on day one.


---

## Get started today

Interested in seeing how ClickHouse works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-1086-get-started-today-sign-up&utm_blogctaid=1086)

---