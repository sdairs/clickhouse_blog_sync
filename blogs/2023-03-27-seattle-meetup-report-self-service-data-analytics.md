---
title: "Seattle Meetup Report: Self-Service Data Analytics for Microsoft’s Biggest Web Properties with ClickHouse "
date: "2023-03-27T10:40:27.111Z"
author: "ClickHouse Editor"
category: "Community"
excerpt: "On January 18th, 2023 Microsoft hosted a ClickHouse community meetup where the WebXT team presented two of their analytics products using ClickHouse: Titan and Microsoft Clarity. The team shared how they are able to analyze petabytes of data in seconds an"
---

# Seattle Meetup Report: Self-Service Data Analytics for Microsoft’s Biggest Web Properties with ClickHouse 

<iframe width="764" height="430" src="https://www.youtube.com/embed/r1ZqjU8ZbNs" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>

<br/>

On January 18th, 2023 Microsoft hosted a ClickHouse community meetup where the WebXT team presented two of their analytics products using ClickHouse: Titan and Microsoft Clarity. The team shared how they are able to analyze petabytes of data in seconds and create custom dashboards with just a few clicks. 

Satish Manivannan, Senior Director of Data and Analytics, introduced the products and discussed the vision of Titan, which aims to provide self-service analytics to thousands of employees across Microsoft. 

## Titan: Self-Service Analytics Tool for Microsoft
WebXT is home to some of the biggest web properties for Microsoft, including Edge Browser, Bing search, MSN, Microsoft Advertising, Maps and more. These web properties generate petabytes of data, and analytics is crucial for its success. 

The WebXT team developed Titan, an internal data analytics tool which enables self-serve interactive data analysis in an efficient and flexible manner. Titan has been in development for two and a half years and is used by over 2,500 people on a monthly basis, receiving over 100,000 queries daily. 

The team chose ClickHouse to power their analytics solution, combined with Apache Superset as the data visualization tool. Both ClickHouse and Superset are open source technologies and Manivannan explained how they see this is a competitive advantage. “We not only contribute to Microsoft technology, we are very much embracing the open source community, so that we can best compete with our fierce competitors. Of course that's where I think we struck gold with ClickHouse among other solutions”, said Manivannan.

Historically the team had been using a combination of in-house and third party analytics tools. Switching to ClickHouse saves the team millions of dollars in license fees.  “We had Adobe Analytics, and we also had Interana, which is called Scuba.” Manivannan explained that the tools worked well however their demands continued to increase. “We needed something we could build in-house, so that we could innovate faster and keep up with the innovation that the team is doing.”

![image 1.png](https://clickhouse.com/uploads/image_1_968291e4d8.png)
_Titan provides interactive analytics to thousands of Microsoft employees, replacing 3rd party tools such as Adobe Analytics, saving millions of dollars._

## High-Level Requirements for Titan
The key goal for Titan was to provide self-service analytics with response times within seconds. This would allow people to interactively slice and dice data and save it as dashboards. The tool needed to also allow for the customization of metrics, filters, and columns. Advanced analytics such as user analytics, cohort analysis, A/B testing and flexible data retention were also important requirements. Manivannan discussed the challenges of freeform analysis of queries and emphasized the need for scalable, performant, and highly available infrastructure.

![Microsoft Titan image 2.png](https://clickhouse.com/uploads/image_2_f073986f73.png)
_ClickHouse was chosen for Titan as it met all of the high level requirements._

Manivannan explained that ClickHouse was an excellent choice for many of these requirements because of its speed and cost-effectiveness. “ClickHouse fits a lot of these boxes. Definitely it is fast. We also did some custom optimization. So our main tagline is, faster and cheaper … ClickHouse plays a big part and meets a lot of our diverse set of data needs.”


He also highlighted the inbuilt telemetry in ClickHouse, which makes monitoring data usage and storage more accessible.

![Microsoft Titan image 3.png](https://clickhouse.com/uploads/image_3_bb933869cc.png)
_Titan platform includes thousands of dashboards for tracking KPIs, custom issue builds, user analytics features, and A/B testing capabilities._

## ClickHouse as the Data Engine for Titan
Lin Tang, Principal Software Engineering Manager on the WebXT Team presented the high-level overview of the Titan architecture, which consists of a data source engine, API, and interactive visualization powered by Superset. The data source engine has three main inputs: Cosmos, Azure, and real-time streaming scenarios.

Bing, which has a lot of diverse and expensive queries, has clusters with hundreds of machines set up to support query requirements. ClickHouse is used as the data engine, and they have multiple clusters set up, with ZooKeeper used for ClickHouse cluster management.

![Microsoft Titan image 4.png](https://clickhouse.com/uploads/Microsoft_Titan_image_4_8e9ae8f7a0.png)
_Titan architecture which consists of a data source engine, API, and interactive visualization powered by Superset._

The API was built to provide authentication and to avoid flooding the backend database with requests. They also query Microsoft internal APIs to get information on experimentation scenarios. To avoid sending every query to the backend database, caching has been implemented, pre-caching data during low load times and showing data right away on custom dashboards.

Tang then discussed how they customized Superset with query builders and visualizations, including a sampling feature that allowed users to switch easily between sampled and raw data. 

## Optimization Techniques for ClickHouse
The talk also covered optimization around ClickHouse, including a near real-time pipeline to collect signals from their production service and a query optimizer built-in to improve query performance. The Joiner Optimizer was implemented to address the challenge of big data joins, resulting in a 10x query improvement. The condition optimizer pre-selected the condition by doing a "where" first, reducing the data size and improving processing time. The time zone optimizer selected the data range first and then applied the timestamp, leading to a good improvement in query performance.

![Microsoft Titan image 5.png](https://clickhouse.com/uploads/Microsoft_Titan_image_5_14cd6743c6.png)
_Near real-time data pipeline for Titan using ClickHouse._

Storage efficiency was also discussed, with the need to optimize storage to improve performance. Tang explained that Titan uses role-based return and deletion to keep track of the data that needs to be deleted, ensuring efficient deletion without impacting system performance. ClickHouse's rich encoding options were also discussed, with ZSTD found to provide a 50% savings for some tables despite slower query performance.

The ClickHouse community meetup at Microsoft provided insights into the successful implementation of Titan and Microsoft Clarity, both based on ClickHouse. The event highlighted the importance of data in the success of Microsoft and demonstrated how self-serve analytics provides value to the organization.

## More Details
- This talk was given at the [ClickHouse Community Meetup](https://www.meetup.com/clickhouse-seattle-user-group/events/290310025/) at the Microsoft office in Redmond on January 18, 2023
- Learn more about how ClickHouse is used within Microsoft Clarity, the free behavior analytics product for website owners in our [meetup report](https://www.clickhouse.com/blog/petabyte-scale-website-behavior-analytics-using-clickhouse). 