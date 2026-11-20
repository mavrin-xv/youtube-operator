#!/usr/bin/env python3
"""Score YouTube title drafts against packaging rules. A lint, not a CTR prediction.

The score says whether a title breaks known rules (too long, buried keyword, hype words,
caps, thumbnail repeating the title). It cannot say which title viewers will pick; only
YouTube's Test & Compare (decided on watch time share) can. Use it to drop the weak drafts
before you spend a test slot on them.

Points (100):
  length          15  30-60 chars best; mobile cuts near 60; hard fail above 100 (YouTube limit)
  front-loaded    15  every word of --keyword inside the first 40 chars (search videos)
  concrete        10  a number, a price, a measurement or a named object count
  plain language  20  minus 10 per hype or bait phrase ("ultimate", "nobody tells you", ...)
  no exclamation  10
  no shouting     10  no ALL-CAPS word longer than 4 letters (acronyms are fine)
  word count      10  4 to 10 words
  thumbnail text  10  0 to 4 words; for --surface browse it must not repeat title words

Usage:
  python title_score.py "Why Your Tabletop Cupped" "The ULTIMATE Guide to Wood Movement!!" --keyword "tabletop cupped"
  python title_score.py --file titles.txt --keyword "tabletop" --thumb "3 FIXES" --surface search
  python title_score.py "..." --format json

Exit codes: 0 ok, 1 at least one title over 100 characters or containing < or >.
"""
import argparse
import json
import re
import sys

BAIT = ["ultimate", "insane", "nobody tells you", "no one tells you", "you won't believe", "mind-blowing", "mind blowing",
        "shocking", "secret", "hack", "hacks", "game changer", "game-changer", "must watch", "must-watch", "best ever",
        "crazy", "epic", "unbelievable", "gone wrong", "life-changing", "everything you need to know", "will blow your mind"]
VAGUE = ["things", "stuff", "everything", "tips and tricks", "some tips"]
STOP = set("a an the and or of to in on for with my your you i is are why how what this that it at by from vs".split())


def content_words(s):
    return {w for w in re.findall(r"[a-z0-9$]+", s.lower()) if w not in STOP}


def score(title, keyword, thumb, surface):
    t = title.strip()
    low = t.lower()
    checks, fatal = [], []
    n = len(t)
    if n > 100:
        fatal.append(f"{n} chars, YouTube allows 100")
    if "<" in t or ">" in t:
        fatal.append("contains < or >, YouTube rejects them in titles")
    pts = 15 if 30 <= n <= 60 else 10 if 61 <= n <= 70 else 8 if n < 30 else 4
    checks.append(("length", pts, 15, f"{n} chars" + ("" if n <= 60 else f"; mobile shows about: \"{t[:57]}...\"")))
    if keyword:
        kws = keyword.lower().split()
        head = low[:40]
        if all(k in head for k in kws):
            checks.append(("front-loaded", 15, 15, f"'{keyword}' in first 40 chars"))
        elif all(k in low for k in kws):
            checks.append(("front-loaded", 7, 15, f"'{keyword}' present but after char 40"))
        else:
            checks.append(("front-loaded", 0, 15, f"'{keyword}' missing"))
    else:
        checks.append(("front-loaded", 10, 15, "no --keyword given; for search videos pass the viewer's phrase"))
    concrete = re.search(r"\d|\$|£|€|\b(one|two|three|four|five|six|seven|eight|nine|ten)\b", low)
    checks.append(("concrete", 10 if concrete else 0, 10, "has a number or price" if concrete else "no number, price or count"))
    hits = [b for b in BAIT if re.search(r"(?<![a-z])" + re.escape(b) + r"(?![a-z])", low)]
    vague = [v for v in VAGUE if re.search(r"\b" + re.escape(v) + r"\b", low)]
    plain = max(0, 20 - 10 * len(hits) - 5 * len(vague))
    checks.append(("plain language", plain, 20, ("bait: " + ", ".join(hits) if hits else "no bait words") +
                   ("; vague: " + ", ".join(vague) if vague else "")))
    checks.append(("no exclamation", 0 if "!" in t else 10, 10, "has '!'" if "!" in t else "ok"))
    caps = [w for w in re.findall(r"\b[A-Z]{5,}\b", t)]
    checks.append(("no shouting", 0 if caps else 10, 10, "caps: " + ", ".join(caps) if caps else "ok"))
    wc = len(t.split())
    checks.append(("word count", 10 if 4 <= wc <= 10 else 5, 10, f"{wc} words"))
    if thumb is None:
        checks.append(("thumbnail text", 5, 10, "no --thumb given; plan 0-4 words of thumbnail text with the title"))
    else:
        tw = len(thumb.split())
        overlap = content_words(thumb) & content_words(t)
        p = 10 if tw <= 4 else 3
        note = f"{tw} words"
        if surface == "browse" and overlap:
            p = min(p, 3)
            note += f"; repeats title words {sorted(overlap)} (browse: the thumbnail should tell the other half)"
        elif overlap:
            note += "; repeats the topic noun, fine for search"
        checks.append(("thumbnail text", p, 10, note))
    notes = []
    if t.endswith("?") and surface == "browse":
        notes.append("question title: no built-in advantage; keep it only if it is what the viewer types")
    return {"title": t, "score": sum(c[1] for c in checks), "fatal": fatal,
            "checks": [{"check": c[0], "points": c[1], "max": c[2], "note": c[3]} for c in checks], "notes": notes}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("titles", nargs="*")
    ap.add_argument("--file", help="one title per line")
    ap.add_argument("--keyword", help="the viewer's search phrase, for search videos")
    ap.add_argument("--thumb", help="planned thumbnail text")
    ap.add_argument("--surface", choices=["search", "browse"], default="search", help="where most views will come from")
    ap.add_argument("--format", choices=["md", "json"], default="md")
    a = ap.parse_args()
    titles = list(a.titles)
    if a.file:
        with open(a.file, encoding="utf-8") as f:
            titles += [l.strip() for l in f if l.strip() and not l.startswith("#")]
    if not titles:
        ap.error("give at least one title")
    res = sorted((score(t, a.keyword, a.thumb, a.surface) for t in titles), key=lambda r: (bool(r["fatal"]), -r["score"]))
    if a.format == "json":
        print(json.dumps(res, indent=1, ensure_ascii=False))
    else:
        for i, r in enumerate(res, 1):
            status = "FAIL " + "; ".join(r["fatal"]) if r["fatal"] else f"{r['score']}/100"
            print(f"{i}. {status}  {r['title']}")
            for c in r["checks"]:
                if c["points"] < c["max"]:
                    print(f"     -{c['max'] - c['points']:>2}  {c['check']}: {c['note']}")
            for n in r["notes"]:
                print(f"     note: {n}")
        print("\nA lint, not a prediction. Put the top 2 or 3 into Test & Compare; watch time share picks the winner.")
    sys.exit(1 if any(r["fatal"] for r in res) else 0)


if __name__ == "__main__":
    main()
