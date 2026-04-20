# AIエージェントによるPPTXアーキテクチャ図解自動生成 実装ガイド

## メタ情報

| 項目 | 内容 |
|---|---|
| 作成日 | 2026-04-20 |
| ステータス | リサーチ完了・実装待ち |
| 目的 | IT系アーキテクチャ図解スライド（DBシリンダ・太矢印・AWS/Azureアイコン）をAIエージェントで70点精度で自動生成する |
| 主要技術 | python-pptx / DESIGN.md / SKILL.md / draw.io / Claude Code |

---

## 概要

### このドキュメントで実現すること

Claude Code等のAIエージェントに、以下を含むPowerPointスライドを自動生成させる：

- DBサーバーを表すシリンダ（円柱）図形
- サービス間を繋ぐ太い矢印
- AWS/AzureのサービスアイコンをPNG埋め込み
- ブランドカラー・フォントを継承したデザイン
- 一貫したレイアウト（ゾーン座標）

### 精度の現実的な期待値

- ピクセルパーフェクトは**期待できない**
- 正しい設計と制約定義で**70点精度は達成可能**
- Do's and Don'ts の明示と EMU 座標のゾーン定義が精度向上の最大要因

### 推奨アーキテクチャ（三層構造）

```
DESIGN.md           ← ブランド哲学・カラー・フォントの方針
    +
トークン JSON        ← 実際の hex 値・pt 値の正本
    +
SKILL.md            ← タスク固有の制約（EMU座標・禁止事項）
```

---

## Part 1: DESIGN.md の基礎知識

### 1-1. DESIGN.md とは

2026年3月に Google Stitch が提唱したデザインシステムの Markdown 表現フォーマット。

- `README.md` がプロジェクト説明の標準であるように、**DESIGN.md はデザイン仕様のAI向け標準**
- LLM が高忠実度で読める Markdown 形式でカラー・タイポグラフィ・コンポーネント仕様を1ファイルに集約
- プロジェクトルート（`/DESIGN.md`）に置くだけで Claude Code・Cursor が自動参照
- `VoltAgent/awesome-design-md` が公開10日で35,000スターを超え、Stripe・Vercel・Linear・Notion など59サービスの DESIGN.md を収録

### 1-2. DESIGN.md の標準セクション構成

```markdown
# DESIGN.md

## Overview & Principles
ブランドの文脈・デザイン哲学（3〜5原則）

## Color Palette
| Token名    | Hex     | 用途               |
|---|---|---|
| primary    | #1E3A5F | メインカラー       |
| accent     | #FF6B35 | CTAボタン・強調    |
| background | #F8F9FA | ページ背景         |

## Typography
| 役割        | フォント              | サイズ | ウェイト |
|---|---|---|---|
| タイトル    | Noto Sans JP Bold    | 36pt  | 700      |
| 本文        | Noto Sans JP Regular | 14pt  | 400      |

## Spacing
- ベースユニット: 8px
- セクション間: 32px（4単位）
- コンポーネント内: 16px（2単位）

## Do's and Don'ts
### Do
- 白背景には必ずプライマリカラーのアクセントを1要素入れる

### Don't
- テキストのみのスライドを作らない
- 3色以上のカラーを1スライドに使わない
```

### 1-3. CLAUDE.md との棲み分け

| ファイル | 役割 | 内容例 |
|---|---|---|
| `CLAUDE.md` | 実装の方法を伝える | コミット規約・禁止操作・言語設定 |
| `DESIGN.md` | 見た目の方針を伝える | カラー・フォント・レイアウト原則 |
| `SKILL.md` | タスク固有の制約を伝える | EMU座標・図形種別・検証コマンド |

### 1-4. 書くべき内容 vs 書かない方がいい内容

**書くべき内容（効果が高い）:**
- ブランドの視覚的哲学・雰囲気（AIが迷ったときの判断基準になる）
- カラーは意味的役割（`primary`, `danger`, `muted`）と hex 値の組み合わせ
- タイポグラフィは「フォント名だけ」でなく「どの場面で使うか」まで記載
- **明示的な禁止事項（Do's and Don'ts セクション）** ← 最も精度向上に効く
- 実際に出荷済みコードに基づいたルール（aspirational ではなく実態）

**書かない方がいい内容（精度が下がる・管理コストが増す）:**
- 全ルールの網羅（肥大化すると逆効果）
- 他ドキュメントとの重複情報（二重管理はズレを生む）
- 具体的な実装コード（SKILL.md やコンポーネントファイルへ委譲）
- aspirational なデザイン（実際の実装と乖離したルール）

---

## Part 2: PPTX生成の実装基盤

### 2-1. 環境構築

```bash
# 必要パッケージのインストール
pip install python-pptx pillow lxml

# AWS/Azureアイコンを使う場合
pip install cairosvg  # SVG→PNG変換（オプション）
```

### 2-2. スライドサイズとEMU座標系の理解

python-pptx の座標は**EMU（English Metric Units）**で管理する。

```python
# 基本変換
1インチ = 914,400 EMU
1センチ = 360,000 EMU
1ポイント = 12,700 EMU

# 16:9 スライドの基準値
SLIDE_W = 9_144_000   # 10インチ = 13.33インチ（実際は下記）
SLIDE_H = 5_143_500   # 7.5インチ

# python-pptxのInches()ヘルパー
from pptx.util import Inches, Pt, Emu
Inches(1)   # = 914400
Pt(12)      # = 152400
Emu(914400) # そのまま
```

**実際の16:9スライドサイズ（標準）:**
```python
SLIDE_W = 9_144_000  # 13.33インチ（横）
SLIDE_H = 5_143_500  # 7.5インチ（縦）
```

### 2-3. ゾーン定義（精度向上の核心）

AIに座標を「計算」させず「参照」させることで精度が大幅に向上する。以下を `SKILL.md` とコード双方に持たせる。

```python
# zones.py（またはSKILL.mdに定数として記載）

SLIDE_W = 9_144_000
SLIDE_H = 5_143_500
MARGIN  = 457_200    # 0.5インチ
GAP     = 304_800    # 0.33インチ

ZONES = {
    "header": {
        "left":   MARGIN,
        "top":    MARGIN,
        "width":  SLIDE_W - 2 * MARGIN,
        "height": 685_800,  # 0.75インチ
    },
    "main_left": {
        "left":   MARGIN,
        "top":    1_143_000,
        "width":  (SLIDE_W - 2 * MARGIN - GAP) // 2,
        "height": 3_200_000,
    },
    "main_right": {
        "left":   MARGIN + (SLIDE_W - 2 * MARGIN - GAP) // 2 + GAP,
        "top":    1_143_000,
        "width":  (SLIDE_W - 2 * MARGIN - GAP) // 2,
        "height": 3_200_000,
    },
    "footer": {
        "left":   MARGIN,
        "top":    4_571_100,
        "width":  SLIDE_W - 2 * MARGIN,
        "height": 380_000,
    },
}
```

---

## Part 3: 図解要素の実装方法

### 3-1. データベースシリンダ（円柱）の描き方

**重要：** python-pptx に `CYLINDER` という名称は存在しない。フローチャート系シェイプで代用する。

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE_TYPE
from pptx.dml.color import RGBColor

prs = Presentation()
slide = prs.slides.add_slide(prs.slide_layouts[6])  # 空白レイアウト

# DBシリンダ（縦置き）
# MSO_SHAPE.FLOW_CHART_MAGNETIC_DISK = 86
from pptx.util import Emu
db_shape = slide.shapes.add_shape(
    86,  # FLOW_CHART_MAGNETIC_DISK（DBシリンダ）
    left=Inches(2),
    top=Inches(2),
    width=Inches(1.2),
    height=Inches(1.5)
)
db_shape.fill.solid()
db_shape.fill.fore_color.rgb = RGBColor(0x1E, 0x6B, 0xAA)  # Azureブルー
db_shape.line.color.rgb = RGBColor(0x0D, 0x47, 0x7A)
db_shape.line.width = Pt(1.5)

# ラベルを追加
tf = db_shape.text_frame
tf.text = "PostgreSQL"
tf.paragraphs[0].runs[0].font.size = Pt(10)
tf.paragraphs[0].runs[0].font.bold = True
tf.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
```

**シリンダ系シェイプ一覧：**

| 用途 | 定数名（MSO_SHAPE） | 値 |
|---|---|---|
| DBシリンダ（縦・推奨） | `FLOW_CHART_MAGNETIC_DISK` | 86 |
| DBシリンダ（横） | `FLOW_CHART_DIRECT_ACCESS_STORAGE` | 87 |
| テープ型ストレージ | `FLOW_CHART_SEQUENTIAL_ACCESS_STORAGE` | 85 |

### 3-2. 太い矢印（Block Arrow）の描き方

```python
# 右向き太矢印
arrow = slide.shapes.add_shape(
    33,  # RIGHT_ARROW
    left=Inches(3.5),
    top=Inches(2.8),
    width=Inches(1.0),
    height=Inches(0.4)
)
arrow.fill.solid()
arrow.fill.fore_color.rgb = RGBColor(0xFF, 0x6B, 0x35)  # アクセントカラー
arrow.line.fill.background()  # 枠線なし

# 矢印に説明テキストを入れる場合
arrow.text_frame.text = "API呼び出し"
arrow.text_frame.paragraphs[0].runs[0].font.size = Pt(8)
arrow.text_frame.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
```

**矢印系シェイプ一覧：**

| 方向 | 定数名（MSO_SHAPE） | 値 |
|---|---|---|
| 右向き | `RIGHT_ARROW` | 33 |
| 左向き | `LEFT_ARROW` | 34 |
| 上向き | `UP_ARROW` | 35 |
| 下向き | `DOWN_ARROW` | 36 |
| 左右双方向 | `LEFT_RIGHT_ARROW` | 37 |
| ノッチ付き右矢印 | `NOTCHED_RIGHT_ARROW` | 50 |
| 五角形矢印 | `PENTAGON` | 56 |

### 3-3. AWS/Azureアイコンの埋め込み

**重要：** python-pptx はSVGネイティブ非対応。PNG変換が最も安定。

#### ステップ1：アイコンの入手

```bash
# AWS公式アイコンパック（PNG形式でダウンロード可能）
# https://aws.amazon.com/architecture/icons/
# ダウンロード後、アイコンフォルダをローカルに配置

# Azure公式（Microsoft Tech Community経由）
# https://www.microsoft.com/en-us/download/details.aspx?id=41937

# OSSのMicrosoftアーキテクチャアイコン
# https://github.com/MichaelKortas/microsoft-architecture-pptx-icons
```

#### ステップ2：PNGとして埋め込む

```python
import os
from pptx.util import Inches

# アイコンディレクトリ
ICON_DIR = "./icons/aws/"

def add_icon(slide, icon_filename, left, top, size=Inches(0.5)):
    """AWSアイコンをスライドに追加"""
    icon_path = os.path.join(ICON_DIR, icon_filename)
    if not os.path.exists(icon_path):
        raise FileNotFoundError(f"アイコンが見つかりません: {icon_path}")
    
    pic = slide.shapes.add_picture(
        icon_path,
        left=left,
        top=top,
        width=size,
        height=size
    )
    return pic

# 使用例
add_icon(slide, "ec2.png", left=Inches(1), top=Inches(2))
add_icon(slide, "rds.png", left=Inches(3), top=Inches(2))
add_icon(slide, "s3.png",  left=Inches(5), top=Inches(2))
```

#### SVG→PNG変換（品質を保ちたい場合）

```python
import cairosvg
from io import BytesIO

def svg_to_png_bytes(svg_path: str, size: int = 128) -> BytesIO:
    """SVGをPNG bytesに変換"""
    png_data = cairosvg.svg2png(
        url=svg_path,
        output_width=size,
        output_height=size
    )
    return BytesIO(png_data)

# 使用例
png_io = svg_to_png_bytes("./icons/aws/ec2.svg", size=64)
slide.shapes.add_picture(png_io, left=Inches(1), top=Inches(2),
                         width=Inches(0.5), height=Inches(0.5))
```

### 3-4. コネクタ線（矢印付きライン）の描き方

図形同士を線で繋ぐ場合：

```python
from pptx.oxml.ns import qn
from lxml import etree

# コネクタを追加（ElbowConnector = 折れ線接続）
connector = slide.shapes.add_connector(
    3,  # MSO_CONNECTOR.ELBOW
    begin_x=Inches(2), begin_y=Inches(2.5),
    end_x=Inches(4),   end_y=Inches(2.5)
)
connector.line.color.rgb = RGBColor(0x66, 0x66, 0x66)
connector.line.width = Pt(1.5)

# 矢印の先端を設定（XML直接操作）
ln = connector.line._ln
tailEnd = etree.SubElement(ln, qn('a:tailEnd'))
tailEnd.set('type', 'arrow')
tailEnd.set('w', 'med')
tailEnd.set('len', 'med')
```

---

## Part 4: テンプレートPPTXを活用したアプローチ

### 4-1. テンプレートPPTXの作り方

既存のデザイン済みPPTXをベースにする場合、スライドを全削除してマスター・テーマだけ残す。

```python
from pptx import Presentation
from pptx.util import Inches

def create_blank_from_template(template_path: str) -> Presentation:
    """既存PPTXからスライドを全削除してテンプレートとして返す"""
    prs = Presentation(template_path)
    
    # 既存スライドを全削除（スライドマスター・テーマは残る）
    xml_slides = prs.slides._sldIdLst
    while len(xml_slides) > 0:
        xml_slides.remove(xml_slides[0])
    
    return prs

# 使用例
prs = create_blank_from_template("brand_template.pptx")
slide = prs.slides.add_slide(prs.slide_layouts[6])  # 空白レイアウト
```

### 4-2. プレースホルダーのテキスト置換

```python
def replace_placeholder_text(slide, idx: int, new_text: str):
    """指定インデックスのプレースホルダーのテキストを置換"""
    for ph in slide.placeholders:
        if ph.placeholder_format.idx == idx:
            ph.text = new_text
            return
    raise ValueError(f"プレースホルダー idx={idx} が見つかりません")

# プレースホルダー一覧を確認する場合
for ph in slide.placeholders:
    print(f"idx={ph.placeholder_format.idx}, name={ph.name}, type={ph.placeholder_format.type}")
```

### 4-3. テンプレートから既存シェイプのスタイルを抽出

```python
def extract_shape_styles(template_path: str):
    """テンプレートPPTXから図形のスタイル情報を抽出"""
    prs = Presentation(template_path)
    styles = []
    
    for slide_num, slide in enumerate(prs.slides):
        for shape in slide.shapes:
            style_info = {
                "slide": slide_num,
                "name": shape.name,
                "shape_type": str(shape.shape_type),
                "left_emu": shape.left,
                "top_emu": shape.top,
                "width_emu": shape.width,
                "height_emu": shape.height,
            }
            if shape.has_text_frame:
                for para in shape.text_frame.paragraphs:
                    for run in para.runs:
                        style_info["font_size"] = str(run.font.size)
                        style_info["font_bold"] = run.font.bold
                        break
            styles.append(style_info)
    
    return styles

# スタイル情報をJSONに保存してSKILL.mdのリファレンスに使う
import json
styles = extract_shape_styles("architecture_template.pptx")
with open("template_styles.json", "w") as f:
    json.dump(styles, f, ensure_ascii=False, indent=2)
```

---

## Part 5: SKILL.md の書き方

### 5-1. SKILL.md の基本構造

```markdown
# SKILL.md - PPTXアーキテクチャ図解生成スキル

## このスキルの目的
python-pptxを使って、IT系アーキテクチャ図解スライドを自動生成する。

## 実行環境
- Python 3.10+
- python-pptx >= 0.6.21
- pillow >= 9.0

## ファイル構成
- `generate.py`      : メイン生成スクリプト
- `zones.py`         : EMUゾーン定義
- `icons/aws/`       : AWSアイコン（PNG）
- `icons/azure/`     : Azureアイコン（PNG）
- `template.pptx`    : ブランドテンプレート
- `thumbnail.py`     : 検証用サムネイル生成
- `validate.py`      : XML検証スクリプト

## スライドサイズ（必ずこの値を使う）
- 横: 9,144,000 EMU (13.33インチ)
- 縦: 5,143,500 EMU (7.5インチ)

## ゾーン定義（必ずこの値を参照すること。座標を自分で計算しない）
| ゾーン名     | left      | top       | width     | height    |
|---|---|---|---|---|
| header      | 457,200   | 457,200   | 8,229,600 | 685,800   |
| main_left   | 457,200   | 1,143,000 | 3,962,400 | 3,200,000 |
| main_right  | 4,724,400 | 1,143,000 | 3,962,400 | 3,200,000 |
| main_full   | 457,200   | 1,143,000 | 8,229,600 | 3,200,000 |
| footer      | 457,200   | 4,571,100 | 8,229,600 | 380,000   |

## 使用可能な図形（必ずこの値を使う）
| 用途           | MSO_SHAPE値 | EMU推奨サイズ（W×H）       |
|---|---|---|
| DBシリンダ     | 86          | 1,097,280 × 1,371,600     |
| 右向き太矢印   | 33          | 914,400 × 365,760         |
| サーバーボックス | 1 (RECT)   | 1,371,600 × 1,097,280     |

## カラーパレット（必ずこの値を使う）
| 役割       | RGB値          |
|---|---|
| primary    | (30, 58, 95)   |
| accent     | (255, 107, 53) |
| background | (248, 249, 250)|
| text_dark  | (33, 37, 41)   |
| aws_orange | (255, 153, 0)  |
| azure_blue | (0, 120, 212)  |

## 禁止事項（Do's and Don'ts）
### やってはいけないこと
- テキストのみのスライドを作らない（必ず視覚要素を含める）
- 図形をゾーン外に配置しない
- 3色以上のカラーを1スライドに使わない
- 図形をオーバーラップさせない（コネクタ線は除く）
- SVGを直接 add_picture() に渡さない（PNG変換必須）
- 座標を独自に計算しない（ZONES定数を参照する）

### やるべきこと
- 各スライド生成後に thumbnail.py で視覚確認
- XMLを変更した場合は validate.py を実行
- アイコンは icons/ ディレクトリのPNGのみ使用

## 生成フロー
1. template.pptx を開く
2. zones.py のZONES定数を参照して座標を決定
3. 図形・アイコン・テキストを追加
4. thumbnail.py で確認
5. 指摘があれば修正して再確認（ゼロ指摘になるまで繰り返す）
```

### 5-2. 検証スクリプト（thumbnail.py）

```python
# thumbnail.py
"""生成されたPPTXのサムネイルをPNG出力して視覚確認する"""
import subprocess
import sys
from pathlib import Path

def generate_thumbnail(pptx_path: str, output_dir: str = "./thumbnails"):
    """LibreOfficeを使ってPPTXをPNGに変換"""
    Path(output_dir).mkdir(exist_ok=True)
    result = subprocess.run([
        "libreoffice", "--headless", "--convert-to", "png",
        "--outdir", output_dir, pptx_path
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"変換エラー: {result.stderr}")
        return None
    
    print(f"サムネイル生成完了: {output_dir}/")
    return output_dir

if __name__ == "__main__":
    pptx_path = sys.argv[1] if len(sys.argv) > 1 else "output.pptx"
    generate_thumbnail(pptx_path)
```

### 5-3. 検証スクリプト（validate.py）

```python
# validate.py
"""PPTXのXML構造を検証して問題を報告する"""
import zipfile
from lxml import etree
from pathlib import Path

def validate_pptx(pptx_path: str) -> list[str]:
    """PPTXのXMLを検証してエラーリストを返す"""
    errors = []
    
    with zipfile.ZipFile(pptx_path, 'r') as z:
        slide_files = [f for f in z.namelist() if f.startswith("ppt/slides/slide")]
        
        for slide_file in sorted(slide_files):
            with z.open(slide_file) as f:
                try:
                    tree = etree.parse(f)
                    root = tree.getroot()
                    
                    # 図形数の確認
                    sp_tree = root.find(".//{http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing}spTree")
                    
                except etree.XMLSyntaxError as e:
                    errors.append(f"{slide_file}: XML構文エラー - {e}")
    
    return errors

if __name__ == "__main__":
    import sys
    pptx_path = sys.argv[1] if len(sys.argv) > 1 else "output.pptx"
    errors = validate_pptx(pptx_path)
    
    if errors:
        print("検証エラー:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print("検証OK: XMLエラーなし")
```

---

## Part 6: draw.io を使ったパイプライン

### 6-1. draw.io → PPTX 変換パイプライン

```bash
# drawio2pptx のインストール
pip install drawio2pptx

# 基本的な変換
python -m drawio2pptx input.drawio output.pptx

# オプション：テンプレートを指定
python -m drawio2pptx input.drawio output.pptx --template brand_template.pptx
```

```python
# drawio2pptx Python API での使用
from drawio2pptx import convert

convert(
    input_path="architecture.drawio",
    output_path="output.pptx",
    template_path="brand_template.pptx"
)
```

### 6-2. draw.io で使えるAWSシリンダ対応シェイプ

draw.io では以下のシェイプライブラリを有効化する：

1. **Extra > Shapes > Networking** → DBシリンダ含む
2. **AWS > All** → AWSアイコン（公式パック）
3. **Azure > All** → Azureアイコン

draw.io でアーキテクチャを組んでから `drawio2pptx` で変換すると、3Dシリンダも正しく変換される（アルファ版だが AWS 対応済み）。

### 6-3. draw.io XML フォーマット（参考）

```xml
<!-- architecture.drawio の基本構造 -->
<mxfile>
  <diagram name="Architecture">
    <mxGraphModel>
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        
        <!-- DBシリンダ -->
        <mxCell id="2" value="PostgreSQL" style="shape=cylinder3;..." vertex="1" parent="1">
          <mxGeometry x="200" y="200" width="80" height="100" as="geometry" />
        </mxCell>
        
        <!-- 太矢印 -->
        <mxCell id="3" value="" style="shape=mxgraph.arrows2.arrow;..." edge="1" parent="1">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

---

## Part 7: 完全な実装例（アーキテクチャ図解スライド1枚）

```python
# generate_architecture_slide.py

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

# === カラー定数 ===
COLOR_PRIMARY    = RGBColor(0x1E, 0x3A, 0x5F)
COLOR_ACCENT     = RGBColor(0xFF, 0x6B, 0x35)
COLOR_AZURE      = RGBColor(0x00, 0x78, 0xD4)
COLOR_AWS_ORANGE = RGBColor(0xFF, 0x99, 0x00)
COLOR_WHITE      = RGBColor(0xFF, 0xFF, 0xFF)
COLOR_GRAY       = RGBColor(0x66, 0x66, 0x66)

# === シェイプ値定数 ===
SHAPE_CYLINDER  = 86   # FLOW_CHART_MAGNETIC_DISK
SHAPE_RECT      = 1    # RECTANGLE
SHAPE_ARROW_R   = 33   # RIGHT_ARROW
SHAPE_ARROW_D   = 36   # DOWN_ARROW

# === EMUゾーン定数 ===
SLIDE_W, SLIDE_H = 9_144_000, 5_143_500
MARGIN = 457_200
GAP    = 304_800

def add_label(slide, text: str, left, top, width, height,
              font_size=10, bold=False, color=COLOR_WHITE, align=PP_ALIGN.CENTER):
    """テキストボックスを追加するヘルパー"""
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(font_size)
    run.font.bold = bold
    run.font.color.rgb = color
    return txBox

def add_component_box(slide, label: str, icon_path: str | None,
                      left, top, width=Inches(1.5), height=Inches(1.5)):
    """サービスコンポーネントボックス（アイコン+ラベル）を追加"""
    # 背景ボックス
    box = slide.shapes.add_shape(SHAPE_RECT, left, top, width, height)
    box.fill.solid()
    box.fill.fore_color.rgb = RGBColor(0xF0, 0xF4, 0xF8)
    box.line.color.rgb = COLOR_PRIMARY
    box.line.width = Pt(1)
    
    # アイコン（あれば）
    icon_size = Inches(0.6)
    icon_left = left + (width - icon_size) // 2
    icon_top  = top + Inches(0.15)
    if icon_path:
        slide.shapes.add_picture(icon_path, icon_left, icon_top,
                                  width=icon_size, height=icon_size)
    
    # ラベル
    label_top = top + height - Inches(0.5)
    add_label(slide, label,
              left=left, top=label_top, width=width, height=Inches(0.4),
              font_size=9, bold=True, color=COLOR_PRIMARY)
    return box

def generate_architecture_slide(output_path: str = "output.pptx",
                                  template_path: str | None = None):
    # PPTXを初期化
    prs = Presentation(template_path) if template_path else Presentation()
    prs.slide_width  = Emu(SLIDE_W)
    prs.slide_height = Emu(SLIDE_H)
    
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # 空白スライド
    
    # --- タイトル ---
    add_label(slide, "クラウドアーキテクチャ概要",
              left=Emu(MARGIN), top=Emu(MARGIN),
              width=Emu(SLIDE_W - 2 * MARGIN), height=Emu(685_800),
              font_size=24, bold=True, color=COLOR_PRIMARY)
    
    # --- コンポーネント配置（横並び3つ） ---
    comp_y      = Emu(1_200_000)
    comp_width  = Inches(1.8)
    comp_height = Inches(1.8)
    
    positions = [
        (Inches(1.0),  "EC2\nWebサーバー", "icons/aws/ec2.png"),
        (Inches(4.75), "RDS\nPostgreSQL",   None),              # アイコンなし→シリンダで代用
        (Inches(8.5),  "S3\nストレージ",    "icons/aws/s3.png"),
    ]
    
    for x_pos, label, icon_path in positions:
        add_component_box(slide, label, icon_path,
                          left=x_pos, top=comp_y,
                          width=comp_width, height=comp_height)
    
    # DBシリンダ（RDSの代わりに使う場合）
    db = slide.shapes.add_shape(
        SHAPE_CYLINDER,
        left=Inches(4.5), top=Emu(1_300_000),
        width=Inches(1.4), height=Inches(1.6)
    )
    db.fill.solid()
    db.fill.fore_color.rgb = COLOR_AZURE
    db.line.color.rgb = RGBColor(0x00, 0x50, 0x9D)
    db.line.width = Pt(1.5)
    
    # --- 右向き太矢印（EC2 → RDS） ---
    arrow1 = slide.shapes.add_shape(
        SHAPE_ARROW_R,
        left=Inches(3.0), top=Emu(1_750_000),
        width=Inches(1.2), height=Inches(0.4)
    )
    arrow1.fill.solid()
    arrow1.fill.fore_color.rgb = COLOR_ACCENT
    arrow1.line.fill.background()
    add_label(slide, "SQL", left=Inches(3.0), top=Emu(1_700_000),
              width=Inches(1.2), height=Emu(300_000),
              font_size=8, color=COLOR_GRAY)
    
    # --- 右向き太矢印（RDS → S3） ---
    arrow2 = slide.shapes.add_shape(
        SHAPE_ARROW_R,
        left=Inches(6.1), top=Emu(1_750_000),
        width=Inches(1.2), height=Inches(0.4)
    )
    arrow2.fill.solid()
    arrow2.fill.fore_color.rgb = COLOR_ACCENT
    arrow2.line.fill.background()
    
    prs.save(output_path)
    print(f"保存完了: {output_path}")

if __name__ == "__main__":
    generate_architecture_slide()
```

---

## Part 8: ベストプラクティスまとめ

### 8-1. アプローチ選択フロー

```
既存PPTXテンプレートがある？
    │
    ├── Yes → テンプレートPPTX + SKILL.md（EMU座標定義）の組み合わせ
    │              ↓
    │          ブランドカラー・フォントを継承しつつ内容を生成
    │
    └── No  → draw.ioでアーキテクチャを組む
                   ↓
               drawio2pptxでPPTXシェイプに変換
                   ↓
               python-pptxでブランドスタイルを後付け適用
```

### 8-2. 70点精度を達成するためのチェックリスト

- [ ] SKILL.md に EMU ゾーン定数を定義してある（AIが座標を計算しない）
- [ ] 使う図形の値（MSO_SHAPE の整数値）を SKILL.md に列挙してある
- [ ] カラーパレットを RGB 値で SKILL.md に記載してある
- [ ] Do's and Don'ts セクションに禁止事項を書いてある
- [ ] thumbnail.py / validate.py による fix-and-verify ループを組み込んでいる
- [ ] AWS/Azure アイコンは PNG 形式で icons/ ディレクトリに配置してある
- [ ] テンプレートPPTX を使う場合はスライドマスターを確認してある

### 8-3. よくあるハマりポイント

| 問題 | 原因 | 対処 |
|---|---|---|
| SVGが埋め込めない | python-pptxがSVG非対応 | PNGに変換してから `add_picture()` |
| 図形が重なる | EMU計算ミス | ZONES定数を参照する仕組みにする |
| DBシリンダが見つからない | `CYLINDER`という名前が存在しない | 値86（FLOW_CHART_MAGNETIC_DISK）を使う |
| テーマカラーが引き継がれない | テンプレートのマスターが参照されていない | `prs.slide_layouts[6]` で空白レイアウトを使う |
| PPTXが開けなくなる | 不正なXMLを注入した | validate.py で確認してから保存 |
| グループ化できない | python-pptxにグループ化APIがない | XML直接操作か、座標をハードコードで回避 |

---

## Part 9: 参考リソース

### OSSリポジトリ

| 名前 | URL | 特徴 |
|---|---|---|
| PPTAgent | https://github.com/icip-cas/pptagent | テンプレート学習型・最も完成度が高い |
| ppt-master | https://github.com/hugohe3/ppt-master | SVG中間フォーマット→ネイティブ図形生成 |
| drawio2pptx | https://github.com/mashu3/drawio2pptx | draw.io→PPTX変換（AWS/3Dシリンダ対応） |
| ppt-agents | https://github.com/chenxingqiang/ppt-agents | Markdown→PPTX変換 |
| awesome-design-md | https://github.com/VoltAgent/awesome-design-md | 59サービスのDESIGN.md収録 |
| awesome-design-md-jp | https://github.com/kzhrknt/awesome-design-md-jp | 日本語版（CJKタイポグラフィ対応） |
| Anthropic PPTX SKILL.md | https://github.com/anthropics/skills/blob/main/skills/pptx/SKILL.md | 公式実装の参考 |

### アイコンリソース

| 名前 | URL | 備考 |
|---|---|---|
| AWS Architecture Icons | https://aws.amazon.com/architecture/icons/ | 公式・PNG DL可 |
| Microsoft Architecture PPTX Icons | https://github.com/MichaelKortas/microsoft-architecture-pptx-icons | OSS |
| Azure Architecture PowerPoint | https://techcommunity.microsoft.com/blog/coreinfrastructureandsecurityblog/designing-cloud-architecture-creating-professional-azure-diagrams-with-powerpoin/3996707 | Microsoft公式 |

### ドキュメント

| 名前 | URL |
|---|---|
| python-pptx 公式ドキュメント | https://python-pptx.readthedocs.io/ |
| MSO_AUTO_SHAPE_TYPE 一覧 | https://python-pptx.readthedocs.io/en/latest/api/enum/MsoAutoShapeType.html |
| msoAutoShapeType.py（全値） | https://github.com/scanny/python-pptx/blob/master/spec/gen_spec/src_data/msoAutoShapeType.py |
| DESIGN.md とは | https://designmd.app/en/what-is-design-md |
| DESIGN.md ベストプラクティス | https://designproject.io/blog/design-md-file/ |

---

## 次のステップ（検証TODO）

- [ ] **Step 1**: python-pptx で DBシリンダ・太矢印の基本動作を確認する（shape値86/33）
- [ ] **Step 2**: AWS公式アイコンパックをダウンロードして PNG 埋め込みを試す
- [ ] **Step 3**: ZONES定数ファイル（`zones.py`）を作り、SKILL.md に EMU ゾーン表を記載する
- [ ] **Step 4**: 既存ブランドPPTXからテンプレートを作成して `create_blank_from_template()` を試す
- [ ] **Step 5**: Claude Code に SKILL.md を渡してアーキテクチャ図解スライドを生成させる
- [ ] **Step 6**: thumbnail.py / validate.py を組み込んで fix-and-verify ループを確認する
- [ ] **Step 7**: drawio2pptx で draw.io ファイルの変換を試す（3Dシリンダ確認）
- [ ] **Step 8**: DESIGN.md を作成してブランド哲学・Do's and Don'ts を整備する
