---
title: "@clickhouse/rowbinary: when your library is also a parser compiler"
date: "2026-07-14T20:59:26.414Z"
author: "Peter Leonov"
category: "Engineering"
excerpt: "We've released @clickhouse/rowbinary a Node.js reader and writer for ClickHouse's RowBinary formats. You can import it and call its generic parser like any other library. But it also ships as an Agent Skill: point a coding agent at the bundled `SKILL.md` "
---

# @clickhouse/rowbinary: when your library is also a parser compiler

We've released [@clickhouse/rowbinary](https://www.npmjs.com/package/@clickhouse/rowbinary), a Node.js reader and writer for ClickHouse's [RowBinary](https://clickhouse.com/docs/interfaces/formats/RowBinary), RowBinaryWithNames, and RowBinaryWithNamesAndTypes formats. You can import it and call its generic parser like any other library. But it also ships as an Agent Skill: point a coding agent at the bundled `SKILL.md` and, instead of calling the library, the agent reads it and writes a parser specialized to your query's exact column types. Those generated parsers run 1.5–3.4x faster than composing the library's functions in a loop, cost about $0.20 each to generate, and avoid the silent data-corruption bugs that models produce when they write binary decoders from memory.

## Why we built it

RowBinary is one of the most efficient ways to get data out of ClickHouse, and one of the most annoying formats to consume from JavaScript. The wire format itself is simple: little-endian primitives, [LEB128](https://en.wikipedia.org/wiki/LEB128) varints for variable widths, no per-row overhead. The pain is on the reader side. Every leaf type has its own read pattern. `Nullable`, `Array`, `Map`, `Tuple`, and `LowCardinality` nest arbitrarily. `DateTime64` needs precision-aware scaling and an optional timezone. The `Variant`, `Dynamic`, and `JSON` types are self-describing and recursive: each value carries its own type tag and dispatches back into the same parsing machinery.

So most applications fall back to JSON formats, which cost real CPU time and, worse, silently round `UInt64` values past `Number.MAX_SAFE_INTEGER` to `float64` unless you take the slow stringify-then-reparse path. Teams that do adopt RowBinary end up with a generic, type-dispatched parser: one function per type, dispatched per cell at runtime. It's easy to maintain and hard to make fast, because every cell pays a dispatch and V8's inliner gives up on the [megamorphic](https://people.dsv.su.se/~beatrice/python/dls15_large_images.pdf) call sites. What you actually want at high QPS is a parser [monomorphized](https://en.wikipedia.org/wiki/Monomorphization) to your query: the right read operations inlined in the right order for your exact columns, with no dispatch at all. Nobody writes these by hand, per query, for every query they ship.

That's the gap this package closes. The library gives you correct, tested reading primitives for the whole ClickHouse type system. The skill teaches a coding agent to assemble those primitives into the hand-tuned, query-specific parser you'd never write yourself.

## What it is and how to use it

The package has two layers.

The first is a library of type-specific reading primitives: one small function per leaf type, plus composable wrappers for `Nullable`, `Array`, `Map`, `Tuple`, and the rest of the type algebra, in full-buffer and chunked-stream variants. Each primitive is written to be monomorphizable (small, single-purpose, free of megamorphic dispatch) so it can be inlined into a query-specific parser without defeating V8's optimizer. This layer is a perfectly usable library on its own: import it, call `parseRowBinary(...)`, get correct results. It also exports writers, streaming in both directions, and a dynamic RowBinaryWithNamesAndTypes pipeline built on [@clickhouse/datatype-parser](https://www.npmjs.com/package/@clickhouse/datatype-parser).

The second layer is the [SKILL.md](https://github.com/ClickHouse/clickhouse-js/blob/main/skills/clickhouse-js-node-rowbinary/SKILL.md). Rather than describing how to call the API, it teaches a coding agent the policy for assembling the primitives into a bespoke parser for a given query's column types. The comments in the library source explain why each block looks the way it does and which axes are safe to change: buffer ownership, `BigInt` vs `number` for 64-bit integers, `Date` mapper hooks, `Decimal` scale handling, `Array` materialization strategy, fast paths for fixed-width columns. The library is the reference implementation, the comments are the design rationale, and the `SKILL.md` is the codegen policy.

To install:

```shell
npm i @clickhouse/rowbinary
```

The skill is registered in the package's `agents.skills` field, so any agent that scans `node_modules` for skills finds it automatically. You can also add it directly:

```shell
npx skills add ClickHouse/clickhouse-js --skill clickhouse-js-node-rowbinary
```

### What the agent generates

Take the orders schema from our benchmarks:

```sql
id     UInt8
uid    UUID
price  Decimal64(2)
status Enum8('new' = 1, 'shipped' = 2, 'done' = 3)
```

Composing the library's public API gives you a correct parser, and it's the obvious thing to write:

```ts
export const readOrderRow: Reader<OrderRow> = (s) => ({
  id: readUInt8(s),
  uid: formatUUID(readUUID(s)),
  price: readDecimal64(2)(s),   // closure rebuilt every row
  status: readInt8(s),
});
```

But every field does its own bounds check, `readDecimal64(2)` builds a fresh closure per row, and `formatUUID` goes through `BigInt`. With the skill loaded, the agent notices that every column is fixed-width and emits this instead:

```ts
export const readOrderRowFast: Reader<OrderRow> = (s) => {
  const { buf, view } = s;
  // Every column is fixed-width: 1 + 16 + 8 + 1 = 26 bytes.
  // One bounds check for the whole row, then read at constant offsets.
  const o = advance(s, 26);
  const id = buf[o]!;
  const uid = formatUUIDTable(buf.subarray(o + 1, o + 17)); // table, not BigInt
  const price: DecimalValue = [view.getBigInt64(o + 17, true), 2];
  const status = view.getInt8(o + 25);
  return { id, uid, price, status };
};
```

One bounds check for the whole 26-byte row, reads at constant offsets, the Decimal scale baked in, and a lookup-table UUID formatter. The output is byte-identical to the composed version and 3.41x faster.

Because the parser is specialized anyway, `.map()`-style transformations are free: rename a column, derive a field, or drop one you never use, and the transformation moves into the read loop at zero extra cost, with zero extra options added to the library.

A few properties worth knowing before you adopt it:

- **The generated parser is a regular piece of code.** A human commits it, and it's reviewed, tested, and benchmarked like any other module. The skill produces source you read, not a binary you trust. The library ships a comprehensive test suite you can borrow to cover the now app-owned reader.  
- **The skill is auditable.** It's a markdown file plus densely commented, tested TypeScript, all in the npm tarball.  
- **The generic reader still works.** Skip the agent entirely and call `parseRowBinary(...)` for a known-good path. The skill is multiplicative, not a replacement.  
- **It works best with a model that can read the whole library** and follow multi-step reference instructions. Small models degrade, but with focused sub-agents they remain viable: Haiku's pass rate jumped from 52% to 86%.

## How we got here

### The conventional answer is a compiler

Schema-driven binary formats have a standard playbook for producing monomorphized parsers: build a codegen compiler. That's the shape `protoc`, `flatc`, and Cap'n Proto all adopted: take a schema, run a compiler, emit specialized code per target language. It works, but a codegen compiler is a real piece of software, with a parser for the schema language, an IR, a backend per target language, an options matrix, a release cadence, and a maintainer queue. Every degree of customization a user wants (a different decimal library, a custom `Date` mapper, `BigInt` vs `number` for `Int64`, eager vs lazy `Array` materialization, a string-interning table for `LowCardinality`) has to be designed as a flag, named, documented, kept stable across versions, and tested against every other flag.

We could have built one for RowBinary in JavaScript. Instead, we decomposed the compiler into artifacts an agent can read and recombine at inference time: densely commented primitives and a markdown file. The customization surface stops being a fixed list of flags and becomes a conversation with a model that has read your library. If you want `Decimal128` mapped to a custom big-decimal library, or `DateTime64(9)` as nanoseconds-in-`BigInt`, or `LowCardinality(String)` materialized through a string-interning table, those aren't flags we have to ship. The agent handles them in a few hundred tokens because it understands the comments in `decimal.ts`. 

### What the eval told us

We benchmarked three decode paths on 50k rows per schema: the correct JSON path (server-side stringification of wide integers, client-side re-parse to `BigInt`), the generic RowBinary reader composed from the library API, and the agent-generated monomorphic parser. Hardware and versions are listed at the end of the post.

RowBinary beats JSON by 3.3x on a wide-integer financial ledger schema on an Apple M4 Max ([benchmark source](https://github.com/ClickHouse/clickhouse-js/blob/8c51d9a12e67e82ef431e8158d5b77ce26e40e3a/skills/clickhouse-js-node-rowbinary/tests/ledger.bench.ts)) and by 2.5x on a 4-core AMD EPYC 7763 in CI ([run](https://github.com/ClickHouse/clickhouse-js/actions/runs/28439460847/job/84273435913#step:9:40)). The gap widens with newer hardware because RowBinary's work is pointer arithmetic and contiguous memory reads, while JSON's is branchy tokenization and `BigInt` allocation. An IoT schema holds a steadier ~2.1x on both machines. Note that these numbers compare against the *correct* JSON path. Bare `JSONEachRow` looks closer at 1.8x, but it silently rounds every `UInt128`, `Int128`, and any `UInt64` past `Number.MAX_SAFE_INTEGER` to `float64`. The decode succeeds, the numbers are wrong, and nothing complains until you compare totals against the server.

The agent-generated parser then beats the composed reader by another 1.5–3.4x:

| Schema | Shape | Speedup vs composed reader |
| :---- | :---- | :---- |
| Financial ledger | Wide integers (`UInt128`, `Int128`) | 1.55x |
| IoT telemetry | `Float64` / integers | 2.46x |
| Orders | Fixed-width, denormalized | 3.41x |

Every numeric-heavy schema we tested came in at 1.5x or better. RowBinary doesn't win everywhere, though. On a string-heavy log schema, `JSONCompactEachRow` beats even the optimized RowBinary reader, and the skill's own guidance says not to use RowBinary there. The skill knows its own boundaries.

Generation cost, averaged across four numeric-heavy schemas with Claude Sonnet 4.6: ~230k tokens in (almost all served from the prompt cache across the agent loop; the unique skill footprint per call is ~28k), ~2.1k tokens out, **$0.20 per parser** with caching and $0.72 as an uncached upper bound. Regenerating per deploy is well within budget.

The eval also showed why the skill matters beyond speed. RowBinary stores a UUID as two little-endian `UInt64` halves, each byte-reversed relative to the text form. Asked to write that decoder purely from memory, with no documentation, tools, or test-and-fix loop, Sonnet 4.6 got the byte order wrong in 3 of 5 runs, each time producing the same silently corrupt output: the 16 wire bytes hexed in order, formatted as a perfectly plausible UUID string. Opus 4.8 was reliable at 5 of 5. With the skill loaded, every run is correct by construction, because the reference primitive sits in the library two function calls away from where the agent is reading.

That failure mode is why we care about this more than the speedup. ClickHouse users run these parsers against billions of rows. A JSON path that rounds `UInt128` to `float64` produces totals that are off by a little across millions of records, and someone notices six weeks later when a finance report doesn't balance. A UUID decoder that hexes the wire bytes in source order produces strings that pass schema validation and quietly break join predicates. These are the bugs that make teams refuse to put AI-generated code on the data path at all. The skill addresses them by making the generated parser a recombination of the official, tested, code-reviewed primitives we maintain. When you review the generated parser in a PR, you're reviewing code assembled from code we wrote.

### What the skill cost to produce

A fair objection is that a capable enough coding agent should be able to write this parser without any skill at all. It can, and that's how the skill got built. Claude Code with Opus, given the RowBinary spec and the ClickHouse source as reference, produced a working reader. It took a few million tokens, roughly a day of continuous prompting, several rounds of test-writing and benchmark-tweaking, and a human reviewing each iteration.

The skill is the compiled artifact of that day. It bakes in the accumulated lessons (LEB128 reads, Decimal scale handling, which integer widths need `BigInt`, how V8 inlines and doesn't) that a model would otherwise rediscover from scratch every time. A compiler is amortized engineering in the same way: someone spent months teaching it the type system and the codegen rules so that every user downstream gets specialized output cheaply. Here the investment was a day of human-AI collaboration, frozen into markdown and commented code, and everyone downstream gets it for a $0.20 inference call.

### Where this fits

Agent Skills landed as a format in October 2025 and became an open standard in December 2025. The most common pattern so far is *ship a `SKILL.md` alongside your npm package so the agent calls your API correctly*: Vercel Labs's `skills` CLI, antfu's `skills-npm`, `npm-agentskills`, and similar. Those are useful, and we already ship one of that shape: [clickhouse-js-node-troubleshooting](https://github.com/ClickHouse/clickhouse-js/tree/main/skills/clickhouse-js-node-troubleshooting), a runbook the agent consults when something breaks.

`@clickhouse/rowbinary` is a different shape: library-as-reference rather than library-as-API. Instead of treating the library as a black box to call, the agent treats it as a transparent reference implementation to fork per query. That changes how you should write code if you're authoring a skill like this. Code meant to be called needs an honest description. Code meant to be read needs dense comments, internal consistency, and no cleverness that doesn't reproduce.

We expect the pattern to generalize. Anywhere you'd have reached for a codegen compiler (narrow, schema-driven, performance-sensitive output), there's now an alternative that costs a markdown file and an inference call. If you find places where the skill produces bad output, the comments in the library are where fixes go; please [file an issue](https://github.com/ClickHouse/clickhouse-js/issues).

### Benchmark environment

Local: Apple M4 Max, Node v24.6.0, macOS 26.5.1, ClickHouse 26.1.1.200. CI: AMD EPYC 7763 (4 vCPU), Node v24.17.0, ClickHouse 26.6.1.1193 ([bench workflow](https://github.com/ClickHouse/clickhouse-js/blob/8c51d9a12e67e82ef431e8158d5b77ce26e40e3a/.github/workflows/bench-skill-rowbinary.yml), [latest run](https://github.com/ClickHouse/clickhouse-js/actions/runs/28439460847)). Source pinned at [`8c51d9a`](https://github.com/ClickHouse/clickhouse-js/tree/8c51d9a12e67e82ef431e8158d5b77ce26e40e3a). 50k rows per schema via `npm run bench`.  