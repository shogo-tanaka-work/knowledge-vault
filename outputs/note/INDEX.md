# Note記事 ダッシュボード

> 記事の原本は `structured/articles/` に格納。
> ここ（`outputs/note/`）にはNote向けに変換された成果物、またはシンボリックリンクを配置する。
> ステータスは各記事のフロントマター `status` フィールドが正。
> **発信戦略の正本**: [`structured/articles/note-publishing-strategy.md`](../../structured/articles/note-publishing-strategy.md)

## ステータス定義

| ステータス | 意味 |
|:---:|:---|
| `draft` | 執筆中・初稿 |
| `review` | レビュー待ち・推敲中 |
| `ready` | 公開準備完了（スクショ追加等の最終仕上げ済み） |
| `published` | 公開済み（`published_url` にリンクあり） |
| `archived` | 廃止・統合済み |

## キーワード戦略タグ定義

| タグ | 意味 |
|:---:|:---|
| `niche` | ニッチ深掘り型（3語複合・資産記事・月2本） |
| `trend` | トレンド瞬発型（新ツール発表当日〜翌日・月2-3本） |
| `evergreen` | 既存資産で恒久流入を狙うリライト対象 |

---

## 記事一覧

### Google広告 x MCP 実践ガイド（3記事シリーズ）

原本: `structured/articles/google-ads-mcp/`
ターゲットキーワード: `Google広告 MCP 構築` / `Google Ads API ローカルMCP` / `リモートMCPサーバー Cloudflare`

| # | タイトル | ステータス | 戦略 | 月間検索数 | 公開後順位 | 更新日 |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|
| 1 | [動機と認証地獄](../../structured/articles/google-ads-mcp/01-motivation-and-auth.md) | `draft` | `niche` | - | - | 2026-04-05 |
| 2 | [ローカルMCPサーバー構築](../../structured/articles/google-ads-mcp/02-local-mcp-server.md) | `draft` | `niche` | - | - | 2026-04-05 |
| 3 | [リモートMCPサーバー構築](../../structured/articles/google-ads-mcp/03-remote-mcp-server.md) | `draft` | `niche` | - | - | 2026-04-05 |
| - | [初期ドラフト（統合前）](../../structured/articles/google-ads-mcp/remote-mcp-server-article.md) | `archived` | - | - | - | 2026-04-05 |

### 検証ラボ由来の記事（単発）

検証ログ（`structured/projects/`）から展開した記事。原本は `outputs/note/` に直接配置。

| タイトル | ステータス | 元検証ログ | 更新日 |
|:---|:---:|:---|:---:|
| [LINEサポートのFAQ対応をAI化してみた](20260522_line-gas-spreadsheet-rag.md) | `draft` | `20260520_line-gas-spreadsheet-rag.md` | 2026-05-22 |
| [YouTube検索トレンドの収集を、Claude CodeとBrowser Use CLIで1コマンドにした話](20260524_browser-use-cli-youtube-trend.md) | `draft` | `tools/20260514_sns-research-automation.md` | 2026-05-24 |
| [AIに任せて、自分用のiOSアプリを実機まで作ってみた](20260601_claude-code-ios-app.md) | `draft` | `projects/20260601_claude-code-ios-app.md` | 2026-06-01 |
| [数ヶ月検索に出なかった自社サイトを、Google検索とAI検索の両方に乗せた話](20260601_cloudflare-ai-search-seo.md) | `draft` | `16_検証ラボ/lab-shogoworks-search-aio/20260601_shogoworks-search-aio.md` | 2026-06-01 |
| [バイブコーディングでVercelに載せて終わり、にしていませんか。$20のはずが$132だった請求書の話](20260602_vercel-cost-vibe-coding.md) | `draft` | `tools/20260602_vercel-cost-build-management.md` | 2026-06-02 |

---

## データフロー

```
structured/articles/  (原本)
        ↓  publishスキルで変換
outputs/note/         (Note向け成果物 or シンボリックリンク)
        ↓  シンボリックリンク
プロジェクト/docs/note/ (参照)
```
