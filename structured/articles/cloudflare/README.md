# Cloudflare アーキテクト視点の教科書

Cloudflareの全サービスを「いつ・なぜ採用するか」のアーキテクト判断軸で整理したナレッジ集。
ツールの使い方ではなく **システム構築時の選定肢** として参照することを目的とする。

きっかけ: [Try the cf CLI Local Explorer (Cloudflare Blog)](https://blog.cloudflare.com/cf-cli-local-explorer/)

---

## 全体ガイド

- [00-overview.md](./00-overview.md) — Cloudflareとは何か（Connectivity Cloud思想とエッジネットワーク）
- [01-cli-tools.md](./01-cli-tools.md) — Wrangler / cf CLI / Terraform / Pulumi の使い分け

---

## サービス別ドキュメント

各サービスは以下の共通テンプレで整理:
**一行サマリ / 解決する課題 / 主要機能 / アーキテクト視点 / 競合・代替 / 料金 / CLI例 / 制限 / 参考リンク**

### Tier 1: 開発者プラットフォーム中核（17 / 17 完了）

- [x] [Workers](./tier1-core/workers.md) — エッジサーバーレス
- [x] [Pages](./tier1-core/pages.md) — Jamstack/フルスタックホスティング
- [x] [R2](./tier1-core/r2.md) — エグレス無料の S3 互換オブジェクトストレージ
- [x] [D1](./tier1-core/d1.md) — エッジ SQLite (SQL DB)
- [x] [KV](./tier1-core/kv.md) — 結果整合性の KVS
- [x] [Durable Objects](./tier1-core/durable-objects.md) — グローバル一意性のステートフルオブジェクト
- [x] [Queues](./tier1-core/queues.md) — エグレス無料のメッセージキュー
- [x] [Hyperdrive](./tier1-core/hyperdrive.md) — リージョナル DB の高速アクセラレータ
- [x] [Vectorize](./tier1-core/vectorize.md) — ベクトルデータベース
- [x] [Workflows](./tier1-core/workflows.md) — 耐久性のある複数ステップアプリ
- [x] [Workers AI](./tier1-core/workers-ai.md) — エッジで動く LLM 推論
- [x] [AI Gateway](./tier1-core/ai-gateway.md) — LLM の観測・キャッシュ・レート制御
- [x] [Tunnel](./tier1-core/tunnel.md) — 公開IP不要でオリジン接続
- [x] [Access](./tier1-core/access.md) — ZTNA (Zero Trust ネットワークアクセス)
- [x] [Turnstile](./tier1-core/turnstile.md) — reCAPTCHA 代替
- [x] [Images](./tier1-core/images.md) — 画像変換・配信
- [x] [Stream](./tier1-core/stream.md) — 動画エンコード・配信

### Tier 2: ゼロトラスト / Cloudflare One（6 / 6 完了）

- [x] [Gateway](./tier2-zero-trust/gateway.md) — DNS/HTTP/Network filtering
- [x] [Browser Isolation](./tier2-zero-trust/browser-isolation.md) — Remote Browser Isolation (NVR)
- [x] [Data Loss Prevention (DLP)](./tier2-zero-trust/dlp.md) — 機密情報の検出と統合制御
- [x] [CASB](./tier2-zero-trust/casb.md) — SaaS の API スキャン（設定ミス検出）
- [x] [Email Security](./tier2-zero-trust/email-security.md) — Pre-delivery phishing/BEC 検出（旧 Area 1）
- [x] [Digital Experience Monitoring](./tier2-zero-trust/dex.md) — WARP 由来の合成テスト・Fleet 監視

### Tier 3: ネットワーク / エッジセキュリティ（11 / 11 完了）

- [x] [WAF](./tier3-network-edge/waf.md) — Web Application Firewall（Managed Rules / Custom Rules / OWASP CRS）
- [x] [DDoS Protection](./tier3-network-edge/ddos.md) — 全プラン無制限の L3-L7 自動緩和
- [x] [Bot Management](./tier3-network-edge/bot-management.md) — ML スコアリング / Verified Bots / AI Crawl Control
- [x] [Cache](./tier3-network-edge/cache.md) — Cache Rules / Cache Reserve / Tiered Cache
- [x] [Argo Smart Routing](./tier3-network-edge/argo-smart-routing.md) — リアルタイム遅延計測ベースの最適経路
- [x] [Load Balancing](./tier3-network-edge/load-balancing.md) — GSLB / マルチクラウド active-active
- [x] [Magic Transit / Magic WAN](./tier3-network-edge/magic-transit-wan.md) — L3 SASE と拠点間 SD-WAN
- [x] [Spectrum](./tier3-network-edge/spectrum.md) — 任意 TCP/UDP のリバースプロキシ
- [x] [API Shield](./tier3-network-edge/api-shield.md) — Schema Validation / mTLS / Sequence / BOLA
- [x] [Rate Limiting](./tier3-network-edge/rate-limiting.md) — Advanced Rate Limiting（複合 / ペイロード）
- [x] [Waiting Room](./tier3-network-edge/waiting-room.md) — 仮想待合室（FIFO / Random / Event）

### Tier 4: その他（次回セッション・14件）

- [ ] DNS / DNS Firewall / Internal DNS
- [ ] Registrar
- [ ] Email Routing / Email Service
- [ ] Zaraz
- [ ] Web Analytics / Logs / Log Explorer
- [ ] Radar
- [ ] RealtimeKit / Realtime SFU
- [ ] Containers
- [ ] Sandbox SDK
- [ ] AI Search / AI Crawl Control
- [ ] Secrets Store
- [ ] Workers for Platforms / Cloudflare for SaaS
- [ ] Pipelines
- [ ] R2 Data Catalog / R2 SQL

---

## 使い方

1. 構築したいサービスのアーキテクチャを考える時、`README.md` の Tier 1 から該当用途を探す
2. 「アーキテクト視点：いつ選ぶか」を読み、Cloudflareが適しているか判断する
3. 適していれば「競合・代替」と料金を見て他社サービスと比較

## 更新方針

- 公式ドキュメント (`developers.cloudflare.com`) を一次ソースとする
- 取得は Browser Use CLI 経由
- 料金や制限値は変動するため、参照日を各ファイル末尾に記載
