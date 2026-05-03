# Images

## 一行サマリ
Cloudflare Imagesは、画像のストレージ・オンザフライ変換・グローバル配信をエッジで統合提供するマネージド画像基盤である。

## 解決する課題（Why）
- デバイス・ブラウザ別に複数サイズの画像を事前生成・保管するコストを排除する。
- レスポンシブ画像、サムネイル、AVIF/WebPトランスコードなどの最適化を、アプリ側のロジックを増やさずに実現する。
- 画像CDN・変換サーバ・ストレージという三層を別々に契約・運用する手間をなくす。
- オリジン画像が大きい場合の帯域コストとLCPなどCore Web Vitals悪化を抑える。

## 主要機能（What）
- **保存（Images storage）**: 画像をCloudflareにアップロードし、変換済みバリアントを含めて配信まで完結。
- **オンザフライ変換（Image Transformations）**: R2や任意のオリジンに置いた画像をURLパラメータ（`width`、`height`、`format`、`quality`、`fit`、`gravity`、`onerror`等）で動的にリサイズ・再エンコード。
- **Workers Bindings**: Workers内から`env.IMAGES.input(...).transform(...).output(...)`形式で変換APIを呼び出し可能。
- **Predefined variants**: `thumbnail=100x100`、`hero=1600x500`のような名前付きバリアントを事前定義し、URLで指定して呼び出す。
- **Polish連携**: ZoneレベルでJPEG/PNG/WebP/AVIFへの自動最適化を行うCloudflare Polishと併用可能。
- **AI機能**: 公式ドキュメント上、画像理解（draw / describe）はWorkers AI側のVision系モデル経由で扱う設計。Images本体は最適化・配信レイヤに特化。

## 2つのモード（必須）
### モード1: Cloudflare Imagesにアップロード保存
- 画像をImagesにアップロードし、ストレージ・変換・配信をすべて任せる。
- 課金は **Images Stored**（保管）と **Images Delivered**（配信回数）。
- バリアントはストレージ消費にカウントされない。

### モード2: 既存R2 / 外部URLにTransformationだけ適用
- 画像はR2や任意のオリジンに置き、URLパターン（例: `/cdn-cgi/image/width=800,format=auto/<source>`）で変換のみ呼び出す。
- 課金は **Images Transformed**（ユニーク変換数）のみ。
- Free planでも月5,000ユニーク変換まで利用可能。

## アーキテクト視点：いつ選ぶか
### 適しているシーン
- ECサイト・メディアサイトで多数のサムネイル・解像度を動的に必要とする場合。
- すでにCloudflareにフロントを乗せており、Polish・R2・Workersと統合したい場合。
- 画像CDN契約と原本ストレージを一本化してベンダーを減らしたい場合。
- ユーザー投稿画像（UGC）を受け取り、即座に配信用に最適化したい場合。

### 適していないシーン
- 動画ストリーミングが主用途（→ Cloudflare Stream）。
- 高度な画像生成・編集AI（背景除去、生成塗りつぶし等）を必須とする場合（Cloudinaryの方が機能網羅）。
- 既存のimgix / Cloudinaryで複雑なカスタム変換パイプラインを構築済みで、移行コストが利得を上回る場合。
- オフライン一括バッチ変換が中心で、エッジキャッシュの恩恵を受けない用途。

## 競合・代替

| 観点 | Cloudflare Images | Cloudinary | imgix | Vercel Image |
|---|---|---|---|---|
| ポジション | 最適化＋配信＋ストレージ統合 | 高機能DAM＋AI編集 | URLベースの画像変換特化 | Next.js統合の画像最適化 |
| 課金軸 | 変換ユニーク数・保管・配信 | クレジット制（変換・帯域） | オリジン画像数・帯域 | Source Images・Transformations |
| AI/編集機能 | 限定的（Workers AIで補完） | 豊富（背景除去、生成塗り等） | 中程度 | 限定的 |
| ストレージ統合 | Images本体＋R2 | 自前ストレージあり | 別途必要 | Vercel Blob |
| CDN | Cloudflare（300+拠点） | Akamai系 | Fastly系 | Vercel Edge |
| 価格感 | 低〜中（小〜中規模で割安） | 高 | 中〜高 | 中 |

S3 + Lambda@Edge + CloudFrontやBunny Optimizerと比較すると、Cloudflare Imagesは「設定の少なさ」と「Free tierで5,000変換」が優位。一方、細粒度の変換ロジックやAI編集はCloudinaryに分がある。

## 料金モデルの要点
- **Free plan**: 月5,000ユニーク変換まで無料。超過すると新規変換は`9422`エラー（既存キャッシュは継続配信、課金なし）。
- **Paid plan**:
  - Images Transformed: 最初の5,000ユニーク変換込み、以降 **$0.50 / 1,000ユニーク変換**。
  - Images Stored: **$5 / 100,000枚 / 月**（保管）。
  - Images Delivered: **$1 / 100,000配信 / 月**。
- ユニーク変換は「原本画像 × パラメータ組合せ」単位。同月内の同一URLリクエストはキャッシュヒットでも初回1回のみ課金。
- `format=auto`は配信形式（AVIF/WebP）が分かれても1ユニークとしてカウント。
- R2併用時はR2のストレージ・オペレーション課金が加算される。

## CLI / IaC 操作例

### Wranglerで変換用Bindingを設定
```toml
# wrangler.toml
name = "image-worker"
main = "src/index.ts"
compatibility_date = "2026-01-01"

[images]
binding = "IMAGES"
```

### Worker内から変換
```typescript
export default {
  async fetch(req: Request, env: Env): Promise<Response> {
    const origin = await fetch("https://example.com/source.jpg");
    const result = await env.IMAGES
      .input(origin.body!)
      .transform({ width: 800, format: "auto", quality: 85 })
      .output({ format: "image/avif" });
    return result.response();
  },
};
```

### URL変換（Zone有効化後）
```
https://example.com/cdn-cgi/image/width=800,format=auto,quality=85/https://origin.example.com/photo.jpg
```

### REST APIで画像アップロード
```bash
curl -X POST \
  -H "Authorization: Bearer $CF_API_TOKEN" \
  -F "file=@photo.jpg" \
  "https://api.cloudflare.com/client/v4/accounts/$ACCOUNT_ID/images/v1"
```

## 制限・注意点
- 入力画像の最大解像度・サイズ・対応フォーマットは公式の[limits and supported formats](https://developers.cloudflare.com/images/reference/)で要確認（一般に最大解像度・最大ファイルサイズに上限あり）。
- Transformationsをzoneで使う場合、ダッシュボードで明示的に有効化が必要。
- デフォルトでは同一zoneのオリジンのみソース許可。外部URLからの変換はSource origins設定が必須。
- Workers Bindings経由の変換は、URLが同一でも呼び出すたびに1ユニーク変換としてカウントされる（URL方式のキャッシュ重複排除と挙動が異なる）。
- 変換結果のキャッシュ寿命はEdge Cache TTLに従うため、Cache Rulesでの調整が必要なケースあり。
- Free planの`9422`エラー時は`onerror=redirect`で原本にフォールバック可能（同一ドメインのソースに限る）。

## 参考リンク
- 公式概要: https://developers.cloudflare.com/images/
- Pricing: https://developers.cloudflare.com/images/pricing/
- Transformations Overview: https://developers.cloudflare.com/images/transform-images/
- Optimization features: https://developers.cloudflare.com/images/optimization/features/
- Workers Bindings: https://developers.cloudflare.com/images/optimization/transformations/bindings/

---
参照日: 2026-05-03
