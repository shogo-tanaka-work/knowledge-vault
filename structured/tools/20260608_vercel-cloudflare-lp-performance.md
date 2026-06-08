# Vercel vs Cloudflare Pages（LP配信性能） 検証ログ

> ステータス: 完了
> 作成日: 2026/06/08
> 最終更新: 2026/06/08
> ファイルパス: /Users/shogo/Documents/ai-business-os/15_ナレッジ基盤/vault/structured/tools/20260608_vercel-cloudflare-lp-performance.md

---

## 📋 検証概要

- **ツール/サービス名**: Vercel / Cloudflare Pages（同一LPサイトを2環境で公開し比較）
- **検証対象**: ホスティング基盤の配信性能比較
- **バージョン/リリース日**: PageSpeed Insights / Lighthouse 13.3.0
- **検証期間**: 2026/06/08 - 2026/06/08
- **検証担当者**: 田中省伍（shogoworks）
- **検証ステータス**: 完了

---

## 1. 背景と検証目的

### なぜこの検証を行うのか
- 同一のLPサイト（shogoworks）を Vercel と Cloudflare Pages の2環境で公開し、表示速度がどちらが速いかを実測で確認したかった。
- 体感として、`.vercel.app` ドメインを持たない（=Cloudflare独自ドメイン）側のほうが表示が速いと感じたため、数値で裏取りする。

### 解決したい課題
- LPサイトのホスティング基盤として、どちらが配信性能に優れるかの判断材料がなかった。
- 「Cloudflareの方が速い」という一般論が自社サイトでも成り立つかを検証する。

### 期待される効果・ビジネスインパクト
- LP制作・提案時の技術選定根拠になる。
- 顧客への説明（なぜCloudflareを選ぶか）に数値と理屈を添えられる。

---

## 2. ツール/機能の基本情報

### 概要
- Vercel / Cloudflare Pages はいずれもフロントエンド向けホスティング基盤。静的サイト・LP・Jamstack配信に対応。

### 提供元
- Vercel, Inc. / Cloudflare, Inc.（NYSE: NET、2019年上場の独立企業）

### 主要機能
- 静的アセットのエッジ配信、エッジ実行（Vercel: Edge/Serverless Functions、Cloudflare: Workers）、独自ドメイン・SSL。

### 技術スタック・アーキテクチャ
- **Cloudflare**: 337都市・100カ国以上のPoP、全拠点同一IPのAnycast構成。Workers（V8 isolates、コールドスタート5ms未満）。
- **Vercel**: 126 PoP / コンピュート20リージョン。実行基盤はAWS Lambda。Edge FunctionsはV8 Edge Runtime。

---

## 3. 検証方法

### 検証環境
- **使用アカウント**: shogoworks
- **プラン/エディション**: （情報なし）
- **検証環境**: 本番（公開URL）

### 検証シナリオ
1. 同一LPを Vercel（`shogo-works-nextjs.vercel.app`）と Cloudflare（`shogoworks.com`）で公開。
2. PageSpeed Insights でモバイル・デスクトップそれぞれ計測。
3. browser-use CLI でPageSpeed解析ページのスコアを自動取得（JS動的描画のためWebFetch不可）。

### 検証データ・サンプル
- 計測URL（Vercel）: https://pagespeed.web.dev/analysis/https-shogo-works-nextjs-vercel-app/dytzxcdvsc
- 計測URL（Cloudflare）: https://pagespeed.web.dev/analysis/https-shogoworks-com/tx27ew7u2d

### 前提条件・制約事項
- ラボデータは単一実行の推定値で、実行ごとに変動する。
- 両環境とも画像が非WebP等の重いデータで、「画像配信の改善」で約1,618 KiBの削減余地あり。

---

## 4. 検証結果

### 定性的評価

#### 機能面の評価
- LP配信用途では両者とも十分。差は配信速度（特にTTFB・初回描画）に出た。

#### 操作性・UI/UX
- （情報なし）

#### 出力品質
- ユーザー補助（93）・おすすめの方法（100）・SEO（100）は全条件で両環境同値。環境差はパフォーマンス領域に限定。

#### 実用性
- 「初回描画・視覚的完了の速さ」では Cloudflare（独自ドメイン）が一貫して速く、体感と整合した。

---

### 定量的評価

#### パフォーマンス（モバイル / Moto G Power・低速4G）

| 指標 | Vercel | Cloudflare | 速い方 |
| --- | --- | --- | --- |
| パフォーマンス | 99 | 75 | Vercel |
| ユーザー補助 | 93 | 93 | 同点 |
| おすすめの方法 | 100 | 100 | 同点 |
| SEO | 100 | 100 | 同点 |
| FCP | 1.1秒 | 0.9秒 | Cloudflare |
| Speed Index | 2.7秒 | 1.1秒 | Cloudflare |
| TBT | 70ms | 40ms | Cloudflare |
| CLS | 0 | 0 | 同点 |
| LCP | 1.7秒 | 9.9秒 | Vercel |

#### パフォーマンス（デスクトップ / カスタムスロットリング）

| 指標 | Vercel | Cloudflare | 速い方 |
| --- | --- | --- | --- |
| パフォーマンス | 85 | 93 | Cloudflare |
| ユーザー補助 | 93 | 93 | 同点 |
| おすすめの方法 | 100 | 100 | 同点 |
| SEO | 100 | 100 | 同点 |
| FCP | 0.5秒 | 0.2秒 | Cloudflare |
| Speed Index | 1.1秒 | 0.5秒 | Cloudflare |
| TBT | 130ms | 0ms | Cloudflare |
| CLS | 0 | 0 | 同点 |
| LCP | 2.4秒 | 1.8秒 | Cloudflare |

#### ROI試算
- （情報なし）

---

## 5. 比較・優位性分析

### 一般論としての基盤比較（2025〜2026年・公開情報ベース）

| 観点 | Cloudflare | Vercel |
| --- | --- | --- |
| エッジ拠点（PoP） | 337都市・100カ国以上 | 126 PoP / コンピュート20リージョン（AWS基盤） |
| 配信方式 | 全拠点同一IPのAnycast（自動で最寄り誘導） | PoP→最寄りリージョンへルーティング |
| エッジ実行 | Workers（V8 isolates・コールドスタート5ms未満） | Serverless（AWS Lambda）/ Edge Functions |
| 静的・LP配信 | 速い傾向（特にアジア等の遠隔地） | 北米・西欧は同等、遠隔地で不利になりやすい |
| 重い動的処理・SSR | Workersは計算上限が低め | Fluid Computeが有利（自社ベンチで平均2.55倍） |

### 優位性
- **Cloudflare**: PoP数の多さ（約2.5〜3倍）とAnycastで、ユーザーへの物理距離（RTT）が短くTTFB・初回描画が小さい。日本・東南アジアなど北米/西欧の外側ほど差が開きやすい。
- **Vercel**: Next.js SSRなど計算量の多い動的処理で有利。Fluid Computeで Cloudflare Workers比 平均2.55倍速いという自社ベンチあり（中立性に留保）。

### 劣位性・懸念点
- モバイル総合のみ Vercel 99 / Cloudflare 75 と逆転。要因は Cloudflare側モバイルLCPの単発値 9.9秒。同一画像でデスクトップは1.8秒、Vercelモバイルでも1.7秒のため、初回アクセス時のキャッシュ未ウォームや計測変動の影響が大きいと考えられ、再計測での確認が望ましい。

---

## 6. リスク評価

### ベンダーロックインリスク
- Cloudflare Workers / Vercel Functions ともに独自ランタイム依存。移植時はエッジ実行部分の書き換えが必要。

### 技術的リスク
- ラボ計測の変動。単一実行値での結論は避け、複数回計測が望ましい。

---

## 7. 連携性・拡張性

- （情報なし）

---

## 8. 実際の使用例・サンプル

### 成果物
- HTMLビジュアルレポート: `10_projects/shogo-works/perf-report-vercel-vs-cloudflare.html`
  - モバイル実測 → デスクトップ実測 → 一般論の基盤比較 を1ファイルに収録。PDF化（A4）対応。

### 取得手法のTips
- PageSpeed解析ページ（pagespeed.web.dev/analysis/...）はスコアをJSで動的描画するため、WebFetchでは取得不可。browser-use CLIで `open` → `eval "document.body.innerText"` でスコアを抽出した。

---

## 9. 学びとナレッジ

### 発見したこと
- 「表示が速い」という体感は数値で裏づけられた。FCP・Speed Index・TBTは全条件でCloudflareが速い。
- 総合スコアの逆転（モバイル）はLCP単発悪化が支配要因で、プラットフォームの実力差ではない可能性が高い。

### うまくいったこと
- browser-use CLIでJS動的描画ページのスコア取得に成功。

### Tips・ベストプラクティス
- LP・静的配信では Cloudflare の方が速い傾向。理由はGoogleとの関係ではなく、自前の337都市Anycastネットワークと独自Workersランタイム。
- 「静的＝Cloudflare／動的SSR＝Vercel」が2026年時点の住み分け。

### 要注意（事実確認）
- 「CloudflareとGoogleの資本提携」は誤解されやすい。2015年にGoogle Capital（現CapitalG）が出資したのは事実だが、Cloudflareは2019年にNYSE上場（NET）した独立企業で、現在Google傘下・資本提携ではない。現存するのはGoogle Cloudとの技術提携程度。速度の源泉はGoogleに由来しない。

---

## 10. 判定と今後のアクション

### 総合評価
⭐️⭐️⭐️⭐️☆（LP配信用途でのCloudflare優位を実測で確認）

### 導入判定
- [x] 条件付きで導入可（LP・静的配信はCloudflare、重いSSRはVercel）

### 判定理由
- LP・静的配信では初動の速さでCloudflareが一貫して優位。デスクトップでは総合スコアも上回った。

### 次のステップ
- [ ] モバイルLCPの再計測（2〜3回）で9.9秒の異常値を確定/解消
- [ ] 画像のWebP化でLCP・パフォーマンス改善
- [x] 検証終了
- [ ] LinkedIn / Qiita / Zenn 向け記事化（Noteは不向き）

### 追加で検証したい項目
- 実ユーザー指標（CrUX / フィールドデータ）での比較。

---

📚 関連リソース

### 公式ドキュメント
- Cloudflare Network（337都市）— https://www.cloudflare.com/network/
- Cloudflare Anycast 解説 — https://www.cloudflare.com/learning/cdn/glossary/anycast-network/
- Vercel Docs - Regions（126 PoP・AWS基盤）— https://vercel.com/docs/regions

### 参考記事・事例
- Vercel Blog - Fluid Compute Benchmark — https://vercel.com/blog/fluid-compute-benchmark-results
- 中立TTFBベンチ（aprets.me）— https://aprets.me/benchmark
- Cloudflare 2015年 Google Capital出資PR — https://www.cloudflare.com/press/press-releases/2015/fidelity-google-microsoft-baidu-and-qualcomm-back-cloudflare/
- Cloudflare 2019 IPO目論見書（SEC, NYSE:NET）— https://www.sec.gov/Archives/edgar/data/0001477333/000119312519244325/d735023d424b4.htm
- Cloudflare - GCP技術パートナー — https://blog.cloudflare.com/cloudflare-is-now-a-google-cloud-platform-technology-partner/

### 検証データ・ログ
- PageSpeed（Vercel）— https://pagespeed.web.dev/analysis/https-shogo-works-nextjs-vercel-app/dytzxcdvsc
- PageSpeed（Cloudflare）— https://pagespeed.web.dev/analysis/https-shogoworks-com/tx27ew7u2d
- HTMLレポート — 10_projects/shogo-works/perf-report-vercel-vs-cloudflare.html

---

✅ メモ・議論ログ
- 公開先候補: LinkedIn / Qiita / Zenn（技術寄りの数値検証のためNoteは不向きとの判断）。

---

## 📝 更新ログ
<!-- このセクションはスキルが自動で追記する。手動編集不要。 -->
| 日時 | 更新内容の概要 |
|---|---|
| 2026/06/08 | ファイル作成（init）＋HTMLレポート内容を反映し完了化（finalize） |
