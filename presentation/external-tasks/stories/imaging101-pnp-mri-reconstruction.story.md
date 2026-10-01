---
schema: 2
id: imaging101-pnp-mri-reconstruction
title: Trace PnP rules without inventing a reconstructed knee
locale: en
purpose: "Explain visible image, saved mask, unitary data consistency and unknown learned denoiser."
scope: "Source image equals visible truth; no acquired k-space or participant result."
recipe: imaging101-pnp-mri-reconstruction-v1
asset_pack: retained-imaging101-pnp-mri-reconstruction-source-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- presentation/external-tasks/briefs/imaging101-pnp-mri-reconstruction.md
- presentation/external-tasks/sources/imaging101-pnp-mri-reconstruction-resolution.json
- scripts/build_imaging_pnp_mri_assets.py
---
# source-image-mask-and-acquisition-gap

```beat
id: source-image-mask-and-acquisition-gap
scene: input
frames: 168
caption: "Visible truth; k-space / result missing · Official Imaging101 acquisition"
narration: "Source input equals visible truth; acquired k-space and participant PnP output are absent."
visual: "Saved source mask; authored PGM mechanics; public truth late only, output empty."
channels:
  progress: [0, 0]
  detail: [0, 0]
  reference: [0, 0]
```

# visible-image-forward-data-contract

```beat
id: visible-image-forward-data-contract
scene: operation
frames: 168
caption: "Separate supplied image from generated Fourier data"
narration: "One visible image generates noiseless masked Fourier data; sigma training label is not acquisition noise."
visual: "Saved source mask; authored PGM mechanics; public truth late only, output empty."
channels:
  progress: [0, 0]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# saved-mask-and-unitary-scale

```beat
id: saved-mask-and-unitary-scale
scene: operation
frames: 168
caption: "Inspect saved mask, unitary scale and patch coverage"
narration: "Saved geometry and public operator rules remain separate from denoising or reconstruction."
visual: "Saved source mask; authored PGM mechanics; public truth late only, output empty."
channels:
  progress: [0.5, 0.5]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

# patch-prior-and-gradient-update

```beat
id: patch-prior-and-gradient-update
scene: operation
frames: 168
caption: "Apply PGM clipping before the unknown denoiser"
narration: "Real gradient and positivity precede a learned patch denoiser; output and convergence unknown."
visual: "Saved source mask; authored PGM mechanics; public truth late only, output empty."
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
visual: "Saved source mask; authored PGM mechanics; public truth late only, output empty."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# reader-source-and-score-rules

```beat
id: reader-source-and-score-rules
scene: reference
frames: 168
caption: "Reader may reveal public source image and normalization"
narration: "Only an explicit reader request reveals public source truth; source and generic normalized-error denominators differ."
visual: "Saved source mask; authored PGM mechanics; public truth late only, output empty."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [1, 1]
cut: intentional-cut
```

# reopen-kspace-runtime-and-rights

```beat
id: reopen-kspace-runtime-and-rights
scene: limits
frames: 168
caption: "Resolve visibility, model compatibility and metrics"
narration: "No acquired k-space, model forward, reconstructed knee or numerical performance."
visual: "Saved source mask; authored PGM mechanics; public truth late only, output empty."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```
