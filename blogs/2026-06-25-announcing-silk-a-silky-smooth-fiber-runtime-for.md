---
title: "Announcing Silk: a silky smooth fiber runtime for ClickHouse"
date: "2026-06-25T19:37:21.023Z"
author: "James Cunningham and Vadim Skipin"
category: "Engineering"
excerpt: "Silk is a new open-source C++ fiber runtime built for ClickHouse, combining a NUMA-aware work-stealing scheduler, io_uring I/O, and zero heap allocation in the steady state to deliver nanosecond-level fiber yields and dramatically lower tail latency for h"
---

# Announcing Silk: a silky smooth fiber runtime for ClickHouse

## TL;DR {#tldr}

*Silk is a stackful-fiber library and scheduler with a NUMA-aware work-stealing loop, io_uring as the I/O ground truth, and zero heap allocation in the steady-state hot path. We built it for ClickHouse, and the first place we aim to integrate it is in our distributed cache.*

## What are fibers? What is Silk? {#what-are-fibers-what-is-silk}

Fibers are a lightweight user-space execution unit, somewhat like threads. Unlike threads, fibers participate in cooperative multitasking instead of the preemptive multitasking that threads use; allowing fibers to yield their work instead of block on it. This particular behavior is best suited for asynchronous I/O, which is becoming more of a bottleneck in distributed systems as CPUs grow faster and clusters grow larger.

Unlike threads, fibers do not have a rich ecosystem of language support, which is why we created Silk. Silk is a C++ library that gives you a cooperative fiber scheduler, backed by a per-CPU scheduler that uses `io_uring` for asynchronous I/O and steals work between cores when local queues run dry. It is exceptional at executing high-concurrency networking I/O (hint hint: ClickHouse) and also at high-currency file I/O (surprise surprise: also ClickHouse).

The name is a homage to Cilk, the 1994 MIT work-stealing scheduler whose name was itself a portmanteau of "silk" plus C. Silk is meant to position itself in that lineage. The fiber-as-silk-thread metaphor is a side benefit.

What made us write a runtime rather than reach for an existing one off the shelf is the combination of properties we needed from it:

1. A fiber that yields in tens of nanoseconds
2. Work stealing that respects CPU topology
3. No heap allocation in the steady state
4. `io_uring` treated as the I/O ground truth rather than as a backend bolted onto an older reactor design.

None of the off-the-shelf options gets all four. So we wrote one that does, and we ship it with the harness, GDB extension, and BPF profiler that proves we aim to depend on it in ClickHouse.

## Why fibers, why these fibers, and why now? {#why-fibers-why-these-fibers-and-why-now}

ClickHouse already has a concurrency model, and it works. It's the right model for the parts of the engine that look like query execution: long-running threads doing real CPU work, where the per-thread overhead is amortized over millions of rows of computation.

Yet, we need silk for the rest of the engine. If you trace a query through ClickHouse Cloud, increasingly the long pole is not "a thread did a lot of computation," it is "ten thousand tiny operations completed in a particular order, and the slowest of them shaped the tail." This takes an aim at increasing the performance of object-storage I/O, distributed cache lookups, replica coordination, HTTP fan-out. All components that are I/O-bound, highly concurrent, and decided at the 99th and 99.9th percentile. They are exactly the workloads where the cost of one in-flight request is supposed to be a stack pointer, not a kernel thread.

The argument for stackful fibers, over OS threads or stackless C++20 coroutines, is essentially this: OS threads are too expensive to use as the primary unit of concurrency in a database engine. A few microseconds per context switch, kilobytes of stack, and a finite number of them before the kernel starts context-switching itself to death. Stackless coroutines are cheap but viral: every function on a suspension path has to be marked `co_await`-able, and the compiler's heap allocation elision optimization (HALO) reliably stops firing the moment the coroutine handle escapes to a real scheduler queue. Stackful fibers give you cheap suspension without the language footprint: any function can yield and the stack is a normal stack.

The historical objection to stackful fibers, dating back to the Photon paper from Alibaba, is cache aliasing: fibers allocated from a slab can have stacks that map to the same L1 cache lines, producing pathological eviction. The Photon paper measured a 13% scheduler-level cost from this. Silk's response is that the problem is a property of slab-allocated stacks specifically, not of stackful fibers in general. Each fiber's stack is `mmap`'d from a per-fiber pool with guard pages on either side. There is no slab and no aliasing. The 13% cost does not appear in our benchmarks, because the precondition for it does not exist.

What silk delivers, by its own benchmarks against the field, is roughly the following:

- About 3.6 nanoseconds per fiber yield with cross-CPU work stealing
- About 7.6 microseconds for an `io_uring` ping-pong
- 5.9 million file IOPS at a working configuration
- Roughly fifteen times the throughput of `boost::asio` at one connection, and roughly four times at high concurrency
- Per-CPU lock-free stack performance up to 2068x faster than a global lock-free stack at 32 threads, via `rseq`

Want to test these numbers yourself? They come from a benchmark harness in the repository (`./bb`) that runs the exact same workloads through silk and the comparison tool, with controlled CPU pinning, fixed warmup periods, percentile tracking, and JSON output that anyone can re-run and verify. The methodology is the strongest single aspect of how silk presents itself.

## How does Silk work? {#how-does-silk-work}

The scheduler runs one OS thread per CPU, pinned. Each scheduler thread owns a per-CPU `ProcessorState` containing a bounded ready queue (a Vyukov MPMC queue with cache-line-aligned producer/consumer slots), an `io_uring` ring for asynchronous I/O and timer expiry, a sleep tree ordered by deadline, and an eventfd that doubles as a wakeup doorbell. Every fiber-bearing operation (submitting an I/O, waking a waiter, scheduling a new fiber) happens on the CPU that originated it whenever possible. When a CPU's ready queue is empty, the scheduler thread wakes via a persistent `IORING_OP_POLL_ADD_MULTI` on the eventfd and runs a service loop that drains its CQ ring, processes expired sleeps, and looks for work to steal.

Work stealing is topology-aware. At startup, silk reads the system's CPU topology from `/sys` and builds a steal-candidate list per CPU, sorted by estimated cost: hyperthread siblings first (about a microsecond), same-socket cores next (about fifty microseconds), and cross-socket cores last (about five hundred microseconds). When a CPU steals, it walks its candidate list in cost order, with random shuffling within each cost tier to avoid hot-spotting. This technique is a concrete realization of a "NUMA-aware" scheduler, it's not just "we have separate queues," it's "we know which CPUs are cheap to steal from and prefer them."

Topology-aware scheduling aside, silk has another important performant property: **the steady-state runtime does no heap allocation.** Fiber stacks come from a pool that is `mmap`'d at init and never freed. `FiberFuture`, `IoFuture`, `SleepFuture`, and `MultipleWaitState` all live on the caller's stack; the `outstandingCount` accounting in `waitForMultiple` exists precisely because the state is on the stack and the function must not return until all in-flight signals have completed. Every container is intrusive: the queue node, suspended-list entry, lock-free-stack hook, and waiter-table hook are *fields inside the `Fiber` object itself*, not separate allocations. A fiber can be enqueued in three different containers simultaneously and the cost is zero additional bytes of heap. The same applies to `SleepFuture`, which carries its own `StackEntry` and `TreeEntry` fields for the cancel queue and the deadline-ordered tree. After init, the hot path does no allocation at all. Not less than other libraries, zero.

The last important performant property we shipped silk with: `boost::asio` allocating per async operation. C++20 stackless coroutines allocate per coroutine frame on the heap unless HALO fires (which usually doesn't happen with a real scheduler). Among production-grade general-purpose async runtimes, the property of zero hot-path allocation belongs almost exclusively to systems engineered for real-time use: DPDK, Seastar, or parts of the Linux kernel itself. Silk is in that category as a deliberate design choice, and the consequence is that it can be deployed in places where allocator behavior is part of the SLA: query execution under memory pressure, kernel-bypass paths, or latency-sensitive hot loops where a `malloc` on the wrong page fault means a missed deadline. All key hotspots of a highly performant distributed database.

## What are some of the design choices? {#what-are-some-of-the-design-choices}

**The synchronization primitives are textbook in shape.** The `FiberFuture` packed-state pattern, the `FiberSequencer` flat-combining loop, and the `FiberMutex` lock-and-flag race-handling are each canonical implementations of patterns that go wrong in subtle ways more often than they're done right. Every memory fence has a paired counterparty. Every CAS uses the strictest necessary ordering and no stronger.

**HALO does not fire with schedulers that handle production workloads.** The standard pitch for C++20 stackless coroutines is "zero overhead because of HALO." HALO requires the coroutine handle never to escape to a scheduler queue. Every real scheduler violates that condition, so the "zero overhead" claim holds for synthetic benchmarks where the scheduler is trivial and breaks for real applications where the scheduler bears real load.

**The race-handling for park-then-wake is the key to throughput.** Every primitive that suspends a fiber has the same shape: optimistically attempt the operation; on failure, set a flag indicating waiters exist; suspend the fiber via a callback that runs after the fiber has fully parked; in the callback, register the fiber as a waiter and re-check for missed wakeups. Once you have read it carefully in `FiberFuture`, the futex, the mutex, and the sequencer all read fast.

**The whole synchronization layer is one pattern.** When you can implement six synchronization primitives in 700 lines because they are all variations on "packed state plus flag CAS plus queue or table plus suspend callback that re-checks," you have found the right abstraction. The construction of the library had each primitive deliberately built on top of the previous one. Six primitives, two patterns, one underlying suspend-callback contract.

**The public API is small.** There are a total of eight verbs in `FiberScheduler`: initialize, destroy, run, schedule, yield, suspend, enqueue/release waiters, and the I/O primitives. The header is under 400 lines and reads like API reference documentation. Stackful state is treated as an implementation detail, not as something the user composes around.

**The benchmarks are reproducible.** Every comparison is apples-to-apples and every run is reproducible from one command. The silk-vs-asio comparison is silk against asio's *better* configuration: enabling asio's io_uring backend made it slower, not faster. The silk-vs-fio comparison is silk against fio's `--ioengine=io_uring`, not against `psync`.

**The operational tooling is as serious as the code.** A working GDB extension that handles both x86_64 and aarch64, with frame layouts pulled from the Boost.Context assembly source files. A BPF profiler with on-CPU and off-CPU sampling, capability-gated for unprivileged use. A benchmark harness that runs comparisons against the reference tool for each workload (asio for network I/O, fio for file I/O, sockperf for TCP latency, nginx for HTTP). The GDB extension has its own integration test in CTest. We want to ship a library that is useful outside of our own authors.

**This is the cache-aliasing rebuttal of Photon.** The Photon paper has been circulating as the standard "stackful fibers are slow" reference for years. The argument that the 13% scheduler-level miss rate it measured is an artifact of slab-allocated stacks, not of stackful fibers per se, and that mmap-from-pool with guard pages sidesteps it entirely, has not been published in the form silk presents it. The benchmarks back it up: silk's per-yield cost is in the nanoseconds, not the microseconds you would expect from a 13% miss-rate runtime.

## Ok, but it's not perfect, right? {#ok-but-its-not-perfect-right}

While we're proud of what we've authored, we can acknowledge limitations and constraints.

First and foremost, Silk is Linux-only. It depends on io_uring, eventfd, mmap with guard pages, rseq, and the modern Linux capability model. There is no portability layer for macOS, Windows, or older kernels. This is a deliberate scope choice, as the target is server-class Linux, and supporting kqueue or IOCP would double the surface for a use case the team does not have.

Second, the scheduler is a process-wide singleton, accessed via static methods on `FiberScheduler`. There is no way to instantiate two isolated schedulers in the same process. This makes the API ergonomic but rules out testing scenarios and advanced usage like "one scheduler for latency-critical work, one for batch." We deliberately kept multi-scheduling out of the library's current scope; as it would be a breaking API change to add later.

Third, the fiber API requires entry-point parameters to fit in 64 bytes (`FIBER_PARAMETERS_SIZE`). Larger payloads need to be heap-allocated and passed by pointer. This avoids per-fiber allocation churn for the common case but is a real constraint that surfaces at compile time via `static_assert`.

And last but not least, the profiler shipping with the library is, in its current form, a generic on-CPU and off-CPU sampling profiler. It's useful, but not yet aware of fiber identity, though per-fiber attribution is on our roadmap. The architectural foundation is in place: silk knows which fiber is running on each thread (via `threadFiber` TLS), the GDB extension already demonstrates that suspended fiber stacks can be walked from outside, and the BPF profiler is structured for incremental probe additions. What's missing is the BPF program updates to read the TLS, plus probably one or two USDT probes at the suspend/resume boundary.

## Where will ClickHouse utilize this first? {#where-will-clickhouse-utilize-this-first}

While we have many places where fibers can increase our performance, the first probable target is our [**distributed cache**](https://clickhouse.com/blog/building-a-distributed-cache-for-s3). It is network-bound and high-fan-out, having a possibility of a single query touching hundreds of cache nodes. It is tail-latency-sensitive in the way that decides query latency. Every cache request maps cleanly to a single fiber: fan in, do io_uring reads, fan out, return. The I/O is io_uring-shaped already, and the working set is dominated by short-lived requests rather than long-running query work, so silk's steady-state zero-allocation property is most visible exactly here. We expect the largest visible wins to be in the tail: the 99th and 99.9th percentiles, where OS scheduler jitter and allocator pauses under thousands of concurrent threads are the dominant contributors, and where silk's per-CPU pinning and zero hot-path allocation give the kernel and the allocator nothing to flinch at. We have already seen this shape on internal benchmarks: at ten thousand concurrent S3-style requests, the fiber executor's 99.9th percentile is roughly 65% better than the equivalent thread-pool executor, even when median throughput is identical and MinIO is the bottleneck on both. Distributed cache is where silk runs smoothest first; the rest of the engine is on a separate timeline, and we will write about each integration as it lands.

## Where can I see more? {#where-can-i-see-more}

Silk is published at [github.com/ClickHouse/silk](http://github.com/ClickHouse/silk). The repository contains the library, the benchmark harness, the GDB extension, the BPF profiler, and four documents worth opening first: [`docs/scheduler.md`](https://github.com/ClickHouse/silk/blob/main/docs/scheduler.md), [`docs/sync.md`](https://github.com/ClickHouse/silk/blob/main/docs/sync.md), [`docs/coroutines.md`](https://github.com/ClickHouse/silk/blob/main/docs/coroutines.md), and [`docs/perf.md`](https://github.com/ClickHouse/silk/blob/main/docs/perf.md). Every benchmark in this post is reproducible from a clean checkout. If you are working on a Linux server-class C++ system and the workload looks like high-concurrency I/O with strict tail-latency requirements (distributed caches, object-storage clients, RPC fabrics, HTTP fan-out), silk is in a state where it would value being kicked at. Read the docs, run the benchmarks, file issues. ClickHouse moves fast because the layers underneath it are precise. Silk is the next layer underneath, and it is the layer we needed.

Lastly, as we weave Silk into ClickHouse, we'll author more pieces about how it has increased performance. Be sure to stay tuned!

---

## Get started today

Interested in seeing how ClickHouse works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-1103-get-started-today-sign-up&utm_blogctaid=1103)

---