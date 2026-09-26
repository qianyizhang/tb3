---
schema: 2
id: wsi-patches
title: Supplied patches remove the search step
locale: en
purpose: Explain a specific operation with an inspectable synthetic witness.
scope: Abstract level-0 spatial canvas, not histology, a source WSI, a prediction or evaluator reference. Fixture coordinates and 512-pixel slots are abstract. Real supplied targets are 256 × 256 pixels with 1024 × 1024 context.
recipe: multiscale-v1
asset_pack: multiscale-v1
source_class: procedural-teaching
reference_policy: no-reference-assets
fps: 24
source_locators:
- groups/lesion-localization/presentation/briefs/wsi-hiesd-patches.md
---

# Supplied patches remove the search step

Authored explanation only. Scientific task records remain authoritative. Integrated operation sub-explanation; source task inputs and references remain separate.

## 1. given

```beat
id: given
frames: 120
caption: Twelve target locations are already supplied.
narration: This is classification at supplied locations, not a whole-slide discovery task.
visual: Show all twelve ID-tagged patch windows at rest.
channels:
  viewport:
  - 0.0
  - 0.0
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

## 2. context

```beat
id: context
frames: 144
caption: Inspect each target together with its context.
narration: Context supports recognition; it does not change the target patch identity.
visual: Zoom one selected window while preserving its overview link.
channels:
  viewport:
  - 0.0
  - 1.0
  selections:
  - 1.0
  - 1.0
  coverage:
  - 0.0
  - 0.0
  outputs:
  - 0.0
  - 0.0
```

## 3. schema

```beat
id: schema
frames: 168
caption: Return one allowed code per patch ID.
narration: The schema has six task classes and an abstention option. No diagnosis is assigned by this diagram.
visual: Output rows stay unfilled; show the real allowed codes only after task binding review.
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

## 4. scope

```beat
id: scope
frames: 96
caption: Do not count twelve patches as twelve independent slides.
narration: This teaching display establishes format, not diagnostic performance.
visual: Hold the ID mapping and the supplied-location boundary.
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
  - 1.0
  - 1.0
```
