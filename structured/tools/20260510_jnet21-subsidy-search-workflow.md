# J-Net21 補助金検索ワークフロー 検証ログ

> ステータス: 完了
> 作成日: 2026/05/10
> 最終更新: 2026/05/10
> ファイルパス: /Users/shogo/Documents/AI事業OS/30_プロジェクト別/knowledge-vault/vault/structured/tools/20260510_jnet21-subsidy-search-workflow.md

---

## 📋 検証概要

- **ツール/サービス名**: J-Net21（中小企業ビジネス支援サイト） + Browser Use CLI + Claude Code
- **検証対象**: 補助金・助成金情報の自動収集・Excel出力ワークフロー
- **バージョン/リリース日**: 2026/05/10 実施
- **検証期間**: 2026/05/10（単日検証）
- **検証担当者**: shogo-tanaka-work
- **検証ステータス**: 完了

---

## 1. 背景と検証目的

### なぜこの検証を行うのか
- 起業支援・経営支援に使える補助金・助成金情報を定期的に収集・整理したい
- J-Net21（中小機構運営）は補助金情報の信頼できる一次ソースだが、手動で調べると時間がかかる
- Browser Use CLI で自動取得・フィルタリング・Excel出力まで一気通貫でできるか検証

### 解決したい課題
- 検索条件（分野・地域・期間）ごとに毎回手動で調べている
- 「今月申請できる補助金」を一覧で把握したい
- 再利用可能なスキルとして Claude Code に組み込みたい

### 期待される効果・ビジネスインパクト
- 補助金調査工数の大幅削減（手動30分 → 自動5分）
- 検索条件を変えるだけで毎月使い回せるワークフロー
- Claude Code スキルとして配布・共有可能

---

## 2. ツール/機能の基本情報

### 概要
- **J-Net21 snavi2**: 補助金・助成金・融資・セミナーを横断検索できる中小機構の支援情報データベース
- **Browser Use CLI**: ブラウザをCLIで操作するツール。`open` / `eval` / `state` コマンドで情報抽出
- **Claude Code**: ワークフロー全体の制御・コード生成・Excel出力を担当

### 提供元
- J-Net21: 独立行政法人 中小企業基盤整備機構（中小機構）https://j-net21.smrj.go.jp/
- Browser Use CLI: Browser Use Inc. https://docs.browser-use.com/

### 主要機能（今回使用したもの）
- `browser-use open [URL]` : ページをロード
- `browser-use eval "[JS]"` : JavaScript を実行して DOM から情報抽出
- `browser-use state` : ページのアクセシビリティツリーを取得（リンク・テキスト）
- Python スクリプト（fetch_and_filter.py）: 全ページ一括取得 + 日付フィルタリング
- Python スクリプト（create_excel.py）: 色分け付き Excel 出力（openpyxl）

### 技術スタック
- Browser Use CLI（`/Users/shogo/.browser-use-env/bin/browser-use`）
- Python 3 + openpyxl
- Claude Code（Sonnet 4.6）

---

## 3. 検証方法

### 検証環境
- **使用アカウント**: shogo-tanaka-work（個人）
- **プラン/エディション**: 無料サイト（J-Net21は認証不要）
- **検証環境**: ローカル Mac / Claude Code セッション内

### 検証シナリオ
1. J-Net21 の補助金検索ページにアクセスし、サイトが読み取れるか確認
2. 検索パラメータ（category / type / field / prefecture / period）を全解析
3. 掲載日基準で直近1ヶ月の補助金一覧を取得（67件）
4. 募集期間基準に切り替えて「2026年5月に申請可能な補助金」を取得（56件）
5. Excel に出力（色分け・ヘッダー固定・検索条件シート付き）
6. Claude Code スキル（jnet21-subsidy-search）として実装・パッケージ化

### 検証データ・サンプル
- 対象URL: `https://j-net21.smrj.go.jp/snavi2/results.php`
- 検索条件: category=2 / type[]=3 / field[]=24,27,28,35,36,37 / prefecture[]=00 / period=2
- 取得件数: 全131件のうち56件（2026年5月に募集期間がかかるもの）

### 前提条件・制約事項
- `browser-use extract` コマンドは未実装（2026/05時点）→ `eval` + JavaScript で代替
- `browser-use wait N（秒数）` は未対応 → `sleep 2`（シェル）で代替
- 日付フィルタはURLパラメータ（startDate / endDate）が無効 → Python で全件取得後にフィルタ

---

## 4. 検証結果

### 定性的評価

#### 機能面の評価
- ページ読み取りは `state` コマンドで問題なく取得できた（テキスト・リンク・属性すべて）
- JavaScript `eval` による DOM 操作が最も柔軟・強力。フォームパラメータの全探索も可能
- ページネーションの正しいURL構造は `state` で実際のリンクを取得して確認できた

#### 操作性・UI/UX
- Claude Code からの自然言語操作がスムーズ
- `browser-use open → sleep → eval` の3ステップが基本パターンとして安定
- セッションをまたいでブラウザが維持されるため連続操作が快適

#### 出力品質
- 全131件のリスト取得成功（重複なし）
- 募集期間の正規表現抽出（`募集期間[：:]\s*(\S+?～\S+)`）が高精度に機能
- Excel 出力は色分け（橙・黄・白/薄青）、ヘッダー固定、2シート構成で実用レベル

#### 実用性
- 検索条件変更のたびに URLパラメータを組み替えるだけで同じワークフローが再利用可能
- スキル化することでトリガーフレーズから即実行できる

---

### 定量的評価

#### 導入コスト

| 項目 | 内容 | 金額/工数 |
| --- | --- | --- |
| 初期設定時間 | Browser Use CLI インストール済みのため設定不要 | 0分 |
| 学習時間 | パラメータ解析・スクリプト作成 | 約60分（今回の検証セッション） |
| 初期費用 | J-Net21 無料 / Browser Use CLI オープンソース | 0円 |

#### 運用コスト

| 項目 | 内容 | 金額 |
| --- | --- | --- |
| 月額利用料 | J-Net21 無料 | 0円 |
| Claude Code 利用料 | セッション内のトークン使用分 | 数十円/回（推定） |
| 従量課金 | なし | - |

#### パフォーマンス

| 項目 | 測定結果 | 備考 |
| --- | --- | --- |
| 1ページ取得時間 | 約3秒（open 1秒 + sleep 2秒） | |
| 全5ページ取得時間 | 約15〜20秒 | Python スクリプト実行 |
| Excel生成時間 | 約1秒 | openpyxl |
| 総所要時間（対話含む） | 約10分 | 条件確認〜Excel出力まで |

#### ROI試算
- **削減できる工数**: 手動調査 30分/回 → 自動 5分/回（25分削減）
- **月次利用想定**: 月4回（週1回）→ 月100分の工数削減
- **コスト削減額**: 人件費換算で月1万円超（時給6,000円換算）
- **投資回収期間**: 初回利用で回収済み

---

## 5. 比較・優位性分析

### 既存ツール/類似サービスとの比較

| 項目 | Browser Use CLI + Claude | 手動検索 | Computer Use |
| --- | --- | --- | --- |
| 取得精度 | ◎ DOM直接解析 | ◎ | ○ 画像認識依存 |
| 速度 | ◎ 全件15秒 | △ 30分 | △ 遅い |
| コスト | ◎ ほぼ無料 | △ 人件費 | △ API費用高 |
| 柔軟性 | ◎ 条件変更が容易 | ○ | ◎ |
| 再利用性 | ◎ スキル化済み | ✗ | △ |

### 優位性
- 認証不要サイトならほぼ完璧に自動化可能
- `eval` による JavaScript 実行で任意のDOM操作・データ抽出が可能
- Python スクリプトとの組み合わせで複雑なフィルタリングも対応

### 劣位性・懸念点
- `extract` コマンドが未実装のため `eval` + JS を書く必要がある
- ページ構造変更（サイトリニューアル）に弱い
- 認証が必要なサイトはセッション管理が別途必要

---

## 6. リスク評価

### セキュリティ

| 評価項目 | 評価 | 詳細 |
| --- | --- | --- |
| データ保管場所 | ローカル | J-Net21データはローカルにのみ保存 |
| 暗号化 | - | 公開情報のため不要 |
| アクセス制御 | - | 公開サイトのため不要 |
| スクレイピング可否 | ○ | J-Net21 利用規約上の問題なし（公開情報） |
| コンプライアンス | ○ | 中小機構公式サイト・公開情報の収集 |

### ベンダーロックインリスク
- J-Net21 のURL構造・パラメータ変更でスクリプト修正が必要になる可能性あり
- Browser Use CLI は OSS のため継続性リスクは低い

### 技術的リスク
- J-Net21 サイトのリニューアルでページ構造が変わると `eval` のJS要修正
- `sleep 2` のタイミングはネットワーク環境により調整が必要な場合あり

---

## 7. 連携性・拡張性

### 既存システムとの連携

| 連携先 | 方法 | 難易度 | 備考 |
| --- | --- | --- | --- |
| Claude Code スキル | SKILL.md + scripts/ | ✅ 完了 | jnet21-subsidy-search スキルとして実装済み |
| Excel (openpyxl) | Python スクリプト | ✅ 完了 | 色分け・ヘッダー固定・複数シート |
| Notion / Slack | 追加実装で可能 | △ | JSON 出力を入力とすれば連携可能 |

### API/統合オプション
- J-Net21 は公式 API 非提供（HTML スクレイピングのみ）
- JSON 中間ファイル（`/tmp/subsidy_data.json`）経由で他ツールと連携可能

### 拡張性・カスタマイズ性
- 検索条件（分野・地域・期間・カテゴリ）はすべてパラメータ化済み
- `fetch_and_filter.py` / `create_excel.py` を個別に呼び出し可能
- フィルタモード `period`（募集期間基準）/ `publish`（掲載日基準）を切り替え可能

---

## 8. 実際の使用例・サンプル

### ユースケース1: 2026年5月に申請できる補助金一覧

**シナリオ**: 募集期間が2026年5月にかかる補助金を全国・補助金種別で検索  
**検索URL**:
```
https://j-net21.smrj.go.jp/snavi2/results.php?category=2&page={page}&sort=publish_date_default
  &type%5B%5D=3
  &field%5B%5D=24&field%5B%5D=27&field%5B%5D=28&field%5B%5D=35&field%5B%5D=36&field%5B%5D=37
  &prefecture%5B%5D=00
  &period=2&displaysort=DESC&displaycount=30
```
**出力**: 56件を Excel（色分け付き）に出力  
**評価**: ◎ 全件正常取得・期間フィルタも正確

### ユースケース2: 直近1ヶ月の掲載分一覧

**シナリオ**: 掲載日基準で2026/04/10〜05/10の補助金を取得  
**出力**: 67件を Excel に出力  
**評価**: ◎

### 成果物
- Excel ファイル: `2026年5月利用可能補助金一覧.xlsx`（56件）
- スキルファイル: `jnet21-subsidy-search.skill` / `jnet21-subsidy-search.zip`

---

## 9. 学びとナレッジ

### 発見したこと
- J-Net21 の snavi2 検索は `field[]` `type[]` `prefecture[]` をURLパラメータで完全に制御できる
- `period=1`（公開日）と `period=2`（開催・開始日）で全く異なる結果になる。用途に応じた使い分けが重要
- 日付範囲フィルタ（startDate / endDate）はURLパラメータでは機能しない → Python で全件取得後フィルタが正解
- ページネーションは `page=N` パラメータで制御（初回は `search_exec=1` が必要）

### うまくいったこと
- `browser-use eval` + JavaScript による DOM 解析で全フォームパラメータを完全解読できた
- `state` コマンドでページネーションリンクの実URLを取得し、正しいページネーション構造を把握
- 正規表現 `募集期間[：:]\s*(\S+?～\S+)` で日本語の募集期間表記を確実に抽出
- Python スクリプト（fetch_and_filter.py + create_excel.py）で安定したバッチ処理を実現

### うまくいかなかったこと
- `browser-use extract` は未実装 → `eval` + JavaScript で代替必要
- `browser-use wait 3` は未対応 → `sleep 2`（シェル）で代替
- URLパラメータによる日付フィルタ（startDate/endDate）は無効
- フォーム submit ボタンをクリックすると別の検索ページに飛んでしまう

### Tips・ベストプラクティス
- **基本パターン**: `browser-use open URL → sleep 2 → browser-use eval "JS"`
- **全パラメータ探索**: `document.querySelectorAll('input[type=checkbox]')` で全チェックボックスを name/value/label ごと取得できる
- **ページネーション取得**: `.pagination-link` の `href` を拾うと正確な遷移URLがわかる
- **重複除去**: JS側で `Set` を使いながら `href` をキーに一意化する
- **募集期間パース**: 年月日を `-` に置換して `datetime.strptime(s, '%Y-%m-%d')` に渡す

### よくあるエラーと対処法
| エラー | 原因 | 対処 |
|-------|------|------|
| `browser-use extract` 未実装 | CLIコマンド未対応 | `browser-use eval "document.body.innerText"` で代替 |
| `browser-use wait 3` エラー | 引数形式が違う | `sleep 2`（シェル） / `browser-use wait selector .classname` |
| ページ取得で空配列 | ロード前にevalを実行 | `browser-use open` 後に `sleep 2` を挟む |
| JSON.parse エラー | `result: ` プレフィックスが含まれる | `output[8:]` でスライスして除去 |
| 日付フォーマット変換エラー | 「令和N年」等の表記 | J-Net21は西暦表記のため実際には問題なし |

---

## 10. 判定と今後のアクション

### 総合評価
⭐️⭐️⭐️⭐️⭐️（5/5）

### 導入判定
- [x] 即座に導入推奨

### 判定理由
- 認証不要のサイトであれば Browser Use CLI + Claude Code で完全自動化が可能
- コスト・精度・再利用性のバランスが優秀
- Claude Code スキル（jnet21-subsidy-search）として実装済みで即利用可能

### 次のステップ
- [x] 検証終了（スキル化まで完了）
- [ ] 月次定期実行のスケジュール化（/schedule スキルで cron 設定）
- [ ] Notion や Slack への自動投稿連携
- [ ] 都道府県別フィルタ対応の強化

### 追加で検証したい項目
- セミナー・イベント（category=1）での同様のワークフロー
- 認証が必要なサイトへの応用（補助金申請ポータル等）
- 定期実行（週次・月次）での差分検出

---

## 📚 関連リソース

### 公式ドキュメント
- J-Net21 支援情報ヘッドライン: https://j-net21.smrj.go.jp/snavi/support/
- J-Net21 snavi2 検索: https://j-net21.smrj.go.jp/snavi2/results.php
- Browser Use CLI: https://docs.browser-use.com/open-source/browser-use-cli

### 社内関連ドキュメント
- Browser Use CLI 基礎検証: `structured/tools/20260420_browser-use-cli.md`
- Browser Use Desktop App: `structured/tools/20260504_browser-use-desktop-app.md`

### 検証データ・ログ
- スキルファイル: `/Users/shogo/Documents/AI事業OS/jnet21-subsidy-search.zip`
- スキルファイル（.skill）: `/Users/shogo/Documents/AI事業OS/jnet21-subsidy-search.skill`
- Excel出力サンプル: `/Users/shogo/Documents/AI事業OS/2026年5月利用可能補助金一覧.xlsx`

---

## ✅ メモ・議論ログ

- J-Net21 の snavi2 パラメータは `browser-use eval` でフォームを直接探索することで完全解読できた
- `period=1`（公開日）vs `period=2`（募集期間）の違いがユーザー要件的に重要。最初に確認すべき
- 掲載日133件 vs 募集期間56件（2026年5月）という結果差が顕著。フィルタ基準によって大きく変わる
- 「期間記載なし」が多数（67件）存在する。これらは通年型の制度が多い模様

---

## 📝 更新ログ

| 日時 | 更新内容の概要 |
|---|---|
| 2026/05/10 | ファイル作成（init）・検証完了のため finalize 同時実施 |
