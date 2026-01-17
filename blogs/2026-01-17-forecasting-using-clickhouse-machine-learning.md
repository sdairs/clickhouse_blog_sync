---
title: "Forecasting Using ClickHouse Machine Learning Functions"
date: "2023-10-26T16:55:35.377Z"
author: "Ensemble"
category: "Engineering"
excerpt: "We welcome a guest post from ensemble who demonstrate how Machine Learning functions can be used in ClickHouse."
---

# Forecasting Using ClickHouse Machine Learning Functions

<blockquote style="font-size: 16px;">
<p>This was originally <a href="https://ensembleanalytics.io/blog/forecasting-using-clickhouse">a post by ensemble analytics</a>, who have kindly allowed republishing of this content. We welcome posts from our community and thank them for their contributions.</p>
</blockquote>

## Introduction

When doing statistical analysis or data science work, the first inclination is usually to break into a programming language such as Python or R at the earliest opportunity.

When we use ClickHouse however, we prefer to take things as far as possible using just the database. By doing this, we can rely on the power of ClickHouse to crunch numbers quickly, and reduce or even totally avoid the amount of code that we need to write. This also means that we can work with smaller in memory datasets on the client side and avoid the need for distributed computation.

A good example of this is forecasting. ClickHouse implements two machine learning functions - Stochastic Linear Regression (stochasticLinearRegression) which can be used for fitting the model, and a function (evalMLMethod) which can be used for subsequent inference directly within the database.

Of course there are more sophisticated forecasting models and more flexibility once you break out of SQL into a fully-fledged programming language, but this technique certainly has it's uses and performs well in our demonstration scenario here.

## Dataset

To demonstrate, we are going to use a simple flight departure dataset which contains a monthly [time series](https://clickhouse.com/resources/engineering/what-is-time-series-database) of the number of passengers departing from different airports using various airlines.

Our aim will be to take this data and use it forecast the same data into the future.

We will aim to build a model using data from 2008 to 2015, and then test the performance of the model between 2015 and 2018. Finally, we will then forecast beyond the period through till 2021.

Our source data has the following structure:

```sql
SELECT *
FROM flight_data
LIMIT 10

┌─AIRLINE─┬─DEPARTURE_AIRPORT─┬──────MONTH─┬─PASSENGERS─┐
│ Delta   │ DIA               │ 2008-01-01 │        434 │
│ Delta   │ DIA               │ 2008-02-01 │        475 │
│ Delta   │ DIA               │ 2008-03-01 │        531 │
│ Delta   │ DIA               │ 2008-04-01 │        509 │
│ Delta   │ DIA               │ 2008-05-01 │        472 │
│ Delta   │ DIA               │ 2008-06-01 │        562 │
│ Delta   │ DIA               │ 2008-07-01 │        642 │
│ Delta   │ DIA               │ 2008-08-01 │        642 │
│ Delta   │ DIA               │ 2008-09-01 │        596 │
│ Delta   │ DIA               │ 2008-10-01 │        503 │
└─────────┴───────────────────┴────────────┴────────────┘

10 rows in set. Elapsed: 0.002 sec. Processed 4.62 thousand rows, 151.54 KB (2.16 million rows/s., 70.86 MB/s.)
Peak memory usage: 229.15 KiB.
```

When plotted, the data looks like this, showing how all airlines are carrying an increased number of passengers over time together with a significant seasonality effect.

![hex01.png](https://clickhouse.com/uploads/hex01_5c80cc5282.png)

## Data Preparation

Our forecasting model uses 13 deterministic features: a linear time trend and 12 dummy (or one-hot encoded) variables representing the 12 months of the year. We exclude the constant term (or intercept) in order to avoid the "dummy variable trap".

The model predicts the logarithm of the number of passengers. The logarithmic transformation allows us to better capture the time-varying amplitude of the seasonal fluctuations.

```sql
CREATE VIEW
    data
AS WITH
    (select toDate(min(MONTH)) from flight_data) as start_date,
    (select toDate(max(MONTH)) from flight_data) as end_date
SELECT
    AIRLINE,
    DEPARTURE_AIRPORT,
    MONTH,
    toFloat64(log(PASSENGERS)) as Target,
    assumeNotNull(dateDiff('month', start_date, MONTH) / dateDiff('month', start_date, end_date)) as Trend,
    if(toMonth(toDate(MONTH)) = 1, 1, 0) as Dummy1,
    if(toMonth(toDate(MONTH)) = 2, 1, 0) as Dummy2,
    if(toMonth(toDate(MONTH)) = 3, 1, 0) as Dummy3,
    if(toMonth(toDate(MONTH)) = 4, 1, 0) as Dummy4,
    if(toMonth(toDate(MONTH)) = 5, 1, 0) as Dummy5,
    if(toMonth(toDate(MONTH)) = 6, 1, 0) as Dummy6,
    if(toMonth(toDate(MONTH)) = 7, 1, 0) as Dummy7,
    if(toMonth(toDate(MONTH)) = 8, 1, 0) as Dummy8,
    if(toMonth(toDate(MONTH)) = 9, 1, 0) as Dummy9,
    if(toMonth(toDate(MONTH)) = 10, 1, 0) as Dummy10,
    if(toMonth(toDate(MONTH)) = 11, 1, 0) as Dummy11,
    if(toMonth(toDate(MONTH)) = 12, 1, 0) as Dummy12
FROM
    flight_data
ORDER BY AIRLINE, DEPARTURE_AIRPORT, MONTH
```

This creates the following view which summarises our dependent and independent variables:

<pre style="position:absolute; max-width:100%;"><code class="hljs language-sql" style="white-space: pre; overflow-x: scroll;max-width: 768px;"><span class="hljs-keyword">SELECT</span> <span class="hljs-operator">*</span>
<span class="hljs-keyword">FROM</span> data
LIMIT <span class="hljs-number">10</span>

┌─AIRLINE─┬─DEPARTURE_AIRPORT─┬──────<span class="hljs-keyword">MONTH</span>─┬─────────────Target─┬────────────────Trend─┬─Dummy1─┬─Dummy2─┬─Dummy3─┬─Dummy4─┬─Dummy5─┬─Dummy6─┬─Dummy7─┬─Dummy8─┬─Dummy9─┬─Dummy10─┬─Dummy11─┬─Dummy12─┐
│ Delta   │ DIA               │ <span class="hljs-number">2008</span><span class="hljs-number">-01</span><span class="hljs-number">-01</span> │ <span class="hljs-number">6.0730445333335865</span> │                    <span class="hljs-number">0</span> │      <span class="hljs-number">1</span> │      <span class="hljs-number">0</span> │      <span class="hljs-number">0</span> │      <span class="hljs-number">0</span> │      <span class="hljs-number">0</span> │      <span class="hljs-number">0</span> │      <span class="hljs-number">0</span> │      <span class="hljs-number">0</span> │      <span class="hljs-number">0</span> │       <span class="hljs-number">0</span> │       <span class="hljs-number">0</span> │       <span class="hljs-number">0</span> │
│ Delta   │ DIA               │ <span class="hljs-number">2008</span><span class="hljs-number">-02</span><span class="hljs-number">-01</span> │  <span class="hljs-number">6.163314804336003</span> │ <span class="hljs-number">0.007633587786259542</span> │      <span class="hljs-number">0</span> │      <span class="hljs-number">1</span> │      <span class="hljs-number">0</span> │      <span class="hljs-number">0</span> │      <span class="hljs-number">0</span> │      <span class="hljs-number">0</span> │      <span class="hljs-number">0</span> │      <span class="hljs-number">0</span> │      <span class="hljs-number">0</span> │       <span class="hljs-number">0</span> │       <span class="hljs-number">0</span> │       <span class="hljs-number">0</span> │
│ Delta   │ DIA               │ <span class="hljs-number">2008</span><span class="hljs-number">-03</span><span class="hljs-number">-01</span> │  <span class="hljs-number">6.274762021388925</span> │ <span class="hljs-number">0.015267175572519083</span> │      <span class="hljs-number">0</span> │      <span class="hljs-number">0</span> │      <span class="hljs-number">1</span> │      <span class="hljs-number">0</span> │      <span class="hljs-number">0</span> │      <span class="hljs-number">0</span> │      <span class="hljs-number">0</span> │      <span class="hljs-number">0</span> │      <span class="hljs-number">0</span> │       <span class="hljs-number">0</span> │       <span class="hljs-number">0</span> │       <span class="hljs-number">0</span> │
│ Delta   │ DIA               │ <span class="hljs-number">2008</span><span class="hljs-number">-04</span><span class="hljs-number">-01</span> │  <span class="hljs-number">6.232448016554782</span> │ <span class="hljs-number">0.022900763358778626</span> │      <span class="hljs-number">0</span> │      <span class="hljs-number">0</span> │      <span class="hljs-number">0</span> │      <span class="hljs-number">1</span> │      <span class="hljs-number">0</span> │      <span class="hljs-number">0</span> │      <span class="hljs-number">0</span> │      <span class="hljs-number">0</span> │      <span class="hljs-number">0</span> │       <span class="hljs-number">0</span> │       <span class="hljs-number">0</span> │       <span class="hljs-number">0</span> │
│ Delta   │ DIA               │ <span class="hljs-number">2008</span><span class="hljs-number">-05</span><span class="hljs-number">-01</span> │  <span class="hljs-number">6.156978985873825</span> │ <span class="hljs-number">0.030534351145038167</span> │      <span class="hljs-number">0</span> │      <span class="hljs-number">0</span> │      <span class="hljs-number">0</span> │      <span class="hljs-number">0</span> │      <span class="hljs-number">1</span> │      <span class="hljs-number">0</span> │      <span class="hljs-number">0</span> │      <span class="hljs-number">0</span> │      <span class="hljs-number">0</span> │       <span class="hljs-number">0</span> │       <span class="hljs-number">0</span> │       <span class="hljs-number">0</span> │
│ Delta   │ DIA               │ <span class="hljs-number">2008</span><span class="hljs-number">-06</span><span class="hljs-number">-01</span> │ <span class="hljs-number">6.3315018500618665</span> │  <span class="hljs-number">0.03816793893129771</span> │      <span class="hljs-number">0</span> │      <span class="hljs-number">0</span> │      <span class="hljs-number">0</span> │      <span class="hljs-number">0</span> │      <span class="hljs-number">0</span> │      <span class="hljs-number">1</span> │      <span class="hljs-number">0</span> │      <span class="hljs-number">0</span> │      <span class="hljs-number">0</span> │       <span class="hljs-number">0</span> │       <span class="hljs-number">0</span> │       <span class="hljs-number">0</span> │
│ Delta   │ DIA               │ <span class="hljs-number">2008</span><span class="hljs-number">-07</span><span class="hljs-number">-01</span> │  <span class="hljs-number">6.464588304624293</span> │  <span class="hljs-number">0.04580152671755725</span> │      <span class="hljs-number">0</span> │      <span class="hljs-number">0</span> │      <span class="hljs-number">0</span> │      <span class="hljs-number">0</span> │      <span class="hljs-number">0</span> │      <span class="hljs-number">0</span> │      <span class="hljs-number">1</span> │      <span class="hljs-number">0</span> │      <span class="hljs-number">0</span> │       <span class="hljs-number">0</span> │       <span class="hljs-number">0</span> │       <span class="hljs-number">0</span> │
│ Delta   │ DIA               │ <span class="hljs-number">2008</span><span class="hljs-number">-08</span><span class="hljs-number">-01</span> │  <span class="hljs-number">6.464588304624293</span> │  <span class="hljs-number">0.05343511450381679</span> │      <span class="hljs-number">0</span> │      <span class="hljs-number">0</span> │      <span class="hljs-number">0</span> │      <span class="hljs-number">0</span> │      <span class="hljs-number">0</span> │      <span class="hljs-number">0</span> │      <span class="hljs-number">0</span> │      <span class="hljs-number">1</span> │      <span class="hljs-number">0</span> │       <span class="hljs-number">0</span> │       <span class="hljs-number">0</span> │       <span class="hljs-number">0</span> │
│ Delta   │ DIA               │ <span class="hljs-number">2008</span><span class="hljs-number">-09</span><span class="hljs-number">-01</span> │  <span class="hljs-number">6.390240666362644</span> │ <span class="hljs-number">0.061068702290076333</span> │      <span class="hljs-number">0</span> │      <span class="hljs-number">0</span> │      <span class="hljs-number">0</span> │      <span class="hljs-number">0</span> │      <span class="hljs-number">0</span> │      <span class="hljs-number">0</span> │      <span class="hljs-number">0</span> │      <span class="hljs-number">0</span> │      <span class="hljs-number">1</span> │       <span class="hljs-number">0</span> │       <span class="hljs-number">0</span> │       <span class="hljs-number">0</span> │
│ Delta   │ DIA               │ <span class="hljs-number">2008</span><span class="hljs-number">-10</span><span class="hljs-number">-01</span> │  <span class="hljs-number">6.220590170138575</span> │  <span class="hljs-number">0.06870229007633588</span> │      <span class="hljs-number">0</span> │      <span class="hljs-number">0</span> │      <span class="hljs-number">0</span> │      <span class="hljs-number">0</span> │      <span class="hljs-number">0</span> │      <span class="hljs-number">0</span> │      <span class="hljs-number">0</span> │      <span class="hljs-number">0</span> │      <span class="hljs-number">0</span> │       <span class="hljs-number">1</span> │       <span class="hljs-number">0</span> │       <span class="hljs-number">0</span> │
└─────────┴───────────────────┴────────────┴────────────────────┴──────────────────────┴────────┴────────┴────────┴────────┴────────┴────────┴────────┴────────┴────────┴─────────┴─────────┴─────────┘

<span class="hljs-number">10</span> <span class="hljs-keyword">rows</span> <span class="hljs-keyword">in</span> set. Elapsed: <span class="hljs-number">0.010</span> sec. Processed <span class="hljs-number">13.86</span> thousand <span class="hljs-keyword">rows</span>, <span class="hljs-number">170.02</span> KB (<span class="hljs-number">1.37</span> million <span class="hljs-keyword">rows</span><span class="hljs-operator">/</span>s., <span class="hljs-number">16.81</span> MB<span class="hljs-operator">/</span>s.)
Peak memory usage: <span class="hljs-number">420.28</span> KiB.
</code></pre>

<div style="margin-top: 36rem">

## Model Training

We use ClickHouse's stochasticLinearRegression algorithm, which trains a linear regression using gradient descent. We build 35 different models at the same time, one for each airline-airport combination.

```sql
CREATE VIEW model as SELECT
    AIRLINE,
    DEPARTURE_AIRPORT,
    stochasticLinearRegressionState(0.5, 0.01, 4, 'SGD')(
        Target, Trend, Dummy1, Dummy2, Dummy3, Dummy4, Dummy5, Dummy6, Dummy7, Dummy8, Dummy9, Dummy10, Dummy11, Dummy12
    ) as state
FROM train_data
GROUP BY AIRLINE, DEPARTURE_AIRPORT
```

As there is a small amount of data, the model is simply defined as a view. For bigger datasets, we may choose to materialize this as a table or a view.

</div>

## Model Evaluation

We can now use the trained model to generate the forecasts over the test set and compare them to the actual values. At this stage we can also transform the data and the forecasts back to the original scale by taking the exponential.

```sql
SELECT
    a.MONTH as MONTH,
    a.AIRLINE as AIRLINE,
    a.DEPARTURE_AIRPORT as DEPARTURE_AIRPORT,
    toInt32(exp(a.Target)) as ACTUAL,
    toInt32(exp(evalMLMethod(b.state, Trend, Dummy1, Dummy2, Dummy3, Dummy4, Dummy5, Dummy6, Dummy7,
    Dummy8, Dummy9, Dummy10, Dummy11, Dummy12))) as FORECAST
FROM test_data as a
LEFT JOIN model as b
on a.AIRLINE = b.AIRLINE and a.DEPARTURE_AIRPORT = b.DEPARTURE_AIRPORT
```

If we compare the forecast and the actuals, we can see that the forecast performed well:

![hex02.png](https://clickhouse.com/uploads/hex02_83c98cd9b6.png)


We can validate this by calculating the Mean Absolute Error (MAE) and Root Mean Squared Error (RMSE) of the forecasts for each airline-airport combination.

<pre style="position:absolute; max-width:100%;"><code class="hljs language-sql" style="white-space: pre; overflow-x: scroll;max-width: 768px;"><span class="hljs-keyword">SELECT</span>
    AIRLINE,
    DEPARTURE_AIRPORT,
    <span class="hljs-built_in">avg</span>(<span class="hljs-built_in">abs</span>(ERROR)) <span class="hljs-keyword">AS</span> MAE,
    <span class="hljs-built_in">sqrt</span>(<span class="hljs-built_in">avg</span>(pow(ERROR, <span class="hljs-number">2</span>))) <span class="hljs-keyword">AS</span> RMSE
<span class="hljs-keyword">FROM</span>
(
    <span class="hljs-keyword">SELECT</span>
        a.AIRLINE <span class="hljs-keyword">AS</span> AIRLINE,
        a.DEPARTURE_AIRPORT <span class="hljs-keyword">AS</span> DEPARTURE_AIRPORT,
        toInt32(<span class="hljs-built_in">exp</span>(a.Target)) <span class="hljs-operator">-</span> toInt32(<span class="hljs-built_in">exp</span>(evalMLMethod(b.state, Trend, Dummy1, Dummy2, Dummy3, Dummy4,
        Dummy5, Dummy6, Dummy7, Dummy8, Dummy9, Dummy10, Dummy11, Dummy12))) <span class="hljs-keyword">AS</span> ERROR
    <span class="hljs-keyword">FROM</span> test_data <span class="hljs-keyword">AS</span> a
    <span class="hljs-keyword">LEFT</span> <span class="hljs-keyword">JOIN</span> model <span class="hljs-keyword">AS</span> b <span class="hljs-keyword">ON</span> (a.AIRLINE <span class="hljs-operator">=</span> b.AIRLINE) <span class="hljs-keyword">AND</span> (a.DEPARTURE_AIRPORT <span class="hljs-operator">=</span> b.DEPARTURE_AIRPORT)
)
<span class="hljs-keyword">GROUP</span> <span class="hljs-keyword">BY</span>
    AIRLINE,
    DEPARTURE_AIRPORT

Query id: <span class="hljs-number">320</span>cad46<span class="hljs-operator">-</span>bb31<span class="hljs-number">-4248</span><span class="hljs-operator">-</span>bd25<span class="hljs-number">-19</span>d98d5d2d15

┌─AIRLINE──┬─DEPARTURE_AIRPORT─┬────────────────MAE─┬───────────────RMSE─┐
│ JetBlue  │ SFO               │  <span class="hljs-number">86.38888888888889</span> │ <span class="hljs-number">110.96671172523367</span> │
│ KLM      │ PDX               │ <span class="hljs-number">167.97222222222223</span> │  <span class="hljs-number">213.4134615143936</span> │
│ Delta    │ SJC               │ <span class="hljs-number">141.80555555555554</span> │  <span class="hljs-number">180.9452802491528</span> │
│ United   │ PDX               │ <span class="hljs-number">115.19444444444444</span> │  <span class="hljs-number">147.7711255812703</span> │
│ JetBlue  │ ORL               │  <span class="hljs-number">97.77777777777777</span> │ <span class="hljs-number">125.28611699271038</span> │
│ KLM      │ JAX               │ <span class="hljs-number">121.27777777777777</span> │ <span class="hljs-number">155.41414207064798</span> │
│ Delta    │ JFK               │              <span class="hljs-number">168.5</span> │  <span class="hljs-number">214.1754213515433</span> │
│ United   │ JAX               │ <span class="hljs-number">153.88888888888889</span> │  <span class="hljs-number">195.9098432102549</span> │
│ Delta    │ SFO               │ <span class="hljs-number">184.66666666666666</span> │ <span class="hljs-number">234.34068267280344</span> │
│ KLM      │ DIA               │ <span class="hljs-number">148.94444444444446</span> │ <span class="hljs-number">189.77618396416344</span> │
│ United   │ JFK               │ <span class="hljs-number">178.02777777777777</span> │   <span class="hljs-number">226.086205289536</span> │
│ Frontier │ ORL               │ <span class="hljs-number">206.38888888888889</span> │ <span class="hljs-number">261.27720485679146</span> │
│ United   │ SJC               │ <span class="hljs-number">119.91666666666667</span> │ <span class="hljs-number">153.72332650288018</span> │
│ KLM      │ SJC               │ <span class="hljs-number">218.13888888888889</span> │ <span class="hljs-number">275.90532796595284</span> │
│ KLM      │ JFK               │  <span class="hljs-number">70.30555555555556</span> │  <span class="hljs-number">90.43244869944515</span> │
│ Delta    │ JAX               │ <span class="hljs-number">186.55555555555554</span> │ <span class="hljs-number">236.69213477990067</span> │
│ Delta    │ ORL               │  <span class="hljs-number">74.44444444444444</span> │  <span class="hljs-number">95.50887102486577</span> │
│ Frontier │ SFO               │  <span class="hljs-number">63.02777777777778</span> │  <span class="hljs-number">80.91748197323548</span> │
│ Frontier │ PDX               │                 <span class="hljs-number">81</span> │ <span class="hljs-number">103.99278821149089</span> │
│ United   │ ORL               │              <span class="hljs-number">111.5</span> │ <span class="hljs-number">142.90031490518138</span> │
│ Frontier │ JAX               │  <span class="hljs-number">98.11111111111111</span> │ <span class="hljs-number">125.86147588166568</span> │
│ Frontier │ DIA               │  <span class="hljs-number">95.91666666666667</span> │ <span class="hljs-number">122.96758832219886</span> │
│ Delta    │ PDX               │  <span class="hljs-number">72.41666666666667</span> │  <span class="hljs-number">92.89046715830904</span> │
│ JetBlue  │ JFK               │ <span class="hljs-number">141.91666666666666</span> │ <span class="hljs-number">181.17877911057906</span> │
│ JetBlue  │ SJC               │              <span class="hljs-number">209.5</span> │  <span class="hljs-number">265.1057441013973</span> │
│ JetBlue  │ JAX               │ <span class="hljs-number">107.30555555555556</span> │ <span class="hljs-number">137.61893845769274</span> │
│ KLM      │ ORL               │ <span class="hljs-number">156.77777777777777</span> │ <span class="hljs-number">199.51287900506296</span> │
│ JetBlue  │ DIA               │  <span class="hljs-number">76.83333333333333</span> │  <span class="hljs-number">98.60076628054729</span> │
│ Frontier │ SJC               │  <span class="hljs-number">97.22222222222223</span> │  <span class="hljs-number">124.6602048236191</span> │
│ Frontier │ JFK               │ <span class="hljs-number">156.33333333333334</span> │ <span class="hljs-number">199.04550010264265</span> │
│ Delta    │ DIA               │                <span class="hljs-number">114</span> │  <span class="hljs-number">146.3065655092454</span> │
│ KLM      │ SFO               │ <span class="hljs-number">119.97222222222223</span> │  <span class="hljs-number">153.7722883573847</span> │
│ United   │ DIA               │  <span class="hljs-number">72.63888888888889</span> │  <span class="hljs-number">93.25666493905706</span> │
│ JetBlue  │ PDX               │ <span class="hljs-number">147.83333333333334</span> │  <span class="hljs-number">188.4872527372725</span> │
│ United   │ SFO               │ <span class="hljs-number">186.83333333333334</span> │ <span class="hljs-number">237.06668072740865</span> │
└──────────┴───────────────────┴────────────────────┴────────────────────┘

<span class="hljs-number">35</span> <span class="hljs-keyword">rows</span> <span class="hljs-keyword">in</span> set. Elapsed: <span class="hljs-number">0.024</span> sec. Processed <span class="hljs-number">18.48</span> thousand <span class="hljs-keyword">rows</span>, <span class="hljs-number">321.55</span> KB (<span class="hljs-number">785.99</span> thousand <span class="hljs-keyword">rows</span><span class="hljs-operator">/</span>s., <span class="hljs-number">13.68</span> MB<span class="hljs-operator">/</span>s.)
Peak memory usage: <span class="hljs-number">766.46</span> KiB.
</code></pre>

<div style="margin-top: 98rem">

## Model Inference

Finally, we can now use the model for generating the forecasts beyond the last date in the dataset. For this purpose, we create a new table containing the dates and their corresponding transformations (time trend and dummy variables) over the subsequent 3 years.

```sql
CREATE VIEW
    future_data
AS WITH
    (select toDate(min(MONTH)) from flight_data) as start_date,
    (select toDate(max(MONTH)) from flight_data) as end_date
SELECT
    AIRLINE,
    DEPARTURE_AIRPORT,
    MONTH + INTERVAL 3 YEAR as MONTH,
    assumeNotNull(dateDiff('month', start_date, MONTH) / dateDiff('month', start_date, end_date)) as Trend,
    if(toMonth(toDate(MONTH)) = 1, 1, 0) as Dummy1,
    if(toMonth(toDate(MONTH)) = 2, 1, 0) as Dummy2,
    if(toMonth(toDate(MONTH)) = 3, 1, 0) as Dummy3,
    if(toMonth(toDate(MONTH)) = 4, 1, 0) as Dummy4,
    if(toMonth(toDate(MONTH)) = 5, 1, 0) as Dummy5,
    if(toMonth(toDate(MONTH)) = 6, 1, 0) as Dummy6,
    if(toMonth(toDate(MONTH)) = 7, 1, 0) as Dummy7,
    if(toMonth(toDate(MONTH)) = 8, 1, 0) as Dummy8,
    if(toMonth(toDate(MONTH)) = 9, 1, 0) as Dummy9,
    if(toMonth(toDate(MONTH)) = 10, 1, 0) as Dummy10,
    if(toMonth(toDate(MONTH)) = 11, 1, 0) as Dummy11,
    if(toMonth(toDate(MONTH)) = 12, 1, 0) as Dummy12
FROM
    test_data
ORDER BY AIRLINE, DEPARTURE_AIRPORT, MONTH

```

Giving us an end to end visualisation of this. Visually, we can see that the increase in passenger numbers and the seasonality has been captured by the out of range forecast.

![hex03.png](https://clickhouse.com/uploads/hex03_016569f589.png)

## Conclusion

In this article we have demonstrated how we can use the ML functions (stochasticLinearRegression and evalMLMethod) that are avaialable within ClickHouse to implement a simple forecasting technique.

In principle, offloading metrics and analytics work like this to the database is a good thing. An analytical database such as ClickHouse will generally outperform and allow us to work with datasets that are bigger than can be processed on a single machine, whilst also reducing the amount of scripting work that needs to take place.

In ClickHouse, this could also be built into a materialized view, meaning that models are continually updated and retrained as new data is captured opening up real-time possibilities.

We believe this pattern could grow in future, with more data science and machine learning algorithms being implemented directly within the database.

A notebook describing the full worked example can be found at [this URL](https://app.hex.tech/d83ae9cc-7cbe-40f3-9899-0c348f283047/hex/ca938f0e-d8e0-4443-b58d-07d08db4a280/draft/logic).

</div>