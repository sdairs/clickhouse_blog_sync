---
title: "The new cost-based join optimizer with reordering support for non-inner joins"
date: "2026-10-28T14:12:53.749Z"
author: "Fisnik Kastrati"
category: "Engineering"
excerpt: "ClickHouse’s new exhaustive cost-based join optimizer safely reorders inner, outer, semi, and anti joins to find the cheapest valid plan."
---

# The new cost-based join optimizer with reordering support for non-inner joins

> **TL;DR:** ClickHouse’s new cost-based join optimizer (CBO) is built on an efficient implementation of DPsub, an exhaustive dynamic-programming algorithm. For queries with up to 12  tables, it finds the cheapest plan under the existing cost model and will be enabled by default in the upcoming 26.10 release.
> <br><br>
> Until now, join reordering worked only across inner joins, and every other join type acted as an optimization barrier. The new optimizer also reorders `LEFT`, `RIGHT` and `FULL` outer joins, as well as `SEMI` and `ANTI` joins. A *conflict detector* makes this safe. It admits only reorderings that preserve the query result (**correctness**) and finds every valid plan in the search space (**completeness**). Both properties are proven, and testing on more than 90,000 join trees and 2.8 million candidate plans found no invalid or missing plans.

---

## Why a database needs a query optimizer

SQL is declarative: a query says *what* result it wants, not *how* to compute it. Between the two sits the query optimizer. It turns the query into an execution plan, a tree of operators such as scans, filters, joins and aggregations, and for any non-trivial query there are many logically equivalent plans that compute exactly the same result. Filters can be applied before a join or after it, a join can build its hash table from either input, joins can run in different orders, with different algorithms.

These plans return the same rows, but their cost can differ by orders of magnitude, because they move very different amounts of data through the pipeline. The optimizer's job is to find a cheap one, and it needs three things for that:

- a **search space**: the plans that are equivalent to the query;
- a **cost model**: an estimate of how expensive each plan is, built on estimates of how many rows each operator produces (from table statistics, indexes, or heuristics);
- a **search strategy**: a way to find a cheap plan in that space without trying every one.

![A query optimizer turns a SQL query into a physical plan](https://clickhouse.com/uploads/join_optimizer_query_to_physical_plan_dark_9957570454.png)

## **Join ordering: searching billions of plans without trying them all.**

No decision matters more than the order of the joins. Different orders produce intermediate results of very different sizes. Joining the two largest tables first may materialize billions of rows, while joining a large table with a small, selective one first may shrink it to a few thousand rows before the expensive join happens. Smaller intermediate results mean less work and less memory, so the optimizer’s goal is to minimize their size.

No other decision also has a bigger search space. Joining *n* tables one after the other already allows *n*! orders. Once a join may combine two intermediate results (a *bushy* plan), the number of distinct join trees is *n*! · C(*n*−1), where C is the Catalan number counting the tree shapes. This simplifies to (2*n*−2)! / (*n*−1)!. For 10 tables that is 3,628,800 left-deep orders, **but more than** 17.6 billion join trees. For 12 tables it is already about **28 trillion**.

There are two classic ways to search this space.

**Greedy optimization.** A greedy optimizer repeatedly joins the two inputs whose result is cheapest. It is fast and often good enough, but it commits early and never revisits a choice, so one locally attractive join can lock it into a poor overall plan. ClickHouse used a greedy optimizer by default.

**Dynamic programming.** A bottom-up, DP-based optimizer finds the cheapest order exactly. It rests on one observation: the best plan for joining a set of tables is built from the best plans of two smaller, disjoint subsets. Instead of enumerating every join tree, whose number grows factorially and reaches billions even for a dozen tables, it solves each subproblem once and reuses the answer. The procedure works in order of increasing subset size:

1. **Base case.** For each single table, the best plan is a scan of that table with its filters applied.
2. **Combine.** For every larger subset of tables, consider each way of splitting it into two non-empty, disjoint parts. Each split yields a candidate plan: join the best plan for the left part with the best plan for the right part, and estimate its cost from the estimated output size and the costs of the two sub-plans.
3. **Keep the winner.** Store the cheapest candidate for that subset. Both parts are smaller than the subset itself, so their best plans are already stored.
4. **Finish.** When the subset containing all tables is reached, its entry is the optimal join order.

Enumerators in this family differ mainly in how they walk through the search space. **DPsub** is the subset-driven variant. It represents every subset of tables as a bitmask, with one bit per table, so each subset is simply an integer between 1 and 2ⁿ−1. Enumerating all subsets means counting upward through these integers. For each subset, the candidate left sides of a split are its own sub-subsets, which can be generated by repeatedly subtracting one and masking with the subset, a trick that steps through all of them without skipping or repeating any. The right side is whatever remains, which is a single XOR with the left side.

What makes this attractive is how cheap the enumeration itself is. Incrementing a counter, subtracting one, ANDing two masks, XORing two masks and counting set bits are among the simplest operations a CPU has. Each typically compiles to a single instruction that completes in about one cycle, and a subset lives entirely in a register. There are no pointers to follow, no sets to allocate and no hashing. The best plan for each subset can be stored in an array indexed by the bitmask, which for 12 tables has only 4,096 entries and fits comfortably in the CPU cache. The search space is still large, since the number of splits grows roughly as 3ⁿ, or about half a million for 12 tables, but the overhead of generating each split is only a handful of cycles. This is why the optimizer can examine every subset and every split exhaustively instead of pruning aggressively.

The simplicity has a price. DPsub also generates splits whose two sides are not connected by any join predicate, so a practical implementation skips those to avoid Cartesian products. And because the work grows exponentially, exhaustive DP is only practical for a limited number of tables: DPsub in ClickHouse enumerates the subsets of up to 12 tables.

> Callout: ClickHouse’s new Join Reordering algorithm is built on an efficient implementation of DPsub. For queries with up to 10 tables (up to 12 if `query_plan_optimize_join_order_limit` raised), it finds the cheapest plan under the existing cost model.

Let's review an example using the TPC-H [dataset](https://clickhouse.com/docs/get-started/sample-datasets/tpch) and compare intermediate result sizes for two join orders for the same TPC-H query. You can see that "Selective table first" approach saves ~100× smaller intermediate results for the query.

![Two join orders for the same TPC-H query and their intermediate result sizes](https://clickhouse.com/uploads/join_optimizer_tpch_join_orders_dark_468d7a69c4.png)

## Beyond inner joins: the Conflict Detector

An exhaustive search, though, can only be as good as the space it is allowed to search, and for most real queries, that space was missing a whole class of joins!

#### The problem

Join order can change a query’s runtime by orders of magnitude. Inner joins make this easy to exploit: they are commutative (`A ⋈ B` equals `B ⋈ A`) and associative (`(A ⋈ B) ⋈ C` equals `A ⋈ (B ⋈ C)`), so every order returns the same result, and the optimizer only has to find the cheapest one.

Many real queries also use other join types, whose behavior depends on which rows have no match on the other side:

| Join type | What it returns |
| --- | --- |
| **Left outer** | Every row from the left table. If there is no match on the right, the right-hand columns are filled with `NULL`(if `join_use_nulls = 1`) |
| **Full outer** | Every row from both tables. Rows without a match are padded with `NULL` on the missing side. |
| **Semi** | Each matching left row once, with the right-hand columns of its first match, with no right-hand columns and no duplicates. This is what `WHERE EXISTS (...)` or `IN (...)` means. |
| **Anti** | Only the left rows that have no match on the right. This is what `WHERE NOT EXISTS (...)` means. |

Left outer, semi and anti joins are not commutative: `A LEFT JOIN B` keeps all rows of `A`, while `B LEFT JOIN A` keeps all rows of `B`. They are often not associative either. Take `(A LEFT JOIN B) JOIN C ON B.x = C.x`. Rows of `A` with no partner in `B` get `NULL` for `B.x`, so the inner join with `C` discards them. If the optimizer instead computes `B JOIN C` first and left-joins `A` onto the result, those rows of `A` survive. The two plans return different results, so the second is not a valid reordering.

To reorder such joins at all, the optimizer needs to answer one question for every candidate join it considers: *is this reordering valid?* The component that answers it is called a **conflict detector**. It changes the search space in two directions. Compared with treating every join as freely reorderable, it makes the space smaller: every invalid reordering it rules out is a part of the space that no longer has to be explored. Compared with treating every non-inner join as a barrier, as ClickHouse did until now, it makes the space larger: all the valid reorderings the barriers hid become available. The optimizer explores more plans than before, and every one of them returns the right result.

## The gap we are closing

Until now, ClickHouse optimized semi and anti joins in a separate phase, outside the inner-join graph:

- The optimizer flattens a join tree into one graph of tables to reorder, but admitted only plain joins: a semi or anti child was never flattened in.
- A semi or anti join at the top capped the graph at two tables: no reassociation, only swapping its two inputs.
- So every semi or anti join was an **optimization barrier**. The query was split into islands of inner joins, each optimized on its own, with the semi and anti joins pinned where the query wrote them.

The consequence: a selective semi or anti join could not be pushed past the inner joins feeding it, so the plan built the full intermediate result first.

Take this query:

```sql
SELECT sum(big.v + mid.v)
FROM big
INNER JOIN mid ON big.k = mid.k
LEFT SEMI JOIN tiny ON big.k = tiny.k
```

`big` and `mid` share their join keys, so `big JOIN mid` is huge; `tiny` holds only a handful of keys, so the semi join throws away almost all of it. With the semi join pinned on top, the plan builds `big JOIN mid` first. Letting the semi join into the join-order search lets the optimizer filter `big` first:

![The semi join pushed below the inner join shrinks the intermediate result about 496 times](https://clickhouse.com/uploads/join_optimizer_semi_join_496x_dark_4295238c90.png)

|  | plan | largest intermediate |
| --- | --- | --- |
| without conflict detector | (big ⋈ mid) ⋉ tiny | 503,768,186 rows |
| with conflict detector | mid ⋈ (big ⋉ tiny) | 1,015,092 rows |

That is a **~496× smaller intermediate result**, with the same join enumerator both times: the only difference is that the semi join takes part in the search. The result is identical.

## Building on research

Our conflict detector is based on [**On the Correct and Complete Enumeration of the Core Search Space**](https://dl.acm.org/doi/10.1145/2463676.2465314) (SIGMOD 2013). The paper showed that earlier approaches could miss valid plans or admit invalid ones, and presented a conflict detector that is provably both correct and complete.

The paper defines the *core search space*: every plan reachable from the original join tree through the algebraic transformations that are valid for its operators. Its conflict detector generates exactly that space, no more and no less. This is the detector we implemented, covering inner, left/right/full outer and left/right semi and anti joins.

## How the detector works

### Four rules

Whether two adjacent joins can be swapped or regrouped without changing the result depends on their types and, in some cases, on whether their predicates reject NULLs. The detector checks four properties to determine which transformations are safe. In the expressions below, ∘ᵃ and ∘ᵇ denote join operators, and e₁, e₂ and e₃ their inputs. The comm property describes a single operator type; the other three are stored in matrices indexed by pairs of operator types:

- **comm**: is the operator commutative? (`a ⋈ b = b ⋈ a`)
- **assoc**: `(e₁ ∘ᵃ e₂) ∘ᵇ e₃ = e₁ ∘ᵃ (e₂ ∘ᵇ e₃)`?
- **l-asscom**: `(e₁ ∘ᵃ e₂) ∘ᵇ e₃ = (e₁ ∘ᵇ e₃) ∘ᵃ e₂`?
- **r-asscom**: `e₁ ∘ᵃ (e₂ ∘ᵇ e₃) = e₂ ∘ᵇ (e₁ ∘ᵃ e₃)`?

Consider this query over `customers`, `orders` and `payments`:

```sql
SELECT customers.id, orders.id, payments.order_id
FROM customers
LEFT JOIN orders ON customers.id = orders.customer_id
INNER JOIN payments ON orders.id = payments.order_id
SETTINGS join_use_nulls = 1
```

With `join_use_nulls = 1`, unmatched rows are padded with NULLs. Plan A below follows the query's written join order; Plan B is a proposed reordering that the detector must reject. These simplified logical plans show the joins and scans, omitting the final projection. They are **not equivalent**.

**Plan A — original**

```text
Inner join [orders.id = payments.order_id]
├── Left outer join [customers.id = orders.customer_id]
│   ├── Scan customers
│   └── Scan orders
└── Scan payments
```

**Plan B — invalid reordering of Plan A**

```text
Left outer join [customers.id = orders.customer_id]
├── Scan customers
└── Inner join [orders.id = payments.order_id]
    ├── Scan orders
    └── Scan payments
```

For a customer with no orders, Plan A creates a row with NULL order fields, then discards it at the inner join because it cannot match a payment. Plan B joins orders to payments first, then preserves that customer at the left join. The detector must reject Plan B as an alternative to Plan A because it changes the result: assoc(⟕, ⋈) is false.

Now consider a different query, with the join types in the other order:

```sql
SELECT customers.id, orders.id, payments.order_id
FROM customers
INNER JOIN orders ON customers.id = orders.customer_id
LEFT JOIN payments ON orders.id = payments.order_id
SETTINGS join_use_nulls = 1
```

For this query, Plan C follows the written order and Plan D is a valid reordering:

**Plan C — original**

```text
Left outer join [orders.id = payments.order_id]
├── Inner join [customers.id = orders.customer_id]
│   ├── Scan customers
│   └── Scan orders
└── Scan payments
```

**Plan D — valid reordering of Plan C**

```text
Inner join [customers.id = orders.customer_id]
├── Scan customers
└── Left outer join [orders.id = payments.order_id]
    ├── Scan orders
    └── Scan payments
```

Plans C and D keep only customers with orders, and preserve each matching order even when it has no payment: assoc(⋈, ⟕) is true. The detector can therefore admit Plan D as an alternative to Plan C.

If both joins are left joins, regrouping is also safe with the same equality conditions. A missing order cannot match a payment because `orders.id = payments.order_id` rejects NULLs. A condition that could match a NULL-padded order would invalidate that guarantee: assoc(⟕, ⟕) holds only under null rejection. This is why the rules depend on both the join types and how their conditions handle NULLs.

Our implementation stores these rules as static data, one row for comm and three matrices, letting the detector check each proposed transformation rather than assume that every regrouping is safe.

### From matrices to a validity test

Before enumeration starts, the detector walks the query's original join tree. For every operator it records the left and right input subtrees, the tables its ON clause references, and the tables on which the clause rejects NULLs. Then, for every pair of operators where the matrices forbid a transformation, it records a conflict.

Each operator requires, on each side, only the tables its ON clause references there, and each conflict is recorded separately as a rule *"if any table of T₁ is already joined, all of T₂ must be too"*. In Plan A, for example, the inner join gets the rule *"if **`orders`** is joined, **`customers`** must be too"*, which rejects Plan B's `orders ⋈ payments`. Keeping the conflicts as separate, conditioned rules, instead of folding them all into the required sets, is what makes the detector complete: it rejects a plan only when a conflict actually applies to it. The validity test is applied every time the enumerator considers joining a set of tables S₁ with a set S₂:

```text
required_left ⊆ S₁  ∧  required_right ⊆ S₂   (or mirrored, with LEFT ↔ RIGHT)
∧  every conflict rule of the operator is obeyed by S₁ ∪ S₂
```

If the test passes, the operator applied at that split decides the kind and strictness of the resulting join. The test is a few bitmask operations, so it adds almost nothing to the enumeration.

### Fitting it into DPsub

DPsub enumerates subsets of tables as bitmasks and, for every subset, finds the cheapest way to build it from two smaller connected subsets. With the detector in place, the whole join tree reaches DPsub as one graph of tables: both sides of every outer, semi and anti join, and `FULL` joins too. A few more pieces were needed:

- **Cross products.** A `CROSS JOIN` joins on nothing, so it adds no edge to the graph. We link its two sides explicitly, as a join of selectivity 1, so the graph stays connected and DPsub can move the cross product to wherever it is cheapest, while it is still executed and reported as a `CROSS JOIN`.
- **The build side.** DPsub's cost model charges a join the same whichever way round its inputs go, so after the search we put the smaller input on the build side of the hash join, mirroring outer joins `LEFT` ↔ `RIGHT`, but never for `ANY`, `SEMI` and `ANTI` joins, whose meaning depends on the side.
- **Bounded search.** DPsub with the detector plans join trees of up to 12 tables, semi, anti and outer joins included. A larger join tree is left to the greedy optimizer.

## Validation I: against the theory

A detector that is wrong even once returns wrong results, so we validated it the way the paper does. For a given number of tables *n*, a harness:

- generates every initial join tree: all tree shapes × all operator assignments × all binary equi-predicates;
- enumerates the entire core search space of each tree;
- and checks every candidate plan three independent ways: the shipped detector, an independent reference implementation that defines the core search space, and execution on random databases with NULLs.

It counts the plans generated outside the core search space (**invalid**, must be 0), the core plans it fails to generate (**missing**), and any plan that fails execution (must be 0).

### Small operator set

Inner, left outer and anti joins:

| tables | join trees | core plans | invalid | missing |
| --- | --- | --- | --- | --- |
| 3 | 30 | 94 | 0 | 0 |
| 4 | 495 | 4,696 | 0 | 0 |
| 5 | 11,010 | 377,434 | 0 | 0 |
| 6 | 2,000 | 145,657 | 0 | 0 |
| 7 | 2,000 | 618,710 | 0 | 0 |

### Large operator set

Inner, left/full outer, semi and anti joins:

| tables | join trees | core plans | invalid | missing |
| --- | --- | --- | --- | --- |
| 3 | 80 | 243 | 0 | 0 |
| 4 | 2,080 | 16,207 | 0 | 0 |
| 5 | 72,320 | 1,615,294 | 0 | 0 |
| 6 | 2,000 | 77,194 | 0 | 0 |
| 7 | 2,000 | 228,662 | 0 | 0 |

(For rows representing 6 and 7 tables, join trees are sampled.) Across all experiments, **the detector generated every one of the 2.8 million core plans and not a single invalid one, and no plan failed execution**.

## Validation II: on the real engine

### Differential fuzzing

A fuzzer generates random multi-way join queries mixing `INNER`, `LEFT`, `RIGHT`, `FULL`, `SEMI` and `ANTI` joins, including ON clauses that reference only one side, over real data with NULLs, duplicate and non-matching keys. Each query runs three ways, compared with an order-independent, NULL-safe checksum computed inside ClickHouse:

- **base**: the written order, no reordering, as the ground truth;
- **greedy**: the existing default optimizer;
- **DPsub**: DPsub with the conflict detector.

1,200 queries of up to 7 tables: **0 mismatches**.

### Search space

How much more of the search space does the detector open up on the real optimizer? Counting the valid plans DPsub explores, for 1,200 sampled queries with 3 to 7 tables:

| tables | queries | no detector | conflict detector | gain |
| --- | --- | --- | --- | --- |
| 3 | 389 | 757 | 757 | 1.00× |
| 4 | 403 | 1,283 | 1,583 | 1.23× |
| 5 | 396 | 1,633 | 2,883 | 1.77× |
| 6 | 407 | 3,228 | 8,868 | 2.75× |
| 7 | 405 | 2,678 | 30,816 | 11.51× |

At 7 tables, **the conflict detector lets DPsub consider 11.5× more valid plans** than it could without one: the more joins a query has, the more good plans the barriers used to hide.

![Valid plans explored by DPsub with and without the conflict detector](https://clickhouse.com/uploads/join_optimizer_dpsub_search_space_e0355c483a.png)

### Tests

Stateless tests in CI check, among others, that every pair of join kinds reaches DPsub as one graph with unchanged results, that `ANY`/`SEMI`/`ANTI` strictness is preserved, `join_use_nulls`, degenerate predicates and cross products.

## Results

Back to our semi-join query:

```sql
SELECT sum(big.v + mid.v)
FROM big
INNER JOIN mid ON big.k = mid.k
LEFT SEMI JOIN tiny ON big.k = tiny.k
```

but now evaluated against the previous default, i.e., the greedy optimizer. On a data set with 3 million rows in `big` and `mid` and 100 keys in `tiny`, greedy keeps the semi join on top of `big JOIN mid`:

```text
Join (left semi)
├── Join (inner)
│   ├── ReadFromMergeTree (big)
│   └── ReadFromMergeTree (mid)
└── ReadFromMergeTree (tiny)
```

DPsub with the conflict detector moves it below the inner join:

```text
Join (inner)
├── ReadFromMergeTree (mid)
└── Join (left semi)
    ├── ReadFromMergeTree (big)
    └── ReadFromMergeTree (tiny)
```

|  | greedy | DPsub + conflict detector | speedup |
| --- | --- | --- | --- |
| runtime join filters off | 0.133 s | 0.035 s | 3.8× |
| runtime join filters on (default) | 0.044 s | 0.037 s | 1.2× |

ClickHouse's runtime join filters, which push the keys of a hash table down to the scan on the other side, already recover part of the bad order on this query; the better plan does not depend on them.

On the TPC-DS (SF1) and TPC-H (SF1/SF10) queries of our performance tests, compared with the greedy default:

| query | greedy | DPsub + conflict detector | change |
| --- | --- | --- | --- |
| TPC-H Q2 | 143 ms | 65 ms | −55% |
| TPC-DS Q73 | 260 ms | 143 ms | −45% |
| TPC-H Q5 | 574 ms | 320 ms | −44% |
| TPC-DS Q86 | 93 ms | 57 ms | −39% |
| TPC-DS Q65 | 302 ms | 227 ms | −25% |

## Using it

Our new DPsub with the conflict detector is the default Cost-Based Optimizer (CBO) for joins starting with 26.10 release:

```sql
SET query_plan_optimize_join_order_algorithm = 'dpsub,greedy';  -- greedy is the fallback for large Joins
SET query_plan_optimize_join_order_conflict_detector = 'c';     -- setting to'' turns it off
```

If you want to compare with the previous behavior, you can switch it off per query.  To get more details and look at the join order, kind and strictness of every join run with  `EXPLAIN actions = 1`:

```sql
EXPLAIN actions = 1
SELECT ...
SETTINGS query_plan_optimize_join_order_algorithm = 'greedy',
         query_plan_optimize_join_order_conflict_detector = ''
```
