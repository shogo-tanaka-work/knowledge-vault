# Browser Use CLI 検証ログ

> ステータス: 検証中
> 作成日: 2026/04/20
> 最終更新: 2026/04/20
> ファイルパス: /Users/shogo/ObsidianVault/knowledge-vault/structured/tools/20260420_browser-use-cli.md

---

## 📋 検証概要

- **ツール/サービス名**: Browser Use CLI
- **検証対象**: 新ツール（ブラウザ自動化 CLI）
- **バージョン/リリース日**: 2025年リリース（YCバック・シード$17M調達済み）
- **検証期間**: 2026/04/20 -（検証中）
- **検証担当者**: shogo-tanaka-work
- **検証ステータス**: 検証中

---

## 1. 背景と検証目的

### なぜこの検証を行うのか
- これまで Google Trends の急上昇キーワード調査を **Anthropic Computer Use** で実施していた
- Computer Use はデスクトップ全体を画面キャプチャで操作するため、速度・コスト・精度の面で課題があった
- Browser Use CLI が Web 特化・DOM 解析ベースでより高精度かつ低コストで同等の自動化を実現できるか検証したい

### 解決したい課題
- Google Trends（急上昇キーワード・日本）を定期取得する作業を自動化したい
- Computer Use では毎回認証が必要・遅い・コストが高いという問題がある
- Claude Code（MCP 経由）から自然言語でブラウザを操作できる環境を構築したい

### 期待される効果・ビジネスインパクト
- Google Trends 調査の自動化による工数削減
- Claude Code + MCP 経由でブラウザ操作を自然言語指示に統合
- Computer Use を Browser Use CLI に置き換えることでコスト削減・精度向上

---

## 2. ツール/機能の基本情報

### 概要
- Playwright + DOM解析ベースの **AIエージェント向けブラウザ自動化フレームワーク**
- CLI として提供されており、ターミナルから直接ブラウザを操作・制御できる
- GitHub スター数 75,000+（2026年4月時点）
- Y Combinator バック企業が開発・運営

### 提供元
- 企業名: Browser Use Inc.
- GitHub: https://github.com/browser-use/browser-use
- 公式サイト: https://browser-use.com/
- 公式 CLI ドキュメント: https://docs.browser-use.com/open-source/browser-use-cli

### 主要機能
- **持続セッション（Daemon アーキテクチャ）**: ブラウザプロセスをコマンド間で維持。コマンドレイテンシ約50ms
- **3種類のブラウザモード**:
  - ヘッドレス Chromium（デフォルト）
  - 実際の Chrome（既存ログイン済みプロファイルをそのまま使用）
  - クラウドブラウザ（リモート）
- **操作コマンド一式**: `click`, `type`, `input`, `scroll`, `hover`, `upload`, `select`, `eval`（JavaScript）, `get html/text`
- **マルチセッション**: `--session <name>` で複数の独立したブラウザセッションを並行管理
- **Cookie 管理**: import/export で認証状態を保持・移植可能
- **MCP サーバー**: Claude Code や任意の LLM から MCP ツールとして呼び出し可能
- **スクリーンショット取得**: `browser-use screenshot`

### 技術スタック・アーキテクチャ
- Python 3.11+ 必須
- Playwright（ヘッドレスブラウザ制御）
- DOM 解析によるクリック可能要素の自動認識
- litellm を依存から除去済み（2025年サプライチェーン攻撃対応後）

---

## 3. 検証方法

### 検証環境
- **使用アカウント**: shogo-tanaka-work
- **プラン/エディション**: オープンソース（セルフホスト）＋ Claude Code MCP 連携
- **検証環境**: ローカル macOS

### 検証シナリオ
1. Browser Use CLI のインストール（`curl` ワンライナー）
2. Claude Code の MCP サーバーとして登録
3. Google Trends（急上昇キーワード・日本）を開いて上位20件を取得
4. Computer Use での同等作業と結果・速度・コストを比較

### 検証データ・サンプル
- 対象 URL: `https://trends.google.com/trending?geo=JP`
- 取得対象: 急上昇キーワード上位20件（日本・当日）

### 前提条件・制約事項
- Python 3.11 以上が必要
- Google Trends はログイン不要だが JS レンダリングが必須（ヘッドレスブラウザが必要な理由）
- 短時間での連続リクエストはレート制限・ブロックの可能性あり

---

## 4. 検証結果

### 定性的評価

#### 機能面の評価
- （随時更新）

#### 操作性・UI/UX
- （随時更新）

#### 出力品質
- （随時更新）

#### 実用性
- （随時更新）

---

### 定量的評価

#### 導入コスト

| 項目 | 内容 | 金額/工数 |
| --- | --- | --- |
| 初期設定時間 | curl インストール〜MCP 登録まで | 推定 15〜30分 |
| 学習時間 | 基本操作を習得するまで | 推定 1〜2時間 |
| 初期費用 | オープンソース（無料） | $0 |

#### 運用コスト

| 項目 | 内容 | 金額 |
| --- | --- | --- |
| 月額利用料 | セルフホスト版 | $0 |
| 年額利用料 | セルフホスト版 | $0 |
| 従量課金 | クラウド版のみ $0.05/step | セルフホストなら無料 |
| 追加オプション | クラウドブラウザ（オプション） | 別途 |

#### パフォーマンス

| 項目 | 測定結果 | 備考 |
| --- | --- | --- |
| コマンドレイテンシ | 約50ms | Daemon アーキテクチャにより高速 |
| WebVoyager ベンチマーク | **89%** | Computer Use（56%）を大幅に上回る |
| Computer Use 比較精度 | +33pt | DOM解析 vs 画面キャプチャの差 |
| 同時処理数 | 複数セッション対応 | `--session` オプションで並列化 |

#### ROI試算
- **削減できる工数**: Google Trends 手動調査の全自動化（毎回数分 → ほぼゼロ）
- **生産性向上**: Claude Code から自然言語1文で実行可能
- **コスト削減額**: Computer Use（トークン従量課金 $3〜$15/Mトークン）→ セルフホストなら実質無料
- **投資回収期間**: インストール30分、即日回収可能

---

## 5. 比較・優位性分析

### 既存ツール/類似サービスとの比較

| 項目 | Browser Use CLI | Computer Use（Anthropic） | pytrends |
| --- | --- | --- | --- |
| 制御範囲 | ブラウザのみ | デスクトップ全体 | Python API（ブラウザ不要） |
| 仕組み | DOM解析（Playwright） | 画面キャプチャ（Vision LLM） | 非公式内部 API |
| モデル依存 | 任意の LLM を選択可 | Claude 3.5 Sonnet 専用 | モデル不要 |
| 精度（WebVoyager） | **89%** | 56% | N/A |
| コスト | 無料（セルフホスト） | トークン従量課金 | 無料 |
| JS レンダリング対応 | ◎ 完全対応 | ◎ 完全対応 | × 非対応 |
| 既存 Chrome プロファイル | ◎ そのまま使用可 | △ 毎回入力 | × |
| Claude Code 連携 | ◎ MCP 登録で自然言語化 | ◯ Claude 専用 | △ Python 呼び出し |
| 安定性リスク | ◯ 公式OSS | ◯ Anthropic 公式 | △ 非公式・突然壊れる可能性 |

### 優位性
- DOM 解析ベースのため JavaScript レンダリング後の要素も確実に取得できる
- WebVoyager ベンチマーク 89% はカテゴリ最高水準
- 既存 Chrome プロファイルをそのまま使えるため、ログイン済みサービスへのアクセスが簡単
- MCP 経由で Claude Code から自然言語1文でブラウザ操作が完結する
- セルフホストなら完全無料、Computer Use と比べてコストが大幅に低い
- Daemon アーキテクチャにより連続操作が高速（毎回起動コスト不要）

### 劣位性・懸念点
- ブラウザ以外のデスクトップアプリは操作不可（Computer Use の方が汎用性は高い）
- Python 3.11+ の環境構築が必要
- litellm 依存がサプライチェーン攻撃を受けた経緯あり（現在は除去済みだが注意）
- Google Trends の急上昇キーワードページはレート制限・アンチボット検出がある

---

## 6. リスク評価

### セキュリティ

| 評価項目 | 評価 | 詳細 |
| --- | --- | --- |
| データ保管場所 | ローカル | セルフホスト版はデータがローカルに留まる |
| 暗号化 | ローカル依存 | Cookie export/import は要注意 |
| アクセス制御 | ローカル | セッション管理は端末上 |
| ログ管理 | 手動 | ログの永続化は別途設定が必要 |
| コンプライアンス | 問題なし | ローカル実行のため情報漏洩リスク低 |

### プライバシー・倫理面
- Google Trends の利用規約の範囲内での使用が前提
- 個人の Chrome プロファイルを使用する場合、ログイン情報を含む操作に注意

### ベンダーロックインリスク
- オープンソースのため低い
- ただし Browser Use 社がクラウド版を強化した場合、セルフホスト版のサポートが薄れる可能性
- litellm 依存除去など OSS 管理の方針変更には引き続き注意が必要

### 技術的リスク
- **サプライチェーンリスク**: 2025年に litellm 経由のサプライチェーン攻撃が発生（現在は対応済み）
- **Google のアンチボット**: Trending Now ページは自動化検出を持つ。実際の Chrome プロファイル使用で回避しやすい
- **JS レンダリング待ち**: `state` コマンドでレンダリング完了を確認してから `get text` する必要がある（タイミング次第で空になる）
- **レート制限**: 1リクエストあたり数秒のウェイトを設けることを推奨

---

## 7. 連携性・拡張性

### 既存システムとの連携

| 連携先 | 方法 | 難易度 | 備考 |
| --- | --- | --- | --- |
| Claude Code | MCP サーバー登録 | ★☆☆（簡単） | `claude mcp add` 1コマンドで登録 |
| Claude API | Python SDK + browser-use ライブラリ | ★★☆（中） | コードベースの統合 |
| 任意の LLM | litellm 経由（要注意） | ★★☆（中） | セキュリティリスクを考慮して慎重に |

### API/統合オプション
- **MCP サーバー登録（推奨）**: `claude mcp add browser-use -- uvx --from 'browser-use[cli]' browser-use --mcp`
- **Claude Code Skill**: `npx skills add https://github.com/browser-use/browser-use --skill browser-use`
- **Python ライブラリ**: `pip install browser-use` でプログラムから呼び出し可能

### 拡張性・カスタマイズ性
- マルチセッションで複数サイトの並列操作が可能
- JavaScript 実行（`browser-use eval`）で任意のスクレーピングロジックを注入できる
- Cookie の import/export により認証状態の永続化・移植が可能

---

## 8. 実際の使用例・サンプル

### ユースケース1: Google Trends 急上昇キーワード取得

**シナリオ**: 日本の急上昇キーワード上位20件を取得する

**インストール**:
```bash
curl -fsSL https://browser-use.com/cli/install.sh | bash
browser-use doctor
```

**Claude Code MCP 登録**:
```bash
claude mcp add browser-use -- uvx --from 'browser-use[cli]' browser-use --mcp
```

**CLI による直接操作**:
```bash
# 1. Google Trends を開く
browser-use open "https://trends.google.com/trending?geo=JP"

# 2. JS レンダリング完了を確認
browser-use state

# 3. テキスト一括取得
browser-use get text

# または JavaScript で直接抽出（より確実）
browser-use eval "
  Array.from(document.querySelectorAll('[data-entity-id]'))
    .map(el => el.innerText.trim())
    .slice(0, 20)
    .join('\n')
"
```

**MCP 登録後（Claude Code から自然言語指示）**:
```
Google Trendsの急上昇ワード上位20件（日本・今日）を取得して一覧化して
```

**評価**: （実施後に更新）

### ユースケース2: 実際の Chrome プロファイルを使ったアンチボット回避

**シナリオ**: ログイン済みのサービスや、アンチボット検出が強いページへのアクセス

**操作例**:
```bash
# 実際の Chrome プロファイルを指定して起動
browser-use --profile /Users/shogo/Library/Application\ Support/Google/Chrome/Default open "https://trends.google.com/trending?geo=JP"
```

**評価**: （実施後に更新）

### スクリーンショット・デモ
- （実施後に更新）

---

## 9. 学びとナレッジ

### 発見したこと
- Google Trends の急上昇キーワードページはクライアントサイド JS でデータが描画されるため、ブラウザ自動化ツールが必要（`requests` や `curl` では取得不可）
- Browser Use は WebVoyager ベンチマーク 89%（Computer Use 56%比）と、Web タスクに特化した精度が高い
- Daemon アーキテクチャにより連続コマンド実行が約50ms で処理され、実用的な速度

### うまくいったこと
- （実施後に更新）

### うまくいかなかったこと
- （実施後に更新）

### Tips・ベストプラクティス
- `browser-use state` コマンドで JS レンダリング完了を確認してから `get text` する（タイミング問題の回避）
- 短時間連続リクエストはブロックされやすいため、リクエスト間に数秒のウェイトを設ける
- アンチボット検出が強いサービスは `--profile` オプションで実際の Chrome プロファイルを使用する
- `--session` オプションで名前付きセッションを使うとマルチタスクがしやすい

### よくあるエラーと対処法
- **`get text` が空になる**: JS レンダリング完了前にコマンドを実行している → `state` で確認後に実行
- **アクセスがブロックされる**: Google のアンチボット検出 → `--profile` で実際の Chrome プロファイルを使用

---

## 10. 判定と今後のアクション

### 総合評価
⭐️⭐️⭐️⭐️⭐️（完了時に記入）

### 導入判定
- [ ] 即座に導入推奨
- [x] 条件付きで導入可（実際に Google Trends 取得が動作することを確認後）
- [ ] 追加検証が必要
- [ ] 導入見送り

### 判定理由
- 調査段階では技術的に問題なく実現可能と判断
- Computer Use と比較して精度・コスト・速度いずれも優位
- 実際の動作確認（Google Trends 取得）を経て判定を更新する

### 次のステップ
- [x] リサーチ・調査完了（2026/04/20）
- [ ] インストール・MCP 登録の実施
- [ ] Google Trends 急上昇キーワード取得の PoC 実施
- [ ] Computer Use との実行結果比較
- [ ] 定期実行・自動化フローの設計

### 追加で検証したい項目
- Google Trends 以外の用途（ECサイト価格比較、求人情報収集など）
- クラウド版（$0.05/step）とセルフホスト版の使い分け判断
- Chrome DevTools MCP（Google Chrome チーム提供、2025年9月公開）との比較・使い分け

---

## 📚 関連リソース

### 公式ドキュメント
- [GitHub - browser-use/browser-use](https://github.com/browser-use/browser-use)
- [Browser Use CLI ドキュメント](https://docs.browser-use.com/open-source/browser-use-cli)
- [Browser Use MCP Server ドキュメント](https://docs.browser-use.com/open-source/customize/integrations/mcp-server)

### 参考記事・事例
- [Helicone - Browser Use vs Computer Use vs Operator（比較記事）](https://www.helicone.ai/blog/browser-use-vs-computer-use-vs-operator)
- [DevelopersIO - Browser Use Web UI 業務適用検証（Classmethod）](https://dev.classmethod.jp/articles/browser-use-web-ui/)
- [PC Watch - browser-use 使い方コラム](https://pc.watch.impress.co.jp/docs/column/nishikawa/1654156.html)
- [WEEL - Browser Use 実践ガイド（日本語）](https://weel.co.jp/media/tech/browser-use/)
- [Scrape.do - Google Trends スクレーピング完全ガイド](https://scrape.do/blog/google-trends-scraping/)
- [ScrapingBee - Best Google Trends Scraping APIs 2026](https://www.scrapingbee.com/blog/best-google-trends-api/)

### 社内関連ドキュメント
- 関連検証ログ: Computer Use による Google Trends 調査（過去の運用）

### 検証データ・ログ
- （実施後に更新）

---

## ✅ メモ・議論ログ
- 2026/04/20: Amical 音声メモからリサーチ依頼。「Computer Use で Google Trends の急上昇キーワードを調べていたが、Browser Use CLI で同等のことができるか」という課題感から調査開始
- 2026/04/20: リサーチ結果として「技術的に十分実現可能、Computer Use より精度・コスト面で優位」と判断。実際の PoC は後日実施予定

---

## 📝 更新ログ
<!-- このセクションはスキルが自動で追記する。手動編集不要。 -->
| 日時 | 更新内容の概要 |
|---|---|
| 2026/04/20 | ファイル作成（init）— リサーチ結果を全セクションに反映 |
