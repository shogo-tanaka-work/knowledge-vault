# Containers

## 一行サマリ
Cloudflare Containersは、Workers Runtime（V8 Isolate）に収まらない任意のDockerイメージをCloudflareエッジ上の軽量VMで実行し、Workerからバインディング経由で `fetch()` 呼び出しできる「Workers拡張用コンテナ実行基盤」である。Region: Earth・Auto-sleep・Durable Object結合が組み込まれており、運用モデルはECSやCloud Runと根本的に異なる（2026-05時点でOpen Beta）。

## 解決する課題（Why）
Cloudflare Workersは高速・グローバル・無料枠強力という強みを持つ一方、V8 Isolate上のWeb標準Runtimeで動かすという制約から以下が苦手だった。

- ネイティブバイナリやffmpeg、Headless Chromium、Pandocなど「Linuxバイナリ前提」のライブラリを呼びたい。
- PythonやGoの既存サーバ実装（Flask / Gin等）をそのまま動かしたい。
- 数十秒〜数分の長時間処理（動画変換、PDFレンダリング、機械学習推論の前処理）。
- 数百MB〜GB規模のヒープやファイルシステムを使う処理。
- 既存のDockerfile資産を捨てずにCloudflareネットワークに載せたい。

選択肢としてはECS / Cloud Run / Fly.io Machinesがあるが、「Workersから呼び出す重処理だけのために別クラウドのVPC・IAM・LB・スケーリング設定を組む」のは過剰投資である。Containersはこの隙間を埋める。Workerが入口・ルーティング・キャッシュ・認可を担い、コンテナはWorkerに収まらない処理だけを引き受ける、という役割分担が前提である。

## 主要機能（What）

### Container Application
Dockerfileまたは事前ビルド済みイメージ（`linux/amd64`）をCloudflare Registryにアップロードし、グローバルに分散配置する。Workerから初めてリクエストが来たタイミングでインスタンスが起動するオンデマンド方式である。

- **インスタンスタイプ**：`lite` / `basic` / `standard-1〜4` のプリセット、またはカスタム（vCPU 1-4、メモリ最大12 GiB、ディスク最大20 GB）。
- **ディスク**：すべてエフェメラル。Auto-sleepで停止すると次回起動時はクリーンな状態に戻る。永続化はR2 / D1 / Durable Object Storageに任せる前提。
- **環境変数 / シークレット**：`envVars`プロパティおよびWorkers Secretsから注入。

### Auto-sleep
リクエストが途絶えてから一定時間（`sleepAfter` プロパティ、例：`'10m'`）でインスタンスを停止する。停止中はvCPU課金が止まる。常駐サーバを24/7立ち上げるのではなく「リクエスト駆動でスピンアップする小さなVM」というモデルが核心であり、コスト構造もこれを前提に設計されている。

### Workers Binding
WorkerからContainerへは、Durable Objects互換のバインディング経由でアクセスする。`getByName()` で名前付きインスタンス（同一名は同一インスタンスにルーティング）、`getRandom()` でロードバランシングを書ける。Worker側がリクエストルーティング・認証・WAF判定を行い、コンテナはピュアなアプリケーションロジックに集中できる。

### Durable Object 連携
Containerクラス自体が Durable Object のサブクラスとして定義される。これにより「DO状態 + コンテナプロセス」を同じインスタンス境界で管理でき、Cloudflareの言うProgrammable Sidecarモデルが成立する。DOのSQLiteストレージにメタデータを置きつつ、コンテナで重処理を回す、という構成が自然に書ける。

### リージョン配置（Region: Earth）
明示的なリージョン指定は不要で、Cloudflareの300拠点超のネットワークから「イメージがプリフェッチされた最寄りのロケーション」が選ばれる。例として南米のリクエストはNeuquénやBuenos Aires、北米西海岸はSan Diegoなどに自動配置される。逆に「東京固定で動かしたい」「特定リージョンを禁止したい」という要件には現状フィットしない。

### イメージ管理
`wrangler containers images list` / `delete` でCloudflare Registry上のイメージを管理する。アカウント全体で50 GBのストレージ上限がある（個別イメージはインスタンスタイプのディスク上限まで）。

## アーキテクト視点：いつ選ぶか

### 適しているシーン
- Workers中心のアプリケーションで、一部だけWeb標準Runtimeに収まらない処理を切り出したい（PDF生成、画像/動画変換、Headlessブラウザ、Pandoc、ffmpeg）。
- 既存のDockerfile資産があり、ECS / Cloud RunのIAM・VPC・LB設計を一から組むほどの規模ではないケース。
- リクエスト駆動でスパイクが立つが、平常時はアイドルでよい処理。Auto-sleepの恩恵を受けやすい。
- Durable Objectベースのアプリでセッション単位の重処理（音声処理、AIパイプラインの前処理）をピン留めしたい。
- 「Workers + R2 + D1 + Containers」だけで完結させたい単一ベンダー構成。

### 適していないシーン
- **GPUワークロード**：現時点で非対応。LLM推論はWorkers AIまたは別クラウドのGPUインスタンスに寄せる。
- **24/7常駐の長時間処理**：Auto-sleep前提のコスト構造のため、常時稼働させるとメモリ・ディスクの継続課金で割高になる。専用VPSかECS Fargateの方が安い。
- **TCP/UDP直接受け**：エンドユーザーが非HTTPプロトコルで直接コンテナに接続することはできない。SMTPサーバ・ゲームサーバ用途は不可。
- **特定リージョン縛り**：データレジデンシー要件（EUのみ・日本のみなど）を厳格に求められるワークロード。
- **既にKubernetesを運用している組織**：Helm / Istio / Argo CDなど周辺エコシステムは使えない。Workers中心への思想転換が前提。

## 競合・代替

| 観点 | Cloudflare Containers | AWS Fargate | Cloud Run | Fly.io Machines | Render | Koyeb | Railway |
|---|---|---|---|---|---|---|---|
| 課金モデル | 秒課金、Auto-sleep標準 | 秒課金、常駐前提 | 100msリクエスト課金、Scale-to-zero標準 | 秒課金、Auto-stop設定可 | 月額固定（Service単位） | 秒課金、Scale-to-zero | 月額従量 |
| Scale-to-zero | あり（標準） | なし（タスク常駐） | あり（標準） | あり（オプション） | 一部プランのみ | あり | なし |
| GPU | 不可 | あり | あり（L4/A100） | あり | なし | 一部 | なし |
| TCP/UDP直接 | 不可（Workers経由必須） | 可（NLB併用） | HTTP/gRPCのみ | TCP/UDP対応 | HTTPのみ | HTTPのみ | HTTP/TCP |
| エッジ性 | 300+拠点、最寄り起動 | リージョン指定 | リージョン指定 | 35+リージョン | 中央集約 | 8リージョン | 中央集約 |
| Workers / Edge統合 | ネイティブ | API Gateway別 | Cloud Functions別 | なし | なし | なし | なし |
| 主用途の相性 | Workersの拡張 | エンタープライズ常駐 | コンテナ全般 | Geo分散アプリ | フルスタック小規模 | 軽量グローバル | 開発体験重視 |

CloudflareがFargate / Cloud Runと張り合うのではなく「Workersに紐づく重処理を置く場所」というポジショニングである点が肝。代わりにWorkersを使わない素のコンテナ実行基盤としては、機能的にCloud RunやFly.ioの方が成熟している。

## 料金
Workers Paid（$5/月）契約が前提。Workers Free単独では使えない。

| 項目 | レート | Workers Paid 込み枠 |
|---|---|---|
| vCPU | $0.000020 / vCPU秒 | 375 vCPU分/月 |
| メモリ | $0.0000025 / GiB秒 | 25 GiB時間/月 |
| ディスク | $0.00000007 / GB秒 | 200 GB時間/月 |

**重要な課金挙動**：vCPUはアクティブ実行時のみ秒課金、メモリ・ディスクは「インスタンスが起動している間ずっと」プロビジョン分が課金される。Auto-sleepでアイドルアウトすると全項目止まる。10msグラニュラリティで計測される。

**ネットワーク下り**：

| リージョン | 単価 | 月次無料枠 |
|---|---|---|
| 北米・欧州 | $0.025/GB | 1 TB |
| オセアニア・韓国・台湾 | $0.05/GB | 500 GB |
| その他 | $0.04/GB | 500 GB |

設計指針：「Auto-sleepで止まる前提で `sleepAfter` を短く」「メモリ/ディスクは過剰プロビジョンしない（停止中以外は払い続ける）」「インスタンスタイプはliteから始めて必要に応じて昇格」。

## CLI / API 例

### wrangler.jsonc 設定
```jsonc
{
  "name": "my-app",
  "main": "src/index.ts",
  "compatibility_date": "2026-05-01",
  "containers": [
    {
      "class_name": "PdfRenderer",
      "image": "./Dockerfile",
      "instance_type": "basic",
      "max_instances": 10
    }
  ],
  "durable_objects": {
    "bindings": [
      { "name": "PDF_RENDERER", "class_name": "PdfRenderer" }
    ]
  },
  "migrations": [
    { "tag": "v1", "new_sqlite_classes": ["PdfRenderer"] }
  ]
}
```

### Container クラス定義（Worker側）
```typescript
import { Container, getRandom } from "@cloudflare/containers";

export class PdfRenderer extends Container {
  defaultPort = 8080;
  sleepAfter = "10m";
  envVars = { LOG_LEVEL: "info" };

  override onStart() { console.log("container started"); }
  override onStop() { console.log("container stopped"); }
  override onError(err: unknown) { console.error("container error", err); }
}

export default {
  async fetch(req: Request, env: Env): Promise<Response> {
    const url = new URL(req.url);

    // 同一ユーザーは同じインスタンスにピン留め
    if (url.pathname.startsWith("/render/")) {
      const userId = url.pathname.split("/")[2];
      const container = env.PDF_RENDERER.getByName(userId);
      return container.fetch(req);
    }

    // ロードバランシング（3インスタンスにランダム分散）
    if (url.pathname.startsWith("/batch/")) {
      const container = await getRandom(env.PDF_RENDERER, 3);
      return container.fetch(req);
    }

    return new Response("not found", { status: 404 });
  },
};
```

### Dockerfile（最小例）
```dockerfile
FROM node:22-slim
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --omit=dev
COPY . .
EXPOSE 8080
CMD ["node", "server.js"]
```

### デプロイ・運用コマンド
```bash
# Worker + Container を一括デプロイ
npx wrangler deploy

# 稼働状況確認
npx wrangler containers list

# Registry上のイメージ一覧（50GB上限管理用）
npx wrangler containers images list

# 古いイメージ削除（ストレージ解放）
npx wrangler containers images delete <image-ref>
```

## 制限・注意点
- **Open Beta（2025年6月開始、2026-05時点も継続）**：API・wrangler設定キー・課金単価がGAまでに変わる可能性がある。プロダクション本番投入は慎重に。
- **GPU不可**：機械学習推論はWorkers AIまたは別ベンダーへ。
- **コールドスタート1〜3秒**：イメージサイズと初期化処理に依存。レイテンシ要件がシビアな同期APIには向かない。Workerでキャッシュを噛ませる、min_instancesを使う等の対策が必要。
- **`linux/amd64` のみ**：Apple Silicon環境からビルドする場合は `--platform=linux/amd64` の指定が必須。
- **メモリ/ディスク上限**：単一インスタンスは最大vCPU 4 / メモリ 12 GiB / ディスク 20 GB。これを超える処理は分割するか別基盤を検討。
- **アカウント上限**：Workers Paidでは同時メモリ6 TiB・同時vCPU 1,500・同時ディスク30 TB・Registry総容量50 GB。Enterpriseでの引き上げは個別交渉。
- **エフェメラルディスク**：Auto-sleepで状態は消える。永続化はR2 / D1 / DO Storageへ。
- **直接的なTCP/UDP受け不可**：エンドユーザー向けのSMTP・カスタムプロトコルサーバには使えない。Workersを介したHTTPトンネルが必須。
- **リージョン明示不可**：データレジデンシー要件があるならGAまで様子見、または代替手段（Workers for Platforms + 専用クラスタ等）を検討。
- **Workers Paid必須**：Free Plan単独では利用不可。$5/月の最小コストが乗る。

## 参考リンク
- Cloudflare Containers Overview：https://developers.cloudflare.com/containers/
- Get Started：https://developers.cloudflare.com/containers/get-started/
- Platform Details / Limits：https://developers.cloudflare.com/containers/platform-details/limits/
- Pricing：https://developers.cloudflare.com/containers/pricing/
- Cloudflare Containers Coming 2025 (Blog)：https://blog.cloudflare.com/cloudflare-containers-coming-2025/
- @cloudflare/containers npm：https://www.npmjs.com/package/@cloudflare/containers
- Cloudflare developers llms.txt：https://developers.cloudflare.com/llms.txt

---
参照日: 2026-05-04
