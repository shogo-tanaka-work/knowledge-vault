# OpenAI Computer Use（ChatGPT agent / Responses API computer ツール）検証ログ

> ステータス: 検証中
> 作成日: 2026/05/27
> 最終更新: 2026/05/28
> ファイルパス: /Users/shogo/Documents/ai-business-os/15_ナレッジ基盤/vault/structured/tools/20260527_openai-operator-cua.md

---

## 📋 検証概要

- **ツール/サービス名**: OpenAI ChatGPT agent（旧 Operator） / Responses API `computer` ツール / Agents SDK サンドボックス / Codex app
- **検証対象**: 新ツール / アップデート
- **バージョン/リリース日**: GPT-5.4（2026-03-05）/ GPT-5.5（2026-04-24）/ ChatGPT agent（2025-07-17 GA）。`computer-use-preview` は 2026-07-23 廃止予定
- **検証期間**: 2026/05/27 -（検証中）
- **検証担当者**:（要記入）
- **検証ステータス**: 検証中

---

## 1. 背景と検証目的

### なぜこの検証を行うのか

- ChatGPT agent はコンシューマ向け面が唯一 GA に到達しており、業務適用の評価対象として優先度が高い
- 専用モデル `computer-use-preview` の廃止予定により、GPT-5.4 / 5.5 へ統合された現行設計の実機評価が必要

### 解決したい課題

- 業務における Web タスク自動化を、コードを書かずに ChatGPT agent で実行できる範囲を確認
- 開発者ハーネス（Responses API + Agents SDK）で自前環境を構築する際の実装コストを把握

### 期待される効果・ビジネスインパクト

- 反復的ブラウザ業務のセルフサービス化
- Agents SDK + 外部サンドボックス（E2B / Modal / Vercel）による安全な実行環境の検証

---

## 2. ツール/機能の基本情報

### 概要

OpenAI は computer use を 3 系統で提供:

1. ChatGPT agent — chatgpt.com 上の総合エージェント（ビジュアル/テキストブラウザ・ターミナル・API）
2. Responses API の `computer` ツール — 開発者が VM などを用意し、スクリーンショット→アクションのループを実装
3. Codex app（macOS） — `@Computer` で macOS GUI を操作

### 提供元

OpenAI（Operator スタンドアロンサイトは 2025-07-17 以降 ChatGPT agent へ統合・サンセット）

### 主要機能

- アクション: `click` / `double_click` / `scroll` / `type` / `wait` / `keypress` / `drag` / `move` / `screenshot`
- Agents SDK サンドボックス連携: Blaxel / Cloudflare / Daytona / E2B / Modal / Runloop / Vercel
- ChatGPT agent は外部 API（Connectors）アクセスも可能

### 技術スタック・アーキテクチャ

- Responses API + `computer` ツール
- Agents SDK（2026-04 更新でサンドボックスをネイティブサポート）
- 入力: テキスト＋スクリーンショット（音声・動画非対応）

---

## 3. 検証方法

### 検証環境

- **使用アカウント**:（要記入）
- **プラン/エディション**: ChatGPT Plus / Pro / Team の評価 + 開発者 API
- **検証環境**: テスト

### 検証シナリオ

1. ChatGPT agent で簡単な Web タスク（情報収集 / フォーム入力）を実行し、成功率・所要時間を計測
2. Responses API の `computer` ツールで Playwright ハーネスを構築して同じタスクを実行
3. Agents SDK の E2B サンドボックスでファイル操作タスクを実行
4. Codex app（macOS）で `@Computer` を呼び macOS GUI 操作の精度を確認

### 検証データ・サンプル

- ベンチ用 Web ページ群（要設計、Anthropic と同条件）

### 前提条件・制約事項

- High-risk action の前に確認フローが入る前提で設計
- Codex は EEA / UK / スイス除外、macOS 限定
- ChatGPT agent: Pro 月 400 メッセージ、その他有料プラン月 40 メッセージ

---

## 4. 検証結果

### 定性的評価

#### 機能面の評価

- 2026/05/28 初回実行: `docker compose exec cua python /app/agent.py "Yahooニュースのトップ見出しを3つ読み上げて"` を実行。ステップ実行・スクリーンショット取得・座標クリック・タイピング・スクロール・ドラッグ全てが基本動作した
- ループ機構（screenshot → action → screenshot の往復）は安定して動く

#### 操作性・UI/UX

- VNC（http://localhost:6080/vnc.html）越しにブラウザ操作の様子をリアルタイム可視化できる。デバッグ容易
- 5900 ポートは生 VNC プロトコル用。ブラウザでは開けない（macOS なら `vnc://localhost:5900`、ブラウザなら 6080 の noVNC）

#### 出力品質

- 初回タスク（「Yahooニュースのトップ見出しを3つ読み上げて」）は16ステップで打ち切り、見出し抽出に到達せず終了
- 失敗原因: デフォルト START_URL が Bing で、検索ステップから始まる必要があった。さらに検索語を「Yahoo新聞」と誤訳し、結果ページで迷子になった
- 「読み上げて」という指示が画面操作系モデルには曖昧で、要約・抽出のどちらをすべきか判断できなかった疑い

#### 実用性

- URL を直接指定し、タスク指示を抽出系の語彙で書けば実用範囲に乗りそうという感触
- ニュース系の素朴な見出し取得タスクでも、初手の指示設計が結果を大きく左右する

---

### 定量的評価

#### 導入コスト

| 項目 | 内容 | 金額/工数 |
| --- | --- | --- |
| 初期設定時間 | API キー発行〜疎通 | （随時更新） |
| 学習時間 | Responses API ループ実装 | （随時更新） |
| 初期費用 | — | $0 |

#### 運用コスト

| 項目 | 内容 | 金額 |
| --- | --- | --- |
| 月額利用料 | ChatGPT Plus / Pro / Team サブスク | — |
| 従量課金 | GPT-5.4: 入 $2.50 / 出 $15.00 / 1M、GPT-5.5: 入 $5.00 / 出 $30.00 / 1M、`computer-use-preview`: 入 $3.00 / 出 $12.00 / 1M | — |
| 追加オプション | ChatGPT agent 追加メッセージはクレジット購入 / per-tool-call 課金示唆あり（未確認） | — |

#### パフォーマンス

| 項目 | 測定結果 | 備考 |
| --- | --- | --- |
| 処理速度 | （要計測） | |
| レスポンスタイム | （要計測） | |
| 同時処理数 | （要確認） | 公式明示なし |
| 成功率 | （要計測） | |

#### ROI試算

- （随時更新）

---

## 5. 比較・優位性分析

### 既存ツール/類似サービスとの比較

| 項目 | OpenAI Computer Use | Anthropic Computer Use | Google Gemini Computer Use |
| --- | --- | --- | --- |
| 機能性 | チャット UI＋API＋Codex で広域 | デスクトップ全般 / `zoom` 機能 | ブラウザ＋Android |
| コスト | GPT-5.4 入 $2.50 / 出 $15 | Opus 4.7 入 $5 / 出 $25 | $1.25〜2.50 / $10〜15 |
| 使いやすさ | ChatGPT agent はノーコード | コンテナデモ前提 | Vertex AI 統合 |
| 連携性 | Agents SDK でサンドボックスネイティブ対応 | Bedrock / Vertex AI 経由 | Agent Sandbox |
| サポート | ChatGPT agent は GA | Public Beta | Preview |

### 優位性

- コンシューマ向け面（ChatGPT agent）が唯一 GA に到達
- Agents SDK が外部サンドボックスをネイティブサポート
- High-risk action gating の確認要求リコール率 92%（公式）

### 劣位性・懸念点

- 専用モデル `computer-use-preview` が 2026-07-23 廃止予定、移行が必要
- 同時実行・タイムアウト・per-tool-call 料金の具体数値が公式不明
- Codex の computer use は EEA / UK / スイス除外

---

## 6. リスク評価

### セキュリティ

| 評価項目 | 評価 | 詳細 |
| --- | --- | --- |
| データ保管場所 | （要確認） | API 利用時のデータ取り扱いを再確認 |
| 暗号化 | （要確認） | 通常の OpenAI API と同等 |
| アクセス制御 | （要確認） | API キー / ChatGPT サブスク |
| ログ管理 | （要確認） | 3 層安全設計（モデル/Operator/プロセス） |
| コンプライアンス | （要確認） | Codex は地域除外あり |

### プライバシー・倫理面

- ChatGPT agent はリモートのビジュアルブラウザ環境で実行されるため、機密情報を扱う際の取り扱いを設計する必要あり
- ToS と Operator System Card のガイドラインに従う

### ベンダーロックインリスク

- Responses API / Agents SDK は OpenAI 固有。サンドボックスは外部ベンダー（E2B 等）にも依存

### 技術的リスク

- 専用モデル廃止に伴う移行コスト
- preview から GA への変更タイミング

---

## 7. 連携性・拡張性

### 既存システムとの連携

| 連携先 | 方法 | 難易度 | 備考 |
| --- | --- | --- | --- |
| E2B | Agents SDK ネイティブ | 低 | サンドボックス実行 |
| Modal | Agents SDK ネイティブ | 低 | サンドボックス実行 |
| Vercel / Cloudflare | Agents SDK ネイティブ | 低 | エッジ実行 |
| Playwright / Selenium | カスタムハーネス | 中 | Responses API + 自前環境 |

### API/統合オプション

- Responses API
- Agents SDK
- Codex app（macOS）

### 拡張性・カスタマイズ性

- Built-in Computer tool / Custom harness / Code-execution 環境の 3 パターンを公式が提示

---

## 8. 実際の使用例・サンプル

### ユースケース1

**シナリオ**: ChatGPT agent で Web 情報収集タスクを実行
**入力**:（要記入）
**出力**:（要記入）
**評価**:（要記入）

### ユースケース2: Yahoo!ニュース見出し抽出（2026/05/28 初回検証）

**シナリオ**: Docker Compose で起動した Responses API ハーネスに「Yahooニュースのトップ見出しを3つ読み上げて」と指示

**入力（実行コマンド）**:
```bash
docker compose exec cua python /app/agent.py "Yahooニュースのトップ見出しを3つ読み上げて"
```

**出力（agent ログ抜粋）**:
- step 1〜16 で click / type / keypress / wait / scroll / drag を順次実行
- 検索語として `Yahoo新聞` をタイピング（誤訳）
- 16ステップで打ち切り、最終応答は「I encountered some issues accessing the Yahoo News Japan site directly from the search results. Would you like me to try accessing it through a different approach, or would you prefer the Bing link?」

**評価**:
- ❌ 見出し抽出は未達成
- ✅ Computer Use ループ自体は完全動作（接続疎通・座標精度・スクリーンショット送信は問題なし）
- 課題: 初期 URL とタスク指示の設計で結果が大きく変わる

### スクリーンショット・デモ

- （随時更新）

---

## 9. 学びとナレッジ

### 発見したこと

- 2026/05/28: Computer Use の弱点は「最初の遷移を AI に任せると寄り道する」。初期 URL とタスクプロンプトの設計で精度が大きく変わる
- VNC は 6080 (noVNC web) と 5900 (raw VNC protocol) で用途が異なる。ブラウザは 6080、デスクトップアプリ（macOS Screen Sharing 等）は 5900

### うまくいったこと

- （随時更新）

### うまくいかなかったこと

- 2026/05/28: Yahoo!ニュース見出し抽出タスクが16ステップで打ち切り。原因は初期 URL が Bing で検索フローから始まったこと、検索語の誤訳（「Yahoo新聞」）、指示の曖昧さ（「読み上げて」）の複合

### Tips・ベストプラクティス

- High-risk action gating を無効化しない（OpenAI ToS / 公式推奨に従う）
- 開発者は分離 VM / human-in-the-loop を組み合わせて運用する
- `computer-use-preview` は新規利用を避け、GPT-5.4 mini / GPT-5.4 / 5.5 への移行を計画する

**タスク指示・環境設計の知見（2026/05/28 初回実行から）**:

- **初期 URL を直接指定する** — `.env` の `START_URL` をターゲットサイトに合わせて変更する（例: `START_URL=https://news.yahoo.co.jp/`）。デフォルトの Bing 起点だと検索ステップが入り、誤訳・寄り道のリスクが大きく増える
- **「読み上げて」より「抽出して列挙」** — 画面操作系モデルは抽出/要約の判別が曖昧。動作動詞は具体的に書く
- **要約禁止を明示する** — 「要約や言い換えはしないこと」と書くと勝手な意訳が減る
- **HTML 構造に近い語彙を使う** — 「主要ニュース」など、画面上のセクション名に近い語を使うと精度が上がる
- **MAX_STEPS は段階的に上げる** — 標準 30 で十分なケースが多い。途中で諦めるなら 50 に上げるが、コストは線形に増える
- **VNC を見ながらデバッグ** — `http://localhost:6080/vnc.html` を開いた状態で agent を走らせると、迷子になる箇所が即座に見える

**推奨タスクプロンプト例（見出し抽出）**:
```
現在開いている Yahoo!ニュースのページから、最上部にある主要ニュースの見出しを上から3つ、そのままの文字で抽出して列挙してください。要約や言い換えはしないこと。
```

### よくあるエラーと対処法

- （随時更新）

---

## 10. 判定と今後のアクション

### 総合評価

⭐️⭐️⭐️⭐️⭐️（完了時に記入）

### 導入判定

- [ ] 即座に導入推奨
- [ ] 条件付きで導入可
- [ ] 追加検証が必要
- [ ] 導入見送り

### 判定理由

- （完了時に記入）

### 次のステップ

- [ ] ChatGPT agent でノーコード Web タスクの成功率を計測
- [ ] Responses API + Playwright ハーネスでカスタム実装
- [ ] Agents SDK サンドボックス（E2B / Modal）の検証
- [ ] Codex app の computer use を macOS で検証

### 追加で検証したい項目

- GPT-5.4 と GPT-5.5 の computer use 性能差
- per-tool-call 課金が存在するなら、その実額

---

📚 関連リソース

### 公式ドキュメント

- [Computer use | OpenAI API](https://developers.openai.com/api/docs/guides/tools-computer-use)
- [Introducing ChatGPT agent | OpenAI](https://openai.com/index/introducing-chatgpt-agent/)
- [The next evolution of the Agents SDK | OpenAI](https://openai.com/index/the-next-evolution-of-the-agents-sdk/)
- [Operator System Card | OpenAI](https://openai.com/index/operator-system-card/)
- [Deprecations | OpenAI API](https://developers.openai.com/api/docs/deprecations)

### 参考記事・事例

- 一次情報のみを採用

### 社内関連ドキュメント

- 横断比較: `16_検証ラボ/lab-research-20260527-computer-use-3vendors/compare.md`
- 詳細レポート: `16_検証ラボ/lab-research-20260527-computer-use-3vendors/openai/report.md`

### 検証データ・ログ

- （随時更新）

---

✅ メモ・議論ログ

- 2026/05/27: 一次情報リサーチ結果を元に初期メモを反映
- 2026/05/28: Docker Compose 環境で初回タスク実行。基本動作確認は OK、見出し抽出は未達成。改善案（START_URL 直指定 / プロンプト具体化 / MAX_STEPS 調整 / VNC デバッグ手順）を「学びとナレッジ」に追記
- 2026/05/28: 数十サイト横断ニュース収集システムのコスト試算を実施。詳細は `16_検証ラボ/lab-computer-use-3vendors/cost-estimation.md` 参照。OpenAI GPT-5.4 + cache で30サイト/月 約$54〜81、既存Playwright方式の約10倍だがセレクタ保守ゼロのメリット

---

## 📝 更新ログ
<!-- このセクションはスキルが自動で追記する。手動編集不要。 -->
| 日時 | 更新内容の概要 |
|---|---|
| 2026/05/27 | ファイル作成（init）。3社横断リサーチ結果から既知情報を反映 |
| 2026/05/28 | 初回タスク実行結果（Yahoo!ニュース見出し抽出）と改善知見を追記。ユースケース2 / Tips / 発見したこと / うまくいかなかったこと / メモログを更新 |
