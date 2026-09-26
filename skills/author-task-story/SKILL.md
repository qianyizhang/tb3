---
name: author-task-story
description: Create or revise canonical TB3 stories for integrated task explainers and catalogue expansion. Use video-explainer to export an established story.
metadata:
  version: "1.0.1"
---

# Author a Task Story

Explain one actual task condition through an inspectable operation. The canonical
`.story.md` owns words and integer-frame timing; briefs and findings own claims.

## Resolve the condition

From the active `workbench.toml`, read repository/group guidance,
`presentation/EXPLAINERS.md`, the entry's leaf catalogue, brief and row in
`presentation/EXPLAINER-LEDGER.json`. Read a finding only for result claims;
use `explain-medical-evidence` if their interpretation is unresolved.

Identify raw inputs, supplied assistance, output and reference visibility.
Preserve search versus supplied-location work, coordinate frames and annotation
coverage. Distinguish teaching fixtures from source data.

## Draft and bind

Use `med story recipes` to select an operation that fits the condition. Record
missing recipes or source dependencies explicitly; visual resemblance is not enough.

Preview with `med story new ENTRY STORY_ID --recipe RECIPE --preview`; omit
`--preview` to write an unbound draft. Replace every authoring marker with sourced
copy, scope and meaningful beats. Preserve channel continuity or declare a cut.
Run `med story check PATH`, then move the finished draft into its owner's
`stories/` directory and explicitly set the leaf catalogue's `illustration.story_id`.

Reuse the shared player, stage, recipe types and assets. Numerical fixtures need
inspectable derivations and establish no medical accuracy. Change scientific
records only within the requested scope.

## Review

Build the frontend and use `med story batch` for local review outputs. Inspect
first/decisive/ending frames, motion, output, legends, captions, narrow layout and
no-GPU behavior; visibly separate references from solver inputs.

Retain reviewer, source snapshot, inspected entries and limits. Compilation,
binding and verified export do not assign visual acceptance. Update the ledger
only for entries actually reviewed; one family story does not complete its siblings.
Preserve earlier receipts.

At closeout, read **Active lessons** in the
[feedback ledger](references/feedback-ledger.md). Record material reusable feedback
with the invoked version and source; routine success needs no entry.
