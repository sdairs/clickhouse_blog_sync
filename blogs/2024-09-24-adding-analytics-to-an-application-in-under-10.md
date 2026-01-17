---
title: "Adding Analytics to an Application in under 10 minutes with ClickHouse Cloud Query Endpoints"
date: "2024-09-24T13:15:33.749Z"
author: "Dale McDiarmid"
category: "Engineering"
excerpt: "Read how you can now add ClickHouse powered analytics to an application in under 10 minutes, thanks to query endpoints."
---

# Adding Analytics to an Application in under 10 minutes with ClickHouse Cloud Query Endpoints

## Introduction

The pace of development at ClickHouse is often a pleasant surprise to newcomers with our [launch week](https://clickhouse.com/launch-week/may-2024) announcing a number of features which make using ClickHouse easier than ever. As someone who enjoys building analytical applications on top of ClickHouse, one of these new features, [API endpoints](https://clickhouse.com/docs/en/get-started/query-endpoints), particularly caught my eye. On playing with the feature, I realized a lot of demo code could now be made significantly simpler while also speeding up the development of new features.

> API endpoints, announced in beta, allow you to expose a secure HTTP endpoint which consumes parameters and uses this to populate and execute a predefined SQL query.

API endpoints do more than make an interface simpler - they add [separation of concerns](https://en.wikipedia.org/wiki/Separation_of_concerns). As well as making it simpler to update an application query, without having to modify or redeploy the code, this allows teams to easily expose analytics without needing to write SQL or interact directly with a ClickHouse database owned by different teams.

To demonstrate this we update one of our demo applications, [ClickPy](https://clickpy.clickhouse.com/), adding new GitHub analytics in a few minutes. We hope the learnings here can be applied to your own ClickHouse applications, making adding new features significantly easier.

To accompany this blog, we’ve included a small cookbook which includes the standalone code for the visualizations added in this blog.

## What is ClickPy?

Earlier this year, we announced [ClickPy](https://clickpy.clickhouse.com/) - a simple real-time dashboard that allows users to view download statistics on Python packages. This app is powered by PyPI data, with a row for every Python package download that has ever occurred! Every time you run `pip install,` we get a row in ClickHouse! 

![clickpy.png](https://clickhouse.com/uploads/clickpy_04b1db8a52.png)

<blockquote style="font-size: 14px;">
<p>This dataset is now <a href="https://clickhouse.com/blog/clickhouse-1-trillion-row-challenge">over a trillion rows</a> with around 1.2b rows added daily and is the perfect example of how big data analytics can be performed with ClickHouse.</p>
</blockquote>

The application itself is pretty simple based on React, NextJs and [Apache ECharts](https://echarts.apache.org/en/index.html). The secret sauce, as we [document in the open-source repo](https://github.com/ClickHouse/clickpy), is the use of ClickHouse materialized views to compute aggregates at insert time thus ensuring queries respond in milliseconds and users get a snappy and responsive experience.

<iframe width="768" height="432" src="https://www.youtube.com/embed/QUigKP7iy7Y?si=gO9MOY85rkJpMf57" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

## Adding a new dataset

Many Python packages are open-source and thus often have their own GitHub repositories. The PyPi data captures this through the`homepage` and `project_urls` columns in the `projects` table e.g. for `clickhouse-connect`, the official ClickHouse Python client, and the `boto3` library.

<pre style="font-size: 14px;"><code class="hljs language-sql"><span class="hljs-keyword">SELECT</span>
	name,
	argMax(home_page, upload_time) <span class="hljs-keyword">AS</span> home_page,
	argMax(project_urls, upload_time) <span class="hljs-keyword">AS</span> project_urls
<span class="hljs-keyword">FROM</span> pypi.projects
<span class="hljs-keyword">WHERE</span> name <span class="hljs-keyword">IN</span> (<span class="hljs-string">'clickhouse-connect'</span>, <span class="hljs-string">'boto3'</span>)
<span class="hljs-keyword">GROUP</span> <span class="hljs-keyword">BY</span> name
FORMAT Vertical

<span class="hljs-type">Row</span> <span class="hljs-number">1</span>:
──────
name:     	boto3
home_page:	https:<span class="hljs-operator">/</span><span class="hljs-operator">/</span>github.com<span class="hljs-operator">/</span>boto<span class="hljs-operator">/</span>boto3
project_urls: [<span class="hljs-string">'Documentation, https://boto3.amazonaws.com/v1/documentation/api/latest/index.html'</span>,<span class="hljs-string">'Source, https://github.com/boto/boto3'</span>]

<span class="hljs-type">Row</span> <span class="hljs-number">2</span>:
──────
name:     	clickhouse<span class="hljs-operator">-</span><span class="hljs-keyword">connect</span>
home_page:	https:<span class="hljs-operator">/</span><span class="hljs-operator">/</span>github.com<span class="hljs-operator">/</span>ClickHouse<span class="hljs-operator">/</span>clickhouse<span class="hljs-operator">-</span><span class="hljs-keyword">connect</span>
project_urls: []

<span class="hljs-number">2</span> <span class="hljs-keyword">rows</span> <span class="hljs-keyword">in</span> set. Elapsed: <span class="hljs-number">0.018</span> sec. Processed <span class="hljs-number">27.48</span> thousand <span class="hljs-keyword">rows</span>, <span class="hljs-number">2.94</span> MB (<span class="hljs-number">1.57</span> million <span class="hljs-keyword">rows</span><span class="hljs-operator">/</span>s., <span class="hljs-number">167.52</span> MB<span class="hljs-operator">/</span>s.)
Peak memory usage: <span class="hljs-number">26.51</span> MiB.
</code></pre>

One of the other popular datasets users often use to experiment with ClickHouse is [GitHub events](https://docs.github.com/en/rest/activity/events?apiVersion=2022-11-28). This captures every star, issue, pull request, comment and fork event made on GitHub, with around 7.75 billion events as of June 2024. Provided by GitHub and updated hourly, this seemed like the perfect complement to our PyPi dataset.

<pre style="font-size: 14px;"><code class="hljs language-sql"><span class="hljs-keyword">CREATE</span> <span class="hljs-keyword">TABLE</span> github.github_events
(
	`file_time` DateTime,
	`event_type` Enum8(<span class="hljs-string">'CommitCommentEvent'</span> <span class="hljs-operator">=</span> <span class="hljs-number">1</span>, <span class="hljs-string">'CreateEvent'</span> <span class="hljs-operator">=</span> <span class="hljs-number">2</span>, <span class="hljs-string">'DeleteEvent'</span> <span class="hljs-operator">=</span> <span class="hljs-number">3</span>, <span class="hljs-string">'ForkEvent'</span> <span class="hljs-operator">=</span> <span class="hljs-number">4</span>, <span class="hljs-string">'GollumEvent'</span> <span class="hljs-operator">=</span> <span class="hljs-number">5</span>, <span class="hljs-string">'IssueCommentEvent'</span> <span class="hljs-operator">=</span> <span class="hljs-number">6</span>, <span class="hljs-string">'IssuesEvent'</span> <span class="hljs-operator">=</span> <span class="hljs-number">7</span>, <span class="hljs-string">'MemberEvent'</span> <span class="hljs-operator">=</span> <span class="hljs-number">8</span>, <span class="hljs-string">'PublicEvent'</span> <span class="hljs-operator">=</span> <span class="hljs-number">9</span>, <span class="hljs-string">'PullRequestEvent'</span> <span class="hljs-operator">=</span> <span class="hljs-number">10</span>, <span class="hljs-string">'PullRequestReviewCommentEvent'</span> <span class="hljs-operator">=</span> <span class="hljs-number">11</span>, <span class="hljs-string">'PushEvent'</span> <span class="hljs-operator">=</span> <span class="hljs-number">12</span>, <span class="hljs-string">'ReleaseEvent'</span> <span class="hljs-operator">=</span> <span class="hljs-number">13</span>, <span class="hljs-string">'SponsorshipEvent'</span> <span class="hljs-operator">=</span> <span class="hljs-number">14</span>, <span class="hljs-string">'WatchEvent'</span> <span class="hljs-operator">=</span> <span class="hljs-number">15</span>, <span class="hljs-string">'GistEvent'</span> <span class="hljs-operator">=</span> <span class="hljs-number">16</span>, <span class="hljs-string">'FollowEvent'</span> <span class="hljs-operator">=</span> <span class="hljs-number">17</span>, <span class="hljs-string">'DownloadEvent'</span> <span class="hljs-operator">=</span> <span class="hljs-number">18</span>, <span class="hljs-string">'PullRequestReviewEvent'</span> <span class="hljs-operator">=</span> <span class="hljs-number">19</span>, <span class="hljs-string">'ForkApplyEvent'</span> <span class="hljs-operator">=</span> <span class="hljs-number">20</span>, <span class="hljs-string">'Event'</span> <span class="hljs-operator">=</span> <span class="hljs-number">21</span>, <span class="hljs-string">'TeamAddEvent'</span> <span class="hljs-operator">=</span> <span class="hljs-number">22</span>),
	`actor_login` LowCardinality(String),
	`repo_name` LowCardinality(String),
	`repo_id` LowCardinality(String),
	`created_at` DateTime,
	`updated_at` DateTime,
	`action` Enum8(<span class="hljs-string">'none'</span> <span class="hljs-operator">=</span> <span class="hljs-number">0</span>, <span class="hljs-string">'created'</span> <span class="hljs-operator">=</span> <span class="hljs-number">1</span>, <span class="hljs-string">'added'</span> <span class="hljs-operator">=</span> <span class="hljs-number">2</span>, <span class="hljs-string">'edited'</span> <span class="hljs-operator">=</span> <span class="hljs-number">3</span>, <span class="hljs-string">'deleted'</span> <span class="hljs-operator">=</span> <span class="hljs-number">4</span>, <span class="hljs-string">'opened'</span> <span class="hljs-operator">=</span> <span class="hljs-number">5</span>, <span class="hljs-string">'closed'</span> <span class="hljs-operator">=</span> <span class="hljs-number">6</span>, <span class="hljs-string">'reopened'</span> <span class="hljs-operator">=</span> <span class="hljs-number">7</span>, <span class="hljs-string">'assigned'</span> <span class="hljs-operator">=</span> <span class="hljs-number">8</span>, <span class="hljs-string">'unassigned'</span> <span class="hljs-operator">=</span> <span class="hljs-number">9</span>, <span class="hljs-string">'labeled'</span> <span class="hljs-operator">=</span> <span class="hljs-number">10</span>, <span class="hljs-string">'unlabeled'</span> <span class="hljs-operator">=</span> <span class="hljs-number">11</span>, <span class="hljs-string">'review_requested'</span> <span class="hljs-operator">=</span> <span class="hljs-number">12</span>, <span class="hljs-string">'review_request_removed'</span> <span class="hljs-operator">=</span> <span class="hljs-number">13</span>, <span class="hljs-string">'synchronize'</span> <span class="hljs-operator">=</span> <span class="hljs-number">14</span>, <span class="hljs-string">'started'</span> <span class="hljs-operator">=</span> <span class="hljs-number">15</span>, <span class="hljs-string">'published'</span> <span class="hljs-operator">=</span> <span class="hljs-number">16</span>, <span class="hljs-string">'update'</span> <span class="hljs-operator">=</span> <span class="hljs-number">17</span>, <span class="hljs-string">'create'</span> <span class="hljs-operator">=</span> <span class="hljs-number">18</span>, <span class="hljs-string">'fork'</span> <span class="hljs-operator">=</span> <span class="hljs-number">19</span>, <span class="hljs-string">'merged'</span> <span class="hljs-operator">=</span> <span class="hljs-number">20</span>),
	`number` UInt32,
	… <span class="hljs-operator">/</span><span class="hljs-operator">/</span> columns omitted <span class="hljs-keyword">for</span> brevity
)
ENGINE <span class="hljs-operator">=</span> MergeTree
<span class="hljs-keyword">ORDER</span> <span class="hljs-keyword">BY</span> (repo_id, event_type, created_at)
</code></pre>

The full schema along with details on loading this dataset and some example queries, can be found [here](https://ghe.clickhouse.tech/). We use a [simple script](https://pastila.nl/?00ab4c18/d0acecfb9cbf62b51afb3afcd342f428#wgzLmxVIj2YhwmT1uguvsQ==) executed hourly to load new events as they are published by GitHub. Our script differs from the documented instructions in that it also extracts a `repo.id`, required for statistics we wish to compute. Our schema also modifies the `ORDER BY` key with a repo_name specified first, since ClickPy enforces this as a filter.

The objective here was pretty simple: add some simple metrics to our main ClickPy analytics page if the package the user was viewing was hosted on GitHub. More specifically, the number of stars, watches, issues and PRs.

![simple_stats.png](https://clickhouse.com/uploads/simple_stats_71a61046f4.png)

For now we keep this simple. We plan to enrich ClickPy further with this data and add more engaging visuals. Stay-tuned.

## A cleaner approach

Previously every visual in ClickPy was powered by a SQL query. Most visuals have a function similar to the following:

<pre style="font-size: 14px;"><code class="hljs language-javascript"><span class="hljs-keyword">export</span> <span class="hljs-keyword">async</span> <span class="hljs-keyword">function</span> <span class="hljs-title function_">getDownloadsOverTime</span>(<span class="hljs-params">{package_name, version, period, min_date, max_date, country_code, type}</span>) {
	<span class="hljs-keyword">const</span> columns = [<span class="hljs-string">'project'</span>, <span class="hljs-string">'date'</span>]
	<span class="hljs-keyword">if</span> (version) {  columns.<span class="hljs-title function_">push</span>(<span class="hljs-string">'version'</span>) }
	<span class="hljs-keyword">if</span> (country_code) { columns.<span class="hljs-title function_">push</span>(<span class="hljs-string">'country_code'</span>) }
	<span class="hljs-keyword">if</span> (type) { columns.<span class="hljs-title function_">push</span>(<span class="hljs-string">'type'</span>)}
	<span class="hljs-keyword">const</span> table = <span class="hljs-title function_">findOptimalTable</span>(columns)
	<span class="hljs-keyword">return</span> <span class="hljs-title function_">query</span>(<span class="hljs-string">'getDownloadsOverTime'</span>,
       <span class="hljs-string">`SELECT
    	  toStartOf<span class="hljs-subst">${period}</span>(date)::Date32 AS x,
    	  sum(count) AS y
	FROM <span class="hljs-subst">${PYPI_DATABASE}</span>.<span class="hljs-subst">${table}</span>
	WHERE (date &gt;= {min_date:String}::Date32) AND (date &lt; {max_date:String}::Date32) AND (project = {package_name:String})
	AND <span class="hljs-subst">${version ? <span class="hljs-string">`version={version:String}`</span>: <span class="hljs-string">'1=1'</span>}</span> AND <span class="hljs-subst">${country_code ? <span class="hljs-string">`country_code={country_code:String}`</span>: <span class="hljs-string">'1=1'</span>}</span> AND <span class="hljs-subst">${type ? <span class="hljs-string">`type={type:String}`</span>: <span class="hljs-string">'1=1'</span>}</span> GROUP BY x
	ORDER BY x ASC`</span>, 
       {
    	  <span class="hljs-attr">package_name</span>: package_name,
    	  <span class="hljs-attr">version</span>: version,
    	  <span class="hljs-attr">min_date</span>: min_date,
    	  <span class="hljs-attr">max_date</span>: max_date,
    	  <span class="hljs-attr">country_code</span>: country_code,
    	  <span class="hljs-attr">type</span>: type,
	})
}
</code></pre>

The above powers the downloads per day line chart and is executed server side. This seems a little messy and results in a [large query file to maintain](https://github.com/ClickHouse/clickpy/blob/30ca7806174dfcc2f902f9f439bb44a086b01bb0/src/utils/clickhouse.js#L134).

Ideally this would just be a simple HTTP call with only the parameters, with a separate API layer maintaining all this SQL logic.

## Enter API endpoints

In ClickHouse Cloud any SQL query can be converted into an API endpoint in a few simple clicks, with SQL parameters automatically detected and converted to POST parameters.

Let's assume we encapsulate all of our statistics in a single endpoint. The query to compute the number of stars, issues, watches and PRs:

<pre style="font-size: 14px;"><code class="hljs language-javascript"><span class="hljs-variable constant_">SET</span> param_min_date = <span class="hljs-string">'2011-01-01'</span>
<span class="hljs-variable constant_">SET</span> param_max_date = <span class="hljs-string">'2024-06-06'</span>
<span class="hljs-variable constant_">SET</span> param_project_name = <span class="hljs-string">'clickhouse-connect'</span>

<span class="hljs-variable constant_">WITH</span>
   (
    	<span class="hljs-variable constant_">SELECT</span> <span class="hljs-title function_">regexpExtract</span>(<span class="hljs-title function_">arrayFilter</span>(l -&gt; (l <span class="hljs-variable constant_">LIKE</span> <span class="hljs-string">'%https://github.com/%'</span>), <span class="hljs-title function_">arrayConcat</span>(project_urls, [home_page]))[<span class="hljs-number">1</span>], <span class="hljs-string">'.*https://github.com/(.*)'</span>)
    	<span class="hljs-variable constant_">FROM</span> pypi.<span class="hljs-property">projects</span>
    	<span class="hljs-variable constant_">WHERE</span> name = {<span class="hljs-attr">package_name</span>:<span class="hljs-title class_">String</span>} <span class="hljs-variable constant_">AND</span> <span class="hljs-title function_">length</span>(<span class="hljs-title function_">arrayFilter</span>(l -&gt; (l <span class="hljs-variable constant_">LIKE</span> <span class="hljs-string">'%https://github.com/%'</span>), <span class="hljs-title function_">arrayConcat</span>(project_urls, [home_page]))) &gt;= <span class="hljs-number">1</span>
    	<span class="hljs-variable constant_">ORDER</span> <span class="hljs-variable constant_">BY</span> upload_time <span class="hljs-variable constant_">DESC</span>
    	<span class="hljs-variable constant_">LIMIT</span> <span class="hljs-number">1</span>
   ) <span class="hljs-variable constant_">AS</span> repo,
   id <span class="hljs-variable constant_">AS</span> (
   	<span class="hljs-variable constant_">SELECT</span> repo_id
   	<span class="hljs-variable constant_">FROM</span> github.<span class="hljs-property">github_events</span>
   	<span class="hljs-variable constant_">WHERE</span> (repo_name = repo) <span class="hljs-variable constant_">LIMIT</span> <span class="hljs-number">1</span>
   )
<span class="hljs-variable constant_">SELECT</span>
   <span class="hljs-title function_">uniqExactIf</span>(actor_login, (event_type = <span class="hljs-string">'WatchEvent'</span>) <span class="hljs-variable constant_">AND</span> (action = <span class="hljs-string">'started'</span>)) <span class="hljs-variable constant_">AS</span> stars,
   <span class="hljs-title function_">uniqExactIf</span>(number, event_type = <span class="hljs-string">'IssuesEvent'</span>) <span class="hljs-variable constant_">AS</span> issues,
   <span class="hljs-title function_">uniqExactIf</span>(actor_login, event_type = <span class="hljs-string">'ForkEvent'</span>) <span class="hljs-variable constant_">AS</span> forks,
   <span class="hljs-title function_">uniqExactIf</span>(number, event_type = <span class="hljs-string">'PullRequestEvent'</span>) <span class="hljs-variable constant_">AS</span> prs
<span class="hljs-variable constant_">FROM</span> github.<span class="hljs-property">github_events</span>
<span class="hljs-variable constant_">WHERE</span> (repo_id <span class="hljs-variable constant_">IN</span> id) <span class="hljs-variable constant_">AND</span> (created_at &gt; {<span class="hljs-attr">min_date</span>:<span class="hljs-title class_">Date32</span>}) <span class="hljs-variable constant_">AND</span> (created_at &lt;= {<span class="hljs-attr">max_date</span>:<span class="hljs-title class_">Date32</span>})
</code></pre>

The above accepts 3 parameters which map to UI filters: The repo name of interest as a string as well as the min and max date range. The first CTE identifies whether the `homepage` or `project_urls` has a link with prefix `https://github.com` and thus whether the project has an associated GitHub repository. Using the GitHub project path a repository name is constructed and used to identify the repository id. 

The use of repository id is important for subsequent queries as repository names can change. Our stats are computed from the main table `github.github_events`, using conditionals 

In [ClickHouse Cloud](https://clickhouse.com/cloud), these parameters are automatically detected and exposed as text boxes the user can populate:

![query_in_cloud.png](https://clickhouse.com/uploads/query_in_cloud_db9e275838.png)

To convert this query into an endpoint, we simply need to click `Share -> API Endpoint`, saving the query with a name and creating an API token to use with "Query Endpoints" permissions. Ensure the endpoint is uses a read-only only:

<a target="_blank" href="/uploads/create_api_endpoint_0d3994f6fc.gif"><img src="/uploads/create_api_endpoint_0d3994f6fc.gif"/></a>

<blockquote style="font-size: 14px;">
<p>Note how we associate the "Play role" with the endpoint. This is a role that ensures this endpoint can only be used to respond to queries on the required tables, as well as imposing quotas that are <a href="https://clickhouse.com/docs/en/operations/quotas">keyed off IP addresses</a>, thus limiting the number of requests a single user can make. For users wishing to invoke endpoints from browsers, CORS headers can also be configured with a list of allowed domains. A default "Read only" role provides a simpler getting started.</p>
</blockquote>

This provides us with a HTTP endpoint we can now execute using curl, with the response returned in JSON:

<pre style="font-size: 14px;"><code class="hljs language-bash">curl -H <span class="hljs-string">"Content-Type: application/json"</span> -X <span class="hljs-string">'POST'</span> -s --user <span class="hljs-string">'&lt;key_id&gt;:&lt;key_secret&gt;'</span> <span class="hljs-string">'https://console-api.clickhouse.cloud/.api/query-endpoints/9001b12a-88d0-4b14-acc3-37cc28d7e5f4/run?format=JSONEachRow'</span> --data-raw <span class="hljs-string">'{"queryVariables":{"project_name":"boto3","min_date":"2011-01-01","max_date":"2024-06-06"}}'</span>

{<span class="hljs-string">"stars"</span>:<span class="hljs-string">"47739"</span>,<span class="hljs-string">"issues"</span>:<span class="hljs-string">"3009"</span>,<span class="hljs-string">"forks"</span>:<span class="hljs-string">"11550"</span>,<span class="hljs-string">"prs"</span>:<span class="hljs-string">"1657"</span>}
</code></pre>

An astute reader might notice we pass the url parameter `"format":"JSONEachRow"` to control the output format. Users can specify any of the over [70 output formats](https://clickhouse.com/docs/en/interfaces/formats#jsoneachrow) supported by ClickHouse here. For example, for `CSVWithNames`:

<pre style="font-size: 14px;"><code class="hljs language-bash">curl -H <span class="hljs-string">"Content-Type: application/json"</span> -X <span class="hljs-string">'POST'</span> -s --user <span class="hljs-string">'&lt;key_id&gt;:&lt;key_secret&gt;'</span> <span class="hljs-string">'https://console-api.clickhouse.cloud/.api/query-endpoints/9001b12a-88d0-4b14-acc3-37cc28d7e5f4/run?format=CSVWithNames'</span> --data-raw <span class="hljs-string">'{"queryVariables":{"project_name":"boto3","min_date":"2011-01-01","max_date":"2024-06-06"}}'</span>

<span class="hljs-string">"stars"</span>,<span class="hljs-string">"issues"</span>,<span class="hljs-string">"forks"</span>,<span class="hljs-string">"prs"</span>
47739,3009,11550,1657
</code></pre>

## Putting it together

The above leaves us with just needing to build our visuals and integrate the API endpoint above.

The React code for components is pretty simple with the most relevant snippets below. More curious readers can find the code [here](https://github.com/ClickHouse/clickpy/blob/main/src/components/GithubStats.jsx).

<pre style="font-size: 14px;"><code class="hljs language-javascript"><span class="hljs-comment">// main panel containing stats</span>
<span class="hljs-keyword">export</span> <span class="hljs-keyword">default</span> <span class="hljs-keyword">async</span> <span class="hljs-keyword">function</span> <span class="hljs-title function_">GithubStats</span>(<span class="hljs-params">{ repo_name, min_date, max_date }</span>) {
  <span class="hljs-keyword">const</span> stats = <span class="hljs-keyword">await</span> <span class="hljs-title function_">getGithubStats</span>(repo_name, min_date, max_date);
  <span class="hljs-keyword">return</span> stats.<span class="hljs-property">length</span> &gt; <span class="hljs-number">0</span> ? (
   <span class="xml"><span class="hljs-tag">&lt;<span class="hljs-name">div</span> <span class="hljs-attr">className</span>=<span class="hljs-string">"flex h-full gap-4 flex-row flex-wrap xl:flex-nowrap"</span>&gt;</span>
    <span class="hljs-tag">&lt;<span class="hljs-name">div</span> <span class="hljs-attr">className</span>=<span class="hljs-string">"flex gap-4 w-full sm:flex-row flex-col"</span>&gt;</span>
      <span class="hljs-tag">&lt;<span class="hljs-name">SimpleStat</span> <span class="hljs-attr">value</span>=<span class="hljs-string">{stats[0]}</span> <span class="hljs-attr">subtitle</span>=<span class="hljs-string">{</span>"# <span class="hljs-attr">Github</span> <span class="hljs-attr">stars</span>"} <span class="hljs-attr">logo</span>=<span class="hljs-string">{</span>"/<span class="hljs-attr">stars.svg</span>"} /&gt;</span>
      <span class="hljs-tag">&lt;<span class="hljs-name">SimpleStat</span> <span class="hljs-attr">value</span>=<span class="hljs-string">{stats[1]}</span> <span class="hljs-attr">subtitle</span>=<span class="hljs-string">{</span>"# <span class="hljs-attr">Pull</span> <span class="hljs-attr">requests</span>"} <span class="hljs-attr">logo</span>=<span class="hljs-string">{</span>"/<span class="hljs-attr">prs.svg</span>"} /&gt;</span>
    <span class="hljs-tag">&lt;/<span class="hljs-name">div</span>&gt;</span>
    <span class="hljs-tag">&lt;<span class="hljs-name">div</span> <span class="hljs-attr">className</span>=<span class="hljs-string">"flex gap-4 w-full sm:flex-row flex-col"</span>&gt;</span>
      <span class="hljs-tag">&lt;<span class="hljs-name">SimpleStat</span> <span class="hljs-attr">value</span>=<span class="hljs-string">{stats[2]}</span> <span class="hljs-attr">subtitle</span>=<span class="hljs-string">{</span>"# <span class="hljs-attr">Issues</span>"} <span class="hljs-attr">logo</span>=<span class="hljs-string">{</span>"/<span class="hljs-attr">issues.svg</span>"}/&gt;</span>
      <span class="hljs-tag">&lt;<span class="hljs-name">SimpleStat</span> <span class="hljs-attr">value</span>=<span class="hljs-string">{stats[3]}</span> <span class="hljs-attr">subtitle</span>=<span class="hljs-string">{</span>"# <span class="hljs-attr">Forks</span>"} <span class="hljs-attr">logo</span>=<span class="hljs-string">{</span>"/<span class="hljs-attr">fork.svg</span>"} /&gt;</span>
    <span class="hljs-tag">&lt;/<span class="hljs-name">div</span>&gt;</span>
   <span class="hljs-tag">&lt;/<span class="hljs-name">div</span>&gt;</span></span>
  ) : <span class="hljs-literal">null</span>;
}

<span class="hljs-comment">// a single state component</span>
<span class="hljs-keyword">export</span> <span class="hljs-keyword">default</span> <span class="hljs-keyword">function</span> <span class="hljs-title function_">SimpleStat</span>(<span class="hljs-params">{ value, subtitle, logo }</span>) {
 <span class="hljs-keyword">return</span> (
   <span class="xml"><span class="hljs-tag">&lt;<span class="hljs-name">div</span> <span class="hljs-attr">className</span>=<span class="hljs-string">"min-w-[250px] rounded-lg bg-slate-850 flex gap-4 p-4 h-24  w-full min-w-72 border border-slate-700"</span>&gt;</span>
     <span class="hljs-tag">&lt;<span class="hljs-name">div</span> <span class="hljs-attr">className</span>=<span class="hljs-string">"items-center flex grow"</span>&gt;</span>
       <span class="hljs-tag">&lt;<span class="hljs-name">Image</span>
         <span class="hljs-attr">width</span>=<span class="hljs-string">{16}</span>
         <span class="hljs-attr">height</span>=<span class="hljs-string">{16}</span>
         <span class="hljs-attr">className</span>=<span class="hljs-string">"h-16 w-16 min-w-16 min-h-16 bg-neutral-850 rounded-lg"</span>
         <span class="hljs-attr">src</span>=<span class="hljs-string">{logo}</span>
         <span class="hljs-attr">alt</span>=<span class="hljs-string">{subtitle}</span>
      /&gt;</span>
       <span class="hljs-tag">&lt;<span class="hljs-name">div</span> <span class="hljs-attr">className</span>=<span class="hljs-string">"ml-2 mr-4"</span>&gt;</span>
         <span class="hljs-tag">&lt;<span class="hljs-name">p</span> <span class="hljs-attr">className</span>=<span class="hljs-string">"text-xl mr-2 font-bold"</span>&gt;</span>{value}<span class="hljs-tag">&lt;/<span class="hljs-name">p</span>&gt;</span>
         <span class="hljs-tag">&lt;<span class="hljs-name">p</span> <span class="hljs-attr">className</span>=<span class="hljs-string">"text-slate-200"</span>&gt;</span>{subtitle}<span class="hljs-tag">&lt;/<span class="hljs-name">p</span>&gt;</span>
       <span class="hljs-tag">&lt;/<span class="hljs-name">div</span>&gt;</span>
     <span class="hljs-tag">&lt;/<span class="hljs-name">div</span>&gt;</span>
   <span class="hljs-tag">&lt;/<span class="hljs-name">div</span>&gt;</span></span>
 );
}
</code></pre>

This code invokes the function `getGithubStats` which in turn invokes the generic function `runAPIEndpoint` function passing the endpoint and its parameters:

<pre style="font-size: 14px;"><code class="hljs language-javascript"><span class="hljs-keyword">export</span> <span class="hljs-keyword">async</span> <span class="hljs-keyword">function</span> <span class="hljs-title function_">runAPIEndpoint</span>(<span class="hljs-params">endpoint, params</span>) {
	<span class="hljs-keyword">const</span> data = {
    	<span class="hljs-attr">queryVariables</span>: params,
    	<span class="hljs-attr">format</span>: <span class="hljs-string">'JSONEachRow'</span>
  	};    
  	<span class="hljs-keyword">const</span> response = <span class="hljs-keyword">await</span> <span class="hljs-title function_">fetch</span>(endpoint, {
    	<span class="hljs-attr">method</span>: <span class="hljs-string">'POST'</span>,
    	<span class="hljs-attr">headers</span>: {
      	<span class="hljs-string">'Content-Type'</span>: <span class="hljs-string">'application/json'</span>,
      	<span class="hljs-string">'Authorization'</span>: <span class="hljs-string">`Basic <span class="hljs-subst">${btoa(<span class="hljs-string">`<span class="hljs-subst">${process.env.API_KEY_ID}</span>:<span class="hljs-subst">${process.env.API_KEY_SECRET}</span>`</span>)}</span>`</span>
    	},
    	<span class="hljs-attr">body</span>: <span class="hljs-title class_">JSON</span>.<span class="hljs-title function_">stringify</span>(data)
  	})
  	<span class="hljs-keyword">return</span> response.<span class="hljs-title function_">json</span>()
}

<span class="hljs-keyword">export</span> <span class="hljs-keyword">async</span> <span class="hljs-keyword">function</span> <span class="hljs-title function_">getGithubStats</span>(<span class="hljs-params">package_name, min_date, max_date</span>) {
	<span class="hljs-keyword">return</span> <span class="hljs-title function_">runAPIEndpoint</span>(process.<span class="hljs-property">env</span>.<span class="hljs-property">GITHUB_STATS_API</span>, {
    	  <span class="hljs-attr">package_name</span>: package_name,
    	  <span class="hljs-attr">min_date</span>: min_date,
    	  <span class="hljs-attr">max_date</span>: max_date
	})
}
</code></pre>

And we're done!

![clickpy_with_new_stats.png](https://clickhouse.com/uploads/clickpy_with_new_stats_0ef111ed47.png)

## A complete example

While the source code for ClickPy is available on Github, users may wish to experiment with a simpler example. For this we’ve prepared a trimmed down version of the application where users can enter a Python package and Github stats are rendered. To render a few details about the package, along with Github statistics, our query returns columns from the projects table:

<pre style="font-size: 14px;"><code class="hljs language-sql"><span class="hljs-keyword">SET</span> param_package_name<span class="hljs-operator">=</span><span class="hljs-string">'boto3'</span>

<span class="hljs-keyword">WITH</span>
  (
        <span class="hljs-keyword">SELECT</span> version
        <span class="hljs-keyword">FROM</span> pypi.projects
        <span class="hljs-keyword">WHERE</span> name <span class="hljs-operator">=</span> {package_name:String}
        <span class="hljs-keyword">ORDER</span> <span class="hljs-keyword">BY</span> arrayMap(x <span class="hljs-operator">-</span><span class="hljs-operator">&gt;</span> toUInt8OrDefault(x, <span class="hljs-number">0</span>), splitByChar(<span class="hljs-string">'.'</span>, version)) <span class="hljs-keyword">DESC</span>
        LIMIT <span class="hljs-number">1</span>
  ) <span class="hljs-keyword">AS</span> max_version,
  project_details <span class="hljs-keyword">AS</span> (
     <span class="hljs-keyword">SELECT</span>
        name,
        max_version,
        summary,
        author,
        author_email,
        license,
        home_page,
        <span class="hljs-built_in">trim</span>(<span class="hljs-keyword">TRAILING</span> <span class="hljs-string">'/'</span> <span class="hljs-keyword">FROM</span> regexpExtract(arrayFilter(l <span class="hljs-operator">-</span><span class="hljs-operator">&gt;</span> (l <span class="hljs-keyword">LIKE</span> <span class="hljs-string">'%https://github.com/%'</span>), arrayConcat(project_urls, [home_page]))[<span class="hljs-number">1</span>], <span class="hljs-string">'.*https://github.com/(.*)'</span>)) <span class="hljs-keyword">AS</span> github
     <span class="hljs-keyword">FROM</span> pypi.projects
     <span class="hljs-keyword">WHERE</span> (name <span class="hljs-operator">=</span> {package_name:String})
     <span class="hljs-keyword">ORDER</span> <span class="hljs-keyword">BY</span> upload_time <span class="hljs-keyword">DESC</span>
     LIMIT <span class="hljs-number">1</span>
  ),
  id <span class="hljs-keyword">AS</span> (
      <span class="hljs-keyword">SELECT</span> repo_id
      <span class="hljs-keyword">FROM</span> github.repo_name_to_id
      <span class="hljs-keyword">WHERE</span> repo_name <span class="hljs-keyword">IN</span> (<span class="hljs-keyword">SELECT</span> github <span class="hljs-keyword">FROM</span> project_details) LIMIT <span class="hljs-number">1</span>
  ),
  stats <span class="hljs-keyword">AS</span> (
     <span class="hljs-keyword">SELECT</span>
        uniqExactIf(actor_login, (event_type <span class="hljs-operator">=</span> <span class="hljs-string">'WatchEvent'</span>) <span class="hljs-keyword">AND</span> (action <span class="hljs-operator">=</span> <span class="hljs-string">'started'</span>)) <span class="hljs-keyword">AS</span> stars,
        uniqExactIf(number, event_type <span class="hljs-operator">=</span> <span class="hljs-string">'IssuesEvent'</span>) <span class="hljs-keyword">AS</span> issues,
        uniqExactIf(actor_login, event_type <span class="hljs-operator">=</span> <span class="hljs-string">'ForkEvent'</span>) <span class="hljs-keyword">AS</span> forks,
        uniqExactIf(number, event_type <span class="hljs-operator">=</span> <span class="hljs-string">'PullRequestEvent'</span>) <span class="hljs-keyword">AS</span> prs
     <span class="hljs-keyword">FROM</span> github.github_events_v2
     <span class="hljs-keyword">WHERE</span> (repo_id <span class="hljs-keyword">IN</span> id)
  )
 <span class="hljs-keyword">SELECT</span> <span class="hljs-operator">*</span> <span class="hljs-keyword">FROM</span> project_details, stats FORMAT Vertical

<span class="hljs-type">Row</span> <span class="hljs-number">1</span>:
──────
name:     	requests
max_version:  <span class="hljs-number">2.32</span><span class="hljs-number">.3</span>
summary:  	Python HTTP <span class="hljs-keyword">for</span> Humans.
author:   	Kenneth Reitz
author_email: me<span class="hljs-variable">@kennethreitz</span>.org
license:  	Apache<span class="hljs-number">-2.0</span>
home_page:	https:<span class="hljs-operator">/</span><span class="hljs-operator">/</span>requests.readthedocs.io
github:   	psf<span class="hljs-operator">/</span>requests
stars:    	<span class="hljs-number">22032</span>
issues:   	<span class="hljs-number">1733</span>
forks:    	<span class="hljs-number">5150</span>
prs:      	<span class="hljs-number">1026</span>

<span class="hljs-number">1</span> <span class="hljs-type">row</span> <span class="hljs-keyword">in</span> set. Elapsed: <span class="hljs-number">0.472</span> sec. Processed <span class="hljs-number">195.71</span> million <span class="hljs-keyword">rows</span>, <span class="hljs-number">394.59</span> MB (<span class="hljs-number">414.49</span> million <span class="hljs-keyword">rows</span><span class="hljs-operator">/</span>s., <span class="hljs-number">835.71</span> MB<span class="hljs-operator">/</span>s.)
Peak memory usage: <span class="hljs-number">723.12</span> MiB.
</code></pre>

This allows us to render some pretty simple statistics:

![requests_example.png](https://clickhouse.com/uploads/requests_example_ce3034134a.png)

<pre style="font-size: 14px;"><code class="hljs language-bash">curl -H <span class="hljs-string">"Content-Type: application/json"</span> -X <span class="hljs-string">'POST'</span> -s --user <span class="hljs-string">'MdhWYPEpXaqiwGMjbXWT:4b1dKbabyQTvuKUWOnI08oXVbUD4tkaxKKjEwz7ORG'</span> <span class="hljs-string">'https://console-api.clickhouse.cloud/.api/query-endpoints/297797b1-c5b0-4741-9f5b-3d6456a9860d/run?format=JSONEachRow'</span> --data-raw <span class="hljs-string">'{"queryVariables":{"package_name":"requests"}}'</span>
</code></pre>

The source code for this application can be found [here](https://github.com/ClickHouse/gitstats_demo).

## Recommended usage

The above examples execute the endpoint call on the server side to keep the example simple. While users can safely expose API credentials on the client side, this should be done with caution. Specifically:

1. Ensure endpoints use an API token assigned “Query Endpoint” permissions to avoid leaking credentials with wider permissions (e.g., to create services) beyond those required.
2. At a minimum, ensure the Read-only role is assigned. If using endpoints for internal projects this may be sufficient. For external projects, we recommend creating a dedicated role and [ensuring that quotas](https://clickhouse.com/docs/en/operations/quotas) are assigned as we did for our earlier example. These quotas can be keyed off IP, thus allowing administrators to limit the number of queries for a user per unit time - effectively creating rate limits. For example our public endpoint for the demo app uses the “endpoint_role” and following quota:

<pre style="font-size: 14px;"><code class="hljs language-sql"><span class="hljs-keyword">CREATE</span> QUOTA endpoint_quota KEYED <span class="hljs-keyword">BY</span> ip_address <span class="hljs-keyword">FOR</span> <span class="hljs-type">INTERVAL</span> <span class="hljs-number">1</span> <span class="hljs-keyword">hour</span> MAX queries <span class="hljs-operator">=</span> <span class="hljs-number">100</span>, result_rows <span class="hljs-operator">=</span> <span class="hljs-number">1</span>, read_rows <span class="hljs-operator">=</span> <span class="hljs-number">3000000000000</span>, execution_time <span class="hljs-operator">=</span> <span class="hljs-number">6000</span> <span class="hljs-keyword">TO</span> endpoint_role<span class="hljs-operator">*</span>
</code></pre>

An example role with the full permissions can be found [here](https://pastila.nl/?002ccf51/917e9d67da452079cd08e9e8b65afe5f#ojEQ0evgldNjSzkT8jk9ZA==).

3. Configure the “Allowed Domains” for CORs when creating the endpoint, limiting this to the domain hosting your application.

## Conclusion

While we used an existing application to demonstrate endpoints, adding new functionality in a few minutes, users can use the same features to rapidly prototype and build their own applications. We have also provided a simple example for users to recreate the GitHub stats visual as an application.
