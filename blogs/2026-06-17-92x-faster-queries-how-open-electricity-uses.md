---
title: "92x faster queries: How Open Electricity uses ClickHouse to track Australia’s energy transition in real time"
date: "2026-06-17T12:06:29.853Z"
author: "ClickHouse"
category: "User stories"
excerpt: "Open Electricity migrated ~1 billion rows of Australian energy data from Postgres and TimescaleDB to ClickHouse, achieving 92x faster queries on a fraction of the hardware."
---

# 92x faster queries: How Open Electricity uses ClickHouse to track Australia’s energy transition in real time

## Summary

* Open Electricity uses ClickHouse to power an open platform and public API serving live Australian energy data across \~1 billion records.  
* Migrating from Postgres and TimescaleDB to ClickHouse delivered a 92x query speed improvement, with a benchmark query dropping from over 5 minutes to just over 3 seconds—and 60 milliseconds via materialized view.  
* ClickHouse runs on significantly less hardware: 4 cores, 4GB RAM, and 200GB disk versus Postgres’s 16 cores, 32GB RAM, and 1.6TB, at a fraction of the cost.

Something remarkable is happening to Australia's electricity grid. In the midst of a massive transformation, it has become one of the most closely watched energy systems on the planet.

"Twenty years ago, the grid was pretty boring," says Nik Cubrilovic, a developer at [Open Electricity](https://openelectricity.org.au/), an open platform tracking Australia's electricity transition. Back then, the country had a hundred-odd generators—coal-fired power stations, the Snowy scheme, a handful of gas plants. "You might add or retire a facility each year," Nik says.

In 2025 alone, Australia registered 40 new facilities. And the grid isn't just growing. "The composition of the grid is also changing," Nik says, highlighting that more than half of those new facilities are battery storage. "The capacity of the coal-fired power stations is decreasing, whereas batteries, solar power, and wind have really taken off."

![](https://clickhouse.com/uploads/openelectricity_jun2026_image1_a384eadde2.png)

*Australia's electricity generation capacity by fuel type since 1999. Coal (black and brown) has declined, while batteries (dark blue), solar (yellow), and wind (green) have surged in recent years.*

"This is what makes our grid interesting, not just in Australia but globally," Nik says. "There are a lot of regulators and researchers all around the world who are interested in Australia's energy data to see how we're adapting with some of the challenges that come out of it."

At a [February 2026 ClickHouse meetup in Melbourne](https://clickhouse.com/videos/202602-melbourne-meetup-openelectricity), Nik shared how Open Electricity is making that data accessible, what led them to migrate over a billion rows to ClickHouse, and why he believes ClickHouse plus Postgres is a "magical pairing."

## A billion rows and counting

Open Electricity pulls its data from two grids: the NEM, or National Electricity Market, covering the eastern states from Tasmania to north Queensland, and the WEM, the Wholesale Electricity Market in Western Australia. Every five minutes, each generating unit reports how much power it produced, and the regulator publishes that data in what Nik describes as "really awkward CSV files" that Open Electricity must then parse and enrich.

The grid, Nik explains, has a hierarchy. Each network is made up of facilities, each facility is made up of units, and each unit has its own fuel technology. "A coal-fired power station might have four different units," he says. "A wind farm might have 30 different wind generators."

The data breaks down into three types: market data (price, demand, generation, and forecasts per region), generation data recorded per unit per interval going back to 1999, and curated facility data built by Open Electricity on top of the raw four-digit regulator codes, covering over 100 fields per facility. Altogether that adds up to around 1 billion records, with the platform adding another 500,000 each day.

The scale is easy to see when you start digging into charts on the Open Electricity [website](https://openelectricity.org.au/). The default 7-day view draws on over 32,000 data points—12 five-minute intervals per hour, 24 hours a day, seven days, across 16 fuel technology groups. The all-time view, stretching back to 1999, requires aggregating around 45 million data points out of that billion-row table, which users can slice by region, fuel type, or renewables versus non-renewables. All of it is served live through a public API used by around 300 companies and institutions.

![](https://clickhouse.com/uploads/openelectricity_jun2026_image3_238c75f05e.png)

*Open Electricity's default view, showing seven days of generation by fuel technology type.*

![](https://clickhouse.com/uploads/openelectricity_jun2026_image2_e5175d3c0f.png)

*The all-time view, aggregated from billions of 5-minute data points stretching back to 1999.*

For Nik, who has worked across finance, crypto, and everywhere in between, nothing matches energy data for its intensity and complexity. "Electricity networks are extremely complex, and there is intricacy in parsing the data to tell its story."

That complexity doesn't go away just because you've put it in a database. For a small team serving live data to hundreds of institutions around the world, every five minutes of every day, getting the infrastructure right matters enormously.

## From TimescaleDB to ClickHouse

For years, Open Electricity ran on a combination of Postgres and TimescaleDB. But with a billion rows and counting, the setup was starting to strain, with some queries taking upwards of five minutes to complete. The worst offenders were joins between market data and generation data. As Nik says, "Doing a join based on an interval and then going back through a billion rows gets pretty expensive pretty quickly."

TimescaleDB did offer some relief. Its time-series functions, particularly time_bucket and time_bucket_gapfill, were useful for a dataset full of gaps, since generators don't run continuously, and filling nulls before joining the data was a constant requirement.

But it also had serious limitations. Continuous aggregates didn't support time_bucket_gapfill, and there was no timezone handling in materialized views—a problem given that, as Nik explains, "We're dealing with east coast time zones and summing it up with west coast time zones and having to show an Australia-wide view on top of that." Queries on continuous aggregates were still slow, and refreshing materialized views locked tables. The team ended up selecting out of large queries and writing results into separate tables manually.

Materialization was the right instinct. What they needed was a purpose-built OLAP engine. "I've been using ClickHouse for longer than ClickHouse has been a company," Nik says. "It's a column store. The compression is great. It's a lot easier to query… if you know SQL, you can pretty quickly pick up some of the custom ClickHouse functions."

It also offered [multiple engine types](https://clickhouse.com/docs/engines/table-engines) for different aggregation patterns, [clear performance benefits](https://clickhouse.com/docs/concepts/why-clickhouse-is-so-fast), and [materialized views](https://clickhouse.com/docs/materialized-views) that Nik and the team have put to full use. "We've got so many different ways of representing energy data that it's very cheap with ClickHouse to create materialized views once you've got your base tables," he says. "We run over 20 of them now, and we keep adding more and more all the time. If we see a hot spot with a query, we just create a new materialized view for it and then point the query to that."

## A new architecture that's 92x faster

With ClickHouse added to the stack, Open Electricity's architecture snapped into a clean division of labor that Nik calls "the best of both worlds—we've got the heavy relational data still in Postgres, but all the analytic workloads are happening on ClickHouse now. There aren't many workloads that you can throw at it where it's just not going to chew through it."

At the core of the ClickHouse setup are two tables: unit_intervals, which stores per-unit 5-minute generation, emissions, and market value data; and market_summary, which holds per-region price and demand. Both use [ReplacingMergeTree](https://clickhouse.com/docs/engines/table-engines/mergetree-family/replacingmergetree), one of ClickHouse's specialized engine types designed for deduplication. "ClickHouse's [documentation](https://clickhouse.com/docs/) and the [GitHub community](https://github.com/ClickHouse/ClickHouse/discussions) around ClickHouse are fantastic," Nik says. "You can learn all about the different engine types and when to apply each one."

On top of those two base tables sits a hierarchy of materialized views, each tuned to its aggregation pattern. "The queries are very fast," Nik says. "Some of those Postgres queries that were taking on the order of minutes are now returning in milliseconds."

To benchmark performance properly, the team ran the same query on both systems, aggregating all-time energy by fuel technology, grouped by month, going back to 1999. Postgres took 313 seconds. ClickHouse took 3.4 seconds. "So it's about 92 times faster," Nik says. "And it gets even better," he adds, noting that with the monthly materialized view, the same query comes back in just 60 milliseconds.

Nik is quick to point out that the benchmark isn't a hardware-for-hardware comparison. Postgres runs on 16 cores, 32 GB of RAM, and 1.6 TB of disk. ClickHouse runs on 4 cores, 4 GB of RAM, and 200 GB—a fraction of the hardware, at a fraction of the cost.

## Lessons learned from the migration

Nik and the team opted for a gradual migration, running the old and new systems in parallel and moving traffic over bit by bit. Feature flags let them toggle between the two systems per endpoint, with identical API output so users never knew which database they were hitting. They could bucket a percentage of users into one or the other, compare results, and flip the switch further when confident.

"ClickHouse is so cheap to run that you can run it in parallel for as long as you need to perfect it," Nik says. "There's no reason you can't go to the office, load up a ClickHouse schema, and start running it alongside your existing workloads and flick it over bit by bit."

While they're happy with where they landed, they had to overcome a few "gotchas." The first was what Nik calls the "FINAL trap." ClickHouse's ReplacingMergeTree engine doesn't deduplicate at query time unless you explicitly add [FINAL](https://clickhouse.com/docs/sql-reference/statements/select/from#final-modifier) to your query. "It's important to understand how ClickHouse is architected," Nik says. Otherwise you can "wake up one morning and all your data is doubled."

The second was a bit subtler. Combining auto-populating materialized views with ReplacingMergeTree can lead to, as Nik puts it, a "disaster," with partial daily aggregates winning the "max version lottery" over complete ones. The team came up with a clever hack: encode data completeness directly into the version number, so a full-day backfill with 288 intervals always outranks a partial auto-populated aggregate with 10.

Timezones caused headaches, too. With east and west coast data flowing through a Python backend, multiple drivers, and a JavaScript frontend, there are around 20 places in the pipeline where dates are touched. "If you alternate between non-timezone and timezone fields, it's going to get mangled," Nik says. He recommends standardizing [DateTime64](https://clickhouse.com/docs/sql-reference/data-types/datetime64) with UTC from day one.

Other gotchas included memory management during backfills (ClickHouse favors [bulk inserts](https://clickhouse.com/docs/optimize/bulk-inserts), and the team found that chunking data into 3-day windows with 20,000-record batches was the most efficient approach) and disk space, where "out of memory" errors often turned out to be ClickHouse running out of temporary disk space for large operations. Nik also recommends matching timeouts to the type of operation, with user-facing queries timing out in seconds and longer-running backfill and optimization tasks given much more room to breathe.

"Each one of these touchpoints I could go on for days about—there's a lot of learned experience in our codebase," he says with a smile.

## ClickHouse + Postgres = "A magical pairing"

Open Electricity's move to ClickHouse has enabled the team to query data in ways that weren't practical before—live, at scale, across a billion rows, in milliseconds.

Nik closed his presentation with two demos that show that speed and flexibility in action: a real-time status page for every coal-fired generator in Australia, displaying capacity and output at every 5-minute interval; and a solar generation heatmap built that same day by a frontend developer, tracking hour-by-hour solar output from 2016 to 2025. "We're talking millisecond-scale queries now," Nik says.

"Postgres combined with ClickHouse is a magical pairing," he continues. "You've got Postgres for all your relational workloads and ClickHouse for all your analytical workloads. It's been working really well for us, allowing us to query data in ways we couldn't before."

For a small nonprofit tracking one of the world's most closely watched energy transitions, that pairing is what lets researchers, journalists, and policymakers see what's happening to Australia's grid in real time, and share that picture with the rest of the world.


---

## Get started today

Interested in seeing how ClickHouse works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-897-get-started-today-sign-up&utm_blogctaid=897)

---