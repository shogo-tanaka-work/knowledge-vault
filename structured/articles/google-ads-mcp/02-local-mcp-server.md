---
title: "Python + FastMCPでGoogle広告MCPサーバーを構築する — Claudeから広告データを操作する"
status: draft
media: note
series: "Google広告 x MCP 実践ガイド"
series_order: 2
created: 2026-04-05
updated: 2026-04-05
source_project: MCPServer/mcp-google-ads-remote
published_url: ""
---

# Python + FastMCPでGoogle広告MCPサーバーを構築する — Claudeから広告データを操作する

> **シリーズ: Google広告 x MCP 実践ガイド**
> 第1回: Google Ads APIの認証設定
> **第2回: ローカルMCPサーバーの構築（本記事）**
> 第3回: Cloudflare Workersでリモート化（予定）

---

## はじめに

前回の記事では、Google Ads APIを利用するための認証設定（OAuthクライアントの作成、Developer Tokenの取得、テストMCCの構築）を完了しました。

今回は、その認証基盤の上に**Python + FastMCPでMCPサーバーを構築**し、Claude DesktopやCursorから自然言語でGoogle広告データを操作できるようにします。

ゴールは明確です。Claudeに「過去30日のキャンペーンパフォーマンスを見せて」と聞くだけで、Google Ads APIが叩かれてデータが返ってくる状態を作ること。MCPサーバーの実装は`google_ads_server.py`という**1ファイルで完結**するので、思ったよりシンプルです。

---

## 完成イメージ

MCPサーバーが動いている状態でClaudeに話しかけると、こんなことができるようになります。

| やりたいこと | Claudeへの指示例 | 呼ばれるツール |
|---|---|---|
| アカウント確認 | 「アカウント一覧を表示して」 | `list_accounts` |
| パフォーマンス分析 | 「過去30日のキャンペーンパフォーマンスを見せて」 | `get_campaign_performance` |
| カスタムクエリ | 「SELECT campaign.name, metrics.clicks FROM campaign WHERE segments.date DURING LAST_7_DAYS」 | `execute_gaql_query` |
| 広告クリエイティブ確認 | 「広告の見出しと説明文を一覧で見たい」 | `get_ad_creatives` |
| トークン確認 | 「認証トークンの有効性を確認して」 | `check_token_validity` |

Claudeがツールの説明文（docstring）を読んで、ユーザーの意図に最適なツールを自動で選んでくれます。GAQLクエリもClaudeが組み立ててくれるので、クエリ構文を覚える必要はありません。

---

## プロジェクト構成

```
mcp-google-ads/
├── google_ads_server.py          # メインサーバー（これ1ファイルで完結）
├── pyproject.toml
├── requirements.txt
├── .env                          # 認証情報（gitignore対象）
├── google_ads_token.json         # OAuthトークン（自動生成）
└── docs/
```

**技術スタック:**

| パッケージ | バージョン | 用途 |
|---|---|---|
| Python | 3.11+ | ランタイム |
| mcp (FastMCP) | >= 1.3.0 | MCPサーバーフレームワーク |
| google-auth | >= 2.25.2 | Google認証基盤 |
| google-auth-oauthlib | >= 1.2.1 | OAuth 2.0フロー |
| requests | >= 2.31.0 | HTTPクライアント |
| pydantic | >= 2.0.0 | パラメータバリデーション |
| python-dotenv | >= 1.0.0 | .env読み込み |

---

## FastMCPの基本

FastMCPは、Pythonの関数をデコレータで簡単にMCPツールとして公開できるフレームワークです。Model Context Protocol（MCP）のPython SDK に含まれています。

### サーバーの初期化

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "google-ads-server",
    dependencies=[
        "google-auth-oauthlib",
        "google-auth",
        "requests",
        "python-dotenv"
    ]
)
```

### ツールの定義

`@mcp.tool()` デコレータをつけるだけで、関数がMCPツールとして公開されます。

```python
@mcp.tool()
async def list_accounts() -> str:
    """アクセス可能なすべてのGoogle Adsアカウントを一覧表示します。"""
    creds = get_credentials()
    headers = get_headers(creds)
    url = f"https://googleads.googleapis.com/{API_VERSION}/customers:listAccessibleCustomers"
    response = requests.get(url, headers=headers)
    # ... 結果をフォーマットして返す
```

ここで重要なのは**docstring**です。Claudeはこの説明文を読んで「このツールは何ができるのか」を判断します。つまり、docstringの品質がツール選択の精度に直結します。

### パラメータの定義

Pydanticの`Field`を使ってパラメータに説明を付けます。

```python
from pydantic import Field

@mcp.tool()
async def execute_gaql_query(
    customer_id: str = Field(description="Google Ads顧客ID（10桁、ハイフンなし）"),
    query: str = Field(description="GAQLクエリ文字列")
) -> str:
    """カスタムGAQL（Google Ads Query Language）クエリを実行します。"""
    # ...
```

Claudeはこのdescriptionを見て、ユーザーの入力からパラメータを適切にマッピングしてくれます。

### サーバーの起動

```python
if __name__ == "__main__":
    mcp.run(transport="stdio")
```

stdioトランスポートで起動するため、Claude DesktopやCursorがプロセスを直接起動して通信します。

---

## 認証モジュールの実装

認証は環境変数 `GOOGLE_ADS_AUTH_TYPE` で2つの方式を切り替えられるようにしています。

### 1. OAuth 2.0（デフォルト）

個人ユーザー向けの認証方式です。フローは以下の通り。

1. `google_ads_token.json` からトークンを読み込み
2. 期限切れならリフレッシュトークンで自動更新
3. トークンファイルがなければブラウザ認証フローを起動

```python
def get_oauth_credentials():
    """OAuthユーザー認証情報を取得・更新します。"""
    creds = None
    token_path = GOOGLE_ADS_CREDENTIALS_PATH
    
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_info(creds_data, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())  # 自動リフレッシュ
        else:
            flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
            creds = flow.run_local_server(port=8080)
    
    return creds
```

### 2. サービスアカウント

自動化システム向けの認証方式です。JSONキーファイルから認証し、ドメイン委任にも対応しています。

```python
def get_service_account_credentials():
    credentials = service_account.Credentials.from_service_account_file(
        GOOGLE_ADS_CREDENTIALS_PATH, scopes=SCOPES
    )
    impersonation_email = os.environ.get("GOOGLE_ADS_IMPERSONATION_EMAIL")
    if impersonation_email:
        credentials = credentials.with_subject(impersonation_email)
    return credentials
```

### ヘッダー構築

Google Ads APIへのリクエストには、認証トークンに加えてDeveloper Tokenとログイン顧客IDが必要です。

```python
headers = {
    'Authorization': f'Bearer {token}',
    'developer-token': GOOGLE_ADS_DEVELOPER_TOKEN,
    'login-customer-id': format_customer_id(LOGIN_CUSTOMER_ID),
    'content-type': 'application/json'
}
```

### 顧客IDの正規化

実運用で地味にハマるポイントが、顧客IDのフォーマットです。ユーザーがハイフン付き・引用符付きなど様々な形式で入力してくることを想定して、正規化関数を用意しています。

```python
def format_customer_id(customer_id: str) -> str:
    customer_id = str(customer_id)
    customer_id = customer_id.replace('\"', '').replace('"', '')
    customer_id = ''.join(char for char in customer_id if char.isdigit())
    return customer_id.zfill(10)
```

`123-456-7890` でも `"1234567890"` でも、すべて `1234567890` に正規化されます。Claudeが顧客IDを渡すときの揺れを吸収する重要な関数です。

---

## 提供する14のMCPツール

このサーバーでは、以下の14ツールを提供しています。

| カテゴリ | ツール名 | 機能 |
|---------|---------|------|
| **アカウント** | `list_accounts` | アクセス可能なアカウント一覧 |
| | `get_account_currency` | アカウントの通貨コード取得 |
| **クエリ・レポート** | `execute_gaql_query` | カスタムGAQLクエリ実行 |
| | `run_gaql` | フォーマット指定GAQL（table/json/csv） |
| | `get_campaign_performance` | キャンペーンパフォーマンス指標 |
| | `get_ad_performance` | 広告パフォーマンス指標 |
| | `get_ad_creatives` | 広告クリエイティブ詳細（見出し・説明文） |
| | `list_resources` | GAQL利用可能リソース一覧 |
| **アセット** | `get_image_assets` | 画像アセット一覧 |
| | `download_image_asset` | 画像ダウンロード |
| | `get_asset_usage` | アセット使用状況 |
| | `analyze_image_assets` | アセットパフォーマンス分析 |
| **認証** | `check_token_validity` | トークン有効性確認 |
| | `refresh_access_token` | アクセストークン手動更新 |

実際に使ってみると、ほとんどのケースは `list_accounts` → `get_campaign_performance` のワークフローか、`run_gaql` でカスタムクエリを投げるパターンに集約されます。Claudeが適切にツールを選んでくれるので、ユーザーはツール名を意識する必要はありません。

---

## GAQL（Google Ads Query Language）について

GAQLはSQLに似たGoogle広告専用のクエリ言語です。MCPサーバー経由でClaudeに「こういうデータが欲しい」と伝えれば、Claudeがクエリを組み立ててくれます。

### 基本構文

```sql
SELECT campaign.name, metrics.clicks, metrics.impressions, metrics.cost_micros
FROM campaign
WHERE segments.date DURING LAST_30_DAYS
ORDER BY metrics.cost_micros DESC
LIMIT 50
```

### 知っておくべきポイント

- **cost_micros**: コスト値は100万分の1単位です。`1,000,000` = 1通貨単位（例: 1 USD、1 JPY）
- **日付フィルタ**: `DURING LAST_7_DAYS`、`DURING LAST_30_DAYS` などの定数が使える
- **出力形式**: `run_gaql` ツールなら `table` / `json` / `csv` を切り替え可能

SQLとの違いとしては、JOINが不要（リソース間の関係はAPI側で解決される）、`*` によるワイルドカード選択ができない、などがあります。

とはいえ、GAQLの細かい構文を覚える必要はほとんどありません。Claudeに「過去7日間でクリック数が多い順にキャンペーンを表示して」と伝えれば、適切なGAQLクエリを生成して実行してくれます。

---

## セットアップ手順

### 1. リポジトリクローン

```bash
git clone https://github.com/cohnen/mcp-google-ads.git
cd mcp-google-ads
```

### 2. 依存パッケージインストール

```bash
pip install -r requirements.txt
```

### 3. .env設定

プロジェクトルートに `.env` ファイルを作成します。

```env
GOOGLE_ADS_AUTH_TYPE=oauth
GOOGLE_ADS_CREDENTIALS_PATH=./google_ads_token.json
GOOGLE_ADS_DEVELOPER_TOKEN=your-developer-token
GOOGLE_ADS_LOGIN_CUSTOMER_ID=your-mcc-id
GOOGLE_ADS_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_ADS_CLIENT_SECRET=your-client-secret
```

前回の記事で取得した認証情報をここに設定してください。`google_ads_token.json` は初回のOAuth認証フロー完了後に自動生成されます。

### 4. Claude Desktopで接続

Claude Desktopの設定ファイル `claude_desktop_config.json` に以下を追加します。

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "google-ads": {
      "command": "python",
      "args": ["/path/to/mcp-google-ads/google_ads_server.py"],
      "env": {
        "GOOGLE_ADS_AUTH_TYPE": "oauth",
        "GOOGLE_ADS_CREDENTIALS_PATH": "/path/to/google_ads_token.json",
        "GOOGLE_ADS_DEVELOPER_TOKEN": "your-developer-token",
        "GOOGLE_ADS_LOGIN_CUSTOMER_ID": "your-mcc-id"
      }
    }
  }
}
```

`/path/to/` の部分は実際のパスに置き換えてください。環境変数は`.env`ではなくここで直接指定することもできます。

### 5. Cursorで接続

CursorのSettings > MCP から「Add new MCP server」で追加します。

- **Type**: command
- **Command**: `python /path/to/mcp-google-ads/google_ads_server.py`

環境変数はCursorのMCP設定画面、またはシェルの環境変数として設定してください。

---

## テストMCCでの動作確認

Developer Tokenが**Pending（テストアカウントアクセス）** の段階では、テストMCC配下のアカウントでのみ動作します。

### 確認手順

1. **`list_accounts`** でアカウントIDを確認 — テストMCC配下のアカウントIDが表示されればOK
2. **`get_account_currency`** で通貨コードを確認 — `JPY` や `USD` が返れば正常
3. **`get_campaign_performance`** を実行 — テストMCCにはキャンペーンがないので空データが返りますが、エラーが出なければAPI通信は成功しています

テスト環境で動作確認ができたら、Developer Tokenの本番承認を申請しましょう。承認後は `.env` の `GOOGLE_ADS_LOGIN_CUSTOMER_ID` を本番MCCのIDに切り替えるだけで移行完了です。

---

## リフレッシュトークンの更新

OAuthトークンは有効期限があり、長期間使わないと期限切れになることがあります。通常はサーバーが自動でリフレッシュしますが、リフレッシュトークン自体が失効した場合は手動更新が必要です。

### 手動更新手順

1. Google Cloud Consoleの認可URLにブラウザでアクセス
2. Googleアカウントでログインし認可コードを取得
3. `google_ads_token.json` の `refresh_token` を新しい値に更新
4. `expiry` を過去日時に設定（例: `2020-01-01T00:00:00.000000Z`）
5. MCPサーバーを再起動すれば、自動で新しいアクセストークンが取得される

あるいは、MCPツールの `check_token_validity` でトークンの状態を確認し、`refresh_access_token` で手動更新を試みることもできます。

---

## まとめ

今回は、Python + FastMCPで Google広告MCPサーバーを構築しました。

- **FastMCPのデコレータ**で、Pythonの関数をMCPツールとして簡単に公開
- **14のツール**で、アカウント管理からGAQLクエリ実行、画像アセット分析まで対応
- **OAuth / サービスアカウント**の2つの認証方式をサポート
- **Claude Desktop / Cursor**の両方から接続可能

`google_ads_server.py` 1ファイルで完結するシンプルな構成ながら、実用的な広告データ操作が可能になります。

ただし、このローカルMCPサーバーには課題もあります。

- **PCが起動していないと使えない** — ローカルプロセスなので当然ですが、外出先からは使えません
- **チーム共有ができない** — 各メンバーが個別にセットアップする必要があります
- **認証情報の管理** — 各端末に.envやトークンファイルを置く必要がある

次回は、このMCPサーバーを**Cloudflare Workersにデプロイしてリモート化**し、どこからでも・誰でもアクセスできるようにします。

---

> **シリーズ: Google広告 x MCP 実践ガイド**
> [第1回: Google Ads APIの認証設定](リンクURL)
> **第2回: ローカルMCPサーバーの構築（本記事）**
> [第3回: Cloudflare Workersでリモート化](リンクURL)
