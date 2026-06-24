---
title: " What's New in pg_clickhouse v0.3.2: Postgres 19, TLS, Regex, and Memory"
date: "2026-06-23T11:25:40.021Z"
author: "David Wheeler"
category: "Engineering"
excerpt: "The latest pg_clickhouse releases bring JSONB, date/time, and array function pushdown, plus HTTP result set streaming for lower memory usage."
---

#  What's New in pg_clickhouse v0.3.2: Postgres 19, TLS, Regex, and Memory

Last week we shipped the latest version of [pg_clickhouse], the interface for
querying [ClickHouse] from [Postgres]. As a minor update, [v0.3.2][gh]
requires no reload, restart, or `ALTER EXTENSION UPDATE`, and we've upgraded
all of the ClickHouse Cloud instances. Your next connection to the database
will load the latest and greatest.

Despite the minor version increment, this release significantly improves
pg_clickhouse in four key areas: Postgres 19, TLS connections, regular
expression pushdown, and memory consumption.

## Postgres 19

The topline change? Support for [PostgreSQL 19 Beta1]. The new Postgres
version required relatively minor revisions to the pg_clickhouse source code
to take advantage of tuple and array optimizations, remove old typedefs, add
new headers, and some test outputs. And with that, we'll be ready for the
final Postgres release this fall and ship day one on Manged Postgres for
ClickHouse.

## TLS connections

[pg_clickhouse] has supported TLS connections since its first release, but
[v0.3.2][gh] introduces a couple of new `CREATE SERVER` options:

*   `secure` specifies the security requirement for a connection: `on` (force
    TLS), `off` (force plaintext), or `auto` (cloud-host/port heuristic, the
    default). Thanks to [Andrey Borodin] for the inspiring [pull request].
*   `min_tls_version` specifies a minimum TLS protocol version: `TLSv1`,
    `TLSv1.1`, `TLSv1.2`, or `TLSv1.3`. It defaults to the TLS library's own
    minimum.

## Regular expressions

More in-depth exploration of the differing behaviors of regular expression
flags revealed errors in our pushdown logic, now repaired. The [Postgres
flags] now push down to ClickHouse as follows:

| Flag | As    | Notes                                                          |
| ---- | ----- | -------------------------------------------------------------- |
| `i`  | `i`   | case-insensitive matching                                      |
| `m`  | `m-s` | `^` and `$` match begin/end line in addition to begin/end text |
| `n`  | `m-s` | Postgres alias for `m`                                         |
| `p`  | `-s`  | don't let `.` and `[^x]` match `\n`                            |
| `s`  | `s`   | let `.` and `[^x]` match `\n`                                  |
| `t`  |       | tight syntax, ignored                                          |
| `w`  | `m`   | inverse partial newline-sensitive matching                     |

The [documentation] also notes the variation in the behaviors of `m` and `p`,
in which Postgres prevents negated character classes (`[^xyz]`) from matching
a newline, while the ClickHouse equivalents do not. Be sure to carefully test
regular expressions that use character classes.

## Memory consumption

A couple of customer queries revealed some memory consumption issues.

One was triggered by using unbuffered queries with the HTTP driver. Such a
configuration has not been recommended or the default since v0.1.10, so should
be quite rare.

The other issue arose when a foreign scan repeatedly re-scanned, as in a
nested-loop join with a parameterized inner foreign scan --- a fairly typical
plan. Be sure to upgrade if you notice memory ballooning while querying a
foreign table.

## And more

Other changes worth mentioning:

*   Added the `compression` option to `CREATE SERVER` to enable ClickHouse
    native protocol compression for query results and `INSERT` data
*   Added mapping to push down `regexp_match()` when its regex argument
    contains no capturing groups
*   Fixed a bug where `ANY()` with an empty array (`WHERE x = ANY('{}')`)
    produced an error in Clickhouse prior to version 25

Download from the usual locations:

*   [PGXN]
*   [GitHub]
*   [Docker]

  [pg_clickhouse]: https://clickhouse.com/docs/cloud/managed-postgres/extensions/pg_clickhouse "pg_clickhouse on PGXN"
  [ClickHouse]: https://clickhouse.com/clickhouse "ClickHouse: The fastest open-source analytical database"
  [Postgres]: https://www.postgresql.org/
    "PostgreSQL: The World's Most Advanced Open Source Relational Database"
  [gh]: https://github.com/ClickHouse/pg_clickhouse/releases/tag/v0.3.2 "pg_clickhouse on GitHub"
  [PGXN]: https://pgxn.org/dist/pg_clickhouse/0.3.2/ "pg_clickhouse 0.3.2 on PGXN"
  [GitHub]: https://github.com/ClickHouse/pg_clickhouse/releases/tag/v0.3.2
    "pg_clickhouse 0.3.2 on GitHub"
  [Docker]: https://github.com/ClickHouse/pg_clickhouse/pkgs/container/pg_clickhouse
    "pg_clickhouse OCI Images"
  [documentation]: https://pgxn.org/dist/pg_clickhouse/doc/pg_clickhouse.html#Regular.Expressions
    "pg_clickhouse: Regular Expressions"
  [Postgres flags]: https://www.postgresql.org/docs/current/functions-matching.html#POSIX-EMBEDDED-OPTIONS-TABLE
    "PostgreSQL Docs: ARE Embedded-Option Letters"
  [PostgreSQL 19 Beta1]: https://www.postgresql.org/about/news/postgresql-19-beta-1-released-3313/
    "PostgreSQL 19 Beta 1 Released!"
  [Andrey Borodin]: https://x4mmm.medium.com
  [pull request]: https://github.com/ClickHouse/pg_clickhouse/pull/227
    "ClickHouse/pg_clickhouse#227 feat: add three-state secure option (on/off/auto) for TLS control"

---

## Try Postgres managed by ClickHouse

ClickHouse + Postgres has become the unified data stack for applications that scale. With Managed Postgres now available in ClickHouse Cloud, this stack is a day-1 decision.

[Get access](https://clickhouse.com/cloud/postgres?loc=blog-cta-994-try-postgres-managed-by-clickhouse-get-access&utm_blogctaid=994)

---