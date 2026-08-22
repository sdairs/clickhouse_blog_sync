---
title: "What else runs on your Postgres server, and how do we stop it from taking the database down?"
date: "2026-08-21T14:11:30.557Z"
author: "Kaushik Iska"
category: "Engineering"
excerpt: "ClickHouse Managed Postgres uses runtime budgets, cgroup limits, and disk-full session exemptions to keep supporting services from compromising database availability."
---

# What else runs on your Postgres server, and how do we stop it from taking the database down?

What else is running on your Postgres server's VM, and what stops it from taking the database down? Alongside Postgres, ours runs several PgBouncer instances, a backup agent, metrics exporters, a local Prometheus, a log collector, and a handful of watchdog timers. Each process protects the database. Each can also leak memory, burn CPU, or fill a disk.

That places every one of them inside the database's failure model. A monitoring process can consume the memory Postgres needs. A backup agent can saturate the CPUs serving queries. Either failure can bring down the whole instance.

## A shared machine is shared memory {#a_shared_machine_is_shared_memory}

Postgres gets one unusually strong boundary. Its `shared_buffers` allocation lives in huge pages reserved at boot, so another process cannot slowly eat into it. We described why we make that allocation strict in our post on [reserving huge pages for Postgres](https://clickhouse.com/blog/huge-pages-clickhouse-managed-postgres).

Postgres also needs memory outside `shared_buffers`. The kernel's page cache, each backend's working memory, connection state, and plenty of smaller allocations come from the same machine-wide pool used by PgBouncer, WAL-G, Prometheus, exporters, and logging. A leak in any one of those processes can consume the headroom every database backend depends on.

ClickHouse Managed Postgres gives the supporting processes explicit resource limits. Four Go services, Prometheus, the WAL-G backup agent, `postgres_exporter`, and `node_exporter`—run in one cgroup v2 slice. The systemd `MemoryHigh` and `MemoryMax` properties write the slice's `memory.high` and `memory.max` controls. Each service also carries a `GOMEMLIMIT` sized so the individual Go heap budgets add up below `memory.high`.

![](https://clickhouse.com/uploads/postgres_process_budgets_overview_5ca144bf83.jpg)

## Runtime and cgroup enforcement {#runtime_and_cgroup_enforcement}

The boundaries do different jobs:

| Boundary | What it does | Why it exists |
| --- | --- | --- |
| `GOMEMLIMIT` | Makes the Go runtime collect more aggressively as its heap approaches its configured target. | Heap growth increases GC frequency before the cgroup reaches kernel-enforced thresholds. |
| `memory.high` | Forces direct reclaim and throttles allocations charged to the cgroup. | Pressure is applied to the processes responsible for the cgroup's memory usage. |
| `memory.max` | Sets the hard cgroup ceiling; if reclaim cannot reduce usage, the kernel raises an OOM event in that cgroup. | OOM victim selection is scoped to processes charged to the supporting-services cgroup. |

`GOMEMLIMIT` is deliberately the first line of defense. Go can react with much more context than the kernel: it knows what is heap, what is live, and when another garbage-collection cycle might help. A service approaching its budget does more collection work and usually stays inside the line on its own.

![](https://clickhouse.com/uploads/postgres_memory_1_gomemlimit_1024_7fb95758fe.gif)

`GOMEMLIMIT` remains a runtime target. Native allocations, retained objects, or a genuine leak can carry a process past it. The cgroup supplies kernel enforcement: charges above `memory.high` enter reclaim and throttling.

![](https://clickhouse.com/uploads/postgres_memory_2_memory_high_8a6aa69486.gif)

Charges that cannot be reclaimed below `memory.max` trigger a cgroup OOM event.

![](https://clickhouse.com/uploads/postgres_memory_3_memory_max_5ac02f4ebd.gif)

Postgres memory is charged to a separate cgroup, so a `memory.max` event in the supporting-services cgroup does not select a Postgres process.

![](https://clickhouse.com/uploads/postgres_memory_4_oom_isolation_488babd703.gif)

The slice's allowance is the same headroom that our [strict-overcommit policy](https://clickhouse.com/blog/strict-memory-overcommit-for-postgres) sets aside on top of Postgres's share. The commit budget reserves the memory; the cgroup holds the processes to it. The two controls describe the same capacity from opposite directions.

## Budgets across every resource {#budgets_across_every_resource}

A process can behave perfectly in heap usage and still hurt the database somewhere else, so the same discipline extends across the VM:

- Backups run at a fraction of the default CPU weight, so foreground database work wins when the machine is busy.
- WAL-G's buffers are a fixed fraction of RAM, keeping memory use bounded as workload grows.
- The log collector has its own memory limiter, keeping a burst of logs from becoming a second incident.
- Metrics leaving the box are hand-picked, so a new label cannot quietly create an unbounded cardinality bill in memory, CPU, and network traffic.

Each resource now has an enforcement point: scheduler weight for CPU, fixed buffer sizing and cgroups for memory, local thresholds for disk, and an allowlist for exported metric series.

## Disk-full session exemptions {#disk_full_session_exemptions}

Postgres needs free disk to make progress, and a full data volume can quickly turn an ordinary workload into an availability incident. At the emergency threshold, the disk-full watchdog terminates sessions to reduce write pressure. Two usernames are exempt from termination: replication and monitoring.

![](https://clickhouse.com/uploads/postgres_disk_1_threshold_15f5a8cee1.gif)

Termination is not indiscriminate. The watchdog reads `pg_stat_activity` and maps each backend's database username to a keep-or-terminate decision.

![](https://clickhouse.com/uploads/postgres_disk_2_classify_201d13c62d.gif)

Sessions from ordinary application usernames are then terminated, which removes their write paths immediately.

![](https://clickhouse.com/uploads/postgres_disk_3_terminate_9423a5f641.gif)

The replication exemption keeps standby WAL streaming active. The monitoring exemption keeps database metrics available to operators and automation during the event.

![](https://clickhouse.com/uploads/postgres_disk_4_preserve_c79184e411.gif)

The backup agent receives a bounded memory allocation and a lower CPU weight. Prometheus is charged to the host-services cgroup. The disk watchdog preserves the replication and monitoring roles explicitly. These controls keep backup, replication, and observability available within defined resource limits.

## Resulting isolation model {#resulting_isolation_model}

A managed Postgres server is a small system of cooperating processes. Reliability depends on treating every supporting service as both protection and potential pressure: give the runtime a budget it can understand, give the kernel a ceiling it can enforce, and keep the emergency path outside the failure it is meant to handle.

These controls are enabled by default on every ClickHouse Managed Postgres server.


---

## Get started with ClickHouse Managed Postgres today

Interested in seeing how ClickHouse Managed Postgres works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?intent=pg&loc=blog-cta-1626-get-started-with-clickhouse-managed-postgres-today-sign-up&utm_blogctaid=1626)

---