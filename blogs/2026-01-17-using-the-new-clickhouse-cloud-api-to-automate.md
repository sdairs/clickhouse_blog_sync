---
title: "Using the New ClickHouse Cloud API to Automate Deployments"
date: "2023-05-30T17:12:23.680Z"
author: "Krithika Balagurunathan"
category: "Product"
excerpt: "Explore the endless possibilities of ClickHouse Cloud's API integration and elevate your data management experience. Seamlessly control & automate deployments."
---

# Using the New ClickHouse Cloud API to Automate Deployments

We are thrilled to announce API support for ClickHouse Cloud that lets you manage your services programmatically.

Modern DevOps frameworks are centered around APIs that automate and streamline deployments. With the newly introduced ClickHouse Cloud API support, you can effortlessly manage your ClickHouse Cloud services within your existing CI/CD pipeline and programmatically perform operations, such as service provisioning, configuration, and scaling.

Common use cases for ClickHouse Cloud API include:

* **Automated provisioning and deprovisioning** – The ClickHouse Cloud API enables automation of various tasks, including programmatically provisioning, configuring, and managing services. This automation saves time and effort by eliminating manual processes, reducing the risk of human errors, and ensuring consistency across environments.
* **Scheduled scaling** – The ClickHouse Cloud API allows you to override auto scaling controls, either scheduled or unscheduled. By adjusting the resource allocation, you can ensure optimal performance and cost efficiency.
* **Flexible configuration management** – You can leverage tools like Ansible, Chef, and Puppet to automate deployments quickly.

ClickHouse Cloud API support includes the ability to:

* Perform lifecycle operations on ClickHouse services, such as launching, starting, and stopping services.
* Configure advanced scaling policies, including minimum and maximum size and idling.
* Manage user access, API keys, and IP Access Lists
* Monitor backup operational status.
* List and update organizational details, including invitations

## To get started with ClickHouse Cloud API

Create an account or login with [ClickHouse Cloud](https://clickhouse.cloud/signUp?utm_source=clickhouse&utm_medium=website&utm_campaign=blog-api). We offer a 30-day trial with $300 in usage credits for new users. Navigate to the API Keys tab, and follow the prompts for generating a key and setting your policy. For more information, please see our documentation [here](https://clickhouse.com/docs/en/cloud/manage/openapi).

![01-create-api-key.png](https://clickhouse.com/uploads/01_create_api_key_4f3856f476.png)

We take measures to secure your API key, secret, and connection. Only the last four characters of your key are stored in our database and are visible after setup so you can identify them in the activity log. Both the key and secret are generated using a cryptographically secure random character generator and stored using a strong hashing algorithm with salt. A web application firewall protects the API endpoint to prevent abuse.

Refer to the REST [API specification](https://clickhouse.com/docs/en/cloud/manage/api/swagger) for the detailed list of supported operations:

![02-api-spec.png](https://clickhouse.com/uploads/02_api_spec_d1c6931697.png)

If you are a Postman user, you can simply import the spec to get set up. API operations are limited to 10 requests every 10 seconds.

![03-postman.png](https://clickhouse.com/uploads/03_postman_372e070398.png)

## What's Next?

We are excited to continue to develop the ClickHouse Cloud API and make it a powerful tool for developers. In the next weeks and months, we are working to:

* Add more methods to the specification, including the ability to:
    * View usage and billing information, including a breakdown of costs by unit and service.
    * View metrics, such as storage, memory allocation, and query stats.
* Develop a Terraform provider to further improve the tooling by allowing developers to automate the creation and management of ClickHouse Cloud services.
* Introduce API support for database operations, such as managing databases, tables, and users.
* Support advanced authentication methods, including Hash-based Message Authentication Code (HMAC).

## Get started today

If you are already a ClickHouse Cloud user, you can log into your service to start using the API. If you are not yet a user, you can [start a ClickHouse Cloud trial today](https://clickhouse.cloud/signUp?utm_source=clickhouse&utm_medium=website&utm_campaign=blog-api) and receive $300 of free credit to get going with your real-time analytics use case!
