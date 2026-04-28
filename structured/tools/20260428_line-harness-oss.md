# LINE Harness OSS 検証ログ

> ステータス: 未検証（検証予定）
> 作成日: 2026/04/28
> 最終更新: 2026/04/28
> ファイルパス: /Users/shogo/ObsidianVault/knowledge-vault/structured/tools/20260428_line-harness-oss.md

---

## 📋 検証概要

- **ツール/サービス名**: LINE Harness OSS
- **検証対象**: 新ツール
- **バージョン**: v0.4.0（MCP対応）
- **GitHub**: https://github.com/Shudesu/line-harness-oss
- **公式サイト**: https://shudesu.github.io/line-harness-oss/
- **ライセンス**: MIT（商用利用可）
- **検証期間**: 2026/04/28 -（未着手）
- **検証担当者**: s-tanaka
- **検証ステータス**: 未検証（検証予定）

---

## 1. 背景と検証目的

### なぜこの検証を行うのか
- LステップやUTAGEと同等の機能をOSSで0円実現できるか確認したい
- Claude Code × LINE Harness APIで「AI → LINE配信」のフルパイプラインを組める可能性を探る
- 前回検証（LINE Bot MCP Server / 2026-04-27）の延長線上にある実践的な選択肢として位置づけ

### 解決したい課題
- Lステップ（月2,980〜32,780円）やUTAGE（月1万円〜）の費用を削減したい
- データをSaaS側に預けず、自分のCloudflareに持ちたい
- 管理画面を開かずClaude Codeの自然言語でLINE運用を完結させたい

### 期待される効果
- 月額0円でステップ配信・セグメント配信・リッチメニュー等を運用できる
- Claude Code（MCP 16ツール）から「友だち数教えて」「VIPに配信して」が可能
- BAN検知・自動移行という他ツールにない差別機能の体験

---

## 2. ツール基本情報

### アーキテクチャ
完全セルフホスティング型。自分のCloudflareアカウントにデプロイして運用する。

| レイヤー | 技術 |
|---|---|
| API / Webhook | Cloudflare Workers + Hono |
| DB | Cloudflare D1（SQLite、42テーブル） |
| 管理画面 | Next.js 15 + Tailwind CSS |
| LIFF | Vite + TypeScript |
| 定期実行 | Workers Cron Triggers（5分ごと） |
| CI/CD | GitHub Actions |

### コスト感
| 友だち数 | コスト |
|---|---|
| 0〜5,000人 | 完全無料（Cloudflare無料枠内） |
| 5,000〜10,000人 | 約 $10/月（Cloudflareのみ） |
| 50,000人以上 | 約 $25/月 |

ソフトウェア本体は永久に0円。

### Lステップ / UTAGE との使い分け判断

| 観点 | LINE Harness | Lステップ | UTAGE |
|---|---|---|---|
| 月額 | 0円（Cloudflare費のみ） | 2,980〜32,780円 | 1万円〜 |
| ステップ配信 | ✅ | ✅ | ✅ |
| セグメント配信 | ✅ | ✅ | ✅ |
| リッチメニュー | ✅ | ✅ | ✅ |
| LIFF フォーム | ✅ | ✅ | ✅ |
| LP 機能 | ❌ | ❌ | ✅ |
| Stripe 決済統合 | ✅ | ❌ | ✅ |
| IF-THEN 自動化 | ✅（7×6完全対応） | 一部 | 一部 |
| BAN 検知・移行 | ✅（独自） | ❌ | ❌ |
| API 公開 | 全機能公開 | 非公開 | 非公開（解放予定） |
| データ所有 | 自分のCloudflare | SaaS側 | SaaS側 |
| AI 連携 | Claude Code対応（公式） | 難 | 難 |

**選択基準まとめ**
- まず0円で仕組みを体感 → **LINE Harness**
- 企業チームで本格運用（権限管理・ノウハウ蓄積） → **Lステップ**
- コンテンツ販売（LINE+LP+決済+会員サイトの一体型） → **UTAGE**

---

## 3. 検証予定タスク

### STEP1: 環境セットアップ（コピペ1回）

**やること**
1. Claude Code を `--dangerously-skip-permissions` モードで起動
2. Cloudflare アカウント作成（https://dash.cloudflare.com/sign-up）
3. LINE公式アカウント作成 + Messaging API有効化
4. **API5点の取得**（詳細は「セットアップ手順」セクション参照）
5. Claude Codeに環境構築プロンプトを1回送信
6. Webhook URL設定 + LINE応答設定

**完了条件**
- 管理画面URL（`line-crm-admin.pages.dev`）でログインできる
- 自分を友だち追加すると管理画面の「友だち」に表示される

---

### STEP2: 基本動作確認（コピペ1回）

**やること**
1. Claude Codeにシナリオ作成プロンプトを1回送信
2. 友だち追加して挨拶→分岐シナリオの動作確認
3. ボタンタップ→自動応答の確認

**完了条件**
- 友だち追加 → Flex Messageで挨拶が届く
- 「X完全自動化」タップ → 対応する返答が届く

---

### STEP3: 発展機能（後で試す）

| # | 機能 | 詳細 |
|---|---|---|
| 3-1 | BAN対策システム | 検知・ステルスモード・バックアップアカウント自動移行の3層 |
| 3-2 | FAQ自動応答チャットボット | 10件一括登録、reply API（無料）で自動返答 |
| 3-3 | LP→LINE→自動シナリオ導線 | LIFF + タグ付与 + セグメント別シナリオの全自動導線 |

プロンプトは STEP3記録セクション に全文を保存済み。

---

## 4. セットアップ手順（詳細）

### 4-1. APIの取得手順

#### API①②：Messaging API Channel ID / Channel secret
1. `manager.line.biz` でLINE公式アカウントを選択
2. 設定 → Messaging API → 「Messaging APIを利用する」
3. プロバイダーを作成（名前を控えておく）
4. 表示された `Channel ID` と `Channel secret` をメモ

#### API③：チャネルアクセストークン
1. 上記画面のリンクから LINE Developers Console を開く
2. プロバイダー → Messaging APIチャネル → 「Messaging API設定」タブ
3. 下部の「チャネルアクセストークン（長期）」→「発行」
4. 表示された長い文字列をメモ

#### API④⑤：LINEログイン チャネルID / チャネルシークレット
> ここが重要。UUID取得・BAN移行・流入経路追跡がこれに依存する。

1. LINE Developers Console → 同じプロバイダー → 「新規チャネル作成」→「LINEログイン」
2. アプリタイプ: 「ウェブアプリ」を選択
3. 作成後の「チャネル基本設定」から `チャネルID` と `チャネルシークレット` をメモ

#### API取得完了チェック
```
API① Channel ID = 
API② Channel secret = 
API③ チャネルアクセストークン = 
API④ LINEログイン チャネルID = 
API⑤ LINEログイン チャネルシークレット = 
```

---

### 4-2. LINE応答設定

Webhook URLを登録後、以下を設定する。

1. `manager.line.biz` → 設定 → Messaging API → Webhook URLを入力 → 保存
2. 左メニュー → 応答設定:
   - あいさつメッセージ → **オフ**
   - Webhook → **オン**
   - 応答メッセージ → **オフ**

> 応答メッセージをオフにしないとLINE側とLINE Harnessが二重応答する。

---

## 5. セットアップ用プロンプト（全文）

### STEP1 環境構築プロンプト

```
# LINE Harness 環境構築

以下の手順を上から順番に全て実行してください。
途中でエラーが出たら、原因を特定して自動で修正し、失敗したステップからやり直してください。
ユーザーに質問せず、全て自動で判断して進めてください。

## API情報（↓ ここにメモの5行を貼り付け ↓）

API① Channel ID = ここにメモの値を貼り付け
API② Channel secret = ここにメモの値を貼り付け
API③ チャネルアクセストークン = ここにメモの値を貼り付け
API④ LINEログイン チャネルID = ここにメモの値を貼り付け
API⑤ LINEログイン チャネルシークレット = ここにメモの値を貼り付け

管理画面用APIキー = sk-line-harness-2026

## 0. 前提：Cloudflare APIトークンの設定

npx wrangler login は使わないでください。代わりに以下の手順でAPIトークンを取得・設定します。

1. https://dash.cloudflare.com/profile/api-tokens を開く
2. 「Create Token」→「Edit Cloudflare Workers」テンプレートを選択
3. 「Account Resources」と「Zone Resources」を自分のアカウントに設定して作成
4. 表示されたトークンを以下のように環境変数にセット：

export CLOUDFLARE_API_TOKEN="取得したトークン"

npx wrangler whoami で認証できることを確認してから次に進んでください。

アカウントIDも控えておきます：

npx wrangler whoami

## 1. D1データベース作成

npx wrangler d1 create line-crm

出力される database_id を控えておいてください。

「already exists」エラーが出た場合：

npx wrangler d1 list

で既存の database_id を確認してください。

## 2. リポジトリのクローンとセットアップ

git clone https://github.com/Shudesu/line-harness-oss.git
cd line-harness-oss
pnpm install

pnpmが入っていない場合は npm install -g pnpm@9 を先に実行してください。
node -v が20未満の場合はNode.js 20以上をインストールしてから再実行してください。

tsconfig.base.json の修正

tsconfig.base.json の lib に "DOM" を追加してください（ないとビルドエラーになります）：

"lib": ["ES2022", "DOM"]

ビルド

pnpm -r build

apps/web のビルドが NEXT_PUBLIC_API_URL is not set で失敗しても無視してOKです（後の手順で対応します）。

## 3. wrangler.toml にD1のdatabase_idを設定

apps/worker/wrangler.toml を以下のように書き換えてください：

- account_id → npx wrangler whoami で確認したアカウントID
- database_id → 手順1で取得した値
- database_name → line-crm

また、R2（画像ストレージ）はCloudflareで別途有効化が必要なため、[[r2_buckets]] セクションは削除またはコメントアウトしてください。削除後、apps/worker/src/index.ts の IMAGES: R2Bucket を IMAGES?: R2Bucket に変更してください。

## 4. D1にスキーマとマイグレーションを適用

まずベーススキーマを適用：

npx wrangler d1 execute line-crm --remote --file=packages/db/schema.sql --config=apps/worker/wrangler.toml

続いてすべてのマイグレーションを順番に適用：

for f in packages/db/migrations/*.sql; do
  echo "Applying: $f"
  npx wrangler d1 execute line-crm --remote --file="$f" --config=apps/worker/wrangler.toml
done

「already exists」「duplicate column」エラーは無視してOKです。

さらに auto_replies テーブルに line_account_id カラムを追加（なければ）：

npx wrangler d1 execute line-crm --remote --config=apps/worker/wrangler.toml \
  --command="ALTER TABLE auto_replies ADD COLUMN line_account_id TEXT"

## 5. Workersのシークレットを設定

echo "API①の値" | npx wrangler secret put LINE_CHANNEL_ID --config=apps/worker/wrangler.toml
echo "API②の値" | npx wrangler secret put LINE_CHANNEL_SECRET --config=apps/worker/wrangler.toml
printf 'API③の値' | npx wrangler secret put LINE_CHANNEL_ACCESS_TOKEN --config=apps/worker/wrangler.toml
echo "sk-line-harness-2026" | npx wrangler secret put API_KEY --config=apps/worker/wrangler.toml
echo "API④の値" | npx wrangler secret put LINE_LOGIN_CHANNEL_ID --config=apps/worker/wrangler.toml
echo "API⑤の値" | npx wrangler secret put LINE_LOGIN_CHANNEL_SECRET --config=apps/worker/wrangler.toml

（チャネルアクセストークンは echo ではなく printf で渡すと特殊文字が安全に処理されます）

## 6. Workersをデプロイ

cd apps/worker && pnpm run deploy

デプロイ後に表示されるURLを控えてください。

## 7. 管理画面をビルド＆デプロイ

apps/web/.env.local を作成：

NEXT_PUBLIC_API_URL=手順6で取得したWorkersのURL
NEXT_PUBLIC_API_KEY=sk-line-harness-2026

ビルド：

cd apps/web && pnpm build

Cloudflare Pagesにデプロイ（out ディレクトリを指定）：

npx wrangler pages deploy out --project-name=line-crm-admin --commit-dirty=true

「Project not found」エラーが出た場合はプロジェクトを先に作成してください：

npx wrangler pages project create line-crm-admin --production-branch=main

## 8. 完了報告

全て完了したら、以下をまとめて報告してください：

✅ Workers API URL：（表示されたURL）
✅ 管理画面 URL：（表示されたURL）
✅ Webhook URL：（Workers API URL + /webhook）
```

---

### STEP2 シナリオ作成プロンプト

```
# LINE Harness シナリオ作成

STEP1でデプロイしたLINE Harness APIを使って、友だち追加時の挨拶→分岐シナリオを構築してください。

Workers API URLとAPIキーは wrangler.toml と .env.local から取得して使ってください。
途中でエラーが出たら、原因を特定して自動で修正し、失敗したステップからやり直してください。

## 前提：Cloudflare APIトークンの確認

export CLOUDFLARE_API_TOKEN="あなたのAPIトークン"

npx wrangler whoami で認証できることを確認してから次に進んでください。

## 事前確認：DBマイグレーションの適用

for f in packages/db/migrations/*.sql; do
  npx wrangler d1 execute line-crm --remote --file="$f" --config=apps/worker/wrangler.toml
done

「already exists」「duplicate column」エラーは無視してOKです。

npx wrangler d1 execute line-crm --remote --config=apps/worker/wrangler.toml \
  --command="ALTER TABLE auto_replies ADD COLUMN line_account_id TEXT"

## コード修正：再フォロー時の挨拶再送

apps/worker/src/routes/webhook.ts の follow イベントハンドラ内、friend_scenarios の既存チェック部分を以下に修正してください：

// 変更前
const existing = await db
  .prepare(`SELECT id FROM friend_scenarios WHERE friend_id = ? AND scenario_id = ?`)
  .bind(friend.id, scenario.id)
  .first<{ id: string }>();
if (!existing) {

// 変更後
const existing = await db
  .prepare(`SELECT id, status FROM friend_scenarios WHERE friend_id = ? AND scenario_id = ?`)
  .bind(friend.id, scenario.id)
  .first<{ id: string; status: string }>();
// ブロック→再追加時に completed の記録を削除して再エンロール
if (existing && existing.status !== 'active') {
  await db.prepare(`DELETE FROM friend_scenarios WHERE id = ?`).bind(existing.id).run();
}
if (!existing || existing.status !== 'active') {

## 1. 友だち追加時の挨拶シナリオを作成

POST /api/scenarios で以下のシナリオを作成：
- name: "友だち追加挨拶"
- triggerType: "friend_add"
- isActive: true

## 2. シナリオにステップを追加

ステップ1（stepOrder: 1、delayMinutes: 0、即時配信）：
- messageType: "flex"
- messageContent: 以下のFlex MessageをJSON文字列にして設定

{
  "type": "bubble",
  "body": {
    "type": "box",
    "layout": "vertical",
    "contents": [
      {
        "type": "text",
        "text": "友だち追加ありがとうございます！🎉",
        "weight": "bold",
        "size": "lg",
        "wrap": true
      },
      {
        "type": "text",
        "text": "どちらに興味がありますか？",
        "margin": "lg",
        "wrap": true
      }
    ]
  },
  "footer": {
    "type": "box",
    "layout": "vertical",
    "spacing": "sm",
    "contents": [
      {
        "type": "button",
        "style": "primary",
        "action": {
          "type": "message",
          "label": "X完全自動化",
          "text": "X完全自動化"
        }
      },
      {
        "type": "button",
        "style": "secondary",
        "action": {
          "type": "message",
          "label": "AI動画編集",
          "text": "AI動画編集"
        }
      }
    ]
  }
}

## 3. 自動応答ルールを2つ作成

npx wrangler d1 execute line-crm --remote --config=apps/worker/wrangler.toml \
  --command="INSERT INTO auto_replies (id, keyword, match_type, response_type, response_content, is_active, line_account_id) VALUES (lower(hex(randomblob(16))), 'X完全自動化', 'exact', 'text', 'X完全自動化に興味があるんですね！👏\n\nこちらの始め方ガイドをご覧ください👇\nhttps://x.com/mercarioji/status/2035255476620075519?s=20\n\nステップごとにコピペだけで設定できます。', 1, NULL)"

npx wrangler d1 execute line-crm --remote --config=apps/worker/wrangler.toml \
  --command="INSERT INTO auto_replies (id, keyword, match_type, response_type, response_content, is_active, line_account_id) VALUES (lower(hex(randomblob(16))), 'AI動画編集', 'exact', 'text', 'AI動画編集に興味があるんですね！🎬\n\nこちらのガイドをご覧ください👇\nhttps://x.com/mercarioji/status/2033146277522022640?s=20\n\n初心者でもすぐに始められます。', 1, NULL)"

## 4. Workerを再デプロイ

cd apps/worker && pnpm run deploy

## 5. 作成完了したら

作成したシナリオと自動応答ルールの内容を表示して、動作テストの方法を教えてください。
```

---

## 6. トラブルシューティング

| 症状 | 原因 | 対処 |
|---|---|---|
| Webhook Verify 失敗 | URLが違う・Workers未デプロイ | URL末尾に `/webhook` が付いているか確認。`cd apps/worker && pnpm run deploy` で再デプロイ |
| 401 Unauthorized | APIキー不一致 | `.env.local` の `NEXT_PUBLIC_API_KEY` と Workers の `API_KEY` シークレットが同じ値か確認 |
| 友だち追加しても管理画面に表示されない | Webhook が無効 | LINE Official Account Manager → 応答設定 → Webhook をオンに |
| 挨拶メッセージが二重に届く | LINE側の自動応答がオン | 応答メッセージ・あいさつメッセージを両方オフに |
| Cloudflare APIトークンエラー | トークン期限切れ・権限不足 | `dash.cloudflare.com/profile/api-tokens` でトークン確認・再発行 → `export CLOUDFLARE_API_TOKEN="新しいトークン"` で再設定 |
| それでも解決しない | 不明 | `/clear` で会話リセット後、プロンプトを再送（2回目は大体うまくいく） |

---

## 7. 検証記録（実施後に記入）

### STEP1 結果
- 実施日:
- 所要時間:
- Workers API URL:
- 管理画面 URL:
- Webhook URL:
- ハマったポイント:
- メモ:

### STEP2 結果
- 実施日:
- 友だち追加→挨拶: ✅ / ❌
- ボタンタップ→自動応答: ✅ / ❌
- メモ:

### STEP3 結果
- 3-1 BAN対策:
- 3-2 FAQ自動応答:
- 3-3 LP導線:

---

## 8. 関連リンク・参考

- LINE Harness GitHub: https://github.com/Shudesu/line-harness-oss
- LINE Harness 公式サイト: https://shudesu.github.io/line-harness-oss/
- 参考記事（今回の手順元）: Xポスト形式の解説記事（@mercarioji）
- 前回検証ログ: [[20260427_line-bot-mcp-server]]
- LINE Official Account Manager: https://manager.line.biz/
- LINE Developers Console: https://developers.line.biz/console/
- Cloudflare Dashboard: https://dash.cloudflare.com/
