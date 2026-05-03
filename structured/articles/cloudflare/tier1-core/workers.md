# Workers

## 一行サマリ
Cloudflareのグローバルネットワーク上でJavaScript / TypeScript / Python / Rust等のコードを実行する、コールドスタートを排した V8 isolate ベースのサーバーレス実行基盤。

## 解決する課題（Why）
従来のサーバーレス（AWS LambdaやCloud Functions）は、リージョン固定・コールドスタート遅延・コンテナ起動コスト・egress課金といった構造的な制約を抱える。Workers はリクエストをユーザー最寄りのエッジロケーションで V8 isolate により直接処理することで、ミリ秒級のレイテンシと実質ゼロのコールドスタートを実現する。フロントエンド配信（静的アセット + SSR）からAPI、Cron、AI推論、長時間バッチまでを単一プラットフォームに統合し、データ転送（egress）課金が存在しない点も大きい。

## 主要機能（What）
- V8 isolate による軽量実行（コンテナ不要、コールドスタートなし、起動時間1秒以内）
- グローバルエッジ配信（Cloudflareネットワーク全ロケーションで自動デプロイ）
- 言語サポート: JavaScript / TypeScript / Python / Rust / WebAssembly
- Bindings によるストレージ・サービス連携（KV / R2 / D1 / Durable Objects / Queues / Hyperdrive / Vectorize / Workers AI）
- Static Assets 統合（フロントエンドフレームワーク React / Next / Astro / Svelte / Vue 等のフルスタック対応）
- Cron Triggers / Queue Consumer / Durable Object Alarms による非同期・スケジュール実行
- Service Bindings による Worker 間通信（インターネットを経由しない内部呼び出し）
- 観測性（Workers Logs、Tail Workers、Logpush、DevTools プロファイリング）

## アーキテクト視点：いつ選ぶか

### 適しているシーン
- グローバルに分散したユーザーへ低レイテンシでAPI/SSRを返したい
- コールドスタートが許容できない（決済・認証・チャット等の対話型ワークロード）
- egress量が多く、AWS/GCPのデータ転送コストが収益を圧迫している
- LP/フロントエンド + 軽量API/BFF を1つのデプロイ単位で配信したい
- AI推論（Workers AI）や Vectorize によるRAGをエッジで完結させたい
- Cron / Queue による非同期処理を別サービスを立てずに同居させたい

### 適していないシーン
- CPU時間が長い重い計算（1リクエストあたり5分超のCPU処理が必要）
- 128 MB を超えるメモリを必要とする処理（大規模ML推論、巨大データのインメモリ処理）
- Node.js のフルAPIや任意のネイティブバイナリが必要なケース（互換レイヤはあるが完全ではない）
- レガシーOS依存・特定リージョン固定の規制要件があるワークロード（データ所在地要件はJurisdictional Restrictionsで対応可能だが要設計）
- ステートフルなTCP/UDPの長時間維持が中心（一部はDurable Objects / TCP socket APIで対応可能）

## 競合・代替（AWS / GCP / Azure / OSS）

| プロバイダ | 対抗サービス | 違い |
|---|---|---|
| AWS | Lambda / Lambda@Edge / CloudFront Functions | Lambdaはリージョン固定でコンテナベース、コールドスタートあり。CloudFront FunctionsはCPU・実行時間が極めて短い（1ms / 10KB）。egress課金あり |
| AWS | App Runner / Fargate | 常駐コンテナ。スケール・課金粒度が粗く、エッジ配信ではない |
| GCP | Cloud Functions / Cloud Run | リージョン配置。Cloud Runはコンテナ単位でスケールするがエッジではない |
| Azure | Azure Functions | リージョンベースFaaS。コールドスタートあり |
| Vercel | Edge Functions / Serverless Functions | Edge Functionsは実体としてCloudflare Workers基盤を一部利用。VercelはDX重視、価格は割高傾向 |
| Netlify | Edge Functions | Deno Deploy基盤。ネットワーク・統合機能ともCloudflareより限定的 |
| Deno | Deno Deploy | V8 isolate + エッジ配信で最も思想が近い競合。Cloudflareに比べBindingsエコシステムが小さい |
| OSS | Fastly Compute@Edge | WASMベースのエッジ実行。言語選択の幅は広いがランタイムDXは異なる |

## 料金モデルの要点
- 無料枠: 100,000 リクエスト / 日、CPU時間 10ms / リクエスト、Worker数 100、KV・Hyperdrive 等の基本枠を含む
- Standard プラン（Workers Paid）: 月額 $5 から、リクエスト 1,000万 / 月 + $0.30 / 100万、CPU時間 3,000万 ms / 月 + $0.02 / 100万 ms
- duration（wall-clock 時間）への課金なし（CPU時間のみ課金）。Lambda 等の duration 課金モデルとの最大の差
- egress / bandwidth 課金が一切ない（R2 含めCloudflareの一貫した方針）
- 静的アセットへのリクエストは無料・無制限
- 注意点: CPU時間ベース課金なので、I/O待ちが多いWorkerは安価。逆に重い計算・SSRはCPU時間が膨らみコスト増。Wrangler の `limits.cpu_ms` 設定で denial-of-wallet 対策を必ず入れる

## CLI / IaC 操作例

```bash
# プロジェクト初期化
npm create cloudflare@latest my-worker

# ローカル開発（Miniflare 経由のローカル isolate）
npx wrangler dev

# リモート（実エッジ）でのデバッグ
npx wrangler dev --remote

# デプロイ
npx wrangler deploy

# バンドルサイズ確認（gzip後3MB / 10MB上限）
npx wrangler deploy --outdir bundled/ --dry-run

# 起動時間プロファイル（1秒上限の調査）
npx wrangler check startup
```

`wrangler.jsonc` での CPU 時間上限設定例:

```jsonc
{
  "name": "my-worker",
  "main": "src/index.ts",
  "compatibility_date": "2026-04-01",
  "limits": {
    "cpu_ms": 30000
  },
  "kv_namespaces": [
    { "binding": "MY_KV", "id": "xxxxxxxx" }
  ]
}
```

## 制限・注意点
- CPU時間: Free 10 ms / 呼び出し、Paid 最大 5 分（デフォルト30秒）
- メモリ: 128 MB / isolate（Free・Paid 共通）
- Worker サイズ: gzip後 Free 3 MB / Paid 10 MB（圧縮前 64 MB）
- 起動時間: グローバルスコープのパース・実行は1秒以内（超過すると `error code 10021`）
- サブリクエスト: Free 50 / リクエスト、Paid 1,000（最大1,000万まで設定可）
- 同時接続: 1呼び出しあたり レスポンスヘッダ受信前の接続は最大6本まで
- リクエスト本文サイズ: Free/Pro 100 MB、Business 200 MB、Enterprise 500 MB（Cloudflare アカウントプランに依存）
- ルート: 1 zone あたり 1,000 ルート、カスタムドメイン 100、`wrangler dev --remote` 時は 50 まで
- Worker 数: Free 100 / Paid 500（超過時は Workers for Platforms を検討）
- Static Assets: Worker version あたり Free 20,000 / Paid 100,000 ファイル、1ファイル 25 MiB
- Cron / Queue Consumer / Durable Object Alarm の wall time は 15 分上限
- ログサイズ: 1リクエスト 256 KB（超過分は記録されない）

## 参考リンク
- https://developers.cloudflare.com/workers/
- https://developers.cloudflare.com/workers/platform/limits/
- https://developers.cloudflare.com/workers/platform/pricing/

---
参照日: 2026-05-03
