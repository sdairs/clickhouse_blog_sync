---
title: "ClickHouse Cloud is now in Public Beta"
date: "2022-10-04T12:42:11.659Z"
author: "The ClickHouse Team"
category: "Product"
excerpt: "ClickHouse Cloud has entered public beta. Get your free trial now!"
---

# ClickHouse Cloud is now in Public Beta

![Cloud beta cover - 2 orbits - 5 elements.png](https://clickhouse.com/uploads/Cloud_beta_cover_2_orbits_5_elements_8b925b27e7.png)

Since inception, ClickHouse has been synonymous with lightning fast query speeds over massive datasets. As the creators of the open source ClickHouse technology, our goal has always been to help our user community to take advantage of this capability with as little friction as possible. This is why we are thrilled to announce the Beta release of ClickHouse Cloud!

We are proud to be one of the fastest-growing, most-loved open source projects, and we are seeing an ever-increasing demand for the unique capabilities of ClickHouse. That is why we wanted to remove any remaining barriers to adoption by offering these capabilities as a serverless product, without any need to manage server infrastructure.

**To get started, simply sign up [here](https://clickhouse.cloud/signUp) for a 14-day free trial.**

## ClickHouse Cloud

To be able to deliver our vision of a cloud native, seamlessly scalable, easy-to-use analytical database, we’ve been working on bringing new innovations to the ClickHouse Cloud experience. Some examples include:

* Developing flexible scaling of both compute and storage by decoupling them.
* Negating the need for tedious re-architecture by using optimized object storage as primary storage. 
* Improving performance and mitigating latency with multi-level caching.
* Improving cost efficiency with higher data compression by default.

ClickHouse Cloud drastically simplifies the use of ClickHouse for developers, data engineers and analysts, allowing them to start building instantly without having to size and scale their cluster. And they only pay for what they use, while at the same time taking advantage of the best price / performance ratio in the industry.

![cloud.png](https://clickhouse.com/uploads/cloud_d553eb32e5.png)

Let’s dig into some of our favorite benefits of ClickHouse Cloud.

### Simplicity

One of the reasons the ClickHouse self-managed database became so popular was the simplicity and ease with which anyone could get started. Downloading a binary and running it is essentially all that is needed to start using the open source software. And because of its performance, many users are content with keeping a single server of ClickHouse running. With ClickHouse Cloud, we have continued our commitment to simplicity for any user, be they operators, developers or analysts.

It starts with providing an intuitive user interface where a user can provision ClickHouse Cloud services within minutes. This serverless offering doesn't require any input in regards to server size, number or topology. That work is done by ClickHouse Cloud and abstracted away from the user.

![create_simple_service.gif](https://clickhouse.com/uploads/create_simple_service_191f14bb20.gif)

Once a service is up and running, administrative tasks such as upgrades and load balancing are done automatically and seamlessly in ClickHouse Cloud, simplifying the life of administrators. Our innovative use of S3 object storage as the primary storage in ClickHouse Cloud allows much more flexibility when increasing capacity. The task of re-architecting server specifications and setups is no longer necessary when using ClickHouse Cloud.

To put it very simply: **It just works.**

### Efficiency

The vast majority of analytical workloads have a choppy utilization: high inserts and query loads at certain times of the day with significantly lower load otherwise. The periods between changes in demand are typically too short for an administrator to manually tune the provisioned servers. This results in resources sitting idle most of the time, leading to unnecessary spend.

This is why ClickHouse Cloud automatically scales resources up, down and even pauses services depending on demand, maximizing resource efficiency. Our separation of compute and storage means we can provision the specific resource needed in a certain situation, rather than having to over-provision a full server to serve the increase in demand in one area. It is also worth noting that our use of object storage as the primary storage has a big impact on the cost efficiency of the service, especially when serving large datasets.

Our [pricing model](https://clickhouse.com/pricing) also reflects this commitment to efficiency: you only pay for work done, not idle resources. Reducing wasted resources is also an environmental benefit, which is taking on a growing importance for us and many of our customers who are looking to reduce their carbon footprint where they can.

### Security

ClickHouse Cloud was built with a security-first philosophy that permeates the whole platform. This “secure by default” mindset means that ClickHouse Cloud generates secure passwords and enforces IP filtering by default. A security team is constantly monitoring and evaluating security threats, dedicated to ensuring the protection and integrity of our customer’s data.

In addition, the platform has strong authentication and role-based access control, including federated authentication via Google. It employs strong encryption at rest and in transit, and strong network access controls, including support for AWS PrivateLink, and provides activity and audit logging.

We have already acquired accreditations such as SOC 2 Type I, with SOC 2 Type II in progress. ClickHouse Cloud is also GDPR and CCPA compliant.

### Ecosystem

ClickHouse Cloud has the ability to seamlessly interact with other systems, such as data sources, user interfaces, and programming languages, often with the simplicity of a few clicks in our Cloud Console. Building on the top of a solid open-source base, we are making significant investments developing and maintaining a strategic set of integrations, and have an active partnership with many key vendors in our ecosystem to help them integrate with our platform. Our incredible community is also full of organizations and individuals who are developing and publishing their own ways of interacting with ClickHouse.

At Beta launch, we have curated a list of ClickHouse Integrations available in our Cloud Console that include:

<table>
 <tr>
   <th>Data Ingestion
   </th>
   <th>Data Visualization
   </th>
   <th>Language Client
   </th>
   <th>SQL Client
   </th>
  </tr>
 <tr>
   <td>S3
   </td>
   <td>Grafana
   </td>
   <td>Go
   </td>
   <td>ClickHouse Client
   </td>
  </tr>
 <tr>
   <td>Kafka
   </td>
   <td>HEX
   </td>
   <td>Python
   </td>
   <td>DataGrip
   </td>
  </tr>
 <tr>
   <td>DBT
   </td>
   <td>Superset
   </td>
   <td>Java
   </td>
   <td>DBeaver
   </td>
  </tr>
 <tr>
   <td>Airbyte
   </td>
   <td>Deepnote
   </td>
   <td>Node.js
   </td>
   <td>Arctype
   </td>
  </tr>
  </table>
<p/>

The full list with more details about the categories and support levels is available in [our public documentation](https://clickhouse.com/docs/en/integrations/).

![s3-integration.gif](https://clickhouse.com/uploads/s3_integration_1bb489af2a.gif)

### Speed

ClickHouse is known for its query speed, especially with massive and quickly growing data volumes. Therefore it was incredibly important to us that ClickHouse Cloud deliver the speed that our users expect, even with all of the additional benefits described above.

The early results from our own benchmarking exercises are public and can be found[ here](https://benchmark.clickhouse.com/). The ability to tune and adjust certain elements of the cloud platform means that this aspect of ClickHouse Cloud will see continuous improvement, but even now we are seeing near parity with a well-tuned ClickHouse self-managed database with most types of queries. The added latency introduced by using object storage fades into insignificance with complex queries, while being mitigated by the advanced multi-level caching capabilities built into ClickHouse Cloud.

We believe that ClickHouse Cloud offers the best price to performance ratio in the industry through these efficiency gains and broadly maintained query and data load speeds.

## Try it out for free

**To get started, simply sign up [here](https://clickhouse.cloud/signUp) for a 14-day free trial.**

## Additional resources

* ClickHouse Cloud [Compatibility Guide](https://clickhouse.com/docs/en/whats-new/cloud-compatibility): See what the differences are between self-managed ClickHouse and ClickHouse Cloud
* Connect with us: Join the ClickHouse community in [Slack.](https://clickhousedb.slack.com/join/shared_invite/zt-1gh9ds7f4-PgDhJAaF8ad5RbWBAAjzFg)