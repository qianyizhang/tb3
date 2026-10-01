---
schema: 2
id: bcer-short-denoise
title: MRI noise estimate, slice filtering and geometry validity
locale: en
purpose: "Explain BCER MRI input, normalized parameter and slice/geometry contracts and educational reference."
scope: "Representative MRI helper only; matching BM3D input/output and clean target absent."
recipe: bcer-denoise-v1
asset_pack: retained-bcer-denoise-source-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- presentation/external-tasks/briefs/bcer-short-denoise.md
- presentation/external-tasks/sources/bcer-short-denoise-resolution.json
- scripts/build_bcer_denoise_assets.py
---
# chapter-0

```beat
id: chapter-0
scene: input
frames: 168
caption: "Matched BM3D input/output and clean GT absent · zenodo.org/records/6624726"
narration: "PI-CAI representative helper only. Native geometry retained; display resize and JPEG encoding are not filtering."
visual: "Representative helper and source-defined normalization/geometry controls; actual output empty."
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
caption: "Whole-volume min/max normalization"
narration: "Finite range normalization differs from source display window; toy values only."
visual: "Representative helper and source-defined normalization/geometry controls; actual output empty."
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
caption: "Estimated sigma in normalized units"
narration: "Choose illustrative estimates; no patient noise distribution or added noise claimed."
visual: "Representative helper and source-defined normalization/geometry controls; actual output empty."
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
caption: "Slice-wise filter and geometry binding"
narration: "BM3D source profile np, restore range and copy geometry; no actual filter result."
visual: "Representative helper and source-defined normalization/geometry controls; actual output empty."
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
caption: "Actual denoised_nifti absent"
narration: "Default output path is a contract; no actual image or result artifact."
visual: "Representative helper and source-defined normalization/geometry controls; actual output empty."
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
caption: "Validator boundary only; no clean target"
narration: "The source channel enables a reader button; it does not reveal the rule automatically. Artifact validity is distinct from noise/detail quality."
visual: "Representative helper and source-defined normalization/geometry controls; actual output empty."
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
caption: "Noise/quality/matched output absent"
narration: "Representative helper is not a matching BCER short case. No tool, model or clinical result."
visual: "Representative helper and source-defined normalization/geometry controls; actual output empty."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```
