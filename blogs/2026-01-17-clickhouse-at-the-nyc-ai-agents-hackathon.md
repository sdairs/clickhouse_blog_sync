---
title: "ClickHouse at the NYC AI Agents Hackathon: Building Agentic AI on Real‑Time Data"
date: "2025-12-08T21:13:51.064Z"
author: "Zoe Steinkamp"
category: "Community"
excerpt: "ClickHouse joined the NYC AI Agents Hackathon as the only database sponsor, powering real time autonomous agents on live data. This recap highlights winning projects like VitalSignal and RedBot and shows how builders use ClickHouse as the real time backbo"
---

# ClickHouse at the NYC AI Agents Hackathon: Building Agentic AI on Real‑Time Data

### **Summary**



* 130+ builders packed Datadog’s New York office on a Saturday to ship autonomous AI agents on real data. 

* ClickHouse showed up as the only database sponsor and became the default choice for data‑intensive agent stacks. 

* Two standout ClickHouse‑powered projects, **VitalSignal** and **RedBot**, took home top prizes for tackling global health alerts and chatbot security. 



### **Why we showed up**

Agentic AI is at its best when it can see **fresh data**, reason over it, and act quickly. That’s exactly the kind of workload ClickHouse is built for.

When the organizers of the NYC AI Agents Hackathon invited us to sponsor, we saw a perfect match:



* **The format:** A focused Saturday event at Datadog’s NYC office with ~135 attendees and a hard timebox. That meant serious builders: roughly half the room were working software engineers, alongside ambitious students and indie hackers. 

* **The challenge:** Build autonomous agents that interact with live data and real‑world APIs. 

* **The rules:** Every team had to use at least three sponsor technologies in their stack, an ideal way to show how ClickHouse pairs with AI agents, LLMs, and orchestration tools. 


We brought a small but mighty crew, **Kevin Zhang, Nataly Merezhuk, and Zoe Steinkamp**, to help teams design schemas, model event streams, and wire ClickHouse into their agents. Being the **only database sponsor** gave participants a clear, opinionated path for anything data‑intensive: logs, events, user profiles, vector‑like analytics, you name it.

By the end of the day, roughly 20 projects were submitted, and a large share of them chose ClickHouse as their real‑time backbone.

![1.jpg](https://clickhouse.com/uploads/1_105ae81507.jpg)

![2.jpg](https://clickhouse.com/uploads/2_92880a2537.jpg)

:::global-blog-cta::: 


### **First Place - VitalSignal**

**What they built**

**VitalSignal** is an autonomous AI agent that delivers **personalized global disease outbreak alerts**. It continuously monitors health‑related signals, runs multi‑factor risk analysis by region and user profile, and pushes timely, tailored alerts to people who might be affected.

The core problem: in a world of constant health crises, it’s hard to know **what matters to you and your loved ones** until it’s already mainstream news, often too late.

**How it works**

ClickHouse sits at the **center of the architecture**, storing: 

* User profiles and preferences 
* Scraped and streamed JSON alerts 
* Metadata from other tools (e.g., images and structured outputs) 

* Sponsor tools like **Airia**, **Structify**, and **PhenoML** help extract and structure signals before they land in ClickHouse. 

* An autonomous agent layer continuously evaluates new events, calculates risk scores, and triggers notifications. 


Because ClickHouse can ingest diverse data types and query them in real time, the builder could experiment quickly without worrying about infrastructure limits.

**Inspiration**

The idea came from a mix of the hackathon prompt and a deeply personal frustration:

“I have family in different parts of the world and often find out about health crises in their area only once it hits mainstream news. I wanted an agent that makes this information accessible sooner, in a way that’s actually personalized.”

Health as a “live data source that’s critically important but overwhelming” turned out to be the perfect canvas for an agentic build.

**Build approach**

The VitalSignal creator treated the hackathon like a deployment day, not a brainstorming session:


**Decisions first, hacking second**: 
* Chose ClickHouse as the database early. 
* Pre‑created accounts and API keys for sponsor tools. 

**Docs‑driven development**: 

* Used an LLM for a quick overview of each tool. 
* Relied on official docs for actual implementation details. 

**Stable core, then integrations**: 
* Built the simplest end‑to‑end workflow first. 
* Iteratively layered in more tools and features once the base was solid. 

**The hardest part (and how they solved it)**

The real challenge wasn’t just technical; it was orchestration of both tools and time:



* Technically, orchestrating **six new platforms** under a 5.5‑hour deadline was intense. Having a fast, reliable database at the core meant every new data type “just worked” when added to ClickHouse. 

* Personally, the biggest struggle was **knowing when to stop**. With everything running smoothly, it was tempting to keep adding “just one more feature.” 


The key lesson: in a time‑boxed hackathon, the hardest skill is recognizing when you have a **“good enough” end‑to‑end solution** and having the discipline to ship it.

**Why ClickHouse mattered**

For VitalSignal, ClickHouse was a multiplier:

“I never once had to worry about database limitations. Whether I was storing user profiles, scraped JSON alerts, or image metadata, I knew ClickHouse could handle it and that queries would be lightning‑fast. That confidence let me stay ambitious and build the features that made the project a winner.”

**What’s next**

The plan is to use sponsor credits to turn VitalSignal from prototype into a full‑scale project:



* Refine the architecture for long‑term reliability and scalability. 

* Get an initial set of real users to test and shape the experience. 

* Explore how to keep the app **accessible and free** for the people who need it most. 


**Advice to future hackers**



* Be **strategic with tools**, don’t integrate everything, integrate the *right* things. 

* Make your **core architectural decisions early**. 

* Define your MVP ruthlessly and build an end‑to‑end experience that actually works. 

* A small, polished project beats an ambitious, half‑broken one every time. 

![3.jpg](https://clickhouse.com/uploads/3_e752d8d93d.jpg)



### **Second Place - RedBot**

**What they built**

**RedBot** is an autonomous AI agent that **attacks chatbot endpoints** on your behalf, safely.

It probes your deployed chatbots, looks for vulnerabilities (prompt injection, data leakage, misconfigurations), and then generates **prescriptive remediation plans**, complete with **ROI‑aware recommendations** so teams know which fixes matter most.

As more companies embed chatbots into websites, from car dealerships to marketplaces, security often lags behind adoption. RedBot aims to close that gap.

**How it works**


The team splits responsibilities across: 

* **Data ingestion:** Crawling chatbot endpoints and collecting responses. 
* **Agent design:** Crafting attack strategies and analysis loops. 
* **UI:** A simple interface where users can point RedBot at their own bots and review findings. 

ClickHouse handles the **large datasets** generated by repeated attacks and tests: 
* Storing prompts, responses, and vulnerability signals. 
* Powering fast queries to slice results by endpoint, attack type, severity, and more. 


The result is a system where teams can run many tests, then quickly zoom in on the riskiest behavior.

**Inspiration**

The starting point was a simple observation:

AI chatbots are everywhere on production websites, but security is often an afterthought.

The team wanted a tool that any developer or security engineer could use to **self‑assess** their own chatbot, no red‑team background required.

**Build approach**

With limited time, the team optimized for a **functional prototype**:



* Clear division of labor: one person on ingestion, one on agent logic, one on UI. 

* Early decision to use ClickHouse for speed and scalability, so they wouldn’t hit a wall as data volumes grew. 

* Ruthless prioritization of core flows over “nice‑to‑have” features. 


Integrating all the moving parts under hackathon pressure was the toughest challenge. The team stayed unblocked through **tight communication** and fast iteration cycles.

**What’s next**



* Refining the UI to make results even easier to interpret. 

* Adding more advanced testing modes and integrations with other platforms. 

* Incorporating user feedback to expand coverage of common chatbot architectures and frameworks. 


**Advice to future hackers**



* Start with a **project that clearly delivers user value**. 

* Focus on a **Minimum Viable Product** that you can actually demo end‑to‑end. 

* Lean into your teammates’ strengths and **don’t hesitate to ask mentors for help**, especially on architecture and stack choices. 

![4.jpg](https://clickhouse.com/uploads/4_9f0f746d9b.jpg)



### **What we saw across teams**

Stepping back from the winners, a few patterns stood out across the room:

**Agents + real‑time data = default pattern**

Teams weren’t just calling LLMs, they were building loops: ingest data → store in ClickHouse → compute features → let agents act. ClickHouse became the natural “source of truth” for events, logs, and metrics. 

**Weekends attract serious builders** 

Running the hackathon on a Saturday shifted the mix toward working engineers who were there to **learn fast, build hard, and (hopefully) win prizes**, alongside motivated students. 

**Stacks built around sponsor tech** 

Because teams had to use three sponsor technologies, we saw a common pattern: one AI‑agent platform + an LLM API + ClickHouse for analytics and state. 

**In‑person mentorship really matters** 

Sponsors that showed up in person and stayed active throughout the day saw significantly more adoption. Having multiple ClickHouse engineers on site let us: 

* Pair program on schema design and queries 
* Help debug integrations quickly 
* Suggest patterns that turned “it sort of works” into “this feels production‑grade” 

* Meaningful prizes drive exploration 
 
Offering a strong ClickHouse‑specific prize made it easier for teams to justify building something **data‑intensive** rather than a minimal demo. It’s a simple signal: if you invest in real‑time analytics, we’ll invest in you. 

**MVPs over grand visions** 

The most successful teams narrowed their scope aggressively: 
Picked a real problem (health alerts, chatbot security) 

* Shipped a narrow but usable loop 
* Used ClickHouse so they wouldn’t get blocked by performance or schema changes mid‑build 

For us, the big takeaway: **agentic AI + real‑time analytics is already a natural pairing** for builders. Hackathons like this just make that visible in one intense, high‑energy day.

![5.jpg](https://clickhouse.com/uploads/5_29742634de.jpg)


### **Thank you**

Huge thanks to:



* **The organizers and Datadog** for hosting a packed, high‑energy event in New York. 

* **Every hacker, engineer, and student** who spent their Saturday experimenting with agentic AI and pushing ClickHouse in creative ways. 

* Our fellow sponsors and mentors who helped shape ambitious ideas into working demos. 


We’re excited to keep showing up where builders are, especially at hackathons focused on **AI agents, live data, and real‑time decision‑making**.

If you’re organizing an AI or data‑focused hackathon and want ClickHouse involved as a sponsor, mentor, or technical partner. We’d love to hear from you.

:::global-blog-cta::: 
