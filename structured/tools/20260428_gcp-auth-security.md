# GCP認証セキュリティ設計 検証ログ

> ステータス: 進行中
> 作成日: 2026/04/28
> 最終更新: 2026/04/28
> ファイルパス: ~/Documents/verification-logs/projects/20260428_gcp-auth-security.md

---

📋 プロジェクト概要

* カテゴリ: セキュリティ設計 / GCP認証基盤
* 期間: 2026/04/28 -（検証中）
* 主要メンバー: 田中省伍（shogoworks）
* ステークホルダー: shogoworks 個人事業
* プロジェクトステータス: 進行中

---

## 0. なぜこの議論をしているか（背景コンテキスト）

### 上位の目的

Anthropicのニュースルーム（anthropic.com/news）を自動クローリングし、
記事タイトル・本文・URLをGoogle DriveもしくはGoogle Docsに自動格納するシステムを構築したい。

### 技術スタック（決定済み）

* **クローリング**: Python または Node.js（n8nからの乗り換え）
* **実行環境**: GitHub Actions（Cron schedule）または Render
* **格納先**: Google Drive / Google Docs
* **GCP認証**: サービスアカウント or OIDC（WIF）

### この議論が生まれた理由

Google Drive / Docs API を使うには GCP 認証が必要。
当初はアクセストークン・APIキー直書きで運用していたが、
セキュリティが低いため OAuth2 / サービスアカウント方式へ乗り換えを検討。
その過程で GCP の組織ポリシー変更が必要になり、
その設定が適切かどうかを壁打ちで整理した。

---

## 1. 背景と目的

* Anthropicニュースの自動収集・格納パイプラインを構築する
* 既存のAPIキー直書き運用を脱し、セキュアな認証方式に移行する
* GCP組織ポリシーの正しい運用方法を理解し、最小権限原則を実現する
* OIDCとサービスアカウントの使い分けを明確にし、実装方針を固める

---

## 2. 取り組み内容

### 実施した施策・活動

* anthropic.com/news の直接fetchが可能かを検証（✅ 確認済み）
* 非公式RSSフィード（RSSHub・Olshansk/rss-feeds）の実用性を検証（❌ 利用不可）
* 二段構えfetch（一覧→個別記事）の実現性を検証（✅ 確認済み）
* Google Drive API の認証方式を比較調査
* GCP組織ポリシー（disableServiceAccountKeyCreation）の仕様を調査
* OIDC / WIF（Workload Identity Federation）の対応プラットフォームを調査
* タグ方式によるサービスアカウントキー作成の最小権限設定を調査

### 使用したツール・技術

* Cloudflare Workers（当初のクローリング実行環境候補）
* GitHub Actions（OIDC対応の実行環境として採用候補）
* Render（Python/Node.js デプロイ先候補 ← OIDCは非対応）
* Google Drive API v3 / Google Docs API v1
* GCP IAM / 組織ポリシー / Workload Identity Federation
* Python `google-auth` / `google-api-python-client`

### 主要な意思決定とその理由

* **n8n → Python/Node.js に変更**: より細かい制御と実行環境の自由度向上のため
* **Cron-job.org または GitHub Actions を外部Cronとして採用**: Cloudflare Workers の無料枠 Cron Trigger（5個/アカウント）を温存するため
* **サービスアカウント方式を採用（Render利用時）**: RenderはOIDCトークンを発行しないためWIFが使えない
* **GitHub Actions利用時はWIF（キーレス）を採用**: JSONキー不要で最もセキュア
* **GCP組織ポリシーはタグ方式で最小権限管理**: 組織全体をONに戻し、必要なサービスアカウントのみ個別除外

---

## 3. 進捗と成果

### 達成できたこと

* anthropic.com/news の HTML fetch が可能なことを実証
* 一覧ページから記事URLを抽出し、個別記事本文を取得するロジックを設計
* 直近の記事一覧（2026年4月分）の取得を確認
* GCP認証の全方式（APIキー/OAuth2/サービスアカウント/WIF）を比較整理
* GCP組織ポリシー変更の背景（2024/05/03ルール改正）を把握
* タグ方式による最小権限設定の手順を公式ドキュメントから確認

### 定量的な成果

* 確認した直近記事数: 10件（2026/03〜04）
* Cloudflare Workers 無料枠 Cron Trigger 消費: 0個（外部Cron回避設計）
* Workerアプリ数消費: 1 / 100個（無料枠内）

### 定性的な成果

* セキュリティ設計の全体像が整理でき、実装フェーズに進める状態になった
* GCP組織ポリシーの「なぜ動かなかったか」が仕様レベルで理解できた
* 現状（組織全体OFF）のリスクを認識し、修正方針が固まった

---

## 4. 学びとナレッジ

### うまくいったこと（Good）

* anthropic.com/news は公式RSSなしでも直接fetchで十分対応可能
* GitHub Actionsを使えばWIFでキーレス認証が実現でき、最もセキュアな構成になる
* タグ方式はGoogleが公式推奨しており、サービスアカウント単位で細かく制御できる

### うまくいかなかったこと（Bad）

* 非公式RSS（RSSHub・Olshansk）は2025年11月以降更新停止または403でアクセス不可
* Render/Fly.io/RailwayなどのPaaSはOIDCトークン未発行のためWIF非対応
* GCPのプロジェクト単位でのポリシー上書きは、組織レベルで強制されている場合には不可能（2025年6月のGoogleフォーラムで確認）
* Claudeコンテナからの直接fetchは「Host not in allowlist」でブロックされる（実行環境の制約）

### 改善ポイント（Improve）

* 現状の組織レベルOFF状態をタグ方式に移行し、最小権限を実現する
* サービスアカウントキーは1SA = 1キーに限定し、スコープを `drive.file` に絞る

### 技術的な発見・Tips

**GCP組織ポリシーの階層と上書きルール（重要）**
```
組織レベルで Enforce=ON → プロジェクト単位での上書きは不可能
組織レベルで Enforce=OFF → 全プロジェクトが解放される（開けっぱなし）
正解: 組織ON + タグ方式で特定SAのみ除外
```

**Cloudflare Workers でのCron回避パターン**
```
node-cronは使えない（常駐プロセスが存在しないため）
外部Cron（cron-job.org / GitHub Actions）が Workerの URL を HTTP GET で叩く
→ CronTrigger消費ゼロで同等の定期実行が実現できる
```

**WIFが使える/使えないプラットフォーム**
```
✅ 使える: GitHub Actions, GitLab CI/CD, AWS EC2, Azure VM
❌ 使えない: Render, Fly.io, Railway, Cloudflare Workers, その他一般PaaS
```

**GCP disableServiceAccountKeyCreation の変更履歴**
```
2024/05/03: 新規作成組織でデフォルトON（強制）に変更
2024/06/16: 漏洩キーの自動無効化もデフォルト化
→ この日以降に作ったGCP組織では初期状態でキー作成不可
```

**Double-lockに注意**
```
iam.disableServiceAccountKeyCreation（新）
iam.disableServiceAccountKeyCreation（legacy）
の2つが存在しており、両方解除しないと動かない場合がある
```

---

## 5. 課題と対応

### 発生した課題

* GCP組織レベルのポリシーが全開放状態になっており、セキュリティリスクがある
* プロジェクト単位での上書き解除を試みたが機能しなかった（組織レベルOFFのため）
* Render環境でのWIF非対応により、実行環境の選定に制約が生じている

### 対応方法（AI推奨手順）

#### 課題①：組織ポリシーの最小権限化（タグ方式）

**未検証。以下の手順で対応可能（Googleの公式推奨手順）。**

**前提ロール（組織レベルで付与が必要）**
```
roles/orgpolicy.policyAdmin  （組織ポリシー管理者）
roles/resourcemanager.tagAdmin（タグ管理者）
※ プロジェクトレベルでは付与不可。組織を選択した状態で付与する。
```

**STEP 1：タグキーとタグ値を作成**
```
GCPコンソール → 「リソースマネージャー」→「タグ」→「タグキーを作成」

タグキー: disableServiceAccountKeyCreation
タグ値1: enforced     （禁止）
タグ値2: not_enforced  （許可）
```

**STEP 2：組織にデフォルトタグ（enforced）を付与**
```
「リソースマネージャー」→「タグ」
→ 組織を選択 →「タグを付与」
キー: disableServiceAccountKeyCreation
値:   enforced
```

**STEP 3：対象サービスアカウントに除外タグを付与**
```
「IAMと管理」→「サービスアカウント」
→ news-crawler@shogoworks-tools.iam... を選択
→「タグ」タブ →「タグを追加」
キー: disableServiceAccountKeyCreation
値:   not_enforced
```

**STEP 4：組織ポリシーを条件付きルールに更新**
```
GCPコンソール → 組織を選択
→「IAMと管理」→「組織のポリシー」
→「iam.disableServiceAccountKeyCreation」→「ポリシーを管理」

ルール1（条件付き・除外）:
  条件: resource.matchTag(
    "YOUR_ORG_ID/disableServiceAccountKeyCreation", "not_enforced"
  )
  適用: 強制しない（OFF）

ルール2（デフォルト）:
  条件: なし
  適用: 強制する（ON）

→「ポリシーを設定」
```

**STEP 5：組織レベルのポリシーをONに戻す**
```
同じポリシー画面でデフォルトルールを「強制する（ON）」に変更
※ STEP 4 完了後に実施すること（逆順にするとキーが使えなくなる）
```

**⚠️ 注意：作業順序**
```
❌ NG: 組織ON → タグ設定（この間に既存キーが無効化される）
✅ OK: タグ作成 → SAにタグ付与 → 条件ポリシー設定 → 組織ON
```

---

#### 課題②：実行環境の選定（GitHub Actions vs Render）

**GitHub Actions を優先推奨（WIFが使えるため）**

```yaml
# .github/workflows/crawl.yml
name: Anthropic News Crawler

on:
  schedule:
    - cron: '0 0 * * *'  # 毎日09:00 JST (UTC+9)

jobs:
  crawl:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      id-token: write    # OIDCトークン発行に必須

    steps:
      - uses: actions/checkout@v4

      # WIF認証（JSONキー不要）
      - uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: ${{ secrets.WIF_PROVIDER }}
          service_account: ${{ secrets.WIF_SA_EMAIL }}

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - run: pip install -r requirements.txt

      # 別ファイルのクローラーを実行
      - run: python src/crawler.py
```

**Renderを使う場合（サービスアカウントJSON方式）**
```
環境変数 GOOGLE_SERVICE_ACCOUNT_JSON にJSONの中身を設定
スコープは drive.file のみに限定
Cron実行は Render の Cron Jobs 機能を使用
```

---

#### 課題③：サービスアカウントの安全な運用ルール

**未検証。以下のルールを運用で守ること。**

```
1. 1 SA = 1キーのみ（複数キーを持たない）
2. スコープは drive.file のみ（drive 全体は付与しない）
3. JSONキーはコードに直書きしない（環境変数で管理）
4. .gitignore に *.json を追加してコミット防止
5. キーは90日でローテーション（GCPコンソールで有効期限設定）
6. 不要になったキーはすぐ削除
7. 漏洩検知の自動無効化設定（iam.serviceAccountKeyExposureResponse）を有効に保つ
```

### 未解決の課題

* タグ方式への移行：**未実施**（手順は確認済み、実作業が残っている）
* Render vs GitHub Actions の最終選定：**未決定**
* WIF設定手順の実際の動作確認：**未検証**
* クローラーの本実装（Python/Node.js コード）：**未着手**

---

## 6. コストとリソース

### 人的リソース

* 田中省伍 1名（設計・実装・運用すべて）

### 金銭的コスト

| 項目 | 月額 |
|------|------|
| Cloudflare Workers（Free） | $0 |
| GitHub Actions（Public repo or Free枠） | $0 |
| GCP（Drive/Docs API） | $0（無料枠内） |
| cron-job.org | $0 |
| Render（Free Tier） | $0〜$7 |

### コスト対効果

* ほぼゼロコストで自動ニュース収集・格納パイプラインが実現できる見込み

---

## 7. 今後の展開

### 次のアクション

* [ ] GCP組織ポリシーをタグ方式に移行（STEP 1〜5）
* [ ] GitHub Actions + WIF の設定・動作確認
* [ ] Python クローラー本実装（二段fetchロジック）
* [ ] Google Drive / Docs への書き込みテスト
* [ ] 本番デプロイ・Cron動作確認

### 横展開の可能性

* 同じ認証基盤を使って OpenAI / Google DeepMind などの他社ニュースにも対応可能
* n8n の Google Drive ノードと同じ認証情報を使い回せる（一度設定すれば永続利用）
* GitHub Actions + WIF のパターンは他のGCPサービス連携にも流用可能

### 長期的な改善案

* WIFが使えない環境でも、将来的にRenderやFly.ioがOIDCサポートを追加する可能性がある
* Workload Identity Federation の設定テンプレートをスキルファイル化する

---

📚 関連リソース

### 成果物・ドキュメント

* `anthropic-news-crawler.md` — クローリング設計まとめ
* `anthropic-news-crawler-arch.png` — アーキテクチャ構成図

### 参考資料

* [GCP公式: Troubleshoot org policy errors for service accounts](https://docs.cloud.google.com/iam/docs/troubleshoot-org-policies)
* [GCP公式: Restricting service account usage](https://docs.cloud.google.com/resource-manager/docs/organization-policy/restricting-service-accounts)
* [GCP公式: Workload Identity Federation](https://docs.cloud.google.com/iam/docs/workload-identity-federation)
* [GCP公式: Using OAuth 2.0 for Server to Server Applications](https://developers.google.com/identity/protocols/oauth2/service-account)
* [GitHub: google-github-actions/auth](https://github.com/google-github-actions/auth)
* [Google Developerフォーラム: プロジェクト単位での上書き不可の確認（2025/06）](https://discuss.google.dev/t/cant-disable-inherited-iam-organization-policy-service-account-key-creation-blocked-at-project-lev/192976)

### 関連プロジェクト

* Cloudflare Workers ドメインルーティング設計（shogo-works Worker）
* shogoworks 会計自動化ツールキット

---

✅ メモ・雑記

* GCP組織ポリシーは2024/05以降に作った組織ではデフォルトON。省伍さんのケースはプロジェクト単位での上書きを試みたが機能せず、組織レベルで解除したという経緯。この動作はGCPの仕様通り。
* Renderなど一般PaaSでのWIF非対応は2026/04時点の情報。将来変わる可能性あり。
* タグ方式はDouble-lockに注意。`iam.disableServiceAccountKeyCreation` と `iam.disableServiceAccountKeyCreation（legacy）` の2つが存在する場合があり、両方対応が必要。
* `drive.file` スコープはアプリが作成したファイルのみアクセス可能。既存のDriveファイルへの読み書きには `drive` または `drive.readonly` が必要になる場合がある点に注意。

---

## 📝 更新ログ

| 日時 | 更新内容の概要 |
|---|---|
| 2026/04/28 | ファイル作成（init）— GCP認証セキュリティ設計の壁打ち内容を記録 |
