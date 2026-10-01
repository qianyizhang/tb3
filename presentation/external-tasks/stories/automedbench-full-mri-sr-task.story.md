---
schema: 2
id: automedbench-full-mri-sr-task
title: "Double MRI grid while preserving source and reference boundaries"
locale: en
purpose: "Explain the pinned Full MRI grid/method/output/metric contracts without reconstruction evidence."
scope: "Task-specific symbolic protocol; matching Full LR/HR selection absent; no clinical result."
recipe: automed-mri-sr-v1
asset_pack: symbolic-automed-mri-sr-v1
source_class: symbolic-protocol
reference_policy: no-reference-assets
fps: 24
source_locators:
- presentation/external-tasks/briefs/automedbench-full-mri-sr-task.md
- presentation/external-tasks/sources/automedbench-full-mri-sr-task-resolution.json
- scripts/build_automed_mri_sr_assets.py
---

# Input

```beat
id: input
scene: input
frames: 288
caption: "Full MRI pair absent · fastmri.med.nyu.edu"
narration: "Required 360×256 MRI LR slice and 720×512 HR are absent. No anatomy, coil/slice join, degradation or native geometry inferred."
visual: "Symbolic MRI grid sockets and pinned rule records, no patient pixels."
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
caption: "Adapt grayscale and resolve the target grid"
narration: "Lite names Swin2SR grayscale-to-RGB adaptation, output-channel mean and final HR grid adjustment. Standard method requirements and S1 example conflict. No model or image transformation executed."
visual: "Symbolic MRI grid sockets and pinned rule records, no patient pixels."
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
caption: "Audit grid, adapt model, upscale and submit"
narration: "Canonical controls seek 4 source workflow stages. The x2 target differs from generic same-shape guidance; empty sockets do not portray reconstructed MRI."
visual: "Symbolic MRI grid sockets and pinned rule records, no patient pixels."
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
narration: "Actual checker accepts finite floating 2D matching private reference shape. No strict float32 or intensity-bound guard. Participant artifact remains unset."
visual: "Symbolic MRI grid sockets and pinned rule records, no patient pixels."
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
visual: "Symbolic MRI grid sockets and pinned rule records, no patient pixels."
channels:
  progress: [0, 0]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```
