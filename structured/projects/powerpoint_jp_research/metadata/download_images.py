#!/usr/bin/env python3
"""image_map.json に基づき各記事の画像を images/{key}_{slug}/ にダウンロード"""
import json
import os
import re
import urllib.request
import urllib.error
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT = Path(__file__).resolve().parent.parent
IMG_MAP = ROOT / "metadata" / "image_map.json"
IMG_DIR = ROOT / "images"
IMG_DIR.mkdir(exist_ok=True)

with open(IMG_MAP) as f:
    M = json.load(f)


def fetch(url, dest):
    if dest.exists() and dest.stat().st_size > 0:
        return "skip", url
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
            data = r.read()
        dest.write_bytes(data)
        return "ok", url
    except Exception as e:
        return f"err:{e}", url


jobs = []
for key, v in M.items():
    folder = IMG_DIR / f"{key}_{v['slug']}"
    folder.mkdir(exist_ok=True)
    if v.get("eyecatch"):
        u = v["eyecatch"]
        fn = re.sub(r"\?.*", "", u.rsplit("/", 1)[-1])
        jobs.append((u, folder / f"_eyecatch_{fn}"))
    for u in v["image_urls"]:
        fn = re.sub(r"\?.*", "", u.rsplit("/", 1)[-1])
        jobs.append((u, folder / fn))

print(f"jobs: {len(jobs)}")
ok = skip = err = 0
with ThreadPoolExecutor(max_workers=8) as ex:
    futs = {ex.submit(fetch, u, d): (u, d) for u, d in jobs}
    for i, fu in enumerate(as_completed(futs), 1):
        st, u = fu.result()
        if st == "ok":
            ok += 1
        elif st == "skip":
            skip += 1
        else:
            err += 1
            print(st, u)
        if i % 200 == 0:
            print(f"{i}/{len(jobs)} ok={ok} skip={skip} err={err}")

print(f"DONE ok={ok} skip={skip} err={err}")
