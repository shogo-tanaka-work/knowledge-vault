# Analytics & Logs (Web Analytics / Logpush / Log Explorer / Workers Observability)

## 一行サマリ
Cloudflareエッジを通過したリクエストとアプリ実行のテレメトリを、無料のRUM（Web Analytics）からSIEM転送（Logpush）、Cloudflare内SQL検索（Log Explorer）、Workers専用のログ・トレース（Workers Observability）まで、レイヤごとに使い分けて観測するための一連の製品群である。

## 解決する課題（Why）
CDN・WAF・Workersに業務トラフィックを通すと、ボトルネックや攻撃の痕跡はCloudflare側にしか残らない。一方でアプリ側のAPMやSIEMにそのデータを取り込めなければ、インシデント調査時に「Cloudflareでは止まったが、その先で何が起きたか」「誰が踏み台になったか」が突合できない。さらにGDPR・改正電気通信事業法以降、サードパーティCookieに依存する従来のWeb分析（GA4等）はそのまま使い続けにくく、エッジ側でCookieを置かずに集計する選択肢が現実的な代替として求められている。Cloudflareの観測系はこれらを以下のように分担して解決する。

- Cookieを置かないRUMでCore Web Vitalsとアクセス数を計測（Web Analytics）。
- HTTPリクエスト・WAFイベント・DNS・Workers Traceなどを連続バッチでR2 / S3 / Datadog / Splunk / Sentinelに転送（Logpush）。
- Cloudflare内に同じログをR2バックエンドで保管し、ダッシュボードからSQL検索（Log Explorer）。
- Workersは`console.log`を書くだけでダッシュボードから検索でき、OTLP互換のトレースも取り出せる（Workers Observability）。
- 全ダッシュボードの数値の出所であるGraphQL Analytics APIを叩いて自前BIに投入。

## 主要機能（What）

### Web Analytics（Cookie-less RUM）
ブラウザ側で動く軽量JS beaconが、Cookie・LocalStorage・Fingerprintingを使わずにPageviews・Visits・Core Web Vitals（LCP / INP / CLS / TTFB / FCP）・Referrer・Country・Device classを集計する仕組みである。GDPR下でCookie同意バナーを出さずに済むのが最大の価値で、全プラン（Freeを含む）で無料で使える。

- **Automatic setup**：Cloudflare上のZoneであれば、ダッシュボードで有効化するだけでHTML応答にbeaconを自動注入する（HTML proxyingが前提）。
- **Manual setup**：Cloudflareプロキシ外のサイト（Vercel / Netlify / S3静的ホスティング等）にも、`<script defer src="https://static.cloudflareinsights.com/beacon.min.js" data-cf-beacon='{"token":"..."}'></script>`を埋めるだけで集計できる。
- **Sites と Token**：計測単位は「Site」で、Siteごとに発行されるTokenでデータが紐付く。1アカウント複数Site可。
- **Edge Analytics（旧Browser Insights）との違い**：Web AnalyticsはRUM（クライアント側beaconベース）。Zone Analyticsはエッジ側で見たHTTPリクエスト全件をサンプリング集計したもので、性質が違う。両者は別物として並列に存在する。
- **エクスポート**：GraphQL Analytics APIから`rumPageloadEventsAdaptiveGroups`等のデータセットで取り出せる。

### Logpush（連続バッチ転送）
Cloudflare上で発生した各種ログを、5分単位前後のバッチで外部ストレージ・SIEMに転送するサービスである。Enterpriseが正規価格帯だが、HTTP requestsデータセットはBusinessでも条件付きで使えるなどデータセットごとに利用可否が異なる。

- **対応データセット**（主なもの）：HTTP requests、Firewall events / WAF、Spectrum events、DNS firewall、Gateway DNS / HTTP / Network、Access requests、Audit logs、Workers Trace events、Workers Invocations、R2 access、Magic IDS / Magic Network Monitoring、CASB findings、Zaraz、DNS logs、Sinkhole、Device Posture results、Page Shield。
- **対応宛先**：R2、S3、GCS、Azure Blob、Datadog、Splunk（HEC）、Microsoft Sentinel、Sumo Logic、New Relic、汎用HTTPS endpoint、S3互換（MinIO等）。
- **フィールド選択 / フィルタ**：データセットごとのフィールド一覧から必要なカラムだけ抽出でき、`filter`式でステータスコード・ホスト・WAFアクション等で絞り込み可能。これでR2・SIEM転送量を抑える。
- **サンプリング**：HTTP requestsはデフォルト全件、`sample`パラメータで0.01〜1.0の比率を指定できる。
- **Logpull（旧REST API）**：HTTP request logsを直近7日間REST取得できた旧API。新規利用は非推奨で、Logpush + R2 / Log Explorerに置き換える設計が公式の推奨。

### Log Explorer（Cloudflare内SQL検索）
LogpushでR2に書き出すのと同じデータを、Cloudflare側で管理されるストレージに保管し、ダッシュボードまたはAPIから**SQL**で検索できるマネージドログ検索サービスである。Splunkを買うほどではないがダッシュボード保持期間（数十時間〜数日）では足りない、という中規模組織のスイートスポット。

- **保持期間**：Enterprise契約で最大2年。
- **料金**：保管$0.10/GB/月（執筆時点）。クエリ料金は別建て、リージョンと実行時間で課金される。
- **対応データセット**：HTTP requests / Firewall events / Access requests / Gateway / WAF / DNS / Page Shield など、Logpush対応データセットのうち順次GA化されている。
- **クエリ例**：`SELECT ClientIP, count(*) FROM http_requests WHERE EdgeResponseStatus = 500 GROUP BY ClientIP ORDER BY 2 DESC LIMIT 50`のようにANSI SQLで書ける。
- **Logpushとの関係**：「Cloudflareに置く（Log Explorer）」と「外に出す（Logpush）」は併用可能。SIEMには既存運用のままLogpushで送りつつ、開発者がアドホックに掘る用途でLog Explorerを引く、というのが実運用パターン。

### Instant Logs（リアルタイム尾引き）
HTTP requestsだけ、ダッシュボードまたは`wrangler`CLI経由でリアルタイムにストリーミング表示できる機能である。本番障害発生時に「いま流れているリクエスト」を直接見るのに使う。Enterprise zone限定。データは保管されない（その場で見るだけ）。

### Workers Observability
Cloudflare Workersに特化した観測スタック。`wrangler.toml`に`[observability] enabled = true`を書くだけで、`console.log`の出力がダッシュボードに集約され、検索・絞り込みができる。

- **Workers Logs**：`console.log` / `console.error`を自動収集。デフォルトで`head_sampling_rate = 1`（全件）、保持期間はFree/Standardともに数日〜7日。`invocation_logs`オプションでリクエスト単位のメタデータも取れる。
- **Tail Workers**：別Workerを「ログ送出先」に指定して、自前で外部システムに転送する仕組み。OTLPエクスポートやSentry連携の中継に使える。
- **`wrangler tail`**：CLIから本番Worker実行ログをリアルタイムストリーム。`--format pretty`でローカルで色付き表示、`--status error`等でフィルタ可。
- **Trace events**：Workers Traceデータセットとして、Worker実行ごとにbindings（KV / R2 / D1 / DO）の呼び出しと処理時間が自動的に記録される。Logpush転送可。
- **OpenTelemetry export**：OTLP互換でHoneycomb / Grafana Cloud / Axiom / Sentry等にトレース・ログを直接送れる。
- **Source maps**：ビルド時に`upload_source_maps = true`を設定するとスタックトレースが圧縮前のソース行に解決される。
- **Query Builder**：エラー率・p99 CPU time・メモリ・サブリクエスト数などを絞り込み・グルーピングして可視化するダッシュボード組み込みクエリツール。

### GraphQL Analytics API
ダッシュボードの全グラフのバックエンドであり、自前BIに数値を持っていく場合の正規ルート。`https://api.cloudflare.com/client/v4/graphql`に対し、Bearer Tokenでクエリを投げる。

- **データセット**：`httpRequestsAdaptiveGroups`、`firewallEventsAdaptive`、`workersInvocationsAdaptive`、`r2OperationsAdaptiveGroups`、`rumPageloadEventsAdaptiveGroups`、`dnsAnalyticsAdaptive`、`gatewayResolverByTimeAdaptiveGroups`等、製品ごとに数十種。
- **Adaptive Sampling**：`Adaptive`が付くデータセットはCloudflareが自動でサンプリング比率を調整しており、レスポンスに`_sampleInterval`が含まれる。集計値はサンプル比率を補正済み。
- **Account / Zone**：`viewer.accounts`配下と`viewer.zones`配下で取れる粒度が異なる。アカウント横断はAccount側、ホスト名・URLパス単位のZone Analytics系はZone側。

## アーキテクト視点：いつ選ぶか

### 適しているシーン
- 「とりあえずGA4の代わりにCookie-lessでPV計測したい」→ Web Analyticsで即終わる（Pro未満でも無料）。
- CDN / WAFを既にCloudflareで運用しており、SIEM（Splunk / Sentinel / Datadog）に流す要件が出てきた → Logpushが自然な接続点。
- ログ保管をAWS / GCPに置きたくない（DXコスト・データ主権）→ R2 + Log ExplorerでCloudflare内に閉じる。
- WorkersでAPI / SaaSバックエンドを構築する組織。`console.log`から本番調査までDXが完結し、別途APMを買わずに回せる。
- 監査要件で「全リクエストを保管」が必要な金融・公共。Logpush（R2 / S3）+ Log Explorerで保持期間を満たす。

### 適していないシーン
- 大規模な行動分析・ファネル・コホート分析が必要なマーケ要件。Web AnalyticsはPV / Vitals中心でAmplitude / Mixpanel / GA4の代替にはならない。
- 既にDatadog / New Relic / Splunkで全アプリのAPMを統一している組織は、Workers Observability単独では運用が分断する。OTLP exportでAPM側に集約する設計が良い。
- HTTP requests以外のリアルタイム尾引き（DNSやFirewall eventsをライブで眺めたい）はInstant Logsが対応していない。
- BusinessプランでLogpush全データセットを使いたいケース。多くはEnterprise必須。

## 競合・代替

| 観点 | Cloudflare（Web Analytics + Logs） | GA4 | Plausible | Fathom | Datadog Logs | Splunk | Grafana Loki | AWS CloudWatch Logs |
|---|---|---|---|---|---|---|---|---|
| 主用途 | エッジ計測 + ログ転送 | マーケ全般 | 軽量Web分析 | 軽量Web分析 | APM中心SIEM | エンタープライズSIEM | OSSログ集約 | AWS統合ログ |
| Cookie | 不要（RUM） | 必要（同意必須） | 不要 | 不要 | NA | NA | NA | NA |
| 価格帯 | 無料〜Enterprise | 無料〜GA360（高） | $9/月〜 | $14/月〜 | $0.10/GB〜 | 高（要見積） | OSS無料〜Cloud | $0.50/GB ingest〜 |
| 保持 | 6ヶ月（RUM）/ 2年（Log Explorer） | 14ヶ月（無料） | 無制限 | 無制限 | 7〜30日標準 | 契約次第 | 自前 | 自由設定 |
| SQL検索 | Log Explorer | BigQuery export | × | × | Log Patterns | SPL | LogQL | Logs Insights |
| エッジ統合 | ◎（自社製品） | ✕ | ✕ | ✕ | ✕ | ✕ | ✕ | ✕ |
| 強み | エッジで取れたものをそのまま | マーケ機能の厚み | 簡潔・倫理的 | 簡潔・倫理的 | APM統合 | エンタープライズ機能 | OSS・コスト | AWS統合 |
| 弱み | 行動分析は弱い | Cookie同意・複雑 | エッジログなし | エッジログなし | Cloudflare固有メトリクスは別経由 | コスト・運用 | スケール運用が重い | クロスクラウド弱い |

Cloudflareの強みは「エッジで止まったリクエストの本物のログをそのまま転送・検索できる」点に尽きる。マーケ分析やアプリAPMの代替ではなく、エッジ側の真実を持って既存の分析基盤に合流させる存在として位置づけるのが現実的。

## 料金

- **Web Analytics**：全プラン無料。Site数・ドメイン数の実質的な制限はなく、保持期間6ヶ月（執筆時点）。Pro以上で詳細なフィルタ・Path単位ドリルダウン精度が改善する程度の差分。
- **Logpush**：基本Enterprise必須。一部データセット（HTTP requests等）はBusinessでも追加課金で使える場合がある。R2に書く場合のR2側コスト（$0.015/GB/月の保管 + Class A/B Operations）が別途かかる。Splunk / Datadog等の宛先側課金は別建て。
- **Log Explorer**：保管 $0.10/GB/月（Enterprise契約）。クエリ実行料金は別途、リージョンと処理データ量に応じて課金。最大2年保持。
- **Workers Observability**：Free / Standard（Paid Workers）に**Workers Logs無料枠**が含まれる（執筆時点で20M logs/月相当）。超過分は$0.60 / 1M logs程度の従量。Logpushで外部に出す場合はEnterprise扱い。Tracesは執筆時点でβ含み、料金体系は順次明示化されている。
- **GraphQL Analytics API**：API利用自体は無料（プランに紐付くデータ範囲・粒度・サンプリングに従う）。

「無料で取れるところ（Web Analytics・Workers Logs・GraphQL API）で要件を満たし、長期保管・SIEM転送が必要になったときだけEnterpriseに上がる」という段階導入が定石。

## CLI / API 例

### Logpush ジョブ作成（HTTP requests → R2）
```bash
# データセットとフィールドはまずDescribeで確認
curl -s "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/logpush/datasets/http_requests/fields" \
  -H "Authorization: Bearer $CF_API_TOKEN" | jq

# ジョブ作成（R2バケットに5xxだけ書く）
curl -X POST "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/logpush/jobs" \
  -H "Authorization: Bearer $CF_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "http-5xx-to-r2",
    "destination_conf": "r2://prod-cf-logs/http/{DATE}?account-id='"$ACCOUNT_ID"'&access-key-id='"$R2_KEY"'&secret-access-key='"$R2_SECRET"'",
    "dataset": "http_requests",
    "logpull_options": "fields=RayID,EdgeStartTimestamp,ClientIP,ClientRequestHost,ClientRequestURI,EdgeResponseStatus&timestamps=rfc3339",
    "filter": "{\"where\":{\"key\":\"EdgeResponseStatus\",\"operator\":\"geq\",\"value\":\"500\"}}",
    "enabled": true
  }'
```

### GraphQL Analytics API（直近1時間の5xx率）
```bash
curl -s https://api.cloudflare.com/client/v4/graphql \
  -H "Authorization: Bearer $CF_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query($zone:String!,$since:Time!,$until:Time!){viewer{zones(filter:{zoneTag:$zone}){httpRequestsAdaptiveGroups(limit:1,filter:{datetime_geq:$since,datetime_leq:$until}){sum{requests} avg{sampleInterval} dimensions{__typename}} http5xx:httpRequestsAdaptiveGroups(limit:1,filter:{datetime_geq:$since,datetime_leq:$until,edgeResponseStatus_geq:500}){sum{requests}}}}}",
    "variables": {"zone":"'"$ZONE_ID"'","since":"2026-05-04T00:00:00Z","until":"2026-05-04T01:00:00Z"}
  }' | jq
```

### Workers ログのライブ尾引き
```bash
# 本番Workerに繋いでリアルタイムログ（5xxのみ・整形）
wrangler tail my-api --format pretty --status error

# observabilityをwrangler.tomlで有効化
cat >> wrangler.toml <<'TOML'
[observability]
enabled = true
head_sampling_rate = 1.0

[observability.logs]
invocation_logs = true
TOML
```

### Log Explorer SQL（ダッシュボードまたはAPI経由）
```sql
-- 直近1時間のホスト別5xx Top 20
SELECT ClientRequestHost AS host, count(*) AS errors
FROM http_requests
WHERE EdgeStartTimestamp > now() - INTERVAL '1' HOUR
  AND EdgeResponseStatus >= 500
GROUP BY host
ORDER BY errors DESC
LIMIT 20;
```

### Web Analytics 手動beacon（Cloudflare外サイトへの埋め込み）
```html
<!-- Token は Web Analytics ダッシュボードから発行 -->
<script defer
  src="https://static.cloudflareinsights.com/beacon.min.js"
  data-cf-beacon='{"token": "YOUR_SITE_TOKEN"}'></script>
```

## 制限・注意点
- **Logpushはプラン依存**：データセットの大半がEnterpriseのみ、HTTP requestsは一部Businessでも可、という不揃いな状態。導入前に必ず`/logpush/datasets`で利用可否を確認する。
- **Log Explorer保持期間とコスト**：最大2年だが、HTTP requests全件をフィルタなしで保管するとTB単位/月になり保管料金が嵩む。`fields`絞り込み・`filter`での減量設計が必須。
- **サンプリング**：ダッシュボードや`*Adaptive*`系GraphQLはトラフィック規模に応じて自動サンプリングされる。`sum.requests`は補正済み数値だが、生ログを必要とする監査用途ではLogpushでサンプル無し転送が必要。
- **Workers Logsの保持と上限**：保持は短期（数日）。長期保管が要るならLogpush（Workers Trace events）でR2に流す前提で設計する。`head_sampling_rate`を下げているとデバッグ時に見たいログが落ちている事故が起きやすい。
- **Web AnalyticsはRUM**：BotやJS無効ブラウザの数は計測されない。Zone Analytics（エッジ集計）と合わせて読むのが正攻法。Bot Managementと組み合わせれば人間トラフィックだけのRUM結果を出せる。
- **PII**：HTTP request logsには`ClientIP`・`ClientRequestURI`・`User-Agent`・`Cookie`等が含まれ、フィールド選択で外さないと個人情報が外部SIEMに出る。GDPR / 個情法対応を前提に最初からフィールドを絞る。
- **Logpullは新規非推奨**：API互換のために残っているが、新規導入はLogpushに統一する。
- **Instant Logsは保管されない**：尾引き専用。後から振り返るならLog Explorer / Logpush + R2を並走させる。
- **GraphQL料金プラン制限**：プランによって取れるデータセット・時間粒度・遡れる期間が違う（FreeはZone analyticsの一部のみ等）。BIに取り込む前にプラン要件を確認する。

## 参考リンク
- Cloudflare Analytics ハブ：https://developers.cloudflare.com/analytics/
- Web Analytics：https://developers.cloudflare.com/web-analytics/
- Logs（Logpush / Instant Logs / Logpull）：https://developers.cloudflare.com/logs/
- Logpush 宛先一覧：https://developers.cloudflare.com/logs/logpush/logpush-job/
- Log Explorer：https://developers.cloudflare.com/log-explorer/
- Workers Observability：https://developers.cloudflare.com/workers/observability/
- Workers Logs：https://developers.cloudflare.com/workers/observability/logs/workers-logs/
- `wrangler tail`：https://developers.cloudflare.com/workers/wrangler/commands/#tail
- GraphQL Analytics API：https://developers.cloudflare.com/analytics/graphql-api/
- Logs llms.txt：https://developers.cloudflare.com/logs/llms.txt
- Analytics llms.txt：https://developers.cloudflare.com/analytics/llms.txt

---
参照日: 2026-05-04
