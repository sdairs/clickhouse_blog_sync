---
title: "How Bullet uses ClickHouse Cloud to give DeFi's fastest exchange real-time analytics"
date: "2026-07-14T14:23:01.118Z"
author: "ClickHouse"
category: "User stories"
excerpt: "Switching from Databricks to ClickHouse Cloud cut Bullet's query latency 10,000x and eliminated an entire serving layer, giving DeFi's fastest exchange real-time analytics at comparable cost."
---

# How Bullet uses ClickHouse Cloud to give DeFi's fastest exchange real-time analytics

## Summary

- Bullet uses ClickHouse Cloud to index, analyze, and monitor its real-time DeFi perpetuals exchange processing 150 million+ rows per hour.
- Switching from Databricks cut query latency 10,000x, from 10-15 seconds to milliseconds, eliminating the need for a separate DynamoDB serving layer entirely.
- Data freshness improved from 1-2 hours to under 5 seconds, at a comparable cost, while handling 1,000x more data across three environments.


When Tristan Frizza and his co-founders started [Bullet](https://www.bullet.xyz/), they had a specific gap in mind. Over the past half-decade, perpetual futures (perps) had emerged as the dominant trading product in crypto, but most were concentrated on centralized exchanges. Platforms like FTX showed the risk of that model; when you trade on a centralized exchange, you custody your assets with them. When FTX collapsed, traders lost everything.

The alternative, DeFi (decentralized finance), existed in principle, but it was too slow and expensive in practice to attract serious traders. On early Ethereum-based exchanges, a single trade could cost $20 and take a minute to settle. “For the average consumer who’s used a Robinhood or Coinbase, that’s a huge downgrade,” Tristan says.

Bullet is his team’s bet on what DeFi can become. The platform offers perpetuals, spot trading, and lending all on a single exchange. Trades settle on a blockchain, users self-custody their assets, and the whole thing runs fast enough for pro traders. As Tristan puts it, “We’re trying to build the ‘everything exchange’ that has everything you need, and everything runs on blockchain, and everything is fast… so it’s quite a lofty goal.”

Tristan spoke at a [January 2026 ClickHouse meetup in Singapore](https://clickhouse.com/videos/singapore-meetup-sierraresearch), where he walked through Bullet’s sub-millisecond trading architecture. He also shared how they’re using [ClickHouse Cloud](https://clickhouse.com/cloud) for event indexing, real-time analytics, monitoring, and how switching from Databricks cut query latency from 10-15 seconds to milliseconds and eliminated an entire serving layer, all while handling 1,000 times more data at a similar cost.

<iframe width="768" height="432" src="https://www.youtube.com/embed/AmGnllMOM-0" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

## The latency problem at the heart of DeFi

In trading, market information travels at the speed of light. That’s why Wall Street firms spend millions on fiber connections and microwave towers, trying to shave microseconds off the time it takes for price information to travel between exchanges. If you’re a market maker quoting prices on a slow platform, you’re constantly exposed; arbitrageurs can buy from your stale quotes faster than you can cancel them. Market makers demand low latency for exactly this reason, and it’s why deep, liquid markets cluster on the fastest venues.

This has historically been DeFi’s Achilles heel. Ethereum L1 settles in about 15 seconds. Solana brought that down to 400 milliseconds, which was revelatory when it launched, but still too slow for derivatives trading. Hyperliquid, one of the most successful recent DeFi trading platforms, gets to around 70 milliseconds by concentrating infrastructure geographically. Binance, as a centralized exchange, hits 10-20 milliseconds, but at the cost of the self-custody and transparency that make DeFi worth using.

“We figured, blockchains have been pretty slow historically,” Tristan says. “Can we do better? Can we make things faster? Can we make market information propagate a lot quicker, but do it in a blockchain way where people own their own assets, and it’s not just sitting on some central server?” By speeding things up, he adds, “We can get a lot more liquidity, and we can get good markets where, at the end of the day, consumers get very good depth, they can trade in very big size, and they’re not taking a lot of slippage and losing out on every trade.”

Bullet, running as an app-specific rollup in pure Rust on Solana, achieves sub-millisecond speeds, faster than Hyperliquid or Binance, including ~500 microseconds at p50 and ~650 microseconds at p99. Tristan stresses the value of that p99 number: “If your median time is a millisecond but your worst case is a second, you’re always going to lose on that worst case,” he says. Low jitter (predictable fills, not just fast ones) is what makes market makers willing to provide liquidity, which is what makes an exchange worth trading on.

![](https://clickhouse.com/uploads/bullet_jul2026_image2_bb6fd7343b.png)

*Order processing time on Bullet's mainnet: p50 (green) holds around 500μs, p99 (yellow) around 650μs, staying within ~150μs of each other across six hours of live trading.*

## Why ClickHouse was a perfect fit

Bullet’s trading infrastructure solves the execution problem, but it creates a different one. Blockchains are state machines, meaning they process transactions and move to the next state, but they don’t retain history. “If someone’s done a trade,” Tristan says, “and they want to come back and audit it for tax purposes, or look back at what were my trades last week, that information is basically gone, because it’s stateless in that sense.”

This is where ClickHouse comes in. Bullet uses [ClickHouse Cloud](https://clickhouse.com/cloud) to index every event the exchange emits and make it queryable in milliseconds. That data powers three main use cases: user-facing features like trade history, P&L charts, and audit logs; real-time analytics like 24-hour volume, leaderboard rankings, and referral rewards; and internal monitoring, with state snapshots every minute feeding Grafana dashboards that alert the team via Slack and PagerDuty before anything goes wrong (Tristan was even paged *during* his presentation in Singapore; “It shows it’s working,” he joked).

Blockchain data is append-only, meaning Bullet is never updating old records, only adding new ones. At over 150 million rows per hour, that volume adds up. ClickHouse’s [columnar storage](https://clickhouse.com/resources/engineering/what-is-columnar-database) model, Tristan says, is a “perfect fit” for this kind of workload. The database powers sub-second queries on time-series data, while its “incredible compression ratio” dramatically reduces storage costs compared to Bullet’s previous approach of storing uncompressed JSON in S3. Similarly, ClickHouse’s [native Kafka integration](https://clickhouse.com/docs/integrations/kafka) “just works out of the box,” letting data flow straight from Bullet’s event stream into the database without custom wiring.

ClickHouse Cloud’s reliability and ease of use are a far cry from Bullet’s previous setup. “Things would break all the time, and I had to maintain it all, even when I’d go on holidays… it was just kind of a nightmare,” Tristan says. “ClickHouse is great. We put our events in there, we put our analytics in there, monitoring, a bunch of other stuff. We use it for the majority of things in our stack. It’s become the one-size-fits-all for a lot of our stuff.”

## Getting data in: ingestion and deduplication

Bullet’s ingestion pipeline starts at the rollup sequencer. A Rust indexer listens over a WebSocket to what Tristan calls a “crazy firehose of thousands of events per second,” batching everything into a Kafka topic that runs on AWS MSK. Redpanda Connect handles event classification, reading each event, identifying what type it is, and routing it to the appropriate Kafka topic (with a parallel feed to S3 Glacier for disaster recovery). ClickHouse Cloud consumes from those topics directly, writing events into dedicated tables rather than one large unstructured database. This keeps queries “very fast,” Tristan says, as each table can be sorted and ordered by the fields that matter most for that event type.

![](https://clickhouse.com/uploads/bullet_jul2026_image1_9844a0777c.png)

*Bullet’s ingestion pipeline: events flow through a Rust indexer into Kafka, where Redpanda Connect classifies and routes them to dedicated ClickHouse Cloud tables, with a parallel S3 backup for recovery.*

The pipeline has been load-tested to 3 million transactions per second with zero message loss. In production, events reach ClickHouse in under a second from the moment they’re emitted by the sequencer. “It scales really well and plugs nicely into ClickHouse,” Tristan says.

One of the more important patterns Bullet uses is ClickHouse’s [ReplacingMergeTree table engine](https://clickhouse.com/docs/engines/table-engines/mergetree-family/replacingmergetree), which solves the problem of deduplication. In a high-throughput pipeline, the same event can arrive more than once (e.g. a network hiccup, a retry, a reindex). Before ClickHouse, Bullet ran deduplication jobs in Spark, processing everything in RAM. It was expensive, hard to scale, and time-consuming for a founder also running the company. With ReplacingMergeTree, each trade has a unique auto-incrementing event number and transaction hash; ClickHouse keeps the latest version of any record with matching keys, using an indexed timestamp as the tiebreaker.

The practical effect (what Tristan calls the “superpower” of ReplacingMergeTree) is that the entire pipeline becomes idempotent. If something breaks, Bullet can reindex from the rollup and ClickHouse deduplicates automatically. “It takes a lot of cognitive load off us,” Tristan says. “We know that our trades table has no duplicates, all our data is clean, and we can just rerun the pipelines, backfill, do all that kind of stuff.”

## Simplified serving infrastructure

Before ClickHouse, Bullet ran its analytics on Databricks. The architecture worked, but there was a fundamental mismatch. As Tristan explains, Spark takes 5 to 30 seconds just to boot the JVM and plan a query. That made it too slow for serving data to a frontend where users expect results in milliseconds.

His workaround was to batch-compute results hourly, push them into DynamoDB, and serve from there. Again, it worked, but it meant maintaining two systems, a batch pipeline and a separate key-value serving layer, and the data was always at least an hour stale. “It was a bit flaky, and I was never very proud of it,” he adds.

ClickHouse made the DynamoDB layer unnecessary. Queries return in milliseconds, so Bullet now calls ClickHouse directly from their API layer with no caching needed. “I was kind of blown away at how fast it was,” Tristan says. “You can just make a query on ClickHouse and it takes like 10 milliseconds. We don’t even need a serving layer anymore.”

For heavier calculations, Bullet uses ClickHouse’s [refreshable materialized views](https://clickhouse.com/docs/materialized-view/refreshable-materialized-view), which let you schedule a view to recompute on a fixed interval rather than triggering on every insert. The trading leaderboard is a good example. Calculating P&L rankings requires joining account snapshots with deposit and withdrawal histories, accounting for the fact that deposited money shouldn’t count toward returns. The query spans six common table expressions with window functions across multiple joins.

In Databricks, this query ran as a 60-minute cron job and took 20-30 minutes to execute, meaning leaderboard data was up to 90 minutes stale by the time it updated. “It was a massive headache,” Tristan says. “For a real-time trading application, that made it kind of boring and not very engaging for a lot of people,” he adds.

In ClickHouse, the equivalent refreshable materialized view runs every 10 minutes, and could be pushed to every minute if needed. As Tristan says, “It’s easy to maintain, and it just works very well out of the box.”

## The results: faster data, fewer moving parts

In the end, switching from Databricks to ClickHouse Cloud cut query latency from 10-15 seconds to milliseconds, a roughly 10,000x improvement. “If you care about building real-time applications or doing real-time analytics, this is where ClickHouse really shines,” Tristan says. “You can query stuff insanely fast. Instead of using things like Spark, which take a long time, you’re getting stuff within milliseconds.”

Data freshness, meanwhile, went from 1-2 hours to less than 5 seconds, meaning traders see their leaderboard positions, referral rewards, and P&L charts in near-real-time. The monthly cost is comparable to Databricks, but ClickHouse now handles 1,000x more data across staging, testnet, and mainnet environments. “It’s not a fair comparison,” Tristan says.

For a lean data engineering team, ClickHouse Cloud has removed a lot of the maintenance burden associated with managing infrastructure. “Being a fast-growing startup, it was nice to offload as much of that work as possible,” he says. “I don’t want to be sitting there running clusters and tuning things and doing all this stuff as well as hiring people and running the company.”

With [ClickHouse Cloud](https://clickhouse.com/cloud), Tristan and the team have simplified their entire data stack, replacing a fragile multi-system architecture with a single database that handles ingestion, analytics, and monitoring at scale. They can focus on building the fastest, most feature-rich trading exchange in DeFi, without a data engineering team of one being the bottleneck.


---

## Get started today

Interested in seeing how ClickHouse works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-1318-get-started-today-sign-up&utm_blogctaid=1318)

---