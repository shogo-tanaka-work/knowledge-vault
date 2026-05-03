# browser-use CLI 2.0 検証ログ

> ステータス: 完了
> 作成日: 2026/04/05
> 最終更新: 2026/05/03
> ファイルパス: /Users/shogo/ObsidianVault/knowledge-vault/structured/tools/FY2025_browse-use-cli-2.md

---

## 📋 検証概要

- **ツール/サービス名**: browser-use CLI 2.0
- **検証対象**: 新ツール（ブラウザ自動化CLI）
- **バージョン/リリース日**: v0.12.6 / 2026年初頭リリース
- **検証期間**: 2026/04/05
- **検証担当者**: shogo-tanaka-work
- **検証ステータス**: 検証完了

---

## 1. 背景と検証目的

### なぜこの検証を行うのか
- browser-use CLI 2.0がリリースされ、Playwright/Seleniumに代わる新しいブラウザ自動化手段として注目
- CLIベースでシンプルに使える点、LLM統合が標準搭載されている点が従来ツールとの差別化ポイント
- 実際の業務タスク（ニュース収集、情報抽出）で使えるか検証する必要がある

### 解決したい課題
- 公式サイトのニュース・ブログ記事を定期的に収集したい
- Cloudflare等のボット対策がされているサイトにもアクセスしたい
- スクリプト化して自動実行可能な仕組みが欲しい
- 将来的にはリモートから利用可能なMCPサーバーとして公開したい

### 期待される効果・ビジネスインパクト
- 手動でのニュース確認作業を自動化（週5-10時間の削減）
- 競合他社の最新情報を漏れなくキャッチアップ
- 複数サイトからの情報集約を自動化

---

## 2. ツール/機能の基本情報

### 概要
- Pythonベースのブラウザ自動化CLI
- Playwrightをバックエンドに使用
- Claude等のLLMと統合し、自然言語でのタスク指示が可能
- CLIモードとPython Agent APIの2つの使い方がある

### 提供元
- GitHub: https://github.com/browser-use/browser-use
- オープンソース（MIT License）
- コミュニティ主導のプロジェクト

### 主要機能
- `browser-use open [URL]` - ブラウザを起動してURLを開く
- `browser-use state` - 現在ページの状態（クリック可能要素等）を取得
- `browser-use screenshot [PATH]` - スクリーンショット保存
- `browser-use get html` - ページのHTML取得
- `browser-use get title` - ページタイトル取得
- `browser-use click [INDEX]` - 要素クリック
- `browser-use type [TEXT]` - テキスト入力
- `browser-use close` - セッション終了
- セッション管理（`-session [NAME]`）
- headedモード（`-headed`）でブラウザ表示

### 技術スタック・アーキテクチャ
- 言語: Python 3.11以上
- ブラウザエンジン: Playwright（Chromium）
- LLM統合: LangChain経由でClaude/OpenAI対応
- MCP対応: `-mcp`フラグで起動可能

---

## 3. 検証方法

### 検証環境
- **使用アカウント**: 個人アカウント
- **プラン/エディション**: OSS版（無料）
- **検証環境**: ローカル開発環境（macOS Darwin 25.2.0、Python 3.11.x、browser-use 0.12.6）

### 検証シナリオ
1. 基本CLI操作の検証（open/state/screenshot等の基本コマンドの動作確認）
2. ニュース抽出の実装（AnthropicとClaude公式サイトからニュース記事を取得）
3. 日付フィルタリング（過去N日間のニュース記事のみ抽出）
4. Cloudflare保護サイト対応（ボット検証があるサイト（Canva）へのアクセス）
5. セッション管理の検証（ブラウザプロセスの適切なクリーンアップ）
6. リモートMCP化の調査（外部から利用可能なMCPサーバーとしての展開可能性）

### 検証データ・サンプル
- 対象サイト1: https://www.anthropic.com/news
- 対象サイト2: https://claude.com/ja-jp/blog
- 対象サイト3: https://www.canva.com/newsroom/（Cloudflare保護）

### 前提条件・制約事項
- Python 3.11以上が必須（3.10以下では動作しない）
- ANTHROPIC_API_KEY環境変数の設定が必要（Agent API使用時）
- headlessモードではCloudflareにブロックされる可能性あり

---

## 4. 検証結果

### 定性的評価

#### 機能面の評価
- 基本的なブラウザ操作は問題なく動作
- HTML取得とBeautifulSoupでの解析が安全に実行可能
- セッション管理により複数の並行実行が可能
- headedモードでCloudflare保護サイトにもアクセス可能
- 長時間タスクは30-120秒かかる（リアルタイム処理には不向き）

#### 操作性・UI/UX
- CLIコマンドがシンプルで直感的
- エラーメッセージがわかりやすい
- セッションのクリーンアップを手動で行う必要がある
- ブラウザプロセスがDockに残る問題（try-finallyで対処可能）

#### 出力品質
- スクリーンショットは高品質で保存される
- HTML取得は完全なDOMを取得可能
- BeautifulSoupでのパースに最適な形式

#### 実用性
- ニュース抽出タスクは実用レベル
- 日付フィルタリングも正確に動作
- 重複除去により精度が向上
- Cloudflare対策として30秒待機が必要（自動化に影響）

---

### 定量的評価

#### 導入コスト

| 項目 | 内容 | 金額/工数 |
| --- | --- | --- |
| 初期設定時間 | CLI インストール〜初回実行まで | 15分 |
| 学習時間 | 基本操作習得〜サンプル実装まで | 2-3時間 |
| 初期費用 | なし（OSS） | 0円 |

#### 運用コスト

| 項目 | 内容 | 金額 |
| --- | --- | --- |
| 月額利用料 | なし（OSS） | 0円 |
| 年額利用料 | なし | 0円 |
| 従量課金 | Anthropic API使用料（Agent API使用時のみ） | 使用量次第 |
| 追加オプション | MCP Cloud（オプション） | 未検証 |

#### パフォーマンス

| 項目 | 測定結果 | 備考 |
| --- | --- | --- |
| ページ読み込み速度 | 3-5秒 | 通常のWebサイト |
| HTML取得時間 | 2-3秒 | `get html`コマンド |
| スクリーンショット取得 | 1-2秒 | 1920x1080解像度 |
| ニュース抽出（全体） | 30-60秒 | HTML取得+パース+フィルタリング |
| Cloudflare対応 | 60-90秒 | 30秒待機含む |

#### ROI試算
- **削減できる工数**: 週5時間（手動ニュース確認作業）
- **生産性向上**: 複数サイト同時監視が可能に
- **コスト削減額**: 月20時間 × 時給換算
- **投資回収期間**: 即時（無料ツールのため）

---

## 5. 比較・優位性分析

### 既存ツール/類似サービスとの比較

| 項目 | browser-use CLI | Playwright | Selenium |
| --- | --- | --- | --- |
| 機能性 | CLI+Python API | Python API | 複数言語対応 |
| コスト | 無料（OSS） | 無料（OSS） | 無料（OSS） |
| 使いやすさ | ⭐️⭐️⭐️⭐️⭐️ | ⭐️⭐️⭐️⭐️ | ⭐️⭐️⭐️ |
| LLM統合 | ネイティブ対応 | なし | なし |
| MCP対応 | あり | なし | なし |
| セッション管理 | CLI標準機能 | 手動実装必要 | 手動実装必要 |

### 優位性
- CLIで簡単に使えるため、シェルスクリプトから呼び出しやすい
- LLM統合が標準搭載されており、自然言語でのタスク指示が可能
- MCP対応によりリモート実行環境の構築が容易
- セッション管理が組み込まれている

### 劣位性・懸念点
- Python 3.11以上必須（環境制約が厳しい）
- 比較的新しいツールのため、情報が少ない
- Cloudflare対策は手動待機が必要（自動化に課題）
- セッションクリーンアップを忘れるとプロセスが残る

---

## 6. リスク評価

### セキュリティ

| 評価項目 | 評価 | 詳細 |
| --- | --- | --- |
| データ保管場所 | ローカル | スクリーンショット、ログはローカル保存 |
| 暗号化 | N/A | HTTPS通信は標準対応 |
| アクセス制御 | ローカル実行 | 認証機能なし（MCP化時は要実装） |
| ログ管理 | ファイル出力 | 標準出力/標準エラー |
| コンプライアンス | 利用者責任 | robots.txt準拠は利用者が確認必要 |

### プライバシー・倫理面
- スクレイピング対象サイトのrobots.txt確認が必要
- 利用規約違反にならないよう注意
- 個人情報を含むページの自動取得は慎重に

### ベンダーロックインリスク
- OSSのため、ベンダーロックインなし
- PlaywrightベースのためMigration可能

### 技術的リスク
- Cloudflare等のボット対策が強化されると突破困難に
- サイト構造変更で抽出ロジックが壊れる可能性
- Python 3.11依存により、古い環境では使用不可

---

## 7. 連携性・拡張性

### 既存システムとの連携

| 連携先 | 方法 | 難易度 | 備考 |
| --- | --- | --- | --- |
| シェルスクリプト | CLIコマンド呼び出し | ⭐️ 簡単 | 標準的なサブプロセス実行 |
| Python | subprocess/Agent API | ⭐️ 簡単 | Agent APIで高度な制御可能 |
| Claude Code | MCP統合 | ⭐️⭐️ 中程度 | mcp-browser-use使用 |
| CI/CD | Docker化 | ⭐️⭐️⭐️ やや難 | Chromium依存関係に注意 |

### API/統合オプション
- Python Agent API: LangChain経由でLLM統合
- MCP Server: `-mcp`フラグでMCPサーバーとして起動
- HTTP Wrapper: mcp-browser-useでHTTP経由アクセス可能

### 拡張性・カスタマイズ性
- Pythonコードで自由にラップ可能
- BeautifulSoupと組み合わせて柔軟なパース処理
- リモートMCPサーバー化でClaude Codeから利用可能

---

## 8. 実際の使用例・サンプル

### ユースケース1: Anthropicニュース抽出

**シナリオ**: Anthropic公式サイトから過去7日間のニュース記事を取得
**入力**: extractor = RecentNewsExtractor(days=7); extractor.extract_news_from_anthropic("https://www.anthropic.com/news")
**出力**: JSON形式の記事一覧（timestamp, url, days, count, articles）
**評価**: 日付フィルタリング、重複除去が正確に動作

### ユースケース2: Cloudflare保護サイト（Canva）

**シナリオ**: Cloudflare保護がかかっているCanvaニュースサイトからニュース取得
**入力**: extractor = CanvaNewsExtractor(); extractor.extract_canva_news()
**出力**: 10-15件のニュース記事（日付情報なし）
**評価**: headedモードで回避成功、ただし30秒待機が必要

### ユースケース3: Claude日本語ブログ抽出

**シナリオ**: https://claude.com/ja-jp/blog から最新記事を取得
**入力**: h2要素（u-text-style-h6クラス）からタイトル取得、次の兄弟要素（captionクラス）から日付取得、grandparent要素内のリンクを検索
**出力**: タイトル + 日付 + URLの記事一覧
**評価**: サイト固有のHTML構造に対応、正確な日付抽出

### スクリーンショット・デモ
- screenshots/anthropic_news.png - Anthropicニュースページ
- screenshots/claude_blog.png - Claudeブログページ
- screenshots/canva_headed.png - Canva（headed mode）

---

## 9. 学びとナレッジ

### 発見したこと
- Python 3.11必須の制約：最初Python 3.10環境で実行したところ、依存関係エラーが発生。requirements.txtで`browser-use>=0.12.0`と指定することで明示化、`/usr/local/bin/python3.11`を直接使用することで解決。
- セッション管理の重要性：`-session`オプションでセッション名を指定できる。複数の並行実行が可能。ただし、`close`コマンドを忘れるとブラウザプロセスがDockに残り続ける。

### うまくいったこと
- XSSリスク回避のための設計変更：`browser-use eval`によるJavaScript実行から、`get html` + BeautifulSoupによる安全なパースに変更
- 日付抽出の精度向上：完全な月名パターン（January〜December）と省略形（Jan〜Dec）の両方に対応、grandparent要素のリンクも検索するようHTML構造の階層を上に辿る
- 重複記事の除去：URL based deduplicationで重複削除
- Cloudflare保護の突破：headedモード + 30秒待機で対応
- セッションクリーンアップの徹底：try-finallyパターンでリソースの確実な解放を保証

### うまくいかなかったこと
- Cloudflare自動突破の完全自動化：headlessモードでは100%ブロックされる。headedモード + 30秒待機でも、時々失敗することがある。完全自動化には限界があり、人間の介入前提の設計が必要。
- リアルタイム処理：1ページの取得に30-60秒かかる。大量サイトの並列処理には不向き。バッチ処理前提の設計が必要。

### Tips・ベストプラクティス
- セッション名の命名規則：`f"{purpose}_{timestamp}"` 例: `"news_extraction_20260405"`
- タイムアウト設定：HTML取得は長めに設定（180秒等）
- デバッグ時のheadedモード活用：DEBUGフラグで切り替え
- robots.txt確認の自動化：urljoin(url, "/robots.txt")でチェック

### よくあるエラーと対処法
- エラー1: Python version not supported → Python 3.11以上にアップグレード
- エラー2: Session already exists → `browser-use --session XXX close`を実行
- エラー3: Timeout expired → `timeout`パラメータを120-180秒に増やす
- エラー4: Command not found: browser-use → `~/.zshrc`に`export PATH="$HOME/.local/bin:$PATH"`を追加

---

## 10. 判定と今後のアクション

### 総合評価
⭐️⭐️⭐️⭐️☆ (4/5)

### 導入判定
- [x] 即座に導入推奨
- [ ] 条件付きで導入可
- [ ] 追加検証が必要
- [ ] 導入見送り

### 判定理由
- ニュース抽出タスクは実用レベルで動作
- Cloudflare対策も可能（headed mode使用）
- セッション管理とクリーンアップの仕組みが確立
- リモートMCP化により、Claude Codeから共有利用可能
- Python 3.11必須という制約はあるが、それを上回る利便性

### 次のステップ
- [x] 基本検証完了
- [ ] リモートMCPサーバー化（Phase 1-6実施）
- [ ] カスタムMCPツール追加
- [ ] Fly.ioへのデプロイ
- [ ] 本番運用開始

### 追加で検証したい項目
- ログイン認証が必要なサイトへのアクセス
- フォーム入力・送信の自動化
- 大量サイトの並列処理パフォーマンス
- エラーリトライロジックの実装

---

## 📚 関連リソース

### 公式ドキュメント
- GitHub: https://github.com/browser-use/browser-use
- CLI Documentation: https://browser-use.com/docs/cli
- Python API: https://browser-use.com/docs/api

### 参考記事・事例
- mcp-browser-use: https://github.com/Saik0s/mcp-browser-use
- Playwright公式: https://playwright.dev/

### 社内関連ドキュメント
- 実装計画: `/Users/shogo/.claude/plans/iridescent-shimmying-ullman.md`
- サンプルコード: `/Volumes/PortableSSD/Documents/AIツールPoCの場所/ClaudeCode/browser_use_poc/samples/`

### 検証データ・ログ
- スクリーンショット: `../screenshots/*.png`
- 抽出結果JSON: `../logs/*.json`

---

## ✅ メモ・議論ログ
- 2026/04/05 14:00 - XSSリスク指摘を受けてevalコマンド使用を中止、BeautifulSoupに変更
- 2026/04/05 14:30 - April 2の記事が取れない問題を発見、日付パターンとHTML構造を修正
- 2026/04/05 15:00 - 重複記事問題を発見、URL based deduplicationを実装
- 2026/04/05 15:30 - Cloudflare対策として--headedモード + 30秒待機を確立
- 2026/04/05 16:00 - セッション残存問題を指摘され、try-finallyパターンを全サンプルに適用
- 2026/04/05 16:30 - リモートMCP化の調査開始、Fly.io採用を決定

---

## 📝 更新ログ
| 日時 | 更新内容の概要 |
|---|---|
| 2026/04/05 | ファイル作成（init） |
| 2026/04/05 | 検証完了、全セクション記入 |
| 2026/05/03 | 旧フォーマット（byTech_ツールPoC）から ai-verification-log フォーマットへ移行 |
