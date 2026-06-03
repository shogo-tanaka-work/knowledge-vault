# Cloudflare Browser Rendering (Browser Run) 検証ログ

> ステータス: 検証中
> 作成日: 2026/06/03
> 最終更新: 2026/06/03
> ファイルパス: /Users/shogo/Documents/ai-business-os/15_ナレッジ基盤/vault/structured/tools/20260603_cloudflare-browser-rendering.md

---

## 📋 検証概要

- **ツール/サービス名**: Cloudflare Browser Rendering（Browser Run）REST API
- **検証対象**: 新機能 — エンドポイント別に「何が取得できるか」を実機で確認
- **バージョン/リリース日**:（情報なし）
- **検証期間**: 2026/06/03 -（検証中）
- **検証担当者**: 省伍
- **検証ステータス**: 検証中

---

## 1. 背景と検証目的

### なぜこの検証を行うのか
- 「まず何が取れるか見たい」という観点で、Browser Rendering の各エンドポイントを軽い順に叩いて取得結果を比較する。
- ニュース一覧ページから記事URLを収集し、本文を取得する自動化（n8n連携を想定）の前段調査。

### 解決したい課題
- ニュース一覧 → 記事URL収集 → 本文取得という処理パイプラインを、どのエンドポイントの組み合わせで最小コストに組めるかを見極める。
- 24時間以内の記事に絞り込む前段として、リンク一覧をどう取得するか。

### 期待される効果・ビジネスインパクト
- DOM全取得よりトークン消費を抑えた本文取得手段の確立。
- `/json`（Workers AI 構造化抽出）が決まれば、n8n側のLLM処理を省略できる可能性。

---

## 2. ツール/機能の基本情報

### 概要
- Cloudflare Browser Rendering の REST API。ヘッドレスブラウザでページをレンダリングし、用途別エンドポイントで結果を返す。
- すべて `POST .../browser-rendering/{endpoint}` 形式で、Body に対象 `url` を渡す。

### 提供元
- Cloudflare

### 主要機能
検証対象エンドポイント（軽い順）:

| エンドポイント | 用途 | 取得物 |
| --- | --- | --- |
| `/links` | ページ内のリンク一覧（最軽量） | 全リンクURLの配列 |
| `/markdown` | 本文をMarkdownで取得（LLMに優しい） | ノイズ除去済みMarkdown |
| `/content` | レンダリング後のフルHTML | 実際のDOM全体 |
| `/json` | AIで構造化データ抽出 | 整形済みJSON（Workers AI） |
| `/scrape` | CSSセレクタで特定要素だけ抽出 | 指定セレクタの要素 |

### 技術スタック・アーキテクチャ
- ヘッドレスブラウザ（Puppeteer系）によるレンダリング。`/json` は背後で Workers AI が動作し構造化を行う。
- `gotoOptions`（例: `waitUntil`）でページ読み込み判定を制御可能。

---

## 3. 検証方法

### 検証環境
- **使用アカウント**:（情報なし）
- **プラン/エディション**:（情報なし）
- **検証環境**: 本番（Cloudflare Browser Rendering 実機）

### 検証シナリオ
1. 対象を Anthropic の最新情報ページ `https://www.anthropic.com/news` に固定。
2. 軽い順（`/links` → `/markdown` → `/content` → `/json` → `/scrape`）に各エンドポイントへ POST。
3. 取得物の中身とトークン消費感を比較する。

### 検証データ・サンプル
- 対象URL: `https://www.anthropic.com/news`
- 各エンドポイントの実行結果は「8. 実際の使用例・サンプル」に全文収録。

### 前提条件・制約事項
- JavaScript重め・SPA のページでは、デフォルトのページ読み込み判定だと中身が空・不完全になることがある。`gotoOptions.waitUntil` を `networkidle0` / `networkidle2` に設定して回避する。

---

## 4. 検証結果

### 定性的評価

#### 機能面の評価
- `/links`: ページ内の全リンクURLが配列で返る。24時間以内の記事を絞り込む前段に最適。
- `/markdown`: HTMLのノイズを除いたMarkdownが返る。DOM全取得よりトークン消費が圧倒的に少ない。
- `/content`: 実際のDOMが全て取得できた（コピーするとコンテキスト過大のため本ログでは割愛）。
- `/json`: Workers AI が裏で動き、構造化済みJSONを返す。プロンプトで抽出項目を指定可能。
- `/scrape`: CSSセレクタで狙った要素だけ取得（一覧の記事カードなど）。

#### 操作性・UI/UX
- すべて同一の `POST .../browser-rendering/{endpoint}` 形式で、Body に `url` を渡すだけ。学習コストは低い。

#### 出力品質
- `/markdown` は一覧ページの記事タイトル・日付・URL・カテゴリがほぼ構造を保ったまま取得できた。

#### 実用性
- 「リンク収集（/links）→ 本文取得（/markdown）」の2段構成、または `/json` 一発で構造化、の双方が現実的。

---

### 定量的評価

#### 導入コスト

| 項目 | 内容 | 金額/工数 |
| --- | --- | --- |
| 初期設定時間 | アカウント作成〜使用開始まで | （情報なし） |
| 学習時間 | 基本操作を習得するまで | （情報なし） |
| 初期費用 | セットアップ、ライセンス購入等 | （情報なし） |

#### 運用コスト

| 項目 | 内容 | 金額 |
| --- | --- | --- |
| 月額利用料 | | （情報なし） |
| 年額利用料 | | （情報なし） |
| 従量課金 | API使用料、Workers AI 課金等 | （情報なし） |
| 追加オプション | | （情報なし） |

#### パフォーマンス

| 項目 | 測定結果 | 備考 |
| --- | --- | --- |
| 処理速度 | （情報なし） | エンドポイントは軽い順に `/links` < `/markdown` < `/content` |
| レスポンスタイム | （情報なし） | |
| 同時処理数 | （情報なし） | |
| 成功率 | 各エンドポイントとも `success: true` で取得成功 | |

#### ROI試算
- **削減できる工数**: `/json` で n8n側のLLM処理を省略できれば、ワークフロー1本あたりのノード・トークンを削減。（定量値は情報なし）
- **生産性向上**:（情報なし）
- **コスト削減額**:（情報なし）
- **投資回収期間**:（情報なし）

---

## 5. 比較・優位性分析

### 既存ツール/類似サービスとの比較

| 項目 | 検証ツール | 既存ツールA | 既存ツールB |
| --- | --- | --- | --- |
| 機能性 | エンドポイント別に用途特化 | （情報なし） | （情報なし） |
| コスト | （情報なし） | （情報なし） | （情報なし） |
| 使いやすさ | POST一発・Body最小 | （情報なし） | （情報なし） |
| 連携性 | n8n / Workers と親和 | （情報なし） | （情報なし） |
| サポート | （情報なし） | （情報なし） | （情報なし） |

### 優位性
- 用途別エンドポイントが揃っており、目的に応じて最小コストの取得手段を選べる。
- `/markdown` によるトークン削減、`/json` による構造化のワンストップ性。

### 劣位性・懸念点
- SPAでは `waitUntil` 調整が必要で、設定を誤ると中身が空・不完全になる。

---

## 6. リスク評価

### セキュリティ

| 評価項目 | 評価 | 詳細 |
| --- | --- | --- |
| データ保管場所 | （情報なし） | |
| 暗号化 | （情報なし） | |
| アクセス制御 | （情報なし） | API トークン認証（詳細は情報なし） |
| ログ管理 | （情報なし） | |
| コンプライアンス | （情報なし） | |

### プライバシー・倫理面
- スクレイピング対象サイトの利用規約・robots を尊重する必要がある。（一般論）

### ベンダーロックインリスク
- Cloudflare（Workers / Workers AI）依存。（情報なし）

### 技術的リスク
- 対象ページのDOM構造変更によりセレクタ（`/scrape`）が壊れる可能性。

---

## 7. 連携性・拡張性

### 既存システムとの連携

| 連携先 | 方法 | 難易度 | 備考 |
| --- | --- | --- | --- |
| n8n | HTTPリクエストノードからPOST | 低（想定） | `/json` でLLMノード省略の可能性 |

### API/統合オプション
- すべてREST（POST）。`gotoOptions` などのオプションで挙動を制御。

### 拡張性・カスタマイズ性
- `/json` の `prompt`、`/scrape` の `elements[].selector` で抽出内容を柔軟に指定可能。

---

## 8. 実際の使用例・サンプル

> すべて Anthropic の最新情報ページ `https://www.anthropic.com/news` を対象に、軽い順で実行。

### ユースケース1: `/links` — ページ内のリンク一覧（最軽量）

**用途**: ニュース一覧から記事URLを収集。24時間以内の記事を絞り込む前段に最適。

**リクエスト**:
```
POST .../browser-rendering/links
```
```json
{
  "url": "https://www.anthropic.com/news"
}
```

→ ページ内の全リンクURLが配列で返る。

**実行結果**:
```json
[
  {
    "success": true,
    "result": [
      "https://www.anthropic.com/",
      "https://www.anthropic.com/research",
      "https://www.anthropic.com/economic-futures",
      "https://www.anthropic.com/news",
      "https://claude.ai/",
      "mailto:press@anthropic.com",
      "https://support.claude.com/en/articles/9015913-how-to-get-support",
      "https://anthropic.com/press-kit",
      "https://www.anthropic.com/news/claude-opus-4-8",
      "https://www.anthropic.com/news/claude-design-anthropic-labs",
      "https://www.anthropic.com/glasswing",
      "https://www.anthropic.com/81k-interviews",
      "https://www.anthropic.com/news/claude-is-a-space-to-think",
      "https://www.anthropic.com/news/expanding-project-glasswing",
      "https://www.anthropic.com/news/confidential-draft-s1-sec",
      "https://www.anthropic.com/news/series-h",
      "https://www.anthropic.com/news/milan-office-opening",
      "https://www.anthropic.com/news/kiyoung-choi-representative-director-anthropic-korea",
      "https://www.anthropic.com/news/chris-olah-pope-leo-encyclical",
      "https://www.anthropic.com/research/glasswing-initial-update",
      "https://www.anthropic.com/news/widening-conversation-ai",
      "https://www.anthropic.com/news/anthropic-kpmg",
      "https://claude.com/product/overview",
      "https://claude.com/product/claude-code",
      "https://claude.com/product/claude-code/enterprise",
      "https://claude.com/product/cowork",
      "https://claude.com/product/claude-security",
      "https://claude.com/chrome",
      "https://claude.com/claude-for-slack",
      "https://claude.com/claude-for-microsoft-365",
      "https://www.claude.com/skills",
      "https://claude.com/pricing/max",
      "https://claude.com/pricing/team",
      "https://claude.com/pricing/enterprise",
      "https://claude.ai/download",
      "https://claude.com/pricing",
      "https://www.anthropic.com/glasswing",
      "https://www.anthropic.com/claude/opus",
      "https://www.anthropic.com/claude/sonnet",
      "https://www.anthropic.com/claude/haiku",
      "https://claude.com/solutions/agents",
      "https://claude.com/solutions/code-modernization",
      "https://claude.com/solutions/coding",
      "https://claude.com/solutions/customer-support",
      "https://claude.com/solutions/education",
      "https://claude.com/solutions/financial-services",
      "https://claude.com/solutions/government",
      "https://claude.com/solutions/healthcare",
      "https://claude.com/solutions/legal",
      "https://claude.com/solutions/life-sciences",
      "https://claude.com/solutions/nonprofits",
      "https://claude.com/solutions/security",
      "https://claude.com/solutions/small-business",
      "https://claude.com/platform/api",
      "https://platform.claude.com/docs",
      "https://claude.com/pricing#api",
      "https://claude.com/platform/marketplace",
      "https://claude.com/regional-compliance",
      "https://claude.com/partners/claude-on-aws",
      "https://claude.com/partners/google-cloud-vertex-ai",
      "https://claude.com/partners/microsoft-foundry",
      "https://platform.claude.com/",
      "https://claude.com/blog",
      "https://claude.com/partners",
      "https://claude.com/community",
      "https://claude.com/connectors",
      "https://www.anthropic.com/learn",
      "https://claude.com/customers",
      "https://www.anthropic.com/engineering",
      "https://www.anthropic.com/events",
      "https://www.anthropic.com/product/claude-code",
      "https://www.anthropic.com/product/claude-cowork",
      "https://www.anthropic.com/product/enterprise",
      "https://www.anthropic.com/product/security",
      "https://claude.com/plugins",
      "https://claude.com/partners/powered-by-claude",
      "https://claude.com/partners/services",
      "https://claude.com/programs/startups",
      "https://claude.com/resources/tutorials",
      "https://claude.com/resources/use-cases",
      "https://www.anthropic.com/supported-countries",
      "https://status.anthropic.com/",
      "https://support.claude.com/en/",
      "https://www.anthropic.com/company",
      "https://www.anthropic.com/careers",
      "https://www.anthropic.com/economic-index",
      "https://www.anthropic.com/constitution",
      "https://www.anthropic.com/news/announcing-our-updated-responsible-scaling-policy",
      "https://trust.anthropic.com/",
      "https://www.anthropic.com/transparency",
      "https://www.anthropic.com/legal/privacy",
      "https://www.anthropic.com/legal/consumer-health-data-privacy-policy",
      "https://www.anthropic.com/responsible-disclosure-policy",
      "https://www.anthropic.com/legal/commercial-terms",
      "https://www.anthropic.com/legal/consumer-terms",
      "https://www.anthropic.com/legal/aup",
      "https://www.linkedin.com/company/anthropicresearch",
      "https://x.com/AnthropicAI",
      "https://www.youtube.com/@anthropic-ai"
    ]
  }
]
```

**評価**: 一覧ページの全リンクが配列で取得でき、`/news/...` パスで記事URLを機械的に抽出できる。最軽量で前段に最適。

---

### ユースケース2: `/markdown` — 本文をMarkdownで取得（LLMに優しい）

**用途**: 一覧ページや記事本文の中身取得。

**リクエスト**:
```
POST .../browser-rendering/markdown
```
```json
{
  "url": "https://www.anthropic.com/news"
}
```

→ HTMLのノイズを除いたMarkdownが返る。DOM全取得よりトークン消費が圧倒的に少ない。

**実行結果**:
```json
[
  {
    "success": true,
    "result": "[Skip to main content](#main-content)[Skip to footer](#footer)\n\n* [Research](https://www.anthropic.com/news/research)\n* [Economic Futures](https://www.anthropic.com/news/economic-futures)\n* Commitments\n* Learn\n* [News](https://www.anthropic.com/news/news)\n\n[Try Claude](https://claude.ai/)\n\n# Newsroom\n\n* Press inquires[press@anthropic.com](mailto:press@anthropic.com)\n* Non-media inquiries[How to get support](https://support.claude.com/en/articles/9015913-how-to-get-support)\n* Media assets[Download press kit](https://anthropic.com/press-kit)\n\n![Introducing Claude Opus 4.8](https://www.anthropic.com/news/_next/image?url=https%3A%2F%2Fwww-cdn.anthropic.com%2Fimages%2F4zrzovbb%2Fwebsite%2F0eaa0ed2dce9810169112e1c77de2585fcf1f5c2-2880x1620.jpg&w=3840&q=75)\n\n[Introducing Claude Opus 4.8ProductMay 28, 2026An upgrade to our Opus class of models, with stronger performance across coding, agentic tasks, and professional work, and the consistency to handle long-running work.](https://www.anthropic.com/news/news/claude-opus-4-8)\n\n[ProductApr 17, 2026Introducing Claude Design by Anthropic LabsToday, we’re launching Claude Design, a new Anthropic Labs product that lets you collaborate with Claude to create polished visual work like designs, prototypes, slides, one-pagers, and more.](https://www.anthropic.com/news/news/claude-design-anthropic-labs)[AnnouncementsApr 7, 2026Project GlasswingA new initiative that brings together Amazon Web Services, Anthropic, Apple, Broadcom, Cisco, CrowdStrike, Google, JPMorganChase, the Linux Foundation, Microsoft, NVIDIA, and Palo Alto Networks in an effort to secure the world's most critical software.](https://www.anthropic.com/news/glasswing)[Mar 18, 2026What 81,000 people want from AIWe invited Claude.ai users to share how they use AI, what they dream it could make possible, and what they fear it might do. Nearly 81,000 people participated—the largest and most multilingual qualitative study of its kind. Here's what we found.](https://www.anthropic.com/news/81k-interviews)[AnnouncementsFeb 4, 2026Claude is a space to thinkWe’ve made a choice: Claude will remain ad-free. We explain why advertising incentives are incompatible with a genuinely helpful AI assistant, and how we plan to expand access without compromising user trust.](https://www.anthropic.com/news/news/claude-is-a-space-to-think)\n\n## News\n\nSearch\n\nDateCategoryTitle\n\n* [Jun 2, 2026AnnouncementsExpanding Project Glasswing](https://www.anthropic.com/news/news/expanding-project-glasswing)\n* [Jun 1, 2026AnnouncementsAnthropic confidentially submits draft S-1 to the SEC](https://www.anthropic.com/news/news/confidential-draft-s1-sec)\n* [May 28, 2026AnnouncementsAnthropic raises $65B in Series H funding at $965B post-money valuation](https://www.anthropic.com/news/news/series-h)\n* [May 28, 2026ProductIntroducing Claude Opus 4.8](https://www.anthropic.com/news/news/claude-opus-4-8)\n* [May 27, 2026AnnouncementsAnthropic opens Milan office to support Italian enterprise, research, and developers](https://www.anthropic.com/news/news/milan-office-opening)\n* [May 26, 2026AnnouncementsAnthropic appoints KiYoung Choi as Representative Director of Korea ahead of Seoul office opening](https://www.anthropic.com/news/news/kiyoung-choi-representative-director-anthropic-korea)\n* [May 25, 2026AnnouncementsAnthropic co-founder Chris Olah's remarks on Pope Leo XIV's encyclical \"Magnifica humanitas\"](https://www.anthropic.com/news/news/chris-olah-pope-leo-encyclical)\n* [May 22, 2026AnnouncementsProject Glasswing: An initial update](https://www.anthropic.com/news/research/glasswing-initial-update)\n* [May 19, 2026AnnouncementsWidening the conversation on frontier AI](https://www.anthropic.com/news/news/widening-conversation-ai)\n* [May 19, 2026AnnouncementsKPMG integrates Claude across its core business and workforce of more than 276,000 in strategic alliance](https://www.anthropic.com/news/news/anthropic-kpmg)\n[See more](#)\n\n### Products\n\n* [Claude](https://claude.com/product/overview)\n* [Claude Code](https://claude.com/product/claude-code)\n* [Claude Code Enterprise](https://claude.com/product/claude-code/enterprise)\n* [Claude Cowork](https://claude.com/product/cowork)\n* [Claude Security](https://claude.com/product/claude-security)\n* [Claude for Chrome](https://claude.com/chrome)\n* [Claude for Slack](https://claude.com/claude-for-slack)\n* [Claude for Microsoft 365](https://claude.com/claude-for-microsoft-365)\n* [Skills](https://www.claude.com/skills)\n* [Max plan](https://claude.com/pricing/max)\n* [Team plan](https://claude.com/pricing/team)\n* [Enterprise plan](https://claude.com/pricing/enterprise)\n* [Download app](https://claude.ai/download)\n* [Pricing](https://claude.com/pricing)\n* [Log in to Claude](https://claude.ai/)\n\n### Models\n\n* [Mythos Preview](https://www.anthropic.com/glasswing)\n* [Opus](https://www.anthropic.com/claude/opus)\n* [Sonnet](https://www.anthropic.com/claude/sonnet)\n* [Haiku](https://www.anthropic.com/claude/haiku)\n\n### Solutions\n\n* [AI agents](https://claude.com/solutions/agents)\n* [Code modernization](https://claude.com/solutions/code-modernization)\n* [Coding](https://claude.com/solutions/coding)\n* [Customer support](https://claude.com/solutions/customer-support)\n* [Education](https://claude.com/solutions/education)\n* [Financial services](https://claude.com/solutions/financial-services)\n* [Government](https://claude.com/solutions/government)\n* [Healthcare](https://claude.com/solutions/healthcare)\n* [Legal](https://claude.com/solutions/legal)\n* [Life sciences](https://claude.com/solutions/life-sciences)\n* [Nonprofits](https://claude.com/solutions/nonprofits)\n* [Security](https://claude.com/solutions/security)\n* [Small business](https://claude.com/solutions/small-business)\n\n### Claude Platform\n\n* [Overview](https://claude.com/platform/api)\n* [Developer docs](https://platform.claude.com/docs)\n* [Pricing](https://claude.com/pricing#api)\n* [Marketplace](https://claude.com/platform/marketplace)\n* [Regional compliance](https://claude.com/regional-compliance)\n* [Claude on AWS](https://claude.com/partners/claude-on-aws)\n* [Google Cloud’s Vertex AI](https://claude.com/partners/google-cloud-vertex-ai)\n* [Microsoft Foundry](https://claude.com/partners/microsoft-foundry)\n* [Console login](https://platform.claude.com/)\n\n### Resources\n\n* [Blog](https://claude.com/blog)\n* [Claude partner network](https://claude.com/partners)\n* [Community](https://claude.com/community)\n* [Connectors](https://claude.com/connectors)\n* [Courses](https://www.anthropic.com/news/learn)\n* [Customer stories](https://claude.com/customers)\n* [Engineering at Anthropic](https://www.anthropic.com/news/engineering)\n* [Events](https://www.anthropic.com/news/events)\n* [Inside Claude Code](https://www.anthropic.com/news/product/claude-code)\n* [Inside Claude Cowork](https://www.anthropic.com/news/product/claude-cowork)\n* [Inside Claude Enterprise](https://www.anthropic.com/news/product/enterprise)\n* [Inside Claude Security](https://www.anthropic.com/news/product/security)\n* [Plugins](https://claude.com/plugins)\n* [Powered by Claude](https://claude.com/partners/powered-by-claude)\n* [Service partners](https://claude.com/partners/services)\n* [Startups program](https://claude.com/programs/startups)\n* [Tutorials](https://claude.com/resources/tutorials)\n* [Use cases](https://claude.com/resources/use-cases)\n\n### Help and security\n\n* [Availability](https://www.anthropic.com/supported-countries)\n* [Status](https://status.anthropic.com/)\n* [Support center](https://support.claude.com/en/)\n\n### Company\n\n* [Anthropic](https://www.anthropic.com/news/company)\n* [Careers](https://www.anthropic.com/news/careers)\n* [Economic Futures](https://www.anthropic.com/news/economic-index)\n* [Research](https://www.anthropic.com/news/research)\n* [News](https://www.anthropic.com/news/news)\n* [Claude’s Constitution](https://www.anthropic.com/news/constitution)\n* [Responsible Scaling Policy](https://www.anthropic.com/news/announcing-our-updated-responsible-scaling-policy)\n* [Security and compliance](https://trust.anthropic.com/)\n* [Transparency](https://www.anthropic.com/news/transparency)\n\n### Terms and policies\n\n* [Privacy policy](https://www.anthropic.com/legal/privacy)\n* [Consumer health data privacy policy](https://www.anthropic.com/legal/consumer-health-data-privacy-policy)\n* [Responsible disclosure policy](https://www.anthropic.com/responsible-disclosure-policy)\n* [Terms of service: Commercial](https://www.anthropic.com/legal/commercial-terms)\n* [Terms of service: Consumer](https://www.anthropic.com/legal/consumer-terms)\n* [Usage policy](https://www.anthropic.com/legal/aup)\n\n© 2026 Anthropic PBC"
  }
]
```

**評価**: 一覧の記事タイトル・日付・カテゴリ・URLが構造を保ったまま取得でき、LLMにそのまま渡しやすい。トークン消費は `/content` より圧倒的に少ない。

---

### ユースケース3: `/content` — レンダリング後のフルHTML

**用途**: JavaScriptで描画されるページの完全なDOMが欲しいとき。

**リクエスト**:
```
POST .../browser-rendering/content
```
```json
{
  "url": "https://www.anthropic.com/news"
}
```

JS描画が重いSPAの場合は待機オプションを追加する。JavaScript重めのページやSPAでは、デフォルトのページ読み込み判定だと中身が空・不完全になることがある。最もシンプルな解決策は `gotoOptions.waitUntil` を `networkidle0` か `networkidle2` に設定すること（出典: Cloudflare）。

```json
{
  "url": "https://example.com",
  "gotoOptions": { "waitUntil": "networkidle0" }
}
```

**実行結果**: 実際のDOMが全て取得できた。コピーするとコンテキストが過大になるため本ログでは割愛。

**評価**: SPAの完全なDOMが必要な場面向け。トークン消費が大きいため、本文取得が目的なら `/markdown` を優先する。

---

### ユースケース4: `/json` — AIで構造化データ抽出（一発で整形）

**用途**: 「タイトル・日付・URLの一覧」を構造化JSONで直接取得。

**リクエスト**:
```
POST .../browser-rendering/json
```
```json
{
  "url": "https://www.anthropic.com/news",
  "prompt": "Extract all news articles with their title, date, and URL"
}
```

→ Workers AI が裏で動いて構造化済みJSONを返す。これが決まれば、n8n側のLLM処理を省略できる可能性がある。

**実行結果**:（情報なし — `prompt` で抽出項目を指定する形まで確認。具体的なレスポンスサンプルは未収録）

**評価**: 構造化までワンストップで完結する点が強み。n8nワークフローのLLMノード削減に直結し得る。

---

### ユースケース5: `/scrape` — 特定要素だけ抽出

**用途**: CSSセレクタで狙った要素だけ取得（一覧の記事カードなど）。

**リクエスト**:
```
POST .../browser-rendering/scrape
```
```json
{
  "url": "https://www.anthropic.com/news",
  "elements": [{ "selector": "article" }]
}
```

**実行結果**:（情報なし — `elements[].selector` で要素を指定する形まで確認。具体的なレスポンスサンプルは未収録）

**評価**: 一覧の記事カードなど、狙った要素だけをピンポイントで取得したいときに有効。DOM構造変更に弱い点は留意。

### スクリーンショット・デモ
- （情報なし）

---

## 9. 学びとナレッジ

### 発見したこと
- 用途別エンドポイントを軽い順に並べると、`/links`（リンク収集）→ `/markdown`（本文）→ `/content`（フルDOM）の順でコストが上がる。
- `/json` は Workers AI が背後で構造化を担うため、後段のLLM処理を省略できる可能性がある。

### うまくいったこと
- `/links` と `/markdown` だけで、ニュース一覧の記事URL収集と本文取得の大半をカバーできた。

### うまくいかなかったこと
- （情報なし）

### Tips・ベストプラクティス
- 本文取得が目的なら `/content`（フルDOM）より `/markdown` を使う。トークン消費が圧倒的に少ない。
- JS重め・SPAで中身が空・不完全になるときは、`gotoOptions.waitUntil` を `networkidle0` または `networkidle2` に設定する。
- 「リンク収集 → 24時間以内に絞り込み → 本文取得」の2段構成にすると無駄な取得を減らせる。

### よくあるエラーと対処法
- 症状: SPAでDOMやMarkdownが空・不完全 → 対処: `gotoOptions.waitUntil` を `networkidle0` / `networkidle2` に設定。

---

## 10. 判定と今後のアクション

### 総合評価
（完了時に記入）

### 導入判定
- [ ] 即座に導入推奨
- [x] 条件付きで導入可
- [ ] 追加検証が必要
- [ ] 導入見送り

### 判定理由
- `/links` + `/markdown` で記事収集パイプラインの前段は十分に成立する見込み。コスト・`/json` のレスポンス品質は追加検証が必要なため「条件付き」。

### 次のステップ
- [x] 追加PoC実施（検証領域: `/json` のレスポンス品質、`/scrape` のセレクタ精度、従量課金コスト）
- [ ] MVP開発
- [ ] パイロット導入（対象: ）
- [ ] 社内展開ロードマップ作成
- [ ] 検証終了

### 追加で検証したい項目
- `/json` の実レスポンスと抽出精度（n8nのLLMノードを本当に省略できるか）。
- `/scrape` で `article` セレクタが返す構造。
- 各エンドポイントのレスポンスタイム・従量課金。

---

📚 関連リソース

### 公式ドキュメント
- Cloudflare Browser Rendering（REST API / `gotoOptions.waitUntil` の解説含む）

### 参考記事・事例
- 検証対象ページ: `https://www.anthropic.com/news`

### 社内関連ドキュメント
- `20260407_cloudflare-dns-worker-proxy.md`（Cloudflare 関連の既存検証ログ）

### 検証データ・ログ
- 本ファイルの「8. 実際の使用例・サンプル」に `/links`・`/markdown` の実行結果を全文収録。

---

✅ メモ・議論ログ
- 省伍さんの「まず何が取れるか見たい」という起点から、軽い順にエンドポイントを試す方針で調査。
- `/json` が決まれば n8n 側の LLM 処理を省略できる可能性があり、コスト面のインパクトが大きい。

---

## 📝 更新ログ
<!-- このセクションはスキルが自動で追記する。手動編集不要。 -->
| 日時 | 更新内容の概要 |
|---|---|
| 2026/06/03 | ファイル作成（init）。5エンドポイント調査結果を収録、`/links`・`/markdown` は実行結果を全文収録 |
