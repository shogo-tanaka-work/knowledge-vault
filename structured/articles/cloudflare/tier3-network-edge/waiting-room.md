# Waiting Room

## 一行サマリ
オリジンが捌ける同時セッション数を超えて押し寄せたトラフィックをCloudflareエッジ側のバーチャル待機室に滞留させ、FIFO / Randomで順次解放することでサーバー過負荷と機会損失を同時に回避する仮想行列サービスである。

## 解決する課題（Why）
チケット販売、ECのフラッシュセール、新製品ローンチ、ワクチン予約、人気ゲームのアカウント登録のような「特定時刻に需要がスパイクする」イベントは、オートスケールでもDB / 在庫 / 決済APIまで拡張しきれず、原則としてどこかでオリジンが折れる。折れた瞬間に全ユーザーが5xxを踏み、CSへの問い合わせが洪水化し、ブランド毀損とリピート機会損失が積み上がる。Waiting Roomはこれをエッジで吸収する形で解決する。

- オリジンが安全に処理できる同時セッション数の上限を宣言し、超過分はエッジで「順番待ち」させる。
- 待機ユーザーには進捗表示付きのカスタムページを返すため、5xxやタイムアウトに比べて離脱率が下がる。
- セール開始前のプレキュー（pre-queue）でアクセス解禁時刻に押し寄せる瞬間最大値を平準化する。
- Bot / 自動化スクリプトに対する事実上のレート制限としても機能する。
- オリジン側のスケーリングコストを過大に積まなくても、ピーク時の体験品質を担保できる。

## 主要機能（What）

### Waiting Room と Waiting Room Rule
Zone単位で「対象とするhost / pathの組」を定義したものがWaiting Roomで、その上に「この条件のリクエストは待機室をバイパスする」ルール（Bypass Rule）や「この期間だけ別パラメータで動かす」イベントを重ねる構造になっている。Waiting Room自体は自動的にCloudflare CDNの後段に挿入されるため、対象のDNSレコードはProxied（オレンジ雲）が前提となる。

### Active users と New users per minute
待機室の挙動を決める二大パラメータである。

- **Total active users**：ルート上で同時に「アクティブ」と見なせるセッション数の上限。`session_duration`（分）非アクティブだったセッションは枠を解放する。オリジンが安全に処理できる同時セッション数を入れる。
- **New users per minute**：1分間あたりに新規でルートへ通すユーザー数の目標値。アクティブ枠が空いていてもこの蛇口で流入を絞れる。
- 計算は各データセンターのローカル予算とグローバル予算の二層で行われ、急激なスパイク時はグローバル伝播に約2分かかるためオーバーシュートが発生し得る。閾値はオリジン許容量の8〜9割で設定するのが安全である。

### Queueing Method（4種類）
キューから誰を先に通すかのアルゴリズム。Advanced Waiting Room（Enterprise add-on）でのみ全種類選択でき、Businessは事実上FIFO相当である。

- **FIFO (First In First Out)**：到着順。最も公平で説明責任が立てやすく、一般的なECセール・チケット販売の第一選択。
- **Random**：キュー内からランダムに選出。「9:00開始の抽選販売で、5分前から並んでも有利にしない」ような体験を作るときに、`shuffle_at_event_start`と組合せて使う。
- **Passthrough**：通常時はキューイングせず通すが、イベント期間中など条件下でのみ制限する切り替え型。
- **Reject**：超過分を待機させずに即拒否（カスタムRejectページを返す）。メンテナンス・営業時間外・席数完全固定型イベントで使う。

### Event Scheduling
セール・抽選などの時刻が事前に分かっているイベント向けに、`event_start_time` / `event_end_time` / `prequeue_start_time` / イベント中だけ書き換える各種パラメータを設定できる。プレキューに入ったユーザーは開始時刻まで「もうすぐ開始します」ページに留まり、開始時刻にRandomシャッフルで一斉に並び替えるとフェアな抽選が成立する。

### Custom Waiting Room Page
待機ページのHTMLをMustacheテンプレートで自作できる。Advanced Waiting Roomが必要。標準で使える主な変数は以下。

- `{{waitTime}}` / `{{waitTimeFormatted}}`：推定待ち時間。
- `{{queueIsFull}}` / `{{queueAll}}`：キュー全埋め / 全員キュー中の状態フラグ。
- `{{refreshIntervalSeconds}}`：自動リロード間隔（既定20秒）。
- ブランド統一・多言語化・アナリティクスタグ埋め込みなど、5xxよりはるかにマシなUXに仕立て上げる。

### Bypass Rules
特定パスや国、IPからのトラフィックを待機室の対象外にするルール。Ruleset Engineの式で書く。

- 利用可能フィールド：`http.request.uri.path` / `http.request.uri.path_extensions` / `http.request.method` / `http.host` / `http.cookie` / `http.request.country` / `ip.src` など。
- 利用不可：`cf.threat_score` / `cf.bot_management.*` / HTTPレスポンス側フィールド（待機判定はリクエスト時点で行うため）。
- 例：`/api/health`や静的アセット（`.js` / `.css` / `.png`）は待機室を通さず素通りさせるのが運用上の定石。

### Mobile App API（JSON Response）
ネイティブアプリから待機室を利用する場合、`json_response_enabled: true`にしてリクエスト時に`Accept: application/json`を付けると、待機ページHTMLの代わりに以下のJSONが返る。アプリ側でネイティブUIを描画でき、HTMLレンダリングを挟まないモバイル決済フローでも使える。

```json
{
  "cfWaitingRoom": {
    "inWaitingRoom": true,
    "waitTime": 10,
    "queueAll": false,
    "queueingMethod": "fifo",
    "refreshIntervalSeconds": 20
  }
}
```

### Queueing All Visitors mode
`queue_all: true`にすると、対象ルートに来た全リクエストを問答無用でキューに送る。負荷試験前のリハーサル・新製品の事前登録ページ・「準備中」を見せたい本番直前など、全ユーザーをまずプールしてから順次通したいケースで使う。

## アーキテクト視点：いつ選ぶか

### 適しているシーン
- 開始時刻が決まっているスパイク型イベント（チケット・コンサート・ECセール・限定ドロップ）の運営。
- オリジンの最大同時処理数（DB接続・在庫API・決済プロバイダのレート上限）が事前に見積もれる業務。
- すでにCloudflare CDNにDNSをProxiedで載せていて、Waiting Roomを挿入するだけで保護できる構成。
- 「5xxは出したくないが、オリジンを過剰スケーリングするコストもかけたくない」というSREの中庸要件。
- ボット・スクレイピング対策として「人間の行列に並ばせる」フィクションが有効なドメイン。

### 適していないシーン
- スパイクが予測不能で、かつ低レイテンシ（待機UIを挟むこと自体が許されない）が必須なリアルタイム取引・ゲームマッチング。
- DNSをCloudflareにProxyせず、外部CDN・ロードバランサのみで運用している構成。
- そもそも全リクエストをキャッシュ可能な静的配信中心のサイト。CDNキャッシュとオリジンスケールで足りる。
- 同時アクティブセッションの厳密な上限がビジネス上特定できないサービス。閾値の設計ができない。
- BusinessプランしかないがFIFO以外のキューイングや複数ホスト・カスタムページが要件のケース。Enterprise + Advanced add-onを前提に再検討する。

## 競合・代替

| 観点 | Cloudflare Waiting Room | Queue-it | Akamai Visitor Prioritization Cloudlet | AWS Virtual Waiting Room (solution) |
|---|---|---|---|---|
| 提供形態 | CDNエッジに統合（同一プレーン） | SaaS（DNS or JS / Connector挿入型） | Akamai EdgeWorkersベースのCloudlet | AWSリファレンス実装（CloudFront + Lambda + DynamoDB） |
| 導入容易性 | DNSをProxiedにするだけ | Connector or JSタグ追加が必要 | Akamayプロパティに紐付け | CloudFormation展開・運用は自社 |
| キューイング方式 | FIFO / Random / Passthrough / Reject | FIFO / 抽選 / 優先度付きが豊富 | 優先度ベースの通過制御 | FIFO相当（実装次第） |
| カスタムページ | Mustacheテンプレ（Advanced必要） | フル自由 / 多言語テンプレ豊富 | 限定的 | 自前で構築 |
| 抽選・プレキュー | Event + shuffle_at_event_start | 専業として最も成熟 | 限定的 | 自前で構築 |
| Mobile App API | JSON Response標準 | SDK / API提供 | 個別対応 | 自前で構築 |
| 料金感 | Business以上 + Advanced add-on | 高価（チケット業界の定番） | Akamai契約必須 | AWS従量＋運用コスト |
| 強み | エッジ統合・運用がCloudflareに閉じる | 抽選・優先度・分析の専業ノウハウ | Akamai既存資産との親和性 | AWSスタック内で完結 |
| 弱み | キューイング戦略はQueue-itほど多彩でない | 別ベンダー・別契約・別連携が増える | Akamai前提・他社で使えない | 運用責任が自社に残る |

エッジCDNとして既にCloudflareを使っているなら、追加の連携を増やさずに済むWaiting Roomがコスト・運用面で優位である。一方、抽選付きチケット販売やキャパシティが極端に逼迫するメガイベントでは、Queue-itのような専業の機能の細かさが効くケースも多い。

## 料金
- **Business**：基本Waiting Room 1個。FIFOのみ、デフォルトテンプレート、host単一対象。とりあえず保護したいだけならここで足りる。
- **Enterprise**：基本Waiting Room 1個に加え、**Advanced Waiting Room**をadd-onで購入できる。複数ホスト/パス対象、Random / Passthrough / Reject、カスタムテンプレート、Event Scheduling、Mobile App API、複数Waiting Roomの同時稼働が解禁される。価格は同時稼働数（concurrent waiting rooms）ベースで個別見積もり。
- 待機室に「入っている」ユーザーへのリクエストはCloudflare側で吸収されるため、オリジン課金（帯域・ワーカー実行）に影響しないのも実利的なメリットである。

## CLI / API 例

### Waiting Room の作成
```bash
curl "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/waiting_rooms" \
  --request POST \
  --header "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  --json '{
    "name": "shop_waiting_room",
    "host": "shop.example.com",
    "path": "/shop",
    "total_active_users": 300,
    "new_users_per_minute": 200,
    "session_duration": 1,
    "queueing_method": "fifo",
    "json_response_enabled": true,
    "queue_all": false
  }'
```

### Event のスケジュール（プレキュー + Random抽選）
```bash
curl "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/waiting_rooms/$ROOM_ID/events" \
  --request POST \
  --header "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  --json '{
    "name": "flash_sale_2026_05_10",
    "event_start_time": "2026-05-10T11:00:00Z",
    "event_end_time":   "2026-05-10T13:00:00Z",
    "prequeue_start_time": "2026-05-10T10:55:00Z",
    "new_users_per_minute": 500,
    "total_active_users": 800,
    "shuffle_at_event_start": true,
    "queueing_method": "random"
  }'
```

### Bypass Rule（Ruleset Engine 式の例）
```text
# 静的アセットとヘルスチェックは待機室をバイパス
ends_with(http.request.uri.path, ".js")
or ends_with(http.request.uri.path, ".css")
or ends_with(http.request.uri.path, ".png")
or http.request.uri.path eq "/api/health"
```

## 制限・注意点
- 対象ドメインのDNSレコードがCloudflare ProxiedでないとWaiting Roomは動作しない。SaaSドメイン・別CDN前段構成では使えない。
- 訪問者のCookie受け入れが必須である。Cookieを拒否するブラウザ・プライバシーモード・iframe埋め込み（Safari + CHIPS非対応）では二重カウント・誤動作が起こり得る。
- 標準で20秒間隔の自動リロードが行われるため、Rate Limiting RulesやWAFで20秒以内の連続リクエストをブロックしない設計が必要。
- 待機ページ自体は静的・キャッシュ可能だが、待ち時間表示の精度はデータセンターローカル予算とグローバル予算の集約の遅延に依存し、最初の2分程度はオーバーシュートが起こり得る。閾値設定は実オリジン能力の8〜9割で設計する。
- BypassフィールドにBot Managementの判定値（`cf.bot_management.*`）やレスポンス側フィールドは使えない。Bot Managementと併用する場合はWAF / Bot Fight Modeを前段で動かして、待機室はあくまで容量制御に専念させる。
- Custom Page・複数ホスト・FIFO以外のキューイング・Eventは**Advanced Waiting Room（Enterprise add-on）**前提である。Business契約でこれらを要件化すると後で詰む。
- Waiting Roomは「同時セッション制御」であり、不正アクセス対策・在庫整合性保証ではない。決済・在庫の整合性はオリジン側で別途確保する必要がある。

## 参考リンク
- Waiting Room 概要：https://developers.cloudflare.com/waiting-room/
- Queueing Methods：https://developers.cloudflare.com/waiting-room/reference/queueing-methods/
- Customize Waiting Room（Custom Page）：https://developers.cloudflare.com/waiting-room/how-to/customize-waiting-room/
- Bypass Rules：https://developers.cloudflare.com/waiting-room/additional-options/waiting-room-rules/bypass-rules/
- JSON Response（Mobile App API）：https://developers.cloudflare.com/waiting-room/how-to/json-response/
- Plans：https://developers.cloudflare.com/waiting-room/plans/
- Waiting Room API：https://developers.cloudflare.com/waiting-room/reference/waiting-room-api/
- API Reference（waiting_rooms）：https://developers.cloudflare.com/api/resources/waiting_rooms/methods/list/
- Waiting Room llms.txt：https://developers.cloudflare.com/waiting-room/llms.txt

---
参照日: 2026-05-04
