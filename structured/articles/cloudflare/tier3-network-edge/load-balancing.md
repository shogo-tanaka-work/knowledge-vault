# Load Balancing

## 一行サマリ
複数のオリジン（マルチクラウド・マルチリージョン・マルチデータセンター）を Pool 単位で束ね、Cloudflare のグローバルエッジ網からヘルスチェック・地理・レイテンシ・接続数を軸にトラフィックを振り分ける GSLB（Global Server Load Balancer）兼アプリケーション LB である。

## 解決する課題（Why）
クラウド・データセンターを跨いだ可用性設計を、自前の DNS や IaaS LB だけで成立させるのは年々苦しくなっている。Route 53 や Azure Traffic Manager は GSLB として機能するが、エッジでのヘルス検知の鮮度・グローバルプロキシ統合・WAF / Bot との一体運用は別問題として残る。Cloudflare Load Balancing は同社のエッジ網（330+ PoP）に統合された GSLB として、以下の課題を一枚岩で扱う。

- マルチクラウド active-active 構成（AWS + GCP / オンプレ + クラウド）の宛先振り分けと自動フェイルオーバー。
- リージョン障害・オリジン障害発生時の DNS TTL に縛られないフェイルオーバー（Proxied モードでは TTL 概念が消える）。
- 地理・レイテンシに基づく最寄りリージョンへのルーティング（GSLB / GeoDNS 相当）。
- ヘルスチェックを世界各地の Cloudflare PoP から多点で実施し、単一 Probing PoP の偏りを排除。
- WAF / CDN / Bot Management / Rate Limiting と同一プレーンでのトラフィック制御。
- L7（HTTP/HTTPS）に加え、Spectrum 連携で L4（TCP/UDP）の GSLB も同様に扱える。

## 主要機能（What）

### Pools & Endpoints
**Pool** は複数 **Endpoint**（旧称 Origin。実体は IP / ホスト名で表されるオリジンサーバー）をひとまとめにした論理グループである。Pool 単位に Health Monitor を貼り、Pool 単位にステータス（Healthy / Degraded / Critical）が決まり、Load Balancer から Pool への振り分けと、Pool 内の Endpoint への振り分けが二段で行われる。

- **Pool = リージョン or クラウド単位**（例：`pool-aws-tokyo`, `pool-gcp-osaka`, `pool-onprem-dc1`）が定石。
- 各 Endpoint には Weight・Virtual Network ID（Tunnel 経由の場合）・Header Override 等を付与できる。
- Pool は Account 単位で再利用可能（複数 Load Balancer から共通 Pool を参照できる）。
- Pool 内の Endpoint 健全数が Minimum Origins を下回ると Pool 自体が Unhealthy 扱いとなり、上位の Traffic Steering が次の Pool にフェイルオーバーする。

### Health Monitors
Pool に紐付けるアクティブヘルスチェック。世界各地の Cloudflare データセンターから定期 Probe を投げ、複数 PoP の合議で判定するため、単一拠点からの誤検知を抑えられる。

- **Type**：HTTP / HTTPS / TCP / UDP-ICMP / ICMP-Ping / SMTP。
- **Selector 相当**：Path / Method / Expected Codes / Expected Body / Custom Header / Host Header / Port / Follow Redirects / Allow Insecure (TLS 検証無効化) / Probe Zone（どの Zone のレピュテーションで Probe するか）。
- **Interval**：60 秒以上が一般的（Free / Pro 制約）。Enterprise は短縮可能。
- **Consecutive up / down**：何回連続成功・失敗で状態遷移するかの閾値。チャタリング抑制の要。
- **Probe Regions**：WNAM / ENAM / WEU / EEU / NSAM / SSAM / OC / ME / NAF / SAF / SEAS / NEAS のうち選択。`Probe All Regions` で全 PoP から検査も可能（Enterprise）。
- 失敗時には **Notification**（Webhook / Email / PagerDuty 連携）を送出。

### Origin Steering（Pool 内の Endpoint 振り分け）
1 つの Pool に複数 Endpoint がある場合、Pool 内でどの Endpoint に流すかを決める方式。

| 方式 | 動作 | 使い所 |
|---|---|---|
| **Random（重み付きラウンドロビン）** | Endpoint Weight に従って確率的に振り分け | 既定値。一般的な水平分散・カナリアリリース（重み 95/5 等） |
| **Hash** | クライアント IP のハッシュで Endpoint を決定 | DNS-only モードでの簡易セッション固定。ECS 設定により粒度調整 |
| **Least Outstanding Requests (LOR)** | 各 Endpoint への未完了リクエスト数 × 重みで最も負荷の低い Endpoint へ | Proxied のみ。リクエスト処理時間にばらつきがある API バックエンド |
| **Least Connections** | 各 Endpoint へのアクティブ接続数で最少を選択 | Proxied のみ。WebSocket / SSE / 長時間接続が混在するワークロード |

LOR と Least Connections は Cloudflare のエッジが各 Endpoint への流量を実測している必要があるため、**DNS-only モードでは選択不可**である。

### Traffic Steering（Pool 間の振り分け）
Load Balancer 単位で、どの Pool に振り分けるかを決める方式。Pool 内の Endpoint 振り分け（Origin Steering）と階層が分かれている点に注意。

| 方式 | 動作 | DNS-only | Proxied | 使い所 |
|---|---|:---:|:---:|---|
| **Off（Failover Order）** | Pool リストの順序通り。先頭 Pool が Healthy ならそこへ全振り、Unhealthy で次へ | ○ | ○ | active-passive。DR 用 |
| **Random** | Pool Weight に基づき確率分散 | ○ | ○ | リージョン横断のラフな A/B |
| **Geo（Region）** | 訪問者の地域（13 リージョン）と Pool のマッピングに従う | ○ | ○ | 「APAC からは Tokyo Pool、EU からは Frankfurt Pool」 |
| **Country（Geo Country）** | ISO 国コード単位でのマッピング | ○ | ○ | データレジデンシー（DE 国民は EU Pool 限定など） |
| **Proximity（GeoCoordinate）** | 訪問者の地理座標から Pool の Lat/Lng への球面距離で最寄りを選択 | ○ | ○ | 国境より物理距離が支配的なワークロード |
| **Dynamic（Latency）** | Cloudflare が継続測定する Pool ごとのレイテンシで最速を選択 | ○ | ○ | クラウド間で実効レイテンシが変動するケース |
| **Least Outstanding Requests** | Pool 単位の未完了リクエスト数で最少を選択 | × | ○ | Pool（リージョン）間で処理時間が偏る API |
| **Least Connections** | Pool 単位のアクティブ接続数で最少を選択 | × | ○ | 長時間接続が多いリアルタイム系 |

DNS-only モードでは **EDNS Client Subnet (ECS)** をリゾルバが付与してくれる場合に限り、Geo / Proximity / Country が訪問者単位で機能する。`location_strategy.prefer_ecs` で ECS の優先度を制御できる。

### Session Affinity（スティッキーセッション）
同一クライアントを同じ Endpoint に固定する仕組み。**Proxied モードでのみ動作**（DNS-only では DNS Persistence で代替）。

- **Cookie Only**：`__cflb` を Cloudflare が発行して Endpoint を覚える。デフォルト TTL 23 時間。HttpOnly / Secure 付与。
- **Cookie + Client IP Fallback**：Cookie が無い初回はクライアント IP ハッシュで決定論的に振り分け。Cookie 取得後は Cookie 優先。
- **HTTP Header**：指定ヘッダ値で固定。`require_all_headers` を有効化するとすべての指定ヘッダ揃いを要求。**Sticky Zero-Downtime Failover は非対応**。
- 不健全になった Endpoint からは自動的に他 Endpoint に再ルーティング。**Session Drain**（メンテ時にセッション維持しつつ新規振り分けを止める）も Endpoint 単位で操作可能。

### Adaptive Routing（フェイルオーバー強化）
ルーティングの動的補正機能。2 つの設定からなる。

- **Hash sessions for failover affinity**：Pool 内 Endpoint のフェイルオーバー時、同一クライアントが同じ代替 Endpoint に行くようハッシュで固定。
- **Failover across pools**：521 / 522 / 523 / 525 / 526 など Cloudflare ⇄ Origin 間エラー発生時、別 Pool に**1 回だけ即時リトライ**。Healthy な代替 Pool が必要。

ヘルスモニタが Critical 判定する前の「最初の 1 リクエスト失敗」を救う性質で、ユーザー体感の可用性に効く。

### Layer 4 LB（Spectrum 連携）
HTTP/HTTPS 以外の TCP / UDP プロトコル（SSH / SMTP / Minecraft / 任意の独自プロトコル）に対しては **Spectrum** が L4 プロキシとして手前に立ち、その配下に Load Balancing の Pool / Monitor / Steering を組み合わせる構成になる。

- Health Monitor の TCP / UDP-ICMP / SMTP タイプはこの L4 構成のためにある。
- ただし **Custom Rules は Spectrum と非互換**で、L7 のリクエスト属性ベースのルーティングはできない。
- 料金は Spectrum 側（Enterprise）と Load Balancing 側の両方が発生する。

### Custom Rules
リクエスト属性に応じて Load Balancer の挙動を上書きするルール群。

- **Expression**：URI パス / Host / ヘッダ / Cookie / Country / ASN など Cloudflare Rules engine と同等の式。
- **Action**：Pool 上書き（特定 Pool へ強制）、Steering Policy 上書き、Session Affinity 上書き、TTL 上書き、Fixed Response（メンテページ等）。
- **典型ユースケース**：`/api/*` は API Pool、`/static/*` は CDN Origin Pool、特定国は Sorry ページ、Beta ユーザー（Cookie）は Canary Pool、など。
- 制約：**非 Enterprise は LB ホスト名あたり 1 ルール**、**Geo Steering と相互排他**、**Spectrum と非互換**。

### DNS-only LB vs Proxied LB
| 観点 | DNS-only（gray cloud） | Proxied（orange cloud） |
|---|---|---|
| 仕組み | Cloudflare DNS が Healthy Pool の A/AAAA を返す | Cloudflare エッジが TCP/TLS を終端しオリジンへ proxy |
| TTL | 設定 TTL に依存（フェイルオーバー反映が遅い） | TTL 概念なし（即時フェイルオーバー） |
| Session Affinity | × | ○ |
| LOR / Least Connections | × | ○ |
| Custom Rules | × | ○ |
| Adaptive Routing | × | ○ |
| WAF / Bot / Cache 連携 | × | ○ |
| 任意プロトコル | ○（DNS だけなので何でも） | HTTP/HTTPS のみ（L4 は Spectrum 併用） |
| 料金 | 安い | Proxy トラフィック費用が乗る |

「TTL 縛りを外したい」「セッション固定が要る」「WAF と連動させたい」なら Proxied 一択、「とにかく軽量に GSLB だけ欲しい」「HTTP 以外を扱いたい」なら DNS-only、と判断軸を分けるのが現実解。

## アーキテクト視点：いつ選ぶか

### 適しているシーン
- AWS / GCP / Azure / オンプレを跨いだ active-active マルチクラウド構成。とくに既に Cloudflare をリバースプロキシとして前段に置いている組織。
- リージョン障害時のフェイルオーバー RTO を **DNS TTL より短く**したい SaaS（Proxied + Adaptive Routing）。
- 「東京・大阪・シンガポール」のような複数リージョン active-active で、ユーザー位置に応じた最寄り PoP を選びたいケース（Dynamic / Proximity）。
- データレジデンシー要件で「DE のユーザーは EU 内 Origin に固定したい」ケース（Country Steering）。
- API バックエンドが処理時間に偏りを持ち、単純なラウンドロビンで詰まりが起きるケース（Least Outstanding Requests）。
- WebSocket / SSE / 長時間接続混在のリアルタイムサービス（Least Connections）。
- 既に WAF / CDN / Bot Management を Cloudflare に集約している組織。LB だけ別ベンダーにするより一体管理が効率的。

### 適していないシーン
- 単一リージョン active-passive で済むワークロード。Route 53 Failover や Azure Traffic Manager で十分でコストも安い。
- 既存 NS1 / F5 BIG-IP DNS / Akamai GTM に深く投資済みで、Real User Monitoring（RUM）ベースの精緻な GSLB 運用ができている組織。Cloudflare の Steering は十分高機能だが、RUM ベース GSLB の細密さでは NS1 / Akamai に劣るケースがある。
- オリジンが完全に Cloudflare 配下（Workers / R2 / D1）で完結する場合は LB 不要。Workers のリージョンレス実行と Smart Placement で代替できる。
- マルチクラスター Kubernetes の east-west トラフィックを GSLB したいケース。これは Service Mesh（Istio / Linkerd / Cilium Cluster Mesh）の領分で、Cloudflare LB は south-north 専用と割り切る。

## 競合・代替

| 観点 | Cloudflare Load Balancing | AWS Route 53 (ARC) | NS1 (IBM) | F5 BIG-IP DNS (旧 GTM) | Akamai GTM | Azure Front Door |
|---|---|---|---|---|---|---|
| 出自 | グローバル CDN/Anycast | AWS マネージド DNS | 純血 Managed DNS / GSLB 専業 | オンプレアプライアンス GSLB | グローバル CDN GSLB | Microsoft マネージド ADC |
| プロキシ統合 | ○（同一エッジで proxy） | ×（DNS のみ。CloudFront 別物） | ×（DNS のみ） | △（BIG-IP LTM 併用） | ○（CDN と統合） | ○（Front Door L7） |
| RUM ベース GSLB | △（Dynamic はエッジ計測） | × | ○（Pulsar） | ○ | ○（mPulse 連携） | △ |
| 健康監視 PoP 数 | 330+ PoP から多点 | 限定リージョン | グローバル | 自前構築 | グローバル | Microsoft 網 |
| L4 / 任意プロトコル | ○（Spectrum 併用） | ○（DNS なら何でも） | ○ | ○ | △ | △（HTTP 中心） |
| 料金モデル | $5/月 + 従量 | $0.50/zone + クエリ + ヘルスチェック | 高い（要見積） | ライセンス（高額） | エンタープライズ契約 | $35/月 + 従量 |
| 強み | エッジ統合・WAF/CDN 一体・即時フェイルオーバー | AWS 内サービス連携・低単価 | RUM ベース・DNS 専門ノウハウ | オンプレ・カスタムロジック自由度 | 大規模配信網との一体運用 | Azure 内サービス連携 |
| 弱み | RUM 精緻さは GTM 系に劣る | プロキシ統合無し・反映が TTL 縛り | 価格・他クラウド統合は手作業 | クラウドネイティブ性に乏しい | 高コスト・小規模に向かない | Azure 外連携は弱い |

Cloudflare の差別化は「**LB が CDN / WAF / Bot / Tunnel と同じデータプレーン上に座っている**」点に尽きる。GSLB 単機能比較では NS1 / Akamai GTM のほうが歴史と精度で勝る場面はあるが、運用面の統合性とコスト効率では Cloudflare に分がある。

## 料金
- **Pro / Business / Enterprise プランへのアドオン**：基本料金 **$5/月** から。
- **従量課金**：
  - **DNS Queries / Proxy Requests**：標準プランで月 50 万クエリ込み、超過分は約 $0.50 / 100 万クエリ。
  - **Health Checks**：1 Endpoint あたり月 1 ドル前後（Probe Region 数・Interval に依存）。
  - **追加 Endpoint / Pool**：標準枠を超えた分は超過課金。
- **Enterprise 契約**：年間契約の総額に組み込まれ、上記単価は交渉対象。Probe All Regions・短い Interval・大量 Endpoint・Custom Rules 複数対応はここで現実的になる。
- **Spectrum との併用（L4）**：Spectrum 自体が Enterprise 機能で別料金。L4 LB をやるなら実質 Enterprise 前提。

「LB だけ単独で買う」より、Pro / Business で WAF や CDN を併用しているサイトに **$5 + 数ドル**で乗せられる手軽さが、競合との実コスト比較で効いてくる。

## CLI / API 例

### Health Monitor 作成
```bash
curl -X POST "https://api.cloudflare.com/client/v4/accounts/${ACCOUNT_ID}/load_balancers/monitors" \
  -H "Authorization: Bearer ${CF_API_TOKEN}" \
  -H "Content-Type: application/json" \
  --data '{
    "type": "https",
    "description": "API healthcheck",
    "method": "GET",
    "path": "/healthz",
    "expected_codes": "200",
    "expected_body": "ok",
    "interval": 60,
    "timeout": 5,
    "retries": 2,
    "consecutive_up": 2,
    "consecutive_down": 3,
    "follow_redirects": false,
    "allow_insecure": false,
    "probe_zone": "example.com",
    "header": { "Host": ["api.example.com"] }
  }'
```

### Pool 作成（AWS Tokyo に 2 Endpoint、LOR で振り分け）
```bash
curl -X POST "https://api.cloudflare.com/client/v4/accounts/${ACCOUNT_ID}/load_balancers/pools" \
  -H "Authorization: Bearer ${CF_API_TOKEN}" \
  -H "Content-Type: application/json" \
  --data '{
    "name": "pool-aws-tokyo",
    "description": "AWS ap-northeast-1 origins",
    "enabled": true,
    "minimum_origins": 1,
    "monitor": "'"${MONITOR_ID}"'",
    "origins": [
      { "name": "tokyo-1", "address": "203.0.113.10", "weight": 1, "enabled": true },
      { "name": "tokyo-2", "address": "203.0.113.11", "weight": 1, "enabled": true }
    ],
    "origin_steering": { "policy": "least_outstanding_requests" },
    "latitude": 35.68,
    "longitude": 139.76,
    "notification_email": "ops@example.com"
  }'
```

### Load Balancer 作成（Proxied / Dynamic Steering / Adaptive Routing 有効）
```bash
curl -X POST "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/load_balancers" \
  -H "Authorization: Bearer ${CF_API_TOKEN}" \
  -H "Content-Type: application/json" \
  --data '{
    "name": "api.example.com",
    "description": "Multi-region API LB",
    "enabled": true,
    "proxied": true,
    "ttl": 30,
    "steering_policy": "dynamic_latency",
    "default_pools": ["'"${POOL_TOKYO}"'", "'"${POOL_OSAKA}"'", "'"${POOL_GCP_OSAKA}"'"],
    "fallback_pool": "'"${POOL_TOKYO}"'",
    "session_affinity": "cookie",
    "session_affinity_ttl": 1800,
    "session_affinity_attributes": { "samesite": "Auto", "secure": "Auto", "drain_duration": 60 },
    "adaptive_routing": { "failover_across_pools": true },
    "rules": [
      {
        "name": "static to cdn pool",
        "condition": "starts_with(http.request.uri.path, \"/static/\")",
        "overrides": { "default_pools": ["'"${POOL_CDN}"'"] }
      }
    ]
  }'
```

### Terraform（cloudflare provider v5）
```hcl
resource "cloudflare_load_balancer_pool" "tokyo" {
  account_id        = var.account_id
  name              = "pool-aws-tokyo"
  minimum_origins   = 1
  monitor           = cloudflare_load_balancer_monitor.api.id
  origins {
    name    = "tokyo-1"
    address = "203.0.113.10"
    weight  = 1
    enabled = true
  }
  origin_steering { policy = "least_outstanding_requests" }
  latitude  = 35.68
  longitude = 139.76
}

resource "cloudflare_load_balancer" "api" {
  zone_id          = var.zone_id
  name             = "api.example.com"
  proxied          = true
  steering_policy  = "dynamic_latency"
  default_pool_ids = [cloudflare_load_balancer_pool.tokyo.id, cloudflare_load_balancer_pool.osaka.id]
  fallback_pool_id = cloudflare_load_balancer_pool.tokyo.id
  session_affinity = "cookie"
  adaptive_routing { failover_across_pools = true }
}
```

## 制限・注意点
- **Session Affinity / Custom Rules / LOR / Least Connections / Adaptive Routing は Proxied 専用**。DNS-only モードでは選択できない。要件に Affinity が含まれるなら Proxied 前提で zone を設計する。
- **Custom Rules は非 Enterprise だと「LB ホスト名あたり 1 ルール」に制限**される。本格的にパスベース・ヘッダベースで Pool を切るなら Enterprise を見込む。
- **Custom Rules と Geo Steering は相互排他**。両方使いたい場合は Custom Rules の中で Pool 上書きをして Geo を再現する。
- **Spectrum と Custom Rules は非互換**。L4 LB ではリクエスト属性ベースの分岐はできない。
- **Health Monitor の Interval を短くする**と Probe トラフィックが Origin 側に乗る。Origin の `/healthz` は軽量・キャッシュなしで設計する。
- **Probe Region を狭める**と単一 PoP 障害が誤検知に直結する。本番は最低 3 リージョン以上を推奨。
- DNS-only モードでの Geo / Proximity / Country は **ECS が無いと Resolver IP の地理位置で判定**されるため、Public Resolver（1.1.1.1 / 8.8.8.8）経由のユーザーで意図しない Pool に振られる可能性がある。`location_strategy` の調整が必要。
- `__cflb` Cookie は HttpOnly のため、フロントエンドの JS からは触れない。SPA からはユーザー識別子を別途持つ必要がある。
- **TTL 縛り問題（DNS-only）**：DNS TTL を 30 秒にしてもキャッシュリゾルバ次第で守られない。RTO が秒単位なら Proxied を選ぶ。
- Adaptive Routing の `Failover across pools` は **Cloudflare ⇄ Origin 系のエラー（5xx の特定コード）にだけ反応**する。アプリ層の 500 では発火しないため、ヘルスチェックの応答ボディ検査と組み合わせて欠損を埋める。
- マルチアカウント運用では Pool / Monitor は Account スコープ、Load Balancer は Zone スコープという階層を意識する。Pool を別 Account から共有することはできない。

## 参考リンク
- Cloudflare Load Balancing Overview：https://developers.cloudflare.com/load-balancing/
- Pools：https://developers.cloudflare.com/load-balancing/pools/
- Monitors：https://developers.cloudflare.com/load-balancing/monitors/
- Traffic Steering：https://developers.cloudflare.com/load-balancing/understand-basics/traffic-steering/
- Steering Policies：https://developers.cloudflare.com/load-balancing/understand-basics/traffic-steering/steering-policies/
- Session Affinity：https://developers.cloudflare.com/load-balancing/understand-basics/session-affinity/
- Adaptive Routing：https://developers.cloudflare.com/load-balancing/understand-basics/adaptive-routing/
- Custom Rules：https://developers.cloudflare.com/load-balancing/additional-options/load-balancing-rules/
- Cloudflare Spectrum（L4 LB 連携）：https://developers.cloudflare.com/spectrum/
- Load Balancing API：https://developers.cloudflare.com/api/operations/load-balancers-list-load-balancers
- Terraform `cloudflare_load_balancer`：https://registry.terraform.io/providers/cloudflare/cloudflare/latest/docs/resources/load_balancer
- Load Balancing llms.txt：https://developers.cloudflare.com/load-balancing/llms.txt

---
参照日: 2026-05-04
