---
title: "How Suprema Gaming made its data platform agent-ready with ClickHouse Cloud"
date: "2026-08-25T18:52:53.704Z"
author: "ClickHouse"
category: "User stories"
excerpt: "Suprema Gaming migrated its analytics platform from Snowflake to ClickHouse Cloud to power a company-wide shift toward agentic operations. "
---

# How Suprema Gaming made its data platform agent-ready with ClickHouse Cloud

## Summary

- Suprema Gaming migrated its analytics platform from Snowflake to ClickHouse Cloud to power a company-wide shift toward agentic operations. 
- The migration cut warehouse costs by 62% while reducing query latency from minutes to milliseconds and improving data freshness from four hours to real time. 
- Every metric was validated to the cent against the reference source before cutover, giving the business the confidence to let AI agents answer directly off the warehouse. 
- Today Suprema runs an early production deployment of ClickHouse Agents, with specialized agents serving teams across the group.


[Suprema Gaming](https://supremagaming.com.br/en) is one of Latin America’s largest gaming companies. Founded in 2019 by three poker enthusiasts and headquartered in Sorocaba, Brazil, it has grown out of [Suprema Poker](https://supremapoker.com.br/en), the world’s largest B2B poker league, into a portfolio of brands whose licensed technology reaches over 500,000 players in more than 70 countries.

In 2025, the freshest data anyone could look at was already four hours old. For a business where thousands of players are active, that lag prevented the team from running investigations, diagnosing incidents, or understanding user behavior at the moment it happens.

“We had the mission to bring modernization to the entire process,” Edilson Junior, Data Platform Architect says. That mission was entrusted to both Edilson and Aluizio Cidral Junior, data engineer. For Suprema, that meant consolidating the group’s fragmented data picture into a single real-time analytics platform while ensuring security and governance.

Behind that mandate was a broader vision: co-founder and CEO Fernando Almeida wanted Suprema to become an agentic-first business, where people use AI agents, not static dashboards, to ask questions and act on the answers. 

“What was missing to make it all work,” Edilson says, “was ClickHouse.”

## Why they needed to go beyond Snowflake
Suprema’s old stack ran on Snowflake. Data flowed from source systems into S3, through SQS and Snowpipe, and into what Edilson describes as a solid, mature database. “Although it was balanced and working well,” he says, “but we realized some things were missing.”

The first was query speed. On Snowflake, queries regularly took minutes, too slow for the real-time, interactive experience the team wanted to deliver to its end users. This was the difference, as Edilson puts it, between “waiting for the report” and “real-time analysis.”

The second was recurring dbt effort. The dbt pipeline was heavy enough that a full rebuild could only be run once a day, so the freshest data was always hours behind. “We didn’t have the possibility of live data,” Edilson says. “It was very much after the fact.”

The third was cost. With Snowflake, cost scaled with every new warehouse and consumer. This made the vision of putting data in front of the whole Suprema group (internal teams, products, partners) expensive to even consider. Snowflake might have been able to get them further, Edilson says, but only by spending considerably more money.

## Choosing ClickHouse Cloud for an agentic future
When Edilson joined Suprema, in 2025, Snowflake was the production analytics platform, and it was working. In 2026, to explore what an AI-native operation would require without disturbing production, Fernando spun oﬀ a small internal team to validate the model.

The move toward ClickHouse was driven by several converging signals. The team already knew the engine firsthand: one of Suprema’s technology partners ran its database on ClickHouse, giving the team direct access to the system—and its speed consistently impressed them. Suprema’s data leadership had also become familiar with ClickHouse through industry events.

As confidence grew, Edilson led a formal evaluation of ClickHouse, Databricks, and Snowflake, comparing latency, cost, and AI readiness. ClickHouse came out ahead on every criterion. The team then built a complete proof of concept themselves. Edilson handled ingestion and the agent layer, using LibreChat on EC2 with trace evaluation through Langfuse, while Aluizio built the full dbt transformation layer. 

The decisive moment came months later, when Fernando took the lead on the agentic initiative. The need was clear: agents require fast access to fresh data. By then, the results of the team’s work had reached him through multiple voices. The final call was his, and he made it with a clear vote of confidence: “Edilson, if you say it’s going to be ClickHouse, I trust your team.” And Suprema went ahead and migrated from Snowflake to [ClickHouse Cloud](https://clickhouse.com/cloud) on AWS.

![01-batch-reporting-to-agentic-operations 1.jpg](https://clickhouse.com/uploads/01_batch_reporting_to_agentic_operations_1_d1cdb8e6f5.jpg)

## Architecting a real-time platform
“One of the best decisions in this transition,” Edilson says, “was the way Aluizio designed the real-time treatment of the data. The architecture gave us the map, but someone still had to define how the data would be handled as it moved through the system.”

When an event occurs in a source system, it moves through a pipeline the team builds only once. dbt, integrated with GitHub Actions, deploys the entire structure in a single pass; from there, the engine takes over. There are no external cron jobs, no separate orchestrator, and no Airflow in the pipeline. The team only needs to revisit the pipeline when the design of the layer architecture changes. 

Data moves across the warehouse layers in seconds, with a p95 lag of roughly one minute. On the consumption side, direct reads from the marts were measured at 27x faster than their previous solution. That speed allows users to check a number through a conversational BI agent without interrupting the flow of the conversation. 

Ingestion was rebuilt around real time as well, along two separate paths. For sources ClickHouse supports natively, [ClickPipes](https://clickhouse.com/cloud/clickpipes) streams changes straight into the warehouse through change data capture. For sources it doesn’t, the team uses Debezium and Kafka, the latter of which doubles as a reusable feed for external clients. Where Suprema once staged everything through S3 and loaded it in batches, the migrated sources now arrive second by second, right after each event happens.

![02-design-structure-once-data-flows 1.jpg](https://clickhouse.com/uploads/02_design_structure_once_data_flows_1_0e1628aa7d.jpg)

## Security and governance: The foundation of trusted AI agents
Opening the warehouse to products, partners, and external data feeds only works if the underlying data remains protected. Aluizio integrated ClickHouse’s native security and governance capabilities into the architecture, recreating in dbt the controls previously used in Snowflake: [role-based access](https://clickhouse.com/docs/operations/access-rights) tailored to each consumer and [PII masked](https://clickhouse.com/docs/cloud/guides/data-masking) at query time, all without relying on external tools.

The balance between accessibility and protection is deliberate. Data engineering works closely with Suprema’s data protection officer, Leonardo Kimura, to define the controls, embedding governed access, traceability, least privilege, and information protection directly into the architecture.

>“Our goal was never just to protect personal data. From the start, we set out to build a platform where information security, privacy and governance are part of the architecture. This creates the foundation for AI agents to evolve on real data without compromising confidentiality, compliance or trust. — Leonardo Kimura, Data Protection Officer, Suprema Gaming

Governance at Suprema goes beyond regulatory compliance; it is a core enabler of the company’s AI strategy. Agents are treated as governed consumers and held to the same standards as every other user of the platform, including access control, data minimization, PII masking, traceability, and auditing. As new agents enter the ecosystem, the controls evolve alongside them, allowing Suprema to innovate without compromising trust in its data.

The warehouse is organized by business unit, with a unified, cross-product customer view layered on top. Built by Aluizio in dbt, this modeling approach is what makes Senna’s “company 360” view possible. The group’s companies are not separate silos that an agent must piece together; their databases are designed from the outset to be analyzed as a single, connected system.


---

## Get started today

Interested in seeing how ClickHouse works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-1649-get-started-today-sign-up&utm_blogctaid=1649)

---

## Numbers the business can trust

Speed would not count for much if Suprema could not trust the numbers. The heart of the migration, Edilson says, is parity, with every metric proven to the cent against the reference source before it goes into production. Whatever number the business reads is the same one the back office shows. For every domain migrated so far, the team audited results month by month until they matched exactly, and on the rare occasion a figure did not line up, they traced it to a specific cause.

To scale that without creating a manual bottleneck, Aluizio designed an iterative validation system. AI agents compare results from the new platform against the reference source, flag discrepancies, and refine the underlying rules until the metrics align. Each validated rule is then captured as a version-controlled dbt test. Every migrated domain passed through this loop before cutover, turning the once-manual task of proving it to the cent into a repeatable process.

The validation process also turned up problems that had been invisible before, such as ingestion gaps and test accounts skewing metrics. Each one became a traceable fix in code. 

Because ClickHouse answers queries in milliseconds, this checking can happen conversationally, in a chat window, instead of in some slow, separate reporting cycle. Most companies start by connecting an LLM to data that was never designed to support an agent. Suprema built its foundation in the opposite order, with each architectural choice addressing a common failure mode of AI over data.

The data is canonical, reducing the risk of the agent producing inconsistent answers. It is real time, so responses reflect what is happening now rather than what happened yesterday. Queries return in milliseconds, keeping the conversation fluid. And governance is built in, with PII masked at query time and least-privilege access defined for each consumer, allowing agents to serve partners without exposing sensitive information.

## Powering Suprema’s shift to agentic operations
Senna is the visible face of Suprema’s agentic system. It gives business users a conversational way to ask questions, check numbers, and act on insights, but behind it is a fleet of 10 specialized agents, each responsible for a distinct function, from data modeling and dbt development to validation, and freshness monitoring.

![03-ai-built-foundation 1.jpg](https://clickhouse.com/uploads/03_ai_built_foundation_1_2936e382f0.jpg)

Their knowledge does not live in a collection of loose prompts. It is encoded in six version-controlled skills, one for each domain, and maintained in the repository as code. When a mart changes, the corresponding skill is updated in the same pull request. This ensures that each agent routes questions to the correct structure rather than improvising, because its knowledge is governed by the same version-control process as the pipeline itself.

What makes Suprema’s approach especially distinct is that Senna, the agentic platform now serving the business, was itself built with agents. The migration from Snowflake to ClickHouse, including the layer architecture, ingestion pipelines, and specification of every dbt model, was carried out with agents that had direct access to ClickHouse Cloud throughout development.'

The work followed a spec-driven approach across each track. Aluizio led dbt modeling and transformations, while Edilson focused on ingestion. The result is a platform built with agents to support a growing ecosystem of specialized agents. That continuity, with AI helping create the foundation on which other AI systems operate, is what Suprema means by “agentic-first.”

The system is also fully observable. Every conversation generates controlled traces in Langfuse, including latency, cost, and the SQL behind each answer. This makes the agentic layer just as auditable as the data pipeline.

>“How can I use AI to say, ‘Analyze this’ or ‘I recommend taking action here,’ if I do not have a complete view of the company’s data? Senna, powered by ClickHouse, brings together management information from across the entire business, connecting finance and accounting with marketing, growth, and people management. It gives us a standardized, 360-degree view of the company and turns that data into practical insights for the people making decisions every day. Ultimately, it amplifies my managers’ ability to make better decisions.” 
— Fernando Almeida, co-founder and CEO, Suprema Gaming

Perhaps the most novel piece, Edilson adds, is a “self-reinforcing feedback loop” that runs through the chat itself. A business user asks an agent a question and gets an answer anchored in live data. They compare it against their back office; if a number looks off, they screenshot it back into the agent, which has the context to check the calculation and flag what needs to change. The user shares that conversation with Edilson’s team, who fix it at the right target, and the improvement flows back into the platform. The data team isn’t paged for every request; the answers come from the system, while the loop makes the system better each time.

![04-parity-to-the-cent-repeatable 1.jpg](https://clickhouse.com/uploads/04_parity_to_the_cent_repeatable_1_e674929b33.jpg)

That agentic-first mindset is taking hold across the whole group. “We create more and more of this community mindset around agentic analytics, where not only internal teams work more with us, but product teams start to have this agentic world too,” Edilson says. “We can create dynamics, build warehouses, and give decision-makers new paths based on real numbers—and now give partners the ability to consume this data with ClickHouse, via API.”

## The results: faster, fresher, and 62% cheaper
One of the biggest areas Suprema looked to improve when they switched from Snowflake to ClickHouse Cloud was query speed. The results bear that out. As Edilson says, “We stopped talking in minutes and started talking in milliseconds.” Data freshness has also seen a massive boost. The data that once took four hours to surface now lands in real time, and the pipeline keeps it current to within about a minute.

And all of it costs far less. As Edilson notes, moving to ClickHouse Cloud has cut Suprema’s warehouse spend by roughly 62%. Importantly, that cost no longer climbs with every new warehouse or consumer the business adds, like it did under the previous setup.

>“Before, I spent 20% of my time planning and 80% executing because I had to start delivering immediately to meet the deadline. Today, that ratio has reversed. I spend 80% of my time planning thoughtfully and understanding the business in detail, then use AI tools to accelerate execution in the remaining 20%.”  
— Fernando Almeida, co-founder and CEO, Suprema Gaming

Today, Suprema has moved the vast majority of its workloads to ClickHouse. The method is now a repeatable playbook: map the source and business rule, port the transformation, validate to the cent, cut over, automate, and then run it again for the next domain. Several of the group’s products have already completed the full cycle in production, proving the process works. That is why the next wave is no longer a bet, but a schedule. The data source may change, but the method remains the same.
The transformation also extends beyond the data platform. Every company in the Suprema group is moving toward the agentic world with the same approach and mindset. As each one joins, Senna’s cross-product view expands and the agents gain a deeper understanding of the business.

Led by Edilson, with backing from Fernando and the rest of the leadership team, what began as a push for lower latency and lower cost ended up reshaping how the group works, turning Suprema into a business run on AI agents, ready for what comes next.

