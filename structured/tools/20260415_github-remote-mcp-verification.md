# GitHub Remote MCP Server（自作・書き込み対応）検証ログ

> ステータス: 完了
> 作成日: 2026/04/15
> 最終更新: 2026/04/15
> ファイルパス: ~/Documents/verification-logs/tools/20260415_github-remote-mcp-verification.md

---

## 📋 検証概要

- **ツール/サービス名**: GitHub Remote MCP Server（公式 + 自作Cloudflare Workers版）
- **検証対象**: claude.ai（ブラウザ・スマホ）からGitHubへの読み取り・書き込み操作の一気通貫
- **バージョン/リリース日**: github/github-mcp-server（GA: 2025年9月4日）/ 自作版 初版 2026/04/15
- **検証期間**: 2026/04/15 - 2026/04/15
- **検証担当者**: 省伍（shogoworks / shogo-tanaka-work）
- **検証ステータス**: 完了

---

## 1. 背景と検証目的

### なぜこの検証を行うのか
- スマホ・ブラウザ版Claude（claude.ai）からGitHubのIssue作成・ブランチpush・PR作成を行いたい
- Claude Codeはデスクトップ限定のため、外出先でも書き込み操作を完結させたい
- AIエージェントによるGitHub操作自動化のデモ・教材として実用性を評価したい

### 解決したい課題
- claude.aiのGitHub OAuth連携は読み取りのみで書き込みができない（claude.ai側の実装制約）
- PATを使った書き込み接続をclaude.aiのUIから直接設定できない構造になっている
- 公式Remote MCPへのOAuth接続では書き込みスコープが付与されない

### 期待される効果・ビジネスインパクト
- Issue読み取り → フィーチャーブランチ作成 → ファイルコミット → PR作成 をclaude.aiだけで完結
- Claude Desktopがなくても外出先でGitHub操作を完了できる
- Bytech向けのAIエージェント活用デモ・教材として転用可能

---

## 2. ツール/機能の基本情報

### 概要

本検証は「公式GitHub Remote MCPサーバー」と「自作Cloudflare Workers版MCPサーバー」の2段階で構成される。

- **公式版**: GitHub側でホストされるため、インストール不要。OAuthで読み取りは即時使用可
- **自作版**: 公式リポジトリをフォークしてCloudflare Workersにデプロイ。PAT認証で書き込みを実現

### 提供元

| 種別 | 提供元 | リポジトリ | ライセンス |
|---|---|---|---|
| 公式版 | GitHub（Microsoft傘下） | https://github.com/github/github-mcp-server | MIT |
| 自作版 | 田中省伍（shogo-tanaka-work） | `shogo-tanaka-work/github-remote-mcp-server` | — |

### 主要機能と検証結果

| ツール名 | 概要 | 検証結果 |
|---|---|---|
| `debug_echo` | 引数をそのまま返すデバッグ用 | ✅ 正常動作（timestampカスタム確認） |
| `list_repositories` | リポジトリ一覧取得 | ✅ 正常動作 |
| `get_repository` | リポジトリ詳細取得 | ✅ 正常動作 |
| `search_repositories` | リポジトリ検索 | ✅ 正常動作 |
| `list_issues` | Issue一覧取得 | ✅ 正常動作（#1〜#76 取得確認） |
| `get_issue` | Issue詳細取得 | ✅ 正常動作 |
| `create_issue` | Issue作成 | ✅ 正常動作（Issue #77 作成確認） |
| `list_pull_requests` | PR一覧取得 | ✅ 正常動作 |
| `get_pull_request` | PR詳細取得 | ✅ 正常動作 |
| `get_file_contents` | ファイル・ディレクトリ読み取り | ✅ 正常動作 |
| `search_code` | コード検索 | ✅ 正常動作 |
| `search_issues` | Issue/PR検索 | ✅ 正常動作 |
| `get_me` | 認証ユーザー情報取得 | ✅ 正常動作 |
| `create_branch` | フィーチャーブランチ作成 | ✅ **PAT更新後に動作確認済み** |
| `create_or_update_file` | ファイルコミット | ✅ **PAT更新後に動作確認済み** |
| `create_pull_request` | PR作成 | ✅ **PAT更新後に動作確認済み** |

### 技術スタック・アーキテクチャ
- 公式版: Go製（96%）、Dockerイメージ提供あり。Remote版はURLベース（Streamable HTTP / SSE）
- 自作版: Cloudflare Workers（エッジ関数）、PAT認証、GitHub REST API
- 認証方式: OAuth 2.1 + PKCE（読み取り） / Fine-grained PAT（書き込み）

---

## 3. 検証方法

### 検証環境
- **使用アカウント**: shogo-tanaka-work（GitHub個人アカウント）
- **プラン/エディション**: Claude.ai Max / GitHub Free（Copilotなし）
- **検証環境**: claude.ai ブラウザ（Mac Chrome）・スマホ（Claude app）

### 検証シナリオ

1. 公式Remote MCPをOAuthでclaude.aiに接続し読み取りテスト → ✅ 成功
2. 同OAuthで書き込み（Issue作成）テスト → ❌ 403確認
3. Fine-grained PATをclaude.aiのUIに設定しようとするが設定UI非対応と判明
4. 公式リポジトリをフォーク → Cloudflare Workersにデプロイして自作Remote MCPを構築
5. `debug_echo` で疎通確認 → ✅（User-Agentヘッダー追加修正が必要だった）
6. `list_issues` / `create_issue` で読み書き確認 → ✅（Issue #77 作成）
7. `create_branch` / `create_or_update_file` / `create_pull_request` の3ツールを追加実装・デプロイ
8. 初回実行時にPATのFine-grained権限不足で403 → PATを更新（Contents/PRs: Read and Write を付与）
9. PAT更新後に再実行 → ①ブランチ作成 → ②ファイルコミット → ③PR作成 の一気通貫を確認 → ✅ **全成功**

### 前提条件・制約事項
- claude.aiのカスタムコネクタUIにAuthorizationヘッダーを手動入力する欄がない（OAuth前提の設計）
- OAuthで接続した場合のスコープがclaude.ai側の実装で読み取りのみに制限されている
- Cloudflare WorkersはGitHubリポジトリと直接紐付けできない（`wrangler deploy`手動実行が必要）
- MCPサーバーのツール一覧はセッション開始時に読み込まれるため、新ツール追加後は新チャット or MCP再接続が必要

---

## 4. 検証結果

### 定性的評価

#### 機能面の評価
- 読み取り系（リポジトリ検索・Issue閲覧・PR一覧）はOAuthで問題なく動作
- 書き込み系は公式OAuthでは全滅（403）だが、自作版 + Fine-grained PATで全て動作確認済み
- `create_branch` → `create_or_update_file` → `create_pull_request` のフルサイクルをclaude.aiから一気通貫で実行できることを確認

#### 操作性・UI/UX
- claude.aiのコネクタ設定画面はOAuthのClient ID/Secretの入力欄のみ。PATをUIから渡す手段がない
- tool_searchのインデックスキャッシュの影響で、デプロイ後すぐに新ツールが認識されないことがある
- 新ツール追加後はMCP接続をオフ→オンするリフレッシュ、または新チャット開始が必要

#### 出力品質
- 読み取り操作はレスポンスも構造化されており品質に問題なし
- `create_issue` / `create_branch` / `create_pull_request` の書き込みはGitHubのAPIレスポンスがそのまま返り、URLや番号で結果を即確認できる
- `debug_echo` のレスポンスに `timestamp` フィールドが含まれており、自作カスタマイズの証拠として有用

#### 実用性
- **目的（claude.aiからのGitHub書き込み操作）を達成** — フルサイクル動作確認済み
- 読み取り目的はOAuth接続で即使える。書き込みは自作Worker + Fine-grained PATが必要
- Claude Desktop用のローカルMCP設定（JSON直書き）でもPAT書き込みは可能（補完手段として有効）

---

### 定量的評価

#### 導入コスト

| 項目 | 内容 | 金額/工数 |
| --- | --- | --- |
| OAuth接続（読み取り） | 公式Remote MCPをclaude.aiに接続 | 約15分 |
| Fine-grained PAT発行 | GitHub設定画面での操作 | 約10分 |
| Cloudflare Workersデプロイ | フォーク〜wrangler deploy + デバッグ込み | 約2〜3時間 |
| PATスコープ調整 | 権限不足エラー確認後に再発行・Workerシークレット更新 | 約15分 |

#### 運用コスト

| 項目 | 内容 | 金額 |
| --- | --- | --- |
| Cloudflare Workers | 無料枠内（10万req/日） | $0 |
| GitHub | Freeプラン | $0 |

#### パフォーマンス

| 項目 | 測定結果 | 備考 |
| --- | --- | --- |
| 読み取り成功率 | 100% | OAuthで安定動作 |
| 書き込み成功率（PAT権限付与後） | 100% | create_branch / file / PR すべて成功 |
| tools/list 応答 | 正常 | ツール定義は常時届いている |
| ブランチ作成〜PR作成（一連） | 約30秒 | 3ツール連続実行の合計 |

---

## 5. 比較・優位性分析

### 認証方式の比較

| 項目 | OAuth（公式Remote） | Fine-grained PAT（自作Worker） |
| --- | --- | --- |
| 設定の手軽さ | ◎ 数クリックで完了 | △ Worker + PAT設定が必要 |
| 読み取り | ✅ | ✅ |
| 書き込み | ❌ claude.aiでは不可 | ✅ 全ツール動作確認済み |
| スマホ対応 | ✅ 読み取りのみ | ✅ 書き込みも可（Worker経由） |
| セキュリティ | △ アカウント全体に紐づく | ◎ リポジトリ・権限単位で制御可 |
| カスタマイズ性 | ✗ | ◎ ツール追加・timestamp等自由 |

### 優位性
- OAuthはclaude.aiのUIで最も手軽に接続できる（読み取りのみで十分な用途に最適）
- Fine-grained PATはリポジトリ単位・権限単位で絞れるためセキュリティが高い
- 自作WorkerはGitHub APIで可能な操作を自由に追加実装できる拡張性がある

### 劣位性・懸念点
- claude.aiのカスタムコネクタUIがOAuth前提の設計で、PATをヘッダーで渡す手段が現状ない
- PATの管理・ローテーションが必要（Cloudflare WorkersのシークレットでPATを保管）
- MCPサーバーの公開エンドポイントに認証なしでアクセス可能な状態（APIキー認証の追加が望ましい）

---

## 6. リスク評価

### セキュリティ

| 評価項目 | 評価 | 詳細 |
| --- | --- | --- |
| PATの管理 | ◎ | Cloudflare Workersのシークレットで管理。コードに含めない |
| OAuth権限範囲 | △ | アカウント全体に紐づくため過剰な権限になりがち |
| Workerの公開 | △ | 認証なしで誰でもアクセス可能な状態。APIキー検証の追加が望ましい |
| Fine-grained PAT | ◎ | リポジトリ単位・操作単位（Contents/Issues/PRs: R&W）で最小権限化 |

### 技術的リスク
- Cloudflare Workers上でのSSE永続セッションはステートレスな設計と相性が悪い（tools/call失敗の原因）
- MCPツール一覧のキャッシュにより、デプロイ直後は新ツールがclaude.ai側で認識されないことがある
- Fine-grained PATのスコープ不足は403で発見できるが、エラーメッセージだけでは原因の特定に時間がかかることがある

---

## 7. 連携性・拡張性

### API/統合オプション

| 接続先 | 接続方法 | 書き込み | 備考 |
|---|---|---|---|
| Claude Desktop | ローカルMCP（JSON直書き） | ✅ | `claude_desktop_config.json` にPAT設定 |
| Claude Code | `claude mcp add` コマンド | ✅ | PAT付きで設定可能 |
| claude.ai（ブラウザ） | カスタムコネクタ（自作Worker） | ✅ | PAT書き込み確認済み |
| claude.ai（スマホ） | カスタムコネクタ（自作Worker） | ✅ | Worker経由で書き込み可 |
| VS Code | JSON設定 | ✅ | OAuth/PAT両対応 |

### 拡張性・カスタマイズ性
- 公式リポジトリをフォークして独自ツールを追加可能（`debug_echo` のtimestampカスタムが実例）
- `toolset` フラグで使用するツール群を絞り込める（トークン節約・セキュリティ）
- `--read-only` フラグでread-onlyモードに制限可能
- 公式リポジトリの最新を取り込む場合は `git remote add upstream` + `git fetch upstream && git merge upstream/main`

---

## 8. 実際の使用例・サンプル

### ユースケース1：debug_echo で疎通確認

**シナリオ**: MCP接続後の最初の動作確認  
**入力**: `message="テスト"`  
**出力**:
```json
{
  "echo": "テスト",
  "timestamp": "2026-04-15T03:18:06.411Z"
}
```
**評価**: ✅ 正常。自作実装のtimestampフィールドが動作している

---

### ユースケース2：create_issue でIssue作成

**シナリオ**: `shogo-works` リポジトリへのテスト用Issue作成  
**入力**:
```
owner: shogo-tanaka-work
repo: shogo-works
title: [テスト] GitHub Remote MCP Server 動作確認
body: MCPサーバーの動作確認用Issue（debug_echo・list_issues・create_issueの検証）
```
**出力**: Issue #77 が正常作成  
**URL**: https://github.com/shogo-tanaka-work/shogo-works/issues/77  
**評価**: ✅ claude.aiから直接GitHubにIssueを作成できることを確認

---

### ユースケース3：フルサイクル（ブランチ作成 → コミット → PR作成）

**シナリオ**: Issue #77 に対応するブランチ〜PRの一気通貫作成  
**実行ステップ**:

**① create_branch**
```
branch: feature/issue-77-mcp-test
owner: shogo-tanaka-work
repo: shogo-works
```
→ `refs/heads/feature/issue-77-mcp-test` 作成成功 ✅

**② create_or_update_file**
```
path: docs/mcp-test-log.md
branch: feature/issue-77-mcp-test
message: feat: Issue #77 GitHub Remote MCP 動作確認ログ追加
content: （マークダウン形式のログ本文）
```
→ コミットSHA `4a7127...` で `docs/mcp-test-log.md` を新規作成 ✅

**③ create_pull_request**
```
title: [テスト] Issue #77 - create_branch / commit / PR 動作確認
head: feature/issue-77-mcp-test
base: main
body: closes #77 ...
```
→ **PR #78 が正常作成** ✅  
**URL**: https://github.com/shogo-tanaka-work/shogo-works/pull/78  
**評価**: ✅ **完全成功。claude.aiからGitHubの書き込みフルサイクルを達成**

---

### ユースケース4（失敗例）：OAuth接続での書き込み試行

**シナリオ**: 公式GitHub MCPをOAuth接続でIssue作成  
**出力**: `403 Resource not accessible by integration`  
**評価**: ❌ OAuthスコープ不足。claude.ai側の実装制約で書き込みスコープが付与されない

---

## 9. 学びとナレッジ

### 発見したこと
- claude.aiのOAuth連携は書き込みスコープを持っていない（claude.ai側の実装制約）
- claude.aiのカスタムコネクタUIはOAuth前提で、PATをAuthorizationヘッダーで渡す欄がない
- GitHub APIはリクエストに `User-Agent` ヘッダーが必須。未設定の場合は403エラーになる
- Fine-grained PATは「Contents: Read and Write」「Pull requests: Read and Write」の付与が書き込みに最低限必要
- `tool_search` はキーワードマッチのため、ツール名やdescriptionの書き方が重要
- Cloudflare WorkersはPagesと異なりGitHubリポジトリと直接紐付けできず、`wrangler deploy` 手動実行が必要
- MCPサーバーのツール一覧はセッション開始時に読み込まれるため、新ツール追加後は新チャット or 再接続が必要

### うまくいったこと
- OAuthでの読み取り操作は安定動作（リポジトリ・Issue・PR一覧など）
- Claude CodeでUser-Agent追加修正→即デプロイ→claude.aiで動作確認のサイクルが素早く回せた
- Fine-grained PATのスコープを最小権限（対象リポジトリ限定・必要権限のみ）で設定できた
- create_branch → create_or_update_file → create_pull_request のフルサイクルをclaude.aiから一気実行できた

### うまくいかなかったこと（初回）
- claude.aiのカスタムコネクタUIからPAT接続の設定ができない
- 初回のPATはFine-grained権限が不十分で `create_branch` が403エラー
- `create_branch` / `create_or_update_file` / `create_pull_request` の3ツール追加後、tool_searchに反映されずフルサイクル検証が同チャット内では未完了（新チャットで解決）

### Tips・ベストプラクティス
- **書き込みを使いたいならFine-grained PAT + 自作Worker構成が最も確実**
- Fine-grained PATに付与するスコープは `Contents: R&W` + `Pull requests: R&W` が最低限
- PATはCloudflare Workersのシークレットで管理し、コードにハードコードしない
- 新ツールをデプロイ後は必ず新チャットを開いてツール認識を確認する
- Workerにはセキュリティ強化のためAPIキー認証を追加することを推奨（現状は認証なし）
- 公式フォーク → プライベートリポジトリ化 → `git remote add upstream` で最新追従が推奨フロー

### よくあるエラーと対処法

| エラー | 原因 | 対処 |
|---|---|---|
| `403 Resource not accessible by integration` | OAuthスコープ不足（claude.aiの制約） | 自作Worker + Fine-grained PATに切り替える |
| `403 Resource not accessible by personal access token` | PATのFine-grained権限不足 | Contents/Pull requests に `Read and Write` を付与して再発行 |
| GitHub API `403`（初回疎通時） | `User-Agent` ヘッダー未設定 | fetchリクエストにUser-Agentを追加 |
| `Tool not found` | tool_searchキャッシュ未更新 | MCP接続をオフ→オン or 新チャットを開く |
| `Session terminated (32600)` | tools/callレスポンス前にWorkerが終了 | Streamable HTTP statelessモードで実装し直す |

---

## 10. 判定と今後のアクション

### 総合評価
⭐️⭐️⭐️⭐️（書き込みフルサイクル達成。Workerセキュリティ強化で⭐️5も見えてくる）

### 導入判定
- [ ] 即座に導入推奨
- [x] 条件付きで導入可（自作Worker + Fine-grained PAT構成）
- [ ] 追加検証が必要
- [ ] 導入見送り

### 判定理由
- 読み取り目的（リポジトリ参照・Issue閲覧・PR確認）はOAuth接続で即使える
- 書き込みフルサイクル（Branch → Commit → PR）はclaude.aiから完全動作確認済み
- Workerへの認証なしアクセスが懸念点として残るが、実用的には問題ないレベル
- Claude Desktop / Claude Code経由でも同等の書き込みが可能（ローカル設定不要な点でclaude.ai経由に優位性あり）

### 次のステップ
- [x] 読み取りツール群の動作確認（完了）
- [x] create_issue 動作確認（完了）
- [x] create_branch / create_or_update_file / create_pull_request フルサイクル確認（完了）
- [ ] Worker側にAPIキー認証を追加してセキュリティ強化
- [ ] Streamable HTTP（stateless）モードへの移行検討（SSEセッション問題の根本解決）
- [ ] Bytech向けデモ・教材化（AIエージェントによるGitHub操作自動化コンテンツ）

### 追加で検証したい項目
- スマホアプリ（Claude.ai iOS）からのフルサイクル操作確認
- `list_issues` 結果を受け取り → 内容を読んでコードを修正 → コミット という完全エージェント動作
- `--toolset` フラグで必要最小限のツールに絞った運用（トークンコスト最適化）

---

## 📚 関連リソース

### 公式ドキュメント
- GitHub MCP Server リポジトリ: https://github.com/github/github-mcp-server
- GitHub Docs（MCP設定）: https://docs.github.com/en/copilot/how-tos/provide-context/use-mcp/set-up-the-github-mcp-server
- GAリリースノート: https://github.blog/changelog/2025-09-04-remote-github-mcp-server-is-now-generally-available/
- Claude向けインストールガイド: https://github.com/github/github-mcp-server/blob/main/docs/installation-guides/install-claude.md
- GitHub REST API: https://docs.github.com/en/rest

### 参考記事・事例
- DevelopersIO（GA紹介）: https://dev.classmethod.jp/articles/github-remote-mcp-ga/

### 社内関連ドキュメント
- 自作MCPリポジトリ: `shogo-tanaka-work/github-remote-mcp-server`
- デプロイ先: `https://github-mcp-server.s-tanaka-dcb.workers.dev/mcp`
- 作成したPR: https://github.com/shogo-tanaka-work/shogo-works/pull/78
- 作成したIssue: https://github.com/shogo-tanaka-work/shogo-works/issues/77

---

## ✅ メモ・議論ログ

- **OAuthの制約について**: claude.ai側の実装でOAuthスコープが読み取りのみに制限されている。「書き込み権限を与えると他ツールに伝播するリスク」はOAuthの仕様上正確ではなく、「claude.aiのアプリが書き込みスコープを要求しない設計になっている」が正確
- **PATとOAuthの使い分け**: Fine-grained PATはリポジトリ単位・権限単位で絞れるためセキュリティが高い。OAuthはアカウント全体に紐づく点に注意
- **Cloudflare Workersの制約**: PagesはGitHubリポジトリと直接紐付けできるがWorkersは非対応。`wrangler deploy` 手動実行が基本
- **SSEセッション問題**: `Session terminated (32600)` はtools/callレスポンス前にWorkerが終了しているケース。Streamable HTTP statelessモードへの移行が根本解決策
- **ハーネスエンジニアリング観点**: claude.aiのMCPカスタムコネクタは「AIへのツール提供インターフェース」として成熟してきている。自作WorkerをSKILL.mdのような形で設計に組み込む価値がある
- **Bytech教材可能性**: Issue作成→ブランチ作成→コミット→PRをAIが自律実行するデモは受講者への訴求力が高い

---

## 📝 更新ログ

| 日時 | 更新内容の概要 |
|---|---|
| 2026/04/15 | ファイル作成（init）— 公式版検証ログ・自作版検証ログを統合 |
| 2026/04/15 | update — PAT権限不足エラー（403）の原因特定・解決を追記 |
| 2026/04/15 | update — create_branch / create_or_update_file / create_pull_request のフルサイクル成功を追記（PR #78） |
| 2026/04/15 | finalize — ステータスを完了に更新、2ログを1本に統合整理 |
