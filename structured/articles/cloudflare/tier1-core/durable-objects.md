# Durable Objects

## 一行サマリ
グローバル一意性を持つステートフルアクター。世界に1つだけ存在する単一インスタンスへ、ストレージ・WebSocket・RPCを束ねて配置するサーバーレス実行単位。

## 解決する課題（Why）
KVやD1では「強整合な単一書き手」「クライアント間のリアルタイム調停」が解けない。KVは結果整合、D1は共有DBに対する楽観ロック前提で、複数Workerからの同時更新を直列化するロジックは自前で組む必要がある。Durable Objectsは「特定IDの処理は世界で1つのインスタンスに集約される」という保証によって、分散ロック・コーディネーター・順序付けキュー・接続ファンアウトといった分散システムの典型課題を、単一スレッドのコードとして書ける形に落とし込む。

## 主要機能（What）
- **グローバル単一インスタンス**: ID単位で世界に1つだけアクティブ化される
- **Storage API**: KV API と SQL API の二系統。SQLite-backed が標準（GA、Free planでも利用可）
- **In-memory state**: アクティブな間はメモリ上の状態を保持、アイドル後にハイバネート
- **WebSocket Hibernation API**: アイドル中の接続を維持しつつ duration 課金を発生させない
- **Alarms API**: 将来時刻に自身を起動して定期処理を実行
- **RPC**: WorkerからJavaScriptネイティブなメソッド呼び出しでDurable Objectを操作

## アーキテクト視点：いつ選ぶか

### 適しているシーン
- リアルタイムチャット、コラボ編集、マルチプレイヤーゲームの部屋単位調停
- レート制限カウンタ、在庫数・席数のような「強整合な単一書き手」
- ユーザー単位・テナント単位のセッション/ステート管理
- WebSocketファンアウト（1接続=1 DOで状態保持）
- 順序保証が必要なイベント処理、軽量なジョブキュー
- AIエージェントの会話状態・ツール実行履歴の保持

### 適していないシーン
- 全ユーザー横断の集計・分析クエリ（→ D1 / Workers Analytics Engine）
- 大容量バイナリ（→ R2、DO Storageは1オブジェクト10GBまで）
- 単一IDあたり1,000 req/秒を恒常的に超えるホットキー型ワークロード
- グローバルに分散した読み取りキャッシュ用途（→ KV）

## 概念モデル（必須セクション）
- **Object ID**: ランダム生成（`idFromName` でないユニークID）または名前由来（`idFromName("room-123")`）。同じIDは世界で常に同じインスタンスにルーティングされる
- **グローバル単一性**: アクティブなインスタンスは常に1つ。ヘルシーなサーバー間で自動マイグレートされ、アプリ側はライフサイクルを管理しない
- **In-memory state + Storage**: メモリ上の状態 + アクター直下に同居する永続ストレージ。同居しているため強整合かつ低レイテンシ
- **SQLite Storage（推奨）**: 各Durable ObjectがSQLiteデータベースを丸ごと1つ持つ。`ctx.storage.sql.exec()` でSQL実行、KVライクな `put/get` も内部的に隠しテーブルで処理
- **Single-threaded cooperative concurrency**: ブラウザのJSと同じく協調的マルチタスキング。レースコンディションが構造的に発生しない
- **Actor model**: メッセージ（HTTP/RPC）受信 → 単一スレッドでロジック実行 → メッセージ送信、というアクターパターンそのもの

## 競合・代替（Akka / Orleans / Erlang/OTP / Lambda + DynamoDB の発想差）
- **Akka / Microsoft Orleans**: アクターモデルとしての発想は同一だが、これらはクラスタ運用・ノード障害時のリバランスを自前で構築する必要がある。Durable ObjectsはCloudflareのグローバルネットワークがランタイム自体を担い、配置・移動・障害復旧が透過的
- **Erlang/OTP**: プロセス単位の隔離と単一スレッド実行という思想は近いが、OTPはあくまで言語ランタイム。Durable ObjectsはエッジネットワークそのものがOTP的役割を果たす
- **AWS Lambda + DynamoDB**: ステートレスFaaS + 外部KV。書き込み調停は条件付きwriteや楽観ロックで自前実装が必要。Durable Objectsは「コード = 単一の書き手」なので、調停ロジックがそもそも不要
- **Redis / Memcached**: 共有キャッシュとしての高速性はあるが、計算とストレージが分離されているためネットワークラウンドトリップが発生。DOは計算とストレージが同居
- 思想差を一言で言うと、Durable Objectsは「アクターランタイムがCDNに溶け込んだ」プロダクトであり、開発者はインフラを意識せずアクター指向で設計できる

## 料金モデルの要点
- **Compute（リクエスト）**: Free 100,000/日、Paid 100万/月込み + $0.15/100万。WebSocketの受信メッセージは20:1で集約課金
- **Compute（Duration）**: Free 13,000 GB-s/日、Paid 400,000 GB-s/月込み + $12.50/100万 GB-s。128MB固定割当で課金。Hibernation中は課金されない点が重要
- **SQLite Storage（2026年1月7日以降課金開始）**: 行読み 5M/日（Free）、25B/月込み + $0.001/100万行（Paid）。行書き 100K/日（Free）、50M/月込み + $1.00/100万行。ストレージ 5 GB込み + $0.20/GB-月
- **KV Storage（Paid限定、レガシー）**: 4KB単位の request units 課金
- **コスト最適化の鉄則**: WebSocket Hibernation APIを必ず使う。例3（非Hibernation）の月$416が、例4（Hibernation）では月$10まで下がる

## CLI / IaC 操作例

### wrangler.jsonc
```jsonc
{
  "name": "chat-room",
  "main": "src/index.ts",
  "compatibility_date": "2026-01-01",
  "durable_objects": {
    "bindings": [
      { "name": "ROOM", "class_name": "ChatRoom" }
    ]
  },
  "migrations": [
    {
      "tag": "v1",
      "new_sqlite_classes": ["ChatRoom"]
    }
  ],
  "limits": {
    "cpu_ms": 30000
  }
}
```

### Durable Objectクラス定義
```typescript
import { DurableObject } from "cloudflare:workers";

export class ChatRoom extends DurableObject {
  sql: SqlStorage;

  constructor(ctx: DurableObjectState, env: Env) {
    super(ctx, env);
    this.sql = ctx.storage.sql;
    this.sql.exec(`
      CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY,
        user TEXT NOT NULL,
        body TEXT NOT NULL,
        created_at INTEGER NOT NULL
      )
    `);
  }

  async postMessage(user: string, body: string): Promise<number> {
    const created_at = Date.now();
    const result = this.sql.exec(
      "INSERT INTO messages (user, body, created_at) VALUES (?, ?, ?) RETURNING id",
      user, body, created_at
    ).one();
    return result.id as number;
  }

  async listMessages(): Promise<unknown[]> {
    return this.sql.exec("SELECT * FROM messages ORDER BY id DESC LIMIT 50").toArray();
  }
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);
    const roomName = url.searchParams.get("room") ?? "default";
    const id = env.ROOM.idFromName(roomName);
    const stub = env.ROOM.get(id);

    // RPC呼び出し
    const messageId = await stub.postMessage("alice", "hello");
    const messages = await stub.listMessages();
    return Response.json({ messageId, messages });
  },
};
```

### デプロイ
```bash
npx wrangler deploy
```

## 制限・注意点
- **単一インスタンスのスループット**: ソフトリミット約1,000 req/秒。ホットキーが想定される場合は、ID設計でシャーディングする
- **CPU per request**: デフォルト30秒、`limits.cpu_ms` で最大5分まで延長可。CPU時間はI/O待ちを含まない
- **Storage per Durable Object**: 10GB（SQLite-backed、Paid）。超過すると書き込みが `SQLITE_FULL` で失敗、読み取りと削除は継続可能
- **キー/値サイズ**: SQLite-backedは key+value 合計2MB、SQL stringやBLOB行も2MB
- **WebSocket受信メッセージ**: 32 MiB
- **Durable Objectクラス数**: アカウントあたり Paid 500、Free 100
- **Free plan**: SQLite-backed のみ。KV-backed はPaid限定
- **Hibernationを阻害する要因に注意**: 非HibernationなWebSocket、ペンディングなPromise/タイマーがあるとアイドル判定されず duration 課金が継続する

## ユースケース具体例
- **マルチプレイヤーゲームのルーム**: `idFromName("room-${roomId}")` でルームごとに1 DO、参加者全員のWebSocketをHibernation API経由で保持
- **AIエージェントのセッション**: `idFromName("agent-${userId}")` でユーザー単位のエージェント状態（会話履歴、ツール呼び出し中間結果）をSQLiteに永続化
- **APIレート制限**: `idFromName("ratelimit-${apiKey}")` でAPIキーごとにカウンタDO、強整合な秒間/分間カウントを実現
- **在庫・席予約**: 商品IDや座席IDでDO化、SQLトランザクションで「残数 > 0 ならデクリメント」を安全に実行
- **コラボ編集（Liveblocks/Yjs風）**: ドキュメント単位でDO、CRDT状態をin-memory + 永続化
- **AI Gateway / D1 / Stream Live**: Cloudflare自身もこれらの内部でDOを多用している

## 参考リンク
- 公式トップ: https://developers.cloudflare.com/durable-objects/
- What are Durable Objects?: https://developers.cloudflare.com/durable-objects/concepts/what-are-durable-objects/
- Limits: https://developers.cloudflare.com/durable-objects/platform/limits/
- Pricing: https://developers.cloudflare.com/durable-objects/platform/pricing/
- Blog「Durable Objects: Easy, Fast, Correct — Choose three」
- Blog「Zero-latency SQLite storage in every Durable Object」

---
参照日: 2026-05-03
