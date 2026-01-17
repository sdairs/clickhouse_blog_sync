---
title: "ClickHouse welcomes LibreChat: Introducing the open-source Agentic Data Stack"
date: "2025-11-04T09:37:29.245Z"
author: "Ryadh Dahimene and Danny Avila"
category: "Product"
excerpt: "We are excited to announce that ClickHouse has acquired LibreChat, the leading open-source AI chat platform."
---

# ClickHouse welcomes LibreChat: Introducing the open-source Agentic Data Stack

We are excited to announce that ClickHouse has acquired LibreChat, the leading open-source AI chat platform that offers a unified interface for interacting with a wide range of large language models (LLMs), giving users and organizations full control over their data, agents, and conversations. We couldn't be more thrilled to welcome Danny Avila (the founder of LibreChat) as well as the LibreChat team and community into the ClickHouse family.

LibreChat becomes a core component in our vision for <a href="https://clickhouse.com/blog/agent-facing-analytics" target="_blank">Agent-Facing Analytics</a>, creating a truly open-source Agentic Data Stack. By combining LibreChat's powerful user experience and AI agent framework with ClickHouse's analytical capabilities at scale, it has never been easier to build analytics agents that can be leveraged to expose massive datasets to agents operating on behalf of users.

## Who is building agentic analytics already?

Usually, in similar announcements, the user quotes are often buried deep into the post. We’ll try to do things a bit differently here and lead with the raw, unfiltered user feedback, then state our thesis right after (you can skip straight to our investment thesis by clicking <a href="https://clickhouse.com/blog/librechat-open-source-agentic-data-stack#reducing-time-to-insight">here</a>).

### Shopify

Shopify, a global e-commerce leader, has embedded AI across its operations, giving employees access to advanced models through a unified internal platform. Using the <a href="https://www.firstround.com/ai/shopify" target="_blank">open-source LibreChat platform</a>, Shopify built tools like an RFP assistant that pulls from company data, rates response confidence, and improves over time.

> “LibreChat powers reflexive AI use across Shopify. With near universal adoption and thousands of custom agents, teams use it to solve real problems, increase productivity, and keep the quality bar high. By connecting more than 30 internal MCP servers, it democratizes access to critical information across the company” \
> \
> *Matt Burnett, Senior Engineer at Shopify*

<div style="margin-top:20px; display: flex; justify-content: center;">
<blockquote class="twitter-tweet"><p lang="en" dir="ltr">Shopify runs an internal fork of librechat, and we merge most everything back. I highly recommend other companies give this project a look for their internal LLM system. It works very well for us. <a href="https://t.co/ihExJyXY2i">https://t.co/ihExJyXY2i</a></p>&mdash; tobi lutke (@tobi) <a href="https://twitter.com/tobi/status/1932846291794510241?ref_src=twsrc%5Etfw">June 11, 2025</a></blockquote> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
</div>

### cBioPortal

The <a href="https://www.cbioportal.org/" target="_blank">cBioPortal for Cancer Genomics</a> provides visualization, analysis, and download of large-scale cancer genomics data sets. The team at cBioPortal recently launched the chat-based <a href="https://chat.cbioportal.org/" target="_blank">cBioAgent</a> that allows users to interact with genomics datasets in plain text (<a href="https://chat.cbioportal.org/share/s2NZmrgtC7neWPM0L3Vl2" target="_blank">example interaction</a>).

> “By leveraging the ClickHouse, MCP, and LibreChat stack, we rapidly delivered a prototype to cBioPortal users that empowered them to ask entirely new questions about cancer genomics and treatment trajectories, get quick answers, and explore data in ways not possible through the existing UI. It puts discovery at cancer researchers' fingertips.” \
> \
> *Ino de Bruijn, Manager Bioinformatics Software Engineering, cBioPortal*

### Fetch

<a href="https://fetch.com/" target="_blank">Fetch</a> is a leading mobile rewards app that allows users to earn points by scanning shopping receipts and redeem them for gift cards. Fetch recently launched <a href="https://fast.fetch.com/" target="_blank">FAST</a>: an AI-powered tool that turns household purchase behavior into business intelligence, insights, and media activation. Running a custom UX for the FAST portal, this use case is a great illustration of user-facing agentic analytics.

> “We built our new product, FAST by Fetch, on ClickHouse to help users instantly discover insights and drive efficient activation. We see agentic analytics as the future of data interaction, enabling more intuitive, dynamic, and impactful use of information. With its unmatched speed and scalability, ClickHouse is well-positioned to power this new generation of agentic experiences, and we’re thrilled to grow our partnership together.” \
> \
> *Sam Corzine, Director of Machine Learning, Fetch*

### SecurityHQ

SecurityHQ is a global Managed Security Service Provider (MSSP) offering 24/7 threat detection, response, and risk management through its worldwide Security Operations Centres.

> "We reached out to ClickHouse to present our use case in building an Agentic AI with ClickHouse MCP and LibreChat similar to what <a href="https://clickhouse.com/blog/agenthouse-demo-clickhouse-llm-mcp" target="_blank">AgentHouse</a> provide. After understanding the implementation strategy used for AgentHouse, we managed to create a robust working prototype of what we wanted. The integration between ClickHouse cloud and the LibreChat using the MCP server has been flawless, making them one of, if not the best use of text-to-SQL implementation I have ever seen. Now that ClickHouse and LibreChat has joined forces will provide even more seamless interaction to our use case in building Agentic Analytics. Looking forward for a LibreHouse cloud solution for agentic analytics." \
> \
> *Nidharshanen Selliah, Associate Data Engineer, SecurityHQ*

### Daimler Truck

Daimler Truck, one of the world’s largest commercial vehicle manufacturers, has deployed LibreChat internally to give all employees secure access to chat tools and data agents. The system democratizes AI use across the company while protecting data and meeting compliance standards. They published a <a href="https://www.daimlertruck.com/en/newsroom/stories/daimler-truck-makes-artificial-intelligence-accessible-to-all-employees-worldwide-with-librechat" target="_blank">detailed story</a> about their setup of LibreChat.

> “With LibreChat, Daimler Truck is making the power of modern AI available to all employees. This enables the company to bring innovation and progress into everyday work – simply, transparently, securely, and full of new opportunities.” \
> \
> From: <a href="https://www.daimlertruck.com/en/newsroom/stories/daimler-truck-makes-artificial-intelligence-accessible-to-all-employees-worldwide-with-librechat" target="_blank">https://www.daimlertruck.com/en/newsroom/stories/daimler-truck-makes-artificial-intelligence-accessible-to-all-employees-worldwide-with-librechat</a>

### and … ClickHouse

Finally, we also use LibreChat on top of our ClickHouse data warehouse internally as well. We deployed several agents that range from product analytics to billing data and support cases analysis. We’ll let you guess from the screenshot below which one is which.

![image1.png](https://clickhouse.com/uploads/image1_4a06083ea0.png)

> “Internally, we also use LibreChat for data analysis and it now handles \~70% of our data warehouse queries for 200+ users. The productivity boost has been remarkable. What impressed me most is LibreChat's vibrant community that continuously contributes and innovates. The synergy between ClickHouse Cloud's blazing-fast query performance and LibreChat's flexible, multi-LLM architecture is unlocking a new generation of data analysis agents \- real-time, secure, powerful, and accessible.” \
> \
> *Dmitry Pavlov, Director of Engineering, ClickHouse*

Now, let’s dive into the motivation behind the Agentic Data Stack.

## Reducing Time to Insight {#reducing-time-to-insight}

<a href="https://benchmark.clickhouse.com/" target="_blank">We are obsessed with world-class speed and performance at ClickHouse.</a> However, traditional analytics workflows often involve multiple handoffs between data engineers writing queries, analysts building dashboards, and business users interpreting results. Each step introduces latency on the left and right sides of the database, often measured in hours or days.

With agentic analytics, that timeline collapses to seconds or minutes. A product manager can ask "What's driving the spike in churn last week?" and immediately receive not just the answer, but the underlying queries, explorations, visualizations, and potential next questions to explore.

This is closely aligned with our own experience at ClickHouse. Earlier this year, we introduced our first agent, Dwaine (Data Warehouse AI Natural Expert): an internal agent that enables our team to query business data through natural language. Since then, questions like "What's our current revenue?", "How is this customer using our product?", "What issues are customers experiencing?" or "What's our website traffic and conversion rate?" are getting close to instant answers.

Dwaine has transformed how our internal teams access insights, eliminating the bottleneck of hand-writing SQL queries and data requests. Just one month after rollout, ClickHouse internal users generated more than 15 million LLM tokens in a single day on Dwaine. As of October 2025, this is now up at 33 million tokens per day.

!['The first 3 months of DWAINE - Token Counts per Day'](https://clickhouse.com/uploads/image5_2176472bfd.png)

*The first 3 months of DWAINE - Token Counts per Day*

If you want to experience the power of agentic analytics first-hand, try the public <a href="https://clickhouse.com/blog/agenthouse-demo-clickhouse-llm-mcp" target="_blank">AgentHouse</a> demo, which exposes publicly available datasets via the Agentic Data Stack.

!['AgentHouse in use'](https://clickhouse.com/uploads/agent_house_v3_7e163b96ca.gif)

## The open-source advantage

The agentic open-source landscape is currently centered around developer tooling and SDKs, which makes perfect sense given that developers are typically the earliest adopters of emerging technologies. The main open-source projects in this space aim to empower builders to create, extend, and customize agentic systems with SDKs, frameworks, orchestration layers, and integrations. This developer-first focus helps establish the foundational ecosystem and standards needed before broader consumer applications take off.

We see the Agentic Data Stack as one of the first proposals of a composable software stack that focuses on the higher-level integration story, allowing users to get started and deliver value in no time. Both ClickHouse and LibreChat share the same open-source software DNA, and joining forces strengthens our commitment to that vision:

* **LibreChat remains 100% open-source** under its existing MIT license
* **Community-first development** continues with the same transparency and openness
* **Expanded roadmap** to bring an even more enterprise-ready analytics experience.

This proven playbook is the same one that we applied when joining forces with <a href="https://clickhouse.com/blog/clickhouse-welcomes-peerdb-adding-the-fastest-postgres-cdc-to-the-fastest-olap-database" target="_blank">PeerDB</a> to provide our ClickPipes CDC capabilities, and <a href="https://clickhouse.com/blog/clickhouse-acquires-hyperdx-the-future-of-open-source-observability" target="_blank">HyperDX</a>, which became the UX of our observability product, ClickStack.

We believe that being good stewards of open-source means not just maintaining code, but actively investing in and growing the communities that depend on it.

## Limitations

Large Language Models can be tricky to use in production. While grounding responses in real-time data often helps, AI agents are not immune to hallucinations: situations where the model generates incorrect information with high confidence.

Our own experience running internal agents within ClickHouse taught us that the best remediation comes from providing the LLMs with the maximum and most accurate context possible. This can be achieved by commenting the tables using the SQL <a href="https://clickhouse.com/docs/sql-reference/statements/alter/column#comment-column" target="_blank">COMMENT</a> syntax, for example, or by providing more context in-line, in the chat, or part of the system prompt of the LLM session.

Finally, robust evaluations are critical for agentic analytics in production because they turn qualitative agent behavior into quantifiable insights, enabling teams to measure effectiveness, detect regressions, and continuously improve system performance.

## What's next for LibreChat and ClickHouse users?

For existing LibreChat deployments: nothing changes. LibreChat continues to work exactly as it does today, and we are committed to continuing to invest in it and make sure the community thrives.

For ClickHouse users, over the coming months, we'll be releasing tailored integration capabilities that make LibreChat a native part of the ClickHouse experience without sacrificing its generic integration capabilities. Think of it as a “happy path” for agentic analytics in LibreChat. This will include:

* Seamless integration of the LibreChat experience alongside your ClickHouse Cloud instances
* Extended support for data visualizations rendering in LibreChat
* OAuth, end-to-end user identification, security, and governance schemes.
* Tailored context providing (aka. semantic layer)

And many more. Please stay tuned for more updates by joining our communities in <a href="https://clickhouse.com/slack" target="_blank">Slack</a> and <a href="https://discord.com/invite/librechat-1086345563026489514" target="_blank">Discord</a>.

Finally, for users of the <a href="https://code.librechat.ai/pricing" target="_blank">LibreChat Code Interpreter API</a> (a paid service offered by LibreChat that provides a sandboxed environment for executing code). We are planning to evolve this offering and discontinue this API in its current form. We understand that changes can take time to implement, and for this reason, we decided to set the timeline of this transition for the next 6 months (targeting May 1st, 2026). We will reach out to all code interpreter users directly to coordinate the transition.

## Get started

**For LibreChat users:** Continue using LibreChat as you always have, and join our community on <a href="https://discord.com/invite/librechat-1086345563026489514" target="_blank">Discord</a> if you haven’t already, to connect with other users building agents.

**For ClickHouse users**: You can already deploy the Agentic Data Stack by following our user guides in our public <a href="https://clickhouse.com/docs/use-cases/AI/MCP/librechat" target="_blank">documentation</a> and <a href="https://www.youtube.com/watch?v=fuyu-AnfRDA" target="_blank">videos</a>

**For everyone else**: Experience the power of the open-source Agentic Data Stack with <a href="https://llm.clickhouse.com/" target="_blank">AgentHouse</a>, and let us know how we can help you succeed\!

<iframe width="768" height="432" src="https://www.youtube.com/embed/fuyu-AnfRDA?si=yMkEk9QtT0bLpLo6" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

As always, the ClickHouse team would be honored to partner with you on your journey toward agentic analytics. Whether you're using LibreChat today or are interested in building analytical agents, please <a href="https://clickhouse.com/company/contact" target="_blank">contact us</a>\!

