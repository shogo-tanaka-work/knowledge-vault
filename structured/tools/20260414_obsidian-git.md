# obsidian-git 検証ログ

> ステータス: 検証中
> 作成日: 2026/04/14
> 最終更新: 2026/04/14
> ファイルパス: /Users/shogo/Obsidian Vault/knowledge-vault/structured/tools/20260414_obsidian-git.md

---

## 📋 検証概要

- **ツール/サービス名**: obsidian-git（Vinzent03/obsidian-git）
- **検証対象**: 新ツール導入
- **バージョン/リリース日**: v2.38.1（2026年4月12日リリース）
- **検証期間**: 2026/04/14 -（検証中）
- **検証担当者**: shogo-tanaka-work
- **検証ステータス**: 検証中

---

## 1. 背景と検証目的

### なぜこの検証を行うのか
- knowledge-vault（ナレッジ管理リポジトリ）をObsidianで参照できるようにすでに設定していたが、Obsidian側からGit操作（コミット・プッシュ）が完結できない状態だった
- Claude Codeがノートを編集した際の変更履歴を追跡したい
- AIによる編集の「監査ログ」としてGitコミット履歴を活用したい

### 解決したい課題
- Obsidianで編集 → 毎回ターミナルでgit操作 という手間をなくしたい
- Claude Code編集 → 自動バックアップ のフローを確立したい
- 複数デバイスで同一リポジトリを参照したい（デスクトップ中心）

### 期待される効果・ビジネスインパクト
- ノート編集から自動コミット・プッシュまでの手作業ゼロ化
- knowledge-vaultのバックアップ信頼性向上
- Claude Code × Obsidian連携ワークフローの基盤整備

---

## 2. ツール/機能の基本情報

### 概要
ObsidianのvaultをそのままGitリポジトリとして管理できるコミュニティプラグイン。自動コミット・プッシュ・プルをObsidian内で完結させる。

### 提供元
- 開発者: Vinzent03（個人開発、OSSコントリビューター）
- GitHub: https://github.com/Vinzent03/obsidian-git
- GitHubスター: 10.4k（2026年4月時点）

### 主要機能
- 指定間隔での自動コミット・プッシュ・プル
- ソースコントロールビュー（ステージ/アンステージ、差分表示）
- コミット履歴ビュー
- エディタ内の変更マーカー表示（デスクトップのみ）

### 技術スタック・アーキテクチャ
- デスクトップ: ローカルのgitバイナリを直接呼び出す（要PATH設定）
- モバイル: isomorphic-git（JS実装）を使用 ← 公式に「非常に不安定」と明記

---

## 3. 検証方法

### 検証環境
- **使用アカウント**: shogo-tanaka-work（GitHub）
- **プラン/エディション**: Obsidian無料版（コミュニティプラグイン利用可）
- **検証環境**: 本番（実際のknowledge-vault）
- **OS**: macOS Darwin 25.2.0

### 検証シナリオ
1. obsidian-gitプラグインのインストール・有効化
2. gitバイナリパスの設定
3. リポジトリ認識の確認
4. 自動コミット・プッシュの動作確認

### 前提条件・制約事項
- knowledge-vaultはすでにGitリポジトリ（origin: github.com:shogo-tanaka-work/knowledge-vault.git）
- Claude Codeで.gitignore整備・CLAUDE.md追加済みのコミットが存在
- モバイルからはCF Workers Remote MCP経由でClaude Code操作するため、モバイル版obsidian-gitは使用しない

---

## 4. 検証結果

### 定性的評価

#### 機能面の評価
- gitバイナリパスを設定すればデスクトップでは問題なく動作
- ソースコントロールビューはGitHubデスクトップアプリに近い操作感

#### 操作性・UI/UX
- インストール後の初期設定にいくつかハマりポイントあり（後述）
- 設定画面が英語のみだが項目は直感的

#### 実用性
- 自動コミット間隔を設定すれば以後は意識不要
- Claude Code編集との組み合わせで「AI編集 → 自動バックアップ」フローが実現

---

### 定量的評価

#### 導入コスト

| 項目 | 内容 | 金額/工数 |
| --- | --- | --- |
| 初期設定時間 | インストール〜動作確認まで | 約1時間（トラブルシュート込み） |
| 学習時間 | 基本操作を習得するまで | 設定後はほぼゼロ |
| 初期費用 | プラグイン自体は無料 | 0円 |

#### 運用コスト

| 項目 | 内容 | 金額 |
| --- | --- | --- |
| 月額利用料 | 無料 | 0円 |
| GitHubストレージ | 通常のテキストノートであれば無料枠内 | 0円 |

---

## 5. 比較・優位性分析

### 既存ツール/類似サービスとの比較

| 項目 | obsidian-git | Obsidian Sync（公式） | Remotely Save |
| --- | --- | --- | --- |
| 機能性 | Git操作フル対応 | 同期のみ | 同期のみ |
| コスト | 無料 | 月額$8〜 | 無料〜 |
| 変更履歴 | Gitで完全保持 | なし | なし |
| モバイル対応 | 不安定 | 安定 | 安定 |
| Claude Code連携 | 最適（同一Gitリポジトリ） | 不可 | 不可 |

### モバイル同期オプション比較（無料運用前提）

| 方法 | 費用 | 安定性 | 設定難易度 | 自動化 |
| --- | --- | --- | --- | --- |
| Obsidian Sync | 月額$8〜 | 安定 | 低 | 完全自動 |
| **a-shell + lg2**（推奨） | **無料** | 中程度 | 中 | 半自動（Shortcuts可） |
| Working Copy | $19.99買い切り | 安定 | 中 | 半自動（Shortcuts可） |
| iSH + git | **無料** | 不安定 | 高 | 手動 |
| Obsidian Gitプラグイン（iOS） | 無料 | 非常に不安定 | 低 | 不可（事実上使用不可） |

### 優位性
- Claude Codeと同一Gitリポジトリを共有するため、AI編集の追跡に最適
- 変更履歴をGitHubで完全管理できる
- 無料で使える

### 劣位性・懸念点
- モバイルのObsidian GitプラグインはiOSサンドボックス制約でネイティブgitが呼べず事実上使用不可
- macOSでgitバイナリのPATH問題が発生する（要手動設定）
- モバイル同期はa-shellなど別アプリを経由する迂回ルートが必要

---

## 6. リスク評価

### セキュリティ

| 評価項目 | 評価 | 詳細 |
| --- | --- | --- |
| データ保管場所 | ✅ | ローカル + GitHubプライベートリポジトリ |
| 認証情報 | ⚠️ | plugins/*/data.jsonに認証トークンが含まれる場合あり → .gitignoreで除外済み |
| アクセス制御 | ✅ | GitHubのSSH認証で管理 |

### 技術的リスク
- 外部SSD上のvaultではObsidianがリポジトリを認識しない場合がある（今回発生）
- モバイルと同時編集した場合の競合リスク → モバイルはobsidian-gitを使わないため回避

---

## 7. 連携性・拡張性

### 既存システムとの連携

| 連携先 | 方法 | 難易度 | 備考 |
| --- | --- | --- | --- |
| Claude Code | 同一Gitリポジトリを共有 | 低 | CLAUDE.mdを配置することでClaudeがvault構造を把握 |
| GitHub | SSH経由でpush/pull | 低 | 設定済み |
| CF Workers Remote MCP | モバイルからClaude Code操作 | 中 | obsidian-gitとは独立した別ルート |
| a-shell（iOS） | lg2コマンドでGitHub経由pull/push | 中 | iPhoneにVaultを同期する手段。Obsidian Gitプラグインの代替 |

---

## 8. 実際の使用例・サンプル

### セットアップの実際の流れ

**シナリオ**: 既存GItリポジトリ（knowledge-vault）にobsidian-gitを追加する

**手順**:
1. Obsidian設定 → Community Plugins → Safe modeをOFF
2. Browse → "Git" → obsidian-git（Vinzent03作）をインストール・有効化
3. プラグイン設定 → Advanced → `Custom Git binary path` に `/usr/local/bin/git` を入力
4. ←ここで「Can't find a valid git repository」エラーが発生（後述）
5. vaultを `/Volumes/PortableSSD/` から `/Users/shogo/Obsidian Vault/` に移動
6. 再度プラグイン設定 → リポジトリ認識を確認 → 成功

### iPhoneでの同期セットアップ（a-shell）

**アーキテクチャ**:

```
[GitHub リポジトリ]
    ↑↓ SSH/HTTPS（lg2コマンド）
[a-shell（iOSターミナルアプリ）]
    ↓ clone先
[iPhoneローカルストレージ "On my iPhone/Obsidian/knowledge-vault/"]
    ↑
[Obsidianアプリ] ← Vaultとして読みに行く
```

**PC vs iPhone の操作比較**:

| 操作 | PC（Obsidian Git プラグイン） | iPhone（a-shell） |
| --- | --- | --- |
| コミット・プッシュ | 自動（設定間隔） | 手動（lg2コマンド） |
| プル | 自動（起動時） | 手動（lg2コマンド） |
| git操作の場所 | Obsidian内UIで完結 | a-shellアプリで実行 |
| 使うgitコマンド | システムgit | `lg2`（libgit2ベース） |

**iPhoneセットアップ手順**:

```bash
# Step 1: SSH鍵生成（a-shell内で実行）
ssh-keygen -t ed25519 -C "your@email.com"
cat ~/.ssh/id_ed25519.pub   # GitHubのSSH keysに登録

# Step 2: ObsidianフォルダをBookmark登録
pickFolder   # ファイルピッカーで「On my iPhone → Obsidian」を選択
renamemark Documents obsidian

# Step 3: 初回クローン
bookmark obsidian
lg2 clone ssh://git@github.com:shogo-tanaka-work/knowledge-vault.git knowledge-vault
cd knowledge-vault
lg2 config user.identityFile "~/Documents/.ssh/id_ed25519"
lg2 config user.name "shogo-tanaka-work"
lg2 config user.email "your@email.com"
# → Obsidianアプリで「フォルダを開く → knowledge-vault」を選択してVaultとして認識
```

**日常のpull/push**:

```bash
# 起動時（PCの変更を取り込む）
bookmark obsidian && cd knowledge-vault && lg2 pull origin

# 終了時（iPhoneの変更をGitHubへ）
bookmark obsidian && cd knowledge-vault && lg2 add . && lg2 commit -m "iOS update" && lg2 push origin
```

Apple Shortcutsに上記コマンドを登録すれば1タップで実行可能。ただし完全自動化は不可（iOSのバックグラウンド制限）。

---

## 9. 学びとナレッジ

### 発見したこと
- ObsidianはシェルのPATHを引き継がないため、gitバイナリのパスを明示的に設定する必要がある
- macOSでHomebrewやカスタムパスにgitをインストールしている場合は特に注意（`/usr/local/bin/git` など）
- `Custom Git binary path` の設定項目は「Advanced」セクションにある
- iOSのObsidian GitプラグインがCannot Findになる根本原因：iOSサンドボックス制約によりネイティブgitバイナリを呼び出せないため。PCとは異なりプラグインが使用不可
- a-shellではUnixの`git`コマンドではなく`lg2`（libgit2ベースの独自実装）を使う。コマンド体系は同じだが呼び出し名が異なる
- ClaudeのiOSアプリはチャットUIのためiPhoneのローカルディレクトリを参照・マウントする機能を持たない。スマホからClaude Codeでknowledge-vaultを操作するにはCF Workers Remote MCP経由が現実的
- .mdファイルは開けるが、.mdxファイルは開けない。AstroにてContent Collectionsを利用するPJがあったが、こちらをObsidianと連携することは出来なさそうだった。

### うまくいったこと
- gitバイナリパスを `/usr/local/bin/git` に設定することでgit認識は解決
- `.gitignore` で `workspace.json`, `cache`, `plugins/*/data.json` を除外し、安全なファイルのみ追跡
- vaultルートに `CLAUDE.md` を追加してClaude Codeにvault構造を説明する設計

### うまくいかなかったこと
- **外部SSD（/Volumes/PortableSSD/）上のvaultでリポジトリが認識されない問題が発生**
  - gitバイナリは認識されたが「Can't find a valid git repository」エラー
  - 原因: macOSのサンドボックスまたは外部ドライブのパス解決の問題と推測
  - 解決策: vaultを内部ストレージ（`/Users/shogo/Obsidian Vault/`）に移動して解決

### Tips・ベストプラクティス
- `.gitignore` の推奨設定:
  ```
  .obsidian/workspace.json
  .obsidian/workspace-mobile.json
  .obsidian/cache
  .obsidian/plugins/*/data.json
  .trash/
  ```
- vaultは内部ストレージに置く（外部ドライブは避ける）
- モバイルでobsidian-gitを使うのは非推奨。モバイルアクセスはCF Workers Remote MCP経由のClaude Code操作で代替
- モバイル同期の使い分け方針：
  - iPhoneでObsidianのUIでノートを読みたい → a-shell + lg2でpullしてVaultを最新化
  - iPhoneからノートを書いてGitHubに反映したい → a-shell + lg2でadd/commit/push
  - iPhoneからClaude Codeでknowledge-vaultを編集・操作したい → CF Workers Remote MCP経由（a-shellは不要）

### よくあるエラーと対処法
| エラー | 原因 | 対処法 |
|---|---|---|
| git not found / PATH error | ObsidianがシェルPATHを引き継がない | Custom Git binary pathに絶対パスを設定 |
| Can't find a valid git repository | 外部ドライブ上のvault or Custom base pathの誤設定 | vaultを内部ストレージに移動、またはCustom base pathを空にする |

---

## 10. 判定と今後のアクション

### 総合評価
⭐️⭐️⭐️⭐️（完了時に更新）
ここのハーネスをつくりこめば非エンジニアでも執筆に関するあらゆる業務をAIで効率化できる
VSCodeを開くのは抵抗がある。~~ClaudeCodeをターミナルで開く時点でどうかという意見もありそうだが~~


### 導入判定
- [x] 条件付きで導入可（vaultを内部ストレージに置く前提）

### 判定理由
- Claude Code × Obsidian連携の基盤として有効
- 無料・軽量で変更履歴管理が可能
- 初期設定にハマりポイントがあるが、一度設定すれば運用コストはほぼゼロ

### 次のステップ
- [ ] 自動コミット間隔の設定と動作確認
- [ ] Claude Codeで編集 → obsidian-gitが自動コミット・プッシュするフローの確認
- [ ] モバイルからのアクセスはCF Workers Remote MCP経由で継続

---

📚 関連リソース

### 公式ドキュメント
- https://github.com/Vinzent03/obsidian-git

### 参考記事・事例
- [Obsidian and Git Quick Setup for Developers（2025年3月）](https://rob.cogit8.org/posts/2025-03-25-obsidian-git-quick-setup-for-developers/)
- [Using Claude Code with Obsidian - Kyle Gao](https://kyleygao.com/blog/2025/using-claude-code-with-obsidian/)
- [Claude Code + Obsidian: Build a Second Brain - DEV Community](https://dev.to/mibii/claude-code-obsidian-build-a-second-brain-that-actually-thinks-d61)
- [What files should I ignore in git? - Obsidian Forum](https://forum.obsidian.md/t/what-files-should-i-ignore-in-git-when-using-obsidian/45554)
- [iOSでa-shellを使ったGitHub自動同期 - Obsidian Forum](https://forum.obsidian.md/t/mobile-automatic-sync-with-github-on-ios-for-free-via-a-shell/46150)
- [iSHなし・Working CopyなしでのiOS Git同期 - Obsidian Forum](https://forum.obsidian.md/t/setting-up-obsidian-git-on-ios-without-ish-or-working-copy/97800)
- [a-shellでObsidian同期（SSH手順詳細） - cwoodall.com](https://cwoodall.com/posts/2022-01-02-obsidian-ios-sync/)

---

✅ メモ・議論ログ
- 外部SSD（PortableSSD）上でのvaultではobsidian-gitがリポジトリを認識しなかった。内部ストレージへの移動で解決。
- モバイルアクセスはCF Workers Remote MCP経由のClaude Code操作で代替するため、モバイル版obsidian-gitは使用しない方針。
- 今後、knowledge-vaultのパスが変わったことでClaude Codeのセッション起動ディレクトリも変更が必要。
- iOSでのObsidianとGitHub同期のアーキテクチャを調査。a-shell（無料）がコミュニティで最も推奨される手段と判明。iSHは動作するが遅くハングリスクあり。
- iPhoneでのGit同期アーキテクチャ：GitHub ↔ a-shell（lg2コマンド） ↔ iPhoneローカルストレージ ← Obsidianアプリ。PC側のObsidian Gitプラグイン（自動）とは異なり、a-shellでの操作は手動トリガー。
- ClaudeのiOSアプリはローカルディレクトリを参照・マウントする機能を持たないため、スマホからknowledge-vaultをClaude経由で操作する場合はCF Workers Remote MCP一択。

---

## 📝 更新ログ
<!-- このセクションはスキルが自動で追記する。手動編集不要。 -->
| 日時 | 更新内容の概要 |
|---|---|
| 2026/04/14 | ファイル作成（init）|
| 2026/04/14 | iPhoneモバイル同期アーキテクチャ（a-shell）の調査結果を追記 |
