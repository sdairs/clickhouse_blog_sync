---
title: "Announcing the ClickHouse Connector for AWS Glue"
date: "2025-08-13T09:01:35.314Z"
author: "Luke Gannon"
category: "Product"
excerpt: "Today, we’re announcing the launch of the official ClickHouse Connector for AWS Glue, which utilizes their Apache Spark-based serverless ETL engine. "
---

# Announcing the ClickHouse Connector for AWS Glue

## Available now in the AWS Marketplace

<style>
div.w-full + p, pre + p {
  text-align: center;
  font-style: italic;
}
</style>

AWS Glue is Amazon’s serverless data integration service that extracts, transforms, and loads data from or to multiple data sources and services. Today, we’re announcing the launch of the official [ClickHouse Connector for AWS Glue](https://clickhouse.com/docs/integrations/glue), which utilizes their Apache Spark-based serverless ETL engine. 

The new ClickHouse Connector for AWS Glue is built on our native Spark connector, enabling you to work with PySpark or Scala within Glue [notebooks](https://docs.aws.amazon.com/glue/latest/dg/using-notebooks-overview.html) or [ETL scripts](https://docs.aws.amazon.com/glue/latest/dg/edit-script.html). Our new connector eliminates the complexity of installing and managing the ClickHouse Spark connector. Now, with a few clicks, you can install it directly from the AWS Marketplace and add it to your Glue environment in no time. 

The connector is available today from the [AWS Marketplace](https://aws.amazon.com/marketplace/pp/prodview-eqvmuopqzdg7s). 

In this blog, we’ll learn how to build scalable production-ready Apache Spark Jobs with AWS Glue in Python.

## Setting up the connector

We’ll start by setting up the connector. 

### Prerequisites

Our connector will work with version 4 of AWS Glue.  The first thing you’ll need to verify is that you have access to the following versions and use the version below:

* ClickHouse Cloud **25.4+**  
* AWS Glue **4 (Spark 3.3, Scala 2, Python 3)**

:::global-blog-cta:::

## Get your ClickHouse connection details

Next, let’s gather the connection details for the ClickHouse service. You can find these by clicking the `Connect` button in ClickHouse Cloud.   

![0_awsglue.png](https://clickhouse.com/uploads/0_awsglue_4f41f0b02a.png)

Make a note of the following credentials, as we’ll be using them in a few steps.

* Host  
* Port  
* Username  
* Password

Note: It’s worth downloading your credentials when you create your service for later use; otherwise, if you lose your password, you’ll need to use the reset functionality in the `connect` modal.

#### Installing the connector via the Marketplace

To install the connector, go to the [AWS Marketplace](https://aws.amazon.com/marketplace/pp/prodview-eqvmuopqzdg7s) and search for “ClickHouse Connector for AWS Glue.” It’s free to subscribe and add to your organization's account.

![1_awsglue.png](https://clickhouse.com/uploads/1_awsglue_eda96c0796.png)

<div>Once you’ve subscribed, head to the Glue console via the search bar.</div>

#### Creating a connection

Finding the Data Connection menu item in the left-hand navigation, we can create a connection with the ClickHouse Connector for AWS Glue. Take note of the class name here; we’ll be reusing that later as part of our Spark configuration when setting up our job. 

![2_awsglue.png](https://clickhouse.com/uploads/2_awsglue_fe5b71e1b7.png)

<p class="image-description">ClickHouse Connector for AWS Glue Details page</p>

After selecting the Connector, you can create a connection, which requires you to supply a name and description that can be reused by many jobs. You can also set up networking options if the data you’re retrieving through your Glue job requires a [VPC connection](https://docs.aws.amazon.com/glue/latest/dg/getting-started-vpc-config.html) or access via a specific Security Group.

![3_awsglue.png](https://clickhouse.com/uploads/3_awsglue_197c517f0d.png)

<p>AWS Glue configurable network settings</p>

## Creating an AWS Glue Job

Heading back to ETL Jobs via the navigation, we can create a job using the script editor. The Visual UI is not supported at the moment, but we plan to add support for this option so that you can create jobs using the Glue no-code interface.

![4_awsglue.png](https://clickhouse.com/uploads/4_awsglue_e7a939aef6.png)

<p>The different AWS Glue options for creating jobs within Glue Studio</p>

Our first goal is to create a small job that writes test data to ClickHouse, so that we can verify our connection and that everything is set up correctly. The script editor provides a full IDE-like experience within the web browser, perfect for creating and editing Glue jobs. You can also set up version control for collaboration and review of Glue Job scripts, set a job on a schedule for repeated runs, and execute the job directly from the editor. 

![5_awsglue.png](https://clickhouse.com/uploads/5_awsglue_26e2adf9f1.png)

<p>AWS Glue Script tab code editor</p>

Before we get started with our script, we’re going to do some setup to make sure we’re using the right IAM permissions, selecting the right AWS Glue version, which will contain the right versions of Apache Spark, Scala, and Python, and configuring some parameters that can be used for our Spark Job.

### IAM Permissions for the Role

You will need to follow the AWS Documentation to [create an IAM](https://docs.aws.amazon.com/glue/latest/dg/create-an-iam-role.html) role that AWS Glue can assume when interacting with other AWS Services, such as temporarily writing to AWS S3 or reading data sources. Ensure the `glue:GetJob` and `glue:GetJobs` are also included in the [IAM roles for the role used in conjunction with the ClickHouse Connector for AWS Glue](https://docs.aws.amazon.com/glue/latest/dg/getting-started-min-privs-job.html#getting-started-min-privs-connectors).   

![6_awsglue.png](https://clickhouse.com/uploads/6_awsglue_26182f7b01.png)

<div>Now we can scroll down and check the environment versions for Spark, Glue, and Python.</div>

#### AWS Glue version

It’s important to note that the ClickHouse connector currently supports running Spark 3.3, Scala 2, and Python 3. You’ll need to configure the Glue Version to be version 4, which supports those versions. 

![7_awsglue.png](https://clickhouse.com/uploads/7_awsglue_38b7fc6679.png)

### Configuring Job Parameters 

I suggest also setting up some parameters that can be reused in the code. You don’t have to do this step, and could replace the arguments section in the script below with the values, but doing this makes it easier to run jobs against multiple environments like dev and production. I suggest creating the following job parameters that can be modified at runtime:

* CLICKHOUSE_HOST   
* CLICKHOUSE_PORT  
* CLICKHOUSE_USERNAME  
* CLICKHOUSE_PASSWORD

Note: parameters need to be supplied through the UI with a prefix of `--` for them to be picked up and used in scripts.  

![8_awsglue.png](https://clickhouse.com/uploads/8_awsglue_cf1f66dee3.png)

<p>Configuring job parameters under Job Details tab</p>

Heading back to the script tab, we can start building a script to prepare for ingesting data into ClickHouse. 

### Setting up the Spark Environment 

The first thing we need to set up is [registering the catalog](https://clickhouse.com/docs/integrations/apache-spark/spark-native-connector#register-the-catalog-required), the Spark catalog will hold the job parameters we created above. We can use the parameters by enhancing the `getResolvedOptions` method to get all the `CLICKHOUSE_` parameters we set up in the UI and then set them in our Spark configuration.

<pre><code type='click-ui' language='python'>
## @params: [JOB_NAME, CLICKHOUSE_HOST, CLICKHOUSE_PORT, CLICKHOUSE_USERNAME, CLICKHOUSE_PASSWORD]
args = getResolvedOptions(sys.argv, [
    'JOB_NAME',
    'CLICKHOUSE_HOST',
    'CLICKHOUSE_PORT',
    'CLICKHOUSE_USERNAME',
    'CLICKHOUSE_PASSWORD',
])

spark.conf.set("spark.sql.catalog.clickhouse", "com.clickhouse.spark.ClickHouseCatalog")
#  Protocol and SSL config for ClickHouse Cloud
spark.conf.set("spark.sql.catalog.clickhouse.protocol", "https")
spark.conf.set("spark.sql.catalog.clickhouse.option.ssl", "true")
spark.conf.set("spark.sql.catalog.clickhouse.option.ssl_mode", "NONE")
#  Connection details
spark.conf.set("spark.sql.catalog.clickhouse.host",args["CLICKHOUSE_HOST"])
spark.conf.set("spark.sql.catalog.clickhouse.http_port", args["CLICKHOUSE_PORT"])
spark.conf.set("spark.sql.catalog.clickhouse.user", args["CLICKHOUSE_USERNAME"])
spark.conf.set("spark.sql.catalog.clickhouse.password", args["CLICKHOUSE_PASSWORD"])
#  Suggestion: consider making this a parameter 
spark.conf.set("spark.sql.catalog.clickhouse.database", "default")
# spark.clickhouse.write.format default value is arrow
spark.conf.set("spark.clickhouse.write.format", "json")
#  spark.clickhouse.read.format default value is json
spark.conf.set("spark.clickhouse.read.format", "arrow")
</code></pre>

<p>Setting the Spark configuration from the resolved Glue Job parameters</p>

Now that the connector is set up, we can start looking at how we write and read data into ClickHouse. The first thing we’ll need to do is create a table in our database. We’re just going to create a narrow table containing employees and their identifiers for testing the connector.

### Managing database tables 

Our connector allows you to execute DDL operations with Spark SQL ([Spark Connector ANTLR Grammar](https://github.com/ClickHouse/spark-clickhouse-connector/blob/main/clickhouse-core/src/main/antlr/com.clickhouse/ClickHouseSQL.g4)), which is extremely handy for [creating](https://spark.apache.org/docs/4.0.0/sql-ref-syntax-ddl-create-table-datasource.html), [altering,](https://spark.apache.org/docs/latest/sql-ref-syntax-ddl-alter-table.html) or [dropping](https://spark.apache.org/docs/4.0.0/sql-ref-syntax-ddl-drop-table.html#content) tables and views. We will just create a simple table for this example that will house some data, containing an `id` and a `name`.

For more information about what data types ClickHouse supports, you can have a look through our [data types documentation](https://clickhouse.com/docs/sql-reference/data-types) when you’re creating your DDL.

<pre><code type='click-ui' language='python'>
logger.info("spark create tbl")
# use ClickHouse database
spark.sql(
    "USE clickhouse;"
)


# create table DDL in the database
spark.sql(
    """
    CREATE TABLE default.glue_job_example (
      id          BIGINT    NOT NULL COMMENT 'sort key',
      name       STRING
    ) USING ClickHouse
    TBLPROPERTIES (
      engine = 'MergeTree()',
      order_by = 'id'
    );
    """
)
</code></pre>

DDL operations using Spark SQL 

Note: We currently do not support sending multiple statements in a single method call. You will need to break these into individual calls.

### Writing data to ClickHouse

We will import Row from `pyspark.sql` to create our dataframe and populate it with employee data. It’s trivial to write data from Dataframes into ClickHouse; the simplest method is to use the `writeTo` method introduced in Spark 3 with the introduction of the `DataFrameWriteV2` API.

<pre><code type='click-ui' language='python'>
from pyspark.sql import Row

# Create DataFrame
data = [
    Row(id=6, name="Mark"), 
    Row(id=19, name="LAEG"),
    Row(id=50, name="Jim"),
    Row(id=71, name="Ian"),
    Row(id=12, name="APCJ"),
    Row(id=11, name="Peter"),
    Row(id=71, name="Eva"),
    Row(id=17, name="Jonny"),
    Row(id=40, name="Anthony"),
    Row(id=55, name="Petra"),
    Row(id=42, name="Nigel"),
    Row(id=48, name="BBC"),
]
df = spark.createDataFrame(data)

# Write DataFrame to ClickHouse
df.writeTo("clickhouse.default.glue_job_example")
    .append()
</code></pre>


Writing a Dataframe into a simple table in ClickHouse 

### Aggregating data sources before writing data to ClickHouse

If we wanted to do some preprocessing and merge two sets of data to create a wide table within ClickHouse, we could use Spark to read from disparate data sources. Below is a pseudo example of taking a dataframe, reading data from S3, and creating summaries before ingesting into ClickHouse.

<pre><code type='click-ui' language='python'>
# Read from multiple sources
first_df = ...
    
# Maybe we need to read from another datasource like S3
second_df = spark.read.parquet("s3://.../")
    
# We can join and create aggregated summaries before ingesting the data into ClickHouse
combined_df = first_df 
    .join(second_df, "column_to_join_on") 
    .groupBy("column_to_group_by_1", "column_to_group_by_2") 
    .agg(
        sum("column_to_sum").alias("sum_column_name"),
        count("column_to_count").alias("count_of_entries_column"),
        avg("column_to_average").alias("avg_column_name")
    )
    
# Write 
df.writeTo("clickhouse.database_name.table_name")
  .append()
</code></pre>

<p>Combining dataframes before writing to ClickHouse</p>

### Reading data from ClickHouse

You can read data from Clickhouse directly into a dataframe using the `spark.sql` method. Here we’re just going to read all the data we’ve ingested in the previous step by using a simple select query and logging it to the output.

<pre><code type='click-ui' language='python'>
# Read DataFrame from ClickHouse
df_read = spark.sql("""
    SELECT 
        *
    FROM 
        clickhouse.default.glue_job_example
""")

# Take the first 10 records from the dataframe
logger.info(str(df.take(10)))
</code></pre>

<p>Reading from ClickHouse into a Spark Dataframe</p>

#### Full scripts for the example Glue job

Copy and paste the whole script into your AWS Glue job. Remember to configure the connector, your environment, and variables as shown above!

<pre><code type='click-ui' language='python'>
import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql import Row

## @params: [JOB_NAME, CLICKHOUSE_PORT, CLICKHOUSE_USERNAME, CLICKHOUSE_PASSWORD]
args = getResolvedOptions(sys.argv, ['JOB_NAME',
    'CLICKHOUSE_HOST',
    'CLICKHOUSE_PORT',
    'CLICKHOUSE_USERNAME',
    'CLICKHOUSE_PASSWORD',
])

sc = SparkContext()
glueContext = GlueContext(sc)
logger = glueContext.get_logger()
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

logger.debug("setting spark conf")
spark.conf.set("spark.sql.catalog.clickhouse", "com.clickhouse.spark.ClickHouseCatalog")

#  Protocol and SSL config for ClickHouse Cloud
spark.conf.set("spark.sql.catalog.clickhouse.protocol", "https")
spark.conf.set("spark.sql.catalog.clickhouse.option.ssl", "true")
spark.conf.set("spark.sql.catalog.clickhouse.option.ssl_mode", "NONE")

#  Connection details
spark.conf.set("spark.sql.catalog.clickhouse.host",args["CLICKHOUSE_HOST"])
spark.conf.set("spark.sql.catalog.clickhouse.http_port", args["CLICKHOUSE_PORT"])
spark.conf.set("spark.sql.catalog.clickhouse.user", args["CLICKHOUSE_USERNAME"])
spark.conf.set("spark.sql.catalog.clickhouse.password", args["CLICKHOUSE_PASSWORD"])

#  Suggestion: consider making the database name a parameter for use in different environments
spark.conf.set("spark.sql.catalog.clickhouse.database", "default")
spark.conf.set("spark.clickhouse.write.format", "json")
#  spark.clickhouse.read.format default value is json
spark.conf.set("spark.clickhouse.read.format", "arrow")
logger.debug("spark conf set")

logger.debug("creating table in ClickHouse")
# use ClickHouse database
spark.sql(
    "USE clickhouse;"
)

# create table DDL in the database
spark.sql(
    """
    CREATE TABLE default.glue_job_example (
      id          BIGINT    NOT NULL COMMENT 'sort key',
      name       STRING
    ) USING ClickHouse
    TBLPROPERTIES (
      engine = 'MergeTree()',
      order_by = 'id'
    );
    """
)
logger.debug("table created in ClickHouse")

# Create the DataFrame
data = [
    Row(id=6, name="Mark"), 
    Row(id=19, name="Luke"),
    Row(id=50, name="Jim"),
    Row(id=71, name="Ian"),
]
df = spark.createDataFrame(data)

# Write DataFrame to ClickHouse
df.writeTo("clickhouse.default.glue_job_example")
    .append()
logger.debug("data ingested into ClickHouse")

# Read DataFrame from ClickHouse
df_read = spark.sql("""
    SELECT 
        *
    FROM 
        clickhouse.default.glue_job_example
""")

logger.debug("data read from ClickHouse")
logger.debug(str(df.take(10)))

job.commit()
</code></pre>

## Taking your AWS Glue pipeline to production

Of course, the above examples are just to get you started, but as you are developing your scripts in AWS Glue, it is always good to think about how you make and manage your pipelines in a reusable and scalable way for production workloads. Here are some things to consider:

#### Tuning your Glue job

Considering and tuning your batch size of data and the types it contains will be crucial for performance. As part of your `.writeTo` method, you can add options to tune the `batchsize`, `socket_timeout`, and `connection_timeout`. I recommend going through all the [Spark Connector configuration options](https://clickhouse.com/docs/integrations/apache-spark/spark-native-connector#configurations), selecting and tuning the ones that make the most sense for your data shape and use case. 

<pre><code type='click-ui' language='python'>
# ClickHouse batch and connection settings
...
.option("batchsize", "100000")  
.option("socket_timeout", "300000")  
.option("connection_timeout", "10000") 
...
</code></pre>

#### Using your Glue Job as part of a Glue Workflow

How and when your Glue jobs run are crucial to your data pipeline. AWS Glue provides [Glue Workflows](https://docs.aws.amazon.com/glue/latest/dg/workflows_overview.html) that allow you to configure triggers to kick off the execution of your Glue job. There are several ways you can trigger your job using Glue workflows:

* Schedule  
* On-demand (via Console, API, or CLI)  
* EventBridge events

Below, we can set up a scheduled trigger in the Glue workflow console to run our job every day at 9 a.m.   

![9_awsglue.png](https://clickhouse.com/uploads/9_awsglue_d7c0fc29aa.png)

<p>Creating a scheduled trigger in Glue Workflows</p>

![10_awsglue.png](https://clickhouse.com/uploads/10_awsglue_cdfda9968c.png)

<p>Editing job parameters for different environments</p>

We could customize our job parameters so that a job can populate different environments, with different amounts of data into different tables. Follow the configuring job parameters section above and modify the script to add additional parameters.     


![11_awsglue.png](https://clickhouse.com/uploads/11_awsglue_873352c7a3.png)

<p>Adding parameters for your Glue Job within your Glue Workflow</p>

### Programmatically creating Glue Jobs with Cloud Formation

There are many neat features that help with managing and scheduling AWS Glue jobs. For example, you can create and manage version-controlled configurations by using [AWS Cloud Formation](https://docs.aws.amazon.com/glue/latest/dg/populate-with-cloudformation-templates.html) to define ETL objects like scripts or triggers. 

Below is an example of creating a cron job for an AWS Glue job that runs every 10 minutes Monday to Friday.

<pre><code type='click-ui' language='yaml'>

---
AWSTemplateFormatVersion: '2010-09-09'
# Sample CFN YAML to demonstrate creating a scheduled trigger
#
# Parameters section contains names that are substituted in the Resources section
# Parameters for CFN template
Parameters:
  # The existing Glue Job to be started by this trigger 
  CFNJobName:
    Type: String
    Default: <NAME OF YOUR GLUE JOB>
  # The name of the trigger to be created
  CFNTriggerName:
    Type: String
    Default: <NAME OF YOUR TRIGGER>	
#
# Sample CFN YAML to demonstrate creating a scheduled trigger for a job
#	
Resources:                                      
# Create trigger to run an existing job (CFNJobName) on a cron schedule.	
  TriggerSample1CFN:
    Type: AWS::Glue::Trigger   
    Properties:
      Name:
        Ref: CFNTriggerName		
      Description: Trigger created with CloudFormation
      Type: SCHEDULED                                                        	   
      Actions:
        - JobName: !Ref CFNJobName                	  
        # Arguments: JSON object
      # # Run the trigger every 10 minutes on Monday to Friday 		
      Schedule: cron(0/10 * ? * MON-FRI *) 
</code></pre>

Example of creating an [AWS Cloud Formation template to schedule Glue Job](https://docs.aws.amazon.com/glue/latest/dg/populate-with-cloudformation-templates.html)

## What's next for the ClickHouse Connector for AWS Glue? 

With the first release of ClickHouse Connector for AWS Glue, we focused on the most common use case we see in production - batch write operations. We’re looking towards the future to extend the functionality and enhance the user experience. 

Before the end of the year, we’ll look to support AWS Glue’s no-code visual interface to make it even simpler for creating and managing dataflows within

The connector's roadmap includes adding more support for IAM roles with AWS Secret Manager and Glue catalog crawler for automated discovery of data sources. If you’re interested in particular features being added, you can [submit an integration request](https://console.clickhouse.cloud/integrations) directly in ClickHouse Cloud.

![12_awsglue.png](https://clickhouse.com/uploads/12_awsglue_a6298e4eeb.png)

<p>Integrations tab within ClickHouse Cloud with “Request a new integration”</p>

## Ready to get started?

If you’re also excited about the potential of using Spark Jobs inside of AWS Glue, [sign up to ClickHouse Cloud](https://console.clickhouse.cloud/signUp) to get **$300 of trial credits** that you can use to create a database service on AWS. You can then subscribe to “ClickHouse Connector for AWS Glue” for free by finding it on the [AWS Marketplace](https://aws.amazon.com/marketplace/pp/prodview-eqvmuopqzdg7s). 

If you have any feedback, feature requests, or issues relating to Apache Spark, you can [create an issue](https://github.com/ClickHouse/spark-clickhouse-connector/issues) in the [ClickHouse Connector for Apache repository](https://github.com/ClickHouse/spark-clickhouse-connector). Don’t forget to share your experiments and use cases with others in our [ClickHouse Community Slack](https://clickhousedb.slack.com/join/shared_invite/zt-2nvsplppi-I7FnTTjR9zCLAbOZnyqb4g)!
