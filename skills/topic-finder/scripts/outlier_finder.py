#!/usr/bin/env python3
"""Find outlier videos on neighbour channels: views divided by that channel's median.

An outlier is a video that pulled far more than its own channel normally does. That
tells you what the audience wanted beyond the channel's usual pull. Copy the question
the video answered, never its package.

Data sources:
  --channels @a,@b      live, YouTube Data API v3 (key from env YOUTUBE_API_KEY)
  --sample FILE.json    offline, a file saved earlier with --save (or the bundled example)

API cost per channel: 1 unit (channels.list) + 1 per 50 uploads (playlistItems.list)
+ 1 per 50 videos (videos.list). 15 channels x 100 videos is about 75 units of the
default 10,000 daily quota. search.list (100 units) is never used.

Tiers (ratio = views / channel median, videos in the window only):
  < 2x normal | 2-5x good | 5-10x strong | > 10x breakout

Usage:
  python outlier_finder.py --sample examples/data/neighbours.json
  python outlier_finder.py --channels @acmejoinery,@offcutstudio --days 365 --save neighbours.json
  python outlier_finder.py --sample n.json --min-ratio 3 --long-only --format csv > outliers.csv

Env: YOUTUBE_API_KEY (only for --channels). Python 3.8+, standard library only.
Exit codes: 0 ok, 1 no data, 2 bad arguments or API error.
"""
import argparse
import csv
import json
import os
import re
import statistics
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime, timedelta, timezone

API = "https://www.googleapis.com/youtube/v3/"
TIERS = [(10, "breakout"), (5, "strong"), (2, "good"), (0, "normal")]


def api(endpoint, key, **params):
    params["key"] = key
    url = API + endpoint + "?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")
        reason = re.search(r'"reason":\s*"([^"]+)"', body)
        sys.exit(f"API error {e.code} on {endpoint}: {reason.group(1) if reason else body[:200]}")


def iso_seconds(d):
    m = re.fullmatch(r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", d or "")
    if not m:
        return 0
    days, h, mi, s = (int(x or 0) for x in m.groups())
    return days * 86400 + h * 3600 + mi * 60 + s


def fetch_channel(handle, key, max_videos):
    q = {"forHandle": handle} if handle.startswith("@") else {"id": handle}
    data = api("channels", key, part="snippet,statistics,contentDetails", **q)
    if not data.get("items"):
        print(f"  skip {handle}: channel not found", file=sys.stderr)
        return None
    ch = data["items"][0]
    uploads = ch["contentDetails"]["relatedPlaylists"]["uploads"]
    ids, token = [], None
    while len(ids) < max_videos:
        p = {"part": "contentDetails", "playlistId": uploads, "maxResults": 50}
        if token:
            p["pageToken"] = token
        page = api("playlistItems", key, **p)
        ids += [it["contentDetails"]["videoId"] for it in page.get("items", [])]
        token = page.get("nextPageToken")
        if not token:
            break
    videos = []
    for i in range(0, min(len(ids), max_videos), 50):
        page = api("videos", key, part="snippet,statistics,contentDetails", id=",".join(ids[i:i + 50]))
        for v in page.get("items", []):
            videos.append({"id": v["id"], "title": v["snippet"]["title"],
                           "published": v["snippet"]["publishedAt"][:10],
                           "views": int(v.get("statistics", {}).get("viewCount", 0)),
                           "duration_s": iso_seconds(v["contentDetails"].get("duration"))})
    return {"handle": handle, "title": ch["snippet"]["title"],
            "subscribers": int(ch["statistics"].get("subscriberCount", 0) or 0), "videos": videos}


def shape(title):
    t = title.lower()
    tags = []
    if re.search(r"\d", t):
        tags.append("number")
    if t.rstrip().endswith("?"):
        tags.append("question")
    if re.match(r"(how|why|what|when|where)\b", t):
        tags.append("how/why")
    if re.search(r"\bvs\.?\b|\bversus\b", t):
        tags.append("versus")
    if re.search(r"\b(i|my|we)\b", t):
        tags.append("first-person")
    if re.search(r"[\[(]", t):
        tags.append("brackets")
    if re.search(r"\b(mistake|wrong|stop|never|don't|fail|ruin)", t):
        tags.append("negative")
    if re.search(r"\b(cheap|budget|cost|costs|price|pricing|free|made|sell|selling|earn)\b|\$", t):
        tags.append("money")
    return tags or ["plain"]


def tier(r):
    return next(name for lim, name in TIERS if r >= lim)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--channels", help="comma-separated @handles or channel ids (needs YOUTUBE_API_KEY)")
    src.add_argument("--sample", help="offline JSON file saved with --save")
    ap.add_argument("--days", type=int, default=365, help="only videos published in the last N days (default 365)")
    ap.add_argument("--min-age-days", type=int, default=14, help="skip videos younger than this, views still growing (default 14)")
    ap.add_argument("--max-videos", type=int, default=100, help="uploads to read per channel (default 100)")
    ap.add_argument("--long-only", action="store_true", help="drop videos of 180 s or less (Shorts have their own median)")
    ap.add_argument("--min-ratio", type=float, default=2.0, help="list videos at or above this ratio (default 2)")
    ap.add_argument("--today", help="YYYY-MM-DD to compute ages against (default: today, or the fetched date of a --sample file)")
    ap.add_argument("--save", help="write the fetched raw data to this JSON file")
    ap.add_argument("--format", choices=["md", "json", "csv"], default="md")
    a = ap.parse_args()

    if a.channels:
        key = os.environ.get("YOUTUBE_API_KEY")
        if not key:
            sys.exit("YOUTUBE_API_KEY is not set. Create a key in Google Cloud (YouTube Data API v3), or use --sample.")
        chans = [fetch_channel(h.strip(), key, a.max_videos) for h in a.channels.split(",") if h.strip()]
        chans = [c for c in chans if c]
        data = {"fetched": datetime.now(timezone.utc).date().isoformat(), "channels": chans}
    else:
        with open(a.sample, encoding="utf-8") as f:
            data = json.load(f)
    if a.save:
        with open(a.save, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=1, ensure_ascii=False)

    # a saved file is read as of the day it was fetched, so old samples keep working
    ref = a.today or (data.get("fetched") if a.sample else None)
    today = datetime.strptime(ref, "%Y-%m-%d").date() if ref else datetime.now(timezone.utc).date()
    lo, hi = today - timedelta(days=a.days), today - timedelta(days=a.min_age_days)
    rows, summary = [], []
    for ch in data.get("channels", []):
        vids = [v for v in ch["videos"]
                if lo <= datetime.strptime(v["published"], "%Y-%m-%d").date() <= hi
                and not (a.long_only and v.get("duration_s", 0) <= 180)]
        if len(vids) < 5:
            summary.append((ch["handle"], len(vids), 0, "too few videos in window, skipped"))
            continue
        med = statistics.median(v["views"] for v in vids)
        summary.append((ch["handle"], len(vids), int(med), ""))
        for v in vids:
            r = v["views"] / med if med else 0
            rows.append({"channel": ch["handle"], "title": v["title"], "id": v["id"], "published": v["published"],
                         "views": v["views"], "median": int(med), "ratio": round(r, 2), "tier": tier(r),
                         "minutes": round(v.get("duration_s", 0) / 60, 1), "shape": shape(v["title"]),
                         "subs": ch.get("subscribers", 0)})
    if not rows:
        print("no videos in the window. Widen --days or lower --min-age-days.", file=sys.stderr)
        sys.exit(1)

    rows.sort(key=lambda x: -x["ratio"])
    hits = [r for r in rows if r["ratio"] >= a.min_ratio]
    all_shapes = Counter(s for r in rows for s in r["shape"])
    hit_shapes = Counter(s for r in hits for s in r["shape"])
    lift = sorted(((s, hit_shapes[s] / max(1, len(hits)), all_shapes[s] / len(rows)) for s in all_shapes),
                  key=lambda x: -(x[1] - x[2]))

    if a.format == "json":
        print(json.dumps({"window": [lo.isoformat(), hi.isoformat()], "channels": summary, "outliers": hits,
                          "shapes": [{"shape": s, "outlier_share": round(h, 2), "all_share": round(b, 2)} for s, h, b in lift]},
                         indent=1, ensure_ascii=False))
        return
    if a.format == "csv":
        w = csv.writer(sys.stdout)
        w.writerow(["ratio", "tier", "channel", "views", "median", "published", "minutes", "title", "id", "shape"])
        for r in hits:
            w.writerow([r["ratio"], r["tier"], r["channel"], r["views"], r["median"], r["published"],
                        r["minutes"], r["title"], r["id"], "+".join(r["shape"])])
        return

    print(f"# Outliers, {lo} to {hi}\n")
    print("| channel | videos in window | median views | note |\n|---|---|---|---|")
    for h, n, med, note in summary:
        print(f"| {h} | {n} | {med:,} | {note} |")
    print(f"\n## {len(hits)} video(s) at {a.min_ratio}x or more\n")
    print("| ratio | tier | channel | views | min | title |\n|---|---|---|---|---|---|")
    for r in hits:
        print(f"| {r['ratio']}x | {r['tier']} | {r['channel']} | {r['views']:,} | {r['minutes']} | {r['title']} |")
    print("\n## Title shapes: share among outliers vs all videos\n")
    print("| shape | outliers | all |\n|---|---|---|")
    for s, h, b in lift:
        print(f"| {s} | {h:.0%} | {b:.0%} |")
    print("\nNext: for each outlier write the viewer question it answered, then score it with topic_score.py.")
    print("Small samples: a shape on 2 outliers is a hint, not a rule.")


if __name__ == "__main__":
    main()
