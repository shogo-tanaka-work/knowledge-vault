# Pipelines

## 一行サマリ
HTTPまたはWorkers binding経由で受け取ったイベントストリームを、SQLで検証・変換・整形し、Apache Iceberg / Parquet / JSON としてR2に書き出すCloudflare内で完結する Streaming ETL である。

## 解決する課題（Why）
Webアプリのクリックストリーム、Workers内で発生するカスタムイベント、IoTテレメトリ、モバイルSDKのイベントログを「とりあえず溜めて、あとで分析する」要件は、これまで Kafka + Kafka Connect + Spark Structured Streaming + AWS Glue + S3 + Athena といった多段スタックで実現されてきた。これは小さなチームには明らかに過剰投資であり、運用の足を引っ張る。Cloudflare Pipelines はこれを以下の点で解消する。

- Workers / Pages / R2 と同じCloudflareアカウント内でストリーミングETLが完結し、外部のメッセージブローカー・実行基盤・スキーマレジストリを持ち込まなくてよい。
- HTTPエンドポイントとWorkers bindingの両方で取り込みが可能で、エッジで生成したイベントをそのまま受け流せる（egressコストなし）。
- 出力をR2上のApache Icebergテーブルにできるため、R2 Data Catalog経由でDuckDB / Spark / Trino / Snowflake から直接クエリでき、別途データウェアハウスへのコピーが不要になる。
- Logpushが「Cloudflare自身が生成する既知のログ（HTTP / WAF / Gateway 等）を宛先に流す」だけなのに対し、Pipelines は「アプリ側で定義したカスタムイベントをスキーマ付きでETLする」用途に応える。両者は補完関係にある。

## 主要機能（What）

### Sources（取り込み）
イベントを受け付ける入口層は2系統である。

- **HTTP Ingest**：`https://{stream-id}.ingest.cloudflare.com` に JSON 配列をPOSTする。モバイルアプリ・SaaSのWebhook・ブラウザ計測タグなど、Cloudflare外部のクライアントから直接送信できる。認証トークン付きで保護する。
- **Workers Binding**：`wrangler.toml` に pipeline binding を設定し、Worker から `env.MY_PIPELINE.send([...])` の形でイベントを投げる。エッジで動く Worker と同一データセンター内でingestされるため、レイテンシ・コストともに最小になる。

両方とも内部的には Stream（耐障害バッファ付きキュー）に書き込まれ、Pipelinesがそこからpullする。

### Transforms（SQL変換）
Streams と Sinks の間に SQL ベースの変換ステージが入る。Pipelines は ingest 時点で以下を担う。

- **Validation**：スキーマに合わない・必須フィールド欠損のレコードを弾く。
- **Filter**：`WHERE event_type IN ('purchase', 'signup')` のような絞り込み。
- **Transform / Enrich**：型変換、文字列加工、`headers` から国コードを抽出、UTC変換など。
- **Projection**：出力先テーブルに必要なカラムだけ残す。

「ingest時に一度SQLを通して整える」設計のため、後段のクエリ側で重い ETL を組まなくて済む。

### Sinks（書き出し先）
出力先は R2 の3形態が選べる。

- **Apache Iceberg（R2 Data Catalog）**：R2 Data Catalog にIcebergテーブルとして登録される。スキーマ進化・タイムトラベル・partition pruning が効き、Spark / Trino / DuckDB / Snowflake からそのまま参照可能。
- **Parquet on R2**：列指向圧縮ファイルとして書き出す。R2上を直接 DuckDB やAthena互換ツールでクエリする運用に向く。
- **JSON on R2**：人間が読める形式で残したいログ・デバッグ用途、後段でJSON Linesをそのまま処理したいケース向け。

### Schema
`schema.json` でフィールド定義を持つ。型は `string` / `int64` / `float64` / `bool` / `timestamp` 等。`required: true` のフィールドが欠けたレコードは取り込み時に弾かれる。スキーマを与えることで Parquet / Iceberg 出力の列型が確定し、後段クエリの安定性が確保される。

```json
{
  "fields": [
    {"name": "user_id",    "type": "string",    "required": true},
    {"name": "event_type", "type": "string",    "required": true},
    {"name": "ts",         "type": "timestamp", "required": true},
    {"name": "amount",     "type": "float64",   "required": false}
  ]
}
```

### Batching
Pipelinesはイベントを単発で書き出さず、時間窓またはサイズ窓でバッチを束ねてから R2 オブジェクトとして書き出す。これにより R2 のClass A操作回数を抑え、Parquetの圧縮効率を高めている。バッチ間隔・最大サイズはsink設定で調整する。

### Partitioning
Iceberg / Parquet 出力には partition キー（`event_date` / `region` / `event_type` など）を指定でき、後段のクエリで partition pruning が効くようになる。時間ベース（hourly / daily）と任意カラムの両方が選べる。カラム値のカーディナリティが高すぎると小ファイルが乱立するため設計時に注意する。

## アーキテクト視点：いつ選ぶか

### 適しているシーン
- Workers / Pages 中心のアプリで、ユーザーアクション・APIリクエスト・ビジネスイベントを構造化ログとして蓄積したい場合。
- モバイルアプリ・ブラウザSDKからのクリックストリームを安価に R2 / Iceberg に流し込み、DuckDB や Snowflake で後追い分析したい場合。
- 既存の Kafka + Spark + Glue 構成が「小さなSaaSにはオーバースペック」になっており、Cloudflare 1社で完結する代替を探している場合。
- Logpush では取れない「アプリ側のドメインイベント（注文確定 / 解約 / 支払い失敗 等）」をスキーマ付きで残したい場合。
- R2 Data Catalog のIcebergテーブルを Snowflake / Trino から外部テーブルとして参照する Lakehouse 構成を組みたい場合。

### 適していないシーン
- Kafka topic に既存システム群が密結合しており、Cloudflareアカウント外のproducer / consumer が大量にいるケース。Pipelinesは単独のメッセージブローカーとしての互換性を提供しない。
- 複数の異種ソース（オンプレDB CDC、SaaS API、IoT MQTT 等）を取り込んで複雑な join / window集計を行うフルスペックの Streaming ETL。Flink / Dataflow / Materialize の領域である。
- 5MB/s（ストリーム単位）を恒常的に超える高スループットなテレメトリ。現在のbeta制限を超えるためEnterprise相談が必要。
- 厳密な exactly-once セマンティクスや低レイテンシ（秒未満）の集計が業務要件に含まれるケース。Pipelinesはバッチ書き出し前提でデザインされている。
- Cloudflareエッジを使っていない既存スタック（AWS / GCP内で完結）にわざわざ持ち込むケース。egress導線が増えるだけで利点が薄い。

## 競合・代替

| 観点 | Cloudflare Pipelines | AWS Kinesis Firehose | GCP Dataflow | Confluent Kafka | Estuary Flow | Materialize | Tinybird |
|---|---|---|---|---|---|---|---|
| 出自 | Cloudflare R2 / Workers連携 | AWS純正サーバーレスdelivery | GCP純正Apache Beamマネージド | Kafka商用ディストリビューション | Streaming ETL SaaS（Gazette由来） | Streaming SQL DB（Materialize Inc） | リアルタイム分析API（Tinybird） |
| Sources | HTTP / Workers binding | Kinesis Streams / DirectPut / MSK | Pub/Sub / Kafka / Files / etc. | producer SDK 多数 | DB CDC / SaaS / Kafka | Kafka / Postgres / Webhook | Kafka / HTTP / S3 |
| Sinks | R2（Iceberg / Parquet / JSON） | S3 / Redshift / OpenSearch / Splunk | BigQuery / GCS / Pub/Sub | Sink Connector多数 | Snowflake / BigQuery / S3 / Iceberg | Materialized View（自身がDB） | API endpoint（HTTP） |
| 変換 | SQL（ingest時） | Lambda / 動的partition | Apache Beam（Java/Python） | ksqlDB / Kafka Streams | TypeScript / SQL | SQL（incremental view maintenance） | SQL（pipe） |
| Iceberg | ネイティブ（R2 Data Catalog） | S3 Tables 経由で対応 | BigQuery Iceberg連携 | Tableflow（Iceberg化） | ネイティブ | 直接出力なし | 直接出力なし |
| 料金モデル | beta無料 + R2課金 | データ量課金 + 変換課金 | vCPU時間 + データ | クラスタ + Cloud契約 | 接続数 + データ量 | レプリカ時間課金 | データ量 + APIリクエスト |
| 得意領域 | Cloudflare内エッジイベント収集 | AWS内ログdelivery | 重ETL / 機械学習前処理 | エンタープライズ汎用ストリーミング | DB CDC中心のELT | リアルタイム集計クエリ | リアルタイムAPI公開 |
| 弱み | beta / 高スループット未対応 / 多種ソース弱い | 変換は Lambda 必須 | 学習コストと運用が重い | 自前運用負荷・コスト | Cloudflareエッジとは独立 | データ取り込みは別途必要 | ストレージは内部固定 |

Cloudflare Pipelines のポジションは「Cloudflareエッジで生成・受信したイベントを、最短経路でR2 Iceberg化する」一点に特化している。AWS / GCP内で完結するワークロードには Firehose / Dataflow が、汎用ストリーミングインフラには Kafka / Confluent が、リアルタイム集計には Materialize / Tinybird がそれぞれ妥当である。

## 料金
- **オープンベータ中**：Pipelines 自体の処理は無料。Workers Paid プラン（$5/月〜）への加入が前提。
- **R2課金**：書き出し先としてのR2のストレージ容量・Class A操作（PUT等）は通常通り課金される。バッチサイズが小さすぎるとClass A操作が増えるため、partitionとbatch間隔の設計でコストを抑える。
- **GA後（予定）**：「ingestされたデータ量・transform処理量・sinkへのdelivery量」に基づく従量課金が予告されている。料金体系変更前に30日以上の事前通知が約束されている。
- **egressなし**：R2のegress無料はそのまま効くため、Snowflake / 外部DuckDBから読み出してもegress課金は発生しない。これがS3 Tablesに対する明確な経済的優位点である。

## CLI / API 例

### Pipeline をセットアップ
```bash
# 対話モードでstream / pipeline / sink を一括作成
npx wrangler pipelines setup --name ecommerce-events

# スキーマファイルを与えて作成
npx wrangler pipelines setup --name ecommerce-events --schema ./schema.json
```

### HTTP Ingest（外部クライアントから）
```bash
curl -X POST https://{stream-id}.ingest.cloudflare.com \
  -H "Authorization: Bearer ${PIPELINE_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '[
    {"user_id":"u_001","event_type":"purchase","ts":"2026-05-04T10:00:00Z","amount":29.9},
    {"user_id":"u_002","event_type":"signup",  "ts":"2026-05-04T10:00:01Z"}
  ]'
```

### Workers Binding 経由
```toml
# wrangler.toml
[[pipelines]]
binding  = "EVENTS"
pipeline = "ecommerce-events"
```

```typescript
// src/index.ts
export default {
  async fetch(req: Request, env: Env): Promise<Response> {
    const body = await req.json<{ user_id: string; event_type: string }>();
    await env.EVENTS.send([
      {
        user_id:    body.user_id,
        event_type: body.event_type,
        ts:         new Date().toISOString(),
      },
    ]);
    return new Response("ok");
  },
} satisfies ExportedHandler<Env>;
```

### スキーマ定義
```json
{
  "fields": [
    {"name": "user_id",    "type": "string",    "required": true},
    {"name": "event_type", "type": "string",    "required": true},
    {"name": "ts",         "type": "timestamp", "required": true},
    {"name": "amount",     "type": "float64",   "required": false}
  ]
}
```

### Iceberg テーブルをDuckDBで読む
```sql
-- R2 Data Catalog の Iceberg REST 経由
INSTALL iceberg;
LOAD iceberg;
ATTACH 'r2-catalog' AS catalog (TYPE ICEBERG, ENDPOINT '...');
SELECT event_type, COUNT(*)
FROM catalog.events.ecommerce
WHERE event_date = DATE '2026-05-04'
GROUP BY 1;
```

## 制限・注意点
- **オープンベータ**である。SLAは未保証で、本番のミッションクリティカル用途は GA を待つ判断が無難。
- ベータ時点の制限：1アカウントあたり stream / pipeline / sink 各 **20個**、ingestリクエストの最大ペイロード **5MB**、stream あたり最大ingestレート **5MB/s**。これを超えるユースケースは制限緩和申請が必要。
- **Workers Paid プラン必須**：Free planではPipelinesを利用できない。
- **リージョン**：Cloudflareのグローバルネットワーク上で動作するため明示的なリージョン指定はないが、R2バケットのlocation hint（WNAM / EEUR / APAC等）に依存する点に注意。データレジデンシー要件があるなら R2 Jurisdictional buckets と組合せる。
- **batch / partition 設計**：partitionキーのカーディナリティが高すぎると小ファイルが乱立し、R2のClass A操作課金とクエリ性能の両方を悪化させる。日次partition + 必要に応じて事業ドメインで分ける程度に留めるのが定石。
- **Logpushとの役割分担**：Cloudflare自身が出すHTTP / WAF / Gateway / Workers Trace等の既知ログは Logpush で R2 / S3 / Splunk に流す。Pipelines は「アプリ側で定義したカスタムイベント」専用と切り分けると運用が破綻しない。両者を一元化したい場合は Logpush先をR2にしてIceberg化する／Pipelinesに集約する／の二択になるが、現状は素直に併用するのが扱いやすい。
- **exactly-once は保証されない**：at-least-once 前提で、後段クエリ側で `(user_id, event_id)` 等の自然キーでdedupする設計を入れておく。
- **Schema変更**：フィールド追加は前方互換だが、型変更・必須化はIcebergテーブルのスキーマ進化ルールに従う。リリース前に検証必須。

## 参考リンク
- Cloudflare Pipelines トップ：https://developers.cloudflare.com/pipelines/
- Getting started：https://developers.cloudflare.com/pipelines/getting-started/
- 仕組み（How Pipelines work）：https://developers.cloudflare.com/pipelines/concepts/how-pipelines-work/
- Limits：https://developers.cloudflare.com/pipelines/platform/limits/
- Pricing：https://developers.cloudflare.com/pipelines/platform/pricing/
- R2 Data Catalog：https://developers.cloudflare.com/r2/data-catalog/
- Logpush（比較対象）：https://developers.cloudflare.com/logs/logpush/
- Workers Pipelines binding：https://developers.cloudflare.com/workers/runtime-apis/bindings/

---
参照日: 2026-05-04
