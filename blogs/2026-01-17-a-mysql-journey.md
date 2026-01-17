---
title: "A MySQL Journey"
date: "2023-10-05T12:42:50.739Z"
author: "The ClickHouse Team"
category: "Engineering"
excerpt: "Read about how ClickHouse has built support for the MySQL protocol and syntax in order to unlock BI tooling and more"
---

# A MySQL Journey

![mysql journey darker path.png](https://clickhouse.com/uploads/mysql_journey_darker_path_bb3de4e1fe.png)

## Introduction

>"Simplicity is the ultimate sophistication." - Leonardo da Vinci

While we love announcing new features for our users at ClickHouse, sometimes their apparent simplicity and clear value can mask some of the significant efforts and complexity in making them possible. This couldn't be more true for our [recent announcement](https://clickhouse.com/blog/clickhouse-cloud-compatible-with-mysql) around supporting BI tools such as Looker Studio and Tableau online through the MySQL protocol. It's immediately obvious how valuable the ability to connect these to ClickHouse is for our users, enabling the simple building of visualizations on TiB of data with tools with which they are familiar. 

**_Readers may wonder why we choose to support these tools through the MySQL interface. This decision was principally based on the speed of providing an offering to our users. Online-only tools such as Looker Studio, Quicksight and Tableau online provide no option for users to use a custom driver and have no publicly available SDKs. While we continue to work with the vendors of these tools to develop official ClickHouse support, this route is invariably a longer-term project. Our existing MySQL support provided 90% of the required existing support. Enhancing this therefore offered the shortest route to meeting our users' needs and unlocking the power of these tools with Clickhouse._**

However, supporting these tools required a journey involving multiple teams within ClickHouse: from the integrations team evaluating and testing these tools against ClickHouse's MySQL interface to the changes required in ClickHouse to support specific MySQL syntax and the improvements to our proxy later to allow the protocol's use in Cloud. In this blog post, we explore some of these improvements.

As well as giving us an opportunity to thank wider contributions, this effort also highlights some of the improvements in the core product, which users can exploit beyond their use of BI tools. Specifically, the improvements in MySQL syntax will hopefully allow a smoother adoption for new users coming from MySQL or other OLTP data stores. For why users might want to consider moving workloads from MySQL/Postgres to ClickHouse, [we recommend a recent blog post](https://clickhouse.com/blog/migrating-data-between-clickhouse-postgres).

## It all starts with testing

On announcing ClickHouse Cloud late last year, we immediately saw a latent demand for visualizing data in ClickHouse. While tools such as Grafana and Superset offer powerful dashboarding features, they either focus on specific use cases or lack the feature maturity required by enterprise teams. More importantly, often, users simply want to use the tools with which they are familiar and productive. In the spirit of meeting users where they are, we set about evaluating the effort to support the MySQL protocol more completely in ClickHouse with the intention of tools such as Google’s Looker Studio and Tableau online "just working".

**_As of the time of writing, we support Looker Studio and Tableau online through the MySQL protocol. Additional improvements are underway that allow users to use AWS QuickSight._**

To achieve this, a period of testing was required. Since tools such as Looker generate SQL through query builders and user interactions (e.g., applying filters), these testing efforts identified a significant gap in support for MySQL syntax. This proved a significant and frustrating effort as often the lack of support for an expression or construct would render the tool useless, pausing further testing until resolved. Once resolved, further issues would arise, with no clear end in sight and this form of testing feeling like an endlessly recursive loop. Fortunately, after multiple enhancements and collaboration between the ClickHouse core and integrations teams, we were happy to announce support for ClickHouse OSS. Below we explore some of these enhancements, showing what is now possible.

**_While our support for the MySQL syntax is now sufficient for BI tooling, there remain outstanding issues, e.g. [[1]](https://github.com/ClickHouse/ClickHouse/issues/53066) [[2]](https://github.com/ClickHouse/ClickHouse/issues/53482). While we aspire to provide as much compatibility as possible, it is unlikely we will guarantee 100% compatibility. Attempting to do this will likely introduce undesirable dependencies and behaviors [[1]](https://github.com/ClickHouse/ClickHouse/pull/46581#discussion_r1117044078) [[2]](https://github.com/ClickHouse/ClickHouse/issues/43755#issuecomment-1482894628).  We are, however, committed to improving our support, mainly through efforts to ensure ANSI SQL differences are minimized, and we welcome issues and improvements._**

## Syntax enhancements

In the interest of keeping examples simple, we use the popular [UK house price dataset](https://clickhouse.com/docs/en/getting-started/example-datasets/uk-price-paid) below. This contains a row for every house sold in the UK between 1995 and the time of writing.

### SHOW COLUMNS

Before we could support any additional MySQL query syntax, support for basic DDL discovery operations was required. These queries are typically issued by BI tools on initial connection as part of a schema and index discovery exercise.  The first of these [`SHOW COLUMNS`](https://github.com/ClickHouse/ClickHouse/issues/49168) allows table columns to be discovered. Further [ClickHouse](https://clickhouse.com/docs/en/sql-reference/statements/show#show-columns) and [MySQL](https://dev.mysql.com/doc/refman/8.0/en/show-columns.html) details.

<pre style="font-size: 9px;"><code class="hljs language-sql"><span class="hljs-keyword">SHOW</span> COLUMNS <span class="hljs-keyword">FROM</span> uk_price_paid <span class="hljs-keyword">FROM</span> <span class="hljs-keyword">default</span> <span class="hljs-keyword">LIKE</span><span class="hljs-string">'%'</span>

┌─field─────┬─type────────────────────────────────────────────────────────────────────────────────┬─<span class="hljs-keyword">null</span>─┬─key─────┬─<span class="hljs-keyword">default</span>─┬─extra─┐
│ addr1 	│ String                                                                          	  │ <span class="hljs-keyword">NO</span>   │ PRI SOR │ ᴺᵁᴸᴸ	 │   	 │
│ addr2 	│ String                                                                          	  │ <span class="hljs-keyword">NO</span>   │ PRI SOR │ ᴺᵁᴸᴸ	 │   	 │
│ county	│ LowCardinality(String)                                                          	  │ <span class="hljs-keyword">NO</span>   │     	   │ ᴺᵁᴸᴸ	 │   	 │
│ <span class="hljs-type">date</span>  	│ <span class="hljs-type">Date</span>                                                                            	  │ <span class="hljs-keyword">NO</span>   │     	   │ ᴺᵁᴸᴸ	 │   	 │
│ district  │ LowCardinality(String)                                                          	  │ <span class="hljs-keyword">NO</span>   │     	   │ ᴺᵁᴸᴸ	 │   	 │
│ duration  │ Enum8(<span class="hljs-string">'unknown'</span> <span class="hljs-operator">=</span> <span class="hljs-number">0</span>, <span class="hljs-string">'freehold'</span> <span class="hljs-operator">=</span> <span class="hljs-number">1</span>, <span class="hljs-string">'leasehold'</span> <span class="hljs-operator">=</span> <span class="hljs-number">2</span>)                           	  │ <span class="hljs-keyword">NO</span>   │     	   │ ᴺᵁᴸᴸ	 │   	 │
│ is_new	│ UInt8                                                                           	  │ <span class="hljs-keyword">NO</span>   │     	   │ ᴺᵁᴸᴸ	 │   	 │
│ locality  │ LowCardinality(String)                                                          	  │ <span class="hljs-keyword">NO</span>   │     	   │ ᴺᵁᴸᴸ	 │   	 │
│ postcode1 │ LowCardinality(String)                                                          	  │ <span class="hljs-keyword">NO</span>   │ PRI SOR │ ᴺᵁᴸᴸ	 │   	 │
│ postcode2 │ LowCardinality(String)                                                          	  │ <span class="hljs-keyword">NO</span>   │ PRI SOR │ ᴺᵁᴸᴸ	 │   	 │
│ price 	│ UInt32                                                                          	  │ <span class="hljs-keyword">NO</span>   │     	   │ ᴺᵁᴸᴸ	 │   	 │
│ street	│ LowCardinality(String)                                                          	  │ <span class="hljs-keyword">NO</span>   │     	   │ ᴺᵁᴸᴸ	 │   	 │
│ town  	│ LowCardinality(String)                                                          	  │ <span class="hljs-keyword">NO</span>   │     	   │ ᴺᵁᴸᴸ	 │   	 │
│ type  	│ Enum8(<span class="hljs-string">'other'</span> <span class="hljs-operator">=</span> <span class="hljs-number">0</span>, <span class="hljs-string">'terraced'</span> <span class="hljs-operator">=</span> <span class="hljs-number">1</span>, <span class="hljs-string">'semi-detached'</span> <span class="hljs-operator">=</span> <span class="hljs-number">2</span>, <span class="hljs-string">'detached'</span> <span class="hljs-operator">=</span> <span class="hljs-number">3</span>, <span class="hljs-string">'flat'</span> <span class="hljs-operator">=</span> <span class="hljs-number">4</span>) │ <span class="hljs-keyword">NO</span>   │     	   │ ᴺᵁᴸᴸ	 │   	 │
└───────────┴─────────────────────────────────────────────────────────────────────────────────────┴──────┴─────────┴─────────┴───────┘

<span class="hljs-number">14</span> <span class="hljs-keyword">rows</span> <span class="hljs-keyword">in</span> set. Elapsed: <span class="hljs-number">0.009</span> sec.
</code></pre>

### SHOW KEYS

Tools additionally aim to identify indices in order to ensure queries are optimized where possible. This required support for the [`SHOW KEYS`](https://github.com/ClickHouse/ClickHouse/issues/49140) statement. Further [ClickHouse](https://clickhouse.com/docs/en/sql-reference/statements/show#show-index) and [MySQL](https://dev.mysql.com/doc/refman/8.0/en/show-index.html) details.

```sql
SHOW INDEXES FROM uk_price_paid
FORMAT Vertical

Row 1:
──────
table:     	uk_price_paid
non_unique:	1
key_name:  	PRIMARY
seq_in_index:  1
column_name:   addr1
collation: 	A
cardinality:   0
sub_part:  	ᴺᵁᴸᴸ
packed:    	ᴺᵁᴸᴸ
null:      	ᴺᵁᴸᴸ
index_type:	PRIMARY
comment:
index_comment:
visible:   	YES
expression:

4 rows in set. Elapsed: 0.007 sec.

```

### NULL safe equal

Once these initial “connection queries” had been overcome, it became apparent that BI tools can generate complex queries. For [“top results”,](https://github.com/ClickHouse/ClickHouse/issues/53061) for example, a JOIN is required using the [NULL safe equal](https://dev.mysql.com/doc/refman/8.0/en/comparison-operators.html#operator_equal-to) operator (also known as the [IS NOT DISTINCT FROM](https://github.com/ClickHouse/ClickHouse/issues/53061)). The NULL-safe equal operator (`<=>`) in MySQL is used in joins and comparisons to handle NULL values, allowing you to compare two expressions while treating NULL values as equal to each other. This is in contrast to the regular equal operator (`=`), which treats NULL as an unknown value and cannot be used to directly compare NULLs.

### MAKEDATE

While the ability to construct dates from year and day values has existed in ClickHouse [since 23.3](https://github.com/ClickHouse/ClickHouse/pull/35628), differences in the case of the function in MySQL meant this [required aliasing ](https://www.google.com/url?q=https://github.com/ClickHouse/ClickHouse/issues/49143&sa=D&source=docs&ust=1695652376986628&usg=AOvVaw22HavKHghx9JpKNjmLUgDP)in ClickHouse. These small differences turned out to be common occurrences during testing and, fortunately often needed [simple fixes](https://github.com/ClickHouse/ClickHouse/pull/49603/files).

Suppose we wished to find the month when houses are, on average, at their cheapest to purchase. Using this, we look to compute the average price for this month for the most expensive year.

```sql
WITH (
    	SELECT toYear(date) AS year
    	FROM uk_price_paid
    	GROUP BY year
    	ORDER BY avg(price) DESC
    	LIMIT 1
	) AS most_expensive_year,
	(
    	SELECT toMonth(date) AS month
    	FROM uk_price_paid
    	GROUP BY month
    	ORDER BY avg(price) ASC
    	LIMIT 1
	) AS cheapest_month
SELECT round(avg(price))
FROM uk_price_paid
WHERE date = MAKEDATE(most_expensive_year, cheapest_month)

┌─round(avg(price))─┐
│        	499902  │
└───────────────────┘

1 row in set. Elapsed: 0.173 sec. Processed 85.49 million rows, 409.36 MB (493.15 million rows/s., 2.36 GB/s.)
Peak memory usage: 264.63 MiB
```

### STR_TO_DATE

When using calculated columns that convert strings and dates, QuickSight issues queries with MySQL's [STR_TO_DATE function](https://dev.mysql.com/doc/refman/8.0/en/date-and-time-functions.html#function_str-to-date). This function’s equivalent in ClickHouse parseDateTime was added in 23.3 and allows users to specify a date pattern when parsing a string. While an alias [has been added](https://github.com/ClickHouse/ClickHouse/issues/43755) for STR_TO_DATE, users should note the ClickHouse implementation does [differ a little](https://github.com/ClickHouse/ClickHouse/issues/43755#issuecomment-1482894628). As an example, consider the modified statement below for loading the UK price-paid dataset (the [original documented](https://clickhouse.com/docs/en/getting-started/example-datasets/uk-price-paid#preprocess-import-data) insert uses [parseDateTimeBestEffortUS](https://clickhouse.com/docs/en/sql-reference/functions/type-conversion-functions#parsedatetimebesteffortus)).

```sql
INSERT INTO uk_price_paid
WITH
  splitByChar(' ', postcode) AS p
SELECT
   toUInt32(price_string) AS price,
   STR_TO_DATE(time, '%Y-%m-%d 00:00') AS date,
   --parseDateTimeBestEffortUS(time) AS date,
   p[1] AS postcode1,
   p[2] AS postcode2,
   transform(a, ['T', 'S', 'D', 'F', 'O'], ['terraced', 'semi-detached', 'detached', 'flat', 'other']) AS type,
   b = 'Y' AS is_new,
   transform(c, ['F', 'L', 'U'], ['freehold', 'leasehold', 'unknown']) AS duration, addr1, addr2, street, locality, town, district, county
FROM url('http://prod.publicdata.landregistry.gov.uk.s3-website-eu-west-1.amazonaws.com/pp-complete.csv', 'CSV', 'uuid_string String, price_string String, time String, postcode String, a String, b String, c String, addr1 String, addr2 String, street String, locality String, town String, district String, county String, d String, e String'
) SETTINGS max_http_get_redirects=10;
```

### String functions - REGEXP & INSTR(str,substr)

The MySQL [REGEXP function](https://dev.mysql.com/doc/refman/8.0/en/regexp.html), required by Looker Studio, provides string matching capabilities with regular expressions. This is comparable to the existing match operator in ClickHouse, with some [key differences](https://github.com/ClickHouse/ClickHouse/issues/47530#issuecomment-1478462064) - principally ClickHouse uses the [re2 library](https://github.com/google/re2/wiki/Syntax) instead of [MySQL’s ICU](https://dev.mysql.com/doc/refman/8.0/en/regexp.html#regexp-syntax), which results in differences in syntax support. 

The INSTR function provides the ability to return the index of the first occurrence of substring. Implementing this in ClickHouse required a [simple alias to the equivalent positionCaseInsensitive function](https://github.com/ClickHouse/ClickHouse/pull/47535).

For an example of these functions, consider the following, which computes the most popular lane names in the UK.

```sql
SELECT
  substring(street, 1, INSTR(street, 'LANE') - 2) AS lane,
  count(*) AS c
FROM uk_price_paid
WHERE street REGEXP '.*\\sLANE'
GROUP BY lane
ORDER BY c DESC
LIMIT 10

┌─lane───┬─────c─┐
│ CHURCH │ 35470 │
│ GREEN  │ 30077 │
│ MILL   │ 25847 │
│ SCHOOL │ 17642 │
│ PARK   │ 17099 │
│ CHAPEL │ 12407 │
│ SANDY  │ 10857 │
│ LONG   │  8888 │
│ BACK   │  8820 │
│ WOOD   │  7979 │
└────────┴───────┘

10 rows in set. Elapsed: 0.086 sec.
```

### TO_DAYS

When converting DateTime columns, during the table column types introspection stage, the [TO_DAYS function is required](https://github.com/ClickHouse/ClickHouse/issues/54277). This required the addition of the function [toDaysSinceYearZero](https://github.com/ClickHouse/ClickHouse/pull/54479/files) to ClickHouse and the alias for TO_DAYS. This function provides the number of days for a date since year 0.

Below we use this query to compute the fastest district to increase its price by 10% from the start of the century.

```sql
SELECT
	district,
	start_price,
	avg_price AS final_price,
	TO_DAYS(final_month::Date) - TO_DAYS(buy_date::Date) AS days_taken
FROM
(
	SELECT
    	CAST('2000-01-01', 'Date') AS buy_date,
    	district,
    	round(avg(price)) AS start_price
	FROM uk_price_paid
	WHERE toStartOfMonth(date) = buy_date
	GROUP BY district
) AS start_price
INNER JOIN
(
	SELECT
    	district,
    	toStartOfMonth(date) AS final_month,
    	round(avg(price)) AS avg_price
	FROM uk_price_paid
	WHERE toYear(date) >= 2000
	GROUP BY
    	district,
    	final_month
	ORDER BY
    	district ASC,
    	final_month ASC
) AS over_time ON over_time.district = start_price.district
WHERE (avg_price * 0.1) >= start_price
ORDER BY days_taken ASC
LIMIT 1 BY district
LIMIT 10

┌─district──────────────────┬─start_price─┬─final_price─┬─days_taken─┐
│ SOMERSET WEST AND TAUNTON │  	133667    │ 	1350000 │    	305  │
│ SOMERSET              	│   56500     │  	685000  │   	1796 │
│ CITY OF LONDON        	│  	245099    │ 	7811526 │   	5053 │
│ HILLINGDON            	│  	125364    │ 	1401759 │   	5083 │
│ BASILDON              	│   97028     │ 	1840461 │   	5114 │
│ BUCKINGHAMSHIRE       	│  	201000    │ 	2346333 │   	5234 │
│ TRAFFORD              	│  	100800    │ 	1024667 │   	5265 │
│ MANCHESTER            	│   55875     │  	579583  │   	5479 │
│ IPSWICH               	│   62656     │  	876525  │   	5538 │
│ RUSHMOOR              	│  	109029    │ 	1285046 │   	5569 │
└───────────────────────────┴─────────────┴─────────────┴────────────┘

10 rows in set. Elapsed: 0.127 sec. Processed 28.50 million rows, 227.79 MB (223.69 million rows/s., 1.79 GB/s.)
Peak memory usage: 53.59 MiB.
```

### DATE_FORMAT

Converting dates to formatted strings represents a common requirement in analytical queries. While ClickHouse supports this through the [formatDateTime](https://clickhouse.com/docs/en/sql-reference/functions/date-time-functions#formatDateTime) function, MySQL syntax exposes a DATE_FORMAT function used by Looker Studio. As well as requiring a simple alias, MySQL supported additional format substitutions ("a", "b", "c", "h", "i", "k", "l" "r", "s", "W"). By ensuring [these are supported for the DATE_FORMAT function](https://github.com/ClickHouse/ClickHouse/issues/46184), ClickHouse users of the [formatDateTime](https://clickhouse.com/docs/en/sql-reference/functions/date-time-functions#formatDateTime) also benefit. In the example below, we compute the most popular day of the week to purchase a house for each month of the year. Note how we also reuse the earlier described STR_TO_DATE, which benefits from the same substitution improvements.

```sql
SELECT
    DATE_FORMAT(date, '%b') AS month,
    DATE_FORMAT(date, '%W') AS day
FROM uk_price_paid
GROUP BY
    month,
    day
ORDER BY
    STR_TO_DATE(month, '%b') ASC,
    count() DESC
LIMIT 1 BY month

┌─month─┬─day────┐
│ Jan   │ Friday │
│ Feb   │ Friday │
│ Mar   │ Friday │
│ Apr   │ Friday │
│ May   │ Friday │
│ Jun   │ Friday │
│ Jul   │ Friday │
│ Aug   │ Friday │
│ Sep   │ Friday │
│ Oct   │ Friday │
│ Nov   │ Friday │
│ Dec   │ Friday │
└───────┴────────┘

12 rows in set. Elapsed: 0.205 sec. Processed 28.57 million rows, 57.14 MB (139.69 million rows/s., 279.37 MB/s.)
Peak memory usage: 1.31 MiB.
```

This is only a sample of the many MySQL functions added as part of our compatibility effort. Some other examples include:

* The [MySQL STD function](https://dev.mysql.com/doc/refman/8.0/en/aggregate-functions.html#function_std) now maps to the [stddevPop](https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/stddevpop) function [through an alias](https://github.com/ClickHouse/ClickHouse/pull/54382/files) in ClickHouse.
* Support for [parsing fractional seconds ](https://github.com/ClickHouse/ClickHouse/pull/48420)fractional seconds `%f` in DateTime strings.

### Something a little bigger…prepared statements!

The above represents mostly simple additions and function aliasing. One of the heavier lifts to move us towards better compatibility was Prepared Statements, required for Tableau Online.

Serge from our integrations team decided to roll up his sleeves and make his first contributions to ClickHouse, and with the guidance of Robert Schulze in our core team, spent days reading MySQL server sources, Go, Java, and Rust client drivers (the official protocol docs were not clear enough at times). After several rounds of review, he arrived [at a first pass](https://github.com/ClickHouse/ClickHouse/pull/54115). 

Prepared statement support represented one of the best examples of "blockers” in testing, which resulted in a linear approach to development. Without implementing this feature, it was not even possible to connect to Tableau online to identify other possible incompatibilities.

> We would also like to recognize the efforts of [Mark from PX](https://www.linkedin.com/in/mark-van-heyningen/), who helped a lot with testing and provided invaluable guidance.

Our initial implementation of prepared statements represents a first pass and is not 100% complete. Tableau Online uses prepared statements without arguments, hardcoding all the values in the query instead of using question marks; while this choice of implementation is unusual, it did allow us to initially skip argument support. Currently, prepared statements are not parsed. The associated query is simply stored internally with a specific ID during the COM_STMT_PREPARE phase and executed on receiving a COM_STMT_EXECUTE command. The COM_STMT_CLOSE command initiates a cleanup.

However, the main challenge was not the missing commands support - it was the fact that unlike COM_QUERY, which handles most of the "regular" queries in MySQL interface, COM_STMT_EXECUTE uses binary protocol instead of text for responses, and it is significantly more complex than its text counterpart and way less forgiving in terms of implementation (in)accuracy.

## Not quite there

While the syntax improvements above enabled OSS ClickHouse users to use the MySQL protocol with their favorite tool, further work was required in order to empower our Cloud users. The native interface of ClickHouse instances in ClickHouse Cloud are not exposed publicly to the internet. This would require every Cloud instance to have its own public IP address - infeasible as our user base grows. Furthermore, there are required networking interface features for which ClickHouse doesn't (and may never will) support e.g. load balancing of connections across a cluster. For these reasons, all communication is routed through our proxy layer powered by Istio.

To fully support MySQL in our Istio Proxy, we also had some challenges. Once connected, the server must send the first packet and then upgrade the connection to TLS. We changed our Istio Proxy to make it able to coordinate such TLS upgrade processes. Additionally, many MySQL clients do not send [SNI information](https://knowledge.digicert.com/quovadis/ssl-certificates/ssl-general-topics/what-is-sni-server-name-indication.html#:~:text=Server%20Name%20Indication%20(SNI)%20is,IP%20address%20and%20port%20number.) in the TLS handshake, which is needed to make routing decisions. To address this, we create dedicated database users in the format `mysql4<subdomain>`, where the username’s suffix is the service domain prefix. The Proxy can then extract this as part of the handshake, where the username is available, and propagate it further to decide which ClickHouse instances to route to.

## More choices and possibilities

Given the above improvements, new users to ClickHouse may be tempted to simply write queries with the MySQL SQL, which they are familiar with. While this is supported and offers a simple migration path for moving applications, we still recommend users rewrite queries in ClickHouse native syntax where resources and time permits. There are two main motivations for this. 

Firstly, ClickHouse's analytical functions often allow queries to be written much simpler.

Consider the following construct: we need to find the value for a column, given the max value of another column which is not in a GROUP BY. More concretely, for the house price dataset, suppose we wish to find the year in which the most expensive house was sold for each district in London.

In MySQL syntax, this might be written as follows:

```sql
SELECT
	uk.district,
	ukp.date AS most_expensive_year
FROM uk_price_paid AS ukp
INNER JOIN
(
	SELECT
    	district,
    	MAX(price) AS max_price
	FROM uk_price_paid
	WHERE town = 'LONDON'
	GROUP BY district
) AS uk ON (ukp.district = uk.district) AND (ukp.price = uk.max_price)
WHERE town = 'LONDON'
ORDER BY uk.district ASC
LIMIT 10

┌─uk.district──────────┬─most_expensive_year─┐
│ BARKING AND DAGENHAM │      	2016-12-14   │
│ BARNET           	   │      	2017-10-31   │
│ BEXLEY           	   │      	2014-07-17   │
│ BRENT            	   │      	2022-03-25   │
│ BROMLEY          	   │      	2019-08-09   │
│ CAMDEN           	   │      	2022-04-22   │
│ CITY OF BRISTOL  	   │      	2020-01-06   │
│ CITY OF LONDON   	   │      	2019-04-04   │
│ CITY OF WESTMINSTER  │      	2017-07-31   │
│ CROYDON          	   │      	2021-03-29   │
└──────────────────────┴─────────────────────┘

10 rows in set. Elapsed: 0.098 sec. Processed 56.99 million rows, 275.41 MB (580.03 million rows/s., 2.80 GB/s.)
Peak memory usage: 871.14 MiB.
```

In ClickHouse, the `argMax` column simplifies this significantly avoiding our INNER JOIN:

```sql
SELECT
	district,
	CAST(argMax(date, price), 'Date') AS most_expensive_year
FROM uk_price_paid
WHERE town = 'LONDON'
GROUP BY district
ORDER BY district ASC
LIMIT 10

┌─district─────────────┬─most_expensive_year─┐
│ BARKING AND DAGENHAM │      	2016-12-14   │
│ BARNET           	   │      	2017-10-31   │
│ BEXLEY           	   │      	2014-07-17   │
│ BRENT            	   │      	2022-03-25   │
│ BROMLEY          	   │      	2019-08-09   │
│ CAMDEN           	   │      	2022-04-22   │
│ CITY OF BRISTOL  	   │      	2020-01-06   │
│ CITY OF LONDON   	   │      	2019-04-04   │
│ CITY OF WESTMINSTER  │        2017-07-31   │
│ CROYDON              │        2021-03-29   │
└──────────────────────┴─────────────────────┘

10 rows in set. Elapsed: 0.047 sec. Processed 28.50 million rows, 53.30 MB (603.85 million rows/s., 1.13 GB/s.)
Peak memory usage: 420.94 MiB.
```

As well as making analytical queries such as this simpler to write, these functions also generally allow ClickHouse to execute queries more efficiently, as shown by the execution times and memory times.

There are cases where users will have a choice. Either use a native ClickHouse integration for a tool or simply revert to the MySQL interface and the tool's existing driver. In most cases, we would recommend users utilize the former where possible for the same reasons as outlined for writing queries - native integrations will typically write more efficient queries for ClickHouse. 

For example, consider Tableau. Since Tableau online offers no ability to contribute a driver without a lengthy engagement with the vendor, connecting to MySQL represented the best path to unlocking our users. Conversely, the more traditional Tableau desktop allows users to use a custom driver. We therefore maintain a ClickHouse driver, which ensures more optimal ClickHouse syntax is used.

If in doubt, please feel free to ask and reach out to our support organization or [via our public Slack channel](http://clickhouse.com/slack).

## Shoutouts

This effort required significant collaboration with both our integrations and core teams, as well as the wider ClickHouse community. We would like to recognize all of the following for contributing and making this possible.

[@JakeBamrah](https://github.com/JakeBamrah) [@ucasfl](https://github.com/ucasfl) [@rschu1ze](https://github.com/ClickHouse/ClickHouse/pull/48017) [@slvrtrn](https://github.com/slvrtrn) [@yariks5s](https://github.com/yariks5s) [@vdimir](https://github.com/vdimir) [@evillique ](https://github.com/evillique) [@tpanetti](https://github.com/tpanetti)

## Conclusion

In this blog post, we have explored the changes that were required in order to support the MySQL syntax sufficiently to allow our users to use BI tools such as Looker and Tableau online with ClickHouse. As well as covering improvements in our Cloud proxy, we have also provided some general guidance on when to use this syntax support for users looking to migrate workloads from MySQL. For readers more interested in Looker studio, our [recent announcement blog post](https://clickhouse.com/blog/clickhouse-cloud-compatible-with-mysql) provides further details.
