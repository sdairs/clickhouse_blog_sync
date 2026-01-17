---
title: "ClickHouse 22.11 Release"
date: "2022-12-01T13:01:06.635Z"
author: "The ClickHouse team"
category: "Engineering"
excerpt: "15 new features. 5 performance optimisations. 32 bug fixes. Including: Composite time intervals, Support for ** Glob, Functions for Spark compatibility, Retries on INSERT, Data Lake support via Apache Hudi and Delta Lake for SELECT queries."
---

# ClickHouse 22.11 Release

![22.11 Release.png](https://clickhouse.com/uploads/22_11_Release_6c3186d9b5.png)

Another month has come and gone. 
Which, of course, means another ClickHouse release!

22.11 is here!

As usual, we host a monthly release webinar where Alexey shares detail of the release, gives away some swag, and we leave time for community questions. Don’t forget to register for 22.12.

If you are interested in exploring these features, 22.11 is already available on [ClickHouse Cloud](https://clickhouse.cloud/signUp) and is the best way to explore new features!  Let us run ClickHouse for you so you can focus on your application.

## Release Summary

15 new features. 5 performance optimisations. 32 bug fixes.

If that’s not enough to get you interested in trying it out. Check out some of the headline items:

* Composite time intervals
* Support for ** Glob
* Functions for Spark compatibility
* Retries on INSERT
* Data Lake support via Apache Hudi and Delta Lake for SELECT queries

And, of course, a host of performance improvements and integration work. Including substantive changes in the python client and updates to both the go and js clients

## Helpful Links

* [22.11 Release Changelog](https://clickhouse.com/docs/en/whats-new/changelog/#-clickhouse-release-2211-2022-11-17)
* [ClickHouse Cloud Changelog (Nov 29, including 22.11)](https://clickhouse.com/docs/en/whats-new/cloud/#november-29-2022)
* [22.11 Release Presentation](https://presentations.clickhouse.com/release_22.11/)
* [ClickHouse 22.11 Release Webinar](https://www.youtube.com/watch?v=LR-fckOOaFo)

<iframe width="560" height="315" src="https://www.youtube.com/embed/LR-fckOOaFo" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

## Retries will save your sanity

Anyone who has done a large data migration into ClickHouse should be excited by the addition of retries on INSERT. Before this addition, large inserts could easily be interrupted and potentially fail due to connection issues with ClickHouse keeper/Zookeeper e.g., due to resource pressure or network interruptions.  A single failed block within an INSERT would fail the whole request. For long-running inserts e.g., a data migration using [remoteSecure](https://clickhouse.com/docs/en/sql-reference/table-functions/remote/), this could be extremely frustrating with the user needing to reset their state. We now add the setting `insert_keeper_max_retries`, which allows inserts to survive reconnections to the keeper and potential restarts. If a block now fails during an INSERT, it will now be retried. If successful, the INSERT will proceed as usual.  A value of 5 should be sufficient and cover most use cases.

## A Deep Dive on ** Glob

Sometimes, we add a feature, and our users are surprised it wasn’t already supported. This month brings such a feature: Recursive traversal with Glob patterns. We now expose this in any table function which accepts a path.  Most of our users will find this particularly valuable when reading from local storage or s3 buckets to either perform ad-hoc analysis of files or selectively insert data into your ClickHouse instance.

Let's show an example to demonstrate how this can be useful. We recently [published a blog post](https://clickhouse.com/blog/clickhouse-git-community-commits) showing the `git-import` tool, distributed with ClickHouse, that lets you index the commit history for a repository - see [here](https://clickhouse.com/docs/en/getting-started/example-datasets/github) for a description of the tables generated. We distribute this data freely for the ClickHouse and Linux repositories in an s3 bucket, with a folder per repository and files named according to their latest year and month. We also maintain a single file per table. We’ll also likely add other open-source repositories here over time.

<pre style='background-color: #222222; border-radius: 8px; padding: 24px; color: #FFFFFF; display: flex; position: relative; white-space: pre-wrap;'>
<div style='color: #FFFFFF; margin-top: -24px; max-width: 98%;'>
clickhouse@my-mac ~ % aws s3 ls s3://datasets-documentation/github/commits/
                           PRE clickhouse/
                           PRE linux/



clickhouse@my-mac ~ % aws s3 ls s3://datasets-documentation/github/commits/clickhouse/

2022-11-09 15:16:26          0
2022-11-30 11:53:43    2625584 commits.tsv.xz
2022-11-30 12:06:57       1020 commits_200812.tsv.xz
2022-11-30 12:06:57        268 commits_200901.tsv.xz

…

2022-11-30 11:53:54    4755844 file_changes.tsv.xz
2022-11-30 12:06:59       1304 file_changes_200812.tsv.xz
2022-11-30 12:06:59        300 file_changes_200901.tsv.xz

…

2022-11-30 11:57:40  135037052 line_changes.tsv.xz
2022-11-30 12:07:01      28396 line_changes_200812.tsv.xz
2022-11-30 12:07:01        472 line_changes_200901.tsv.xz

…
</div>
</pre>
</p>

Maintaining a hierarchical and file naming strategy has benefits beyond simply aiding navigation. As ClickHouse users, it allows you to target specific subsets of data using s3 functions, thus reducing the data that needs to be read to answer a query. Glob patterns now supercharge this ability!

With the addition of Glob patterns, we now support the recursion of directories using the `**` pattern in addition to our existing support for:

- Expansion patterns, e.g. `{1..10}`
- Set matches, e.g. `{commits, file-changes}`

Let's demonstrate some of these abilities with the above data:

Counting the commits by repository - note the `**` to recurse and only use the commit files, as well as the virtual `_path` column.

<pre style='background-color: #222222; border-radius: 8px; padding: 24px; color: #FFFFFF; display: flex; position: relative; white-space: pre-wrap;'>
<div style='color: #FFFFFF; margin-top: -24px; max-width: 98%;'>
SELECT
    splitByChar('/', _path)[-2] AS repository,
    count() AS `number of commits`
FROM s3('https://datasets-documentation.s3.amazonaws.com/github/commits/**/commits.tsv.xz', 'TSV')
GROUP BY _path

┌─repository─┬─number of commits─┐
│ clickhouse │             62785 │
│ linux      │           1046773 │
└────────────┴───────────────────┘

2 rows in set. Elapsed: 6.717 sec. Processed 1.11 million rows, 250.11 MB (165.18 thousand rows/s., 37.23 MB/s.)
</div>
</pre>
</p>

What about if we count the number of commits by month for the first 6 months of 2022? We could apply a WHERE clause and filter by time. This would meaning reading all of the data, which will be slow - we leave this to the reader try! With glob patterns, however, we only read what we need…

<pre style='background-color: #222222; border-radius: 8px; padding: 24px; color: #FFFFFF; display: flex; position: relative; white-space: pre-wrap;'>
<div style='color: #FFFFFF; margin-top: -24px; max-width: 98%;'>
SELECT
    splitByChar('/', _path)[-2] AS repository,
    month,
    count() AS `number of commits`
FROM s3('https://datasets-documentation.s3.amazonaws.com/github/commits/**/commits_2022{01..06}.tsv.xz', 'TSV', 'hash String,author LowCardinality(String), time DateTime, message String, files_added UInt32, files_deleted UInt32, files_renamed UInt32, files_modified UInt32, lines_added UInt32, lines_deleted UInt32, hunks_added UInt32, hunks_removed UInt32, hunks_changed UInt32')
GROUP BY
    _path,
    toStartOfMonth(time) AS month
ORDER BY
    repository ASC,
    month ASC

┌─repository─┬──────month─┬─number of commits─┐
│ clickhouse │ 2022-01-01 │              1085 │
│ clickhouse │ 2022-02-01 │               802 │
│ clickhouse │ 2022-03-01 │              1099 │
│ clickhouse │ 2022-04-01 │              1188 │
│ clickhouse │ 2022-05-01 │              1541 │
│ clickhouse │ 2022-06-01 │              1243 │
│ linux      │ 2022-01-01 │              5374 │
│ linux      │ 2022-02-01 │              6768 │
│ linux      │ 2022-03-01 │              5919 │
│ linux      │ 2022-04-01 │              7232 │
│ linux      │ 2022-05-01 │              7105 │
│ linux      │ 2022-06-01 │              6404 │
└────────────┴────────────┴───────────────────┘

12 rows in set. Elapsed: 3.501 sec. Processed 32.25 thousand rows, 4.95 MB (9.21 thousand rows/s., 1.41 MB/s.)
</div>
</pre>
</p>

Finally, let's use our new set ability to restrict to the Clickhouse and Linux commits through a set filter, and see if any Kernel committers have also contributed to ClickHouse (we also use a few array functions for fun :)  - yes there are more natural ways to solve!)…

<pre style='background-color: #222222; border-radius: 8px; padding: 24px; color: #FFFFFF; display: flex; position: relative; white-space: pre-wrap;'>
<div style='color: #FFFFFF; margin-top: -24px; max-width: 98%;'>
WITH
    commits AS
    (
        SELECT
            repository,
            author
        FROM s3('https://datasets-documentation.s3.amazonaws.com/github/commits/{linux,clickhouse}/commits_*.tsv.xz', 'TSV', 'hash String,author LowCardinality(String), time DateTime, message String, files_added UInt32, files_deleted UInt32, files_renamed UInt32, files_modified UInt32, lines_added UInt32, lines_deleted UInt32, hunks_added UInt32, hunks_removed UInt32, hunks_changed UInt32')
        GROUP BY
            splitByChar('/', _path)[-2] AS repository,
            author
    ),
    authors AS
    (
        SELECT
            groupArrayIf(author, repository = 'linux') AS linux_authors,
            groupArrayIf(author, repository = 'clickhouse') AS clickhouse_authors
        FROM commits
    )
SELECT arrayJoin(arrayIntersect(linux_authors, clickhouse_authors)) AS common_authors
FROM authors

┌─common_authors──────┐
│ root                │
│ Hui Wang            │
│ Dmitry              │
│ Matwey V. Kornilov  │
│ Salvatore Mesoraca  │
│ Ivan Babrou         │
│ Robert Schulze      │
│ Sergey Kononenko    │
│ Anatoly Pugachev    │
│ Azat Khuzhin        │
│ Ken Chen            │
│ Maxim Nikulin       │
│ Gabriel             │
│ Quanfa Fu           │
│ Rafael David Tinoco │
│ Ben                 │
│ Vladimir            │
│ Jiebin Sun          │
│ George              │
│ Yong Wang           │
│ Dmitry Bilunov      │
│ Ilya                │
└─────────────────────┘
</div>
</pre>
</p>

Results here are a little tricky as the author field (contributors name) is not a great way to uniquely identify individuals, but we acknowledge those in our community who genuinely make this distinguished list.

Feel free to answer any of the questions listed [here](https://clickhouse.com/docs/en/getting-started/example-datasets/github/) using the s3 function and glob patterns.