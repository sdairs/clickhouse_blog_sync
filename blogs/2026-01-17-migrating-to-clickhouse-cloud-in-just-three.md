---
title: "Migrating to ClickHouse Cloud in just three months with no downtime: A 120 terabyte data journey and its benefits"
date: "2024-08-14T12:26:07.134Z"
author: "Vladimir Rudev, Lead Solution Architect, Azur Games"
category: "User stories"
excerpt: "It was clear that a large-scale infrastructure overhaul was necessary, as our technical debt was becoming unmanageable.  We had been using ClickHouse for years, so exploring ClickHouse Cloud on AWS made sense. "
---

# Migrating to ClickHouse Cloud in just three months with no downtime: A 120 terabyte data journey and its benefits

![Azur Games.png](https://clickhouse.com/uploads/Azur_Games_bd2e39de7d.png)

_This is a guest post from Vladimir Rudev, Lead Solution Architect, Azur Games._

Last year, we realized our existing technical solution no longer met the growing needs of our company. It was clear that a large-scale infrastructure overhaul was necessary, as our technical debt was becoming unmanageable.

We had been using ClickHouse for years, so exploring ClickHouse Cloud on AWS made sense. 

The challenge was migrating a 120 TB database without causing any downtime in our analytics and ensuring a seamless transition. We opted for a “full duplication,” verification, and atomic switchover approach to achieve this. You might wonder where all this data came from. As the top-one mobile game publisher by download numbers, we’ve launched over 150 projects, resulting in over 8 billion total installs. Naturally, this generates a massive volume of telemetry data.

A hypercasual game is a simple, easy-to-play mobile game with low barriers to entry. Such fast-paced, simple games generate massive amounts of telemetry data from user interactions, which is crucial for understanding player behavior, optimizing monetization, experimenting, and improving the overall gaming experience. This holds true for the casual and mid-core games that Azur Games also develops. The requirement for data analytics is true across all genres.

In this article, I’ll detail how the migration went, the challenges we faced, and the advantages we gained.

_Spoiler: Not only did we manage the migration successfully, but we also experienced numerous positive outcomes. The final cost of service after moving to the cloud remained comparable to what it was before. Additionally, we freed up half the time of two engineers, saved a lot of stress, and shifted our focus from maintenance to creation and more interesting tasks._

![Kingdome Clash.jpeg](https://clickhouse.com/uploads/Kingdome_Clash_bb657b24be.jpeg)

Now, let’s review the process point-by-point.

The main **objectives** we were looking to hit:

1. Increase storage reliability.
2. Improve operational reliability and reduce the number of failures.
3. Simplify maintenance.
4. Ensure flexibility for growth.
5. Optimize costs for our budget.

Our starting point:

**Resources:**
* Twenty powerful database servers + 3 low-power ones for ZooKeeper.
* 11 Airflow servers (200+ vCPUs).
* 6 MinIO servers (S3 emulator, Airflow cache).
* 4 MySQL database servers.
* Four servers for BI and support services.
* 2 Airflow engineers.
* 1 DevOps engineer.

Total: 45 servers and three specialists.

There are also many managed units, with the seven most significant being: CH, ZK, MySQL, MinIO, Airflow (scheduler, workers), and BI.

**Tools:**
* Ansible to manage all servers.
* Airflow 2.2.3, which was two years old.
* MinIO version is also two years old.
* ClickHouse 21.3, which was more than two years old.

## Concerns
**TL;DR:** The risk of a single disk failure leading to an entire shard collapse was a significant concern. This would result in complete data unavailability for some projects for an extended period. The most daunting fear has always been the cascading failure of data drives.

This problem is not uncommon in long-running projects with heavy disk usage. Disks installed in servers are often from the same batch, and they tend to fail at similar times. The same operating time means the same probability of failure. When one disk fails, the load on its neighboring disk increases. In our servers, organized in RAID 10, disks work in pairs, meaning that the failure of one can increase the likelihood of its partner, a copy, failing too. If a pair of disks from the same group fails, the entire server goes down.

We don’t worry when one replica goes down for 3-6 hours. However, if a 15 TB drive fails, synchronization can take about a week. If another partner disk fails during this time, the entire server fails, and resynchronizing the replica can take three days to a week. During this period, the remaining replica is heavily overloaded with ETL processes and synchronization to the new server. This is why it's recommended to have three replicas per shard with no more than 60% load on each replica, although this is significantly more expensive.

The second major issue was MinIO. Updating MinIO live was risky for us. As our volumes grew, service failures became more frequent, and adding resources to the MinIO cluster only helped a little. It was evident that we were either doing something wrong or encountering a bug in a specific version of MinIO that we hadn't yet identified. Over time, failures became more frequent, causing ETL processes to crash. The Airflow engineer had to spend considerable time checking and restoring failed ETLs.

To sum it up, there were two main pain points we learned to live with:

1. Admins struggled when software crashes occurred without a straightforward fix that didn't involve updates.
2. Airflow engineers faced constant disruptions when ETL processes broke, which, in one way or another, happened every time something failed. It affected data availability timelines and new feature development. 

Although we automated as much as possible to minimize these issues, significant time was still required for ETL support, impacting morale.

## Alternative solutions we considered other than ClickHouse Cloud
![Bunker Wars.jpeg](https://clickhouse.com/uploads/Bunker_Wars_c30c5bffb4.jpeg)

Finding the right solution took considerable time. Let me remind you of the main tasks we need to address:

1. Storage reliability.
2. Operational reliability.
3. Ease of maintenance.
4. Flexibility for growth.
5. Optimal cost for our budget.

These were our options:

**1. Stay on bare metal, but change provider — the rest remains as is**

This would address the fourth point, but it wouldn’t keep costs the same.

**2. Move to AWS/Google/Azure**

Properly configured, this option could solve issues with storage reliability, operational reliability, and cost flexibility. With expertise in Kubernetes, we could partially address ease of maintenance.

However, the cost issue still needs to be solved. Here’s a detailed explanation: Moving to AWS without ClickHouse Cloud provides more powerful hardware but at a much higher price due to the large amount of data. AWS can help mitigate inefficient configurations by allowing the use of a single "fat" server. We could use one large shard instead of multiple smaller ones and put a ton of drives in there, but we’d still need at least two replicas. This would mean managing 240 TB of data on disks, costing thousands of extra dollars for storage alone, not including other expenses. So, cost remains a significant concern.

There are also options to split data into hot and cold storage, potentially halving the costs. However, these solutions need extensive planning, testing, and time from a highly qualified engineer. The challenge is finding the correct configuration for our data processing patterns without compromising speed and service quality in the future.

**3. Stay with the previous provider, but move within its framework**

This option would allow us to update to the latest software versions and address some technical debt. However, it would only superficially touch on the other goals.

## Why we chose ClickHouse Cloud

ClickHouse Cloud, connected seamlessly through AWS PrivateLink, offers significant cost savings with features like storing data on S3 instead of disks and Zero Copy Replication (ZCR). The latter plays the critical part here, as ZCR allows for two replicas in a shard without storing two copies of the data. This way, the volume of the stored data ends up being the same as its actual size.

S3 provides 99.999999% data durability at a lower cost than traditional disks used for storage.

## Migration outcome
![Airflow workers details.jpg](https://clickhouse.com/uploads/Airflow_workers_details_d349b95566.jpg)

**Hardware:**

* Airflow now operates with 24 to 40 vCPUs and is working auto-scaling.
* ClickHouse now has three replicas with all data on S3. All requests are tested on real volume, and none perform worse than on the old ClickHouse setup (this is important, and we double-checked this several times).
* A significant portion of requests are now processed faster, with the rest performing about the same.
* The remaining databases are now included in RDS.
* The load on admins and ETL engineers has decreased significantly.
* While the total cost (ClickHouse database + ETL infrastructure) has increased slightly, it remains comparable.

**And what about our goals?**

1. Storage reliability: ALL critical units (DB, S3) are included in a “service” that guarantees reliability. We offloaded many complex tasks, making SaaS solutions incomparably cheaper. 

2. Operational reliability, growth flexibility, and optimal cost: Achieved 100%. 

3. Ease of maintenance: Solved by 80-85%. The problem wasn’t completely eliminated but was significantly reduced. Considering the resources invested, this is a good result, more than compensating for the slight cost increase as we’ve saved a lot of engineers’ time. 

4. Flexibility for growth: Achieved 100%. 

5. We spent three months of full-time work from two engineers and a month of my time on the move. The cost of service not only remains comparable but is covered many times over by the benefits received.

**Reduced Complexity:**

1. MinIO, which was replaced by Amazon S3. 

2. Three different Airflow deployments. The latest version on excellent hardware handles the entire load perfectly. 

3. Numerous unnecessary configs and scripts for the setup and maintenance of old servers.

**Advantages gained:**

1. The system as a whole has become simpler, faster, and more reliable. 

2. The layer of admins between the code and the result has become thinner. Our team now has more control and capabilities, and we can use them without involving admins. They can add the necessary software to Python and scale up and down without involving administrators, reducing intermediate steps in routine operations. 

3. We received excellent hardware from Amazon. This is especially true with the new Airflow. Fast S3, along with a super-fast network and disks, has significantly sped up our ETL. 

4. We gained the ability to scale 2x, 5x, or 10x in minutes when needed. For example, when an integration is temporarily broken on the data provider's side, and we need to accept more data than usual quickly. 

5. We received the latest version of ClickHouse, and ongoing upgrades on a rolling basis managed by the ClickHouse Team, which includes numerous new features and optimizations we need to try: 

* New convenient functions for calculating everything;
* Optimizations that can speed up some of our queries;
* New features related to data storage that can potentially save us space (which affects costs) and also speed up queries;
* Features that will help our ETLs become faster, more reliable, and more straightforward. 

6. Tasks requiring experimentation will be completed faster. When selecting optimal server parameters nowadays, I often don’t even have time to make myself a cup of tea before the new configuration is applied. It's always nice to see results quickly. There’s no need to switch to another task while waiting. 

7. Experimenting is now manageable. I always have a list of “things I can do better” in my head, almost all related to data. Any experiment requiring a significant overhaul of the data storage and recording circuit used to put a strain on the disks, but this is no longer a concern. The process was intimidating in the old ClickHouse, but that’s no longer the case. We can load the new ClickHouse as much as we want without fear of failure.

## Business Impact
![ETL status (high level).jpg](https://clickhouse.com/uploads/ETL_status_high_level_555210bdda.jpg)

The main benefit is saving employee time, which can now be spent on more exciting and strategic tasks. One of our administrators has about 60% of their time freed up, and our ETL engineer now saves 40% of their time. 

This also saves a lot of stress, though calculating the moral component is more challenging. Now, instead of constantly maintaining complex infrastructure, we can focus on creation.
The company always has a backlog of interesting tasks; for instance, we were finally able to start experimenting with the DBT (Data Build Tool), which is now widely used in analytics and fits our needs perfectly. 

Additionally, many business tasks began to reach release much faster. In many cases, the time spent was reduced by twofold or more.

A classic example is the need for a new data aggregation that must be recalculated for the entire historical period. 

Previously, in order to do this, we needed to calculate the available free resources in the cluster, estimate their speed, multiply by the volume of calculations, and get the deadline for completion — assuming everything went well, there were no critical failures, and the cluster remained stable.

Now, we can instantly add computing power on both the ETL and DBMS sides. This means tasks are completed faster, proportional to the resources used. 

>  By achieving results faster at the exact resource cost, the business naturally benefits.

## Have any new problems come with it?
Not exactly new problems, but a new reality. Life in the cloud follows different rules. The cloud is usually merciless in terms of cost. You pay for every byte sent over the network and every processor cycle used. And if you don’t use it to its full potential, it’s still running idle. This forces us to implement algorithms and architectures to maximize efficiency.

However, all this has a positive effect from all this. Combined with very fast scaling and super-powerful hardware, it’s possible to increase system performance multiple times with minimal effort.

The architecture of the new cluster is also significantly different from what we had. What worked well for us in the past turned out to be ineffective in the new cluster. But new solutions have emerged to address the same problems. During the move, we adjusted to the new reality.

## Migration Timeline

**July.** We began active work on the migration. For a month, we engaged with the ClickHouse team, gradually familiarizing ourselves with the product and conducting small experiments.

**August.** Realizing the need for a thorough trial, we started moving data. We aimed to complete the transfer within a month, or at most six weeks, while also performing the necessary refactoring, which would also take about a month. This is where our first mistake surfaced. Our two engineers were frequently distracted by business-related tasks, causing delays. Consequently, we could only complete some things within the planned timeframe.

**September.** We spent the entire month moving data and making the necessary adjustments.

**October.** This month was initially planned as a safety net. We completed the pending tasks and conducted thorough testing. By the end of September, we discovered problems in the data merging process that we had yet to notice earlier. During the first half of October, we continued adding data. In the second half, we focused on ensuring that all data was transferred correctly. Despite our efforts, the work still needed to be finished by the end of October.

**November.** With one month left, it seemed like we were able to breathe a little and focus on transferring and verifying the data more meticulously. Accuracy was our top priority. The team did an incredible job. By mid-November, we were almost ready to switch over the analytics to the new system.

We made the switch on November 21st and immediately encountered two unpleasant bugs. Some queries in ClickHouse started behaving differently than expected. We reported the issues to the ClickHouse team, who quickly provided a workaround for the first issue and fixed the second one on their end.

By November 23rd, we had switched our BI operations to the new ClickHouse system.

On November 27th, we signed the contract and shut down the old servers.

**Total**: 3 months of active work.

## Why the ClickHouse team is a treat to work with

>The architecture of ClickHouse Cloud differs significantly from the traditional on-premises setup. This led to us having some issues during the testing phase. The ClickHouse team was very supportive, helping us find alternative solutions and even quickly making code changes in ClickHouse specifically for our needs.

## Summary

In just three months, we deployed a new, more technically advanced solution. This allowed us to achieve nearly 100% reliability in storage and service, provided potential for future growth, and freed up significant time for our engineers. The benefits gained from these improvements more than justify the slightly increased cost of maintenance.

