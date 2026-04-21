# Claude Code + GitHub + Vercel でつくるAI駆動開発の環境

> ゼロから本番公開まで — ジュニアエンジニア向け解説

---

## この記事の対象読者

- Git と GitHub の基本操作（clone / push / PR）ができる
- HTML・CSS・JavaScript を書いたことがある
- AI が実際の開発現場でどう使われているか知りたい

---

## STEP 0: 全体像を把握する

まず「どのツールが何をするのか」を理解しておきましょう。

```
┌─────────────────────────────────────────────────┐
│                  開発者のPC                       │
│                                                   │
│  [Claude Code]  ←── AIが実装・PR作成を支援        │
│       ↓                                           │
│  [コードエディタ / ターミナル]                     │
└───────────────────┬─────────────────────────────┘
                    │ git push
                    ↓
┌─────────────────────────────────────────────────┐
│                  GitHub                           │
│                                                   │
│  ・コードの保管場所（リポジトリ）                  │
│  ・PR（変更提案）のレビュー・マージ                │
│  ・GitHub Actions でテスト自動実行（任意）          │
│  ・Dependabot で脆弱性を自動検知                   │
└───────────────────┬─────────────────────────────┘
                    │ mainブランチにマージ → 自動デプロイ
                    ↓
┌─────────────────────────────────────────────────┐
│                  Vercel                           │
│                                                   │
│  ・サイトのホスティング（公開場所）                 │
│  ・PRのたびにプレビューURLを自動生成               │
│  ・カスタムドメインの紐付け・SSL自動発行           │
└─────────────────────────────────────────────────┘
```

**一言で言うと：**
- **Claude Code** = AI搭載の開発アシスタント（実装・PR作成まで担う）
- **GitHub** = コードの管理・品質チェックの場所
- **Vercel** = 本番サイトを公開・運用する場所

---

## STEP 1: 開発環境のセットアップ

必要なツールを3つインストールします。

### 1-1. Node.js v22

Vercel や Astro などのフロントエンドツールを動かすために必要です。

```bash
# バージョン確認（22.x.x と表示されればOK）
node -v
```

インストールされていない場合は [Node.js 公式サイト](https://nodejs.org/) から LTS（v22）をダウンロードしてください。

### 1-2. GitHub CLI（gh コマンド）

ターミナルから GitHub を操作するためのツールです。

```bash
# macOS（Homebrew）
brew install gh

# インストール後、認証
gh auth login
```

`gh auth login` を実行すると対話形式で GitHub アカウントの認証が進みます。ブラウザが開くので画面の指示に従ってください。

### 1-3. Claude Code（Anthropic CLI）

```bash
npm install -g @anthropic-ai/claude-code
```

インストール後、`claude` コマンドで起動します。API キーの設定は初回起動時に案内されます。

---

## STEP 2: GitHubリポジトリを「守る」設定

リポジトリを作っただけでは、誰でも（自分でも）mainブランチに直接 push できてしまいます。これは「安全レールがない状態」です。以下の設定でリポジトリを守りましょう。

### なぜ直接 main に push してはいけないのか

```
【危険な状態（設定なし）】
開発者 → main に直接 push → 即座に本番へ反映
         ↑ バグがあっても止まらない

【安全な状態（設定あり）】
開発者 → feature ブランチ → PR 作成 → CI チェック → マージ → 本番へ反映
                                         ↑ ここで問題を検知できる
```

### 2-1. mainブランチ保護（Rulesets）

GitHub のリポジトリページから設定します。

```
Settings → Rules → Rulesets → New ruleset
```

**重要な設定項目：**

| 設定 | 値 | 意味 |
|------|-----|------|
| Enforcement status | **Active** | これが Disabled だとルールが一切効かない |
| Target branches | `main` | 保護対象 |
| Require a pull request | ON | PR 経由でないとマージ不可 |
| Require status checks to pass | ON（任意） | CI が通らないとマージ不可 |
| Block force pushes | ON | 強制上書き禁止 |

> **ポイント：** Enforcement status を `Active` にするのを忘れずに。`Disabled` で作成すると設定が全て無効になります（実際によくあるミスです）。

### 2-2. Dependabot の有効化

使っているライブラリに脆弱性（セキュリティの穴）が発見されたとき、自動で修正PRを作ってくれます。

```
Settings → Code security → Dependabot alerts → Enable
Settings → Code security → Dependabot security updates → Enable
```

さらに、`.github/dependabot.yml` をリポジトリに追加しておくと週次で自動チェックが走ります。

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
    labels:
      - "dependencies"
```

> **実体験：** Dependabot を有効にした直後に 11件の脆弱性（うち high が 5件）を検出しました。気づかないまま運用し続けていたリスクが一瞬で見えます。

### 2-3. マージ戦略を Squash merge に統一

```
Settings → General → Pull Requests
```

| マージ方法 | ON/OFF | 理由 |
|------------|--------|------|
| Merge commit | **OFF** | 履歴が複雑になる |
| **Squash merge** | **ON** | 1PR = 1コミットでシンプル |
| Rebase merge | **OFF** | コンフリクト時にやっかい |

Squash merge にすると「1つの PR = 1つのコミット」になり、main の履歴が読みやすくなります。

---

## STEP 3: Claude Code のプランモードで設計する

Claude Code の最大の特徴は「実装前に設計を合意してから動く」プランモードです。

### プランモードとは

```bash
claude  # Claude Code を起動
```

起動後、`/plan` と入力するとプランモードに入ります。

**プランモードでできること：**
- 実装方針を複数の選択肢で提示してくれる
- 「どのアプローチにしますか？」と確認してから実装を始める
- 設計の記録をファイルに保存する

### 実際のやりとりイメージ

```
ユーザー: サービス紹介ページを追加したい

Claude Code: 以下の3点について確認させてください。
  1. ページ構成：シングルページ vs. カテゴリ別複数ページ
  2. デザイン：既存デザインに合わせる vs. 新規デザイン
  3. コンテンツ：静的テキスト vs. CMSで管理

どれにしますか？

ユーザー: シングルページ、既存デザイン、静的テキスト

Claude Code: 了解です。では実装を開始します...
```

実装の前に方針を合意するので、「作ってみたら思ってたのと違う」という手戻りが大幅に減ります。

### Claude Code が担うこと

- コードの実装
- テストの作成
- `gh pr create` による PR の自動作成
- エラーの調査と修正提案

**人間が担うこと（Claude Code が触れない領域）：**
- GitHub・Vercel の GUI 操作（ブラウザ上の設定）
- sudo が必要な OS 権限操作
- 最終的なマージの判断

---

## STEP 4: CI/CDパイプライン（任意・推奨）

> **この STEP は任意です。** 最初はスキップして STEP 5 に進んでも本番公開はできます。ただし以下のリスクを把握した上で判断してください。

### CI/CD を導入しない場合のリスク

| リスク | 内容 |
|--------|------|
| バグが main に入る | テストを手動で実行し忘れると気づかない |
| Dependabot PR の品質が不明 | 自動作成された PR が問題ないか確認できない |
| 後から導入が大変 | チームが増えると後付けコストが跳ね上がる |

### CI を導入する場合（最小構成）

`.github/workflows/ci.yml` を作成するだけです。

```yaml
name: CI
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '22'
      - run: npm ci
      - run: npm run test    # テストが通らないとマージ不可
      - run: npm run build   # ビルドが通らないとマージ不可
```

このファイルをリポジトリに追加 → GitHub がPRのたびに自動実行してくれます。

---

## STEP 5: Vercel でホスティング → 本番公開

コードができたら Vercel で公開します。GitHub と連携するだけで、main へのマージが自動で本番反映になります。

### 5-1. Vercel でプロジェクト作成

1. [vercel.com](https://vercel.com) にアクセス → GitHub でログイン
2. 「Add New Project」→ GitHub リポジトリを選択
3. フレームワークが自動検出される（Astro / Next.js など）
4. 「Deploy」をクリック

初回デプロイが完了すると `https://[project-name].vercel.app` でサイトが公開されます。

### 5-2. 環境変数の設定

API キーなど秘密の情報は、コードに直接書かずに Vercel の環境変数として管理します。

```
Vercel ダッシュボード → Project → Settings → Environment Variables
```

| 変数名 | 用途 |
|--------|------|
| `RESEND_API_KEY` | メール送信API |
| `PUBLIC_GA4_ID` | Google Analytics |

> **重要：** API キーをコードに書いて GitHub に push するのは厳禁です。必ず環境変数で管理してください。

### 5-3. プレビューデプロイ（Vercel の便利な機能）

Vercel は PR を作るたびに自動でプレビュー用の URL を発行します。

```
main → https://your-domain.com（本番）
PR#5 → https://your-project-abc123.vercel.app（プレビュー）
PR#6 → https://your-project-def456.vercel.app（プレビュー）
```

本番に影響を与えずに「この変更、見た目どう？」を確認できます。マージ前に動作確認できる安全網です。

### 5-4. カスタムドメインの紐付け

独自ドメイン（例: `yoursite.com`）を使いたい場合：

```
Vercel ダッシュボード → Project → Settings → Domains → Add
```

ドメインを入力すると、DNS に追加すべきレコードが表示されます。ドメインレジストラ（お名前.com など）の DNS 設定にそのレコードを追加するだけです。SSL 証明書は Vercel が自動で発行・更新してくれます。

**mainにマージ = 本番リリース**という明確なルールができるため、チームでの開発でも認識のズレが起きにくくなります。

---

## STEP 6: 運用フェーズ — 変更は常に PR 経由

環境が整ったあとの日常的な開発フローです。

### 通常の変更手順

```bash
# 1. ブランチを作る
git checkout -b feat/add-contact-form

# 2. Claude Code で実装
claude
# → Claude Code が実装・テストを行い、PRを自動作成

# 3. GitHub でマージ
# → Vercel が自動でデプロイ
```

Claude Code が `gh pr create` まで自動でやってくれます。人間がやるのは「PR の内容を確認してマージボタンを押す」だけです。

### Dependabot のアップデート対応

毎週月曜日（設定次第）に Dependabot が依存パッケージのアップデート PR を自動作成します。

```
例）
PR: chore: bump astro from 4.15.0 to 4.16.0
PR: chore: bump @astrojs/react from 3.6.0 to 3.7.0
```

CI が通っていれば基本的にマージして問題ありません。CI を入れていない場合は自分でビルド確認が必要です（これが STEP 4 を推奨する理由のひとつです）。

---

## まとめ

| ツール | 役割 | コスト |
|--------|------|--------|
| Claude Code | AI による実装・PR 作成 | API 利用料のみ |
| GitHub | コード管理・品質チェック | 個人は無料 |
| Vercel | ホスティング・プレビューデプロイ | Hobby プランは無料 |

この環境を構築することで：

- **設計 → 実装 → PR → デプロイ** の流れが半自動化される
- バグを本番に入れる前に止める仕組みができる
- 「mainにマージ = リリース」という明確なルールで運用できる

実際にこの環境で HP を制作したところ、設計から本番公開まで **約3時間** で完了しました。手動でやれば 2〜3日かかる作業量です。

---

## 関連ログ

- `structured/tools/20260405_claude-code-hp-development.md` — Astro HP 制作の全検証記録
- `structured/tools/20260407_github-repo-security-setup.md` — GitHub セキュリティ設定の詳細
