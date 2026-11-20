---
name: analytics-loop
description: Reviews a published YouTube video at fixed windows (2 h, 48 h, 7 d, 28 d) from YouTube Studio exports. Reads CTR per traffic source with a confidence range against the channel's own baseline, computes watch time per impression, finds the top retention drops and the curve shape, diagnoses packaging, delivery or topic, lists only the actions allowed in that window, and writes a postmortem plus a decision journal entry. Use when someone says "why is my video not doing well", "my CTR is low", "retention dropped", "review my video", "YouTube analytics", "postmortem", "should I change the thumbnail", or pastes Studio numbers.
---

# Analytics loop

The loop turns each video into one lesson for the next. It works only if you compare with your own baselines, wait
for enough data, and change one thing at a time.

## Inputs

- Studio exports (Analytics, Advanced mode, Export current view as CSV):
  - by **traffic source**: impressions, impressions CTR, views, average view duration;
  - the **audience retention** curve (second, percent still watching), if you have it.
- The video length and the review window.
- Your baselines: median CTR per source, median average view duration percent, median R30 over your last 10 to 20
  videos. Keep them in a small JSON file (`examples/data/baseline.json` shows the format).

The YouTube Analytics API does not return impressions or impressions CTR, so exports are the reliable source for
packaging numbers. Views and watch time also come from the API if you prefer it.

## Procedure

1. Check the window. Before 48 hours, or under about 1,000 impressions on a source, packaging numbers are noise.
2. Run the review:

   ```bash
   python3 scripts/video_review.py --traffic traffic.csv --retention retention.csv \
       --baseline baseline.json --length 7:05 --window 7d --postmortem postmortem.md
   ```

   Per source you get CTR with a 95% range (Wilson interval), the baseline, average view duration, and watch time
   per impression (CTR x average view duration). A source reads "below baseline" only when the whole range is under
   it.
3. Read the diagnosis. The full table is in [references/diagnosis.md](references/diagnosis.md):
   - low CTR, normal hold: a **packaging** problem. Test a new thumbnail concept, then the title.
   - normal CTR, low hold: a **delivery** problem. The video does not keep the promise; open the script at the drops.
   - low CTR and low hold: a **topic** problem. Do not repackage; take the lesson into the next topic score.
4. Do only what the window allows (the script prints it). Every fix names a timestamp and the change at that spot.
5. Write one line in `templates/decision-journal.md` for every change: date, what, why (which number), what you
   expect, when you check.
6. At 28 days, finish the postmortem (`templates/postmortem.md`) and feed the lesson into the topic matrix and the
   packaging rules.

## Metrics, briefly

Full dictionary: [references/metrics.md](references/metrics.md). The one number closest to what YouTube distributes
on is watch time per impression: 5% CTR x 3:00 beats 8% CTR x 1:00.

## Rules

- Compare only with your own videos, within one traffic source. CTR falls as impressions widen to colder audiences;
  falling CTR with rising impressions is often success.
- One change at a time, or the result teaches nothing.
- Data younger than 48 hours is "not returned yet", never zero.
- Do not act on the myths in [references/myths.md](references/myths.md).
- Unlist a weak old video if you must. Never delete; deleting loses the data.

## Output

The review table, the retention reading, the diagnosis, the allowed actions, the postmortem file at 28 days, and the
decision journal line.
