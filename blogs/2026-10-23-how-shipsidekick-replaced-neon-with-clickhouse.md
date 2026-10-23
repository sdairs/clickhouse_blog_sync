---
title: "How Shipsidekick replaced Neon with ClickHouse Managed Postgres for 10x faster queries and better reliability"
date: "2026-10-23T10:11:36.150Z"
author: "ClickHouse"
category: "User stories"
excerpt: "Shipsidekick moved from Neon to ClickHouse Managed Postgres in a single weekend, cutting CPU usage from 100% to 5-10% and making queries about 10x faster."
---

# How Shipsidekick replaced Neon with ClickHouse Managed Postgres for 10x faster queries and better reliability

## Summary

- Shipsidekick uses ClickHouse Managed Postgres to power its combined warehouse, order, and transportation management platform for shippers and 3PLs.
- After struggling with frequent Neon, a Databricks company, outages and slow support, Shipsidekick migrated in a single weekend, with ClickPipes replicating 500 GB of data in 4-5 hours.
- Since the migration, CPU usage has dropped from 100% to 5-10%, cache hit rate has risen from 30-35% to 99%, and queries run about 10x faster.

Sawyer Bateman has spent most of his career thinking about shipping and logistics. In the fall of 2024, Sawyer started his new company, [Shipsidekick](https://www.shipsidekick.com/). It’s focused on “the next layer of the logistics stack,” combining warehouse, order, and transportation management into a single platform for shippers and 3PLs, with an AI sidekick that helps teams manage their operations. Shipsidekick is a web application, with all the screens, reports, and user sessions that come with it.

“I’m not a database guy,” Sawyer told the crowd at an [August 2026 ClickHouse meetup in Vancouver](https://www.linkedin.com/posts/were-heading-to-vancouver-clickhouse-share-7495289403422953473-BlXz/). This is the story of how a self-described “generalist founder” and his team chose [ClickHouse Managed Postgres](https://clickhouse.com/cloud/postgres), migrating away from Neon, and how the migration made queries about 10 times faster and their database far more reliable.

<iframe width="768" height="432" src="https://www.youtube.com/embed/C32-hYFSQXk" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

## The challenges with Neon

After previous experience building companies using a Ruby on Rails monolith on MySQL more than a decade earlier, Sawyer wanted to try a more modern framework. He built Shipsidekick as a Next.js app deployed on Vercel. Following the standard advice at the time, he paired the serverless application with a serverless Postgres provider and landed on Neon.

“Neon was okay for a little while,” he says. That changed, however, when Shipsidekick turned on Vercel’s new Fluid compute. The hybrid model was cheaper and more performant on the application side, but it immediately caused trouble with Postgres connection pools.

The old pooling stack, Sawyer explains, had three layers, and fixing one only broke another. Prisma, Shipsidekick’s ORM, maintains its own internal connection pool. Vercel wants you to create a `pg` pool, pass it to Prisma, and attach it to a plugin that shares connections across Fluid compute sessions. Neon sits behind a PgBouncer instance that advertises 10,000 pooled connections, “but they share it between we don’t know how many people,” Sawyer says.

“We just had tons of problems trying to tune,” he adds. “No matter how we sliced it, we ended up hitting pool exhaustion and pool timeout issues… we would either get the Prisma pool getting exhausted, or the Vercel fluid pool getting exhausted. If we took some of those pools away, we would get errors from Neon because we’d hit their PgBouncer limits.”

Failures became easy to predict. “We would go down the minute we crossed like 3,000 connections, no matter what,” he says. The instance was always CPU-capped, and RAM was saturated. Monday, when customers ship orders from the weekend, was the toughest day of the week. “We would have to shut off our Neon database every Monday when things got busy.”

Neon’s support was of little help. One urgent ticket, filed while the database was down, didn’t get a response until 38 hours later. Another took six days. Meanwhile, Neon (acquired in 2025 by Databricks) kept emailing to suggest Shipsidekick upgrade to Databricks Lakebase. “Both the technology limitations and vendor support weren’t meeting our needs,” Sawyer says. “We had to navigate many stressful situations on our own.”

By mid-2026, Sawyer had scaled Neon to the top of its autoscaling range, 16 compute units (about 64 GB of RAM). “We were paying a lot,” he says, noting that even with a bill of nearly $2,300 a month, their cache hit rate topped out at 30-35%, and customers were emailing about slow load times. “At that point, I decided we needed a new solution.”

## Why they chose ClickHouse Managed Postgres

They evaluated PlanetScale, whose Metal offering with NVMe-backed storage was appealing. But PlanetScale’s high-availability setup requires two replicas, so “you’re essentially paying for three databases,” Sawyer says. His estimate came to $4,000-5,000 a month.

Then he saw a [post by ClickHouse on Hacker News](https://news.ycombinator.com/item?id=48872874). It showed [how the team scaled PgBouncer to 4x throughput](https://clickhouse.com/blog/pgbouncer-clickhouse-managed-postgres) in [ClickHouse Managed Postgres](https://clickhouse.com/cloud/postgres). “Because we’d been fighting with PgBouncer so much, I thought that was very interesting,” Sawyer says.

Several other things attracted him. First, he says, “the pricing was fantastic.” ClickHouse Managed Postgres also offered more instance options than PlanetScale, with “just the right mix of CPU, memory, and storage.” The 16 vCPU, 128 GiB RAM, 3.7 TB storage-optimized instance he chose, with one standby. Even at full price, it came in well under his PlanetScale estimate.

Part of the difference is that ClickHouse lets you run a single standby rather than requiring two. “Instead of having write consensus on committing your writes, they just stream the writes to the standby,” he explains. “Maybe you lose a second of writes if you have to fail over. I’m okay with that for a third cheaper and increased write performance.”

Another draw was the [documentation](https://clickhouse.com/docs/products/managed-postgres/overview). “The docs that ClickHouse has put together for Postgres are incredible,” Sawyer says. “This does not feel like a new product. Nothing in the docs was ever incorrect, out of date, or led us astray.”

And then there were the people. Researching the product, Sawyer found a Reddit thread where [Sai Srirampur](https://www.linkedin.com/in/sai-krishna-srirampur-1741b019), who leads ClickHouse Managed Postgres after the acquisition of his former company PeerDB, was answering questions in public. “Seeing the ClickHouse team talking openly with commenters,” Sawyer says, “that gave us a lot of confidence.”

## “The migration process was dead simple”

Sawyer created an account on July 16th. Sai personally emailed him the same day, and within a couple of hours they were in a shared Slack channel. That responsiveness is a welcome change. “I have no doubt that if we were down with ClickHouse, we would have a response within minutes, if not seconds,” Sawyer says.

He calls the migration process “dead simple.” The team followed ClickHouse’s [Neon Postgres source setup guide](https://clickhouse.com/docs/integrations/clickpipes/postgres/source/neon-postgres): enable logical replication on Neon, create a ClickPipe from the Data Sources panel in the ClickHouse console, and let it replicate. Shipsidekick had around 500 GB of data at the time. Sai estimated replication would take a day and a half. It ended up taking four or five hours.

At the Vancouver meetup, Sawyer flagged one hiccup for anyone following the same path. A cron job in the application ran multiple transactions that, replicated mid-flight rather than in their end state, tripped a partial unique index on the invoices table. “The solution was very simple,” Sawyer says: drop the offending index, let replication finish, then re-create it.

[ClickPipes](https://clickhouse.com/cloud/clickpipes), he notes, handled the interruption gracefully. “Even though there was an error in the replication, it didn’t lose anything,” he says. “It literally just waited until the error was resolved, and then everything continued as if nothing was wrong.”

The other open question was connection pooling. Shipsidekick’s traffic is spiky by nature. A wave of Shopify webhooks can take the app from zero to 10,000 requests per second. On Vercel, that means spinning up many function instances, each with its own pool. Sawyer asked the ClickHouse team how to configure PgBouncer for a serverless environment. It turned out there was nothing to configure. ClickHouse Managed Postgres [bundles a PgBouncer instance with every server](https://clickhouse.com/docs/products/managed-postgres/connection#pgbouncer), so Shipsidekick pulled out the Vercel pools and connects straight to it. “Long story short, it was no problem,” Sawyer says.

## 10x faster queries, with 90-95% less CPU usage

The migration finished on a Sunday, since Sawyer wanted to cut over on a weekend. Monday, once the most stressful day of the week, came and went. “It was like crickets,” he says.

They saw the benefits right away. On ClickHouse Managed Postgres, CPU usage typically sits at 5-10%. “That’s fantastic to see after seeing it struggle at 100%, 24/7 on Neon,” Sawyer says. Connections to the actual Postgres database hover between one and 200 at any given time.

> “The ClickHouse Managed Postgres PgBouncer does a great job of absorbing whatever’s happening on Vercel. We don’t even bother to try to control the spiky request nature. It’s just fine. The cache hit rate was a big win, going from 30-35% to 99%.”
>
> — Sawyer Bateman, Founder and CEO, Shipsidekick

Between that jump in cache hit rate and ClickHouse Managed Postgres’s [NVMe-backed storage](https://clickhouse.com/blog/postgres-managed-by-clickhouse#why-postgres-managed-by-clickhouse), which keeps data on fast local disks rather than network-attached storage, performance is like night and day. “Our query times just cratered,” Sawyer says.

He ran a side-by-side test against the old Neon instance, still provisioned but with zero load. Pulling a month of shipment data (roughly 500,000 rows) took a minute and 20 seconds on Neon and about 6 seconds on ClickHouse. Two months of data, which wouldn’t complete at all on Neon, returned on ClickHouse in 20 seconds. “On average it’s 10 times faster than Neon, and in the best case, seemingly infinitely faster,” he says, “because half the time Neon would just not work.”

## AI agents and read replicas

On Neon, Shipsidekick had a small, cheap read replica that all its AI agents and MCP servers pointed at. Read replicas in ClickHouse Managed Postgres currently have to match the primary’s size (and price), so Sawyer initially skipped one and gave the agents a read-only role on the primary instead. “That was fine for a little while,” he says, until a team member’s agent ran a query that went unnoticed for a few days, buried in a tool call, pushing CPU to 40-50%. “I was like, okay, wake-up call. Your AI reads can impact your primary performance.”

To prevent this, they implemented statement and transaction timeouts on the read-only role. The longer-term fix was a dedicated read replica for the agents.

## Happier customers, with more analytics to come

Since the migration, Sawyer has been exploring what else to use ClickHouse for. The team is already using [ClickHouse Agents](https://clickhouse.com/docs/products/cloud/features/ai-ml/agents) for performance investigations, since the agents have access to the logs, Postgres statistics, and slow query data. “It’s been a fantastic foil to help us with what to do next and how to improve,” he says.

He’s also been asking the agents which workloads should move to ClickHouse proper, with Shipsidekick’s in-app dashboards being the natural first candidate. “We have dashboards in the application, but they’re slow,” Sawyer says. As the company’s analytics outgrow Postgres, the team is well-positioned to make that move. “I have a lot of faith now in ClickPipes because it worked so well for the migration,” he adds. “When it comes time to actually start using ClickHouse, it’s going to be obvious who we’re going to use.”

For Shipsidekick, what matters most is how the app feels to customers. Sawyer recalls a conversation a few days after the migration to ClickHouse Managed Postgres, with the same customer who had emailed about slow load times. “They were like, ‘I don’t know what you did, but the app’s fast now.’ And I was like, ‘I know what I did. We got rid of Neon.’”

From weekly outages and days-long support waits, to a weekend migration and a database that barely notices its busiest day, it’s been quite a turnaround for Shipsidekick.

> “We’re loving this unified platform, managing both ClickHouse and Postgres together. Everything’s fast, customers are happy, and so are we.”
>
> — Sawyer Bateman, Founder and CEO, Shipsidekick

---

## Get started with ClickHouse Managed Postgres today

Interested in seeing how ClickHouse Managed Postgres works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?intent=pg&loc=blog-cta-2782-get-started-with-clickhouse-managed-postgres-today-sign-up&utm_blogctaid=2782)

---