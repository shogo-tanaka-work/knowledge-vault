---
title: "Cloudflare WorkersでリモートMCPサーバーを構築する — どこからでもGoogle広告を分析する"
status: draft
media: note
series: "Google広告 x MCP 実践ガイド"
series_order: 3
created: 2026-04-05
updated: 2026-04-05
source_project: MCPServer/mcp-google-ads-remote
published_url: ""
---

# Cloudflare WorkersでリモートMCPサーバーを構築する — どこからでもGoogle広告を分析する

> **シリーズ: Google広告 x MCP 実践ガイド**
> 第1回: Google Ads APIの認証設定
> 第2回: ローカルMCPサーバーの構築
> **第3回: Cloudflare WorkersでリモートMCPサーバーを構築（本記事・最終回）**

---

## はじめに

前回までの2記事で、Google Ads APIの認証セットアップと、Python + FastMCPによるローカルMCPサーバーの構築を完了しました。Claude DesktopやCursorから「過去30日のキャンペーンパフォーマンスを見せて」と聞けば、Google Ads APIを叩いてデータが返ってくる状態です。

しかし、使い込んでいくとローカル版の課題が見えてきました。

- **PCを起動していないと使えない** — 外出先やスマホからは一切アクセスできない
- **チーム共有ができない** — 同僚に「このMCPサーバー使ってみて」と言えない
- **Web版Claudeから使えない** — stdioはローカルプロセス間通信なので、ブラウザ上のClaude（claude.ai）からは接続できない

ローカルMCPは「自分のPC上でしか動かない」という構造的な制約を持っています。これを解決するには、MCPサーバーをクラウド上に移す必要があります。

今回のゴールは、**Cloudflare Workers上にリモートMCPサーバーを構築し、どこからでもGoogle広告データを分析できる環境を作ること**です。シリーズ最終回として、ローカルからリモートへの進化を完成させます。

---

## ローカルMCP vs リモートMCP

まず、ローカルMCPとリモートMCPの違いを整理しておきます。

```
ローカルMCP:
  Claude Desktop → (stdio) → ローカルプロセス → Google Ads API
  ※ 同じPCでしか使えない

リモートMCP:
  Claude Desktop / Web版Claude / Cursor → (HTTP) → クラウドサーバー → Google Ads API
  ※ どこからでもアクセス可能
```

ローカル版はstdio（標準入出力）でプロセス間通信を行うため、同じマシン上でしか動きません。リモート版はHTTP経由で通信するため、インターネットに接続できるあらゆるクライアントから利用可能になります。

MCPプロトコルが定義するトランスポートは、stdioとStreamable HTTP（SSE: Server-Sent Events）の2つ。リモートMCPは後者を使います。

---

## プラットフォーム選定: なぜCloudflare Workersか

リモートMCPサーバーをどこにホスティングするか。3つの候補を検討しました。

### 決め手1: SSEストリーミングと実行時間

MCPはStreamable HTTPでサーバーからクライアントにレスポンスを返します。このストリーミング接続が維持される時間が、プラットフォーム選定の最大の分岐点です。

- **Vercel**: Hobbyプラン10秒、Proプラン60秒の実行時間制限。MCPセッションではツール呼び出しを含む対話が続くため、この制限を超えることは十分にありうる
- **Render**: SSEの技術的制約はなし。ただし無料プランは15分でスリープし、復帰に10〜30秒のコールドスタートが発生する
- **Cloudflare Workers**: ストリーミングレスポンスに対応し、実行時間制限が他のサーバーレスプラットフォームと比べて柔軟

### 決め手2: コールドスタート

MCPクライアントがサーバーに接続する瞬間のレスポンス速度は、体験に直結します。

- **Workers**: エッジロケーション上で実行されるため、コールドスタートはほぼゼロ
- **Vercel**: コールドスタートあり（Renderほど深刻ではない）
- **Render**: 無料プランでスリープ復帰10〜30秒。MCPの接続タイムアウトに引っかかる可能性がある

### 決め手3: コスト

| プラットフォーム | 無料枠 | 課金モデル |
|:---|:---|:---|
| Cloudflare Workers | **10万リクエスト/日** | リクエスト単位 |
| Vercel | 100GB-hrs/月 | 実行時間ベース |
| Render | 750時間/月（スリープあり） | 常時起動時間ベース |

MCPサーバーの利用パターンは「1日に数十〜数百リクエスト」程度。Workers無料枠の10万リクエスト/日は、個人〜小規模チームの利用なら全く問題になりません。

### 決め手4: Hono + @hono/mcp エコシステム

技術選定で見逃せないのが、**HonoフレームワークとそのMCPアダプターがCloudflare Workers向けに最適化されている**点です。

- Honoの作者はCloudflare所属。Workers上での動作が最も安定している
- `@hono/mcp` が提供する `StreamableHTTPTransport` はWorkers前提で設計されている
- 依存パッケージは4つだけ（hono, @modelcontextprotocol/sdk, @hono/mcp, zod）
- 軽量な構成がWorkersのバンドルサイズ制限とも好相性

### 比較まとめ

| 要件 | Workers | Vercel | Render |
|:---|:---:|:---:|:---:|
| SSEストリーミング | ○ | △（時間制限） | ○ |
| コールドスタート | ほぼなし | あり | 大きい |
| 無料枠 | 10万req/日 | 100GB-hrs/月 | 750hrs/月 |
| エコシステム | Hono最適化 | Next.js向き | 汎用 |

結論として、**SSEストリーミング対応・コールドスタートの短さ・コスト・Honoエコシステムとの親和性**の4点から、Cloudflare Workersを選択しました。

---

## 技術スタック

リモート版のプロジェクト構成は以下の通りです。

```
mcp-google-ads-remote/
├── src/
│   ├── index.ts              # Honoアプリ + MCPエンドポイント
│   ├── tools.ts              # MCPツール実装
│   ├── google-ads-client.ts  # Google Ads APIクライアント
│   └── types.ts              # TypeScript型定義
├── scripts/
│   └── generate-token.js     # JWTトークン生成
├── wrangler.toml             # Cloudflare Workers設定
└── package.json
```

依存パッケージ:

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

たった4つ。Honoの軽量さがWorkersの制約と好相性なのは前述の通りです。

---

## 実装のポイント

### ステートレス設計

```typescript
app.all('/mcp', async (c) => {
  // リクエストごとにMCPサーバーとトランスポートを作成
  const mcpServer = createMcpServer(c.env);
  const transport = new StreamableHTTPTransport();
  await mcpServer.connect(transport);
  return transport.handleRequest(c);
});
```

Cloudflare Workersはリクエストごとに独立した実行コンテキストを持ち、グローバル状態を共有しません。つまり「ステートレスに設計せざるを得ない」制約があります。

これは一見すると制約ですが、実際にはアーキテクチャの健全性を担保してくれます。Renderのように常時起動するサーバーでは、インスタンスの生存管理やメモリリークへの配慮が必要です。Workersならそもそもその心配がありません。

### JWT認証

```typescript
app.use('/mcp', async (c, next) => {
  const jwtMiddleware = jwt({ secret: c.env.JWT_SECRET });
  await jwtMiddleware(c, next);
  
  // ソルトの一致チェック（二重チェック）
  const payload = c.get('jwtPayload');
  if (payload.salt !== c.env.JWT_SALT) {
    return c.json({ error: 'Unauthorized' }, 401);
  }
});
```

リモートMCPサーバーは公開エンドポイントになるため、認証が必須です。認証方式として**JWT（JSON Web Token）** を選びました。

- **API Keyより安全**: 有効期限を設定でき、ペイロードに任意の情報を含められる
- **OAuth2よりシンプル**: 認可サーバーが不要。個人〜小規模チームの用途なら十分
- **二重チェック**: JWT署名検証に加え、ペイロード内の `salt` フィールドをサーバー側の環境変数と照合

トークンは2週間で期限切れに設定し、`scripts/generate-token.js` で再生成する運用です。

### Google Ads API連携の違い

ローカル版はPythonの `google-auth` ライブラリでOAuthトークンを自動管理していました。しかしWorkers環境ではNode.jsネイティブのモジュールが使えないため、**fetch APIでOAuthトークンを直接更新**します。

```typescript
async getAccessToken(): Promise<string> {
  const response = await fetch('https://oauth2.googleapis.com/token', {
    method: 'POST',
    body: new URLSearchParams({
      client_id: this.env.GOOGLE_ADS_CLIENT_ID,
      client_secret: this.env.GOOGLE_ADS_CLIENT_SECRET,
      refresh_token: this.env.GOOGLE_ADS_REFRESH_TOKEN,
      grant_type: 'refresh_token'
    })
  });
  // アクセストークンをキャッシュ（有効期限5分前に更新）
}
```

Workers環境の制約が、逆にAPIの仕組みを深く理解するきっかけになりました。ライブラリが隠蔽していたOAuth2のトークン更新フローを、自前で実装することで仕組みが明確になります。

---

## ローカル版との比較

ローカル版とリモート版の違いを一覧にまとめます。

| 観点 | ローカル版 | リモート版 |
|:---|:---|:---|
| 言語 | Python | TypeScript |
| フレームワーク | FastMCP | Hono + @hono/mcp |
| 通信方式 | stdio（ローカルプロセス） | Streamable HTTP/SSE |
| 認証（API） | OAuth / Service Account | OAuth Refresh Token |
| 認証（クライアント） | なし（ローカルのため不要） | JWT Bearer Token |
| API Version | v19 | v23 |
| ツール数 | 13 | 9 |
| デプロイ | ローカルプロセス | Cloudflare Workers |
| チーム共有 | 不可 | 可能 |
| Web版Claude | 非対応 | 対応 |
| コスト | 無料（自分のPC） | 無料（Workers無料枠） |

ツール数がリモート版で少ない理由は、`download_image_asset` 等のローカルファイルシステム依存ツールを除外したためです。リモートサーバーにはファイルシステムがないので、画像ダウンロードのようなツールは構造的に不要になります。

---

## デプロイ手順

### 1. シークレット設定

Google Ads APIとJWT認証に必要な6つのシークレットを登録します。

```bash
wrangler secret put GOOGLE_ADS_DEVELOPER_TOKEN
wrangler secret put GOOGLE_ADS_CLIENT_ID
wrangler secret put GOOGLE_ADS_CLIENT_SECRET
wrangler secret put GOOGLE_ADS_REFRESH_TOKEN
wrangler secret put JWT_SECRET
wrangler secret put JWT_SALT
```

`wrangler secret put` はCLIから対話形式で値を入力でき、ダッシュボードを開く必要がありません。コード上では `c.env.GOOGLE_ADS_CLIENT_ID` のようにアクセスできます。

### 2. デプロイ

```bash
npm run deploy
# → https://mcp-google-ads.your-account.workers.dev
```

これだけです。Cloudflare Workersのデプロイはとにかく速い。数秒で完了します。

### 3. JWTトークン生成

```bash
node scripts/generate-token.js
```

生成されたトークンをMCPクライアントの設定に使います。有効期限は2週間です。

### 4. Claude Desktopから接続

```json
{
  "mcpServers": {
    "google-ads": {
      "command": "mcp-remote",
      "args": [
        "https://mcp-google-ads.your-account.workers.dev/mcp",
        "--header",
        "Authorization: Bearer your-jwt-token"
      ]
    }
  }
}
```

`mcp-remote` はリモートMCPサーバーへの接続を仲介するプロキシツールです。Claude Desktopのstdioトランスポートと、リモートサーバーのStreamable HTTPトランスポートの間を橋渡しします。

---

## 運用Tips

- **リアルタイムログ**: `wrangler tail` で本番環境のログをストリーミング確認できる。デバッグ時に重宝する
- **ヘルスチェック**: `GET /` でサーバー情報とツール一覧をJSON形式で返却。動作確認に使える
- **JWTトークン再生成**: 2週間で期限切れになるため、定期的に `node scripts/generate-token.js` で再生成が必要
- **トークン確認**: `check_token_validity` ツールでGoogle Adsトークンの有効性をMCPクライアントから直接確認可能。「トークンの状態確認して」と聞くだけでOK

---

## シリーズまとめ

3記事を通じてやったことを振り返ります。

| 回 | 内容 | キーポイント |
|:---|:---|:---|
| 第1回 | Google広告APIの認証セットアップ | OAuth2クライアント作成、Developer Token取得、テストMCC構築 |
| 第2回 | Python + FastMCPでローカルMCPサーバー構築 | 1ファイルで13ツール実装、Claude Desktopから即利用可能 |
| 第3回 | TypeScript + Hono + Cloudflare WorkersでリモートMCPサーバー構築 | どこからでもアクセス可能、Web版Claude対応 |

**得られたもの:**

- どのデバイスからでも自然言語でGoogle広告データを分析できる環境
- MCPの「ローカル → リモート」進化の実践的知見
- プラットフォーム選定の判断基準（SSE対応、コールドスタート、コスト、エコシステム）

**今後の展望:**

- **Durable Objectsを活用したセッション管理** — 現在はステートレスだが、セッションを維持できれば対話の文脈を跨いだ分析が可能になる
- **ツールの追加** — レポート生成、入札戦略変更、キーワード追加など、書き込み系のツールを段階的に実装
- **他のMCPクライアントからの接続検証** — Windsurf、Cline等の対応状況を確認

---

## リポジトリ

- ローカル版: [https://github.com/cohnen/mcp-google-ads](https://github.com/cohnen/mcp-google-ads)
- リモート版: （リポジトリURL準備中）

---

> **シリーズ: Google広告 x MCP 実践ガイド**
> [第1回: Google Ads APIの認証設定](リンクプレースホルダ)
> [第2回: ローカルMCPサーバーの構築](リンクプレースホルダ)
> [第3回: Cloudflare WorkersでリモートMCPサーバーを構築（本記事）](リンクプレースホルダ)
