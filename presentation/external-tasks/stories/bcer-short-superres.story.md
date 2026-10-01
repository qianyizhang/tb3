---
schema: 2
id: bcer-short-superres
title: Choose a physical grid without claiming new measured detail
locale: en
purpose: "Explain representative MRI input, exact-grid interpolation and artifact-only grading."
scope: "Representative upstream helper; no matching BCER output, caller target or high-resolution truth."
recipe: bcer-superres-v1
asset_pack: retained-bcer-superres-source-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- presentation/external-tasks/briefs/bcer-short-superres.md
- presentation/external-tasks/sources/bcer-short-superres-resolution.json
- scripts/build_bcer_superres_assets.py
---
# chapter-0

```beat
id: chapter-0
scene: input
frames: 168
caption: "No matched output/HR truth · zenodo.org/records/6624726"
narration: "Representative PI-CAI helper; display derivative stated, no resampling performed."
visual: "Representative source MRI, symbolic grid calculations and empty output."
channels:
  progress: [0, 0]
  detail: [0, 0]
  reference: [0, 0]
```

# chapter-1

```beat
id: chapter-1
scene: operation
frames: 168
caption: "Read source physical geometry"
narration: "Separate arbitrary MRI intensity from spacing, origin and direction."
visual: "Representative source MRI, symbolic grid calculations and empty output."
channels:
  progress: [0, 0]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# chapter-2

```beat
id: chapter-2
scene: operation
frames: 168
caption: "Choose a target; derive ceil(N×s/t)"
narration: "Illustrative exact-header spacing targets; not actual output grids."
visual: "Representative source MRI, symbolic grid calculations and empty output."
channels:
  progress: [0.5, 0.5]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

# chapter-3

```beat
id: chapter-3
scene: operation
frames: 168
caption: "Interpolate without measuring new detail"
narration: "Identity transform, interpolation, input pixel type and outside-FOV limits."
visual: "Representative source MRI, symbolic grid calculations and empty output."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# chapter-4

```beat
id: chapter-4
scene: output
frames: 168
caption: "Actual resampled_nifti empty"
narration: "Typed default path and response only; no high-resolution result."
visual: "Representative source MRI, symbolic grid calculations and empty output."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# chapter-5

```beat
id: chapter-5
scene: reference
frames: 168
caption: "Reveal grader boundary, not target image"
narration: "Explicit reader reveal shows artifact success, path and nonempty rules, not quality."
visual: "Representative source MRI, symbolic grid calculations and empty output."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [1, 1]
cut: intentional-cut
```

# chapter-6

```beat
id: chapter-6
scene: limits
frames: 168
caption: "Denser sampling does not measure new detail"
narration: "Matched target, output and independent truth absent; no clinical performance."
visual: "Representative source MRI, symbolic grid calculations and empty output."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```
