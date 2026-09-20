# Segment the aorta and its branches

Develop and apply a prediction method to segment the aorta and its branches.

## Value

These spatial labels make structures or abnormalities available for quantitative analysis and review. They do not by themselves establish a diagnosis.

## Given

### Original data

CT angiography volumes.

### Supplied helpers

Training aortic-tree masks and voxel spacing metadata. These are training aids; held-out targets remain evaluation references.

### Callable tools

A medical ML development environment; dependency installation, training and inference resources are task-specific and were not exercised in this survey.

### Reference-only material

Evaluation targets are references, not extra solver inputs. Local filesystem visibility has not been audited by running this external task.

## Task specification

Develop the learning/inference pipeline using the allowed training partition, then submit predictions for every required evaluation case. Preserve case IDs, label taxonomy and image geometry.

## Expected output

Binary vessel-tree NRRD (.seg.nrrd) masks with a CSV mapping source case IDs to files.

## Evaluation

Dice and Hausdorff distance; the challenge description additionally discusses sensitivity-based robustness analysis. This statement describes the published task; no new score or equivalence with the original challenge grader is claimed.

## Visual explanation

### Workflow

- CT angiography volumes
- Develop and apply a prediction pipeline
- Binary vessel-tree NRRD (.seg.nrrd) masks with a CSV mapping source case IDs to files

### Input

**Contract view; native sample not yet illustrated.** CT angiography volumes.

### Supplied helpers

**Given material, not an answer reveal.** Training aortic-tree masks and voxel spacing metadata. These are training aids; held-out targets remain evaluation references.

### Reference or output

**Expected artifact, not an actual prediction.** Binary vessel-tree NRRD (.seg.nrrd) masks with a CSV mapping source case IDs to files.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| Competition workflow | Training aortic-tree masks and voxel spacing metadata. | Prepare data, train or adapt a model, validate and produce the final submission. |

## Difficulty

Thin branches, large vessel sizes and scan variation make both boundary accuracy and robustness important.

## Sources

- [Pinned challenge description](https://github.com/rajpurkarlab/ReX-MLE/blob/b3d8f7c3ff1df5af46d8f3e5312760af3ad18a53/rex-mle/rexmle/challenges/seg_a/description.md)

## Coverage

A shared definition brief for the linked catalogue entries. Case identities and source conditions remain in the catalogue; this is not a claim to enumerate all generated or external cases.

## Gaps

The challenge description was inspected; its local ReX-MLE data-preparation and grading adapters were not replayed. Native example views are not yet attached to this definition.
