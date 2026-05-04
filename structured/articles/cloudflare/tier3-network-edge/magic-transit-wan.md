# Magic Transit / Magic WAN

## 一行サマリ
Magic Transitは「インターネット側から自社の既存IP帯域（最低/24）に来るトラフィック」をBGPアナウンスでCloudflareエッジに引き込み、Anycast PoPでDDoS吸収・L3-L4ファイアウォール適用後にGRE/IPsec/CNI経由で自社データセンターへ戻す“DDoS防御つきインターネットゲートウェイ”である。一方Magic WANは「自社拠点・クラウド・リモートユーザー（WARP）相互の社内通信」をCloudflareネットワーク上のオーバーレイとして束ね、MPLS・ハブ&スポークVPNを置き換えるWANaaS（SD-WAN）であり、トラフィックの“向き”と“目的”が真逆の製品である。

## 解決する課題（Why）
従来型のオンプレ・キャリアMPLS網は、DDoS被害・拠点増加に伴うフルメッシュVPN管理・クラウド直行通信のバックホールという3つの構造課題を抱える。リージョナルなScrubbing Centerに依存するDDoS防御は攻撃源から遠く、回線容量を超えれば即破綻する。MPLSは月額が高く新拠点追加に数週間〜数ヶ月かかる。SaaS全盛時代に全トラフィックを本社経由で出すと帯域とレイテンシが爆発する。Cloudflareはこれを以下のように解き直す。

- 既存パブリックIP帯域（/24以上）をCloudflare Anycastで世界310拠点超に同時アナウンスし、攻撃を発信源近傍で吸収する（Magic Transit）。
- 拠点・VPC・リモートユーザーを単一オーバーレイに集約し、フルメッシュ管理を不要化（Magic WAN）。
- L3-L4ファイアウォール（Magic Firewall）をエッジで適用し、オンプレFW筐体を撤去可能にする。
- パブリックインターネットを通らないCNI（専用線・Equinix/Megaport仮想接続）で帯域・遅延・コストを安定化。
- WARPクライアントと統合し、リモート社員も同じWANオーバーレイの“拠点”として扱える。

## 主要機能（What）

### Magic Transit
顧客のパブリック`/24`以上のプレフィックスをCloudflareがBGPでアナウンスし、AnycastでL3トラフィックを吸い上げ、洗浄後に顧客側へ戻す“on-ramp from the Internet”である。Always-On / On-Demand（攻撃時のみ切替）の両モードに対応する。

- **BGP Advertisement**：BYOIP（Bring Your Own IP）で顧客プレフィックスをCloudflareがアナウンス。Cloudflare-leased IP（`/24`未満の場合）も選択可。
- **Anycast 吸収**：世界中のPoPで同一プレフィックスを受け、攻撃源最寄りで遮断。容量は数百Tbps級。
- **Advanced DDoS**：L3/L4の振幅増幅・SYN flood・UDP reflectionをML+シグネチャで自動緩和。SLAは攻撃検知3秒・緩和10秒以内。
- **戻し経路（Return Path）**：GRE トンネル / IPsec トンネル / CNI（専用線）から選択。Direct Server Return（DSR）構成で、レスポンスはCloudflareを経由せず直接インターネットへ返す設計が標準。
- **Magic Firewall 統合**：エッジでL3-L4ルールを適用し、不要プロトコル・国・IPを落とす。
- **トンネルヘルスチェック・トラフィックステアリング**：複数トンネルの優先度設定とフェイルオーバー。

### Magic WAN
拠点・クラウドVPC・リモートWARPユーザーを単一オーバーレイで結ぶSD-WAN/WANaaS。MPLSとハブ&スポークIPsecを置き換える“Cloudflareをバックボーンとして使う”発想である。

- **Sites & Tunnels**：各拠点を「Site」として登録し、IPsec / GRE トンネルで近傍PoPに接続。Site配下の内部プレフィックスを静的ルートまたはBGPで広告。
- **Magic WAN Connector**：Cloudflareが配布する仮想/物理アプライアンス（x86 / ARM、KVM・VMware・AWS AMI等）。ZTP（Zero-Touch Provisioning）でオンサイト設定不要、SD-WAN相当のアンダーレイ束ねを担う。
- **WARP 連携**：リモート社員のWARPクライアントをMagic WANの“仮想Site”として扱い、拠点リソースへ直接到達できる。Gateway / Accessポリシーがそのまま適用可能。
- **Multi-Cloud Networking**：AWS / Azure / GCPのVPCをディスカバリし、Cloud Connector経由でWAN参加。クラウド間通信もCloudflareバックボーンを通る。
- **BGP ピアリング**：Site側ルーターとPoP間でBGPセッションを張り、プレフィックス追加削除を動的化。
- **Magic Firewall 統合**：拠点間（east-west）通信にも同じL3-L4ポリシーを強制。

### Magic Firewall
Magic Transit / Magic WANに付帯するクラウドL3-L4 FWaaS。Wireshark構文ベースの「Cloudflare Rules language」でパケットヘッダ・ペイロード長・プロトコルを評価し、エッジで遮断する。IDS（Intrusion Detection System）として既知シグネチャの監視も提供。オンプレのCisco ASA / Fortinet筐体を撤去し、ルール管理をAPI/Terraform化する用途が中心。Magic Transit / Magic WANの契約に内包され、単独販売はされない。

### Cloudflare Network Interconnect (CNI)
顧客ネットワークをパブリックインターネットを介さずCloudflareへ直接接続する物理/仮想クロスコネクト。

- **Direct CNI**：Cloudflare PoPと同居するデータセンター内（Equinix / Coresite等）で物理ポートを直接ケーブル接続。
- **Partner CNI**：Equinix Fabric / Megaport / Console Connect / PacketFabric等のNaaSパートナー経由で仮想クロスコネクト。物理同居なしに数分でプロビジョニング可能。
- **Cloud CNI**：AWS Direct Connect / Azure ExpressRoute / Google Partner Interconnectからの専用接続。
- **Dataplane v1 / v2**：v1はGREトンネル前提でMagic Transit DSR・Egress・Zero Trustに対応。v2はCustomer Connectivity Router（CCR）ベースでGRE不要のシンプルなBGPルーティングを提供。
- Magic Transit/WANの“最終マイル”として、回線品質・MTU・レイテンシを安定化させる。

### WARP-Magic 連携
WARPクライアントはMagic WANの「リモートSite」として動作し、社員端末からWAN内のプライベートIPに直接到達できる。Gateway（外向きSWG）+ Access（内向き認可）+ Magic WAN（拠点間）+ WARP（端末）が単一プレーンで設計でき、SASE/SSE全機能を1ベンダーに集約できるのがCloudflareの構造的優位である。

## アーキテクト視点：いつ選ぶか

### Magic Transit を選ぶシーン
- 自社で`/24`以上のIP帯域を保有しており、ゲーミング・金融・公共系等で大規模L3/L4 DDoSを常時警戒する組織。
- オンプレDC・コロケーションを残しつつ、上流ISPのDDoS Scrubbingでは容量・SLA不足な場合。
- WAFだけでなく、HTTP以外のプロトコル（DNS権威 / SMTP / ゲームサーバ / VoIP）も保護対象に含むケース。
- 公開IPを変えずにCloudflareへ移行したい（既存DNSレコード・パートナー連携の更改コストを抑えたい）ケース。

### Magic WAN を選ぶシーン
- 数十〜数百拠点をMPLSまたはハブ&スポークIPsecで運用しており、回線費・運用負荷が肥大化している組織。
- 拠点・マルチクラウド・リモート社員をひとつのWANポリシー面で扱いたい（SASE移行の一環）。
- 既にCloudflare One（Access / Gateway / WARP）を導入済みで、L3レベルの拠点間通信もCloudflareに寄せたい。
- 新規拠点立ち上げが頻繁で、回線開通リードタイムを数日以内に短縮したい。

### 適していないシーン
- 自社IPを持たず、Webサービスの保護だけが目的なら通常の**Cloudflare WAF / Proxy（Tier1）で十分**。Magic Transitはオーバースペックで高額。
- 規制で「特定海外事業者にL3トラフィックを集約してはならない」制約がある政府・防衛系。
- 数拠点しかない小規模組織でMPLS課題が顕在化していない場合、Magic WANは投資回収が遅い。
- リアルタイム性が極端に重要（金融HFT・産業制御）な拠点間通信で、Cloudflare PoP経由のレイテンシが許容できないケース。
- 既にAWS Cloud WAN / Azure Virtual WANに全面投資済みで、クラウド出口がそちらに寄っている場合。

## 競合・代替

| 観点 | Cloudflare Magic Transit/WAN | AWS Cloud WAN | Megaport (MCR) | Aryaka | Zscaler ZIA/ZPA | Cato Networks | Versa SASE |
|---|---|---|---|---|---|---|---|
| 出自 | Anycast CDN / DDoS防御 | AWSグローバルバックボーン | NaaS / クロスコネクト | マネージドSD-WAN（FlexCore） | 純血SASE / SWG | SD-WAN+SSEのフル統合PoP | SD-WAN（Versa OS）+SSE |
| L3 DDoS 防御 | ◎（数百Tbps Anycast） | △（AWS Shield別） | ✕ | △ | △（HTTPS中心） | ○ | ○ |
| 拠点間 SD-WAN | ○（Magic WAN Connector） | ◎（AWS内優位） | ◎（NaaS） | ◎（マネージド込み） | △（ZPA中心） | ◎（SASE統合） | ◎（機能最多） |
| BYOIP / BGP | ◎（標準） | ○ | ○ | △ | ✕ | △ | ○ |
| FWaaS / SWG | Magic Firewall + Gateway | NW Firewall | パートナー経由 | パートナー経由 | ◎（本職） | ◎（統合） | ◎（統合） |
| クラウド接続 | CNI（Direct/Partner/Cloud） | AWSネイティブ | 全クラウド対応 | 全クラウド対応 | クラウドコネクタ | 統合PoP | 統合PoP |
| 価格 | Enterprise契約（要見積） | AWS従量+Attachment課金 | ポート+VXC従量 | 高額・マネージド込み | 高額（ユーザー課金） | 中〜高（バンドル） | 高額（機能フル） |
| 強み | DDoS実績・Anycast網・Cloudflare One統合 | AWSとの密結合・運用容易 | 物理接続の柔軟性 | フルマネージド・運用代行 | SASEの成熟度 | 単一ベンダーSASE完結 | 機能網羅性・カスタマイズ |
| 弱み | 物理回線・ラストワンマイルは別途 | AWS外の拠点接続は別工夫 | セキュリティ機能なし | 高コスト・ロックイン | L3/拠点間は弱い | PoP数はCloudflareに劣る | 運用が複雑 |

CloudflareはDDoS防御の容量・PoP数・Cloudflare Oneとの統合という3点で他に代替が利きにくい。逆に「拠点間SD-WANの機能網羅」だけを軸にするとCato/Versaのほうが成熟しており、AWS中心の組織はCloud WANと比較する価値がある。Megaport/Equinixは“競合”というよりCloudflare CNIの**パートナー側**として併用する関係である。

## 料金
Magic Transit / Magic WAN / Magic Firewall / CNIはいずれも**Enterprise専用・契約ベース**であり、公開価格は存在しない。一般的に以下の軸で見積もられる。

- **Magic Transit**：保護対象帯域幅（Mbps / Gbps）、保護対象プレフィックス数、Always-On / On-Demand、トンネル本数、SLAレベル。
- **Magic WAN**：Site数、契約帯域、Connectorライセンス数、Cloud Connector数、WARPシート数。
- **Magic Firewall**：Magic Transit / WAN契約に内包（単独購入不可）。ルール数・IDS有効化で上振れ。
- **CNI**：Direct CNIはポート費（年額）、Partner CNIはNaaS側ポート+VXC費+Cloudflare側接続費の合算、Cloud CNIは各クラウドのDirect Connect/ExpressRoute側課金が別途発生。

PoC段階ではAlways-OnではなくOn-Demand Magic Transitから入る、CNI なしのIPsec接続で開始してから物理接続にアップグレードする、というステップで初期費を抑えるのが定石である。

## CLI / API 例
Cloudflare APIはアカウントスコープのRESTで、`/accounts/{account_id}/magic/...`配下にSites / Connectors / IPsec Tunnels / GRE Tunnels / Static Routesが並ぶ。以下はcurl例。

### IPsec トンネル作成
```bash
curl -X POST "https://api.cloudflare.com/client/v4/accounts/${ACCOUNT_ID}/magic/ipsec_tunnels" \
  -H "Authorization: Bearer ${CF_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "tokyo-dc-ipsec-01",
    "customer_endpoint": "203.0.113.10",
    "cloudflare_endpoint": "162.159.65.1",
    "interface_address": "10.212.0.1/31",
    "description": "Tokyo DC primary IPsec to NRT PoP",
    "psk": "REPLACE_WITH_STRONG_PSK",
    "health_check": {
      "enabled": true,
      "type": "request",
      "rate": "mid"
    }
  }'
```

### GRE トンネル作成（Magic Transit戻し経路）
```bash
curl -X POST "https://api.cloudflare.com/client/v4/accounts/${ACCOUNT_ID}/magic/gre_tunnels" \
  -H "Authorization: Bearer ${CF_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "tokyo-dc-gre-01",
    "customer_gre_endpoint": "203.0.113.10",
    "cloudflare_gre_endpoint": "162.159.66.1",
    "interface_address": "10.224.0.1/31",
    "mtu": 1476,
    "ttl": 64,
    "description": "Magic Transit return path"
  }'
```

### Magic WAN Site と静的ルート作成
```bash
# Site作成
curl -X POST "https://api.cloudflare.com/client/v4/accounts/${ACCOUNT_ID}/magic/sites" \
  -H "Authorization: Bearer ${CF_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "osaka-branch",
    "description": "Osaka branch office",
    "location": { "lat": "34.6937", "lon": "135.5023" }
  }'

# 拠点配下プレフィックスをトンネル経由でルーティング
curl -X POST "https://api.cloudflare.com/client/v4/accounts/${ACCOUNT_ID}/magic/routes" \
  -H "Authorization: Bearer ${CF_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "prefix": "10.10.20.0/24",
    "nexthop": "10.212.0.0",
    "priority": 100,
    "description": "osaka-branch internal subnet"
  }'
```

### Magic Firewall ルール（特定国からのSSHを遮断）
```bash
curl -X POST "https://api.cloudflare.com/client/v4/accounts/${ACCOUNT_ID}/magic/schemas/network_firewall/rulesets" \
  -H "Authorization: Bearer ${CF_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "block-foreign-ssh",
    "expression": "ip.geoip.country in {\"KP\" \"RU\"} and tcp.dstport == 22",
    "action": "block",
    "enabled": true
  }'
```

実運用ではTerraform `cloudflare` providerの `cloudflare_magic_wan_*` / `cloudflare_magic_firewall_ruleset` リソースで宣言的に管理するのが主流である。

## 制限・注意点
- **BGPアナウンスは原則`/24`単位**。`/25`以下は自社プレフィックスとしてはアナウンスできず、Cloudflare-leased IPの利用が必要になる。
- **MTU設計が要**。GREは1476、IPsecは1436前後が目安。クライアント側でPath MTU Discoveryが効かない経路（ICMP遮断）だとTCP通信が無言で詰まる。設計段階でMSS Clamping必須。
- **DSR（Direct Server Return）構成が前提**。下り（顧客→クライアント）はCloudflareを通らないため、戻り経路のFW・NATがCloudflareの送信元IPを許可している必要がある。
- **Encrypted Magic Transit**（IPsec）はGRE比でスループットが落ちる。高帯域はGRE+別途暗号化、またはCNIでパブリック経路を回避する設計が無難。
- **リージョン選定**：日本拠点ならNRT/HND/KIX/ITM等の最寄りPoPに紐付くようBGPコミュニティとSite Locationを設定する。グローバルAnycastのまま放置すると意図せず海外PoP経由になることがある。
- **On-Demand Magic Transit**は攻撃検知時のみBGPを切り替えるため、平時はCloudflareを経由しない。Always-Onと比べてPoCは安価だが、切替時に数秒のセッション断が発生し得る。
- **Magic WAN ConnectorはZTP前提**。MDM的な運用基盤がない場合、初期キッティングで詰まる。物理アプライアンスはサポート国・物流リードタイムを事前確認。
- **CNI Partner経由**は中継NaaS（Megaport/Equinix）側のMTUとVLAN設計に依存する。両端でMTU 1500を確保できるかが性能の分かれ目。
- **Magic Firewall**は単独販売されない。FWaaSだけ欲しいというユースケースには使えず、Magic Transit/WAN契約とセット。
- **Cloudflare One（Gateway/Access/WARP）**との料金体系は別。SASE全部入りで見せられる見積もりでも、内訳上はZero Trustライセンス+Magic WAN+Magic Transit+CNIに分かれる点に注意。

## 参考リンク
- Magic Transit：https://developers.cloudflare.com/magic-transit/
- Magic WAN：https://developers.cloudflare.com/magic-wan/
- Magic Firewall（Network Firewall）：https://developers.cloudflare.com/magic-firewall/
- Cloudflare Network Interconnect：https://developers.cloudflare.com/network-interconnect/
- Magic WAN Connector：https://developers.cloudflare.com/magic-wan/configuration/connector/
- Magic Transit BYOIP：https://developers.cloudflare.com/byoip/
- Cloudflare API（Magic Transit/WAN）：https://developers.cloudflare.com/api/operations/magic-ipsec-tunnels-list-i-psec-tunnels
- Terraform `cloudflare` provider：https://registry.terraform.io/providers/cloudflare/cloudflare/latest/docs

---
参照日: 2026-05-04
