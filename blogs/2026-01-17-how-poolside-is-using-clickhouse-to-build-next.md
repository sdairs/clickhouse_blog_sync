---
title: "How Poolside is using ClickHouse to build next-gen AI for software development"
date: "2025-03-02T21:05:48.316Z"
author: "The ClickHouse Team"
category: "User stories"
excerpt: "Read how Poolside is building next-generation AI for software engineering with ClickHouse Cloud at the core of their analytics workflows—querying billions of records in real time to analyze AI model performance and enable faster iteration."
---

# How Poolside is using ClickHouse to build next-gen AI for software development

![Poolside.png](https://clickhouse.com/uploads/Poolside_ba4fb435be.png)

Everything [poolside](https://poolside.ai/) does revolves around one goal: scaling intelligence. Co-founders Eiso Kant and Jason Warner are on a mission to redefine software development by [closing the gap between human and machine intelligence](https://poolside.ai/checkpoint/announcing-our-500-million-fundraise-to-make-progress-towards-agi), empowering developers to be more productive and creative, and unleashing a wave of innovation to tackle humanity’s greatest challenges.

"We’re focused on bringing AI to software developers on a daily basis in a way that drives increasingly more productivity and enjoyment in the job," Eiso told ClickHouse recently. "To do that, we build foundation models from the ground up, with our own unique point of view, research, and approach that we think sets us apart from competitors."

But scaling innovation requires more than ambition: it demands infrastructure capable of handling billions of documents and running complex analytics at unprecedented speeds. As Eiso and the team scaled their training clusters to 10,000 GPUs and expanded their research to more than 800,000 real-world codebases, they realized their existing data pipelines couldn’t keep pace with the scale and speed they required.

Last year, they turned to [ClickHouse Cloud](https://clickhouse.com/cloud), a move that has allowed them to iterate faster, explore new approaches, and refine their AI models with greater precision. 

<blockquote>
<p> "ClickHouse gives us the speed to look at the data directly, letting us make faster decisions and iterate quickly, which is core to our mission."</p>
<p>Eiso Kant, poolslde</p>
</blockquote>

## Data growing pains

Six months ago, poolside’s data operations were a patchwork of ad-hoc pipelines managed by just two engineers. Today, Eiso says, they have "around a dozen people running data pipelines in different ways, shapes, and forms." This rapid growth has underlined the need for a more advanced database solution to manage their increasingly complex workflows.

At the heart of poolside’s work is an iterative approach to AI development. Their models analyze billions of documents and receive deterministic feedback, allowing them to improve reasoning and coding capabilities. But as the company scaled, poolside’s existing pipelines struggled to keep up with the demands of running large-scale queries across datasets. These delays slowed the team’s ability to experiment, make decisions, and refine their models.

>"How fast can we go from idea to dataset? That’s the metric that drives everything we do."

Adding to the complexity was the sheer scale of their operations. With massive compute clusters powering their AI training and research, they needed infrastructure that could handle large-scale data and help their team work faster and smarter. "How fast can we go from idea to dataset? That’s the metric that drives everything we do," Eiso says. Simply put, their existing setup couldn’t keep up with the speed or scalability their vision demanded.

## Choosing ClickHouse Cloud

> "If you only get to pick one thing, you’re glad you picked ClickHouse."

Eiso was no stranger to ClickHouse. He first encountered the database nearly a decade ago when it was open-sourced and had used it extensively at his previous companies, source{d} and Athenian. Having witnessed its speed and efficiency firsthand, he knew it could address Poolside’s growing data needs. "Even when you abuse it, you’re happy you did,” he says. “If you only get to pick one thing, you’re glad you picked ClickHouse."

While the familiarity helped, Eiso says the decision to choose ClickHouse was primarily about one thing: speed. "At the end of the day, the only thing we care about is speed," he says. Whether querying billions of records or analyzing the performance of AI models in real time, ClickHouse’s superior performance as a columnar OLAP database meant it could deliver results in seconds. For poolside’s iterative workflows, this translated into tangible advantages — running more experiments, exploring more ideas, and refining their models faster.

[ClickHouse Cloud](https://clickhouse.com/cloud) added another major benefit: simplicity. By choosing a managed service, the poolside team could avoid the burden of maintaining database infrastructure internally, freeing them to focus on scaling AI models and refining research, rather than troubleshooting performance issues or managing servers.

## Turning complexity into efficiency

The adoption of ClickHouse Cloud has transformed poolside’s data architecture, making it more streamlined, scalable, and efficient. Alongside standardized Spark pipelines to handle data processing, this shift allows the team to manage massive datasets consistently while maintaining the flexibility needed for fast experimentation.

[ClickPipes](https://clickhouse.com/cloud/clickpipes) has been a big part of this transformation. By simplifying the ingestion of datasets from queuing systems and object storage, it ensures each newly enriched dataset flows seamlessly into ClickHouse. This lets poolside analyze and validate data at every stage of their iterative AI workflows, with minimal management and no reliance on third-party infrastructure.

ClickHouse sits at the core of their analytics workflows, delivering results from billions of records in seconds. Its performance lets poolside’s engineers focus on analyzing data and refining models instead of troubleshooting bottlenecks. For tasks requiring different strengths, the team also incorporates other tools like Dremio, creating a flexible multi-engine system. This means engineers can choose the best query engine for each workload, whether it’s ClickHouse for lightning-fast analytics or Dremio for more specialized needs.

Today, ClickHouse is primarily used internally, with around 50 terabytes of compressed data stored in ClickHouse Cloud. This architecture supports billions of documents, delivering real-time insights that fuel poolside’s iterative workflows. With data bottlenecks eliminated, the team can experiment, innovate, and push the boundaries of AI at scale.

## Building the future of AI

As they chart the future of AI, poolside is setting their sights on even greater challenges. Their next steps include scaling their models further and pushing the limits of what their infrastructure can achieve. As they expand their research with larger datasets and new reinforcement learning techniques, ClickHouse Cloud will be a big enabler of their mission.

Eiso sees a future where anyone — not just seasoned developers — can use AI to build technology and solve complex problems. As the gap between human and machine intelligence continues to close, poolside’s tools promise to lower the barrier to entry, unlocking innovation for a wider audience as more people access the power of software development.

> "ClickHouse makes a lot of sense for what we’re trying to do. It lets us work faster, think bigger, and focus on what we care about most — scaling intelligence through AI."

As poolside grows, they’re not just building technology. They’re laying the foundation for a future where intelligence is scaled to tackle humanity’s shared challenges. With ClickHouse by their side, they’re redefining what’s possible in AI and software development.

*To see how ClickHouse can scale your company’s data operations, [try ClickHouse Cloud free for 30 days](https://console.clickhouse.cloud/signUp).*



