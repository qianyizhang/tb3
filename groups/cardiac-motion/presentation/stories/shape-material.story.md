---
schema: 2
id: shape-material
title: The same phase shapes allow different material motion
locale: en
purpose: Explain a specific operation with an inspectable synthetic witness.
scope: Analytic teaching shell, not a patient ventricle or physiological mechanics model. Neither correspondence
  map was inferred from images.
recipe: shape-material-v1
asset_pack: shape-material-v1
source_class: procedural-teaching
reference_policy: no-reference-assets
fps: 24
source_locators:
- groups/cardiac-motion/presentation/briefs/tb3-cardiac-material-motion.md
---

# The same phase shapes allow different material motion

Authored explanation only. Scientific task records remain authoritative. Integrated operation sub-explanation; source task inputs and references remain separate.

## 1. shape

```beat
id: shape
frames: 144
caption: First observe only the change in surface shape.
narration: A phase sequence describes where the surface is, not which material point moved where.
visual: Show the shell without material tracks; retain its basal opening.
channels:
  phase:
  - 0.0
  - 1.0
  markers:
  - 0.0
  - 0.0
  alternative:
  - 0.0
  - 0.0
```

## 2. identity

```beat
id: identity
frames: 144
caption: Now add persistent material identities.
narration: These markers are constructed for this fixture. They were not recovered by an agent.
visual: Reveal named material markers and their tracks for map A.
channels:
  phase:
  - 1.0
  - 1.0
  markers:
  - 0.0
  - 1.0
  alternative:
  - 0.0
  - 0.0
```

## 3. alternative

```beat
id: alternative
frames: 216
caption: A second material map fits the identical shapes.
narration: Move points around the periodic angle while retaining the same surface set at every phase.
visual: Show equal-sized A/B panels. Only trajectories differ; never swap in a different shell.
channels:
  phase:
  - 1.0
  - 1.0
  markers:
  - 1.0
  - 1.0
  alternative:
  - 0.0
  - 1.0
```

## 4. contrast

```beat
id: contrast
frames: 144
caption: Matching shapes does not identify the true motion.
narration: The differing trajectories expose the ambiguity. Neither map is validated physiology.
visual: Hold both maps at the same phase; highlight two different endpoints for the same material ID.
channels:
  phase:
  - 1.0
  - 1.0
  markers:
  - 1.0
  - 1.0
  alternative:
  - 1.0
  - 1.0
```

## 5. output

```beat
id: output
frames: 120
caption: State which output the real task actually requires.
narration: Per-phase geometry, trajectories and mechanics require different evidence and checks.
visual: Output-format labels remain schemas, not computed clinical quantities.
channels:
  phase:
  - 1.0
  - 1.0
  markers:
  - 1.0
  - 1.0
  alternative:
  - 1.0
  - 1.0
```
