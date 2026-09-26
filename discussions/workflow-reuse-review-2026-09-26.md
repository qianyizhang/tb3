# Workflow reuse review — 2026-09-26

The skills and scaffolding are implemented. The follow-up polish removes repeated
instructions, obsolete proposal text and duplicated export bookkeeping while
preserving inspection, provenance and acceptance boundaries.

## Decisions and scope

The user requested a survey and reusable skills/scaffolding, then directed repairs
and completion, followed by simplification and a commit. The assistant treated
expansion as the proposed workflow tooling. The separate explainer catalogue
remains **13/205 reviewed entries**; no new binding or acceptance status is claimed.

The [discussion record](records/workflow-reuse-review-2026-09-26.json) retains
actors, source task, original survey hashes and validation scope. The
[original survey and implementation report](../.local/skill-polish-20260926/before/discussions/workflow-reuse-review-2026-09-26.md)
is retained locally. Earlier rendering and research outcomes remain historical
evidence, not fresh acceptance of subsequent edits.

## Findings and repairs

| Observed gap | Delivered repair |
| --- | --- |
| Installed video instructions differed under the same version; their workspace link would break after installation. | Canonical/standalone routing comes first; workspace contracts resolve from `workbench.toml`. Complete skill trees are compared before mirroring. |
| Story authoring repeatedly assembled the same recipe structure. | `author-task-story` and `med story recipes/new/check` reuse compiler schemas, create unbound drafts and reject unfinished authoring fields. |
| Export closeout depended on temporary batch scripts. | `med story batch new/run/check` pins source/build inputs, retains failures, verifies outputs and produces a local gallery. Visual acceptance remains a review decision. |
| Study comparisons need explicit source, assistance and scoring boundaries. | `design-medical-study` provides a compact condition table and routes to existing idea/protocol, dataset and recovery owners. |
| Earlier evidence-skill condensation lost inspection and attribution requirements. | Preserve v1.1 inspection rules and add behavioral review cases. No fresh agent evaluation or recovery claim. |
| Sampled WSI export placed a region name over a class marker. | Move the region label above its rectangle; retain the original export and inspect the regenerated views. |

The retained [WSI comparison](../groups/lesion-localization/findings/wsi-astra-sol-method-comparison.md)
and [trace-analysis investigation](trace-analysis-regression-2026-09-23.md) informed
these boundaries; this workflow review does not reassess their medical conclusions.

## Current owners

- [Skill lifecycle](../docs/skill-lifecycle.md): versions, feedback and installed mirrors.
- [Explainer contract](../presentation/EXPLAINERS.md): authoring, binding and export commands.
- [Architecture](../docs/architecture.md): compiler, authoring, batch and validation modules.
- [Research design](../docs/research-design.md), [datasets](../datasets/README.md) and
  [reproduction](../docs/reproduce.md): study, source and recovery contracts.
- [Per-entry ledger](../presentation/EXPLAINER-LEDGER.json): 6 reviewed spatial,
  7 reviewed planar, 42 awaiting operation work/review, 102 source-contract
  dependencies and 48 source-input dependencies.

## Evidence and limits

The initial implementation passed the pinned-index repository gate (**180 tests**)
and browser-free frontend checks. Two fresh exports passed receipt verification
and full decoding (**1,248 frames at 24 fps**); first, decisive and ending stills
were inspected. Full motion, narrow layout, no-GPU behavior and all other catalogue
entries received no new visual acceptance in this task.

[Implementation receipts](../.local/skill-expansion-20260926/REPORT.md) ·
[Two-story gallery](../.local/skill-expansion-20260926/batch-final/review.html) ·
[Polish and commit validation](../.local/skill-polish-20260926/REPORT.md)

No medical trial, source-data acquisition, runtime installation or publication was
performed. Reopen when a real invocation exposes a gap, source/recipe ownership
changes, or the separate remaining catalogue expansion is selected.
