# Locate and label dental abnormalities

Develop and apply a prediction method to locate and label dental abnormalities.

## Value

These spatial labels make structures or abnormalities available for quantitative analysis and review. They do not by themselves establish a diagnosis.

## Given

### Original data

Panoramic dental X-rays.

### Supplied helpers

Training images with partial or full quadrant, tooth-number and disease annotations; additional unlabeled images. These are training aids; held-out targets remain evaluation references.

### Callable tools

A medical ML development environment; dependency installation, training and inference resources are task-specific and were not exercised in this survey.

### Reference-only material

Evaluation targets are references, not extra solver inputs. Local filesystem visibility has not been audited by running this external task.

## Task specification

Develop the learning/inference pipeline using the allowed training partition, then submit predictions for every required evaluation case. Preserve case IDs, label taxonomy and image geometry.

## Expected output

Bounding boxes with quadrant, tooth identity and diagnosis, indexed by image_id in the required JSON/CSV submission.

## Evaluation

Average precision across overlap thresholds, evaluated separately for quadrant, enumeration and diagnosis. This statement describes the published task; no new score or equivalence with the original challenge grader is claimed.

## Visual explanation

### Workflow

- Panoramic dental X-rays
- Develop and apply a prediction pipeline
- Bounding boxes with quadrant, tooth identity and diagnosis, indexed by image_id in the required JSON/CSV submission

### Input

**Contract view; native sample not yet illustrated.** Panoramic dental X-rays.

### Supplied helpers

**Given material, not an answer reveal.** Training images with partial or full quadrant, tooth-number and disease annotations; additional unlabeled images. These are training aids; held-out targets remain evaluation references.

### Reference or output

**Expected artifact, not an actual prediction.** Bounding boxes with quadrant, tooth identity and diagnosis, indexed by image_id in the required JSON/CSV submission.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| Competition workflow | Training images with partial or full quadrant, tooth-number and disease annotations; additional unlabeled images. | Prepare data, train or adapt a model, validate and produce the final submission. |

## Difficulty

Train across unequal annotation levels and preserve the distinction between tooth numbering and disease detection.

## Sources

- [Pinned challenge description](https://github.com/rajpurkarlab/ReX-MLE/blob/b3d8f7c3ff1df5af46d8f3e5312760af3ad18a53/rex-mle/rexmle/challenges/dentex/description.md)

## Coverage

A shared definition brief for the linked catalogue entries. Case identities and source conditions remain in the catalogue; this is not a claim to enumerate all generated or external cases.

## Gaps

The challenge description was inspected; its local ReX-MLE data-preparation and grading adapters were not replayed. Native example views are not yet attached to this definition.
