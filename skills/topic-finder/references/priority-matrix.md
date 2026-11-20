# Priority matrix (100 points)

| Criterion | Max | 0 points | Full points |
|---|---|---|---|
| Audience interest | 20 | nobody asks, no outliers | many askers, neighbour outliers of 3x or more |
| Clear question | 20 | a topic ("wood movement") | one sharp question in viewer words ("why did my tabletop cup?") |
| Your contribution | 15 | a rewrite of what is already out there | your measurement, your case, your angle |
| Evidence available | 15 | memory only | a test, a source, a demo you can run on camera |
| Visual potential | 15 | talking about text | a mechanism or result you can show moving |
| Production cost (inverted) | 10 | weeks of new sets or assets | reuses what you have |
| Series potential | 5 | one-off | opens two or more follow-ups |

**Hard gate:** contribution 0 or evidence 0 means do not produce, whatever the total. Move it to research.

## Scoring tips

- Score interest from the evidence column only. If you cannot point to a quote or an outlier, interest is 5 at most.
- Score the question by writing it out. If you need "and" to write it, it is two videos.
- Contribution is the column most people inflate. Ask: what will this video show that the top three results do not?
- Re-score a topic after its research is done; evidence often moves from 0 to 10.

## CSV columns

`topic, interest, question, contribution, evidence, visual, cost, series, demand_quotes, outlier_ratio`

`demand_quotes` and `outlier_ratio` are optional; with them the output labels each row quoted, outlier only, or
guess. `python3 scripts/topic_score.py --template` prints an empty file.
