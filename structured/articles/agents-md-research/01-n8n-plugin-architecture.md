# n8n の Claude Code プラグインアーキテクチャ完全分解

n8n（https://github.com/n8n-io/n8n）は OSS ノーコードワークフロービルダーとして著名だが、AI エージェント向け設定の実装としても 2025-2026 年時点で最も先進的な事例の一つ。`AGENTS.md` を入口にしつつ、`.claude/plugins/n8n/` で **独自プラグインマーケットプレイス** を構築している点が他プロジェクトと一線を画す。

本記事では n8n のプラグイン体系を、設定ファイル・エージェント定義・スキル分類・テレメトリ機構・サブパッケージ補足の 5 つの観点から完全分解する。

## 1. settings.json による独自プラグインマーケットプレイス

引用元: [.claude/settings.json](https://raw.githubusercontent.com/n8n-io/n8n/master/.claude/settings.json)（746 bytes）

```json
{
  "permissions": {
    "allow": [
      "Bash(git log:*)", "Bash(git show:*)", "Bash(grep:*)", "Bash(ls:*)",
      "Bash(pnpm build)", "Bash(pnpm lint:*)", "Bash(pnpm test:*)",
      "Bash(pnpm typecheck:*)", "Bash(popd)", "Bash(pushd:*)",
      "Bash(mkdir -p .claude/plans)", "Write(.claude/plans/*)"
    ]
  },
  "hooks": {
    "PostToolUse": [{
      "matcher": "Skill",
      "hooks": [{"type": "command", "command": "node .claude/plugins/n8n/scripts/track-skill-usage.mjs", "timeout": 10, "async": true}]
    }]
  },
  "extraKnownMarketplaces": {
    "n8n": {"source": {"source": "directory", "path": "./.claude/plugins/n8n"}}
  },
  "enabledPlugins": {"n8n@n8n": true}
}
```

### 観点抽出

- **`extraKnownMarketplaces`** は Claude Code の比較的新しい機能で、社内/プロジェクト内に独自プラグインレジストリを定義できる。n8n はこれを **「リポジトリ同梱の社内マーケットプレイス」** として活用し、すべての社内スキル・エージェント・コマンドに `n8n:` ネームスペースを付与している。個人やサードパーティが作るスキルとの命名衝突を防ぐ設計。
- **権限の最小許可リスト**：破壊的操作（`rm`、`push --force`、`reset --hard` 等）は一切含まれず、読み取り系 git コマンド・テスト系 pnpm コマンド・`.claude/plans/` への書き込みだけ。
- **`enabledPlugins: {"n8n@n8n": true}`** は「`n8n` プラグインを `n8n` マーケットプレイスから有効化」という記法。同名衝突を許容する仕組みを採用している。

## 2. プラグイン構造（`.claude/plugins/n8n/`）

```
.claude/plugins/n8n/
├── .claude-plugin/
│   ├── plugin.json       (name: "n8n", version: "0.2.0")
│   └── marketplace.json  (owner 設定)
├── agents/
│   ├── developer.md
│   └── linear-issue-triager.md
├── commands/
│   ├── plan.md           → /n8n:plan
│   └── triage.md         → /n8n:triage
├── skills/               (14 スキル)
│   ├── content-design/
│   ├── conventions/
│   ├── create-community-node-lint-rule/
│   ├── create-issue/
│   ├── create-pr/
│   ├── create-skill/
│   ├── design-system-rules/
│   ├── linear-issue/
│   ├── loom-transcript/
│   ├── node-add-oauth/
│   ├── protect-endpoints/
│   ├── reproduce-bug/
│   ├── setup-mcps/
│   └── spec-driven-development/
└── scripts/
    └── track-skill-usage.mjs
```

引用元: [GitHub API contents](https://api.github.com/repos/n8n-io/n8n/contents/.claude/plugins/n8n)

## 3. エージェント役割分離（developer / linear-issue-triager）

n8n は 2 つのエージェントを **明確に役割分離** して定義している。これは「エージェントの分業」を OSS で公式化した数少ない例。

### 3.1 `n8n:developer`（青色）

引用元: [agents/developer.md](https://raw.githubusercontent.com/n8n-io/n8n/master/.claude/plugins/n8n/agents/developer.md)

フルスタック開発エージェント。Vue 3 + Pinia フロントエンド、Node.js + TypeScript バックエンド、ワークフローエンジンをカバー。

定義された 5 ステップワークフロー:
1. Linear MCP でチケット取得
2. 影響パッケージ特定
3. 実装
4. テスト追加
5. PR 作成

### 3.2 `n8n:linear-issue-triager`（赤色）

引用元: [agents/linear-issue-triager.md](https://raw.githubusercontent.com/n8n-io/n8n/master/.claude/plugins/n8n/agents/linear-issue-triager.md)

**実装は行わず調査のみ** という明確な制約を持つエージェント。

主な特徴:
- CRITICAL / HIGH / MEDIUM / LOW の severity 分類体系
- Linear チケットへの直接書き込み禁止（人間が確認してから書く）
- git log + GitHub CLI + Linear MCP を組み合わせた深掘り手順
- 青色の developer と赤色の triager で **視覚的に役割を区別**

### 観点抽出

- **「実装しないエージェント」を公式に定義**することで、調査と実装の責任を分離。エージェント間の暗黙の越権を構造的に防ぐ。
- 色（青/赤）による視覚識別は、Claude Code の UI 上で「いま誰が動いているか」を即座に把握させる UX 設計。

## 4. 14 スキルの分類

スキルを機能カテゴリで再分類すると、n8n のエージェント設計思想が浮かび上がる。

### 4.1 PR / Issue 系（コントリビューションフロー）

| スキル | 目的 | 注目点 |
|---|---|---|
| `create-pr` | PR 作成 | タイトルは Conventional Commits 正規表現で検証。セキュリティ修正は中立的タイトル必須。`(no-changelog)` サフィックスでリリースノート除外 |
| `create-issue` | Issue 作成 | テンプレート準拠 |
| `linear-issue` | Linear 連携 | チケット取得 |

引用元: [skills/create-pr/SKILL.md](https://raw.githubusercontent.com/n8n-io/n8n/master/.claude/plugins/n8n/skills/create-pr/SKILL.md)

### 4.2 実装系（コード改修パターン）

| スキル | 目的 | 注目点 |
|---|---|---|
| `node-add-oauth` | 既存ノードへの OAuth2 追加 | 10 ステップ手順。カスタムスコープ UI、gateway API（Atlassian 型）対応 |
| `protect-endpoints` | REST 認証スコープ付与 | `@ProjectScope` / `@GlobalScope` の標準マッピング、ControllerRegistryMetadata によるリグレッションテストパターン |
| `create-community-node-lint-rule` | コミュニティノード ESLint ルール作成 | - |

引用元: [skills/protect-endpoints/SKILL.md](https://raw.githubusercontent.com/n8n-io/n8n/master/.claude/plugins/n8n/skills/protect-endpoints/SKILL.md)、[skills/node-add-oauth/SKILL.md](https://raw.githubusercontent.com/n8n-io/n8n/master/.claude/plugins/n8n/skills/node-add-oauth/SKILL.md)

### 4.3 調査・診断系

| スキル | 目的 | 注目点 |
|---|---|---|
| `reproduce-bug` | バグ再現テスト作成（実装はしない） | CONFIRMED / LIKELY / UNCONFIRMED / SKIPPED / ALREADY_FIXED の 5 段階分類。「本物のクレデンシャル必須」「レースコンディション」「クラウド固有インフラ」はハードベイルアウト |
| `loom-transcript` | Loom 動画トランスクリプト取得 | 認証不要で動画から仕様を読める |

引用元: [skills/reproduce-bug/SKILL.md](https://raw.githubusercontent.com/n8n-io/n8n/master/.claude/plugins/n8n/skills/reproduce-bug/SKILL.md)、[skills/loom-transcript/SKILL.md](https://raw.githubusercontent.com/n8n-io/n8n/master/.claude/plugins/n8n/skills/loom-transcript/SKILL.md)

### 4.4 仕様・規約系

| スキル | 目的 | 注目点 |
|---|---|---|
| `spec-driven-development` | `.claude/specs/` を正本に実装と仕様の乖離を検出 | Aligned / Drift / Gaps の 3 分類で差分報告 |
| `conventions` | コーディング規約 | - |
| `design-system-rules` | デザインシステム遵守 | Semantic tokens → Primitives → Hard-coded values の優先順位。非推奨コンポーネント・レガシートークンを強警告 |
| `content-design` | コンテンツデザイン | - |

引用元: [skills/spec-driven-development/SKILL.md](https://raw.githubusercontent.com/n8n-io/n8n/master/.claude/plugins/n8n/skills/spec-driven-development/SKILL.md)、[skills/design-system-rules/SKILL.md](https://raw.githubusercontent.com/n8n-io/n8n/master/.claude/plugins/n8n/skills/design-system-rules/SKILL.md)

### 4.5 メタ系

| スキル | 目的 | 注目点 |
|---|---|---|
| `create-skill` | 新スキル作成 | **スキルを自己増殖させるメタスキル**。組織として継続的にスキルを増やす仕組みをツール化 |
| `setup-mcps` | MCP サーバセットアップ | - |

### 観点抽出

- 「**実装はしない、再現テストだけ作る**」スキル（`reproduce-bug`）の存在は、AI エージェントの責任範囲を絞る設計の典型例。
- `create-skill` というメタスキルが組織内に存在すると、エージェント設定が **継続的に成長する仕組み** が確立される。
- `loom-transcript` のように「人間が動画で共有した仕様を AI に読ませる」スキルは、**非テキスト情報をエージェントに渡す経路** の設計として注目に値する。
- スキル粒度は「ドメイン特化のレシピ」レベル。汎用スキルではなく **n8n 固有のコードベース知識を埋め込んだ手順書** として機能している。

## 5. PostToolUse フックによるテレメトリ送信

引用元: [scripts/track-skill-usage.mjs](https://raw.githubusercontent.com/n8n-io/n8n/master/.claude/plugins/n8n/scripts/track-skill-usage.mjs)

`settings.json` の `PostToolUse` フックが、Skill ツール実行のたびに `track-skill-usage.mjs` を非同期実行する。スクリプトはユーザー識別子を SHA-256 でハッシュ化したうえで `telemetry.n8n.io` に送信する。

### 観点抽出

- **OSS 内部で「どのスキルが使われているか」を定量計測する仕組み**。社内のエージェント設計を改善するためのフィードバックループ。
- 個人開発者向けには `track-skill-usage.mjs` を実行しない選択肢も提供されており、プライバシー設計が明示的。
- `async: true` で送信失敗が開発を妨げないようになっている（10 秒タイムアウト付き）。

## 6. コマンド — エージェントへの委譲ラッパー

### `/n8n:plan`

引用元: [commands/plan.md](https://raw.githubusercontent.com/n8n-io/n8n/master/.claude/plugins/n8n/commands/plan.md)

Linear チケット ID（例: PAY-XXXX）を引数に取り、`.claude/plans/<TICKET-ID>.md`（gitignore 済み）に実装計画を保存する。出力構造はタイトル・リンク・サマリ・実装計画・テスト戦略・リスクの 6 セクション。

### `/n8n:triage`

引用元: [commands/triage.md](https://raw.githubusercontent.com/n8n-io/n8n/master/.claude/plugins/n8n/commands/triage.md)

`n8n:linear-issue-triager` エージェントへの委譲ラッパー。コマンドはエージェント呼び出しを簡略化する役割。

## 7. サブパッケージ AGENTS.md（モノレポ階層）

n8n は **モノレポのサブパッケージごとに AGENTS.md を配置** している。グローバル指示と局所的指示を分離する設計。

### 7.1 `packages/frontend/AGENTS.md`

引用元: [packages/frontend/AGENTS.md](https://raw.githubusercontent.com/n8n-io/n8n/master/packages/frontend/AGENTS.md)

- `@n8n/design-system` / `editor-ui` 変更時に `design-system-rules` スキル使用を必須化
- アイコン名は `updatedIconSet` から選択（`deprecatedIconSet` 禁止）
- 期間定数のハードコード禁止 → 集約定数を参照

### 7.2 `packages/testing/playwright/AGENTS.md`

引用元: [packages/testing/playwright/AGENTS.md](https://raw.githubusercontent.com/n8n-io/n8n/master/packages/testing/playwright/AGENTS.md)（14,310 bytes、サブパッケージ最大規模）

特筆すべき機能:

#### Janitor 静的解析ツール

E2E テストの品質維持のために定義された 5 ルール:
- `selector-purity`: 選択子の純度チェック
- `no-page-in-flow`: フロー関数内での page 参照禁止
- `boundary-protection`: テスト境界の保護
- `dead-code`: 死コード検出
- `duplicate-logic`: 重複ロジック検出

ベースライン機能で「既存違反は許容、新規違反のみブロック」という **段階的適用モード** を採用。レガシーコードを抱えるプロジェクトでも導入できる設計。

#### TCR（Test && Commit || Revert）ワークフロー

`pnpm janitor tcr --execute` の使用を必須化。テスト失敗時は自動リバートし、成功時のみコミット確定する。**AI エージェントがコードを変更する前提での CI ガードレール設計**として機能する。

### 観点抽出

- モノレポでは「グローバル AGENTS.md」と「サブパッケージ AGENTS.md」の **2 階層構造** が標準化されつつある（同様の例: vercel/next.js、apache/airflow、langgenius/dify）。
- Playwright AGENTS.md は単なる規約ではなく、**Janitor + TCR という独自ツールチェーン** を伴う。これはエージェント設定が「指示書」から「ツール統合プラットフォーム」に進化していることを示す。

## 8. 全体構造の意義

n8n の `.claude/plugins/n8n/` は、AGENTS.md の枠を超えた **エージェント向け開発プラットフォーム** として設計されている。具体的には:

1. **マーケットプレイス機構** で命名衝突を回避し、社内・個人・サードパーティのエージェント資産を共存可能にする
2. **役割分離されたエージェント**（developer / triager）でタスク種別ごとに責任を切る
3. **粒度の細かいスキル群**（14 個）でドメイン固有のレシピをツール化する
4. **メタスキル**（`create-skill`）でエージェント設定の継続的成長を保証する
5. **テレメトリフック** で利用実態を計測しエージェント設計を改善する
6. **サブパッケージ AGENTS.md** で局所的なルールを切り出す
7. **独自静的解析ツール**（Janitor）と **TCR ワークフロー** でエージェント変更を CI レベルで検証する

この組み合わせは、現時点の OSS で他に類例を見ない実装の深さを持つ。

## 引用元一覧

- [AGENTS.md](https://raw.githubusercontent.com/n8n-io/n8n/master/AGENTS.md)
- [.claude/settings.json](https://raw.githubusercontent.com/n8n-io/n8n/master/.claude/settings.json)
- [.claude/README.md](https://raw.githubusercontent.com/n8n-io/n8n/master/.claude/README.md)
- [.claude/plugins/n8n/README.md](https://raw.githubusercontent.com/n8n-io/n8n/master/.claude/plugins/n8n/README.md)
- [agents/developer.md](https://raw.githubusercontent.com/n8n-io/n8n/master/.claude/plugins/n8n/agents/developer.md)
- [agents/linear-issue-triager.md](https://raw.githubusercontent.com/n8n-io/n8n/master/.claude/plugins/n8n/agents/linear-issue-triager.md)
- [commands/plan.md](https://raw.githubusercontent.com/n8n-io/n8n/master/.claude/plugins/n8n/commands/plan.md)
- [commands/triage.md](https://raw.githubusercontent.com/n8n-io/n8n/master/.claude/plugins/n8n/commands/triage.md)
- [skills/create-pr/SKILL.md](https://raw.githubusercontent.com/n8n-io/n8n/master/.claude/plugins/n8n/skills/create-pr/SKILL.md)
- [skills/protect-endpoints/SKILL.md](https://raw.githubusercontent.com/n8n-io/n8n/master/.claude/plugins/n8n/skills/protect-endpoints/SKILL.md)
- [skills/node-add-oauth/SKILL.md](https://raw.githubusercontent.com/n8n-io/n8n/master/.claude/plugins/n8n/skills/node-add-oauth/SKILL.md)
- [skills/reproduce-bug/SKILL.md](https://raw.githubusercontent.com/n8n-io/n8n/master/.claude/plugins/n8n/skills/reproduce-bug/SKILL.md)
- [skills/spec-driven-development/SKILL.md](https://raw.githubusercontent.com/n8n-io/n8n/master/.claude/plugins/n8n/skills/spec-driven-development/SKILL.md)
- [skills/design-system-rules/SKILL.md](https://raw.githubusercontent.com/n8n-io/n8n/master/.claude/plugins/n8n/skills/design-system-rules/SKILL.md)
- [skills/loom-transcript/SKILL.md](https://raw.githubusercontent.com/n8n-io/n8n/master/.claude/plugins/n8n/skills/loom-transcript/SKILL.md)
- [scripts/track-skill-usage.mjs](https://raw.githubusercontent.com/n8n-io/n8n/master/.claude/plugins/n8n/scripts/track-skill-usage.mjs)
- [packages/frontend/AGENTS.md](https://raw.githubusercontent.com/n8n-io/n8n/master/packages/frontend/AGENTS.md)
- [packages/testing/playwright/AGENTS.md](https://raw.githubusercontent.com/n8n-io/n8n/master/packages/testing/playwright/AGENTS.md)
