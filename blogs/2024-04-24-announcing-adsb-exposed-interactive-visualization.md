---
title: "Announcing adsb.exposed - Interactive Visualization and Analytics on ADS-B Flight Data with ClickHouse "
date: "2024-04-24T08:55:39.134Z"
author: "Alexey Milovidov"
category: "Engineering"
excerpt: "Read about how we built an interactive visualization and analytics tool,  adsb.exposed, with ClickHouse. In the process, enjoy some truly stunning images!"
---

# Announcing adsb.exposed - Interactive Visualization and Analytics on ADS-B Flight Data with ClickHouse 

You’ve probably heard of Flight Radar, the Real-Time Flight Tracker Map, and had a lot of fun following aircraft around the sky, but in this blog post, we’ll introduce you to something even cooler!!

ADS-B (Automatic Dependent Surveillance-Broadcast) is a radio protocol used to broadcast various flight data. Our co founder and CTO Alexey Milovidov has built an interactive visualization and analytics tool on this data. If nothing else, he's invented an entirely new art form in the process!

![newyork.png](https://clickhouse.com/uploads/newyork_4b4291b34f.png)
[Helicopters over Manhattan](https://adsb.exposed/?zoom=12&lat=40.7168&lng=285.9893&query=e18e8c8d6a1db73c63953798ad8919a9)

This website aggregates and visualizes massive amounts of air traffic data. The data is hosted in a[ ClickHouse](https://github.com/ClickHouse/ClickHouse/) database and queried on the fly. You can tune the visualizations with custom SQL queries and drill down from 50 billion records to individual data records. The result is some pretty spectacular imagery!

While this blog post mainly focuses on how the demo was built, feel free to [skip to the end](/blog/interactive-visualization-analytics-adsb-flight-data-with-clickhouse#awesome-visualizations) for some jaw-dropping visuals. 

Alternatively, visit [https://adsb.exposed](https://adsb.exposed), find the visual for your local city, and share it on social media! We’re offering a ClickHouse T-shirt to the most beautiful image, and the winner will be [announced on our next community call](https://clickhouse.com/company/events/v24-4-community-release-call) on 30th April.

The full source code for this demo can be found [here](https://github.com/ClickHouse/adsb.exposed?tab=readme-ov-file).

## How do you get ADS-B data?

ADS-B is broadcast by "transponders" installed on airplanes (and not only planes). This protocol is unencrypted, and there are no restrictions on collecting, using, or redistributing this data. Most passenger airplanes are obligated to broadcast this data, and even gliders, drones, and airport ground vehicles in certain countries. Military and private light aircraft might or may not broadcast.

It is possible to collect this data out of thin air using your own radio receiver (e.g., in the form of SDR), although your receiver will see the data only in a specific range of your location. There are platforms for sharing and exchange of this data. Some platforms invite participants to share the data but restrict its redistribution by providing commercial access. While the source data, broadcast by airplanes, is essentially public domain, the companies may produce and license derivative works from this data.

We use the data from two sources: [ADSB.lol](https://www.adsb.lol/) (complete historical data is provided without restrictions: 30 to 50 million records per day, available since 2023 under the [Open Database License](https://github.com/adsblol/globe_history_2024/blob/main/LICENSE-ODbL.txt)) and [ADSB-Exchange](https://www.adsbexchange.com/products/historical-data/) (only provides samples of data from the first day of each month: around 1.2 billion records per day with better coverage).

<blockquote style="font-size: 14px;">
<p>Another promising data source, <a href="https://airplanes.live/">airplanes.live</a>, has been brought to our attention. The author offered to provide historical and real-time data for non-commercial usage. It has great coverage and data quality, and we are going to include it in the following days.</p>
</blockquote>

## Implementation Details

The website is implemented as a single HTML page. It does not use JavaScript frameworks, and the source code is not minified, so it is easy to read.

### Rendering the Map

The [Leaflet](https://github.com/Leaflet/Leaflet/) library is used to display the map in two layers. The background layer uses tiles from OpenStreetMap to create a typical geographic map. The main layer overlays the visualization on top of the background map.

The visualization layer uses a `GridLayer` with a custom callback function, `createTile` which generates Canvas elements on the fly:

<pre style="font-size: 14px;"><code class="hljs language-javascript">L.<span class="hljs-property">GridLayer</span>.<span class="hljs-property">ClickHouse</span> = L.<span class="hljs-property">GridLayer</span>.<span class="hljs-title function_">extend</span>({
	<span class="hljs-attr">createTile</span>: <span class="hljs-keyword">function</span>(<span class="hljs-params">coords, done</span>) {
    	<span class="hljs-keyword">let</span> tile = L.<span class="hljs-property">DomUtil</span>.<span class="hljs-title function_">create</span>(<span class="hljs-string">'canvas'</span>, <span class="hljs-string">'leaflet-tile'</span>);
    	tile.<span class="hljs-property">width</span> = <span class="hljs-number">1024</span>;
    	tile.<span class="hljs-property">height</span> = <span class="hljs-number">1024</span>;
    	<span class="hljs-title function_">render</span>(<span class="hljs-variable language_">this</span>.<span class="hljs-property">options</span>.<span class="hljs-property">table</span>, <span class="hljs-variable language_">this</span>.<span class="hljs-property">options</span>.<span class="hljs-property">priority</span>, coords, tile).<span class="hljs-title function_">then</span>(<span class="hljs-function"><span class="hljs-params">err</span> =&gt;</span> <span class="hljs-title function_">done</span>(err, tile));
    	<span class="hljs-keyword">return</span> tile;
	}
});

<span class="hljs-keyword">const</span> layer_options = {
	<span class="hljs-attr">tileSize</span>: <span class="hljs-number">1024</span>,
	<span class="hljs-attr">minZoom</span>: <span class="hljs-number">2</span>,
	<span class="hljs-attr">maxZoom</span>: <span class="hljs-number">19</span>,
	<span class="hljs-attr">minNativeZoom</span>: <span class="hljs-number">2</span>,
	<span class="hljs-attr">maxNativeZoom</span>: <span class="hljs-number">16</span>,
	<span class="hljs-attr">attribution</span>: <span class="hljs-string">'(c) Alexey Milovidov, ClickHouse, Inc. (data: adsb.lol, adsbexchange.com)'</span>
};
</code></pre>
Each tile has a high resolution of 1024x1024 size to lower the number of requests to the database.

The rendering function performs a request to ClickHouse using its HTTP API with the JavaScript's fetch function:

<pre style="font-size: 14px;"><code class="hljs language-javascript"><span class="hljs-keyword">const</span> query_id = <span class="hljs-string">`<span class="hljs-subst">${uuid}</span>-<span class="hljs-subst">${query_sequence_num}</span>-<span class="hljs-subst">${table}</span>-<span class="hljs-subst">${coords.z - <span class="hljs-number">2</span>}</span>-<span class="hljs-subst">${coords.x}</span>-<span class="hljs-subst">${coords.y}</span>`</span>;
<span class="hljs-keyword">const</span> hosts = <span class="hljs-title function_">getHosts</span>(key);
<span class="hljs-keyword">const</span> <span class="hljs-title function_">url</span> = host =&gt; <span class="hljs-string">`<span class="hljs-subst">${host}</span>/?user=website&amp;default_format=RowBinary`</span> +
	<span class="hljs-string">`&amp;query_id=<span class="hljs-subst">${query_id}</span>&amp;replace_running_query=1`</span> +
	<span class="hljs-string">`&amp;param_table=<span class="hljs-subst">${table}</span>&amp;param_sampling=<span class="hljs-subst">${[<span class="hljs-number">0</span>, <span class="hljs-number">100</span>, <span class="hljs-number">10</span>, <span class="hljs-number">1</span>][priority]}</span>`</span> +
	<span class="hljs-string">`&amp;param_z=<span class="hljs-subst">${coords.z - <span class="hljs-number">2</span>}</span>&amp;param_x=<span class="hljs-subst">${coords.x}</span>&amp;param_y=<span class="hljs-subst">${coords.y}</span>`</span>;

progress_update_period = <span class="hljs-number">1</span>;
<span class="hljs-keyword">const</span> response = <span class="hljs-keyword">await</span> <span class="hljs-title class_">Promise</span>.<span class="hljs-title function_">race</span>(hosts.<span class="hljs-title function_">map</span>(<span class="hljs-function"><span class="hljs-params">host</span> =&gt;</span> <span class="hljs-title function_">fetch</span>(<span class="hljs-title function_">url</span>(host), { <span class="hljs-attr">method</span>: <span class="hljs-string">'POST'</span>, <span class="hljs-attr">body</span>: sql })));
</code></pre>

A user can edit the SQL query on the fly using a form on the page to adjust the visualization. This parameterized query accepts tile coordinates (x, y) and zoom level as parameters.

The query returns RGBA values of each pixel of the image in the RowBinary format (1024x1024 pixels, 1048576 rows, 4 bytes each, 4 MiB in total for each tile). It uses ZSTD compression in HTTP response as long as the browser supports it. It was a nice observation that ZSTD compression over raw pixels bitmap works better than PNG! (not surprising, though).

While the image data is often compressed several times, hundreds of megabytes still have to be transferred over the network. This is why the service can feel slow on bad Internet connections.

<pre style="font-size: 14px;"><code class="hljs language-javascript"><span class="hljs-keyword">let</span> ctx = tile.<span class="hljs-title function_">getContext</span>(<span class="hljs-string">'2d'</span>);
<span class="hljs-keyword">let</span> image = ctx.<span class="hljs-title function_">createImageData</span>(<span class="hljs-number">1024</span>, <span class="hljs-number">1024</span>, {<span class="hljs-attr">colorSpace</span>: <span class="hljs-string">'display-p3'</span>});
<span class="hljs-keyword">let</span> arr = <span class="hljs-keyword">new</span> <span class="hljs-title class_">Uint8ClampedArray</span>(buf);

<span class="hljs-keyword">for</span> (<span class="hljs-keyword">let</span> i = <span class="hljs-number">0</span>; i &lt; <span class="hljs-number">1024</span> * <span class="hljs-number">1024</span> * <span class="hljs-number">4</span>; ++i) { image.<span class="hljs-property">data</span>[i] = arr[i]; }

ctx.<span class="hljs-title function_">putImageData</span>(image, <span class="hljs-number">0</span>, <span class="hljs-number">0</span>, <span class="hljs-number">0</span>, <span class="hljs-number">0</span>, <span class="hljs-number">1024</span>, <span class="hljs-number">1024</span>);
</code></pre>

The data is put on the canvas using the "Display P3" color space to have a wider gamut in supporting browsers.

We use three different tables with different levels of detail: `planes_mercator` contains 100% of the data, `planes_mercator_sample10` 10%, and `planes_mercator_sample100` 1%. The loading starts with a 1% sample to provide instant response even while rendering the whole world. After loading the first level of detail, it continues to the next level of 10% before progressing with 100% of the data. This delivers a nice effect on progressive loading.

The image data is also cached on the client using a simple JavaScript object:

<pre style="font-size: 14px;"><code class="hljs language-javascript"><span class="hljs-keyword">if</span> (!cached_tiles[key]) cached_tiles[key] = [];
<span class="hljs-comment">/// If there is a higer-detail tile, skip rendering of this level of detal.</span>
<span class="hljs-keyword">if</span> (cached_tiles[key][priority + <span class="hljs-number">1</span>]) <span class="hljs-keyword">return</span>;
buf = cached_tiles[key][priority];
</code></pre>

The only downside is that after browsing for a certain time, the page will eat too much memory - something to address in future versions.

### Database and Queries

The database is small by ClickHouse standards. As of March 29th, 2024, it had 44.47 billion rows in the planes_mercator table and was continuously updated with new records. It takes 1.6 TB of disk space.

The table schema is as follows (you can read it in the[ setup.sql](https://github.com/ClickHouse/adsb.exposed/blob/main/setup.sql) source):

<pre style="font-size: 14px;"><code class="hljs language-sql"><span class="hljs-keyword">CREATE</span> <span class="hljs-keyword">TABLE</span> planes_mercator
(
    `mercator_x` UInt32 MATERIALIZED <span class="hljs-number">4294967295</span> <span class="hljs-operator">*</span> ((lon <span class="hljs-operator">+</span> <span class="hljs-number">180</span>) <span class="hljs-operator">/</span> <span class="hljs-number">360</span>),
    `mercator_y` UInt32 MATERIALIZED <span class="hljs-number">4294967295</span> <span class="hljs-operator">*</span> ((<span class="hljs-number">1</span> <span class="hljs-operator">/</span> <span class="hljs-number">2</span>) <span class="hljs-operator">-</span> ((<span class="hljs-built_in">log</span>(<span class="hljs-built_in">tan</span>(((lat <span class="hljs-operator">+</span> <span class="hljs-number">90</span>) <span class="hljs-operator">/</span> <span class="hljs-number">360</span>) <span class="hljs-operator">*</span> pi())) <span class="hljs-operator">/</span> <span class="hljs-number">2</span>) <span class="hljs-operator">/</span> pi())),
    `<span class="hljs-type">time</span>` DateTime64(<span class="hljs-number">3</span>),
    `<span class="hljs-type">date</span>` <span class="hljs-type">Date</span>,
    `icao` String,
    `r` String,
    `t` LowCardinality(String),
    `dbFlags` Int32,
    `noRegData` Bool,
    `ownOp` LowCardinality(String),
    `<span class="hljs-keyword">year</span>` UInt16,
    `<span class="hljs-keyword">desc</span>` LowCardinality(String),
    `lat` Float64,
    `lon` Float64,
    `altitude` Int32,
    `ground_speed` Float32,
    `track_degrees` Float32,
    `flags` UInt32,
    `vertical_rate` Int32,
    `aircraft_alert` Int64,
    `aircraft_alt_geom` Int64,
    `aircraft_gva` Int64,
    `aircraft_nac_p` Int64,
    `aircraft_nac_v` Int64,
    `aircraft_nic` Int64,
    `aircraft_nic_baro` Int64,
    `aircraft_rc` Int64,
    `aircraft_sda` Int64,
    `aircraft_sil` Int64,
    `aircraft_sil_type` LowCardinality(String),
    `aircraft_spi` Int64,
    `aircraft_track` Float64,
    `aircraft_type` LowCardinality(String),
    `aircraft_version` Int64,
    `aircraft_category` Enum8(<span class="hljs-string">'A0'</span>, <span class="hljs-string">'A1'</span>, <span class="hljs-string">'A2'</span>, <span class="hljs-string">'A3'</span>, <span class="hljs-string">'A4'</span>, <span class="hljs-string">'A5'</span>, <span class="hljs-string">'A6'</span>, <span class="hljs-string">'A7'</span>, <span class="hljs-string">'B0'</span>, <span class="hljs-string">'B1'</span>, <span class="hljs-string">'B2'</span>, <span class="hljs-string">'B3'</span>, <span class="hljs-string">'B4'</span>, <span class="hljs-string">'B5'</span>, <span class="hljs-string">'B6'</span>, <span class="hljs-string">'B7'</span>, <span class="hljs-string">'C0'</span>, <span class="hljs-string">'C1'</span>, <span class="hljs-string">'C2'</span>, <span class="hljs-string">'C3'</span>, <span class="hljs-string">'C4'</span>, <span class="hljs-string">'C5'</span>, <span class="hljs-string">'C6'</span>, <span class="hljs-string">'C7'</span>, <span class="hljs-string">'D0'</span>, <span class="hljs-string">'D1'</span>, <span class="hljs-string">'D2'</span>, <span class="hljs-string">'D3'</span>, <span class="hljs-string">'D4'</span>, <span class="hljs-string">'D5'</span>, <span class="hljs-string">'D6'</span>, <span class="hljs-string">'D7'</span>, <span class="hljs-string">''</span>),
    `aircraft_emergency` Enum8(<span class="hljs-string">''</span>, <span class="hljs-string">'none'</span>, <span class="hljs-string">'general'</span>, <span class="hljs-string">'downed'</span>, <span class="hljs-string">'lifeguard'</span>, <span class="hljs-string">'minfuel'</span>, <span class="hljs-string">'nordo'</span>, <span class="hljs-string">'unlawful'</span>, <span class="hljs-string">'reserved'</span>),
    `aircraft_flight` LowCardinality(String),
    `aircraft_squawk` String,
    `aircraft_baro_rate` Int64,
    `aircraft_nav_altitude_fms` Int64,
    `aircraft_nav_altitude_mcp` Int64,
    `aircraft_nav_modes` <span class="hljs-keyword">Array</span>(Enum8(<span class="hljs-string">'althold'</span>, <span class="hljs-string">'approach'</span>, <span class="hljs-string">'autopilot'</span>, <span class="hljs-string">'lnav'</span>, <span class="hljs-string">'tcas'</span>, <span class="hljs-string">'vnav'</span>)),
    `aircraft_nav_qnh` Float64,
    `aircraft_geom_rate` Int64,
    `aircraft_ias` Int64,
    `aircraft_mach` Float64,
    `aircraft_mag_heading` Float64,
    `aircraft_oat` Int64,
    `aircraft_roll` Float64,
    `aircraft_tas` Int64,
    `aircraft_tat` Int64,
    `aircraft_true_heading` Float64,
    `aircraft_wd` Int64,
    `aircraft_ws` Int64,
    `aircraft_track_rate` Float64,
    `aircraft_nav_heading` Float64,
    `source` LowCardinality(String),
    `geometric_altitude` Int32,
    `geometric_vertical_rate` Int32,
    `indicated_airspeed` Int32,
    `roll_angle` Float32,
    INDEX idx_x mercator_x TYPE minmax GRANULARITY <span class="hljs-number">1</span>,
    INDEX idx_y mercator_y TYPE minmax GRANULARITY <span class="hljs-number">1</span>
)
ENGINE <span class="hljs-operator">=</span> MergeTree
<span class="hljs-keyword">ORDER</span> <span class="hljs-keyword">BY</span> (mortonEncode(mercator_x, mercator_y), <span class="hljs-type">time</span>)
</code></pre>

This schema contains lat and lon values that are converted to coordinates in the Web-Mercator projection automatically with [MATERIALIZED columns](https://clickhouse.com/docs/en/sql-reference/statements/alter/column#materialize-column). This is used by the Leaflet software and most of the maps on the Internet. The Mercator coordinates are stored in UInt32, making it easy to do arithmetics with tile coordinates and zoom levels in a SQL query.

A Morton Curve of Web Mercator sorts the table coordinates with a [minmax index](https://clickhouse.com/docs/en/optimize/skipping-indexes), allowing queries for certain tiles to only read the data they need.

[Materialized Views](https://clickhouse.com/docs/en/guides/developer/cascading-materialized-views) are used to produce the tables for different detail levels:

<pre style="font-size: 14px;"><code class="hljs language-sql"><span class="hljs-keyword">CREATE</span> <span class="hljs-keyword">TABLE</span> planes_mercator_sample10 <span class="hljs-keyword">AS</span> planes_mercator;

<span class="hljs-keyword">CREATE</span> <span class="hljs-keyword">TABLE</span> planes_mercator_sample100 <span class="hljs-keyword">AS</span> planes_mercator;

<span class="hljs-keyword">CREATE</span> MATERIALIZED <span class="hljs-keyword">VIEW</span> view_sample10 <span class="hljs-keyword">TO</span> planes_mercator_sample10
<span class="hljs-keyword">AS</span> <span class="hljs-keyword">SELECT</span> <span class="hljs-operator">*</span>
<span class="hljs-keyword">FROM</span> planes_mercator
<span class="hljs-keyword">WHERE</span> (rand() <span class="hljs-operator">%</span> <span class="hljs-number">10</span>) <span class="hljs-operator">=</span> <span class="hljs-number">0</span>;

<span class="hljs-keyword">CREATE</span> MATERIALIZED <span class="hljs-keyword">VIEW</span> view_sample100 <span class="hljs-keyword">TO</span> planes_mercator_sample100
<span class="hljs-keyword">AS</span> <span class="hljs-keyword">SELECT</span> <span class="hljs-operator">*</span>
<span class="hljs-keyword">FROM</span> planes_mercator
<span class="hljs-keyword">WHERE</span> (rand() <span class="hljs-operator">%</span> <span class="hljs-number">100</span>) <span class="hljs-operator">=</span> <span class="hljs-number">0</span>;
</code></pre>

### Using ClickHouse Cloud

We use a service on our staging environment in[ ClickHouse Cloud](https://clickhouse.com/cloud). The staging environment is used to test new ClickHouse versions and new types of infrastructure that we implement. 

For example, we can try different types of machines and different scales of the service, or we can test new features, such as distributed cache, that are in development. 

The staging environment also uses fault injection: We interrupt network connections with a certain probability to ensure that the service operates normally. Furthermore, it exploits chaos engineering: We terminate various machines of `clickhouse-server` and `clickhouse-keeper` at random and also randomly scale the service back and forth to a different number of machines. This is how this project facilitates the development and testing of our service.

Finally, requests are also load-balanced to a backup service. Whichever service returns first will be used. This is how we can avoid downtime while still using our staging environment.

### Example query: Boeing vs. Airbus

Consider the following rather topical visualization: ["Boeing vs. Airbus"](https://adsb.exposed/?zoom=3&lat=14.4347&lng=26.0156&query=ecd939dcdb623a87a0965dd7985c7646).

<a href="https://adsb.exposed/?zoom=3&lat=14.4347&lng=26.0156&query=ecd939dcdb623a87a0965dd7985c7646" target="_blank"><img src="/uploads/boeing_vs_airbus_04895d9640.png"/></a>

Let's take a look at an SQL query for this visualization:

<pre style="font-size: 14px;"><code class="hljs language-sql"><span class="hljs-keyword">WITH</span>
	bitShiftLeft(<span class="hljs-number">1</span>::UInt64, {z:UInt8}) <span class="hljs-keyword">AS</span> zoom_factor,
	bitShiftLeft(<span class="hljs-number">1</span>::UInt64, <span class="hljs-number">32</span> <span class="hljs-operator">-</span> {z:UInt8}) <span class="hljs-keyword">AS</span> tile_size,

	tile_size <span class="hljs-operator">*</span> {x:UInt16} <span class="hljs-keyword">AS</span> tile_x_begin,
	tile_size <span class="hljs-operator">*</span> ({x:UInt16} <span class="hljs-operator">+</span> <span class="hljs-number">1</span>) <span class="hljs-keyword">AS</span> tile_x_end,

	tile_size <span class="hljs-operator">*</span> {y:UInt16} <span class="hljs-keyword">AS</span> tile_y_begin,
	tile_size <span class="hljs-operator">*</span> ({y:UInt16} <span class="hljs-operator">+</span> <span class="hljs-number">1</span>) <span class="hljs-keyword">AS</span> tile_y_end,

	mercator_x <span class="hljs-operator">&gt;=</span> tile_x_begin <span class="hljs-keyword">AND</span> mercator_x <span class="hljs-operator">&lt;</span> tile_x_end
	<span class="hljs-keyword">AND</span> mercator_y <span class="hljs-operator">&gt;=</span> tile_y_begin <span class="hljs-keyword">AND</span> mercator_y <span class="hljs-operator">&lt;</span> tile_y_end <span class="hljs-keyword">AS</span> in_tile,

	bitShiftRight(mercator_x <span class="hljs-operator">-</span> tile_x_begin, <span class="hljs-number">32</span> <span class="hljs-operator">-</span> <span class="hljs-number">10</span> <span class="hljs-operator">-</span> {z:UInt8}) <span class="hljs-keyword">AS</span> x,
	bitShiftRight(mercator_y <span class="hljs-operator">-</span> tile_y_begin, <span class="hljs-number">32</span> <span class="hljs-operator">-</span> <span class="hljs-number">10</span> <span class="hljs-operator">-</span> {z:UInt8}) <span class="hljs-keyword">AS</span> y,

	y <span class="hljs-operator">*</span> <span class="hljs-number">1024</span> <span class="hljs-operator">+</span> x <span class="hljs-keyword">AS</span> pos,

	<span class="hljs-built_in">count</span>() <span class="hljs-keyword">AS</span> total,
	<span class="hljs-built_in">sum</span>(<span class="hljs-keyword">desc</span> <span class="hljs-keyword">LIKE</span> <span class="hljs-string">'BOEING%'</span>) <span class="hljs-keyword">AS</span> boeing,
	<span class="hljs-built_in">sum</span>(<span class="hljs-keyword">desc</span> <span class="hljs-keyword">LIKE</span> <span class="hljs-string">'AIRBUS%'</span>) <span class="hljs-keyword">AS</span> airbus,
	<span class="hljs-built_in">sum</span>(<span class="hljs-keyword">NOT</span> (<span class="hljs-keyword">desc</span> <span class="hljs-keyword">LIKE</span> <span class="hljs-string">'BOEING%'</span> <span class="hljs-keyword">OR</span> <span class="hljs-keyword">desc</span> <span class="hljs-keyword">LIKE</span> <span class="hljs-string">'AIRBUS%'</span>)) <span class="hljs-keyword">AS</span> other,

	greatest(<span class="hljs-number">1000000</span> DIV {sampling:UInt32} DIV zoom_factor, total) <span class="hljs-keyword">AS</span> max_total,
	greatest(<span class="hljs-number">1000000</span> DIV {sampling:UInt32} DIV zoom_factor, boeing) <span class="hljs-keyword">AS</span> max_boeing,
	greatest(<span class="hljs-number">1000000</span> DIV {sampling:UInt32} DIV zoom_factor, airbus) <span class="hljs-keyword">AS</span> max_airbus,
	greatest(<span class="hljs-number">1000000</span> DIV {sampling:UInt32} DIV zoom_factor, other) <span class="hljs-keyword">AS</span> max_other,

	pow(total <span class="hljs-operator">/</span> max_total, <span class="hljs-number">1</span><span class="hljs-operator">/</span><span class="hljs-number">5</span>) <span class="hljs-keyword">AS</span> transparency,

	<span class="hljs-number">255</span> <span class="hljs-operator">*</span> (<span class="hljs-number">1</span> <span class="hljs-operator">+</span> transparency) <span class="hljs-operator">/</span> <span class="hljs-number">2</span> <span class="hljs-keyword">AS</span> alpha,
	pow(boeing, <span class="hljs-number">1</span><span class="hljs-operator">/</span><span class="hljs-number">5</span>) <span class="hljs-operator">*</span> <span class="hljs-number">256</span> DIV (<span class="hljs-number">1</span> <span class="hljs-operator">+</span> pow(max_boeing, <span class="hljs-number">1</span><span class="hljs-operator">/</span><span class="hljs-number">5</span>)) <span class="hljs-keyword">AS</span> red,
	pow(airbus, <span class="hljs-number">1</span><span class="hljs-operator">/</span><span class="hljs-number">5</span>) <span class="hljs-operator">*</span> <span class="hljs-number">256</span> DIV (<span class="hljs-number">1</span> <span class="hljs-operator">+</span> pow(max_airbus, <span class="hljs-number">1</span><span class="hljs-operator">/</span><span class="hljs-number">5</span>)) <span class="hljs-keyword">AS</span> green,
	pow(other, <span class="hljs-number">1</span><span class="hljs-operator">/</span><span class="hljs-number">5</span>) <span class="hljs-operator">*</span> <span class="hljs-number">256</span> DIV (<span class="hljs-number">1</span> <span class="hljs-operator">+</span> pow(max_other, <span class="hljs-number">1</span><span class="hljs-operator">/</span><span class="hljs-number">5</span>)) <span class="hljs-keyword">AS</span> blue

<span class="hljs-keyword">SELECT</span> round(red)::UInt8, round(green)::UInt8, round(blue)::UInt8, round(alpha)::UInt8
<span class="hljs-keyword">FROM</span> {<span class="hljs-keyword">table</span>:Identifier}
<span class="hljs-keyword">WHERE</span> in_tile
<span class="hljs-keyword">GROUP</span> <span class="hljs-keyword">BY</span> pos <span class="hljs-keyword">ORDER</span> <span class="hljs-keyword">BY</span> pos <span class="hljs-keyword">WITH</span> FILL <span class="hljs-keyword">FROM</span> <span class="hljs-number">0</span> <span class="hljs-keyword">TO</span> <span class="hljs-number">1024</span><span class="hljs-operator">*</span><span class="hljs-number">1024</span>
</code></pre>

The first part of the query calculates the condition `in_tile`, which is used in the `WHERE` section to filter the data in the requested tile. It then calculates the colors: alpha, red, green, and blue. They are adjusted by the [`pow`](https://clickhouse.com/docs/en/sql-reference/functions/math-functions#pow) function for better uniformity, clamped to the `0..255` range, and converted to `UInt8`. The sampling parameter is used for adjustment so that queries with a lower level of detail will return pictures with mostly the same relative colors. We group by the pixel coordinate pos and also use the [WITH FILL modifier](https://clickhouse.com/docs/en/sql-reference/statements/select/order-by#order-by-expr-with-fill-modifier) in the ORDER BY to fill zeros in the pixel positions that have no data. As a result, we will get an RGBA bitmap with the exact 1024x1024 size.

### Reports

If you select an area with the right mouse button or use a selection tool, it will generate a report from the database for the selection area. This is entirely straightforward. For example, here is a query for the top aircraft types:

<pre style="font-size: 14px;"><code class="hljs language-javascript"><span class="hljs-keyword">const</span> sql_types = <span class="hljs-string">`
	WITH mercator_x &gt;= {left:UInt32} AND mercator_x &lt; {right:UInt32}
    	AND mercator_y &gt;= {top:UInt32} AND mercator_y &lt; {bottom:UInt32} AS in_tile
	SELECT t, anyIf(desc, desc != '') AS desc, count() AS c
	FROM {table:Identifier}
	WHERE t != '' AND <span class="hljs-subst">${condition}</span>
	GROUP BY t
	ORDER BY c DESC
	LIMIT 100`</span>;
</code></pre>

The report is calculated for flight numbers, aircraft types, registration (tail numbers), and owners. You can click on any item and it will apply a filter to the main SQL query. For example, click on A388 and it will show you a visualization for the Airbus 380-800.

As a bonus, if you move the cursor over an aircraft type, it will go to Wikipedia API and try to find a picture of this aircraft. It often finds something else on Wikipedia, though.

### Saved Queries

You can edit a query and then share a link. The query is converted to a 128-bit hash and saved in the same ClickHouse database:

<pre style="font-size: 14px;"><code class="hljs language-javascript"><span class="hljs-keyword">async</span> <span class="hljs-keyword">function</span> <span class="hljs-title function_">saveQuery</span>(<span class="hljs-params">text</span>) {
	<span class="hljs-keyword">const</span> sql = <span class="hljs-string">`INSERT INTO saved_queries (text) FORMAT RawBLOB`</span>;
	<span class="hljs-keyword">const</span> hosts = <span class="hljs-title function_">getHosts</span>(<span class="hljs-literal">null</span>);
	<span class="hljs-keyword">const</span> <span class="hljs-title function_">url</span> = host =&gt; <span class="hljs-string">`<span class="hljs-subst">${host}</span>/?user=website_saved_queries&amp;query=<span class="hljs-subst">${<span class="hljs-built_in">encodeURIComponent</span>(sql)}</span>`</span>;
	<span class="hljs-keyword">const</span> response = <span class="hljs-keyword">await</span> <span class="hljs-title class_">Promise</span>.<span class="hljs-title function_">all</span>(hosts.<span class="hljs-title function_">map</span>(<span class="hljs-function"><span class="hljs-params">host</span> =&gt;</span> <span class="hljs-title function_">fetch</span>(<span class="hljs-title function_">url</span>(host), { <span class="hljs-attr">method</span>: <span class="hljs-string">'POST'</span>, <span class="hljs-attr">body</span>: text })));
}

<span class="hljs-keyword">async</span> <span class="hljs-keyword">function</span> <span class="hljs-title function_">loadQuery</span>(<span class="hljs-params">hash</span>) {
	<span class="hljs-keyword">const</span> sql = <span class="hljs-string">`SELECT text FROM saved_queries WHERE hash = unhex({hash:String}) LIMIT 1`</span>;
	<span class="hljs-keyword">const</span> hosts = <span class="hljs-title function_">getHosts</span>(<span class="hljs-literal">null</span>);
	<span class="hljs-keyword">const</span> <span class="hljs-title function_">url</span> = host =&gt; <span class="hljs-string">`<span class="hljs-subst">${host}</span>/?user=website_saved_queries&amp;default_format=JSON&amp;param_hash=<span class="hljs-subst">${hash}</span>`</span>;
	<span class="hljs-keyword">const</span> response = <span class="hljs-keyword">await</span> <span class="hljs-title class_">Promise</span>.<span class="hljs-title function_">race</span>(hosts.<span class="hljs-title function_">map</span>(<span class="hljs-function"><span class="hljs-params">host</span> =&gt;</span> <span class="hljs-title function_">fetch</span>(<span class="hljs-title function_">url</span>(host), { <span class="hljs-attr">method</span>: <span class="hljs-string">'POST'</span>, <span class="hljs-attr">body</span>: sql })));
	<span class="hljs-keyword">const</span> data = <span class="hljs-keyword">await</span> response.<span class="hljs-title function_">json</span>();
	<span class="hljs-keyword">return</span> data.<span class="hljs-property">data</span>[<span class="hljs-number">0</span>].<span class="hljs-property">text</span>;
}
</code></pre>

We use a different user `website_saved_queries` with different access control and quotas for these queries.

### Progress Bar

It is nice to display a progress bar with the amount of data processed in rows and bytes.

<pre style="font-size: 14px;"><code class="hljs language-javascript"><span class="hljs-keyword">const</span> sql = <span class="hljs-string">`SELECT
        	sum(read_rows) AS r,
        	sum(total_rows_approx) AS t,
        	sum(read_bytes) AS b,
        	r / max(elapsed) AS rps,
        	b / max(elapsed) AS bps,
        	formatReadableQuantity(r) AS formatted_rows,
        	formatReadableSize(b) AS formatted_bytes,
        	formatReadableQuantity(rps) AS formatted_rps,
        	formatReadableSize(bps) AS formatted_bps
    	FROM clusterAllReplicas(default, system.processes)
    	WHERE user = 'website' AND startsWith(query_id, {uuid:String})`</span>;

	<span class="hljs-keyword">const</span> hosts = <span class="hljs-title function_">getHosts</span>(uuid);
	<span class="hljs-keyword">const</span> <span class="hljs-title function_">url</span> = host =&gt; <span class="hljs-string">`<span class="hljs-subst">${host}</span>/?user=website_progress&amp;default_format=JSON&amp;param_uuid=<span class="hljs-subst">${uuid}</span>`</span>;

	<span class="hljs-keyword">let</span> responses = <span class="hljs-keyword">await</span> <span class="hljs-title class_">Promise</span>.<span class="hljs-title function_">all</span>(hosts.<span class="hljs-title function_">map</span>(<span class="hljs-function"><span class="hljs-params">host</span> =&gt;</span> <span class="hljs-title function_">fetch</span>(<span class="hljs-title function_">url</span>(host), { <span class="hljs-attr">method</span>: <span class="hljs-string">'POST'</span>, <span class="hljs-attr">body</span>: sql })));
	<span class="hljs-keyword">let</span> datas = <span class="hljs-keyword">await</span> <span class="hljs-title class_">Promise</span>.<span class="hljs-title function_">all</span>(responses.<span class="hljs-title function_">map</span>(<span class="hljs-function"><span class="hljs-params">response</span> =&gt;</span> response.<span class="hljs-title function_">json</span>()));
</code></pre>

We select from the `system.processes` table across all servers in the cluster. It does not display the precise progress because there are many tiles requested in parallel and many queries, with some of them finished and some still in progress. The query will see only in-progress queries, so the total processed records will be lower than the actual.

We also color the progress bar differently when we are loading the first level of detail, the second level of detail, etc.

### Cache Locality

The service in ClickHouse Cloud can use multiple replicas, and by default, the requests are routed to an arbitrary healthy replica. Queries that process a large amount of data will be parallelized across many replicas, whereas simpler queries will use just a single replica. The data is stored in AWS S3 and each replica pod also has a locally attached SSD which is used for the cache, and consequently, the page cache in memory also impacts the final query time.

## Awesome visualizations

Below we present some of the initial images selected by Alexey. This touches the surface, with the site providing a treasure trove of free wall art! 

### [Denver Airport](https://adsb.exposed/?zoom=11&lat=39.8665&lng=255.3566&query=dd3c1af70baafa35055b06fa3556d96e)

<a href="https://adsb.exposed/?zoom=11&lat=39.8665&lng=255.3566&query=dd3c1af70baafa35055b06fa3556d96e" target="_blank"><img src="/uploads/denver_a93317a793.png"/></a>

If we [zoom into the airport](https://adsb.exposed/?zoom=15&lat=39.8592&lng=255.3276&query=b4659aba93f0e495ef2aa837ee793874), we can see where the planes are parked and even color them by a manufacturer or an airline:

<a href="https://adsb.exposed/?zoom=15&lat=39.8592&lng=255.3276&query=b4659aba93f0e495ef2aa837ee793874" target="_blank"><img src="/uploads/denver_airlines_47d20cce6b.png"/></a>

### [Military training in Texas](https://adsb.exposed/?zoom=7&lat=32.1944&lng=261.9682&query=64acf6eb47ad04237460ef46873f3bc3)

<a href="https://adsb.exposed/?zoom=7&lat=32.1944&lng=261.9682&query=64acf6eb47ad04237460ef46873f3bc3" target="_blank"><img src="/uploads/texas_military_1daff87bbf.png"/></a>

### [In London, helicopters fly over the river](https://adsb.exposed/?zoom=12&lat=51.5079&lng=359.8960&query=e18e8c8d6a1db73c63953798ad8919a9)

<a href="https://adsb.exposed/?zoom=12&lat=51.5079&lng=359.8960&query=e18e8c8d6a1db73c63953798ad8919a9" target="_blank"><img src="/uploads/London_helicopters_2229e7507c.png"/></a>

### [In Las Vegas there is no river](https://adsb.exposed/?zoom=10&lat=36.1374&lng=244.8811&query=e18e8c8d6a1db73c63953798ad8919a9)

<a href="https://adsb.exposed/?zoom=10&lat=36.1374&lng=244.8811&query=e18e8c8d6a1db73c63953798ad8919a9" target="_blank"><img src="/uploads/Vegas_46ae535118.png"/></a>

### [Bay Area small airports](https://adsb.exposed/?zoom=9&lat=37.8100&lng=238.0987&query=045cd07e7640e0b6b0d10cf0fd80282c)

<a href="https://adsb.exposed/?zoom=9&lat=37.8100&lng=238.0987&query=045cd07e7640e0b6b0d10cf0fd80282c" target="_blank"><img src="/uploads/Adsb_Exposed_Issue_432_ecf338ecc1.png"/></a>

### [F-16 air bases in the US](https://adsb.exposed/?zoom=5&lat=37.0900&lng=267.1385&query=b8af6c7320f23c451d629cea6ae21826)

<a href="https://adsb.exposed/?zoom=5&lat=37.0900&lng=267.1385&query=b8af6c7320f23c451d629cea6ae21826" target="_blank"><img src="/uploads/f16s_2ded0c9d97.png"/></a>

### [A strange hole near Mexico City](https://adsb.exposed/?zoom=9&lat=19.1139&lng=261.3813&query=dd3c1af70baafa35055b06fa3556d96e)

<a href="https://adsb.exposed/?zoom=9&lat=19.1139&lng=261.3813&query=dd3c1af70baafa35055b06fa3556d96e" target="_blank"><img src="/uploads/mexico_hole_4f405ccd56.png"/></a>

### [A volcano](https://adsb.exposed/?zoom=8&lat=28.2122&lng=343.5701&query=dd3c1af70baafa35055b06fa3556d96e)

<a href="https://adsb.exposed/?zoom=8&lat=28.2122&lng=343.5701&query=dd3c1af70baafa35055b06fa3556d96e" target="_blank"><img src="/uploads/volcano_c91c697de0.png"/></a>

### [Area 51](https://adsb.exposed/?zoom=8&lat=37.2784&lng=243.9184&query=dd3c1af70baafa35055b06fa3556d96e)

<a href="https://adsb.exposed/?zoom=8&lat=37.2784&lng=243.9184&query=dd3c1af70baafa35055b06fa3556d96e" target="_blank"><img src="/uploads/area51_047000a0a2.png"/></a>

### [Emirates Engineering](https://adsb.exposed/?zoom=15&lat=25.2518&lng=55.3630&query=b4659aba93f0e495ef2aa837ee793874)

In Dubai Airport, the green hairball is a hangar of Emirates Engineering where Airbuses are maintained.

<a href="https://adsb.exposed/?zoom=15&lat=25.2518&lng=55.3630&query=b4659aba93f0e495ef2aa837ee793874" target="_blank"><img src="/uploads/emirates_engineering_35e196151d.png"/></a>

### [Airlines all over Europe](https://adsb.exposed/?zoom=5&lat=51.0966&lng=10.3271&query=e9f7cdd454ff0473b47d750316976179)

<a href="https://adsb.exposed/?zoom=5&lat=51.0966&lng=10.3271&query=e9f7cdd454ff0473b47d750316976179" target="_blank"><img src="/uploads/european_airlines_6c6f234a56.png"/></a>

### [Dallas small airports](https://adsb.exposed/?zoom=9&lat=32.9119&lng=262.9988&query=045cd07e7640e0b6b0d10cf0fd80282c)

<a href="https://adsb.exposed/?zoom=9&lat=32.9119&lng=262.9988&query=045cd07e7640e0b6b0d10cf0fd80282c" target="_blank"><img src="/uploads/dallas_80a8e1593c.png"/></a>
