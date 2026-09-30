# Set an ABRA medical viewer to a requested state

**Mixed illustration — source CT is retained; loaded OHIF viewport and slice mapping are missing. Obtain the study through the official TCIA collection.** [Official acquisition route](https://www.cancerimagingarchive.net/collection/lidc-idri/).

A pinned ABRA viewer-control task asks for a viewport state, not a diagnosis. This explanation uses **one real, retained LIDC-IDRI-0003 CT archive member** as a fixed source preview and a **symbolic viewer control**. No OHIF action, loaded viewport state, agent result, or score was retained.

## Given

### Original data

The task starts from an OHIF/Orthanc study and a prompt requesting a viewer change. ABRA's public manifest identifies a LIDC-IDRI-0003 CT series with **140 DICOM instances**. The retained CT archive contains all 140 files; all share the manifest Study and Series UIDs. Its fixed teaching preview is archive member `00000001.dcm`, DICOM `InstanceNumber=80`, 512×512 pixels. **Archive order and DICOM instance number are not verified OHIF `sliceIndex` values.** The preview uses the member's DICOM slope/intercept and window center −600/width 1600. The actual loaded OHIF viewport, order and index-to-image mapping remain unavailable.

### Supplied helpers

The task description supplies the requested slice number. The study/series manifest supplies instance counts and identifiers. The separate series-selection variant may call `get_study_series`. No segmentation, report, diagnosis, or image finding is supplied by this slice-navigation task.

### Callable tools

For the representative variant, `set_viewport_slice` would set the active viewport index. Other pinned tier-1 variants call `set_window_level`, combine slice and window control, or use `get_study_series` then `select_series`. None was called here. The local mock control is not OHIF.

### Reference-only material

The generated task YAML repeats a requested target in `expected_outcome` for the scorer. For this slice variant, **70 is already visible in the task description**; it is not hidden clinical truth. The grader-only expected-state representation stays separate from any observed final viewport state, which is absent.

## Task specification

Static derivation from the pinned generator and manifest yields task `t1_slice_lidc_idri_0003`: start at index **0**, request `140 // 2 = 70`, and use `set_viewport_slice`. This is a requested **zero-based state index**, not DICOM `InstanceNumber` and not proof that the fixed preview corresponds to index 70. A local mock slider can illustrate candidate state values without calling the viewer. The other variants have distinct target fields and tools; their task answers are not conflated with this slice request.

## Expected output

A final OHIF viewport state containing API `sliceIndex=70` is the requested outcome. No final API state, screenshot of the loaded viewer, action trace, or observed score exists in this pack. The local control value is an illustration only.

## Evaluation

`StateDiffScorer` maps YAML `slice_index` to API `sliceIndex` and compares only expected fields present in the task outcome. A missing final-state field fails; numeric comparison uses absolute difference ≤ default **0.01**; string fields use string equality. Field passes divided by the number of checked fields gives partial credit. Window-preset tasks set tolerance **1.0**. This is viewer-state comparison, not verification of CT anatomy, physical slice order, or clinical interpretation. No scorer was run.

## Visual explanation

An actual fixed CT source preview establishes what data type the viewer would display; its archive member and DICOM instance are labeled explicitly. A separate symbolic state-control diagram maps prompt target 70 → hypothetical `set_viewport_slice(slice_index=70)` → empty final-state slot. An accessible local candidate-index slider can move within 0–139, but is labeled as a mock value and never as a performed action. The output scene shows the requested API field and the absent observed state side by side.

## Difficulty

The task is about controlling and checking state across a viewer API. Manifest order, archive member names, DICOM instance numbers, anatomical z positions, and OHIF indices are different concepts until the viewer's actual ordering is inspected.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| Source condition | Exact target slice/window parameters or a series description; metadata-query tools. | Coordinate multiple UI operations and verify the final state; anatomical interpretation is usually unnecessary. |

## Sources

- [Pinned ABRA tier-1 task generator](https://github.com/Luab/ABRA/blob/688814615dc368a66276798cb864fe9a587d7e6c/scripts/task_generators/tier1.py) and [state-difference scorer](https://github.com/Luab/ABRA/blob/688814615dc368a66276798cb864fe9a587d7e6c/src/scoring/outcome/state_diff_scorer.py).
- [LIDC-IDRI collection, attribution and access terms](https://www.cancerimagingarchive.net/collection/lidc-idri/) and [TCIA data usage policy](https://www.cancerimagingarchive.net/data-usage-policies-and-restrictions/). The original CT archive's `LICENSE` is retained locally.
- [Source resolution receipt](../sources/abra-viewer-control-resolution.json).

## Coverage

This shared brief explains the representative slice-navigation task and names other pinned viewer-control variants. It asserts neither that OHIF loaded the retained DICOM archive nor that a viewer action or state comparison occurred.

## Runtime visibility limit

This source audit establishes the public prompt target, callable tool schema and scorer fields. It does not establish live solver filesystem isolation, task YAML placement or loaded viewer ordering; no source-proven runtime was launched. The reader pack contains no private grader asset.
