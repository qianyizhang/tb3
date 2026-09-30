# Classify brain glioma grade through BCER tools

The BCER medium workflow orders four MRI modalities through segmentation, ROI features, and a rule-based HGG/LGG output. This is a **symbolic source-code explanation**: no matching case, feature table, classification, reference grade, model run, or score was retained.

## Given

### Original data

One case-matched NIfTI set containing **T1, contrast-enhanced T1c, T2, and FLAIR**. The four modality identities matter; an unrelated T1c image does not complete a case. No such four-sequence case is available here. The [official BraTS 2021 route](https://www.med.upenn.edu/cbica/brats2021/) requires registration/data access; BraTS Task 2 targets MGMT methylation, **not** this BCER HGG/LGG output.

### Supplied helpers

The BCER case manifest, runtime state, typed artifact registry, and registered tool interfaces guide routing. They do not supply a tumor mask, feature measurement, or grade answer. Fault profiles may mutate tokens, paths, arguments, or T1c/FLAIR bindings, so a file existing at a path does not prove correct modality meaning.

### Callable tools

`identify_sequences` → `brats_mri_segmentation` → `extract_roi_features` → `classify_brain_glioma_grade`. No tool was called for this explainer. Segmentation output defines the tumor ROI for feature extraction; the grade tool reads a CSV and writes classification JSON. The pinned segmentation source has a dependency-unavailable heuristic fallback using FLAIR and T1c intensities; its bundled-model branch is separate. A missing bundle in that branch is not itself a fallback trigger. Neither branch was run here or establishes a clinically valid mask.

### Reference-only material

For any **accuracy** study, a case-matched tumor annotation and independently established true HGG/LGG grade would be separate references. Neither is retained and neither is used by the pinned BCER structural scorer. Their absence here does not prove an executed runtime filesystem-isolation property.

## Task specification

Bind all four sequences to the correct roles, obtain tumor subregions, extract at least one ROI-feature row, then write a grade-classification artifact. The pinned feature tool resamples the selected ROI mask into each image grid and computes `volume_ml` from selected voxels times that image’s spacing product divided by 1,000. The pinned grade tool prefers rows marked as whole tumor; if none are marked, it uses all CSV rows. From valid nonnegative `volume_ml` values it takes the **maximum** and predicts HGG at or above the default **35 ml** threshold, otherwise LGG. If no valid volume exists, it selects HGG when at least two of four named texture-feature fields are present, otherwise LGG. This is a transparent heuristic, **not a trained or clinically validated grade model**. The optional `confidence` is formula-derived, not calibrated probability. This explanation never instantiates a case value or grade.

## Expected output

The artifact registry must carry `feature_table_path` to a CSV with at least one row and `classification_path` to JSON with a nonempty `predicted_grade`. Both are **outputs**, not supplied truth; neither file exists in this pack.

## Evaluation

The task-completion ratio checks **four required tool-stage successes and two required artifact paths** (six structural items). Separately, `success_criteria` requires `classify_brain_glioma_grade` tool success. Two invariants check a nonempty feature CSV and a `predicted_grade` JSON field whose value is not null, an empty string, empty list, or empty object. This invariant does not itself enforce an HGG/LGG enum. These are path, format, and workflow checks; they do **not** compare segmentation with an annotation, compare grade with a diagnosis, or measure HGG/LGG accuracy. A nonempty feature CSV can reach the grade tool even when no valid volume exists, triggering its texture-availability fallback.

## Visual explanation

The first scene has four empty modality sockets and a common-header source warning. The route scene names the ordered tools. The operation scene lets the reader focus one fixed stage at a time to inspect its required input, output artifact, and invariant; the classifier panel displays the **static rule**, with every case value and grade output unset. Output and limits scenes retain empty artifacts and a source/reference boundary. No patient image, segmentation, feature number, class label or tool success is simulated.

## Difficulty

The workflow depends on modality identity and propagation of the segmentation/feature artifacts. Structural completion is distinct from anatomical correctness and independent grade validity. Source-code rule transparency does not supply clinical evidence.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| Source condition | A case manifest, runtime state, typed artifact references and registered specialist tools. Fault/recovery variants may alter paths, arguments or available modalities. | Correct artifact propagation is distinct from whether the features support the clinical grade. |

## Sources

- [Pinned BCER task contract](https://github.com/Albertlongzi/BCER/blob/d10816712793a9e27f2e70640f9afc06f08a0c5c/configs/tasks_registry.json).
- [Pinned BCER grade-tool source](https://github.com/Albertlongzi/BCER/blob/d10816712793a9e27f2e70640f9afc06f08a0c5c/tools/brain_glioma_grade_classification.py).
- [Official BraTS 2021 data route](https://www.med.upenn.edu/cbica/brats2021/).
- [Source resolution receipt](../sources/bcer-medium-brain-grade-classify-resolution.json).

## Coverage

A shared definition brief for the linked catalogue entries. Case identities and source conditions remain in the catalogue; this is not a claim to enumerate all generated or external cases.
