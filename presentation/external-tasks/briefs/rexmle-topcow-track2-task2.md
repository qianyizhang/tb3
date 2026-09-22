# Locate the Circle of Willis in an MR volume

Develop and apply a prediction method to locate the Circle of Willis in an MR volume.

## Value

These spatial labels make structures or abnormalities available for quantitative analysis and review. They do not by themselves establish a diagnosis.

## Given

### Original data

Head MR angiography.

### Supplied helpers

Training 3D bounding boxes and case metadata. These are training aids; held-out targets remain evaluation references.

### Callable tools

A medical ML development environment; dependency installation, training and inference resources are task-specific and were not exercised in this survey.

### Reference-only material

Evaluation targets are references, not extra solver inputs. Local filesystem visibility has not been audited by running this external task.

## Task specification

Develop the learning/inference pipeline using the allowed training partition, then submit predictions for every required evaluation case. Preserve case IDs, label taxonomy and image geometry.

## Expected output

A JSON box with size:[x,y,z] in voxel counts and location:[x,y,z] as the center in voxel coordinates, plus a case-to-file CSV.

## Evaluation

3D intersection-over-union is the stated primary localization metric. This statement describes the published task; no new score or equivalence with the original challenge grader is claimed.

## Visual explanation

### Workflow

- Head MR angiography
- Develop and apply a prediction pipeline
- A JSON box with size:[x,y,z] and location:[x,y,z]

### Input

**Contract view; native sample not yet illustrated.** Head MR angiography.

### Supplied helpers

**Given material, not an answer reveal.** Training 3D bounding boxes and case metadata. These are training aids; held-out targets remain evaluation references.

### Reference or output

**Expected artifact, not an actual prediction.** A JSON box with size:[x,y,z] in voxel counts and location:[x,y,z] as the center in voxel coordinates, plus a case-to-file CSV.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| Competition workflow | Training 3D bounding boxes and case metadata. | Prepare data, train or adapt a model, validate and produce the final submission. |

## Difficulty

Locate the arterial ring despite incomplete or weakly visible communicating vessels.

## Sources

- [Pinned challenge description](https://github.com/rajpurkarlab/ReX-MLE/blob/b3d8f7c3ff1df5af46d8f3e5312760af3ad18a53/rex-mle/rexmle/challenges/topcow-track2-task2/description.md)

## Coverage

A shared definition brief for the linked catalogue entries. Case identities and source conditions remain in the catalogue; this is not a claim to enumerate all generated or external cases.

## Gaps

The challenge description was inspected; its local ReX-MLE data-preparation and grading adapters were not replayed. Native example views are not yet attached to this definition.
