---
title: LINE×GAS×スプレッドシート簡易RAG｜X単発投稿案（無料プラン140字版）
status: draft
created: 2026-05-22
updated: 2026-05-22
type: case-study
related:
  - structured/projects/20260520_line-gas-spreadsheet-rag.md
medium: x
target_cta: note記事
constraints:
  - 無料プラン想定。1投稿140字以内（日本語）
  - 煽り表現は使わない
  - 進行中の検証であり、精度評価は未完了。誇張しない
  - 詳細はnote記事または技術ブログへ誘導
---

# X単発投稿案：LINE×GAS×スプレッドシート簡易RAG

5パターンの単発投稿案。案A〜Dはnote記事へ、案Eは技術ブログへ誘導する。
投稿時にURL（`[note URL]` / `[tech-blog URL]`）を差し替える。

---

## 案A：シンプル告知型（note誘導）

```
LINEのFAQ対応を、DifyなしでGASとスプレッドシートだけでAI化してみました。質問の意味をベクトルで捉えて近いFAQを返す簡易RAG構成です。作った理由とハマりどころはnoteにまとめました。

→ [note URL]
```

---

## 案B：数字提示型（note誘導）

```
DifyなしのLINEチャットボットを検証中。質問を1536次元のベクトルに変換→類似度検索→LLM判定の三段構えで、無関係な質問にはあえて答えない設計にしました。応答は数秒で完結。詳細はnoteに書いています。

→ [note URL]
```

---

## 案C：仕組み一行説明型（note誘導）

```
LINE Webhook → GASのdoPostで直接受け → OpenAIで埋め込み → スプレッドシート全行とコサイン類似度 → gpt-5-miniで最終判定。Difyを介さない簡易RAGの構成と判断の理由をnoteにまとめました。

→ [note URL]
```

---

## 案D：用途提示型（note誘導）

```
同じFAQに何度も答える運用、地味にしんどい。LINEのサポート一次対応を、運用担当者がスプレッドシートだけで完結できる形でAI化してみました。Difyなしの構成です。仕組みと設計の判断はnoteに。

→ [note URL]
```

---

## 案E：技術ブログ誘導型（tech-blog誘導）

```
GASのdoPostはHTTPヘッダを読めず、LINE公式の署名検証が実装できない——など、GAS×LINE×OpenAIで簡易RAGを組むときのハマりどころを技術記事にまとめました。差分検知や再送ループ対策も。

→ [tech-blog URL]
```

---

## 運用メモ

- 案A〜Dはnote記事へ、案Eは技術ブログ（Zenn/Qiita）へ誘導
- 投稿時間の目安：平日の朝7〜8時台、または夜21時台
- ハッシュタグは入れないか、入れても1個まで（例：`#GAS`）
- 進行中の検証のため「精度が高い」等の断定は避け、「検証中」「中間報告」のトーンを保つ
- 煽り表現・誇張は使わない
