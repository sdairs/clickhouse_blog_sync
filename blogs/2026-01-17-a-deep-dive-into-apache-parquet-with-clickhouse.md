---
title: "A Deep Dive into Apache Parquet with ClickHouse - Part 1"
date: "2023-04-17T16:55:22.850Z"
author: "Dale McDiarmid"
category: "Engineering"
excerpt: "Learn out about how to query and write Apache Parquet files in the first post of our series on the popular data exchange format"
---

# A Deep Dive into Apache Parquet with ClickHouse - Part 1

![Parquet Intro.png](https://clickhouse.com/uploads/Parquet_Intro_e2d2a428ad.png)

## Introduction

Since its [release in 2013](https://blog.twitter.com/engineering/en_us/a/2013/announcing-parquet-10-columnar-storage-for-hadoop) as a columnar storage for Hadoop, Parquet has become almost ubiquitous as a file interchange format that offers efficient storage and retrieval. This adoption has led to it becoming the foundation for more recent data lake formats, e.g., [Apache Iceberg](https://iceberg.apache.org/). In this blog series, we explore how ClickHouse can be used to read and write this format before diving into the Parquet in more detail. For more experienced Parquet users, we also discuss some optimizations that users can make when writing Parquet files using ClickHouse to maximize compression, as well as some recent developments to optimize read performance using parallelization.

For our examples, we utilize the [UK house price](https://clickhouse.com/docs/en/getting-started/example-datasets/uk-price-paid) dataset. This contains data about prices paid for real estate property in England and Wales, from 1995 to the time of writing. We distribute this in Parquet format in the public s3 bucket `s3://datasets-documentation/uk-house-prices/parquet/`.

### ClickHouse Local

For our examples, we use local and S3-hosted Parquet files, querying these with [ClickHouse Local](https://clickhouse.com/blog/extracting-converting-querying-local-files-with-sql-clickhouse-local). ClickHouse Local is an easy-to-use version of ClickHouse that is ideal for developers who need to perform fast processing on local and remote files using SQL without having to install a full database server. Designed and optimized for data analysis using the local compute resources on your laptop or workstation, users can query, filter, and transform data files in almost any format using only SQL and without having to write a single line of Python code. We recommend this recent blog post for an overview of this tool's capabilities. Most importantly, ClickHouse Local and ClickHouse Server share the same code for Parquet reading and writing, so any explanations apply to both.

## What is Parquet?

The [official description](https://parquet.apache.org/) for Apache Parquet provides an excellent summary of its design and properties: “Apache Parquet is an open source, **column-oriented** data file format designed for **efficient data storage** and **retrieval**”. 

Similar to ClickHouse’s [MergeTree format](https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/mergetree), data is stored [column-oriented](https://clickhouse.com/docs/en/intro#why-column-oriented-databases-work-better-in-the-olap-scenario). This effectively means values of the same column are stored together, in contrast to row-oriented file formats (e.g., Avro), where row data is colocated. 

This data orientation, along with support for a number of [encoding techniques](https://parquet.apache.org/docs/file-format/data-pages/encodings/) suited to the modern processors’ pipeline, allows for a high compression rate and efficient storage property. Column orientation additionally minimizes the amount of data read, as only the necessary columns are read from storage for analytical queries such as group bys. When coupled with high compression rates and internal statistics provided on each column (stored as metadata), Parquet also promises fast retrieval. 

This latter property largely depends on the full exploitation of the metadata, the level of parallelization in any query engine, and the decisions made when storing the data. We discuss these below in relation to ClickHouse.

Before we dig into the internals of Parquet, we’ll cover how ClickHouse supports the writing and reading of this format.

## Querying Parquet with ClickHouse

In the example below, we assume our house price data has been exported to a single `house_prices.parquet` file and the use of ClickHouse Local to query unless stated otherwise.

### Reading schemas

Identifying the schema of any file can be achieved with the [DESCRIBE statement](https://clickhouse.com/docs/en/sql-reference/statements/describe-table) and [file table function](https://clickhouse.com/docs/en/sql-reference/functions/files#file):

```sql
DESCRIBE TABLE file('house_prices.parquet')

┌─name──────┬─type─────────────┬
│ price 	│ Nullable(UInt32) │
│ date  	│ Nullable(UInt16) │
│ postcode1 │ Nullable(String) │
│ postcode2 │ Nullable(String) │
│ type  	│ Nullable(Int8)   │
│ is_new	│ Nullable(UInt8)  │
│ duration  │ Nullable(Int8)   │
│ addr1 	│ Nullable(String) │
│ addr2 	│ Nullable(String) │
│ street	│ Nullable(String) │
│ locality  │ Nullable(String) │
│ town  	│ Nullable(String) │
│ district  │ Nullable(String) │
│ county	│ Nullable(String) |
└───────────┴──────────────────┴
```

### Querying local files

This above file table function can be used as the input to a `SELECT` query, allowing us to execute queries over the Parquet file. Below we compute the average price per year for properties in London.

```sql
SELECT
	toYear(toDate(date)) AS year,
	round(avg(price)) AS price,
	bar(price, 0, 2000000, 100)
FROM file('house_prices.parquet')
WHERE town = 'LONDON'
GROUP BY year
ORDER BY year ASC

┌─year─┬───price─┬─bar(round(avg(price)), 0, 2000000, 100)──────────────┐
│ 1995 │  109120 │ █████▍                                            	│
│ 1996 │  118672 │ █████▉                                            	│
│ 1997 │  136530 │ ██████▊                                           	│
│ 1998 │  153014 │ ███████▋                                          	│
│ 1999 │  180639 │ █████████                                         	│
│ 2000 │  215860 │ ██████████▊                                       	│
│ 2001 │  232998 │ ███████████▋                                      	│
│ 2002 │  263690 │ █████████████▏                                    	│
│ 2003 │  278423 │ █████████████▉                                    	│
│ 2004 │  304666 │ ███████████████▏                                  	│
│ 2005 │  322886 │ ████████████████▏                                 	│
│ 2006 │  356189 │ █████████████████▊                                	│
│ 2007 │  404065 │ ████████████████████▏                             	│
│ 2008 │  420741 │ █████████████████████                             	│
│ 2009 │  427767 │ █████████████████████▍                            	│
│ 2010 │  480329 │ ████████████████████████                          	│
│ 2011 │  496293 │ ████████████████████████▊                         	│
│ 2012 │  519473 │ █████████████████████████▉                        	│
│ 2013 │  616182 │ ██████████████████████████████▊                   	│
│ 2014 │  724107 │ ████████████████████████████████████▏             	│
│ 2015 │  792274 │ ███████████████████████████████████████▌          	│
│ 2016 │  843685 │ ██████████████████████████████████████████▏       	│
│ 2017 │  983673 │ █████████████████████████████████████████████████▏	│
│ 2018 │ 1016702 │ ██████████████████████████████████████████████████▊  │
│ 2019 │ 1041915 │ ████████████████████████████████████████████████████ │
│ 2020 │ 1060936 │ █████████████████████████████████████████████████████│
│ 2021 │  968152 │ ████████████████████████████████████████████████▍ 	│
│ 2022 │  967439 │ ████████████████████████████████████████████████▎ 	│
│ 2023 │  830317 │ █████████████████████████████████████████▌        	│
└──────┴─────────┴──────────────────────────────────────────────────────┘

29 rows in set. Elapsed: 0.625 sec. Processed 28.11 million rows, 750.65 MB (44.97 million rows/s., 1.20 GB/s.)
```

### Querying files on S3

While the above file function can be used with ClickHouse server instances, it requires files to be present on the server filesystem under the configured [user_files_path](https://clickhouse.com/docs/en/operations/server-configuration-parameters/settings#server_configuration_parameters-user_files_path) directory. Parquet files are more naturally read from S3 in these circumstances. This is a common requirement in data lake use cases where ad hoc analysis is required. The above file function can be replaced with the [s3 function](https://clickhouse.com/docs/en/sql-reference/table-functions/s3) in this case, for AWS Athena like querying:

```sql
SELECT
	toYear(toDate(date)) AS year,
	round(avg(price)) AS price,
	bar(price, 0, 2000000, 100)
FROM s3('https://datasets-documentation.s3.eu-west-3.amazonaws.com/uk-house-prices/parquet/house_prices_all.parquet')
WHERE town = 'LONDON'
GROUP BY year
ORDER BY year ASC

┌─year─┬───price─┬─bar(round(avg(price)), 0, 2000000, 100)───────────────┐
│ 1995 │  109120 │ █████▍                                            	 │
│ 1996 │  118672 │ █████▉                                             	 │
│ 1997 │  136530 │ ██████▊                                           	 │
│ 1998 │  153014 │ ███████▋                                          	 │
│ 1999 │  180639 │ █████████                                         	 │

...

29 rows in set. Elapsed: 2.069 sec. Processed 28.11 million rows, 750.65 MB (13.59 million rows/s., 362.87 MB/s.)
```

### Querying multiple files

Both of these functions support glob patterns, allowing subsets of files to be selected. As we will discuss in a later post, this provides advantages beyond just querying across files - principally parallelization of reads. Below we limit our query to all `house_prices_` files with a year suffix - this assumes we have a file per year (see below).

```sql
SELECT
	toYear(toDate(date)) AS year,
	round(avg(price)) AS price,
	bar(price, 0, 2000000, 100)
FROM s3('https://datasets-documentation.s3.eu-west-3.amazonaws.com/uk-house-prices/parquet/house_prices_{1..2}*.parquet')
WHERE town = 'LONDON'
GROUP BY year
ORDER BY year ASC

29 rows in set. Elapsed: 3.387 sec. Processed 28.11 million rows, 750.65 MB (8.30 million rows/s., 221.66 MB/s.)
```

Users should also be aware of the [s3Cluster](https://clickhouse.com/docs/en/sql-reference/table-functions/s3Cluster) function, which allows the processing of files in parallel from many nodes in a cluster - particularly relevant to ClickHouse Cloud users. This can provide significant performance benefits, especially in cases where there are many files to be read (allowing work to be distributed).

## Writing Parquet with ClickHouse

Writing table data in ClickHouse to Parquet files can be achieved in a few ways. The preferred option here typically depends on if you are utilizing ClickHouse Server or ClickHouse Local. In the examples below, we assume a `uk_price_paid` table has been populated with the data. See [here](https://clickhouse.com/docs/en/getting-started/example-datasets/uk-price-paid) for details on loading this.

### Writing local files

Using the [`INTO FUNCTION`](https://clickhouse.com/docs/en/sql-reference/statements/insert-into#inserting-into-table-function) clause, we can write parquet using the same file function as for reading. This is most appropriate for ClickHouse Local, where files can be written to any location on the local filesystem. ClickHouse server will write these to the directory specified by the configuration parameter [`user_files_path`](https://clickhouse.com/docs/en/operations/server-configuration-parameters/settings#server_configuration_parameters-user_files_path).

```sql
INSERT INTO FUNCTION file('house_prices.parquet') SELECT *
FROM uk_price_paid

0 rows in set. Elapsed: 12.490 sec. Processed 28.11 million rows, 1.32 GB (2.25 million rows/s., 105.97 MB/s.)

dalemcdiarmid@dales-mac houseprices % ls -lh house_prices.parquet
-rw-r-----  1 dalemcdiarmid  staff   243M 17 Apr 16:59 house_prices.parquet
```

In most cases, including ClickHouse Cloud, the local server filesystem is not accessible. In these cases, users can connect via `clickhouse-client` and utilize the INTO OUTFILE clause to write the parquet file to the client’s filesystem. The desired out format will be auto-detected here based on the file extension. 

```sql
SELECT *
FROM uk_price_paid
INTO OUTFILE 'house_prices.parquet'

28113076 rows in set. Elapsed: 15.690 sec. Processed 28.11 million rows, 2.47 GB (1.79 million rows/s., 157.47 MB/s.)

clickhouse@clickhouse-mac ~ % ls -lh house_prices.parquet
-rw-r--r--  1 dalemcdiarmid  staff   291M 17 Apr 18:23 house_prices.parquet
```

Alternatively, users can simply issue a SELECT query, specifying the output format as Parquet, and redirecting the results to a file. In this example, we pass the `--query` parameter to the client from the terminal.

```bash
clickhouse@clickhouse-mac ~ % ./clickhouse client --query "SELECT * FROM uk_price_paid FORMAT Parquet" > house_price.parquet
```

These last 2 approaches produce a slightly larger file than our previous file function approach. We will explain why in part 2 of this series, but for now users are recommended to use the earlier `INSERT INTO FUNCTION` approach where possible for more optimal sizes.

### Writing files to S3

Often, client storage is limited. In these cases, users may wish to write files to object storage such as S3 and GCS. These are both supported via the same [s3 function](https://clickhouse.com/docs/en/sql-reference/table-functions/s3) as used for reading. Note that credentials will be required - in the example below, we pass these as function parameters, but [IAM credentials are also supported](https://clickhouse.com/docs/en/integrations/s3#managing-credentials).

```sql
INSERT INTO FUNCTION s3('https://datasets-documentation.s3.eu-west-3.amazonaws.com/uk-house-prices/parquet/house_prices_sample.parquet', '<aws_access_key_id>', '<aws_secret_access_key>') SELECT *
FROM uk_price_paid
LIMIT 1000

0 rows in set. Elapsed: 0.726 sec. Processed 2.00 thousand rows, 987.86 KB (2.75 thousand rows/s., 1.36 MB/s.)
```

### Writing multiple files

Finally, it is often desirable to limit the size of any single Parquet file. To assist with writing to files, users can utilize the PARTITION BY clause with the [`INTO FUNCTION`](https://clickhouse.com/docs/en/sql-reference/statements/insert-into#inserting-into-table-function) clause. This accepts any SQL expression to create a partition id for each row in the result set. This `parition_id` can, in turn, be used in the file path to ensure rows are assigned to distinct files. In the example below, we partition by year. House sales belonging to the same year will therefore be written to the same file. Files will be suffixed with their respective year as shown.

```bash
INSERT INTO FUNCTION file('house_prices_{_partition_id}.parquet') PARTITION BY toYear(date) SELECT * FROM uk_price_paid

0 rows in set. Elapsed: 23.281 sec. Processed 28.11 million rows, 1.32 GB (1.21 million rows/s., 56.85 MB/s.)

clickhouse@clickhouse-mac houseprices % ls house_prices_*
house_prices_1995.parquet    house_prices_2001.parquet    house_prices_2007.parquet    house_prices_2013.parquet    house_prices_2019.parquet
house_prices_1996.parquet    house_prices_2002.parquet    house_prices_2008.parquet    house_prices_2014.parquet    house_prices_2020.parquet
house_prices_1997.parquet    house_prices_2003.parquet    house_prices_2009.parquet    house_prices_2015.parquet    house_prices_2021.parquet
house_prices_1998.parquet    house_prices_2004.parquet    house_prices_2010.parquet    house_prices_2016.parquet    house_prices_2022.parquet
house_prices_1999.parquet    house_prices_2005.parquet    house_prices_2011.parquet    house_prices_2017.parquet    house_prices_2023.parquet
house_prices_2000.parquet    house_prices_2006.parquet    house_prices_2012.parquet    house_prices_2018.parquet
```

This same approach can be used with the s3 function.

```sql
INSERT INTO FUNCTION s3('https://datasets-documentation.s3.eu-west-3.amazonaws.com/uk-house-prices/parquet/house_prices_sample_{_partition_id}.parquet', '<aws_access_key_id>', '<aws_secret_access_key>') PARTITION BY toYear(date) SELECT *
FROM uk_price_paid
LIMIT 1000

0 rows in set. Elapsed: 2.247 sec. Processed 2.00 thousand rows, 987.86 KB (889.92 rows/s., 439.56 KB/s.)
```

At the time of writing, this `PARTITION BY` clause is [not currently supported](https://github.com/ClickHouse/ClickHouse/issues/30274) for `INTO OUTFILE`. 

## Converting files to Parquet

Combining the above allows us to convert files between formats using ClickHouse Local. In the example below, we use ClickHouse Local with the file function to read a local copy of the house price dataset in CSV format, containing all 28m rows, before writing it to S3 as Parquet. These files are partitioned the data by year as shown earlier.

```sql
INSERT INTO FUNCTION s3('https://datasets-documentation.s3.eu-west-3.amazonaws.com/uk-house-prices/parquet/house_prices_sample_{_partition_id}.parquet', '<aws_access_key_id>', '<aws_secret_access_key>') PARTITION BY toYear(date) SELECT *
FROM file('house_prices.csv')

0 rows in set. Elapsed: 223.864 sec. Processed 28.11 million rows, 5.87 GB (125.58 thousand rows/s., 26.24 MB/s.)
```

![s3_files_parquet.png](https://clickhouse.com/uploads/s3_files_parquet_6cc0a22093.png)

## Inserting Parquet files into ClickHouse

All of the previous examples assume users are querying local and S3-hosted files for ad hoc analysis or migrating data out of ClickHouse to Parquet for distribution. While Parquet is a data store agnostic format for file distribution, it will not be as efficient for querying as ClickHouse MergeTree tables, with the latter able to [exploit indexes](https://clickhouse.com/docs/en/getting-started/example-datasets/metrica#next-steps) and format-specific optimizations. Consider the performance of the following query, which computes the average price per year for properties in London using a local Parquet file and MergeTree table with the [recommended schema](https://clickhouse.com/docs/en/getting-started/example-datasets/uk-price-paid#create-table) (both run on Macbook Pro 2021):

```sql
SELECT
	toYear(toDate(date)) AS year,
	round(avg(price)) AS price,
	bar(price, 0, 2000000, 100)
FROM file('house_prices.parquet')
WHERE town = 'LONDON'
GROUP BY year
ORDER BY year ASC

29 rows in set. Elapsed: 0.625 sec. Processed 28.11 million rows, 750.65 MB (44.97 million rows/s., 1.20 GB/s.)

SELECT
	toYear(toDate(date)) AS year,
	round(avg(price)) AS price,
	bar(price, 0, 2000000, 100)
FROM uk_price_paid
WHERE town = 'LONDON'
GROUP BY year
ORDER BY year ASC

29 rows in set. Elapsed: 0.022 sec.
```

The difference here is dramatic and justifies why for large datasets requiring real-time performance, users load Parquet files into ClickHouse. Below we assume the `uk_price_paid` table has been pre-created.

### Loading from local files

Files can be loaded from client machines using the [`INFILE`](https://clickhouse.com/docs/en/sql-reference/statements/insert-into#single-file-with-from-infile) clause. The following query is executed from the `clickhouse-client` and reads data from the local client’s file system.

```sql
INSERT INTO uk_price_paid FROM INFILE 'house_price.parquet' FORMAT Parquet
28113076 rows in set. Elapsed: 15.412 sec. Processed 28.11 million rows, 1.27 GB (1.82 million rows/s., 82.61 MB/s.)
```

This approach also [supports glob patterns](https://clickhouse.com/docs/en/sql-reference/statements/insert-into#multiple-files-with-from-infile-using-globs) should the user's data be spread across multiple Parquet files. Alternatively, Parquet files can be re-directed into the `clickhouse-client` using the `--query` parameter:

```bash
clickhouse@clickhouse-mac ~ % ~/clickhouse client --query "INSERT INTO uk_price_paid FORMAT Parquet" < house_price.parquet
```

### Loading from S3

With client storage often limited and with the rise of object storage-based data lakes, Parquet files often reside on S3 or GCS. Again, we can use the s3 function to read these files, inserting their data into a MergeTree table with the [INSERT INTO SELECT](https://clickhouse.com/docs/en/sql-reference/statements/insert-into#inserting-the-results-of-select) clause. In the example below, we utilize a glob pattern to read files partitioned by year, executing this query on a three-node ClickHouse Cloud cluster.

```sql
INSERT INTO uk_price_paid SELECT *
FROM s3('https://datasets-documentation.s3.eu-west-3.amazonaws.com/uk-house-prices/parquet/house_prices_{1..2}*.parquet')

0 rows in set. Elapsed: 12.028 sec. Processed 28.11 million rows, 4.64 GB (2.34 million rows/s., 385.96 MB/s.)
```

Similar to reading, this can be accelerated by using the [s3Cluster](https://clickhouse.com/docs/en/sql-reference/table-functions/s3Cluster) function. To ensure inserts and reads are distributed across the cluster, the setting [`parallel_distributed_insert_select`](https://clickhouse.com/docs/en/operations/settings/settings#parallel_distributed_insert_select) must be enabled (otherwise, only reads will be distributed, and inserts will be sent to the coordinating node). The following query is run on the same Cloud cluster used in the previous example, showing the benefit of parallelizing this work.

```sql
SET parallel_distributed_insert_select=1
INSERT INTO uk_price_paid SELECT *
FROM s3Cluster('default', 'https://datasets-documentation.s3.eu-west-3.amazonaws.com/uk-house-prices/parquet/house_prices_{1..2}*.parquet')

0 rows in set. Elapsed: 6.425 sec. Processed 28.11 million rows, 4.64 GB (4.38 million rows/s., 722.58 MB/s.)
```

## Conclusion

In this blog series's first part, we introduced the Parquet format and showed how this could be queried and written using ClickHouse. In the next post, we will dive into the format in more detail, further exploring the ClickHouse integration and recent performance improvements and tips for optimizing your queries.



