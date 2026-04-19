# MiniMax CLI（mmx-cli）検証ログ

> ステータス: 完了
> 作成日: 2026/04/18
> 最終更新: 2026/04/18
> ファイルパス: structured/tools/20260418_minimax-mmx-cli.md

---

## 検証概要

- **ツール/サービス名**: MiniMax CLI（mmx-cli）
- **検証対象**: TTS・動画・画像・音楽生成パイプラインのCLI置き換え可否
- **バージョン**: 2026年4月リリース（OSSの公式CLIツール）
- **検証期間**: 2026/04/18
- **検証ステータス**: 完了

---

## 1. 背景と検証目的

### なぜこの検証を行うのか

MiniMax APIを使ったTTSや動画生成のパイプラインを作るとき、これまではPython/TypeScriptで専用スクリプトを書いてLLMからそのスクリプトを呼び出す方法を取っていた。

MiniMaxが公式CLIツール「mmx-cli」をリリースしたという情報を見かけて「スクリプト不要になるのではないか」と思い、ドキュメントを全部読んで限界値を確認した。

### 解決したい課題

- n8n・Claude Code・Difyなどのワークフロー自動化でMiniMax APIを直接叩く専用スクリプトを排除したい
- LLMエージェントからMiniMaxの各機能をシェル一行で呼び出せるか確認する

---

## 2. ツール基本情報

| 項目 | 内容 |
|---|---|
| 提供元 | MiniMax（OSSで公開）|
| リポジトリ | https://github.com/MiniMax-AI/cli |
| インストール | `npm install -g mmx-cli` |
| 認証 | `mmx auth login --api-key sk-xxxxx` |
| エージェント対応 | Claude Code・Cursor・OpenCodeなどのAIエージェント向け設計 |

---

## 3. できること・できないこと（機能別）

### テキスト生成（mmx text）

**✅ CLIで完結**
- マルチターン会話（`--message`複数渡し or JSONファイル読み込み）
- ストリーミング出力（`--stream`）
- システムプロンプト指定（`--system`）
- モデル切り替え：`MiniMax-M2.7`（デフォルト）、`MiniMax-M2.7-highspeed`
- JSON出力モード（`--output json`）
- ツール定義の渡し込み（`--tool`フラグ）
- temperature・top-p・max-tokensの調整

**❌ できないこと**
- Function Calling の実行自体はCLI側では行わない（定義を渡すだけ）

---

### 画像生成（mmx image）

**✅ CLIで完結**
- テキストから画像生成（`image-01`モデル固定）
- アスペクト比指定（`--aspect-ratio 16:9`など）
- バッチ生成（`--n 3`で3枚同時）
- キャラクター一貫性（`--subject-ref type=character,image=path`）
- 出力ディレクトリ指定・ファイル名プレフィックス指定

**❌ できないこと**
- モデルの切り替え（`image-01`のみ）
- インペインティングや画像編集（生成のみ）

---

### 動画生成（mmx video）

**✅ CLIで完結**
- テキストプロンプトから動画生成（デフォルト：`MiniMax-Hailuo-2.3`）
- 高速版モデル切り替え（`--model MiniMax-Hailuo-2.3-Fast`）
- 非同期実行→task IDで進捗ポーリング（`--async` + `mmx video task get`）
- ダウンロードまで自動待機（`--download sunset.mp4`）
- 最初のフレーム画像を指定（`--first-frame`）
- 完了時のWebhook通知（`--callback-url`）

**⚠️ 要検証・不明点**
- 解像度・秒数の指定（768P/1080P、6s/10sの選択がCLIフラグ上で明示されていない）
- Hailuo-02の512P対応（Pay as You Goでは$0.10と最安値だが、CLIでの指定方法不明）

---

### TTS・音声合成（mmx speech）

**✅ CLIで完結**（想像より全部入りだった）
- 30種類以上のプリセットボイス（`mmx speech voices`で一覧確認可能）
- speed・volume・pitchの調整
- ストリーミング再生（`--stream | mpv -`でリアルタイム再生）
- ファイルから読み込み（`--text-file -`でstdinも可）
- 字幕タイミングデータの取得（`--subtitles`）
- 音響エフェクト追加（`--sound-effect`）
- カスタム発音指定（`--pronunciation from/to`）
- モデル切り替え：`speech-2.8-hd`（デフォルト）、`speech-2.6`、`speech-02`
- 40言語対応（`--language`でブースト）
- 出力フォーマット・サンプルレート・ビットレート・チャンネル数の細かい指定

**❌ できないこと**
- クローンボイスの**登録**はCLI非対応（下記参照）

---

### ボイスクローン——ここだけ注意が必要

**✅ 登録済みクローンボイスの利用はCLI可（おそらく）**

`--voice voice_clone_xxxxx` という形でvoice_idを渡せば、登録済みクローンボイスでのTTSはCLIから実行できる可能性が高い。ただし未検証。

**❌ クローンボイスの登録はCLI非対応**

音声クローンの登録フローはAPIを直接叩く必要がある。

1. 音声ファイルをFile Upload APIでアップロード → `file_id`取得
2. Voice Clone APIに `file_id` と任意の `voice_id` を渡してクローン作成
3. 生成された `voice_id` をTTS APIに渡して合成

**整理：「クローンボイスを新規登録するときだけスクリプトが必要」。一度登録してしまえば、あとはCLIで運用できる。**

**❌ voice_design（プロンプトからボイス生成）はCLI非対応**

カスタムボイスをテキスト説明から生成する `voice_design` 機能は、MCPサーバー経由でのみ利用可能。CLIには未実装。

---

### 音楽生成（mmx music）

**✅ CLIで完結**（フラグが最も多い。かなり細かく制御できる）
- 歌詞付き生成（`--lyrics`で直接、または`--lyrics-file`でファイル指定）
- インストゥルメンタル（`--instrumental`）
- ボーカルスタイル指定（`--vocals "male and female duet, harmonies in chorus"`）
- ジャンル・ムード・楽器・テンポ・BPM・キー（それぞれ個別フラグ）
- 曲の構成指定（`--structure "verse-chorus-verse-bridge-chorus"`）
- 参照アーティスト指定（`--references "similar to Ed Sheeran"`）
- 避けたい要素の指定（`--avoid`）
- AIGCウォーターマーク埋め込み（`--aigc-watermark`）

**⚠️ 要確認**
- カバー生成（参照音声から新しいボーカルで歌わせる機能）はMCP版にある記述があるが、CLI版では確認できず

---

### 画像理解（mmx vision）

**✅ CLIで完結**
- ローカルファイル・URL・file_idのいずれかを指定
- 自由なプロンプトで質問（`--prompt "What breed?"`）
- JSON出力対応

**❌ できないこと**
- 複数画像の同時入力
- 動画理解（画像のみ）

---

### エージェント連携・パイプ処理

**✅ CLIで完結**（最大のポイント）

エージェント（Claude Code等）からの自動実行を想定した設計になっている。

- `--non-interactive`：対話プロンプトを出さずにエラーで即終了
- `--quiet`：スピナーなし、stdoutが純粋なデータのみ
- `--output json`：機械可読なJSON出力
- `--dry-run`：APIを実際に叩かずにリクエスト内容を確認
- `mmx config export-schema`：全コマンドをAnthropicやOpenAI互換のツール定義JSONとしてエクスポート

```bash
# stdoutが純粋データなので安全にパイプできる
URL=$(mmx image generate --prompt "A sunset" --quiet)
mmx vision describe --image "$URL" --quiet

# 非同期動画生成のワークフロー
TASK=$(mmx video generate --prompt "A robot" --async --quiet | jq -r '.taskId')
mmx video task get --task-id "$TASK" --output json
mmx video download --task-id "$TASK" --out robot.mp4
```

---

## 4. 料金体系（Pay as You Go）

| 種別 | 単価 |
|------|------|
| テキスト（M2.7 input） | $0.3 / Mトークン |
| テキスト（M2.7 output） | $1.2 / Mトークン |
| 動画（Hailuo-2.3-Fast 768P 6s） | $0.19 / 本 |
| 動画（Hailuo-2.3 768P 6s） | $0.28 / 本 |
| 動画（Hailuo-2.3 1080P 6s） | $0.49 / 本 |
| TTS turbo | $60 / M文字 |
| TTS HD | $100 / M文字 |
| 音楽生成（Music-2.6） | $0.15 / 曲（〜5分） |
| 画像生成（image-01） | $0.0035 / 枚 |
| ボイスクローン（Rapid） | $1.5 / ボイス |

ボリュームを一定以上使うなら Token Plan（月額$10〜）の方がコスパが良い場面もある。

---

## 5. まとめ：スクリプト置き換え可否

| やりたいこと | 置き換え可否 |
|---|---|
| TTS（プリセットボイス） | ✅ 完全置き換え可能 |
| 動画生成→ダウンロード | ✅ 完全置き換え可能 |
| 画像生成 | ✅ 完全置き換え可能 |
| 音楽生成（歌詞・スタイル細かく指定） | ✅ 完全置き換え可能 |
| TTS（クローンボイス使用） | ⚠️ 登録だけAPIが必要。使用はCLI可（要検証） |
| クローンボイス登録 | ❌ スクリプト継続必要 |
| voice_design | ❌ MCP経由のみ |

Claude Codeから `npx skills add MiniMax-AI/cli -y -g` で一発追加できる。

---

## 6. 参考リンク

- [MiniMax CLI GitHub](https://github.com/MiniMax-AI/cli)
- [公式CLIドキュメント](https://platform.minimax.io/docs/token-plan/minimax-cli)
- [Pay as You Go 料金表](https://platform.minimax.io/docs/guides/pricing-paygo)
- [Token Plan 料金表](https://platform.minimax.io/docs/guides/pricing-token-plan)
