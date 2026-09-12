---
title: "Loading Parquet data into MySQL with ClickHouse"
date: "2026-09-11T13:17:45.862Z"
author: "Mark Needham"
category: "Engineering"
excerpt: "Use ClickHouse to load Parquet files into MySQL, explore remote data, and run MySQL queries with table functions and named collections."
---

# Loading Parquet data into MySQL with ClickHouse

A couple of weeks ago, I was working on a video for the [MySQL CDC connector for ClickPipes](https://clickhouse.com/blog/mysql-cdc-connector-for-clickpipes-is-now-generally-available) and I needed to get some data from Parquet files into MySQL. There isn't a native way to do this, so I decided to use [clickhouse-local](https://clickhouse.com/docs/concepts/features/tools-and-utilities/clickhouse-local), my favorite tool for doing this type of adhoc data work.

<iframe width="768" height="432" src="https://www.youtube.com/embed/PNkIYSVz-AU" frameborder="0" allowfullscreen></iframe>

## Setting up MySQL

I used AWS RDS for MySQL in the video, but to make it easier to reproduce, we'll use MySQL running on my machine for this blog post. We can launch MySQL by running the following:

```bash
docker run --name parquet-mysql \
    -p 127.0.0.1:3306:3306 \
    -e MYSQL_ROOT_PASSWORD=local-root-password \
    -e MYSQL_DATABASE=stackoverflow \
    -e MYSQL_USER=admin \
    -e MYSQL_PASSWORD=local-demo-password \
    -v parquet-mysql-data:/var/lib/mysql \
    mysql:8.4
```

## Setting up ClickHouse

We'll run ClickHouse via its binary, which we can download like this:

```bash
curl https://clickhouse.com | sh
```

We'll then launch it:

```bash
./clickhouse -mn \
--config-file ch-config.yaml \
--param_mysql_password "local-demo-password" \
--param_mysql_host "127.0.0.1:3306" \
--output-format Pretty
```

> **Tip**
>
> We're passing in the MySQL host and password in plain text because it's running on our machine. For a production system, we'd have those values stored in environment variables.

The contents of `ch-config.yaml` are shown below:

```yaml
echo: 0
users_config: ch-users.yaml
named_collections:
  mysql_demo:
    host: '127.0.0.01'
    port: 3306
    user: 'admin'
    password: 'local-demo-password'
    database: 'stackoverflow'
```

`ch-users.yaml` contains config for the default user. The named collection `mysql_demo` contains our MySQL credentials that we'll use later in the post.

## Exploring StackOverflow dataset

Now that we've got MySQL and ClickHouse running, let's explore our dataset. We're going to work with StackOverflow votes data, which lives in the following S3 bucket:

```sql
SET url_base = 'https://datasets-documentation.s3.eu-west-3.amazonaws.com/stackoverflow/parquet/votes/';
```

When using the `url` table function, the `url_base` parameter is prepended to relative paths so that we don't have to repeat the same base URL multiple times. We can describe the `2024.parquet` file in that bucket like this:

```sql
DESCRIBE url('2024.parquet');
```

```shell
┌──────────────┬──────────────────────┐
│ name         │ type                 │
├──────────────┼──────────────────────┤
│ Id           │ Int64                │
│ PostId       │ Int64                │
│ VoteTypeId   │ Int64                │
│ CreationDate │ DateTime64(3, 'UTC') │
│ UserId       │ Int64                │
│ BountyAmount │ UInt64               │
└──────────────┴──────────────────────┘

6 rows in set. Elapsed: 0.445 sec.
```

## Creating table in MySQL

Let's now connect to MySQL:

```bash
docker exec -it parquet-mysql mysql -u admin -p stackoverflow
```

And then run the following query to create a table to store this data:


```sql
CREATE TABLE votes_from_parquet
(
    Id           BIGINT NOT NULL PRIMARY KEY,
    PostId       BIGINT,
    VoteTypeId   BIGINT NOT NULL,
    CreationDate DATETIME(3) NOT NULL,
    UserId       BIGINT,
    BountyAmount BIGINT UNSIGNED DEFAULT 0
)
ENGINE = InnoDB;
```

```shell
Query OK, 0 rows affected (0.039 sec)
```


## Inserting data in MySQL

Back to ClickHouse we go to ingest the data.
We're going to use the [`mysql`](https://clickhouse.com/docs/reference/functions/table-functions/mysql) table function, as shown in the following query:

```sql
INSERT INTO FUNCTION mysql(
    {mysql_host:String},     -- MySQL host
    'stackoverflow',         -- MySQL database
    'votes_from_parquet',    -- MySQL table
    'admin',                 -- MySQL user
    {mysql_password:String}  -- MySQL password
)
(Id, PostId, VoteTypeId, CreationDate, UserId, BountyAmount)
SELECT Id, PostId, VoteTypeId, CreationDate, UserId, BountyAmount
FROM url('2024.parquet');
```

```shell
2296977 rows in set. Elapsed: 16.609 sec. Processed 2.30 million rows, 21.63 MB (138.29 thousand rows/s., 1.30 MB/s.)
Peak memory usage: 227.31 MiB.
```

## Querying MySQL from ClickHouse

We can also query MySQL by using the `mysql` table function in the `FROM` clause:

```sql
SELECT *
FROM mysql(
    {mysql_host:String},
    'stackoverflow',
    (
        SELECT count(*) AS `votes`
        FROM votes_from_parquet
        WHERE tuple(VoteTypeId, PostId) IN ((2, 37996101), (2, 802038))
    ),
    'admin',
    {mysql_password:String}
);
```

When we pass in the inner query like this, it uses ClickHouse syntax. ClickHouse parses it into a syntax tree, converts supported ClickHouse constructs into MySQL-valid SQL, and then sends the resulting query to MySQL for execution.

```shell
┏━━━━━━━┓
┃ votes ┃
┡━━━━━━━┩
│     5 │
└───────┘

1 row in set. Elapsed: 1.708 sec.
```

Alternatively, we can pass in the query as a string to the `query` function, but this time the query must be MySQL-SQL. ClickHouse treats it as an opaque string and sends it directly to MySQL without parsing or rewriting the SQL inside it. If we pass it as is, we'll get an exception:


```sql
SELECT *
FROM mysql(
    {mysql_host:String},
    'stackoverflow',
    query($sql$
        SELECT count(*) AS `votes`
        FROM votes_from_parquet
        WHERE tuple(VoteTypeId, PostId) IN ((2, 37996101), (2, 802038))
    $sql$),
    'admin',
    {mysql_password:String}
);
```

```shell
Received exception:
Code: 1000. DB::Exception: mysqlxx::BadQuery: FUNCTION stackoverflow.tuple does not exist while executing query: 'SELECT * FROM (
        SELECT count(*) AS `votes`
        FROM votes_from_parquet
        WHERE tuple(VoteTypeId, PostId) IN ((2, 37996101), (2, 802038))
    ) AS __subquery LIMIT 0' (127.0.0.1:3306). (POCO_EXCEPTION)
```

`tuple` doesn't exist in MySQL, so its unable to parse the query. But if we remove `tuple` and send this query, it'll work fine:

```sql
SELECT *
FROM mysql(
    {mysql_host:String},
    'stackoverflow',
    query($sql$
        SELECT count(*) AS `votes`
        FROM votes_from_parquet
        WHERE (VoteTypeId, PostId) IN ((2, 37996101), (2, 802038))
    $sql$),
    'admin',
    {mysql_password:String}
);
```

## Querying MySQL from ClickHouse with named collection

We can also query MySQL using the credentials that we defined in a named collection in our config file. We can query the server's named collections with this query:

```sql
SELECT *
FROM system.named_collections
FORMAT Vertical;
```

```shell
Row 1:
──────
name:         mysql_demo
collection:   {'database':'[HIDDEN]','host':'[HIDDEN]','password':'[HIDDEN]','port':'[HIDDEN]','user':'[HIDDEN]'}
source:       CONFIG
create_query:

1 row in set. Elapsed: 0.001 sec.
```

We can then pass in `mysql_demo` as the first argument, with the query being provided as a string:

```sql
SELECT *
FROM mysql(
    mysql_demo,
    query=$sql$
    SELECT count(*)
    FROM votes_from_parquet
    WHERE (VoteTypeId = 2 AND CreationDate = '2024-01-01')
    $sql$
);
```

```text
┌──────────┐
│ count(*) │
├──────────┤
│ 10067    │
└──────────┘

1 row in set. Elapsed: 1.100 sec.
```

Let's finish with one more query that finds the posts with both upvotes and downvotes:

```sql
SELECT * FROM mysql(mysql_demo, query = '
  SELECT PostId, upvotes, downvotes,
         upvotes + downvotes AS total_votes,
         ROUND(
           100.0 * LEAST(upvotes, downvotes) / (upvotes + downvotes),
           1
         ) AS balance_pct
        FROM
        (
          SELECT PostId, SUM(VoteTypeId = 2) AS upvotes, 
                 SUM(VoteTypeId = 3) AS downvotes
          FROM votes_from_parquet
          WHERE VoteTypeId IN (2, 3)
          GROUP BY PostId
        ) AS vote_totals
  WHERE upvotes > 0 AND downvotes > 0
  ORDER BY LEAST(upvotes, downvotes) DESC, total_votes DESC
  LIMIT 10'
);
```

```shell
┌──────────┬─────────┬───────────┬─────────────┬─────────────┐
│ PostId   │ upvotes │ downvotes │ total_votes │ balance_pct │
├──────────┼─────────┼───────────┼─────────────┼─────────────┤
│ 69699772 │ 205     │ 23        │ 228         │ 10.1        │
│ 69713899 │ 53      │ 9         │ 62          │ 14.5        │
│ 62099904 │ 37      │ 8         │ 45          │ 17.8        │
│ 10032024 │ 7       │ 16        │ 23          │ 30.4        │
│ 78114790 │ 7       │ 12        │ 19          │ 36.8        │
│ 62477194 │ 7       │ 9         │ 16          │ 43.8        │
│ 72231704 │ 8       │ 7         │ 15          │ 46.7        │
│ 77766725 │ 7       │ 8         │ 15          │ 46.7        │
│ 78129981 │ 24      │ 6         │ 30          │ 20          │
│ 77767692 │ 6       │ 8         │ 14          │ 42.9        │
└──────────┴─────────┴───────────┴─────────────┴─────────────┘

10 rows in set. Elapsed: 8.883 sec.
```

## Conclusion

In this blog post, we've used ClickHouse to read a Parquet file, loads its contents into MySQL and query the results.

Being able to do all of that without leaving ClickHouse is why I like table functions so much. And MySQL is just one option. There are also table functions for [Postgres](https://clickhouse.com/docs/reference/functions/table-functions/postgresql), [SQLite](https://clickhouse.com/docs/reference/functions/table-functions/sqlite), and [MongoDB](https://clickhouse.com/docs/reference/functions/table-functions/mongodb), to name just a few.

---

## Get started today

Interested in seeing how ClickHouse works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-1967-get-started-today-sign-up&utm_blogctaid=1967)

---