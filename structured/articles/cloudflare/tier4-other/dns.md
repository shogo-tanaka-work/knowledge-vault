# DNS (Authoritative / DNS Firewall / Internal DNS)

## 一行サマリ
Cloudflare DNSは、Anycastで世界配信される権威DNS（Authoritative）と、外部権威ネームサーバの前段にキャッシュ層を挟むDNS Firewall、そしてZero Trust配下のクライアントだけが解決できるInternal DNSを束ねた、エッジ統合型のDNSプラットフォームである。

## 解決する課題（Why）
DNSは「動いて当たり前」と扱われやすい一方、レイテンシ・改ざん耐性・対DDoS・社内外名前空間の分離・複数プロバイダ間のフェイルオーバといった要件が現実には積層しており、単一の権威サーバ運用では捌けない。Cloudflare DNSは以下を一つのコントロールプレーンで解決する。

- 全レコードをAnycast配信し、地理的に最も近いPoPから応答してDNSルックアップのレイテンシを最小化する。
- DNSSECで応答の改ざん・キャッシュポイズニングを抑止し、Multi-signer DNSSECで複数プロバイダ運用とも両立させる。
- 既存のBIND/PowerDNSなど自社権威の前段にDNS Firewallを置き、recursive側からのDDoSとRandom Prefix Attackを吸収する。
- 社内向けプライベートゾーンをInternal DNSとしてZero Trust（WARP/Gateway）配下にだけ公開する。
- パブリックリゾルバ（1.1.1.1）と権威DNSは別プロダクトであり、役割を分離した上で同一エッジ網に同居させる。

## 主要機能（What）

### Authoritative DNS
ドメインのNSをCloudflareに委任し、A/AAAA/CNAME/MX/TXT/SRV/CAA/HTTPS/SVCB等のレコードをAnycastで配信する権威DNSサービスである。Free zoneでも商用利用可能で、DNSのみ利用（プロキシなし、いわゆる"DNS-only"運用）も許容される。

- **CNAME Flattening**：Apex（example.com）にCNAMEを置く構成を、応答時に解決済みA/AAAAへ畳み込んで返す。RFC違反を回避しつつSaaS（HerokuやNetlify）をApexに当てられる。
- **Proxied vs DNS-only**：レコード単位でプロキシ（オレンジ雲）を切り替え、CDN/WAF経由かDNS応答のみかを選択する。
- **Bulk import / export**：BINDゾーンファイル形式でのインポート・エクスポートに対応。
- **Wildcard / Geo Steering**：Wildcardレコード、およびLoad Balancing連携でのGeoルーティング・ヘルスチェック付き応答。

### DNSSEC / Multi-signer DNSSEC
ゾーンに対してDNSSECを有効化すると、CloudflareがKSK/ZSKを管理しDSレコードをレジストラに登録するだけで運用が完結する。Multi-signer DNSSECは、Cloudflareと別プロバイダの両方を権威として並立させるマルチプロバイダ構成においても、各プロバイダが自分のZSKで署名し合う仕組みで、片寄せなしのDNSSEC運用を可能にする。

- ワンクリック有効化（自動鍵管理 / 自動ロールオーバー）。
- Multi-signer Model 2（各プロバイダが自分の鍵で署名し、互いのDNSKEYをゾーンに含める）を公式サポート。
- Secondary DNSと組み合わせた冗長構成でもDNSSECを維持できる。

### Secondary DNS / Multi-provider DNS
Cloudflareをsecondaryとして使う構成（外部primary → Cloudflare）と、primaryとして使う構成（Cloudflare primary → 外部secondary）の双方をサポートする。AXFR/IXFRゾーン転送、TSIGによる転送認証に対応する。

- **Cloudflare as Secondary**：BIND/PowerDNS/Route 53などのprimaryからAXFR/IXFRで取り込み、Cloudflareエッジから配信。プロキシ機能やDDoS吸収はsecondary構成でも有効。
- **Cloudflare as Primary**：Cloudflareをマスタにして、他社DNSへ転送。
- **Multi-provider DNS**：両プロバイダをNSに並べる構成で、片方の障害時にもクライアントが他方から応答を得られる。Multi-signer DNSSECはこのパターンの完成形。
- TSIG（HMAC-SHA256等）でゾーン転送を相互認証。

### Internal DNS（Zero Trust連携）
WARP/Gateway配下のデバイスにのみ解決させたい社内ホスト名を、パブリックには露出しない形で配信する仕組みである。Gateway DNS resolverに「DNS view」を設定し、Internal Zoneに登録したレコードを社内クライアントへ返す。社外から同じFQDNを引いても応答は返らない。

- **DNS Views**：ソース（拠点・ユーザ・グループ・Virtual Network）に応じて異なるゾーンを返す split-horizon DNS。
- **Internal Zones**：パブリックゾーンとは別管理のプライベートゾーン。Tunnel経由の社内リソースに名前を付ける用途と相性が良い。
- **Conditional Forwarding**：特定サフィックス（例：corp.example.com）だけオンプレDNSに転送する設定。
- 既存のActive Directory DNSやRoute 53 Resolverに代替・併用できる位置付け。

### DNS Firewall
お客様自身が運用する外部権威ネームサーバ（BIND/NSDなど）の前段にCloudflareのAnycast IPを置き、そこにキャッシュとDDoS緩和層を挿入するサービスである。Authoritative DNSと違い「権威そのものをCloudflareに委ねる」のではなく、「権威の前にプロキシキャッシュを噛ませる」アーキテクチャである。

- 専用Anycast IPv4/IPv6ペアを発行し、レジストラ側のNSをそのIPに張ったgluedレコードに切り替えて運用。
- Random Prefix Attack（ランダムサブドメインによるキャッシュ枯渇攻撃）を含むDNS DDoSをエッジで吸収。
- TTL尊重のキャッシュ層により、オリジンnameserverへのQPSを大幅に削減。
- 既存DNS基盤（オンプレBIND、ベンダロックを避けたい商用DNS）の延命策として有効。

### DNS Analytics / Logpush
全クエリの応答コード・QType・PoP・国別分布をダッシュボードとGraphQL Analytics APIで参照できる。EnterpriseではLogpushでDNSクエリログをR2/S3/GCS/Splunk/Datadogへ継続転送可能。

- レコード単位・国別・QType別のクエリ数とエラー率の可視化。
- DNSSEC validation failureやNXDOMAIN比率の監視。
- LogpushによるSIEM連携とコンプライアンス用途の長期保管。

### 1.1.1.1 リゾルバとの違い
1.1.1.1 は **public recursive resolver**（クライアントから引かれる側）、Cloudflare DNSのAuthoritative/DNS Firewallは **authoritative**（ゾーンを保持する側）であり、役割が完全に異なる。同じCloudflareエッジに同居しているため一見混同されがちだが、課金・設定・運用ドメインは別物である。Zero TrustのGateway DNS resolverは1.1.1.1ベースで動作し、Internal DNSはこのGateway resolverに「自社ビュー」をオーバレイする形で実装されている。

## アーキテクト視点：いつ選ぶか

### 適しているシーン
- すでにCloudflareをCDN/WAFとして使っており、DNSを同じプレーンに寄せて運用を単純化したい組織。
- DNSSECを「鍵管理込みでワンクリック運用」したいが、自前でBIND鍵ローテーションを書きたくないチーム。
- マルチプロバイダ冗長を組みたいが、Multi-signer DNSSECで片寄せなしの設計を維持したいケース。
- 自社権威ネームサーバを温存しつつ、DDoS対策とキャッシュ層だけ外注したい（=DNS Firewall）伝統的インフラ部門。
- WARP/Tunnelで社内アプリを公開しており、Internal DNSで「社内からだけ引ける名前空間」を欲しいZero Trust組織。

### 適していないシーン
- AWS / GCPでマネージド運用をRoute 53 / Cloud DNSに完全寄せ済みで、Terraformやエコシステム連携も含めて他社に外せないケース。
- DNSベースの高機能トラフィックステアリング（NS1のFiltersや細かいGeo IPデータベース連携）を業務要件として使い倒しているケース。Cloudflare Load Balancingでも近いことはできるが、純血DNSベンダの柔軟性には及ばない部分がある。
- Internal DNSが必須要件で、かつZero Trust（WARP）配布の運用体制が未整備な組織。BetaフェーズかつWARP前提のため、「DNSだけ欲しい」用途では過剰となる。

## 競合・代替

| 観点 | Cloudflare DNS | AWS Route 53 | Google Cloud DNS | NS1 (IBM) | Akamai Edge DNS | Dyn (Oracle) |
|---|---|---|---|---|---|---|
| 出自 | CDN / Anycastネットワーク | AWSマネージドDNS | GCPマネージドDNS | DNS専業（高機能ステアリング） | CDN / DNS専業 | DNS老舗（Oracle買収） |
| Authoritative | 標準（Free zoneあり） | 標準 | 標準 | 標準 | 標準 | 標準 |
| DNSSEC | ワンクリック / Multi-signer対応 | KSK持ち込み運用 | 標準対応 | 標準対応 | 標準対応 | 標準対応 |
| Secondary / Multi-provider | AXFR/IXFR + TSIG / Multi-signer | Primary中心、Secondary別途 | Primary中心 | 強力 | 強力 | 強力 |
| DNS Firewall（権威前段） | 標準提供（専用プロダクト） | なし（Shieldは別概念） | なし | なし | Edge DNSが該当機能を内包 | なし |
| Internal / Private DNS | Internal DNS（Beta、WARP連携） | Route 53 Resolver / Private Zone | Cloud DNS Private Zones | NS1 Private DNS | 別プロダクト | 別プロダクト |
| Geo / Traffic Steering | Load Balancing連携 | Routing Policies（豊富） | Routing Policies | 最強クラス（Filter Chain） | 強力 | 強力 |
| Analytics | ダッシュボード+GraphQL+Logpush | CloudWatch Logs（Resolver Query Logs別途） | Cloud Logging | NS1 Pulsar / Data Streams | 標準同梱 | 標準同梱 |
| 価格 | Authoritativeは無料、Advanced/Enterpriseで段差 | $0.50/zone/月+クエリ課金 | $0.20-0.40/zone/月+クエリ課金 | 高価（要見積もり） | 高価（要見積もり） | 高価（要見積もり） |
| 強み | エッジ統合・無料権威・Multi-signer・DNS Firewall単独提供 | AWS資産との統合・Routing Policies | GCP資産との統合・シンプル | Steeringの柔軟性 | グローバル網・大企業向け運用 | 老舗の運用ノウハウ |
| 弱み | 高機能Steeringは追従途上、Internal DNSはBeta | Multi-signer DNSSECは未成熟 | 機能数で他社に劣る | 価格と運用負荷 | 価格 | プロダクトの将来性に懸念 |

CloudflareはAuthoritative DNSが無料で開始でき、DNSSEC・Multi-signer・DNS Firewall・Internal DNSまで同一アカウントに揃う点が最大の差別化要因である。逆に、ルーティング表現の柔軟性やGeoIPステアリングの精緻さを業務要件の中核に据えるなら、NS1やRoute 53を併用するのが妥当である。

## 料金

- **Authoritative DNS（Free zone）**：レコード数の実質的な上限はゾーンあたり3,500件程度（プラン依存）、クエリ数は無制限・無料。Free/Pro/Businessプランすべてに含まれる。
- **Advanced DNS（add-on）**：年契約。レコード数上限の引き上げ、Multi-signer DNSSEC、Secondary DNS、Logpush（DNS logs）、専用Anycast IP、99.9999% SLAなどが解放される。中堅以上のドメイン運用が前提。
- **Enterprise DNS**：Advanced DNSをEnterprise契約にバンドル。サポートSLA・専用Anycast IPv4/IPv6・カスタムDNSSEC運用・GraphQL長期保持などが含まれる。
- **DNS Firewall**：Enterpriseプランの専用プロダクト。クラスタ単位（Anycast IPペア）で課金され、月額固定+QPS従量の構成。Authoritative運用しないがCloudflareの保護層だけ買いたい層向け。
- **Internal DNS**：Zero Trust（Cloudflare One）ライセンスに紐付く。Gateway/WARP配布が前提。

「Authoritative DNSは無料、付加価値（Multi-signer / Secondary / Logpush / Internal / Firewall）でEnterpriseに段差」が値付けの基本構造である。

## CLI / API 例

### curl（v4 API）
```bash
# ゾーン作成
curl -X POST "https://api.cloudflare.com/client/v4/zones" \
  -H "Authorization: Bearer ${CF_API_TOKEN}" \
  -H "Content-Type: application/json" \
  --data '{"name":"example.com","account":{"id":"'${CF_ACCOUNT_ID}'"},"type":"full"}'

# Aレコード追加（DNS-only）
curl -X POST "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/dns_records" \
  -H "Authorization: Bearer ${CF_API_TOKEN}" \
  -H "Content-Type: application/json" \
  --data '{"type":"A","name":"api","content":"203.0.113.10","ttl":300,"proxied":false}'

# DNSSEC有効化（Cloudflare署名・自動鍵管理）
curl -X PATCH "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/dnssec" \
  -H "Authorization: Bearer ${CF_API_TOKEN}" \
  -H "Content-Type: application/json" \
  --data '{"status":"active"}'

# Secondary DNSのprimary登録（Cloudflareをsecondaryとして使う場合）
curl -X POST "https://api.cloudflare.com/client/v4/accounts/${CF_ACCOUNT_ID}/secondary_dns/primaries" \
  -H "Authorization: Bearer ${CF_API_TOKEN}" \
  -H "Content-Type: application/json" \
  --data '{"name":"primary-bind","ip":"198.51.100.10","port":53,"ixfr_enable":true,"tsig_id":"'${TSIG_ID}'"}'
```

### Terraform（cloudflare provider v5）
```hcl
resource "cloudflare_zone" "main" {
  account_id = var.account_id
  name       = "example.com"
  type       = "full"
}

resource "cloudflare_dns_record" "api" {
  zone_id = cloudflare_zone.main.id
  type    = "A"
  name    = "api"
  content = "203.0.113.10"
  ttl     = 300
  proxied = false
}

resource "cloudflare_dnssec" "main" {
  zone_id = cloudflare_zone.main.id
  status  = "active"
}

# DNS Firewall（recursive保護ではなくauthoritative前段キャッシュ）
resource "cloudflare_dns_firewall" "edge" {
  account_id          = var.account_id
  name                = "primary-bind-cluster"
  upstream_ips        = ["198.51.100.10", "198.51.100.11"]
  minimum_cache_ttl   = 60
  maximum_cache_ttl   = 900
  deprecate_any_requests = true
}
```

### BINDゾーンファイル取り込み
```bash
# UI: DNS → Records → Import and Export → Import DNS records
# API:
curl -X POST "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/dns_records/import" \
  -H "Authorization: Bearer ${CF_API_TOKEN}" \
  -F "file=@example.com.zone" \
  -F "proxied=false"
```

## 制限・注意点
- Free/Pro/BusinessプランのDNSレコード上限はゾーンあたり概ね3,500件であり、巨大ゾーンを運用する場合はAdvanced DNSが前提となる。
- Multi-signer DNSSECは双方のプロバイダがModel 2に対応している必要がある。Route 53は対応途上のため、組み合わせ次第で実装が成立しないことがある。
- Cloudflareから割り当てられるNSホスト名（例：`xxx.ns.cloudflare.com`）は固定ペアで、自分で名指しすることはできない。Vanity Nameservers（自社ドメインのNS名で配信）はBusinessプラン以上が必要。
- DNS Firewallの専用Anycast IPは契約単位で固定だが、IP自体の永続性は契約継続が前提。クラスタ廃止と同時に失効するため、レジストラのglue更新が必要。
- DNS-onlyレコード（プロキシ無効）はCloudflareのDDoS吸収対象外であり、オリジンIPが直接露出する。プロキシ前提の防御を効かせたいレコードはオレンジ雲のままにする。
- Internal DNSはBetaであり、Enterprise(Zero Trust)契約とWARP配布が前提。GA前のため設定UIや挙動が変動する。
- AXFR/IXFRゾーン転送はTSIG必須。プレーン転送は認証なしの脆弱構成となるため、本番では使わない。
- 1.1.1.1 publicリゾルバはAuthoritative DNSと別プロダクトであり、ゾーン側の障害は1.1.1.1には影響しない（逆も同様）。混同しない。
- DNSSECのDSレコード登録はレジストラ側の操作であり、Cloudflareから自動で完結しない（CDS/CDNSKEY自動同期に対応するレジストラなら自動化可能）。

## 参考リンク
- Cloudflare DNS overview：https://developers.cloudflare.com/dns/
- Cloudflare DNS llms.txt：https://developers.cloudflare.com/dns/llms.txt
- DNSSEC：https://developers.cloudflare.com/dns/dnssec/
- Multi-signer DNSSEC：https://developers.cloudflare.com/dns/dnssec/multi-signer-dnssec/
- Secondary DNS：https://developers.cloudflare.com/dns/zone-setups/zone-transfers/
- DNS Firewall：https://developers.cloudflare.com/dns/dns-firewall/
- Internal DNS：https://developers.cloudflare.com/dns/internal-dns/
- DNS Analytics：https://developers.cloudflare.com/dns/additional-options/analytics/
- 1.1.1.1 Public Resolver：https://developers.cloudflare.com/1.1.1.1/
- Terraform `cloudflare_dns_record` / `cloudflare_dnssec` / `cloudflare_dns_firewall`：https://registry.terraform.io/providers/cloudflare/cloudflare/latest/docs

---
参照日: 2026-05-04
