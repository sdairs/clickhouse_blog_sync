---
title: "How Visa went from multi-day reporting to conversational analytics agents with ClickHouse Cloud and LibreChat"
date: "2026-06-24T15:12:01.773Z"
author: "ClickHouse"
category: "User stories"
excerpt: "Visa paired LibreChat with ClickHouse Cloud to build conversational BI agents on Authorize.net payments data, cutting multi-day reports to sub-second queries and reclaiming 8-10 hours per user each week."
---

# How Visa went from multi-day reporting to conversational analytics agents with ClickHouse Cloud and LibreChat

## Summary

* Visa used [ClickHouse Cloud](https://clickhouse.com/cloud) to build conversational BI agents on [Authorize.net](http://Authorize.net) payments data, letting teams query in natural language instead of writing SQL.   
* Pairing [LibreChat](https://www.librechat.ai/) with ClickHouse via the [ClickHouse MCP server](https://github.com/ClickHouse/mcp-clickhouse), the team turned multi-day reporting into sub-second answers over 40 PBs containing millions of rows.   
* Materialized views delivered roughly 50-70x faster analyses, reclaiming 8-10 hours per user each week while preserving Visa’s security and governance controls

"At Visa, we share a deep love of enterprise-scale data analytics," says Rafeeq Abdul, Senior Director of Engineering in the company's Authorize.net payments solution. "We've built a very strong partnership with ClickHouse over the past year-plus to enable a vision and deliver a strong analytics platform that powers business insights and drives business outcomes."

The partnership started in 2025 when Visa's observability team successfully migrated a major [application-logging use case](https://clickhouse.com/resources/engineering/log-monitoring) from Splunk to ClickHouse. That early win, built with open-source ClickHouse running on-premise, proved the database could handle petabyte-scale workloads at Visa's standards. The next step in their ClickHouse journey was moving beyond logs to the business data itself.

Rafeeq joined us at our [2026 Open House user conference](https://clickhouse.com/openhouse/) in San Francisco, where he shared how Visa used [ClickHouse Cloud](https://clickhouse.com/cloud) on AWS and LibreChat to build a conversational AI intelligence layer that delivers sub-second insights at scale, while respecting the key controls and governance principles within Visa's ecosystem.

## Deriving signals from the data

Authorize.net, a Visa solution, lets SMBs accept credit card and electronic payments online. The platform analyzes around $250 million in annual revenue across 2 million authorization events and 500,000 raw transactions, with a data footprint of roughly 40 petabytes that's growing by the day.

"The numbers here speak to the volume," Rafeeq says, "but they hide a story."

The story, as Rafeeq tells it, is what those numbers make possible. "Data is the fuel," he says. Value comes not from any one table but from the signals that emerge across them. Merchants, gateways, usage, APIs, segmentation, recommendations, attrition, revenue… each is a different lens on the same payments activity, all of it spread across hundreds of source tables in a multi-database topology, with individual queries scanning millions of rows.

And each signal, Rafeeq adds, matters to a different audience. Product managers need customer, usage, and attrition signals to understand how the product is being adopted. Visa's executives want concise revenue and trend summaries. And the product itself draws on the same data to power features and surface insights for customers.

## Why Visa chose ClickHouse Cloud

As Rafeeq explains, the long-standing challenge for Visa wasn't so much accessing the data as getting it fast enough to do anything about it. Legacy pipelines processed large volumes inefficiently, so daily, weekly, and monthly reports could take two to three days to produce. Getting an answer in the first place usually meant routing the question through a specialized data analyst with a multi-day turnaround time. By the time a report landed, the window to act on it had already closed.

"That's where we challenged ourselves to build a real-time platform that allows us to extract the business value and drive business outcomes by modernizing our data analytics stack fully native to the cloud," Rafeeq says.

They chose [ClickHouse Cloud](https://clickhouse.com/cloud) for a number of reasons. For one, Rafeeq says, it "completely offloaded" the burden of managing scale, letting the team bring infrastructure online with far less friction and keep their attention on outcomes. The [separation of storage and compute](https://clickhouse.com/docs/guides/separation-storage-compute) also gives them granular control over cost, with the ability to size unit cost to actual demand.

On performance and features, ClickHouse excelled at flat-table scans across hundreds of columns, proved enterprise-ready for BI integrations including Power BI, and offered state-of-the-art encryption and CMEK support. Rafeeq also highlights ClickHouse's excellent [compression and storage efficiency](https://clickhouse.com/docs/data-compression/compression-in-clickhouse), as well as its [vibrant and mature community](https://clickhouse.com/community), which combine to give the platform a "very solid foundation."

## Building conversational analytics agents with LibreChat and ClickHouse MCP

With ClickHouse Cloud as the backbone, the team built an interface that makes it usable by everyone. The solution pairs LibreChat, an open-source conversational AI interface [acquired by ClickHouse](https://clickhouse.com/blog/clickhouse-acquires-librechat), with the [ClickHouse MCP server](https://github.com/ClickHouse/mcp-clickhouse), which lets AI agents explore and run queries against data in ClickHouse Cloud.

The effect, as Rafeeq puts it, is to "evenly distribute knowledge across all users." Visa's internal teams don't have to be seasoned SQL engineers; they can ask questions in natural language (e.g. "show revenue risk by merchant segment") and all the complexity of joins and denormalization stays hidden behind the curtain.

The results speak for themselves, with sub-second queries over millions of rows. As Rafeeq puts it, "The multi-day process of turning raw data into useful insights has been squashed into milliseconds."

<video autoplay="1" muted="1" loop="1" controls="0">
  <source src="https://clickhouse.com/uploads/visa_librechat_B_fullres_crf32_c8c5d3438e.mp4" type="video/mp4" />
</video>

ClickHouse's [materialized views](https://clickhouse.com/docs/materialized-views), which pre-compute and incrementally update results as new data arrives, is a big reason for that performance. Different from other similar database approaches, materialized views in ClickHouse processes as inserts occur instead of a static time interval. In one example, a revenue analysis that scanned 500,000 rows in 2-3 seconds now reads from a 624-row materialized view in just 100 milliseconds, roughly 50 times faster. An approval analysis by card brands dropped from 2 million rows read in 3-5 seconds to a 29,000-row view in 100 milliseconds, about 70 times faster. And a merchant risk analysis that required a multi-table join and took 5-8 seconds now completes in 200 milliseconds from a pre-joined view, about 30 times faster.

> "Every signal matters to someone making a critical business decision, and those decisions can't wait days for answers. ClickHouse Cloud and LibreChat deliver real-time insights to the right people, helping identify at-risk merchants and surface millions of dollars in potential revenue risk."
>
> — Rafeeq Abdul, Sr. Director of Engineering, Visa

## Fresh data, secure and governed control

Rafeeq is quick to stress that none of these results came at the expense of security. "The key principles of Visa data compliance and governance are rigorous and upheld" he says.

ClickHouse provides the deployment flexibility to meet Visa where they are in terms of security and compliance requirements. In the new pipeline, data starts in on-prem SQL databases, which remain in place. Files are PGP-encrypted in transit and handed off into Amazon S3 as a protected, raw data store. From there, a VPC PrivateLink connection feeds a custom ETL pipeline that moves the data into ClickHouse Cloud, so the data plane is reached over private connectivity rather than the public internet.

![Visa User Story Diagram (1).jpg](https://clickhouse.com/uploads/Visa_User_Story_Diagram_1_25b4bd037b.jpg)

This architecture, Rafeeq explains, delivers both freshness and control. Change data capture and materialized views keep data current and shaped for the way teams consume it, while federated access controls govern who can see what. The result is fewer handoffs and simpler management, delivering real-time insight with disciplined, enterprise-ready controls.

## The business impact: revenue and time savings

While the latency and performance achievements are impressive, the big payoff for Visa is what these enable for the business. By flagging at-risk merchants in real time, they've surfaced millions of dollars in revenue risk, fast enough to act on. In the old system, that kind of signal would often show up days late.

From a productivity standpoint, work that used to eat up hours of an analyst's week has effectively gone to zero. Manual dashboard creation, data lookups across hundreds of tables, and report prep for intake/onboarding are now completely self-service, generated on demand via plain English, turning around in seconds instead of 2 to 3 days. "Everything is now available at their fingertips in a natural-language scenario," Rafeeq says. All told, he estimates that the platform has helped Visa reclaim 8 to 10 hours per user, per week and collectively save thousands of hours across teams per month.

With [ClickHouse Cloud](https://clickhouse.com/cloud), [LibreChat](https://www.librechat.ai/), and the [ClickHouse MCP server](https://github.com/ClickHouse/mcp-clickhouse), what began as a logging migration from Splunk has become a way for Visa's business teams to interrogate payments data directly, without waiting around for a SQL specialist. Looking ahead, Rafeeq says the team plans to "continue to extend our partnership and build on top of our platform," widening the set of questions anyone at Visa can answer, in natural language, in real time.

---

## Get started today

Interested in seeing how ClickHouse works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-1036-get-started-today-sign-up&utm_blogctaid=1036)

---