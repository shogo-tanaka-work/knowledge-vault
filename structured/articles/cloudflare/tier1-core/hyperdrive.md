# Hyperdrive

## 一行サマリ
Workersから既存のPostgreSQL/MySQLへのアクセスを高速化する、グローバル接続プーリング+クエリキャッシュサービス。

## 解決する課題（Why）
Cloudflare Workersは300以上のロケーションで稼働するステートレス環境のため、中央集権的な既存DB（RDS等）に接続するたびに以下の問題が発生する。

- 新規TCP/TLS接続の確立に複数ラウンドトリップを要し、遠隔地からだとリクエストごとに数百msのレイテンシが発生する
- ステートレスなWorkerが大量に分散実行されると、DB側の最大コネクション数を即座に枯渇させる
- 同じ読み取りクエリを世界中のリージョンから繰り返し実行すると、オリジンDBに不要な負荷がかかる

Hyperdriveはこの「Workersと既存RDBの相性問題」を、コードを書き換えずに解消するための専用ミドルウェアである。

## 主要機能（What）
- 既存PostgreSQL/MySQLへの接続文字列ベースのプロキシ
- Cloudflareエッジでの接続セットアップ（TLS含む）
- オリジンDB近傍リージョンでの常駐コネクションプール（transaction mode）
- 読み取り（非ミューテーション）クエリの自動キャッシュ（`max_age`設定可能）
- 標準ドライバ（`pg`, `postgres.js`, `mysql2`等）と既存ORMをそのまま利用可能
- Workers Placementとの併用でさらなるレイテンシ削減

## 仕組み（必須セクション）
Hyperdriveは3層構成で動作する。

1. **エッジ接続セットアップ**: Workerからの接続要求をWorkerに最も近いCloudflareエッジで終端。TLSハンドシェイク等のセットアップコストを同一ロケーション内に閉じ込める。
2. **コネクションプーリング**: オリジンDBに近いリージョンに常駐するコネクションプールを保持。Worker→Hyperdriveエッジ→Hyperdriveプール→DB という経路で、既存ウォームコネクションを再利用する。プールはtransaction mode（トランザクション完了で接続返却、`RESET`される）。
3. **クエリキャッシング**: クエリをパースしてSELECT等の読み取りを判定。設定された`max_age`の間、レスポンスをキャッシュし、オリジンDBへの問い合わせ自体を省略する。

Hyperdriveは分散システムなので、クライアントが既存プールに到達できない場合は新規プールが立ち上がる（可用性を優先）。

## アーキテクト視点：いつ選ぶか

### 適しているシーン
- 既存のPostgreSQL/MySQL（RDS, Aurora, Cloud SQL, Neon, Supabase, PlanetScale, CockroachDB, Timescale等）をそのまま使い続けたい
- D1のサイズ上限・トランザクション制約・Postgres互換性不足が壁になっている
- 既存ORM（Prisma, Drizzle, TypeORM等）やSQL資産を捨てずにWorkersへ移行したい
- グローバルにユーザーがいるが、DBは1リージョンに集約したい
- 読み取り偏重ワークロードでDB負荷を下げたい

### 適していないシーン
- そもそも新規プロジェクトでCloudflareに閉じてよい → D1で十分なケースが多い
- 全クエリが書き込み中心でキャッシュ効果が薄く、かつDBが地理的に近い → Hyperdriveのメリットが薄い
- 60秒を超える長時間クエリ・バッチ処理（クエリは強制終了される）
- セッション固定の前提（`SET`を跨いで保持したい等）が必要なアプリ → transaction mode制約と相性が悪い
- DBがCloudflareネットワークから到達できない閉域内（Tunnel等の併用が前提となる）

## 対応DB
- **PostgreSQL系**: PostgreSQL本体、Neon、Supabase、AWS RDS Postgres、Aurora Postgres、Google Cloud SQL Postgres、Azure Database for PostgreSQL、CockroachDB、Timescale等
- **MySQL系**: MySQL本体、PlanetScale、AWS RDS MySQL、Aurora MySQL、Google Cloud SQL MySQL等

ドライバは`postgres.js` / `node-postgres (pg)` / `mysql2`等の標準ライブラリがそのまま動く。Named prepared statementsは`postgres.js`と`node-postgres`が最適。

## 料金モデルの要点
- Workersプランに同梱され、Hyperdrive固有の追加料金は無い
- 接続プーリング・クエリキャッシュ自体に追加課金は発生しない
- データ転送（egress）課金も無い
- Free: 100,000クエリ/日（00:00 UTCリセット）、Paid: 無制限
- 課金カウント対象は「Hyperdrive経由のあらゆるDBステートメント」（SELECT/INSERT/UPDATE/DELETE/DDL、キャッシュHit/Missを問わず同等にカウント）

## CLI / IaC 操作例

設定作成（接続文字列を渡す）。
```bash
npx wrangler hyperdrive create my-hyperdrive \
  --connection-string="postgres://user:password@db.example.com:5432/mydb"
```

`wrangler.jsonc` にバインディング追加。
```jsonc
{
  "name": "my-worker",
  "hyperdrive": [
    {
      "binding": "HYPERDRIVE",
      "id": "<生成されたID>"
    }
  ],
  "placement": {
    "region": "aws:us-east-1"
  }
}
```

Worker側コード（`pg`ドライバ）。
```ts
import { Client } from "pg";

export default {
  async fetch(request, env, ctx): Promise<Response> {
    const client = new Client({
      connectionString: env.HYPERDRIVE.connectionString,
    });
    await client.connect();
    const result = await client.query("SELECT * FROM pg_tables");
    return Response.json(result.rows);
  },
} satisfies ExportedHandler<{ HYPERDRIVE: Hyperdrive }>;
```

## 制限・注意点
- **設定数**: Free 10 / Paid 25（アカウントあたり）
- **オリジンDB接続数**: Free 約20 / Paid 約100（設定あたり）。分散システム特性上、稀に超過する場合あり
- **クエリ最大実行時間**: 60秒（超過は強制終了）
- **キャッシュ対象レスポンス上限**: 50MB（超えるものはキャッシュされないがWorkerには返る）
- **初期接続タイムアウト**: 15秒、**アイドル接続タイムアウト**: 10分
- **Pooling mode**: transaction modeのみ。`SET`はトランザクション/単一クエリ内に閉じる。複数クエリで状態を保持するために長時間トランザクションを張るのは反パターン（プール再利用性を損なう）
- **Named prepared statements**: 一部ドライバでは未対応・性能劣化あり
- 接続枯渇エラー（`Failed to acquire a connection from the pool`）は長時間クエリ/トランザクションが主因。クエリの短縮で対処する

## 参考リンク
- 概要: https://developers.cloudflare.com/hyperdrive/
- 仕組み: https://developers.cloudflare.com/hyperdrive/concepts/how-hyperdrive-works/
- Limits: https://developers.cloudflare.com/hyperdrive/platform/limits/
- Pricing: https://developers.cloudflare.com/hyperdrive/platform/pricing/

---
参照日: 2026-05-03
