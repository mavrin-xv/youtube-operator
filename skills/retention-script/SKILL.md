---
name: retention-script
description: Writes and checks a spoken YouTube script built for retention, after the package is approved. Picks a structure, makes the first 30 seconds confirm the title and thumbnail, plans a pattern reset every 45 to 90 seconds, places a payoff before the midpoint, ends on a takeaway instead of an outro, and keeps a claims register for every fact and number. A linter estimates length from a measured speaking rate and flags throat-clearing openers, weak transitions, long sentences and untagged numbers. Use when someone says "write the script", "script for my video", "check my script", "my retention drops", "hook for the video", "make it shorter", or pastes a draft script.
---

# Retention script

The script delivers the package. Its job in order: keep the promise in the first 30 seconds, change what the viewer
understands in every block, and end while something is still happening.

## Inputs

- The approved package from the video card (title, thumbnail, first line).
- The proof you will show, and its sources.
- Target length, and the measured speaking rate of the voice (words per minute from a real take; 150 is only a
  starting guess, voices vary a lot).

## Procedure

1. **Pick one structure** from [references/structures.md](references/structures.md) (problem, causes, fix; myth
   list; race; journey of one object; before and after; teardown; build-along; question ladder). Name it in the
   video card.
2. **Write the first 30 seconds** by the rules in [references/first-30-seconds.md](references/first-30-seconds.md):
   the first line confirms the package in other words; the question is clear by 0:05; by 0:30 the viewer knows why
   it matters and what shape the answer takes ("three causes, one test").
3. **Write the body.** Every block opens a small question and closes it. Transitions are causal ("so", "but",
   "which means"), never "next", "also", "moving on". Plan a reset every 45 to 90 seconds: a new visual, a
   full-screen insert, a question, a change of place. Put a concrete payoff before the midpoint.
4. **Write the ending**: the takeaway in one sentence, then the next question or the next video. No "thanks for
   watching", no long outro. Leave the last 5 to 20 seconds for the end screen while something still happens.
5. **Register every claim.** Copy `templates/claims-register.md`, one row per factual sentence and every number,
   and tag the sentence in the script with `[c1]`, `[c2]`. No row means cut it or reword it to what you can source.
6. **Mark the script** for the linter: `## Block` headings, `[direction lines]` in brackets for visuals, `[payoff]`
   before the first payoff sentence.
7. **Lint it:**

   ```bash
   python3 scripts/script_lint.py script.md --wpm 160 --target 420 --claims claims.md
   ```

   Blockers (exit 1): a throat-clearing opener, a claim tag with no register row. Warnings: long sentences, weak
   transitions, stretches without a reset, a late payoff, outro filler, untagged numbers, a length miss over 10%.
   Fix them or write why you keep one.
8. **Read it aloud once**, or run it through text to speech. Rewrite anything you trip over.
9. **Cheap tests** with fresh readers (people or agents who did not write it): explain the main idea back in three
   sentences; which sentences can go without loss; what is wrong or oversimplified. Fix what two tests flag.

## Writing for the ear

- One idea per sentence, mostly 3 to 15 words. The linter flags anything over 20.
- Numbers as you would say them ("about one percent"), each with a register row.
- The picture before the term: show the bowl-shaped board, then say "cupping".
- Length is what the answer needs. Never pad to reach a length for ads; a tight 5:40 beats a padded 8:10.

## Rules

- No logo sting, no "welcome back", no "in this video", no "before we start, subscribe".
- Do not open a loop you will not close. Over-promising in the opening makes the retention cliff.
- If the video runs past 8 minutes, put a second payoff shortly after 8:00; that is a common drop zone.
- A human approves the script before recording.

## Output

The script file, the claims register, the linter output, and the timing table (block, start, seconds).
