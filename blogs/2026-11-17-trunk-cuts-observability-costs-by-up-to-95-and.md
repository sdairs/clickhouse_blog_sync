---
title: "Trunk cuts observability costs by up to 95% and reclaims 20 engineering hours a week with ClickHouse Observability"
date: "2026-11-18T15:03:59.204Z"
author: "ClickHouse"
category: "User stories"
excerpt: "Trunk cuts observability costs by up to 95%, reclaims 20 engineering hours a week, and accelerates flaky test detection with ClickHouse."
---

# Trunk cuts observability costs by up to 95% and reclaims 20 engineering hours a week with ClickHouse Observability

## Summary

- Trunk, a CI acceleration platform, uses ClickHouse Observability to analyze about 2 billion customer test results a day.
- Replacing Datadog with ClickHouse Observability cut costs by 15-20x while ingesting 100% of traffic instead of just 15%, and agents can now investigate incidents across application and observability data in one technology.
- Moving from self-managed TimescaleDB to ClickHouse Cloud cut flaky test detection from up to an hour to five minutes or less, with fewer service issues.

[Trunk](https://trunk.io/) is a CI acceleration platform that helps engineering teams ship code as fast as their engineers and agents write it. As co-founder and CTO Matt Matheson explains, the company was founded on the premise that the teams behind developer tooling are generally understaffed. 

“If you look at big players like Facebook and Google, they pour a lot of money into developer experience and developer productivity,” he says. “We wanted to build those same services and tools, democratize that, and bring it to companies that can’t afford to staff a team of 10 or 15 or 100, but still give them access to the same high-quality developer experience.”

That gap has only grown as coding agents have multiplied the number of pull requests teams open every day. Trunk tackles it as a unified platform built on a shared data layer. [Dynamic CI](https://trunk.io/dynamic-ci) uses it to skip the CI jobs a change doesn’t need. [Flaky Tests](https://trunk.io/flaky-tests) uses it to detect and quarantine unreliable tests automatically. [Merge Queue](https://trunk.io/merge-queue) uses it to test unrelated changes in parallel and keep main green. Teams like Brex, Ramp, and Zillow rely on it.

That shared data layer is the heart of the platform, and as Matt notes, getting it right took a few attempts. “Once we adopted ClickHouse Cloud and learned how to really marry it to the problems we were solving,” he says, “we saw a much better user experience, we saw our costs go down significantly, and our efforts to operate our own product went way down.”

We caught up with Matt and staff platform engineer Patrice Boisclair-Laberge to learn how replacing Datadog with self-managed ClickHouse Observability cut observability costs by 15-20x and moving from TimescaleDB to [ClickHouse Cloud](https://clickhouse.com/cloud) on AWS made flaky test detection faster and more reliable.

## From 15% of logs in Datadog to 100% in ClickHouse Observability {#from_15_of_logs_in_datadog_to_100_in_clickhouse_observability}

As Matt notes, observability matters more to Trunk than to most startups its size, since parts of its products are on the critical path. The merge queue gates every change to a customer’s repository. Flaky test quarantining keeps unreliable tests from blocking that work. 

“If those things go down, our customers lose the ability to do work,” he says. “Our ability to know that something is going down and prevent it or fix it before customers even realize is critical to maintaining those relationships. We don’t want to ever risk our reputation.”

Trunk’s previous observability setup was built around Datadog. By 2025, however, the cost had become unsustainable. “The shift to agents means that we need more data, more logs to be successful. We needed a new, cost-efficient solution to build our observability platform on.”

The team had already moved to ClickHouse for analytics, so when Patrice learned that ClickHouse had [acquired HyperDX](https://clickhouse.com/blog/clickhouse-acquires-hyperdx-the-future-of-open-source-observability), he decided to give it a try. HyperDX later became the UI for ClickStack, ClickHouse's open-source observability stack.

Trunk already collected metrics with OpenTelemetry, so the setup was straightforward. They installed ClickStack’s [OpenTelemetry collector](https://clickhouse.com/docs/clickstack/ingesting-data/collector) and just started uploading, using the ClickStack UI for dashboards and investigations. 

Near the end of their time on Datadog, Trunk sent it only 15% of traffic to manage costs. Today, 100% goes to ClickHouse Observability, and the team no longer samples logs. Everything at info level and higher is kept, about 375,000 log lines and 2.2 million traces per minute, with 30 days of retention. Patrice estimates ClickHouse Observability is 15-20x cheaper to run than Datadog.

> “On-call investigation in ClickHouse Observability now matches the speed it had on Datadog, but now with 100% of our logs. That was the gold standard of what we wanted to achieve and we’re very happy we achieved it.” — Patrice Boisclair-Laberge, Staff Platform Engineer, Trunk

## A unified platform for people and agent observability {#a_unified_platform_for_people_and_agent_observability}

For Matt, a key benefit is having traces, logs, and metrics under one roof. “More data in ClickHouse Observability means faster on-call response from humans and agents,” he says. “I can grab the traces that hit this endpoint, I can pull all the logs related to them, I can see if there’s temporal correlation on metrics there, and just put the whole story together in one place.”

Patrice says Trunk’s agents are great at investigating issues in ClickHouse Observability, and they’ve taken over dashboards too. “I don’t think we have a single human-made dashboard in the last six months. We all use the [ClickStack MCP](https://clickhouse.com/docs/clickstack/mcp) or the notebooks to generate them. You just tell your agent what you want, and it makes the dashboard. It’s fantastic.”

Agents are also doing more of the work on the application side. Trunk runs an internal incident bot that uses the MCP server to query its application tables, triggered automatically by incidents or manually to look into a customer’s usage. “Salespeople can more easily debug stuff and not escalate to engineers as often,” Patrice says. Matt agrees, adding, “Teams that don’t work on the product at all can just dispatch Claude Code to check out any customer issue.”

Because Trunk’s application data and observability data are both in ClickHouse, agents have fewer technologies to work across. 

> “I want people to learn the fewest technologies possible. That also applies to AI. It just means we need fewer MCPs. The AI models are really good at using ClickHouse for observability, especially with the ClickStack MCP, and investigating an outage often means pulling from both.” — Matt Matheson, co-founder and CTO, Trunk

Trunk evaluated other leading AI SRE tools, but found them unnecessary. “At the end of the day, ClickHouse Observability with the MCP plus Claude Code or Codex was as good,” Matt says. “There was no need to bring in a whole other vendor to respond to incidents and get things fixed.” By his estimate, AI-assisted triage with ClickStack gives back about half an engineer’s time, roughly 20 hours a week.

For Trunk, Matt says, leaning on agents for triage has become essential. “It’s absolutely mission-critical, our ability to function as a small team and still ship a lot of features, but also maintain a high-quality service. That’s just impossible without that always-on, AI-assisted triage, which is amazing with an off-the-shelf agent and just access to ClickHouse Observability.”

## Migrating analytics from TimescaleDB to ClickHouse Cloud {#migrating_analytics_from_timescaledb_to_clickhouse_cloud}

Before ClickHouse, Trunk stored customer test and CI data in TimescaleDB, a time-series extension for Postgres. In the beginning, the team used Timescale’s hosted service, but as Patrice says, “We faced a ton of performance issues.” 

They moved to self-managed bare metal servers running Postgres and TimescaleDB on local SSDs. Performance improved, but maintenance became a burden. “It took us a lot of custom work,” Matt says. “We were very much in the weeds of changing things in Timescale that we shouldn’t have to touch.”

Patrice recalls the team digging into Postgres functions and reimplementing some of them to better suit Trunk’s workload. By his estimate, Timescale took half of an engineer’s time each year across the company. All the processing around Timescale also slowed the product down, so detecting a flaky test could take up to an hour. “It was becoming unmanageable for us, I was constantly getting paged in the middle of the night,” he says.

When the team discovered ClickHouse, they first tried self-hosting it, and then quickly moved to fully managed [ClickHouse Cloud](https://clickhouse.com/cloud) once it could connect privately in Trunk’s region, which their data-heavy workload needed to avoid egress costs. 

Patrice, who had spent a year and a half running Postgres on bare metal, admits he had doubts about how well a SaaS database could perform. “But once we tested ClickHouse Cloud, it was very performant,” he says. “The proof was in the pudding.”

## Faster detection, new features, and lower costs {#faster_detection_new_features_and_lower_costs}

Trunk moved off TimescaleDB in stages. They first used [ClickPipes](https://clickhouse.com/cloud/clickpipes) to sync data from Postgres into ClickHouse, then switched to dual writes, and finally wrote only to ClickHouse and deleted the Timescale tables. A few Postgres tables still replicate over ClickPipes. The team leaned heavily on ClickHouse’s [documentation](https://clickhouse.com/docs/concepts/best-practices). “We learned a ton from that,” Patrice says.

Customers didn’t see the move itself, but they did notice flaky test detection dropping from up to an hour to five minutes at most. Because ClickHouse handles the data load, Matt explains, analysis jobs run faster and more often. “That was huge for customers, and the reliability went way up,” he says. “If we were to look at our own outages, the adoption of ClickHouse would be a huge marker, like a step function down in terms of issues for the service.”

“We did get positive feedback on the speed-up in detection,” he adds. “But this is an area where no news is good news. What really happened is we just heard less from our customers.”

Faster queries also unlocked new features like rollups and real-time views of CI usage. “There were a lot of features we wanted to implement that were impossible with TimescaleDB,” Patrice says. “They would be like two or three minute page loads, which is unacceptable. But then with ClickHouse, it’s a matter of seconds.” Behind the scenes, the team retired many of their legacy ETL pipelines, handling that work with [materialized views](https://clickhouse.com/docs/concepts/features/materialized-views) or computing it live.

For Matt, the payoff is in velocity. “We’re able to ship more features,” he says. “Originally, our thesis was ‘let’s find flaky tests.’ That was the tip of the spear. But once we got onto ClickHouse, it became so easy to do any other type of data analysis such as finding slow tests, new tests, and cluster analysis. All that stuff that was always on the roadmap, suddenly we were able to ship just very quickly.”

Trunk now processes almost 2 billion test results a day, with customer workloads 10-15x larger than what it handled on Postgres. “It’s scaled amazingly,” Patrice says. 

Database for database, Matt adds, Timescale may have cost less to operate, but Trunk ran “so much compute to do data processing that is almost free in ClickHouse, or way cheaper.” Factor in the engineering time Timescale took to maintain, he says, and “if we were to add it up, ClickHouse would end up being much cheaper.”

## Moving fast on ClickHouse Cloud {#moving_fast_on_clickhouse_cloud}

Two migrations in, Trunk plans to keep building on ClickHouse. “ClickHouse scales so well, we want to put everything in ClickHouse,” Matt says. Next up is sending every PagerDuty page straight to an agent that reads ClickHouse Observability first. “The context and the leg up the first time a human looks at it is invaluable, and it happens so fast that it should always happen.” Patrice notes that ClickHouse’s continuous innovation gives Trunk confidence in the technology and partnership. For example, they’ve been invited to ClickHouse’s [PromQL private preview](https://clickhouse.com/blog/introducing-promql) and plan to try it.

Patrice takes a moment to shout out the support they’ve received from ClickHouse. “The team is extremely responsive,” he says. “Also, we’ve barely had to talk to them, which is great.” 

For Matt, access to ClickHouse’s product teams has been equally valuable. “Being able to give feedback on things we use and hear about what’s coming up has been really valuable,” he says. “It’s a good way to get exposure to the roadmap and have our voice heard.”

Asked to sum up the team’s experience with ClickHouse for observability and real-time analytics so far, Patrice keeps it short and sweet. “It allows us to move fast, and we love that.”

---

## Get started today

Interested in seeing how ClickHouse works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-3070-get-started-today-sign-up&utm_blogctaid=3070)

---