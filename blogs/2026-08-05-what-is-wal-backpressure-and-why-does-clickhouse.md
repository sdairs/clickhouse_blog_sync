---
title: "What is WAL backpressure, and why does ClickHouse Managed Postgres need it?"
date: "2026-08-05T15:58:59.466Z"
author: "Kaushik Iska"
category: "Engineering"
excerpt: "How ClickHouse Managed Postgres uses WAL-aware backpressure to slow client writes, protect disk space, and let the archiver recover."
---

# What is WAL backpressure, and why does ClickHouse Managed Postgres need it?

What is WAL archiving, and why would we deliberately throttle our database's writes? All changes to Postgres land in the write-ahead log (WAL) before they touch a table, and our managed Postgres uploads each finished WAL segment to object storage to make point-in-time recovery possible. Postgres may not delete a segment until its upload succeeds, so when the workload writes faster than the archiver ships, WAL piles up until the disk fills. Postgres treats a full WAL disk as a PANIC: the instance goes down.

## Backpressure from the data plane

ClickHouse Managed Postgres responds with backpressure. A systemd timer counts the pending segments every 15 seconds and caps Postgres's write bandwidth with the cgroup v2 I/O controller. The caps are fractions of the disk's provisioned throughput, and they tighten as the backlog deepens:

| Pending segments | Write cap | On a 500 MB/s disk |
|---:|---:|---:|
| 100 | 80% of baseline | 400 MB/s |
| 500 | 50% of baseline | 250 MB/s |
| 1,000 | 20% of baseline | 100 MB/s |

Slower writes mean less WAL per second, and the archiver gains ground. All of this happens on the data plane, so even if the control plane is down or unreachable, the database keeps protecting itself.

![WAL backpressure architecture: client backends are write-throttled while the archiver, checkpointer, WAL writer, and logger retain full disk throughput](https://clickhouse.com/uploads/wal_backpressure_diagram_9dbc349236.jpg)

## Don't throttle the cure

A cap on the whole service would also cap the cure: the archiver draining the queue, the checkpointer that lets old WAL be deleted, even the logger the archiver writes through. So the throttle splits the cgroup in two. Each Postgres process announces its role in its process title, so the drain path is sorted into an immune group and every client backend into a throttled one. Only the throttled group is capped, and reads are never capped at all.

## Seeing it in action

We ran the mechanism on a single EC2 box and let it fight a deliberately backed-up archiver. The setup:

- **Box:** m7i.2xlarge (8 vCPU, 32 GB), Ubuntu 24.04, Postgres 16.
- **Data disk:** a dedicated gp3 volume provisioned at 500 MB/s, which is the throttle baseline, so the tiers work out to 400, 250, and 100 MB/s.
- **Throttle:** the production throttle class, verbatim, on a 15-second systemd timer, with `Delegate=yes` on the Postgres unit so it can manage the sub-cgroups.
- **The backed-up object store:** an `archive_command` rate-limited to 4 MB/s, one quarter of a segment per second. At minute 20 the limit is removed, simulating the moment object storage recovers.
- **Workload:** pgbench simple-update, 48 clients, scale 300, for 35 minutes.

What happened, in order:

- **Before the benchmark started**, bulk-loading the pgbench tables had already pushed the backlog past 100 segments, and the 80% cap was in force at t=0 with 224 segments pending. Bulk loads are exactly the workloads that outrun archiving.
- **Minute 1.9:** backlog crossed 500, cap dropped to 50%.
- **Minute 4.7:** backlog crossed 1,000, cap dropped to 20%. The backlog was growing at about 170 segments a minute, roughly 45 MB/s of WAL.
- **Minutes 0-20:** pgbench stepped down with each tier: a 22,000 TPS burst at the start, 12,800 under the 80% cap, 11,800 under 50%, 9,600 under 20%.
- **Minute 20:** the "object storage" recovered with the backlog at its peak, 3,433 segments, 53 GiB of retained WAL.
- **Minutes 20-23.7:** the immune archiver drained about 850 segments a minute at full disk speed while the workload kept running under its cap.
- **Minute 23.8:** backlog back under 100; the timer removed the throttle on its next pass, and the count hit zero moments later. pgbench settled at 12,200 TPS with the archiver keeping pace.
- **Throughout:** the data disk never passed 33% full, and no human was involved at any point.

![WAL archival backlog through the incident](https://clickhouse.com/uploads/backlog_timeline_42c2112da9.png)

![pgbench throughput as the tiers engage](https://clickhouse.com/uploads/tps_timeline_39d8f01c1d.png)

The classification is visible in the cgroup filesystem. Ten minutes in, the immune group holds exactly the drain path, sorted there by process title, including the `archive_command` children the archiver spawned. The 48 client backends sit in the throttled group, and the literal `io.max` shows the 20% cap applies to writes only:


```text
== immune ==
4679  /usr/lib/postgresql/16/bin/postgres -D /dat/16/data
4680  postgres: 16/main: checkpointer
4681  postgres: 16/main: background writer
4683  postgres: 16/main: walwriter
4685  postgres: 16/main: archiver archiving 00000001000000000000009E
8354  pv -q -L 4m pg_wal/00000001000000000000009E

== throttled ==
4684  postgres: 16/main: autovacuum launcher
4973  postgres: 16/main: postgres bench [local] COMMIT
4974  postgres: 16/main: postgres bench [local] COMMIT
      ... 46 more client backends ...

$ cat throttled/io.max
259:1 rbps=max wbps=104857600 riops=max wiops=max
```

One caveat in this run, this workload's bytes are almost entirely WAL, and commits ride through the immune WAL writer, so the caps cut throughput much harder than they cut WAL production, which fell only about 10%. The throttle buys time against the disk; how much depends on how data-heavy the writes are.

## The takeaway

A few minutes of slower workload buys an instance that never writes itself to death. The tiers engage exactly at their thresholds, the drain path runs at full speed through the whole incident, and the cap releases itself the moment the backlog clears. Every ClickHouse Managed Postgres server ships with this by default.


---

## Try Postgres managed by ClickHouse

ClickHouse + Postgres has become the unified data stack for applications that scale. With Managed Postgres now available in ClickHouse Cloud, this stack is a day-1 decision.

[Sign up](https://clickhouse.com/cloud/postgres?loc=blog-cta-1473-try-postgres-managed-by-clickhouse-sign-up&utm_blogctaid=1473)

---