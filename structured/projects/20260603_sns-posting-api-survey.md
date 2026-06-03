# SNS自動投稿API現状調査（Threads / X / LinkedIn）検証ログ

> ステータス: 進行中
> 作成日: 2026/06/03
> 最終更新: 2026/06/03（初回リサーチ反映）
> ファイルパス: /Users/shogo/Documents/ai-business-os/15_ナレッジ基盤/vault/structured/projects/20260603_sns-posting-api-survey.md

---

📋 プロジェクト概要
* カテゴリ: SNS発信の自動化 / 媒体別投稿APIの現状調査
* 期間: 2026/06/03 -（調査中）
* 主要メンバー: shogo
* ステークホルダー: shogo（媒体別発信プロジェクト群 10_projects/Threads発信・X発信・LinkedIn発信 のオーナー）
* プロジェクトステータス: 進行中

> 媒体別にナレッジを溜めているが投稿は基本手動という課題に対し、自動投稿の道筋を探る基礎調査。スクレイピングはログイン必須・規約違反のため不可とし、公式APIの有無・料金・審査要件を媒体ごとに確定させる。

---

## 1. 背景と目的

* 各媒体（Threads / X / LinkedIn 等）にナレッジを溜めて発信しているが、投稿が手動のままで運用負荷が高い
* スクレイピングは(1)規約上不可、(2)ログインを伴うため現実的でない、という理由で方法から除外。公式APIに絞る
* 知りたかったのは「各媒体の投稿APIが無料で使えるのか／従量課金なのか／そもそも個人に開放されているのか」
* 特に伸ばしたい X と LinkedIn が、従量課金でしか使えないのか、LinkedIn は個人では実質使えないのかを確認したい
* Threads は無料枠で投稿できそうという当たりがついていたので、その裏取りも兼ねる

---

## 2. 取り組み内容

### 実施した施策・活動

* 2026/06/03: web-researcher 3並列で Threads / X / LinkedIn の投稿API現状を公式ドキュメント中心に調査
* 料金・無料枠・審査要件・認証方式・レート制限・自動化規約・最近の変更を媒体横断で比較

### 使用したツール・技術

* 調査: web-researcher（WebSearch + WebFetch）
* 対象API: Threads API（Meta）/ X API v2 / LinkedIn Posts API（旧 UGC Posts / Share API）

### 主要な意思決定とその理由

* スクレイピングを完全に除外し公式API一択で評価する（規約・ログイン制約のため）
* 料金は変動が激しい領域のため「2026年6月時点」と明記し、再調査前提でナレッジ化する

---

## 3. 進捗と成果

### 達成できたこと — 媒体別の結論

| 媒体 | 公式投稿API | 料金 | 個人の実用性 | 必須手続き |
|---|---|---|---|---|
| Threads | あり（Threads API） | 無料 | ◎ | Meta開発者登録＋App Review＋IG Business連携 |
| X（旧Twitter） | あり（X API v2） | 従量課金のみ（無料枠廃止） | ○テキスト / △リンク | console.x.com 登録＋OAuth2 User Context |
| LinkedIn | あり（Posts API） | 個人投稿は無料・審査不要 | ○ | Share on LinkedIn 製品追加＋OAuth2 |

### 定量的な成果 — 媒体別の詳細

**Threads（Meta）**
* 料金: 完全無料。有料/従量課金プランなし
* レート制限（本番・24h）: 投稿250件 / 返信1,000件 / 削除100件
* 認証: OAuth 2.0。長期トークン有効期限60日、自動更新なし（手動リフレッシュをバッチ化する必要あり）
* 必須: Meta開発者アカウント、アプリ作成、Instagram Business/Creatorアカウント連携、App Review通過（自分1人で使う場合も threads_content_publish には審査が必要）
* スコープ: threads_basic / threads_content_publish ほか
* できること: テキスト/画像/動画/カルーセル投稿、返信、引用、再投稿、削除、インサイト、Webhooks
* 予約投稿: API非対応。自前でキュー＋cron実装が必要

**X（旧Twitter）**
* 2026/02/06に無料枠を廃止、従量課金（Pay-Per-Use / クレジット購入型）へ全面移行。Basic($200/月)・Pro($5,000/月)は新規受付終了（既存のみ継続）
* 投稿単価（2026/04/20改定後）:
  * テキスト/メディア投稿（URLなし）: $0.015 / 投稿
  * URL含む投稿: $0.200 / 投稿（4月改定で約20倍に値上げ）
  * リプライ: $0.010 / 投稿
* 実用コスト試算: URLなしなら月30投稿で約$0.45、90投稿で約$1.35。URL付きは月30投稿で約$6.00
* レート制限（料金とは別）: POST /2/tweets はユーザー単位100回/15分、アプリ単位10,000回/24h
* 認証: OAuth 2.0 User Context（必須）。App-Only不可。スコープ tweet.write
* 可否: メディア投稿◯ / スレッド連投◯（in_reply_to_tweet_id 連鎖）/ 予約投稿◯（scheduled_date）
* 注意: 従量課金にハードキャップなし → Developer Console で支出上限(Spending Limit)を必ず設定

**LinkedIn**
* 現行は Posts API（POST /rest/posts）。旧 UGC Posts API / Share API は deprecated
* 個人プロフィール投稿: `Share on LinkedIn` 製品をアプリに追加するだけで `w_member_social` を取得でき、**審査不要・無料**
* 組織（会社ページ）投稿: Community Management API 経由で、法人格・事業用メール必須の厳格な審査。個人メールでは通過困難（却下時は新アプリ作り直し）
* 認証: OAuth 2.0 Authorization Code。アクセストークン60日、リフレッシュトークン365日（リフレッシュ付与はMDP承認アプリのみの可能性あり、Share単体では要確認）
* レート制限: メンバー単位150リクエスト/日、アプリ全体100,000/日
* 個人プロフィール自動投稿の難易度: 低〜中（トークン更新の自動化が最大の運用コスト）

### 定性的な成果 — 事前の当たりの答え合わせ

* Threads 無料枠 → 当たり（250投稿/日の無料枠で確定）
* X は従量課金でしか使えないのか → その通り。無料枠は2026/2に廃止済み。ただしテキストのみなら極めて安価
* LinkedIn はそもそも使えないのか → 誤解。個人プロフィール投稿は審査不要・無料で利用可能。審査が厳しいのは会社ページ投稿だけ

---

## 4. 学びとナレッジ

### うまくいったこと（Good）

* 3媒体すべてに公式の投稿APIが存在し、個人でも投稿自動化の道がある
* X はテキスト本文のみなら月数十円〜数百円レベルで自動投稿でき、コスト障壁は思ったより低い
* LinkedIn の個人投稿は無料・審査不要で、想定より敷居が低い

### うまくいかなかったこと / 注意点（Bad）

* X はURLを本文に含めると$0.20/投稿に跳ねる。ブログ記事リンクを毎回貼る運用はコスト急増
* Threads・X両方で本人1人運用でも審査やUser Context認証が必要で、初期セットアップに手間
* LinkedIn の会社ページ投稿は法人格必須で個人事業主には実質クローズド

### 改善ポイント / 運用設計のヒント

* X のURL課金回避: 本文にリンクを入れず、投稿後にリプライ($0.01)でリンクを返す形式にすると最大1/20にコスト圧縮できる可能性
* 3媒体共通でアクセストークンが60日失効 → トークン自動更新バッチが自動化成功の生命線。ここを最初に作り込む
* 予約投稿はThreadsがAPI非対応なので、媒体横断のスケジューラ（キュー＋cron）を自前基盤側に持つ設計が筋が良い

### 技術的な発見・Tips

* Threads API は Graph API とは別建て（base: graph.threads.net）。投稿はコンテナ作成→公開の2ステップ
* X は2026年に2回も価格改定があり、料金は固定費として計画しにくい（公式も「Consoleで最新確認」と案内）
* LinkedIn は Posts API への移行期。新規実装は UGC Posts ではなく Posts API を使う

---

## 5. 課題と対応

### 発生した課題（自動化に向けた論点）

* トークン60日失効への対応（3媒体共通）→ リフレッシュ自動化バッチを実装
* X のURL課金 → 本文URLを避けリプライ方式 or リンクなし運用に設計変更
* Threadsの予約投稿非対応 → 基盤側にスケジューラを持つ
* X従量課金の青天井リスク → Spending Limit設定で防御

### 未解決の課題

* LinkedIn の Share on LinkedIn 単体でリフレッシュトークンが自動付与されるか（再認証要否）は実装時に要確認
* Threads投稿APIに Instagram連携が今も必須かは公式ドキュメントで最終確認が必要（一部「不確実」情報あり）
* 各媒体のApp Review / 製品審査の実所要日数（Threadsは公称2〜3日だが初回却下で2〜3週間見込み）

---

## 6. コストとリソース

### 金銭的コスト（投稿API、2026/06時点）

* Threads: 無料
* X: 従量課金。テキストのみ月30投稿で約$0.45、URL付きは約$6.00。支出上限の設定前提
* LinkedIn: 個人投稿は無料

### コスト対効果

* 伸ばしたいX・LinkedInのうち、LinkedInは無料で着手可能、Xもテキスト中心なら低コスト。投資対効果は高い
* 最大の隠れコストは金銭よりトークン更新・審査・認証フローの実装工数

---

## 7. 今後の展開

### 次のアクション

* 着手しやすい順の推奨: (1)LinkedIn個人投稿（無料・審査不要）→ (2)Threads（無料だがApp Review要）→ (3)X（従量課金・URL運用設計が要検討）
* 各媒体でアプリ登録 → OAuth疎通 → 1投稿成功までをPoCで確認
* トークン自動更新バッチの共通設計を先に固める

### 横展開の可能性

* 媒体別発信プロジェクト（10_projects/Threads発信・X発信・LinkedIn発信）の溜め込みナレッジを、自動投稿基盤に流し込むパイプライン化
* [[20260603_multi-agent-infra-comparison]] のエージェント実行基盤上に、投稿ジョブを載せる構成（n8n → ジョブ → 各媒体API）

### 長期的な改善案

* 媒体横断の予約投稿スケジューラ＋トークン管理を共通基盤化し、媒体追加をプラガブルにする

---

📚 関連リソース

### 参考資料（一次情報）

* Threads: https://developers.facebook.com/docs/threads/overview ／ publishing: https://developers.facebook.com/docs/threads/reference/publishing/ ／ long-lived tokens: https://developers.facebook.com/docs/threads/get-started/long-lived-tokens/
* X: https://docs.x.com/x-api/getting-started/pricing ／ rate limits: https://docs.x.com/x-api/fundamentals/rate-limits ／ 値上げ報道: https://techcrunch.com/2026/04/22/x-makes-it-more-expensive-to-post-links-through-its-api/
* LinkedIn: https://learn.microsoft.com/en-us/linkedin/consumer/integrations/self-serve/share-on-linkedin ／ Posts API: https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/posts-api ／ getting access: https://learn.microsoft.com/en-us/linkedin/shared/authentication/getting-access

### 関連プロジェクト

* [[20260603_multi-agent-infra-comparison]] — エージェント実行基盤（投稿ジョブの実行先候補）
* 10_projects/Threads発信 ／ 10_projects/X発信 ／ 10_projects/LinkedIn発信

---

✅ メモ・雑記

* 結論ひとことメモ: 自動投稿は3媒体とも公式APIで実現可能。着手は「LinkedIn個人（無料・審査不要）→ Threads（無料・要審査）→ X（従量・URL運用注意）」の順が現実的
* 料金は変動が激しいので、本格着手前に各媒体の公式料金ページを再確認すること（特にX）

---

## 📝 更新ログ
<!-- このセクションはスキルが自動で追記する。手動編集不要。 -->
| 日時 | 更新内容の概要 |
|---|---|
| 2026/06/03 | ファイル作成（init）。Threads/X/LinkedIn の投稿API現状（料金・無料枠・審査・認証）を3媒体横断で調査・構造化 |
