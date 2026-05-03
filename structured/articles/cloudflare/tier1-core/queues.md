# Queues

## 一行サマリ
Cloudflare Queues は Workers と統合された、エグレス料金ゼロのグローバル分散メッセージキューである。

## 解決する課題（Why）
- Worker 間や外部システムとの非同期処理を、配信保証付きで実現する必要がある。
- 既存クラウドのキュー（SQS / Pub/Sub）は egress 料金とリージョン固定が運用コストを押し上げる。
- リクエスト処理から重い後段処理を切り離し、ピーク吸収・バッチ化・リトライを統一的に扱いたい。
- Cloudflare Workers / R2 / D1 とゼロ設定で連携する非同期基盤がほしい。

## 主要機能（What）
- **Producer**: Worker から `env.MY_QUEUE.send(msg)` / `sendBatch([...])` で投入。最大 256KB / バッチ。
- **Consumer (Push)**: バインドした Worker が自動起動。バッチ最大 100 件、待機時間最大 60 秒で受信。
- **Consumer (Pull)**: Cloudflare 外のインフラから HTTP REST で pull 可能。`visibilityTimeout` は最大 12 時間。
- **Dead Letter Queue (DLQ)**: 最大リトライ超過のメッセージを別キューに転送。
- **Batching / Retries / Delays**: バッチサイズ・待機時間・遅延配信（最大 24 時間）・リトライ回数（最大 100）を設定可能。
- **Message Retention**: 既定 4 日、最大 14 日（Free プランは 24 時間固定）。
- **Event Subscriptions**: R2 などの Cloudflare イベントをキューにルーティング。
- **Observability**: Wrangler / ダッシュボードからバックログ・スループット監視。

## アーキテクト視点：いつ選ぶか

### 適しているシーン
- Cloudflare Workers / R2 / D1 を中核に据えた非同期処理基盤。
- ファンアウトせず、producer → queue → consumer の単純な疎結合化を求めるユースケース。
- エグレス料金を回避したいクロスリージョン / マルチクラウド連携（pull consumer で外部から取得）。
- バッチ処理に向く ETL、Webhook 受け取り、メール送信、画像処理ジョブなど。
- スパイク吸収バッファ（5,000 msg/sec/queue まで）。

### 適していないシーン
- ミリ秒レイテンシ・厳密な順序保証（FIFO）が必須なケース。Queues は順序保証を明示しない。
- 1キューあたり 5,000 msg/sec を超える超高スループット要件 → Kafka 系。
- Pub/Sub 型のファンアウト配信（1 メッセージを N consumer に同報）→ 単独では非対応。
- 128KB 超のペイロード（R2 へオフロードして参照を流す設計が必要）。
- Cloudflare 外で完結する純粋オンプレ構成（メリット薄）。

## 競合・代替（SQS / Pub/Sub / SNS / Kafka / RabbitMQ）

| 観点 | Cloudflare Queues | AWS SQS | GCP Pub/Sub | Apache Kafka |
|---|---|---|---|---|
| エグレス料金 | 無料 | リージョン外で発生 | リージョン外で発生 | 自前運用次第 |
| スループット上限 | 5,000 msg/sec/queue | ほぼ無制限（Standard） | 数百万 msg/sec | 数百万 msg/sec |
| 配信保証 | At-least-once | At-least-once（FIFO は exactly-once） | At-least-once | At-least-once / exactly-once |
| 順序 | 保証なし | FIFO キューあり | 順序キーで保証 | パーティション内で保証 |
| 課金単位 | 64KB 単位の operation | リクエスト数 + データ転送 | データ量 + 操作 | 自前 / Confluent 従量 |
| 適性 | Workers 統合・低コスト非同期 | AWS 中心の汎用キュー | GCP 中心ファンアウト | 大規模ストリーミング |

## 料金モデルの要点
- **課金単位**: 64KB ごとに 1 operation。write / read / delete それぞれカウント。
- **Free プラン**: 10,000 ops/日、保持 24 時間固定。
- **Paid プラン**: 1,000,000 ops/月まで無料、超過分 $0.40 / 100 万 ops。
- **エグレス料金 / 帯域料金は一切なし**。
- 標準的なメッセージ処理は 1 件あたり 3 ops（write + read + delete）。
- リトライは追加 read を消費。DLQ 送りは追加 write を消費。
- 概算式: `((メッセージ数 * 3) - 1,000,000) / 1,000,000 * $0.40`。
- 例: 1日100万件・30日 → 月 $35.60。127KB×1億件/月 → 月 $239.60。

## CLI / IaC 操作例

キュー作成と Worker バインド。

```bash
# キュー作成
npx wrangler queues create my-queue

# DLQ 作成
npx wrangler queues create my-queue-dlq

# コンシューマ設定
npx wrangler queues consumer add my-queue my-worker
```

`wrangler.jsonc` 設定例。

```jsonc
{
  "name": "my-worker",
  "main": "src/index.ts",
  "compatibility_date": "2026-04-01",
  "queues": {
    "producers": [
      { "binding": "MY_QUEUE", "queue": "my-queue" }
    ],
    "consumers": [
      {
        "queue": "my-queue",
        "max_batch_size": 10,
        "max_batch_timeout": 5,
        "max_retries": 3,
        "dead_letter_queue": "my-queue-dlq"
      }
    ]
  },
  "limits": { "cpu_ms": 300000 }
}
```

Worker コード例。

```typescript
export default {
  // Producer（HTTP リクエストハンドラ）
  async fetch(req: Request, env: Env) {
    await env.MY_QUEUE.send({ userId: "u_123", action: "signup" });
    return new Response("queued");
  },

  // Consumer（push型）
  async queue(batch: MessageBatch, env: Env) {
    for (const msg of batch.messages) {
      try {
        await processMessage(msg.body);
        msg.ack();
      } catch (e) {
        msg.retry({ delaySeconds: 30 });
      }
    }
  }
};
```

## 制限・注意点
- **メッセージサイズ**: 128KB 上限。超過時は R2 にオフロードしポインタを送る設計に切り替える。
- **per-queue スループット**: 5,000 msg/sec。超過時は `Too Many Requests` で send が失敗する。
- **保存期間**: 最大 14 日（Free は 24 時間固定）。期限切れメッセージは自動削除され、課金は write + delete のみ。
- **バックログ上限**: キューあたり 25GB。超過すると `Storage Limit Exceeded`。
- **同時 consumer 起動**: push 型で 250 並列。
- **CPU 時間**: consumer Worker は既定 30 秒、最大 5 分まで `cpu_ms` で拡張可能。Wall time は 15 分上限。
- **順序保証なし**: 順序が要件ならアプリ側でシーケンス管理が必要。
- **pull consumer**: `visibilityTimeout` 最大 12 時間。明示的 ack/retry を忘れると再配信される。
- **アカウント上限**: 1 アカウントあたり 10,000 キュー。
- メッセージあたり約 100 バイトの内部メタデータがサイズに加算される。

## 参考リンク
- [Cloudflare Queues 公式ドキュメント](https://developers.cloudflare.com/queues/)
- [Limits](https://developers.cloudflare.com/queues/platform/limits/)
- [Pricing](https://developers.cloudflare.com/queues/platform/pricing/)
- [JavaScript APIs](https://developers.cloudflare.com/queues/configuration/javascript-apis/)
- [Dead Letter Queues](https://developers.cloudflare.com/queues/configuration/dead-letter-queues/)
- [Pull Consumers](https://developers.cloudflare.com/queues/configuration/pull-consumers/)

---
参照日: 2026-05-03
