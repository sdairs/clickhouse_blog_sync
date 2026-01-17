---
title: "SQL Dynamic Column Selection with ClickHouse"
date: "2023-11-28T09:38:31.153Z"
author: "Mark Needham"
category: "Engineering"
excerpt: "In this blog post, we'll learn all about dynamic column selection in ClickHouse."
---

# SQL Dynamic Column Selection with ClickHouse

When working with datasets that contain a lot of columns, we’ll often want to compute aggregations on a subset of those columns. 

Having to type out all the columns that we want to operate on is pretty tedious, so I was pleased to learn that ClickHouse has functionality that allows for dynamic column selection.

<iframe width="768" height="432" src="https://www.youtube.com/embed/moabRqqHNo4?si=jgmInV-u3UxtLvMS" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>

## Import NYC Taxis dataset

We’re going to use the NYC taxis dataset and in particular the data for yellow taxis in January 2023. We’ll download the Parquet file for that month and then launch a ClickHouse Local instance and ingest it:

```sql
./clickhouse local -m
```

```sql
CREATE TABLE trips ENGINE MergeTree 
ORDER BY (tpep_pickup_datetime) AS 
from file('yellow tripdata Jan 2023.parquet', Parquet)
select *
SETTINGS schema_inference_make_columns_nullable = 0;
```

We can have a look at the schema of the table by running the following query:

```sql
DESCRIBE TABLE trips
SETTINGS describe_compact_output = 1;
```

```text
┌─name──────────────────┬─type──────────┐
│ VendorID              │ Int64         │
│ tpep_pickup_datetime  │ DateTime64(6) │
│ tpep_dropoff_datetime │ DateTime64(6) │
│ passenger_count       │ Float64       │
│ trip_distance         │ Float64       │
│ RatecodeID            │ Float64       │
│ store_and_fwd_flag    │ String        │
│ PULocationID          │ Int64         │
│ DOLocationID          │ Int64         │
│ payment_type          │ Int64         │
│ fare_amount           │ Float64       │
│ extra                 │ Float64       │
│ mta_tax               │ Float64       │
│ tip_amount            │ Float64       │
│ tolls_amount          │ Float64       │
│ improvement_surcharge │ Float64       │
│ total_amount          │ Float64       │
│ congestion_surcharge  │ Float64       │
│ airport_fee           │ Float64       │
└───────────────────────┴───────────────┘
```


## Dynamically selecting columns


Now, let’s say that we only want to work with the columns that contain _amount. Rather than having to type out those columns individually, we can use the COLUMNS clause to return the columns that match a regular expression. A query to return the first 10 rows for the amount columns would look like this:

```sql
FROM trips 
SELECT COLUMNS('.*_amount')
LIMIT 10;
```

```text
┌─fare_amount─┬─tip_amount─┬─tolls_amount─┬─total_amount─┐
│           0 │          0 │            0 │            0 │
│         120 │          0 │            0 │        120.3 │
│          45 │       9.06 │            0 │        54.36 │
│          75 │      15.06 │            0 │        90.36 │
│          55 │      14.45 │            0 │        72.25 │
│         4.5 │          0 │            0 │         6.55 │
│          10 │          0 │            0 │         10.8 │
│         115 │          5 │            0 │        120.3 │
│          78 │      15.76 │            0 │        94.56 │
│        19.5 │          0 │            0 │        21.55 │
└─────────────┴────────────┴──────────────┴──────────────┘
```

Let’s say we also want to return columns that contain the terms fee or tax. We can update the regular expression to include those:

```sql
FROM trips
SELECT
  COLUMNS('.*_amount|fee|tax')
ORDER BY rand() 
LIMIT 3
FORMAT Vertical;
```

```text
Row 1:
──────
fare_amount:  9.3
mta_tax:      0.5
tip_amount:   0
tolls_amount: 0
total_amount: 13.3
airport_fee:  0

Row 2:
──────
fare_amount:  10
mta_tax:      0.5
tip_amount:   2
tolls_amount: 0
total_amount: 16
airport_fee:  0

Row 3:
──────
fare_amount:  18.4
mta_tax:      0.5
tip_amount:   1
tolls_amount: 0
total_amount: 23.4
airport_fee:  0
```

## Apply functions to all columns

We can also use the `APPLY` function to apply functions across every column. For example, if we wanted to find the maximum value of each of those columns, we could run the following query:

```sql
FROM trips 
SELECT 
  COLUMNS('.*_amount|fee|tax')
  APPLY(max)
FORMAT Vertical;
```

```text
Row 1:
──────
max(fare_amount):  1160.1
max(mta_tax):      53.16
max(tip_amount):   380.8
max(tolls_amount): 196.99
max(total_amount): 1169.4
max(airport_fee):  1.25
```

Or maybe, we’d like to see the average instead:

```sql
FROM trips 
SELECT 
  COLUMNS('.*_amount|fee|tax')
  APPLY(avg)
FORMAT Vertical;
```

```text
Row 1:
──────
avg(fare_amount):  18.36706861234277
avg(mta_tax):      0.48828997712900174
avg(tip_amount):   3.3679406710521764
avg(tolls_amount): 0.5184906575852216
avg(total_amount): 27.020383107155837
avg(airport_fee):  0.10489592293640923
```

Those values contain a lot of decimal places, but luckily we can fix that by chaining functions. In this case, we’ll apply the avg function, followed by the round function:

```sql
FROM trips 
SELECT 
  COLUMNS('.*_amount|fee|tax')
  APPLY(avg)
  APPLY(round)
FORMAT Vertical;
```

```text
Row 1:
──────
round(avg(fare_amount)):  18
round(avg(mta_tax)):      0
round(avg(tip_amount)):   3
round(avg(tolls_amount)): 1
round(avg(total_amount)): 27
round(avg(airport_fee)):  0
```

But that rounds the averages to whole numbers. If we want to round to, say, 2 decimal places, we can do that as well. As well as taking in functions, the APPLY function takes in a lambda, which gives us the flexibility to have the round function round our average values to 2 decimal places:

```sql
FROM trips 
SELECT 
  COLUMNS('.*_amount|fee|tax')
  APPLY(avg)
  APPLY(col -> round(col, 2))
FORMAT Vertical;
```

```text
Row 1:
──────
round(avg(fare_amount), 2):  18.37
round(avg(mta_tax), 2):      0.49
round(avg(tip_amount), 2):   3.37
round(avg(tolls_amount), 2): 0.52
round(avg(total_amount), 2): 27.02
round(avg(airport_fee), 2):  0.1
```

## Replacing columns

So far so good. But let’s say we want to adjust one of the values, while leaving the other ones as they are. For example, maybe we want to double the total amount and divide the MTA tax by 1.1. We can do that by using the REPLACE clause, which will replace a column while leaving the other ones as they are.

```sql
FROM trips 
SELECT 
  COLUMNS('.*_amount|fee|tax')
  REPLACE(
    total_amount*2 AS total_amount,
    mta_tax/1.1 AS mta_tax
  ) 
  APPLY(avg)
  APPLY(col -> round(col, 2))
FORMAT Vertical;
```

```text
Row 1:
──────
round(avg(fare_amount), 2):               18.37
round(divide(avg(mta_tax), 1.1), 2):      0.44
round(avg(tip_amount), 2):                3.37
round(avg(tolls_amount), 2):              0.52
round(multiply(avg(total_amount), 2), 2): 54.04
round(avg(airport_fee), 2):               0.1
```

We can see that those two columns have both been replaced and the other columns are as they were in the previous query.
Excluding columns

We can also choose to exclude a field by using the EXCEPT clause. For example, to remove the tolls_amount column, we would write the following query:

```sql
FROM trips 
SELECT 
  COLUMNS('.*_amount|fee|tax') EXCEPT(tolls_amount)
  REPLACE(
    total_amount*2 AS total_amount,
    mta_tax/1.1 AS mta_tax
  ) 
  APPLY(avg)
  APPLY(col -> round(col, 2))
FORMAT Vertical;
```

```text
Row 1:
──────
round(avg(fare_amount), 2):               18.37
round(divide(avg(mta_tax), 1.1), 2):      0.44
round(avg(tip_amount), 2):                3.37
round(multiply(avg(total_amount), 2), 2): 54.04
round(avg(airport_fee), 2):               0.1
```

`tolls_amount` has now been removed and the other columns remain.

## In Conclusion

Hopefully you’ve seen that even with a dataset that didn’t have that many columns, ClickHouse’s dynamic column selection functionality saves us a bunch of typing in our SQL queries. 

Give these clauses a try on your own data and let us know how you get on!
