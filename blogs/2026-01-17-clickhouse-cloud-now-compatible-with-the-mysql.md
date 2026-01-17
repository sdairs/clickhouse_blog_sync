---
title: "ClickHouse Cloud now Compatible with the MySQL Protocol"
date: "2023-10-05T12:20:54.218Z"
author: "Ryadh Dahimene"
category: "Engineering"
excerpt: "ClickHouse Cloud is now compatible with the MySQL protocol unlocking BI tools such as Looker Studio for our users "
---

# ClickHouse Cloud now Compatible with the MySQL Protocol

ClickHouse's compatibility with third-party business intelligence tools and data visualization platforms is crucial for deriving insights from the stored data. Tools like Superset, Metabase, and Grafana can connect natively to ClickHouse and help users create fast and meaningful dashboards and reports, leveraging ClickHouse’s unbeatable performance and versatility. 

However, some of our users deploy tools that do not yet provide a native ClickHouse connector. Often, these tools are also proprietary solutions and don’t offer easy ways for us to contribute a native integration. To address this requirement, we are thrilled today to announce that compatibility can be achieved leveraging the [MySQL interface for ClickHouse](https://clickhouse.com/docs/en/interfaces/mysql), now available in ClickHouse Cloud. As of the time of writing this, compatibility allows our users to use Looker Studio and Tableau online with ClickHouse with support for Amazon QuickSight under active development.

<iframe width="768" height="432" src="https://www.youtube.com/embed/Lb0_f3xAWqE?si=ZtJVlwESDhDbXCZd&amp;start=2200" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>

## A concrete example with ClickHouse Cloud and Google Looker Studio

We designed an opt-in experience for the MySQL interface in ClickHouse Cloud in order to limit the network exposure of Cloud services by default. Using the connection string screen, you can now access the MySQL tab and decide to enable the MySQL interface for your service.

![mysql_protocol_enable.png](https://clickhouse.com/uploads/mysql_protocol_enable_918aa8a730.png)

Once enabled, your ClickHouse Service will expose port 3306 and prompt you with your MySQL connection string that includes your unique MySQL username. The password will be the same as the service's default user password.

With these settings, you can now go to your [Looker Studio](https://lookerstudio.google.com/) interface,declare a new MySQL Data Source, and provide the provided credentials. 

![looker_mysql.png](https://clickhouse.com/uploads/looker_mysql_53e2568b78.png)

In the Looker Studio UI, you’ll need to check the "Enable SSL" option. ClickHouse Cloud's SSL certificate is signed by LetsEncrypt. You can download this root cert [here](https://letsencrypt.org/certs/isrgrootx1.pem) and upload it in Looker Studio. 

![enable_ssl_mysql.png](https://clickhouse.com/uploads/enable_ssl_mysql_42acf992ac.png)

That’s it! In a few steps, you now have a working connection in place between Looker Studio and ClickHouse Cloud that is using the MySQL interface. Alternatively, you can also leverage this interface to accelerate the migration of your custom applications built for MySQL to ClickHouse Cloud for faster analytics capabilities at scale.

![hackernews_looker.png](https://clickhouse.com/uploads/hackernews_looker_5ab1e4313d.png)

## What’s next?

We tested this feature extensively with Google Looker Studio and Tableau online and improved the overall compatibility of the MySQL interface in ClickHouse by addressing [numerous issues](https://github.com/ClickHouse/ClickHouse/issues?q=is%3Aissue+%22MySQL%22+author%3Aslvrtrn+) (shoutout to Serge Klochkov and Robert Schulze for the great work!). For a detailed description of the work done and efforts made by Serge and the team, see [here](https://clickhouse.com/blog/mysql-support-in-clickhouse-the-journey). We’ll be continuing this evaluation and continuous improvement on different platforms, prioritized based on user feedback. As of now, we are already exploring Microsoft PowerBI and Amazon QuickSight.

As always, user feedback is extremely valuable. If you experience limitations with this functionality for a specific tool or platform or you’d like to see support for another tool, please don’t hesitate to reach out to us ([contact form](https://clickhouse.com/company/contact), [new issue](https://github.com/ClickHouse/ClickHouse/issues/new/choose)).
