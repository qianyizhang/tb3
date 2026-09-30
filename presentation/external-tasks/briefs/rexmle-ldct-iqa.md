# Predict perceived low-dose CT image quality

Train or adapt a no-reference method and submit a scalar quality prediction for each test CT. **Training CT only; test absent.** [Official acquisition](https://zenodo.org/records/7833096).

## Value

Agreement with reader perception can inform quality assessment; it does not establish diagnostic accuracy, denoising benefit or dose safety.

## Given

### Original data

Official training example 0559.tif is a 512 × 512 normalized float TIFF. The retained preview linearly maps values 0..1 to grayscale 0..255. HU calibration, anatomical orientation and physical spacing are absent; this is not an applied HU window despite the source description's 350/40 acquisition display convention.

### Supplied helpers

The exact public train.json label is 3.8. It is a reader-score training helper, not a model output or hidden test target. Reader scale endpoints are not established by the inspected adapter. No pristine reference is required at inference.

### Callable tools

The ReX workflow prepares data, develops a method and infers predictions. No tool, preparation, training or inference was run here.

### Reference-only material

The pinned adapter declares private/test_labels.csv for evaluation. Held-out images and private scores are absent locally; actual runtime filesystem visibility remains unaudited.

## Task specification

Preserve unique exact image IDs; infer one quality_score per test image. The preparer stages separate upstream train/test archives, not the random_state=42 split described in generic prose. Its zero-valued sample submission is a template, not a prediction.

## Expected output

submission.csv with image_id (extensionless test stem) and numeric quality_score. All illustrated output values remain unset; the artifact is neither a mask nor a restored CT.

## Evaluation

The pinned grader joins IDs against private labels and checks merged row count. Its score is abs(PLCC)+abs(SROCC)+abs(KROCC), nominally 0..3 for finite nondegenerate coefficients. Signs are discarded. Its overall is mean leaderboard metric position when available, otherwise negative absolute Pearson correlation. Those fields are different; no measured correlation or rank is reported. Constant/non-finite arrays and duplicate IDs need explicit validation before any future execution.

## Visual explanation

### Input

One official training CT with a persistent gap and acquisition route.

### Supplied helpers

The public 3.8 training label is available as helper material; partition selection demonstrates solver/evaluator roles without exposing any hidden target.

### Reference or output

An unfilled CSV schema and correlation formulas, followed by explicit limits. No invented reader scores, predictions or leaderboard results.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| Competition workflow | Training examples with radiologists’ mean opinion scores; no pristine image is required at inference. | Prepare data, train or adapt a model, validate and produce the final submission. |

## Difficulty

Predict perceived quality under combined noise/streak artifacts rather than equating smoothness with usability.

## Sources

- [Pinned ReX adapter](https://github.com/rajpurkarlab/ReX-MLE/tree/b3d8f7c3ff1df5af46d8f3e5312760af3ad18a53/rex-mle/rexmle/challenges/ldct-iqa)
- [Official dataset](https://zenodo.org/records/7833096), DOI 10.5281/zenodo.7833096

## Coverage

A shared definition brief for the linked catalogue entries. Case identities and source conditions remain in the catalogue; this is not a claim to enumerate all generated or external cases.

## Gaps

Only one official training example was extracted through verified bounded ranges. Test data, private labels, predictions and measured metrics are missing. Zenodo CC-BY-4.0 metadata conflicts with ReX CC-BY-NC-SA-4.0; resolve terms before redistribution. Recover exact held-out assets and validate visibility before reopening execution.
