---
title: "ClickGap: Autonomous QA for ClickHouse"
date: "2026-08-25T12:19:59.369Z"
author: "Lareb Zafar"
category: "Engineering"
excerpt: "ClickGap reviews merged ClickHouse changes, executes reproducers, rejects false positives, and attributes regressions to specific commits."
---

# ClickGap: Autonomous QA for ClickHouse

ClickHouse merges between 50 and 100 pull requests on a typical working day. Each one lands in a performance-critical C++ database running in production. Any merge can introduce a wrong result, trigger a crash in an untested feature combination, or make a query quietly run 30 percent slower.

Pointing an AI agent at the problem seems obvious, but it is also a fast route to becoming a cautionary tale. 

curl recently ended the bug bounty it had operated since 2019 after a flood of AI-generated reports, which its maintainer described as "slop". Producing a plausible bug report is nearly free; triaging one costs an engineer. Our maintainers did not sign up to babysit a chatbot.

We built one anyway. It received a one-line cameo in [Agentic coding at ClickHouse](https://clickhouse.com/blog/agentic-coding); this post is the long version. 

[ClickGap](https://github.com/clickgapai) is an autonomous QA agent that reviews every pull request merged into ClickHouse. It designs and executes tests against real builds, bisects regressions to the commit that introduced them, and files issues and pull requests in the public tracker without a human approving the send button.

Five months after launch, [ClickGap’s GitHub account](https://github.com/ClickHouse/ClickHouse/issues?q=is%3Aissue+author%3Aclickgapai) has filed roughly 500 issues and opened around 200 pull requests, adding coverage for code paths that had merged without it. More than half of the issues are already closed, overwhelmingly as completed rather than dismissed, and over 200 were closed with a linked fix PR. ClickGap reviews each pull request after it merges because merged code is what ships. Findings arrive within hours, well before a release could carry the defect to users.

In this blog post, we're going to go through some of the challenges of building ClickGap, and how we got to the point that when that bot says, “This is broken,” the maintainer believes it.

## A database that is already tested to death {#a_database_that_is_already_tested_to_death}

ClickHouse CI executes tests tens of millions of times each day: stateless SQL suites, integration clusters, sanitizer builds, stress tests, fuzzers, and statistical performance comparisons. Nothing merges without a human maintainer’s approval, and every pull request is also inspected by an in-house reviewer, [clickhouse-gh\[bot\]](https://github.com/apps/clickhouse-gh), which reads the diff and requests changes with file-and-line findings. It catches a meaningful share of defects before merge. 

Yet some defects still survive the human reviewer, the machine reviewer, and the test wall. CI proves only that written tests continue to pass; it says nothing about behavior, no test exercises. Newly merged code is especially exposed because pull requests routinely introduce changed lines the test suite never reaches. Those gaps account for ClickGap’s roughly 200 coverage PRs.

Other defects are invisible to result assertions because correctness remains unchanged while execution cost rises. A skip index can be built, consume disk, and never skip a single row. Every query still returns the right result while wasting the resources the index was supposed to save.

## What it found in ClickHouse {#what_it_found_in_clickhouse}

The public tracker spans roughly 35 component labels, from the query analyzer and MergeTree to replication. Its findings cluster into four recurring categories.

**The smuggled semantics change** ([#113763](https://github.com/ClickHouse/ClickHouse/issues/113763)). A pull request adding the `gini` aggregate function also changed the result types and values of a broad family of existing `<agg>If<Combinator>(x, NULL)` expressions. Nothing in the title, description, or changelog disclosed that impact. This class of defect is easy to miss when review remains bound by the pull request’s stated purpose: the change may correctly implement what it announces while silently breaking things it does not mention.

**The resource-safety hole** ([#114987](https://github.com/ClickHouse/ClickHouse/issues/114987)). The learning phase of a new adaptive aggregator returned before reaching the external-spill branch. Under the affected configuration, a query that previously spilled to disk could instead hit its memory limit. The report did not merely speculate about an OOM. It measured spill-part counts across three configurations (46, then 7, then 0\) and compared memory consumption between the old and new paths.

What followed was a two-bot relay. [groeneai](https://github.com/groeneai), another ClickHouse bot, reproduced the counters and narrowed the blast radius: the failure required a raised tuning threshold rather than the default configuration. ClickGap publicly accepted the correction instead of defending its original severity, and the [fix](https://github.com/ClickHouse/ClickHouse/pull/115038) was merged within a day.

**The silent performance bugs** ([#114990](https://github.com/ClickHouse/ClickHouse/issues/114990), [#114105](https://github.com/ClickHouse/ClickHouse/issues/114105)). Neither defect crashes the server or corrupts results. Both quietly make queries more expensive.

In #114990, a skip index was built, stored on disk, and then ignored. A query that previously read one of sixteen granules now read all sixteen while returning identical results. Result assertions cannot detect that failure; they see the same answer, but don’t see that it’s now doing sixteen times the work.

In #114105, an unconditional `std::adjacent_find` added another scan to a hot constructor, slowing array-heavy queries by 14.6 to 30.9 percent. Performance claims demand stronger evidence because CI timings naturally fluctuate. This report separated signal from noise: across more than a thousand measurements, master varied by only a fraction of a percent while the change produced double-digit regressions. It also identified the exact code path and cited the source comment contradicted by the measurements. “Correct but slower” is a defect class of its own, and catching it requires statistics rather than assertions.

**The coverage business** ([#114766](https://github.com/ClickHouse/ClickHouse/pull/114766), one of roughly 200). Machine-written tests commonly fail in two ways: they execute the new code without detecting whether its behavior is broken, or they duplicate coverage the existing suite already provides.

Every ClickGap coverage finding must clear both bars. The analysis must identify an exact single-line source mutation that would make the new test fail and explain what the test covers that the reviewed pull request’s own tests do not. If it cannot answer either question, the finding is dropped.

For the strongest claims, ClickGap runs the experiment. It deliberately breaks the behavior under test, builds the modified server, and demonstrates that the new test fails while the tests submitted with the original pull request remain green.

## How it works {#how_it_works}

ClickGap is a single daemon watching the merge stream. Eligibility is decided once, at intake. Reverts, re-ports of previously reviewed changes, and pull requests too large to analyze are skipped; everything else enters the pipeline. For each eligible pull request, the daemon syncs the source, provisions a binary verified to contain the merge commit (downloading a fresh CI artifact when possible and building from source otherwise) and prepares an isolated worktree with a warmed server.

Two analysts run against that environment. The bug analyst forms hypotheses, but each must be converted into an executed test. A hypothesis advances only when the observed behavior disagrees with the expected contract. The coverage analyst runs second, seeded with line-level coverage for the changed code. It is skipped when those lines are already covered.

Each candidate finding first faces an adversarial reviewer whose sole job is to reject it. Anything that survives must then clear ten gates enforced by the pipeline:

1. **Concrete consequences.** The defect must produce an observable impact: a wrong result, data loss, a crash, a security flaw, rejection of valid input, a measured slowdown, or lost CI signal. “This code is dead” is not enough.  
2. **Valid citations.** Every referenced file and line must exist in the current source tree.  
3. **Complete-file review.** The analyst must read each changed file in full, not only the diff.  
4. **Caller analysis.** The analyst must inspect the code paths that invoke the changed code.  
5. **Existing-test search.** The test suite must be searched in at least three distinct ways. Few mistakes destroy trust faster than reporting a “missing test” that already exists.  
6. **Executed reproducer.** The proving test must run against a real binary.  
7. **Evidence matches the claim.** A bug finding must include the observed failure. A coverage finding must produce the proposed test as a real file on disk.  
8. **Coverage kill-tests.** Coverage claims face targeted challenges: is the gap real, and does the proposed test detect the behavior it claims to protect?  
9. **Reviewer approval.** The adversarial reviewer’s verdict must be recorded as a pass.  
10. **No known false-positive match.** Each finding is compared with past mistakes corrected by maintainers. An error learned once cannot be filed twice.

Eight gates are implemented entirely as ordinary code. Only the coverage kill-tests and adversarial verdict require model judgment.

After all ten gates pass, the pipeline chooses an external action. A coverage gap becomes a test-only pull request. A locally reproduced bug becomes an issue. A bug with a runnable test that cannot be confirmed locally becomes a proof pull request, allowing ClickHouse CI to act as the prover. Most candidates produce no external action at all.

Ownership continues after filing. ClickGap monitors CI for every submission and classifies each failure as its own test, a known flaky test, or infrastructure. If ClickGap caused the failure, it reads the logs and pushes a repair, with a maximum of five attempts before escalating to a human. Every repair passes its own gates, including two consecutive local runs, because one passing run may only indicate flakiness.

Review feedback enters the same closed loop. When a reviewer requests changes, ClickGap updates the submission, reruns validation, and replies with evidence. A separate daemon-side verifier then executes the tests independently. No analyst can certify its own success.

![](https://clickhouse.com/uploads/clickgap_aug2026_agentic_bug_review_memory_b038927b7c.jpg)  

From merged PR to filed artifact. Every finding must survive execution, adversarial review, and ten gates enforced in code before any issue or pull request is filed; the archive bin, not the tracker, is where most findings end.

## Where the findings actually come from {#where_the_findings_actually_come_from}

The gates explain why maintainers can trust what ClickGap files. They do not explain how it finds anything worth filing. Detection rests on four advantages.

**First, it reads beyond the diff.** The gates require the analyst to read every changed file in full, inspect each caller, and follow equivalent logic into sibling code paths. That reach exposed the earlier `gini` regression ([#113763](https://github.com/ClickHouse/ClickHouse/issues/113763)): the root cause involved six sibling overrides and a consumer the original diff never touched. The same pattern recurs across the tracker: a pull request repairs an invariant in one branch while leaving an equivalent neighboring branch unchanged.

**Second, it works from a checklist rather than intuition.** The review prompt contains roughly twenty ClickHouse-specific defect patterns, covering areas such as join edge cases, concurrency hazards, and lifetime errors. Each pattern specifies what to inspect and where to search. The list grows from evidence. A separate process has analyzed nearly 2000 confirmed ClickHouse bugs and converted their lessons into memories for future reviews. When a bug matches no existing pattern, the system drafts a new checklist entry.

**Third, coverage gaps are measured rather than inferred.** LLVM line coverage identifies the exact changed lines that no test executes. Even then, an uncovered line counts only if the analyst can name a mutation that the proposed test would kill and explain the user-visible risk.

**Fourth, economics favors breadth.** Hypotheses are cheap, a complete review costs a couple of dollars in model usage, and local validation takes minutes. The analyst can explore many candidates for each pull request and retain only those whose executed tests disagree with expected behavior. Every review also begins with roughly thirty recalled lessons from prior findings.

Detection itself is continuously tested. The benchmark starts with real bugs that ClickGap previously found and maintainers confirmed. For each one, the repository is rewound to the moment the reviewed pull request merged, while the defect was still present, and the analyst reviews that state again from scratch. The question is binary: does it rediscover the bug?

Every proposed efficiency change, such as shortening the prompt, runs against the same corpus under both the old and new configurations. If the cheaper configuration misses bugs the existing one catches, it does not ship.

## Cheap on purpose, measured for it {#cheap_on_purpose_measured_for_it}

A couple of dollars per pull request reviewed. The recall benchmark above is its guardrail: a cost reduction that weakens bug detection does not ship. A cheap reviewer that catches nothing is not efficient; it is merely lower-cost noise. Within that constraint, savings come from four places.

**Plain code consumes no model time.** Work with an exact contract runs as ordinary code: repairing issue bodies to match the upstream template, detecting duplicate filings by comparing files and overlapping titles against ClickGap’s history, and rendering the self-review checklist. These operations cost no tokens and cannot drift.

**Smaller models handle recoverable work.** One condenses long CI logs before the primary analyst reads them. Another runs mutation tests against coverage claims. A third provides a second opinion on whether a bisected commit could plausibly have caused the failure before anyone is mentioned publicly. In each case, an incorrect result is either caught downstream or survivable by design. The expensive model with extended reasoning is reserved for the two judgments the system depends on: finding bugs and rejecting weak findings.

**Work unlikely to justify its cost is skipped.** Well-covered changes bypass the coverage analyst. Ineligible pull requests never enter the pipeline. Finding classes that maintainers consistently ignore are automatically suppressed.

**Every optimization must preserve recall.** When we shortened the analyst’s prompt, the candidate version had to pass a paired benchmark against the full prompt using the same confirmed-bug seeds. It matched the baseline: its only paired miss rediscovered the bug on both reruns, indicating run-to-run variance rather than a repeatable regression. It also found one bug the full prompt missed while reducing cost by 11 percent and session time by 17 percent. Only then did it become the default.

There is a second economy here, much larger than the bot’s own bill: the engineering cost avoided by catching defects early. A bug reported within hours of its merge is usually fixed with a follow-up commit. The diff is still fresh in the author’s mind, nothing has shipped, no users are affected, and the fix lands only on master.

Once the same defect reaches a release, the cost multiplies. Someone must determine which released versions are affected, bisect the regression to its introducing commit, and backport the fix to every affected release branch. Each bug caught between merge and release avoids that entire bill. That is the real return on reviewing at merge time.

## Never name the wrong PR {#never_name_the_wrong_pr}

A report that says, “This regressed in 26.4, this commit introduced it, and these supported branches still carry it,” is worth ten reports that merely say, “This is broken.” 

The affected-version matrix is deterministic code. For every ClickHouse release still under support, it downloads the real binary, executes the reproducer, and records the outcome. The reproducer is intentionally narrow: a small script receives a binary and exits `1` when the bug appears or `0` when it does not. A timeout counts as neither result. It also runs without secrets in its environment because reproducers are shaped by issue reporters and cannot be treated as fully trusted.

Bisection identifies the introducing commit by testing builds between a known-good and a known-bad point. ClickGap obtains those builds from three sources: official release binaries back to roughly 25.8, per-commit CI artifacts from master, and source builds wherever gaps remain.

Every candidate build is tested up to three times, with timeouts abstaining from the vote. A single flaky result cannot redirect the search. At the final boundary, the suspected commit must still fail while the nearest earlier testable build passes. Confidence decreases for every untestable commit in the range and can never increase to compensate.

Before any pull request is named, a final causal check asks whether its change could plausibly produce the observed failure. It vetoes the attribution only when the answer is clearly no. The governing rule is simple: naming the wrong pull request is worse than naming none. The ledger shows that ClickGap follows it. The bisector abstains because a defect is too old or the evidence gaps are too wide, roughly three times as often as it identifies a culprit.

## The part nobody plans for: earning trust {#the_part_nobody_plans_for_earning_trust}

The commit history tells this part of the story better than any retrospective could.

Day one includes a commit titled “Increase filing limits to 10 (PRs, issues, daily, concurrent).” We assumed throughput would be the bottleneck. For three days—until the first crash report and first coverage pull request landed—the evidence even seemed to support us. The next five months taught the opposite lesson.

The low point arrived about six weeks in, when ClickGap published its private reasoning as a comment on a real pull request instead of posting an answer. The fix appears in the history as “Stop bot from posting LLM-reasoning-as-reply spam.” A second commit followed the same day: “refuse to post LLM-meta-reasoning-as-reply spam (final layer).” The first layer, unsurprisingly, had not been final.

We then audited every path capable of publishing a message under “Close residual spam vectors.” That audit also revealed duplicate alerts flooding our own Slack. The next day, we built the control that should have existed from the start. It tracks the previous thirty days of filed issues. If fewer than 25 percent receive any maintainer response, ClickGap stops filing lower-confidence findings until engagement recovers.

Filing volume stopped being a configuration value we controlled. It became a privilege maintainers continuously grant.

Measurement forced the next humiliation. We took one thirty-day window and asked a simple question: of the findings the bot proposed, how many did maintainers actually accept? A third of coverage findings; half of bug reports. That number is the reason the consequence gate exists, and the reason the bot now files far fewer bug reports than its analysts propose.

Some of the hardest failures came from components returning valid-looking answers after doing no useful work. The affected-versions check was initially agent-driven. Its chosen download helper supported only amd64, while ClickGap ran on aarch64. Every fetch failed, so every version came back `unknown`. Because `unknown` is valid when a build genuinely cannot be fetched, the failure looked like conservative reporting rather than complete loss of coverage. We replaced the check with deterministic code that distinguishes a tested version from a failed fetch.

A similar failure occurred in CI log summarization. ClickHouse’s test runner prints a ✅ or ❌ for each test. A small model interpreted that pattern as a code-review prompt and emitted `Final Verdict: ✅ Approve`. The downstream parser treated `Approve` as a passing test result, leaving a real failure unhandled. Review-shaped summaries are now rejected before they reach the parser.

Both incidents reinforced the same rule: plausible state is not evidence of successful execution. A standing reconciler now walks every in-flight item and checks its recorded state against the underlying artifacts and external systems.

The maintainer-facing output changed just as much as the pipeline. The commit history records the progression: “issue bodies to maintainer spec — TLDR, code links, folds, author cc, no banner,” followed by “Trim every remaining maintainer-facing surface to the point” and “Stop silencing human maintainers behind CI-bot churn.”

A new issue now exposes roughly ten lines by default: a bold symptom, a permalink to the suspected root cause, a one-command reproducer, and expected versus actual behavior. Supporting analysis is collapsed into detailed blocks, including an “Open risks” section that separates verified facts from unresolved assumptions.

Replies are limited to five per thread and reviewed before posting. The reviewer may rewrite a response, but it cannot discard a reply to a maintainer. That restriction exists because suppressing an imperfect answer looks indistinguishable from ignoring the person who reported the problem.

![](https://clickhouse.com/uploads/clickgap_aug2026_image2_9ab359cb5a.png)  

**What a maintainer actually sees when a ClickGap issue opens**: the symptom, the root-cause permalink, a one-command reproducer, and everything else one click away.

And when the bot is wrong, the response is part of the product. Shown a false positive on a self-referential system.processes query, it answered: "You're right, and thanks for the precise diagnosis... I'll add self-referential system.processes.query reads to the oracle's exclusion list so this class doesn't get filed again" ([#110141](https://github.com/ClickHouse/ClickHouse/issues/110141)). That exclusion shipped. Every such verdict lands in a disagreement ledger, and the ledger is what the bot studies.

## Memory, and why Loom exists {#memory_and_why_loom_exists}

ClickGap stores experience at three levels. Case memories record the history and outcome of individual findings. Lessons extract reusable rules from those cases, either through automated learning flows or operator review. A doctrine file holds the smaller set of rules that every analyst and reviewer run must receive; other memories are retrieved only when relevant.

The doctrine file is limited to 150 lines because its entire contents accompany every finding. Admission is strictly evidence-based: each rule must cite a human maintainer’s verdict. The bot’s own conclusions are ineligible. Reviewer-specific preferences may be included only when substantiated by actual review feedback.

Each review records the keys of the memories it retrieved. Once a finding reaches a terminal state, a positive outcome boosts those memories’ future rankings, with the effect decaying on a 90-day half-life. Negative outcomes are retained but do not immediately penalize individual memories. Because a review typically retrieves about 30 lessons, a single bad outcome provides insufficient evidence to determine which memory, if any, contributed to it.

The memory plane began as a local SQLite store. A few months later, it moved to Loom, an internal memory service built at ClickHouse for AI agents. Loom stores typed, tagged memories in ClickHouse and exposes search, provenance, and outcome feedback through an API.

The migration had to clear a retrieval benchmark before it shipped, and it paid off in two ways. First, it corrected our intuition. Restricting recall to memories tagged with the same subsystem as the bug (its area of the codebase: joins, replication, storage) seemed sensible. In blind evaluation, it reduced retrieval quality by 22 percent because the strongest lessons often crossed subsystem boundaries. Treating those same tags as soft ranking signals instead improved quality by 12 percent.

Second, Loom made memory impact measurable. Every retrieval leaves a trace that can be joined with what maintainers ultimately did with the finding. “Did this lesson ever help?” stopped being a matter of intuition and became a query.

## What comes next {#what_comes_next}

ClickHouse development spans both public and private repositories. Recently, a second fully isolated instance, `clickgap-private`, began operating against the private repository and filed its first issues within a day. It immediately faced the cold-start problem: without a history of maintainer verdicts, a new bot is liable to repeat every mistake the public instance has already learned from.

The private instance writes to its own namespace, which began empty, and reads through a one-way join to the public namespace. At query time, it inherits the experience encoded in thousands of public memories, while everything it learns remains private.

The difficult part was making “one-way” absolute. ClickGap issues writes against recalled memories for outcome reinforcement and provenance links. After the join, however, a recalled key may belong to the public namespace. Every write is therefore filtered by key ownership, and the server independently enforces the namespace boundary. A public search can never return a private key. We use two safeguards, because this kind of leak would be silent.

Whether experience transfers across codebases remains an open, measurable question. The same recall-to-outcome instrumentation runs on both sides. Ask us again in a quarter.

![](https://clickhouse.com/uploads/clickgap_aug2026_loom_public_private_memory_dcc80e80b4.jpg)  

How clickgap-private starts from N instead of 0. Reads federate one way across namespaces; writes are filtered by key ownership. Nothing is copied, nothing private flows back: inheritance at query time, not by copy.

## If you want this for your own codebase {#if_you_want_this_for_your_own_codebase}

Most of these principles apply even if you never build a bot. They describe a disciplined QA culture encoded and enforced in software.

1. **Scope it to one codebase, and mean it.** Most of ClickGap’s precision comes from ClickHouse-specific knowledge, not the model.  
2. **Charge an evidence toll before anything external happens.** Require an executed test, verified citations, and a consequence a user would notice.  
3. **Use determinism wherever determinism is possible.** Agents drift; `for` loops do not.  
4. **Treat confident negatives as the most dangerous output.** A false positive wastes an afternoon. A false negative leaves the defect for the next control to catch, and sometimes that next control is a user.  
5. **Never name an unconfirmed suspect.** “Incomplete range” is better than the wrong author.  
6. **Design every report for a ten-second scan, then throttle based on outcomes.** If humans stop engaging, automatically file less.  
7. **Let only human verdicts become doctrine.** Measure whether memory improves outcomes instead of assuming it does.  
8. **Budget for the grind.** Expect three fixes for every feature, concentrated around trust, state recovery, and correctly interpreting your own CI.

## The point {#the_point}

We built ClickGap because the merge stream had outgrown human review capacity. The results suggest the bet paid off: roughly 500 issues filed, more than 200 closed with a linked fix PR, and around 200 test-coverage PRs, all in public and against a codebase already tested exhaustively.

Most of the machinery was not designed to make the bot smarter. It was designed to make the bot worth listening to, which turned out to be the real product. Its reports enter the same tracker as everyone else’s and stand or fall on the same evidence. 

The numbers in this post are deliberately rounded. Public counts can be reproduced through GitHub searches against the bot’s account.

If building systems that must earn trust in public sounds like your kind of problem, [ClickHouse is hiring](https://clickhouse.com/company/careers).


---

## Get started today

Interested in seeing how ClickHouse works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-1632-get-started-today-sign-up&utm_blogctaid=1632)

---