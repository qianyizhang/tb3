# Process cardiac cine MRI into a report

Segment a beating-heart image sequence, extract features, classify disease and generate a report.

## Value

Time-resolved cardiac images support assessment of heart structure and function.

## Given

### Original data

Required source modalities — cardiac: one or more of cine_nifti, cine_h5.

### Supplied helpers

A case manifest, runtime state, typed artifact references and registered specialist tools. Fault/recovery variants may alter paths, arguments or available modalities.

### Callable tools

Registered tools: `identify_sequences`, `segment_cardiac_cine`, `extract_roi_features`, `classify_cardiac_cine_disease`, `generate_report`.

### Reference-only material

Evaluation targets are references, not extra solver inputs. Local filesystem visibility has not been audited by running this external task.

## Task specification

Required stage sequence: identify_sequences → segment_cardiac_cine → extract_roi_features → classify_cardiac_cine_disease → generate_report. Resolve actual case paths and pass each artifact to its downstream consumer.

## Expected output

Retain artifacts under these registry keys: `seg_path`, `classification_path`, `feature_table_path`, `report_json_path`.

## Evaluation

The registry requires stage success plus nifti nonempty, json field non empty, csv non empty, json non empty. These checks establish execution/artifact validity; they do not independently establish anatomical accuracy.

## Visual explanation

### Workflow

- Case modalities + runtime manifest
- Execute 5 required stage(s)
- Retained image / feature / report artifacts

### Input

**Contract view; native sample not yet illustrated.** Required source modalities — cardiac: one or more of cine_nifti, cine_h5.

### Supplied helpers

**Given material, not an answer reveal.** A case manifest, runtime state, typed artifact references and registered specialist tools. Fault/recovery variants may alter paths, arguments or available modalities.

### Reference or output

**Expected artifact, not an actual prediction.** Retain artifacts under these registry keys: `seg_path`, `classification_path`, `feature_table_path`, `report_json_path`.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| Source condition | A case manifest, runtime state, typed artifact references and registered specialist tools. Fault/recovery variants may alter paths, arguments or available modalities. | Every stage depends on earlier masks and temporal data; a completed report need not be medically correct. |

## Difficulty

Every stage depends on earlier masks and temporal data; a completed report need not be medically correct.

## Sources

- [Pinned task registry](https://github.com/Albertlongzi/BCER/blob/d10816712793a9e27f2e70640f9afc06f08a0c5c/configs/tasks_registry.json)

## Coverage

A shared definition brief for the linked catalogue entries. Case identities and source conditions remain in the catalogue; this is not a claim to enumerate all generated or external cases.

## Gaps

Native input/helper/reference views are still missing for this definition. The contract was read from source; no external model or benchmark run was launched.
