# R2 Data Catalog & R2 SQL

## 一行サマリ
R2バケット内のParquetをApache Icebergテーブルとして管理する「Iceberg REST Catalog」と、その上で動くサーバレスSQLエンジン「R2 SQL」をCloudflareがマネージドで提供する。エグレス無料のオブジェクトストレージをそのままレイクハウスの一次層に変える組合せである。

## 解決する課題（Why）
データレイクをS3に置くと「ストレージは安いがクエリのたびにエグレスとリクエスト課金が積み上がる」「Glue Catalog / Athena / EMR / Snowflakeなど複数サービスを束ねないと分析できない」という構造問題から逃れにくい。Iceberg自体は仕様に過ぎず、カタログサーバ・テーブルメンテナンス（コンパクション、スナップショット失効）・クエリエンジンを別々に運用する必要があり、PoC段階の小規模チームには重い。Cloudflare R2 Data Catalog + R2 SQLは以下を解決する。

- R2のゼロエグレスを活かして、外部クラウド・他リージョンからも追加課金なしで分析できるレイクハウス基盤を作る。
- Iceberg REST Catalogをマネージドで提供し、自前でNessie / Polaris / Glueを立てる手間を省く。
- 同じテーブルをSpark / Trino / DuckDB / PyIceberg / Snowflakeから並行アクセスでき、エンジン選択の自由度を確保する。
- Cloudflare PipelinesでWorkers / Queuesからのストリームを直接Icebergテーブルに書き込み、ETLパイプラインを最小化する。
- R2 SQLでBIユースケースの軽量クエリは追加サービス不要で完結させる。

## 主要機能（What）

### Iceberg REST Catalog
R2バケット単位でカタログを有効化すると、Apache Iceberg REST Catalog仕様に準拠したエンドポイントが払い出される。Cloudflareが裏側でメタデータJSON・マニフェスト・スナップショットを管理し、クライアントは標準Icebergクライアント（pyiceberg、iceberg-spark-runtime、Trino iceberg connector等）から接続できる。

- カタログ単位：R2バケットごとに1カタログ。Namespace（DB相当）とTable（テーブル）の2階層。
- 認証：Cloudflare APIトークンをBearerとして渡す。Iceberg REST仕様の`/v1/config`、`/v1/namespaces`、`/v1/namespaces/{ns}/tables`等がそのまま使える。
- ストレージ：Parquetファイル本体はR2バケット内にIceberg標準レイアウトで配置される。S3互換APIとIceberg APIの両方からアクセス可能。
- スキーマ進化・タイムトラベル・パーティション進化などIceberg v2仕様の機能が利用できる。

### Table maintenance
Icebergで実運用すると不可避の「小ファイル問題」「孤児ファイル蓄積」「スナップショット肥大」をCloudflare側でバックグラウンド実行する。利用者は明示的にcompactionジョブを書く必要がない（ただしベータ段階では自動化範囲は段階的に拡大中）。

### R2 SQL
R2 Data Catalog上のIcebergテーブルをSQLで直接クエリするサーバレス分散エンジンである。Wrangler CLIまたはAPI経由で投げる。ファイルプルーニング・分散コンピュートを自動適用し、クエリごとにスキャン量に応じた課金（オープンベータ中は無料）。

- インターフェース：`wrangler r2 sql query <warehouse> "<SQL>"` の単発クエリ実行が中心。BIツール向けJDBC/ODBCは現時点では未提供。
- ユースケース：軽量な集計・直近データの確認・Workers Analytics連携。重い長時間ジョブはSpark / Trinoに振る使い分けが想定される。

### コネクタ（Spark / DuckDB / Trino / PyIceberg / Snowflake）
Iceberg REST Catalog標準準拠のため、各エンジンの公式コネクタがそのまま使える。

- **PyIceberg**：`pyiceberg.catalog.load_catalog`に`type=rest`、`uri`、`token`を渡すだけで接続。ノートブック検証の最短経路。
- **DuckDB**：`iceberg`拡張＋`ATTACH 'r2_catalog' AS catalog (TYPE iceberg, ENDPOINT '...')`でローカルから直接クエリ。
- **Spark / Trino**：`iceberg-rest`カタログ設定でwarehouse URIとR2のS3互換アクセスキーを渡す。EMR / Databricks / 自前k8s Sparkどれからでも接続可能。
- **Snowflake**：External Volume（S3互換としてR2を指定）＋ Iceberg Catalog Integration（REST）で外部Icebergテーブルを参照。

### Cloudflare Pipelines連携
Cloudflare Pipelines（Workers / Queues / HTTPからのストリームをバッチ化してR2に書き出すサービス）が、出力先としてR2 Data Catalogを直接サポートする。Workersのイベント → Pipelines → Icebergテーブル化、までをCloudflare内で完結できる。これによりKafka + Flink + Iceberg Sinkに相当する構成を、Cloudflareスタック単独で組める。

## アーキテクト視点：いつ選ぶか

### 適しているシーン
- 既にR2をオブジェクトストレージとして使っており、ログ・イベント・clickstreamを分析したいケース。エグレス無料で他クラウドのSparkクラスタからも引ける。
- マルチクラウドでデータを共有したいが、AWS S3に置くとGCP / Azure側からの転送費用が重いケース。
- Workers / Queues / Pipelinesでイベントパイプラインを組んでいる組織。Sink先としてIcebergテーブルが直結する。
- BIではなく「Notebookでアドホックに探索」「DuckDB / PyIcebergで小回りに分析」が中心の小〜中規模チーム。
- スタートアップ・PoC段階で、Snowflake / Databricksの最低契約額を払う前にレイクハウスを立てたいケース。

### 適していないシーン
- Snowflake / Databricks / BigQueryで既にエンタープライズ契約があり、UC（Unity Catalog）/ Polaris / BigLake metastoreによるガバナンスが要件化している組織。
- 細かい行レベルセキュリティ・列マスキング・データリネージなどガバナンス機能が必須のケース。Cloudflareは現時点でテーブル単位のIcebergアクセスに留まる。
- ストリーミング更新の遅延要件が秒オーダーのケース。Pipelinesはバッチ前提で、Iceberg側のコミット粒度も分単位が現実的。
- ペタバイト級でクエリレイテンシSLAが厳しいワークロード。R2 SQLはまだベータで、本格BIにはSpark / Trino併用が前提。

## 競合・代替

| 観点 | R2 Data Catalog + R2 SQL | AWS S3 Tables | Snowflake Iceberg | Databricks UC | Tabular（買収済） | GCP BigLake | MotherDuck |
|---|---|---|---|---|---|---|---|
| 出自 | R2 + Workers Pipelines統合 | S3 + Athena統合 | DWH純血 | Spark / Lakehouse純血 | Iceberg設立メンバー製カタログ | BigQuery + GCS統合 | DuckDBクラウド |
| カタログ | Iceberg REST（マネージド） | S3 Tables（独自＋REST互換） | Snowflake Catalog / Polaris OSS | Unity Catalog | Iceberg REST | BigLake metastore | DuckDB Catalog |
| クエリエンジン | R2 SQL（ベータ）+ 外部Spark/Trino/DuckDB | Athena / EMR / Redshift | Snowflake | Photon / Spark SQL | エンジンは別 | BigQuery | DuckDB |
| エグレス | ゼロ（最大の差別化） | リージョン外で課金 | コンピュート課金に内包 | 同左 | ストレージ依存 | 同左 | DuckDB側 |
| ストリーミング書込 | Pipelines統合 | Firehose → S3 Tables | Snowpipe Streaming | DLT / Auto Loader | 別途Flink等 | Pub/Sub → BQ | 別途 |
| ガバナンス | 弱（テーブル単位） | IAM + Lake Formation | 強 | 強（業界トップ級） | 中 | 中〜強 | 弱 |
| 価格モデル | R2ストレージ + クエリ従量 | S3 + 各エンジン | Credit | DBU | エンジン依存 | スロット + ストレージ | 月額+クエリ |
| 強み | エグレス無料・Workersスタック統合 | AWSネイティブ統合 | 成熟したDWH機能 | Lakehouse運用ノウハウ | OSS純度 | BQの分析力 | DuckDBの軽量さ |
| 弱み | ベータ・ガバナンス追従途上 | AWSロックイン | 高コスト・クローズド | 高コスト | エンジンは別途必要 | GCPロックイン | スケール上限 |

CloudflareのポジションはS3 Tables（AWS）に最も近いが、「エグレス無料 × Workers / Pipelinesからの直結」という2点で差別化される。Snowflake / Databricks水準のガバナンス・ML統合が要件の中核なら現時点では併用または代替が妥当である。

## 料金

- **R2ストレージ**：標準R2の単価（$0.015/GB/月）＋Class A/B操作。エグレスは引き続き無料。
- **R2 Data Catalog**：パブリックベータ中は追加課金なし。GA時にCatalog API call課金（メタデータ操作単位）が導入される予定。
- **R2 SQL**：オープンベータ中は無料（R2のストレージ・操作費のみ）。GA前に最低30日の予告期間を経て、スキャン量ベースの従量課金に移行予定。
- **Pipelines連携**：Pipelines自体の料金（取込量／処理時間）に従う。Iceberg書き出し自体に追加料金はかからない。

「ベータ中はR2の標準コストだけで回る」のが現状最大のメリットであり、本番採用前にGA価格表の確認とクエリ量見積もりが必須である。

## CLI / API 例

### Catalog作成（Wrangler）
```bash
# R2バケットにData Catalogを有効化
wrangler r2 bucket catalog enable my-lakehouse

# Catalog情報の確認（warehouse URI、エンドポイント、トークン作成手順を表示）
wrangler r2 bucket catalog get my-lakehouse

# Iceberg REST用のAPIトークンを発行（Dashboard or API）
# token は Bearer として各エンジンに渡す
```

### PyIcebergから接続
```python
from pyiceberg.catalog import load_catalog

catalog = load_catalog(
    "r2_catalog",
    **{
        "type": "rest",
        "uri": "https://catalog.cloudflarestorage.com/<account_id>/my-lakehouse",
        "warehouse": "my-lakehouse",
        "token": "<CF_API_TOKEN>",
    },
)

catalog.create_namespace("analytics")
table = catalog.load_table("analytics.events")
df = table.scan(row_filter="event_date = '2026-05-01'").to_pandas()
```

### DuckDBから接続
```sql
INSTALL iceberg;
LOAD iceberg;

ATTACH 'my-lakehouse' AS r2lake (
    TYPE iceberg,
    ENDPOINT 'https://catalog.cloudflarestorage.com/<account_id>/my-lakehouse',
    TOKEN '<CF_API_TOKEN>'
);

SELECT event_type, COUNT(*) AS n
FROM r2lake.analytics.events
WHERE event_date >= DATE '2026-05-01'
GROUP BY event_type
ORDER BY n DESC;
```

### Sparkカタログ設定
```bash
spark-sql \
  --packages org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.5.0 \
  --conf spark.sql.catalog.r2lake=org.apache.iceberg.spark.SparkCatalog \
  --conf spark.sql.catalog.r2lake.type=rest \
  --conf spark.sql.catalog.r2lake.uri=https://catalog.cloudflarestorage.com/<account_id>/my-lakehouse \
  --conf spark.sql.catalog.r2lake.warehouse=my-lakehouse \
  --conf spark.sql.catalog.r2lake.token=<CF_API_TOKEN> \
  --conf spark.sql.catalog.r2lake.io-impl=org.apache.iceberg.aws.s3.S3FileIO \
  --conf spark.sql.catalog.r2lake.s3.endpoint=https://<account_id>.r2.cloudflarestorage.com \
  --conf spark.sql.catalog.r2lake.s3.access-key-id=<R2_ACCESS_KEY> \
  --conf spark.sql.catalog.r2lake.s3.secret-access-key=<R2_SECRET_KEY>
```

### R2 SQLクエリ
```bash
# Wrangler経由で単発クエリ
wrangler r2 sql query my-lakehouse \
  "SELECT event_type, COUNT(*) AS n
     FROM analytics.events
    WHERE event_date >= DATE '2026-05-01'
    GROUP BY event_type
    ORDER BY n DESC
    LIMIT 100"
```

### Pipelines → Iceberg Sink（概念）
```bash
# Pipelineを作成してR2 Data Catalogのテーブルへ書き出す
wrangler pipelines create events-pipeline \
  --sink-type r2-iceberg \
  --catalog my-lakehouse \
  --namespace analytics \
  --table events \
  --partition-by event_date
```

## 制限・注意点
- 2026年5月時点、R2 Data CatalogもR2 SQLもパブリック／オープンベータ。プロダクション本格採用はGAアナウンスとSLA明記を待つのが安全。
- Icebergは現時点でv2仕様準拠。ブランチ／タグなどv3相当機能の実装範囲は今後拡張予定。
- Table maintenance（compaction、スナップショット失効、孤児ファイル削除）の自動化範囲はベータ段階で段階的に拡大中。長期運用では自前監視と必要に応じたSpark `RewriteDataFiles`手動実行が現実解。
- R2 SQLはJDBC/ODBC・BI直結に未対応。Tableau / LookerからはSpark / Trino / DuckDB経由でカタログにつなぐ構成になる。
- 認可粒度はカタログ単位のAPIトークンが基本で、行レベル・列レベルセキュリティはエンジン側（Trino / Sparkのポリシー、Snowflakeのマスキング）で担保する必要がある。
- R2のリージョン特性（Cloudflareのloc-hint指定）はストレージ局所性に効くが、カタログAPI自体はグローバルエンドポイント前提。レイテンシ要件があるなら同居エンジンの配置を検討。
- 同一テーブルをR2 SQLと外部Sparkで並行書込する場合は、Icebergの楽観ロックとリトライ前提で設計する。書込窓口を1本化したほうが運用は楽。

## 参考リンク
- R2 Data Catalog 概要：https://developers.cloudflare.com/r2/data-catalog/
- R2 SQL 概要：https://developers.cloudflare.com/r2-sql/
- R2 ドキュメント：https://developers.cloudflare.com/r2/
- Cloudflare Pipelines：https://developers.cloudflare.com/pipelines/
- Apache Iceberg REST Catalog Spec：https://iceberg.apache.org/spec/
- PyIceberg：https://py.iceberg.apache.org/
- DuckDB Iceberg拡張：https://duckdb.org/docs/extensions/iceberg
- Iceberg Spark Quickstart：https://iceberg.apache.org/docs/latest/spark-getting-started/

---
参照日: 2026-05-04
