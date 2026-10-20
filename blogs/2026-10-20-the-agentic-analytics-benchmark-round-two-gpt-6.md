---
title: "The Agentic Analytics Benchmark, round two: GPT-6, Claude Opus 5.5, Claude Sonnet 5.5"
date: "2026-10-20T08:07:44.299Z"
author: "Eduardo Vellasques, Lionel Palacin and Al Brown"
category: "Engineering"
excerpt: "We added GPT-6 Astra, Luna and Sol, Claude Opus 5.5 and Claude Sonnet 5.5 to the Agentic Analytics Benchmark: all five land mid-board within a point of each other, and Sonnet 5.5 brings the biggest change in turns, cost and truncated runs."
---

# The Agentic Analytics Benchmark, round two: GPT-6, Claude Opus 5.5, Claude Sonnet 5.5

## TL;DR

In September we published the [Agentic Analytics Benchmark](https://clickhouse.com/blog/agentic-analytics-benchmark-data-agent-mnist): 29 models answering 201 analytics questions over a synthetic ClickHouse data warehouse, each writing its own SQL in an agentic loop. This is the follow-up.

* We added five models to the Agentic Analytics Benchmark: the GPT-6 family (Astra, Luna, Sol), Claude Opus 5.5 and Claude Sonnet 5.5, on the same 201 questions, warehouse and judge panel as the first post.
* Claude Fable 5.1 keeps the top spot at 76.6%. All five new models land in a 68.7 to 69.7% band, mid-board and statistically tied with each other.
* No GPT-6 variant passes GPT-5.5 at default reasoning effort, and the three are within one point of each other.
* Sonnet 5.5 is the largest generational step this round: 6.5 points over Sonnet 5, zero runs out of budget against 16, at about 5 cents per question.

## Terms used in this post {#terms_used_in_this_post}

* The board: the 34 models ranked by pass rate on the 201 questions at a 60-turn budget. It is frozen: a new model is added with the same questions, warehouse and judges.
* Turn: one model call. A turn can issue several SQL queries. The budget is 60 turns per question.
* Turn-limited (TL): a run that hit the 60-turn budget without answering. It counts as a fail.
* Judge panel: three model judges, one seat per provider, that vote on each answer. The candidate's own model never grades it.
* Column linker: two correct answers can name columns differently. When one answer's columns contain the other's, the shared columns match by name with no model call. Otherwise a small model is asked which columns correspond, and the result comparison runs on that mapping.
* Dimensional CRM layer (dbt_dds): the warehouse's normalized tables. 83 of the 201 questions need them, and finding them was the first post's main discriminator.

## What changed since the first post {#what_changed_since_the_first_post}

The [first post](https://clickhouse.com/blog/agentic-analytics-benchmark-data-agent-mnist) ran an agentic loop (the model writes SQL, reads results, and decides when to answer) with a 60-turn budget, a deterministic result comparison, and a judge panel with one seat per provider, where no model grades its own answers. None of that changed. This post adds five models.

The harness changed too. It is public at [github.com/ClickHouse/data-agent-mnist](https://github.com/ClickHouse/data-agent-mnist), synced from the tree the board runs on, and since the version the first post linked:

* **Engine and timezone pin.** The board manifest records the query engine release and the session timezone, and a run on a different one is refused. A silent engine upgrade had flipped one question's ground truth, which is exactly the drift a repeatable benchmark exists to prevent.
* **Credential preflight.** Every provider that the candidates, the judges and the column linker will touch is checked before the first paid call, so a dead judge credential stops the run instead of degrading the scoring one question at a time.
* **Numeric tolerance as configuration.** The comparator no longer assumes money. Rounding and the tolerances are a scoring section in the model config, with the currency values as the default.
* **Linker fix for wide result sets.** When one answer's columns contain the other's, the shared columns map by identity with no model call. The fix is forward-only; the published board was not re-scored.
* **A judge model that carries uncertainty.** A many-facet Rasch model over the cached panel votes gives candidate ability, judge severity and an own-family coefficient with bootstrap intervals, offline from the results file.
* **Hooks for experiments.** A second corpus is one environment variable, so a development set can live beside the frozen board. Every runner takes a gate callback that can attach a note to a query result.
* **LibreChat runner.** A runner scores a LibreChat agent on the same questions, warehouse and panel as the direct loop: on the full board the product scored 69.7% against 66.2% for the direct loop on the same model, inside noise.

The contamination probe from the first post was run on all five new models. None of them recovers an anonymized entity name from a question prefix (0 of 25 each), and their completion similarity to our questions sits in the same low band as the rest of the board. Sonnet 5.5, the one model of the five with a Spider control, recovers 81% of entity names on Spider dev against 7% on our questions, which tells us the probe is sensitive to memorization where it exists.

## The board at 34 models {#the_board_at_34_models}

In the figure below, models are ranked by their pass rate at a 60-turn budget. The five new rows are in blue.

![](https://clickhouse.com/uploads/aab_followup_oct2026_image1_e63183b6fe.png)

*The board at a 60-turn budget, 34 models. Bright yellow marks the six rows in a statistical tie with the leader; on 201 questions the 95% interval is about ±6 to 7 points. Turns and SQL are per-question medians. TL is the number of questions a model never finished within the budget. Blue bars mark the five models added since the first post.*

The top of the board is unchanged from the first post. All five additions enter between ranks 9 and 15, and all five conclude on every question, which the TL column shows is not a given even for frontier models.

### The GPT-6 family

GPT-6 Astra, Luna and Sol ran through the same OpenAI-compatible path as the board's other OpenAI seats, at default reasoning effort. They span 68.7 to 69.7% with overlapping intervals, just below GPT-5.5 (70.4%) and above GPT-5.6 (67.7%). No GPT-6 variant leads its predecessor here. All three answered every question inside the budget, with the board's usual failure shape: wrong plan first, no runtime errors.

Default effort is a caveat. The first post showed on the Gemini line how much a budget-shaped knob moves a number, and GPT-6 supports an "xhigh" effort that no model on the board has been run with. Until that sweep runs, "GPT-6 at default effort" is the label for these rows.

### Claude Opus 5.5

Opus 5.5 enters at 69.7%, 2.0 points above Opus 5 and within noise of it, level with Kimi K2.6 and GPT-6 Sol. Like Opus 5 it concluded on every question, with a slightly shorter loop: a median of 4 turns and 6 queries against 5 and 7.

### Claude Sonnet 5.5

Sonnet 5.5 is the most interesting of the five: accuracy moves a little and everything else moves a lot.

**Accuracy.** 68.7% (138 of 201) against 62.2% for Sonnet 5. Paired on the same questions it wins 31 and loses 18, a net of 13 at p of about 0.09: directional, not significant. It ties GLM-5.2 and GPT-6 Astra, one point above Opus 5 and one below Opus 5.5.

**Where the gain is.** On the 83 questions that need the dimensional CRM layer (dbt_dds), Sonnet 5 scored 62.7% and Sonnet 5.5 scores 73.5%; on the rest, 61.9% against 65.3%. The gain is on the multi-hop questions, and not from finding the tables more often: both models discover the dimensional layer on about 89% of the questions that need it. It uses them better.

![](https://clickhouse.com/uploads/aab_followup_oct2026_image4_8e4a43abd1.png)

*Pass rate at 60 turns on the 83 dimensional (dbt_dds) questions against the 118 others, 34 models, with how often each model's SQL touched the dimensional layer at all. Every new row holds or gains on the dimensional questions except Opus 5.5, which is 2 points lower there than on the rest.*

**Efficiency.** This is where we see the biggest improvement. Sonnet 5 hit the 60-turn cap on 16 of 201 runs, so its pass rate sat 5 points below its rate on the runs it did conclude. Sonnet 5.5 hit the cap zero times, at a mean of 3.5 turns per question against 9.1, a median of 13.7 seconds per answer against 26, and $10.39 for the full run at list price against $14.40: about 5 cents a question against 7.

![](https://clickhouse.com/uploads/aab_followup_oct2026_image3_32cff4638e.png)

*Wall-clock per question, 34 models, ordered by the median (tick); the bar is the 90th percentile. GPT-6 Sol and Sonnet 5.5 are among the fastest rows on the board. Astra is the slowest of the new rows, with a median of 46 seconds and a 90th percentile past 90.*

**Failure shape.** Of Sonnet 5.5's 63 failures, 75% are wrong plan, 19% wrong data selection, 6% wrong implementation. There were no no-attempts and no runtime errors. Sonnet 5 had 5% no-attempt and 15% wrong implementation. Sonnet 5.5 always attempts and computes correctly more often; when it fails, it fails on the plan.

## The picture is the same, at a higher floor {#the_picture_is_the_same_at_a_higher_floor}

Two findings from the first post hold with five more models.

**Planning is still the main failure mode.** For every new model, wrong plan is the largest bucket and runtime errors are absent. SQL execution is solved for this class of model; what remains is deciding what to compute.

![](https://clickhouse.com/uploads/aab_followup_oct2026_image5_9fa26edd05.png)

*Share of each model's concluded failures by mode, 34 models, turn-limited runs excluded. Wrong plan is the largest share for every new row, from 51% (Astra) to 75% (Sonnet 5.5), and none of the five produced a runtime error. Astra stands out with 27% wrong data selection and 13% no attempt; Opus 5.5 and Sonnet 5.5 always make an attempt.*

**Price still spans a factor of eight inside the top group, and the mid-tier is closing.** On the first board the cheap seat in a family was the one that ran out of budget: Sonnet 5 hit the cap on 16 questions against zero for Opus 5, and Gemini 3.5 Flash on 28. Sonnet 5.5 breaks that pattern. It runs the whole board for about a fifth of what Opus 5 costs, with no truncated runs, and lands within one point of it.

![](https://clickhouse.com/uploads/aab_followup_oct2026_image2_3c5a6f9871.png)

*Mean list-price cost per question against pass rate, 30 models, log scale. Sonnet 5.5 sits just right of the cost frontier at about 5 cents per question. GPT-6 Astra, Luna, Sol and Opus 5.5 are left off: they ran through a gateway whose usage records do not split cached from uncached input reliably, so a list-price cost from them would be too low for GPT-6 and too high for Opus 5.5.*

We said last time that you have to run the benchmark yourself to pick a model. Five new frontier models later, that is still the advice: the top-line score barely moved, and the property that actually changed (turns, cost, truncation) is the one a leaderboard number hides.

## Run this on your own data warehouse {#run_this_on_your_own_data_warehouse}

Nothing here is specific to our warehouse or to ClickHouse. The harness is the same one the first post described: an instrumented assistant, a modeled warehouse schema, a curated and anonymized question set with committee ground truth, and a judge panel in which no model grades its own answers. Adding a model is a registry entry and one command, and the engine pin means a re-run reproduces the board.

Your warehouse will have its own discriminator. Ours is a dimensional CRM layer; yours might be a slowly changing dimension, a semi-structured event table, or a naming convention nobody wrote down. The only way to find it is to run the benchmark on your schema, with your questions, and look at where the models fail.

## What's next {#whats_next}

The reasoning-effort sweep for the GPT-6 family, so the three variants are compared at more than one effort level. The split-role architecture question from the first post (strongest model plans, cheapest model executes) is still the follow-up we are most interested in. A companion post on labeling failures and ranking tables follows this one.

## Code {#code}

* Harness: [github.com/ClickHouse/data-agent-mnist](https://github.com/ClickHouse/data-agent-mnist), Apache 2.0. The two worked examples under examples/ run from the published tree on three API keys.

---

## Get started today

Interested in seeing how ClickHouse works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-2748-get-started-today-sign-up&utm_blogctaid=2748)

---