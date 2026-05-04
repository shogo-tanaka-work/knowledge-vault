# OSS の AGENTS.md / CLAUDE.md 実装事例 — 横断調査オーバービュー

調査日: 2026-05-04
調査対象: 主要 OSS 25 リポジトリ（ノーコード/ローコード/自動化系 10 + 大手プロダクト 15）

## このシリーズの目的

「AGENTS.md ベストプラクティス」「CLAUDE.md ベストプラクティス」として一般に流通している汎用テンプレートを超えて、**実プロダクトで採用されている応用・差別化された設計観点**を抽出し、知識の引き出しとして蓄積する。

公式ドキュメントには載らないが、実コードベースでは採用されている工夫 — 例えば独自プラグインマーケットプレイスの構築、失敗ログを動的に蓄積する運用ループ、AI が踏み越えてはいけない設計境界の表現方法など — を 3 本の深掘り記事に分割して整理した。

## 採用ファイル種別マトリクス

| リポジトリ | AGENTS.md | CLAUDE.md | .claude/ | .cursor/ | copilot-instructions | その他独自 |
|---|---|---|---|---|---|---|
| n8n-io/n8n | ✓（階層） | - | ✓ プラグイン | - | - | - |
| langgenius/dify | ✓（階層） | △ 9byte | ✓ hooks | - | - | `.agents/skills/` |
| Budibase/budibase | △ 9byte | ✓ 7.8KB | - | - | - | - |
| directus/directus | ✓ | △ リダイレクト | ✓ | - | - | `ai_policy.md` |
| activepieces/activepieces | ✓ | △ 9byte | - | - | - | `.agents/features/` 46 件 |
| langflow-ai/langflow | ✓ | △ リダイレクト | - | ✓ | - | `AGENTS-example.md` |
| appsmithorg/appsmith | - | - | - | ✓ rules + lessons | - | - |
| ToolJet / NocoDB / Automatisch / Flowise | - | - | - | - | - | - |
| vercel/next.js | ✓ | - | - | - | - | $スキル参照 |
| microsoft/vscode | △ リダイレクト | - | - | - | ✓ 本体 | - |
| openai/codex | ✓ | - | - | - | - | - |
| cline/cline | - | ✓ ルーター | - | - | - | `.clinerules/` |
| All-Hands-AI/OpenHands | ✓ | - | - | - | - | `microagents/` |
| supabase/supabase | - | - | - | - | ✓ レビュー特化 | `.github/instructions/` |
| apache/airflow | ✓ | - | - | - | - | `code-review.instructions.md` |
| denoland/deno | - | ✓ | - | - | - | - |
| temporalio/temporal | ✓ | - | - | - | - | - |
| huggingface/transformers | - | - | - | - | ✓ | `# Copied from` |
| openai/openai-cookbook | ✓ | - | - | - | - | - |
| sst/opencode | ✓ | - | - | - | - | - |

採用率: ノーコード系 6/10、大手系 14/15。AI ネイティブ製品ほど深い実装を持つ傾向。

## 業界トレンド 6 点

### 1. AGENTS.md が事実上の業界標準に収束

OpenAI Codex 起源、現在 Linux Foundation 配下の Agentic AI Foundation が管理する規格。Claude Code・Cursor・Copilot など複数エージェントが共通参照する中立フォーマットとして浮上した。

### 2. CLAUDE.md は「AGENTS.md への薄いリダイレクト」用法に収束

directus/directus の `.claude/CLAUDE.md`（"See agents.md in the repository root" の 1 行）、langflow-ai/langflow の CLAUDE.md（280 bytes）、activepieces の 9 bytes ファイルなど、メンテコストを AGENTS.md に集約する戦略が複数で観測される。

### 3. `.agents/` ディレクトリの出現

Dify（`.agents/skills/`）、Activepieces（`.agents/features/` 46 件、`.agents/rules/`、`.agents/skills/`）、Langflow（`.agents/skills/`）が `.claude/`・`.cursor/` に加えて `.agents/` を設置。ツール非依存の汎用エージェント設定の標準化が始まっている。

### 4. ignore ファイルの多元化

Activepieces は `.claudeignore`・`.agentignore`・`.cursorignore` を並列管理。エージェント別に除外設定を分離する運用が登場している。

### 5. 失敗ログの動的蓄積パターン

Appsmith の `.cursor/lessons.md`（ユーザー訂正のたびに記録）、cline の `.clinerules/`（手動介入が必要だった時に書く）、OpenAI Cookbook の Operational Insights など、**静的なベストプラクティスではなく経験則ライブラリとして運用**する思想が広がっている。詳細は [02-failure-log-accumulation.md](./02-failure-log-accumulation.md)。

### 6. AI 生成コードへの防衛的記述が逆説的に登場

Apache Airflow の code-review instructions が「AI 生成 PR のレッドフラグリスト」（fabricated diffs / unrelated file changes / empty descriptions など）を含む。エージェント向けガイドが、エージェント産物を人間がレビューするための指針も兼ねるという二重構造。詳細は [03-security-boundary-design.md](./03-security-boundary-design.md)。

## 深掘り記事ナビゲーション

### [01-n8n-plugin-architecture.md](./01-n8n-plugin-architecture.md)

n8n の `.claude/plugins/n8n/` 体系の完全分解。`extraKnownMarketplaces` を活用した独自プラグインマーケットプレイス、14 スキルの分類、エージェント役割分離（developer / linear-issue-triager）、PostToolUse フックによるテレメトリ送信、`packages/testing/playwright/AGENTS.md` の TCR + Janitor 静的解析統合まで。

### [02-failure-log-accumulation.md](./02-failure-log-accumulation.md)

Appsmith・cline・OpenAI Cookbook を題材にした失敗ログ蓄積パターンの比較。「いつ書くか」のポリシー、セルフイプルーブメントループ、tribal knowledge の動的蓄積システムとしての設計思想。

### [03-security-boundary-design.md](./03-security-boundary-design.md)

Airflow・Next.js・Activepieces・Directus・Dify・n8n を題材に、AI が踏み越えてはいけない設計境界の表現方法を分類。アーキテクチャ境界、エディション境界、SSRF 対策、`--no-verify` 物理ブロック、AI 自律性のガバナンス、セキュリティ修正の中立的タイトル規則まで。

## 引用元一覧（横断調査の一次出典）

- [n8n AGENTS.md](https://raw.githubusercontent.com/n8n-io/n8n/master/AGENTS.md)
- [n8n .claude/settings.json](https://raw.githubusercontent.com/n8n-io/n8n/master/.claude/settings.json)
- [Dify api/AGENTS.md](https://raw.githubusercontent.com/langgenius/dify/main/api/AGENTS.md)
- [Budibase CLAUDE.md](https://raw.githubusercontent.com/Budibase/budibase/master/CLAUDE.md)
- [Directus AGENTS.md](https://raw.githubusercontent.com/directus/directus/main/AGENTS.md)
- [Directus ai_policy.md](https://raw.githubusercontent.com/directus/directus/main/ai_policy.md)
- [Activepieces AGENTS.md](https://raw.githubusercontent.com/activepieces/activepieces/main/AGENTS.md)
- [Langflow AGENTS-example.md](https://raw.githubusercontent.com/langflow-ai/langflow/main/AGENTS-example.md)
- [Appsmith .cursor/rules/agent-behavior.mdc](https://raw.githubusercontent.com/appsmithorg/appsmith/release/.cursor/rules/agent-behavior.mdc)
- [Appsmith .cursor/lessons.md](https://raw.githubusercontent.com/appsmithorg/appsmith/release/.cursor/lessons.md)
- [Next.js AGENTS.md](https://raw.githubusercontent.com/vercel/next.js/canary/AGENTS.md)
- [VS Code copilot-instructions.md](https://raw.githubusercontent.com/microsoft/vscode/main/.github/copilot-instructions.md)
- [OpenAI Codex AGENTS.md](https://raw.githubusercontent.com/openai/codex/main/AGENTS.md)
- [cline .clinerules/general.md](https://raw.githubusercontent.com/cline/cline/main/.clinerules/general.md)
- [OpenHands AGENTS.md](https://raw.githubusercontent.com/All-Hands-AI/OpenHands/main/AGENTS.md)
- [Supabase copilot-instructions.md](https://raw.githubusercontent.com/supabase/supabase/master/.github/copilot-instructions.md)
- [Airflow AGENTS.md](https://raw.githubusercontent.com/apache/airflow/main/AGENTS.md)
- [Airflow code-review.instructions.md](https://raw.githubusercontent.com/apache/airflow/main/.github/instructions/code-review.instructions.md)
- [Deno CLAUDE.md](https://raw.githubusercontent.com/denoland/deno/main/CLAUDE.md)
- [Temporal AGENTS.md](https://raw.githubusercontent.com/temporalio/temporal/main/AGENTS.md)
- [HuggingFace Transformers copilot-instructions.md](https://raw.githubusercontent.com/huggingface/transformers/main/.github/copilot-instructions.md)
- [opencode AGENTS.md](https://raw.githubusercontent.com/sst/opencode/dev/AGENTS.md)
- [agentmd/agent.md 規格リポジトリ](https://github.com/agentmd/agent.md)
