# Walkthrough: one video for an invented channel

Northwind Woodshop is an invented woodworking channel with 4,300 subscribers. Its neighbours (Acme Joinery, Offcut
Studio, Bench and Burr, Garage Craft Co) are invented too, and so are all of the numbers. Every output below is real
output from the scripts on the files in `examples/data/`. Sample files are read as of their `fetched` date
(2026-03-01), so the results do not change as time passes.

Run everything from the repo root. Use `python3` or `python3` if `python` is not Python 3.

## 1. Where the channel stands (channel-lane)

```bash
python3 skills/channel-lane/scripts/channel_audit.py examples/data/own-channel.json
```

```
# Channel audit: @northwindwoodshop, last 15 uploads

- Median views: 1,779
- Publish bar (top 20%): 2,842 views. Judge every new package against this.
- Views per subscriber at the median: 0.41 (mixed: subscribers plus some reach)

## Outliers (3x or more): 2

- 4.7x  8,360  Why My Tabletop Cupped
- 3.84x  6,840  Why My Box Joints Gapped

## Misses (0.5x or less): 3

- 0.3x  532  Router Bit Storage Rack  <- unlist candidate (old and under 0.3x)
- 0.37x  665  Shop Tour: 9 Square Meters
- 0.48x  855  Bench Hook in 20 Minutes
```

Both outliers answer a "why did my project fail" question. The misses are shop tours and storage builds. That gives
the channel card its lane: diagnose a failed project, then show the fix.

## 2. What the neighbours' audiences wanted (topic-finder)

```bash
python3 skills/topic-finder/scripts/outlier_finder.py --sample examples/data/neighbours.json
```

```
| ratio | tier | channel | views | min | title |
|---|---|---|---|---|---|
| 10.49x | breakout | @offcutstudio | 70,800 | 13.3 | How Much I Made Selling Cutting Boards |
| 6.44x | strong | @benchandburr | 10,220 | 19.9 | Why Your Saw Drifts Left |
| 5.77x | strong | @acmejoinery | 136,500 | 17.9 | I Built a Workbench for $90 |
| 5.07x | strong | @garagecraftco | 193,800 | 20.6 | I Turned a One-Car Garage Into a Woodshop |
| 3.73x | good | @offcutstudio | 25,200 | 17.3 | Why Cheap Clamps Ruin Square Boxes |
...
| shape | outliers | all |
| how/why | 50% | 11% |
| money | 50% | 15% |
```

With a free API key (`export YOUTUBE_API_KEY=...`) the same command takes `--channels @a,@b --save file.json`.
Fifteen channels of 100 videos cost about 75 of the 10,000 daily quota units.

The comments on the channel's own outlier show the questions viewers still have:

```bash
python3 skills/topic-finder/scripts/comment_questions.py --file examples/data/comments.json
```

```
1. [4 asked, 58 likes]  cup, tabletop, stop, week, humid
   "Why did my oak tabletop cup after two weeks? I finished both sides."
2. [4 asked, 40 likes]  finish, walnut, safe, food, cut
   "What finish did you use on the walnut?"
```

The candidates go into `topics.csv` with their evidence and get scored:

```bash
python3 skills/topic-finder/scripts/topic_score.py examples/data/topics.csv
```

```
| # | total | gate | demand | topic | weakest |
|---|---|---|---|---|---|
| 1 | 86 | pass | quoted (9) | Why your tabletop cupped (and the 3 fixes that work) | contribution |
| 2 | 77 | pass | quoted (6) | How much a cutting board really costs to make | visual |
| 3 | 70 | pass | quoted (3) | What a $90 workbench gets wrong | contribution |
| 4 | 67 | research first | quoted (5) | Why your saw drifts left | contribution |
| 5 | 59 | research first | quoted (2) | Hide glue vs PVA: a 6-month joint test | evidence |
| 6 | 29 | research first | guess (0) | Best woodworking tips 2026 | evidence |
```

The winner is a follow-up to the channel's own best video, which answers the questions its comments still ask.
"Saw drifts left" scores well on demand but has no contribution yet (no test, no new angle), so it waits.

## 3. Package before script (packaging-lab)

Three concepts become five drafts in `titles.txt`:

```bash
python3 skills/packaging-lab/scripts/title_score.py --file examples/data/titles.txt --keyword tabletop --thumb "3 FIXES"
```

```
1. 100/100  Why Your Tabletop Cupped (and 3 Fixes That Work)
2. 100/100  I Fixed a Cupped Walnut Tabletop in 2 Days
3. 90/100  Tabletop Cupped? The Moisture Mistake Behind It
     -10  concrete: no number, price or count
4. 35/100  The ULTIMATE Guide to Wood Movement Nobody Tells You About!!
     -20  plain language: bait: ultimate, nobody tells you
5. FAIL 121 chars, YouTube allows 100  Everything You Need to Know About Wood Movement, ...
```

Exit code 1, because draft 5 cannot be uploaded at all. Drafts 1 and 2 go into Test & Compare with two thumbnails.
The score is a lint for obvious mistakes. Watch time share in the test picks the winner.

## 4. Script that keeps the promise (retention-script)

`examples/script.md` is draft 2 of a short cut of the script, with problems planted on purpose.

```bash
python3 skills/retention-script/scripts/script_lint.py examples/script.md --wpm 160 --target 180 --claims examples/claims-register.md
```

```
363 words at 160 wpm = about 2:16

| start | block | seconds |
|---|---|---|
| 0:00 | Hook | 15 |
| 0:15 | Minimum world | 24 |
| 0:39 | Cause one: one face drier than the other | 22 |
...
WARN   0:34 number without a claim tag: "On a top 80 centimetres wide, that is close to a centimetre of movemen"
WARN   1:01 weak transition: "Next, the boards themselves." (try so / but / which means)
WARN   1:03 long sentence (39 words): "Lumber that came out of a kiln last week and went straight into a humi..."
WARN   outro filler in the last 15%: 'thanks for watching'. End on the takeaway and the next question
WARN   estimated 2:16 vs target 3:00 (-24%); cut or add, never pad
```

Exit 0: no blockers, nine warnings to fix or explain. The `160` comes from timing one real take; the default of 150
is only a starting guess.

## 5. Publish package (publish-package)

```bash
python3 skills/retention-script/scripts/script_lint.py examples/script.md --wpm 160 --format json > timing.json
python3 skills/publish-package/scripts/publish_lint.py --chapters-from timing.json --duration 2:16
```

```
00:00 Hook
00:15 Minimum world
00:39 Cause one: one face drier than the other
01:01 Cause two: the wood was not ready
...
```

The chapter titles are then edited into small promises (see `examples/description.md`), and the whole package is
linted:

```bash
python3 skills/publish-package/scripts/publish_lint.py --title "Why Your Tabletop Cupped (and 3 Fixes That Work)" \
  --description examples/description.md --tags "tabletop cupping,cupped tabletop,wood movement,table top warp" \
  --duration 2:16 --thumb examples/data/thumb-small.png --owned example.com
```

```
title 48/100 chars, description 673/5000 bytes, tags 69/500 chars
BLOCK  thumbnail is 1200x675; use at least 1280x720
WARN   owned link without utm_source: https://example.com/wood-movement
```

Exit 1. The thumbnail was exported at the wrong size, and one link to the channel's own site has no utm tag. Both are
two-minute fixes that would otherwise ship.

## 6. Review after 7 days (analytics-loop)

The review data belongs to the channel's earlier 7:05 upload "Why My Tabletop Cupped", the outlier from step 1. It
shows how the loop reads a video that did well overall but still has one weak source.

```bash
python3 skills/analytics-loop/scripts/video_review.py --traffic examples/data/traffic.csv \
  --retention examples/data/retention.csv --baseline examples/data/baseline.json --length 7:05 --window 7d
```

```
| source | impressions | CTR % (95% range) | baseline | AVD s | AVD % | watch s per impression | read |
|---|---|---|---|---|---|---|---|
| Browse features | 18,400 | 2.9 (2.7 to 3.2) | 4.2 | 171 | 40 | 5.0 | below baseline |
| YouTube search | 6,200 | 7.8 (7.2 to 8.5) | 7.5 | 196 | 46 | 15.3 | inside the noise |
| Suggested videos | 9,100 | 3.6 (3.2 to 4.0) | 3.9 | 160 | 38 | 5.8 | inside the noise |
| Channel pages | 700 | 9.1 (7.2 to 11.5) | 8.0 | 210 | 49 | 19.1 | sample too small |

Retention: 72% still watching at 0:30 (baseline 66%). Shape: flat: a healthy hold after the opening.
- drop of 12 points between 0:00 and 0:10: open the script there
- drop of 9 points between 4:30 and 5:00: open the script there

## Diagnosis

- Packaging problem: viewers who click stay, but too few click. Test a new thumbnail first, then the title. Keep the video.
```

Search works, and people who click stay. Browse is the one source where the whole CTR range sits under the baseline,
so the one allowed change is a new thumbnail concept, logged in the decision journal (see
`skills/analytics-loop/templates/decision-journal.md` for that exact entry). The drop at 4:30 is noted for the next
script, not fixed in this video.
