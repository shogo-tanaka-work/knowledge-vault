# Cloudflareとは — Connectivity Cloud という思想

## 一行サマリ

世界330都市以上に分散した自社ネットワーク上に **「コンピュート / ストレージ / セキュリティ / 接続」を統合提供するクラウド** 。AWS/GCP/Azure とは設計思想が異なり、「ユーザーの一番近くで処理する」前提でスタックが組まれている。

## Cloudflareが「3大クラウド」と違う3点

### 1. リージョンではなく "エッジ" が単位

AWS は `us-east-1` のようにリージョン単位でリソースを配置する。Cloudflare はコードとデータを世界中のデータセンターに自動分散する。「どこにデプロイするか」を考えず、ユーザー最寄りで実行される。

### 2. エグレス料金がほぼゼロ

R2 (オブジェクトストレージ) と Queues はエグレス（外向き転送）料金が無料。これは S3 のエグレス課金から逃れるための強力な選択肢になる。

### 3. CDN/WAF と Compute が地続き

元々 CDN/DDoS 防御の会社なので、Worker (コード) と WAF/Cache が同じレイヤで動く。「リクエストがオリジンに届く前にコードが走る」のが標準。

## 製品ファミリーの俯瞰

```
┌─────────────────────────────────────────────────────────┐
│                   Cloudflare Network                    │
│              （330+都市・Anycast IP・1.1.1.1）            │
└─────────────────────────────────────────────────────────┘
   │
   ├── Developer Platform        ← アプリ構築 (Workers, R2, D1...)
   ├── AI Platform              ← Workers AI, AI Gateway, Vectorize
   ├── Application Services     ← CDN, WAF, DDoS, Bot Management
   ├── Zero Trust (One)         ← Access, Tunnel, Gateway, DLP
   ├── Network Services         ← Magic Transit, Magic WAN, Spectrum
   └── Domain & DNS             ← Registrar, DNS, Email Routing
```

## 「いつCloudflareを第一候補に検討するか」

| 状況 | 推奨理由 |
|------|---------|
| グローバル配信が前提のサービス | エッジ実行・Anycastで標準対応 |
| エグレス料金が痛いストレージ用途 | R2 がエグレス無料 |
| サーバーレスでスタートアップを高速立ち上げ | Workers + Pages + D1/R2 で完結 |
| BtoB SaaS で社内アクセス制御が要る | Access + Tunnel で VPN レス |
| LLM アプリで複数プロバイダ運用 | AI Gateway でキャッシュ・観測一元化 |
| WordPress/既存サイトを高速化 | CDN + APO だけで導入可能 |
| グローバルチームの社内ツール公開 | Tunnel + Access が VPN より楽 |

## 「Cloudflareを第一候補にしない方がよい」典型

- **重い計算 / 長時間バッチ**: Workers の CPU 時間制限（数十ms〜数分）。GPU 集中処理も基本不可（Workers AIで提供される一部モデルのみ）
- **巨大なリレーショナルDB**: D1 は SQLite ベースで規模上限あり。本格 OLTP は Hyperdrive 経由の Postgres などを使う必要がある
- **マルチクラウドの管理面の中心**: IAM / 組織設計の柔軟性は AWS/GCP に劣る
- **特定リージョン縛りの規制対応**: Data Localization Suite はあるが、リージョン固定の純度では純AWSの方が単純

## アーキテクト判断フローチャート（簡易）

```
質問: Webアプリを作る
  ├─ グローバル & 軽量？ → Workers + Pages + R2/D1
  ├─ AIアプリで複数LLM使う？ → 上記 + AI Gateway + Vectorize
  ├─ 既存オリジンのCDN/WAFだけ欲しい？ → Cloudflare 標準プロキシのみ
  └─ 社内ツール公開したい？ → Tunnel + Access (VPN置換)

質問: ストレージを置く
  ├─ オブジェクト / 大量転送あり？ → R2（エグレス無料）
  ├─ KV で十分？ → Workers KV
  ├─ SQL が要る & 軽量？ → D1
  ├─ ステートフルなセッション/同期？ → Durable Objects
  └─ 既存 RDS/Postgres を高速化？ → Hyperdrive

質問: ゼロトラスト導入
  └─ Cloudflare One (Access + Gateway + Tunnel + DLP + CASB)
```

## 参考リンク

- [Cloudflare Products 一覧](https://developers.cloudflare.com/products/)
- [Reference Architectures](https://developers.cloudflare.com/reference-architecture/)
- [Cloudflare Blog](https://blog.cloudflare.com/)

---
参照日: 2026-05-03
