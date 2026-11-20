---
title: "What's new in clickhousectl v0.6.0"
date: "2026-11-19T19:41:35.286Z"
author: "Al Brown"
category: "Product"
excerpt: "clickhousectl v0.6.0 finds projects the way Git does, connects to Cloud without a password, adds search, shell completions and feedback, and verifies every install."
---

# What's new in clickhousectl v0.6.0

[`clickhousectl`](https://github.com/ClickHouse/clickhousectl) (`chctl`) is one CLI for ClickHouse and Postgres, both on your laptop and in ClickHouse Cloud. Locally it installs and switches ClickHouse versions, runs project-scoped ClickHouse servers and Docker-backed Postgres, and connects clients. In Cloud it covers the whole lifecycle of ClickHouse, ClickHouse Managed Postgres, ClickPipes, ClickStack, backups, keys and members.

[v0.5.0](https://clickhouse.com/blog/clickhousectl-v0-5-0) took UDFs from local to Cloud, added ClickHouse Managed Postgres observability and standardised the command surface. The highlights in v0.6.0:

- **Projects that work like Git**: run commands from any subdirectory of a project, pin the project root with an environment variable, and check server config into the repo.
- **Cloud connections without a password**: `cloud clickhouse client` signs you in through the browser, and `create --dotenv` writes the one-time password to `.env` and keeps it out of the terminal.
- **`search`, shell completions and `feedback`**: find a command or flag by keyword, complete it with Tab, and tell us what the CLI couldn't do.
- **ClickHouse Managed Postgres**: the service is now GA, and the CLI adds Postgres 19, AWS PrivateLink endpoints, standby counts and deletion protection.
- **ClickPipes from discovery output**: `--columns-from` turns `schema-discover` output into a pipe's destination columns.
- **Verified installs**: the install script, `update`, and npm, check every download against the release's checksums. Install no longer relies on the GitHub API.

A few of these change existing behaviour, and OAuth logins saved by 0.5.x need one fresh login. See [the upgrade notes](#upgrade-notes).

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

## Projects that work like Git

In 0.5.x, project-scoped commands used the exact current directory. Start a server in the project root, `cd` into `src/`, and the CLI no longer saw it. In 0.6.0 a directory containing `.clickhouse/` is a project root, the way a directory containing `.git/` is for Git.

Run `clickhousectl local init` once in your project directory. Local servers, Postgres instances, saved API keys, UDF sources and the `.env` fallback then resolve from that directory or any subdirectory below it.

```bash
clickhousectl local init
clickhousectl local clickhouse start dev
cd src/app
clickhousectl local client dev --query "SELECT version()"
```

The nearest `.clickhouse/` wins, so a project nested inside another is its own project. The walk stops at your home directory, so the global `~/.clickhouse/` is never a project for the directories beneath it. `.clickhouse/` is git-ignored, so run `local init` once after cloning a repository. Starting a server without `local init` still works.

### Name the project root explicitly

Scripts, CI jobs and monorepos often need one project root wherever a command runs. Set `CLICKHOUSECTL_PROJECT_DIR` and discovery is skipped:

```bash
export CLICKHOUSECTL_PROJECT_DIR=~/code/app
clickhousectl local init               # initializes ~/code/app, not the current directory
clickhousectl local clickhouse start   # state in ~/code/app/.clickhouse/
```

### Server config you can check in

Named configs used to apply only with `--config`, and only from your home directory. Nothing applied to every start, and a team couldn't share a config through the repo. Every `local clickhouse start` now merges two `config.d` directories before the `--config` file:

| Location | Applies to | When |
| --- | --- | --- |
| `~/.clickhouse/config.d/` | every server on this machine | every start |
| `clickhouse/config.d/` in the project root | every server in this project | every start |
| `~/.clickhouse/configs/` | the server you name it for | only with `--config NAME` |

Later layers win, and the data path and ports the CLI manages always come last. `local init` scaffolds `clickhouse/config.d/`, and `local clickhouse configs` lists what will apply.

```bash
cat > clickhouse/config.d/logging.xml <<'XML'
<clickhouse>
    <logger><level>debug</level></logger>
</clickhouse>
XML
clickhousectl local clickhouse start dev
```

See the [local development guide](https://github.com/ClickHouse/clickhousectl/blob/main/docs/guides/local-development.md).

## Connect to Cloud without handling a password

The Cloud API returns the `default` user's password once, at creation. Two additions mean you rarely need to see it.

### An interactive client, signed in through the browser

`cloud clickhouse client` opens `clickhouse client` on a Cloud service over the native TLS protocol. The client signs you in through a browser as your Cloud user, so no service password is involved. It needs an installed ClickHouse 25.12 or newer, and arguments after `--` go to `clickhouse client` unchanged.

```bash
clickhousectl local install latest
clickhousectl cloud clickhouse client <service-id>
clickhousectl cloud clickhouse client --name analytics -q "SELECT version()" -- --format CSV
```

The browser step needs a person, so keep using `cloud clickhouse query` in CI and agents.

### Connection settings written to `.env`

`cloud clickhouse create --dotenv` writes the new service's connection settings and its one-time password to `.env` (or the file you name). The password then goes only to the file. It is left out of both the human and the JSON output, so it never reaches an agent's context or a transcript.

```bash
clickhousectl cloud clickhouse create --name analytics \
  --ip-allow 203.0.113.10/32 --dotenv .env.local
```

The target file is checked before the service is created. If the write fails after creation, the command prints the password as usual and exits 1, so the credential is never lost.

For an existing service, `cloud clickhouse dotenv` writes the same settings without a password. It is a read, so it works with an OAuth login:

```bash
clickhousectl cloud clickhouse dotenv <service-id> --local
```

Both write `CLICKHOUSE_HOST`, `CLICKHOUSE_PORT`, `CLICKHOUSE_HTTP_PORT`, `CLICKHOUSE_USER` and `CLICKHOUSE_SECURE=true`. An existing file is edited in place and only those keys are replaced, so a password written at creation survives a later `dotenv`.

See the [Cloud service guide](https://github.com/ClickHouse/clickhousectl/blob/main/docs/guides/cloud-service.md).

## Find commands with `search`

Agents learn the CLI by walking `--help`. That breaks down when the capability they want is a flag and not a command. An "IP access list", for example, is `--ip-allow`. The new top-level `search` ranks commands by their path, flags, descriptions and agent context, and shows up to three matching flags for each. A small synonym table maps console words to the CLI's words.

```bash
clickhousectl search ip access list
cloud clickhouse create  Create a service
    --ip-allow      Allowed IP/CIDR, optionally IP_OR_CIDR=DESCRIPTION (repeatable)
cloud clickhouse update  Update service configuration
    --add-ip-allow     IP/CIDR to add, optionally IP_OR_CIDR=DESCRIPTION (repeatable)
    --remove-ip-allow  IP or CIDR to remove from the service allow list (repeatable)
cloud postgres create  Create a Postgres service
    --ip-allow  Allowed IPv4 address or CIDR and ports (repeatable)
...
```

`--limit` sets how many commands come back (default 5) and `--json` returns a `results` array. A search that matches nothing exits 0 with an empty array. It runs offline and touches no state.

## Shell completions

The command tree is deep, so 0.6.0 adds Tab completion for bash, zsh and fish. One line in your shell startup file registers both `clickhousectl` and `chctl`:

```bash
eval "$(clickhousectl completions bash)"   # ~/.bashrc
eval "$(clickhousectl completions zsh)"    # ~/.zshrc, after compinit
clickhousectl completions fish | source    # ~/.config/fish/config.fish
```

Completion covers commands, flags, local server and Postgres instance names, and installed versions. It runs the installed CLI on each Tab press, so it stays current after `update`. It works offline and records no telemetry.

## Tell us what the CLI couldn't do

Telemetry shows which commands ran, not what someone was trying to do. `clickhousectl feedback` sends a short free-text message to the team, and the agent context in help invites coding agents to use it when the CLI lacked a capability or its help misled them.

```bash
clickhousectl feedback "postgres client should accept a database name"
```

A message is at most 500 characters. It is sent with the CLI version, OS, architecture, whether a coding agent was detected, and the IDs of the Cloud organisations your active credentials belong to. It never includes your name, email, keys or organisation names. Feedback is an explicit action, so `telemetry disable` and `DO_NOT_TRACK` don't block it. The [feedback reference](https://github.com/ClickHouse/clickhousectl/blob/main/docs/reference/feedback.md) lists everything that is sent.

## ClickHouse Managed Postgres

The Postgres operations have graduated from Beta in the Cloud API, so the Beta label has gone from `cloud postgres`. The release also adds four things you can set from the terminal.

**Postgres 19.** `postgres create --pg-version 19` is accepted, for organisations that have Postgres 19 enabled.

**Private endpoints over AWS PrivateLink (Beta).** The new `cloud postgres private-endpoint` group creates an endpoint service for an AWS Postgres service, approves the VPC endpoints that may connect, and manages the extra regions allowed to reach it. The API replaces each list it is sent in full, so `update` reads the endpoint, merges your change and sends only the lists that changed. Approving one VPC endpoint never revokes another.

**Standby count.** `--standby-count 0|1|2` on `create` and `update` sets the number of hot standbys. `none` takes 0, `async` takes 1 and `sync` takes 1 or 2. A count the given `--ha-type` doesn't take fails as a usage error before any request. `get` and `list` show the count.

**Deletion protection.** `postgres update --deletion-protection true` makes the API reject `delete` for that service until you turn it off. It applies to organisations with deletion protection enabled, and `get` and `list` show the setting.

```bash
clickhousectl cloud postgres create --name app-db --region us-east-1 --size <size> \
  --pg-version 19 --ha-type sync --standby-count 2
clickhousectl cloud postgres private-endpoint create <postgres-id>
clickhousectl cloud postgres private-endpoint update <postgres-id> \
  --add-vpc-endpoint 'vpce-0123456789abcdef0=Production VPC'
clickhousectl cloud postgres update <postgres-id> --deletion-protection true
```

Smaller changes:

- `logs`, `metrics`, `slow-queries list`, `slow-queries get` and `backup list` take `--name <postgres-name>` in place of the service ID.
- `slow-queries list` shows each pattern's database, user, operation and app, which are the keys `slow-queries get` needs.
- `logs --severity` is checked against the supported levels before the request.
- `config patch` and `config replace` read the document from stdin with `--file -`.
- New GCP local-SSD sizes are accepted by `--size`, and its help names a small size per provider.
- Help for `switchover` now describes what it does. It also works on a service without HA, by moving the primary onto a newly provisioned server.

See the [ClickHouse Managed Postgres guide](https://github.com/ClickHouse/clickhousectl/blob/main/docs/guides/managed-postgres.md).

## ClickHouse service configuration

**Deletion protection.** Turn it on with `clickhouse create --deletion-protection`, or change it later with `clickhouse update --deletion-protection true|false`. `clickhouse delete` refuses a protected service with the error code `deletion_protected`, and the error's `command` field holds the `update` command that turns protection off. With `--force`, the service is checked before it is stopped, so a protected service is never stopped either.

```bash
clickhousectl cloud clickhouse create --name prod --deletion-protection
clickhousectl cloud clickhouse update <service-id> --deletion-protection false
clickhousectl cloud clickhouse delete <service-id>
```

**JWT authentication providers (Beta).** `cloud clickhouse jwt-provider` lets users sign in to a service with a JWT from your identity provider, on the Enterprise tier. A token holder receives the ClickHouse roles listed in the token's roles claim. `update` replaces the whole configuration, so pass `--roles-claim` again to keep it.

```bash
clickhousectl cloud clickhouse jwt-provider create <service-id> corp-sso \
  --issuer https://auth.example.com --audience analytics \
  --jwks-url https://auth.example.com/.well-known/jwks.json \
  --roles-claim clickhouse:roles
```

**Instance profiles.** Enterprise and BYOC organisations can change the instance profile with `clickhouse scale --profile`. `clickhouse profile list` shows the available profiles.

**Any region.** `clickhouse create --region` now accepts any region ID and leaves validation to Cloud, so a private region that isn't publicly listed works like a public one. If Cloud rejects a region and a known one is a close match, the error names it. `--custom-region`, added in 0.5.1 for this case, is now a deprecated alias of `--region` and will be removed in 1.0.0.

Also: `clickhouse delete --force` waits at most 10 minutes for the stop and deletes nothing if it times out, and `backup list` takes `--name <service-name>` in place of the service ID.

See the [Cloud service guide](https://github.com/ClickHouse/clickhousectl/blob/main/docs/guides/cloud-service.md).

## ClickPipes

Creating a Kafka, Kinesis, object storage or Pub/Sub pipe used to mean copying every discovered field into a `--column` flag by hand. Those four creates now take `--columns-from <PATH|->`, which reads `clickpipe schema-discover --json` output as it is. Every source field becomes a destination column, along with every metadata field that isn't disabled by default, and each type is used as discovered.

```bash
clickhousectl cloud clickpipe schema-discover object-storage <service-id> \
  --storage-type s3 --source-url 'https://example-bucket.s3.amazonaws.com/events/**' \
  --format JSONEachRow --iam-role "$S3_IAM_ROLE_ARN" --json > discovery.json

clickhousectl cloud clickpipe create object-storage <service-id> \
  --name events-snapshot --storage-type s3 \
  --source-url 'https://example-bucket.s3.amazonaws.com/events/**' \
  --format JSONEachRow --iam-role "$S3_IAM_ROLE_ARN" \
  --database default --table events \
  --columns-from discovery.json --start-paused
```

Edit `discovery.json` first to drop fields you don't want, or add more with `--column`. `--columns-from -` reads stdin, so discovery can be piped straight into create. `schema-discover` also marks which fields are metadata that ClickPipes adds, such as `_topic` or `_path`, in new `Virtual` and `Disabled By Default` columns.

New options:

- **MongoDB**: `--table-mapping-json` accepts `mongoConfig`. `{"persistDeletedDocuments": true}` keeps the full document as it was right before a delete, not only its `_id`.
- **Postgres and MySQL**: `--use-json-native-format true` stores JSON columns as native ClickHouse `JSON` and not `String`. It is a create-time choice and needs the feature enabled for the organisation.
- **Object storage**: `--skip-first-lines <N>` for TabSeparated formats, on `create` and `schema-discover`, and `--object-storage-max-file-size <BYTES>` on `create` and `settings update`.
- **Reverse private endpoints**: `--custom-private-dns-mapping NAME=TARGET_ID` is now accepted for `VPC_ENDPOINT_SERVICE`, where the target is an availability zone ID such as `use1-az1`.
- `clickpipe list` and `--name` lookups follow every page, so they see all pipes without new flags.

The CLI also catches more mistakes before a request is sent, and is clearer about what a command did:

- Kafka creates and schema discovery require authentication, and Kafka, Kinesis and Pub/Sub creates require columns. The API always rejected these requests, and they now fail locally as usage errors.
- Every source's flags are checked before credentials are read.
- `clickpipe start` exits 1 with its own error code when the API accepts the start but doesn't apply it: `clickpipe_still_pausing`, `clickpipe_start_not_applied`, or `clickpipe_start_no_effect` for a `Completed` pipe.
- `cdc-scaling update` needs both `--cpu-millicores` and `--memory-gb`, and says the change was accepted, not completed.
- `clickpipe update` rejects a root `settings` object, because the whole-pipe update doesn't apply it. Use `clickpipe settings update`.

See the [ClickPipes guide](https://github.com/ClickHouse/clickhousectl/blob/main/docs/guides/clickpipes.md) and the [ClickPipe configuration reference](https://github.com/ClickHouse/clickhousectl/blob/main/docs/reference/clickpipe-configuration.md).

## ClickStack

Dashboards and alerts accept PromQL charts. Set `configType` to `promql` in a chart config to query `expressions` against a source of kind `promql`, in `dashboard create`, `update` and `validate`, and in inline alert charts. In 0.5.0 the CLI's own chart check rejected these before they reached the API.

`alert list` gains server-side filters: `--tag`, `--search`, `--source` and `--state`. Repeat a flag to match any of several values.

```bash
clickhousectl cloud clickstack alert list <service-id> --state ALERT --state PENDING --tag checkout
```

Log sources accept the OpenTelemetry `eventNameExpression` and `severityNumberExpression` fields in `source create|update --file`, and metric and PromQL sources accept `minAutoGranularity`.

The CLI still rejects unknown keys in a `--file` body before sending it, but it now leaves the values to the API. A new chart kind or enum value in ClickStack no longer needs a CLI release before you can use it.

See the [ClickStack guide](https://github.com/ClickHouse/clickhousectl/blob/main/docs/guides/clickstack.md).

## Organisation and BYOC

Three new Beta command groups:

- `cloud org byoc access` controls when ClickHouse personnel may access your BYOC infrastructure. `--mode always` allows it, `--mode never` denies it, and `--mode window` allows it for `--duration` seconds from `--start`.
- `cloud org preview` lists the preview features offered to the organisation and switches them on or off.
- `cloud member notification-settings` lists and updates a member's own overrides of their role's notification defaults, from flags or a `--file` body.

```bash
clickhousectl cloud org byoc access update <byoc-id> --mode window \
  --start 2026-11-10T09:00:00Z --duration 14400
clickhousectl cloud org preview list
clickhousectl cloud member notification-settings update <user-id> --effect disabled \
  --notification service_backup_failed --resource <service-id> --channel email
```

`cloud org role list` and role name lookups now follow every page, so they stay complete for organisations with more than 250 roles. `cloud activity list` returns the last 7 days by default, because the whole history of a busy organisation floods an agent's context. Pass `--from-date` for older entries. `--to-date` now includes the named day.

## Built for automation and agents

### Async commands say what to poll

Async Cloud writes return as soon as the API accepts them. Agents rarely read the completion table in the docs, so they guessed what to poll. Those commands' `--json` output now carries a `next` object with the resolved read command, the field to check and the values that mean done or failed:

```json
"next": {
  "command": "clickhousectl cloud clickhouse get 1234-... --org-id 5678-... --json",
  "field": "state",
  "until": ["running"],
  "fail_on": ["failed"],
  "interval_seconds": 5
}
```

Run `command` as it is and stop when `field` holds one of the `until` values. It covers ClickHouse service create, start, wake, stop and delete, Postgres create, restore, read-replica create, resize and promote, ClickPipe start, stop and resync, CDC scaling, and reverse private endpoint creation. Commands with no reliable completion signal, such as a Postgres switchover or an HA change, carry no `next`, and the [automation reference](https://github.com/ClickHouse/clickhousectl/blob/main/docs/reference/automation.md) says what to check for those.

### Exit codes and error codes you can branch on

- **A 403 is no longer an auth error.** Every Cloud API 403 used to exit 4 with `auth_required`, so a quota or policy refusal sent agents to log in again with a valid key. A 403 now exits 1 with `http_4xx` and the server's message. Exit 4 stays for a 401, missing credentials and rejected credential checks.
- **Invalid input always exits 2.** Input that is checked after parsing but can never succeed, such as an unknown `--provider`, a malformed `--ip-allow` or a `--file` body with unknown fields, used to exit 1. An empty resource ID, often an unset shell variable, is also a usage error, and nothing is sent.
- **`resource_not_found` means what it says.** It is reported consistently for missing resources selected by ID or `--name`, and its `command` field lists what does exist in that scope. A delete the API rejects for a service that still exists reports `http_4xx`.
- **Errors name the problem.** A `--file` that can't be read names the flag and path. A body with the wrong shape names the JSON path of the offending value, such as `policies[0].permissions[0]`. Help lists `--file` body fields, and enum errors list the accepted values.
- **One JSON error envelope.** `update` and `skills` failures, and `auth login`, `logout` and `signup`, now follow JSON mode. Local errors keep clickhousectl's own summary in `message` and put text from other programs (ClickHouse, Docker, the OS) in `details`.

### Smaller changes

- `CLICKHOUSECTL_AUTO_JSON=0` keeps human output under a detected coding agent. An explicit `--json` still wins.
- Resize, HA and CDC scaling updates say the change was accepted, not completed.
- Pagination cursors that start with `-` are accepted, and every list command a hint suggests is checked to parse.

## Verified installs and safer updates

Until now the install script, the npm postinstall and `update` all trusted TLS to one download path, and nothing checked the binary. From v0.6.0, every release publishes a `SHA256SUMS` file and a GitHub build provenance attestation for its archives. The archives are served from builds.clickhouse.com and `SHA256SUMS` is read from the GitHub release, so the server that delivers an archive can't also vouch for it.

| Install path | What is checked |
| --- | --- |
| Install script | The archive against the GitHub release's `SHA256SUMS`. A mismatch installs nothing |
| `clickhousectl update` | The same check, before extracting. A mismatch leaves the installed binary unchanged |
| npm | The archive against the `SHA256SUMS` embedded in the npm package at publish time |
| pip, uv, pipx | No separate download. The binary is inside the wheel that PyPI serves |
| `cargo install` | Builds from the crates.io source, which Cargo checks against the index checksum |

To check that an archive was built by the repository's release workflow, verify its attestation with the GitHub CLI:

```bash
gh attestation verify "clickhousectl-${TARGET}-${VERSION}.tar.gz" -R ClickHouse/clickhousectl
```

`update` itself is more careful:

- It refuses to overwrite a binary that npm, pip, uv or pipx manages, and prints the package manager's upgrade command.
- It swaps the binary only after the new one runs `--version` successfully. A failure leaves the old binary in place.
- The latest version is resolved from builds.clickhouse.com. 0.5.0 asked the GitHub API, which allows 60 unauthenticated requests per hour per IP, so `update` could fail with `403 rate limit exceeded`. If you hit that on 0.5.x, rerun the install script.
- The background update check can be turned off with `CLICKHOUSECTL_NO_UPDATE_CHECK=1`. `--version` no longer waits up to 10 seconds on the network, and a failed check is retried after an hour, not a day.

See [release verification](https://github.com/ClickHouse/clickhousectl/blob/main/docs/reference/install-verification.md).

## Authentication

**OAuth logins are pinned to their authorization server.** `cloud auth login` now saves the authorization server's configuration with the tokens, and every refresh uses that saved configuration. A login saved by 0.5.x doesn't have it, so `auth status` shows OAuth as `Login required` and Cloud commands exit 4 with a re-login message. Run `clickhousectl cloud auth login` once after upgrading.

**A saved API key works only against the API it was saved for.** When `auth login --api-key` verifies a key against a non-production API with `--url`, that API is saved with the key. A later command that names a different API exits 4 without sending the key.

**Saved credentials fail closed.** A `credentials.json` that exists but can't be read stops Cloud commands with an error naming the file. The CLI no longer falls through to environment or OAuth credentials you didn't intend to use. An OAuth login that can't be refreshed is kept and reported as `Expired`, where it used to be removed. Tokens are written atomically and refresh is locked, so two commands running at once can't corrupt the file.

**Stored query keys are gone.** Since 0.5.0, `cloud clickhouse query` binds your active API key to the service's Query API endpoint. 0.6.0 stops using the older per-service keys that earlier versions created and stored, though the keys themselves still exist in your organisation. It also removes `repair-query-key`. A leftover record is removed on the next query or delete of that service, and the CLI prints the `cloud key delete` command for the key it named. A read-only API key can't bind itself, and now fails with `query_key_bind_forbidden` and the command that binds it with a write-capable key.

Also: when credentials reach several organisations and none is selected, the command exits 2 and lists each organisation's ID and name. An `--org-name` that matches more than one organisation lists the IDs to pass to `--org-id`. The OAuth device flow can sign in against a custom API target by setting `CLICKHOUSECTL_AUTH_URL` and `CLICKHOUSECTL_CLIENT_ID`.

See the [authentication reference](https://github.com/ClickHouse/clickhousectl/blob/main/docs/reference/authentication.md).

## Local development improvements

**Run a ClickHouse build you compiled yourself.** `local install --binary <PATH>` copies the file into `~/.clickhouse/versions/`, runs the copy with `--version`, and installs it under the version it reports. From there `local use`, `clickhouse start --version` and `local remove` treat it like any other install. Pass `--force` to replace it after a rebuild.

```bash
clickhousectl local install --binary ~/ClickHouse/build/programs/clickhouse
```

The rest is a round of fixes:

- A stopped server restarts on the version it last ran. Before, `stop` cleared the recorded version, so a later `start` without `--version` ran the data directory on the default version and silently upgraded or downgraded it.
- Commands that take a server name follow one selection rule when it is omitted: the server named `default`, else the project's only server of that engine. With several and no `default`, they fail with `server_selection_required` and list the names. `remove` never guesses.
- Read-only commands such as `list` no longer create `.clickhouse/` in the current directory.
- The port check detects wildcard and `::1` listeners, rejects port 0 and equal HTTP and TCP ports, and an omitted port never takes the one the other listener uses.
- Server processes are found natively, without `pgrep`, `ps` or `lsof`, and a stored PID is confirmed to be a ClickHouse server before the CLI trusts it.
- `local clickhouse stop`, `remove` and `local remove` no longer need Docker.
- Exact versions install on Intel macOS again.
- `dotenv` quotes values that contain `$` or other shell-special characters.

And for local Postgres:

- `local postgres client` stops a script at the first failed statement and exits 3. Before, a failing `--queries-file` or piped script printed the error and exited 0. Pass `-- -v ON_ERROR_STOP=0` to run the remaining statements.
- New containers are named `clickhousectl-pg-<project hash>-<name>-<major>`, so two projects can use the same instance name. Existing containers keep their names.
- Resuming an instance whose port is now taken fails with `port_in_use`. Stopping an instance that is already stopped succeeds and reports `already_stopped`.

See the [local development guide](https://github.com/ClickHouse/clickhousectl/blob/main/docs/guides/local-development.md).

## Command renames

`local server` is now `local clickhouse`, and `cloud service` is now `cloud clickhouse`, with `ch` and `pg` as short aliases for the two engines. The old names still work. Locally, each engine's `list` and `stop-all` now cover only that engine, and `local status` shows both.

## Upgrade notes

The renames keep their old spellings, so most scripts carry on working. These changes need action or change what an existing script sees.

### Breaking changes

| Change | 0.5.x | 0.6.0 |
| --- | --- | --- |
| OAuth logins saved by an earlier version can't be used | The saved login was refreshed and used | `auth status` shows `Login required`. Run `clickhousectl cloud auth login` once |
| `local server list` and `local server stop-all` cover ClickHouse only | Both listed and stopped ClickHouse and Postgres | `local status` lists both engines. `local postgres stop-all` stops Postgres |
| `repair-query-key` is removed, and stored per-service query keys are no longer used | `cloud service repair-query-key <id>` | Queries bind the active API key. Delete leftover `clickhousectl-query-<service-name>` keys with `cloud key delete` |
| Kafka ClickPipe creates and discovery require authentication. Kafka, Kinesis and Pub/Sub creates require columns | The request was sent and the API rejected it (exit 1) | Usage error (exit 2) before any request. Pass `--auth` or a credential flag, and `--column` or `--columns-from` |
| JSON `project_scope` for local commands | `parent_projects_searched` present | `kind` is `project_root`, `current_directory` or `env_override`. `parent_projects_searched` is removed |

### Behaviour changes

| Change | 0.5.x | 0.6.0 |
| --- | --- | --- |
| Project scope | The exact current directory | The nearest `.clickhouse/` in the current directory or a parent, up to your home directory. A `.clickhouse/` in a shared parent now becomes the project for directories beneath it, so run `local init` in each project |
| A Cloud API 403 that isn't about credentials | Exit 4, `auth_required` | Exit 1, `http_4xx` |
| Invalid input found after parsing | Exit 1, code `other` | Exit 2, usage error |
| `local postgres client` with a file or piped script | Carried on after a failed statement and exited 0 | Stops at the first failed statement and exits 3 |
| `cloud activity list` with no dates | The whole history | The last 7 days. Pass `--from-date` for more |
| `clickhousectl update` on an npm, pip, uv or pipx install | Overwrote the managed binary | Refuses, and prints the package manager's upgrade command |
| `--custom-region` on service create | Sent a region the CLI didn't know | Deprecated alias of `--region`, removed in 1.0.0 |
| Installing a release older than v0.6.0 with the script or `update` | Installed without a checksum | Refused, because those releases have no `SHA256SUMS` |

## The Rust API library

`clickhousectl` is built on [`clickhouse-cloud-api`](https://crates.io/crates/clickhouse-cloud-api), a typed Rust client for the ClickHouse Cloud API that is released in lockstep with the CLI. From 0.6.0 it has a [changelog](https://github.com/ClickHouse/clickhousectl/blob/main/crates/clickhouse-cloud-api/CHANGELOG.md) that says what a Rust caller must change to upgrade. The larger changes in this release:

- Timestamp fields are `jiff::Timestamp`, where they were `chrono` types. On the wire they are still RFC 3339 in UTC.
- Request structs with a required field no longer implement `Default`, so `..Default::default()` can't silently fill a field the API has just made required.
- The crate re-exports `reqwest`, so a prebuilt HTTP client uses the same version as the library.

## Thanks

Thanks to [Emanuele De Cupis](https://github.com/balanza), who added OAuth device login against custom API targets ([#1082](https://github.com/ClickHouse/clickhousectl/pull/1082)), to [@divyenduz](https://github.com/divyenduz), who removed the Beta label from Postgres ([#1382](https://github.com/ClickHouse/clickhousectl/pull/1382)), and to [Andrey Chudnovskiy](https://github.com/achudnovskij), who added Postgres 19 ([#1462](https://github.com/ClickHouse/clickhousectl/pull/1462)).
