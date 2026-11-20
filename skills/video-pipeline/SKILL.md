---
name: video-pipeline
description: Runs one YouTube video from idea to 28-day review as a gated pipeline (lane, topic, packaging, script, publish, review) and routes each stage to the right skill in this pack. Keeps one video card per video so nothing is decided twice. Use when someone says "plan a YouTube video", "next video for my channel", "what should I do next on YouTube", "take this idea to publish", "where is this video stuck", or starts any YouTube task without naming a stage.
---

# Video pipeline

One video, one card, six gates. The card (`templates/video-card.md`) is the single place where decisions live; every
stage reads it first and writes its result back.

Production (filming, editing, animation, voice) is not in this pack. The pipeline hands the approved script and
package to whatever production you use and picks the video up again at the publish stage.

## Route the request

| The user has or asks for | Go to | Gate it must pass |
|---|---|---|
| no channel card, or "what should my channel be about" | `channel-lane` | A |
| "what should I make next", a list of ideas, neighbour channels | `topic-finder` | B |
| a chosen topic, "title and thumbnail", "which title is better" | `packaging-lab` | C |
| an approved package, "write the script", a draft script | `retention-script` | D |
| a finished video, "description", "chapters", "ready to publish?" | `publish-package` | G |
| Studio numbers, "why is this video not doing well", "CTR", "retention" | `analytics-loop` | I |

If the request skips a stage, check the card for the earlier gate. A missing gate is the first job, unless the user
says the earlier stage is done elsewhere; then write "done outside" with their words and the date.

## Gates

Full checklists: [references/gates.md](references/gates.md). In short:

- **A, lane:** the channel card names one viewer, one outcome, one lane sentence and one primary business metric.
- **B, topic:** score at least 60 on the matrix, contribution and evidence above zero, at least one quoted demand
  signal or an outlier of 3x or more.
- **C, packaging:** three different concepts written; the pick and the backup pass the truth, phone and stranger tests;
  `title_score.py` reports no FAIL.
- **D, script:** `script_lint.py` exits 0; every claim has a register row; the first line confirms the package.
- **G, publish:** `publish_lint.py` exits 0 and the human checklist is ticked.
- **I, review:** a review at 48 h, 7 d and 28 d, each written into the card; one change at a time, logged in the
  decision journal.

## Procedure

1. Find or create the video card. Fill the front matter (`status`, `channel`).
2. Read the channel card. If it is missing, stop and run `channel-lane` first; topics without a lane drift.
3. Run the stage the request needs, through its skill. Write the result into the card.
4. Check the gate. If it fails, say which line failed and what would make it pass. Do not move the status on.
5. At the end of every turn, tell the user the card status and the single next action.

## Rules

- Packaging comes before the script. The script exists to deliver the package; writing it first produces a video that
  is hard to package.
- One change at a time after publish. Two changes at once teach nothing.
- Never compare a video with other channels' CTR or retention; you cannot see them. Compare with your own medians.
- Never link an unpublished video anywhere (end screen, card, description, playlist).
- Never buy views, use view bots or sub-for-sub. They corrupt the data the loop learns from.
- A human approves the package, the script and the publish. The agent proposes.

## Output

At each stop: the card section that changed, the gate result (pass or the failing line), and one next action.
