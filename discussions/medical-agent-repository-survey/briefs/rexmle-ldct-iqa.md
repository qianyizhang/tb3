# Predict perceived low-dose CT image quality

Develop and apply a prediction method to predict perceived low-dose CT image quality.

## Value

Quality assessment/repair can support image review, but agreement with a benchmark reference does not demonstrate a clinical benefit.

## Given

### Original data

Low-dose CT images containing noise and reconstruction artifacts.

### Supplied helpers

Training examples with radiologists’ mean opinion scores; no pristine image is required at inference. These are training aids; held-out targets remain evaluation references.

### Callable tools

A medical ML development environment; dependency installation, training and inference resources are task-specific and were not exercised in this survey.

### Reference-only material

Evaluation targets are references, not extra solver inputs. Local filesystem visibility has not been audited by running this external task.

## Task specification

Develop the learning/inference pipeline using the allowed training partition, then submit predictions for every required evaluation case. Preserve case IDs, label taxonomy and image geometry.

## Expected output

A CSV with image_id and quality_score.

## Evaluation

The description combines absolute correlation coefficients between predicted quality and reader scores. This statement describes the published task; no new score or equivalence with the original challenge grader is claimed.

## Visual explanation

### Workflow

- Low-dose CT images containing noise and reconstruction artifacts
- Develop and apply a prediction pipeline
- A CSV with image_id and quality_score

### Input

**Contract view; native sample not yet illustrated.** Low-dose CT images containing noise and reconstruction artifacts.

### Supplied helpers

**Given material, not an answer reveal.** Training examples with radiologists’ mean opinion scores; no pristine image is required at inference. These are training aids; held-out targets remain evaluation references.

### Reference or output

**Expected artifact, not an actual prediction.** A CSV with image_id and quality_score.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| Competition workflow | Training examples with radiologists’ mean opinion scores; no pristine image is required at inference. | Prepare data, train or adapt a model, validate and produce the final submission. |

## Difficulty

Learn perceived usability rather than simply measuring smoothness; clinically relevant texture may look like noise.

## Sources

- [Pinned challenge description](https://github.com/rajpurkarlab/ReX-MLE/blob/b3d8f7c3ff1df5af46d8f3e5312760af3ad18a53/rex-mle/rexmle/challenges/ldct-iqa/description.md)

## Coverage

A shared definition brief for the linked catalogue entries. Case identities and source conditions remain in the catalogue; this is not a claim to enumerate all generated or external cases.

## Gaps

The challenge description was inspected; its local ReX-MLE data-preparation and grading adapters were not replayed. Native example views are not yet attached to this definition.
