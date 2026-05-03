# Stream

## 一行サマリ
Cloudflare Stream は、動画のアップロード・エンコード・保存・配信・プレイヤを単一APIで提供するサーバーレス動画基盤である。

## 解決する課題（Why）
自前で「FFmpeg によるトランスコード」「S3 などのオブジェクトストレージ」「CloudFront など CDN」「HLS/DASH のマニフェスト生成」「Video.js などのプレイヤ」「署名URLによるアクセス制御」「ライブ配信用 RTMP/SRT インジェスト」を組み合わせるパイプラインを構築・運用しなくて済む。Stream は H.264 + 適応的ビットレートストリーミング（360p〜1080p）を自動生成し、Cloudflareのグローバルネットワーク経由で配信するため、インフラ運用コストとエッジ最適化の二重の負担を一気に剥がせる。

## 主要機能（What）
- VOD アップロード（直接アップロード、URLからの取り込み、TUS による再開可能アップロード、Direct Creator Upload による署名付き一回限りURL）
- ライブ配信（Live Input：RTMPS/SRT インジェスト、低遅延HLS、DVR、自動録画）
- 自動トランスコード（H.264、ABR、複数解像度、Closed GOP 推奨）
- HLS / DASH マニフェスト自動生成
- 組み込み Stream Player（iframe 埋め込み）と独自プレイヤ向けマニフェストURL の両対応
- Signed URL によるアクセス制御（有効期限、IP/地域制限）
- MP4 ダウンロード（オフライン視聴用）
- Simulcasting（YouTube/Twitch などへの同時配信、SRT/RTMP Live Outputs）
- 静止画・アニメーションサムネイル生成
- 視聴分析（per-creator 単位、視聴ログ）

## アーキテクト視点：いつ選ぶか

### 適しているシーン
- VOD 配信プラットフォーム（オンライン講座、社内ナレッジ、メディアサイト）
- ユーザー投稿型動画サービス（Direct Creator Upload で安全に直アップ）
- ライブ配信を含むイベント・ウェビナー基盤
- 社内トレーニング・eラーニング教材配信
- Cloudflare の他サービス（Workers, R2, Access）と統合した動画ワークフロー

### 適していないシーン
- 4K/HDR 配信が必須なプレミアムコンテンツ（HDR は SDR に再エンコードされる、最大 1080p）
- 30GB を超える元ファイルをそのまま扱いたいケース
- DRM（Widevine/PlayReady/FairPlay）が契約上必須な OTT 大規模商用配信（Mux や AWS Media Services の方が成熟）
- 元ファイルをそのまま再ダウンロードして配布する用途（オリジナル入力ファイルは取得不可）
- HLS/DASH ではなく独自プロトコルや特殊コーデック（AV1, VP9）が必要な要件

## 競合・代替

| 観点 | Cloudflare Stream | Mux | api.video | Bunny Stream | AWS MediaConvert + CloudFront |
|---|---|---|---|---|---|
| 課金軸 | 保存分（min）+ 配信分（min） | エンコード + 配信 + 保存 | 取り込み + 配信 | 保存（GB）+ 配信（GB） | エンコード秒 + ストレージ + 配信 |
| 配信単価の目安 | $1 / 1,000 min | $0.00096/min 程度（プラン依存） | $0.30/1,000 min（配信） | $0.005〜0.06/GB | CloudFront 従量＋AWS egress |
| ライブ配信 | 標準対応（RTMPS/SRT、DVR） | 標準対応、低遅延に強い | 標準対応 | 標準対応 | MediaLive 別サービス |
| プレイヤ提供 | あり（iframe） | Mux Player | あり | あり | なし（自前/サードパーティ） |
| DRM | なし（Signed URL のみ） | あり（追加課金） | あり | なし | あり（SPEKE 連携） |
| エッジ統合 | Cloudflare 全機能と直結 | 独自CDN | 独自CDN | Bunny CDN | AWS CloudFront |
| 強み | 単純な料金、Workers連携 | 分析・QoEメトリクス | API設計の素直さ | 価格と速度 | 柔軟なパイプライン構築 |

## 料金モデルの要点
- **保存**：1,000分あたり $5 のプリペイド。ファイルサイズではなく動画の長さで課金。エンコード後の複数解像度や MP4 ダウンロード生成分は課金対象外。
- **配信**：1,000分あたり $1 のポストペイド従量課金。HLS/DASH セグメント単位で計上。クライアントのプリロード・バッファも配信扱い、ブラウザキャッシュからの再生は非課金。
- **取り込み・エンコード・帯域は無料**。配信課金にエッジ転送費用が含まれるため、CloudFront のような egress 別請求が発生しない。
- ライブと VOD は同じ単価で課金され、視聴者ゼロのライブは配信課金 $0、録画分のみ保存課金。
- Direct Creator Upload は `maxDurationSeconds` 分の保存枠が一時的に予約され、未使用なら解放される。
- 大規模利用はエンタープライズ契約でボリューム割引あり。

## CLI / IaC 操作例

```bash
# 直接アップロード（ファイル）
curl -X POST -H "Authorization: Bearer $CF_API_TOKEN" \
  -F file=@video.mp4 \
  https://api.cloudflare.com/client/v4/accounts/$ACCOUNT_ID/stream

# URL からの取り込み
curl -X POST -H "Authorization: Bearer $CF_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com/source.mp4","meta":{"name":"sample"}}' \
  https://api.cloudflare.com/client/v4/accounts/$ACCOUNT_ID/stream/copy

# Direct Creator Upload URL 発行（最大 600 秒の動画想定）
curl -X POST -H "Authorization: Bearer $CF_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"maxDurationSeconds":600}' \
  https://api.cloudflare.com/client/v4/accounts/$ACCOUNT_ID/stream/direct_upload

# Live Input（RTMPS/SRT 受信エンドポイント）の作成
curl -X POST -H "Authorization: Bearer $CF_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"recording":{"mode":"automatic"}}' \
  https://api.cloudflare.com/client/v4/accounts/$ACCOUNT_ID/stream/live_inputs

# Signed URL 用の鍵を発行
curl -X POST -H "Authorization: Bearer $CF_API_TOKEN" \
  https://api.cloudflare.com/client/v4/accounts/$ACCOUNT_ID/stream/keys
```

```hcl
# Terraform：Live Input を IaC 管理
resource "cloudflare_stream_live_input" "main_event" {
  account_id = var.account_id
  meta = { name = "main-event" }
  recording = {
    mode              = "automatic"
    require_signed_urls = true
  }
}
```

```html
<!-- 埋め込みプレイヤ -->
<iframe
  src="https://customer-<CODE>.cloudflarestream.com/<VIDEO_UID>/iframe"
  allow="accelerometer; gyroscope; autoplay; encrypted-media; picture-in-picture;"
  allowfullscreen></iframe>

<!-- 独自プレイヤ向け HLS -->
<video controls>
  <source src="https://customer-<CODE>.cloudflarestream.com/<VIDEO_UID>/manifest/video.m3u8"
          type="application/x-mpegURL">
</video>
```

## 制限・注意点
- 1動画あたり最大 **30GB**、デフォルトで **同時 120本** までキューイング/エンコード可能。
- 元の入力ファイルそのものは再ダウンロード不可（MP4 Downloads は再エンコード版）。
- 解像度は **360p〜1080p** までで、4K/HDR は SDR に再エンコードされ配信される。
- 推奨入力：MP4 / H.264 high profile / AAC / 30fps以下 / Closed GOP / Fast Start（moov atom 先頭）。
- HDR は対応外（SDR にダウンコンバート）、AV1/VP9 出力なし。
- CSP を設定する場合は `videodelivery.net` と `*.cloudflarestream.com` を `frame-src` / `media-src` / `connect-src` 等に追加する必要がある。
- サブスク解約後 **30日** で動画は削除される。
- 保存枠を使い切ると新規アップロードが拒否される（エンタープライズは継続可）。
- DRM は標準では提供されないため、有料コンテンツ保護は Signed URL ベースとなる。
- PageSpeed Insights では複数プレイヤ埋め込み時にスコア低下する傾向があるため、lazy loading またはサムネイル先行表示を推奨。

## 参考リンク
- 公式ドキュメント: https://developers.cloudflare.com/stream/
- 料金: https://developers.cloudflare.com/stream/pricing/
- FAQ: https://developers.cloudflare.com/stream/faq/
- Live Input: https://developers.cloudflare.com/stream/stream-live/
- Direct Creator Uploads: https://developers.cloudflare.com/stream/uploading-videos/direct-creator-uploads/
- Signed URLs: https://developers.cloudflare.com/stream/viewing-videos/securing-your-stream/

---
参照日: 2026-05-03
