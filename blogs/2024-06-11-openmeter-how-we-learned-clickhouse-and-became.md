---
title: "OpenMeter - How we learned ClickHouse and became certified ClickHouse Developers"
date: "2024-06-11T13:13:55.724Z"
author: "Márk Sági-Kazár"
category: "Engineering"
excerpt: "The team at OpenMeter offer tips and advice on how to learn ClickHouse and become a certified Clickhouse developer."
---

# OpenMeter - How we learned ClickHouse and became certified ClickHouse Developers

ClickHouse is at the heart of [OpenMeter](https://openmeter.io/)'s architecture, serving our customers' real-time usage metering needs with remarkable efficiency and reliability. Although we've been leveraging ClickHouse for a while, I only recently had the time to complete the official ClickHouse Developer training.

I'd like to share my experience completing the training and becoming a certified ClickHouse Developer in this post.

## Why Learn ClickHouse?

ClickHouse is an excellent fit for real-time data and analytics. It is one of the fastest-growing databases, powering production use cases at Cloudflare, Netflix, OpenMeter, and many more. Even if you don't have a use case today, it's worth learning ClickHouse to familiarize yourself with a columnar database.

Most software engineers use some database during their careers. Often, it's a relational database management system (RDBMS) like Postgres, a document store like MongoDB, or, occasionally, a graph database. ClickHouse, as a columnar database, stands out from all of these.

While most databases are designed to model data, store, and manage state, ClickHouse's real power lies in its ability to analyze large datasets quickly. In today's fast-paced, data-driven world, businesses base their decisions on all the information they accumulate.

So, even if you don't need ClickHouse today and never will in your current job, you will likely encounter use cases where it excels. Even if ClickHouse is not your solution, it is an excellent model for effectively teaching you how to work with large datasets. Learning ClickHouse can also broaden your understanding of database technologies and enhance your data handling skills, preparing you for a wide range of challenges in data analytics.

If that doesn't convince you, I have one last argument: ClickHouse is fun. It's easy to run locally, load in some data, and run analytical queries against it.

I highly recommend you give it a shot.

## How not to learn ClickHouse?

When I first encountered ClickHouse, I thought, "SQL, but column-oriented. Gotcha…" Which put me on the wrong course first. While the familiar syntax helps initially, there are fundamental differences between ClickHouse and relational databases like Postgres. It's important to keep an open mind about these differences and prepare yourself to redefine some of the concepts you've learned and understood in other database management systems.

For example, primary keys, indices, and table alterations work differently in ClickHouse. Understanding these nuances is crucial for leveraging ClickHouse's full potential.

With that out, let's move on to how to get started with ClickHouse.

## How to get started?

The ClickHouse team offers several resources to help you learn ClickHouse effectively.

The obvious starting point is the documentation, where you can read about the basic concepts. The documentation is excellent, and that's where I began my journey with ClickHouse. [ClickHouse training](https://clickhouse.com/learn) is another great resource I can't recommend enough.

ClickHouse offers two types of training:

1. **On-Demand Training**: This allows you to learn at your own pace.
2. **Instructor-Based, Live Training**: This provides a more interactive learning experience with a live instructor.

Both training options are free at the time of this writing.

Choose the one that better suits your learning style. I prefer tinkering with what I'm learning and taking the time to experiment, so I opted for the on-demand training.

The on-demand course consists of 12 modules. It starts by explaining the basic concepts of ClickHouse and walks you through everything you need to become an effective user. Each module includes a 15 to 30-minute video lesson, followed by one or two hands-on exercises, each taking about an hour.

It's been a while since I completed a training program like this, mostly because I often find it hard to stay engaged. However, I thoroughly enjoyed the ClickHouse training. It was easy to follow, and the explanations and examples provided by the instructor were beneficial.

I recommend starting by exploring the documentation and then checking out the training. Twelve hours is not that much, especially given its value.

## Tips for completing the training

### Use ClickHouse Cloud

The instructor recommends using [ClickHouse Cloud](https://clickhouse.cloud/) throughout the training, and I highly recommend the same. Although running ClickHouse locally is super easy, ClickHouse Cloud provides a few benefits that come in handy during the training.

First, the SQL console in ClickHouse Cloud is superior to the open-source version. While you can use the CLI or any other GUI client, I found using the one in the Cloud easier. It also allows you to save your queries and revisit them later.

Some modules, especially those explaining sharding and replication, require more complex setups. While these setups are not impossible to achieve locally, they are probably not something you want to spend time on during your initial learning phase. Using the cloud, you get all that functionality without any additional effort.

ClickHouse offers a free trial that is more than enough to complete the training, so it doesn't cost you anything to get started.

### The documentation is your friend

The [documentation](https://clickhouse.com/docs) was excellent and helpful during the training in multiple ways.

First, it provides additional information on the topics discussed in the training modules. After reviewing the documentation and reading the relevant sections, I found they were helpful in each lesson. Although the instructor gave excellent explanations, the additional context helped me better understand how ClickHouse works.

The documentation also proved helpful during the hands-on labs. I'm slow at learning new syntaxes, so I kept the SQL reference open in a tab to quickly switch to it and search for the keyword or the function I needed to use.

### Take a break from time to time

It might be tempting to grind through all twelve modules in one go. I did that with a few modules, which later proved wrong.

Give the new information time to settle in your mind, especially when completing modules explaining familiar concepts (like primary keys) that work differently in ClickHouse.

Take a few minutes or even an hour between modules. It's a marathon, not a sprint.

## Taking the certification exam

ClickHouse [recently announced](https://clickhouse.com/blog/first-official-clickhouse-certification) its first certification exam for the ClickHouse Developer course days after I completed it, so naturally, I also took the exam.

Overall, the exam is not challenging. The tasks I had the most difficulty with required analytical queries, mainly because ClickHouse is still relatively new to me. It has many functions you can't find in other SQL databases, and I'm not great at remembering names.

Here are some tips that may help you get through the exam successfully.

### Be comfortable with the documentation

Unless your superpower is memorizing function definitions and syntax, consider becoming comfortable with navigating the documentation. Knowing where to look for a specific function is often faster than using the search. It certainly isn't mine, so I usually refer to the documentation during the exam.

### Go through the lab solutions one more time

It shouldn't come as a surprise, but the exam relies heavily on what you've learned during the course. Although the examples and datasets are different, the types of questions are very similar to the lab exercises. So, even if you don't go through the labs again as practice, check out the code samples to prepare for what to expect during the exam.

### Read through all the tasks first

This may feel cliché, but I strongly recommend reading through all the tasks and solving the easy ones first. Doing so will allow you to spend more time on the difficult ones (yes, some are more difficult than others). This approach also helps reduce pressure if you're short on time.

## Conclusion

These tips will help you succeed in learning ClickHouse (and completing the certification). Most importantly, I hope you will have as much fun as I did.









