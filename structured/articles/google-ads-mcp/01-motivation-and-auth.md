---
title: "Google広告APIをAIに直接つなぐ — MCPサーバーを作った動機と、認証地獄の乗り越え方"
status: draft
media: note
series: "Google広告 x MCP 実践ガイド"
series_order: 1
created: 2026-04-05
updated: 2026-04-05
source_project: MCPServer/mcp-google-ads-remote
published_url: ""
---

# Google広告APIをAIに直接つなぐ — MCPサーバーを作った動機と、認証地獄の乗り越え方

> ※ この記事はシリーズの第1回です。第2回ではローカルMCPサーバーの構築、第3回ではリモートMCPサーバーの構築を扱います。

## はじめに / なぜ作ったのか

Google広告を運用していると、毎日のように管理画面にログインしてデータを確認する作業が発生します。「過去30日のキャンペーンパフォーマンスどうだっけ？」「先週のCPA高かったキャンペーンどれだっけ？」——そのたびにブラウザを開いて、フィルタをかけて、期間を設定して……。

**もっと楽にできないのか。**

たとえば、Claude や Cursor に「過去30日のキャンペーンパフォーマンス見せて」と自然言語で聞いたら、そのまま Google広告 API を叩いてデータを返してくれる。そんな世界があったら最高ですよね。

それを実現するのが **MCP（Model Context Protocol）** という仕組みです。

この記事では、MCPサーバーを作って Google広告 API と AI を直接つなぐまでの道のりを、3回シリーズでお届けします。

| 回 | 内容 |
|---|---|
| **第1回（本記事）** | 動機と、認証まわりのセットアップ |
| 第2回 | Python + FastMCP でローカル MCP サーバーを構築 |
| 第3回 | リモート MCP サーバーとして公開・運用 |

第1回の今回は、最初にして最大の壁——**Google広告APIの認証**——を乗り越えるところまでを解説します。

---

## MCPとは（簡潔に）

MCP（Model Context Protocol）は、Anthropic社が提唱したオープン標準プロトコルです。よく「**AIアプリケーションのためのUSB-Cポート**」と表現されます。

USB-Cがどんなデバイスでも同じポートで接続できるように、MCPはどんな外部サービスでも同じプロトコルでAIにつなげられる——そんな思想です。

構造はシンプルです。

```
Claude / Cursor（AIクライアント）
      ↕ MCP プロトコル
   MCPサーバー
      ↕ 
   外部API（Google広告 API など）
```

2026年現在、MCPのエコシステムは急速に広がっています。Web版のClaudeでもMCPサーバーに接続でき、VS Codeとの統合も進んでいます。npmやpipで公開されたMCPサーバーを1クリックでインストールできる環境も整いつつあります。

ただ、MCPの仕様自体を深掘りするのはこの記事の目的ではないので、ここでは「AIと外部APIをつなぐ標準規格」とだけ理解してもらえれば十分です。本題に入りましょう。

---

## Google広告API認証 — ここが本記事の核心

正直に言います。MCPサーバーのコードを書くより、**認証を通すほうが10倍大変**でした。

Google広告APIの認証は、必要なものが多く、手順も長い。しかもエラーメッセージがわかりにくい。ここで挫折する人も多いのではないかと思います。

### 全体像

まず、必要なものを一覧で見てみましょう。

| # | 必要なもの | 取得場所 |
|---|---|---|
| 1 | GCPプロジェクト | Google Cloud Console |
| 2 | Google Ads APIの有効化 | GCPのAPIライブラリ |
| 3 | OAuth同意画面の設定 | GCPの認証情報 |
| 4 | OAuthクライアントID（client_id + client_secret） | GCPの認証情報 |
| 5 | デベロッパートークン（Developer Token） | Google広告管理画面 |
| 6 | リフレッシュトークン | OAuth認証フロー |

多いですよね。フローとしてはこうなります。

```
GCPプロジェクト作成
  ↓
Google Ads API有効化
  ↓
OAuth同意画面設定
  ↓
OAuthクライアントID作成 → client_id + client_secret取得
  ↓
Developer Token取得（Google広告管理画面のAPIセンター）
  ↓
認可コード取得（ブラウザでOAuth認証）
  ↓
リフレッシュトークン発行（curlでトークン交換）
  ↓
API動作確認（curlで直叩き）
```

では、1ステップずつ見ていきます。

---

### Step 1: GCPプロジェクト作成 + API有効化

まずは [Google Cloud Console](https://console.cloud.google.com/) で新規プロジェクトを作成します。

プロジェクト名は何でもOKですが、後から見てわかる名前にしておくと良いでしょう（例: `google-ads-mcp`）。

プロジェクトができたら、左メニューの「**APIとサービス**」→「**ライブラリ**」に進み、検索窓で「Google Ads API」を検索して**有効化**します。

> 💡 組織のGCP環境がある場合は、そこにプロジェクトを作成するケースもあります。個人で試す場合は個人のGCPアカウントで問題ありません。

---

### Step 2: OAuth同意画面の設定

次に、OAuth同意画面を設定します。「**APIとサービス**」→「**OAuth同意画面**」に進みます。

設定のポイント:

- **ユーザータイプ**: 「外部」を選択
- **スコープ**: `https://www.googleapis.com/auth/adwords` を追加
- **テストユーザー**: 自分のGoogleアカウントのメールアドレスを追加

テストユーザーの追加を忘れると、認証時に「このアプリはアクセスできません」的なエラーが出るので注意してください。

> 📎 参考: [Google Ads API の OAuth 設定について](https://blog.flinters.co.jp/entry/2024/06/19/120000_1)

---

### Step 3: OAuthクライアントIDの作成

「**APIとサービス**」→「**認証情報**」→「**認証情報を作成**」→「**OAuthクライアントID**」と進みます。

- **アプリケーションの種類**: 「デスクトップアプリ」を選択
- 名前は適当でOK

作成すると、**client_id** と **client_secret** が表示されます。この2つは後で使うので控えておきましょう。JSONファイルとしてダウンロードもできるので、保存しておくと安心です。

---

### Step 4: Developer Tokenの取得

ここがちょっと特殊です。Developer Tokenは **GCPではなく、Google広告の管理画面** から取得します。

[Google広告](https://ads.google.com/) にログインし、「**ツールと設定**」→「**APIセンター**」に進むと、22文字の英数字トークンが表示されます。これがDeveloper Tokenです。

**ここで重要な注意点があります。**

- 最初に発行されるDeveloper Tokenは **Pending（テスト）状態** です
- Pending状態では、**テストMCCアカウント配下でしか動作しません**
- 本番のGoogle広告アカウントにアクセスするには、**本番承認（Standard Access）** が必要です
- 承認には通常 **1〜3営業日** かかります

この「Pending問題」については後のセクションで詳しく触れます。ハマりポイントの筆頭です。

---

### Step 5: リフレッシュトークンの発行

いよいよOAuthフローを実行して、リフレッシュトークンを取得します。

**① 認可コードの取得**

以下のURLをブラウザで開きます（`your-client-id` は Step 3 で取得した client_id に置き換え）。

```
https://accounts.google.com/o/oauth2/auth?client_id=your-client-id.apps.googleusercontent.com&redirect_uri=http://localhost&scope=https://www.googleapis.com/auth/adwords&access_type=offline&response_type=code
```

Googleアカウントでログインし、アクセスを許可すると、`http://localhost` にリダイレクトされます。

ここでポイント。**localhostにサーバーが立っていないので、ブラウザには「サイトに到達できません」と表示されます。** でも大丈夫です。ブラウザのアドレスバーを見てください。URLに `code=` というパラメータが含まれているはずです。その値が認可コードです。

```
http://localhost/?code=4/0Axxxxxxxxxxxxxxxxxxxxxxxx&scope=...
```

この `code=` の後ろの値をコピーします。

**② トークン交換**

取得した認可コードを使って、curlでリフレッシュトークンに交換します。

```bash
curl \
  --data "grant_type=authorization_code" \
  --data "client_id=your-client-id.apps.googleusercontent.com" \
  --data "client_secret=your-client-secret" \
  --data "redirect_uri=http://localhost" \
  --data "code=取得した認可コード" \
  https://www.googleapis.com/oauth2/v3/token
```

成功すると、こんなレスポンスが返ります。

```json
{
  "access_token": "ya29.xxxxx...",
  "expires_in": 3599,
  "refresh_token": "1//0exxxxx...",
  "scope": "https://www.googleapis.com/auth/adwords",
  "token_type": "Bearer"
}
```

**`refresh_token` の値を必ず保存してください。** これが今後ずっと使う認証情報です。access_tokenは1時間で期限切れになりますが、refresh_tokenがあれば何度でもaccess_tokenを再発行できます。

---

### Step 6: 動作確認（curlでAPI直叩き）

ここまでで必要な認証情報が揃いました。実際にAPIを叩いてみましょう。

**アカウント一覧の取得:**

```bash
curl -f --request GET \
  "https://googleads.googleapis.com/v19/customers:listAccessibleCustomers" \
  --header "Content-Type: application/json" \
  --header "developer-token: your-developer-token" \
  --header "Authorization: Bearer your-access-token"
```

アクセス可能なカスタマーIDの一覧が返ればOKです。

**GAQLクエリのテスト:**

もう少し踏み込んで、GAQL（Google Ads Query Language）でキャンペーン一覧も取得してみましょう。

```bash
curl -i -X POST \
  "https://googleads.googleapis.com/v19/customers/your-customer-id/googleAds:searchStream" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-access-token" \
  -H "developer-token: your-developer-token" \
  -H "login-customer-id: your-mcc-id" \
  --data '{
    "query": "SELECT campaign.id, campaign.name FROM campaign ORDER BY campaign.id"
  }'
```

データが返ってきたら、認証は成功です。おめでとうございます！

……と言いたいところですが、ここに辿り着くまでに僕はかなりハマりました。次のセクションでその話をします。

---

## ハマりポイント: 403エラーとDeveloper Token Pending問題

### `login-customer-id` の罠

GAQLクエリを投げるとき、ヘッダーに `login-customer-id` を指定する必要があります。MCC（マネージャーアカウント）配下のクライアントアカウントを操作する場合です。

最初、僕はここに**クライアントアカウントのID**を指定していました。結果は `403 Forbidden`。

正解は **MCCのID** を指定することです。操作対象のクライアントアカウントIDはURLパスの `customers/{customer-id}` の部分に入れます。`login-customer-id` はあくまで「どのMCCとしてログインするか」を示すヘッダーです。

### Pending Developer Tokenの壁

Developer Tokenが Pending（テスト）状態だと、**テストMCCアカウント配下でしか動作しません**。

「テストMCCに本番アカウントを紐づければいいのでは？」と思うかもしれませんが、それはできません。**テストMCCと本番MCCは完全に分離されています。** テストMCCに本番のクライアントアカウントを紐づけることはできないのです。

さらに厄介なのは、テストMCC自体にはキャンペーンなどのデータが存在しないこと。つまり、GAQLクエリを投げても**データは空で返ります**。

「APIは通っているのにデータが返ってこない……何が間違っているんだ？」と悩みましたが、何も間違っていませんでした。テストMCCにはデータがないだけです。

### 本番承認後の切り替え

Developer Tokenの本番承認（Standard Access）が下りたら、以下を切り替えます。

- `login-customer-id` → **本番MCCのID**
- URLの `customers/{id}` → **本番クライアントアカウントのID**

これで本番データにアクセスできるようになります。承認には通常1〜3営業日かかるので、早めに申請しておくことをおすすめします。

---

## 次回予告

認証が通りました。これで Google広告 API を叩く準備は整いました。

次回（第2回）は、この認証情報を使って **Python + FastMCP で MCPサーバーを実装** します。Claude に自然言語で「キャンペーンの成果を見せて」と聞くだけで、Google広告のデータが返ってくる——そんな体験を作っていきます。

お楽しみに！

---

## シリーズ記事

- **第1回（本記事）**: Google広告APIをAIに直接つなぐ — MCPサーバーを作った動機と、認証地獄の乗り越え方
- 第2回: （近日公開）ローカルMCPサーバーの構築
- 第3回: （近日公開）リモートMCPサーバーの構築
