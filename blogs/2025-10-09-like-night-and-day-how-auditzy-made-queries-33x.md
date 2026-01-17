---
title: "“Like night and day”: How Auditzy made queries 33x faster by switching from Postgres to ClickHouse"
date: "2025-10-09T10:32:49.551Z"
author: "Mayank Joshi, Co-Founder and CTO, Auditzy"
category: "User stories"
excerpt: "When Mumbai-based startup Auditzy hit Postgres performance limits, they switched to ClickHouse—and saw queries run 33× faster with 10× better compression."
---

# “Like night and day”: How Auditzy made queries 33x faster by switching from Postgres to ClickHouse

Every click, scroll, and page load tells a story about how users experience a website. Founded in Mumbai, India, in 2022, [Auditzy](https://auditzy.com/)’s mission is to capture those signals and turn them into insights that different teams across a business can actually use.

“We connect the dots between website speed and business outcomes,” says co-founder and CTO Mayank Joshi. “In a nutshell, Auditzy helps brands monitor and optimize performance, while also helping them understand the impact of that performance on their business.”

Auditzy tracks a wide range of signals. Performance metrics such as load time, visual stability, and interactivity show how quickly and smoothly a site responds. Visitor persona data adds context with details like browser, network, operating system, and geolocation. Event tracking maps the user journey with things like add-to-cart, payment, scroll depth, and timing. 

The value of these insights depends on who’s looking at them. “Tech teams use them to understand performance-related bottlenecks, like a slow-loading image or visually unstable layout,” Mayank explains. “Business leaders use them to get a clear view of the impact website speed is having on their business. Marketing and SEO teams use them to compare their website with competitors and know exactly where they stand.”

Delivering and supporting that vision at scale requires a modern data architecture built for speed, resilience, and growth. At a [July 2025 ClickHouse meetup in Mumbai](https://clickhouse.com/videos/mumbai-meetup-auditzy-12jul25), Mayank described the challenges Auditzy faced with Postgres, why they decided to migrate to ClickHouse, and what life looks like now with an ultra-fast, scalable architecture.

<iframe width="768" height="432" src="https://www.youtube.com/embed/7jG8C8lXkpM?si=YW4ONU24ueBx3z38" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

<br/>

## The pains of Postgres

Auditzy’s original architecture was simple enough. Data flowed from websites via a lightweight script into a Golang backend, which transformed the events and pushed them through AWS Kinesis into a Postgres cluster on Azure. 

“This setup worked decently when we had lower data volumes,” Mayank says. “But as we started to grow and scale, the cracks began to show.”

Auditzy’s old Postgres-based architecture: sluggish, fragile, and overworked:
![495743692-3d1f8dca-1c10-4a53-9eac-959666f29300.png](https://clickhouse.com/uploads/495743692_3d1f8dca_1c10_4a53_9eac_959666f29300_56f7ae6437.png)

One of the biggest issues was query latency, especially with large datasets. “Any time we ran a query on a 100- or 200-million row dataset, it would take not just seconds, but minutes,” he says. “For a product that’s pitching real-time insights, this was not ideal.”

Ingestion wasn’t any better. Bulk inserts slowed to a crawl during traffic surges, and every attempted fix—caching mechanisms, partitioning, materialized views, even custom aggregation systems—only added complexity. “All those workarounds created technical debt and meant we had to write a lot of code in order to maintain performance,” Mayank says.

On top of that came the daily grind of maintenance. Postgres needed regular babysitting to manage index bloat and vacuum operations. As a result, new feature development dragged, bogged down by long test cycles and endless performance tuning.

“With all these growing challenges, our efforts were kept more on the maintenance side, rather than building the product itself,” Mayank says. He knew they needed a better database—one purpose-built for speed, scale, and real-time analytics.


## Enter ClickHouse, the perfect fit

Auditzy’s journey to ClickHouse began in 2023, when Mayank came across a [blog post by Zerodha](https://zerodha.tech/blog/logging-at-zerodha/). The trading platform had migrated its logging infrastructure from an ELK-based stack to ClickHouse and reported massive gains in speed and efficiency. “That really piqued my interest,” he recalls. When Auditzy started running into its own scaling problems, he decided to see if ClickHouse might be the answer.

His first step was a proof of concept. He imported 300 million rows of data into ClickHouse and ran the same queries the team had been struggling with in Postgres. “The difference in terms of query times was like night and day,” he says. “Who doesn’t love blazing-fast speed?”

ClickHouse also proved cost-efficient—“not just in terms of compute, but also when it comes to storage, thanks to its compression capabilities.” He highlights [advanced codecs](https://clickhouse.com/docs/data-compression/compression-in-clickhouse) such as DoubleDelta for date-time fields or LZ4 and ZSTD for other data types.

Thanks to ClickHouse’s [SQL compatibility](https://clickhouse.com/docs/sql-reference), migrating from Postgres was smoother than expected. “We didn’t have to rewrite queries from scratch,” Mayank says. “We just made a few tweaks here and there, and everything worked seamlessly.” The database’s open-source model, strong community backing, and flexible hosting options added further confidence, as did the minimal maintenance required. “It just runs like clockwork,” he adds.

In the end, Auditzy’s ClickHouse experience mirrored everything Mayank had read from other users. It’s battle-tested, built for real-time analytics use cases, and “already used by brands handling trillions of rows and petabytes of data at scale,” he says. “Auditzy and ClickHouse make perfect sense together.”


## New architecture, massive results

Today, Auditzy’s architecture looks much the same on the surface. Data still flows from client devices into a Golang backend, passing through AWS Kinesis and landing in a database. But the switch from Postgres to ClickHouse, Mayank says, has “made a huge impact.”

Auditzy’s new ClickHouse-based architecture: fast, scalable, and reliable:
![495743694-a7fa2698-896f-4e35-8d5a-bd518436e0f2.png](https://clickhouse.com/uploads/495743694_a7fa2698_896f_4e35_8d5a_bd518436e0f2_4ed2057f75.png)

The biggest and most obvious win is query speed. Median queries that once took around 10 seconds in Postgres now return in just 300 milliseconds—a 33x boost. Even the most complex queries, which previously dragged on for a full minute, now complete in about 15 seconds. “And we’re continuously working to bring it down further,” Mayank says.

Storage efficiency has been just as impressive. A dataset of 2 billion rows that consumed 2.5 TB in Postgres shrank to 250 GB in ClickHouse, a 10x compression rate. “This has drastically reduced our storage cost,” he says.

With ClickHouse, technical debt has all but disappeared. “All the workarounds we used to do before—we’ve removed all of that,” Mayank says. Freed from maintenance, the team can move much faster. “Earlier, we used to release a couple of features in a month. Now, we can directly query raw data and create new dashboards or analytics on the fly.”


## A “game-changer” for the future

Mayank and the team didn’t stop at a successful migration. “Once we got the boost and the base we needed, thanks to ClickHouse, we started asking ourselves: how can we make this performance data more understandable and easier for our customers to use?” he says.

The answer is Auditzy Copilot, a conversational assistant designed to bring real-time analytics to everyone in an organization. Instead of navigating fixed dashboards or relying on pre-built reports, users can ask questions in plain language—why a product detail page is slower than usual, how checkout performs in a specific browser, which visitor personas are converting best—and get instant answers.

Behind the scenes, ClickHouse provides the speed, while LLMs supply the intelligence. The [ClickHouse MCP server](https://clickhouse.com/blog/integrating-clickhouse-mcp) acts as the bridge between the two, translating natural-language prompts into database queries and returning results in real time. The vision is to make analytics more dynamic, accessible, and collaborative. Developers can still dig into the details, but marketers, product managers, and business leaders will be able to generate insights on their own, without waiting on analysts or engineers.

For Mayank and the Auditzy team, the move to ClickHouse was never just about solving today’s bottlenecks. It was about building a foundation for the future. 

“ClickHouse has been a game-changer for us,” he says. “Not just in terms of user experience for our dashboard, but also in terms of developer experience. It’s allowed us to think in real time, putting our focus back on product-building rather than babysitting infrastructure.”

Ready to transform your team’s data operations? [Try ClickHouse Cloud free for 30 days](https://clickhouse.com/cloud).



