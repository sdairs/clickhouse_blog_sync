---
title: "Querying Pandas DataFrames with ClickHouse"
date: "2023-11-15T11:54:52.266Z"
author: "Mark Needham"
category: "Engineering"
excerpt: "In this blog post, we'll learn how to query Pandas DataFrames using chDB, a Python library powered by ClickHouse. "
---

# Querying Pandas DataFrames with ClickHouse

In the world of data analysis, Pandas is considered the starting point for most Python-based data exploration. But what if we want to query our DataFrames using an OLAP database like ClickHouse to take advantage of its query engine and SQL support?

This is where [chDB](https://github.com/chdb-io/chdb/tree/main), a Python library powered by ClickHouse, comes into play. We’ve already featured chDB [a couple](https://clickhouse.com/blog/welcome-chdb-to-clickhouse) [of times](https://clickhouse.com/blog/chdb-embedded-clickhouse-rocket-engine-on-a-bicycle) already on the blog, but in this post we’re going to focus on its ability to query Pandas DataFrames, join them together, aggregate data, and then export the results back to Pandas.

<iframe  width="768" height="432" src="https://www.youtube.com/embed/udlfgc5eVTY?si=mc3DecB_XfyEA4W7" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen style="margin-bottom: 15px"></iframe>

chDB is available via PyPi, which means we can install it with pip:

```
pip install chdb
```

We’ll also need to install Pandas and PyArrow as the DataFrame functionality of chDB has dependencies on those libraries:

```bash
pip install pandas pyarrow
```

Ok, now we’re good to go. We’re going to explore [Kaggle’s Canadian house prices for top cities
Dataset](https://www.kaggle.com/datasets/jeremylarcher/canadian-house-prices-for-top-cities), which contains real estate data from the 2021 census. 

Once we’ve downloaded the CSV file, we’re going to read it into a Pandas DataFrame.

```python
import pandas as pd
house_prices = pd.read_csv(
  filepath_or_buffer="data/HouseListings-Top45Cities-10292023-kaggle.csv", 
  encoding = "ISO-8859-1"
)
```

And then we can have a look at a couple of the records:

```python
house_prices.head(n=2).T
```

```
                                          0                      1
City                                Toronto                Toronto
Price                              779900.0               799999.0
Address               #318 -20 SOUTHPORT ST  #818 -60 SOUTHPORT ST
Number_Beds                               3                      3
Number_Baths                              2                      1
Province                            Ontario                Ontario
Population                          5647656                5647656
Latitude                            43.7417                43.7417
Longitude                          -79.3733               -79.3733
Median_Family_Income                97000.0                97000.0
```

## Querying DataFrames with ClickHouse

To query a DataFrame in chDB, we need to import the `chdb.dataframe` module:

```python
import chdb.dataframe as cdf
```

This module has a function called query that we can use. We can pass in 1 or more DataFrames as named parameters, which we can then address in the query. The parameter names that we use can be addressed as `__<parameter-name>__`. The following query finds the top 10 cities with the most properties:

```python
cdf.query(
    house_prices=house_prices, 
    sql="""
FROM __house_prices__
SELECT City, Province, count(*)
GROUP BY ALL
LIMIT 10
""")
```

```text
             City            Province  count()
    b'White Rock' b'British Columbia'     1175
       b'Toronto'          b'Ontario'     1276
       b'Kelowna' b'British Columbia'     1280
      b'Winnipeg'         b'Manitoba'      530
      b'Winnipeg'          b'Ontario'        1
      b'Red Deer'          b'Alberta'      326
   b'Thunder Bay'          b'Ontario'      154
    b'Lethbridge'          b'Alberta'      379
b'St. Catharines'          b'Ontario'     1268
b'Trois-Rivieres'           b'Quebec'      165
```

## Joining DataFrames with ClickHouse

As well as querying individual DataFrames, we can also join them together. So we’re going to bring in another dataset that contains [metadata about Canadian cities](https://simplemaps.com/data/canada-cities). Let’s have a look at that one:

```python
cities = pd.read_csv(
    filepath_or_buffer="data/canadacities.csv"
)

cities.head(n=1).T
```

```text
                                                               0
city                                                     Toronto
city_ascii                                               Toronto
province_id                                                   ON
province_name                                            Ontario
lat                                                      43.7417
lng                                                     -79.3733
population                                             5647656.0
density                                                   4427.8
timezone                                         America/Toronto
ranking                                                        1
postal         M5T M5V M5P M5S M5R M5E M5G M5A M5C M5B M5M M5...
id                                                    1124279679
```

We can join this DataFrame with the first one via the city_ascii and province_name fields. 

```python
top_cities = cdf.query(
    house_prices=house_prices, 
    cities=cities,
    sql="""
FROM __house_prices__ AS hp
JOIN __cities__ AS c 
ON c.city_ascii = hp.City AND c.province_name = hp.Province
SELECT City, Province, count(*),
       round(avg(Price)) AS avgPrice,
       round(max(Price)) AS maxPrice,
       ranking, density
GROUP BY ALL
LIMIT 10
""")
```

If we view the top_cities variable, we’ll see similar to the following:

```text
           City   Province  count()  avgPrice   maxPrice  ranking  density
   b'Brantford' b'Ontario'      628  955923.0  6495000.0        2   1061.2
    b'Hamilton' b'Ontario'     1289  975543.0 10995000.0        2    509.1
 b'Thunder Bay' b'Ontario'      154  459703.0  5599000.0        2    332.1
     b'Caledon' b'Ontario'     1336 1383366.0  9995000.0        3    111.2
     b'Calgary' b'Alberta'     1322  660046.0  5250000.0        1   1592.4
     b'Windsor' b'Ontario'      720  643019.0  2750000.0        2   1572.8
b'Medicine Hat' b'Alberta'      277  448137.0  1475000.0        3    565.1
    b'Montreal'  b'Quebec'      212  931392.0  4400000.0        1   4833.5
    b'Edmonton' b'Alberta'     1351  425582.0  4463445.0        1   1320.4
     b'Sudbury' b'Ontario'      203  596087.0  7699900.0        2     52.1
```

`top_cities` has the type `<class 'chdb.dataframe.query.Table'>` and we can actually query chDB tables using SQL as well. We can do this using the query function where the underlying table is accessible as `__table__ `. 

So, if we wanted to get the first 5 rows of top_cities, we could write the following:

```python
top_cities.query("""
FROM __table__ 
SELECT City, maxPrice, ranking, density 
LIMIT 5
""")
```

```text
          City   maxPrice  ranking  density
  b'Brantford'  6495000.0        2   1061.2
   b'Hamilton' 10995000.0        2    509.1
b'Thunder Bay'  5599000.0        2    332.1
    b'Caledon'  9995000.0        3    111.2
    b'Calgary'  5250000.0        1   1592.4
```

## Exporting chDB Tables to Pandas DataFrames

And if we’ve done enough querying with ClickHouse, we can always convert that table back to a Pandas DataFrame using the to_pandas function:

```python
top_cities_df = top_cities.to_pandas()
```

And let’s do a bit of querying in Pandas to finish off:

```python
(top_cities_df[top_cities_df["Province"] == b"Ontario"]
  .sort_values(["ranking", "density"])
  .drop(["Province"], axis=1)
)  
```

```text
          City  count()  avgPrice   maxPrice  ranking  density
    b'Sudbury'      203  596087.0  7699900.0        2     52.1
b'Thunder Bay'      154  459703.0  5599000.0        2    332.1
   b'Hamilton'     1289  975543.0 10995000.0        2    509.1
  b'Brantford'      628  955923.0  6495000.0        2   1061.2
    b'Windsor'      720  643019.0  2750000.0        2   1572.8
    b'Caledon'     1336 1383366.0  9995000.0        3    111.2
```

## In Conclusion

chDB is constantly evolving, but what it can already do is pretty cool. So head over to [the GitHub page](https://github.com/chdb-io/chdb/tree/main) and give it a try!