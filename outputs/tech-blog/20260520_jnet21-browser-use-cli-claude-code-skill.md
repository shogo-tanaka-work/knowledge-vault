---
title: Claude CodeとBrowser Use CLIでJ-Net21補助金検索を自動化し、スキル化するまで
status: draft
created: 2026-05-20
updated: 2026-05-20
type: tech-tutorial
related:
  - structured/tools/20260510_jnet21-subsidy-search-workflow.md
medium: tech-blog
target_cta: GitHub（jnet21-subsidy-search スキルリポジトリ）
target_platforms:
  - Zenn
  - Qiita
---

# Claude CodeとBrowser Use CLIでJ-Net21補助金検索を自動化し、スキル化するまで

<!-- 画像案①（アイキャッチ）: Claude Code・Browser Use CLI・J-Net21の関係を示すシンプルな構成図。Zenn/Qiitaのカード表示で映えるよう、横長で文字大きめ -->

## TL;DR

- J-Net21の補助金検索をClaude CodeとBrowser Use CLIとPythonで完全自動化
- フォーム操作はやめて、URLパラメータ完全解析とDOM直接抽出で安定化
- `browser-use extract`未実装、`wait`引数仕様、`startDate/endDate`無効など、ドキュメントと実装のギャップに対する具体的なワークアラウンドを共有
- 最終的にClaude Codeの「スキル」（`.skill`形式）としてパッケージ化し、トリガーフレーズで即起動可能に
- 131件の全件取得から56件への期間フィルタと色分けExcel出力までを約20秒で実行

対象読者: ブラウザ自動化、LLMエージェント実装、業務自動化系のスクリプト開発に興味がある方。

---

## 1. 課題設定

中小企業支援の現場では、今月使える補助金リストを定期的に作成する作業が発生します。手動でJ-Net21を巡回すると、検索条件の組み替え、全ページ確認、Excel転記で1回30分。月4回なら年間24時間。

LLMエージェントとブラウザ自動化を組み合わせれば、これ全部潰せるのではと思い立って構築した記録です。

---

## 2. 技術スタック

| レイヤ | 採用 | 補足 |
| --- | --- | --- |
| データソース | J-Net21 snavi2 | 認証不要、公開情報 |
| ブラウザ操作 | Browser Use CLI | `open` / `eval` / `state` を多用 |
| データ処理 | Python 3 + openpyxl | フィルタリング、Excel出力 |
| オーケストレーション | Claude Code（Sonnet 4.6） | 全体制御、スクリプト生成 |
| 配布形式 | Claude Code Skill（`.skill`） | チーム配布、再利用 |

特別なものはなく、すべて無料かOSSです。総コストはClaude Codeのトークン使用分のみで、1回あたり数十円程度。

---

## 3. Browser Use CLIの基本3コマンド

検証の過程で実用に耐えたのは、結局この3つだけでした。

```bash
# ページをロード
browser-use open "https://j-net21.smrj.go.jp/snavi2/results.php?..."

# JavaScriptを実行してDOMから情報抽出
browser-use eval "JSON.stringify([...document.querySelectorAll('.result-item')].map(e => e.innerText))"

# アクセシビリティツリーを取得。リンク・テキスト構造の把握用
browser-use state
```

基本パターンは固定で、

```bash
browser-use open <URL>
sleep 2
browser-use eval "<JS>"
```

ロード後の`sleep 2`を必ず挟みます。これを怠ると`eval`の結果が空配列になります（後述）。

<!-- 画像案②: 上記3コマンドを実行しているターミナルスクショ。それぞれの出力サンプルが見えるとよい -->

### 注意: 未実装と仕様差

公式ドキュメントに載っていながら、実際には未実装か異なる挙動のコマンドが複数ありました。

| コマンド | 想定 | 実態 | 対処 |
| --- | --- | --- | --- |
| `browser-use extract` | DOM抽出のショートカット | 2026/05時点で未実装 | `eval`とJSで代替 |
| `browser-use wait 3` | N秒待機 | 引数形式が違う | シェルの`sleep 2`で代替 |
| `browser-use wait .classname` | 要素待機 | こちらは動く | DOM要素を待つ場合はこちら |

ドキュメントを鵜呑みにせず、最小コマンドで動作確認しながら進めるのが安全です。

---

## 4. J-Net21 URLパラメータの完全解析

最初、検索フォームのチェックボックスを`eval`経由でクリックさせていましたが、フォーム送信後に別の検索ページに飛ばされる謎仕様にぶつかり方針転換しました。

代わりに、フォーム上のすべてのinput要素を一括抽出するJSを書きました。

```javascript
JSON.stringify(
  [...document.querySelectorAll('input[type=checkbox], input[type=radio], select option')]
    .map(e => ({
      name: e.name,
      value: e.value,
      label: e.closest('label')?.innerText || e.parentElement?.innerText || ''
    }))
)
```

これを`browser-use eval`で実行すると、`field[]` `type[]` `prefecture[]` `period`の全選択肢が一覧で取得できます。結果として把握できた主要パラメータが以下。

```
category=2          # 1:セミナー / 2:補助金等 / 3:融資
type[]=3            # 3:補助金 / 5:助成金 / ほか
field[]=24,27,28,35,36,37  # 分野。複数指定可
prefecture[]=00    # 00:全国 / 01:北海道 / ...
period=2            # 1:掲載日基準 / 2:募集期間基準
displaysort=DESC
displaycount=30
search_exec=1       # 初回検索時に必要
page=2              # ページネーション
```

特に`period=1`と`period=2`は同一条件で全く異なる結果を返すため、用途確認が必須です。今回のケースでは2026年5月に申請可能なものが要件だったので`period=2`を採用しました。

<!-- 画像案③: URLパラメータ解析のJS実行結果スクショ。チェックボックスのname/value/labelが一覧表示されている画面 -->

---

## 5. ページネーションと全件取得

ページネーションのURL構造は`state`コマンドで実際のリンクを拾うのが確実です。

```bash
browser-use state | grep "page="
```

これで`.pagination-link`の`href`が取れます。実際には`page=2`、`page=3`と単純な数字インクリメントでした。全5ページをPythonで順次取得するスクリプトを書きました。

```python
# fetch_and_filter.py（抜粋）
import json, re, subprocess, time
from datetime import datetime

BASE = ("https://j-net21.smrj.go.jp/snavi2/results.php"
        "?category=2&type%5B%5D=3"
        "&field%5B%5D=24&field%5B%5D=27&field%5B%5D=28"
        "&field%5B%5D=35&field%5B%5D=36&field%5B%5D=37"
        "&prefecture%5B%5D=00&period=2"
        "&displaysort=DESC&displaycount=30&search_exec=1")

def fetch_page(page: int) -> list[dict]:
    url = f"{BASE}&page={page}"
    subprocess.run(["browser-use", "open", url], check=True)
    time.sleep(2)
    result = subprocess.run(
        ["browser-use", "eval",
         """JSON.stringify([...document.querySelectorAll('.result-item')]
            .map(e => ({
              title: e.querySelector('.result-title')?.innerText,
              link: e.querySelector('a')?.href,
              text: e.innerText
            })))"""],
        capture_output=True, text=True, check=True
    )
    # browser-useの出力は "result: " プレフィックス付き
    raw = result.stdout.strip()
    if raw.startswith("result: "):
        raw = raw[8:]
    return json.loads(raw)

all_items = []
seen = set()
for p in range(1, 6):
    for item in fetch_page(p):
        if item["link"] not in seen:
            seen.add(item["link"])
            all_items.append(item)
```

`Set`でhrefをキーに重複排除しているのは、ページ境界での重複や広告差し込みを吸収するためです。

---

## 6. 募集期間フィルタ（正規表現）

J-Net21の各案件本文中に「募集期間: 2026年4月15日〜2026年6月30日」のような表記があります。これを正規表現で抜いて、対象月にかかるものだけ残します。

```python
PERIOD_RE = re.compile(r'募集期間[：:]\s*(\S+?～\S+)')

def in_target_month(text: str, year: int, month: int) -> bool:
    m = PERIOD_RE.search(text)
    if not m:
        return False  # 期間記載なしは除外。通年型は別途扱い
    start_str, end_str = m.group(1).split("～")
    start = parse_jp_date(start_str)
    end = parse_jp_date(end_str)
    target_start = datetime(year, month, 1)
    target_end = datetime(year, month + 1, 1) if month < 12 else datetime(year + 1, 1, 1)
    return start < target_end and end >= target_start

def parse_jp_date(s: str) -> datetime:
    # "2026年5月10日" → "2026-5-10"
    s = s.replace("年", "-").replace("月", "-").replace("日", "")
    return datetime.strptime(s, "%Y-%m-%d")
```

J-Net21は西暦表記で統一されているため、令和換算など面倒な処理は不要でした。もし「令和N年」表記が混じるサイトを扱うなら、ここに変換ロジックを追加します。

注意点として、期間記載なしが全131件中67件と多い。これらは通年型の制度が多いため、用途に応じて拾うかどうかを判断する必要があります。今回は除外しました。

---

## 7. Excel出力（openpyxl）

openpyxlで色分け付きExcelを生成します。

```python
# create_excel.py（抜粋）
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font
from datetime import datetime, timedelta

URGENT = PatternFill(start_color="FFA500", end_color="FFA500", fill_type="solid")
SOON   = PatternFill(start_color="FFFF99", end_color="FFFF99", fill_type="solid")
NORMAL = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")

def color_by_deadline(deadline: datetime) -> PatternFill:
    days = (deadline - datetime.now()).days
    if days <= 7:  return URGENT
    if days <= 30: return SOON
    return NORMAL

wb = Workbook()
ws = wb.active
ws.title = "補助金一覧"
ws.append(["タイトル", "募集期間", "URL", "分野"])
ws.freeze_panes = "A2"  # ヘッダー固定

for item in sorted_items:
    row = ws.max_row + 1
    ws.append([item["title"], item["period"], item["link"], item["field"]])
    fill = color_by_deadline(item["deadline"])
    for col in range(1, 5):
        ws.cell(row=row, column=col).fill = fill

# 検索条件シート
ws2 = wb.create_sheet("検索条件")
ws2.append(["パラメータ", "値"])
ws2.append(["カテゴリ", "補助金"])
ws2.append(["分野", "創業/経営革新/..."])
ws2.append(["地域", "全国"])
ws2.append(["期間基準", "募集期間（period=2）"])
ws2.append(["対象月", "2026年5月"])

wb.save("2026年5月利用可能補助金一覧.xlsx")
```

「検索条件」シートを別タブで保存しておくと、後から「これどの条件で取ったやつだっけ？」となったときの自力解決率が上がります。納品時の説明責任にも効きます。

<!-- 画像案④: 出力されたExcelの実物スクショ。色分けされた一覧と「検索条件」シートのタブが両方見える状態 -->

---

## 8. Claude Codeスキルとしてのパッケージ化

最後に、この一連のワークフローをClaude Codeのスキルとしてまとめます。スキルディレクトリの構成は以下。

```
jnet21-subsidy-search/
├── SKILL.md           # トリガー定義、引数仕様、実行手順
└── scripts/
    ├── fetch_and_filter.py
    └── create_excel.py
```

`SKILL.md`の主要部分はこんな感じ。

```markdown
---
name: jnet21-subsidy-search
description: |
  J-Net21から補助金情報を自動収集し、指定された期間で
  フィルタリングして色分けExcelに出力するスキル。
  「補助金一覧出して」「今月の補助金まとめて」等で発動。
---

# 使い方

引数:
- period_mode: "publish"（掲載日基準） / "period"（募集期間基準。既定）
- target_year, target_month: 期間フィルタ対象。既定は今月
- fields: 分野コード。既定は創業・経営革新系の主要分野
- prefecture: 都道府県コード。既定は00で全国

実行:
1. scripts/fetch_and_filter.pyを実行してJSON中間ファイル生成
2. scripts/create_excel.pyでExcelに変換
3. 出力ファイルパスをユーザーに通知
```

`.skill`ファイル（zip形式）にパッケージ化すれば、他のメンバーにも配布可能です。

<!-- 画像案⑤: Claude Codeでスキルが起動している様子のスクショ。トリガーフレーズ入力からExcelが生成されるまでの流れ -->

---

## 9. ハマりポイント総まとめ

実装中につまずいた箇所と対処を一覧で。

| 症状 | 原因 | 対処 |
| --- | --- | --- |
| `browser-use extract`が動かない | 未実装 | `eval`とJSで代替 |
| `browser-use wait 3`がエラー | 引数形式が秒数ではない | `sleep 2`（シェル）か`wait .selector` |
| `eval`の結果が空配列 | ページロード前に実行している | `open`の後に`sleep 2`を挟む |
| `JSON.parse`でエラー | `result: `プレフィックスが付く | `output[8:]`でスライス |
| URL`startDate`/`endDate`が効かない | サーバ側で未対応 | 全件取得後にPythonでフィルタ |
| フォームsubmitで別ページに飛ぶ | サイト固有挙動 | フォーム操作を避けURLパラメータ直打ち |

特に最後の、フォーム操作を避けてURLパラメータで攻める、というのは他サイトでも応用が効く一般原則だと思います。

---

## 10. 計測結果

実測値です。

| 項目 | 値 |
| --- | --- |
| 1ページ取得時間 | 約3秒。open 1秒 + sleep 2秒 |
| 全5ページ取得 | 約15〜20秒 |
| フィルタリング | 1秒以下 |
| Excel生成 | 約1秒 |
| 総所要時間（対話含む） | 約5分。条件確認から成果物受領まで |
| 取得件数 | 全131件 → フィルタ後56件 |

---

## 11. 横展開できそうな対象

同じパターンが効きそうな対象を備忘でリストアップします。

- jGrants（公募情報）
- 都道府県の補助金ポータル
- 業界団体の助成金情報ページ
- 競合の新着情報やプレスリリース定期ウォッチ
- 求人情報の条件フィルタ収集
- 公的調達、入札情報

認証不要かつ一覧ページが構造化されていて、URLパラメータで絞り込めるサイトであれば、本記事のパターンがほぼそのまま使えるはずです。

---

## 利用上の注意・免責

本記事を実装の参考にされる際は、以下の点をご確認ください。

J-Net21の利用規約には、2026年5月時点でスクレイピングや自動アクセスを明示的に禁止する条文は確認できませんでした。サイト自体が公的機関の中小企業向け情報を集約する設計のため、情報集約の性格を持ったサービスではあります。

ただし、コンテンツの著作権は中小企業基盤整備機構または情報提供者に帰属しています。実装にあたっては以下を遵守してください。

- 用途は自身または自社クライアントの情報収集の範囲に留めること
- 取得した一覧を第三者に販売したり、有料サービスに組み込む使い方は推奨しません
- アクセス間隔は1〜3秒以上空け、サーバー負荷を最小化すること
- 二次利用時は出典として「中小機構 J-Net21」を明記すること
- 補助金名・期間・金額・URLといった事実情報のみを扱い、記事本文の全文転載は避けること

本記事はあくまで技術的な手法の共有を目的としたものです。実装と運用は各自の責任で行ってください。本記事の内容に基づいて発生したいかなる結果についても、筆者は保証・サポートを行いません。

特に補助金リストの販売など商用配布を目的とした利用は、著作権侵害リスクの観点から推奨しません。本記事はその用途を想定していません。

---

## まとめ

LLMエージェントとブラウザ自動化の組み合わせは派手な題材になりがちですが、本記事のようにドキュメントの欠落、フォーム挙動の罠、日付パースの泥臭さといった現場の細部に向き合うことで、ようやく実用に乗ります。

スキル化までやっておくと、自分だけでなくチーム全体の生産性に効くので、ぜひ試してみてください。

スキルリポジトリ（jnet21-subsidy-search）: [GitHub URL]

---

## 参考

- J-Net21 snavi2: https://j-net21.smrj.go.jp/snavi2/results.php
- Browser Use CLI: https://docs.browser-use.com/open-source/browser-use-cli
- openpyxl: https://openpyxl.readthedocs.io/

---

## メモ

- 想定文字数: 約6500字。Zenn/Qiita標準的なテックチュートリアル長
- 投稿先: Zenn（メイン）→ Qiita（クロスポスト）想定
- 公開タグ案: Zenn `claude-code` `browser-use` `python` `automation`、Qiita `Python` `ClaudeCode` `自動化` `スクレイピング`
