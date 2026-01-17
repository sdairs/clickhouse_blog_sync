---
title: "London Meetup Report: How Cloudflare Processes Hundreds of Millions of Rows per Second with ClickHouse"
date: "2023-10-20T07:56:26.419Z"
author: "Elissa Weve"
category: "Community"
excerpt: "Discover how Cloudflare leverages ClickHouse dictionaries to process hundreds of millions of rows per second for applications like web traffic analysis and customer dashboards in this London meetup report."
---

# London Meetup Report: How Cloudflare Processes Hundreds of Millions of Rows per Second with ClickHouse

<iframe width="764" height="430" src="https://www.youtube.com/embed/0A8nTASRERo" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>

<br/>

On September 19th, 2023, we were fortunate to have Cloudflare once again host our ClickHouse Community meetup at their beautiful office in central London. We heard from James Morrison, Systems Engineer at Cloudflare who shared details about their extensive history with ClickHouse, the intricacies of managing dictionaries, and the various challenges and solutions encountered along the way.

Cloudflare is one of the earliest adopters of ClickHouse. As James mentioned, "ClickHouse was open-sourced in 2016, and we were running in production by the end of that year." Not only has Cloudflare trusted and adopted ClickHouse from its early days, but they have also made contributions to its development. 

Cloudflare uses ClickHouse for multiple use cases including:

- **HTTP and DNS Analytics:** Essential for monitoring and understanding the massive web traffic that Cloudflare handles daily.

- **Logging Analytics, Traffic and Bot Management:** Before even starting the bot analysis and classification, Cloudflare relies on ClickHouse for efficient log collection. By leveraging its real-time analysis capabilities, Cloudflare can effectively manage and filter web traffic, distinguishing between legitimate users and bot traffic.

- **Cloudflare Worker Runtime Analysis:** Cloudflare Workers empower developers to run serverless applications closer to the end user. ClickHouse provides critical runtime analytics that ensures optimal performance.

- **Internal Analytics Workload:** ClickHouse is instrumental in powering Cloudflare's internal data analytics.

- **Customer Dashboards:** ClickHouse ensures that Cloudflare's customer dashboards offer real-time, comprehensive data views, reflecting its vast storage and swift data retrieval capabilities.

- **Firewall Analytics & Cloudflare Radar:** Essential tools like Firewall Analytics and the Cloudflare Radar rely on ClickHouse to store vast amounts of data and retrieve it promptly on demand.

## Scale of Operations ##
James shared the massive scale of Cloudlare’s ClickHouse deployment, "This year we actually exceeded a thousand active replicas. That's processing hundreds of millions of inserted rows every second". He mentioned how they've leveraged ClickHouse’s powerful sampling features for their diverse datasets, from HTTP requests to DNS lookups.

<br/>

>"ClickHouse was open sourced in 2016, and we were running in production by the end of that year, so we've been long term users. Since then we've scaled up exponentially. This year we actually exceeded a thousand active replicas. That's processing hundreds of millions of inserted rows every second, which actually corresponds to quite a significantly larger number of events because we've been using a lot of sampling." 

<br/>

## Deciphering ClickHouse Dictionaries ##
[Dictionaries in ClickHouse](https://clickhouse.com/docs/en/sql-reference/dictionaries) enable efficient key-value lookups [accelerating queries which would otherwise need an expensive JOIN](https://clickhouse.com/blog/clickhouse-fully-supports-joins-direct-join-part4#direct-join). They are crucial in real-time analytics scenarios that Cloudflare products rely upon. "Dictionaries allow us to do key-value lookups in our queries, typically storing the data in memory, which allows us to do join type queries more efficiently," said James. 

![Cloudflare1.png](https://clickhouse.com/uploads/Cloudflare1_9575742cf5.png)

The usage of dictionaries has grown considerably over the years with 184 dictionaries deployed in various places.

## Challenges with Memory Consumption ##
James discussed the issues they confronted, especially concerning memory consumption. Their largest dictionary exceeded 20GiB of memory, with the total overhead of all dictionaries surpassing 15 TiB. 

![Cloudflare2.png](https://clickhouse.com/uploads/Cloudflare2_588746cb5f.png)

He then highlighted their shift from the ['hashed' layout to the 'hashed array' layout](https://clickhouse.com/blog/faster-queries-dictionaries-clickhouse#choosing-a-layout), which significantly reduced memory footprints by over 4x.

![Cloudflare3.png](https://clickhouse.com/uploads/Cloudflare3_597bb5f744.png)

Another significant concern was the varied set of dependencies for their dictionaries on external systems. This made supporting the dictionaries challenging with limited visibility into downstream systems. Additionally, these systems would be subject to requests from ClickHouse placing an often unwelcome additional load on these services. 

Cloudflare's solution, the 'ClickHouse Dictionary Dumper', helped with these issues. It effectively separates data production from consumption, allowing them to handle potential upstream failures seamlessly. James explained, "We produce data in Cronjobs and Kubernetes... on each ClickHouse replica, we have a timer which is just pulling the dictionary bundle out of object storage and extracting it onto disk."

## Continual Evolution ##
While discussing potential enhancements, James hinted at further optimizing memory use, possibly through in-memory compression. He also discussed the dynamic nature of dictionaries, suggesting some static dictionaries might become dynamic in the future, especially with the introduction of the 'clickhouse-dictionary-dumper.'

## More Details ##
- This talk was given at the [ClickHouse Community Meetup](https://www.meetup.com/clickhouse-london-user-group/events/295026299/) in London on September 19th, 2023
- The presentation materials are available [on GitHub](https://github.com/ClickHouse/clickhouse-presentations/tree/master/meetup84)

## Further Reading ##

- [HTTP Analytics for 6M requests per second using ClickHouse](https://blog.cloudflare.com/http-analytics-for-6m-requests-per-second-using-clickhouse/) (Cloudflare blog)
- [Log analytics using ClickHouse](https://blog.cloudflare.com/log-analytics-using-clickhouse/) (Cloudflare blog)
- [ClickHouse Capacity Estimation Framework](https://blog.cloudflare.com/clickhouse-capacity-estimation-framework/) (Cloudflare blog)

