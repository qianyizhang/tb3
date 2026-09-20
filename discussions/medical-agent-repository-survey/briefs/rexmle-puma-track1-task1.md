# Label tissue types in melanoma histology

Develop and apply a prediction method to label tissue types in melanoma histology.

## Value

These spatial labels make structures or abnormalities available for quantitative analysis and review. They do not by themselves establish a diagnosis.

## Given

### Original data

H&E-stained tissue image regions at high magnification.

### Supplied helpers

Training region annotations, class definitions and larger context images. These are training aids; held-out targets remain evaluation references.

### Callable tools

A medical ML development environment; dependency installation, training and inference resources are task-specific and were not exercised in this survey.

### Reference-only material

Evaluation targets are references, not extra solver inputs. Local filesystem visibility has not been audited by running this external task.

## Task specification

Develop the learning/inference pipeline using the allowed training partition, then submit predictions for every required evaluation case. Preserve case IDs, label taxonomy and image geometry.

## Expected output

A TIF semantic mask using background 0 and five foreground tissue labels, plus a case-to-mask CSV.

## Evaluation

Micro Dice over foreground classes; the source explicitly excludes background. This statement describes the published task; no new score or equivalence with the original challenge grader is claimed.

## Visual explanation

### Workflow

- H&E-stained tissue image regions at high magnification
- Develop and apply a prediction pipeline
- A TIF semantic mask using background 0 and five foreground tissue labels

### Input

**Contract view; native sample not yet illustrated.** H&E-stained tissue image regions at high magnification.

### Supplied helpers

**Given material, not an answer reveal.** Training region annotations, class definitions and larger context images. These are training aids; held-out targets remain evaluation references.

### Reference or output

**Expected artifact, not an actual prediction.** A TIF semantic mask using background 0 and five foreground tissue labels, plus a case-to-mask CSV.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| Competition workflow | Training region annotations, class definitions and larger context images. | Prepare data, train or adapt a model, validate and produce the final submission. |

## Difficulty

Distinguish tissue compartments across primary and metastatic lesions, including low-contrast boundaries.

## Sources

- [Track 2 alias: source explicitly declares the same tissue task](https://github.com/rajpurkarlab/ReX-MLE/blob/b3d8f7c3ff1df5af46d8f3e5312760af3ad18a53/rex-mle/rexmle/challenges/puma-track2-task1/description.md)

- [Pinned challenge description](https://github.com/rajpurkarlab/ReX-MLE/blob/b3d8f7c3ff1df5af46d8f3e5312760af3ad18a53/rex-mle/rexmle/challenges/puma-track1-task1/description.md)

## Coverage

PUMA Track 1 Task 1 and Track 2 Task 1 explicitly share the same tissue definition, data and evaluation in the source. A shared definition brief covers both catalogue entries. Case identities and source conditions remain in the catalogue; this is not a claim to enumerate all generated or external cases.

## Gaps

The challenge description was inspected; its local ReX-MLE data-preparation and grading adapters were not replayed. Native example views are not yet attached to this definition.
