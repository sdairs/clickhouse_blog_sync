---
title: "What’s new in the ClickHouse Grafana plugin"
date: "2026-08-13T16:14:40.296Z"
author: "Alex Fedotyev"
category: "Engineering"
excerpt: "ClickHouse Grafana plugin 4.20 brings compact query mode, click-to-filter log investigation, guided variable and annotation editors, and OpenTelemetry dashboards"
---

# What’s new in the ClickHouse Grafana plugin


In the spring, I wrote about [where we wanted to take the ClickHouse Grafana plugin](https://clickhouse.com/blog/grafana-plugin-vision). A good share of that has now shipped. The recent work, which was done in close partnership with Grafana Labs, has focused on making the common cases of finding a log line, narrowing to one service, or detecting a deployment, faster without SQL, while always ensuring full SQL is just one click away for more advanced needs.

## Contributors {#contributors}

As always, thank you to our open source contributors and users who help improve the plugin for everyone.

[aangelisc](https://github.com/aangelisc), [adamyeats](https://github.com/adamyeats), [akkikumar72](https://github.com/akkikumar72), [alyssajoyner](https://github.com/alyssajoyner), [bossinc](https://github.com/bossinc), [fabrizio-grafana](https://github.com/fabrizio-grafana), [fleon](https://github.com/fleon), [hkrutzer](https://github.com/hkrutzer), [itsgareth](https://github.com/itsgareth), [itsmylife](https://github.com/itsmylife), [iwysiu](https://github.com/iwysiu), [karl-power](https://github.com/karl-power), [katebrenner](https://github.com/katebrenner), [lwandz13](https://github.com/lwandz13), [MattiasMTS](https://github.com/MattiasMTS), [mattvella07](https://github.com/mattvella07), [Orenico10](https://github.com/Orenico10), [SaiPrasanna9](https://github.com/SaiPrasanna9), [stackempty](https://github.com/stackempty), [Tarasusrus](https://github.com/Tarasusrus)

When working on the user experience, our efforts are focused on optimizing for the common adoption path that we see our users take - sending OpenTelemetry logs and traces into ClickHouse, as well as increasingly metrics, using the [ClickHouse exporter for the OpenTelemetry Collector](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/exporter/clickhouseexporter), before reaching for Grafana to investigate. 

The query builder has always been part of the plugin since v1, but for someone new, or for a user looking to quickly filter events, design inefficiencies meant it was often faster to drop into writing ClickHouse SQL by hand. The recent work has focused on making the common cases of finding a log line, narrowing to one service, or detecting a deployment, faster without SQL, while always ensuring full SQL is just one click away for more advanced needs. We’ve linked the pull request behind each feature so you can dig in.

## Search first, SQL one click away {#search_first_sql_one_click_away}

If you’ve just got a table with logs in it, configuring the datasource shouldn’t be complicated. Single-table mode ([#1832](https://github.com/grafana/clickhouse-datasource/pull/1832)) is designed for exactly that use case. Point the datasource at your table, confirm its columns, and the editor gets out of your way - giving you a simpler, more focused experience.

![grafana_aug2026_image6.png](https://clickhouse.com/uploads/grafana_aug2026_image6_4cbd16c154.png)

<p style='text-align: center; font-style: italic;'>Single table configuration mode</p>

With single-table mode configured, compact query mode ([#1841](https://github.com/grafana/clickhouse-datasource/pull/1841)) replaces the full builder with a more focused experience: type a log message and the plugin writes the query for you, while type-aware filters, query history, and a live SQL preview help you refine it. The generated SQL is always available to copy or edit directly.

While the compact editor is currently scoped to single-table configurations, this aligns perfectly with common Grafana patterns where users create dedicated data sources for specific log or trace streams. For example, you could easily create "Logs - Prod", "Logs - Staging" and so on. This approach not only provides a focused experience; to try it, simply create a targeted datasource for your specific table, open Explore, and let us know how it works for your workflow.

![grafana_aug2026_image4.png](https://clickhouse.com/uploads/grafana_aug2026_image4_8e21d4030f.png)

<p style='text-align: center; font-style: italic;'>Compact query mode in Explore, with the search box, type-aware filters, query history, and the live SQL preview</p>

*Note*: Early users provided feedback that they would like the ability to show custom fields/columns for their logs in the compact mode, whether for those using the OpenTelemetry or custom schema e.g. Query logs. This has been addressed by a new improvement under PR [#2108](https://github.com/grafana/clickhouse-datasource/pull/2108), and will be included in the next plugin build.

## Investigate by clicking, not typing {#investigate_by_clicking_not_typing}

Most investigations are iterative: you start with a search, inspect the results, and then narrow or widen them by applying and removing filters. The latest plugin improvements let you follow that flow by clicking, without needing to edit the SQL. 

Expanded log rows now organize OpenTelemetry attributes into collapsible Resource, Scope, and Log sections ([#1829](https://github.com/grafana/clickhouse-datasource/pull/1829)). From there, you can filter for or filter out any value; applied filters are highlighted, and clicking one again removes it ([#1824](https://github.com/grafana/clickhouse-datasource/pull/1824)). You can also select text within a log message and filter on that substring directly ([#1738](https://github.com/grafana/clickhouse-datasource/pull/1738)).

![grafana_aug2026_image3.png](https://clickhouse.com/uploads/grafana_aug2026_image3_3ed6aa15e5.png)

<p style='text-align: center; font-style: italic;'>Filter on the text highlight to filter</p>

Additionally, for dashboards, ad hoc filters can now discover keys and values within ClickHouse Map columns and can apply filters across multiple tables ([#1793](https://github.com/grafana/clickhouse-datasource/pull/1793), [#1757](https://github.com/grafana/clickhouse-datasource/pull/1757)). Aliases and OpenTelemetry Map keys are resolved consistently whether you add a filter by clicking or through the query builder.

![grafana_aug2026_image5.png](https://clickhouse.com/uploads/grafana_aug2026_image5_a1ac926f0c.png)

## Out-of-the-box dashboards - useful the moment you connect {#outofthebox_dashboards_useful_the_moment_you_connect}

As OpenTelemetry rises as the industry standard for collecting and storing logs and traces, ClickHouse has been uniquely tuned to handle that data at scale. To ensure you can derive immediate value from this data, the plugin now includes three OpenTelemetry dashboards out of the box ([#1869](https://github.com/grafana/clickhouse-datasource/pull/1869)): a Logs Explorer, a Traces Explorer, and a per-service deep dive that ties logs and traces together. 

These panels are fully interactive with filters, annotations, log samples panels per each service and similarly KPIs and top errors for traces and service dashboards.

![grafana_aug2026_image2.png](https://clickhouse.com/uploads/grafana_aug2026_image2_8cae5f8d2c.png)

## Less SQL for dashboard scaffolding {#less_sql_for_dashboard_scaffolding}

Building richer dashboards often means adding variables and annotations, but until now both required users to write the underlying SQL. That added unnecessary complexity to common tasks such as making a dashboard filterable or marking deployments on a chart.

The new annotation editor ([#1922](https://github.com/grafana/clickhouse-datasource/pull/1922)) provides a guided experience: select a column to monitor, such as `service.version`, and the plugin generates the change-detection SQL automatically. This allows both changes and reversions to be easily detected, allowing deployments and rollbacks to appear as separate markers. The guided variable editor ([#1868](https://github.com/grafana/clickhouse-datasource/pull/1868)) works similarly: choose a column, including a key within a Map column, and it generates the SQL needed to retrieve its distinct values. In both editors, the generated SQL remains visible and editable, and any changes you make take precedence.

![grafana_aug2026_image7.png](https://clickhouse.com/uploads/grafana_aug2026_image7_25d8a06d13.png)

<p style='text-align: center; font-style: italic;'>The annotation editor’s change-detection preset and the guided variable editor</p>

---

## Get started today

Interested in seeing how ClickHouse works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-1537-get-started-today-sign-up&utm_blogctaid=1537)

---


## Try it {#try_it}

To try the plugin, make sure you're on version 4.20 or later of the [ClickHouse data source](https://grafana.com/grafana/plugins/grafana-clickhouse-datasource/) (install or update it from the Grafana plugin catalog), then point a data source at your OpenTelemetry tables. 

The principle behind all of these improvements is the same one we set out in the spring: common tasks shouldn’t require SQL, but SQL should always be one click away when you need it. If you use ClickHouse with Grafana, the most valuable feedback you can give us is where the experience still gets in your way. Compact query mode is intentionally starting with single-table data sources so we can learn from real-world usage before taking it further.

## Appendix: everything else that shipped {#appendix_everything_else_that_shipped}

Not every improvement warrants a headline. Many of these changes are small on their own, but together they make the plugin faster, more reliable, and easier to use.

1. **A smarter builder.** Conventional log columns are detected automatically ([#1791](https://github.com/grafana/clickhouse-datasource/pull/1791)); tooltips link directly to relevant documentation ([#1790](https://github.com/grafana/clickhouse-datasource/pull/1790)); and a shared schema picker now powers the builder, variable editor, and annotation editor ([#1828](https://github.com/grafana/clickhouse-datasource/pull/1828)). Time columns are also combined into a single `ORDER BY` ([#1695](https://github.com/grafana/clickhouse-datasource/pull/1695)) for better primary key usage. Explore can show raw log samples beneath metrics charts ([#1744](https://github.com/grafana/clickhouse-datasource/pull/1744)), and attribute columns can use JSON as well as Map types ([#1866](https://github.com/grafana/clickhouse-datasource/pull/1866)).  
2. **Better performance.** Schema introspection is cached per datasource ([#1787](https://github.com/grafana/clickhouse-datasource/pull/1787)), while fast trace-ID lookup is no longer tied to OpenTelemetry mode ([#1786](https://github.com/grafana/clickhouse-datasource/pull/1786)).  
3. **Grafana 13 readiness.** Compatibility work clears the path to Grafana 13 without changing behaviour on Grafana 11.6 or 12.x ([#1861](https://github.com/grafana/clickhouse-datasource/pull/1861), [#1863](https://github.com/grafana/clickhouse-datasource/pull/1863)).  
4. **Greater reliability.** Span links open the correct linked trace ([#1890](https://github.com/grafana/clickhouse-datasource/pull/1890)), and SQL validation now uses a port of ClickHouse's own lexer ([#1778](https://github.com/grafana/clickhouse-datasource/pull/1778)).  
5. **Self-observability.** The plugin backend is instrumented with OpenTelemetry, with a machine-readable contract for its spans ([#1734](https://github.com/grafana/clickhouse-datasource/pull/1734), [#1735](https://github.com/grafana/clickhouse-datasource/pull/1735)).  
6. **Attribution and identity.** When header forwarding is enabled, queries can carry the Grafana user’s identity into ClickHouse for row policies, quotas, and query-log attribution ([#1797](https://github.com/grafana/clickhouse-datasource/pull/1797)). This release also adds foundational support for Grafana’s SQL abstractions ([#1756](https://github.com/grafana/clickhouse-datasource/pull/1756)).
