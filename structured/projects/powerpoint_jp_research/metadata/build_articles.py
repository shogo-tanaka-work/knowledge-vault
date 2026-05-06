#!/usr/bin/env python3
"""articles_raw/*.json を articles/{key}_{slug}.md にmarkdown化"""
import json
import os
import re
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "metadata" / "articles_raw"
OUT = ROOT / "articles"
OUT.mkdir(exist_ok=True)


def slugify(name: str) -> str:
    s = re.sub(r"[【】「」（）\(\)\[\]『』、。・！？!?\s\-:：/／\\＼&＆#]+", "_", name)
    s = re.sub(r"_+", "_", s).strip("_")
    return s[:40]


class Md(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out = []
        self.image_urls = []
        self.in_strong = False
        self.in_h = None
        self.in_blockquote = False
        self.in_li = False
        self.in_a = None
        self.figcap_buf = None
        self.last_img_alt = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "p":
            pass
        elif tag in ("h1", "h2", "h3", "h4"):
            self.in_h = tag
        elif tag == "br":
            self.out.append("\n")
        elif tag == "strong":
            self.in_strong = True
            self.out.append("**")
        elif tag == "blockquote":
            self.in_blockquote = True
        elif tag == "li":
            self.in_li = True
            self.out.append("- ")
        elif tag == "a":
            self.in_a = a.get("href", "")
            self.out.append("[")
        elif tag == "img":
            src = a.get("src", "")
            alt = a.get("alt", "")
            if src:
                self.image_urls.append(src)
                fn = src.rsplit("/", 1)[-1].split("?")[0]
                self.out.append(f"\n![{alt}](../images/__KEY__/{fn})\n")
                self.last_img_alt = alt
        elif tag == "figcaption":
            self.figcap_buf = []

    def handle_endtag(self, tag):
        if tag == "p":
            self.out.append("\n\n")
        elif tag in ("h1", "h2", "h3", "h4"):
            self.out.insert(-1 if False else len(self.out), "")
            level = int(tag[1])
            text = "".join(self.out[-1:]) if self.out else ""
            # simpler: prepend later
            self.in_h = None
            self.out.append("\n\n")
        elif tag == "strong":
            self.in_strong = False
            self.out.append("**")
        elif tag == "blockquote":
            self.in_blockquote = False
            self.out.append("\n\n")
        elif tag == "li":
            self.in_li = False
            self.out.append("\n")
        elif tag == "a":
            href = self.in_a or ""
            self.in_a = None
            self.out.append(f"]({href})")
        elif tag == "figcaption":
            cap = "".join(self.figcap_buf or []).strip()
            self.figcap_buf = None
            if cap:
                self.out.append(f"*{cap}*\n\n")

    def handle_data(self, data):
        if self.figcap_buf is not None:
            self.figcap_buf.append(data)
            return
        if self.in_h:
            level = int(self.in_h[1])
            self.out.append(f"\n{'#' * level} {data}\n")
            return
        if self.in_blockquote:
            self.out.append(f"> {data}")
            return
        self.out.append(data)


def html_to_md(html: str):
    p = Md()
    p.feed(html or "")
    md = "".join(p.out)
    md = re.sub(r"\n{3,}", "\n\n", md)
    return md, p.image_urls


def process(jp):
    with open(jp) as f:
        d = json.load(f)["data"]
    key = d["key"]
    name = d.get("name") or ""
    body = d.get("body") or ""
    md_body, imgs = html_to_md(body)
    md_body = md_body.replace("__KEY__", f"{key}_{slugify(name)}")
    hashtags = [h["hashtag"]["name"] for h in d.get("hashtags") or []]
    note_url = f"https://note.com/powerpoint_jp/n/{key}"
    eyecatch = d.get("eyecatch") or ""
    md = f"""---
key: {key}
title: {name}
url: {note_url}
publishAt: {d.get('publishAt') or ''}
likeCount: {d.get('like_count') or 0}
hashtags: {hashtags}
eyecatch: {eyecatch}
image_count: {len(imgs)}
---

# {name}

[note原文]({note_url})

{md_body}
"""
    fn = OUT / f"{key}_{slugify(name)}.md"
    fn.write_text(md, encoding="utf-8")
    return key, slugify(name), imgs, eyecatch


if __name__ == "__main__":
    image_map = {}
    for jp in sorted(RAW.glob("*.json")):
        try:
            key, slug, imgs, eyecatch = process(jp)
            image_map[key] = {"slug": slug, "eyecatch": eyecatch, "image_urls": imgs}
        except Exception as e:
            print(f"ERR {jp.name}: {e}")
    out = ROOT / "metadata" / "image_map.json"
    out.write_text(json.dumps(image_map, ensure_ascii=False, indent=2))
    print(f"articles: {len(image_map)}, total images: {sum(len(v['image_urls']) for v in image_map.values())}")
