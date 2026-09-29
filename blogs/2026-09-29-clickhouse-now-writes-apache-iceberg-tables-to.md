---
title: "ClickHouse now writes Apache Iceberg tables to Microsoft OneLake"
date: "2026-09-29T07:17:01.504Z"
author: "Melvyn Peignon"
category: "Product"
excerpt: "ClickHouse today announced the ability to write directly to Microsoft OneLake, the unified data lake service within Microsoft Fabric."
---

# ClickHouse now writes Apache Iceberg tables to Microsoft OneLake

Following our announcement that [ClickHouse is data lake ready](https://clickhouse.com/blog/clickhouse-is-data-lake-ready), we've continued to expand support for open data lake ecosystems and catalog integrations. At the end of June 2026, ClickHouse supported writing Iceberg tables to object storage, where you provide the S3 or Microsoft Azure ADLSgen2 path directly. This works, but it has a limitation: unless those tables are also registered in a catalog, other tools in your organization can't discover or query them.

At [OpenHouse 2026](https://clickhouse.com/openhouse/san-francisco), we announced that ClickHouse now writes Iceberg tables directly to Microsoft OneLake. Your results are registered in the OneLake catalog using [Iceberg REST-based Table APIs](https://learn.microsoft.com/en-us/fabric/onelake/table-apis/iceberg-table-apis-overview), secured by [OneLake Security](https://learn.microsoft.com/en-us/fabric/onelake/security/data-access-control-model), and queryable by compatible tools and engines.

You can read data from OneLake, accelerate it in ClickHouse, and push results back to OneLake for the rest of your organization to consume, all through the same catalog connection.

## **Use case: AI agents that write results back to OneLake**

As AI agents become more embedded in analytical workflows, they need two things from their database: fast reads to answer questions in real time, and a way to publish their results where the rest of the organization can use them.

Say you have an AI agent that monitors order data in ClickHouse, detects anomalies (unusual spikes in returns, shipping delays by region, revenue drops by product line), and produces a daily summary table with anomaly scores and recommended actions. Before catalog writes, those results stayed in ClickHouse.

With OneLake write support, the agent runs its queries in ClickHouse and writes the results directly to an Iceberg table in OneLake. That table shows up automatically for every tool connected to the OneLake catalog. Your operations team sees it in Microsoft Power BI, data science picks it up in Fabric Spark, and the agent's output is secured by the same [OneLake Security access controls](https://learn.microsoft.com/en-us/fabric/onelake/security/data-access-control-model) as the rest of your data. The agent produces the insight, ClickHouse provides the analytical query speed, and OneLake handles the distribution.

This is what Melvyn Peignon demoed at OpenHouse: ClickHouse querying OneLake Iceberg tables to power an analytics AI assistant. Write support closes the loop, letting the assistant publish its results back to the same catalog it reads from.

## **Use case: Applications writing directly to OneLake via ClickHouse**

Beyond writing aggregated query results, you can also use ClickHouse as the write path for applications that need to land data directly into OneLake. Rather than routing through a separate ingestion layer, applications write to ClickHouse and the results flow into OneLake as a managed Iceberg table, governed and discoverable from the moment they land.

## **How it works**

If you've already connected ClickHouse to OneLake for reads, writes use the same connection. No additional setup is required.

The connection uses the `DataLakeCatalog` engine, which connects ClickHouse to OneLake's Iceberg-compatible Table APIs. You authenticate via Microsoft Entra ID (formerly Azure Active Directory) using a service principal, and ClickHouse uses that identity both to discover tables in the catalog and to read and write data in OneLake storage.

Setting up the connection looks like this:

```sql
SET allow_database_iceberg = 1;

CREATE DATABASE onelake_catalog
ENGINE = DataLakeCatalog('https://onelake.table.fabric.microsoft.com/iceberg')
SETTINGS
    catalog_type = 'onelake',
    warehouse = '<workspace_id>/<lakehouse_id>',
    onelake_tenant_id = '<tenant_id>',
    oauth_server_uri = '<https://login.microsoftonline.com/><tenant_uuid>/oauth2/v2.0/token',
    auth_scope = '<https://storage.azure.com/.default>',
    onelake_client_id = '<client_id>',
    onelake_client_secret = '<client_secret>';
```

The `warehouse` parameter combines your Fabric workspace ID and lakehouse ID. You can find these in the Microsoft Fabric portal. The `onelake_client_id` and `onelake_client_secret` come from a service principal registered in Entra ID. See [Microsoft's documentation](https://learn.microsoft.com/en-us/fabric/onelake/table-apis/table-apis-overview#prerequisites) for a step-by-step guide on gathering these credentials.

Once the connection is in place, the entire OneLake catalog appears as a ClickHouse database. You can list tables, inspect schemas, and query data just like any other database in ClickHouse:

```sql
SHOW TABLES FROM onelake_catalog;

SELECT count(*)
FROM onelake_catalog.`<namespace>.<table_name>`
WHERE region = 'EMEA';
```

Note the backtick syntax around the namespace and table name. ClickHouse doesn't support multiple namespace levels natively, so the full `namespace.table` path is wrapped in backticks.

And now, the new part. Writing results back uses the same `INSERT INTO` syntax you'd use with any ClickHouse table:

```sql
INSERT INTO onelake_catalog.`<namespace>.<output_table>`
SELECT
    region,
    count() AS order_count,
    sum(revenue) AS total_revenue
FROM onelake_catalog.`<namespace>.<source_table>`
GROUP BY region;
```

The resulting table is managed by the OneLake catalog and secured by [OneLake Security access controls](https://learn.microsoft.com/en-us/fabric/onelake/security/data-access-control-model). Any Iceberg-compatible engine connected to the same catalog can read it. You can also write from a local MergeTree table into OneLake, which is the typical pattern when you've accelerated data locally and want to publish the results back.

For full setup instructions, see the [OneLake catalog documentation](https://clickhouse.com/docs/use-cases/data-lake/onelake-catalog).

## **Why OneLake**

OneLake is the unification layer for Microsoft Fabric. Every tenant gets exactly one OneLake instance, provisioned automatically, and all data inside it inherits a single governance model with lineage tracking, data protection, certification, and catalog integration. Workspace-level permissions mean different teams can own their data independently while still contributing to the same lake. Writing to OneLake means your results become part of that governance model from the moment they land.

The interoperability story is where it gets interesting. [Shortcuts](https://learn.microsoft.com/en-us/fabric/onelake/onelake-shortcuts) are symbolic links that point to data in S3, Google Cloud Storage, Azure ADLS, or other OneLake locations without moving or duplicating data. [Mirroring](https://learn.microsoft.com/en-us/fabric/mirroring/overview) continuously replicates databases (SQL Server, Snowflake, Oracle, and others) using zero-ETL technology into OneLake as Delta Lake tables, which are automatically converted to Apache Iceberg. Between the two, OneLake can surface data from across clouds and on-premises systems in one place, without ETL pipelines or manual data movement.

OneLake also keeps Delta Lake and Iceberg in sync automatically. A table written in one format is readable in the other. So when ClickHouse writes an Iceberg table to OneLake, that data is accessible to every tool in the Microsoft Fabric stack, including those that speak Delta Lake.

At the OpenHouse session, Kevin Liu (Engineer at Microsoft and Apache Iceberg PMC member) demonstrated DuckDB, Spark, PyIceberg, Databricks, Snowflake, and Salesforce all reading from the same OneLake table.

On the security side, Microsoft announced at Build 2026 that OneLake Security is now GA, with table, row, and column-level security enforced across the platform. They also announced that the security APIs are opening up to third-party engines. This is something we're actively looking at for deeper ClickHouse integration.

## **What's next**

OneLake is the first catalog to support writes from ClickHouse, with more catalogs planned over the coming months. We're also working on deeper integration with OneLake's [fine-grained security APIs](https://learn.microsoft.com/en-us/fabric/onelake/security/onelake-security-integrations-external-engines), which are now open to third-party engines.

For the full breakdown of what ClickHouse supports across formats, catalogs, and cloud storage, check the [data lake support matrix](https://clickhouse.com/docs/use-cases/data-lake/support-matrix).

## **Get started**

If you're already connected to OneLake for reads, the [OneLake catalog guide](https://clickhouse.com/docs/use-cases/data-lake/onelake-catalog) covers everything you need for writes. Starting from scratch, begin with the [data lake getting started guide](https://clickhouse.com/docs/use-cases/data-lake/getting-started) and [try ClickHouse Cloud](https://clickhouse.com/cloud).
