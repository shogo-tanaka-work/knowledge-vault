# 失敗ログ蓄積パターン — AI エージェント運用における経験則ライブラリ設計

AI エージェント設定ファイルには 2 つの設計思想がある。1 つは **静的なベストプラクティス集**（コーディング規約・ビルドコマンド・テスト戦略）として固定的に記述するもの。もう 1 つは **動的に蓄積される経験則ライブラリ**として、現場の失敗・回避策・tribal knowledge を運用しながら追記していくもの。

後者を採用している代表例が Appsmith・cline・OpenAI Cookbook の 3 つ。本記事ではこれらの失敗ログ蓄積パターンを比較し、長期運用を前提とした AI 設定ファイルの設計思想を抽出する。

## 1. Appsmith — `.cursor/lessons.md` のセルフイプルーブメントループ

### 1.1 仕組み

引用元: [.cursor/rules/agent-behavior.mdc](https://raw.githubusercontent.com/appsmithorg/appsmith/release/.cursor/rules/agent-behavior.mdc)

Appsmith の Cursor 設定では、エージェントの行動規範として以下のループが定義されている:

> "After user corrections, document patterns in `.cursor/lessons.md`. Incrementally refine rules to prevent recurring mistakes."

つまり「ユーザーから訂正を受けたら、そのパターンを `.cursor/lessons.md` に記録し、ルールを継続的に改善する」というセルフイプルーブメント（自己改善）ループを公式ワークフローとして組み込んでいる。

### 1.2 蓄積されている内容（実例）

引用元: [.cursor/lessons.md](https://raw.githubusercontent.com/appsmithorg/appsmith/release/.cursor/lessons.md)

2026 Q1-Q2 の実障害が時系列で記録されている。代表例:

- **Spring Boot アップグレードでの `@Override` サイレント失敗**: バージョン違いによりインターフェース変更が無告知で発生し、`@Override` が消えてもコンパイルが通る現象
- **`FormGroup` のアクセシビリティ問題**: 特定のスクリーンリーダーで挙動が崩れるパターン
- **並列テストの共有 setup パターン**: 複数テスト間でのリソース競合の落とし穴

これらは公式ドキュメントには載らないが、**実際にエージェントが踏んだ地雷の記録**として後続のエージェントセッションに渡される。

### 1.3 観点抽出

- **「ユーザー訂正をエージェントが恒久知識に変換する」プロセスを公式化**している点が独特。通常はメンテナが手動で書く tribal knowledge を、AI エージェント自身が記録する経路を作っている。
- ファイル名が `lessons.md`（教訓集）であり、ベストプラクティス集ではないことが意図的。完璧な指針ではなく **失敗から学んだ事項** に限定することで、エントロピーの増加を防いでいる。
- 別ファイル `agent-behavior.mdc` に「複雑な問題にはサブエージェントを活用して研究・探索・並列分析を委譲」という **エージェント分担戦略** も明示されている。

## 2. cline — `.clinerules/general.md` の「いつ書くか」ポリシー

### 2.1 仕組み

引用元: [.clinerules/general.md](https://raw.githubusercontent.com/cline/cline/main/.clinerules/general.md)

cline の設定は `CLAUDE.md` を入口にして `.clinerules/` 配下のドメイン別ファイル（`general.md`、`network.md`、`cli.md` 等）を参照する分散構造。

特に `general.md` は **「このファイルをいつ更新するか」の基準** を明示している点でユニーク:

- 手動介入が必要だった時
- 複数試行が必要だった時
- gotcha（落とし穴）に当たった時
- 経験則として「次回も役立つ」と感じた時

これは「ドキュメントを書くタイミング」をエージェント自身に判断させるためのメタルール。

### 2.2 蓄積されている内容（実例）

- **gRPC/Protobuf の 3 箇所更新ゴッチャ**: 1 つの定義変更には 3 ファイルの同期更新が必要。さもないと Anthropic API 側で **サイレントリセット** が発生する
- **StateManager Cache Timing の例外ケース**: 通常のキャッシュフローから外れる条件
- gRPC の変換マッピングのような「動かしてみないとわからない」性質の知識

### 2.3 観点抽出

- **「いつ書くか」の基準をルール化** することで、ドキュメントの肥大化を抑制しつつ価値の高い知識だけが残る設計。
- 静的なベストプラクティスではなく **「動かしたら詰まった事項」だけを記録**することで、ファイルが「最新の地雷マップ」として機能する。
- ドメイン分割（network / cli / general）により、エージェントが関連ファイルだけを読み込めばよく、コンテキスト効率が高い。

## 3. OpenAI Cookbook — Operational Insights セクション

引用元: [openai/openai-cookbook AGENTS.md](https://raw.githubusercontent.com/openai/openai-cookbook/main/AGENTS.md)

### 3.1 仕組み

ノートブック中心のリポジトリらしく、AGENTS.md の中に **「Operational Insights」セクション**として運用上の知見を蓄積している。具体的には:

- `registry.yaml` と `authors.yaml` の整合性維持義務
- ノートブック実行時の認証・環境分離パターン
- 過去に発生した運用上の落とし穴

### 3.2 観点抽出

- セクション名が「Best Practices」ではなく **「Operational Insights」（運用上の洞察）** になっている。これは「あるべき姿」ではなく「実際に起きたこと」を記録する意図の表れ。
- 軽量な実装で、独立ファイルを切らずに AGENTS.md 内のセクションとして同居させる方式。リポジトリ規模に応じた選択肢として有効。

## 4. 設計思想の比較 — 静的ベストプラクティス vs 動的経験則ライブラリ

| 観点 | 静的ベストプラクティス | 動的経験則ライブラリ |
|---|---|---|
| 記述タイミング | 設計時に一括記述 | 失敗・訂正のたびに追記 |
| 主たる目的 | 「あるべき姿」の規範化 | 「実際に起きたこと」の記録 |
| 肥大化リスク | 高（網羅的に書きがち） | 低（更新基準で制御） |
| 陳腐化リスク | 高（コードと乖離） | 低（実体験に紐づく） |
| 例 | 多くの汎用 AGENTS.md | Appsmith lessons / cline rules / OpenAI Cookbook insights |

### 観点抽出

- **動的経験則ライブラリの最大の利点** は、ドキュメントが実際に発生した事象に裏打ちされていること。エージェントが「過去に同じ罠に落ちた事例」を参照できるため、再発防止精度が高い。
- 一方で、書き手側に「いつ書くか」の判断基準が要求されるため、cline のような明示的なメタルールが重要になる。
- 両方を併存させる構成（静的ガイド + lessons.md）が現実的。Appsmith は `.cursor/rules/` で静的指針、`.cursor/lessons.md` で動的蓄積、と完全に分離している。

## 5. 共通する設計パターン

3 例から抽出できる共通設計パターン:

### パターン A: ベストプラクティスと経験則を別ファイルに分離する

混在させると更新責任が曖昧になる。Appsmith のように `rules/` と `lessons.md` を完全に分けるのが明快。

### パターン B: 「いつ書くか」を明文化する

cline の `general.md` のように、追記の判断基準そのものをドキュメント化する。これにより肥大化と陳腐化を同時に抑制できる。

### パターン C: 失敗の主体を「エージェント」と認識する

従来の RUNBOOK は人間オペレーター向けだったが、AI 設定ファイルでは **エージェントが踏んだ地雷** を記録する。このシフトにより、エージェント特有のミス（例: AI 訓練データに無い API 変更へのサイレント失敗）が記録対象になる。

### パターン D: メタルール — エージェント自身に記録を委ねる

Appsmith の「ユーザー訂正後に lessons を更新する」のように、エージェントの行動ループに記録を組み込む。これによりメンテナの手動更新負荷を下げる。

## 6. 採用判断のフレーム

動的経験則ライブラリを導入すべきか否かは、以下の条件で判断できる:

| 条件 | 動的ライブラリの有効性 |
|---|---|
| エージェントセッションが繰り返し走る | 高 |
| コードベースが古く、tribal knowledge が多い | 高 |
| 公式ドキュメントが追いつかないペースで開発される | 高 |
| エージェントセッションが 1 回限り | 低 |
| 規範的ガイドだけで十分な小規模プロジェクト | 低 |

## 引用元一覧

- [Appsmith .cursor/rules/agent-behavior.mdc](https://raw.githubusercontent.com/appsmithorg/appsmith/release/.cursor/rules/agent-behavior.mdc)
- [Appsmith .cursor/lessons.md](https://raw.githubusercontent.com/appsmithorg/appsmith/release/.cursor/lessons.md)
- [Appsmith .cursor/rules/playwright.mdc](https://raw.githubusercontent.com/appsmithorg/appsmith/release/.cursor/rules/playwright.mdc)
- [cline CLAUDE.md](https://raw.githubusercontent.com/cline/cline/main/CLAUDE.md)
- [cline .clinerules/general.md](https://raw.githubusercontent.com/cline/cline/main/.clinerules/general.md)
- [OpenAI Cookbook AGENTS.md](https://raw.githubusercontent.com/openai/openai-cookbook/main/AGENTS.md)
