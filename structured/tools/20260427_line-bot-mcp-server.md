# LINE Bot MCP Server 検証ログ

> ステータス: 検証中
> 作成日: 2026/04/27
> 最終更新: 2026/04/27
> ファイルパス: /Users/shogo/ObsidianVault/knowledge-vault/structured/tools/20260427_line-bot-mcp-server.md

---

## 📋 検証概要

- **ツール/サービス名**: LINE Bot MCP Server（`@line/line-bot-mcp-server`）
- **検証対象**: 新ツール
- **バージョン/リリース日**: Preview版（実験的目的向け）
- **検証期間**: 2026/04/27 -（検証中）
- **検証担当者**: s-tanaka
- **検証ステータス**: 検証中

---

## 1. 背景と検証目的

### なぜこの検証を行うのか
- Claude Code（MCP）からLINEメッセージを送信できるか確認したかった
- テキストメッセージおよびFlexメッセージをAIエージェントから自動送信するユースケースを想定

### 解決したい課題
- LINE通知・マーケティング配信をAIエージェントから直接操作できるようにしたい
- 手動でLINE配信する工数を削減したい

### 期待される効果・ビジネスインパクト
- AIエージェントがLINE通知を自動送信できるワークフローの実現
- Flexメッセージ（リッチなUIカード）も自動生成・送信できれば表現力が高まる

---

## 2. ツール/機能の基本情報

### 概要
- LINE公式が提供するMCPサーバー。Claude等のAIクライアントからLINE Messaging APIを通じてメッセージ送信・プロフィール取得を行える

### 提供元
- LINE株式会社（GitHub: `line/line-bot-mcp-server`）

### 主要機能
- `push_text_message` — ユーザーへのテキストメッセージ送信
- `push_flex_message` — リッチフォーマットのFlexメッセージ送信
- `get_profile` — ユーザープロフィール情報の取得

### 技術スタック・アーキテクチャ
- TypeScript製・Node.js v20以上必須
- ビルドツール: tsc（TypeScript compiler）
- フォーマッター: Prettier
- テスト: Vitest
- インストール方法: npx または Docker、またはローカルビルド

---

## 3. 検証方法

### 検証環境
- **使用アカウント**: LINE Developersアカウント（個人）
- **プラン/エディション**: Preview版
- **検証環境**: テスト
- **OS**: Windows（参考記事はLinux/macOS向けのため注意が必要）

### 検証シナリオ
1. LINE Developers ConsoleからChannel Access TokenとDestination User IDを取得
2. リポジトリをクローンして `npm install`
3. `npm run build` でビルド → distディレクトリ生成
4. Claude Desktopの `claude_desktop_config.json` にMCPサーバーを登録
5. Claudeから `push_text_message` ツールを呼び出してテキスト送信を確認
6. Claudeから `push_flex_message` ツールを呼び出してFlexメッセージ送信を確認

### 検証データ・サンプル
- テスト用LINEアカウントへの送信で動作確認

### 前提条件・制約事項
- LINE DevelopersアカウントおよびMessaging APIチャネルが必要
- Channel Access TokenとDestination User IDが必須
- Node.js v20以上が必要

---

## 4. 検証結果

### 定性的評価

#### 機能面の評価
- テキストメッセージ送信（`push_text_message`）: 動作確認済み
- Flexメッセージ送信（`push_flex_message`）: 動作確認済み
- ツール呼び出しのレスポンスは明確でわかりやすい

#### 操作性・UI/UX
- Claude Desktopからの設定は config.json への記述のみでシンプル
- Claude上でツール名・引数が明示されるため操作しやすい

#### 出力品質
- 送信したメッセージがLINEアプリに届くことを確認
- Flexメッセージのレンダリングも正常

#### 実用性
- AIエージェントがLINE通知を自動送信するユースケースに十分対応可能
- Preview版のため本番利用には注意が必要

---

### 定量的評価

#### 導入コスト

| 項目 | 内容 | 金額/工数 |
| --- | --- | --- |
| 初期設定時間 | LINE Developers登録〜Claude Desktop設定完了まで | 1〜2時間程度 |
| 学習時間 | 基本操作を習得するまで | 30分程度 |
| 初期費用 | セットアップ、ライセンス購入等 | 無料 |

#### 運用コスト

| 項目 | 内容 | 金額 |
| --- | --- | --- |
| 月額利用料 | | 無料（LINE Messaging API基本料金内） |
| 年額利用料 | | （情報なし） |
| 従量課金 | LINE Messaging API送信数に依存 | 無料枠あり（超過分は有料） |
| 追加オプション | | （情報なし） |

#### パフォーマンス

| 項目 | 測定結果 | 備考 |
| --- | --- | --- |
| 処理速度 | （随時更新） | |
| レスポンスタイム | （随時更新） | |
| 同時処理数 | （随時更新） | |
| 成功率 | （随時更新） | |

#### ROI試算
- **削減できる工数**:（随時更新）
- **生産性向上**:（随時更新）
- **コスト削減額**:（随時更新）
- **投資回収期間**:（随時更新）

---

## 5. 比較・優位性分析

### 既存ツール/類似サービスとの比較

| 項目 | LINE Bot MCP Server | UTAGE MCP | Lメッセージ MCP |
| --- | --- | --- | --- |
| 機能性 | テキスト/Flex送信・プロフィール取得 | ファネル・LP・配信管理全般 | （要調査） |
| コスト | 無料（LINE API費用のみ） | （要調査） | （要調査） |
| 使いやすさ | セットアップにビルドが必要 | 接続URL登録のみ | （要調査） |
| 連携性 | LINE Messaging API | UTAGEのAPI全般 | Lメッセージ配信 |
| サポート | Preview版・GitHubのみ | ヘルプドキュメントあり | （要調査） |

### 優位性
- LINE公式が提供しているため信頼性が高い
- テキスト/Flex両対応でリッチな通知が可能
- 無料で試せる

### 劣位性・懸念点
- Preview版のため仕様変更リスクあり
- Windowsでのビルドに追加手順が必要（→ セクション9参照）
- push送信のみでincoming webhook等は対象外

---

## 6. リスク評価

### セキュリティ

| 評価項目 | 評価 | 詳細 |
| --- | --- | --- |
| データ保管場所 | ローカル | Channel Access TokenはローカルのconfigファイルまたはENVで管理 |
| 暗号化 | （随時更新） | |
| アクセス制御 | Channel Access Tokenによる認証 | Tokenが漏洩するとメッセージ送信が可能になるため厳重管理が必要 |
| ログ管理 | （随時更新） | |
| コンプライアンス | LINE Messaging API利用規約に準拠 | |

### プライバシー・倫理面
- Destination User IDの管理に注意（個人を特定する情報）
- Channel Access Tokenをconfigファイルにベタ書きしない（環境変数で管理推奨）

### ベンダーロックインリスク
- LINE Messaging APIに依存するためLINEの仕様変更の影響を受ける
- Preview版のため廃止リスクあり

### 技術的リスク
- Node.js v20以上が必要（バージョン管理に注意）
- Windowsでは追加対応が必要（→ セクション9参照）

---

## 7. 連携性・拡張性

### 既存システムとの連携

| 連携先 | 方法 | 難易度 | 備考 |
| --- | --- | --- | --- |
| Claude Desktop | claude_desktop_config.json | 低 | 公式対応 |
| Claude Code | MCP設定ファイル | 低 | 同様の設定で動作 |
| LINE Messaging API | Channel Access Token | 中 | LINE Developersアカウント必要 |

### API/統合オプション
- LINE Messaging APIのpush送信エンドポイントをMCPでラップしている構造
- Dockerでの実行も可能（Windowsでのビルド回避策として有効）

### 拡張性・カスタマイズ性
- OSS公開のためフォークして独自ツールを追加可能
- 現状のツールは3つ（push_text / push_flex / get_profile）とシンプル

---

## 8. 実際の使用例・サンプル

### ユースケース1: テキストメッセージ送信

**シナリオ**: ClaudeからLINEにテキスト通知を送信する
**入力**: 「〇〇さんにLINEで『明日の会議は10時からです』と送って」
**出力**: LINEアプリに指定テキストが届く
**評価**: 正常動作を確認

### ユースケース2: Flexメッセージ送信

**シナリオ**: ClaudeからリッチなカードUIをLINEで送信する
**入力**: Flexメッセージ用JSONを指定してpush_flex_messageを呼び出す
**出力**: LINEアプリにカードレイアウトのメッセージが届く
**評価**: 正常動作を確認

### スクリーンショット・デモ
- （随時更新）

---

## 9. 学びとナレッジ

### 発見したこと
- LINE公式提供のMCPサーバーが既にテキスト/Flex送信に対応している
- セットアップはChannel Access TokenとUser IDがあればすぐ試せる

### うまくいったこと
- テキストメッセージ・Flexメッセージともに送信成功
- Claude Desktopからの操作はシンプルで直感的

### うまくいかなかったこと
- **Windowsでのビルドエラー**（詳細は下記「よくあるエラーと対処法」参照）

### Tips・ベストプラクティス
- Channel Access TokenとUser IDは環境変数で管理する（configファイルへのハードコードは避ける）
- Dockerを使うとWindows環境でもビルドなしで実行できる

### よくあるエラーと対処法

#### ⚠️ Windows環境でのビルドエラー: `rm` コマンドが認識されない

**現象**:
`npm run build` を実行すると以下のようなエラーが発生する。

```
'rm' は、内部コマンドまたは外部コマンド、
操作可能なプログラムまたはバッチ ファイルとして認識されていません。
```

**原因**:
`package.json` の `clean` スクリプトにUnix系コマンド `rm -rf` が使用されており、Windowsでは認識されない。`build` スクリプトは内部で `clean` を呼び出すため、ビルドが失敗する。

```json
// package.json 該当箇所
"clean": "rm -rf dist/*",
"build": "npm run format:check && npm run typecheck:test && npm run clean && tsc && shx chmod +x dist/*.js"
```

**対処法①: rimraf を使う（推奨）**

クロスプラットフォーム対応の `rm -rf` 相当ツール。

```bash
npm install --save-dev rimraf
```

`package.json` の `clean` スクリプトを書き換える：

```json
"clean": "rimraf dist/*"
```

その後 `npm run build` を再実行。

**対処法②: PowerShellで手動削除してからビルド**

```powershell
Remove-Item -Recurse -Force dist\*
npx tsc
```

**対処法③: Dockerを使う（ビルド不要）**

公式のDockerイメージを使えばWindowsでのビルドをスキップできる。

```bash
docker pull ghcr.io/line/line-bot-mcp-server
```

---

## 10. 判定と今後のアクション

### 総合評価
⭐️⭐️⭐️⭐️（完了時に確定）

### 導入判定
- [ ] 即座に導入推奨
- [x] 条件付きで導入可（Preview版のため本番利用は慎重に）
- [ ] 追加検証が必要
- [ ] 導入見送り

### 判定理由
- テキスト/Flex送信ともに動作確認済みで実用的
- Preview版のため本番導入は仕様安定後が望ましい
- Windowsでの追加対応（rimrafまたはDocker）が必要な点は注意

### 次のステップ

#### 🔜 次にやりたいこと: LINEマーケティング周りのMCP展開

LINE/LINEマーケティングに関連したMCPが続々登場している。以下を今後検証したい。

| ツール | 状況 | 概要 | 優先度 |
| --- | --- | --- | --- |
| **UTAGE（宴）MCP** | ✅ MCP対応済み | ファネル・LP・配信管理をAIから直接操作可能。Claude Code対応済み。接続URLを登録して認証するだけで使える | 高 |
| **Lメッセージ MCP** | 要調査 | LINE配信ツールのMCP連携。詳細は引き続き調査 | 中 |

**UTAGE MCPの操作例:**
- 「新しいファネルを作成してLPページを追加して」
- 「配信アカウントの一覧を見せて」
- 「このページのヘッドラインを変更して」

**LINE Bot MCP → UTAGE MCP の連携シナリオ:**
- LINE Bot MCPで個別通知 × UTAGE MCPでファネル・シナリオ管理を組み合わせることでLINEマーケティングの自動化が実現できる可能性がある

### 追加で検証したい項目
- [ ] UTAGE MCP のセットアップと基本操作
- [ ] Lメッセージ MCPの存在確認と機能調査
- [ ] LINE Bot MCP × UTAGE MCPの連携シナリオ設計
- [ ] 本番環境でのChannel Access Token管理方法

---

## 📚 関連リソース

### 公式ドキュメント
- [line/line-bot-mcp-server — GitHub](https://github.com/line/line-bot-mcp-server)
- [package.json（ビルドスクリプト詳細）](https://github.com/line/line-bot-mcp-server/blob/main/package.json)

### 参考記事・事例
- [LINE Bot MCPサーバーを使ってみた — Classmethod](https://dev.classmethod.jp/articles/line-bot-mcp-server/)
- [UTAGE API機能・AI連携（MCP）リリース](https://help.utage-system.com/archives/25648)

### 社内関連ドキュメント
- （情報なし）

### 検証データ・ログ
- （随時更新）

---

## ✅ メモ・議論ログ
- 参考にしたサイト（Classmethod記事）はLinux/macOS向けの解説。Windowsで手順通り進めるとビルドエラーになるので注意
- WindowsユーザーはrimrafかDockerを使うと詰まらずに済む
- UTAGE MCPはすでにClaude Code対応済みなので次のセッションで試せる

---

## 📝 更新ログ
<!-- このセクションはスキルが自動で追記する。手動編集不要。 -->
| 日時 | 更新内容の概要 |
|---|---|
| 2026/04/27 | ファイル作成（init）— テキスト/Flex送信検証内容・Windowsビルドエラー対処法・UTAGE/Lメッセージの次ステップを記録 |
