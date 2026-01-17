---
title: "Billions of transactions, two-thirds lower cost: Why ProcessOut switched from Elasticsearch to ClickHouse Cloud"
date: "2025-09-29T11:36:42.112Z"
author: "ClickHouse Team"
category: "User stories"
excerpt: "ProcessOut replaced a costly, slow, hard-to-change Elasticsearch setup with ClickHouse Cloud, lowering costs by two-thirds and reducing latency from minutes to ~2 seconds."
---

# Billions of transactions, two-thirds lower cost: Why ProcessOut switched from Elasticsearch to ClickHouse Cloud

For most companies, payments are like plumbing—necessary but opaque, and often a source of frustration. The team at [ProcessOut](https://www.processout.com/) sees it differently. With their payment orchestration platform, they’re on a mission to make payments a superpower for growth.

“We’re passionate about helping brands optimize their payments and use them to realize their boldest business ambitions,” says Maaike Bosch, the company’s CMO.

Founded in 2015, ProcessOut offers five core capabilities—smart routing, monitoring (analytics), payment vaulting solutions, payment method management, money reconciliations—giving merchants the flexibility to connect with multiple payment service providers (PSPs), expand into new markets, and improve performance without adding technical debt.

Data is a huge part of that. Merchants use ProcessOut not only to process transactions, but to see what’s happening in real time, compare authorization rates across providers, detect anomalies, benchmark against anonymized industry data, and export raw events for deeper analysis. Underneath it all is [ClickHouse Cloud](https://clickhouse.com/cloud), powering everything from live dashboards and self-serve analytics to internal experimentation that drives new features.

We caught up with Maaike and software engineer Josh Thomas to learn why they decided to replace their Elasticsearch-based data architecture, how they landed on ClickHouse Cloud, and the impact it’s had so far.

## Outgrowing Elasticsearch

Josh joined ProcessOut in January 2022, two years after the company was acquired. One of his first tasks was figuring out how to get more out of the platform’s data. “As a payment orchestration platform, we’re always looking for ways to add value on top of the PSP,” he says. “A big part of how we do that is through data.”

At the time, ProcessOut’s analytics layer was running on Elasticsearch. “It had worked for a long time,” Josh says, “but as we scaled, it got very expensive, both in money and time, to make changes or grow the infrastructure.” And with Elasticsearch’s sharding model, he explains, there was no easy way to just “throw more money” at the problem.

Those limitations became a catalyst for something bigger: a complete rebuild of ProcessOut’s data architecture. The goal was to modernize the stack, speed up development, and give a newly formed cross-functional data team the tools to experiment more easily.

“We realized that if we wanted a more modern data architecture and a faster way of building new data products, we needed a different solution for storing that data,” Josh says.

![po_1.png](https://clickhouse.com/uploads/po_1_0198d16e0d.png)

## Choosing ClickHouse Cloud

When the rebuild began in 2023, Josh was the only backend engineer on the project. That made one requirement non-negotiable: low maintenance. “From the get-go, the new database had to be simple to run,” he says. “I needed as few things to go wrong as possible.”

Their initial shortlist included Apache Pinot and Apache Druid, but as Josh puts it, “We realized we definitely wanted a managed solution.” They looked at Tinybird and other hosted ClickHouse solutions before deciding on ClickHouse’s own managed service, [ClickHouse Cloud](https://clickhouse.com/cloud).

From the start, they were drawn to ClickHouse’s simplicity. As Josh explains, its [single-binary deployment](https://clickhouse.com/docs/integrations/data-formats/binary-native) made prototyping easy. He recalls spinning up [clickhouse-local](https://clickhouse.com/docs/operations/utilities/clickhouse-local) as a “really cool moment… you could get an idea of the engine very quickly. It’s really easy to get off the ground and very intuitive to use.”

Along with low maintenance, the team’s requirements included speed, scalability, easy ingestion, and the ability to experiment quickly. Cost efficiency was high on the list, too, and ClickHouse Cloud’s [compute-storage separation](https://clickhouse.com/docs/guides/separation-storage-compute) (with data stored on S3) was a big draw. “This made it massively more cost-efficient than storing data on disk,” Josh says.

Coming from Elasticsearch, Josh also found it “refreshing” that [ClickHouse uses SQL](https://clickhouse.com/docs/sql-reference). “You didn’t need to know anything else, really. It’s very easy for anybody to start using.” 

And while ClickHouse Cloud had only just gone GA in December 2022, Josh was encouraged to see that so many of the top contributors to the open-source project worked for ClickHouse. “It just seemed like a well-provisioned company,” he says.

## Speed, scale, and two-thirds cost savings

Today, ClickHouse Cloud stores roughly 35 TB of ProcessOut’s payment data. It actually takes Josh a moment to look up the total, as he doesn’t think about it much. “That’s the beauty of it being stored on S3,” he says. “I’m not paranoid about the costs growing.” That storage covers billions of transactions each year, plus many more events with batched writes factored in.

One of the clearest benefits of the new setup is cost efficiency. Since replacing Elasticsearch with ClickHouse Cloud, ProcessOut’s analytics costs have dropped by two-thirds.

Performance has also taken a big leap. Where Elasticsearch relied on a cron job that could lag minutes behind, transactions now land in ClickHouse with about two seconds of end-to-end latency. “Once we realized how fast you can upsert data in ClickHouse, our requirements started getting stricter, because we realized we could probably push it,” Josh says.

Internally, ClickHouse powers much of ProcessOut’s daily work to improve merchants’ payment performance. A lot of that analysis is still done manually through ad hoc queries, which Josh calls ClickHouse “perfect for.” The team also uses the ClickHouse console to inspect data directly, making it easier to troubleshoot, verify, and iterate on new ideas.

That ease of iteration has opened the door to more experimentation. “Before, with Elasticsearch, it was very painful to make any changes,” Josh says. “Whether it was adding a field or creating a whole new model, we basically didn’t do it, because nobody wanted to go near it. But because ClickHouse Cloud is just SQL, we can be flexible in our implementation while ensuring that all compliance requirements are met .”

That agility, he adds, has “increased how many bets we can take” when building new tools and features—a force multiplier that translates into a better experience for customers.

![po_2.png](https://clickhouse.com/uploads/po_2_cd858bac4d.png)

## Payments as a superpower

ProcessOut is already exploring additional ClickHouse features like [refreshable materialized views](https://clickhouse.com/docs/materialized-view/refreshable-materialized-view). “Being able to transform data async without having to bring in another orchestration system external to ClickHouse is really nice,” Josh says. With a new cross-functional team but still just one backend engineer, minimizing complexity is key. “If we can contain something within ClickHouse, that’s really valuable to us, and it also helps upskill the team.”

Looking ahead, Josh sees ClickHouse as the foundation for even richer analytics. The team plans to incorporate “many more sources of data” and use periodic transformations to join them together. “That way, you can get more insights about your payments, essentially.” And with ClickHouse Cloud taking care of scale and operations, the team can focus on building capabilities rather than managing infrastructure.

For ProcessOut, those insights go right to the heart of their mission: simplifying payments and helping brands turn them into a growth driver. As Maaike puts it, “Payments don’t have to be complex—they can actually be the superpower of your company.”

Curious how ClickHouse can transform your team’s data operations? [Try it free for 30 days](https://clickhouse.com/cloud).
