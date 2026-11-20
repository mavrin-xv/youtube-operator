---
name: topic-finder
description: Picks the next YouTube video topic from evidence instead of taste. Finds outlier videos on neighbour channels (views divided by that channel's median, via the YouTube Data API with a key from env), groups real viewer questions from comments, and ranks candidates on a 100-point priority matrix with a hard proof gate. Use when someone asks "what should my next video be", "video ideas", "find outliers", "what is working in my niche", "topic research for YouTube", "mine comments for ideas", or has a list of ideas to rank.
---

# Topic finder

An outlier tells you what an audience wanted beyond a channel's normal pull. A quoted question tells you the words
they use. A score tells you which of your ideas you can actually prove on screen. You need all three.

## Inputs

- The channel card (from `channel-lane`): viewer, lane, main traffic source.
- 10 to 15 neighbour channels: direct (same topic), adjacent (same viewer, other topic), aspirational (bigger).
- Optional: `YOUTUBE_API_KEY` in the environment. Without it, every script also runs on saved JSON files.

## Procedure

1. **Neighbour outliers.** Pull the last 12 months and rank by ratio:

   ```bash
   python3 scripts/outlier_finder.py --channels @a,@b,@c --days 365 --long-only --save neighbours.json
   ```

   Cost: about 3 to 5 quota units per channel out of 10,000 a day. Tiers: under 2x normal, 2 to 5x good, 5 to 10x
   strong, over 10x breakout. Videos younger than 14 days are skipped because their views are still growing.
   Read the shape-lift table at the end: a title shape (number, question, money, first person) that is far more
   common among outliers than among all videos is a hint, not a rule. Details:
   [references/outliers.md](references/outliers.md).
2. **Write down the question each outlier answered**, in one line, in the viewer's words. Copy the question, never
   the package. A copied title on a smaller channel loses to the original.
3. **Demand from comments.** For the top 3 to 5 outliers, and for your own last videos:

   ```bash
   python3 scripts/comment_questions.py --video VIDEO_ID --max 300 --save comments.json
   ```

   It drops praise and spam, keeps questions, and groups them by shared words. Quote the clearest comment in each
   group word for word. Other demand sources, ranked by how direct they are, are in
   [references/demand-signals.md](references/demand-signals.md).
4. **Score the candidates.** Fill a CSV (`python3 scripts/topic_score.py --template > topics.csv`), one row per idea,
   then:

   ```bash
   python3 scripts/topic_score.py topics.csv
   ```

   The criteria and what 0 and full points look like are in
   [references/priority-matrix.md](references/priority-matrix.md). Score honestly: the matrix is only as good as
   the evidence column.
5. **Pick** the highest score that passes the gate. Write the topic block of the video card: the viewer question with
   its source, the proof you will show, three competing videos and how yours differs, the next video it leads to.

## Hard rules

- Contribution 0 or evidence 0 means "research first", whatever the total. Run the test, then score again.
- An idea with no quoted demand is labelled a guess. Guesses are allowed; pretending they are evidence is not.
- Never claim to know another channel's CTR or retention. Public view counts are all you see.
- The ratio uses the channel median. Some tools use the average; their numbers will be lower for channels with one
  huge hit. Say which you used.
- One comment group is one video. Do not split a question across videos.

## Output

A ranked table (score, gate, demand label), the chosen topic, and the filled topic block of the video card.
