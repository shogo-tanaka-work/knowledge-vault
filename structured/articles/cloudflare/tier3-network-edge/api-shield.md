# API Shield

## 一行サマリ
OpenAPIスキーマ・学習済みスキーマ・mTLS・JWT検証・シーケンス分析を組み合わせ、Web全般を見るWAFでは捉えきれない「APIに固有の脆弱性と濫用」をエッジで止めるAPI専用のセキュリティレイヤである。

## 解決する課題（Why）
APIエンドポイントは「正規ユーザーが正しい認証情報で、ただし想定外の使い方をする」攻撃に晒される。OWASP API Top 10が挙げるBOLA（Broken Object Level Authorization）、認証不備、過剰なデータ露出、リソース消費の濫用などは、シグネチャベースのWAFが得意とする「明らかに悪意あるペイロード」とは性質が異なる。さらに、開発チームが把握していないShadow APIや、廃止したはずのZombie APIが本番に残り続けるガバナンス問題も常態化している。API Shieldはこれをエッジで以下のように解く。

- 通過する全リクエストを観測してShadow / Zombie APIを自動検出し、棚卸しを継続的に維持する。
- OpenAPIスキーマ（持ち込みまたは学習）に違反するリクエストをエッジで遮断する。
- mTLSとJWT検証で「呼び出し元の正当性」をオリジン到達前に保証する。
- BOLA / Volumetric Abuse / Sequence Mitigationでビジネスロジックを悪用する濫用を検出・抑制する。
- GraphQLの深さ・複雑度を制御し、単一クエリでのリソース枯渇攻撃を防ぐ。

WAFは「Webアプリ全般のシグネチャ防御」、API ShieldはAPIに特化した「振る舞い・契約・アイデンティティ防御」と役割が分かれており、両者は併用が前提である。

## 主要機能（What）

### API Discovery
通過トラフィックからAPIエンドポイントを自動抽出し、Endpoint Managementに登録する機能である。検出方法は2系統あり、ヒューリスティック検出（パスパターン・コンテンツタイプから推定）と、Session Identifierベースの検出（Cookieやヘッダで識別したセッションを軸にエンドポイントを集計）が併用される。Session Identifierを設定するほうが精度が高く、認証後にしか露出しない管理API・内部APIまで拾える。Shadow API / Zombie APIの可視化はAPI Shield導入の最初のROIになる。

### Schema Validation
OpenAPI v3.0/v3.1のスキーマに基づいてリクエストを検証し、違反したものをLog / Block / Override Status Codeで処理する。スキーマの入手経路は2つ。

- **Uploaded Schema**：開発チームが管理しているOpenAPIファイルをそのままアップロードする。CIから差し替えれば「契約=防御ルール」が一致する。
- **Learned Schema**：API Shieldが通過トラフィックから自動生成するスキーマ。OpenAPI管理が追いついていない既存APIに対して、まずLearnedで叩き台を作り、エクスポートして開発チームに正本化させる運用が現実解。

検証対象はパス・メソッド・クエリパラメータ・ヘッダ・リクエストボディ・型・必須項目まで広く、未知のパラメータや型不一致を弾く。

### mTLS（Mutual TLS）
Cloudflareが管理するCA、または持ち込みCAでクライアント証明書を発行し、エッジで検証する機能である。B2B API、IoTデバイス、モバイルアプリのバックエンドAPIなど、「呼び出し元が限定された機械」に対する正当性検証として使う。Endpoint Management上で「mTLS必須エンドポイント」を指定し、Cloudflare Rulesと組み合わせて未提示・無効証明書のリクエストをブロックする。mTLS機能自体はEnterprise以外の顧客にも開放されている例外領域である。

### JWT Validation
リクエストに付与されたJWTをエッジで検証し、署名・有効期限・iss / aud / sub等のクレームを評価する。Token Configurationsで複数のIdP（Auth0 / Cognito / Okta / Firebase Auth等のJWKS）を登録し、エンドポイントごとに「どの発行者を許容するか」を縛れる。さらにJWTのclaim値をTransform RulesやRulesetでヘッダに伝搬させ、オリジン側で再検証せずにユーザーIDを取り出す構成が可能。Authentication Postureと併用すると「JWT必須エンドポイントなのに無認証で叩かれている」異常を検知できる。

### Sequence Mitigation / Sequence Analytics
APIエンドポイントの「呼ばれる順序」をシーケンスとして観測する機能である。たとえば「/login → /transfer」のように特定の順序でしか呼ばれないはずのエンドポイントが、ボットによる総当たり的呼び出しでスキップされた場合に検出・遮断できる。Sequence Analyticsで観測パターンを可視化し、Sequence Mitigationでルール化する流れになる。OWASP API Top 10のうち「ビジネスロジックの濫用」を狙い撃ちする数少ない実装である。

### BOLA Protection
Broken Object Level Authorization（他ユーザーのリソースID指定で他人のデータを取得する古典的脆弱性）の兆候を検出する。エンドポイント別に「同一ユーザーが多様なオブジェクトIDを連続で叩いている」「通常分布を外れたID走査が起きている」といったパターンを統計的に拾い、Endpoint Insightsとして提示する。Block化はSequence MitigationやRate Limiting Rulesと組み合わせて実装する。

### Volumetric Abuse Detection
エンドポイントごとに「セッション単位 / IP単位 / JWT sub単位」で正常リクエストレートを学習し、外れ値を検出する機能である。WAFのRate Limiting Rulesが「閾値を人間が決める」のに対し、こちらは「正常分布をエッジが自動学習する」。クレデンシャルスタッフィング、在庫買い占めボット、価格スクレイピングなどの検出に向く。検出結果から推奨Rate Limit Ruleを生成できる。

### GraphQL Malicious Query Protection
単一GraphQLクエリでリソースを枯渇させる攻撃（深いネスト、巨大エイリアス、循環フラグメント）を、クエリの深さ（depth）とサイズ（size）の上限で制限する機能である。GraphQLはRESTと違って単一エンドポイントで任意のクエリを受け付けるため、従来のURL単位レート制限が効かない。API ShieldはGraphQL固有の構造解析でこのギャップを埋める。

### Endpoint Management / Labels / Routing
検出・登録された全エンドポイントに対し、Label（PII含む / 認証必須 / 内部用 等のメタ情報）を付与し、それを軸にポリシー・分析・アラートを束ねる。Routingでオリジンの振り分け、Developer Portal機能で社内向けAPIカタログの公開も可能。

## アーキテクト視点：いつ選ぶか

### 適しているシーン
- 既にCloudflare WAF / CDNを使っており、API向けに別ベンダーの専用ツールを新規導入する前に、同一プレーンで一段上げたい組織。
- OpenAPIスキーマを開発チームが管理しているが、本番に「契約として」適用する仕組みがない組織。Schema ValidationでCI連携が一気に成立する。
- B2B API、フィンテック、医療情報API、IoTバックエンドなどmTLSが業務要件に入る組織。
- 「Shadow API / Zombie APIがどれだけあるか分からない」状態のレガシーAPI資産を抱える組織。Discovery単独でもROIが出る。
- GraphQL APIを本番で公開しており、深さ・複雑度起因のDoSが懸念される組織。

### 適していないシーン
- Salt Security / Noname / Traceableなど純血API Securityベンダーを既に導入し、ML異常検知・E2Eトレーシング・OWASP API Top 10ダッシュボードを業務として使い倒している組織。API Shieldの分析深度はまだ追従途上である。
- API流量がCloudflareエッジを通っていない（オンプレ / 別CDN / プライベート閉域）組織。Magic Transit / Tunnel経由で集約しない限り効かない。
- Enterprise契約を持たないPro / Business顧客。Endpoint ManagementとmTLSを除く中核機能は事実上Enterprise add-onである。
- 単純なREST APIにRate Limitingを足したいだけのケース。WAF Rate Limiting Rulesで足りる。

## 競合・代替

| 観点 | Cloudflare API Shield | Salt Security | Noname Security | 42Crunch | Traceable | AWS WAF + API Gateway | Kong | Apigee |
|---|---|---|---|---|---|---|---|---|
| 出自 | CDN / WAFエッジ統合 | 純血API Security（ML中心） | 純血API Security（Discovery中心） | OpenAPI契約セキュリティ専業 | API分散トレース起点 | クラウドWAF + マネージドAPI GW | OSS APIゲートウェイ | エンタープライズAPI管理 |
| 配置 | エッジ（インライン） | アウトオブバンド + インライン | アウトオブバンド + インライン | CIシフトレフト + ランタイム | エージェント / アウトオブバンド | クラウド内インライン | インライン（自社ホスト可） | インライン |
| Discovery | ヒューリスティック + Session ID | 高精度ML | 高精度・Discoveryが本職 | スキーマ起点 | 分散トレース起点 | 限定的 | 限定的 | 限定的 |
| Schema Validation | OpenAPI Upload + Learned | 学習中心 | 学習中心 | 最強クラス（OpenAPI契約専業） | あり | 限定的 | あり | あり |
| BOLA / Logic Abuse | あり（エッジ統計） | 強み（MLベース） | あり | 限定的 | 強み（トレース解析） | 弱い | 弱い | 弱い |
| mTLS / JWT | 標準 | 検出のみ | 検出のみ | 検出のみ | 検出のみ | 別構成 | 標準 | 標準 |
| GraphQL保護 | depth / size制限 | あり | あり | OpenAPIスコープ外 | あり | 弱い | プラグイン | プラグイン |
| 価格 | Enterprise add-on | 高価（要見積） | 高価（要見積） | OpenAPI規模に応じた中位 | 高価（要見積） | AWS従量 | OSS無料〜Enterprise | 高価 |
| 強み | エッジ統合・WAF/Bot/CDNと同一プレーン | 業界最先端の検出深度 | Discoveryと棚卸しの完成度 | OpenAPIガバナンスのCI統合 | 分散環境の可視化 | AWS資産との相性 | 自社運用の自由度 | エンタープライズ管理機能 |
| 弱み | 検出深度は専業に劣る | 高コスト・運用負荷 | 高コスト・新興ベンダー | ランタイム検出は弱い | 高コスト・導入重い | API特化機能は弱い | セキュリティは後付け | 重厚・高価 |

API Shieldの差別化はWAF / Bot Management / Cache / Workers / mTLSが同一プレーンで束なる点に尽きる。逆にOWASP API Top 10をフルカバーするML検出・E2Eトレース・SOC運用ノウハウまで業務要件にあるなら、Salt / Noname / Traceableの併用または代替が妥当である。

## 料金

- **Endpoint Management / Schema Validation / mTLS**：全プランの顧客が利用可能（mTLSはCloudflare管理CAで証明書発行可）。Pro / Businessでも一部機能には触れる。
- **API Discovery（Session ID版）/ JWT Validation / Sequence Mitigation / Sequence Analytics / BOLA Protection / Volumetric Abuse Detection / GraphQL Protection / Schema Learning**：Enterprise add-on。Application Security Advanced / API Shieldライセンスのいずれかが必要。
- **非契約Preview**：Enterprise顧客向けに、API Shield機能の一部を従量課金なしで試用できる枠が提供される。本番採用前のPoCはここで行うのが定石。
- **JDCloud顧客には提供されない**地理的制約がある。

WAF / Bot Management / DDoSとは別ラインで課金されるため、見積もりはApplication Security全体のバンドル価格として営業に出させるのが現実的である。

## CLI / API 例

### OpenAPIスキーマのアップロード（Schema Validation）
```bash
# ZONE_ID とAPI Tokenを準備し、OpenAPI v3スキーマを登録
curl -X POST \
  "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/schema_validation/schemas" \
  -H "Authorization: Bearer ${CF_API_TOKEN}" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@./openapi.yaml" \
  -F "kind=openapi_v3" \
  -F "name=payments-api-v1" \
  -F "validation_enabled=true"

# Schema Validation設定（違反時のデフォルト動作をBlockに）
curl -X PUT \
  "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/schema_validation/settings" \
  -H "Authorization: Bearer ${CF_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"validation_default_mitigation_action":"block","validation_override_mitigation_action":null}'
```

### mTLSクライアント証明書の発行（Cloudflare管理CA）
```bash
# Cloudflare管理CAからクライアント証明書を発行
curl -X POST \
  "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/client_certificates" \
  -H "Authorization: Bearer ${CF_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "csr": "'"$(cat client.csr | sed ':a;N;$!ba;s/\n/\\n/g')"'",
    "validity_days": 365
  }'

# mTLS Hostname設定（特定ホスト名でクライアント証明書を必須化）
curl -X POST \
  "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/access/certificates/settings" \
  -H "Authorization: Bearer ${CF_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"settings":[{"hostname":"api.example.com","client_certificate_forwarding":true,"china_network":false}]}'
```

### JWT Token Configurationの登録
```bash
# JWKSエンドポイントを指定してToken Configを作成
curl -X POST \
  "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/api_gateway/token_configurations" \
  -H "Authorization: Bearer ${CF_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "auth0-prod",
    "credential_location": "authorization_header_bearer",
    "token_sources": [{"jwks_uri":"https://acme.auth0.com/.well-known/jwks.json"}]
  }'
```

### 検出済みエンドポイント一覧の取得（Discovery結果）
```bash
curl -X GET \
  "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/api_gateway/discovery/operations?state=review" \
  -H "Authorization: Bearer ${CF_API_TOKEN}"
```

## 制限・注意点
- 中核機能（Discovery Session ID / JWT / Sequence / BOLA / Volumetric / GraphQL / Schema Learning）はEnterprise add-onである。Pro / BusinessではEndpoint Management・mTLS・Uploaded Schema Validationまでに限定される。
- Schema Validationの精度はOpenAPIスキーマの品質に依存する。型定義が雑なスキーマをアップロードすると誤遮断が起きるため、最初はLog Onlyで運用ログを観測し、段階的にBlockへ昇格する手順が必須。
- Learned Schemaは観測トラフィックに依存するため、低頻度エンドポイントや認証後にしか呼ばれないエンドポイントは学習が遅い。Session Identifier設定とセットでないと精度が出ない。
- mTLSはエッジ-クライアント間の検証であり、エッジ-オリジン間（Authenticated Origin Pulls）とは別機能。両方を要件として整理すること。
- JWT Validationは署名・期限・claim一致までで、認可ロジック（このユーザーがこのリソースを操作してよいか）はオリジン側責務。BOLAはこの認可漏れを統計的に検出するに過ぎず、根本対策はオリジン側の修正である。
- Sequence MitigationはAPI Shieldが「正常な順序」を観測できているエンドポイント群でのみ有効。新規ローンチAPIには学習期間が必要。
- GraphQL保護はdepth / sizeまでで、クエリコストベース（フィールドごとの重み付け）の制限は本機能では未対応。重い実装はApolloレベルでのcomplexity制御も併用する。
- API Shieldの分析画面はWAF / Bot Managementと別UIに分かれており、APIに関するシグナルだけを見るには複数ダッシュボードを行き来する必要がある。
- Cloudflareエッジを通らないAPIには一切効かない。マルチCDN・直接到達経路がある場合は、API Shield配下に統一する設計が前提となる。

## 参考リンク
- API Shield Overview：https://developers.cloudflare.com/api-shield/
- Security Features：https://developers.cloudflare.com/api-shield/security/
- Management and Monitoring：https://developers.cloudflare.com/api-shield/management-and-monitoring/
- Schema Validation：https://developers.cloudflare.com/api-shield/security/schema-validation/
- mTLS：https://developers.cloudflare.com/api-shield/security/mtls/
- JWT Validation：https://developers.cloudflare.com/api-shield/security/jwt-validation/
- Sequence Mitigation：https://developers.cloudflare.com/api-shield/security/sequence-mitigation/
- BOLA Protection：https://developers.cloudflare.com/api-shield/security/bola-protection/
- Volumetric Abuse Detection：https://developers.cloudflare.com/api-shield/security/volumetric-abuse-detection/
- GraphQL Malicious Query Protection：https://developers.cloudflare.com/api-shield/security/graphql-protection/
- API Shield API（Cloudflare API Reference）：https://developers.cloudflare.com/api/operations/api-shield-api-discovery-retrieve-discovered-operations-on-a-zone
- API Shield llms.txt：https://developers.cloudflare.com/api-shield/llms.txt

---
参照日: 2026-05-04
