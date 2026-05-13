# Consulting Slide Solution — クライアント説明用一式

> **想定ユース**: コンサル提案・企業説明レベルのプロフェッショナルなスライドを、AI エージェント（Claude Code）と HTML/CSS を組み合わせて高速に量産・編集可能 PPTX 化するソリューション。
> **本一式の用途**: 投影用サンプル・仕組み解説・手順書・スキル定義をまとめて配布する。

---

## このフォルダの中身

```
consulting-slide-solution/
├── README.md                   ← まずここを読む（全体像）
├── 01-仕組みの解説.md          ← なぜこのフローで品質が出るのかの理屈
├── 02-使い方手順書.md          ← 実際の使い方（4 シナリオ）
├── 03-スキル一覧と発動.md      ← Claude Code スキルの内容と発動キーワード
├── 使い方手順書.html           ← ブラウザで読める版（02-使い方手順書.md の HTML 版）
│
├── input/                      ← 【入力】参考 PowerPoint / 画像 / PDF を置く場所
│   └── pptx雛形素材.png                       （Mode A/B の入力素材）
│
├── src/                        ← 【中間】HTML スライド設計図（編集対象）
│   └── 12-ai-workflow-asis.html  ほか
│
├── output/                     ← 【出力】最終 PowerPoint
│   ├── consulting-html-slides.pptx          (画像埋込・見た目完全再現)
│   ├── 12-ai-workflow-asis-editable.pptx    (完全編集可能・ネイティブシェイプ)
│   └── ai_proposal_workflow_current.pptx
│
├── assets/style.css            ← 共有スタイル（コンサル風配色・タイポ）
│
├── scripts/                    ← 再生成用スクリプト
│   ├── 01_build_pptx_image_embed.py     (src/*.html → PNG → 画像埋込 PPTX)
│   ├── 02_build_pptx_editable.py        (HTML 設計を元にネイティブ再構築)
│   └── build_ai_proposal_workflow.py
│
└── .claude/skills/             ← Claude Code スキル（自動発動）
    ├── consulting-slide-remake/         ← 画像 → コンサル風スライド再現
    └── slide-design-patterns/           ← パワポ研由来のパターン辞書
```

---

## 起点パターンは 2 系統

| 起点 | フロー |
|---|---|
| **参考スライド画像がある** | 画像 → `consulting-slide-remake` Mode A → HTML → PPTX |
| **参考画像がない（ゼロから）** | テキスト指示 → **Nano Banana / GPT-Image-2 等で 1 枚生成** → 同じく Mode A 以降に流す |

ゼロから作る場合も、生成画像はあくまで **構図のたたき台** として使い、最終アウトプットは HTML/PPTX で編集可能な状態にする。詳しくは `01-仕組みの解説.md` のアーキテクチャ図を参照。

## 5 分で全体像をつかむ

このソリューションは **3 つのレイヤー** で動いている。

```
┌─────────────────────────────────────────────────────────┐
│  レイヤー1: プロンプトスキル（再現性の核）                │
│  consulting-slide-remake / slide-design-patterns          │
│  → 「何をどう描くか」をコンサル品質で言語化              │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│  レイヤー2: HTML/CSS スライド（編集容易な中間表現）       │
│  src/*.html + assets/style.css                            │
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
- **PowerPoint で開きたい**: `output/consulting-html-slides.pptx` をダブルクリック（投影向け）
- **編集したい**: `output/12-ai-workflow-asis-editable.pptx` をダブルクリック（テキスト・図形すべて編集可）
- **仕組みを把握したい**: `01-仕組みの解説.md`
- **自分で動かしたい**: `02-使い方手順書.md`

---

## 動作要件（再生成する場合のみ）

- macOS / Linux
- Python 3.10+ with `python-pptx`, `playwright`, `Pillow`
- Google Chrome（PNG レンダリング用）
- Claude Code（プロンプトスキルを発動させる場合）

```bash
pip install python-pptx playwright Pillow
# Chrome は通常インストール済み
```
