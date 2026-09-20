# Medical presentation

Groups own authored stories, source-linked cards, figures and source notices.
This directory owns the shared index and interactive tour renderer. Run
`uv run med present --serve`; add `--local-media` after restoring tour inputs.

All seven stories have portable prose. Six retain scientific figures and guided
tours; longitudinal reading remains exploratory. `med check --assets` verifies
17 exact figure extractions when needed. `med media prepare` restores the retained
derived tour snapshot from its canonical input manifest, and `med media check`
checks its display invariants. Missing local inputs never trigger downloads.

The CLI and frontend consume the same status vocabulary. Group stories display
current experiment review flags beside the authored historical synthesis. Runtime
reads do not hash every evidence file, poll jobs or use pathname relocation maps.
Historical source locators remain provenance, not fallback file resolution.

Use [the media guide](tours/TOOL.md) for declared rendering dependencies and
`npm run media -- --help` for video/still options. Generated arrays and videos stay
local; static figures remain in Git. The old interview is recoverable through
`archive/manifest.json`. Literature context is recorded in
[the editorial source notes](editorial/external-source-notes.md).
