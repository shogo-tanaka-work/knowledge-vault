# Data Loss Prevention (Cloudflare One)

## 一行サマリ
Cloudflare DLPは、Gateway・CASB・Email Security・AI Gatewayという複数のトラフィック検査点に共通して差し込まれる検出エンジンであり、機密データの外部流出を「インライン（HTTP/メール）」と「データ保管時（SaaS API）」の両面で同時に制御するアドオンサービスである。

## 解決する課題（Why）
クラウドとSaaS、生成AIの普及によって機密データの流出経路は劇的に増えており、エンドポイントDLPやメール単体のDLPでは「ChatGPTにソースコードを貼られる」「Google Driveから個人共有される」「退職者が顧客リストをダウンロードする」といった経路を網羅できない。Cloudflare DLPは、ZTNAと同じConnectivity Cloud上に検査エンジンを置くことで以下を解決する。

- インライン経路（Web/SaaS/AI）と静止データ経路（SaaS API）の検査ポリシーを単一プロファイルで共有できる。
- TLSインスペクション済みのGatewayトラフィックに直接適用できるため、追加プロキシを挟まずにDLPを有効化できる。
- 既知のサンプル文書・実データを基にしたファジー検出（Document Fingerprinting / EDM）が可能で、正規表現だけのDLPに比べて誤検知を抑えられる。
- 生成AIプロンプトの検査（AI Gateway連携）にも同じプロファイルを再利用できる。

## 主要機能（What）
DLPはそれ自体が独立したプロキシではなく、**検出ロジック（Detection entries）→ プロファイル → ポリシー** の3層で構成され、Gateway / CASB / Email Security / AI Gateway から呼び出される。

- **Predefined profiles**：Cloudflareがメンテする組み込みプロファイル。Financial Information、Social Security / Insurance / Tax / Identifier Numbers、Health Information、Credentials and Secrets など多数を提供する。Free / Pay-as-you-goプランでもこのうち2種は利用可能で、評価導入のハードルが低い。
- **Custom profiles（regex）**：RE2構文の正規表現で独自パターンを定義する。1パターンあたり1024バイト、UTF-8最大4バイト/文字までという上限がある。社員番号・案件IDなど社内固有の識別子に使う。
- **Exact Data Match (EDM)**：顧客マスタや従業員名簿などの実データを `.csv` / `.txt`（LF改行）でアップロードし、Cloudflare到達前にクライアント側でハッシュ化する。トラフィック側もハッシュ化して照合するため、機密データそのものはCloudflareに渡らず、ログでも自動マスクされる。各エントリは最低6文字必要。
- **Document Fingerprinting**：契約書テンプレートや設計書のサンプル `.docx` / `.txt`（10MBまで）をアップロードすると、Cloudflareがフィンガープリントを生成し、類似度しきい値（0-100%）で「派生したコピー」を検出する。完全一致ではないため、抜粋・改変されたコピーにも反応する。
- **Optical Character Recognition (OCR)**：画像・PDF内のテキストをスキャンして上記プロファイルにかける機能。スクリーンショット経由の流出に対応する。
- **Custom Wordlists / AI prompt topics**：機密用語リスト、および生成AIプロンプトのトピック分類（ソースコード共有、個人情報送信など）にも対応する。
- **対応ファイル種別**：テキスト・CSV、Microsoft Office 2007+ (`.docx` / `.xlsx` / `.pptx`) およびMicrosoft 365、PDF、ZIP（再帰圧縮10階層まで）。

### Gateway / CASB / Email との統合（DLPは検出側）
Gateway・CASB・Email Securityは別記事で詳述するが、DLPはこれらに「呼び出される側」として動作する。統合点を整理すると以下になる。

| 統合先 | 検査対象 | 前提条件 |
|---|---|---|
| Cloudflare Gateway（HTTP policy） | インラインHTTP/HTTPSトラフィック | TLSインスペクション必須・WARP / PACでクライアントを誘導 |
| Cloudflare CASB | Google Workspace / Microsoft 365 / Salesforce / GitHub等のSaaSに保管中のファイル | API経由のテナント連携（OAuth） |
| Cloudflare Email Security | Outboundメール本文・添付 | Email Security導入済みドメイン |
| Cloudflare AI Gateway | 生成AIへのプロンプト・レスポンス | TLSインスペクション不要（AI Gateway自体が中継するため） |

このため「DLPだけ」を導入しても効果はなく、最低でもGatewayまたはCASB / Email Securityのいずれかと組み合わせる前提となる。

## アーキテクト視点：いつ選ぶか

### 適しているシーン
- すでにCloudflare GatewayでSWGを運用しており、TLSインスペクションが有効な組織。最小コストでインラインDLPを足せる。
- Microsoft 365 / Google WorkspaceをCASB対象として持ち、保管中ファイルに対する継続スキャンが必要なケース。
- 生成AI利用ガバナンスの整備で、ChatGPT・Claude等への機密データ投入をブロックしたい組織（AI Gateway連携）。
- 顧客マスタなど「実データ」を既に保有しており、EDMでハッシュ照合したいケース。サンプル契約書のコピー検出にDocument Fingerprintingが要るケース。
- Predefined profilesで足りる、PCI / PII / マイナンバー的な汎用検出から始めたい組織。

### 適していないシーン
- エンドポイント側でのコピー＆ペースト・USB転送・印刷を制御したいケース。CloudflareのDLPはネットワーク・SaaS APIの検査が主眼であり、ホストエージェント由来の制御はできない（Symantec DLP / Forcepoint DLPの領域）。
- TLSインスペクションを組織ポリシーや法規制で許容できない環境。インラインDLPは事実上機能しない。
- ニッチなビジネスアプリ（独自プロトコル・SaaS未対応のもの）に対する保管中スキャン。CASBコネクタが提供されないSaaSは対象外となる。
- DLP単体で買いたい組織。AdvanceedなDLPはZero Trust Enterpriseプランのアドオンであり、DLPだけ切り出した契約形態は存在しない。

## 競合・代替

| 観点 | Cloudflare DLP | Symantec DLP | Microsoft Purview DLP | Netskope DLP | Forcepoint DLP |
|---|---|---|---|---|---|
| 提供形態 | SASE/SSE一体型のアドオン | エージェント＋オンプレ＋クラウドの複合 | Microsoft 365に組み込み | SASE一体型 | エンドポイント＋ネットワーク＋クラウド |
| インライン検査 | Gateway経由（TLS必須） | プロキシ製品と組合せ | Edge / Defender for Cloud Apps | 内蔵プロキシ | 専用ネットワークDLP |
| SaaS API連携 | CASB（M365 / Workspace / Salesforce / GitHub等） | CloudSOC | M365内は強い・他SaaSはDefender for Cloud Apps | 100以上のSaaS | CASB別ライセンス |
| 検出技術 | Predefined / regex / EDM / Fingerprinting / OCR / AI prompt | EDM / Fingerprinting / VML / OCR | Sensitive info types / EDM / Fingerprinting / Trainable classifiers | EDM / Fingerprinting / ML | Fingerprinting / 機械学習 / OCR |
| エンドポイント制御 | なし | あり（強み） | Endpoint DLP（M365 E5） | あり | あり（強み） |
| 生成AI対応 | AI Gateway連携でネイティブ | 個別ポリシーで対応 | Purview AI Hub | SkopeAI | 個別対応 |
| 価格モデル | Zero Trust Enterpriseアドオン | エンタープライズライセンス | M365 E5に同梱 / 別ライセンス | サブスクリプション | サブスクリプション |
| 強み | SASEと同一ファブリック・AI連携・EDMが既定で利用可 | 検出エンジンの成熟・エンドポイント | M365との一体感・コスト効率 | SaaSカバレッジ | エンドポイント検査 |
| 弱み | エンドポイント制御がない・Enterprise必須 | 運用コスト高・別物のアーキ | M365外のカバレッジ | Cloudflare比でアーキが分散 | クラウドネイティブ感は薄い |

CloudflareのDLPは「検出器の網羅度」では老舗3社（Symantec / Forcepoint / Microsoft Purview）に並び始めた段階であり、強みは検出器単体ではなくSASE一体での運用容易性とAI Gatewayとの統合にある。

## 料金
- **Free / Pay-as-you-go**：Predefined profilesのうち2種（Financial Information / Social Security 等の識別子系）、ペイロードロギング、誤検知レポートのみ利用可能。評価・PoC用途の位置付け。
- **Zero Trust Enterprise**：DLPはこのプランの**アドオン**として提供される。すべてのPredefined profile、Custom regex、EDM、Document Fingerprinting、OCR、AI promptトピック検出、CASB / Email Security連携、API経由のプロファイル管理、SIEM連携などが解放される。
- DLPは**ユーザー単位の追加課金**であり、対象ユーザー数とCASBコネクタ数で見積りが膨らみやすい。Enterprise契約時にCloudflare営業との個別見積りが前提となる。

## CLI / IaC 操作例
DLPプロファイルとデータセット（EDM・Fingerprinting）はTerraform Provider v5以降で `cloudflare_zero_trust_dlp_*` リソースとして管理できる。

```hcl
# Custom DLP profile（regexベース）
resource "cloudflare_zero_trust_dlp_custom_profile" "employee_id" {
  account_id  = var.account_id
  name        = "Employee ID Pattern"
  description = "EMP-12345 形式の社員番号を検出"

  entry {
    name    = "Employee ID"
    enabled = true
    pattern = {
      regex      = "EMP-[0-9]{5}"
      validation = "luhn" # 任意。クレジットカード形式の場合
    }
  }

  context_awareness = {
    enabled = true
    skip = {
      files = false # ファイル本文もスキャン
    }
  }
}

# EDM データセット（実データのハッシュ照合）
resource "cloudflare_zero_trust_dlp_dataset" "customers_edm" {
  account_id        = var.account_id
  name              = "Customer Master EDM"
  description       = "顧客マスタからのEDMデータセット"
  encoding_version  = 2
  upload {
    type = "exact_data_match"
  }
}

# Gateway HTTP policy にDLPプロファイルを適用
resource "cloudflare_zero_trust_gateway_policy" "block_employee_id_upload" {
  account_id = var.account_id
  name       = "Block Employee ID upload"
  precedence = 100
  action     = "block"
  filters    = ["http"]

  traffic = "any(dlp.profiles[*] in {\"${cloudflare_zero_trust_dlp_custom_profile.employee_id.id}\"})"
}
```

EDMデータセットは `cloudflare_zero_trust_dlp_dataset` を作成した後、CLIまたは管理画面から `.csv` / `.txt` を**クライアント側でハッシュ化してアップロード**するフローになる。実データそのものはTerraform stateには載らないため、stateの暗号化と分離は不要だが、生CSVの保管場所は別途設計する必要がある。

## 制限・注意点
- **TLSインスペクション必須**：インラインHTTPでのDLPはTLS復号を前提とする。証明書ピンニングを行うアプリ（金融系SDK等）はBypass設定が必要で、その経路のDLPは効かなくなる。
- **誤検知**：regexベースの検出は誤検知が出やすい。Document FingerprintingとEDMで補完するか、Context awareness（前後のキーワードで絞り込む機能）を併用する設計が望ましい。
- **スキャン上限**：Document Fingerprintingのサンプル文書は1ファイル10MBまで、regexパターンは1024バイトまで、EDMの各エントリは最低6文字必要、ZIPは再帰10階層まで。これを超える対象は検出から漏れる。
- **暗号化済みファイル**：パスワード付きZIP、暗号化PDFなどは復号できないため、Gatewayポリシー側で「暗号化ファイル全般をブロック」する別ルールと組合せるのが定石である。
- **ペイロードロギングの取り扱い**：マッチしたペイロードを画像付きで保存する機能は、それ自体が機密データの新たな保管点になる。閲覧権限を持つロールを最小化し、アクセスログを別ストレージに集約する運用が必要である。
- **アドオン契約**：Zero Trust Enterpriseのアドオンであり、Pay-as-you-goから単独でアップグレードできない。導入には商談ベースの契約変更が必要である。
- **エンドポイント制御の不在**：USBコピー・ローカル印刷・スクリーンショット転送は対象外。エンドポイントDLPと併用する場合は責務分界を明確にしておく。

## 参考リンク
- Data Loss Prevention：https://developers.cloudflare.com/cloudflare-one/policies/data-loss-prevention/
- DLP profiles：https://developers.cloudflare.com/cloudflare-one/policies/data-loss-prevention/dlp-profiles/
- Detection entries（EDM / Fingerprinting / Wordlists）：https://developers.cloudflare.com/cloudflare-one/policies/data-loss-prevention/detection-entries/configure-detection-entries/
- Cloudflare One llms.txt：https://developers.cloudflare.com/cloudflare-one/llms.txt
- Terraform Provider（cloudflare_zero_trust_dlp_*）：https://registry.terraform.io/providers/cloudflare/cloudflare/latest/docs

---
参照日: 2026-05-03
