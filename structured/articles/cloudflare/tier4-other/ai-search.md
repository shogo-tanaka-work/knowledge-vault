# AI Search & AI Crawl Control

## 一行サマリ
AI Searchは、R2バケット・任意Webサイト・直接アップロードしたファイルを自動でチャンク・埋め込みしてVectorizeにインデックスし、ハイブリッド検索／リランキング／回答生成までを単一インスタンスで提供するマネージドRAGサービスであり、AI Crawl Controlは、その逆方向、つまり「自分のサイトに来るAIクローラ」をBot Managementの識別基盤の上で可視化・許可ブロック・課金（Pay per crawl, HTTP 402）するコントロールパネルである。RAGを「作る側」と「クロールされる側」の両端を、Cloudflareがエッジで一体化して扱う。

## 解決する課題（Why）
LLMの応答精度を業務データで底上げするには「RAG（Retrieval-Augmented Generation）」が事実上の標準だが、これを自前で組むと、データソースの差分取り込み、PDF/HTMLからのテキスト抽出、チャンキング、埋め込みモデル呼び出し、ベクタDB運用、ハイブリッド検索、リランキング、コンテキスト組み立て、LLM呼び出し、という7〜8段の配管を構築・維持しなければならない。各レイヤを別ベンダーで組むと、認証・コスト・レイテンシ・データ転送料が累積して破綻しやすい。AI Search（旧AutoRAG）はこのスタック全体を1インスタンスにまとめ、ソースを指定するだけで動く形に圧縮する。

一方で、AIクローラ問題は逆方向の課題である。GPTBot / ClaudeBot / PerplexityBot / Google-Extended などが大量にコンテンツを取得し、サイト運営者は帯域コストとオリジン負荷を負担しながら、自分のコンテンツがどう使われたかを把握できない。robots.txtは紳士協定であり、無視するクローラも多い。AI Crawl Controlは、Cloudflare Bot Managementが既に持っている「正規Botの一次ソース識別」を流用し、AIクローラだけを切り出して可視化・ブロック・課金する。Pay per crawlは「払えば通す、払わなければ402を返す」という新しい交渉プロトコルで、コンテンツ提供者が初めて主体的に値付けできる。

要するに、AI Searchは「自社データをLLMに食わせる側」の運用負荷を、AI Crawl Controlは「LLMにデータを食われる側」の経済的・技術的非対称を、それぞれエッジで解消する。両者は対になっており、Cloudflareが「AIインターネットの双方向ゲートウェイ」を取りに行っているプロダクトである。

## 主要機能（What）

### AI Search Pipeline（マネージドRAG）
インスタンスを作成すると、データソース取り込み → チャンキング → 埋め込み生成 → Vectorize書き込み → クエリ書き換え → ベクタ／キーワード検索 → リランキング → 回答生成、という8段のパイプラインが自動で組み上がる。各段はインスタンス作成後も編集可能で、埋め込みモデルだけは作成時に固定（インデックスとモデルが1対1）になる。

- **インデックス更新**：データソースを継続監視して差分を再取り込みする「Automated Indexing」を内蔵。手動再同期も可能。
- **Hybrid Search**：ベクタ検索（意味）とBM25キーワード検索（厳密一致）を同一クエリで合成。スコア閾値・件数を指定できる。
- **Retrieval type**：`hybrid` / `vector` / `keyword` の3モードをクエリ時に切替可能。
- **Metadata filtering**：チャンクに付与した任意メタデータ（カテゴリ・バージョン・言語・テナントID等）に対し`eq / ne / gt / gte / lt / lte`の演算子で絞り込み。

### Sources（R2 / Webサイト / 直接アップロード）
取り込み元は3種類。

- **R2 Bucket**：PDF / Markdown / HTML / プレーンテキスト等をR2に置けば、Path filterで対象を限定しつつ取り込み。最も標準的な使い方。
- **Website（Web Crawler）**：自分の管理ドメインに対し、AI Search内蔵のクローラを差し向けて自動収集する。2026年4月以降の新規インスタンスは「managed storage, vector index, and web crawling」が同梱され、外部ストレージなしで完結する。
- **Direct Upload**：API経由で個別ファイルをインスタンスに直投入。ユーザー単位・テナント単位で動的にコーパスを作るユースケース（per-tenant search）に向く。

### Embedding & Vectorize 連携
埋め込みはWorkers AI上のモデル（`@cf/baai/bge-*`系など）を呼び出して生成され、結果は裏側でCloudflare Vectorizeに格納される。利用者からは「Vectorizeを直接触らずに済む抽象化」として提供されるが、料金面ではVectorize（dimensions × vectors stored / queried）の従量が背後で走っているため、コスト試算では意識する必要がある。

### Re-ranking
ベクタ検索の上位候補を、別の小型クロスエンコーダ系モデルで再スコアリングして並べ直す機能。リコールが大きいインデックスでも、最終的にLLMに渡るチャンク数を絞り込みつつ精度を上げられる。リランキング用モデルもインスタンス設定で差し替え可能。

### Generation（chatCompletions）
Workers Bindingの`chatCompletions()`またはREST APIで「検索＋回答生成」を1呼び出しで実行できる。検索したチャンクを自動でコンテキストに差し込み、System Promptをカスタマイズし、`stream: true`でストリーミング応答も返せる。クエリ書き換え（過去ターンを踏まえてユーザー質問をリライト）もここに統合されている。

### MCP & Embeddable UI
各インスタンスはMCPエンドポイントを自動公開するため、ClaudeやChatGPTなどのMCP対応エージェントから「ツール」としてそのまま検索できる。さらに埋め込み可能なSearch UIコンポーネントも用意され、社内ポータル等にコピペで貼れる。

### AI Crawl Control（識別とポリシー）
Cloudflareが既存のBot Managementで蓄積している「正規Botのフィンガープリント＋IPレンジ＋User-Agent」のデータベースから、AI関連クローラ（GPTBot / ChatGPT-User / ClaudeBot / Claude-Web / PerplexityBot / Google-Extended / CCBot / Amazonbot / Bytespider など）を切り出して、専用ダッシュボードで可視化する。

- **ポリシー**：個別クローラ単位、または「すべてのAIクローラ」単位で `Allow / Block / Challenge` を設定。
- **robots.txtコンプライアンス追跡**：「robots.txtで拒否しているのに来ているクローラ」をハイライトし、ルール違反者にだけブロックを適用といった運用ができる。
- **トラフィック分析**：どのクローラがどのパスをどれだけ叩いているかをパス単位・時系列で確認可能。

### Pay per crawl
コンテンツ単価をサイト側が設定し、AIクローラがそれを払えば通す、払わなければ`HTTP 402 Payment Required`を返す、という課金プロトコル。CloudflareがAI事業者との決済を仲介し、サイト所有者にレベニューシェアされる。出版社・ニュースメディア・教育コンテンツ事業者向けのマネタイズ機能で、現状ベータ。

## アーキテクト視点：いつ選ぶか

### 適しているシーン
- **AI Search**：すでにR2でドキュメント・社内マニュアル・カスタマーサポート記事を保管している、または自社サイトをそのままナレッジベース化したい組織。RAG配管を自前運用する人員がない。
- **AI Search**：MCPサーバとしてエージェントから検索を呼びたいケース。Workers Binding／REST API／MCP／埋め込みUIを横並びで使い分けたいプロダクト。
- **AI Search**：マルチテナントSaaSで「テナントごとに独立したインデックス」を動的に作って捨てる必要があるユースケース（namespace bindingで最大10インスタンスを束ねられる）。
- **AI Crawl Control**：すでにCloudflareプロキシ配下にあるメディア・出版・ドキュメントサイトで、AIクローラの帯域消費とコンテンツ流出を可視化したい組織。
- **AI Crawl Control**：robots.txtに`Disallow`を書いても無視されている疑いがあり、技術的にブロックする必要があるケース。
- **Pay per crawl**：高品質コンテンツを抱え、AI事業者からの収益化交渉力を上げたい大手メディア。

### 適していないシーン
- **AI Search**：1日数千万チャンクを超える超大規模インデックス、または1ms未満のレイテンシ要件。マネージドである以上チューニング自由度は限定される。Vectorizeを直接、もしくはPinecone / Qdrantを使う方が適する。
- **AI Search**：Cloudflare以外のLLM（Anthropic API、OpenAI API、Bedrock）を生成側に使い、検索だけ別ベンダーに置きたい場合は、`search()`のみ使って自前でLLMに渡す形になり、`chatCompletions()`の旨味が薄れる。
- **AI Crawl Control**：Cloudflareをプロキシ経由していない（DNSのみ）サイト。トラフィックがエッジを通らないため識別もブロックも効かない。
- **Pay per crawl**：個人ブログレベルのトラフィックでは交渉力もレベニューシェアも実額が立たない。エンタープライズメディア向けの機能と割り切る。

## 競合・代替

| 観点 | Cloudflare AI Search | OpenAI Assistants File Search | Pinecone Assistant | Vertex AI Search | Amazon Kendra | Algolia AI Search | Elastic ESRE |
|---|---|---|---|---|---|---|---|
| 出自 | エッジ統合マネージドRAG（旧AutoRAG） | OpenAI純正RAG（Assistants API） | Pinecone上のマネージドRAG | Google Cloud純正Enterprise Search | AWS純正Enterprise Search | サイト内検索SaaSのAI拡張 | Elasticsearch + AIツール群 |
| データ取り込み | R2 / Webクロール / 直接Upload | ファイルUpload | ファイル / URL Upload | GCS / BigQuery / Web / 多数 | S3 / SharePoint / RDS等 | 各種コネクタ | 各種Beats / Logstash / Connector |
| ベクタDB | Vectorize（同梱） | OpenAI管理（不可視） | Pinecone | Vertex Vector Search | Kendra内蔵 | Algolia独自 | Elasticsearch dense_vector |
| ハイブリッド検索 | ◯（Vector + BM25） | △（Vector中心） | ◯ | ◯ | ◯ | ◯（Algoliaの強み） | ◯ |
| リランキング | ◯（差し替え可） | △ | ◯ | ◯ | ◯ | ◯ | ◯（ELSER等） |
| MCPエンドポイント | 標準提供 | × | × | × | × | × | × |
| LLM生成統合 | Workers AI連携 | 同社GPT固定 | 任意LLM | Geminiに最適化 | 任意LLM | 任意LLM | 任意LLM |
| 強み | エッジ実行・低レイテンシ・配管不要 | OpenAIエコシステム密結合 | ベクタDBの成熟度 | GCPデータ資産との統合 | 企業データソースの広さ | UX・ファセット検索の作り込み | OSS資産・運用知見 |
| 弱み | Beta、モデル選択の幅は限定 | 透明性低・コスト不透明 | RAG配管は別途必要 | GCP前提・複雑 | 高コスト・複雑 | RAG（生成）は外付け | 自前運用負荷 |

AI Searchの本質的な独自性は「Vectorize / Workers AI / R2 / Workersをエッジで束ねた1パッケージ」であり、特にWorkers BindingからLLM呼び出しまで往復ゼロ・ネットワーク跨ぎゼロでRAGを完結できる点は、他クラウドのRAGスタックでは到達しづらい。一方で、エンタープライズコネクタ（SharePoint・Salesforce・Confluence等）の品揃えはKendra / Vertex AI Searchが圧倒的に厚い。

AI Crawl Controlに直接対応する商用プロダクトは現状ほぼ存在せず、`DataDome` / `HUMAN`（旧PerimeterX）等のBot対策SaaSがAIクローラ識別を強化しつつある段階。Pay per crawlに至ってはCloudflare独自で、`TollBit`のようなスタートアップが類似モデルを提供する程度である。

## 料金

AI Searchは複数コンポーネントの合算課金で、以下の各レイヤが個別に従量化される。

- **Workers AI（埋め込み生成 + 生成 + リランキング + クエリ書き換え）**：呼び出すモデルごとにNeurons課金。インデックス時の埋め込み生成、クエリ時の埋め込み生成、リランキング、回答生成すべてが累積する。
- **Vectorize**：保管ベクタ数 × dimensions と、クエリ時のベクタ読み出し量で課金。AI Searchが背後で消費する。
- **R2**：データソース側のストレージ＋取り込み時のClass Aオペレーション。2026年4月以降の新規インスタンスは「managed storage」を選べばここはAI Search内に内包される。
- **Search Query**：AI Search固有のクエリ単価が別途加算される（料金表は`AI Search → Limits & Pricing`を参照）。
- **Workers**：Worker経由でクエリを叩くなら通常のWorkers Requests / CPU Time。

つまり「埋め込み生成のNeurons」「Vectorizeの保管／クエリ」「Search Query単価」「LLM生成のNeurons」の4本立てで見積もるのが実務的である。最新値はダッシュボードの`AI Search → 該当インスタンス → Pricing`で必ず実測すること。

AI Crawl Control本体は、Cloudflareプロキシ配下のZoneであれば基本機能（識別ダッシュボード・Allow/Block・robots.txt追跡）は無料〜既存プラン込みで提供される。Pay per crawlはベータで、課金フローが回り始めればAI事業者からの支払いに対するレベニューシェアモデルとなる。Bot Managementの上位機能（高度なヒューリスティック、ML Botスコア）はEnterpriseプランの`Bot Management`アドオンが前提なので、識別精度を上げるならそこと組み合わせる設計になる。

## CLI / API 例

### AI Search インスタンス作成（wrangler）
```bash
# R2バケットをソースにしたインスタンスを作成
wrangler ai-search create my-knowledge \
  --source-type=r2 \
  --r2-bucket=docs-bucket \
  --embedding-model=@cf/baai/bge-base-en-v1.5 \
  --generation-model=@cf/meta/llama-3.3-70b-instruct \
  --rerank-model=@cf/baai/bge-reranker-base

# Webサイトをクロールするインスタンス
wrangler ai-search create my-site-rag \
  --source-type=website \
  --site-url=https://docs.example.com \
  --include-paths="/guide/*,/api/*"
```

### Workers Binding（wrangler.toml）
```toml
compatibility_date = "2026-03-27"

# 単一インスタンスにバインド
[[ai_search]]
binding = "MY_SEARCH"
instance_name = "my-knowledge"

# Namespace全体にバインド（最大10インスタンスを動的にlist/get）
[[ai_search_namespaces]]
binding = "TENANT_SEARCH"
namespace = "tenants"
```

### Worker からのクエリ（search + chatCompletions）
```ts
export default {
  async fetch(req: Request, env: Env): Promise<Response> {
    const { query } = await req.json<{ query: string }>();

    // 1. 検索のみ（ベクタ＋BM25のハイブリッド、メタデータでフィルタ）
    const hits = await env.MY_SEARCH.search({
      query,
      retrieval_type: "hybrid",
      max_num_results: 8,
      score_threshold: 0.5,
      rewrite_query: true,
      rerank: true,
      filters: { language: { eq: "ja" }, version: { gte: 3 } },
    });

    // 2. 検索 + LLM応答生成（ストリーミング）
    const stream = await env.MY_SEARCH.chatCompletions({
      messages: [{ role: "user", content: query }],
      stream: true,
      system_prompt: "あなたは社内ナレッジに基づいて回答するアシスタントです。",
    });

    return new Response(stream, {
      headers: { "content-type": "text/event-stream" },
    });
  },
};
```

### REST API（外部システムからのクエリ）
```bash
curl -X POST \
  -H "Authorization: Bearer $CF_API_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{
    "query": "Workers KVとR2の使い分けは？",
    "retrieval_type": "hybrid",
    "max_num_results": 5,
    "rerank": true
  }' \
  "https://api.cloudflare.com/client/v4/accounts/$ACCOUNT_ID/ai-search/instances/my-knowledge/search"
```

### AI Crawl Control ルール（REST API）
```bash
# 全AIクローラに対するブロックルールを作成
curl -X POST \
  -H "Authorization: Bearer $CF_API_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{
    "action": "block",
    "scope": "all_ai_crawlers",
    "description": "Block all AI crawlers by default"
  }' \
  "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/ai-crawl-control/rules"

# 特定クローラだけ許可（GPTBot / ClaudeBotは通す）
curl -X POST \
  -H "Authorization: Bearer $CF_API_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{
    "action": "allow",
    "crawlers": ["GPTBot", "ClaudeBot"],
    "description": "Allow OpenAI and Anthropic only"
  }' \
  "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/ai-crawl-control/rules"
```

### Pay per crawl（HTTP 402を返す設定例）
```bash
# 1ページあたりの単価を設定（USD）してPay per crawlを有効化
curl -X PUT \
  -H "Authorization: Bearer $CF_API_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{
    "enabled": true,
    "price_per_request_usd": 0.001,
    "applicable_paths": ["/articles/*"],
    "fallback_action": "402"
  }' \
  "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/ai-crawl-control/pay-per-crawl"
```

## 制限・注意点
- **AI SearchはBeta**（2026-05時点）。SLAは未提供で、APIシグネチャや課金体系は変更され得る。プロダクションで使うなら、`search()`の戻り値型を抽象化レイヤで包んでベンダー依存を局所化しておく。
- **埋め込みモデルはインスタンス作成時に固定**。後から変更すると全チャンクの再埋め込みが必要なため、最初のモデル選定を慎重に行う（多言語が必要なら`bge-m3`系、英語特化なら`bge-base-en-v1.5`等）。
- **対応モデルはWorkers AIのカタログ依存**。`@cf/baai/bge-*` / `@cf/meta/llama-*` / `@cf/google/gemma-*` 等、Workers AI側で提供されているモデルが順次取り込まれる。OpenAI埋め込み（`text-embedding-3-large`等）は直接は使えない。
- **リージョン**：Cloudflareのグローバルエッジ上で動作するが、Workers AIのGPUリージョンはまだ全PoPに行き渡っておらず、推論は最寄りのGPU PoPにルーティングされる。データレジデンシー要件があるEU等では、Vectorizeおよび埋め込み実行がEU内に閉じる構成かを確認する必要がある。
- **インデックス再同期のタイミング**：Automated Indexingは「継続的」だが、ニアリアルタイムではなく数分〜数十分のラグがある。投稿直後の新着記事をすぐ検索したいなら、明示的な再同期APIを叩く設計が必要。
- **AI Crawl Controlの識別精度はBot Management依存**。User-Agent詐称＋住宅プロキシ経由のスクレイパは、Bot Managementの上位プラン（ML Score / JA3 / JA4フィンガープリンティング）がないと完全には捕捉できない。
- **Pay per crawlはベータ**かつAI事業者側の対応が前提。GPTBot / ClaudeBot等が決済プロトコルに対応していなければ、現状は単純に402で拒否されるだけになる。導入前に対応状況を確認する。
- **robots.txtは依然として必要**。AI Crawl Controlでブロックしてもrobots.txtを更新していなければ「正直なクローラ」も巻き込んで止めることになる。技術ブロックと宣言（robots.txt / `ai.txt` / `llms.txt`）はセットで運用する。
- **MCP公開時の認可**：AI SearchインスタンスのMCPエンドポイントを外部エージェントに開放する場合、トークンスコープ・レート制限・テナント分離を必ず噛ませる。社内データが他テナントに漏れる経路になり得る。

## 参考リンク
- AI Search Overview：https://developers.cloudflare.com/ai-search/
- AI Search Configuration：https://developers.cloudflare.com/ai-search/configuration/
- AI Search Workers Binding：https://developers.cloudflare.com/ai-search/usage/workers-binding/
- AI Crawl Control Overview：https://developers.cloudflare.com/ai-crawl-control/
- Pay per crawl：https://developers.cloudflare.com/ai-crawl-control/features/pay-per-crawl/
- Workers AI（埋め込み・生成モデル）：https://developers.cloudflare.com/workers-ai/
- Vectorize：https://developers.cloudflare.com/vectorize/
- Bot Management：https://developers.cloudflare.com/bots/
- Cloudflare AI Search product page：https://www.cloudflare.com/developer-platform/products/ai-search/
- llms.txt（AI Crawl Control）：https://developers.cloudflare.com/ai-crawl-control/llms.txt

---
参照日: 2026-05-04
