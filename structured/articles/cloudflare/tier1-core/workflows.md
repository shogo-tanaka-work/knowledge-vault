# Workflows

## 一行サマリ
Cloudflare Workers上で動作する耐久性のある複数ステップ実行エンジン。AWS Step FunctionsやTemporalに相当し、ステップごとに状態を永続化しながら最大1年間にわたる長時間処理を確実に完遂する。

## 解決する課題（Why）
- 長時間にわたる処理を単一リクエストで完結できない（タイムアウト・接続切断）
- API呼び出しや外部システム連携の失敗時に、途中から安全に再開したい
- ユーザーオンボーディングや承認待ちなど、人間や外部イベントを挟む非同期フローを管理したい
- 自前でジョブキュー・状態管理DB・リトライロジックを構築する運用負担を排除したい
- 数日〜数週間にわたるスリープを必要とするビジネスプロセス（トライアル期限切れ、リマインダー等）を実装したい

## 主要機能（What）
- **`step.do(name, fn)`**: 任意の処理を耐久ステップとして実行。結果は永続化され、失敗時は自動リトライ。
- **`step.sleep(name, duration)` / `step.sleepUntil(name, date)`**: 秒〜最大365日のスリープ。スリープ中はCPU課金されず、同時実行数にもカウントされない。
- **`step.waitForEvent(name, opts)`**: 外部イベント（Webhook、承認、ユーザー入力）を待機。タイムアウト指定可。
- **リトライ制御**: ステップ単位で `retries.limit / delay / backoff` と `timeout` を設定。
- **`WorkflowEntrypoint` クラス**: Workersランタイム上で `run(event, step)` を実装する形でWorkflowを定義。
- **インスタンス管理API**: 作成・取得・一時停止・再開・終了をプログラム的またはREST APIで制御。
- **Python SDK**: TypeScriptに加えPythonでもWorkflow定義が可能。
- **Observability**: 組み込みのダッシュボード／`wrangler tail` で各ステップの実行状況・リトライ履歴を可視化。

## アーキテクト視点：いつ選ぶか

### 適しているシーン
- すでにCloudflare Workers／R2／D1／Workers AIを採用しており、エコシステム内で完結させたい
- 数分〜数日にわたる非同期処理（オンボーディング、決済後処理、データETL、AIパイプライン）
- 人間の承認やWebhook受信を挟むhuman-in-the-loopフロー
- グローバル分散・ゼロインフラ運用が要件
- 小〜中規模で、専用クラスタ（Temporal等）を立てるオーバーヘッドを避けたい
- AIエージェントの長時間タスク（複数LLM呼び出し＋外部API連携＋状態保持）

### 適していないシーン
- ステップあたり1MiBを超える大きな中間データを頻繁に扱う（R2等の外部ストレージ参照に切り替えれば回避可）
- ミリ秒単位のリアルタイム性が要求される同期処理（通常のWorkerで十分）
- 25,000ステップを超える超巨大DAG・複雑なfan-out/fan-in（Temporalの方が表現力で優位）
- マルチクラウド／オンプレ環境とのハイブリッド要件
- 既存のAWS資産が大きく、Step FunctionsとEventBridge等が密結合している

## 競合・代替

| 観点 | Cloudflare Workflows | AWS Step Functions | Temporal | Inngest | Trigger.dev |
|---|---|---|---|---|---|
| 実行モデル | コードファースト（TS/Python） | ASL（JSON/YAML DSL） | コードファースト（多言語SDK） | コードファースト（イベント駆動） | コードファースト（TS） |
| ホスティング | フルマネージド（Cloudflare） | フルマネージド（AWS） | セルフホスト or Temporal Cloud | マネージド／セルフホスト | マネージド／セルフホスト |
| 最大実行時間 | 1年（step.sleep） | 1年（Standard） | 無制限 | 数日〜（プラン依存） | 数日〜 |
| 最小課金単位 | CPU時間（待機中ゼロ） | 状態遷移数 | アクション数（Cloud） | ステップ実行数 | 実行時間 |
| グローバル分散 | 標準（エッジ） | リージョン単位 | クラスタ構成次第 | マネージド側で抽象化 | マネージド側で抽象化 |
| 学習コスト | 低（Workers知見があれば） | 中（ASL習得が必要） | 中〜高（概念が豊富） | 低 | 低 |
| 強み | エッジ統合・低コスト・待機無料 | AWSサービス統合の豊富さ | ワークフロー表現力・成熟度 | DX・イベント駆動 | DX・Vercel系との親和性 |

## 料金モデルの要点
- Workers Standardと同一課金体系。追加料金なし。
- **CPU時間**: 月3,000万msまで無料、超過分100万msあたり$0.02。待機中（`step.sleep`、I/O待ち、`step.waitForEvent`中）はCPU課金されない。
- **リクエスト（invocation）**: 月1,000万まで無料、超過100万あたり$0.30。Workflow内のサブリクエストは追加課金されない。
- **ストレージ**: 1GBまで無料、超過分$0.20/GB-月。状態保持期間は無料3日／有料7日（デフォルト、短縮可）。
- Freeプランでも利用可（CPU 10ms、日次10万実行、ストレージ1GB）。
- **コスト最適化観点**: 長時間スリープを多用しても課金されないため、リマインダーやスケジュールジョブを大量に走らせる用途に強い。

## CLI / IaC 操作例

Workflow定義（`src/index.ts`）:

```typescript
import {
  WorkflowEntrypoint,
  WorkflowStep,
  WorkflowEvent,
} from "cloudflare:workers";

type Env = {
  MY_WORKFLOW: Workflow;
  BUCKET: R2Bucket;
  AI: Ai;
};

export class OnboardingWorkflow extends WorkflowEntrypoint<Env> {
  async run(event: WorkflowEvent<{ userId: string }>, step: WorkflowStep) {
    const profile = await step.do("fetch user profile", async () => {
      const res = await fetch(`https://api.example.com/users/${event.payload.userId}`);
      return await res.json();
    });

    await step.do(
      "send welcome email",
      {
        retries: { limit: 5, delay: "10 seconds", backoff: "exponential" },
        timeout: "2 minutes",
      },
      async () => {
        await fetch("https://api.mailer.com/send", {
          method: "POST",
          body: JSON.stringify({ to: profile.email, template: "welcome" }),
        });
      },
    );

    await step.sleep("wait 7 days for trial", "7 days");

    await step.waitForEvent("await upgrade", {
      event: "user.upgraded",
      timeout: "30 days",
    });

    await step.do("provision paid features", async () => {
      // ...
    });
  }
}
```

`wrangler.jsonc`:

```jsonc
{
  "name": "onboarding-worker",
  "main": "src/index.ts",
  "compatibility_date": "2026-04-01",
  "workflows": [
    {
      "name": "onboarding",
      "binding": "MY_WORKFLOW",
      "class_name": "OnboardingWorkflow"
    }
  ],
  "limits": {
    "cpu_ms": 300000,
    "subrequests": 100000
  }
}
```

主要コマンド:

```bash
# デプロイ
npx wrangler deploy

# Workflow一覧
npx wrangler workflows list

# インスタンス起動
npx wrangler workflows trigger onboarding '{"userId":"u_123"}'

# インスタンス状態確認
npx wrangler workflows instances describe onboarding <instance-id>

# 一時停止／再開／終了
npx wrangler workflows instances pause onboarding <instance-id>
npx wrangler workflows instances resume onboarding <instance-id>
npx wrangler workflows instances terminate onboarding <instance-id>

# ログtail
npx wrangler tail
```

## 制限・注意点
- **最大ステップ数**: 有料プランデフォルト10,000、最大25,000（Wrangler設定で拡張）。Free 1,024。
- **最大実行期間（wall time）**: 各ステップ無制限、`step.sleep` は最大365日。
- **CPU時間**: ステップあたりデフォルト30秒、最大5分（`limits.cpu_ms`で設定）。
- **ペイロード／ステップ結果**: イベントペイロード・各ステップ結果ともに最大1MiB。大容量データはR2に格納し参照を返す。`ReadableStream<Uint8Array>` で返却することでストリーム化も可能。
- **状態保持容量**: 1インスタンスあたり最大1GB（有料）／100MB（Free）。
- **同時実行**: 有料50,000、Free 100。待機中は同時実行数にカウントされない。
- **インスタンス作成レート**: 有料 アカウントあたり300/秒、Workflowあたり100/秒。
- **状態保持期間**: 完了済みインスタンスは有料30日／Free 3日で削除。
- **サブリクエスト**: デフォルト10,000、最大1,000万まで拡張可。
- **Workers for Platforms名前空間にはデプロイ不可。**
- **冪等性の責務はユーザー側**: ステップ関数は再実行されうるため、外部副作用は冪等になるよう設計する必要がある。

## ユースケース具体例
- **ユーザーオンボーディング**: 登録 → ウェルカムメール → 7日後トライアル終了通知 → アップグレード待機 → 有料機能プロビジョニング
- **決済処理**: 注文受付 → 在庫予約 → 決済API呼び出し（リトライ付） → 配送指示 → 通知。途中失敗時は補償ステップで自動ロールバック
- **データETL**: R2の生データ取得 → AI推論で要約 → D1へ書き込み → Webhook通知。各段階を独立ステップ化し巨大データもストリームで扱う
- **AIエージェント**: 複数LLM呼び出しと外部ツール実行を耐久実行。失敗時に途中ステップから再開
- **承認フロー**: 申請受領 → 管理者へ通知 → `step.waitForEvent` で承認待機（最大30日） → 承認後アクション
- **リマインダー／スケジュールジョブ**: ユーザーごとに長期スリープを大量並行実行（待機中は課金ゼロ・同時実行枠も消費しない）

## 参考リンク
- 公式ドキュメント: https://developers.cloudflare.com/workflows/
- 制限: https://developers.cloudflare.com/workflows/reference/limits/
- 料金: https://developers.cloudflare.com/workflows/reference/pricing/
- Workers REST API: https://developers.cloudflare.com/api/

---
参照日: 2026-05-03
