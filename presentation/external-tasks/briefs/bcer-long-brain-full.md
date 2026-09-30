# Build the BCER brain tumor artifact and report chain

Build the BCER brain tumor artifact and report chain. This symbolic explanation is a task-contract illustration; no model, task tool or evaluator was run.

## Given

### Original data

A single BraTS-style case with T1, T1c, T2 and FLAIR NIfTI inputs; no matched four-sequence case is local.

### Supplied helpers

Case manifest, modality map and typed artifact registry.

### Callable tools

identify_sequences → conditional register_to_reference → brats_mri_segmentation → extract_roi_features → classify_brain_glioma_grade → generate_report.

### Reference-only material

Case-matched tumor mask and true grade are separate reference material, absent from this pack.

## Task specification

Map all four modalities; register T2/FLAIR to T1c only when geometry requires it. The segmenter may use its MONAI bundle or, when dependencies are absent, a T1c/FLAIR heuristic that can fill an empty threshold mask with a synthetic ellipsoid. Produce segmentation and WT mask, feature CSV, rule-based grade output, then a run report. The fallback and rule output are not patient truth.

## Expected output

seg_path and wt_mask_path NIfTI; feature_table_path CSV; classification_path JSON with predicted_grade; report_json_path JSON. No files were generated.

## Evaluation

The completion ratio has five required stage successes plus five artifact paths (10 checks). The separate success rule names those five tool successes. Seven invariants require the segmentation and WT paths/nonempty masks/affine match, a feature CSV row, nonempty predicted_grade, and nonempty report JSON. Registration is conditional, absent from the required-stage list for co-registered BraTS-style input. None of these checks compares a mask or grade against truth, and a nonempty fallback mask is not validation of MONAI segmentation.

## Visual explanation

The first view contains only the four empty source sockets and top acquisition warning. Later views distinguish conditional registration, bundle-versus-heuristic segmentation, ROI features, rule-based grade, and empty required output. The pinned report helper reads case-state/modality mapping, segmentation status and feature previews/volumes; it does not directly fetch the grade classifier's predicted_grade. The brain report helper defaults to a configured local VLM server for an additional structured report/image-QC attempt; the deterministic report JSON and model-generated content are separate artifacts. No server, model, or image-QC step was run. No private reference is mounted.

## Difficulty

No matching complete four-modality BraTS case, BCER saved output, or case-matched reference annotation/grade retained. The source-code comment says a missing MONAI bundle triggers heuristic fallback, but the executable branch only falls back when dependencies fail; a missing bundle with dependencies present raises. The report helper may mark optional registration missing when correctly skipped, and its brain report JSON does not directly include predicted_grade. BraTS 2021 Task 2 is MGMT methylation, not the BCER HGG/LGG grade target; an image alone would not supply latter truth. Reopen when an authorized matching source case and separately preserved output/reference roles are available.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| Source condition | A case manifest, runtime state, typed artifact references and registered specialist tools. Fault/recovery variants may alter paths, arguments or available modalities. | Maintaining sequence identity and artifact provenance across the full chain is central; report completion alone is weak anatomical evidence. |

## Sources

- [Pinned task source](https://github.com/Albertlongzi/BCER/blob/d10816712793a9e27f2e70640f9afc06f08a0c5c/configs/tasks_registry.json).
- [Official source route](https://www.med.upenn.edu/cbica/brats2021/).
- [Source resolution receipt](../sources/bcer-long-brain-full-resolution.json).

## Coverage

A shared definition brief for the linked catalogue entries. Case identities and source conditions remain in the catalogue; this is not a claim to enumerate all generated or external cases.
