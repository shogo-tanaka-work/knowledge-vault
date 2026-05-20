# LINE×GAS×Spreadsheet RAG（Difyレス構成）検証ログ

> ステータス: 進行中（実機E2Eまで完了／回答精度の本格評価が未完了）
> 作成日: 2026/05/20
> 最終更新: 2026/05/20
> ファイルパス: /Users/shogo/Documents/ai-business-os/15_ナレッジ基盤/vault/structured/projects/20260520_line-gas-spreadsheet-rag.md

---

📋 プロジェクト概要
* カテゴリ: チャットボット / RAG（簡易ベクトル検索）/ LINEチャットサポートAI化
* 期間: 2026/05/18 - 2026/05/20（実機E2E疎通まで）
* 主要メンバー: 田中省伍、K W
* ステークホルダー: クライアント（チャットサポート運用担当）
* プロジェクトステータス: 進行中（実機動作確認済み・精度評価フェーズへ移行予定）

---

## 1. 背景と目的
* LINE公式アカウントのチャットサポートをAI化する試験。既存FAQをスプレッドシートで管理し、ユーザーの自由入力に対し意味的に近いQ&Aを返す構成を検証する。
* 当初は `20260517_chatbot-spreadsheet-embedding.md` のDify中継案（LINE → Dify開始ノード → GAS）で設計していたが、(a) ユーザー導線が「Webの回答画面へ誘導」となり通常のLINEチャット体験から外れる、(b) Difyノード設定の運用負荷、の2点を踏まえてDifyを廃した直結構成へコンセプト変更。
* 本検証の目的は「Dify非経由でも三段構え判定（埋め込み→類似度→LLM最終判定）が成立し、LINE replyToken有効内に応答できる」ことの実証と、運用者がスプレッドシートだけで完結できるFAQ更新フローの確立。

---

## 2. 取り組み内容

### 実施した施策・活動
* LINE Webhook を GAS Web App の `doPost` で直接受ける構成を実装。Difyを介さない直結ルートで動作確認。
* スプレッドシート `knowledge` シートを簡易ベクトルDBとして設計（A:ID / B:質問 / C:回答 / D:embedding / E:hash）。運用者は A〜C のみ編集し、D・E はスクリプトが自動管理。
* 差分検知（`sha256(質問+回答)` を hash 列に保存し不一致行のみ再ベクトル化）を実装し、再実行コストをほぼゼロに抑制。
* `clasp` で GAS プロジェクトを管理。`src/main.js` / `Config.js` / `Embedding.js` / `Knowledge.js` の4ファイル構成で役割を分離。
* スプレッドシート上のカスタムメニュー「チャットボット > インデックス再構築 / 行の高さを整える」と、毎日4時の自動再ベクトル化トリガ（`createDailyTrigger`）を実装。
* LINE実機からの送信に対し、ヒット質問は正回答、無関係質問はフォールバック文言が返ることをE2Eで確認。

### 使用したツール・技術
* LINE Messaging API（Webhook / reply API、テキスト上限5000字）
* Google Apps Script（GAS Web App、`doPost`／`clasp` でローカル管理）
* Googleスプレッドシート（コンテナバインド型・簡易ベクトルDB／構造化ログシート「ログ」）
* OpenAI Embeddings API（`text-embedding-3-small` / 1536次元、バッチサイズ96）
* OpenAI Chat Completions API（最終判定LLM: `gpt-5-mini`、`response_format: json_object` でJSON固定）
* CacheService（インデックスキャッシュ、TTL 6時間、100KB上限を超える場合はスキップしてシート直読みにフォールバック）

### 主要な意思決定とその理由
* **Dify中継を廃し、LINE Webhook → GAS doPost の直結構成に変更**。LINE通常チャット体験を維持しつつ、運用要素を「スプレッドシート＋GAS」に絞り込む。
* **クエリトークンによる簡易認証**を採用。GAS の `doPost(e)` は HTTPヘッダにアクセスできず、LINE公式の `X-Line-Signature`（HMAC-SHA256）検証が実装不可能。代替として Webhook URL に `?token=<LINE_CHANNEL_SECRET と同一値>` を付与し、受信側で一致判定。署名検証ロジック自体は `verifyLineSignature_` として残し、GAS以外（Cloud Run等）への移行時に流用可能な状態にしてある。
* **三段構え判定**を採用：(1) 質問を埋め込み（1536次元）、(2) 全行とコサイン類似度を取り上位K=5件抽出、(3) 最大類似度 ≥ 0.7 かつ LLMが `relevant=true` と判定したときのみ回答を返す。閾値未満・LLM不一致時は固定フォールバック文言。
* **差分検知＋日次トリガ**：行ごとに `sha256(質問+回答)` を保存し、不一致 or 未ベクトル化の行のみを Embeddings API に渡す。データ更新はリアルタイム不要との前提を確定。
* **判定LLMに `gpt-5-mini` を採用**。推論モデル系の制約に合わせ `temperature` 指定は省略（既定値1のみ許容）、`response_format: json_object` で出力を JSON 固定。
* **再送ループの抑止**：`doPost` は例外時も HTTP 200（`{ok:false, reason}`）を返す。LINE側の再送による副作用を回避し、エラー詳細はシート「ログ」と Cloud Logging に出力。
* **シートロガー**：処理経路の各イベント（`doPost:start` / `handleTextMessage:answered` 等）を「ログ」シートに構造化JSONで追記。`clasp logs` と二系統で追跡可能。

---

## 3. 進捗と成果

### 達成できたこと
* `src/` 配下4ファイル構成で、LINE実機から「埋め込み → 類似度上位K → LLM判定 → 返信」の一連動作が完了。
* 差分検知が機能し、1行編集 → `buildIndex` で当該行のD・E列のみが更新されることを確認。
* 不正リクエスト（token不一致/欠落）が `unauthorized` として破棄されることを確認（ログシート上で確認可能）。
* スプレッドシートのカスタムメニュー経由でも、日次トリガ経由でもインデックス再構築が動作。

### 定量的な成果
* 1質問あたり応答時間: 埋め込み ~0.3s + LLM判定 ~1〜3s 程度で、LINE replyToken の有効時間内に余裕で応答完結。
* 現行ナレッジ件数: 約20数件（FAQ初期投入分）。

### 定性的な成果
* Dify中継を排除したことで、運用者がDify管理画面を一切触らずスプレッドシートのみで完結できる体験を確立。
* スクリプトの責務分離（IF/設定/埋め込み/ナレッジ）が明確になり、後続のスケール検証や置き換え（例: 専用ベクトルDB化）に向けた拡張ポイントが見えやすい状態。

---

## 4. 学びとナレッジ

### うまくいったこと（Good）
* Dify中継を外したことで構成要素が「LINE / GAS / スプレッドシート / OpenAI」だけに収まり、障害点・運用窓口がシンプル化した。
* `response_format: json_object` ＋ 厳格なプロンプト指定により、LLM判定の出力ブレを抑制できた（`relevant` と `index` の2フィールド固定）。
* シートロガーを早期に組み込んだことで、`clasp logs` だけでは追いにくい本番挙動（特に LINE 側からの実リクエスト形状）を即時に俯瞰できた。

### うまくいかなかったこと（Bad）
* GAS `doPost` がヘッダ非対応のため LINE 公式の署名検証を採用できず、共有シークレットをURLに乗せる簡易方式に妥協せざるを得なかった。
* 回答精度の本格評価（既存マニュアル刷新後の質的検証）は今回のスコープでは未完了。

### 改善ポイント（Improve）
* 既存マニュアルをFAQ化するチャンキング指針（質問粒度・回答長）の標準化。
* 件数が増えた際の `CacheService` 上限（100KB）越えに対する戦略の事前策定（部分キャッシュ／チャンク分割／別ストア）。

### 技術的な発見・Tips
* **GAS doPost の制約**：`e.postData` は取れるが HTTPヘッダは取得不可。LINEの `X-Line-Signature` 検証は不可能で、URLクエリトークンが現実解。
* **CacheService 100KB 上限**：シリアライズ後サイズで判定し、超える場合は無条件にシート直読みへフォールバックする実装が安全。
* **シート上の embedding 列**：JSON文字列のままだと行高が伸びて視認性が下がる。`WrapStrategy.CLIP` ＋既定行高（21px）への再整形を書き込み後に挟むと運用画面が崩れない。
* **推論モデル系の API 仕様**：`gpt-5-mini` 等は `temperature` 既定値1のみ受け付ける。指定しない実装にしておくとモデル切替時の事故を防げる。
* **再送ループ対策**：例外時も 200 を返し、内部状態はログシートに残す。LINE は非2xxで再送するため、エラー時 5xx を返すと処理が嵐になる。

---

## 5. 課題と対応

### 発生した課題
* LINE 公式署名検証が GAS では実装不能。
* `CacheService` の 100KB 上限。ナレッジ件数増加時に体感応答が遅くなる懸念。
* 現行20数件規模では類似度閾値（0.7）の妥当性が判断しきれない。件数が増えるとスコア分布が変わる可能性。
* マニュアル文書を Q&A 形式に分解するチャンキングが属人的。

### 対応方法
* 署名検証は HMAC ロジックを `verifyLineSignature_` として残置し、将来 GAS 以外への移行時に即流用可能な状態を維持。当面はクエリトークンで運用。
* キャッシュ越え時は自動でシート直読みにフォールバック。インデックス再構築後はキャッシュ破棄。
* 精度は次フェーズ（既存マニュアル刷新後）で本格評価。テスト関数 `testSearch(q)` で LINE 非経由のスポット評価を継続。

### 未解決の課題
* 既存マニュアル（クライアント現行コンテンツ）刷新後の回答精度評価。
* ナレッジが数百〜数千件規模に拡大した際のスケール耐性：CacheService 上限・コサイン類似度の全件計算コスト・スコア分布の変化、いずれも未測定。
* スケール到達時点での専用ベクトルDB（pgvector / Qdrant 等）への移行判断基準。

---

## 6. コストとリソース

### 人的リソース
* 田中省伍（実装・GAS／LINE連携・検証）、K W（ナレッジ整備・Script Properties設定・LINEチャネル管理）

### 金銭的コスト
* OpenAI API：K W社アカウントの余剰枠を継続活用（GASから直接呼び出し）。
* 1問あたりトークンコスト：埋め込み（質問1本＋判定LLMの候補5件＋プロンプト）。20数件規模では実額負担は軽微。
* スプレッドシート／GAS／LINE Messaging API：いずれも無料枠内。

### コスト対効果
* （精度評価フェーズ完了時に記入）

---

## 7. 今後の展開

### 次のアクション
* [田中省伍] 回答精度評価：既存マニュアルから生成したQ&Aセットに対し、`testSearch` でスコア・採否を一括検証するスクリプトを追加。
* [K W] 既存マニュアル刷新：現行のサポート手順書をQ&A粒度に分解し `knowledge` シートへ投入。
* [田中省伍] スケール耐性試験：ダミーデータでナレッジを 500 / 2000 件まで増やし、`loadIndex_` の所要時間と CacheService 越境時のフォールバック挙動を計測。
* [田中省伍] 閾値・TOP_K のチューニング：刷新後データで `SIMILARITY_THRESHOLD` と `TOP_K` を再キャリブレーション。

### 横展開の可能性
* 同様の「スプレッドシート＋GAS＋LINE」構成は、別クライアントの社内FAQ／問い合わせ一次受けにそのまま応用可能。
* Dify中継版（20260517構成）と、本Difyレス構成のどちらを採るかは、運用窓口の数（Dify管理を許容できるか）で選択。

### 長期的な改善案
* ナレッジ数百件超えの段階で、専用ベクトルDB（pgvector / Qdrant 等）＋ API ゲートウェイ構成へ移行。GAS は管理用UI／日次ジョブに役割を縮退。
* GAS から Cloud Run / Cloudflare Workers への移行検討（HMAC署名検証が必要になった時点）。
* シートロガーの内容を BigQuery 等に転送し、応答品質メトリクスを継続監視。

---

📚 関連リソース

### 成果物・ドキュメント
* 実装一式: `/Users/shogo/Documents/ai-business-os/16_検証ラボ/lab-line-gas-spreadsheet-rag/`
  * `src/main.js` — doPost / リクエスト検証 / LINE返信 / オーケストレーション / シートロガー
  * `src/Config.js` — Script Properties アクセサ・動作パラメータ（モデル名・閾値・キャッシュTTL 等）
  * `src/Embedding.js` — OpenAI Embeddings 呼び出し（`embedBatch` / `embedQuery`）
  * `src/Knowledge.js` — `buildIndex` / `search_` / `judge_` / `answerQuestion` / `testSearch` / メニュー・トリガ
* セットアップ・運用手順: `lab-line-gas-spreadsheet-rag/README.md`

### 参考資料
* LINE Developers ドキュメント（Messaging API / Webhook 設定）
* OpenAI API ドキュメント（Embeddings / Chat Completions / response_format）
* Apps Script Web App（doPost のヘッダ非対応制約）

### 関連プロジェクト
* `20260517_chatbot-spreadsheet-embedding.md`（Dify中継案／本検証の前段構成）

---

✅ メモ・雑記
* LINE実機E2Eは確認済み。次フェーズは「回答精度」と「スケール耐性」の二軸が論点。
* 鍵類は Script Properties のみ。`16_検証ラボ/` は `.gitignore` 済みのため鍵がリポジトリに乗らない構造。

---

## 📝 更新ログ
<!-- このセクションはスキルが自動で追記する。手動編集不要。 -->
| 日時 | 更新内容の概要 |
|---|---|
| 2026/05/20 | ファイル作成（init）／lab-line-gas-spreadsheet-rag の実装内容と実機E2E結果を各セクションへ反映 |
