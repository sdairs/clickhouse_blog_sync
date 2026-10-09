---
title: "How we migrated Clera’s 500 GB production database to ClickHouse Managed Postgres overnight"
date: "2026-10-08T20:51:48.827Z"
author: "Daniel Wintermeyer"
category: "User stories"
excerpt: "Clera migrated its 500 GB production database and 500+ tables to ClickHouse Managed Postgres overnight, cutting CPU usage from 100% to 10–20%."
---

# How we migrated Clera’s 500 GB production database to ClickHouse Managed Postgres overnight

## Summary

Clera, an AI talent agent representing 200,000+ candidates, runs their operational database on ClickHouse Managed Postgres after outgrowing their previous provider. The team evaluated Supabase, Neon, and PlanetScale, choosing ClickHouse Managed Postgres for its NVMe-backed performance, which won on both their own production workload and sysbench TPC-C, a standardized benchmark. They migrated 500+ tables from the EU to the US overnight, with production traffic still hitting the database; CPU usage dropped from days at 100% to 10 to 20%.

*This is a guest post by Daniel Wintermeyer, CTO and co-founder of [Clera](https://www.getclera.com/), and founding engineer Julian Bouchard. The original post lives on Clera’s blog [here](http://www.getclera.com/blog/how-we-migrated-to-clickhouse-managed-postgres).*


Hiring is broken. Candidates apply into the void, founders drown in resumes they don’t want to read, and the people who’d be a great fit almost never end up in the same room. We decided there had to be a better way. You don’t search for a job. You talk to [Clera](https://www.getclera.com/). 

We’re an AI talent agent that works on both sides of the market, representing more than 200,000 candidates and helping them get hired at mostly pre-seed to Series B companies in New York and San Francisco. Right now, the platform has around 2,250 live jobs, and more than 2,000 new candidates are joining every day.

Under the hood, we run a multi-agent system. On the candidate side, you sign up, talk to us through email, iMessage or a chat interface, and agents handle everything from first intake and getting to know your preferences, through to proposing and matching you to the right roles. On the company side, we sit in the founders’ Slack channels and introduce candidates directly, so there’s no application step. We only propose jobs that are a fit, and we curate hard enough that around 50% of the intros we make lead to an interview. Since we work on a success-based fee, what matters to us is people getting placed somewhere they want to work.

The biggest part of the system is data. Every intake conversation, job listing, and signal about who’s a fit for what role feeds the matchmaking engine, and that engine is only as good as the data behind it. It turns out this is a really hard issue to solve.

## Outgrowing our old database vendor

At the time of migration we ran more than 500 GB of data on Postgres (now closer to a terabyte). Before we migrated to ClickHouse Managed Postgres, we ran into many, many issues with our previous database vendor.

One of the clearest examples was a single talent query, a candidate lookup that should have been instant, but instead took around three seconds. We had analytical queries everywhere, and stretches where the database sat at 100% CPU for six straight days. There were also timeouts, and missing and failed writes. If you’ve faced these, you know how painful they are, because you need to retry, and you really don’t want your database letting you down. At its worst we had bursts where we couldn’t even write an update to a table from a primary key.

When Julian looked at our workload, it broke into three types:

* **Hot reads**: the smaller CTEs, job listing queries, and materialized view reads that need to come up quickly when someone browses the site.   
* **Point lookups**: the tiny primary key reads and writes that should be sub-millisecond when nothing blocks them.   
* **Background work**: the heavy analytics CTEs that the team runs or dashboards show, plus materialized view refreshes for SEO. 

The biggest pain was point lookups. They were taking multiple seconds because they were getting blocked by the background queries. On top of that, we scrape a lot of data, so we get spiky scrape bursts that pile IOPS, CPU, and wall-clock time on top of everything else.

We decided we needed an operational Postgres where point lookups stay fast while analytics and scrape bursts run alongside, with storage that can take the IOPS, managed by someone else. We’re not really database people. We wanted something that just works.

## Choosing ClickHouse Managed Postgres

We started by evaluating four vendors: Supabase, Neon, PlanetScale, and [ClickHouse Managed Postgres](https://clickhouse.com/cloud/postgres). We didn’t know ClickHouse was an option until our friends at [Langfuse](https://langfuse.com/) were like, “Oh, by the way, ClickHouse is now also in the running for this. They have managed Postgres with NVMe storage. You should talk to them as well.”

We tested the vendors in two ways. First on our own production data, replayed under simulated load on the workload we actually run, and second with a standardized benchmark, to get a generalizable number that other providers publish results on.

## Benchmarking our production workload {#benchmarking_our_production_workload}

For the replay, we loaded around 500 GB of production data onto all four providers and ran the three query classes above, measuring:

* Queries per second (QPS)  
* P99 latency  
* Error percentage  
* Acquire times  
* Wait events (how often stuff was being blocked that we didn’t want blocked) 

Julian tried running everything through each provider’s pooler, but the poolers all had different settings and equalizing them wasn’t worth it, so the final numbers are on direct connections.

ClickHouse Managed Postgres won nearly everything, especially IOPS. The difference was [local NVMe storage](https://www.ubicloud.com/blog/postgresql-performance-local-vs-network-attached-storage) versus the network-attached storage most providers use, which adds latency on every disk read and write. That alone was enough to immediately eliminate Supabase and Neon, leaving PlanetScale and ClickHouse.

## Validating the benchmark with TPC-C {#validating_the_benchmark_with_tpcc}

We then ran sysbench TPC-C. It’s basically a business-simulating dataset with a mix of read and write queries. (It’s important to note that sysbench isn’t fully TPC-C compliant, but it gives us a comparable baseline.) Both providers ran on the same machine class with 500 GB of generated data. One experiment was 8, 16, 32, 64, and 128 threads, three times back to back, so we could measure variance between runs as well as throughput. We ran multiple experiments, once again tracking QPS, P99, and error rate, and this time measuring transactions per second (TPS) and variation as well. 

ClickHouse Managed Postgres swept again. Stock, without touching anything, its throughput advantage ranged from around 16% at 128 threads to 42% at 16 threads:

![](https://clickhouse.com/uploads/planetscale_clickhouse_postgres_tps_table_preview_caed406a40.png)

It’s important to note, that they don’t run the same PostgreSQL settings out of the box. Tuning is part of each provider's offering but can be manually adjusted to a degree. So we got feedback from PlanetScale on how to equalize these, which we took into account, though we couldn’t test huge pages without going through their engineering team.

Everything is in an [open-source repo on GitHub](http://github.com/getclera/ps-vs-ch-benchmark), including all the results, logs, scripts, and Terraform files, plus a short LaTeX write-up and a dump of context for your LLMs. Please take a look, scrutinize it, reproduce it, and email us if there are mistakes. If you’re evaluating a database of any type, we encourage you to run something like this yourself and make it open source. You can be wrong, and then people can correct you. That’s the beauty of sharing knowledge in a community.

## Migrating the database overnight with ClickPipes

![](https://clickhouse.com/uploads/clera_oct2026_image2_a3a8515192.png)

It was a Thursday when we decided to go with ClickHouse Managed Postgres. On Friday morning, Daniel got a flat white and walked into our 10 a.m. daily prepared to talk about the upcoming migration. Julian said, “Oh, by the way, we’re already on ClickHouse.”

At 11 p.m. the night before, Julian had finished the final prep work. He knew that if we did all the prep and then sat on it, we’d keep pushing it out. So, figuring it would have to be done eventually, he decided we might as well do it now.

For the prep stage, we followed [ClickHouse’s migration guide](https://clickhouse.com/docs/products/managed-postgres/migrations/clickpipes). On the source side, that meant WAL lifetime settings, enabling publications, and pre-checks on keys and extensions. Extensions were the biggest pain. Postgres offers a wide variety of them, and some providers have very specific extensions that don’t port anywhere else. Julian had spent a few days beforehand changing parts of the system to get around that and make sure we could cleanly migrate to any provider.

He set up two [ClickPipes](https://clickhouse.com/cloud/clickpipes) pipelines, one for the core data and one for the non-essential data, so he could focus on the core data and let both run in parallel. Our founding team is German and our database had been in the EU, so we took the opportunity to move it to the US at the same time. That’s 500+ tables crossing the Atlantic while production traffic was hitting it. At one point during testing, Julian ran into an issue due the EU latency + table volume combo. Someone at ClickHouse made a PR for it at 11 p.m. That kind of responsiveness was nice and made the transition a lot easier.

The migration itself was easy enough. The harder part was putting the triggers back, rebuilding the indexes, and resequencing tables. Then there were parity checks and the actual cutover, redeploying the entire system pointing at the new database and making sure nothing was breaking too hard. It all had to be done quickly, because we apply a lot of schema changes and you don’t want people changing the old schema while the new one has already been copied. By 6 or 7 a.m. it was mostly monitoring and cleanup. After the 10 a.m. daily, Julian went to bed.

## Faster queries and ready to scale

With ClickHouse Managed Postgres, everything loads a lot faster for our users and internal admins, who use our tooling every day and are very grateful. No one’s afraid anymore that someone on the team will randomly run a multi-hour analytics query that takes the whole system down. That used to happen on occasion, but not anymore.

Just as important, we have room to breathe. We’re currently sitting around 10 to 20% CPU usage most of the time. We haven’t changed a single setting since the migration. The out-of-the-box performance was already tuned for what we needed, and for us it just worked. Price-wise, it’s about where we were before, if anything slightly cheaper, but with better performance and scalability.

It’s worth noting we didn’t migrate to ClickHouse the analytics database. We migrated to their managed Postgres service, which is essentially vanilla Postgres backed by local NVMe storage instead of network-attached disks. Right now that’s all we need, but if the analytics side of the business ever outgrows it, the path is there. Managed Postgres can sync to ClickHouse when we need it to. In the meantime, we’re confident we can throw a lot more at the system.

**By the numbers**

* 500 GB migrated (now closer to 1 TB)  
* 500+ tables moved from the EU to the US  
* 1 night, from final prep to cutover  
* 100% → 10 to 20% CPU  
* Up to 42% more TPS than the runner-up on sysbench TPC-C  
* 0 settings changed since migration

---

## Get started with ClickHouse Managed Postgres today

Interested in seeing how ClickHouse Managed Postgres works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?intent=pg&loc=blog-cta-2562-get-started-with-clickhouse-managed-postgres-today-sign-up&utm_blogctaid=2562)

---