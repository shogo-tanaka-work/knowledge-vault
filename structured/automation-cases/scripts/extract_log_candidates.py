"""面談ログから2軍カード化候補（成功×80字以上）を抽出してJSONL化する。

出力:
  source/log_candidates.jsonl  ... 全候補（1行=1件）
  source/log_candidates_batch_NN.jsonl ... バッチ分割版（agent並列投入用）
"""
from __future__ import annotations

import csv
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT / "source" / "automation-cases.csv"
OUT_ALL = ROOT / "source" / "log_candidates.jsonl"
BATCH_DIR = ROOT / "source"
BATCH_SIZE = 110  # 654件 → 約6バッチ

MIN_CONTENT_LEN = 80
LOG_SHEETS = {"業務系の面談ログ_Gen", "業務系の面談ログ_Biz"}


def main() -> None:
    candidates: list[dict] = []
    with CSV_PATH.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["source_sheet"] not in LOG_SHEETS:
                continue
            if "成功" not in row["outcome"]:
                continue
            content = (row.get("qualitative_effect", "") + " " + row.get("notes", "")).strip()
            if len(content) < MIN_CONTENT_LEN:
                continue
            candidates.append({
                "id": row["id"],
                "sheet": row["source_sheet"],
                "row": row["source_row"],
                "category": row["category"],
                "tools": row["tools"],
                "outcome": row["outcome"],
                "qualitative": row.get("qualitative_effect", ""),
                "notes": row.get("notes", ""),
                "quant": row.get("quant_effect", ""),
            })

    with OUT_ALL.open("w", encoding="utf-8") as f:
        for c in candidates:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")

    n_batches = math.ceil(len(candidates) / BATCH_SIZE)
    for i in range(n_batches):
        chunk = candidates[i * BATCH_SIZE:(i + 1) * BATCH_SIZE]
        path = BATCH_DIR / f"log_candidates_batch_{i+1:02d}.jsonl"
        with path.open("w", encoding="utf-8") as f:
            for c in chunk:
                f.write(json.dumps(c, ensure_ascii=False) + "\n")

    print(f"total={len(candidates)} batches={n_batches} batch_size={BATCH_SIZE}")


if __name__ == "__main__":
    main()
