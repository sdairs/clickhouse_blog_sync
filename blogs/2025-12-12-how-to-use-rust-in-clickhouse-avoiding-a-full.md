---
title: "How to use Rust in ClickHouse: avoiding a full rewrite"
date: "2025-12-12T10:55:05.414Z"
author: "Alexey Milovidov"
category: "Engineering"
excerpt: "An annotated version of Alexey's presentation at the P99 conference on the use of Rust in ClickHouse."
---

# How to use Rust in ClickHouse: avoiding a full rewrite

<style>
.rich_content p {
    padding-bottom: 1em;
}
</style>

I recently presented [a talk at the P99 conference](https://www.p99conf.io/session/clickhouses-c-rust-journey/), where I explained our experiences working with Rust at ClickHouse, a predominantly C++ codebase.

The video of the talk is included below. 

<iframe width="768" height="432" src="https://www.youtube.com/embed/Q61QnV5r1fA?si=yJDft-hsiUF8vaac" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

I also wanted to make it available as an annotated presentation, so I've included [the slides](https://presentations.clickhouse.com/2025-p99/) along with a marked-up transcript of the talk.

## Introduction

<div class="slide" id="1.svg">
  <img loading="lazy" src="/uploads/1_34f74fcb12.svg" alt="Rust in ClickHouse - How to avoid a fullrewrite" style="max-width: 100%" />
  <div><a style="float: right; text-decoration: none; border-bottom: none; padding-left: 1em;" href="https://presentations.clickhouse.com/2025-p99/index.html#cover/#cover">#</a>
  <p class="slide-text">Hi, I am Alexey, ClickHouse developer, and my story today is about our migration from C++ to Rust.</p>
  </div>
</div>

## What is ClickHouse?

<div class="slide" id="2.svg">
  <img loading="lazy" src="uploads/2_0b1fd13b93.svg" alt="Slide about ClickHouse being written in C++ and questioning whether Rust would be better" style="max-width: 100%" />
  <div><a style="float: right; text-decoration: none; border-bottom: none; padding-left: 1em;" href="https://presentations.clickhouse.com/2025-p99/index.html#2">#</a>
  <p class="slide-text">So what is ClickHouse? ClickHouse is an open source analytic database management system with a lot of contributors and a lot of stars on GitHub. It is in fact the most popular open source analytic database, and it is mostly written in C++. It has one and a half million lines of code, which is actually not a lot compared to other database management systems like MySQL or Postgres. It is, I would say, normal. And it has a history for more than 10 years, with a lot of people all over the internet contributing to ClickHouse and modifying its source code. It has tons of production usages—maybe hundreds or thousands of companies, maybe even more.</p>

<p class="slide-text">
It is easy to hire people with C++ knowledge. Universities still teach C++ and some of them do it quite well. And the language is well represented among database management systems. Not only MySQL is in C++, but also Postgres is in C, MongoDB is in C++, Redis is in C, ClickHouse is in C++, DuckDB is in C++. Not every database management system is in C or C++, but anyway. Graphics applications, desktop applications for audio processing, music, 3D modeling, computer-aided design, operating systems—obviously most of them are in C++—video games, still C++ is the king, scientific data analysis, etc. So C++ is everywhere.
</p>

<p class="slide-text">
But the question is, if we started today, should we write ClickHouse in C++? Maybe we should write it in Rust. Does it make sense to maybe rewrite our precious database from C++ to Rust?
</p>

  </div>
</div>

## Is C++ a pain?

<div class="slide" id="3.svg">
  <img loading="lazy" src="/uploads/3_20cdc77a7c.svg" alt="Slide about ClickHouse's comprehensive CI testing system to manage C++ development challenges" style="max-width: 100%" />
  <div><a style="float: right; text-decoration: none; border-bottom: none; padding-left: 1em;" href="https://presentations.clickhouse.com/2025-p99/index.html#2">#</a>
  <p class="slide-text">
  
  What is wrong with C++ actually? Is it a pain? Yes, it is, because it is an unsafe programming language. It's not memory safe. Segmentation faults, memory corruptions, race conditions—they are everywhere. If you only start writing in C++, most likely you will have segmentation faults, race conditions, and memory corruption. It is almost inevitable. Almost, because actually you can try to do your best to avoid this pain, but it requires so many efforts.
  </p>

<p class="slide-text">
For example, in ClickHouse, we have a huge continuous integration system that runs tens of millions of tests every day. That are actually like tens of thousands of tests in a lot of different combinations with all possible sanitizers: address sanitizer, thread sanitizer, memory sanitizer, and undefined behavior sanitizer. We do it for every commit in every pull request on master with a lot of functional tests and stress tests and fuzzing, including coverage-guided fuzzing. And I can say it helps. It helps a lot. But it is not 100%, and the remaining percent or so will still be represented as a lot of bugs.
</p>

<p class="slide-text">
So maybe it's time to rewrite in Rust.
</p>

  </div>
</div>

## Reasons for Rust vs arguments against Rust

<div class="slide" id="4.svg">
  <img loading="lazy" src="/uploads/4_70a17c8459.svg" alt="Slide presenting reasons for and against using Rust, including safety, modern libraries, and hype as pros, versus concerns about rewrite time, language mixing, and accumulated knowledge as cons." style="max-width: 100%" />
  <div><a style="float: right; text-decoration: none; border-bottom: none; padding-left: 1em;" href="https://presentations.clickhouse.com/2025-p99/index.html#4">#</a>
  <p class="slide-text">
  The advantages are obvious. Memory and thread safety, modern libraries. Some libraries are only available in Rust, not in C++. And there is a lot of hype—Rust is trendy, and many new engineers write in Rust. And sometimes I think that when we pay someone to work full-time on C++, some people will write in Rust for free, or even pay us to get a chance to write code in their favorite programming language. And if this language is so loved, we can use it as an advantage.
  </p>
    <p class="slide-text">
    But there are a lot of arguments against migration. The main argument is that rewrite is always hard to do. It takes years, and if we dedicate all our team to do a rewrite, we will lose the time, we will be behind, we will lose all our accumulated knowledge in C++. And actually, I don't like the drama and hype around Rust. Like every week or so, there is a post on social networks, there is some scandal about someone leaving the community, someone being disappointed, someone arguing about something. It does not happen in C++. In C++ it is boring. Every grey beard understands it is a bad language, but it is with us, we have to bear with it.
    </p>

  </div>
</div>

## Our Approach: Iterative development

<div class="slide" id="5.svg">
  <img loading="lazy" src="/uploads/5_c2ca445959.svg" alt="Slide describing ClickHouse's iterative Rust adoption approach: integrating Rust into CMake build system using corrosion (2022), then adding BLAKE3 hashing as first non-essential library example, with performance comparison chart." style="max-width: 100%" />
  <div><a style="float: right; text-decoration: none; border-bottom: none; padding-left: 1em;" href="https://presentations.clickhouse.com/2025-p99/index.html#5">#</a>
  
  <p class="slide-text">
  So instead of a full rewrite, we chose iterative development, maybe just to give it a chance, just to explore if it's worth trying to taste this ecosystem, this language. The first step is just to introduce Rust into the build system.
</p>
  <p class="slide-text">
  Our build system is CMake and there is a CMake project named Corrosion, specifically for building with Rust libraries and linking with Rust libraries in C++. You only have to write a small wrapper for the library interface and then it will do everything for you. So we decided to test it on something that we not actually needed. We made a task: add one new function to the SQL dialect.  In SQL we have about 2,000 functions and we decided to take one new with the only library available in Rust—BLAKE3. 
  </p>
  </div> 
</div>

## Integrating Rust code into ClickHouse

<div class="slide" id="6.svg">
  <img loading="lazy" src="/uploads/6_21f4d572aa.svg" alt="GitHub pull request #33435 showing the integration of Rust code into ClickHouse with BLAKE3 hash-function library, merged on October 3, 2022 with 134 commits and 25 files changed." style="max-width: 100%" />
  <div><a style="float: right; text-decoration: none; border-bottom: none; padding-left: 1em;" href="https://presentations.clickhouse.com/2025-p99/index.html#6">#</a>
    <p class="slide-text">
    And it was a success. It was <a href="https://clickhouse.com/docs/sql-reference/functions/hash-functions">added in 2022</a> and the integration basically worked.
    </p>
  </div>
</div>

## Improving clickhouse-client with Rust

<div class="slide" id="7.svg">
  <img loading="lazy" src="/uploads/7_a75041e40d.svg" alt="Slide showing terminal screenshot of clickhouse-client improvements made with Rust, noting this was the first external Rust contribution and proving Rust's value despite an initial panic bug." style="max-width: 100%" />
  <div><a style="float: right; text-decoration: none; border-bottom: none; padding-left: 1em;" href="https://presentations.clickhouse.com/2025-p99/index.html#7">#</a>
    <p class="slide-text">
  So the next step is to add something more serious. And thankfully <a href="https://github.com/ClickHouse/ClickHouse/pull/33435">we received a contribution from an external developer</a>. It was an external developer—now we hired him, not just to write Rust, actually he is a C++ developer. But anyway, he contributed this thing, an improvement for history navigation in the command line ClickHouse client. And you know, it is quite logical because Rust is very good for rewriting command line applications. Sometimes I think that maybe everything that people do in Rust is just rewriting CLI tools. But actually, it's not only good for that.
  </p>
  <p class="slide-text">
  So it was worth it. It is a really usable feature contributed by an external person. It's really great.  
  </p>
  </div>
</div>

## Community contributions and improvements

<div class="slide" id="8.svg">
  <img loading="lazy" src="/uploads/8_ecc04f730f.svg" alt="GitHub pull request list showing multiple Rust-related improvements to ClickHouse client, including fuzzy search features, build fixes, and interactive history search, spanning from September to December 2022." style="max-width: 100%" />
  <div><a style="float: right; text-decoration: none; border-bottom: none; padding-left: 1em;" href="https://presentations.clickhouse.com/2025-p99/index.html#8">#</a>
  <p class="slide-text">
  Unfortunately, it introduced a lot of problems, and you can see it in this list of pull requests. So the first was adding this library, then fixing builds, then reverting for some reason, then again fixing something, then reverting, and fixing something. And it is hard to figure out what was happening. I will tell about it in more detail. 
  </p>
  </div>
</div>

## PRQL - Pipelined Relational Query Language

<div class="slide" id="9.svg">
  <img loading="lazy" src="/uploads/9_a0389be0a8.svg" alt="PRQL offers a modern, pipelined alternative to SQL with filter and sort operations, demonstrated through a track_plays query comparison." style="max-width: 100%" />
  <div><a style="float: right; text-decoration: none; border-bottom: none; padding-left: 1em;" href="https://presentations.clickhouse.com/2025-p99/index.html#9">#</a>
  <p class="slide-text">
  A new data language. It is named <a href="https://github.com/PRQL/prql">PRQL</a>, Pipeline Relational Query Language. And you can see to the left an example with SQL in ClickHouse dialect, and to the right, an example with PRQL. And you know, actually I like SQL more, but not everyone. And we tried to use this PRQL, just an example of a sizable library to test. And it was just a student coursework. It was finished. The student gets his excellent grade. And now we have this library and its apparent problems.
  </p>
  </div>
</div>


## delta-kernel-rs: A library for Delta Lake

<div class="slide" id="10.svg">
  <img loading="lazy" src="/uploads/10_72f2818b35.svg" alt="Slide explaining delta-kernel-rs, a Rust library for Delta Lake format, highlighting Data Lake concepts and the evolution from Java to Rust implementations." style="max-width: 100%" />
  <div><a style="float: right; text-decoration: none; border-bottom: none; padding-left: 1em;" href="https://presentations.clickhouse.com/2025-p99/index.html#10">#</a>
  <p class="slide-text">
  Okay, now the next step is to add something that we actually need, not just something to test the integration. And it was a library for Delta Lake. Delta Lake is one of the data formats for data lakes. And data lakes is a kind of database when the data format can be independent of the query engine. So you have data in one place, and you can use any query engine, including ClickHouse, or something like DataFusion to query this data. It is quite popular, it makes data more accessible, but the ecosystem is still in early stage—it is fragmented, fragile.  </p>

  <p class="slide-text">
  So when we wanted to add support for Iceberg and Delta Lake, we were looking for libraries, and unfortunately, the first libraries were available only in Java. After a few years, they were also added in Rust. However, there were no libraries in C++, and we faced two alternatives: write our own library in C++, which is probably pointless, waste of time, because it is just like parsing a bunch of JSON files and redirecting HTTP requests. Or just reuse a Rust library. Now we have this option. And the <a href="https://github.com/delta-io/delta-kernel-rs">Delta Kernel RS</a> is the official library from Databricks. We did it. And it worked. But not without problems.

  </p>
  </div>
</div>

## Challenges of combining Rust and C++

<div class="slide" id="11.svg">
  <img loading="lazy" src="/uploads/11_22f2d5cea8.svg" alt="Slide discussing challenges of reproducible builds when combining Rust and C++, emphasizing dependency pinning and hermetic build requirements." style="max-width: 100%" />
  <div><a style="float: right; text-decoration: none; border-bottom: none; padding-left: 1em;" href="https://presentations.clickhouse.com/2025-p99/index.html#11">#</a>
  <p class="slide-text">
  What are the problems with Rust? It is a so perfect programming language, it uses all our experience to avoid mistakes of C++. But when we use C++ and Rust together, it could be problematic.
  </p>

<p class="slide-text">
The first problem is to ensure that all builds are reproducible. Dependencies must be pinned, built from the source code. The build system should be hermetic, isolated from the internet. And it was already solved in our C++ codebase. It was not easy, but now with Rust we have to solve it again. Actually it is as easy as vendoring the dependencies, but for some reason it took a few steps to do.
</p>


  </div>
</div>

## Writing wrappers between Rust and C++

<div class="slide" id="12.svg">
  <img loading="lazy" src="/uploads/12_1bf806fe05.svg" alt="Slide describing challenges with writing wrappers for Rust libraries in C++, noting they're error-prone but issues are caught through fuzzing and CI." style="max-width: 100%" />
  <div><a style="float: right; text-decoration: none; border-bottom: none; padding-left: 1em;" href="https://presentations.clickhouse.com/2025-p99/index.html#12">#</a>
  <p class="slide-text">
  Another problem. And sometimes you will have mistakes, you will have bugs just in this wrapper. You will get segmentation faults, crashes. And good news is that we already have our continuous integration system that we get from our experience with C++, and it saves us. It finds these seg faults and crashes very quickly, and all of them are trivial. It's not like a memory corruption that you will debug for a month. It is easy.
  </p>
  </div>
</div>

## Problems with Rust

<div class="slide" id="13.svg">
  <img loading="lazy" src="/uploads/13_6a444586fb.svg" alt="Slide titled "Problems with Rust" featuring a humorous image of a "DON'T PANIC" label, referencing The Hitchhiker's Guide to the Galaxy." style="max-width: 100%" />
  <div><a style="float: right; text-decoration: none; border-bottom: none; padding-left: 1em;" href="https://presentations.clickhouse.com/2025-p99/index.html#13">#</a>
  <p class="slide-text">
  
Another problem with Rust. It is panics. What is panic? It is a way to terminate the program or just to raise something that will terminate. It is like an assertion, a failure trap, or std::terminate. It crashes your program. But it is memory safe. Similarly to like null pointer dereference in C++. But everyone worries about null pointer dereferences because it is a segmentation fault. In Rust it is very similar, it is just a crash, but it is memory safe.
  </p>

<p class="slide-text">
And it is not a problem with Rust. The same problems are in many libraries that just crash the program too often instead of using something like exceptions. When a library uses panic, it could be an indication of a bug like failure to parse. We help to fix these bugs in the libraries. It is also an indication that panic can be mistakenly used instead of exceptions. Rust does not actually have exceptions. It has the possibility to unwind the stack, but if you try to implement exceptions in Rust, you will have so many troubles that you will regret it. As a result, libraries in Rust tend to use panic too much, even when it is not appropriate. And we have to find and fix all these cases, just to avoid abrupt termination of our server application.
</p>

  </div>
</div>

## Panic! handling in Rust

<div class="slide" id="14.svg">
  <img loading="lazy" src="/uploads/14_bfcd1117b8.svg" alt="Slide explaining that Rust panic is memory-safe but overused, discussing when it indicates bugs versus being misused instead of exceptions, and noting ClickHouse CI found bugs in every Rust library used." style="max-width: 100%" />
  <div><a style="float: right; text-decoration: none; border-bottom: none; padding-left: 1em;" href="https://presentations.clickhouse.com/2025-p99/index.html#14">#</a>
  <p class="slide-text">
  It looks like this. We added PRQL. Our fuzzer immediately found this query: `x -> y`. Any user can enter this query and it leads to a server crash. We don't need it. And we notify the author, the author fixes it. Not a big deal.
  </p>
  </div>
</div>

## Finding bugs through fuzzing

<div class="slide" id="15.svg">
  <img loading="lazy" src="/uploads/15_75654c7126.svg" alt="GitHub comment thread showing a discussion about avoiding panics in Rust code, with a referenced issue about SQL query panic found by ClickHouse fuzzer." style="max-width: 100%" />
  <div><a style="float: right; text-decoration: none; border-bottom: none; padding-left: 1em;" href="https://presentations.clickhouse.com/2025-p99/index.html#15">#</a>
  <p></p>
  </div>
</div>

## Sanitizers in mixed Rust/C++ Code

<div class="slide" id="16.svg">
  <img loading="lazy" src="/uploads/16_fa70fb03b4.svg" alt="Slide explaining that sanitizers like MSan and ASan require all code including Rust to be compiled with instrumentation, necessitating compilation from source, though this has become easier by 2025." style="max-width: 100%" />
  <div><a style="float: right; text-decoration: none; border-bottom: none; padding-left: 1em;" href="https://presentations.clickhouse.com/2025-p99/index.html#16">#</a>
  <p class="slide-text">
  Okay, sanitizers. Rust does not actually need sanitizers if you write in pure Rust. But if you write in C++ and just link a Rust library, you have to use sanitizers in C++. Sanitizers is like the inherent part of C++. And all the code must be compiled with sanitizers, including Rust. If you generate data from Rust, it has to be instrumented so the C++ code with memory sanitizer knows that the memory is initialized. And it was a problem three years ago, but now in 2025, it is not a problem. There is a toolchain with memory sanitizer for Rust. You specify a single option, and it does this stuff.
  </p>
  </div>
</div>

## Cross-compilation challenges

<div class="slide" id="17.svg">
  <img loading="lazy" src="/uploads/17_f5486e6f2c.svg" alt="Slide discussing cross-compilation challenges, noting it's easier in Rust than C++ but still requires arcane knowledge due to diverse build systems and implicit assumptions." style="max-width: 100%" />
  <div><a style="float: right; text-decoration: none; border-bottom: none; padding-left: 1em;" href="https://presentations.clickhouse.com/2025-p99/index.html#17">#</a>
  <p class="slide-text">
  Cross-compilation. Some people might think that cross-compilation in Rust or Go is something new, but it is not new. In C++ cross-compilation existed for at least 20 years, maybe 30 years. It was always a solved problem. But it was not an easy problem to solve. Many build systems have implicit assumptions and just forget about the possibility of cross-compilation. It's like cross-compilation is not first class in C++. You can do everything. You can set up cross-compilation in C++, it is easy. We did it, and actually we use it every time. Even if the host and target are equal, we do cross-compilation just for reproducible builds. For Rust it is easier, but if you use Rust together with C++, you have to just repeat everything twice. And it is quite annoying.
  </p>
  </div>
</div>

## Linkage of common dependencies

<div class="slide" id="18.svg">
  <img loading="lazy" src="/uploads/18_a6788fe8f9.svg" alt="Slide explaining dependency linkage issues where ClickHouse uses vendored OpenSSL but delta-kernel-rs's reqwest dependency links system OpenSSL, breaking hermetic builds." style="max-width: 100%" />
  <div><a style="float: right; text-decoration: none; border-bottom: none; padding-left: 1em;" href="https://presentations.clickhouse.com/2025-p99/index.html#18">#</a>
  <p class="slide-text">
  Common dependencies. What if you use a special version of OpenSSL that you like for compliance certifications? But you use a Rust library that has a transitive dependency, and this dependency tries to link with system OpenSSL. I don't like it. Should not happen. And it is actually not a problem. You can switch this library to use RustTLS. But how to switch it to use your own OpenSSL? It is possible. I will not explain the details—it is possible, it is one of the complications.
  </p>
  </div>
</div>

## Code composability

<div class="slide" id="19.svg">
  <img loading="lazy" src="/uploads/19_7eb8827ed7.svg" alt="Slide about code composability challenges when large codebases with established conventions integrate complex libraries like delta-kernel-rs that may break those conventions, though this isn't inherently a Rust problem." style="max-width: 100%" />
  <div><a style="float: right; text-decoration: none; border-bottom: none; padding-left: 1em;" href="https://presentations.clickhouse.com/2025-p99/index.html#19">#</a>
  <p class="slide-text">
  Composability of the code. It is about a lot of conventions, a lot of small details. How you ensure that the code behaves in a way it should behave in your system. Like how does it track allocated memory? How does it spawn threads, maintain connection pools, do HTTP requests? And if you include a new complex library, it might break your conventions. And this is not a problem with Rust. It is just more likely to happen if you combine two different language ecosystems.
  </p>
  </div>
</div>

## Small surprises: Symbol names in PRQL

<div class="slide" id="20.svg">
  <img loading="lazy" src="/uploads/20_ec522fed4b.svg" alt="Slide titled "Small surprises" showing extremely long, complex symbol names from PRQL code compilation, demonstrating verbose naming conventions." style="max-width: 100%" />
  <div><a style="float: right; text-decoration: none; border-bottom: none; padding-left: 1em;" href="https://presentations.clickhouse.com/2025-p99/index.html#20">#</a>
  <p class="slide-text">
  There are small problems that were quite surprising. For example, when we linked with PRQL, the binary size increased significantly.
  </p>
<p>

And when I looked at the list of symbols (compiler functions in the binary), I found this. This is the code generated with some sort of parser combinator library. And it is probably named chumsky by the name of the person and the problem this symbol itself it's name is about hundreds of kilobytes that we had to fix.</p>


  </div>
</div>

## Dependencies (SBOM)

<div class="slide" id="21.svg">
  <img loading="lazy" src="/uploads/21_6ff0af2470.svg" alt="Slide showing SQL queries counting licenses, revealing 156 non-Rust vendor licenses and 672 Rust vendor dependencies, discussing Rust's modularity advantages and dependency management." style="max-width: 100%" />
  <div><a style="float: right; text-decoration: none; border-bottom: none; padding-left: 1em;" href="https://presentations.clickhouse.com/2025-p99/index.html#21">#</a>
  <p class="slide-text">
  What about dependencies? When we only used C++ we had 156 dependent C++ libraries. It is a lot. But when we added Rust, the number of dependencies, even only Rust dependencies, became almost 700. And on the one hand, it is a huge advantage of Rust. It is modular, composable. People write code in a single way, not like in C++ when everyone writes in their own way. Actually, it is not that bad. It is not as bad as npm, but it is still not like peace of mind with just about a hundred dependencies.
  </p>
  </div>
</div>

## Takeaways

<div class="slide" id="22.svg">
  <img loading="lazy" src="/uploads/22_50d59675f5.svg" alt="Final slide with key takeaways: Rust is great, ClickHouse wasn't rewritten in Rust, but Rust can be used within ClickHouse, with GitHub repository link." style="max-width: 100%" />
  <div><a style="float: right; text-decoration: none; border-bottom: none; padding-left: 1em;" href="https://presentations.clickhouse.com/2025-p99/index.html#22">#</a>
  <p class="slide-text">
  Okay, actually, Rust has its problems. It is inevitable — every new technology has its problems — but Rust is a great language. And introducing it incrementally, we did not rewrite ClickHouse in Rust. We just opened the door for Rust, and now if you like Rust, if you love it, you can write in Rust in ClickHouse, and we will be really grateful. We will really appreciate if you do your contributions in Rust in our codebase. We are ready for that. We are not like smug C++ engineers. You are very welcome to be a ClickHouse contributor. Thank you.
  </p>
  </div>
</div>
