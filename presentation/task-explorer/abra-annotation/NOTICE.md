# ABRA annotation source views

Native LIDC-IDRI-0003 CT (140 axial slices) and DICOM-LIDC-IDRI-Nodules SEG,
Nodule 1 / Annotation 12, are retained from the 2026-09-21 sample receipt.
Five full slices and eight reader-selected 111 x 111 crops use DICOM LINEAR
window center -600 HU, width 1500 HU. Native rows/columns are not resampled.
Patient right appears at image left. Pixel centers are zero-based (x=column,
y=row); display overlays add one half pixel in SVG coordinates. In-plane spacing
is 0.820312 mm; ascending patient-z slices are 2.5 mm apart. The crop origin
(313,292) is a reader-selected reference aid, never a supplied target location.

The pinned ABRA manifest lists one annotator for Nodule 1. All eight masks align
by source SOP UID, position, orientation and spacing. Replaying the selected pure
consensus and task-generator functions reproduces that single mask and yields
ordinary s066 and oracle Nodule 1 tasks targeting the same slice. Contours use
the largest marching-squares component at level 0.5, in native pixel coordinates.
This does not validate other nodules or reproduce a published benchmark run.

The ordinary task supplies slice 66 and a lung window; its reference is private.
The separate oracle task deliberately supplies reference-derived contours and
hardcoded confidence values through a callable tool. The oracle is not newly run
pathology inference. Reference-copy annotations and slice-penalty arithmetic are
author teaching examples, not saved agent answers or measured model performance.
Full Shapely scoring and OHIF interaction were not executed. The pure penalty
function and source logic, not a fabricated benchmark run, support the displayed
same-polygon arithmetic. Shape normalization is heuristic, not proven optimal.

Data attribution: Armato et al., LIDC-IDRI, TCIA, DOI 10.7937/K9/TCIA.2015.LO9QL9SX;
Fedorov et al., DICOM-LIDC-IDRI-Nodules, DOI 10.7937/TCIA.2018.h7umfurq.
Both data sources list CC BY 3.0. ABRA code is MIT at commit
688814615dc368a66276798cb864fe9a587d7e6c. No clinical or model accuracy is inferred.
Rebuild with scripts/audit_abra_annotation.py and scripts/build_abra_annotation_assets.py
into fresh local destinations. Exact source and derivation hashes are in the audit.
