---
title: "How iSAM Funds built an options research platform for a 10,000x data problem with ClickHouse Cloud"
date: "2026-10-09T18:47:59.606Z"
author: "ClickHouse"
category: "User stories"
excerpt: "iSAM Funds uses ClickHouse Cloud to research full options history, achieving 35–50x compression and 100x faster single-core ingestion while simplifying its data pipelines."
---

# How iSAM Funds built an options research platform for a 10,000x data problem with ClickHouse Cloud

## Summary

- iSAM’s options desk runs its market data research platform on ClickHouse Cloud, giving researchers fast, interactive access to full options history for hypothesis testing.
- Migrating from Postgres to ClickHouse gave the team 35-50x compression over their previous footprint and took single-core ingestion from 8,000 to 800,000 rows/sec.
- ClickHouse’s columnar storage and vectorized execution made queries fast enough to run on demand, letting the team drop pre-computed rollups and materialized views and removing a layer of pipeline complexity.

[iSAM Funds](https://isam.com/) is a UK-based alternative asset manager specializing in systematic investing. The firm is relentlessly data-driven. “Data forms such a key part of our architecture,” says Steve Barham, iSAM’s Head of Options Development. “Our technology requirements are informed by the data we can observe, how we can store it, and what information we can extract from it.”

The iSAM Options desk was created around three years ago, with a broad remit of bringing cross-asset options capability into the firm. 

As Steve explains, capturing market data on an underlying listed instrument (e.g. a future, a listed equity) is well-trodden ground. Those markets tick frequently, and handling that flow is bread and butter for most firms. “The challenge comes when you want to start looking at the options market on top of that data,” he says. “When the underlying moves, how many related options move in response to that?”

His design estimate for that fan-out is around 10,000 symbols. “That puts you into a very different kind of space from a data engineering perspective,” he says. Everything downstream inherits that multiplier—distributing the data, storing it, and then querying it back out again.

We caught up with Steve to learn about the technical challenge his team is solving, and how [ClickHouse Cloud](https://clickhouse.com/cloud) on AWS helps them handle far more data, reduce the complexity around it, and shorten the path from a researcher’s idea to a tested hypothesis.

## Sizing the problem before solving it {#sizing_the_problem_before_solving_it}

The first step, Steve says, was measuring the problem. That starts with reference data, establishing for a given underlying which options exist on it, and for a given market what the underlying set looks like. This tells you how much data you’ll need to process. The goal, as Steve describes it, is to build consistent snapshots of as much of the market as possible, and build derived data pipelines and trading systems from that market data.

A key consideration for scaling is the distribution of the market data activity across exchange products, which is rarely uniform. “CME Group lists several hundred futures markets, many of which have associated options markets,” Steve says. “But if there’s little volume on a market, then you don’t have much of a data challenge.” On the flipside is something like treasuries or S&P futures, with many listed contracts and heavy liquidity moving through them. He describes the activity as unevenly distributed across markets. That makes simple horizontal partitioning or sharding less effective: volumes vary significantly by market, and there are too few markets for naïve partitioning to balance the load reliably.

For Steve and his team, building the options data platform ultimately came down to two core challenges. “Analysing the volume of data you’re dealing with is the first phase, and then giving yourself confidence that you’re going to be able to distribute, store, and query that volume is the next step,” he says. “That’s where ClickHouse came in for us.”

## From Postgres to ClickHouse {#from_postgres_to_clickhouse}

When it comes to building something new, Steve thinks about decision-making in terms of innovation tokens. “What are you going to spend your innovation tokens on?” he asks. “Is it going to be the business domain? The tech domain? Some combination of the two?” 

On technology, Steve’s team chose the “boring, familiar” route, prototyping with Postgres. It got them a reasonable way into the iteration, letting them run the experiment and measure the problem. But as the team’s ambitions grew in both the breadth and depth of the data they wanted to capture, he says, “it very quickly became clear that we would need a fairly fundamental change in how that data was persisted.”

Other teams inside iSAM had been working with ClickHouse at varying levels of sophistication, and the reports coming back were encouraging enough for Steve to commit time to running a trial. He set up a parallel persistence path for the desk’s data on the same hardware, to see what the technology could do. 

The results were impressive. Storing data in time-series order, without anything he considers special in the way of tuning, produced 35-50x compression over the team’s Postgres footprint. Single-core ingestion went from 8,000 rows per second to 800,000.

Just as valuable was ClickHouse’s flexibility in ingest and egress. The iSAM Options desk builds much of its internal data infrastructure on Apache Arrow. “I can just talk Arrow to ClickHouse,” Steve says. “I can send it an Arrow-encoded frame to insert and have confidence that it’s going to get there, and I can do the same to pull the data out.” Whether it’s Arrow, Parquet, or JSON, he isn’t constantly reshuffling data between encodings every time it crosses a boundary. “That lack of opinion on what data should look like over the wire—that’s a really big thing,” he says.

## Choosing ClickHouse Cloud to focus on innovation {#choosing_clickhouse_cloud_to_focus_on_innovation}

The desk was live on ClickHouse within a couple weeks. “When you’re building, time to market is critical. I like iterations to run quickly. I like to show people the results of changes as quickly as I can, so that we can rapidly find the right product and iterate on that,” says Steve.

Within a month or two, the question had shifted from whether ClickHouse worked to whether the team should be running it themselves. “It became apparent this was going to be a core part of our data infrastructure,” Steve says. 

> “I didn’t want to spend my innovation budget learning how to run ClickHouse on-prem with failover and all the things you need when this is one of your primary data stores. I just wanted a turnkey solution that would let me proceed with confidence. That’s what ClickHouse Cloud gave me.” — Steve Barham, Head of Options Development, iSAM

ClickHouse’s managed service still had to satisfy iSAM’s requirements as a systematic fund. iSAM runs a substantial AWS footprint of its own and gates network access to its ClickHouse services accordingly, reaching them over the firm’s existing direct connectivity into AWS. The deployment integrates with iSAM’s enterprise authentication stack, a core requirement for the platform.

One newer capability that’s proven useful is pushing backups into iSAM’s own buckets. The team uses that to pull a subset of production data into on-prem ClickHouse instances, for developer productivity,  isolated from production load.

## Fast enough to keep things simple {#fast_enough_to_keep_things_simple}

For Steve, one of ClickHouse’s biggest advantages is the way its performance reduces complexity. Rollups, materialized views, pre-aggregated data stored in down-sampled form—“a lot of these things we’ve just stopped doing, because ClickHouse is quick enough between the column store and vectorized execution,” he says. “If I want to stick a chart on a page with a year’s worth of bar data, that’s fine, I just run that query.”

That’s not to say simplicity is the goal everywhere. “I’m happy our system has areas of high complexity,” Steve says. “That’s inevitable. If we didn’t have that, we wouldn’t be a competitive business.” What he doesn’t want is complexity accumulating in a web front end, or in a pipeline whose only job is pre-aggregating data. “I want that complexity to sit in the right place.”

As Steve puts it, that’s what a fast database buys a team: “A system as performant as ClickHouse, we’ve been able to throw any query at it, it just works.”

From a business standpoint, that speed shows up in how quickly ideas can be tested. iSAM’s researchers don’t query ClickHouse directly (access is mediated through the desk’s own systems), but its performance allows them to rapidly test new ideas across the full universe and full history. “My aim is to make data exploration faster and more consistent, so that our researchers have a shortened time horizon between idea and time to market,” Steve says.

> “Time to market has become the most important metric, especially with AI. How quickly can you test your hypothesis? How quickly can you see if this is going to work? ClickHouse has been really, really helpful for that.” — Steve Barham, Head of Options Development, iSAM

## Room to keep growing {#room_to_keep_growing}

The other thing [ClickHouse Cloud](https://clickhouse.com/cloud) gives the desk is headroom. As Steve sees it, throwing more compute at parallel dataset construction doesn’t remove a constraint so much as move it into the state store. The data store has to scale along with everything else. 

When a large rebuild is coming and the team knows they’ll be hammering ClickHouse for hours, they scale the instance up, run the backfills, and let it scale back down, rather than sizing an on-premises machine for a peak that arrives occasionally. Steve calls it “a very cost-efficient way of renting some very expensive hardware.”

That headroom gets more important as the desk keeps expanding. The team has gone from futures to FX to equity options in three years, multiplying the data underneath at every step. Steve says their next focus is reconstructing large datasets across full history faster.

Beyond performance and scalability, Steve highlights the support he’s gotten from the ClickHouse team, including a shared Slack channel that’s been running since the early days of the migration. “Being able to talk to genuinely technical people allows us to shortcut a lot of handholding and triage,” he says.

Ultimately, Steve’s desk exists to pull information out of the volatility space and build strategies on it. That means holding far more data than a conventional trading desk and getting answers as quickly as possible. With ClickHouse Cloud, the full history stays online and queryable, fewer pipelines sit between a question and its answer, and the platform scales as each new market multiplies the data underneath.

---

## Get started today

Interested in seeing how ClickHouse works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-2573-get-started-today-sign-up&utm_blogctaid=2573)

---