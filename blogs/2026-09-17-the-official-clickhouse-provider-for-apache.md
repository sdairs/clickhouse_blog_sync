---
title: "The official ClickHouse provider for Apache Airflow is now available"
date: "2026-09-17T18:06:01.746Z"
author: "Aditya Chidurala, Bentsi Leviav and Alex Francoeur"
category: "Product"
excerpt: "The official ClickHouse provider for Apache Airflow simplifies data workflows with standard SQL operators, bulk inserts, and shared setup across self-managed Airflow and Astronomer."
---

# The official ClickHouse provider for Apache Airflow is now available

## Summary

ClickHouse now has an official integration with Apache Airflow, making it easier for teams to orchestrate and manage ClickHouse data workflows wherever they run Airflow. Many ClickHouse customers are already using the new Apache Airflow provider in production today.

## Introduction {#introduction}

Many ClickHouse users rely on [Apache Airflow](https://airflow.apache.org/), the open source standard for orchestrating data pipelines to schedule ingestion, transformations, and recurring analytical jobs. Until now, connecting the two usually meant installing a community plugin or writing custom integration code.

Airflow now has an upstream ClickHouse provider: [`apache-airflow-providers-clickhousedb`](https://airflow.apache.org/registry/providers/clickhousedb/1.0.0/). It uses ClickHouse Connect over HTTP(S), works with Airflow’s common SQL operators, and includes a ClickHouse hook for bulk and client-specific operations. This post shows how to install it, configure a connection, and run the same workflow on a self-managed Airflow setup or a managed platform like [Astronomer](https://www.astronomer.io/).

## Community origins {#community_origins}

Before this release, the ClickHouse community solved this problem on its own. Anton Bryzgalov ([bryzgaloff](https://github.com/bryzgaloff)) created the [airflow-clickhouse-plugin](https://github.com/bryzgaloff/airflow-clickhouse-plugin) back when Airflow had no native way to talk to ClickHouse. He maintained it for years, evolving it into the de facto standard for the Airflow and ClickHouse community, [and one of the top 1% downloaded packages](https://clickpy.clickhouse.com/dashboard/airflow-clickhouse-plugin) on PyPI. Its conventions even shaped the internal tooling our own data warehouse team built. Contributions like these are why the ClickHouse ecosystem is what it is today. Thank you, Anton.

For teams that want an officially maintained integration, the provider is a natural upgrade path. It's where our investment and new features will land, and moving over is mostly mechanical. Install the provider, point your connection at the HTTP(S) port, and use the standard `SQLExecuteQueryOperator` in your DAGs. 

## Why an official provider {#why_an_official_provider}

We ship new ClickHouse features constantly, and an official provider living upstream lets the integration keep pace with the database instead of always playing catch-up.

A few decisions shaped the implementation:

- **Built on ClickHouse Connect.** The provider connects over the [HTTP interface](https://clickhouse.com/docs/interfaces/http) using [`clickhouse-connect`](https://clickhouse.com/docs/integrations/python), the Python client we maintain in-house. When the client gets faster or gains features, the provider inherits them.  
- **Airflow's common SQL framework.** The provider exposes ClickHouse through `apache-airflow-providers-common-sql`, so the standard `SQLExecuteQueryOperator` handles DDL, DML, and analytical queries. No ClickHouse-specific operator to learn.  
- **A hook for everything else.** For bulk inserts, streaming, or ClickHouse-specific client calls, `ClickHouseHook` gives you direct access, including a `bulk_insert_rows` method that uses the native columnar insert path.

## How customers use Airflow with ClickHouse {#how_customers_use_airflow_with_clickhouse}

Many of our customers run Airflow with ClickHouse today. The pairing shows up across nearly every industry we serve, and in our own stack.

The relationship with Astronomer runs both directions, too. Astro Observe, their data observability product, is [built on ClickHouse Cloud](https://clickhouse.com/blog/why-astronomer-chose-clickhouse-to-power-its-new-data-observability-platform-astro-observe), handling billions of Airflow workflow events to power real-time pipeline insights for Airflow users. The team behind the platform that runs Airflow for thousands of companies chose ClickHouse for its own analytics.

[Chartmetric](https://clickhouse.com/blog/chartmetric-scaling-music-analytics), which tracks more than 12 million artists across streaming and social platforms, pairs Airflow-orchestrated pipelines with ClickHouse Cloud, including a playlist cache pipeline that ingests over 15 million rows every five minutes.

We run the same pattern ourselves. Our [internal data warehouse](https://clickhouse.com/blog/building-a-data-warehouse-with-clickhouse) is built on ClickHouse Cloud with Airflow scheduling the insert jobs across 76 DAGs across 40+ data sources, moving around 6 billion rows a day. The entire company relies on it, from leadership reviewing weekly metrics to product, sales, and support teams answering day-to-day questions, and increasingly the agentic workflows we're building on top of our own data. Airflow is the component that keeps it all fed.

## Getting started with Apache Airflow {#getting_started_with_apache_airflow}

If you're running open source Airflow, the provider installs like any other:

<pre><code type='click-ui' language='bash'>
pip install apache-airflow-providers-clickhousedb
</code></pre>

It pulls in `apache-airflow-providers-common-sql` and `clickhouse-connect` automatically. Next, create a connection. The provider registers a `clickhouse` connection type, so you can configure it in the Airflow UI under **Admin > Connections**, or define it as an environment variable:

<pre><code type='click-ui' language='bash'>
export AIRFLOW_CONN_CLICKHOUSE_DEFAULT='{
    "conn_type": "clickhouse",
    "host": "abc123.clickhouse.cloud",
    "port": 8443,
    "login": "default",
    "password": "secret",
    "schema": "my_database",
    "extra": {"secure": true}
}'
</code></pre>

For [ClickHouse Cloud](https://clickhouse.com/cloud) or any TLS-enabled cluster, set `secure` to `true` and use port `8443`.

![](https://clickhouse.com/uploads/airflow_sep2026_connection_6e4f1f764f.png)

From there, a DAG is just standard Airflow:

<pre><code type='click-ui' language='python'>
from datetime import datetime

from airflow import DAG
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator

with DAG(
    dag_id="clickhouse_example",
    start_date=datetime(2026, 1, 1),
    default_args={"conn_id": "clickhouse_default"},
    schedule="@daily",
    catchup=False,
) as dag:
    create_table = SQLExecuteQueryOperator(
        task_id="create_table",
        sql="""
            CREATE TABLE IF NOT EXISTS events_daily (
                day  Date,
                user_id String,
                events UInt64
            ) ENGINE = MergeTree()
            ORDER BY (day, user_id);
        """,
    )

    aggregate = SQLExecuteQueryOperator(
        task_id="aggregate_events",
        sql="""
            INSERT INTO events_daily
            SELECT toDate(ts), user_id, count()
            FROM events
            WHERE toDate(ts) = yesterday()
            GROUP BY toDate(ts), user_id;
        """,
    )

    create_table &gt;&gt; aggregate
</code></pre>

![](https://clickhouse.com/uploads/airflow_sep2026_dag_5081933f5c.png)

For workloads that don't fit a SQL operator, `ClickHouseHook` gets you to the underlying client:

<pre><code type='click-ui' language='python'>
from airflow.providers.clickhousedb.hooks.clickhouse import ClickHouseHook

hook = ClickHouseHook(clickhouse_conn_id="clickhouse_default")
hook.bulk_insert_rows(
    table="events",
    rows=[("user1", "click"), ("user2", "view")],
    column_names=["user_id", "action"],
    batch_size=1000,
)
</code></pre>

The full walkthrough, including session settings, per-task database overrides, and connection options, is in [our docs](https://clickhouse.com/docs/integrations/airflow). If you'd rather see it live, Bentsi Leviav [demoed the provider](https://youtu.be/f4jNltAxgIA?t=894) as part of the ecosystem talk at [Open House 2026](https://clickhouse.com/blog/open-house-2026-day-2#apache-airflow-native-provider), our user conference back in May.

## Getting started with Astronomer {#getting_started_with_astronomer}

[Astronomer](https://www.astronomer.io/) is the managed Airflow platform many of our customers run in production, and the [Astro CLI](https://www.astronomer.io/docs/astro/cli/overview) is the fastest way to get a local Airflow environment running. The provider works out of the box.

First, install the CLI and scaffold a project:

<pre><code type='click-ui' language='bash'>
brew install astro
astro dev init
</code></pre>

Add the provider to the `requirements.txt` in your new project:

```shell
apache-airflow-providers-clickhousedb
```

Then start Airflow locally:

<pre><code type='click-ui' language='bash'>
astro dev start
</code></pre>

This spins up the Airflow components in containers on your machine. Once it's up, open the Airflow UI at `localhost:8080`, head to **Admin > Connections**, and create a connection with the **ClickHouse** type, pointing at your ClickHouse Cloud service or self-hosted cluster (remember `secure: true` and port `8443` for TLS).

Drop the DAG from the section above into the `dags/` folder and it'll appear in the UI, ready to trigger.

If you're running on Astro, there's an even more turnkey path for the connection. The [Environment Manager](https://www.astronomer.io/docs/astro/create-and-link-connections) in the Astro UI lets you create the ClickHouse connection once, store the credentials in Astro's managed secrets backend, and share it across every deployment in your workspace, with per-deployment overrides where you need them. The Astro CLI can [pull those same connections into your local environment](https://www.astronomer.io/docs/astro/cli/local-connections), so you configure ClickHouse once and use it everywhere, local or hosted.

![](https://clickhouse.com/uploads/airflow_sep2026_astronomer_e98964a5d8.png)

When you're ready for production, `astro deploy` ships the same project, provider and all, to your Astro deployment. Nothing about the ClickHouse setup changes between local and production.

## What's next {#whats_next}

The provider is available today and is already being used in production at scale by early adopters. We'll be prioritizing new capabilities based on what the community asks for, so if there's something you need, [open an issue or a PR](https://github.com/apache/airflow) and let us know.

If you're orchestrating ClickHouse with Airflow today, we'd love to hear how it's going. Come say hi in the [ClickHouse Community Slack](https://clickhouse.com/slack), and if you're new to ClickHouse, you can [get started with ClickHouse Cloud](https://console.clickhouse.cloud/signUp) in minutes with $300 in free credits. We can't wait to see what you build with it.


---

## Get started today

Interested in seeing how ClickHouse works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-2112-get-started-today-sign-up&utm_blogctaid=2112)

---