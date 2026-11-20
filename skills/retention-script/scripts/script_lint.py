#!/usr/bin/env python3
"""Lint a spoken video script for retention problems before anyone records it.

Script format (markdown):
  ## Block title          a block; every heading counts as a pattern reset
  [b-roll: clamp slips]   a direction line in square brackets; not spoken, also counts as a reset
  [payoff]                mark the first concrete payoff (checked against the midpoint)
  Spoken text ... [c3]    claim tags [c1], [c2] point to rows in the claims register

Checks:
  BLOCK  the first spoken line is a throat-clear ("welcome back", "in this video", "hey guys" ...)
  BLOCK  a claim tag points to an id that is not in --claims
  WARN   no question or promise in the first two sentences (the viewer must know the question by 0:05)
  WARN   a sentence longer than --max-words (default 20): write for the ear
  WARN   weak transitions ("next", "moving on", "also", "another thing"): use so / but / which means
  WARN   a stretch longer than --reset seconds (default 90) with no heading or direction line
  WARN   no [payoff] before the midpoint (only when the script uses [payoff])
  WARN   outro filler in the last 15% ("thanks for watching", "like and subscribe" ...)
  WARN   a sentence with a number and no claim tag
  WARN   estimated length more than 10% off --target

Length is words / --wpm. Measure your own rate on a real take (words / minutes) and pass it;
150 is only a starting guess, and voices differ by a lot.

Usage:
  python script_lint.py examples/script.md --wpm 160 --target 420 --claims examples/claims-register.md
  python script_lint.py script.md --format json

Exit codes: 0 no blockers, 1 blockers found, 2 file error.
"""
import argparse
import json
import re
import sys

OPENERS = ["welcome back", "welcome to", "hey guys", "hi guys", "hello everyone", "what's up", "whats up", "in this video",
           "today we're going to", "today i'm going to", "before we start", "before we get started", "don't forget to subscribe",
           "make sure to subscribe", "my name is"]
WEAK = re.compile(r"^(next|moving on|also|another thing|now let's|now lets|okay so|ok so|alright)\b", re.I)
OUTRO = ["thanks for watching", "thank you for watching", "like and subscribe", "smash that", "hit the bell", "see you next time",
         "see you in the next", "that's it for today", "that's all for today"]
TAG = re.compile(r"\[(c\d+)\]", re.I)


def sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]


def mmss(s):
    s = int(round(s))
    return f"{s // 60}:{s % 60:02d}"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file")
    ap.add_argument("--wpm", type=float, default=150, help="measured words per minute of the voice (default 150, a guess)")
    ap.add_argument("--target", type=float, help="target length in seconds")
    ap.add_argument("--max-words", type=int, default=20)
    ap.add_argument("--reset", type=float, default=90, help="max seconds without a heading or direction line (default 90)")
    ap.add_argument("--claims", help="claims register markdown; ids like c1 in the first column")
    ap.add_argument("--format", choices=["md", "json"], default="md")
    a = ap.parse_args()
    try:
        lines = open(a.file, encoding="utf-8").read().splitlines()
    except OSError as e:
        print(e, file=sys.stderr)
        sys.exit(2)

    wps = a.wpm / 60
    blocks, events, spoken_all = [], [], []   # events: (kind, word_offset, text)
    words_so_far, cur = 0, {"title": "(before first heading)", "start": 0, "words": 0}
    for line in lines:
        s = line.strip()
        if not s or s.startswith("<!--") or s.startswith("# "):
            continue
        if s.startswith("## "):
            if cur["words"] or cur["title"] != "(before first heading)":
                blocks.append(cur)
            cur = {"title": s[3:].strip(), "start": words_so_far, "words": 0}
            events.append(("reset", words_so_far, s))
            continue
        if re.fullmatch(r"\[[^\]]+\]", s) and not TAG.fullmatch(s):
            events.append(("payoff" if s.lower() == "[payoff]" else "reset", words_so_far, s))
            continue
        text = re.sub(r"\[[^\]]*\]", lambda m: m.group(0) if TAG.fullmatch(m.group(0)) else "", s)
        for sent in sentences(text):
            n = len(TAG.sub("", sent).split())
            spoken_all.append((words_so_far, sent))
            words_so_far += n
            cur["words"] += n
    blocks.append(cur)
    total = words_so_far
    secs = total / wps if wps else 0
    issues = []

    def add(level, msg):
        issues.append({"level": level, "msg": msg})

    if not spoken_all:
        print("no spoken text found", file=sys.stderr)
        sys.exit(2)
    first = TAG.sub("", spoken_all[0][1]).lower()
    for o in OPENERS:
        if o in first:
            add("BLOCK", f"first line opens with '{o}': start on the promise instead (\"{spoken_all[0][1][:80]}\")")
            break
    head = " ".join(s for _, s in spoken_all[:2]).lower()
    if "?" not in head and not re.search(r"\b(why|how|what|here's|this is the|the reason|you'll|by the end)\b", head):
        add("WARN", "no question or promise in the first two sentences")
    for off, s in spoken_all:
        n = len(TAG.sub("", s).split())
        if n > a.max_words:
            add("WARN", f"{mmss(off / wps)} long sentence ({n} words): \"{s[:70]}...\"")
        if WEAK.match(s):
            add("WARN", f"{mmss(off / wps)} weak transition: \"{s[:60]}\" (try so / but / which means)")
        if re.search(r"\d", TAG.sub("", s)) and not TAG.search(s) and not re.search(r"\b\d{1,2}:\d{2}\b", s):
            add("WARN", f"{mmss(off / wps)} number without a claim tag: \"{s[:70]}\"")
    marks = sorted(o for k, o, _ in events) + [total]
    prev = 0
    for m in marks:
        gap = (m - prev) / wps
        if gap > a.reset:
            add("WARN", f"{mmss(prev / wps)} to {mmss(m / wps)}: {gap:.0f} s with no reset (heading or [direction])")
        prev = max(prev, m)
    payoffs = [o for k, o, _ in events if k == "payoff"]
    if payoffs and payoffs[0] > total / 2:
        add("WARN", f"first [payoff] at {mmss(payoffs[0] / wps)}, after the midpoint {mmss(secs / 2)}")
    elif not payoffs:
        add("INFO", "mark the first concrete payoff with [payoff] to check it lands before the midpoint")
    tail = " ".join(s for o, s in spoken_all if o >= total * 0.85).lower()
    for o in OUTRO:
        if o in tail:
            add("WARN", f"outro filler in the last 15%: '{o}'. End on the takeaway and the next question")
    if a.target:
        off = (secs - a.target) / a.target
        if abs(off) > 0.10:
            add("WARN", f"estimated {mmss(secs)} vs target {mmss(a.target)} ({off:+.0%}); cut or add, never pad")
    if a.claims:
        reg = set(m.lower() for m in re.findall(r"^\|\s*(c\d+)\s*\|", open(a.claims, encoding="utf-8").read(), re.M | re.I))
        used = {t.lower() for _, s in spoken_all for t in TAG.findall(s)}
        for t in sorted(used - reg):
            add("BLOCK", f"claim tag [{t}] has no row in {a.claims}")
        for t in sorted(reg - used):
            add("INFO", f"register row {t} is not used in the script")

    out = {"words": total, "wpm": a.wpm, "estimated": mmss(secs),
           "blocks": [{"title": b["title"], "start": mmss(b["start"] / wps), "seconds": round(b["words"] / wps)} for b in blocks],
           "issues": issues}
    if a.format == "json":
        print(json.dumps(out, indent=1, ensure_ascii=False))
    else:
        print(f"{total} words at {a.wpm:g} wpm = about {mmss(secs)}\n")
        print("| start | block | seconds |\n|---|---|---|")
        for b in out["blocks"]:
            print(f"| {b['start']} | {b['title']} | {b['seconds']} |")
        print()
        for lvl in ("BLOCK", "WARN", "INFO"):
            for i in issues:
                if i["level"] == lvl:
                    print(f"{lvl:5}  {i['msg']}")
        if not issues:
            print("no issues")
    sys.exit(1 if any(i["level"] == "BLOCK" for i in issues) else 0)


if __name__ == "__main__":
    main()
