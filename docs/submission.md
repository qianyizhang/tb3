# Historical case-32 submission handoff

[Current report](../site/index.html) · [Research archive](archive.md)

**Selection superseded.** BR-010 paused promotion of the micro-boundary cases
over unresolved task-validity concerns. The later anatomy retrospective favors
BR-017 M02, with scope and repeatability caveats. This document preserves the
original package handoff; it does not endorse case 32 as the current lead.
[Reassessment](research-rounds/BR-010-mask-only-anatomy.md) ·
[Current anatomy verdict](anatomy-experiments.md#candidate-verdict).

## Task selected at the initial closeout

**Case 32: anatomical annotation audit.** Inspect one CT/segmentation pair,
review eleven labels, and return a JSON report with spatial witnesses for errors.
The controlled left-kidney extension adds 63 voxels while retaining 0.993572
Dice overlap with the source mask.

- [Original task instruction](../probes/revisions/br004-single/tasks/dicom-audit-32/instruction.md)
- [Frozen eight-task screen](evidence/br004-single-patient-freeze.json)
- [Terra review](evidence/br004-single-case-32-review.json)
- [Sol review](evidence/br004-sol-case-32-review.json)
- [Cross-model analysis and selection rationale](../catalog/analyses/br004-sol-followup.md)

The same original task bytes produced one normally completed Terra/max miss and
one Sol/xhigh miss. These are development-selected observations. They are not
three independent qualifying failures per required model.

## Clean submission

A separate task owns the clean package at **`../dicom-anatomy-audit`** (a sibling
repository/workspace). Its `README.md`, `EVALUATION.md` when available, and
`evidence/` own package-specific commands, results and packaging differences.
This path is a local handoff, not a published GitHub URL or a directory included
in this workshop clone.

At the final handoff on 2026-09-15, the clean repository was committed at
`77a3544` (42 files, approximately 6 MB), with `README.md` and `EVALUATION.md`
as entry points. No remote or publication was created.

The submission owner reported:

- 22/22 unchanged upstream Linux static checks;
- independent source-edit, decoded-SEG and ground-truth reconstruction;
- 76 grading controls and pilot replays;
- matched Docker oracle = 1 / nop = 0;
- 22/22 static checks and 76/76 controls from a clean staged Git archive.

Its task checksum is
`9fe26c9b1ec697d3a01972597854ada56ba47f40dfa78e1313baf184599ae9ec`.
Portable receipts are in that repository's `evidence/{static,local-checks,
controls,clean-archive,package-manifest,pilot-results}.json`. These are
handoff-reported checks; the workshop did not rerun them. The new package records
its metadata/canary/reviewer-material delta separately from the original task.

No new Sol or adversarial trial had launched at handoff. The original Terra/Sol
pilots remain the only model observations in the clean package. Consult its
`EVALUATION.md` for any later changes; this workshop's pilot table stays frozen.

## Assignment status boundary

The [original assignment](task.md) requests static/rubric/build/control checks,
three Sol/xhigh trials, three Opus/max trials, and one adversarial trial per
standard configuration. The workshop's pilot work alone does not complete that
matrix. The [requirements record](requirements.md) preserves the inspected
upstream rules and their pinned version.

The submission owner reported unavailable Claude credentials during preparation.
No missing run should be presented as a failure or a waived requirement.
Interview explanations are explicitly AI-assisted; any difference from upstream
human-authorship requirements belongs in the clean package's evaluation status.

No new experiment, publication or qualification run is part of this archive
cleanup. The workshop and submission have separate ownership and evidence.
