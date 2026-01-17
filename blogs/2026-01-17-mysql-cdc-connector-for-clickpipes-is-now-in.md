---
title: "MySQL CDC connector for ClickPipes is now in Private Preview"
date: "2025-04-09T23:28:09.522Z"
author: "Sai Srirampur"
category: "Product"
excerpt: "We are excited to announce the availability of the MySQL CDC connector in ClickPipes in private preview. With this, customers can easily replicate their MySQL databases to ClickHouse Cloud with just a few clicks."
---

# MySQL CDC connector for ClickPipes is now in Private Preview

Today, we’re excited to announce the private preview of the [MySQL](https://www.mysql.com/) Change Data Capture (CDC) connector in [ClickPipes](https://clickhouse.com/cloud/clickpipes)! This enables customers to replicate their MySQL databases to [ClickHouse Cloud](https://clickhouse.cloud/) in just a few clicks and leverage ClickHouse for blazing-fast analytics. You can use this connector for both continuous replication and one-time migration from MySQL, no matter where it's running—whether in the cloud (RDS, Aurora, CloudSQL, Azure, etc.) or on-premises.

The experience is natively integrated into ClickHouse Cloud through ClickPipes, the built-in ingestion service of ClickHouse Cloud. This eliminates the need for external ETL tools, which are often expensive and require significant overhead to set up and manage. This connector is powered by [**PeerDB**](https://github.com/PeerDB-io/peerdb), a fully open source database replication project by ClickHouse—so there’s no lock-in, and the value extends to self-hosted ClickHouse users as well.


[**You can sign up to the private preview by following this link.**](https://clickhouse.com/cloud/clickpipes/mysql-cdc-connector)


After launching our Postgres CDC connector a few months ago—which has been rapidly growing in adoption—there was overwhelming demand from customers to provide similar capabilities for MySQL data sources. We’ve heard all of that feedback and are now launching the MySQL connector in ClickPipes.

<iframe width="768" height="432" src="https://www.youtube.com/embed/9d8EMVHrKkc?si=iSdrgQpS25AnTMKB" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

## Purpose-built for MySQL and ClickHouse

Our focus at ClickPipes has always been quality over quantity, so any connector we add is built to scale. The same applies to the MySQL CDC connector — it’s designed to handle terabytes of data, delivering blazing-fast performance with replication latency as low as a few seconds. It supports MySQL-native features, including replication of JSON and vector types, along with flexible replication modes, including GTID-based and binary log position-based (POS) options.

## Key Features

The [MySQL CDC connector](https://clickhouse.com/docs/integrations/clickpipes/mysql) comes packed with features designed to make it easy to initiate and manage replication from MySQL to ClickHouse Cloud. Here’s a list of key capabilities:

* **Blazing-Fast Initial Loads (Backfills):** Migrate terabytes of existing data across hundreds of MySQL tables to ClickHouse within a day. You can configure the number of parallel threads to migrate multiple tables simultaneously. Soon, we plan to support intra-table parallelism—using multiple threads to migrate a single large table.  
    
* **Continuous Replication (CDC):** After the initial load, continuously replicate changes—including all DML operations (INSERTs, UPDATEs, DELETEs)—from MySQL to ClickHouse with latencies as **low as a few seconds**.  
    
* **Table and Column-Level Filtering:** Selectively replicate only the tables and columns you need from MySQL—helping reduce data transfer and storage overhead while supporting compliance and privacy needs, such as excluding PII.

 ![tableselector (1).png](https://clickhouse.com/uploads/tableselector_1_ca659eded9.png)
    
* **Schema Changes:** Automatically replicate schema changes during CDC, including DDL commands like ADD COLUMN and DROP COLUMN on MySQL.  
    
* **Flexible Replication Modes:** The connector relies on MySQL’s binary log for replication and supports both file position-based (POS) and GTID-based replication modes.  
    
* **Native Data Type Support:** Fully supports MySQL-native data types—including vectors, unsigned integers, geospatial types, JSON, vectors and more.  
    
* **MySQL Version Compatibility:** Supports all MySQL versions 8.0.1 and above.  
    
* **In-Place Editing:** Modify existing MySQL CDC Pipes to add new tables, adjust sync intervals (data-freshness), or update configuration settings—all without downtime.  

![editsettings (1).png](https://clickhouse.com/uploads/editsettings_1_debffc96f2.png)
    
* **Enterprise-Grade Security:** Securely connect MySQL sources using SSH tunneling, AWS PrivateLink, and IP-based access controls.  
    
* **Built-in metrics and monitoring:** Enjoy a fully managed replication solution with built-in monitoring, metrics, logs, and high availability—eliminating operational overhead for your team.

![metrics (1).png](https://clickhouse.com/uploads/metrics_1_523cd3d942.png)
    

## How to sign up for Private Preview?

You can sign up for the private preview by filling out [the form on this page](https://clickhouse.com/cloud/clickpipes/mysql-cdc-connector). Our team will reach out to you within a few days and work closely with you to provide early access. Given the anticipated demand, there may be a slight delay, but we’ll ensure we connect with you as soon as possible.

The Private Preview entails no cost and is fully free. This is a great opportunity for you to get firsthand experience with the native MySQL integration in ClickHouse Cloud and directly influence the roadmap. Looking forward to having you onboard!