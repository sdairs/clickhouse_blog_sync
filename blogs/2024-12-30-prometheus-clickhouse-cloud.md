---
title: "Prometheusを活用したClickHouse Cloudの強化されたモニタリング"
date: "2024-12-30T08:05:00.462Z"
author: "ClickHouse"
category: "Product"
excerpt: "本日、ClickHouse CloudがPrometheusとの連携による強化されたモニタリングをサポートしたことをお知らせします。"
---

# Prometheusを活用したClickHouse Cloudの強化されたモニタリング

本日、ClickHouse CloudがPrometheusによる拡張モニタリングをサポートしたことをお知らせできるのを楽しみにしています。この機能は一般利用可能で、クラウドインスタンスのモニタリングをこれまでになく簡単にします。ユーザーが普段使っているツールをそのまま利用できるため、オブザーバビリティにこだわるエンジニアにとって大きなメリットがあります。  

多くの組織にとって、クラウドサービスを導入するときに必須となる要件のひとつが、ClickHouse自体とは独立して、その稼働状況やパフォーマンスを監視できることです。  

この機能を試したい方は[こちらのドキュメント](https://clickhouse.com/docs/en/integrations/prometheus)をご覧ください。DatadogやGrafanaとどう連携するかを学習したい方のために、ドキュメントにはシンプルな例も用意しています。  

Prometheus APIを既存のアプローチに比べてどう活用できるかや、効率的に実装する上での課題に興味があれば、ぜひこのまま読み進めてください。  

## 背景と課題  

依存するクラウドサービスを集中して監視できることは、組織にとって重要です。これまで、ClickHouse Cloudを監視したいユーザーは、必要なメトリクスをsystemテーブルに対してSQLで問い合わせて取得する方法に頼っていました。SQLに慣れていたとしても、目的に合ったクエリを組み立てるために必要なsystemテーブルを探すのは時間がかかりがちです。さらに、監視エージェント用に適切なアクセス制御や権限の設定を行う手間も発生します。  

[Datadogなどのエージェント](https://docs.datadoghq.com/integrations/clickhouse/?_gl=1*iimrav*_gcl_au*MTIyOTE0NTEyOC4xNzE0NTU5MTU0*_ga*MzEzNTA0MTk0LjE3MTQ1NTkxNTU.*_ga_KN80RDFSQK*MTcxNDU2MTYxNS4yLjAuMTcxNDU2MTYxNS4wLjAuMTkyNjc5Nzc1NQ..*_fplc*NUNqVVFSN2hEQU02YUEyJTJGS2VDV0l0MzFYQmZ5emNJem5BdWx2OHlKT2NvYiUyQnVnbiUyRno3S0lpWTkwU1dzdUNtWW5pOWtNWHlKbzJxZjNRVGh5R0JxUlZZMjBGTHV3JTJGWG93cmF2SlpycnR1JTJGeEE4WUY3V0pWY1M3RnhJTkl2dyUzRCUzRA..&_ga=2.15437109.220939076.1714559156-313504194.1714559155&tab=host)を利用してClickHouse Cloudを監視する方法もありますが、Datadogの例ではクラウド側のプロキシレイヤーの都合上、呼び出すたびに異なるインスタンスへリクエストが飛ぶ可能性があり、結果的に取得したメトリクスの解釈が難しくなる課題がありました。clusterAllReplicas関数を使い、細かな設定を行うことで対策は可能でしたが、SELECTクエリによる定期的なポーリングが続くため、インスタンスがアイドル状態になるのを妨げる問題もありました。  

ClickHouse Cloudのインスタンスは、利用していないときに自動的にアイドル化してコンピュートコストを抑える仕組みを備えています。そのため、監視のために継続的にクエリを投げ続けることが、ユーザーにとって好ましくないケースが多かったのです。  

さらに、Prometheusフォーマットはこの手のメトリクスデータにおいて事実上の標準になりつつあり、GrafanaやDatadogなどの人気ツールも標準で対応しています。  

よって、インスタンスが未使用のときに邪魔をせず、アイドル状態を妨げることなくPrometheus形式のメトリクスを提供できるシンプルなエンドポイントが最適解だと考えました。  

## シンプルでエレガントな設計  

今回のエンドポイントに求められる要件は以下のとおりです:  

* **Prometheus形式のメトリクスを返す** - 既存の広く使われている監視エージェントに対応する  
* **アイドル状態のインスタンスを起こさない** - アイドル状態なら、そのことを示す簡単な情報だけ返す  
* **インスタンスのアイドル化を妨げない** - このエンドポイントへのリクエストは、インスタンスのアイドル化判定に影響を与えない  

ClickHouse本体側の[設定機能](https://clickhouse.com/docs/en/operations/server-configuration-parameters/settings#prometheus)を活用して各インスタンスにPrometheusエンドポイントを個別に設定することも考えられましたが、アイドル状態のインスタンスをどう扱うかという問題があり、さらにインスタンスごとにユーザーを作り権限を設定してエージェント側へ配布するのは、セキュリティ上のリスクや運用面の煩雑さを招きます。  

そこで、このエンドポイントを[既存のCloud API](https://clickhouse.com/docs/en/cloud/manage/api/api-overview)として実装することにしました。このAPIはすでにインスタンスの作成や設定を扱っており、組織単位のアクセス制御も備えています。数クリックでAPIキーを作成・取り消しできるため、セキュリティの攻撃面を最小限にしつつ、ClickHouseやSQLの知識が不要なシンプルなエンドポイントを提供できます。  

その結果、組織IDとインスタンスIDを指定するだけで、Prometheus形式のメトリクスを安全にリクエストできるCloud APIエンドポイントを用意しました。  

![prometheus_01.png](https://clickhouse.com/uploads/prometheus_01_a5a8008aad.png)  

> APIキーは組織単位で作成され、「Developer」または「Admin」を選択できます。Prometheusエンドポイントには「Developer」権限で十分なので、不正アクセスを受けても新しいサービスの作成や破壊などのリスクを最小化できます。  

## 実装  

Cloud API経由でこのエンドポイントを実装することで、仕組みをシンプルに保ちました。Cloud APIはすでに各インスタンスの状態を把握しており、アイドル状態のインスタンスにはリクエストを送らないようにできるからです。インスタンスが稼働中であれば、権限を絞った専用ユーザーでリクエストを発行します。このユーザーからのリクエストは、インスタンスのアイドル化判定の対象外となります。  

### メトリクス収集の効率化  

あとは、systemテーブルで必要なメトリクスを集約するクエリをどう書くかという問題が残りました。ユーザーが必要とするメトリクスは複数のsystemテーブルに散在しており、ひとつの大きなクエリで取得するとそれなりに負荷がかかります。そこで、このクエリを毎回実行しないよう、最近追加された[Refreshable Materialized Views](https://clickhouse.com/blog/clickhouse-release-23-12#refreshable-materialized-views)の仕組みを活用しています。  

このビューは現在1分ごとに定期的にクエリを実行し、その結果を`system.custom_metrics`テーブルに書き込みます。このターゲットテーブルはMemoryエンジンを使っており、Cloud APIから高速に参照可能です。以下のテーブル定義とビューの例を示します（興味がある方向けです）。  

```sql
CREATE TABLE system.custom_metrics
(
	`name` String,
	`value` Float64,
	`help` String,
	`labels` Map(String, String),
	`type` String
)
ENGINE = Memory
```

```sql
CREATE MATERIALIZED VIEW system.custom_metrics_refresher
REFRESH EVERY 1 MINUTE TO system.custom_metrics
(
	`name` String,
	`value` Nullable(Float64),
	`help` String,
	`labels` Map(String, String),
	`type` String
)
AS SELECT
	concat('ClickHouse_', event) AS name,
	toFloat64(value) AS value,
	description AS help,
	map('hostname', hostName(), 'table', 'system.events') AS labels,
	'counter' AS type
FROM system.events
UNION ALL
//他のメトリクス
```

このように、マテリアライズドビューのリフレッシュ間隔によってクエリを実行する頻度を制御し、1分に1回以上は走らないようにしています。誤った設定のエージェントなどから過剰なリクエストを送られても、サービスに負荷がかかるようなことを防げます。  

## エンドポイントの利用方法  

まずはClickHouse CloudでAPIキーを作成します。その手順は次のとおりです。  

![prometheus_02.gif](https://clickhouse.com/uploads/prometheus_02_161cd4ae79.gif)  

エンドポイントが利用できる状態になったら、組織IDとインスタンスIDを取得します。  

![prometheus_03.gif](https://clickhouse.com/uploads/prometheus_03_1630d99c09.gif)  

あとは、以下のようにHTTPリクエストを送るだけです:  

<pre><code class="hljs language-bash" style="font-size: 12px;"><span class="hljs-built_in">export</span> KEY_SECRET=&lt;key_secret&gt;
<span class="hljs-built_in">export</span> KEY_ID=&lt;key_id&gt;
<span class="hljs-built_in">export</span> ORG_ID=&lt;org <span class="hljs-built_in">id</span>&gt;
<span class="hljs-built_in">export</span> INSTANCE_ID=&lt;instance <span class="hljs-built_in">id</span>&gt;
curl --silent --user <span class="hljs-variable">$KEY_ID</span>:<span class="hljs-variable">$KEY_SECRET</span> https://api.control-plane.clickhouse-staging.com/v1/organizations/<span class="hljs-variable">$ORG_ID</span>/services/<span class="hljs-variable">$INSTANCE_ID</span>/prometheus 

…
<span class="hljs-comment"># HELP ClickHouse_ServiceInfo サービスに関する情報（クラスタのステータスやClickHouseのバージョンなど）</span>
<span class="hljs-comment"># TYPE ClickHouse_ServiceInfo untyped</span>
ClickHouse_ServiceInfo{clickhouse_org=<span class="hljs-string">"c2ba4799-a76e-456f-a71a-b021b1fafe60"</span>,clickhouse_service=<span class="hljs-string">"12f4a114-9746-4a75-9ce5-161ec3a73c4c"</span>,clickhouse_service_name=<span class="hljs-string">"test service"</span>,clickhouse_cluster_status=<span class="hljs-string">"running"</span>,clickhouse_version=<span class="hljs-string">"24.5"</span>,scrape=<span class="hljs-string">"full"</span>} 1

<span class="hljs-comment"># HELP ClickHouseProfileEvents_Query クエリとして解釈され、実行される可能性があるクエリの数</span>
<span class="hljs-comment"># TYPE ClickHouseProfileEvents_Query counter</span>
ClickHouseProfileEvents_Query{clickhouse_org=<span class="hljs-string">"c2ba4799-a76e-456f-a71a-b021b1fafe60"</span>,clickhouse_service=<span class="hljs-string">"12f4a114-9746-4a75-9ce5-161ec3a73c4c"</span>,clickhouse_service_name=<span class="hljs-string">"test service"</span>,hostname=<span class="hljs-string">"c-cream-ma-20-server-3vd2ehh-0"</span>,instance=<span class="hljs-string">"c-cream-ma-20-server-3vd2ehh-0"</span>,table=<span class="hljs-string">"system.events"</span>} 6

<span class="hljs-comment"># HELP ClickHouseProfileEvents_QueriesWithSubqueries サブクエリを含むすべてのクエリの数</span>
<span class="hljs-comment"># TYPE ClickHouseProfileEvents_QueriesWithSubqueries counter</span>
ClickHouseProfileEvents_QueriesWithSubqueries{clickhouse_org=<span class="hljs-string">"c2ba4799-a76e-456f-a71a-b021b1fafe60"</span>,clickhouse_service=<span class="hljs-string">"12f4a114-9746-4a75-9ce5-161ec3a73c4c"</span>,clickhouse_service_name=<span class="hljs-string">"test service"</span>,hostname=<span class="hljs-string">"c-cream-ma-20-server-3vd2ehh-0"</span>,instance=<span class="hljs-string">"c-cream-ma-20-server-3vd2ehh-0"</span>,table=<span class="hljs-string">"system.events"</span>} 230

<span class="hljs-comment"># HELP ClickHouseProfileEvents_SelectQueriesWithSubqueries サブクエリを含むSELECTクエリの数</span>
<span class="hljs-comment"># TYPE ClickHouseProfileEvents_SelectQueriesWithSubqueries counter</span>
ClickHouseProfileEvents_SelectQueriesWithSubqueries{clickhouse_org=<span class="hljs-string">"c2ba4799-a76e-456f-a71a-b021b1fafe60"</span>,clickhouse_service=<span class="hljs-string">"12f4a114-9746-4a75-9ce5-161ec3a73c4c"</span>,clickhouse_service_name=<span class="hljs-string">"test service"</span>,hostname=<span class="hljs-string">"c-cream-ma-20-server-3vd2ehh-0"</span>,instance=<span class="hljs-string">"c-cream-ma-20-server-3vd2ehh-0"</span>,table=<span class="hljs-string">"system.events"</span>} 224

<span class="hljs-comment"># HELP ClickHouseProfileEvents_FileOpen 開かれたファイルの回数</span>
<span class="hljs-comment"># TYPE ClickHouseProfileEvents_FileOpen counter</span>
ClickHouseProfileEvents_FileOpen{clickhouse_org=<span class="hljs-string">"c2ba4799-a76e-456f-a71a-b021b1fafe60"</span>,clickhouse_service=<span class="hljs-string">"12f4a114-9746-4a75-9ce5-161ec3a73c4c"</span>,clickhouse_service_name=<span class="hljs-string">"test service"</span>,hostname=<span class="hljs-string">"c-cream-ma-20-server-3vd2ehh-0"</span>,instance=<span class="hljs-string">"c-cream-ma-20-server-3vd2ehh-0"</span>,table=<span class="hljs-string">"system.events"</span>} 4157

<span class="hljs-comment"># HELP ClickHouseProfileEvents_Seek 'lseek'関数が呼び出された回数</span>
<span class="hljs-comment"># TYPE ClickHouseProfileEvents_Seek counter</span>
ClickHouseProfileEvents_Seek{clickhouse_org=<span class="hljs-string">"c2ba4799-a76e-456f-a71a-b021b1fafe60"</span>,clickhouse_service=<span class="hljs-string">"12f4a114-9746-4a75-9ce5-161ec3a73c4c"</span>,clickhouse_service_name=<span class="hljs-string">"test service"</span>,hostname=<span class="hljs-string">"c-cream-ma-20-server-3vd2ehh-0"</span>,instance=<span class="hljs-string">"c-cream-ma-20-server-3vd2ehh-0"</span>,table=<span class="hljs-string">"system.events"</span>} 1840
…
</code></pre>  

ClickHouse CloudのPrometheusエンドポイントは、[ClickHouseネイティブのPrometheusエンドポイント](https://clickhouse.com/docs/en/operations/server-configuration-parameters/settings#prometheus)と同等のメトリクスを公開しています。上記は一部の例ですが、実際にはClickHouseを監視するのに有用な1000を超えるメトリクスを返しています。公開されているメトリクスはClickHouseのドキュメントで確認できます。  

もし必要なメトリクスがあれば、ぜひご要望をお知らせください。  

インスタンスがアイドル状態の場合は、以下のように示されます:  

```bash
# HELP ClickHouse_ServiceInfo サービスに関する情報（クラスタのステータスやClickHouseのバージョンなど）
# TYPE ClickHouse_ServiceInfo untyped
ClickHouse_ServiceInfo{clickhouse_org="c2ba4799-a76e-456f-a71a-b021b1fafe60",clickhouse_service="12f4a114-9746-4a75-9ce5-161ec3a73c4c",clickhouse_service_name="test service",clickhouse_cluster_status="idle",clickhouse_version="24.5",scrape="full"}
```  

## Prometheusの例  

Prometheusをインストールするには、公式の[ガイド](https://prometheus.io/docs/prometheus/latest/installation/)を参照してください。  

下記はClickHouse CloudをPrometheusでスクレイプする設定例です。先ほどの手順で取得した `<ORG_ID>`、`<INSTANCE_ID>`、`<KEY_ID>`、`<KEY_SECRET>`が必要です。`honor_labels`の設定は`true`にしておく必要があります。こうしないと、インスタンスラベルが正しく設定されません。  

```yaml
global:
  scrape_interval: 15s
scrape_configs:
  - job_name: "prometheus"
    static_configs:
    - targets: ["localhost:9090"]
  - job_name: "clickhouse"
    static_configs:
      - targets: ["api.clickhouse.cloud"]
    scheme: https
    metrics_path: "/v1/organizations/<ORG_ID>/services/<INSTANCE_ID>/prometheus"
    basic_auth:
      username: <KEY_ID>
      password: <KEY_SECRET>
    honor_labels: true
```  

## Datadogの例  

Datadog Agentと[OpenMetrics連携](https://docs.datadoghq.com/integrations/guide/prometheus-host-collection/)を使うと、ClickHouse Cloudのエンドポイントからメトリクスを収集できます。以下は簡単な設定例です。  

```yaml
init_config:

instances:
   - openmetrics_endpoint: 'https://api.control-plane.clickhouse.com/v1/organizations/97a33bdb-4db3-4067-b14f-ce40f621aae1/services/f7fefb6e-41a5-48fa-9f5f-deaaa442d5d8/prometheus'
     namespace: 'clickhouse'
     metrics:
         - '^ClickHouse_.*'
     username: username
     password: password
```  

下記は、Datadogエージェントで収集したメトリクスを使い、大きなINSERT処理を実行中のClickHouseを監視する様子です:  

![prometheus_04.png](https://clickhouse.com/uploads/prometheus_04_f635fe5b64.png)  

DatadogやGrafanaとの連携については、[こちらのドキュメント](https://clickhouse.com/docs/en/integrations/prometheus)で詳しく解説しています。  

## 結論  

今回リリースしたPrometheus連携によって、お気に入りのオブザーバビリティツールでClickHouse Cloudを簡単に監視できるようになります。メトリクスのセットは、私たちがClickHouseを監視する中で有用だと感じたものが中心ですが、今後も拡張される予定です。もし必要なメトリクスや、ほかのツールとの連携に関する要望があれば、ぜひ教えてください。  