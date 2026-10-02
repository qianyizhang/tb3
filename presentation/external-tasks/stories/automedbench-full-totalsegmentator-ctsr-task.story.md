---
schema: 2
id: automedbench-full-totalsegmentator-ctsr-task
title: "Restore TotalSegmentator through-plane detail without a Full pair"
locale: en
purpose: "Explain the pinned Full TotalSegmentator same-grid/method/output/metric contracts without reconstruction evidence."
scope: "Task-specific symbolic protocol; matching Full degraded/private CT selection absent; no clinical result."
recipe: automed-totalsegmentator-ctsr-v1
asset_pack: symbolic-automed-totalsegmentator-ctsr-v1
source_class: symbolic-protocol
reference_policy: no-reference-assets
fps: 24
source_locators:
- presentation/external-tasks/briefs/automedbench-full-totalsegmentator-ctsr-task.md
- presentation/external-tasks/sources/automedbench-full-totalsegmentator-ctsr-task-resolution.json
- scripts/build_automed_totalsegmentator_ctsr_assets.py
---

# Input

```beat
id: input
scene: input
frames: 288
caption: "CT pair absent · zenodo.org/records/10047292"
narration: "Exact Full degraded TotalSegmentator CT volume and hidden same-grid target are absent. Upstream v2.0.1 metadata and segmentation counts do not establish this pair. x4 z-axis is declared; no source voxels, physical geometry or Full membership inferred."
visual: "Symbolic same-grid CT sockets and pinned rule records, no patient pixels."
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
caption: "Compare declared x4 CT checkpoint variants"
narration: "Lite names PlainCNN trilinear x4; Standard compares 5 named checkpoints. Generic binary/organ-lesion prompts conflict with CT-SR. No weight or image transformation executed."
visual: "Symbolic same-grid CT sockets and pinned rule records, no patient pixels."
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
caption: "Audit, map HU, restore same grid and submit"
narration: "Canonical controls seek 4 source workflow stages. The source requires preserving CT grid/HU on the same grid. Empty sockets do not portray restored CT or missing high-frequency detail."
visual: "Symbolic same-grid CT sockets and pinned rule records, no patient pixels."
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
caption: "Finite 3D shape check differs from geometry prose"
narration: "Actual checker requires finite 3D NIfTI and target shape if available; HU and constant checks only warn. Missing outputs do not invalidate present-format. Artifact remains unset."
visual: "Symbolic same-grid CT sockets and pinned rule records, no patient pixels."
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
caption: "Inspect completion-weighted SSIM; target absent"
narration: "Explicit reader control reveals configured SSIM thresholds .98/.95 and completion-weighted proxy only. No LPIPS/LDCT bands. Private CT never appears; no clinical accuracy established."
visual: "Symbolic same-grid CT sockets and pinned rule records, no patient pixels."
channels:
  progress: [0, 0]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```
