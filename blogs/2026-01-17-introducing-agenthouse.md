---
title: "Introducing AgentHouse"
date: "2025-04-22T10:07:19.805Z"
author: "Dmitry Pavlov"
category: "Engineering"
excerpt: "Meet AgentHouse - an interactive public demo that combines ClickHouse's real-time analytics with Anthropic's LLM via the MCP server, built to showcase how anyone can talk to data using natural language."
---

# Introducing AgentHouse

![Blog_IntroducingAgentHouse_202504_FNL.png](https://clickhouse.com/uploads/Blog_Introducing_Agent_House_202504_FNL_0639a4c186.png)

## Introducing AgentHouse

A few weeks after Anthropic released its[ MCP protocol](https://docs.anthropic.com/en/docs/agents-and-tools/mcp) in 2024, the ClickHouse integrations team showed a small internal demo of Anthropic’s Sonnet model accessing a ClickHouse database. It was a very basic integration involving running a simple query against random data and getting a result to the LLM.

As an internal DWH team lead at ClickHouse, once I saw the demo, I immediately wanted to have this in[ my Data Warehouse](https://clickhouse.com/blog/building-a-data-warehouse-with-clickhouse). I want my lovely internal users (sales, ops, product, finance, and engineering teams at ClickHouse) to be able to talk to the data instead of using the traditional BI tool or running queries.

Two months later, we launched Dwaine (Data Warehouse AI Natural Expert) - an internal LLM that helps internal users answer their questions based on data. What is our revenue? What is this customer doing? What problems do our customers face right now? How many visitors do we have on our website, and what is our conversion rate? Dwaine dramatically helped our internal users to get those and other insights. You may have seen my[ small personal article in LinkedIn](https://www.linkedin.com/pulse/bi-dead-change-my-mind-dmitry-pavlov-2otae).

After I described this experience, many people reached out to me and asked for a demo. I demonstrated Dwaine to a few friends and partners, but though they were super excited, I felt they could not experience its full potential as they could not talk to Dwaine by themselves because it worked with confidential information.

This is how AgentHouse, available at [llm.clickhouse.com](https://llm.clickhouse.com), was built. But let him introduce himself :) All further text is written by the AgentHouse LLM.

## Hi, I’m AgentHouse!

I'm [AgentHouse](https://llm.clickhouse.com) - a fully interactive demo environment that showcases the powerful combination of ClickHouse's real-time analytics capabilities with large language models. My name combines "Agent" (representing the LLM agent) and "House" (from ClickHouse), highlighting how these technologies work together seamlessly. Together with other demo environments ([ClickHouse SQL Playground](http://sql.clickhouse.com) and [ADSB visualizer](https://adsb.exposed/)), I allow you to try the ClickHouse Cloud database in different real-world scenarios without creating an account or uploading any data.

<img preview="/uploads/agent_house_v3_7e163b96ca.gif"  src="/uploads/agent_house_high_res_1518b84bbd.gif" alt="agenthouse.gif" class="h-auto w-auto max-w-full"  style="width: 100%;">

:::global-blog-cta:::

## What am I made of?

These are my main body parts:

1. **[Anthropic’s large language model Claude Sonnet](https://www.anthropic.com/claude/sonnet)** - this LLM is especially good at understanding complex contexts and reasoning about structured data – making it an ideal partner for ClickHouse's analytical prowess. The model's ability to understand database schemas, generate accurate SQL, and interpret query results demonstrates why ClickHouse and advanced LLMs are natural companions.

2. **[LibreChat UI project](https://www.librechat.ai)** - an open-source LLM UI that helps you work with popular LLMs out of the box. We selected LibreChat as the user interface because of its open-source nature, clean design, and growing community support. We would also like to thank the LibreСhat team for their assistance when building this demo.

3. My secret sauce is the **[ClickHouse MCP](https://github.com/ClickHouse/mcp-clickhouse)** (Model Context Protocol) server that the ClickHouse team developed. This specialized server acts as the bridge between ClickHouse databases and large language models, enabling:

* Efficient data transfer between ClickHouse and LLMs
* Intelligent query optimization for LLM-generated SQL
* Context management for stateful conversations about data
* Secure and controlled access to database resources
* Streamlined handling of various public datasets

4. **[ClickHouse Cloud database](https://clickhouse.com)** - a fully-managed cloud service that provides the ClickHouse database as a Software-as-a-Service (SaaS) offering. 

![Images_PoweringAIAgentsAnalytics_202504_FNL(1).png](https://clickhouse.com/uploads/Images_Powering_AI_Agents_Analytics_202504_FNL_1_54be5a6747.png)

## Why Sonnet and LibreChat?

Anthropic's Sonnet model represents a significant advancement in LLM capabilities, particularly in understanding complex contexts and reasoning about structured data – making it an ideal partner for ClickHouse's analytical prowess. The model's ability to understand database schemas, generate accurate SQL and interpret query results demonstrates why ClickHouse and advanced LLMs are natural companions.

I use LibreChat as the user interface because of its open-source nature, clean design, and growing community support. The interface allows users to have natural conversations about their data and to build visual artifacts (charts, tables, etc),  making complex analytical tasks accessible even to those without SQL knowledge.

## My purpose

<p>
I was created specifically as a testing ground for users to delve &#x1F609; into how ClickHouse, through our MCP server, can serve as an ideal backend for LLM applications. I have access to multiple public datasets that showcase various use cases, allowing you to explore the possibilities through a simple conversational interface. This includes 37 different datasets, including:
</p>

* **github** - Contains GitHub activity data, repositories, and user interactions. Updated hourly.
* **pypi** - a row for every Python package downloaded with `pip`, updated daily - over 1.3 trillion rows
* **rubygems** - a row for every gem installed - updated hourly - over 180 billion rows 
* **hackernews** - Contains posts and comments from Hacker News
* **imdb**- Contains movie database information from IMDB
* **nyc_taxi** - Contains NYC taxi trip data
* **opensky** - Contains aviation data from the OpenSky Network
* **reddit** - Contains posts and comments from Reddit
* **stackoverflow** - Contains questions and answers from Stack Overflow
* **uk** - contains a comprehensive collection of UK property transaction data and related geographical information

And others.

## My key features

* Test Natural Language Queries: See how plain English questions transform into optimized SQL queries for ClickHouse via the MCP server
* Experience Real-Time Analytics: Witness how our MCP server enables ClickHouse's renowned speed to be combined with AI-powered insights with minimal latency
* Try Interactive Data Exploration: Explore demo datasets through a conversational interface powered by the MCP-LLM connection
* View Automated Visualizations: See how data flowing through our MCP server can be automatically visualized

## Exploring the Demo

To start with AgentHouse, go to  [llm.clickhouse.com](https://llm.clickhouse.com), and log into the demo environment with your Google account and start asking questions. A great way to start is to ask "Which datasets do you have?" - this will give you a list of databases and you can start exploring them.

I look forward to answering all your questions!

