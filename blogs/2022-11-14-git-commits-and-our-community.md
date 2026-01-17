---
title: "Git commits and our community"
date: "2022-11-14T14:54:34.904Z"
author: "The ClickHouse team"
category: "Engineering"
excerpt: "Read about how you can store the git commit history of any repository in ClickHouse for analysis...starting with ClickHouse itself."
---

# Git commits and our community

![community-is-strength.jpg](https://clickhouse.com/uploads/community_is_strength_65569fbe5b.jpg)

This is the first in a series where we’ll highlight some cool queries and share interesting tips and tricks related to ClickHouse. For the first few posts, we will focus on an analysis of the ClickHouse repository using the `git-import` tool distributed with ClickHouse.

## Introduction

In this post, we’d like to give some insights back to our community. The [Github archive](https://ghe.clickhouse.tech/) dataset has been the foundation for examples and demos for some time. While a great resource, it doesn’t track the details of repositories at a code level, e.g., commits and changes to lines of code, but instead focuses on issues, stars, PRs, and events. Meanwhile, Git insights (via pulse) are interesting but incomplete…and exploring ClickHouse is substantially more fun.

Fortunately, a tool is distributed with ClickHouse that solves this very issue: the `git-import` tool.

<pre style='background-color: #222222; border-radius: 8px; padding: 24px; color: #FFFFFF; display: flex; position: relative; white-space: pre-wrap;'>
<div style='color: #FFFFFF; margin-top: -24px; max-width: 98%;'>
ClickHouse % clickhouse-git-import -h

A tool to extract information from Git repository for analytics.

It dumps the data for the following tables:
- commits - commits with statistics;
- file_changes - files changed in every commit with the info about the change and statistics;
- line_changes - every changed line in every changed file in every commit with full info about the line and the information about previous change of this line.

The largest and the most important table is "line_changes".

Run this tool inside your git repository. It will create .tsv files that can be loaded into ClickHouse (or into other DBMS if you dare).
</div>
</pre>
</p>

For the ClickHouse repository, this generates files of the following sizes in a few minutes as of November 8th, 2022:

* `commits.tsv` - 7.8M - 266,051 rows
* `file_changes.tsv` - 53M - 266,051 rows
* `line_changes.tsv` - 2.7G - 7,535,157 rows

You can generate this data for any repository on Github (see linux [here](https://clickhouse.com/docs/en/getting-started/example-datasets/github#downloading-and-inserting-the-data)) and analyze your own projects using the questions below for inspiration. If you don’t have time to generate the data yourself, we’ve loaded our own data into [play.clickhouse.com](https://sql.clickhouse.com?query_id=DCQPNPAIMAQXRLHYURLKVJ) (note the database is `git_clickhouse`) so our community can play with the example queries.

## Questions answered

The tool handily proposes some possible questions for you to answer. We’ve answered these, in addition to some others of interest, for the ClickHouse repository. You can find the complete list of questions and their current answers [here](https://clickhouse.com/docs/en/getting-started/example-datasets/github).  Please share your own insights for both ClickHouse and other repositories, and feel free to contribute queries and improvements!

Note that some of the questions are quite broad and open to interpretation, so we welcome alternatives. The data is also intended for high-level analytical purposes. It can be imprecise for a few reasons (e.g., dirty and broken commit histories), making some more exact queries particularly challenging. This shouldn’t impact any high-level analysis, however.

In future posts, we’ll dig into some specific queries and highlight a range of ClickHouse functionality. For now, we’d like to present the opportunity to solve one of the tools suggested questions for which the current answer feels like it could be improved….

## A Challenge

The most challenging query posed by the tool is probably the reconstruction of the git blame command. As a reminder, `git blame` shows the current file, annotating each line in the given file with information from the revision that last modified the line. For example,

<pre style='background-color: #222222; border-radius: 8px; padding: 24px; color: #FFFFFF; display: flex; position: relative; white-space: pre-wrap;'>
<div style='color: #FFFFFF; margin-top: -24px; max-width: 98%;  font-size: 12px;}'>
ClickHouse % git blame src/Storages/StorageReplicatedMergeTree.cpp | head

Blaming lines: 100% (8630/8630), done.
cdeda4ab915 src/Storages/StorageReplicatedMergeTree.cpp      (Alexey Milovidov     2020-04-15 23:28:05 +0300    1) #include <Core/Defines.h>
cdeda4ab915 src/Storages/StorageReplicatedMergeTree.cpp      (Alexey Milovidov     2020-04-15 23:28:05 +0300    2)
b40d9200d20 src/Storages/StorageReplicatedMergeTree.cpp      (Anton Popov          2022-10-23 03:29:26 +0000    3) #include <cstddef>
210882b9c4d src/Storages/StorageReplicatedMergeTree.cpp      (alesapin             2022-10-03 23:30:50 +0200    4) #include <ranges>
4c391f8e994 src/Storages/StorageReplicatedMergeTree.cpp      (Mike Kot             2021-06-20 11:24:43 +0300    5) #include "Common/hex.h"
a6ca9f266f1 dbms/src/Storages/StorageReplicatedMergeTree.cpp (Alexey Milovidov     2019-05-03 05:00:57 +0300    6) #include <Common/Macros.h>
a6ca9f266f1 dbms/src/Storages/StorageReplicatedMergeTree.cpp (Alexey Milovidov     2019-05-03 05:00:57 +0300    7) #include <Common/StringUtils/StringUtils.h>
3e5ef56644b dbms/src/Storages/StorageReplicatedMergeTree.cpp (Alexander Burmak     2019-11-27 12:39:44 +0300    8) #include <Common/ZooKeeper/KeeperException.h>
3e5ef56644b dbms/src/Storages/StorageReplicatedMergeTree.cpp (Alexander Burmak     2019-11-27 12:39:44 +0300    9) #include <Common/ZooKeeper/Types.h>
3e5ef56644b dbms/src/Storages/StorageReplicatedMergeTree.cpp (Alexander Burmak     2019-11-27 12:39:44 +0300   10) #include <Common/escapeForFileName.h>
</div>
</pre>
</p>

Reconstructing this from a history of commits is particularly challenging - especially since ClickHouse doesn’t currently have an `arrayFold` or `arrayReduce` function which iterates with the current state. Our documentation has an [approximate solution](https://clickhouse.com/docs/en/getting-started/example-datasets/github/#git-blame) appropriate for high-level analysis, but we hope you can improve this.

We leave this to the reader to solve - with a t-shirt for the first to present their answer - tweet us at @ClickHouse, send us an email at  [community@clickhouse.com](mailto:community@clickhouse.com) with the title “git blame solution” or just raise a PR on the [doc page](https://github.com/ClickHouse/ClickHouse/blob/master/docs/en/getting-started/example-datasets/github.md).

A few tips:

* When comparing your query result with `git-blame`, make sure you check out the same commit for which this dataset was generated up to - if using play, check the latest commit [here](https://sql.clickhouse.com?query_id=7ARCDLHQCESYBP3INDPTVO). This is the same as the distributed datasets available [here](https://clickhouse.com/docs/en/getting-started/example-datasets/github#downloading-and-inserting-the-data).
* Also, consider that files can be renamed, and thus changes can be logged under different paths. We have solved this for you with a UDF, which gives you the complete change history. See [here](https://clickhouse.com/docs/en/getting-started/example-datasets/github#line-by-line-commit-history-of-a-file).
* The `line_changes` table has a row for every line change - see the `line` field, as well as the time and commit. The `sign` field indicates if the lines were an insertion (1) or deletion (-1).
* The insertion and deletion of a line cause the position of all previous lines, at that moment in line, to change by 1 or -1, respectively.

A completely accurate answer is unlikely for all files due to issues in the commit history. An answer which is close, with justifications for discrepancies attributed to the data, will therefore be accepted. If an exact solution is not submitted by December 14th, the closest and current accepted solution will win.

For those of you wanting to participate, ClickHouse Cloud is a great starting point to solve the challenge - spin up a cluster, [load the data](https://clickhouse.com/docs/en/getting-started/example-datasets/github/#downloading-and-inserting-the-data), let us deal with the infrastructure, and get querying!

## Conclusion

In this post, we’ve introduced the `git-import` tool and presented a query for our community to solve, with a t-shirt prize at stake! We encourage readers to explore the full list of questions and current answers and hope our community finds value in this data. In future posts, we’ll dive into some of the specific queries.

