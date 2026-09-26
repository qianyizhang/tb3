---
schema: 2
id: ct-forward
title: CT reconstruction must explain the measurements
locale: en
purpose: Explain a specific operation with an inspectable synthetic witness.
scope: Unitless geometric phantom with a simplified parallel-beam operator, not a patient CT reconstruction.
recipe: inverse-v1
asset_pack: inverse-problems-v1
source_class: procedural-teaching
reference_policy: no-reference-assets
fps: 24
source_locators:
- presentation/external-tasks/briefs/imaging101.md
acquisition: ct-parallel
---

# CT reconstruction must explain the measurements

Authored explanation only. Scientific task records remain authoritative. Integrated operation sub-explanation; source task inputs and references remain separate.

## 1. object

```beat
id: object
frames: 96
caption: This is a geometric object, not an organ model.
narration: Use it only to explain a measurement operator.
visual: Show the scalar field with a teaching-fixture label.
channels:
  observations:
  - 0.0
  - 0.0
  reconstruction:
  - 0.0
  - 0.0
  residual:
  - 0.0
  - 0.0
```

## 2. measure

```beat
id: measure
frames: 168
caption: Each CT measurement integrates along a line.
narration: The sinogram was generated from this exact field at ninety angles.
visual: Show the computed sinogram and an explicit angle axis.
channels:
  observations:
  - 0.0
  - 1.0
  reconstruction:
  - 0.0
  - 0.0
  residual:
  - 0.0
  - 0.0
```

## 3. recover

```beat
id: recover
frames: 168
caption: The reconstruction is an image, not a mesh.
narration: Filtered backprojection produces the displayed image. It is a declared baseline.
visual: Reveal the actual stored reconstruction, not a clean source substituted as output.
channels:
  observations:
  - 1.0
  - 1.0
  reconstruction:
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
caption: Reproject and inspect the nonzero residual.
narration: The residual is computed under the same simplified forward model.
visual: Plot residual values from arrays; never label an arbitrary zero as success.
channels:
  observations:
  - 1.0
  - 1.0
  reconstruction:
  - 1.0
  - 1.0
  residual:
  - 0.0
  - 1.0
```
