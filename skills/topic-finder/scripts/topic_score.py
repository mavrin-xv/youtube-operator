#!/usr/bin/env python3
"""Rank video topic candidates on a 100-point priority matrix with a hard proof gate.

Criteria and maximum points:
  interest      20  demand signals: quoted questions, neighbour outliers
  question      20  one sharp question in the viewer's words, not a topic
  contribution  15  what only you can show: your test, your case, your angle
  evidence      15  proof you can put on screen: a test, a source, a demo
  visual        15  a mechanism or result you can show moving
  cost          10  inverted: 10 = reuses what you have, 0 = weeks of new work
  series         5  opens two or more follow-ups

Hard gate: contribution = 0 or evidence = 0 means "research first", whatever the total.
A topic with no quoted demand is labelled "outlier only" if outlier_ratio >= 3, else "guess".

Input: CSV with a header row. Required columns: topic plus the seven criteria.
Optional: demand_quotes (count of real quoted questions), outlier_ratio (best neighbour ratio).

Usage:
  python topic_score.py examples/data/topics.csv
  python topic_score.py topics.csv --format json
  python topic_score.py --template > topics.csv     # empty CSV to fill in

Exit codes: 0 ok, 2 bad input (a value above its maximum, a missing column).
"""
import argparse
import csv
import json
import sys

MAX = {"interest": 20, "question": 20, "contribution": 15, "evidence": 15, "visual": 15, "cost": 10, "series": 5}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", nargs="?", help="CSV of candidates")
    ap.add_argument("--format", choices=["md", "json"], default="md")
    ap.add_argument("--template", action="store_true", help="print an empty CSV header and one example row")
    a = ap.parse_args()

    cols = ["topic"] + list(MAX) + ["demand_quotes", "outlier_ratio"]
    if a.template:
        print(",".join(cols))
        print('"Why your tabletop cupped",16,18,12,12,13,8,4,7,4.4')
        return
    if not a.file:
        ap.error("give a CSV file or --template")

    rows, errors = [], []
    with open(a.file, encoding="utf-8-sig", newline="") as f:
        for n, r in enumerate(csv.DictReader(f), start=2):
            missing = [c for c in ["topic"] + list(MAX) if c not in r]
            if missing:
                sys.exit(f"missing column(s): {', '.join(missing)}")
            s = {}
            for c, m in MAX.items():
                try:
                    v = float(r[c] or 0)
                except ValueError:
                    errors.append(f"line {n}: {c}={r[c]!r} is not a number")
                    continue
                if not 0 <= v <= m:
                    errors.append(f"line {n}: {c}={v:g} outside 0..{m}")
                s[c] = v
            total = sum(s.values())
            quotes = int(float(r.get("demand_quotes") or 0))
            gate = "research first" if s.get("contribution", 0) == 0 or s.get("evidence", 0) == 0 else "pass"
            weakest = min(MAX, key=lambda c: s.get(c, 0) / MAX[c])
            rows.append({"topic": r["topic"], "total": round(total), "gate": gate, "scores": s,
                         "demand": "quoted" if quotes else ("outlier only" if float(r.get("outlier_ratio") or 0) >= 3 else "guess"),
                         "quotes": quotes,
                         "outlier_ratio": r.get("outlier_ratio") or "", "weakest": weakest})
    if errors:
        print("\n".join(errors), file=sys.stderr)
        sys.exit(2)

    rows.sort(key=lambda x: (x["gate"] != "pass", -x["total"]))
    if a.format == "json":
        print(json.dumps(rows, indent=1, ensure_ascii=False))
        return
    print("| # | total | gate | demand | topic | weakest |\n|---|---|---|---|---|---|")
    for i, r in enumerate(rows, 1):
        print(f"| {i} | {r['total']} | {r['gate']} | {r['demand']} ({r['quotes']}) | {r['topic']} | {r['weakest']} |")
    nxt = next((r for r in rows if r["gate"] == "pass"), None)
    print()
    if nxt:
        print(f"Make next: \"{nxt['topic']}\" ({nxt['total']}/100). Weakest criterion: {nxt['weakest']}.")
    else:
        print("No candidate passes the proof gate. Run the test or find the source before producing anything.")
    blocked = [r["topic"] for r in rows if r["gate"] != "pass"]
    if blocked:
        print("Research first (no contribution or no evidence): " + "; ".join(blocked))


if __name__ == "__main__":
    main()
