---
title: "Introducing Postgres to Postgres ClickPipes in ClickHouse Cloud"
date: "2026-06-11T16:10:02.435Z"
author: "Amogh Bharadwaj"
category: "Product"
excerpt: "Postgres to Postgres ClickPipes brings fully managed, low-downtime Postgres migrations to ClickHouse Cloud."
---

# Introducing Postgres to Postgres ClickPipes in ClickHouse Cloud

Migrating [Postgres](https://www.postgresql.org/) between providers often involves more manual effort than users expect. This blog talks about the challenges with current migration paths, and how the new **Postgres to Postgres ClickPipes** in [Postgres by ClickHouse](https://clickhouse.com/cloud/postgres) (now in [public beta](https://clickhouse.com/blog/postgres-managed-by-clickhouse-beta)!) enables seamless, **fully managed** migrations with minimal downtime and operational overhead.

## The complexity of Postgres migrations today {#the-complexity-of-postgres-migrations-today}

Achieving a true apples-to-apples migration experience is critical for Postgres-to-Postgres migrations. A Postgres database is far more than a collection of tables: indexes, constraints, sequences, triggers, and other database objects each play a role in running core business logic. Preserving these objects correctly is essential to ensuring applications behave identically after the migration.

Despite this, most managed Postgres providers simply point users to documentation of various tools, and lack a purpose-built fully managed migration tooling. 

Stitching them together into a reliable migration workflow introduces several hassles:

* **Operational complexity becomes a barrier to adoption.** Users are expected to install and manage command-line tools, generate schema dumps, restore them correctly, and coordinate the migration process themselves.  
* **Migrations require expertise that many users don't have.** While [`pg_dump`](https://www.postgresql.org/docs/current/app-pgdump.html) and [`pg_restore`](https://www.postgresql.org/docs/current/app-pgrestore.html) are powerful tools, they expose users to the intricacies of Postgres. This increases the risk of errors and makes migrations more intimidating.  
* **Large migrations are slow and opaque.** Standard `pg_dump` and `pg_restore` or native logical replication workflows can take hours for large datasets, while providing little visibility into progress or failures. Monitoring these long-running pipelines often becomes an operational burden in itself. [This benchmark](https://clickhouse.com/blog/practical-postgres-migrations-at-scale-peerdb#benchmarking-large-postgres-migrations) goes into depth about this.  
* **Online migrations require highly reliable CDC.** Teams typically rely on Change Data Capture (CDC) to keep the destination continuously synchronized while preparing for a controlled cutover. Since restarting from scratch can be expensive, the CDC pipeline must be highly reliable.

## Introducing Postgres to Postgres ClickPipes {#introducing-postgres-to-postgres-clickpipes}

To address the challenges discussed in the previous section, we built a fully managed Postgres migration service for Postgres by ClickHouse in [ClickHouse Cloud](https://clickhouse.com/cloud). Postgres to Postgres ClickPipes abstracts away much of the operational complexity involved in setting up and running a migration.

![](https://clickhouse.com/uploads/postgres_clickpipes_jun2026_image3_ef085baf50.jpg)


### Automated schema dump {#automated-schema-dump}

One of its key features is [**automated schema migration**](https://github.com/PeerDB-io/peerdb/pull/4283). Instead of requiring users to install and run tools such as `pg_dump` and `psql`, ClickPipes performs the schema dump and restore under the hood.

Since we are abstracting this away from the user, we made sure to cover any corner cases that one might run into. Listing a few salient ones:

* Support for **secure connections** to source. This includes using TLS, certificates and even private links.  
* Avoiding conflicts due to **Postgres roles.**  These roles can always be created during cutover and are not necessary for the data movement itself.  
* Accounting for differences in source and target **Postgres versions**. pg_dump version and source server versions need to be compatible with one another.  
* **Single round-trip** connection to apply on destination, reducing latency. Running every statement in the dump file sequentially could be long-running otherwise and run into timeouts.  
* **Transactional** application of schema dump to allow for **idempotent** retries. This provides flexibility and room for making corrections and changes on the fly without having to recreate the ClickPipe.  
* Dump errors immediately shown in ClickPipes UI and also via **notifications**.

Running these operations inside ClickHouse Cloud also provides the benefit of **colocation** - schema dumps and initial loads are executed close to the source database making it faster than running it on your machine.

For users with specialized requirements, ClickPipes **also supports a manual mode** that allows custom migration workflows with links to relevant documentation.

![](https://clickhouse.com/uploads/postgres_clickpipes_jun2026_image2_5477b13b51.png)

### Parallel initial loads and reliable CDC {#parallel-initial-loads-and-reliable-cdc}

Postgres to Postgres ClickPipes is powered by PeerDB, which provides two key capabilities for online migrations: **parallel initial loads** to reduce the time required to move terabytes from days to hours, and **reliable CDC** always reading the replication slot on source, with support for features such as automatic **column addition** propagation and TOASTs to avoid costly resyncs during cutover.

For a deeper dive, check out our earlier blog post [here](https://clickhouse.com/blog/practical-postgres-migrations-at-scale-peerdb#benchmarking-large-postgres-migrations).

### Retry mechanisms and alerting {#retry-mechanisms-and-alerting}

The Postgres to Postgres ClickPipe is resilient to transient errors on both pull and push, with both processes being independent of each other, and every activity being surrounded by retries.

In addition to robustness, this also allows us to have a smarter **notification system** which can send out emails and UI bell notifications based on the number of failed retries.

![](https://clickhouse.com/uploads/postgres_clickpipes_jun2026_image1_710956fdde.png)

### Demo {#demo}

The following demo showcases the onboarding experience where you will see a ClickPipe created with just a few clicks with a clean, step-by-step wizard.


<video autoplay="1" muted="1" loop="1" controls="0">
  <source src="https://clickhouse.com/uploads/PG_Auto_Full_web_1addd06105.mp4" type="video/mp4" />
</video>

## Next steps {#next-steps}

With your transactional loads moved over to Postgres by ClickHouse, you are now all set to plug in blazing fast **analytics** powered by ClickHouse. Here are a few links to get this done in minutes:

* [Integrating Postgres data with ClickHouse](https://clickhouse.com/docs/cloud/managed-postgres/clickhouse-integration)  
* [Query ClickHouse from PSQL using pg_clickhouse, our own extension!](https://clickhouse.com/docs/cloud/managed-postgres/extensions/pg_clickhouse)

Next on our roadmap is a set of features designed to assist with **cutover**, providing a smoother end-to-end migration experience into Postgres by ClickHouse. Stay tuned!


---

## Get started today

Interested in seeing how ClickHouse works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-868-get-started-today-sign-up&utm_blogctaid=868)

---