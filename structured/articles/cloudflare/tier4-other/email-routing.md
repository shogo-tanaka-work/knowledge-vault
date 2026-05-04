# Email Routing

## 一行サマリ
独自ドメインに届くメールを任意のメールボックスへ転送する受信専用のメール基盤で、MXレコード自動設定・カスタムアドレス・キャッチオール・Email Workersによるコード処理までを無料で提供するCloudflareの軽量メールゲートウェイである。

## 解決する課題（Why）
独自ドメインで `info@` や `support@` を「受けたいだけ」のとき、Google WorkspaceやMicrosoft 365を契約するのは過剰投資である。SES（受信）やPostfixの自前運用は学習コスト・保守負荷が重く、ImprovMXのようなフォワーディング専業SaaSは無料枠に通数制限が付く。Email Routingはこの「受信転送だけ欲しい」というニーズに対し、以下を解決する。

- 独自ドメインの任意エイリアス（`hello@`, `noreply+xxx@` 等）を、既存のGmail / iCloud / Outlookアカウントへ無料で転送。
- MX / SPF / TXTレコードのCloudflare DNS側自動セットアップで、設定ミス起因の不達を回避。
- Catch-all（受信箱全部受け）で、サインアップごとに使い捨てエイリアスを発行する運用が可能。
- Email Workersにより「受信メールをコードで処理して、別アドレスへ転送・拒否・Slack通知」までを単一のWorkerランタイムで完結。
- 個人事業・スタートアップ初期の「メール用にWorkspaceを月額課金するほどではない」フェーズの定石。

## 主要機能（What）

### Address Routing（カスタムアドレス → 宛先アドレス）
受信側の「Custom address」（例：`hello@example.com`）と、転送先の「Destination address」（例：`me@gmail.com`）を1:1または1:Nで紐付けるルールベースの転送機能である。Destination addressは事前にCloudflareから送られる確認メールでVerificationを通す必要があり、未認証の宛先には転送が走らない。

- マッチャ：完全一致（literal）／ Catch-all。
- アクション：転送（forward）／ Worker実行（worker）／ ドロップ（drop）。
- ルール上限：200件、Destination address上限：200件。

### Catch-all
ドメイン全体で「明示ルールにマッチしなかった全アドレス」をまとめて1つの宛先に流す機能である。サービスごとに `service-name@example.com` を発行する使い捨てエイリアス運用に向く。OFFにすると未定義アドレス宛は拒否（bounce）される。

### MX records 自動セットアップ
Email Routingを有効化すると、対象ZoneのMX 3レコード（`route1/2/3.mx.cloudflare.net`）とSPF（`v=spf1 include:_spf.mx.cloudflare.net ~all`）がDNSへ自動投入される。CloudflareをAuthoritative DNSとして使っていることが前提条件。

### Email Workers
受信メールをWorkers Runtime上の `email()` ハンドラで処理する機能である。`message.forward()` / `message.setReject()` / `message.reply()`（Reply-from制約あり）が利用でき、許可リスト・SPAMフィルタ・Slack通知・条件分岐転送などをコードで書ける。

### Verification / Analytics
Destination addressは確認メールでVerifyしないと使えない。受信通数・処理結果（forward / drop / reject）はAnalyticsで可視化される。Cloudflareは転送経路上でメッセージを保存しない（プライバシーファースト設計）。

## アーキテクト視点：いつ選ぶか

### 受信転送のみで十分なシーン
- 個人ドメイン・LP用ドメインで `contact@` `hello@` を受けて、運用者の個人Gmailに集約したいだけのケース。
- Cloudflare DNSを既に使っている組織で、Workspace契約までは要らないサブドメイン用（`status.example.com` の通知メール受け等）。
- サインアップごとに使い捨てエイリアスを発行したいプライバシー重視の個人運用（Catch-all + Workerフィルタ）。
- Webhookライクに「メール受信をトリガーにWorkerを起動したい」サーバーレスメール処理。

### 適していないシーン
- **送信が必要な業務**：Email Routingは受信専用で、SMTP送信機能を一切持たない。送信はResend / SendGrid / Amazon SES / Mailgun 等を別途契約する必要がある。
- **グループウェア要件**：カレンダー・共有ドライブ・会議室予約・複数ユーザーのメールボックス共有が要るならGoogle Workspace / Microsoft 365が正解。
- **メーリングリスト・大量配信**：Email Routingは1通ずつの転送であり、リスト管理（購読・解除・配信状況）は守備範囲外。
- **法的なメール保管要件**：Cloudflareはメッセージを保存しないため、e-discovery・監査要件があるならExchange Online / Google VaultやSESの受信ログ＋S3保管が必要。
- **添付25MiB超を想定する業務**：上限超過は配送失敗となる。

## 競合・代替

| 観点 | Cloudflare Email Routing | ImprovMX | ForwardEmail.net | Google Workspace | Microsoft 365 | Amazon SES（受信） |
|---|---|---|---|---|---|---|
| 主用途 | 受信転送 + Workersコード処理 | 受信転送SaaS | 受信転送SaaS（OSS） | フルメール+SaaS | フルメール+SaaS | 受信SMTPエンドポイント |
| 送信 | 不可 | 別途SMTP Relayあり（有料） | あり（API/SMTP） | あり | あり | あり（送信本職） |
| Catch-all | 標準 | 有料 | 標準 | 可（エイリアス） | 可（エイリアス） | ルールで実装 |
| カスタムロジック | Email Workers（JS/TS） | 限定的 | Webhook / Regex | Apps Script | Power Automate | Lambda |
| メールボックス | なし（転送のみ） | なし | なし | あり | あり | なし（S3保管） |
| 料金 | 無料 | $9〜/月（Premium） | 無料〜$3/月 | $7.20〜/月 | $7.20〜/月 | $0.10/1,000通 + S3 |
| DNS連携 | 自動（Cloudflare DNS） | 手動 | 手動 | 手動（ガイド付き） | 手動（ガイド付き） | 手動 |
| 強み | Workers連携・無料・DNS自動 | UIシンプル・老舗 | OSS・透明性 | グループウェア最強 | Office連携 | AWS統合・ログ保管 |
| 弱み | 送信不可・保管なし | 無料枠が薄い | UI・サポートは弱め | 高コスト | 高コスト | 受信は脇役・要設計 |

Email RoutingはWorkersランタイムとの結合で「受信メール → サーバーレス処理」が書ける点が他社にはない差別化要因である。逆に「送信もしたい」「メールボックスが要る」要件には全く応えないので、SES / Resend / Workspaceとの組み合わせが前提になる。

## 料金
- **無料**：ルール200件・Destination address 200件・Catch-all・MX自動設定・Analyticsまで全機能を無料で利用可能。トラフィック従量課金もなし。
- **Email Workers**：Workers側の料金体系（Free 100k req/day / Standard $5〜）に従う。受信メール1通＝1リクエスト相当。CPU / メモリ上限超過（`EXCEEDED_CPU`）は有料プランへ移行で緩和。

事実上「Cloudflare DNSを使っていれば追加料金なしで導入できる」という点が最大の優位である。

## CLI / API 例

### REST API（Routing Rule 作成）
```bash
# Custom address → Destination address 転送ルール
curl -X POST "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/email/routing/rules" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $CF_API_TOKEN" \
  -d '{
    "name": "hello -> me@gmail.com",
    "enabled": true,
    "matchers": [
      {"type": "literal", "field": "to", "value": "hello@example.com"}
    ],
    "actions": [
      {"type": "forward", "value": ["me@gmail.com"]}
    ]
  }'
```

### REST API（Destination Address 追加 → Verification送信）
```bash
curl -X POST "https://api.cloudflare.com/client/v4/accounts/$ACCOUNT_ID/email/routing/addresses" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $CF_API_TOKEN" \
  -d '{"email": "me@gmail.com"}'
# → Cloudflareから確認メールが届くので、リンクをクリックしてVerify
```

### Email Worker（許可リスト + 転送）
```ts
// wrangler.toml 側で:
//   [[routes]]
//   pattern = "example.com"
//   custom_domain = true
//   ※ Email Routing側で「Email Worker action」として該当Workerをバインド

export default {
  async email(message: ForwardableEmailMessage, env: Env, ctx: ExecutionContext) {
    const allowList = ["partner@trusted.example", "ops@trusted.example"];

    if (!allowList.includes(message.from)) {
      message.setReject("Address not allowed");
      return;
    }

    // 通常転送
    await message.forward("inbox@corp.example");

    // 件名にタグがあればSlackへも通知
    const subject = message.headers.get("subject") ?? "";
    if (subject.includes("[ALERT]")) {
      await fetch(env.SLACK_WEBHOOK, {
        method: "POST",
        body: JSON.stringify({ text: `Mail alert from ${message.from}: ${subject}` }),
      });
    }
  },
};
```

### Wrangler（Email Worker のデプロイ）
```bash
wrangler deploy
# デプロイ後、ダッシュボードの Email → Routing rules で
# Custom address のアクションを「Send to a Worker」にして当該Workerを選択
```

## 制限・注意点
- **送信不可**：Email RoutingはMTA outboundを持たない。Worker内の `message.reply()` は受信メッセージへの応答に限定され、新規メールの起票はできない。任意宛先への送信はResend / SendGrid / Amazon SES / Mailgun を別途構成する。
- **Reply-from制約**：`message.reply()` の `from` はEmail Routingで管理しているCustom addressに限られる。任意のFromで送ることはできない。
- **MailChannels連携の終了**：旧来WorkersからMailChannels無料中継で送信するパターンは2024年に終了済みで、現在の標準解はResendまたはSESである。Email Routingの送信不可点はこの背景もある。
- **メッセージサイズ上限25MiB**：超過分は受信側で配送失敗となる。大容量添付前提のワークフローは別経路を用意する。
- **メッセージは保存しない**：転送経路上の保管は行わない設計のため、配送失敗したメールの再送・サルベージはできない。監査要件があるならWorker内でR2 / S3に明示的に書き出す実装が必要。
- **Drop / Reject時のbounce**：明示ルール非マッチかつCatch-all OFFの場合は送信側にbounce。Workerで `setReject()` を返すと宛先不明として返送される。
- **SPAM・添付**：Cloudflare側で基本的なSPAM判定はあるが、ユーザー側ではSPAMしきい値の調整UIが薄い。重要メールの誤判定対策として、転送先（Gmail等）側のフィルタとの二段構えが現実的。
- **SPF / DKIM / DMARC**：MX切替時にCloudflareがSPFを `include:_spf.mx.cloudflare.net` で自動上書きする。送信用SaaS（SES等）併用時はSPFのincludeを手動で追記しないと送信側DMARCが落ちる。DKIMは送信側SaaSで設定、DMARCポリシーは `p=quarantine` 以上を別途宣言する運用が前提。
- **上限**：ルール200件 / Destination address 200件。大規模なエイリアス運用はCatch-all + Worker側の動的判定で吸収する。
- **Cloudflare DNSが前提**：他社DNSをAuthoritativeにしている場合は利用不可。MX自動設定の対象もCloudflare DNS Zoneに限られる。
- **Email Workersのリソース**：無料プランではCPU / メモリ制限により大きなメールや重い処理で失敗しうる。`EXCEEDED_CPU` が出る場合はWorkers Paidへ。

## 参考リンク
- Email Routing 概要：https://developers.cloudflare.com/email-routing/
- Limits：https://developers.cloudflare.com/email-routing/limits/
- Email Workers：https://developers.cloudflare.com/email-routing/email-workers/
- Email Workers Runtime API：https://developers.cloudflare.com/email-routing/email-workers/runtime-api/
- Routing Rules API：https://developers.cloudflare.com/api/operations/email-routing-routing-rules-list-routing-rules
- Setup（MX / SPF）：https://developers.cloudflare.com/email-routing/setup/email-routing-addresses/
- Cloudflare Email Service（後継ブランド）：https://developers.cloudflare.com/email-service/
- llms.txt：https://developers.cloudflare.com/email-routing/llms.txt

---
参照日: 2026-05-04
