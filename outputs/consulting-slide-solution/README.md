# Consulting Slide Solution — クライアント説明用一式

> **想定ユース**: コンサル提案・企業説明レベルのプロフェッショナルなスライドを、AI エージェント（Claude Code）と HTML/CSS を組み合わせて高速に量産・編集可能 PPTX 化するソリューション。
> **本一式の用途**: 投影用サンプル・仕組み解説・手順書・スキル定義をまとめて配布する。

---

## このフォルダの中身

```
consulting-slide-solution/
├── README.md                   ← まずここを読む（全体像）
├── 01-仕組みの解説.md          ← なぜこのフローで品質が出るのかの理屈
├── 02-使い方手順書.md          ← 実際の使い方（5 シナリオ）
├── 03-スキル一覧と発動.md      ← Claude Code スキルの内容と発動キーワード
├── 使い方手順書.html           ← ブラウザで読める版（02-使い方手順書.md の HTML 版）
│
├── .claude/
│   └── skills/                ← Claude Code が自動発動するスキル本体
│       ├── consulting-slide-remake/   （画像 → コンサル風スライド再現）
│       └── slide-design-patterns/     （パワポ研由来のパターン辞書）
│
├── slides-source/             ← HTML スライドのソース（編集対象）
│   └── 01-cover.html  〜  12-ai-workflow-asis.html
│
├── assets/
│   ├── style.css              ← HTML スライド共通スタイル（配色・タイポ）
│   ├── images/                ← HTML スライドに埋め込む画像
│   └── references/            ← Mode A に流す参考スライド画像の置き場所
│
├── pptx/                      ← 生成済 PowerPoint（唯一の出力先）
│   ├── consulting-html-slides.pptx          (12 枚 / 画像埋込・見た目完全再現)
│   └── 12-ai-workflow-asis-editable.pptx    (1 枚 / 完全編集可能・ネイティブシェイプ)
│
└── scripts/                   ← 再生成用スクリプト（HTML を編集した後だけ実行）
    ├── 01_build_pptx_image_embed.py     (HTML → PNG → 画像埋込 PPTX)
    └── 02_build_pptx_editable.py        (HTML 設計を元にネイティブ再構築)
```

### フォルダの役割（編集対象 / 出力 / リファレンス）

| 役割 | フォルダ | いつ触る |
|---|---|---|
| **編集対象** | `slides-source/`, `assets/` | 文言や配色を変えたい時 |
| **入力** | `assets/references/` | Mode A に流す参考画像を置く時 |
| **出力** | `pptx/` | 触らない（スクリプトが上書き） |
| **リファレンス** | `.claude/skills/` | Claude Code が自動参照（手で触らない） |
| **実行ツール** | `scripts/` | HTML 編集後に PPTX を再生成する時のみ |

---

## 起点パターンは 2 系統

| 起点 | フロー |
|---|---|
| **参考スライド画像がある** | 画像を `assets/references/` に置く → `consulting-slide-remake` Mode A → HTML → PPTX |
| **参考画像がない（ゼロから）** | テキスト指示 → **Nano Banana / GPT-Image-2 等で 1 枚生成** → 同じく Mode A 以降に流す |

ゼロから作る場合も、生成画像はあくまで **構図のたたき台** として使い、最終アウトプットは HTML/PPTX で編集可能な状態にする。詳しくは `01-仕組みの解説.md` のアーキテクチャ図を参照。

## 5 分で全体像をつかむ

このソリューションは **3 つのレイヤー** で動いている。

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
│  slides-source/*.html + assets/style.css                  │
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

## いますぐ確認したい

- **ブラウザで手順を読みたい**: `使い方手順書.html` をダブルクリック
- **PowerPoint で開きたい**: `pptx/consulting-html-slides.pptx` をダブルクリック（投影向け）
- **編集したい**: `pptx/12-ai-workflow-asis-editable.pptx` をダブルクリック（テキスト・図形すべて編集可）
- **仕組みを把握したい**: `01-仕組みの解説.md`
- **自分で動かしたい**: `02-使い方手順書.md`

---

## スキルの自動発動について

このフォルダを Claude Code で開けば、`.claude/skills/` 配下のスキルが **そのまま発動可能** になっています（`/skills` で確認できます）。別環境にコピーする場合も `.claude/skills/` ごと持っていけば即座に有効です。

---

## 動作要件（再生成する場合のみ）

- macOS / Linux
- Python 3.10+ with `python-pptx`, `playwright`, `Pillow`, `lxml`
- Google Chrome（PNG レンダリング用）
- Claude Code（プロンプトスキルを発動させる場合）

```bash
pip install python-pptx playwright Pillow lxml
# Chrome は通常インストール済み
```
