---
title: "The future of observability won’t be one proprietary AI agent. It will be thousands built by teams."
date: "2026-06-22T12:19:19.034Z"
author: "Mike Shi"
category: "Product"
excerpt: "We don’t think observability will be dominated by a single AI agent. The future belongs to teams building agents around their own systems, workflows, and operational knowledge."
---

# The future of observability won’t be one proprietary AI agent. It will be thousands built by teams.

The common vendor bet in observability right now is convergence.

One SRE agent, built into one platform, trained around one vendor’s view of how incidents should be investigated. It understands your telemetry, answers your questions, explains what went wrong, and eventually helps fix production before anyone opens a dashboard.

That version of the future will be useful, but it will also be too narrow.
Observability does not work like a generic support queue. Debugging is shaped by the systems a team owns, the way those systems fail, the data they trust, the runbooks they follow, the tools they use, and the operational scars they have accumulated over time. A database team, frontend team, payments team, and infrastructure team do not investigate production the same way.

**In this post, we explore why we think the future of observability will not be one proprietary AI agent, but thousands built by teams like yours.**

## AI agents are becoming the new interface for observability

I hope most people would agree that the shift to AI agents in observability is no longer a particularly bold prediction.

Today, most investigations begin with a human opening dashboards, searching logs, inspecting traces, and manually gathering context. Increasingly, that work is being delegated to agents. Models are already capable of querying telemetry, summarizing findings, identifying patterns, and generating plausible hypotheses about what is happening within a system.

![agents_humans.png](https://clickhouse.com/uploads/agents_humans_b65d7ba6ce.png)

As models continue to improve, the interface to observability will increasingly become human → agent → data instead of human → dashboard → data. Engineers will still decide what action to take, but much of the mechanical work of an investigation will happen before they ever touch a chart or write a query.

<blockquote>
<p>"We actually see a trend shift in our Slack incident channels. Engineers previously used to share links to logs or metrics. Now teams are sharing snippets of AI investigations and diving deep into it." <br><br></p>
<p>Anil K, DoorDash</p>
</blockquote>

## AI changes the shape of observability workloads

Most discussions about observability agents focus on what the agents can do. Far less attention is given to what happens underneath when they become a normal part of the workflow.

A human investigator is relatively constrained. They open a handful of dashboards, run some queries, inspect a trace or two, and gradually narrow the search space. Even experienced engineers can only evaluate so many possibilities at once.

An agent has no such limitation. While an engineer may compare two time windows, an agent can compare twenty. While a human might manually investigate a few likely causes, an agent can pursue dozens of hypotheses simultaneously, continuously gathering evidence and eliminating dead ends as it goes.

<iframe src="https://clickhouse.com/uploads/clickstack_vs_traditional_82948145ce.html"  width="100%" height="auto" style="aspect-ratio: 1100/550;"></iframe>

The practical consequence is that investigations become broader and place greater demands on the underlying systems. Agents can examine more historical data and explore far more potential explanations before converging on an answer. This all results in more queries requiring low-latency responses.

<blockquote>
<p>"Agents could brute force it — make 10 queries instead of what, if I query, I would make two dashboard clicks. Which means our API layer or storage have to be robust to take that non-linear pattern of queries." <br><br></p>
<p>Anil K, DoorDash</p>
</blockquote>

It also changes the requirements around the underlying data. Agents can only reason over the context they are given. If historical data has been discarded, important context may be missing. If telemetry has been heavily sampled, critical evidence may simply not exist in the dataset. Unlike experienced engineers, agents cannot compensate for these gaps with intuition or institutional knowledge. Their conclusions are constrained by the completeness and fidelity of the data available to them.

Most observability platforms were designed around human investigators and the workloads they generate. The next generation will increasingly need to support investigations carried out on behalf of humans.

## An industry betting on the great SRE agent

A lot of companies are investing in building for a simple vision of the future: the universal SRE agent.

![god_agent.png](https://clickhouse.com/uploads/god_agent_8d5db894d0.png)

This is a compelling idea. An observability vendor provides the platform, the data, and the agent. Engineers ask questions in natural language instead of learning dashboards, writing queries, or navigating telemetry. Over time, the agent becomes increasingly capable, eventually handling much of the investigation process on its own.

There is real value in this model. Most observability tools remain difficult to use, and agents have the potential to dramatically lower the barrier to understanding and operating complex systems.

Models will also continue to improve and will become better at reasoning, better at writing SQL, and better at packaging common investigation patterns into reusable workflows. Much of what we consider expert knowledge today will become increasingly accessible through agents.

## The hard part of debugging: context

The problem is that debugging does not converge quite as neatly as software vendors would like. 

While models continue to improve, what remains difficult is context. 

The next step in an investigation depends on far more than the telemetry sitting inside an observability platform. It depends on how a team operates, which signals it trusts, what has broken before, how ownership is divided, and where operational knowledge lives. Much of that context is scattered across runbooks, tickets, postmortems, Slack threads, internal documentation, deployment systems, and the heads of experienced engineers.

<blockquote>
<p>"Ring Central is a 25-year-old company. There is a lot of tribal knowledge within the operations team that is not documented anywhere, no matter whether we've connected all the wikis. If you don't have any data to give it, it's going to just hallucinate." <br><br></p>
<p>Sushant Hiray, AI Leader, RingCentral</p>
</blockquote>

## Every team works differently

Furthermore, two companies running similar technology stacks can investigate the same incident in completely different ways because their systems, teams, and operational history are different. A vendor can package best practices, but it cannot package the accumulated experience of every engineering team that uses its product.

Much of the context required to debug production systems lives outside the observability platform itself. It is scattered across runbooks, tickets, postmortems, internal documentation, Slack threads, deployment systems, and the institutional knowledge of engineers who have operated the system for years. The location of that knowledge, the way teams are structured, and the processes they follow vary not only across organizations, but across industries and functions within those organizations.

None of these approaches is inherently correct. They simply reflect different mental models built through experience. The signals teams trust, the workflows they follow, and the context they rely on are often unique to the systems they operate.

## A more open model for agentic observability

Taken together, these challenges point toward a very different future than the one many vendors are betting on. 

As agents become the primary interface for observability and investigations increasingly shaped by organizational context, the value shifts away from a single universal agent toward agents built for specific teams and domains.

<blockquote>
<p>"Instead of building a super-cooled arrangement from the get-go, we doubled down on building a headless platform - improve our APIs, our data storage - and build an observability MCP so that we would unblock or enable every engineer or every team to build their own agentic workflows, which are more tailored towards their debugging use cases." <br><br></p>
<p>Anil K., DoorDash</p>
</blockquote>

Instead of converging on a single SRE agent, we believe observability is more likely to evolve into an ecosystem of specialized agents, each optimized for a particular organization, team, or problem space. Some will focus on infrastructure, others on databases, security, payments, customer experience, or internal platforms. Many will be built around an organization’s own runbooks, documentation, workflows, business logic, and operational knowledge.

Just as importantly, this future depends on openness. 

By "openness," we do not simply mean open-source software. We mean giving teams and individual engineers the freedom to choose the best technology for each layer of the stack:  models, harnesses, tools, workflows, and interfaces. It means being able to build agents around the systems and processes that already exist within an organization rather than adapting those processes to fit a vendor’s view of how observability should work.

It also means having the freedom to choose the layers beneath those agents. Teams should control where their data lives, how skills are developed and managed, which MCP gateways and servers sit in front of production systems, and how the agent’s behavior is observed, governed, and integrated into the rest of the engineering environment.

<blockquote>
<p>"The way we prefer is to partner with platforms that give us enough flexibility that there's an opportunity for us to build on top of that. As long as it works with enough of our internal tooling, that's the sweet spot."<br><br></p>
<p>Sushant Hiray, AI Leader, RingCentral</p>
</blockquote>

The most successful observability platforms will not be the ones that force everyone into a single way of working. They will be the ones that provide a shared foundation upon which thousands of different agents can be built.

## Agents need shared context
If every team or even individual builds and adapts their own agents, investigations will not happen in one place. One engineer may start in an IDE, another in a notebook, another in an internal chat interface, and another through a custom incident workflow. Agents may run in different harnesses, use different models, and follow different investigation paths, even when they are all trying to understand the same production issue.

This creates a collaboration problem. Investigation output cannot remain trapped inside transient chat sessions or private agent traces. Teams need durable, inspectable artifacts that show what was queried, what evidence was found, which hypotheses were explored, and why a conclusion was reached. This matters for humans reviewing an incident, but it also matters for future agents that need to learn from previous investigations instead of starting from scratch every time.

<video autoplay="1" muted="1" loop="1" controls="0">
  <source src="https://clickhouse.com/uploads/Notebook_Video_Product_D_1280p_crf20_e65a30386e.mp4" type="video/mp4" />
</video>


As a result, agentic observability will require some form of persistent investigation surface where humans and agents can collaborate. A place where investigations can be shared, reviewed, rerun, refined, and built upon over time. Whether an investigation begins in an IDE, a notebook, a chat interface, or a custom workflow is ultimately less important than having a common place where the results can be preserved and reused.

These investigation artifacts become more than a record of what happened. They become a growing body of operational knowledge that future engineers and future agents can draw upon when similar problems arise.

## Humans will still be the control plane

All of this assumes that humans remain in the control plane, at least for now.

Agents can gather evidence, execute investigations, explore hypotheses, and surface relevant context far faster than any individual engineer. But they still lack the judgment required to understand business priorities, weigh competing risks, navigate ambiguity, and ultimately decide what action should be taken. Those decisions remain the responsibility of the people operating the system.

Perhaps that changes over time. It is easy to imagine a future where specialized agents collaborate with one another, continuously monitoring systems and autonomously resolving classes of incidents without human involvement. But that is not the future we are building for today.

Today, the more practical and useful model is collaboration. Agents accelerate investigations. Humans provide direction. Agents gather context. Humans make decisions. The notebook becomes the shared workspace where those interactions take place, creating a durable record that can be inspected, shared, refined, and reused.

Whether the future eventually becomes fully autonomous or remains permanently human-guided, one thing seems increasingly clear: the future of observability will not be one proprietary AI agent sitting behind a single vendor interface.

It will be thousands of agents, built by you.





---

## Get started Managed ClickStack today

Managed ClickStack gives your teams an open foundation for agentic observability, powered by the performance of ClickHouse.

Get started with Managed ClickStack in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?intent=o11y&loc=blog-cta-985-get-started-managed-clickstack-today-sign-up&utm_blogctaid=985)

---