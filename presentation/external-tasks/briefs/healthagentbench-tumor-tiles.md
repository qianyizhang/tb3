# Find tumor-bearing slide tiles

Locate every tumor-containing grid tile in a whole-slide pathology image. **This explanation is a symbolic protocol view:** bounded exact-slide source bytes and a decoded overview were recovered to local audit evidence, but source-image reuse and redistribution terms remain unresolved, so no slide pixels enter this collection pack.

## Given

### Original data

The pinned solver task supplies a whole-slide H&E image at `/data/slide/current/slide.tif`. The pack cannot display that image. The verified local source audit establishes its native level-zero extent, **114,688×100,352 px**, but this diagram contains no tissue, anatomy, tumor or patient image.

### Supplied helpers

The public `slide_0001` task row declares `analysis_tile_size=256`, `analysis_downsample=16` and `tumor_threshold=0.2`. A 256-px analysis tile spans 4,096 level-zero pixels per side. The editable `submission.json` template supplies task ID, instruction, `contains_tumor`, and an initially empty `predicted_tumor_tiles` list; its default `contains_tumor:false` is **not a gold label**.

### Callable tools

The pinned task permits local slide inspection and task-specific software under its conditions. No slide viewer, model, preparer, or evaluator is run in this explanation.

### Reference-only material

The verifier privately obtains an expert mask and derives gold grid coordinates where label-2 pixels occupy at least 0.2 of a tile's mask patch. Neither mask nor selected coordinates are in this pack. An image filename in the bootstrap can imply the answer; the first reader view shows only the opaque task ID and missing-image socket.

## Task specification

Search the whole slide, rather than a supplied tumor crop. The source dimensions and stride define **28 columns × 25 rows** (700 possible coordinates, x=0–27 and y=0–24); the last row is **2,048 level-zero pixels high**. `x=floor(level0_x/4096)` and `y=floor(level0_y/4096)` locate a candidate cell. The diagram's unclassified cursor demonstrates this mapping; it is not an image inspection, a selection, or evidence of tumor.

## Expected output

Write `/workspace/submission.json` as a one-row JSON list with the retained task ID and instruction, a `contains_tumor` boolean, and `predicted_tumor_tiles` as `{x:int,y:int}` coordinates. The pack contains an **empty prediction schema**, no participant answer.

## Evaluation

The pinned scorer normalizes predicted coordinates to a set, dropping duplicates, and computes tile-level precision, recall and F1 against private mask-derived gold. Reward is 1 only if F1≥0.90; `contains_tumor` is requested but not read by this tile scorer. Coordinate bounds are not enforced by the scorer, and Python boolean values can pass its integer type check; these are implementation quirks, not valid coordinate guidance. Both empty gold and prediction yield F1=0 in this scorer. No F1 or reward was observed. The separate CAMELYON16 challenge's AUC/FROC metrics are not this HealthAgentBench score.

## Visual explanation

The opening shows a plainly absent WSI input. Inspect reveals an **authored abstract grid** and moves a single unclassified coordinate cursor; no cell depicts tissue or a positive tile. The operation maps pixel positions to grid indices and explains the private 0.2 mask-fraction rule. Output and reference scenes preserve the empty prediction and unavailable evaluator answer. A common-header warning links the [official CAMELYON16 Rules](https://camelyon16.grand-challenge.org/Rules/) and the registration/permission route.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| Source condition | A fixed grid: each displayed 256×256 tile at downsample 16 covers 4096×4096 level-zero pixels. Task ID and output schema are supplied. | Search a large slide, ignore non-tissue and recognize tumor across variable tissue appearance. A selected crop would remove much of the search burden. |

## Difficulty

A whole-slide search is materially different from a cropped lesion example. The abstract grid explains coordinate bookkeeping but cannot establish a tumor location, completeness, or diagnostic performance.

## Sources

- [Pinned task prompt](https://github.com/microsoft/HealthAgentBench/blob/bcbb8085fd549469e2dc7455f4bfd68a1b98895a/tasks/tumor_area_selection_pathology_slide_0001/instruction.md).
- [Official CAMELYON16 Rules and access route](https://camelyon16.grand-challenge.org/Rules/).
- [Source resolution receipt](../sources/healthagentbench-tumor-tiles-resolution.json).

## Coverage

A shared definition brief for the linked catalogue entries. Case identities and source conditions remain in the catalogue; this is not a claim to enumerate all generated or external cases.

## Gaps

Only bounded TIFF ranges and a decoded overview were recovered to local ignored source-audit evidence; the full WSI was not recovered. Image reuse awaits intended-use and derivative-distribution authorization. Full-resolution inspection, hidden mask, participant prediction, and observed score are unavailable. Reopen image-backed presentation only with explicit terms/registration resolution, exact matched WSI identity and a separate private-reference boundary.

## Cases

The pictured grid is authored geometry, not a case image. Other cases may have different slide dimensions and positive tiles; the numbers above apply to the pinned `slide_0001` source audit only.
