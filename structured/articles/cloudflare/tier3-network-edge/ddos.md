# DDoS Protection

## 一行サマリ
Cloudflareの全エッジ（330都市超・100カ国超、数百Tbps級のAnycastネットワーク）をそのまま吸収帯域として使い、L3/4からL7までのDDoSをManaged Rulesetで自動緩和する常時稼働型サービスである。Free含む全プランで無制限・無従量課金で提供される点が業界内で突出している。

## 解決する課題（Why）
DDoSは「攻撃者が用意できる帯域 vs 防御側が用意できる吸収帯域」の単純な算数で勝負が決まる。自前のオリジン回線・専用アプライアンス・キャリア提供のクリーンパイプでは、Tbps級のVolumetric攻撃や数億rpsのHTTPフラッドを正面で受けることは現実的でなく、攻撃中に追加帯域を契約する時間的余裕もない。CloudflareのDDoS Protectionは以下を解決する。

- Anycastで全世界のエッジにトラフィックを分散吸収し、攻撃元に近いPoPで落とす（オリジン回線への到達を防ぐ）。
- L3/4 SYN/ACK/UDP/DNSフラッド、L7 HTTPフラッドをManaged Rulesetで自動検知・自動緩和（人手介入なし）。
- 攻撃の規模・継続時間に依存しない定額課金（Free含む全プラン）で、契約直後から数百Tbpsの吸収余力にアクセスできる。
- BGP Anycast / GRE / IPSec / CNI経由でWebに限らない任意のIPプロトコルを保護（Magic Transit / Spectrum）。
- Adaptive DDoS Protectionで、サービス固有のトラフィック形状（地域分布・User Agent比率・クエリパターン）から逸脱するフラッドを検知。

## 主要機能（What）

### HTTP DDoS Protection
HTTP/HTTPS上のL7フラッド（GET/POSTフラッド、Cache Bypass攻撃、ランダムURL攻撃、ボットネット由来のリクエストフラッド）を緩和するManaged Rulesetである。Cloudflareプロキシ配下（オレンジクラウド有効）のゾーンに自動適用される。

- Ruleset Engineで管理され、各ルールは独自の検知ロジックとアクション（Block / Managed Challenge / JS Challenge / Log）を持つ。
- 全プランで有効。Free / Pro / Businessでも上限・従量課金なしで稼働する。
- Override Rulesでルール単位のSensitivity（Default / Low / High）とAction上書きが可能（プランにより上書き本数が異なる）。
- アクセプタンスは秒単位で、Cloudflare Radar / DDoS Reportで世界中の攻撃トレンドが公開されている。

### Network-layer DDoS Protection (L3/4)
SYNフラッド、ACKフラッド、UDPフラッド、DNSフラッド、SYN-ACK Reflection、TCPフラグメント攻撃などL3/4のVolumetric攻撃を緩和するManaged Rulesetである。プロキシ配下のIP（Cloudflare CDN / Spectrum / Magic Transit）に対して自動適用される。

- Spectrumを使えば任意のTCP/UDPサービス（ゲーム・SSH・SMTP・カスタムプロトコル）を同層で保護できる。
- Magic Transitを使えばBGP Anycast / GRE / IPSec / CNIで自社ASのIPプレフィックス全体をCloudflareに引き込み、Webに限らないオンプレ・クラウドを保護できる。
- 全プランで有効、ただし「プロキシまたはMagic Transitでトラフィックを引き込んでいる」ことが前提。素のオリジンIPがDNSに残ったままだとバイパスされる。

### Advanced DDoS Protection (Magic Transit / Spectrum向け)
Magic Transit / Spectrum契約者向けの上位機能群である。汎用Managed Rulesetでは検知しにくい、状態を持つ高度な攻撃に対応する。

- **Advanced TCP Protection**：スプーフィングされたACKフラッド、Out-of-state TCP、最適化されたSYNフラッドなど、ステートフル解析が必要な攻撃をフィンガープリントで識別。
- **Advanced DNS Protection**：ランダム化サブドメイン攻撃（NXDOMAIN水責め）、DNS Amplification、権威DNS向けの細粒度フラッド対策。
- **Advanced alerts**：フィルタ付きの粒度の高いアラート（プレフィックス単位・攻撃種別単位）。
- Advanced DDoS Protectionアドオン契約が前提。標準のMagic Transit / Spectrumには含まれない。

### Adaptive DDoS Protection
サイト固有のトラフィックプロファイルを学習し、そのベースラインから逸脱する攻撃を検知する適応型ルールセットである。汎用シグネチャでは見抜けない「合法に見えるが当該サイトの平常時とは明らかに違う」フラッドに効く。

- **エラー率プロファイリング**：通常時の5xx / 4xx比率を学習し、急増を攻撃シグナルとして扱う。Free / Pro / Businessでも基本機能が利用可能。
- **トラフィック形状プロファイリング**（Enterprise + Advanced DDoS Protection）：Client Country、User Agent分布、クエリ文字列、Bot Score / ML Scoreまで含めた多次元プロファイル。
- **Proactive false positive detection**（Business / Enterprise）：新規ルールを本番投入前にライブトラフィックでDry-runし誤検知を抑制。

### Override Rules
Managed Rulesetは原則そのまま使う前提だが、サービス特性で誤検知が起きる場合はOverride Rulesでルール単位の挙動を上書きできる。

- 上書き対象：Action（Block / Challenge / Log / Disable）、Sensitivity Level（High / Default / Low / Essentially Off）。
- プラン別の上書き上限：Free / Pro / Business / Standard Enterpriseは概ね1ルール、Enterprise + Advanced DDoS Protectionは10ルール上書き＋Expression fields＋Multi-rule対応。
- Sensitivityを下げる運用は緊急時のみとし、平常時はDefaultで運用するのが原則。

### Alerts & Analytics
攻撃検知・緩和の可視化はDashboard / API / Logpushで取得できる。

- **DDoS Attack Alerts**：HTTP / L3-4双方の攻撃検知時にメール・Webhook・PagerDuty通知（全プラン基本対応）。
- **Network Analytics v2**：Magic Transit / Spectrum向けのパケット単位の統計（送信元国・プロトコル・アタックベクター）。
- **HTTP DDoS Attack Analytics**：Securityダッシュボードに攻撃イベント単位で集約表示。
- **Logpush（Enterprise）**：攻撃イベントログをS3 / R2 / Splunk / Datadog / Sentinelに継続転送。
- **Cloudflare Radar**：自社攻撃ではなく業界全体の攻撃トレンドを参照する公開ダッシュボード。

### Always-On vs On-Demand（Magic Transit）
Magic Transitの引き込みモードは2種類あり、設計時にどちらを選ぶか明示する必要がある。

- **Always-On**：常時CloudflareがBGPでプレフィックスを広告し、平常時から全トラフィックがエッジを経由する。最も検知が早く緩和遅延がほぼゼロ。レイテンシ要件が許容できるなら推奨。
- **On-Demand**：平常時は自社ASでBGP広告し、攻撃検知時のみCloudflare側に切り替える。レイテンシを最優先するが、切り替え遅延（数十秒〜分単位）の間はオリジンが攻撃を受ける。
- 一般論として、Eコマース・SaaS・APIゲートウェイなどダウンタイム許容度が低いワークロードはAlways-On、自前バックボーンを持つキャリアやレイテンシ厳格なゲーム配信はOn-Demandを選ぶ判断軸となる。

## アーキテクト視点：いつ選ぶか

### 適しているシーン
- すでにCloudflare CDN / WAFをプロキシ配下で使っているWebサービス。HTTP DDoSは追加コスト・追加設定なしで自動有効。
- 自社ASのIPプレフィックスを保護したいキャリア・ホスティング・ゲーム配信事業者（Magic Transit Always-On）。
- 過去にDDoSで実害があり「次は数Tbps級でも耐える」吸収帯域を即時に欲しい組織。Cloudflareの公称ネットワーク容量はマルチTbps級で、過去にも数Tbps〜数億rpsの攻撃を緩和した実績が公表されている。
- 攻撃規模に応じた従量課金を避け、年度予算を固定したい組織。AWS Shield Advanced / Akamai Prolexicは攻撃中の超過帯域に従量課金的要素が絡むことがあるが、CloudflareはFree含めて無制限・定額。
- Webだけでなく任意プロトコル（SSH / SMTP / ゲーム / 独自TCP/UDP）を同じ防御層で保護したいケース（Spectrum / Magic Transit）。

### 適していないシーン
- Cloudflare以外のCDN / プロキシで運用が完結しており、オリジンIPがDNS公開されたまま隠蔽できないケース。L3/4はバイパスされるため意味をなさない。
- オンプレ回線の上流ISPが既にスクラビングサービスを提供しており、社内SLAでそれを使う前提になっている組織（重複投資になる）。
- レイテンシが極端に厳しい金融トレーディング・低遅延ゲーム配信で、Always-On導入が許容できず、かつOn-Demand切り替え時間も許容できないケース（このときはISPスクラビング併用）。
- 規制上、特定国の事業者にトラフィックを集約してはならない政府・防衛系。

## 競合・代替

| 観点 | Cloudflare DDoS Protection | AWS Shield Advanced | Akamai Prolexic | Imperva DDoS Protection | Radware DefensePro |
|---|---|---|---|---|---|
| 出自 | Anycast CDN（全プロダクト統合） | AWS WAF / CloudFront連動 | スクラビングセンター（純血DDoS） | WAF / CDN統合 | オンプレアプライアンス＋クラウド |
| ネットワーク容量 | 数百Tbps級・330都市超 | AWS Globalバックボーン | 数十Tbps級・グローバルスクラビング | マルチTbps級 | パートナー網に依存 |
| L3/4対策 | Magic Transit / Spectrumで全プロトコル | Shield Advanced（CloudFront / NLB / EIP） | BGP / GRE / Tunnel | BGP / Proxy | BGP / GRE |
| L7対策 | HTTP DDoS Managed Ruleset（全プラン） | AWS WAF併用が前提 | Kona / App Protector | 標準同梱 | AppWall併用 |
| Always-On / On-Demand | 両対応（Magic Transit） | Always-On（AWSリソースに対して） | 両対応 | 両対応 | 両対応 |
| 価格モデル | 全プラン無制限・無従量。Magic Transit / Spectrumは別途有償 | $3,000/月＋データ転送、コスト保護あり | 6〜7桁ドル/年（要見積もり） | 要見積もり | アプライアンス＋年額 |
| 強み | 全プラン無制限・エッジ統合・運用シンプル | AWS資産との結合・WAF / Firewall Managerと一体運用 | 大手金融・キャリア導入実績・専任SOC | DDoS / WAF / Botの統合 | オンプレ＋クラウドのハイブリッド |
| 弱み | Cloudflareエッジに引き込めない構成は対象外 | AWS外のリソース保護不可・高コスト | 高コスト・契約までの時間 | PoP網はCloudflareに劣る | クラウド単独運用には冗長 |

Cloudflareの最大の差別化は **「Free含む全プランでHTTP / L3-4 DDoS対策が無制限・無従量で標準提供される」** という料金モデルそのものである。AWS Shield Advancedは月額$3,000＋データ転送、Akamai Prolexicは年額契約で6〜7桁ドル規模が一般的という業界相場の中で、Cloudflareは「契約しなくても無料アカウントですぐ使える」位置に立っている。これは攻撃を受けてから防御を契約しても遅い、というDDoS特有の時間制約に対する強い解である。

## 料金

- **Free / Pro / Business**：HTTP DDoS / L3-4 DDoS Managed Ruleset、基本Adaptive Protection（エラー率ベース）、基本アラート、Override 1ルールが無制限・無従量で利用可能。Volumetric攻撃を受けても従量課金は発生しない。
- **Enterprise（標準）**：上記に加え、誤検知抑制の強化（エラー率＋ヒストリカル）、SLA、専任サポート。
- **Enterprise + Advanced DDoS Protection（アドオン）**：Adaptive Protectionのフルプロファイル（Country / UA / Query / ML Score）、Override 10ルール＋Expression fields＋Multi-rule、Advanced alerts。
- **Magic Transit**：自社ASのIPプレフィックスをBGPでCloudflareに引き込む。年額契約・帯域とプレフィックス数で見積もり。Always-On / On-Demandはここで選択。
- **Spectrum**：任意のTCP/UDPポートをプロキシ。Enterprise契約のアプリケーション単位課金が中心。

「Web保護目的ならFreeで十分、自社ASやプロトコル丸ごと保護はMagic Transit / Spectrumで有償」という二段構成が基本設計となる。

## CLI / API 例

### HTTP DDoS Managed Rulesetの状態確認
```bash
# ゾーン配下に適用されているDDoS Managed Rulesetを取得
curl -X GET \
  "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/rulesets" \
  -H "Authorization: Bearer ${CF_API_TOKEN}" \
  | jq '.result[] | select(.kind=="managed" and (.name|test("DDoS")))'
```

### Override Rule（特定ルールのSensitivityをLowに、ActionをLogへ）
```bash
# ゾーンのhttp_ddos_managed_rulesetエントリーポイントにオーバーライドを書く
curl -X PUT \
  "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/rulesets/phases/http_ddos_l7/entrypoint" \
  -H "Authorization: Bearer ${CF_API_TOKEN}" \
  -H "Content-Type: application/json" \
  --data '{
    "rules": [{
      "action": "execute",
      "expression": "true",
      "action_parameters": {
        "id": "4d21379b4f9f4bb5fbaa75a8ccba7f5c",
        "overrides": {
          "rules": [{
            "id": "<rule_id_to_override>",
            "action": "log",
            "sensitivity_level": "low"
          }]
        }
      }
    }]
  }'
```

### Terraform（cloudflare provider v5）
```hcl
# HTTP DDoS Managed RulesetのOverride（ルール単位でSensitivity緩和）
resource "cloudflare_ruleset" "http_ddos_override" {
  zone_id     = var.zone_id
  name        = "HTTP DDoS override"
  description = "Lower sensitivity for legitimate burst traffic"
  kind        = "zone"
  phase       = "ddos_l7"

  rules = [{
    action      = "execute"
    expression  = "true"
    description = "Execute managed DDoS ruleset with overrides"
    action_parameters = {
      id = "4d21379b4f9f4bb5fbaa75a8ccba7f5c"  # HTTP DDoS Managed Ruleset
      overrides = {
        rules = [{
          id                = "<rule_id>"
          sensitivity_level = "low"
          action            = "log"
        }]
      }
    }
  }]
}

# Network-layer DDoS Managed Rulesetも同様、phase = "ddos_l4"
resource "cloudflare_ruleset" "network_ddos_override" {
  account_id  = var.account_id
  name        = "Network DDoS override"
  kind        = "root"
  phase       = "ddos_l4"

  rules = [{
    action     = "execute"
    expression = "true"
    action_parameters = {
      id = "3b64149bfa6e4220bbbc2bd6db589552"  # Network-layer DDoS Managed Ruleset
    }
  }]
}
```

### DDoS Attack Alertの登録（Notification Policy API）
```bash
curl -X POST \
  "https://api.cloudflare.com/client/v4/accounts/${ACCOUNT_ID}/alerting/v3/policies" \
  -H "Authorization: Bearer ${CF_API_TOKEN}" \
  -H "Content-Type: application/json" \
  --data '{
    "name": "DDoS Attack Alert",
    "alert_type": "dos_attack_l7",
    "enabled": true,
    "mechanisms": {
      "email": [{"id": "ops@example.com"}],
      "webhooks": [{"id": "<webhook_id>"}]
    }
  }'
```

## 制限・注意点
- **Free / Pro / BusinessのHTTP DDoSは無制限だが、L3/4対策はあくまで「Cloudflareプロキシ配下のIP宛トラフィック」が対象**である。オレンジクラウドOFF（DNS only）にしているレコード、または直接オリジンIPがDNS公開されている場合は素通りで届く。Magic Transitなしの構成では、オリジンIPの隠蔽（Authenticated Origin Pulls / IP Allow List）が必須。
- **任意プロトコル（SSH / SMTP / ゲームサーバー / 独自TCP/UDP）を守るならSpectrumまたはMagic Transitが必須**。Free / Pro / BusinessではWeb（HTTP/HTTPS）以外の引き込みができない。
- **Adaptive DDoS Protectionのフル機能はEnterprise + Advanced DDoS Protectionアドオン限定**。Free / Pro / Businessはエラー率ベースの基本プロファイルのみ。
- **Override Rulesは緊急対応の道具**であり、常時Sensitivityを下げて運用するのはアンチパターン。緩和ルールは時限的に入れて、原因が解消したらDefaultに戻す運用ルールを定義する。
- **Always-On Magic Transitはレイテンシが増える**（Cloudflareエッジ経由の分）。低遅延ゲーム配信や金融系は事前にPoP距離・RTTを計測すべき。
- **DNSが攻撃面のときはCloudflare DNS（権威）またはAdvanced DNS Protectionへの移行が前提**。自社で権威DNSを運用したままだと、DNS層のフラッドでサービス全体が落ちる。
- **検知後の自動緩和はManaged Rulesetが行うため、運用側で「攻撃が来たらこのルールを有効化する」操作は不要**。逆にいうと、自分で見たい攻撃まで自動でChallenge / Blockされるため、検証時はLogアクションのオーバーライドを明示的に入れる。
- **コスト保護の有無**：AWS Shield Advancedの「DDoS Cost Protection（攻撃中のスケールアウト料金返金）」のような明示的な仕組みはCloudflareにはない。代わりに **そもそも攻撃トラフィックがオリジンに届かない／従量課金が発生しない** という構造でコストを守る。

## 参考リンク
- Cloudflare DDoS Protection（公式ドキュメント）：https://developers.cloudflare.com/ddos-protection/
- HTTP DDoS Managed Ruleset：https://developers.cloudflare.com/ddos-protection/managed-rulesets/http/
- Network-layer DDoS Managed Ruleset：https://developers.cloudflare.com/ddos-protection/managed-rulesets/network/
- Advanced DDoS Protection (Magic Transit)：https://developers.cloudflare.com/ddos-protection/advanced-ddos-systems/
- Adaptive DDoS Protection：https://developers.cloudflare.com/ddos-protection/managed-rulesets/adaptive-protection/
- Magic Transit：https://developers.cloudflare.com/magic-transit/
- Spectrum：https://developers.cloudflare.com/spectrum/
- Cloudflare Network（容量・PoP数）：https://www.cloudflare.com/network/
- Cloudflare Radar（攻撃トレンド）：https://radar.cloudflare.com/
- Terraform `cloudflare_ruleset`：https://registry.terraform.io/providers/cloudflare/cloudflare/latest/docs/resources/ruleset

---
参照日: 2026-05-04
