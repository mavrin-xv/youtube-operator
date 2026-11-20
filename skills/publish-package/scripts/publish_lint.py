#!/usr/bin/env python3
"""Check a YouTube publish package against the platform limits before you press publish.

BLOCK (exit 1):
  title empty, over 100 characters, or containing < or >
  description over 5000 bytes, or containing < or >
  tags over 500 characters in total (YouTube counts quotes around tags with spaces)
  more than 15 hashtags (YouTube then ignores all of them)
  chapters that break YouTube's rules: first must be 00:00, at least 3, each at least 10 s,
  in order, and inside the video length
  a placeholder left in (TODO, TBD, XXX, [link], {{...}}, lorem)
  thumbnail smaller than 1280x720, not about 16:9, or over 2 MB
WARN:
  more than 3 hashtags (only the first 3 show above the title)
  an owned link without utm_source (pass your domains with --owned)
  the first 150 characters of the description do not repeat a title word
  no chapters on a video longer than 5 minutes

Builder mode: --chapters-from FILE turns "M:SS Title" lines (or a script_lint json) into a
chapter block you can paste.

Usage:
  python publish_lint.py --title "..." --description desc.md --tags "a,b,c" --duration 7:05 --thumb thumb.png --owned example.com
  python publish_lint.py --chapters-from chapters.txt --duration 7:05

Exit codes: 0 ok, 1 blockers, 2 file error.
"""
import argparse
import json
import os
import re
import struct
import sys

TS = re.compile(r"^\s*((?:\d{1,2}:)?\d{1,2}:\d{2})\s+[-:|]?\s*(.+?)\s*$")
PLACEHOLDER = re.compile(r"\b(TODO|TBD|XXX|lorem ipsum)\b|\[link\]|\{\{[^}]*\}\}", re.I)
URL = re.compile(r"https?://[^\s)>\]]+", re.I)


def secs(t):
    p = [int(x) for x in t.split(":")]
    return p[0] * 3600 + p[1] * 60 + p[2] if len(p) == 3 else p[0] * 60 + p[1]


def fmt(s):
    s = int(s)
    return f"{s // 3600}:{s % 3600 // 60:02d}:{s % 60:02d}" if s >= 3600 else f"{s // 60:02d}:{s % 60:02d}"


def image_size(path):
    with open(path, "rb") as f:
        head = f.read(26)
        if head[:8] == b"\x89PNG\r\n\x1a\n":
            return struct.unpack(">II", head[16:24])
        if head[:2] == b"\xff\xd8":
            f.seek(2)
            while True:
                b = f.read(1)
                while b and b != b"\xff":
                    b = f.read(1)
                while b == b"\xff":
                    b = f.read(1)
                if not b:
                    return None
                if b[0] in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                    f.read(3)
                    h, w = struct.unpack(">HH", f.read(4))
                    return w, h
                ln = struct.unpack(">H", f.read(2))[0]
                f.read(ln - 2)
    return None


def chapters(text):
    return [(secs(m.group(1)), m.group(2)) for m in (TS.match(l) for l in text.splitlines()) if m]


def check_chapters(ch, duration, add):
    if not ch:
        return
    if ch[0][0] != 0:
        add("BLOCK", f"first chapter starts at {fmt(ch[0][0])}; YouTube needs 00:00")
    if len(ch) < 3:
        add("BLOCK", f"{len(ch)} chapters; YouTube needs at least 3")
    for (t1, n1), (t2, _) in zip(ch, ch[1:]):
        if t2 <= t1:
            add("BLOCK", f"chapter '{n1}' is out of order")
        elif t2 - t1 < 10:
            add("BLOCK", f"chapter '{n1}' is {t2 - t1} s; each must be at least 10 s")
    if duration:
        if ch[-1][0] >= duration:
            add("BLOCK", f"last chapter {fmt(ch[-1][0])} is past the video length {fmt(duration)}")
        elif duration - ch[-1][0] < 10:
            add("BLOCK", f"last chapter is {duration - ch[-1][0]} s; each must be at least 10 s")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--title")
    ap.add_argument("--description", help="description file (plain text or markdown)")
    ap.add_argument("--tags", default="", help="comma-separated tags")
    ap.add_argument("--duration", help="video length M:SS or H:MM:SS")
    ap.add_argument("--thumb", help="thumbnail PNG or JPEG")
    ap.add_argument("--owned", default="", help="comma-separated domains you own; their links need utm_source")
    ap.add_argument("--chapters-from", help="builder mode: file with 'M:SS Title' lines or script_lint --format json output")
    ap.add_argument("--format", choices=["md", "json"], default="md")
    a = ap.parse_args()
    duration = secs(a.duration) if a.duration else None
    issues = []

    def add(level, msg):
        issues.append({"level": level, "msg": msg})

    if a.chapters_from:
        raw = open(a.chapters_from, encoding="utf-8").read()
        try:
            ch = [(secs(b["start"]), b["title"]) for b in json.loads(raw)["blocks"]]
        except (ValueError, KeyError, TypeError):
            ch = chapters(raw)
        if ch and ch[0][0] != 0:
            ch[0] = (0, ch[0][1])
        merged = []
        for t, n in ch:   # fold chapters under 10 s into the previous one
            if merged and t - merged[-1][0] < 10:
                continue
            merged.append((t, n))
        check_chapters(merged, duration, add)
        print("\n".join(f"{fmt(t)} {n}" for t, n in merged))
        for i in issues:
            print(f"{i['level']:5}  {i['msg']}", file=sys.stderr)
        sys.exit(1 if any(i["level"] == "BLOCK" for i in issues) else 0)

    if not a.title:
        ap.error("--title is required (or use --chapters-from)")
    t = a.title.strip()
    if not t:
        add("BLOCK", "title is empty")
    if len(t) > 100:
        add("BLOCK", f"title is {len(t)} characters; the limit is 100")
    if "<" in t or ">" in t:
        add("BLOCK", "title contains < or >")
    desc = ""
    if a.description:
        try:
            desc = open(a.description, encoding="utf-8").read()
        except OSError as e:
            print(e, file=sys.stderr)
            sys.exit(2)
        nb = len(desc.encode("utf-8"))
        if nb > 5000:
            add("BLOCK", f"description is {nb} bytes; the limit is 5000")
        if "<" in desc or ">" in desc:
            add("BLOCK", "description contains < or >")
        m = PLACEHOLDER.search(desc)
        if m:
            add("BLOCK", f"placeholder left in the description: '{m.group(0)}'")
        tags_h = re.findall(r"(?<![\w/#])#[A-Za-z][\w]*", desc)
        if len(tags_h) > 15:
            add("BLOCK", f"{len(tags_h)} hashtags; above 15 YouTube ignores all of them")
        elif len(tags_h) > 3:
            add("WARN", f"{len(tags_h)} hashtags; only the first 3 show above the title")
        title_words = {w for w in re.findall(r"[a-z]{4,}", t.lower())}
        if title_words and not title_words & set(re.findall(r"[a-z]{4,}", desc[:150].lower())):
            add("WARN", "the first 150 characters of the description share no word with the title (that text shows in search)")
        owned = [d.strip().lower() for d in a.owned.split(",") if d.strip()]
        for u in URL.findall(desc):
            if any(d in u.lower() for d in owned) and "utm_source=" not in u:
                add("WARN", f"owned link without utm_source: {u}")
        ch = chapters(desc)
        check_chapters(ch, duration, add)
        if not ch and duration and duration > 300:
            add("WARN", "no chapters on a video over 5 minutes")
    tags = [x.strip() for x in a.tags.split(",") if x.strip()]
    tag_len = sum(len(x) + (2 if " " in x else 0) for x in tags) + max(0, len(tags) - 1)
    if tag_len > 500:
        add("BLOCK", f"tags are {tag_len} characters; the limit is 500")
    if a.thumb:
        try:
            size = image_size(a.thumb)
            mb = os.path.getsize(a.thumb) / 1024 / 1024
        except OSError as e:
            print(e, file=sys.stderr)
            sys.exit(2)
        if not size:
            add("BLOCK", "thumbnail is not a readable PNG or JPEG")
        else:
            w, h = size
            if w < 1280 or h < 720:
                add("BLOCK", f"thumbnail is {w}x{h}; use at least 1280x720")
            if abs(w / h - 16 / 9) > 0.02:
                add("BLOCK", f"thumbnail ratio {w / h:.2f}; use 16:9")
        if mb > 2:
            add("BLOCK", f"thumbnail is {mb:.1f} MB; the limit is 2 MB")
    out = {"title_chars": len(t), "description_bytes": len(desc.encode("utf-8")), "tags_chars": tag_len, "issues": issues}
    if a.format == "json":
        print(json.dumps(out, indent=1))
    else:
        print(f"title {len(t)}/100 chars, description {out['description_bytes']}/5000 bytes, tags {tag_len}/500 chars")
        for lvl in ("BLOCK", "WARN"):
            for i in issues:
                if i["level"] == lvl:
                    print(f"{lvl:5}  {i['msg']}")
        if not issues:
            print("package passes the platform checks; now run the human checklist")
    sys.exit(1 if any(i["level"] == "BLOCK" for i in issues) else 0)


if __name__ == "__main__":
    main()
