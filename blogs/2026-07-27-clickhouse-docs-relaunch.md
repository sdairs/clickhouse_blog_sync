---
title: "ClickHouse docs relaunch"
date: "2026-07-27T17:23:55.068Z"
author: "Shaun Struwig, Dominic Tran and Alexey Milovidov"
category: "Engineering"
excerpt: "We have relaunched clickhouse.com/docs on Mintlify, with a redesigned search and Ask AI experience, a docs MCP server, simpler navigation, an interactive API playground, and expanded localization — built for both human readers and the coding agents"
---

# ClickHouse docs relaunch

At ClickHouse, we believe that our developer documentation is a product, and we are always looking for ways to improve it for our customers and the open-source community. 

Today, we’re announcing a refresh of [clickhouse.com/docs](http://clickhouse.com/docs) on Mintlify, [the intelligent knowledge platform](https://www.mintlify.com/) serving tens of millions of developers each month, and powering help centers, support centers, and developer documentation sites for companies like Anthropic, Microsoft, Coinbase, Perplexity, and now also ClickHouse.

## Why have we migrated platforms? {#why-have-we-migrated-platforms}

The developer documentation space has seen a huge amount of change in the past year alone. Today, more than half of developer docs traffic comes from coding agents, rather than from humans alone. This shift has meant that the requirements for what a documentation site should do have also changed. While our previous platform, Docusaurus, had served us well for many years, it was designed for an exclusively human audience in mind, long before “Agents” had taken over our terminals.

We’ve partnered with Mintlify for our new documentation site because the platform was designed from the ground up with both humans and agents in mind. The move to the new platform allows us to provide a higher-quality developer docs experience to you, iterate faster, and focus on what we’re really passionate about - which is ensuring we provide the best documentation experience we can for you.

## What’s changed? {#whats-changed}

### Improved search experience & agent accessibility

When you arrive on the new docs, you’ll be greeted with a new landing page and shiny new UI. Placing search and Ask AI front and center is a conscious choice to embrace changing access patterns and help you to find the answers you’re looking for more quickly. You can now search across our docs, blog, and even GitHub issues, or Ask AI for more curated responses to your questions.

For users who want to point their agents directly at the docs for up to date answers, we’ve included instructions and one click commands on the landing page to set up the docs MCP server with built-in tools to search across the site, reads and navigates your site’s virtual filesystem using shell-style commands, and provide feedback to our team when an agent finds a page that is incorrect, outdated, confusing, or incomplete.

Setting up the docs MCP server with Claude Code is as easy as running the following command from the terminal:

<pre><code type='click-ui' language='bash'>
claude mcp add --transport http clickhouse-docs https://clickhouse.com/mcp --scope user
</code></pre>

The site now automatically detects when an agent is making a request, and will serve markdown rather than HTML to the agent to process content faster and with fewer tokens.

### Simpler information architecture

Common user feedback we received in the past was that they found the docs difficult to navigate because the top nav featured various multi-level dropdowns for different product surfaces and user goals. In the new site, we’ve simplified the navigation, breaking out documentation for core database functionality common to both Open Source ClickHouse and ClickHouse Cloud, from Cloud-specific product documentation.

You’ll find the core database documentation organized into sections based on what it is you’re trying to achieve:

- [**Get started**](https://clickhouse.com/docs/get-started): This section contains a new quick start explorer section, migration guides, install instructions, and sample datasets to explore.  
- [**Concepts**](https://clickhouse.com/docs/concepts): In this section, you’ll find fundamental concepts, core product feature overviews, and best practices to help you get the most out of ClickHouse  
- [**Guides**](https://clickhouse.com/docs/guides/clickhouse): Here you'll find long-form content to help you achieve a specific goal or apply ClickHouse to a particular use case.  
- [**Reference**](https://clickhouse.com/docs/reference/home): In this section, you’ll find reference docs for functions, settings, data types, formats, table engines, etc.

Documentation for specific ClickHouse solutions like Cloud, ClickStack, Managed Postgres, are now found under the “Solutions” tab, and follow a similar organisational pattern, and we’ve split our integrations docs into 3 separate sections for ClickPipes, Language Clients, and connectors.

Structuring the docs with clear user goals in mind across different areas of our product surface positions us to provide a more consistent docs experience for you.

### API playground

Users of our API docs will remember being directed to a different platform. That’s no longer the case, and you can now access docs generated from our OpenAPI spec directly in the docs for both [Cloud](https://clickhouse.com/docs/products/cloud/api-reference/organization/get-list-of-available-organizations) and [ClickStack](https://clickhouse.com/docs/clickstack/api-reference). If you click the “Try it” button in the API explorer, you can fill in your credentials and the site will securely show you the response from your ClickHouse service, allowing you to quickly explore our API without ever having to leave the browser.

### Usability improvements - for you, and for us

The Mintlify platform brings several usability improvements with it, both for you, and for us. Each page has an option to copy the page as markdown, to view the page’s markdown directly, and a quick link to set up the MCP server. We’ve also included the option to download a page as a .pdf for those of you that would like to do some reading offline.

We’ve had a feedback widget on our docs for quite some time, but the new platform brings quality-of-life improvements to how we track and action your feedback. We can now triage each piece of feedback, add our own comments, and track the status of each.

As a globally distributed remote-first company, we’re big users of Slack, and the addition of a Slack agent to make docs updates, along with a Notion-style visual editor, will help us move faster in updating the docs for you. We’re also looking forward to using Mintlify’s [automations](https://www.mintlify.com/docs/automations) feature for automatic content maintenance on our docs.

### Serving the community from a single repo

Active community members will know that our docs have historically been split across two repositories: ClickHouse/ClickHouse (for reference docs), and ClickHouse/clickhouse-docs (for guides, tutorials, product docs). We’ve now moved our docs back into our [core development repository](https://github.com/ClickHouse/ClickHouse/tree/master/docs). 

With agents relying on documentation as the source of truth, it’s now more important than it ever was to keep docs up to date with code changes. 

The move allows us to keep docs close to the code, and the engineers and community contributors who write that code - making it easier to catch docs drift with automated AI review. It also helps us to serve the community from a single place, without requiring an additional context switching step when you want to report an issue on the docs. And, it means that contributions to docs will now land your name in `system.contributors`, as contributions to the code do. 

Documentation is a highly valued, but often overlooked aspect of open source software, and it’s a great area to make a first contribution to ClickHouse. We are looking forward to seeing more first-time contributors step into the world of open source through a small, but no less appreciated, docs PR.

### Extended localization support

Our docs are currently made available in English, Japanese, Korean, Simplified-Chinese, and Russian. With the launch of the new site, we’ve extended localization support to Brazilian-Portuguese, Spanish, French, and Arabic. While we do our best to ensure LLM translations for these languages are of a high-standard, we welcome contributions from native-speakers of these languages in our community to improve their accuracy even further.

### Embedded documentation

**Contributed by Alexey Milovidov**

The ClickHouse 26.6 release introduces a major usability improvement for those most at home in the terminal: you can now search for and read reference documentation directly from your client. Type `help <topic>` or `\h <topic>` to view the docs instantly. The documentation is also available via [ClickHouse Reference](https://play.clickhouse.com/docs?user=play) or on your live server at `/docs`.

This is made possible with the introduction of a new system table: `system.documentation`. While some tables like `system.functions` and `system.settings` already had documentation embedded, there were some undocumented areas. New system tables have been added for table engines, database engines, formats, aggregate function combinators, dictionary layouts, dictionary sources, data skipping index types, and disk types - each now containing their respective documentation.

Watch Alexey give a demo of the feature in the [26.6 release call](https://www.youtube.com/live/-NmqMH9y4EY?si=ZAIEQmVVAOlii257&t=596).

## We’d love to hear your thoughts {#wed-love-to-hear-your-thoughts}

We’d love to hear your thoughts and feedback on the new site. You can reach our docs team via the feedback form (thumbs up, thumbs down buttons) at the bottom of every docs page, from the ‘raise an issue’ button at the bottom of every docs page, or directly via our [community slack](https://clickhouse.com/slack). Your feedback helps us greatly in building a better docs experience for you.  


---

## Get started today

Interested in seeing how ClickHouse works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-1412-get-started-today-sign-up&utm_blogctaid=1412)

---