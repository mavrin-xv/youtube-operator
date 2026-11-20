---
name: channel-lane
description: Defines what a YouTube channel is for (one viewer, one outcome, one lane sentence, one business metric, the traffic source to build for) and audits an existing channel against its own median, listing outliers, misses, the publish bar and unlist candidates. Use when someone says "what should my channel be about", "niche for my YouTube", "audit my channel", "why is my channel not growing", "channel strategy", "who is my channel for", or before the first video of a new channel.
---

# Channel lane

A channel is weak where its smallest factor is: audience interest, clarity of the promise, quality of viewing,
desire to come back. This skill finds the smallest one and writes the channel card every other skill reads.

## Inputs

- What the person makes or sells, and why they want a channel (ask if missing; the business goal decides the metric).
- For an existing channel: its handle, so you can pull uploads with `outlier_finder.py --save`.
- Optional: 10 to 15 neighbour channels the same viewer watches.

## Procedure: new channel

1. Fill `templates/channel-card.md` with the person, one field at a time. Push back on vague answers:
   - "Everyone interested in X" is not a viewer. Ask for one real person and what they are trying to do this week.
   - "Learn about X" is not an outcome. Ask what the viewer can do after the video.
2. Pick the primary business goal and its metric from the table in
   [references/strategy.md](references/strategy.md). One goal. A second goal is a tiebreaker, not a target.
3. Pick the main traffic source (search, suggested, browse) using the same reference. A B2B or how-to channel is
   usually search first, suggested second; judge it against search numbers, not browse CTR.
4. Write the series grammar: what repeats in every episode and what is new each time.
5. Write the "never" list and the rhythm you can hold for six months (one good long video every one or two weeks is
   an honest start for one person).
6. Check gate A in the video-pipeline skill. Save the card.

## Procedure: existing channel audit

1. Pull the uploads (needs `YOUTUBE_API_KEY`, 2 to 4 quota units):

   ```bash
   python3 ../topic-finder/scripts/outlier_finder.py --channels @yourhandle --save mine.json
   python3 scripts/channel_audit.py mine.json --last 15
   ```

   Without a key, build the same JSON by hand from Studio (Content tab: title, published date, views). Format: see
   `examples/data/own-channel.json` in the repo root.
2. Read the output:
   - **Median** of the last 10 to 20 uploads. Median, not mean: one hit skews a mean.
   - **Publish bar**: the views of the current top 20%. Every new package is judged against it.
   - **Outliers** (3x or more): for each, name the one variable that differs from a normal upload (topic, title
     shape, thumbnail type, format, length). If two differ, the evidence is mixed; say so.
   - **Misses** (0.5x or less): same exercise.
   - **Views per subscriber**: under 0.1 means only subscribers watch; over 1 means search or browse carries it.
   - **Unlist candidates**: under 0.3x and older than 90 days. Unlist, never delete; deleting loses the data.
3. Write one fix per channel surface (banner, trailer, playlists, description; see the reference) and one variable to
   test in the next upload. Not five.

## Rules

- Fix the channel page only after about six videos. Before that, every hour goes into videos.
- The trailer or featured video is the best performer, not the newest.
- Never compare with other channels' CTR or retention. You only see their public view counts.

## Output

The filled channel card, or the audit table plus: the smallest factor, one surface fix, one variable to test next.
