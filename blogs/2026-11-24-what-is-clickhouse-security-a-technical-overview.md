---
title: "What is ClickHouse Security? A technical overview of the agentic SIEM built on ClickHouse"
date: "2026-11-26T09:27:22.147Z"
author: "Kira Furuichi"
category: "Product"
excerpt: "ClickHouse Security is an agentic SIEM on ClickHouse. See how sources, pipelines, SQL and Sigma detections, investigations, and AI agents work together."
---

# What is ClickHouse Security? A technical overview of the agentic SIEM built on ClickHouse

[ClickHouse Security is an agentic SIEM that runs on ClickHouse](https://clickhouse.com/security). It collects logs from over 120 cloud, identity, and SaaS sources, runs detections on them, tracks investigations, and puts AI agents to work on alert triage, detection tuning, and threat hunting, all on one platform. It is the integrated offering between RunReveal and ClickHouse Cloud, and [recently entered private preview.](https://clickhouse.com/blog/introducing-clickhouse-security-agentic-siem) This post walks through sources and pipelines, detections, investigations, agents, and the ways you can build on top of it:

* **Sources and pipelines:** 120+ first-party integrations with built-in pipelines that filter, route, and enrich logs before storage. Create custom webhook and S3 sources.  
* **Detections:** Managed detections out of the box, plus your own as scheduled SQL or streaming Sigma rules, managed as code in Git through the CLI.  
* **Investigations:** Alerts can open cases with a timeline of queries, results, notes, and indicators, with agent assistants to help coordinate.  
* **Agents:** AI agents triage alerts, tune and generate detections, and hunt threats, and you can build your own with the MCP server, API, CLI, and Slack bot and the LLM of your choice.  
* **Storage:** Everything is queryable with SQL on ClickHouse, where columnar storage and compression keep queries fast and long retention affordable.

## What is ClickHouse Security? {#what_is_clickhouse_security}

ClickHouse Security is an agentic SIEM built on ClickHouse. It ingests security logs from cloud, identity, and SaaS sources, stores them in your ClickHouse Cloud service, runs managed and custom detections, organizes alerts into investigations, and runs AI agents that triage alerts, tune detections, and hunt threats.

The platform comes from RunReveal, which built a security data platform on ClickHouse before [joining ClickHouse in September 2026](https://clickhouse.com/blog/clickhouse-welcomes-runreveal). Because ClickHouse Security builds on RunReveal technology, the [RunReveal docs](https://docs.runreveal.com/) are an excellent resource that describe the platform in more detail than this post can.  They continue to be maintained and kept up to date with new releases.

Three design choices shape the platform.

* **Agents are part of the platform:** They work on the same data, detections, and investigations your analysts use, so there's no separate AI SOC tool to connect.  
* **Pipelines are built in:** You filter, route, and enrich logs inside the platform before they're stored, with no separate pipeline layer to buy and run.  
* **Your data sits in ClickHouse:** If you already use ClickHouse for observability or analytics, security data can now be sent there instead of in a separate SIEM.

During the Private Preview, approved customers select a ClickHouse Cloud service and provision the schemas and views that ClickHouse Security uses. The security team works in ClickHouse Security, and the data stays in a database you can also query directly with SQL.

ClickHouse Security is for teams that need to keep and search large volumes of security data: SOC analysts and managers, detection engineers, threat hunters, and security engineers who run the pipeline underneath them.

## How does ClickHouse Security collect and process logs? {#how_does_clickhouse_security_collect_and_process_logs}

ClickHouse Security collects logs through 120+ first-party integrations. Each [source](https://docs.runreveal.com/sources) ingests by webhook, API polling, or object storage, and built-in pipelines filter, route, and enrich the data before it's stored in ClickHouse. Data from our first party sources are normalized to a standard schema, similar to OCSF; the raw log is also persisted, so teams can reference and query that if needed.

The [source catalog](https://docs.runreveal.com/sources) covers cloud, identity, and SaaS data, including AWS CloudTrail, Okta, Azure Entra, Cloudflare, CrowdStrike, GitHub, Kubernetes audit logs, Microsoft 365, and OpenTelemetry (OTLP JSON). You can filter it by ingest method, category, and plan. If a source has no integration, the Custom Source wizard walks you through choosing an ingest method, connecting, verifying, previewing data, and mapping JSON paths to normalized fields.

### Three ways to ingest

| Method | How it works | What to know |
| ----- | ----- | ----- |
| Webhook | The platform generates a unique URL, and your app sends events to it. | Easiest to set up and maintain, but clients that don’t retry requests may not be recoverable. |
| API polling | The platform calls the source's API, usually on a 60-second timer, and stores a token to track where it left off. | Credentials are stored encrypted. A failed poll doesn't advance the watermark, so the next poll retries the same window. |
| Object storage | Logs land in a bucket you control, an event notification goes to a queue, and the platform downloads the referenced object. | Supports AWS S3, Azure Blob Storage, Google Cloud Storage, and Cloudflare R2. |

The `reveald` agent is a log forwarder that tails files, journald, and Windows event data.  You can also bring-your-own forwarders that support S3 as a destination. Health checks alert you when a source stops sending data, so a silent gap doesn't go unnoticed.

Data from our first-party sources enters ClickHouse Security normalized and ready to query. ClickHouse Security follows a data schema very similar to OCSF, but is slightly different and more opinionated. Raw logs are also kept, so security teams can leverage both the normalized and raw data when needed.

### Pipelines for filters and transforms, Federated Search for existing S3 data

Security logs vary widely in volume and value. [Log processing pipelines](https://docs.runreveal.com/logs) support transforms, enrichment, filtering, and sampling, so you decide what's stored and what shape it's in before it lands. Transforms normalize source fields into a common schema, which is what lets one detection run across data from different sources. Because the pipelines are part of the platform, you don't run or pay for a separate pipeline layer.

You can also query data that you haven't ingested. [Federated search](https://docs.runreveal.com/logs) reads from external S3-compatible buckets without loading the data first.

## How do detections work in ClickHouse Security? {#how_do_detections_work_in_clickhouse_security}

ClickHouse Security runs two kinds of [detections](https://docs.runreveal.com/detections): scheduled SQL rules for joins, aggregations, and historical analysis, and streaming Sigma rules for real-time pattern matching. You can start from a library of managed detections or write your own, and you can manage all of them as code in Git.

| Type | Language | When it runs | Best for |
| ----- | ----- | ----- | ----- |
| Scheduled (batch) | ClickHouse SQL | On a cron schedule | Correlation, Aggregations, historical analysis |
| Streaming | Sigma YAML | In real time as events arrive | Simple pattern matching and shareable rules |

### Managed detections

The Detection Query Library holds curated SQL rules, and the Sigma Detection Library holds streaming Sigma rules. You subscribe to a managed detection to enable it, and you can set its notifications, parameters, and optional AI triage when you do. Tier 1 detections, tagged `tier-one`, are the ones recommended for the sources you've connected. You can also sync packs from the [public-detection-packs GitHub repository](https://github.com/runreveal/public-detection-packs).

### Write your own

This SQL detection, adapted from the [RunReveal quick start](https://docs.runreveal.com/how-to-guides/detections-signals-alerts-quick-start), flags a suspicious login event from a webhook source. It reads from the `logs` table, extracts fields from `rawLog`, and uses the `{from:DateTime}` and `{to:DateTime}` parameters to limit each run to its time window. Run on a schedule such as `*/5 * * * *`, it checks every five minutes.

<pre><code type='click-ui' language='sql'>
SELECT
    eventName,
    actor,
    srcIP
FROM logs
WHERE sourceType = 'structured-webhook'
  AND receivedAt BETWEEN {from:DateTime} AND {to:DateTime}
  AND eventName = 'suspicious_login'
  AND srcIP = '192.168.1.100';
</code></pre>

The same logic as a streaming Sigma rule matches on fields that the pipeline has already extracted.

```yaml
title: Suspicious login
logsource:
  service: structured-webhook
detection:
  selection:
    eventName: suspicious_login
    rawLog.srcIP: 192.168.1.100
  condition: selection
level: medium
riskscore: 50
```

### Signals, alerts, and severity

A detection result without a notification channel lands in the `signals` table, which you use for analysis and tuning. A result with a channel, such as email, Slack, or PagerDuty, lands in the `alerts` table. Both are ordinary ClickHouse tables, so you can query them with SQL like any other data.

Each detection carries a severity (Low, Medium, High, or Critical), a risk score from 0 to 100, and a MITRE ATT&CK mapping. A finding stores the matched log, the MITRE ATT&CK mapping, the risk score, and the rule that fired, so an analyst can see why it triggered without rebuilding the query.

### Detections as code

Detections are code, and you can manage them that way. This enables security teams to write detections in SQL with AI assistance, keep them in Git with peer review, and deploy them through the CLI and a GitHub Action. The CLI includes commands to export, test, sync, and dry-run detections. Before a detection goes live, you can run [CI/CD tests for your detections as code against sample or historical events](https://blog.runreveal.com/runreveal-detection-cicd-guide/).

## How do investigations work? {#how_do_investigations_work}

An [investigation](https://docs.runreveal.com/investigations) is a workspace for tracking a security incident. It collects related alerts, queries, query results, chats, graphs, and notes into one chronological timeline, with a status, severity, classification, tags, and an assignee.

An alert can join an investigation in two ways. An analyst can attach it from the alert detail view. Or a detection with auto-create enabled opens an investigation when it fires, with the alert attached as the first artifact. By default, each alert gets its own investigation. A beta grouping setting opens one investigation per detection run instead, in batches of up to 200 alerts.

### What goes into an investigation

There are 11 artifact types, including queries, query results, alerts, chats, chat messages, graphs, links, and indicators. Security engineers can add them as they work:

* **Queries and results:** Run SQL against your logs, then use "Add to Investigation" to keep the query and its result on the timeline.  
* **Notes:** Write Markdown notes alongside the evidence.  
* **Indicators:** Track structured indicators of compromise by type and value, and look them up across investigations.  
* **Stars:** Mark the artifacts that matter, then filter the timeline by artifact type or starred items, or search artifact content.

Status changes and artifact additions are logged with timestamps and user attribution, which gives you an audit trail. Resolution and update artifacts can't be deleted.

### From open to closed

1. Open an investigation, or let a detection open one.  
2. Add artifacts from queries, alerts, chats, and graphs, and write notes as you work.  
3. Set the status to `investigating` once work starts.  
4. Close it with a classification of true positive, false positive, or inconclusive, plus optional resolution details.

### Querying, graphs, and dashboards

Because logs live in ClickHouse, every pivot is a SQL query. [Dashboards](https://docs.runreveal.com/dashboards) are built the same way: a graph is a SQL query with a chart type (line, column, area, bar, pie, or KPI), panels hold graphs, and a layout arranges panels. AI chat can generate a graph from a plain-English description. If you already use Grafana or Jupyter, [integrations](https://docs.runreveal.com/integrations) connect both to your security data.

## What do the AI agents do? {#what_do_the_ai_agents_do}

Agents in ClickHouse Security work on the same logs, detections, and investigations as your analysts. They triage alerts, support detection tuning and generation, and help hunt threats. You can reach the same data through [AI chat](https://docs.runreveal.com/ai-chat) in the console or from Slack.

### Alert triage

Triage is the agent workflow with the [most detail in the docs](https://docs.runreveal.com/ai-chat). When a detection has AI triage enabled and fires, the default triage agent works the investigation that opens, focused on the alert that opened it. The [AI SOC guide](https://docs.runreveal.com/how-to-guides/ai-soc-guide) describes a fixed 11-step run. While it works, the investigation shows the status `agent-triage`. The agent:

* Classifies the case as true positive, false positive, or inconclusive, with a one-sentence summary under 150 characters  
* Adjusts severity when the logs don't match the detection's default  
* Checks indicators from earlier investigations before it writes its note  
* Escalates real concerns to `investigating` and closes clear false positives

As part of the triage process, your agents will suggest options to tune noisy detections so your alerts maintain high fidelity and criticality.

### The security team stay in control

Analysts and security engineers review the cases that reach `investigating`, take response actions, tune detections, and record the resolution. The docs also set guardrails. Turn on AI triage only for reviewed, stable detections, because a new or noisy detection can open hundreds of investigations at once. The agent adds indicators only for true positives, and notes added after a case closes don't change its classification. You can cancel pending agent tasks from the agent queue. In Slack, mutating agent actions need your confirmation.

### AI chat

[AI chat](https://docs.runreveal.com/ai-chat/native-ai-chat) is a purpose-built investigation agent in the console. Analysts ask questions in plain language, and the agent writes and runs the ClickHouse SQL, so you can explore your data without knowing the schema or the query syntax first. It lists tables, reads schemas, checks query history, queries your logs, and explains what it did and what it found.

These prompts, taken from the docs, show the range of work it handles:

| Task | Example prompt | What the agent does |
| ----- | ----- | ----- |
| Ad hoc queries | "Show me all failed login attempts from the last 24 hours" | Runs SQL against your logs and returns the results. |
| Finding patterns | "What IP addresses had the most failed authentication attempts?" | Aggregates the events and ranks the results. |
| Exploring your data | "What tables contain network traffic data?" | Lists the tables and reads their schemas. |
| Investigating an incident | "I need to investigate a suspicious login from IP 192.168.1.100" | Analyzes login patterns, cross-references threat intelligence when it's configured, and suggests next steps. |
| Explaining what happened | "Why did this detection fire?" or "What caused this spike in DNS queries?" | Traces the matching events and explains the cause. |
| Reviewing coverage | "What detection rules do we have for privilege escalation?" | Looks up the existing detections for that behavior. |
| Creating detections | "Create a new detection for suspicious file downloads from Slack" | Drafts a rule from your description for you to review. |
| Deciding what's next | "What should I investigate next?" | Suggests a follow-up based on what it has found so far. |

Under the hood, chat runs a loop. It gathers context, forms a hypothesis, picks the next action, and runs a query or tool. When a query returns a syntax error, it learns from the error and tries again. Every action is explained and logged, and access follows the same role-based permissions as the rest of the workspace.

Chat keeps your investigation history across sessions, so a multi-day investigation picks up where it stopped. In an interactive chat, it can also recall truncated query results and keep notes in a scratchpad. A few habits improve the answers: give a timeframe ("last 24 hours" works better than "recently"), include context ("high-priority alerts" works better than "all alerts"), start broad, and ask for explanations and recommendations. You can also chat from your terminal with `runreveal agent`, which uses the same chat sessions.

Model calls run server-side with your own provider keys and inference provider, and chat history stays on the platform. AI chat works with Anthropic (Claude), OpenAI, Google AI, and AWS Bedrock through an IAM role. Google Vertex AI is available on request. Admins add provider keys and set the default model in AI settings, and each user picks a provider and model when they start a chat.

![](https://clickhouse.com/uploads/image3_2c87e7abbe.png)

### MCP server

The [MCP server](https://docs.runreveal.com/ai-chat/model-context-protocol) allows you to connect AI assistants like Claude and Cursor to external data sources and tools. There are two ways to run it:

* **Remote:** A hosted server over HTTP/HTTPS that authenticates with OAuth. OAuth tokens are specific to a workspace and carry scopes.  
* **Local:** A server you run yourself with the `runreveal mcp` command, authenticated with an API token. It suits on-premises and air-gapped deployments.

In Claude Desktop or Claude.ai, you add it as an integration. In Claude Code, one command registers it, where `<server-url>` is the server URL from your workspace:

<pre><code type='click-ui' language='bash'>
claude mcp add -t http runreveal '&lt;server-url&gt;'
</code></pre>

Four read tools cover exploration: `source_list`, `list_tables`, `get_table_schema`, and `run_query`, which executes ClickHouse SQL. Write-capable tools cover creating and updating detections, managed detection subscriptions, agents, investigations, dashboards and graphs, agent skills, and notifications. Each tool needs the matching OAuth scope or API token permission, so an assistant that only needs to read can be limited to read access.

The docs recommend reviewing any generated detection in the UI before you enable it, and validating it against real log data first. They also advise time-bounding SQL detections with `{from:DateTime}` and `{to:DateTime}`.

### Slack bot

The [Slack bot](https://docs.runreveal.com/integrations/slack-bot) runs the AI agent directly from Slack. An operator or admin installs it from AI settings, picks a bot role, and approves the Slack OAuth consent screen. A model provider has to be configured first.

Each user links their own Slack identity to their account. In a direct message, the agent runs with that user's own role. In a channel mention or a group DM, it runs under the bot role chosen at install, so shared-channel actions stay within that role's permissions. The bot answers when mentioned in a channel or will respond directly in a DM without needing to be mentioned. Each Slack thread maps to one chat, so follow-up questions keep their context, and Slack and the console share chat history.

![](https://clickhouse.com/uploads/image1_f88721b1f5.png)

## Can you build your own agents and workflows with ClickHouse Security? {#can_you_build_your_own_agents_and_workflows_with_clickhouse_security}

Yes. ClickHouse Security exposes the platform through an MCP server, an API, a CLI, and a Slack bot, so you can build agents and workflows with the LLM of your choice on top of your security data.

| Interface | What you can do with it |
| ----- | ----- |
| [MCP server](https://docs.runreveal.com/ai-chat) | Connect assistants such as Claude and Cursor over a remote HTTP/HTTPS server that authenticates with OAuth. Tools cover querying data, managing detections, and exploring schemas. |
| [API](https://docs.runreveal.com/api-reference) | Call the platform programmatically. The API reference describes how to generate an OpenAPI 3.0 spec with the CLI. |
| CLI | Export, test, sync, and dry-run detections, and subscribe to managed detections. |
| [Slack bot](https://docs.runreveal.com/integrations) | Investigate with AI chat from Slack DMs and channel mentions. Each Slack user links to their own account. |

Reusable prompts and agent skills make those workflows repeatable. A prompt is a template that takes dynamic arguments and works with MCP-compatible assistants. A skill is a Markdown playbook that can inline saved queries and notification channels, so an incident response checklist can run the same way every time.

## Why run a SIEM on ClickHouse? {#why_run_a_siem_on_clickhouse}

A SIEM is a data problem first. Security data arrives continuously and in high volume, has to stay searchable for a long time, and has to answer queries quickly while an analyst waits. ClickHouse's columnar storage and compression keep long retention affordable, and its parallel query execution keeps searches fast as data grows.

When [RunReveal joined the team](https://clickhouse.com/blog/clickhouse-welcomes-runreveal), we described security as the largest and fastest growing data workload in the enterprise. Cloud audit logs, identity events, endpoint telemetry, and network flows all need continuous high-throughput ingest, multi-year retention, and fast queries during live analysis. Those are exactly the workloads ClickHouse is built for.

That has practical effects for a security team.

* **You keep more data:** Cheaper retention means you can store the logs you'd otherwise filter out to control cost, and search them later when an investigation needs them.  
* **Everything is SQL:** Detections, signals, alerts, dashboards, and ad hoc hunts are all queries over ClickHouse tables, so one query language covers detection, investigation, and reporting.  
* **Agents get fast answers:** Agents query the same tables your team does, so the speed of the database sets the speed of an investigation.  
* **Security data sits next to your other data:** If you already use ClickHouse, security data can now be a part of the ClickHouse ecosystem instead of being sent down into a separate SIEM.

## How do you get started with ClickHouse Security? {#how_do_you_get_started_with_clickhouse_security}

ClickHouse Security is in Private Preview, and you can [request access](https://clickhouse.com/security#request-access) on the product page. Once you're approved, a typical path looks like this:

1. Select [the ClickHouse Cloud service](https://docs.runreveal.com/how-to-guides/connect-clickhouse-cloud) to use and provision the schemas and views.  
2. Connect your first sources, starting with the cloud and identity logs you already collect.  
3. Subscribe to managed detections for those sources, and add your own as SQL or Sigma rules.  
4. Turn on AI triage for detections you've reviewed and trust.  
5. Connect your own tools through the MCP server, API, CLI, or Slack bot.

To see how a security team runs this day to day, join our [December 3 webinar](https://clickhouse.com/company/events/202612-AMER-Webinar-ClickHouse-Security), where Morgan Fenton, a senior incident response security engineer at ClickHouse, walks through our own setup and Evan Johnson, CEO and co-founder of RunReveal, joins the live Q&A.

## FAQ {#faq}

### What is an agentic SIEM?

An agentic SIEM is a security information and event management platform that is built for agents to use as much as humans. In ClickHouse Security, agents work directly on the stored logs, detections, and investigations, so triage, detection tuning, and threat hunting use the same data as your team.

### How is ClickHouse Security related to RunReveal?

ClickHouse Security is the integrated offering between RunReveal and ClickHouse Cloud, built on RunReveal technology. RunReveal was built on ClickHouse from the start. Existing RunReveal customers stay supported, and the [launch announcement](https://clickhouse.com/blog/introducing-clickhouse-security-agentic-siem) covers what changes for them.

### Where can I read the product documentation?

The [RunReveal docs](https://docs.runreveal.com/) cover sources, detections, investigations, AI chat, dashboards, and the API in detail.

---

## Get started today

Interested in seeing how ClickHouse works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-3190-get-started-today-sign-up&utm_blogctaid=3190)

---