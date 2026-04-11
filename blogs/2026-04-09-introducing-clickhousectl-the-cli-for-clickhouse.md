---
title: "Introducing clickhousectl: the CLI for ClickHouse local and cloud (beta)"
date: "2026-04-09T17:14:34.583Z"
author: "Al Brown"
category: "Product"
excerpt: "clickhousectl is the official CLI for ClickHouse. It manages local installations, runs local servers, and operates ClickHouse Cloud. It's designed to work for humans and AI agents alike."
---

# Introducing clickhousectl: the CLI for ClickHouse local and cloud (beta)

`clickhousectl` is the official CLI for ClickHouse. It manages local installations, runs local servers, and operates ClickHouse Cloud. It's designed to work for humans and AI agents alike. It's in beta starting today.

```shell
curl https://clickhouse.com/cli | sh
```

> **Beta:** clickhousectl is currently in beta. Features and behavior may change.

## Why a CLI, and why now

Agentic development is the biggest shift in how software gets built in decades, and is fundamentally changing how platforms like ClickHouse will be used. High quality, powerful infrastructure matters more than ever, but it needs to adapt to a new way of working: agents interacting on behalf of the user.

Agentic Experience is now an integral part of Developer Experience.

ClickHouse is open source, it's a single binary, and it runs great on a laptop. The local developer experience has long been one of ClickHouse's many strengths. But the experience was designed for humans. There’s more we can do to help LLMs develop with ClickHouse.

Whether an agent is building a local prototype or deploying to production on ClickHouse Cloud, `clickhousectl` gives it a streamlined, predictable interface that supports agentic development.

## Local development

### Version management

`clickhousectl` works as a version manager for ClickHouse, inspired by tools like `uv` and `pnpm`. The CLI helps to discover and download available ClickHouse versions. Installed binaries are stored in a global repository at `~/.clickhouse/versions/`, so they can be reused across projects without duplicating storage.

```shell
# See what's available
clickhousectl local list --remote

# Install the latest stable release
clickhousectl local install stable

# Set the active version (installs it if needed)
clickhousectl local use stable
```

### Project scaffolding

`clickhousectl` can scaffold a standard project structure for your ClickHouse SQL files. This is optional (use your own structure if you prefer), but for agents, having a consistent convention means less ambiguity when writing and organizing SQL.

```shell
clickhousectl local init
```

This creates:

```
clickhouse/
├── tables/                 # CREATE TABLE statements
├── materialized_views/     # Materialized view definitions
├── queries/                # Saved queries
└── seed/                   # Seed data and INSERT statements
```

### Running local servers

`clickhousectl` can create, manage and query local ClickHouse server instances. Each server gets its own isolated, persistent data directory, so you can run multiple servers side by side for different projects. If default ports are already in use, free ports are detected and assigned automatically.

```shell
# Start a server with the system default version (configured by `clickhousectl local use`)
clickhousectl local server start --name dev

# Connect and run a query
clickhousectl local client --name dev --query "CREATE DATABASE product"

# Run SQL from a file
clickhousectl local client --name dev --queries-file clickhouse/tables/events.sql

# Start a second server with a specific version
clickhousectl local server start --name dev-new --version 26.3
```

## ClickHouse Cloud

When it's time to go to production, the same CLI that managed your local development now manages your cloud infrastructure. The cloud commands cover organizations, services, backups, API keys, team members, invitations, and activity logs. Every command supports `--json` output for easy parsing by agents and scripts.

```shell
# Create with specific infrastructure
clickhousectl cloud service create --name my-service \
  --provider aws \
  --region us-east-1 \
  --min-replica-memory-gb 8 \
  --max-replica-memory-gb 32 \
  --num-replicas 2

# List services
clickhousectl cloud service list

# Scale a running service
clickhousectl cloud service scale <service-id> \
  --min-replica-memory-gb 24 \
  --max-replica-memory-gb 48 \
  --num-replicas 3
```

## Destructive operations and permissions
clickhousectl supports destructive operations — removing servers, dropping data, deleting Cloud services — as you'd expect from a CLI.

Using the CLI with AI agents means those agents inherit the ability to perform destructive operations. We're still investigating what good looks like for agent guardrails here, so we'd encourage you to be cautious when pairing agents with clickhousectl around production resources.

For ClickHouse Cloud, clickhousectl supports two authentication methods: OAuth and API keys. OAuth uses a device flow that opens your browser. Credentials obtained through OAuth are read-only, meaning you can list services, run queries, and inspect resources, but you cannot perform destructive operations. To create, scale, delete, or otherwise modify Cloud resources, you must authenticate with an API key.

API keys are created at the organization level, so an agent authenticated with a key is scoped to that organization and can't escape to another. You're responsible for creating the key and selecting its permissions — read-write across all services, read-only on some and read-write on others, or whatever granularity fits your setup.

## Agent skills

`clickhousectl` can also install the official [ClickHouse Agent Skills](https://github.com/ClickHouse/agent-skills) directly into your coding agents. In addition to the existing best practices skill, we’ve added 2 new skills that help your agent work with ClickHouse locally and in the cloud using the CLI.

```shell
# Interactive: choose your agents
clickhousectl skills

# Non-interactive: install into all detected agents automatically
clickhousectl skills --detected-only
```

## Get started

`clickhousectl` is in beta for macOS and Linux.

```shell
curl https://clickhouse.com/cli | sh
```

Tip: A `chctl` alias is created automatically for convenience.

We'd love feedback. If you hit issues or have ideas for what the CLI should do next, [let us know on GitHub](https://github.com/ClickHouse/clickhousectl).