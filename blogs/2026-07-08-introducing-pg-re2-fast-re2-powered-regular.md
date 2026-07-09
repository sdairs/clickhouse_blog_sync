---
title: "Introducing pg_re2, fast, RE2-powered regular expressions in Postgres"
date: "2026-07-08T18:12:04.068Z"
author: "David Wheeler and Philip Dubé"
category: "Engineering"
excerpt: "Introducing pg_re2, a Postgres extension that brings ClickHouse's fast RE2-powered regular expressions to Postgres, with benchmarks and pg_clickhouse pushdown integration."
---

# Introducing pg_re2, fast, RE2-powered regular expressions in Postgres

Speed is a feature that motivates much of ClickHouse product design and
engineering. One can plainly see this attention to performance in our
development of benchmarks, such as [ClickBench] and [PostgresBench], some of
which have become industry standards. Unsurprisingly this ethos reaches the
deepest crevices of our products, down to SQL functions and operators.

In that spirit, we've introduced [pg_re2], a Postgres extension providing fast
[RE2]-powered [regular expressions] in Postgres. Install it from
[PGXN][pg_re2] or [GitHub]; [ClickHouse Managed Postgres] already has it.

You can install it like so:

<pre><code type='click-ui' language='sql'>
CREATE EXTENSION re2;
</code></pre>

Then you're ready to go!

<pre><code type='click-ui' language='sql'>
SELECT 'HouseQuake' @~ 'Quake\b';
</code></pre>

<pre style="overflow-x:auto;white-space:pre"><code class="hljs language-shell mb-9 border border-solid border-neutral-750" style="word-break:normal;white-space:pre"> ?column? 
----------
 t
(1 row)
</code></pre>

Hit [the docs] for the full list of features.

Of course, Postgres itself provides a wealth of [regular expression operators
and functions][pgre]. Why provide an alternate? Two reasons: speed, of course,
but also compatibility.

## The need for speed {#the-need-for-speed}

Ultimately, the Postgres and RE2 regular expression engines rest on
fundamentally different search algorithms. Postgres [POSIX] regular
expressions depend on [backtracking], returning the longest match, while RE2
relies on [finite automata]. In his [article announcing RE2] back in 2010,
[Russ Cox] summarized:

> RE2 demonstrates that it is possible to use automata theory to implement
> almost all the features of a modern backtracking regular expression library
> like PCRE. Because it is rooted in the theoretical foundation of automata,
> RE2 provides stronger guarantees on execution time than and enables
> high-level analyses that would be difficult or impossible with ad hoc
> implementations. Finally, RE2 is [open source]. Have fun!

Such findings underpin the choice to power ClickHouse [string search], [string
replacement], [string extraction], and [string splitting] with RE2. We wanted
to provide similar benefit to our Postgres users.

### Benchmark {#benchmark}

Naturally, the [pg_re2 project][GitHub] includes a [benchmark] that compares
the raw performance of its RE2-backed regex functions to the Postgres native
functions. This graph summarizes the horizontal speedup factors on an AWS
m6g.2xlarge instance with PostgreSQL 18:

![RE2 Speedup over PostgreSQL Builtin Regex](https://clickhouse.com/uploads/pg_re2_jul2026_image1_fa7bcb65f4.png)

Findings:

*   **RE2 wins every test**, with performance 1.8x to 8.6x that of Postgres.

*   The largest gains come from **extract_all** (7.2-8.6x) which returns
    arrays directly, in contrast to the *admittedly unfair* comparison to the
    Postgres `regexp_matches(..., 'g')` function's set-returning overhead.

#### Indexing {#indexing}

[pg_re2 v0.4.0] adds a matching operator, `@~`, to complement the Postgres `~`
operator, along with btree and GIN [index support] to reduce the need for
table scans when evaluating RE2 regular expressions. A second benchmark
compares RE2 to Postgres regular expression index performance on the same
server:

![RE2 Index Scan Speedup over PostgreSQL](https://clickhouse.com/uploads/pg_re2_jul2026_image2_9fd86a3a47.png)

Findings:

*   **RE2 again wins every test**, with 1.1x to 1.8x acceleration over the
    equivalent Postgres operations.

*   **Prefix** matching against a btree index provides similar overall speedup
    to a table scan because each applies raw execution speed to index entries.

*   The `gin_re2_ops` GIN opclass benefits from collecting the byte-equivalent
    **trigrams that RE2 requires,** including across punctuation, such that
    patterns like `error_code=42[0-9]` use the index where Postgres regular
    expressions against the `pg_trgm` opclass fall back to a full table scan.

*   On **plain-word patterns** the RE2 `gin_re2_ops` and Postgres `pg_trgm`
    opclasses extract similar keys and `pg_trgm`'s cheaper consistent check
    can win (see `error_code=123` above).

Overall, the performance improvements identified by Russ Cox hold true for
regular expressions in Postgres, too.

## We are so compatible {#we-are-so-compatible}

The second driver for creating pg_re2 was compatibility with ClickHouse
regular expression functions. Turns out that [RE2] differs from [Postgres
POSIX expressions][pgre] not only in speed but also syntax. These variations
matter because [pg_clickhouse v0.2.0] added [pushdown] for several PostgreSQL
operators and functions. It works well for simple regexen:

<pre><code type='click-ui' language='sql'>
SELECT id, by FROM log.entries WHERE by ~ 'Click' ORDER BY id;
</code></pre>

<pre style="overflow-x:auto;white-space:pre"><code class="hljs language-shell mb-9 border border-solid border-neutral-750" style="word-break:normal;white-space:pre"> id |     by     
----+------------
  1 | ClickHouse
  5 | MouseClick
 (2 rows)
</code></pre>

> If you'd like to follow along, the following examples use this ClickHouse
> table:
>
> <pre><code type='click-ui' language='sql'>
> CREATE TABLE entries (
>     id UInt32 NOT NULL,
>     by String NOT NULL
> ) ENGINE = MergeTree ORDER BY (id);
>
> INSERT INTO entries VALUES
>     ( 1, 'ClickHouse' ),
>     ( 2, 'HouseQuake' ),
>     ( 3, 'HouseQuake' ),
>     ( 4, 'QuakerOats' ),
>     ( 5, 'MouseClick' );</code></pre>
> And this pg_clickhouse foreign table configuration in Postgres:
> <pre><code type='click-ui' language='sql'>
> CREATE EXTENSION pg_clickhouse;
> CREATE EXTENSION re2;
> CREATE SERVER ch FOREIGN DATA WRAPPER clickhouse_fdw OPTIONS(driver 'binary');
> CREATE USER MAPPING FOR CURRENT_USER SERVER ch;
> CREATE SCHEMA log;
> IMPORT FOREIGN SCHEMA "default" FROM SERVER ch INTO log;</code></pre>

It's also useful for simple anchored expressions like `^` and `$`:

<pre><code type='click-ui' language='sql'>
SELECT id, by FROM log.entries WHERE by ~ '^House' ORDER BY id;
</code></pre>

<pre style="overflow-x:auto;white-space:pre"><code class="hljs language-shell mb-9 border border-solid border-neutral-750" style="word-break:normal;white-space:pre"> id |     by     
----+------------
  2 | HouseQuake
  3 | HouseQuake
(2 rows)
</code></pre>

But sometimes pg_clickhouse returns unexpected results:

<pre><code type='click-ui' language='sql'>
SELECT id, by ~ 'Quake\b' FROM log.entries WHERE by ~ 'Quake\b';
</code></pre>

<pre style="overflow-x:auto;white-space:pre"><code class="hljs language-shell mb-9 border border-solid border-neutral-750" style="word-break:normal;white-space:pre"> id | ?column? 
----+----------
  2 | f
  3 | f
(2 rows)
</code></pre>

Here `by ~ 'Quake\b'` in the `WHERE` clause, which pushes down to ClickHouse,
returns true for two rows, but the same expression in the select list, which
executes in Postgres, surprisingly returns false! How could that be?

## Postgres POSIX vs. ClickHouse RE2 {#postgres-posix-vs-clickhouse-re2}

This perplexing outcome derives from a difference between the two engines. In
ClickHouse, `\b` represents a word boundary, while in Postgres it represents a
backspace character. Thus the `WHERE` expression pushed down to ClickHouse
returns true, while the `SELECT` expression that executes in Postgres does
not.

A panoply of such variations exists between these two engines. Quite a few of
the backslash features work differently or don't exist in one or the other:

|    Feature    |               Postgres                |           ClickHouse          |
| ------------- | ------------------------------------- | ----------------------------- |
| `\b`          | backspace                             | word boundary                 |
| `\B`          | Backslash                             | not word boundary             |
| `\cx`         | low-order 5 bits same as `x`          | 🚫                            |
| `\C`          | 🚫                                    | match a single byte           |
| `\uwxyz`      | character with hex value `0xwxyz`     | 🚫                            |
| `\Ustuvwxyz`  | character with hex value `0xstuvwxyz` | 🚫                            |
| `\m`          | beginning of word                     | 🚫                            |
| `\M`          | end of word                           | 🚫                            |
| `\y`          | word boundary                         | 🚫                            |
| `\Y`          | not word boundary                     | 🚫                            |
| `\Z`          | end of string                         | 🚫                            |
| `\1`, `\2` …  | backreference to nth capture          | 🚫                            |
| `\f`          | form feed                             | form feed                     |
| `\Q...\E`     | 🚫                                    | literal text                  |
| `\p{Foo}`     | 🚫                                    | Unicode character class `Foo` |
| `\pF`         | 🚫                                    | Unicode character class `F`   |
| `[:ascii:]`   | ASCII characters                      | ASCII characters              |

Both also support flags passed via `(?xyz)` or via an additional argument to
Postgres functions. But the flags deviate substantially:

| Flag |               Postgres              |             ClickHouse           |
| ---- | ----------------------------------- | -------------------------------- |
| `b`  | rest of regex is a basic regex      | 🚫                               |
| `c`  | case-sensitive matching             | 🚫                               |
| `e`  | rest of regex is an extended regex  | 🚫                               |
| `g`  | return all matches                  | 🚫                               |
| `i`  | case-insensitive matching           | case-insensitive                 |
| `m`  | historical synonym for `n`          | `^` and `$` match begin/end line |
| `n`  | newline-sensitive matching          | 🚫 (use `m`)                     |
| `p`  | partial newline-sensitive matching  | 🚫                               |
| `q`  | rest of regex is literal text       | 🚫                               |
| `s`  | non-newline matching (default)      | let `.` match `\n` (default)     |
| `t`  | tight syntax (e.g., not expanded)   | 🚫                               |
| `w`  | inverse partial newline-sensitive   | 🚫                               |
| `x`  | expanded syntax                     | 🚫                               |
| `U`  |  🚫                                 | ungreedy                         |

The wording for flags supported by both engines differs, but *seems* to amount
to the equivalent behaviors. For example, PostgreSQL's term "non-newline
matching" means the pattern is insensitive to and therefore *does* match
newlines. These documentation differences complicate validation of the
behaviors difficult without testing!

But wait, there's more! A few examples:

*   ClickHouse doesn't support arbitrary lookahead or lookbehind assertions
    (`(?=re)`, `(?!re)`, `(?<=re)`, and `(?<!re)`)
*   ClickHouse doesn't support backreferences (`\1`, `\2`, etc.), such as one
    might use to pair quotation marks: `(["'])(.*?)\1`; but both
    support them in replacement expressions
*   Collations and locales determine the non-ASCII characters included in
    Postgres character classes, while ClickHouse RE2 character classes contain
    only ASCII characters.

## Consequences {#consequences}

These variations constitute a fraction of the differences between the two
regular expression engines. Clearly one must be wary of them when querying
[pg_clickhouse] tables. Test your regular expressions thoroughly, especially
when using flags, character classes, and backslash features.

To simplify the problem (or maybe create [two problems]), we've added [pg_re2]
function pushdown to [pg_clickhouse v0.3.0]. Using [pg_re2] functions for
columns in [pg_clickhouse] tables provides multiple benefits over pushing down
Postgres regex functions:

*   No need to determine whether pushdown is happening or not, as the behavior
    matches on both databases
*   RE2 delivers asymptotically better performance; we might have
    [mentioned](#the-need-for-speed) that fact
*   For ClickHouse use cases, one need only grapple with a single regex syntax

The benefits become clear when revisiting the unanticipated results that
started [this section](#we-are-so-compatible):

<pre><code type='click-ui' language='sql'>
SELECT id, by ~ 'Quake\b' FROM log.entries WHERE by ~ 'Quake\b';
</code></pre>

<pre style="overflow-x:auto;white-space:pre"><code class="hljs language-shell mb-9 border border-solid border-neutral-750" style="word-break:normal;white-space:pre"> id | ?column? 
----+----------
  2 | f
  3 | f
(2 rows)
</code></pre>

Note again that `~` returns true when pushed down to ClickHouse, but false
when executed in Postgres. Replacing the Postgres `~` operator with the re2
extension's `re2match()` function still pushes down to the ClickHouse [match
function]:

<pre><code type='click-ui' language='sql'>
SELECT id, re2match(by, 'Quake\b')
FROM log.entries where re2match(by, 'Quake\b');
</code></pre>

<pre style="overflow-x:auto;white-space:pre"><code class="hljs language-shell mb-9 border border-solid border-neutral-750" style="word-break:normal;white-space:pre"> id | re2match 
----+----------
  2 | t
  3 | t
(2 rows)
</code></pre>

But because the re2 extension uses the same [RE2] library as ClickHouse, the
query now returns consistent results: `re2match()` returns true when executing
in Postgres *and* when pushed down to ClickHouse.

## Let's go! {#lets-go}

The [re2 extension][pg_re2] derives from our goal to synthesize Postgres &
ClickHouse as cooperating parts of a single, high performance data platform.
It thus duplicates the full suite of ClickHouse regex functions described in
the [string search], [string replacement], [string extraction], and [string
splitting] documentation, and its test suite draws from ClickHouse's existing
regex tests.

We therefore wholeheartedly recommend using [pg_re2] where possible for faster
regex execution on Postgres. Even more so for analytical queries to ensure
performance and pushdown remain consistent once the data migrates to
ClickHouse.

  [ClickBench]: https://benchmark.clickhouse.com "ClickBench — a Benchmark For Analytical DBMS"
  [PostgresBench]: https://postgresbench.clickhouse.com "PostgresBench — A Reproducible Benchmark for Postgres Services"
  [pg_re2]: https://pgxn.org/dist/re2/ "re2 extension on PGXN"
  [RE2]: https://github.com/google/re2/wiki/Syntax "RE2 Syntax"
  [regular expressions]: https://en.wikipedia.org/wiki/Regular_expression "Wikipedia: Regular expression"
  [GitHub]: https://github.com/ClickHouse/pg_re2 "re2 extension on GitHub"
  [ClickHouse Managed Postgres]: https://clickhouse.com/docs/cloud/managed-postgres "ClickHouse Docs: Managed Postgres"
  [pgre]: https://www.postgresql.org/docs/current/functions-matching.html#FUNCTIONS-POSIX-REGEXP
    "PostgreSQL Docs: POSIX Regular Expressions"
  [POSIX]: https://www.regular-expressions.info/posix.html "POSIX Basic Regular Expressions"
  [the docs]: https://pgxn.org/dist/re2/doc/re2.html "re2 extension Documentation"
  [backtracking]: https://en.wikipedia.org/wiki/Backtracking "Wikipedia: Backtracking"
  [finite automata]: https://en.wikipedia.org/wiki/Finite-state_machine "Wikipedia: Finite-state machine"
  [article announcing RE2]: https://swtch.com/~rsc/regexp/regexp3.html
    "Regular Expression Matching in the Wild"
  [Russ Cox]: https://swtch.com/~rsc/ "Russ Cox"
  [open source]: https://github.com/google/re2/blob/main/LICENSE "RE2’s BSD 3-Clause  License"
  [string search]: https://clickhouse.com/docs/sql-reference/functions/string-search-functions
    "ClickHouse Docs: Functions for Searching in Strings"
  [string replacement]: https://clickhouse.com/docs/sql-reference/functions/string-replace-functions
    "ClickHouse Docs: Functions for string replacement"
  [string extraction]: https://clickhouse.com/docs/sql-reference/functions/string-functions#regexpExtract
    "ClickHouse Docs: regexpExtract"
  [string splitting]: https://clickhouse.com/docs/sql-reference/functions/splitting-merging-functions
    "ClickHouse Docs: Functions for splitting strings"
  [benchmark]: https://github.com/ClickHouse/pg_re2/tree/main/benchmark
  [pg_re2 v0.4.0]: https://github.com/ClickHouse/pg_re2/releases/tag/v0.4.0 "pg_re2 v0.4.0 on GitHub"
  [index support]: https://pgxn.org/dist/re2/0.4.0/doc/re2.html#Index.Support "re2 Documentation: Index Support"
  [two problems]: https://regex.info/blog/2006-09-15/247 "Source of the famous “Now you have two problems” quote"
  [pg_clickhouse v0.2.0]: https://github.com/ClickHouse/pg_clickhouse/releases/tag/v0.2.0
    "pg_clickhouse v0.2.0 on GitHub"
  [pushdown]: https://whatisdatabase.com/optimizing-database-performance-with-pushdown-techniques
    "Optimizing Database Performance with Pushdown Techniques"
  [pg_clickhouse]: https://clickhouse.com/docs/cloud/managed-postgres/extensions/pg_clickhouse
    "ClickHouse Docs: pg_clickhouse reference documentation"
  [pg_clickhouse v0.3.0]: https://github.com/ClickHouse/pg_clickhouse/releases/tag/v0.3.0
    "pg_clickhouse v0.3.0 on GitHub"
  [match function]: https://clickhouse.com/docs/sql-reference/functions/string-search-functions#match
    "ClickHouse Docs: match"


---

## Try Postgres managed by ClickHouse

ClickHouse + Postgres has become the unified data stack for applications that scale. With Managed Postgres now available in ClickHouse Cloud, this stack is a day-1 decision.

[Sign up](https://clickhouse.com/cloud/postgres?loc=blog-cta-1234-try-postgres-managed-by-clickhouse-sign-up&utm_blogctaid=1234)

---