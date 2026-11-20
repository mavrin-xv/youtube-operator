# Contributing

Useful contributions, roughly in order:

1. **A live API run.** The `--channels` and `--video` paths follow the documented YouTube Data API but were not run during development. A report with the command, the quota used and any error is the most useful thing you can send. Remove your key and channel ids first.
2. **Studio export formats.** Column names in Studio exports change and differ by language. If `video_review.py` cannot read your export, send the header row and two anonymised lines.
3. **Rules from real use.** A title the linter scored high that flopped in Test & Compare, a script warning that cries wolf, a diagnosis that pointed the wrong way. Include the before and after.
4. **Word lists for other languages.** Bait words, weak transitions and banned openers are English only.
5. **Platform reports.** macOS and Linux runs of the checks in [AGENTS.md](AGENTS.md); so far only Windows with Git Bash has been tested.

Before a pull request, run the checks in [AGENTS.md](AGENTS.md). Keep examples on the invented woodworking channels, Acme or Northwind.

Scripts stay on the Python standard library. Production tools (editors, renderers, voice) stay out of this pack; link to them from your own setup instead.
