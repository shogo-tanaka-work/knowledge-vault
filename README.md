# Knowledge Vault — ナレッジ蓄積・記事管理の中央リポジトリ

学んだことを構造化ナレッジとして蓄積し、Note・YouTube・HP等のメディアに横展開する仕組み。
**記事・コンテンツ制作の全体管理はこのリポジトリが起点になる。**

## このリポジトリの役割

1. **ナレッジの原本管理** — 検証ログ・記事原稿はすべて `structured/` に集約
2. **メディア横展開** — スキルで Note/YouTube/HP 等に変換し `outputs/` に出力
3. **他プロジェクトとの連携** — 各プロジェクトからはシンボリックリンクで参照

```
他プロジェクト（MCPServer/mcp-google-ads 等）
    └── docs/note/
        └── 01-xxx.md  →  symlink  →  このリポジトリの structured/articles/ を参照
```

つまり、どのプロジェクトで作業していても、**記事の原本は常にここに存在する**。

---

## ディレクトリ構成

```
knowledge-vault/
├── raw/                       ← 音声メモの生データ（Amical文字起こし等）
│   └── voice-memo-buffer.md
│
├── structured/                ← 全コンテンツの原本（シングルソース）
│   ├── tools/                 ← ツール単位の検証ログ
│   │   └── 20260405_claude-code-hp-development.md
│   ├── projects/              ← PJ単位の検証ログ
│   │   └── 20260331_n8n-automation.md
│   └── articles/              ← 記事原稿（テーマ別サブディレクトリ）
│       └── google-ads-mcp/
│           ├── 01-motivation-and-auth.md
│           ├── 02-local-mcp-server.md
│           └── 03-remote-mcp-server.md
│
├── outputs/                   ← メディア別変換済み成果物
│   ├── note/
│   │   └── INDEX.md           ← ダッシュボード（全記事のステータス一覧）
│   ├── youtube/
│   ├── udemy/
│   ├── sns/
│   └── hp/
│
└── .claude/skills/            ← プロジェクトローカルスキル
    └── knowledge-transform/
```

---

## データフロー

```
 話す（Amical）→ raw/ に生データ蓄積
                    ↓
           「ログ更新して」（ai-verification-log スキル）
                    ↓
           structured/ に構造化ナレッジとして蓄積
            ├── tools/      検証ログ
            ├── projects/   PJログ
            └── articles/   記事原稿
                    ↓
           「Note記事にして」（publish コマンド）
                    ↓
           outputs/note/INDEX.md にエントリ追加
           プロジェクト側に symlink 作成
```

---

## 使い方

### 検証ログの蓄積（init → update → finalize）

```bash
# 1. 検証開始
ログ作成して

# 2. 都度メモを追記
pbpasteの内容でログ更新して

# 3. 検証完了
ログ完成させて
```

### 記事の作成（publish）

```bash
# 検証ログから記事化
structured/tools/20260405_claude-code.md をNote記事にして

# 直接記事を作成（任意のプロジェクトで）
この内容をNote記事にして

# 全メディアに一括展開
このログを全メディアに展開して
```

**publishが自動でやること:**
1. `structured/articles/[テーマ]/` に原本ファイルを作成（フロントマター付き）
2. 元プロジェクトの `docs/note/` にシンボリックリンクを作成
3. `outputs/note/INDEX.md` にエントリを追加

### メディア横展開（knowledge-transform スキル）

```bash
# 個別メディア
structured/tools/20260405_amical.md をNote記事にして
structured/tools/20260405_amical.md をYouTube台本にして
structured/tools/20260405_amical.md をSNS投稿にして

# 一括
structured/tools/20260405_amical.md を全メディアに展開して
```

成果物は `outputs/[メディア]/` に保存される。

---

## 記事のステータス管理

各記事のフロントマターで `status` を管理する。ダッシュボードは `outputs/note/INDEX.md`。

```yaml
---
title: "記事タイトル"
status: draft          # draft → review → ready → published
media: note
series: "シリーズ名"
source_project: "MCPServer/mcp-google-ads-remote"
published_url: ""      # 公開後にURLを記入
---
```

| ステータス | 意味 |
|:---:|:---|
| `draft` | 執筆中 |
| `review` | 推敲中 |
| `ready` | 公開準備完了 |
| `published` | 公開済み |
| `archived` | 廃止・統合済み |

---

## 他プロジェクトとの関係

各プロジェクト内で作った記事・ドキュメントは、このリポジトリの `structured/articles/` に原本を配置する。プロジェクト側には**シンボリックリンクのみ**を置く。

```
MCPServer/mcp-google-ads-remote/docs/note/
  └── 01-motivation-and-auth.md → symlink → knowledge-vault/structured/articles/google-ads-mcp/...

MCPServer/mcp-discord/docs/note/
  └── invoice-mcp.md → symlink → knowledge-vault/structured/articles/invoice-mcp/...
```

**なぜこうするのか:**
- 「記事どこ？」→ 常に `structured/articles/` を見ればいい
- ステータスが一覧で把握できる（`outputs/note/INDEX.md`）
- プロジェクト間で散在しない

---

## 使用スキル

| スキル | 場所 | 用途 |
|---|---|---|
| ai-verification-log | `~/.claude/skills/`（グローバル） | 検証ログの蓄積 + 記事化（publish） |
| knowledge-transform | `.claude/skills/`（ローカル） | 構造化ナレッジ → メディア別変換 |

---

## ファイル命名規則

- 検証ログ: `YYYYMMDD_[テーマ名].md`（例: `20260405_amical.md`）
- 記事原稿: `[連番]-[slug].md`（シリーズ）or `[slug].md`（単発）
- テーマディレクトリ: 英語kebab-case（例: `google-ads-mcp`）

---

## 関連

- Linear: [SHO-133](https://linear.app/shogoworks/issue/SHO-133) — AIツール最新情報の収集→検証→ナレッジ発信パイプライン構築
