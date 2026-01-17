---
title: "Good technology blogs: a reading list for the holidays"
date: "2025-12-28T23:02:26.600Z"
author: "Alexey Milovidov"
category: "Engineering"
excerpt: "A collection of my favorite technology blogs"
---

# Good technology blogs: a reading list for the holidays

I enjoy reading blogs about performance optimizations, data structures and algorithms, database development, compilers, operating systems, programming languages, computer science and mathematics, hardware and networks, web development, computer graphics, and AI. I'll share some of my favorites with you, to help you survive the holidays.

## [Daniel Lemire](https://lemire.me/blog/)

Daniel is the author of many high-performance libraries and algorithms. His articles cover details of low-level performance optimizations, and he often finds opportunities to improve fundamental building blocks and computational kernels, used in every program, like parsing IP addresses, validating UTF-8, compressing sequences of numbers, converting numbers to strings, etc. His libraries and algorithms are adopted in ClickHouse too, for example, [simdjson](https://github.com/ClickHouse/ClickHouse/pull/5124) and [Roaring bitmap](https://github.com/ClickHouse/ClickHouse/pull/4207). We have also contributed numerous bug fixes back to these libraries.

## [Ash Vardanyan](https://ashvardanian.com/archives/)

Ash is one of the most visible enthusiasts of performance optimizations and hardware. He is the author of USearch (a library for vector search with HNSW) and StringZilla (a collection of computational kernels for string processing), and both of them are used in ClickHouse.

## [Wojciech Muła](http://0x80.pl/notesen.html)

Highly optimized computational kernels with and without SIMD instructions. For some reason, this blog does not use HTTPS, but that does not diminish its value.

## [Daniel Kutenin](https://danlark.org/)

Daniel is an expert in performance optimizations, algorithms, and compilers. He is also a [ClickHouse contributor](https://github.com/ClickHouse/ClickHouse/pulls?q=is%3Apr+author%3Adanlark1+is%3Aclosed), where he has implemented many string algorithms, such as an adaptation of Volnitsky's substring search for case-insensitive strings and for searching multiple strings at once (better than Aho-Corasick on a small number of strings), integrated Hyperscan (now Vectorscan) for multi and fuzzy search, and added string distances. Most importantly, he is the author of [Miniselect](https://github.com/danlark1/miniselect) which is a library for partial sorting, also integrated into ClickHouse.

## [Fangrui Song (MaskRay)](https://maskray.me/)

This is a blog about compilers, linkers, and executable binary formats. The amount of information in this blog will make you worry about yourself.

## [Yann Collet](https://fastcompression.blogspot.com/)

Yann is the author of lz4 and zstd, one of the most important libraries for databases. I [integrated LZ4](https://github.com/ClickHouse/ClickHouse/commit/58110f5cde5f3ececf2b439ab8cc36748559012d) in ClickHouse in 2012, and it was fantastic! I remember how I was amazed and eager to see his zhuff algorithm open-sourced, but he did even more by releasing zstd in 2015, which I immediately [integrated in ClickHouse](https://github.com/ClickHouse/ClickHouse/commit/7d11fc0931267ca4468c3379f358d7345a692664), replacing quicklz. We even found a few bugs in the first 0.x versions of zstd :) I spent a lot of time trying to understand the mechanics of LZ4, and ended up [optimizing it just a little](https://clickhouse.com/blog/lz4-compression-in-clickhouse).

Yann now works at Facebook, and his personal blog stopped being updated. For more resources about compression, you can check the [data compression forum](https://encode.su/) and read [Data Compression Explained](https://mattmahoney.net/dc/dce.html) from Matt Mahoney.

## [Dan Luu](https://danluu.com/)

Dan has many great articles about [CPU](https://danluu.com/hardware-unforgiving/) and [performance profiling](https://danluu.com/perf-tracing/).

## [Brendan Gregg](https://www.brendangregg.com/blog/index.html)

If you are interested in performance profiling, introspection, instrumentation, and tracing, read this blog.

## [Russ Cox](https://research.swtch.com/)

Russ is the author of the re2 library, he writes about algorithms amongst other topics. Re2 was a revolution for us - I still remember how colleagues tried to convince me that giving end users access to queries with arbitrary regular expressions would end up with DoS, but I knew it was going to be alright because [I use re2](https://github.com/ClickHouse/ClickHouse/commit/ea816297c2ae16b50a20ebd684471a535b59e6b0)! This was proven by practice - in 15 years, there was not a single case to lose trust in re2. There are faster libraries, like [vectorscan/hyperscan](https://github.com/ClickHouse/ClickHouse/pull/4816) and more versatile libraries, but re2 remains unbeaten. This article about [uninitialized memory](https://research.swtch.com/sparse) is especially interesting.

## [Bruce Dawson](https://randomascii.wordpress.com/)

Bruce has many articles about [floating point numbers](https://randomascii.wordpress.com/category/floating-point/).

## [Probably Dance](https://probablydance.com/)

This blog by Malte Skarupke is amazing. Scroll down to find the tech articles. He [didn't write the fastest hash table](https://probablydance.com/2017/02/26/i-wrote-the-fastest-hashtable/).

## [Alisa Sireneva](https://purplesyringa.moe/blog/)

Amazing blog about low-level optimizations, algorithms, and compilers. Don't worry, you can easily skip the articles about Rust if you want.

## [Kamila Szewczyk](https://iczelia.net/posts/)

Good articles about data compression, such as [this](https://iczelia.net/posts/lz-ent-detection/).

## [Salvatore Sanfilippo](https://antirez.com/)

A blog from the author of Redis. He writes rarely, and not only about AI. I really liked his smaz compression library and linenoise (an alternative to readline). He writes about experiments and observations from a first person perspective, and he is able to rethink some ideas and approaches without influence. It's worth noting that Redis lacks multithreading, it does not have on-disk data structures, and it does not implement distributed consensus. Finally, its development speed is very low, and the author uses a very conservative approach to software development. That's why there are many Redis clones, but none of them are comparable in terms of its reach.

## [Mitchell Hashimoto](https://mitchellh.com/writing)

This blog isn't about databases. It's great to read about the first-person perspective of the founder of Hashicorp, as well as the development of a terminal emulator in Zig.

## [Fabien Sanglard](https://fabiensanglard.net/)

This blog is also not about databases, but there is a lot of good stuff in it, such as the article about [pseudorandom permutations](https://fabiensanglard.net/fizzlefade/index.php).

## [Ben E. C. Boyter](https://boyter.org/)

Ben is the author of scc - a tool for counting lines of code. I especially liked his article about [analyzing GitHub](https://boyter.org/posts/an-informal-survey-of-10-million-github-bitbucket-gitlab-projects/).

## [Nikita Lapkov](https://laplab.me/posts/)

Nikita has many good articles about databases. He is also a ClickHouse contributor, where he [implemented](https://github.com/ClickHouse/ClickHouse/pull/4247) the first version of [always-on profiler](https://presentations.clickhouse.com/2019-yatalks-moscow/).

## [Simon Willison](https://simonwillison.net/)

Simon writes about AI. Even if you already get nauseous from this topic, don't run away, because Simon writes about first-person, hands-on experience with new models and tools. The articles are concise and unpretentious, which makes them pleasant to read.

## [Andrej Karpathy](https://karpathy.github.io/)

This is a great blog about AI, with articles like [this](https://karpathy.github.io/2015/05/21/rnn-effectiveness/) you should probably have read ten years ago. Today he is active on [YouTube](https://www.youtube.com/@AndrejKarpathy/videos).

## [Jay Mody](https://jaykmody.com/)

This is such a great blog about AI! Only five articles, though.

## [Kyle Kingsbury](https://jepsen.io/blog)

He tests the consistency of distributed databases, and there is hardly any database that survives his testing. Kyle is the author of the Jepsen framework, which is also [used in ClickHouse](https://github.com/ClickHouse/ClickHouse/tree/master/tests/jepsen.clickhouse), as well as in any self-respecting distributed DBMS.

## [Database Architects](https://databasearchitects.blogspot.com/)

A blog from developers of academic databases from TUM and CWI. The covered topics are often very similar to the development of ClickHouse.

## [DBMS Musings by Daniel Abadi](https://dbmsmusings.blogspot.com/)

A similar blog about databases, mostly column-oriented. Not updated since 2019.

## [Marc Brooker](https://brooker.co.za/blog/)

A blog about databases and distributed systems.

## [Mark Callaghan](https://smalldatum.blogspot.com/)

The last articles are all about how he compiled a certain version of MySQL or PostgreSQL and compared performance. It's very boring. I like this blog.

## [Raymond Chen](https://devblogs.microsoft.com/oldnewthing/)

A lot of interesting curiosities from the history of the development of Windows.

## [Bartosz Ciechanowski](https://ciechanow.ski/archives/)

This blog isn't about databases or AI, and the articles appear very rarely. This is the best blog I've ever seen.

## [Justine Tunney](https://justine.lol/)

She is the author of Cosmopolitan Libc, and the blog is great to read if you are interested in binary formats, linkers and loaders, machine instructions, operating systems, and hardware. Note that ClickHouse does not use Cosmopolitan Libc, as it is still hard to apply for large C++ applications. We have a build with Musl-libc, and I also hope that LLVM libc will eventually be suitable for ClickHouse.

## [Alex Kladov](https://matklad.github.io/)

Numerous articles discuss low-level code and performance. Sometimes about Rust and Zig, but should you worry?

## [LLVM blog](https://blog.llvm.org/)

If you are interested in compilers.

## [LWN](https://lwn.net/)

If you are interested in operating systems.

## [v8](https://v8.dev/blog)

If you are interested in web browsers.

## [Julia Evans](https://jvns.ca/)

A collection of brief notes on things worth knowing.

## [Rachel](https://rachelbythebay.com/w/)

Many small observations about tech.

## [Charles Bloom](https://cbloomrants.blogspot.com/)

Many good articles about data compression. From this blog, I learned the term ["cache table"](https://cbloomrants.blogspot.com/2010/11/11-19-10-hashes-and-cache-tables.html), and cache tables are widely used in ClickHouse, for cache dictionaries, for data compression, and for small caches.

## [Peter Kankowski](https://www.strchr.com/)

Low-level performance optimization tricks. For some reason, it is not updated anymore, but some of the old articles are golden.

## [Jeff Preshing](https://preshing.com/)

Also not updated, but there are many good articles, like this one about [pseudorandom permutations](https://preshing.com/20121224/how-to-generate-a-sequence-of-unique-random-integers/).

## [Marek](https://idea.popcount.org/)

It's been a long time since the last update, but there are many good articles, e.g., about [bitslicing](https://idea.popcount.org/2013-01-30-bitsliced-siphash/).

## Thoughts

While going through my favorite blogs, I've noticed that some of them have sadly stopped updating. Some blogs even disappeared, like a blog of Yury Lifshits about string and nearest neighbor algorithms or a blog of Eugene Kirpichev about functional data structures, such as [incremental regular expressions](http://jkff.info/articles/ire/). Sometimes there are rumors that the authors are still alive and continue to write somewhere on ~~darknet~~Facebook, but about therapy, philosophy, or parenting. What I really want is for them to continue writing great articles about technology!