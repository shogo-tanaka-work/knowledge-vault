# CLAUDE.md - knowledge-vault

このディレクトリはObsidian保管庫 兼 Git管理されたナレッジリポジトリです。
Claude Codeはこのディレクトリのmarkdownファイルを直接読み書きできます。

## 構造

- `raw/`               : 音声メモバッファ（Amical → voice-memo-buffer.md に蓄積）
- `structured/tools/`  : ツール単位の検証ログ（YYYYMMDD_*.md 形式）
- `structured/articles/` : 記事原稿（テーマ別フォルダ）
- `outputs/`           : メディア別成果物（note / youtube / udemy / sns / hp）

## データフロー

```
話す（Amical）
    ↓
raw/voice-memo-buffer.md に生データ蓄積
    ↓
ai-verification-log スキルで structured/ に構造化
    ↓
knowledge-transform スキルで outputs/ の各メディア向けに展開
```

## スキル

- `ai-verification-log`  : グローバルスキル（検証ログの作成・更新）
- `knowledge-transform`  : ローカルスキル（`.claude/skills/knowledge-transform/`）

## 規約

- markdownファイルは自由に編集してよい
- コミットは obsidian-git（自動）または Claude Code の git 操作で行う
- `.obsidian/workspace.json` は編集・コミットしない（gitignore済み）
- `structured/projects/` 配下は `.gitignore` で除外（機密情報を含む場合がある）
