# Computer Use / Browser Use / ローカルLLM系エージェント 調査ログ

> ステータス: 進行中
> 作成日: 2026/06/01
> 最終更新: 2026/06/01
> ファイルパス: /Users/shogo/Documents/ai-business-os/15_ナレッジ基盤/vault/structured/projects/20260601_computer-use-browser-use-local-llm-survey.md

---

📋 プロジェクト概要
* カテゴリ: AI Agent / GUI Automation リサーチ
* 期間: 2026/06/01 -（検証中）
* 主要メンバー: 田中翔吾
* ステークホルダー: （情報なし）
* プロジェクトステータス: 進行中

---

## 1. 背景と目的

* AIエージェント運用の主流となる自動化レイヤ（API / MCP / DOM操作 / CLI / GUI）のうち、どの順序で組み合わせるとコストと安定性のバランスが取れるかを整理する
* Computer Use系のGUIエージェントは汎用に見えるが、コストとトークン消費が高く長期タスクで失敗率が上がるため、GUIに依存しすぎない構成を設計したい
* 自身の主要用途（Make / Dify / Discord / GA4 / GitHub / Next.js / VSCode / Figma）を前提に、Browser Use・ローカルLLM・OmniParser・Agent S2 系の選択肢を比較し、推奨スタックを確定させる
* 優先順位の指針として API → MCP → DOM操作 → CLI → GUI操作 の階層を採用し、GUIは最後の手段として位置付ける

---

## 2. 取り組み内容

### 実施した施策・活動

* Browser Use 系（Playwright / Chrome DevTools Protocol 経由のDOM操作）と Computer Use 系（スクリーンショット＋VLM解析ループ）のアーキテクチャ差分を整理した
* ローカルLLM 用ランタイムとして Ollama を中心に、GUI 認識に強いマルチモーダルモデル（Qwen2.5-VL、CogAgent）の位置付けを調査した
* GUIエージェント OSS（Open Computer Use、Open Interpreter、Microsoft OmniParser / OmniTool）を一覧化し、それぞれの守備範囲を比較した
* 研究系最新動向として Agent S2 の Planner / Executor / Grounding 分離アーキテクチャを確認した

### 使用したツール・技術

* Browser Use 基盤: Playwright、Chrome DevTools Protocol、MCP
* クラウドGUIエージェント: Claude Computer Use、Codex Computer Use
* ローカルLLMランタイム: Ollama（事実上の標準）
* GUI理解に強いローカルVLM:
  * Qwen2.5-VL — GUI理解・テキスト認識・ボタン認識が強く Computer Use 用途で有力
  * CogAgent — GUI専用寄りのVLMで高解像度UI認識を重視
* GUIエージェントOSS:
  * Open Computer Use — Ollama ＋ PyAutoGUI ＋ スクショ解析。完全ローカルでマウス・キーボード制御まで対応
  * Open Interpreter — GUIとCLIを横断する実運用寄り構成。例: ファイル整理は Python、変換処理は CLI、必要時のみGUI
* Microsoft 系:
  * OmniParser — スクリーンショットからボタン・入力欄・アイコンといったUI要素を抽出し構造化するパーサー
  * OmniTool — OmniParser に任意のLLM（OpenAI / Anthropic / Qwen 等）を組み合わせて利用する構成
* 研究系: Agent S2（Planner / Executor / Grounding を分離するコンポジショナルなフレームワーク）

### 主要な意思決定とその理由

* GUIは万能に見えるが UI 変更耐性が低くトークン消費も大きいため、GUIでしかできない処理に限定する方針を採る
* DOM が存在する操作対象（GA4 / Make / Dify / GitHub / Discord Web / Slack Web / Google Workspace 等）は Browser Use ＋ Playwright ＋ MCP に寄せる
* DOM が存在しないネイティブアプリ（VSCode / Figma Desktop / Finder / Excel Desktop / Photoshop / Discord Desktop など）に限り Computer Use を許容する
* ローカルでの GUI 操作は Ollama ＋ Qwen2.5-VL ＋ Open Interpreter を起点に検証する

---

## 3. 進捗と成果

### 達成できたこと

* GUI自動化スタックの優先順位を API → MCP → DOM操作 → CLI → GUI操作 という階層で言語化できた
* Browser Use と Computer Use のコスト構造の差（DOM直叩き vs スクショ＋VLM解析ループ）を整理した
* ローカルLLM / クラウドLLM / OSS / 研究フレームワークを役割別にマッピングし、自分の用途に当てはめた推奨構成を確定させた

### 定量的な成果

* （情報なし）

### 定性的な成果

* GUIエージェントは画面を動画的に見ているのではなく、大量の静止画を反復解析しているという理解が共有された
* 「GUI操作回数 ≒ トークン消費量」というメンタルモデルを確立し、設計時の判断軸として使えるようにした
* 推奨ターゲット比率として Browser Use 90% / CLI 5% / Computer Use 5%、もしくはローカル実行 95% ＋ 高性能クラウドGUIエージェント 5% という目安を持てた

---

## 4. 学びとナレッジ

### うまくいったこと（Good）

* Browser Use 系（Playwright / CDP 経由）は `document.querySelector()` や `button.click()` 相当でHTML構造を直接操作するため、高速かつ安定し低コストになる
* DOM 完結する SaaS（GA4 / Make / Dify / GitHub / Discord Web / Slack Web / Google Workspace）では Browser Use ＋ Playwright ＋ MCP の構成が機能する見込みが立った
* Open Interpreter のように GUI と CLI を組み合わせる設計は、ファイル整理を Python、変換処理を CLI、必要時のみ GUI、と役割を切り分けて実運用に乗せやすい

### うまくいかなかったこと（Bad）

* Computer Use はスクリーンショット取得 → LLM 解析 → 次アクション決定のループを毎ステップ繰り返すため、GUI 操作回数がそのままトークン消費量に直結する
* ローカルLLMでも Computer Use は可能だが、精度は Claude > GPT 系 > ローカル の順で、現状はクラウドの大型モデルと同水準の精度には届かない

### 改善ポイント（Improve）

* 事前に画面を準備する: Discord なら投稿対象チャンネルを開いた状態で渡し、エージェントには投稿だけを担当させる
* タスクを分割する: Slack確認 / Issue作成 / 修正、のように1ステップ完結のタスクへ分けてからエージェントに渡す
* GUI探索を減らす: Finder でフォルダを辿らせず、Spotlight でファイル名を入力して Enter させるなど、キーボードショートカットを優先する

### 技術的な発見・Tips

* Computer Use の高コスト要因は、スクリーンショット解析を毎ターン挟むループ構造そのものにある
* OmniParser はスクリーンショットを UI 要素単位に構造化し、後段の LLM がボタン・入力欄・アイコンを認識しやすくする前処理として機能する
* Agent S2 は Planner と Executor、さらに Grounding を分離し、大型モデルが計画、小型モデルがクリック判定を担う構成で、精度向上とコスト削減を両立している
* 従来の「画面全部を毎回 LLM へ送る」運用から、OmniParser で UI を構造化し、小型モデルが実行、必要時のみ大型モデルへエスカレーション、という構成への移行が進みつつある

---

## 5. 課題と対応

### 発生した課題

* GUI 操作中心の構成は UI 変更に弱く、長期タスクで失敗率が上がる
* スクリーンショット解析を繰り返す Computer Use はトークン消費が線形以上に膨らみやすい

### 対応方法

* DOM が存在する対象は Browser Use 系（Playwright / MCP）に寄せ、Computer Use はネイティブアプリ限定で利用する
* タスクを単位化し、エージェントに渡す前に対象画面を準備しておくことで GUI ループを最小化する
* 履歴圧縮・セマンティック要約・GUI 構造化を組み合わせ、毎ターンの送信量を抑制する

### 未解決の課題

* ローカルLLMでの Computer Use の精度がクラウド大型モデルにどこまで近づくかは継続検証が必要
* 実際の運用比率（Browser Use 90% / CLI 5% / Computer Use 5%）が手元の業務でも成立するかの実測

---

## 6. コストとリソース

### 人的リソース

* （情報なし）

### 金銭的コスト

* （情報なし）

### コスト対効果

* （完了時に記入）

---

## 7. 今後の展開

### 次のアクション

* 推奨スタックの実証として Ollama ＋ Qwen2.5-VL ＋ Open Interpreter を手元にセットアップする
* DOM完結タスクは Browser Use ＋ Playwright ＋ MCP で実装し、GUI が必須なケースだけ Claude Computer Use または Codex Computer Use にフォールバックする運用ルールを定める
* 利用シナリオ別の振り分け方針を以下で運用する
  * GitHub → Browser Use
  * GA4 → MCP
  * Discord 通知 → API
  * Next.js 起動 → CLI
  * VSCode 編集 → Computer Use
* 理想構成の目安は Browser Use 90% / CLI 5% / Computer Use 5%、またはローカル実行 95% ＋ 高性能クラウドGUIエージェント 5%

### 横展開の可能性

* （要記入）

### 長期的な改善案

* OmniParser で UI を構造化し、小型モデルが実行、必要時のみ大型モデルを呼び出す段階的エスカレーション構成へ移行する
* 履歴圧縮・セマンティック要約・GUI 構造化を組み合わせ、長期タスクでも送信量が破綻しないパイプラインを整える

---

📚 関連リソース

### 成果物・ドキュメント

* （随時更新）

### 参考資料

* [Ollama](https://ollama.com)
* [Open Interpreter — GitHub](https://github.com/OpenInterpreter/open-interpreter)
* [OmniParser — GitHub](https://github.com/microsoft/OmniParser)
* [Agent S — GitHub](https://github.com/simular-ai/Agent-S)
* [Open Computer Use — GitHub](https://github.com/Clad3815/open-computer-use)
* Agent S2: A Compositional Generalist-Specialist Framework for Computer Use Agents — arXiv:2504.00906
* CogAgent: A Visual Language Model for GUI Agents — arXiv:2312.08914
* OmniParser for Pure Vision Based GUI Agent — arXiv:2408.00203
* SecAgent: Efficient Mobile GUI Agent with Semantic Context — arXiv:2603.08533

### 関連プロジェクト

* （随時更新）

---

✅ メモ・雑記

* ローカルLLMでの GUI 操作は近年急速に発展しているが、精度では Claude が依然優位。コストはローカルが圧倒的に安いため、用途に応じた使い分けが鍵
* Ollama はローカルLLM運用の事実上の標準として扱える
* Computer Use を入れる場合でも、まず Open Interpreter のような GUI ＋ CLI のハイブリッドから入ると理解が進みやすい

---

## 📝 更新ログ
<!-- このセクションはスキルが自動で追記する。手動編集不要。 -->
| 日時 | 更新内容の概要 |
|---|---|
| 2026/06/01 | ファイル作成（init）— ユーザー提示の調査まとめを各セクションへ反映 |
