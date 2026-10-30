---
title: "Meet GroeneAI: our autonomous contributor to ClickHouse"
date: "2026-10-29T12:53:19.737Z"
author: "James Cunningham, Artem Brustovetskii and Alex Soffronow Pagonidis"
category: "Engineering"
excerpt: "Meet GroeneAI, ClickHouse’s autonomous engineering agent that contributed more than 3,000 merged pull requests in under seven months."
---

# Meet GroeneAI: our autonomous contributor to ClickHouse

## Finding CI Failures in the Wild

While writing software can sometimes be difficult, you never perceived it as the bottleneck of your day. After you’ve ran your own tests, confirmed the functionality, submitted your change, waited patiently to see what your coworkers thought of your code, aaaaaaaaand it failed CI.

But, come to find out it was never your own bug, it was the failure that had nothing to do with your change. You had to leave your patch, search earlier CI runs, reproduce the failure, and decide whether the problem lived in the database, in the test, or in its environment. Rerunning the job often produced a passing result. The underlying problem stayed where it was, and the next contributor met it again.

Somebody has to do that work, and since March 2026 in the ClickHouse codebase, that somebody is frequently not a person.

We built [GroeneAI](https://github.com/groeneai) to take on those investigations. It is a fully autonomous AI engineering agent that works 24 hours a day, seven days a week. It reproduces failures, writes and tests fixes, and follows its pull requests through CI and review. Groene means "green" in Dutch, which records the original goal: keep CI green.

It opened its first [ClickHouse issue](https://github.com/ClickHouse/ClickHouse/issues/100708) on the 25th of March, followed by its first [pull request](https://github.com/ClickHouse/ClickHouse/pull/100715) 72 minutes later, and hasn’t stopped since. The agent carries out the whole development process without a human in the loop. It selects the work, investigates the cause, designs and implements a fix, builds ClickHouse, runs the tests, and opens the pull request. No person performs these steps, and most of the time no person chooses them either. GroeneAI finds the bulk of its own work in CI results, fuzzer findings, and user reports. A maintainer can also hand it a bug with a single comment. Human involvement otherwise starts at review, where a maintainer decides whether to accept the change or redirect GroeneAI to their liking.

The follow-up work is autonomous too. GroeneAI monitors CI, answers review comments, revises implementations, and rebases changes as the repository moves. A task can stay active across many sessions, with the investigation and its next steps preserved throughout.

As GroeneAI investigated failures, it learned how the codebase fits together. It saves root causes, failed approaches, and reviewer feedback in persistent memory, then uses those lessons in later tasks. That loop carried it into correctness and performance problems across the SQL engine, storage, query planning, and the test infrastructure around them. The scope did not stay on CI for long.

By October 2026, GroeneAI had contributed more than 3,000 merged pull requests to ClickHouse. Over the three months to October 19th, it ranked second among ClickHouse contributors by authored non-merge commits, behind ClickHouse co-founder and CTO [Alexey Milovidov](https://clickhouse.com/company/our-story).

![Monthly activity in ClickHouse/ClickHouse. Openings, merges, and closures are counted in the month each event occurred. October includes October 1st to 25th only.](https://clickhouse.com/uploads/groeneai_monthly_activity_019fdadb4a.png)

Monthly activity in ClickHouse/ClickHouse. Openings, merges, and closures are counted in the month each event occurred. October includes October 1st to 25th only.

The agent runs on [Nerve](https://github.com/ClickHouse/nerve), our open-source agent runtime. Nerve provides persistent sessions, memory, tools, and scheduled execution. GroeneAI adds a development workflow built for ClickHouse. How that workflow reached its current shape is best told through one bug.

While we are proud of every change our little robot has produced, we’d like to highlight some specific months where it really shined:

## June: a cache that remembered the wrong thing

On June 3rd, GroeneAI was [watching CI for its own DDL change](https://github.com/ClickHouse/ClickHouse/pull/106192#issuecomment-4612881667) when an unrelated test, `03047_on_fly_update_delete`, failed under distributed query plans on S3 storage. The failure looked flaky. A rerun would have passed. GroeneAI reproduced it instead, and the reproduction is where the bug became visible.

The [query condition cache](https://clickhouse.com/docs/concepts/features/performance/caches/query-condition-cache) remembers which ranges of a data part contain no rows matching a filter, so a later query with the same condition can skip them. The entry is only trustworthy if the filter saw the real data. If another operation removed or changed rows first, an empty result says more about that operation than about what is stored.

The [investigation](https://github.com/ClickHouse/ClickHouse/pull/107145#issuecomment-4677062740) traced the apparent flakiness to randomized index granularity. With larger granules, one surviving matching row kept a range eligible for reading and hid the bug. With one row per granule, the incorrect skipping decision reproduced every time. The missing guard was old. It dated back to the [original query condition cache implementation](https://github.com/ClickHouse/ClickHouse/pull/69236), merged in March of the previous year, which applied mutations before `PREWHERE` but recorded the resulting empty ranges without checking whether those mutations had changed the rows.

The [regression test](https://github.com/ClickHouse/ClickHouse/blob/b7182f6c45469181b66158e293e1d5c4f6100755/tests/queries/0_stateless/03229_query_condition_cache_on_fly_mutations.sql) makes that concrete. It creates 100 rows where `id` and `v` both run from 0 to 99. It stops background merges and submits an asynchronous update that sets `v` to zero for rows with `id >= 50`. The original part stays available, so a query can choose whether to apply the pending mutation as it reads. After enabling and clearing the cache, the test performs two reads:

```sql
SELECT count() FROM t_qcc_on_fly_update
PREWHERE v >= 50 SETTINGS apply_mutations_on_fly=1;

SELECT count() FROM t_qcc_on_fly_update
PREWHERE v >= 50 SETTINGS apply_mutations_on_fly=0;
```

The first query should return zero, because the update changes every matching value. The second should return 50, because it reads the original values. Before the fix, the first query wrote a cache entry that made the second skip the matching rows.

| Read | Before the fix | Expected and after the fix |
| --- | --- | --- |
| Apply the pending update | 0 | 0 |
| Read the original values | 0 | 50 |

Recorded results for the UPDATE case in the PR's single-replica regression fixture, with `index_granularity = 1` and `mutations_sync = 0`.

The reader side was already careful: it avoided cached results when mutations were active. The missing protection was on the writing side. [PR #107145](https://github.com/ClickHouse/ClickHouse/pull/107145) guards both cache-writing paths with a [check for mutation steps or patch parts](https://github.com/ClickHouse/ClickHouse/blob/b7182f6c45469181b66158e293e1d5c4f6100755/src/Storages/MergeTree/MergeTreeReadTask.cpp#L464-L476) before `PREWHERE`. When those transformations are active, the [read processor](https://github.com/ClickHouse/ClickHouse/blob/b7182f6c45469181b66158e293e1d5c4f6100755/src/Storages/MergeTree/MergeTreeSelectProcessor.cpp#L272-L325) suppresses cache updates from `PREWHERE` and withholds the metadata that would let a downstream `WHERE` filter write an entry. Row-level security gets the same guard, with a [two-user regression test](https://github.com/ClickHouse/ClickHouse/blob/b7182f6c45469181b66158e293e1d5c4f6100755/tests/queries/0_stateless/03229_query_condition_cache_row_policy.sh) that gives one user access to `v < 50` and the other an always-true policy. Queries without these transformations keep the optimization.

The pull request thread shows how GroeneAI worked in June, before the pipeline in the next section existed. It opened [PR #107145](https://github.com/ClickHouse/ClickHouse/pull/107145) on June 11th with a table of what it had verified. Four review findings arrived the same day: the `WHERE` path was still unguarded, row policies needed the same guard, the patch-part case had no test, and that test was non-deterministic. GroeneAI fixed each one and re-posted the table after every fixup, five times in twelve hours. Eight days later, [alesapin asked](https://github.com/ClickHouse/ClickHouse/pull/107145#issuecomment-4752368866) whether the change disabled `PREWHERE` under lightweight mutations. GroeneAI [answered in 31 minutes](https://github.com/ClickHouse/ClickHouse/pull/107145#issuecomment-4752601585): only the cache write was suppressed, and keying the cache on mutation state was the alternative if he preferred it. He approved 33 minutes after that.

The change merged on June 19th. Its tests cover updates, deletes, patch parts, row policies, and predicates kept explicitly in `WHERE`. One rule holds in every case: a filter can record that a range contains no matching rows only when it evaluated the data that the cache entry represents.

Good job, robot.

## July: one investigation becomes a process

The cache fix took sixteen days from the failed test to the merge. A build, an overnight CI run, and a reviewer returning days later all sit inside that span. An agent that forgets between sessions cannot do this work at all, and an agent that remembers the wrong thing does it badly. In July, after the June fix, we introduced the pipeline that the current workflow still uses, and we have kept changing its checks as new failures exposed missing cases.

The intake starts with events, storing GitHub notifications and tracking each consumer's position in the inbox. GroeneAI's inbox processor then associates actionable messages with tasks. A separate scheduled scan examines CI failures, including those that never appeared in the account's participating notifications.

The resulting task is durable, as Nerve stores its Markdown content and indexes it in SQLite. GroeneAI adds a checkpoint that records the phase, branch, commit, build identity, completed tests, evidence locations, and next action. A later session recovers that state without needing the previous conversation to stay alive.

![Nerve retains the task and schedules execution. GroeneAI's workflow controls phase handoffs. Corrections return to implementation, while CI and maintainer feedback can resume work after publication.](https://clickhouse.com/uploads/groeneai_nerve_lifecycle_a688ba89ee.png)

Nerve retains the task and schedules execution. GroeneAI's workflow controls phase handoffs. Corrections return to implementation, while CI and maintainer feedback can resume work after publication.

The cache fix shows why that state matters: A resumed worker needs to know which read path was already guarded, which test exercises `WHERE`, and whether the patch-part test waits for its update. A checkpoint points to the relevant artifacts, which preserves the difference between a completed change and an unresolved test condition.

Memory carries information across different tasks. Short operating rules enter the session context. Longer investigations live in files that load when relevant, while semantic recall retrieves previous findings and procedures. Skills provide reusable instructions for work such as building ClickHouse or investigating a CI failure.

Stored information can also go stale, and the workflow treats it that way. GroeneAI's build instructions require a check of the current CI compiler configuration and CMake cache, even when memory already holds a compiler version. The remembered lesson points the worker at evidence it must verify in the current checkout. The [Nerve task documentation](https://github.com/ClickHouse/nerve/blob/main/docs/tasks.md), [source-ingestion documentation](https://github.com/ClickHouse/nerve/blob/main/docs/sources.md), and [memory documentation](https://github.com/ClickHouse/nerve/blob/main/docs/memory.md) describe these runtime primitives.

On top of that runtime, the workflow splits a new contribution into three phases with different jobs.

A planning worker investigates the report, checks the source and existing fixes, and writes an approach with a reproduction procedure. A separate model reviews the plan. Work can stop here if the report is a duplicate, cannot be reproduced, or needs a maintainer's decision.

An implementation worker then makes the change in the task's checkout. Its instructions require evidence that the regression test fails without the patch and passes with it. If the plan's assumptions do not hold, the worker records what it ran and returns the task to planning.

A fresh review session examines the code before it reads the implementer's validation narrative. It must inspect the changed functions, their callers, and related implementations, then compare the tests with the proposed pull request description. GroeneAI uses Claude for its main worker sessions and Codex for separate reviews of the approach and the resulting change. The reviewer builds its own explanation of the patch and compares it with the implementation evidence. An accepted substantive finding becomes a correction for implementation. A disputed finding needs code or test evidence that explains the disagreement.

The workflow also checks which revision was reviewed. The ordinary pre-push path requires a completed second-model review recorded against the proposed commit, tree, or complete patch identity. Findings still require adjudication, and a review of an earlier version must not silently authorize a later code change.

## August: the process at work

Two changes from August show that process at work, beginning to truly shine autonomously. The first is a planner optimization that GroeneAI had to prove safe before a maintainer would merge it, and the second repairs a CI report that engineers read when they judge somebody else's change.

Let’s see how the robot did:

### The first, making UNION DISTINCT use parallel work

In [PR #115173](https://github.com/ClickHouse/ClickHouse/pull/115173), GroeneAI noticed that two equivalent query forms produced different pipelines, and that the slower one was the form people write. Its change is small. What the pull request records is how GroeneAI argued for it. Before the merge it [measured the opposite case](https://github.com/ClickHouse/ClickHouse/pull/115173#issuecomment-5399220630), a sweep over duplicate density and thread count, found a 16-thread input that became 22% slower and the largest penalty at `max_threads = 1`, and added the guard that keeps the old plan on one thread. Its own [second-model review](https://github.com/ClickHouse/ClickHouse/pull/115173#issuecomment-5318654935) then rejected the first regression test, because disabling the preliminary step while keeping its plan label would still have passed an assertion that only checked for presence. The test now asserts exactly two preliminary plan steps and three `DistinctTransform`s, and a targeted flip of the flag in either planner makes it fail.

The two forms were `UNION DISTINCT`, which sent all rows through one final deduplication step, and an outer `SELECT DISTINCT` around `UNION ALL`, which first removed duplicates within each branch in parallel. The patch adds a [preliminary distinct step](https://github.com/ClickHouse/ClickHouse/blob/2848e3ee55e51800a4bf0b7a609de7f26c6e2d93/src/Planner/Planner.cpp#L2105-L2131) for `UNION DISTINCT` when the effective thread count exceeds one, pushes it into the branches, and keeps the final step, because different branches can hold the same values. Both planner implementations were updated. `INTERSECT` and `EXCEPT` keep their existing plans.

![Branch-local deduplication reduces the rows entering the final distinct stage. The final stage still removes duplicates shared by different branches.](https://clickhouse.com/uploads/groeneai_union_distinct_82a6c5bf02.png)

Branch-local deduplication reduces the rows entering the final distinct stage. The final stage still removes duplicates shared by different branches.

The pull request reports this experiment on a release build, with two branches of eight million rows each, 2,000 distinct values, and the fastest of seven runs:

| `max_threads` | Before | After |
| --- | --- | --- |
| 1 | 60 ms | 61 ms |
| 8 | 44 ms | 13 ms |
| 16 | 59 ms | 9 ms |

That table is the duplicate-heavy case the change was built for. The sweep is why the guard at `max_threads = 1` exists, and why the table does not claim a speedup for every input. The change merged on August 27th with a [regression test](https://github.com/ClickHouse/ClickHouse/blob/2848e3ee55e51800a4bf0b7a609de7f26c6e2d93/tests/queries/0_stateless/04951_union_distinct_preliminary_distinct.sql) that covers query results and execution-plan structure.

### The second, making CI failures easier to interpret

The second change is to a tool GroeneAI depends on. [PR #114451](https://github.com/ClickHouse/ClickHouse/pull/114451) addressed a performance-comparison report whose summary passed while its details showed 22 red rows. GroeneAI did not touch the verdict. It built the regression tests from two real report artifacts, a passing shard with 11 unstable queries and a failing shard that had to stay red, and asserted that its fix changed only the display.

The report had assigned a hardcoded failure status to every detail row and displayed both the baseline and the candidate side of each comparison. The [result-builder change](https://github.com/ClickHouse/ClickHouse/blob/883eb8e9f09c273eb6cfca435d388882064db0f0/ci/jobs/performance_tests.py#L649-L684) carries the actual query verdict into the report and displays each comparison once, preferring the candidate side, while preserving the rows stored in the CI database and their history links. The [regression tests](https://github.com/ClickHouse/ClickHouse/blob/883eb8e9f09c273eb6cfca435d388882064db0f0/ci/tests/test_perf_check_results_children.py) assert that the passing shard produces 11 unstable rows and that the failing shard keeps its failure status. The change merged on August 17th.

## September: one injection evolves into a chain of improvements

In September the focus moved into security. Five of the pull requests merged that month closed a SQL injection, and each one led to the next. The first, [PR #108469](https://github.com/ClickHouse/ClickHouse/pull/108469), had been open since June 25th. GroeneAI had found that the PostgreSQL wire protocol spliced prepared-statement parameters into the SQL text as raw strings, so a value such as `x' UNION ALL SELECT ... --` escaped its literal. On September 2nd, one of our maintainers pushed two commits of his own to GroeneAI's branch: quoting for COPY identifiers and a CancelRequest fix. The next morning he asked GroeneAI to review them:

![PR #108469: the maintainer's request on September 3rd, 2026, and the opening of GroeneAI's review of his commits.](https://clickhouse.com/uploads/groeneai_pr_108469_handover_a91fc4ec87.png)

PR #108469: the maintainer's request on September 3rd, 2026, and the opening of GroeneAI's review of his commits.

GroeneAI [answered in an hour](https://github.com/ClickHouse/ClickHouse/pull/108469#issuecomment-5523227317). It confirmed both fixes against a debug build, then listed three gaps and called none of them a blocker: the new cancel key came from a non-cryptographic generator, no test pinned the key as a credential, and the COPY FROM table name was the one injection arm without a probe. Antonio answered the first gap himself with four more commits, including a cancellation key drawn from `RAND_bytes`, and handed the pull request back. Within a few hours, GroeneAI had [closed the other two gaps](https://github.com/ClickHouse/ClickHouse/pull/108469#issuecomment-5526760414) and found two more defects on its own: the cancel secret appeared in the query id, and two listeners could hand out the same connection id. The change merged the next morning, 71 days after it opened. When a second ClickHouse agent, ClickGap, found a regression in the merged code the following day, GroeneAI had [the fix](https://github.com/ClickHouse/ClickHouse/pull/118210) open within two hours.

The merge did not end the class. Four days later [PR #111516](https://github.com/ClickHouse/ClickHouse/pull/111516) closed the string-literal sinks in the PostgreSQL metadata queries. The day after that, ClickGap [reported](https://github.com/ClickHouse/ClickHouse/issues/118954) that the identifier sinks were still open: a remote table name of `a"; CREATE TABLE t(x int); --` ran on the PostgreSQL server, because the code escaped a double quote with a backslash and PostgreSQL honors only `""`. GroeneAI opened [PR #119103](https://github.com/ClickHouse/ClickHouse/pull/119103) the same evening, recorded a read-path residual in its last paragraph, and opened [PR #119216](https://github.com/ClickHouse/ClickHouse/pull/119216) for that residual the next day. [PR #117421](https://github.com/ClickHouse/ClickHouse/pull/117421) applied the same analysis to the SQLite engine, where review found a data race in the vendored library and the fix needed a [one-line change](https://github.com/ClickHouse/sqlite-amalgamation/pull/3) in a second repository first. Each pull request names the one before it, and each description states what it leaves open.

The oldest item on the list was not an injection. In March 2022, Alexey Milovidov had filed [issue #35504](https://github.com/ClickHouse/ClickHouse/issues/35504): `clickhouse-client` did not check the domain name on the server certificate. [PR #116724](https://github.com/ClickHouse/ClickHouse/pull/116724) traced it to one literal, a default of `false` in `SSLManager.cpp` that made every outbound TLS connection accept any CA-signed certificate for any host. The fix turns the check on for clients, keeps the server default, exempts loopback addresses, and documents the two settings that restore the old behaviour. Alexey approved it on September 20th, four and a half years after he filed it, and it was backported to four release branches.

## October: one sentence from a maintainer

Most of GroeneAI's work starts with a signal nobody typed: a failed test, a fuzzer finding, a report in the issue tracker. Sometimes it starts with a person. On September 28th, an external user reported that a dictionary with a local ClickHouse source kept the roles its user held at load time. A role granted later never took effect, every update failed with `ACCESS_DENIED`, and the dictionary served stale data until somebody reloaded it. A week later a maintainer read the report and handed it over:

![Issue #122663: the maintainer's request and GroeneAI's two replies, all on October 5th, 2026.](https://clickhouse.com/uploads/groeneai_issue_122663_9780945053.png)

Issue #122663: the maintainer's request and GroeneAI's two replies, all on October 5th, 2026.

The mention arrived in the inbox like any other notification and became a task. GroeneAI reproduced the bug against the released 26.8.10.6 binary, traced it to a context that has stored the user's default roles as a fixed list since a 2023 change, and had [PR #124051](https://github.com/ClickHouse/ClickHouse/pull/124051) open within seven hours. The fix is 17 lines in two source files. The test is 108 lines and fails on master every run.

The thread shows the lessons from the sections above in force. GroeneAI left two comments on the pull request, both collapsed by default: the second-model review with zero blocking findings, and the validation gate. There is no re-posted table, because the pipeline ran those checks before publication. When [the maintainer asked](https://github.com/ClickHouse/ClickHouse/pull/124051#discussion_r4218996610) it to "just check if this is needed elsewhere", GroeneAI measured every other place that runs queries as a ClickHouse user, from remote dictionary sources to definer views and HTTP sessions, and [answered with a table](https://github.com/ClickHouse/ClickHouse/pull/124051#discussion_r4220613248) in under three hours. He approved 21 minutes later and merged the same afternoon, three days after his first sentence.

## Six months in numbers

By October 25th, 2026, GroeneAI had opened over 4,400 pull requests in `ClickHouse/ClickHouse`. Of those, over 3,100 had merged, roughly 750 remained open, and nearly 500 closed without merging. Among pull requests with a completed decision, 86.5% were merged.

Monthly merges grew from almost 100 in April to almost 700 in September, and the first 25 days of October added over 800. The work includes over 1,300 merged pull requests labeled as bug fixes, almost tied with CI and tests, and roughly 150 for performance improvements. Twenty-three carry the critical-bug-fix label.

![Selected changelog labels on merged pull requests as of October 25th. Labels can overlap, so these counts should not be added together.](https://clickhouse.com/uploads/groeneai_changelog_labels_7104d3b720.png)

Selected changelog labels on merged pull requests as of October 25th. Labels can overlap, so these counts should not be added together.

The merged pull requests reference over 1,000 distinct issues through GitHub's closing-issue links. They also include work that never began with an issue: new regression coverage, clearer CI reports, and improvements found while investigating another failure.

The median merged patch changes 67 lines across three files. The examples above fit that pattern. Correct a read-path assumption, add a missing planner step, repair a misleading CI result, or bind a parameter as data. A small patch can protect a widely used operation, especially when it arrives with a test that makes the original failure reproducible.

## Most importantly, learning from the reviewers

Opening a pull request leaves work outstanding. A check can fail, a base branch can move, or a maintainer can ask for a different approach. GroeneAI retains the task and routes those events to maintenance or human-response workers.

That feedback also changes how it approaches the next problem. During an investigation, it saves root causes, reproduction steps, failed approaches, and reviewer directives in persistent memory. A new task opens with a recall of relevant history, which gives it findings that are no longer in the current conversation.

Each week, GroeneAI examines human feedback on requested changes, rejected pull requests, and selected merged contributions. It distills those outcomes into `REVIEW-LESSONS.md`, recording the originating pull request, the reviewer's decision, and the lesson to apply. The instructions for implementation, for review, and for substantive replies all require reading that document before working.

One saved lesson has a visible origin. In [PR #109738](https://github.com/ClickHouse/ClickHouse/pull/109738), the fix expanded during review to cover additional cases, while the description still named only the original bug. The reviewer's note is the shortest possible statement of the problem:

![Avogar's review on PR #109738, July 23rd, 2026.](https://clickhouse.com/uploads/groeneai_pr_109738_review_18d53880f7.png)

Avogar's review on PR #109738, July 23rd, 2026.

Both notes became lessons. The first is now the instruction that a description must reflect the complete final change, so that later reviews compare the code and tests with an accurate statement of what the patch promises. The second took longer to learn. In June, GroeneAI had re-posted its validation table five times on one pull request. In September, a maintainer on [PR #117727](https://github.com/ClickHouse/ClickHouse/pull/117727) opened his comment with "if you read this between the many agentic comments". GroeneAI's reply conceded the point:

![GroeneAI's reply on PR #117727, September 2nd, 2026.](https://clickhouse.com/uploads/groeneai_pr_117727_reply_ba2470a9c4.png)

GroeneAI's reply on PR #117727, September 2nd, 2026.

That reply became a standing directive. From then on, GroeneAI's pull request comments carry a note that no reader sees unless they open the raw Markdown:

> REVIEW-LESSONS standing directive: two maintainers have named this fleet's comment volume as the reviewer load (@rschu1ze #117727, @Algunenano #117619). This ONE collapsed comment is all that is posted; the a-i validation table is deliberately NOT posted.
Source: [PR #120259](https://github.com/ClickHouse/ClickHouse/pull/120259#issuecomment-5686386824), hidden HTML comment in the raw Markdown.
> 

GroeneAI also compares automated findings it dismissed with the human review that followed. When a maintainer raises an issue the agent had waved off, it records both the earlier decision and the later correction. The memory keeps why the previous judgment failed, which makes the correction available beyond the single pull request where it happened.

For CI fixes, the merge is not the end. GroeneAI keeps a `verifying` task state after merge, and a scheduled worker queries subsequent failures on `master`. Its instructions require at least two days of master runs without the reported failure before the task closes, and continuing failures go back to investigation. The merge decision and the later check against the original failure signal stay separate steps.

## What this makes possible?

GroeneAI's contributions reach several parts of database engineering. Correctness fixes protect query results. Execution improvements make better use of parallelism. CI changes help contributors interpret failures, and regression tests preserve the conditions that exposed a bug in the first place.

Continuous operation is what makes this possible across long builds, delayed CI results, and review conversations that span days. Nerve retains the investigation, and GroeneAI returns to it when new evidence arrives. Persistent memory lets the next task start with the lessons of the work that came before it.

The result is visible in ClickHouse's code and tests: more than 3,000 merged contributions from an autonomous agent in under seven months. An intermittent failure can become a deterministic regression test. A missing planner step can become a faster query. A review correction can become a reusable engineering lesson. The public [issues and pull requests](https://github.com/ClickHouse/ClickHouse/pulls?q=is%3Apr+author%3AgroeneAI) show that process continuing every day.

If you would like to build an autonomous coworker from the pieces we have created, our self-hosted runtime named [Nerve](https://github.com/ClickHouse/nerve) is open-source. We would love to hear about new ways to leverage it!

If instead, GroeneAI is a robot you would like to work alongside, take a look at our [Careers page](https://clickhouse.com/company/careers). ClickHouse is always looking for talent that can leverage the power of AI and autonomy to easily reach corners of the house that were previously difficult to clean.
