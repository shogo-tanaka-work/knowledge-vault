# Sandbox SDK

## 一行サマリ
AIエージェントが生成した任意コードを安全に実行するための、Cloudflare Containers + Workers + Durable Objectsで構成された永続的・隔離型のLinuxサンドボックスSDKである。

## 解決する課題（Why）
LLMにコードを書かせるところまでは安価に実現できるが、「そのコードを安全に走らせる場所」が抜けると、エージェントは推論にとどまり実際の作業を完結できない。ローカル実行は信頼境界を壊し、共有VMはマルチテナント分離が甘く、自前のFirecracker/gVisorクラスタは運用コストが重い。Cloudflare Sandbox SDKはこの「AIに渡してよい任意コード実行環境」を、Workersから一行で呼び出せるマネージドDurable Objectとして提供する。

- LLM出力の任意シェルコマンド・任意Python/JavaScriptコードを、ホストとも他テナントとも隔離した環境で実行する。
- 永続ファイルシステムと長時間バックグラウンドプロセスを、エージェントの「自分のPC」として持たせる。
- 開発サーバを立ててプレビューURLで人間にレビューさせる、テストを走らせて結果を読む、といった開発者の作業ループをエージェントが模倣できるようにする。
- egress proxy経由で資格情報をエージェントから隠したまま外部APIに認証する、という「鍵を渡さず仕事をさせる」運用を成立させる。
- Cloudflareネットワーク内に閉じることで、Workersからの呼び出しレイテンシ・課金・ログ・ID管理を統一する。

## 主要機能（What）

### Shell実行（exec / Streaming output）
`sandbox.exec()` で任意のシェルコマンドを実行し、stdout / stderr / exit codeを取得する。`execStream()`系APIでは出力をリアルタイムでストリーミングでき、長時間ビルド・テスト・学習ジョブの進捗をWorkersから人間やLLMにそのまま流せる。タイムアウト管理と非ゼロ終了コードのハンドリングは標準で組み込まれている。

### ファイルシステム
コンテナ内に永続的なLinuxファイルシステムを持ち、`writeFile` / `readFile` / `mkdir` / `deleteFile` 等で操作する。inotifyベースのファイル監視も提供されており、エージェントが「ファイルが変わったら次のステップに進む」イベント駆動ループを書ける。R2 / S3 / GCSをマウントして大容量データやモデルファイルを共有することも可能である。

### Code Interpreter（Python / JS / TS の永続実行）
セッションをまたいで変数・import・状態が残るコードインタプリタを持つ。Jupyterノートブック相当のセル実行体験で、データ分析・機械学習エージェント用途に向く。チャート・テーブルなどのリッチ出力もそのまま扱える。

### Port Preview / 公開URL
コンテナ内で起動したHTTPサーバを `exposePort()` で公開し、Cloudflareが発行するプレビューURLで外部から到達できるようにする。Vite/Next.jsの開発サーバをエージェントに立てさせて、人間がブラウザで動作確認する、という開発ループを成立させる。`.workers.dev`はワイルドカードサブドメインを張れないため、本番運用ではカスタムドメイン設定が前提となる。

### PTY / WebSocket Terminal
擬似端末をWebSocket経由で開けるため、xterm.jsを噛ませれば人間がブラウザからエージェントのコンテナに直接ログインしてデバッグできる。「リクエスト・レスポンス型のexec」では捌けない対話的シェル（vim / REPL / curses系TUI）もそのまま動く。

### 永続化 / Snapshots
コンテナのディスク状態をスナップショットとして取得し、R2にtieredキャッシュで保存する。リージョン跨ぎの暖機起動が現実的な時間で済むため、エージェントが何時間にも渡って同じワーキングコピーで作業し続けるユースケースに耐える。スリープからの復帰・別リージョンへの再配置でも作業ツリーは保持される。

### Egress Proxy（信頼境界）
サンドボックスから外向き通信は、Cloudflare側のプログラマブルegress proxyを通る。OAuthトークンやAPIキーはこのproxyに保持され、ネットワークレイヤで宛先ドメイン別に注入される。エージェント本体は資格情報を一切見ないため、プロンプトインジェクションでトークンを漏らされる経路を物理的に塞げる。

### Workers Binding / Durable Objects 連携
SandboxはDurable Objectとしてバインドされ、Workersから `getSandbox(env.Sandbox, "session-id")` で取り出す。同じIDで再取得すれば同じコンテナに戻れるため、ユーザー単位・セッション単位の永続環境が自然に書ける。Durable Objectsのrouting特性をそのまま流用できる点がE2BやModal Sandboxesに対する構造的な強みである。

## アーキテクト視点：いつ選ぶか

### 適しているシーン
- LLMを核にした「コードを書いて走らせて結果を読む」エージェント（Code Interpreter / SWEエージェント / データ分析Bot）。
- ユーザーごとにIDE的な永続ワークスペースを払い出すSaaS（オンラインIDE、教育プラットフォーム、Replit的サービス）。
- すでにCloudflare Workers / Durable Objects / R2上にアプリを載せており、追加のクラウドアカウントを増やさずにサンドボックスを足したいケース。
- 任意コード実行を「自社で持つ」ことのコンプライアンス上の重さを避けたい中小〜中堅のエージェントSaaS。
- Egress proxyで資格情報をエージェントから隠す要件があるケース（カスタマー資格でAPIを叩く必要があるが、LLMには渡したくない）。

### 適していないシーン
- GPUを必須とする推論・学習ワークロード。Sandboxは現時点でCPUコンテナのみであり、GPUインスタンスは別途Workers AI / Containers GPU系を検討する。
- 数万並列のバッチ処理・MapReduce的ワークロード。同時実行枠はかなり緩和されたとはいえ、Spark / Dataflow / Batch系の代替にはならない。
- 数百ms以下のスタートアップが必須のリクエスト型コード実行。素のWorkers isolateやDynamic Workersのほうが2桁速い。
- 「外部に出さないオンプレ」要件。Cloudflareネットワーク前提のため、データ主権要件が厳しい組織には合わない。
- 既存のKubernetes / Firecrackerクラスタの運用ノウハウがあり、自社で握りたい組織。

## 競合・代替

| 観点 | Cloudflare Sandbox SDK | E2B | Modal Sandboxes | Daytona | CodeSandbox CDE | Replit Agent | Anthropic Code Execution |
|---|---|---|---|---|---|---|---|
| 出自 | Workers / Containers / DO | エージェント向けサンドボックス専業 | Pythonデータ・AI実行基盤 | OSS Dev Environment Manager | オンラインIDE発のCDE | オンラインIDE / エージェント | Claude tool（Anthropic API） |
| 隔離単位 | Container（Durable Object単位） | Firecracker microVM | gVisor / Firecracker | Docker / k8s | Firecracker microVM | Repl（NixOSベース） | Anthropic管理サンドボックス |
| 永続化 | R2スナップショット・FS永続 | スナップショット | Volume / 永続ファイルシステム | Workspace永続 | 標準 | 標準 | セッション内のみ |
| GPU | 不可 | 一部対応 | 強力（A100/H100） | 環境次第 | 限定 | 限定 | 不可 |
| Port Preview | あり（ワイルドカードDNS必要） | あり | あり | あり | あり | あり | なし |
| Workers / エッジ統合 | 一級市民 | 別クラウド | 別クラウド | 別クラウド | 別クラウド | 別クラウド | API経由 |
| 信頼境界（資格情報） | Egress proxyで分離 | アプリ層次第 | アプリ層次第 | アプリ層次第 | アプリ層次第 | アプリ層次第 | Anthropic側で管理 |
| 強み | DO routing・WorkersネイティブAPI・egress proxy | エージェント専用UX・成熟 | GPU・データ系の太いランタイム | OSSで自社運用可能 | IDE体験・CDE | エージェントUX一体型 | Claudeから即座に使える |
| 弱み | GPUなし・Beta機能あり | 自前クラウドで分離管理 | エッジ統合は弱い | マネージド色は薄い | エージェント用途は二次的 | 外部から呼びにくい | 永続化・カスタマイズが弱い |

CloudflareのSandbox SDKは「Workersアプリの一部としてサンドボックスをバインドできる」点と「egress proxyで資格情報をエージェントから引き剥がす」点が他社と差別化される。一方、GPUワークロードや巨大データ処理ではModal、エージェント側UXの成熟度ではE2Bが先行している。

## 料金
- Workers Paidプラン（$5/月〜）が前提。Workers / Durable Objectsの通常課金に加え、Cloudflare Containersの「Active CPU Pricing」（コンテナがCPUを使った時間にのみ課金、アイドル時間は無課金）が積み上がる。
- インスタンスタイプは lite / basic / standard / large 系のサイズが選べ、それぞれメモリ・vCPU・並列上限が異なる。GAタイミングで同時実行枠は大幅に拡張されており、liteは概ね1.5万、basicは6千、それより大きいサイズで1千以上が標準で用意される。
- スナップショットの保存はR2の通常ストレージ・オペレーション課金が乗る。長時間アイドル後の暖機復帰で帯域・操作費が発生する点に注意。
- Egress proxyを通る外向きトラフィックはWorkersの通常egressに準じ、超過分はバンドル次第で従量。
- 開発・検証用途であれば、Free + 短時間検証の組み合わせで月数ドルレンジに収まる。AIエージェントSaaSとして本番展開する場合は、ユーザーあたりCPU秒数 × Active CPU単価で見積もるのが筋である。

## CLI / API 例

### wrangler.toml
```toml
name = "agent-sandbox"
main = "src/index.ts"
compatibility_date = "2026-04-01"

[[containers]]
class_name   = "Sandbox"
image        = "./Dockerfile"
instance_type = "basic"
max_instances = 50

[[durable_objects.bindings]]
class_name = "Sandbox"
name       = "Sandbox"

[[migrations]]
tag = "v1"
new_sqlite_classes = ["Sandbox"]
```

### Worker 側コード（最小例）
```ts
import { getSandbox } from "@cloudflare/sandbox";
export { Sandbox } from "@cloudflare/sandbox";

type Env = { Sandbox: DurableObjectNamespace };

export default {
  async fetch(req: Request, env: Env): Promise<Response> {
    const url = new URL(req.url);
    const sandbox = getSandbox(env.Sandbox, "user-42-session");

    if (url.pathname === "/run") {
      // 1) シェル実行
      const r = await sandbox.exec(`python3 -c "print(2 + 2)"`);
      // 2) FS書き込み
      await sandbox.writeFile("/workspace/hello.txt", "Hello, Sandbox!");
      // 3) FS読み出し
      const f = await sandbox.readFile("/workspace/hello.txt");
      return Response.json({ stdout: r.stdout, exit: r.exitCode, file: f });
    }

    if (url.pathname === "/preview") {
      // 4) コンテナ内でdev serverを起動し、Port Previewで公開
      await sandbox.exec("npm --prefix /workspace/app run dev &");
      const { url: previewUrl } = await sandbox.exposePort(3000);
      return Response.json({ previewUrl });
    }

    return new Response("ok");
  },
};
```

### Streaming output
```ts
const stream = await sandbox.execStream("pytest -q");
for await (const chunk of stream.stdout) {
  controller.enqueue(chunk); // ReadableStreamに流してSSEでLLMやUIに転送
}
```

### Code Interpreter（永続コンテキスト）
```ts
const ctx = await sandbox.createCodeContext("python");
await sandbox.runCode(ctx, "import pandas as pd; df = pd.read_csv('/data/x.csv')");
const summary = await sandbox.runCode(ctx, "df.describe().to_json()");
```

## 制限・注意点
- 2026年4月時点でCore機能はGAだが、egress proxy / PTY / 一部スナップショット制御などはまだBeta扱いのものがある。APIシグネチャは v1.x で固まりつつあるが、SDKのChangelogは確認しておく。
- GPUは現時点で非対応。GPUが必要なら Workers AI（Cloudflareホストモデル）か外部のModal / RunPod系と組み合わせる。
- `exposePort()` で発行されるプレビューURLは、`*.workers.dev` ではなく自社のカスタムドメイン＋ワイルドカードDNSが必要。本番設計では最初から専用サブドメインを切る。
- 同時実行は `max_instances` と各インスタンスタイプの並列上限で律速される。AIエージェントSaaSとして展開する場合、ユーザーあたり1コンテナ前提のスケール上限を必ず計算する。
- Durable ObjectsのID単位でコンテナが固定されるため、特定ユーザーのセッションが特定リージョンにピン留めされる。グローバルレイテンシ均一化を期待してはいけない。
- Egress proxy経由で資格情報を注入する場合、ドメイン別ポリシーの設計を最初に固めておかないと、エージェントが資格情報のスコープを越えて使い始めるリスクがある（プロンプトインジェクションでの権限昇格）。
- スナップショットは便利だが、機密データを含んだままR2に残るためライフサイクル管理（保持期間・削除）はアプリ側で運用する。
- ローカル開発時は `wrangler dev` でDocker経由のコンテナを起動する。CIでのE2Eテストは、コンテナビルド時間とR2モック有無を踏まえて設計する。

## 参考リンク
- Sandbox SDK Docs（Overview）：https://developers.cloudflare.com/sandbox/
- Getting Started：https://developers.cloudflare.com/sandbox/get-started/
- GitHub `cloudflare/sandbox-sdk`：https://github.com/cloudflare/sandbox-sdk
- Blog: Agents have their own computers with Sandboxes GA：https://blog.cloudflare.com/sandbox-ga/
- Blog: Sandboxing AI agents, 100x faster（Dynamic Workers）：https://blog.cloudflare.com/dynamic-workers/
- Blog: Project Think：https://blog.cloudflare.com/project-think/
- Product page: Cloudflare Sandboxes：https://workers.cloudflare.com/product/sandboxes
- Cloudflare Containers Pricing：https://developers.cloudflare.com/containers/platform-details/pricing/
- InfoQ: Cloudflare Sandboxes Reach GA：https://www.infoq.com/news/2026/04/cloudflare-sandboxes-ga/

---
参照日: 2026-05-04
