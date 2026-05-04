# Radar

## 一行サマリ
Cloudflareのグローバルネットワーク（Anycast 300+ PoP）と1.1.1.1パブリックDNSリゾルバから観測したトラフィック・攻撃・ルーティング・DNS・メールの集計データを、ダッシュボードとAPIで公開する"インターネットの天気予報"である。

## 解決する課題（Why）
インターネットは単一の事業者が管理する閉じたシステムではなく、AS（自律システム）・IXP・ISP・CDN・パブリッククラウドが緩く連携した分散ネットワークである。「いまブラジルで通信障害が起きているのか」「特定ASからのトラフィックが急減した原因は何か」「IPv6普及率は本当に上がっているのか」「自社サービスのレイテンシ悪化は世界全体の傾向なのか」といった問いに答える一次データは、各事業者の観測スコープに閉じていることが多い。Cloudflare Radarはこれを以下の用途で公開データセットとして利用可能にする。

- グローバルなネットワーク事象（障害・攻撃・ルーティング異常）の早期検知。
- 国・AS・業界別のトラフィック傾向把握による市場分析・競合調査。
- 脅威インテリジェンス（DDoS規模・標的国・攻撃ベクトル分布）の参照。
- IPv6 / HTTP/3 / TLS 1.3 / Post-Quantum暗号などプロトコル普及率の継続観測。
- 学術研究・報道・SLA調査における引用可能な一次ソース。

## 主要機能（What）

### Traffic Trends
HTTPリクエスト・NetFlows（L3/L4トラフィック）を国・AS・デバイス種別・IPバージョン・Botクラス別に時系列で可視化する層である。ベースラインからの逸脱を自動検出し、急増・急減を「Internet weather report」としてダッシュボード上部に表示する。

- 切り口：Country / AS / Device type（Desktop / Mobile / Other）/ IP version / Bot class（Likely Human / Likely Automated / Verified Bot）/ HTTP version。
- 時間粒度：直近1時間〜2年。直近24h・7d・28dが既定の比較窓。
- 用途：特定国でのサービス障害判定、モバイル比率の地域差分析、Bot比率の時間帯変動把握。

### Quality（Internet Quality）
スピードテストツール（speed.cloudflare.com）由来のデータを集計し、回線品質を国・AS別に可視化する層である。Median / p25 / p75のbandwidth・latency・jitter・loaded latency（Bufferbloat指標）を提供する。

- 用途：ISPの品質ランキング、地域別ブロードバンド普及度比較、Bufferbloatの実測分布。

### Security & Attacks
Cloudflareが緩和したL3/L4 DDoSとL7（HTTPアプリケーション層）攻撃を、攻撃元・標的・ベクトル・規模で分解して公開する層である。

- L3/L4：SYN Flood / UDP Flood / DNS Amplification / Mirai系などのベクトル別シェア、Tbps級攻撃のピーク観測。
- L7：Mitigation技法別（WAF / DDoS Managed Rules / IP Reputation / Access Rules）の遮断比率、業界別標的分布。
- Bot分析：Verified Bot（Googlebot等）と未検証Botの比率、Bot vs Humanの時系列。

### Routing（BGP）
インターネット上のBGPルーティング異常を観測する層である。RPKI Valid/Invalid/NotFound比率、BGP Hijack疑いのアナウンス、Prefix起源変更（MOAS: Multi-Origin AS）、AS関連性などをダッシュボード化している。

- 用途：自社AS / 顧客ASのRPKI検証カバレッジ確認、ルートリーク・ハイジャックの早期検知、IXP参加状況の把握。

### DNS（1.1.1.1由来）
Cloudflare Public Resolver（1.1.1.1 / 1.0.0.1）に届いたDNSクエリを匿名化集計したデータセットである。生IPは保持せず、国・ASレベルに匿名化された統計のみを公開する。

- Domain ranking：人気ドメインの世界・国別ランキング（Alexa後継としてCloudflare Domain Rankingが利用される）。
- Top domains by category：Social Media / News / Adult / Gambling 等カテゴリ別Top。
- DNSSEC・DoH（DNS over HTTPS）/ DoT利用率、Query type分布、応答コード比率。

### Internet Outages / Annotations
国・AS単位の通信障害（Internet shutdowns / Cable cut / Power outage / Cyberattack）を、トラフィック急減検出と公開情報の組合せで記録するタイムラインである。Annotationは政府主導のシャットダウン、ケーブル切断、選挙時の遮断などをラベル付けして公開する。

- 用途：報道・政策研究、SLA交渉時の根拠データ、海底ケーブル障害の影響範囲推定。

### Email Routing Stats
Cloudflareが処理したメール（Email Routing経由・受信メール）から、SPF / DKIM / DMARCのpass率、悪性メール比率、送信元国・ASのシェアを公開する層である。

- 用途：DMARC普及度の地域差分析、なりすまし送信元の傾向把握。

### Adoption & End User Experience
プロトコル・技術普及率の継続観測。IPv6 adoption（国・AS別）、HTTP/3 / QUIC、TLS 1.3、Post-Quantum KEM（X25519MLKEM768）の利用比率を時系列で提供する。

- 用途：自社サービスのプロトコル更新計画、業界レポート用のベンチマーク。

### AS data
AS単位のサマリ（トラフィック規模、IPv6カバレッジ、RPKI状況、隣接AS、地理分布）を提供する。AS Lookupとして個別AS番号で詳細を引ける。

### URL Scanner
任意URLの安全性・接続性・配信構成を解析するスタンドアロンツールである。スクリーンショット・DOM・リクエストツリー・SSL証明書・Geo配信・脅威判定までを返す。Radar APIから`/url-scanner/scan`で叩ける。

### Datasets
研究用に公開されているダウンロード可能データセット群。Domain Ranking CSV、AS関連性データ、Outage履歴、IPv6/HTTP普及率時系列など。CC BY-NC 4.0ライセンスで配布される。

### API
すべてのRadarカテゴリは`api.cloudflare.com/client/v4/radar/*`配下のREST APIから取得可能である。Cloudflare APIトークン（Account → Radar → Read）で認証し、無料tierとして全プラン共通で利用できる。

### MCP Server
RadarデータをClaude / 他LLMから直接参照するためのModel Context Protocolサーバーが公式提供されている。`radar.cloudflare.com/mcp`系のエンドポイントをClaude Desktop等に登録すると、自然言語で「日本の直近24時間のHTTPトラフィック傾向」を聞くだけで集計値を返せる。

## アーキテクト視点：いつ選ぶか

### 適しているシーン
- リサーチャー・記者・アナリストが、引用可能な一次データを無料で参照したい用途。CC BY-NC 4.0で論文・記事への引用が許可されている。
- SOC・脅威インテリチームのDDoSベクトル傾向把握、攻撃元AS / 国の補助情報。
- ネットワーク運用者の障害判定（「自社視点で観測した遅延が世界的傾向か、自社網起因か」の切り分け）。
- 製品開発者のプロトコル採用判断（IPv6・HTTP/3・TLS 1.3普及率の継続モニタリング）。
- SLA交渉・キャリア選定時の客観データ提供（特定国・ASの品質ランキング）。
- 経営層向けに「インターネット全体の動向」をダッシュボード化したい広報・経営企画用途。

### 適していないシーン
- 自社サービスのRUM（Real User Monitoring）・APM・固有メトリクス。Radarはあくまでグローバル集計値であり、自社固有のユーザー体験は測れない。Datadog RUM / New Relic / Cloudflare自身のWeb Analytics・Browser Insightsを使う。
- リアルタイム（秒〜分単位）の障害アラート用途。Radarの集計粒度は数分〜時間単位で、即応的なインシデント検知用ではない。
- 商用での再販・有料サービス組込み（CC BY-NC 4.0は非商用ライセンス）。商用利用はCloudflareへの個別問い合わせが必要。
- Cloudflareトラフィックを通らないクローズドネットワーク・特定地域専用網の分析。観測点バイアスから外れる。

## 競合・代替

| 観点 | Cloudflare Radar | Akamai mPulse Reports | Google Internet Stats | IODA | Ookla Speedtest Insights | Wayback Outages | SimilarWeb |
|---|---|---|---|---|---|---|---|
| 出自 | CDN / Anycast網・1.1.1.1 | CDN（Akamai網） | パブリッククラウド・Search | 学術（Georgia Tech） | スピードテスト専業 | アーカイブ非公式 | Web Analytics専業 |
| Traffic | 標準（HTTP / NetFlows） | 一部公開 | 限定公開（透明性レポート） | × | × | × | サイト訪問数推計 |
| Outages | タイムライン・Annotation充実 | 限定 | 一部地域 | 強み（学術研究グレード） | △ | 限定 | × |
| Routing / BGP | RPKI / BGP異常 | × | × | △ | × | × | × |
| Quality | speed.cloudflare.com由来 | × | △ | × | 最強（世界スピードテスト） | × | × |
| DDoS / Attack | L3-L7・ベクトル別 | △（年次レポート中心） | △（透明性レポート） | × | × | × | × |
| API | 全カテゴリ無料tier | 限定 | 限定 | あり（学術用） | 有料 | × | 有料 |
| ライセンス | CC BY-NC 4.0 | 商用 | 商用 | 学術 | 商用 | 非公式 | 商用 |
| 強み | カバー範囲の広さ・無料・更新頻度 | Akamai網からの視点 | Google視点の補助データ | 学術的厳密性・障害DB | 回線速度の標準指標 | アーカイブ性 | マーケ向けWeb指標 |
| 弱み | Cloudflare観測網バイアス | 公開範囲が限定的 | 不定期更新・断片的 | UI簡素・速度なし | DDoS / Routingなし | 構造化されない | ネットワーク層は対象外 |

Radarの差別化は「広いカバレッジ × 無料公開 × API化 × 更新頻度（リアルタイム〜数分遅延）」の4点である。Ooklaは回線速度の業界標準として併用、IODAは障害の学術的精査で併用、というのが実務的な棲み分けになる。

## 料金

- **ダッシュボード**：完全無料・登録不要。`radar.cloudflare.com`に直接アクセスして全カテゴリ閲覧可能。
- **API**：全Cloudflareプラン（Free含む）で利用可能、追加料金なし。Cloudflare APIトークン（Account → Radar → Read権限）で認証する。
- **データライセンス**：CC BY-NC 4.0（クレジット表記必須・非商用）。商用利用や大量データ取得はCloudflare営業に個別相談。
- **Datasetsダウンロード**：無料。Domain Ranking等のCSVは定期更新。
- **MCP Server**：無料。Claude Desktop等のMCPクライアントから利用可能。
- **Rate Limit**：公式ドキュメントで明示されたAPI rate limitはなく、Cloudflare APIの一般的な制限（1300 req/5min前後）に準じる。大量問い合わせはAccount単位で逓減する可能性がある。

## CLI / API 例

### APIトークン作成
ダッシュボード「My Profile → API Tokens → Create Custom Token」で、`Account → Radar → Read`権限のみのトークンを発行する。

### HTTPトラフィック傾向（直近7日・日本）
```bash
curl -s "https://api.cloudflare.com/client/v4/radar/http/timeseries?dateRange=7d&location=JP&format=json" \
  --header "Authorization: Bearer ${RADAR_TOKEN}" | jq '.result.serie_0.timestamps | length'
```

### DNS Top Domains（カテゴリ：News、グローバルTop10）
```bash
curl -s "https://api.cloudflare.com/client/v4/radar/ranking/top?limit=10&date=2026-05-01&domainCategory=News" \
  --header "Authorization: Bearer ${RADAR_TOKEN}" | jq '.result.top_0[]'
```

### IPv6 Adoption（国別ランキング、直近28日）
```bash
curl -s "https://api.cloudflare.com/client/v4/radar/http/summary/ip_version?dateRange=28d&format=json" \
  --header "Authorization: Bearer ${RADAR_TOKEN}" | jq '.result.summary_0'
```

### Internet Outages（直近30日・全世界）
```bash
curl -s "https://api.cloudflare.com/client/v4/radar/annotations/outages?dateRange=30d&format=json" \
  --header "Authorization: Bearer ${RADAR_TOKEN}" | jq '.result.annotations[] | {location, eventType, startDate, endDate}'
```

### L3/L4 DDoS攻撃ベクトル分布
```bash
curl -s "https://api.cloudflare.com/client/v4/radar/attacks/layer3/summary/protocol?dateRange=7d&format=json" \
  --header "Authorization: Bearer ${RADAR_TOKEN}" | jq '.result.summary_0'
```

### URL Scanner（任意URLの安全性スキャン）
```bash
# スキャン投入
curl -s -X POST "https://api.cloudflare.com/client/v4/accounts/${ACCOUNT_ID}/urlscanner/v2/scan" \
  --header "Authorization: Bearer ${RADAR_TOKEN}" \
  --header "Content-Type: application/json" \
  --data '{"url": "https://example.com"}' | jq '.uuid'

# 結果取得
curl -s "https://api.cloudflare.com/client/v4/accounts/${ACCOUNT_ID}/urlscanner/v2/result/${UUID}" \
  --header "Authorization: Bearer ${RADAR_TOKEN}" | jq '.result.task'
```

## 制限・注意点
- **Cloudflare観測点バイアス**：データソースはCloudflareのCDN網と1.1.1.1リゾルバである。Cloudflareを利用していないサイト・ISPの内部トラフィック・中国本土の閉域網などは観測対象外、もしくは過小評価される。グローバル傾向の代理指標として読む必要がある。
- **サンプリング・正規化**：HTTPトラフィックは絶対値ではなく、ベースライン比の相対値（％）で表示されることが多い。ベースライン期間の選択次第で印象が変わるため、APIで生時系列を取って独自に解釈することが推奨される。
- **DNSデータの匿名化**：1.1.1.1のクエリは個人特定可能な形では公開されない。国・AS粒度の集計のみで、特定ユーザーの行動追跡には使えない（仕様上の制約であり、プライバシー保護でもある）。
- **API rate limit**：明示値はないが、Cloudflare API共通の制限（5分あたり1300リクエスト前後）が暗黙に適用される。大量バックフィルは時間を分散するか、Datasetsダウンロードで一括取得する。
- **ライセンス**：CC BY-NC 4.0は非商用限定。商用ダッシュボード・有料SaaSへの組込みは別途契約が必要。Attribution（出典記載）は常に必須。
- **データ遅延**：リアルタイムを謳うが、実際は数分〜数十分のラグがある。SOCのリアルタイム検知用ではなく、傾向分析・事後調査用と捉える。
- **Outage Annotationの粒度**：国レベル・AS レベルの粒度で、都市・建物単位の障害は取れない。政府主導のシャットダウンは公開情報ベースで人手ラベル付けされるため、未公表の遮断は反映が遅れることがある。
- **Domain Ranking**：Alexaの代替として広く使われるが、1.1.1.1のクエリベースであり、CloudflareDNSを使わないユーザー層（中国本土・特定企業ネットワーク）の嗜好は反映されにくい。

## 参考リンク
- Cloudflare Radar（ダッシュボード）：https://radar.cloudflare.com/
- Radar Developer Docs：https://developers.cloudflare.com/radar/
- Radar API Reference：https://developers.cloudflare.com/api/operations/radar-get-http-timeseries
- Radar 初回API リクエスト：https://developers.cloudflare.com/radar/get-started/first-request/
- Radar Concepts（Aggregation / Bot classes / Confidence / Normalization）：https://developers.cloudflare.com/radar/concepts/
- Radar Datasets：https://developers.cloudflare.com/radar/investigate/radar-datasets/
- URL Scanner：https://developers.cloudflare.com/radar/investigate/url-scanner/
- Radar MCP Server：https://developers.cloudflare.com/agents/model-context-protocol/
- llms.txt（ドキュメント索引）：https://developers.cloudflare.com/radar/llms.txt
- Cloudflare Domain Ranking：https://radar.cloudflare.com/domains
- Cloudflare Blog（Radar関連）：https://blog.cloudflare.com/tag/cloudflare-radar/

---
参照日: 2026-05-04
