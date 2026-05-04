# Rate Limiting

## 一行サマリ
Cloudflareエッジで「同じ識別子（IP / Header / Cookie / Body フィールド等）から一定期間に何リクエスト来たか」をカウントし、閾値を超えたものをBlock / Challenge / Logするレートベース制御である。WAF配下の「Rate limiting rules」として統合され、Enterpriseでは複雑な特徴量や複雑度スコアに基づくAdvanced Rate Limitingまで一気通貫で書ける。

## 解決する課題（Why）
WAFの署名ベース防御は「1リクエスト単体が悪性かどうか」しか見ない。そのためログイン総当たり、商品在庫の買い占め、価格スクレイピング、APIキー流出後の暴走呼び出しといった「個別リクエストは正常だが、頻度が異常」な攻撃を捉えられない。Originのアプリ側でカウンタを実装すると、(1) インスタンス間の状態共有（Redis等）、(2) WAF・LBより手前で止められない、(3) Botネットワークによる分散リクエストで識別子設計を間違えやすい、という運用負債を抱える。Cloudflare Rate Limitingはこれをエッジ側で完結させ、以下を解決する。

- ログインPOSTやワンタイムトークン検証エンドポイントへの総当たりを、ユーザー名（リクエストボディ）単位で抑止。
- 在庫・予約・チケット販売の買い占めBotを、Cookie / セッションID単位で抑止。
- 公開API（無料プラン）における暴走呼び出しを、APIキー（Header）単位で抑止。
- スクレイピングを、JA3/JA4フィンガープリントやASN単位でしきい値運用。
- Originに到達する前にBlock / Managed Challengeで返すことで、バックエンドの計算資源・DB接続を保護。

## 主要機能（What）

### Rate Limiting Rules（WAF統合）
2023年の刷新で従来の「Legacy Rate Limiting」はWAF配下の `rate limiting rules` として統合された。WAF Custom Rules / Managed Rulesと同じRules言語（`http.request.uri.path`, `http.request.method`, `ip.src`, `cf.bot_management.score` 等）でマッチ条件を書き、そこに「Period内に何回マッチしたら何をするか」を重ねる構造になっている。

- **Expression**：マッチ対象を絞り込むRules言語式。`http.request.uri.path eq "/api/login" and http.request.method eq "POST"` のように、レート制限を効かせたいエンドポイントだけを切り出す。
- **Characteristics（カウント単位）**：誰／何ごとにカウントするか。IP / IP with NAT / Header / Cookie / Body / JA3-JA4 / ASN / Country / Path / Custom など。
- **Period**：カウントの時間窓（秒）。Free 10秒、Pro 最大1分、Business / Enterprise 最大10分（最大65,535秒まで対応するプランあり）。
- **Requests per period**：閾値。
- **Mitigation timeout（Duration）**：閾値到達後、どれだけの間アクションを継続するか。Pro 最大1時間、Business / Enterprise 最大24時間。
- **Action**：Block / Managed Challenge / JS Challenge / Interactive Challenge / Log。EnterpriseではBlock時に「Throttle requests above rate」（超過分のみブロック、閾値以下は通す）が選べる。

### Advanced Rate Limiting（Business以上 / 多くはEnterprise）
標準のIP単位カウントでは捉えられないユースケースを、複合特徴量とペイロードベースで吸収する上位機能群。

- **Complex characteristics**：複数のSelectorを組み合わせ「同一IP + 同一User-Agent + 同一Cookie値」のような複合キーでカウント。Botネットの分散攻撃で「IPは違うがUser-Agentが同じ」「Cookieは違うがJA4が同じ」といった揺らぎを潰せる。
- **Payload-based**：`http.request.body.form["username"]` のようにリクエストボディ内のフィールドをカウント単位にできる。ログインAPIで「同じusernameに対する試行回数」を直接抑制でき、IP単位より攻撃意図に近い指標になる。
- **Complexity score**：1リクエストの「重さ」（コスト）を score として加算し、純粋な回数ではなく総コストで閾値を切るモデル。重いGraphQLクエリやレポート生成APIでの暴走対策に向く。
- **Throttle action**：閾値超過分のみをBlock / Challengeし、閾値以下のリクエストはそのまま通す（純粋な「整流」）。

### Counting Characteristics（プラン別対応）
カウント単位として何を選べるかはプランで明確に分かれる。

| プラン | 利用可能な Characteristics |
|---|---|
| Free | IP のみ |
| Pro | IP |
| Business | IP / IP with NAT |
| Enterprise（Advanced） | IP / IP with NAT / Header / Cookie / ASN / Country / Path / JA3-JA4 Fingerprint / JSON field / Body / Form input / Custom expression |

「IP with NAT」はCloudflareが推定する「同一NAT配下を1ユーザーとみなす」拡張で、モバイルキャリアNATや企業プロキシで誤ブロックを抑える。

### Mitigation Timeout（Duration）
閾値到達後、どれくらい制裁を続けるか。短すぎれば攻撃側が即座にリトライするだけになるし、長すぎれば誤検知が業務を止める。一般的な設計指針は次の通り。

- ログインBrute-force：Period 60s / Threshold 5〜10 / Timeout 10〜30分（人間のリトライ時間に合わせる）。
- スクレイピング：Period 60s / Threshold 100〜300 / Timeout 1〜24時間（ターゲットコンテンツの重要度次第）。
- API濫用：Period 60s / Threshold = プランごとのRPS×60 / Timeout 10分〜1時間（請求と整合する制裁時間）。

### Workers Rate Limiting API（自前実装の選択肢）
WAFのRate Limiting Rulesは「ゾーン全体に対するエッジ手前の機械的制御」だが、Workers Rate Limiting APIは「Worker内のロジック条件込みでカウントしたい」場合の補完である。

- `env.MY_RATE_LIMITER.limit({ key })` のシンプルなAPIで、内部的にDurable Objectsベースのカウンタが走る。
- 認証後のユーザーID単位、ワークフローのステップ単位など、WAF Expressionでは表現しづらい「アプリ文脈で正規化したキー」でレート制限できる。
- KV / Durable Objectsを直接叩いて自前カウンタを書くこともできるが、それは整合性・コスト・実装複雑度を引き受ける覚悟が要る。Rate Limiting APIは「DOで自前実装する一歩手前」を引き受ける位置づけである。

### Legacy Rate Limiting（deprecated）からの移行
2017年から提供されていた旧Rate Limiting（ダッシュボード上で「Tools → Rate Limiting」にあった独立機能）は、現在は新しい「WAF配下のRate limiting rules」に統合されている。

- 旧ルールは引き続き動作するが、新規作成は新形式で行う前提。
- 旧ルールは「URLパターン + Method + Threshold」しか持たないため、Expressionによる柔軟な絞り込みやEnterprise Advanced機能が使えない。
- 移行はCloudflareダッシュボードの誘導またはAPI（`POST /zones/{id}/rulesets/.../rules` で `phase = http_ratelimit`）で行う。Terraform管理下なら `cloudflare_ruleset` リソースに `phase = "http_ratelimit"` で書き直す。

## アーキテクト視点：いつ選ぶか

### Bot Management / API Shield との役割分担
3者は「速度・形・素性」のどこで切るかで棲み分ける。

- **Rate Limiting**：速度（頻度）で切る。識別子と閾値・期間というシンプルなモデル。Bot判定ができない（しない）リクエストにも効く。
- **Bot Management**：素性（人間 / 良性Bot / 悪性Bot）で切る。Bot Score、JA4、機械学習による行動分析。「人間っぽいかどうか」の判定そのもの。
- **API Shield**：形（API契約）で切る。OpenAPIスキーマからの逸脱、Schema Validation、Sequence Mitigation、JWT検証。APIエンドポイントを「正しい形のリクエストか」で守る。

実運用では `[Bot Management で明確な悪性Botを落とす] → [API Shieldでスキーマ違反を落とす] → [Rate Limitingで人間/Bot問わず頻度異常を抑える]` のように直列配置する。Rate Limiting単独では「分散Bot」「人間っぽいBot」を取り逃がしやすく、Bot Management単独では「正規ユーザーの暴走」「APIキー漏洩後の悪用」を取り逃がしやすい。

### 適しているシーン
- ログインAPI / OTP送信API / パスワードリセットAPIなど、明確に「同一識別子からの連続試行」が攻撃シグナルになるエンドポイント。
- 公開APIの無料プランRPS制限の実装基盤（課金プラン別のしきい値運用）。
- 在庫・予約・チケットなど買い占めBot対策（Cookie / セッション単位）。
- スクレイピング対策の第1段（JA3/JA4 / ASN単位でPeriod長め）。

### 適していないシーン
- そもそもCloudflare経由していないトラフィック（Origin直アクセス可能なIP）にはRate Limitingは効かない。Origin IP秘匿が前提。
- Worker内のロジック条件・認証後ユーザーID単位の制御は、Workers Rate Limiting APIまたはアプリ側実装の方が適切。
- 短期スパイクではなく長期傾向（1日単位の総量配分）はQuota管理の世界で、Apigee Quotaや自前のメータリングが向く。

## 競合・代替

| 観点 | Cloudflare Rate Limiting | AWS WAF Rate-based | Kong Rate Limiting | Apigee Quota / Spike Arrest | Akamai Rate Controls | Imperva ABP |
|---|---|---|---|---|---|---|
| 配置 | エッジ（Cloudflareネットワーク） | エッジ（CloudFront / ALB / API GW） | API Gateway内 | API Management内 | エッジ（Akamai） | エッジ（Imperva） |
| カウント単位 | IP / Header / Cookie / Body / JA3-JA4 / ASN / Country 他（Enterprise） | IP / Header / Forwarded IP / カスタムキー | Consumer / Credential / IP / Service / Header | API key / Developer / App / Product | IP / Geo / カスタム | IP / セッション / フィンガープリント |
| ペイロード単位カウント | あり（Form input / JSON field / Body）※Enterprise | 限定的（ヘッダ・クエリ中心） | あり（Body parser plugin） | あり（API Productに紐づく） | あり | あり |
| Throttle（超過分のみ） | あり | あり（Block / Count） | あり | Spike Arrestで実装 | あり | あり |
| Bot対策との統合 | Bot Managementと密結合 | AWS WAF Bot Controlは別ルール | 別Plugin | 別商品 | Bot Manager別商品 | 同一プラットフォーム強み |
| 強み | エッジ統合・JA4 / Body単位までエッジで完結 | AWSスタック完結・IaC成熟 | OSS基盤・自前運用OK・拡張性 | API管理基盤としての設計力 | 大規模配信基盤・成熟度 | Bot対策と一体運用 |
| 弱み | Free / ProでIP単位以外不可 | カウント単位の柔軟性は中位 | 自前運用のオーバーヘッド | エッジではなくAPIゲートウェイ位置 | 高コスト・調達ハードル | 高コスト |

CloudflareのRate Limitingは「エッジで止められる」「JA4 / Body / Cookieまでエッジで効く」「Bot Management / API Shield / WAFと同じプレーンで書ける」点に集約される。Originがマルチクラウドだったり、API Gatewayレイヤを別ベンダーで揃えていてもエッジ手前で1段絞れるのが最大の差別化要因である。

## 料金
- **Free**：Rate Limiting Rules 1ルール（一部公開情報では「Previously Free」枠相当）。Period最大10秒、IP単位のみ。検証用途。
- **Pro**：5ルール程度。Period最大1分、Mitigation Timeout最大1時間、IP単位のみ。
- **Business**：15ルール程度。IP / IP with NAT。Period・Timeoutともに上限拡張。
- **Enterprise**：100ルール超 + Advanced Rate Limiting（Header / Cookie / Body / JA4 / ASN / Country / Custom expression、Complexity score、Throttle action）。Period最大10分（プラン詳細によっては65,535秒まで）、Timeout最大24時間。

実装上は「Free / Proは『IPベースの最低限の防衛線』、Business以上から『業務要件に沿ったRate Limiting設計』が現実解」と割り切るのが妥当である。WAFやBot Managementとセットで Enterprise Advanced を引くケースが多い。

## CLI / API 例

### Ruleset API（curl）でレート制限ルールを追加
http_ratelimit phaseのrulesetに追加する形になる。

```bash
ZONE_ID="..."
TOKEN="..."

# 1) http_ratelimit phaseのentry point rulesetを取得（無ければ作成）
curl -s -X GET \
  "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/rulesets/phases/http_ratelimit/entrypoint" \
  -H "Authorization: Bearer ${TOKEN}"

# 2) ルールを追加：/api/login への POST に対し、IP単位で60秒5回を超えたら10分Block
curl -s -X POST \
  "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/rulesets/phases/http_ratelimit/entrypoint/rules" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  --data '{
    "description": "Login brute-force protection",
    "expression": "(http.request.uri.path eq \"/api/login\" and http.request.method eq \"POST\")",
    "action": "block",
    "ratelimit": {
      "characteristics": ["ip.src", "cf.colo.id"],
      "period": 60,
      "requests_per_period": 5,
      "mitigation_timeout": 600
    }
  }'
```

### Terraform（cloudflare provider v5）
```hcl
resource "cloudflare_ruleset" "rate_limit_login" {
  zone_id     = var.zone_id
  name        = "Rate limiting rules"
  description = "Edge rate limiting"
  kind        = "zone"
  phase       = "http_ratelimit"

  rules = [
    {
      description = "Login brute-force: 5 req/60s per IP -> block 10min"
      expression  = "(http.request.uri.path eq \"/api/login\" and http.request.method eq \"POST\")"
      action      = "block"
      ratelimit = {
        characteristics     = ["ip.src", "cf.colo.id"]
        period              = 60
        requests_per_period = 5
        mitigation_timeout  = 600
      }
    },
    {
      description = "API key abuse: 1000 req/60s per X-Api-Key -> managed_challenge 1h"
      expression  = "(starts_with(http.request.uri.path, \"/api/\"))"
      action      = "managed_challenge"
      ratelimit = {
        characteristics     = ["http.request.headers[\"x-api-key\"]", "cf.colo.id"]
        period              = 60
        requests_per_period = 1000
        mitigation_timeout  = 3600
      }
    },
    {
      description = "Login attempts per username (Advanced Rate Limiting / Enterprise)"
      expression  = "(http.request.uri.path eq \"/api/login\" and http.request.method eq \"POST\")"
      action      = "block"
      ratelimit = {
        characteristics     = ["http.request.body.form[\"username\"]", "cf.colo.id"]
        period              = 60
        requests_per_period = 10
        mitigation_timeout  = 1800
      }
    },
  ]
}
```

### Workers Rate Limiting API
```jsonc
// wrangler.jsonc
{
  "name": "api-worker",
  "main": "src/index.ts",
  "compatibility_date": "2025-01-01",
  "ratelimits": [
    { "name": "API_LIMITER", "namespace_id": "1001", "simple": { "limit": 100, "period": 60 } }
  ]
}
```

```ts
export default {
  async fetch(req: Request, env: Env): Promise<Response> {
    const userId = await authenticate(req); // 認証後のユーザーID
    const { success } = await env.API_LIMITER.limit({ key: userId });
    if (!success) return new Response("rate limited", { status: 429 });
    return handle(req);
  },
};
```

## 制限・注意点
- **カウンタ更新の遅延**：Cloudflareは「リクエスト検知からカウンタ反映まで数秒の遅延がある」と明記している。閾値直後の数秒間は超過リクエストがOriginに届く前提で設計する（Origin側にも保険を置く）。
- **Period上限はプラン依存**：Free 10秒、Pro 1分、Business / Enterprise 10分〜（プラン詳細により最大65,535秒）。Period長を前提にした設計（例：1時間レート）はBusiness以上。
- **Counting Characteristics数とルール数の上限**：プランごとに利用可能な特徴量の種類数とルール数が決まる。Header / Cookie / Body単位が必要なら原則Enterprise。
- **`cf.colo.id` の扱い**：CloudflareはAnycastで複数PoPに分散するため、特徴量に `cf.colo.id` を加えて「PoPごとカウント」とする運用が公式サンプルでも採用されている。グローバルに厳密な集約カウントが要るケースには向かない（その用途はWorkers Rate Limiting APIや自前DOで実装）。
- **OriginIP直叩き対策**：Cloudflareを通らなければ意味がない。Authenticated Origin Pulls / Cloudflare Tunnel / Origin IPホワイトリストで直アクセスを塞ぐ前提が必要。
- **Bot Managementとの順序**：同一フェーズで動作するため、ルールの優先順位（Custom Rules → Rate Limiting Rules → Managed Rules）を意識して設計する。Bot Management未契約の環境でRate Limitingだけに頼ると、分散Botに対しては効果が薄い。
- **Legacy Rate Limitingの扱い**：旧ルールは新形式と並存できるが、Advanced機能・新Expression言語が使えないため、移行を前提に棚卸しする。

## 参考リンク
- Cloudflare WAF Rate Limiting Rules：https://developers.cloudflare.com/waf/rate-limiting-rules/
- Advanced Rate Limiting：https://developers.cloudflare.com/waf/rate-limiting-rules/use-cases/
- Counting characteristics（プラン別対応）：https://developers.cloudflare.com/waf/rate-limiting-rules/parameters/#characteristics
- Workers Rate Limiting API：https://developers.cloudflare.com/workers/runtime-apis/bindings/rate-limit/
- Ruleset API（http_ratelimit phase）：https://developers.cloudflare.com/ruleset-engine/about/phases/
- Terraform `cloudflare_ruleset`：https://registry.terraform.io/providers/cloudflare/cloudflare/latest/docs/resources/ruleset
- Cloudflare Plans（料金）：https://www.cloudflare.com/plans/
- Bot Management（役割分担）：https://developers.cloudflare.com/bots/
- API Shield（役割分担）：https://developers.cloudflare.com/api-shield/

---
参照日: 2026-05-04
