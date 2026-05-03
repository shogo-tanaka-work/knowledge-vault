# Gateway (Cloudflare One)

## 一行サマリ
ユーザー・デバイスから出るDNS / HTTP / L3-L4トラフィックをCloudflareエッジに集約し、宛先・コンテンツ・アイデンティティ・デバイスポスチャを軸に評価して通す／止める／書き換えるSWG（Secure Web Gateway）兼DNSフィルタである。

## 解決する課題（Why）
社内端末を境界の中に閉じ込めるレガシープロキシは、リモートワーク・SaaS中心の業務形態とは相性が悪い。ローカルブレイクアウト後のトラフィックを誰もログしていない、悪性ドメインへのDNS解決を止められない、退職者の端末から社外ネットワークへ機密ファイルが流れても気づけない、といった盲点が常態化している。Cloudflare Gatewayはこれをエッジ集約型のSASEモデルで置き換え、以下を解決する。

- 全社のDNS / HTTP / L4トラフィックを単一の制御点で監視・制御。
- マルウェア配布ドメイン・フィッシングサイト・カテゴリ違反サイトの遮断。
- TLSを復号した上でのアンチウイルス・DLP・テナント制御・ブラウザ分離。
- WARP配下デバイスからインターネット／プライベートネットワーク双方への通信ポリシー統一。
- 監査・インシデント調査に耐えるリクエスト単位のログ保持。

## 主要機能（What）

### DNS フィルタ
Cloudflare Resolver（1.1.1.1）を経由するDNSクエリをポリシー判定して解決をブロック・上書きする層である。WARPなしでも、DNS Locations（拠点IP登録）やルーターのDNS設定だけで導入できるため、Gatewayのなかで最も導入障壁が低い。

- **Action**：Allow / Block / Override / Safe Search / YouTube Restricted Mode。
- **Selector**：Domain / Host / Content Categories / Security Categories / Resolved IP / Source IP / Location / Query Record Type / User Email / User Group / Country。
- **Content Categories / Security Categories**：CloudflareのIntelligenceフィードに基づく分類（成人向け / ギャンブル / マルウェア / フィッシング / 新規登録ドメイン 等）でドメイン群を一括制御。
- **DNS Locations**：固定IPの拠点はそのIPからのクエリにポリシーを紐付け、ローミング端末はWARPで識別する。

### HTTP インスペクション
WARP経由でTLSを復号し、HTTP/HTTPSペイロード単位の制御を行う層である。Cloudflareルート証明書、または企業所有の証明書を端末に配布することが前提となる。

- 主要機能：URL / Host / File Type ブロック、Anti-Virus（アップロード・ダウンロードのスキャン）、DLP（クレジットカード番号・社内識別子等の流出検知）、Tenant Control（自社M365テナントのみ許可など）、Browser Isolation（リモートブラウザ隔離）、Quarantine、カスタムBlock Page。
- Selector：URL / Domain / Host / HTTP Method / File Type / Application / Content Categories / Country / Source IP / User / Group / Device Posture。
- Browser Isolation（RBI）と組合せると、未分類サイトを「読めるが貼り付け・ダウンロード不可」のRead-onlyモードで開く運用が可能。

### Network ポリシー（L3-L4）
HTTPに収まらないトラフィック（SSH / RDP / SMTP / 任意のTCP・UDP）を制御する層である。Magic WAN / GRE / IPSec / WARPで集約したパケットをIP・ポート・プロトコル・SNI単位で評価する。

- Action：Allow / Block / Network Override（宛先IP・ポートの書き換え）。Audit SSHはDeprecatedで、SSH監査はAccess for Infrastructureに移行している。
- Selector：Source/Destination IP・Port、Protocol、SNI、Application、Content Categories、Virtual Network、User、Group、Device Posture。
- Cloudflare Tunnelで公開した社内ネットワーク（Private Network）への到達制御も同じレイヤで書ける。

### WARP クライアント
Gatewayのフル機能（HTTP復号・Device Posture・User identity）を引き出す前提となるエンドポイントエージェントである。MDM配布（Intune / Jamf / Kandji）でデバイス登録し、Splitトンネルで「会社が見たいトラフィック」だけをCloudflareに送る運用が現実的である。

- Device Postureチェック：OSバージョン / ディスク暗号化 / EDR稼働 / 証明書存在 / シリアルナンバーリスト など。
- User identity：Cloudflare Accessで認証したIdPユーザーをそのままGatewayポリシーのSelectorに利用できる。
- Split Tunnel：Include / Excludeモードで、業務SaaSのみ流す／プライベート帯域は除外、といった設計が可能。

### Logs
すべてのDNS / Network / HTTPリクエストはGateway Activity Logに記録される。Logpushを使えばS3 / R2 / Splunk / Datadog / Sentinelに継続転送でき、SIEM連携が成立する。Free / Standardはダッシュボード上での保持期間が短く、長期保管はLogpush（Enterprise）が前提となる。

## アーキテクト視点：いつ選ぶか

### 適しているシーン
- VPN撤廃・SASE移行の文脈で、SWG / DNSフィルタを単一ベンダーで揃えたい中小〜中堅企業。
- 「悪性ドメインを止めたい」だけが先に欲しいケース（DNS Locations + Content Categoriesで即日導入）。
- 全社員にWARPを配り、Tunnelで社内アプリも公開している組織。Access（誰が）+ Tunnel（どこへ）+ Gateway（何を）が一気通貫で書ける。
- Cloudflareエッジを既にCDN / WAFで使っている組織にとって、ログ・アイデンティティ・証明書配布の運用基盤を流用できる。
- 50ユーザー以下のスタートアップで、コストゼロでSWGを導入したいケース。

### 適していないシーン
- ZscalerやNetskopeに既に大規模投資済みで、CASB / SSPM / Advanced DLP / UEBAなどフル機能を業務要件として使い倒している組織。CloudflareのDLP・CASB相当機能はEnterprise領域では追従途上である。
- オンプレミスのレガシーWindowsアプリ群が、TLS復号と相性の悪い独自プロトコルで通信しているケース。HTTPインスペクションは個別にBypass設計が必要。
- WARPを配布する運用体制（MDM・端末ポリシー）がない組織。DNSフィルタ単独運用で止めるのが現実解。
- 政府・防衛系で「特定国の事業者にトラフィックを集約してはならない」という制約がある場合。

## 競合・代替

| 観点 | Cloudflare Gateway | Zscaler ZIA | Netskope SWG | Cisco Umbrella |
|---|---|---|---|---|
| 出自 | CDN / Anycastネットワーク | 純血SASE / SWG専業 | CASBから拡張したSSE | DNSフィルタ（旧OpenDNS）から拡張 |
| DNSフィルタ | 標準（無料枠あり） | 別モジュール | 別モジュール | 本職 |
| HTTPインスペクション | 標準・TLS復号対応 | 高機能・成熟 | 高機能・成熟 | SIG add-on |
| L4 / Network | 統合（Magic WAN連携） | 専用ZPA / Cloud Connector | NewEdgeで対応 | SIG / Tunnel |
| CASB / Advanced DLP | 追従途上 | 強力 | 最強クラス | 中位 |
| Browser Isolation | 標準同梱（CloudflareのRBI） | 別ライセンス | 別ライセンス | 別ライセンス |
| 価格 | 50ユーザー無料 / $7〜 | 高価（要見積もり） | 高価（要見積もり） | $2.20〜（DNS Essentials） |
| 強み | エッジ統合・Access/Tunnelとの結合・無料枠 | エンタープライズでの成熟・運用ノウハウ | データ中心SSE・CASB成熟度 | DNSフィルタの精度・既存Cisco資産との相性 |
| 弱み | 大規模CASB / UEBA要件は弱い | 高コスト・複雑 | 高コスト・PoP網はCloudflareに劣る | DNS主体でHTTP / L4は後発 |

CloudflareはAccess / Tunnel / Gateway / Browser Isolation / DLPを単一プレーンで束ねるアーキテクチャ的なシンプルさが最大の差別化要因である。逆にZscaler / Netskope水準の成熟したCASB・SSPMが業務要件の中核なら、現時点では併用または代替が妥当である。

## 料金

- **Free（Zero Trust Free）**：50ユーザーまで。DNSフィルタ・HTTPインスペクション・Network ポリシー・WARP・基本Browser Isolation（限定的）が含まれる。Activity Logのダッシュボード保持期間は短い。
- **Standard（Pay-as-you-go）**：$7/ユーザー/月程度から、ユーザー数に応じた従量課金。51ユーザー目以降が課金対象、Free機能の上限拡張・SLA向上が中心。
- **Enterprise**：年間契約。Logpush、Advanced DLP、CASB、SCIM強制再評価、User Risk Score、Magic WAN統合、専用PoP・専用IP、サポートSLAなど。SaaS全社展開や監査要件のある組織はここを前提に設計する。

Gateway / Access / Tunnelは同じZero Trustライセンスにバンドルされており、「Gatewayだけ」「Accessだけ」を別契約する形にはならない。50ユーザー無料枠を最大限活かし、必要になった機能（Logpush・DLP）でEnterpriseに上がる、という段階導入が現実的である。

## CLI / IaC 操作例

### Terraform（cloudflare provider v5）
```hcl
# DNS: マルウェア・フィッシングカテゴリをブロック
resource "cloudflare_zero_trust_gateway_policy" "block_malware_dns" {
  account_id  = var.account_id
  name        = "Block malware/phishing (DNS)"
  description = "Security categories block at DNS layer"
  precedence  = 1000
  enabled     = true
  action      = "block"
  filters     = ["dns"]
  traffic     = "any(dns.security_category[*] in {68 80 178 83})"
}

# HTTP: 業務時間外にSNS系をBrowser Isolationへ
resource "cloudflare_zero_trust_gateway_policy" "isolate_social" {
  account_id  = var.account_id
  name        = "Isolate social media"
  precedence  = 2000
  enabled     = true
  action      = "isolate"
  filters     = ["http"]
  traffic     = "any(http.request.uri.content_category[*] in {5})"
  identity    = "any(identity.groups.name[*] in {\"general-staff\"})"
}

# Network: 社外SSHを原則ブロック、踏み台のみ許可
resource "cloudflare_zero_trust_gateway_policy" "block_egress_ssh" {
  account_id = var.account_id
  name       = "Block egress SSH"
  precedence = 3000
  enabled    = true
  action     = "block"
  filters    = ["l4"]
  traffic    = "net.dst.port == 22 and not(net.dst.ip in {203.0.113.10})"
}
```

### WARP デバイス登録（MDM経由の例）
```bash
# macOS（Jamf / Kandjiでconfig profile配布が本筋。手動検証用）
sudo warp-cli registration new --team-name acme

# 接続・ステータス確認
warp-cli connect
warp-cli status

# Gateway DoH接続のみ使う場合（HTTP/L4は流さない）
warp-cli mode doh
```

### DNS Location（拠点IPベース）の登録
オフィス固定IPからのDNSクエリにポリシーを当てる場合は、Zero Trustダッシュボード「Gateway → DNS Locations」で拠点IPv4/IPv6を登録するか、APIで`POST /accounts/{id}/gateway/locations`を叩く。

## 制限・注意点
- HTTPインスペクションはCloudflareルート証明書（または持ち込み証明書）の端末配布が前提である。BYOD・非管理端末ではDNS / Networkまでに留めるのが現実解。
- 一部アプリ（Apple Push、銀行系、証明書ピン留めSDK）はTLS復号と相性が悪く、ホスト単位でDo Not Inspect（バイパス）設定が必要。
- Logpushによる長期ログ転送はEnterprise機能であり、Free / Standardはダッシュボード保持に依存する。コンプライアンス要件があるなら最初からEnterprise前提で設計する。
- Network ポリシーのprecedence管理はTerraform provider v4にハッシュ計算起因の制約があり、v5への移行が推奨される。
- Cloudflare AccessやTunnelは前提として別記事を参照。Gatewayは「外向きトラフィックの制御」、Accessは「内向きアプリへの認可」、Tunnelは「内部の到達経路」と役割が分かれている。
- 50ユーザーFreeはAccess / Gateway / Tunnel合算の制限であり、Gateway単独の枠ではない点に注意。
- WARPのSplit Tunnelを誤設定すると業務SaaSがCloudflareを経由しない（＝ポリシーが効かない）状態になる。Includeモード運用とテストが必須。

## 参考リンク
- Cloudflare Gateway Policies：https://developers.cloudflare.com/cloudflare-one/policies/gateway/
- DNS Policies：https://developers.cloudflare.com/cloudflare-one/policies/gateway/dns-policies/
- HTTP Policies：https://developers.cloudflare.com/cloudflare-one/policies/gateway/http-policies/
- Network Policies：https://developers.cloudflare.com/cloudflare-one/policies/gateway/network-policies/
- WARP client：https://developers.cloudflare.com/cloudflare-one/connections/connect-devices/warp/
- Zero Trust Plans：https://www.cloudflare.com/plans/zero-trust-services/
- Terraform `cloudflare_zero_trust_gateway_policy`：https://registry.terraform.io/providers/cloudflare/cloudflare/latest/docs/resources/zero_trust_gateway_policy
- Cloudflare One llms.txt：https://developers.cloudflare.com/cloudflare-one/llms.txt

---
参照日: 2026-05-03
