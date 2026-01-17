---
title: "How Blacksmith paired Postgres and ClickHouse for fast CI and real-time observability"
date: "2025-07-29T12:50:25.401Z"
author: "ClickHouse Team"
category: "Community"
excerpt: "What happens when you combine Postgres, ClickHouse Cloud, and real-time ingestion via the Postgres CDC connector in ClickPipes?"
---

# How Blacksmith paired Postgres and ClickHouse for fast CI and real-time observability

Slow CI pipelines can disrupt an entire team’s rhythm. When builds drag on or fail without explanation, developers lose momentum and delays pile up. GitHub Actions has become the default choice for many teams, but it wasn’t built with speed or observability in mind. That leaves developers scratching their heads when things go wrong.

[Blacksmith](http://blacksmith.sh) is on a mission to change that. Founded in 2024, the company now runs CI for more than 600 organizations and handles over 9 million jobs per month. Its drop-in replacement for GitHub Actions radically improves build times and gives teams the tools to see inside their pipelines. With features like step-by-step visibility, caching insights, and global log search, Blacksmith helps developers understand why a job failed, which steps are slowing things down, and how to fix issues before they hit production.

“We offer a lot of observability features that go beyond what GitHub offers,” says Gabe Guerra, Blacksmith’s Head of Growth. “That requires us to store a lot of data and give users a way to query it and ask questions about their CI logs or VM metrics, very quickly.”

Today, Blacksmith queries terabytes of observability data through [ClickHouse Cloud](https://clickhouse.com/cloud). At our [2025 Open House user conference](https://clickhouse.com/openhouse), ClickHouse Director of Product Management Sai Srirampur [sat down with Gabe](https://clickhouse.com/openhouse#video-blacksmith) to talk about how Blacksmith came to adopt ClickHouse, why the Postgres CDC connector has been so valuable to their workflow, and which recent features (e.g. Ask AI, MCP) have stood out the most.

<iframe width="768" height="432" src="https://www.youtube.com/embed/dSwT5sP1Ryw?si=KS6w-vj7QZn1mtMf" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

## The new data standard for modern companies

Like many startups, Blacksmith began by storing its operational metadata in Postgres. It was a natural choice for transactional data—reliable, well-understood, and easy to integrate with the rest of their stack. But as the team began building more advanced observability and analytics features, they ran into limitations.

“We collect a lot of metadata, which we use not just for observability, but for go-to-market and understanding user behavior as well,” Gabe says. “Postgres just isn’t built for the kinds of analytical queries we want to run. It's quite slow.”

At first, they tried a managed wrapper around the open-source version of ClickHouse to speed things up. But as Gabe explains, the experience wasn’t ideal. “We had difficulties with local testing and local development,” he says. Eventually, they adopted [ClickHouse Cloud](https://clickhouse.com/cloud) for better performance, a smoother developer experience, and greater scalability.

A key part of that setup is [ClickPipes](https://clickhouse.com/cloud/clickpipes), ClickHouse’s native ingestion service. Blacksmith uses ClickPipes to connect their Postgres instance directly to ClickHouse Cloud via the [Postgres CDC connector](https://clickhouse.com/cloud/clickpipes/postgres-cdc-connector). This lets them stream changes in real time without the need for complex ETL tooling. Any relevant metadata—user actions, build history, performance stats—can be analyzed almost instantly, without touching the application layer.

“The CDC connector is great because we can just push that data into ClickHouse and start playing around with it,” Gabe says.

It’s a clean and effective architecture that’s becoming the default data stack for modern companies looking to bring real-time visibility to their operations. Postgres remains the system of record for Blacksmith’s transactional data, while ClickHouse powers fast, flexible analytics for its engineering and go-to-market teams.

## A better developer experience with ClickHouse

Gabe also highlighted some of his favorite new features in ClickHouse Cloud. The first is [Ask AI](https://clickhouse.com/ai), an embedded assistant that lets users describe what they’re looking for in plain English and generates SQL queries based on their schema, saved queries, and active workspace context. It’s designed to help folks like Gabe get from questions to insights faster, without needing to navigate dashboards or remember query syntax.

“SQL is one of those things where you always forget the syntax—some of these SQL queries can get kind of crazy,” he says. “It’s nice to be able to ask the question in English, have it understand your table schema, and get something useful back and adjust from there.”

Ask AI is part of a broader push to make ClickHouse more accessible not just to engineers, but to AI-powered agents and tools as well. The recently launched [ClickHouse MCP (Model Context Protocol) server](https://clickhouse.com/blog/integrating-clickhouse-mcp) provides a secure, structured interface that allows LLMs and external agents to inspect schemas and run scoped, read-only queries. For ClickHouse Cloud users, it lays the foundation for more intelligent, agent-driven workflows in the future.

ClickHouse’s embedded dashboards are another reason Gabe keeps coming back. “I really like the interfaces to create graphs after you generate the data,” he says. While his team also uses Retool to create dashboards, he often finds ClickHouse easier to work with. “I tend to build it in ClickHouse, and then export the query to Retool,” he says. “It’s been seamless, going from asking a question to visualizing data.”

## The future of CI runs on ClickHouse Cloud

As Blacksmith grows, ClickHouse has become an important part of their workflow, powering fast, flexible analytics across their modern Postgres-plus-ClickHouse stack. With real-time ingestion through the Postgres CDC connector and new features like Ask AI, ClickHouse Cloud gives the team what they need to move fast and stay focused on serving customers.

For teams trying to speed up CI without overhauling their workflows, Gabe has a simple message: “If you're suffering from slow CI and you're using GitHub Actions, try [Blacksmith](http://Blacksmith). You don't have to take my word for it. It’s literally a one-line change. In 30 seconds, you can test it out for yourself and benchmark the difference.”