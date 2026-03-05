---
title: "ClickPipes向けPostgres CDCコネクタがパブリックベータで利用可能になりました"
date: "2025-02-19T00:38:53.169Z"
author: "Sai Srirampur"
category: "Product"
excerpt: "ClickPipesでPostgres CDCコネクタがパブリックベータとして利用可能になったことを大変うれしく思います。これにより、お客様は数回のクリックだけで、PostgresデータベースをClickHouse Cloudへ簡単にレプリケートできるようになります。"
---

# ClickPipes向けPostgres CDCコネクタがパブリックベータで利用可能になりました

本日、[ClickPipes向けPostgres CDCコネクタのパブリックベータ版](https://clickhouse.com/cloud/clickpipes/postgres-cdc-connector)をリリースしたことをお知らせします。これにより、お客様はPostgresデータベースをClickHouse Cloudに数回のクリックで簡単にレプリケートできるようになります。実際に使うには、サービスの**Data Source**タブに移動し、Postgresのタイルを選択して、Postgresデータベースとの連携を数ステップで設定するだけです。

<img src="/uploads/Postgres_CDC_Add_Data_Source_e058704d02.gif" 
     alt="Postgres CDC Add Data Source" 
     loading="lazy">

Postgres CDCのリーディングカンパニーである[PeerDBとの提携](https://clickhouse.com/blog/clickhouse-welcomes-peerdb-adding-the-fastest-postgres-cdc-to-the-fastest-olap-database)により、ClickHouse Cloudにネイティブ統合を実現し、[Postgres CDCコネクタをClickPipes向けにプライベートプレビュー](https://clickhouse.com/blog/postgres-cdc-connector-clickpipes-private-preview)としてリリースしました。

プライベートプレビュー期間中には、多くのお客様から大きな反響をいただきました。実際にサービスを試したり、貴重なフィードバックをお寄せいただいたり、運用環境で利用してペタバイト規模のデータをPostgresからClickHouseにレプリケートいただいたケースもありました。その後、さらなる改善を加え、今回、ネイティブなPostgres CDCをClickHouse Cloud上で誰でも利用できるようパブリックベータとしてご提供します。

## お客様のフィードバック

Postgres CDCコネクタは、すでに[Syntage](https://syntage.com/)、[Neon](https://neon.tech/)、[Blacksmith](https://www.blacksmith.sh/)、[Vapi](https://vapi.ai/)、[Adora](https://adora.so/)、[Daisychain](https://www.daisychain.app/)、[Unify](https://www.unifygtm.com/home-lp)、[Ottimate](https://ottimate.com/)など、さまざまな企業に導入されています。以下に、参考顧客からいただいたフィードバックを一部ご紹介します：

_“Postgres CDCコネクタをClickPipesで利用していて、素晴らしい体験をしています。30TBものAuroraデータベースをClickHouse Cloudへシームレスに移行し、常時同期を維持できています。過去にETLツールで苦い経験をしていたため、当初は高負荷に耐えられるツールは期待していませんでしたが、ClickPipesは信頼性とパフォーマンスの点で非常に驚きでした。”_ - [Matteus Pedroso](https://www.linkedin.com/in/matheuspedroso/), Co-founder and CEO, [Syntage](https://syntage.com/)

_“私たちはNeonの課金データ（Postgres）をリアルタイム分析のためにClickHouseへ同期していますが、ClickPipes for Postgresのおかげでこのプロセスが非常に簡単になりました。CDCの速度はとても速く、数秒以内の最新データを扱える上、運用中のPostgresデータベースへの負荷も最小限に抑えられています。PostgresとClickHouseをスムーズに統合するために欠かせないソリューションです！”_ - Mo Abedi, Software Engineer in Billing team, [Neon.tech](https://neon.tech/)

## 製品の強化ポイント

<iframe width="768" height="432" src="https://www.youtube.com/embed/fHuFSmafYUo?si=yEFblvI2MuUBadBO" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

### パフォーマンスを最優先に設計

このPostgres CDCコネクタは、高いパフォーマンスを実現するよう、PostgresとClickHouseの特性を最大限に活かして設計されています。Postgres側では並列スナップショット機能により、初期ロードやバックフィルを10倍高速化し、テラバイト規模の移行も数時間で完了できます。また、[レプリケーションスロットを連続的にフラッシュ](https://clickhouse.com/blog/enhancing-postgres-to-clickhouse-replication-using-peerdb#efficiently-flush-the-replication-slot)する仕組みにより、数秒単位で常に最新データを反映可能です。  
ClickHouse側でも、複数レプリカへの並列書き込みや、[メモリ管理を最適化するチャンク分割の設定](https://clickhouse.com/blog/enhancing-postgres-to-clickhouse-replication-using-peerdb#better-memory-handling-on-clickhouse)などにより、パフォーマンスと信頼性をさらに向上しています。

これらの基本設計に加えて、過去数ヶ月でエンタープライズ級の運用を支援する新機能が多数追加されました。以下に主な強化点をご紹介します。

### ユーザー向けアラート機能

この機能により、ClickPipeに関する障害や問題の兆候をアラートとしてお知らせします。アラートはClickHouse Cloudの通知センターやメール経由で通知され、たとえば「レプリケーションスロットが異常に増えている」「ストリーム外のマテリアライズドビュー（MV）で取り込みに失敗している」「接続性の問題がある」など、状況に応じて問題が分類されます。あわせて自己解決のための手順も案内されるため、迅速なトラブルシューティングが可能です。

<img src="/uploads/Postgres_CDC_User_Notifications_cddc06fced.gif" 
     alt="ユーザーが通知を設定する様子" 
     loading="lazy">

### ソースモニタリングページ

CDC実行中のPostgresデータベースを監視できる新しいページも追加しました。このページでは、アクティブなレプリケーションスロットの一覧やステータス、スロットのサイズ変化を示すグラフ、Postgres側のウェイトイベントなど、重要な指標を可視化します。レプリケーションの進捗を把握し、ボトルネックの特定やパフォーマンス最適化に役立てることができます。

![Postgresのレプリケーションスロット状況と遅延を示すビジュアル](https://clickhouse.com/uploads/Postgres_CDC_Source_Monitoring_852798cd65.png)

### Open API対応

プライベートプレビュー期間中、多くのお客様から「管理対象テーブルが多い場合、UIだけでパイプを作成・管理するのは手間がかかる」という声が寄せられました。そこで、Open APIによるプログラムでのパイプ管理が可能になりました。現在はプライベートベータとして提供しており、興味のある方は[db-integrations-support@clickhouse.com](mailto:db-integrations-support@clickhouse.com)までご連絡ください。今後はTerraformでPostgres CDC向けClickPipesを管理できる機能も追加予定です。

### PeerDB オープンソースの強化

このコネクタは、[オープンソース](https://github.com/PeerDB-io/peerdb/)のPostgres CDCコードベースであるPeerDBをベースにしています。エンタープライズ運用に対応できるよう、ここ数ヶ月で機能強化を進めてきました。過去2ヶ月で、8回のマイナーリリースと3回のメジャーリリースを含む多数の[リリース](https://github.com/PeerDB-io/peerdb/releases)を行っています。主な改善点は以下のとおりです。

* [複数のClickHouseレプリカを利用した取り込みで性能を向上](https://github.com/PeerDB-io/peerdb/pull/2256)  
* [重負荷下でも性能を落とさないよう、レプリケーションスロットへの再接続を排除](https://github.com/PeerDB-io/peerdb/pull/2371)  
* [誤検知エラーを除外するためのリトライロジックを一新](https://github.com/PeerDB-io/peerdb/pull/2122)  
* Postgresからのデータ取得とClickHouseへの書き込みを非同期化し、レプリケーションスロットのフラッシュ処理を最適化  

## 料金体系

パブリックベータ期間中、Postgres CDCコネクタ（ClickPipes）は無料でご利用いただけます。今後、次の段階であるGA（General Availability）フェーズに移行するときに価格を導入する予定です。詳細はまだ検討中ですが、リアルタイム分析ユースケースをスケールさせやすいよう、競争力ある価格設定を目指します。

## まとめ

最後までお読みいただきありがとうございます。現在はパブリックベータとしてPostgres CDCの機能を提供しており、今後、製品が十分に成熟した段階でGAリリースを目指します。パブリックベータ期間中に何か問題が発生したり、質問やご意見がある場合、あるいは製品チームと直接話したい場合は、[db-integrations-support@clickhouse.com](mailto:db-integrations-support@clickhouse.com)までお気軽にご連絡ください。

ネイティブなPostgres CDC機能をClickHouse Cloudでお試しいただけるよう、以下のリンクをぜひご覧ください。

- [PostgresからClickHouseへのデータ取り込み（CDC方式）](https://clickhouse.com/docs/en/integrations/clickpipes/postgres)  
- [ClickPipes for Postgresに関するFAQ](https://clickhouse.com/docs/en/integrations/clickpipes/postgres/faq)  
- [ClickHouse Cloudを無料で試してみる](https://clickhouse.com/docs/en/cloud/get-started/cloud-quick-start)  