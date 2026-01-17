---
title: "Under the Hood: Building MySQL Change Data Capture in ClickPipes"
date: "2025-05-13T15:31:24.035Z"
author: "Kaushik Iska, Philip Dubé"
category: "Engineering"
excerpt: "CDC is a critical pattern in modern data architectures that require real-time data integration. In this deep dive, we'll explore how ClickPipes implements CDC for MySQL databases."
---

# Under the Hood: Building MySQL Change Data Capture in ClickPipes

## **Introduction**

Change Data Capture (CDC) is a critical pattern in modern data architectures that require real-time data integration. In this technical deep dive, we'll explore how ClickPipes—the native data integration solution in ClickHouse Cloud—implements CDC for MySQL databases. This article presents the internals of our MySQL CDC implementation for engineers and architects who want to understand the mechanisms that power reliable, high-performance database replication.


## **MySQL Replication Fundamentals**

Let’s start by going over the fundamentals of replication in MySQL.


### **Binary Logs: The Foundation of MySQL CDC**

MySQL's binary log (binlog) is the cornerstone of its replication architecture. It records all changes to database data and structure sequentially, as shown in the diagram below:



![01.png](https://clickhouse.com/uploads/01_a677bd56ca.png)


The binary log contains events representing:



* Data manipulation (INSERT, UPDATE, DELETE)
* Data definition (CREATE, ALTER, DROP)
* Transaction boundaries (BEGIN, COMMIT, ROLLBACK)

Each binary log event has an event header with metadata (timestamp, server ID, etc.) and an event body with the actual change data.


### **Binary Log Formats**

MySQL offers three binlog formats:



1. **STATEMENT**: Logs SQL statements
    * Small log size
    * Non-deterministic functions may cause replication issues
    * Not suitable for CDC
2. **ROW**: Logs changed rows
    * Records before/after images of changed rows
    * Highest fidelity but larger log size
    * **Required for CDC**
3. **MIXED**: Uses STATEMENT by default, switches to ROW when needed
    * Not suitable for CDC

**Prerequisite — binlog_row_image = FULL**

ClickPipes needs every row change in the MySQL binary log to carry the complete before- and after-image, so the source must run with binlog_row_image='FULL' (this is the default in MySQL 8.x). Lighter modes such as MINIMAL or NOBLOB drop unchanged columns to save space, but they prevent ClickPipes from replaying updates idempotently and from handling primary-key rewrites safely. The change to binlog_row_image = FULL mainly increases UPDATE-heavy binlogs, while inserts and deletes stay the same, so the overhead is usually modest.


### **Global Transaction Identifiers (GTIDs)**

GTIDs provide a consistent way to identify transactions across servers:

```
GTID = source_id:transaction_id
```

Example GTID set: `123e4567-e89b-12d3-a456-426614174000:1-1000,2000-3000`

Benefits of GTID-based replication:



* Transaction tracking across server restarts
* Simpler failover and high availability
* Easier replication topology changes


## **ClickPipes MySQL CDC Architecture**

ClickPipes implements CDC for MySQL through a robust architecture that handles both initial data loading and continuous replication.


### **Architecture Overview**

The diagram below shows the architecture of MySQL CDC in ClickPipes:



![02.png](https://clickhouse.com/uploads/02_a591171ab6.png)


The ClickPipes MySQL CDC pipeline consists of several key components:



1. **Connection Management**: Establishes and maintains connections to the source MySQL database
2. **Binlog Syncer**: Connects to MySQL's binary log stream
3. **Event Processor**: Processes binary log events into structured change records
4. **Schema Registry**: Tracks the structure of source tables
5. **Checkpointing**: Records progress to enable resumption after failures
6. **Transformation Layer**: Converts MySQL types to ClickHouse types
7. **Sink Layer**: Writes data to ClickHouse efficiently


### **Connection and Setup**

When a MySQL CDC flow starts, ClickPipes:



1. Validates MySQL configurations
    * Ensures binlog_format = 'ROW'
    * Checks binlog_row_image = 'FULL'
    * Verifies binlog retention settings
2. Examines replication capabilities
    * Detects GTID support
    * Establishes replication position
3. Extracts table schemas
    * Retrieves column definitions and types
    * Identifies primary keys
    * Maps MySQL types to ClickHouse types


### **Initial Data Loading**

Before streaming changes, ClickPipes performs an initial snapshot:



![442909790-f9daa28f-1445-42fb-8cfb-3f801aca6e07.png](https://clickhouse.com/uploads/442909790_f9daa28f_1445_42fb_8cfb_3f801aca6e07_28bcc7019d.png)


This process:



1. Creates a consistent snapshot of the data
2. Sets up the target tables in ClickHouse
3. Records the binlog position or GTID to start streaming from


### **Streaming Changes**

After initial loading, ClickPipes streams changes continuously:



![442909792-be7c8e3c-6e63-49ac-b563-38330378f10c.png](https://clickhouse.com/uploads/442909792_be7c8e3c_6e63_49ac_b563_38330378f10c_14c5224d05.png)


The streaming process:



1. Connects to MySQL's binlog stream
2. Processes events in transaction order
3. Converts row events to structured change records
4. Applies changes to ClickHouse
5. Updates checkpoints to track progress


## **GTID vs. Binlog Position-Based Replication**

ClickPipes supports both replication methods:


### **GTID-Based Replication**

GTIDs provide a logical, consistent way to track transactions. When a transaction completes, the GTID set is updated and stored in the checkpoint. This mechanism supports efficient resumption and is resilient to server restarts or topology changes.


### **Binlog Position-Based Replication**

Traditional binlog position tracking works with file names and positions. When a file rotation event occurs, the position is updated with the new file name and position. Though effective, this approach is less resilient to server changes and more complex to manage in high-availability setups. In case of fail-over you will have to resync a pipe.


## **Processing Binary Log Events**

ClickPipes processes several types of binlog events:


### **Row Events**



![442909788-f2a647f4-b22d-41a6-abf5-e5c6580fb78b.png](https://clickhouse.com/uploads/442909788_f2a647f4_b22d_41a6_abf5_e5c6580fb78b_0c1f373155.png)


The pipeline handles:



1. **INSERT operations**: Extracts column values and creates insert records
2. **UPDATE operations**: Captures both before/after values and creates update records
3. **DELETE operations**: Extracts column values and creates delete records


### **Schema Change Events**

ClickPipes detects and processes schema changes by parsing DDL statements. The system:



1. Uses TiDB's SQL parser to parse DDL statements
2. Extracts schema changes (especially column additions)
3. Updates the schema registry
4. Propagates changes to target tables


## **Type Mapping and Conversion**

ClickPipes handles the full range of MySQL data types:


<table>
  <tr>
   <td><strong>MySQL Type</strong>
   </td>
   <td><strong>ClickHouse Type</strong>
   </td>
   <td><strong>Notes</strong>
   </td>
  </tr>
  <tr>
   <td>TINYINT
   </td>
   <td>Int8/UInt8
   </td>
   <td>Unsigned variants map to UInt
   </td>
  </tr>
  <tr>
   <td>TINYINT(1)
   </td>
   <td>Bool
   </td>
   <td>
   </td>
  </tr>
  <tr>
   <td>SMALLINT
   </td>
   <td>Int16/UInt16
   </td>
   <td>
   </td>
  </tr>
  <tr>
   <td>MEDIUMINT
   </td>
   <td>Int32/UInt32
   </td>
   <td>(MySQL has 24 bit integers)
   </td>
  </tr>
  <tr>
   <td>INT
   </td>
   <td>Int32/UInt32
   </td>
   <td>
   </td>
  </tr>
  <tr>
   <td>BIGINT
   </td>
   <td>Int64/UInt64
   </td>
   <td>
   </td>
  </tr>
  <tr>
   <td>FLOAT
   </td>
   <td>Float32
   </td>
   <td>
   </td>
  </tr>
  <tr>
   <td>DOUBLE
   </td>
   <td>Float64
   </td>
   <td>
   </td>
  </tr>
  <tr>
   <td>DECIMAL
   </td>
   <td>Decimal
   </td>
   <td>Preserves precision and scale
   </td>
  </tr>
  <tr>
   <td>CHAR/VARCHAR/TEXT
   </td>
   <td>String
   </td>
   <td>
   </td>
  </tr>
  <tr>
   <td>BINARY/VARBINARY/BLOB
   </td>
   <td>String
   </td>
   <td>
   </td>
  </tr>
  <tr>
   <td>JSON
   </td>
   <td>String
   </td>
   <td>Preserved as JSON text
   </td>
  </tr>
  <tr>
   <td>DATE
   </td>
   <td>Date32
   </td>
   <td>
   </td>
  </tr>
  <tr>
   <td>TIME
   </td>
   <td>DateTime64(6)
   </td>
   <td>The date portion is Unix epoch
   </td>
  </tr>
  <tr>
   <td>YEAR
   </td>
   <td>Int16
   </td>
   <td>
   </td>
  </tr>
  <tr>
   <td>DATETIME/TIMESTAMP
   </td>
   <td>DateTime64(6)
   </td>
   <td>
   </td>
  </tr>
  <tr>
   <td>ENUM
   </td>
   <td>LowCardinality(String)
   </td>
   <td>
   </td>
  </tr>
  <tr>
   <td>SET
   </td>
   <td>String
   </td>
   <td>Comma-separated values
   </td>
  </tr>
  <tr>
   <td>BIT
   </td>
   <td>UInt64
   </td>
   <td>
   </td>
  </tr>
  <tr>
   <td>GEOMETRY
   </td>
   <td>String
   </td>
   <td>WKT format
   </td>
  </tr>
  <tr>
   <td>VECTOR
   </td>
   <td>Array(Float32)
   </td>
   <td>For MySQL 8.4+
   </td>
  </tr>
</table>


The type conversion system handles edge cases like:



* Enum/Set value lookups (requires binlog_row_metadata)
* Binary data processing


## **Performance Optimizations**

ClickPipes implements several optimizations for MySQL CDC:


### **Transaction Batching**

Changes are grouped by transaction to maintain consistency, with configurable batch sizes.


### **Idle Timeout**

The system uses idle timeouts to detect when no data is flowing, preventing resource wastage during periods of inactivity.


### **Parallelism**

The system uses parallel processing where possible:



* Parallel schema retrieval
* Batched table processing
* Concurrent ClickHouse writes


### **Backoff Strategy**

Intelligent retry logic with exponential backoff ensures resilience against transient failures.


## **Monitoring and Observability**

ClickPipes provides comprehensive monitoring for MySQL CDC flows. Key metrics include:



* Records processed per second
* Bytes read from binlog
* Replication lag
* Error rates
* Current position/GTID


## **Handling Failure Scenarios**

ClickPipes implements robust error handling for various failure scenarios:


### **Connection Failures**

The system automatically retries connections with backoff, handling transient network issues gracefully.


### **Schema Skew**

The system detects and reports on schema skew, ensuring that differences between source and target schemas don't cause silent data corruption.


### **Resumption After Failure**

The system maintains checkpoints to resume after failures, ensuring that data is not lost or duplicated.


## **Open Source Contributions**

Building the MySQL CDC functionality in ClickPipes required significant enhancements to the open source libraries we use. Our team has contributed several improvements to the `go-mysql-org/go-mysql` library, which powers our CDC implementation:



* [MariaDB authentication support](https://github.com/go-mysql-org/go-mysql/pull/998)
* [Modern logging with log/slog](https://github.com/go-mysql-org/go-mysql/pull/993)
* [Bitwise optimizations for improved performance](https://github.com/go-mysql-org/go-mysql/pull/995)
* [Context support for SQL driver](https://github.com/go-mysql-org/go-mysql/pull/997)
* [MySQL vector type support](https://github.com/go-mysql-org/go-mysql/pull/1004)

These contributions ensure that ClickPipes uses a robust, well-maintained foundation for MySQL replication.


## **Best Practices**

For optimal MySQL CDC performance with ClickPipes:



1. **MySQL Configuration**
    * Set `binlog_format = 'ROW'`
    * Set `binlog_row_image = 'FULL'`
    * Set `binlog_row_metadata = 'FULL'` (for column filtering, avoiding issues due to dropped columns on source, & rich enum/set support)
    * Set adequate binlog retention (at least 24 hours)
2. **Table Design**
    * Use primary keys on all tables
    * Avoid large object columns in high-change tables
    * Consider partitioning large tables
3. **Network Optimization**
    * Co-locate ClickPipes and MySQL when possible
    * Use VPC peering or private connectivity
    * Enable TLS for secure transmission
4. **Monitoring**
    * Track replication lag
    * Monitor binlog growth rate
    * Set up alerts for replication delays


## **Benchmarks and Performance**

Comprehensive performance benchmarks for ClickPipes MySQL CDC will be published soon. Initial testing shows promising results across various workloads, including high-frequency small transactions, large bulk operations, and realistic mixed workloads. The system is designed to handle tens of thousands of changes per second with sub 30s latency under optimal conditions.


## **Limitations and Edge Cases**

ClickPipes MySQL CDC has some limitations:



1. **Schema Changes**:
    * Column additions are fully supported
    * Column drops and renames are detected but not propagated
    * Table renames require manual intervention
2. **Data Types**:
    * Binary data must be within size limits
3. **Replication Requirements**:
    * Binary logs must be enabled and properly configured
    * Sufficient privileges are required
    * Tables must have primary keys for optimal performance
4. **TRUNCATE** operations are not supported.


## **Conclusion**

ClickPipes MySQL CDC provides a robust, high-performance solution for capturing and processing changes from MySQL databases. By leveraging MySQL's native replication capabilities and implementing intelligent processing pipelines, it enables real-time data integration with ClickHouse.

The system's architecture balances reliability, performance, and ease of use, making it suitable for a wide range of use cases from operational data stores to analytics pipelines. By understanding the inner workings of the MySQL CDC implementation, users can optimize their data flows and troubleshoot issues more effectively.

For more information on setting up MySQL CDC with ClickPipes, refer to the[ official documentation](https://clickhouse.com/docs/en/integrations/clickpipes). [MySQL CDC in Clickpipes is now available in Private Preview please give it a try](https://clickhouse.com/blog/mysql-cdc-connector-clickpipes-private-preview)!


## **References**



1. [MySQL Binary Log Documentation](https://dev.mysql.com/doc/refman/8.4/en/binary-log.html)
2. [ClickPipes for MySQL Documentation](https://clickhouse.com/docs/integrations/clickpipes/mysql)
3. [go-mysql-org/go-mysql library](https://github.com/go-mysql-org/go-mysql)