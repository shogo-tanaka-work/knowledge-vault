---
title: "Google Ads APIをAIに直接つなぐ — Cloudflare WorkersでリモートMCPサーバーを構築した話"
status: archived
media: note
series: "Google広告 x MCP 実践ガイド"
series_order: 0
created: 2026-01-14
updated: 2026-04-05
source_project: MCPServer/mcp-google-ads-remote
note: "初期ドラフト。01-03の3記事に分割・再構成済み"
published_url: ""
---

# Google Ads APIをAIに直接つなぐ — Cloudflare WorkersでリモートMCPサーバーを構築した話

## はじめに

<!-- TODO: 詳細執筆 -->

- MCPとは何か: AIモデルが外部ツール・データソースにアクセスするための標準プロトコル
- ローカルMCP vs リモートMCP: ローカルはPC上でプロセスとして動作、リモートはHTTP経由でどこからでも接続可能
- 動機: Google Ads の運用データをClaude / Cursorから直接確認・分析したかった
- ローカルMCPサーバー（Python版）は既にあったが、チーム共有やマルチデバイス利用のためにリモート化を決意
- この記事で扱うこと: Cloudflare Workers上にリモートMCPサーバーを構築し、Google Ads APIと接続するまでの全体像

---

## アーキテクチャ概要

<!-- TODO: 詳細執筆 -->

### 全体構成

```
MCPクライアント                    Cloudflare Workers                Google
(Claude Desktop /            ┌─────────────────────────┐
 Cursor / etc.)              │  Hono App               │
        │                    │  ├─ JWT認証ミドルウェア   │
        │  Streamable HTTP   │  ├─ /mcp エンドポイント  │──→ Google Ads API
        └───────────────────→│  │   └─ MCPサーバー      │      (REST v23)
           (Bearer JWT)      │  │       └─ 9ツール      │
                             │  └─ /sse エンドポイント  │──→ Google OAuth2
                             └─────────────────────────┘      (トークン更新)
```

### 技術スタック

- **ランタイム**: Cloudflare Workers（Edge Runtime）
- **フレームワーク**: Hono v4.6
- **MCPライブラリ**: `@modelcontextprotocol/sdk` v1.0 + `@hono/mcp` v0.1（StreamableHTTPTransport）
- **認証**: `hono/jwt`（JWTベアラートークン + ソルト検証）
- **バリデーション**: Zod v3.24
- **言語**: TypeScript 5.7
- **デプロイ**: Wrangler v3.99

### 提供するMCPツール（9種）

| ツール名 | 機能 |
|---------|------|
| `list_accounts` | アクセス可能なアカウント一覧 |
| `execute_gaql_query` | 任意のGAQLクエリ実行 |
| `get_campaign_performance` | キャンペーンパフォーマンス取得 |
| `get_ad_performance` | 広告パフォーマンス取得 |
| `run_gaql` | フォーマット指定付きGAQL実行（table/json/csv） |
| `get_ad_creatives` | 広告クリエイティブ詳細取得 |
| `get_account_currency` | アカウント通貨コード取得 |
| `get_image_assets` | 画像アセット一覧取得 |
| `check_token_validity` | アクセストークンの有効性確認 |

---

## プラットフォーム選定理由

リモートMCPサーバーをどこにホスティングするか。選択肢として **Cloudflare Workers**、**Vercel（Serverless Functions）**、**Render** の3つを検討し、最終的にCloudflare Workersを選択した。この判断に至った理由を詳しく書く。

### 最大の分岐点: SSEストリーミングと実行時間

MCPプロトコルは **Streamable HTTP** というトランスポートを使い、サーバーからクライアントへのレスポンスをHTTPストリーミング（SSE: Server-Sent Events）で返す。このストリーミング接続が維持される時間が、プラットフォーム選定における最大の分岐点になった。

**Vercel** のServerless Functionsにはレスポンスタイムアウトがある。Hobbyプランで10秒、Proプランでも60秒が上限だ。MCPのセッションでは、ユーザーがAIと対話しながらツールを呼び出すため、1つのセッションがこの制限を超えることは十分にありうる。ストリーミングレスポンス自体はVercelでも技術的に可能だが、この時間制限がボトルネックになる。

**Render** は通常のHTTPサーバーとして動作するため、SSEのストリーミングに技術的な制約はない。ただし、無料プランではサーバーが15分間リクエストがないとスリープし、次のリクエスト時にコールドスタートが発生する。MCPクライアントからの初回接続に数十秒かかるのは、体験として致命的だ。

**Cloudflare Workers** はリクエスト単位で起動するエッジ関数だが、ストリーミングレスポンスに対応しており、実行時間の制約が他のサーバーレスプラットフォームと比べて柔軟だ。レスポンスを返し始めてからの持続時間には寛容で、MCPのユースケースに適している。

### ステートレス設計との親和性

今回のMCPサーバーは、リクエストごとに `McpServer` インスタンスと `StreamableHTTPTransport` を新規生成するステートレス設計を採用している。

```typescript
app.all('/mcp', async (c) => {
  // リクエストごとにMCPサーバーとトランスポートを作成
  // （Cloudflare Workersはステートレスなため）
  const mcpServer = createMcpServer(c.env);
  const transport = new StreamableHTTPTransport();
  await mcpServer.connect(transport);
  return transport.handleRequest(c);
});
```

このパターンはCloudflare Workersの実行モデルと完璧に一致する。Workersはリクエストごとに独立した実行コンテキストを持ち、グローバル状態を共有しない。つまり「ステートレスに設計せざるを得ない」制約が、逆にアーキテクチャの健全性を担保してくれる。

Renderのように常時起動するサーバーでは、インスタンスの生存管理やメモリリークへの配慮が必要になる。Workersならそもそもその心配がない。

### コールドスタートの速さ

MCPクライアント（Claude DesktopやCursor）がサーバーに接続する際、レスポンスの速さは体験に直結する。

Cloudflare Workersはエッジロケーション上で実行されるため、コールドスタートはほぼゼロに近い。世界中に分散されたエッジから最も近いポイントで処理されるため、レイテンシも低い。

Renderの無料プランではスリープからの復帰に10〜30秒かかることがあり、MCPの接続タイムアウトに引っかかる可能性がある。Vercelもコールドスタートが存在するが、Renderほど深刻ではない。

### コスト: 個人利用なら無料枠で十分

| プラットフォーム | 無料枠 | 課金モデル |
|:---|:---|:---|
| Cloudflare Workers | **10万リクエスト/日** | リクエスト単位 |
| Vercel | 100GB-hrs/月 | 実行時間ベース |
| Render | 750時間/月（スリープあり） | 常時起動時間ベース |

MCPサーバーの利用パターンは「1日に数十〜数百リクエスト」程度だ。Cloudflare Workersの10万リクエスト/日という無料枠は、個人〜小規模チームの利用であれば全く問題にならない。

Renderは750時間/月の無料枠があるが、常時起動しているとすぐに使い切る。スリープを許容すればコスト内に収まるが、前述のコールドスタート問題が生じる。

### Hono + @hono/mcp エコシステム

技術選定において見逃せないのが、**HonoフレームワークとそのMCPアダプターがCloudflare Workers向けに最適化されている**点だ。

Honoの作者はCloudflareに所属しており、Cloudflare Workers上での動作が最も安定している。`@hono/mcp` が提供する `StreamableHTTPTransport` も、Workers上での動作を前提に設計されている。

```json
{
  "dependencies": {
    "@hono/mcp": "^0.1.0",
    "@modelcontextprotocol/sdk": "^1.0.0",
    "hono": "^4.6.0",
    "zod": "^3.24.0"
  }
}
```

依存パッケージは4つだけ。Honoの軽量さがWorkersの制約（バンドルサイズ制限）とも好相性だ。

### Secrets管理の手軽さ

Google Ads APIとの連携には、以下の機密情報を管理する必要がある:

- Google Ads Developer Token
- OAuth2 Client ID / Client Secret / Refresh Token
- JWT Secret / Salt

Cloudflare Workersでは `wrangler secret put` コマンドで安全にシークレットを登録でき、コード上では `c.env.GOOGLE_ADS_CLIENT_ID` のようにアクセスできる。追加のシークレット管理サービスは不要だ。

これはVercelやRenderでも環境変数として設定可能なので大きな差別化要因ではないが、Wranglerの `secret put` はCLIから直接設定でき、ダッシュボードを開く必要がない点が開発体験として良い。

### 比較まとめ

| 要件 | Cloudflare Workers | Vercel | Render |
|:---|:---:|:---:|:---:|
| SSEストリーミング | **○** | △（時間制限） | ○ |
| コールドスタート | **ほぼなし** | あり | 大きい（Free） |
| 課金モデル | **リクエスト単位** | 実行時間 | 常時起動 |
| 無料枠 | **10万req/日** | 100GB-hrs/月 | 750hrs/月 |
| デプロイ | `npm run deploy` | Git連携 | Git連携 |
| エコシステム | **Hono最適化** | Next.js向き | 汎用 |

### 結論

リモートMCPサーバーのホスティングには **Cloudflare Workersが現時点での最適解** だと考えている。理由をまとめると:

1. **SSE/ストリーミングを実行時間制限なくサポート** — MCPプロトコルの要件を満たす
2. **コールドスタートがほぼゼロ** — MCPクライアントからの接続が即座に確立する
3. **個人利用なら無料枠で十分** — 10万リクエスト/日はMCP用途では使い切れない
4. **Hono + @hono/mcp がWorkers向けに最適化** — 最も安定したランタイム上で動作する
5. **ステートレスモデルが設計を強制する** — アーキテクチャの健全性を自然に担保

特に「Honoエコシステムとの親和性」は大きい。`@hono/mcp` の `StreamableHTTPTransport` を使えば、数十行のコードでMCPプロトコル対応のHTTPサーバーが構築できる。この開発効率は他のプラットフォームでは得られない。

---

## 実装のポイント

<!-- TODO: 詳細執筆 -->

### Hono + @hono/mcp によるMCPサーバー構築

- `McpServer`（`@modelcontextprotocol/sdk`）でツール定義、`StreamableHTTPTransport`（`@hono/mcp`）でHTTPトランスポートを提供
- リクエストごとにサーバーインスタンスを生成するステートレスパターン
- Zodスキーマでツールのパラメータを型安全にバリデーション
- `/mcp` エンドポイント1つで `app.all()` により全HTTPメソッドを受け付ける設計

### JWT認証

- `hono/jwt` ミドルウェアで `/mcp` と `/sse` エンドポイントを保護
- JWT署名検証に加え、ペイロード内の `salt` フィールドを `JWT_SALT` 環境変数と照合する二重チェック
- CORS設定により、リモートMCPクライアントからのクロスオリジンリクエストを許可

### Google Ads API連携

- OAuthリフレッシュトークンからアクセストークンを自動取得・キャッシュ（有効期限5分前に更新）
- Google Ads API v23を使用（`wrangler.toml` の `API_VERSION` で管理）
- GAQL（Google Ads Query Language）でデータ取得、table/json/csv形式で出力可能
- `login-customer-id` ヘッダーによるMCCアカウント経由のアクセスに対応

---

## デプロイと運用

<!-- TODO: 詳細執筆 -->

### セットアップ手順

1. リポジトリをクローン
2. `npm install` で依存パッケージをインストール
3. `wrangler secret put` で6つのシークレットを設定:
   - `GOOGLE_ADS_DEVELOPER_TOKEN`
   - `GOOGLE_ADS_CLIENT_ID`
   - `GOOGLE_ADS_CLIENT_SECRET`
   - `GOOGLE_ADS_REFRESH_TOKEN`
   - `JWT_SECRET`
   - `JWT_SALT`
4. `npm run deploy` でCloudflare Workersにデプロイ

### MCPクライアントからの接続

- **Claude Desktop**: `mcp-remote` プロキシを使用してStreamable HTTP接続
- **Cursor**: MCP設定画面でURL + Authorizationヘッダーを指定

### トークン管理

- Google Ads APIのリフレッシュトークンは長期間有効だが、定期的な更新が必要な場合がある
- `check_token_validity` ツールでトークンの有効性をMCPクライアントから直接確認可能
- アクセストークンはリクエスト内でキャッシュされるが、Workers のステートレス性により次のリクエストでは再取得される

### 監視

- `wrangler tail` コマンドでリアルタイムログを確認
- ヘルスチェック: `GET /` でサーバー情報とツール一覧をJSON形式で返却

---

## まとめ

<!-- TODO: 詳細執筆 -->

- Cloudflare Workers + Hono + @hono/mcp の組み合わせで、リモートMCPサーバーを短期間で構築できた
- プラットフォーム選定では「SSEストリーミング対応」「コールドスタート」「コスト」が決め手
- ステートレス設計がWorkersの実行モデルと合致し、シンプルなアーキテクチャを維持できた
- Google Ads APIのような認証が複雑なAPIでも、Workersの Secrets管理とOAuthトークンの自動更新で運用負荷を低減
- リモートMCPサーバーにより、ローカル環境に依存せず、どのデバイス・どのMCPクライアントからでもGoogle Adsデータにアクセス可能になった
- 今後の展望: Durable Objectsを活用したセッション管理、ツールの追加（レポート生成、入札戦略変更など）
