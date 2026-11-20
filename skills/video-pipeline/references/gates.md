# Gates

A gate is passed when every line is true. Write the result into the video card with the date.

## A. Lane (channel card)

- [ ] Viewer: one real person, what they already know, what they are trying to do this week.
- [ ] Outcome: what the viewer can do after a video that they could not before ("know more" fails).
- [ ] Lane sentence a stranger can repeat: "<who> learns <what> through <format>".
- [ ] Primary business goal and its metric (ads, sponsors, leads, own product, trust).
- [ ] Main traffic source chosen (search, suggested or browse) and why.
- [ ] Series grammar: what repeats every episode, what is new every time.
- [ ] A "never on this channel" list.
- [ ] A rhythm you can hold for six months.

## B. Topic

- [ ] The viewer question written in the viewer's words, with its source.
- [ ] Priority score of 60 or more (`topic_score.py`).
- [ ] Contribution above 0 and evidence above 0 (hard gate).
- [ ] At least one quoted demand signal, or a neighbour outlier of 3x or more on the same question.
- [ ] Three competing videos named, and how this one is different.
- [ ] The next video it leads to.
- [ ] The utm slug, final now.

## C. Packaging

- [ ] Three concepts of different types (proof, mechanism, consequence), not three wordings of one.
- [ ] `title_score.py` shows no FAIL for the pick and the backup.
- [ ] Truth test: every claim in the title and thumbnail has a timestamp in the video that shows it.
- [ ] Phone test: the thumbnail at 120 px wide, next to six real thumbnails from the same search, still names the
      subject and the reason to click.
- [ ] Stranger test: someone (or a fresh agent) who sees only the package says what the video will show; the answer
      matches the promise.
- [ ] The first spoken line confirms the same promise in other words.

## D. Script

- [ ] Structure named (see the retention-script skill).
- [ ] `script_lint.py` exits 0 with `--claims`, and the warnings are fixed or accepted with a reason.
- [ ] The question is clear by 0:05, the reason to stay by 0:30.
- [ ] Every block changes what the viewer understands.
- [ ] A concrete payoff before the midpoint.
- [ ] Ending: one-sentence takeaway, then the next question. No outro.
- [ ] Read aloud once. Anything you trip over is rewritten.
- [ ] A human approved the script before recording.

## G. Publish

- [ ] `publish_lint.py` exits 0 on the final title, description, tags, duration and thumbnail file.
- [ ] Every link clicked once; owned links carry utm.
- [ ] End screen and cards point only at public videos.
- [ ] Captions checked (auto captions corrected for names and numbers).
- [ ] Playlist set; altered or synthetic content disclosure decided.
- [ ] Two or three variants ready for Test & Compare.
- [ ] A human said yes.

## I. Review

- [ ] 0 to 2 h: technical check only.
- [ ] 48 h: packaging read by traffic source; at most one change, logged.
- [ ] 7 d: `video_review.py` output in the card; three observations, one hypothesis.
- [ ] 28 d: postmortem written; decision journal updated; the lesson fed into the next topic score.
