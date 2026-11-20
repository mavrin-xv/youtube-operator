# AGENTS.md

Notes for coding agents (Claude Code, Codex, Cursor, others) working on this repository.

## What this is

Seven Agent Skills for running a YouTube channel from lane to 28-day review. The product is the `SKILL.md` text plus small stdlib Python scripts. There is no server, no database and no production engine.

## Layout

- `skills/<name>/SKILL.md`: what the agent does and when. Frontmatter has `name` (same as the folder) and `description` only. Keep each under 500 lines; long material goes in `references/`.
- `skills/<name>/scripts/*.py`: Python 3.8+, standard library only, each with `--help`. Network calls only in `outlier_finder.py --channels` and `comment_questions.py --video`, and only with `YOUTUBE_API_KEY` from the environment.
- `skills/<name>/templates/`: files the agent copies and fills (video card, channel card, claims register, description, checklists, postmortem, decision journal).
- `examples/data/`: an invented woodworking channel and its neighbours. Sample files carry a `fetched` date; scripts read them as of that date so outputs stay stable.
- `examples/script.md`, `examples/description.md`, `examples/data/thumb-small.png`: problems planted on purpose (weak transitions, outro filler, an untagged number, a link without utm, a thumbnail under 1280x720). Do not fix them.

## Rules

- Never call `search.list` (100 quota units). Use `channels.list`, `playlistItems.list`, `videos.list`, `commentThreads.list`.
- Never print or save the API key.
- Never claim to know another channel's CTR or retention. Public numbers only.
- No real channel names, people, companies or ids in examples. Use the invented woodworking channels, Acme or Northwind, and example.com.

## Checks before you finish

```bash
E=examples/data
for f in skills/*/scripts/*.py; do python3 "$f" --help >/dev/null || echo "FAIL $f"; done
python3 skills/channel-lane/scripts/channel_audit.py $E/own-channel.json            # median 1,779, 2 outliers, 3 misses
python3 skills/topic-finder/scripts/outlier_finder.py --sample $E/neighbours.json   # 8 videos at 2.0x or more, top 10.49x
python3 skills/topic-finder/scripts/topic_score.py $E/topics.csv                    # #1 86 pass, 3 "research first"
python3 skills/packaging-lab/scripts/title_score.py --file $E/titles.txt --keyword tabletop; echo $?   # one FAIL, exit 1
python3 skills/retention-script/scripts/script_lint.py examples/script.md --wpm 160 --target 180 --claims examples/claims-register.md   # 2:16, 9 WARN, exit 0
python3 skills/publish-package/scripts/publish_lint.py --title "Why Your Tabletop Cupped" --duration 2:16 --description examples/description.md --thumb $E/thumb-small.png --owned example.com; echo $?   # BLOCK thumbnail, exit 1
python3 skills/analytics-loop/scripts/video_review.py --traffic $E/traffic.csv --retention $E/retention.csv --baseline $E/baseline.json --length 7:05   # packaging problem
bash -n install.sh
```

If you change a rule or a weight, update the expected results here and the outputs in `examples/walkthrough.md` and the README quick start.
