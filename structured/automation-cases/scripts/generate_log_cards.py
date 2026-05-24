"""verdict_batch_*.jsonl の YES 判定を元に、面談ログ由来の2軍カードを生成する。

入力:
  source/log_candidates.jsonl
  source/verdict_batch_*.jsonl
出力:
  cards/log/log-NNN-<tool>-<category>.md
  cards/log/INDEX.md
"""
from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "source"
OUT_DIR = ROOT / "cards" / "log"


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


def main() -> None:
    candidates = {}
    with (SRC / "log_candidates.jsonl").open(encoding="utf-8") as f:
        for line in f:
            row = json.loads(line)
            candidates[row["id"]] = row

    verdicts = {}
    for vp in sorted(SRC.glob("verdict_batch_*.jsonl")):
        with vp.open(encoding="utf-8") as f:
            for line in f:
                v = json.loads(line)
                verdicts[v["id"]] = v

    yes_ids = [vid for vid, v in verdicts.items() if v["decision"] == "YES"]
    yes_ids.sort()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    # 既存の log-*.md をクリーンアップ
    for old in OUT_DIR.glob("log-*.md"):
        old.unlink()

    meta_list = []
    for idx, src_id in enumerate(yes_ids, start=1):
        cand = candidates.get(src_id)
        vd = verdicts[src_id]
        if not cand:
            continue
        categories = parse_list_cell(cand.get("category", ""))
        tools = parse_list_cell(cand.get("tools", ""))
        primary_tool = vd.get("primary_tool") or (tools[0] if tools else "AI")
        primary_cat = vd.get("primary_category") or (categories[0] if categories else "業務改善")
        slug = slugify(f"{primary_tool}-{primary_cat}")
        filename = f"log-{idx:03d}-{slug}.md"

        summary = vd.get("summary", "").strip()
        quant = cand.get("quant", "").strip()
        qualitative = cand.get("qualitative", "").strip()
        notes = cand.get("notes", "").strip()

        title = summary or f"{primary_tool}による{primary_cat}"

        front_matter = "\n".join([
            "---",
            f"id: log-{idx:03d}",
            f"tier: 2",
            f"category: {render_yaml_list(categories)}",
            f"tools: {render_yaml_list(tools)}",
            f'primary_tool: "{primary_tool}"',
            f'primary_category: "{primary_cat}"',
            f'quant_effect: "{quant}"',
            f'source_sheet: {cand.get("sheet", "")}',
            f'source_row: {cand.get("row", "")}',
            f'source_csv_id: {src_id}',
            "published_axes: []  # TODO",
            "---",
        ])

        body = f"""
# {title}

> ⚠ 2軍カード。元データは面談メモのため Before/After 列はなし。
> 講師所感と定性効果から再構成し、発信時に汎化済み Before/After を起こすこと。

## AI判定サマリ
- 判定理由: {vd.get('reason', '')}
- 一行サマリ: {summary or '(なし)'}

## 定量効果

{quant or '(記載なし)'}

## 定性効果（元データ）

{qualitative or '(記載なし)'}

## 特記事項・講師所感（元データ）

{notes or '(記載なし)'}

## 業務課題カテゴリ

{', '.join(categories) or '未分類'}

## 使用AIツール

{', '.join(tools) or '未指定'}

## 汎用化Tips

<!-- TODO -->

## 発信角度の候補

<!-- TODO: note / X / Threads / LinkedIn / 技術ブログ -->
"""

        (OUT_DIR / filename).write_text(front_matter + body, encoding="utf-8")
        meta_list.append({
            "id": f"log-{idx:03d}",
            "filename": filename,
            "title": title[:60],
            "primary_tool": primary_tool,
            "primary_category": primary_cat,
            "categories": categories,
            "tools": tools,
        })

    # INDEX 生成
    lines = [
        "# 自動化事例カード（2軍：面談ログ由来） INDEX",
        "",
        f"合計 {len(meta_list)} 件（AI評価で YES と判定された面談ログ）",
        "",
        "1軍カードは ../INDEX.md を参照。",
        "",
        "## 主要ツール別",
        "",
    ]
    by_tool: dict[str, list[dict]] = defaultdict(list)
    by_cat: dict[str, list[dict]] = defaultdict(list)
    for m in meta_list:
        by_tool[m["primary_tool"]].append(m)
        by_cat[m["primary_category"]].append(m)

    for tool in sorted(by_tool, key=lambda k: -len(by_tool[k])):
        lines.append(f"### {tool}（{len(by_tool[tool])}件）")
        for m in by_tool[tool]:
            lines.append(f"- [{m['id']} {m['title']}](./{m['filename']})")
        lines.append("")

    lines.append("## 主要カテゴリ別")
    lines.append("")
    for cat in sorted(by_cat, key=lambda k: -len(by_cat[k])):
        lines.append(f"### {cat}（{len(by_cat[cat])}件）")
        for m in by_cat[cat]:
            lines.append(f"- [{m['id']} {m['title']}](./{m['filename']})")
        lines.append("")

    (OUT_DIR / "INDEX.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"generated {len(meta_list)} tier-2 cards under {OUT_DIR}")


if __name__ == "__main__":
    main()
