---
title: "How Physical Intelligence unified its robotics data stack with Postgres managed by ClickHouse"
date: "2026-08-07T04:12:00.818Z"
category: "User stories"
excerpt: "Physical Intelligence runs both its OLAP and OLTP workloads on ClickHouse managed Postgres and ClickHouse Cloud"
---

# How Physical Intelligence unified its robotics data stack with Postgres managed by ClickHouse

## Summary

* [Physical Intelligence](https://www.pi.website/) builds robotics foundation models and uses [Postgres managed by ClickHouse](https://clickhouse.com/cloud/postgres) to combine OLAP and OLTP workloads in one unified data stack.
* They migrated to ClickHouse Cloud after their previous single RDS Postgres instance couldn’t handle both their transactional and high-cardinality analytical workloads.
* They can now explore their data faster and more easily, with rows growing from the 10 to 100 billion row range.

[Watch on YouTube](https://youtube.com/watch?v=4CaEBYbthFc)

## Introduction
[00:04] Host: Yeah, with that I think I'll pass it over to Physical Intelligence. We'll talk about, you know, their use case and how they are finding value. This is going to be the most fun part. So yeah, thank you so much.

[00:18] Karan: Yeah, hey guys. I'm Karan, and Chandra and I are going to be presenting about our use case with ClickHouse. We work at Physical Intelligence. For those of you who don't know, Physical Intelligence is a company that does robotics. So we're very much a research lab — we are pushing frontier models in robotics.

[00:36] And as Sai said before, basically our mission statement is bringing general purpose AI into the physical world. That's what Physical Intelligence does — which is a very broad mission statement, so I'll get into specifics.

[00:50] But to roughly go through what this presentation is going to look like: I'll talk about what Physical Intelligence is, what we do, and how we built our foundation model. And then one of the most important parts of building the foundation model is our data — and that's why, you know, ClickHouse has come into play. ClickHouse and Postgres actually, because we have a variety of data and they serve both those use cases really well.

## Three axes of generalization
[01:11] Karan: So yeah, what does it mean to bring general purpose AI into the physical world? So we divided roughly into like three categories. And this slide is not super illustrative, but what we're really trying to say is that we care about three axes of generalization.

[01:26] So the first axis is we do generalization across environments — and I actually have a video that will present that. And what that means is we want a foundation model that can run on a robot in any kind of environment, you know, whether it's your home or whether it's a factory floor.

[01:44] We also want to do foundation models that can run on any kind of embodiment. So as you can see, there's different kinds of robots — there's like a single-arm robot, multi-arm robot, robots with legs, robots with wheels. And finally, a robot brain that can do any kind of tasks. So this is laundry, folding clothes, making coffee.

[02:06] And if we can achieve these three axes of generalization, we pretty much have a foundation model that can do anything in the physical world. So this is what we're going for.

## Foundation models for robotics
[02:16] Karan: So at the core of it — I keep mentioning foundation models. I'm not going to go into exactly what a foundation model is, but what we know is that in the last five years or so there's been an explosion in terms of foundation models in every space. They're doing, clearly, like all of our jobs actually. There's video generation models. There's models that are trained specifically for maths and physics problems. Robotics foundation models are the new frontier.

[02:45] And at the core of it, you know, classical robotics can be broken down into multiple different aspects. So there's planning and reasoning, which is, you know, you can use your classical methods such as like A-star to search a space. You can have SLAM to detect objects and know where you are. There's object recognition — your classic CV methods. There's low-level control to actually control your robots.

[03:07] And classical robotics has gotten us pretty far, but at the core of it, you know, it's not a solved problem. And so a foundation model for robotics is something that we hope will solve this problem, in the sense that, you know, unlike classical methods, we're trying to build a robot brain from scratch — so very similar to a large language model.

[03:30] And what this brain does is basically, not unlike a human, it'll take in data from different sources and then execute actions on a robot. And to do that, we need a lot — a lot — of data.

[03:44] And what I can do is I can show you a quick example of how this works. We had a latest release a few months ago called π0.7, which is our 0.7 release for our foundation model.

## π0.7 demo video
[03:55] Video: Introducing π0.7, a steerable model with emergent capabilities. It's one model that can do many tasks in many environments on many robots. Typically, each of these tasks would require fine-tuning a specialist model. π0.7 can do them right out of the box.

[04:31] Video: What we found is that by training the model on enough data and then prompting it in the right way, we can maintain great performance without any specialized fine-tuning.

[05:22] Video: In addition to language, we've added the ability to prompt the model with visual sub-goals, which we generate using a lightweight world model. It predicts what success looks like, and then shows the robot visually what to do. This lets us better guide π0.7 and chain together skills in entirely new ways.

[05:42] Video: We've also seen other new capabilities emerge. For example, we can collect laundry folding data on one robot, and then ask π0.7 to perform the exact same task on a completely different embodiment. Here we ask the much larger bimanual UR5e to fold a t-shirt. We've never collected folding data on this embodiment, so the motions that the arms need to make are completely different from what's in the training data. We've seen this cross-embodiment transfer work across very different robots and many different tasks.

[06:19] Video: Finally, we decided to see what we could do without collecting any task-specific data at all. Because π0.7 is so steerable, we've been able to coach it with language commands to do entirely unexpected tasks — like air-frying a sweet potato.

[06:52] Video: By learning from this human coaching, the robot can later do the task entirely on its own.

[07:04] Video: We're really excited about having one model that is so good at so many things. We can try more tasks than ever before, and as a result we're seeing some really cool emergent capabilities. It feels like a big step towards having robots that can do anything you tell them to. Thank you.

## How the model learns — and why data matters
[07:56] Karan: So yeah, just getting back to the point — which is, you know, a lot of these foundation models, the way they work. And here's a little sneak peek: this is from our paper, this is online, open source. Again, we very much believe in the open source community, so we open source all of our models.

[08:11] But at the core of it, the way this works is, you know, as a kid you've taken in a lot of information. You've taken visual information, such as like what rooms you're in, where you've been, and you are told about different objects across different tasks. Like, once you know what a fruit looks like, you know what all fruit look like.

[08:36] And similarly, that's what we're trying to achieve with robots — granted that vision language models are much more sample-inefficient than human beings, but we're getting there very fast.

[08:46] So the way this really works is that we need a lot of data. And there's different kinds of data. You get robot data, you get data that's fed into the core of a vision language action model. So there's a lot of data from the web — so, you know, videos or images from the web with labels. Ego-centric human data, which is humans doing tasks with a little camera on their head, and that translating to robot.

[09:16] And then all of this goes into, at the core of it, a vision language action model — which you can think of as just an LLM with a vision encoder and an action decoder. And then finally you run inference, and we can achieve all of the things that we saw in the video.

[09:33] And I do want to emphasize the data aspect a lot here, because as I said, we need a lot of types of diverse data for the model to work. And we've shown, as you saw in the video, that if you give it enough diverse data it can generalize to a new dataset — data from different kinds of embodiments. So in this case, this is the UR5e.

## Three kinds of data
[10:01] Karan: But the data divides into roughly three aspects. This presentation is focused on the last two. So there's raw data, transactional data, and then the metadata and annotations. And all of them serve a little bit of a different purpose.

[10:14] Raw data. So raw data is the actual data that the model consumes during training. And this is the petabyte-scale data that you need to train any large language model. Most of this data is append-only. It's heavily based on random reads, because when you're training you need to generate a random seed and then train on this data. We do mostly no post-processing on this data — we take the data as is. And then the storage obviously needs to be cheap, because it's petabyte scale. So that's a whole different challenge in itself.

[10:43] Transactional data. Then there's the two other kinds of data. One is transactional data. This is your day-to-day "we need to run a company" data — how we're collecting all of the annotations, the actual how of the company, how that works. These are the things that require ACID guarantees. So if you ask someone to label your data, we need to make sure that there's no double labeling, there's some sort of queuing. And all of that can roughly fit in less than 100 million rows. We, of course, need strong consistency for this, and SQL-style querying is preferred.

[11:12] Metadata and annotations. And then the last kind of data we have is metadata and annotations. And this is also used in training a lot. The cardinality is very high, but the size is pretty low. And so this is where we get into the 10 to 100 billion row range. This is where eventual consistency is OK — you don't really need all of your annotations to be transactional. We use this for long-running filters and GROUP BY queries. Researchers are actively traversing this data to figure out whether some kind of data has been collected, what data we need to annotate, what data we don't need to annotate.

[11:53] And as a result, to support the transactional data and the metadata-plus-annotation use case, we need two different kinds of engines: one is Postgres and one is ClickHouse. And so, you know, I'll give it to Chandra to talk more about how we handle that.

## Where we started: a single RDS database
[12:07] Chandra: Yeah, thanks, Karan. Before I go further into how we collected this data, and how do we separate that, and what we do with this data — I want to give a quick overview of where we were at the start of this year and what are the solutions that we were looking at.

[12:22] At the start of this year we had like a single RDS database where researchers would query to get whatever information they want. And like, we had an explosion somewhere around like Q1, and it was creating all sorts of random queries, in addition to like ambitious queries that researchers were asking.

[12:47] We essentially were running into scaling issues with our existing system. That's when we were trying to migrate away from Postgres, and we were like, okay, let's directly go to ClickHouse. And then we started on that — just when we were about to start on that, we saw the [Postgres-to-ClickHouse offering](https://clickhouse.com/cloud/postgres). That's when we decided, instead of doing a quick cutover, we would consider this.

[13:09] JSONB everywhere. Another couple of things that I want to add — what we were doing at the start of the year was, like, we had JSONB everywhere. Essentially, like, whenever somebody wants to add a new data type… I don't know if people know about annotations. Annotations are, essentially, you are telling the robot what a specific thing is, and this can come in various shapes and forms. So whenever there's a new shape and form, people would be like, "okay, I'll just put this in JSONB, nobody's looking at it, I will query" — and then, boom, when you are querying, you have all sorts of issues.

## Why ClickHouse
[13:43] Chandra: So we ended up then choosing ClickHouse. Why ClickHouse? One of the most common patterns with these annotations is, like, people insert this data and then later at some point down the line they query on those data. So inserts have to be fast, whereas they can tolerate some amount of latency as far as the reads are concerned. So when we were exploring, ReplacingMergeTree turned out to be like a really perfect fit for that specific use case where we want to scale.

[14:10] And the other problem I was talking about, which is JSONB everywhere — again, we essentially expanded it, made it columnar. And ClickHouse is really great for sparse datasets, and we also got added safety on top of all of this.

[14:27] Then for all the queries which are essentially adding a lot of load onto our database, we ended up creating materialized views, that helped us with, one, making the queries faster, [and two,] reducing the load on the database.

## The migration
[14:43] Chandra: Talking a little bit more about how we went about the migration: we essentially leveraged — Sai and Kaushik — that's the first step. But then we used ClickPipes, which I was a little bit skeptical about when we started, because, oh, like, we haven't tested this out. But then it just worked out of the box when we started. And then we also did some amount of de-risking by, like, copying this dataset, running these queries, making sure it works. And last, we had this compute and storage separation that helped quite a bit.

[15:26] So once we had that — now we have two different worlds, one for OLTP, one for OLAP, all on a single database essentially. Like, most of our operational workloads go into our Postgres, and then we have set up ClickPipes which end up in our data lake, essentially on the OLAP side. We now have all of our annotations through to telemetry, all of them ending up in a single place.

[15:58] This also gave us added benefit where people started building new sorts of applications that they were not thinking about before, because they have all of their datasets in one place. We could support, like I said, all sorts of weird queries that people were asking — like, "hey, for this particular robot, did we collect this kind of data in that particular scene? Can we get all of that data?"

[16:27] And I don't have to really go deep into the NVMe part. Essentially, once we migrated here, there are a class of issues that we were seeing before that were completely gone. And finally, we took this as an opportunity to move away, to move into at least managed migrations, which was really seamless for us.

## Tuning and scaling
[16:50] Chandra: And finally, once we migrated here, we also started thinking about what kind of tuning to do, how we can scale this platform well. And some of the things that ClickHouse provides out of the box helped us — which is isolating read and write queries. Then for all of our batch workloads, we started using PgBouncer, and kind of preventing DDoS onto our main database. And then I talked about materialized views, which is essentially purpose-built views for various use cases.

[17:27] [I'll let Karan talk about] how we were leveraging that in one of our applications. Karan?

## The go/data app — "has the robot ever seen an air fryer?"
[17:32] Karan: So I think the one cool application that I wanted to talk about, that we're using this a lot for, is something that we actually built a few weeks ago — a few months ago — which is a way to explore our data.

[17:44] And the question that we wanted to answer, as Chandra pointed out, is — if you saw the video, one of the hallmark demos in that video was the air fryer. Which is like, hey, can the robot do an air fryer task which it has never seen before in any dataset? But none of us knew whether that data existed in the dataset. And to make a claim that this robot is doing this task without having seen that data, we needed to be sure. But given the amount of data that we have, answering that question was very hard without something that was extremely efficient to query.

[18:17] And so a lot of the questions were going on, it's like, "hey, has the robot seen air fryer data?" Like, we don't know. And it took us like three weeks to figure out — late last year or early this year — whether we actually had air fryer data in the robot data.

[18:30] And to do that — before we moved to Postgres and ClickHouse, we were just on RDS — and to do that, we had to write multi-table joins that took multiple days to run. Because it's not just about querying whether this kind of episode exists, but it's also about querying whether this specific word exists anywhere in the dataset. Because it's possible that "air fryer" might be mistyped — that would be a dash "-fryer" or an underscore "_fryer".

[18:55] But now we built this app — we call it go/data, as go-links internally. We basically have all of our transactional data in Postgres, and we dump it all into ClickHouse using ClickPipes. It's pretty seamless — we don't have to really do anything, we just clicked a button and everything started to work. And then once we have that, we have an application that actually [uses] materialized views to let anybody search anything across all of our data. And this is an extremely powerful thing to give to our researchers.

[19:24] It's just a data dashboard, as you can imagine. You can build a little SQL query which runs straight against SQL — this is to make it easy for researchers to write queries, we have all the drop-downs populated. But the more interesting feature here is the chat. And the chat, at the core of it, is you can type in anything — like, for example, "successful folding episodes", or you can type in "give me episodes with air fryer in it" with any misspelling you want. And we automatically — we obviously have an agent running in the background that does a lot of queries against Postgres and ClickHouse depending on what kind of query it is, and then figures out which tables to query and how to query it, and then presents you the results.

[20:07] Unfortunately, I can't go super deep into this — this is pretty proprietary. But this would not have been possible without the combination of Postgres, ClickPipes and ClickHouse. So this is a very important unlock for us.

## Q&A — full-text indexing
[20:21] Karan: Yeah, so we do use a full-text index. We use — I think exactly which index we use… for full-text search. But we do use a full-text search index, and we actually have multiple indices. And depending on the kind of query you do, we choose which exact index, which query to do to hit that index.

## Bonus: telemetry
[20:44] Karan: Cool. And then a bonus, which is our telemetry. And this is something that actually we didn't cover here, but it's very important for us — because this is actually what [unclear] easy to use, most folks know how to use. And then ClickHouse is extremely fast for telemetry.

[21:08] And so we started off with actually migrating all of our telemetry to ClickHouse. And we use that in combination with ClickStack and Grafana to make this possible. So it is kind of cool that there is a single platform that supports telemetry and OLAP and OLTP. And it just makes all that much easier. Yeah, that's it.

[21:30] Oh, well — here's a 10,000-foot view of all that we just talked about, which is our stack: what runs on our transactional workloads and what runs on our analytic workloads. We have Postgres and it's auto-replicated into ClickHouse. This is what Sai and Kaushik were talking about before.

---

## Get started today

Interested in seeing how ClickHouse works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-1481-get-started-today-sign-up&utm_blogctaid=1481)

---