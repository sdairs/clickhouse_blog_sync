---
title: "How Sierra uses ClickHouse to bridge observability and analytics"
date: "2025-08-28T08:35:09.544Z"
author: "ClickHouse Team"
category: "User stories"
excerpt: "“We don’t fear cardinality anymore. We don’t have the technical constraints we had earlier. ClickHouse lets us run really, really fast queries at scale.” Arup Malakar, Software Engineer, Sierra"
---

# How Sierra uses ClickHouse to bridge observability and analytics

<style>
div.w-full + p, pre + p {
  text-align: center;
  font-style: italic;
}
</style>

For years, [observability](https://clickhouse.com/resources/engineering/what-is-observability) and analytics have inhabited two separate islands, each with its own tools, teams, and priorities. On observability island, residents monitor system health, configure alerts, and respond to incidents in real time. Across the water, the analytics tribe builds dashboards, runs A/B tests, and tries to forecast business performance.

But for Arup Malakar, a software engineer at [Sierra](https://sierra.ai/), that divide no longer makes sense. Why keep building remote settlements when a single bridge could connect engineers and analysts in one shared system, with one shared language and one shared view of reality?

“At the end of the day, it’s all data,” Arup says. “And we just need a way to access it.”

At [ClickHouse’s 2025 Open House user conference](https://clickhouse.com/openhouse#video-Sierraai), Arup shared how Sierra—a platform for building better customer experiences with AI—is using ClickHouse to power both real-time observability and high-level analytics from a single source of truth.

## A foundation for AI-first customer experiences

Sierra believes we’re on the cusp of a major shift—one where agents become the primary interface between brands and their users.

“If you look at how different technology has emerged over time, it has always led to new experiences,” Arup says. He compares it to the rise of websites in the 1990s and 2000s, or the mobile app boom in the 2010s. “In this new world, we believe that every business will have an agent users can interact with. It’s where the business will establish their brand and make customer interactions quicker, easier, and more efficient.”

That vision is already taking shape inside some of the world’s biggest brands. CLEAR relies on Sierra agents to help travelers manage memberships and answer questions. ADT uses them to troubleshoot alarms and resolve billing issues. Sonos deploys AI agents to reduce a key onboarding metric they call “time to music.”

[Sierra’s Agent OS](https://sierra.ai/product/build-your-ai-agent) is the only platform that supports both no code and programmatic agent development. At its foundation is the Agent SDK, Sierra’s platform as a service for building agents with code. It enables any developer to define their own customer journeys, the workflows which describe what the agent should do, and how. Sierra's Agent SDK also fits seamlessly within existing software development life cycles, with version control, release gating, continuous integration, delivery and deployment, audit, and more.

Agent Studio is Sierra’s no code tool. It enables any team to define customer journeys in plain English based on the existing procedures used by the customer experience and operations teams. Powered by ClickHouse, it’s how teams measure agent performance, run experiments, and connect what’s happening in the product to what’s happening in customer conversations.

“Agents are very interesting because every interaction captures where users are having trouble,” Arup explains. “That can often shape how a company thinks about its roadmap. You know exactly where the friction is and what people want from the product. And we use ClickHouse for that.”

## Where observability and analytics drifted apart

In the world Sierra is building, every user interaction is rich with signals, whether they’re technical, behavioral, or business-related. But traditionally, the tools used for capturing and acting on those signals have been split across two very different stacks.

On one side is observability, optimized for speed and system health. SREs and DevOps teams monitor latency, errors, and alerts. Infrastructure engineers manage deployments and plan for capacity. Security and compliance teams handle audits and scan for anomalies.

On the other side is analytics, focused on longer-term trends and user behavior. Product managers look at feature adoption and experiment results. Data analysts run segmentation and attribution reports. Executives track top-line KPIs and forecast business performance.

These workflows are deeply interdependent, but they’ve rarely shared the same underlying systems. As Arup explains, “split stacks were a workaround, not a requirement”—a response to the technical limitations that existed before solutions like ClickHouse.

Observability stacks need millisecond query times and near-zero ingestion lag. “We want queries to be fast, because we want to evaluate every minute if errors are above threshold,” he says. “And we want to know if the error happened within the last minute, not if it happened 10 minutes ago.” That often means limiting dimensionality, dropping high-cardinality fields, and optimizing for fast alerts rather than deep exploration.

Analytics systems, by contrast, usually prioritize flexibility over speed, supporting complex joins, richer context, and long-term storage. At most companies, the result is two different pipelines, two sets of dashboards, and two different ways of understanding what’s happening.

## Building the bridge with ClickHouse

For Sierra, separating observability and analytics didn’t make sense. Because they use outcome-based pricing, an HTTP error on a customer return API doesn’t just affect uptime; it impacts whether a user gets their issue resolved and whether the company gets paid. 

“If the system is down and the transaction fails, we escalate to a human and don’t charge for that transaction,” Arup explains. “That’s a system metric directly tied to a business outcome.”

Rather than treat observability and analytics as different islands with competing priorities, Sierra began thinking of them as one unified data challenge—two views on the same event stream. 

ClickHouse made that shift possible. Arup points to features like [columnar storage](https://clickhouse.com/docs/faq/general/columnar-database), [vectorized query execution](https://clickhouse.com/docs/development/architecture), and [materialized views](https://clickhouse.com/docs/materialized-views), saying: “All of those techniques let us run really, really fast queries at scale.” He also highlights ClickHouse’s “amazing real-time ingestion,” with live dashboards and alerts made easier by integrations with [Kafka](https://clickhouse.com/docs/integrations/kafka), [Kinesis](https://clickhouse.com/docs/integrations/clickpipes/kinesis), and [S3](https://clickhouse.com/docs/integrations/s3).

The database has been especially valuable when dealing with high-cardinality data. Whereas traditional observability systems often drop fields to preserve performance, ClickHouse lets Sierra retain the full context without sacrificing speed, and query it all using standard SQL.

“We don’t fear cardinality anymore,” Arup says. “We still have to shape the data for query performance, but with tricks like materialized views and pre-aggregation, we don’t worry about it. We can basically have all the data in one place and use it to answer all our questions.”

<div class="my-6"><div class="rounded-lg bg-white/10 p-4"><h3 class="text-inherit undefined Typography_suiTitleh3__JlLe2  group/mdHeader toc-ignore" id="test">Get started with ClickStack</h3><p>Spin up the world’s fastest and most scalable open source observability stack, in seconds.</p><a class=" w-full" target="_self" href="https://clickhouse.com/docs/use-cases/observability/clickstack/getting-started?loc=blog-o11y-global-cta&amp;utm_source=clickhouse&amp;utm_medium=web&amp;utm_campaign=blog"><button class="styles_button__3smpn mt-6 w-full font-medium" data-type="primary"><span class="flex items-center whitespace-nowrap">Try now</span></button></a></div></div>

## Turning queries into real-time alerts

Along with dashboards and analysis, ClickHouse also powers Sierra’s real-time alerts. Every user interaction, whether over voice or chat, generates a structured event that gets written into ClickHouse. These events flow into a central table, where materialized views handle minute-by-minute aggregation of key metrics.

![Google Keep Note (9).png](https://clickhouse.com/uploads/Google_Keep_Note_9_064dfe9fd2.png)

<p>A materialized view tracking customer API errors, updated in near-real time.</p>

To expose these metrics, Sierra uses ClickHouse’s web query API, which supports Prometheus wire format. “We can point Prometheus at the ClickHouse endpoint,” Arup says, “and it will scrape the metrics every minute or so.” Prometheus handles the alert evaluation, scheduling, and delivery, allowing Sierra to notify its customers when something’s off.

As Arup explains, the current setup is still evolving. Alerts are configured manually for now, but the goal is to make them fully self-service. “We want customers who are looking at our analytics dashboard to be able to click and configure an alert on the business metrics they care about,” he says. “Observability and analysis as two sides of the same coin.”

## One island, one language

Sierra is changing how companies speak to their customers, replacing static support flows with AI agents that learn, adapt, and improve over time. Behind that shift is another transformation: a rethinking of how teams use data across technical and business domains.

For Arup and the team, the long-term vision goes beyond infrastructure. It’s about collapsing old silos—technically, by unifying systems within ClickHouse, and culturally, by giving teams a shared language and understanding of what matters.

“Everything is just an event,” he says. From system errors and outages to user behavior and product insights, it all flows through the same stream. With ClickHouse as the engine, Sierra can store that data, analyze it in SQL, and use it to connect performance at every level.

At Sierra, the results are already visible. “Product managers talk in system metrics now,” Arup says. “Platform engineers think about how infrastructure changes affect business performance. The key is in the data living together. ClickHouse is amazing for that.”

Arup imagines a future where that divide disappears entirely. “It would be really cool if we no longer thought of observability and analytics as two different islands, but just one data problem, powered by a really good compute engine like ClickHouse.”

To learn more about ClickHouse and see how it can bring speed and scalability to your team’s data operations, [try ClickHouse Cloud free for 30 days](https://clickhouse.com/cloud).
