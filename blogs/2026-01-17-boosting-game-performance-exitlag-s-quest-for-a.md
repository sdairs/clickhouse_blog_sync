---
title: "Boosting Game Performance: ExitLag's Quest for a Better Data Management System"
date: "2023-06-26T12:02:12.263Z"
author: "Elissa Weve"
category: "User stories"
excerpt: "Discover how Exitlag is revolutionizing online gaming, eliminating lag, and enhancing routing for over 1,700 games worldwide with the power of ClickHouse."
---

# Boosting Game Performance: ExitLag's Quest for a Better Data Management System

Imagine playing your favorite online game with almost no lag, enjoying smooth gameplay, and experiencing improved routing that reduces ping and ends packet loss. This is the kind of elevated gaming experience that [ExitLag](http://www.exitlag.com) is bringing to gamers worldwide.

ExitLag is a tool that optimizes the gaming experience for over 1,700 games on over 900 servers worldwide and provides a faster, less crowded connection, thus minimizing lag, enhancing game routes, and ending packet loss. In their continuous effort to resolve common connection problems for gamers, ExitLag faced performance issues with MySQL. They encountered bottlenecks and slowdowns with specific analytical queries about user behavior analysis and network route mapping, especially as their data volume increased.

In order to provide a better gaming experience, ExitLag has developed a sophisticated method for sending connection packets from users. These packets are sent simultaneously through different routes, thus increasing the guarantee that the packet will be delivered. Information such as region, IP, date, and connection type is used to decide the best route.

[Datacosmos Consultoria](https://www.datacosmos.com.br/), a leading IT consultancy based in Brazil, specializing in database and cloud services, has been instrumental in helping ExitLag take their customer experience to the next level with ClickHouse. 

![Exitlag_dashboard.png](https://clickhouse.com/uploads/Exitlag_dashboard_a2f4db9e3e.png)

## From MySQL to ClickHouse 
Datacosmos helped ExitLag transition from MySQL to ClickHouse, which they chose for its exceptional performance, scalability, and efficient data compression capabilities. ClickHouse offers a significant advantage over MySQL when it comes to the performance of analytical queries. In the past, even if a server had resources comparable to or better than those used in ClickHouse, it was still impossible to analyze certain data with the same level of efficiency. With ClickHouse, ExitLag could quickly process billions of lines of data in a short time, catering to their need for speed and scale.

ExitLag processes approximately 6 million daily events, using ClickHouse to analyze user behavior on their service and map possible network routes. These valuable insights into user behavior, game preferences, session durations, and network performance have not only provided gamers with optimized routes and an enhanced gaming experience but also improved ExitLag's ability to handle data at scale.

![Exitlag_architecture.png](https://clickhouse.com/uploads/Exitlag_architecture_f36c38c856.png)

## ClickHouse Advantages
ClickHouse's materialized views have been another game-changer for ExitLag. By precomputing and storing results of complex queries, materialized views provide faster access to aggregated data, reducing the need for repetitive computations. This feature, coupled with ClickHouse's scalability, has allowed ExitLag to efficiently handle an increasing data volume and provide swift responses to analytical queries. Visualization tools such as Grafana and Power BI, as well as ad-hoc queries, are used to analyze and present this aggregate data.

The transition to ClickHouse has resulted in significant cost savings. ClickHouse's efficient data compression allows for managing vast volumes of data with lower disk consumption, resulting in reduced infrastructure costs. Additionally, faster data analysis with ClickHouse has optimized resource utilization, further driving down operational costs.

As Leandro Sandmann, Co-Founder and Executive Board Member at Exitlag, states, “My experience with ClickHouse adoption has been revolutionary. By implementing this innovative technology, I have witnessed a significant jump in the productivity of my business. The benefits were immediate, with faster data processing and accurate analytics that allowed me to make strategic decisions with confidence. ClickHouse opened new horizons for the growth and success of my company, raising our executive vision to levels never reached before.”

## Future Plans with ClickHouse
Moving forward, ExitLag plans to leverage ClickHouse's analytical and machine learning capabilities. They aim to deepen their understanding of user behavior, network performance, and game preferences to continually improve their services. They also plan to explore ClickHouse's advanced features such as data replication and real-time analytics and predictions.

ExitLag's journey in embracing ClickHouse, with the help of Datacosmos Consultoria, has not only solved their data management challenges but also redefined their ability to provide a superior gaming experience. The transition from MySQL to ClickHouse has showcased the importance of finding a solution that aligns with a company's specific needs, while also being scalable and cost-effective.

As Rodrigo Salviatto, Director of Datacosmos explains, "If the goal is to analyze a large amount of data, in the order of billions of lines, in a time reduced to a minimum, the most appropriate choice is ClickHouse."

## Learn More

Visit: [www.exitlag.com](www.exitlag.com)

Visit: [www.datacosmos.com.br](https://www.datacosmos.com.br/)

