# Supabase 公式ドキュメント全リサーチ → 自分用教材化（SHO-179）検証ログ

> ステータス: 完了
> 作成日: 2026/05/08
> 最終更新: 2026/05/08
> 完了日: 2026/05/08
> ファイルパス: /Users/shogo/Documents/AI事業OS/30_プロジェクト別/knowledge-vault/vault/structured/projects/20260508_supabase-textbook.md

---

📋 プロジェクト概要
* カテゴリ: ナレッジ蓄積 / BaaS リサーチ / byTech 講座教材化
* 期間: 2026/05/08 - 2026/05/08（1日完了）
* 主要メンバー: 田中省伍
* ステークホルダー: byTech 受講生（将来の派生コンテンツ読者）
* プロジェクトステータス: 完了

---

## 1. 背景と目的

* Supabase はアップデート頻度が高く、把握が追いついていない
* ISO/IEC 27001 取得などにより、エンタープライズ／実務レベルのセキュリティ担保がしやすくなってきた印象
* Data API 周り（テーブル追加系）にも新機能が出ている
* 「何がどこまで安全に使えるか」を自分の中で整理し、プロダクト改善ヒントとしても使える状態にする
* 今後 byTech 講座で非エンジニア／バイブコーダーが Supabase を採用するケースが増える見込み。先回りして日本語の体系教材を用意する土台にする
* Linear タスク: [SHO-179](https://linear.app/shogoworks/issue/SHO-179)

---

## 2. 取り組み内容

### 実施した施策・活動
* 2026/05/08 計画策定。`~/.claude/plans/mcp-show-179-spa-inherited-puddle.md` に実行計画と Step Ledger を配置（state of truth）
* 2026/05/08 robots.txt 確認（`Allow: /`、AI 学習・検索とも明示許可）

### 使用したツール・技術
* WebFetch（主軸の取得手段）
* Exa CLI（Launch Week / Changelog の横断要約に補助利用予定）
* browser-use CLI（JS 必須ページのみ例外的に利用予定）
* Claude Code サブエージェント（Explore / general-purpose / web-researcher を並列・直列で使い分け）
* `ai-verification-log` スキル（本ログ管理）
* `knowledge-transform` スキル（Phase 6 以降の派生時）

### 主要な意思決定とその理由
* スコープ：「コア概念フル」+「セキュリティ網羅」+「最新アップデート（副）」のハイブリッドに決定。SDK リファレンスは目次レベルで押さえる
* 読み手：自分用 → 公開用派生の 2 段構え
* 正本保存先（公開）：`shogo-works/repo/src/content/knowledge/web-development/supabase-docs/` 配下の `.mdx`（Astro コンテンツコレクション、HP のナレッジページとして公開）。Note 等への二次展開は別タスクで派生
* 非公開ワークスペース（URL 一覧・自分用メモ）：`knowledge-vault/vault/structured/projects/supabase-textbook-workspace/`
* セッション運用：1 セッション 1〜2 ステップで進行（コンテキスト＆レート上限考慮）。進捗台帳はプラン本体の Step Ledger に集約
* 取得手段優先順位：WebFetch → Exa → browser-use（例外時のみ）

---

## 3. 進捗と成果

### 達成できたこと
* 計画策定完了（Step Ledger 24 ステップを定義）
* `ai-verification-log init` 実行完了（本ファイル作成）
* shogo-works HP の Astro コンテンツコレクションに **20 章の `.mdx` ファイル** を全て公開可能な状態で配置
* `astro check` で 0 errors / 0 warnings 達成（73 ファイル検証）

### 定量的な成果
* 公開ファイル数：20 ファイル（00_index、10_overview、20-27コア8章、30-34セキュリティ5章、40-41アップデート2章、50リファレンス目次、90改善ヒント、99ソース）
* 取得済 Supabase docs URL 総数：2,075 件（うち章別に WebFetch で取得した一次ソース：約 130 件）
* コア章のコード例：約 50 テーマ
* セキュリティ章のマトリクス：機能×安全度4段階×プラン依存
* Launch Week ダイジェスト：LWX〜LW15+Dec2025の7イベント、49ハイライト
* Changelog ダイジェスト：2025-05〜2026-05の43エントリ、6トレンド

### 定性的な成果
* 公式 docs 2,000ページを「コア概念フル + セキュリティ網羅 + 最新動向（副）」のスコープで日本語教材化
* 「安全に使える領域マップ」を中核アウトプットとして整理（採用判断時の判断軸として再利用可能）
* byTech 講座の入門/実務/採用判断3コースに展開可能な構成
* HP に直接公開できる Astro 形式のため、二次展開（Note / Udemy / SNS）の元ソースになる

---

## 4. 学びとナレッジ

### うまくいったこと（Good）
* **計画書の Step Ledger をセッション横断の state of truth にする運用**：1セッション1〜2ステップでも進捗が一目で分かり、復帰コストがほぼゼロだった
* **3〜4並列のサブエージェント分担**：コア章8つを3並列バッチで進められ、context 効率が良かった
* **frontmatter を必須最小限に絞った決定**：`gas-best-practices.mdx` 準拠を緩めたことで本文の構成（要点/解説/使い方/注意点/原文）にフォーカスでき、章ごとのトーンが揃った
* **safe zones map を最後の統合作業として自分で書く方針**：横断視点が要る章はサブエージェントに任せず統合者が書くことで品質が上がった
* **`astro check` でゼロエラーを保証**：MDX の構文エラーを最終工程で機械的に検証

### うまくいかなかったこと（Bad）
* **web-researcher エージェントが Write 権限を持たない仕様を見落とし**：Phase 4 で2エージェントの出力を自分で書き戻す必要があった。事前に general-purpose を使うべきだった
* **公式 docs の 404 が想定より多かった**：Database/Migrations や RLS Performance 等いくつかのページが 404。代替ソース（GitHub リポジトリ、別カテゴリのページ）で補ったが、最初に sitemap で実 URL を引いてから依頼すれば回避できた
* **Management API リファレンスが WebFetch サイズ上限超で取得できず**：「要追記」で残った

### 改善ポイント（Improve）
* サブエージェント発注前に Write 権限の有無を確認する運用フローに修正
* WebFetch の URL リストは sitemap から実 URL を引いた後で渡す
* 並列バッチのバッチ数は3〜4を上限に固定するとレート制限に当たらない
* 「公開先と非公開ワークスペースを早い段階で分離する」決定は他プロジェクトでも踏襲したい

### 技術的な発見・Tips
* Astro `knowledge` コレクションのスキーマ：`title / description / category / createdAt` の4つが必須、それ以外（sortOrder/tags/author等）は任意
* Supabase 直近のトレンド：「セキュリティ・バイ・デフォルト」（OpenAPI 匿名アクセス廃止、Data API デフォルト非公開化、JWT 非対称署名）
* AI/エージェント対応の機能追加が急速：Remote MCP Server、Claude Code プラグインヒント、AI Assistant v2、postgres.new
* Branching 2.0（LW15）で GitHub 不要のブランチ運用が可能になり、本番ワークフロー組み込み難度が下がった
* 公式 robots.txt は `Allow: /` + AI 学習・検索を明示許可（教材化前提のクロールが堂々と可能）

---

## 5. 課題と対応

### 発生した課題
* （随時更新）

### 対応方法
* （随時更新）

### 未解決の課題
* （随時更新）

---

## 6. コストとリソース

### 人的リソース
* 田中省伍（PM 兼実装者）+ Claude Code サブエージェント

### 金銭的コスト
* Claude API 利用料（測定中）

### コスト対効果
* （完了時に記入）

---

## 7. 今後の展開

### 次のアクション
* HP（shogo-works）の dev server で全章のレンダリング目視確認
* `knowledge-transform` スキルで Note 記事へ二次展開（別タスクで起票）
* Linear SHO-179 を Done に変更
* 章間の内部リンクを Astro 規約に沿って張る（必要に応じて）
* SDK・CLI 章の Management API 部分を「要追記」のまま残してあるため、後日補完

### 横展開の可能性
* **Note 記事**：「Supabase 公式ドキュメントを全部読んだ結果まとめ」シリーズ
* **Udemy 教材**：byTech 入門・実務・採用判断の3コース
* **SNS 投稿**：Launch Week / Changelog ダイジェストを定期発信のネタに
* **byTech 講座カリキュラム**：第34章「安全に使える領域マップ」を採用判断モジュールとして組み込み

### 長期的な改善案
* Supabase はアップデート頻度が高いので、Launch Week / Changelog 章は四半期に一度の更新運用が必要
* HP のナレッジページに「最終確認日」表示を追加すると更新追跡しやすい
* 同じパターンで Vercel / Cloudflare Workers / Hono など他のウェブ開発スタックの教材も整備可能

---

📚 関連リソース

### 成果物・ドキュメント
* 実行計画 + Step Ledger: `~/.claude/plans/mcp-show-179-spa-inherited-puddle.md`
* 公開先（予定）: `shogo-works/repo/src/content/knowledge/web-development/supabase-docs/` （`.mdx`、Astro）
* 既存サンプル（frontmatter 参照用）: `shogo-works/repo/src/content/knowledge/web-development/gas-best-practices.mdx`
* ワークスペース（予定）: `knowledge-vault/vault/structured/projects/supabase-textbook-workspace/`

### 参考資料
* Supabase 公式ドキュメント: https://supabase.com/docs
* Supabase robots.txt: https://supabase.com/robots.txt（全クローラー許可確認済み）
* Supabase sitemap: https://supabase.com/sitemap.xml

### 関連プロジェクト
* `vault/structured/tools/20260502_supabase-medical-system-qa.md`（医療システム設計での Supabase 検討）
* `vault/structured/tools/20250830_amazon-q-kiro-db-design.md`（DB 設計関連）

---

✅ メモ・雑記
* （随時追記）

---

## 📝 更新ログ
<!-- このセクションはスキルが自動で追記する。手動編集不要。 -->
| 日時 | 更新内容の概要 |
|---|---|
| 2026/05/08 | ファイル作成（init）。計画策定・スコープ確定・Step Ledger 定義まで反映 |
| 2026/05/08 | 公開先を HP リポ（shogo-works Astro `src/content/knowledge/web-development/supabase-docs/`）に変更。Note 等への二次展開は別タスクへ後送り。ワークスペースを knowledge-vault 側に分離 |
| 2026/05/08 | Phase 0〜6 すべて実行。20章のmdx執筆完了、`astro check` 0 errors / 0 warnings。最終化（finalize） |
