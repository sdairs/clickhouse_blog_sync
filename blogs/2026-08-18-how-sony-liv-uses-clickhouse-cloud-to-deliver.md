---
title: "How Sony LIV uses ClickHouse Cloud to deliver live streaming analytics at billion-row scale"
date: "2026-08-18T16:20:22.442Z"
author: "ClickHouse"
category: "User stories"
excerpt: "Sony LIV consolidated fragmented batch, Elasticsearch, and BigQuery workloads on ClickHouse Cloud, delivering sub-second analytics across billions of daily streaming events."
---

# How Sony LIV uses ClickHouse Cloud to deliver live streaming analytics at billion-row scale

## Summary

- Sony LIV uses ClickHouse to power real-time QoS and QoE analytics across its OTT streaming platform, ingesting billions of telemetry events per day.
- Their team consolidated a fragmented stack of batch pipelines, Elasticsearch, and BigQuery into a single, scalable, cloud-native data platform on ClickHouse Cloud.
- Queries that previously took tens of seconds to minutes now complete in less than a second, dramatically improving operational responsiveness during live events.


![2026-08-11_2f9421ec_01_sony-liv-customer-story-blog-cover-yellow.jpg](https://clickhouse.com/uploads/2026_08_11_2f9421ec_01_sony_liv_customer_story_blog_cover_yellow_004abd96ab.jpg)

When a marquee cricket match reaches its final over, or a UEFA Champions League knockout match goes to penalties, millions of people reach for their phones. Traffic spikes without warning. For a streaming platform like [Sony LIV](https://www.sonyliv.com/), that moment is the ultimate test.

Launched in 2013, Sony LIV has grown into one of India’s leading OTT platforms, serving live sports, entertainment, originals, movies, and TV content across millions of users and devices. It operates at enormous scale, particularly during live sporting events, where concurrency and telemetry volumes can rise sharply within very short time windows.

Beyond video delivery, Sony LIV’s data and platform engineering team is responsible for providing the infrastructure to understand what’s happening across the platform, from how individual users are experiencing the stream, to how the service is holding up, to how ads are performing. As VP of Platform Engineering Vaibhav Gupta puts it, “Real-time operational visibility and user analytics are business critical.”

We caught up with Vaibhav to learn how Sony LIV rebuilt their analytics infrastructure around [ClickHouse Cloud](https://console.clickhouse.cloud/). “The overall goal,” he says, “is to build a cloud-native, real-time, highly scalable data platform capable of supporting both business intelligence and operational decision-making during massive live events.”

## A stack built for batch, not live events

Before ClickHouse, Sony LIV’s analytics ecosystem relied on a mix of traditional data warehouse systems, batch pipelines, Elasticsearch-based observability workflows, BigQuery-based analytics workloads, and multiple fragmented telemetry stores. “While these systems worked for specific use cases,” Vaibhav says, “we faced several limitations as our scale increased.”

The first was speed. As Vaibhav explains, most pipelines were optimized for batch analytics rather than ultra-low latency streaming analytics. “During live sports events, operational teams need visibility within seconds, not minutes,” he says.

Cost was also a growing concern. As telemetry volumes climbed into the billions of events per day, storage and query costs “increased significantly,” Vaibhav says, particularly for high-cardinality observability workloads and long-retention analytics.

Fragmentation made both problems harder to solve. Playback telemetry, CDN metrics, application events, clickstream data, and ad-tech events all lived in different systems. Piecing together a coherent picture during a live event meant stitching data from multiple sources, slowly, and often after the moment had passed.

Meanwhile, the team faced major query performance bottlenecks. Ad-hoc analytical queries over large telemetry datasets, Vaibhav says, became “increasingly slow and expensive,” especially during peak traffic periods.

And then there was live sports traffic itself, which, as Vaibhav explains, doesn’t behave like normal traffic. “Traffic patterns can spike several multiples within minutes after a wicket, goal, or major match event. Existing systems struggled to scale efficiently for these patterns.”

## Finding a system that could do it all

The team knew they needed a better solution. They evaluated a handful of analytics and observability platforms, focusing on both operational telemetry and product analytics workloads.

Among their key requirements, Sony LIV needed sub-second query response times on very large datasets, high ingestion throughput during live events, cost-efficient storage at billions of events per day, and near real-time processing and querying for operational dashboards. They also wanted a single data platform capable of supporting a variety of use cases, and the architecture had to scale horizontally during unpredictable traffic spikes.

Vaibhav knew it was a lot to ask of any one platform. “Most systems were strong in one or two dimensions,” he says, “but struggled when all requirements were combined.”

The team learned of [ClickHouse Cloud](https://console.clickhouse.cloud/) through industry engineering discussions, high-scale observability use cases, open-source analytics communities, and streaming and telemetry engineering benchmarks. “ClickHouse stood out because of its architecture and performance characteristics for large-scale analytical workloads,” Vaibhav recalls.

That query performance, Vaibhav says, was the first thing that set it apart. “ClickHouse demonstrated exceptional performance for large-scale aggregations and time-series analytics,” he says. The team was also attracted by ClickHouse’s [high compression ratios](https://clickhouse.com/docs/data-compression/compression-in-clickhouse) and [columnar storage model](https://clickhouse.com/resources/engineering/what-is-columnar-database), which promised to significantly improve storage economics.

On real-time analytics, Vaibhav says, “It aligned very well with our need for operational dashboards and live telemetry analytics.” Meanwhile, the database’s [distributed architecture](https://clickhouse.com/docs/academic_overview) matched Sony LIV’s scaling requirements for live sports traffic, and its open ecosystem and [integration flexibility](https://clickhouse.com/docs/integrations) were strong advantages for their engineering teams.

Perhaps most importantly, Vaibhav adds, “It allowed us to consolidate multiple analytics workloads into a more unified platform,” giving the team a shared data foundation and a single place to query across all of them.

## A unified, real-time analytics architecture

The move to ClickHouse completely transformed Sony LIV’s architecture. Where the old system was an operationally complex patchwork of telemetry systems, batch-heavy pipelines, storage systems, and different query engines for different teams, the new stack, Vaibhav says, “is significantly more real-time and centralized.”

In Sony LIV’s ClickHouse-based architecture, client SDKs, streaming services, CDN infrastructure, and ad systems all feed into an event streaming pipeline built on Amazon Kinesis. From there, a real-time processing layer via ClickPipes writes into a ClickHouse analytics cluster, which serves as the single source of truth for operational dashboards, product analytics, QoE systems, and SRE workflows across the organization.

![sony-liv_aug2026_image1.jpg](https://clickhouse.com/uploads/sony_liv_aug2026_image1_50084638e6.jpg)

Today, ClickHouse powers a wide range of analytics use cases. On the streaming side, the team runs playback QoE analytics, startup latency analysis, buffering analysis, and device-level telemetry. CDN performance analytics give the operations team visibility into how content is being delivered across regions. Real-time operational dashboards surface issues as they happen. Clickstream and user engagement analytics inform product decisions. Ad event analytics support the ad-tech team. And when something goes wrong, SRE teams use ClickHouse for incident troubleshooting.
a
“We’re also integrating ClickHouse deeper into observability and predictive operational workflows,” Vaibhav adds, with even more use cases already in the pipeline.

## Faster answers, better visibility, lower costs

Since moving to ClickHouse, Sony LIV has seen huge improvements in analytical query latency, especially on high-volume telemetry datasets. Queries that took tens of seconds to minutes in the old system now complete in sub-second to low-single-digit seconds. “This dramatically improved operational responsiveness during live events,” Vaibhav says.

With better query performance comes vastly improved real-time visibility. Operational teams now have real-time insight into playback failures, buffering spikes, regional degradation, device-specific issues, and CDN anomalies. “This directly improved incident response workflows,” Vaibhav says.

Another major benefit is cost optimization. ClickHouse’s compression efficiency, columnar storage model, and optimized compute usage, Vaibhav says, have “significantly improved overall analytics infrastructure efficiency… especially for high-retention telemetry workloads, the storage economics improved materially compared to earlier systems.”

Operational efficiency has improved too. Teams across SRE, product, streaming engineering, analytics, and ad-tech now work from more unified datasets and dashboards. “This reduced operational fragmentation and improved collaboration,” Vaibhav says. For engineering teams specifically, he adds, “it improved productivity because teams spend less time waiting for analytics and more time acting on insights.”

Finally, the platform now handles live sports traffic the way it was always meant to. Large traffic spikes during major tournaments and high-concurrency streaming events, which had previously strained the stack, are now handled with ease. As Vaibhav says, “Faster visibility translates directly into better viewer experience and improved platform reliability.”

## What’s next for Sony LIV and ClickHouse

Rebuilding around ClickHouse has already transformed Sony LIV’s analytics infrastructure. The future roadmap is even more ambitious, with ClickHouse continuing to play a key role in the team’s push toward a fully intelligent, real-time data platform.

Today, that roadmap includes building out a broader in-house clickstream and behavioral analytics platform, with ClickHouse as the foundation for a unified view of user behavior across the service. The team is also working on predictive autoscaling models, using historical traffic patterns and live telemetry data to anticipate demand during major sporting events before it arrives, rather than reacting after the spike hits.

Other items on the roadmap include deepening QoE analytics with richer real-time streaming intelligence and playback quality monitoring; modernizing and expanding operational observability use cases across infrastructure, applications, CDN, and video pipelines; improving real-time ad delivery visibility and monetization analytics; and using large-scale telemetry datasets for anomaly detection and operational intelligence.

“ClickHouse has become a foundational layer in our real-time analytics and observability modernization journey,” Vaibhav says. “Our long-term vision is to build a highly intelligent, real-time, cloud-native analytics platform capable of supporting the next generation of large-scale OTT streaming operations.”


---

## Get started today

Interested in seeing how ClickHouse works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-1567-get-started-today-sign-up&utm_blogctaid=1567)

---