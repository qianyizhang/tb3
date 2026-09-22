# Classify arterial connections from MR angiography

Develop and apply a prediction method to classify arterial connections from MR angiography.

## Value

These spatial labels make structures or abnormalities available for quantitative analysis and review. They do not by themselves establish a diagnosis.

## Given

### Original data

Head MR angiography.

### Supplied helpers

Training graph-edge labels and definitions of the target arterial connections. These are training aids; held-out targets remain evaluation references.

### Callable tools

A medical ML development environment; dependency installation, training and inference resources are task-specific and were not exercised in this survey.

### Reference-only material

Evaluation targets are references, not extra solver inputs. Local filesystem visibility has not been audited by running this external task.

## Task specification

Develop the learning/inference pipeline using the allowed training partition, then submit predictions for every required evaluation case. Preserve case IDs, label taxonomy and image geometry.

## Expected output

A JSON record of binary connection labels with the required case index.

## Evaluation

The description evaluates graph/variant classification, including balanced accuracy. This statement describes the published task; no new score or equivalence with the original challenge grader is claimed.

## Visual explanation

### Workflow

- Head MR angiography
- Develop and apply a prediction pipeline
- A JSON record of binary connection labels with the required case index

### Input

**Contract view; native sample not yet illustrated.** Head MR angiography.

### Supplied helpers

**Given material, not an answer reveal.** Training graph-edge labels and definitions of the target arterial connections. These are training aids; held-out targets remain evaluation references.

### Reference or output

**Expected artifact, not an actual prediction.** A JSON record of binary connection labels with the required case index.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| Competition workflow | Training graph-edge labels and definitions of the target arterial connections. | Prepare data, train or adapt a model, validate and produce the final submission. |

## Difficulty

Low MR signal can mimic an absent connection; resolve topology rather than measuring only vessel overlap.

## Sources

- [Pinned challenge description](https://github.com/rajpurkarlab/ReX-MLE/blob/b3d8f7c3ff1df5af46d8f3e5312760af3ad18a53/rex-mle/rexmle/challenges/topcow-track2-task3/description.md)

## Coverage

A shared definition brief for the linked catalogue entries. Case identities and source conditions remain in the catalogue; this is not a claim to enumerate all generated or external cases.

## Gaps

The challenge description was inspected; its local ReX-MLE data-preparation and grading adapters were not replayed. Native example views are not yet attached to this definition.
