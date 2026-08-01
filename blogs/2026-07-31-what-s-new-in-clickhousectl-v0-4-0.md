---
title: "What's new in clickhousectl v0.4.0"
date: "2026-07-31T11:44:09.031Z"
author: "Al Brown"
category: "Product"
excerpt: "clickhousectl v0.4.0 adds horizontal autoscaling for Cloud services, ClickPipe schema discovery, finer control over ClickPipe ingestion, and opt-out anonymous usage telemetry."
---

# What's new in clickhousectl v0.4.0

[`clickhousectl`](https://github.com/ClickHouse/clickhousectl) is the CLI for ClickHouse, local and cloud, built to help both humans and AI agents develop with ClickHouse.

[v0.3.0](https://clickhouse.com/blog/clickhousectl-v0-3-0) brought agent-aware defaults, OAuth querying for Cloud, and custom local server configs. v0.4.0 adds horizontal autoscaling for Cloud services, ClickPipe schema discovery, finer control over ClickPipe ingestion, and opt-out anonymous usage telemetry.

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

## Horizontal autoscaling for Cloud services

ClickHouse Cloud services have two autoscaling modes: vertical (a fixed replica count with variable memory per replica) and horizontal (fixed memory per replica with a variable replica count). v0.4.0 exposes horizontal autoscaling on `service create` and `service scale`:

```bash
clickhousectl cloud service create --name my-service \
  --min-replicas 2 --max-replicas 8 --autoscaling-mode horizontal

clickhousectl cloud service scale <service-id> \
  --min-replicas 2 --max-replicas 8 --autoscaling-mode horizontal
```

The horizontal flags are mutually exclusive with the vertical ones (`--num-replicas`, `--min-replica-memory-gb`/`--max-replica-memory-gb` as a variable range), and the CLI rejects `--min-replicas` without `--max-replicas` before making any network call. Horizontal autoscaling requires the org-level feature to be enabled.

## ClickPipe schema discovery (beta)

`clickpipe schema-discover` probes a Kafka or Kinesis source and returns the inferred fields and types without creating a pipe. Use it to preview the `--column` definitions before you create the pipe for real. It takes the same source connection flags as the corresponding `create` subcommand, minus the destination options:

```bash
clickhousectl cloud clickpipe schema-discover <service-id> kafka \
  --brokers 'broker:9092' --topics events \
  --format JSONEachRow \
  --auth SCRAM-SHA-256 --username user --password pass
```

Note that `schema-discover` requires an API key and does not support a read-only OAuth login.

## Finer control over ClickPipe ingestion

Object storage pipes with continuous ingestion get two new controls: `--skip-initial-load` skips the initial snapshot and only ingests new objects, and `--start-after` resumes ingestion after a specific object key:

```bash
clickhousectl cloud clickpipe create object-storage <service-id> \
  --name my-s3-continuous-pipe \
  --source-url 'https://bucket.s3.us-east-1.amazonaws.com/data/**' \
  --format JSONEachRow \
  --continuous \
  --queue-url 'https://sqs.us-east-1.amazonaws.com/123/my-queue' \
  --start-after obj-key-001 \
  --database default --table events \
  --column "event_id:Int64" --column "name:String"
```

`--skip-initial-load` only applies when `--queue-url` is set, and it's mutually exclusive with `--start-after`.

MySQL CDC pipes can now set the replication server ID with `--server-id`, useful when multiple pipes read from the same MySQL instance or to avoid colliding with existing replicas:

```bash
clickhousectl cloud clickpipe create mysql <service-id> \
  --name my-mysql-pipe \
  --host mysql.example.com \
  --username root --password pass \
  --table-mapping "mydb.users:mydb_users" \
  --server-id 4242
```

## Partial updates for Postgres configs

`cloud postgres config patch` now applies true partial updates. Pass only the settings you want to change and everything else in the config keeps its current value:

```bash
clickhousectl cloud postgres config patch <pg-id> --set max_connections=500
```

## Global OAuth tokens

OAuth tokens from `cloud auth login` now live globally at `~/.clickhouse/tokens.json`, alongside your versions and configs. Existing project-local token files are migrated automatically on first use. OAuth remains **read-only**.

API key credentials (`credentials.json`) stay project-local. Use API keys for destructive permissions on a per-org / per-project level.

## Safer local server lifecycle

`local server stop <name>` is now idempotent, matching `docker stop` and `systemctl stop`. Stopping a server that exists but isn't running succeeds with exit code 0 instead of erroring. Unknown names still fail, so typos surface. `--json` output gains an `already_stopped` field so scripts can tell a real stop from a no-op.

`local remove <version>` now refuses to delete a version that a running server is using. Previously it deleted the binary out from under the server and reported success. It fails with the server names listed, and `--force` stops them first:

```bash
clickhousectl local remove 26.5
# Error: Version 26.5 is in use by running server(s): default.
# Stop them first, or pass --force.

clickhousectl local remove 26.5 --force
# Stopped server 'default'
# Removed 26.5
```

`--config` is now the primary flag for `local server start` (`--config-file` still works as a hidden alias), and `stop-all` flushes its progress output immediately, so it no longer looks frozen during the graceful-kill wait.

## Anonymous usage telemetry

v0.4.0 adds anonymous usage telemetry to help us understand which commands matter. Each event contains: the command path, the *names* of flags passed (never values, never positional arguments), the exit code, the CLI version, OS and architecture, whether it ran in CI, and whether it ran under a detected coding agent. There is **no install ID and no fingerprinting**.

The first run of `clickhousectl` prints a one-time telemetry notice and sends no telemetry, giving you the opportunity to opt-out before anything is sent. Opting out works any of these ways:

```bash
# Persistently, per machine
clickhousectl telemetry disable

# Check the current state
clickhousectl telemetry status

# Per environment/shell (https://consoledonottrack.com)
export DO_NOT_TRACK=1
```

To see exactly what would be sent without sending it, set `CHCTL_TELEMETRY_DEBUG=1`. You can compile telemetry out entirely with `cargo build --no-default-features`. Full details are in the [telemetry docs](https://clickhouse.com/docs/interfaces/cli#telemetry).

## Running server in one command

On a fresh install you can now start a server without setting a default or specifying a version and it will automatically install the latest master build of ClickHouse. 

```bash
clickhousectl local server start
```

`clickhousectl` also now records the etag of an installed master build. If the build hasn't moved, the installed binary is reused on successive installs:

```bash
clickhousectl local install latest
# first run: downloads master
clickhousectl local install latest
# latest is up to date (master build unchanged); using 26.7.1.1
```

## Better update visibility

`clickhousectl` looks for an available update when you run a command, caches the result, and does not look again for 24 hours. The "update available" message is now more present on successive commands to encourage more frequent updating. Running `clickhousectl update` updates the binary, and clears the cache.