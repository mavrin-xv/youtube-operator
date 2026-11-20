---
name: packaging-lab
description: Designs the YouTube title, thumbnail and first spoken line as one promise before the script exists. Writes three different concepts, scores title drafts with a rule-based lint, runs the truth, phone and stranger tests, and sets up a thumbnail and title A/B test in YouTube Test & Compare. Use when someone says "title for my video", "thumbnail idea", "which title is better", "score these titles", "A/B test thumbnails", "my CTR is low", "packaging", or pastes title drafts.
---

# Packaging lab

The title, the thumbnail and the first line are one promise in three forms. If the package is weak, the script will
not save the video; if the package is written first, the script has to deliver something specific.

## Inputs

- The topic block of the video card: viewer question, proof, main traffic source.
- Optional: 6 real thumbnails from the same search or the same suggested column (screenshots), for the phone test.

## Procedure

1. **Three concepts, not three wordings.** For the one promise, write:
   - **Proof**: show the result or the measurement (a number, a before and after).
   - **Mechanism**: show the thing that breaks or the process.
   - **Consequence**: show what the viewer loses if they do nothing.

   Each concept is a title, a thumbnail sketch (0 to 4 words of text, at most 3 visual elements) and a first
   spoken line. Rules for each part: [references/title-rules.md](references/title-rules.md) and
   [references/thumbnail-checklist.md](references/thumbnail-checklist.md).
2. **Lint the titles.** Put 5 to 10 drafts in a file and run:

   ```bash
   python3 scripts/title_score.py --file titles.txt --keyword "viewer phrase" --thumb "THUMB TEXT" --surface search
   ```

   It checks length, the keyword in the first 40 characters, a concrete number or object, bait words, caps,
   exclamation marks and thumbnail overlap. It is a lint, not a prediction: it drops weak drafts, it cannot pick
   the winner. Any FAIL (over 100 characters, or < or >) is not allowed.
3. **Run the three tests** on the best two concepts:
   - **Truth**: every claim the title and thumbnail make, or imply, has a timestamp in the video that shows it.
   - **Phone**: the thumbnail at 120 px and 240 px wide, next to the 6 real thumbnails, light and dark mode, with a
     duration badge drawn in the bottom-right. Can a stranger still name the subject and the reason to click?
   - **Stranger**: give only the package to someone (or a fresh agent with no context) and ask "what will this video
     show you, and what will you know after?" If the answer differs from the promise, rework.
4. **Pick one and a backup.** Write both into the video card with the test results.
5. **Plan the A/B test.** Upload up to three variants in Test & Compare. How it decides and what to do with the
   result: [references/test-and-compare.md](references/test-and-compare.md).

## Rules

- Search videos: clarity first. The title carries the viewer's phrase; the thumbnail names the topic in 2 to 4 big
  words plus one object. Browse videos: the thumbnail tells the other half of the title and does not repeat it.
- The thumbnail text is ideally a line the video says. A stronger word the video never says is an overclaim.
- Never fake proof: no invented dashboard, benchmark or success state. An illustration must look like one.
- Keep the bottom-right corner clear (the duration badge covers it) and the bottom edge clear (progress bar).
- Do not edit the title or thumbnail while a Test & Compare test runs; it stops the test.
- Changing a package after publish is an experiment: one change, a reason from data, a dated log entry.

## Output

A table of the three concepts, the lint scores, the test results, the pick, the backup, and the Test & Compare plan.
