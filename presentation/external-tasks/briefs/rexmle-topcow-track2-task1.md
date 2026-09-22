# Label the Circle of Willis on MR angiography

Develop and apply a prediction method to label the Circle of Willis on MR angiography.

## Value

These spatial labels make structures or abnormalities available for quantitative analysis and review. They do not by themselves establish a diagnosis.

## Given

### Original data

MR angiography of the brain’s arterial circulation.

### Supplied helpers

Labeled training masks, class IDs and case metadata. These are training aids; held-out targets remain evaluation references.

### Callable tools

A medical ML development environment; dependency installation, training and inference resources are task-specific and were not exercised in this survey.

### Reference-only material

Evaluation targets are references, not extra solver inputs. Local filesystem visibility has not been audited by running this external task.

## Task specification

Develop the learning/inference pipeline using the allowed training partition, then submit predictions for every required evaluation case. Preserve case IDs, label taxonomy and image geometry.

## Expected output

A multiclass vessel segmentation aligned to the source scan and the required submission index.

## Evaluation

The description uses vessel Dice, with additional topology and boundary measures. This statement describes the published task; no new score or equivalence with the original challenge grader is claimed.

## Visual explanation

### Workflow

- MR angiography of the brain’s arterial circulation
- Develop and apply a prediction pipeline
- A multiclass vessel segmentation aligned to the source scan and the required submission index

### Input

**Contract view; native sample not yet illustrated.** MR angiography of the brain’s arterial circulation.

### Supplied helpers

**Given material, not an answer reveal.** Labeled training masks, class IDs and case metadata. These are training aids; held-out targets remain evaluation references.

### Reference or output

**Expected artifact, not an actual prediction.** A multiclass vessel segmentation aligned to the source scan and the required submission index.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| Competition workflow | Labeled training masks, class IDs and case metadata. | Prepare data, train or adapt a model, validate and produce the final submission. |

## Difficulty

Small communicating arteries and anatomical variants make branch identity and connectivity difficult.

## Sources

- [Pinned challenge description](https://github.com/rajpurkarlab/ReX-MLE/blob/b3d8f7c3ff1df5af46d8f3e5312760af3ad18a53/rex-mle/rexmle/challenges/topcow-track2-task1/description.md)

## Coverage

A shared definition brief for the linked catalogue entries. Case identities and source conditions remain in the catalogue; this is not a claim to enumerate all generated or external cases.

## Gaps

The challenge description was inspected; its local ReX-MLE data-preparation and grading adapters were not replayed. Native example views are not yet attached to this definition.
