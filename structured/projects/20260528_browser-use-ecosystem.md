# browser-use エコシステム ローカル検証 検証ログ

> ステータス: 進行中
> 作成日: 2026/05/28
> 最終更新: 2026/05/28（リサーチ追記）
> ファイルパス: /Users/shogo/Documents/ai-business-os/15_ナレッジ基盤/vault/structured/projects/20260528_browser-use-ecosystem.md

---

📋 プロジェクト概要
* カテゴリ: ブラウザ自動化基盤 / AI 記事執筆自動化のホスト先選定
* 期間: 2026/05/28 -（検証中）
* 主要メンバー: shogo
* ステークホルダー: shogo（AI 事業 OS オーナー）
* プロジェクトステータス: 進行中

---

## 1. 背景と目的

* 先行ラボ `lab-computer-use-3vendors` で Anthropic / OpenAI / Google の Computer Use を比較。コスト・トークン消費の論点が整理された
* AI 記事執筆自動化パイプラインのブラウザ操作基盤として、Computer Use よりトークン効率と運用コストを下げられる代替が必要
* 候補が browser-use 社の OSS エコシステム（メインライブラリ / browser-harness / SDK / workflow-use 等）
* 本 PJ では各リポをローカル環境で順次触り、無料枠クラウド（Cloudflare 系優先、Render/Railway 除外）にホストする価値があるかを評価する

---

## 2. 取り組み内容

### 実施した施策・活動

* 2026/05/28: web-researcher による browser-use 組織 GitHub の網羅リサーチ完了（公開 44 リポのうち上位 ~13 件の用途・LLM-callable 性・ホスト適性・直近更新日を整理）
* 2026/05/28: 検証ラボ `16_検証ラボ/lab-browser-use-ecosystem/` 作成。リポ単位サブディレクトリ 9 個を切る
* 2026/05/28: 全 9 リポの技術深掘りリサーチを web-researcher 3 並列で実施し、各サブディレクトリに `report.md` を配置（概要・アーキ・機能・インストール・LLM 呼び出し経路・コンテナ適性・コスト・直近更新・強弱・検証お題）

### 使用したツール・技術

* GitHub Organization: https://github.com/browser-use
* 検証対象（優先順位順）:
  * 第1波（マスト）: `browser-use`（メイン Python）/ `browser-harness` / `sdk`
  * 第2波: `workflow-use` / `agent-sdk`
  * 第3波: `video-use`
  * 第4波: `bux` / `desktop` / `web-ui`
* ホスト候補: Cloudflare Workers / Containers、Oracle Cloud Free Tier、Fly.io、GCP Cloud Run 常時無料分、Browser Use Cloud（ハイブリッド案）

### 主要な意思決定とその理由

* **ローカル検証を先行**：Fargate 等にホストする前に各リポをローカルで触り、実機の手触り・トークン消費・ホスト難易度を確認してから判断する
* **Render / Railway は除外**：無料枠の空きがない / 制約がきつい状況のため
* **Cloudflare 優先**：Workers / Containers の無料枠とエッジ実行の親和性を見たい

---

## 3. 進捗と成果

### 達成できたこと

* 2026/05/28: GitHub Organization の網羅リサーチ完了。各リポの位置付けと推奨組合せ（`browser-use --mcp` + `browser-harness` + `agent-sdk` を Fargate 化）を整理
* 2026/05/28: 9 リポの技術 report.md 完成。リサーチで判明した重要事実:
  - **workflow-use は v0.2.11（2024-11）止まりで事実上メンテ停滞中**、かつ AGPL-3.0 → 採用優先度を下げるべき
  - **web-ui は v3.0.0 で VibeSurf（Chrome 拡張）に変革**、Gradio/Docker 構成は実質レガシー
  - **video-use はコミット 16 件で PoC 段階**、プロダクション投入は非推奨
  - **agent-sdk は MIT・Playwright 不要で 256MB RAM 動作可** → Cloudflare 戦略との相性が良い
  - **sdk（Cloud SDK）が Cloudflare Workers/Pages に直接デプロイ可能な唯一の選択肢**（ブラウザ不要のため）
  - **bux は Ubuntu 専用・Docker 非対応**、Fargate 構想と思想が違うことを確認

### 定量的な成果

* （随時更新）

### 定性的な成果

* （随時更新）

---

## 4. 学びとナレッジ

### うまくいったこと（Good）

* （随時更新）

### うまくいかなかったこと（Bad）

* （随時更新）

### 改善ポイント（Improve）

* （随時更新）

### 技術的な発見・Tips

* `browser-use` メインリポは `uvx --from 'browser-use[cli]' browser-use --mcp` で stdio MCP サーバーとして即起動できる
* `browser-harness` は Computer Use 比でトークン消費が約 1/8（出典: simonlin.net の 2026 update 記事）
* `workflow-use` は AGPL v3.0 のため商用利用時のライセンス確認が必須
* `bux` は systemd 前提の VPS 常駐型で、Fargate 構想とはアーキ思想が異なる

---

## 5. 課題と対応

### 発生した課題

* （随時更新）

### 対応方法

* （随時更新）

### 未解決の課題

* 第1波検証後、stdio MCP を HTTP/SSE にラップするレイヤーの安定性が未確認
* Cloudflare Workers でブラウザバイナリを同梱できるかは要検証

---

## 6. コストとリソース

### 人的リソース

* shogo 単独

### 金銭的コスト

* ローカル検証フェーズ: $0 を想定（LLM API トークンのみ）
* クラウドホストフェーズ: 無料枠優先、超過時のみ実費

### コスト対効果

* （完了時に記入）

---

## 7. 今後の展開

### 次のアクション

1. `01-browser-use/` から着手 — `--mcp` 起動 + Claude Code 連携の最小検証
2. `02-browser-harness/` — CDP 直結ハーネスでトークン消費を実測
3. `03-sdk/` — Cloud API 経由の最小タスク
4. 第1波完了時点で `hosting-plan.md` 初稿を書く
5. 第2波（workflow-use / agent-sdk）→ 第3波（video-use）→ 第4波（bux / desktop / web-ui）

### 横展開の可能性

* AI 記事執筆自動化パイプライン本体への組み込み
* note 記事化（Computer Use 比較続編として）

### 長期的な改善案

* （要記入）

---

📚 関連リソース

### 成果物・ドキュメント

* ラボ実体: `/Users/shogo/Documents/ai-business-os/16_検証ラボ/lab-browser-use-ecosystem/`
* 先行ラボ: `/Users/shogo/Documents/ai-business-os/16_検証ラボ/lab-computer-use-3vendors/`
* プラン: `/Users/shogo/.claude/plans/16-15-16-github-url-llm-cli-https-githu-imperative-axolotl.md`

### 参考資料

* [browser-use/browser-use](https://github.com/browser-use/browser-use)
* [MCP Server - Browser Use](https://docs.browser-use.com/open-source/customize/integrations/mcp-server)
* [browser-use/browser-harness](https://github.com/browser-use/browser-harness)
* [Browser Harness in 2026: Still the Most Token-Efficient Browser Tool](https://www.simonlin.net/tutorials/browser-harness-2026-update/)
* [browser-use/sdk](https://github.com/browser-use/sdk)
* [browser-use/bux](https://github.com/browser-use/bux)
* [browser-use/workflow-use](https://github.com/browser-use/workflow-use)
* [browser-use/agent-sdk](https://github.com/browser-use/agent-sdk)
* [browser-use/web-ui](https://github.com/browser-use/web-ui)
* [browser-use/video-use](https://github.com/browser-use/video-use)
* [browser-use/desktop](https://github.com/browser-use/desktop)
* [browser-use/terminal](https://github.com/browser-use/terminal)
* [Implementing Nova Act MCP Server on ECS Fargate（参考実装）](https://aws.plainenglish.io/implementing-nova-act-mcp-server-on-ecs-fargate-bd79f7c63db2)

### 関連プロジェクト

* `lab-computer-use-3vendors`（先行比較ラボ）
* 10_プロジェクト 配下の AI 記事執筆自動化（ホスト先候補として本検証結果を流し込む）

---

✅ メモ・雑記

* （随時追記）

---

## 📝 更新ログ
<!-- このセクションはスキルが自動で追記する。手動編集不要。 -->
| 日時 | 更新内容の概要 |
|---|---|
| 2026/05/28 | ファイル作成（init）。背景・対象リポ・優先順位・次のアクションまでを初期入力 |
| 2026/05/28 | update: 9 リポの技術 report.md を各サブディレクトリに配置。重要事実（workflow-use メンテ停滞・web-ui の VibeSurf 化・sdk が Cloudflare 直結唯一・bux の Docker 非対応 等）を「学びとナレッジ」に追記 |
