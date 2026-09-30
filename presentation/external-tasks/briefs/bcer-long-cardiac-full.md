# Turn cardiac cine MRI into BCER segmentation, a disease-group rule, and a report

This is a **symbolic, source-code-backed workflow explanation**. No matched cine, BCER-generated mask, feature table, classification, report, expert mask, disease-group reference, or run is retained.

## Given

### Original data

One case-matched cardiac cine NIfTI or raw cine H5. The H5 branch needs reconstruction to NIfTI before cine segmentation; reconstruction is conditional and is not one of the five required success stages. The BCER dataset documentation gives ACDC ED/ES 3D NIfTI examples, but one 3D phase does not establish a 4D temporal curve. No matching case is available here. [Official ACDC data route](https://www.creatis.insa-lyon.fr/Challenge/acdc/databases.html).

### Supplied helpers

The case manifest, runtime state/artifact registry, callable tools, and `Info.cfg` phase metadata when available. ED/ES values in `Info.cfg` are 1-based and are converted to zero-based frame indices. The same file may contain `Group`, an answer-bearing disease-group field. The pinned classifier reads and echoes it as `ground_truth_group`/`ground_truth_match` if present; this source behavior does **not** establish independent validation or enforced answer isolation.

### Callable tools

`identify_sequences` → conditional raw-H5 reconstruction → `segment_cardiac_cine` → `extract_roi_features` → `classify_cardiac_cine_disease` → `generate_report`. None was called for this explainer. The segmentation source accepts a 3D phase or splits a 4D cine into 3D frames. With default ED/ES-only processing it uses valid phase metadata; otherwise all frames are processed. Its declared ACDC labels are 1 RV, 2 myocardium, 3 LV. A label declaration is not expert truth.

### Reference-only material

A case-matched expert segmentation and independently established clinical disease group would be needed for accuracy. Neither is retained. Because the pinned classifier may read `Info.cfg Group`, the historical source code alone does not prove that an answer-bearing field is isolated from the solver. This explainer has no reference asset.

## Task specification

Produce segmentation, a feature CSV, rule-based group classification, then report JSON. ROI-feature extraction uses masks and image grids for a separate required CSV. The classifier **does not consume that CSV**: it computes LV/RV EDV, ESV and EF, myocardial measures and a contraction proxy from segmentation frames. It chooses ED/ES from explicit paths/indices, valid `Info.cfg`, or LV-volume extrema when available; one 3D phase can map ED and ES to the same frame and cannot support a temporal curve. The group rule can output NOR, MINF, DCM, HCM, RV, or **UNCLASSIFIED**. Its `needs_vlm_review` flag is a rule output, not adjudication. `generate_report` reads run state and artifacts to write report JSON; that report is answer-owned output, not a clinical reference.

## Expected output

`seg_path` NIfTI, `feature_table_path` CSV, `classification_path` JSON with `predicted_group`, and `report_json_path` JSON. All four paths are empty in this teaching pack. No patient phase volume, disease group, report finding, or metric is instantiated.

## Evaluation

The task-completion ratio has **five required tool-stage successes plus four required artifact paths = nine checks**. A separate success rule requires those five tools to succeed. Four invariants test nonempty segmentation NIfTI, feature CSV (at least one row), classification JSON `predicted_group`, and report JSON. A nonempty `UNCLASSIFIED` group may satisfy the JSON-field invariant. None compares segmentation with an expert mask, group with an independent diagnosis, or report with clinical truth. The structural scorer therefore does not establish diagnostic correctness.

## Visual explanation

Start with an absent-input socket and the common-header acquisition warning. A symbolic branch selector distinguishes raw H5 requiring reconstruction from cine NIfTI. A phase selector shows how 3D single-phase, 4D valid ED/ES metadata, or 4D missing metadata changes phase handling, without drawn anatomy or values. The operation view keeps required feature CSV parallel to segmentation-derived classification, followed by report generation. Output paths remain empty; references remain absent.

## Difficulty

Modality and phase identity, segmentation geometry, feature/report artifacts, and label-bearing metadata must be tracked separately. Static rule visibility is not evidence of a correct mask or disease group.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| Source condition | A case manifest, runtime state, typed artifact references and registered specialist tools. Fault/recovery variants may alter paths, arguments or available modalities. | Every stage depends on earlier masks and temporal data; a completed report need not be medically correct. |

## Sources

- [Pinned BCER task contract](https://github.com/Albertlongzi/BCER/blob/d10816712793a9e27f2e70640f9afc06f08a0c5c/configs/tasks_registry.json).
- [Pinned cine segmentation source](https://github.com/Albertlongzi/BCER/blob/d10816712793a9e27f2e70640f9afc06f08a0c5c/tools/cardiac_cine_segmentation.py) and [classifier source](https://github.com/Albertlongzi/BCER/blob/d10816712793a9e27f2e70640f9afc06f08a0c5c/tools/cardiac_cine_classification.py).
- [Official ACDC source route](https://www.creatis.insa-lyon.fr/Challenge/acdc/databases.html).
- [Source resolution receipt](../sources/bcer-long-cardiac-full-resolution.json).

## Coverage

A shared definition brief for the linked catalogue entries. Case identities and source conditions remain in the catalogue; this is not a claim to enumerate all generated or external cases.
