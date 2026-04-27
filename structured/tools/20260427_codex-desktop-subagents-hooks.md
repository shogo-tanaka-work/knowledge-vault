# Codex Desktop — サブエージェント・Hooks 検証ログ

> ステータス: 完了（一部機能は未対応確認）
> 作成日: 2026/04/27
> 最終更新: 2026/04/27
> ファイルパス: /Users/shogo/ObsidianVault/knowledge-vault/structured/tools/20260427_codex-desktop-subagents-hooks.md

---

## 📋 検証概要

- **ツール/サービス名**: Codex Desktop（OpenAI）
- **検証対象**: サブエージェント機能・Hooks機能
- **バージョン**: 26.422.30944（macOS）
- **検証期間**: 2026/04/27
- **検証担当者**: s-tanaka
- **参照ファイル**: `/Volumes/PortableSSD/Documents/AIツールPoCの場所/Codex/`

---

## 1. 背景と検証目的

### なぜこの検証を行うのか
- Claude Codeのサブエージェント・Hooksに相当する機能がCodexにあるか確認したかった
- 非エンジニア・ビジネスサイドへの説明材料として機能差異を整理したかった

### 解決したい課題
- Codex Desktopを「単なるチャット」ではなく自動化・並列化ツールとして使えるか評価する
- HooksをCI/CDやコンプライアンス用途に活用できるか検証する

---

## 2. Claude Codeとの機能対応表

| 機能 | Claude Code | Codex Desktop/CLI |
|---|---|---|
| サブエージェント | あり（Agentツール） | あり（`.codex/agents/*.toml`） |
| Hooks | あり（7イベント） | CLIはあり / **Desktopは未対応**（v26.422） |
| MCP統合 | あり | あり（豊富、自身をMCPサーバーに公開も可） |
| 設定ファイル | CLAUDE.md | AGENTS.md（形式非互換） |
| パーミッションモード | 3段階 | 3段階（OSサンドボックスが強み） |
| GitHub Action | なし（公式） | あり（公式サポート） |
| スラッシュコマンド | あり | あり（`/review` `/diff` `/compact` 等） |

---

## 3. サブエージェント検証

### 設定方法
プロジェクト配下の `.codex/agents/` に `.toml` ファイルを置くだけで認識される。`config.toml` への追記は不要。

```
.codex/agents/code-reviewer.toml
```

```toml
name = "code-reviewer"
description = "Review diffs and report concrete risks before summarizing."
developer_instructions = """
You are a review-focused sub-agent.
Inspect the diff carefully and report:
- correctness bugs
- behavioral regressions
- security or data-loss risks
- missing tests
Order findings by severity, cite files and lines when possible.
"""
model = "gpt-5.4-mini"
model_reasoning_effort = "medium"
```

### 検証結果
- **認識**: プロジェクトを `trust_level = "trusted"` に設定済みであれば即時認識される ✅
- `~/.codex/config.toml` への追記は不要
- デスクトップUIからスレッドとして呼び出し可能

---

## 4. Hooks検証

### 設定方法（正しい形式）
`~/.codex/config.toml` に以下を追記する必要がある。

```toml
[features]
codex_hooks = true

[[hooks.PreToolUse]]
command = "/path/to/scripts/security-check.sh"
```

**書き方の注意点：**
- `[hooks.PreToolUse]`（単一テーブル）は **エラー**。`[[hooks.PreToolUse]]`（配列テーブル）が正しい
- `matcher = { tool_name = "bash" }` はエラー。`matcher = "bash"` の文字列形式が正しい
- スクリプトを置くだけでは動作しない。必ず `config.toml` への登録が必要

### Hooksのイベント種類（6種類、固定）
| イベント | タイミング |
|---|---|
| `SessionStart` | セッション開始時 |
| `PreToolUse` | ツール実行直前 |
| `PostToolUse` | ツール実行直後 |
| `PermissionRequest` | 承認要求前 |
| `UserPromptSubmit` | プロンプト送信時 |
| `Stop` | 会話終了時 |

イベント種類はプラットフォーム固定で、ユーザーによる追加・変更は不可。
1つのイベントに複数スクリプトを設定可能。各スクリプトに `matcher` で実行条件を絞り込める。

### 検証結果（Codex Desktop v26.422.30944）
- **config.toml の構文エラー対応**: `[[hooks.PreToolUse]]` 形式に修正後、起動エラーは解消 ✅
- **Hooks発火**: **未確認（発火せず）** ❌
- **原因**: アプリログの `Features enabled` に `codex_hooks` が含まれていない

```
# 実際のログ
Features enabled: "enable_request_compression, collaboration_modes, personality,
request_rule, fast_mode, image_generation, ..."
# → codex_hooks の記載なし
```

- **結論**: `codex_hooks` フィーチャーキーはDesktop v26.422では未実装。設定は静かに無視される
- **CLIでは動作する**可能性あり（CLI版は別実装）

---

## 5. 実ファイル構成（PoC）

```
/Volumes/PortableSSD/Documents/AIツールPoCの場所/Codex/
├── AGENTS.md                          # プロジェクト指示（CLAUDE.mdに相当）
├── conversation_summary.md            # Codex Desktop機能まとめ
├── .codex/
│   └── agents/
│       └── code-reviewer.toml         # サブエージェント定義（動作確認済み）
├── scripts/
│   └── security-check.sh              # Hooks用スクリプト（登録済み・未発火）
├── docs/
│   └── codex_desktop_subagents_hooks.md
└── examples/
    └── codex-config.toml.example
```

`~/.codex/config.toml` に追記済みの内容：

```toml
[features]
codex_hooks = true

[[hooks.PreToolUse]]
command = "/Volumes/PortableSSD/Documents/AIツールPoCの場所/Codex/scripts/security-check.sh"
```

---

## 6. 学びとナレッジ

### サブエージェント
- `.codex/agents/` にtomlを置くだけ。設定ファイル不要で即使える
- エージェントごとにモデル・推論レベル・MCPサーバーをオーバーライドできる
- 並列処理の本質は「速さ」だけでなく「各エージェントが迷わず集中できること」

### Hooks
- Desktopアプリ版ではv26.422時点で未実装（CLI版には実装済み）
- 将来のアップデートで対応する可能性あり（設定は残しておいてよい）
- イベント種類は固定6種。スクリプト数は制限なし、matcherで条件を絞れる

### ビジネス活用観点
- サブエージェントは「複数担当者を同時アサインする感覚」
- Hooksは「AIの行動にコンプライアンス・承認・ログを自動連動させる仕組み」
- コンテキストウィンドウが大きくても並列処理が有効な理由：各エージェントが専用のクリーンなコンテキストで集中できるため品質が上がる

---

## 7. 次のアクション

- [ ] CLI版でのHooks発火を確認する（`codex` コマンド経由）
- [ ] Codex Desktopのアップデートでhooks対応を確認する
- [ ] サブエージェント（code-reviewer）を実際の開発タスクで運用検証する
