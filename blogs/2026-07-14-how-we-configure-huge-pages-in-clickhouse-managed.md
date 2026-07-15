---
title: "How we configure huge pages in ClickHouse Managed Postgres"
date: "2026-07-14T14:59:25.235Z"
author: "Kaushik Iska"
category: "Engineering"
excerpt: "How ClickHouse Managed Postgres reserves, enforces, and sizes huge pages so shared_buffers avoids the per-connection page-table tax that eats RAM and stalls reads on 4KB pages."
---

# How we configure huge pages in ClickHouse Managed Postgres

What are huge pages, and why do they matter for Postgres? The OS hands out memory in 4KB pages, and the CPU keeps a small cache of virtual-to-physical translations, the TLB. A huge page is the same memory in much bigger units, 2MB or 1GB, so one page-table entry covers up to 262,144x more ground.

Postgres is unusually sensitive to page size. Its cache, shared_buffers, is one big shared-memory segment, and every backend process maps it through its own page tables. At 4KB pages, a 100GB cache costs each backend about 200MB of page-table entries, so 100 connections burns 20GB of RAM on page tables alone; with 2MB huge pages, tens of MB. And a TLB holds a few thousand translations, which covers just a few MB of that cache at 4KB, so each 2MB page gives a slot 512x the reach, the hot working set stays in the TLB, and reads stop stalling on page-table walks.

In ClickHouse Managed Postgres every server runs its buffer cache on huge pages. Getting that to hold reliably takes three pieces: reserving the pages early, refusing to run without them, and sizing shared_buffers so the whole shared memory segment lands on the reserved pool exactly.

![](https://clickhouse.com/uploads/hugepages_postgres_jul2026_image1_e990803005.png)

## Reserving the pages {#reserving_the_pages}

A quarter of the machine's memory is reserved as huge pages, mirroring the `shared_buffers` = 25% of RAM rule in the base configuration. The reservation runs before Postgres ever starts, and it flushes caches and compacts memory first so the kernel can still find contiguous 2MB blocks:

<pre><code type='click-ui' language='bash'>
echo 'vm.nr_hugepages = <target>' > /etc/sysctl.d/10-hugepages.conf
sync
echo 3 > /proc/sys/vm/drop_caches
echo 1 > /proc/sys/vm/compact_memory
sysctl --system
</code></pre>

The allocation is then verified against `HugePages_Total` in `/proc/meminfo`, and provisioning fails if the kernel comes up short. Huge pages can only be reserved reliably while memory is unfragmented; on a machine that has been under load, the same request routinely fails.

## Refusing to run without them {#refusing_to_run_without_them}

Postgres is pinned to `huge_pages = 'on'`, so it either gets its pages or refuses to start. The default, `'try'`, silently falls back to 4KB pages with nothing in the logs, and every property described above quietly disappears. A refusal at startup is diagnosable; a silent fallback is discovered months later, usually by a profiler.

There is a runtime check, too. The postmaster's `/proc/<pid>/status` records how much of its address space sits on hugetlb pages; on the demo box below it reads:

<pre><code type='click-ui' language='bash'>
$ grep HugetlbPages /proc/<postmaster pid>/status
HugetlbPages:   700416 kB
</code></pre>

`HugetlbPages: 0` on a server that should be using huge pages means the fallback happened.

## Sizing shared_buffers to the page {#sizing_shared_buffers_to_the_page}

Postgres's shared memory segment is bigger than shared_buffers: it also carries buffer descriptors, WAL buffers, and lock tables. On the demo box below, `shared_buffers = 32GB` produces a 32.75GB segment, about 750MB of overhead. If shared_buffers alone filled the reserved pool, the full segment would not fit, and `'on'` would refuse to boot. The sizing works in two passes. First point shared_buffers at the entire pool, then ask the binary what the full segment would actually cost, without starting the server:

<pre><code type='click-ui' language='bash'>
postgres -D <datadir> -C shared_memory_size
</code></pre>

Subtract the difference back out of shared_buffers, round down to whole 8KB blocks, and write the result:

<pre><code type='click-ui' language='bash'>
# conf.d/002-hugepages.conf
huge_pages = 'on'
huge_page_size = 0        # use the system default, 2MB
shared_buffers = <measured fit>kB
</code></pre>

The overhead is measured rather than assumed because it shifts with version and settings, and measuring at the larger size errs a few pages under the reservation. The reserved pool and the rest of memory are then accounted separately: huge pages do not count toward the kernel's commit limit, so memory overcommit is tuned against the remaining 75% of RAM.

## Seeing it on real hardware {#seeing_it_on_real_hardware}

We put the claim about page tables on a single EC2 box: an `r7i.4xlarge` (16 vCPU, 128GB), Postgres 16 with `shared_buffers = 32GB`, and a pgbench dataset whose 15.6GB accounts table is loaded fully into the cache with `pg_prewarm`. Each test connection then runs one full sequential scan of that table, which makes its backend touch every cached page and build its complete page-table mapping, and holds the connection open. We sampled the kernel's `PageTables` counter from `/proc/meminfo` at 25, 50, 100, and 200 connections, once with 4KB pages and once with 2MB huge pages. Same box, same data, same access pattern; the only variable is the page size.

![](https://clickhouse.com/uploads/hugepages_postgres_jul2026_image2_d02cfccbc0.png)

With 4KB pages, page tables grow by 31.1MB per connection, matching the arithmetic (15.6GB of touched cache / 4KB pages x 8 bytes per entry = 31.2MB), and reach 6.1GB at 200 connections, kernel memory spent on bookkeeping for 15.6GB of data. With 2MB huge pages the same 200 connections cost 111MB, about 0.5MB per connection.

| Connections | PageTables, 4KB | PageTables, 2MB huge pages |
| ----: | ----: | ----: |
| 0 | 48 MB | 5 MB |
| 25 | 789 MB | 18 MB |
| 50 | 1.53 GB | 31 MB |
| 100 | 3.06 GB | 58 MB |
| 200 | 6.12 GB | 111 MB |

The `huge_pages = 'on'` behavior is equally visible. With no pool reserved, Postgres refuses to start and says why:

<pre><code type='click-ui' language='bash'>
FATAL:  could not map anonymous shared memory: Cannot allocate memory
HINT:  This error usually means that PostgreSQL's request for a shared
memory segment exceeded available memory, swap space, or huge pages.
</code></pre>

Throughput moves too, though less dramatically than the memory: select-only pgbench at 100 clients ran 373,083 TPS on 4KB pages and 418,087 TPS on 2MB huge pages, a 12% difference on an otherwise identical box. The structural change is in the memory: page tables that scale linearly with connections versus page tables that stay flat.

## The takeaway {#the_takeaway}

Huge pages turn shared_buffers from a per-connection page-table tax into a flat, translation-friendly cache. Reserving the pool before fragmentation, running `huge_pages = 'on'` so a broken setup fails at boot instead of degrading silently, and sizing the segment to the reservation with the numbers the postgres binary itself reports are what make the configuration hold in production rather than only on a fresh box.

---

## Try Postgres managed by ClickHouse

ClickHouse + Postgres has become the unified data stack for applications that scale. With Managed Postgres now available in ClickHouse Cloud, this stack is a day-1 decision.

[Sign up](https://clickhouse.com/cloud/postgres?loc=blog-cta-1323-try-postgres-managed-by-clickhouse-sign-up&utm_blogctaid=1323)

---