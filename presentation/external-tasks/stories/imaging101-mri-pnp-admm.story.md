---
schema: 2
id: imaging101-mri-pnp-admm
title: Trace PnP-ADMM without inventing a reconstructed brain image
locale: en
purpose: "Explain actual masks, Fourier consistency and residual-denoiser updates."
scope: "Source-visible brain image; missing noise scale; no participant outcome."
recipe: imaging101-pnp-admm-v1
asset_pack: retained-imaging101-pnp-admm-source-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- presentation/external-tasks/briefs/imaging101-mri-pnp-admm.md
- presentation/external-tasks/sources/imaging101-mri-pnp-admm-resolution.json
- scripts/build_imaging_pnp_admm_assets.py
---
# source-masks-missing-observation

```beat
id: source-masks-missing-observation
scene: input
frames: 168
caption: "Masks only; scale missing · Official Imaging101 acquisition"
narration: "Raw masks/noise contain no measured k-space; required metadata noise scale absent."
visual: "Actual binary masks; symbolic algorithm rules; actual output empty."
channels:
  progress: [0, 0]
  detail: [0, 0]
  reference: [0, 0]
```

# observation-initialization

```beat
id: observation-initialization
scene: operation
frames: 168
caption: "Separate observation synthesis and real initialization"
narration: "Unshifted FFT and complex all-bin noise; source image is solver-visible."
visual: "Actual binary masks; symbolic algorithm rules; actual output empty."
channels:
  progress: [0, 0]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# sampled-fourier-consistency

```beat
id: sampled-fourier-consistency
scene: operation
frames: 168
caption: "Inspect actual masks and sampled Fourier consistency"
narration: "Three mask displays preserve native cells; controls never run a solver."
visual: "Actual binary masks; symbolic algorithm rules; actual output empty."
channels:
  progress: [0.5, 0.5]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

# residual-denoiser-dual

```beat
id: residual-denoiser-dual
scene: operation
frames: 168
caption: "Separate learned residual and dual update rules"
narration: "Normalize, scale and invert residual-denoiser input; no checkpoint or reconstruction run."
visual: "Actual binary masks; symbolic algorithm rules; actual output empty."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# absent-participant-output

```beat
id: absent-participant-output
scene: output
frames: 168
caption: "Participant reconstruction and metric remain empty"
narration: "Saved source examples are not a fresh method outcome."
visual: "Actual binary masks; symbolic algorithm rules; actual output empty."
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
narration: "Source image solver-visible; educational rules only, no private or image reference."
visual: "Actual binary masks; symbolic algorithm rules; actual output empty."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [1, 1]
cut: intentional-cut
```

# unresolved-scale-checkpoint

```beat
id: unresolved-scale-checkpoint
scene: limits
frames: 168
caption: "Resolve missing scale and checkpoint conditions"
narration: "No measured observation, participant image, score or clinical finding."
visual: "Actual binary masks; symbolic algorithm rules; actual output empty."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```
