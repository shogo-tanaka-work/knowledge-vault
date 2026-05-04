# Bot Management

## 一行サマリ
ZoneのHTTPリクエスト1本ごとに「人間らしさ」を1〜99のスコアで評価し、スコア・カテゴリ・Verified Bots判定・JA3/JA4フィンガープリント・AIクローラ識別子を変数化してWAFやWorkerから参照させる、Cloudflareエッジ上のボット制御プレーンである。「悪いボットを止める」だけでなく「良いボットは正しく通す」「AIクローラを意図的に管理する」までを同じレイヤで扱う。

## 解決する課題（Why）
Webサイトに到達するトラフィックの相当部分は人間ではない。クレデンシャルスタッフィング、在庫枯渇攻撃（スニーカーボット）、コンテンツスクレイピング、価格情報の自動収集、AI学習用クロール、不正アカウント作成、コメントスパム、決済不正の試行、これらは従来「IPブロック」「User-Agent判定」「CAPTCHA表示」で凌いできたが、いずれも実用限界に達している。

- 住宅プロキシ・モバイルキャリアIP経由の分散ボットはIP評価では止まらない。
- ヘッドレスChromeやPlaywrightは普通のUser-Agentを名乗る。
- CAPTCHAは正規ユーザーのCVRを落とす一方、解読サービスで突破される。
- AI学習クローラ（GPTBot, ClaudeBot, PerplexityBot等）の急増で「サーバ負荷」「コンテンツ無断学習」「自社UXの代替」という新たな論点が生まれた。
- 一方で検索エンジン・監視SaaS・正規連携ボットは通さなければ事業が成立しない。

Cloudflare Bot Managementは、これらをエッジ側でリクエスト単位にスコアリングし、WAF Custom Rule・Rate Limiting・Workersのいずれからも同じ変数として参照できる形に正規化する。

## 主要機能（What）

### Bot Score（cf.bot_management.score）
1〜99の整数で「自動化らしさ」を表現する変数である。1に近いほどボット確実、99に近いほど人間確実。Bot Management（Enterprise）では1〜99の生スコアが、Pro/Business（Super Bot Fight Mode）ではAutomated / Likely Automated / Likely Human / Verified Botのカテゴリ単位で利用できる。

- 1：自動化が確実（既知のヘッドレス・既知の悪性シグネチャ）。
- 2〜29：Likely Automated。スクレイピング・自動化ツールが多い帯。
- 30〜99：Likely Human。日常的なブラウザトラフィック。
- Verified Bot：別フラグ（後述）で表現される正規ボット。

WAFのfilter式で `cf.bot_management.score < 30` のように直接参照でき、Workers KVやLogpushにそのまま流せる。

### 機械学習検出（ML Detection）
1日あたり数千億リクエスト規模の学習データをもとにした主検出エンジンである。HTTPヘッダ構成、TLSハンドシェイクの特徴、セッションを跨いだ挙動、リクエスト間の時間的分布などをまとめてモデルに食わせ、2〜99のスコアを出力する。Cloudflareのネットワーク全体を学習基盤に使えるため、単一ドメインでは見えない攻撃パターンを横断的に学べる点がアーキテクチャ上の最大の強みである。

### ヒューリスティック検出
既知の悪性パターン（古典的なスクレイパーのシグネチャ、明らかに偽装されたUser-Agent、矛盾したヘッダ組み合わせ）を即座に弾くルールベース検出。スコア1の判定は概ねこの層から出る。

### JS Detections
軽量なJavaScriptを応答に注入し、ブラウザ側の挙動・APIサポート状況・自動化フラグ（navigator.webdriver等）を検査する仕組みである。ヘッドレスChrome・Puppeteer・Playwrightといった自動化ブラウザの検出精度を底上げする。プライバシーに配慮した最小限のシグナルのみを収集する設計。

### 異常検出（Anomaly Detection）
Enterpriseで利用できる教師なし学習エンジン。当該ゾーンの過去のトラフィックをベースラインとし、そこからの外れ値を検出する。「業界平均から見たボット」ではなく「あなたのサイトにとって不自然なリクエスト」を識別するレイヤである。

### Super Bot Fight Mode（Pro/Business）
Pro / Businessプラン向けの中間グレード。カテゴリ単位（Definitely Automated / Likely Automated / Verified Bot）でAction（Allow / Block / Managed Challenge）を設定する。WAF Custom Ruleからも参照可能だが、生スコアは取れない。Businessではより細かい設定とJS Detectionsが利用できる。

### Bot Fight Mode（Free）
Freeプラン向けの単一トグル。検知されたボットトラフィックに対してチャレンジを発動する。設定の粒度はなく、特定パスの除外などはできない。導入コストはゼロだが、誤検知が起きた場合の調整余地が乏しいのが現実。

### Verified Bots
Cloudflareが「正規」と認定したボットのリスト。Googlebot, Bingbot, Applebot, Slack Linkチェッカー, Stripe Webhook, Datadog Synthetics, UptimeRobot等を含む。`cf.client.bot` 変数や `cf.verified_bot_category` で識別できる。「全ボットを止めたいが、検索インデックスと監視は通したい」という現実解はこのリストに依存する。新規ボットの登録申請も受け付けている。

### AI Crawl Control / AI Audit
GPTBot, ClaudeBot, PerplexityBot, Google-Extended, CCBot等の「AI学習・推論用クローラ」を独立カテゴリとして可視化・制御する機能。ダッシュボードからワンクリックで「AIクローラを全部ブロック」「特定のクローラのみ許可」が設定でき、robots.txtの管理UIや、サイト所有者向けのToS雛形（AI学習禁止の文言）も同梱される。Bot Managementの中でも近年最も投資されている領域である。

### AI Labyrinth
不正なAIクローラを「無限に生成されるダミーページの迷路」に誘い込み、リソースを浪費させる対抗策。robots.txtを無視するクローラに対する積極的な防御として位置付けられている。検出されたクローラには本物のコンテンツではなく、AI生成のもっともらしい無意味なページが返される。

### JA3 / JA4 フィンガープリント
TLS ClientHelloの構成（バージョン、Cipher Suites、拡張、Elliptic Curves等）から導出される指紋。`cf.bot_management.ja3_hash` / `cf.bot_management.ja4` として変数化されており、特定のボットツールが残す固有のJA4を直接WAFルールでブロックできる。User-Agentが偽装されてもTLSスタックの実装は容易には変えられないため、JA4は「偽装に強い識別子」として実務上極めて有効である。

### Turnstile連携
CAPTCHAの代替プロダクト。ユーザーにパズルを解かせず、ブラウザのテレメトリのみで人間性を判定する。Bot ManagementとTurnstileを組み合わせると、「スコアが微妙な帯（例：20〜40）はTurnstileに通す」「決済・ログイン・登録だけはTurnstile強制」といったCVRに優しい運用が組める。Apple端末向けには Private Access Token (PAT) によるパスワードレスな人間性証明にも対応。

### Bot Analytics
Bot Managementを有効化したゾーンには専用のAnalyticsダッシュボードが付き、リクエストをBot Score別・カテゴリ別・User-Agent別・JA4別に内訳表示できる。WAFルール作成前のチューニング、誤検知調査、AIクローラのトラフィック把握に使う。

## アーキテクト視点：いつ選ぶか

### 適しているシーン
- ECサイト・チケッティング・予約系で在庫枯渇攻撃やスニーカーボットに恒常的に晒されている事業。生スコア＋JA4でターゲットを絞れる。
- 銀行・証券・SaaSログインでクレデンシャルスタッフィングが観測されているサービス。スコアとTurnstile併用で正規ユーザーの摩擦を最小化できる。
- 自社コンテンツの無断AI学習を抑止したいメディア・出版・EdTech・ナレッジSaaS。AI Crawl Control + AI Labyrinthが直接刺さる領域。
- 既にCloudflare WAF / CDNを使っており、ルール記述のために `cf.bot_management.*` 変数が使える状態にしたい組織。
- Bot対策に独自の専用ベンダー（DataDome / HUMAN等）を入れる前に、エッジ標準の機能で十分な打率が出せるかを試したい組織。

### 適していないシーン
- そもそもCloudflare以外のCDN（Akamai / Fastly / CloudFront）が前段で終端しており、Cloudflareにトラフィックが通らない構成。Bot Managementはエッジ通過が前提である。
- 検出後のレスポンスをアプリ側で精緻に分岐させたいが、Workersを使う設計を許容できない場合。WAFのAction（Block / Challenge / Log）だけでは表現力が足りないシーンが必ず出る。
- アプリ自身がBot前提で動く（公開API・RSS・Webhook配信元等）ため「ほぼ全リクエストが自動化」の正常状態にあるサービス。Verified Botリストとカスタムルールの設計コストが先に立つ。
- 「AI学習クローラに対しては自社で課金して通す」といった商業的なボット流量取引（Pay per Crawl的なモデル）を主目的に置くケースは、Cloudflareの新領域プロダクト群（Pay per Crawl等）も含めて別途検討が必要。

## 競合・代替

| 観点 | Cloudflare Bot Management | Akamai Bot Manager Premier | DataDome | HUMAN (旧PerimeterX) | Imperva Advanced Bot Protection | Kasada |
|---|---|---|---|---|---|---|
| デプロイモデル | エッジ統合（CDN/WAFと同居） | エッジ統合（Akamai上） | リバースプロキシ / SDK / コネクタ | リバースプロキシ / SDK | リバースプロキシ / SDK | リバースプロキシ / SDK |
| 検出主軸 | ML + ヒューリスティック + JA4 + JS Detections | ML + Behavioral + デバイス指紋 | ML + サーバ側シグナル中心 | クライアント側JS / SDKの濃いテレメトリ | ML + クライアント側 | クライアントチャレンジ（独自暗号） |
| AIクローラ制御 | AI Crawl Control / AI Labyrinth標準 | 個別ルール対応 | AI bot対応進行中 | 対応中 | 対応中 | 対応中 |
| Verified Bots | 公式リスト + 申請制 | 同等 | 内部リスト | 内部リスト | 内部リスト | 内部リスト |
| CAPTCHA代替 | Turnstile / PAT | 独自Challenge | 独自Challenge | Human Challenge | Imperva Challenge | Cryptographic Challenge |
| ログ / 分析 | Bot Analytics + Logpush | Akamai Analytics | DataDomeダッシュボード | HUMANダッシュボード | Imperva Analytics | Kasadaダッシュボード |
| 価格帯 | Free〜Enterprise（段階あり） | エンタープライズのみ | エンタープライズのみ | エンタープライズのみ | エンタープライズのみ | エンタープライズのみ |
| 強み | エッジ統合・段階導入・AI領域への先行投資 | 大規模ECでの実績・成熟度 | 純血ボット専業の精度 | クライアント側テレメトリの厚み | WAF/DDoSとの統合 | 独自暗号チャレンジの突破困難性 |
| 弱み | 専業ベンダーのSOC運用支援は弱い | 高コスト・Akamai前提 | Cloudflare前段の場合は二重統合 | 同左 | 同左 | 同左 |

専業ベンダーは「ボット対策のSOCサービス」「対攻撃チューニングコンサル」を込みで提供してくる点が差別化になる。Cloudflareは「既にCDN/WAFが入っているなら追加コストと運用が最小」という構造的優位を持つが、専業レベルのアドバイザリは期待しないほうがよい。

## 料金

- **Free（Bot Fight Mode）**：単一トグルでボットチャレンジ。Zoneの全リクエストに一律適用、除外設定はほぼ不可。検証・個人ブログ用途。
- **Pro（Super Bot Fight Mode）**：Definitely Automated / Verified Botに対するAction設定（Allow / Block / Managed Challenge）。WAF Custom Ruleから限定的にカテゴリ参照可。
- **Business（Super Bot Fight Mode + JS Detections）**：Likely Automatedも独立カテゴリで扱える。JS Detectionsが利用可能。WAF Custom Ruleでより柔軟な分岐が書ける。
- **Enterprise（Bot Management for Enterprise）**：1〜99の生スコア、JA3/JA4フィンガープリント、Anomaly Detection、AI Crawl Control / AI Labyrinthのフル機能、Bot Analytics、Logpush、専用サポート。年間契約・要見積もり。

「カテゴリベースで十分か、生スコアと指紋まで必要か」が最大の分岐点である。EC・金融・大規模メディアは原則Enterprise前提、中小Bizサイト・SaaSの初期防衛はSuper Bot Fight Modeで足りるケースが多い。AI Crawl Controlの一部機能はFreeでも提供されているが、フルコントロールはEnterpriseに集約されつつある。

## CLI / API 例

### WAF Custom Rule（Bot Scoreでのブロック例）
ログインエンドポイントで「Bot Score < 30 かつ Verified Botでない」リクエストをManaged Challengeに回す。

```bash
curl -X POST "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/rulesets/phases/http_request_firewall_custom/entrypoint" \
  -H "Authorization: Bearer ${CF_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "rules": [
      {
        "action": "managed_challenge",
        "expression": "(http.request.uri.path eq \"/login\" and cf.bot_management.score lt 30 and not cf.client.bot)",
        "description": "Challenge low-score non-verified bots on login"
      },
      {
        "action": "block",
        "expression": "(cf.bot_management.score eq 1 or cf.bot_management.ja4 in {\"t13d1516h2_8daaf6152771_b186095e22b6\"})",
        "description": "Hard-block definite bots and known-bad JA4"
      }
    ]
  }'
```

### AIクローラの一括ブロック
`cf.bot_management.verified_bot_category` や `cf.verified_bot_category` で `"AI Crawler"` を判定する、もしくはダッシュボードのAI Crawl Controlのトグルで一括設定する。

```
(cf.verified_bot_category eq "AI Crawler") -> block
```

### Terraform（cloudflare provider v5）
```hcl
resource "cloudflare_ruleset" "bot_protection" {
  zone_id     = var.zone_id
  name        = "Bot protection"
  description = "Bot Management driven WAF rules"
  kind        = "zone"
  phase       = "http_request_firewall_custom"

  rules = [
    {
      action      = "managed_challenge"
      expression  = "(http.request.uri.path eq \"/login\" and cf.bot_management.score lt 30 and not cf.client.bot)"
      description = "Challenge low-score non-verified bots on login"
      enabled     = true
    },
    {
      action      = "block"
      expression  = "(cf.bot_management.score eq 1)"
      description = "Block definitely automated traffic"
      enabled     = true
    },
    {
      action      = "block"
      expression  = "(cf.verified_bot_category eq \"AI Crawler\")"
      description = "Block all AI crawlers"
      enabled     = true
    }
  ]
}
```

### Workersでのスコア参照
```js
export default {
  async fetch(request) {
    const score = request.cf?.botManagement?.score ?? 99;
    const ja4   = request.cf?.botManagement?.ja4;
    if (score < 10) {
      return new Response("forbidden", { status: 403 });
    }
    // 中間スコアはTurnstileのトークン検証を要求
    if (score < 30 && !request.headers.get("cf-turnstile-token")) {
      return Response.redirect("https://example.com/verify", 302);
    }
    return fetch(request);
  }
};
```

## 制限・注意点
- 1〜99の生スコア、JA3/JA4、Anomaly Detection、AI Labyrinthのフル機能はEnterprise（Bot Management for Enterprise）限定。Pro/Businessはカテゴリ判定どまりである点を最初に握っておく。
- Bot ScoreはCloudflareをトラフィックが通過する前提で算出される。Cloudflareがオリジン直前のリバースプロキシではなく、別CDNが前段にある構成では多くのシグナルが取れない。
- JS Detectionsはレスポンスへのスクリプト注入を伴う。SPA・厳格なCSP・PWAでのCSPホワイトリスト調整が必要なケースがある。
- Verified Botリストへの追加は申請制で即時ではない。自社の連携ボットがブロックされる事故を避けるため、内部・取引先のBotは事前にIPリストでAllowする運用と併用するのが安全である。
- Turnstileを多用しすぎると正規ユーザーのCVRに悪影響が出る。「スコア低帯のみ」「機微エンドポイントのみ」に絞る設計が原則。
- Bot ScoreベースのブロックはWAFログには残るが、原因調査にはBot AnalyticsとLogpush（Enterprise）の両方が必要になる。Standard以下のログ保持では事後検証が厳しい。
- AI Labyrinthはクローラのリソースを浪費させる対抗策である一方、自社のCDN転送量・Workers実行コストにも跳ねる可能性がある。導入時はコストモデルを確認する。
- robots.txt遵守の善意のクローラと、無視する悪意のクローラを同列に扱わない設計が必要。AI Crawl Controlのカテゴリ別設定で分岐を明示する。
- WAF / Rate Limiting / Bot Management / Turnstile / Workersは同じ `cf.*` 変数で連携できるが、評価順序（Phase）を理解せずにルールを足すと意図と異なる順で発火する。Rulesetのphaseとprecedenceは設計時に明文化する。

## 参考リンク
- Cloudflare Bot Management 公式ドキュメント：https://developers.cloudflare.com/bots/
- Bot Score の概念：https://developers.cloudflare.com/bots/concepts/bot-score/
- Super Bot Fight Mode：https://developers.cloudflare.com/bots/get-started/super-bot-fight-mode/
- Bot Management for Enterprise：https://developers.cloudflare.com/bots/get-started/bot-management/
- AI Crawl Control / AI bots：https://developers.cloudflare.com/bots/concepts/bot/#ai-bots
- AI Labyrinth：https://blog.cloudflare.com/ai-labyrinth/
- Verified Bots：https://developers.cloudflare.com/bots/concepts/bot/verified-bots/
- JA3/JA4 フィンガープリント：https://developers.cloudflare.com/bots/concepts/ja3-ja4-fingerprint/
- Turnstile：https://developers.cloudflare.com/turnstile/
- Bot Management 製品ページ：https://www.cloudflare.com/application-services/products/bot-management/

---
参照日: 2026-05-04
