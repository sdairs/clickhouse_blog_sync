---
title: "Anlytic.com - Big-Data Analytics at the Dutch Police"
date: "2025-04-28T15:30:42.402Z"
author: "ClickHouse Team"
category: "User stories"
excerpt: "\"If we are looking at high-performance database systems for these types of workloads, the only two options are ClickHouse and Snowflake. ClickHouse is significantly faster.\" - Martijn Witteveen, CEO"
---

# Anlytic.com - Big-Data Analytics at the Dutch Police

<p>
<em>In this interview, we enjoyed sitting down with <a href="https://www.anlytic.com/">Anlytic.com</a> to delve into their experience with our ClickHouse and ClickHouse Cloud on AWS. We discussed the challenges they faced before discovering ClickHouse, the impact it has had on their data analytics, and how it has transformed the way their team operates. Their insights offer a firsthand look at how ClickHouse's speed, scalability, and flexibility drive innovation and efficiency in their organization. Enjoy this deep dive into their journey with ClickHouse, and perhaps find inspiration for your own data challenges.</em>
</p>
<h3>Do you mind introducing yourself?</h3>


<p>
My name is Martijn Witteveen. I am 28 years old, and I live with my wife in Amsterdam. After I was kicked out of high school, I started my first company selling energy contracts to businesses. During that time, I realized the need to have passion in what you do. That passion is needed to keep your energy levels as high as possible. Needless to say, selling energy contracts wasn't my passion. I finished high school and then started studying math at an applied university. I was surprised how good I was at this, and after a year, I continued studying Econometrics. After a year, I switched to a double bachelor's degree combining Econometrics with Business economics. During this time, I was an automation engineer, where, after 1.5 years, I managed 13+ engineers, wrote style guides for the company, and gave masterclasses in software development. 
</p>
<h3>What is the origin story of the company or the team within the company? What problem are you solving?</h3>


<p>
Although the automation engineering job was technically challenging, my passion lies in data. During COVID, I started freelancing as a data engineer. After six months, I was introduced to the National Police in the Netherlands. They had built a handful of dashboards for the Head of the Police and ministers in the parliament. They asked for my help to take these dashboards to production. While working on the data infrastructure, I realized a massive duplication of work was occurring. Not directly in this process, but the reporting flow, as the industry standard, has an enormous productivity issue. The de facto way of working is by pre-building data assets to be used in dashboards. Then, these dashboards are stripped apart into separate Word documents, where, in turn, implications are discussed. If we look at that process and the communication flows required, we face two major issues. The first is that pre-building data assets lack the flexibility required to make an extensive range of analyses. That means that instead of sharing data around an organization, we share insights on dashboards, for which in-depth analysis requires another layer of building data assets. Previous BI tools are built upon that assumption. With the rise of ClickHouse this assumption is no longer required, but previous BI systems are still working under this assumption. We shouldn't distribute dashboards but the data itself. When we do this, a second issue arises: communication around the data itself. Copy and paste charts into Word documents to write reports disconnects those reports from the data itself. Resulting in a massive duplication of work. 
</p>
<p>
At Anlytic.com, we remove the data accessibility barrier by directly distributing data around an organization. With our reporting features, we keep this data connected in one place, which we are calling a Data Hub. 
</p>
<h3>What is most important when you tell your, or your team’s, story?</h3>

<p>
We are going against all odds; we are creating a category in an established market in which our product functions as a substitute. And I love it! I genuinely believe that we can impact how companies are run in the future. 
</p>

<iframe width="560" height="315" src="https://www.youtube.com/embed/NJ99IsdfMSs?si=vz9ai9_-_z2dGfNl" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

<h3>What requirements did you have for the database/store component(s) in your architecture?</h3>
<ul>

<li>By limiting pre-processing of data, performance is our most significant barrier. </li>

<li>On-demand scaling of our database plays a large role in ad-hoc advanced calculations</li>

<li>To guarantee data quality, we wanted to stay as close as possible to a fully structured SQL database</li>

<li>On-premise option </li>
</ul>
<h3>Discovery of ClickHouse - how did you hear about it, and what made you excited to give it a try? What were your hesitations?</h3>

>If we are looking at high-performance database systems for these types of workloads, the only two options are ClickHouse and Snowflake. ClickHouse is significantly faster. Before ClickHouse, we were using Postgres. Here, we had one query that was taking 80+ seconds to load. I tried everything to get the performance up for this query. When I switched to ClickHouse, the runtime dropped to 0.3 seconds. 

<p>
My most considerable hesitation was the majority of the application. One clear signal of this is the quality of the client libraries. We are using Golang, and the GitHub page already shows that they are not implementing the Golang standard database interface. This would and is resulting in much extra code on our side. But the performance is unprecedented and is worth it.
</p>
<h3>How did you evaluate ClickHouse? How did ClickHouse perform against the alternatives considered?</h3>


<p>
As I mentioned before, the performance update when switching from Postgres was extreme. The same holds for the runtime of the data pipelines. At this moment, we are processing around 1 billion rows per month, reducing the cost of these pipelines significantly. 
</p>
<h3>What alternative databases did you consider?</h3>


<p>
The main alternative was Snowflake. One major issue with Snowflake is the lack of an On-Prem solution. Some of our clients run a complete Anlytic.com instance on their cloud for, them having the option to spin up ClickHouse ourselves saves us a lot of extra work.
</p>
<h3>What were the considerations when weighing the use of cloud vs self-managed ClickHouse?</h3>


<p>
The cloud instance has an excellent sleeping mode. This makes the cost go down significantly while still having a heavy instance running during working hours. As I said, we are using both self-managed instances for our On-Prem solution and the Cloud instance for our cloud-hosted instances.  
</p>
<h3>Can you share some quantitative metrics about ClickHouse's performance (e.g., ingest/query latency/overall data volumes/cost efficiency)?</h3>


<p>
We are still in the early stages. For now, we see that on our primary cloud instance, we read more than 1.8TB per month. With over 90 billion rows monthly read. All with an average query time of around 0.3 seconds.
</p>
<h3>Looking forward, what's next for you (and your use of ClickHouse)?</h3>


<p>
Soon, we will add a managed ClickHouse option to Anlytic.com. Together with our managed databases, we will start writing data connectors. 
</p>
<p>
Next to managed databases, we are working on adding metrics and real-time data to the system. 
</p>
<p>
My goal is to create predefined data hubs. For example, I want to make a SaaS data hub that connects to Stripe, a CRM, Google Analytics, and Application metrics. Then, we can combine Postgres for low data volumes and ClickHouse for large data volumes. 
</p>
<h3>How would you describe ClickHouse in 3 words?  </h3>


<ul>
<li> Unprecedented Fast </li>
<li>Heavyweight</li>
<li>Flexible</li></ul>

Interested in learning more? [Watch Anlytic's Meetup presentation.](https://www.youtube.com/watch?v=NJ99IsdfMSs)