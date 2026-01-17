---
title: "From text to charts: a faster way to visualize with ClickStack"
date: "2025-10-22T11:41:42.689Z"
author: "ClickStack Team"
category: "Product"
excerpt: "Discover how ClickStack’s new text-to-chart feature makes analyzing logs, traces, and metrics effortless - turning plain text into instant observability visualizations that speed up root cause analysis."
---

# From text to charts: a faster way to visualize with ClickStack

![clickstack-text-to-chart.png](https://clickhouse.com/uploads/clickstack_text_to_chart_1ec8213e10.png)

ClickStack's new text-to-chart feature makes analyzing observability data simpler than ever. Whether you're working with logs or traces, ClickStack lets you create charts just by describing them. No menus, no dropdowns - just type what you want to see and get instant visualizations that accelerate your path to root cause analysis.

Over the last year, large language models have started finding their way into observability tools, helping users move faster and spend less time on repetitive work. With ClickStack, we're now bringing that same convenience to data visualization.

[ClickStack](https://clickhouse.com/docs/use-cases/observability/clickstack/overview) is a high-performance observability stack that aims to democratize access to ClickStack for everyone. It brings the power, speed, and flexibility of ClickHouse to logs, metrics, and traces - all in an open-source package that anyone can use. This new feature continues that mission by making ClickStack even easier to use. 

![simple_text_to_chart.gif](https://clickhouse.com/uploads/simple_text_to_chart_49ec63e8ed.gif)

## Describe your chart, and we'll build it

Want to see error rates by service over the last 24 hours? Just type it out. Need a latency breakdown by endpoint? Describe it, and the chart appears.

ClickStack takes your text prompt, converts this to a query using an LLM, and automatically builds the corresponding visualization. It's fast, intuitive, and designed to get you from idea to insight in seconds.

This kind of natural-language chart generation first emerged in business intelligence tools, but it's now proving just as useful in observability. When you're exploring logs, traces, or metrics, being able to instantly visualize patterns can make it much easier to spot anomalies and understand what's really happening in your systems.

<div class="my-6"><div class="rounded-lg bg-white/10 p-4"><h3 class="text-inherit undefined Typography_suiTitleh3__JlLe2  group/mdHeader toc-ignore" id="test">Get started with ClickStack
</h3><p>Ready to explore the world's fastest and most scalable open source observability stack? Start locally in seconds.</p><a class=" w-full" target="_self" href="https://clickhouse.com/docs/use-cases/observability/clickstack/getting-started?loc=blog-o11y-global-cta&amp;utm_source=clickhouse&amp;utm_medium=web&amp;utm_campaign=blog"><button class="styles_button__3smpn mt-6 w-full font-medium" data-type="primary"><span class="flex items-center whitespace-nowrap">Start exploring</span></button></a></div></div>


## Trying it out

Enabling the text-to-chart just requires an Anthropic API key. Set the environment variable `ANTHROPIC_API_KEY`, and ClickStack will enable the feature.

The quickest way to get started and experiment with the feature, is with our [local-only Docker image ](https://clickhouse.com/docs/use-cases/observability/clickstack/deployment/hyperdx-only)specifying the key via the `-e` flag.

```bash
docker run -p 8080:8080 docker.hyperdx.io/hyperdx/hyperdx-local -e ANTHROPIC_API_KEY='<YOUR KEY>'
```

Note that this Docker image is intended for quick experimentation, not production use. Authentication is disabled in the local image, which makes it perfect for testing new features but unsuitable for live environments.

For feature testing, connect to our [public demo environment](https://play-clickstack.clickhouse.com/). Launch HyperDX locally at localhost:8080, click `Connect to Demo Server` and you'll automatically have access to a live stream of logs, traces, and metrics for our OTel demo environment.

![hyperdx_demo.png](https://clickhouse.com/uploads/hyperdx_demo_f562ea040d.png)

Once you're connected, head over to the **Chart Explorer**. At the top, you'll find the **AI Assistant** ready to help you describe and generate charts instantly. Just select a data source and try a few prompts, and see how fast you can go from text to visualization.

In the example below, we generate charts for the logs and traces based only on some simple text prompts.

![text_to_chart.gif](https://clickhouse.com/uploads/text_to_chart_6b73d46e08.gif)

## What's next

Currently, the feature relies on users having an Anthropic account. Future iterations of the feature will support other LLM providers, including OpenAI.

This is also one of several AI-based features we're building to make ClickStack more intuitive and productive. We're just getting started, and there's plenty more to come that will make exploring your observability data even faster and more powerful.
