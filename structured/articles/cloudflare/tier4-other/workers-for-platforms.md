# Workers for Platforms / Cloudflare for SaaS

## 一行サマリ
エンドユーザー（=自社プラットフォームの顧客）が書いたコードと、エンドユーザーが持ち込んだカスタムドメインを、自社のSaaS基盤に安全に乗せるための2製品である。Workers for Platformsはマルチテナントの「コード実行」を、Cloudflare for SaaSはマルチテナントの「ドメイン/SSL終端」をCloudflareエッジ上で代行する。

## 解決する課題（Why）
ShopifyやWebflow、Notion、ローコード/ノーコード、AIエージェントマーケットプレイスのようなマルチテナントSaaSを作る際、必ずぶつかる2つの壁がある。

ひとつ目は「顧客のコードをどう動かすか」。各テナントが書いたJavaScript / TypeScript / WASMを安全に隔離し、テナント単位でCPU・サブリクエスト・メモリ制限を掛け、ログ/メトリクスをテナントID付きで吐き、AI生成コードのような信頼できないコードもサンドボックス化したい。FaaS（Lambda / Cloud Run）でテナントごとに関数を作る運用は数百テナントで破綻し、コールドスタート・関数数上限・IAMの複雑度が一気に重くなる。

ふたつ目は「顧客のドメインをどう載せるか」。`shop.customer-brand.com` のように顧客の独自ドメインを自社SaaSに向けさせ、SSL証明書を自動発行・自動更新し、HTTPSの可用性をSaaS事業者側で保証したい。さらに金融・ヘルスケア向けにmTLS、エンタープライズ向けにApex（ルートドメイン）プロキシ、規制業種向けに自社IPレンジ（BYOIP）まで要求される。Let's Encrypt + 手動運用では数千テナント規模で確実に事故る。

Workers for PlatformsとCloudflare for SaaSは、この2つの壁をCloudflareエッジに丸ごと押し出して解決する。

- Workers for Platformsはdispatch namespace上で「親Worker（Dispatch Worker）→ 顧客Worker（User Worker）→ 共通の外向きWorker（Outbound Worker）」の3層を構成し、テナントコード実行・隔離・観測・送信ポリシーを一括で扱う。
- Cloudflare for SaaSは顧客ドメインを `CNAME → customers.saas.example.com` で受け取り、Cloudflareがホストネーム検証・SSL証明書発行更新・SNIルーティング・mTLS・Apex proxying・BYOIPを代行する。
- 両者を組み合わせると「顧客の独自ドメインで、顧客のコードを、Cloudflareエッジで実行する」マルチテナントSaaSが、自前のFaaS基盤・自前の証明書管理・自前のフロントロードバランサーなしで成立する。

## 主要機能（What）

### Workers for Platforms

#### Dispatch namespace
顧客Workerをまとめて格納する論理コンテナ。1つのSaaS事業者が `production` / `staging` のように複数namespaceを持ち、各namespace配下にテナント単位のUser Workerを並べる。`wrangler dispatch-namespace create` で作成し、Dispatch Workerからnamespace bindingで参照する。

#### Dispatch Worker
リクエストを最初に受ける親Worker。HostヘッダーやURLパス、JWT、テナントIDから対応するUser Workerを選び、`env.DISPATCHER.get(scriptName).fetch(request)` で動的にディスパッチする。認証・レート制限・課金カウント・テナント識別など「全テナント共通の前処理」をここに集約する。

#### User Worker
顧客自身（またはAI、テンプレートビルダー）が書いてアップロードする個別Worker。dispatch namespaceに `wrangler deploy --dispatch-namespace <ns>` でアップロードされ、Dispatch Workerから動的に呼ばれる。各User Workerは独立したIsolateで実行され、他テナントのKV・DO・環境変数・メモリには一切アクセスできない。Custom Limits（CPU時間・サブリクエスト数）をテナント単位で設定でき、暴走テナントが基盤を巻き込まない。

#### Outbound Worker
User Workerが外向き（fetch）するすべてのリクエストを横取りする「egress proxy Worker」。User Workerから直接外部APIを叩かれる代わりに、いったんOutbound Workerを経由させ、許可ドメインのallowlist、PII除去、共通ヘッダー注入、テナントIDのアウトバウンドログ、レート制限を掛けられる。AI生成コードを動かす前提なら事実上必須。

#### Static Assets
User Workerに静的ファイル（HTML / CSS / JS / 画像）をバンドルでき、Cloudflareエッジで直接配信される。テナントごとのテーマ・ビルド成果物をUser Workerと一緒にデプロイし、Origin不要のフルスタックSaaSが組める。

#### Tags
User Workerに任意のメタデータタグ（`customer_id:1234`、`plan:enterprise`、`region:apac`）を付与でき、API/wranglerからタグでフィルタリング・一括削除・観測対象の絞り込みが可能。テナント解約時に `tag=customer_id:1234` でまとめて削除、といった運用が一発で打てる。

#### Custom Limits
User Worker単位でCPU時間・サブリクエスト数の上限を上書きできる。Freeプランのテナントは50ms、Enterpriseテナントは300msのように、課金プランに応じた制限をプラットフォーム側から強制する。

#### Observability
全namespace横断でログ・メトリクス・トレースを収集し、Datadog / Splunk / Grafana / Logpushで吐ける。テナントIDタグと組み合わせ、どのテナントが何msのCPUを食ったかをそのまま課金システムに流せる。

### Cloudflare for SaaS

#### Custom Hostnames
SaaS顧客の独自ドメイン（例：`shop.customer-brand.com`）を受け入れる中核機能。顧客側のDNSで `CNAME shop → customers.saas.example.com` を立てさせ、Cloudflareがホストネーム検証（CNAMEまたはHTTPトークン）→ 証明書発行 → ルーティングまで自動化する。SaaS事業者は API 1本（`POST /custom_hostnames`）で登録するだけで、SNI/Hostヘッダー単位のルーティングが裏で出来上がる。

#### SSL for SaaS
Custom Hostnameごとに自動発行されるTLS証明書。デフォルトはLet's Encrypt / Google Trust Services経由のDV証明書を自動発行・自動更新する。Enterpriseでは持ち込み証明書（BYO certificate）、CSR提出、CA選択、ワイルドカードカスタムホストネーム、Advanced Certificate Manager相当の機能が解放される。SaaS事業者側で「証明書が切れた」という事故を物理的に起こさないのが最大の価値。

#### Fallback Origin
すべてのCustom Hostname宛トラフィックの最終転送先となるオリジン1つ。プロキシ化されたA / AAAA / CNAMEで指定する。実運用ではこのfallback originをDispatch Worker（Workers for Platforms）にしておくのが定石で、ホスト名→テナント解決をWorker側で完結させる。

#### Apex Proxying
顧客が `customer-brand.com` のようなルートドメイン（apex / zone apex）をそのまま向けたい場合に使う。通常CNAMEはapexに張れないため、CloudflareがANAME相当のフラット化を行いCloudflareアドレスを返す。Enterprise限定アドオン。

#### mTLS（Authenticated Origin Pulls / Client Certificates）
2系統ある。(1) エッジ↔オリジン間mTLSで、SaaS事業者のオリジンに「Cloudflareから来た」ことを保証する Authenticated Origin Pulls。(2) エンドユーザー↔エッジ間mTLSで、Custom Hostnameごとにクライアント証明書検証を有効化し、API利用者ごとに証明書発行する。金融・医療・B2BのAPI SaaSで頻出。

#### BYO Certificate
顧客自身が用意したEV / OV証明書、またはSaaS事業者がDigiCertやEntrustで発行した証明書をアップロードして使う。Enterprise限定。規制業種・監査要件で「DV不可」のケースで必要になる。

#### BYOIP（Bring Your Own IP）
SaaS事業者が保有する/24以上のIPv4レンジ、または/48以上のIPv6レンジをCloudflareにBGPアナウンスさせる。顧客側ファイアウォールのIP allowlistにSaaS事業者のIP帯を登録するエンタープライズ要件、自社ブランドのIP評価維持、規制でCloudflare共有IPが使えない国・業種で必須となる。Enterpriseアドオン。

## アーキテクト視点：いつ選ぶか

### Workers for Platforms

#### 適しているシーン
- ノーコード / ローコード / CMS / ECビルダーが、テナント独自のサーバーロジック（カスタムチェックアウト、独自ルーティング、A/Bテストルール）をエッジで動かしたい。
- AIエージェントマーケットプレイスやLLMツールホスティングで、ユーザー生成コード（あるいはLLM生成コード）をサンドボックス化して動かしたい。Outbound Workerで外向き先を制限する前提とセットで強力。
- Shopify / Wix / Squarespace相当のSaaSで、テナントごとのEdge Functionsを提供する機能を後付けしたい。
- 既にCloudflare Workersで自社プロダクトを動かしており、その上にテナント拡張機構を乗せたい。

#### 適していないシーン
- テナントが数十程度で、各テナントの拡張も限定的な規模。普通のWorkers + 環境変数 + KVで十分で、$25/月のWorkers for Platforms契約は過剰。
- Node.js互換 / 長時間実行 / 大きなメモリが必要なワークロード。Workers Isolateの30秒CPU上限・128MBメモリでは足りない。Containers / Cloud Run / ECSが本筋。
- 顧客コードが「信頼できる社内チームが書く」だけのケース。隔離不要なら通常のmulti-tenant Worker構成で良い。

### Cloudflare for SaaS

#### 適しているシーン
- B2B / B2Cで「顧客が独自ドメインで自社サービスにアクセスする」体験を提供する全SaaS（EC、CMS、LMS、フォーラム、メールマーケ、サポートポータル、ヘルプセンター）。
- 数千〜数万テナント規模でSSL証明書の自動更新を絶対に事故らせたくない。
- 規制業種顧客にmTLS / BYO certificate / BYOIPを売り物として提供したい。
- 既存のCustom Hostname自前実装（ACME自動化＋HAProxyでSNIルーティング）を運用負債として捨てたい。

#### 適していないシーン
- ドメインを自社で完全管理し、サブドメイン（`customer.saas.example.com`）方式で十分なケース。Cloudflare for SaaSのコストとEnterprise要件は不要で、普通のCloudflareゾーン + ワイルドカード証明書で足りる。
- 顧客が極めて少数（数社）で、運用チームが手動証明書管理を許容できる。
- 全テナントが同じドメイン階層を共有し、テナント識別がパスベース（`/tenant-a/`）で完結する場合。

## 競合・代替

| 観点 | Workers for Platforms | Cloudflare for SaaS | Vercel Spaces / Multi-tenant | Netlify Multi-tenant | Fastly Compute@Edge | AWS App Runner + ACM | Approximated.app |
|---|---|---|---|---|---|---|---|
| 主目的 | 顧客コードの実行隔離 | 顧客ドメイン/SSL代行 | 顧客プロジェクトのホスティング | 顧客サイトのホスティング | エッジ実行 | コンテナホスティング | Custom Hostname特化 |
| マルチテナント設計 | Dispatch Worker明示モデル | Custom Hostname API | プロジェクト単位 | サイト単位 | 単一サービス内で実装 | サービス単位 | API一本 |
| カスタムドメイン規模 | （別途SaaS要） | 数万〜無制限 | 数千 | 数千 | （別途実装） | ACM上限あり | 数千〜 |
| SSL自動化 | （SaaS側） | 完全自動 / BYO / mTLS | Let's Encrypt自動 | Let's Encrypt自動 | 別途 | ACM | Let's Encrypt自動 |
| 顧客コード実行 | Isolate（強隔離） | なし | Edge Functions | Edge Functions | 強隔離（Wasm） | コンテナ（VM境界） | なし |
| AI生成コード適性 | Outbound Workerで本職 | 該当せず | 限定的 | 限定的 | 可能だが事例少 | 可能だが起動遅い | 該当せず |
| Apex proxying | （SaaS側） | Enterpriseアドオン | 一部対応 | 一部対応 | 個別実装 | Route 53 ALIAS | 対応 |
| BYOIP | （SaaS側） | Enterpriseアドオン | 不可 | 不可 | 可能（契約） | 一部対応 | 不可 |
| mTLS | Worker側で実装可 | エッジで提供 | 限定的 | 限定的 | 可能 | NLBで実装 | 不可 |
| 価格モデル | $25/月+従量 | プラン+ホスト名$0.10/月 | プロジェクト課金 | サイト課金 | 従量 | 時間/リクエスト課金 | 月額固定 |
| Enterprise契約 | 不要（Standardから可） | 標準/Pro/Business/Enterprise | あり | あり | あり | AWS契約 | あり |

VercelやNetlifyの「マルチテナントホスティング」は、SaaS事業者が自社プラットフォームを売る用途には機能が薄く、課金モデルもエンドユーザーごとに線形コストが乗る。AWS App Runner + ACMはコンテナ前提で起動が遅く、数千テナントの自動証明書発行ではACMの上限に引っかかりやすい。Approximated.appはCustom Hostname部分だけを切り出した特化サービスで、コード実行は持たない。Fastly Compute@EdgeはWasm隔離が強力だがdispatch namespace相当の「顧客Workerを動的にデプロイする」モデルは事業者側で組む必要がある。

Cloudflareの強みは、「コード実行（Workers for Platforms）」と「ドメイン/SSL（Cloudflare for SaaS）」を別製品として独立して買え、両者を組み合わせるとマルチテナントSaaSのフロントエンドがほぼ完成する点にある。

## 料金

### Workers for Platforms
- **Standard**：$25/月。月2000万リクエスト・6000万CPU-ms・1000スクリプト含み、超過分は100万リクエストあたり$0.30、CPU 100万msあたり$0.02、追加スクリプト1個あたり$0.02。Enterprise契約は不要で、課金が立てば誰でも使える。
- **Custom Limits**：テナント単位でCPU/subrequest上限を設定する機能自体に追加課金はない。
- **Subrequest**：課金対象外。Outbound Worker経由の外向きfetchも個別課金されない。
- **Dispatch chain**：Dispatch Worker → User Worker → Outbound Workerの一連の呼び出しで「1リクエスト」としてカウントされる。

### Cloudflare for SaaS
- **Free / Pro / Business**：含み100ホスト名、超過は1ホスト名あたり$0.10/月。最大50,000ホスト名まで自助で扱える。
- **Enterprise**：個別見積もり、50,000超のホスト名対応、Apex proxying / BYOIP / Custom certificates / CSR / CA選択 / ワイルドカードカスタムホストネーム / Custom metadataがアドオンで追加可能（具体額は非公開）。
- **DV証明書発行**：自動発行・自動更新自体に追加課金なし。

「数千テナントのSaaSをFree/Proベースで運用し、ホスト名$0.10/月だけがマージナルコスト」という構造は、独自ACME自動化＋自前ロードバランサーと比べて圧倒的に安い。Workers for Platformsと組み合わせても、$25/月＋ホスト名$0.10×N＋従量という極めて読みやすいコスト曲線になる。

## CLI / API 例

### Workers for Platforms：dispatch namespace 作成・User Worker デプロイ
```bash
# namespace作成
npx wrangler dispatch-namespace create production

# Dispatch Worker（自社管理）
npx wrangler deploy --name dispatcher

# User Worker をテナントcustomer-1234として namespace にデプロイ
npx wrangler deploy \
  --name customer-1234 \
  --dispatch-namespace production \
  --tag customer_id:1234 \
  --tag plan:enterprise

# タグ条件で一括削除（テナント解約時）
npx wrangler dispatch-namespace delete-scripts production \
  --tag customer_id:1234
```

Dispatch Worker側のコード例（要点のみ）：
```ts
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const tenant = resolveTenant(request); // Hostヘッダー等から
    const userWorker = env.DISPATCHER.get(tenant, {}, {
      outbound: { tenant_id: tenant }, // Outbound Workerに渡される
      limits: { cpuMs: 50 },
    });
    return userWorker.fetch(request);
  },
};
```

### Cloudflare for SaaS：Custom Hostname 登録
```bash
# 顧客ドメイン shop.customer-brand.com を登録、DV証明書を自動発行
curl -X POST "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/custom_hostnames" \
  -H "Authorization: Bearer $CF_API_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{
    "hostname": "shop.customer-brand.com",
    "ssl": {
      "method": "http",
      "type": "dv",
      "settings": {
        "min_tls_version": "1.2",
        "ciphers": ["ECDHE-ECDSA-AES128-GCM-SHA256"],
        "http2": "on"
      },
      "bundle_method": "ubiquitous"
    },
    "custom_metadata": {
      "tenant_id": "1234",
      "plan": "enterprise"
    }
  }'

# ホストネーム検証ステータス確認
curl -X GET "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/custom_hostnames/$HOSTNAME_ID" \
  -H "Authorization: Bearer $CF_API_TOKEN"
```

### Cloudflare for SaaS：mTLS（Custom Hostnameごとのクライアント証明書検証）
```bash
# クライアントCAを zone にアップロード
curl -X POST "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/client_certificates" \
  -H "Authorization: Bearer $CF_API_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{
    "certificate": "-----BEGIN CERTIFICATE-----\n...",
    "private_key": "-----BEGIN PRIVATE KEY-----\n..."
  }'

# Custom Hostname に mTLS を有効化
curl -X PATCH "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/custom_hostnames/$HOSTNAME_ID" \
  -H "Authorization: Bearer $CF_API_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{
    "ssl": {
      "settings": {
        "tls_1_3": "on",
        "min_tls_version": "1.2"
      },
      "type": "dv",
      "method": "http"
    },
    "ssl_settings": { "client_certificate": true }
  }'
```

### Terraform（cloudflare provider v5）
```hcl
resource "cloudflare_workers_for_platforms_dispatch_namespace" "prod" {
  account_id = var.account_id
  name       = "production"
}

resource "cloudflare_custom_hostname" "tenant_1234" {
  zone_id  = var.zone_id
  hostname = "shop.customer-brand.com"

  ssl = {
    method         = "http"
    type           = "dv"
    bundle_method  = "ubiquitous"
    wildcard       = false
    settings = {
      min_tls_version = "1.2"
      http2           = "on"
    }
  }

  custom_metadata = {
    tenant_id = "1234"
    plan      = "enterprise"
  }
}
```

## 制限・注意点
- **Workers for PlatformsはStandardプランから利用可能**だが、$25/月の固定費がベース。テナント数が極めて少ないPoC段階では、通常のWorkers + KVの方が安い。
- **User Workerサイズ・CPU・メモリ制限はWorker本体と同じ**：圧縮後10MB、CPU 30秒（リクエストの場合）、メモリ128MB。Node.js全機能は使えず、`nodejs_compat` フラグで限定APIのみ。
- **Outbound Workerは「全外向きfetchを横取り」**するため、設計を誤るとレイテンシ倍増・タイムアウト連鎖の温床になる。Outbound Worker内でさらに外部APIを呼ぶ際の二重カウント・二重タイムアウトに注意。
- **Custom Hostnameの証明書発行レート**：1zoneあたり / 1日あたりの発行レートに上限があり、初回大量移行（数万テナント一括）では分割登録が必要。Enterprise契約でレート緩和を依頼するのが定石。
- **DV証明書発行は顧客DNSに依存**：顧客側で `CNAME` 設定が誤っているとhostname validation pendingのまま証明書が発行されず、ステータス監視と顧客への通知UIをSaaS側で必ず作る。
- **Apex proxyingはEnterpriseアドオン**：Pro/Businessプランでは顧客のapex（`customer-brand.com`）を直接向ける運用は不可で、サブドメイン誘導しかできない。エンタープライズ顧客の要望が出る前提なら最初からEnterpriseで設計する。
- **BYOIPはBGP・LOA・RPKIの実務が必須**：単に契約すれば使えるわけではなく、IRR登録・LOA作成・ROA登録・段階的なBGPアナウンスが伴う。Cloudflare側との共同オペレーションが数週間単位で発生する。
- **mTLS（Client Certificates）はSNI単位の証明書プール管理**：失効CRL/OCSPの設計、クライアント証明書発行フロー、ローテーション、失効時のテナント通知をSaaS側でフルに作り込む必要がある。
- **Custom metadataはEnterpriseアドオン**：`custom_metadata` をWorkerから読み取れる便利機能だが、有償アドオン扱い。代替としてDispatch Worker側でテナントID→メタデータをKVで引く設計が現実的。
- **Workers for PlatformsとCloudflare for SaaSは独立製品**：両方契約しないと「顧客ドメインで顧客コードを動かす」フルセットにはならない。料金見積もりで漏れやすい。
- **両製品ともWorker / Custom Hostnameの上限値はEnterpriseで緩和できる**ものの、Free/Pro/Business段階で50,000ホスト名・1,000スクリプトを超える設計は早めにEnterprise相談に切り替える。
- **Static Assets配信はUser Worker単位**：テナントごとに静的アセットを別バンドルでデプロイするとストレージとデプロイ時間が膨らむ。共通テーマはR2 + Cache APIに寄せる設計が安全。

## 参考リンク
- Workers for Platforms 概要：https://developers.cloudflare.com/cloudflare-for-platforms/workers-for-platforms/
- Workers for Platforms Get started：https://developers.cloudflare.com/cloudflare-for-platforms/workers-for-platforms/get-started/configuration/
- Workers for Platforms Pricing：https://developers.cloudflare.com/cloudflare-for-platforms/workers-for-platforms/platform/pricing/
- Outbound Workers：https://developers.cloudflare.com/cloudflare-for-platforms/workers-for-platforms/configuration/outbound-workers/
- Custom Limits：https://developers.cloudflare.com/cloudflare-for-platforms/workers-for-platforms/configuration/custom-limits/
- Cloudflare for SaaS 概要：https://developers.cloudflare.com/cloudflare-for-platforms/cloudflare-for-saas/
- Cloudflare for SaaS Get started：https://developers.cloudflare.com/cloudflare-for-saas/start/getting-started/
- Cloudflare for SaaS Plans：https://developers.cloudflare.com/cloudflare-for-saas/plans/
- Custom Hostnames API：https://developers.cloudflare.com/api/operations/custom-hostname-for-a-zone-create-custom-hostname
- mTLS for SaaS：https://developers.cloudflare.com/cloudflare-for-saas/security/mtls/
- Apex Proxying：https://developers.cloudflare.com/cloudflare-for-saas/start/advanced-settings/apex-proxying/
- BYOIP：https://developers.cloudflare.com/byoip/
- Terraform `cloudflare_custom_hostname`：https://registry.terraform.io/providers/cloudflare/cloudflare/latest/docs/resources/custom_hostname
- Terraform `cloudflare_workers_for_platforms_dispatch_namespace`：https://registry.terraform.io/providers/cloudflare/cloudflare/latest/docs/resources/workers_for_platforms_dispatch_namespace

---
参照日: 2026-05-04
