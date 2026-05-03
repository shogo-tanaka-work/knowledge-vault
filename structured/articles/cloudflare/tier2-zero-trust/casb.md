# CASB (Cloudflare One)

## 一行サマリ
SaaSやIaaSのAPIに直接接続し、設定ミス・過剰共有・不審なユーザー活動・データ露出を継続スキャンで検出するAPIベースのCloud Access Security Brokerである。

## 解決する課題（Why）
SaaS時代のセキュリティ事故の多くは、攻撃者の侵入ではなくテナント側の「設定の歪み」と「共有の事故」から生じる。Public link付きのGoogle Drive、MFA未設定のOkta管理者、外部組織が招待されたままのSlackチャネル、退職者が残したGitHubトークン。こうした問題はネットワーク経路を通らないため、ファイアウォールでもSWGでも見えない。Cloudflare CASBはSaaSのAPIに直接接続し、テナント内部の状態を読み取って以下を解決する。

- SaaSテナントの**設定ミス（misconfiguration）**の継続的な検出。
- ファイル・ドキュメント・リポジトリの**過剰共有（over-sharing / public exposure）**の発見。
- 未承認SaaSやAI利用といった**Shadow IT / Shadow AI**の可視化。
- DLPと組合せたSaaS内コンテンツの**機密データ露出**検知。
- 退職者・元従業員アカウントや権限肥大の検出。

ネットワーク経路を通らない領域、すなわち「すでにSaaS内部で起きている事象」を捕まえるためのレイヤである。

## 主要機能（What）

### APIスキャン方式
CASBは各SaaSのAPIにOAuthまたは管理者権限で接続し、**read-only**の最小権限で定期スキャンを実行する。スキャン間隔は概ね1時間〜24時間で、ネットワーク経路にプロキシとして割り込まないため、ユーザー体験やレイテンシには影響しない。Inlineの制御（DLPブロックなど）はGatewayが担当し、APIによるテナント可視化はCASBが担当する、という役割分担である。

### 対応SaaS / IaaS
2026年5月時点で以下に対応する（カテゴリ別）。

- **生産性スイート**：Google Workspace（Gmail / Drive / Calendar / Admin）、Microsoft 365（Admin Center / Outlook / SharePoint / OneDrive）
- **クラウドストレージ**：Box、Dropbox、Google Drive、OneDrive、SharePoint、AWS S3、GCP Cloud Storage
- **コラボレーション**：Slack、Atlassian Confluence、Atlassian Jira
- **CRM / ITSM**：Salesforce、ServiceNow
- **開発基盤**：GitHub、Bitbucket Cloud
- **AI**：Anthropic、OpenAI、Microsoft 365 Copilot、Gemini for Google Workspace

AI系SaaSへの対応はShadow AI対策として近年強化されている領域であり、生成AIの業務利用が広がる組織での価値が高い。

### Findings（検出種別）
検出結果は二系統に分類される。

- **Posture Findings**：テナント設定そのものに対する問題。MFA未強制、管理者権限の過剰付与、Public sharing有効、外部ユーザー招待、退職者アカウント残存、APIトークン露出など。
- **Content Findings**：SaaS内のファイル・メッセージに含まれる機密データ。クレジットカード番号・マイナンバー・ソースコード上のシークレットなどがDLPプロファイルとマッチした際に生成される。

各FindingにはSeverityが付与される。

| Severity | 対応の目安 |
|---|---|
| Critical | 即日対応（公開状態のシークレット、特権アカウント乗っ取り疑い等） |
| High | 同週中に対応（公開ドキュメント、MFA未強制管理者等） |
| Medium | 同月中にレビュー |
| Low | 情報提供・定期レビュー対象 |

### DLP / Gateway との連携
Content FindingsはCloudflare DLPのプロファイル（PCI / PII / カスタム正規表現等）と連動する。Posture Findingsの一部、特にGoogle Workspaceのファイル共有系Findingは、画面上から**Gateway HTTPポリシーをワンクリックで生成**できるよう接続されており、検出 → ブロックの動線が短い。Inline制御は常にGatewayが担い、CASBはトリガーと文脈を提供する役割となる。

## アーキテクト視点：いつ選ぶか

### 適しているシーン
- 既にCloudflare Zero Trust（Access / Gateway / DLP）を導入済みで、SaaS内部の監査レイヤを足したい組織。
- Google Workspace / Microsoft 365 を全社で使い、外部共有の事故を継続的に発見したい中規模組織。
- GitHub / Bitbucket でのシークレット露出・public化事故を早期に検出したい開発組織。
- Shadow AI（ChatGPT / Claude / Copilotの個人利用）の可視化を始めたい組織。
- 50ユーザー無料枠の中で「軽量CASB」を試したいスタートアップ。

### 適していないシーン
- **Inlineでの強制制御を主軸にしたい**ケース。CloudflareのCASBはAPI型に特化しており、Reverse proxy / Forward proxy型のセッション内介入を期待するならNetskopeやDefender for Cloud Appsの方が向く。
- **長尾のSaaS**（業界特化アプリや国産SaaS）まで広く対応させたいケース。ロングテール対応はNetskope / McAfee MVISION の方が成熟している。
- **オンプレSaaS（自社ホストGitLabなど）**の監査。CASB対象は基本的にクラウド版に限られる。
- **コンプライアンス報告書を自動生成したい**といった重厚な監査機能を求めるケース。Cloudflare CASBは検出と是正動線にフォーカスしており、レポーティング機能は最小限である。

## 競合・代替

| 観点 | Cloudflare CASB | Netskope CASB | Microsoft Defender for Cloud Apps | McAfee（Trellix）MVISION Cloud | Palo Alto SaaS Security |
|---|---|---|---|---|---|
| 主モデル | API型に特化 | API + Inline（Forward / Reverse Proxy）両対応 | API + Conditional Access App Control（Reverse Proxy） | API + Inline | API + Inline |
| 強み | Zero Trustスタック（Access / Gateway / DLP）と一体・無料枠あり | カバーSaaS数が最大級・UEBAが強力 | Microsoft 365との統合が圧倒的・Entra連動 | 老舗で大企業導入実績豊富 | Prisma SASEとの統合 |
| 弱み | 対応SaaS数は競合より少なめ・Inline制御は別コンポーネント | 価格高め・運用がリッチで重い | M365以外のカバレッジは中庸 | UIが古め・SKU体系が複雑 | 単独利用しにくい |
| Inline DLPブロック | Gatewayに委譲（連携あり） | 自前 | 自前（Conditional Access） | 自前 | 自前 |
| 料金感 | Zero Trust Free〜・Standardから従量 | 個別見積（高単価帯） | M365 E5に内包またはアドオン | 個別見積 | Prismaバンドル |

カバレッジとInline制御の総合力ではNetskope / Microsoftが上位だが、「Cloudflare One全体に1点足せばSaaS可視化が立つ」という統合性とコスト効率は他にない強みである。

## 料金
- **Free**：Zero Trust Freeに含まれ、最大2つのCASB integration まで設定可能。50ユーザーまで。Posture Findings は確認可能だが、Findingの詳細表示や全integration活用にはEnterpriseが必要。
- **Pay-as-you-go / Standard**：Zero Trust有償プランの一部としてCASBが利用可能（ユーザー単価ベース）。
- **Enterprise**：全対応SaaS integration、詳細Finding（影響範囲・関連ユーザー・修復導線）、DLPプロファイル連携、SCIM、サポートSLAが付帯する。

要するに、PoCはFreeで2 integrationまで試し、本格運用時はZero Trust Enterpriseに揃えるのが現実的な導入パスである。

## CLI / IaC 操作例

CASB integration自体（OAuthでSaaSテナントに接続する操作）は管理画面ベースであり、Terraformの正式リソースは限定的である。一方、CASBから検出されたFindingに対する**Gatewayポリシー化**や、CASB前段の**Access統合**はTerraformで宣言できる。

### Terraform：Findingsを起点にしたGateway HTTPポリシー
```hcl
# CASBが検出したGoogle Workspaceの公開ファイル共有を、Gatewayでブロック
resource "cloudflare_zero_trust_gateway_policy" "block_public_drive" {
  account_id  = var.account_id
  name        = "Block public Google Drive shares flagged by CASB"
  description = "CASB Posture Finding 経由で発見された公開リンクをDownload時にブロック"
  precedence  = 100
  action      = "block"
  filters     = ["http"]
  enabled     = true

  traffic = "any(http.request.uri.content_category[*] in {\"file sharing\"})"
  identity = "any(identity.email matches \".*@example.com\")"
}
```

### Terraform：CASB対象SaaSをAccess SaaS Applicationとして前段に立てる
```hcl
resource "cloudflare_zero_trust_access_application" "salesforce" {
  account_id       = var.account_id
  name             = "Salesforce"
  type             = "saas"
  session_duration = "24h"

  saas_app = {
    auth_type = "saml"
    sp_entity_id = "https://example.my.salesforce.com"
    consumer_service_url = "https://example.my.salesforce.com?so=..."
  }
}
```

CASBはSaaSテナント内部を見るレイヤ、Access SaaS統合はSaaSへの入口を見るレイヤであり、両者を組合せると「入口でSSO制御 + 内部で設定監査」の二重防御になる。

### API（参考）
- `GET /accounts/{account_id}/zt_risk_scoring/integrations`
- `GET /accounts/{account_id}/zt_risk_scoring/findings`

Findings APIをCI / SOAR連携で叩き、Slack通知やJira起票につなぐ運用が現実的である。

## 制限・注意点
- **Inlineブロックは持たない**。リアルタイム遮断はGateway / DLP併用が前提である。CASB単体導入では「見える化」までに留まる。
- **対応SaaSの幅は競合より狭い**。社内利用SaaSの棚卸しを先に行い、対応外であればNetskope等の併用も検討する。
- **APIスキャン間隔は1〜24時間**。ゼロタイムでの検知ではなく、設定ミスを「事後最短」で見つける性質と理解する。
- **Free枠は2 integration / Finding詳細制限あり**。本番運用ではEnterpriseが事実上の前提となる。
- **OAuth認可スコープが広い**ものもあり、対象SaaS側の管理者と権限レビューを行ったうえで接続する必要がある。
- **オンプレSaaS（自社GitLab等）は対象外**。
- Findingの放置は「検出している＝管理している」という誤った安心を生む。SLA（Severity別の対応期限）を運用ルールとして定めるべきである。

## 参考リンク
- Cloudflare CASB 概要：https://developers.cloudflare.com/cloudflare-one/applications/casb/
- CASB integrations 一覧：https://developers.cloudflare.com/cloudflare-one/applications/casb/casb-integrations/
- Manage findings：https://developers.cloudflare.com/cloudflare-one/applications/casb/manage-findings/
- Cloudflare DLP：https://developers.cloudflare.com/cloudflare-one/policies/data-loss-prevention/
- Cloudflare Gateway：https://developers.cloudflare.com/cloudflare-one/policies/gateway/
- Cloudflare One llms.txt：https://developers.cloudflare.com/cloudflare-one/llms.txt
- Terraform Provider（cloudflare_zero_trust_gateway_policy / cloudflare_zero_trust_access_application）：https://registry.terraform.io/providers/cloudflare/cloudflare/latest/docs

---
参照日: 2026-05-03
