---
title: "More Visibility, Less Guesswork: ClickHouse Cloud's New Monitoring Capabilities"
date: "2026-03-25T21:17:28.529Z"
author: "Mihir Gokhale"
category: "Product"
excerpt: " ClickHouse Cloud's new monitoring capabilities give platform administrators deeper visibility into their deployments, with a unified   Overview page, infrastructure scaling insights, and automatic email and Slack notifications for common issues."
---

# More Visibility, Less Guesswork: ClickHouse Cloud's New Monitoring Capabilities

ClickHouse gives users an incredible amount of control to optimize database performance. Platform administrators sit at the center of this experience: they tune scaling controls, configure server settings, and ultimately own the health of their deployment. On ClickHouse Cloud, we're releasing a set of improvements designed to give deeper visibility into how the ClickHouse server is behaving to proactively surface warnings before they become problems.

<h2 id="more-dashboards">More dashboards</h2>

The ClickHouse Cloud console already comes built-in with several monitoring dashboards. We added a few more.

<h3 id="new-overview-page">New overview page</h3>

The new Overview page brings the most important signals about your deployment into a single, unified view. Designed to give administrators an at-a-glance health check of their ClickHouse environment, you can now spend less time hunting for information and more time acting on it.

<h3 id="infrastructure-page-deeper-scaling-visibility">Infrastructure page: Deeper scaling visibility</h3>

The new Infrastructure page gives administrators a clearer view into how their services are scaling over time. CPU and Memory utilization metrics, now with additional aggregation types, show how much utilization your ClickHouse cluster is getting.

New modals showcase ClickHouse's [automatic scaling](https://clickhouse.com/docs/manage/scaling) behavior to help users better understand why and how their cluster scaled, and also make better decisions around custom scaling configurations like vertical scaling limits and idling behavior.

![](https://clickhouse.com/uploads/clicklens_mar2026_image1_621e99285e.png)

<h2 id="get-ahead-of-issues-with-new-notifications">Get ahead of issues with new notifications</h2>

When users onboard onto ClickHouse, a common set of issues frequently come up. Administrators will be automatically notified via email when a service is at risk of degraded performance or failures, including due to:

* **Too many parts**: a common cause of merge pressure and query slowdowns
* **Failed mutations**: which can silently stall data changes if left undetected
* **Query concurrency**: helping you catch saturation before high query concurrency impacts end users

<h3 id="slack-notifications">Slack notifications</h3>

You can configure all these notifications, and more, to be sent directly to Slack via your organization's notification settings.

These improvements provide administrators with better visibility into ClickHouse behavior, so you can spend less time diagnosing issues and more time optimizing your performance.

These features are being rolled out now in ClickHouse Cloud. Log in to your console to explore the new dashboards and configure your notification preferences.


---

## Get started today

Interested in seeing how ClickHouse works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-271-get-started-today-sign-up&utm_blogctaid=271)

---