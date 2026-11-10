# Timeline snapshots

Each `<YYYY-MM-DD>.html` and `<YYYY-MM-DD>.md` is a dated snapshot written by `uv run mar timeline --keep`. They merge the author's questions, decisions, rule and oracle changes, runs and git commits in time order. The `.html` is self-contained (open it in a browser); the `.md` is the same entries grouped by day, readable on GitHub, with kind labels in bold and links as relative paths.

These files hold the author's own words (verbatim question and change quotes). Review them before any public release.

A snapshot is a record, not a live page: links to `runs/` point at ignored files that exist only on the machine that made it. Links to `experiments/kept/` work everywhere. A later snapshot never overwrites an earlier day's file; the same day overwrites itself.
