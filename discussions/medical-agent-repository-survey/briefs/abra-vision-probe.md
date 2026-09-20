# Recognize an image’s modality or display treatment

Identify CT, MRI or radiography, or the applied windowing preset; reject noise controls.

## Value

Tests a specific part of using a medical image viewer; success in navigation or metadata lookup is separate from diagnostic accuracy.

## Given

### Original data

A rendered image or a Gaussian-noise control image.

### Supplied helpers

Four answer options. Slice selection and preprocessing are performed by the task generator.

### Callable tools

ABRA viewer and submission tools on the OHIF/Orthanc stack.

### Reference-only material

Evaluation targets are references, not extra solver inputs. Local filesystem visibility has not been audited by running this external task.

## Task specification

Identify CT, MRI or radiography, or the applied windowing preset; reject noise controls.

## Expected output

One option letter through submit_answer; N/A is the target for noise controls.

## Evaluation

Exact answer match within a three-turn budget.

## Visual explanation

### Workflow

- Study or rendered observation
- Requested viewer / reasoning action
- Final state or submitted answer

### Input

**Contract view; native sample not yet illustrated.** A rendered image or a Gaussian-noise control image.

### Supplied helpers

**Given material, not an answer reveal.** Four answer options. Slice selection and preprocessing are performed by the task generator.

### Reference or output

**Expected artifact, not an actual prediction.** One option letter through submit_answer; N/A is the target for noise controls.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| Source condition | Four answer options. Slice selection and preprocessing are performed by the task generator. | These probes isolate basic visual recognition from navigation, but selected slices remove the volume-search problem. |

## Difficulty

These probes isolate basic visual recognition from navigation, but selected slices remove the volume-search problem.

## Sources

- [Task generator](https://github.com/Luab/ABRA/blob/688814615dc368a66276798cb864fe9a587d7e6c/scripts/task_generators/vision_probe.py)

## Coverage

A shared definition brief for the linked catalogue entries. Case identities and source conditions remain in the catalogue; this is not a claim to enumerate all generated or external cases.

## Gaps

Native input/helper/reference views are still missing for this definition. The contract was read from source; no external model or benchmark run was launched.
