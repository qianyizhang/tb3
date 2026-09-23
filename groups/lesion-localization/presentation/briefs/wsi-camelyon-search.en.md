# CAMELYON16 · Find metastases across a whole slide

Search a lymph-node slide for tumor, then return each finding in slide coordinates.

## Value

The work is a sequence: survey at low magnification, inspect suspicious tissue, and map findings back to the full slide.

## Given

### Original data

- **Sample:** `tumor_091`, a positive H&E lymph-node slide.
- **Image:** pyramidal TIFF, 61,440 × 53,760 pixels at 0.227273 µm/pixel.

### Supplied helpers

- The proposed input includes the original slide, pixel scale, and a region reader.
- The teaching crop was selected using the reference. It demonstrates local inspection, not autonomous search.

### Callable tools

- Read an overview or a region at a chosen location and scale.
- Mark points or contours and export slide coordinates.

### Reference-only material

- The paired XML contains six Tumor polygons and one Exclusion polygon.
- Red marks tumor; cyan marks an excluded region. Polygon count is not lesion count.
- The reference is for reader reveal and evaluation, not a proposed solver input.

## Task specification

- Search the full slide and inspect candidate regions.
- Return locations and confidence; contours are optional. A negative answer is allowed.
- Define polygon merging and Exclusion rules before scoring.

## Expected output

- `lesions.json`: `slide_id` and `detections[]` with `x_px`, `y_px`, `confidence`, and optionally `polygon_px`.
- Coordinates use level 0, origin at the upper left.

## Evaluation

- Measure lesion recall and false positives per slide; score contours separately with IoU or Dice.
- Negatives, lesion matching tolerance, and a frozen scorer are still needed. This single positive teaching slide cannot rank systems.

## Visual explanation

### Workflow

- Full slide and scale
- Search, zoom, and verify candidates
- Export locations and optional contours

### Input

![CAMELYON16 full-slide source thumbnail without reference overlay](../../../../.local/wsi-ground-truth/explainer/assets/camelyon-overview-input.jpg)

### Supplied helpers

- The shown 1,600 × 1,600-pixel crop begins at level-0 coordinate (47,739, 31,340).
- It was selected using a Tumor annotation; finding that location is no longer part of the local demonstration.

### Reference or output

![CAMELYON16 source reference: red tumor and cyan exclusion, not a model result](../../../../.local/wsi-ground-truth/explainer/assets/camelyon-overview-reference.png)

## Conditions

| Condition | Supplied help | Work remaining |
| --- | --- | --- |
| Whole-slide search | Original image and scale | Search, verify, and locate lesions |
| Teaching crop | Reference-selected region | Inspect morphology; search cannot be assessed |

## Difficulty

- Slide coverage, scale changes, and false-positive control remain untested in this proposed task.

## Sources

- [Official AWS release and CC0 terms](https://registry.opendata.aws/camelyon/) · [file guide](https://camelyon-dataset.s3.us-west-2.amazonaws.com/CAMELYON16/README.md) · [dataset paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC6007545/).
- Radboudumc and UMC Utrecht published the paired image and XML. License wording on older pages differs; the receipt pins the supplying release.

## Coverage

- One paired positive slide and XML. Two additional selection-screen XML files have no paired slide in this local package.

## Gaps

- No negative slide, frozen scorer, lesion-level clinical review, or model run.
- The pyramid has padding; coordinate mapping must use its recorded level transform.
