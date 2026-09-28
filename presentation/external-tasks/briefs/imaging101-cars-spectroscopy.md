# Estimate gas temperature from Raman spectra

Infer temperature from one published synthetic nitrogen CARS spectrum. The saved
reference fit and released end-to-end harness have different output and scoring
contracts; the explainer keeps those conditions explicit.

## Value

Connect a temperature-dependent molecular spectrum to measured intensity, then
separate a physically meaningful parameter estimate from spectral agreement.

## Given

### Original data

`raw_data.npz` contains float64 `measurements` and `nu_axis`, each shape `(1, 200)`.
The axis spans 2280–2330 cm⁻¹; intensities are dimensionless and max-normalized.
This is source-generated synthetic gas data, not a measured experimental spectrum.

### Supplied helpers

README and metadata supply the molecular/universal constants, N₂ species,
10 bar pressure, 1 cm⁻¹ pump linewidth, 0.5 cm⁻¹ slit width, noise level 0.02 and
seed 42. L2 adds `plan/approach.md`, which explicitly names the true 2400 K;
L3 also adds software design. The source implementation itself is not seeded
into the L1–L3 writable workspace.

### Callable tools

The selected source condition uses Python/numerical dependencies and a command
runner to implement the pipeline. The source solver uses bounded SciPy
`least_squares(method='trf', max_nfev=100)`; L2 prose calls it LM. No runtime
installation, inverse optimization or agent execution was performed for this tour.

### Reference-only material

Scientifically, `ground_truth.npz` holds the clean spectrum, true temperature
2400 K and mole fraction 0.79. **Released staging copies it to the solver:**
L1–L3 all copy the entire `data/` directory. Three executions of the selected
file-seeding method reproduce this, with installation commands intercepted.
The Docker source also mounts the entire task directory read-only; this is not
hidden-reference isolation. Its runtime was not launched.

The player initially hides the clean curve for teaching, then reveals it explicitly.
That reader-facing reveal must not be mistaken for a private solver reference.

## Task specification

Implement a forward spectrum and invert the observed spectrum for temperature.
The pinned implementation uses 30 rotational states, two vibrational levels,
Q/O/S branches, a relaxation matrix, coherent nonresonant background, pump/slit
operations and local-mean downsampling from a 0.05 cm⁻¹ grid. It fits temperature,
mole fraction, spectral shift and slit width within explicit bounds.

Two bounded forward curves at 2000 and 2800 K show the operation with other
parameters fixed. These teaching diagnostics are not optimizer iterates.

## Expected output

The active local end-to-end prompt/scorer expects `output/reconstruction.npy`:
a numeric reconstructed spectral array. Retain `(1, 200)` for this acquired case.
A separate CARS adapter expects `reconstruction.npz` containing `y_pred` and
`temperature_pred`. Do not treat these formats as interchangeable.

The published source fit is 2391.5641794510043 K, with a saved `(1, 200)` spectrum.
It is retained source output, not a new agent result.

## Evaluation

| Condition | Comparison | Replayed saved-fit result |
|---|---|---|
| Active local generic scorer | Fitted array versus clean spectrum | NCC 0.999979; NRMSE 0.002403; no Kelvin-error field |
| Separate native CARS adapter | Fitted spectrum versus measurements, plus temperature versus truth | NCC 0.998361; NRMSE 0.018240; absolute temperature error 8.435821 K |
| Generic raw-data no-op control | Noisy measurements versus clean spectrum | NCC 0.998346; NRMSE 0.018418; not a fitted result |

NCC is cosine similarity; NRMSE divides RMSE by reference dynamic range.
The generic reader squeezes only arrays with more than two dimensions:
flattening the saved fit to `(200,)` fails reference-shape selection. A `(1,)`
temperature output selects a scalar reference and gives infinite range-normalized
NRMSE, not a Kelvin-error metric. These are retained contract diagnostics.

No CARS `metrics.json` or evaluation tests appear in the pinned Git tree or asset
manifest. The HF directory listing timed out, so this does not establish absence
from every external store. No threshold or pass/fail was invented. The inspected
Docker fallback requires `ground_truth.npy`; the acquired reference is NPZ.

## Visual explanation

### Workflow

- Inspect all 200 native spectral samples and physical metadata.
- Trace the actual L1–L3 staging boundary.
- Compare fixed forward proposals and inspect saved-fit residuals at exact indices.
- Reveal the clean source curve and compare the two scoring paths.

### Input

Exact published samples plotted at their original wavenumbers, without resampling.

### Supplied helpers

Metadata constants and assistance levels are distinct from the source implementation
and from the two diagnostic forward curves.

### Reference or output

Saved fit is solid orange; clean reference is dashed purple; measured samples are
dark-green points. True parameters and clean reference appear under an explicit
reader reveal. Staging exposure remains labeled in that scene.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| L1 · README | README, requirements, all data including ground truth | Choose and implement the computational method; held-out validity is not established. |
| L2 · + approach | L1 plus algorithmic approach naming true 2400 K | Design and implement the proposed approach. |
| L3 · + design | L2 plus function signatures and data flow | Implement the specified interfaces and numerical details. |

## Difficulty

Temperature, shift and slit width affect spectral shape. In this pinned forward
implementation, max normalization cancels the mole-fraction amplitude factor:
changing x from 0.79 to 0.20 at fixed temperature changed the normalized curve by
at most 2.23 × 10⁻¹⁶. This implementation diagnostic does not establish general
physical identifiability. A small spectral error alone is insufficient evidence
for every fitted parameter.

## Sources

- [Pinned task README](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/tasks/cars_spectroscopy/README.md)
- [Pinned runner staging](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/evaluation_harness/runner.py)
- [Active generic scorer](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/evaluation_harness/reference_scoring.py)
- [Native CARS scoring adapter](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/evaluation_harness/task_scoring.py)
- [Pinned data release](https://huggingface.co/datasets/starpacker52/imaging-101/tree/a9de559b54849a25988a8a0d8a5e869063a5a7a3/tasks/cars_spectroscopy)
- [Source audit and exact receipts](../sources/imaging101-cars-audit.json)
- [Numerical asset provenance](../../task-explorer/imaging101-cars/NOTICE.md)

## Coverage

One synthetic gas case, its saved fit and selected source contracts. Function-level
fixtures and plan judgments are separate modes, not reproduced benchmark outcomes.

## Gaps

No new agent result, inverse solve, Docker execution or benchmark pass. Missing
thresholds remain unresolved. Forward diagnostics emitted retained NumPy matmul
warnings; all returned samples were finite and the 2400 K curve reproduced the
source clean spectrum within 1.34 × 10⁻¹¹. No uncertainty interval or general
capability estimate follows from this single saved result.
