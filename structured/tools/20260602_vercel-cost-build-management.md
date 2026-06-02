# Vercel料金超過対策 × ビルド管理改善 検証ログ

> ステータス: 進行中（方針①②対応済み、③④は段階対応）
> 作成日: 2026/06/02
> 最終更新: 2026/06/02
> ファイルパス: ~/Documents/ai-business-os/15_ナレッジ基盤/vault/structured/tools/20260602_vercel-cost-build-management.md

---

## 📋 検証概要
- **ツール/サービス名**: Vercel（Proプラン）
- **検証対象**: 料金超過の原因分析とビルド管理によるコスト最適化
- **バージョン/リリース日**: 2025〜2026年の新課金体系（Fluid Compute / Active CPU / Elastic Build Machines）を前提
- **検証期間**: 2026/06/02 -（対応継続中）
- **検証担当者**: 田中省伍（shogoworks）
- **検証ステータス**: 方針①②は対応済み、③④は段階的に対応

---

## 1. 背景と検証目的
### なぜこの検証を行うのか
- 契約プランは $20/月（Pro）だが、実請求が $132.62 まで膨らんだ。On-Demand 超過が約 $112。原因を特定し、再発を止める。

### 解決したい課題
- ビルドが想定より頻繁に走り、Build CPU Minutes が積み上がっている。
- featureブランチ運用が確立されておらず、mainへの細かいPR・マージが多い。

### 期待される効果・ビジネスインパクト
- 月次のホスティングコストを契約プラン相当（数十ドル規模）まで圧縮する。
- 「作って終わり」ではなく運用保守・コストまで見る開発フローを確立する。

---

## 2. ツール/機能の基本情報
### 概要
- VercelはGitHub連携で、デフォルトでは全ブランチへのpush・PR作成時に自動でデプロイ（ビルド）を実行する。
- mainへの直接マージが多いほど、そのたびに本番ビルドが走りコストが積み上がる。

### 提供元
- Vercel Inc.

### 主要機能（コストに関わるメトリクス）
- **Build CPU Minutes**: ビルド実行時のCPU時間に対する課金。今回の超過の主因。
- **Fast Origin Transfer**: オリジンからのデータ転送量。
- **Fluid Active CPU**: Fluid Compute上で実際にCPUを使った時間に対する課金。常時起動に近いコストだが今回は軽微。

### 技術スタック・アーキテクチャ
- 2025/4/23 から Fluid Compute がデフォルト化。2025〜2026年に Active CPU 課金（I/O待ち中は課金されず実CPU時間のみ）へ移行。
- 新規チームのビルドマシンは Elastic Build Machines がデフォルト（従来の Turbo 固定から自動スケールへ）。

---

## 3. 検証方法
### 検証環境
- **使用アカウント**: shogoworks Vercel Pro
- **プラン/エディション**: Pro（$20/月/ユーザー）
- **検証環境**: 本番（実プロジェクト）
- **対象プロジェクト**: `sales-management-system-dev` / `sales-management-system-prod`

### 検証シナリオ
1. 請求の費用内訳を確認し、超過の主因メトリクスを特定する。
2. 開発フロー（ブランチ・PR・マージの粒度）とビルド発火条件を突き合わせる。
3. Ignored Build Step で production 以外のビルドを止め、効果を見る。

### 前提条件・制約事項
- featureブランチでのPreview確認は現状の運用に組み込まれていない（=止めても実害が小さい）。

---

## 4. 検証結果
### 定性的評価
- 超過の構造はサーバーレス構成そのものの問題ではなく、ビルド回数の多さに起因していた。
- Fluid Active CPU（常時起動に近いコスト）は $1.80 で、今回の超過分としては軽微だった。

### 定量的評価

#### 費用内訳（当月の額面）
| 項目 | 金額 | 全体に占める割合 |
| --- | --- | --- |
| Build CPU Minutes | $145.43 | 約90% |
| Fast Origin Transfer | $2.53 | 少額 |
| Fluid Active CPU | $1.80 | 少額 |
| その他 | 少額 | - |

- 契約プラン: $20/月
- 実請求（On-Demand超過込み）: $132.62
- 超過額: 約 $112
- **Build CPU Minutes が全体の約90%を占め、ビルドの頻度・回数が主因。**

#### 対応後の見込み
- Ignored Build Step（Only build production）により、featureブランチ・未割り当てブランチへのpush/PRではビルドが走らなくなる。ビルド回数の削減でBuild CPU Minutesの圧縮を見込む。

---

## 5. 比較・優位性分析
### 他ホスティングとのコスト比較（2026年）
| プラットフォーム | ビルド | 帯域 | 備考 |
| --- | --- | --- | --- |
| Vercel | $0.0035/CPU分〜（Elastic） | $0.15/GB（超過） | Next.js最適化が最強、コストは高め |
| Cloudflare Pages | 月500ビルド（無料）、実質無制限に近い | Egress無料 | コスト最安、帯域課金なし |
| Netlify | 100分/月（無料） | 100GB/月（無料） | 2025年に無料枠を300分→100分へ削減 |
| Render | 月500ビルド分（無料） | 100GB/月（無料） | フルスタック対応、Next.js最適化は弱い |

### 優位性
- Next.jsとの統合・DX・Preview体験はVercelが優れる。

### 劣位性・懸念点
- ビルド・帯域の従量課金が他社より高く、放置すると膨らみやすい。Next.js以外（Astro等）なら Cloudflare Pages 移行でビルド・帯域コストをほぼゼロに近づけられる。

---

## 6. リスク評価
### コスト暴走リスクと対策
- Spend Management を設定しない限り、On-Demand 超過は上限なく課金され続ける。
- 対策: Spend Management で 50%/75%/100% 通知、上限到達時に production を自動停止（ハードリミット相当）。新規Proチームは $200 がデフォルト予算。
- 注意: チェックは数分ごとのため、上限到達後も数分は課金が継続しうる。絶対上限より低い値を設定するのが安全。

### ベンダーロックインリスク
- 旧 Vercel Postgres / KV は Marketplace 移行で Neon / Upstash へ。自社継続は Blob / Edge Config 中心。用途別にホスティングを分離する余地がある。

---

## 9. 学びとナレッジ
### 発見したこと
- 超過の主因は「常時起動コスト」ではなく「ビルド回数の多さ」だった。
- Ignored Build Step の「Only build production」はVercel組み込みオプションで、bashコマンドによるキャンセルとは仕組みが異なる。キャンセルされたビルドはデプロイメントクォータにカウントされるが、スキップ（ビルド未実行）はCPU消費が発生しない。

### Tips・ベストプラクティス
- **Turbo固定 → Elastic に変更**: Turbo $0.126/分 に対し Elastic は $0.0035/CPU分から。多くのPJでコスト半減以上。
- **Ignored Build Step で production 以外をスキップ**: `if [[ "$VERCEL_ENV" == "production" ]]; then exit 1; else exit 0; fi`。
- **`vercel.json` でブランチ単位制御**: `git.deploymentEnabled` でパターン指定のデプロイ無効化。
- **Turborepo Remote Cache**: モノレポなら追加費用ゼロでビルド時間を最大85%削減。全プラン無料。
- **On-Demand Concurrent Builds を「1ブランチ1ビルド」に制限**: 並行ビルドの無駄を抑制。
- **Active CPU 課金の理解**: I/O待ち中は課金されないため、API RouteへのCache-Control / ISR 設定でActive CPU消費を削減できる。

---

## 10. 判定と今後のアクション
### 総合評価
⭐️⭐️⭐️⭐️☆ — 原因は明快で、組み込みオプションで止血可能。運用フロー整備が残課題。

### 対応ロードマップ
- 🔴 **完了**: Ignored Build Step を「Only build production」に設定（dev=developのみ / prod=mainのみビルド）→ ビルド回数を削減
- 🔴 **完了**: mainのPR運用 → 直接プッシュを防止（既に実施済み、追加対応不要）
- 🟡 **今後**: Spend Limit をハードリミットに変更 → 上限超過を防ぐ
- 🟢 **ゆくゆく**: featureブランチ運用へ移行（作業者 → feature/* → develop → main）→ 開発品質向上・本番障害リスク低減

### トレードオフ
- featureブランチ単位のPreview URLが発行されなくなる。動作確認はdevelop/mainマージ後に行う運用へ。現状Preview確認は運用に組み込まれていないため実害なし。

### 次のステップ
- [ ] Spend Management のハードリミット設定
- [ ] Elastic Build Machines への切替確認（Turbo固定になっていないか）
- [ ] 数週間後に請求を再確認し、Build CPU Minutes の削減効果を測定

---

📚 関連リソース
### 公式ドキュメント・出典
- Managing Builds: https://vercel.com/docs/builds/managing-builds
- Spend Management: https://vercel.com/docs/spend-management
- Remote Caching: https://vercel.com/docs/monorepos/remote-caching
- Ignored Build Step KB: https://vercel.com/kb/guide/how-do-i-use-the-ignored-build-step-field-on-vercel
- Git Configuration: https://vercel.com/docs/project-configuration/git-configuration
- Introducing Active CPU pricing for Fluid compute: https://vercel.com/blog/introducing-active-cpu-pricing-for-fluid-compute
- Fluid compute pricing: https://vercel.com/docs/functions/usage-and-pricing
- Do canceled deployments count toward quota?（GitHub Discussion）: https://github.com/vercel/vercel/discussions/5716

### 関連プロジェクト
- `structured/projects/20260508_vercel-textbook.md`（Vercel教材化PJ）

---

✅ メモ・議論ログ
- 内訳の額面合計（$145.43 + α）と実請求 $132.62 の差は、プラン内包分・クレジット控除によるもの。記事では「Build CPUが約9割」という構造を主眼にする。

---

## 📝 更新ログ
| 日時 | 更新内容の概要 |
|---|---|
| 2026/06/02 | ファイル作成（init）。料金超過レポートを構造化し、最新ベストプラクティスを反映 |
