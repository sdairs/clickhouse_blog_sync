---
title: "Agents can now provision ClickHouse and Postgres on ClickHouse Cloud"
date: "2026-06-10T15:49:47.293Z"
author: "Chloé Carasso dit Carson"
category: "Product"
excerpt: "One command in the Stripe CLI provisions a ClickHouse or Postgres service on ClickHouse Cloud and hands working credentials straight to your agent, with no UI or manual setup."
---

# Agents can now provision ClickHouse and Postgres on ClickHouse Cloud

ClickHouse is now available in [Stripe Projects](https://projects.dev/), the new Stripe CLI workflow that lets developers and AI agents provision real infrastructure without leaving the command line.

Starting today, one command provisions a ClickHouse or Postgres service on ClickHouse Cloud, returns working credentials to your environment, and hands off to [`clickhousectl`](https://clickhouse.com/blog/introducing-clickhousectl-official-cli-for-clickhouse-local-and-cloud), a new ClickHouse CLI built for agents, so the agent can keep building.

## Why we built this {#why-we-built-this}

Agents cannot create accounts, click through setup flows, or paste credentials into a config file. We built this integration so that spinning up a ClickHouse or Postgres service on ClickHouse Cloud is something an agent can do completely, with real credentials landing in the environment without any UI interaction.

Stripe Projects is the CLI workflow that puts it all together. Run `stripe projects init my-app`, select the services you need, and Stripe Projects provisions real resources in your own provider accounts, syncs credentials to your `.env`, and keeps everything auditable from the terminal. Credentials land in your environment without any manual steps, and the workflow is the same whether a human or an agent is running it.

This is a developer preview. We want feedback from teams building agent-assisted workflows or just trying to cut the time from new repo to running app.

## What can you provision? {#what-can-you-provision}

ClickHouse Cloud offers two services through Stripe Projects:

**ClickHouse** is the real-time analytics database. ClickHouse is known for: high-ingest, high-concurrency, billions of rows in milliseconds. If your app needs to query event streams, power user-facing analytics, or run aggregations at scale, this is the right service.

**Postgres (public beta)** is a fully managed Postgres service on ClickHouse Cloud, built on local NVMe storage for microsecond latency and up to 10x faster performance on I/O-heavy workloads. For teams that need a transactional store alongside their analytics layer, both services are provisioned through the same CLI workflow, land in the same account, and share credentials.

## How credentials flow to the agent {#how-credentials-flow-to-the-agent}

Once provisioning completes, credentials are written directly to your `.env` file in an agent-readable format. From there, the agent picks them up and continues all operations through `clickhousectl`, the ClickHouse CLI, without any manual credential handling or context switching.

> Note: clickhousectl >v0.3.0 is required.

## Try it {#try-it}

ClickHouse is in the Stripe Projects developer preview today.

<pre><code type='click-ui' language='bash'>
# Create a project
stripe projects init my-app

# Add a ClickHouse service
stripe projects add clickhouse/clickhouse

# Or add a managed Postgres service (public beta)
stripe projects add clickhouse/postgres
</code></pre>


Install the Stripe CLI, run `stripe projects init my-app`, and add whichever service fits your stack. Credentials sync to `.env` automatically. From there, `clickhousectl` takes over: set up data ingestion with ClickPipes, query your service, and keep building without leaving the terminal.

To learn more, visit [clickhouse.com/cloud](https://clickhouse.com/cloud) or the [Stripe Projects documentation](https://docs.stripe.com/projects).


---

## Get started today

Interested in seeing how ClickHouse works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-850-get-started-today-sign-up&utm_blogctaid=850)

---