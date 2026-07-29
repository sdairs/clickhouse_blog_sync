---
title: "Why strict memory overcommit matters for Postgres"
date: "2026-07-28T16:14:42.628Z"
author: "Kaushik Iska"
category: "Engineering"
excerpt: "Why ClickHouse Managed Postgres runs strict memory overcommit by default, and how it turns an instance-wide OOM restart into a single failed query — shown side by side on identical hardware, with no measurable throughput cost."
---

# Why strict memory overcommit matters for Postgres

What is memory overcommit, and why does Postgres like for it to be strict? When a process calls `malloc`, Linux grants address space and attaches physical memory only when each page is first touched. The kernel's term for the granted space is a commitment, and overcommit is its policy of extending more commitments than the machine can back, since most allocations are never fully used. When touched pages exceed physical memory, the kernel invokes the OOM killer, which SIGKILLs a process to reclaim memory.

Postgres is unusually exposed to that policy. Every backend shares one memory segment holding shared buffers, WAL buffers, and lock tables, and a backend that dies by SIGKILL can leave that segment in an unknown state. The postmaster's only safe response is to assume corruption: it terminates every backend, drops every connection, and replays the WAL through crash recovery.

A single backend killed by the OOM killer mid-query therefore restarts the entire instance.

In ClickHouse Managed Postgres every server runs strict overcommit, `vm.overcommit_memory = 2`. The kernel tracks committed memory and refuses allocations past a commit limit, so the failure surfaces as `ENOMEM` from `malloc` before physical memory is exhausted. Postgres handles `ENOMEM` like any other error: the query fails with `out of memory`, the transaction rolls back, and the remaining connections keep working. This is the setting the Postgres documentation recommends in its chapter on kernel resources.

## Setting the commit limit

Strict overcommit is only useful if the limit is in the right place. Too high and the kernel still hands out more than it can back; too low and queries fail while memory sits free. Every server gets an explicit limit in kilobytes rather than the kernel's default ratio:

```
# /etc/sysctl.d/99-overcommit.conf
vm.overcommit_memory=2
vm.overcommit_kbytes=<computed from MemTotal>
```

The limit is 80% of the memory that is available for ordinary allocations, plus 2GB. Two details set the size of that first term.

The first is that a quarter of the machine is already reserved as huge pages for `shared_buffers`, and huge pages do not count toward the commit limit. Postgres maps that segment once at startup, outside the accounting the commit limit governs, so the limit is computed against the remaining 75% of RAM rather than the whole machine.

The second is the 80%: what remains has to cover the kernel itself, page tables, the page cache, and every per-backend allocation Postgres makes at runtime, so the limit deliberately stops short of the memory that is actually there. The 2GB on top is headroom for the sidecar processes that share the box with Postgres, the backup agent and the metrics exporters.

The result is a commit limit of roughly 60% of total RAM plus 2GB, and a kernel that starts returning `ENOMEM` while several gigabytes are still physically free. That gap is the point. The error arrives while there is still memory available to handle the error.

---

## Get started with ClickHouse Managed Postgres today

Interested in seeing how ClickHouse Managed Postgres works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?intent=pg&loc=blog-cta-1425-get-started-with-clickhouse-managed-postgres-today-sign-up&utm_blogctaid=1425)

---


## Seeing it on real hardware

We put both policies on a single EC2 box: an `m7i.2xlarge` (8 vCPU, 30.8GiB), Postgres 16 with a quarter of memory reserved as 2MB huge pages and `shared_buffers = 6864MB` mapped onto that pool, and a 3GB pgbench dataset. Of the 30.8GiB, the huge page pool takes 7.7GiB, which leaves 23.1GiB for everything else. The production formula puts the strict commit limit at 20.5GiB, about 2.6GiB below what the machine can physically hand out.

The workload is the same in both arms. Twenty idle sessions stay connected as bystanders, a client opens a fresh connection every 0.3 seconds to see whether the server is reachable, and then sessions arrive one at a time, each building about 2GB of in-memory arrays and holding it. Nothing about the query is exotic: it is an ordinary aggregate over `generate_series` that happens to be large, the shape of a query that sorts or aggregates more than anyone expected. Sessions keep arriving until the run ends itself. The only variable between the two arms is `vm.overcommit_memory`.

![postgres_overcommit_jul2026_image2.png](https://clickhouse.com/uploads/postgres_overcommit_jul2026_image2_54dec0104b.png)

Under the kernel's default policy, committed memory climbs straight through the limit the kernel itself reports. `CommitLimit` on this box reads 11.6GiB, and committed memory passed it at the sixth session and kept going to 23.6GiB, more than double, because under `vm.overcommit_memory = 0` that limit is advisory and the kernel only applies a loose heuristic per allocation. Twenty-four seconds into the ramp, with 1.3GB left available, the twelfth session touched a page the machine could not back and the OOM killer chose the largest resident process, a backend holding 2.4GB:

```
Out of memory: Killed process 21268 (postgres) total-vm:9779160kB, anon-rss:2480672kB, oom_score_adj:0
```

What Postgres does next is in the server log, and it is not scoped to the session that asked for too much:

```
22:13:30.507 LOG:  server process (PID 21268) was terminated by signal 9: Killed
22:13:30.509 LOG:  terminating any other active server processes
22:13:30.604 FATAL:  the database system is in recovery mode
22:13:30.808 LOG:  all server processes terminated; reinitializing
22:13:30.876 LOG:  database system was not properly shut down; automatic recovery in progress
22:13:30.886 LOG:  redo starts at 3/592F5160
22:14:00.699 LOG:  checkpoint complete: wrote 239686 buffers (27.3%); ... distance=1964319 kB
22:14:00.703 LOG:  database system is ready to accept connections
```

All twenty bystander sessions were dropped. They had no relationship to the memory-hungry query beyond sharing an instance with it. The write load before the ramp had left 1.9GB of WAL since the last checkpoint, and getting through it, redo followed by a checkpoint that wrote 27% of the buffer cache, took the server out of service for 30.2 seconds. A client attempting a fresh connection every 0.3 seconds measured the same window the timestamps show. The kernel's choice of victim is not confined to Postgres either: the same OOM event killed the login session's `systemd` and `(sd-pam)`, which ended the SSH session running the test.

Under strict overcommit, the same ramp on the same box stops earlier and much more quietly. Committed memory rose to 19.8GiB and stopped there, against the enforced limit of 20.5GiB. At 20.4 seconds the tenth session asked for another 500MB, and the kernel refused:

```
ERROR:  out of memory
DETAIL:  Failed on request of size 502000072 in memory context "SPI TupTable".
CONTEXT:  SQL statement "SELECT array_agg(repeat('x', 1000)) FROM generate_series(1, 500000) g"
```

That is the entire failure. One query received an error, its transaction rolled back, and its memory was released. The nine sessions that had already claimed their 2GB kept it. All twenty bystanders stayed connected, every one of the new-connection probes succeeded, and the kernel logged no OOM kill at all. At the moment of refusal 3.8GB were still available, which is what makes the difference: Postgres was told no while it still had the memory to report the error, roll back, and carry on.

|  | default policy | strict overcommit |
| :---- | ----: | ----: |
| Commit limit | 11.6GiB, advisory | 20.5GiB, enforced |
| Peak committed memory | 23.6GiB | 19.8GiB |
| Memory still available at the failure | 1.3GB | 3.8GB |
| How it failed | SIGKILL of a backend | `ERROR: out of memory` |
| Sessions affected | 20 of 20 dropped | 1 query, 0 sessions dropped |
| Unable to serve a new connection | 30.2s | 0s |

![postgres_overcommit_jul2026_image3.png](https://clickhouse.com/uploads/postgres_overcommit_jul2026_image3_3ad6ddbb15.png)

The last question is what the policy costs when nothing is failing. `vm.overcommit_memory` is a runtime kernel setting, so the two arms can be compared without restarting Postgres, keeping `shared_buffers`, the page cache, and every backend identical between measurements; the arms are interleaved and repeated so that cache warmth and table bloat land on both equally.

![postgres_overcommit_jul2026_image1.png](https://clickhouse.com/uploads/postgres_overcommit_jul2026_image1_98ce211640.png)

Neither workload separates the two policies. Select-only ran at 216,606 transactions/sec under the default policy and 211,882 under strict, a 2.2% difference against a run-to-run spread of 4 to 5% within each arm. Read-write ran at 15,790 and 15,878, a 0.6% difference. Strict overcommit changes what the kernel promises, and the accounting it does to keep that promise costs nothing a benchmark on this box can distinguish from noise.

Two notes on the honesty of that last comparison. Read-write throughput on a freshly loaded dataset climbed from 12,800 to 15,800 transactions/sec before settling, so the read-write numbers above come from a second pass taken after it plateaued; the first pass measures warm-up rather than policy. That pass also runs the arms in `default, strict, strict, default` order, because a fixed order lets whatever drift is left accumulate in favour of whichever arm goes second.

## The takeaway

Memory exhaustion is not a question of whether but of when, and the policy in place decides what it costs. Under the kernel's default policy the cost is a SIGKILL, an instance-wide restart, and every connected client dropped. Under strict overcommit, sized against the memory a Postgres box actually has available, the cost is one error on one query while every other session keeps working.

Every ClickHouse Managed Postgres server ships with strict overcommit by default. Provision a Postgres and see it in action: [https://clickhouse.com/cloud/postgres](https://clickhouse.com/cloud/postgres)   



