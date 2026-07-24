---
title: "What's new in clickhousectl v0.3.0"
date: "2026-07-23T17:10:28.201Z"
author: "Al Brown"
category: "Product"
excerpt: "clickhousectl v0.3.0 brings a raft of improvements for the agentic experience, more ways to install, OAuth support for Query Endpoints, and custom configs."
---

# What's new in clickhousectl v0.3.0

[`clickhousectl`](https://github.com/ClickHouse/clickhousectl) is the CLI for ClickHouse, local and cloud, built to help both humans and AI agents develop with ClickHouse.

[v0.2.0](https://clickhouse.com/blog/clickhousectl-v0-2-0-postgres-clickpipes-more) brought managed Postgres, ClickPipes for eight data sources, and SQL-over-HTTP. v0.3.0 brings a raft of improvements for the agentic experience, more ways to install, OAuth support for Query Endpoints, and custom configs.

If you already have it installed, update in place:

```bash
clickhousectl update
```

If not, install it using your favorite method below:

```bash
curl https://clickhouse.com/cli | sh
pip install clickhousectl
uv tool install clickhousectl
npm i -g clickhousectl
cargo install clickhousectl
```

## A global `clickhouse` on your PATH

When you select a default ClickHouse version with `clickhousectl local use latest`, this now puts ClickHouse on your path at `~/.local/bin/clickhouse`. It's similar to doing `./clickhouse install` with the binary itself, but allows you to manage the version globally with `clickhousectl`. This means you can shell directly to the `clickhouse` binary to use its myriad of subcommands (`local`, `benchmark`, `format`, etc,.)

## Improving the agent experience

### Structured output by default for agents

In v0.3.0, `clickhousectl` can detect when it's running inside various coding agents, and optimise its behavior automatically. For example, it will now default to JSON output on stdout when running inside an agent.

This detection depends on agents self-declaring via non-sensitive environment variables (`AGENT`, `AI_AGENT` and some agent-specific variables that have not standardised yet).

### Meaningful error codes

Alongside this, exit codes now follow [`gh`](https://cli.github.com/) conventions, so agents and scripts can branch on why a command failed.

| Code | Meaning                                                      |
| ---- | ------------------------------------------------------------ |
| `0`  | Success                                                      |
| `1`  | Error (anything not classified below)                       |
| `2`  | Cancelled (user aborted)                                    |
| `4`  | Auth required (no credentials, 401/403, OAuth-only writes)  |

## `.env` support for Cloud credentials

`clickhousectl` now reads a `.env` file in your working directory for `CLICKHOUSE_` environment variables. Add your Cloud API credentials in there and any `cloud` command will pick them up:

```env
CLICKHOUSE_CLOUD_API_KEY=your-key
CLICKHOUSE_CLOUD_API_SECRET=your-secret
```

## Query ClickHouse Cloud services with OAuth

`cloud service query` runs SQL against a Cloud service over HTTP. Previously, it only supported using API keys for auth and required provisioning a Query Endpoint. v0.3.0 adds support for querying services with OAuth. When using OAuth, you do not need to first provision a Query Endpoint.

```bash
clickhousectl cloud auth login
clickhousectl cloud service query --name my-service --query "SELECT 1"
```

Querying an idled service wakes it automatically. A stopped service is never woken and fails with a hint to run `clickhousectl cloud service start`.

## Custom config files for local servers

Local servers start with sensible defaults, but sometimes you need to flip a setting. v0.3.0 lets you drop a config into `~/.clickhouse/configs/` and apply it by name:

```bash
mkdir -p ~/.clickhouse/configs
cat > ~/.clickhouse/configs/analytics.xml <<'EOF'
<clickhouse>
    <query_log>
        <database>system</database>
        <table>query_log</table>
    </query_log>
</clickhouse>
EOF

# See which configs are available
clickhousectl local server configs

# Start a server with one applied
clickhousectl local server start --config-file analytics
```

The named file is overlaid on top of ClickHouse's built-in defaults, so it only needs to contain the settings you want to change, no need to reproduce a full config. Files can be `.xml`, `.yaml`, or `.yml`, and you can reference them by name with or without the extension.

## More install options

`clickhousectl` already ships via the install script, `cargo binstall`, npm, and crates.io. v0.3.0 adds the Python packaging ecosystem:

```bash
pip install clickhousectl
# or
pipx install clickhousectl
# or
uv tool install clickhousectl
```

## Postgres in `local init`

`local init` scaffolds a standard folder structure for your ClickHouse project files. With managed and local Postgres now part of `clickhousectl`, `init` also lays down a `postgres/` tree alongside the `clickhouse/` one:

```bash
clickhousectl local init
```

```
clickhouse/
├── tables/
├── materialized_views/
├── queries/
└── seed/
postgres/
├── tables/
├── views/
├── functions/
├── queries/
└── seed/
```

## Faster, offline-friendly version resolution

When you ask for a version spec like `stable` or `26.5`, `clickhousectl` now checks your already-installed versions *before* reaching out to the network. If you've got a match locally, commands like `clickhousectl local use 26.5` resolve instantly and work offline, only falling back to a remote lookup when there's nothing suitable installed.

## Deprecated fields removed

Deprecated API fields are now hidden from CLI output to prevent confusing agents.
