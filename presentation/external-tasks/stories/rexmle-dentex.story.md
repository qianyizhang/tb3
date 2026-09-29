---
schema: 2
id: rexmle-dentex
title: Find and label teeth on a panoramic radiograph
locale: en
purpose: Inspect one task-matched source radiograph, the localization and hierarchical-label output contract, and a separately revealed private source reference.
scope: Actual ReX-split input and reader-only source boxes; empty prediction schema. No model result or validated AP.
recipe: rexmle-dentex-v1
asset_pack: retained-rexmle-dentex-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- presentation/external-tasks/briefs/rexmle-dentex.md
- presentation/external-tasks/sources/rexmle-dentex-resolution.json
- scripts/build_rexmle_dentex_assets.py
---

# A real DENTEX test input

```beat
id: input
scene: input
frames: 288
caption: Inspect the complete 1976 × 976 panorama
narration: This is the actual DENTEX radiograph train_266.png. The pinned ReX adapter shuffles 705 fully annotated source images with seed 42, placing 564 in public training and 141 in a private-label test partition. This image belongs to the latter. No finding location, model prediction, or private box is supplied on this first read.
visual: Native-aspect panoramic source image alone, with the 705 to 564 and 141 split strip. A persistent notice links the official source and states that no prediction or validated AP is retained.
channels:
  box: [0, 0]
  labels: [0, 0]
  reference: [0, 0]
```

# Locate before labeling

```beat
id: localize
scene: localize
frames: 336
caption: Search the full image, then encode a pixel box
narration: The solver must search the full panoramic image. A crosshair marks only the pixel-coordinate ruler, not a detected tooth. A proposed localization uses x and y from the upper left, then width and height in source pixels. No candidate box is saved here.
visual: Actual image with a neutral center coordinate ruler; adjacent x,y,width,height operation card, never a reference contour or model box.
channels:
  box: [0, 1]
  labels: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# One box carries three labels

```beat
id: encode
scene: encode
frames: 360
caption: Quadrant → tooth enumeration → diagnosis
narration: For each future predicted box, the ReX JSON needs a quadrant ID, tooth-enumeration ID, diagnosis ID, and confidence. These are fields of the same localization, not three separate patient images. The CSV row points from image ID train_266 to a per-image JSON file. Its annotations array is empty because no prediction was run.
visual: Exact CSV row and empty JSON schema beside a five-field hierarchy. Source category IDs remain untouched.
channels:
  box: [1, 1]
  labels: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

# Reveal the source answer separately

```beat
id: reference
scene: reference
frames: 384
caption: Five private source boxes, only on reader reveal
narration: The official source includes five annotations for this image. They are a private ReX test reference, not an agent output. Only an explicit reader reveal mounts the amber dashed boxes. Each row keeps the original zero-based source IDs and shows its source category name beside the native x,y,width,height box.
visual: Covered reference initially, then five dashed amber source boxes on the real image and a matching line-style legend. Input image and private reference remain distinct.
channels:
  box: [0, 0]
  labels: [0, 0]
  reference: [0, 1]
cut: intentional-cut
```

# The unresolved scorer caveat

```beat
id: audit
scene: audit
frames: 336
caption: Source labels start at zero; scorer categories start at one
narration: Pinned ReX grading passes original ground-truth category IDs through, yet declares category lists numbered from one. The source diagnosis ID zero means Impacted, while the grader's diagnosis ID one is caries. This mismatch needs a focused scorer check before any AP interpretation. We have no prediction, run or score to report.
visual: Three-row source-ID versus grader-ID comparison and one concrete diagnosis-name counterexample; no AP chart.
channels:
  box: [0, 0]
  labels: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```
