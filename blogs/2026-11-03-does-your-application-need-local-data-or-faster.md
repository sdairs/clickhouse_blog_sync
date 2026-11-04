---
title: "Does your application need local data or faster Postgres?"
date: "2026-11-03T14:55:13.054Z"
author: "Lionel Palacin and Gülçin Yıldırım Jelínek"
category: "Engineering"
excerpt: "Local synchronization makes reads fast, but adds another data layer to manage. Explore how AI agents change the trade-off and when NVMe-backed Postgres can simplify the architecture."
---

# Does your application need local data or faster Postgres?

## Summary

Before adding local copies to make your application fast, ask why it’s slow to begin with.

Local synchronization adds complexity, especially when agents keep changing the working set. A fast, central NVMe-backed Postgres offers a simpler starting point: query directly and scale reads with replicas.

Applications need fast reads and writes, otherwise they’re not usable. When the main Postgres instance cannot deliver good performance, one existing solution is to synchronize part of the working set close to the application. Reads become local, and less pressure is placed on the central database. This can be good, but the trade off is another layer of data to manage, while writes still depend on a central Postgres.

In this blog, we’ll explore how local data synchronization works, why AI agents make the local working set harder to predict, and whether a faster central Postgres instance could simplify the architecture from the beginning.

## Start with the database bottleneck

Many of the managed Postgres services keep their data on network-attached storage. [Amazon RDS for PostgreSQL](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_Storage.html), for example, stores data on EBS volumes reached over the network, and each volume has its own IOPS and throughput limits. Other services, such as Neon, go further and separate compute from storage entirely. These designs give you storage that survives the loss of a compute node and flexible provisioning, but every read that misses the cache has to cross the network.

That matters once a workload becomes I/O-bound. At that point, adding compute doesn't make the database faster. Reads still have to fetch pages from storage, writes still generate [WAL](https://www.postgresql.org/docs/current/wal-intro.html), and background work such as [VACUUM](https://www.postgresql.org/docs/current/routine-vacuuming.html) competes for the same I/O budget. As concurrency rises, queries slow down and tail latency grows.

This is why applications on managed Postgres often get slower as usage grows, even when CPU and memory look fine. Before you add a local data layer to work around that latency, check whether the real bottleneck is the storage under your database.

## Do you need a second copy of your data?

When the main database gets slow, the usual fix is to add a layer in front of it. For years that meant a cache like Redis or Valkey. More recently, sync engines have taken the idea further by keeping a synchronized copy of the data the application needs inside the application itself. A sync layer subscribes to the database's [logical replication](https://www.postgresql.org/docs/current/logical-replication.html) stream, filters the changes down to a declared subset, and keeps that subset materialized in a local store. The store can live in memory, in an embedded database on the client, or in a cache on an edge node. The mechanism is the same.

The developer declares the subset up front: which tables, which rows (usually a filter on a tenant or user column), and which columns. In a multi-tenant application, the subset for one client is typically that tenant's rows and nothing else. Every client that declares the same subset receives the same stream of changes, so the sync layer's cost is shared when many clients want the same data.

Once the subset is in place, reads for anything inside it are local. Screens, forms and dashboards query the local store, and the round trip to Postgres disappears from the read path for those reads. Reads for anything outside the subset still go to the database, or the subset has to be widened first.

<iframe src="/uploads/01_electric_local_reads_bddae64671.html" title="Local synchronization: select a subset, synchronize it, and read locally" width="100%" height="720" frameborder="0" style="width:100%;height:720px;border:0;max-height:none;" loading="lazy"></iframe>

What the application has gained is a second copy of part of its data, with its own lifecycle. Someone has to decide what belongs in the subset, when it changes, how long a client keeps it, and what happens when the schema changes. This is worth it for applications that work offline or on unreliable networks, and for applications where many clients read the same, stable working set. It is less obviously worth it when the only requirement is fast reads from an online database with good connectivity. Predictable queries make the subset easy to declare. On their own, they don't mean you need a local copy.

## Most applications also need to write

A sync layer handles the read path only, so the application must maintain a separate write path to the central Postgres, usually through its own API. Once a transaction commits, the change flows back out via logical replication, through the sync layer, and into every local store whose declared subset includes the affected rows. So a write produces two separate events on the client: the API response, and the arrival of the committed change in the local dataset shortly after..

To hide that gap, applications keep optimistic state. The change is applied to the local view immediately, before the server has confirmed it. The application then has to reconcile that provisional state with what arrives through the sync stream, which includes the committed version of its own write as well as writes from other clients touching the same rows. When its own write shows up in the stream, the provisional copy is dropped. If the write is rejected, the provisional copy has to be rolled back and the view corrected.

<iframe src="/uploads/02_write_and_reconcile_e094f8720c.html" title="Write to Postgres and reconcile the synchronized local view" width="100%" height="720" frameborder="0" style="width:100%;height:720px;border:0;max-height:none;" loading="lazy"></iframe>

Postgres remains the authoritative source throughout, and it is still the place where [concurrent writes](https://www.postgresql.org/docs/current/transaction-iso.html) are ordered, through transactions. An application that reads committed state directly from Postgres gets that ordering for free. It never waits for a local copy to catch up and never holds two versions of the same row. A local copy gives fast reads in exchange for a reconciliation problem the application has to own. Pending local changes, committed data arriving asynchronously, and the view the user sees all have to agree.

## Agents make the working set harder to predict

A traditional application works with a bounded working set because people navigate it in predictable patterns. A product page loads product information, a billing page loads one specific account, and a search page queries a given set of fields. An AI agent behaves differently: it could load a product, identify the customers who bought it, and then look for similar products, all based on the prompts and context provided at runtime.

The paradigm is different now. With agents, a developer cannot always predict the application’s working set or accurately define its boundaries. Declared subsets remain possible, but the working-set boundary must be broad enough to support the agent’s possible query paths. On-demand and progressive loading  can avoid synchronizing the entire subset upfront, but data that has not been materialized still requires a remote request before it becomes locally queryable.

This creates several trade-offs:

- Synchronize broadly and transfer data the agent may never use.
- Load progressively and put synchronization back in the read path.
- Create task-specific subsets and manage their lifecycle individually.

A sync layer’s fan-out is most effective when many consumers reuse the same subset. When agents require different, changing subsets of data, there is less reuse across local copies and fewer opportunities to amortize synchronization work. The question becomes: if the dataset is a moving target, keeps growing, and continually requires new data to be synchronized locally, is this architecture still relevant?

## What if Postgres is already fast enough?

[ClickHouse Managed Postgres](https://clickhouse.com/blog/postgres-managed-by-clickhouse-beta) runs Postgres on [NVMe storage](https://clickhouse.com/blog/postgres-on-nvme) physically attached to the database compute. Compared with network-attached storage, this lowers disk latency and provides substantially more IOPS for reads, writes, WAL activity, and maintenance. The result is [lower query latency and higher  query throughput than network attached Postgres solution.](https://postgresbench.clickhouse.com/)

In the case of an application with good connectivity, if querying a central Postgres instance already satisfies the requirements in terms of latency and throughput, then maintaining a synchronized local dataset might result in greater complexity than the improvement in performance brings.

This matters also for server-side agents. They usually run close to backend services and already depend on network access to an inference service or other tools. They may also exist for only one task, making it difficult to reuse a local dataset enough to justify synchronizing it. When the agent’s working set keeps moving, directly querying a fast authoritative database can be simpler:

- Query any authorized operational data through the existing API
- Read and write against the same authoritative system
- Read from the central instance when immediate consistency matters
- Avoid synchronizing data the agent may never query

The architecture becomes:

<iframe src="/uploads/03_nvme_postgres_473d96d4ca.html" title="Applications and agents querying ClickHouse Managed Postgres on local NVMe" width="100%" height="720" frameborder="0" style="width:100%;height:720px;border:0;max-height:none;" loading="lazy"></iframe>

ClickHouse Managed Postgres [supports read replicas](https://clickhouse.com/docs/products/managed-postgres/read-replicas), allowing read-heavy agent workloads to scale horizontally without creating a local dataset for every agent.

NVMe does not solve inefficient queries. Connection pooling, query optimization, and concurrency controls are still important. Although faster storage increases the capacity of the central database, it does not eliminate all the limitations. The advantage from an architectural point of view is that more work can remain on the usual Postgres path before it becomes necessary to carry out another application-level data copy.

## What if you need multi-AZ durability?

There is one copy the database does need, and it isn’t an application-level one. Local NVMe is fast because it sits next to the compute, which also means it doesn’t survive the loss of that compute on its own. ClickHouse Managed Postgres handles this the way Postgres has always handled it: with replication at the database layer rather than a replicated disk.

A service can run with [up to two standbys](https://clickhouse.com/docs/products/managed-postgres/high-availability) spread across availability zones. With two standbys, replication is synchronous: the primary waits for at least one standby to acknowledge a write before confirming it, so a failover loses no committed transactions. With one standby, replication is asynchronous, which trades a small window of recent transactions for lower write latency. In both cases, failover promotes a standby automatically. Independently of standbys, WAL is continuously archived to object storage and base backups support point-in-time recovery.

[The HA round of PostgresBench](https://clickhouse.com/blog/postgresbench-ha) measured what these guarantees cost. With two synchronous standbys, ClickHouse Managed Postgres delivered about 4x the throughput of an Amazon RDS Multi-AZ cluster running the same two-standby quorum configuration, so the durability doesn’t give back the performance the previous section argued for.

For the question this post is asking, what matters is where those copies live. They sit under the database, the service manages them, and the application never sees them or has to reconcile them.



---

## Start with ClickHouse Managed Postgres

See how your workload performs on local NVMe. Sign up for ClickHouse Cloud and provision your first managed Postgres service.

[Sign up](https://console.clickhouse.cloud/signup?intent=PG&loc=blog-cta-2841-start-with-clickhouse-managed-postgres-sign-up&utm_blogctaid=2841)

---

## Scale analytics beyond Postgres

As the dataset grows and more agents access it, the workload will include more historical scans, aggregations, and comparisons involving large volumes of data. Although the system has fast NVMe storage, Postgres is still a row-oriented transactional database, so those queries would be better met by ClickHouse.

ClickHouse Managed Postgres combines the two engines into a single data layer. [WalShadow](https://clickhouse.com/docs/products/managed-postgres/sync-to-clickhouse/walshadow) replicates certain Postgres tables directly into ClickHouse by using the physical WAL. The feature is currently in private preview and has a commit-to-visible latency of about [200 ms as shown in ClickHouse's benchmark](https://clickhouse.com/blog/introducing-walshadow). The replication process remains asynchronous.

The [pg_clickhouse extension](https://clickhouse.com/docs/products/managed-postgres/extensions/pg_clickhouse/introduction) makes it possible to access ClickHouse tables via Postgres and sends supported analytical queries down to ClickHouse. Applications and agents can maintain a connection to Postgres while using different engines for transactional work and for analytical purposes. For this to work, foreign tables must be configured and pushdown must be supported; automatic routing of every query is not provided.

<iframe src="/uploads/04_postgres_and_clickhouse_b3ea8f8d85.html" title="Transactional and analytical queries with pg_clickhouse and WalShadow" width="100%" height="720" frameborder="0" style="width:100%;height:720px;border:0;max-height:none;" loading="lazy"></iframe>

Replication is still involved, but the analytical copy handles the shared workload at the data layer by carrying out large scans and aggregations on a columnar engine. The analytical capacity is able to increase on its own without the need to distribute those datasets among each agent's runtime.

## Start with the simplest architecture

Local synchronization is a great solution when applications need offline access, have limited network connection, or repeatedly read a predictable working set. For normal applications, the first step is to measure whether the central database can meet the required latency and throughput before introducing another copy of the data.

AI agents make this decision more important: their queries can change with every task, making local datasets harder to define. ClickHouse Managed Postgres provides a foundation for serving those evolving needs: keep operational reads and writes in Postgres, add read replicas where freshness requirements allow. When application usage outscale Postgres, offload analytical workloads to ClickHouse.

Start simple with ClickHouse Managed Postgres, grow with ClickHouse.