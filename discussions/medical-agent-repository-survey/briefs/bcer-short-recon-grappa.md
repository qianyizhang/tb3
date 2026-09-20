# Reconstruct accelerated cardiac MRI

Turn undersampled multi-coil MRI measurements into a reconstructed image with GRAPPA.

## Value

Reconstruction is needed before raw MRI measurements become interpretable images.

## Given

### Original data

Required source modalities — cardiac: one or more of h5, raw_kspace.

### Supplied helpers

A case manifest, runtime state, typed artifact references and registered specialist tools. Fault/recovery variants may alter paths, arguments or available modalities.

### Callable tools

Registered tools: `reconstruct_grappa`.

### Reference-only material

Evaluation targets are references, not extra solver inputs. Local filesystem visibility has not been audited by running this external task.

## Task specification

Required stage sequence: reconstruct_grappa. Resolve actual case paths and pass each artifact to its downstream consumer.

## Expected output

Retain artifacts under these registry keys: `reconstructed_nifti`.

## Evaluation

The registry requires stage success plus path exists, nifti nonempty. These checks establish execution/artifact validity; they do not independently establish anatomical accuracy.

## Visual explanation

### Workflow

- Case modalities + runtime manifest
- Execute 1 required stage(s)
- Retained image / feature / report artifacts

### Input

**Contract view; native sample not yet illustrated.** Required source modalities — cardiac: one or more of h5, raw_kspace.

### Supplied helpers

**Given material, not an answer reveal.** A case manifest, runtime state, typed artifact references and registered specialist tools. Fault/recovery variants may alter paths, arguments or available modalities.

### Reference or output

**Expected artifact, not an actual prediction.** Retain artifacts under these registry keys: `reconstructed_nifti`.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| Source condition | A case manifest, runtime state, typed artifact references and registered specialist tools. Fault/recovery variants may alter paths, arguments or available modalities. | Raw measurement dimensions and calibration must reach the correct tool in the correct form. |

## Difficulty

Raw measurement dimensions and calibration must reach the correct tool in the correct form.

## Sources

- [Pinned task registry](https://github.com/Albertlongzi/BCER/blob/d10816712793a9e27f2e70640f9afc06f08a0c5c/configs/tasks_registry.json)

## Coverage

A shared definition brief for the linked catalogue entries. Case identities and source conditions remain in the catalogue; this is not a claim to enumerate all generated or external cases.

## Gaps

Native input/helper/reference views are still missing for this definition. The contract was read from source; no external model or benchmark run was launched.
