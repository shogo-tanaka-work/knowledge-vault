# Google Computer Use（Gemini Computer Use / Project Mariner）検証ログ

> ステータス: 検証中
> 作成日: 2026/05/27
> 最終更新: 2026/05/27
> ファイルパス: /Users/shogo/Documents/ai-business-os/15_ナレッジ基盤/vault/structured/tools/20260527_google-project-mariner.md

---

## 📋 検証概要

- **ツール/サービス名**: Google Gemini Computer Use API / Project Mariner / Vertex AI Computer Use
- **検証対象**: 新ツール / アップデート
- **バージョン/リリース日**: `gemini-2.5-computer-use-preview-10-2025`（2025-10-07 Public Preview）／ Gemini 3 Pro / Flash Preview に組み込みサポート追加（2026-01-29）
- **検証期間**: 2026/05/27 -（検証中）
- **検証担当者**:（要記入）
- **検証ステータス**: 検証中

---

## 1. 背景と検証目的

### なぜこの検証を行うのか

- Google は Gemini Developer API と Vertex AI の双方から Computer Use を提供しており、GCP 既存環境を持つチームには統合の利点がある
- Agent Sandbox / Agent Gateway / Model Armor といった Google Cloud Next '26 発表の企業向け機能の実用性を確認する

### 解決したい課題

- ブラウザ・モバイル UI を主体とした業務自動化の実現可能性とコストを評価
- 安全境界（`safety_decision` フィールド・ToS の確認バイパス禁止）を実装に組み込む難易度を確認

### 期待される効果・ビジネスインパクト

- GCP 環境のチームにとって Vertex AI 上での統合運用が可能
- Android UI 操作対応により、モバイル業務自動化の可能性

---

## 2. ツール/機能の基本情報

### 概要

- Gemini モデルにスクリーンショットを与え、1000×1000 グリッド座標で 13 種のアクションを返す
- Project Mariner は DeepMind 提供の UI エージェント製品（Chrome 拡張）。米国 Google AI Ultra 限定
- 全体的に Preview 扱い（GA なし）

### 提供元

Google（Google DeepMind / Google Cloud）

### 主要機能

13 アクション:

| カテゴリ | アクション |
|---|---|
| ナビゲーション | `open_web_browser` / `navigate` / `go_back` / `go_forward` / `search` |
| インタラクション | `click_at` / `hover_at` / `type_text_at` / `key_combination` / `drag_and_drop` |
| スクロール | `scroll_document` / `scroll_at` |
| タイミング | `wait_5_seconds` |

カスタム関数による拡張も可能。

### 技術スタック・アーキテクチャ

- Gemini API（generateContent API） / Interactions API（Beta） / Vertex AI Generative AI SDK
- Agent Sandbox による隔離実行（Google Cloud Next '26）

---

## 3. 検証方法

### 検証環境

- **使用アカウント**:（要記入）
- **プラン/エディション**: Gemini Developer API（Paid Tier）/ Vertex AI
- **検証環境**: テスト

### 検証シナリオ

1. AI Studio から `gemini-2.5-computer-use-preview-10-2025` で簡単な Web タスクを実行
2. Vertex AI 経由で同じタスクを実行し、コスト・レイテンシを計測
3. Gemini 3 Pro / Flash Preview での組み込み computer use と比較
4. `safety_decision` のリクエスト承認フローを実装して、UX 影響を評価

### 検証データ・サンプル

- ベンチ用 Web ページ群（要設計、Anthropic / OpenAI と同条件）

### 前提条件・制約事項

- 推奨解像度 1440×900 / 入力 128K / 出力 64K トークン
- `gemini-3.5-flash` は Computer Use 非対応
- 公式に「エラーと脆弱性が生じやすい可能性」と注意喚起

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
| 初期設定時間 | AI Studio または Vertex AI のセットアップ | （随時更新） |
| 学習時間 | API ループ＋座標系の習得 | （随時更新） |
| 初期費用 | — | $0 |

#### 運用コスト

| 項目 | 内容 | 金額 |
| --- | --- | --- |
| 月額利用料 | サブスク無し（従量） | $0 |
| 従量課金 | Gemini Developer API: 入 $1.25（≤200K）/ $2.50（>200K）、出 $10.00 / $15.00 / 1M | — |
| Vertex AI | Gemini 2.5 Pro SKU と同一レート | — |
| 無料枠 | なし | — |

#### パフォーマンス

| 項目 | 測定結果 | 備考 |
| --- | --- | --- |
| 処理速度 | （要計測） | Online-Mind2Web で約 225 秒（公式） |
| レスポンスタイム | （要計測） | |
| 同時処理数 | 公式明示なし | |
| 成功率 | （要計測） | Online-Mind2Web 70%+ |

#### ROI試算

- （随時更新）

---

## 5. 比較・優位性分析

### 既存ツール/類似サービスとの比較

| 項目 | Google Gemini Computer Use | Anthropic Computer Use | OpenAI Computer Use |
| --- | --- | --- | --- |
| 機能性 | ブラウザ＋Android | デスクトップ全般 | チャット UI＋API＋Codex |
| コスト | 入 $1.25〜2.50 / 出 $10〜15（/1M） | 入 $5 / 出 $25（Opus 4.7） | 入 $2.50 / 出 $15（GPT-5.4） |
| 使いやすさ | Vertex AI 統合 | コンテナデモ | ChatGPT agent でノーコード |
| 連携性 | Agent Sandbox / Agent Gateway | Bedrock / Vertex AI | Agents SDK サンドボックス |
| サポート | Preview | Public Beta | ChatGPT agent は GA |

### 優位性

- Vertex AI 統合により GCP 既存環境にスムーズに組み込める
- 入力料金が 3 社中最も安価（≤200K で $1.25/1M）
- Android UI 対応
- `safety_decision` による明示的な承認フロー設計
- Online-Mind2Web 70%+ で公式リーダーシップ主張

### 劣位性・懸念点

- 全体的に Preview 扱いで GA なし
- 公式に「エラーと脆弱性が生じやすい可能性」と注意喚起
- OSWorld / WebVoyager 等の具体数値が公式ブログ画像内（数値未抽出）
- 無料枠なし
- Project Mariner は米国 Google AI Ultra 限定で日本から UI 経由では利用不可

---

## 6. リスク評価

### セキュリティ

| 評価項目 | 評価 | 詳細 |
| --- | --- | --- |
| データ保管場所 | （要確認） | Vertex AI 一般のデータ保護に準拠と推測 |
| 暗号化 | （要確認） | Vertex AI 標準 |
| アクセス制御 | （要確認） | GCP IAM / API キー |
| ログ管理 | （要確認） | Vertex AI Agent Gateway でログ集約可能 |
| コンプライアンス | （要確認） | Preview のため変更可能性あり |

### プライバシー・倫理面

- ToS で `require_confirmation` の自動バイパスを明示的に禁止
- 禁止ユースケース: CAPTCHA 解析、ユーザー同意なしの法的条件承認、明示的承認なしの金融取引

### ベンダーロックインリスク

- GCP / Vertex AI への統合が深い場合、移行コストは高め

### 技術的リスク

- Preview のため API 仕様変更リスク
- 同時実行・タイムアウト等の定量制約が公式不明

---

## 7. 連携性・拡張性

### 既存システムとの連携

| 連携先 | 方法 | 難易度 | 備考 |
| --- | --- | --- | --- |
| Vertex AI | Gen AI SDK for Python | 低 | （要検証） |
| Agent Sandbox | Vertex AI 経由 | 中 | Google Cloud Next '26 で一般提供 |
| Browserbase | 公式ライブデモがホスト | 中 | （要確認） |

### API/統合オプション

- Gemini Developer API（generateContent）
- Interactions API（Beta）
- Vertex AI Computer Use

### 拡張性・カスタマイズ性

- カスタム関数によるアクション拡張
- 1000×1000 グリッド座標を実画面解像度にスケーリング

---

## 8. 実際の使用例・サンプル

### ユースケース1

**シナリオ**: AI Studio で `gemini-2.5-computer-use-preview-10-2025` を呼び出して Web タスクを実行
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

- `safety_decision` フィールドをアプリケーション側で必ず処理する
- サンドボックス VM / コンテナでの実行を前提とする
- ナビゲーション許可リスト / ブロックリストをカスタムシステムプロンプトに含める

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

- [ ] AI Studio で `gemini-2.5-computer-use-preview-10-2025` の動作確認
- [ ] Vertex AI 経由でコスト・レイテンシ計測
- [ ] Gemini 3 Pro / Flash Preview の組み込み computer use 検証
- [ ] Agent Sandbox 実環境での隔離動作確認

### 追加で検証したい項目

- Android UI 操作の精度
- Agent Gateway + Model Armor の挙動
- Gemini 3.5 Pro での Computer Use 対応状況（現状未確認）

---

📚 関連リソース

### 公式ドキュメント

- [Gemini Computer Use Model ブログ](https://blog.google/innovation-and-ai/models-and-research/google-deepmind/gemini-computer-use-model/)
- [Gemini API Computer Use (generateContent API)](https://ai.google.dev/gemini-api/docs/computer-use)
- [Gemini API Computer Use (Interactions API)](https://ai.google.dev/gemini-api/docs/interactions/computer-use)
- [Vertex AI Computer Use](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/computer-use)
- [Google Cloud Next 2026 Wrap-Up](https://cloud.google.com/blog/topics/google-cloud-next/google-cloud-next-2026-wrap-up)

### 参考記事・事例

- 一次情報のみを採用

### 社内関連ドキュメント

- 横断比較: `16_検証ラボ/lab-research-20260527-computer-use-3vendors/compare.md`
- 詳細レポート: `16_検証ラボ/lab-research-20260527-computer-use-3vendors/google/report.md`

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
