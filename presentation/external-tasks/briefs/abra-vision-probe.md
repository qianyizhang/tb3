> **Source CT examples only — exact task/control PNGs and results remain absent; recover them through [official ABRA setup](https://github.com/Luab/ABRA/blob/688814615dc368a66276798cb864fe9a587d7e6c/README.md#2-download-datasets).**

# Identify an ABRA image modality or display treatment

Classify one preselected image with one option letter. The operation separates modality recognition from display-pipeline recognition; it makes no diagnosis.

## Given

### Original data

The controller injects a selected sidecar PNG into the first user message. Five UID-matched LIDC-IDRI-0003 source CT instances are shown through two pinned window formulas, at native 512×512 size. These are independently derived source examples, not recovered selected task PNGs. Exact generated probe task and control PNG remain absent; MRI/DX image examples remain missing.

### Supplied helpers

The generator selects the series, index and pipeline, supplies four options, and removes volume search. For 140 instances, its five indices are 14, 42, 70, 98 and 126. Indices follow stack-normal position order, falling back to InstanceNumber, not ZIP order. The seed does not change the selection formula.

### Callable tools

Only `submit_answer`, with three turns. No BI-RADS oracle tool is supplied. The image payload metadata is not injected with the first image; the system prompt may separately contain initial viewport window/level and study context. Exact realized hints are unverified without a run.

### Reference-only material

Generator state maps known modality or pipeline to a letter; the noise condition maps to N/A. No generated answer or participant result is bundled. This is a metadata-derived label, not clinical adjudication.

## Task specification

| Question | A | B | C | D |
|---|---|---|---|---|
| Modality | CT | MRI (including MR) | DX | N/A |
| Display treatment | Lung window | Soft tissue window | Breast MRI | N/A |

Normal modality probes use `dicom_preprocessor=default`; that transfer is not established by the retained pins, so its exact condition remains a missing socket. Lung/soft examples do not reconstruct it.

Normal CT display probes use rescaled HU with lung C=-600/W=1500 or soft-tissue C=40/W=400. Breast MRI uses the 1st–99th intensity percentiles, with flat-image fallback; its units are not HU. DX has modality probes only.

**Naming discrepancy:** `noise_gaussian` actually ignores input values and produces uniform integer noise in [0,255], seeded with 42 by default, at the same dimensions. It is neither Gaussian nor additive scan noise. No anatomy survives this replacement.

## Expected output

One `submit_answer.arguments.answer` string containing only A/B/C/D. The participant field stays empty; any interactive letter choice is visibly illustrative and is never sent to ABRA.

## Evaluation

The last submit_answer is compared with the generated expected string after lowercase/whitespace normalization. No participant score is shown. A label match cannot establish diagnosis, navigation skill or a causal effect of noise.

## Visual explanation

Select the question and display condition. Matched native CT source examples show the same selected instance under lung and soft-tissue transfer, with no resizing or interpolation. A separately labeled authored 8×8 HU ramp teaches clipping/scaling numerically. A separate seeded integer-noise grid shows value replacement, not a noisy patient scan. MRI is represented by percentile endpoints rather than a fabricated MRI. All toy cells and letter choices are labeled illustrative. The reader reference chapter reveals source label rules; leaving it or resetting covers them again.

## Sources

- [Pinned generator](https://github.com/Luab/ABRA/blob/688814615dc368a66276798cb864fe9a587d7e6c/scripts/task_generators/vision_probe.py)
- [Pinned actual noise implementation](https://github.com/Luab/ABRA/blob/688814615dc368a66276798cb864fe9a587d7e6c/preprocessor/pipelines/noise_gaussian.py)
- [Official data/setup route](https://github.com/Luab/ABRA/blob/688814615dc368a66276798cb864fe9a587d7e6c/README.md#2-download-datasets)
- [Resolution receipt](../sources/abra-vision-probe-resolution.json)

## Gaps

No exact generated task, sidecar PNG, actual control PNG, participant answer or score. Numerical transfer checks reproduce an abstract formula, not the original viewer image. Initial system window/level may offer information; no strict image-only claim is made. The task's “Gaussian” label differs from its implementation.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| Modality, normal/replacement noise | Selected image, four modality options | Judge visual category or N/A from supplied view |
| Display, normal/replacement noise | Selected processed image, four display options | Identify treatment or N/A; no volume search |

## Coverage

One probe definition with source-supported normal/control branches; no exhaustive case recovery or measured performance.
