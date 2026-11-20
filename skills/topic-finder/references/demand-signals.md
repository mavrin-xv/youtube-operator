# Demand signals

Ranked by how directly they show a real person wants the answer.

1. **Questions in comments** on neighbour outliers and on your own videos (`comment_questions.py`). Group by the
   question underneath, count each group, quote the clearest one word for word.
2. **Search**: YouTube autocomplete (type the start of the question in an incognito window), your website's search
   console queries, "People also ask" boxes.
3. **Forums where the viewer asks for help**: subreddits, Discord servers, Stack Exchange, GitHub issues, product
   forums. A thread with many replies and no good answer is a strong signal.
4. **Your own sales and support questions.** If customers ask it on calls, viewers search it.
5. **Neighbour outliers** without comment evidence: you know the topic pulled, you do not yet know the question.

Not demand: what you find interesting, a trend headline with no questions under it, a keyword tool's volume with no
real phrasing behind it.

## Comment loop after every publish

At 7 days and 28 days:

1. Pull comments: `python3 scripts/comment_questions.py --video VIDEO_ID --save c.json`.
2. Keep the groups you can answer with a demo or a test.
3. For each kept group, write one title that answers it, in the commenter's words.
4. Add the group to `topics.csv` with `demand_quotes` set to the group size.

## Labels for the video card

- **quoted**: at least one real question, with its source.
- **outlier only**: a neighbour video of 3x or more on the same question, no quotes yet.
- **guess**: neither. Allowed, but say so.
