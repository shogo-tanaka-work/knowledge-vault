---
title: 過去note掘り起こしThreads（補助金／LINE FAQ／YouTubeトレンド）
status: ready
created: 2026-06-01
updated: 2026-06-01
type: resurfacing
related:
  - https://note.com/shogo_works/n/na0da15e17973
  - https://note.com/shogo_works/n/n76fac823e8e8
  - https://note.com/shogo_works/n/naf5ebc746981
medium: threads
target_cta: 該当note記事へ誘導
format: plain-text（マークダウン非対応。投稿時は各「投稿本文」だけをコピペ）
---

# 過去note掘り起こしThreads

公開済みnote 3本を、単発の掴み投稿で再浮上させる。各投稿は会話体・150〜200字。
掴み自体に気づきを1つ入れて、続きが気になる人だけnoteへ飛ばす（2層設計）。
角度を変えた複数案を用意。空き枠にローテーションで割り付ける。

公開URL:
- 補助金リサーチ（閲覧数1位）: https://note.com/shogo_works/n/na0da15e17973
- LINE FAQ AI化（2位）: https://note.com/shogo_works/n/n76fac823e8e8
- YouTubeトレンド収集（3位）: https://note.com/shogo_works/n/naf5ebc746981

---

# ① 補助金リサーチ（閲覧数1位・主力）

## 補助金-A（痛み共感型）

投稿本文 ↓

「今月使える補助金ある？」って聞かれるたびに、J-Net21を開いて分野選んで地域選んで期間絞って、一件ずつExcelに転記…。毎回30分、月4回で2時間が消えてた。

これ、Claude Codeに任せたら5分になった。条件を変えれば毎月そのまま使い回せる。

やり方と詰まったところ ↓
https://note.com/shogo_works/n/na0da15e17973

#業務自動化 #生成AI #ClaudeCode #補助金

## 補助金-B（数字インパクト型）

投稿本文 ↓

補助金リサーチ、30分 → 5分。

「2026年5月に申請できる創業支援系を全国で取って」とプロンプトで投げるだけ。裏でJ-Net21を自動でめくって、募集期間で絞って、色分けExcelに出してくれる。

構築過程はnoteに ↓
https://note.com/shogo_works/n/na0da15e17973

#業務効率化 #生成AI #ClaudeCode #BrowserUse

## 補助金-C（対象指名型）

投稿本文 ↓

経営や総務で「今月の補助金、一覧で出して」を定期でやってる人へ。

あの検索と転記、まるごとAIに任せられます。欲しい条件を日本語で指示するだけで、J-Net21から該当案件だけExcelに。

具体的な作り方 ↓
https://note.com/shogo_works/n/na0da15e17973

#補助金 #業務自動化 #DX推進 #生成AI

---

# ② LINE FAQ の AI化（閲覧数2位）

## LINE-A（痛み共感型）

投稿本文 ↓

LINE公式の問い合わせ対応をしてると、料金は？納期は？キャンセルは？って同じ質問に何度も答えてる自分に気づく。8割は過去の焼き直し。

これをAI化したけど、運用者が触るのはGoogleスプレッドシート1枚だけにした。

中身 ↓
https://note.com/shogo_works/n/n76fac823e8e8

#業務自動化 #生成AI #LINE #GAS

## LINE-B（技術判断型）

投稿本文 ↓

FAQボット、最初はDifyを噛ませる設計だった。でもやめた。

理由は引き継ぎ。クライアントが誰でも同じ条件で動かせるとは限らないし、GASに加えてDifyのノード設定まで覚えるのは負荷が二重。結局LINE＋GAS＋スプシ＋OpenAIの4つだけに絞った。

判断の詳細 ↓
https://note.com/shogo_works/n/n76fac823e8e8

#生成AI #RAG #GAS #業務改善

## LINE-C（構成・学び型）

投稿本文 ↓

Difyなしでも簡易RAGは作れる。

埋め込み → 類似度検索 → LLM最終判定、の三段で「答えるべき質問か」を判定。運用窓口はスプレッドシートのQ&A列だけで、ベクトル化はスクリプトが裏で自動管理する。

構成図つきで解説 ↓
https://note.com/shogo_works/n/n76fac823e8e8

#RAG #生成AI #LINE #ノーコード

---

# ③ YouTubeトレンド収集（閲覧数3位）

## YouTube-A（痛み共感型）

投稿本文 ↓

毎週月曜の朝、Googleトレンドの「探す」タブを開いて、日本・過去1ヶ月・YouTube検索に切り替えて、上位50件をスプシに転記…。20〜30分。誰かに任せるほどでもない、こういう作業が一番長く残る。

1コマンドにした話 ↓
https://note.com/shogo_works/n/naf5ebc746981

#業務自動化 #生成AI #ClaudeCode #BrowserUse

## YouTube-B（技術判断型）

投稿本文 ↓

YouTubeの「検索トレンド」はData APIじゃ取れない。gprop=youtube相当が公式提供されてないから。

だからブラウザ自動化に振り切った。Makeでもn8nでもなくCLIにした理由も含めてnoteに書いた。

→ https://note.com/shogo_works/n/naf5ebc746981

#生成AI #ブラウザ自動化 #BrowserUse #データ収集

## YouTube-C（数字インパクト型）

投稿本文 ↓

週20〜30分の手作業が、10秒に。

おかげで収集頻度を「週1」から「日次」に上げる余地までできた。Claude Code＋Browser Use CLIで、ターミナル1コマンド。

やり方 ↓
https://note.com/shogo_works/n/naf5ebc746981

#業務効率化 #生成AI #ClaudeCode #SNSマーケティング

---

## ローテーション運用メモ

- 閲覧数1位の補助金を良い枠（週頭・初動）に置く。反応が良ければ角度を変えて再投下する
- 同じnoteを連投しない。最低でも中2〜3日あける
- 掴み（1〜2文目）に必ず気づきを入れる。「詳細はこちら」だけにしない
- リンクを踏まない人にも価値が残る形を維持する
- 反応の良かった案（A/B/C）を記録し、勝ちパターンを再利用する
