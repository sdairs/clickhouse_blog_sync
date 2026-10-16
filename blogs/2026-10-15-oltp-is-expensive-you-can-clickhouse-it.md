---
title: "OLTP is expensive, you can ClickHouse it."
date: "2026-10-15T14:59:39.900Z"
author: "Andrey Chudnovskiy"
category: "Engineering"
excerpt: "Offload settled Postgres data to ClickHouse to reduce storage and query costs while keeping active transactions in Postgres."
---

# OLTP is expensive, you can ClickHouse it.

<style>
div.w-full + p,
span.relative + p {
  text-align: center;
  font-style: italic;
}
</style>

## Summary {#summary}

In this article we explore a new application pattern - offloading more of your Postgres data to ClickHouse. Leading to an order of magnitude better unit economics for your applications, as the data size increases.

We start with what an Online Transactional Processing (OLTP) database like Postgres does on every write and read, and the costs it takes on to keep transactions ACID-compliant. We then show how to stop paying those costs for the data and queries that don’t need them.

![](https://clickhouse.com/uploads/oltp_oct2026_postgres_clickhouse_matrix_863a16d405.png)

## The last time the datasets exploded {#the_last_time_the_datasets_exploded}

Back in the 2000s Web and Mobile booms exponentially increased the dataset sizes the systems needed to process. At the time, many fast growing companies turned to NoSQL databases for scalability and efficiency, which SQL databases couldn’t provide at the time.

Over the following few years the question of operational databases' scalability was resolved. With the cloud advancements, the latest systems offer tens of terabytes on single-writer OSS PostgreSQL deployments. With some closed source forks scaling beyond 100 TB of storage without compromising OLTP guarantees. While systems like Spanner and sharded MySQL/Postgres allow web-scale companies to achieve transactional consistency at global scale.

The increased scalability comes with a big cloud infrastructure bill. The systems based on OLTP engines scale linearly at best. You pay N times more for Postgres, you get up to N times more storage and processing power. With ClickHouse Managed Postgres NVMe based architecture you can get better multipliers on transactional throughput.  
Still though as your dataset sizes explode, the compute and storage costs grow linearly. 

In 2026, thanks to the agentic AI boom, the data sizes and query volumes are rising faster than ever before, reaching tens of terabytes of transactional data hit earlier in the cycle, demanding a better economy for fast-moving companies.

We can look outside of the traditional OLTP box for a solution, just like the web companies in the 2000s did.

## Why is your PostgreSQL bill high {#why_is_your_postgresql_bill_high}

*PostgreSQL here is used as the most popular OLTP database for new applications. Other operational database systems work with very similar mechanics.*

PostgreSQL guarantees four fundamental transactional properties for all data it writes and reads: Atomicity, Consistency, Isolation, and Durability (ACID):

* **Atomicity:** all of a transaction’s changes apply, or none do.  
* **Consistency:** each transaction leaves the database in a valid state, with all constraints satisfied.  
* **Isolation:** concurrent transactions don’t interfere; each behaves as if it ran alone.  
* **Durability:** committed changes survive process crashes and instance failures.

Guaranteeing ACID for complex, multi-row transactions while thousands run concurrently is a hard problem. Postgres solves it with a few mechanisms, and each one adds work to every write:  
For durability, it flushes the transaction’s write-ahead log (WAL) record to disk before confirming each COMMIT. For isolation, it uses MVCC: an update never changes a row in place. Instead, it writes a complete new physical copy of the row and leaves the old copy behind as a dead tuple until VACUUM reclaims it. And so that a read right after a write sees the new data, every insert or update also modifies every affected index entry.

Add it all up, and the amplification is steep: to change \~100 bytes of row data, Postgres modifies several 8 KB heap and index pages in the buffer pool and eventually writes tens of kilobytes to disk as WAL, full-page images and page flushes

That is not just the write path. When the system fully supports ACID, data formats are built for that too, and the reads involve additional costs:

- **Storage size:** Postgres keeps every tuple in uncompressed 8 KB pages. Settled, rarely read data costs as much to store as rows you update every second.  
- **Read I/O:** every row read loads the full tuple, with all its columns, plus the index pages that locate it. Once the data outgrows RAM, those 8 KB pages keep pushing each other out of the cache, so more and more reads go to disk.  
- **Index amplification:** any lookup by something other than the primary key needs an index, because a full table scan is too expensive at scale. Postgres updates every index inside the write transaction, which slows writes and multiplies storage and vacuum costs.

Here is a simplified view of and write and read amplifications in PostgreSQL database, when the dataset exceeds memory buffers:

<video autoplay="1" muted="1" loop="1" controls="1">
  <source src="https://clickhouse.com/uploads/oltp_oct2026_image2_eadf7ff337.mp4" type="video/mp4" />
</video>

## Distributed Postgres won’t help {#distributed_postgres_won_t_help}

Shared storage and sharded systems are designed to allow linear scale with the data size and workload. 

For a sharded PostgreSQL system, with some investment in schema, you can achieve near linear scalability of data size and transactional capability as you throw more dollars. 

In the real world, most applications get diminishing returns due to costs of additional coordination and occasional multi-phase cross shard commits.

Shared storage solutions incur more infrastructure costs to process the workload as more parts of the distributed system need redundancy. The additional costs then amortised with aggressive multi-tenant packing on the storage side. 

Even when additional optimizations and cheaper object storage are taken into account, those systems generally cost more than simple OSS deployments for production workloads.

## Most data stops changing. Its OLTP bill doesn’t. {#most_data_stops_changing_its_oltp_bill_doesn_t}

Many applications across different business domains treat actively changed and settled data differently. Active state and recent rows frequently used to write new transactions, read by users and integration systems. After certain window or activity criteria passed - the data stays mostly read-only, accessed infrequently while still needs to be preserved.

Here are some examples across different business application domains:

- Financial transactions before the previous statement are preserved for infrequent access or audit  
- Retail purchases beyond the return window become read-only though needed for history views  
- Social activities after the eligible change window passed still available for browsing  
- Tenant metadata for deactivated customers become readonly

In all those examples, once data moved from mutate-heavy to settled state, the need for ACID subsided. Though, the data incurs associated costs, as long as maintained in the OLTP storage.

## Postgres writes, ClickHouse remembers {#postgres_writes_clickhouse_remembers}

ClickHouse is a SQL database engine. It can process any SQL workload your application needs a database for. 

ClickHouse isn’t optimized for high-frequency ACID transactions, and that changes the economics completely:

* **Storage:** columnar compression typically shrinks datasets 10–30×.  
* **Infrastructure:** Postgres offerings rely on large, high-performance disks or layers of caching, about 5× the cost of a comparable ClickHouse Cloud setup.  
* **Indexing:** indexes are built in the background over large batches of rows, so updating them takes orders of magnitude less CPU per record.  
* **Aggregations:** summary and analytical queries cost about 100× less to run, thanks to purpose-built index structures, a simpler concurrency model and no cache contention with writes.

The trade-offs:

* **Slower single-row reads:** rebuilding a full row from column data can take hundreds of milliseconds.  
* **Eventual consistency:** reads may see values up to about a second old.

Few applications accept that for data that’s actively changing. But once the data settles, why pay 5–10x to keep it ready for updates that never come?

Here is how it works:

- Writes and fresh row reads remain in Postgres.  
- ClickHouse serves reads from settled data reads, most of the queries requiring aggregation, as well as occasional writes.  
- ClickHouse offers the best economics for real-time analytical queries and data warehousing for both data tiers.

Bonus: Fewer indexes, lighter maintenance, means less PostgreSQL compute costs.

![](https://clickhouse.com/uploads/oltp_oct2026_image3_0bf6200a86.png)  
*(Janitor AI CEO shares a success story on offloading settled data to ClickHouse at CH South Bay Meetup)*

Building an application using 2 databases, keeping data in sync and system complexity under control is a challenging task. ClickHouse cloud is built to make this easy.

## Postgres + ClickHouse on ClickHouse Cloud. {#postgres_clickhouse_on_clickhouse_cloud}

Our mission at ClickHouse is to deliver best in class price-performance for both analytical and transactional workload.

<iframe src="/uploads/oltp_oct2026_postgres_clickhouse_architecture_07f962d034.html" frameborder="0" style="width: 100%; height: 600px;"></iframe>

Unified OLTP+OLAP stack on ClickHouse Cloud is optimized to get most out of the strengths of Postgres and ClickHouse, and provide a seamless integration experience:

- Local NVME store for Postgres data offers 2x-10x faster transactions and higher throughput for OLTP workload.  
- WalShadow - our latest native CDC option, enables data replication to ClickHouse within milliseconds without costs for the Postgres performance and stability.  
- pg_clickhouse is best in class FDW for Postgres. Your application can continue using Postgres protocol, while unlocking the economics of ClickHouse. Saving you upfront engineering costs.

You can build this pattern on ClickHouse Cloud today and cut the cost of serving settled data by an order of magnitude. Next on our roadmap is a fully managed experience that offloads settled data to ClickHouse for you.

Try it out!

---

## Get started with ClickHouse Managed Postgres today

Interested in seeing how ClickHouse Managed Postgres works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?intent=pg&loc=blog-cta-2663-get-started-with-clickhouse-managed-postgres-today-sign-up&utm_blogctaid=2663)

---