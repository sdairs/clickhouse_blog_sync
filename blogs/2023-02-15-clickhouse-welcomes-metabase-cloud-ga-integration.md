---
title: "ClickHouse welcomes Metabase Cloud GA integration"
date: "2023-02-15T16:16:47.091Z"
author: "The ClickHouse Team"
category: "Engineering"
excerpt: "We're pleased to announce the GA release of the official ClickHouse plugin for Metabase and its availability in Metabase Cloud!"
---

# ClickHouse welcomes Metabase Cloud GA integration


<iframe width="764" height="430" src="https://www.youtube.com/embed/UK2fIHiEWOg" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>

<br />
At ClickHouse, we passionately believe supporting our open-source ecosystem is fundamental to adoption and ensuring our users are successful. As part of this, it's always a pleasure to work with other companies whose complementary technologies are also grounded in open source. Today we are pleased to announce the availability of the ClickHouse plugin in Metabase Cloud!

In this blog post, we explore the history of the plugin and its journey to becoming available in Metabase Cloud and our plans for the future.

To learn more about Metabase and the ClickHouse plugin, join our [joint webinar on the 7th of March](/company/events/2023-03-07-metabase-clickhouse-webinar) as we build visualizations on multi-TB datasets with a few clicks! As a teaser, we've recorded a simple introduction to go with today's announcement.

## What is Metabase?

Users new to ClickHouse have several visualization options, and your choice will often depend on your existing tooling and requirements. However, we increasingly see users gravitating to Metabase due to its simplicity and ability to allow users to construct beautiful visualizations without needing to worry about writing SQL.

Queries can be constructed by simply dragging and dropping fields - a feature likely to appeal to business users. Focusing on fast data exploration, the breadth of visuals and customizability is constantly expanding, with users enthusiastic about the clean and simple interface and workflow.

## A little bit of history

Many of [our community integrations](https://clickhouse.com/blog/clickhouse-dbt-project-introduction-and-webinar) experience a similar journey, starting off as a community project for one user and growing in adoption before becoming an official project sponsored by ClickHouse. The [ClickHouse plugin for Metabase](https://github.com/ClickHouse/metabase-clickhouse-driver) is another great example of this, and largely thanks to the work of [Felix Mueller](https://github.com/enqueue) and the [early work of other contributors](https://github.com/metabase/metabase/pull/8722), it is another example of community success. In November last year, the repository was transferred to ClickHouse. As well as addressing a [few compatibility issues](https://github.com/ClickHouse/metabase-clickhouse-driver/pull/107), we [improved tests](https://github.com/ClickHouse/metabase-clickhouse-driver/pull/112), [upgraded the underlying JDBC driver](https://github.com/ClickHouse/metabase-clickhouse-driver/issues/90), [improved CI](https://github.com/ClickHouse/metabase-clickhouse-driver/pull/106), and allowed [advanced connection settings](https://github.com/ClickHouse/metabase-clickhouse-driver/pull/109) such as [SSH tunnels](https://github.com/ClickHouse/metabase-clickhouse-driver/pull/116). 

Confident the integration was mature with wide adoption, we approached Metabase to expose this plugin within their Cloud offering with the hope this would ensure the widest possible adoption.

## Collaboration

The release of any plugin in Metabase Cloud requires an extensive code review process. In late January, we began the process of making our plugin available in Metabase Cloud. Thanks to the historical efforts of the community and recent improvements, the required changes were minimal. Impressively, Metabase provided feedback within a few days, and the plugin was released today in Metabase Cloud.

## Future Plans

At this point, we consider the plugin stable and ready for production deployment. We have a few minor issues we’d like to address in the coming weeks - specifically [improving table listings](https://github.com/ClickHouse/metabase-clickhouse-driver/issues/137) and making SSL certificate configuration [more user-friendly](https://github.com/ClickHouse/metabase-clickhouse-driver/issues/136). However, we’re always open to community feedback and would welcome ideas from the community.
