---
title: "What's new in clickhousectl v0.5.0"
date: "2026-11-02T14:46:08.768Z"
author: "Al Brown"
category: "Product"
excerpt: "clickhousectl v0.5.0 takes UDFs from local to Cloud, adds ClickHouse Managed Postgres observability, standardises the command surface, and lists the API-key permissions every Cloud command needs."
---

# What's new in clickhousectl v0.5.0

[`clickhousectl`](https://github.com/ClickHouse/clickhousectl) (`chctl`) is one CLI for ClickHouse and Postgres, both on your laptop and in ClickHouse Cloud.
Locally it installs and switches ClickHouse versions, runs project-scoped ClickHouse servers and Docker-backed
Postgres, and connects clients. In Cloud it covers the whole lifecycle of ClickHouse, ClickHouse Managed Postgres,
ClickPipes, ClickStack, backups, keys and members.

[v0.4.0](https://clickhouse.com/blog/clickhousectl-v0-4-0) left beta and added horizontal autoscaling and ClickPipe schema discovery. The highlights in v0.5.0:

- **UDFs end-to-end**: scaffold, test locally, then ship to Cloud with one command.
- **ClickHouse Managed Postgres**: metrics, server logs, slow-query patterns, read-only SQL over HTTP, and
  IP allow rules.
- **A more consistent, automation-friendly CLI**: uniform selectors, `--file` inputs, global org selection,
  JSON errors everywhere. Note that some of these are **breaking**; see [the breaking changes](#breaking-changes).
- **Saved queries and Query API endpoints**: saved queries are GA, and can be exposed as HTTP endpoints.
- **BigQuery CDC ClickPipes**: continuous replication from BigQuery, on an interval or a cron schedule.
- **ClickStack** comes to the CLI: dashboards, alerts, webhooks, saved searches, sources and roles.
- **Permissions in help**: every Cloud command lists the API-key permissions it needs.
- **Far wider Cloud coverage**: service settings, scaling schedules, upgrade windows, snapshots, backup buckets,
  BYOC infrastructure, org roles, quotas, credits.

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

## User-defined functions: local to Cloud

Executable UDFs now have a complete workflow. `local udf init` scaffolds a UDF directory (a `udf.json` definition plus a
Python script, or native `amd64/`/`arm64/` binaries). `local udf deploy` installs it into a local server so you can
test it with plain SQL. When it works, `cloud udf deploy` packages the directory, creates the UDF (or a new version),
attaches it to your service and wakes the service, all in one step.

For finer control, the lower-level Cloud commands are also available (Beta): `cloud udf create`, `version create`,
`attach` / `detach` (with `--wake`) and `attachment list`.

```bash
clickhousectl local udf init my_udf
clickhousectl local udf deploy my_udf
clickhousectl local client --query "SELECT my_udf(1)"
clickhousectl cloud udf deploy my_udf --service <service-id>
```

See the [user-defined functions guide](https://github.com/ClickHouse/clickhousectl/blob/main/docs/guides/user-defined-functions.md).

## ClickHouse Managed Postgres: observability, querying and network access

You can now inspect ClickHouse Managed Postgres services from the terminal. `postgres metrics` returns service metrics as compact
series, `postgres logs` shows server logs as a table (filter by severity or body text), and `postgres slow-queries`
lists normalised query patterns sorted by total/avg/p95/p99 duration, CPU, rows, WAL and more. `get` then shows one
pattern's recent executions. `postgres prometheus` exposes the raw Prometheus endpoint for your existing scraping setup.
Agents can use the same commands to do root-cause analysis on slow Postgres.

`cloud postgres query` runs read-only SQL over HTTP using your OAuth login, with no `psql`, network path or password
needed. Also new: `postgres backup list` (with a Status column), provider shown in `postgres list`, and
validated `config` inputs. `postgres get` shows the earliest restore time. Config writes (`--set`,
`--pg-config-file`) accept 29 more Postgres settings, including autovacuum thresholds, `checkpoint_timeout`,
`wal_buffers`, `io_method` and `default_toast_compression`. Enum values are checked before anything is sent.

You can also set network access from the CLI. `postgres create` takes repeatable
`--ip-allow <IP_OR_CIDR>:<PORTS>[=<DESCRIPTION>]` rules or `--block-public-access`, and `postgres update` adds and
removes rules with `--add-ip-allow` and `--remove-ip-allow <RULE_ID>` (IPv4 only). `postgres restore` copies the
source's IP rules to the restored service, because the restore API would otherwise open it to all addresses.

```bash
clickhousectl cloud postgres slow-queries list <postgres-id> \
  --from-date 2026-10-14T00:00:00Z --to-date 2026-10-15T00:00:00Z --sort-by p95_duration
clickhousectl cloud postgres logs <postgres-id> --from-date ... --to-date ... --severity ERROR
clickhousectl cloud postgres query <postgres-id> --query "SELECT version()"
clickhousectl cloud postgres update <postgres-id> --add-ip-allow '203.0.113.0/24:5432..6432=office'
```

See the [ClickHouse Managed Postgres guide](https://github.com/ClickHouse/clickhousectl/blob/main/docs/guides/managed-postgres.md).

## A consistent command surface

0.5.0 standardises how commands take their inputs, so that once you've learnt one command you know the shape of
the rest. That matters for people, and even more for agents that generalise from one command to the next. The rules
are now:

- Finish the subcommand path, then give existing resources by **positional ID**.
- Alternatively, select a resource by exact name with **`--name`**.
- Choose the organisation with **`--org-id` or `--org-name`**, accepted anywhere after `cloud`.
- **`--new-name`** renames a resource.

Most changes keep the old spelling as a hidden alias, but a few break existing scripts.

### Breaking changes

| Change | 0.4.x | 0.5.0 |
| --- | --- | --- |
| Rename flag on updates (`service`, `postgres`, `key`, `org update`). `--name` now *selects* the target | `cloud service update <id> --name reporting` | `cloud service update <id> --new-name reporting` |
| Org commands (`org get`, `update`, `usage`, `prometheus`) now select the org like every other command, with `--org-id` / `--org-name`, not a positional ID. The org is the scope, not the resource | `cloud org get <org-id>` | `cloud org get --org-id <org-id>` (or `--org-name prod`) |
| ClickPipe schema discovery argument order (Kafka, Kinesis, object storage, Pub/Sub) | `cloud clickpipe schema-discover <service-id> kafka ...` | `cloud clickpipe schema-discover kafka <service-id> ...` |
| Native client/server arguments must follow `--`. Unknown flags were previously swallowed silently | `local client dev --some-native-flag` | `local client dev -- --some-native-flag` |
| `--wait` / `--wait-timeout` removed from `postgres promote` / `switchover` | `cloud postgres promote <id> --wait` | `cloud postgres promote <id>`, then poll `cloud postgres get <id>` |
| GCP Postgres sizes renamed to match the API, with no aliases. C4/C4A/C4D gain `-lssd-`, Z3 gains `highmem` | `--size c4-standard-4` | `--size c4-standard-lssd-4` (`z3-highlssd-8` → `z3-highmem-highlssd-8`) |
| `--encryption-key` / `--encryption-role` removed from `service create`, as the API no longer accepts them | `cloud service create ... --encryption-key <arn>` | Removed (`service get` still shows the fields) |

The old forms fail with a usage error (exit 2) and are not silently reinterpreted.

### Additive (old forms still work)

| Change | 0.4.x | 0.5.0 |
| --- | --- | --- |
| Global org selection | `--org-id` only on the leaf command | `cloud --org-name prod service list`. Works at any depth |
| Select by name everywhere (services, Postgres, keys, ClickPipes, roles, BYOC, endpoints, ClickStack); `--email` for members/invitations | `cloud service query --id <id>` / `--name` only on query | `cloud service get --name analytics`, `cloud clickpipe get <service-id> --name ingest-orders` |
| Positional local instance names | mixed `--name` / positional per command | `local postgres start app`, `local server dotenv dev` (`--name` is a hidden alias) |
| JSON document input | `--config-file` / `--settings-file` / `--file` | `--file <PATH>` (`-` for stdin where supported); old spellings are hidden aliases |
| Postgres restore/read-replica source by name | source ID only | `--source-name primary` |

## Saved queries and Query API endpoints

`cloud saved-query` creates, updates and deletes saved queries with default parameters. The operations
are now GA, so the Beta label has gone. With `cloud query-api-endpoint` you can manage Query API endpoints and expose
saved queries as HTTP endpoints, for example to serve dashboards or apps straight from ClickHouse. Fixed:
`query-api-endpoint list` and `--name` lookups failed with a decoding error as soon as an org had an endpoint.

```bash
clickhousectl cloud saved-query create <service-id> --name top_pages --database default \
  --sql-file top_pages.sql --param limit=10
```

See the [Query API reference](https://github.com/ClickHouse/clickhousectl/blob/main/docs/reference/query-api.md).

## ClickPipes

ClickPipes support grew a lot in this release. The headline addition is `clickpipe update`, a complete update command
that safely patches settings on running pipes, including the CDC pause → update → resume flow. CDC pipes gain advanced
table mappings (including table engine choice; ReplacingMergeTree is now the default for Postgres), destination
database selection, and CDC scaling.

**BigQuery CDC.** `clickpipe create bigquery` used to support snapshots only. It now takes
`--replication-mode cdc` or `cdc_only` with `--replication-method query_based` (each table names a
`queryCdcWatermarkColumn`) or `events_based` (each table names an `eventsFunction`, `appends` or `changes`). Syncs run
on `--sync-interval-seconds` or a cron schedule with `--sync-cron` (UTC unless you prefix `CRON_TZ=<zone>`). Tuning
flags cover pull parallelism, visibility delay and pull window size. Invalid combinations fail locally, before the
service-account key is read.

```bash
clickhousectl cloud clickpipe create bigquery <service-id> --name orders-cdc ... \
  --replication-mode cdc --replication-method query_based --sync-cron '*/15 * * * *' \
  --table-mapping-json '{"sourceDatasetName":"shop","sourceTable":"orders","targetTable":"orders","queryCdcWatermarkColumn":"updated_at"}'
```

The full example, with `--service-account-file` and `--staging-path`, is in the
[ClickPipe configuration reference](https://github.com/ClickHouse/clickhousectl/blob/main/docs/reference/clickpipe-configuration.md) under "Configure BigQuery CDC".

Also: MongoDB table mappings accept `structuredIngestion` (typed columns, exclusions, sorting keys and
partitioning instead of a single JSON column), and MySQL pipes accept `--mysql-type cloudsqlmysql` for Cloud SQL.

Smaller additions: Postgres TLS controls, GCP workload identity, Kinesis
Protobuf schemas (and auth inferred from access keys), Kafka AWS Glue schema registry, MongoDB initial-load
parallelism, BigQuery snapshot tuning, source tuning options, streaming table definitions, starting supported pipes
paused, and DNS targets. Validation now happens before anything is sent: port ranges, scale ranges, insert sizes and
required object-storage columns are checked up front.

```bash
clickhousectl cloud clickpipe stop <service-id> <clickpipe-id>
clickhousectl cloud clickpipe update <service-id> <clickpipe-id> --file patch.json
clickhousectl cloud clickpipe start <service-id> <clickpipe-id>
```

See the [ClickPipes guide](https://github.com/ClickHouse/clickhousectl/blob/main/docs/guides/clickpipes.md) and the [ClickPipe configuration reference](https://github.com/ClickHouse/clickhousectl/blob/main/docs/reference/clickpipe-configuration.md).

## ClickStack

New `cloud clickstack` command group for managing ClickStack (observability) resources in a Cloud service:
data sources, roles, dashboards, alerts, webhooks and saved searches. You can keep dashboards and alerts as JSON in
your repo and apply them from CI, or let an agent build a dashboard for you. `dashboard validate` checks a
definition before you create it, and `webhook validate` does the same for webhooks.

The CLI supports the latest ClickStack API contract:

- Dashboards accept all four filter kinds (query expression, static list, Prometheus label, source filter),
  stacked-line tiles, series heatmaps and `lineInterpolation`.
- Alerts can use an inline `chartConfig` (`source: inline`) instead of a tile or saved search. `channel`/`channels`
  are now optional, and the new `displayName` and `tags` fields pass through. `name` is now a Handlebars title template.
  `alert list` shows `displayName`, and `--name` matches either field.
- Role permissions are checked against their integration (ClickHouse or MongoDB), so a typo fails locally instead
  of being dropped silently.

```bash
clickhousectl cloud clickstack source list <service-id>
clickhousectl cloud clickstack dashboard validate <service-id> --file dashboard.json
clickhousectl cloud clickstack dashboard create <service-id> --file dashboard.json
clickhousectl cloud clickstack webhook validate <service-id> --file webhook.json
clickhousectl cloud clickstack webhook create <service-id> --file webhook.json
clickhousectl cloud clickstack alert create <service-id> --file alert.json
```

See the [ClickStack guide](https://github.com/ClickHouse/clickhousectl/blob/main/docs/guides/clickstack.md).

## Service configuration

Many more Cloud service settings can now be managed from the CLI:

- `service settings`: read the ClickHouse settings schema and set or get settings, with typed values.
- `service scaling-schedule`: time-based scaling schedules.
- `service upgrade-window`: control when upgrades happen.
- `service profile list`: discover the available service profiles for a region.
- `service wake`: wake an idled service explicitly.
- `service snapshot` (Beta): list snapshots and manage snapshot configuration.
- `service replica-aware-routing`.
- IP allowlist descriptions.

```bash
clickhousectl cloud service settings set <service-id> --setting 'enable_analyzer=1'
clickhousectl cloud service scaling-schedule set <service-id> --file schedule.json
```

See the [Cloud service guide](https://github.com/ClickHouse/clickhousectl/blob/main/docs/guides/cloud-service.md).

## Backups

`backup bucket` manages a service's own backup bucket (bring your own storage), and `service backup-config` manages
backup configuration, including encryption. Backup timestamps are now normalised to UTC. AWS backup
buckets take `iamRoleExternalId` in the `--file` body (required on create; on update, omit it to keep the current
value, set it to replace it, or set it to `null` to clear it).

## Organisation, governance and BYOC

New org-level commands: `org role` (custom roles), `org quota`, `org balance` (credit balances), `org prometheus`
discovery and `org notifications` (Beta). It pages through org notifications and filters by severity, type,
resource and date range. `org byoc` manages BYOC infrastructure end to end: `validate` checks that your cloud account is ready,
`create` (including bring-your-own-VPC flags) provisions it, `progress` tracks provisioning, and `get`, `update` and
`delete` cover the rest. Private endpoint config and tags are also supported.

```bash
clickhousectl cloud org byoc validate ...
clickhousectl cloud org byoc create ...
clickhousectl cloud org byoc progress ...
```

## Authentication and identity

`cloud auth whoami` shows the identity behind your active credentials, and `auth login` and `auth status` now
verify and display it. The first time you run `service query`, the CLI now binds your own API key and no longer mints
a separate query key, so it uses the roles you already have. Empty API-key credentials are rejected, and `--debug`
explains which credential source was picked and why.

```bash
clickhousectl cloud auth whoami
```

## Commands tell you which permissions they need

Every Cloud command's help now lists the API-key permissions required by the API calls it makes behind the scenes.
The list is generated from the API definitions, so it stays in step with the API. An agent can read it before running
a command and know whether its key is enough, instead of finding out from a failed call. It also lays the groundwork
for an upcoming feature that will let agents request a permission elevation when they need to run a command their key
doesn't cover.

```bash
clickhousectl cloud service create --help
...
  API key permission: control-plane:organization:create-service
  API key permission: control-plane:service:manage
```

## Built for automation and agents

- **JSON errors everywhere**: in `--json` mode (or when an agent is detected), every Cloud runtime failure, including
  auth errors and cancellations, is printed as a structured JSON error. Exit codes are stable: 1 error, 2 usage,
  3 cancelled, 4 auth required.
- **Structured output for management commands**, with documented JSON output contracts (see the [automation reference](https://github.com/ClickHouse/clickhousectl/blob/main/docs/reference/automation.md)).
- **`--all` pagination** for API keys, and selector pagination for ClickStack.
- Closed stdout pipes (`| head`) are handled quietly.
- Agent context blocks in help were standardised and checked across the whole command tree.
- Agent detection now follows the agents.md `AI_AGENT` variable first. An unrecognised value in the legacy
  `AGENT` variable no longer switches on JSON output (a known agent name or `AGENT=1` still does).
- Paged list output is consistent: UDF lists return a top-level `result` array with `nextCursor`, the same
  shape as `cloud key list`.

## Local development improvements

Local development gets a round of fixes:

- Server ports are preserved across config reloads.
- Postgres SQL files and stdin are streamed through Docker (`psql` piping works).
- The runtime `.gitignore` is restored by `init`.
- Downloads are conditional, so the latest builds are reused.
- Errors for corrupted metadata and Docker failures are clearer.
- Anonymous Postgres volumes are removed together with their containers.

`local udf` (above) is the main new local feature.

## Thanks

Thanks to [Zach Naimon](https://github.com/ArctypeZach), who co-authored the UDF work in this release, and to
[@ylw510](https://github.com/ylw510), who made failed installs show the error output from `clickhouse --version`
([#993](https://github.com/ClickHouse/clickhousectl/pull/993)).
