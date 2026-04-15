# note記事分析AIエージェント 検証ログ

> ステータス: 進行中
> 作成日: 2026/04/15
> 最終更新: 2026/04/15
> ファイルパス: /Users/shogo/ObsidianVault/knowledge-vault/structured/projects/20260415_note-article-analysis-agent.md

---

📋 プロジェクト概要
* カテゴリ: AIエージェント開発 / コンテンツ分析
* 期間: 2026/04/15 -（検証中）
* 主要メンバー: 田中省伍
* ステークホルダー: （要記入）
* プロジェクトステータス: 進行中
* Linearタスク: SHO-134

---

## 1. 背景と目的

* note.jpの技術・AI・ビジネスジャンルにおいて、バズっている記事・有料記事・SEO上位記事を効率よく収集・分析したい
* 手動でnoteを巡回するのはコストが高く、見逃しが多い
* 「生成AIの組織導入・展開」「経営×生成AI」など特定テーマのトレンドをキャッチアップしたい
* 収集した情報をDiscord（個人）とSlack（チーム向け）に自動配信する仕組みを作る

---

## 2. 取り組み内容

### 実施した施策・活動

* note.jp のデータ取得方法を調査（RSS / 公式API / 非公式API / スクレイピング）
* 「良い記事」の定量指標を整理し、スコアリング式を設計
* ターゲットジャンル・収集ハッシュタグを決定
* アーキテクチャ（フェッチ→スコアリング→要約→配信）を設計
* Linear SHO-134 に調査結果を追記

### 使用したツール・技術

* note非公式API v3（データ取得メイン）
* Python / httpx（APIフェッチ予定）
* Claude API / claude-sonnet-4-6（記事要約・SEO分析予定）
* Discord Bot（個人向け配信予定）
* Slack Webhook（チーム向け配信予定）

### 主要な意思決定とその理由

* **非公式API v3 をメインに採用**: 公式APIが存在しないため。スキ数・有料フラグ・フォロワー数など豊富なデータが取得可能
* **スクレイピングはフォールバック**: 利用規約で明示禁止はないが、API優先で負荷を最小化
* **レート制限対策**: 1〜3秒ディレイ設定で対応
* **定期実行基盤として GitHub Actions を採用**: Cloudflare Workers・Vercel・GAS・Google Colab と比較検討の上で決定。理由は「4. 学びとナレッジ > 定期実行基盤 技術選定メモ」参照

---

## 3. 進捗と成果

### 達成できたこと

* note.jp のデータ取得方針を確定（非公式API v3 採用）
* 主要APIエンドポイントを特定済み
* スコアリング式（案）を策定

### 定量的な成果

* （随時更新）

### 定性的な成果

* APIエンドポイント一覧・スコアリング式・アーキテクチャ設計を Linear SHO-134 に集約

---

## 4. 学びとナレッジ

### うまくいったこと（Good）

* （随時更新）

### うまくいかなかったこと（Bad）

* （随時更新）

### 改善ポイント（Improve）

* （随時更新）

### 技術的な発見・Tips

* note には公式APIがなく、非公式API v3（`https://note.com/api/v3/`）が広く使われている
* robots.txt では `/n/*`（記事）`/m/*`（マガジン）のクロールは許可されている
* 有料記事の本文は購入ユーザー権限が必要なため、タイトル・冒頭部分のみ取得可能
* RSS はユーザー別のみで、タグ別・人気記事別のフィードは存在しない

#### 定期実行基盤 技術選定メモ（2026/04/15）

| 選択肢 | 実行時間上限 | 言語 | 無料cron頻度 | 今回の評価 |
|---|---|---|---|---|
| **GitHub Actions** | 6時間 | 何でも可 | 制限なし（Public は完全無料） | **採用** |
| Cloudflare Workers | 30秒（無料）/ 15分（有料） | JS/TS のみ | 可 | 実行時間・言語がネック |
| Vercel | 10秒（無料）/ 60秒（Pro） | JS/TS 主体 | 1日1回（無料） | 実行時間・コストがネック |
| Google Apps Script | 6分/回 | JS のみ | 可（無料） | JS のみ・6分制限がネック |
| Google Colab | セッション依存 | Python | 非対応（手動） | 自動化に不向き |

**決定理由**
* このエージェントは「rate limit ディレイ込みの API フェッチ（20件）+ Claude API 呼び出し」で 1〜2分かかる見込み
* Cloudflare Workers（30秒）・Vercel（10秒）・GAS（6分）は実行時間がネック
* Colab は自動化非対応
* GitHub Actions は Public リポジトリなら完全無料・Python ネイティブ・6時間制限で余裕

**コスト試算（毎日1回実行）**
* GitHub Actions: $0（Public リポジトリ）
* Claude Haiku（テーマ判定 × 20件）: 約45円/月
* Claude Sonnet（通知文生成 × 10件）: 約135円/月
* **合計: 約180円/月**

---

## 5. 課題と対応

### 発生した課題

* （随時更新）

### 対応方法

* （随時更新）

### 未解決の課題

* API v3 の現時点での疎通確認（まだ実測していない）
* ビュー数フィールドの取得可否（実装時期によって不安定との報告あり）
* レート制限の実測値（1〜3秒ディレイで十分かは未確認）
* 有料記事の本文取得可否（購入権限が必要と推測）

---

## 6. コストとリソース

### 人的リソース

* 田中省伍（1名）

### 金銭的コスト

* Claude API 費用: （随時更新）
* その他インフラ費用: （随時更新）

### コスト対効果

* （完了時に記入）

---

## 7. 今後の展開

### 次のアクション

* **Phase 1**: Python スクリプトで API v3 の疎通確認（実測）
  * `https://note.com/api/v3/searches?context=note&q=生成AI` でヒット確認
  * スキ数・有料フラグ・コメント数が取得できるかを検証
* **Phase 2**: スコアリングロジックの実装・チューニング
* **Phase 3**: Claude API による要約・SEO要素抽出の品質評価
* **Phase 4**: Discord Bot / Slack Webhook への配信実装

### 収集ハッシュタグ（確定）

`#生成AI` `#ChatGPT` `#LLM` `#Claude` `#AI活用` `#組織変革` `#経営` `#マーケティング`

### スコアリング設計（確定版・2軸）

```python
# バズスコア: 1日あたりの engagement 速度
days = max((now - published_at).days + 0.5, 0.5)
engagement_weight = likes + comments * 2
buzz_score = (engagement_weight / days) * (1.2 if is_paid else 1.0)

# エンゲージメント率スコア: フォロワー規模比（無名クリエイターの良記事を拾う）
eng_score = (engagement_weight / max(creator_followers, 100)) * (1.2 if is_paid else 1.0)

# LLM テーマ判定（Claude Haiku）でテーマ適合スコア 0.0〜1.0 を取得し乗算
final_buzz = buzz_score * theme_score
final_eng  = eng_score  * theme_score

# 各軸上位5件の Union（重複除去）→ 最大10件を配信
```

### 主要APIエンドポイント

```
# タグ・キーワード検索
GET https://note.com/api/v3/searches?context=note&q={keyword}

# ハッシュタグ詳細
GET https://note.com/api/v2/hashtags/{tagname}

# 記事詳細（スキ数・有料フラグ・コメント数）
GET https://note.com/api/v3/notes/{article_id}/

# クリエイター記事一覧
GET https://note.com/api/v2/creators/{username}/contents?kind=note&page=1

# クリエイター情報（フォロワー数・認証バッジ）
GET https://note.com/api/v2/creators/{creator_id}
```

### 横展開の可能性

* Zenn / Qiita など他の技術記事プラットフォームへの応用

### 長期的な改善案

* 時系列分析によるトレンドの変化検出
* 記事公開からスキ数増加速度のモニタリング（急上昇検知）

---

📚 関連リソース

### 成果物・ドキュメント

* Linear SHO-134: https://linear.app/shogoworks/issue/SHO-134/note記事分析aiエージェント構築キーワード検索seoバズ分析

### 参考資料

* [【2025年7月】noteの非公式APIを整理｜ブオナローティ](https://note.com/fuji1080/n/n0b22ae25a97b)
* [note非公式APIの活用アイディア６選](https://note.com/manochi/n/n4f57e7ae7b9b)
* [Pythonで自分のnote記事の閲覧数・スキ数・コメント数を取得する方法](https://note.com/midorimegane/n/n1574645cf467)

### 関連プロジェクト

* （随時更新）

---

✅ メモ・雑記

* 壁打ちセッション（2026/04/15）で方針を固めた
* 「生成AIの組織導入・展開」「経営×生成AI」テーマが特に気になっているとのこと
* Discord が個人用メイン、Slack は世間・チーム向けの2配信先構成

---

## 📝 更新ログ
<!-- このセクションはスキルが自動で追記する。手動編集不要。 -->
| 日時 | 更新内容の概要 |
|---|---|
| 2026/04/15 | ファイル作成（init）— 壁打ちセッションの調査結果・方針を初期投入 |
| 2026/04/15 | 技術選定メモ追記（実行基盤比較・スコアリング確定版・コスト試算） |
