---
schema: 2
id: healthagentbench-tumor-tiles
title: Search a whole slide for tumor-bearing tiles
locale: en
purpose: "Explain the pinned whole-slide tile-search contract with verified geometry and a symbolic missing-image boundary."
scope: "Authored grid only. No slide pixels, private mask, prediction or measured score."
recipe: healthagentbench-tumor-tiles-v1
asset_pack: retained-healthagentbench-tumor-tiles-symbolic-v2
source_class: symbolic-protocol
reference_policy: no-reference-assets
fps: 24
source_locators:
- presentation/external-tasks/briefs/healthagentbench-tumor-tiles.md
- presentation/external-tasks/sources/healthagentbench-tumor-tiles-resolution.json
- scripts/build_tumor_tiles_symbolic_assets.py
---

# Begin with the missing source image

```beat
id: input
scene: input
frames: 264
caption: "The WSI is required but absent here"
narration: "The task supplies a whole-slide image, but this collection view withholds the recovered derivative while source terms are resolved. This empty socket shows no tissue or tumor. The verified native extent is 114,688 by 100,352 level-zero pixels."
visual: "Missing-image socket and public task-row fields; no grid or answer initially."
channels:
  cursor: [0, 0]
  detail: [0, 0]
  reference: [0, 0]
```

# Inspect an abstract coordinate grid

```beat
id: inspect
scene: inspect
frames: 312
caption: "Inspect the coordinate grid"
narration: "A 256-pixel task tile at downsample 16 spans 4,096 native pixels. The verified slide extent yields 28 columns and 25 rows; the final row is only 2,048 native pixels high. This blank grid is authored geometry. The moving outline is an unclassified cursor, not a tumor finding."
visual: "Abstract 28 by 25 grid, clipped final row, and one unclassified cursor."
channels:
  cursor: [0, 1]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

# Map candidate positions to coordinates

```beat
id: operation
scene: operation
frames: 312
caption: "Map native pixels to tile coordinates"
narration: "Floor-dividing native x and y by 4,096 identifies a candidate grid cell. The private evaluator derives a positive cell only when label-2 tumor occupies at least 0.2 of that cell's mask patch. No mask or positive tiles are available in this explanation."
visual: "Pixel-to-grid arithmetic and empty candidate set; no patient content."
channels:
  cursor: [0, 1]
  detail: [1, 1]
  reference: [0, 0]
cut: intentional-cut
```

# Show the empty output contract

```beat
id: schema
scene: schema
frames: 276
caption: "Write the required submission"
narration: "The requested JSON retains task_id and instruction, sets contains_tumor, and lists integer x-y tile pairs. The pinned scorer deduplicates coordinates and uses tile-set F1; it does not read contains_tumor or enforce grid bounds. No participant prediction was generated."
visual: "Empty submission schema, with no selected coordinates."
channels:
  cursor: [0, 0]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# Keep the private answer outside

```beat
id: reference
scene: reference
frames: 228
caption: "Keep evaluator material separate"
narration: "The hidden expert mask and gold tile set are absent. Reward would require tile-level F1 of at least 0.90 against those private coordinates. This is a rule, not an observed result."
visual: "Unavailable reference and no score."
channels:
  cursor: [0, 0]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# State the acquisition limit

```beat
id: limits
scene: limits
frames: 252
caption: "Read the source and rights limit"
narration: "Bounded exact-slide ranges and a derived overview remain local audit evidence. The collection pack contains no derived WSI pixels pending registration and intended-use permission review under the original CAMELYON16 rules. Restore an image-backed explanation only with clear authorization and matched source provenance."
visual: "Symbolic scope and official acquisition route."
channels:
  cursor: [0, 0]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```
