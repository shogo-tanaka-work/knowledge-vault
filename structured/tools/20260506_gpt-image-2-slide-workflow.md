# GPT Image 2を用いたスライド制作ワークフロー 検証ログ

> ステータス: 検証中
> 作成日: 2026/05/06
> 最終更新: 2026/05/06
> ファイルパス: /Users/shogo/ObsidianVault/knowledge-vault/structured/tools/20260506_gpt-image-2-slide-workflow.md

---

📋 プロジェクト概要
* カテゴリ: AIスライド制作 / 画像生成 / PowerPoint自動化
* 期間: 2026/05/06 -（検証中）
* 主要メンバー: shogo
* ステークホルダー: 法人向け資料制作、AI教材、スライド制作支援ワークフロー
* プロジェクトステータス: 進行中

---

## 1. 背景と目的
* Claude Agent SkillsやPowerPoint操作系Skillを使うとPPTX生成はできるが、出力がAIらしいシンプルなデザインに寄りやすい。
* 目標は、Big4系コンサル資料のような高密度・整った余白・罫線・注釈・チャート表現を持つスライドデザインへ近づけること。
* LP制作では、GPT Image 2で高品質なデザイン画像を生成し、Figmaやコード化ツールを経由してHTML/CSSへ落とし込む流れが見えている。
* この考え方をスライド制作にも応用できないか検証する。
* 目的は、GPT Image 2を「デザインカンプ生成担当」、PowerPoint Agent Skillsを「PPTX実装担当」として分業できるか見極めること。

---

## 2. 取り組み内容

### 実施した施策・活動
* noteのパワポ研アカウント `https://note.com/powerpoint_jp` がCodexから読めるか確認した。
* 公開ページ、記事一覧、公開個別記事は読み取り可能であることを確認した。
* パワポ研記事を、スライドデザインの型や構成パターン抽出に使える可能性を確認した。
* GPT Image 2 / `gpt-image-2` の利用可否を調査した。
* Codex内蔵の画像生成ツールではモデル名を直接指定できないことを確認した。
* OpenAI API上では `gpt-image-2` が画像生成・編集向けモデルとして確認できることを確認した。
* 今回の実運用では、Codexから直接呼ぶより、ChatGPTブラウザ画面でGPT Image 2を呼び出す方向が現実的と判断した。
* 国内外で「GPT Image 2をPowerPoint / slide deck / Figma / Canvaに応用する事例」があるか調査した。
* SlidesPilot、NoteGPT、CapCut、Figma Slides、SlideForgeなど、近い思想のツール・記事を確認した。

### 使用したツール・技術
* ChatGPT / GPT Image 2
* Codex
* OpenAI API
* PowerPoint Agent Skills
* Figma / Figma Slides
* Canva
* SlideForge
* パワポ研 note
* Astro / HTML / CSS制作フローの応用知見

### 主要な意思決定とその理由
* GPT Image 2をPPTX生成そのものではなく、完成スライド画像・デザインカンプ生成に使う。
  * 理由: 画像生成モデルは視覚品質に強いが、編集可能なPPTXオブジェクト生成は別問題のため。
* PPTX化は別工程に分ける。
  * 理由: 画像1枚貼り、Figma/Canva経由、Visionで解析してPPTXオブジェクトへ再構成、という複数ルートがあるため。
* まずは1枚スライド単位でPoCする。
  * 理由: 比較表、市場マップ、ロードマップなど型が明確なスライドで品質差を見やすいため。

---

## 3. 進捗と成果

### 達成できたこと
* GPT Image 2はOpenAI公式モデルページで確認できた。
* Codexのこのチャット環境では、内蔵画像生成ツールにモデル指定引数がないため、`gpt-image-2` を直接指定できないと整理した。
* OpenAI API経由なら `gpt-image-2` を使った画像生成・編集の実装は可能と整理した。
* ChatGPTブラウザ画面でGPT Image 2を使い、生成画像をスライド制作フローへ持ち込む方針が現実的と判断した。
* 既存事例調査では、GPT Image 2を「slide-ready graphics」やスライド生成ツールに組み込む動きが確認できた。
* SlideForgeの「画像・スクショから編集可能PPTXへ再構成する」思想が、今回の仮説にかなり近いと確認した。

### 定量的な成果
* 調査した観点:
  * GPT Image 2公式モデル確認
  * Codexからの直接利用可否
  * OpenAI API経由の利用可否
  * ChatGPTブラウザ経由の運用可能性
  * PowerPoint / Figma / Canva / SlideForge連携事例
* 実スライド生成PoCは未実施。

### 定性的な成果
* 「画像生成モデルでスライドの見た目を先に作る」という発想は、Agent Skills単体の弱点を補う可能性が高い。
* GPT Image 2をデザインカンプ生成に使い、Agent SkillsでPPTXとして再実装する分業が最も筋がよい。
* ただし、画像から完全編集可能なPPTXへ落とす工程が最大の検証ポイント。

---

## 4. 学びとナレッジ

### うまくいったこと（Good）
* GPT Image 2の公式存在確認、Codexからの直接指定不可、API/ChatGPT経由の利用可能性を整理できた。
* LP制作で使われる「画像生成 → Figma / コード化 → 実装」の考え方を、スライド制作へ転用する仮説が立った。
* スライド制作では、画像生成とPPTX実装を分けると各AIの得意領域に合う。
* パワポ研の公開noteは、スライドの型抽出に使える可能性がある。

### うまくいかなかったこと（Bad）
* Codex内蔵の画像生成ツールでは、`gpt-image-2` を明示指定できない。
* GPT Image 2で生成した画像は、そのままだと編集可能なPPTXではない。
* Figma SlidesのPPTX exportには、フォント置換、インタラクションの静止化、グラデーションの変換など制限がある。
* 画像1枚貼り運用は見た目はよいが、後からテキストや図形を細かく編集しづらい。

### 改善ポイント（Improve）
* まずは比較表、2軸マップ、ロードマップの3種類でスライド1枚PoCを行う。
* GPT Image 2で生成した16:9画像を、次の3ルートで比較する。
  * 画像1枚としてPowerPointに貼る
  * Figma / Figma Slides / Canvaへ取り込み、PPTX exportする
  * Visionで画像を解析し、PowerPoint Agent Skillsでテキストボックス・図形・罫線・チャート風オブジェクトへ再構成する
* Big4風のスライド品質を測る評価軸を作る。
  * 情報密度
  * 余白
  * フォント階層
  * 罫線・区切り
  * 色数
  * 注釈・脚注
  * チャートの説得力
  * 編集可能性

### 技術的な発見・Tips
* GPT Image 2は「最終成果物」より「視覚的な正解例」を作らせる方が使いやすい。
* PowerPoint Agent Skillsには、完成画像を読み取って再現する役割を持たせるとよい。
* プロンプトでは「consulting slide」「Big Four style」のような雰囲気指定だけでなく、16:9、余白、罫線、凡例、脚注、ページ番号、出典、タイトルの粒度まで指定する必要がある。
* 日本語テキストを含む場合は、画像生成時の文字崩れを考慮し、最終テキストはPPTX側で差し替える前提がよい。

---

## 5. 課題と対応

### 発生した課題
* GPT Image 2をCodexから直接モデル指定して呼べない。
* 画像生成結果を編集可能なPPTXへ変換する工程が未確定。
* Big4風デザインをAIに指示するためのプロンプト・評価基準が未整備。
* パワポ研の知見を参照する場合、著作権・再配布リスクに注意が必要。

### 対応方法
* 当面はChatGPTブラウザ画面からGPT Image 2を使う。
* Codex側では、生成画像を読み取り、PPTX化手順やHTML/CSS化手順を設計する。
* パワポ研は公開記事の読み取り、要約、パターン抽出に限定し、画像や本文の再配布はしない。
* SlideForgeのような画像からPPTX再構成の思想を参考にする。

### 未解決の課題
* GPT Image 2で生成したスライド画像の品質評価は未実施。
* 画像から編集可能PPTXへの再構成品質は未検証。
* Figma / Canva / SlideForge / Agent Skillsのどのルートが最も実用的か未確定。
* API経由で `gpt-image-2` を使う場合のコスト・権限・実装方法は未検証。

---

## 6. コストとリソース

### 人的リソース
* ユーザー: スライド品質の要件定義、Big4風デザインの判断、PoC評価。
* Codex: 調査、ワークフロー設計、ログ化、PPTX化実装補助。
* ChatGPT: GPT Image 2によるスライド画像生成。

### 金銭的コスト
* ChatGPT利用料: 利用プラン内で検証予定。
* OpenAI API利用料: API経由PoCを行う場合は別途計測。
* Figma / Canva / SlideForge等: 無料枠または有料プランの確認が必要。

### コスト対効果
* スライドデザイン初稿の品質が上がれば、従来の「AI生成PPTXを人間が大幅修正する」工程を短縮できる可能性がある。
* 一方、編集可能PPTX化に手間がかかる場合、画像1枚運用または重要スライド限定運用が現実的。

---

## 7. 今後の展開

### 次のアクション
* GPT Image 2で1枚スライド画像を生成する。
  * 比較表
  * 2軸ポジショニングマップ
  * ロードマップ
* 生成画像をPowerPointへ貼り、画像1枚運用の実用性を確認する。
* 生成画像をAgent Skillsで編集可能PPTXへ再構成するPoCを行う。
* 生成画像をFigma / Canva / SlideForgeへ入れた場合のPPTX export品質を比較する。
* Big4風スライドプロンプトのテンプレートを作る。

### 横展開の可能性
* 法人研修資料の表紙・章扉・キースライド生成
* 提案資料のエグゼクティブサマリー生成
* AI教材の図解・比較表・ワークフロー図生成
* LP制作ワークフローとの共通化
* パワポ研由来のスライドパターン辞書との連携

### 長期的な改善案
* GPT Image 2で生成した完成イメージを、PowerPoint XML / pptxgenjs / Agent Skillsで再現する自動パイプラインを作る。
* 「スライド画像 → 構造JSON → PPTX」の中間表現を定義する。
* パワポ研のスライドパターン辞書を、プロンプト生成とPPTX再構成の両方に使う。
* 画像生成モデル、Visionモデル、PowerPoint操作Skillの3段構成にする。

---

📚 関連リソース

### 成果物・ドキュメント
* `structured/tools/20260506_slide-design-patterns.md`
* `structured/projects/powerpoint_jp_research/README.md`
* shogo-works内のClaude Agent Skills / PowerPoint関連Knowledge

### 参考資料
* パワポ研 note: https://note.com/powerpoint_jp
* OpenAI GPT Image 2: https://developers.openai.com/api/docs/models/gpt-image-2
* OpenAI Image generation guide: https://platform.openai.com/docs/guides/image-generation
* SlidesPilot GPT Image 2 Slides: https://www.slidespilot.com/features/gpt-image-2-slides
* NoteGPT GPT Image 2 Slides: https://notegpt.io/gpt-image-2-slides
* CapCut GPT Image 2 presentation design: https://www.capcut.com/ideas/gpt-image-2/gpt-image-2-for-presentation-design
* Figma Slides export: https://help.figma.com/hc/en-us/articles/24848334599447-Export-from-Figma-Slides
* SlideForge image to PPTX: https://slideforge.dev/tools/image-to-pptx
* AI総合研究所 GPT Image 2記事: https://www.ai-souken.com/article/what-is-gpt-image-2

### 関連プロジェクト
* slide-design-patterns Skill
* パワポ研 noteリサーチ
* PowerPoint Agent Skills検証
* AIスライド制作自動化

---

✅ メモ・雑記
* 「AIくさいPPTX」を避けるには、PPTX生成エンジンだけでなく、先に高品質な完成イメージを作る工程が重要。
* GPT Image 2は、AIスライド制作におけるアートディレクター役として使うのが有望。
* 画像1枚運用は最短で見た目が良いが、編集性が弱い。重要ページのみ画像1枚、本文ページはPPTXオブジェクト、というハイブリッドもあり。
* 日本語テキストは最終的にPowerPoint側で編集可能テキストとして載せ直す前提が安全。

---

## 📝 更新ログ
<!-- このセクションはスキルが自動で追記する。手動編集不要。 -->
| 日時 | 更新内容の概要 |
|---|---|
| 2026/05/06 | ファイル作成（GPT Image 2を用いたスライド制作ワークフロー検証ログ） |
