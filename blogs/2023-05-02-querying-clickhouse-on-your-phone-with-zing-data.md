---
title: "Querying ClickHouse on your Phone with Zing Data & ChatGPT"
date: "2023-05-02T08:48:50.755Z"
author: "Zach Hendlin, Co-founder & CEO of Zing Data"
category: "User stories"
excerpt: "Read about how Zing data allows users to query ClickHouse from their phone using natural language queries powered by OpenAI's ChatGPT"
---

# Querying ClickHouse on your Phone with Zing Data & ChatGPT


<iframe width="768" height="432" src="https://www.youtube.com/embed/R04i98GAR-o" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>

ClickHouse is used by companies to power fast queries. But for many companies, the challenge of having an analyst write a query, create a dashboard, and share that throughout the organization adds substantial lag to getting questions answered – even if the database is fast. 

Zing Data is a modern data analysis and business intelligence platform, built to work on any device you have - iOS, Android, and the web. Even from mobile, Zing’s new ClickHouse support means you can: 

* Query with natural language querying (powered by OpenAI’s ChatGPT)

* Visually query in just a few taps – even from raw tables and views

* Set up real-time alerts (push or email) to get notified when data changes

* Query based on your phone’s current location

Zing’s AI-powered query optimization helps suggest date handling (like casting timestamps to dates), graph types, and even handles long running queries – simply sending you a notification when results are ready and showing sampled previews for large result sets.

## Mobile Querying and Visualization

Zing Data's [mobile app provides a powerful yet simple interface for querying and visualizing ClickHouse data on the go](https://docs.getzingdata.com/docs/asking-questions/). Unlike other BI tools which require somebody at a computer to pre-create dashboards or limit you to certain filters, Zing lets you ask _any question of your raw data from iOS, Android, and the Web._

The app supports a wide range of visualizations, including line charts, bar charts, data tables, maps, and more. Calculated fields, a SQL typeahead, and joins empower you to do more complex data operations.

For long running queries, Zing’s server persists a connection to ClickHouse to complete the query in the background, and sends you a push notification when the results are ready.

## Enabling OpenAI Queries on ClickHouse Data

Zing Data's ClickHouse integration allows you to leverage the power of OpenAI to ask complex questions and receive meaningful answers fast. Ask questions in a conversational style without worrying about syntax or debugging SQL – and Zing supports asking natural language questions in an array of languages including English, Spanish, French, German, and Japanese (among others).

Zing’s query intelligence layer takes the SQL for your natural language query and applies visualization logic - ensuring aggregations are on the y-axis, dates/times are on x-axis, and multiple group bys show up as stacked series.

<div style="display:flex; justify-content: center;">
<img src="/uploads/zing_with_open_ai_c30c3e592b.jpg" alt="zing_with_open_ai.jpg" class="w-auto max-w-full h-auto" style="width:350px">
</div>

## Real-Time Alerts 

Zing Data's [real-time alerts functionality](https://docs.getzingdata.com/docs/alerts/) allows users to set up push notifications or emails that trigger when certain conditions are met in a query on ClickHouse data. This enables users to monitor their data in real-time and take action when important trends or anomalies are detected without having to constantly check dashboards.

Users can create alerts based on a wide range of conditions, such as when sales exceed a certain threshold, when inventory levels drop below a certain level, or when customer churn rates increase beyond a certain level. Alert conditions can be checked as frequently as every minute, or as infrequently as every month.

Zing Data's real-time alerts are highly customizable - for example you can set up multiple alerts for different conditions or datasets and each user can have their own individual alert settings.

<div style="display:flex; justify-content: center;">
<img src="/uploads/zing_alerts_5f600e693d.jpg" alt="zing_alerts.jpg" class="w-auto max-w-full h-auto" style="width:350px">
</div>

## Location-Based Questions

For any tables with latitude and longitude fields, [Zing can query and display results based on your phone’s current location](https://docs.getzingdata.com/docs/location-based-querying/). For instance, a maintenance worker could see all the high priority jobs that are beyond their SLA within 10 miles of their current location to go take action. Or a store manager could see which nearby warehouses are stock of a critical product. 

This location can be dynamic to each user’s device, so somebody in Tampa will see results within 10 miles of their location, while another user accessing the same question will see results within 10 miles of, say, San Francisco.

<div style="display:flex; justify-content: center;">
<img src="/uploads/zing_locations_621093cd2e.gif" alt="zing_locations.gif" class="w-auto max-w-full h-auto" >
</div>

## Getting Started

Zing Data's ClickHouse integration is a powerful tool that enables users to query and visualize ClickHouse data on mobile devices web, run advanced OpenAI queries on ClickHouse data, and set up real-time alerts on top of ClickHouse data. 

Whether you're a data analyst, a business user, or a developer, Zing Data's ClickHouse integration can help you unlock valuable insights from your data and make better decisions in real-time. 

Both Zing Data and ClickHouse have generous free tiers and are affordable at scale. A [step-by-step setup guide to getting started is here](https://docs.getzingdata.com/docs/setting-up-a-data-source/clickhouse_setup/).


