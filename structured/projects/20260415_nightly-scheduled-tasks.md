# 夜間定期実行タスク 検証ログ

> ステータス: 進行中
> 作成日: 2026/04/15
> 最終更新: 2026/04/16
> ファイルパス: /Users/shogo/ObsidianVault/knowledge-vault/structured/projects/20260415_nightly-scheduled-tasks.md

---

📋 プロジェクト概要
* カテゴリ: Claude Code自動化 / AI活用最適化
* 期間: 2026/04/15 -（検証中）
* 主要メンバー: 田中省伍
* ステークホルダー: （情報なし）
* プロジェクトステータス: 進行中

---

## 1. 背景と目的

* Claude Maxプランには時間あたり・週あたりのレートリミットがある
* 日中の作業時間だけではそのリミットを100%使い切れていない（就寝中は0%活用）
* 過去のClaude Codeセッションで「レートリミットを使い倒しきれていない」という気づきがあった
* 「寝てる間も動く仕組みを作りたい」という発想が本プロジェクトの発端
* 目標: 非稼働時間帯（主に深夜〜早朝）にClaudeを自律的に動かし、週あたりのレートリミット消化率を最大化する

---

## 2. 取り組み内容

### 実施した施策・活動
* 2026/04/16: shogo-works（Astro製ブログ）向けに AI 記事自動生成システムを構築
  * AIツール（ChatGPT / Gemini / Claude / Codex）関連の技術記事を夜間に自動生成・保存する仕組み
  * cron（02:10）→ `generate-ai-articles.sh` → `claude --permission-mode auto -p` → MDX 保存

### 使用したツール・技術
* Claude Code CLI（`claude --permission-mode auto -p "$(cat prompt.md)"` 形式）
* macOS cron + `pmset` による深夜自動起動
* shogo-works（Astro 6.1.4 + MDX）のコンテンツスキーマ（Zod）

### 主要な意思決定とその理由
* `/schedule` スキル（RemoteTrigger）ではなく **既存の cron インフラに乗せる** 方針を採用
  * 理由: Mac が深夜に確実に起動している前提が成立しており、cron が最もシンプル
* 専用の TypeScript スクリプト（Anthropic SDK）ではなく **Claude Code CLI に prompt.md を渡す** 方式を採用
  * 理由: 追加の依存関係なし・WebSearch や Agent tool が CLI 側で既に使える

---

## 3. 進捗と成果

### 達成できたこと
* cron（02:10）に `generate-ai-articles.sh` を登録し、夜間自動実行の仕組みを構築
* `prompt.md`・`topic-queue.json` によるハイブリッドトピック選定の設計
* Claude がWebSearchで最新AIニュースを収集し、MDX記事の内容自体は正常に生成できることを確認（5記事分のコンテンツ生成を確認）
* 破壊的コマンド（rm / git push / sudo など）を deny リストで永続ブロック

### 定量的な成果
* 生成記事数: 0件保存成功（権限問題により保留中）
* 生成コンテンツ: 5記事分のドラフト内容を確認済み

### 定性的な成果
* 記事品質は既存の shogo-works 記事と遜色ないクオリティで生成できることを確認

---

## 4. 学びとナレッジ

### うまくいったこと（Good）
* Claude Code CLI の `-p` モードで prompt.md を渡すだけで WebSearch・Agent 並列実行が動く
* 記事の内容生成自体は問題なく動作。品質も既存記事と遜色なし
* cron への追加・deny リスト設定など既存インフラへの組み込みは順調

### うまくいかなかったこと（Bad）

**① `timeout` コマンドが macOS 標準に存在しない**
* スクリプト内で `timeout 1740 claude ...` としていたが、macOS はデフォルトで GNU coreutils を持たないため `timeout: command not found` で即終了
* 対処: `timeout` を除去し claude コマンドを直接実行

**② グローバル設定の `defaultMode: "plan"` がバッチ実行を妨害**
* `~/.claude/settings.json` に `"defaultMode": "plan"` が設定されていたため、`--permission-mode auto` で起動しても Claude がプランモードに入り「承認いただければ実行を開始します」で停止
* 対処: プロジェクト設定（`.claude/settings.local.json`）に `"permissions": { "defaultMode": "auto" }` を追加してオーバーライド

**③ 外付けSSDへの Write 権限がサブエージェントに引き継がれない**
* `--permission-mode auto` でも、作業ディレクトリ外（`/Volumes/PortableSSD/...`）への書き込みは別途許可が必要
* `settings.local.json` の `allow` に `Write(/Volumes/...)` を追加したが、サブエージェント（Agent tool で並列生成）には権限が完全には引き継がれなかった
* グローバル設定（`~/.claude/settings.json`）に追加しても解消せず
* **根本的な対処（保留）: shogo-works をローカル（Mac 内蔵ストレージ）に移行する方針に切り替え**

**④ crontab 書き込みがプロジェクト設定の permissions でブロックされた**
* `.claude/settings.local.json` に `"allow": ["Bash(crontab -l)"]` のみ設定されており、`crontab /tmp/xxx` の書き込みがブロックされた
* 対処: `"Bash(crontab /tmp/crontab_new.txt)"` を allow に追加

### 改善ポイント（Improve）
* shogo-works をローカルストレージに移行後、出力パスを更新すれば権限問題は解消される見込み
* macOS 向けスクリプトでは `timeout` の代わりに `perl -e 'alarm(1740); exec @ARGV' -- command` か、Homebrew で `coreutils` を入れて `gtimeout` を使う選択肢がある
* サブエージェントへの権限引き継ぎは `additionalDirectories` だけでは不十分。`Write(path)` を allow に明示的に追加する必要がある

### 技術的な発見・Tips
* `claude --permission-mode auto -p "$(cat prompt.md)"` はバッチ実行の基本形として機能する
* `settings.local.json` の `permissions.defaultMode: "auto"` でグローバルの `plan` モードをプロジェクト単位でオーバーライドできる
* `deny` リストは `--permission-mode auto` でも有効（破壊的コマンドを永続ブロック可能）
* 外付けドライブへの書き込みは `additionalDirectories` に加えて `allow` への `Write(path/**)` の明示追加が必要だが、サブエージェントへの権限引き継ぎは不安定

---

## 5. 課題と対応

### 発生した課題
* 外付けSSD（`/Volumes/PortableSSD/`）への書き込み権限がサブエージェントに引き継がれず、記事ファイルの保存に失敗

### 対応方法
* shogo-works プロジェクトをローカルストレージへ移行する方針に切り替え（リポジトリ整備後に実施予定）

### 未解決の課題
* shogo-works のローカル移行が完了していないため、記事の自動保存が未実現
* ローカル移行後にスクリプト3箇所のパスを更新する必要がある（`generate-ai-articles.sh` / `prompt.md` / `settings.local.json`）

---

## 6. コストとリソース

### 人的リソース
* 設計・実装: 田中省伍（都度）

### 金銭的コスト
* Claude Max プランのレートリミット内で運用（追加課金なし）

### コスト対効果
* （完了時に記入）

---

## 7. 今後の展開

### 次のアクション
* shogo-works を GitHub リポジトリ化 → ローカル（Mac 内蔵）にクローン
* スクリプト3箇所のパス更新（`SSD_PATH` → ローカルパス）
* 再度 `bash ~/scripts/generate-ai-articles.sh` で動作確認

### 横展開の可能性
* 同様のアプローチを他のAIツール（Gemini、GPT等）のAPI枠活用にも応用できる可能性

### 長期的な改善案
* 夜間実行の結果を朝のダッシュボード（Obsidian）に自動集約する仕組みの構築
* タスクの実行履歴・成果をログとして蓄積し、どのタスクが効果的かを評価する

---

📚 関連リソース

### 成果物・ドキュメント
* `/Users/shogo/夜間定期実行タスク/ai-article-generator/prompt.md` — 記事生成指示プロンプト
* `/Users/shogo/夜間定期実行タスク/ai-article-generator/topic-queue.json` — トピックキュー
* `/Users/shogo/scripts/generate-ai-articles.sh` — 実行スクリプト
* crontab: `10 2 * * * /Users/shogo/scripts/generate-ai-articles.sh`

### 参考資料
* （随時更新）

### 関連プロジェクト
* `/schedule` スキル関連ドキュメント
* `nightly-executor` スキル
* knowledge-vault パイプライン（`raw/` → `structured/` フロー）

---

✅ メモ・雑記
* プロジェクト発端: 過去のClaude Codeセッションでレートリミット未活用の問題を認識
* Claude Maxプランの時間あたり・週あたりのレートリミットを就寝中に消化できれば、実質的な利用効率が大幅に向上する

---

## 📝 更新ログ
<!-- このセクションはスキルが自動で追記する。手動編集不要。 -->
| 日時 | 更新内容の概要 |
|---|---|
| 2026/04/15 | ファイル作成（init）— プロジェクト背景・動機・タスク候補を初期投入 |
| 2026/04/16 | 実装セッション記録 — スクリプト構築・ハマりポイント（timeout/plan mode/SSD権限）・現状と次のアクションを追記 |
