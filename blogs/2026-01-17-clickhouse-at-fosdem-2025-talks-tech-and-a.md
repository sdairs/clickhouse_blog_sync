---
title: "ClickHouse at FOSDEM 2025: talks, tech, and a community dinner"
date: "2025-02-25T15:08:26.398Z"
author: "Tyler Hannan"
category: "Community"
excerpt: "This year, ClickHouse made a strong showing at FOSDEM 2025, with several team members traveling to Belgium and multiple talks covering everything from powerful new JSON data types to the challenges of fuzzing databases."
---

# ClickHouse at FOSDEM 2025: talks, tech, and a community dinner

This year, ClickHouse made a strong showing at FOSDEM 2025, with several team members traveling to Belgium and multiple talks covering everything from powerful new JSON data types to the challenges of fuzzing databases. If you weren’t able to attend (or just want a recap), here’s what went down in Brussels.

## What is FOSDEM?

For those unfamiliar, **FOSDEM** (Free and Open Source Developers' European Meeting) is one of the biggest open-source conferences in the world. Every year, thousands of developers, engineers, and open-source enthusiasts gather in Brussels to share knowledge, showcase projects, and engage in deep technical discussions. It's a place where open-source software meets innovation, and where deep-dive technical talks are the norm.

And this year, ClickHouse was **well represented**.

## The ClickHouse Talks

### How We Built a New Powerful JSON Data Type for ClickHouse

JSON support is a hot topic for ClickHouse users, and at FOSDEM, we shared details about the **new JSON data type** we built. This talk covered **why** we introduced it, how it **differs from traditional JSON handling**, and what kind of performance benefits users can expect. If you're working with semi-structured data at scale, this was a must-watch.

**Speaker:** Robert Schulze

**Abstract:** JSON has become the lingua franca for handling semi-structured and unstructured data in modern data systems. Whether it’s in logging and observability scenarios, real-time data streaming, mobile app storage, or machine learning pipelines, JSON’s flexible structure makes it the go-to format for capturing and transmitting data across distributed systems.

At ClickHouse, we’ve long recognized the importance of seamless JSON support. But as simple as JSON seems, leveraging it effectively at scale presents unique challenges. In this talk we will discuss how we built a new powerful JSON data type for ClickHouse with true column-oriented storage, support for dynamically changing data structure and ability to query individual JSON paths really fast.

Links related to the topic:

* [RFC: Semistructured Columns #54864](https://github.com/ClickHouse/ClickHouse/issues/54864)
* [Implement Variant data type #58047](https://github.com/ClickHouse/ClickHouse/pull/58047)
* [Implement Dynamic data type #63058](https://github.com/ClickHouse/ClickHouse/pull/63058)
* [Implement new JSON data type. #66444](https://github.com/ClickHouse/ClickHouse/pull/66444)

<iframe width="768" height="432" src="https://www.youtube.com/embed/JohjugQedSk?si=6jBEdh9MHSoAP7yA" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

### Fuzzing Databases is Difficult

Database reliability and security are always important priorities, and fuzz testing is one way to uncover hidden bugs. But as it turns out, **fuzzing databases is hard**. This talk dove into the complexities of fuzz testing, why traditional approaches don't always work well for databases, and what strategies can improve effectiveness. If you’re interested in database internals or security, this one was for you.

**Speaker:** Pedro Ferreira 

**Abstract:** After fuzzing databases for the last 3 years, I learned that simple design decisions on a fuzzer impact on the issues it can ever find. In this talk I would to address some of those decisions. As an example, I would to discuss about the design of BuzzHouse, a new database fuzzer to test ClickHouse.

Links related to the topic: 
[First iteration of Buzzhouse #71085
](https://github.com/ClickHouse/ClickHouse/pull/71085)

<iframe width="768" height="432" src="https://www.youtube.com/embed/CW4Ntdtp7lg?si=8zlyBIg8xzXiecCF" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

### ** rDNS Map: The Internet in Your Hands**

Reverse DNS (rDNS) is an often-overlooked but powerful tool for understanding the structure of the internet. This talk explored how we can **map out rDNS data** at scale and why it's useful for network monitoring, security research, and even performance optimization.

**Speaker:** Alexey Milovidov

**Abstract:** I've created an rDNS map, available at https://reversedns.space/, and I want to tell you how. It was not hard to do, but there was a lot of unusual and amusing stuff in the process.

<iframe width="768" height="432" src="https://www.youtube.com/embed/0hDOr9Pp1-4?si=ppV4bjsQUqxwz6b8" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

## Wrapping Up with a Community Dinner

Of course, no ClickHouse event is complete without some time with the community. After a full day of talks, we gathered with our community members for dinner and drinks in Brussels. It was a chance to meet users, discuss database internals, and share ideas over great food and drinks. If you were there, thanks for joining us! If not, we hope to see you at the next one. 

In the meantime, feel free to join us on [Slack](https://clickhouse.com/slack) or give the [ClickHouse repository](https://github.com/ClickHouse/clickhouse) a star.

## Some Photos

![FOSDEM_Robert.png](https://clickhouse.com/uploads/FOSDEM_Robert_7ae18824d8.png)

![FOSDEM_Pedro.png](https://clickhouse.com/uploads/FOSDEM_Pedro_281eabed62.png)

![FOSDEM_Alexey.png](https://clickhouse.com/uploads/FOSDEM_Alexey_f71f4433fb.png)

![FOSDEM_Room_Full.png](https://clickhouse.com/uploads/FOSDEM_Room_Full_42d27aab9b.png)

![FOSDEM_Dinner_Venue.jpg](https://clickhouse.com/uploads/FOSDEM_Dinner_Venue_2d60dbbefb.jpg)

![FOSDEM_Dinner_Full.jpg](https://clickhouse.com/uploads/FOSDEM_Dinner_Full_bbae49afa6.jpg)
