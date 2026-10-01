---
schema: 2
id: bcer-short-recon-grappa
title: Separate GRAPPA from passthrough, sampling skip and failed frames
locale: en
purpose: "Explain symbolic multi-coil k-space, calibration and faithful reconstruction-mode boundaries."
scope: "No matching cardiac H5, ACS, reconstruction or pristine truth."
recipe: bcer-grappa-v1
asset_pack: retained-bcer-grappa-source-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- presentation/external-tasks/briefs/bcer-short-recon-grappa.md
- presentation/external-tasks/sources/bcer-short-recon-grappa-resolution.json
- scripts/build_bcer_grappa_assets.py
---
# chapter-0

```beat
id: chapter-0
scene: input
frames: 168
caption: "Missing H5/output · CMRxRecon2025: cmrxrecon.github.io/2025/Join-the-Challenge.html"
narration: "Symbolic frequency mask and coil layout; no patient measurements."
visual: "Symbolic coil/mask/calibration rules; actual output empty."
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
caption: "Bind complex frame axes and nonspatial order"
narration: "Explicit coil/phase/slice layout and pixel spacing needed for faithful output."
visual: "Symbolic coil/mask/calibration rules; actual output empty."
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
caption: "Inspect calibration, sampling skip and frame failure"
narration: "Canonical conditions explain source rules; no actual GRAPPA kernel or runtime result."
visual: "Symbolic coil/mask/calibration rules; actual output empty."
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
caption: "IFFT+RSS magnitude and output geometry"
narration: "No reconstruction image; optional readout crop and placeholder spacing remain qualified."
visual: "Symbolic coil/mask/calibration rules; actual output empty."
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
caption: "Actual reconstructed_nifti empty"
narration: "Mode/counters/spacing/crop fields describe a future recorded artifact only."
visual: "Symbolic coil/mask/calibration rules; actual output empty."
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
caption: "Reveal mode and grader limits, not image truth"
narration: "Source channel enables eligibility, not automatic reveal. Explicit reader request exposes public mode rules; no image truth."
visual: "Symbolic coil/mask/calibration rules; actual output empty."
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
caption: "Measurement/calibration/quality gaps remain"
narration: "No matching raw H5, reference or output; acquire source through official route."
visual: "Symbolic coil/mask/calibration rules; actual output empty."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```
