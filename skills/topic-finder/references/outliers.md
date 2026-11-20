# Outliers

## The ratio

`ratio = views of the video / median views of that channel's videos in the same window`

- Median, because one viral video pulls the mean up and makes every other video look like a miss.
- vidIQ's Outliers tool describes its score as a multiple of the channel's average, and its exact formula is not
  public. Expect our numbers to be higher than theirs for channels with one big hit. Neither is wrong; know which
  one you are reading.
- Same window only: a 2019 video with years of search traffic is not comparable with last month's upload.
- Skip videos younger than 14 days (`--min-age-days`); their views are still growing.
- Long and short videos live in different worlds. Use `--long-only` (drops anything of 180 s or less) unless you are
  researching Shorts.

## Tiers

| Ratio | Read |
|---|---|
| under 2x | normal for that channel |
| 2 to 5x | good: the topic or package pulled more than usual |
| 5 to 10x | strong: worth a line in your topic list |
| over 10x | breakout: study it, check if one outside event explains it (news, a big share) |

## What to take from an outlier

1. The question the video answered, in one line.
2. The one variable that differs from that channel's normal upload: topic, title shape, thumbnail type, format, length.
3. Whether your channel can answer the same question with something only you can show.

What not to take: the title, the thumbnail, the exact angle. You are a different channel with a different audience.

## Shape lift

`outlier_finder.py` tags each title with simple shapes (number, question, how or why, versus, first person,
brackets, negative, money). The table compares the share of each shape among outliers with its share among all
videos. A lift of 2x on 20 videos is a hint to test, not a law. Small samples swing.

## Quota (YouTube Data API v3)

| Call | Cost | Used for |
|---|---|---|
| channels.list (forHandle or id) | 1 unit | the uploads playlist id and subscriber count |
| playlistItems.list | 1 unit per 50 items | the upload list |
| videos.list | 1 unit per 50 videos | views and durations |
| commentThreads.list | 1 unit per 100 comments | comment questions |
| search.list | 100 units | never used here |

Default quota is 10,000 units a day per project. 15 channels x 100 videos is about 75 units.

## Getting a key (free)

1. Create a project in the Google Cloud console.
2. Enable "YouTube Data API v3".
3. Create an API key, restrict it to that API.
4. `export YOUTUBE_API_KEY=...` in your shell. Never commit it.
