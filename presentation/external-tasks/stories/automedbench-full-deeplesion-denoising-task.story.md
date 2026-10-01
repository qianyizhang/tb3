---
schema: 2
id: automedbench-full-deeplesion-denoising-task
title: Trace DeepLesion noise without inventing a clean CT
locale: en
purpose: "Explain normalized Gaussian-noise declaration, Full assistance and private clean-reference rules."
scope: "Matching Full noisy CT/private clean target absent; authored noise mechanics and actual output empty."
recipe: automedbench-full-deeplesion-denoising-task-v1
asset_pack: retained-automedbench-full-deeplesion-denoising-task-source-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- presentation/external-tasks/briefs/automedbench-full-deeplesion-denoising-task.md
- presentation/external-tasks/sources/automedbench-full-deeplesion-denoising-task-resolution.json
- scripts/build_automed_deeplesion_denoise_assets.py
---
# full-pair-and-source-gap

```beat
id: full-pair-and-source-gap
scene: input
frames: 168
caption: "Matching noisy CT / target absent · Official DeepLesion acquisition"
narration: "Full harness supplies no image cases; matching normalized noisy CT, private clean target and noise lineage unavailable."
visual: "Authored noisy values, same-geometry unknown clean/output sockets; no CT or denoising result."
channels:
  progress: [0, 0]
  detail: [0, 0]
  reference: [0, 0]
```

# normalized-noise-and-input-contract

```beat
id: normalized-noise-and-input-contract
scene: operation
frames: 168
caption: "Keep normalized σ separate from CT dose and HU"
narration: "Gaussian sigma 0.05 is normalized intensity; seed, clipping, calibration and matching native noise unavailable."
visual: "Authored noisy values, same-geometry unknown clean/output sockets; no CT or denoising result."
channels:
  progress: [0, 0]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# same-observation-clean-ambiguity

```beat
id: same-observation-clean-ambiguity
scene: operation
frames: 168
caption: "Compare Full Lite, Standard and format boundary"
narration: "Assistance controls prescribe or compare methods; checker validity remains weaker than task output requirements."
visual: "Authored noisy values, same-geometry unknown clean/output sockets; no CT or denoising result."
channels:
  progress: [0.5, 0.5]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

# method-output-and-evaluator-contract

```beat
id: method-output-and-evaluator-contract
scene: operation
frames: 168
caption: "Keep clean values unknown behind the noisy observations"
narration: "Authored noisy 2 × 2 to unknown 2 × 2 cells illustrate same 512² geometry; multiple clean/noise pairs, no native noise draw or denoised result."
visual: "Authored noisy values, same-geometry unknown clean/output sockets; no CT or denoising result."
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
visual: "Authored noisy values, same-geometry unknown clean/output sockets; no CT or denoising result."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# reader-private-reference-boundaries

```beat
id: reader-private-reference-boundaries
scene: reference
frames: 168
caption: "Reveal evaluator rules without private image access"
narration: "Runner metrics, missing bands and effective fallback differ from named config; no private reference or score shown."
visual: "Authored noisy values, same-geometry unknown clean/output sockets; no CT or denoising result."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [1, 1]
cut: intentional-cut
```

# reopen-full-case-and-bands

```beat
id: reopen-full-case-and-bands
scene: limits
frames: 168
caption: "Resolve native cases, noise lineage and metric assets"
narration: "No native CT, private clean truth, preserved lesion detail, model denoising or measured metric."
visual: "Authored noisy values, same-geometry unknown clean/output sockets; no CT or denoising result."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```
