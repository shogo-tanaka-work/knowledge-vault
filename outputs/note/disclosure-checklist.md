# 検証ログ 公開可否チェックリスト

> 対象: `structured/tools/` 配下の検証ログ
> 用途: note記事化時の元素材選定。L2 無料記事 / L3 有料記事 のどちらに使えるかの判断材料
> 作成日: 2026-05-07
> 判定者: Claude（一次目視） → ユーザー確認・修正

## 判定ラベル定義

| ラベル | 意味 | 公開時の対応 |
|:---:|:---|:---|
| `OK` | そのまま公開可。ツール単体検証・公開情報・自分の環境のみ | パス情報の頭注を消す程度で投稿可 |
| `要編集` | 公開してもよいが事前編集が必要。絶対パス・固有名・受講生表現等が混在 | 編集チェック後に公開可 |
| `NG` | 公開不可。クライアント案件由来・固有業務情報・機密含む | 公開せず、抽象化した別記事を新規作成すること |

## 記事化ポテンシャル定義

| マーク | 意味 |
|:---:|:---|
| ◎ | L2 ストック資産記事の主素材として高ポテンシャル |
| ○ | 部分的に引用・補足として使える |
| △ | 単体では弱いが、シリーズ・まとめの一部として使える |
| - | 記事化対象外 |

---

## 一覧（時系列・新しい順）

| ファイル | 状態 | 記事化 | コメント |
|---|:---:|:---:|---|
| 20260506_slide-design-patterns.md | OK | ◎ | 自作スキル検証、汎用ノウハウ |
| 20260506_gpt-image-2-slide-workflow.md | OK | ◎ | GPT Image 2 × スライド制作のニッチKW候補 |
| 20260504_browser-use-desktop-app.md | OK | ◎ | Browser Use Desktop の網羅レビュー、「クライアント」は技術用語のみ |
| 20260503_line-dify-chatbot.md | OK | ◎ | LINE × Dify 統合手順、公開情報のみ |
| 20260503_gas-youtube-data-api.md | 要編集 | ○ | GAS実装ログ。絶対パス除去のみで可 |
| 20260502_supabase-medical-system-qa.md | NG | - | 医療クリニック向けSaaS案件由来。「医療×コンプライアンス」に抽象化した別記事を新規執筆推奨 |
| 20260428_stt-api-comparison.md | 要編集 | ◎ | STT API比較決定版。「受講生」表現を「読者」に置換すれば最強の資産記事素材 |
| 20260428_openai-codex-2026.md | OK | ◎ | Codex 2026年3-4月アップデート。トレンド型→ニッチKW化の好素材 |
| 20260428_line-harness-oss.md | OK | ◎ | LINE Harness OSS、独自概念ハーネスとの連携で資産記事化可 |
| 20260428_gcp-auth-security.md | 要編集 | ○ | GCP認証セキュリティ。verification-logsパス除去必要 |
| 20260428_codex-workflow-2026may.md | OK | ◎ | Codexワークフロー戦略、結論確定済みで完成度高い |
| 20260427_line-bot-mcp-server.md | OK | ○ | LINE Bot MCP検証 |
| 20260427_codex-desktop-subagents-hooks.md | OK | ◎ | Codex Desktop詳細検証、サブエージェント・hooksはニッチKW候補 |
| 20260420_video-use.md | OK | ○ | Video Use リサーチ |
| 20260420_pptx_architecture_diagram_ai_generation.md | OK | ◎ | PPTXアーキテクチャ図解自動生成、独自実装ログ |
| 20260420_microsoft-copilot-pricing.md | OK | ○ | Copilot料金リサーチ、公開情報のみ |
| 20260420_claude-design.md | OK | ○ | Claude Design検証 |
| 20260420_browser-use-cli.md | OK | ◎ | Browser Use CLI 詳細検証 |
| 20260418_minimax-mmx-cli.md | OK | ○ | MiniMax CLI |
| 20260418_claude-design-tool.md | OK | ○ | Claude Design Tool |
| 20260415_github-remote-mcp-verification.md | 要編集 | ◎ | 自作Remote MCP書き込み対応、~/Documentsパス除去必要 |
| 20260414_obsidian-git.md | OK | ○ | obsidian-git検証 |
| 20260407_github-repo-security-setup.md | OK | ◎ | GitHubセキュリティ運用設定、B2B向け資産記事になる |
| 20260407_cloudflare-dns-worker-proxy.md | 要編集 | ○ | DNS移行戦略、~/Documentsパス除去・自ドメイン名匿名化必要 |
| 20260406_claude-computer-use.md | OK | ○ | Claude Computer Use Docker環境 |
| 20260405_claude-code-hp-development.md | 要編集 | ◎ | Claude Code × Astro HP制作、PortableSSDパス除去で公開可 |
| 20260201_kindle-shoeisha-ebook-scraping.md | 要編集 | △ | スクレイピング対象が翔泳社書籍。法務観点でグレー、公開時は技術論のみ抽出 |
| 20260120_minimax-voice-clone-batch.md | OK | ◎ | MINIMAX 音声クローンAPI一括生成 |
| 20251101_google-workspace-flows.md | OK | ◎ | Google Workspace Flows活用と制約、B2B向け |
| 20251101_gemini-file-search-rag.md | OK | ◎ | Gemini File Search RAG構築 |
| 20251011_training-knowledge-dify-bedrock.md | 要編集 | ○ | Biz研修・社内エンジニア教育用素材。「研修用」表現を中立化すれば公開可 |
| 20251011_a2a-agent-communication.md | OK | ◎ | A2A自律エージェント基礎、独自概念整理として資産化向き |
| 20251007_google-meet-minutes-notify.md | OK | ◎ | Google Meet議事録通知システム、B2B向け実装ログ |
| 20251006_claude-code-sdk-workflow.md | OK | ◎ | Claude Code SDK開発ワークフロー、第1本目候補 |
| 20251002_webflow-stitch-figma.md | OK | ○ | Webflow×Stitch×Figma連携 |
| 20250922_webflow-ai-site.md | OK | ◎ | Webflow AI次世代サイト構築 |
| 20250919_majin-prompt-presentation.md | OK | ◎ | まじん式プロンプト×プレゼン作成 |
| 20250918_ai-design-gemini-canvas-stitch.md | OK | ◎ | Gemini Canvas / Stitch 制作実務検証 |
| 20250830_notebooklm-knowledge-sharing.md | OK | ◎ | NotebookLM社内ナレッジ共有最適化、B2B向け |
| 20250830_amazon-q-kiro-db-design.md | OK | ◎ | Amazon Q/Kiro DB設計実装 |
| 20250826_amazon-q-kiro-dev-acceleration.md | OK | ◎ | Amazon Q/Kiro 開発高速化 |
| 20250823_realtime-voice-subtitle-translation.md | OK | ◎ | リアルタイム音声字幕翻訳調査 |
| 20250816_ai-gantt-chart.md | OK | ◎ | AI多機能ガントチャート構築、現場仕様のニッチ需要あり |
| 20250809_power-automate-copilot.md | OK | ◎ | Power Automate × Copilot 業務フロー |
| 20250809_google-ads-mcp.md | OK | ◎ | Google Ads MCP統合分析、既にarticles/に派生記事あり |
| 20250809_elevenlabs-voice-agent.md | OK | ◎ | ElevenLabs音声会話エージェント |
| 20250802_n8n-mcp-workflow.md | OK | ◎ | n8n × MCP ワークフロー自動構築 |
| 20250802_kombai-design-to-code.md | OK | ○ | Kombai デザイン→コード変換 |
| 20250726_reservation-sales-scraping.md | 要編集 | △ | 予約・売上スクレイピング。対象サービス名と業種を匿名化必要 |
| 20250719_frontend-design-validation.md | OK | ○ | フロントエンドデザイン検証 |
| 20250705_excel-ai-poc.md | OK | ◎ | Excel × AI（ローカルLLM活用）、機密データ論点あるが汎用論 |
| 20250705_coding-cli-marketing.md | OK | ○ | コーディングCLI × マーケティング |

### FY2025_ プレフィックス（テンプレート系）

| ファイル | 状態 | 記事化 | コメント |
|---|:---:|:---:|---|
| FY2025_browser-use-cli-2.md | OK | ◎ | browser-use CLI 2.0 |
| FY2025_marp-cli-slide.md | OK | ◎ | Marp CLI スライド作成 |
| FY2025_meta-mcp.md | OK | ○ | META MCP検証 |
| FY2025_project-template.md | - | - | テンプレートファイル、公開対象外 |
| FY2025_techjii-automation.md | OK | △ | テクじい自動化、独自キャラ前提なので扱い注意 |
| FY2025_tool-poc-template.md | - | - | テンプレートファイル、公開対象外 |

### その他（時系列以外）

| ファイル | 状態 | 記事化 | コメント |
|---|:---:|:---:|---|
| cloudflare-vercel-proxy-guide.md | OK | ◎ | Cloudflare × Vercel サブパスプロキシ手順書、完成度高い |

---

## サマリー

| カテゴリ | 件数 |
|:---|---:|
| OK（即公開可） | 41 |
| 要編集（編集後公開可） | 8 |
| NG（公開不可） | 1 |
| 対象外（テンプレート） | 2 |
| **合計** | **52** |

> 注: 上記件数は本リスト作成時点。新規追加・ステータス変更時は本ファイルを更新する。

## 第1本目〜第5本目の推奨候補（記事化◎の中から）

L2 ストック型・ニッチキーワード狙いとして優先度の高い順:

1. **20260427_codex-desktop-subagents-hooks.md** — Codex Desktop サブエージェント×hooks、競合最薄
2. **20260428_stt-api-comparison.md** — STT API比較、既に「決定版」レベルで完成度高い（要編集後即公開）
3. **20251006_claude-code-sdk-workflow.md** — Claude Code SDK 開発ワークフロー
4. **20250830_notebooklm-knowledge-sharing.md** — NotebookLM 社内ナレッジ共有、B2B層に刺さる
5. **20250816_ai-gantt-chart.md** — AI多機能ガントチャート、現場仕様で独自性高い

## NGファイルの代替戦略

`20260502_supabase-medical-system-qa.md` は記事化NGだが、含まれる以下の知識は **医療色を抜いた抽象記事** として価値がある:

- Supabase RLS設計パターン
- 日本の個人情報保護法×SaaSの一般論
- セキュリティガイドライン参照のしかた

→ 別途 `structured/articles/` に「Supabase RLS で要配慮個人情報を扱う設計パターン（業界非依存版）」として書き起こすことを推奨。
