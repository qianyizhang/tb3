# Outline a lung nodule inside an imaging viewer

Navigate to a CT slice and draw a circle or polygon around the requested lung nodule.

## Value

An outline localizes a finding for review and measurement. A correct tool call alone does not establish that the lesion was outlined correctly.

## Given

### Original data

LIDC-IDRI chest CT in the OHIF / Orthanc viewer.

### Supplied helpers

The ordinary task names a slice and specifies a lung window. The oracle variant offers reference-derived contours through a tool.

### Callable tools

Viewer navigation, image retrieval, windowing and annotation tools; oracle tasks add query_pathology_model.

### Reference-only material

Ordinary annotation is compared with reference polygons. In the oracle condition, reference-derived contours are deliberately returned through a tool.

## Task specification

Select the specified slice, apply the lung window and place a segmentation annotation. The inspected ordinary single-slice task permits 15 turns.

## Expected output

An annotation attached to the correct study and slice.

## Evaluation

This generator specifies IoU ≥ 0.5 against a reference polygon. The overall benchmark separately combines planning, execution and outcome.

## Visual explanation

### Workflow

- CT + slice hint
- Navigate and outline
- Viewer annotation

### Input

![Native CT slice](../../../presentation/tours/data/task-briefs/abra-input.png)

LIDC-IDRI-0003, slice 66 (zero-based ascending patient-z), from ABRA’s study manifest. Lung window: width 1500, center −600 HU. This reader-selected slice maximizes one annotation’s area; the full volume has 140 slices.

### Supplied helpers

Ordinary task: slice number and window settings, without an outline. Oracle task: a callable tool supplies a contour. Reveal the reference to see the kind of boundary oracle assistance provides.

### Reference or output

![Released annotation and reader-only crop](../../../presentation/tours/data/task-briefs/abra-reference.png)

Gold: source DICOM SEG “Nodule 1 — Annotation 12”, aligned by referenced image UID and geometry. Right: post-hoc enlargement chosen using the annotation. This is one source annotation, not a regenerated consensus polygon or agent prediction. LIDC-IDRI / TCIA, CC BY 3.0.

## Conditions

| Condition | Supplied help | Work remaining |
| --- | --- | --- |
| Slice hint | Slice number + lung window | Identify the nodule boundary and place the annotation. |
| Oracle contour | Reference-derived contour via pathology tool | Retrieve and transfer the supplied contour to the right slice. |

## Difficulty

Ordinary annotation still requires visual boundary judgment. The oracle variant supplies that boundary and emphasizes transferring it correctly into the viewer.

## Sources

- [Ordinary annotation generator](https://github.com/Luab/ABRA/blob/688814615dc368a66276798cb864fe9a587d7e6c/scripts/task_generators/tier3.py)
- [Oracle generator](https://github.com/Luab/ABRA/blob/688814615dc368a66276798cb864fe9a587d7e6c/scripts/task_generators/tier3_oracle.py)
- [Task suite and scoring](https://github.com/Luab/ABRA/blob/688814615dc368a66276798cb864fe9a587d7e6c/README.md)

- [Exact study manifest](https://github.com/Luab/ABRA/blob/688814615dc368a66276798cb864fe9a587d7e6c/data/studies/study_manifest.json)
- [LIDC-IDRI attribution](https://www.cancerimagingarchive.net/collection/lidc-idri/)
- [Sample download and rendering receipt](../samples.json)

## Coverage

Viewer control · metadata QA · vision probes · annotation · oracle annotation · longitudinal lesion tasks · BI-RADS · oracle BI-RADS.

## Gaps

CT and source annotation are available. Generated YAML, consensus regeneration, viewer interaction and actual agent annotation remain uncurated. Data acquisition alone does not reproduce those results.
