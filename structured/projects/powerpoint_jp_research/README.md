# パワポ研 note 記事リサーチ プロジェクト

note アカウント [パワポ研 (@powerpoint_jp)](https://note.com/powerpoint_jp) の公開記事を、ビジネス向けパワポ作成エージェントスキルの情報源として整理したもの。

## 取得日
2026-05-06

## ライセンス・注意

- **個人研究用ローカル保管**。再配布・公開を禁ずる
- 本文・画像の著作権は note 投稿者（パワポ研）に帰属
- スキル経由で参照する際も、原典 URL（各記事 frontmatter の `url`）を併記する

## 統計

| 項目 | 件数 |
|---|---|
| 公開記事総数（クリエイター API） | 90 |
| 厳選マガジン「テーマ別スライド集」 | 51 |
| 「資料作成術」マガジン | 160（重複含む） |
| 「サイト・ツール」マガジン | 47 |
| 「プロフェッショナルファームの資料」マガジン | 15 |
| **収集対象（人気上位30 + 厳選51 + プロファーム15、重複除外）** | **78** |
| ダウンロード画像枚数 | 1,631 |
| 画像合計サイズ | 約 186MB |

## ディレクトリ構成

```
powerpoint_jp_research/
├── README.md                # 本ファイル
├── metadata/
│   ├── all_articles.json    # 全記事のメタ情報統合（target_urlsを含む）
│   ├── target_articles.json # 収集対象78件のメタ
│   ├── image_map.json       # 記事key→画像URL一覧
│   ├── creator_p*.json      # creators API レスポンス（page1-15）
│   ├── mag_*.json           # 各マガジンの notes API レスポンス
│   ├── articles_raw/*.json  # 個別記事 API レスポンス（HTML本文を含む）
│   ├── build_articles.py    # JSON → markdown 変換スクリプト
│   └── download_images.py   # 画像並列ダウンローダ
├── articles/                # 78記事の markdown（frontmatter + 本文 + 画像参照）
├── images/                  # 記事ごとの画像（{key}_{slug}/ 配下）
└── patterns/
    └── slide_patterns.md    # スライドパターン辞書（スキルの正本）
```

## API エンドポイント（参考）

- `https://note.com/api/v2/creators/powerpoint_jp/contents?kind=note&page=N`
- `https://note.com/api/v1/magazines/{magazine_key}/notes?page=N`
- `https://note.com/api/v3/notes/{note_key}`

## 更新方法

新記事が出たときの差分取得手順:

```bash
cd metadata
# 1. 最新メタを取得
curl -s "https://note.com/api/v2/creators/powerpoint_jp/contents?kind=note&page=1" -o creator_p1_new.json
# 2. 新規 key を target_articles.json と diff
# 3. 新規 key について articles_raw/{key}.json を取得
# 4. python3 build_articles.py で markdown 化
# 5. python3 download_images.py で画像追加
# 6. patterns/slide_patterns.md に追記
```

## スキル連携

- スキル本体: `.claude/skills/slide-design-patterns/SKILL.md`
- 参照方式: 同スキルの `references/` 配下から相対 symlink で `patterns/slide_patterns.md`・`articles/`・`images/` を参照
- プロジェクト移動時はスキル側の symlink を貼り直すだけで済む
