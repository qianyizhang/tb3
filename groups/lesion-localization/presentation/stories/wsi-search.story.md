---
schema: 2
id: wsi-search
title: From overview search to level-0 coordinates
locale: en
purpose: Explain a specific operation with an inspectable synthetic witness.
scope: Abstract level-0 spatial canvas, not histology, a source WSI, a prediction or evaluator reference.
recipe: multiscale-v1
asset_pack: multiscale-v1
source_class: procedural-teaching
reference_policy: no-reference-assets
fps: 24
source_locators:
- groups/lesion-localization/presentation/briefs/wsi-camelyon-search.md
---

# From overview search to level-0 coordinates

Authored explanation only. Scientific task records remain authoritative. Integrated operation sub-explanation; source task inputs and references remain separate.

## 1. overview

```beat
id: overview
frames: 120
caption: A whole-slide task begins with a large search space.
narration: The geometric canvas illustrates navigation only. Real recognition needs the source slide.
visual: Show overview grid and a viewport rectangle; no fake tissue texture.
channels:
  viewport:
  - 0.0
  - 0.0
  selections:
  - 0.0
  - 0.0
  coverage:
  - 0.0
  - 0.0
  outputs:
  - 0.0
  - 0.0
```

## 2. zoom

```beat
id: zoom
frames: 168
caption: Zooming changes the view, not the slide coordinate frame.
narration: Retain the viewport origin and downsample factor.
visual: Move to the selected viewport and expose its explicit local-to-level0 affine.
channels:
  viewport:
  - 0.0
  - 1.0
  selections:
  - 0.0
  - 0.0
  coverage:
  - 0.0
  - 0.0
  outputs:
  - 0.0
  - 0.0
```

## 3. inspect

```beat
id: inspect
frames: 144
caption: Inspect candidates without pre-marking the answer.
narration: A selected location is a candidate, not a verified lesion.
visual: Show the selected local point with an amber crosshair and no diagnosis.
channels:
  viewport:
  - 1.0
  - 1.0
  selections:
  - 0.0
  - 1.0
  coverage:
  - 0.0
  - 0.0
  outputs:
  - 0.0
  - 0.0
```

## 4. return

```beat
id: return
frames: 168
caption: Return the corresponding level-0 coordinate.
narration: For the fixture, origin plus four times the local offset gives 2680, 2040.
visual: Generate the coordinate label from the affine; do not hardcode the result in the scene.
channels:
  viewport:
  - 1.0
  - 1.0
  selections:
  - 1.0
  - 1.0
  coverage:
  - 0.0
  - 0.0
  outputs:
  - 0.0
  - 1.0
```
