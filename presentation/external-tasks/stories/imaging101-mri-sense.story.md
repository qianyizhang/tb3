---
schema: 2
id: imaging101-mri-sense
title: Trace SENSE encoding without inventing an MRI reconstruction
locale: en
purpose: "Explain actual coil maps, complex encoding and scaled CG rules."
scope: "Synthetic source phantom; loader and R3/R4 mismatch; no participant outcome."
recipe: imaging101-sense-v1
asset_pack: retained-imaging101-sense-source-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- presentation/external-tasks/briefs/imaging101-mri-sense.md
- presentation/external-tasks/sources/imaging101-mri-sense-resolution.json
- scripts/build_imaging_sense_assets.py
---
# source-maps-and-gap

```beat
id: source-maps-and-gap
scene: input
frames: 168
caption: "Loader/R mismatch; no result · Official Imaging101 acquisition"
narration: "Synthetic maps and masked data present; full-kspace loader keys absent, main R differs."
visual: "Actual synthetic map magnitudes; symbolic CG rules; actual output empty."
channels:
  progress: [0, 0]
  detail: [0, 0]
  reference: [0, 0]
```

# complex-encoding-conventions

```beat
id: complex-encoding-conventions
scene: operation
frames: 168
caption: "Keep complex sensitivity and FFT conventions explicit"
narration: "Centered FFT inverse scaling and complex coil maps differ from map-magnitude display."
visual: "Actual synthetic map magnitudes; symbolic CG rules; actual output empty."
channels:
  progress: [0, 0]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# coil-display-and-mask-contract

```beat
id: coil-display-and-mask-contract
scene: operation
frames: 168
caption: "Inspect native coil maps and sampled-row counts"
narration: "Three native coil displays preserve array cells; no calibration or solver execution."
visual: "Actual synthetic map magnitudes; symbolic CG rules; actual output empty."
channels:
  progress: [0.5, 0.5]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

# scaled-conjugate-gradient-rule

```beat
id: scaled-conjugate-gradient-rule
scene: operation
frames: 168
caption: "Separate scaled inverse helper and CG normal equations"
narration: "No explicit regularization; first-coil mask and discarded convergence info need qualification."
visual: "Actual synthetic map magnitudes; symbolic CG rules; actual output empty."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# participant-output-empty

```beat
id: participant-output-empty
scene: output
frames: 168
caption: "Participant reconstruction and metric remain empty"
narration: "Saved source examples are not a fresh method outcome."
visual: "Actual synthetic map magnitudes; symbolic CG rules; actual output empty."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# reader-source-metric-rules

```beat
id: reader-source-metric-rules
scene: reference
frames: 168
caption: "Reveal source-truth and magnitude-scoring rules"
narration: "Synthetic phantom solver-visible; educational rules only, no private or image reference."
visual: "Actual synthetic map magnitudes; symbolic CG rules; actual output empty."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [1, 1]
cut: intentional-cut
```

# reopen-loader-and-runtime-join

```beat
id: reopen-loader-and-runtime-join
scene: limits
frames: 168
caption: "Reconcile loader, mask and selected reference"
narration: "No matching end-to-end lineage, participant reconstruction or clinical outcome."
visual: "Actual synthetic map magnitudes; symbolic CG rules; actual output empty."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```
