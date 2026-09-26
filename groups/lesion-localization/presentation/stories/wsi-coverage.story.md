---
schema: 2
id: wsi-coverage
title: Label coverage is not the same as normal tissue
locale: en
purpose: Explain a specific operation with an inspectable synthetic witness.
scope: "Abstract level-0 spatial canvas, not histology, a source WSI, a prediction or evaluator reference. Coverage\
  \ rectangles and C1\u2013C6 codes are synthetic."
recipe: multiscale-v1
asset_pack: multiscale-v1
source_class: procedural-teaching
reference_policy: no-reference-assets
fps: 24
source_locators:
- groups/lesion-localization/presentation/briefs/wsi-hiesd-map.md
---

# Label coverage is not the same as normal tissue

Authored explanation only. Scientific task records remain authoritative. Integrated operation sub-explanation; source task inputs and references remain separate.

## 1. field

```beat
id: field
frames: 120
caption: The source view and the annotated domain differ.
narration: What is visible is not necessarily what has a dense reference label.
visual: Show the entire abstract canvas without labels.
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

## 2. domain

```beat
id: domain
frames: 168
caption: Make the evaluated domain explicit.
narration: Hatch the unannotated area; never treat it as normal background.
visual: Overlay the two declared coverage regions and exclude every other location.
channels:
  viewport:
  - 0.0
  - 0.0
  selections:
  - 0.0
  - 0.0
  coverage:
  - 0.0
  - 1.0
  outputs:
  - 0.0
  - 0.0
```

## 3. classes

```beat
id: classes
frames: 168
caption: Six semantic classes need six distinct keys.
narration: Class identities and object instance identities must not share a misleading legend.
visual: "Show C1\u2013C6 swatches and separate object IDs. Label the codes teaching-only."
channels:
  viewport:
  - 0.0
  - 0.0
  selections:
  - 0.0
  - 1.0
  coverage:
  - 1.0
  - 1.0
  outputs:
  - 0.0
  - 1.0
```

## 4. limit

```beat
id: limit
frames: 120
caption: Metrics belong only to the declared coverage.
narration: A whole-slide display does not justify a whole-slide accuracy claim.
visual: Keep coverage visible when the output is revealed.
channels:
  viewport:
  - 0.0
  - 0.0
  selections:
  - 1.0
  - 1.0
  coverage:
  - 1.0
  - 1.0
  outputs:
  - 1.0
  - 1.0
```
