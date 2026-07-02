---
title: "How Jua delivers the world’s most accurate physics simulations 3x faster with ClickHouse Cloud"
date: "2026-07-01T10:14:52.161Z"
author: "ClickHouse"
category: "User stories"
excerpt: "Jua replaced a file-based forecast pipeline with ClickHouse Cloud, cutting data delivery time from one hour to 20 minutes and historical query times from hours to seconds — giving energy traders a faster edge."
---

# How Jua delivers the world’s most accurate physics simulations 3x faster with ClickHouse Cloud

## Summary

* Jua uses ClickHouse Cloud to power the world’s first physics foundation model, delivering physics simulation data to energy traders and grid operators faster than any competing platform.  
* ClickHouse Cloud cut forecast delivery time from one hour to 20 minutes, helped reduce compute costs by a third, and cut historical query times from hours to seconds.  
* Jua chose ClickHouse Cloud for its operational simplicity, cost efficiency, and ability to handle both point queries and large regional aggregations at petabyte scale.

[Jua](https://jua.ai/) is a Zurich-based physics AI company with an ambitious vision: to simulate the entire universe. Its architecture combines a world model that learns the governing physics of any system purely from observational data, and a continuous learning agent that trains inside that world model and optimizes toward whatever objective a customer defines.

The company started with the atmosphere, arguably the hardest proving ground there is. Predicting it requires learning multiple branches of physics simultaneously, including fluid dynamics, thermodynamics, radiative transfer, and atmospheric chemistry.

![jua_jun2026_image2.png](uploads/jua_jun2026_image2_dc4b92b36b.png)

[EPT-2](https://docs.jua.ai/models-and-products/jua-models/ept-2), Jua's physics foundation model, does exactly that. It holds the global state of the art in atmospheric prediction, outperforming Google DeepMind, Microsoft, and Nvidia in independent benchmarks. And because it learns actual physics rather than statistical patterns, it transfers to other fluid dynamics problems like airfoil simulations and wind tunnel scenarios with minimal fine-tuning.

Weather forecasting for energy traders is the first commercial application of that architecture. As renewables add volatility to the grid, accurate forecasts have never mattered more. "If suddenly a cloud appears where you didn't expect it, your solar generation might drop for a small period of time, which puts a lot of strain on the grid," says engineering lead Mark Frey. "With more accurate forecasts, you can guarantee a more stable power grid."

But building the world's first universal physics simulation engine is only half the challenge. Getting that data into customers' hands faster than anyone else requires an entirely different kind of infrastructure. That's where ClickHouse comes in.

We caught up with Mark to learn about the data challenges behind the platform, why they chose [ClickHouse Cloud](https://clickhouse.com/cloud), and how speed has become a core part of Jua's competitive edge.

## When 10 PB becomes 1 - a story of compression

"We generate a lot of data per day," Mark says. Each forecast run ingests data from multiple models (EPT-2, open-source models, classical numerical models from European weather agencies), amounting to several hundred gigabytes per model. With multiple forecast runs per day, that adds up to around four terabytes of new data ingested daily, for a total compressed dataset of around 1 petabyte, or over 10-12 petabytes uncompressed.

![jua_jun2026_image1.png](https://clickhouse.com/uploads/jua_jun2026_image1_9ca605ee41.png)

For a long time, the industry has handled data like this the traditional way, using file-based storage, with atmospheric data saved as large arrays and dumped to disk. It works at a basic level, but it creates a bottleneck between generating a forecast and making it accessible. For Jua, getting data from files to customers meant managing pre-fetching, caching to API servers, and manually notifying customers when data was ready.

"We observed that it adds a lot of overhead and complexity to make that data readily available for customers to query," Mark says. "If you have a forecast you can generate in 20 minutes but it takes an hour for people to access it, you don't really gain much from being faster."

In Jua's market, that matters enormously. Every trader and grid operator is working from weather forecasts. The advantage goes to whoever has the most accurate data, updated most frequently, available the soonest. "Time really matters," Mark says. "If you have the data before others do, then you have an edge."

## Choosing ClickHouse Cloud

In their old setup, Jua worked extensively with Zarr files, experimenting with different architectures and pre-fetching approaches across various backends. But as Mark says, "It quickly became clear that for a small team, this is too much maintenance."

They looked at other options, including TileDB, before ultimately landing on ClickHouse. They were swayed in part by the [user stories](https://clickhouse.com/user-stories) they read on ClickHouse's blog, including [how Tesla built a quadrillion-scale observability platform](https://clickhouse.com/blog/how-tesla-built-quadrillion-scale-observability-platform-on-clickhouse). "That was a big plus for us, because we had just crossed the petabyte scale on our old storage backend," Mark says.

The initial test was straightforward. They stood up the open-source version locally and ran it against their real data. "What was really nice about ClickHouse was that we could just try it out," Mark says. It handled the workload well. That was enough to move forward.

When it came to deployment, Jua weighed self-hosting against [ClickHouse Cloud](https://clickhouse.com/cloud). With a team of 10 engineers, the operational burden of self-hosting wasn't realistic or appealing. "We don't have the resources to have a dedicated team just making sure our ClickHouse cluster is up and running," Mark says.

ClickHouse Cloud's [separation of storage and compute](https://clickhouse.com/docs/guides/separation-storage-compute) was also a deciding factor. "If we had to replicate all the data, storage costs would increase significantly, and the setup would be much more complicated," Mark says. "This would again result in more maintenance overhead."

Ultimately, it was cost and operational simplicity that sold them on ClickHouse Cloud. As Mark puts it, "We realized pretty quickly that ClickHouse Cloud is actually not that expensive, especially given that we have no development costs ourselves. The time to get started was short, which was a big plus, and the maintenance effort is minimal."

## Faster forecasts, lower costs

They saw the impact right away. By replacing the file-based pipeline with ClickHouse, Jua eliminated much of the manual overhead that had been slowing down data delivery. "It was roughly an hour from when we started a forecast until data was available," Mark says. "Now, because it's real-time, our upload overhead is about 20 seconds. So for our flagship model, EPT-2, we've cut delivery time from an hour to 20 minutes."

The speed gains had a knock-on effect on infrastructure costs, too. Faster uploads meant the GPU instances running the output computation could be freed up sooner. "We're now about a third faster than before," Mark says, "which translates to roughly a third in cost savings."

For historical queries, the improvement was even more dramatic. Before ClickHouse, a user requesting two years of data for a single location meant manually trawling through hundreds of files, a process that could take hours. "Now, with ClickHouse, it's a matter of seconds," Mark says. "Customers can do it on demand, so we don't have to do any manual labor."

Mark was also surprised by how well ClickHouse handles the full range of query types Jua needs. Physics simulation data, he explains, tends to be queried in two very different ways: specific lookups and large regional aggregations. File-based systems typically favor one over the other, but ClickHouse handles both. "It handles all the caching for us," he says, "and it allows both point queries like 'what's the forecast for Zurich?' as well as broader requests like 'give me all the data for Germany.' On top of that, what's super helpful for us, we can also do analytics, like 'what's the maximum wind speed in Austria for the next week?'"

## What's next for Jua and ClickHouse

Jua's ClickHouse journey is just getting started. The team plans to add more models, more features, and more historical data, steps that will expand Jua's physics simulation capabilities into new domains and sectors like insurance and agriculture. ClickHouse now holds actual weather observations going back to 1990, enabling queries like "what are the top 10 sunniest places in Germany?" that would have been impractical before.

Mark is also keeping an eye on ClickHouse's observability offerings, including [ClickStack](https://clickhouse.com/clickstack) and its recent [acquisition of Langfuse](https://clickhouse.com/blog/clickhouse-acquires-langfuse-open-source-llm-observability). As the platform grows, having deeper visibility into how the stack is performing becomes increasingly important. "ClickHouse's offerings there are great, so we'll probably be looking into those features," he says.

When it comes to building a competitive edge, the proof is already there. The gap between Jua and other providers goes beyond model accuracy; it's in how fast that data reaches the people who need it. "We observe this ourselves when we have to interact with other providers," Mark says. "Our API is just much, much faster, which comes down to the backend."

---

## Get started today

Interested in seeing how ClickHouse works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-1149-get-started-today-sign-up&utm_blogctaid=1149)

---