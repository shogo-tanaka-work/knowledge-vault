# チラシ収集自動化エージェント 検証ログ

> ステータス: 進行中
> 作成日: 2026/06/09
> 最終更新: 2026/06/09（2回目）
> ファイルパス: /Users/shogo/Documents/ai-business-os/15_ナレッジ基盤/vault/structured/projects/20260609_chirashi-automation.md

---

📋 プロジェクト概要

- カテゴリ: 生活自動化 / AI エージェント開発 / ライフハック
- 期間: 2026/06/08 -（検証中）
- 主要メンバー: 田中省伍
- ステークホルダー: 個人利用
- プロジェクトステータス: 進行中

---

## 1. 背景と目的

- 毎朝、近隣スーパーの特売チラシを手動で確認するのが手間。横断比較ができないため、どこが一番安いか判断しにくい
- 郵便番号を入力するだけで「今日の近隣スーパー特売一覧」が自動生成される個人ツールを構築したい
- 3ステップ構想: (1) 個人用CLI → (2) ブラウザからアクセス可能 → (3) 広告付き一般公開
- ただし調査の結果、チラシデータの法的リスクが判明し、Step1（個人CLI）に限定する判断をした

---

## 2. 取り組み内容

### フェーズ1: CLI MVP（chirashi-sale-finder スキル）

- Browser Use CLI でトクバイを自動操作し、近隣スーパーのチラシ画像を取得
- Claude のマルチモーダル機能でチラシ画像を直接読み取り、商品名・価格・有効日を構造化
- 165-0027（東京都中野区野方）で実E2E検証。サミット・ヨークフーズのチラシ取得・Vision解析まで動作確認
- 成果物: `.agents/skills/chirashi-sale-finder/`（SKILL.md, scripts/, reference/）

### フェーズ2: エージェント化（lab-chirasshi_automation）

- Hermes Agent（Nous Research OSS、2026/02リリース）を活用した自律エージェント構成を設計・実装
- Browser Use CLI を「ツール」として呼び出す設計（コード生成不要・トークン効率化）
- GPT-5 nano（推論モデル）でオーケストレーション + Vision 両方を担当
- MacBook 上で 42 ステップ完走（画像21枚取得）を確認。将来 Ubuntu 常駐 PC への移行予定
- 成果物: `16_検証ラボ/lab-chirasshi_automation/agent/`（agent.py, tools/, .env）

### フェーズ3: 通知機能強化（Discord Webhook）

- `agent/tools/file_tools.py` の `notify()` に Discord Webhook 送信ブロックを追加
- `DISCORD_WEBHOOK_URL` 環境変数を読み取り、設定されていれば Webhook POST を実行
- メッセージ 2000 文字超過時は末尾を「…(省略)」で自動トリム（Discord の制限対応）
- 優先順位: Discord → LINE Notify → ターミナル出力
- `.env.example` に `DISCORD_WEBHOOK_URL=` 項目を追記
- 標準ライブラリ（`urllib.request`）のみで実装。追加依存なし
- `SKILL.md` の Step 7 を「完了報告 & Discord通知」に更新し設定方法を記載

### 実装した主要コンポーネント

- `scripts/list_stores.js`: トクバイ店舗一覧抽出 + 多層スーパー判定（WHITELIST 30+チェーン・ブラックリスト・店名正規化）
- `scripts/extract_flyers.js`: チラシ画像 CDN URL 抽出 + 高解像度版 URL 生成
- `scripts/capture.sh` → `agent/tools/browser_use_tool.py`: capture.sh から eval_js_file ツールに進化
- `agent/tools/analyze_image.py`: GPT-5 nano Vision API でチラシ解析
- `reference/known_stores.md`: ヨーク・西友・サミット等の常時取得店舗を固定登録

### 主要な意思決定とその理由

- **データソース**: トクバイを主に採用（Shufoo! は canvas ビューアで画像取得が困難なため）
- **スクレイピング方式**: `/leaflets` は 404 のため、店舗ページ本体の画像 CDN URL を直接 DL する方式を採用
- **Vision モデル**: GPT-5 nano（推論モデル）を採用。max_completion_tokens=8000 が必要
- **公開範囲**: 個人利用限定。チラシ画像の著作権・ポータル利用規約を考慮し再配信しない
- **検索エリア**: 野方1丁目居住のため、野方5/6丁目（野方駅前）と沼袋を除外し、高円寺（166-0003）をサブ検索として追加
- **エージェント構成**: Playwright でのコード生成方式ではなく、browser-use CLI をツールとして呼び出す方式を採用（LLM のトークン消費を5〜10分の1に削減）

---

## 3. 進捗と成果

### 達成できたこと

- 郵便番号入力 → 近隣スーパー自動特定 → チラシ画像取得 → Vision 解析 → Markdown 出力の全パイプライン完成
- 実データ（野方1丁目エリア）でエンドツーエンド動作確認
- Hermes Agent ベースのエージェントループが 42 ステップ完走（画像21枚取得成功）
- ヨークフーズ HP からの直接取得（browser-use 不要・curl のみ）も実装
- 多層スーパー判定で業種無差別の327件から食品スーパー26件を正確に絞り込み
- 2026/06/09 実行: 75 ステップ完走、チラシ画像 28 枚 + ヨーク直取得 2 枚（計 30 枚）取得済み
- Discord Webhook 通知実装完了（`DISCORD_WEBHOOK_URL` 環境変数で有効化）

### 定量的な成果

- 月間ランニングコスト試算: GPT-5 nano（オーケストレーション + Vision）~¥30/月
- 一回の実行で取得できたチラシ画像: 最大 21 枚
- スーパー判定精度: WHITELIST 30+チェーン + BLACKLIST で誤判定ほぼゼロ
- エージェントステップ数: 42ステップで完了（上限 100 に余裕あり）

### 定性的な成果

- 「テキスト層（店舗一覧）= eval 抽出」と「画像層（チラシ中身）= Vision 解析」の設計分離が有効に機能した
- ヨークフーズ HP の画像 URL パターン（`YO{MMDD}_{店舗コード}_{面}-1_{連番}.jpg`）を発見し、curl のみで高解像度チラシ取得が可能と判明
- Note 記事の切り口が確定（「技術的にはできたが公開しなかった理由」というポジション）

---

## 4. 学びとナレッジ

### うまくいったこと（Good）

- browser-use CLI の `eval` 方式（DOM テキスト層）と Vision 解析（画像層）の役割分担が明確で実装がシンプル
- 既存スキル（jnet21-subsidy-search）の巡回ループ・sleep 作法・result: プレフィックス処理をそのまま流用できた
- GPT-5 nano は Vision + Function Calling を 1 モデルで担え、アーキテクチャがシンプルになった
- `known_stores.md` による「常時取得店舗」の固定登録方式が柔軟性と確実性を両立できた

### うまくいかなかったこと（Bad）

- `/leaflets` URL が 404 → 初期設計から変更が必要だった
- `eval $(cat file.js)` が Python subprocess でシェル展開されない → `eval_js_file` ツールを別途実装する必要があった
- GPT-5 nano の `max_completion_tokens=2000` では推論トークン不足で空レスポンス → 8000 必要と判明
- `.env` のキーをモジュールレベルで読むと import 時（`_load_dotenv()` より先）に評価されて空になる

### 改善ポイント（Improve）

- チラシ有無の事前判定（チラシ未登録店の早期スキップ）があると効率化できる
- ヨーク以外の HP 直取得対応（イトーヨーカドー・西友 HP など）の体制整備
- 複数日にわたるチラシ履歴の蓄積と「いつもより安い」検出機能

### 技術的な発見・Tips

- トクバイのチラシ CDN: `image.tokubai.co.jp/images/bargain_office_leaflets/w=サイズ/ID.jpg` → `w=1200` に置換で高解像度版取得可能
- トクバイ検索の `bargain_keyword` は郵便番号・地名・チェーン名を受け付ける。郵便番号が近い順で最精度
- Gemini 2.0 Flash は 2026/06/01 でサービス終了済み。移行先は Gemini 2.5 Flash-Lite（$0.10/$0.40 per 1M）
- GPT-5 nano は推論モデル（o 系）のため `max_tokens` は非対応、`max_completion_tokens` を使う
- Hermes Agent（Nous Research、2026/02リリース）の正確な位置付け:
  - LangGraph（グラフ型ステートマシン）や Strands（軽量モデル駆動）とは**別カテゴリ**
  - 「長期稼働ランタイム + 自己改善」が設計思想。使うほどスキルが蓄積される
  - **3層メモリ内蔵**: Skills System（Markdown化手順） + セッション横断永続記憶（FTS5+LLM要約） + ユーザーモデリング
  - Discord/Slack/Telegram をネイティブ統合。Socket Modeで常駐サーバー不要
  - v0.16（2026/06/05）でmacOS/Windows/Linux デスクトップアプリ + Web管理パネル正式リリース
  - 現在の agent.py はバニラ OpenAI function calling（Hermes 未導入）。コメントの「インストール後に差し替える」が未実施
  - Hermes を正式導入すればセッションメモリ問題・チャンネル統合・スキル蓄積が全て解決する

### フレームワーク選定の考え方（2026年時点）

| ユースケース | 推奨 |
|---|---|
| 長期稼働エージェント・Discord/Slack統合 | **Hermes Agent** |
| 複雑な決定論的フロー・enterprise | LangGraph |
| AWS環境・ツール数千規模 | AWS Strands |
| ノーコード寄り・外部サービス連携 | n8n |

---

## 5. 課題と対応

### 発生した課題

- トクバイ利用規約がスクレイピングを禁止（個人・非商用でも免除されない）
- チラシ画像には著作権がある → 再配信・公開サービス化はリスク大
- 165-0027（野方全体）の検索では野方駅前（5/6丁目）が優先されて野方1丁目から遠い店が上位に来た
- GPT-5 nano の推論モデル特性（空レスポンス問題）
- `eval $(cat file.js)` のシェル展開が Python subprocess で動かない

### 対応方法

- 法的リスク: 個人の私的利用（閲覧の自動代行）に限定。再配信・公開は行わない方針で確定
- 検索エリア: `list_stores.js` に `FAR_ADDRESS` フィルタを追加し野方5/6丁目・沼袋を除外。高円寺（166-0003）をサブ検索として追加
- 空レスポンス: `max_completion_tokens=8000` に変更
- eval_js_file: `browser_use_tool.py` に専用ツールを実装

### 未解決の課題

- Hermes Agent のセットアップ（MacBook 上は動作確認済み、Ubuntu 移行は未実施）
- Discord Webhook URL の発行・`.env` への設定（コード実装済み・URL未設定）
- チラシ有無を事前判定して取得対象を絞り込む仕組み
- 複数郵便番号エリアでの動作確認
- 6/9 実行で Markdown ファイル（今日の特売.md）が未生成（Vision解析フェーズで停止した模様）

---

## 6. コストとリソース

### 人的リソース

- 実装工数: 2日（2026/06/08〜09）

### 金銭的コスト（月次・日次実行想定）

| 項目 | 費用 |
|---|---|
| GPT-5 nano（オーケストレーション + Vision） | ~¥30/月 |
| Hermes Agent（OSS・ローカル） | ¥0 |
| browser-use CLI（ローカル） | ¥0 |
| Ubuntu 常駐 PC 電気代 | ~¥100/月 |
| **合計** | **~¥130/月** |

### コスト対効果

- 毎朝5〜10分かかっていたチラシ確認作業がゼロになる見込み（月 2.5〜5 時間の削減）

---

## 7. 今後の展開

### 次のアクション

- [ ] Discord Webhook URL を発行して `agent/.env` に設定（`DISCORD_WEBHOOK_URL=https://...`）
- [ ] Hermes Agent のセットアップ（MacBook 環境で完成させてから Ubuntu に移植）
- [ ] Ubuntu 常駐 PC への移行・cron 設定（毎朝 7:00 実行）
- [ ] 6/9 の Vision 解析フェーズ停止原因の調査（画像 30 枚はある・Markdown が未生成）
- [ ] 西友・サミット・オーケー 高円寺等の固定店舗チラシの安定取得を追検証
- [ ] イトーヨーカドー HP のチラシ URL パターンを調査
- [ ] Note/Zenn 記事化（コード非公開・「やれる技術とやっていい行為は別」という判断軸の記事）

### 横展開の可能性

- 同じパイプライン（browser-use + Vision + エージェント）は請求書・名刺・商品ラベル・手書き伝票等の「人間向け画像」から情報抽出する用途全般に応用可能
- 別郵便番号エリアへの横展開は `python3 -m agent.agent <zip1> <zip2>` で対応可能

### 長期的な改善案

- 日次 cron で履歴を蓄積し「いつもより安い」検出機能を追加
- チラシ有効日を自動判定して今日有効な特売のみに絞り込む精度向上
- Step2（ブラウザ公開）はチラシポータルとの B2B 正規連携が実現した場合に再検討

---

📚 関連リソース

### 成果物・ドキュメント

- スキル（Phase1）: `/Users/shogo/Documents/ai-business-os/.agents/skills/chirashi-sale-finder/`
- エージェント実装（Phase2）: `/Users/shogo/Documents/ai-business-os/16_検証ラボ/lab-chirasshi_automation/`
- 記事ドラフト（Note/LinkedIn/X/Zenn）: `/Users/shogo/Documents/ai-business-os/15_ナレッジ基盤/vault/structured/articles/chirashi-automation/`
- 検証データ（チラシ画像・Markdown出力）: `16_検証ラボ/lab-chirasshi_automation/2026-06-08/`, `2026-06-09/`

### 参考資料

- Hermes Agent（Nous Research）: https://hermes-agent.org / https://github.com/NousResearch/hermes-agent
- Hermes v0.16「The Surface Release」（2026/06/05）: Desktop + Web管理パネル正式化
- 2026年フレームワーク比較: https://qubittool.com/blog/ai-agent-framework-comparison-2026
- Discord/Slack統合（Composio経由）: https://composio.dev/toolkits/discord/framework/hermes-agent
- GPT-5 nano 料金: $0.05/$0.40 per 1M tokens（Vision 対応・推論モデル）
- Gemini 2.5 Flash-Lite: $0.10/$0.40 per 1M tokens（Gemini 2.0 Flash の後継）
- zipcloud 郵便番号 API: https://zipcloud.ibsnet.co.jp/api/search?zipcode=XXXXXXX

### 関連プロジェクト

- jnet21-subsidy-search スキル（browser-use 巡回パターンの参照元）
- poc-archive（Hono+React+D1+R2 の Cloudflare スタック、Step2 の土台候補）

---

✅ メモ・雑記

- Shufoo!/トクバイはスクレイピング禁止だが、個人の私的閲覧の自動代行という位置付けで進めている。再配信・公開はしない
- ヨークフーズの画像 URL パターン `YO{MMDD}_201_{面}-1_1.jpg` は 2026/06 実測。店舗コード 201 = 中野店
- 野方1丁目は中野駅・野方駅・沼袋駅の中間エリア。検索は 165-0027（野方・5/6丁目除外）+ 166-0003（高円寺）の 2 エリア構成
- トクバイの `response_format: json_object` は GPT-5 nano では非対応 → コードブロック除去で対処

---

## 📝 更新ログ

| 日時 | 更新内容の概要 |
|---|---|
| 2026/06/09 | ファイル作成（init） |
| 2026/06/09 | Discord Webhook通知実装・6/9実行結果（75ステップ、画像30枚）を反映（update） |
| 2026/06/09 | Hermes Agent の正確な位置付け・フレームワーク比較・Discord統合パターンを追記（update） |
