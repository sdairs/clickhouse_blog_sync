---
title: "ClickPipes is Now Generally Available"
date: "2023-09-26T12:33:53.186Z"
author: "Ryadh Dahimene"
category: "Product"
excerpt: "Extracting valuable insights for real-time analytics applications often depends on the availability of fresh and clean data. Streamlined access to this data is a game changer for data-driven decision making."
---

# ClickPipes is Now Generally Available

Extracting valuable insights for real-time analytics applications often depends on the availability of fresh and clean data. Streamlined access to this data is a game changer for data-driven decision making.

Today at ClickHouse, we are thrilled to [announce the general availability of ClickPipes](/blog/clickhouse-announces-clickpipes?loc=clickpipes-ga-blog), our continuous data ingestion service for [ClickHouse Cloud](/cloud?loc=clickpipes-ga-blog).

This represents a significant milestone for ClickHouse Cloud. Since ClickPipes was initially announced mid-July in [private beta](/blog/clickhouse-cloud-clickpipes-for-kafka-managed-ingestion-service?loc=clickpipes-ga-blog), it has been used by organizations to successfully unlock real-time analytics use-cases, allowing them to ingest data easily and focus on the important part: extracting insights thanks to ClickHouse’s unparalleled performance.

For GA, we added the following features to ClickPipes:

- Support for Confluent Cloud’s schema registry (JSON_SR)
- Support for Amazon MSK 
- ClickPipes specific metrics, available in the details panel to display count and size of ingested data + errors if any
- Support for more data types including FixedString, Date, DateTime, Tuple and Array, JSON
- UI/UX and reliability improvements

![clickpipes_1mn-min.gif](https://clickhouse.com/uploads/clickpipes_1mn_min_0c61fc05dc.gif)

Key ClickPipes features include:

- **Easy and intuitive data onboarding**: Setting up a new ingestion pipeline takes just a few steps. Select an incoming data source and format, tune your schema, and let your pipeline run.
- **Built for continuous ingestion**: ClickPipes manages your continuous ingestion pipelines so that you don’t have to. Set up your pipeline and let us handle the rest.
- **Designed for speed and scale**: ClickPipes provides the scalability you need to handle increasing data volumes, ensuring your systems can handle future demands effortlessly.
- **Unlock your real time analytics**: Built leveraging our deep expertise in real time data management systems, ClickPipes handles the complexities of real time ingestion for optimal performance.

![Screenshot 2023-09-26 at 12.31.29.png](https://clickhouse.com/uploads/Screenshot_2023_09_26_at_12_31_29_6f3bdb8962.png)

## Give ClickPipes a spin today!

You can find the documentation and a tutorial about how to [get started here](https://clickhouse.com/docs/en/integrations/clickpipes). As always, we’d love to hear your feedback and suggestions ([contact us](/company/contact?loc=clickpipes-ga-blog)).

## Links:

- [Press Release](/blog/clickhouse-announces-clickpipes?loc=clickpipes-ga-blog)
- [ClickPipes Website](/cloud/clickpipes?loc=clickpipes-ga-blog)
- [Video demonstration](/videos/clickpipes-demo?loc=clickpipes-ga-blog)
- [Documentation](https://clickhouse.com/docs/en/integrations/clickpipes)


