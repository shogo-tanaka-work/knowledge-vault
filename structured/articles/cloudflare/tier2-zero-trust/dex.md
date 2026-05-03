# Digital Experience Monitoring (Cloudflare One)

## 一行サマリ
WARPデバイスから送出されるテレメトリと合成テスト（Synthetic Tests）を集約し、ユーザー端末からSaaS・社内アプリ・Tunnel配下のオリジンに至るまでのエンドツーエンドな到達性とパフォーマンスを可視化するDEX（Digital Experience Monitoring）サービスである。

## 解決する課題（Why）— リモートワーク時代の「ユーザー側起因の障害」可視化
従来のAPMやサーバー側モニタリングは「オリジンからの応答」までしか見ておらず、ユーザー宅のWi-Fi品質・ISPの経路問題・端末のCPU/メモリ枯渇・WARPの接続不全など、サーバーサイドからは観測できない領域が完全な盲点となっていた。リモートワーク常態化により、ヘルプデスクへの「なんか遅い」という曖昧な問い合わせが急増しているが、これを再現・切り分けする手段が長年欠けていた。Cloudflare DEXはWARPクライアントが既に各端末に入っている前提を活かし、以下を解決する。

- 端末ごとのCPU・メモリ・接続先colo・WARP接続状態を一覧で把握できる。
- 任意のSaaS・社内エンドポイントへの合成HTTP/Traceroute試験を5〜60分間隔で全端末から自動実行し、地域・ISPごとの劣化を統計的に検知する。
- ユーザーから「重い」と申告があった瞬間にリモートでPCAP・WARP診断ログを採取できる（端末を取り上げる必要がない）。
- ヘルプデスクの「ログを送ってください」ワークフローを撤廃できる。

## 主要機能（What）

- **Fleet Status**：colo別の接続デバイス数、接続状態（Connected / Disconnected / Paused / Connecting）、クライアントモード分布、OS・WARPバージョン分布、CPU・メモリ使用率の時系列を一画面で提示する。
- **Synthetic Application Monitoring (Tests)**：WARP配下の端末から定期的にHTTPまたはTracerouteを実行する合成監視。
  - **HTTP Test**：5〜60分間隔。Resource fetch time / Server response time / DNS response time / HTTPステータスを測定。公開URL・プライベートホスト名（local domain fallback要登録）どちらも対象。
  - **Traceroute Test**：5〜60分間隔。RTT・Packet loss・Hop数・Hop毎のIP/応答時間/ロス率・Availabilityを測定。
- **DEX Rules**：どのユーザー・グループ・端末で各テストを実行するかをポリシーで指定する（全社一律ではなくセグメント単位の運用が可能）。
- **Remote Captures**：管理者がダッシュボードから対象端末（最大10台同時）を指定し、リモートでPCAP・WARP診断ログを採取する機能。
  - **PCAP**：WARPトンネル外（既定インターフェース）と内側の双方を取得。`capture-default.pcap` / `capture-tunnel.pcap` / `results.json` の3点をWiresharkで解析できる。最大600秒・50MB、Windowsは同時実行不可。
  - **WARP Diagnostic Logs**：直近96時間の診断ログ。任意でSplit Tunnelの全ルートテストを併走可能（その間端末性能に影響あり）。100MB超は自動アップロード不可で手動共有となる。
  - 対応OSは Windows / macOS / Linux（2024.12.492.0以降）。iOS / Android / ChromeOSは非対応。
- **Test History**：合成テストの結果を時系列・端末別・地域別に蓄積。Logpush経由でR2・外部クラウドストレージ・SIEMへ転送可能。既定保持期間は7日。
- **Notifications**：以下3種のアラートを email / webhook / 三者連携 に発報する。
  - Device Connectivity Anomaly（WARP接続のスパイク・ドロップをZ-score ±3.5σで検知）
  - DEX Test Latency（HTTP fetch時間・Traceroute RTTの異常）
  - DEX Test Low Availability（成功率がSLO閾値（例: 98.0%）を割った場合）
  - colo・OS・WARPバージョン・テスト名でフィルタ可能。
- **DEX MCP Server**：DEXのデータをClaudeなどMCP対応エージェントから問い合わせ可能にする統合（最近追加）。
- **EU Customer Metadata Boundary対応**：EUコンプライアンス要件下でも利用できる。

## アーキテクト視点：いつ選ぶか

### 適しているシーン
- WARPを既に全社展開している、または展開予定の組織。DEXは追加課金なしで「ついてくる」性格の機能であり、WARP導入の正当化材料にもなる。
- リモートワーク主体・グローバル分散チームで、ヘルプデスクが「ユーザー宅のネットワーク問題」と「アプリ側問題」を切り分ける材料を欲しがっているケース。
- Cloudflare Access / Gateway / Tunnelで既にZero Trustスタックを統一している環境。DEXはこの3者と同じ管理面（Cloudflare One）に乗るため、サイロが増えない。
- SaaS（Microsoft 365、Salesforce等）の地域別劣化を「実ユーザー視点」で監視したいケース。Cloudflareのcolo網を利用するため、社外SaaSの可用性を社員のロケーション別に観測できる。
- VIP端末（経営層・営業担当）の常時状態監視。

### 適していないシーン
- WARPを導入しない / できない組織。DEXはWARPデバイスから送られるテレメトリで成立しており、エージェントレスでは何も取れない。BYOD で WARP を強制できない場合は別系統（Catchpoint等の合成監視SaaS）を検討する。
- アプリケーション内部のトランザクション・コードレベルのトレースを取りたいケース。これはDatadog APM / New Relic等のAPMの領域であり、DEXは「外形監視＋端末状態」に特化する。
- iOS / Android主体のモバイルワーカー集団で詳細PCAPまで欲しいケース。Remote CapturesのPCAP取得はデスクトップ3OS限定である。
- 1分未満の高頻度監視を要するクリティカル業務系。テスト最小間隔は5分である。

## 競合・代替

| 観点 | Cloudflare DEX | Catchpoint | ThousandEyes (Cisco) | Nexthink | Microsoft Intune Endpoint analytics |
|---|---|---|---|---|---|
| 観測点 | WARP端末＋Cloudflare colo | 専用ノード＋エンドポイントエージェント | 専用エンタープライズエージェント＋Cloud Agent | 端末常駐エージェント＋センサー | Intune配下のWindows/macOS端末 |
| 強み | Zero Trustスタックと同管理面・追加課金軽い | 合成監視の老舗・ノード網が広範 | ネットワークパス可視化が圧倒的・BGPまで追える | 端末DEX全般（アプリ起動失敗・クラッシュまで）・ITSM連携 | Intune標準・Windowsとの親和性 |
| 弱み | WARP前提・APMトレースは持たない | 価格高め・端末側DEXは弱い | 高価・運用が重い | 価格高め・ネットワーク深掘りはThousandEyesに劣る | macOS以外は弱い・Cloudflare系SaaS監視は不得手 |
| 価格帯 | Zero Trustプラン内（Free 50ユーザーまで含む） | エンタープライズ商談 | エンタープライズ商談（高額帯） | エンタープライズ商談 | Intune Suite に同梱 |
| 適合 | Cloudflare One採用組織 | グローバルSaaS事業者 | 大企業のネットワーク部門 | エンドユーザー体験を重視する大企業IT | Microsoft 365中心の中堅企業 |

DEXは「WARPを入れてしまえばタダ同然で得られる端末＋経路の可視化」というポジショニングであり、専門合成監視（Catchpoint / ThousandEyes）の代替というより、Zero Trust導入の副産物として最初に手を伸ばすべき選択肢である。深掘りが必要になった段階で専門ツールを足す、という二段構えが現実的である。

## 料金（Cloudflare Zero Trust 上で WARP デバイスが必要、プラン差）
- **Free**：50ユーザーまでZero Trustの基本機能（Access / Gateway / WARP）が無料。DEXのFleet status・基本的なSynthetic Tests・Remote Capturesも利用可能で、検証・少人数組織であればコストゼロで一通り触れる。
- **Pay-as-you-go (Standard)**：$7/ユーザー/月程度。ユーザー数の制約がなくなり、DEXのテスト本数・履歴量・通知も実運用レベルに広がる。
- **Enterprise / SASE bundle**：DEX MCP・高度なLogpush連携・SLA・EU Customer Metadata Boundary・複数アカウント横断などが上位プランに紐づく。SASEバンドル（Cloudflare One Enterprise）に組み込むのが一般的である。

DEX独立の課金体系は存在せず、「Zero Trustプラン＋WARPデバイスシート」のサブセットとして提供される点が運用上重要である。逆に言えばWARPユーザー数が課金単位そのものになる。

## CLI / IaC 操作例

### Terraform（cloudflare provider v5）
```hcl
resource "cloudflare_zero_trust_dex_test" "salesforce_http" {
  account_id  = var.account_id
  name        = "Salesforce HTTP"
  description = "Salesforce login page reachability from all WARP devices"
  enabled     = true
  interval    = "0h5m0s"
  target_policies = [{
    id      = cloudflare_zero_trust_device_settings_policy.default.id
    default = true
  }]

  data = {
    host   = "https://login.salesforce.com"
    kind   = "http"
    method = "GET"
  }
}

resource "cloudflare_zero_trust_dex_test" "internal_api_traceroute" {
  account_id = var.account_id
  name       = "Internal API Traceroute"
  enabled    = true
  interval   = "0h15m0s"

  data = {
    host = "10.20.30.40"
    kind = "traceroute"
  }
}
```

### 通知（Notification policy）
Notification policy はCloudflareダッシュボード（Notifications）で `DEX Test Latency` / `DEX Test Low Availability` / `Device Connectivity Anomaly` を選び、SLO閾値・対象テスト・配信先（email / webhook / PagerDuty 等）を設定する。Terraformでも `cloudflare_notification_policy` で管理できる。

### Logpush（テスト結果の長期保管）
```hcl
resource "cloudflare_logpush_job" "dex_results" {
  account_id      = var.account_id
  name            = "dex-test-results-to-r2"
  dataset         = "zero_trust_network_sessions"  # 該当データセット名は要確認
  destination_conf = "r2://dex-logs/{DATE}?account-id=${var.account_id}&access-key-id=...&secret-access-key=..."
  enabled         = true
}
```

## 制限・注意点
- **WARP 導入が前提**：DEXはWARPクライアントから送られるテレメトリと、WARP配下で実行される合成テストで成立する。WARP未導入の端末・BYODで非同意の端末は完全に観測対象外となる。
- **テスト最小間隔は5分**：1分未満のリアルタイム監視は不可。クリティカル業務はAPM・外形監視SaaSと併用する。
- **Remote Capturesの制約**：1キャプチャあたり最大600秒・50MB、対応OSはWindows / macOS / Linux（2024.12.492.0以降）のみ、iOS / Android / ChromeOS非対応、Windowsは同時実行不可、サードパーティのキャプチャツールが干渉する場合がある。
- **WARP診断ログ**：直近96時間が対象、100MB超は自動アップロード不可で手動共有が必要。
- **テスト結果の既定保持は7日**：それ以上の長期分析にはLogpush経由でR2・S3・SIEMへ送出する設計が必要となる。
- **アラートのZ-scoreは「直近5分 vs 過去4時間」で計算される**：恒常的な低品質環境ではベースラインが低く張りつき、異常を検知しづらい。SLO型アラートを併用するのが定石である。
- **テスト本数上限・並列度はプラン依存**：大量導入時はCloudflareアカウント担当に上限確認が必須である。
- **プライベートエンドポイントへの試験**：Tunnel経由でCloudflareに引き込まれている、または local domain fallback に登録されているホスト名のみが対象となる。
- **DEX単体ではアプリ内処理時間は測れない**：HTTP testは外形のresource fetch timeまでである。アプリ内のトランザクション分解はAPMで補完する。

## 参考リンク
- DEX 概要：https://developers.cloudflare.com/cloudflare-one/insights/dex/
- Synthetic tests：https://developers.cloudflare.com/cloudflare-one/insights/dex/tests/
- HTTP test：https://developers.cloudflare.com/cloudflare-one/insights/dex/tests/http/
- Traceroute test：https://developers.cloudflare.com/cloudflare-one/insights/dex/tests/traceroute/
- Fleet status：https://developers.cloudflare.com/cloudflare-one/insights/dex/fleet-status/
- Remote captures：https://developers.cloudflare.com/cloudflare-one/insights/dex/remote-captures/
- Notifications：https://developers.cloudflare.com/cloudflare-one/insights/dex/notifications/
- Cloudflare One llms.txt：https://developers.cloudflare.com/cloudflare-one/llms.txt
- Terraform `cloudflare_zero_trust_dex_test`：https://registry.terraform.io/providers/cloudflare/cloudflare/latest/docs

---
参照日: 2026-05-03
