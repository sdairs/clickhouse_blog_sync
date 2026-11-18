---
title: "Bring your Claude Platform organization to ClickHouse Cloud with linked billing"
date: "2026-11-17T18:14:57.955Z"
author: "Ryadh Dahimene, Alice Dalby and Andrew Wilkins"
category: "Product"
excerpt: "Link your Claude Platform organization to ClickHouse Cloud and have Anthropic bill Claude API usage in ClickHouse Agents and AI Functions directly on your existing terms."
---

# Bring your Claude Platform organization to ClickHouse Cloud with linked billing

Linked billing lets you link your Claude Platform organization to ClickHouse Cloud, with no API key to share. Anthropic bills Claude API usage in ClickHouse Agents and AI Functions directly to your Claude organization, on your existing terms. 

[ClickHouse Agents](https://clickhouse.com/docs/products/cloud/features/ai-ml/agents) has run on Claude since its public beta in June, preconfigured for every ClickHouse Cloud customer. [AI Functions](https://clickhouse.com/docs/reference/functions/regular-functions/ai-functions), now in private preview in ClickHouse Cloud, let you call a model directly from SQL. Customers who already have a Claude organization asked whether that usage could be billed to it directly. With linked billing, it can.

## No API key to manage {#no_api_key_to_manage}

Bringing your own model provider to a platform usually means pasting an API key, then scoping it, rotating it and tracking where it is stored. Linked billing removes that step. An admin approves the link, and Claude API usage in ClickHouse Agents and AI Functions is then billed to your Claude organization. You can review the link or unlink at any time under Linked platforms in the Claude Console, or unlink from Organization settings in ClickHouse Cloud.

## What ships {#what_ships}

* Anthropic bills Claude API usage in ClickHouse Agents and AI Functions directly to your Claude organization, on your existing terms.   
* Requests go to Anthropic directly and run in ClickHouse’s organization on Claude Platform. ClickHouse’s organization settings apply, including data retention, rate limits and enabled features. Your Claude organization’s settings, such as zero data retention (ZDR), IP allowlists, and encryption keys, do not carry over.  
* You can set a monthly spend limit when you link and change it at any time in the Claude Console. Your organization-wide limit also applies.  
* The Claude Console shows this month’s spend through ClickHouse Cloud and the full link history.

ClickHouse is building the open platform for AI. You choose the models, agents, and MCP clients, and they run where your data already lives. Linked billing extends that flexibility to how you pay. If your organization already has a Claude organization, you can link it to ClickHouse Cloud without opening a second account or managing a new API key.

## Who can use it {#who_can_use_it}

Ask your ClickHouse account team to enable linked billing. You need the Admin role in ClickHouse Cloud and the Owner, Admin or Billing role in your Claude organization. While linked billing is enabled, ClickHouse Cloud serves Claude models only. The full requirements are in the [linked billing docs](https://clickhouse.com/docs/products/cloud/features/ai-ml/linked-billing-claude-platform). 

## How to link {#how_to_link}

1. In ClickHouse Cloud, open Organization settings and click **Link your Claude organization** in the Claude organization section.  
2. Choose the Claude organization to link.  
3. Review how billing works and click **Continue**.  
4. Set a monthly spend limit, or click **Continue** without a limit.  
5. Click **Link and authorize**.  
6. Back in ClickHouse Cloud, the section shows **Linked**.

To unlink, click Unlink in Organization settings.

## Resources {#resources}

* [Linked billing docs](https://clickhouse.com/docs/products/cloud/features/ai-ml/linked-billing-claude-platform)   
* [ClickHouse Agents docs](https://clickhouse.com/docs/products/cloud/features/ai-ml/agents)  
* [AI Functions docs](https://clickhouse.com/docs/reference/functions/regular-functions/ai-functions) and [private preview sign-up](https://clickhouse.com/cloud/ai-functions-and-inference-services-waitlist)


---

## Get started today

Interested in seeing how ClickHouse works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-3057-get-started-today-sign-up&utm_blogctaid=3057)

---