# Note記事 ダッシュボード

> 記事の原本は `structured/articles/` に格納。
> ここ（`outputs/note/`）にはNote向けに変換された成果物、またはシンボリックリンクを配置する。
> ステータスは各記事のフロントマター `status` フィールドが正。

## ステータス定義

| ステータス | 意味 |
|:---:|:---|
| `draft` | 執筆中・初稿 |
| `review` | レビュー待ち・推敲中 |
| `ready` | 公開準備完了（スクショ追加等の最終仕上げ済み） |
| `published` | 公開済み（`published_url` にリンクあり） |
| `archived` | 廃止・統合済み |

---

## 記事一覧

### Google広告 x MCP 実践ガイド（3記事シリーズ）

原本: `structured/articles/google-ads-mcp/`

| # | タイトル | ステータス | 更新日 |
|:---:|:---|:---:|:---:|
| 1 | [動機と認証地獄](../../structured/articles/google-ads-mcp/01-motivation-and-auth.md) | `draft` | 2026-04-05 |
| 2 | [ローカルMCPサーバー構築](../../structured/articles/google-ads-mcp/02-local-mcp-server.md) | `draft` | 2026-04-05 |
| 3 | [リモートMCPサーバー構築](../../structured/articles/google-ads-mcp/03-remote-mcp-server.md) | `draft` | 2026-04-05 |
| - | [初期ドラフト（統合前）](../../structured/articles/google-ads-mcp/remote-mcp-server-article.md) | `archived` | 2026-04-05 |

---

## データフロー

```
structured/articles/  (原本)
        ↓  publishスキルで変換
outputs/note/         (Note向け成果物 or シンボリックリンク)
        ↓  シンボリックリンク
プロジェクト/docs/note/ (参照)
```
