---
title: "🗽 Postgres Summit US 2026 retrospective"
date: "2026-10-07T17:05:28.728Z"
author: "David Wheeler"
category: "Community"
excerpt: "Highlights from Postgres Summit US 2026 in New York City, where ClickHouse sponsored the community and demonstrated its growing Postgres integrations."
---

# 🗽 Postgres Summit US 2026 retrospective

Last week a number of HouseCats attended [Postgres Summit US 2026](https://2026.postgressummit.us) in New York
City, which ClickHouse helped sponsor. I enjoyed the commute: just 20-30m on
the subway each day. My colleagues [Zoe](https://clickhouse.com/authors/zoe-steinkamp "Zoe Steinkamp"), [Amog](https://clickhouse.com/authors/amog-iska "Amog Iska"), and [Josh](https://clickhouse.com/authors/josh-ventura "Josh Ventura") flew in to staff
our booth and meet the community. We savored a couple of terrific dinners
together at [The Tyger](https://www.thetygernyc.com) and [Raku](https://www.rakunyc.com/pages/menu-east-village), organized by [Zoe](https://clickhouse.com/authors/zoe-steinkamp "Zoe Steinkamp"). So much laughing!

On the first day, Wednesday, I immediately found myself meshed into the
natural social milieu of the conference. A number of attendees approached our
booth, not just for our [yellow elephant & killer stickers](https://lnkd.in/p/gTx3j83c), or for the chance
to win a [Pikachu](https://en.wikipedia.org/wiki/Pikachu "Pikachu on Wikipedia") stuffy in a [Totoro](https://en.wikipedia.org/wiki/My_Neighbor_Totoro "My Neighbor Totoro on Wikipedia") backpack, but to find out just how we
integrate Postgres and ClickHouse.

## Postgres in da ClickHouse {#postgres-in-da-clickhouse}

Fortunately I lead an early session on this very topic, [Postgres in da ClickHouse](https://postgresql.us/events/postgressummitus2026/schedule/session/2473-postgres-in-da-clickhouse/). We invited all comers, resulting in a very nice turnout. The talk
began with some background on [ClickHouse](https://github.com/ClickHouse/ClickHouse "ClickHouse on GitHub"), the open-source analytical
database; [ClickHouse Cloud](https://clickhouse.com/cloud "ClickHouse Cloud") the platform; and how our latest product,
[ClickHouse Managed Postgres](https://clickhouse.com/cloud/postgres), slots into our vision of the default data
stack. Spoilers: seamlessly use Postgres for [OLTP](https://en.wikipedia.org/wiki/Online_transaction_processing "Wikipedia: Online transaction processing") workloads and ClickHouse
for [OLAP](https://en.wikipedia.org/wiki/Online_analytical_processing "Wikipedia: Online analytical processing - Wikipedia") workloads.

Seamlessly how? I demoed four of our technologies that smooth the integration
of Postgres and ClickHouse:

*   [pg_stat_ch](https://clickhouse.com/blog/pg_stat_ch-postgres-extension-stats-to-clickhouse "pg_stat_ch: a PostgreSQL extension that exports every metric to ClickHouse") records metrics for every Postgres query into the ClickHouse
    analytics stack for [query insights](https://clickhouse.com/blog/postgres-query-insights-clickhouse-cloud "Introducing Postgres Query Insights in ClickHouse Cloud"). My thanks to [Amog](https://clickhouse.com/authors/amog-iska "Amog Iska") for filling gaps
    in my knowledge to answer some questions about it.
*   [pg_clickhouse](https://clickhouse.com/docs/products/managed-postgres/extensions/pg_clickhouse/introduction "ClickHouse Docs: pg_clickhouse"), my baby, allows one to query ClickHouse tables from
    Postgres using native Postgres SQL. It currently [pushes down 16 of the 22 TPC-H](https://clickhouse.com/blog/pg_clickhouse-whats-new-july-2026 "What's new in pg_clickhouse v0.10.0: Subqueries, TPC-H Speedups, C Driver, and Aggregates") queries to ClickHouse, including nearly all Postgres data types and
    aggregate functions.
*   The [chdb_hook](https://clickhouse.com/docs/products/managed-postgres/extensions/chdb/chdb_hook "ClickHouse Docs: chdb_hook") module enables efficient, flexible import and export of
    data lake files by passing a URL to the Postgres [COPY](https://www.postgresql.org/docs/current/sql-copy.html "PostgreSQL Docs: COPY") command. It
    supports all of the ClickHouse [data formats](https://clickhouse.com/docs/reference/formats "ClickHouse Docs: Formats for input and output data") and cloud object storage
    platforms and [outperforms similar extensions](https://clickhouse.com/blog/introducing-chdb-postgres "Introducing chdb Postgres extension: High-performance imports from cloud storage").
*   [WalShadow](https://clickhouse.com/blog/introducing-walshadow "Introducing WalShadow: Sub-second Postgres replication to ClickHouse from physical WAL") provides physical replication from Postgres to ClickHouse for
    sub-second data visibility to your analytical queries.

I found demoing the features and revealing benchmark results especially
gratifying, as numerous heads bobbed and their owners made mental or literal
notes for follow-up. And follow-up they did. The booth saw a good stream of
questions about the products and integration, and several people stopped me in
the hallway track to learn more.

## Session highlights {#session_highlights}

The stress of presenting behind me, I relaxed into attending a few sessions a
day by friends new and old alike. A few highlights.

### Plan advice

Postgres committer Robert Haas [introduced pg_plan_advice](https://postgresql.us/events/postgressummitus2026/schedule/session/2450-pg_plan_advice-plan-stability-and-user-planner-control-for-postgresql/ "pg_plan_advice: Plan Stability and User Planner Control for PostgreSQL?"), a feature he added
to the upcoming Postgres 19 release, and covered and some of the underlying
technical challenges and choices implementing it. I appreciate the dedication
of the Postgres committers not to add "hints" to SQL syntax; this feature
seems like a great tool to nonetheless give users the power to influence the
planner without changing their SQL.

### Index prefetching

Committer Peter Geoghegan gave an [An Overview of Index Prefetching](https://postgresql.us/events/postgressummitus2026/schedule/session/2448-an-overview-of-index-prefetching/), which he
hopes to land in time for Postgres 20. It provides sizeable improvements via
parallel [Asynchronous I/O](https://en.wikipedia.org/wiki/Asynchronous_I/O "Wikipedia: Asynchronous I/O") for normal index scans, as opposed to bitmap
scans, which must sort data after reading it. It promises the biggest gain for
uncached data, where parallel read performance matches bitmap index scanning.
As conference organizer Chelsea Dole pointed out to me, Peter often delivers
no-effort features: when it lands, index prefetching will require no effort to
adopt! Anyone who upgrades to Postgres 20 will simply gain better index scan
performance.

### Open source CDC

Committer Amit Kapala surveyed the range open source [CDC plugins](https://postgresql.us/events/postgressummitus2026/schedule/session/2338-comparative-study-of-postgresql-cdc-plugins-and-open-source-consumer-ecosystems/ "Comparative Study of PostgreSQL CDC Plugins and Open-Source Consumer Ecosystems"). Each
serves a particular use case: in-core logical replication for physical
standbys, [Debeezium](https://debezium.io "Debeezium: Stream changes from your database") for event streaming, and our own [PeerDB](https://www.peerdb.io "Fast, simple, and cost effective Postgres replication") for data
warehousing. I admire Amit's dedication to continually improving logical
replication. I wonder what he makes of [WalShadow](https://clickhouse.com/blog/introducing-walshadow "Introducing WalShadow: Sub-second Postgres replication to ClickHouse from physical WAL")? I should have asked.

### No obituaries

Fujitsu's Gary Evans delivered [a fun talk](https://postgresql.us/events/postgressummitus2026/schedule/session/2308-30-years-of-postgresql-and-zero-obituaries/ "30 Years of PostgreSQL and Zero Obituaries") on the long history of
technologies that have promise to "kill" SQL and PostgreSQL. He showed a
rather extensive graveyard of technologies, including NoSQL, scaling ("web
scale"), and vector search, all of which appeared in specialized database
servers, and have since been replaced with new features or extensions of
Postgres (JSON/JSONB, Citus, pgVector).

### Secret decoder ring

Microsoft's Claire Giordano made an entertaining presentation on the basics of
Postgres replication. Her [secret decoder ring](https://postgresql.us/events/postgressummitus2026/schedule/session/2431-a-secret-decoder-ring-for-postgres-replication-a-beginners-guide/ "A Secret Decoder Ring for Postgres Replication: A Beginner's Guide") taught me, a replication
dilettante, quite a lot.

### PostgreSQL communities in Africa

Community advocate Benedict Kofi Amofah gave us the lowdown on the rapidly
evolving [Postgres organizations in Africa](https://postgresql.us/events/postgressummitus2026/schedule/session/2305-from-the-ground-up-building-and-growing-postgresql-communities-in-africa/ "From the Ground Up: Building and Growing PostgreSQL Communities in Africa"), starting with Madagascar, kenya,
Ghana, Cameroon, and Togo, with more in the works. Perhaps unsurprisingly,
this organic user groups mirrors the earlier experiences of community
organizers in South America and, further back in time, in North America and
Europe. The world will soon be all Postgres!

### CloudNative extensions

Gabriele Fedi of EnterpriseDB [covered](https://postgresql.us/events/postgressummitus2026/schedule/session/2316-cloudnativepg-rethinking-postgresql-extensions-in-kubernetes/ "CloudNativePG: Rethinking PostgreSQL Extensions in Kubernetes") the history and status of extension
packaging for [CloudNativePG](https://cloudnative-pg.io "Run PostgreSQL the Kubernetes way"). This was a fun one for me, as I helped to get
the [extension_control_path](https://www.postgresql.org/message-id/E1tumbY-003Dl3-2o%40gemulon.postgresql.org) feature added to Postgres, which allows
CloudNativePG to load extension files from an read-only OCI image in
Kubernetes. In recognition of which, I took some time over the weekend to [add a CloudNativePG extension OCI image to pg_clickhouse](https://github.com/ClickHouse/pg_clickhouse/pull/390 "ClickHouse/pg_clickhouse#390 Add CloudNativePG OCI images").

### Paging theory

I was super into [The Pager is the Product: PostgreSQL in Cloud Environments](https://postgresql.us/events/postgressummitus2026/schedule/session/2452-the-pager-is-the-product-postgresql-in-cloud-environments/),
by Apple's Stephen Brandon. Alas, I had to bail after ten minutes because I
was paged! 🤣 (No worries, all was fine.)

### Hallway track

I met or caught up with a slew of people in the hallway track, as well. I
chatted with my former colleague Christoph Pettus of [PGX](https://pgexperts.com "PostgreSQL Experts, because your data is your business") about an ongoing
project to add Mac Minis to the Postgres [build farm](https://buildfarm.postgresql.org); Dominic Preuss of
[VillageSQL](https://villagesql.com/) about the Postgres extensions ecosystem; and Dave Cramer of [AWS](https://aws.amazon.com "Amazon Web Services")
about the challenges of maintaining open-source extensions and other ecosystem
tools across vendors and providers.

I pitched Dave on attending the [Postgres Ecosystem Foundation](https://2026.pgconf.eu/community-events/postgres_ecosystem_foundation/) session
[PGConf.EU](https://2026.pgconf.eu "PostgreSQL Conference Europe 2026") in November, where we'll strategize ways to begin to address these
very challenges. I'm co-organizing this half-day session with colleagues from
Percona, EDB, and PgEdge. Dave can't make it that day, but *you* should come!

Speaking of extensions, I also spent time talking with Soumava Ghosh & Corey
Huinker of Apple, Divya Bhargov of Microsoft, and Lukas Fittl of pganalyze
about various issues, including extension upgrades, Postgres major version
upgrades, debugging extensions (and the Postgres core!) issues. Tarus Balog of
Percona gabbed on about the Postgres ClickHouse extensions and tools covered
in [my talk](#postgres-in-da-clickhouse).

### So many people

[Postgres Summit US 2026](https://2026.postgressummit.us) is a modestly-sized if growing conference. Still, I
visited with *so many people!* I enjoyed socially catching up with Joe Conway
(AWS), Robert Treat (AWS), Stacey Haysler (PGX), Chelsea Dole (Citadel),
Gabriele Bartolini (EDB), Peter Geoghegan (AWS), Corey Huinker (Apple), Jelte
Fennema-Nio (MotherDuck), Claire Giordano (Microsoft), Bruce Momjian (EDB),
Jan Wiek (himself), Jonathan Katz (Databricks), and engineers from Supabase,
Aiven, Apple, Pinecone, and at least 8 other companies whose names escape me
now.

Then I slept most of the weekend.

## There's more {#theres_more}

The [PostgreSQL Event Calendar](https://ics.postgresql.life) lists dozens of global, regional, and local
Postgres community conferences every year. Maybe hundreds? I dunno, it's a
*lot.* This was ClickHouse's first foray into Postgres conference sponsorship,
but only the start. A great start, in my estimation. Next up, we're sponsoring
[PGConf.EU](https://2026.pgconf.eu "PostgreSQL Conference Europe 2026") in Valencia in November. I'll be there talking about the
aforementioned [Postgres Ecosystem Foundation](https://2026.pgconf.eu/community-events/postgres_ecosystem_foundation/) project, but also [how to contribute to the PostgreSQL documentation](https://www.postgresql.eu/events/pgconfeu2026/schedule/session/7973-how-to-contribute-to-the-postgresql-documentation/ "How to Contribute to the PostgreSQL Documentation"). See you in València!

---

## Get started with ClickHouse Managed Postgres today

Interested in seeing how ClickHouse Managed Postgres works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?intent=pg&loc=blog-cta-2544-get-started-with-clickhouse-managed-postgres-today-sign-up&utm_blogctaid=2544)

---