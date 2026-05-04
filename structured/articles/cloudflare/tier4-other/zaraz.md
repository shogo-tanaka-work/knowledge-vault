# Zaraz

## 一行サマリ
GA4・Meta Pixel・TikTok Pixelなどの3rd-partyタグをブラウザではなくCloudflareエッジ（Worker）側で実行することで、ページのJavaScriptバンドルとサードパーティドメインへのリクエストを排し、Core Web Vitalsとプライバシーの両方を改善するサーバーサイド・タグマネージャである。

## 解決する課題（Why）
Google Tag Manager（GTM）に代表される従来型のタグマネージャは、計測タグ・広告ピクセル・チャットボットの増加に応じてブラウザでロードするJSバンドルが肥大化し、結果としてLCP / INP / CLSを悪化させる。さらにサードパーティドメインに対する直接リクエストはAdblockerやITP / ETPで遮断され、計測の歩留まりも年々下がっている。Cloudflare Zarazはこれをエッジ実行モデルで置き換え、以下を解決する。

- GA4 / Meta Pixel / TikTokなどのタグをCloudflare WorkerのCloud側で実行し、ブラウザ側のJSロードを最小化（多くは1ファイル数KBの`zaraz/i.js`のみ）。
- サードパーティドメインへのリクエストを廃し、すべて自ドメイン（`/cdn-cgi/zaraz/...`）経由に集約。Adblocker・ITPの影響を抑え、計測の歩留まりを回復。
- Consent Management Platform（CMP）を標準提供し、GDPR / ePrivacy対応のクッキー同意モーダルを設定UIから生成。
- IPマスキング・ハッシュ化など、サーバーサイド経由ならではのプライバシー処理を集中管理。
- Cloudflare上でホスティングしている場合、追加スクリプト埋め込み不要で自動注入される。

## 主要機能（What）

### Tools Library
Zaraz Dashboardが提供するManaged Component（事前定義されたタグ）のカタログである。GA4 / Google Ads / Meta Pixel / Meta CAPI（Conversions API）/ TikTok Pixel / X (Twitter) / LinkedIn Insight / Microsoft Clarity / HubSpot / Hotjar / Intercom / Crisp など、主要な計測・広告・チャット系ツールがネイティブ対応している。各ツールはダッシュボードのフォームに測定IDやAPIキーを入れるだけで稼働する。

- **Server-side（Conversions API系）対応**：Meta CAPIなど、本来サーバー間通信が必要なツールも、Zarazがサーバー側からEvent送信を行うため別途エンドポイント実装は不要。
- **追加トークン・API Secret管理**：Zarazのツール設定UIでSecretを保管し、ブラウザに露出させない。

### Triggers & Actions
タグが「いつ」「何を」送るかを定義する仕組みである。

- **Triggers**：Page Load / Click / Form Submission / Element Visibility / カスタムイベント（`zaraz.track('event_name', {...})`）など、発火条件を宣言的に設定。
- **Actions**：Pageview / Event / E-commerce の3種に分類。各ツールごとにどのTriggerでどのActionを送るかをマトリクス的に紐付ける。
- **Auto-actions**：GA4等の主要ツールではTrigger設定なしでもPageviewを自動送信する省力モードを提供。

### Consent API / Consent Management Platform
GDPR・ePrivacy指令に準拠したクッキー同意モーダルをノーコードで生成・運用する仕組みである。

- **Purposes**：「広告計測」「行動分析」「機能向上」のような目的単位で同意を管理し、各ツールをいずれかのPurposeに紐付ける。
- **Consent storage**：ユーザーの同意状態はファーストパーティCookieにJSON形式で保存される（purpose → true / false / undefined のマップ）。
- **`zaraz.consent` API**：`zaraz.consent.set({...})` / `zaraz.consent.get(purposeId)` / `zaraz.showConsentModal()`等で、独自UIから同意状態を制御可能。
- **未同意トリガーのキャッシュ**：同意前に発生したイベントは保留され、同意取得後にまとめて発火する。

### Custom HTML / Managed Components SDK
Tools Libraryに無いタグを独自に持ち込む経路である。

- **Custom HTML Action**：従来のGTMライクに任意のHTML / JSスニペットを発火条件に応じてブラウザ側に注入。
- **Custom Managed Component**：[Managed Components仕様](https://managedcomponents.dev/)に従って実装したコンポーネントをアップロードすれば、ブラウザを経由せずWorker内で完結するタグを自作できる。
- **Workers Integration**：Cloudflare Worker内から`env.ZARAZ.track()`相当のbinding経由でサーバー側イベントを発火させ、Zarazに集約してから各ツールに配信できる。

### Web Analytics 連携
Cloudflare Web Analytics（プライバシーフレンドリーなRUM）とZarazは同じCloudflareプレーンで動作し、Zaraz経由でWeb Analyticsのイベントを送る・両方を同一ドメイン上で配信するといった統合運用が可能。Web Analyticsは`zaraz/...`の同一パスから配信されるため、Adblocker耐性を共有する。

### Privacy 機能
- **IPマスキング**：エッジでクライアントIPを匿名化（最後のオクテットを切り落とす等）してから3rd-partyに転送。
- **Hashing**：Email / 電話番号などのPIIをSHA-256でハッシュ化してからMeta CAPI等へ送信する組み込み変換。
- **Cookie書き換え**：3rd-party Cookieをファーストパーティ化（Zaraz経由で発行）し、ITP / ETPの寿命短縮を回避。

## アーキテクト視点：いつ選ぶか

### 適しているシーン
- すでにCloudflareでZone（DNS / CDN）を運用しており、Webサイトの計測・広告タグをまとめてエッジに寄せたいケース。Workersの追加実装なしで自動注入される。
- Core Web Vitals（特にLCP / INP）を改善する必要があるEC・メディアサイト。GTM由来の数十KB〜数百KBのJSをほぼゼロにできる。
- Meta CAPI / Google Ads Enhanced Conversions など、サーバーサイド計測を本格導入したいが、別途タグサーバー（Stape等）を立てたくない組織。
- GDPR / ePrivacy対応で同意モーダルを早急に整備したいヨーロッパ向けサービス。
- Adblocker耐性を高めて計測歩留まりを上げたいD2C・広告運用の現場。

### 適していないシーン
- Cloudflareをプロキシとして通していない（DNSのみ運用）サイト。`/cdn-cgi/zaraz/`が利用できないため恩恵が薄い。
- GTMで数百のカスタムタグ・トリガー資産を蓄積済みで、移行コストが高い大企業。Tools Library外のタグはCustom HTMLかManaged Component自作が必要。
- 複数CDN・複数クラウド構成で、特定ベンダーへのタグ集約を避けたい組織。
- Tealium iQ / Segment レベルのCDP的データルーティング・大規模オーディエンス管理が要件の組織。Zarazはタグマネージャ寄りで、CDPフル機能は持たない。

## 競合・代替

| 観点 | Cloudflare Zaraz | Google Tag Manager | Segment (Twilio) | RudderStack | Tealium iQ | Snowplow |
|---|---|---|---|---|---|---|
| 出自 | エッジWorker型タグマネージャ | クライアントサイドTM標準 | CDP / イベントルーティング | OSS版Segment | エンタープライズTM / CDP | OSS Behavioral Data Platform |
| 実行場所 | Cloudflare Edge（Worker） | ブラウザ（GTM Server-side別） | サーバー（マネージド） | サーバー（OSS / Cloud） | ブラウザ + Server-side | 自前収集パイプライン |
| ブラウザJS負荷 | 極小（数KB） | 大（数十〜数百KB） | 中（analytics.js） | 中 | 中〜大 | 中 |
| Consent管理 | 標準同梱（CMP） | Consent Mode連携 | 別CMP前提 | 別CMP前提 | Tealium ConsentManager | 別CMP前提 |
| 料金最低帯 | Free（月100K events） | Free | Free（1K MTU） | Free（OSS）/ Cloud有料 | 要見積もり | OSS無料 / SaaSは有料 |
| 強み | エッジ統合・自動注入・CWV改善 | 普及度・ナレッジ量 | 統合先の多さ・CDPライク | OSSで自社ホスト可 | エンタープライズの成熟度 | 生データオーナーシップ |
| 弱み | Tools Library外は自作必要 | バンドル肥大・Adblock影響 | コスト急増（MTU課金） | 運用負荷（OSS自前） | 高コスト・複雑 | 実装・運用の重さ |

ZarazはGTMの「ブラウザJS実行」「Adblockに弱い」という弱点を構造的に解消する点で独自である。一方、Segment / RudderStack / Snowplowが担う「複数SaaSへのイベントFan-out」「データウェアハウスへの永続化」のレイヤとは目的が異なるため、CDP的用途では併用設計になることが多い。

## 料金

- **Free**：月10万events（Cloudflareアカウントあたり）まで無料。Tools Library・Triggers・Consent管理・Auto-actionsを含む基本機能は全て利用可能。
- **Pro / Business（Workers Paid同様の従量帯）**：月100万events以上の規模で、超過分は$0.50 / 100K events 程度の従量課金（最新の単価はダッシュボードのBilling表示を参照）。Custom Managed ComponentやWorkers Bindingを本格活用するなら本帯以上が前提。
- **Enterprise**：月数千万events〜のスケール、契約単位のEvent単価交渉、専用サポート、SLA、Audit Logの長期保管。大規模ECや広告主はここで設計する。

events数の数え方は「ZarazがTrigger経由で発火したAction1件＝1event」が基本である。Pageviewの自動取得もevent数に算入されるため、`zaraz.track()`を細かく呼びすぎると無料枠を早く消費する点に注意する。最新の上限・単価はCloudflareダッシュボードの`Zaraz → Settings → Billing`で実数を必ず確認すること。

## CLI / API 例

### 設定の取得（REST API）
ZarazにはCloud APIが用意されており、ダッシュボード設定をJSONとしてエクスポート・インポートできる。CI／環境間移送に有用。

```bash
# ZoneのZaraz設定（Tools / Triggers / Actions）を取得
curl -s -H "Authorization: Bearer $CF_API_TOKEN" \
  "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/settings/zaraz/config" \
  | jq .

# 設定を別環境（staging→prod）に流し込み
curl -s -X PUT \
  -H "Authorization: Bearer $CF_API_TOKEN" \
  -H "Content-Type: application/json" \
  --data @zaraz-config.json \
  "https://api.cloudflare.com/client/v4/zones/$PROD_ZONE_ID/settings/zaraz/config"
```

### ブラウザからのEvent発火
```html
<script>
  // カスタムイベント
  zaraz.track('signup_completed', { plan: 'pro', amount: 29 });

  // ユーザー属性のセット（Eコマースでの顧客紐付け）
  zaraz.set('user_id', 'u_12345');

  // E-commerce専用アクション
  zaraz.ecommerce('Order Completed', {
    order_id: 'o_98765',
    total: 12800,
    products: [{ sku: 'SKU-1', price: 6400, quantity: 2 }],
  });

  // 同意モーダルを再表示（フッタの「Cookie設定」リンクから呼ぶ等）
  zaraz.showConsentModal();
</script>
```

### Worker から zaraz.track()（Workers Integration）
```ts
// wrangler.toml で zaraz binding を有効化していれば、Worker側からも発火可能
export default {
  async fetch(req: Request, env: Env) {
    // 例：A/B振り分け結果を計測
    await env.ZARAZ.track('experiment_assigned', {
      experiment: 'pricing-v2',
      variant: 'B',
    });
    return new Response('ok');
  },
};
```

### Consent状態の取得
```js
// Purpose IDは Zaraz Dashboard で確認できる
const analyticsConsent = zaraz.consent.get('analytics');
if (analyticsConsent === true) {
  // 同意済みの場合のみ独自計測を追加発火
  zaraz.track('extra_analytics_event', {});
}
```

## 制限・注意点
- 月間event数の上限はプラン依存であり、`zaraz.track()`を細かく呼びすぎると無料枠（10万/月）を即座に消費する。重要イベントに絞って設計するのが原則。
- Tools Libraryに無いタグはCustom HTMLかCustom Managed Componentで持ち込む必要があり、後者は[Managed Components仕様](https://managedcomponents.dev/)の理解が前提。Custom HTMLを多用するとサーバーサイド実行の利点が薄れる。
- Auto-injectが有効でもCloudflareプロキシを経由しないドメイン（`gray cloud`）では`/cdn-cgi/zaraz/i.js`が配信されない。マルチサブドメイン構成では各Zoneでプロキシ設定を確認する。
- サーバーサイド実行ゆえに、リアルタイム性を要求する一部の広告タグ（クリック単位の即時応答が必要な系）では数十〜数百msのエッジ往復遅延がボトルネックになることがある。Conversion計測のような非同期用途が本来の対象。
- Consent未取得状態のイベントはキャッシュされて同意後に一括送信されるが、ユーザーが拒否を選んだ場合は破棄される。Adverse Selection的に「決して送られないevent」が常に発生する点は、レポート設計時に考慮する。
- Audit / 詳細な実行ログはダッシュボード保持期間に依存。長期分析が要件ならLogpush（Enterprise）かWeb Analytics / Workers Analytics Engineへの自前出力を検討する。
- IPマスキングやHashingは個別ツールごとの設定であり、デフォルトで全ツールに自動適用されるわけではない。プライバシー要件があるなら各タグ単位で明示的に有効化する。

## 参考リンク
- Zaraz Overview：https://developers.cloudflare.com/zaraz/
- Get started：https://developers.cloudflare.com/zaraz/get-started/
- Web API（track / set / ecommerce）：https://developers.cloudflare.com/zaraz/web-api/
- Consent management：https://developers.cloudflare.com/zaraz/consent-management/
- Managed Components仕様：https://managedcomponents.dev/
- Cloudflare Zaraz product page：https://www.cloudflare.com/application-services/products/zaraz/
- llms.txt（ドキュメント全体インデックス）：https://developers.cloudflare.com/zaraz/llms.txt

---
参照日: 2026-05-04
