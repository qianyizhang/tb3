# HiESD · Map findings by gastric tissue strip

Build a coarse category map for each strip of tissue on a gastric resection slide.

## Value

Identify a region locally, place it within its strip, then summarize findings strip by strip.

## Given

### Original data

- **Sample:** one H&E gastric ESD slide with two tissue strips.
- **Image:** 39,887 × 28,702-pixel SVS at 0.2458 µm/pixel; a 64× downsampled thumbnail is also available.

### Supplied helpers

- Optional `c1`/`c2` strip masks identify which strip a point belongs to, not its histology.
- The teaching crop was selected from the reference and removes the search step.

### Callable tools

- Read the slide at multiple scales, mark strips and regions, and export a map.

### Reference-only material

- This sample has 88 coarse XML regions in six categories: gastritis, two types of intestinal metaplasia, lymphoid follicle, normal gland, and `tub1` adenocarcinoma.
- Regions cover groups of glands; they are not precise gland boundaries. Unannotated tissue is not a normal label.

## Task specification

- Identify coarse categories and their locations on each tissue strip.
- Summarize each strip and retain undecided areas.
- Use only annotated area as the denominator for any annotated-area fraction.

## Expected output

- `strip_map.json`: `strip_id`, `regions[{class, polygon_level0_px, confidence}]`, and a per-strip summary.
- Multiply XML thumbnail coordinates by 64 to map them to level-0 pixels.

## Evaluation

- Check supported region or patch categories first; assess strip assignment and coarse location separately.
- Exact boundary Dice, margin status, and invasion depth are unsupported by this reference.

## Visual explanation

### Workflow

- Full slide with optional strip masks
- Classify and locate regions within each strip
- Export a coarse map for each strip

### Input

![HiESD source thumbnail showing two gastric tissue strips without reference](../../../../.local/wsi-ground-truth/explainer/assets/hiesd-overview-input.jpg)

### Supplied helpers

- The official `c1`/`c2` masks can be supplied as a separate assistance condition.
- The shown 2,048 × 2,048-pixel crop begins at (32,192, 2,560) and was chosen using a `tub1` reference region.

### Reference or output

![HiESD coarse XML categories over the source thumbnail, not a model result](../../../../.local/wsi-ground-truth/explainer/assets/hiesd-overview-reference.png)

| Color | Reference class |
| --- | --- |
| Dark red `#8B0000` | `tub1` well-differentiated adenocarcinoma |
| Purple `#8A2BE2` | Normal gland |
| Blue `#0000FF` | Chronic gastritis |
| Bright green `#00FF00` | Lymphoid follicle |
| Dark green `#008000` | Complete intestinal metaplasia |
| Yellow `#FFFF00` | Incomplete intestinal metaplasia |

## Conditions

| Condition | Supplied help | Work remaining |
| --- | --- | --- |
| Original slide | Image and scale | Identify strips and build category maps |
| Strip masks supplied | `c1`/`c2` masks | Classify and locate regions within strips |

## Difficulty

- Multi-scale morphology and strip-level synthesis are task hypotheses, not measured difficulty.

## Sources

- [Native SVS on Figshare, CC BY 4.0](https://doi.org/10.6084/m9.figshare.28919840) · [pinned author supplement](https://huggingface.co/datasets/JSGe-AI/HiESD/tree/f35faff3300342aaa31c87465b264b98fa6b8726) · [dataset paper](https://www.nature.com/articles/s41597-025-05679-1) · [author code](https://github.com/JSGe-AI/HiESD).

## Coverage

- One paired SVS, thumbnail, category PNG/XML, and two strip masks. A second low-resolution preview has no paired WSI locally.

## Gaps

- The category PNG contains interpolation colors; this page uses the coarse XML rather than inventing a color remapping.
- No full-dataset audit, frozen scorer, or model run.
