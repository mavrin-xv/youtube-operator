# Metric dictionary

| Metric | What it really measures | Read it with |
|---|---|---|
| Impressions | thumbnail shown on YouTube surfaces (counted when at least half visible for about a second); excludes external embeds | traffic source |
| Impressions CTR | share of those impressions that became views | traffic source, volume, age of the video |
| Views | all starts, including external and end screen | |
| Average view duration (AVD) | minutes watched per view | video length |
| Average percentage viewed | AVD divided by length | length: short videos score higher naturally |
| R30 (intro retention) | share still watching at 0:30 | the package promise |
| Retention curve | where people leave | the script at that timestamp |
| Relative retention | your curve against similar-length videos on YouTube | |
| Watch time per impression | CTR x AVD; close to what YouTube distributes on | |
| End screen element CTR | share who clicked to the next video | the spoken ending |
| New and returning viewers | whether the channel builds a habit | series design |
| Subscribers per 1,000 views | whether the video makes people want more | the ending, the lane |
| Business metric | tagged visits, sign-ups, calls | the description and the pinned comment |

## Where the numbers come from

- Studio exports: everything above, including impressions and impressions CTR.
- YouTube Analytics API: views, watch time, average view duration, retention by elapsed ratio, traffic sources. It
  does not return impressions or impressions CTR.
- Your web analytics: visits and sign-ups from links with `utm_source=youtube`.
- Other channels: public view counts only. Never claim to know their CTR or retention.

Studio and the API can differ by a few percent for the last two days. Use one source per comparison.
