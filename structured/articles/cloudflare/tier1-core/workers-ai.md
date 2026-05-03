# Workers AI

## 一行サマリ
Cloudflareのグローバルネットワーク上のサーバーレスGPUで、Llama・Mistral・Whisper等のOSSモデルを推論実行できるAIプラットフォーム。

## 解決する課題（Why）
自前GPUの調達・スケーリング・遊休コストといったAI推論基盤の運用負担を排除する。Workers/Pagesと同じエッジ拠点で推論が走るため、別クラウドのLLM APIを呼ぶ場合に発生する追加レイテンシとエグレス費用を回避できる。アイドル時の課金がない従量課金（Neurons）で、PoCから本番までインフラ設計を書き換えずにスケールできる。

## 主要機能（What）
- Text Generation：Llama 3/4、Mistral、Qwen、Gemma、DeepSeek、GPT-OSS、Kimi等のチャット/指示モデル
- Text Embeddings：BGE系、Qwen3-Embedding、PLaMo Embedding等
- Image Generation：FLUX 1/2、Leonardo Lucid Origin、Phoenix
- Speech：Whisper（ASR）、MeloTTS、Deepgram Aura/Nova/Flux（TTS・STT、WebSocket対応）
- Translation：m2m100、IndicTrans2
- Classification / Object Detection / Reranker / Vision LLM
- Function calling・Reasoning・Vision入力対応モデルあり
- AI Gateway / Vectorize / Workers / Durable Objects との統合

## 提供モデル抜粋
カタログ総数97モデル（2026-05時点）。代表例:
- Llama 3.1/3.2/3.3、Llama 4 Scout 17B（MoE）、Llama Guard 3
- Mistral 7B、Mistral Small 3.1 24B
- Qwen 2.5 Coder 32B、QwQ 32B、Qwen3 30B-A3B
- DeepSeek-R1-Distill-Qwen-32B
- GPT-OSS 20B/120B（OpenAIオープンウェイト）
- Gemma 3 12B / Gemma 4 26B-A4B
- Kimi K2.5 / K2.6（Moonshot、1Tパラメータ・262k context）
- GLM-4.7-Flash（Zhipu）
- Whisper / Whisper-large-v3-turbo
- BGE Embeddings（small/base/large/m3）

## アーキテクト視点：いつ選ぶか
### 適しているシーン
- OSSモデルで要件を満たせるユースケース（チャットボット、要約、RAG、埋め込み生成、画像生成、文字起こし）
- Workers / Pages と同居させてエッジ近接で推論したい構成
- アイドル時間が長く従量課金のメリットが大きい用途
- データ主権の理由でCloudflareネットワーク内で完結させたい場合
- Vectorize + Workers AI で完結するRAGパイプライン

### 適していないシーン
- GPT-5、Claude Sonnet 4.5、Gemini 3 Pro等のフロンティアモデルが必須の用途 → AI Gateway経由でOpenAI/Anthropic/Google直結が妥当
- 大規模ファインチューニング（LoRA対応はあるが基盤学習は不可）
- 1分あたり数千req超のText Generationを単一プランで張り付かせる用途（task type別レート制限あり）
- リアルタイム性極端に厳しい音声対話（一部モデルはWebSocket対応だが選択肢は限定的）

## 競合・代替

| 観点 | Workers AI | OpenAI API | AWS Bedrock | Replicate | Together / Groq |
|---|---|---|---|---|---|
| モデル | OSS中心97種 | GPT-4o/5、o系 | Anthropic/Meta/Mistral等マルチ | OSS幅広い | OSS中心 |
| デプロイ拠点 | Cloudflareエッジ | 米国中心 | AWSリージョン | 集約GPU | 集約GPU |
| エッジ統合 | Workers同居で最強 | 別ネットワーク | AWS内なら強 | 弱 | 弱 |
| 課金 | Neurons従量 | トークン従量 | トークン従量 | 秒課金 | トークン従量 |
| フロンティアモデル | × | ◎ | ◎（Claude） | △ | △ |
| OSS最新追従 | ○（gpt-oss・Kimi等迅速） | × | ○ | ◎ | ◎ |
| 無料枠 | 10,000 Neurons/日 | なし | なし | 限定 | 限定 |

## 料金モデルの要点
- 単価：**$0.011 / 1,000 Neurons**（バックエンドはNeurons課金、UIは$/トークン換算で表示）
- 無料枠：**全プランで10,000 Neurons/日**、UTC 0時リセット
- Workers Free：無料枠超過分は不可、Paidへアップグレード必須
- Workers Paid：無料枠超過分を $0.011/1k Neurons で従量課金
- モデル例（M=百万トークン）:
  - Llama 3.1 8B fp8-fast：input $0.045/M、output $0.384/M
  - Llama 3.3 70B fp8-fast：input $0.293/M、output $2.253/M
  - GPT-OSS 120B：input $0.350/M、output $0.750/M
  - Kimi K2.6：input $0.95/M、cached input $0.16/M、output $4.00/M
  - BGE-large-en-v1.5：$0.204/M input
  - Whisper：$0.0005/audio min
  - FLUX-1-schnell：$0.0000528/512x512タイル + $0.0001056/step

## CLI / IaC 操作例
**wrangler.jsonc**
```jsonc
{
  "name": "my-worker",
  "main": "src/index.ts",
  "compatibility_date": "2026-05-01",
  "ai": { "binding": "AI" }
}
```

**Worker内呼び出し**
```ts
export default {
  async fetch(req, env) {
    const res = await env.AI.run("@cf/meta/llama-3.1-8b-instruct-fp8-fast", {
      messages: [
        { role: "system", content: "あなたは簡潔に答えるアシスタントです。" },
        { role: "user", content: "Workers AIとは？" }
      ]
    });
    return Response.json(res);
  }
} satisfies ExportedHandler<{ AI: Ai }>;
```

**Embeddings + Vectorize**
```ts
const { data } = await env.AI.run("@cf/baai/bge-m3", { text: ["RAG用テキスト"] });
await env.VEC.insert([{ id: "1", values: data[0] }]);
```

**REST API（外部から）**
```bash
curl https://api.cloudflare.com/client/v4/accounts/$ACCOUNT/ai/run/@cf/meta/llama-3.1-8b-instruct \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"prompt":"Hello"}'
```

## 制限・注意点
- **Rate Limit（task type別、デフォルト/分）**:
  - Text Generation：300（モデル別に150〜1500の例外あり）
  - Text Embeddings：3000（bge-large-en-v1.5は1500）
  - Text-to-Image：720（SD v1.5 img2imgは1500）
  - Automatic Speech Recognition / Translation / Image-to-Text：720
  - Image Classification / Object Detection：3000
  - Summarization：1500、Text Classification：2000
- ローカル開発（`wrangler dev`）の推論もレート制限にカウントされる
- Beta段階のモデルはレート制限が低い場合あり
- 上限緩和・プライベートカスタムモデルはCustom Requirements Formで個別交渉
- フロンティアモデル不在：高度な推論・長文context・最新ベンチ最強系は別系統が必要

## AI Gateway との併用
Workers AIだけでフロンティアモデル要件を満たせない場合、**AI Gateway** をフロントに置きOpenAI/Anthropic/Bedrock/Vertex/Workers AIへルーティングする構成が定石。
- キャッシュ（同一プロンプトの再利用でコスト削減）
- レート制限・リトライ・モデルフォールバック（OpenAI障害時にWorkers AIへ自動切替）
- ログ・分析・コスト可視化を一元化
- Workers AI自体もAI Gatewayの`run`オプションでgateway経由実行可能

典型構成: Workers → AI Gateway → (Workers AI / OpenAI / Anthropic) → Vectorize で記憶。

## 参考リンク
- 公式トップ: https://developers.cloudflare.com/workers-ai/
- モデルカタログ: https://developers.cloudflare.com/workers-ai/models/
- Pricing: https://developers.cloudflare.com/workers-ai/platform/pricing/
- Limits: https://developers.cloudflare.com/workers-ai/platform/limits/
- 統合AIモデルカタログ: https://developers.cloudflare.com/ai/models/

---
参照日: 2026-05-03
