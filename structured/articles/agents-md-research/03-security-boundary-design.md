# セキュリティ・境界設計 — AI が踏み越えてはいけない線の表現方法

AI エージェントは指示が曖昧だと暴走しがちで、しかも「動くコード」を作るために最短経路を取ろうとする傾向がある。このため、コードベース側で **「ここから先は絶対に踏み越えるな」** という境界を明示する記述が、2025-2026 年の AGENTS.md / CLAUDE.md で急速に発達している。

本記事では Airflow・Next.js・Activepieces・Directus・Dify・n8n の 6 例を題材に、AI が侵してはいけない境界を表現する方法を 5 つの分類で整理する。

## 分類 A: アーキテクチャ境界

「このコンポーネントはこの責任を絶対に持たない」という設計上の不変条件をエージェントに伝える。

### A1: Apache Airflow — 「Scheduler はユーザーコードを実行しない」

引用元: [apache/airflow AGENTS.md](https://raw.githubusercontent.com/apache/airflow/main/AGENTS.md)

Airflow の AGENTS.md には以下のような明示的記述がある:

> Architecture Boundaries（Scheduler / Worker / API Server の責務境界）
> Scheduler は絶対にユーザーコードを実行しない。

これは Airflow のセキュリティモデルそのもの — Scheduler が DAG ファイルから任意コードを実行すると Worker と権限境界が壊れる — を AI に教えるための記述。AI は「動かすために」境界を踏み越えがちなので、明示しておかないとリスクがある。

### A2: Next.js — DCE / エッジ vs Node ランタイム境界

引用元: [vercel/next.js AGENTS.md](https://raw.githubusercontent.com/vercel/next.js/canary/AGENTS.md)

- DCE（Dead Code Elimination）の境界: `define-env.ts`、`entry-base.ts` の役割を AI に明示
- エッジランタイムと Node ランタイムの境界: 両者で動作する API の差異
- `NEXT_SKIP_ISOLATE=1` の落とし穴

### 観点抽出

- アーキテクチャ境界はコードを読むだけでは見えにくい（「あえて書かない」設計判断は痕跡が残らない）。AI 設定ファイルで明示することの意義が大きい。
- 「絶対に〜しない」という否定形での宣言が効果的。肯定形（「〜する」）よりも境界として機能する。

## 分類 B: エディション境界（CE/EE/Cloud）

OSS のオープンコア型ビジネスモデルでは、CE（Community Edition）と EE（Enterprise Edition）でコードが分離される。AI は意図せず EE コードを CE に import してしまいがちなので、明示が必要。

### B1: Activepieces — `src/app/ee/` import 禁止

引用元: [activepieces/activepieces AGENTS.md](https://raw.githubusercontent.com/activepieces/activepieces/main/AGENTS.md)

> CE コードに `src/app/ee/` を絶対 import しない

これに加え、エディション分岐のテストパターン、ライセンスチェックの位置などが詳細に記述されている。

### 観点抽出

- エディション境界はビジネス上の理由（ライセンス・課金）で存在するため、技術的には自由に行き来できてしまう。AI 視点では「使えるなら使う」になりがちで、明示的な禁止指示が必要。
- 違反検出のための ESLint ルールや CI チェックも併設するのが理想。

## 分類 C: 入出力境界（SSRF / インジェクション対策）

外部からの入力・外部への出力を扱う境界。AI が標準ライブラリ（`axios`、`fetch`）を直接使ってしまうと SSRF 等の脆弱性を生む。

### C1: Activepieces — `safeHttp.axios` 強制

引用元: [activepieces/activepieces AGENTS.md](https://raw.githubusercontent.com/activepieces/activepieces/main/AGENTS.md)

サーバーパッケージからの外部 HTTP には標準 axios ではなく `safeHttp.axios` を使うよう指示。プライベート IP（10.x.x.x、169.254.x.x、127.x.x.x 等）へのリクエストをブロックする SSRF 対策ラッパー。

### C2: Dify — SQLAlchemy で `tenant_id` スコープ必須

引用元: [langgenius/dify api/AGENTS.md](https://raw.githubusercontent.com/langgenius/dify/main/api/AGENTS.md)

> SQLAlchemy 操作では必ず `tenant_id` でクエリをスコープする
> 生 SQL の使用禁止

マルチテナント SaaS で AI が「便利だから」と他テナントのデータに横断クエリを書いてしまうリスクへの対策。

### 観点抽出

- AI は標準 API を使いがち。**「標準より独自ラッパーを使え」** という指示は明示的に書く必要がある。
- 入出力境界は脆弱性に直結するため、規約の遵守を **CI レベルで強制**（ESLint カスタムルール、grep ベース禁止チェック等）するのが望ましい。Activepieces はこの両輪。

## 分類 D: 自律性境界（ガバナンス）

AI エージェントの自律的な行動範囲を制限する。「人間の介在を必須とする操作」を明文化する。

### D1: Directus — `ai_policy.md` で「完全自律 PR 禁止」

引用元: [directus/directus ai_policy.md](https://raw.githubusercontent.com/directus/directus/main/ai_policy.md)

技術仕様（AGENTS.md）と独立した **ガバナンスポリシーファイル** として `ai_policy.md` を設置。

> The policy explicitly prohibits 'fully autonomous agents' from creating issues, pull requests, or contributions without human involvement.

加えて AGENTS.md に **「🤖🤖🤖 を含む Issue/PR は優先処理される」** という Bonus セクションも設置 — AI 発のコントリビューションを識別するシグナル。

### D2: Apache Airflow — `Drafted-by:` フッター義務化

引用元: [apache/airflow AGENTS.md](https://raw.githubusercontent.com/apache/airflow/main/AGENTS.md)

エージェントが作成した GitHub メッセージには `Drafted-by: <Agent Name and Version>` フッター義務化。人間レビューの有無も明記する。

### D3: Dify — `--no-verify` 物理ブロック

引用元: [langgenius/dify .claude/settings.json](https://github.com/langgenius/dify/blob/main/.claude/settings.json)

Claude Code の `PreToolUse` フックで `npx -y block-no-verify@1.1.1` を実行。`git push --no-verify` をシステムレベルでブロックし、AI が「テストが通らないなら飛ばす」を物理的にできなくする。

### 観点抽出

- 自律性境界は **規約レベルだけでなく、フック・CI・ファイル分離** など多層で実装されている。
- AI 出力をリポジトリ上で識別可能にする（`Drafted-by:` フッター、🤖 マーカー）ことで、人間レビュアーが差別的な確認を入れられる。
- 技術仕様（AGENTS.md）とガバナンス（ai_policy.md）の **ファイル分離** は、両者の更新責任が異なる（前者は開発者、後者はメンテナ・法務）ことを反映した賢い設計。

## 分類 E: コミュニケーション境界（情報開示・タイトル規則）

OSS では Issue・PR・コミットメッセージが公開される。セキュリティ修正で攻撃ベクターを露出すると、修正前のバージョンを使っているユーザーが攻撃される。

### E1: n8n — セキュリティ修正の中立的タイトル規則

引用元: [n8n AGENTS.md](https://raw.githubusercontent.com/n8n-io/n8n/master/AGENTS.md)

セキュリティ修正時のブランチ名・コミットメッセージ・テスト記述・コードコメントすべてについて「攻撃ベクターを一切露出しない」ルール。具体例:

- ブランチ名: `fix/auth-edge-case`（×: `fix/auth-bypass-via-jwt-replay`）
- PR タイトル: 中立的表現
- テストコメント: 攻撃の再現方法を直接書かない

### E2: Apache Airflow — AI 生成コードのレッドフラグ検出

引用元: [apache/airflow code-review.instructions.md](https://raw.githubusercontent.com/apache/airflow/main/.github/instructions/code-review.instructions.md)

レビュアー指示として AI 生成 PR の **レッドフラグリスト** を文書化:

- fabricated diffs（実在しない API への参照）
- unrelated file changes（無関係ファイルの変更）
- empty descriptions（空の PR 説明）
- ライブラリバージョンの幻覚

逆説的だが、AI 設定ファイル内に「AI 生成成果物への警戒項目」が書かれている点が 2026 年的。

### E3: Next.js — `<!-- NEXT_JS_LLM_PR -->` マーカー

引用元: [vercel/next.js AGENTS.md](https://raw.githubusercontent.com/vercel/next.js/canary/AGENTS.md)

PR 末尾に `<!-- NEXT_JS_LLM_PR -->` HTML コメント挿入を義務化。CI/分類に活用される。

### 観点抽出

- セキュリティ修正の情報開示制御は OSS 特有の問題で、**AI が「丁寧に書こう」として攻撃ベクターを書き出してしまう** リスクへの対策。
- AI 生成 PR を識別可能にすることで、レビュアー側のチェックリストを変えられる（fabrication 検査の重点化など）。

## 横断的考察

### 1. 境界記述は否定形が効く

「〜してはいけない」「〜は禁止」という否定形のほうが、肯定形より明確に境界として機能する。AI は肯定形だと「他の方法もある」と解釈しがちなため。

### 2. 多層防御が標準化しつつある

単に AGENTS.md に書くだけでは AI が無視する可能性があるため、複数レイヤーで境界を実装する事例が増えている:

| 層 | 例 |
|---|---|
| ドキュメント層 | AGENTS.md / ai_policy.md の記述 |
| ツール層 | `safeHttp.axios` などのラッパー |
| フック層 | Claude Code `PreToolUse` フックでブロック |
| CI 層 | ESLint カスタムルール、Layering check |
| レビュー層 | AI 生成コードのレッドフラグリスト |
| プロセス層 | `Drafted-by:` フッター義務、🤖 マーカー |

### 3. 「AI 用ファイルが AI 警戒項目を含む」という逆説

Airflow の事例が象徴的だが、AI エージェント設定ファイルが「AI 生成成果物にどう警戒するか」も同居させる流れが出てきている。これは 2026 年現在の業界が **AI を強力なツールとして利用しつつ、そのリスクも前提化する成熟段階** に入っていることを示す。

### 4. ガバナンスの独立ファイル化

Directus の `ai_policy.md` は技術仕様とガバナンスポリシーを分離している。これは更新責任の違いを反映した設計で、AI 関連政策が法務・コンプライアンス文書としても扱われる流れの先取り。

### 5. 公開リポジトリ特有の制約への対応

n8n のセキュリティ修正中立化ルールは、**OSS だからこそ必要** な記述。プライベートリポジトリでは不要だが、OSS では「修正情報が逆に攻撃の手がかりになる」リスクがある。

## 引用元一覧

- [n8n AGENTS.md](https://raw.githubusercontent.com/n8n-io/n8n/master/AGENTS.md)
- [Apache Airflow AGENTS.md](https://raw.githubusercontent.com/apache/airflow/main/AGENTS.md)
- [Apache Airflow code-review.instructions.md](https://raw.githubusercontent.com/apache/airflow/main/.github/instructions/code-review.instructions.md)
- [vercel/next.js AGENTS.md](https://raw.githubusercontent.com/vercel/next.js/canary/AGENTS.md)
- [activepieces AGENTS.md](https://raw.githubusercontent.com/activepieces/activepieces/main/AGENTS.md)
- [Directus ai_policy.md](https://raw.githubusercontent.com/directus/directus/main/ai_policy.md)
- [Directus AGENTS.md](https://raw.githubusercontent.com/directus/directus/main/AGENTS.md)
- [Dify api/AGENTS.md](https://raw.githubusercontent.com/langgenius/dify/main/api/AGENTS.md)
- [Dify .claude/settings.json](https://github.com/langgenius/dify/blob/main/.claude/settings.json)
