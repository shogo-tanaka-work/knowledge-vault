# GitHubリポジトリ セキュリティ・運用設定 検証ログ

> ステータス: 完了
> 作成日: 2026/04/07
> 最終更新: 2026/04/07
> ファイルパス: /Volumes/PortableSSD/Documents/knowledge-vault/structured/tools/20260407_github-repo-security-setup.md

---

## 📋 検証概要

- **ツール/サービス名**: GitHub Repository Settings（Rulesets, Dependabot, Branch Protection）
- **検証対象**: 個人開発リポジトリのセキュリティ・運用設定のベストプラクティス適用
- **対象リポジトリ**: shogo-tanaka-work/shogo-works
- **検証期間**: 2026/04/07（1日で完結）
- **検証担当者**: 田中省伍
- **検証ステータス**: 完了

---

## 1. 背景と検証目的

### なぜこの検証を行うのか
- ポートフォリオサイトのリポジトリにセキュリティ設定が一切されていなかった
- mainブランチへの直接push、CI未テスト、依存パッケージの脆弱性未検知など、運用上のリスクがあった
- 個人開発でも最低限のGitHub運用ベストプラクティスを把握・適用しておきたい

### 解決したい課題
- mainブランチが無保護（直push可能、CIスキップ可能）
- Dependabotが無効で脆弱性に気づけない
- CIでテストが実行されていない
- マージ戦略が未統一で履歴が散らかる
- .gitignoreが不十分でOS固有ファイルが混入するリスク

---

## 2. 設定前の状態（監査結果）

Claude Codeで `gh api` を使ってリポジトリの全設定を監査した。

### 問題点一覧

| カテゴリ | 項目 | 設定前の状態 | リスク |
|----------|------|-------------|--------|
| ブランチ保護 | mainブランチルール | 未設定 | 高 |
| ブランチ保護 | CIステータスチェック必須 | 未設定 | 高 |
| 依存管理 | Dependabotセキュリティ更新 | 無効 | 高 |
| 依存管理 | dependabot.yml | 未作成 | 中 |
| CI/CD | テスト実行 | CIに含まれていない | 高 |
| CI/CD | Node.jsバージョン | claude.ymlがv20のまま | 中 |
| リポジトリ | マージ戦略 | 3種全て有効 | 低 |
| リポジトリ | Auto delete branches | 無効 | 低 |
| リポジトリ | .gitignore | 最低限のみ | 低 |
| セキュリティ | Secret scanning | 有効（OK） | - |
| セキュリティ | Push protection | 有効（OK） | - |

---

## 3. 実施した設定（手順と学び）

### 3-1. mainブランチの保護（Rulesets）

**設定場所**: Settings → Rules → Rulesets

**重要な学び:**
- GitHub UIが最近変わり、「Branch protection rules（旧）」と「Rulesets（新）」の2つが存在する
- 新しいUIではRulesetsが表示される。どちらでも同等の保護が可能
- **Enforcement statusを `Active` にしないとルールが一切効かない**（最初 `Disabled` で作成してしまい機能しなかった）

**設定内容:**
```
Ruleset: main
├── Enforcement: active ← 最重要。これがdisabledだと全て無効
├── Target: refs/heads/main
├── Rules:
│   ├── deletion（ブランチ削除禁止）
│   ├── non_fast_forward（force push禁止）
│   ├── pull_request（PR必須、required approvals: 0）
│   └── required_status_checks（CIのbuildジョブ必須）
└── strict_required_status_checks_policy: true（マージ前にブランチ最新化必須）
```

**「Require branches to be up to date before merging」の意味:**
```
main:  A ─── B ─── C (他のPRマージ) ← 今のmain
        \
feat:    └── D (自分の変更) ← Cの変更を知らない

→ DだけでCIが通っても、C+Dの組み合わせで壊れる可能性がある
→ 「Update branch」でCを取り込み → CIが再実行 → 組み合わせでもOKを保証
```

これがないと「PRのCIは通ったけどマージ後に壊れる」事故が起きる。

**確認コマンド:**
```bash
gh api repos/OWNER/REPO/rulesets/RULESET_ID | jq '{name, enforcement, rules}'
```

### 3-2. CIにテスト実行を追加

**変更ファイル**: `.github/workflows/ci.yml`

```yaml
- run: npm ci
- run: npm run test     # ← 追加
- run: npm run check
- run: npm run build
```

**学び:**
- `npm run check`（astro check）と `npm run build` はあったが、vitest が実行されていなかった
- テストを書いてもCIで実行しなければ意味がない
- ブランチ保護でこのCIジョブを必須にしているので、テスト失敗 = マージ不可になる

### 3-3. Dependabotの設定

**2つの設定が必要:**

**A. GitHub UIでの有効化（Settings → Code security）**
- Dependabot alerts → Enable
- Dependabot security updates → Enable
- これで脆弱性発見時に自動アラート＋修正PRが作られる

**B. 設定ファイル（`.github/dependabot.yml`）**
```yaml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5
    labels:
      - "dependencies"
    commit-message:
      prefix: "chore"
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
    labels:
      - "dependencies"
    commit-message:
      prefix: "chore"
```

**重要な学び:**
- `dependabot.yml` はGitHub Actionsのワークフローではない
- `.github/` フォルダには2種類のものが入る:
  - `workflows/` → GitHub Actionsランナーが実行
  - `dependabot.yml`, PRテンプレート等 → **GitHubプラットフォーム本体が読み取って実行**
- 設定ファイルをリポジトリに置くだけで、GitHub側が自動で週次チェックを実行
- npm依存だけでなく `github-actions` のバージョンも監視対象にすべき
- 有効化した直後に11件の脆弱性（high 5件, moderate 6件）を検出 → 放置していたリスクが顕在化

### 3-4. Node.jsバージョンの統一

**問題**: ci.yml はNode 22に更新済みだったが、claude.yml と claude-review.yml がNode 20のまま

**変更**: 3ファイルともNode 22に統一

**学び:**
- Astro 6は `>=22.12.0` を要求する
- ワークフロー間でランタイムバージョンが異なると、CIは通るがClaude Actionで失敗するなどの事故が起きる
- `.nvmrc` をリポジトリに置いてバージョンを一元管理する方法もある

### 3-5. マージ戦略の統一

**設定場所**: Settings → General → Pull Requests

| 方法 | 設定 | 理由 |
|------|------|------|
| Merge commit | **OFF** | 履歴が複雑になる |
| **Squash merge** | **ON** | 1PR=1コミットで履歴がクリーン |
| Rebase merge | **OFF** | コンフリクト時にややこしい |

**学び:**
- Squash mergeにするとPRタイトルがそのままコミットメッセージになる
- Conventional Commits形式（`feat:`, `fix:` 等）でPRタイトルを付ければmainの履歴が自然と綺麗になる
- 個人開発では Squash merge 一択が最もシンプル

### 3-6. Auto delete head branches

**設定場所**: Settings → General → Pull Requests → 「Automatically delete head branches」

**学び:**
- マージ済みブランチの自動削除はGitHub Actionsではなく、リポジトリ設定の1チェックボックス
- 設定前にマージされたブランチは手動削除が必要
- 削除しても「Restore branch」でいつでも復元可能

### 3-7. .gitignoreの補完

**追加したパターン:**

| カテゴリ | パターン | 理由 |
|----------|---------|------|
| macOS | `.DS_Store` | Finderが全ディレクトリに生成 |
| macOS | `._*` | 外部ドライブ（PortableSSD）で特に発生しやすい |
| macOS | `.AppleDouble`, `.Spotlight-V100`, `.Trashes` | 外部ドライブのメタデータ |
| エディタ | `.vscode/`, `.idea/`, `*.swp` | 個人設定の混入防止 |
| テスト | `coverage/` | vitest --coverage の出力 |
| ログ | `*.log`, `npm-debug.log*` | デバッグログ |
| ホスティング | `.vercel`, `.netlify` | 将来の移行に備え |

---

## 4. 設定後の最終状態

| カテゴリ | 項目 | 状態 |
|----------|------|------|
| ブランチ保護 | Ruleset (active) | PR必須 + CI必須 + 最新化必須 |
| ブランチ保護 | force push / 削除 | 禁止 |
| CI/CD | テスト実行 | 含まれている |
| CI/CD | Node.jsバージョン | 全ワークフローでv22統一 |
| 依存管理 | Dependabot alerts | 有効 |
| 依存管理 | Dependabot security updates | 有効 |
| 依存管理 | dependabot.yml | npm + github-actions 週次 |
| セキュリティ | Secret scanning | 有効 |
| セキュリティ | Push protection | 有効 |
| リポジトリ | マージ戦略 | Squash merge のみ |
| リポジトリ | Auto delete branches | 有効 |
| リポジトリ | .gitignore | macOS/エディタ/カバレッジ等 追加済み |

---

## 5. 未対応（将来タスク）

| 項目 | 優先度 | 備考 |
|------|--------|------|
| ANTHROPIC_API_KEY Secret | 中 | Claude Code Action使用時に設定 |
| CODEOWNERS | 低 | チーム拡大時に設定 |
| ESLint導入 | 中 | コード品質の自動チェック |
| LICENSE | 低 | 公開リポジトリには推奨 |

---

## 6. 監査コマンド集（再利用用）

今回使ったgh CLIコマンド。他のリポジトリでも使える。

```bash
# リポジトリ設定の確認
gh api repos/OWNER/REPO --jq '{
  default_branch,
  allow_merge_commit,
  allow_squash_merge,
  allow_rebase_merge,
  delete_branch_on_merge
}'

# セキュリティ設定の確認
gh api repos/OWNER/REPO --jq '.security_and_analysis'

# ブランチ保護ルールの確認
gh api repos/OWNER/REPO/branches/main/protection

# Rulesets の確認
gh api repos/OWNER/REPO/rulesets
gh api repos/OWNER/REPO/rulesets/RULESET_ID | jq '{name, enforcement, rules}'

# Secrets の確認（値は見えない）
gh api repos/OWNER/REPO/actions/secrets --jq '.total_count'

# リモートブランチ一覧
gh api repos/OWNER/REPO/branches --jq '.[].name'

# マージ済みブランチの特定
gh pr list --head "BRANCH_NAME" --state merged
```

---

## 7. 所感と次のアクション

### 気づき
- 個人開発でも最低限のブランチ保護 + Dependabot は必須。設定コストは30分程度だが、放置すると脆弱性に気づけない
- GitHub UIが「Branch protection rules」から「Rulesets」に移行中。ネット記事は旧UIの情報が多いので注意
- Dependabotを有効にした瞬間に11件の脆弱性が検出された。気づかないまま運用していたリスクが大きい
- `.github/` フォルダにはワークフロー以外のプラットフォーム設定も入る、という構造理解が重要

### 次のアクション
- [ ] 今回の知見をNote記事として公開（「個人開発者向けGitHubリポジトリ設定チェックリスト」）
- [ ] 社内共有用にまとめ（新プロジェクト立ち上げ時のテンプレートとして）
- [ ] 他の個人リポジトリにも同じ設定を横展開
- [ ] Dependabotが作成したPRの対応
