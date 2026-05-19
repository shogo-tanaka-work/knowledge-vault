# Vercel 公式ドキュメント全リサーチ → 自分用教材化 検証ログ

> ステータス: 完了
> 作成日: 2026/05/08
> 最終更新: 2026/05/08
> ファイルパス: /Users/shogo/Documents/AI事業OS/30_プロジェクト別/knowledge-vault/vault/structured/projects/20260508_vercel-textbook.md

---

📋 プロジェクト概要
* カテゴリ: ナレッジ蓄積 / フロントエンドプラットフォーム リサーチ / byTech 講座教材化
* 期間: 2026/05/08 - 2026/05/08
* 主要メンバー: 田中省伍
* ステークホルダー: byTech 受講生（将来の派生コンテンツ読者）
* プロジェクトステータス: 完了

---

## 1. 背景と目的

* Supabase（SHO-179）と同じ業務手順で Vercel を体系化する派生プロジェクト
* Vercel は AI Cloud としてのリブランディング以降、`v0` / `AI Gateway` / `AI SDK` / `MCP Servers` / `Sandbox` 等の AI インフラと、`WAF` / `Bot Management` / `BotID` / `Deployment Protection` / `RBAC` / `DDoS Mitigation` 等のセキュリティ機能が大幅に拡張されている
* Next.js 知識との重なりは把握しつつ、**Vercel プラットフォーム側の機能** に焦点を当てた日本語教材を整備する
* byTech 受講生が今後採用するケースが増える見込み。先回りして判断軸を整理し、HP に公開できる教材化を行う
* Linear: 未起票（必要なら別途）

---

## 2. 取り組み内容

### 実施した施策・活動
* 2026/05/08 計画策定。`~/.claude/plans/vercel-docs-textbook.md` に実行計画と Step Ledger（30 ステップ）を配置
* 2026/05/08 robots.txt 確認（`ai-input=yes / search=yes`、`ai-train=no`、教材化目的の参照は OK）
* 2026/05/08 ディレクトリ作成（公開先 `vercel-docs/` + ワークスペース `vercel-textbook-workspace/`）
* 2026/05/08 sitemap.xml 取得 → URL 一覧をカテゴリ別分類（採用 195 件 / 除外候補 30 件、22 章にマッピング）
* 2026/05/08 全 22 章執筆完了：00-index / 10-overview / コア 8 章 / セキュリティ 6 章 / AI 4 章 / 最新動向 2 章 / リファレンス 1 章 / 90-product-hints / 99-sources
* 2026/05/08 `npm run check` 実行：73 files / 0 errors / 0 warnings（追加分は問題なし、既存 zod 等 hint のみ）

### 使用したツール・技術
* WebFetch（主軸）
* Exa CLI（Changelog / Ship Week 横断要約用、限定的に使用）
* browser-use CLI（出番なし。WebFetch で完結）
* Claude Code サブエージェント（general-purpose、最大 5 並列バッチ）
* `ai-verification-log` スキル（本ログ管理）
* `knowledge-transform` スキル（後段の派生時に使用予定）

### 主要な意思決定とその理由
* スコープ：「コア機能フル + セキュリティ網羅 + AI インフラ網羅」のハイブリッドに決定
* 読み手・保存先・体裁は **Supabase 教材と同じ**（自分用 → 公開派生、shogo-works Astro リポ、frontmatter 必須最小、本文 6 セクションテンプレ）
* セッション運用：1 セッション = 1〜2 ステップ（コア章 3 並列バッチは 1 ステップ扱い）
* 完了時は `feat/vercel-docs-knowledge` ブランチを切って main 向け PR（Supabase と同パターン）
* セキュリティ章 30〜34 を 4 並列で投入後、35-safe-zones-map（統合）を self で執筆 → 結果として 5 並列で投入し統合章は別途 self 執筆

---

## 3. 進捗と成果

### 達成できたこと
* 計画策定完了（Step Ledger 30 ステップ定義）
* メモリポインタ登録完了
* `ai-verification-log init` 実行完了
* 全 22 章の `.mdx` 執筆完了
* `astro check` で構造的問題ゼロを確認

### 定量的な成果
* 全 22 章作成完了
* 総文字数：約 145,000 字超（章別平均 6,500 字）。最大は 23 章 ISR & Image Optimization の 12,500 字
* 一次ソース URL：195 件採用 / 30 件除外候補に分類
* `astro check` 結果：0 errors / 0 warnings
* セッション数：本セッション含む複数セッションに分割。3〜5 並列の general-purpose エージェントを多用しスループットを最大化

### 定性的な成果
* Supabase 教材と並ぶ「Web 開発スタック教材」の 2 本目を確立
* セキュリティ章とプラン依存マトリクスを「35-safe-zones-map」として独立章化し、本シリーズの中核に
* AI インフラ（v0 / AI Gateway / MCP / Sandbox / Agent）の境界を 4 章で整理し、Vercel の AI Cloud 戦略を読み解ける構造に
* 「Changelog ダイジェスト」を網羅ではなく 5 トピック軸で意味づけし、教材としての可読性を担保

---

## 4. 学びとナレッジ

### うまくいったこと（Good）
* general-purpose エージェント 3〜5 並列バッチによる執筆スループット（コア章 8 章を 3 セッション分の並列で消化）
* Step Ledger をセッション横断の唯一の進捗台帳として運用するパターン（再開時のロスゼロ）
* Supabase 教材と同形式の 6 セクションテンプレ踏襲により、章間の品質ばらつきを抑制
* WebFetch を主軸にした取得戦略（200 件超の URL を Exa 補助なしでほぼ完了）

### うまくいかなかったこと（Bad）
* Step 5-1 で初回 agent が「計画提示・承認待ち」で停止した。プロンプトに「即着手・確認不要・最後まで完遂」を明記して再投入で解決
* CVE-2026-23869 など一部の changelog URL が 404。一次ソース欄に明記する運用で対応
* sitemap.xml がフラット形式で約 1,000 URL あり、WebFetch のサンプリング上限により一部 canonical（`/docs/security` `/docs/cli` 等）はナビからの推定採用となった

### 改善ポイント（Improve）
* agent プロンプトのデフォルトに「即着手・確認不要・Write まで一気通貫」を含める
* sitemap が大量の場合は最初に `/docs` 配下のみフィルタリングしてからカテゴリ分類する
* 推定採用した URL は 99-sources で個別マークすると後段の追跡が楽になる

### 技術的な発見・Tips
* Supabase（`Allow: /` + AI 学習も明示許可）と異なり、Vercel は `ai-train=no`。**学習用途と参照用途を区別する** robots.txt の運用が一般化しつつある
* Vercel の AI Cloud リブランディングの正確な時期は公式に明示されていない。「2025 年前後」と表記
* Fluid Compute は 2025/4/23 から新規プロジェクトでデフォルト化（既存は手動切替）
* v0 は独立サブドメイン `v0.app/docs`（Vercel 配下に docs 無し）。AI Gateway は `/docs/ai-gateway/*` と `/ai-gateway` LP の二系統
* Sandbox は SDK Docs と REST API beta（v2）の二系統。Persistent Sandbox は別 changelog で beta 扱い
* Skew Protection は Turborepo 2.4.1 未満で常時 cache miss バグあり。教材で明記済み
* Marketplace 移行：旧 Vercel Postgres / KV は Neon / Upstash 系へ移管、自社継続は Blob と Edge Config のみ

---

## 5. 課題と対応

### 発生した課題
* Step 5-1 agent が承認待ちで停止
* 一部 URL（CVE-2026-23869 / `/docs/rest-api/errors`）が 404
* WebFetch サンプリング上限により一部 canonical URL が推定採用に

### 対応方法
* agent プロンプトに「即着手・確認不要」を明記して再投入
* 404 URL は本文では「詳細未確認」扱い、一次ソース欄に明記
* 推定採用 URL は 99-sources の注意点セクションに明記し、404 時は Documentation トップから再検索する運用を提示

### 未解決の課題
* 35-safe-zones-map のプラン依存表は 2026-05-08 時点の理解で記述。Vercel のプラン変更頻度を考えると四半期単位で見直しが必要
* 旧 Supabase 教材ディレクトリ（`supabase-docs/`）が現リポに見当たらない（コミット差分か、別リポ移管の可能性）。本タスクには無影響

---

## 6. コストとリソース

### 人的リソース
* 田中省伍（PM 兼実装者）+ Claude Code サブエージェント（general-purpose 多並列）

### 金銭的コスト
* Claude API 利用料（測定中、複数セッション × 並列エージェントのため Supabase 教材と同等以上を見込む）

### コスト対効果
* 22 章 / 145,000 字超の教材を数セッションで完成。手作業換算で数十時間相当のリサーチ・執筆を短縮
* byTech 講座教材として転用可能、Note / SNS / Udemy への横展開素材として再利用見込み

---

## 7. 今後の展開

### 次のアクション
* `feat/vercel-docs-knowledge` ブランチ作成 + main 向け PR（Supabase 教材と同パターン）— ユーザー確認後に実施
* 半年後に 35-safe-zones-map のプラン依存表を見直し
* `knowledge-transform` で Note / Udemy / SNS 派生

### 横展開の可能性
* `knowledge-transform` スキルで Note 記事 / Udemy 教材 / SNS 投稿へ展開
* byTech 講座カリキュラムへの組み込み（Supabase と並ぶ Web 開発スタックの 2 本柱）
* 「Vercel × Supabase で完結する Web スタック」統合教材

### 長期的な改善案
* Supabase 教材と相互参照させる（「Supabase + Vercel で完結する Web スタック」のような統合教材）
* AI Cloud 領域（AI Gateway / Sandbox / Agent）を切り出した独立教材化（変化が速い領域なので別ライフサイクル管理）

---

📚 関連リソース

### 成果物・ドキュメント
* 実行計画 + Step Ledger: `~/.claude/plans/vercel-docs-textbook.md`
* 公開先（作成済）: `shogo-works/repo/src/content/knowledge/web-development/vercel-docs/`（22 章 mdx）
* ワークスペース: `knowledge-vault/vault/structured/projects/vercel-textbook-workspace/00_url_inventory.md`

### 参考資料
* Vercel 公式ドキュメント: https://vercel.com/docs
* Vercel robots.txt: https://vercel.com/robots.txt（`ai-input=yes / search=yes / ai-train=no` 確認済み）
* Vercel sitemap: https://vercel.com/sitemap.xml
* Vercel Changelog: https://vercel.com/changelog
* Vercel Trust Center: https://vercel.com/security

### 関連プロジェクト
* `vault/structured/projects/20260508_supabase-textbook.md`（同パターンの先行プロジェクト・完了済）

---

✅ メモ・雑記
* 並列実行のスループットが今回最大の収穫。Supabase 教材は逐次処理だったが、本 PJ は 3〜5 並列で短縮効果が顕著
* 「セキュリティ章で個別にプラン依存を書く」「最後に統合マトリクスを self で書く」の二段構成は再現性が高い
* AI Cloud 領域（v0 / AI Gateway / MCP / Sandbox / Agent）は変化が速く、本シリーズも半年〜1 年単位で見直し前提

---

## 📝 更新ログ
<!-- このセクションはスキルが自動で追記する。手動編集不要。 -->
| 日時 | 更新内容の概要 |
|---|---|
| 2026/05/08 | ファイル作成（init）。計画策定・スコープ確定・Step Ledger 30 ステップ定義まで反映 |
| 2026/05/08 | 最終化（finalize）。全 22 章執筆完了 / astro check 0 errors / 残作業は git ブランチ + PR のみ |
