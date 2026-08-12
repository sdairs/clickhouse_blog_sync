---
title: "What's new in pg_clickhouse v0.10.0: Subqueries, TPC-H Speedups, C Driver, and Aggregates"
date: "2026-08-11T17:40:40.622Z"
author: "Josh Ventura"
category: "Engineering"
excerpt: " Discover what's new in pg_clickhouse v0.10.0: 16 of 22 TPC-H queries now push down in full, plus a rebuilt C driver and broader aggregate support."
---

# What's new in pg_clickhouse v0.10.0: Subqueries, TPC-H Speedups, C Driver, and Aggregates


Continuing our investment in pg\_clickhouse, improving pushdown coverage for analytic workloads has remained our top focus, with full pushdown across the TPC-H benchmark suite as our immediate metric. We've had a lot of progress since our last update in [June](https://clickhouse.com/blog/pg_clickhouse-whats-new-june-2026), including on the TPC-H scoreboard, which we haven't really talked about since [our introductory post](https://clickhouse.com/blog/introducing-pg_clickhouse#semi-join-pushdown) back in December, so that's where we'll start. With the release of v0.10.0, our scoreboard has moved from 12 of 22 TPC-H queries fully pushed down to 16, leaving only **6** to go to finish off the set.

Along the way, we also

- rebuilt the binary driver on a new plain-C client library,  
- more than doubled the surface area of functions and aggregates that push down,  
- hardened the binary driver against a couple of concurrency bugs, detailed below.

## The scoreboard

Three more TPC-H queries now fully push down. All three were exceedingly inefficient before because, due to the shape of the query, pg\_clickhouse had to fetch every row from ClickHouse individually and then evaluate the subquery on it locally ([full chart](https://github.com/ClickHouse/pg_clickhouse/#test-case-tpc-h)):

| Query | PostgreSQL | pg\_clickhouse 0.3 | pg\_clickhouse 0.10 | Pushdown |
| :---- | ----: | ----: | ----: | :---: |
| Q2 | 588 ms | 3,446 ms | 24 ms | ✔ |
| Q17 | 2107 ms | 32,709 ms | 37 ms | ✔ |
| Q22 | 270 ms | 1,415 ms | 45 ms | ✼ |

( ✔ \= whole query is a single foreign scan )  
( ✼ \= pushed down, but as more than one remote query; typically an outer scan plus one `InitPlan` scan.)

Q17 is the trophy: a correlated subquery averaging `l_quantity` per part that, back when it evaluated once per outer row against 6M line items at scale factor 1, took **32.7 seconds**. Fully pushed down, it's **37 milliseconds.** That's three orders of magnitude difference, and shows off a clear case where pg\_clickhouse outperforms native PostgreSQL's own plan for the same query (2.1s).

Six queries remain unpushed: Q13, Q15, Q16, Q18, Q20, Q21. Q16 and Q18 show us the way forward; pg\_clickhouse *already pushes down* the SQL shape they need (`IN` and `NOT IN` deparsed as anti/semi-joins, as in Q2 and Q17); what blocks them is that PostgreSQL flattens their subqueries into anti/semi-joins whose *inputs are themselves joins*, and the deparser doesn't yet walk a join tree on both sides of a join. Q15 and Q20 hit variants of the same issue. That's the next cohesive piece of subquery pushdown.

## Finishing the subquery story

[December's headline feature](https://clickhouse.com/blog/introducing-pg_clickhouse#semi-join-pushdown) was teaching the planner to push a whole correlated `EXISTS` subquery down as a single `LEFT SEMI JOIN` instead of a nested loop with one ClickHouse round trip per outer row. This moved the needle from 3 of 22 TPC-H queries all the way to 12\. The ten remaining queries shared one problem: the planner couldn't fold subqueries into a join at all, so it left a `SubPlan` behind. This is a piece of a query plan that describes a complete plan for a separate query that runs as part of executing the full query, usually once per row. Pushing that down was the fifth item on our roadmap, and we knocked it out ([\#289](https://github.com/ClickHouse/pg_clickhouse/pull/289)) as of this latest release (0.10.0). Now, subqueries in Postgres become subqueries in ClickHouse:

```sql
EXPLAIN (VERBOSE, COSTS OFF)
SELECT s.sale_id, s.amount FROM sales s
WHERE s.amount > (SELECT 1.5 * avg(s2.amount) FROM sales s2
                  WHERE s2.item_id = s.item_id)
ORDER BY s.sale_id;
```

```
 Foreign Scan on subplan_test.sales s
   Output: s.sale_id, s.amount
   Remote SQL: SELECT sale_id, amount FROM subplan_test.sales r1 WHERE ((r1.amount > (SELECT (1.5 * avg(q1_1.amount)) FROM subplan_test.sales q1_1 WHERE ((q1_1.item_id = (r1.item_id)))))) ORDER BY r1.sale_id ASC NULLS LAST
   SubPlan expr_1
     ->  Foreign Scan
           Output: ((1.5 * avg(s2.amount)))
           Relations: Aggregate on (sales s2)
           Remote SQL: SELECT (1.5 * avg(amount)) FROM subplan_test.sales WHERE ((item_id = {p1:Int32}))
(8 rows)
```

The `EXPLAIN` still shows the `SubPlan` node (that's just PostgreSQL's bookkeeping for the correlation), but you can see the top `Remote SQL` contains the whole comparison, including the subquery, in one statement we ship to ClickHouse. The same mechanism enables pg\_clickhouse to push down the whole of TPC-H Q2: one `Foreign Scan` and one remote query. `NOT IN` gets the same treatment via a `LEFT ANTI JOIN` (the negated cousin of v0.1.0's semi-join) whenever the planner can prove the transformation safe.

> Note that none of this works below ClickHouse 25.8, which doesn't support the correlated-subquery SQL shape; `pg_clickhouse` checks the server version at plan time and falls back to local evaluation on older servers, the same as it always does for unsupported shapes.

### NOT IN, implemented correctly

Pushing down the SQL was the easy part. The harder part was making sure it computed the same answer PostgreSQL would ([\#315](https://github.com/ClickHouse/pg_clickhouse/pull/315), [\#317](https://github.com/ClickHouse/pg_clickhouse/pull/317)), and that was its own rabbit hole. ClickHouse's `IN` operates on two-valued logic, PostgreSQL's on three-valued. That means `x NOT IN (1, NULL)` can be `FALSE` (`x=1`) or `NULL` in PostgreSQL, but never `TRUE`. Pushed down naively, these expressions can silently invert results wherever a `NULL` is involved in a comparison, `WHERE NOT IN` returning rows PostgreSQL would filter out, `GROUP BY` merging a `NULL` group into `FALSE`, etc. None of it shows up in ordinary testing, which is exactly why it's dangerous in a pushdown extension; the plan looks right and the output is subtly wrong.

V0.10's fix tracks how each expression's result gets consumed, so we know how much hedging the query has to do to keep results consistent. This is where the rabbit hole took on a [menger sponge](https://en.wikipedia.org/wiki/Menger_sponge) vibe:

- A filter condition can treat `NULL` like `FALSE` for free, so ClickHouse behavior is fine in conditions outside of `NOT`.  
- A value position or a negation needs extra checking for null values to inject the correct Postgres value into the result.  
- If pg\_clickhouse can prove the operands can't be `NULL` (by tracing them to a non-NULL constant, or a column with a `NOT NULL` constraint that no outer join has re-nulled, or a non-nullable operation over these...), it can skip adding the guards that inject the Postgres behavior.

So a query with our guards and Postgres behavior implemented looks like this:

```sql
EXPLAIN (VERBOSE, COSTS OFF)
SELECT id FROM tnull WHERE xn NOT IN (1, NULL) ORDER BY id;
```

```
 Foreign Scan on in_null_test.tnull
   Output: id
   Remote SQL: SELECT id FROM in_null_test.tnull WHERE ((CASE WHEN xn IS NULL AND notEmpty([1,NULL]) THEN NULL WHEN countEqual([1,NULL], xn) > 0 THEN false WHEN countEqual([1,NULL], NULL) > 0 THEN NULL ELSE true END)) ORDER BY id ASC NULLS LAST
(3 rows)
```

While a common, NULL-free case can ship as a plain native `IN`:

```sql
EXPLAIN (VERBOSE, COSTS OFF)
SELECT id FROM tnull WHERE xn NOT IN (1, 500) ORDER BY id;
```

```
 Foreign Scan on in_null_test.tnull
   Output: id
   Remote SQL: SELECT id FROM in_null_test.tnull WHERE ((xn NOT IN (1,500))) ORDER BY id ASC NULLS LAST
(3 rows)
```

A follow-up ([\#317](https://github.com/ClickHouse/pg_clickhouse/pull/317)) generalized this behavior to the whole `IN` family of operators (`IN`, `NOT IN`, `= ANY`, `= ALL`, `<> ANY`, `<> ALL`), scalar and array forms alike, allowing them to push down unconditionally instead of falling back to local evaluation when non-nullability couldn't be proven.

Additionally, we had a little bug where `<> ANY(array)` actually computed `<> ALL`, which we knocked out while we were in the area.

All of this rests on the assumption that ClickHouse's `IN` actually behaves the two-valued way we've been describing. A server-level setting (`transform_null_in`) can change that. So we added `transform_null_in 0` to the default `pg_clickhouse.session_settings`, to make sure a ClickHouse server profile can't silently pull the rug out from under the guards we just described.

---

## Get started with ClickHouse Managed Postgres today

Interested in seeing how ClickHouse Managed Postgres works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?intent=pg&loc=blog-cta-1503-get-started-with-clickhouse-managed-postgres-today-sign-up&utm_blogctaid=1503)

---


## Broadening what pushes down

Alongside the join and subquery work, the list of individual functions, operators, and aggregates that push down grew substantially. Too substantially to list in full here (see the [CHANGELOG](https://github.com/ClickHouse/pg_clickhouse/blob/main/CHANGELOG.md) for detail), but here's a sample of where the breadth came from:

* **Regex:** We've covered a lot of updates here in our [earlier newspost](https://clickhouse.com/blog/introducing-pg_re2-regex-in-postgres), so give that a look\!

* **Aggregates:**  
  * **Statistical aggregates ([\#290](https://github.com/ClickHouse/pg_clickhouse/pull/290))**  
    * `corr`, `covar_pop`/`samp`  
    * `stddev_pop`/`samp`  
    * `var_pop`/`samp`  
    * `any_value`  
  * **Ordered-set aggregates ([\#291](https://github.com/ClickHouse/pg_clickhouse/pull/291)):** Mapped to ClickHouse's parametric forms.  
    * `percentile_cont`/`disc` → `quantile(s)`/`quantileExactLow`

* **Partitionwise aggregation ([\#298](https://github.com/ClickHouse/pg_clickhouse/pull/298)):** Useful if you've moved analytics-heavy partitions to ClickHouse and kept transaction-heavy partitions in Postgres. 
  * **Foreign partition compute:** A query aggregating over a partitioned table with a mix of local and foreign partitions now computes the foreign partition's share on ClickHouse instead of fetching its rows.  
    * This is for decomposable aggregates like `count`, `sum`, `min`, `max`, `avg` over integers.  
    * Requires `enable_partitionwise_aggregate`.

* **Everything else:**  
  * **Formatting and encoding:** `encode(bytea, 'hex'|'base64'|'base64url')` ([\#302](https://github.com/ClickHouse/pg_clickhouse/pull/302)).  
  * **Strings:** Three-argument `ltrim`/`rtrim`/`btrim` ([\#307](https://github.com/ClickHouse/pg_clickhouse/pull/307)),  
  * **Cost estimation:** Fixed some cost functions to keep the planner picking cheaper option for MIN/MAX on ClickHouse. ([\#310](https://github.com/ClickHouse/pg_clickhouse/pull/310))  
  * **Dates and times:**  
    * Interval arithmetic extended to `date`/`timestamp` operands and subtraction ([\#301](https://github.com/ClickHouse/pg_clickhouse/pull/301))  
    * Retuned the `CURRENT_*`/`now()`/`clock_timestamp()` family for session time zone and sub-second precision.

Beneath all of that lies an important architectural change: builtin function pushdown is now opt-in ([\#245](https://github.com/ClickHouse/pg_clickhouse/pull/245)). Early on, any Postgres builtin whose name matched a ClickHouse function shipped by default, which meant a signature or behavioral difference could silently change results. The concrete case that forced the change was trig functions (`asin`/`acos`/`atanh`/`acosh`): Postgres raises an error when these are called on a value outside their domain, while ClickHouse returns `NaN`. Since v0.3.0, a function only pushes down if it's explicitly mapped, which is slower to grow the list but means the list is trustworthy in terms of preserving Postgres semantics.

## Driver Updates

Our introductory post described modernizing on the old clickhouse\_fdw lineage in part by adopting `clickhouse-cpp` for native-protocol access. That's already out of date: in v0.3.1, we replaced it wholesale with [ClickHouse/clickhouse-c](https://github.com/ClickHouse/clickhouse-c), a new C client vendored as a git submodule ([\#254](https://github.com/ClickHouse/pg_clickhouse/pull/254)). The switch wasn't just a dependency bump; mixing C++ exception handling with PostgreSQL's own `setjmp`/`longjmp`\-based error handling had been a source of crashes, and clickhouse-cpp's monolithic result buffering meant memory use scaled with result size. By contrast, clickhouse-c streams results block by block instead, and dropped the vendored library's build time and size by over 75%.

We continued that consolidation after the initial clickhouse-c switch: the HTTP driver now speaks ClickHouse's Native format, too: the same encoding and decoding the binary driver already used, in place of the old TSV-based path ([\#328](https://github.com/ClickHouse/pg_clickhouse/pull/328)). One casualty of that change is `fetch_size`, the batching option from the HTTP driver's earlier streaming work. The native decoder streams one curl chunk at a time regardless, so there's nothing left for that setting to configure, and it's now deprecated.  On the write side, the binary driver now flushes buffered `INSERT`/`COPY FROM` data past 64MiB ([\#303](https://github.com/ClickHouse/pg_clickhouse/pull/303)), instead of holding an entire batch in memory. Both drivers gained explicit `compression` (none/lz4/zstd) ([\#268](https://github.com/ClickHouse/pg_clickhouse/pull/268)) and TLS controls (`secure` \= on/off/auto, `min_tls_version`) ([\#272](https://github.com/ClickHouse/pg_clickhouse/pull/272)), replacing a heuristic that inferred TLS from the hostname and port. Type coverage widened as well: we now support multidimensional arrays for both reads and writes in both drivers ([\#233](https://github.com/ClickHouse/pg_clickhouse/pull/233)), and `Array(Nullable(T))` inserts over the binary protocol ([\#316](https://github.com/ClickHouse/pg_clickhouse/pull/316)).

Both drivers now sharing one binary encoding path is also what made several reliability fixes possible this cycle. Concurrent foreign scans on the binary driver (e.g. a correlated subquery or a nested-loop join over two foreign tables) used to collide on a single shared connection and crash; each concurrent scan now gets its own connection ([\#296](https://github.com/ClickHouse/pg_clickhouse/pull/296)), which also closed a related use-after-free in a rescanned foreign scan's batch memory context. We also have a fix for a particular query structure failing during execution due to choosing an invalid relation OID when choosing a user to run the query as ([\#319](https://github.com/ClickHouse/pg_clickhouse/pull/319)).

Getting more into the nitty-gritty, we also closed a subsecond-precision loss when inserting timestamps over HTTP ([\#300](https://github.com/ClickHouse/pg_clickhouse/pull/300)), and to top it all off, a broader static-analysis pass over the codebase turned up and fixed a handful of other latent bugs ([\#313](https://github.com/ClickHouse/pg_clickhouse/pull/313)); these hadn't showed up in the field, but were worth closing before they could.

## New surface area

A handful of additions expand what you can *do*, not just what pushes down automatically: `clickhouse_query(server, sql)` runs an arbitrary query against a configured server and types the result by your column definition list, now with binary-driver support ([\#309](https://github.com/ClickHouse/pg_clickhouse/pull/309)). That column definition list is unavoidable (Postgres needs to know the shape of the rows before it can start fetching them), but it also means `clickhouse_query()` has no way to run something like `CREATE TABLE`, which returns no rows and has no shape to declare. That's what its new companion, `clickhouse_perform(server, sql)`, is for: a procedure, called with `CALL` instead of `SELECT`, for statements you run for effect rather than for rows ([\#329](https://github.com/ClickHouse/pg_clickhouse/pull/329)). Additionally, largely for internal use in conditional logic, `clickhouse_server_version(server)` reports the connected server's version ([\#293](https://github.com/ClickHouse/pg_clickhouse/pull/293)).

If you've been using `clickhouse_raw_query()` for this, it's now deprecated and will be removed next release ([\#329](https://github.com/ClickHouse/pg_clickhouse/pull/329)). Move to `clickhouse_query()` or `CALL clickhouse_perform()` instead; both go through a configured foreign server, with its own connection handling and driver selection, rather than a raw, ad-hoc connection string.

## Old Surface Area

We've posted elsewhere about a number of these features from past releases, but forgot to mention them here, and wanted to set the record straight.

* **JSON:**  
  * **Operators and functions:** `->`/`->>` and `jsonb_extract_path[_text]()` map onto ClickHouse's [sub-column syntax](https://clickhouse.com/docs/sql-reference/data-types/newjson#reading-json-paths-as-sub-columns) ([\#169](https://github.com/ClickHouse/pg_clickhouse/pull/169), [\#176](https://github.com/ClickHouse/pg_clickhouse/pull/176)).  
  * **Types:** ClickHouse's native `JSON` type maps onto Postgres `json` with the same operator support.

* **Arrays:**  
  * **New functions and operators:** Over a dozen functions push down:  
    * `array_cat`  
    * `append`  
    * `remove`  
    * `to_string`  
    * `length`  
    * `hasAll`/`hasAny` for `@>`/`<@`/`&&`  
    * Slice syntax (`arr[L:U]`) as `arraySlice()`  
    * Still more...

* **Aggregates:**  
  * **Window functions ([\#175](https://github.com/ClickHouse/pg_clickhouse/pull/175)):** The full set pushes down, including these and their friends:  
    * `ROW_NUMBER`  
    * `RANK`  
    * `LEAD`/`LAG`  
    * `NTILE`  
  * **Booleans and String** ([\#184](https://github.com/ClickHouse/pg_clickhouse/pull/184)): `bool_and`,  `bool_or`, `string_agg`

* **Everything else:**  
  * `to_char()` with format-string validation ([\#244](https://github.com/ClickHouse/pg_clickhouse/pull/244))  
  * `split_part()` ([\#206](https://github.com/ClickHouse/pg_clickhouse/pull/206))  
  * `fuzzystrmatch`'s `soundex()`/`levenshtein()` ([\#210](https://github.com/ClickHouse/pg_clickhouse/pull/210)).

## What's left

Beyond the six remaining TPC-H queries, much of [the original roadmap](https://clickhouse.com/blog/introducing-pg_clickhouse#semi-join-pushdown) remains open: the remaining uncovered PostgreSQL functions, lightweight `DELETE`/`UPDATE`, and `UNION` pushdown. The join-tree-on-both-sides limitation blocking Q15/16/18/20 is the most consequential piece and the natural next post in this series, if we don't knock out all six by next release.
