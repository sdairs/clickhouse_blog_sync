---
title: "How SewerAI is using ClickHouse to modernize sewer management at scale"
date: "2025-09-19T10:13:47.114Z"
author: "ClickHouse Team"
category: "User stories"
excerpt: "“Our compute usage remained stable. We didn’t have any more failing updates. Because of that, we didn’t have backlogs. Our analytics were up to date, and our customers were happy.”"
---

# How SewerAI is using ClickHouse to modernize sewer management at scale

Sewer management is a dirty job. From crawling through sludge-filled pipes to squinting at endless hours of inspection footage looking for cracks and corrosion, it’s a tough, thankless task that most people are happy to hand off to the fine folks at [SewerAI](https://www.sewerai.com/).

SewerAI is building the industry’s first web-based platform for underground infrastructure management. Created by sewer assessment professionals, it uses computer vision to automate defect detection, streamlines collaboration across inspection teams, and provides cloud-based tools to store, analyze, and act on inspection data. 

ClickHouse powers the real-time analytics layer within the platform, allowing cities to pull insights from billions of rows of inspection data in seconds. “We've been using ClickHouse for almost as long as the company has existed,” Sabrina says. “We have a lot of features based on it, and a lot of lessons learned along the way.”

At a [May 2025 ClickHouse meetup in Austin](https://clickhouse.com/videos/cWF8HgOCYZc), Sabrina shared one of those lessons in detail: how the team denormalized their entire dataset into a single giant “Megatable” to deliver real-time analytics, while keeping costs under control.

## Modernizing an underserved industry

If you’ve ever walked down the street and seen workers in uniform dropping a camera down a manhole, chances are you’ve witnessed a sewer inspection in action.

“You thought your Netflix recommendations were bad,” Sabrina jokes. “Somebody has to watch those videos and go, ‘Hey, there's a crack here, there's tree roots there. Wow, there’s a lot of water—hopefully just water—in this pipe. And what are all these rats doing here?’”

Municipalities rely on that footage to decide what to fix and when. But in an industry long underserved by technology, they’re often working with outdated systems. “We’ve seen DVDs, stacks of CDs, major cities still using fax machines,” Sabrina says. And with an aging workforce nearing retirement, the next generation isn’t exactly trained to handle a fax line.

SewerAI was founded in 2019 to fix this problem. As Sabrina puts it, the company’s founders asked, “Why do humans have to watch these videos? It’s really boring, and you have to identify consistent patterns. Sounds like a perfect job for AI, right?”

That's where [ClickHouse](https://clickhouse.com/cloud) came into the picture. “We had loads and loads of data, and we wanted to use it to train AI to identify problems in video,” Sabrina says. “That's what we started using ClickHouse for, and it works great.”

But as the team began digging in, it became clear the industry needed more than smarter video review. It needed a modern data platform. The team began building a full cloud-based system for underground infrastructure management. They started with Postgres, an age-old choice for transactional workflows. But when it came to analytics, it didn’t hold up.

“Say you're a city municipal worker,” Sabrina says. “You've got a meeting in half an hour, and based on the last nine months of data that you loaded into SewerAI, you need to make a case that you need more trucks. You don't have time to run a query across nine months of data and 40-odd relational Postgres tables. You need your answers now.”

## Postgres to PeerDB to ClickPipes

The first challenge was getting all that Postgres data into ClickHouse. Their initial setup used Confluent with Debezium and Kafka streams. “This worked fine—right up until we did our SOC-2 compliance,” Sabrina says. “Then they said, ‘Nope, Confluent needs to go.’”

Plan B was to self-host Debezium and use AWS Kinesis. “I do not recommend this solution,” she says. “It does not scale well, and you will spend a lot of time debugging your Debezium server.”

Eventually, they found [PeerDB](https://www.peerdb.io/). “Basically, you hook up your Postgres, and it pulls the data out every second of every day and moves it into ClickHouse,” Sabrina says. “A perfect mirror.”

“We weren’t the only ones who thought PeerDB was really cool,” she adds, noting [ClickHouse’s acquisition of PeerDB in July 2024](https://clickhouse.com/blog/clickhouse-acquires-peerdb-to-boost-real-time-analytics-with-postgres-cdc-integration). “You know you picked the right solution when the database you’re using buys your solution.”

That acquisition paved the way for [ClickPipes](https://clickhouse.com/cloud/clickpipes), which builds on PeerDB and makes ingestion even simpler. As of May 2025, it now offers a native [Postgres CDC connector](https://clickhouse.com/cloud/clickpipes/postgres-cdc-connector) that lets teams replicate entire Postgres databases to ClickHouse Cloud in a few clicks. For anyone just starting to copy data from Postgres to ClickHouse, Sabrina says, “Start with ClickPipes.”

![0_sewerai.png](https://clickhouse.com/uploads/0_sewerai_6f2f3a5581.png)

At SewerAI, customer data flows from Postgres to ClickHouse to power fast, live analytics.

## The Megatable awakens

Getting data into ClickHouse was just the beginning. “Now our data is in ClickHouse—now what?” Sabrina asks. “Now we can use it for live analytics, right? ClickHouse is great, ClickHouse is really fast. There’s only one problem…”

The problem was that PeerDB had mirrored their Postgres schema table for table. That meant they still had to join 40-plus tables at query time. This might have worked (slowly) in Postgres, but in ClickHouse, it left too much performance on the table.

To fix it, they turned to a classic database optimization technique called [denormalization](https://clickhouse.com/docs/data-modeling/denormalization). “What we're doing is essentially avoiding joins at query time,” Sabrina explains. By duplicating data across tables, they could dramatically reduce the cost of analytical queries.

Step one was cleaning and formatting—turning nested JSON and nullable fields into structured, formatted tables. “We had a lot of default information we needed to handle,” Sabrina says. “We did this with ClickHouse’s [materialized views](https://clickhouse.com/docs/materialized-views).”

But the real breakthrough came with ClickHouse’s new [refreshable materialized views](https://clickhouse.com/docs/materialized-view/refreshable-materialized-view). “I gotta tell you, I love these,” she says. These views let the team join multiple tables, apply business logic, and continuously populate a single, denormalized table: the “Megatable.”

“As you can tell by the name, it’s quite big,” Sabrina says. With hundreds of billions of rows, the Megatable is what powers SewerAI’s live analytics. “If you’re a customer of ours, you pull up your data from the past six months, run your analytics, and boom—your query goes against the Megatable. One table, lots of duplicate information. But we don’t care, because it’s fast to query.”

![1_sewerai.png](https://clickhouse.com/uploads/1_sewerai_bec58b88c5.png)
Data flows through materialized and refreshable views into a single denormalized Megatable.

## A tsunami of data

Building the Megatable solved one problem, but it created another. “Our system is quite computationally expensive, what with all the copying and joining and inserting," Sabrina explains. “For our price tier, our compute capacity is pretty much always at limit.”

That pressure hit a breaking point any time customers performed large operations, such as uploading thousands of videos or editing inspections in bulk. “This is going to cause a tidal wave of data coming into Postgres, through your PeerDB streams, into the PeerDB tables,” Sabrina says. “And then it’s going to smash into those views and overflow the compute capacity.”

As updates failed, backlogs began to build. Meanwhile, new data kept streaming in, creating what Sabrina calls “the data equivalent of a traffic jam. You’ve got one accident, and then everybody sits in traffic for two hours waiting to get through it.” 

Analytics lagged so far behind that customers started to notice. “At that point,” she says, “you know you’ve got a problem.”

As a startup, SewerAI had to keep growing. But as Sabrina puts it, “More customers means more data. And more data means more tidal waves.” With volumes surging, the team knew that if they wanted to scale the business, they needed a more efficient way to stay afloat.

![2_sewerai.png](https://clickhouse.com/uploads/2_sewerai_e79e4dae43.png)

SewerAI’s data storage and query volume surged, leading to update failures and backlogs.

## Making the system smarter

SewerAI didn’t have the luxury of scaling up compute. Instead, they had to make the system smarter. They started with a simple question: “Why are we running queries on the entire database if we’re really only interested in the new stuff?” Sabrina says. Rather than refreshing materialized views against the full dataset, they began querying just the most recent slice, typically the last 70 seconds of data. “That did a lot for us,” she says.

From there, it was all about shaving off inefficiencies. They added [projections](https://clickhouse.com/docs/sql-reference/statements/alter/projection) to all their clean tables, which Sabrina says were “very helpful for our compute cost.” They leaned into [dictionaries](https://clickhouse.com/docs/sql-reference/dictionaries), which proved “much more efficient than LEFT ANY joins” for repeat lookups. And they discovered that even the order of join tables mattered—a “duh” moment, but one that made a huge difference.

They also restructured queries for better performance. Swapping out [DISTINCT](https://clickhouse.com/docs/sql-reference/statements/select/distinct) for [LIMIT](https://clickhouse.com/docs/sql-reference/statements/select/limit) helped reduce load. But the biggest win came from filtering early. “For the love of God, don’t be me—filter before you join,” Sabrina says. “This was like a threefold increase in speed at half the compute cost—something absolutely ridiculous.”

The results spoke for themselves. Over the past three months, data volumes tripled and read/write operations increased tenfold. And yet, compute usage held steady. “We didn’t have any more failing updates,” Sabrina says. “Because of that, we didn’t have backlogs. Therefore our analytics were up to date, and customers were happy.”

## Scaling sewer management

Looking ahead, one of the team’s top priorities is finishing their [ClickPipes](https://clickhouse.com/cloud/clickpipes) migration to streamline how data flows into ClickHouse Cloud. “This is something we’re actively working on with the very kind, responsive, and patient people at ClickHouse,” Sabrina says.

They’re also focused on scaling refreshable views and doing whatever else they can to keep costs in check. “I think this is a problem everyone can understand, unless you work for a FAANG and money isn’t a problem for you, you lucky bastards,” she adds jokingly.

SewerAI’s journey is proof that no industry is too niche—or too messy—for a modern data platform. With ClickHouse, Sabrina and the team have built a system that can handle the flood of real-time infrastructure data, stay responsive to customer needs, and keep evolving as the company scales.

Curious how ClickHouse Cloud can help you scale your data operations? [Try it free for 30 days.](https://clickhouse.com/cloud)