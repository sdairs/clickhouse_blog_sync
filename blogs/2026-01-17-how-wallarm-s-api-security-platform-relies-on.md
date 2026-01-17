---
title: "How Wallarm’s API security platform relies on ClickHouse Cloud to detect and block attacks"
date: "2025-04-29T19:49:19.887Z"
author: "ClickHouse Team"
category: "User stories"
excerpt: "“We need our platform to operate in real time. The moment we detect suspicious activity, we aim to block the API user before they can attack the site or exploit a vulnerability.”  - Slava Yudanov, VP of Engineering, Wallarm"
---

# How Wallarm’s API security platform relies on ClickHouse Cloud to detect and block attacks

<p>
As the nerve center of today’s digital ecosystems, APIs power everything from mobile apps to large-scale enterprise operations. But while they make it easier to share data and build new services, they also create openings for attackers, putting businesses at risk. And with AI adoption accelerating, the stakes are only getting higher.
</p>
<p>
Founded in 2016, <a href="https://www.wallarm.com/">Wallarm</a>’s mission is simple yet critical: to help enterprises prevent and protect against breaches across all of their APIs. With solutions for discovery, protection, response, and testing, Wallarm’s advanced API security platform is trusted by security teams at companies like Panasonic, Miro, Dropbox, and others. Through features like API Sessions, Wallarm gives enterprises deep visibility into their API traffic, helping them identify vulnerabilities and block attacks.
</p>
<p>
As demand for API security continued to grow, Wallarm faced challenges in scaling their infrastructure to deliver real-time threat detection. Their journey to <a href="https://clickhouse.com/cloud">ClickHouse Cloud</a> wasn’t just about solving a technical bottleneck; it was about driving growth, strengthening their platform, and doing even more to protect customers.
</p>
<p>

![Wallarm1.png](https://clickhouse.com/uploads/Wallarm1_c9d9697558.png)

</p>
<p style="text-align: center">
<em>Detailed information for an API request containing a SQL injection attack for a session. </em>
</p>
<h2>Early data hurdles</h2>


<p>
The first version of Wallarm’s API Sessions relied on Cassandra, using an eventual consistency model to process events. This setup was fine for batch processing, but it wasn’t fast enough for real-time security. By the time suspicious activity was detected, malicious actors could have already exploited vulnerabilities, leaving customers exposed.
</p>
<p>
“The companies that use our platform need to to detect and respond to threats in as close to real-time as possible,” says Slava Yudanov, Wallarm’s VP of Engineering.
</p>
<p>
The challenge only grew as Wallarm shifted from analyzing individual API requests to understanding behavior across entire sessions. “When you’re just looking at single requests, you don’t need to capture much data,” says Tim Erlin, Wallarm’s VP of Product. “But once you need to track sessions and understand behavior over time, that changes. You need a highly performant data store that lets you do that and still respond in real time.”
</p>
<p>
To address the latency issue, Wallarm moved to a self-hosted ClickHouse deployment. The new setup gave them the real-time analytics they needed, allowing API Sessions to aggregate and analyze requests on the fly. However, it also came with new hurdles.
</p>
<p>
Their self-hosted cluster was underutilized, running at only 30% capacity while racking up high operational costs. Without the in-house expertise required to manage a self-hosted setup, Slava’s team estimated that outsourcing support at the scale they needed would cost upwards of $30,000 per month. At that price tag, it was clear they needed a better solution.
</p>
<h2>Choosing ClickHouse Cloud</h2>


>"We need our platform to operate in real time. The moment we detect suspicious activity, we aim to block the API user before they can attack the site or exploit a vulnerability." - Slava Yudanov, VP of Engineering, Wallarm

<p>
When Wallarm’s leadership team began thinking about alternatives, <a href="https://clickhouse.com/cloud">ClickHouse Cloud</a> stood out as the natural next step. Their CEO, a long-time advocate of ClickHouse, was confident it could meet the demands of real-time API security. Even so, moving to a managed cloud service was a big shift for the team, especially given their background in self-hosted infrastructure and the security challenges of handling sensitive API data.
</p>
<p>
ClickHouse Cloud offered a scalable, cost-effective solution with pricing based on actual usage rather than fixed infrastructure costs. It also promised to offload the operational burden, freeing Wallarm’s engineers to focus on innovation rather than day-to-day maintenance.
</p>
<p>
Still, privacy remained a key consideration. “We’ve always prioritized a privacy-first architecture,” Tim says. “We don’t want to collect more data than necessary. We prefer to build conclusions, not data lakes.” For Wallarm, that meant finding a solution that could handle real-time analytics without forcing them to store every request and response.
</p>
<p>
Security concerns also loomed large. “It was a difficult choice,” Slava says. “As a security company, we prefer to keep as much data as possible inside our accounts. If we can avoid it, we don’t like to share data with cloud providers.” After working closely with the ClickHouse team, they determined that ClickHouse Cloud met their strict security and privacy needs, while offering a smooth transition from their existing setup.
</p>
<h2>The migration process</h2>


<p>
Migrating from a self-hosted ClickHouse deployment to ClickHouse Cloud required careful planning. Wallarm took a phased approach, onboarding clients one at a time to be sure the system performed reliably under production workloads, with minimal disruption to customers. This allowed them to validate each step of the migration and address any potential issues before scaling up.
</p>
<p>
One adjustment they made during migration involved optimizing their data pipeline to improve performance. The team adopted <a href="https://clickhouse.com/docs/en/optimize/asynchronous-inserts">async inserts</a>, a feature in ClickHouse that allows data to be written in batches rather than one row at a time. This sped up ingestion while reducing the load on the database, leading to smoother operations under high traffic volumes. “This helped us handle the scale of our data more efficiently in the new environment,” Slava says.
</p>
<p>
Another strategic decision was to reduce data retention. While their self-hosted setup stored 30 days of API request data, Wallarm chose to retain only seven days’ worth in the cloud. This helped them keep costs under control while still meeting operational needs, since most actionable insights come from recent data. 
</p>
<h2>Real results</h2>


<p>
Switching to ClickHouse Cloud has been a win for Wallarm’s team and customers. With their self-hosted setup, API session data could take up to 40 seconds to load — unacceptable for real-time security needs. Now, with ClickHouse Cloud, performance has improved dramatically, delivering near-instant results and letting customers respond to threats without delay.
</p>
<p>
For Slava and Wallarm’s engineering team, the move has been just as impactful. By offloading infrastructure management to ClickHouse Cloud, engineers can focus on building new features and improving the customer experience, rather than troubleshooting operational issues.
</p>
<p>
This operational efficiency has also translated into big-time cost savings. Staying with a self-hosted ClickHouse deployment would have required an annual investment of over $300,000. With ClickHouse Cloud, Wallarm expects to cut those costs to around $100,000 for comparable workloads — all while gaining the scalability to support future growth.
</p>
<h2>Securing the future</h2>


<p style="text-align: center">

![Wallarm2.png](https://clickhouse.com/uploads/Wallarm2_b3b6a4a5a0.png)

<em>Trend chart of API Abuse</em>
</p>
<p>
As AI adoption accelerates, it’s changing the threat landscape. According to Wallarm’s research, 98.9% of AI vulnerabilities are API-related. The reason is simple: AI systems and agentic AI rely heavily on APIs to function. Whether it’s pulling data, interacting with third-party services, or enabling AI agents to take action, those API calls create new opportunities for attackers.
</p>
<p>
Between 2023 and 2024, the number of AI-related CVEs jumped from 39 to 439 — a 1,025% increase. When Wallarm reviewed the U.S. Cybersecurity and Infrastructure Security Agency’s (CISA) catalog of known exploited vulnerabilities, they found that 50% were API-related in 2024, up from just 20% the year prior. In other words, as Tim says, “AI security is API security.”
</p>
<p>
With ClickHouse Cloud, Wallarm is ready for whatever comes next. The migration has given them the speed, scale, and flexibility they need to tackle today’s threats while staying ahead of the new risks that come with AI and agentic AI adoption. As APIs continue to power the digital world, Wallarm remains focused on helping security and DevOps teams detect and block attacks in real time, so their businesses can keep moving forward with confidence.
</p>
<p>
To learn more about ClickHouse and see how it can reshape your team’s data operations, <a href="https://clickhouse.com/cloud">try Clickhouse Cloud free for 30 days</a>.
</p>