#!/usr/bin/env python3
"""Audit your own channel's recent uploads against their own median.

Prints:
  median views of the last N uploads (median, never mean: one hit skews a mean)
  publish bar = views of the current top 20% (80th percentile), the line every new package is judged against
  outliers  >= 3x median: name the ONE variable that differs (topic, title shape, thumbnail, format, length)
  misses    <= 0.5x median
  unlist candidates: < 0.3x median AND older than 90 days (unlist, never delete: deleting loses data)
  views per subscriber: < 0.1 = only subscribers watch, > 1 = search or browse carries it

Input: a JSON file in the format outlier_finder.py writes with --save (first channel is used,
or pick one with --handle). Get yours with:
  python ../../topic-finder/scripts/outlier_finder.py --channels @yourhandle --save mine.json

Usage:
  python channel_audit.py examples/data/own-channel.json
  python channel_audit.py mine.json --last 20 --format json

Exit codes: 0 ok, 1 fewer than 5 videos.
"""
import argparse
import json
import statistics
import sys
from datetime import datetime, timezone


def pct(values, q):
    v = sorted(values)
    k = (len(v) - 1) * q
    lo, hi = int(k), min(int(k) + 1, len(v) - 1)
    return v[lo] + (v[hi] - v[lo]) * (k - lo)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file")
    ap.add_argument("--handle", help="channel to audit if the file has several")
    ap.add_argument("--last", type=int, default=15, help="recent uploads to use (default 15; 10 to 20 is sensible)")
    ap.add_argument("--min-age-days", type=int, default=14, help="skip uploads younger than this (default 14)")
    ap.add_argument("--today", help="YYYY-MM-DD (default: the file's fetched date, else today)")
    ap.add_argument("--format", choices=["md", "json"], default="md")
    a = ap.parse_args()

    with open(a.file, encoding="utf-8") as f:
        data = json.load(f)
    chans = data.get("channels", [])
    ch = next((c for c in chans if c["handle"] == a.handle), None) if a.handle else (chans[0] if chans else None)
    if not ch:
        sys.exit("channel not found in file")
    ref = a.today or data.get("fetched")  # a saved file is read as of the day it was fetched
    today = datetime.strptime(ref, "%Y-%m-%d").date() if ref else datetime.now(timezone.utc).date()
    vids = []
    for v in ch["videos"]:
        age = (today - datetime.strptime(v["published"], "%Y-%m-%d").date()).days
        if age >= a.min_age_days:
            vids.append(dict(v, age=age))
    vids.sort(key=lambda v: v["age"])
    vids = vids[: a.last]
    if len(vids) < 5:
        print("fewer than 5 uploads old enough to judge; publish more before auditing", file=sys.stderr)
        sys.exit(1)

    views = [v["views"] for v in vids]
    med = statistics.median(views)
    bar = pct(views, 0.8)
    for v in vids:
        v["ratio"] = round(v["views"] / med, 2) if med else 0
    outliers = [v for v in vids if v["ratio"] >= 3]
    misses = [v for v in vids if v["ratio"] <= 0.5]
    unlist = [v for v in misses if v["views"] < 0.3 * med and v["age"] > 90]
    subs = ch.get("subscribers") or 0
    vps = round(med / subs, 2) if subs else None
    if vps is None:
        carry = "unknown (no subscriber count)"
    elif vps < 0.1:
        carry = "subscribers only: packaging is not reaching new viewers"
    elif vps > 1:
        carry = "search or browse carries the channel"
    else:
        carry = "mixed: subscribers plus some reach"

    res = {"channel": ch["handle"], "uploads": len(vids), "median": int(med), "publish_bar": int(bar),
           "views_per_sub": vps, "reading": carry,
           "outliers": [{k: v[k] for k in ("title", "views", "ratio", "age")} for v in sorted(outliers, key=lambda x: -x["ratio"])],
           "misses": [{k: v[k] for k in ("title", "views", "ratio", "age")} for v in sorted(misses, key=lambda x: x["ratio"])],
           "unlist_candidates": [v["title"] for v in unlist]}
    if a.format == "json":
        print(json.dumps(res, indent=1, ensure_ascii=False))
        return
    print(f"# Channel audit: {ch['handle']}, last {len(vids)} uploads\n")
    print(f"- Median views: {int(med):,}")
    print(f"- Publish bar (top 20%): {int(bar):,} views. Judge every new package against this.")
    print(f"- Views per subscriber at the median: {vps} ({carry})")
    print(f"\n## Outliers (3x or more): {len(outliers)}\n")
    for v in res["outliers"]:
        print(f"- {v['ratio']}x  {v['views']:,}  {v['title']}")
    print("  For each, name the one variable that differs from a normal upload. Two variables differ = mixed evidence, say so.")
    print(f"\n## Misses (0.5x or less): {len(misses)}\n")
    for v in res["misses"]:
        flag = "  <- unlist candidate (old and under 0.3x)" if v["title"] in res["unlist_candidates"] else ""
        print(f"- {v['ratio']}x  {v['views']:,}  {v['title']}{flag}")
    print("\nNext: one fix per channel surface (banner, trailer, playlists) and ONE variable to test in the next upload.")


if __name__ == "__main__":
    main()
