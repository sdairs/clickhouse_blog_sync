---
title: "How to speed up LZ4 decompression in ClickHouse?"
date: "2022-07-12T03:52:41.061Z"
author: "Alexey Milovidov"
category: "Engineering"
excerpt: "Explore the reasons behind the prominence of the LZ_decompress_fast function and optimize your ClickHouse queries for enhanced efficiency. Read more here."
---

# How to speed up LZ4 decompression in ClickHouse?

When you run queries in [ClickHouse](https://clickhouse.com/), you might notice that the profiler often shows the `LZ_decompress_fast` function near the top. What is going on? This question had us wondering how to choose the best compression algorithm.

ClickHouse stores data in compressed form. When running queries, ClickHouse tries to do as little as possible, in order to conserve CPU resources. In many cases, all the potentially time-consuming computations are already well optimized, plus the user wrote a well thought-out query. Then all that's left to do is to perform decompression.

[Read further](https://habr.com/en/company/yandex/blog/457612/)