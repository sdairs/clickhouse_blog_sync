---
title: "ClickPy reaches one trillion rows"
date: "2024-08-27T15:25:02.295Z"
author: "ClickHouse Team"
category: "Product"
excerpt: "ClickPy, a free service built on top of ClickHouse that lets you run real-time analytics on PyPi package downloads, has reached 1 trillion rows."
---

# ClickPy reaches one trillion rows

[PyPi](https://pypi.org/) (Python Package Index) is the software repository for the Python programming language. It sits at the center of the Python ecosystem, where various libraries are downloaded almost 2 billion times daily.

Metadata related to those downloads can be accessed in BigQuery. This is fine for doing ad-hoc queries, but we wanted to create a user-facing service that lets users explore their favorite packages.

Enter [ClickPy](https://clickpy.clickhouse.com/), a free service built on top of ClickHouse that lets you run real-time analytics on PyPi package downloads. The code is also open-source and available [on GitHub](https://github.com/ClickHouse/clickpy) so that you can run the service locally.

![0_Google Keep (1).png](https://clickhouse.com/uploads/0_Google_Keep_1_fa9128f2fa.png)

ClickPy has been live for around 9 months, and a couple of weeks ago, the main table in the database exceeded **1 trillion rows,** representing 1 trillion downloads of various libraries.

This blog post will explain how we built the application and handled such a large dataset.

## Modeling the data

This project contains data for three broad entities:

* Countries - country name and code.
* Projects - metadata about each PyPi project.
* Downloads - metadata about each project installation.

We’re going to create one table for each dataset. They will be called `countries`, `projects,` and `pypi,` respectively.

`pypi` contains the most data since every download is one row, and we have a lot of rows! Therefore, we will create downstream tables for common query patterns and corresponding materialized views to populate those tables. The diagram below shows all the tables that we’ll create:


![ClickPy 1 Trillion Rows Banner (1).png](https://clickhouse.com/uploads/Click_Py_1_Trillion_Rows_Banner_1_f5d4a623f9.png)

ClickHouse also supports dictionaries, which are in-memory key-value pairs useful for reference data. We will create dictionaries for countries, mapping the country code to the country name, and another for projects, mapping the project name to the last update time.

## Ingesting the data

The underlying data for the projects and downloads is available in BigQuery. However, exporting the data takes several hours, so we exported the data into Google Cloud Storage buckets as Parquet files. You can find the [query to do this](https://github.com/ClickHouse/clickpy?tab=readme-ov-file#exporting-data) in the ClickPy GitHub repository. 

We then import the data into two tables: `projects` and `pypi`. We won’t go into the queries to create those tables, but you can [find the queries in this file](https://github.com/ClickHouse/clickpy/blob/a2d71004cb30e67c703741e50ccb6d8b1d0a0066/ClickHouse.md?plain=1#L471).

We can then run the following query to import the projects:


```sql
INSERT INTO projects 
SELECT *
FROM s3(
'https://storage.googleapis.com/clickhouse_public_datasets/pypi/packages/packages-*.parquet'
)
```

And the following query to import the downloads:

```sql
INSERT INTO pypi 
SELECT timestamp::Date as date, country_code, project, file.type as type, 
       installer.name as installer, 
       arrayStringConcat(arraySlice(splitByChar('.', python), 1, 2), '.') as python_minor, 
       system.name as system, file.version as version 
FROM s3(
  'https://<bucket>/file_downloads-00000000001*.parquet', 
  'Parquet', 
  'timestamp DateTime64(6), country_code LowCardinality(String), url String, project String, `file.filename` String, `file.project` String, `file.version` String, `file.type` String, `installer.name` String, `installer.version` String, python String, `implementation.name` String, `implementation.version` String, `distro.name` String, `distro.version` String, `distro.id` String, `distro.libc.lib` String, `distro.libc.version` String, `system.name` String, `system.release` String, cpu String, openssl_version String, setuptools_version String, rustc_version String,tls_protocol String, tls_cipher String') 
WHERE python_minor != '' AND system != '' 
SETTINGS input_format_null_as_default = 1, 
         input_format_parquet_import_nested = 1

```

We used this script to load the first 600 billion rows. We then have [a cron job](https://github.com/ClickHouse/ClickLoad#running) that runs every hour and extracts the new rows that have been added since the last time it ran and exports those into Parquet files as well. There are then some workers that pick up those Parquet files and ingest them into ClickHouse. The tool that does this is called  ClickLoad and you can read more about it in [this blog post](https://clickhouse.com/blog/supercharge-your-clickhouse-data-loads-part3).

![ClickPy 1 Trillion Rows Banner.png](https://clickhouse.com/uploads/Click_Py_1_Trillion_Rows_Banner_af6fbffea7.png)

Finally, we have a CSV file containing countries that we import using the following query:

```sql
INSERT INTO pypi.countries 
SELECT name,  `alpha-2` AS code
FROM url(
'https://gist.githubusercontent.com/gingerwizard/963e2aa7b0f65a3e8761ce2d413ba02c/raw/4b09800f48d932890eedd3ec5f7de380f2067947/country_codes.csv'
)
```

Let’s also look at the materialized view that populates one of the downstream tables from `pypi`. In ClickHouse, materialized views are bits of SQL executed whenever rows are inserted into the upstream table.

```sql
CREATE MATERIALIZED VIEW pypi.pypi_downloads_per_day_by_version_by_system_mv 
TO pypi.pypi_downloads_per_day_by_version_by_system (
  `date` Date, 
  `project` String, 
  `version` String, 
  `system` String, 
  `count` Int64
) AS 
SELECT date, project, version, system, count() AS count 
FROM pypi.pypi 
GROUP BY date, project, version, system
```

We have one of these materialized views for each downstream table described in the modeling section above.

## ClickPy’s frontend

The front end for ClickPy is written in Next.JS and React. The app code is [also available in the GitHub repository](https://github.com/ClickHouse/clickpy/tree/main/src).

The home page contains an overview of all the pages, showing emerging repositories, popular ones that haven’t been updated in a while, recent releases, and more. You can click through to any of the linked projects:

![1_browser_projects.png](https://clickhouse.com/uploads/1_browser_projects_d0c5e7bb1f.png)

Alternatively, you can search for your favorite project in the search bar.

![2_Google Keep (2).png](https://clickhouse.com/uploads/2_Google_Keep_2_d6964cc26a.png)

Let’s look at the [openai](https://clickpy.clickhouse.com/dashboard/openai) library, which interacts with OpenAI’s APIs. If we search for `openai` and click on the first result, we’ll see the following page:

![3_Google Keep (3).png](https://clickhouse.com/uploads/3_Google_Keep_3_77f7387d6b.png)

The top part of the page includes some data pulled from GitHub, but below that are download statistics. Each widget has an arrow button, which, when clicked, will take us to the Play UI with the query underlying the widget pre-filled. 

For example, we’ll see [this query](https://clickpy-clickhouse.clickhouse.com/play?user=play&url=https://clickpy-clickhouse.clickhouse.com?param_package_name%3Dopenai%26param_min_date%3D2011-01-01%26param_max_date%3D2024-08-20#U0VMRUNUCiAgICAgICAgICAgIHZlcnNpb24gQVMgbmFtZSwKICAgICAgICAgICAgc3VtKGNvdW50KSBBUyB2YWx1ZQogICAgICAgIEZST00gcHlwaS5weXBpX2Rvd25sb2Fkc19wZXJfZGF5X2J5X3ZlcnNpb24KICAgICAgICBXSEVSRSAoZGF0ZSA+PSB7bWluX2RhdGU6U3RyaW5nfTo6RGF0ZTMyKSBBTkQgKGRhdGUgPCB7bWF4X2RhdGU6U3RyaW5nfTo6RGF0ZTMyKSBBTkQgKHByb2plY3QgPSB7cGFja2FnZV9uYW1lOlN0cmluZ30pIAogICAgICAgICAgICBBTkQgMT0xIEFORCAxPTEgQU5EIDE9MQogICAgICAgIEdST1VQIEJZIHZlcnNpb24gT1JERVIgQlkgdmFsdWUgREVTQyBMSU1JVCA2) if we click on the ‘Top Versions’ query:

![4_Google Keep (4).png](https://clickhouse.com/uploads/4_Google_Keep_4_f1f0dd500f.png)


The latest version of the OpenAI library at the time of writing is 1.41.0, but way more people downloaded a version first released in September 2023.

## Querying the data 

In addition to using the Play UI, if you want to query the data directly, you can connect to the database using the read-only `play `user using ClickHouse Client:

```sql
./clickhouse client \
  -h clickpy-clickhouse.clickhouse.com \
  --user play --secure \
  --database pypi
```

You can see a list of the tables available to query by running the following:

```sql
SHOW TABLES

┌─name─────────────────────────────────────────────────────────────────┐
│ countries                                                            │
│ countries_dict                                                       │
│ last_updated_dict                                                    │
│ projects                                                             │
│ pypi                                                                 │
│ pypi_downloads                                                       │
│ pypi_downloads_by_version                                            │
│ pypi_downloads_by_version_mv                                         │
│ pypi_downloads_max_min                                               │
│ pypi_downloads_max_min_mv                                            │
│ pypi_downloads_mv                                                    │
│ pypi_downloads_per_day                                               │
│ pypi_downloads_per_day_by_version                                    │
│ pypi_downloads_per_day_by_version_by_country                         │
│ pypi_downloads_per_day_by_version_by_country_mv                      │
│ pypi_downloads_per_day_by_version_by_file_type                       │
│ pypi_downloads_per_day_by_version_by_file_type_mv                    │
│ pypi_downloads_per_day_by_version_by_installer_by_type               │
│ pypi_downloads_per_day_by_version_by_installer_by_type_by_country    │
│ pypi_downloads_per_day_by_version_by_installer_by_type_by_country_mv │
│ pypi_downloads_per_day_by_version_by_installer_by_type_mv            │
│ pypi_downloads_per_day_by_version_by_python                          │
│ pypi_downloads_per_day_by_version_by_python_by_country               │
│ pypi_downloads_per_day_by_version_by_python_by_country_mv            │
│ pypi_downloads_per_day_by_version_by_python_mv                       │
│ pypi_downloads_per_day_by_version_by_system                          │
│ pypi_downloads_per_day_by_version_by_system_by_country               │
│ pypi_downloads_per_day_by_version_by_system_by_country_mv            │
│ pypi_downloads_per_day_by_version_by_system_mv                       │
│ pypi_downloads_per_day_by_version_mv                                 │
│ pypi_downloads_per_day_mv                                            │
│ pypi_downloads_per_month                                             │
│ pypi_downloads_per_month_mv                                          │
└──────────────────────────────────────────────────────────────────────┘
```
There’s a limit of 10 billion rows read per query, so you probably don’t want to query the `pypi` table since you’ll likely exceed the limit.

The other tables have a lot fewer rows, so we could, for example, write the following query to compute the number of downloads of pandas over the last 10 days and also show a nice little bar chart:

```sql
WITH downloadsPerDay AS (
   SELECT date, sum(count) AS count
   FROM pypi.pypi_downloads_per_day
   WHERE (date >= (now() - (((10 * 24) * 60) * 60))) AND (project = 'pandas')
   GROUP BY ALL
)

SELECT date, count,
    formatReadableQuantity(count) AS readableSize,
    bar(count, 0, (SELECT max(count) FROM downloadsPerDay), 10) AS bar
FROM downloadsPerDay

GROUP BY ALL
ORDER BY date ASC

┌───────date─┬───count─┬─readableSize─┬─bar────────┐
│ 2024-08-12 │ 9787106 │ 9.79 million │ █████████▉ │
│ 2024-08-13 │ 9727401 │ 9.73 million │ █████████▉ │
│ 2024-08-14 │ 9309011 │ 9.31 million │ █████████▍ │
│ 2024-08-15 │ 8825396 │ 8.83 million │ ████████▉  │
│ 2024-08-16 │ 9428220 │ 9.43 million │ █████████▌ │
│ 2024-08-17 │ 5915869 │ 5.92 million │ ██████     │
│ 2024-08-18 │ 5955829 │ 5.96 million │ ██████     │
│ 2024-08-19 │ 9118143 │ 9.12 million │ █████████▎ │
│ 2024-08-20 │ 9846985 │ 9.85 million │ ██████████ │
└────────────┴─────────┴──────────────┴────────────┘
```

We can see a pretty big dip over the weekend, but otherwise, it’s pretty steady at around 9 million daily downloads.

## What next?

More data will be ingested! Since we noticed that the 1 trillion milestone had been achieved, another 36 billion rows have been ingested.

We’d love for you to get involved with the ClickPy project. On the [project's issues page](https://github.com/ClickHouse/clickpy/issues/58), please let us know if you notice any issues or ideas you have for improving the app.

If you build any tools or apps on top of the data, tag us on Twitter [@clickhousedb,](https://x.com/@clickhousedb) and we’ll help promote them.