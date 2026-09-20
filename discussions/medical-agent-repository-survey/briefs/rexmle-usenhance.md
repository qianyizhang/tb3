# Enhance handheld ultrasound images

Develop and apply a prediction method to enhance handheld ultrasound images.

## Value

Quality assessment/repair can support image review, but agreement with a benchmark reference does not demonstrate a clinical benefit.

## Given

### Original data

Lower-quality handheld ultrasound B-mode images.

### Supplied helpers

Paired training examples from higher-quality ultrasound and the source image conventions. These are training aids; held-out targets remain evaluation references.

### Callable tools

A medical ML development environment; dependency installation, training and inference resources are task-specific and were not exercised in this survey.

### Reference-only material

Evaluation targets are references, not extra solver inputs. Local filesystem visibility has not been audited by running this external task.

## Task specification

Develop the learning/inference pipeline using the allowed training partition, then submit predictions for every required evaluation case. Preserve case IDs, label taxonomy and image geometry.

## Expected output

Enhanced images saved as PNG and a CSV with image_id and enhanced_image_path.

## Evaluation

Local correlation, SSIM and PSNR; original challenge rank aggregation differs from the description’s normalized composite. This statement describes the published task; no new score or equivalence with the original challenge grader is claimed.

## Visual explanation

### Workflow

- Lower-quality handheld ultrasound B-mode images
- Develop and apply a prediction pipeline
- Enhanced images saved as PNG and a CSV with image_id and enhanced_image_path

### Input

**Contract view; native sample not yet illustrated.** Lower-quality handheld ultrasound B-mode images.

### Supplied helpers

**Given material, not an answer reveal.** Paired training examples from higher-quality ultrasound and the source image conventions. These are training aids; held-out targets remain evaluation references.

### Reference or output

**Expected artifact, not an actual prediction.** Enhanced images saved as PNG and a CSV with image_id and enhanced_image_path.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| Competition workflow | Paired training examples from higher-quality ultrasound and the source image conventions. | Prepare data, train or adapt a model, validate and produce the final submission. |

## Difficulty

Improve contrast and noise without inventing structures; paired devices may not depict exactly identical anatomy.

## Sources

- [Pinned challenge description](https://github.com/rajpurkarlab/ReX-MLE/blob/b3d8f7c3ff1df5af46d8f3e5312760af3ad18a53/rex-mle/rexmle/challenges/usenhance/description.md)

## Coverage

A shared definition brief for the linked catalogue entries. Case identities and source conditions remain in the catalogue; this is not a claim to enumerate all generated or external cases.

## Gaps

The challenge description was inspected; its local ReX-MLE data-preparation and grading adapters were not replayed. Native example views are not yet attached to this definition.
