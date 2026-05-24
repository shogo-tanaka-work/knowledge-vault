---
title: Claude Code × Browser Use CLI で YouTube トレンド取得｜X単発投稿案（無料プラン140字版）
status: draft
created: 2026-05-24
updated: 2026-05-24
type: case-study
related:
  - structured/tools/20260514_sns-research-automation.md
  - .claude/skills/browser-use-googletrends/SKILL.md
medium: x
target_cta: note記事（案A〜D） / 技術ブログ記事（案E）
format: plain-text（マークダウン非対応のため、投稿時は各案の「投稿本文」だけをコピペする）
constraints:
  - 無料プラン想定。1投稿140字以内（日本語）
  - 煽り表現は使わない
  - 詳細はnote記事または技術ブログへ誘導
  - 2026年のXアルゴリズムはハッシュタグ推薦効果がほぼ消滅。本文キーワードと滞在時間が重視される
---

# X単発投稿案：Claude Code × Browser Use CLI で YouTube トレンド取得

5パターンの単発投稿案。案A〜Dはnote記事へ、案Eは技術ブログへ誘導する。
投稿時にURL（`[note URL]` / `[tech-blog URL]`）を差し替える。

---

## 案A：シンプル告知型（note誘導）

投稿本文 ↓

Google トレンドのYouTube検索トレンド取得を、Claude Code経由のBrowser Use CLIで自動化しました。ブラウザを開いてテキストを抜くまでをコマンド一発で。仕組みと使い所をnoteにまとめています。

→ [note URL]

---

## 案B：数字提示型（note誘導）

投稿本文 ↓

YouTubeトレンド取得を4ステップでCLI化。
①Trendsを期間指定で開く
②12秒待機
③innerTextを取得
④ブラウザを閉じる
Browser Use CLIをClaude Codeから呼ぶだけ。背景はnoteに。

→ [note URL]

---

## 案C：仕組み一行説明型（note誘導）

投稿本文 ↓

browser-use open でGoogle トレンドを開いて、sleep後にtitle確認、document.body.innerTextで一括取得、close。スクレイパーを書かずにLLMにブラウザを操らせる構成です。判断の経緯はnoteに。

→ [note URL]

---

## 案D：用途提示型（note誘導）

投稿本文 ↓

企画前にYouTubeで何が伸びているか眺める作業、毎週やると地味に重い。Google トレンドの探すタブをCLIで叩いて、急上昇キーワードをそのままClaude Codeに渡せるようにしました。使い所はnoteに。

→ [note URL]

---

## 案E：技術寄り型（tech-blog誘導）

投稿本文 ↓

Google トレンドはJSが重く単純curlでは取れない。Browser Use CLIでヘッドレス起動→12秒待機→innerText抽出という構成で安定化させました。アンチボット時の実Chromeプロファイル運用も技術記事に。

→ [tech-blog URL]

---

## 運用メモ

- 案A〜Dはnote記事へ、案Eは技術ブログ（Zenn/Qiita）へ誘導
- 投稿時間の目安：平日の朝7〜8時台、または夜21時台
- ハッシュタグは基本つけない方針。本文に `Claude Code` `Browser Use` `Google トレンド` `YouTube` のキーワードを自然に含める
- 進行中の運用知見ベース。「最強」「神」等の煽り表現は使わない
- 公開順序の目安：note記事を先に公開 → X案A〜Dを数日に分けて投稿 → 技術記事公開後に案Eを投稿
