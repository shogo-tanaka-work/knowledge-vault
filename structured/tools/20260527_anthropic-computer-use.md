# Anthropic Computer Use 検証ログ

> ステータス: 検証中
> 作成日: 2026/05/27
> 最終更新: 2026/05/27
> ファイルパス: /Users/shogo/Documents/ai-business-os/15_ナレッジ基盤/vault/structured/tools/20260527_anthropic-computer-use.md

---

## 📋 検証概要

- **ツール/サービス名**: Anthropic Claude Computer Use（`computer_use` tool）
- **検証対象**: 新ツール / アップデート（`computer_20251124`）
- **バージョン/リリース日**: tool バージョン `computer_20251124`（最新）、`computer_20201022`（旧）。ベータヘッダー `computer-use-2025-11-24`
- **検証期間**: 2026/05/27 -（検証中）
- **検証担当者**:（要記入）
- **検証ステータス**: 検証中

---

## 1. 背景と検証目的

### なぜこの検証を行うのか

- 2026年5月末時点で Anthropic / OpenAI / Google の Computer Use 系機能の差を実機で把握し、業務適用の意思決定に使う
- Anthropic は API オンリーでコンテナ運用前提という独自の立ち位置を取っており、開発者統合・長尺タスクの観点で他社と比較する必要がある

### 解決したい課題

- 社内業務の中で「ブラウザ・GUI を AI に操作させる」ユースケースの実現可能性とコストを定量化する
- セキュリティ要件（プロンプトインジェクション対策・確認フロー）が社内ガイドラインに合致するかを確認する

### 期待される効果・ビジネスインパクト

- 反復的なブラウザ業務の自動化（社内ツール操作 / 情報収集）
- Opus 4.7 の高い視覚認識精度を活かせるユースケース（OCR 的タスク・複雑 UI の操作）の特定

---

## 2. ツール/機能の基本情報

### 概要

Claude モデルにスクリーンショットを与え、`computer_use` ツール経由でマウス・キーボード操作を実行させる仕組み。2024-10 公開以降、2026-05 時点でも Public Beta 継続中。

### 提供元

Anthropic（API 経由 / Amazon Bedrock / Google Cloud Vertex AI で提供）

### 主要機能

- アクション: `screenshot` / `left_click` / `right_click` / `double_click` / `middle_click` / `left_click_drag` / `type` / `key` / `scroll` / `mouse_move` / `cursor_position`
- 新ツールバージョン `computer_20251124` で `zoom`（領域拡大）追加
- Opus 4.7 は長辺 2,576px の大型画像入力に対応

### 技術スタック・アーキテクチャ

- Messages API + `anthropic-beta: computer-use-2025-11-24` ヘッダー
- 公式デモは Ubuntu + X11 + VNC を Docker コンテナで動作

---

## 3. 検証方法

### 検証環境

- **使用アカウント**:（要記入）
- **プラン/エディション**: Anthropic API 直接アクセス（要検討: Bedrock / Vertex AI 経由）
- **検証環境**: テスト

### 検証シナリオ

1. 公式 Docker デモ `ghcr.io/anthropics/anthropic-quickstarts:computer-use-demo-latest` を起動し、ベースラインを確認
2. 単純な Web フォーム入力タスク（成功率・所要トークン数を計測）
3. 複雑な UI（社内ダッシュボード / Google Sheets 等）での操作精度確認
4. Opus 4.7 の `zoom` 機能を使った高密度 UI の正答率比較

### 検証データ・サンプル

- ベンチ用 Web ページ群（要設計）

### 前提条件・制約事項

- 隔離環境（VM / コンテナ）で実行する
- 機密データを含むセッションは扱わない

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
| 初期設定時間 | Docker デモ起動〜疎通確認 | （随時更新） |
| 学習時間 | API ループ実装の習得 | （随時更新） |
| 初期費用 | API キー発行のみ | $0 |

#### 運用コスト

| 項目 | 内容 | 金額 |
| --- | --- | --- |
| 月額利用料 | サブスク無し（従量） | $0 |
| 従量課金 | Opus 4.7: 入 $5/MTok・出 $25/MTok / Sonnet 4.6: 入 $3・出 $15 / Haiku 4.5: 入 $1・出 $5 | — |
| 追加オプション | Batch API で入力 50% 割引 | — |
| ベータ overhead | システムプロンプトに 466〜499 トークン加算 | — |

#### パフォーマンス

| 項目 | 測定結果 | 備考 |
| --- | --- | --- |
| 処理速度 | （要計測） | アクションあたりの平均レイテンシ |
| 同時処理数 | 公式明示なし（要計測） | |
| 成功率 | （要計測） | シナリオ別 |

#### ROI試算

- （随時更新）

---

## 5. 比較・優位性分析

### 既存ツール/類似サービスとの比較

| 項目 | Anthropic Computer Use | OpenAI Responses API computer | Google Gemini Computer Use |
| --- | --- | --- | --- |
| 機能性 | デスクトップ全般 / `zoom` 機能 | 任意の環境を開発者が用意 | ブラウザ＋Android |
| コスト | Opus 4.7 入 $5/出 $25 | GPT-5.4 入 $2.50/出 $15 | $1.25〜2.50/$10〜15 |
| 使いやすさ | コンテナデモが成熟 | Agents SDK でサンドボックス連携 | Vertex AI 統合 |
| 連携性 | Bedrock / Vertex AI に並列展開 | E2B / Modal / Vercel ネイティブ | Agent Sandbox |
| サポート | Public Beta | 一部 GA（ChatGPT agent） | Preview |

### 優位性

- 視覚認識精度（Opus 4.7 で XBOW 報告 98.5%）
- OSWorld で Opus 4.5 が 66.26% と高水準
- VM / コンテナでの隔離運用が公式ガイドラインで明確
- 大型画像入力（長辺 2,576px）に対応

### 劣位性・懸念点

- claude.ai 通常 UI で利用できないため、エンドユーザー向け面が存在しない
- Beta 継続中で破壊的変更リスクがある
- 同時実行・タイムアウト等の定量制約が公式に明示されていない

---

## 6. リスク評価

### セキュリティ

| 評価項目 | 評価 | 詳細 |
| --- | --- | --- |
| データ保管場所 | （要確認） | ZDR 契約で API 処理後保持しない |
| 暗号化 | （要確認） | 通常の Anthropic API と同等 |
| アクセス制御 | （要確認） | API キーベース |
| ログ管理 | （要確認） | スクリーンショット等はクライアント側に保存 |
| コンプライアンス | （要確認） | Beta 機能であり破壊的変更の可能性あり |

### プライバシー・倫理面

- スクリーンショット内に個人情報が含まれる場合の取り扱いを設計する必要あり
- 自動プロンプトインジェクション検出はあるが、最終的にユーザー確認が必須

### ベンダーロックインリスク

- API 互換は Bedrock / Vertex AI 経由でも利用可能で、純粋な Anthropic 単独ロックインは緩和されている

### 技術的リスク

- ベータの破壊的変更
- 視覚モデル特有の誤認識リスク

---

## 7. 連携性・拡張性

### 既存システムとの連携

| 連携先 | 方法 | 難易度 | 備考 |
| --- | --- | --- | --- |
| AWS Bedrock | `API_PROVIDER=bedrock` | 低 | （要検証） |
| GCP Vertex AI | `API_PROVIDER=vertex` | 低 | （要検証） |
| Playwright | カスタムハーネス | 中 | 公式デモは VNC ベース |

### API/統合オプション

- Messages API（ベータヘッダー付き）
- Docker コンテナの参照実装

### 拡張性・カスタマイズ性

- 解像度を `WIDTH` / `HEIGHT` で変更可能
- カスタムツール定義との併用可能

---

## 8. 実際の使用例・サンプル

### ユースケース1

**シナリオ**: 公式デモを起動して画面操作ループを確認
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

- 隔離環境（VM / Docker）で動作させる
- 推奨解像度 1024×768 から開始する
- スクリーンショットは画像トークンとして課金されるため、`zoom` 機能でリージョン限定取得を活用する

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

- [ ] 公式 Docker デモを起動して動作確認
- [ ] 簡単な Web タスクで成功率・所要トークン数を計測
- [ ] Opus 4.7 / Sonnet 4.6 / Haiku 4.5 のコスト・精度比較
- [ ] OpenAI / Google との横断ベンチ実施

### 追加で検証したい項目

- `zoom` 機能を活用した高密度 UI の精度
- Bedrock / Vertex AI 経由でのレイテンシ・コスト差

---

📚 関連リソース

### 公式ドキュメント

- [Computer use tool - Claude API Docs](https://platform.claude.com/docs/en/docs/agents-and-tools/tool-use/computer-use-tool)
- [Beta headers - Claude API Docs](https://platform.claude.com/docs/en/api/beta-headers)
- [Introducing computer use, a new Claude 3.5 Sonnet](https://www.anthropic.com/news/3-5-models-and-computer-use)
- [Claude Opus 4.5 system card](https://www.anthropic.com/claude-opus-4-5-system-card)

### 参考記事・事例

- 一次情報のみを採用（2次情報は除外）

### 社内関連ドキュメント

- 横断比較: `16_検証ラボ/lab-research-20260527-computer-use-3vendors/compare.md`
- 詳細レポート: `16_検証ラボ/lab-research-20260527-computer-use-3vendors/anthropic/report.md`

### 検証データ・ログ

- （随時更新）

---

✅ メモ・議論ログ

- 2026/05/27: 一次情報リサーチ結果を元に初期メモを反映
- 2026/05/28: 数十サイト横断ニュース収集システムのコスト試算を実施。詳細は `16_検証ラボ/lab-computer-use-3vendors/cost-estimation.md` 参照。Sonnet 4.6 + prompt cache で1サイト約$0.08〜0.10、Opus 4.7 は新トークナイザで+35%なのでさらに高め

---

## 📝 更新ログ
<!-- このセクションはスキルが自動で追記する。手動編集不要。 -->
| 日時 | 更新内容の概要 |
|---|---|
| 2026/05/27 | ファイル作成（init）。3社横断リサーチ結果から既知情報を反映 |
