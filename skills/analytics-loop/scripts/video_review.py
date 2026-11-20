#!/usr/bin/env python3
"""Review one published video from YouTube Studio exports and write a postmortem skeleton.

Why exports: the YouTube Analytics API does not return impressions or impressions CTR,
so this reads the CSVs you download from Studio (Analytics > Advanced mode > Export).

Inputs:
  --traffic FILE   CSV, one row per traffic source, columns (case-insensitive, extra columns ignored):
                   traffic_source, impressions, ctr_pct, views, avg_view_duration_s
  --retention FILE optional CSV: second, pct   (audience retention curve, pct of viewers still watching)
  --baseline FILE  optional JSON: {"ctr_pct": {"Browse features": 4.1, ...}, "avd_pct": 38, "r30": 62}
                   your own channel medians; never compare with other channels
  --length 7:05    video length
  --window 7d      review window: 2h, 48h, 7d or 28d (decides which actions are allowed)

What it prints:
  per traffic source: impressions, CTR with a 95% interval, AVD, watch time per impression,
  and whether the sample is too small to read (under 1000 impressions)
  retention: 30-second hold, top 3 drops, curve shape
  a diagnosis from the table in references/diagnosis.md, then the actions allowed in this window
  with --postmortem FILE: a markdown skeleton with the numbers filled in

Usage:
  python video_review.py --traffic examples/data/traffic.csv --retention examples/data/retention.csv \
      --baseline examples/data/baseline.json --length 7:05 --window 7d --postmortem pm.md
"""
import argparse
import csv
import json
import math
import sys

ACTIONS = {
    "2h": "Watch only. Fix broken things (wrong thumbnail, missing link, typo). Do not change title or thumbnail yet: the sample is noise.",
    "48h": "If browse CTR is well under your baseline with 1000+ impressions, swap ONE element (thumbnail first) or start Test & Compare. Log it.",
    "7d": "Judge packaging and retention against your baselines. One change at most. Pin a comment answering the top question.",
    "28d": "Write the postmortem. Decide: make a follow-up, update the description and end screen, or leave it. Feed the lesson into the next topic score.",
}


def wilson(p, n, z=1.96):
    if n <= 0:
        return 0.0, 0.0
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0, c - h), min(1, c + h)


def secs(t):
    p = [int(x) for x in t.split(":")]
    return p[0] * 3600 + p[1] * 60 + p[2] if len(p) == 3 else p[0] * 60 + p[1]


def read_csv(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return [{k.strip().lower(): (v or "").strip() for k, v in r.items()} for r in csv.DictReader(f)]


def num(r, k):
    v = r.get(k, "").replace(",", "").replace("%", "")
    return float(v) if v else 0.0


def shape(curve, length):
    """Classify the retention curve. curve = sorted [(second, pct)]."""
    if len(curve) < 4:
        return "too few points", []
    drops = []
    for (s1, p1), (s2, p2) in zip(curve, curve[1:]):
        drops.append((p1 - p2, s1, s2))
    drops.sort(reverse=True)
    top = [d for d in drops if d[0] > 0][:3]
    rises = [(s1, s2) for (s1, p1), (s2, p2) in zip(curve, curve[1:]) if p2 > p1 + 1]
    first30 = next((p for s, p in curve if s >= 30), curve[-1][1])
    mid = next((p for s, p in curve if s >= length / 2), curve[-1][1])
    end = curve[-1][1]
    if first30 < 50:
        kind = "cliff: the opening loses people, the promise or the first 30 s do not match the package"
    elif rises:
        kind = f"bumps: viewers rewatch or skip back near {rises[0][0]} to {rises[0][1]} s, find out why and give more of it"
    elif mid - end > (first30 - mid) * 1.5 and mid - end > 10:
        kind = "late slide: the middle holds but the second half leaks, cut or move the payoff earlier"
    elif first30 - mid > 25:
        kind = "steady slide: no single moment, the pace or the structure is too even"
    else:
        kind = "flat: a healthy hold after the opening"
    return kind, top


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--traffic", required=True)
    ap.add_argument("--retention")
    ap.add_argument("--baseline")
    ap.add_argument("--length", required=True, help="video length M:SS or H:MM:SS")
    ap.add_argument("--window", choices=list(ACTIONS), default="7d")
    ap.add_argument("--min-impressions", type=int, default=1000)
    ap.add_argument("--postmortem", help="write a markdown postmortem skeleton here")
    ap.add_argument("--title", default="(video title)")
    a = ap.parse_args()
    length = secs(a.length)
    try:
        rows = read_csv(a.traffic)
        base = json.load(open(a.baseline, encoding="utf-8")) if a.baseline else {}
        curve = sorted((num(r, "second"), num(r, "pct")) for r in read_csv(a.retention)) if a.retention else []
    except (OSError, ValueError) as e:
        print(e, file=sys.stderr)
        sys.exit(2)
    out = []
    p = out.append
    p(f"# Review: {a.title} ({a.window} window)\n")
    p("| source | impressions | CTR % (95% range) | baseline | AVD s | AVD % | watch s per impression | read |")
    p("|---|---|---|---|---|---|---|---|")
    findings = []
    tot_imp = tot_views = tot_wt = 0
    for r in rows:
        src = r.get("traffic_source", "?")
        imp, ctr, views, avd = num(r, "impressions"), num(r, "ctr_pct"), num(r, "views"), num(r, "avg_view_duration_s")
        lo, hi = wilson(ctr / 100, imp)
        b = base.get("ctr_pct", {}).get(src)
        wtpi = ctr / 100 * avd
        tot_imp += imp
        tot_views += views
        tot_wt += views * avd
        if imp == 0:
            read = "no impressions data (external, direct, playlists)"
        elif imp < a.min_impressions:
            read = "sample too small"
        elif b is not None and hi * 100 < b:
            read = "below baseline"
            findings.append(("ctr_low", src))
        elif b is not None and lo * 100 > b:
            read = "above baseline"
        else:
            read = "inside the noise"
        rng = f"{ctr:.1f} ({lo * 100:.1f} to {hi * 100:.1f})" if imp else "n/a"
        p(f"| {src} | {int(imp):,} | {rng} | {b if b is not None else '-'} | {avd:.0f} | {avd / length * 100:.0f} | {wtpi:.1f} | {read} |")
    avd_all = tot_wt / tot_views if tot_views else 0
    avd_pct = avd_all / length * 100
    p(f"\nAll sources: {int(tot_views):,} views, AVD {avd_all:.0f} s ({avd_pct:.0f}% of {a.length}).")
    if base.get("avd_pct") is not None:
        p(f"Your AVD baseline: {base['avd_pct']}%.")
        if avd_pct < base["avd_pct"] - 5:
            findings.append(("avd_low", None))
    if curve:
        kind, top = shape(curve, length)
        r30 = next((pc for s, pc in curve if s >= 30), curve[-1][1])
        p(f"\nRetention: {r30:.0f}% still watching at 0:30" + (f" (baseline {base['r30']}%)" if base.get("r30") is not None else "") + f". Shape: {kind}.")
        if base.get("r30") is not None and r30 < base["r30"] - 5:
            findings.append(("r30_low", None))
        for d, s1, s2 in top:
            p(f"- drop of {d:.0f} points between {int(s1) // 60}:{int(s1) % 60:02d} and {int(s2) // 60}:{int(s2) % 60:02d}: open the script there")
    p("\n## Diagnosis\n")
    kinds = {k for k, _ in findings}
    if "ctr_low" in kinds and not ({"avd_low", "r30_low"} & kinds):
        p("- Packaging problem: viewers who click stay, but too few click. Test a new thumbnail first, then the title. Keep the video.")
    if ("avd_low" in kinds or "r30_low" in kinds) and "ctr_low" not in kinds:
        p("- Delivery problem: the package works, the video does not keep the promise. Check the first 30 s against the title and thumbnail, then the top drops.")
    if "ctr_low" in kinds and ({"avd_low", "r30_low"} & kinds):
        p("- Topic problem: low clicks and low hold. Do not repackage this one; take the lesson into the next topic score.")
    if not findings:
        p("- Nothing reads as a problem against your baselines in this window. Do not change anything for the sake of it.")
    p(f"\n## Allowed in the {a.window} window\n\n{ACTIONS[a.window]}")
    text = "\n".join(out)
    print(text)
    if a.postmortem:
        with open(a.postmortem, "w", encoding="utf-8") as f:
            f.write(text + "\n\n## Postmortem\n\n- Hypothesis before publishing:\n- What happened (numbers above):\n"
                    "- One variable we would change:\n- Decision (follow-up / update / leave):\n- Lesson for topic scoring:\n")
        print(f"\npostmortem skeleton written to {a.postmortem}")


if __name__ == "__main__":
    main()
