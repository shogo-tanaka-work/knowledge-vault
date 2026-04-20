# Claude Design 検証ログ

> ステータス: 検証中
> 作成日: 2026/04/20
> 最終更新: 2026/04/20
> ファイルパス: /Users/shogo/ObsidianVault/knowledge-vault/structured/tools/20260420_claude-design.md

---

## 📋 検証概要

- **ツール/サービス名**: Claude Design（Anthropic Labs）
- **検証対象**: 新機能（リサーチプレビュー）
- **バージョン/リリース日**: リサーチプレビュー / 2026年4月17日
- **検証期間**: 2026/04/20 -（検証中）
- **検証担当者**: shogo-tanaka-work
- **検証ステータス**: 検証中

---

## 1. 背景と検証目的

### なぜこの検証を行うのか
- 2026年4月17日にAnthropicが突如「Claude Design」をリリースし、Figma株が下落するほどの市場インパクトを与えた
- 法人向けスライド・システム解説図の作成にどこまで使えるかを把握したい
- CLAUDE.md等のデザイン指示書との組み合わせで品質がどこまで上がるかを探りたい

### 解決したい課題
- 法人向けスライド（提案書・決算資料・システム解説図）の作成に要する工数を削減したい
- 矢印・補足情報が多いシステム図をAIで自動生成できるか検証したい
- 企業ブランドに沿ったデザインを毎回一から作らずに済む方法を確立したい

### 期待される効果・ビジネスインパクト
- スライド初稿作成時間を大幅削減（現状: 数時間 → 目標: 30分以内）
- デザインシステムを一度登録すれば以後の全スライドに自動適用
- PPTX直接エクスポートにより既存ワークフローへの組み込みが容易

---

## 2. ツール/機能の基本情報

### 概要
Anthropic Labsが提供するリサーチプレビュー段階の新製品。テキストプロンプトからプロトタイプ・スライド・ランディングページ・ワンページャーなどのビジュアルを生成できる。チャット＋キャンバスの二画面構成で、インラインコメントで特定要素に直接フィードバックしながら反復生成できる。

### 提供元
- Anthropic（Anthropic Labs）
- Claude.ai の有料プランに紐づく機能（設定でONにする必要あり）

### 主要機能
- テキストプロンプト → スライド・プロトタイプ・ランディングページ生成
- チャット＋キャンバスの二画面構成（インラインコメント対応）
- **デザインシステム登録機能**: コードベース・デザインファイル・ブランド資料を読み込んで自動適用
- Canva公式連携（生成後にCanvaで共同編集・共有）
- Claude Codeへのハンドオフバンドル（そのままコーディングに渡せる）
- エクスポート: PPTX / PDF / スタンドアロンHTML / ZIP / Canva送出

### 技術スタック・アーキテクチャ
- 動力モデル: **Claude Opus 4.7**
- 生成形式: React 18.3.1 + Babel 7.29.0（固定ハッシュ）
- 内部設計方針（リーク情報より）: 1ファイル1000行以下を強制、デザインシステムの色以外を勝手に追加しない

---

## 3. 検証方法

### 検証環境
- **使用アカウント**: Claude Pro/Max/Team/Enterprise のいずれか（要有効化）
- **プラン/エディション**: Pro以上（デフォルトOFF、設定から有効化必要）
- **検証環境**: Claude.ai（ブラウザ）

### 検証シナリオ
1. Claude Designでシンプルな法人向けスライドを生成する
2. デザインシステム（ブランドカラー・フォント）を登録して一貫性を確認する
3. システム解説図（矢印・フロー）の生成品質を確認する
4. PPTX形式でエクスポートして既存テンプレートとの整合性を確認する
5. CLAUDE.md形式のデザイン指示書を渡した場合の品質変化を確認する

### 検証データ・サンプル
- （実際の検証時に追記）

### 前提条件・制約事項
- Pro以上のプランが必要（Free不可）
- Claude.ai 設定 > Claude Design をONにする必要あり
- 現時点ではリサーチプレビュー段階（機能変更・廃止の可能性あり）
- 2026/04/20時点: まだ実際の使用検証未実施（今回はリサーチのみ）

---

## 4. 検証結果

### 定性的評価

#### 機能面の評価
- 【リサーチ段階】PPTX直接エクスポート対応は実用上の大きな強み
- 【リサーチ段階】デザインシステムの自動適用機能は法人用途で特に有効
- 【リサーチ段階】Canva連携により非エンジニアも最終調整しやすい

#### 操作性・UI/UX
- チャット＋キャンバス二画面構成はイテレーション向き
- インラインコメントで特定要素への直接フィードバックが可能
- （実使用後に追記）

#### 出力品質
- 【第三者評価より】細かい指示なしでは「Anthropic感」に寄った均質なデザインになりやすい
- 【第三者評価より】デザイン知識なしで叩き台を即生成できる点は高評価
- 【第三者評価より】Figmaの代替ではなく、ラピッドプロトタイピング（Lovable代替）として位置づけるべき

#### 実用性
- 法人スライド用途では「叩き台の即生成→Canvaで仕上げ」のハイブリッド運用が現実的
- デザインシステム登録後はオンブランドの一貫性が自動担保される

---

### 定量的評価

#### 導入コスト

| 項目 | 内容 | 金額/工数 |
| --- | --- | --- |
| 初期設定時間 | アカウント有効化〜デザインシステム登録まで | （検証後に更新） |
| 学習時間 | 基本操作を習得するまで | （検証後に更新） |
| 初期費用 | Proプランに含まれる（追加費用なし） | $0（プラン費用別） |

#### 運用コスト

| 項目 | 内容 | 金額 |
| --- | --- | --- |
| 月額利用料 | Proプランに含まれる | プラン費用に含む |
| 従量課金 | Opus 4.7使用のためトークンコスト注意 | （検証後に確認） |

#### パフォーマンス

| 項目 | 測定結果 | 備考 |
| --- | --- | --- |
| 処理速度 | （検証後に更新） | Opus 4.7のため重い可能性 |
| レスポンスタイム | （検証後に更新） | |
| 成功率 | （検証後に更新） | |

#### ROI試算
- **削減できる工数**: スライド初稿作成 数時間 → 目標30分以内（未検証）
- **生産性向上**: （検証後に更新）
- **コスト削減額**: （検証後に更新）

---

## 5. 比較・優位性分析

### 既存ツール/類似サービスとの比較

| 項目 | Claude Design | Claude for PowerPoint | Claude Code + Marp | Claude Artifacts |
| --- | --- | --- | --- | --- |
| PPTXエクスポート | ✅ 直接 | ✅ アドイン経由 | △ PDF変換 | ❌ |
| デザインシステム統合 | ✅ 自動読み込み | ✅ テンプレート読み取り | ✅ CLAUDE.md | △ |
| 対象プラン | Pro以上 | Pro以上 | 全プラン | 全プラン |
| git管理 | ❌ | ❌ | ✅ | ❌ |
| 品質 | 叩き台レベル | オンブランド | 高品質 | 中程度 |
| システム図 | △ | ❌ | ✅ Mermaid | ✅ SVG |

### ユースケース別推奨ルート（リサーチまとめ）

| シナリオ | 推奨アプローチ |
|---------|--------------|
| 既存PPTXテンプレートあり | Claude for PowerPoint |
| ブランド統一スライドを大量生成 | Claude Design（デザインシステム登録→PPTX出力） |
| システム解説図・矢印フロー図 | Claude Code + Mermaid MCP（23種類対応） |
| 複雑なアーキテクチャ図 | Draw.io XML生成 → インポート |
| 決算資料・提案書（品質重視・git管理） | Claude Code + Marp |
| 速度重視の叩き台 | Claude Design |

### 優位性
- PPTX直接エクスポートはArtifactsにない強み
- デザインシステムの自動読み込みにより法人ブランドの一貫性を担保できる
- Canva連携で非エンジニアのチームメンバーも最終編集しやすい

### 劣位性・懸念点
- リサーチプレビュー段階のため機能・仕様が変わる可能性あり
- Opus 4.7専用のためコストが高い
- 細かい指示なしでは均質なデザインに寄りやすい
- Figmaレベルの細かいデザイン制御は不可

---

## 6. リスク評価

### セキュリティ

| 評価項目 | 評価 | 詳細 |
| --- | --- | --- |
| データ保管場所 | 要確認 | Anthropicのサーバー（US）と思われる |
| 暗号化 | 要確認 | （検証後に更新） |
| アクセス制御 | ✅ | Claudeアカウント認証 |
| コンプライアンス | 要確認 | Enterprise版では個別対応の可能性 |

### プライバシー・倫理面
- デザインシステム登録時にブランドファイル・コードベースをアップロードする必要があり、機密情報の取り扱いに注意
- Enterpriseプランでは学習データからの除外設定が利用可能

### ベンダーロックインリスク
- Canvaとの公式連携でエクスポートは容易
- PPTXエクスポートにより既存ツールへの移行は比較的しやすい

### 技術的リスク
- リサーチプレビュー段階のため、本番運用への採用は安定化を待つべき
- Opus 4.7専用のため、モデル変更時に品質が変わる可能性

---

## 7. 連携性・拡張性

### 既存システムとの連携

| 連携先 | 方法 | 難易度 | 備考 |
| --- | --- | --- | --- |
| Canva | 公式連携（ボタン一発） | 低 | 共同編集・共有が可能 |
| Claude Code | ハンドオフバンドル | 中 | そのまま開発に渡せる |
| Microsoft PowerPoint | PPTXエクスポート | 低 | 直接ダウンロード |
| Google Slides | 非対応（MCP連携が必要） | 高 | Claude単体では不可 |

### API/統合オプション
- Claude Code との連携（ハンドオフバンドル）
- Canva公式API連携

### 拡張性・カスタマイズ性
- デザインシステム登録によるブランドカスタマイズ
- コードベース・Figmaファイル・PDFブランド資料のアップロード対応

---

## 8. 実際の使用例・サンプル

### ユースケース1: DevelopersIO事例（Claude Code + Marp）

**シナリオ**: 議事録からMarp形式の提案書スライドをClaude Codeで自動生成
**構成**:
```
rules/（画像プロンプト指針・提案書構成ルール）
commands/（カスタムスラッシュコマンド）
templates/（Marpテーマ・提案書テンプレート）
```
**ポイント**: 固定セクション（契約条項等）はテンプレートから丸コピーを強制し、変更禁止ルールをCLAUDE.mdに記述
**評価**: 実運用レベルに到達している実証済み事例

### ユースケース2: Anthropic Cookbook — frontend aestheticsプロンプト

**シナリオ**: システムプロンプトにデザインシステムを渡して高品質スライドを生成
**入力例**:
```xml
<frontend_aesthetics>
Typography: JetBrains Mono / Playfair Display / Clash Display / IBM Plex family
（Inter・Roboto・Arialは避ける）
Color: CSS variablesで一貫性を確保。支配的カラー＋シャープなアクセント
Motion: CSS-onlyアニメーション、animation-delayでスタガードリビール
</frontend_aesthetics>
```
**評価**: 2段階アプローチ（アウトライン承認→デッキ生成）で品質安定

### スクリーンショット・デモ
- （実際の検証時に追記）

---

## 9. 学びとナレッジ

### 発見したこと
- Claude Designは2026年4月17日リリースの全く新しいツール（3日前）
- PPTX直接エクスポート対応はArtifactsにはなかった強み
- Mermaid MCP Serverで23種類のダイアグラムが生成可能（システム図に有効）
- 日本語コンテキストでは「プロンプト設計3層構造（型・ルール・禁則）」が有効

### うまくいったこと（リサーチ段階）
- 既存PPTXテンプレートがある場合: Claude for PowerPoint が最も適合
- システム解説図: Claude Code + Mermaid MCP の組み合わせが実用品質

### うまくいかなかったこと（既知の課題）
- Google Slidesへの直接書き込みはClaude単体では不可（MCP連携が必要）
- 細かい指示なしでは「Anthropic感」に寄った均質なデザインになりやすい
- 複雑なアーキテクチャ図は詳細プロンプトが必要

### Tips・ベストプラクティス

**デザイン品質を上げるプロンプト設計3層構造（Zenn記事より）:**
```
層1: 型（構成）
  → スライド数・セクション順序を明示

層2: ルール
  → 「1スライド1メッセージ」「タイトル15文字以内」「箇条書き3〜5項目」

層3: 禁則
  → 「文字だけスライド禁止」「曖昧表現禁止（検討中等）」「5色以上禁止」
```

**有効なプロンプト要素（cloudpack記事より）:**
- 目的明示・ターゲット指定・枚数指定・出力形式 の4要素

**Claude Code + Marp のワークフロー例:**
```
Marp形式のMarkdownで作成してください。
スライド枚数: 6枚 / テーマ: AWS導入提案
対象: 経営層
構成: タイトル→課題→メリット→移行フロー→コスト試算→まとめ
```

### よくあるエラーと対処法
- （実際の検証時に追記）

---

## 10. 判定と今後のアクション

### 総合評価
⭐️⭐️⭐️⭐️（完了時に更新 / リサーチ段階では暫定4）

### 導入判定
- [ ] 即座に導入推奨
- [x] 条件付きで導入可（リサーチ段階の暫定判定）
- [ ] 追加検証が必要
- [ ] 導入見送り

### 判定理由
- PPTX直接エクスポートとデザインシステム統合は法人用途で強力
- ただしリサーチプレビュー段階のため本番採用は安定化を待つべき
- ユースケース別に最適ツールが異なるため、用途を絞った実使用検証が必要

### 次のステップ
- [x] リサーチ実施・ログ記録
- [ ] Claude Design を実際に操作して品質を確認（Claude.ai ProアカウントでON設定）
- [ ] デザインシステム登録機能を試す（ブランドカラー・フォント）
- [ ] システム解説図を Mermaid MCP で生成してみる
- [ ] Claude Code + Marp で提案書スライドを実際に生成する

### 追加で検証したい項目
- Claude Designのデザインシステム登録の具体的な手順と品質
- Mermaid MCP Serverの23種類のダイアグラム生成品質
- CLAUDE.mdに書いたデザインルールがどこまで反映されるか
- 複雑なシステム構成図（マイクロサービス・クラウドアーキテクチャ等）の生成品質

---

## 📚 関連リソース

### 公式ドキュメント
- [Introducing Claude Design by Anthropic Labs](https://www.anthropic.com/news/claude-design-anthropic-labs)
- [Get started with Claude Design](https://support.claude.com/en/articles/14604416-get-started-with-claude-design)
- [Set up your design system in Claude Design](https://support.claude.com/en/articles/14604397-set-up-your-design-system-in-claude-design)
- [Claude for PowerPoint](https://claude.com/claude-for-powerpoint)
- [Custom visuals in chat](https://support.claude.com/en/articles/13979539-custom-visuals-in-chat)
- [Prompting for frontend aesthetics | Claude Cookbook](https://platform.claude.com/cookbook/coding-prompting-for-frontend-aesthetics)

### 参考記事・事例
- [Anthropic launches Claude Design | TechCrunch](https://techcrunch.com/2026/04/17/anthropic-launches-claude-design-a-new-product-for-creating-quick-visuals/)
- [Anthropic just launched Claude Design, challenges Figma | VentureBeat](https://venturebeat.com/technology/anthropic-just-launched-claude-design-an-ai-tool-that-turns-prompts-into-prototypes-and-challenges-figma)
- [AIスライド作成の最適解を探る【2026年版】 - Zenn](https://zenn.dev/mjinia/articles/cef5337a4f177f)
- [Claudeでスライド作成！構成案・Artifacts・Marp活用術 - cloudpack](https://cloudpack.jp/column/generative-ai/claude-slide-creation-guide.html)
- [Claude Designスライド作成最速レビュー - note](https://note.com/yoshifujidesign/n/ncddbf57cc4f8)
- [ざっくりClaude Designを触ってみた - Zenn](https://zenn.dev/yokomachi/articles/202604_claude_design_chottodake)
- [Claude Designを触ってみた - Qiita](https://qiita.com/ryu-ki/items/bca0ee8f15a13dfd8cfa)
- [AIに自動でアーキテクチャ図を書いてもらいたい - Qiita](https://qiita.com/nashitake/items/5259d1e26b045d363b6a)
- [Claude Codeで議事録から提案書スライドを自動生成 | DevelopersIO](https://dev.classmethod.jp/articles/claude-code-nano-banana-pro-proposal-slide-generation/)
- [How to use Claude AI + draw.io to Create Architecture Diagrams - DEV Community](https://dev.to/rushier/how-to-use-claude-ai-drawio-to-create-architecture-diagrams-for-projects-17i1)
- [Reveal Presentations — Generate Slide Decks from Claude Code | Autonomee.ai](https://autonomee.ai/blog/reveal-presentations-generate-slide-decks-from-claude-code/)
- [Every Way to Make Slides with Claude in 2026](https://www.the-ai-corner.com/p/every-way-to-make-slides-with-claude)
- [Claude Design System Prompt（非公式・リーク）](https://github.com/elder-plinius/CL4R1T4S/blob/main/ANTHROPIC/Claude-Design-Sys-Prompt.txt)

### 社内関連ドキュメント
- リサーチプランファイル: `/Users/shogo/.claude/plans/ticklish-greeting-feather.md`

---

## ✅ メモ・議論ログ
- 2026/04/20: Claude Designが3日前（4/17）にリリースされたばかりであることが判明。リリース直後の検証となる
- 2026/04/20: 今回は実際の操作ではなくWebリサーチのみ。次フェーズで実操作検証を行う
- 2026/04/20: スライド用途はウェブサイト制作より法人向けスライド・システム解説図を重視してリサーチ
- 2026/04/20: Claude DesignはFigmaの代替ではなくLovable代替（ラピッドプロトタイピング）というポジショニングが業界評価として定着しつつある

---

## 📝 更新ログ
<!-- このセクションはスキルが自動で追記する。手動編集不要。 -->
| 日時 | 更新内容の概要 |
|---|---|
| 2026/04/20 | ファイル作成（init）— Webリサーチ結果を元に初稿作成 |
