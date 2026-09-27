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

- Tissue masks identify compartments. Pilot roi1 = COCO 942 (20 cells), roi2 = COCO 940 (175), roi3 = COCO 941 (323). Older teaching images use COCO order instead.
- Fixed-size source boxes encode cell points; they are not nuclear contours.
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

- This joint tissue/area/density contract remains proposed. Retained [original pilots](../../experiments/wsi-tiger-context-astra-medium/protocol.md) and [revised pilots](../../experiments/wsi-tiger-context-v2-sol6-xhigh/protocol.md) returned ROI-local `points.json` with compartment codes only.
- The revised point scorer matches one to one within 20 px and reports labels read at both source and submitted centers; neither is an evaluated tissue contour or density result.

- Assess tissue segmentation, cell detection, compartment assignment, and count error separately.
- Use the annotated compartment area as the density denominator. Cells/mm² is not the clinical stromal TIL area percentage.

## Visual explanation

The [canonical story](../stories/tiger-context.story.md) uses actual ROI pixels, a separate tissue/cell reference reveal, coordinate transforms and a worked density denominator. Its [source audit](../sources/tiger-context-audit.json) verifies nine source files and all 70 files in four unique frozen conditions. The [teaching pack notice](../../../../presentation/task-explorer/tiger-context/NOTICE.md) documents colors and terms; the older static image below keeps its own legend.

### Workflow

- Official ROI and scale
- Find tissue and cells, then link them
- Export compartment counts, area, and density

### Input

![TIGER whole-slide source thumbnail; dense cell reference is limited to ROIs](../../../../.local/wsi-ground-truth/explainer/assets/tiger-overview-input.jpg)

### Supplied helpers

- Three official ROI locations are known. The paired ROI PNGs match native TIFF crops pixel for pixel (RGB mean absolute error 0).

### Reference or output

![COCO 940 / pilot roi2 (older teaching ROI 1) source reference: colored tissue and yellow cell boxes, not a model result](../../../../.local/wsi-ground-truth/explainer/assets/tiger-roi1-reference.png)

| Color | Reference class |
| --- | --- |
| Red `#e6425e` | Invasive tumor |
| Blue `#28a8c7` | Tumor-associated stroma |
| Orange `#f08c38` | Healthy glands |
| Green `#88b929` | Inflamed tumor-associated stroma (code 6) |
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

- No exhaustive full-slide cell reference, separate lymphocyte/plasma-cell labels or exact nuclear outlines.
- Point-task freezes and diagnostic trials exist; a joint contour/area/density evaluator remains to be frozen. No new trial or held-out generalization claim follows from this explainer.
- Define boundary attribution, reference inclusion and the class 2/6 merge policy before evaluation.

## Worked reference example

COCO 940 / pilot roi2: code 2 has 45 cells in 324,146 pixels (0.06760694 mm²); code 6 has 129 in 82,968 pixels (0.01730459 mm²). Pooling gives 174 / 0.08491152 = **2,049.19 cells/mm²**, not the mean of the separate densities. Code 0 is excluded; zero area yields unavailable density. These are source-derived calculations, not predictions.

Source centers use the released COCO boxes. Mask lookup uses rounded center coordinates as in the frozen scorer; the historical teaching receipt used floor. All 518 centers are integer-valued, so the audited assignments agree here. The constructed (+2,+3)-pixel shift at COCO 941 center (465,870) demonstrates a label change from 1 to 2; it is not an agent-output claim.
