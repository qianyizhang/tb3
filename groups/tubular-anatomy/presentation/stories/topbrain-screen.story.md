---
schema: 2
id: topbrain-screen
title: Screen TopBrain predictions for a repair task
locale: en
purpose: Inspect retained segmentation predictions, reference fitness and calibration
  before admitting a named-vessel repair task.
scope: Five selected public development MRA scans; one TA36 model component. Author
  reference access, saved geometric calibration and no admitted brain task or coding-agent
  trial. No new inference or clinical adjudication.
recipe: topbrain-screen-v1
asset_pack: retained-topbrain-screen-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- groups/tubular-anatomy/presentation/briefs/tb3-topbrain-screen.md
- groups/tubular-anatomy/findings/topbrain-screen-scope.md
- groups/tubular-anatomy/presentation/sources/topbrain-screen-audit.json
- groups/tubular-anatomy/experiments/br033/protocol.md
- docs/research-rounds/BR-033-brain-resumption.md
- docs/evidence/br033-brain-resumption.json
- scripts/build_topbrain_screen_assets.py
- scripts/build_resect_assets.py
- scripts/build_respiratory_assets.py
---

# Inspect sources before admitting a repair task

## Start with actual development images

```beat
id: inputs
scene: inputs
frames: 192
caption: Start with actual development images
narration: The author has native MRA, untouched released-model predictions and source
  labels. References help choose candidates. These are public training scans, not
  a hidden clinical test set.
visual: Native-axis MRA projection from case 004. No reference geometry, scores or
  calibration output.
channels:
  view:
  - 0
  - 0
  output:
  - 0
  - 0
  reference:
  - 0
  - 0
```

## Five predictions are not five agent trials

```beat
id: cohort
scene: cohort
frames: 288
caption: Five predictions are not five agent trials
narration: One released ResEncM component produced five full-volume segmentations.
  Compare the unchanged predictions with separately revealed labels. Macro Dice weights
  each present nonbackground class equally; it does not establish branch-level correctness.
visual: Cycle all five matched MRA/prediction/reference views and their actual class
  scores.
channels:
  view:
  - 0
  - 1
  output:
  - 0
  - 0
  reference:
  - 1
  - 1
cut: intentional-cut
```

## Preserve an already supported variant

```beat
id: variants
scene: variants
frames: 240
caption: Preserve an already supported variant
narration: Cases 006 and 011 were selected using references for third-A2 and third-A3
  anatomy. The prediction already preserves each variant and its selected carotid
  parent connection. These are potential preservation controls, not repair failures.
visual: Two source-derived projections retain physical pixel aspect. Orange third-A2,
  teal third-A3, blue selected parent chain.
channels:
  view:
  - 0
  - 1
  output:
  - 0
  - 0
  reference:
  - 1
  - 1
cut: intentional-cut
```

## A new face contact is not an anatomical verdict

```beat
id: contacts
scene: contacts
frames: 576
caption: A new face contact is not an anatomical verdict
narration: Three PCA–SCA candidates gain face contacts, but every reference already
  touches through edges or corners. Six- and twenty-six-neighbour tests answer different
  discrete questions. Contact counts measure PCA voxels neighboring SCA; they are
  not counts of anatomical connections.
visual: Inspect three native planes for each of 004 left, 007 right and 011 left.
  Preserve source pixels, same-plane overlays and per-axis millimetre aspect.
channels:
  view:
  - 0
  - 1
  output:
  - 0
  - 0
  reference:
  - 1
  - 1
cut: intentional-cut
```

## Check the reference parent chain too

```beat
id: parent
scene: parent
frames: 192
caption: Check the reference parent chain too
narration: In case 007, thirteen percent of the reference left-M2 voxels are outside
  the selected carotid parent component. The reference itself requires review. A numerical
  reference gap cannot automatically become a prediction error.
visual: Reference reveal highlights the disconnected left-MCA portions in pink, with
  the exact denominator and chain named.
channels:
  view:
  - 0
  - 0
  output:
  - 0
  - 0
  reference:
  - 1
  - 1
cut: intentional-cut
```

## A small real gap yields to simple geometry

```beat
id: calibration
scene: calibration
frames: 240
caption: A small real gap yields to simple geometry
narration: The saved author baseline bridges a detached right-SCA fragment by nearest-point
  geometry. It adds two native-grid voxels and makes no other full-volume changes.
  No image or reference signal chooses this bridge; candidate selection remains reference-assisted.
visual: Hold native k=79 at the actual additions. Reveal the saved two-voxel bridge
  beside the unchanged prediction.
channels:
  view:
  - 0.5
  - 0.5
  output:
  - 0
  - 1
  reference:
  - 0
  - 0
cut: intentional-cut
```

## Connectivity is not exact reference recovery

```beat
id: reference
scene: calibration
frames: 192
caption: Connectivity is not exact reference recovery
narration: One added voxel matches reference right-SCA and one is reference background.
  Keep that disagreement visible. The output is a useful geometry calibration, with
  no brain task frozen and no agent result to revise.
visual: Replace the right panel with source reference labels and outline both actual
  additions, while holding the same native section.
channels:
  view:
  - 0.5
  - 0.5
  output:
  - 1
  - 1
  reference:
  - 0
  - 1
```

## Inspect the saved route and CPRs

```beat
id: outputs
scene: cpr
frames: 288
caption: Inspect the saved route and CPRs
narration: The retained route runs eighty-five point five-seven millimetres from basilar
  parent to right-SCA target. Eight curved reformations sample the original MRA. Export
  consistency and close reference-route agreement do not by themselves establish difficult
  anatomical reasoning.
visual: Show the retained route over prediction context and all eight saved CPR rotations
  at calibrated arc/offset aspect. Animation selects saved views, not solver iterations.
channels:
  view:
  - 0
  - 1
  output:
  - 1
  - 1
  reference:
  - 1
  - 1
cut: intentional-cut
```

## No clean hard brain task was admitted

```beat
id: decision
scene: admission
frames: 192
caption: No clean hard brain task was admitted
narration: The small gap was easy geometric calibration. The contact candidates retained
  reference ambiguity, and the selected variants were already preserved. Following
  its admission rule, the source study froze no brain task and launched no coding-agent
  trial.
visual: Reveal the recorded dispositions and distinguish five segmentation predictions
  from zero admitted brain tasks and zero coding-agent trials.
channels:
  view:
  - 0
  - 0
  output:
  - 1
  - 1
  reference:
  - 1
  - 1
cut: intentional-cut
```

## The original hypothesis remains open

```beat
id: limits
scene: limits
frames: 192
caption: The original hypothesis remains open
narration: This bounded development screen does not establish that TopBrain lacks
  suitable cases or that brain vessels are intrinsically harder. A future trial needs
  a substantial supported natural error, valid parent-connected controls and an independent
  frozen verifier.
visual: Show the unresolved admission conditions. Retain training exposure, thin-vessel
  screening limits and lack of expert adjudication.
channels:
  view:
  - 0
  - 0
  output:
  - 1
  - 1
  reference:
  - 1
  - 1
cut: intentional-cut
```
