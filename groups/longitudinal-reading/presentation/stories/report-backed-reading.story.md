---
schema: 2
id: report-backed-reading
title: 'Proposed image reading with a private report reference'
locale: en
purpose: Explain the unexecuted BR-018 protocol for complete-examination reading, evidence-linked answers and bidirectional comparison to private report claims without implying a patient case or model result.
scope: Symbolic protocol only; zero admitted CT/report pairs and zero model trials.
recipe: report-reading-v1
asset_pack: symbolic-report-reading-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- groups/longitudinal-reading/presentation/briefs/tb3-report-backed-reading.md
- groups/longitudinal-reading/presentation/sources/report-backed-reading-audit.json
- groups/longitudinal-reading/presentation/sources/report-backed-reading-resolution.json
- docs/research-rounds/BR-018-report-backed-diagnosis.md
- presentation/task-explorer/report-reading/manifest.json
- scripts/build_report_reading_assets.py
---

# Symbolic protocol illustration — no admitted CT/report pair is available here; request real data through the official CT-RATE access page

## Confirm the absent case before the workflow

```beat
id: availability
scene: availability
frames: 120
caption: 'Symbolic protocol; no admitted CT/report pair. Access route: official CT-RATE page.'
narration: This is a symbolic explanation of a parked proposal. No examination and original report have been admitted together, and no model has tried the task. CT-RATE is a possible source, but gated access and case admission are still required.
visual: Keep the official CT-RATE acquisition warning above an empty examination slot, empty verified-context slots and the two observed zero counts. No patient-like pixels or report text.
channels:
  phase: [0, 0]
  helper: [0, 0]
  output: [0, 0]
  reference: [0, 0]
```

## Separate proposed inputs from the private report

```beat
id: input
scene: input
frames: 144
caption: Full examination and verified pre-exam context only
narration: If a case is later admitted, the solver would receive the complete native examination plus verified age, sex, indication, technique and available comparisons. Unknown context is omitted. The original report, patient mapping and claim table remain outside the solver.
visual: Show an abstract volume container and unfilled context slots. Keep the private evaluator ledger and proposed answer out of the DOM.
channels:
  phase: [0, 0]
  helper: [1, 1]
  output: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

## Map inspection to evidence locations

```beat
id: viewer
scene: viewer
frames: 168
caption: Search the whole volume, then identify a location
narration: The proposed orientation-aware viewer would move among axial, coronal and sagittal planes and record what was actually shown. An observation should link to an image filename and slice, or a physical RAS-millimetre location once a case affine is verified. This wireframe has no image voxels or numeric coordinates.
visual: Move orthogonal translucent planes through an abstract box and link one cursor to an empty evidence-location slot. Keep the official access warning visible.
channels:
  phase: [0, 1]
  helper: [1, 1]
  output: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

## Shape an answer without inventing a finding

```beat
id: answer
scene: answer
frames: 168
caption: Empty answer.json fields and evidence mapping
narration: The proposed answer has findings, impression, limitations and evidence summary fields. A finding would carry observation, location, certainty and image evidence. Present, possible and indeterminate are allowed certainty terms. The fields remain empty because no model answer exists.
visual: Connect the abstract viewer location to an empty answer schema. Clearly label every array empty and proposed; show no diagnostic phrase.
channels:
  phase: [0, 1]
  helper: [1, 1]
  output: [1, 1]
  reference: [0, 0]
cut: intentional-cut
```

## Reveal the proposed private reference role

```beat
id: reference
scene: reference
frames: 168
caption: Original report claims are evaluator-only
narration: A later evaluator would preserve exact report excerpts and their anatomy, negation, uncertainty and laterality. The report is a fallible source for concordance, not pathology truth. These empty claim columns appear only after the reader reveals the private reference role.
visual: Mount an empty private claim-ledger card only after reader reference reveal. Do not show report text, patient IDs or hidden categories in the initial solver view.
channels:
  phase: [0, 0]
  helper: [1, 1]
  output: [1, 1]
  reference: [0, 1]
cut: intentional-cut
```

## Compare in both directions

```beat
id: comparison
scene: comparison
frames: 192
caption: Omissions and unsupported additions need separate review
narration: The proposed review sends each source report claim to matched, missed, contradicted or unresolved. It separately sends answer additions to supported, explicitly contradicted or unmentioned and needing review. Report silence alone does not prove an image-grounded addition false. No claim is scored here.
visual: Animate highlighting across two labeled category tracks with no patient claim. Keep the private reference gate explicit and the warning at top.
channels:
  phase: [0, 1]
  helper: [1, 1]
  output: [1, 1]
  reference: [1, 1]
cut: intentional-cut
```

## State the unexecuted controls and admission gate

```beat
id: limits
scene: limits
frames: 168
caption: Proposed controls, no clinical result
narration: Empty, indiscriminately positive and contradictory answers and a copied-reference host control were planned, not executed. Source-derived explanation would require authorized CT-RATE access, a verified image/report pairing, native geometry review, a frozen private claim ledger and enforced runtime isolation. The proposed twelve-patient sample is not an observed denominator.
visual: Show the control names as unscored protocol cards and the case-admission checklist. The official CT-RATE link and zero admitted pairs and trials stay visible.
channels:
  phase: [0, 0]
  helper: [1, 1]
  output: [1, 1]
  reference: [1, 1]
cut: intentional-cut
```
