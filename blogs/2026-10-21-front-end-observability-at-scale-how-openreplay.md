---
title: "Front-end observability at scale: How OpenReplay captures billions of daily events in real time with ClickHouse"
date: "2026-10-21T18:40:19.428Z"
author: "ClickHouse"
category: "User stories"
excerpt: "OpenReplay replaced Postgres with ClickHouse to ingest billions of events and up to 6 TB a day on a single, vertically scaled instance, with sub-second queries and retention handled by a single TTL setting."
---

# Front-end observability at scale: How OpenReplay captures billions of daily events in real time with ClickHouse

## Summary

- OpenReplay is a self-hosted session replay and product analytics platform that helps developers reproduce bugs by showing them exactly what a user did.
- With ClickHouse, a single TTL setting replaced Postgres’s weekend-long manual cleanups, and materialized views cut pipeline changes from two days to half a day.
- Today, OpenReplay’s largest customers ingest billions of events and ~6 TB per day on a single, vertically scaled ClickHouse instance, with sub-second queries.

[OpenReplay](https://openreplay.com/) is a session replay and product analytics platform built for developers. By seeing how users interact with their app, product teams can use the platform to identify friction, understand user behavior, and troubleshoot and fix issues faster.

Mehdi Osman, OpenReplay’s founder and CEO, describes it as observability for front-end engineers. “It’s like sitting next to a user,” he says. “You don’t have to call them, you don’t have to do interviews. You’re just sitting quietly and looking at exactly what they’re doing.”

One of OpenReplay’s biggest differentiators is that it’s fully self-hosted. “That gives absolute data control and governance for our end customers,” Mehdi says. It’s also open source, which lets the team rapidly iterate on community feedback, and fits with the platform being built on other open-source projects like ClickHouse, Postgres, Kafka, and Redis.

As Mehdi puts it, the data challenge has three parts. The backend has to ingest terabytes per day for each customer. “Any grain of sand could impact the whole ingestion pipeline,” he says. OpenReplay then has to turn that data into something useful, which is “where ClickHouse comes into the picture.” And all of it has to run inside each customer’s own environment, with minimal operational overhead for the customer and for OpenReplay’s small team.

We caught up with Mehdi and senior software engineer Taha Yassine Kraiem to chat about their journey, including how OpenReplay’s largest customers ingest billions of events per day on a single, vertically scaled ClickHouse instance, with sub-second queries.

## Replacing Postgres with ClickHouse

Back in 2019, OpenReplay ran everything on Postgres, hosted on AWS. The transactional database handled metadata fine, but behavioral events (the clicks and page views that make up a session) were a different story. “It’s not an analytics database,” Mehdi says. “There were things we couldn’t do on Postgres that would take ages to run.” The team tried sharding the tables to compensate, but as Mehdi says, “that created an operational mess we couldn’t deal with. That was a no-go.”

A good example of the performance problem is OpenReplay’s session search. It can combine multiple event types in sequence, with criteria on each. The team’s target was a response under one second. Even after adding indexes, partitioning, and sharding, typical Postgres queries came back in around three seconds, with some taking up to 10 seconds.

After migrating to ClickHouse, average response time dropped to about a second. “We could never accomplish that with Postgres,” Mehdi says. “I mean, we could, but it would mean lots of work, lots of sharding, operational overhead which we didn’t have.”

Storage was a similar story. Events tables that had grown to around 1 TB in Postgres compressed down to 1 or 2 GB in ClickHouse. “It was like nothing basically,” Taha says. “And even running queries on compressed data is still super fast.”

The other problem with Postgres was retention. OpenReplay keeps session data for a set period and then deletes it. In Postgres, that meant scripts, deletes, and vacuuming that locked tables and forced restarts. “It was a complete mess,” Taha says. “It took us a lot of time and a lot of effort, and sometimes something doesn’t go right and we have to fix it.”

Because customers self-host, cleanups also meant coordinating with each of them over the weekend, when traffic was low. “That takes days because it’s just vacuuming, it’s locking tables, you don’t understand what's going on,” Mehdi says.

With ClickHouse’s [TTL (time-to-live) feature](https://clickhouse.com/docs/concepts/features/operations/delete/ttl), retention is set once, at installation. “For some customers it’s three months, for others it’s a year, for others it’s a month,” Mehdi says. “We just set it there and that’s it, the data is taken care of.” A lifecycle rule on the object store handles the recording files the same way, and Postgres holds only metadata. Weekend cleanup calls with customers are a thing of the past. “With ClickHouse,” Taha says, “we connect with them once or twice every six months, just to check if there’s any maintenance we need to do.”

“That TTL is damn valuable,” Mehdi adds. “I know it’s a small feature. You’ll talk about the JSON and the caching and the queries. But TTL saved us too many weekends.”

## How OpenReplay builds on ClickHouse

Today, ClickHouse is at the center of OpenReplay’s data pipeline. Every behavioral event lands in a single table; from there, a chain of [materialized views](https://clickhouse.com/docs/concepts/features/materialized-views) fires on each insert, transforming the rows and passing them along. “Each one will extract and transform data until it reaches its destination table,” Taha explains. “It works awesomely fast. We just change the database and that’s it. We don’t have to edit any code behind it.”

That’s a marked change from how the pipeline used to work, when moving data between tables meant either Postgres triggers or Go workers (the language the pipeline is written in), and any change to a table’s structure required a matching change to the worker. Go workers still handle part of the pipeline today, but with materialized views, a change that used to take two days of development and debugging now takes around half a day. “Having everything centralized in ClickHouse has made life far simpler,” Taha says.

Mehdi adds that materialized views are also where new features start. “When it’s a new feature and we’re not yet sure about the data structure, we rely on these materialized views because we can process data very quickly,” he says. “We can drop it, redo it again. Over a few iterations, when we’re sure about it, we take that part and put it into the Go code, because then the insertion is way faster.”

He also highlights ClickHouse’s [native JSON support](https://clickhouse.com/docs/reference/data-types/newjson), which opened the door to custom events. While clicks and page views are captured automatically, customers doing serious product analytics want to instrument their own events (e.g. “payment done” or “order sent” with a name, body, and list of properties). “Without the JSON support in ClickHouse, we wouldn’t be able to do it,” Mehdi says, “because you’re not just inserting those events, it needs to be super easy to query later on and build all of these funnels and heat maps and flows. Behind the scenes, ClickHouse treats these properties like columns, and you don’t even see it.”

It all sits in a schema simple enough to describe in a sentence or two. “We basically have two main tables,” Mehdi says. “A sessions table that contains the metadata about the recording, and an events table, a big flat table where all the events are being inserted. Two tables, pretty easy to understand, and yet we’re able to do very powerful queries on top of it.”

## Billions of events a day on one instance

OpenReplay sees a wide range of data volumes. Some customers ingest a million or two events a day. Others ingest billions, up to 6 TB of data per day. Even at that scale, each deployment runs on a single ClickHouse instance, a deliberate choice for a product that lives on customer infrastructure. Rather than sharding or clustering, the team scales vertically, adding RAM and CPU as a customer grows. As Mehdi puts it, “We haven’t even covered the depth of what ClickHouse can handle.”

He cites one customer, a multi-billion-dollar fintech company, that chose OpenReplay because it’s self-hosted. “They can run the entire platform on their servers, and they have full control over data privacy and security,” he says. Their two main use cases are bug reproduction and support. Users write in saying they couldn’t complete a payment or sign a contract. A support agent can co-browse with them live and annotate their screen. If that doesn’t resolve it, a developer replays the session with the developer tools open.

The fintech’s deployment records hundreds of thousands of sessions a day, each containing hundreds of events. That adds up to hundreds of millions of events daily, all of it going into a single ClickHouse instance on Kubernetes. “Whenever they grow, every few months, we scale it vertically,” Mehdi says. “We don't have to shard it, we don’t have to add other ClickHouse instances. So it makes the operational cost pretty low, which is extremely important in a self-hosting setting.”

The calculus would be different, he adds, if OpenReplay were SaaS-only. “We would probably subscribe to the [ClickHouse Cloud](https://clickhouse.com/cloud) offering and that’s it,” he says. “But we’re deploying the entire product onto their servers, and that’s why we have to be very lean.”

## Time to replay, and what’s next

Internally, OpenReplay tracks a metric it calls “time to replay,” measuring how long it takes from a session happening to a developer being able to click play and watch it.

> “Ingestion has to be real-time at scale. If you’re capturing a few thousand events, you won’t see it. But if you’re capturing terabytes of data every day, any small hiccup can have an impact and it would take a day or two to recover from the lag. So it’s very important to have a streamlined pipeline, and ClickHouse is a big part of that.”
>
> — Mehdi Osman, OpenReplay’s founder and CEO

On the query side, the goal is that every view in the product, from searches to funnels, heat maps, and flow charts, returns in under two seconds. The team recently enabled ClickHouse’s [query cache](https://clickhouse.com/docs/concepts/features/performance/caches/query-cache), so a query one engineer runs is instantaneous for a colleague a few minutes later. “Caching is one of those things you enable and it just works,” Mehdi says. Asked if there was anything he wanted to add about writing queries against ClickHouse, Taha’s answer was the same. “Nothing special,” he says. “It just works.”

OpenReplay is now using ClickHouse to build an upcoming agents feature that automatically reviews session recordings and proactively surfaces issues, since no team can watch hundreds of thousands of recordings a day. “Think of it as a team of analysts whose job is to review all of the user sessions as a human would,” Mehdi says, adding that every trace the agents produce goes into ClickHouse: “This is what we use for eval, this is what we use for troubleshooting, this is what we use to learn about how the agents are performing.”

Seven years in, ClickHouse has become one of a handful of standard components OpenReplay trusts to run on infrastructure it doesn’t control. Customers keep data on their own servers, and OpenReplay’s stack stays lean enough for them to run it themselves. “All of these things are picked for a reason,” Mehdi says, “which is very little overhead, even when it comes to deploying it for the customer and maintaining it later.”

---

## Get started today

Interested in seeing how ClickHouse works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-2768-get-started-today-sign-up&utm_blogctaid=2768)

---