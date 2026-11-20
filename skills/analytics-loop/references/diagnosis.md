# Diagnosis

## Symptom table

| Symptom | Likely causes | Next step | Do not conclude |
|---|---|---|---|
| Few impressions | little demand for the topic, a new channel, search ranking not formed yet | wait 28 days for search; check the demand evidence; pick better next time | that the algorithm hates you |
| Impressions fine, low CTR within one source | unclear package, wrong promise for that surface, unreadable when small | Test & Compare a new concept, not a reword | that the video is bad |
| Good CTR, cliff before 0:30 | package and opening do not match | rewrite the next openings; consider a package that matches this content | that people dislike the topic |
| Good R30, steep drop mid-video | a weak block, no signpost, a long setup | cut or restructure that block in the next video | that videos must be shorter |
| Good retention, few views | packaging or topic demand, not the video | packaging test; a similar topic with more demand | that quality does not matter |
| Views but no business result | wrong audience, no clear next step, link buried | first lines of the description, pinned comment, the ending as the call to action | that YouTube does not work for your business |
| Many new viewers, few returning | one-off topics, no series | build a series and a playlist path | |

## Retention shapes

| Shape | Meaning | Look at |
|---|---|---|
| cliff in the first 30 s | the opening did not confirm the package, or started slow | the first line, the first visual, the title |
| steady slide | normal; the slope tells you about pace | compare with your own similar-length videos |
| sudden drop mid-video | a block that does not earn its place, a tangent, a weak transition | the 10 seconds before the drop |
| bump | rewatching: a high-value moment, or confusion | is it a payoff or a hard part? |
| late slide or drop before the end | the ending said "done" too early | move the takeaway later, cut the outro |
| flat and high | strong | a follow-up or a Shorts cut |

`video_review.py` names the shape from the curve with simple rules and lists the top three drops. Treat its label
as a pointer to where to look, then watch the video at those timestamps.

## Review windows

| When | Look at | Allowed |
|---|---|---|
| 0 to 2 h | it plays, HD processed, captions, chapters show, end screen, links | fix technical errors only |
| 48 to 72 h | impressions and CTR by source, R30, first comments | one packaging change if the first is clearly broken, with 1,000+ impressions |
| 7 d | full curve, average view duration, end screen clicks, traffic split, tagged visits | three observations, one hypothesis, at most one change |
| 28 d | totals against your median, search share, business result | postmortem, decision journal, update topic and packaging rules |

## Small samples

At 1,000 impressions and about 5% CTR, the 95% range is roughly plus or minus 1.35 percentage points. At 10,000 it
is about plus or minus 0.43. The script prints the range so you can see when a difference is real.
