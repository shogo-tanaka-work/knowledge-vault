# Anthropic ニュースルーム 自動クローリング 設計まとめ

> 作成日：2026-04-28  
> 目的：anthropic.com/news を定期収集し、Discord/Notion等へ自動通知する

---

## 1. 前提調査結果

### RSSの現状

| ソース | 状況 |
|--------|------|
| Anthropic 公式RSS | **非公開**（存在しない） |
| RSSHub `rsshub.app/anthropic/news` | **403エラー**（アクセス不可） |
| Olshansk/rss-feeds（GitHub） | **2025年11月で更新停止**（約5ヶ月放置） |

**結論：既存の非公式RSSは実用上使えない。HTML直接fetchが現実解。**

### 直接fetchの可否確認

| URL | 結果 |
|-----|------|
| `https://www.anthropic.com/news` | ✅ 取得可（HTMLにURL・タイトル・日付が含まれる） |
| `https://www.anthropic.com/news/claude-opus-4-7` | ✅ 本文取得可 |

---

## 2. クローリング設計（二段構えfetch）

### フロー

```
STEP 1: 一覧ページ取得
  GET https://www.anthropic.com/news
    └─ /news/xxxxx 形式のURLを全抽出
    └─ 日付をパースして「直近1年」でフィルタ

STEP 2: 各記事ページを個別取得
  GET https://www.anthropic.com/news/{slug}
    └─ 本文（<p>タグ）を抽出
    └─ タイトル・日付・本文サマリーを構造化
```

### 直近取得できた記事（2026年4月時点）

| 日付 | タイトル | URL |
|------|---------|-----|
| 2026-04-24 | An update on our election safeguards | `/news/election-safeguards-update` |
| 2026-04-24 | Anthropic and NEC collaborate | `/news/anthropic-nec` |
| 2026-04-20 | Anthropic and Amazon expand collaboration | `/news/anthropic-amazon-compute` |
| 2026-04-17 | Introducing Claude Design by Anthropic Labs | `/news/claude-design-anthropic-labs` |
| 2026-04-16 | Introducing Claude Opus 4.7 | `/news/claude-opus-4-7` |

---

## 3. アーキテクチャ

### 採用構成

```
外部Cron（cron-job.org / GitHub Actions）
  └─ HTTP GET → Cloudflare Worker（HTTPリクエストで起動）
        ├─ STEP1: anthropic.com/news をfetch → URL一覧抽出
        ├─ STEP2: 各記事URLをfetch → 本文抽出
        ├─ KV: 既取得済みURLを管理（重複通知防止）
        └─ Discord Webhook / Notion API へ通知
```

### なぜこの構成か

- **Cloudflare Workers Free** は常駐プロセスではなく、HTTPリクエストで起動する V8 Isolate
- **node-cron は使えない**（常駐プロセスが存在しないため）
- **Cron Trigger（CF側）は無料プランで5個/アカウントまで**→ 温存したい場合は外部Cronで代替
- **外部CronからWorkerのURLを叩く**ことでCron Trigger消費をゼロにできる

---

## 4. Cloudflare Workers 無料プランの制限

| 項目 | Free | Paid（$5/月〜） |
|------|------|----------------|
| Workerアプリ数 | **100個** | 500個 |
| リクエスト数 | 100,000回/日 | 無制限 |
| CPU時間 | 10ms/リクエスト | 最大5分 |
| **Cron Trigger数** | **5個/アカウント** | 250個 |
| KV読み取り | 100,000回/日 | 従量 |
| Worker容量 | 3MB | 10MB |

> 今回のニュースクローラーは1 Worker消費、Cron Trigger消費ゼロ（外部Cron使用）

---

## 5. Cron Trigger 回避方法

### node-cronは使えない（理由）

```
❌ 一般サーバー：Node.jsプロセスが常駐 → node-cronがタイマー管理
✅ Cloudflare Workers：リクエスト来たときだけ起動 → 常駐プロセス自体が存在しない
```

### 回避策：外部CronでWorkerを叩く

| サービス | 無料枠 | 備考 |
|---------|--------|------|
| **cron-job.org** | 無制限 | UIでURL登録するだけ。最速 |
| **GitHub Actions** `schedule:` | 無制限（public repo）| yml1ファイルで完結 |
| **n8n Schedule Trigger** | 既存環境あり | 既存フローに追加するだけ |

---

## 6. 実装方針（決定事項）

- **実行環境**：Cloudflare Workers（既存 `shogo-works` アカウント）
- **Cron管理**：cron-job.org または GitHub Actions（CF Cron Triggerは使わない）
- **データ取得**：二段fetch（一覧 → 個別記事）
- **重複管理**：Workers KV に取得済みURLをキャッシュ
- **通知先**：Discord Webhook（または Notion API）
- **フィルタ**：直近1年以内の記事のみ対象

---

## 7. 次のステップ

- [ ] Cloudflare Worker コード実装
- [ ] KV Namespace 作成（重複管理用）
- [ ] cron-job.org または GitHub Actions 設定
- [ ] 通知先（Discord/Notion）Webhook設定
- [ ] 動作確認・本番デプロイ
