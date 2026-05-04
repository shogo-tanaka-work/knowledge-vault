# Cache (Cache Rules / Cache Reserve / Tiered Cache)

## 一行サマリ
Cloudflareエッジで静的・準静的リソースを各PoPに保持し、Cache Rulesでキャッシュ条件とTTLを宣言、Tiered Cacheで上位ティアに集約してオリジン負荷を削り、Cache ReserveでR2上に長期退避させる、エッジキャッシュ層の総体である。

## 解決する課題（Why）
オリジンサーバーは「同じレスポンスを世界中のユーザーに何度も返す」ために計算リソース・帯域・コストを浪費し、トラフィック急増時には真っ先にスケール限界に当たる。さらに、各PoPが個別にオリジンへフェッチする素朴なCDNでは、エッジが200拠点以上に分散しているほどキャッシュミス率が悪化し、オリジンへの「広く浅い負荷」が消えない。Cloudflare Cacheはこれをエッジ・上位ティア・永続ストアの三段構えで解決する。

- グローバルに分散したPoPでの応答による初回TTFB短縮とオリジン負荷削減。
- Tiered Cacheによる上位ティア集約で、オリジンへの重複フェッチを構造的に削る。
- Cache ReserveでLRU退避を回避し、長尾コンテンツも常時エッジ近傍から配信。
- Cache RulesでURL・Cookie・デバイス・ステータスコード等の条件で宣言的にキャッシュ戦略を分岐。
- Always Onlineでオリジン障害時もキャッシュ済みコンテンツを継続配信。
- Purge API・Cache Tag・Stale-While-Revalidateで「鮮度」と「可用性」のトレードオフを運用可能に。

## 主要機能（What）

### Cache Rules
URL・ホスト・リクエストヘッダ・Cookie・デバイスタイプ等のマッチャに対して、キャッシュ可否・TTL・キャッシュキー・Origin Cache Controlの優先順位を宣言する仕組みである。旧Page Rulesの後継で、評価順序（precedence）と複数条件のAND/ORを明示できる。

- **設定可能アクション**：Eligible for cache（キャッシュ対象化）、Edge TTL、Browser TTL、Custom Cache Key、Cache Reserve eligibility、Bypass Cache on Cookie、Origin Cache Controlの尊重可否、Serve Stale Content、Respect Strong ETags など。
- **マッチャ**：`http.host`、`http.request.uri.path`、`http.request.uri.query`、`http.cookie`、`http.user_agent`、`ip.geoip.country`、`http.request.headers["x-foo"]` などRulesetエンジンの全式が利用可能。
- **ルール上限**：Free 10 / Pro 25 / Business 50 / Enterprise 300（プラン依存）。
- **API / Terraform**：Rulesets API（phase: `http_request_cache_settings`）で操作する。Terraformは `cloudflare_ruleset` リソースで宣言。

### Cache Keys & TTL
Cloudflareは既定で「URL（クエリ含む）+ ホスト + スキーム」をキャッシュキーとし、デバイスや言語ヘッダは含めない。Custom Cache Keyを使うと、特定クエリパラメータのみを含める／除外する、Cookie値で分岐する、ヘッダで分岐する、といった粒度設計が可能になる。

- **Edge Cache TTL**：CloudflareのPoPに保持する時間。Cache Rulesで明示するか、`Cache-Control: s-maxage` / `max-age` をオリジンが返すと尊重される。
- **Browser Cache TTL**：ブラウザ側 `Cache-Control: max-age` を上書きする。
- **Cache TTL by status code**：200/301は長め、404/5xxは短めなど、ステータス別TTLを宣言できる。
- **デフォルトTTL**（オリジンがCache-Control未指定の場合）：200/206/301は120分、302/303は20分、404/410は3分。
- **既定キャッシュ対象拡張子**：画像（GIF/PNG/JPEG/WEBP）、動画（MP4/WEBM）、CSS/JS、PDF/DOC等60種類以上。HTML / JSONは既定では非キャッシュ（動的・個別化想定のため）。HTMLをキャッシュする場合はCache Rulesで明示的に「Eligible for cache」を有効化する。
- **Origin Cache Controlとの優先順位**：Cache Rulesで明示したTTLが最優先。次にオリジン `Cache-Control` / `Expires`、最後にCloudflareデフォルト。

### Tiered Cache
全PoPが直接オリジンを叩くのではなく、上位ティアPoPに集約してからオリジンにフェッチする構造である。下位ティアのキャッシュミスは上位ティアでヒットする確率が高く、オリジンRPSを構造的に削減できる。

- **Smart Tiered Cache Topology**：レイテンシデータから動的に最適な単一の上位ティアを選択する。Cloudflareが推奨する構成で、設定はトグル一つ。Pro以上で利用可能（Freeは対象外、後述）。
- **Generic Global Tiered Cache**：複数の上位ティアをグローバルに配置し、遠距離訪問者のレイテンシ削減を優先する。Enterprise向け。
- **Custom Topology**：Enterprise顧客がアカウントチームと協議の上で個別構築する専用トポロジ。
- **リージョンヒント**：オリジンがクラウド（AWS/GCP/Azure）の場合、リージョン指定で上位ティアを地理的に近接させてオリジンRTTを最小化できる。

### Cache Reserve
R2上に構築された永続ストアにキャッシュアセットを退避させ、PoPからのLRU退避を実質的に回避する仕組みである。長尾コンテンツや滅多に呼ばれない大ファイルでも「ほぼ常にキャッシュヒット」状態を維持できる。

- **対象条件**：Cache-Eligibleであること、Edge TTLが10時間以上、`Content-Length` ヘッダ付き、画像変換時はオリジナルのみ。
- **保持期間**：30日間アクセスがなければ削除候補。
- **課金モデル**（R2と類似）：
  - ストレージ：$0.015 / GB-month
  - Class A操作（書き込み、Cache Reserveへの保存）：$4.50 / 100万リクエスト
  - Class B操作（読み出し、エッジミス時の取得）：$0.36 / 100万リクエスト
- **有効化**：ダッシュボードからの単純トグルだが、有料Cache Reserveプランの契約が前提。

### Always Online
オリジンサーバーがダウンした際に、エッジキャッシュ済みのコンテンツを継続配信する機能である。完全に静的なページであれば、オリジン障害中もユーザーには通常運用に見える。Internet Archive連携版（過去にあった機能）は廃止され、現在はCloudflare自身のキャッシュからのみ配信される。Free含む全プランで利用可能だが、効果はキャッシュヒット率に依存する。HTMLをキャッシュ対象にしていない場合、オリジン障害時にAlways Onlineは無力なので、Cache Rulesで主要ページのHTMLキャッシュを明示しておくのが実装上の必須条件である。

### Purge
キャッシュを即時無効化する手段である。粒度別に複数の方式が用意されている。

- **Single-File (URL) Purge**：個別URL指定。最も推奨される細粒度パージ。
- **Purge by Tag**：オリジンが返す `Cache-Tag` ヘッダで束ねたグループ単位。Enterprise機能。
- **Purge by Hostname**：ホスト単位。Enterprise機能。
- **Purge by Prefix**：URLプレフィックス単位。Enterprise機能。
- **Purge Everything**：ゾーン全体。最終手段。
- **レート制限**（プラン別）：
  - Single-File：Free 800 URL/秒、Pro/Business 1,500 URL/秒、Enterprise 3,000 URL/秒。
  - Hostname/Tag/Prefix/Everything：Free 5 req/分、Pro 5 req/秒、Business 10 req/秒、Enterprise 50 req/秒。
- **API**：`POST /zones/{zone_id}/purge_cache` 一本で、ボディに `files` / `tags` / `hosts` / `prefixes` / `purge_everything` を指定。

### Stale-While-Revalidate (SWR)
オリジンが `Cache-Control: stale-while-revalidate=N` を返すと、TTL切れ直後のN秒間は「古いキャッシュを返しつつ、バックグラウンドでオリジン再検証」を行う。ユーザー体験は古いコンテンツでも即時応答、オリジンには再検証リクエスト1本のみ、というキャッシュ理論上の理想状態を作れる。Cache Rulesの `Serve Stale Content` と組み合わせ、オリジンが応答失敗した際に古いキャッシュをフォールバック配信する設計も可能。

### Crawler Hints
コンテンツ更新タイミングを検索エンジンクローラに通知する機能（IndexNow準拠）。クローラが「変更がない時に巡回しない」ことで、オリジンへの不要なクロールトラフィックを削減できる。SEO的なペナルティはなく、有効化トグルのみ。

### Vary for Images
`Accept` ヘッダ（ブラウザのフォーマットサポート情報）を見て、同一URLからWebP / AVIF / JPEGなどブラウザ最適なフォーマットを返す機能である。Cache KeyにAcceptを含める必要があるが、Cloudflare側がVary対応キャッシュキーを自動構築する。Polish / Image Resizing / Imagesと組み合わせて使う前提の機能。

## アーキテクト視点：いつ選ぶか

### 適しているシーン
- 既にCloudflareをDNS / プロキシとして使っており、追加コストゼロでCDN効果を得たいケース。
- 静的サイト・JAMstack・メディアサイトなど、キャッシュ可能率が高いワークロード。
- オリジンがクラウドの単一リージョンにあり、グローバル配信のレイテンシとコストを下げたいケース（Tiered Cache + Smart Topology）。
- 大量の長尾コンテンツ（過去記事・滅多に再生されない動画・地域限定アセット）を抱え、LRU退避でオリジンに戻されると困るケース（Cache Reserve）。
- リリース時の即時無効化が業務要件で、Cache Tagでアトミックに無効化したいCMS / EC（Purge by Tag、Enterprise）。
- オリジンが脆弱（小規模VPS、サーバレスのコールドスタート）で、Always Online + 長めのEdge TTLで耐障害性を補いたいケース。

### 適していないシーン
- すべてのレスポンスがログイン後の個別化コンテンツで、キャッシュキーを設計しても共有キャッシュが成立しない（純粋なSaaS管理画面など）。
- 厳格なリアルタイム性が求められ、SWRや短TTLでも許容できないユースケース（株価ティッカー、ライブスコア。これはWebSocket / SSEで設計すべき）。
- オリジンが既にCDN（CloudFront / Fastly）でフロントされ、Cloudflareをセキュリティ層のみで使う構成。Tiered Cache / Cache Reserveの恩恵が二重CDNで打ち消される。
- 5GB超の単一ファイルを扱う（Enterpriseでも上限5GB、Free/Pro/Businessは512MB）。Stream / R2直配信が現実解。
- HIPAA / 金融など、エッジに個人データを置けない規制要件がある領域。Cache RulesでBypass Cache on Cookieを徹底するか、キャッシュ自体を諦める。

## 競合・代替

| 観点 | Cloudflare Cache | Fastly | Akamai | AWS CloudFront | Bunny.net | Fly.io |
|---|---|---|---|---|---|---|
| 出自 | フルスタックCDN / セキュリティ統合 | プログラマブルCDN（VCL/Compute@Edge） | 老舗エンタープライズCDN | AWSバンドルCDN | 低価格特化CDN | エッジコンピュート（CDN特化ではない） |
| 設定モデル | Cache Rules（宣言的）+ Workers | VCL / Compute@Edge（手続き的） | プロパティマネージャ（GUI主体） | Behaviors / Functions | シンプルGUI | アプリ実行 + キャッシュは副次的 |
| 永続キャッシュ層 | Cache Reserve（R2） | Origin Shield（単一上位ティア） | Tiered Distribution | Origin Shield（リージョン単位） | Perma-Cache | なし |
| 上位ティア | Smart / Generic / Custom | Origin Shield POP指定 | 多層階層キャッシュ | Origin Shield | Geo-Replication | なし |
| Tag Purge | Enterprise | 標準（強み） | 標準 | Invalidation Path（Tag非対応） | 標準 | なし |
| 即時Purge | 数秒〜 | 〜150ms（業界最速級） | 数秒〜 | 数十秒〜分 | 数秒〜 | アプリ次第 |
| 価格 | Free含む4段階・帯域無制限 | 帯域従量・高め | 要見積もり・高価 | 帯域従量・リージョン別 | 帯域$0.005〜と最安級 | Compute従量 |
| 強み | 統合・無料枠・Cache Reserve・帯域無料 | プログラマビリティ・即時Purge | 大規模配信実績・SLA | AWS連携・S3直結 | 価格 | アプリ近接配置 |
| 弱み | プログラマビリティはWorkers前提 | コスト・学習コスト | 高価・運用重厚 | Tag Purge非対応・キャッシュキー柔軟性低 | エンタープライズ機能薄い | CDN特化機能なし |

CloudflareはCache Rulesの宣言的シンプルさ、無料枠と帯域無料、Cache ReserveによるR2連携、Workersでの拡張、の組合せで「中堅まではこれ一枚で完結する」のが最大の強みである。即時Tag Purgeの一点突破ならFastly、AWS純正で揃えるならCloudFront、純粋な帯域単価ならBunny.netが候補に上がる。

## 料金

- **Cache 本体**：すべてのプランで標準提供。Free含めて帯域無制限・追加課金なし。
- **Tiered Cache**：
  - Smart Tiered Cache Topology：Pro以上（Freeは対象外）。追加課金なし。
  - Generic Global / Custom Topology：Enterprise専用。
- **Cache Reserve**：有料Cache Reserveプランの契約が前提。R2類似の従量課金：
  - ストレージ：$0.015 / GB-month
  - Class A（書き込み）：$4.50 / 100万リクエスト
  - Class B（読み出し）：$0.36 / 100万リクエスト
- **Always Online**：Free含む全プランで標準。
- **Purge**：API / Dashboardで標準。Tag / Hostname / Prefix PurgeはEnterprise機能。
- **Cache Rules上限**：Free 10 / Pro 25 / Business 50 / Enterprise 300。

オリジン側エグレス料金とCDN帯域料金が事実上ゼロ（Cloudflareは帯域課金なし）であり、AWS S3 + CloudFrontと比較すると大規模配信ほどコスト差が大きく開く。逆にCache Reserveは「使った分だけ」モデルであり、長尾コンテンツのヒット率向上と読み出し課金のバランス設計が必要になる。

## CLI / API 例

### Cache Rule作成（curl、Rulesets API）
```bash
# HTMLを5分キャッシュし、ログインCookieがあるときはバイパス
curl -X POST "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/rulesets" \
  -H "Authorization: Bearer ${CF_API_TOKEN}" \
  -H "Content-Type: application/json" \
  --data '{
    "name": "Cache HTML with cookie bypass",
    "kind": "zone",
    "phase": "http_request_cache_settings",
    "rules": [{
      "expression": "(http.request.uri.path matches \"^/blog/\")",
      "action": "set_cache_settings",
      "action_parameters": {
        "cache": true,
        "edge_ttl": { "mode": "override_origin", "default": 300 },
        "browser_ttl": { "mode": "override_origin", "default": 60 },
        "cache_reserve": { "eligible": true, "minimum_file_size": 0 },
        "serve_stale": { "disable_stale_while_updating": false }
      }
    }]
  }'
```

### Purge by URL
```bash
curl -X POST "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/purge_cache" \
  -H "Authorization: Bearer ${CF_API_TOKEN}" \
  -H "Content-Type: application/json" \
  --data '{
    "files": [
      "https://example.com/index.html",
      "https://example.com/assets/app.css"
    ]
  }'
```

### Purge by Tag（Enterprise）
```bash
curl -X POST "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/purge_cache" \
  -H "Authorization: Bearer ${CF_API_TOKEN}" \
  -H "Content-Type: application/json" \
  --data '{ "tags": ["product-1234", "category-shoes"] }'
```

### Terraform（cloudflare provider v5）
```hcl
# Cache Rule: 画像系を1日キャッシュ + Cache Reserve対象化
resource "cloudflare_ruleset" "cache_images" {
  zone_id = var.zone_id
  name    = "Cache images aggressively"
  kind    = "zone"
  phase   = "http_request_cache_settings"

  rules {
    expression  = "(http.request.uri.path.extension in {\"jpg\" \"jpeg\" \"png\" \"webp\" \"avif\"})"
    action      = "set_cache_settings"
    description = "Long TTL for images, eligible for Cache Reserve"

    action_parameters {
      cache = true
      edge_ttl {
        mode    = "override_origin"
        default = 86400
      }
      browser_ttl {
        mode    = "override_origin"
        default = 86400
      }
      cache_reserve {
        eligible          = true
        minimum_file_size = 0
      }
    }
  }
}

# Tiered Cache: Smart Topologyを有効化
resource "cloudflare_tiered_cache" "smart" {
  zone_id    = var.zone_id
  cache_type = "smart"
}

# Cache Reserve（ゾーン単位の有効化）
resource "cloudflare_zone_cache_reserve" "this" {
  zone_id = var.zone_id
  enabled = true
}
```

## 制限・注意点
- 単一ファイルの最大キャッシュサイズはFree/Pro/Business 512MB、Enterpriseはデフォルト5GB。これを超えるアセットはStream / R2直配信が現実解。
- HTML / JSONはデフォルトで非キャッシュ。Cache Rulesで明示的に「Eligible for cache」を有効化しないと、Always Onlineも効かない。
- Cache Reserveは最低Edge TTL 10時間が条件。短TTLのアセットは退避対象外。
- Cache Reserve は `Content-Length` ヘッダがないレスポンス（Chunked TransferのみのオリジンやWorkersのstreaming response）も対象外になる。
- Tag / Hostname / Prefix PurgeはEnterprise限定。Pro / Businessでは Single-File と Purge Everything のみ。
- Purge Everythingはエッジ全PoPからの追い出しなので、直後はオリジン負荷が一時的に跳ねる。リリース時はSWR + Cache Tag（Enterprise）で局所的に剥がす設計が望ましい。
- Bypass Cache on Cookieは正規表現マッチで設定するが、ログインCookie名がアプリ依存なので、Cookie命名規則をフロントエンドと事前合意しておく必要がある。
- Custom Cache Keyに含めるパラメータが多いほどキャッシュフラグメンテーションが進み、ヒット率が低下する。クエリパラメータの正規化（不要パラメータの除外、ソート）を併用する。
- Workers経由のレスポンスは別途 `cf.cacheEverything` / `cacheTtl` の明示が必要で、Cache Rulesと挙動が一部異なる。Workers + Cache APIを使う場合はキャッシュ責務がアプリ側に移る点に注意。
- Smart Tiered Cache Topologyの「対応プラン」は時期によって表記揺れがある（Pro以上が標準、Free対応はEnterpriseアカウント傘下のFreeなど条件付き）。導入時はダッシュボードのトグル可否を確認するのが確実。
- Vary for Imagesを有効化するとキャッシュキーが分岐するため、ヒット率が落ちる可能性がある。Polish / Cloudflare Imagesと併用する前提で考える。

## 参考リンク
- Cloudflare Cache 概要：https://developers.cloudflare.com/cache/
- Cache Rules：https://developers.cloudflare.com/cache/how-to/cache-rules/
- Default Cache Behavior：https://developers.cloudflare.com/cache/concepts/default-cache-behavior/
- Tiered Cache：https://developers.cloudflare.com/cache/how-to/tiered-cache/
- Cache Reserve：https://developers.cloudflare.com/cache/advanced-configuration/cache-reserve/
- Purge Cache：https://developers.cloudflare.com/cache/how-to/purge-cache/
- Crawler Hints：https://developers.cloudflare.com/cache/advanced-configuration/crawler-hints/
- Vary for Images：https://developers.cloudflare.com/cache/advanced-configuration/vary-for-images/
- Cache llms.txt：https://developers.cloudflare.com/cache/llms.txt
- Terraform `cloudflare_ruleset`：https://registry.terraform.io/providers/cloudflare/cloudflare/latest/docs/resources/ruleset

---
参照日: 2026-05-04
