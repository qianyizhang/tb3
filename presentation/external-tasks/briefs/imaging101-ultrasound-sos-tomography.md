# Map sound speed from ultrasound travel times

Implement a computational method to map sound speed from ultrasound travel times.

> **Actual gap:** Native synthetic parallel-beam sums omit pixel-length scaling; calibrated seconds and ring paths are unestablished. Source truth is solver-visible; no participant reconstruction or score. [Official pinned acquisition](https://huggingface.co/datasets/starpacker52/imaging-101/tree/a9de559b54849a25988a8a0d8a5e869063a5a7a3/tasks/ultrasound_sos_tomography).

## Value

This imaging problem tests the computational step between acquired measurements and an interpretable image or physical-property map.

## Given

### Original data

Synthetic parallel-beam noisy projection sums: 1×128×60 float64, with angles 0–177° in 3° steps. Source Radon omits physical pixel length; these values are not calibrated seconds or acquired ring-transducer data.

### Supplied helpers

128-pixel detector grid and 60 angles are actual operator inputs. Nominal 0.5 mm pixels / 50 mm ring are metadata, not implemented physical ray geometry. Clean/full projections and speed/slowness truth are solver-visible; approach/design depend on assistance.

### Callable tools

Python and the task’s numerical/model dependencies. End-to-end, function-level and planning modes assess different work.

### Reference-only material

data/ground_truth.npz contains solver-visible synthetic speed and slowness arrays; raw_data also includes clean/full projections. Source reconstructions are retained provenance, not participant output. Educational reveal does not establish blind evaluation.

## Task specification

Implement the linked README’s forward/inverse problem with its array conventions and units. The expected artifact below describes the scientific result; the selected harness mode owns exact filenames and callable signatures.

## Expected output

Generic output/reconstruction.npy is a real 128×128 speed map (m/s). Main instead saves reconstructions.npz with several speed/slowness keys. No participant map is shown.

## Evaluation

Generic same-shape NPZ ranking selects sos_phantom, full 16384 speed entries; NRMSE is range-normalized RMSE and NCC uncentered cosine without flux scaling for this task. Main instead scores 0.8 centre-cropped slowness; the exact source helper crops [13:115,13:115], 102×102 = 10,404 entries. Its range NRMSE returns 0 for an exactly constant reference, whereas generic NRMSE returns infinity. Source NCC returns 0 for an exactly zero norm; generic uses epsilon 1e-30. Source SSIM is local skimage with reference range, unlike the generic global-moment surrogate; source constant-range SSIM has no explicit guard. Main computes top-level thresholds from best cropped-slowness source results; generic can attach them to full-speed scores when that metrics file is present. This file is not retained and no effective threshold/verdict is established. Nothing was scored.

## Visual explanation

### Workflow

- Native synthetic parallel-beam projection samples, with physical seconds uncalibrated
- Map sound speed from ultrasound travel times
- A 2D map of sound speed

### Input

**Exact indexed native source values; no reconstruction.** Synthetic parallel-beam noisy projection sums: 1×128×60 float64, with angles 0–177° in 3° steps. Source Radon omits physical pixel length; these values are not calibrated seconds or acquired ring-transducer data.

### Supplied helpers

**Given material, not an answer reveal.** 128-pixel detector grid and 60 angles are actual operator inputs. Nominal 0.5 mm pixels / 50 mm ring are metadata, not implemented physical ray geometry. Clean/full projections and speed/slowness truth are solver-visible; approach/design depend on assistance.

### Reference or output

**Expected artifact, not an actual prediction.** Generic output/reconstruction.npy is a real 128×128 speed map (m/s). Main instead saves reconstructions.npz with several speed/slowness keys. No participant map is shown.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| L1 · README | README, data description and method hints. | Choose and implement a workable algorithm. |
| L2 · + approach | A proposed algorithmic approach is added. | Design the software and implement the method. |
| L3 · + design | Approach and software design are added. | Implement the specified design and numerical details. |

## Difficulty

Sparse parallel-beam inversion has 7680 samples for 16384 pixels. Actual geometry, missing pixel-length scaling, signed slowness and reference units must be resolved; no refraction operator is implemented.

## Sources

- [Pinned task README](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/tasks/ultrasound_sos_tomography/README.md)
- [Evaluation modes and assistance](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/README.md)

## Coverage

One scientific task definition across L1/L2/L3 assistance. This collection includes non-medical astronomy, optics and Earth-science tasks as well as medical imaging.

## Gaps

Native synthetic parallel-beam sums omit pixel-length scaling; calibrated seconds and ring paths are unestablished. Source truth is solver-visible; no participant reconstruction or score. Pin physical path/pixel-length scaling and operator/adjoint convention; choose blind inversion or method reproduction; isolate synthetic truth for blind work; reconcile speed versus cropped slowness reference and effective evaluator before scoring.
