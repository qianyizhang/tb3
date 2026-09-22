# Predict glioma grade through a tool chain

Segment the tumor, extract region features and classify high- versus low-grade glioma.

## Value

The workflow makes the intermediate evidence behind a classification inspectable.

## Given

### Original data

Required source modalities — brain: all of T1, T1c, T2, FLAIR.

### Supplied helpers

A case manifest, runtime state, typed artifact references and registered specialist tools. Fault/recovery variants may alter paths, arguments or available modalities.

### Callable tools

Registered tools: `identify_sequences`, `brats_mri_segmentation`, `extract_roi_features`, `classify_brain_glioma_grade`.

### Reference-only material

Evaluation targets are references, not extra solver inputs. Local filesystem visibility has not been audited by running this external task.

## Task specification

Required stage sequence: identify_sequences → brats_mri_segmentation → extract_roi_features → classify_brain_glioma_grade. Resolve actual case paths and pass each artifact to its downstream consumer.

## Expected output

Retain artifacts under these registry keys: `feature_table_path`, `classification_path`.

## Evaluation

The registry requires stage success plus csv non empty, json field non empty. These checks establish execution/artifact validity; they do not independently establish anatomical accuracy.

## Visual explanation

### Workflow

- Case modalities + runtime manifest
- Execute 4 required stage(s)
- Retained image / feature / report artifacts

### Input

**Contract view; native sample not yet illustrated.** Required source modalities — brain: all of T1, T1c, T2, FLAIR.

### Supplied helpers

**Given material, not an answer reveal.** A case manifest, runtime state, typed artifact references and registered specialist tools. Fault/recovery variants may alter paths, arguments or available modalities.

### Reference or output

**Expected artifact, not an actual prediction.** Retain artifacts under these registry keys: `feature_table_path`, `classification_path`.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| Source condition | A case manifest, runtime state, typed artifact references and registered specialist tools. Fault/recovery variants may alter paths, arguments or available modalities. | Correct artifact propagation is distinct from whether the features support the clinical grade. |

## Difficulty

Correct artifact propagation is distinct from whether the features support the clinical grade.

## Sources

- [Pinned task registry](https://github.com/Albertlongzi/BCER/blob/d10816712793a9e27f2e70640f9afc06f08a0c5c/configs/tasks_registry.json)

## Coverage

A shared definition brief for the linked catalogue entries. Case identities and source conditions remain in the catalogue; this is not a claim to enumerate all generated or external cases.

## Gaps

Native input/helper/reference views are still missing for this definition. The contract was read from source; no external model or benchmark run was launched.
