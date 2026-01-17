---
title: "ClickHouse Open House Roadshow NYC videos are here"
date: "2025-10-21T12:11:40.894Z"
author: "Tanya Bragin"
category: "Community"
excerpt: "The ClickHouse Open House Roadshow kicked off in New York on October 7th with compelling customer stories from Modal, Ramp, and Capital One, and all session videos are now live."
---

# ClickHouse Open House Roadshow NYC videos are here

After the success of our [ClickHouse Open House](https://clickhouse.com/openhouse) conference in San Francisco in May, we knew we had to take this show on the road. 

On October 7th, the ClickHouse community came together in New York to hear from ClickHouse customers Capital One, Ramp, and Modal, alongside the ClickHouse product and leadership teams. 

For those who couldn't make it, and for attendees who want to revisit the sessions, we've now released the recordings from the event!

![ClickHouse Open House 2025](https://clickhouse.com/uploads/open_house_new_york_2025_36052dc03c.png)

We organized the presentations around four key use cases showcasing where ClickHouse shines. 

First is **real-time analytics**, or 'immersive data-driven applications,' that need both recent and historical data with instant interactive filtering. As one of our customers puts it, they're building apps where users expect responses right away, not in 5-10 seconds.

The second use case is **observability**, where SREs and DevOps teams increasingly adopt ClickHouse as observability data keeps getting more voluminous and structured over time. Companies like eBay moved from Elastic to ClickHouse early on, and we're seeing this trend accelerate as teams want more control over their data to build AI-enabled monitoring features.

The third is **data warehousing**, which includes leveraging ClickHouse as an interactive query layer on top of data lakes. The key word here is 'interactive.' Traditional query engines are optimized for batch workloads, but when you're applying AI to your data warehouse or data lake, you need that human-level responsiveness where you can ask a question, get a quick response, and iterate.

And finally, there's **AI and ML infrastructure** itself - ClickHouse is being used for data prep and transformation, as an offline and online feature store for model training and inference, for vector search, and of course for observability of AI systems. It's become essential infrastructure for data science teams.

## Capital One: Real-time analytics

Capital One, the banking and credit card company, uses ClickHouse to power its Slingshot data management and cost optimization platform. 

Salim Sayed and Syd Mehmood chose ClickHouse for its speed, scalability, and cost efficiency. They transformed dashboard load times from 5-6 seconds to under half a second, achieving **80% improvement in response times while cutting infrastructure costs by 50%.**

<iframe width="768" height="432" src="https://www.youtube.com/embed/8Avld0BlDlg?si=dkcRkjQX-kd5w8hL" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media;a gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

➡️ [How Capital One Slingshot cut infrastructure costs by 50%](https://clickhouse.com/videos/open-house-nyc-capital-one)

## Ramp: Observability

Ramp, a finance operations platform, faced challenges scaling analytics queries on Postgres. Four engineers were tasked with solving this problem, and within four weeks, they had put their new ClickHouse-based system into QA.

Ryan Delgado, who leads Ramp’s platform team, walks through the story and explains why turning those slow queries into reports that ran hundreds of times faster was so impactful that his entire OLAP team got promoted.

<iframe width="768" height="432" src="https://www.youtube.com/embed/mPZ7Bck_cMI?si=PfSIbO4sGNT4_nHU" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

➡️ [ClickHouse at Ramp: Just OLAP it](https://clickhouse.com/videos/open-house-nyc-ramp)

## Modal Labs: Data warehousing

Modal is an infrastructure platform for running large-scale GPU workloads in the cloud. They use ClickHouse as the backbone of their real-time observability platform.

In this talk, Ro Arepally explains how they solved a scaling bottleneck by switching to ClickHouse, transforming their logging infrastructure into a system that **handles half a trillion logs and delivers instant search results.**

<iframe width="768" height="432" src="https://www.youtube.com/embed/1LXK-mgdKCg?si=C3XlDag4pt5T5zF8" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

➡️ [How Modal delivers instant search on 500B+ logs](https://clickhouse.com/videos/open-house-nyc-modal)

## What's Next

Each of these stories deserves a deeper dive. Over the coming weeks, we’ll break down the technical architectures and lessons learned in individual posts [on our blog](https://clickhouse.com/blog?category=user-stories).

The [Open House Roadshow](https://clickhouse.com/openhouse) continues! We're bringing these conversations to more cities, connecting with data teams who are pushing the boundaries of what's possible with real-time analytics.

Check out the [full video playlist from NYC](https://clickhouse.com/videos?category=open-house), stay tuned for videos from Sydney and Bangalore, and join us at our final roadshow stop in Amsterdam on October 28th.

➡️ [Join us in Amsterdam](https://clickhouse.com/openhouse/amsterdam)
