# Registrar

## 一行サマリ
Cloudflareアカウントで管理するドメインを、レジストリ卸価格＋ICANN手数料の実費（at-cost）だけで登録・更新・移管できる、マークアップなし・WHOIS Privacy標準・DNSSECワンクリックのドメインレジストラである。

## 解決する課題（Why）
従来の主要レジストラ（GoDaddy / Namecheap / お名前.com 等）は、卸価格に独自マークアップを乗せ、WHOIS Privacy・DNSSEC・Registry Lockなどを別料金オプションとして販売するビジネスモデルが定着している。さらに「初年度激安・更新時に通常価格へ跳ね上がる更新トラップ」「自動更新を切るとサイトが落ちる事故」「移管時のトランスファーロック解除や認証コード発行が有料・遅延」といった摩擦が常態化している。Cloudflare Registrarはこれを以下のように整理する。

- レジストリ卸価格＋ICANN手数料（年$0.18）以外のマークアップを取らない。初年度・更新で価格が変わらない。
- WHOIS Privacy（登録者情報の代理表示）を標準提供、追加料金なし。
- DNSSECをダッシュボードからワンクリック有効化、追加料金なし。
- Cloudflare DNS / WAF / Pages / Workersと同一アカウントで完結し、ネームサーバ管理の二重運用が不要。
- 自動更新が標準ON。支払い手段が有効なら更新を逃さない。

ただし「Cloudflare DNSをネームサーバとして使うこと」が前提で、TLDも限定（.jp / .co.jp 等は対象外）であるため、すべてのドメインを集約できるわけではない。

## 主要機能（What）

### At-cost pricing
レジストリ卸価格＋ICANN手数料（gTLDで$0.18/年）のみを請求する仕組みである。Cloudflareは登録手数料・更新手数料を上乗せしない。

- 価格はTLDごとにレジストリ卸価格に連動するため、レジストリ側の値上げで変動する。Cloudflare独自のマークアップ・キャンペーン価格・更新時の値上げは存在しない。
- 「初年度$1で2年目から$20」のような引き込み価格は採用していない。1年目から正規卸価格である。
- 課金は契約しているCloudflareアカウントの支払い手段（クレジットカード / PayPal）に紐づき、ドメイン単独の請求書ではなく月次請求に統合される。

### Domain Transfer（他社からの移管）
他社レジストラからCloudflare Registrarへ移管するフローである。発生作業30分程度、完了まで最大10日（多くは5営業日以内）が目安となる。

- 旧レジストラ側でTransfer Lockを解除し、Auth Code（EPP code / authinfo / transfer code）を発行。
- Cloudflareダッシュボード「Registrar → Transfer Domains」で対象ドメインとAuth Codeを入力。
- 旧レジストラからの確認メール承認、または自動承認（規定期間経過）で移管が完了する。
- ICANN規定により「登録から60日未満のドメイン」「直近60日以内に移管したドメイン」は移管不可。Registrant情報変更直後の60日ロックも同様に適用される。
- Shopify / Wix / Squareなどネームサーバ変更を許可しないプラットフォーム経由の登録は、いったん別レジストラに移管し60日待機してからCloudflareへ、という二段階移管が必要。

### Registry Lock（Custom Domain Protection）
レジストリ階層でドメインをロックし、UIからの変更を一切受け付けないオプションである。「侵害されたCloudflareアカウントからのドメインハイジャック」を防ぐ最後の砦に位置する。

- Enterpriseプラン限定で、高価値ドメインのみが対象。Cloudflareアカウントチームへの個別相談で有効化される。
- 有効化後はネームサーバ変更・コンタクト変更・移管などすべての変更がout-of-band認証（事前に取り決めた手動プロセス）を経由する。ダッシュボードからは操作インターフェース自体が消える。
- 対応TLDは「レジストリがRegistry Lockをサポートしているもの」に限られる。.com / .net / .org など主要gTLDが中心。
- 価格はEnterprise契約に内包。個別見積もり。

### WHOIS Privacy（標準）
登録者情報をWHOIS / RDAP公開情報から代理表示（redaction）する機能である。GoDaddy等で年$10〜$20の追加課金が一般的なオプションを、Cloudflareは無料・標準ONで提供する。

- gTLDではTechnical / Administrative / Registrant連絡先がCloudflareの代理アドレスに置き換わる。
- ccTLDはレジストリ規約により挙動が異なる（.us は法的に開示必須）。
- 法執行・知財侵害の正式なWHOIS開示要請は、CloudflareのWHOIS request窓口経由で対応される。

### Auto-renew
新規登録・移管完了後、自動更新がデフォルトで有効になる。

- 失効リスクの高いドメインを「うっかり期限切れ」で失う事故を防ぐ設計。
- 個別ドメインで明示的にOFFにすると、期限到来でCloudflareは更新しない。
- 支払い手段の有効性確認はアカウント単位で行われ、失敗すると全ドメインの更新が滞る。

### DNSSEC ワンクリック有効化
ダッシュボード「DNS → Settings → DNSSEC」からの操作だけでDSレコードがレジストリ側に登録される。Cloudflare DNSをネームサーバとして使っている前提なので、KSK/ZSK鍵管理はCloudflare側に任せる形となる。

### Registrar API
ドメイン検索・空き確認・新規登録までをCloudflare API v4経由で実行できる（2026-05時点でβ）。

- 認証はBearerトークン（`CLOUDFLARE_API_TOKEN`）。
- 対応エンドポイント：`/registrar/domain-search`、`/registrar/domain-check`、`/registrar/registrations`。
- 未対応：更新・移管・コンタクト更新・ロック操作。これらは引き続きダッシュボード操作。

### 対応TLD
公式に「400以上のTLDをサポート」と表記されている。主要gTLD（.com / .net / .org / .io / .dev / .app / .ai 等）と一部ccTLD（.us / .uk / .co / .me / .tv 等）が中心。

- IDN（国際化ドメイン名・アクセント記号や非ラテン文字を含むドメイン）は非対応。
- 一部ccTLDはレジストリ規約により新規登録不可・移管のみ可能、または逆のパターンがある。
- .us は米国居住・法人要件（Nexus要件）がある。

## アーキテクト視点：いつ選ぶか

### 適しているシーン
- Cloudflare DNS / Pages / Workers / Zero Trustをすでに使っており、ドメイン管理だけ別レジストラに残っている組織。ネームサーバ運用が一本化される。
- WHOIS Privacy・DNSSEC・自動更新を「全ドメインで強制」したい運用。標準ONなので運用コストが下がる。
- 個人開発者・スタートアップで、複数の.dev / .io / .ai ドメインを長期保有したい場合。マークアップなしの効果が累積する。
- 移管トラップ・更新時の価格跳ね上がりを排除したい中規模Web事業者。
- IaC（Terraform / Pulumi）でDNSとアプリを管理しており、ドメイン契約だけが手動運用になっているケース。少なくとも更新・自動更新の運用負荷は消える。

### 適していないシーン
- .jp / .co.jp / .cn / .de など Cloudflare Registrarが対応していないTLDを主軸に運用している組織。お名前.com / Gandi / Namecheap等の併用が必須。
- ドメインを大量バルク登録（100ドメイン超を一括取得・転売）するドメイナーやSEOアフィリエイト運用。Cloudflareは投機的な大量登録を想定しておらず、API側にも更新・移管エンドポイントが揃っていない。
- 登録者情報をどうしても自社管理のWHOIS代理サービス（プロキシ業者）に固定したい場合。Cloudflareの代理表示は変更できない。
- Cloudflare DNS以外のネームサーバ（Route53 / NS1 / Akamai 等）を使い続けたいケース。Cloudflare Registrar はCloudflare DNSとセットでの利用が前提。
- IDN・特殊TLD・新興ccTLDを主に扱うケース。

## 競合・代替

| 観点 | Cloudflare Registrar | AWS Route 53 Domains | Squarespace Domains（旧Google Domains） | Namecheap | GoDaddy | Gandi | Porkbun |
|---|---|---|---|---|---|---|---|
| 価格モデル | At-cost（卸＋ICANN手数料のみ） | 卸近辺＋小マークアップ | 一律価格・WHOIS Privacy標準 | 初年度安・更新時上昇 | 初年度安・更新時大幅上昇 | 中価格帯・固定 | 低価格帯・透明性高い |
| WHOIS Privacy | 標準・無料 | 標準・無料 | 標準・無料 | 標準（Free WhoisGuard） | 有料オプション中心 | 標準・無料 | 標準・無料 |
| DNSSEC | ワンクリック・無料 | 対応・無料 | 対応 | 対応 | 対応 | 対応 | 対応 |
| Registry Lock | Enterpriseのみ・無料 | 非提供 | 非提供 | 非提供 | 有料 | 一部TLDで有料 | 非提供 |
| 対応TLD数 | 400+（主要gTLD中心、.jp等不可） | 多数（.jp含む） | Squarespace移行で限定的 | 500+ | 500+ | 750+（最広） | 500+ |
| バルク登録 | 不向き | 可 | 可 | 可（バルク機能あり） | 可 | 可 | 可 |
| API成熟度 | 検索・登録のみβ | 安定・更新まで対応 | 限定 | 限定 | 限定 | 安定 | 安定 |
| 強み | マークアップなし・Cloudflare統合 | AWSアカウント統合・自動化 | UI完成度・移行先がSquarespace | 価格・サポート・UI | TLD網羅性・サポート | TLD網羅性・倫理運営 | 価格・透明性 |
| 弱み | 対応TLD限定・DNS固定 | UI古い・価格はat-costではない | Squarespace移行で先行き不透明 | 更新トラップ | 更新時の値上がり・営業電話 | UIが質素 | サポート規模 |

Cloudflare Registrarは「価格透明性 × Cloudflareプラットフォーム統合」に最適化されており、競合より一歩抜けている。ただし対応TLDと運用前提（DNSをCloudflareに寄せる）に強い縛りがあるため、全ドメインを集約するのは現実には難しい。.jpを含むポートフォリオは Gandi / Route53 / お名前.com との併用が現実解。

## 料金

- **登録費用**：レジストリ卸価格＋ICANN手数料（gTLDで$0.18/年）。マークアップ・登録手数料・サービス手数料はゼロ。
- **更新費用**：登録費用と同額。初年度割引・更新時値上げは存在しない。
- **移管費用**：移管時に1年分の更新が自動で発生し、その費用のみ請求される（ICANN仕様）。Cloudflare側の移管手数料はゼロ。
- **WHOIS Privacy**：無料・標準。
- **DNSSEC**：無料・標準。
- **Registry Lock（Custom Domain Protection）**：Enterprise契約に内包、個別見積もり。
- **Cloudflareアカウントプラン**：Free / Pro / Business / EnterpriseいずれでもRegistrar機能は使える。プランを上げてもRegistrar価格には影響しない。

参考価格（2026-05時点、レジストリ卸変動あり）：.com $9.77 / 年、.net $11.61 / 年、.io $34.80 / 年、.dev $12.18 / 年、.app $13.59 / 年、.ai $80前後 / 年。

## CLI / API 例

### Cloudflare API（v4）でドメイン検索・空き確認・登録
```bash
# 環境変数
export CLOUDFLARE_API_TOKEN="..."
export ACCOUNT_ID="..."

# キーワードからドメイン候補を検索
curl --request GET \
  --url "https://api.cloudflare.com/client/v4/accounts/$ACCOUNT_ID/registrar/domain-search?q=acme%20corp&limit=5" \
  --header "Authorization: Bearer $CLOUDFLARE_API_TOKEN"

# 個別ドメインの空き・価格を確認
curl --request POST \
  --url "https://api.cloudflare.com/client/v4/accounts/$ACCOUNT_ID/registrar/domain-check" \
  --header "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  --header "Content-Type: application/json" \
  --data '{"domains": ["acmecorp.dev", "acmecorp.io"]}'

# 新規登録（アカウントの既定支払い手段に課金される）
curl --request POST \
  --url "https://api.cloudflare.com/client/v4/accounts/$ACCOUNT_ID/registrar/registrations" \
  --header "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  --header "Content-Type: application/json" \
  --data '{"domain_name": "acmecorp.dev"}'
```

### 既存ドメインの状態取得（コンタクト・ロック・自動更新）
```bash
# アカウント配下のドメイン一覧
curl --request GET \
  --url "https://api.cloudflare.com/client/v4/accounts/$ACCOUNT_ID/registrar/domains" \
  --header "Authorization: Bearer $CLOUDFLARE_API_TOKEN"

# 単一ドメインの詳細（auto_renew, transfer_lock, contacts, registry_statuses 等）
curl --request GET \
  --url "https://api.cloudflare.com/client/v4/accounts/$ACCOUNT_ID/registrar/domains/acmecorp.dev" \
  --header "Authorization: Bearer $CLOUDFLARE_API_TOKEN"
```

### 移管・更新・ロック操作
ダッシュボード操作が前提。Auth Code発行・Transfer Lockのトグル・自動更新切り替えは「Registrar → 該当ドメイン → Configuration」配下に集約されている。APIは2026-05時点で更新・移管・ロック操作・コンタクト更新が未提供。

## 制限・注意点
- Cloudflare DNSをネームサーバとして使うのが必須。他社DNS（Route53 / NS1 / Akamai 等）に向けたままRegistrarだけ使うことはできない。
- 対応TLDは400+だが、日本主要TLDの.jp / .co.jp / .ne.jp / .or.jp は対象外。中国 .cn、ドイツ .de なども非対応。これらは別レジストラで運用継続が必要。
- IDN（アクセント記号付き・非ラテン文字ドメイン）は登録不可。
- Premium TLD（レジストリ側でプレミアム価格設定されているドメイン名）は登録できない、または別途プレミアム価格が適用される場合がある。
- 新規登録の支払いは有効なクレジットカード / PayPalが必要。一部の地域では決済が制限される。
- ICANN規定により、登録60日未満・移管60日未満のドメインは他社へ転出できない。Registrant情報変更直後も同様。
- Shopify / Wix / Squareで取得したドメインはネームサーバ変更を許可しないため、別レジストラ経由＋60日待機の二段階移管が必要。
- Registrar APIはβで、更新・移管・ロック操作・コンタクト更新は未対応。完全自動化はできない。
- 自動更新が前提設計のため、支払い手段切れ・カード期限切れの監視を運用に組み込む必要がある。アカウント単位で更新が止まるリスクがある。
- Registry Lock（Custom Domain Protection）はEnterprise限定、対応TLDも限定。Free / Pro / Businessでは利用できない。
- WHOIS開示要請に対する応答ポリシーはCloudflareの規定に従う。法的開示要請のSLAをコントロールしたい組織は別途検討が必要。
- バルク登録・転売目的のドメイナー運用は想定外。利用規約・運用フロー両面で不向き。

## 参考リンク
- Cloudflare Registrar（製品ページ）：https://developers.cloudflare.com/registrar/
- Supported TLDs：https://developers.cloudflare.com/registrar/top-level-domains/
- Transfer domain to Cloudflare：https://developers.cloudflare.com/registrar/get-started/transfer-domain-to-cloudflare/
- Transfer out from Cloudflare：https://developers.cloudflare.com/registrar/account-options/transfer-out-from-cloudflare/
- Inter-account transfer：https://developers.cloudflare.com/registrar/account-options/inter-account-transfer/
- WHOIS redaction：https://developers.cloudflare.com/registrar/account-options/whois-redaction/
- WHOIS requests：https://developers.cloudflare.com/registrar/whoisrequests/
- Enable DNSSEC：https://developers.cloudflare.com/registrar/get-started/enable-dnssec/
- Custom Domain Protection（Registry Lock）：https://developers.cloudflare.com/registrar/custom-domain-protection/
- Registrar API guide：https://developers.cloudflare.com/registrar/registrar-api/
- API reference：https://developers.cloudflare.com/api/resources/registrar/
- Troubleshooting：https://developers.cloudflare.com/registrar/troubleshooting/
- Registrar llms.txt：https://developers.cloudflare.com/registrar/llms.txt

---
参照日: 2026-05-04
