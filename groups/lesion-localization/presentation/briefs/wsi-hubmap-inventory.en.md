# HuBMAP · Count and measure glomeruli

Find every glomerulus on a kidney slide, then outline and measure each one.

## Value

A glomerulus is a small filtering unit. An object list makes misses, duplicates, and area errors inspectable separately.

## Given

### Original data

- **Sample:** `aaa6a05cc`, a PAS-stained kidney training slide.
- **Image:** 13,013 × 18,484-pixel TIFF at 0.65 µm/pixel.

### Supplied helpers

- The default input is the image and physical scale; an anatomical-region JSON can be added as context.
- The teaching crop centers on a reference object, so it cannot test full-slide search.

### Callable tools

- Read at multiple scales, edit contours, remove duplicates, and calculate polygon area.

### Reference-only material

- The source package has 99 glomerulus polygons in image coordinates, drafted with machine assistance and corrected by experts.
- A separate anatomical-region file is optional context, not a disease-grade reference.

## Task specification

- Survey the slide and return a complete list without duplicates.
- Record a center, contour, and physical area for each object.
- Distinguish adjacent objects; do not infer disease grades.

## Expected output

- `glomeruli.geojson` with contours and `inventory.csv` with `id, center_x_px, center_y_px, area_um2`.
- Convert polygon pixel area with 0.65² µm² per pixel.

## Evaluation

- Match objects one to one, then report misses, duplicates, and false detections.
- Score contour overlap and area error for matched objects. A global Dice score can hide missed small objects.

## Visual explanation

### Workflow

- Original PAS slide and scale
- Find, verify, and deduplicate objects
- Export contours, count, and areas

### Input

![HuBMAP PAS kidney source thumbnail without reference](../../../../.local/wsi-ground-truth/explainer/assets/hubmap-overview-input.jpg)

### Supplied helpers

- The shown 1,600 × 1,600-pixel crop begins at (2,016, 6,706), spans about 1.04 mm, and was chosen using the first reference polygon.

### Reference or output

![HuBMAP source glomerulus contours in teal, not a model result](../../../../.local/wsi-ground-truth/explainer/assets/hubmap-overview-reference.png)

## Conditions

| Condition | Supplied help | Work remaining |
| --- | --- | --- |
| Whole-slide inventory | Image and physical scale | Search, segment, deduplicate, measure |
| Teaching crop | Reference-selected region | Inspect structure and contours only |

## Difficulty

- Slide coverage, tubule–glomerulus distinction, and deduplication have not been measured in a model trial.

## Sources

- [Author Zenodo release v1, CC BY 4.0](https://zenodo.org/records/7729610) · [challenge site](https://cns-iu.github.io/ccf-research-kaggle-2021/) · [dataset paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC10356924/).
- Three ZIP members were extracted and checked individually. The full 33.6 GB archive was not acquired or checksum-verified.

## Coverage

- One TIFF, glomerulus JSON, and anatomical-region JSON. The 99 polygons are source reference objects, not model results.

## Gaps

- No disease-grade reference, frozen scorer, clinical review, or model run. A public training slide does not establish held-out generalization.
