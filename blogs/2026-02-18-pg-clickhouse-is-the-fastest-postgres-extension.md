---
title: "pg_clickhouse is the fastest Postgres extension on ClickBench"
date: "2026-02-18T11:46:55.753Z"
author: "David Wheeler"
category: "Product"
excerpt: "The pg_clickhouse extension minimizes the effort required to run typical analytics queries in Postgres by delegating execution to ClickHouse."
---

# pg_clickhouse is the fastest Postgres extension on ClickBench

In December 2025, we launched [pg_clickhouse](https://github.com/ClickHouse/pg_clickhouse), a PostgreSQL extension to query ClickHouse directly from Postgres. Its primary goal is to minimize the application migration effort required to move analytics workloads from Postgres to ClickHouse. In designing pg_clickhouse, we made deliberate architectural choices to ensure that you can continue to use the familiar Postgres interface for both transactional and analytical queries, while harnessing the full power of ClickHouse for analytics.

In this blog post, we examine those design choices and highlight their performance impact by benchmarking pg_clickhouse in [ClickBench](https://benchmark.clickhouse.com/).

## Query pushdown vs. shoehorning analytics into Postgres

We designed **pg_clickhouse** to minimize load on Postgres by offloading analytic execution as much as possible to ClickHouse. Instead of running heavy analytics inside Postgres and consuming its resources, it rewrites queries for execution in ClickHouse and only the results are returned, on a best-effort basis.

This architecture contrasts with most analytic extensions that embed columnar storage and analytic execution engines directly within Postgres. While those approaches can accelerate analytics, they still rely on Postgres resources and are ultimately constrained by a single shared node. As data volumes grow into the terabyte or tens-of-terabytes range, analytics workloads begin to compete with transactional workloads for the same system resources.

By delegating execution to ClickHouse, pg_clickhouse enables independent scaling and avoids resource contention within Postgres. This model especially enhances aggregation-heavy queries that scan millions or billions of rows. In this context, effective **query pushdown** is the central challenge, not just for filtering, but for aggregation in particular.

## pg_clickhouse is the fastest Postgres extension on ClickBench

To evaluate the impact of these design choices, we recently added pg_clickhouse to ClickBench, a standard benchmark for analytical DBMS.

As of the end of January, the results are in: ***pg_clickhouse is [the fastest PostgreSQL extension](https://benchmark.clickhouse.com/#system=+gkus|_b|pnc|saB&type=-&machine=-ca2l|6t|g4e|6ax|ae-l|6ale|g-l|3al&cluster_size=-&opensource=-&hardware=+c&tuned=+n&metric=combined&queries=-), outperforming all other Postgres analytics extensions, performing only slightly slower than native ClickHouse itself.*** Across all 42 ClickBench queries, on both ARM64 (c8g) and AMD64 (c6a) instances, performance closely tracks ClickHouse.

![Screenshot comparing the ClickBench performance of pg_clickhouse to ClickHouse on both arm64 (c8g) and amd64 (c6a) servers.](https://clickhouse.com/uploads/clickbench_2026_02_02_c689143402.png)

These results confirm that pg_clickhouse pushes down full query execution to ClickHouse. The only measurable overhead comes from rewriting queries, the network round-trip, and converting the results to Postgres. Postgres does not execute the analytical workload itself; it acts purely as a routing and result layer.

## Comprehensive aggregate and expression pushdown

ClickBench relies a relatively simple schema: a single denormalized table with no `JOIN`s. While this avoids join pushdown complexity, it highlights something equally important: *comprehensive aggregate and expression pushdown.*

The benchmark exercises a broad range of operations that pg_clickhouse fully entrusts to ClickHouse, including:

*   `COUNT()`, `SUM()`, `AVG()`, `COUNT(DISTINCT)`
*   `MIN()`, `MAX()`
*   `GROUP BY`
*   `ORDER BY` (including `ORDER BY COUNT()`)
*   `HAVING`
*   `EXTRACT()`, `DATE_TRUNC`
*   Date comparisons
*   `LIKE`, `REGEXP_REPLACE()`
*   `CASE WHEN`

These represent only a subset of the aggregates, functions, and expressions currently supported. We continue to expand coverage, document supported patterns, and close remaining gaps, most recently in [yesterday's 0.1.4 release](https://github.com/ClickHouse/pg_clickhouse/releases/tag/v0.1.4).

And we're not stopping here. Work is already underway to support more complex query shapes, including subqueries and [CTEs](https://www.postgresql.org/docs/current/queries-with.html). We'll share more on these improvements in the coming months.

## Get Started

To start using **pg_clickhouse**, you can try the open-source version through [this quickstart guide](https://github.com/ClickHouse/pg_clickhouse/blob/main/doc/tutorial.md). **pg_clickhouse** also comes included in our [managed Postgres service](https://clickhouse.com/cloud/postgres).

---

## Try Postgres managed by ClickHouse

ClickHouse + Postgres has become the unified data stack for applications that scale. With Managed Postgres now available in ClickHouse Cloud, this stack is a day-1 decision.

[Get access](https://clickhouse.com/cloud/postgres?loc=blog-cta-67-try-postgres-managed-by-clickhouse-get-access&utm_blogctaid=67)

---