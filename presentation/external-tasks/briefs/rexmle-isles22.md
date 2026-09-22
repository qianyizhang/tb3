# Segment ischemic stroke lesions

Develop and apply a prediction method to segment ischemic stroke lesions.

## Value

These spatial labels make structures or abnormalities available for quantitative analysis and review. They do not by themselves establish a diagnosis.

## Given

### Original data

Brain DWI, ADC and FLAIR MRI volumes.

### Supplied helpers

Labeled training cases and the source challenge’s image/submission conventions. These are training aids; held-out targets remain evaluation references.

### Callable tools

A medical ML development environment; dependency installation, training and inference resources are task-specific and were not exercised in this survey.

### Reference-only material

Evaluation targets are references, not extra solver inputs. Local filesystem visibility has not been audited by running this external task.

## Task specification

Develop the learning/inference pipeline using the allowed training partition, then submit predictions for every required evaluation case. Preserve case IDs, label taxonomy and image geometry.

## Expected output

A binary lesion mask in the input image geometry, saved as NIfTI.

## Evaluation

Dice overlap is primary, with additional lesion-level and volume measures described by the source. This statement describes the published task; no new score or equivalence with the original challenge grader is claimed.

## Visual explanation

### Workflow

- Brain DWI, ADC and FLAIR MRI volumes
- Develop and apply a prediction pipeline
- A binary lesion mask in the input image geometry, saved as NIfTI

### Input

**Contract view; native sample not yet illustrated.** Brain DWI, ADC and FLAIR MRI volumes.

### Supplied helpers

**Given material, not an answer reveal.** Labeled training cases and the source challenge’s image/submission conventions. These are training aids; held-out targets remain evaluation references.

### Reference or output

**Expected artifact, not an actual prediction.** A binary lesion mask in the input image geometry, saved as NIfTI.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| Competition workflow | Labeled training cases and the source challenge’s image/submission conventions. | Prepare data, train or adapt a model, validate and produce the final submission. |

## Difficulty

Small lesions and differences between MRI contrasts make volume overlap alone an incomplete description of errors.

## Sources

- [Pinned challenge description](https://github.com/rajpurkarlab/ReX-MLE/blob/b3d8f7c3ff1df5af46d8f3e5312760af3ad18a53/rex-mle/rexmle/challenges/isles22/description.md)

## Coverage

A shared definition brief for the linked catalogue entries. Case identities and source conditions remain in the catalogue; this is not a claim to enumerate all generated or external cases.

## Gaps

The challenge description was inspected; its local ReX-MLE data-preparation and grading adapters were not replayed. Native example views are not yet attached to this definition. The description includes the original challenge’s container submission; the adapted local submission path needs confirmation before execution.
