# Spectrum

## 一行サマリ
HTTP/HTTPSに収まらない任意のTCP/UDPアプリケーション（SSH・Minecraft・MQTT・RDP・FTP・カスタムゲームプロトコル等）を、Cloudflare Anycastエッジでリバースプロキシし、L3/4 DDoS緩和・オリジンIP秘匿・アクセス制御・Argo経路最適化を一括で適用するL4プロキシサービスである。

## 解決する課題（Why）
ゲームサーバー・SSH踏み台・産業用MQTTブローカー・社内RDPゲートウェイのような「HTTP化できない」サービスを公開すると、CDN/WAFの恩恵を受けられず、オリジンIPがそのままインターネットに露出する。一度IPが特定されればL3/4 DDoSで簡単に落ち、IPローテーションで逃げ続けるか、回線会社のクリーンパイプ契約に頼るしかない。Spectrumはこの状況を以下のように解決する。

- オリジンIPをCloudflare Anycast IPの背後に隠蔽し、IPベースの直撃DDoSを物理的に届かなくする。
- Cloudflareの無制限L3/4 DDoS緩和をHTTP以外のプロトコルにも適用する（Pro以上は緩和能力に追加課金なし）。
- IP Access Rulesで国/ASN/IPレンジ単位のホワイトリスト/ブラックリストを、ゲームサーバーやSSHにも適用する。
- Origin Authentication（mTLS）でCloudflareエッジ↔オリジン間を相互認証し、IPフィルタすり抜けからオリジンを守る。
- Argo Smart Routingでゲーム/対戦系のRTTジッタを実測ベースで最適化する。
- Load Balancingと組み合わせ、TCP/UDPサービスにもヘルスチェック・ジオステアリングを適用する。

## 主要機能（What）

### TCP/UDP Application
Spectrumの中核オブジェクト。「edge側のhostname:port」と「origin側のIP:port」をマッピングし、プロトコル（tcp/udp）・TLS終端（off / flexible / full / strict）・Proxy Protocol（v1 / v2 / Simple）を指定する。Edge IPはAnycast Dynamic（Cloudflareの共有IPプール）またはStatic/Reserved IP（Enterprise）から選択する。

- DNSターゲットはCNAME（zone内hostname）またはApex（ルートドメイン）を指定可能。
- Edge portとOrigin portは異なる値を取れる（例：edge 25565 → origin 25600）。
- 単一Anycast IPの背後に複数アプリケーションを束ねられる（ポート単位で多重化）。

### Origin Authentication (mTLS)
Cloudflareエッジ↔オリジン間でmTLSを張り、「このTLSセッションは間違いなくCloudflareから来た」とオリジン側で検証する仕組み。Cloudflare Origin CAが発行するクライアント証明書をエッジが提示し、オリジンのTLSサーバーがCAチェーン検証で受理する。これによりオリジンIPが何らかの形で漏れても、直接接続を拒否できる。

### IP Access Rules
ゾーン/アカウント単位のIP / CIDR / ASN / Country単位のAllow / Block / Challenge / JS Challengeルールが、Spectrumで公開したTCP/UDPサービスにも自動適用される。SSH踏み台を「日本のオフィスIPと特定VPN ASNのみAllow、それ以外Block」といった運用がGUI/APIで完結する。

### Argo Smart Routing 連動
Argoを契約している場合、Spectrumトラフィックも実測RTTベースの最適経路でCloudflareバックボーンを通す。BGPデフォルトでは中継ASを跨ぐ非効率な経路に落ちるリージョン間（例：日本↔ブラジル、APAC↔EU）で、対戦ゲーム・株取引・SSHのレスポンス改善に効く。

### Load Balancing 連動
Cloudflare Load Balancerをoriginに指定でき、TCPヘルスチェック（接続成功 or 任意のバナー文字列マッチ）でフェイルオーバー、ジオステアリング（最寄りリージョンへ振る）、加重ステアリング、Session Affinityを適用できる。「Tokyo / Singapore / Frankfurt にゲームサーバーを置き、プレイヤーの最寄りに飛ばす」がL4のまま実現する。

### Wireshark / PCAP 連携
Enterpriseプランでは、特定Spectrumアプリのエッジ受信パケットをCloudflareダッシュボード/APIからPCAP形式でキャプチャできる（Magic Network Monitoring / PCAPs機能）。L4トラブル（TCP RSTの発生源、独自プロトコルのハンドシェイク失敗）をエッジ側から直接観測できる。

## アーキテクト視点：いつ選ぶか

### 適しているシーン
- Minecraft / FPS / MOBA等のゲームサーバーをDDoS被害から守りたいケース。Anycast IP + L3/4無制限緩和の組み合わせが本職。
- 全社員に踏み台SSHを公開する必要があり、IP Access RulesでBYOD/出張IPまでホワイトリスト管理したい運用（ただし長期運用ではAccess for Infrastructureの方が監査要件に強い）。
- 産業IoT / コネクテッドカーのMQTTブローカーを公開し、デバイス→Cloudflare→オリジンの経路でTLS/mTLSを終端したい。
- カスタムTCPプロトコル（独自ゲームメタサーバ、金融系FIX、監視系Syslog等）でCDN/WAFの恩恵を受けたい。
- 既存のCloudflare契約にArgo / Load Balancingがあり、HTTP以外の社内サービスにも経路最適化と冗長化を波及させたい。

### 適していないシーン
- HTTP/HTTPSアプリ。通常のCloudflareプロキシ（オレンジクラウド）+ Workers + Cacheで十分であり、Spectrum経由はキャッシュもWAFも効かないため筋が悪い。
- TLS終端を絶対にオリジンでしか行いたくないが、Cloudflareでアプリ層WAFも掛けたいというケース（Spectrumはペイロード検査をしない）。
- 任意UDPやカスタムTCPポートが要件で、契約がBusiness以下のケース。Pro/Businessは限定ポート（SSH 22 / Minecraft 25565等）しか開けられず、Enterprise契約が前提になる。
- ゼロトラスト原則でSSHを完全に潰し、ブラウザベースのSSHコンソールに置き換えたい組織。Cloudflare Tunnel + Access for Infrastructure（旧SSH over Access）の方が監査・録画・短期証明書発行まで一気通貫で揃う。
- 大量の小さなUDPパケット（VoIP / WebRTC SFU / リアルタイム音声）。SpectrumはL4プロキシであり、特定のリアルタイム最適化（Cloudflare Calls / Realtime SFU）は別製品である。

## 競合・代替

| 観点 | Cloudflare Spectrum | AWS NLB + Shield Advanced | Fastly TCP/TLS | Akamai App Layer L4 (Prolexic Connect) | Path.net | Imperva Network DDoS |
|---|---|---|---|---|---|---|
| 提供形態 | Anycast L4リバースプロキシ | リージョナルNLB + DDoS保護 | TLSターミネーション中心 | BGP経路転換 + L4スクラビング | ゲーム特化スクラビング | BGP / GREトンネル型スクラビング |
| 任意TCP/UDP | Enterprise | NLBで任意ポート可、UDPも可 | TLS over TCPが中心、任意UDPは弱い | 任意TCP/UDP対応 | 任意TCP/UDP（ゲーム特化） | 任意TCP/UDP対応 |
| Anycast | 全PoP | 単一リージョン（Global Acceleratorで補完） | 全PoP | Anycast scrubbing | 専用Anycast | スクラビングセンター |
| DDoS緩和 | 無制限・追加課金なし | Shield Advanced契約必須・年$3kベース＋越過費用免除 | 標準DDoS+追加契約 | 業界トップ級・契約ベース | ゲーム特化大容量 | 大容量・スクラビング型 |
| ゲームサーバー実績 | 多数（Minecraft / Hypixel事例） | 一般用途中心 | 少なめ | エンタープライズ寄り | 本職 | エンタープライズ寄り |
| mTLS to Origin | Origin Authentication標準 | NLB単体では不可（ターゲット側で実装） | 対応 | 対応 | 対応 | 対応 |
| IP Access Rules | ダッシュボード即時 | Security Groups / NACLで実装 | ACL記述 | 個別設定 | 管理画面 | 管理画面 |
| 価格モデル | プラン+Enterprise契約 | リソース課金+Shield Advanced固定費 | 従量課金 | 高額・契約ベース | 中価格・ゲーム向け | 高額・契約ベース |

CloudflareのAnycast網と「L3/4 DDoS緩和の超過課金なし」モデルは、ゲーム/SSH/カスタムプロトコル領域では価格性能比で他を圧倒する。一方、エンタープライズ大規模回線（数百Gbpsの帯域保証付きスクラビング）はAkamai Prolexic / Imperva側に分がある。

## 料金

- **Free / Pro**：Pro以下はSpectrumの利用範囲が極めて限定的で、SSH（TCP 22）/ Minecraft（TCP 25565）等の特定アプリケーション向けプリセットのみ。任意ポートやカスタムTCPプロトコルは不可。
- **Business**：Pro範囲に加えて一部追加プロトコル（メール系・限定ポート）が利用可能。それでも任意TCP/UDPは開けない。
- **Enterprise**：任意のTCP/UDPポート、UDPアプリケーション全般、Reserved/Static IP、Origin Authentication、Argo連動、Load Balancing連動、PCAPs、BYOIPがフルに使える。Spectrum自体がEnterpriseアドオン契約として価格設定され、帯域・接続数・対象アプリケーション数ベースで個別見積もりとなる。

ProプランでSSH踏み台をCloudflare経由にする、というのが小規模ユースケースとして成立する数少ない選択肢である。Minecraft運営はProから始められるが、UDPベースのゲーム（多くのFPS / RTS）はEnterprise必須となる点に注意。

## CLI / API 例

### Spectrumアプリ作成（curl）
```bash
# SSH踏み台（Pro以上で可）。edge 22 → origin 192.0.2.10:22
curl -X POST "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/spectrum/apps" \
  -H "Authorization: Bearer $CF_API_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{
    "protocol": "tcp/22",
    "dns": { "type": "CNAME", "name": "ssh.example.com" },
    "origin_direct": ["tcp://192.0.2.10:22"],
    "ip_firewall": true,
    "proxy_protocol": "v2",
    "tls": "off",
    "edge_ips": { "type": "dynamic", "connectivity": "all" }
  }'

# カスタムUDPゲーム（Enterprise必須）。edge 30000 → origin 198.51.100.20:30000
curl -X POST "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/spectrum/apps" \
  -H "Authorization: Bearer $CF_API_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{
    "protocol": "udp/30000",
    "dns": { "type": "CNAME", "name": "game.example.com" },
    "origin_direct": ["udp://198.51.100.20:30000"],
    "ip_firewall": true,
    "edge_ips": { "type": "static", "ips": ["203.0.113.5"] }
  }'
```

### Terraform（cloudflare provider v5）
```hcl
# Minecraft（Proでも可）
resource "cloudflare_spectrum_application" "minecraft" {
  zone_id        = var.zone_id
  protocol       = "tcp/25565"
  ip_firewall    = true
  proxy_protocol = "off"
  tls            = "off"

  dns = {
    type = "CNAME"
    name = "play.example.com"
  }

  origin_direct = ["tcp://192.0.2.50:25565"]

  edge_ips = {
    type         = "dynamic"
    connectivity = "all"
  }
}

# Origin AuthenticationありのMQTTブローカー（Enterprise）
resource "cloudflare_spectrum_application" "mqtt" {
  zone_id        = var.zone_id
  protocol       = "tcp/8883"
  ip_firewall    = true
  proxy_protocol = "v2"
  tls            = "strict"   # Origin証明書をCAチェーン検証

  dns = {
    type = "CNAME"
    name = "mqtt.example.com"
  }

  origin_direct = ["tcp://198.51.100.30:8883"]

  edge_ips = {
    type = "static"
    ips  = ["203.0.113.10"]
  }
}
```

### IP Access Rule（Spectrumにも適用される）
```bash
# 日本以外をBlock
curl -X POST "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/firewall/access_rules/rules" \
  -H "Authorization: Bearer $CF_API_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{
    "mode": "block",
    "configuration": { "target": "country", "value": "!JP" },
    "notes": "SSH/Game: JP only"
  }'
```

## 制限・注意点
- **UDP・任意TCPはEnterprise限定**。Pro/BusinessはSSH/Minecraft等プリセットアプリに固定で、ポート変更も基本不可。要件出しの段階で契約レベルの確認が必須。
- **L7処理は一切行われない**。WAFルール、Bot Management、Cache、Workersは適用されず、Spectrumを通したトラフィックはL3/4 DDoS緩和とIP Access Rulesしか効かない。HTTP/HTTPSは通常プロキシで通すべき。
- **Reserved IP（Static Edge IP）はEnterpriseアドオン**。固定IPでファイアウォール許可リスト登録が必要なクライアント（産業機器・企業VPN）相手では事実上必須となる。
- **Origin Authentication（mTLS）を有効化しないとIP漏洩時に丸裸**になる。Spectrumを「IP隠蔽」の手段として使うなら、tls=strict + Origin CA証明書 + オリジン側のクライアント証明書検証はセットで設計する。
- **帯域・PPS制限**：Enterprise契約でも、Spectrumのアプリケーション単位で接続数・PPS・帯域に上限がある（具体値は契約ごと）。大規模UDP洪水を「サービスとして」受け切る要件は、Magic Transit（BGP経路転換型）の方が筋が良い。
- **PROXY Protocol対応はオリジン側の実装が必要**。HAProxy / Nginx（stream module）/ MosquittoなどはPROXY v1/v2を解釈できるが、独自実装サーバーには改修が必要。Simple ProxyはCloudflare独自の軽量ヘッダで、自作実装の負担を減らせる。
- **CDN / Workers / Cacheの恩恵はゼロ**。「HTTPなのにSpectrumに乗せる」設計は、機能を捨てているだけになる。
- **IPv6ターゲットへの対応は限定的**。オリジンはIPv4前提で組むのが安全。
- **同一Anycast IP/portの衝突**：Free/Proの共有Anycast IPでは、他テナントとの兼ね合いで特定ポートが既に占有されている可能性がある。Reserved IPで回避する。
- **長期SSH運用ではAccess for Infrastructureを優先**。Spectrum + IP Access Rulesは「公開ポートの最低限の保護」止まりで、ユーザー単位のポリシー・録画・短期証明書発行はできない。

## 参考リンク
- Cloudflare Spectrum 概要：https://developers.cloudflare.com/spectrum/
- Get started：https://developers.cloudflare.com/spectrum/get-started/
- Configuration options：https://developers.cloudflare.com/spectrum/reference/configuration-options/
- Spectrum API（Cloudflare API docs）：https://developers.cloudflare.com/api/operations/spectrum-applications-list-spectrum-applications
- Terraform `cloudflare_spectrum_application`：https://registry.terraform.io/providers/cloudflare/cloudflare/latest/docs/resources/spectrum_application
- Argo Smart Routing：https://developers.cloudflare.com/argo-smart-routing/
- Load Balancing（TCP/UDPヘルスチェック）：https://developers.cloudflare.com/load-balancing/
- Magic Transit（BGP型の代替）：https://developers.cloudflare.com/magic-transit/
- Spectrum llms.txt：https://developers.cloudflare.com/spectrum/llms.txt

---
参照日: 2026-05-04
