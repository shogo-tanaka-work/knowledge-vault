---
name: slide-design-patterns
description: ビジネス向けパワポ・スライド作成の依頼時に「パワポ研」由来のスライドパターン辞書を参照して、テーマ別の構成・配色・図解パターンを提案するスキル。「比較スライド」「事業紹介」「ロードマップ」「KPIツリー」「概念図」「会社概要」「エグゼクティブサマリー」「TAM SAM SOM」「資金調達ピッチ」「事業ポートフォリオ」「ファネル」「マトリックス」「サンバースト」「ウォーターフォール」「フローチャート」「ピラミッド」「循環図」「タイムライン」「市場シェア」「参入障壁」「MVV（ミッション・ビジョン・バリュー）」「表紙スライド」「ディバイダー」「青色系プレゼン」「コンサルっぽい資料」「IR資料風」「ピッチデック」「営業資料デザイン」などのキーワードで必ず発動すること。スライド生成自体は majin-slide-pptx / navy-blue-pptx 等の既存スキルに委譲し、本スキルはパターン辞書（構成例・配色・代表参考スライド）を提供する側として動く。
---

# slide-design-patterns

note アカウント [パワポ研](https://note.com/powerpoint_jp) の人気記事78本＋著者キュレーション「テーマ別スライド集」「プロフェッショナルファームの資料」から抽出したスライドパターン辞書を参照するスキル。

## 何ができるか

「比較スライド作って」「事業ポートフォリオを1枚で」「資金調達ピッチの構成」といった依頼に対して、**パワポ研流の鉄板構成・代表参考事例・配色パターン**を提示する。

## 動き方

1. **辞書を開く**: `references/patterns.md` を Read して、依頼内容に該当するテーマを「依頼ワード逆引き」テーブルで特定する
2. **代表記事を引く**: 該当エントリの `key`（例 `nf57434bd50ee`）を頼りに `references/articles/{key}_*.md` を Read して、具体的な構成例・引用元IR資料・スライド評を取得
3. **画像を確認**: 必要なら `references/images/{key}_*/` 配下の画像を見て、ユーザーに参考画像のパスを案内する
4. **構成案を提示**: 抽出した構成・配色・図解パターンを、ユーザーの題材に当てはめた具体案として返す
5. **生成への橋渡し**: 実際の `.pptx` 生成が必要なら `majin-slide-pptx` / `navy-blue-pptx` / `navy-blue-pptx-json` 等の生成系スキルに引き継ぐ

## 参照規約

- **絶対パス禁止**。本スキルディレクトリからの相対パス（`references/...`）のみ使用する
- `references/` 配下は symlink。Vault ルート以下の `structured/projects/powerpoint_jp_research/` 本体を指す
- 出典（note 原文 URL）は提案に必ず併記する。各記事 markdown の frontmatter `url` フィールドを使う
- 画像・本文は **個人研究用ローカル保管**。ユーザーが第三者に共有・再配布する用途では使わない

## 既存スキルとの連携

| 役割 | スキル |
|---|---|
| **本スキル**: パターン辞書・構成提案 | slide-design-patterns（このスキル） |
| まじん式テンプレでPPTX生成 | majin-slide-pptx |
| ネイビーブルー系テンプレで生成 | navy-blue-pptx / navy-blue-pptx-json |

「依頼内容を整理 → パターン辞書で構成決め → 既存生成スキルで .pptx 出力」という流れを基本動作とする。

## メンテナンス

### symlink の再構築（プロジェクト移動時）

`structured/projects/powerpoint_jp_research/` を別パスに移動した場合は、本スキルの `references/` 配下の symlink を貼り直す:

```bash
SKILL_DIR=".claude/skills/slide-design-patterns/references"
# references/ から見た相対パス。Vault ルート (knowledge-vault/) までは ../../../.. の4階層
PROJECT_REL="../../../../structured/projects/powerpoint_jp_research"  # 移動後の相対パスに合わせて変更

cd "$SKILL_DIR"
ln -sfn "$PROJECT_REL/patterns/slide_patterns.md" patterns.md
ln -sfn "$PROJECT_REL/articles" articles
ln -sfn "$PROJECT_REL/images" images
ln -sfn "$PROJECT_REL/README.md" project_readme.md
```

### 記事の追加取得

パワポ研の note に新記事が出たときは、`structured/projects/powerpoint_jp_research/README.md` の「更新方法」節に記載した手順で差分取得し、`patterns/slide_patterns.md` に追記する。symlink は変更不要。
