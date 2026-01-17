---
title: "Singapore Meetup Report: How ClickHouse Powers Ahrefs, the World's Most Active Web Crawler"
date: "2023-10-19T09:36:39.440Z"
author: "Elissa Weve"
category: "Community"
excerpt: "Learn how Ahrefs is able to handle trillions of rows efficiently with ClickHouse, their innovative solutions for data insertion, and their collaborative contributions to the broader ClickHouse community."
---

# Singapore Meetup Report: How ClickHouse Powers Ahrefs, the World's Most Active Web Crawler

![Ahrefs_photo.png](https://clickhouse.com/uploads/Ahrefs_photo_85bd1c256b.png)

On July 27th, 2023, Alibaba Cloud hosted the ClickHouse community meetup in Singapore. We had the pleasure of hearing from Yasunari (Yasu) Watanabe from Ahrefs, who shared their journey with ClickHouse on a massive scale.

Founded in 2010, [Ahrefs](https://ahrefs.com/) is renowned for processing immense volumes of web analytics data to provide valuable SEO metrics. They have the most active crawler in the industry, with the world’s largest index of live backlinks.

![Ahrefs1.png](https://clickhouse.com/uploads/Ahrefs1_7df5bcab84.png)

## Early Data Storage Solutions ##
Yasu shared Ahrefs' journey over the years working with various data storage solutions. 
“We tried all the available solutions out there, including Cassandra and Hypertable, but none of them really met our requirements. So we ended up developing a custom solution that was optimized for crawling the web with limited resources,” Yasu explained.

As part of their own customer storage solution for the web crawler, they used the Quantcast File System (QFS), alongside Elasticsearch for other non-crawler tasks. While this combination served them well for some time, it soon revealed its limitations due to an inflexible query engine, the absence of advanced features, and scaling challenges. Yasu shared, “Times change, feature requirements become more complex, the size of the web is growing and our infrastructure keeps on scaling up, so we went looking for some alternative solutions”.

## Migration to ClickHouse ##
In 2019, Ahrefs discovered ClickHouse. They were initially drawn to the ClickHouse architecture which resembled their custom system. ClickHouse offered superior performance, a SQL interface, versatile I/O support, and a column-oriented approach. This made querying highly efficient for their growing datasets.

Currently, Ahrefs has embedded ClickHouse deeply into their system. They operate multiple ClickHouse clusters on their hardware, with the main cluster being geo-replicated for both redundancy and task-specific efficiency. Yasu shared the massive scale at which they operate, “We have multiple clusters deployed on our hardware with hundreds of hosts. Our main cluster is now geo-replicated, and we designate some replicas for read-heavy operations and others for write-heavy operations. Many of our tables are quite large, with trillions and trillions of rows, as well as tens of columns.”

![Ahrefs2.png](https://clickhouse.com/uploads/Ahrefs2_99b947590b.png)

## Advanced Interactions with ClickHouse ##
Yasu revealed Ahrefs' strategies for advanced interaction with ClickHouse. To handle their large scale data insertions, Ahrefs uses a buffering technique, grouping data for fewer insert operations, which reduces subsequent merging tasks. Yasu explained "We also use extensive use of fetch and [attach commands to move parts efficiently](https://clickhouse.com/docs/en/sql-reference/statements/alter/partition) across different servers. This one, it's a really, really nice feature that’s handled by ClickHouse." 

![Ahrefs3.png](https://clickhouse.com/uploads/Ahrefs3_6b163950fe.png)

## Internal Monitoring Tools ##
Ahrefs developed tools including the "Birdseye View Tool" for a complete overview of ClickHouse clusters and the "Query Analyzer" to understand and optimize query performance. Yasu hinted at the possibility of these tools being open-sourced, which would be a great contribution to the broader tech community.

![Ahrefs4.png](https://clickhouse.com/uploads/Ahrefs4_e71ac490b3.png)
![Ahrefs5.png](https://clickhouse.com/uploads/Ahrefs5_1a1adb6654.png)

## Mark Compression: Ahrefs' Contribution to ClickHouse ##
Discussing an upstream patch Ahrefs proposed to ClickHouse, Yasu explained the issue with marks, which help locate rows in compressed data files. Large-scale queries can strain the cache of these marks, affecting performance. Ahrefs' solution involved compressing these marks for efficiency. After using their solution for a year, Ahrefs discussed its potential with the ClickHouse team. The final accepted solution divided marks into blocks with a custom compression scheme, which eliminated the need for mutexes, reducing memory consumption by three to six times. 

![Ahrefs6.png](https://clickhouse.com/uploads/Ahrefs6_6f39c3d04f.png)

## Summary ##
Ahrefs' switch to ClickHouse has brought significant improvements in data handling and performance. This transition has allowed them to manage massive data volumes more efficiently. Their innovations, like the mark compression solution, have enhanced query performance, saving memory and time. Yasu concluded “I would say that our decision to start using CickHouse in Ahrefs is not without its hurdles, but, overall it's been a great success. We're happy with the performance that is able to keep up with our usage demands. And we really appreciate the active feature development and bug fixes that go on in the regular monthly releases.”

Ahrefs continues to work on new features, promising further advancements in their collaboration with ClickHouse. 

## More Details ##
- This talk was given at the [ClickHouse Community Meetup](https://www.meetup.com/clickhouse-singapore-meetup-group/events/294428050/) in Singapore on July 27th, 2023
- The presentation materials are available [on GitHub](https://github.com/ClickHouse/clickhouse-presentations/tree/master/meetup80)
