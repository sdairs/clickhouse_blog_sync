---
title: "ClickStack APIs arrive in the ClickHouse Cloud OpenAPI"
date: "2026-03-03T17:36:35.849Z"
category: "Product"
excerpt: "ClickStack APIs arrive in the ClickHouse Cloud OpenAPI"
---

# ClickStack APIs arrive in the ClickHouse Cloud OpenAPI

<style>
div.w-full + p,
span.relative + p {
  text-align: center;
  font-style: italic;
}
</style>

As teams scale their observability with ClickStack across more services and environments, keeping configuration consistent becomes its own challenge. A dashboard built for one service needs to be replicated for the next. Alerts configured in development need to be recreated in staging and production. The more environments you operate, the more manual work is involved. And with it, the risk of drift, missed alerts, and inconsistency.

With ClickStack resources now in the ClickHouse Cloud API, observability configuration can live in your deployment pipelines, version control, and infrastructure-as-code workflows. Dashboards follow a service from dev through staging to production. Alerts ship alongside the applications they monitor. Configuration is reviewed in pull requests and deployed through CI/CD.

Together with capabilities like role-based access control on the roadmap, this lays the foundation for production-grade observability workflows with the same controls teams already apply to application code.

[Explore the full API reference](https://clickhouse.com/docs/cloud/manage/api/swagger#tag/ClickStack)

## **Getting started** {#getting_started}

Getting started takes minutes if you already have a Managed ClickStack service and a ClickHouse Cloud API key.

**Prerequisites:** a ClickHouse Cloud organization with a Managed ClickStack service, and an API key with Service Admin or Org Admin permissions.

The full endpoint reference — including request and response schemas for all supported resources — is available in the [ClickStack API documentation](https://clickhouse.com/docs/use-cases/observability/clickstack/api-reference). The OpenAPI spec can also be [downloaded directly](https://api.clickhouse.cloud/v1) for SDK generation or to import into tools like [Postman](https://www.postman.com/) for interactive exploration.

## **What you can do now** {#what_you_can_do_now}

The API covers the core resources teams need to manage ClickStack programmatically:

**Dashboards** can be created, read, updated, and deleted through the API, including chart configurations and dashboard-level filters. Dashboards built through the API render identically in the ClickStack UI, with the same layout and behavior you would get by building them interactively.

**Alerts** can be defined as rules tied to dashboard tiles or saved searches with webhook delivery.

**Sources** and **Webhooks** round out the supported resources — list your configured data sources and webhook destinations to retrieve the IDs that dashboard and alert configurations require, without manual lookups.

This release enables the first wave of the config-as-code improvements. We are continuing to expand coverage — a Terraform provider for ClickStack is actively in development, and additional resource types are on the way.

## **How it works** {#how_it_works}

ClickStack endpoints live under the same base path as the rest of the ClickHouse Cloud API:

```shell
https://api.clickhouse.cloud/v1/organizations/{organizationId}/services/{serviceId}/clickstack/...
```

**If you are already using ClickHouse Cloud API keys, you can start making ClickStack API calls immediately — no separate credentials or token exchange required.** The only requirement is that the API key has Org Admin or Service Admin permissions. API keys scoped to particular services will have access to the ClickStack teams corresponding to those services, while Org Admin keys have access to all services.

A dedicated "Manage ClickStack API" permission is assigned by default to Org Admin and Service Admin roles, with finer-grained access control planned for a future release.

We also invested in making the API spec clean and predictable for tooling consumers. Inline schemas have been replaced with named types, number fields use `integer` rather than `number`, and validation errors return structured details rather than opaque 400 responses. These choices matter when generating SDKs, writing Terraform providers, or integrating with CI/CD tooling that consumes the OpenAPI spec directly.

## **Examples** {#examples}

Here are a few common examples to illustrate how the API works in practice.

**List all dashboards for a ClickStack service:**

<pre><code type='click-ui' language='bash'>
curl -X GET \
  'https://api.clickhouse.cloud/v1/organizations/{organizationId}/services/{serviceId}/clickstack/dashboards' \
  --user '<keyId>:<keySecret>' \
  -H 'Content-Type: application/json'
</code></pre>

**Create a dashboard with a request volume time series chart filtered by service name:**

<pre><code type='click-ui' language='bash'>
curl -X POST \
  'https://api.clickhouse.cloud/v1/organizations/{organizationId}/services/{serviceId}/clickstack/dashboards' \
  --user '<keyId>:<keySecret>' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "API Monitoring Dashboard",
    "tiles": [
      {
        "x": 0,
        "y": 0,
        "w": 24,
        "h": 12,
        "name": "Request Volume",
        "config": {
          "displayType": "line",
          "sourceId": "[sourceId]",
          "asRatio": false,
          "alignDateRangeToGranularity": true,
          "fillNulls": true,
          "select": [
            {
              "valueExpression": "",
              "aggFn": "count",
              "where": "ServiceName:\"api\"",
              "whereLanguage": "lucene"
            }
          ]
        }
      }
    ],
    "tags": ["monitoring"]
  }'
</code></pre>

**Create an alert on a dashboard chart with webhook notification to Slack:**

<pre><code type='click-ui' language='bash'>
curl -X POST \
  'https://api.clickhouse.cloud/v1/organizations/{organizationId}/services/{serviceId}/clickstack/alerts' \
  --user '<keyId>:<keySecret>' \
  -H 'Content-Type: application/json' \
  -d '{
        "name": "Alert SREs when request rate is high",
        "message": "API request rate exceeded expected volume",
        "threshold": 1000,
        "interval": "1m",
        "thresholdType": "above",
        "source": "tile",
        "channel": {
        	"type": "webhook",
        	"webhookId": "[webhookId]",
        	"webhookService": "slack_api",
        	"slackChannelId": "#prod-api-alerts"
        	},
        "tileId": "[tileId]",
        "dashboardId": "[dashboardId]"
}'
</code></pre>

The response includes the created resource with its assigned `id`, which you can then use for updates. Validation errors return structured details so issues surface immediately rather than silently producing misconfigured resources.

**Tip:** The OpenAPI spec is available for [download](https://api.clickhouse.cloud/v1) and works with the tooling you already use. Import it into [Postman](https://www.postman.com/) or [Insomnia](https://insomnia.rest/) to generate a ready-to-use collection, open it in the [Swagger Editor](https://editor.swagger.io/) to explore endpoints in your browser, or use it with VS Code extensions like [REST Client](https://marketplace.visualstudio.com/items?itemName=humao.rest-client) or [Thunder Client](https://marketplace.visualstudio.com/items?itemName=rangav.vscode-thunder-client) for a lightweight workflow without leaving your editor.

## **What comes next** {#what_comes_next}

The ClickStack API is the first of several capabilities focused on making ClickStack easier to integrate and operate at scale. A Terraform provider is in active development, finer-grained access control is on the roadmap, and we plan to expand the API surface with additional resources as the offering matures.

We would love to hear what resources and workflows matter most to your team. Join the ClickHouse Slack and hop into the [#olly-clickstack channel](https://clickhouse.com/slack) to share feedback, ask questions, or help shape what comes next.


---

## Get started today with ClickStack

Interested in seeing how ClickStack works for your observability data? Get started in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-91-get-started-today-with-clickstack-sign-up&utm_blogctaid=91)

---