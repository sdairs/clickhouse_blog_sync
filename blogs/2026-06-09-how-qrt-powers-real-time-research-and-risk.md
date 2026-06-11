---
title: "How QRT powers real-time research and risk management at petabyte scale"
date: "2026-06-09T15:52:52.319Z"
author: "ClickHouse"
category: "User stories"
excerpt: "How QRT, a cloud-native quantitative investment manager, uses ClickHouse Cloud and ClickStack to power firm-wide research, real-time risk and P&L, and observability at petabyte scale."
---

# How QRT powers real-time research and risk management at petabyte scale

## Summary

* QRT, a global investment manager, uses ClickHouse Cloud to power a data platform serving researchers, as well as a real-time risk and P&L system. 
* Beyond supporting researchers, ClickStack is also the foundation for QRT's observability infrastructure.

Quantitative trading is, at its core, a data challenge. Funds seek to store more of it, query it faster, and act on it first.

[Qube Research & Technologies (QRT)](https://www.qube-rt.com/) is a global quantitative investment manager headquartered in London. The firm's decision to use [ClickHouse Cloud](https://clickhouse.com/cloud) reflects a philosophy that dates back to the firm's origins. Most hedge funds founded in the 1990s and 2000s run on-premise data centers built up over decades. But QRT, launched in 2018 amid a rapid spinout of Credit Suisse's proprietary trading arm, was originally built in the cloud. Rather than inheriting legacy on-premise infrastructure, it built itself cloud-native from day one.

## Built for the cloud, ready to scale

QRT uses [ClickHouse Cloud](https://clickhouse.com/cloud) across two of their major systems. One centralized platform that gives researchers across the firm access to the data they need to develop trading strategies, and another near real-time risk monitoring, management, and P&L system.

"We wanted something faster and much more scalable," says a senior engineer on the team. "With our previous database, we were limited by the number of writers, the number of readers, and the total load per cluster. With ClickHouse, we don't have those limitations."

Beyond supporting researchers, ClickHouse is also the foundation for QRT's observability infrastructure. The migration to [ClickStack](https://clickhouse.com/clickstack), ClickHouse's integrated observability stack, consolidated logs, metrics, and traces onto a single backend for the first time. Alerts, log queries, and metric aggregations that used to require managing multiple systems now run against a single ClickHouse instance using standard SQL. "Having all our monitoring on one backend gives us the simplicity to maintain and is reliably fast," says the QRT engineer.

---

## Get started today

Interested in seeing how ClickHouse works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-828-get-started-today-sign-up&utm_blogctaid=828)

---