---
title: "Postgres CDC connector for ClickPipes is now in Public Beta"
date: "2025-02-17T18:24:33.152Z"
author: "Sai Srirampur"
category: "Product"
excerpt: "We are excited to announce the availability of the Postgres CDC connector in ClickPipes in public beta. With this, customers can easily replicate their Postgres databases to ClickHouse Cloud with just a few clicks."
---

# Postgres CDC connector for ClickPipes is now in Public Beta

Today, we are excited to announce the availability of [the Postgres CDC connector in ClickPipes in public beta](https://clickhouse.com/cloud/clickpipes/postgres-cdc-connector). With this, customers can easily replicate their Postgres databases to ClickHouse Cloud with just a few clicks. Simply go to the **Data Source** tab in your service, choose the Postgres tile, and follow a few steps to integrate your Postgres databases.

<img src="/uploads/Postgres_CDC_Add_Data_Source_e058704d02.gif" 
     alt="Postgres CDC Add Data Source" 
     loading="lazy">


After [joining forces with PeerDB](https://clickhouse.com/blog/clickhouse-welcomes-peerdb-adding-the-fastest-postgres-cdc-to-the-fastest-olap-database), a leading Postgres CDC company, we integrated it natively into ClickHouse Cloud and [released](https://clickhouse.com/blog/postgres-cdc-connector-clickpipes-private-preview) the private preview of the Postgres CDC connector in ClickPipes.

The response during the Private Preview was overwhelming! Many customers tested the service, provided valuable feedback, ran production workloads, and replicated multiple petabytes of data from Postgres to ClickHouse. After further refining the experience, we are now ready to make native Postgres CDC in ClickHouse Cloud available to everyone.

## Customer feedback

The Postgres CDC connector in ClickPipes is already being used by multiple organizations, including [Syntage](https://syntage.com/), [Neon](https://neon.tech/), [Blacksmith](https://www.blacksmith.sh/), [Vapi](https://vapi.ai/), [Adora](https://adora.so/), [Daisychain](https://www.daisychain.app/), [Unify](https://www.unifygtm.com/home-lp), [Ottimate](https://ottimate.com/) and [others](https://clickhouse.com/cloud/clickpipes/postgres-cdc-connector). Below are a few testimonials capturing feedback from our reference customers:

_“We are having an amazing experience using the Postgres CDC connector in ClickPipes. We seamlessly moved our 30TB Aurora database to ClickHouse Cloud and are continuously keeping it in sync. We did not expect any ETL tool to handle our load, especially after a bitter experience in the past. However, we were pleasantly surprised by how reliable and performant ClickPipes has been for us.”_ - [Matteus Pedroso](https://www.linkedin.com/in/matheuspedroso/), Co-founder and CEO, [Syntage](https://syntage.com/)

_“ClickPipes for Postgres has made it incredibly easy for us to keep our billing data in Postgres synchronized with ClickHouse for efficient analytics. The CDC experience is blazing fast, ensuring data freshness within seconds while minimizing the load on our production Postgres database. An invaluable solution for seamlessly integrating Postgres with ClickHouse!”_ - Mo Abedi, Software Engineer in Billing team, [Neon.tech](https://neon.tech/)

## Product Enhancements

<iframe width="768" height="432" src="https://www.youtube.com/embed/fHuFSmafYUo?si=yEFblvI2MuUBadBO" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

### Built for performance

The Postgres CDC connector is built on strong foundations, with performance at the forefront. It has been purpose-built for Postgres and ClickHouse and implements many native optimizations. On the Postgres side, parallel snapshotting enables 10x faster initial loads and backfills, allowing terabyte-scale migrations in hours, while continuous [flushing of the replication slot](https://clickhouse.com/blog/enhancing-postgres-to-clickhouse-replication-using-peerdb#efficiently-flush-the-replication-slot) to intermediary stages ensures data freshness within seconds. On the ClickHouse side, parallel ingestion through multiple replicas and [configurable chunking](https://clickhouse.com/blog/enhancing-postgres-to-clickhouse-replication-using-peerdb#better-memory-handling-on-clickhouse) for better memory management improve performance and reliability.

Beyond these foundations, over the past few months, the team has added several features to support enterprise-grade production workloads. Below are the highlights:

### User facing alerts

This feature enables alerts for failures or potential issues with ClickPipe. Alerts are surfaced via the Notifications center in ClickHouse Cloud and via email. Each alert classifies the issue type—for example, when a replication slot is growing unexpectedly, off stream MVs are failing during ingestion, or there are connectivity issues, among others—and provides self-mitigation steps to help you resolve them.

<img src="/uploads/Postgres_CDC_User_Notifications_cddc06fced.gif" 
     alt="Gif showing how users can configure notifications" 
     loading="lazy">

### Source Monitoring Page

We also introduced a new page that allows you to monitor the source Postgres database during CDC. The page provides key insights, including a list of active replication slots, their status, a chart showing replication slot growth over time, and associated wait events in Postgres. This offers detailed visibility into the progress of replication, helping you identify bottlenecks and optimize performance.

![Visual showing Postgres replication slot status and lag.](https://clickhouse.com/uploads/Postgres_CDC_Source_Monitoring_852798cd65.png)

### Open API Support

A common piece of feedback we've received from customers during the private preview is that it becomes difficult to create and manage pipes with potentially hundreds of tables through the UI. To address this, we added Open API support, which enables you to create and manage pipes programmatically. Currently, Open API support is in private beta. If you're interested in trying it, reach out to our team at db-integrations-support@clickhouse.com. The next step in this effort is to add Terraform support for creating and managing ClickPipes for Postgres CDC.

### PeerDB Open Source Enhancements

This connector is powered by PeerDB, our [open source](https://github.com/PeerDB-io/peerdb/) Postgres CDC codebase. In the past couple of months, we've made several improvements to make PeerDB enterprise-ready. In the past two months, we've made 8 minor and 3 major [releases](https://github.com/PeerDB-io/peerdb/releases). Notable improvements include:

* [Improved ingestion performance by using multiple replicas in ClickHouse.](https://github.com/PeerDB-io/peerdb/pull/2256)
    
* [Eliminated reconnections to the replication slot for better performance under heavy workloads.](https://github.com/PeerDB-io/peerdb/pull/2371)
    
* [Revamped retry logic to filter false positive errors.](https://github.com/PeerDB-io/peerdb/pull/2122)
    
* Asynchronous pulling from Postgres and pushing to ClickHouse to enhance replication slot flushing logic.
    

## Pricing

During the public beta, the Postgres CDC connector in ClickPipes will be free of charge. We plan to introduce pricing during the next phase, General Availability (GA). The exact pricing is still to be determined, but our goal is to keep it competitive to support real-time analytics use cases at scale.

## Conclusion

I hope you enjoyed reading the blog. The next phase for us is the General Availability (GA) of Postgres CDC in ClickPipes once the feature is ready. During the public beta, if you run into issues, have questions, or want to chat with the product team, please reach out at [db-integrations-support@clickhouse.com](mailto:db-integrations-support@clickhouse.com).

Interested in trying the native Postgres CDC capabilities in ClickHouse Cloud? Check out these helpful links:

* [Ingesting data from Postgres to ClickHouse (using CDC)](https://clickhouse.com/docs/en/integrations/clickpipes/postgres)
    
* [ClickPipes for Postgres FAQ](https://clickhouse.com/docs/en/integrations/clickpipes/postgres/faq)
    
* [Try ClickHouse Cloud for free](https://clickhouse.com/docs/en/cloud/get-started/cloud-quick-start)