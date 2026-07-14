---
title: "How Insider One uses ClickHouse Cloud to power real-time customer engagement at scale"
date: "2026-07-13T11:03:24.464Z"
author: "ClickHouse"
category: "User stories"
excerpt: "Insider One cut query latency by up to 75% and eliminated operational overhead by moving its Unified Customer Database from self-managed ClickHouse to ClickHouse Cloud."
---

# How Insider One uses ClickHouse Cloud to power real-time customer engagement at scale

## Summary

- Insider One uses ClickHouse Cloud to power real-time segmentation, personalization, and analytics across its customer engagement platform.
- Migrating from self-managed ClickHouse to ClickHouse Cloud reduced query latency by 70-75% for large customers while eliminating operational overhead.
- Predictable performance at scale lets Insider One ship features more confidently and support an AI-native roadmap built on real-time data.


[Insider One](https://insiderone.com/), AI-native customer engagement platform that helps marketers act on customer data in real time, all in one place. Instead of making teams stitch together separate systems for data, orchestration, and execution, Insider One believes the future belongs to unified platforms where insight and action are built on the same foundation.

“Solving all of our customers’ problems in a single platform is really important to us,” says Yigit Karadeniz, a senior product manager focused on the data layer behind Insider One’s platform—what the team internally calls its Unified Customer Database (UCD).

UCD has driven Insider One’s evolution from a set of channel-focused products into an all-in-one platform trusted by global brands like Adidas, L’Oréal, and MediaMarkt. But delivering that kind of experience at scale comes with strict technical requirements. Every segmentation query, audience count, and personalization decision has to return fast enough to keep the product usable, even as data volumes grow and workflows get more complex.

We caught up with Yigit to talk about how UCD underpins Insider One’s product offerings, why the team moved from a self-managed ClickHouse deployment to [ClickHouse Cloud](https://clickhouse.com/cloud), and how a faster, more flexible data foundation is helping them prepare for an AI-powered future—what Yigit calls “the age of imagination” for marketers.

## The spark behind a unified foundation

UCD didn’t begin as some grand platform initiative. As Yigit explains, it started with a simple realization inside the product team: “We have all this customer data—why aren’t we unifying it?”

At the time, Insider One’s products were organized by channel. Web personalization had its own data store. Mobile app engagement had another. Each worked independently, but as customers adopted more of the platform, the limitations became clear. The same user existed in multiple places, and understanding behavior across channels required extra work.

Unifying that data began as a side project, initially owned by a single developer. “We found out the job was much bigger and had huge potential,” Yigit says. Bringing web and app data together meant creating a foundation that every part of the product could depend on.

Early on, the team evaluated several databases, including Amazon Redshift and Snowflake. Both were solid options for traditional analytics workloads, but UCD wasn’t being built for offline reporting. It needed to support high-volume event ingestion and low-latency queries that powered live segmentation and personalization inside the product.

That pointed them to ClickHouse. And over time, they became increasingly fluent in how to get the most out of it. “We’ve been using ClickHouse since the day we established UCD,” Yigit says. “We’ve never thought about changing it, because even if something’s lacking, we can always find the solution with ClickHouse. You could say we’re kind of addicted.”

As the side project grew, Insider One formalized UCD as a dedicated system responsible for event data, user attributes, identity resolution, and profile unification across channels. What started as a side project became the foundation the rest of the platform is built on.

## From self-managed to ClickHouse Cloud

For years, Insider One ran ClickHouse in a self-managed setup on AWS. That setup served the platform well and scaled reliably alongside UCD as adoption increased, and moving to ClickHouse Cloud was the next deliberate step in that journey.

But success introduced a new kind of pressure. “We were getting bigger and bigger clients,” Yigit says. “That growth raised the bar on what our infrastructure had to deliver.” Larger customers meant larger datasets, more concurrent queries, and tighter expectations around performance and reliability.

Increasingly, meeting those expectations meant managing infrastructure, tuning clusters, and balancing performance against cost. That extra operational effort was necessary to protect the customer experience, but as Yigit explains, it came with tradeoffs. “Every hour spent tuning clusters was an hour not spent on the product roadmap,” he says.

Eventually, the team began looking at [ClickHouse Cloud](https://clickhouse.com/cloud). The managed service promised to remove the operational burden of running clusters internally, so the team could focus more fully on building product capabilities. In many ways, it was a continuation of the same philosophy that led them to build UCD in the first place: keep the foundation fast and reliable, and free the product team to focus on what sets Insider One apart.

## Validating the move to a managed service

Before committing fully, the team wanted proof that moving to ClickHouse Cloud would preserve the performance characteristics UCD depended on, while removing the operational burden of self-management. Evren Baykan, Director of Data Platforms at Insider One, led the validation work.

They started with a POC based on real workloads. They migrated one of Insider One’s largest customer datasets in an anonymized form and replayed the kinds of queries that matter most to the platform: segmentation queries triggered from the UI, audience counts that update as filters change, and analytical jobs supporting scheduled campaigns.

The results were obvious right away. Without significant changes on their end, average query latency dropped by 50-60%. And as Evren points out, the gains increased with scale: “As the data size got bigger, the latency drop became more significant.” For Insider One’s largest customers, improvements reached 70-75%. “This was the ‘aha’ moment for us,” he says.

Those gains also showed up where they mattered most. The team closely tracks latency percentiles (P50, P75, P90, and P99) because long-tail delays are what customers feel most when building segments or launching campaigns. ClickHouse Cloud consistently reduced those outliers, making performance not just faster, but more predictable.

## Fewer headaches, more product features

Dashboard metrics aside, Yigit says the most immediate impacts of migrating to ClickHouse Cloud have been operational relief and the product velocity that comes with it.

Before the move, performance issues surfaced through the channels you’d expect—internal reporting on query performance against SLA targets. These signals were manageable, but they pulled engineering time toward maintenance and away from building, with teams focused on tuning infrastructure to protect the user experience.

Since migrating to ClickHouse Cloud, those signals have all but disappeared. “We’re not getting any negative feedback,” Yigit says, “which is a good business metric for me.”

With the burden of managing clusters off their plate, the team can focus more of their energy on building on UCD rather than maintaining it. “ClickHouse Cloud has enabled us to build more confidently,” Yigit says, “and to deploy some of the features we were waiting to develop.”

## Building for the age of imagination

As Insider One looks to the future, the role of UCD continues to expand. Their roadmap increasingly centers on giving customers freedom to explore, transform, and activate their data, moving beyond fixed workflows toward more flexible, AI-driven experiences.

For Yigit, that shift represents a broader change in how marketers interact with technology. “To me, the age of AI means the age of imagination,” he says. The goal isn’t just faster queries or better dashboards, but a platform that lets customers experiment with their data in new ways and turn ideas into action without friction.

Beneath that vision, one requirement remains constant. The data foundation has to be fast, flexible, and reliable enough to keep up. “ClickHouse is essential for us to activate and optimize all of our current capabilities in a faster, more secure, and scalable way,” Yigit says.

ClickHouse Cloud gives Insider One the foundation it needs to keep evolving while staying unified at its core. As customer expectations rise and AI-driven use cases become even more central, that foundation gives Yigit and the team room to imagine what comes next, and the confidence to go build it.


---

## Get started today

Interested in seeing how ClickHouse works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-1282-get-started-today-sign-up&utm_blogctaid=1282)

---