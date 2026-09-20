# Label brain arteries on MR angiography

Develop and apply a prediction method to label brain arteries on MR angiography.

## Value

These spatial labels make structures or abnormalities available for quantitative analysis and review. They do not by themselves establish a diagnosis.

## Given

### Original data

Head MR angiography volumes.

### Supplied helpers

Training vessel masks with the source’s 42 foreground vessel labels. These are training aids; held-out targets remain evaluation references.

### Callable tools

A medical ML development environment; dependency installation, training and inference resources are task-specific and were not exercised in this survey.

### Reference-only material

Evaluation targets are references, not extra solver inputs. Local filesystem visibility has not been audited by running this external task.

## Task specification

Develop the learning/inference pipeline using the allowed training partition, then submit predictions for every required evaluation case. Preserve case IDs, label taxonomy and image geometry.

## Expected output

A multiclass NIfTI segmentation with labels 0–42 and a case/modality/file CSV.

## Evaluation

Mean vessel Dice is primary; the description lists additional topology/connectivity measures. This statement describes the published task; no new score or equivalence with the original challenge grader is claimed.

## Visual explanation

### Workflow

- Head MR angiography volumes
- Develop and apply a prediction pipeline
- A multiclass NIfTI segmentation with labels 0–42 and a case/modality/file CSV

### Input

**Contract view; native sample not yet illustrated.** Head MR angiography volumes.

### Supplied helpers

**Given material, not an answer reveal.** Training vessel masks with the source’s 42 foreground vessel labels. These are training aids; held-out targets remain evaluation references.

### Reference or output

**Expected artifact, not an actual prediction.** A multiclass NIfTI segmentation with labels 0–42 and a case/modality/file CSV.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| Competition workflow | Training vessel masks with the source’s 42 foreground vessel labels. | Prepare data, train or adapt a model, validate and produce the final submission. |

## Difficulty

MR vessel appearance differs from CT, and the label taxonomy is also different between these tracks.

## Sources

- [Pinned challenge description](https://github.com/rajpurkarlab/ReX-MLE/blob/b3d8f7c3ff1df5af46d8f3e5312760af3ad18a53/rex-mle/rexmle/challenges/topbrain-track2/description.md)

## Coverage

A shared definition brief for the linked catalogue entries. Case identities and source conditions remain in the catalogue; this is not a claim to enumerate all generated or external cases.

## Gaps

The challenge description was inspected; its local ReX-MLE data-preparation and grading adapters were not replayed. Native example views are not yet attached to this definition.
