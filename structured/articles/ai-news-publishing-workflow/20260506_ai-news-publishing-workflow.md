# AIニュース収集・公開フロー 検証ログ

> ステータス: 検証中
> 作成日: 2026/05/06
> 最終更新: 2026/05/06
> ファイルパス: /Users/shogo/ObsidianVault/knowledge-vault/structured/articles/ai-news-publishing-workflow/20260506_ai-news-publishing-workflow.md

---

📋 プロジェクト概要
* カテゴリ: AIニュース運用 / Codex Skills / Astroコンテンツ運用
* 期間: 2026/05/06 -（検証中）
* 主要メンバー: shogo
* ステークホルダー: shogo-worksサイト読者、AI教材・AIニュース運用者
* プロジェクトステータス: 進行中

---

## 1. 背景と目的
* AIツールの公式アップデートを毎日追う必要があるが、手動リサーチだけでは漏れや整理コストが大きい。
* 公式情報を `docs/research` に蓄積し、そこから公開コンテンツへ落とし込む運用をCodex Skill化できるか検証した。
* 当初は「教材化」としてKnowledgeへ直接反映する想定だったが、GPT-5.5 Instantのような速報性の高い更新は、教科書型KnowledgeよりAIニュース記事に近いと判断した。
* 目的は、日次リサーチ、AIニュース化、Knowledge最小反映、バックログ化までを一言指示で回せる運用に近づけること。

---

## 2. 取り組み内容

### 実施した施策・活動
* `daily-ai-update-monitor` Skillを参照し、2026/05/06時点のAI公式アップデートを調査した。
* 対象はChatGPT/OpenAI、Gemini、Claude、Claude Code、GitHub Copilot、Genspark、Manus、Dify、n8n、Meta AI、Runway、xAI/Grok、ByteDance Seed、Pika。
* 調査結果を `docs/research/daily-ai-updates/2026-05-06.md` と各ツール別 `official-updates` に記録した。
* 当初作成した `ai-news-to-curriculum` Skillで、Knowledgeへの落とし込みを試した。
* ユーザーとの議論を経て、公開先を `src/content/knowledge/ai-tools` ではなく `src/content/ai-news` に寄せる方針へ修正した。
* Skillを `ai-news-publisher` として更新し、日次リサーチからAIニュース記事を作成し、Knowledgeには必要最小限だけ反映する役割へ変更した。
* 直前にKnowledgeへ作成したGPT-5.5 InstantとGemini Workspace管理の記事は削除し、AIニュース記事として作り直した。
* Claude金融サービス向けエージェントテンプレートは、Knowledge詳細追記ではなくAIニュース記事へ分離し、Knowledge側は設計思想の短い追記に戻した。

### 使用したツール・技術
* Codex
* Codex Skill / Claude Skill互換構成
* `daily-ai-update-monitor`
* `skill-creator`
* `ai-news-publisher`
* Astro Content Collections
* `src/content/ai-news`
* `src/content/knowledge/ai-tools`
* OpenAI / Google Workspace / Anthropic / GitHub / n8n 公式情報

### 主要な意思決定とその理由
* AIニュースとKnowledgeを分離する。
  * 理由: 最新情報を教科書型Knowledgeへ直接入れると、粒度が揺れ、教材の恒久性が落ちるため。
* `src/content/ai-news` を一次公開先にする。
  * 理由: 既に `aiNews` collection、一覧ページ、ツール別ページ、詳細ページが存在しており、速報記事の器として整っていたため。
* Knowledge更新は「既存教材の前提が古くなる箇所」に限定する。
  * 理由: モデル一覧、料金、トークン、使えるツール一覧、管理者設定など、長く参照される情報だけを残す方が運用品質が高い。
* Skill名を `ai-news-to-curriculum` から `ai-news-publisher` へ寄せる。
  * 理由: 実際の役割が教材化ではなく、AIニュース公開判断と公開処理に変わったため。

---

## 3. 進捗と成果

### 達成できたこと
* 日次AIニュースの公式リサーチを実行できた。
* 2026/05/06分の更新あり7件、更新なし9件を整理できた。
* `ai-news-publisher` Skillを作成し、AIニュース公開向けの判断基準・配置マップ・出力フォーマットを整備した。
* AIニュース記事を3本追加した。
  * `src/content/ai-news/chatgpt-openai/gpt-5-5-instant.mdx`
  * `src/content/ai-news/gemini/workspace-ai-control-center-meet-consent.mdx`
  * `src/content/ai-news/claude/finance-agents.mdx`
* Knowledgeへ直接作った記事を削除し、公開先をAIニュース側へ修正した。
* `npm run check` を実行し、0 errorsで通過した。

### 定量的な成果
* 調査対象: 16カテゴリ
* 更新あり: 7件
* 更新なし: 9件
* AIニュース反映: 3本
* Knowledge最小反映: 1本
* 検証結果: `npm run check` 0 errors

### 定性的な成果
* 「今日のAIニュース取ってきて」から「公開すべきニュースだけ記事化」までの動線が見えてきた。
* KnowledgeとAIニュースの役割が明確になった。
* 今後は「今日のリサーチして、AIニュース化して、Knowledge更新候補だけバックログに入れて」という一言指示に近づけられる見込み。

---

## 4. 学びとナレッジ

### うまくいったこと（Good）
* 既存サイトに `src/content/ai-news` が既に存在していたため、新規設計せずに運用導線へ接続できた。
* AIニュース記事のfrontmatterはKnowledgeより軽く、速報向けに扱いやすい。
* `relatedKnowledge` を使うことで、ニュース記事から既存教材への導線を作れる。
* Knowledge更新を最小化したことで、教材の教科書感を壊さずに済む。

### うまくいかなかったこと（Bad）
* 最初は「教材化」という言葉に引っ張られ、GPT-5.5 InstantやGemini Workspace管理をKnowledgeへ直接入れてしまった。
* 最新ニュースと恒久教材の粒度を分けないと、サイト内の情報設計が曖昧になる。
* `docs/research` は `.gitignore` 対象のため、実装成果として見えにくい。別途公開バックログや要約ログが必要。

### 改善ポイント（Improve）
* `ai-news-publisher` 実行時に、AIニュース記事化、Knowledge最小反映、保留、見送りを必ず表で出す。
* Knowledge更新候補は、その場で全部反映せず、バックログに残す運用を検討する。
* AIニュース一覧ページに、`candidate` / `promoted` の意味を運用上どう使うか決める。
* 日次リサーチからAIニュース記事作成までの一括Skillを作る場合、`daily-ai-update-monitor` と `ai-news-publisher` を順番に呼ぶ上位Skillにする。

### 技術的な発見・Tips
* Astro Content Collections側では `aiNews` collectionが既に定義されており、`tool` enumとfrontmatterを合わせれば追加しやすい。
* `npm run check` はsandbox内だとCloudflare Vite pluginの `listen EPERM 0.0.0.0:9229` で失敗することがある。権限付き再実行では成功した。
* AIニュースの本文は「何が変わったか」「影響」「教材化メモ」の3見出し程度が運用しやすい。

---

## 5. 課題と対応

### 発生した課題
* Knowledgeへ直接作った記事が、速報記事としては重すぎた。
* GPT-5.5 InstantやGemini Workspace管理のような更新は、教科書ページよりニュース記事の方が自然だった。
* Skill名と実態がずれていた。

### 対応方法
* `ai-news-to-curriculum` を `ai-news-publisher` に更新した。
* AIニュース公開マップ、選別基準、出力フォーマットをAIニュース基準に書き換えた。
* Knowledge新規記事2本を削除し、AIニュース記事へ移した。
* Claude Knowledge記事は、ニュース詳細を削除し、業務エージェント設計思想だけ残した。

### 未解決の課題
* バックログをどこに置くか未確定。
  * 候補: `docs/research/ai-news-editorial-backlog/YYYY-MM-DD.md`
* Knowledge最小反映専用Skillを別に作るか未確定。
  * 候補: `ai-news-to-knowledge-maintenance`
* 日次リサーチから公開までを一言で動かす上位Skillは未作成。

---

## 6. コストとリソース

### 人的リソース
* Codexによるリサーチ、Skill作成、MDX反映、検証。
* ユーザーによる公開先・情報設計の判断。

### 金銭的コスト
* 追加費用は未計測。
* Webリサーチ、Codex実行、OpenAI/Claude等の利用コストは通常利用範囲。

### コスト対効果
* 毎日の公式アップデート確認から公開候補整理までを半自動化できれば、手動調査・判断・記事化の工数削減が見込める。

---

## 7. 今後の展開

### 次のアクション
* AIニュース公開バックログの保存先とフォーマットを決める。
* `ai-news-publisher` を数回運用して、判定基準を調整する。
* Knowledge最小反映専用Skillを作るか判断する。
* 上位Skillとして「今日のAIニュースを調査して、公開記事化して、Knowledge候補をバックログへ入れる」を作る。

### 横展開の可能性
* AIニュースサイト運用
* Zenn / note / HP記事への展開
* 法人研修用の最新AI動向レポート生成
* SNS投稿生成

### 長期的な改善案
* 更新情報を「速報」「教材更新候補」「料金・モデル変更」「セキュリティ注意」「見送り」に分類する運用へ拡張する。
* `status: candidate` から `promoted` への昇格ルールを決め、一定期間後にKnowledgeへ反映するか判断する。
* RSS / GitHub release / 公式ブログの取得をスケジュール実行に寄せる。

---

📚 関連リソース

### 成果物・ドキュメント
* `docs/research/daily-ai-updates/2026-05-06.md`
* `.claude/skills/daily-ai-update-monitor/SKILL.md`
* `.claude/skills/ai-news-publisher/SKILL.md`
* `src/content/ai-news/chatgpt-openai/gpt-5-5-instant.mdx`
* `src/content/ai-news/gemini/workspace-ai-control-center-meet-consent.mdx`
* `src/content/ai-news/claude/finance-agents.mdx`
* `src/content/knowledge/ai-tools/claude/agent-skills.mdx`

### 参考資料
* OpenAI GPT-5.5 Instant: https://openai.com/index/gpt-5-5-instant/
* OpenAI GPT-5.5 Instant System Card: https://openai.com/index/gpt-5-5-instant-system-card/
* Google Workspace AI control center: https://workspaceupdates.googleblog.com/2026/05/securely-manage-AI-and-agent-access-to-Workspace-data-with-the-AI-control-center.html
* Google Meet explicit consent: https://workspaceupdates.googleblog.com/2026/04/require-explicit-consent-for-take-notes-with-Gemini-recordings-and-transcripts-in-Google-Meet.html
* Anthropic finance agents: https://www.anthropic.com/news/finance-agents
* Claude Code v2.1.129: https://github.com/anthropics/claude-code/releases/tag/v2.1.129
* n8n v2.20.0: https://github.com/n8n-io/n8n/releases/tag/n8n%402.20.0

### 関連プロジェクト
* shogo-works personal site
* AIニュース運用
* AI教材更新運用

---

✅ メモ・雑記
* 「教材化」という言葉は、AIニュース記事化とKnowledge恒久反映に分けた方がよい。
* 速報はAIニュースへ、教科書的に残す情報はKnowledgeへ、という分離が今後の基本方針。
* バックログは「やることリスト」ではなく、Knowledgeへ昇格するかを後で判断するための編集判断ログとして扱う。

---

## 📝 更新ログ
<!-- このセクションはスキルが自動で追記する。手動編集不要。 -->
| 日時 | 更新内容の概要 |
|---|---|
| 2026/05/06 | ファイル作成（AIニュース収集・公開フロー検証ログ） |
