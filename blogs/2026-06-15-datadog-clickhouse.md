---
title: "Datadog と ClickHouse が提携、最新のオブザーバビリティにフルフィデリティ（全量）なデータをもたらす"
date: "2026-06-15T07:52:31.073Z"
author: "ClickHouse"
category: "Product"
excerpt: "ClickHouseとDatadogが提携し、大規模環境での完全忠実なログ保持と、エンジニアが日々頼りにしている強力な検索・調査体験を組み合わせて提供します。"
---

# Datadog と ClickHouse が提携、最新のオブザーバビリティにフルフィデリティ（全量）なデータをもたらす

オブザーバビリティチームがこれまで以上に多くのデータを収集する時代になりました。AIアプリケーション、エージェント型ワークフロー、そしてますます分散化するシステムの台頭により、テレメトリの量はわずか数年前には想像もできなかった水準にまで達しています。

その結果、ClickHouseはオブザーバビリティデータを大規模に保存・分析しようとする組織にとっての第一選択肢として、ますます採用されるようになっています。[OpenAI](https://clickhouse.com/blog/why-openai-uses-clickhouse-for-petabyte-scale-observability)、DoorDash、[Anthropic](https://clickhouse.com/blog/how-anthropic-is-using-clickhouse-to-scale-observability-for-ai-era)、Shopifyなどがその例であり、長期保持に必要なコスト効率と高速なクエリ性能を兼ね備えています。同時に、Datadogは業界で最も人気のあるオブザーバビリティプラットフォームの一つとしての地位を確立しています。

これまで多くの組織は、完全なテレメトリデータを保持することと、そのデータを日々利用しているツールからアクセス可能な状態に保つことの間で、選択を迫られることが少なくありませんでした。保持期間、サンプリング戦略、保存場所に関する判断は、運用上の要件よりもコストの観点から左右されることが多々ありました。

本日、こうしたトレードオフを解消するための、ClickHouseとDatadogによる新たなパートナーシップを発表できることを大変嬉しく思います。Previewとして提供される新機能により、組織はDatadog Observability Pipelinesを通じてログを直接ClickHouseへルーティングし、そのログをDatadog Log Explorerから検索できるようになります。ClickHouseのコスト効率とパフォーマンスを、Datadogの使い慣れた体験と組み合わせることが可能になります。

## Datadog Observability PipelinesでClickHouseへログをルーティングする

Datadog Observability Pipelinesは、幅広いソースからテレメトリを収集・処理・ルーティングする柔軟な手段を提供します。OpenTelemetryやOCSFといったオープン標準をサポートしており、組織はテレメトリを一元管理しつつ、データの保存先をコントロールできます。

![datadog_to_clickhouse.png](https://clickhouse.com/uploads/datadog_to_clickhouse_28cf8ed604.png)

ネイティブのClickHouse宛先により、Observability Pipelinesを通じてログを直接ClickHouseへルーティングできるようになりました。ClickHouseへ到達する前に、パース、エンリッチメント、フィルタリング、変換、リダクションといった機能を活用し、ログが一貫した構造を持ち、分析に必要なコンテキストを備えた状態にすることができます。

これらの機能は、エンリッチメントとルーティングを大規模に管理する簡便な手段を提供することで、OpenTelemetry Collectorを補完します。組織はDatadogの広範な収集エコシステム(インテグレーションやエージェントを含む)を継続的に利用しながら、OpenTelemetry互換のスキーマを用いてClickHouseへテレメトリを送ることができます。

その結果として実現するのが、大量のテレメトリに最適化された柔軟なオブザーバビリティアーキテクチャです。チームは直近のデータをDatadogで調査しつつ、完全なテレメトリデータセットをClickHouseに保持することで、ワークフローを変えることなく、履歴分析、長期にわたる調査、フル忠実度のデータアクセスを可能にします。[ClickHouse Cloudのストレージとコンピュートの分離](https://clickhouse.com/docs/cloud/reference/shared-merge-tree)により、組織は低コストでデータを保持しつつ、クエリリソースを独立してスケールさせ、ワークロードを分離し、保持データに影響を与えることなく要件の変化に応じて容量を調整できます。

## ClickHouseのログをDatadog Log Explorerから直接検索する

ストレージは、必要なときにデータにアクセスできて初めて意味を持ちます。

フェデレーテッドログ検索により、チームはClickHouseに保存されたログをDatadog Log Explorerから直接検索できます。ログはClickHouseに留まったままで、データの複製や再取り込みは不要であり、エンジニアがすでに利用しているトラブルシューティングや調査のワークフローをそのまま維持できます。

このアプローチには、いくつかの利点があります。

第一に、組織は大幅に多くのテレメトリをより長期間保持でき、調査で必要となった際に履歴データを利用可能な状態に保てます。サンプリング、フィルタリング、破棄の対象となりかねない大量のログも、ClickHouseに保存しつつDatadogから検索可能なままにできます。

第二に、チームは単一のインターフェースで作業を進められ、すでに慣れ親しんだDatadogの体験を維持しながら、ClickHouseのスケーラビリティとフル忠実度のテレメトリ保持を享受できます。エンジニアは、特定のデータセットがどこにあるかに応じて複数のシステムを切り替える必要がなくなります。

最後に、データは元々保存された場所に留まります。クエリはClickHouseに対して直接実行されるため、テレメトリの重複コピーを維持するための運用負担を回避できます。

## 両プラットフォームの強みを融合する

ClickHouseとDatadogを組み合わせることで、チームは慣れ親しんだワークフローで調査・トラブルシューティング・検索を続けながら、はるかに多くのテレメトリデータを保存・保持できるようになります。その結果が、柔軟なオブザーバビリティアーキテクチャです。Datadogはエンジニアリングチームが日々頼りにしている収集、ユーザー体験、調査機能を提供し、ClickHouseは長期的なテレメトリ保存と分析のためのスケーラブルな基盤を提供します。

このパートナーシップにより、お客様は性能、使いやすさ、データへのアクセス性を犠牲にすることなく、データの保存場所、保持期間、アクセス方法に対するコントロールを強化できます。

## はじめに

Datadog Observability Pipelines向けのネイティブClickHouseインテグレーションと、Datadog Log Explorerからのフェデレーテッドログ検索は、Previewとして提供されます。

ClickHouseのスケーラブルなオブザーバビリティストレージとDatadogのオブザーバビリティ体験を組み合わせることに関心をお持ちであれば、本日より[https://www.datadoghq.com/product-preview/federated-search/](https://www.datadoghq.com/product-preview/federated-search/)からプライベートプレビューへのアクセスをリクエストいただけます。

---

## 今すぐ始めましょう

ClickStack が皆さんのオブザーバビリティデータでどのように動作するか試してみませんか？ClickHouse Cloud のマネージド ClickStack なら数分で利用を開始でき、$300 の無料クレジットも受け取れます。

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-886-sign-up&utm_blogctaid=886)

---