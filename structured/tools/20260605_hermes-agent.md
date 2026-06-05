# Hermes Agent 検証ログ

> ステータス: 完了
> 作成日: 2026/06/05
> 最終更新: 2026/06/05
> ファイルパス: /Users/shogo/Documents/ai-business-os/15_ナレッジ基盤/vault/structured/tools/20260605_hermes-agent.md

---

## 📋 検証概要

- **ツール/サービス名**: Hermes Agent（Nous Research）
- **検証対象**: 新ツール（オープンソースの自律AIエージェント基盤）
- **バージョン/リリース日**: v0.15.2（2026年時点・MITライセンス）
- **検証期間**: 2026/06/05（公開ドキュメント・公開サイトの机上調査のみ）
- **検証担当者**: 田中省伍
- **検証ステータス**: 完了
- **調査手段**: Browser Use CLI で公開サイトを巡回 ＋ 公開されている `/llms-full.txt`（全61,352行のドキュメント全文ダンプ）を取得・精読。実際のインストール・実行は未実施（机上調査）。

---

## 1. 背景と検証目的

### なぜこの検証を行うのか
- 「Hermes Agent とは何がどこまでできるのか」を、エージェント本体だけでなく CLI / WebUI / Desktop / メッセージング連携まで含めて業務目線で把握するため。
- Claude Code・Devin・OpenHands といった既存コーディングエージェントとの位置づけの違いを明確にし、自社・顧客の業務自動化で使えるかを判断するため。

### 解決したい課題
- AIエージェントを「IDE内のコーディング補助」から「サーバー常駐・複数チャネル運用の業務エージェント」へ広げたい。
- 補助金リサーチ・SNS発信・定例レポートなど、当方が抱える反復業務をエージェントに常駐委譲できるかを見極めたい。

### 期待される効果・ビジネスインパクト
- MITライセンスのOSSで、LLM API課金以外のソフト費用ゼロ。セルフホストで自社サーバー常駐エージェントを構築できる可能性。
- Telegram/Slack/Discord/Email など普段のチャネルから自然言語で業務指示 → 自動実行 → 定例化（cron）まで一気通貫にできる。

---

## 2. ツール/機能の基本情報

### 概要
Hermes Agent は Nous Research が提供する**オープンソース（MITライセンス）の自律型AIエージェント**。公式の位置づけは「IDEに縛られたコーディング副操縦士でも、単一APIをラップしたチャットボットでもない」「自分のサーバー上に常駐し、学んだことを記憶し、長く動かすほど賢くなるエージェント」。

特徴を一言でいうと「**どこにでも住む（Lives Where You Do）／長く動かすほど育つ（Grows the Longer It Runs）常駐型エージェント**」。コーディング特化ではなく、Web調査・ブラウザ操作・画像生成・音声・定例自動化まで含む汎用業務エージェント。

### 提供元
- **Nous Research**（https://nousresearch.com ）。自社で Hermes 4 系（Hermes-4-70B / 405B）など独自モデルも開発しているAI研究組織。
- リポジトリ: https://github.com/NousResearch/hermes-agent （MIT License・2026）
- 公式サイト: https://hermes-agent.nousresearch.com/

### 主要機能（4つのインターフェース）
Hermes は「同一のエージェントコア・同一の設定/セッション/スキル/メモリ」を、複数のフロントエンドから操作する設計。CLIで設定したものがDesktopにもWebにも反映され、状態を共有する。

1. **CLI / TUI**（`hermes`, `hermes --tui`）: ターミナルUI本体。マルチライン編集、スラッシュコマンド補完、ストリーミング、割り込み&リダイレクト、バックグラウンドセッション、git worktree並列実行。
2. **Web Dashboard**（`hermes dashboard` → `http://127.0.0.1:9119`）: ブラウザ管理UI。設定/APIキー/セッション/ログ/cronをGUI管理。Chatタブはxterm.js経由でTUIをそのまま埋め込み。**完全ローカル実行**（データはlocalhostから出ない）。
3. **Desktop App**（macOS/Windows/Linux・Electron製）: チャット中心のネイティブGUI。ファイルブラウザ、プレビューレール、音声、設定UI、マルチ会話、Agents/Command Centerによるオーケストレーション面。
4. **Messaging Gateway**: 単一の常駐プロセスが Telegram, Discord, Slack, WhatsApp, Signal, SMS, Email, Matrix, Mattermost, Teams, LINE, Home Assistant ほか20+チャネルに接続。1インスタンスを複数人・複数チャネルで共有。

### 技術スタック・アーキテクチャ
- 実装は Python（`run_agent.py` の `AIAgent` クラスが中核）。CLI/Gateway/Desktop/Dashboard すべて同じコアを駆動。
- セッションは SQLite（`~/.hermes/state.db`）に保存（メタ情報・履歴・全文検索インデックス）。
- LLMは**OpenAI互換API**なら何でも接続可。OpenRouter / Nous Portal / OpenAI / Anthropic / Google / z.ai / Kimi / MiniMax、ローカル（Ollama/vLLM/llama.cpp/SGLang）まで。
- Gateway は60秒ごとにcronスケジューラをtick。各プラットフォームadapter→per-chatセッションストア→AIAgentの流れ。
- 設定は `~/.hermes/config.yaml`、秘密情報は `~/.hermes/.env`(0600) に分離。

---

## 3. 検証方法

### 検証環境
- **使用アカウント**: なし（未ログイン・公開ページのみ）
- **プラン/エディション**: OSS本体（無料）。Nous Portal等の有料サブスクは未契約。
- **検証環境**: 机上調査（Browser Use CLIによる公開サイト巡回＋公式ドキュメント全文の取得・精読）。実インストール・実行は未実施。

### 検証シナリオ
1. トップページ（https://hermes-agent.nousresearch.com/ ）を開き、ナビ/フッター/CTAから導線（DOCS / PORTAL / DESKTOP APP / GitHub / Discord）を抽出。
2. `/docs` を開き、ドキュメントサイトの全ナビゲーション構造を取得。
3. 公開されている `/docs/assets/files/llms-full-*.txt`（LLM向け全文ダンプ・約61,000行）を取得し、機能セクションを系統的に精読。
4. 機能ごとに「できること」と「業務活用アイデア」を抽出。

### 検証データ・サンプル
- 取得した一次資料: トップページHTML/テキスト、`/docs` ナビ構造、`llms-full.txt`（全文）、トップページのスクリーンショット（/tmp/hermes-home.png）。

### 前提条件・制約事項
- 公開ドキュメントベースの机上評価。実機での精度・安定性・コスト実測は未実施（「定量的評価」は公称値ベース）。
- Nous Portal の具体的な料金プラン・金額は本サイト上には明示されておらず（portal.nousresearch.com 側で要ログイン/サインアップ）、本ログでは「（要ログイン・未検証）」とする。

---

## 4. 検証結果

### 定性的評価

#### 機能面の評価（機能ごとに「できること／業務活用」）

**A. エージェント本体（自律実行）**
- できること: 自然言語タスクを受け、`web_search`/`web_extract`/`terminal`/`read_file`/`patch`/`browser_*`/`vision_analyze`/`image_generate`/`text_to_speech`/`memory`/`delegate_task`/`execute_code`/`cronjob`/`send_message` などのツールをループで自律実行。toolsetは `web,terminal,skills` のように選択可能。
- 業務活用: 「最新のGRPO学習手法を調べて要約して」のような調査タスク、ファイル横断分析、定例レポート生成などをエンドツーエンドで委譲。

**B. 永続メモリ & スキル（“育つ”中核）**
- できること: **メモリ**＝事実（ユーザー/プロジェクト/環境の知識、`MEMORY.md`/`USER.md`）を関連度ベースで自動想起。**スキル**＝手順（やり方の段階的手順書）を類似タスク時に想起。agentskills.io オープン標準互換、progressive disclosureでトークン節約。
- 業務活用: 当方の knowledge-vault / SNS発信フォーマット / 補助金リサーチ手順などを「スキル」として持たせ、繰り返すほど運用が固まる。当方既存の `.claude/skills` 運用思想と親和性が高い。

**C. スケジュール自動化（cron）**
- できること: 自然言語またはcron式で定期実行。ジョブにスキルを紐付け、結果を任意プラットフォームへ配信、pause/resume/edit対応。Gatewayが60秒ごとに評価。
- 業務活用: 毎朝のデイリーブリーフィング、定例バックアップ、補助金の月次チェック、SNSネタの定期リサーチを無人運用。

**D. サブエージェント委譲 & 並列化**
- できること: `delegate_task` で独立コンテキスト・制限付きツールセット・専用ターミナルを持つ子エージェントを生成（既定3並列・設定可）。`execute_code` でPythonからHermesツールをRPC呼び出しし多段ワークフローを1ターンに圧縮。
- 業務活用: 「複数観点の並列調査」「大量ファイルの分担処理」をゼロコンテキストコストのパイプラインで実行。

**E. サンドボックス（5バックエンド）**
- できること: terminalバックエンドを local / docker / ssh / singularity / modal / daytona から選択。コンテナはread-onlyルートFS・全capability drop・特権昇格禁止・PID上限256・namespace分離でハードニング。Dockerは1コンテナをセッション全体で永続共有（pip installが持続）。
- 業務活用: 信頼できないコード実行や顧客環境を汚さないリモート実行。SSHバックエンドは「エージェントが自分のコードを改変できない」分離構成として推奨。

**F. フル Web & ブラウザ操作**
- できること: Web検索/抽出、ブラウザ自動化（Browserbase/Browser Use cloud/ローカルChrome等CDP接続）、ビジョン、画像生成（FAL.ai・9モデル）、TTS（10プロバイダ、Edge TTSは無料）、マルチモデル推論。
- 業務活用: フォーム入力・情報抽出の自動化、画像生成、音声応答。当方のBrowser Use CLI運用と用途が重なる。

**G. マルチチャネル常駐（Messaging Gateway）**
- できること: 20+チャネル（Telegram/Discord/Slack/WhatsApp/Signal/SMS/Email/Matrix/Mattermost/Teams/LINE/Home Assistant 等）に単一プロセスで接続。プラットフォームごとにVoice/Images/Files/Threads/Reactions/Typing/Streaming対応度が異なる（Telegram/Discord/Slack/Matrix/Feishuがフル対応寄り）。1インスタンスを複数人で共有可。
- 業務活用: 普段使うチャットから業務指示。チーム共有のアシスタントBot、Home Assistant連携で音声/家電操作も。

**H. 連携・拡張（MCP/API/IDE）**
- できること: 任意のMCPサーバーをstdio/HTTPで接続（GitHub/DB/社内API等）。OpenAI互換APIサーバーとして公開（Open WebUI/LobeChat/LibreChat接続）。ACP対応エディタ（VS Code/Zed/JetBrains）にエージェント・差分・ターミナルを表示。プラグイン機構（tools/hooks/memory provider/context engine）。
- 業務活用: 既存の社内ツール群をMCP経由で接続し、Hermesを“ハブ”化。当方の mcp-usage-strategy（MCPとCLIの使い分け）の知見と直結。

**I. その他注目機能**
- Web Dashboard内に **150+設定項目のフォームエディタ**、APIキー管理、セッション全文検索（FTS5）、ログのライブtail。
- **チェックポイント/ロールバック**（ファイル変更前に自動スナップショット、`/rollback`）。
- **バッチ処理**（数百〜数千プロンプトを並列実行しShareGPT形式のtrajectory生成 → 学習データ/評価向け）。
- **Personality/SOUL.md** による人格カスタマイズ、Skins/Themes。
- **プロンプトキャッシュ**（Claude系で1時間プレフィックスキャッシュ・常時ON・設定不要）。

#### 操作性・UI/UX
- インストールはワンライナー（`curl ... install.sh | bash`、Windowsは `iex (irm install.ps1)`）。`hermes setup --portal` 一発でモデル＋ツールゲートウェイまで構成完了を謳う。
- CLIはステータスバー（モデル/トークン/コンテキスト充填率/コスト/経過時間/YOLO警告）など作り込みが厚い。Claude Code利用者には馴染みやすい思想。
- 4インターフェースが状態共有で相互レジューム可能（CLIで開始→Desktopで再開、等）。

#### 出力品質
- 出力品質は使用するLLM依存（Hermes自体はエージェントランタイム）。公式は agent用途に Claude Sonnet 4.6 / GPT-5.5 Pro / Gemini 3 Pro / DeepSeek V4 Pro 等のフロンティアモデルを推奨。自社モデル Hermes 4 は「チャット/推論向けでツールコールのループには不向き」と公式が明言（agent用途には非推奨）。

#### 実用性
- 「サーバー常駐＋複数チャネル＋定例自動化＋記憶」という組み合わせは、コーディング補助型エージェント（Claude Code/Cursor等）とは別レイヤーの実用性。業務自動化OS的な使い方に向く。

### 定量的評価

#### 導入コスト
| 項目 | 内容 | 金額/工数 |
| --- | --- | --- |
| 初期設定時間 | ワンライナーインストール＋`hermes setup --portal` | 公称「2分以内」 |
| 学習時間 | CLI基本操作（Claude Code経験者なら低） | 数十分〜（体感未実測） |
| 初期費用 | ソフトウェア本体 | 0円（MIT OSS） |

#### 運用コスト
| 項目 | 内容 | 金額 |
| --- | --- | --- |
| 月額利用料 | Hermes Agent本体 | 0円（OSS） |
| 従量課金 | 接続したLLMプロバイダのAPI課金のみ | プロバイダ依存（ローカルモデルなら0円） |
| 追加オプション | Nous Portal サブスク（300+モデル＋Tool Gateway一括） | （要ログイン・未検証／portal側で確認要） |

#### パフォーマンス
| 項目 | 測定結果 | 備考 |
| --- | --- | --- |
| 処理速度 | （情報なし） | 机上調査のため未実測 |
| 同時処理数 | サブエージェント既定3並列（設定可）／バックグラウンドセッション複数 | 公称 |
| コンテナ既定 | CPU1コア/メモリ5GB/ディスク50GB | container_* で変更可 |

#### ROI試算
- **削減できる工数**: 定例リサーチ/レポート/SNSネタ収集の無人化により、反復作業の時間削減が期待（具体値は要PoC）。
- **コスト削減額**: 本体無料＋ローカルモデル併用で、SaaS型エージェント費用を圧縮可能。
- **投資回収期間**: ソフト費用ゼロのため、API課金を上回る工数削減が出れば即回収（要実測）。

---

## 5. 比較・優位性分析

### 既存ツール/類似サービスとの比較
| 項目 | Hermes Agent | Claude Code | Devin / Cursor等 |
| --- | --- | --- | --- |
| 位置づけ | サーバー常駐の汎用業務エージェント | ターミナル/IDEのコーディングエージェント | コーディング自律/IDE統合 |
| ライセンス/料金 | OSS(MIT)・本体無料 | 商用（API/サブスク） | 商用 |
| モデル | 任意のOpenAI互換（マルチプロバイダ・ローカル可） | Anthropic中心 | 各社 |
| チャネル | CLI/TUI/Web/Desktop/20+メッセージング | CLI/IDE/Web/Desktop | 主にIDE/Web |
| 常駐・cron | ◎（Gateway常駐＋自然言語cron） | △ | △ |
| 記憶/スキル | ◎（永続メモリ＋agentskills.io互換） | ◎（CLAUDE.md/メモリ/スキル） | ○ |
| セルフホスト | ◎ | × | × |

### 優位性
- **OSS・セルフホスト・マルチプロバイダ**：ベンダーロックインを避けつつローカルモデルで完全無料運用も可能。
- **常駐＋マルチチャネル＋cron**：チャットUIから業務を“住まわせる”運用がしやすい。
- 4インターフェース状態共有・MCP/ACP/API互換で既存エコシステムに溶け込む。

### 劣位性・懸念点
- コーディング特化IDE統合の作り込みは専用ツール（Cursor/Claude Code）に一日の長。Hermesはコード兼汎用ゆえ、純コーディング用途では比較検証が必要。
- 自社開発・運用責任が自分側（OSS常駐＝サーバー/セキュリティ/アップデート管理は自己責任）。
- ドキュメント上、WindowsネイティブとWSL2前提の記述が混在（FAQは「ネイティブ不可・WSL2前提」、インストール節はネイティブWindows対応を明記）。バージョンにより差異がある可能性 → 実機確認推奨。

---

## 6. リスク評価

### セキュリティ
| 評価項目 | 評価 | 詳細 |
| --- | --- | --- |
| データ保管場所 | ◎ローカル | 会話/メモリ/スキルは `~/.hermes/` にローカル保存。テレメトリ/解析の収集なし。APIは設定したLLMプロバイダにのみ送信。 |
| 認可制御 | ◎ | Gatewayは既定で全拒否（allowlist or DMペアリング必須）。admin/userの2層権限。 |
| 危険コマンド承認 | ◎ | 危険パターンに承認プロンプト（manual/smart/off）。`rm -rf /`・fork bomb・`mkfs`等は**ハードライン・ブロックリスト**でYOLOでも実行不可。 |
| コンテナ分離 | ◎ | read-onlyルート・cap全drop・特権昇格禁止・namespace分離。 |
| 認証情報管理 | ○ | `.env`(0600)に分離。Nous PortalはOAuthのrefresh tokenのみ保存し短命JWTを都度発行。 |

### プライバシー・倫理面
- ローカル完結・テレメトリなしはプライバシー上有利。一方、ブラウザ操作/メッセージング自動化は対象サービスの規約順守が前提。

### ベンダーロックインリスク
- 低い。OSS＋OpenAI互換マルチプロバイダ＋ローカルモデルで脱ロックイン可能。ただしNous Portalの便利さに寄せると一定の依存は生じる。

### 技術的リスク
- 常駐サービスとしての運用（systemd/launchd）、セキュリティ更新、MCP/外部キー管理は自己責任。`--yolo`/`approvals.mode: off`の誤用で破壊的操作のリスク（ハードラインで最悪は防止）。

---

## 7. 連携性・拡張性

### 既存システムとの連携
| 連携先 | 方法 | 難易度 | 備考 |
| --- | --- | --- | --- |
| 任意の社内ツール/GitHub/DB | MCP（stdio/HTTP）| 低〜中 | per-serverツールフィルタ・sampling対応 |
| 既存フロントエンド | OpenAI互換APIサーバー | 低 | Open WebUI/LobeChat/LibreChat接続 |
| IDE | ACP | 低 | VS Code/Zed/JetBrains |
| メッセージング | Gateway adapter | 低 | 20+チャネル |
| Home Assistant | ha_* ツール | 中 | 家電/IoT操作 |

### API/統合オプション
- OpenAI互換エンドポイント公開、MCPクライアント/サーバー両対応、Pythonライブラリとして `from run_agent import AIAgent` で組み込み可能。

### 拡張性・カスタマイズ性
- プラグイン3種（general/メモリプロバイダ/context engine）、カスタムツール/フック、SOUL.mdによる人格、quick_commands（LLMを介さない即時シェルコマンド）、Skins。

---

## 8. 実際の使用例・サンプル

### ユースケース1: 毎朝のデイリーブリーフィングBot
**シナリオ**: Gateway常駐＋cronで毎朝、指定トピックをWeb調査し要約をTelegram配信。
**入力**: 自然言語cron「毎朝7時に最新のAIエージェント動向を調べて要約して送って」。
**出力**: 要約メッセージが指定チャネルに自動配信。
**評価**: 当方の「技術ブログ発信」「SNS発信」のネタ収集に転用可能（要PoC）。

### ユースケース2: チーム共有アシスタント
**シナリオ**: 1インスタンスをallowlist/ペアリングで複数メンバーに開放。Slack/Discordから業務指示。
**評価**: admin/user権限分離で安全に共有可能。

### ユースケース3: サンドボックス委譲リサーチ
**シナリオ**: `delegate_task`で複数観点を並列調査、`execute_code`でPython集計を1ターンに圧縮、SSH/Dockerバックエンドで隔離実行。
**評価**: 当方の補助金リサーチ/スクレイピング系タスクの並列化に有望。

### スクリーンショット・デモ
- トップページキャプチャ: /tmp/hermes-home.png（「THE AGENT THAT GROWS WITH YOU」「OPEN SOURCE • MIT LICENSE」、インストール手順、6つの特徴カードを確認）。

---

## 9. 学びとナレッジ

### 発見したこと
- Hermesは「コーディングエージェント」ではなく「**サーバー常駐の汎用業務エージェントOS**」。CLI/Web/Desktop/メッセージングが同一コアを共有する設計が肝。
- 公式が `/llms.txt` と `/llms-full.txt`（全文ダンプ）を公開しており、AIエージェントによる調査が極めて容易（机上調査がほぼ完結）。LLMO/AIO観点でも参考になる実装。
- 自社モデル Hermes 4 を「agent用途には非推奨」と公式が明言しているのは誠実。エージェント基盤とモデルを分離して考える設計思想が明確。

### うまくいったこと
- Browser Use CLI でサイト構造を抽出 → `/docs` の `llms-full.txt` を `curl` で取得する流れが効率的。SPA相手でも公開txtダンプがあれば全機能を網羅できた。

### うまくいかなかったこと
- Nous Portal の具体的な料金は公開トップ/ドキュメントには金額の明示がなく、portal側の要ログイン領域のため未確認（スコープ上スキップ）。

### Tips・ベストプラクティス
- 任意サイト調査では、まず `/llms.txt`・`/llms-full.txt`・`/sitemap.xml`・`/robots.txt` を確認すると、ブラウザ巡回せずに全体像を取得できる場合がある。
- Hermes導入時は `hermes setup --portal` が最短だが、脱ロックイン重視ならOpenRouter or ローカルモデル＋個別ツールキーの構成も可。
- 常駐運用は必ずallowlist/ペアリングを設定し、`--yolo`/`approvals.mode: off`は信頼環境のみ。

### よくあるエラーと対処法（公式FAQより）
- `hermes: command not found` → シェルのPATH再読込（`source ~/.bashrc`）。
- ローカルモデルでタイムアウト → `HERMES_STREAM_READ_TIMEOUT=1800` 等。
- WSL2からWindows Chrome操作 → `/browser connect`より`chrome-devtools-mcp`のMCPブリッジ推奨。

---

## 10. 判定と今後のアクション

### 総合評価
⭐️⭐️⭐️⭐️☆（4.0／5・**机上調査時点**）

### 導入判定
- [ ] 即座に導入推奨
- [x] 条件付きで導入可
- [ ] 追加検証が必要
- [ ] 導入見送り

### 判定理由
- OSS(MIT)・セルフホスト・マルチプロバイダ・常駐＋cron＋マルチチャネルという構成は、当方の「業務自動化OS／発信／補助金リサーチ」の方向性と高い親和性。本体無料でPoCコストが低く、試す価値が大きい。
- 一方、実機での精度・安定性・運用負荷・Nous Portal料金は未実測。常駐運用のセキュリティ/保守責任が自分側に来る点を踏まえ「条件付き導入可」。

### 次のステップ
- [x] 追加PoC実施（検証領域: ローカル/OpenRouter接続での実インストール＆`hermes setup`、cronで定例リサーチBotを1本構築）
- [ ] MVP開発
- [ ] パイロット導入
- [ ] 社内展開ロードマップ作成
- [ ] 検証終了

### 追加で検証したい項目
- Nous Portal の料金プラン・モデル従量と、OpenRouter直/ローカルモデルとのコスト比較。
- `delegate_task`/`execute_code` の並列リサーチ実測（補助金リサーチskillの移植可否）。
- Desktop/Web DashboardのUX実測と、既存 `.claude/skills` 資産（agentskills.io互換）の流用可否。
- MCP連携で当方の既存MCP（Notion/Linear/Gmail等）をHermesから使えるか。

---

## 11. 競合比較（Claude Code / Codex / Cloudflareとの違い）

設計思想で割り切ると整理しやすい。**Hermes＝運用フレームワーク**、**Claude Code / Codex＝コーディングエージェント本体**、**Cloudflare（Agents SDK＋Workers AI）＝サーバレスでエージェントを“作る”土台**。レイヤーが異なる。Cloudflareはエッジ/サーバレス（Durable Objects上で起動）が思想で、「自前PCに常駐」という用途とは土俵が違う点に注意。

### 機能単位の比較
| 軸 | Hermes Agent | Claude Code (Agent SDK) | Codex (OpenAI) | Cloudflare Agents SDK |
| --- | --- | --- | --- | --- |
| 正体 | 常駐型・汎用業務エージェント基盤 | コーディングエージェント＋SDK | コーディングエージェント | エージェントを作るSDK/PaaS |
| LLM | **自由**（OpenAI互換/ローカルOSS可） | Anthropic固定 | OpenAI固定 | Workers AI(OSS)＋外部API |
| 本体ライセンス | **OSS(MIT)・無料** | 商用 | 商用 | SDK無料・実行はCF課金 |
| ランニングコスト | **ローカルLLMなら0円**化可 | API従量（必須） | API従量（必須） | CF実行＋推論課金 |
| 常駐のしやすさ | ◎ `gateway install`でsystemd常駐 | △ 自前で常駐ループ実装 | △ 同左 | ○ ただしサーバレス常駐 |
| スケジューリング(cron) | **標準装備**（自然言語cron） | ✕ 自作 | ✕ 自作 | ○ Cron Triggers |
| メッセージング連携 | **20+チャネル標準** | ✕ 自作 | ✕ 自作 | ✕ 自作 |
| 永続メモリ/スキル | **標準装備** | メモリ/スキルあり | △ | 自前(Durable/KV) |
| SDK/組み込み | Python(`AIAgent`)＋OpenAI互換API公開 | **SDK充実** | SDK/AgentKit | **SDK中心** |
| サンドボックス | local/docker/ssh/modal等5種 | 権限制御あり | クラウド実行は隔離 | V8 isolate(強い分離) |
| コーディング品質/IDE統合 | ○(汎用) | **◎** | **◎** | △ |

### 「定期メール監視・SNS収集」での判断軸
- **Claude Code Agent SDKで書く場合**: 常駐/スケジューラ/メール・SNS接続/通知配信/記憶DBを自分で実装。自由でコンパクトだが、**LLMはAnthropic従量課金が必ず発生**。監視のような「軽いが高頻度」なタスクほどAPIコストが積み上がる。
- **Hermesが効く理由**: ①cron・メール/SNS連携・通知配信・記憶が“設定だけ”で揃い、配管をほぼ書かない ②**ローカルOSS LLMでランニングコストをゼロ化できる**（高頻度タスクで効く）③マルチユーザー共有＋権限分離が標準 ④モデル差し替えでロックインしない。
- **Claude Code / Codexが勝つ場面**: タスクの中身が「コードを書く・直す・PRを出す」で、推論/コーディング品質が成果を左右する用途。量が少なくフロンティアモデル前提でAPI従量が苦にならない。

### 落としどころ（推奨）
> 監視・収集・定例配信などの**運用反復タスク → Hermesに常駐**（ローカル/安価モデルでコスト最小）。
> コードを書く・難しい判断の**実装タスク → Claude Code / Codex**（必要に応じフロンティアモデル）。

両者は排他ではない。HermesはコーディングCLIをPTYツールとして内部起動でき（Claude Code/Codexを呼べる）、MCPにも対応。**「常駐オーケストレーター＝Hermes、頭脳の一部＝Claude Code」のハイブリッド**が現実解。

---

## 12. 運用形態（サーバ常駐・起動モード）

常駐の正体は **「gateway」という単一デーモンプロセス**。これが①メッセージング接続 ②APIエンドポイント ③cronスケジューラ を内包する。「常駐させる＝gatewayを起動する」。以下の3モードは排他ではなく、gateway常駐の上に同時に乗る。

### ① systemd / launchd でデーモン化（常駐の基本形）
```bash
hermes gateway install                 # user常駐サービス化（Linux=systemd / mac=launchd）
sudo hermes gateway install --system   # Linux: ブート時のシステムサービス
hermes gateway start / stop / status
```
gatewayは**60秒ごとにcronスケジューラをtick**し、各チャネルの着信も待ち受ける。

### ② HTTPエンドポイントを立てて呼び出す（API Server / SDK的利用）
OpenAI互換のHTTPサーバを公開できる。別アプリや自作UIからプロンプトをPOST →フルツールで処理して結果を返す。
```bash
# ~/.hermes/.env
API_SERVER_ENABLED=true
API_SERVER_KEY=change-me
```
```bash
hermes gateway   # → [API Server] listening on http://127.0.0.1:8642
curl http://localhost:8642/v1/chat/completions \
  -H "Authorization: Bearer change-me" \
  -d '{"model":"hermes-agent","messages":[{"role":"user","content":"今日の未読メールを要約して"}]}'
```
- 主要エンドポイント: `/v1/chat/completions`・`/v1/responses`（サーバ側で会話状態保持）・`/v1/runs`（実行投入＋SSE進捗購読）・`/api/jobs`（外部からcronジョブCRUD）。
- Pythonから直接埋め込むなら `from run_agent import AIAgent` も可能。

### ③ cronで無人実行＋自動承認
gateway内蔵スケジューラ（OSのcronではない）。自然言語でも組める。
```bash
hermes cron create "every 1d at 09:00" "未読メールを要約してTelegramに送って"
# チャットで「毎朝9時にAIニュースを要約して送って」と言うだけでも可
```
無人で承認なしに進めるには：
```yaml
# ~/.hermes/config.yaml
approvals:
  cron_mode: approve   # cron実行が危険コマンドに当たった時、自動承認（既定は deny）
```
- `cron_mode: approve` でも **`rm -rf /`・fork bomb等のハードラインブロックは無効化不可**（最悪の事故は構造的に防止）。
- 「無人＋自動承認」は任意コマンド実行を許す状態 →**terminalバックエンドをdocker/ssh等で隔離し、本番資産と同居させない**のが鉄則。
- **no-agent（スクリプトのみ）モード**もあり、LLMを使わず定型スクリプトを定期実行し標準出力を配信できる（定型監視に最も安全＆無料）。

### 3モードの使い分け
| 起動形態 | Hermesの機能 | 向くユースケース |
| --- | --- | --- |
| systemdでデーモン化 | `gateway install`（常駐の土台） | 常時稼働の前提 |
| エンドポイント立てて呼ぶ | API Server（OpenAI互換HTTP）＋Pythonライブラリ | 別アプリ/自作UIから呼ぶ、SDK的利用 |
| cronで無人＋自動承認 | 内蔵cron ＋ `cron_mode: approve` | メール監視・SNS収集・定例配信 |

当方の「専用機に常駐させ、メール監視・SNS収集を無人で回す」用途は **①＋③（必要なら②）** の組み合わせがベストフィット。

---

## 📚 関連リソース

### 公式ドキュメント
- 公式サイト: https://hermes-agent.nousresearch.com/
- ドキュメント: https://hermes-agent.nousresearch.com/docs
- LLM向け全文ダンプ: https://hermes-agent.nousresearch.com/docs/llms.txt ／ /llms-full.txt
- Desktopダウンロード: https://hermes-agent.nousresearch.com/desktop
- GitHub: https://github.com/NousResearch/hermes-agent
- Nous Portal: https://portal.nousresearch.com/ （要ログイン・料金未確認）
- Nous Chat: https://chat.nousresearch.com
- Discord: https://discord.gg/NousResearch

### 調査した主なドキュメントページ（サイトマップ）
- Getting Started: installation / quickstart / learning-path / updating / termux / nix-setup
- User Guide: cli / tui / configuration / configuring-models / sessions / profiles / git-worktrees / docker / security / checkpoints-and-rollback / windows-native / desktop
- Features: overview / tools / skills / curator / memory / context-files / personality / plugins / cron / delegation / kanban / goals / code-execution / hooks / batch-processing / voice-mode / browser / vision / image-generation / tts / mcp / acp / api-server / honcho / provider-routing / fallback-providers / credential-pools / web-dashboard / web-search / x-search / computer-use / deliverable-mode / lsp / tool-gateway / subscription-proxy
- Messaging: index ＋ telegram/discord/slack/whatsapp/signal/email/sms/matrix/mattermost/homeassistant/teams/line/feishu/wecom/weixin/dingtalk/qq/yuanbao/bluebubbles/google_chat/ntfy/webhooks/open-webui
- Integrations: index / providers / nous-portal
- Developer Guide: contributing / architecture / agent-loop / prompt-assembly / gateway-internals / adding-tools / adding-providers / creating-skills など
- Reference: cli-commands / slash-commands / environment-variables / tools-reference / toolsets-reference / model-catalog / skills-catalog / faq

### 社内関連ドキュメント
- [[skills-directory-layout]]（.agents/.claude スキル共通化）— Hermesの agentskills.io 互換と関連
- mcp-usage-strategy スキル（MCPとCLIの使い分け）— HermesのMCP連携と直結
- browser-use-googletrends スキル（本調査で使用したBrowser Use CLI）

### 検証データ・ログ
- 取得元一次データ: /tmp/hermes-llms-full.txt（公式全文ダンプ・61,352行）、/tmp/hermes-home.png（トップページキャプチャ）

---

## ✅ メモ・議論ログ
- 調査は2026/06/05、Browser Use CLI（ローカル）＋curlで実施。実インストール・実行は未実施の机上評価。
- ドキュメントのWindows対応（ネイティブ/WSL2）に記述差あり。導入時は実機で要確認。
- Nous Portalの料金は公開ページに金額明示なし → 別途portalで確認するタスクを残す。

---

## 📝 更新ログ
| 日時 | 更新内容の概要 |
|---|---|
| 2026/06/05 | ファイル作成（init） |
| 2026/06/05 | Browser Use CLI＋公式llms-full.txt調査結果を全セクションに反映（update） |
| 2026/06/05 | ステータスを「完了」に変更、総合評価・導入判定を確定（finalize） |
| 2026/06/05 | 「11. 競合比較（Claude Code/Codex/Cloudflare）」「12. 運用形態（起動・常駐モード）」を追記 |
