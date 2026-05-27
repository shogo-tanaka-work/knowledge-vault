# OpenAI Computer Use（ChatGPT agent / Responses API computer ツール）検証ログ

> ステータス: 検証中
> 作成日: 2026/05/27
> 最終更新: 2026/05/27
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

- （随時更新）

#### 操作性・UI/UX

- （随時更新）

#### 出力品質

- （随時更新）

#### 実用性

- （随時更新）

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

### スクリーンショット・デモ

- （随時更新）

---

## 9. 学びとナレッジ

### 発見したこと

- （随時更新）

### うまくいったこと

- （随時更新）

### うまくいかなかったこと

- （随時更新）

### Tips・ベストプラクティス

- High-risk action gating を無効化しない（OpenAI ToS / 公式推奨に従う）
- 開発者は分離 VM / human-in-the-loop を組み合わせて運用する
- `computer-use-preview` は新規利用を避け、GPT-5.4 mini / GPT-5.4 / 5.5 への移行を計画する

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

---

## 📝 更新ログ
<!-- このセクションはスキルが自動で追記する。手動編集不要。 -->
| 日時 | 更新内容の概要 |
|---|---|
| 2026/05/27 | ファイル作成（init）。3社横断リサーチ結果から既知情報を反映 |
