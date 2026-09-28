# Reconstruct CT from noisy photon counts

Recover an attenuation slice from noisy projections, giving lower-count rays less
weight. **Source-input blocker:** the pinned release mixes two acquisition conditions.

## Value

Low photon counts make projection uncertainty uneven; weighting changes how
strongly each ray constrains the reconstructed image.

## Given

### Original data

Post-log sinograms and count weights: `(1, 256, 367)`; angles: `(1, 256)`.
The downloaded raw data use **1,000** incident photons, while manifest-verified
metadata says **300**. Raw-data and truth hashes disagree with the benchmark manifest.

### Supplied helpers

Parallel-beam geometry; expected counts `I0 × exp(-Ax)`; post-log transform
`-log(counts/I0)`; count-derived weights. Source code floors counts at one.

### Callable tools

Python with NumPy and SVMBIR projectors. No reconstruction was executed in this audit.

### Reference-only material

**Truth is solver-visible:** L1–L3 copy the entire `data` directory, including
`ground_truth.npz`. Fixtures and saved outputs remain outside the seeded workspace.

## Task specification

Implement reconstruction from the measurements. Resolve the contradictory dose,
truth and units before treating any saved output as a matched result.

## Expected output

One real `256 × 256` array at `output/reconstruction.npy` for end-to-end scoring.
The task's separate native archive uses reconstruction keys.

## Evaluation

Live generic scoring uses the full image. The separate task-aware helper crops
to `204 × 204` and reports cosine NCC and reference-range NRMSE. Neither pinned
repository supplies `metrics.json`; historical notebook thresholds establish no
current pass/fail.

## Visual explanation

### Workflow

- Inspect photon counts, post-log projections and geometry
- Weight rays and reconstruct attenuation
- Compare only against a matched reference condition

### Input

**Unresolved source pairing.** The native 1,000-photon measurements are retained
separately from manifest-verified 300-photon metadata and fixtures.

### Supplied helpers

**Given material.** Geometry and statistical weights constrain reconstruction;
they do not repair the release's conflicting provenance.

### Reference or output

**Saved arrays, not agent predictions.** The fixture phantom matches the saved
FBP/PWLS metric crops, but differs from downloaded truth. No matched native story
has been accepted. The existing CT drawing is conceptual, not a dataset sample.

## Conditions

| Condition | Supplied help | Work remaining |
| --- | --- | --- |
| L1 · README | README, complete data directory, requirements. | Choose and implement reconstruction. |
| L2 · + approach | Adds an SVMBIR/q-GGMRF approach. | Resolve differences from the supplied TV implementation. |
| L3 · + design | Adds the software plan. | Resolve outdated function names and implement the method. |

## Difficulty

Weighting, regularization and count clipping affect the solution. The release
inconsistency prevents attributing saved differences to weighting alone.

## Sources

- [Pinned task README](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/tasks/ct_poisson_lowdose/README.md)
- [Pinned dataset files](https://huggingface.co/datasets/starpacker52/imaging-101/tree/a9de559b54849a25988a8a0d8a5e869063a5a7a3/tasks/ct_poisson_lowdose)
- [Pinned end-to-end scorer](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/evaluation_harness/scorer.py)
- [Source audit and reopening conditions](../sources/imaging101-poisson-lowdose-audit.json)

## Coverage

One synthetic 256-pixel CT task; 13 task sources and 60 shared files verified.
Four numerical/metadata assets match the manifest; two do not. No patient or
agent capability claim.

## Gaps

Recover manifest-matching raw data and truth, or obtain an explicitly revised,
coherent source condition. Reconcile `cm^-1` prose versus `mm^-1` metadata,
solver/output provenance and scoring boundaries before canonical authoring.
This entry remains incomplete; no scope exclusion has been approved.
