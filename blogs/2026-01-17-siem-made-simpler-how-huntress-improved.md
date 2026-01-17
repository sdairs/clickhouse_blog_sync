---
title: "SIEM made simpler: How Huntress improved performance and slashed costs with ClickHouse"
date: "2024-11-19T15:41:30.816Z"
author: "ClickHouse Team"
category: "User stories"
excerpt: "By moving from Elasticsearch to ClickHouse Cloud, Huntress slashed monthly costs from $70K to $5K and scaled to handle up to 200,000 records per second."
---

# SIEM made simpler: How Huntress improved performance and slashed costs with ClickHouse

<p>
<a href="https://www.huntress.com/">Huntress</a> is on a mission to make enterprise-level security accessible to everyone. Founded in 2015 by a team of ex-NSA cyber operators, the managed security platform offers a range of solutions designed to keep small and mid-sized businesses safe from cyber threats.
</p>
<p>
But while Huntress positions itself as a security company, co-founder and CTO Chris Bisnett admits — only half-joking — that “secretly we’re a big data company.” With more than 3 million endpoints, data from over a million Microsoft 365 identities, and logs flowing in from around half a million data sources, Huntress’s ability to analyze and act on this massive volume of information is central to its success.
</p>
<p>
At a <a href="https://www.youtube.com/watch?v=lhsWNofOcdk">ClickHouse meetup in New York</a>, Chris explained how switching to ClickHouse Cloud has helped Huntress optimize performance, address scaling challenges, and simplify their big data workflows, all while saving tens of thousands of dollars each month.
</p>
<p><iframe width="560" height="315" src="https://www.youtube.com/embed/h-dkVkEh5ec?si=45p_t5huvxEUU1hp" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe></p>
<h2>The SIEM dilemma</h2>


<p>
A <a href="https://clickhouse.com/engineering-resources/siem">SIEM (Security Information and Event Management)</a> system is designed to collect, process, and analyze logs and security data from various sources within an organization’s network. It acts as a centralized hub, pulling in information from firewalls, cloud infrastructure, identity providers, and other devices to detect and respond to potential threats in real time.
</p>
<p>
But managing a SIEM is tricky at the best of times. The challenge, as Chris describes it, is twofold: volume and variety. SIEMs must handle huge amounts of data coming from diverse sources, each in its own format — syslog, JSON, plain text, and more. This requires companies like Huntress to develop custom parsers and schemas to standardize and make the data usable. As data volumes surge, the costs associated with processing and storing it also increase, making it difficult to maintain efficiency and affordability.
</p>
<p>
For Huntress, the standard SIEM challenges are amplified by the needs of their customers — SMBs with limited IT resources. “They don’t have big budgets or internal security teams, and yet they need a lot of the same things as larger enterprises,” Chris says of Huntress’s customers. “So there’s gotta be a trade-off somewhere. It’s our job to figure that part out.”
</p>
<p>
To provide customers with the same level of 24/7 monitoring and proactive threat protection as enterprise companies, Huntress needed a more efficient database management system that could process logs from millions of endpoints while keeping costs in check. Adding to the pressure was an ambitious timeline of improving their SIEM solution in 6-8 months.
</p>
<p>
“A lot of people said it couldn’t be done,” Chris says. “But we did it anyway.”
</p>
<h2>In search of a better database</h2>


<p>
Chris and the team kicked off a search for a database that could handle their growing data volumes without driving costs through the roof. They began by exploring familiar options, including Elasticsearch, which they had used before. But while Elasticsearch offered strong search capabilities, scaling it for Huntress’s workload was, in Chris’s words, “super expensive,” costing upwards of $70,000 per month. They also considered Postgres, but as Chris explains, “The problem there is, if you want to scale it, you’ve got to have multiple individual Postgres databases,” which added unwanted complexity and increased costs.
</p>
<p>
Microsoft Sentinel, another contender, was briefly evaluated for its ability to manage large data volumes. For Huntress, however, building their SIEM on an existing solution like Sentinel offered little opportunity for differentiation. It was important to keep a competitive edge by creating a unique system tailored to their needs, rather than relying on a pre-built solution.
</p>
<p>
Around this time, they noticed <a href="https://clickhouse.com/cloud">ClickHouse Cloud</a> gaining popularity. They decided to give it a try and found that the managed service offered a scalable solution that met Huntress’s data needs at a fraction of the cost of Elasticsearch — around $5,000 per month for a comparable workload. ClickHouse’s support for <a href="https://clickhouse.com/docs/en/materialized-view">materialized views</a> and advanced query capabilities, without requiring extensive configuration, made it an ideal fit for powering their SIEM, balancing performance, affordability, and the specific needs of their customers.
</p>
<p>
“The best part is, there’s zero maintenance required,” Chris says. “We just ingest a ton of data in there; it’s super efficient and way cheaper than other solutions. It checks all the boxes.”
</p>
<h2>Huntress’s new data infrastructure</h2>


<p>
Huntress’s implementation of ClickHouse is defined by its simplicity. “To me, simple generally means cheaper and more reliable,” Chris says. “It means fewer parts to go wrong.”
</p>
<p>
As a Ruby on Rails shop, they use Vector.dev (a tool open-sourced by Datadog) to batch and transform data before it reaches ClickHouse. According to Chris, Vector allows Huntress to handle large-scale inserts — up to 200,000 records per second — which ClickHouse manages “without batting an eye.” This architecture reflects Chris’s philosophy of keeping infrastructure lean to minimize points of failure and reduce costs and maintenance requirements.
</p>
<p>


![386382601-f9fcb272-9d89-4c88-b29b-6a1900aad069.png](https://clickhouse.com/uploads/386382601_f9fcb272_9d89_4c88_b29b_6a1900aad069_b49ad86b4c.png)

</p>
<p>
Huntress’s data pipeline: Rails and Vector process data before integration into ClickHouse for optimal performance.
</p>
<p>
Data sources are funneled through Vector, which batches and routes the data directly into ClickHouse. The team uses HTTP as the insert method, taking advantage of Vector’s templating language to dynamically map data fields to ClickHouse tables. This setup has allowed Huntress to scale their data ingestion seamlessly, without adding complexity or overhead.
</p>
<h2>Lessons learned along the way</h2>


<p>
For the Huntress team, implementing and scaling ClickHouse wasn’t without its challenges. During his presentation in New York, Chris shared a few key lessons learned:
</p>
<h3>Partitioning</h3>


<p>
Initially, Huntress tried to partition data by tenants and days, following a common pattern in other databases like Postgres. However, they quickly ran into limitations, as ClickHouse restricts the number of partitions per insert. As Chris explains, they learned that partitions in ClickHouse are best used for lifecycle management, such as time-to-live (TTL) configurations, rather than for primary data sharding.
</p>
<h3>Table ordering</h3>


<p>
Defining a proper sorting key was important for optimizing performance. Huntress found that ordering tables by tenant ID and other common fields dramatically improved query speeds. As Chris explains, “The ordering of your data, your primary key, and your sorting key is super important. This is maybe the biggest thing that drives performance in ClickHouse.” 
</p>
<p>
ClickHouse’s ability to skip over irrelevant data based on sorting keys is a powerful feature, but it requires precision from the outset. Chris notes that fixing the table order after the fact can be complex and time-consuming — something the Huntress team experienced firsthand.
</p>
<h3>Data skipping indexes</h3>


<p>
While ClickHouse’s <a href="https://clickhouse.com/docs/en/optimize/skipping-indexes">data skipping indexes</a> can improve query performance by ignoring non-relevant granules, they “aren’t magic,” Chris says. The team found that these indexes function differently from secondary indexes in Postgres; in order to be effective, the data must be ordered correctly, and the indexes should be applied strategically. When not set up properly, the Huntress team saw little to no performance improvement. “The real performance issue was having to visit multiple parts to find the data we needed,” Chris says.
</p>
<h2>Building a scalable, efficient future</h2>


<p>
By switching to ClickHouse Cloud, Huntress has transformed its approach to data management, cutting costs by more than 90% while improving performance. The new setup easily processes up to 200,000 records per second, allowing Huntress to scale as its customer base grows. ClickHouse’s features, like materialized views and advanced query capabilities, have given the team the foundation and framework needed to create a streamlined, low-maintenance system that meets their needs now and in the future.
</p>
<p>
Not only has the move to ClickHouse strengthened Huntress’s ability to deliver fast, accurate threat detection, it has reinforced their mission of making enterprise-level security accessible to everyone. With a scalable and efficient data infrastructure in place, Huntress is poised to keep expanding its services, ensuring that comprehensive, affordable protection remains within reach for small and mid-sized businesses around the world.
</p>
<p><iframe width="560" height="315" src="https://www.youtube.com/embed/lhsWNofOcdk?si=emJ_LXrSqLZjLzIm" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe></p>

><p>To learn more about how ClickHouse can help you improve performance and scalability while reducing costs, <a href="https://clickhouse.com/cloud">try ClickHouse Cloud free for 30 days</a>.
</p></p>

