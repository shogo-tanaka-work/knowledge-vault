# WAF (Web Application Firewall)

## 一行サマリ
Cloudflareのグローバルエッジ上でHTTP/HTTPSリクエストをL7インスペクションし、署名ベースのManaged Rules・スコアリング型のOWASP Core Rule Set・式言語で書く自前のCustom Rules・Rate Limitingを単一のRuleset Engineで合成評価する、エッジ統合型のアプリケーションファイアウォールである。

## 解決する課題（Why）
オリジン手前でアプリケーション層攻撃を止める仕組みは、もはやオプションではなく前提である。一方で、自前運用のWAF（ModSecurity・appliance型）はルールメンテナンス・誤検知調整・スケール・ゼロデイ追従の負荷が重く、SaaSベンダーのWAFは料金とロックインが重い。Cloudflare WAFは既にCDNとしてプロキシしている経路上にWAFを差し込めるという、アーキテクチャ的な「ついで」の優位を持つ。具体的には以下を解決する。

- 既知CVE・OWASP Top 10・ゼロデイ脆弱性に対する署名・スコアリング両建ての即時防御。
- 自社固有のビジネスロジック（特定パス・特定User-Agent・国別・JA3指紋など）に対する宣言的な拒否ルール。
- 認証エンドポイントへのクレデンシャルスタッフィング、漏洩済みパスワードでのログイン試行の検知。
- レスポンスボディからのPII / クレジットカード番号漏洩の検出（Enterprise）。
- DDoS・Bot Management・Rate Limitingと同じプレーンで一貫したアクション（Block / Challenge / Managed Challenge / JS Challenge / Log / Skip）を運用できること。
- 全ゾーン横断のポリシー適用（Account-level Ruleset）による、子会社・マルチブランド構成での統制。

## 主要機能（What）

### Ruleset Engine と Expression Language
Cloudflare WAFは2021年以降、すべてのルール（Managed・Custom・Rate Limiting）を「Ruleset Engine」と呼ばれる単一の評価基盤と、Wiresharkライクな式言語の上に統合している。古い「Firewall Rules」「Page Rules（WAF部分）」はこのエンジンへ移行済みである。

- Expressionの例：`(http.request.uri.path contains "/admin" and ip.geoip.country ne "JP") or (cf.threat_score gt 14)`
- フィールド：HTTPメソッド / URI / ヘッダ / ボディ / Cookie / IP / ASN / Country / TLS指紋（`cf.bot_management.ja3_hash`）/ Bot Score / Threat Score / Verified Bot 等。
- Action：`block` / `challenge` / `managed_challenge` / `js_challenge` / `log` / `skip` / `rewrite` / `compress_response`。
- Phase：`http_request_firewall_managed`、`http_request_firewall_custom`、`http_ratelimit`、`http_response_firewall_managed`（Sensitive Data Detection用）など、評価フェーズ単位でルールセットが束ねられる。

### Managed Rulesets
Cloudflareのセキュリティチームが運用する署名ベースの保守済みルール群である。プランごとに使える対象が分かれる。

- **Cloudflare Free Managed Ruleset**：全プランで有効化可能な、誤検知が少ない高インパクト脆弱性の最低限カバー。Freeプランでも使える。
- **Cloudflare Managed Ruleset**：CVE追従・ゼロデイ対応を含む本命のManaged Rules。Pro以上で利用可能。
- **Cloudflare OWASP Core Ruleset**：後述のスコアリング型ルール。Pro以上。
- **Cloudflare Exposed Credentials Check Ruleset**：認証エンドポイント向けの漏洩クレデンシャル照合。Pro以上（公式ドキュメントは新しい「Leaked Credentials Detection」機能の利用を推奨）。
- **Cloudflare Sensitive Data Detection**：レスポンスフェーズで動作するDLP相当のルールセット。Enterprise限定。

各Managed Rulesetは個別ルール単位でOverride（無効化・アクション変更・特定フィールドのSensitivity調整）が可能で、誤検知が出たら「ルールごと殺す」のではなく「該当パス・該当パラメータでだけ緩める」運用が定石である。

### Custom Rules
Expression Languageで書く自前のFirewallルールである。Managed Rulesetが汎用署名で網を張る一方、Custom Rulesは「自社ドメイン特有の拒否要件」を表現する。

- 典型ユースケース：管理画面パスを社内IPに限定 / 特定ASN（VPN・ホスティング系）を一括Challenge / 古いTLSバージョンや特定User-Agentを遮断 / 特定エンドポイントへのPOSTサイズ制限。
- Skipルールにより「以降のManaged RulesetやBot Fight Modeを評価しない」ホワイトリスト経路を作れる。順序設計（precedence）が事故源になりやすい。
- プラン別ルール本数上限：Free 5、Pro 20、Business 100、Enterprise 1,000（Account-level Rulesetを含めるとさらに拡張可）。

### OWASP Core Rule Set
Cloudflare版のOWASP CRS実装で、伝統的なModSecurity CRSとは異なりCloudflareがメンテナンスする独自フォークである。

- **スコアリングモデル**：個別ルールがマッチするごとに「threat score」に加点され、設定したスコア閾値を超えた時点でアクション（Block等）が発火する。1ルール1ブロックではない。
- **Paranoia Level**：CRS文化を踏襲したParanoia Level（PL1〜PL4相当）で網の細かさを切り替える。PLを上げると検知率と誤検知率が同時に上がるため、Logモードで一定期間ベースラインを取ってから本適用する運用が前提。公式に明記の閾値推奨値については最新ドキュメント参照。
- Cloudflare ManagedとOWASPは並列に動かすのが標準で、Managedで個別CVEを止めつつ、OWASPで未知パターンの傾向検知を担う。

### Rate Limiting 統合
旧「Rate Limiting Rules」も現在はWAFのRuleset Engineに統合されている。Custom Rulesと同じExpressionで対象を絞り込み、`http_ratelimit` フェーズで評価される。

- **キー指定**：IP / Cookie / ヘッダ値 / クエリパラメータ / JA3指紋など任意フィールドの組合せでカウンタを分けられる。
- **カウント条件**：レスポンスステータスを条件にできる（例：401を返した数だけカウント＝失敗ログインのみ計測）。
- **Action**：Block / Managed Challenge / JS Challenge / Log。Block時のレスポンス内容（ステータス・本文・ヘッダ）も指定可能。
- **Advanced Rate Limiting**：Enterprise限定で、複雑なキー設計・長時間ウィンドウ・高QPSに耐える本格運用向け。Bot Managementと組み合わせて「Bot Score低いものだけ厳格にレート制御」が可能。

### Exposed Credentials Check / Leaked Credentials Detection
ログインフォームに投げられたユーザー名・パスワード組合せを、Cloudflareが保有する漏洩クレデンシャルDBに対してハッシュ照合する機能である。Pro以上で利用可能。

- 検出時はリクエストにヘッダ（`Exposed-Credential-Check: 1` 相当）を付加するか、Custom Rulesから`cf.waf.credential_check.*` 系フィールドを参照して任意のアクション（Block / Challenge / 強制パスワードリセット導線への302）を取れる。
- 公式ドキュメントでは旧「Exposed Credentials Check Ruleset」より新しい「Leaked Credentials Detection」機能の利用が推奨されている。アプリ側でログインエンドポイント（パス・パラメータ名）の登録が必要。

### Sensitive Data Detection（Enterprise限定）
レスポンスフェーズで動作する稀なルールセットで、オリジンからの応答ボディに含まれるPII（メールアドレス・電話番号・SSN・クレジットカード番号など）を検出する。事故的な大量データ流出をエッジで検知・ログ化する用途である。Blockではなく検知・通知ベースで運用するのが現実的で、純粋な「DLP製品」のリプレースとしては機能不足の領域もある。

### Deployment Models
- **Zone-level Ruleset**：個別ドメイン（Zone）単位でManaged / Custom / Rate Limitingを設定する標準形。
- **Account-level Ruleset**：Enterprise限定で、アカウント配下の複数Zoneに横串でルールを適用する。M&A後の多ブランド統制、グループ会社全体の最低基準ポリシーの強制に使う。
- いずれもRuleset APIまたはTerraformで宣言的に管理でき、ダッシュボード操作とコード管理を併用するとprecedenceが壊れやすい点に注意。

## アーキテクト視点：いつ選ぶか

### 適しているシーン
- 既にCloudflareをCDN / DNSとして使っており、オリジン手前にWAFを差し込む追加コストが「プランアップだけ」で済むケース。最速のROI。
- グローバル分散・高QPSのWebサービスで、リージョン選定なしにエッジで弾ける運用が要件のケース。AWS WAF（ALB / CloudFront貼付け）よりも全リージョン一様にレイテンシが低い。
- マルチブランド・マルチドメインで、Account-level Rulesetによる「全社最低基準」ポリシーをコードで強制したい組織。
- API GatewayとしてのCloudflare（API Shield / Workers）と組合せ、スキーマバリデーション・mTLS・JWT検証を含む包括的なAPI防御を一本化したいケース。
- セキュリティ専任が薄く、Managed RulesetsとBot Fight Modeのデフォルト品質に頼りたい中規模事業者。

### 適していないシーン
- オリジンがCloudflareをプロキシしていない、またはオンプレ・閉域網にあって外部公開していないアプリ。WAFは前段に立てて初めて意味を持つ。
- 「真のWAAP」要件としてAPI Discovery（未知エンドポイントの自動発見）・スキーマ自動生成・GraphQLインスペクション・自動学習型ベースラインを業務要件として求めるケース。CloudflareもAPI Shieldで追従しているが、Imperva / Akamai EAA / Salt Securityなど専業の成熟度には届かない領域がある。
- 厳しい規制業界（金融・公的機関）で、トラフィックを米系CDN事業者に集約することが許されないケース。
- アプリケーションの応答にPIIが大量に含まれ、本格DLPとしてのインスペクション・トークナイゼーション・暗号化を必要とするケース。Sensitive Data Detectionは検知止まりで、Imperva DAM相当の機能ではない。
- 既存のオリジン側WAF（AWS WAF + Shield Advanced、ModSecurity）に深く投資済みで、ルール資産の移植コストが正当化できないケース。

## 競合・代替

| 観点 | Cloudflare WAF | AWS WAF | Akamai App & API Protector | Imperva Cloud WAF | F5 Distributed Cloud WAAP |
|---|---|---|---|---|---|
| 出自 | CDN統合・Anycastエッジ | クラウドベンダー純正 | CDN統合（Kona Site Defenderの後継） | 専業セキュリティベンダー | NGINX / Shape Securityを統合したWAAP |
| Managed Rules | Cloudflare Managed + OWASP CRS（自社フォーク） | AWS Managed Rule Groups + Marketplace | Akamai KSD Rules + Adaptive Security Engine | Imperva Threat Research | F5 Signature DB + ML |
| Custom Rules式言語 | Wiresharkライク統合DSL（強力） | JSON Statement（冗長） | GUI中心 | GUI + 独自DSL | GUI + JSON |
| Rate Limiting | WAF統合・Advanced（EE） | 別機能（Rate-based rules） | 標準 | 標準 | 標準 |
| Bot Management | 同一プレーン（Bot Management別ライセンス） | Bot Control（別料金） | Bot Manager（別ライセンス） | Advanced Bot Protection（別） | Shape由来で強力 |
| API Security | API Shield（同梱・別ライセンスあり） | 弱い（API Gateway側で別構成） | 強い | 強い | 強い |
| Account / Org横断ポリシー | Account-level Ruleset（EE） | Firewall Manager | 標準 | 標準 | 標準 |
| 価格モデル | プラン同梱（Pro $25 / Business $250 / EE要見積） | 従量（ルール数 + リクエスト数） | 高額・要見積 | 高額・要見積 | 高額・要見積 |
| 強み | エッジ統合・式言語の表現力・コスト | AWS資産との統合・IaC親和性・細粒度課金 | 大企業向け運用実績・サポート | 検知精度・専業の成熟度 | Bot対策とWAFの一体化 |
| 弱み | 大企業向けAPI Discovery / 高度DLPは追従途上 | 式が冗長・グローバルレイテンシ・DDoS連携が弱い | 高コスト・運用が重い | 高コスト・クラウド統合は後発 | 導入コスト・国内事例が少ない |

Cloudflare WAFの本質的優位は「CDN・DDoS・Bot・Workers・API Shieldと同じプレーンで完結する」点にあり、AWS WAFの優位は「IaCとIAMが他のAWS資産と一体で語れる」点にある。Akamai / Imperva / F5は機能成熟度では先行するが、価格と運用負荷でCloudflareに置き換える事例が増えている、というのが現状の力学である。

## 料金
公式の最新価格は `https://www.cloudflare.com/plans/` を参照のこと。本稿執筆時点（2026-05-04）の概観は以下である。

- **Free**：Cloudflare Free Managed Ruleset、Custom Rules 5本、基本的なRate Limiting。OWASP Core RulesetとCloudflare Managed Rulesetは含まれない。検証用途・個人ブログ向け。
- **Pro**（$25/月程度）：Cloudflare Managed Ruleset、OWASP Core Ruleset、Exposed Credentials Check、Custom Rules 20本。中小事業者の標準ライン。
- **Business**（$250/月程度）：Pro機能 + Custom Rules 100本、Custom WAFルール拡張、PCI DSS対応構成、Page Shield等の連携機能。
- **Enterprise**（要見積もり）：Sensitive Data Detection、Advanced Rate Limiting、Account-level Ruleset、Custom Rules 1,000本、API Shield統合、Logpush、24/365 SLA。多ドメイン・規制業種・高QPSサービスはここを前提に設計する。

注意点として、Bot Management・API Shield Advanced・Page Shield Plus・DDoS Advanced等の上位機能は同じプランの中でも追加SKUになる場合がある。営業見積もりを取る際は「WAF本体」ではなく「Bot / API / DDoSの上位機能とのセット価格」を必ず確認する。具体的な金額は公式に明記なしの組合せが多く、Enterprise契約は個別交渉が前提である。

## CLI / API 例

Cloudflare WAFには専用CLIは存在せず（`cf waf` 系のコマンドは公式に明記なし）、運用はRuleset APIまたはTerraform Cloudflare Providerで行うのが定石である。

### curl：Custom Rule追加（Zone-level Ruleset）
```bash
# 該当ZoneのCustom Ruleset IDを取得
curl -sS "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/rulesets" \
  -H "Authorization: Bearer ${CF_API_TOKEN}" \
  | jq '.result[] | select(.phase=="http_request_firewall_custom")'

# Custom Rulesetに「管理画面は社内IPのみ」ルールを追加
curl -sS -X POST \
  "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/rulesets/${RULESET_ID}/rules" \
  -H "Authorization: Bearer ${CF_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Allow /admin from corp IPs only",
    "expression": "(http.request.uri.path contains \"/admin\") and not (ip.src in {203.0.113.0/24 198.51.100.0/24})",
    "action": "block",
    "enabled": true
  }'
```

### Terraform（cloudflare provider v5）
```hcl
# Managed Rulesetを有効化（Cloudflare Managed Ruleset を Block で適用）
resource "cloudflare_ruleset" "zone_managed_waf" {
  zone_id     = var.zone_id
  name        = "Zone managed WAF entrypoint"
  description = "Deploy Cloudflare Managed Ruleset"
  kind        = "zone"
  phase       = "http_request_firewall_managed"

  rules {
    action      = "execute"
    description = "Execute Cloudflare Managed Ruleset"
    expression  = "true"
    action_parameters {
      id = "efb7b8c949ac4650a09736fc376e9aee" # Cloudflare Managed Ruleset ID（公式参照）
      overrides {
        action = "block"
      }
    }
  }
}

# OWASP Core Ruleset：Paranoia Levelを上げ閾値Block
resource "cloudflare_ruleset" "zone_owasp" {
  zone_id = var.zone_id
  name    = "Zone OWASP entrypoint"
  kind    = "zone"
  phase   = "http_request_firewall_managed"

  rules {
    action      = "execute"
    description = "OWASP CRS with PL2"
    expression  = "true"
    action_parameters {
      id = "4814384a9e5d4991b9815dcfc25d2f1f" # OWASP Ruleset ID（公式参照）
      overrides {
        # Paranoia Level・閾値・タグ別アクションをここで上書き
        action = "block"
      }
    }
  }
}

# Custom Rule：失敗ログインのRate Limiting（IP+ユーザー名キー）
resource "cloudflare_ruleset" "zone_ratelimit" {
  zone_id = var.zone_id
  name    = "Zone rate limiting"
  kind    = "zone"
  phase   = "http_ratelimit"

  rules {
    action      = "block"
    description = "Throttle failed logins per IP+user"
    expression  = "(http.request.uri.path eq \"/api/login\") and (http.request.method eq \"POST\")"
    ratelimit {
      characteristics     = ["ip.src", "http.request.body.form[\"username\"]"]
      period              = 60
      requests_per_period = 5
      mitigation_timeout  = 600
      counting_expression = "http.response.code eq 401"
    }
  }
}
```

Ruleset IDは公式ドキュメント（`https://developers.cloudflare.com/waf/managed-rules/reference/`）に列挙されており、コード固定ではなくDataソースとして参照する書き方も可能である。

## 制限・注意点
- Managed Rulesetsの個別ルールに対するOverrideは可能だが、ルール内部の検知ロジックそのものはブラックボックスである。「なぜ誤検知したか」の最終的な再現はサポートチケットで問い合わせる前提となる。
- OWASP Core Rulesetはスコアリング方式のため、単一ルールの除外ではなく「閾値・対象パスごとのアクション切替」で運用する。誤検知対応にはPenalty Box的なログ駆動チューニングが必要。
- Custom Rulesのprecedence設計を誤ると、Skipルールが想定外にManaged Rulesetを無効化する事故が起きる。Terraformで全ルール宣言を一元管理し、ダッシュボード手編集を禁止する運用が安全。
- Sensitive Data Detectionはレスポンスフェーズで動作するため、レスポンスのパフォーマンスに微影響がある。さらに大規模なPIIマスキング・トークナイゼーションは本機能の対象外で、別途DLP製品との併用が必要。
- Rate Limitingのカウンタはエッジノード分散カウントであり、厳密な「グローバルで秒間Nリクエスト」を保証するものではない。許容スパイクを織り込んだ閾値設計が必要。
- Cloudflare WAFはあくまで「Cloudflareをプロキシとして経由するトラフィック」にしか効かない。オリジンIPが漏れて直接叩かれる経路を残すと無意味になるため、Authenticated Origin Pulls / Argo Tunnel / オリジンIPホワイトリストによる「バイパス防止」設計が必須である。
- Bot Management・API Shield Advanced・Page Shield Plusなどの上位機能は同じWAFプレーンに乗るが別ライセンスである。コスト試算時は「WAF本体」だけで見積もると後で外れる。
- Account-level RulesetはEnterprise限定で、Zone-levelとの優先順位ルールを把握しないと「子Zoneで上書きしたつもりが効かない」事故が起きる。

## 参考リンク
- Cloudflare WAF：https://developers.cloudflare.com/waf/
- Managed Rules：https://developers.cloudflare.com/waf/managed-rules/
- Custom Rules：https://developers.cloudflare.com/waf/custom-rules/
- Rate Limiting Rules：https://developers.cloudflare.com/waf/rate-limiting-rules/
- Ruleset Engine：https://developers.cloudflare.com/ruleset-engine/
- Expression Language（Fields）：https://developers.cloudflare.com/ruleset-engine/rules-language/fields/
- Leaked Credentials Detection：https://developers.cloudflare.com/waf/detections/leaked-credentials/
- Sensitive Data Detection：https://developers.cloudflare.com/waf/managed-rules/reference/sensitive-data-detection/
- Plans：https://www.cloudflare.com/plans/
- Terraform `cloudflare_ruleset`：https://registry.terraform.io/providers/cloudflare/cloudflare/latest/docs/resources/ruleset

---
参照日: 2026-05-04
