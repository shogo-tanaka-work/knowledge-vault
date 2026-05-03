# Pages

## 一行サマリ
Cloudflare Pages は、Git 連携または Direct Upload で静的アセットを Cloudflare のグローバルネットワークに即時配信し、Pages Functions により Workers ランタイムでサーバサイド処理も実行できるフルスタック JAMstack ホスティングである。

## 解決する課題（Why）
従来の静的サイトホスティングは「CDN 配信は速いが、API・認証・SSR を組み込もうとすると別サービス（Lambda、API Gateway）が必要で構成が分散する」という問題を抱える。Pages は静的アセット配信と Workers ベースのサーバ処理を 1 プロジェクトに統合し、Git push から本番デプロイ・プレビューデプロイ・ロールバックまでを単一パイプラインで完結させる。Edge ネットワーク上に配置されるためオリジンレイテンシが消え、無料枠でも商用レベルの帯域・リクエスト数を扱える。

## 主要機能（What）
- **Git 連携 / Direct Upload / C3 CLI**：GitHub・GitLab 接続による自動ビルド、ビルド済みアセットの直接アップロード、`create-cloudflare`（C3）からの初期化に対応。
- **Pages Functions**：`functions/` ディレクトリに配置したコードを Workers ランタイムで実行。ファイルベースルーティング、Middleware、KV / D1 / R2 / Durable Objects への Bindings、Node.js 互換 API のサブセットを提供。
- **プレビューデプロイ**：ブランチ・PR ごとに一意 URL を発行（無制限）。
- **Rollbacks**：本番デプロイを過去のバージョンへワンクリックで切り戻し。
- **Redirects / Headers**：`_redirects`・`_headers` ファイルによる宣言的設定。
- **カスタムドメイン・自動 TLS・HTTP/3・Brotli・Smart Placement** を標準搭載。

## アーキテクト視点：いつ選ぶか

### 適しているシーン
- Astro / Next.js / Nuxt / SvelteKit / Hugo などの静的・ハイブリッド SSG/SSR サイト。
- マーケティング LP、ドキュメントサイト、ブログ、コーポレートサイトなど Edge 配信が活きる用途。
- 軽量な API・フォーム処理・認証ミドルウェアを同一リポジトリで完結させたいプロジェクト。
- プレビュー URL を活用したレビュー文化を持つチーム。
- D1 / R2 / KV と密結合させたフルスタック JAMstack 構成。

### 適していないシーン
- 重量級バックエンド処理、長時間実行ジョブ、WebSocket を多用するアプリ（Workers の制約に従う）。
- ファイル数が極端に多いサイト（無料 20,000、有料 100,000 ファイル制限）。
- 単一ファイル 25 MiB 超を直接配信したいケース（R2 + 公開バケットへ分離が必要）。
- 月 500 ビルドを超える高頻度デプロイを Free プランで運用したいケース。
- Cloudflare 公式が「新規は Workers を推奨」と案内しており、長期的に最大限の機能拡張を求める場合は Workers 単体構成のほうが将来性がある（公式ドキュメントに「Migrate to Workers」リンクが常設）。

## Workers との関係（Pages 特有：必須セクション）
Pages Functions は内部的には Cloudflare Workers ランタイムで動作する。両者の使い分けは以下の通り。

| 観点 | Pages | Workers |
|---|---|---|
| 主目的 | 静的アセット配信 + 付随的なサーバ処理 | コードファースト、汎用エッジ実行環境 |
| 静的アセット | 一級市民。`_headers` / `_redirects` で宣言的に制御 | `assets` バインディングで近年対応 |
| ルーティング | `functions/` ディレクトリのファイルベース（規約駆動） | `wrangler.toml` の `routes` または `fetch` ハンドラ内で自由に記述 |
| デプロイ単位 | プロジェクト＝サイト。Git 連携前提のワークフロー | Worker 単位。Git 連携も可だが必須ではない |
| ビルド | Cloudflare 側でフレームワーク自動ビルド | ローカル / CI でビルドし `wrangler deploy` |
| 制限 | Builds 月 500（Free）、ファイル数・サイズ制限あり | リクエスト課金。アセット制限は別体系 |
| 課金 | Functions リクエストは Workers 課金枠を消費（Standard usage model） | 同左 |

Cloudflare 公式は近年 Workers の Static Assets 機能を強化し、ドキュメントナビにも「Migrate to Workers」を常設している。新規プロジェクトでフルスタックを志向する場合、Workers 単体のほうが将来の機能追従性が高い。一方、既存の SSG / フレームワークを Git 連携で素早く載せ替える用途では Pages が依然として最短経路である。

## 競合・代替

| プロバイダ | 違い |
|---|---|
| Vercel | Next.js 最適化と DX が圧倒的。Edge Functions と Serverless Functions の二層構造。帯域課金が高めで、Cloudflare に対し中〜大規模で価格差が出る。 |
| Netlify | 元祖 JAMstack。Build Plugins が豊富、Forms / Identity など独自機能あり。Edge Functions は Deno ベース。ビルド時間課金が中心。 |
| AWS Amplify Hosting | AWS エコシステムとの統合（Cognito / AppSync）が強み。CloudFront 経由の配信。設定が AWS 標準で複雑だが企業要件に強い。 |
| Firebase Hosting | Google のエコシステム（Auth / Firestore / Cloud Functions）と一体運用。Cloud Run 統合で SSR 可能。Asia 配信は良好。 |
| S3 + CloudFront | フルセルフ構築。柔軟性最大だが、ビルドパイプライン・キャッシュ無効化・ACM 証明書管理を自前で組む必要あり。コストは大規模配信で最安クラス。 |

差別化軸：Pages は「Cloudflare ネットワークの広さと Workers エコシステム（D1 / R2 / KV / Durable Objects / Queues）への密結合」「無料枠の太さ（無制限帯域・無制限リクエスト・月 500 ビルド）」が最大の武器。

## 料金モデルの要点
- **配信**：帯域・リクエスト数ともに無制限・無料（Free プラン含む）。
- **ビルド**：Free 月 500 / 同時 1、Pro 月 5,000 / 同時 5、Business 月 20,000 / 同時 20。タイムアウト 20 分。
- **Functions**：Workers 課金枠を共有（Standard usage model）。Free は 1 日 100,000 リクエスト、Paid は $5/月で 1,000 万リクエスト含み、超過分は $0.30/100 万リクエスト。
- **カスタムドメイン**：Free 100 / Pro 250 / Business 500 / Enterprise 500+。
- **ファイル数**：Free 20,000 / Paid 100,000（`PAGES_WRANGLER_MAJOR_VERSION=4` 設定が必要）。
- **ファイルサイズ**：1 ファイル最大 25 MiB。超過分は R2 に逃がす設計が定石。

## CLI / IaC 操作例

```bash
# プロジェクト初期化（C3）
npm create cloudflare@latest my-site -- --framework=astro

# ローカル開発（Pages Functions 含む）
npx wrangler pages dev ./dist

# Direct Upload による本番デプロイ
npx wrangler pages deploy ./dist --project-name=my-site --branch=main

# プロジェクト一覧
npx wrangler pages project list

# デプロイ履歴
npx wrangler pages deployment list --project-name=my-site

# シークレット設定（Functions 用）
npx wrangler pages secret put API_KEY --project-name=my-site
```

`wrangler.toml`（Pages Functions 用）：

```toml
name = "my-site"
compatibility_date = "2026-04-01"
pages_build_output_dir = "./dist"

[[d1_databases]]
binding = "DB"
database_name = "my-db"
database_id = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

[[r2_buckets]]
binding = "ASSETS"
bucket_name = "my-assets"
```

Terraform は `cloudflare_pages_project` リソースでプロジェクト・ビルド設定・環境変数・カスタムドメインを宣言的に管理可能。

## 制限・注意点
- **Free プランのビルド回数**：月 500 回上限。CI で頻繁にプレビュー生成するチームは Pro 必須。
- **同時ビルド**：Free は 1。マージ集中時にキューイングが発生。
- **ビルドタイムアウト**：20 分固定。重い SSG はビルド分割または事前ビルド戦略が必要。
- **ファイル数 20,000 / 100,000**：画像が多い E コマース・ギャラリー系は要注意。R2 + 動的配信に切り替える。
- **単一ファイル 25 MiB**：動画・大型 PDF は R2 へ。
- **`_headers` / `_redirects`**：ヘッダ 100 ルール、リダイレクト 2,000 静的 + 100 動的まで。超える場合は Bulk Redirects または Functions で実装。
- **新規プロジェクトの方向性**：Cloudflare 自身が「Migrate to Workers」を案内しており、Pages は機能追加よりも Workers Static Assets への統合が今後の主軸。新規構築時は Workers 単体構成も比較検討すべき。
- **Functions のコールドスタート**：Workers 同様ほぼゼロだが、大規模 Bindings 利用時はリージョン配置（Smart Placement）の検証が必要。
- **プロジェクト数**：1 アカウントあたりソフトリミット 100。短期間の大量作成はスロットリング対象。

## 参考リンク
- Cloudflare Pages Overview: https://developers.cloudflare.com/pages/
- Pages Limits: https://developers.cloudflare.com/pages/platform/limits/
- Pages Functions: https://developers.cloudflare.com/pages/functions/
- Migrate to Workers: https://developers.cloudflare.com/workers/static-assets/migration-guides/migrate-from-pages/
- Wrangler Pages Commands: https://developers.cloudflare.com/workers/wrangler/commands/#pages

---
参照日: 2026-05-03
