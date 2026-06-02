---
title: Vercelの請求が$20プランで$132になった原因はビルド回数だった — Build CPU Minutesを止血する実践
status: draft
created: 2026-06-02
updated: 2026-06-02
type: tech-tutorial
related:
  - 15_ナレッジ基盤/vault/structured/tools/20260602_vercel-cost-build-management.md
medium: tech-blog
target_cta: shogoworks.com
target_platforms:
  - Zenn
  - Qiita
---

# Vercelの請求が$20プランで$132になった原因はビルド回数だった — Build CPU Minutesを止血する実践

Vercel Proプラン（$20/月）の請求が、ある月に$132.62まで膨らんだ。差額の約$112はすべてOn-Demandの超過分だった。本記事では、原因をどう特定し、どの設定で止血したか、そして2025〜2026年の新課金体系を踏まえて何が効くのかを整理する。

## 1. まず内訳を見る

コスト最適化は内訳の確認から始まる。Vercelダッシュボードの Usage で、どのメトリクスが課金を押し上げているかを把握する。今回の内訳は次のとおり。

| 項目 | 金額 | 割合 |
| --- | --- | --- |
| Build CPU Minutes | $145.43 | 約90% |
| Fast Origin Transfer | $2.53 | 少額 |
| Fluid Active CPU | $1.80 | 少額 |

サーバーレス構成だと「常時起動コスト（Fluid Active CPU）が原因では」と疑いがちだが、実際は$1.80と軽微。突出していたのは Build CPU Minutes、つまりビルド実行時のCPU時間だった。

## 2. 2025〜2026年の課金モデルを押さえる

原因を理解するには、現行の課金体系を知っておくと話が早い。

### Build CPU Minutes とビルドマシン

ビルドは選択したマシンのCPU時間で課金される。マシンの単価は以下のように差が大きい。

| 種別 | vCPU | 単価 |
| --- | --- | --- |
| Standard | 4 | $0.014/分（On-Demand時のみ課金） |
| Enhanced | 8 | $0.028/分（常時課金） |
| Turbo | 30 | $0.126/分（常時課金） |
| Elastic | 4〜30 | $0.0035/CPU分（自動最適化） |

2025年以降の新規チームは Elastic Build Machines がデフォルト。Turbo固定のままだと$0.126/分かかるが、多くのプロジェクトは30 vCPUを使い切らない。Elasticへ切り替えるだけでコストが半分以下になるケースは珍しくない。
出典: https://vercel.com/docs/builds/managing-builds

### Fluid Compute と Active CPU 課金

2025/4/23 から Fluid Compute がデフォルト化し、Active CPU 課金が導入された。従来は関数のI/O待ち中もCPU課金されていたが、Active CPU 課金ではコードが実際にCPUを使った時間のみ課金される。100msの計算と400msのDB待ちがある関数なら、課金対象は100msだけだ。AI/LLMのようなアイドルの多いワークロードでは最大90%の削減になる。
出典: https://vercel.com/blog/introducing-active-cpu-pricing-for-fluid-compute

## 3. なぜビルドが積み上がったか

VercelはGitHub連携時、デフォルトで全ブランチへのプッシュ・PR作成時に自動ビルドを実行する。プレビューデプロイは便利な反面、mainへ細かくPRを出してマージするフローでは、反映のたびに本番ビルドが走る。featureブランチを切らずに進めると、その回数はさらに増える。

一回あたりのビルドは小さくても、回数が積もればBuild CPU Minutesは$145に届く。コストはビルドの重さではなく回数で効いていた。

## 4. 止血：Ignored Build Step

本番に関係ないビルドを止めるには Ignored Build Step を使う。プロジェクト設定の Settings → Build and Deployment → Ignored Build Step にスクリプトを置く。終了コード `0` でビルドをスキップ、`1` 以上で続行する。

production以外をスキップする最小構成は次のとおり。

```bash
if [[ "$VERCEL_ENV" == "production" ]]; then
  exit 1;
else
  exit 0;
fi
```

ダッシュボードのプリセット「Only build production」を選べば、同じ挙動をGUIだけで設定できる。今回は各プロジェクトでこれを採用した。

- `sales-management-system-dev`：developブランチのみビルド
- `sales-management-system-prod`：mainブランチのみビルド

ブランチパターン単位で制御したい場合は `vercel.json` の `git.deploymentEnabled` を使う。

```json
{
  "git": {
    "deploymentEnabled": {
      "internal-*": false
    }
  }
}
```

出典: https://vercel.com/docs/project-configuration/git-configuration

### キャンセルされたビルドのクォータ扱い

注意点が一つある。Vercel公式メンテナーはGitHub Discussionで、Ignored Build Step経由でキャンセルされたデプロイは「デプロイメントクォータ」にカウントされると述べている。ただしBuild CPU Minutesは実際に走ったビルド分のみカウントされる。スキップ＝ビルド未実行＝CPU消費なし、という構造なので、コスト削減の手段としては有効だ。
出典: https://github.com/vercel/vercel/discussions/5716

トレードオフとして、ブランチごとのプレビューURLは発行されなくなる。動作確認はdevelop/mainマージ後に行う運用へ寄せる。プレビュー確認を運用に組み込んでいないなら影響は小さい。

## 5. さらに効く打ち手

### Spend Management でハードリミット

Settings → Billing → Spend Management をONにすると、50%/75%/100%で通知が飛び、上限到達時に全プロジェクトの本番デプロイを自動停止できる。新規Proチームは$200がデフォルト予算。チェックは数分ごとのため、絶対上限より低めに設定するのが安全。停止後の再開はプロジェクトごとに手動。
出典: https://vercel.com/docs/spend-management

### Turborepo Remote Cache

モノレポなら、Turborepoのリモートキャッシュが自動で有効になる（追加設定不要）。変更のないパッケージのタスクをキャッシュから復元し、CI時間を最大85%削減できる。全プラン無料（Proは月1TBまでfair use）。外部CIでも `TURBO_TOKEN` / `TURBO_TEAM` を設定すれば使える。
出典: https://vercel.com/docs/monorepos/remote-caching

### Concurrent Builds の制限と配信側の最適化

On-Demand Concurrent Builds を「1ブランチ1ビルド」に制限すると並行ビルドの無駄を抑えられる。配信側では `next/image` とCDN前段配置でFast Origin Transferを、API RouteへのCache-Control / ISR設定でActive CPU消費を削減できる。

## 6. 用途別ホスティングという選択肢

対応後も超過が続く、あるいは規模が拡大するなら、用途でホスティングを分けるのも手だ。

| プラットフォーム | ビルド | 帯域 | 向き |
| --- | --- | --- | --- |
| Vercel | $0.0035/CPU分〜（Elastic） | $0.15/GB（超過） | Next.js最適化、DX重視 |
| Cloudflare Pages | 月500ビルド無料、実質無制限に近い | Egress無料 | コスト最安、静的サイト |
| Netlify | 100分/月（無料） | 100GB/月（無料） | 2025年に無料枠縮小 |
| Render | 月500ビルド分（無料） | 100GB/月（無料） | フルスタック |

Next.js以外（Astro等）のLP・静的サイトなら、Cloudflare Pagesへの移行でビルド・帯域コストをほぼゼロに近づけられる。管理システムはVercel、軽いサイトはCloudflare、と分けるだけで構造が変わる。

## まとめ

- コスト調査は内訳の確認から。今回はBuild CPU Minutesが約90%で、ビルド回数が主因だった。
- Ignored Build Step（Only build production）で本番以外のビルドを止めるのが最短の止血。
- 中長期では Elastic Build Machines への切替、Spend Management のハードリミット、Turborepo Remote Cache が効く。
- フレームワーク次第では用途別ホスティング分離も選択肢になる。

作って公開するところまではAIが加速してくれる。請求書を読み、止める出費を止める運用は、まだ人間の仕事だ。

## 参考

- Managing Builds: https://vercel.com/docs/builds/managing-builds
- Spend Management: https://vercel.com/docs/spend-management
- Remote Caching: https://vercel.com/docs/monorepos/remote-caching
- Ignored Build Step KB: https://vercel.com/kb/guide/how-do-i-use-the-ignored-build-step-field-on-vercel
- Git Configuration: https://vercel.com/docs/project-configuration/git-configuration
- Active CPU pricing for Fluid compute: https://vercel.com/blog/introducing-active-cpu-pricing-for-fluid-compute
- Do canceled deployments count toward quota?: https://github.com/vercel/vercel/discussions/5716
