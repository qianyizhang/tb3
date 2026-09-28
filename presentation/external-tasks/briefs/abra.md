# Outline a lung nodule inside an imaging viewer

**Identify a boundary on the requested native CT slice and attach a circle or
polygon annotation.** The ordinary condition requires visual judgment; the
separate oracle condition supplies a source-derived contour through a tool.

## Value

A correctly placed annotation combines image interpretation, pixel geometry and
viewer attachment. Successful tool syntax alone does not establish any of them.

## Given

### Original data

LIDC-IDRI-0003 CT from ABRA's pinned study manifest: 140 axial images, each
512 × 512 pixels. The retained source series has 0.820312 mm in-plane spacing
and 2.5 mm slice steps. Zero-based slices are ordered by ascending patient-z.
The task expects an OHIF/Orthanc environment; this explanation is a calibrated
source visualization, not a replay of that environment.

### Supplied helpers

The regenerated ordinary `t3_seg_lidc_idri_0003_nodule_1_s066` prompt names
**slice 66**, Nodule 1, and lung window width 1500 / center −600 HU. It supplies
no boundary, target point or reference mask. The initial viewer slice is 0.

The separate oracle task asks the agent to query an overview, request a contour
and transfer it to the recommended slice. The prepared oracle uses source
reference polygons, not fresh pathology-model inference. Its 0.95 overview
confidence and per-slice taper are hardcoded, not measured calibration.

### Callable tools

Series navigation, slice selection, windowing, image retrieval and circle/polygon
annotation. Coordinates are zero-based **native image pixels**, x=column and y=row.
The annotation tool requires a label, slice index and region geometry, and writes
to the active series' labelmap. Oracle tasks add `query_pathology_model`.

### Reference-only material

The source DICOM SEG is Nodule 1 / Annotation 12. The pinned manifest lists only
one annotator for this nodule. All eight SEG frames match their CT source image
UID, position, orientation and pixel spacing. Applying the pinned volumetric
≥50% consensus function therefore reproduces that annotator's mask on slices
62–69; it does not create independent expert consensus. The generator extracts
the largest marching-squares contour per nonempty slice.

The ordinary solver does not receive those polygons. In the oracle condition,
the same reference-derived contour is deliberately exposed by the oracle tool.

## Task specification

Select the correct CT series, navigate to the specified slice, apply the lung
window, inspect the image and place a circle or polygon around the nodule.
The ordinary single-slice task allows 15 turns and declares vision required.
The oracle single-nodule task allows 10 turns and declares vision unnecessary;
its representative slice is also 66 in this source case.

## Expected output

An annotation attached to the active CT series and the intended slice. The
polygon tool takes `label`, `slice_index` and `points: [[x,y], …]`, and declares a
segmentation ID, segment index, slice index and filled-pixel count in its return.
The explainer's dashed reference-copy polygon is an author illustration of this
contract, not a saved agent result. No live OHIF interaction was executed.

## Evaluation

The pinned single-slice scorer selects the highest **raw IoU minus slice penalty**
among extracted geometries. Polygon outcome uses that nonnegative score directly.
Circle and rectangle outcomes divide by a reference-derived shape heuristic,
capped at 1. The heuristic is not a demonstrated global optimum. The threshold
0.5 defines a reported hit on the normalized outcome; it is not simply raw IoU.

A same-polygon reference copy has analytical IoU 1. The exact penalty function
subtracts 0.2, 0.4 and 0.6 for one-, two- and three-slice offsets, then 1 for larger
offsets. Adjacent-slice copies can therefore meet the hit threshold. An absent
slice index has no scorer penalty, although the tool schema requires that field.
These are author arithmetic examples, not clinical/model scores or full Shapely
scorer execution. Full scoring and actual viewer attachment remain unverified.

ABRA's overall score combines planning 0.20, execution 0.30 and outcome 0.50.
No overall score or model comparison is produced here. Source overlap does not
establish diagnostic correctness or completeness of a scan review.

## Visual explanation

### Workflow

- Navigate from the initial CT view to the supplied slice and lung window.
- Determine a boundary, or query the separate oracle for a supplied contour.
- Attach native-pixel geometry and distinguish overlap from attachment scoring.

### Input

Five native full-field slices illustrate navigation; source pixels are not
resampled. A white coordinate witness at (128,256) is an author-chosen ruler
point, not a lesion hint. LPS millimeters are derived from native DICOM geometry;
annotation arguments remain in image pixels.

### Supplied helpers

Ordinary: slice and window only. Oracle: overview and source-derived contour,
revealed separately. A source contour does not appear in the ordinary input view.

### Reference or output

Reader reference reveal shows the eight source masks and native 111 × 111 crops
with origin (313,292). Crops are reference-selected, not solver hints. Slice 66
has 629 labeled pixels. Teal solid is reader reference; yellow dashed is an
author reference-copy annotation; blue dotted is the oracle contour.

## Conditions

| Condition | Supplied help | Work remaining |
| --- | --- | --- |
| Ordinary s066 | Slice 66 and lung window | Judge the boundary and attach an annotation; 15 turns. |
| Oracle Nodule 1 | Source-derived overview and contour through a tool | Query and transfer the contour to the proper slice; 10 turns. |

## Difficulty

Native-pixel geometry, slice identity and active series must stay consistent.
Ordinary visual boundary judgment and oracle contour transfer are different
capabilities. A score above threshold need not prove exact slice attachment.

## Coverage

One source nodule and two regenerated conditions at ABRA commit
`688814615dc368a66276798cb864fe9a587d7e6c`. The full benchmark's other nodules,
volumetric tasks and task families are not reproduced by this example.

## Gaps

No retained agent output, live OHIF session, full benchmark scorer replay or
independent clinical adjudication is claimed. Pure selected generator functions
and source geometry were checked without launching a trial or installing runtimes.

## Sources

- [Source audit, exact hashes and reconstruction limits](../sources/abra-annotation-audit.json)
- [Native source derivation and attribution](../../task-explorer/abra-annotation/NOTICE.md)
- [Original sample acquisition receipt](../samples.json)
- [Ordinary and consensus generator](https://github.com/Luab/ABRA/blob/688814615dc368a66276798cb864fe9a587d7e6c/scripts/task_generators/tier3.py)
- [Oracle generator](https://github.com/Luab/ABRA/blob/688814615dc368a66276798cb864fe9a587d7e6c/scripts/task_generators/tier3_oracle.py)
- [Pinned outcome scorer](https://github.com/Luab/ABRA/blob/688814615dc368a66276798cb864fe9a587d7e6c/src/scoring/outcome/iou_scorer.py)
- [Native pixel tool contract](https://github.com/Luab/ABRA/blob/688814615dc368a66276798cb864fe9a587d7e6c/src/tasks/tool_registry.py)
- [Exact study manifest](https://github.com/Luab/ABRA/blob/688814615dc368a66276798cb864fe9a587d7e6c/data/studies/study_manifest.json)
- [LIDC-IDRI CT data](https://www.cancerimagingarchive.net/collection/lidc-idri/)
- [DICOM-LIDC-IDRI-Nodules SEG data](https://www.cancerimagingarchive.net/analysis-result/dicom-lidc-idri-nodules/)
