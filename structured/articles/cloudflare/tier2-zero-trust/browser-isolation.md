# Browser Isolation (Cloudflare One)

## 一行サマリ
Cloudflareのエッジ上で実行された「リモートブラウザ」が描画ベクター情報のみをユーザー端末に転送し、JavaScriptや能動コンテンツを端末に一切到達させずにWebを閲覧させる、Network Vector Rendering（NVR）方式のリモートブラウザ分離（Remote Browser Isolation, RBI）サービスである。

## 解決する課題（Why）
従来のセキュアWebゲートウェイ（SWG）はURL/カテゴリでブロックする発想であり、未分類ドメインや正規サイトを踏み台にしたゼロデイ・水飲み場攻撃には無力である。一方で従来のRBIはピクセルストリーミングやDOMミラーリング方式が主流で、帯域・遅延・レンダリング崩れの問題からユーザー体験が著しく劣化していた。Cloudflare Browser Isolationは以下を解決する。

- ブラウザ経由のゼロデイマルウェア・ドライブバイダウンロードの遮断（コードはエッジで実行され端末に届かない）。
- フィッシングサイトでのキーボード入力禁止による認証情報窃取の抑止。
- コピー＆ペースト・印刷・アップロード・ダウンロードを粒度を持って制御することによる情報持ち出しの抑止（DLPの代替・補完）。
- BYOD・委託先・契約社員などの非管理端末に対し、エージェント不要で安全な業務Webアクセスを配布。
- 既存ブラウザのまま使えるため、専用クライアントを配るタイプのRBI（Talon等）に比べ展開コストが極小。

## 主要機能（What）

- **Network Vector Rendering (NVR)**：Cloudflare独自方式。リモートブラウザがレンダリングした「描画ベクター」（描画コマンド列）のみをHTML5互換クライアントに転送する。ピクセルストリーミングのような帯域消費もDOMミラーリングのような互換性問題も避け、ローカルブラウザで描画したのと見分けがつかない体験を実現する。
- **Clientless（プレフィックスURL方式）**：`https://<team>.cloudflareaccess.com/browser/<URL>` の形式でアクセスするだけで、WARPクライアント無しに任意の端末からRBIを利用できる。BYOD・社外協力者・短期契約者向け。
- **In-line（WARP/Gateway経由）**：WARPクライアントを入れた管理端末に対しては、通常のURLを透過的にIsolate判定する。ユーザーは普段どおり閲覧し、危険サイトのみ自動的にエッジブラウザへ流れる。
- **Access連携（Clientlessの認可レイヤ）**：Clientless Web Isolationの入口にCloudflare Accessポリシーを掛けられる。誰がリモートブラウザを使えるか、どのIdPで認証するかをAccessのDSLで制御する。社内Webアプリの保護に使う通常のAccessポリシー（Tier 1参照）と同じ仕組みを再利用する。
- **Data protection controls（`bisoadmincontrols`）**：以下6項目を許可/禁止/限定の単位で設定する。
  - **Copy（Remote → Client）**：リモート→ローカル方向のクリップボードコピー。
  - **Paste（Client → Remote）**：ローカル→リモート方向の貼付け。
  - **Download**：ファイルのローカル保存。`view in remote browser only`（プレビュー閲覧のみ）も選択可。
  - **Upload**：ローカルからリモートへのファイルアップロード。
  - **Keyboard**：キーボード入力。フィッシング疑惑サイトで入力だけ禁止する用途に有効。
  - **Print**：ローカル印刷。
- **Tunnel連携によるプライベートWebアプリの分離アクセス**：Tunnel配下の社内アプリ（例：`http://192.168.2.1:7148`）へClientless URL経由で到達できる。VPN無しに非管理端末から社内Webを安全に触らせたい場合の決定打。
- **Local Domain Fallback / Do Not Isolate**：信頼済みドメインや銀行・社内SaaS等、分離するとUXが壊れるサイトを明示的に除外できる。Local Domain FallbackはGateway側のDNS逃がし機能と組合わせて使う。

## アーキテクト視点：いつ選ぶか

### 適しているシーン
- 未分類ドメインや短期間しか存在しないフィッシング・C2系ドメインを踏ませる前提で、SWGブロックでは取りこぼす攻撃面を物理的に切り離したい組織。
- BYOD・業務委託・M&A直後で端末管理が混在しており、エージェント配布が現実的でないケースのSafe Browsing提供。
- 開発者・SOCがマルウェアサンプルや疑わしいURLを業務として開く必要があり、検体実行を端末に持ち込みたくない。
- 機密データ取扱い系SaaS（Salesforce / HRIS / 経理）について、ダウンロードと印刷だけ禁止して情報持ち出しを抑える「軽量DLP」用途。
- 子会社・取引先に対し、Tunnel配下の社内Webアプリへのアクセスを「クライアントレスかつIsolated」で配布したい。

### 適していないシーン
- 動画会議・WebRTC・低遅延ゲーム等、リアルタイム双方向メディア前提のアプリ。NVRでも遅延・互換性が問題になりやすい。
- 帯域が極端に細い回線（モバイル従量課金、海上・現場拠点）。NVRはピクセル方式より軽いが完全にローカルブラウザ並みではない。
- 「すべてのWebを常にIsolate」の運用設計。コスト・体感・対応外サイトの観点で破綻するため、リスクベースで部分適用するのが定石。
- エンドポイントDLPの全代替。クリップボード/印刷/DLは抑えられるが、スクリーンショットや写真撮影には無力で、エンドポイントEDR/DLPと併用する前提である。

## 競合・代替

| 観点 | Cloudflare RBI | Menlo Security | Zscaler Cloud Browser | Talon (Palo Alto Prisma Access Browser) |
|---|---|---|---|---|
| レンダリング方式 | Network Vector Rendering（描画コマンド転送） | DOM Mirroring / Adaptive Clientless Rendering | ピクセル/DOM混合 | 専用Chromiumフォーク（端末側で実行） |
| クライアント | 不要（既存ブラウザのまま） | 不要 | 不要（Zscalerクライアント有でも可） | 専用ブラウザ配布が必要 |
| Clientless URL | あり（`/browser/<URL>`） | あり | あり | 概念が異なる（ブラウザ自体が境界） |
| Access/ZTNA統合 | Cloudflare Access / Tunnelとネイティブ連携 | 単体製品寄り、ZTNAは別連携 | Zscaler Private Access統合 | Prisma Access統合 |
| DLPコントロール | clipboard / print / DL / UL / keyboard | 同等 | 同等 | ブラウザ内ポリシーで強力 |
| 強み | エッジ網のレイテンシ優位・他Cloudflare One機能と一体・既存ブラウザ流用 | RBI専業の歴史と精度 | 大企業向けSWG/ZTNAスイート統合 | エンタープライズブラウザというカテゴリ自体の強さ |
| 弱み | RBI単体としての成熟度では老舗に一歩譲る側面 | スイート全体の選択肢が狭い | アーキテクチャが重い・価格 | 端末側に専用ブラウザ配布の運用コスト |
| 価格モデル | Zero Trust Pay-as-you-go / Enterpriseのアドオン | エンタープライズ商談 | エンタープライズ商談 | エンタープライズ商談（買収後Prisma配下） |

Cloudflareの差別化要素は「Access / Gateway / Tunnel / WARPと同じコントロールプレーンに乗っていること」「NVRによるUXの近さ」であり、Zero Trust一式をCloudflareで揃える前提なら第一候補となる。

## 料金
- **Free / Pay-as-you-go ベース**：Browser IsolationはCloudflare Zero Trustの**アドオン**として提供される。
- **Pay-as-you-go**：ユーザー単位の従量課金にBrowser Isolationアドオン料金が加算される（公開Webでは「Pay-as-you-goおよびEnterpriseプランへのアドオン」と明記）。
- **Enterprise**：契約に組込み可能。SCIM・User Risk Score・SLAなどとセットで提案される。

無料枠50ユーザーのZero Trust基本機能には**含まれない**点が、Tier 1で扱ったAccessとの大きな違いである。RBIを使う段階で課金プランへの移行が必要となる。

## CLI / IaC 操作例

### Terraform：Isolateアクション付きGatewayポリシー（HTTPルール）
Browser Isolationは `cloudflare_zero_trust_gateway_policy` の `action = "isolate"` で発動し、`rule_settings.bisoadmincontrols` で粒度制御を行う。

```hcl
resource "cloudflare_zero_trust_gateway_policy" "isolate_uncategorized" {
  account_id  = var.account_id
  name        = "Isolate uncategorized & risky categories"
  description = "未分類・新規ドメイン・セキュリティリスクをRBIへ"
  precedence  = 100
  enabled     = true
  action      = "isolate"
  filters     = ["http"]

  # 未分類 + 新規ドメイン + Security Risksカテゴリ
  traffic = "any(http.request.uri.content_category[*] in {1 2 3})"

  rule_settings = {
    biso_admin_controls = {
      dcp = true   # disable copy   (Remote -> Client)
      dp  = true   # disable paste  (Client -> Remote)
      dd  = true   # disable download
      du  = true   # disable upload
      dk  = false  # keyboard許可（業務閲覧のため）
      dpr = true   # disable print
    }
  }
}
```

### Terraform：機密SaaSの「ダウンロード/印刷だけ禁止」軽量DLPパターン
```hcl
resource "cloudflare_zero_trust_gateway_policy" "isolate_hris" {
  account_id = var.account_id
  name       = "Isolate HRIS - block download/print only"
  precedence = 50
  enabled    = true
  action     = "isolate"
  filters    = ["http"]

  traffic = "any(http.request.host in {\"hris.example.com\"})"

  rule_settings = {
    biso_admin_controls = {
      dcp = false
      dp  = false
      dd  = true
      du  = false
      dk  = false
      dpr = true
    }
  }
}
```

### Clientless URL（運用例）
```
https://<team-name>.cloudflareaccess.com/browser/https://intranet.internal/
```
このURLの前段にAccess applicationを掛けることで、認証済みユーザーだけがClientless RBI経由で社内Tunnelアプリに到達できる構成を組める。

## 制限・注意点
- **HTTPポリシーの適用にはTLS復号が必須**。証明書ピン留めしているサイト・アプリではIsolate配下で動かない場合がある。
- **WebRTC / 動画会議系**は遅延と互換性の問題で実用に耐えないことが多い。Do Not Isolateで明示除外する設計が前提。
- **PDF・大容量メディア**はリモートブラウザ内ビューア（`view in remote browser only`）に閉じ込めると安全側に倒せるが、ローカル編集ワークフローとは衝突する。
- **同時セッション数**：ブラウザ種別あたりの同時インスタンス数に上限がある（公式トラブルシュートで言及。「No Browsers Available」エラー）。重め業務での前提条件として把握しておくこと。
- **Clientless URLの公開範囲**：Access policyを正しく組まないと、`/browser/<任意URL>` で社内Tunnelの全アプリに到達されうる。AccessのIncludeを必ず人/グループ単位に絞る。
- **AccessのBypassポリシー併用時の注意**：Tier 1で触れたとおり、Bypassは制御を完全に外す。Clientless RBIの入口でBypassを多用するとRBIごと素通りされるため、原則Service Authで代替する。
- **OS・GPU依存の描画問題**：Windowsで稀にWebGL関連エラー・空白描画が発生する。ソフトウェアラスタライゼーション設定で回避できるケースがあるが、業務利用前のパイロット検証必須。
- **コスト跳ね**：「全URLをIsolate」設計は、ユーザー数 × トラフィックでアドオン費用が跳ねる。リスクカテゴリ・未分類・特定SaaSなど対象を絞った設計が定石である。

## 参考リンク
- Browser Isolation 概要：https://developers.cloudflare.com/cloudflare-one/policies/browser-isolation/
- Isolation policies（bisoadmincontrols）：https://developers.cloudflare.com/cloudflare-one/policies/browser-isolation/isolation-policies/
- Setup（In-line / Clientless）：https://developers.cloudflare.com/cloudflare-one/policies/browser-isolation/setup/
- Clientless Web Isolation：https://developers.cloudflare.com/cloudflare-one/policies/browser-isolation/setup/clientless-browser-isolation/
- Troubleshooting：https://developers.cloudflare.com/cloudflare-one/policies/browser-isolation/troubleshooting/
- Terraform Provider（cloudflare_zero_trust_gateway_policy）：https://registry.terraform.io/providers/cloudflare/cloudflare/latest/docs/resources/zero_trust_gateway_policy

---
参照日: 2026-05-03
