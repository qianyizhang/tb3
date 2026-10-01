---
schema: 2
id: imaging101-pet-mlem
title: Trace PET measurements without inventing an activity image
locale: en
purpose: "Explain native scaled counts, background and MLEM/OSEM source rules."
scope: "Synthetic measurements only; no patient or participant activity result."
recipe: imaging101-pet-mlem-v1
asset_pack: retained-imaging101-pet-mlem-source-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- presentation/external-tasks/briefs/imaging101-pet-mlem.md
- presentation/external-tasks/sources/imaging101-pet-mlem-resolution.json
- scripts/build_imaging_pet_mlem_assets.py
---
# scaled-counts-source-gap

```beat
id: scaled-counts-source-gap
scene: input
frames: 168
caption: "Synthetic input; no activity image · Official Imaging101 acquisition"
narration: "Native synthetic sinogram is present, but no patient study or participant activity reconstruction."
visual: "Native synthetic scaled-count measurements; symbolic updates; actual output empty."
channels:
  progress: [0, 0]
  detail: [0, 0]
  reference: [0, 0]
```

# poisson-additive-background

```beat
id: poisson-additive-background
scene: operation
frames: 168
caption: "Keep integer counts and stored relative units distinct"
narration: "Poisson count draw is divided by one thousand; additive background shares the stored scale."
visual: "Native synthetic scaled-count measurements; symbolic updates; actual output empty."
channels:
  progress: [0, 0]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# native-angle-profiles

```beat
id: native-angle-profiles
scene: operation
frames: 168
caption: "Inspect native angle profiles and background"
narration: "Three native angular profiles; observed measurements and uniform background, no reconstruction."
visual: "Native synthetic scaled-count measurements; symbolic updates; actual output empty."
channels:
  progress: [0.5, 0.5]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

# mlem-osem-rules

```beat
id: mlem-osem-rules
scene: operation
frames: 168
caption: "Trace multiplicative MLEM and ordered subsets"
narration: "Source MLEM and OSEM use unfiltered backprojection; no FBP, exact-adjoint or convergence claim."
visual: "Native synthetic scaled-count measurements; symbolic updates; actual output empty."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# absent-activity-output

```beat
id: absent-activity-output
scene: output
frames: 168
caption: "Participant reconstruction and metric remain empty"
narration: "Saved source examples are not a fresh method outcome."
visual: "Native synthetic scaled-count measurements; symbolic updates; actual output empty."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# late-source-reference-rules

```beat
id: late-source-reference-rules
scene: reference
frames: 168
caption: "Reveal source-truth and magnitude-scoring rules"
narration: "Synthetic activity truth is solver-visible; masked/full metrics and baseline thresholds differ."
visual: "Native synthetic scaled-count measurements; symbolic updates; actual output empty."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [1, 1]
cut: intentional-cut
```

# unresolved-operator-calibration

```beat
id: unresolved-operator-calibration
scene: limits
frames: 168
caption: "Resolve operator, calibration and evaluator lineage"
narration: "No reconstructed activity, clinical uptake, fresh likelihood or numeric performance."
visual: "Native synthetic scaled-count measurements; symbolic updates; actual output empty."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```
