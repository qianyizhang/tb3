---
schema: 2
id: automedbench-full-ldct-denoising-task
title: "Denoise CT while preserving scale and reference boundaries"
locale: en
purpose: "Explain the pinned Full HU/method/output/metric contracts without denoising evidence."
scope: "Task-specific symbolic protocol; matching Full noisy-clean selection absent; no clinical result."
recipe: automed-ldct-denoising-v1
asset_pack: symbolic-automed-ldct-denoising-v1
source_class: symbolic-protocol
reference_policy: no-reference-assets
fps: 24
source_locators:
- presentation/external-tasks/briefs/automedbench-full-ldct-denoising-task.md
- presentation/external-tasks/sources/automedbench-full-ldct-denoising-task-resolution.json
- scripts/build_automed_ldct_denoising_assets.py
---

# Input

```beat
id: input
scene: input
frames: 288
caption: "Full CT pair absent · aapm.org/grandchallenge/lowdosect/"
narration: "Required 512 × 512 HU input is absent. Config ranges conflict; no patient, spacing, noise or upstream equivalence is inferred."
visual: "Symbolic HU socket and pinned rule records, no patient pixels."
channels:
  progress: [0, 0]
  detail: [0, 1]
  reference: [0, 0]
```

# Helper

```beat
id: helper
scene: helper
frames: 288
caption: "Choose inference-only HU mapping and sigma"
narration: "Lite names DRUNet with sigma. Standard compares at least 3 methods including 2 DNNs; source S1 example conflicts. No model or source transformation executed."
visual: "Symbolic HU socket and pinned rule records, no patient pixels."
channels:
  progress: [0, 0]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

# Operation

```beat
id: operation
scene: operation
frames: 288
caption: "Plan, denoise, invert and submit"
narration: "Canonical controls seek four source workflow stages. HU-to-normalized mapping and inverse remain participant work; the empty diagram is not reconstructed CT."
visual: "Symbolic HU socket and pinned rule records, no patient pixels."
channels:
  progress: [0, 1]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

# Output

```beat
id: output
scene: output
frames: 288
caption: "Finite floating shape check differs from prose"
narration: "Actual checker accepts finite floating 2D matching private reference shape. No strict float32 or HU-bound guard. Participant artifact remains unset."
visual: "Symbolic HU socket and pinned rule records, no patient pixels."
channels:
  progress: [0, 0]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

# Limits

```beat
id: limits
scene: limits
frames: 288
caption: "Inspect v3 rating rules; private targets stay absent"
narration: "Explicit reader control reveals public metric policy only. Present v3 bands gate PSNR/SSIM, no LPIPS threshold; score field names do not establish clinical accuracy."
visual: "Symbolic HU socket and pinned rule records, no patient pixels."
channels:
  progress: [0, 0]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```
