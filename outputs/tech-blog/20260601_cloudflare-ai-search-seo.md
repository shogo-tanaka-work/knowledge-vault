---
title: Cloudflare Pages の Astro サイトが Google にも AI検索にも出ない原因は robots.txt の二重管理だった
status: draft
created: 2026-06-01
updated: 2026-06-01
type: tech-tutorial
related:
  - 16_検証ラボ/lab-shogoworks-search-aio/20260601_shogoworks-search-aio.md
medium: tech-blog
target_cta: shogoworks.com
target_platforms:
  - Zenn
  - Qiita
---

# Cloudflare Pages の Astro サイトが Google にも AI検索にも出ない原因は robots.txt の二重管理だった

## TL;DR

- Cloudflare Pages + Squarespace ドメインで公開した Astro サイトが、数ヶ月たっても `site:` 検索で0件だった
- 原因は2つ重なっていた
  - **Google検索に出ない**：Search Console 未登録 + 被リンク0で自然クロールが一度も来ていなかった
  - **AI検索に出ない**：Cloudflare の AI Crawl Control「Managed robots.txt」が、ソースの `public/robots.txt` を上書きして AIクローラーをブロックし続けていた
- 解決は、Search Console への能動登録 + `@astrojs/sitemap` 導入 + Cloudflare の Managed robots.txt を OFF + Content-Signal で粒度制御
- robots.txt を `search=yes, ai-input=yes, ai-train=no` で宣言し、AI検索の引用は許可・学習データ収集は拒否、の両取りにした

環境：Astro / Cloudflare Pages / Squarespace（ドメイン）/ ナレッジ788ページのサービスサイト。

## 課題設定

公開済みの Astro サイト（shogoworks.com）が、DNS 割り当てから数ヶ月たっても Google 検索に出てこない。サイト自体はブラウザで正常に表示される。`site:shogoworks.com` を叩くと0件。

調べていくと、Google検索の問題と AI検索（ChatGPT・Gemini・Claude 等）の問題が別々に存在していた。順に潰していく。

## 前提のアーキテクチャ

```
[ Astro ] --build--> 静的アセット
     |
     v
[ Cloudflare Pages ] -- ホスティング
     |  └ AI Crawl Control（Managed robots.txt を自動挿入しうる）
     v
[ Squarespace ドメイン ] -- DNS は Cloudflare 側で管理（TXT等）
     |
     v
[ Google Search Console ] -- インデックスの入口
```

| レイヤ | 採用 | 役割 |
|---|---|---|
| フレームワーク | Astro | 静的サイト生成、`@astrojs/sitemap` |
| ホスティング | Cloudflare Pages | 配信 + AI Crawl Control |
| ドメイン | Squarespace | 所有・DNS は Cloudflare で管理 |
| 検索登録 | Google Search Console | クロール・インデックスの起点 |

## 問題1：Google検索にヒットしない

### 症状

`site:shogoworks.com` が0件。サイトは正常表示。

### 原因

Search Console に未登録だった。新規ドメインで被リンクが0件だと、Google のクローラーが存在を知る手がかりがなく、自然クロールが一度も来ない。Search Console では `前回のクロール: 該当なし` と表示されていた。

公開しただけでは見つけてもらえない。能動的に存在を知らせる必要がある。

### 解決手順

**① Search Console にドメインを登録**

```
https://search.google.com/search-console
→ プロパティタイプ「ドメイン」で shogoworks.com を登録
→ Cloudflare の DNS に TXT レコードを追加して所有権を確認
```

**② インデックス登録をリクエスト**

```
URL検査 → https://shogoworks.com/ → インデックス登録をリクエスト
```

**③ サイトマップを生成する（Astro）**

`/sitemap.xml` が404だったため `@astrojs/sitemap` を導入する。

```bash
npm install @astrojs/sitemap
```

```js
// astro.config.mjs
import { defineConfig } from 'astro/config'
import sitemap from '@astrojs/sitemap'

export default defineConfig({
  site: 'https://shogoworks.com', // ← これが無いと sitemap が生成されない
  integrations: [sitemap()],
})
```

`site` オプションを忘れると sitemap が出力されない。ここはハマりやすい。

**④ サイトマップを送信する**

Astro が出力するのは `sitemap.xml` ではなく `sitemap-index.xml` である点に注意する。

```
Search Console → サイトマップ → https://shogoworks.com/sitemap-index.xml を送信
```

結果は788ページ検出、ステータス「成功」だった。

## 問題2：AI検索（ChatGPT・Gemini・Claude）にヒットしない

### 症状

`public/robots.txt` を書き換えて ClaudeBot・GPTBot・Google-Extended を解放しても、デプロイのたびに次のブロックが復活する。

```
User-agent: ClaudeBot
Disallow: /

User-agent: GPTBot
Disallow: /

User-agent: Google-Extended
Disallow: /
```

### つまずいたポイント

正しく書いてデプロイしても、ブラウザで確認すると毎回 Cloudflare の自動生成ブロックが先頭に追記され、自分の設定と混在していた。

```
# BEGIN Cloudflare Managed content   ← 消えない
User-agent: ClaudeBot
Disallow: /
...
# END Cloudflare Managed Content

# ↓ 自分が書いた設定（後ろに追記される）
User-agent: *
Allow: /
```

robots.txt は上から順に評価されるため、後半の Allow より先頭の Disallow が勝ってしまう。これで AIクローラーがブロックされ続けていた。

### 根本原因

Cloudflare の **AI Crawl Control「Managed robots.txt」機能が ON** になっていた。これは人間が見る robots.txt とは別に、AIクローラー向けの robots.txt を Cloudflare が自動生成して挿入する機能で、ソースの robots.txt を書いても上書きされる。

### 解決手順

```
Cloudflare Dashboard
→ 対象ドメインを選択
→ Security → AI Crawl Control
→ Managed robots.txt → OFF
```

OFF にすると `public/robots.txt` がそのまま反映された。

### 最終的な robots.txt

```
User-agent: *
Content-Signal: search=yes,ai-input=yes,ai-train=no
Allow: /

User-agent: CCBot
Disallow: /

User-agent: Amazonbot
Disallow: /

User-agent: Bytespider
Disallow: /

User-agent: Applebot-Extended
Disallow: /

Sitemap: https://shogoworks.com/sitemap-index.xml
```

| Bot | 設定 | 意図 |
|-----|------|------|
| ClaudeBot | Allow | Claude検索への引用を許可 |
| GPTBot | Allow | ChatGPT検索への引用を許可 |
| Google-Extended | Allow | Gemini検索への引用を許可 |
| CCBot | Disallow | 学習データ収集をブロック |
| Amazonbot | Disallow | 学習データ収集をブロック |
| Bytespider | Disallow | 学習データ収集をブロック |
| Applebot-Extended | Disallow | 学習データ収集をブロック |

`Content-Signal: search=yes, ai-input=yes, ai-train=no` は、検索インデックスと RAG・検索グラウンディングは許可しつつ、学習データ利用は拒否する宣言になる。全許可・全拒否の二択ではなく、用途ごとに粒度を分けられる。

## Managed robots.txt を OFF にする判断

### メリット

- `public/robots.txt` がそのまま反映され、意図どおりのクローラー制御ができる
- `Content-Signal: ai-input=yes` で RAG・検索グラウンディングへの許可を標準化された形式で宣言できる
- robots.txt にサイトマップURLを含められ、AIクローラーのページ発見効率が上がる
- ChatGPT・Gemini・Perplexity・Claude などの AI検索で引用・回答候補に入る可能性が高まる
- AI学習はNO・AI検索はYESという粒度の権利管理ができる

### 注意点

- Cloudflare の自動保護が外れるため、robots.txt の管理が完全に自己責任になる
- 設定ミスで意図しないクローラーを解放・ブロックするリスクがある
- 新しい AIクローラーが登場したら手動で追記対応が要る
- AIクローラーへの解放でサーバー負荷が増える可能性がある（Cloudflare Pages 利用なら通常は許容範囲）
- 自社コンテンツが競合の AIツールに引用されうる点も理解して設定する

## 計測・結果

- サイトマップ検出ページ数：788、送信ステータス「成功」
- `public/robots.txt` の内容が反映され、AIクローラー向けブロックの混在を解消
- Google検索・AI検索の双方に対して、クロール許可とページ発見の経路を確立

ハマりポイントを一覧で残す。

| # | 症状 | 原因 | 対処 |
|---|---|---|---|
| 1 | `site:` 検索が0件 | Search Console 未登録・被リンク0で自然クロール未到達 | ドメイン登録＋所有権確認＋インデックス登録リクエスト |
| 2 | `/sitemap.xml` が404 | `@astrojs/sitemap` 未導入、`site` 未設定 | 導入し `astro.config.mjs` に `site` を設定 |
| 3 | サイトマップ送信が通らない | Astro の出力は `sitemap-index.xml` | `sitemap-index.xml` を送信 |
| 4 | robots.txt の AIブロックが復活 | Cloudflare AI Crawl Control の Managed robots.txt が ON | Managed robots.txt を OFF |
| 5 | Allow より Disallow が優先 | robots.txt は上から評価される | 先頭の自動ブロックを排除し、自前の設定だけにする |

## 横展開

この一連は、Astro + Cloudflare Pages 構成の他サイトにそのまま使えるチェックリストになる。新規サイト公開時に「Search Console 能動登録」「sitemap-index 送信」「Cloudflare の AI 機能の状態確認」をテンプレ化しておくと、同じ数ヶ月の空白を二度と作らずに済む。

## まとめ

「設定したのに効かない」ときは、設定が二重管理されていないかを疑うとよい。今回は Cloudflare が robots.txt を二重に持っていた。あわせて、新規ドメインは公開しただけでは見つからないので Search Console への能動登録が要る。そして AI検索時代の robots.txt は、全許可・全拒否ではなく `search` / `ai-input` / `ai-train` の粒度で、検索・AI検索・学習利用を個別にコントロールするのが要点になる。

---

Zenn 用タグ: `Cloudflare` `Astro` `SEO` `robotstxt` `AI検索`
Qiita 用タグ: `Cloudflare` `Astro` `SEO` `SearchConsole` `LLMO`
