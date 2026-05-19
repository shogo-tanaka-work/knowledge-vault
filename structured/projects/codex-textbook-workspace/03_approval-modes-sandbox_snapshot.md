# Snapshot: approval-modes-sandbox（2026-05-08 取得）

## ソース URL

1. https://developers.openai.com/codex/agent-approvals-security
2. https://developers.openai.com/codex/concepts/sandboxing
3. https://developers.openai.com/codex/config-reference
4. https://github.com/openai/codex/releases （CHANGELOG.md は releases ページへリダイレクト）

## 主要な確定事項（既存 mdx との差分）

### 1. config.toml のキーは「トップレベル」が正

既存 mdx は `[permissions.default] approval = "..."` という古いネスト構造で書かれているが、現行 reference では:

```toml
approval_policy = "on-request"   # untrusted | on-request | never | { granular = { ... } }
sandbox_mode    = "workspace-write"  # read-only | workspace-write | danger-full-access
```

### 2. granular のキーは boolean

- `sandbox_approval`（サンドボックスエスカレーション要求の挙動）
- `rules`（execpolicy ルールにマッチした時のプロンプト）
- `mcp_elicitations`（MCP からのプロンプト）
- `request_permissions`（追加権限要求のプロンプト）
- `skill_approval`（スキルスクリプトの承認）

```toml
approval_policy = { granular = {
  sandbox_approval = true,
  rules = true,
  mcp_elicitations = true,
  request_permissions = false,
  skill_approval = false
} }
```

### 3. CLI フラグ

```bash
codex --sandbox workspace-write --ask-for-approval on-request
codex --sandbox read-only --ask-for-approval on-request
codex --ask-for-approval never -a never
```

`-a` は `--ask-for-approval` のショート形。

### 4. ネットワーク制御の正しい書式

```toml
[permissions.<name>.network]
enabled = true
mode    = "limited"   # limited | full

[permissions.<name>.network.domains]
"api.github.com"      = "allow"
"registry.npmjs.org"  = "allow"
"*.internal.example"  = "deny"

[permissions.<name>.network.unix_sockets]
"/tmp/my-service.sock" = "allow"
```

`proxy_url` / `socks_url` / `enable_socks5` も同セクションで指定可能。

### 5. workspace-write 拡張キー

```toml
[sandbox_workspace_write]
writable_roots       = ["/path/to/extra"]   # 追加で書込許可
network_access       = false                # ワークスペース書込時のネット可否
exclude_slash_tmp    = false
exclude_tmpdir_env_var = false
```

### 6. 管理者強制設定（requirements.toml）

- `allowed_sandbox_modes`
- `allowed_approval_policies`
- `allowed_web_search_modes`
- `permissions.filesystem.deny_read`
- `rules.prefix_rules`（pattern / decision: `prompt | forbidden` / justification）

### 7. プロファイル

```toml
[profiles.<name>]
# sandbox_workspace_write / web_search / windows.sandbox を上書き
```

### 8. 「常に書き込み禁止」の保護ディレクトリ

公式 sandboxing ページには明示リストなし → 既存 mdx の `.git/ .agents/ .codex/` 表記は一次ソースに直接対応せず。記述は**控えめに「機密ディレクトリは保護される」程度に弱める**か、CLI 実装側のドキュメントが見つかる場合のみ復活。今回は弱めに変更。

### 9. /permissions コマンド

「チャットや計画モードで変更を行わない場合、`/permissions` コマンドで `read-only` モードに切り替える」と記述あり。動的に権限レベルを調整できる。

### 10. v0.129.0（2026-05-07）の関連変更

- Windows sandbox: 名前付きパイプアクセス、ConPTY 終了、PowerShell allow ルール、worktree `safe.directory`、unsafe Git オプション処理を改善
- カスタム CA 認証を TLS インスペクションプロキシ配下で修正
- 実行ポリシー: heredoc リダイレクトの承認マッチング改善
- Linux サンドボックス: 古い `bwrap`、スローマウントプローブ、シンボリンク保護、共有 `/tmp` セットアップでの信頼性向上
- MCP / Hook 出力: 際限のない出力増大に対する境界処理を追加

## 反映方針（mdx 更新）

- 全 TOML 例を新書式に書き直す
- granular の値を boolean に修正
- ネットワーク許可ルールを新書式 `[permissions.<name>.network.domains]` map 形式へ
- CLI フラグ `--ask-for-approval` を併記
- `常に書き込み禁止` ブロックは弱めに表現
- 「最近の更新」節を新設し v0.129.0 のサンドボックス強化を 1 段落で要約
- frontmatter に `updatedAt: 2026-05-08` を追加
