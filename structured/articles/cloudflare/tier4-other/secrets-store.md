# Secrets Store

## 一行サマリ
APIキー・トークン・DB接続文字列などの機密情報をCloudflareアカウント単位で一元的に暗号化保管し、Workers / AI Gateway などからbinding経由で参照する集中型シークレット管理サービスである。Worker単位で分散していたシークレットを「アカウント・スコープ」に引き上げ、複数Worker間の共有・更新・監査を一元化する。

## 解決する課題（Why）
従来のCloudflare Workersでは、`wrangler secret put`によるWorker-scopedなシークレット管理（Workers Variables and Secrets）が標準であり、シークレットはWorkerごとに独立して保管されていた。これは小規模構成では十分だが、組織が成長すると次の問題が顕在化する。

- 同じAPIキー（例：Stripe / OpenAI / Slack Webhook）を複数のWorkerで使うとき、Workerごとに同一値を`wrangler secret put`する必要があり、ローテーション時に取りこぼしが発生する。
- どのWorkerにどのシークレットが入っているのかをアカウント横断で把握する手段がなく、棚卸し・離任者対応・コンプライアンス監査のコストが高い。
- Worker-scopedシークレットは値そのものを後から取得できない（書き込み専用）ため、開発者が「どの値が設定されているか」を確認する手段がなく、ローテーション漏れの温床になる。
- IaC化したい場合も、Worker単位でWrangler操作を繰り返す必要があり、シークレットの「単一の正本」を持てない。

Cloudflare Secrets Storeはこれをアカウント・スコープの中央リポジトリ化することで解決する。Workerからは`store_id` + `secret_name`で参照し、ローテーションはStore側で1回行えば全Workerに即座に反映される。Audit Logsで作成・更新・削除・参照の履歴がアカウント単位で追跡可能になり、RBACで権限分離もできる。

## 主要機能（What）

### Account-scopeのSecret管理
シークレットは`Store`という論理コンテナに格納され、Storeはアカウント単位で作成する。1アカウントあたり最大100シークレット（オープンベータ時点）が保持でき、各シークレット値は最大64 KiB（65,536 bytes）。Storeはダッシュボード・wrangler・REST API・Terraformから操作可能で、すべてのCloudflareデータセンターに暗号化された状態でレプリケートされる（中国ネットワークは現時点で対象外）。

### Workers Binding
`wrangler.toml`（または`wrangler.jsonc`）に`secrets_store_secrets`を宣言することで、Worker側からは通常のenv変数のように`env.<BINDING>.get()`で値を取得できる。binding時に`store_id`と`secret_name`を指定するため、Worker本体のデプロイをやり直さなくてもStore側で値を更新すれば次の実行から新しい値が反映される（=ローテーション時にWorker再デプロイ不要）。

```toml
[[secrets_store_secrets]]
binding = "OPENAI_API_KEY"
store_id = "<STORE_ID>"
secret_name = "openai-prod"
```

### AI Gateway BYOK（Bring Your Own Keys）連携
AI Gateway側からSecrets Storeに登録した各種AIプロバイダキー（OpenAI / Anthropic等）を`cf-aig-byok-alias`ヘッダで参照する仕組みが標準提供されている。これによりAI Gatewayの設定UIに直接APIキーを書かずに済み、複数キーのエイリアス切り替え（例：`default` / `team-a` / `team-b`）も実現できる。

### Rotation（ローテーション）
ローテーションは「Store側で値を更新する」だけで完了する。Worker再デプロイは不要で、binding経由の参照は次のリクエストから新しい値を返す。シークレット名（`secret_name`）は維持したまま、値だけを差し替えるのが基本パターン。複数のWorkerで同じ`secret_name`を参照していれば、1回の更新で全箇所が一括ローテーションされる。

### Audit Logs
アカウント標準のAudit Logs基盤と統合され、以下が記録される。

- **Access**：シークレット値・メタ情報の参照
- **Create**：新規作成（`duplicate`経由の場合は`duplicated_from_id`フィールド付き）
- **Update**：メタ情報・値の更新（値そのものを更新した場合は`value_modified: true`が立つ）
- **Delete**：削除

これによりコンプライアンス監査（SOC2 / ISO 27001）で求められる「機密情報の操作履歴」をCloudflareプレーン内で完結させられる。

### Access Control / RBAC
4つの専用ロールが提供されており、開発者・運用者・閲覧者で権限を分離できる。

| ロール | 値・メタの編集 | 値・メタの閲覧 | binding作成 | AI Gateway連携作成 |
|---|---|---|---|---|
| Super Administrator | 可 | 可 | 可 | 可 |
| Secrets Store Admin | 可 | 可 | 不可 | 不可 |
| Secrets Store Deployer | 不可 | メタのみ | 可 | 可 |
| Secrets Store Reporter | 不可 | メタのみ | 不可 | 不可 |

API Tokenスコープは`Account Secrets Store Edit`（編集）と`Account Secrets Store Read`（メタ閲覧）の2種類。CIから値を更新したい場合はEditを、参照棚卸し用途ならReadのみを発行する設計が原則。

### REST API
ダッシュボード操作はすべてREST APIにマップされており、IaC・CI連携が可能である。

- `POST /accounts/{account_id}/secrets_store/stores` — Store作成
- `GET /accounts/{account_id}/secrets_store/stores` — Store一覧
- `POST /accounts/{account_id}/secrets_store/stores/{store_id}/secrets` — Secret作成（複数まとめて投入可）
- `GET /accounts/{account_id}/secrets_store/stores/{store_id}/secrets` — Secret一覧
- `PATCH /accounts/{account_id}/secrets_store/stores/{store_id}/secrets/{secret_id}` — 値・メタ更新（ローテーションの正攻法）
- `POST /accounts/{account_id}/secrets_store/stores/{store_id}/secrets/{secret_id}/duplicate` — 別名複製（環境分離向け）
- `DELETE /accounts/{account_id}/secrets_store/stores/{store_id}/secrets/{secret_id}` — 削除
- `GET /accounts/{account_id}/secrets_store/quota` — クォータ確認

### vs Workers Secrets（worker-scoped）
| 観点 | Secrets Store（account-scoped） | Workers Secrets（worker-scoped） |
|---|---|---|
| スコープ | アカウント単位 | Worker単位 |
| 共有 | 複数Workerから`store_id`+`secret_name`で共有可 | 共有不可（同値を各Workerに別途投入） |
| ローテーション | Store側で1回更新→全Workerに即反映 | Workerごとに`wrangler secret put`を再実行 |
| 値の閲覧 | メタ情報の参照可（権限次第） | 書き込み後は閲覧不可（write-only） |
| Audit | アカウント標準のAudit Logsで一元管理 | 限定的（デプロイログ程度） |
| RBAC | 専用ロール4種で分離 | アカウント全体の権限に従属 |
| 適性 | 複数Workerで共有・本格運用 | 単一Worker・PoC・個人開発 |
| Binding形式 | `[[secrets_store_secrets]]` | `[vars]` / `wrangler secret put` |

## アーキテクト視点：いつ選ぶか

### 適しているシーン
- 同一APIキー（OpenAI / Anthropic / Stripe / Slack Webhook 等）を複数のWorkerやAI Gatewayで共有しているケース。ローテーション工数が桁で減る。
- SOC2 / ISO 27001等のコンプライアンス監査で「機密情報のアクセス・変更ログ」「権限分離の証跡」が要件になっている組織。
- 開発・ステージング・本番環境を別Worker（または別namespace）で構成しており、環境間で同じ正本シークレットを安全に複製したいケース。`duplicate` APIで明示的に派生関係を残せる。
- AI Gatewayと組み合わせてAIプロバイダキーをチーム単位でエイリアス管理したい組織。BYOKフローが標準連携される。
- IaC（Terraform / Pulumi）でCloudflare資産を管理しており、シークレットの単一の正本を持ちたいケース。

### 適していないシーン
- 単一Workerだけで完結し、シークレットも1〜2件しかない個人プロジェクト。`wrangler secret put`で十分で、Storeを別途設計するメリットが薄い。
- アカウントあたり100件・値64 KiBの上限を超える、KMSキー本体・大規模クライアント証明書の保管。これらはAWS KMS / GCP KMS / HashiCorp Vault のHSM連携領域に寄せる。
- 中国ネットワーク（Cloudflare China Network）で配信するWorkerが必須要件のケース。現時点で対象外。
- HSM裏付けのキー操作（署名・暗号化API）が必要なケース。Secrets Storeは「値の保管・参照」が役割で、KMSのような演算プリミティブは提供しない。
- ベータ段階のため本番のクリティカル経路（決済・認証の主要キー）を即座に全寄せするのは慎重に評価すべき。GA前提のSLAが必要ならVault / AWS Secrets Managerを並行運用する設計が無難。

## 競合・代替

| 観点 | Cloudflare Secrets Store | HashiCorp Vault | AWS Secrets Manager | GCP Secret Manager | Azure Key Vault | Doppler | 1Password Connect |
|---|---|---|---|---|---|---|---|
| 出自 | Cloudflare統合（Workers / AI Gateway） | OSS / Enterprise シークレット基盤の事実上の標準 | AWS マネージドシークレット | GCP マネージドシークレット | Azure マネージドキー / シークレット / 証明書 | DevOps向けSaaS（環境変数中心） | 1Password基盤の開発者向け配信 |
| スコープ | アカウント単位 | namespace / path | アカウント / リージョン | プロジェクト | Vault単位 | Project / Config | Vault単位 |
| 配信先 | Workers / AI Gateway（binding） | あらゆる経路（CLI / SDK / Agent） | AWSサービス全般 / SDK | GCPサービス全般 / SDK | Azureサービス全般 / SDK | あらゆるランタイム（Doppler CLI） | あらゆるランタイム（Connect Server） |
| ローテーション | Store側更新で即時反映 | Dynamic Secrets / Lease | Lambda連携で自動ローテ | バージョン管理＋手動・自動 | バージョン管理＋自動 | Webhook / Integration | 手動寄り |
| HSM / KMS | 非対応（暗号化方式は未公開） | Transit / Vault Enterprise HSM | KMS統合 | KMS統合 | HSM統合 | 非対応 | 非対応 |
| Audit | アカウント Audit Logs統合 | 詳細監査ログ | CloudTrail | Cloud Audit Logs | Azure Monitor | あり | あり |
| 料金最低帯 | Open Beta（無料） | OSS無料 / Enterprise有料 | $0.40 / secret / 月＋API課金 | $0.06 / version / 月＋API課金 | 標準は$0.03 / 10K操作 | Free（小規模） | Business以上の追加費用 |
| 強み | Workers / AI Gatewayへのゼロ運用統合 | 機能網羅性・Dynamic Secrets | AWS統合の深さ | GCP統合の深さ | Azure統合・HSM | DX良好・多ランタイム対応 | パスワード基盤との一体運用 |
| 弱み | KMSなし・件数100件・Beta | セルフホスト運用負荷 | コスト・AWS外配信は工夫要 | アクセス制御がIAMに従属 | 学習コスト | DevOps外用途は弱い | 開発者基盤としてはニッチ |

Secrets Storeの位置づけは「Cloudflareプレーン上にWorkers / AI Gatewayと統合された軽量なAccount-scopedシークレット倉庫」であり、Vault / AWS Secrets Manager / GCP Secret Manager / Azure Key Vault が担う「マルチクラウド汎用シークレット基盤」「Dynamic Secrets」「HSM裏付け」の用途とは正面競合しない。Cloudflareエッジ上のワークロードに限れば、bindingの容易さと再デプロイ不要なローテーションで運用コストを大きく下げられるため、Cloudflare中心構成では第一選択になる。

## 料金
オープンベータ（Open Beta）期間中は無料で利用できる。Cloudflare公式ドキュメントには現時点で価格表は掲載されておらず、GA後の課金モデル（per-secret / per-API call）も明示されていない。同種サービスの相場（AWS Secrets Manager: $0.40/secret/月 + API課金、GCP Secret Manager: $0.06/version/月 + API課金）を踏まえると、GA後はストア件数とAPI呼び出し回数の従量帯が想定される。本番投入前にCloudflareダッシュボードの`Secrets Store → Plans`またはアカウントマネージャに最新の単価を必ず確認すること。

## CLI / API 例

### wrangler でStoreとSecretを作成
```bash
# Storeを作成（remote=本番リソース）
npx wrangler secrets-store store create "prod-shared" --remote

# Storeの一覧
npx wrangler secrets-store store list

# Secretを作成（scopes=workers でWorker binding向けに登録）
npx wrangler secrets-store secret create <STORE_ID> \
  --name openai-prod \
  --scopes workers \
  --remote
# 値はプロンプトで標準入力から
```

### wrangler.toml にbindingを宣言
```toml
name = "ai-gateway-proxy"
main = "src/index.ts"
compatibility_date = "2026-04-01"

[[secrets_store_secrets]]
binding = "OPENAI_API_KEY"
store_id = "<STORE_ID>"
secret_name = "openai-prod"

[[secrets_store_secrets]]
binding = "ANTHROPIC_API_KEY"
store_id = "<STORE_ID>"
secret_name = "anthropic-prod"
```

### Workerコードからの参照
```ts
export interface Env {
  OPENAI_API_KEY: SecretsStoreSecret;
  ANTHROPIC_API_KEY: SecretsStoreSecret;
}

export default {
  async fetch(req: Request, env: Env): Promise<Response> {
    // .get() は非同期。値はその場で復号されメモリ上に展開される
    const apiKey = await env.OPENAI_API_KEY.get();

    const upstream = await fetch("https://api.openai.com/v1/chat/completions", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${apiKey}`,
        "Content-Type": "application/json",
      },
      body: await req.text(),
    });

    return new Response(upstream.body, {
      status: upstream.status,
      headers: upstream.headers,
    });
  },
};
```

### REST APIでSecretをローテーション
```bash
# 値を差し替え（再デプロイ不要で全bindingに反映）
curl -X PATCH \
  -H "Authorization: Bearer $CF_API_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{"value": "sk-new-rotated-key", "scopes": ["workers"]}' \
  "https://api.cloudflare.com/client/v4/accounts/$ACCOUNT_ID/secrets_store/stores/$STORE_ID/secrets/$SECRET_ID"

# Storeのクォータ確認（残件数）
curl -s -H "Authorization: Bearer $CF_API_TOKEN" \
  "https://api.cloudflare.com/client/v4/accounts/$ACCOUNT_ID/secrets_store/quota" \
  | jq .

# stagingにduplicateして派生関係を残す
curl -X POST \
  -H "Authorization: Bearer $CF_API_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{"name": "openai-staging", "scopes": ["workers"]}' \
  "https://api.cloudflare.com/client/v4/accounts/$ACCOUNT_ID/secrets_store/stores/$STORE_ID/secrets/$SECRET_ID/duplicate"
```

### AI Gateway BYOK連携（参考）
```bash
# AI Gateway経由のリクエストでaliasを指定
curl https://gateway.ai.cloudflare.com/v1/<ACCOUNT_ID>/<GATEWAY>/openai/chat/completions \
  -H "Authorization: Bearer $CF_AIG_TOKEN" \
  -H "cf-aig-byok-alias: team-a" \
  -H "Content-Type: application/json" \
  --data '{"model":"gpt-4o-mini","messages":[{"role":"user","content":"hi"}]}'
```

## 制限・注意点
- **オープンベータ**段階のため、SLA・GA後の料金・後方互換性が確定していない。クリティカル経路（決済・本番認証）への全面移行は慎重に評価する。
- アカウントあたりの**シークレット件数は100件**（ベータ時点）、1値あたり**64 KiB**まで。これを超える要件はVault / AWS Secrets Managerに寄せる。
- **KMS / HSM連携は未提供**。署名・暗号化APIなどキー演算プリミティブが必要な用途には不向き。Secrets Storeはあくまで「値の保管・参照」のレイヤである。
- **Cloudflare China Network 非対応**。中国向け配信を必須とするWorkerは併用設計が必要。
- 暗号化方式の詳細（鍵管理階層・カスタマーマネージドキーの可否）は公式ドキュメントで明示されておらず、「すべてのCloudflareデータセンターに暗号化保存」という記述に留まる。法令・契約上の要求がある場合は事前にCloudflare営業へ確認する。
- シークレット名にスペース不可、`scopes`（現時点で実用的なのは`workers`）の指定が必要。binding時の`store_id`と`secret_name`はWorkerデプロイ時に検証されるため、タイポはデプロイ失敗で即時に検知される。
- `env.BINDING.get()`は**非同期**呼び出し。同期的なグローバル定数参照のように扱うとTypeScript / 実行時の双方でハマる。値は呼び出しごとにキャッシュされる挙動を前提に、ホットパスでは関数内に閉じて再利用する。
- Worker-scoped Secrets（`wrangler secret put`）は引き続き利用可能で、両者は併存できる。段階的移行する場合は「共有が必要なものから順にStoreへ寄せる」のが安全。
- ローテーション時、古い値を参照していたコネクション・キャッシュが残ると一時的にエラーが出る場合がある。アプリ側でリトライ・401時の再取得ロジックを持たせるのが堅牢。
- Audit Logsの保持期間はアカウントプランに依存（Enterprise以外は短い）。長期保管が要件ならLogpushでオブジェクトストレージ・SIEMへ転送する設計を併用する。

## 参考リンク
- Secrets Store Overview：https://developers.cloudflare.com/secrets-store/
- Workers Integration：https://developers.cloudflare.com/secrets-store/integrations/workers/
- Manage Secrets：https://developers.cloudflare.com/secrets-store/manage-secrets/
- Access Control（RBAC）：https://developers.cloudflare.com/secrets-store/access-control/
- Audit Logs：https://developers.cloudflare.com/secrets-store/audit-logs/
- REST API（secrets_store）：https://developers.cloudflare.com/api/resources/secrets_store/
- AI Gateway BYOK：https://developers.cloudflare.com/ai-gateway/configuration/bring-your-own-keys/
- llms.txt（ドキュメント全体インデックス）：https://developers.cloudflare.com/secrets-store/llms.txt

---
参照日: 2026-05-04
