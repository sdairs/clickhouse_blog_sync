---
title: "Postgres wait events, now in Query Insights"
date: "2026-10-19T11:15:28.796Z"
author: "Amog Iska"
category: "Product"
excerpt: "Query Insights for ClickHouse Managed Postgres now shows what active sessions are waiting on, with wait event breakdowns, blocked-session and lock-wait charts, and the same metrics in Prometheus."
---

# Postgres wait events, now in Query Insights

## What’s new and why it matters {#whats_new_and_why_it_matters}

We introduced [Query Insights](https://clickhouse.com/blog/postgres-query-insights-clickhouse-cloud) to help you find expensive queries and understand the CPU, reads, and writes behind them. But finding a slow query is only part of the picture. The database may be spending its time on disk I/O, waiting on a lock, or simply busy on CPU. Query Insights for ClickHouse Managed Postgres now includes wait event metrics, so you can see what active sessions are waiting on and how that changes over time. The breakdowns show the average number of active sessions per wait category and each category’s share of total load. Alongside your query and resource metrics, this helps you narrow down what to investigate next.

## Inspect wait events and their share of load {#inspect_wait_events_and_their_share_of_load}

In Query Insights, the **Active sessions by wait type** chart groups activity on your primary by `wait_event_type`. Each bar shows the average number of active client sessions over that interval, split into categories such as `IO` and `Lock`. For details on what each wait type and event means, see the [PostgreSQL documentation](https://www.postgresql.org/docs/current/monitoring-stats.html#WAIT-EVENT-TABLE).

In the chart below, lock waits account for the largest share of activity, followed by Timeout and CPU. Here, CPU means a session is active with no reported wait event; it is not a direct measurement of CPU utilization.

![](https://clickhouse.com/uploads/pg_wait_events_oct2026_image1_c33c76b4ba.png)

If you want a closer look, hover over any bar to see the specific events driving each wait type.

![](https://clickhouse.com/uploads/pg_wait_events_oct2026_image2_07f8d702ea.png)

The highlighted interval has 25 average active sessions, with 13 waiting on locks. The tooltip breaks those lock waits down further: 4.5 for `tuple`, 3.5 for `transactionid`, 3 for `relation`, and 2 for `advisory`.

Click the card to open the **Waits** table. Here you’ll find the individual `wait_event` values, their average active sessions, and their share of the total load.

![](https://clickhouse.com/uploads/pg_wait_events_oct2026_image3_5310ee8cfc.png)

Across the selected range, the four `Lock` rows add up to about 42% of the load. Relation locks account for 15.2% and tuple locks for 12.4%, making them the largest contributors within that category.

## Understand lock contention with two additional metrics {#understand_lock_contention_with_two_additional_metrics}

Two charts sit next to the wait breakdown. **Blocked sessions** show the average number of sessions waiting on locks. **Lock wait time** reports how long those sessions had been waiting when sampled, with p50, p95, and maximum values.

![](https://clickhouse.com/uploads/pg_wait_events_oct2026_image4_1ca95ec813.png)

In these charts, roughly 9 to 12 sessions are blocked through much of the busy period, peaking at about 13. Maximum lock waits repeatedly rise above 100 seconds, while p50 stays below 10 seconds. Together, the charts show how many sessions are affected and how long they’ve been held up.

## Monitor through Prometheus {#monitor_through_prometheus}

We recently added [Query Insights metrics](https://clickhouse.com/docs/products/managed-postgres/monitoring/metrics) to the Managed Postgres Prometheus endpoint. That includes query counts and total execution time for calculating throughput and **average latency**, as well as **failed queries**, **rows returned or affected**, **buffer activity**, and **WAL generation**. Counts are split by operation, so you can follow changes in read and write traffic.

Wait events are available through Prometheus too. You can graph **active sessions by wait event** and **maximum lock wait time** next to your query metrics in Grafana, and alert on persistent lock contention.

The [Prometheus integration guide](https://clickhouse.com/docs/products/managed-postgres/monitoring/prometheus) covers authentication and scrape configuration. This allows you to build custom dashboards and alerting pipelines that fit your needs.

## Investigate with ClickHouse Agents {#investigate_with_clickhouse_agents}

[ClickHouse Agents](https://clickhouse.com/blog/clickhouse-agents-managed-postgres) can look at wait events alongside slow query patterns and service metrics to help you decide what to investigate. Try asking:

> What is my Postgres database waiting on, and what should I investigate next?

Here is an example of ClickHouse Agents debugging wait events:

<video autoplay="1" muted="1" loop="1" controls="0">
  <source src="https://clickhouse.com/uploads/pg_wait_events_oct2026_agents_demo_71d67c8d5c.mp4" type="video/mp4" />
</video>

## Give it a try {#give_it_a_try}

You’ll find the new charts in Query Insights in your Managed Postgres service. See the [documentation](https://clickhouse.com/docs/products/managed-postgres/monitoring/query-insights) for more on Query Insights.

[Try it out](https://clickhouse.com/cloud/postgres), and let us know what you think.

---

## Get started with ClickHouse Managed Postgres today

Interested in seeing how ClickHouse Managed Postgres works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?intent=pg&loc=blog-cta-2739-get-started-with-clickhouse-managed-postgres-today-sign-up&utm_blogctaid=2739)

---