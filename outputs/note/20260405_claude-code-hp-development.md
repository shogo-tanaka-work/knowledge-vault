# Claude Codeで個人HPを1日で作って公開した: 設計からデプロイまで全部AIに任せてみた結果

## TL;DR
- Claude Codeを使って、Astro製の個人HP（サービスページ追加〜Cloudflare Pagesデプロイ〜カスタムドメイン設定）を**約3時間で完了**した
- プランモードで設計 → イシュー駆動開発（5件） → TDD実装 → PR作成・マージ → デプロイまで、**開発の全工程をほぼClaude Codeだけで一気通貫**できた
- Lighthouseスコアは **Performance 100 / Accessibility 95 / Best Practices 100 / SEO 100**。ホスティング費用は月額0円

## なぜ試したのか

個人事業（shogoworks.com）のHPにサービス詳細ページがなく、提供内容や料金が伝わらないという課題がありました。同時に、自分自身が「AI駆動開発を実践している」という実績を作りたかった。そこで、Claude Codeが設計からデプロイまで本当に一気通貫で回せるのか、実際の本番プロジェクトで検証してみることにしました。

## やったこと

### 環境・前提
- **Claude Code**: Opus 4.6（1Mコンテキスト）
- **技術スタック**: Astro 6 + React Islands + TailwindCSS 4 + TypeScript
- **ホスティング**: Cloudflare Pages（Freeプラン）
- **ドメイン**: Squarespace Domains → Cloudflare DNSに移行
- **メール**: Google Workspace Business Standard（MXレコード移行が必要）

### 作業の流れ

1. **プランモードで設計**（約30分）
   - カテゴリ構成・料金・ターゲットをAskUserQuestionで3択提示しながら方針決定
   - Webサーチエージェントで市場相場を自動調査し、料金プランの根拠を取得

2. **イシュー駆動開発で実装**（約30分）
   - GitHub Issueを5件作成（型拡張 / ページ新設 / ナビ / リンク / アナリティクス）
   - 各Issueをブランチ → TDD実装（Red → Green → Refactor）→ PR → マージで処理
   - 1サイクル5〜10分で完了、5件合わせて約30分

3. **Cloudflare Pagesにデプロイ**（約75分）
   - Astroアダプタを`@astrojs/node`から`@astrojs/cloudflare`に切り替え
   - Cloudflare Pagesプロジェクト作成 → DNSレコード設定 → ネームサーバー切り替え → カスタムドメイン紐付け

## わかったこと

### 良かった点
- **プランモードの設計力が高い**: 選択肢をプレビュー付きで提示してくれるため、意思決定が速い。「AIコンサルティング」→「AI伴走支援」への名称変更なども対話の中でスムーズに決定できた
- **イシュー駆動開発がシームレス**: `gh issue create` → 実装 → `gh pr create` → `gh pr merge` が連続で実行され、Issue 1件あたり5〜10分でTDD実装〜マージまで完了する
- **DNS設定のガイドが正確**: Cloudflare UIでの手動操作が必要な部分も、ステップバイステップで的確に案内してくれた。スクリーンショットを共有しながら進められた
- **セキュリティ監査エージェントが優秀**: DNS設定時にsecurity-auditorが14項目の監査レポートを自動生成。MXレコード不足やDMARC未設定などの問題を事前に検出してくれた

### 気になった点
- **npmキャッシュの権限問題**: `sudo chown -R` が必要な場面が複数回発生。Claude Codeからはsudo実行できないため、手動介入が必要だった（セキュリティ的には正しい挙動）
- **GUI操作は案内止まり**: Cloudflare/Squarespace等のWebUIは直接操作できない。案内は正確だが、手動作業が残る
- **PageSpeed Insights APIのレート制限**: 429エラーで3回連続失敗。Lighthouse CLIもnpm権限問題で実行できず、最終的にChrome DevToolsで手動計測した

### 意外だった発見
- **Cloudflareの自動DNSスキャンはMXレコードを全て拾えない**: 5つ中1つしか検出されなかった。残り4つは手動追加が必要。自動スキャンを信用してはいけないという教訓を得た
- **security-auditorエージェントはコードレビューだけでなくDNS設定の監査にも使える**: 意外な汎用性があった
- **Astro 6 + @astrojs/cloudflare でLighthouse全項目90点以上が簡単に達成できる**: Astro Islandsパターン（ゼロJSデフォルト + 必要な箇所だけReact）の威力を実感

## 実際の使用例

### イシュー駆動開発の1サイクル

ServiceItem型の拡張とサービスデータ再定義（Issue #1）の場合：

```
1. git checkout -b feat/service-data-model
2. テスト作成（tests/data/services.test.ts）→ Red確認
3. 型拡張 + データ定義 → Green確認
4. npx astro check → 型エラー0件
5. git add → commit → push
6. gh pr create → gh pr merge --squash
```

結果: PR #6マージ完了、Issue #1自動クローズ。所要時間約10分。

### DNS移行時のセキュリティ監査

security-auditorエージェントが生成した14項目の監査レポートから、以下の問題を事前検出：
- **CRITICAL**: MXレコードが5つ中1つしか設定されていない → 手動で4つ追加
- **HIGH**: DMARCが未設定 → `p=quarantine`で追加
- **HIGH**: Resend DKIMの完全性確認が必要

これらをネームサーバー切り替え前に対処できたため、メール停止を回避できた。

## 数字で見る成果

| 項目 | 結果 |
|---|---|
| 全体所要時間 | 約3時間（手動なら推定2〜3日） |
| Issue処理速度 | 1件あたり5〜10分 |
| テスト | 13件全通過 |
| Lighthouse Performance | 100/100 |
| Lighthouse SEO | 100/100 |
| ビルド時間 | 約1.5秒 |
| ホスティング月額 | 0円 |

## 総合評価
⭐⭐⭐⭐⭐（5/5） — プランニングからデプロイまでの一気通貫ワークフローは現時点で唯一無二

### こんな人・用途に向いてる
- 個人事業主・フリーランスで自分のHPを素早く立ち上げたい人
- イシュー駆動開発やTDDのワークフローをAIで回してみたいエンジニア
- Cloudflare Pages + カスタムドメインの設定を初めてやる人（ガイドが正確なので安心）
- AI駆動開発の実践事例を自分のポートフォリオとして残したい人

### 向いていない場合
- GUI操作（Cloudflare管理画面など）を完全自動化したい場合 → Claude Codeからは操作できない
- npmの権限問題などOS権限が絡む操作が多い環境 → 手動介入が頻発する

## まとめ・次にやること

Claude Codeの最大の強みは、**設計（プランモード）→ 実装（TDD）→ デプロイ（gh CLI連携）の全工程を1つのセッションで完結できること**。1Mコンテキストのおかげで長時間のセッションでも文脈を失わず、DNS設定のような専門的な作業も安全にガイドしてくれました。

手動でやれば2〜3日かかる作業が3時間で終わり、しかもLighthouseスコアは全項目90点以上。ホスティング費用0円。AI駆動開発の実用性を実感した1日でした。

### 今後の予定
- お問い合わせフォームのHTMLエスケープ修正（XSSリスク対策）
- Resendのfromアドレスを本番用に変更
- CI/CDパイプライン（GitHub Actions）の動作確認
- Astro Content Collectionsを使ったブログ機能の追加

---
#AI #ClaudeCode #AI駆動開発 #Astro #CloudflarePages #個人HP #検証 #ナレッジ
