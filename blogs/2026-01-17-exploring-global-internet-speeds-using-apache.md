---
title: "Exploring Global Internet Speeds using Apache Iceberg and ClickHouse"
date: "2024-02-08T14:11:05.114Z"
author: "Dale McDiarmid"
category: "Engineering"
excerpt: "In a feature-rich blog post, we demonstrate ClickHouse's support for Apache Iceberg and how this fits into our Real-time Data Warehouse vision before visualizing internet speed data with just SQL!"
---

# Exploring Global Internet Speeds using Apache Iceberg and ClickHouse

At ClickHouse, we often find ourselves downloading and exploring increasingly large datasets, which invariably need a fast internet connection. When looking to move house and country and needing to ensure I had fast internet, I discovered the sizable [Ookla dataset](https://www.ookla.com/ookla-for-good/open-data) providing internet performance for all locations around the world. This dataset represents the world's largest source of crowdsourced network tests, covering both fixed and mobile internet performance with coverage for the majority of the world's land surface.

While Ookla already provides [excellent tooling](https://www.ookla.com/ookla-for-good/open-data#interactive-map) for exploring internet performance by location using this dataset, it presented an opportunity to explore both ClickHouse's Apache Iceberg support as well as ever-expanding geo functions. 

Limiting this a little further, I was curious to see the feasibility of **visualizing geographical data with just SQL by converting geo polygons to SVGs**. This takes us on a tour of h3 indexes, polygon dictionaries, Mercator projections, color interpolations, and centroid computation using UDFs. If you are curious how we ended up with the following with just SQL, read on…

![h3_as_svg_highres.png](https://clickhouse.com/uploads/h3_as_svg_highres_25510a0a73.png)

<blockquote style="font-size: 14px;">
<p>Note: ClickHouse supports a number of visualization tools ideal for this dataset, including but not limited to Superset. Our limitation to using just SQL was just for fun!</p>
</blockquote>

Before diving into the dataset, we’ll do a quick refresh on the value of Apache Iceberg and its support and relevance to ClickHouse. For those familiar with this topic, feel free to [jump to the part](/blog/exploring-global-internet-speeds-with-apache-iceberg-clickhouse#exploring-the-data) we start querying!

## Apache Iceberg

Apache Iceberg has gathered significant attention in recent years, with it fundamental to the evolution of the “Data Lake” concept to a “Lake House.” By providing a high-performance table format for data, Iceberg brings table-like semantics to structured data stored in a data lake. More specifically, this open-table format is vendor-agnostic and allows data files, typically in structured Parquet, to be exposed as tables with support for schema evolution, deletes, updates, transactions, and even ACID compliance. This represents a logical evolution from more legacy data lakes based on technologies such as Hadoop and Hive.

Maybe, most importantly, this data format allows query engines like Spark and Trino to safely work with the same tables, at the same time, while also delivering features such as partitioning which potentially can be exploited by query planners to accelerate queries.

## ClickHouse support

While ClickHouse is a lot more than simply a query engine, we acknowledge the importance of these open standards in allowing users to avoid vendor lock-in as well as a sensible data interchange format for other tooling. As discussed in a recent blog post, ["The Unbundling of the Cloud Data Warehouse"](https://clickhouse.com/blog/the-unbundling-of-the-cloud-data-warehouse#the-unbundling-of-the-cloud-data-warehouse) we consider the lake house to be a fundamental component in the modern data architecture, complementing real-time analytical databases perfectly. In this architecture, the lake house provides cost-effective cold storage and a common source of truth, with support for ad hoc querying. 

However, for more demanding use cases, such as user-facing data-intensive applications, which require low latency queries and support for high concurrency, subsets can be moved to ClickHouse. This allows users to benefit from both the open interchange format of Iceberg for their cold storage and long-term retention, using ClickHouse as a real-time data warehouse for when query performance is critical.

![real_time_datawarehouse_iceberg.png](https://clickhouse.com/uploads/real_time_datawarehouse_iceberg_7e8a1f4692.png)

### Querying Iceberg with ClickHouse

Realizing this vision requires the ability to query Iceberg files from ClickHouse. As a lake house format, this is currently supported through a dedicated table [iceberg](https://clickhouse.com/docs/en/sql-reference/table-functions/iceberg) function. This assumes the data is hosted on an S3-compliant service such as AWS S3 or Minio. 

For our examples, we’ve made the Ookla dataset available in the following public S3 bucket for users to experiment.

[s3://datasets-documentation/ookla/iceberg/](https://datasets-documentation.s3.eu-west-3.amazonaws.com/ookla/iceberg/)

We can describe the schema of the Ookla data using a DESCRIBE query with the iceberg function replacing our table name. Unlike Parquet, which relies on sampling the actual data, the schema is read from the Iceberg metadata files.

```sql
DESCRIBE TABLE iceberg('https://datasets-documentation.s3.eu-west-3.amazonaws.com/ookla/iceberg/')
SETTINGS describe_compact_output = 1

┌─name────────────┬─type─────────────┐
│ quadkey     	  │ Nullable(String) │
│ tile        	  │ Nullable(String) │
│ avg_d_kbps  	  │ Nullable(Int32)  │
│ avg_u_kbps  	  │ Nullable(Int32)  │
│ avg_lat_ms  	  │ Nullable(Int32)  │
│ avg_lat_down_ms │ Nullable(Int32)  │
│ avg_lat_up_ms   │ Nullable(Int32)  │
│ tests       	  │ Nullable(Int32)  │
│ devices     	  │ Nullable(Int32)  │
│ year_month  	  │ Nullable(Date)   │
└─────────────────┴──────────────────┘

10 rows in set. Elapsed: 0.216 sec.
```

Similarly, querying rows can be performed with standard SQL with the table function replacing the table name. In the following, we sample some rows and count the total size of the data set.

```sql
SELECT *
FROM iceberg('https://datasets-documentation.s3.eu-west-3.amazonaws.com/ookla/iceberg/')
LIMIT 1
FORMAT Vertical

Row 1:
──────
quadkey:     	1202021303331311
tile:        	POLYGON((4.9163818359375 51.2206474303833, 4.921875 51.2206474303833, 4.921875 51.2172068072334, 4.9163818359375 51.2172068072334, 4.9163818359375 51.2206474303833))
avg_d_kbps:  	109291
avg_u_kbps:  	15426
avg_lat_ms:  	12
avg_lat_down_ms: ᴺᵁᴸᴸ
avg_lat_up_ms:   ᴺᵁᴸᴸ
tests:       	6
devices:     	4
year_month:  	2021-06-01

1 row in set. Elapsed: 2.100 sec. Processed 8.19 thousand rows, 232.12 KB (3.90 thousand rows/s., 110.52 KB/s.)
Peak memory usage: 4.09 MiB.


SELECT count()
FROM iceberg('https://datasets-documentation.s3.eu-west-3.amazonaws.com/ookla/iceberg/')

┌───count()─┐
│ 128006990 │
└───────────┘

1 row in set. Elapsed: 0.701 sec. Processed 128.01 million rows, 21.55 KB (182.68 million rows/s., 30.75 KB/s.)
Peak memory usage: 4.09 MiB
```

We can see that Ookla divides the surface of the earth into Polygons using the [WKT format](https://en.wikipedia.org/wiki/Well-known_text_representation_of_geometry). We’ll delve into this in the 2nd half of the blog; for now, we’ll complete our simple examples with an aggregation computing the average number of devices per polygon and the median, 90th, 99th, and 99.9th quantiles for download speed.

```sql
SELECT
    round(avg(devices), 2) AS avg_devices,
    arrayMap(m -> round(m / 1000), quantiles(0.5, 0.9, 0.99, 0.999)(avg_d_kbps)) AS download_mbps
FROM iceberg('https://datasets-documentation.s3.eu-west-3.amazonaws.com/ookla/iceberg/')

┌─avg_devices─┬─download_mbps────┐
│   	 5.64 │ [51,249,502,762] │
└─────────────┴──────────────────┘

1 row in set. Elapsed: 4.704 sec. Processed 128.01 million rows, 3.75 GB (27.21 million rows/s., 797.63 MB/s.)
Peak memory usage: 22.89 MiB.
```

The above provides some simple examples of how their real-time data warehouse might function: cold Iceberg storage in the lake house and hot queries for real-time analytics in ClickHouse.

### A few limitations

The above represents some very simple queries. Before we dive into a deeper topic of how to visualize this data, it's worth highlighting some of the areas where further improvement is required (and planned) for ClickHouse's Iceberg support. 

* Currently, ClickHouse will not read Iceberg files that have [row-based deletes](https://iceberg.apache.org/spec/) (v2) or whose [schema has evolved](https://iceberg.apache.org/docs/latest/evolution/). The user will receive a read exception in these cases unless they [explicitly request it is ignored](https://clickhouse.com/docs/en/operations/settings/settings#iceberg_engine_ignore_schema_evolution).
* During query evaluation, ClickHouse doesn't currently exploit partitions to prune the data scanned. This represents a significant possibility for improving query execution and aligns with the [recent improvements made to Parquet](https://clickhouse.com/blog/clickhouse-release-23-07).
* The current implementation is bound to S3. In the future, we expect this coupling to be removed, with support added for any object storage supported by ClickHouse.
* Similar to ClickHouse's ordering key, Iceberg supports the ability to sort data. By ensuring data files within the Iceberg table are split and sorted, queries can potentially skip files during execution. This has the potential to further reduce the data scanned, improving performance.

## Exploring the data

With the basics out of the way, let's pivot this blog slightly and explore the Ookla data in a little more detail with the objective of visualizing internet speeds with just SQL.

### Reading and enriching

As noted earlier, the Ookla data separates the earth into polygons of varying sizes from which internet performance statistics have been collected. These Polygons are defined in the [WKT format](https://en.wikipedia.org/wiki/Well-known_text_representation_of_geometry), a markup language for representing spatial objects. This format makes sense for Iceberg and for data distribution purposes since the underlying Parquet files have no native Polygon representation.

```sql
POLYGON((-160.02685546875 70.6435894914449, -160.021362304688 70.6435894914449, -160.021362304688 70.6417687358462, -160.02685546875 70.6417687358462, -160.02685546875 70.6435894914449))
```

Querying this, however, requires conversion to a numerical representation. For ClickHouse, this can be performed with the [readWKTPolygon](https://clickhouse.com/docs/en/sql-reference/functions/geo/polygons#readwktpolygon) function. As shown below, this converts the text representation to a [Polygon](https://clickhouse.com/docs/en/sql-reference/data-types/geo#polygon) type on which we can later use [ClickHouse’s large range of geometric functions](https://clickhouse.com/docs/en/sql-reference/functions/geo/polygons). Note these Polygons contain longitude and latitude values.

```sql
SELECT readWKTPolygon(assumeNotNull(tile)) AS poly, toTypeName(poly) as type
FROM iceberg('https://datasets-documentation.s3.eu-west-3.amazonaws.com/ookla/iceberg/')
LIMIT 1
FORMAT Vertical

Row 1:
──────
poly:                                        	[[(4.9163818359375,51.2206474303833),(4.921875,51.2206474303833),(4.921875,51.2172068072334),(4.9163818359375,51.2172068072334),(4.9163818359375,51.2206474303833)]]
type: Polygon

1 row in set. Elapsed: 1.920 sec. Processed 8.19 thousand rows, 232.12 KB (4.27 thousand rows/s., 120.91 KB/s.)
Peak memory usage: 4.10 MiB.
```

For a gentle introduction to Polygons and parsing WKT data, we recommend the following video from our very own [“Data with Mark”](https://www.youtube.com/playlist?list=PL0Z2YDlm0b3gcY5R_MUo4fT5bPqUQ66ep).

<iframe width="768" height="432" src="https://www.youtube.com/embed/BKml8WUKb1c?si=-CYvNU4KRvACtssB" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>

<p></p>

<blockquote style="font-size: 14px;">
<p>Note the above video uses the most recent files from the Ookla dataset for which a centroid is provided.</p>
</blockquote>

While more recent versions of the Ookla dataset include a precomputed centroid of each polygon (from the 2nd quarter of 2023), the dataset goes back to 2019. As we’ll show later, this centroid (a lat/lon pair) can be useful when rendering the data. Fortunately, this is [relatively simple to compute](https://en.wikipedia.org/wiki/Centroid#Of_a_polygon) as our polygons are non-self-intersecting and closed. For the curious reader, some sample Python code ([credit](https://stackoverflow.com/questions/75699024/finding-the-centroid-of-a-polygon-in-python)) is shown below.

```python
def centroid(vertices):
	x, y = 0, 0
	n = len(vertices)
	signed_area = 0
       # computes the signed area and y and x accumulators - signed_area UDF function
	for i in range(len(vertices)):
    	  x0, y0 = vertices[i]
    	  x1, y1 = vertices[(i + 1) % n]
    	  # shoelace formula - maps to area function below
    	  area = (x0 * y1) - (x1 * y0)
    	  signed_area += area
    	  x += (x0 + x1) * area
    	  y += (y0 + y1) * area
       # final step of centroid function
	signed_area *= 0.5
	x /= 6 * signed_area
	y /= 6 * signed_area
	return x, y

x, y = centroid([(-160.037841796875, 70.6363054807905), (-160.032348632812, 70.6363054807905),(-160.032348632812, 70.6344840663086), (-160.037841796875, 70.6344840663086), (-160.037841796875, 70.6363054807905)])
print(x,y)
```

```bash
python centroid.py
-160.03509089358298 70.63539286610323
```

Converting this to a SQL UDF we can use at query time is simplest if we decompose the problem into several functions.

```sql
CREATE FUNCTION area AS (v1,v2) -> ((v1.1 * v2.2) - (v2.1 * v1.2))

CREATE FUNCTION signed_area AS polygon ->
   (
       arrayFold((acc, x) -> (
       (acc.1) + ((((x.1).1) + ((polygon[((x.2) + 1) % (length(polygon) + 1)]).1)) * area(x.1, polygon[((x.2) + 1) % (length(polygon) + 1)])),
       (acc.2) + ((((x.1).2) + ((polygon[((x.2) + 1) % (length(polygon) + 1)]).2)) * area(x.1, polygon[((x.2) + 1) % (length(polygon) + 1)])),
       (acc.3) + area(x.1, polygon[((x.2) + 1) % (length(polygon) + 1)])), arrayZip(polygon, range(1, length(polygon) + 1)), (0.0, 0.0, 0.0)
   )
)

CREATE FUNCTION centroid as polygon -> ((signed_area(polygon).1) / ((6 * (signed_area(polygon).3)) * 0.5), (signed_area(polygon).2) / ((6 * (signed_area(polygon).3)) * 0.5))
```

A quick test confirms our UDF gives the same result as the Python implementation.

```sql
SELECT centroid([(-160.037841796875, 70.6363054807905), (-160.032348632812, 70.6363054807905), (-160.032348632812, 70.6344840663086), (-160.037841796875, 70.6344840663086), (-160.037841796875, 70.6363054807905)]) AS centroid

┌─centroid────────────────────────────────┐
│ (-160.03509089358298,70.63539286610323) │
└─────────────────────────────────────────┘

1 row in set. Elapsed: 0.017 sec.
```

With the above functions, we can now read our Polygon data and compute a centroid consisting of a longitude and latitude. As we’ll show, we can exploit these centroids when visualizing the data.

### Loading the data

While all of the following queries could be used with the iceberg table function, this requires the data to be downloaded for each query, often limiting performance to our network bandwidth. Since we're going to be running a number of queries, it makes sense to load the data into ClickHouse to enjoy the performance benefits highlighted earlier. We modify our table schema to include the converted Polygon (a [Ring type](https://clickhouse.com/docs/en/sql-reference/data-types/geo#ring) - see below) and centroid (a [Point type](https://clickhouse.com/docs/en/sql-reference/data-types/geo#point)), extracting these with our functions above.

```sql
CREATE TABLE default.ookla
(
	`quadkey` Nullable(String),
	`polygon` Ring,
	`centroid` Point,
	`avg_d_kbps` Nullable(Int32),
	`avg_u_kbps` Nullable(Int32),
	`avg_lat_ms` Nullable(Int32),
	`avg_lat_down_ms` Nullable(Int32),
	`avg_lat_up_ms` Nullable(Int32),
	`tests` Nullable(Int32),
	`devices` Nullable(Int32),
	`year_month` Nullable(Date)
)
ENGINE = MergeTree ORDER BY tuple()

INSERT INTO ookla SELECT
	quadkey,
	readWKTPolygon(assumeNotNull(tile))[1] AS polygon,
	centroid(polygon) AS centroid,
	avg_d_kbps,
	avg_u_kbps,
	avg_lat_ms,
	avg_lat_down_ms,
	avg_lat_up_ms,
	tests,
	devices,
	year_month
FROM iceberg('https://datasets-documentation.s3.eu-west-3.amazonaws.com/ookla/iceberg/')

0 rows in set. Elapsed: 549.829 sec. Processed 128.01 million rows, 3.75 GB (232.81 thousand rows/s., 6.82 MB/s.)
Peak memory usage: 2.16 GiB.
```

<blockquote style="font-size: 14px;">
<p>Readers may notice that we use the first element from the array returned by the readWKTPolygon function. Polygons can consist of multiple rings, each consisting of a closed space. The first entry describes the outer space, with subsequent array entries specifying any holes. Since our polygons are closed, with no internal holes, we only have a single entry - allowing us to map our polygons to the simpler Ring type.</p>
</blockquote>

Our example only includes data for fixed devices. Data for mobile devices also exists for the curious.

### Polygons to SVGs

As noted, we could exploit several visualization tools to render this data now. However, these do incur an overhead - installation and, more importantly, time to gain familiarity and expertise. Given that the SVG format is inherently a vector-based format capable of rendering polygons, maybe we can just convert these polygons to an SVG to provide a 2D visualization of the data as a map?

This requires a means of converting each polygon to an [SVG polygon entry](https://www.w3schools.com/graphics/svg_polygon.asp). Ideally, we’d also be able to set the style of each polygon to convey a metric, e.g., download speed. As ever, the community had already thought of this problem with ClickHouse providing the [SVG function](https://clickhouse.com/docs//sql-reference/functions/geo/svg)!

This allows us to convert a Polygon in ClickHouse to an SVG polygon, as well as passing a style:

```sql
SELECT SVG([(-160.037841796875, 70.6363054807905), (-160.032348632812, 70.6363054807905), (-160.032348632812, 70.6344840663086), (-160.037841796875, 70.6344840663086), (-160.037841796875, 70.6363054807905)], 'fill: rgb(255, 55,38);') AS svg FORMAT Vertical

Row 1:
──────
svg: <polygon points="-160.038,70.6363 -160.032,70.6363 -160.032,70.6345 -160.038,70.6345 -160.038,70.6363" style="fill: rgb(255, 55,38);"/>

1 row in set. Elapsed: 0.002 sec.
```

### Points to Pixels

While the above is promising, we can't simply use coordinates as our latitudes and longitudes if visualizing as a 2d map. The coordinates represent positions on a three-dimensional surface, i.e., the Earth's surface, and not a 2d surface. A number of techniques, known as projections, exist for converting latitude and longitudes to points on 2d surfaces such as a map or a computer screen. This process inevitably involves some compromise or distortion in the representation of the Earth's surface because it's impossible to flatten a sphere without stretching or compressing its surface in some way.

A popular projection often used for maps is the [Mercator projector](https://en.wikipedia.org/wiki/Mercator_projection). This has a number of advantages; principally, it preserves angles and shapes at a local scale, making it an excellent choice for navigation. It also has the advantage that constant bearings (directions of travel) are straight lines, making navigating simple. Finally, while the Mercator projection accurately represents areas near the equator, it significantly distorts size and shape as one moves toward the poles. Landmasses like Greenland and Antarctica appear much larger than they are in reality compared to equatorial regions.

While ClickHouse doesn't have a Mercator function built in, we can solve this with another SQL UDF. Here, we project our point into a pixel space with dimensions 1024x1024.

```sql
-- coord (lon, lat) format
CREATE OR REPLACE FUNCTION mercator AS (coord, width, height) -> (
   ((coord.1) + 180) * (width / 360),
   (height / 2) - ((width * ln(tan((pi() / 4) + ((((coord.2) * pi()) / 180) / 2)))) / (2 * pi()))
)

SELECT mercator((-160.037841796875, 70.6363054807905), 1024, 1024) AS pixel_coords

┌─pixel_coords──────────────────┐
│ (56.78125,223.79687511938704) │
└───────────────────────────────┘

1 row in set. Elapsed: 0.001 sec.
```

To apply the projection to an entire polygon, we can exploit the [arrayMap](http://arrayMap) function.

```sql
SELECT polygon, arrayMap(p -> mercator(p, 1024, 1024), polygon) AS pixels
FROM ookla
LIMIT 1
FORMAT Vertical

Row 1:
──────
polygon: [(-51.30615234375,-30.0358110426678),(-51.3006591796875,-30.0358110426678),(-51.3006591796875,-30.0405664305846),(-51.30615234375,-30.0405664305846),(-51.30615234375,-30.0358110426678)]
pixels:  [(366.0625,601.6406251005949),(366.078125,601.6406251005949),(366.078125,601.6562501003996),(366.0625,601.6562501003996),(366.0625,601.6406251005949)]

1 row in set. Elapsed: 0.012 sec.
```

### Size limitations

With our SVG and Mercator functions, we are well-placed to generate our first SVG. The following query iterates over the full 128 million polygons and converts them to an `svg` element. We also output an opening and closing `&lt;svg>` tag containing a background color and the coordinates for the [viewBox](https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute/viewBox).  

For this initial query, we want to confirm this rendering technique works, and hence, use a fixed style and don’t consider any metrics for now. We redirect the output of this query to a file. Note we use the output format [CustomSeparated](https://clickhouse.com/docs/en/sql-reference/formats#format-customseparated) to generate our `svg` opening and closing tag.

```bash
clickhouse client --query "SELECT SVG(arrayMap(p -> mercator(p, 1024, 1024), polygon), 'fill: rgb(255, 55,38);')
FROM ookla
FORMAT CustomSeparated
SETTINGS format_custom_result_before_delimiter = '<svg style=\"background-color: rgb(17,17,17);\" viewBox=\"0 0 1024 1024\" xmlns:svg=\"http://www.w3.org/2000/svg\" xmlns=\"http://www.w3.org/2000/svg\">', format_custom_result_after_delimiter = '</svg>', format_custom_escaping_rule = 'Raw'" > world.svg
```

What may have been predictable for many, is that 128 million polygons produce quite a large svg file!

```bash
(base) clickhouse@ClickHouse-MacBook-Pro ookla % ls -lh world.svg
-rw-r--r--  1 dalemcdiarmid  wheel	31G  2 Feb 17:04 world.svg
```

At 31GB, this isn’t renderable by a browser or tool on most machines and is even unrealistic to convert to compressed formats using tools such as [ImageMagick](https://www.imagemagick.org/script/index.php).  We welcome suggestions if you have an idea how to achieve this!

### Summarizing using dictionaries

Our first effort might be to summarize the data into much larger polygons representing geographical regions. For this, we require a means of determining in which larger polygons our small polygons lie. This is possible with functions such as [`polygonsWithinCartesian`](https://clickhouse.com/docs/en/sql-reference/functions/geo/polygons#polygonswithincartesian), which will be expensive to compute for 128 million polygons. 

Fortunately, ClickHouse has [Polygon Dictionaries](https://clickhouse.com/docs/en/sql-reference/dictionaries/external-dictionaries/external-dicts-dict-polygon/) to address this very problem. These allow users to search for the polygon containing a specific point efficiently. This requires each of our small polygons to be represented by a single point, such as a centroid :) 

As an example, suppose we want to summarize our polygons into countries. We store our target polygons in a `countries` table:

```sql
CREATE TABLE countries
(
  `name` String,
  `coordinates` MultiPolygon
)
ENGINE = MergeTree
ORDER BY name

INSERT INTO countries
SELECT name, coordinates
FROM (
SELECT JSONExtractString(JSONExtractString(json, 'properties'), 'ADMIN') as name,
JSONExtractString(JSONExtractRaw(json, 'geometry'), 'type') as type,
if(type == 'Polygon', [JSONExtract(JSONExtractRaw(JSONExtractRaw(json, 'geometry'), 'coordinates'), 'Polygon')], JSONExtract(JSONExtractRaw(JSONExtractRaw(json, 'geometry'), 'coordinates'), 'MultiPolygon')) as coordinates
 	FROM (SELECT arrayJoin(JSONExtractArrayRaw(json, 'features')) as json
       	FROM url('https://datasets-documentation.s3.eu-west-3.amazonaws.com/countries/countries.geojson', JSONAsString)))
```
 
Our country's polygons are represented as geoJSON and are available here. The above `INSERT SELECT` extracts these polygons from the JSON using JSONExtract* functions, storing them in the `countries` table. 

And yet again we have a video for this very topic covering the query and subsequent dictionary:

<iframe width="768" height="432" src="https://www.youtube.com/embed/FyRsriQp46E?si=6M_5AX37ugfkBUbz" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>

<p></p>

```sql
CREATE DICTIONARY country_polygons
(
    `coordinates` MultiPolygon,
    `name` String
)
PRIMARY KEY coordinates
SOURCE(CLICKHOUSE(TABLE 'countries'))
LIFETIME(MIN 0 MAX 0)
LAYOUT(POLYGON(STORE_POLYGON_KEY_COLUMN 1))
```

This dictionary is indexed by the coordinates of our polygon and allows us to retrieve the polygon associated with a specific latitude and longitude using the [`dictGet`](https://clickhouse.com/docs/en/sql-reference/functions/ext-dict-functions#dictGet) function. For example,

```sql
SELECT dictGet(country_polygons, 'name', (-2.72647, 55.599621)) AS location

┌─location───────┐
│ United Kingdom │
└────────────────┘
1 row in set. Elapsed: 0.012 sec.
```

Notice the speed of retrieval here. Aside from being useful in our later visualizations, this dictionary allows us to obtain quick insight into the internet speeds of different countries. For example, we can quickly determine that maybe the South Georgia islands are the best place to live for fast internet!

<pre style="font-size: 14px;"><code class="hljs language-sql"><span class="hljs-keyword">SELECT</span> dictGet(country_polygons, <span class="hljs-string">'name'</span>, centroid) <span class="hljs-keyword">AS</span> country,
    <span class="hljs-built_in">avg</span>(avg_d_kbps) <span class="hljs-keyword">AS</span> download_speed,
    <span class="hljs-built_in">sum</span>(devices) <span class="hljs-keyword">AS</span> total_devices
<span class="hljs-keyword">FROM</span> ookla
<span class="hljs-keyword">GROUP</span> <span class="hljs-keyword">BY</span> country
<span class="hljs-keyword">ORDER</span> <span class="hljs-keyword">BY</span> download_speed <span class="hljs-keyword">DESC</span>
LIMIT <span class="hljs-number">10</span>

┌─country──────────────────────────────────┬─────download_speed─┬─total_devices─┐
│ South Georgia <span class="hljs-keyword">and</span> South Sandwich Islands │    		 <span class="hljs-number">198885</span> │    		 <span class="hljs-number">4</span>  │
│ Singapore                       		   │ <span class="hljs-number">197264.31481017102</span> │  	    <span class="hljs-number">3591446</span> │
│ Hong Kong S.A.R.                		   │   <span class="hljs-number">166375.523948868</span> │  	    <span class="hljs-number">3891226</span> │
│ China                           		   │ <span class="hljs-number">158978.10242450528</span> │ 	   <span class="hljs-number">53841880</span> │
│ Thailand                        		   │ <span class="hljs-number">155309.49656953348</span> │ 	   <span class="hljs-number">27506456</span> │
│ Iceland                         		   │ <span class="hljs-number">152290.62935414084</span> │   	 <span class="hljs-number">281514</span> │
│ United States <span class="hljs-keyword">of</span> America        		   │ <span class="hljs-number">149532.95964270137</span> │     <span class="hljs-number">246966470</span> │
│ South Korea                     		   │  <span class="hljs-number">149115.5647068738</span> │  	    <span class="hljs-number">2129690</span> │
│ United Arab Emirates            		   │  <span class="hljs-number">148936.4285346194</span> │  	    <span class="hljs-number">8380900</span> │
│ Jersey                          		   │ <span class="hljs-number">146030.67963711882</span> │   	 <span class="hljs-number">100902</span> │
└──────────────────────────────────────────┴────────────────────┴───────────────┘

<span class="hljs-number">10</span> <span class="hljs-keyword">rows</span> <span class="hljs-keyword">in</span> set. Elapsed: <span class="hljs-number">5.467</span> sec. Processed <span class="hljs-number">256.01</span> million <span class="hljs-keyword">rows</span>, <span class="hljs-number">6.66</span> GB (<span class="hljs-number">46.83</span> million <span class="hljs-keyword">rows</span><span class="hljs-operator">/</span>s., <span class="hljs-number">1.22</span> GB<span class="hljs-operator">/</span>s.)
Peak memory usage: <span class="hljs-number">129.74</span> MiB.
</code></pre>

Finally, as we’ll see below, it might also be helpful to be able to retrieve the polygon for a country efficiently based on its name. This can be achieved with a simple dictionary using the same `countries` table.

```sql
CREATE DICTIONARY default.country_names
(
	`coordinates` MultiPolygon,
	`name` String
)
PRIMARY KEY name
SOURCE(CLICKHOUSE(TABLE 'countries'))
LIFETIME(MIN 0 MAX 0)
LAYOUT(COMPLEX_KEY_HASHED())

SELECT dictGet(country_names, 'coordinates', 'Yemen') AS coords

[[[(53.308239457000155,12.11839453700017),(53.310267307000146,12.11144367200015)..

1 row in set. Elapsed: 0.007 sec.
```

For more details on dictionaries we recommend the following [blog post](https://clickhouse.com/blog/faster-queries-dictionaries-clickhouse).

### Global SVG

Armed with our dictionaries, centroids, Mercator UDF, and SVG functions, we can generate our first (usable) SVG.

![country_svg.png](https://clickhouse.com/uploads/country_svg_03800935c7.png)

The above SVG is 9.2MB and is generated by the following query, which completes in 11 seconds. As shown in the key, red here represents slow internet speed (download rate), while green represents faster connection speed.

<pre style="font-size: 14px;"><code class="hljs language-sql"><span class="hljs-keyword">WITH</span>
   <span class="hljs-comment">-- settings determining height, width and color range</span>
   <span class="hljs-number">1024</span> <span class="hljs-keyword">AS</span> height, <span class="hljs-number">1024</span> <span class="hljs-keyword">AS</span> width, [<span class="hljs-number">234</span>, <span class="hljs-number">36</span>, <span class="hljs-number">19</span>] <span class="hljs-keyword">AS</span> lc, [<span class="hljs-number">0</span>, <span class="hljs-number">156</span>, <span class="hljs-number">31</span>] <span class="hljs-keyword">AS</span> uc,
   country_rates <span class="hljs-keyword">AS</span>
   (
       <span class="hljs-comment">-- compute the average download speed per country using country_polygons dictionary</span>
       <span class="hljs-keyword">SELECT</span>
           dictGet(country_polygons, <span class="hljs-string">'name'</span>, centroid) <span class="hljs-keyword">AS</span> country,
           <span class="hljs-built_in">avg</span>(avg_d_kbps) <span class="hljs-keyword">AS</span> download_speed
       <span class="hljs-keyword">FROM</span> ookla
       <span class="hljs-comment">-- exclude 'Antarctica' as polygon isnt fully closed</span>
       <span class="hljs-keyword">WHERE</span> country <span class="hljs-operator">!=</span> <span class="hljs-string">'Antarctica'</span>
       <span class="hljs-keyword">GROUP</span> <span class="hljs-keyword">BY</span> country
   ),
   (
       <span class="hljs-comment">-- compute min speed over all countries</span>
       <span class="hljs-keyword">SELECT</span> <span class="hljs-built_in">min</span>(download_speed)
       <span class="hljs-keyword">FROM</span> country_rates
   ) <span class="hljs-keyword">AS</span> min_speed,
   (
       <span class="hljs-comment">-- compute max speed over all countries</span>
       <span class="hljs-keyword">SELECT</span> <span class="hljs-built_in">max</span>(download_speed)
       <span class="hljs-keyword">FROM</span> country_rates
   ) <span class="hljs-keyword">AS</span> max_speed,
   country_colors <span class="hljs-keyword">AS</span>
   (
       <span class="hljs-keyword">SELECT</span>
           country,
           download_speed,
           (download_speed <span class="hljs-operator">-</span> min_speed) <span class="hljs-operator">/</span> (max_speed <span class="hljs-operator">-</span> min_speed) <span class="hljs-keyword">AS</span> <span class="hljs-keyword">percent</span>,
           <span class="hljs-comment">-- compute a rgb value based on linear interolation between yellow and red</span>
           format(<span class="hljs-string">'rgb({},{},{})'</span>, toUInt8((lc[<span class="hljs-number">1</span>]) <span class="hljs-operator">+</span> (<span class="hljs-keyword">percent</span> <span class="hljs-operator">*</span> ((uc[<span class="hljs-number">1</span>]) <span class="hljs-operator">-</span> (lc[<span class="hljs-number">1</span>])))), toUInt8((lc[<span class="hljs-number">2</span>]) <span class="hljs-operator">+</span> (<span class="hljs-keyword">percent</span> <span class="hljs-operator">*</span> ((uc[<span class="hljs-number">2</span>]) <span class="hljs-operator">-</span> (lc[<span class="hljs-number">2</span>])))), toUInt8((lc[<span class="hljs-number">3</span>]) <span class="hljs-operator">+</span> (<span class="hljs-keyword">percent</span> <span class="hljs-operator">*</span> ((uc[<span class="hljs-number">3</span>]) <span class="hljs-operator">-</span> (lc[<span class="hljs-number">3</span>]))))) <span class="hljs-keyword">AS</span> rgb,
           <span class="hljs-comment">--  get polygon for country name and mercator project every point</span>
           arrayMap(p <span class="hljs-operator">-</span><span class="hljs-operator">&gt;</span> arrayMap(r <span class="hljs-operator">-</span><span class="hljs-operator">&gt;</span> arrayMap(x <span class="hljs-operator">-</span><span class="hljs-operator">&gt;</span> mercator(x, width, height), r), p), dictGet(country_names, <span class="hljs-string">'coordinates'</span>, country)) <span class="hljs-keyword">AS</span> pixel_poly
       <span class="hljs-keyword">FROM</span> country_rates
   )
<span class="hljs-comment">-- convert country polygon to svg</span>
<span class="hljs-keyword">SELECT</span> SVG(pixel_poly, format(<span class="hljs-string">'fill: {};'</span>, rgb))
<span class="hljs-keyword">FROM</span> country_colors
<span class="hljs-comment">-- send output to file</span>
<span class="hljs-keyword">INTO</span> OUTFILE <span class="hljs-string">'countries.svg'</span>
FORMAT CustomSeparated
SETTINGS format_custom_result_before_delimiter <span class="hljs-operator">=</span> <span class="hljs-string">'&lt;svg style="background-color: rgb(17,17,17);" viewBox="0 0 1024 1024" xmlns:svg="http://www.w3.org/2000/svg" xmlns="http://www.w3.org/2000/svg"&gt;'</span>, format_custom_result_after_delimiter <span class="hljs-operator">=</span> <span class="hljs-string">'&lt;/svg&gt;'</span>, format_custom_escaping_rule <span class="hljs-operator">=</span> <span class="hljs-string">'Raw'</span>

<span class="hljs-number">246</span> <span class="hljs-keyword">rows</span> <span class="hljs-keyword">in</span> set. Elapsed: <span class="hljs-number">1.396</span> sec. Processed <span class="hljs-number">384.02</span> million <span class="hljs-keyword">rows</span>, <span class="hljs-number">8.06</span> GB (<span class="hljs-number">275.15</span> million <span class="hljs-keyword">rows</span><span class="hljs-operator">/</span>s., <span class="hljs-number">5.78</span> GB<span class="hljs-operator">/</span>s.)
Peak memory usage: <span class="hljs-number">39.54</span> MiB.
</code></pre>

Despite just assembling the above concepts, there is a lot going on here. We’ve commented on the SQL, which hopefully helps, but in summary:

* We declare constants such as the color gradient (lc = yellow, uc = red) and the image height in the first CTE.
* For each country, we use the `country_polygons` dictionary to compute the average speed, similar to our earlier query.
* For the above values, we determine the maximum and minimum internet speeds. These are used to generate color for each country, using a simple [linear interpolation](https://en.wikipedia.org/wiki/Linear_interpolation) between our color ranges. 
* For each country, using its name, we use the reverse dictionary `country_names` to obtain the polygon. These polygons are complex, with many internal holes represented as Rings. We thus need to use nested `arrayMap` functions to project them using the Mercator projection function.
* Finally, we convert the project country polygons to SVG using the SVG function and RGB values. This is output to a local file using the INTO OUTFILE clause.

### Summarizing using h3 indexes

While the above query proves the concept of rendering SVGs from our geographical data, it is too coarse in its summarization. Visualizing internet speeds by country is interesting but only slightly builds on the earlier query, which listed internet speeds by country.

We could aim to populate our `country_polygons` dictionary with larger polygons from [public sources](https://www.google.com/search?q=polygons+earth&oq=polygons+earth+&gs_lcrp=EgZjaHJvbWUyDAgAEEUYDxgWGB4YOTIICAEQABgWGB4yCAgCEAAYFhgeMg0IAxAAGIYDGIAEGIoFMg0IBBAAGIYDGIAEGIoFMg0IBRAAGIYDGIAEGIoFMg0IBhAAGIYDGIAEGIoF0gEINjM5MWowajSoAgCwAgA&sourceid=chrome&ie=UTF-8). However, this seems a little restrictive, and ideally, we would be able to generate our vectors by a specified resolution, which controls the same of the polygons we render.

[H3](https://eng.uber.com/h3/) is a geographical indexing system developed by Uber, where the Earth's surface is divided into a grid of even hexagonal cells. This system is hierarchical, i.e., each hexagon on the top level ("parent") can be split into seven even smaller ones ("children"), and so on. When using the indexing system, we define a resolution between 0 and 15. The greater the resolution, the smaller each hexagon and, thus, the greater number required to cover the Earth's surface.

The differences in resolution on the number of polygons can be illustrated with a simple ClickHouse query using the function [h3NumHexagons](https://clickhouse.com/docs/en/sql-reference/functions/geo/h3#h3numhexagons), which returns the number of hexagons per resolution.

```sql
SELECT h3NumHexagons(CAST(number, 'UInt8')) AS num_hexagons
FROM numbers(0, 16)

┌─res─┬────num_hexagons─┐
│   0 │    		    122 │
│   1 │    		    842 │
│   2 │   		   5882 │
│   3 │  		  41162 │
│   4 │ 		  88122 │
│   5 │		    2016842 │
│   6 │   	   14117882 │
│   7 │   	   98825162 │
│   8 │  	  691776122 │
│   9 │ 	 4842432842 │
│  10 │     33897029882 │
│  11 │    237279209162 │
│  12 │   1660954464122 │
│  13 │  11626681248842 │
│  14 │  81386768741882 │
│  15 │ 569707381193162 │
└─────┴─────────────────┘

16 rows in set. Elapsed: 0.001 sec.
```

ClickHouse supports h3 through a[ number of functions](https://clickhouse.com/docs/en/sql-reference/functions/geo/h3), including the ability to convert a longitude and latitude to a h3 index via the [geoToH3](https://clickhouse.com/docs/en/sql-reference/functions/geo/h3#geotoh3) function with a specified resolution. Using this function, we can convert our centroids to a h3 index on which we can aggregate and compute statistics such as average download speed. Once aggregated, we can reverse this process with the function [h3ToGeoBoundary](https://clickhouse.com/docs/en/sql-reference/functions/geo/h3#h3togeoboundary) to convert a h3 index and its hexagon to a polygon. Finally, we use this Mercator projection and SVG function to produce our SVG. We visualize this process below:

![points_to_svg_process.png](https://clickhouse.com/uploads/points_to_svg_process_243d50da57.png)
<a href="/uploads/h3_as_svg_highres_25510a0a73.png" target="_blank"><img src="/uploads/h3_as_svg_b57e545553.png"/></a>

Above, we show the result for a resolution of 6, which produces 14,117,882 polygons and a file size of 165MB. This takes Chrome around 1 minute to render on a Macbook M2. 
By modifying the resolution, we can control the size of our polygons and the level of detail in our visualization. If we reduce the resolution to 4, our file size also decreases to 9.2MB as our visualization becomes more coarser with Chrome able to render this almost instantly.

![h3_as_svg_res_4.png](https://clickhouse.com/uploads/h3_as_svg_res_4_758b1401ef.png)

Our query here:

<pre style="font-size: 14px;"><code class="hljs language-sql">Our query here:
<span class="hljs-keyword">WITH</span>
   <span class="hljs-number">1024</span> <span class="hljs-keyword">AS</span> height, <span class="hljs-number">1024</span> <span class="hljs-keyword">AS</span> width, <span class="hljs-number">6</span> <span class="hljs-keyword">AS</span> resolution, <span class="hljs-number">30</span> <span class="hljs-keyword">AS</span> lc, <span class="hljs-number">144</span> <span class="hljs-keyword">AS</span> uc,
   h3_rates <span class="hljs-keyword">AS</span>
   (
       <span class="hljs-keyword">SELECT</span>
           geoToH3(centroid<span class="hljs-number">.1</span>, centroid<span class="hljs-number">.2</span>, resolution) <span class="hljs-keyword">AS</span> h3,
           <span class="hljs-built_in">avg</span>(avg_d_kbps) <span class="hljs-keyword">AS</span> download_speed
       <span class="hljs-keyword">FROM</span> ookla
       – <span class="hljs-keyword">filter</span> <span class="hljs-keyword">out</span> <span class="hljs-keyword">as</span> these <span class="hljs-keyword">are</span> sporadic <span class="hljs-keyword">and</span> don’t cover the continent
       <span class="hljs-keyword">WHERE</span> dictGet(country_polygons, <span class="hljs-string">'name'</span>, centroid) <span class="hljs-operator">!=</span> <span class="hljs-string">'Antarctica'</span>
       <span class="hljs-keyword">GROUP</span> <span class="hljs-keyword">BY</span> h3
   ),
   (
       <span class="hljs-keyword">SELECT</span> <span class="hljs-built_in">min</span>(download_speed) <span class="hljs-keyword">FROM</span> h3_rates
   ) <span class="hljs-keyword">AS</span> min_speed,
   (
       <span class="hljs-keyword">SELECT</span> quantile(<span class="hljs-number">0.95</span>)(download_speed) <span class="hljs-keyword">FROM</span> h3_rates
   ) <span class="hljs-keyword">AS</span> max_speed,
   h3_colors <span class="hljs-keyword">AS</span>
   (
       <span class="hljs-keyword">SELECT</span>
           <span class="hljs-comment">-- sqrt gradient</span>
           arrayMap(x <span class="hljs-operator">-</span><span class="hljs-operator">&gt;</span> (x<span class="hljs-number">.2</span>), arrayConcat(h3ToGeoBoundary(h3), [h3ToGeoBoundary(h3)[<span class="hljs-number">1</span>]])) <span class="hljs-keyword">AS</span> longs,
           <span class="hljs-built_in">sqrt</span>(download_speed <span class="hljs-operator">-</span> min_speed) <span class="hljs-operator">/</span> <span class="hljs-built_in">sqrt</span>(max_speed <span class="hljs-operator">-</span> min_speed) <span class="hljs-keyword">AS</span> <span class="hljs-keyword">percent</span>,
           <span class="hljs-comment">-- oklch color with gradient on hue</span>
           format(<span class="hljs-string">'oklch(60% 0.23 {})'</span>, toUInt8(lc <span class="hljs-operator">+</span> (<span class="hljs-keyword">percent</span> <span class="hljs-operator">*</span> (uc <span class="hljs-operator">-</span> lc)))) <span class="hljs-keyword">AS</span> oklch,
           arrayMap(p <span class="hljs-operator">-</span><span class="hljs-operator">&gt;</span> mercator((p<span class="hljs-number">.2</span>, p<span class="hljs-number">.1</span>), width, height), h3ToGeoBoundary(h3)) <span class="hljs-keyword">AS</span> pixel_poly
       <span class="hljs-keyword">FROM</span> h3_rates
       <span class="hljs-comment">-- filter out points crossing 180 meridian</span>
       <span class="hljs-keyword">WHERE</span> arrayExists(i <span class="hljs-operator">-</span><span class="hljs-operator">&gt;</span> (<span class="hljs-built_in">abs</span>((longs[i]) <span class="hljs-operator">-</span> (longs[i <span class="hljs-operator">+</span> <span class="hljs-number">1</span>])) <span class="hljs-operator">&gt;</span> <span class="hljs-number">180</span>), <span class="hljs-keyword">range</span>(<span class="hljs-number">1</span>, length(longs) <span class="hljs-operator">+</span> <span class="hljs-number">1</span>)) <span class="hljs-operator">=</span> <span class="hljs-number">0</span>
   )
<span class="hljs-keyword">SELECT</span> SVG(pixel_poly, format(<span class="hljs-string">'fill: {};'</span>, oklch))
<span class="hljs-keyword">FROM</span> h3_colors
<span class="hljs-keyword">INTO</span> OUTFILE <span class="hljs-string">'h3_countries.svg'</span> <span class="hljs-keyword">TRUNCATE</span>
FORMAT CustomSeparated
SETTINGS format_custom_result_before_delimiter <span class="hljs-operator">=</span> <span class="hljs-string">'&lt;svg style="background-color: rgb(17,17,17);" viewBox="0 0 1024 1024" xmlns:svg="http://www.w3.org/2000/svg" xmlns="http://www.w3.org/2000/svg"&gt;'</span>, format_custom_result_after_delimiter <span class="hljs-operator">=</span> <span class="hljs-string">'&lt;/svg&gt;'</span>, format_custom_escaping_rule <span class="hljs-operator">=</span> <span class="hljs-string">'Raw'</span>

<span class="hljs-number">55889</span> <span class="hljs-keyword">rows</span> <span class="hljs-keyword">in</span> set. Elapsed: <span class="hljs-number">10.101</span> sec. Processed <span class="hljs-number">384.02</span> million <span class="hljs-keyword">rows</span>, <span class="hljs-number">8.06</span> GB (<span class="hljs-number">38.02</span> million <span class="hljs-keyword">rows</span><span class="hljs-operator">/</span>s., <span class="hljs-number">798.38</span> MB<span class="hljs-operator">/</span>s.)
Peak memory usage: <span class="hljs-number">23.73</span> MiB.
</code></pre>

Aside from the conversion of the centroids to h3 indexes and their aggregation, there are a few other interesting parts of this query:

* We extract the longitudes into a separate array, and the first entry is also appended to the end. I.e. `arrayMap(x -> (x.2), arrayConcat(h3ToGeoBoundary(h3), [h3ToGeoBoundary(h3)[1]]))`. This allows us to examine consecutive pairs of longitudinal points and filter out those which cross the 180 meridian (these render as lines ruining our visual) i.e. `WHERE arrayExists(i -> (abs((longs[i]) - (longs[i + 1])) > 180), range(1, length(longs) + 1)) = 0`
* Rather than using an RGB color gradient, we’ve opted to use Oklch. This offers several[ advantages of RGB](https://evilmartians.com/chronicles/oklch-in-css-why-quit-rgb-hsl) (and HSL), delivering more expected results and smoother gradients while being easier to generate as only one dimension (hue) needs to be changed for our palette. Above our palette goes from red (low bandwidth) to green (high bandwidth), with a square root gradient between 30 and 144 hues. The `sqrt` here gives us a more even distribution of values, which are naturally clustered if linear, allowing us to differentiate regions. Our use of the 95th percentile for 144 also helps here.

### Rasterizing as an alternative

The h3 index approach above is flexible and realistic for rendering images based on a resolution of up to around 7. Values higher than this produce files that can’t be rendered by most browsers, e.g., 7 and 8 produce a file size of 600MB (just about renders!) and 1.85GB. The absence of data for some geographical regions (e.g. Africa) also becomes more apparent at these higher resolutions as the polygons for each centroid become smaller, i.e. more space is simply empty.

An alternative to this approach is to [rasterize the image](https://en.wikipedia.org/wiki/Rasterisation), generating a pixel for each centroid instead of a polygon. This approach is potentially also more flexible as when we specify the desired resolution (through the Mercator) function, this will map directly to the number of pixels used to represent our centroids. The data representation should also be smaller on disk for the same equivalent number of polygons.

The principle of this approach is simple. We project each centroid using our Mercator function, specifying a resolution and rounding the x and y values. Each of these x and y pairs represents a pixel, for which we can compute a statistic such as the average download rate using a simple `GROUP BY.` The following computes the average download rate per x,y pixel (for a resolution of 2048 x2048) using this approach, returning the pixels in row and column order.

```sql
SELECT
	(y * 2048) + x AS pos,
	avg(avg_d_kbps) AS download_speed
FROM ookla
GROUP BY
	round(mercator(centroid, 2048, 2048).1) AS x,
	round(mercator(centroid, 2048, 2048).2) AS y
ORDER BY pos ASC WITH FILL FROM 0 TO 2048 * 2048
```

Using the same approaches described above, the following query computes a color gradient using the min and max range of the download speed, outputting an RGBA value for each pixel. Below, we fix the alpha channel to 255 and use a linear function for our color gradient with the 95th percentile as our upper bound (to help compress our gradient). In this case, we use the query to create a view `ookla_as_pixels` to simplify the next step of visualizing this data. Note we use a background color of (17, 17, 17, 255) to represent those pixels with a null value for the download speed, i.e. no data points, and ensure our RGBA values are UInt8s.

<pre style="font-size: 13px;"><code class="hljs language-sql"><span class="hljs-keyword">CREATE</span> <span class="hljs-keyword">OR</span> REPLACE <span class="hljs-keyword">VIEW</span> ookla_as_pixels <span class="hljs-keyword">AS</span>
<span class="hljs-keyword">WITH</span> [<span class="hljs-number">234</span>, <span class="hljs-number">36</span>, <span class="hljs-number">19</span>] <span class="hljs-keyword">AS</span> lc, [<span class="hljs-number">0</span>, <span class="hljs-number">156</span>, <span class="hljs-number">31</span>] <span class="hljs-keyword">AS</span> uc, [<span class="hljs-number">17</span>,<span class="hljs-number">17</span>,<span class="hljs-number">17</span>] <span class="hljs-keyword">As</span> bg,
pixels <span class="hljs-keyword">AS</span>
(
	<span class="hljs-keyword">SELECT</span> (y <span class="hljs-operator">*</span> <span class="hljs-number">2048</span>) <span class="hljs-operator">+</span> x <span class="hljs-keyword">AS</span> pos,
    	<span class="hljs-built_in">avg</span>(avg_d_kbps) <span class="hljs-keyword">AS</span> download_speed
	<span class="hljs-keyword">FROM</span> ookla
	<span class="hljs-keyword">GROUP</span> <span class="hljs-keyword">BY</span>
    	round(mercator(centroid, <span class="hljs-number">2048</span>, <span class="hljs-number">2048</span>)<span class="hljs-number">.1</span>) <span class="hljs-keyword">AS</span> x,
    	round(mercator(centroid, <span class="hljs-number">2048</span>, <span class="hljs-number">2048</span>)<span class="hljs-number">.2</span>) <span class="hljs-keyword">AS</span> y
	<span class="hljs-keyword">ORDER</span> <span class="hljs-keyword">BY</span>
    	pos <span class="hljs-keyword">WITH</span> FILL <span class="hljs-keyword">FROM</span> <span class="hljs-number">0</span> <span class="hljs-keyword">TO</span> <span class="hljs-number">2048</span> <span class="hljs-operator">*</span> <span class="hljs-number">2048</span>
),
(
	<span class="hljs-keyword">SELECT</span> <span class="hljs-built_in">min</span>(download_speed)
	<span class="hljs-keyword">FROM</span> pixels
) <span class="hljs-keyword">AS</span> min_speed,
(
	<span class="hljs-keyword">SELECT</span> quantile(<span class="hljs-number">0.95</span>)(download_speed)
	<span class="hljs-keyword">FROM</span> pixels
) <span class="hljs-keyword">AS</span> max_speed,
pixel_colors <span class="hljs-keyword">AS</span> (
	<span class="hljs-keyword">SELECT</span>
	least(if(isNull(download_speed),<span class="hljs-number">0</span>, (download_speed <span class="hljs-operator">-</span> min_speed) <span class="hljs-operator">/</span> (max_speed <span class="hljs-operator">-</span> min_speed)), <span class="hljs-number">1.0</span>) <span class="hljs-keyword">AS</span> <span class="hljs-keyword">percent</span>,
	if(isNull(download_speed),bg[<span class="hljs-number">1</span>], toUInt8(lc[<span class="hljs-number">1</span>] <span class="hljs-operator">+</span> (<span class="hljs-keyword">percent</span> <span class="hljs-operator">*</span> (uc[<span class="hljs-number">1</span>] <span class="hljs-operator">-</span> lc[<span class="hljs-number">1</span>])))) <span class="hljs-keyword">AS</span> red,
	if(isNull(download_speed),bg[<span class="hljs-number">2</span>], toUInt8(lc[<span class="hljs-number">2</span>] <span class="hljs-operator">+</span> (<span class="hljs-keyword">percent</span> <span class="hljs-operator">*</span> (uc[<span class="hljs-number">2</span>] <span class="hljs-operator">-</span> lc[<span class="hljs-number">2</span>])))) <span class="hljs-keyword">AS</span> green,
	if(isNull(download_speed),bg[<span class="hljs-number">3</span>], toUInt8(lc[<span class="hljs-number">3</span>] <span class="hljs-operator">+</span> (<span class="hljs-keyword">percent</span> <span class="hljs-operator">*</span> (uc[<span class="hljs-number">3</span>] <span class="hljs-operator">-</span> lc[<span class="hljs-number">3</span>])))) <span class="hljs-keyword">AS</span> blue
	<span class="hljs-keyword">FROM</span> pixels
) <span class="hljs-keyword">SELECT</span> red::UInt8, green::UInt8, blue::UInt8, <span class="hljs-number">255</span>::UInt8 <span class="hljs-keyword">as</span> alpha <span class="hljs-keyword">FROM</span> pixel_colors
</code></pre>

Converting this data to an image is most easily done using a [Canvas element](https://www.w3schools.com/html/html5_canvas.asp) and some simple js. We effectively have 4 bytes per pixel and 2048 x 2048 x 4 bytes in total or approximately 16MB. Using the `putImageData` we render this data directly into a canvas.

```html
<!doctype html>
<html>
<head>
   <meta charset="utf-8">
   <link rel="icon" href="favicon.png">
   <title>Simple Ookla Visual</title>
</head>
<body>
   <div id="error"></div>
   <canvas id="canvas" width="2048" height="2048"></canvas>
   <script>
       async function render(tile) {
           const url = `http://localhost:8123/?user=default&default_format=RowBinary`;
           const response = await fetch(url, { method: 'POST', body: 'SELECT * FROM ookla_as_pixels' });
           if (!response.ok) {
               const text = await response.text();
               let err = document.getElementById('error');
               err.textContent = text;
               err.style.display = 'block';
               return;
           }
           buf = await response.arrayBuffer();
           let ctx = tile.getContext('2d');
           let image = ctx.createImageData(2048, 2048);
           let arr = new Uint8ClampedArray(buf);

           for (let i = 0; i < 2048 * 2048 * 4; ++i) {
               image.data[i] = arr[i];
           }
           ctx.putImageData(image, 0, 0, 0, 0, 2048, 2048);
           let err = document.getElementById('error');
           err.style.display = 'none';
       }
       const canvas = document.getElementById("canvas");
       render(canvas).then((err) => {
           if (err) {
               let err = document.getElementById('error');
               err.textContent = text;
           } else {
               err.style.display = 'none'
           }
       })
   </script>
</body>
</html>
```

<blockquote style="font-size: 14px;">
<p>This <a href="https://github.com/ClickHouse/adsb.exposed/blob/main/index.html#L407">code provided by</a> Alexey Milovidov who has taken this to a whole new level with his  <a href="https://github.com/ClickHouse/adsb.exposed/tree/main">Interactive visualization and analytics on ADS-B data</a>.</p>
</blockquote>

The above exploits the ClickHouse’s [HTTP interface](https://clickhouse.com/docs/en/interfaces/http) and ability to return results in [RowBinary format](https://clickhouse.com/docs/en/integrations/data-formats/binary-native#exporting-to-rowbinary). The creation of a view has significantly simplified our SQL query to simply `SELECT * FROM ookla_as_pixels`. Our resulting image.

<a href="/uploads/h3_raster_c5c7db39fa.png" target="_blank"><img src="/uploads/h3_raster_c5c7db39fa.png"/></a>

This represents a nice alternative to our SVG approach, even if we did have to use a little more than just SQL :) 

## Conclusion
This post has introduced the Iceberg data format and discussed the current state of support in ClickHouse, with examples of how to query and import the data. We have explored the Ookla internet speed dataset, distributed in Iceberg format, and used the opportunity to explore h3 indexes, polygon dictionaries, Mercator projections, color interpolations, and centroid computation using UDFs - all with the aim of visualizing the data with just SQL.

While we have mainly focused on download speed and fixed devices, we’d love to see others use similar approaches to explore other metrics. Alternatively, we welcome suggestions on improving the above!
