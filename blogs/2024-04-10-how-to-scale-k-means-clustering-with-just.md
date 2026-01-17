---
title: "How to Scale K-Means Clustering with just ClickHouse SQL"
date: "2024-04-10T11:53:37.389Z"
author: "Dale McDiarmid"
category: "Engineering"
excerpt: "Learn how to scale K-Means clustering to billions of rows using ClickHouse Materialized Views"
---

# How to Scale K-Means Clustering with just ClickHouse SQL

## Introduction

Recently, when helping a user who wanted to compute centroids from vectors held in ClickHouse, we realized that the same solution could be used to implement K-Means clustering. They wanted to solve this at scale across potentially billions of data points while ensuring memory could be tightly managed. In this post, we give implementing K-means clustering using just SQL a try and show that it scales to billions of rows.

<blockquote style="font-size: 14px;">
<p>In the writing of this blog, we became aware of the work performed by Boris Tyshkevich. While we use a different approach in this blog, we would like to recognize Boris for his work and for having this idea well before we did!</p>
</blockquote>

As part of implementing K-Means with ClickHouse SQL, we cluster 170M NYC taxi rides in under 3 minutes. The equivalent scikit-learn operation with the same resources takes over 100 minutes and requires 90GB of RAM. With no memory limitations and ClickHouse automatically distributing the computation, we show that ClickHouse can accelerate machine learning workloads and reduce iteration time.

![kmeans_cluster_1.png](https://clickhouse.com/uploads/kmeans_cluster_1_b68b16e5d0.png)

All of the code for this blog post can be found in a notebook [here](https://github.com/ClickHouse/examples/blob/main/blog-examples/kmeans/kmeans.ipynb).

## Why K-Means in ClickHouse SQL?

The key motivation for using ClickHouse SQL to do K-Means is that training is not memory-bound, making it possible to cluster PB datasets thanks to the incremental computation of centroids (with settings to limit memory overhead). In contrast, distributing this workload across servers using Python-based approaches would require an additional framework and complexity. 

Additionally, we can easily increase the [level of parallelism in our clustering](https://clickhouse.com/blog/supercharge-your-clickhouse-data-loads-part2) to use the full resources of a Clickhouse instance. Should we need to handle larger datasets, we simply scale the database service - a simple operation in ClickHouse Cloud. 

Transforming the data for K-Means is a simple SQL query that can process billions of rows per second. With centroids and points held in ClickHouse, we can compute statistics such as model errors with just SQL and potentially use our clusters for other operations e.g. product quantization for vector search.

## K-Means recap

K-Means is an [unsupervised machine learning algorithm](https://cloud.google.com/discover/what-is-unsupervised-learning) for partitioning a dataset into K distinct, non-overlapping subgroups (clusters) where each data point belongs to the cluster with the nearest mean (the cluster's centroid). The process begins by initializing K centroids randomly or based on some heuristic. These centroids serve as the initial representatives of the clusters. The algorithm then iterates through two main steps until convergence: assignment and update. 

In the assignment step, each data point is assigned to the nearest cluster based on the Euclidean distance (or another distance metric) between it and the centroids. In the update step, the centroids are recalculated as the mean of all points assigned to their respective clusters, potentially shifting their positions. 

This process is guaranteed to converge, with the assignments of points to clusters eventually stabilizing and not changing between iterations. The number of clusters, K, needs to be specified beforehand and heavily influences the algorithm's effectiveness with the optimal value depending on the dataset and the goal of the clustering. For more details, we recommend this [excellent overview](https://medium.com/@dilekamadushan/introduction-to-k-means-clustering-7c0ebc997e00).

## Points and centroids

The key problem our user posed was the ability to efficiently compute centroids. Suppose we have a simple data schema for a `transactions` table, where each row represents a bank transaction for a specific customer. Vectors in ClickHouse are represented as an `Array` type. 

<pre style="font-size: 13px;"><code class="hljs language-sql"><span class="hljs-keyword">CREATE</span> <span class="hljs-keyword">TABLE</span> transactions
(
  id UInt32,
  vector <span class="hljs-keyword">Array</span>(Float32), 
  <span class="hljs-comment">-- e.g.[0.6860357,-1.0086979,0.83166444,-1.0089169,0.22888935]</span>
  customer UInt32,
  ...other columns omitted <span class="hljs-keyword">for</span> brevity
)
ENGINE <span class="hljs-operator">=</span> MergeTree <span class="hljs-keyword">ORDER</span> <span class="hljs-keyword">BY</span> id
</code></pre>

Our user wanted to find the centroid for each customer, effectively the positional average of all the transaction vectors associated with each customer. To find the set of average vectors, we can use the `avgForEach`<sub><a href="https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/avg">[1][2]</a></sub> function. For instance, consider the example of computing the average of 3 vectors, each with 4 elements:

<pre style="font-size: 13px;"><code class="hljs language-sql"><span class="hljs-keyword">WITH</span> vectors <span class="hljs-keyword">AS</span>
   (
       <span class="hljs-keyword">SELECT</span> c1 <span class="hljs-keyword">AS</span> vector
       <span class="hljs-keyword">FROM</span> <span class="hljs-keyword">VALUES</span>([<span class="hljs-number">1</span>, <span class="hljs-number">2</span>, <span class="hljs-number">3</span>, <span class="hljs-number">4</span>], [<span class="hljs-number">5</span>, <span class="hljs-number">6</span>, <span class="hljs-number">7</span>, <span class="hljs-number">8</span>], [<span class="hljs-number">9</span>, <span class="hljs-number">10</span>, <span class="hljs-number">11</span>, <span class="hljs-number">12</span>])
   )
<span class="hljs-keyword">SELECT</span> avgForEach(vector) <span class="hljs-keyword">AS</span> centroid
<span class="hljs-keyword">FROM</span> vectors

┌─centroid──┐
│ [<span class="hljs-number">5</span>,<span class="hljs-number">6</span>,<span class="hljs-number">7</span>,<span class="hljs-number">8</span>] │
└───────────┘
</code></pre>

In our original `transactions` table, computing the average per customer thus becomes:

<pre style="font-size: 13px;"><code class="hljs language-sql"><span class="hljs-keyword">SELECT</span> customer, avgForEach(vector) <span class="hljs-keyword">AS</span> centroid <span class="hljs-keyword">FROM</span> transactions <span class="hljs-keyword">GROUP</span> <span class="hljs-keyword">BY</span> customer
</code></pre>

While simple, this approach has a few limitations. Firstly, for very large datasets, when the `vector` contains many `Float32` points and the `customer` column has many unique elements (high cardinality), this query can be very memory intensive. Secondly, and maybe more relevant to K-Means, this approach requires us to rerun the query if new rows are inserted, which is inefficient. We can address these problems through Materialized Views and the AggregatingMergeTree engine.

### Incrementally computing centroids with Materialized Views 

Materialized Views allow us to shift the cost of computing our centroids to insert time. Unlike in other databases, a ClickHouse Materialized View is just a trigger that runs a query on blocks of data as they are inserted into a table. The results of this query are inserted into a second "target" table. In our case, the Materialized View query will compute our centroids, inserting the results to a table `centroids`.

![Incremental computing centroids with MV.png](https://clickhouse.com/uploads/Incremental_computing_centroids_with_MV_ca482bcd3f.png)

There are some important details here:

* Our query, which computes our centroids, must produce the result set in a format that can be merged with subsequent result sets - since every block inserted will produce a result set. Rather than just sending averages to our `centroids` table ([the average of an average would be incorrect](https://www.stevefenton.co.uk/blog/2020/02/can-you-average-averages-in-your-analytics/)), we send the [“average state”](https://clickhouse.com/blog/aggregate-functions-combinators-in-clickhouse-for-arrays-maps-and-states#working-with-aggregation-states). The average state representation contains the sum of each vector position, along with a count. This is achieved using the [`avgForEachState`](https://clickhouse.com/docs/en/sql-reference/aggregate-functions/combinators#-state) function - notice how we’ve just appended `State` to our function name! The AggregatingMergeTree table engine is required to store these aggregation states. We explore this more below.
* The entire process is incremental with the `centroids` table containing the final state i.e. a row per centroid. Readers will notice that the table which receives inserts has a Null table engine. This causes the inserted rows to be thrown away, saving the IO associated with writing the full dataset on each iteration.
* The query of our Materialized View is only executed on the blocks as they are inserted. The number of rows in each block can vary depending on the method of insertion. We recommend at least 1000 rows per block if formulating blocks on the client side, e.g., using the Go client. If the server is left to form blocks (e.g. when inserting by HTTP), the size can also [be specified](https://clickhouse.com/docs/en/operations/settings/settings#max_insert_block_size).
* If using an `INSERT INTO SELECT` where ClickHouse reads rows from another table or external source, e.g. S3, the block size can be controlled by several key parameters discussed in detail in [previous blogs](https://clickhouse.com/blog/supercharge-your-clickhouse-data-loads-part2#shifting-gears). These settings (along with the [number of insert threads](https://clickhouse.com/docs/en/operations/settings/settings#max-insert-threads)) can have a dramatic effect on both the memory used (larger blocks = more memory) and the speed of ingestion (larger blocks = faster). These settings mean the amount of memory used [can be finely controlled](https://clickhouse.com/blog/supercharge-your-clickhouse-data-loads-part2#formula-one) in exchange for performance.

### AggregatingMergeTree

Our target table `centroids` uses the engine [AggregatingMergeTree](https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/aggregatingmergetree):

<pre style="font-size: 13px;"><code class="hljs language-sql"><span class="hljs-keyword">CREATE</span> <span class="hljs-keyword">TABLE</span> centroids
(
   customer UInt32,
   vector AggregateFunction(avgForEach, <span class="hljs-keyword">Array</span>(Float32))
)
ENGINE <span class="hljs-operator">=</span> AggregatingMergeTree  <span class="hljs-keyword">ORDER</span> <span class="hljs-keyword">BY</span> customer
</code></pre>

Our `vector` column here contains the aggregate states produced by the [`avgForEachState`](https://clickhouse.com/blog/aggregate-functions-combinators-in-clickhouse-for-arrays-maps-and-states) function above. These are intermediate centroids that must be merged to produce a final answer. This column needs to be of the appropriate type [`AggregateFunction(avgForEach, Array(Float32))`](https://clickhouse.com/docs/en/sql-reference/data-types/aggregatefunction).

Like all ClickHouse MergeTree tables, the AggregatingMergeTree [stores data as parts that must be merged](https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/mergetree#mergetree-data-storage) transparently to allow more efficient querying. When merging parts containing our aggregate states, this must be done so that only states pertaining to the same customer are merged. This is effectively achieved by ordering the table by the `customer` column with the `ORDER BY` clause. At query time, we must also ensure intermediate states are grouped and merged. This can be achieved by ensuring we `GROUP BY` by the column `customer` and use the Merge equivalent of the `avgForEach` function: `avgForEachMerge.`

<pre style="font-size: 13px;"><code class="hljs language-sql"><span class="hljs-keyword">SELECT</span> customer, avgForEachMerge(vector) <span class="hljs-keyword">AS</span> centroid
<span class="hljs-keyword">FROM</span> centroids <span class="hljs-keyword">GROUP</span> <span class="hljs-keyword">BY</span> customer
</code></pre>

<blockquote style="font-size: 14px;">
<p>All aggregation functions have an equivalent state function, obtained by appending <code>State</code> to their name, which produces an intermediate representation that can be stored and then retrieved and merged with a <code>Merge</code> equivalent. For more details, we recommend <a href="https://clickhouse.com/blog/aggregate-functions-combinators-in-clickhouse-for-arrays-maps-and-states">this blog</a> and the video from our <a href="https://www.youtube.com/watch?v=7ApwD0cfAFI">very own Mark</a>.</p>
</blockquote>

This query will be very fast compared to our earlier `GROUP BY`. Most of the work for computing averages has been moved to insert time, with a small number of rows left for query time merging. Consider the performance of the following two approaches using 100m random transactions on a 48GiB, 12 vCPU Cloud service. Steps to load the data [here](https://gist.github.com/gingerwizard/f92337c1d0b04372adff8c2821cab46a).

Contrast the performance of computing our centroids from the `transactions` table:

<pre style="font-size: 13px;"><code class="hljs language-sql"><span class="hljs-keyword">SELECT</span> customer, avgForEach(vector) <span class="hljs-keyword">AS</span> centroid
<span class="hljs-keyword">FROM</span> transactions <span class="hljs-keyword">GROUP</span> <span class="hljs-keyword">BY</span> customer
<span class="hljs-keyword">ORDER</span> <span class="hljs-keyword">BY</span> customer <span class="hljs-keyword">ASC</span>
LIMIT <span class="hljs-number">1</span> FORMAT Vertical

<span class="hljs-number">10</span> <span class="hljs-keyword">rows</span> <span class="hljs-keyword">in</span> set. Elapsed: <span class="hljs-number">147.526</span> sec. Processed <span class="hljs-number">100.00</span> million <span class="hljs-keyword">rows</span>, <span class="hljs-number">41.20</span> GB (<span class="hljs-number">677.85</span> thousand <span class="hljs-keyword">rows</span><span class="hljs-operator">/</span>s., <span class="hljs-number">279.27</span> MB<span class="hljs-operator">/</span>s.)

<span class="hljs-type">Row</span> <span class="hljs-number">1</span>:
──────
customer: <span class="hljs-number">1</span>
centroid: [<span class="hljs-number">0.49645231463677153</span>,<span class="hljs-number">0.5042792240640065</span>,...,<span class="hljs-number">0.5017436349466129</span>]

<span class="hljs-number">1</span> <span class="hljs-type">row</span> <span class="hljs-keyword">in</span> set. Elapsed: <span class="hljs-number">36.017</span> sec. Processed <span class="hljs-number">100.00</span> million <span class="hljs-keyword">rows</span>, <span class="hljs-number">41.20</span> GB (<span class="hljs-number">2.78</span> million <span class="hljs-keyword">rows</span><span class="hljs-operator">/</span>s., <span class="hljs-number">1.14</span> GB<span class="hljs-operator">/</span>s.)
Peak memory usage: <span class="hljs-number">437.54</span> MiB.
</code></pre>

vs the `centroids` table with is over 1700x faster:

<pre style="font-size: 13px;"><code class="hljs language-sql"><span class="hljs-keyword">SELECT</span> customer, avgForEachMerge(vector) <span class="hljs-keyword">AS</span> centroid
<span class="hljs-keyword">FROM</span> centroids <span class="hljs-keyword">GROUP</span> <span class="hljs-keyword">BY</span> customer
<span class="hljs-keyword">ORDER</span> <span class="hljs-keyword">BY</span> customer <span class="hljs-keyword">ASC</span>
LIMIT <span class="hljs-number">1</span>
FORMAT Vertical

<span class="hljs-type">Row</span> <span class="hljs-number">1</span>:
──────
customer: <span class="hljs-number">1</span>
centroid: [<span class="hljs-number">0.49645231463677153</span>,<span class="hljs-number">0.5042792240640065</span>,...,<span class="hljs-number">0.5017436349466129</span>]

<span class="hljs-number">1</span> <span class="hljs-type">row</span> <span class="hljs-keyword">in</span> set. Elapsed: <span class="hljs-number">0.085</span> sec. Processed <span class="hljs-number">10.00</span> thousand <span class="hljs-keyword">rows</span>, <span class="hljs-number">16.28</span> MB (<span class="hljs-number">117.15</span> thousand <span class="hljs-keyword">rows</span><span class="hljs-operator">/</span>s., <span class="hljs-number">190.73</span> MB<span class="hljs-operator">/</span>s.)
</code></pre>

## Putting it all together

With our ability to compute centroids incrementally, let's focus on K-Means clustering. Let's assume we're trying to cluster a table `points` where each row has a vector representation. Here, we will cluster on similarity rather than just basing our centroids on the customer as we did with transactions.

### A single iteration

We need to be able to store the current centroids after each iteration of the algorithm. **For now, let's assume we have identified an optimal value of K.** Our target table for our centroids might look like this:

<pre style="font-size: 13px;"><code class="hljs language-sql"><span class="hljs-keyword">CREATE</span> <span class="hljs-keyword">TABLE</span> centroids
(
  k UInt32,
  iteration UInt32,
  centroid UInt32,
  vector AggregateFunction(avgForEach, <span class="hljs-keyword">Array</span>(Float32))
)
ENGINE <span class="hljs-operator">=</span> AggregatingMergeTree 
<span class="hljs-keyword">ORDER</span> <span class="hljs-keyword">BY</span> (k, iteration, centroid)
</code></pre>

The value of the `k` column is set to our chosen value of K. Our `centroid` column here denotes the centroid number itself, with a value between 0 and `K-1`. Rather than use a separate table for each iteration of the algorithm, we simply include an `iteration` column and ensure our ordering key is `(k, iteration, centroid)`. ClickHouse will ensure the intermediate state is only merged for each unique K, centroid, and iteration. This means our final row count will be small, ensuring fast querying of these centroids.

Our Materialized View for computing our centroids should be familiar with only a small adjustment to also `GROUP BY k, centroid, and iteration`:

<pre style="font-size: 13px;"><code class="hljs language-sql"><span class="hljs-keyword">CREATE</span> <span class="hljs-keyword">TABLE</span> temp
(
   k UInt32,
   iteration UInt32,
   centroid UInt32,
   vector <span class="hljs-keyword">Array</span>(Float32)
)
ENGINE <span class="hljs-operator">=</span> <span class="hljs-keyword">Null</span>

<span class="hljs-keyword">CREATE</span> MATERIALIZED <span class="hljs-keyword">VIEW</span> centroids_mv <span class="hljs-keyword">TO</span> centroids
<span class="hljs-keyword">AS</span> <span class="hljs-keyword">SELECT</span> k, iteration, centroid, avgForEachState(vector) <span class="hljs-keyword">AS</span> vector
<span class="hljs-keyword">FROM</span> temp <span class="hljs-keyword">GROUP</span> <span class="hljs-keyword">BY</span> k, centroid, iteration
</code></pre>

Notice that our query executes over blocks inserted into a `temp` table, not our data source table transactions, which does not have an `iteration` or `centroid` column. This temp table will receive our inserts and uses the Null table engine again to avoid writing data. With these building blocks in place, we can visualize a single iteration of the algorithm assuming `K = 5`:

![kmeans_clickhouse.png](https://clickhouse.com/uploads/kmeans_clickhouse_59999c3dc2.png)

The above shows how we insert into our temp table and thus compute our centroids by performing an `INSERT INTO SELECT` with a `points` table as our source data. **This insertion effectively represents an iteration of the algorithm.** The `SELECT` query here is critical as it needs to specify the transaction vector and its current centroid and iteration (and fixed value of K). How might we compute the latter of these two? The full `INSERT INTO SELECT` is shown below:

<pre style="font-size: 13px;"><code class="hljs language-sql"><span class="hljs-keyword">INSERT</span> <span class="hljs-keyword">INTO</span> temp 
<span class="hljs-keyword">WITH</span>
  <span class="hljs-number">5</span> <span class="hljs-keyword">as</span> k_val,
  <span class="hljs-comment">-- (1) obtain the max value of iteration - will be the previous iteration</span>
  (
      <span class="hljs-keyword">SELECT</span> <span class="hljs-built_in">max</span>(iteration)
      <span class="hljs-keyword">FROM</span> centroids 
      <span class="hljs-comment">-- As later we will reuse this table for all values of K</span>
      <span class="hljs-keyword">WHERE</span> k <span class="hljs-operator">=</span> k_val
  ) <span class="hljs-keyword">AS</span> c_iteration,
  (
      <span class="hljs-comment">-- (3) convert centroids into a array of tuples </span>
      <span class="hljs-comment">-- i.e. [(0, [vector]), (1, [vector]), ... , (k-1, [vector])]</span>
      <span class="hljs-keyword">SELECT</span> groupArray((centroid, position))
      <span class="hljs-keyword">FROM</span>
      (
         <span class="hljs-comment">-- (2) compute the centroids from the previous iteration</span>
          <span class="hljs-keyword">SELECT</span>
              centroid,
              avgForEachMerge(vector) <span class="hljs-keyword">AS</span> position
          <span class="hljs-keyword">FROM</span> centroids
          <span class="hljs-keyword">WHERE</span> iteration <span class="hljs-operator">=</span> c_iteration <span class="hljs-keyword">AND</span> k <span class="hljs-operator">=</span> k_val
          <span class="hljs-keyword">GROUP</span> <span class="hljs-keyword">BY</span> centroid
      )
  ) <span class="hljs-keyword">AS</span> c_centroids
<span class="hljs-keyword">SELECT</span>
  k_val <span class="hljs-keyword">AS</span> k,
  <span class="hljs-comment">-- (4) increment the iteration</span>
  c_iteration <span class="hljs-operator">+</span> <span class="hljs-number">1</span> <span class="hljs-keyword">AS</span> iteration,
  <span class="hljs-comment">-- (5) find the closest centroid for this vector using Euclidean distance</span>
  (arraySort(c <span class="hljs-operator">-</span><span class="hljs-operator">&gt;</span> (c<span class="hljs-number">.2</span>), arrayMap(x <span class="hljs-operator">-</span><span class="hljs-operator">&gt;</span> (x<span class="hljs-number">.1</span>, L2Distance(x<span class="hljs-number">.2</span>, vector)), c_centroids))[<span class="hljs-number">1</span>])<span class="hljs-number">.1</span> <span class="hljs-keyword">AS</span> centroid,
  vector <span class="hljs-keyword">AS</span> v
<span class="hljs-keyword">FROM</span> points
</code></pre>

Firstly, at (1), this query identifies the number of the previous iteration. This is then used within the CTE at (2) to determine the centroids produced for this iteration (and chosen K), using the same `avgForEachMerge` query shown earlier. These centroids are collapsed into a single row containing an array of Tuples via the `groupArray` query to facilitate easy matching against the points. In the `SELECT`, we increment the iteration number (4) and compute the new closest centroid (with the Euclidean distance [`L2Distance`](https://clickhouse.com/docs/en/sql-reference/functions/distance-functions#l2distance) function) using an [`arrayMap`](https://clickhouse.com/docs/en/sql-reference/functions/array-functions#sort) and [`arraySort`](https://clickhouse.com/docs/en/sql-reference/functions/array-functions#sort) functions for each point.

By inserting the rows into temp here, with a centroid based on the previous iteration, we can allow the Materialized View to compute the new centroids (with the iteration value +1).

### Initializing the centroids

The above assumes we have some initial centroids for iteration 1, which are used to compute membership. This requires us to initialize the system. We can do this by simply selecting and inserting K random points with the following query (k=5):

<pre style="font-size: 13px;"><code class="hljs language-sql"><span class="hljs-keyword">INSERT</span> <span class="hljs-keyword">INTO</span> temp <span class="hljs-keyword">WITH</span> 
  <span class="hljs-number">5</span> <span class="hljs-keyword">as</span> k_val,
  vectors <span class="hljs-keyword">AS</span>
  (
      <span class="hljs-keyword">SELECT</span> vector
      <span class="hljs-keyword">FROM</span> points
      <span class="hljs-comment">-- select random points, use k to make pseudo-random</span>
      <span class="hljs-keyword">ORDER</span> <span class="hljs-keyword">BY</span> cityHash64(concat(toString(id), toString(k_val))) <span class="hljs-keyword">ASC</span>
      LIMIT k_val <span class="hljs-comment">-- k</span>
  )
<span class="hljs-keyword">SELECT</span>
  k_val <span class="hljs-keyword">as</span> k,
  <span class="hljs-number">1</span> <span class="hljs-keyword">AS</span> iteration,
  rowNumberInAllBlocks() <span class="hljs-keyword">AS</span> centroid,
  vector
<span class="hljs-keyword">FROM</span> vectors
</code></pre>

<blockquote style="font-size: 14px;">
<p>Successful clustering is very sensitive to the initial placement of centroids;  poor assignment leads to slow convergence or suboptimal clustering. We will discuss this a little later.</p>
</blockquote>

### Centroid assignment and when to stop iterating

All of the above represents a single iteration (and initialization step). After each iteration, we need to make a decision as to whether to stop based on an empirical measurement of whether the clustering has converged. The simplest way to do this is to simply stop when points no longer change centroids (and thus clusters) between iterations.

<blockquote style="font-size: 14px;">
<p>To identify which points belong to which centroids, we can use the above SELECT from our earlier <code>INSERT INTO SELECT</code> at any time.</p>
</blockquote>

To compute the number of points that moved clusters in the last iteration, we first compute the centroids for the previous two iterations (1) and (2). Using these, we identify the centroids for each point for each iteration (3) and (4). If these are the same (5), we return 0 and 1 otherwise. A total of these (6) values provides us with the number of points that moved clusters.

<pre style="font-size: 13px;"><code class="hljs language-sql"><span class="hljs-keyword">WITH</span> <span class="hljs-number">5</span> <span class="hljs-keyword">as</span> k_val,
(
      <span class="hljs-keyword">SELECT</span> <span class="hljs-built_in">max</span>(iteration)
      <span class="hljs-keyword">FROM</span> centroids
) <span class="hljs-keyword">AS</span> c_iteration,
(
  <span class="hljs-comment">-- (1) current centroids</span>
  <span class="hljs-keyword">SELECT</span> groupArray((centroid, position))
  <span class="hljs-keyword">FROM</span>
  (
      <span class="hljs-keyword">SELECT</span>
          centroid,
          avgForEachMerge(vector) <span class="hljs-keyword">AS</span> position
      <span class="hljs-keyword">FROM</span> centroids
      <span class="hljs-keyword">WHERE</span> iteration <span class="hljs-operator">=</span> c_iteration <span class="hljs-keyword">AND</span> k <span class="hljs-operator">=</span> k_val
      <span class="hljs-keyword">GROUP</span> <span class="hljs-keyword">BY</span> centroid
  )
) <span class="hljs-keyword">AS</span> c_centroids,
(
  <span class="hljs-comment">-- (2) previous centroids</span>
  <span class="hljs-keyword">SELECT</span> groupArray((centroid, position))
  <span class="hljs-keyword">FROM</span>
  (
      <span class="hljs-keyword">SELECT</span>
          centroid,
          avgForEachMerge(vector) <span class="hljs-keyword">AS</span> position
      <span class="hljs-keyword">FROM</span> centroids
      <span class="hljs-keyword">WHERE</span> iteration <span class="hljs-operator">=</span> (c_iteration<span class="hljs-number">-1</span>) <span class="hljs-keyword">AND</span> k <span class="hljs-operator">=</span> k_val
      <span class="hljs-keyword">GROUP</span> <span class="hljs-keyword">BY</span> centroid
  )
) <span class="hljs-keyword">AS</span> c_p_centroids
<span class="hljs-comment">-- (6) sum differences</span>
<span class="hljs-keyword">SELECT</span> <span class="hljs-built_in">sum</span>(changed) <span class="hljs-keyword">FROM</span> (
  <span class="hljs-keyword">SELECT</span> id,
  <span class="hljs-comment">-- (3) current centroid for point</span>
  (arraySort(c <span class="hljs-operator">-</span><span class="hljs-operator">&gt;</span> (c<span class="hljs-number">.2</span>), arrayMap(x <span class="hljs-operator">-</span><span class="hljs-operator">&gt;</span> (x<span class="hljs-number">.1</span>, L2Distance(x<span class="hljs-number">.2</span>, vector)), c_centroids))[<span class="hljs-number">1</span>])<span class="hljs-number">.1</span> <span class="hljs-keyword">AS</span> cluster,
  <span class="hljs-comment">-- (4) previous centroid for point</span>
  (arraySort(c <span class="hljs-operator">-</span><span class="hljs-operator">&gt;</span> (c<span class="hljs-number">.2</span>), arrayMap(x <span class="hljs-operator">-</span><span class="hljs-operator">&gt;</span> (x<span class="hljs-number">.1</span>, L2Distance(x<span class="hljs-number">.2</span>, vector)), c_p_centroids))[<span class="hljs-number">1</span>])<span class="hljs-number">.1</span> <span class="hljs-keyword">AS</span> cluster_p,
  <span class="hljs-comment">-- (5) difference in allocation</span>
  if(cluster <span class="hljs-operator">=</span> cluster_p, <span class="hljs-number">0</span>, <span class="hljs-number">1</span>) <span class="hljs-keyword">as</span> changed
  <span class="hljs-keyword">FROM</span> points
)
</code></pre>

## A test dataset

The above has been mostly theoretical. Let's see if the above actually works on a real dataset! For this, we'll use a 3m row subset of the popular NYC taxis dataset as the clusters are hopefully relatable. To create and insert the data from S3: 

<pre style="font-size: 13px;"><code class="hljs language-sql"><span class="hljs-keyword">CREATE</span> <span class="hljs-keyword">TABLE</span> trips (
  trip_id         	UInt32,
  pickup_datetime 	DateTime,
  dropoff_datetime	DateTime,
  pickup_longitude	Nullable(Float64),
  pickup_latitude 	Nullable(Float64),
  dropoff_longitude   Nullable(Float64),
  dropoff_latitude	Nullable(Float64),
  passenger_count 	UInt8,
  trip_distance   	Float32,
  fare_amount     	Float32,
  extra           	Float32,
  tip_amount      	Float32,
  tolls_amount    	Float32,
  total_amount    	Float32,
  payment_type    	Enum(<span class="hljs-string">'CSH'</span> <span class="hljs-operator">=</span> <span class="hljs-number">1</span>, <span class="hljs-string">'CRE'</span> <span class="hljs-operator">=</span> <span class="hljs-number">2</span>, <span class="hljs-string">'NOC'</span> <span class="hljs-operator">=</span> <span class="hljs-number">3</span>, <span class="hljs-string">'DIS'</span> <span class="hljs-operator">=</span> <span class="hljs-number">4</span>, <span class="hljs-string">'UNK'</span> <span class="hljs-operator">=</span> <span class="hljs-number">5</span>),
  pickup_ntaname  	LowCardinality(String),
  dropoff_ntaname 	LowCardinality(String)
)
ENGINE <span class="hljs-operator">=</span> MergeTree
<span class="hljs-keyword">ORDER</span> <span class="hljs-keyword">BY</span> (pickup_datetime, dropoff_datetime);

<span class="hljs-keyword">INSERT</span> <span class="hljs-keyword">INTO</span> trips <span class="hljs-keyword">SELECT</span> trip_id, pickup_datetime, dropoff_datetime, pickup_longitude, pickup_latitude, dropoff_longitude, dropoff_latitude, passenger_count, trip_distance, fare_amount, extra, tip_amount, tolls_amount, total_amount, payment_type, pickup_ntaname, dropoff_ntaname
<span class="hljs-keyword">FROM</span> gcs(<span class="hljs-string">'https://storage.googleapis.com/clickhouse-public-datasets/nyc-taxi/trips_{0..2}.gz'</span>, <span class="hljs-string">'TabSeparatedWithNames'</span>);
</code></pre>

### Feature selection

Feature selection is crucial for good clustering as it directly impacts the quality of the clusters formed. We won’t go into detail here on how we selected our features. For those interested, we include the notes in the [notebook](https://github.com/ClickHouse/examples/blob/main/blog-examples/kmeans/kmeans.ipynb). We end up with the following `points` table:

<pre style="font-size: 13px;"><code class="hljs language-sql"><span class="hljs-keyword">CREATE</span> <span class="hljs-keyword">TABLE</span> points
(
   `id` UInt32,
   `vector` <span class="hljs-keyword">Array</span>(Float32),
   `pickup_hour` UInt8,
   `pickup_day_of_week` UInt8,
   `pickup_day_of_month` UInt8,
   `dropoff_hour` UInt8,
   `pickup_longitude` Float64,
   `pickup_latitude` Float64,
   `dropoff_longitude` Float64,
   `dropoff_latitude` Float64,
   `passenger_count` UInt8,
   `trip_distance` Float32,
   `fare_amount` Float32,
   `total_amount` Float32
) ENGINE <span class="hljs-operator">=</span> MergeTree <span class="hljs-keyword">ORDER</span> <span class="hljs-keyword">BY</span> id
</code></pre>

To populate this table, we use an `INSERT INTO SELECT` SQL query, which creates the features, scales them, and filters any outliers. Note our final columns are also encoded in a `vector` column.

<blockquote style="font-size: 14px;">
<p>The linked query is our first attempt at producing features. We expect more work to be possible here, which might produce better results than those shown. Suggestions are welcome!</p>
</blockquote>

### A little bit of Python

We have described how an iteration in the algorithm effectively reduces to an `INSERT INTO SELECT`, with the Materialized View handling the maintenance of the centroids. This means we need to invoke this statement N times until convergence has occurred.

<blockquote style="font-size: 14px;">
<p>Rather than waiting to reach a state where no points move between centroids, we use a threshold of 1000 i.e. if fewer than 1000 points move clusters, we stop. This check is made every 5 iterations.</p>
</blockquote>

The pseudo code for performing K-Means for a specific value of K becomes very simple given most of the work is performed by ClickHouse. 

<pre style="font-size: 13px;"><code class="hljs language-python"><span class="hljs-keyword">def</span> <span class="hljs-title function_">kmeans</span>(<span class="hljs-params">k, report_every = <span class="hljs-number">5</span>, min_cluster_move = <span class="hljs-number">1000</span></span>):
   startTime = time.time()
   <span class="hljs-comment"># INITIALIZATION QUERY</span>
   run_init_query(k)
   i = <span class="hljs-number">0</span>
   <span class="hljs-keyword">while</span> <span class="hljs-literal">True</span>:
       <span class="hljs-comment"># ITERATION QUERY</span>
       run_iteration_query(k)
       <span class="hljs-comment"># report every N iterations</span>
       <span class="hljs-keyword">if</span> (i + <span class="hljs-number">1</span>) % report_every == <span class="hljs-number">0</span> <span class="hljs-keyword">or</span> i == <span class="hljs-number">0</span>:
           num_moved = calculate_points_moved(k)
           <span class="hljs-keyword">if</span> num_moved &lt;= min_cluster_move:
               <span class="hljs-keyword">break</span>
       i += <span class="hljs-number">1</span>
   execution_time = (time.time() - startTime))
   <span class="hljs-comment"># COMPUTE d^2 ERROR</span>
   d_2_error = compute_d2_error(k)
   <span class="hljs-comment"># return the d^2, execution time and num of required iterations</span>
   <span class="hljs-keyword">return</span> d_2_error, execution_time, i+<span class="hljs-number">1</span>
</code></pre>  

The full code for this loop, including the queries, can be found in the [notebook](https://github.com/ClickHouse/examples/blob/main/blog-examples/kmeans/kmeans.ipynb#feature-engineering).

### Choosing K

So far, we’ve assumed K has been identified. There are several techniques for determining the optimal value of K, the simplest of which is to compute the aggregate squared distance (SSE) between each point and its respective cluster for each value of K. This gives us a cost metric that we aim to minimize. The method `compute_d2_error` computes this using the following SQL query (assuming a value of 5 for K):

<pre style="font-size: 12px;"><code class="hljs language-sql"><span class="hljs-keyword">WITH</span> <span class="hljs-number">5</span> <span class="hljs-keyword">as</span> k_val,
(
       <span class="hljs-keyword">SELECT</span> <span class="hljs-built_in">max</span>(iteration)
       <span class="hljs-keyword">FROM</span> centroids <span class="hljs-keyword">WHERE</span> k<span class="hljs-operator">=</span>{k}
) <span class="hljs-keyword">AS</span> c_iteration,
(
   <span class="hljs-keyword">SELECT</span> groupArray((centroid, position))
   <span class="hljs-keyword">FROM</span>
   (
       <span class="hljs-keyword">SELECT</span>
           centroid,
           avgForEachMerge(vector) <span class="hljs-keyword">AS</span> position
       <span class="hljs-keyword">FROM</span> centroids
       <span class="hljs-keyword">WHERE</span> iteration <span class="hljs-operator">=</span> c_iteration <span class="hljs-keyword">AND</span> k<span class="hljs-operator">=</span>k_val
       <span class="hljs-keyword">GROUP</span> <span class="hljs-keyword">BY</span> centroid
   )
) <span class="hljs-keyword">AS</span> c_centroids
<span class="hljs-keyword">SELECT</span>
   <span class="hljs-built_in">sum</span>(pow((arraySort(c <span class="hljs-operator">-</span><span class="hljs-operator">&gt;</span> (c<span class="hljs-number">.2</span>), arrayMap(x <span class="hljs-operator">-</span><span class="hljs-operator">&gt;</span> (x<span class="hljs-number">.1</span>, L2Distance(x<span class="hljs-number">.2</span>, vector)), c_centroids))[<span class="hljs-number">1</span>])<span class="hljs-number">.2</span>, <span class="hljs-number">2</span>)) <span class="hljs-keyword">AS</span> distance
<span class="hljs-keyword">FROM</span> points
</code></pre>

<blockquote style="font-size: 14px;">
<p>This value is guaranteed to decrease as we increase K e.g. if we set K to the number of points, each cluster will have 1 point thus giving us an error of 0. Unfortunately, this won’t generalize the data very well!</p>
</blockquote>

As K increases, SSE typically decreases because the data points are closer to their cluster centroids. The goal is to find the "elbow point" where the rate of decrease in SSE sharply changes. This point indicates a diminishing return on the benefit of increasing K. Choosing K at the elbow point provides a model that captures the inherent grouping in the data without overfitting. A simple way to identify this elbow point is to plot K vs SEE and identify the value visually. For our NYC taxis data, we measure and plot SSE for the K values 2 to 20:

![k_vs_d_2.png](https://clickhouse.com/uploads/k_vs_d_2_db70f33f8d.png)

The elbow point here isn’t as clear as we’d like, but a value of 5 seems a reasonable candidate.

<blockquote style="font-size: 14px;">
<p>The above results are based on a single end-to-end run for each value of K. K-Means can converge to a local minimum with no guarantee that nearby points will end up in the same cluster. It would be advisable to run multiple values for each value of K, each time with different initial centroids, to find the best candidate.</p>
</blockquote>

### Results

If we select 5 as our value for K, the algorithm takes around 30 iterations and 20 seconds to converge on a 12 vCPU ClickHouse Cloud node. This approach considers all 3 million rows for each iteration.

<pre style="font-size: 12px;"><code class="hljs language-none">k=5
initializing...OK
Iteration 0
Number changed cluster in first iteration: 421206
Iteration 1, 2, 3, 4
Number changed cluster in iteration 5: 87939
Iteration 5, 6, 7, 8, 9
Number changed cluster in iteration 10: 3610
Iteration 10, 11, 12, 13, 14
Number changed cluster in iteration 15: 1335
Iteration 15, 16, 17, 18, 19
Number changed cluster in iteration 20: 1104
Iteration 20, 21, 22, 23, 24
Number changed cluster in iteration 25: 390
stopping as moved less than 1000 clusters in last iteration
Execution time in seconds: 20.79200577735901
D^2 error for 5: 33000373.34968858
</code></pre>

To visualize these clusters, we need to reduce the dimensionality. For this, we use [Principal Component Analysis (PCA)](https://en.wikipedia.org/wiki/Principal_component_analysis). We defer the implementation of PCA in SQL to another blog and just use Python with a sample of 10,000 random points. We can evaluate the effectiveness of PCA in capturing the essential properties of data by checking how much variance the principal components account for. 82% is less than the typically used threshold of 90%, but sufficient for an understanding of the effectiveness of our clustering:

<pre style="font-size: 12px;"><code class="hljs language-none">Explained variances of the 3 principal components: 0.824
</code></pre>

Using our 3 principal components, we can plot the same random 10,000 points and associate a color with each according to its cluster.

![kmeans_1.png](https://clickhouse.com/uploads/kmeans_1_26cf9b1a0b.png)

The PCA visualization of the clusters shows a dense plane across PC1 and PC3, neatly divided into four distinct clusters, suggesting constrained variance within these dimensions. Along the 2nd principal component (PC2), the visualization becomes sparser, with a cluster (number 3) that diverges from the main group and could be particularly interesting.

To understand our clusters, we need labels. Ideally, we would produce these by exploring the distribution of every column in each cluster, looking for unique characteristics and temporal/spatial patterns. We’ll try to do this succinctly with a SQL query to understand the distribution of each column in each cluster. For the columns to focus on, we can inspect the values of the PCA components and identify the dimensions that dominate. Code for doing this can be found in the notebook and identifies the following:

<pre style="font-size: 12px;"><code class="hljs language-none">PCA1:: ['pickup_day_of_month: 0.9999497049810415', 'dropoff_latitude: -0.006371842399701939', 'pickup_hour: 0.004444108327647353', 'dropoff_hour: 0.003868258226185553', …]

PCA 2:: ['total_amount: 0.5489526881298809', 'fare_amount: 0.5463895585884886', 'pickup_longitude: 0.43181504878694826', 'pickup_latitude: -0.3074228612885196', 'dropoff_longitude: 0.2756342866763702', 'dropoff_latitude: -0.19809343490462433', …]

PCA 3:: ['dropoff_hour: -0.6998176337701472', 'pickup_hour: -0.6995098287872831', 'pickup_day_of_week: 0.1134719682173672', 'pickup_longitude: -0.05495391127067617', …]
</code></pre>

For PCA1, `pickup_day_of_month` is important, suggesting a focus on the time of the month. For PC2, dimensions, the location of pickup and drop off, and the cost of the ride appear to contribute heavily. This component probably focuses on a specific trip type. Finally, for PC3, the hour in which the trip occurred seems the most relevant. To understand how these columns differ per cluster with respect to time, date, and price, we again can just use an SQL query:

<pre style="font-size: 13px;"><code class="hljs language-sql"><span class="hljs-keyword">WITH</span>
   <span class="hljs-number">5</span> <span class="hljs-keyword">AS</span> k_val,
   (
       <span class="hljs-keyword">SELECT</span> <span class="hljs-built_in">max</span>(iteration)
       <span class="hljs-keyword">FROM</span> centroids
       <span class="hljs-keyword">WHERE</span> k <span class="hljs-operator">=</span> k_val
   ) <span class="hljs-keyword">AS</span> c_iteration,
   (
       <span class="hljs-keyword">SELECT</span> groupArray((centroid, position))
       <span class="hljs-keyword">FROM</span>
       (
           <span class="hljs-keyword">SELECT</span>
               centroid,
               avgForEachMerge(vector) <span class="hljs-keyword">AS</span> position
           <span class="hljs-keyword">FROM</span> centroids
           <span class="hljs-keyword">WHERE</span> (iteration <span class="hljs-operator">=</span> c_iteration) <span class="hljs-keyword">AND</span> (k <span class="hljs-operator">=</span> k_val)
           <span class="hljs-keyword">GROUP</span> <span class="hljs-keyword">BY</span> centroid
       )
   ) <span class="hljs-keyword">AS</span> c_centroids
<span class="hljs-keyword">SELECT</span>
   (arraySort(c <span class="hljs-operator">-</span><span class="hljs-operator">&gt;</span> (c<span class="hljs-number">.2</span>), arrayMap(x <span class="hljs-operator">-</span><span class="hljs-operator">&gt;</span> (x<span class="hljs-number">.1</span>, L2Distance(x<span class="hljs-number">.2</span>, vector)), c_centroids))[<span class="hljs-number">1</span>])<span class="hljs-number">.1</span> <span class="hljs-keyword">AS</span> cluster,
   <span class="hljs-built_in">floor</span>(<span class="hljs-built_in">avg</span>(pickup_day_of_month)) <span class="hljs-keyword">AS</span> pickup_day_of_month,
   round(<span class="hljs-built_in">avg</span>(pickup_hour)) <span class="hljs-keyword">AS</span> avg_pickup_hour,
   round(<span class="hljs-built_in">avg</span>(fare_amount)) <span class="hljs-keyword">AS</span> avg_fare_amount,
   round(<span class="hljs-built_in">avg</span>(total_amount)) <span class="hljs-keyword">AS</span> avg_total_amount
<span class="hljs-keyword">FROM</span> points
<span class="hljs-keyword">GROUP</span> <span class="hljs-keyword">BY</span> cluster
<span class="hljs-keyword">ORDER</span> <span class="hljs-keyword">BY</span> cluster <span class="hljs-keyword">ASC</span>

┌─cluster─┬─pickup_day_of_month─┬─avg_pickup_hour─┬─avg_fare_amount─┬─avg_total_amount─┐
│   	<span class="hljs-number">0</span> │              	<span class="hljs-number">11</span>  │          	<span class="hljs-number">14</span>    │          	<span class="hljs-number">11</span>  │           	<span class="hljs-number">13</span> │
│   	<span class="hljs-number">1</span> │               	<span class="hljs-number">3</span>   │          	<span class="hljs-number">14</span>    │          	<span class="hljs-number">12</span>  │           	<span class="hljs-number">14</span> │
│   	<span class="hljs-number">2</span> │              	<span class="hljs-number">18</span>  │          	<span class="hljs-number">13</span>    │          	<span class="hljs-number">11</span>  │           	<span class="hljs-number">13</span> │
│   	<span class="hljs-number">3</span> │              	<span class="hljs-number">16</span>  │          	<span class="hljs-number">14</span>    │          	<span class="hljs-number">49</span>  │           	<span class="hljs-number">58</span> │
│   	<span class="hljs-number">4</span> │              	<span class="hljs-number">26</span>  │          	<span class="hljs-number">14</span>    │          	<span class="hljs-number">12</span>  │           	<span class="hljs-number">14</span> │
└─────────┴─────────────────────┴─────────────────┴─────────────────┴──────────────────┘

<span class="hljs-number">9</span> <span class="hljs-keyword">rows</span> <span class="hljs-keyword">in</span> set. Elapsed: <span class="hljs-number">0.625</span> sec. Processed <span class="hljs-number">2.95</span> million <span class="hljs-keyword">rows</span>, <span class="hljs-number">195.09</span> MB (<span class="hljs-number">4.72</span> million <span class="hljs-keyword">rows</span><span class="hljs-operator">/</span>s., <span class="hljs-number">312.17</span> MB<span class="hljs-operator">/</span>s.)
Peak memory usage: <span class="hljs-number">720.16</span> MiB.
</code></pre>

Cluster 3 is clearly associated with more expensive trips. Given that the cost of the trip was associated with a principal component, which also identified pickup and drop-off locations as key, these are probably associated with a specific trip type. Other clusters need a deeper analysis but seem to be focused on monthly patterns. We can plot the pickup and drop-off locations for just cluster 3 on a map visualization. Blue and red points represent the pickup and drop-off locations, respectively, in the following plot:

![clusters_nyc_map.png](https://clickhouse.com/uploads/clusters_nyc_map_8c69700732.png)

On close inspection of the plot, this cluster is associated with airport trips to and from JFK. 

## Scaling

Our previous example uses only a 3m row subset of the NYC taxi rides. Testing on a larger dataset for all of taxi rides for 2009 (170m rows), we can complete clustering for k=5 in around 3 mins with a ClickHouse service using 60 cores.  

<pre style="font-size: 12px;"><code class="hljs language-none">k=5
initializing...OK
…
Iteration 15, 16, 17, 18, 19
Number changed cluster in iteration 20: 288
stopping as moved less than 1000 clusters in last iteration
Execution time in seconds: 178.61135005950928
D^2 error for 5: 1839404623.265372
Completed in 178.61135005950928s and 20 iterations with error 1839404623.265372
</code></pre>

This produces similar clusters to our previous smaller subset. Running the same clustering on a 64 core `m5d.16xlarge` using scikit-learn takes 6132s, over 34x slower! Steps to reproduce this benchmark can be found at the end of the notebook and using [these steps](https://gist.github.com/gingerwizard/979e8e10fca6e0d186bf3eb848eb2628) for scikit-learn.

## Potential improvements & future work

Clustering is very sensitive to the initial points selected. K-Means++ is an improvement over standard K-Means clustering that addresses this by introducing a smarter initialization process that aims to spread out the initial centroids, reducing the likelihood of poor initial centroid placement and leading to faster convergence as well as potentially better clustering. We leave this as an exercise for the reader to improve.

K-Means also struggles to handle categorical variables. This can be partially handled with one-hot encoding (also possible in SQL) as well as dedicated algorithms such as [KModes clustering](https://www.analyticsvidhya.com/blog/2021/06/kmodes-clustering-algorithm-for-categorical-data/) designed for this class of data. Custom distance functions for specific domains instead of just Euclidean distance are also common and should be implementable using User Defined Functions (UDFs).

Finally, it might also be interesting to explore other soft clustering algorithms, such as Gaussian Mixture Models for normally distributed features, or Hierarchical Clustering algorithms, such as Agglomerative clustering. These latter approaches also overcome one of the main limitations of K-Means - the need to specify K. We would love to see attempts to implement these in ClickHouse SQL!
