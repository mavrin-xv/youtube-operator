---
name: publish-package
description: Builds and checks everything that ships with a YouTube video besides the video itself: description, chapters, tags, hashtags, thumbnail file, end screen, cards, playlist, disclosure and tagged links. A linter checks YouTube's limits (100-character title, 5,000-byte description, 500-character tags, 15 hashtags, chapter rules, thumbnail size) and catches leftover placeholders; a builder turns script timings into valid chapters. Use when someone says "write the description", "make chapters", "ready to publish", "publish checklist", "tags for my video", "end screen", "why are my chapters not showing", or pastes a description.
---

# Publish package

A broken chapter list silently does nothing. A placeholder left in the description ships to every viewer. This skill
makes the package correct before the publish button, then plans the first 48 hours.

## Inputs

- Final title, the script (or its timing table), the video length, the thumbnail file.
- The owned links and their utm slug from the video card.
- Whether the next video is public yet (only public videos can be linked).

## Procedure

1. **Description.** Fill `templates/description.md`:
   - Lines 1 and 2 carry the answer or the promise with the viewer's search phrase (they show in search and above
     "more").
   - 2 to 4 lines of context: what you measured or showed, the conditions, what is not covered.
   - Chapters, sources and method, the next video (only if public), one specific question for the comments, the fixed
     footer.
2. **Chapters.** Build them from the script timings, then edit the titles into small promises (not "Intro",
   "Part 2"):

   ```bash
   python3 ../retention-script/scripts/script_lint.py script.md --wpm 160 --format json > timing.json
   python3 scripts/publish_lint.py --chapters-from timing.json --duration 7:05
   ```

   After the edit, re-time them against the real cut. YouTube only shows chapters if the first is at 00:00, there
   are at least 3, and each is at least 10 seconds long.
3. **Tags**: 5 to 10, mainly the main term and its common misspellings. They matter little; spend two minutes.
4. **Hashtags**: 0 to 3. Only the first 3 show above the title; more than 15 and YouTube ignores all of them.
5. **Lint the whole package:**

   ```bash
   python3 scripts/publish_lint.py --title "..." --description description.md --tags "a,b,c" \
       --duration 7:05 --thumb thumb.png --owned yourdomain.com
   ```

   Exit 1 means a blocker. Limits and their sources: [references/limits.md](references/limits.md).
6. **Human checklist**: `templates/publish-checklist.md`. Click every link once.
7. **Distribution plan** for the first 48 hours: [references/distribution.md](references/distribution.md).

## Rules

- Every owned link carries `utm_source=youtube&utm_medium=video&utm_campaign=<slug>`, so the business result is
  measurable.
- Never link an unpublished video in the end screen, a card, the description or a playlist.
- End screen in the last 5 to 20 seconds: one specific next video or a playlist, plus subscribe. The spoken ending
  leads into it.
- Cards: one or two, at the moment a related video is the natural next step, never in the first 30 seconds.
- Altered or synthetic content disclosure: yes for realistic people, places or events that did not happen. Animated
  explainers and diagrams usually do not need it. Check YouTube's current policy page when unsure.
- Mass-produced, near-identical videos risk demonetisation. Each video needs its own research and structure.
- No magic hour. Publish when you can watch the first two hours for technical problems.

## Output

The final description, the chapter block, the tag list, the linter result (exit code and lines), the ticked
checklist, and the 48-hour distribution plan.
