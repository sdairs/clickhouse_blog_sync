---
title: "A Story of Open-source GitHub Activity using ClickHouse + Grafana"
date: "2023-02-10T09:56:01.348Z"
author: "The ClickHouse Team"
category: "Engineering"
excerpt: "Read about, and watch our recent webinar on how ClickHouse and Grafana can be used to build beautiful real-time dashboards, with a demo taking Grafana users down memory lane and 10 years since the first commit."
---

# A Story of Open-source GitHub Activity using ClickHouse + Grafana

<iframe width="764" height="429" src="https://www.youtube.com/embed/fXC6vzNc7g0" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>
<p>&nbsp;</p>

We recently [delivered a webinar](https://www.youtube.com/watch?v=fXC6vzNc7g0) with our friends at Grafana, introducing the [official ClickHouse Grafana plugin](https://grafana.com/grafana/plugins/grafana-clickhouse-datasource/). During this webinar, we presented the plugin's history and the reasons behind the design choices and plans for the future.

Like any good webinar, however, we wanted to present a demo of the technology itself. Coincidentally, we were presenting that webinar exactly 10 years since the first Git commit to Grafana. Coupled with some recent frustration over limited GitHub analytics, we decided to present an analysis of the Grafana repository.

In this blog post, we review our findings and hopefully give our readers the tools to reproduce the same work on their projects.

## A source of frustration

Whenever looking at a new GitHub project, as engineers, we often turn to GitHub analytics - officially known as Pulse. At this point, our frustration typically begins, and we’re presented with some pretty underwhelming analytics.

![github_analytics_1.png](https://clickhouse.com/uploads/github_analytics_1_c6ebb0cf85.png)
![github_analytics_2.png](https://clickhouse.com/uploads/github_analytics_2_a148685719.png)

Given the importance of the date, with it being 10 years since the first commit, we decided to see if we could do better. What better tools to solve the task than the world’s leading OSS OLAP database and data visualization tool?!

## Finding the data

For any good analysis, we need good data. Fortunately for us, the data we need is either public or can be generated.

GitHub publishes the full event history of all public repositories through a wonderful project [GH Archive](https://www.gharchive.org/). This represents a fairly small dataset for ClickHouse, and we’ve already documented [thoroughly how to load and analyze this](https://ghe.clickhouse.tech/#how-this-dataset-is-created). With all pull requests, issues, stars, forks, watches & comments for every repository on GitHub since the beginning of 2011, and over 5.5 billion events, it provides an excellent “background” dataset for our analysis. Note that this dataset is also available in [play.clickhouse.com](https://sql.clickhouse.com?query_id=JAUTYJJXBOSATPJD9B624X) for you to query for free. Alternatively, [load this dataset ](https://ghe.clickhouse.tech/#download-the-dataset)into ClickHouse yourself. 

While the above dataset provides us with an overview of GitHub Projects, it doesn’t provide commit histories. Admittedly, this would be a much larger dataset. However, using the [git-import ](https://clickhouse.com/docs/en/getting-started/example-datasets/github#generating-the-data)tool distributed with ClickHouse, we can easily generate the full commit history of a repository with a single command. This produces three files of increasing granularity: a file with a row for every commit, a file with a row per file change, and finally, a line-by-line change history.  We had already used this same tool to do an analysis on our own ClickHouse repository and documented the steps [here](https://clickhouse.com/docs/en/getting-started/example-datasets/github#downloading-and-inserting-the-data).

While all of the datasets used in our demo are public and can be downloaded or generated, we’ve also assembled [some simple instructions](https://gist.github.com/gingerwizard/1c03af6be54b56fe0f11871278555cfd) to make reproducing this demo a little easier. Our dashboard is also available in [Grafana’s public catalog](https://grafana.com/grafana/dashboards/18065). 

## Building the visualizations

Armed with both datasets, building visualizations became straightforward. Our final dashboard aimed to use both datasets, with a list of possible questions already documented - [here](https://ghe.clickhouse.tech/#let-s-play-with-the-data) and [here](https://clickhouse.com/docs/en/getting-started/example-datasets/github#queries). This left us simply needing to select those questions of interest and use the appropriate Grafana syntax to ensure time filters were respected before choosing a visualization. In the spirit of OSS, we also explored some of Grafana’s community visualizations, such as the [Treemap](https://grafana.com/grafana/plugins/marcusolsson-treemap-panel/) and [Word Cloud](https://grafana.com/grafana/plugins/magnesium-wordcloud-panel/) plugins. To visualize committers over time, for example, we simply need to inject the variables `$__timeFilter(time)` and `$__timeInterval(time)` to ensure the time filter is applied and the bucket sizes are appropriate. For more details on how these work, either watch the webinar or see [here](https://github.com/grafana/clickhouse-datasource#macros).

![grafana_heatmap.png](https://clickhouse.com/uploads/grafana_heatmap_5fb5bda626.png)

```sql
SELECT $__timeInterval(time) as time, author, count(*) as ` ` FROM commits WHERE $__timeFilter(time) AND author IN (
    SELECT author
    FROM commits WHERE author NOT LIKE '%renovate[bot]%' AND $__timeFilter(time)
    GROUP BY author
    ORDER BY count() DESC
    LIMIT 15
) GROUP BY author, time ORDER BY time, author ASC, time DESC LIMIT 10000
```

## The final result

We encourage the users to watch the webinar to not only learn some tips and tricks for building ClickHouse powered visualizations in Grafana but also to obtain a better appreciation for the history of such as successful OSS project as Grafana. For us, we’re impressed that Grafana founder [Torkel](https://github.com/torkelo) remains such an instrumental committer today as when the project was founded. Having spent a good part of the first 5yrs rewriting each other's code, [Carl Bergquist](https://github.com/bergquist) and Torkel have clearly had a huge impact on what is a thriving community today. While the number of commits per day has steadily increased, what is apparent is the amount of work done by commits has increased dramatically. Key features such as alerting being added and a docker file being made available are by far the most popular issues. Finally, we were happy to see people committing to both repositories while noticing that community members starring both repositories (now over 6500) star Grafana first! Hopefully you agree our final dashboard is alittle richer than Github Pulse.

![grafana-1.png](https://clickhouse.com/uploads/grafana_1_c609ddf5bc.png)

![grafana-2.png](https://clickhouse.com/uploads/grafana_2_46122611c0.png)

## Gathering community feedback

Webinars give us the opportunity to collect direct feedback from our community. At the end, we thus asked our users which features they would next want to see supported in the ClickHouse datasource for Grafana. The results below were enlightening to us, and you can expect them to influence our roadmap, which we will publish shortly in our [public repository](https://github.com/grafana/clickhouse-datasource/issues).

![grafana_poll.png](https://clickhouse.com/uploads/grafana_poll_222766278a.png)

## Conclusion

In this post, we’ve summarised our recent webinar with Grafana concerning the official Grafana plugin for ClickHouse. Thanks to our friends at Grafana for hosting, congratulations on the last 10 yrs, and we enjoy watching.
