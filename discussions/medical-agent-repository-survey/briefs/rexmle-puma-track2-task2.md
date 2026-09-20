# Locate and classify ten nucleus types

Develop and apply a prediction method to locate and classify ten nucleus types.

## Value

These spatial labels make structures or abnormalities available for quantitative analysis and review. They do not by themselves establish a diagnosis.

## Given

### Original data

H&E melanoma histology regions.

### Supplied helpers

Fine-grained nucleus annotations for ten tumor, immune, stromal and other cell classes. These are training aids; held-out targets remain evaluation references.

### Callable tools

A medical ML development environment; dependency installation, training and inference resources are task-specific and were not exercised in this survey.

### Reference-only material

Evaluation targets are references, not extra solver inputs. Local filesystem visibility has not been audited by running this external task.

## Task specification

Develop the learning/inference pipeline using the allowed training partition, then submit predictions for every required evaluation case. Preserve case IDs, label taxonomy and image geometry.

## Expected output

Per-case JSON with class-labeled polygons or the supported simplified nucleus-centroid format; confidence is optional. A CSV indexes case_id and predicted_nuclei_path.

## Evaluation

Macro F1 over ten classes using the source’s centroid-based detection matching policy. This statement describes the published task; no new score or equivalence with the original challenge grader is claimed.

## Visual explanation

### Workflow

- H&E melanoma histology regions
- Develop and apply a prediction pipeline
- Per-case JSON containing nucleus centroids and class

### Input

**Contract view; native sample not yet illustrated.** H&E melanoma histology regions.

### Supplied helpers

**Given material, not an answer reveal.** Fine-grained nucleus annotations for ten tumor, immune, stromal and other cell classes. These are training aids; held-out targets remain evaluation references.

### Reference or output

**Expected artifact, not an actual prediction.** Per-case JSON with class-labeled polygons or the supported simplified nucleus-centroid format; confidence is optional. A CSV indexes case_id and predicted_nuclei_path.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| Competition workflow | Fine-grained nucleus annotations for ten tumor, immune, stromal and other cell classes. | Prepare data, train or adapt a model, validate and produce the final submission. |

## Difficulty

Fine-grained cell identity is harder than grouping cells into tumor/immune/other, especially for rare classes.

## Sources

- [Pinned challenge description](https://github.com/rajpurkarlab/ReX-MLE/blob/b3d8f7c3ff1df5af46d8f3e5312760af3ad18a53/rex-mle/rexmle/challenges/puma-track2-task2/description.md)

## Coverage

A shared definition brief for the linked catalogue entries. Case identities and source conditions remain in the catalogue; this is not a claim to enumerate all generated or external cases.

## Gaps

The challenge description was inspected; its local ReX-MLE data-preparation and grading adapters were not replayed. Native example views are not yet attached to this definition.
