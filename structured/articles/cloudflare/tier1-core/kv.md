# Workers KV

## 一行サマリ

Cloudflareのグローバル分散KVストア。世界中のエッジから低レイテンシで読み込めるため、読み込み比率が圧倒的に高く結果整合性で許容できるユースケース（設定値・認証情報・キャッシュ・フィーチャーフラグ等）に最適化されている。

## 解決する課題（Why）

従来のリージョン型KVS（DynamoDBやElastiCache）はリージョン外からのアクセスでレイテンシが跳ね上がる。グローバルにユーザーを抱えるアプリケーションでは、リージョン選定・レプリケーション設計・接続プール管理がアーキテクトの負担になる。Workers KVはCloudflareの300超データセンターに自動レプリケートし、Workersのバインディング経由でゼロ設定の低レイテンシ読み込みを提供する。「読み込みが多く、わずかな伝搬遅延を許容できる」ワークロードを最小コードで実装できる。

## 主要機能（What）

- Workersバインディングによる`get` / `put` / `delete` / `list` API
- REST API経由での外部アプリからの操作
- キーごとのメタデータ（最大1024バイト）保存
- TTL指定による自動削除（`expirationTtl`）
- リード時のエッジキャッシュ（`cacheTtl`、最小30秒）
- ネームスペース単位での論理分離（1アカウントあたり1,000ネームスペース）

## アーキテクト視点：いつ選ぶか

### 適しているシーン（読込多い・結果整合性OK）

- グローバル配信の設定値・フィーチャーフラグ
- APIレスポンスキャッシュ
- ユーザープリファレンス・認証セッションのキャッシュ層
- A/Bテストのバリアント割り当て
- 静的アセットのメタデータ・ルーティングテーブル
- 読込:書込比が概ね100:1以上のワークロード

### 適していないシーン（強整合・高頻度書込み）

- 在庫数・残高・カウンタなど強整合が必須の処理 → Durable Objectsを使う
- 同一キーへの秒間1回超の書込み（書込みレート制限）
- リレーショナルクエリやJOIN・トランザクション → D1
- 大容量バイナリ（25 MiB超） → R2
- 書込み即時に全リージョンへ反映が必要なケース（最大60秒の伝搬遅延あり）

## 結果整合性の仕組み（必須セクション）

Workers KVはEventually Consistent（結果整合）モデルを採用する。書込みは中央データセンターに集約された後、世界中のエッジへ非同期にレプリケートされる。各エッジには直近のリードキャッシュが保持され、デフォルトで最大60秒間は古い値が返却される可能性がある。

挙動の要点:

- 書込み直後の同一キー読み込みでも、別リージョンでは旧値が返ることがある
- `cacheTtl`を短くすればフレッシュさは増すが、オリジン読み込みが増えコストとレイテンシが上がる
- 同一キーへの書込みは1秒1回までに制限される
- 強整合が必要な値はWorkers KVに置かず、Durable Objectsへ寄せる（KVはあくまで読込最適化レイヤ）

リード戦略の指針:

- 全エッジで完全一致が必要 → Workers KV不適合
- 「数十秒以内に伝搬すれば良い」 → Workers KVが最適
- 書込み元と読み込み元が同じWorker実行内 → ローカル変数や`waitUntil`でカバー

## 競合・代替（DynamoDB / Redis / Memcached / Durable Objects / D1）

| 観点 | Workers KV | DynamoDB | Redis (ElastiCache) | Durable Objects | D1 |
|---|---|---|---|---|---|
| 配置 | グローバル分散（自動） | リージョン（Global Tables有） | リージョン | グローバル単一インスタンス | リージョン分散 |
| 整合性 | 結果整合（最大60秒） | 強整合オプション有 | 強整合 | 強整合 | 強整合 |
| クエリ | Key-Value + プレフィックスリスト | KV + GSI/LSI | 多様なデータ構造 | 任意ロジック | SQL |
| 書込みレート | 同一キー1/秒 | 高スループット | 非常に高い | シングルライタ | 中 |
| 値サイズ上限 | 25 MiB | 400 KB | メモリ依存 | 128 KiB（KV API） | カラム制限内 |
| 料金 | 読込 $0.50/M、書込 $5/M | 読込/書込ユニット課金 | インスタンス時間課金 | リクエスト+期間課金 | 行スキャン課金 |
| 主用途 | グローバル設定・キャッシュ | OLTP | セッション・キャッシュ | 強整合カウンタ・状態 | リレーショナル |

選定の指針: 「グローバル読込重視・結果整合OK」ならKV、「強整合の状態管理」ならDurable Objects、「リレーショナル」ならD1、「大容量オブジェクト」ならR2。

## 料金モデルの要点

Free / Paidプランで無料枠と従量課金が異なる。

- 読込: 100,000/日（Free）/ 1000万/月、超過分$0.50/100万（Paid）
- 書込: 1,000/日（Free）/ 100万/月、超過分$5.00/100万（Paid）
- 削除: 1,000/日（Free）/ 100万/月、超過分$5.00/100万（Paid）
- リスト: 1,000/日（Free）/ 100万/月、超過分$5.00/100万（Paid）
- ストレージ: 1 GB / 1 GB+ $0.50/GB-月

ポイント:

- データ転送（egress）課金なし
- 存在しないキーへのGETも課金対象（404でも操作回数にカウント）
- バルク読込は読み込んだキー数で課金
- ダッシュボード・wrangler経由の操作も課金対象
- 書込みコストが読込の10倍。書込み頻度が高いワークロードは設計を見直す

## CLI / IaC 操作例

```bash
# ネームスペース作成
wrangler kv namespace create "MY_KV"

# プレビュー用ネームスペース作成
wrangler kv namespace create "MY_KV" --preview

# キー書込み
wrangler kv key put --binding=MY_KV "user:123" '{"plan":"pro"}'

# TTL付き書込み（60秒で失効）
wrangler kv key put --binding=MY_KV "session:abc" "token" --ttl 60

# キー読込
wrangler kv key get --binding=MY_KV "user:123"

# キー削除
wrangler kv key delete --binding=MY_KV "user:123"

# プレフィックス指定リスト
wrangler kv key list --binding=MY_KV --prefix "user:"

# バルク書込み（JSONファイル）
wrangler kv bulk put --binding=MY_KV ./data.json
```

`wrangler.jsonc`でのバインディング定義:

```jsonc
{
  "kv_namespaces": [
    {
      "binding": "MY_KV",
      "id": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
      "preview_id": "yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy"
    }
  ]
}
```

Workers内での利用:

```typescript
export default {
  async fetch(request, env): Promise<Response> {
    await env.MY_KV.put("KEY", "VALUE", { expirationTtl: 3600 });
    const value = await env.MY_KV.get("KEY", { cacheTtl: 60 });
    const list = await env.MY_KV.list({ prefix: "user:" });
    await env.MY_KV.delete("KEY");
    return new Response(value);
  },
} satisfies ExportedHandler<{ MY_KV: KVNamespace }>;
```

## 制限・注意点

| 項目 | 制限値 |
|---|---|
| キーサイズ | 512バイト |
| 値サイズ | 25 MiB |
| キーメタデータ | 1024バイト |
| 同一キーへの書込み | 1秒に1回 |
| 異なるキーへの書込み（Free） | 1,000/日 |
| 1Worker起動あたりのオペレーション | 1,000 |
| アカウントあたりネームスペース数 | 1,000 |
| ストレージ（Free） | 1 GB |
| `cacheTtl`最小値 | 30秒 |

注意点:

- 同一キーの高頻度書込みは構造的に不可能。カウンタや在庫管理には使わない
- Free planでは1日1,000書込み制限があり、本番運用前提ならPaid必須
- 書込み伝搬は最大60秒、強整合を期待するコードは書かない
- 1 Worker呼び出しで1,000オペレーションを超える設計はバルクAPIに切り替える
- REST APIはCloudflare REST APIのレートリミットが別途適用される

## 参考リンク

- [Workers KV Overview](https://developers.cloudflare.com/kv/)
- [KV Limits](https://developers.cloudflare.com/kv/platform/limits/)
- [KV Pricing](https://developers.cloudflare.com/kv/platform/pricing/)
- [Workers Binding API](https://developers.cloudflare.com/kv/api/)
- [KV REST API](https://developers.cloudflare.com/api/operations/workers-kv-namespace-list-namespaces)

---
参照日: 2026-05-03
