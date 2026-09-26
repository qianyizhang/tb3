---
schema: 2
id: rigid-correspondence
title: One transform must explain every correspondence
locale: en
purpose: Explain a specific operation with an inspectable synthetic witness.
scope: "Synthetic asymmetric fiducials. This demonstrates rigid coordinate transfer, not a solution to deformable\
  \ or MRI\u2013ultrasound registration."
recipe: correspondence-v1
asset_pack: correspondence-v1
source_class: procedural-teaching
reference_policy: no-reference-assets
fps: 24
source_locators:
- groups/registration/presentation/briefs/tb3-oblique-pose.md
---

# One transform must explain every correspondence

Authored explanation only. Scientific task records remain authoritative. Integrated operation sub-explanation; source task inputs and references remain separate.

## 1. frames

```beat
id: frames
frames: 120
caption: These coordinates belong to different frames.
narration: Moving and fixed are roles, not left and right on the screen.
visual: Show both geometric fiducial sets with their own axes and IDs.
channels:
  transform:
  - 0.0
  - 0.0
  query:
  - 0.0
  - 0.0
  residual:
  - 0.0
  - 0.0
```

## 2. fit

```beat
id: fit
frames: 168
caption: Apply the same transform to all points.
narration: Use the constructed fixed-from-moving transform. The teaching alignment is not an estimated patient result.
visual: Interpolate a valid rotation and translation; never linearly blend matrix coefficients.
channels:
  transform:
  - 0.0
  - 1.0
  query:
  - 0.0
  - 0.0
  residual:
  - 0.0
  - 0.0
```

## 3. transfer

```beat
id: transfer
frames: 144
caption: A query point becomes a target coordinate.
narration: Point transfer returns a coordinate; full registration returns a transform.
visual: Select P2 and show transform arithmetic, with the selected point tied to the mesh.
channels:
  transform:
  - 1.0
  - 1.0
  query:
  - 0.0
  - 1.0
  residual:
  - 0.0
  - 0.0
```

## 4. check

```beat
id: check
frames: 144
caption: Check points not used to define the transform.
narration: P4 and P5 are held-out fixture witnesses. Show computed residuals with metre units.
visual: Reveal residual segments and derived values; they are zero only to numeric tolerance.
channels:
  transform:
  - 1.0
  - 1.0
  query:
  - 1.0
  - 1.0
  residual:
  - 0.0
  - 1.0
```

## 5. scope

```beat
id: scope
frames: 96
caption: Deformation is a different contract.
narration: A rigid demonstration cannot claim to explain all respiratory or cross-modality changes.
visual: Preserve both views and a one-line boundary.
channels:
  transform:
  - 1.0
  - 1.0
  query:
  - 1.0
  - 1.0
  residual:
  - 1.0
  - 1.0
```
