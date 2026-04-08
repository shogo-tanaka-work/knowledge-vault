# Claude Code × Astro HP制作ワークフロー 検証ログ

> ステータス: 完了
> 作成日: 2026/04/05
> 最終更新: 2026/04/05（手順書追記）
> ファイルパス: /Volumes/PortableSSD/Documents/knowledge-vault/structured/tools/20260405_claude-code-hp-development.md

---

## 📋 検証概要

- **ツール/サービス名**: Claude Code（Anthropic CLI） + GitHub CLI + Cloudflare Pages
- **検証対象**: Claude Codeを活用したHP制作〜公開の一気通貫ワークフロー
- **バージョン/リリース日**: Claude Opus 4.6（1Mコンテキスト）
- **検証期間**: 2026/04/05 - 2026/04/05（1日で完結）
- **検証担当者**: 田中省伍
- **検証ステータス**: 完了

---

## 1. 背景と検証目的

### なぜこの検証を行うのか
- Claude Codeが「プランニング → イシュー作成 → TDD実装 → PR作成・マージ → デプロイ → DNS設定」という開発の全工程をどこまで一気通貫で担えるかを実証する
- 非エンジニア・ジュニアエンジニア向けサービスの説得力として「自分自身がAI駆動開発を実践している」実績を作る

### 解決したい課題
- 個人HPにサービス詳細ページがなく、提供サービスの内容・料金が伝わらない
- Cloudflare Pagesへのデプロイとカスタムドメイン設定の知見を蓄積したい
- イシュー駆動開発のワークフローをClaude Codeで回せるか確認したい

### 期待される効果・ビジネスインパクト
- shogoworks.comとして本番公開し、サービス案内・集客の基盤を構築
- AI駆動開発の実践事例として、自身のサービス提供時の説得材料になる

---

## 2. ツール/機能の基本情報

### 概要
Claude Code（Anthropic公式CLI）を中心に、GitHub CLI（gh）、Cloudflare Pages を組み合わせた開発ワークフロー。プランモードで設計→イシュー作成→TDDで実装→PR作成・マージ→デプロイまでを1セッションで実行。

### 提供元
- **Claude Code**: Anthropic（Claude Opus 4.6, 1Mコンテキスト）
- **GitHub CLI**: GitHub（gh コマンド）
- **Cloudflare Pages**: Cloudflare（Free プラン）

### 主要機能
- **プランモード**: 実装前にプランファイルを作成し、ユーザーと方針をすり合わせる
- **イシュー駆動開発**: gh issue create でGitHubイシューを自動作成
- **TDD実装**: テスト先行（Red → Green → Refactor）でコード実装
- **PR自動化**: gh pr create → gh pr merge でPRの作成・マージを自動実行
- **セキュリティ監査**: security-auditorエージェントによるDNS設定のレビュー

### 技術スタック・アーキテクチャ
- Astro 6 + React Islands + TailwindCSS 4
- TypeScript 5.x / Zod（バリデーション）
- @astrojs/cloudflare アダプタ
- Vitest（テストフレームワーク）
- Cloudflare Pages（ホスティング）
- Squarespace Domains → Cloudflare DNS（ネームサーバー移行）

---

## 3. 検証方法

### 検証環境
- **使用アカウント**: shogo-tanaka-work（GitHub）/ S-tanaka@shogoworks.com（Cloudflare）
- **プラン/エディション**: Claude Code（Opus 4.6）/ GitHub Free / Cloudflare Free
- **検証環境**: 本番（shogoworks.com に直接デプロイ）

### 検証シナリオ
1. プランモードでサービスページ追加の設計（カテゴリ構成・料金・ターゲット定義）
2. Webサーチで市場相場を調査し、料金プランを策定
3. GitHubリポジトリ（shogo-works）に初期コードをコピー・コミット
4. GitHub Issueを5件作成（イシューテンプレート活用）
5. Issue #1〜#5を順にブランチ→TDD実装→PR→マージで処理
6. Cloudflareアダプタに切り替え→Cloudflare Pagesデプロイ
7. DNS設定（MX/DKIM/SPF/DMARC）→ネームサーバー切り替え→カスタムドメイン設定
8. Lighthouse評価で品質確認

### 検証データ・サンプル
- リポジトリ: https://github.com/shogo-tanaka-work/shogo-works
- 本番URL: https://shogoworks.com

### 前提条件・制約事項
- Google Workspace Business Standardでメール利用中（MXレコード移行が必要）
- ドメインはGoogle Domains購入→Squarespace Domainsに自動移行済み
- npmキャッシュの権限問題（sudo chown -R が必要だった）が複数回発生

---

## 4. 検証結果

### 定性的評価

#### 機能面の評価
- **プランモード**: AskUserQuestionで3つの選択肢（カテゴリ構成・ページ構成・サービス名表現）を同時に提示し、効率的に方針決定できた。Webサーチエージェントで市場相場を自動調査し、料金プランの根拠を提供
- **イシュー駆動開発**: gh issue create / gh pr create / gh pr merge を連続実行し、Issue作成→実装→PR→マージの1サイクルが5〜10分で完了。5件のIssueを約30分で全て処理
- **TDD**: テスト先行でRed→Green→Refactorを厳密に実行。vitest パスエイリアスの設定やtsconfig.jsonのexclude修正など、テスト基盤の整備も自動で対応
- **セキュリティ監査**: DNS設定時にsecurity-auditorエージェントが14項目の監査レポートを生成。MXレコード不足（5つ中1つしかなかった）、DMARC未設定、SPFの重複リスクなどを検出

#### 操作性・UI/UX
- プランモードのプレビュー付き選択肢（AskUserQuestion）が直感的で、設計の意思決定が速い
- ただしnpmキャッシュ権限問題でsudo実行が必要な場面があり、Claude Codeからは実行できず手動対応が必要だった（セキュリティ的には正しい挙動）

#### 出力品質
- Lighthouse スコア: Performance 100 / Accessibility 95 / Best Practices 100 / SEO 100
- Astro Islands パターンに従った設計で、ゼロJSのデフォルト + React Islands（インタラクション部分のみ）
- レスポンシブ対応、スクロールアニメーション、ホバーエフェクト等も適切に実装

#### 実用性
- 1日（約3時間）で「サービスページ追加 + アナリティクス導入 + Cloudflare Pagesデプロイ + カスタムドメイン設定」を完了。手動でやれば2〜3日はかかる作業量
- DNS設定はCloudflare UIでの手動作業が多く、Claude Codeが直接操作できない領域。ただしステップバイステップの案内が正確で、スクリーンショートを共有しながら進められた

---

### 定量的評価

#### 導入コスト

| 項目 | 内容 | 金額/工数 |
| --- | --- | --- |
| 初期設定時間 | リポジトリ作成〜初期コミット | 約15分 |
| Issue作成〜全実装完了 | 5件のIssue（型拡張/ページ新設/ナビ/リンク/アナリティクス） | 約30分 |
| Cloudflareデプロイ+DNS設定 | アダプタ切替〜カスタムドメイン設定完了 | 約60分 |
| 全体所要時間 | プランニング開始〜本番公開 | 約3時間 |

#### 運用コスト

| 項目 | 内容 | 金額 |
| --- | --- | --- |
| Cloudflare Pages | Free プラン | 0円/月 |
| カスタムドメイン | Squarespace Domains（Google Workspace付帯） | Google Workspace料金に含む |
| GA4 + Microsoft Clarity | 無料 | 0円/月 |
| Claude Code | Opus 4.6 利用料（APIベース） | セッション分 |

#### パフォーマンス

| 項目 | 測定結果 | 備考 |
| --- | --- | --- |
| Lighthouse Performance | 100/100 | モバイル計測 |
| Lighthouse Accessibility | 95/100 | モバイル計測 |
| Lighthouse Best Practices | 100/100 | モバイル計測 |
| Lighthouse SEO | 100/100 | モバイル計測 |
| ビルド時間 | 約1.5秒 | astro build |
| テスト実行時間 | 約7秒（13テスト） | vitest run |

#### ROI試算
- **削減できる工数**: 手動開発比で約60〜70%削減（3時間 vs 推定2〜3日）
- **生産性向上**: イシュー1件あたり5〜10分でTDD実装〜PRマージ完了
- **コスト削減額**: ホスティング費用0円（Cloudflare Pages Free）
- **投資回収期間**: 即時（初期費用なし）

---

## 5. 比較・優位性分析

### 既存ツール/類似サービスとの比較

| 項目 | Claude Code | Cursor | GitHub Copilot |
| --- | --- | --- | --- |
| プランモード | ✅ 専用モードあり | ❌ なし | ❌ なし |
| イシュー作成自動化 | ✅ gh CLI連携 | ❌ 手動 | ❌ 手動 |
| PR作成・マージ | ✅ gh CLI連携 | ❌ 手動 | ✅ Copilot Workspace（限定） |
| TDD支援 | ✅ Red→Green→Refactor | △ 部分的 | △ 部分的 |
| DNS設定ガイド | ✅ スクショベースで案内 | ❌ 対象外 | ❌ 対象外 |
| セキュリティ監査 | ✅ エージェント内蔵 | ❌ なし | ❌ なし |
| コンテキスト窓 | 1Mトークン | 制限あり | 制限あり |

### 優位性
- プランモード→実装→PR→マージの一気通貫フローが他ツールにない
- 1Mコンテキストにより、長時間セッションでも文脈を失わない
- security-auditorやExploreなどの専門エージェントを並列起動できる
- gh CLI統合でGitHub操作がシームレス

### 劣位性・懸念点
- npmキャッシュ権限問題など、OS権限が絡む操作は手動介入が必要
- Cloudflare/Squarespace等のGUI操作はClaude Codeから直接実行できない（スクリーンショートベースの案内にとどまる）
- PageSpeed Insights APIのレート制限にかかり、Lighthouse CLIもnpm権限問題で実行できなかった

---

## 6. リスク評価

### セキュリティ

| 評価項目 | 評価 | 詳細 |
| --- | --- | --- |
| データ保管場所 | ✅ | コードはGitHub、ホスティングはCloudflare。どちらもSOC2準拠 |
| 暗号化 | ✅ | SSL/TLS自動発行（Cloudflare）、HTTPS強制 |
| アクセス制御 | ✅ | GitHub Private可、Cloudflare Access設定可 |
| ログ管理 | ✅ | GA4 + Microsoft Clarity でユーザー行動を記録 |
| コンプライアンス | ✅ | プライバシーポリシー・利用規約ページ設置済み |

### DNS移行時のリスク（実際に発生した問題）
- **MXレコード不足**: Cloudflareの自動スキャンで5つ中1つしか検出されず。手動で4つ追加が必要だった。security-auditorエージェントが検出してくれた
- **DMARC未設定**: なりすまし対策なしの状態だった。`p=quarantine` で追加
- **Squarespace向けレコード残存**: Aレコード（198.49.23.144）とCNAME（www → squarespace）がPages設定時に競合。削除してから再設定で解決

### 技術的リスク
- お問い合わせフォームの `from` が `onboarding@resend.dev`（Resendデモ用）のまま。本番では要変更
- HTMLメール本文にユーザー入力をエスケープなしで埋め込んでいる（XSSリスク）。要修正

---

## 7. 連携性・拡張性

### 既存システムとの連携

| 連携先 | 方法 | 難易度 | 備考 |
| --- | --- | --- | --- |
| GitHub | gh CLI（issue/pr/label操作） | 低 | シームレスに動作 |
| Cloudflare Pages | GitHub連携（mainブランチ自動デプロイ） | 低 | 初回設定のみUI操作 |
| Google Analytics 4 | 環境変数でID管理、Head.astroに埋め込み | 低 | PUBLIC_GA4_ID |
| Microsoft Clarity | 同上 | 低 | PUBLIC_CLARITY_ID |
| Resend（メール送信） | API経由、環境変数でキー管理 | 低 | RESEND_API_KEY |
| Google Workspace | MXレコード設定でメール継続 | 中 | DNS移行時に要注意 |

### API/統合オプション
- Cloudflare Workers連携でサーバーサイド処理を拡張可能
- Astro SSRモード（@astrojs/cloudflare）でAPIエンドポイント追加可能

### 拡張性・カスタマイズ性
- Astro Islands パターンにより、必要な箇所だけReact化可能
- src/data/ のTypeScriptデータファイルでコンテンツ管理（CMSなしでも運用可能）

---

## 8. 実際の使用例・サンプル

### ユースケース1: イシュー駆動開発の1サイクル

**シナリオ**: ServiceItem型の拡張とサービスデータ再定義（Issue #1）

**入力**: プランファイルに基づいた実装指示

**実行フロー**:
```
1. git checkout -b feat/service-data-model
2. テスト作成（tests/data/services.test.ts）→ Red確認
3. 型拡張（src/types/index.ts）+ データ定義（src/data/services.ts）→ Green確認
4. npx astro check → 型エラー0件
5. git add → git commit → git push
6. gh pr create → gh pr merge --squash
7. git checkout main → git pull
```

**出力**: PR #6 マージ完了、Issue #1 自動クローズ

**評価**: 1サイクル約10分。テスト8件全通過、型エラー0件

### ユースケース2: DNS設定のセキュリティ監査

**シナリオ**: Cloudflare DNS設定の安全性を確認

**入力**: スクリーンショートで現在のDNSレコード一覧を共有

**実行フロー**:
```
1. security-auditorエージェントを起動
2. 14項目の監査レポートを生成
3. CRITICAL: MXレコード不足を検出
4. HIGH: DMARC未設定を検出
5. HIGH: Resend DKIMの完全性確認を推奨
6. MEDIUM: HTMLエスケープ未実装を指摘
```

**出力**: 優先度付き14項目の監査レポート + 実装チェックリスト

**評価**: DNS移行の安全性が大幅に向上。MXレコード不足を事前に検出できたのは大きい

### ユースケース3: Astro × Cloudflare Pages デプロイ 完全手順書

個人事業主・フリーランスがAstroサイトをCloudflare Pagesで公開し、Google Workspaceで取得済みのカスタムドメインを紐付けるまでの全手順。Squarespace Domains（旧Google Domains）でドメイン管理している前提。

---

#### Phase 1: Astroアダプタの切り替え（コード変更）

**前提**: Astro プロジェクトが `@astrojs/node` アダプタで動作している状態

**Step 1-1**: パッケージの入れ替え
```bash
npm uninstall @astrojs/node
npm install @astrojs/cloudflare
```

**Step 1-2**: `astro.config.ts` を編集
```typescript
// Before
import node from "@astrojs/node";
export default defineConfig({
  adapter: node({ mode: "standalone" }),
  // ...
});

// After
import cloudflare from "@astrojs/cloudflare";
export default defineConfig({
  adapter: cloudflare(),
  // ...
});
```

**Step 1-3**: ビルド確認
```bash
npx astro build
```
→ `dist/` にCloudflare Pages用のビルド成果物が生成されること。
→ SSR対応のAPIルート（例: `/api/contact`）も含まれること。

**Step 1-4**: コミット・push
```bash
git add astro.config.ts package.json package-lock.json
git commit -m "feat: アダプタを@astrojs/cloudflareに切り替え"
git push origin main
```

**⚠️ ハマりポイント**: npmキャッシュにroot所有ファイルが混在していると `npm install` が失敗する。`sudo chown -R $(whoami) ~/.npm` で解決。

---

#### Phase 2: Cloudflare Pages プロジェクト作成（GUI操作）

**Step 2-1**: Cloudflare ダッシュボードにログイン
- https://dash.cloudflare.com にアクセス

**Step 2-2**: プロジェクト作成
1. 左メニュー「Workers & Pages」をクリック
2. 「Create」ボタン → 「Pages」タブ → 「Connect to Git」
3. GitHub を選択 → アカウント連携（初回のみOAuth認証）
4. リポジトリ一覧から対象リポジトリを選択
5. 「Begin setup」をクリック

**Step 2-3**: ビルド設定
| 設定項目 | 値 |
|---------|-----|
| Project name | `shogo-works`（= URLの `shogo-works.pages.dev` 部分） |
| Production branch | `main` |
| Framework preset | `Astro`（自動検出される） |
| Build command | `npm run build` |
| Build output directory | `dist` |

**Step 2-4**: 環境変数の設定
同じ画面の「Environment variables (advanced)」を展開して追加：

| 変数名 | 用途 | 必須 |
|--------|------|------|
| `RESEND_API_KEY` | お問い合わせフォームのメール送信 | はい |
| `CONTACT_TO_EMAIL` | お問い合わせの送信先アドレス | はい |
| `PUBLIC_GA4_ID` | Google Analytics 4 測定ID | いいえ（後から追加可） |
| `PUBLIC_CLARITY_ID` | Microsoft Clarity プロジェクトID | いいえ（後から追加可） |

**Step 2-5**: デプロイ実行
「Save and Deploy」をクリック → 初回ビルド+デプロイが開始（2〜3分）。

**✅ 確認**: `https://[project-name].pages.dev` でサイトが表示されること。
今回の場合: `https://shogo-works.s-tanaka-dcb.workers.dev`

**💡 ポイント**: この時点で `main` ブランチへのpushで自動デプロイが有効になっている。以降のコード変更はmainにマージするだけで本番に自動反映される。

---

#### Phase 3: Cloudflare にドメインを追加（DNS管理の移行準備）

ここからが最も複雑で慎重さが求められるフェーズ。Google Workspace（メール）を壊さないことが最優先。

**Step 3-1**: ドメイン追加
1. Cloudflare ダッシュボード左上「Add a domain」
2. `shogoworks.com` を入力 → 「Continue」
3. プラン「Free」を選択 → 「Continue」

**Step 3-2**: DNS レコードの自動スキャン確認
Cloudflareが既存DNSレコードを自動スキャンする。**ここが最大の注意ポイント**。

スキャン結果に以下が含まれるか確認する：

**■ メール関連（Google Workspace） — 最重要**

MXレコード（メール受信に必須、5つ全て必要）:

| Type | Name | Content | Priority |
|------|------|---------|----------|
| MX | @ | ASPMX.L.GOOGLE.COM | 1 |
| MX | @ | ALT1.ASPMX.L.GOOGLE.COM | 5 |
| MX | @ | ALT2.ASPMX.L.GOOGLE.COM | 5 |
| MX | @ | ALT3.ASPMX.L.GOOGLE.COM | 10 |
| MX | @ | ALT4.ASPMX.L.GOOGLE.COM | 10 |

**⚠️ 実際に起きた問題**: 自動スキャンで5つ中1つしか検出されなかった。残り4つは手動で「+ Add record」から追加が必要だった。**自動スキャンを信用してはいけない。**

SPFレコード（メール送信元認証）:

| Type | Name | Content |
|------|------|---------|
| TXT | @ | `v=spf1 include:_spf.google.com ~all` |

DKIMレコード（メール署名検証）:

| Type | Name | Content |
|------|------|---------|
| TXT | google._domainkey | `v=DKIM1; k=rsa;...`（Google Workspace管理画面で確認） |

**■ Resend/SES関連（お問い合わせフォーム用）**

| Type | Name | Content |
|------|------|---------|
| MX | send | `feedback-smtp.[region].amazonses.com` (優先度10) |
| TXT | resend._domainkey | `p=MIGfMA0GC...`（Resend管理画面で確認） |
| TXT | send | `v=spf1 include:amazonses.com ~all` |

**■ Squarespace向け（後で削除するがこの時点では残す）**

| Type | Name | Content | 備考 |
|------|------|---------|------|
| A | @ | 198.49.23.144 | Squarespace IP → 後でPages用に置換 |
| CNAME | www | ext-sq.squarespace.com | 同上 |

**■ 削除してよいレコード**

| Type | Name | 理由 |
|------|------|------|
| CNAME | _domainconnect | Squarespace自動設定用。不要 |

**Step 3-3**: DMARC レコードの追加（なりすまし対策）
自動スキャンでは検出されないので手動追加：

| Type | Name | Content |
|------|------|---------|
| TXT | _dmarc | `v=DMARC1; p=quarantine; rua=mailto:dmarc@shogoworks.com` |

初期運用では `p=none`（監視のみ）でも可。段階的に `quarantine` → `reject` に強化する。

**Step 3-4**: セキュリティ監査（推奨）
ネームサーバー切り替え前に、全レコードの整合性を確認する。確認観点：

1. MXレコードが5つ全て揃っているか（表示が切れている場合はクリックしてフル値を確認）
2. SPFレコードがルートドメインに1つだけか（複数あるとエラー）
3. DKIMの値がGoogle Workspace管理画面と一致するか
4. Resend管理画面のDNS Records が全て「Verified」か
5. DMARCが追加されているか

**✅ 全レコード確認後**、「Continue to activation」をクリック。

---

#### Phase 4: ネームサーバーの切り替え

**Step 4-1**: Cloudflareが指定するネームサーバーを確認
画面に2つのネームサーバーが表示される（例）：
```
hayes.ns.cloudflare.com
zara.ns.cloudflare.com
```

同時に、削除すべき既存ネームサーバーも表示される（例）：
```
❌ ns-cloud-b1.googledomains.com
❌ ns-cloud-b2.googledomains.com
❌ ns-cloud-b3.googledomains.com
❌ ns-cloud-b4.googledomains.com
```

**Step 4-2**: Squarespace Domains で切り替え
1. https://account.squarespace.com/domains/managed/[ドメイン名]/dns/domain-nameserver にアクセス
2. 「ドメイン ネームサーバー」画面で既存の `ns-cloud-*.googledomains.com` が表示される
3. **右上の「カスタム ネームサーバーを使用」ボタンをクリック**
4. Cloudflareの2つのネームサーバーを入力して保存

**⚠️ ハマりポイント**: Squarespace Domainsの画面には既存ネームサーバーの「削除ボタン」がない。「カスタム ネームサーバーを使用」ボタンをクリックすると入力フォームに切り替わり、そこで新しいネームサーバーを入力する仕組み。直感的ではないので注意。

**Step 4-3**: DNSSECの確認
Squarespace Domains の左メニュー「DNSSEC」を確認。ONになっていたらOFFにする（Cloudflare移行後にCloudflare側で再有効化可能）。

**Step 4-4**: Cloudflareで反映確認
1. Cloudflareの画面に戻り「I updated my nameservers」をクリック
2. ダッシュボード → shogoworks.com → 「Overview」を開く
3. ステータスが「Pending Nameserver Update」→「Active」に変わるのを待つ
4. 「Check nameservers」ボタンで手動再チェック可能
5. 通常は数分〜数十分で反映（最大48時間）

**✅ 確認**: 「Your domain is now protected by Cloudflare」と表示されればOK。

---

#### Phase 5: Cloudflare Pages にカスタムドメインを紐付け

**Step 5-1**: Squarespace向けレコードの削除
DNS設定画面で以下を削除：

| 削除対象 | 理由 |
|---------|------|
| A: `shogoworks.com → 198.49.23.144` | Squarespace IP。Pagesに置換するため |
| CNAME: `www → ext-sq.squarespace.com` | 同上 |

**⚠️ ハマりポイント**: この削除をせずにカスタムドメインを追加しようとすると「ドメインは既に使われています」エラーが出る。

**Step 5-2**: カスタムドメインの追加
1. 「Workers & Pages」→ プロジェクト選択 → 「Settings」タブ
2. 「Domains & Routes」セクションの「+ Add」をクリック
3. `shogoworks.com` を入力 → 追加
4. Cloudflareが自動的にDNSレコード（CNAME）を作成

**Step 5-3**: SSL証明書の自動発行
カスタムドメイン追加後、Cloudflareが自動でSSL証明書を発行（数分）。

**Step 5-4**: 動作確認
```
https://shogoworks.com → サイトが表示されること
https://shogoworks.com/services → サービスページが表示されること
```

**💡 オプション**: `www.shogoworks.com` も同様に「+ Add」から追加可能。必須ではない（www なしが主流）。

---

#### Phase 6: デプロイ後の確認

**Step 6-1**: 自動デプロイの動作確認
Cloudflare PagesはGitHub連携で `main` ブランチへのpush時に自動ビルド・デプロイを実行する。
確認方法: コードを修正 → mainにマージ → 数分後にサイトに反映されていること。

**Step 6-2**: メール送受信テスト
ネームサーバー切り替え後、Google Workspaceのメールが正常に動作するか確認：
- 外部メール（Gmail等）から `@shogoworks.com` にメール送信 → 受信できること
- `@shogoworks.com` から外部にメール送信 → 相手に届くこと

**Step 6-3**: Lighthouse 計測
Chrome DevTools → Lighthouseタブ → 「Analyze page load」で品質確認。
今回の結果: Performance 100 / Accessibility 95 / Best Practices 100 / SEO 100

**Step 6-4**: Google MX Toolbox で DNS 検証（推奨）
https://toolbox.googleapps.com/apps/checkmx/ に `shogoworks.com` を入力し、MX/SPF/DKIM の設定が正しいか一括確認。

---

#### 全体のタイムライン（実績）

| 時刻 | 作業内容 | 所要時間 |
|------|---------|---------|
| 19:00 | Phase 1: アダプタ切り替え | 5分 |
| 19:10 | Phase 2: Cloudflare Pages プロジェクト作成 | 10分 |
| 20:50 | Phase 3: DNS レコード確認・MX追加・DMARC追加 | 30分 |
| 21:30 | Phase 4: ネームサーバー切り替え | 10分 |
| 21:37 | Active 確認 | 3分（反映が速かった） |
| 21:39 | Phase 5: カスタムドメイン紐付け | 5分 |
| 21:41 | Phase 6: 動作確認・Lighthouse計測 | 10分 |
| **合計** | | **約75分** |

---

#### 今回の構成での月額ランニングコスト

| サービス | プラン | 月額 |
|---------|--------|------|
| Cloudflare Pages | Free | 0円 |
| Cloudflare DNS | Free（ドメイン追加） | 0円 |
| カスタムドメイン | Squarespace Domains（GWS付帯） | GWS料金に含む |
| SSL証明書 | Cloudflare自動発行 | 0円 |
| GA4 + Clarity | 無料 | 0円 |
| **合計（ホスティング部分）** | | **0円** |

---

## 9. 学びとナレッジ

### 発見したこと
- Claude Codeのプランモードは「設計 → 確認 → 実装」の流れを強制するため、手戻りが少ない
- security-auditorエージェントはDNS設定の監査にも使える（コードレビューだけでなく）
- Cloudflareの自動DNSスキャンはMXレコードを全て拾えないことがある（5つ中1つだけ検出）
- Astro 6 + @astrojs/cloudflare の組み合わせでLighthouse全項目90点以上が容易に達成できる

### うまくいったこと
- 1日で「設計 → 5件のIssue実装 → デプロイ → カスタムドメイン設定」を完了
- TDDの徹底（テスト13件全通過）
- プランモードでの料金設定（Webサーチで市場相場を調査 → モニター価格で差別化）
- スクリーンショートベースのDNS設定ガイドが正確だった

### うまくいかなかったこと
- **npmキャッシュ権限問題**: `sudo chown -R` が必要で、Claude Codeからは実行できず。複数回発生し、ユーザーの手動介入が必要だった
- **PageSpeed Insights API**: レート制限（429）で3回連続失敗。Lighthouse CLIもnpm権限問題で実行不可。最終的にChrome DevToolsで手動計測
- **Squarespace Domainsの操作**: ネームサーバー変更画面に「削除ボタン」がなく、「カスタムネームサーバーを使用」ボタンで切り替える仕様だった。UIの直感性に欠ける

### Tips・ベストプラクティス
- **DNS移行前にCloudflare側のレコードを完璧にしてからネームサーバーを切り替える**。切り替え後にレコード不足が判明するとメールが止まる
- **MXレコードは必ず手動で全5つ確認する**。自動スキャンを信用しない
- **DMARCは初期は `p=none`（監視のみ）で始め、問題なければ段階的に `p=quarantine` → `p=reject` に強化**
- **vitest でAstroプロジェクトのテストを書く場合、`vitest.config.ts` に `@` エイリアスを設定し、`tsconfig.json` の `exclude` に `vitest.config.ts` を追加する**（astro checkが型エラーを出すため）
- **Cloudflare PagesにカスタムドメインをAddする前に、既存のA/CNAMEレコードを削除する**。残っていると「ドメインは既に使われています」エラーが出る

### よくあるエラーと対処法

| エラー | 原因 | 対処法 |
|---|---|---|
| `npm error EACCES: permission denied` | npmキャッシュにroot所有ファイルが混在 | `sudo chown -R $(whoami) ~/.npm` |
| `Cannot find name '__dirname'` | vitest.config.tsをastro checkが型チェック対象にする | tsconfig.jsonのexcludeに`vitest.config.ts`を追加 |
| `Cannot find module 'node:path'` | 同上 | `fileURLToPath(new URL("./src", import.meta.url))` を使う |
| Cloudflare Pages「ドメインは既に使われています」 | 既存のA/CNAMEレコードが残っている | DNS設定で既存レコードを削除してからAdd |
| PageSpeed Insights API 429 | レート制限 | Chrome DevToolsのLighthouseタブで手動計測 |

---

## 10. 判定と今後のアクション

### 総合評価
⭐️⭐️⭐️⭐️⭐️（5/5）

### 導入判定
- [x] 即座に導入推奨
- [ ] 条件付きで導入可
- [ ] 追加検証が必要
- [ ] 導入見送り

### 判定理由
- 1日で設計〜本番公開を完了できるスピード感は圧倒的
- イシュー駆動開発 + TDDのワークフローがClaude Code上で完結する
- DNS設定のような専門知識が必要な領域でも、エージェント（security-auditor）が安全性を担保してくれる
- Lighthouse全項目90点以上は、手動開発でもなかなか達成できないレベル
- ホスティング費用0円で本番運用可能

### 次のステップ
- [x] 検証終了
- [ ] HTMLエスケープ修正（お問い合わせフォームのXSSリスク対策）
- [ ] Resendのfromアドレスを `onboarding@resend.dev` から本番用に変更
- [ ] FDE的サービスの詳細追加（Issue #6）
- [ ] CI/CD パイプライン（GitHub Actions）の動作確認
- [ ] www.shogoworks.com のリダイレクト設定（必要に応じて）

### 追加で検証したい項目
- Cloudflare Workers との連携（エッジでの動的処理）
- Astro Content Collections を使ったブログ機能の追加
- Cloudflare Web Analytics（GA4の代替としてプライバシー重視の選択肢）

---

📚 関連リソース

### 公式ドキュメント
- [Astro Cloudflare Adapter](https://docs.astro.build/en/guides/integrations-guide/cloudflare/)
- [Cloudflare Pages](https://developers.cloudflare.com/pages/)
- [Google Workspace MX Records](https://support.google.com/a/answer/174125)
- [Microsoft Clarity](https://clarity.microsoft.com/)

### 参考記事・事例
- Cloudflare DNS + Google Workspace 共存設定
- Squarespace Domains → Cloudflare ネームサーバー移行手順

### 検証データ・ログ
- リポジトリ: https://github.com/shogo-tanaka-work/shogo-works
- 本番URL: https://shogoworks.com
- PR一覧: #6（型拡張）/ #7（ページ新設）/ #8（ナビ）/ #9（リンク）/ #10（アナリティクス）/ #11（CFアダプタ）

---

✅ メモ・議論ログ
- サービス名「AI活用コンサルティング」→ ユーザーが「コンサル」嫌いとのことで「AI伴走支援」に変更
- 料金はWebサーチで市場相場調査後、定価+モニター価格（2〜3割引）の2段構成に
- DNS移行でsecurity-auditorが14項目の監査レポートを生成。MXレコード不足・DMARC未設定を事前検出
- Squarespace DomainsのUIで「削除ボタンがない」問題 → 「カスタムネームサーバーを使用」で切替

---

## 📝 更新ログ
<!-- このセクションはスキルが自動で追記する。手動編集不要。 -->
| 日時 | 更新内容の概要 |
|---|---|
| 2026/04/05 | ファイル作成（init） — 全セクション記入済みで作成 |
| 2026/04/05 | 最終化（finalize） — 検証完了 |
| 2026/04/05 | ユースケース3追記 — Cloudflare Pages デプロイ完全手順書（Phase 1〜6、ハマりポイント、タイムライン含む） |
