---
title: "MySQL CDC connector for ClickPipes is now in Public Beta"
date: "2025-07-17T17:08:34.544Z"
author: " Amogh Bharadwaj"
category: "Product"
excerpt: "We’re excited to open up the public beta of the MySQL CDC connector in ClickPipes."
---

# MySQL CDC connector for ClickPipes is now in Public Beta

We’re excited to open up the [public beta of the MySQL CDC connector in ClickPipes](https://clickhouse.com/cloud/clickpipes/mysql-cdc-connector)! With just a few clicks, you can start streaming your [MySQL](https://clickhouse.com/docs/integrations/clickpipes/mysql/source/generic) data directly into [ClickHouse Cloud](https://clickhouse.cloud/). Simply head to the Data Source tab in your service, choose MySQL CDC, and walk through the guided setup.

<iframe width="560" height="315" src="https://www.youtube.com/embed/LcClJOYpUnM?si=y4jaGen-Nl_VkP1Q" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
The journey to this release started earlier this year. After celebrating our Postgres CDC launch in February, we turned our attention to MySQL—working closely with early users to shape the experience. By April 2025, we had a Private Preview live.

What followed exceeded our expectations. Customers adopted the connector quickly, pushing production workloads through it, offering sharp feedback, and syncing massive volumes of data from MySQL to ClickHouse. That hands-on input has been invaluable in polishing the product—and now, we're ready to share it with everyone.

## Customer feedback

Here’s what some of our reference customers have to say:

"Previously, our CDC workflows relied on a complex broker-based streaming infrastructure. This approach was not only resource-intensive but also required significant operational overhead. We've transitioned to using the MySQL CDC connector in ClickPipes, and the impact has been transformative. ClickPipes has allowed us to modernize our data pipeline, reduce maintenance costs, and focus on delivering value through analytics rather than infrastructure management. No more managing clusters, brokers, or custom connectors - ClickPipes just works out of the box." -- [BrainRocket](https://www.brainrocket.com/)

"ClickPipes MySQL CDC connector has been an excellent tool for us to stream our data into Clickhouse . It offered reliable, real-time replication with about a one-minute delay. It was simple to set up, cost-effective, handled both historical and ongoing sync smoothly, and supported private VPC networking to keep our data secure. ClickPipes, paired with ClickHouse Cloud, gives us true real-time analytics without the complexity. It just works!" - [NOCD](https://www.treatmyocd.com/)

## Product Enhancements

<iframe width="560" height="315" src="https://www.youtube.com/embed/nHKuvUXXqEU?si=Hv-CI_Hnspsyl8uk" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

### Built for performance

The MySQL CDC connector has been carefully designed with broad compatibility and performance in mind. Whether you're running MySQL 5.7, 8.0, or a [MariaDB](https://clickhouse.com/docs/integrations/clickpipes/mysql/source/generic_maria) variant, the connector goes beyond basic compatibility. It deeply understands the nuances of each version—differences in binary log formats, [GTID](https://clickhouse.com/docs/integrations/clickpipes/mysql/faq#how-is-replication-managed) behavior, and schema introspection—and adjusts its validation and replication logic accordingly. This allows it to deliver consistent, reliable replication across environments that may behave quite differently under the hood.

#### Parallel Snapshotting for Blazing Fast Initial Loads

For the initial load, we are able to [optimize performance](https://github.com/PeerDB-io/peerdb/pull/2909) by partitioning data using a source column you provide, which enables parallel reads and speeds up large-scale migrations. Compared to single-threaded loads, we've seen 3x faster sync times with 4 threads and up to 8–10x faster with 16 threads on well-provisioned systems. This approach also improves reliability: breaking the load into smaller chunks makes it easier to retry specific segments in case of recoverable errors like network hiccups. It also enhances visibility, letting users track progress more granularly.

#### Reliable and Intelligent Change Data Capture

The MySQL CDC connector in ClickPipes is built for reliability and ease of use. It maintains [transactional consistency](https://github.com/PeerDB-io/peerdb/pull/2502) when reading from the binary logs, ensuring accurate replication into ClickHouse. We [automatically detect and propagate column additions](https://github.com/PeerDB-io/peerdb/pull/2557), so your ClickHouse schema stays in sync as your source evolves. With broad data type support—[including vector types](https://github.com/PeerDB-io/peerdb/pull/2648)—you can replicate modern, complex workloads seamlessly. And even during idle periods, [we continuously advance our binary log checkpoint](https://github.com/PeerDB-io/peerdb/pull/3070), so resuming from interruptions is fast and efficient.

As more customers began using the connector in real-world environments, we focused on expanding its capabilities to meet the needs of production-scale systems. Here’s what’s new:

### User-facing alerts

This [feature](https://github.com/PeerDB-io/peerdb/pull/2573) surfaces alerts for failures or potential issues across both the MySQL source and ClickHouse destination in your ClickPipe. Notifications appear in the ClickHouse Cloud Notifications center and are also sent via email. Currently, we generate alerts for issues like source connection failures, data type mismatches between MySQL and ClickHouse, and ingestion failures on the ClickHouse side. Each alert includes helpful context and, where applicable, self-mitigation steps to guide you toward a resolution.

<iframe width="560" height="315" src="https://www.youtube.com/embed/Uhe1_BMOAxg?si=icPS10OfUJm1pp3F" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

### PeerDB Open Source Enhancements

Under the hood, this connector is built on PeerDB, our open-source CDC engine. Over the past few months, we’ve made key enhancements to PeerDB:

* [Exporting granular metrics](https://github.com/PeerDB-io/peerdb/pull/2687) for CDC and initial load.  
* [A thorough classification system](https://github.com/PeerDB-io/peerdb/pull/2494) to catch and surface errors needing user intervention.  
* Extensive support for secure connections to your source database via [root CAs](https://github.com/PeerDB-io/peerdb/pull/2621) and TLS hostnames.

## Pricing

The MySQL CDC connector in ClickPipes is free to use during the public beta. As we move toward General Availability (GA), we’ll introduce pricing that reflects the value we provide—while remaining competitive and accessible for real-time analytics at scale. Pricing details will be shared ahead of GA.

## Conclusion

Thanks for reading! We're now focused on the next milestone: bringing MySQL CDC in ClickPipes to General Availability. In the meantime, we’d love to hear from you—whether you have questions, feedback, or just want to connect with the product team. Feel free to reach out at [db-integrations-support@clickhouse.com](mailto:db-integrations-support@clickhouse.com).

Ready to get started with native MySQL CDC in ClickHouse Cloud? Here are some resources to help you dive in:

* [ClickPipes for MySQL FAQ](https://clickhouse.com/docs/integrations/clickpipes/mysql/faq)  
* [Try ClickHouse Cloud for free](https://clickhouse.com/docs/getting-started/quick-start/cloud)