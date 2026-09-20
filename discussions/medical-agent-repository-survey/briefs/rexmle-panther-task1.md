# Segment pancreatic tumor on diagnostic MRI

Develop and apply a prediction method to segment pancreatic tumor on diagnostic MRI.

## Value

These spatial labels make structures or abnormalities available for quantitative analysis and review. They do not by themselves establish a diagnosis.

## Given

### Original data

Contrast-enhanced arterial-phase T1-weighted pancreas MRI.

### Supplied helpers

Training tumor masks and image-geometry metadata. These are training aids; held-out targets remain evaluation references.

### Callable tools

A medical ML development environment; dependency installation, training and inference resources are task-specific and were not exercised in this survey.

### Reference-only material

Evaluation targets are references, not extra solver inputs. Local filesystem visibility has not been audited by running this external task.

## Task specification

Develop the learning/inference pipeline using the allowed training partition, then submit predictions for every required evaluation case. Preserve case IDs, label taxonomy and image geometry.

## Expected output

A binary tumor mask per case in MHA format plus a patient-to-file submission CSV.

## Evaluation

Dice is the stated primary score; the description also reports surface accuracy and Hausdorff distance. This statement describes the published task; no new score or equivalence with the original challenge grader is claimed.

## Visual explanation

### Workflow

- Contrast-enhanced arterial-phase T1-weighted pancreas MRI
- Develop and apply a prediction pipeline
- A binary tumor mask per case in MHA format plus a patient-to-file submission CSV

### Input

**Contract view; native sample not yet illustrated.** Contrast-enhanced arterial-phase T1-weighted pancreas MRI.

### Supplied helpers

**Given material, not an answer reveal.** Training tumor masks and image-geometry metadata. These are training aids; held-out targets remain evaluation references.

### Reference or output

**Expected artifact, not an actual prediction.** A binary tumor mask per case in MHA format plus a patient-to-file submission CSV.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| Competition workflow | Training tumor masks and image-geometry metadata. | Prepare data, train or adapt a model, validate and produce the final submission. |

## Difficulty

The tumor boundary can be subtle against normal pancreas and nearby tissue; preserve physical geometry.

## Sources

- [Pinned challenge description](https://github.com/rajpurkarlab/ReX-MLE/blob/b3d8f7c3ff1df5af46d8f3e5312760af3ad18a53/rex-mle/rexmle/challenges/panther-task1/description.md)

## Coverage

A shared definition brief for the linked catalogue entries. Case identities and source conditions remain in the catalogue; this is not a claim to enumerate all generated or external cases.

## Gaps

The challenge description was inspected; its local ReX-MLE data-preparation and grading adapters were not replayed. Native example views are not yet attached to this definition.
