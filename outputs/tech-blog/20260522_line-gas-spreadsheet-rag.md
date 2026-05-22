---
title: DifyなしでLINE×GAS×スプレッドシートに簡易RAGを実装する｜三段構え判定とGASの制約回避
status: draft
created: 2026-05-22
updated: 2026-05-22
type: tech-tutorial
related:
  - structured/projects/20260520_line-gas-spreadsheet-rag.md
medium: tech-blog
target_cta: GitHub
target_platforms:
  - Zenn
  - Qiita
---

# DifyなしでLINE×GAS×スプレッドシートに簡易RAGを実装する｜三段構え判定とGASの制約回避

## TL;DR

- LINEのFAQボットを、Dify等のワークフローツールを介さず **LINE Messaging API + Google Apps Script + スプレッドシート + OpenAI API** だけで構成した
- スプレッドシートを簡易ベクトルDBとして使い、**埋め込み → コサイン類似度（上位K）→ LLM最終判定** の三段構えで「回答すべき質問か」を判定する
- GASの `doPost` は **HTTPヘッダを読めない** ため、LINE公式の署名検証（`X-Line-Signature`）は実装不能。クエリトークンによる簡易認証で代替した
- `sha256(質問+回答)` による差分検知で、変更行だけを再ベクトル化。再実行コストをほぼゼロにできる
- 実機E2Eまで確認済み。回答精度の定量評価とスケール耐性の測定は次フェーズ（本記事は中間報告）

この記事は、クライアント案件で検証した構成を一般化して書いている。クライアント固有の情報は含まない。

## 課題設定：なぜDifyを使わなかったのか

LINEのFAQ対応をAI化する場合、LINEのWebhookをDifyの開始ノードで受け、そこからスクリプトを呼ぶ構成がよく採られる。最初はその案で設計していた。

ただ、二点が引っかかって直結構成へ切り替えた。

1. **ユーザー導線**：Dify中継だと回答が「Webの回答画面へ誘導」する形になりやすく、LINEトーク内で会話が完結する通常のチャット体験から外れる
2. **運用負荷**：Difyのノード設定は、引き継ぎ先の運用担当者にとって「もうひとつ覚えるもの」になる

結果、構成要素を **LINE / GAS / スプレッドシート / OpenAI** の4つに絞った。障害点が減り、運用窓口がスプレッドシートに一本化される。

## 全体アーキテクチャ

```
LINE Messaging API
   │  Webhook（message event）
   ▼
Google Apps Script（Web App: doPost）
   ├─ リクエスト検証（クエリトークン照合）
   ├─ embedQuery()  → OpenAI Embeddings API
   ├─ search_()     → コサイン類似度で上位K件抽出
   └─ judge_()      → LLM最終判定（gpt-5-mini / JSON固定）
   ▼
LINE reply API → ユーザーへ回答 or 固定フォールバック文言

スプレッドシート「knowledge」シート ＝ 簡易ベクトルDB
  A:ID  B:質問  C:回答  D:embedding（自動）  E:hash（自動）
  └ 差分検知で変更行のみ再ベクトル化（日次トリガ + 手動メニュー）
```

GASプロジェクトは `clasp` でローカル管理し、責務を4ファイルに分けた。

| ファイル | 役割 |
|---|---|
| `main.js` | doPost / リクエスト検証 / LINE返信 / オーケストレーション / シートロガー |
| `Config.js` | Script Properties アクセサと動作パラメータ（モデル名・閾値・TTL等） |
| `Embedding.js` | OpenAI Embeddings 呼び出し（`embedBatch` / `embedQuery`） |
| `Knowledge.js` | `buildIndex` / `search_` / `judge_` / `answerQuestion` / `testSearch` / メニュー・トリガ |

## 技術スタック

| 要素 | 採用したもの | 補足 |
|---|---|---|
| メッセージ基盤 | LINE Messaging API | Webhook受信 + reply API。テキスト上限5000字 |
| 実行環境 | Google Apps Script（Web App） | `doPost` で受信。`clasp` でローカル管理 |
| データストア | Googleスプレッドシート | コンテナバインド型。簡易ベクトルDB兼ログ |
| 埋め込み | OpenAI `text-embedding-3-small` | 1536次元、バッチサイズ96 |
| 最終判定LLM | OpenAI `gpt-5-mini` | `response_format: json_object` で出力をJSON固定 |
| キャッシュ | GAS CacheService | TTL 6時間、100KB上限超過時はシート直読みへ |

## RAGとは何か、なぜ「三段構え」にするのか

RAG（Retrieval-Augmented Generation／検索拡張生成）とは、ユーザーの入力に対し、外部データから関連情報を検索し、その内容をもとに応答を生成する手法のことだ。今回はその検索層を、専用ベクトルDBではなくスプレッドシートで簡易的に再現している。

ここで素朴に実装すると「いちばん近いFAQを返す」だけになる。だが問題は、**FAQに無い質問でも「いちばん近い行」は必ず存在する**ことだ。スコアがそこそこ高いだけで機械的に返すと、見当違いの回答を堂々と送ってしまう。

そこで判定を三段構えにした。

### Step 1：質問の埋め込み

ユーザーの質問を `text-embedding-3-small` で1536次元のベクトルに変換する。

```javascript
// Embedding.js（概念コード）
function embedQuery(text) {
  const res = callOpenAI_('/v1/embeddings', {
    model: 'text-embedding-3-small',
    input: text,
  });
  return res.data[0].embedding; // length 1536
}
```

### Step 2：コサイン類似度で上位K件抽出

スプレッドシートの全行（D列のembedding）と質問ベクトルのコサイン類似度を計算し、スコア降順で上位K=5件を取り出す。

```javascript
// 概念コード：両ベクトルとも非ゼロ前提
function cosineSimilarity_(a, b) {
  let dot = 0, na = 0, nb = 0;
  for (let i = 0; i < a.length; i++) {
    dot += a[i] * b[i];
    na += a[i] * a[i];
    nb += b[i] * b[i];
  }
  return dot / (Math.sqrt(na) * Math.sqrt(nb));
}
```

### Step 3：LLMによる最終判定

上位5件の候補を `gpt-5-mini` に渡し、「質問に本当に関連する候補はどれか」を判定させる。出力は `response_format: json_object` でJSONに固定し、`relevant`（真偽）と `index`（候補番号 or null）の2フィールドだけを返させる。

そして **回答を返す条件は「最大類似度 ≥ 0.7」かつ「LLMが `relevant=true`」の両方**。どちらかが否定したらフォールバック文言に切り替える。数値スコアという機械的フィルタと、LLMという意味的フィルタを直列に置くことで、「近いけど答えになっていない質問」を弾く。

> **設計思想**：ボットが堂々と間違えるより、「答えられない」と正直に返すほうがサポート品質としてはマシ。

なお `gpt-5-mini` のような推論モデル系は `temperature` を既定値（1）以外で受け付けない。指定しない実装にしておくと、モデルを切り替えたときの事故を防げる。

応答時間の実測は、埋め込みが約0.3秒、LLM判定が1〜3秒程度。LINEの `replyToken` 有効時間内に余裕で収まる。

## ハマりどころ①：GASの `doPost` はHTTPヘッダを読めない

LINEのWebhookには、リクエストが正規のものか検証する `X-Line-Signature` ヘッダ（HMAC-SHA256署名）がある。本来はこれを検証したい。

ところがGAS Web Appの `doPost(e)` は、`e.postData` でリクエストボディは取れるが、**HTTPヘッダにはアクセスできない**。つまりLINE公式の署名検証は構造的に実装不能だった。

### Q. ではどう認証するのか？

代替として、Webhook URLにクエリパラメータでトークンを付与し、受信側で照合する簡易認証にした。

```javascript
// main.js（概念コード）
function verifyRequest_(e) {
  const expected = getProp_('LINE_CHANNEL_SECRET');
  const token = e.parameter && e.parameter.token;
  return token === expected; // ?token=<secret> を照合
}
```

Webhook URLは `https://script.google.com/macros/s/XXXX/exec?token=<secret>` の形になる。正規の署名検証ではないので、ここは妥協点だと明記しておく。

ただし、HMAC署名を検証するロジック自体は `verifyLineSignature_` として未使用のまま残置してある。将来 Cloud Run など、ヘッダを読める基盤に移したときそのまま流用できる状態にしておくのが狙いだ。

## ハマりどころ②：全件再ベクトル化を避ける差分検知

FAQを1件直すたびに全件をベクトル化し直すのは、API課金的にも時間的にも無駄が大きい。

そこで各行について `sha256(質問 + "\n" + 回答)` を計算してE列（hash列）に保存する。`buildIndex` 実行時に、現在のハッシュと保存済みハッシュを比較し、**不一致の行（と未ベクトル化の行）だけ**をEmbeddings APIに渡す。

```javascript
// 概念コード
const hash = sha256_(question + '\n' + answer);
const storedHash = String(row[HASH_COL] || '');
if (hash !== storedHash || !hasVector) {
  targets.push({ rowIndex, text: question + '\n' + answer, hash });
}
```

これで、20数件のうち1件だけ編集してもAPIに送られるのはその1件分だけ。「データ更新はリアルタイム不要」という前提を確定できたので、再ベクトル化のトリガは **毎日決まった時刻の自動トリガ** と **スプレッドシートのカスタムメニュー** の2系統に割り切った。運用担当者はA〜C列（ID・質問・回答）を編集するだけで、D・E列はスクリプトが自動管理する。

## ハマりどころ③：CacheServiceの100KB上限

ベクトル一覧をGASの `CacheService` にTTL 6時間で載せて高速化している。ただし `CacheService` は1項目あたり100KBの上限がある。

対策として、**シリアライズ後のサイズで判定し、100KBを超える場合は無条件にスプレッドシート直読みへフォールバック**する実装にした。動作は止まらないが、件数が数百〜数千件規模になったときの挙動はまだ未測定で、次フェーズの宿題になっている。

## ハマりどころ④：LINEの再送ループを止める

LINEのWebhookは、レスポンスが2xx以外だとリクエストを再送する。`doPost` で例外時に5xxを返すと、再送 → また失敗 → また再送、と処理が嵐になる。

対策はシンプルで、**例外が起きても必ずHTTP 200を返す**。ボディに `{ ok: false, reason }` を入れて失敗を表現し、エラーの詳細はログシートと Cloud Logging に残す。

```javascript
function doPost(e) {
  try {
    // ... 通常処理 ...
    return jsonResponse_({ ok: true });
  } catch (err) {
    logToSheet_('error', 'doPost:exception', { message: String(err) });
    return jsonResponse_({ ok: false, reason: String(err) }); // 常に200
  }
}
```

あわせて、処理経路の各イベント（`doPost:start`、`handleTextMessage:answered` 等）を「ログ」シートに構造化JSONで追記するシートロガーを早期に組み込んだ。`clasp logs`（Cloud Logging）とシートロガーの二系統で挙動を追えるようにしておくと、特にLINE側から来る実リクエストの形状を確認するときに効く。

## ハマりポイントまとめ

| 症状・制約 | 原因 | 対応 |
|---|---|---|
| LINE公式の署名検証ができない | `doPost` はHTTPヘッダ非対応 | クエリトークン簡易認証。HMACロジックは残置 |
| 全件再ベクトル化が重い | 編集のたびに全行を投げていた | `sha256` 差分検知で変更行のみ再ベクトル化 |
| キャッシュに載らない | CacheService 100KB上限 | 超過時はシート直読みへフォールバック |
| 再送ループ | 非2xxでLINEが再送 | 例外時も200を返し、詳細はログへ |
| embedding列で行高が伸びる | JSON文字列がそのまま表示される | `WrapStrategy.CLIP` + 既定行高へ再整形 |

## 現状と次フェーズ

現時点で確認できているのは以下まで。

- 実機LINEからの送信で「埋め込み → 類似度上位K → LLM判定 → 返信」が一連で動作（E2E）
- 差分検知が機能し、1行編集で当該行のD・E列だけが更新される
- token不一致・欠落のリクエストが `unauthorized` で破棄される
- カスタムメニュー経由・日次トリガ経由の両方でインデックス再構築が動作

未着手なのは次の通り。**この記事はあくまで中間報告である。**

- 回答精度の定量評価（既存マニュアルをQ&A化したうえでの質的検証）
- 数百〜数千件規模でのスケール耐性（CacheService上限、全件コサイン類似度の計算コスト、スコア分布の変化）
- 類似度閾値（0.7）と TOP_K の再キャリブレーション
- 数千件規模に達した場合の専用ベクトルDB（pgvector / Qdrant 等）への移行判断

## まとめ

スプレッドシートを簡易ベクトルDBに見立てれば、専用基盤を立てずともLINE上でRAG的なFAQボットは動く。GASならではの制約（ヘッダ非対応、キャッシュ上限、再送）は確かにあるが、それぞれ現実的な回避策に落とし込める。

「専用ベクトルDBを立てるほどではないが、キーワード検索では物足りない」——その中間の規模に、この構成はちょうど効く。実装一式の整理が済んだらGitHubで公開予定なので、続報を待っていてほしい。

---

**Zenn想定タグ**：`gas` `line` `openai` `rag` `embeddings`
**Qiita想定タグ**：`GoogleAppsScript` `LINE` `OpenAI` `RAG` `embedding`
