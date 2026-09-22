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

## Task Briefs and task navigation

The [Task Brief rulebook](task-explorer/RULEBOOK.md) defines compact explanations
with explicit assistance and input-first visuals. The source survey lives under
`presentation/external-tasks/`; internal briefs stay with groups.
The [task taxonomy](../docs/task-taxonomy.md) separates capabilities, research
roles and ownership. The root catalogue composes group catalogues and the survey;
it offers capability and repository views plus a supporting-research filter.
Build the standalone explorer with `med brief build`, check it with
`med brief check`, or scaffold a proposed brief with `med brief new --help`.
These commands use the installed native CLI and never launch a trial.

The explorer also has [dataset learning pages](../datasets/README.md): a searchable
source index, selected sample provenance, input/reference explanations and links
back to the tasks. Dataset pages are included in standalone and integrated builds.
