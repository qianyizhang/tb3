# TIGER · Count immune cells by tissue compartment

Locate immune cells and measure where they occur in an annotated tissue region.

## Value

Counting cells and identifying the tissue around them are distinct steps. The task links the two.

## Given

### Original data

- **Sample:** `114S`, a breast H&E whole slide at 0.456694 µm/pixel.
- **Paired material:** three source-defined ROIs, tissue masks, whole-slide XML, and COCO cell boxes.

### Supplied helpers

- The first condition supplies an official ROI and scale, removing full-slide search.
- A comparison condition also supplies tissue reference labels, leaving cell detection and compartment assignment.

### Callable tools

- Zoom the image, mark cell centers, outline tissue regions, and summarize counts by compartment.

### Reference-only material

- Tissue masks identify compartments. The three paired ROIs contain 175, 323, and 20 source cell boxes.
- Lymphocytes and plasma cells are merged in this release; they cannot be scored as separate classes here.
- An unannotated area outside the ROIs is not a cell-negative reference.

## Task specification

- Mark tissue compartments and immune-cell centers; assign each cell to a compartment.
- Report count, annotated area, and density. Exclude mask class 0.
- Decide before evaluation whether tissue classes 2 and 6 are combined.

## Expected output

- `cells.csv`: `x_px, y_px, class, compartment`.
- `regions.geojson`: compartment outlines.
- `summary.csv`: `compartment, n_cells, area_mm2, density_per_mm2`.
- Map ROI coordinates back to the whole slide using the crop origin.

## Evaluation

- Assess tissue segmentation, cell detection, compartment assignment, and count error separately.
- Use the annotated compartment area as the density denominator. Cells/mm² is not the clinical stromal TIL area percentage.

## Visual explanation

### Workflow

- Official ROI and scale
- Find tissue and cells, then link them
- Export compartment counts, area, and density

### Input

![TIGER whole-slide source thumbnail; dense cell reference is limited to ROIs](../../../../.local/wsi-ground-truth/explainer/assets/tiger-overview-input.jpg)

### Supplied helpers

- Three official ROI locations are known. The paired ROI PNGs match native TIFF crops pixel for pixel (RGB mean absolute error 0).

### Reference or output

![TIGER ROI 1 source reference: colored tissue and yellow cell boxes, not a model result](../../../../.local/wsi-ground-truth/explainer/assets/tiger-roi1-reference.png)

| Color | Reference class |
| --- | --- |
| Red `#e6425e` | Invasive tumor |
| Blue `#28a8c7` | Tumor-associated stroma |
| Orange `#f08c38` | Healthy glands |
| Green `#88b929` | Inflamed stroma |
| Gray `#8792a7` | Other |
| Yellow boxes `#ffe600` | Lymphocytes and plasma cells |

## Conditions

| Condition | Supplied help | Work remaining |
| --- | --- | --- |
| Joint task | ROI and scale | Segment tissue, detect cells, assign compartments |
| Tissue supplied | Add tissue reference | Detect cells and count by known compartment |

## Difficulty

- Small-object detection and tissue-context assignment are separable hypotheses for a later trial.

## Sources

- [Official TIGER data guide](https://tiger.grand-challenge.org/Data/) · [AWS release](https://registry.opendata.aws/tiger/) · [example algorithm](https://grand-challenge.org/algorithms/tiger-algorithm-example/) · [CC BY-NC 4.0 terms](https://tiger-training.s3.us-west-2.amazonaws.com/license.txt).
- This selection uses the JB material. PanopTILs was not acquired for this fourth route.

## Coverage

- One WSI, three paired ROIs, and 518 source cell boxes. Other COCO ROIs are not counted as paired samples.

## Gaps

- No exhaustive full-slide cell reference, separate lymphocyte/plasma-cell labels, exact nuclear outlines, frozen scorer, or model run.
