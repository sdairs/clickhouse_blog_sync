---
title: "We taught ClickStack to read your logs like a detective novel"
date: "2026-04-02T08:49:37.240Z"
author: "The ClickStack Team"
category: "Engineering"
excerpt: "ClickStack gets a literary upgrade with \"AI Summarize\", transforming raw logs into vivid, story-driven narratives that finally explain what's really happening in your systems."
---

# We taught ClickStack to read your logs like a detective novel

## We taught ClickStack to read your logs like a detective novel

If you've ever been paged at 3am and stared at a wall of `EmptyCartAsync called with userId=a0cd950c-39ec-11f0-8ddd-a2eca416a8a4` wondering what it means for the business -- you're not alone.

Logs are written by machines, for machines. Traces are trees of span with nanosecond timestamps. Log patterns are clusters of identical messages that tell you *something* is happening 113,526 times but won't tell you *why you should care*. The gap between raw telemetry and human understanding is where SRE time goes to die.

Today we're shipping **AI Summarize** -- a new feature in HyperDX that generates narrative summaries of your logs, traces, and log patterns. It works on any event in the side panel and on the pattern drawer. One click, and your cryptic span becomes a story.

## What It Looks Like

Open any log entry, trace span, or log pattern in HyperDX. You'll see a new **Summarize** button below the event body. Click it, and after a brief analysis you get something like this:

![april_fools_ai_clickstack_1.png](https://clickhouse.com/uploads/april_fools_ai_clickstack_1_112d4f71ce.png)

Or maybe you'll get David Attenborough narrating your checkout flow:

![april_fools_ai_clickstack_2.png](https://clickhouse.com/uploads/april_fools_ai_clickstack_2_2b7d270393.png)

Or Shakespeare lamenting your latency:

![april_fools_ai_clickstack_3.png](https://clickhouse.com/uploads/april_fools_ai_clickstack_3_01357825e5.png)

Hit **Regenerate** to get a new version. The theme adapts to context -- errors get Detective Noir, performance issues get Shakespearean Drama, and normal info events get the Nature Documentary treatment.

## It knows your stack

The summaries aren't random mad-libs. AI Summarize understands the OpenTelemetry and Kubernetes attributes already present in your telemetry -- service names, versions, HTTP endpoints, database systems, RPC calls, exceptions, pod names, namespaces, durations, and more. It reads what's there and weaves it into the narrative.

A 1ms Redis call gets *"extraordinarily swift -- the peregrine falcon of API calls, diving at breathtaking speed."* A checkout span that errors out with a cache exception gets *"Then I found the body -- the kind of exception that ends careers and starts postmortems."* A 5-second database query gets *"an age! Methinks the user doth grow weary, staring at the spinning wheel of fortune."*

The mood adapts too. Errors and exceptions trigger darker themes. Warnings get suspicious. Healthy spans get the nature documentary they deserve.

For **log patterns**, the summary incorporates the repeat count -- because a message that appears 113,526 times deserves to be called out:

*"Hark! A refrain most persistent: 'EmptyCartAsync called with &lt;*>'. 113,526 times it echoes through the cluster, like a chorus that hath forgotten how to stop."*

## Zero tokens. Zero data sharing. Zero cost.

Here's the part we're most proud of: **AI Summarize doesn't use any LLM.** There is no API call to OpenAI, Anthropic, or any other provider. No tokens are consumed. Your data never leaves the browser.

The summaries are generated entirely on the client side using hand-written phrase pools and OTel-aware data extraction. The "AI" in "AI Summarize" stands for "Artisanally Improvised."

This means:

* **No cost** -- works on every HyperDX deployment, open source or cloud, with no AI API key required
* **No privacy concerns** -- event data stays in your browser tab, never sent to a third-party model
* **No latency** -- the ~2 second "analysis" delay is theatrical, not computational
* **No hallucinations** -- every fact in the summary comes directly from your event attributes

Click the `(i)` icon next to any summary to see the disclosure. If the feature isn't for you, the same popover has a "Don't show again" link that persists via localStorage.

## Try it

**AI Summarize** is going live today in HyperDX. Open any log, trace, or pattern and look for the sparkle icon.

After the first week the button is hidden by default to keep the UI clean, but you can bring it back anytime by adding `?smart=true` to your HyperDX URL. It stays active through the end of April 2026.

We're also evaluating a version that uses actual AI on the backend -- the infrastructure is already in place. If you'd like to see real LLM-powered summaries as a permanent feature, let us know on [GitHub](https://github.com/hyperdxio/hyperdx) in [Slack](https://clickhousedb.slack.com/archives/C09GJFL66FK).

Happy April Fools! The joke is the delivery, not the feature. Every fact in the summary comes from your real OTel attributes. Every Kubernetes pod name is accurate. We just thought your 3am pages deserved better writing.

*"We are such stuff as spans are made on, and our little traces are rounded with a timeout."*
