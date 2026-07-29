---
title: "How Fetch built its flexible agentic analytics tool on ClickHouse Cloud"
date: "2026-07-28T10:17:48.051Z"
author: "ClickHouse"
category: "User stories"
excerpt: "Fetch built FAST, a conversational BI agent on ClickHouse Cloud, so non-technical teams can query 150 billion rows a day in plain language and get answers in minutes instead of days."
---

# How Fetch built its flexible agentic analytics tool on ClickHouse Cloud

## Summary

- Fetch built FAST, its self-serve, conversational BI agent, on ClickHouse Cloud, which ingests over 150 billion rows a day from receipt and offer data.
- The team chose ClickHouse Cloud for fast ad hoc queries, compute isolation that keeps users’ workloads from colliding, and simple batch loading through ClickPipes.
- Answers that used to take days now come back in minutes, letting Fetch’s analytics team focus on harder problems instead of fielding constant one-off requests.


[Fetch](https://fetch.com/) is a popular rewards app, where every month, more than 13 million people shop online, scan receipts, play games, and get rewarded for what they buy. Those receipts give Fetch a 360-degree view of the consumer, which it uses to help brands build lifelong consumers while rewarding users for buying the products they already love.

In a single day, Fetch users snap over 13 million scanned receipts, with over 30 million line-items matched to a specific product, and 150 billion rows (50 TB uncompressed, 6.5 TB compressed) ingested into [ClickHouse Cloud](https://clickhouse.com/cloud) on AWS. As the company grew, all that data created an analytics bottleneck. In the words of Senior Analytics Engineer Brendan Sigale, “Fetch has an infinite amount of revenue-driving data, but a finite amount of people who know how to use it.”

> “Our sales and commercialization teams know our business and what matters to our brand partners. FAST helps them iterate on ideas quickly, build more powerful campaigns, and deliver better results for brands and users alike.”
>
> — Brendan Sigale, Senior Analytics Engineer, Fetch

Brendan joined us at [Open House SF 2026](https://clickhouse.com/openhouse/san-francisco), where he shared how Fetch built FAST, a flexible agentic analytics platform that lets non-technical teams across the company query purchase data in plain language and get answers in minutes instead of days.

## How FAST works at Fetch

FAST stands for “Fetch AI Semantic Technology.” It offers a familiar conversational UI where users can ask questions in plain language and talk to the data directly. “That makes speed really important,” Brendan says. “If you ask a question and then wait hours or minutes or even 30 seconds for a response, you get distracted, the creativity flow is gone…. that’s not an interactive experience.”

A basic example of how someone might use FAST is when a user planning a breakfast-category Offer asked, “How many people have bought orange juice in the last few months?” FAST interpreted the question, looked up how Fetch defines orange juice in its product taxonomies, mapped that against the semantic models for how to query the underlying tables, and returned an answer: about 2.6 million people.

From there, it got a bit more complicated. The same user wanted to know how many of those buyers also purchased muffins or breakfast breads. That’s an intersection of two groups, the kind of thing that’s hard to keep precomputed. “You run into scalability issues really fast,” Brendan says. The query ran, and the answer came back near 1.16 million.

Finally, he kicked things up a notch by narrowing the question to something no pre-aggregated table could answer: how many of those buyers also got bagels in the same shopping trip, with single-serve orange juice bottles filtered out? “There’s no chance you have that ready to go and pre-aggregated,” Brendan says. “You have to run this with a custom query.” 

That’s exactly what FAST did, joining two distinct purchase lists on the same receipt, scanning 207 million rows in less than a second, returning 130,883 users. “You just can’t do that on another platform,” Brendan says, “especially for a query of this complexity.”

With the audience identified, the user then asked FAST to draft an offer pitch. It produced a breakfast-basket promotion pairing orange juice with bagels. “The key is you can take those insights and turn them into action with FAST,” Brendan says. 

By democratizing access to the data, Fetch’s sales and commercialization teams can move faster. “It helps non-technical users iterate through their ideas really rapidly and creatively in a way that just wasn’t possible before,” Brendan says.

## Fast conversational BI agent responses with ClickHouse Cloud

As Brendan says, a conversational BI agent is only as useful as the speed behind it: “We couldn’t call it FAST if it wasn’t actually fast.” With ClickHouse, the median agent response time is 1.9 seconds. “This would easily be minutes in a traditional cloud data warehouse,” he adds.

The solution also has to be flexible. “You can’t have these queries be pre-aggregated,” Brendan says. “We had to have a real-time analytics platform that’s flexible enough to do these ad hoc queries, while being fast enough to actually have this interactive chat experience.”

For LLMs to write effective, performant queries, the database needs to be well-documented and easy to write and train. And it has to stay consistent under load. “The complex query that I’m running shouldn’t affect the complex query, and especially the easy queries somebody else is running,” Brendan says. “ClickHouse Cloud’s [compute isolation](https://clickhouse.com/blog/introducing-warehouses-compute-compute-separation-in-clickhouse-cloud) between queries was really big for us, and the simplified architecture made it really easy to manage and stand up.”

The other real-time analytics solutions Fetch looked at came up short in these areas. “The other platforms are optimized for these predictable workloads, where you know the scale and scope of the questions being asked,” Brendan says. “They all had issues for our use case, whether it was because they weren’t fast enough or they had reliability issues.”

Loading data into those other platforms was also difficult, with limited support for logical views and ingestion paths “clearly not designed for our batch loading workflow.” [ClickPipes](https://clickhouse.com/cloud/clickpipes), on the other hand, makes ingesting data straightforward. “ClickHouse Cloud with ClickPipes has been able to handle that really seamlessly,” Brendan says.

It also helped Fetch overcome scaling challenges. “The more compute you add, the more network hops and shuffles you’re dealing with across all those nodes, and that became a real bottleneck,” Brendan says of the other platforms. “Whereas with ClickHouse, we had very easy, consistent scaling. If we needed more performance, we just scaled up.”

Finally, the other platforms often required steps like cache warmup to reach good performance, but “those types of things we just didn’t have to do with ClickHouse,” Brendan says.

## FAST’s ClickHouse-based pipeline

Every night, the pipeline grabs a full copy of the data FAST needs from Snowflake, syncs it into S3, and uses ClickPipes to load it into a new versioned table. It then repoints a view at that table. “It’s just a DAG with some API calls to make the ClickPipe update the view,” Brendan says.

![Fetch Customer Story.jpg](https://clickhouse.com/uploads/Fetch_Customer_Story_3155f010e5.jpg)

*FAST’s nightly pipeline, from Snowflake through S3 into versioned ClickHouse tables.*

Brendan acknowledges that this isn’t a textbook approach. “In an ideal world, we’re doing incremental data loading, but to minimize joins and extract as much performance as possible, we have a really wide table structure with all of our dimensional data in each row.” Since that structure doesn’t play well with lightweight updates, the nightly refresh wins on simplicity.

“Most importantly for us,” Brendan adds, “it’s very easy for LLMs.” The model never has to track which version of a table is current or rewrite its query targets on the fly. It points at the receipts view and runs, and the view always resolves to the latest data. The same setup makes incident response easier as well, since rolling back to an earlier version of the data is just a matter of repointing the view.

## Answers in minutes instead of days

Today, FAST handles more than 500 queries a day from roughly 100 users, with median latency around 1.9 seconds. Brendan says it’s cost-effective compared to platforms that offer similar or worse performance. “The most important thing for us,” he adds, is the time to analytics: questions that once took days because it needed to wait for a ticket to be picked up now get answered in minutes.

One member of Fetch’s channel partnerships team, Sara, offers a real-world example.

> “I was in a live meeting where the team wanted to understand the potential scale of a campaign. Instead of following up later, I used FAST to pull audience sizing in real time. What started as an exploratory conversation turned into a committed plan because we had the data instantly.”
>
> — Sara S., Channel Partnerships, Fetch

That benefit extends to Fetch’s analytics team as well. Before, Sara’s question would have become a ticket, and answering it would have pulled an analyst away from other priorities. With FAST, sales and commercialization teams can follow their own ideas, while the analytics team spends their time on the foundational challenges that affect the whole company.


---

## Get started today

Interested in seeing how ClickHouse works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-1413-get-started-today-sign-up&utm_blogctaid=1413)

---