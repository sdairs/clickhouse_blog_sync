---
title: "ClickHouse at FOSDEM 2026"
date: "2026-04-08T18:00:47.189Z"
author: "Tyler Hannan"
category: "Company and culture"
excerpt: "FOSDEM 2026 took place on 31 January and 1 February in Brussels, and it was a great weekend for the ClickHouse community, both inside the conference rooms and out."
---

# ClickHouse at FOSDEM 2026

FOSDEM 2026 took place on 31 January and 1 February in Brussels, and it was a great weekend for the ClickHouse community, both inside the conference rooms and out.

## Community Dinner

The weekend kicked off with the ClickHouse community dinner at L'Ultime Atome in Ixelles, Brussels. 106 people joined us for dinner, drinks, and some of the best conversations of the conference. ClickHouse founder Alexey was there to chat and answer questions. Thanks to everyone who came out; it was a fantastic evening (some pictures are at the end of this post).

But it wasn’t just a chance to eat and drink; we had multiple presentations at the event itself.

## Our Talks

### Planes, Ships, Birds – Building Real-Time Visualizations with ClickHouse

**Track:** Geospatial · **Day:** Saturday
**Speaker:** Alexey Milovidov · [Slides](https://presentations.clickhouse.com/2026-fosdem-geospatial/)

This session walked through creating an analytical application from the ground up, covering the entire workflow: data collection, processing, and visualization. The stack uses Leaflet, ClickHouse, and a collection of shell scripts. The finished result is published at [adsb.exposed](https://adsb.exposed/), and the talk uncovered how it was built.

<iframe width="560" height="315" src="https://www.youtube.com/embed/YOlEcBLDVvk?si=5EVmFmI2v--q6DKX" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

---

### Hotpatching ClickHouse in Production with XRay

**Track:** LLVM · **Day:** Saturday
**Speaker:** Pablo Marcos · [Slides](https://fosdem.org/2026/events/attachments/N7MVZT-hotpatching-clickhouse-with-llvm-xray/slides/266966/hotpatchi_f1nbs5s.pdf)

Ever been debugging a production issue and wished you'd added just one more log statement — only to face a rebuild, a wait for CI, and a full redeploy? The ClickHouse team integrated LLVM's XRay to solve exactly this. It lets you hot-patch a running production system to inject logging, profiling, and even deliberate delays into any function, with no rebuild required.

XRay reserves space at function entry and exit points that can be atomically patched with custom handlers at runtime. The team built three handler types: LOG to add the trace points you forgot, SLEEP to reproduce or prevent timing-sensitive bugs, and PROFILE for deterministic profiling to complement the existing sampling profiler. The performance overhead when inactive is negligible.

Control is via a SQL query — `SYSTEM INSTRUMENT ADD LOG 'QueryMetricLog::startQuery' 'message'` — which patches the function instantly, with results appearing in `system.trace_log`. The talk also covered the integration challenges (ELF parsing, thread-safety, atomic patching), performance numbers (4–7% binary size increase, near-zero runtime cost), and real production war stories.

<iframe width="560" height="315" src="https://www.youtube.com/embed/DZeVcRD0rWM?si=X47mRrsF1LXTIjLp" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

---

### Inverted database indexes: The why, the what, and the how.

**Track:** Databbases · **Day:** Saturday 
**Speaker:** Elmi Ahmadov · [Slides](https://presentations.clickhouse.com/2026-fosdem-inverted-index/Inverted_indexes_the_what_the_why_the_how.pdf)

Database usage in practice often involves heavy text processing. For example, in "observability" use cases, databases must extract, store, and search billions of log messages daily. Most databases, including many column-oriented OLAP databases, struggle with such massive amounts of text data. The only way to process text data at scale is by using specialized inverted indexes in databases.

This presentation explains how inverted indexes work and which (text) search patterns they support. Where appropriate, we describe our experience and the gotchas we encountered when adding an inverted index to ClickHouse, one of the most popular open-source databases for analytics.

<iframe width="560" height="315" src="https://www.youtube.com/embed/6eM1rCZy7XI?si=MwfUq1E_fFmQC6K8" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

---

### ClickHouse's C++ and Rust Journey

**Track:** Rust · **Day:** Sunday
**Speaker:** Alexey Milovidov · [Slides](https://presentations.clickhouse.com/2025-p99/)

For a large C++ codebase, a full rewrite to Rust is not an option — only gradual integration with Rust libraries is realistic, and even then there are many complications and rough edges. This talk described the experience of integrating Rust and C++ code in ClickHouse, and some of the weird and unusual problems the team had to overcome along the way.

<iframe width="560" height="315" src="https://www.youtube.com/embed/433zALc6u3Y?si=Ux9Htf42tdWYQas-" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

---

### How to Move Bytes Around

**Track:** Software Performance · **Day:** Sunday
**Speaker:** Alexey Milovidov · [Slides](https://presentations.clickhouse.com/2026-fosdem-memcpy/)

If you take a random program and start profiling it, you'll usually find `memcpy` near the top — though that doesn't necessarily mean memcpy is slow. As the abstract puts it: the most hopeless thing a C++/Rust developer can do (while no one is watching) is optimize memcpy to move bytes faster. That's exactly what this talk did.

<iframe width="560" height="315" src="https://www.youtube.com/embed/rPX-3UrFiF4?si=OP7_nRl8v16xccCf" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

---

### Contributing to MariaDB & Postgres

**Track:** Databases · **Day:** Saturday
**Speakers:** Georgi Kodinov, Kevin Biju

A two-part talk on contributing to major open-source database projects.

Georgi Kodinov walked through what it actually takes to get a contribution into the MariaDB server codebase, following a real bug fix — two lines of code — through its entire review process, and explaining why the bar is higher than it might seem on a project of this scale.

Kevin Biju traced his own path from setting up a local Postgres build to contributing bug-fix patches and documentation updates. The talk outlines how the Postgres development process and community operate, with the aim of demystifying the process so more engineers feel confident making their first (or next) patch.

<iframe width="560" height="315" src="https://www.youtube.com/embed/BgODDRqp6yA?si=j2NchIseWMoIWAvW" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

---

## From the Community

We weren't the only ones talking about ClickHouse at FOSDEM. Here are some talks from the community that are worth checking out:

### Dynamic Bot Blocking with Web-Server Access-Log Analytics

Alexander Krizhanovsky - [Video](https://fosdem.org/2026/schedule/event/3BMPMU-dynamic_bot_blocking_with_web-server_access-log_analytics/)

Bots generate roughly half of all Internet traffic. Some are clearly malicious (password crackers, vulnerability scanners, application-level/L7 DDoS), and others are merely unwanted (web scrapers, carting, appointment etc) bots. Traditional challenges (CAPTCHAs, JavaScript checks) degrade user experience, and some vendors are deprecating them. An alternative is traffic and behavior analytics, which is much more sophisticated, but can be far more effective.

Complicating matters, there are cloud services not only helping to bypass challenges, but also mimic browsers and human behavior. It's tough to build a solid protection system withstand such proxy services.

In this talk, we present WebShield, a small open-source Python daemon that analyzes Tempesta FW, an open-source web accelerator, access logs and dynamically classifies and blocks bad bots.

You'll learn: * Which bots are easy to detect (e.g., L7 DDoS, password crackers) and which are harder (e.g., scrapers, carting/checkout abuse). * Why your secret weapon is your users’ access patterns and traffic statistics—and how to use them. * How to efficiently deliver web-server access logs to an analytics database (e.g., ClickHouse). * Traffic fingerprints (JA3, JA4, p0f): how they’re computed and their applicability for machine learning * Tempesta Fingerprints: lightweight fingerprints designed for automatic web clients clustering. * How to correlate multiple traffic characteristics and catch lazy bot developers. * Baseline models for access-log analytics and how to validate them. * How to block large botnets without blocking half the Internet. * Scoring, behavioral analysis, and other advanced techniques are not yet implemented

## Photos

We wish you could have been there. Here are some images that capture a sense of the experience. Do you want to join the next one? Let us know and we can help with your presentation.

![](https://clickhouse.com/uploads/IMG_2418_278b810aed.jpg)

![](https://clickhouse.com/uploads/PXL_20260201_105432126_93a240840f.jpg)

![](https://clickhouse.com/uploads/1000137544_91dc7234e1.jpg)

![](https://clickhouse.com/uploads/PXL_20260131_194611228_13bf9b1778.jpg)

![](https://clickhouse.com/uploads/PXL_20260201_141128012_622724b026.jpg)

![](https://clickhouse.com/uploads/PXL_20260131_194552756_a8aeaf6c81.jpg)