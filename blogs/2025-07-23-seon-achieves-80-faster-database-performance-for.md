---
title: "SEON Achieves 80% Faster Database Performance for Anti-Fraud Platform with ClickHouse on AWS"
date: "2025-07-23T09:16:59.135Z"
author: "AWS"
category: "User stories"
excerpt: "Learn how anti-fraud platform SEON worked with ClickHouse and used AWS to improve near real-time data analytics by 80% and reduce data storage costs by 30%"
---

# SEON Achieves 80% Faster Database Performance for Anti-Fraud Platform with ClickHouse on AWS

This was originally [published by AWS](https://aws.amazon.com/solutions/case-studies/seon-clickhouse/).

[SEON](https://seon.io/) wants to make the internet a safer place to do business. Co-headquartered in the US and Hungary, the company offers an integrated fraud prevention and AML (anti-money laundering) platform that helps customers in sectors such as financial services, ecommerce, and iGaming. As SEON entered a period of rapid growth, the increasing volume of transactions introduced new demands on database performance. To support its momentum and enhance the efficiency of its customer screening process, SEON worked with [AWS Partner](https://partners.amazonaws.com/partners/0018a00001mU61yAAC/ClickHouse)  [ClickHouse](https://clickhouse.com/) to optimize performance and scalability. Using Amazon Web Services (AWS), the three companies engineered a solution that improved processing time by over 80 percent.

## About SEON

SEON helps risk teams detect and stop fraud and money laundering while ensuring regulatory compliance. By combining real-time digital footprint analysis, device intelligence, and AI-driven rules, SEON empowers more than 5,000 forward-thinking businesses globally to prevent sophisticated threats before they occur. With integrated fraud prevention and AML capabilities, SEON operates from Austin, London, Budapest, and Singapore.

## Opportunity | A need for a high-performance database for massive datasets

SEON's fraud detection technology helps build trust in online transactions. The company helps customers identify multiple types of fraud, including [chargeback fraud](https://seon.io/resources/chargeback-vs-refund/) and credentials theft, and provides login and transaction monitoring. SEON's platform connects to a customer's system using an API. During a customer transaction or event, it builds up a digital footprint of a user in real time. Building that digital footprint starts with linking email addresses, phone numbers, IP addresses, device IDs, and social media accounts. Using additional datasets and pulling in customer-specific rule sets, the platform applies machine learning algorithms and generates a risk score for transactions in seconds.

As the company expanded, so did the volume of transactions and events that needed to be processed in near real-time. This growth presented opportunities to optimize performance, particularly for enterprise clients with sophisticated rule sets. While smaller customers typically used around 30 rule sets, larger enterprise clients benefited from implementing up to 1,000 customized rules. During this expansion, certain industries, such as iGaming platforms and payment providers, expressed interest in even more responsive performance and enhanced speed for fraud detection scans, all aligning with their business requirements.

SEON's engineering-led team began to look at alternative databases to raise performance levels and increase decision times. "We needed sub-second latency and we knew we had to make those decisions at massive volumes," says Adam Berkecz, vice president of architecture at SEON.

:::global-blog-cta:::

## Solution | A managed service and a rich collaboration with partners

SEON's engineers were aware of ClickHouse's open-source database and began to explore its capabilities. The column-oriented online analytic processing (OLAP) database is designed for rapid processing of huge datasets in real time. After initial discussions with ClickHouse, SEON also met with the company's founding team at [AWS re:Invent](https://reinvent.awsevents.com/), where it gained insights into the technology's capabilities and the development roadmap. 

SEON soon realized that, although the technology was a great fit, hosting and maintaining it was no simple task. It engaged with ClickHouse about running a managed service for it on AWS and working together to optimize performance. "With just a few clicks, we could spin up our cluster and start work without having to train our database administration team to use another database engine," says Berkecz. SEON's engineering team worked closely with ClickHouse, and its AWS solution architect, to optimize performance and quickly uncovered opportunities for significant improvements. 

Berkecz appreciates the team at ClickHouse. "We have a proactive relationship with ClickHouse and they are so enthusiastic about our platform," says Berkecz. "We're an engineering company and we always want to know what's going on under the hood. Whenever we tell them we need to improve things, they always listen, and they deliver."

The initial optimization project was completed in 6 months, but the teams soon found another application for the ClickHouse database. One of the more advanced fraud analytics actions that SEON performs is called a clone search. This uncovers linked fraud activity by identifying replicated customer data in multiple fraudulent accounts. The same email addresses, IP addresses, or device IDs are used by criminals to create multiple fake identities. Because of the intensive processing needed to run this analysis, scan results were asynchronous, unlike SEON's typical near real-time fraud screening. However, during an architectural review meeting, one of SEON's engineers, who was also working on the ClickHouse integration project, suggested running the workflow on the new database. Again, the results were positive.

The ClickHouse database runs on AWS. SEON uses [Amazon Elastic Compute Cloud](https://aws.amazon.com/ec2/) (Amazon EC2) for compute power and uses [Amazon Elastic Kubernetes Service](https://aws.amazon.com/eks/) (Amazon EKS) to orchestrate and manage its Amazon EC2 instances. "Amazon EKS can scale up and down so easily and even self-heal in some situations," says Berkecz.

## Outcome | Tests delivered ‘even lower latencies than expected’

The SEON and ClickHouse engineering teams were delighted with the results. For customers with simple rule sets, the performance is up to 50 times faster. Database performance for the screening part of the scan was up to 80 percent faster in some instances. And because ClickHouse’s column-oriented database compresses data efficiently, SEON has also been able to reduce storage costs by around 30 percent. 
SEON’s customers were also impressed. The company ran a load balancing test with an iGaming platform that imagined a worst-case scenario of web traffic. “The results were stellar,” says Berkecz. “That customer wanted to push us to see what we could do with massive traffic, and our system served them with even lower latencies than expected.”
Berkecz is delighted with the performance improvements. “Using AWS, for me the leading cloud provider, always gives us the confidence that we are using the right tools and the bleeding edge of technology,” says Berkecz. “AWS is obsessed with customer service. They are always there for us—once even during their account manager’s 30th birthday party. It’s great to have that safety net.”


