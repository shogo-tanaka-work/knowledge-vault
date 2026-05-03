# Vectorize

## 一行サマリ
Cloudflare Workersから低レイテンシで利用できるグローバル分散型ベクトルデータベース。RAG・セマンティック検索・レコメンド用途のembedding保存とANN検索を担う。

## 解決する課題（Why）
LLMアプリケーションで「自社データに基づく回答」を実現するには、テキストや画像をembedding化してベクトル検索する基盤が必要となる。PineconeやWeaviateは別クラウドに置く必要があり、Workersから呼ぶたびに外部APIへのレイテンシ・egress・別契約・別IAMが発生する。Vectorizeはこの構成を「Workersバインディング1本」に圧縮し、Workers AI（embedding生成）・R2（原本ファイル）・D1（メタ情報）と同一ネットワーク内で完結させる。インフラ運用ゼロ、egress無料、従量課金で小さく始められる点が本質的な価値である。

## 主要機能（What）
- **インデックス（Index）**: ベクトル集合の単位。作成時に次元数（dimensions）と距離関数（cosine / euclidean / dot-product）を固定する。
- **名前空間（Namespace）**: 1インデックス内で論理分割する仕組み。マルチテナントSaaSでテナント分離に使う。
- **メタデータフィルタ**: ベクトルにJSONメタデータを紐付け、`metadataIndexes`を作成すれば`filter`句で事前絞り込みができる（例: `tenant_id`、`lang`、`published_after`）。
- **メタデータインデックス**: フィルタ高速化のため明示的にインデックス対象フィールドを宣言する。1インデックスあたり最大10件。
- **upsert / query / getByIds / deleteByIds / list**: 基本CRUD。Workers内ではバインディング経由、外部からはREST APIで操作可能。
- **Workers AIとの直結**: `@cf/baai/bge-base-en-v1.5`等のembeddingモデルが同一プラットフォーム上で動く。
- **AI Search（旧AutoRAG）連携**: R2に置いたドキュメントを自動チャンク化→embedding→Vectorize格納→検索までをマネージドで提供。

## アーキテクト視点：いつ選ぶか

### 適しているシーン
- Cloudflare Workers / Pages / Workers AI を主軸にしたAIアプリケーション
- 中小規模（〜1000万ベクトル/インデックス）のRAG、社内文書検索、商品レコメンド
- グローバルにエッジから低レイテンシで検索したいユースケース
- egress課金を避けたい・契約をCloudflare 1社に集約したい場合
- プロトタイピング〜本番初期段階で、運用ノードを抱えたくないケース

### 適していないシーン
- 1インデックスに1000万件超のベクトルを格納したい大規模検索基盤
- 1536次元を超える高次元embedding（OpenAI `text-embedding-3-large` の3072次元等）をネイティブで扱いたい場合（次元削減が必要）
- ハイブリッド検索（BM25＋ベクトル）やリランキングをDB側で完結させたい場合 → OpenSearchやWeaviateが優位
- 既存PostgreSQLにデータがあり、トランザクション整合性を保ったままベクトル検索したい場合 → pgvector
- HNSWパラメータ（efConstruction、M値）を細かくチューニングしたい高度ユーザー

## 競合・代替

| 観点 | Vectorize | Pinecone | pgvector | Qdrant |
|---|---|---|---|---|
| 提供形態 | サーバーレス（Workersバインディング） | フルマネージドSaaS | PostgreSQL拡張（自前/RDS等） | OSS / Cloud |
| 最大次元 | 1536 | 制限緩い（〜20000） | 2000（実用） | 制限緩い |
| 最大件数/Index | 1000万 | 数億〜 | DBサイズ依存 | ノード次第 |
| 距離関数 | cosine / euclidean / dot | cosine / euclidean / dot | 同左 | 同左＋manhattan |
| メタデータフィルタ | あり（要index宣言） | あり（柔軟） | SQL WHERE | 強力 |
| ハイブリッド検索 | なし | sparse-dense対応 | 別途FTS併用 | あり |
| 課金軸 | クエリ次元数＋保存次元数 | Pod時間 or サーバーレス読書 | DB料金 | ノード/リソース |
| エコシステム | Workers AI / R2 / D1 と同居 | LangChain等広く対応 | RDB資産流用 | OSS自由度 |
| egress | 無料 | あり | クラウド依存 | 構成次第 |

WeaviateはGraphQL中心でモジュラー、ChromaはローカルOSSで開発用途、Turbopufferは同じくサーバーレス＋オブジェクトストレージ型でVectorizeと最も思想が近い競合。OpenSearchはKNNプラグインで本格検索基盤を組む選択肢。

## 料金モデルの要点
- 課金軸は2つだけ: **クエリ次元数**と**保存次元数**。CPU・メモリ・インデックス数・active hoursは課金対象外。
- Workers Paid 月額無料枠: クエリ5000万次元、保存1000万次元。
- 超過分: クエリ $0.01 / 100万次元、保存 $0.05 / 1億次元。
- Workers Free 枠: クエリ3000万次元、保存500万次元。
- egress無料、HTTP API/CLIからのクエリも課金対象。空インデックスは保存課金ゼロ。
- 計算式: `((queried + stored) * dims * $0.01/1M) + (stored * dims * $0.05/100M)`
- 実例: 768次元 × 5万ベクトル × 月20万クエリ ≒ **$1.94 / 月**。1536次元 × 50万ベクトル × 月100万クエリで **$23.42 / 月**。

## CLI / IaC 操作例

### インデックス作成（wrangler）
```bash
# cosine距離、768次元（Workers AI bge-base-en-v1.5想定）
wrangler vectorize create my-rag-index \
  --dimensions=768 \
  --metric=cosine

# メタデータインデックス追加（filter高速化）
wrangler vectorize create-metadata-index my-rag-index \
  --property-name=tenant_id \
  --type=string
```

### wrangler.toml バインディング
```toml
[[vectorize]]
binding = "VECTORIZE"
index_name = "my-rag-index"

[ai]
binding = "AI"
```

### Worker内でのupsert・query
```typescript
export default {
  async fetch(req: Request, env: Env): Promise<Response> {
    const { query } = await req.json<{ query: string }>();

    // 1. クエリ文字列をembedding化（Workers AI）
    const { data } = await env.AI.run("@cf/baai/bge-base-en-v1.5", {
      text: [query],
    });
    const vector = data[0];

    // 2. Vectorizeに類似検索（メタデータフィルタ付き）
    const matches = await env.VECTORIZE.query(vector, {
      topK: 5,
      returnMetadata: "all",
      filter: { tenant_id: { $eq: "acme" } },
    });

    return Response.json(matches);
  },
} satisfies ExportedHandler<Env>;
```

## 制限・注意点
- **最大次元数: 1536** （float32）。OpenAI `text-embedding-3-large` (3072次元) はそのまま入らないため、`dimensions` パラメータで縮約するか別モデルを選ぶ。
- **インデックスあたり最大1000万ベクトル**。これを超える規模は別インデックス分割（テナント別 / 期間別）の設計が必要。
- **メタデータ上限: 1ベクトルあたり10KiB**。原本テキストはR2/D1に逃がし、Vectorizeにはポインタとフィルタ用フィールドのみ持たせる設計が定石。
- **メタデータインデックス上限: 10件 / インデックス**、1フィールドあたりインデックス対象データ最大64バイト。
- **topK上限: メタデータ込みで50件、メタデータなしで100件**。リランキング前提で広く取りたい場合は要工夫。
- **upsertバッチ: Workers経由1000件、HTTP API 5000件**。アップロードファイル最大100MB。
- **インデックスのスキーマは作成後変更不可**（次元数・距離関数）。embeddingモデル変更時はインデックス作り直しになる。
- **強整合性ではない**: upsert直後の即時クエリで取得できないことがある。書き込み後数秒の伝搬を見込む。
- 削除済みベクトルが課金対象に含まれるかなど、詳細は最新ドキュメントで都度確認。

## RAG構成例

### 構成
```
[ユーザー質問]
      │
      ▼
┌──────────────────────────────┐
│  Cloudflare Worker (Hono等)  │
└──────┬───────────────────┬───┘
       │ ①embed            │ ④回答生成
       ▼                   ▼
  Workers AI            Workers AI
 (bge-base-en-v1.5)   (llama-3.1等)
       │                   ▲
       │ ②query            │ ③context
       ▼                   │
   Vectorize ──── matches ─┘
       │
       │ メタデータに doc_id / r2_key
       ▼
       R2 (原本Markdown / PDF)
       D1 (権限・テナント情報)
```

### インジェスト側コード例
```typescript
// 1. R2のドキュメントを読む → チャンク分割
const obj = await env.R2.get("docs/policy.md");
const text = await obj!.text();
const chunks = splitIntoChunks(text, 500); // 500トークン目安

// 2. embedding一括生成
const { data: vectors } = await env.AI.run(
  "@cf/baai/bge-base-en-v1.5",
  { text: chunks }
);

// 3. Vectorizeへupsert
await env.VECTORIZE.upsert(
  vectors.map((values, i) => ({
    id: `policy-${i}`,
    values,
    metadata: {
      tenant_id: "acme",
      doc_id: "policy",
      chunk_index: i,
      r2_key: "docs/policy.md",
    },
  }))
);
```

### クエリ側コード例
```typescript
// 1. 質問をembed
const { data } = await env.AI.run("@cf/baai/bge-base-en-v1.5", {
  text: [userQuestion],
});

// 2. Vectorize検索（テナント分離をfilterで担保）
const { matches } = await env.VECTORIZE.query(data[0], {
  topK: 5,
  returnMetadata: "all",
  filter: { tenant_id: { $eq: tenantId } },
});

// 3. R2から原本チャンク取得 → プロンプト合成
const contexts = await Promise.all(
  matches.map(async (m) => {
    const obj = await env.R2.get(m.metadata!.r2_key as string);
    return await obj!.text();
  })
);

// 4. LLMに投入
const answer = await env.AI.run("@cf/meta/llama-3.1-8b-instruct", {
  messages: [
    { role: "system", content: "以下のコンテキストのみを根拠に回答せよ。" },
    { role: "user", content: `${contexts.join("\n---\n")}\n\nQ: ${userQuestion}` },
  ],
});
```

マネージドでよければ **AI Search（旧AutoRAG）** が上記パイプラインを一括代替する。R2バケットを指定すれば自動でチャンク化・embedding・Vectorize格納・更新監視まで担う。

## 参考リンク
- 公式トップ: https://developers.cloudflare.com/vectorize/
- Limits: https://developers.cloudflare.com/vectorize/platform/limits/
- Pricing: https://developers.cloudflare.com/vectorize/platform/pricing/
- Get started: https://developers.cloudflare.com/vectorize/get-started/intro/
- AI Search: https://developers.cloudflare.com/ai-search/
- Workers AI（embeddingモデル）: https://developers.cloudflare.com/workers-ai/models/

---
参照日: 2026-05-03
