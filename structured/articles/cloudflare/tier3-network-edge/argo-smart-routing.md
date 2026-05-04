# Argo Smart Routing

## 一行サマリ
オリジンへ向かうトラフィックを、Cloudflareが自社網内で観測しているリアルタイムの遅延・パケットロス・輻輳情報に基づいて経路選定し、BGPの「最短ホップ」よりも体感的に速い経路でオリジンに届けるエッジ層のオーバーレイルーティングサービスである。

## 解決する課題（Why）
インターネットの基本ルーティングプロトコルであるBGPは、AS間の到達性と経路ポリシーを成立させることが目的であり、遅延・ジッタ・パケットロスといった「実効的な速さ」を最適化する仕組みを持たない。結果として、AS数が少ない（ホップ数が短い）経路が選ばれても、そのASがピーク時間帯に輻輳していればRTTは悪化する。さらに以下のような構造的な問題が常態化している。

- ピアリング先のトランジットが混雑し、特定リージョン⇔オリジン間だけ夜間に遅くなる。
- 海底ケーブル障害でルートが切り替わった際、BGP収束まで数十秒〜数分のロスが発生する。
- DSR（直接サーバ応答）的なIP Anycastだけでは、最寄りエッジから先（エッジ→オリジン区間）のラストマイルを最適化できない。
- 動的コンテンツ（API・パーソナライズページ）はキャッシュできず、オリジン往復のRTTがそのまま体感速度になる。

Argo Smart Routingはこれを「Cloudflareが自社で計測しているエッジ間・エッジ→オリジン間の実遅延データ」を使って解決する。Cloudflareは1秒あたり数千万〜億単位のリクエストを世界中のPoPで処理しており、その実測値からアグリゲートされたヒートマップを使って、利用者ごとに最適な中継PoP経由の経路を選ぶ。

## 主要機能（What）

### Smart Routing（経路選定）
クライアント↔最寄りエッジは通常のAnycastで処理し、エッジ↔オリジンの区間をCloudflareバックボーンとPoP網を介して中継する。具体的には、リクエストを受けたPoPがオリジン直接へ抜けるのではなく、別の混雑していない中継PoPを経由してオリジン側ASに最も近いPoPから抜ける、という「Cloudflare網内での迂回」を選択する。

- 経路選定の単位はオリジンASおよび宛先プレフィックス。
- 中継PoPは数十ms単位で更新されるレイテンシテーブルから選ばれる。
- TCP / TLSセッションはCloudflare網内では再利用され、コネクション確立コストが圧縮される。

### リアルタイム遅延計測
Cloudflareは公称で1秒あたり9300万HTTPリクエスト規模を世界中のエッジで処理しており、その全体から得られるTTFB（Time to First Byte）・RTT・再送率をリアルタイムに集計し、PoP↔オリジンの実効レイテンシマトリクスを維持している。Argoはこのマトリクスを参照し、宛先ASに対して「いま最も速いPoP出口」を選ぶ。

- 計測は通常トラフィックそのものを使うパッシブ計測が主体。能動プローブも補助的に使われる。
- 障害（特定区間のパケロス急増・RTT急増）を検知すると、BGPの収束を待たずに迂回経路へ切り替わる。

### Tiered Cache との連動
Argo Smart Routingはオリジン到達のためのオーバーレイであり、Tiered Cacheはキャッシュ階層を組むことで上位PoPにキャッシュを集約し、オリジンへのリクエスト数自体を減らす機能である。両者は別契約・別目的だが、Tiered Cacheの「上位PoP→オリジン」の区間にArgo Smart Routingが効くため組合せると効果が乗る。

- Tiered Cacheは下位PoP→上位PoP→オリジンの三段構成でキャッシュヒット率を底上げする。
- 上位PoPからオリジンへ抜ける区間でArgoが最速経路を選ぶことで、キャッシュミス時のTTFBが短縮される。
- 静的コンテンツ中心ならまずTiered Cache、APIや動的コンテンツが多いならArgoから先に効く、という使い分けになる。

### RTT 削減効果
Cloudflareの公称ベンチマークでは、Argo Smart Routing有効時にWebアプリのパフォーマンスが平均30%改善する。実測ダッシュボードでは「Argo経由 vs Argo未経由」のTTFBヒストグラムと、PoPごとの遅延改善ヒートマップ（負値＝Argoを通さない方が速いリージョン）が確認できる。詳細メトリクスは過去48時間に500リクエスト以上Argo経由で処理されている場合に表示される。

## アーキテクト視点：いつ選ぶか

### 適しているシーン
- グローバル展開しているSaaSのAPIゲートウェイ。動的コンテンツでキャッシュが効かず、世界中からのRTTがそのままUXに直結する。
- 動画配信・SNS・チャットなどリアルタイム性の高いアプリケーション（Discord事例で平均33msの短縮実績）。
- オリジンが少数リージョンに集中しており、遠隔地ユーザーのRTTが国内ユーザーの数倍になっているケース。マルチリージョンで再構築するよりArgoの方が圧倒的に安く速い。
- 既にCloudflareプロキシ配下（オレンジクラウド）で運用しているサービスで、追加投資なしにラストマイル最適化を入れたい。
- 海底ケーブル障害・トランジット切替の影響を受けやすい地域（南米・アフリカ・東南アジア）への配信。

### 適していないシーン
- 静的アセットがほぼ100%でキャッシュヒット率が極めて高いサイト。Argoが効くのはキャッシュミスでオリジン往復する局面に限られるため、まずTiered Cache / Cache Reserveを優先する。
- オリジンが単一リージョンかつユーザーも同地域に集中しているケース。BGP最短経路と実効最速経路の差が小さいので投資対効果が薄い。
- Cloudflareプロキシを通さない構成（DNS Onlyのグレークラウド）。Argoはプロキシ前提なので有効化しても通らない。
- 大量の攻撃トラフィックを受けているサイト。WAF / DDoSで遮断されたトラフィックはArgoの課金対象外だが、正当トラフィックの帯域が大きい場合は従量コストが想定外に膨らむことがある。

## 競合・代替

| 観点 | Cloudflare Argo Smart Routing | AWS Global Accelerator | Fastly Network Services | Akamai SureRoute | GCP Premium Tier |
|---|---|---|---|---|---|
| 出自 | CDN網のオーバーレイルーティング | AWS Anycast + Global Network | Fastly POP網内最適化 | CDN動的サイトアクセラレーション | GCP Premium Networkバックボーン |
| 経路選定の根拠 | 実トラフィックのレイテンシ実測 | AWSグローバルバックボーンのSLA | Fastly内部メトリクス | 複数代替経路を並列試行（race） | GCPバックボーン優先 |
| 適用対象 | エッジ↔オリジン区間 | クライアント↔ALB / NLB / EC2 | エッジ↔オリジン区間 | エッジ↔オリジン区間 | クライアント↔GCPリソース |
| キャッシュ統合 | Tiered Cacheと連携 | 該当なし（CloudFrontは別） | Fastly CDNと統合 | Akamai CDNと統合 | Cloud CDNと統合 |
| 料金 | $5/月 + リクエスト・帯域従量 | $0.025/時間 + データ転送 | プラン込み・要見積もり | 要見積もり（高額） | データ転送に上乗せ |
| 強み | 実測ベース・無設定で効く | AWSサービスとの統合・固定IP | 細かい設定が可能 | 大企業向け実績 | GCP内通信が高速 |
| 弱み | Cloudflareプロキシ前提 | AWSロックイン・コスト高 | Fastly利用前提 | 高コスト・契約プロセス重い | GCP外への効果は限定的 |

Argoの差別化はシンプルさにある。1クリックで有効化し、コードもインフラも変更せずにグローバルRTTが平均30%改善する、という「他に選択肢がないレベルの低い導入摩擦」が最大の価値である。AWS Global Acceleratorはクライアント側のAnycast IP取得が主目的なので、性質が異なる比較対象になる。

## 料金

- **基本料金**：$5/月の固定料金。
- **従量課金**：Argo経由で処理されたリクエスト数および帯域に応じた従量。WAF / DDoS / Bot Managementで軽減された攻撃トラフィックは課金対象外。
- **Enterprise**：年間契約に含まれるプレビュー・割引枠あり。商談ベース。
- **請求プロファイル必須**：有効化前にBillingプロファイルを登録する必要がある。

Cloudflareダッシュボードの「Notifications → Usage Based Billing」で閾値超過アラートを設定するのが運用上の必須項目。動的トラフィックが急増したサービスでは月額が想定の数倍に振れることがあるため、最初からアラート前提で組む。

## CLI / API 例

### REST API（Zone Setting）
```bash
# Argo Smart Routingを有効化
curl -X PATCH \
  "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/argo/smart_routing" \
  -H "Authorization: Bearer ${CF_API_TOKEN}" \
  -H "Content-Type: application/json" \
  --data '{"value":"on"}'

# 現在の状態確認
curl -X GET \
  "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/argo/smart_routing" \
  -H "Authorization: Bearer ${CF_API_TOKEN}"

# 無効化
curl -X PATCH \
  "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/argo/smart_routing" \
  -H "Authorization: Bearer ${CF_API_TOKEN}" \
  -H "Content-Type: application/json" \
  --data '{"value":"off"}'
```

### Terraform（cloudflare provider v5）
```hcl
resource "cloudflare_argo_smart_routing" "this" {
  zone_id = var.zone_id
  value   = "on"
}
```

### 効果計測
有効化後48時間以上経過し、Argo経由のリクエストが500件を超えると、ダッシュボードの`Analytics → Performance`にTTFBヒストグラムとPoPごとの遅延改善ヒートマップが表示される。負値（青）は「Argoを通さない方が速い」リージョンを意味するため、定期的に確認して期待効果を検証する。

## 制限・注意点
- **Cloudflareプロキシ配下が前提**：DNS Only（グレークラウド）レコードには効かない。プロキシ済み（オレンジクラウド）であることを必ず確認する。
- **キャッシュヒットには寄与しない**：Argoはオリジン到達経路の最適化であり、エッジでキャッシュヒットしているリクエストには関与しない。キャッシュ可能なコンテンツはまずCache Rules / Tiered Cache / Cache Reserveで詰める。
- **WebSocket / 長時間コネクション**：基本的に効くが、コネクション確立後の経路は固定される。経路変動の恩恵を受けるのは新規接続。
- **従量コストの予見性が低い**：トラフィックバーストでコストが跳ねるため、Usage Based Billing通知の設定は必須。
- **Argo Tunnelは別物・廃止済み**：かつて`argo-smart-routing/argo-tunnel/`配下に存在した「Argo Tunnel」は、2021年にCloudflare Tunnelへ統合・名称変更され、無料化された。現在`cloudflared`デーモンで動かしているTunnelの実体がそれであり、Argo Smart Routing（本記事）とは別契約・別課金。混同が多いので設計レビューでは必ず分離して説明する。
- **オリジン側の対応は不要**：Cloudflareから見えるオリジンIPが変わるわけではないため、オリジン側のFWルール変更は不要。ただしCloudflare IPレンジの許可リストは最新版を参照。
- **Enterprise契約での無料プレビュー**：Enterpriseプランには一定期間の無料プレビュー枠が用意されることがある。営業経由で確認する。

## 参考リンク
- Argo Smart Routing 公式：https://developers.cloudflare.com/argo-smart-routing/
- Get Started：https://developers.cloudflare.com/argo-smart-routing/get-started/
- Analytics：https://developers.cloudflare.com/argo-smart-routing/analytics/
- 製品ページ：https://www.cloudflare.com/application-services/products/argo-smart-routing/
- Tiered Cache：https://developers.cloudflare.com/cache/how-to/tiered-cache/
- Cloudflare Tunnel（旧Argo Tunnel）：https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/
- API Reference（Argo Smart Routing）：https://developers.cloudflare.com/api/operations/argo-smart-routing-patch-smart-routing-setting

---
参照日: 2026-05-04
