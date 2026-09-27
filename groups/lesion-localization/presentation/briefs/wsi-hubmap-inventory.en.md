# HuBMAP · Count and measure glomeruli

**Proposed contour task:** find each glomerular profile, outline it and measure its area. Retained diagnostic pilots returned **points only**; they do not evaluate this fuller deliverable.

## Value

A glomerulus is a kidney filtering structure. Separate records expose missed profiles, duplicate entries and boundary errors that a union mask can hide.

## Given

### Original data

PAS kidney training TIFF `aaa6a05cc`: **13,013 × 18,484 level-0 pixels**, with OME spacing **0.65 µm/pixel** on both axes. Upper-left origin; x increases right and y down.

### Supplied helpers

Default: image and scale. Optional cortex/medulla polygons provide rough regional context, not glomerulus answers or an adjudicated negative domain. They were not supplied to the retained point pilots.

### Callable tools

Read crops, trace contours, reconcile overlapping views and compute geometry. Point pilots had a GT-free overview and crop helper; direct TIFF reads were also possible.

### Reference-only material

The source `gt_masks` member contains **99 glomerulus polygons**, initialized automatically and expert-corrected. Reader reveals and reference-selected crops are teaching aids, not solver inputs.

## Task specification

Survey the slide, retain one stable record per distinct profile and map crop-local coordinates back to level 0. Export centers, contours and calibrated area. Do not infer disease grades, three-dimensional volumes or whole-kidney counts.

## Expected output

`glomeruli.geojson` and `inventory.csv`: `id, center_x_px, center_y_px, area_um2`. Use polygon area centroids consistently; **pixel area × 0.65²** gives µm². The displayed worked example comes from source reference, not an agent answer.

## Evaluation

The contour proposal needs frozen one-to-one matching, edge-profile rules, valid reference coverage, per-object overlap and area-error measures. Unmatched candidates require adjudication before clinical false-positive claims. Point pilots instead match a point inside a polygon or within **50 µm of its edge**. The revised pilot reports reference recall and queues extras for review. Harbor reward checks the artifact contract, not contour accuracy.

## Visual explanation

### Workflow

Whole-slide input → optional context → teaching crop → reference contour → native coordinates → duplicate reconciliation → physical area → worked inventory.

### Input

![Source PAS thumbnail without glomerulus reference](../../../../.local/wsi-ground-truth/explainer/assets/hubmap-overview-input.jpg)

### Supplied helpers

The teaching crop starts at **(2016,6706)**, covers **1600 × 1600 native pixels (1.04 mm wide)** and was chosen using the first reference polygon. Two overlapping views of the same object demonstrate a constructed duplicate, not an observed agent error.

### Reference or output

![Source glomerulus contours in teal; reader reference, not a prediction](../../../../.local/wsi-ground-truth/explainer/assets/hubmap-overview-reference.png)

## Conditions

| Condition | Supplied help | Work remaining |
| --- | --- | --- |
| Proposed contour inventory | Image and scale | Search, outline, deduplicate, measure |
| Optional anatomical context | Rough cortex/medulla regions | Locate and outline individual profiles |
| Teaching crop | Reference-selected location | Inspect geometry; full-slide search removed |
| Original point pilot | GT-free overview and crop helper | Return level-0 centers; no contours |
| Revised reference-recall pilot | Same images; explicit uncertain-profile guidance | Return centers and notes; extras await review |

## Difficulty

Coverage, nearby-object identity and contour precision are distinct operations. Point results cannot establish contour or area performance. Public training exposure is unresolved.

## Sources

- [Author release v1, CC BY 4.0](https://zenodo.org/records/7729610) · [annotation methods](https://pmc.ncbi.nlm.nih.gov/articles/PMC10356924/).
- [Source receipt](../../../../datasets/receipts/wsi-teaching-samples.json) · [display derivation](../../../../presentation/task-explorer/hubmap-inventory/NOTICE.md).
- [Original point protocol](../../experiments/wsi-hubmap-inventory-astra-medium/protocol.md) · [revised point protocol](../../experiments/wsi-hubmap-inventory-v2-sol6-xhigh/protocol.md).

## Coverage

One TIFF and two annotation JSON members were CRC32/SHA-256 checked. The **33.6 GB archive was not acquired or checksum-verified**. The 99 polygons are not an independently adjudicated exhaustive count.

## Cases

All views use `aaa6a05cc`. Worked `ref-NNN` IDs follow one-based source-array order because original feature IDs repeat. A teaching crop is not an independent case.

## Gaps

The contour/area proposal has no frozen evaluator or evaluated contour output. Point pilots already exist under separate protocols. Reference inclusion, partial profiles and disease grades remain unresolved; no clinical adjudication or new trial is implied.
