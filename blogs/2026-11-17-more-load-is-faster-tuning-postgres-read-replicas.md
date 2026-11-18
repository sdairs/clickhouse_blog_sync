---
title: "More load is faster: Tuning Postgres read replicas"
date: "2026-11-18T10:14:57.555Z"
author: "Colton Shepard"
category: "Engineering"
excerpt: "Testing Postgres read replicas reveals why more write traffic can reduce lag, how WAL settings affect latency, and where aggressive tuning introduces tradeoffs."
---

# More load is faster: Tuning Postgres read replicas

## TL;DR {#tldr}

* Replica lag is lower than conventional wisdom suggests out of the box if you have traffic, and pretty easy to get to a few seconds with basic tuning.   
* You can get some spectacularly short replica lag if you’re willing to be unreasonable or incur tradeoffs.   
* If you care a lot about read replica lag and want a relatively safe starting point for tuning, try `archive_timeout=5s` and `wal_retrieve_retry_interval=500ms`.  
* Some of these options can lead to high network bills with synchronous HA.

Sometimes, the simple problems are the ones that really surprise you. Recently, a user of ClickHouse Managed Postgres mentioned an issue with unexpectedly high read replica delay, and I took the chance to poke around. I quickly realized that Postgres has a lot of config options that I haven’t tested for a few major versions, and that some of what I’ve taken as well-known information is a bit out of date. I hope you’ll also be surprised by some of this. 

Read replicas are one of the classic pillars of any traditional relational database. If you’ve ever wanted to separate read traffic from write, or just wanted to scale reads, you’ve probably considered setting one up, and I’d bet that most readers of this blog have one in production somewhere. The way they work is fairly simple: you have a primary database that takes normal traffic, and mirror all of its updates to one or more read replicas that serve your non-updating traffic. 

There’s a few ways to set this up. The classic configuration is streaming replication, where changes are sent in (more or less) real time to the replicas, but it has some downsides we don’t like that I’ve detailed at the end of this blog. The other popular method, which we’ve chosen as the default on ClickHouse Managed Postgres, is to take advantage of the fact that we already collect WAL to use for our backups, and use it to keep the replica in sync. It’s somewhat slower, and since we can’t use `hot_standby_feedback` without a streaming connection, long running queries on the replica block replay until they complete or hit timeouts, but it’s a tradeoff we’re happy about. 

Unfortunately, Postgres likes to be efficient about switching WAL segments, which can lead to some unexpected behavior. With the default configs we ship, Postgres switches segments every 16MB of changes or 60 seconds, whichever comes first. We’ve found this to be a good default value in practice, as on a production system under moderate load you’ll usually only see a couple seconds of replica lag. This happens because changes on a moderately loaded system hit the 16MB target pretty quickly and you’re not really left waiting most of the time, and most environments with a read replica have a considerable level of baseline load. 

The problem comes from low throughput scenarios. If you don’t have a lot of write traffic coming in, Postgres won’t ship the change, and your replica won’t see an update for as long as 60 seconds. In my experience, this typically is discovered in the early phases of testing a platform, and this isn’t the first company where I’ve heard complaints of the resulting slow replica behavior. It’s always awkward to explain that a system is slow because you didn’t put enough load on it, and I like knowing how far you can push software before breaking it, so when it came up I thought I’d test things for myself. 

## Baseline tests {#baseline_tests}

I fired up a few test instances of ClickHouse Managed Postgres, set up pgbench to simulate load, and got to work. In order to measure replica lag, I added a heartbeat tool that wrote a row to the primary every 200ms and continually polled the same table on the replica. I kept the hardware pretty small to make it easier to actually stress the systems. There was a primary and one read replica, each using i8g.large instances with 16GB of RAM, 2 vCPUs, and 468GB of local NVMe SSD running PG 18.6. I ended up adding 2 quorum synchronous commit HA standbys midway through testing to better reflect production workloads, which cut throughput about 10% and had no measurable effect on replica lag. WAL generation reached up to 120MB/s (105MB/s with HA) in these tests, so despite the low core count this should give the replica mechanism the kind of throughput you’d see in a busy production environment. Please note that “idle” in the charts below does include trivial traffic to the heartbeat table (1 write every ~200ms), but zero pgbench load.

The first finding confirmed the cause of the surprise: the report of replica lag was, indeed, caused by not having enough load on the system. Replica lag with stock tuning yields a U-shaped curve based on throughput, with both extremely low and extremely high throughput causing big spikes in lag. The sweet spot in the middle is where data comes in fast enough to ship WAL segments right away but not fast enough to overwhelm anything, and the right side of the U comes from archive upload starting to fall behind. 

![](https://clickhouse.com/uploads/postgres_replica_nov2026_image1_d589648c1a.png)

This was pretty good right out of the gate, as the moderate load of 12MB/s led to ~3 second replication delay, and that’s good enough for most use cases. Having confirmation that it wouldn’t be an issue in prod was a good start, but we could do better, and I had a test environment in dire need of a good workout. 

## Sensible tuning {#sensible_tuning}

There’s not a lot of tuning relevant to replication lag, but a few things came to mind. The 16MB WAL segment size can only be tuned when building a new database using `initdb --wal-segsize` or by using `pg_resetwal --wal-segsize` in a maintenance window, which is not generally useful for tuning an existing environment. The next good candidate was the 60 second interval, which is controlled by the `archive_timeout` parameter. This simply controls how long Postgres will wait before shipping the segment anyways, so it’s about as relevant as it gets. 

There’s a related setting here of `wal_retrieve_retry_interval` that also turned out to be relevant. This one controls how long Postgres will wait between retry attempts if it fails to find the requested WAL segment on the first try, and for all practical purposes it can be better seen as a poll interval.

I tried a bunch of different values under a couple different levels of simulated load. I’ve lumped `wal_retrieve_retry_interval` and `archive_timeout` together here, as in practice they were doing the same job for the purposes of replication lag. 

![](https://clickhouse.com/uploads/postgres_replica_nov2026_image2_9f3362f374.png)

Interestingly, this seemed to stop giving improvements once it got too low. The limit is that each poll ended up taking about 0.8s of WAL-G sequential calls, so there wasn’t much point going below a second or so. Here’s a constructed example with a breakdown on where the time typically went:

```shell
t+0.00  restored log file N              <- N fetched
t+0.20  Archive N+1 does not exist       <- wal-g call (not there yet)
t+0.45  restored log file N   (again)    <- Postgres re-fetches N from the archive
t+0.70  Archive N+1 does not exist       <- wal-g call
t+0.80  Archive 00000002.history ...     <- timeline check (recovery_target_timeline=latest)
        waiting for WAL ...              -> sleep wal_retrieve_retry_interval (5 s), repeat

```

The re-fetch occurs because Postgres does not persist a local copy of segments restored from archive. If the next segment is not yet archived when requested, or Postgres otherwise fails to fetch it, then it will re-fetch and re-read the segment containing the last valid record before trying the next segment again. I believe the history check could be omitted if `recovery_target_timeline` was pinned instead of using the default value of latest, but that would mean the replica wouldn’t survive HA failover and probably wouldn’t be worth the cost. 

Unfortunately, this does come with some nontrivial costs. `archive_timeout` is going to increase network overhead with synchronous HA, which might get expensive with cross-AZ HA configurations. Shipping 16MB to each standby once every `archive_timeout` will add up over time, with a 2s `archive_timeout` costing 17MB/s and reaching over 1TB/day with 2 standbys. The read replica will also see some side effects, as every missed poll will re-download and re-decompress the previous segment from object storage. 

Replica CPU spiked a bit more than I expected, too. The replica only had 2 vCPUs, so the tests had an unrealistically high relative impact. As far as I can tell, the CPU load is almost entirely driven by poll rate, as every poll forces a re-fetch and decompression and is effectively a fixed cost regardless of instance size or data volume. The load overhead should more or less disappear into the background on a more realistic 8+ core production-grade system. Unfortunately, I ran out of time to test that for this project. 

![](https://clickhouse.com/uploads/postgres_replica_nov2026_image3_5252c21ac9.png)

## Less sensible tuning {#less_sensible_tuning}

When I looked for other room for improvement, I found that `archive_timeout` sadly only accepts integer parameters, so going below 1 second wasn’t reasonable. I eventually realized that Postgres has a nifty little mechanism to force a switch to a new WAL file, `pg_switch_wal()`. I started firing it off in a loop at various short intervals, and got some more interesting results. I’ve included the previous values for comparison: 

![](https://clickhouse.com/uploads/postgres_replica_nov2026_image4_da92d33a5a.png)

This didn’t actually make things better enough to be worthwhile. Each segment incurred WAL-G fetch overhead of its own, so as intervals shrunk that overhead ate more and more of our time. It also gives us an explanation as to why the p99 was so much worse than the p50 when WAL switches were too aggressive: any slowdown or failure causes a cascade of backed up segments.

The switch loop also had a notable impact on overhead. The primary sends a 16MB segment to each HA standby every time there’s a forced WAL switch, which is going to add up pretty fast if there’s cross-AZ or cross-cloud traffic to worry about. Primary throughput dropped by somewhere around 15% with the switch loop running, which is a fairly significant tradeoff.  

The next decreasingly reasonable thing to try was to get creative and deal with the WAL-G overhead. A lot of time was being spent waiting for WAL-G to start up a fresh process for each and every fetch, and I didn’t actually need to do that. We have a WAL-G daemon already running on these machines, so I could abuse that fact with a simple config line:

```shell
restore_command = '/usr/bin/walg-daemon-client /tmp/wal-g wal-fetch %f %p'
```

This shaved about 55ms on a hit and about 85ms on a miss for every fetch, and as you can see below this really added up for the 250ms switch loop. It was helpful but less dramatic at 1s and pretty pointless for anything else. Increasing external dependencies in the replay path certainly isn’t a good idea in a production environment, but it’s neat to see how far you can push such things: 

![](https://clickhouse.com/uploads/postgres_replica_nov2026_image5_536ae6a287.png)

All in all, not a bad day’s work! One last thing to check: How does all the archive shipping tuning compare to just using streaming replication, anyways?

![](https://clickhouse.com/uploads/postgres_replica_nov2026_image6_24149633ee.png)

Alas, we haven’t beaten it. On the bright side, we don’t need to. A second or three of replication lag is more than enough for most use cases, and there are a few well-known downsides to streaming replication that prevent us from making it the default choice.

* The `hot_standby_feedback` parameter can prevent VACUUM from removing recently dead rows on the primary if they are needed by the replica.   
* A replication slot getting stuck or backing up can fill up your disk and cause an outage on the primary unless `max_slot_wal_keep_size` is set.  
* Replication overhead can contribute to primary load. As most users of read replicas use them to prevent resource constraints, this hurts the people who need replicas most.   
* HA failovers can be tricky, and it’s pretty easy to get a setup that breaks the replica on failover. 

We do use streaming replicas for HA standbys, where the lack of read activity and guaranteed hardware match to prod mitigates those downsides effectively, and the subsecond lag matters a lot for minimizing downtime. 

---

## Get started with ClickHouse Managed Postgres today

Interested in seeing how ClickHouse Managed Postgres works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?intent=pg&loc=blog-cta-3069-get-started-with-clickhouse-managed-postgres-today-sign-up&utm_blogctaid=3069)

---