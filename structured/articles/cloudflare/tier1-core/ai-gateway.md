# AI Gateway

## 一行サマリ
複数LLMプロバイダの前段に置くプロキシで、観測（ログ・分析・コスト追跡）、キャッシュ、レート制限、フォールバック、リトライ、ガードレールを1行のエンドポイント差し替えだけで提供するCloudflareのマネージドサービスである。

## 解決する課題（Why）
- マルチプロバイダ運用でログ・分析が分散し、横断的に「誰が・どのモデルで・いくら使ったか」を把握できない。
- プロバイダ障害やレート制限によるリクエスト失敗で、本番AI機能の可用性が落ちる。
- 同一プロンプトの重複呼び出しでトークン課金が膨らむ。
- アプリ側に直接APIキーを持たせると、悪用・暴走時のコスト爆発を止められない。
- 機密情報の流入・流出（PII等）に対するガードレールが各アプリ実装に依存する。

## 主要機能（What）
- **ロギング / コスト追跡**：リクエスト・レスポンス・トークン数・コストを自動保存し、ダッシュボードと分析APIから参照する。
- **キャッシュ**：標準キャッシュ（完全一致）に加え、セマンティックキャッシュ（意味的近似）でヒット率を引き上げる。Cache TTLは最大1か月。
- **レート制限**：ゲートウェイ単位でリクエスト数を制御し、暴走・コスト爆発を抑止する。
- **フォールバック**：プロバイダAが失敗したらBに自動切替し、可用性を確保する。
- **リトライ**：一過性エラーに対する自動再試行で成功率を底上げする。
- **ガードレール（DLP連携）**：Cloudflare One DLPプロファイルを共有し、入出力の機密検出・マスキングを行う。
- **データセット / Logpush**：保存ログを外部ストレージへエクスポートし、長期保管・他システム連携を可能にする。
- **Universal Endpoint**：単一エンドポイントから複数プロバイダを呼び分け、フォールバックチェーンを宣言的に定義できる。

## 対応プロバイダ
公式に対応するネイティブプロバイダ（2026-05時点）:

OpenAI / Anthropic / Workers AI / Amazon Bedrock / Google Vertex AI / Google AI Studio / Azure OpenAI / Mistral AI / Cohere / Groq / DeepSeek / Perplexity / Replicate / HuggingFace / OpenRouter / xAI (Grok) / Cerebras / Baseten / Cartesia / Deepgram / ElevenLabs / Fal AI / Ideogram / Parallel。

OpenAI互換SDKを使うプロバイダはOpenAI互換モードで透過的に通る。

## アーキテクト視点：いつ選ぶか

### 適しているシーン
- すでにCloudflareエコシステム（Workers / Pages / R2 / D1）でアプリを構築している。
- 複数LLMプロバイダを併用し、横断的な可観測性とフォールバックを最小工数で揃えたい。
- エッジに近い場所でキャッシュ・レート制限を効かせて、レイテンシとコストを同時に下げたい。
- DLP・監査ログ要件があり、Cloudflare One側のポリシーと統合したい。
- PoC段階で「とりあえず1行で観測層を入れたい」スタートアップ・社内ツール。

### 適していないシーン
- 評価実験（eval）、プロンプト管理、データセット運用まで含めたLLMOps全体を1ツールで賄いたい場合（LangSmith / Langfuse / Braintrustの方が深い）。
- プロンプトテンプレートのバージョン管理・A/Bテスト・人間レビューワークフローを重視する場合（Portkey / Helicone Promptsの方が機能が厚い）。
- オンプレ・閉域ネットワーク内で完結させたい場合（Cloudflareエッジを経由する前提が崩れる）。
- 1リクエスト25MBを超える巨大ペイロードを扱うユースケース。

## 競合・代替

| 観点 | AI Gateway | Helicone | Portkey | LangSmith |
|---|---|---|---|---|
| 提供形態 | マネージド（エッジ） | マネージド/OSS | マネージド/OSS | マネージド |
| 導入コスト | エンドポイント差し替え1行 | エンドポイント差し替え1行 | SDK or プロキシ | SDK埋め込み |
| キャッシュ | 標準＋セマンティック | あり | あり | なし（評価寄り） |
| フォールバック | あり（宣言的） | あり | あり（強力） | なし |
| プロンプト管理 | 弱い | あり | 強い | 強い |
| eval / トレース深掘り | 弱い | 中 | 中 | 強い |
| 価格 | 無料枠あり、従量 | 無料枠あり | 無料枠あり | 有料寄り |
| 強み | エッジ近接・Cloudflareスタック統合 | OSS・シンプル | ルーティング戦略 | LangChain連携・eval |

その他、OpenLLMetry（OpenTelemetryベースの計測ライブラリ）やBraintrust（eval特化）は補完的に併用されることが多い。

## 料金モデルの要点
- **本体は無料で利用可能**（全プランで提供）。Gateway数は無料プラン10/有料プラン20。
- 無料プラン：ログ保存はアカウント全体で10万件まで。
- 有料プラン：ゲートウェイあたり1000万ログまで。
- 上限到達時は「自動削除」または「保存停止」を選択。Logpushで外部退避可。
- セマンティックキャッシュ等の高度機能は従量課金がかかる場合があるため、料金ページで最新を確認する。

## CLI / IaC 操作例
ベースURLを差し替えるだけで導入できる。OpenAI SDKでの例:

```ts
import OpenAI from "openai";

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
  baseURL: "https://gateway.ai.cloudflare.com/v1/<ACCOUNT_ID>/<GATEWAY_ID>/openai",
});

const res = await openai.chat.completions.create({
  model: "gpt-4o-mini",
  messages: [{ role: "user", content: "hello" }],
});
```

Workers Bindingsでも利用可能:

```toml
# wrangler.toml
[ai]
binding = "AI"

[[ai_gateway]]
binding = "GATEWAY"
gateway_id = "my-gateway"
```

Universal Endpointでフォールバックチェーンを宣言:

```bash
curl https://gateway.ai.cloudflare.com/v1/<ACCOUNT_ID>/<GATEWAY_ID> \
  -H "Content-Type: application/json" \
  -d '[
    {"provider":"workers-ai","endpoint":"@cf/meta/llama-3.1-8b-instruct","headers":{...},"query":{...}},
    {"provider":"openai","endpoint":"chat/completions","headers":{...},"query":{...}}
  ]'
```

## 制限・注意点
- キャッシュ可能なリクエストサイズは25MB/リクエスト、Cache TTLは最大1か月。
- カスタムメタデータは1リクエストあたり5エントリまで。
- ログサイズは1ログ10MBまで（超過分は保存されない）。
- ログ保存レートは500ログ/秒/ゲートウェイ。
- Logpushジョブはアカウントあたり4、Logpushペイロードは1MB/ログ。
- DLPはCloudflare One側のプロファイルを共有するため、Cloudflare One側の設定権限と整合を取る必要がある。
- すべてのトラフィックがCloudflareエッジを経由するため、特定リージョン要件・閉域要件があるユースケースでは適合性を要確認。
- セマンティックキャッシュは類似性閾値の設計次第で「誤ヒット」のリスクがある。重要な動的応答にはキャッシュ除外設定を入れる。

## 参考リンク
- 公式トップ: https://developers.cloudflare.com/ai-gateway/
- Limits: https://developers.cloudflare.com/ai-gateway/reference/limits/
- 対応プロバイダ一覧: https://developers.cloudflare.com/ai-gateway/providers/
- Pricing: https://developers.cloudflare.com/ai-gateway/reference/pricing/
- Universal Endpoint: https://developers.cloudflare.com/ai-gateway/providers/universal/

---
参照日: 2026-05-03
