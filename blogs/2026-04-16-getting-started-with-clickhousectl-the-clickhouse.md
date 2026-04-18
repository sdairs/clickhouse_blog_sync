---
title: "Getting started with clickhousectl: the ClickHouse CLI for local and cloud"
date: "2026-04-16T16:58:58.042Z"
author: "Al Brown"
category: "Product"
excerpt: "A hands-on guide to clickhousectl, the ClickHouse CLI. Install it, scaffold a project, manage local servers, connect to ClickHouse Cloud, and set up CI/CD — all from your terminal."
---

# Getting started with clickhousectl: the ClickHouse CLI for local and cloud

If you work with ClickHouse regularly, you usually need two things: a clean local setup and a way to manage Cloud services from the terminal. clickhousectl gives you both in one place. It handles local version management, isolated servers, project scaffolding, and ClickHouse Cloud operations without sending you off to a pile of shell scripts.

Install it:

```shell
curl https://clickhouse.com/cli | sh
```

The installer detects your OS and architecture, drops the binary at `~/.local/bin/clickhousectl`, and creates a `chctl` alias. Check it's on your path:

```shell
chctl --version
```

## Bootstrap a project

Install a ClickHouse version and mark it active:

```shell
chctl local use stable
```

This grabs the latest stable release if you don't already have it and sets it as the active version. Binaries live in `~/.clickhouse/versions/` and are shared across every project on the machine, so you're not re-downloading ClickHouse each time. Check what you're on:

```shell
chctl local which

26.2.8.7 (stable)
```

To list what's installed locally, or see everything available upstream:

```shell
chctl local list
chctl local list --remote
```

Pin a specific release when you need to:

```shell
chctl local use 26.3
```

Now make a directory for the project and drop into it. The scaffolded layout, the named server's data directory, and the SQL files are all scoped to whichever directory you run `chctl` from, so pick a home for it up front:

```shell
mkdir events-pipeline && cd events-pipeline
```

Scaffold the layout:

```shell
chctl local init

clickhouse/
├── tables/              # CREATE TABLE statements
├── materialized_views/  # Materialized view definitions
├── queries/             # Saved analytical queries
└── seed/                # Test data (CSVs or INSERT scripts)
```

A sensible standard layout helps humans and agents alike keep track of what's going on. Keep `tables/` and `materialized_views/` as your schema source of truth, drop day-to-day queries into `queries/`, and use `seed/` for anything you need to load during development.

Write a table to `clickhouse/tables/events.sql`:

```sql
CREATE TABLE IF NOT EXISTS events
(
    timestamp DateTime,
    user_id   UInt64,
    event     LowCardinality(String),
    properties String
)
ENGINE = MergeTree()
ORDER BY (event, timestamp)
```

Start a named server and apply it:

```shell
chctl local server start --name dev
chctl local client --name dev --queries-file clickhouse/tables/events.sql
```

This gives you an isolated instance with its own data directory at `.clickhouse/servers/dev/data/`. Run as many named servers as you want; they don't share state.

Seed some rows. Write to `clickhouse/seed/events.sql`:

```sql
INSERT INTO events VALUES
    (now(), 1, 'page_view', '{"page": "/pricing"}'),
    (now(), 2, 'signup', '{"plan": "cloud"}'),
    (now(), 1, 'page_view', '{"page": "/docs"}');
```

Apply it and query:

```shell
chctl local client --name dev --queries-file clickhouse/seed/events.sql
chctl local client --name dev --query "SELECT event, count() FROM events GROUP BY event"

┌─event─────┬─count()─┐
│ page_view │       2 │
│ signup    │       1 │
└───────────┴─────────┘
```

## Manage local dev servers

Named servers get more useful once you run multiple versions side by side. Spin up a second server alongside `dev`, but on a different release:

```shell
chctl local server start --name staging --version latest
```

`--version` overrides your pinned version for this server only. `dev` keeps running on whatever `chctl local use stable` resolved to; `staging` runs on whatever `latest` resolves to right now. If that version isn't installed, `chctl` fetches it first.

List them:

```shell
chctl local server list
+---------+---------+-------+------------+-----------+----------+
| Name    | Status  | PID   | Version    | HTTP Port | TCP Port |
+---------+---------+-------+------------+-----------+----------+
| dev     | running | 99493 | 26.2.8.7   | 8126      | 9003     |
| staging | running | 98060 | 26.4.1.997 | 8128      | 9007     |
+---------+---------+-------+------------+-----------+----------+

2 servers, 2 running
```

This is the pattern for upgrade testing: keep `dev` on the version you run in production, point `staging` at the one you're evaluating, and apply the same schema files to both. If something breaks, you find out before the upgrade.

Ports auto-assign when the defaults are taken, so you don't have to manage them yourself.

Apply the same schema files to the new server:

```shell
chctl local client --name staging --queries-file clickhouse/tables/events.sql
```

And run any saved query against whichever server you pick:

```shell
chctl local client --name staging --queries-file clickhouse/queries/daily_events.sql
```

Stop a server when you're done:

```shell
chctl local server stop staging
```

Or delete it and its data directory entirely:

```shell
chctl local server remove staging
```

## Connect to ClickHouse Cloud

Every command you've seen so far has a Cloud equivalent.

Cloud auth is split in two by design. Browser-based OAuth gets you read-only access. Anything that mutates state (creating services, scaling them, applying schema changes) requires explicit API key authentication.

The split exists because `chctl` is a tool an agent can drive. Getting an API key requires a deliberate step in the Cloud console, which forces the question: do I actually want to give this CLI (and by extension, whatever's running it) write access to my Cloud account?

Authenticate for read-only access:

```shell
chctl cloud auth login
```

OAuth opens in your browser; the token is cached locally after. If you belong to more than one Cloud organisation, list them and pick one:

```shell
chctl cloud org list
+-------------------+--------------+
| Name              | ID           |
+-------------------+--------------+
| CLICKHOUSECTL_CLI | 5fae43a3-... |
+-------------------+--------------+
```

With a single org, `chctl` auto-selects it and you can skip this step. With multiple, pass `--org-id` to scope commands:

```shell
chctl cloud service list --org-id 5fae43a3-xxxx-xxxx-xxxx-6e139718b9a3

+------+----------+---------+----------+-----------+--------------+
| Name | ID       | State   | Provider | Region    | Endpoint     |
+------+----------+---------+----------+-----------+--------------+
| blog | c04e...  | running | aws      | us-east-1 | xyz...cloud  |
+------+----------+---------+----------+-----------+--------------+
```

For anything that writes, generate an API key in the [Cloud console](https://clickhouse.cloud) and authenticate with it:

```shell
chctl cloud auth login --api-key <key> --api-secret <secret>
```

Or set `CLICKHOUSE_API_KEY` and `CLICKHOUSE_API_SECRET` as environment variables and `chctl` will pick them up automatically. API keys are scoped to a single org at creation time, so `--org-id` isn't needed once you're authenticated this way. Stay tuned for improvements to the auth flow.

With write access, create a service:

```shell
chctl cloud service create --provider aws --region us-east-1 --name getting_started

Service created successfully!

Service: getting_started
  ID: c04e0b96-xxxx-xxxx-xxxx-a91717ae4906
  State: provisioning
  Provider: aws
  Region: us-east-1
  Replicas: 3
  Min Memory/Replica: 16 GB
  Max Memory/Replica: 120 GB
  Host: xyz.us-east-1.aws.clickhouse.cloud
  Port: 9440

Credentials (save these, password shown only once):
  Username: default
  Password: xyz
```

Save the password somewhere you can retrieve it. It's not shown again.

Scaling works the same way. Pass only what you want to change. No need to restate every parameter:

```shell
chctl cloud service scale c04e0b96-xxxx-xxxx-xxxx-a91717ae4906 --num-replicas 4

Service getting_started scaling updated
  Replicas: 4
```

Apply the schema files you developed locally:

```shell
chctl cloud service client --name getting_started --queries-file clickhouse/tables/events.sql --user default --password xyz
```

## Develop with an AI agent

`chctl` ships agent skills for coding assistants. To install the Claude Code set:

```shell
chctl skills --agent claude
```

Three skills land in `.claude/skills/`:

- [`clickhouse-best-practices`](https://github.com/ClickHouse/agent-skills/tree/main/skills/clickhouse-best-practices): 28 rules covering schema design, query optimisation, and inserts. Keeps the agent honest about primary keys, data types, JOINs, and partitioning.
- [`clickhousectl-local-dev`](https://github.com/ClickHouse/agent-skills/tree/main/skills/clickhousectl-local-dev): how to manage versions, scaffold projects, start servers, write schemas, and seed data with `chctl`.
- [`clickhousectl-cloud-deploy`](https://github.com/ClickHouse/agent-skills/tree/main/skills/clickhousectl-cloud-deploy): Cloud authentication, service creation, schema migration from local, and application connection config.

With these loaded, a prompt like:

> Set up a ClickHouse project for tracking web analytics events. I want to store page views, sessions, and conversions.

gets the agent to pick up `clickhousectl-local-dev`, where it will do something like:
- install a ClickHouse version
- scaffold the project
- start a dev server
- write out files like `clickhouse/tables/page_views.sql`, `sessions.sql`, and `conversions.sql`
- seed data
- run verification

Follow up with:

> Push this to ClickHouse Cloud. Create a service in AWS us-east-1.

and it switches to `clickhousectl-cloud-deploy`: `cloud auth login`, `cloud service create`, then `cloud service client --queries-file` against the same SQL files it just wrote locally. The local project is the source of truth. Cloud is just another target.

## Use clickhousectl in CI/CD

`chctl` is a static binary with JSON output and env-var auth, so it drops into pipelines without a lot of wrapper scripting.

Here's a GitHub Actions workflow that spins up ClickHouse, applies your schema, and runs test queries on every push:

```yaml
name: Schema validation
on: [push]

env:
  CLICKHOUSE_VERSION: "26.3"

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install clickhousectl
        run: curl https://clickhouse.com/cli | sh

      - name: Install ClickHouse
        run: chctl local install ${{ env.CLICKHOUSE_VERSION }}

      - name: Start server
        run: chctl local server start --name ci

      - name: Apply schema
        run: |
          for f in clickhouse/tables/*.sql; do
            chctl local client --name ci --queries-file "$f"
          done

      - name: Run test queries
        run: |
          for f in clickhouse/queries/test_*.sql; do
            chctl local client --name ci --queries-file "$f"
          done

      - name: Stop server
        run: chctl local server stop ci
```

Pin `CLICKHOUSE_VERSION` to match production. Upgrade it in one place and CI validates your whole schema against the new release on the next push, which is most of the confidence you need before an upgrade.

For Cloud writes from CI, set `CLICKHOUSE_API_KEY` and `CLICKHOUSE_API_SECRET` as secrets in your workflow and `chctl` picks them up automatically. Or pass them explicitly:

```shell
chctl cloud auth login --api-key $CLICKHOUSE_API_KEY --api-secret $CLICKHOUSE_API_SECRET
```

`--json` gives you machine-readable output for anything scripted downstream:

```shell
chctl cloud service list --json | jq '.[0].id'
```

## What's next

clickhousectl is open source at [github.com/ClickHouse/clickhousectl](https://github.com/ClickHouse/clickhousectl). For the design thinking behind it, see [Introducing clickhousectl](/blog/introducing-clickhousectl).

If you don't have a ClickHouse Cloud account yet, [sign up](https://clickhouse.cloud) and run the last two sections against a real service.