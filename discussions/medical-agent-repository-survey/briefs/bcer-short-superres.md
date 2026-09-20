# Resample an MRI volume

Produce an MRI volume on the requested sampling grid.

## Value

A common grid allows later processing to consume compatible arrays.

## Given

### Original data

Required source modalities — prostate: one or more of T2w, ADC, DWI_highb; brain: one or more of T1, T1c, T2, FLAIR.

### Supplied helpers

A case manifest, runtime state, typed artifact references and registered specialist tools. Fault/recovery variants may alter paths, arguments or available modalities.

### Callable tools

Registered tools: `resample_image`.

### Reference-only material

Evaluation targets are references, not extra solver inputs. Local filesystem visibility has not been audited by running this external task.

## Task specification

Required stage sequence: resample_image. Resolve actual case paths and pass each artifact to its downstream consumer.

## Expected output

Retain artifacts under these registry keys: `resampled_nifti`.

## Evaluation

The registry requires stage success plus path exists, nifti nonempty. These checks establish execution/artifact validity; they do not independently establish anatomical accuracy.

## Visual explanation

### Workflow

- Case modalities + runtime manifest
- Execute 1 required stage(s)
- Retained image / feature / report artifacts

### Input

**Contract view; native sample not yet illustrated.** Required source modalities — prostate: one or more of T2w, ADC, DWI_highb; brain: one or more of T1, T1c, T2, FLAIR.

### Supplied helpers

**Given material, not an answer reveal.** A case manifest, runtime state, typed artifact references and registered specialist tools. Fault/recovery variants may alter paths, arguments or available modalities.

### Reference or output

**Expected artifact, not an actual prediction.** Retain artifacts under these registry keys: `resampled_nifti`.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| Source condition | A case manifest, runtime state, typed artifact references and registered specialist tools. Fault/recovery variants may alter paths, arguments or available modalities. | Interpolation changes the grid but does not by itself recover newly measured anatomical detail. |

## Difficulty

Interpolation changes the grid but does not by itself recover newly measured anatomical detail.

## Sources

- [Pinned task registry](https://github.com/Albertlongzi/BCER/blob/d10816712793a9e27f2e70640f9afc06f08a0c5c/configs/tasks_registry.json)

## Coverage

A shared definition brief for the linked catalogue entries. Case identities and source conditions remain in the catalogue; this is not a claim to enumerate all generated or external cases.

## Gaps

Native input/helper/reference views are still missing for this definition. The contract was read from source; no external model or benchmark run was launched.
