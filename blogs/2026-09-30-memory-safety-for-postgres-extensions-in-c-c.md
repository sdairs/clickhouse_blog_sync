---
title: "Memory safety for Postgres extensions in C/C++"
date: "2026-09-30T13:56:27.997Z"
author: "Philip Dubé"
category: "Engineering"
excerpt: "How ClickHouse’s Postgres extensions handle the memory safety challenges of combining C and C++, from clean language boundaries to isolated helper processes."
---

# Memory safety for Postgres extensions in C/C++

We’ve developed a few postgres extensions at ClickHouse:

* [pg_clickhouse](https://clickhouse.com/blog/introducing-pg_clickhouse) (clickhouse fdw)  
* [pg_re2](https://clickhouse.com/blog/introducing-pg_re2-regex-in-postgres) (integrates re2, the same regex engine used by ClickHouse, into postgres)  
* [pg_chdb](https://clickhouse.com/blog/introducing-chdb-postgres) (ClickHouse object storage capabilities for COPY in postgres)  
* [pg_stat_ch](https://clickhouse.com/blog/pg_stat_ch-postgres-extension-stats-to-clickhouse) (ships metrics & logs)

All of these involved bringing C++ into a Postgres extension. Postgres is C. Surely C & C++ play nice together, right?

No. Postgres has its own memory allocation pattern built around [MemoryContext](https://www.cybertec-postgresql.com/en/memory-context-for-postgresql-memory-management/). Instead of using malloc/free, one should use palloc/pfree. These functions associate allocations with a MemoryContext, which can work as an [arena allocator](https://en.wikipedia.org/wiki/Region-based_memory_management) freeing everything at the end of a transaction or aggregate or what have you. MemoryContexts can also have callbacks to act as destructors. Postgres handles failed memory allocations by raising an error, for which it has a whole PG_TRY/PG_CATCH/PG_FINALLY macro package built on [setjmp/longjmp](https://en.cppreference.com/c/program/setjmp). PG_FINALLY is another method of building [RAII](https://en.wikipedia.org/wiki/Resource_acquisition_is_initialization)-like destructor logic.

C++ code on the other hand tends to use new/delete, which invokes constructors/destructors, & raises [std::bad_alloc](https://en.cppreference.com/cpp/memory/new/bad_alloc) on failed allocation. These two systems do not interact well: setjmp/longjmp skips C++ cleanup; jumping past nontrivial destructors for automatic objects is [undefined behavior](https://eel.is/c++draft/csetjmp.syn), not merely a leak. PG_FINALLY and MemoryContext callbacks do not make such a jump safe. Exceptions bypass PG_CATCH/PG_FINALLY. Worse, an uncaught exception causes the process to abort, which even in a background worker will lead to the Postgres postmaster process having to restart everything in fear that shared memory has been corrupted.

Each of these extensions took a different strategy around memory safety.

## pg_clickhouse {#pg_clickhouse}

For pg_clickhouse we have completely eradicated the use of C++. This involved replacing [clickhouse-cpp](https://github.com/clickhouse/clickhouse-cpp) with an entirely new C library, [clickhouse-c](https://github.com/ClickHouse/clickhouse-c), which we recently wrapped in another library, [pg-clickhouse-c](https://github.com/ClickHouse/pg-clickhouse-c), in order to consolidate postgres logic while keeping clickhouse-c a general-purpose library. clickhouse-c was designed to be transport-agnostic, supporting [Native](https://clickhouse.com/docs/reference/formats/Native) format outside Native protocol, so now the HTTP driver shares much of its decoding/encoding logic with the binary driver by using Native format over HTTP. For HTTP we use libcurl, which offers a low level enough interface to play nice with Postgres's environment.

For example, previously in `binary.cpp`, `make_datum` converted a ClickHouse String with:

```cpp
auto s = std::string(col->AsStrict<ColumnString>()->At(row));
ret = PointerGetDatum(cstring_to_text_with_len(s.data(), s.size()));
```

`cstring_to_text_with_len` allocates a Postgres text value with `palloc`. If that allocation fails, Postgres raises ERROR and jumps to its error handler, bypassing `s`'s destructor. Surrounding C++ try/catch cannot catch this jump.

## pg_re2 {#pg_re2}

For pg_re2 C++ is scoped to [re2_wrapper.cpp](https://github.com/ClickHouse/pg_re2/blob/main/src/re2_wrapper.cpp). All C++ allocations happen within C++ try/catch, & it doesn't call into postgres C code. Separation of concerns is sufficient for this encapsulation to draw a clean line between the two systems.

## pg_chdb {#pg_chdb}

pg_chdb reuses pg-clickhouse-c for decoding/encoding native blocks. Originally it loaded [libchdb](https://clickhouse.com/docs/chdb/) into the background worker, but eventually moved libchdb into a separate helper executable. Isolating libchdb is the point: its C++ runtime, threads, allocations, and failures live outside a Postgres backend or managed background worker. The backend forks and execs this helper, so it remains a descendant of postmaster, but postmaster does not manage it as a background worker. This helper only needs enough information to run a ClickHouse query & exchange Native blocks, so it has no need for postgres headers. A libchdb crash can then fail the calling operation without itself triggering Postgres cluster crash recovery.

## pg_stat_ch {#pg_stat_ch}

pg_stat_ch relies on OpenTelemetry libraries & [Arrow's C++ bindings](https://arrow.apache.org/docs/cpp/), as [nanoarrow](https://arrow.apache.org/nanoarrow/latest/) lacks many IPC features. C++ code is isolated to a Postgres background worker which we then instrument with C++ exception handling & PG exception handling. A terminate handler routes uncaught exceptions / std::terminate through `ereport(FATAL)` instead of default `abort()` / SIGABRT. FATAL normally runs Postgres process-exit cleanup and exits with status 1. Postmaster accepts this as a non-crash exit if shared-memory detachment also completes cleanly; worker restart then follows `bgw_restart_time`. By contrast, abnormal worker termination can trigger cluster-wide crash recovery and disconnect other sessions.

This is a mitigation, not a general crash-isolation guarantee. FATAL cannot repair inconsistent shared memory, and failed cleanup can still make postmaster treat exit as a crash. A process-wide terminate handler also needs scrutiny if invoked by a library thread: it does not make Postgres error handling and exit callbacks safe to call from arbitrary threads.

Writing this blog exposed a concrete ownership problem, addressed in [PR #126](https://github.com/ClickHouse/pg_stat_ch/pull/126): an interrupted dequeue could leave a slot pointing to already-freed error text or already-released query text. Recovery retries the slot before tail advances, potentially freeing or releasing the same reference twice. Long term moving C++ dependencies into a helper executable, as done in pg_chdb, will further harden pg_stat_ch. [PR #129](https://github.com/ClickHouse/pg_stat_ch/pull/129) is the first step: isolate C++ in `src/exporter` with no Postgres dependency and let `bgworker.c` handle the C/C++ boundary.


---

## Get started today

Interested in seeing how ClickHouse works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-2463-get-started-today-sign-up&utm_blogctaid=2463)

---