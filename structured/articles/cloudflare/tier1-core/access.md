# Access (Cloudflare One)

## 一行サマリ
アプリケーションの前段にCloudflareエッジを置き、IdP認証とポリシー判定によってアクセスを制御するアイデンティティ対応プロキシ型のZTNA（Zero Trust Network Access）サービスである。

## 解決する課題（Why）
従来型のVPNは「ネットワークに入れたら全部見える」というフラットな信頼モデルであり、退職時のアクセス剥奪が遅れる、踏み台化されやすい、SaaSには適用できない、といった構造的な問題を抱えている。Cloudflare Accessはこれを置き換え、すべてのHTTPリクエストをエッジで認証・認可することで以下を解決する。

- VPNゲートウェイの撤廃と運用負荷の削減。
- SaaSアプリ・社内Webアプリ・SSH/RDP・MCPサーバーまで同一ポリシーで保護。
- 退職・権限変更時にIdP側で無効化すればアクセスが即座に剥奪される。
- デバイスポスチャ・地理・リスクスコアを組み合わせた継続的な評価が可能。

## 主要機能（What）
- **IdP連携**：Google / Okta / Microsoft Entra ID / GitHub / 任意のSAML・OIDCを統合。複数IdPの同時運用にも対応する。
- **ポリシーDSL**：Action（Allow / Block / Bypass / Service Auth）× Rule type（Include / Exclude / Require）× Selector（Email / Country / IP / Device posture / User Risk Score 等）の組合せでアクセスを定義する。
- **Service Token / mTLS**：人間ユーザーを介さないM2M通信向けの認証方式。CI/CDやエージェントから内部APIへのアクセスに使う。
- **Browser-based RDP / SSH**：クライアントレスでRDP・SSHをブラウザから利用可能。クリップボード制御・UNIXユーザー名制限などの細かいConnection contextを設定できる。
- **Linked App Token / Managed OAuth**：Accessをアイデンティティ層として外部アプリに渡せる仕組み。
- **継続評価**：IP・国・デバイスポスチャ・リスクスコアはセッション中もリクエストごとに評価される。

## アクセスフロー
```
ユーザー → Cloudflareエッジ（最寄りPoP）
        ↓ IdPへリダイレクトしSSO認証
        ↓ JWT発行（Cf-Access-Jwt-Assertion）
        ↓ Access policy 判定（Service Auth → Bypass → Allow/Block の順）
        ↓ Tunnel または公開オリジンへルーティング
       オリジンアプリ
```

オリジンに到達するリクエストには署名付きJWTが付与され、オリジン側で再検証することで「Cloudflareを経由していないリクエスト」を排除できる。

## 対応IdP
SAML・OIDC汎用に加え、以下を専用コネクタとして提供する。

- Google / Google Workspace
- Okta（OIDC・SAML両対応）
- Microsoft Entra ID（旧Azure AD）
- GitHub
- OneLogin（OIDC・SAML）
- PingOne / PingFederate
- JumpCloud / Keycloak / Centrify / Citrix ADC（SAML）
- Amazon Cognito / AWS IAM（SAML）
- Facebook / LinkedIn / Yandex（ソーシャル）
- One-time PIN（IdP不要、メール宛にOTP送信）

## アーキテクト視点：いつ選ぶか

### 適しているシーン
- 社内管理ツール（Admin panel、Grafana、Kibana、Jenkins、Argo CD）の保護。
- staging / preview環境の関係者限定公開。
- VPN撤廃を前提としたZTNA移行。
- SaaS（Salesforce / Workday等）にCloudflare Accessを差し込んでSSOを統一。
- MCPサーバーや内部APIの認可レイヤとして。
- クライアントレスで外部協力会社にSSH・RDPを配りたいケース。

### 適していないシーン
- B2C向けのエンドユーザー認証（顧客アカウントのサインアップ・パスワードリセット等のフルライフサイクルが必要）。これはAuth0 / Cognito / Cloudflareの別機能（Managed OAuth）の領域である。
- IdPを持たない・整備する気がない組織（OTPで凌げる規模ならよいが、本格運用にはIdP前提）。
- アプリ内の細粒度認可（行レベル権限など）。Accessはあくまで「到達できるか」を制御する層であり、アプリ内RBACは別途必要である。

## 競合・代替

| 観点 | Cloudflare Access | Okta SSO | Tailscale | Twingate |
|---|---|---|---|---|
| モデル | アイデンティティ対応プロキシ（HTTP/SSH/RDP） | IdP+SSOブローカー | WireGuardベースのMesh VPN | ZTNAコネクタ型 |
| クライアント | 不要（HTTPはブラウザのみ） | 不要 | 必要（WireGuardクライアント） | 必要 |
| SaaS保護 | 可能（SAML IdPとして振る舞う） | 本職 | 不可 | 限定的 |
| 内部Webアプリ | Tunnelと組合せでDNS不要・IP公開不要 | リバースプロキシ別途必要 | ネットワーク到達で代用 | コネクタ経由 |
| 価格 | 50ユーザーまで無料 | $2〜/ユーザー/月〜 | 3ユーザーまで無料 | 5ユーザーまで無料 |
| 強み | エッジで完結・無料枠が広い・Tunnel連携 | IdPとしての成熟度・ガバナンス | 設定の容易さ | UI |
| 弱み | IdP機能は持たない（前段にIdP必須） | アプリ前段プロキシ機能は別 | HTTPアプリ単位の認可は弱い | 規模感はAccessに劣る |

CloudflareにはWorkersベースのアプリ認証機構もあるが、AccessはIdP統合・ポリシー判定・監査ログまで揃ったマネージドな選択肢であり、自前実装より優先される。

## Tunnel との組合せ
Accessは「誰が来てよいか」を決めるレイヤで、Cloudflare Tunnel（cloudflared）は「どこへ繋ぐか」を決めるレイヤである。両者の組合せで、

- オリジンサーバーのインバウンドポートを完全に閉じられる（アウトバウンドのみでCloudflareへ接続）。
- DNSを公開しない内部ホスト名でも社外からアクセスできる。
- IPアドレスベースの攻撃面がゼロになる。

という構成が成立する。実運用では「Tunnel + Access」をセットで設計するのが定石である。

## 料金モデルの要点
- **Free**：50ユーザーまでAccess・Gateway基本機能を利用可能。
- **Standard / Pay-as-you-go**：$7/ユーザー/月程度から、ユーザー数に応じて従量課金。
- **Enterprise**：User Risk Score、AI controls、SCIMの高度連携、サポートSLAなどが追加される。

無料枠が50ユーザーまであるため、スタートアップや少人数チームではコストゼロでZTNAを導入できる点が大きな差別化要素である。

## CLI / IaC 操作例

### Terraform（cloudflare provider v5）
```hcl
resource "cloudflare_zero_trust_access_application" "internal_admin" {
  account_id       = var.account_id
  name             = "Internal Admin"
  domain           = "admin.example.com"
  type             = "self_hosted"
  session_duration = "24h"
  allowed_idps     = [cloudflare_zero_trust_access_identity_provider.google.id]
  auto_redirect_to_identity = true
}

resource "cloudflare_zero_trust_access_policy" "allow_company" {
  account_id     = var.account_id
  application_id = cloudflare_zero_trust_access_application.internal_admin.id
  name           = "Allow company emails"
  precedence     = 1
  decision       = "allow"

  include = [{
    email_domain = { domain = "example.com" }
  }]

  require = [{
    geo = { country_code = "JP" }
  }]
}
```

### wrangler / cloudflared
- `cloudflared tunnel create internal-admin`
- `cloudflared tunnel route dns internal-admin admin.example.com`
- `cloudflared tunnel run internal-admin`

これでオリジンを公開せずに `admin.example.com` をAccess配下に出せる。

## 制限・注意点
- SaaSアプリにおいては、Accessはサインオン時とセッション再発行時のみポリシーを評価する。セッション継続中の継続評価はSaaS側のセッション管理に委ねられる。
- **Bypass**ポリシーはセキュリティ制御を完全に外し、ログも残らない。安易な利用は厳禁で、原則Service Authで代替する。
- Bypassポリシーにデバイスポスチャを組合せた場合、ZarazやWorkersがリクエストを横取りすると機能しない既知の制約がある。
- 「Include: Everyone」「Include: One-time PIN」を入れると事実上全公開になる典型的な誤設定がある。
- User Risk ScoreやSCIM強制再評価などはEnterpriseプランの機能である。
- オリジン側でJWT検証をしないと、Cloudflareをバイパスする攻撃経路が残る。Tunnelとの併用で塞ぐのが望ましい。

## 参考リンク
- Cloudflare Access Policies：https://developers.cloudflare.com/cloudflare-one/policies/access/
- Add web applications：https://developers.cloudflare.com/cloudflare-one/applications/
- Identity providers：https://developers.cloudflare.com/cloudflare-one/identity/
- Cloudflare One llms.txt：https://developers.cloudflare.com/cloudflare-one/llms.txt
- Terraform Provider (cloudflare_zero_trust_access_application)：https://registry.terraform.io/providers/cloudflare/cloudflare/latest/docs

---
参照日: 2026-05-03
