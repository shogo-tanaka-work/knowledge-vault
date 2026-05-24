"""automation-cases.csv から発信ネタカードの雛形を生成する。

成果報告DB系（業務成果報告DB / Biz成果報告DB）の行のみを対象とし、
1行=1カードの Markdown を cards/ 配下に出力する。

汎用化Tips・発信角度の候補は人手加筆前提で TODO コメントを残す。
INDEX.md も同時生成。
"""
from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path
from collections import defaultdict

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
DEFAULT_CSV = ROOT / "source" / "automation-cases.csv"
CARDS_DIR = ROOT / "cards"

TARGET_SHEETS = {"業務成果報告DB", "Biz成果報告DB"}


def slugify(text: str, max_len: int = 40) -> str:
    text = text.strip()
    text = re.sub(r"[\s/、，,／・\\]+", "-", text)
    text = re.sub(r"[^\wぁ-んァ-ヶ一-鿿A-Za-z0-9\-]", "", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text[:max_len] or "case"


def parse_list_cell(value: str) -> list[str]:
    if not value:
        return []
    return [v.strip() for v in re.split(r"[,、，]", value) if v.strip()]


def render_yaml_list(items: list[str]) -> str:
    if not items:
        return "[]"
    escaped = [f'"{i}"' if any(c in i for c in ",[]\"") else i for i in items]
    return "[" + ", ".join(escaped) + "]"


def make_card(row: dict, card_id: int) -> tuple[str, str]:
    categories = parse_list_cell(row.get("category", ""))
    tools = parse_list_cell(row.get("tools", ""))
    primary_tool = tools[0] if tools else "AI"
    primary_cat = categories[0] if categories else "業務改善"

    slug = slugify(f"{primary_tool}-{primary_cat}")
    filename = f"{card_id:03d}-{slug}.md"

    quant = (row.get("quant_effect") or "").strip()
    title_hint = quant if quant else primary_cat
    h1 = f"{primary_tool}による{primary_cat}（{title_hint}）" if quant else f"{primary_tool}による{primary_cat}"

    front_matter = "\n".join([
        "---",
        f"id: {card_id:03d}",
        f"category: {render_yaml_list(categories)}",
        f"tools: {render_yaml_list(tools)}",
        f'quant_effect: "{quant}"',
        "status: 完成事例",
        f'source_sheet: {row.get("source_sheet", "")}',
        f'source_row: {row.get("source_row", "")}',
        "published_axes: []  # TODO: note / X / Threads / LinkedIn / 技術ブログ から選ぶ",
        "---",
    ])

    body = f"""
# {h1}

> ⚠ タイトルは雛形。汎化済み本文を読んだうえで書き直すこと。

## Before（改善前の課題）

{row.get('before', '').strip() or '（元データに記載なし）'}

## After（改善後の変化）

{row.get('after', '').strip() or '（元データに記載なし）'}

## 定量効果

{quant or '（数値情報なし）'}

## 定性効果

{row.get('qualitative_effect', '').strip() or '（記載なし）'}

## 講師所感・特記事項

{row.get('notes', '').strip() or '（記載なし）'}

## 社内展開の有無

{row.get('internal_rollout', '').strip() or '（記載なし）'}

## 汎用化Tips（他業務へ展開する際のポイント）

<!-- TODO: 業界・業務に依存しない再現手順や勘所を3〜5項目で書き出す -->

## 発信角度の候補

<!-- TODO: 媒体別の切り口メモ
- note:
- X:
- Threads:
- LinkedIn:
- 技術ブログ:
-->
"""

    return filename, front_matter + body


def generate_index(cards: list[dict]) -> str:
    by_category: dict[str, list[dict]] = defaultdict(list)
    by_tool: dict[str, list[dict]] = defaultdict(list)
    for c in cards:
        for cat in c["categories"] or ["未分類"]:
            by_category[cat].append(c)
        for tool in c["tools"] or ["未指定"]:
            by_tool[tool].append(c)

    lines = ["# 自動化事例カード INDEX", "",
             f"合計 {len(cards)} 件（フェーズ1: 成果報告DB系）", ""]

    lines.append("## カテゴリ別")
    lines.append("")
    for cat in sorted(by_category, key=lambda k: -len(by_category[k])):
        lines.append(f"### {cat}（{len(by_category[cat])}件）")
        for c in by_category[cat]:
            lines.append(f"- [{c['id']:03d} {c['title']}](./{c['filename']})")
        lines.append("")

    lines.append("## ツール別")
    lines.append("")
    for tool in sorted(by_tool, key=lambda k: -len(by_tool[k])):
        lines.append(f"### {tool}（{len(by_tool[tool])}件）")
        for c in by_tool[tool]:
            lines.append(f"- [{c['id']:03d} {c['title']}](./{c['filename']})")
        lines.append("")

    lines.append("## 全件（ID順）")
    lines.append("")
    for c in cards:
        lines.append(f"- [{c['id']:03d} {c['title']}](./{c['filename']}) — {', '.join(c['categories']) or '未分類'} / {', '.join(c['tools']) or '未指定'}")

    return "\n".join(lines) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    ap.add_argument("--out-dir", type=Path, default=CARDS_DIR)
    args = ap.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)

    cards_meta: list[dict] = []
    card_id = 0
    with args.csv.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("source_sheet") not in TARGET_SHEETS:
                continue
            if not (row.get("before") or row.get("after") or row.get("quant_effect")):
                continue
            card_id += 1
            filename, content = make_card(row, card_id)
            (args.out_dir / filename).write_text(content, encoding="utf-8")
            cats = parse_list_cell(row.get("category", ""))
            tools = parse_list_cell(row.get("tools", ""))
            cards_meta.append({
                "id": card_id,
                "filename": filename,
                "title": f"{tools[0] if tools else 'AI'} × {cats[0] if cats else '業務改善'}",
                "categories": cats,
                "tools": tools,
            })

    index_md = generate_index(cards_meta)
    (args.out_dir / "INDEX.md").write_text(index_md, encoding="utf-8")

    print(f"generated {len(cards_meta)} cards under {args.out_dir}")


if __name__ == "__main__":
    main()
