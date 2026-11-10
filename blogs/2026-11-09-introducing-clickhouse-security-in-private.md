---
title: "Introducing ClickHouse Security in private preview, built on RunReveal"
date: "2026-11-09T16:59:45.905Z"
author: "Evan Johnson"
category: "Product"
excerpt: "ClickHouse Security, an agentic SIEM built on RunReveal and ClickHouse Cloud, is now in private preview, with AI agents, 100+ integrations and built-in detections running on your own ClickHouse service."
---

# Introducing ClickHouse Security in private preview, built on RunReveal

Today we’re announcing ClickHouse Security is entering Private Preview. [ClickHouse Security](http://clickhouse.com/security) is an agentic SIEM built for the next decade of scale, and is the integrated offering between RunReveal and ClickHouse Cloud.

The RunReveal team has been working to rapidly integrate with ClickHouse Cloud [since joining forces in September](https://clickhouse.com/blog/clickhouse-welcomes-runreveal). Our goal is to make ClickHouse Cloud the easiest and most performant place for a company’s security data, and provide the interfaces that AI agents need to defend modern environments.

To request access to the ClickHouse Security Private Preview, [please fill out the form found here](http://clickhouse.com/security#request-access).

## Getting started with the ClickHouse Security private preview {#getting_started}

Once approved for our Private Preview, customers will log into ClickHouse Security using their ClickHouse Cloud account. You’ll see your existing ClickHouse services pre-populated in our dashboard.

Schemas, views, and all of the batteries are included to turn your ClickHouse service into a fully functioning security data platform. Setting this up requires selecting the ClickHouse service you want to deploy ClickHouse Security to, provisioning the schemas, and that’s all! You’ll be able to then connect data sources, run agents, and detect threats as described in the [RunReveal documentation](http://docs.runreveal.com/).

### How ClickHouse Security works

ClickHouse Security turns a ClickHouse Cloud service into a battery-included agentic SIEM, using the schemas and views provisioned on the service you pick during setup.

* **Put agents to work:** Agents are part of the platform, not an add-on. Using the AI capabilities within ClickHouse Security, security engineers can create agents for alert triage, detection tuning and generation, threat hunting, and more. Team members can ask follow-up questions in natural language through AI chat, without writing traditional queries. Security teams that want to go further can build their own agentic workflows with the LLM of their choice, through an MCP server, API, CLI, and Slack bot.
* **Get data in fast:** First-party integrations connect over one hundred cloud, identity, and SaaS sources and bring data in normalized. Built-in pipelines filter, route, and enrich logs before they’re stored, so there’s no separate pipeline layer to buy or manage.
* **Detection built-in, or your own:** Managed detections cover common threats from day one. Write your own as scheduled SQL or streaming Sigma rules, and manage them as code with the CLI (export, test, sync, dry run). Each finding stores the matched log, MITRE ATT&CK mapping, risk score, and the rule that fired.

<iframe width="768" height="432" src="https://www.youtube.com/embed/_qnyZ7Ytag8" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

### Why run it in ClickHouse

ClickHouse Security sits on the database built for how telemetry looks today: continuous high-volume ingest, retention measured in years, and investigation queries that need to return while an analyst is still looking at the screen. ClickHouse’s columnar storage and compression keep large volumes of logs affordable to retain, and its parallel query execution keeps searches fast as the data grows, so teams don’t have to choose between keeping the data and being able to search it.

A SIEM is usually one more silo to send data to. If you already use ClickHouse, ClickHouse Security is an extension of the platform you’re familiar with. It runs on your own ClickHouse Cloud service and uses your ClickHouse Cloud sign-in, so there’s no separate system to feed and no separate login to manage.

> “Building robotics foundation models means making sense of billions of annotations and telemetry records,” says Karan Dhabalia, Engineer at Physical Intelligence. “We started with ClickHouse for observability, then expanded into real-time analytics, Postgres, and AI development with Langfuse. This shared foundation simplifies operations and helps our researchers develop better models. With ClickHouse Security now in private preview, we’re excited to see the platform grow.”

During the preview, ClickHouse Security is provided at no charge, and you pay only for the ClickHouse Cloud compute and storage your service uses, at standard ClickHouse Cloud pricing. Participation requires accepting the [ClickHouse Security Cloud Preview Addendum](https://clickhouse.com/legal/clickHouse-security-cloud-preview-addendum). Pricing for ClickHouse Security will be set at general availability.

## What’s happening with RunReveal? {#whats_happening_with_runreveal}

RunReveal was built on ClickHouse from day one of forming the company. This means that there is no hairy migration or major bait-and-switch as we continue to support our customers with the technology stack we’ve already built. ClickHouse Security is the same RunReveal team with additional resources and a tighter integration with ClickHouse Cloud.

As part of this work, we updated RunReveal to use ClickHouse Cloud authentication, and connecting it to an existing ClickHouse service now takes just a few clicks. This is the new model for ClickHouse Security and the future deployment model for existing RunReveal SaaS customers.

The only key change in RunReveal’s offering is that our customers will not have the option of using RunReveal’s multi-tenant ClickHouse cluster in the future. Over the coming months, we plan to work with our customers to transition them to their own independent ClickHouse service along with their data. 

## One platform for security data, built to keep pace with AI {#one_platform_for_security_data}

We have an aggressive roadmap over the next few months. Here is where we’re focused:

* **More deployment regions**, so ClickHouse Security can run alongside your ClickHouse services wherever they run.
* **More capabilities**, prioritized by what customers ask for. Our team remains committed to working incredibly close to our customers to ensure we are providing the most powerful and flexible platform for their security data.
* **Agent powered security**: Our customers power their detection and response programs through agents and we’re working on making that experience even better. Tedious authoring of detections, threat hunting, and incident response are jobs for an agent and not a SOC analyst. 

We’ll share more as we get closer to general availability.

---

## Get started today

Interested in seeing how ClickHouse works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-2982-get-started-today-sign-up&utm_blogctaid=2982)

---