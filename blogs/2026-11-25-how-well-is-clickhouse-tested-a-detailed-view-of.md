---
title: "How well is ClickHouse tested? A detailed view of increasing our own coverage"
date: "2026-11-25T17:13:02.569Z"
author: "Alexey Bakharev and James Cunningham"
category: "Engineering"
excerpt: "A deep dive into how ClickHouse measures and improves test coverage with LLVM instrumentation, per-test data, targeted CI, and AI-generated tests."
---

# How well is ClickHouse tested? A detailed view of increasing our own coverage

ClickHouse has about 2.6 million lines of C++ code, and more than 80 pull requests land in master every day. With such a codebase and such a pace, nobody can track by hand which features, components, and settings are covered with tests. Some PRs bring very good tests with the new code. Some do not. We understood that without knowing how good our tests are, we cannot judge how reliable our database is. So we measured it.

## Where does ClickHouse stand next to others?

We were able to gather the coverages of several popular databases in order to see where we landed among them.

| Database | Published coverage | Source |
| --- | --- | --- |
| SQLite | 100% branch coverage and MC/DC of the core library, in a defined configuration | [Testing documentation](https://www.sqlite.org/testing.html#coverage) |
| ClickHouse | 91.8% lines; 81.0% branches; 91.8% functions, 2026-11-12 | [coverage.clickhouse.com](https://coverage.clickhouse.com/) |
| DuckDB | 91% lines; 82.9% branches; 90.6% functions, default unit test suite, 2026-11-04 | [Coverage artifact of its CI](https://github.com/duckdb/duckdb/actions/runs/41748038561), no published page |
| Apache DataFusion | 83.3% lines, 2026-11-04 | [Codecov dashboard](https://app.codecov.io/gh/apache/datafusion) |
| PostgreSQL | 81.0% lines; 64.9% branches; 89.2% functions, 20devel, 2026-10-29 | [coverage.postgresql.org](https://coverage.postgresql.org/) |
| TiDB | 72.1% lines, 2026-11-04 | [Codecov dashboard](https://app.codecov.io/gh/pingcap/tidb) |
| MongoDB | Measured in its Evergreen CI with gcovr, no public report |  |

SQLite reports 100% branch coverage, which is very reasonable, given that it is a small library with a test suite written for that target. Among the big databases that measure and report their coverage, we were happy to find that ClickHouse and DuckDB are at the top, a little over one percentage point apart. Every project counts different directories and runs different test sets, so the numbers may differ in scope, but it’s great to see coverage expanded to such large areas for some of the industry’s most critical workloads.

Few databases actually publish their test coverage. The table lists the numbers we could find, next to our own. So if you’re reading this and thinking “hey, where is my favorite database??” let us know what you find so that we can add it!

## How do you measure the coverage of a C++ program?

Before we look at the report, it helps to know what coverage in C++ actually looks like. A compiler sorely lacks human eyeballs, so it sees a function very differently than we do.

### From basic blocks to counters

A compiler does not see lines, it instead sees a control flow graph. Each node is a basic block with a run of instructions with one entry at the top, one exit at the bottom, and no branch in between. A branch ends a block, and its edges lead to the next blocks, like so:

```c++
int f(int x)
{
    int y = 0;      // block A
    if (x > 0)
        y = x * 2;  // block B
    return y;       // block C
}
```

Block A ends with the `if`. One edge goes to block B, and the other jumps straight to block C. In LLVM IR, block C starts with a phi function:

```txt
%y = phi i32 [ %mul, %B ], [ 0, %A ]
```

A phi function picks a value by the edge the program came from: `%mul` after block B, and `0` when the condition was false. That is why coverage tools care about edges, not only blocks. A test with `x = 5` executes all three blocks, but it never takes the edge from A to C. The false outcome of the `if` lives on an edge with no code of its own. It’s details like these that make attempting to accurately understand coverage so… fun.

### Two sides of the same coverage coin

Clang offers two kinds of instrumentation, and ClickHouse unsurprisingly leverages both:

- SanitizerCoverage (`-fsanitize-coverage=trace-pc-guard`) works on LLVM IR. It splits such edges with an empty block and calls `__sanitizer_cov_trace_pc_guard` on every edge. The program implements the callback and decides what to record, which libFuzzer uses to guide its inputs. The callback only knows machine addresses, so they have to be symbolized back to source. Our first per-test coverage, `SANITIZE_COVERAGE`, [added in 2023](https://github.com/ClickHouse/ClickHouse/pull/56102), used it to record which functions each test called.
- Source-based coverage (`-fprofile-instr-generate -fcoverage-mapping`) works in the Clang front end, on the C++ source. It puts counters on source regions and stores a coverage mapping from the counters to file and line ranges in the binary. Not every block needs a counter of its own, though. The count of the false path above is the count of the `if` minus the count of block B, so the mapping stores it as an expression. In March, we merged [#99513](https://github.com/ClickHouse/ClickHouse/pull/99513) to move our per-test data to source-based coverage, and every number on this page now comes from it.

When configured with the above flags, we must perform some data massaging to get an actual report. First, the process must exit. Upon exiting with the supplied configuration above, the runtime writes its counters into a `.profraw` file. `llvm-profdata merge` then combines the raw files of many processes into one indexed `.profdata`. Finally, `llvm-cov` combines that profile with the binary, which carries the mapping, and produces a report: a text summary, annotated source, JSON, or an `lcov` tracefile that `genhtml` renders as HTML. If you are curious about what that report can actually look like, you can read more from the official [LLVM Coverage Mapping Format](https://llvm.org/docs/CoverageMappingFormat.html) docs from llvm.org. But be careful, “here be dragons” applies to pretty much all pieces of the LLVM website; even the icon.

To generate such a report in ClickHouse specifically, two CMake options are also supplied:

- `-DWITH_COVERAGE=ON` builds the binary for the report. It also adds `-mllvm -runtime-counter-relocation` for continuous mode (`%c` in `LLVM_PROFILE_FILE`), so a server that a test kills on purpose still leaves its profile behind. Third-party code in `contrib/` is built without instrumentation.
- `-DWITH_COVERAGE_DEPTH=ON` adds per-test collection. The server reads its own counters and coverage mapping at runtime, which powers `SYSTEM SET COVERAGE TEST` and the per-test table further down.

### What do these numbers actually mean?

Our report publishes three numbers, each measuring different things.

1. Line coverage asks whether each source line was executed at least once. This is the number everybody quotes when they talk about coverage percentage.
2. Function coverage asks whether each function was called at least once. But beware, as it is the coarsest measurement. A function with 200 lines and one call counts the same as a function with one line. A coverage report is not an indicator of importance of function or its popularity.
3. Branch coverage counts the outcomes of conditions that happened. Every condition has two outcomes, and each outcome is a branch. Its existence gives us a richer report than line coverage.

### How is the coverage collected in CI?

ClickHouse has three kinds of tests in the source repository: [functional tests](https://clickhouse.com/docs/resources/develop-contribute/contribute/continuous-integration#functional-stateless-tests) (over 17,000 files today), [integration tests](https://clickhouse.com/docs/resources/develop-contribute/contribute/continuous-integration#integration-tests) (nearly 1,200 modules), and unit tests. CI runs them in many configurations: with `Replicated` databases, with parallel replicas, with asynchronous inserts, on S3 storage, under every sanitizer. In total, CI executes about 80 million tests per day.

The coverage report uses the same tests and the same configurations as a normal CI run, on a binary built with `-DWITH_COVERAGE=ON`. 23 test shards run in parallel: one for unit tests, 14 for the functional suite in its configurations, and 8 for the integration modules. Each shard produces a profile, a merge job combines the 23 profiles into one tracefile and renders the HTML. The whole run takes about 2 hours and is repeated every 3 hours on the latest commit of master. The merge is all-or-nothing: if one profile is missing or corrupt, the job publishes nothing, because a partial measurement is worse than no measurement. Here is an [example](https://s3.amazonaws.com/clickhouse-test-reports/praktika.html?PR=130036&sha=latest&name_0=PR) of a CI report showing all LLVM shards and the final merge job.

## How can I see ClickHouse’s coverage?

The live report is at [coverage.clickhouse.com](https://coverage.clickhouse.com/). It is rebuilt every 3 hours from the latest commit of master, and every directory and file can be browsed line by line.

![ClickHouse coverage dashboard showing line, function, and branch coverage](https://clickhouse.com/uploads/coverage_dashboard_a728c26cca.png)

On November 12th, 2026, the tests of master crossed the threshold of 91.8% of all source lines; 91.8% of all functions and nearly 81% of all branches. In absolute numbers, that was 1,120,775 of 1,257,404 instrumented lines of `src/`, `programs/` and `base/`, with `contrib/` of course being discounted from our coverage reports.

If you care to notice, two steps in the coverage graphs stand out, but they are not new tests. The jump at the end of August came from a fix in the measurement itself: the profiles of servers that tests kill on purpose were lost before, and since late August, they are counted. The dip in late September came from excluding unit test sources and unused tools from the report, which removed about 107,000 lines that were not shipped code. Most of the improvement has come from the tireless work of our contributors, but we have had an ace up our sleeve when it comes to improving coverage.

## How do we improve the coverage?

A report is useful only if somebody acts on it. We built an AI agent that writes tests for uncovered code. It runs on [Nerve](https://github.com/ClickHouse/nerve), our self-hosted agent runtime, and is part of [ClickGap](https://clickhouse.com/blog/clickgap-autonomous-qa-for-clickhouse), our autonomous QA contributor.

While our little coverage agent is mighty, it is still a pretty young portion of ClickGap. Its first pull request, [#124221](https://github.com/ClickHouse/ClickHouse/pull/124221), was opened on October 6th. By November 3rd it has opened 17 pull requests, 16 of them merged and 1 open. Together they add 34 test files with about 2,900 lines of tests and close 41 coverage gaps. The coverage reports of these PRs add up to about 5,600 newly covered lines, between 260 and 890 per PR. Good robot.

Initially, the first evolution of ClickGap’s coverage agent produced standalone PRs to close single gaps, leading to isolated changes, but an explosion of review pressure. Starting in late October, the agent now batches its work: [#127806](https://github.com/ClickHouse/ClickHouse/pull/127806) adds 9 tests for 7 components, and its coverage report shows nearly 540 newly covered lines in 46 files. [#125583](https://github.com/ClickHouse/ClickHouse/pull/125583) has the most so far, with about 890 newly covered lines in 75 files.

The agent works in five steps:

1. The agent finds the gaps. It takes the four newest master coverage reports spread over the last day and looks for functions and `if`/`else` blocks with zero hits in all of them. A file is a candidate only if it is identical in all four commits, so a gap is never an artifact of a fresh change.
2. The agent narrows each gap. One task is one function or one block. One task produces one test.
3. A worker agent writes the test. It gets the task, the source around the gap, and a checkout of the same commit. Then it writes a stateless SQL or shell test and runs it locally against the coverage binary of that commit.
4. The test must pass the guardrails. A manager agent reviews the test against these criteria and rejects tests that hard-code expected values or weaken the checks. The worker gets the review back and has a limited number of attempts:
   1. It is required to pass three runs in a row without a failure, to catch flakiness.
   2. It must not depend on the state left by other tests.
   3. It is required to execute the target lines, verified with the instrumented binary.
   4. It must check the results of the code it runs.
5. A deterministic script publishes the test. It is the only component with a GitHub token, and it opens a draft pull request from a bot account with the `ci-llvm-coverage` label. Its coverage run reports the newly covered lines, the proof that the test does what the task asked. The PR becomes ready for review only when CI is green, and reviewer comments go back to the worker as repair tasks.

Finally, a maintainer reviews and merges every test, like any other PR. One PR at a time, we increase our coverage and our confidence. But with every PR comes a price, and with over one million lines, those prices can stack up, so we have to identify when it is appropriate to run which portion of CI.

## Coverage per test: running only the tests that matter

The report of master says how much of the code the tests cover, but it does not say which test covers what. For that, we collect a second kind of data every night: for every functional test and every integration module, the exact lines it executed. The rows go into CIDB, our internal ClickHouse database for everything about CI, and they look like this:

| check\_start\_time | check\_name | test\_name | file | line\_start | line\_end |
| --- | --- | --- | --- | --- | --- |
| 2026-11-04 04:38:07 | Stateless tests (per\_test\_coverage, 2/8) | 00001\_select\_1.sql | src/Interpreters/executeQuery.cpp | 331 | 331 |
| 2026-11-04 04:38:07 | Stateless tests (per\_test\_coverage, 2/8) | 00001\_select\_1.sql | src/Interpreters/executeQuery.cpp | 333 | 333 |
| 2026-11-04 04:38:07 | Stateless tests (per\_test\_coverage, 2/8) | 00001\_select\_1.sql | src/Interpreters/executeQuery.cpp | 341 | 341 |
| 2026-11-04 04:38:07 | Stateless tests (per\_test\_coverage, 2/8) | 00001\_select\_1.sql | src/Interpreters/executeQuery.cpp | 359 | 359 |
| 2026-11-04 04:38:07 | Stateless tests (per\_test\_coverage, 2/8) | 00001\_select\_1.sql | src/Interpreters/executeQuery.cpp | 363 | 363 |
| 2026-11-04 04:38:07 | Stateless tests (per\_test\_coverage, 2/8) | 00001\_select\_1.sql | src/Interpreters/executeQuery.cpp | 440 | 447 |

`00001_select_1.sql` is the most complex (read: simple) test we have: it runs `SELECT 1`. Seems basic enough, right? On the night of November 4th, it still executed about 43,000 code regions in about 1,400 source files. One night of all tests gives about 300 million rows. CIDB’s coverage table holds roughly 36 billion. With this table we can produce some fun exercises of coverage. For example, we can produce a query that shows which tests exercise a function. Take [`StorageMergeTree::optimize`](https://github.com/ClickHouse/ClickHouse/blob/0d35156299d7ce2815322b55fe5193947e650bc4/src/Storages/StorageMergeTree.cpp#L3165-L3358), the implementation of `OPTIMIZE TABLE`. About 1,000 tests reach the function, and all of them reach its first lines.

Only three reach [the exception for OPTIMIZE DEDUPLICATE](https://github.com/ClickHouse/ClickHouse/blob/0d35156299d7ce2815322b55fe5193947e650bc4/src/Storages/StorageMergeTree.cpp#L3190) on a table with projections: [02968\_projection\_merge.sql](https://github.com/ClickHouse/ClickHouse/blob/0d35156299d7ce2815322b55fe5193947e650bc4/tests/queries/0_stateless/02968_projection_merge.sql), [03206\_projection\_merge\_special\_mergetree.sql](https://github.com/ClickHouse/ClickHouse/blob/0d35156299d7ce2815322b55fe5193947e650bc4/tests/queries/0_stateless/03206_projection_merge_special_mergetree.sql), and [03206\_projection\_merge\_special\_mergetree\_ignore.sql](https://github.com/ClickHouse/ClickHouse/blob/0d35156299d7ce2815322b55fe5193947e650bc4/tests/queries/0_stateless/03206_projection_merge_special_mergetree_ignore.sql).

Only three reach [the per-partition merge call of OPTIMIZE ... FINAL](https://github.com/ClickHouse/ClickHouse/blob/0d35156299d7ce2815322b55fe5193947e650bc4/src/Storages/StorageMergeTree.cpp#L3281-L3290): [00991\_system\_parts\_race\_condition\_long.sh](https://github.com/ClickHouse/ClickHouse/blob/0d35156299d7ce2815322b55fe5193947e650bc4/tests/queries/0_stateless/00991_system_parts_race_condition_long.sh), [03815\_debug\_assertion\_column\_sizes\_race.sh](https://github.com/ClickHouse/ClickHouse/blob/0d35156299d7ce2815322b55fe5193947e650bc4/tests/queries/0_stateless/03815_debug_assertion_column_sizes_race.sh), and [05259\_optimize\_final\_unmergeable\_partition.sql](https://github.com/ClickHouse/ClickHouse/blob/0d35156299d7ce2815322b55fe5193947e650bc4/tests/queries/0_stateless/05259_optimize_final_unmergeable_partition.sql).

A rare region names the tests that really exercise a piece of code. The entry of a popular function names almost everything. Test selection is built on that difference! The data tells CI which tests are worth running when a PR touches a piece of code. The dataset has over 17,000 functional tests and nearly 1,200 integration modules, and most of them never execute those lines.

Running all of them on a plain build is cheap enough that we do it every time, but running all of them under every sanitizer is not: a full suite under ThreadSanitizer or MemorySanitizer takes 3 to 10 times longer than on a plain build, and we run three sanitizers in several configurations each.

For a long time we did exactly that for every commit of every PR: the functional suites, in full, under every sanitizer until August; and the integration suites until the end of September. Most of that time went to tests, but unfortunately, tests that did not execute the changed code. Coverage per test lets us tell the difference, so now the sanitizer jobs run only the tests related to the change. The full suite does not go away, though. Every PR commit still runs it on the debug and plain builds, and master runs it under every sanitizer after every merge. The selection only decides where the expensive instrumentation is spent.

But how do pull requests utilize this table? Each targeted job builds its list of tests from three sources:

1. Every test whose file the PR touches runs.
2. Every test that failed in this PR during the last 30 days runs, except failures in runs where everything failed at once.
3. Coverage selects the rest.

The changed lines of the PR are looked up in the table, in the three newest nightly exports. Every test that owns a matching region is a candidate. A region wider than 40 lines, or owned by more than 150 tests like the entry of `optimize`, is too generic and is ignored. Each candidate gets a score: a rare and narrow region counts more than a popular and wide one. The best 250 functional tests or 100 integration modules run. The first two sources always run.

That strategy materializes to having the median PR gets about 80 tests from the coverage source. A targeted functional job under a sanitizer takes about 25 minutes, a targeted integration job about double that time. A full set of sanitizer integration suites costs about 2,100 machine-minutes per commit, and the targeted jobs cost less than ten times that. With the functional suites included, a PR commit needs about 40 machine-hours less than before, close to 100,000 machine-hours per week at about 350 PR commits per day, thanks to all of our wonderful and eager contributors.

Two more jobs build on the same selection. The flaky checks run the changed tests many times under every sanitizer; in the last 30 days they failed in about 5% of PR commits, and each failure caught an unstable test before the merge. The targeted AST fuzzer fuzzes the queries of the selected tests instead of random ones, so its time budget is spent near the changed code.

To keep this table current, the table is updated via a nightly build with `-DWITH_COVERAGE_DEPTH=ON`, on which the server can read its own LLVM counters. Before every test the runner executes `SYSTEM SET COVERAGE TEST '<test name>'`. The server flushes the counters of the previous test, resolves them to file and line ranges with the coverage mapping of its own binary, writes the rows into `system.coverage_log`, and resets the counters. Functional tests run one at a time, so the counters belong to one test. Integration tests are recorded per module, through files that every server, Keeper and bridge process writes next to its log, because a module may kill its servers at any moment. At the end of each shard the rows are exported into CIDB.

## Coverage per pull request: increasing only the confidence that matters

While our numbers from master answer "how much" and our numbers from the per-test data answer "which test". The third question is the one a reviewer asks: is the code of this PR tested? The `LLVM Coverage` job of a pull request answers it in the CI comment. A pull request runs that job on request, with the `ci-coverage` or `ci-llvm-coverage` label. This is the comment on [#127836](https://github.com/ClickHouse/ClickHouse/pull/127836#issuecomment-6416656492), a change in `MergeTree` reading:

> LLVM Coverage Report
>
> Measured on commit 2bce354c.
>
> | Metric | Baseline | Current | Δ |
> | --- | --- | --- | --- |
> | Lines | 88.70% | 88.60% | -0.10% |
> | Functions | 91.50% | 91.50% | +0.00% |
> | Branches | 80.40% | 80.40% | +0.00% |
>
> **Changed lines:** Changed C/C++ lines covered: 181/192 (94.27%) · [Uncovered code](https://s3.amazonaws.com/clickhouse-test-reports/PRs/127836/2bce354c8fd7aa68323e503c5ea5524dcd0722c2/pr/llvm_coverage/print_uncovered_code/print_uncovered_code.log)
>
> [Full report](https://s3.amazonaws.com/clickhouse-test-reports/PRs/127836/2bce354c8fd7aa68323e503c5ea5524dcd0722c2/pr/llvm_coverage/generate_llvm_coverage_report/index.html) · [Diff report](https://s3.amazonaws.com/clickhouse-test-reports/PRs/127836/2bce354c8fd7aa68323e503c5ea5524dcd0722c2/pr/llvm_coverage/generate_llvm_coverage_diff_report/index_diff.html)

### Differential code coverage

The [diff report](https://s3.amazonaws.com/clickhouse-test-reports/PRs/127836/2bce354c8fd7aa68323e503c5ea5524dcd0722c2/pr/llvm_coverage/generate_llvm_coverage_diff_report/index_diff.html) is a coverage report for the changed files only, next to the master baseline. Inserted lines that the tests executed are green, inserted lines that nothing executed are red, and unchanged lines keep their baseline color. It is made with `lcov` and `genhtml` from two tracefiles cut down to the changed files, the PR run and the nearest master ancestor, with the PR diff as the mapping between the two line numberings.

![Differential coverage report showing covered and uncovered changed lines](https://clickhouse.com/uploads/differential_coverage_report_4737a95904.png)

The job also writes the [uncovered code](https://s3.amazonaws.com/clickhouse-test-reports/PRs/127836/2bce354c8fd7aa68323e503c5ea5524dcd0722c2/pr/llvm_coverage/print_uncovered_code/print_uncovered_code.log) as plain text with the surrounding lines, so a reviewer can read the 11 untested lines of this PR without opening the HTML. And it has a gate: a PR whose total line coverage drops more than 0.3 percentage points below master fails the check.

### Newly covered code

A PR that only adds tests doesn't change any C++ lines, so the differential report has nothing to show. For such PRs, the job answers the opposite question: which lines does master not cover that this PR covers now? The comment of the agent PR [#127806](https://github.com/ClickHouse/ClickHouse/pull/127806#issuecomment-6494581419) reads:

> **Changed lines:** Uncovered code analysis did not run: No coverable C/C++ source files changed (contrib/ is excluded from coverage).
>
> **Newly covered:** +535 lines in 46 files (-99 lines lost coverage) · [Details](https://s3.amazonaws.com/clickhouse-test-reports/PRs/127806/13b9c091f290ee311cadfab2c87cc87d615374ea/pr/llvm_coverage/newly_covered_lines/newly_covered_lines.log)

The [details](https://s3.amazonaws.com/clickhouse-test-reports/PRs/127806/13b9c091f290ee311cadfab2c87cc87d615374ea/pr/llvm_coverage/newly_covered_lines/newly_covered_lines.log) list the lines per file. The PR tracefile is compared with the master baseline and up to six older master tracefiles: a line is newly covered only if it has zero hits in every baseline and hits in the PR run, and lost only if it has hits in every baseline and none in the PR run. The older baselines are what makes the number usable. With one baseline, background threads and parallel execution produce about 1,300 false "newly covered" lines per run; with seven, about 150.

### Lost baseline coverage

A PR may change existing logic so that a code path is no longer executed by any test. We counted such lines in the changed files, called the metric lost baseline coverage, and gave it a gate. In practice, the count was almost always empty, and when it was not, the cause was a test that behaved differently in that run, not the change. We removed it after three months. The total coverage gate does the same job with less noise, and the "lost coverage" count survives in the newly covered report above.

## What should this look like in the future?

The harness already pays for itself! We know how much of ClickHouse the tests execute, down to the line. Every PR gets a verdict on its own code, the sanitizer runs cost a fraction of what they did a year ago, and an agent turns red lines into tests every day. Still, we are not done. We want the numbers to be more precise, and we want them to tell us more about our code than they do today. While we have many ideas, a few on the top of our minds are:

- A covered line is not a tested line. The test should not only execute the code but also verify what it did; a small change in the source should make some tests fail. Coverage cannot see that. Mutation testing can, and it is the next thing we want to try.
- Two runs of the same suite on the same binary still do not give identical coverage. Background threads and parallel execution leave a noise floor of a few hundred lines per run, so every comparison needs several baselines. We would like one run to be enough.
- The per-test data has blind spots. A new source file has no rows until the night after its merge, so the targeted jobs cannot select tests for it. And a test gets credit only for what it executed itself; work done by background threads lands on whichever test was running at that moment.
- The report counts lines, functions, and branches. It does not yet answer the question we started with: which features and settings are covered? The per-test table has the data for it. A setting or a feature is a set of code regions, and we know which tests reach each of them. Turning that into a report is work we have not done yet.

In a rapidly growing industry where robots are increasingly responsible for development, we are making our greatest effort to date to increase our confidence in their outcomes. That effort comes in many shapes and sizes, and increasing our test coverage along with our test scrutiny is probably our largest! If you are interested in working alongside teammates who deeply care about increasing the quality of databases we operate, take a look at our [Careers page](https://clickhouse.com/company/careers). ClickHouse is always looking for contributors to leverage the power of CI to prevent problems before they ever find their way to users.

