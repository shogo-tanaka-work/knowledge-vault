---
title: Cloudflare/Astroサイトを検索・AI検索に乗せた話｜X単発投稿案（140字版）
status: draft
created: 2026-06-01
updated: 2026-06-01
type: how-to
related:
  - 16_検証ラボ/lab-shogoworks-search-aio/20260601_shogoworks-search-aio.md
  - outputs/note/20260601_cloudflare-ai-search-seo.md
medium: x
target_cta: note記事
constraints:
  - 無料プラン想定。1投稿140字以内（日本語）
  - 煽り表現は使わない
  - 詳細はnote記事へ誘導
---

# X単発投稿案（140字以内・note誘導型）

すべて単発で完結し、続きを読みたい人だけがnoteに飛ぶ動線。反応を見ながらA/Bで使い分ける。

note記事URL（差し替え）: `https://note.com/<account>/<slug>`

---

## 案A: シンプル告知型

```
数ヶ月Google検索に出なかった自社サイトを、検索とAI検索の両方に乗せました。原因はSearch Console未登録と、Cloudflareがrobots.txtを二重管理してAIクローラーをブロックしていたこと。手順と詰まりどころはnoteに。

→ [note URL]
#AIO #SEO
```

## 案B: ハマりどころ型

```
robots.txtを直してもデプロイのたびAIクローラーのブロックが復活する沼にハマった。犯人はCloudflareのAI Crawl Control「Managed robots.txt」。OFFにしたら自分の設定が反映された。効かない時は二重管理を疑う。

→ [note URL]
#Cloudflare #SEO
```

## 案C: AIO論点型

```
AI検索時代のrobots.txtは全許可・全拒否じゃない。search=yes / ai-input=yes / ai-train=no で、検索とAI検索の引用はOK・学習はNOと粒度で宣言できる。自社サイトをAIに引用させる設計、やってますか。

→ [note URL]
#AIO #LLMO
```

## 案D: 見落とし注意型

```
公開しただけのサイトは検索に出ません。被リンク0だと自然クロールも来ない。Search Consoleへの能動登録とサイトマップ送信で788ページ検出・成功。新規ドメインの最初の一歩、地味だけど必須でした。

→ [note URL]
#SEO #AIO
```

---

## 運用メモ

- 案A〜Dは単発で完結。反応を見て使い分ける（技術寄せ=B、論点寄せ=C、汎用=A/D）
- 各案140字以内（リンク・ハッシュタグ込みで調整）。投稿時に文字数を再確認する
- CTAリンクは公開後に差し替え。図版（Search Console 788ページ成功／Cloudflare設定画面）を添えると伸びやすい
- ハッシュタグは2個まで。多用しない
