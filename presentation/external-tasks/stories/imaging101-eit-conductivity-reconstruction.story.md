---
schema: 2
id: imaging101-eit-conductivity-reconstruction
title: "Pair EIT boundary voltages with conductivity domains"
locale: en
purpose: "Explain native synthetic point-electrode measurements and an unsubmitted inverse contract."
scope: "Matching synthetic input; solver-visible source truth; unresolved generic output/reference scale."
recipe: imaging-eit-v1
asset_pack: retained-imaging-eit-v1
source_class: source-derived-teaching
reference_policy: no-reference-assets
fps: 24
source_locators:
- presentation/external-tasks/briefs/imaging101-eit-conductivity-reconstruction.md
- presentation/external-tasks/sources/imaging101-eit-conductivity-reconstruction-resolution.json
- scripts/build_imaging_eit_assets.py
---

# Input

```beat
id: input
scene: input
frames: 192
caption: "Blind inversion unproven \u00b7 huggingface.co/datasets/starpacker52/imaging-101"
narration: "Native synthetic mesh and ordered voltage pairs are available. Point electrode indices and measurement sign follow pinned source, with no patient acquisition."
visual: "Native measurement geometry and task-specific contract diagram; no reconstructed image."
channels:
  progress: [0, 0]
  detail: [0, 1]
  reference: [0, 0]
```

# Helper

```beat
id: helper
scene: helper
frames: 192
caption: "Source truth is already solver-visible"
narration: "L1 contains data including anomaly conductivities. L2 adds approach, L3 adds design. Educational truth reveal is explicit and resets on backward replay or exit; it does not change solver visibility."
visual: "Native measurement geometry and task-specific contract diagram; no reconstructed image."
channels:
  progress: [0, 0]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

# Operation 1

```beat
id: operation-0
scene: operation
frames: 168
caption: "Pair ordered boundary voltages"
narration: "Native synthetic measurements remain inputs. BP, JAC and GREIT retain distinct normalization and domains; no FEM, inverse map or score is computed."
visual: "Canonical step and method rules; participant output remains absent."
channels:
  progress: [0.0, 0.0]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

# Operation 2

```beat
id: operation-1
scene: operation
frames: 168
caption: "Preserve voltage sign and gauge"
narration: "Native synthetic measurements remain inputs. BP, JAC and GREIT retain distinct normalization and domains; no FEM, inverse map or score is computed."
visual: "Canonical step and method rules; participant output remains absent."
channels:
  progress: [0.3333333333333333, 0.3333333333333333]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

# Operation 3

```beat
id: operation-2
scene: operation
frames: 168
caption: "Qualify inverse assumptions"
narration: "Native synthetic measurements remain inputs. BP, JAC and GREIT retain distinct normalization and domains; no FEM, inverse map or score is computed."
visual: "Canonical step and method rules; participant output remains absent."
channels:
  progress: [0.6666666666666666, 0.6666666666666666]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

# Operation 4

```beat
id: operation-3
scene: operation
frames: 168
caption: "Declare output spatial domain"
narration: "Native synthetic measurements remain inputs. BP, JAC and GREIT retain distinct normalization and domains; no FEM, inverse map or score is computed."
visual: "Canonical step and method rules; participant output remains absent."
channels:
  progress: [1.0, 1.0]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

# Output

```beat
id: output
scene: output
frames: 192
caption: "One generic artifact \u00b7 three method domains"
narration: "Generic reconstruction.npy is distinct from source BP 376-node, JAC 686-element and GREIT 32-square grid files. No prediction, map or score is supplied."
visual: "Native measurement geometry and task-specific contract diagram; no reconstructed image."
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
frames: 192
caption: "A shape match does not settle reference meaning"
narration: "Generic reference auto-discovery can compare a change estimate with absolute anomaly conductivity or saved method output depending on shape. Generic uncentered cosine and task centered correlation differ. No pass threshold is established."
visual: "Native measurement geometry and task-specific contract diagram; no reconstructed image."
channels:
  progress: [0, 0]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```
