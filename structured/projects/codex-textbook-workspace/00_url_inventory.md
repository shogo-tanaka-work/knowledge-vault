# OpenAI Codex Docs URL Inventory

> 取得日：2026-05-08
> ソース：https://developers.openai.com/codex （左ナビ + Changelog）、https://github.com/openai/codex
> 取得方法：WebFetch + web-researcher サブエージェントによるリサーチ。docs/research の二次情報も照合。
> 利用ポリシー：OpenAI Terms of Use（教育・引用目的の要約は出典明示で許容）。robots.txt の細目は別途要再確認。
> 補足：CLI 本体は `github.com/openai/codex`（npm `@openai/codex` / brew `codex`）。GitHub Action は `github.com/openai/codex-action`。Codex App は Desktop / Web / Cloud / Chrome 拡張の複数サーフェス。

---

## 00-index / overview

| URL | ページタイトル | 想定章番号 |
|---|---|---|
| https://developers.openai.com/codex | Codex トップ | 0 |
| https://developers.openai.com/codex/quickstart | Quickstart | 10 |
| https://developers.openai.com/codex/use-cases | Use Cases | 22 |
| https://developers.openai.com/codex/learn/best-practices | Best Practices | 21 |
| https://developers.openai.com/codex/changelog | Changelog | - |
| https://developers.openai.com/codex/changelog/rss.xml | Changelog RSS | - |

## 10-models-and-pricing

| URL | ページタイトル | 想定章番号 |
|---|---|---|
| https://developers.openai.com/codex/models | Models（GPT-5.3-Codex / Spark） | 11 |
| https://developers.openai.com/codex/pricing | Pricing（トークン課金） | 12 |
| https://help.openai.com/en/articles/20001106-codex-rate-card | Codex Rate Card | 12 |
| https://openai.com/index/introducing-gpt-5-3-codex/ | Introducing GPT-5.3-Codex | 11 |

## 20-cli

| URL | ページタイトル | 想定章番号 |
|---|---|---|
| https://developers.openai.com/codex/cli | CLI 概要 | 13 |
| https://developers.openai.com/codex/cli/features | CLI Features | 13 |
| https://developers.openai.com/codex/cli/reference | CLI Reference（コマンドオプション） | 14 |
| https://developers.openai.com/codex/cli/slash-commands | Slash Commands | 15 |
| https://github.com/openai/codex | openai/codex（CLI ソース） | 0,13 |
| https://github.com/openai/codex/blob/main/README.md | README | 0,13 |
| https://github.com/openai/codex/blob/main/AGENTS.md | AGENTS.md（リポ実例） | 2 |
| https://github.com/openai/codex/blob/main/CHANGELOG.md | CHANGELOG | - |
| https://www.npmjs.com/package/@openai/codex | npm パッケージ | 10,13 |

## 21-ide

| URL | ページタイトル | 想定章番号 |
|---|---|---|
| https://developers.openai.com/codex/ide | IDE 拡張 | 16 |
| https://developers.openai.com/codex/ide/features | IDE Features | 16 |
| https://www.jetbrains.com/help/ai-assistant/codex-agent.html | JetBrains Codex Agent ドキュメント | 16 |
| https://blog.jetbrains.com/ai/2026/01/codex-in-jetbrains-ides/ | Codex in JetBrains IDEs（公式ブログ） | 16 |

## 22-app-and-cloud

| URL | ページタイトル | 想定章番号 |
|---|---|---|
| https://developers.openai.com/codex/app | Codex App 概要 | 17 |
| https://developers.openai.com/codex/app/features | App Features | 17 |
| https://developers.openai.com/codex/app/automations | App Automations | 9 |
| https://developers.openai.com/codex/app/computer-use | Computer Use | 18 |
| https://developers.openai.com/codex/cloud | Cloud / Web | 19 |
| https://openai.com/index/codex-for-almost-everything/ | Codex for (almost) everything | 0,9,18 |

## 30-skills-mcp-config

| URL | ページタイトル | 想定章番号 |
|---|---|---|
| https://developers.openai.com/codex/skills | Agent Skills | 4 |
| https://developers.openai.com/codex/mcp | MCP（Model Context Protocol） | 6 |
| https://developers.openai.com/codex/agent-approvals-security | Agent Approvals & Security | 1 |
| https://developers.openai.com/codex/concepts/sandboxing | Sandboxing | 1 |
| https://developers.openai.com/codex/config-reference | Configuration Reference | 20 |
| https://developers.openai.com/codex/config-advanced | Advanced Configuration | 20 |
| https://developers.openai.com/codex/guides/agents-md | AGENTS.md ガイド | 2 |
| https://developers.openai.com/codex/guides/agents-sdk | Agents SDK 連携 | - |

## 40-github-and-cicd

| URL | ページタイトル | 想定章番号 |
|---|---|---|
| https://developers.openai.com/codex/integrations/github | GitHub コードレビュー統合 | 5 |
| https://developers.openai.com/codex/github-action | GitHub Action | 5 |
| https://github.com/openai/codex-action | openai/codex-action リポ | 5 |

## 50-enterprise-and-policy

| URL | ページタイトル | 想定章番号 |
|---|---|---|
| https://developers.openai.com/codex/enterprise/admin-setup | Enterprise Admin Setup | 23 |
| https://developers.openai.com/codex/codex-for-oss-terms | OSS プログラム利用規約 | - |
| https://openai.com/policies/row-terms-of-use/ | OpenAI Terms of Use | - |
| https://openai.com/policies/usage-policies/ | OpenAI Usage Policies | - |

## 60-blog-and-launch

| URL | ページタイトル | 想定章番号 |
|---|---|---|
| https://openai.com/index/introducing-codex/ | Introducing Codex | 0 |
| https://openai.com/index/codex-for-almost-everything/ | Codex for (almost) everything | 0 |
| https://openai.com/index/introducing-gpt-5-3-codex/ | Introducing GPT-5.3-Codex | 11 |

---

## 章 ↔ ファイル対応（決定版）

| sort | mdx | 主たる一次ソース |
|---|---|---|
| 0 | overview.mdx | /codex（トップ） + 主要ブログ |
| 1 | approval-modes-sandbox.mdx | /codex/agent-approvals-security + /codex/concepts/sandboxing |
| 2 | agents-md.mdx | /codex/guides/agents-md + リポ AGENTS.md |
| 3 | subagents.mdx | CLI Features の subagents 節 + GitHub README |
| 4 | agent-skills.mdx | /codex/skills |
| 5 | github-action-cicd.mdx | /codex/github-action + /codex/integrations/github + codex-action リポ |
| 6 | mcp-integration.mdx | /codex/mcp |
| 7 | vs-claude-code.mdx | 両プロダクト公式 + ベンチ記事 |
| 8 | marketplace.mdx | Changelog（Plugins 90+） |
| 9 | automations.mdx | /codex/app/automations |
| 10 | quickstart.mdx | /codex/quickstart |
| 11 | models.mdx | /codex/models + GPT-5.3-Codex ブログ |
| 12 | pricing.mdx | /codex/pricing + Rate Card |
| 13 | cli-features.mdx | /codex/cli + /codex/cli/features |
| 14 | cli-reference.mdx | /codex/cli/reference |
| 15 | slash-commands.mdx | /codex/cli/slash-commands |
| 16 | ide-extension.mdx | /codex/ide + /codex/ide/features + JetBrains 記事 |
| 17 | codex-app.mdx | /codex/app + /codex/app/features |
| 18 | computer-use.mdx | /codex/app/computer-use + Codex for (almost) everything |
| 19 | cloud-web.mdx | /codex/cloud |
| 20 | config-reference.mdx | /codex/config-reference + /codex/config-advanced |
| 21 | best-practices.mdx | /codex/learn/best-practices |
| 22 | use-cases.mdx | /codex/use-cases |
| 23 | enterprise-admin.mdx | /codex/enterprise/admin-setup |

## 進行ノート

- 既存 10 本（sort 0〜9）は最新化、新規 14 本（sort 10〜23）は新規作成
- 取得手段優先順位：WebFetch → Exa CLI → browser-use CLI（例外時のみ）
- 各章ごとに fact-checker → technical-editor の直列レビュー
