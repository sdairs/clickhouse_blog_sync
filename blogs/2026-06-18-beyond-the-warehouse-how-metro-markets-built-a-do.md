---
title: "Beyond the warehouse: How METRO Markets built a do-it-all data platform on ClickHouse Cloud"
date: "2026-06-18T20:31:40.804Z"
author: "ClickHouse"
category: "User stories"
excerpt: "How METRO Markets replaced a failing Hadoop-based stack with ClickHouse Cloud to build a single platform now powering data warehousing, real-time seller analytics, credit risk modeling, observability, and AI across the whole company."
---

# Beyond the warehouse: How METRO Markets built a do-it-all data platform on ClickHouse Cloud

## Summary

- METRO Markets uses ClickHouse Cloud to power data warehousing, real-time seller analytics, credit risk modeling, observability, new AI use cases, and more.
- After outgrowing a self-hosted Hadoop-based stack, METRO Markets consolidated all company data into a single warehouse for the first time in its history.
- METRO Markets observed substantially faster query performance and lower storage costs compared to BigQuery and Snowflake, and adoption spread faster than anyone anticipated.

Across Europe, the big blue-and-yellow [METRO](https://www.metroag.de/en) wholesale stores are a familiar sight. For six decades, the cash-and-carry warehouses have supplied the continent's restaurants, hotels, and caterers, spanning over 600 locations across more than 20 countries, and cementing METRO's place as one of the largest retailers in the world.

But in 2018, a team inside the company looked at the B2B commerce landscape and saw a gap. Even a company of METRO's scale could only offer its customers a fraction of what they needed to run their businesses. An online marketplace, purpose-built for the hospitality industry, promised a far wider selection than any physical store could ever stock.

[METRO Markets](https://metro-markets.de/) launched in Germany in September 2019 and today operates across six European countries, with over a million products available to the hotels, restaurants, and catering businesses that form its customer base. Behind the scenes, a lean data team powers the intelligence that keeps the platform running, from seller analytics and credit risk scoring to behavioral data and operational logging, all of it flowing through [ClickHouse Cloud](https://clickhouse.com/cloud).

We caught up with the METRO Markets team to find out how their search for a better data warehouse led to something far more valuable and ambitious: a single platform that gives every team in the company a shared view of reality, in real time.

## Growing pains in the data layer

When Luis Jurado joined in 2020 as Data Engineering Team Lead, he arrived into a company growing faster than its infrastructure. Their self-hosted data stack was built on Impala and Kudu, tools from the Hadoop ecosystem that made sense at a certain scale but were showing their limits. "It grew out of hand as the company grew," he says. "There were a lot of in-house maintenance issues, and it wasn't easy to scale."

As the business scaled, data reliability became a growing concern. Engineering teams built parallel data stores to keep pace with demand, but business reporting remained dependent on Impala, which increasingly struggled to meet the reliability and consistency expectations of growing METRO Markets. "We had different teams looking at different numbers," says Hakan Dilaver, Head of Engineering Operations and Security. For a company making real-time decisions about pricing, logistics, and credit, that misalignment came with real costs.

There was a human cost, too. Despite the company's growth, the data team hadn't grown as fast as other parts of the business. Markus Nutz, Data Engineering and Science Lead, describes talented people spending too much time checking whether something had broken overnight rather than doing work that actually moved the needle. They needed something to make everyone's lives easier… or as Markus puts it, "something that just works."

## The road less traveled

When they began looking at alternatives, the obvious choice was Google BigQuery. It's what the broader METRO group uses, and, as Luis says, "Choosing tooling that differs from the rest of the group always requires some extra explanation and consensus."

Even so, the team ran a proper analysis, testing BigQuery alongside Snowflake and ClickHouse against the actual queries they run in production. On queries large and small, Luis says, "ClickHouse ran faster." On one particularly demanding query, we observed a significant difference in completion time between platforms. On another query, response time dropped from four seconds to under 200 milliseconds.

But performance alone wasn't going to win the argument. "From a business standpoint, there was also a need to predict our costs," Luis says. "Cost predictability was a challenge with alternatives. While controls were available to cap spending, we found they came with performance trade offs that didn't work for our use case." ClickHouse's [pricing model](https://clickhouse.com/pricing?plan=scale&provider=aws&region=us-east-1&hours=8&storageCompressed=false), by contrast, made it possible to forecast expenditure without sacrificing query speed.

"We needed the next step in our data journey," Luis says. "We did an analysis of a few tools, tested some of them, and landed on ClickHouse."

## Building the foundation

In the current architecture, Airbyte handles the majority of data movement, pulling from MySQL and Postgres sources via CDC connectors and writing into ClickHouse, though the team plans to test ClickHouse's native ingestion engine, [ClickPipes](https://clickhouse.com/cloud/clickpipes), once GCP support is available. For deduplication during background merges, they use ClickHouse's [ReplacingMergeTree engine](https://clickhouse.com/docs/engines/table-engines/mergetree-family/replacingmergetree) with an experimental cleanup feature. "We look forward to using ClickPipes when it is available for us on GCP to further simplify this infrastructure," Markus says.

One particular challenge was Google Analytics data, which lives in BigQuery and couldn't be moved through standard connectors. The team solved it by dumping the data into cloud storage buckets and loading it into ClickHouse via external tables. Markus calls it a "big step forward," adding, "We now finally have all our company data in one data warehouse."

On the consumption side, Luis says ClickHouse's broad compatibility has been as important as its ingestion capabilities. "When we were on Impala, the only drivers available were ODBC or JDBC," he explains. "Our services are mostly written in PHP. We couldn't use Grafana or Looker Studio." ClickHouse's MySQL-protocol endpoint changed that, allowing developers and business analysts to query the same data through whatever tool they prefer.

## One data platform, many stories

When METRO Markets adopted ClickHouse, nobody anticipated how quickly it would expand beyond its original mandate. What began as a data warehousing project has become a single, scalable platform spanning storage, analytics, machine learning, and observability.

Today, ClickHouse serves as the company's central [data warehouse](https://clickhouse.com/resources/engineering/choosing-cloud-data-warehouse), consolidating transactional data, behavioral data, and MongoDB collections in one place. "That's something we hadn't managed since METRO Markets started," Markus says.

Built atop that foundation is a growing layer of [real-time analytics](https://clickhouse.com/resources/engineering/what-is-real-time-analytics). Merchants who sell on the platform can see, in near real time, whether they're delivering on time, how competitive their pricing is, and how their products are performing. Because it directly affects how sellers run their businesses, the data needs to be fast and available. ClickHouse handles both.

ClickHouse's [Query API endpoints feature](https://clickhouse.com/docs/cloud/get-started/query-endpoints) (which Markus calls a "nice surprise… the documentation sells it a little bit short") have become central to several of these use cases. The team uses them to surface user characteristics like VIP status and account flags to downstream systems instantly. They also power a lightweight [feature store](https://clickhouse.com/blog/powering-featurestores-with-clickhouse) for the company's credit risk model. For every transaction, user features are fetched from ClickHouse and a prediction is generated end to end, without any intermediary systems. "If you think about how you'd normally build a feature store — the infrastructure, the ingestion pipelines — it was a bit of a gamble," Markus says. "But we took the bet, and it's working very well."

Teams are also starting to use ClickHouse for [observability](https://clickhouse.com/resources/engineering/observability). Engineers across the company use it to store and interrogate operational logs, particularly API logs from the seller-facing platform, where being able to run ad hoc counts and rate-limit queries without building a separate metrics layer saves significant time. "With ClickHouse, you can just go and query it," Luis says. "That would be really difficult with standard logs." Hakan adds that the team is exploring moving one of their largest log partitions from Datadog into ClickHouse.

And then there's AI, the use case nobody planned for. Several internal teams are exploring LLM-powered tools to help customer-facing staff look up order information and resolve issues faster. The path of least resistance to the relevant data almost always leads to ClickHouse. It's an example of something [ClickHouse is seeing accelerate across the industry](https://clickhouse.com/blog/ai-redrawing-database-market): as AI agents become the primary interface to data, the database underneath them needs to be fast, concurrent, and always on.

## Cheaper, faster, more reliable

ClickHouse's impact shows up first in storage, which, as Luis explains, leads directly to costs. "When I talk to Hakan, I always say things like, 'this terabyte of data in MySQL costs X amount of dollars to store, but move it to ClickHouse and now it's 100 megabytes, which is also cheaper to store per gigabyte,'" he says. "So it's a clear win."

The decision to go with a managed solution has also proven important. Having lived through the operational burden of running Impala and Kudu themselves, the team made a deliberate choice to let [ClickHouse Cloud](https://clickhouse.com/cloud) handle the infrastructure. As Luis puts it, "We found the pain of self-hosting in our previous solution and didn't want to take that risk again."

"The biggest benefit for me," Markus says, "is having all the data available and being able to query it fast." Benchmark testing against our production queries indicated that ClickHouse was better suited to our particular use case and query patterns.

Hakan agrees: "The most important part was being able to centralize our data operations in a solution that's fast and reliable." That reliability has resolved the misalignment that once plagued the company. Instead of different teams looking at different data sources and getting different versions of the truth, business and engineering draw from the same warehouse, through the tool of their choosing, and the platform stays up.

## The journey continues

Across METRO Markets, teams the data platform never even targeted have found reasons to build on ClickHouse. "The benefits and the number of things we've ended up using it for, because of the feature set, has been more than we anticipated," Luis says.

The journey, he adds, is far from over. "We want to incorporate a lot more things in the future," he says. Next on the roadmap is connecting their Kafka and Flink streaming infrastructure to ClickHouse, opening the door to real-time stream processing use cases that will take the platform further still.

With ClickHouse, what was initially scoped as a data warehousing project has become, quietly and organically, the do-it-all data infrastructure for the whole company.

---

## Get started today

Interested in seeing how ClickHouse works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-963-get-started-today-sign-up&utm_blogctaid=963)

---