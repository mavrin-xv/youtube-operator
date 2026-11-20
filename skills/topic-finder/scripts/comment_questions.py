#!/usr/bin/env python3
"""Turn video comments into grouped viewer questions: the most direct demand signal there is.

Keeps comments that ask something, drops praise and spam, groups questions that share
the same content words, and prints each group with its size, total likes and the
clearest comment quoted word for word. One group can become one video.

Input (pick one):
  --file comments.json   a list of strings, a list of {"text", "likes"} objects, or a raw
                         YouTube commentThreads.list response (or a list of them)
  --video VIDEO_ID       live pull via YouTube Data API v3, 1 quota unit per 100 threads,
                         key from env YOUTUBE_API_KEY

Usage:
  python comment_questions.py --file examples/data/comments.json
  python comment_questions.py --video abc123xyz00 --max 500 --save comments.json
  python comment_questions.py --file c.json --min-group 2 --format json

Env: YOUTUBE_API_KEY (only for --video). Exit codes: 0 ok, 1 no questions found, 2 error.
"""
import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

QWORDS = r"(how|why|what|which|where|when|who|can|could|does|do|did|is|are|should|would|will|any|anyone)"
PRAISE = re.compile(r"^(great|awesome|amazing|nice|love|thanks|thank you|first|wow|cool|beautiful)\b[^?]*$", re.I)
SPAM = re.compile(r"https?://|whatsapp|telegram|t\.me/|crypto|investment|\bdm me\b|check my channel", re.I)
STOP = set("""a an the and or but if of to in on at for with from by about as is are was were be been being do does did
can could should would will shall may might must i you he she it we they me my your our their this that these those
what which who whom whose why how when where there here any anyone anybody some just really very so too also than then
not no yes have has had get got make made use used using one thing things video videos please know way much many more
does don't doesn't isn't can't im i'm you're it's thats that's like would've want need""".split())


def fetch(video, key, limit):
    out, token = [], None
    while len(out) < limit:
        p = {"part": "snippet", "videoId": video, "maxResults": 100, "order": "relevance", "textFormat": "plainText", "key": key}
        if token:
            p["pageToken"] = token
        url = "https://www.googleapis.com/youtube/v3/commentThreads?" + urllib.parse.urlencode(p)
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                page = json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            sys.exit(f"API error {e.code}: comments may be disabled, or the key lacks YouTube Data API v3")
        out.append(page)
        token = page.get("nextPageToken")
        if not token:
            break
    return out


def normalise(data):
    pages = data if isinstance(data, list) and data and isinstance(data[0], dict) and "items" in data[0] else None
    if isinstance(data, dict) and "items" in data:
        pages = [data]
    if pages:
        res = []
        for pg in pages:
            for it in pg.get("items", []):
                s = it["snippet"]["topLevelComment"]["snippet"]
                res.append({"text": s.get("textDisplay") or s.get("textOriginal", ""), "likes": int(s.get("likeCount", 0))})
        return res
    return [{"text": c, "likes": 0} if isinstance(c, str) else {"text": c.get("text", ""), "likes": int(c.get("likes", 0))}
            for c in data]


def is_question(t):
    t = t.strip()
    if "?" in t:
        return True
    return bool(re.match(QWORDS + r"\b", t, re.I)) and len(t.split()) >= 4


def stem(w):
    for suf in ("ing", "ed", "es", "s"):
        if w.endswith(suf) and len(w) - len(suf) >= 3:
            w = w[: -len(suf)]
            break
    if len(w) > 3 and w[-1] == w[-2] and w[-1] not in "lseo":   # cupp -> cup, but keep "all", "glass", "coffee"
        w = w[:-1]
    return w


def keywords(t):
    words = re.findall(r"[a-z][a-z'\-]+", t.lower())
    return {stem(w) for w in words if w not in STOP and len(w) > 2}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--file")
    g.add_argument("--video")
    ap.add_argument("--max", type=int, default=300, help="comment threads to pull with --video (default 300)")
    ap.add_argument("--save", help="save the raw pull to this file")
    ap.add_argument("--min-group", type=int, default=1, help="hide groups smaller than this (default 1)")
    ap.add_argument("--overlap", type=float, default=0.3, help="keyword overlap to join a group, 0..1 (default 0.3)")
    ap.add_argument("--format", choices=["md", "json"], default="md")
    a = ap.parse_args()

    if a.video:
        key = os.environ.get("YOUTUBE_API_KEY") or sys.exit("YOUTUBE_API_KEY is not set")
        data = fetch(a.video, key, a.max)
    else:
        with open(a.file, encoding="utf-8") as f:
            data = json.load(f)
    if a.save:
        with open(a.save, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=1, ensure_ascii=False)

    comments = normalise(data)
    kept = [c for c in comments if not SPAM.search(c["text"]) and not PRAISE.match(c["text"].strip()) and is_question(c["text"])]
    groups = []
    for c in sorted(kept, key=lambda x: -x["likes"]):
        kw = keywords(c["text"])
        best, score = None, 0.0
        for gr in groups:
            inter = len(kw & gr["kw"])
            s = inter / max(1, min(len(kw), len(gr["kw"])))
            if inter >= 2 and s > score:
                best, score = gr, s
        if best and score >= a.overlap:
            best["items"].append(c)
            best["kw"] |= kw
        else:
            groups.append({"kw": set(kw), "items": [c]})
    groups = [gr for gr in groups if len(gr["items"]) >= a.min_group]
    groups.sort(key=lambda gr: (-len(gr["items"]), -sum(i["likes"] for i in gr["items"])))
    if not groups:
        print(f"{len(comments)} comments, no questions found.", file=sys.stderr)
        sys.exit(1)

    if a.format == "json":
        print(json.dumps([{"size": len(gr["items"]), "likes": sum(i["likes"] for i in gr["items"]),
                           "quote": gr["items"][0]["text"], "keywords": sorted(gr["kw"])[:12],
                           "all": [i["text"] for i in gr["items"]]} for gr in groups], indent=1, ensure_ascii=False))
        return
    print(f"{len(comments)} comments, {len(kept)} questions, {len(groups)} group(s)\n")
    for i, gr in enumerate(groups, 1):
        common = sorted(gr["kw"], key=lambda w: -sum(w in keywords(x["text"]) for x in gr["items"]))[:5]
        print(f"{i}. [{len(gr['items'])} asked, {sum(x['likes'] for x in gr['items'])} likes]  {', '.join(common)}")
        print(f"   \"{gr['items'][0]['text'].strip()[:220]}\"")
    print("\nWrite one title that answers each group of 2 or more. Praise and spam were dropped.")


if __name__ == "__main__":
    main()
