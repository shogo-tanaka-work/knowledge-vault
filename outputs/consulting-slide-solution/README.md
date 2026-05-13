# Consulting Slide Solution — クライアント説明用一式

> **想定ユース**: コンサル提案・企業説明レベルのプロフェッショナルなスライドを、AI エージェント（Claude Code）と HTML/CSS を組み合わせて高速に量産・編集可能 PPTX 化するソリューション。
> **本一式の用途**: 投影用サンプル・仕組み解説・手順書・スキル定義をまとめて配布する。

---

## このフォルダの中身

```
consulting-slide-solution/
├── README.md                   ← まずここを読む（全体像）
├── 使い方手順書.html           ← ブラウザで読める版の手順書（docs/02 の HTML 版）
│
├── docs/                       ← 解説・手順ドキュメント一式
│   ├── 01-仕組みの解説.md       （なぜこのフローで品質が出るのかの理屈）
│   ├── 02-使い方手順書.md       （実際の使い方・5 シナリオ）
│   └── 03-スキル一覧と発動.md   （Claude Code スキルの内容と発動キーワード）
│
├── .claude/
│   └── skills/                ← Claude Code が自動発動するスキル本体
│       ├── consulting-slide-remake/   （画像 → コンサル風スライド再現）
│       └── slide-design-patterns/     （パワポ研由来のパターン辞書）
│
├── tmp-source/             ← 【中間ソース】HTML スライド本体（編集対象）
│   └── 01-cover.html  〜  12-ai-workflow-asis.html
│
├── assets/
│   ├── style.css              ← HTML スライド共通スタイル（配色・タイポ）
│   ├── images/                ← HTML スライドに埋め込む画像
│   └── references/            ← Mode A / Mode B に流す参考スライド画像の置き場所
│
├── outputs/                      ← 【最終アウトプット】クライアントに渡す PowerPoint
│   ├── consulting-html-slides.pptx          (12 枚 / 画像埋込・見た目完全再現)
│   └── 12-ai-workflow-asis-editable.pptx    (1 枚 / 完全編集可能・ネイティブシェイプ)
│
└── scripts/                   ← 再生成用スクリプト（HTML を編集した後だけ実行）
    ├── 01_build_pptx_image_embed.py     (HTML → PNG → 画像埋込 PPTX)
    └── 02_build_pptx_editable.py        (HTML 設計を元にネイティブ再構築)
```

### `tmp-source/` と `outputs/` の関係

このソリューションは **「HTML を設計図にして、それを PPTX に焼く」** 2 段階構造です。両方とも出力物ですが役割が違います。

```
[ 入力 ]                  [ 中間ソース ]                [ 最終アウトプット ]
参考画像 / テキスト指示  →  tmp-source/*.html   →   outputs/*.pptx
                            （HTML 設計図）              （クライアント納品物）
                            ↑                            ↑
                            Claude や手で編集する所      触らない・スクリプトが上書き
```

- **`tmp-source/`** : 文言・配色・図形を編集する場所。Claude Code が新規スライドを作る時もここに HTML を追加する。**人間（または Claude）が編集する側**。
- **`outputs/`** : `scripts/*.py` を実行すると `tmp-source/` から自動生成される。**クライアントに渡すのはこちら**。手で開いて文言だけ直すことも可能（編集可能 PPTX の場合のみ）。

### フォルダの役割まとめ

| 役割 | フォルダ | いつ触る |
|---|---|---|
| **編集対象（中間）** | `tmp-source/`, `assets/` | 文言や配色を変えたい時に手で or Claude 経由で編集 |
| **入力** | `assets/references/` | Mode A / Mode B に流す参考画像を置く時 |
| **最終出力** | `outputs/` | 触らない（スクリプトが上書き）。**ここの .pptx をクライアントに渡す** |
| **スキル本体** | `.claude/skills/` | Claude Code が自動参照（手で触らない） |
| **実行ツール** | `scripts/` | HTML 編集後に PPTX を再生成する時のみ |
| **解説** | `docs/` | 仕組み・手順を読む時 |

---

## スライド作成の2つのパターン

| 起点 | フロー |
|---|---|
| **参考スライド画像がある** | 画像を `assets/references/` に置く → `consulting-slide-remake` Mode A → HTML → PPTX |
| **参考画像がない（ゼロから）** | テキスト指示 → **Nano Banana / GPT-Image-2 等で 1 枚生成** → 同じく Mode A 以降に流す |

ゼロから作る場合も、生成画像はあくまで **構図のたたき台** として使い、最終アウトプットは HTML/PPTX で編集可能な状態にする。詳しくは `docs/01-仕組みの解説.md` のアーキテクチャ図を参照。

## 全体構成（3レイヤー）

スキル → HTML → PPTX の3段階で動いています。

```
┌─────────────────────────────────────────────────────────┐
│  レイヤー1: プロンプトスキル（再現性の核）                │
│  .claude/skills/consulting-slide-remake                   │
│  .claude/skills/slide-design-patterns                     │
│  → 「何をどう描くか」をコンサル品質で言語化              │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│  レイヤー2: HTML/CSS スライド（編集容易な中間表現）       │
│  tmp-source/*.html + assets/style.css                  │
│  → ネイビー・ブロンズ等のコンサル配色を共通化            │
│  → 矢印・DB 図形は SVG でベクター表現                    │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│  レイヤー3: PowerPoint 出力（クライアント納品形式）       │
│  scripts/01_build_pptx_image_embed.py  → 画像埋込         │
│  scripts/02_build_pptx_editable.py     → 編集可能         │
└─────────────────────────────────────────────────────────┘
```

「画像で品質を保つか」「PPTX で編集可能にするか」をユースケースで使い分けられる構造になっている。

---

## どこから手をつけるか

| やりたいこと | 開くファイル |
|---|---|
| 完成したスライドを見る（投影用） | `outputs/consulting-html-slides.pptx` |
| 完成したスライドを編集する | `outputs/12-ai-workflow-asis-editable.pptx` |
| 手順書をブラウザで読む | `使い方手順書.html` |
| 仕組みを理解する | `docs/01-仕組みの解説.md` |
| 自分で動かす | `docs/02-使い方手順書.md` |
| スキルの発動キーワードを調べる | `docs/03-スキル一覧と発動.md` |

---

## スキルの読み込みについて

このフォルダを Claude Code で開けば、`.claude/skills/` 配下のスキルが自動で読み込まれます（`/skills` で一覧確認可）。別環境にコピーする場合も `.claude/skills/` ごと持っていけば、そのまま使えます。

---

## 動作要件（PPTXを再生成する場合のみ）

- macOS / Linux
- Python 3.10+ with `python-pptx`, `playwright`, `Pillow`, `lxml`
- Google Chrome（PNG レンダリング用）
- Claude Code（プロンプトスキルを発動させる場合）

```bash
pip install python-pptx playwright Pillow lxml
# Chrome は通常インストール済み
```
