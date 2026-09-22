# Task taxonomy refactor — 2026-09-22

User request: assess the taxonomy in
[Refactor Docs Tasks](chatgpt-conversation://6ab23169-b548-83e8-abe1-6686ed1954d1)
and refactor it properly. Implementation source:
[current task](codex://threads/01a0c829-8fec-7262-8a65-c76a593724f9).

## Findings and implementation decision

Actor: **user** authorized taxonomy refactoring. Actor: **assistant** selected
and implemented the axis definitions, catalogue composition, classifications and
navigation. The user did not separately approve every category or display name.

The earlier proposal correctly separated supplied-mask audit, raw segmentation,
correspondence and supporting research. Its top-level buckets still combined
operations with subject-specific workflows. The maintained
[taxonomy guide](../docs/task-taxonomy.md) now distinguishes primary deliverable,
secondary operations, agent work, research role, research owner and repository.
The guide records boundary examples and reopening criteria.

The existing Task Explorer now composes group-owned catalogues and the external
survey. It supports capability/repository views, role filtering and a filter for
case solving, method implementation or tool-workflow operation. Existing
repository, definition, case and assistance deep links remain navigable.
No new experiment record type or score aggregation was introduced.

## Source-backed boundaries

- The four CT organ experiments share one definition, with explicit CT-only and
  callable-LiteMedSAM assistance plus each experiment's original protocol.
- Dental original/v2/v3 and longitudinal CT original/revised/candidate contracts
  remain separate definitions under related-task families. Candidate curation
  retains its `endpoint_only` comparison and probability/reason sidecar.
- Supplied-coordinate CT candidate judgment is recognition; context inference is
  reporting. Neither silently counts as full-volume lesion discovery/tracking.
- RESECT remains correspondence despite its audit name. Its older proposed
  three-case brief remains distinct from the later two-query pilot.
- MRI frame association is data engineering. The historical research-owner ID
  remains stable; anatomical labeling now names the group's broader current scope.
- Cardiac BR-025/027/029 are supporting author studies. Supplied-mask BR-035
  remains a motion/mechanics task, with material truth separate from mesh fit.
- BR-033 is linked twice with distinct scopes: airway agent pilot and TopBrain
  source/direct-model screen. The historical record is neither split nor merged.
- The external catalogue classifies definitions by deliverable, including health
  record conversion, record QA, prediction and eligibility. Method-building and
  direct case solving remain separate filters.

## Coverage and validation

The implemented catalogue contains 200 authored entries: 159 external definitions,
31 internal task definitions/revisions and 10 supporting entries. Related
navigation families can contain several definitions. All 59 internal experiment
IDs are linked; all 284 imported source records retain their exact inventory IDs
and brief/condition links. Source records, definitions, cases and attempts are
separate counts. These are the refactor's dated inventory counts, not a claim of
scientifically comparable tasks or executed trials.

New checks reject omitted experiments, unscoped or unknown links, incorrect group
owners, unknown axes and families crossing primary task boundaries. Regression
checks cover composition, immutable source resolution, legacy navigation and
new capability/role/agent-work filters. Browser outputs and screenshots remain
local under `runs/task-taxonomy-20260922/`.

Validation completed on an isolated staged snapshot based on `d85f388`: all
98 offline tests and the full `make check PYTHON=python3.12` gate passed. Browser
checks covered 200 briefs, 428 condition selections, 284 imported source records
and all 59 internal experiments, with no page errors or remote requests. The
portable snapshot explicitly reports its two pre-existing optional Imaging-101
preview files as absent; the local preview resolves them. Browser-free JavaScript
checks and formatting also passed.

The simultaneous documentation-cleanup task owns recipe fixes, method-index
history relocation, doc-link checker changes and historical artifact retirement.
This change owns taxonomy metadata, task briefs, renderer, relevant navigation
prose and tests. Frozen prompts, scientific scorers, runs and original outcomes
are not modified by this taxonomy refactor.

Reopen classification when a new/changed contract exposes an unclear boundary,
a mixed historical record needs a more precise scope, or reader feedback shows
that a family hides a meaningful difference. Clinical/reference disputes still
use the existing issue and review workflow.

## Illustration coverage follow-up

Actor: **user** requested intuitive illustrations for every named task/group.
Actor: **assistant** added ten study-specific input/output diagrams for the
previously unillustrated supporting entries and seven conceptual fallbacks for
entries with curated source images. Source images remain the first choice;
missing optional media retain a notice alongside their schematic fallback.

The study drawings distinguish reference-box tool calibration, provenance
tracing, geometric shortcut controls, anatomy curation, registration diagnostics,
all-phase contours, sparse anchors, material motion and vessel-source screening.
“Study output” identifies supporting research. Matching legends separate supplied
anchors, predictions and references; no drawing represents a measured result.

All 200 definitions have an Overview visual, including each variant in the 140
navigation families/entries. The builder now rejects missing required visuals or
incomplete illustration metadata. Browser coverage checks all 428 condition
selections and exercises missing-image fallbacks for each of the seven native
examples. The ten new studies and seven fallbacks also have a local visual-review
contact sheet; screenshots and the updated preview live under
`runs/task-illustrations-20260922/`.
