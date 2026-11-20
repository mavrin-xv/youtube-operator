# YouTube metadata limits

Checked by `publish_lint.py`. Limits change; when in doubt, check the YouTube Data API reference for the video
resource and the YouTube Help pages named below.

| Field | Limit | Source |
|---|---|---|
| Title | 100 characters, no < or > | YouTube Data API, `videos` resource, `snippet.title` |
| Description | 5,000 bytes, no < or > | same, `snippet.description` |
| Tags | 500 characters in total; a tag with a space counts its surrounding quotes | same, `snippet.tags` |
| Hashtags | first 3 shown above the title; more than 15 means all are ignored | YouTube Help, "Use hashtags for YouTube videos" |
| Chapters | first at 00:00, at least 3, each at least 10 s, in order | YouTube Help, "Video chapters" |
| Thumbnail | 1280 x 720 recommended (640 px wide minimum), 16:9, under 2 MB, JPG, PNG or GIF | YouTube Help, "Add video thumbnails" |
| End screen | added in the last 5 to 20 s of the video | YouTube Help, "Add end screens to videos" |

The linter blocks thumbnails under 1280 x 720 even though YouTube accepts 640 px wide: a small file looks soft on
TVs and large screens.

## Chapter titles

- A small promise or finding ("Cause two: the wood was not ready"), not "Part 2".
- Chapters help search (key moments) and let viewers jump. On browse videos they can lower average view duration a
  little; for search-first channels keep them.

## Placeholder catch

The linter blocks `TODO`, `TBD`, `XXX`, `lorem ipsum`, `[link]` and `{{...}}`. Before upload also search your own
markers (for example `<video_id>`, which the < > rule catches).
