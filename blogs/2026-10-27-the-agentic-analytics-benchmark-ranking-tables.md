---
title: "The Agentic Analytics Benchmark: ranking tables and labeling failures with Jev"
date: "2026-10-27T16:57:44.552Z"
author: "Eduardo Vellasques, Lionel Palacin and Al Brown"
category: "Engineering"
excerpt: "Jev ranks warehouse tables and labels agent failures in under a second, but adding retrieval hints leaves accuracy flat across 20 models on the Agentic Analytics Benchmark."
---

# The Agentic Analytics Benchmark: ranking tables and labeling failures with Jev

This post is about Jev, TypeSafe's System One model, and what it did for us on the Agentic Analytics Benchmark. Jev does not generate text. You hand it some state and typed questions (a yes/no answered as a calibrated probability, a pick-one choice, a rubric score), and it returns typed answers with confidence in roughly 70 to 500 milliseconds. One call can carry many questions, and nothing in the call is specific to a benchmark: the state is whatever you pass in, and the questions are plain instructions. That makes it a classifier over whatever you hand it, and we gave it two jobs: reading a failed run and saying what went wrong, and reading a question and saying which tables it needs.

## TL;DR {#tldr}

* Jev labels every failure in under a second. On a four-model development run, the finer taxonomy makes wrong data selection the largest bucket, most of it entity resolution rather than wrong table, and flags 18 answers the grader likely scored wrong.  
* Jev also ranks the warehouse's tables per question at nDCG@10 0.951 in 0.4 seconds, with no fine-tuning and no gold data at run time.  
* Fed back to the agent as an in-loop hint, the ranking left accuracy flat across 20 models, and the turn saving on the development set did not survive the board. The ranking is the result; the hint is not.

## Finding the right tables, and whether telling the agent helps {#finding_the_right_tables_and_whether_telling_the_agent_helps}

This is the second half of round two. The companion post added GPT-6, Claude Opus 5.5 and Claude Sonnet 5.5 to the board; this one asks whether a cheap retrieval component built on Jev can move it. The first post found that finding the tables matters more than joining them. Models in the top half of the board discover the dimensional CRM tables on 87 to 99% of the questions that need them; models in the bottom half often do not find them at all. On the 201-question board, the five most accurate models query 78% of the dimensional tables their questions need, the five least accurate 49%, and 43% of failed runs never read at least one table the reference answer uses.

That is a retrieval problem, and retrieval is something you can put in front of any model without retraining it. So we asked: if a cheap component ranked the tables before the first query, and the agent was told, would the wrong-table failures go away? Two question sets appear below. The 201-question board is frozen and scores a model once. The 136-question development set is a separate set over the same 18-table warehouse, built so we can run experiments and set thresholds without touching the board. Everything Jev was tuned on comes from the development set; the board is the held-out check.


### Labeling every failure, and auditing the judge

The first post classified every failure into five modes (no attempt, wrong plan, wrong data selection, wrong implementation, runtime error) with a frontier-model classifier. That works, but it is coarse, and it presumes the failure is real. We wanted something cheap enough to run on every eval that also answers two finer questions: what exactly went wrong, and did the grader get it right?

For each failed run, the labeler hands the classifier the trajectory (question, reference and candidate SQL, results, final answer) and asks four questions in one call: which of sixteen failure sub-modes fits, which system-prompt rule would have prevented it, whether a schema hint up front would have helped, and whether the answer looks correct despite the fail verdict. Anything checkable from the SQL text, such as whether it filtered on the snapshot date, is decided in code and passed in as a fact, so the classifier only makes the judgment calls.

In code, the four questions are two choices and two yes/no probabilities, sent in one call with the trajectory as the state. This is the shape of the labeler as it ships in the repository, trimmed:

<pre><code type='click-ui' language='python'>
from typesafe_sdk import TypeSafeClient, Choice, Noul

questions = {
    "sub_mode": Choice(
        instructions="Given the question, the reference SQL and answer, and "
                     "the candidate's SQL, results and final answer, pick the "
                     "single most specific sub-mode for why it failed.",
        criteria=SUB_MODES),    # 16 sub-modes, each with a one-line meaning
    "prevented_by_rule": Choice(
        instructions="Which judgment-call schema-prompt rule best explains "
                     "the failure? Choose 'none' if no listed rule does.",
        criteria=RULES),        # the rule set is a config file
    "schema_hint_would_help": Noul(
        instructions="Would a correct schema-use hint before the first "
                     "query most likely have prevented this failure?"),
    "correct_despite_fail": Noul(
        instructions="Does the candidate's final answer actually look "
                     "correct for the question, despite being scored a failure?"),
}

with TypeSafeClient() as client:
    resp = client.system_one(state=trajectory, questions=questions)

resp.choices["sub_mode"].choice            # e.g. "wrong_identifier"
resp.nouls["correct_despite_fail"].noul    # a calibrated probability, 0 to 1

</code></pre>

The state is a dictionary: the question, the reference SQL and answer, the candidate's SQL, result sets and final answer, and the facts the code already decided, such as whether the SQL filtered on the snapshot date. Jev answers all four questions from that one payload.

We ran it over a four-model development-set run (Claude Sonnet 4.6, GPT-4.1, Qwen3-Coder 30B, Gemini 2.5 Flash): 277 failures across 544 attempts. Three things came out.

**The finer taxonomy moves the largest bucket.** Every sub-mode nests under exactly one of the five coarse modes, so the two views are comparable. Under the coarse modes, wrong plan is the most common failure. Under the sub-modes, wrong data selection is the largest bucket (87 of 277), and most of it is entity resolution: using the wrong identifier or literal for an organization (29), or never resolving the named entity before querying facts (20), together outweigh picking the wrong table (28) or column (10). The sub-modes pull entity-resolution and wrong-table errors out of "planning" and localize them. That is what pointed at table retrieval as the lever to try.

**Failure profiles are model-specific.** Gemini 2.5 Flash gives up after an empty result. GPT-4.1 writes SQL that does not run and carries about half the runtime errors. Qwen3-Coder 30B spreads across plan, data and no-attempt. Sonnet 4.6 fails on substance and carries 6 of the 7 grader-artifact cases. Label confidence rises as models get weaker, which is what you would expect: clear-cut failures are easier to name.

**The judge needs auditing, and a classifier can do it.** “Correct despite fail” is scored on every failure, not only on the ones labeled as a grading problem, so it flags 37 of 277 as possible grader errors; a threshold of 0.65 narrows that to 18. Tracing the high-confidence ones landed on one mechanism in our deterministic comparator: it returns "not equal" on a row-count difference before it gets to linking columns, so a correct answer that splits one question into one query per entity, or returns a time series where the reference is a snapshot, is scored as a fail. That comparator bug is now tracked. “Correct despite fail” is also a category the five failure modes cannot express, because they presume the failure is real.

![](https://clickhouse.com/uploads/jev_oct2026_image1_888b51a460.png)

*The 277 failures of a four-model development-set run, by sub-mode, coloured by the coarse mode each nests under. The largest single bar is stopping early after an empty result, almost all of it Gemini 2.5 Flash. Summed by colour, wrong data selection is the largest bucket, most of it entity resolution rather than wrong table. Grey bars are not model failures: seven answers judged correct despite a fail verdict and one ambiguous question.*

**One example.** Asked for one organization's MRR, GPT-4.1 split the company name "*White, Leonard and Kelly*" into three names, got an empty result, and reported that no such organizations exist. The labeler calls it wrong identifier at 0.94 confidence, attributes it to no stated rule (correct: nothing in the prompt covers splitting a name, and every mechanical check on the SQL is clean), scores "**a schema hint would have helped**" at 0.78, and "**correct despite fail**" at 0.20. A purely semantic failure that no regex catches, labeled in one call.

### Ranking the tables

For the ranking job the state is the question plus the warehouse schema, and the questions are one yes/no per table: "*does answering this question need this table?*"

Scored against the tables the reference SQL reads: mean nDCG@10 of 0.951, recall@10 of 0.991, and for 84% of questions the top five tables already contain every table the answer needs. About 0.4 seconds per question.

![](https://clickhouse.com/uploads/jev_oct2026_image2_0ea704181c.png)

*Table ranking quality on the 136-question development set, scored against the tables the reference SQL reads. Recall at k is the share of needed tables that appear in the top k; all-required at k is the share of questions whose top k already contains every table the answer needs. Both climb fast: at five tables, recall is 95% and 84% of questions have everything they need, and at ten tables recall is 99%. The gap between the two lines is the questions that need two or three tables where one of them ranks low; it is also why the ranking is delivered as a hint and never used to prune the schema.*

Part of that recall is the warehouse being small, at 18 tables. In a companion pilot on public text-to-SQL catalogs with 75 to 710 tables (BEAVER, BIRD, Spider, MMQA, 250 cases), the same yes/no ranking reached 87% recall@10 and found every required table in 73% of cases, at a p90 of 3.4 seconds and about $0.50 for the whole run. That is well below 0.991, and it is still ahead of two agents that explored the same schemas with SQL queries, which found fewer required tables and took 25 to 83 seconds per case. So the method carries to wide catalogs; the near-perfect recall does not, and on a real warehouse you should expect the former.

### Two ways to use the ranking

A good ranking is only useful if the agent acts on it, and the agent is not ours to retrain: it is whichever model is being benchmarked, with the schema in its prompt and a tool that runs SQL. So the ranking has to reach the model as text it can read, and two constraints shape how.

First, the ranking cannot simply replace the schema. For about one question in six, a table the answer needs sits outside the top five, so removing lower-ranked tables from the prompt would make those questions unanswerable. The full schema stays in the prompt, and the ranking only says where to look first.

Second, putting the ranked tables in the system prompt does not help. In a two-model pilot, prepending the top five tables to every question moved the pass count by +6 of 136 for GPT-4.1 and +7 of 125 for Qwen3-Coder 30B, while re-grading the same baseline runs flipped 21 and 28 verdicts: inside grading noise. Prepending it only to the runs that had missed a needed table did better. GPT-4.1 recovered 11 questions and regressed none, Qwen3-Coder 30B recovered 13 and regressed 3. But that selection needs the gold answer.

Given that in real life we don’t have access to the gold answer, we use a proxy: the classifier's confident set. This is defined as the set of tables it scores at 0.5 or above. A query that reads none of them is usually reaching for the wrong table. That is the in-loop gate.

**In the loop.** The gate checks every query the model runs. If none of the tables the run has read so far is in the confident set, it adds a short note to that query's result, containing:

* The table the query read  
* The top three ranked tables  
* An instruction to check whether the table holds the asked-for data and to query the top-ranked table if not

As mentioned before, the full schema stays in the system prompt. The gate checks every query but adds its note at most once per run. The note is appended to the result of the query that triggered it, not sent as a message of its own, so it does not cost the model an extra turn, and a gated run and its baseline are compared at the same 60-turn budget.

![jev-schema-retrieval.png](https://clickhouse.com/uploads/jev_schema_retrieval_8929dd2f16.png)

*For each question the classifier scores every one of the 18 tables with a yes/no probability, and the tables at 0.5 or above form the confident set. Up front, the top five tables are prepended to the prompt. In the loop, the gate checks each query the agent runs; when none of the tables read so far is in the confident set, it appends a note to that query's result naming the top-ranked tables. Neither path removes anything from the schema the agent sees.*

**A worked example.** Take the question "*graph MRR per month per sub-region / AE / territory in EMEA North region, last 12 months*". Four tables score above 0.5 and fourteen sit well under. One of the two tables the answer needs is in the confident set; the other, the monthly MRR table, scores 0.27 and is not. This leads to the following:

* A query that reads the account dimension is inside the set, so nothing happens.  
* A query that reads the service dimension (0.08) is outside it, so the note fires and points at the account dimension.

Two dev-set runs on this question show both outcomes. **o4-mini** never read the account dimension in its baseline run. With the gate on, its first queries read tables outside the confident set, the note fired once and named the account dimension, and the model queried it. Both runs pass, in 12 and 14 turns. The baseline already had the answer, so the note could only change the path, and it did: this example shows the mechanism firing as designed, not a recovery. Claude Haiku 4.5 failed in two turns without reading either needed table, but the tables it did read were in the confident set, so the gate never fired and the gated run failed the same way.

![](https://clickhouse.com/uploads/jev_oct2026_image4_b05b22cb46.png)

*Per-table probability for one real question. Four tables clear the 0.5 line and form the confident set. Stars mark the tables the reference SQL reads: one is inside the set, the other is not. A query that reads inside the set runs unremarked; one that reads outside it gets the note.*

### Does it help?

We ran the gate paired, on and off for the same question and model at the 60-turn budget, across 20 models on the 136-question development set and the 201-question board, graded by the benchmark's normal jury. The deltas below are on the cells where the gate actually fired (14% of dev cells, 20% of board cells). Intervals are 95% bootstraps.

| Set | Fired cells | Recovered / regressed | Net (95% CI) | Turns | Output tokens |
| ----- | ----- | ----- | ----- | ----- | ----- |
| Dev (136 q) | 371 | 34 / 40 | −6 (−23 to +11) | −6.1% (−12.1 to +0.1) | −9.3% (−25.4 to +5.8) |
| Board (201 q) | 812 | 87 / 69 | +18 (−6 to +42) | +0.5% (−4.8 to +6.4) | −6.1% (−16.1 to +3.9) |
| Pooled | 1,183 | 121 / 109 | +12 (−18 to +42) | −1.5% (−5.6 to +2.9) | −7.1% (−15.5 to +1.4) |

**Accuracy is flat.** The dev set leans one way, the board the other, and pooled the net is +12 with an interval that spans zero. The mechanism does what it is built for: 34 of the 121 recoveries follow the exact chain (the baseline skipped a gold table, the note named it, the gated run queried it). But 19 of the 109 regressions ran the same chain and the model still got the answer wrong, and the rest on both sides is run-to-run noise. Knowing the right table is not the bottleneck; using it correctly is, and that is a plan failure the hint cannot fix.

**Turns: a dev-set saving that does not survive held-out questions, for a reason worth knowing.** On the dev set, gated runs used 176 fewer query turns in aggregate. On the board the saving is gone. The mechanism is identical on both: over-exploring runs (10 or more baseline turns) are 22% of fired cells on both sets, and the gate cuts them by 17% in turns and 17% in output tokens on both. What differs is the other 78%. Runs that were already short pay a tax when the note lands: +6% turns on the dev set, +17% on the board. The saving did not disappear on held-out questions. A larger tax on runs that were already fine cancelled it.

**Output tokens: suggestive, within noise.** The output-token reduction points the same way on both sets and none of the intervals excludes zero. The aggregate is carried by a few long runs, and that tail cuts both ways: one Gemma 4 31B cell went from 29 turns and 1,628 output tokens at baseline to the 60-turn cap and 48,910 tokens with the note. Amortized over all runs, since the gate fires on one run in five to seven, the output saving is about 1% and the turn effect is nil.

![](https://clickhouse.com/uploads/jev_oct2026_image5_07f16fab7c.png)

*Per model, the change in turns and in output tokens on the cells where the gate fired, on the development set and on the held-out board. The bar is the aggregate over those cells, which is what rolls up to the totals in the table above; the tick is the median cell. On the development set the median cell is flat for most models while the aggregate is pulled down by a few over-exploring runs. On the board the same tail turns into a cost, with one Gemma 4 31B cell running to the turn cap. Each model rests on 8 to 61 fired cells, so read the bars as spread, not as results.*

### What we keep

The labeler is an instrument we now run on every development-set eval: one offline pass gives the coarse failure breakdown, the finer sub-modes, and a grader audit, for well under a second per failure. Its finer taxonomy also revises the first post's headline: a share of what we called wrong plan is wrong table or wrong entity, which is retrieval, not reasoning.

The retrieval ranking is the part that works: a sub-second, near-free component that puts the right tables at the top of the list for a question, with no fine-tuning and no gold data at run time. Anyone building an analytics agent over a wide schema should have one.

The in-loop hint is the negative result, and reporting it is the point. It leaves accuracy flat, it cuts turns only where a model was over-exploring, and on held-out questions that cut is cancelled by the tax it puts on runs that were fine. The board told us the same thing from the other direction. In the companion post, Sonnet 5.5 improved on the dimensional questions without discovering the tables any more often than Sonnet 5. The frontier models already find the tables. What they get wrong is what to do with them.

## Run this on your own data warehouse {#run_this_on_your_own_data_warehouse}

Nothing here is specific to our warehouse or to ClickHouse. The harness is the same one the first post described: an instrumented assistant, a modeled warehouse schema, a curated and anonymized question set with committee ground truth, and a judge panel in which no model grades its own answers. Adding a model is a registry entry and one command, and the engine pin means a re-run reproduces the board.

Your warehouse will have its own discriminator. Ours is a dimensional CRM layer; yours might be a slowly changing dimension, a semi-structured event table, or a naming convention nobody wrote down. The only way to find it is to run the benchmark on your schema, with your questions, and look at where the models fail.

## What's next {#whats_next}

The split-role architecture question from the first post (strongest model plans, cheapest model executes) is still the follow-up we are most interested in, and the flat result on hints sharpens it: if the plan is where the models fail, the plan is where the expensive model belongs. On the retrieval side, the ranking has been scored on an 18-table warehouse and a 250-case public pilot; the open question is the catalog size at which a hint starts to pay for itself.

## Code {#code}

* Harness: [github.com/ClickHouse/data-agent-mnist](http://github.com/ClickHouse/data-agent-mnist), Apache 2.0.  
  * The labeler and the ranker ship as the optional Jev extra  
  * The README section "*Optional: ranking and labeling with Jev*" covers setup, which needs a TypeSafe key.  
  * schema_retrieval.py scores the ranking  
  * schema_retrieval_agent.py feeds it to the agent up front or in the loop and measures the delta  
  * label_failure_modes.py labels a graded run. The rule set the labeler checks is a config file you copy for your warehouse.

---

## Get started today

Interested in seeing how ClickHouse works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-2800-get-started-today-sign-up&utm_blogctaid=2800)

---