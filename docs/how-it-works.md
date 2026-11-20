# How it works

## One card, six gates

Every video has one card (`skills/video-pipeline/templates/video-card.md`). Each skill reads the card, does its stage,
writes the result back, and checks a gate. The pipeline will not move a video forward past a failed gate, and it
says which line failed.

```
channel card (once)            video card (per video)
      |                               |
  [A] lane  -->  [B] topic  -->  [C] package  -->  [D] script  -->  production  -->  [G] publish  -->  [I] review
                   ^                                                 (yours)                          |
                   +----------------------- lessons from the 28-day postmortem -----------------------+
```

Production is outside the pack on purpose. Filming, editing, animation and voice differ for every channel. The pack
gives production an approved package and script, then takes the video back at the publish stage.

## Why packaging comes before the script

The title and thumbnail decide whether anyone starts the video. The first 30 seconds decide whether they stay. If the
script comes first, the package has to describe whatever got written, and that is usually vague. If the package comes
first, the script has one job: keep that promise.

## What the scripts measure, and what they do not

| Script | Measures | Does not |
|---|---|---|
| `channel_audit.py` | your median, the top-20% bar, outliers and misses against your own median | compare you with other channels |
| `outlier_finder.py` | views divided by each neighbour's own median; title shapes among outliers | see anyone's CTR or retention (not public) |
| `comment_questions.py` | groups of real questions in comments, by word overlap | understand meaning; it is a word grouper |
| `topic_score.py` | the weighted matrix you filled in, with gates | decide demand for you; the numbers are your judgement |
| `title_score.py` | length, front-loading, bait words, caps, word count, thumbnail overlap | predict CTR; it is a lint |
| `script_lint.py` | length from your speaking rate, openers, transitions, resets, payoff position, claim tags | judge whether the idea is good |
| `publish_lint.py` | YouTube field limits, chapter rules, thumbnail size, placeholders, utm | check that links work (click them) |
| `video_review.py` | CTR per source with a Wilson 95% interval, watch time per impression, retention drops, a diagnosis | see impressions without a Studio export |

## Data sources

- **YouTube Data API v3**, with a free key, for public numbers: uploads, views, durations, comments. The scripts use
  only cheap calls (1 unit each) and never `search.list` (100 units).
- **YouTube Studio exports** for your own impressions, CTR and retention. The Analytics API does not return
  impressions or impressions CTR, so the review reads CSV exports.
- **Saved JSON files** (`--save`, then `--sample`), so a pull can be rerun, shared and tested offline.

## Why medians

One viral video lifts an average and hides what is normal for a channel. The median does not move much. Commercial
outlier tools use their own formulas (vidIQ describes its score as a comparison with the channel's average); this
pack uses the median and says so.

## Small samples

A CTR from 300 impressions can be off by several points. The review prints a 95% range and only calls a source
"below baseline" when the whole range is under it. Under `--min-impressions` (default 1,000) a source is marked
"sample too small".
