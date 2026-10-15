---
title: "How Ridgeline unified Iceberg and ClickHouse into one analytics layer for investment management"
date: "2026-10-14T17:36:29.534Z"
author: "ClickHouse"
category: "User stories"
excerpt: "Ridgeline rebuilt its performance analytics on ClickHouse Cloud, querying decades of Iceberg history alongside recent data so it can serve investment managers 10x larger than before and more than double the customers live on its platform."
---

# How Ridgeline unified Iceberg and ClickHouse into one analytics layer for investment management

## Summary

- Ridgeline uses ClickHouse Cloud to power performance analytics for its cloud-native, all-in-one investment management platform.
- They chose ClickHouse for its analytical performance and affordability over Redshift, SingleStore, Postgres columnar plugins, and a custom in-memory engine; and ClickHouse Cloud for its security and governance features.
- The performance boost has allowed Ridgeline to serve customers 10x larger than before and more than double the number of customers live on the platform.

Most asset managers run trading, accounting, reporting, CRM, and analytics as separate systems, stitched together and reconciled after the fact. [Ridgeline](https://ridgeline.ai/) brings them all together on a single platform with a unified data model and built-in AI. “We’re trying to be that all-encompassing, all-in-one offering,” says Hayden Hudgins, manager of performance measurement and analytics.

Inside the company, Hayden’s team sits downstream of trading and accounting, turning raw transaction numbers into investment performance and analytics. Did a portfolio make money or lose money? Why did that happen? What are the impacts to the portfolio and weightings inside it?

Two things have to be true for any of it to work. “Across Ridgeline, a big thing is speed and accuracy,” says technical product manager Erin Corrado. “We have to be very fast—that’s a market differentiator—and also accurate, because if we give wrong reporting numbers or stale data, we’re going to hear about it from our customers. ClickHouse gives us the leverage to perform these types of analytical queries very quickly and accurately.”

We caught up with Hayden and Erin to learn how they rebuilt Ridgeline’s performance analytics, from the wall they hit with Postgres, to their decision to build on [ClickHouse Cloud](https://clickhouse.com/cloud) on AWS, to the 10x architectural shift that has helped them more than double their customer base.

## Moving upmarket, and outgrowing Postgres

Ridgeline is “primarily a Postgres shop,” Erin says, “Postgres is very good at transactions; if you have accounting or trades, it’s excellent at that. But if you have these big complex aggregations where you have to pull a lot of data together and analyze them, ClickHouse is the clear winner.”

Two years ago, Ridgeline began onboarding a class of customer roughly 10 times larger than anything it had seen before. The workload is unforgiving to begin with. Ridgeline derives daily profit-and-loss data for every portfolio in the system, and the resulting tables are wide: on the order of 40 to 80 columns written for each portfolio, every day. The analytics running on top of that data are less like queries and more like math. “A lot of these reports require us to pull in this data and then do what is effectively an integral in SQL,” Hayden says.

Under the old customer load, Postgres held up. But as Ridgeline moved upmarket, the asks got bigger. As Hayden recalls, “It got to the point where we would need to calculate inception-to-date reports for portfolios that go back decades at daily granularity, and do it over thousands of portfolios.”

At that scale, one of two things could happen. Because Ridgeline runs a shared infrastructure layer, with the Postgres instance common to multiple teams, the performance team would effectively consume the entire cluster to compute a single report. Or the job would run into a hard ceiling. “We’d be using up all of our memory capacity, constantly vertically scaling our Postgres box,” Hayden says. Running these upmarket reports on the original system would likely have taken hours or potentially not even complete.

The customers Ridgeline wanted to bring onto the platform that year represented a 10–40x increase in volume. No version of the existing architecture could absorb that. “It was a requirement for getting these customers live,” Hayden says. “We had customers we wanted to sign and get live to move our business upstream, and the way we saw it, we had to provide these capabilities.”

## Choosing ClickHouse Cloud for its security and governance

When evaluating potential solutions, Ridgeline’s criteria started with a pass/fail question: could they service these reports at all? Whatever survived that was judged on a “sliding scale between performance and cost,” Hayden says. “What’s the fastest solution we can get that’s cost effective?”

The team looked at Redshift, at Trino over Iceberg, at SingleStore, at plugins that would let Postgres behave more like a column store. They re-examined whether the problem was Postgres itself or the way they were using it. They even considered writing a calculations engine from scratch, in memory, with its own data typing.

In the end, ClickHouse won on performance and it also came at a lower cost than the other analytical stores Ridgeline priced.

The next decision was how to run it. They started by self-hosting ClickHouse and got a working version running in staging. Then they asked what productionizing it would cost. “After a lot of conversations with our principal engineers and C-level executives, we decided we didn’t want to invest in figuring out how to run this and operationalize this,” Hayden says.

That left [ClickHouse Cloud](https://clickhouse.com/cloud) and [Bring Your Own Cloud](https://clickhouse.com/cloud/bring-your-own-cloud). The deciding factor was security. Ridgeline is a financial services company operating under SOC 2, and BYOC at the time meant granting a third party a footprint inside Ridgeline’s own VPC. (BYOC is now generally available on [AWS](https://clickhouse.com/blog/announcing-general-availability-of-clickhouse-bring-your-own-cloud-on-aws) and [Google Cloud](https://clickhouse.com/blog/byoc-gcp-ga), with the data plane running inside the customer’s own account, and SOC 2 Type II coverage extending to BYOC deployments.) ClickHouse’s managed service was the cleaner option. Ridgeline wrote ClickHouse into its data-sharing agreements and governed the relationship with straightforward ingress and egress rules.

The isolation requirements were unique enough that Ridgeline’s engineers and ClickHouse’s engineers designed the structure together. Ridgeline needed data at rest isolated across environments that aren’t permitted to touch each other, so it runs separate ClickHouse organizations for staging and production, sharing credits across them, with individual ClickHouse services per customer beneath. Along the way, Ridgeline asked for API endpoints to provision that infrastructure programmatically (capabilities that now underpin the [Terraform provider](https://registry.terraform.io/providers/ClickHouse/clickhouse/latest/docs) available to every ClickHouse Cloud customer). “I’d like to think it was a helpful partnership on both ends,” Hayden says.

ClickHouse Cloud also absorbed work the team would otherwise own outright. Ridgeline runs primary and secondary regions with failover between them for business continuity, and they worked with ClickHouse support to build the recovery capabilities they needed. “If we had just taken open-source ClickHouse and tried to manage everything ourselves, it would have been a much heavier burden,” Erin says.

## Querying Iceberg data through ClickHouse

Today, accounting data, generated inside Ridgeline, is written directly into ClickHouse. Vendor data (e.g. custodian feeds, pricing data) lands transactionally in Postgres, where it belongs, and replicates into ClickHouse via [ClickPipes CDC](https://clickhouse.com/cloud/clickpipes). And historical data, which arrives from customers’ legacy providers in enormous volumes, takes a third path.

That third path was its own 10x problem. Ridgeline could handle hundreds of millions of rows of history without much ceremony, but as the business moved upmarket, customers started showing up with one billion rows, then two billion. So the team built a Spark pipeline that ingests those bulk uploads and lands them in [Iceberg](https://clickhouse.com/blog/clickhouse-is-data-lake-ready), where storing decades of history is more economical. Adapters built by Erin’s team then pull that Iceberg data into ClickHouse on demand.

> “We need a full view of what happened from the inception of the portfolio to where it is today in the Ridgeline system. That’s what Iceberg tables plus ClickHouse provide us.”
>
> — Hayden Hudgins, Performance Measurement and Analytics Manager, Ridgeline

Recent data lives in ClickHouse, hundreds of gigabytes per tenant, typically covering two to four years. Older data stays in Iceberg and is read through ClickHouse’s Iceberg connector. “The 40-millisecond hit of that connector is fine,” Hayden says. “If you’re querying 40 years of data, people expect it to be slightly slower.”

![](https://clickhouse.com/uploads/ridgeline_oct2026_image1_3fa0bb96f5.png)

Hayden notes that [materialized views](https://clickhouse.com/docs/concepts/features/materialized-views) have become the “backbone” of what his team provides. They now run a series of materialized views that transform write-side data into optimized read-side views, with the [ReplacingMergeTree table engine](https://clickhouse.com/docs/reference/engines/table-engines/mergetree-family/replacingmergetree) reconciling everything in the background. “We’re defining the SQL and saying, okay, we trust that the MergeTree logic inside ClickHouse is going to get things where they need to be,” he says. He adds that while the performance gains are great, the ease of development matters just as much. “We can write one within a day and we know it’s going to materialize the way we want.”

## What ClickHouse unlocked for Ridgeline

The clearest measure of the project’s success is the size of the customers Ridgeline can now bring onto the platform. The old architecture had a hard size threshold that capped the business’s growth. With ClickHouse, the company has more than doubled the number of customers running on the platform, while moving decisively upmarket.

> “The key unlock was getting customers live that we couldn't have previously been able to. If we hadn’t shipped those 10x architectural changes, we wouldn’t have been able to sign the contracts we ultimately did.”
>
> — Hayden Hudgins, Performance Measurement and Analytics Manager, Ridgeline

Day to day, the difference shows up in the performance reports Ridgeline’s customers rely on. These are multi-page PDFs produced in giant batches, one for every portfolio under management. With ClickHouse, batches that once ran for hours now complete in minutes. And importantly, those reports are reviewed and re-run before they go out.

Under the old system, that loop would have been measured in coffee breaks or overnight waits. As Hayden recalls, “It was, okay, I’m going to kick this thing off and go get lunch or a cup of coffee, then come back later and check it.” Now a change made in one part of the system flows through the pipeline and materialized views within about a minute, the report re-runs against ClickHouse, and the customer can validate that the numbers changed as expected.

As Erin points out, the end users never see any of this. “They don’t really care if it’s ClickHouse or whatever else,” she says. “They just see a performance report.”

## Building toward the next 10x leap

With [ClickHouse Cloud](https://clickhouse.com/cloud) as a foundation, Ridgeline is already thinking about the next threshold. Internally, the team talks about “whale scale” customers running portfolios that are another order of magnitude larger than those of Ridgeline's current customers. “We 10x’d a year or two ago,” Hayden says, “and we’re trying to do it again.”

That includes deeper functionality on data the platform is only now able to hold. As Hayden explains, “With Iceberg and ClickHouse, customers can bring large volumes of historical performance data into Ridgeline and make that history available alongside Ridgeline-calculated results, preserving Inception-to-Date performance reporting across their transition to Ridgeline.”

It also includes new territory inside the company. Ridgeline’s reconciliation team is evaluating ClickHouse for a near-real-time analytics dashboard a prospective customer has asked for. “It’s looking like the only way to really have that in near real time is ClickHouse,” Erin says. “That’s just not doable with our other current tooling.”

The pattern that started in performance analytics is spreading. “We’re finding more use cases where our Postgres story is just not going to make it,” she adds. With ClickHouse Cloud, the team has somewhere to put those workloads. “There are definitely more items on the roadmap for ClickHouse within Ridgeline,” Hayden says.

---

## Get started today

Interested in seeing how ClickHouse works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-2623-get-started-today-sign-up&utm_blogctaid=2623)

---