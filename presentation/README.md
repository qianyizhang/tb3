# Medical presentation

Groups own their authored story, source-linked card, figures and figure sources.
This directory owns the shared index/player, references, exact export manifest
and historical-path relocation map. Run `python3.12 scripts/med present --serve
--local-media`; omit `--local-media` for a portable static build.

The local player uses existing derived arrays; missing data does not cause scans
to download or models to run. All seven stories have portable prose. Six retain
scientific figures and guided tours. Longitudinal reading is explicitly exploratory.
Use `python3.12 scripts/med assets` to verify exact figure derivation. `scripts/med-media`
is the media export entry point; see [its tool guide](tours/TOOL.md).

Original figure-source bytes and attribution are retained under group ownership.
relocations.json resolves historical paths without rewriting hash-bound source
receipts. Tour data and movies are ignored, with static figures in Git. The old
interview publication remains recoverable through archive/manifest.json.

## Task Briefs and the external survey

The [Task Brief rulebook](task-explorer/RULEBOOK.md) defines compact explanations
with explicit assistance and input-first visuals. The source survey lives under
`discussions/medical-agent-repository-survey/`; internal briefs stay with groups.
Build the standalone explorer with `python3.12 scripts/med brief build`, check it
with `python3.12 scripts/med brief check`, or scaffold a proposed brief with
`python3.12 scripts/med brief new --help`. None of these commands launches a trial.
